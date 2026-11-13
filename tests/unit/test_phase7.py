import asyncio
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.integrations.prediction import (
    MockPredictionProvider,
    PredictionCall,
    PredictionFailure,
    UnavailablePredictionProvider,
    execute_provider,
    select_provider,
)
from app.schemas.api.predictions import ModelMetadata, ProviderResult, Range
from app.schemas.api.scenarios import ScenarioInput
from app.services.predictions import PredictionService, domain_reasons
from tests.fixtures.phase7 import MODEL_ID, metadata, request, request_body


def call():
    return PredictionCall(request=request(), metadata=metadata(), collection_fingerprint="a" * 64)


@pytest.mark.parametrize("field", ["gravity", "oxygen", "pressure", "airflow", "material"])
def test_missing_conditions(field):
    scenario = request_body()["scenario"]
    scenario.pop(field)
    assert f"{field}_missing" in domain_reasons(
        ScenarioInput.model_validate(scenario), metadata(), "TEST_ONLY_observable"
    )


@pytest.mark.parametrize("field", ["gravity", "oxygen", "pressure", "airflow"])
def test_domain_bounds(field):
    scenario = request_body()["scenario"]
    scenario[field]["value"] = "1"
    assert f"{field}_outside_domain" in domain_reasons(
        ScenarioInput.model_validate(scenario), metadata(), "TEST_ONLY_observable"
    )


def test_material_observable_and_oxygen_meaning():
    scenario = request_body()["scenario"]
    scenario["material"]["key"] = "OTHER"
    scenario["oxygen"]["meaning"] = "oxidizer_oxygen_fraction_percent"
    reasons = domain_reasons(ScenarioInput.model_validate(scenario), metadata(), "other")
    assert set(reasons) == {
        "material_unsupported",
        "observable_unsupported",
        "oxygen_meaning_unsupported",
    }
    assert domain_reasons(request().scenario, metadata(), request().observable) == []


def test_unknown_metadata_and_reversed_range():
    raw = metadata().model_dump(mode="json")
    raw["schema_version"] = 2
    with pytest.raises(ValidationError):
        ModelMetadata.model_validate(raw)
    with pytest.raises(ValidationError):
        Range(minimum="1", maximum="0", unit="g")


@pytest.mark.parametrize("value", ["NaN", "Infinity", "1e999", 1.2, True, None])
def test_bad_domain_numbers(value):
    with pytest.raises(ValidationError):
        Range(minimum=value, maximum="0", unit="g")


async def test_mock_transport_only():
    result = await execute_provider(MockPredictionProvider(), call(), 1)
    assert result.origin == "synthetic"
    assert result.value == "0"
    assert result.dataset_version == metadata().dataset_version
    assert result.uncertainty.method_ref == metadata().uncertainty_ref
    assert metadata().limitations[0] in result.limitations


async def test_unavailable_and_timeout():
    with pytest.raises(PredictionFailure) as error:
        await execute_provider(UnavailablePredictionProvider(), call(), 1)
    assert error.value.status == 503

    class Slow:
        origin = "synthetic"

        async def predict(self, call):
            await asyncio.sleep(1)

    with pytest.raises(PredictionFailure) as error:
        await execute_provider(Slow(), call(), 0.001)
    assert error.value.status == 504


@pytest.mark.parametrize(
    "field,value",
    [
        ("model_version", "wrong"),
        ("dataset_version", "wrong"),
        ("unit", "wrong"),
        ("value", "NaN"),
        ("origin", "real"),
        ("limitations", ()),
        ("uncertainty", None),
    ],
)
async def test_provider_rejects_malformed_or_mismatched(field, value):
    result = (await MockPredictionProvider().predict(call())).model_dump()
    result[field] = value

    class Bad:
        origin = "synthetic"

        async def predict(self, call):
            return result

    with pytest.raises(PredictionFailure) as error:
        await execute_provider(Bad(), call(), 1)
    assert error.value.status == 502


def test_injection_per_application():
    a = SimpleNamespace(state=SimpleNamespace(prediction_provider_factory=MockPredictionProvider))
    b = SimpleNamespace(
        state=SimpleNamespace(settings=SimpleNamespace(prediction_provider="unavailable"))
    )
    assert isinstance(select_provider(a), MockPredictionProvider)
    assert isinstance(select_provider(b), UnavailablePredictionProvider)


def test_registry_row_is_insufficient():
    service = PredictionService(None, None, MockPredictionProvider())
    snapshot = (
        {"origin": "synthetic", "reviewState": "unreviewed"},
        {"version": "TEST_ONLY-v1", "validation_status": "validated"},
        None,
        None,
        "test",
    )
    readiness = service.assessment(MODEL_ID, snapshot)
    assert readiness.state == "not_ready"
    assert "model_metadata_unavailable" in readiness.reasons
    assert "scientific_collection_unreviewed" in readiness.reasons


