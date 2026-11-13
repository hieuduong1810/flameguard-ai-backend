from datetime import UTC, datetime
from decimal import Decimal

from pydantic import ValidationError

from app.integrations.prediction import (
    PredictionCall,
    PredictionFailure,
    ProviderRegistration,
    execute_provider,
)
from app.repositories.prediction_registry import model_record, training_record
from app.schemas.api.predictions import ModelMetadata, PredictionResponse, Readiness
from app.services.collection import admit_collection
from app.services.scenario_interpretation import fingerprint
from app.services.unit_of_work import read_unit_of_work


def domain_reasons(scenario, metadata, observable):
    reasons = []
    if observable not in metadata.observables:
        reasons.append("observable_unsupported")
    if scenario.material is None:
        reasons.append("material_missing")
    elif scenario.material.key not in metadata.materials:
        reasons.append("material_unsupported")
    for name in ("gravity", "oxygen", "pressure", "airflow"):
        quantity, bounds = getattr(scenario, name), getattr(metadata, name)
        if quantity is None:
            reasons.append(f"{name}_missing")
        elif quantity.unit != bounds.unit:
            reasons.append(f"{name}_unit_unsupported")
        elif not Decimal(bounds.minimum) <= Decimal(quantity.value) <= Decimal(bounds.maximum):
            reasons.append(f"{name}_outside_domain")
    if scenario.oxygen and scenario.oxygen.meaning != metadata.oxygen_meaning:
        reasons.append("oxygen_meaning_unsupported")
    return reasons


class PredictionService:
    def __init__(self, sessions, settings, provider):
        self.sessions, self.settings, self.provider = sessions, settings, provider

    async def snapshot(self, model_id):
        async with self.sessions() as session, read_unit_of_work(session):
            config, _ = await admit_collection(session, self.settings, capture_content=True)
            row = await model_record(session, model_id)
            metadata, training = None, None
            if row and row["applicability_domain"] and len(row["applicability_domain"]) <= 32768:
                try:
                    metadata = ModelMetadata.model_validate_json(row["applicability_domain"])
                    training = await training_record(session, model_id, metadata.training_run_id)
                except (ValidationError, ValueError):
                    metadata = None
            binding = fingerprint(
                {
                    "collection": config["phase5ContentHash"],
                    "collection_id": config["collectionId"],
                    "origin": config.get("origin"),
                    "review_state": config.get("reviewState"),
                    "dataset_version": config.get("phase5DatasetVersion"),
                    "model": {**row, "id": str(row["id"])} if row else None,
                    "training": training,
                }
            )
            return config, row, metadata, training, binding

    def assessment(self, model_id, snapshot):
        config, row, metadata, training, _ = snapshot
        reasons = []
        if row is None:
            reasons.append("model_unavailable")
        elif row["validation_status"] != "validated":
            reasons.append("model_unvalidated")
        if metadata is None:
            reasons.append("model_metadata_unavailable")
        elif metadata.validation_expires_at <= datetime.now(UTC):
            reasons.append("model_validation_expired")
        if metadata and any(
            getattr(metadata, name).unit != unit
            for name, unit in (
                ("gravity", "g"),
                ("oxygen", "%"),
                ("pressure", "psia"),
                ("airflow", "cm/s"),
            )
        ):
            reasons.append("domain_units_unsupported")
        if metadata and (
            training is None
            or training["training_dataset_ref"] != metadata.dataset_version
            or training["metrics_ref"] != metadata.evaluation_ref
        ):
            reasons.append("training_evaluation_binding_unavailable")
        if metadata and config.get("phase5DatasetVersion") != metadata.dataset_version:
            reasons.append("dataset_version_unavailable")
        # Admission currently permits only unreviewed/unknown collections. Real
        # publication needs a separately approved admission change and acceptance.
        if config.get("origin") != "real" or config.get("reviewState") != "reviewed":
            reasons.append("scientific_collection_unreviewed")
        if self.provider.origin != "real":
            reasons.append("validated_provider_unavailable")
        registration = getattr(self.provider, "registration", None)
        if (
            not isinstance(registration, ProviderRegistration)
            or not metadata
            or not row
            or (
                registration.model_id != model_id
                or registration.model_version != row["version"]
                or registration.dataset_version != metadata.dataset_version
                or registration.artifact_ref != metadata.artifact_ref
                or not registration.artifact_available
                or not registration.provider_version.strip()
            )
        ):
            reasons.append("provider_model_binding_unavailable")
        return Readiness(
            state="not_ready" if reasons else "ready",
            reasons=reasons,
            model_id=model_id,
            model_version=row["version"] if row else None,
            dataset_version=metadata.dataset_version if metadata else None,
            origin=config.get("origin", "unknown"),
            capabilities=dict(metadata.observables) if metadata else {},
            limitations=list(metadata.limitations) if metadata else [],
        )

    async def readiness(self, model_id):
        if model_id is None:
            return Readiness(reasons=["model_selection_required"])
        return self.assessment(model_id, await self.snapshot(model_id))

    async def predict(self, request):
        snapshot = await self.snapshot(request.model_id)
        readiness = self.assessment(request.model_id, snapshot)
        metadata = snapshot[2]
        if (
            readiness.model_version is not None
            and request.expected_model_version != readiness.model_version
        ):
            raise PredictionFailure("VERSION_CONFLICT", 409)
        if (
            readiness.dataset_version is not None
            and request.expected_dataset_version != readiness.dataset_version
        ):
            raise PredictionFailure("VERSION_CONFLICT", 409)
        if readiness.state != "ready":
            return PredictionResponse(
                state="not_ready", readiness=readiness, reasons=readiness.reasons
            )
        reasons = domain_reasons(request.scenario, metadata, request.observable)
        if reasons:
            return PredictionResponse(state="unsupported", readiness=readiness, reasons=reasons)
        call = PredictionCall(
            request=request, metadata=metadata, collection_fingerprint=snapshot[4]
        )
        result = await execute_provider(
            self.provider, call, self.settings.prediction_timeout_seconds
        )
        current = await self.snapshot(request.model_id)
        if current[4] != snapshot[4] or self.assessment(request.model_id, current).state != "ready":
            raise PredictionFailure("VERSION_CONFLICT", 409)
        return PredictionResponse(state="predicted", readiness=readiness, reasons=[], result=result)
