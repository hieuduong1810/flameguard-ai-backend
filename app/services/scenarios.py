import asyncio
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.integrations.scenario_evidence.config import ScenarioProviders
from app.integrations.scenario_evidence.execution import ProviderFailure, execute
from app.integrations.scenario_evidence.models import (
    AssociationRecord,
    ProviderRequest,
    RunEvidence,
)
from app.integrations.scenario_evidence.run_policy import validate_decisions
from app.repositories.phase5_scenarios import ScenarioEvidenceRepository
from app.schemas.api.scenarios import (
    DIMS,
    Bindings,
    ConditionEvidence,
    Coverage,
    Dimension,
    Evaluation,
    EvaluationRequest,
    EvidenceContext,
    FixtureLabel,
    InvestigationIdentity,
    RunEvaluation,
)
from app.services.collection import admit_collection, collection_context
from app.services.errors import Phase4Error
from app.services.scenario_interpretation import SCENARIO_MAPPING_VERSION, fingerprint, interpret
from app.services.scenario_pillars import pillar_section
from app.services.scenario_rankings import ranking_section
from app.services.scenario_traversal import (
    check_deliveries,
    check_snapshot,
    page_for,
    require_replay,
    summarize,
)
from app.services.unit_of_work import read_unit_of_work


@dataclass(frozen=True, slots=True)
class Snapshot:
    context: EvidenceContext
    scope: Bindings
    providers: ScenarioProviders
    total_runs: int
    runs: tuple[RunEvidence, ...]
    identities: tuple[InvestigationIdentity, ...] | None
    associations: tuple[AssociationRecord, ...] | None


class ScenarioService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        settings: Settings,
        providers: ScenarioProviders,
    ) -> None:
        self.session_factory = session_factory
        self.settings = settings
        self.providers = providers

    async def snapshot(self, request: EvaluationRequest, digest: str) -> Snapshot:
        if not self.settings.catalog_collection_manifest:
            raise Phase4Error("COLLECTION_SCOPE_INVALID")
        async with self.session_factory() as session, read_unit_of_work(session):
            config, slugs = await admit_collection(session, self.settings, capture_content=True)
            context = EvidenceContext.model_validate(collection_context(config))
            providers = self.providers.for_context(context)
            if not config["phase5DatasetVersion"]:
                providers = ScenarioProviders()
            scope = Bindings.model_validate(
                {
                    "scenarioDigest": digest,
                    "collectionFingerprint": fingerprint(
                        {
                            "version": 1,
                            "storedContent": config["phase5ContentHash"],
                            "context": context.model_dump(mode="json"),
                            "slugs": slugs,
                        }
                    ),
                    "collectionId": context.collection_id,
                    "datasetVersion": config["phase5DatasetVersion"],
                    "identityVersion": config["phase5IdentityVersion"],
                    "scenarioMappingVersion": SCENARIO_MAPPING_VERSION,
                    "mappingVersion": providers.run_policy.mapping_version
                    if providers.run_policy
                    else None,
                    "ruleVersion": providers.run_policy.version if providers.run_policy else None,
                    "classificationVersion": (
                        providers.classifications.version if providers.classifications else None
                    ),
                    "pillar": request.pillar,
                }
            )
            check_snapshot(request, scope)
            repo = ScenarioEvidenceRepository(session, slugs)
            total, runs = (
                await repo.runs(request.pages.run_offset, request.pages.limit)
                if providers.run_policy
                else (0, ())
            )
            identities = await repo.ranking_identities() if providers.rankings else ()
            associations = (
                await repo.associations(providers.classifications.claim_ids)
                if providers.classifications
                else ()
            )
            return Snapshot(context, scope, providers, total, runs, identities, associations)

    async def evaluate(self, request: EvaluationRequest) -> Evaluation:
        require_replay(request)
        interpreted = interpret(request.scenario)
        snapshot = await self.snapshot(request, interpreted.digest)
        provider_request = ProviderRequest(snapshot.scope, request.scenario, snapshot.context)
        (
            coverage,
            (rankings, ranking_digest),
            (pillars, classification_digest),
        ) = await asyncio.gather(
            coverage_section(snapshot, provider_request, request),
            ranking_section(
                snapshot.providers.rankings, provider_request, request, snapshot.identities
            ),
            pillar_section(
                snapshot.providers.classifications,
                provider_request,
                request,
                snapshot.associations,
            ),
        )
        scope = snapshot.scope.model_copy(
            update={
                "ranking_fingerprint": ranking_digest,
                "classification_fingerprint": classification_digest,
            }
        )
        check_deliveries(request, scope)
        return Evaluation(
            scenario=interpreted,
            context=snapshot.context,
            scope=scope,
            coverage=coverage,
            rankings=rankings,
            pillar_evidence=pillars,
        )


def unavailable_coverage(reason: str, rejected: bool = False) -> Coverage:
    return Coverage(
        state="rejected" if rejected else "unavailable",
        reason_codes=(reason,),
        items=None,
        page=None,
        examined_runs=0,
        required_conditions_complete=None,
        collection_traversal_complete=False,
        dimensions=tuple(
            Dimension(dimension=name, status="unavailable", reason_codes=(reason,)) for name in DIMS
        ),
    )


async def coverage_section(
    snapshot: Snapshot,
    provider_request: ProviderRequest,
    request: EvaluationRequest,
) -> Coverage:
    policy = snapshot.providers.run_policy
    if policy is None:
        reason = (
            "RULE_POLICY_UNAVAILABLE"
            if snapshot.context.origin == "synthetic"
            else "SCIENTIFIC_REVIEW_NOT_ACCEPTED"
        )
        return unavailable_coverage(reason)
    try:
        supplied = await execute(policy.evaluate(provider_request, snapshot.runs))
        decisions = validate_decisions(provider_request, snapshot.runs, supplied)
    except ProviderFailure as exc:
        return unavailable_coverage(exc.code, exc.rejected)
    scope = snapshot.scope
    label = FixtureLabel(
        collection_id=scope.collection_id,
        dataset_version=scope.dataset_version,
        provider_version=policy.version,
    )
    items = tuple(
        RunEvaluation(
            run=run.run,
            dimensions=dimension_results,
            conditions=tuple(
                ConditionEvidence(**condition.model_dump(), context=label)
                for condition in run.conditions
            ),
            required_conditions_complete=run.complete,
            context=label,
        )
        for run, dimension_results in zip(snapshot.runs, decisions, strict=True)
    )
    complete = all(run.complete for run in snapshot.runs)
    page = page_for(request, scope, "run_offset", snapshot.total_runs)
    return Coverage(
        state="evaluated",
        reason_codes=(
            ("NO_RUNS_IN_EXAMINED_PAGE",)
            if not items
            else ("CONDITION_LIMIT_EXCEEDED",)
            if not complete
            else ()
        ),
        items=items,
        dimensions=summarize(items),
        page=page,
        examined_runs=len(items),
        required_conditions_complete=complete,
        collection_traversal_complete=page.offset == 0 and len(items) == page.total and complete,
    )