def test_uncertainty_interval_validation():
    raw = {
        "model_id": MODEL_ID,
        "model_version": "TEST_ONLY-v1",
        "dataset_version": "TEST_ONLY-v1",
        "observable": "TEST_ONLY",
        "value": "2",
        "unit": "TEST_ONLY",
        "origin": "synthetic",
        "provider_version": "TEST_ONLY-v1",
        "collection_fingerprint": "a" * 64,
        "uncertainty": {"lower": "0", "upper": "1", "method_ref": "TEST_ONLY"},
        "limitations": ["TEST_ONLY"],
    }
    with pytest.raises(ValidationError):
        ProviderResult.model_validate(raw)


@pytest.mark.parametrize(
    "field", ["artifact_ref", "evaluation_ref", "uncertainty_ref", "training_run_id"]
)
def test_incomplete_owner_declarations(field):
    raw = metadata().model_dump(mode="json")
    raw.pop(field)
    with pytest.raises(ValidationError):
        ModelMetadata.model_validate(raw)


def test_unknown_units_are_explicit():
    raw = metadata().model_dump()
    raw["gravity"]["unit"] = "m/s2"
    assert "gravity_unit_unsupported" in domain_reasons(
        request().scenario, ModelMetadata.model_validate(raw), request().observable
    )


async def test_provider_exception_sanitized_and_cancellation_propagated():
    class Broken:
        origin = "synthetic"

        async def predict(self, call):
            raise RuntimeError("private-provider-credentials")

    with pytest.raises(PredictionFailure) as error:
        await execute_provider(Broken(), call(), 1)
    assert error.value.code == "PROVIDER_UNAVAILABLE"
    assert "private" not in str(error.value)

    class Cancelled:
        origin = "synthetic"

        async def predict(self, call):
            raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await execute_provider(Cancelled(), call(), 1)


async def test_adapter_cannot_mutate_validation_units():
    class Mutating(MockPredictionProvider):
        async def predict(self, call):
            call.metadata.observables[call.request.observable] = "wrong_unit"
            return await super().predict(call)

    with pytest.raises(PredictionFailure) as error:
        await execute_provider(Mutating(), call(), 1)
    assert error.value.status == 502


async def test_constructed_provider_result_is_revalidated():
    class Constructed(MockPredictionProvider):
        async def predict(self, call):
            valid = await super().predict(call)
            return valid.model_copy(update={"value": "NaN"})

    with pytest.raises(PredictionFailure) as error:
        await execute_provider(Constructed(), call(), 1)
    assert error.value.status == 502


@pytest.mark.parametrize("changed", ["training", "dataset", "provider"])
def test_readiness_checks_identity_bindings(changed):
    from app.integrations.prediction import ProviderRegistration

    registration = ProviderRegistration(
        provider_version="TEST_ONLY-provider",
        model_id=MODEL_ID,
        model_version="TEST_ONLY-v1",
        dataset_version=metadata().dataset_version,
        artifact_ref=metadata().artifact_ref,
        artifact_available=True,
    )
    provider = SimpleNamespace(origin="real", registration=registration)
    service = PredictionService(None, None, provider)
    config = {
        "origin": "synthetic",
        "reviewState": "unreviewed",
        "phase5DatasetVersion": metadata().dataset_version,
    }
    training = {
        "training_dataset_ref": metadata().dataset_version,
        "metrics_ref": metadata().evaluation_ref,
    }
    if changed == "training":
        training["metrics_ref"] = "TEST_ONLY-wrong"
        expected = "training_evaluation_binding_unavailable"
    elif changed == "dataset":
        config["phase5DatasetVersion"] = "TEST_ONLY-wrong"
        expected = "dataset_version_unavailable"
    else:
        provider.registration = registration.model_copy(update={"artifact_available": False})
        expected = "provider_model_binding_unavailable"
    result = service.assessment(
        MODEL_ID,
        (
            config,
            {"version": "TEST_ONLY-v1", "validation_status": "validated"},
            metadata(),
            training,
            "fixture",
        ),
    )
    assert result.state == "not_ready"
    assert expected in result.reasons


def test_expired_model_remains_not_ready():
    from datetime import UTC, datetime

    declaration = metadata().model_copy(
        update={"validation_expires_at": datetime(2000, 1, 1, tzinfo=UTC)}
    )
    service = PredictionService(None, None, MockPredictionProvider())
    snapshot = (
        {"origin": "synthetic", "reviewState": "unreviewed"},
        {"version": "TEST_ONLY-v1", "validation_status": "validated"},
        declaration,
        None,
        "fixture",
    )
    assert "model_validation_expired" in service.assessment(MODEL_ID, snapshot).reasons


@pytest.mark.parametrize("value", [None, "2100-01-01T00:00:00"])
def test_expiry_requires_aware_owner_declaration(value):
    raw = metadata().model_dump(mode="json")
    raw["validation_expires_at"] = value
    with pytest.raises(ValidationError):
        ModelMetadata.model_validate(raw)
