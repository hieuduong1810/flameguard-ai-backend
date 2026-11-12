import json
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, StringConstraints, field_validator

from app.integrations.scenario_evidence.execution import (
    MAX_ENTRIES,
    ProviderFailure,
    decode,
    reject,
)
from app.integrations.scenario_evidence.models import ProviderRequest
from app.schemas.api.scenarios import (
    DecimalText,
    Fingerprint,
    FixtureLabel,
    InvestigationIdentity,
    Pillar,
    RankedInvestigation,
    RankingComponent,
    ScoreScale,
    WireInput,
)

FIXTURE_COLLECTION = "synthetic-phase4-v1"
FIXTURE_DATASET = "TEST_ONLY_fixture-v1"
RANKING_VERSION = "TEST_ONLY_fixed-ranking-v1"
CONTRACT_VERSION = "TEST_ONLY_ranking-contract-v1"
DELIVERY_ID = "TEST_ONLY_fixed-delivery-v1"
APPLICABILITY = "TEST_ONLY fixed scenario and material"
CAVEAT = "TEST_ONLY fixture scores for engineering only"
RATIONALE = "TEST_ONLY pre-authored ranking order and tie"
PROVENANCE = "TEST_ONLY fixed ranking fixture"

SCALES = (
    ScoreScale(
        kind="scenario_relevance",
        minimum="0",
        maximum="100",
        meaning="TEST_ONLY scenario relevance for the declared fixture scenario",
    ),
    ScoreScale(
        kind="catalog_usefulness",
        minimum="0",
        maximum="5",
        meaning="TEST_ONLY catalog usefulness independent of the scenario",
    ),
    ScoreScale(
        kind="fixture_component",
        minimum="0",
        maximum="1",
        meaning="TEST_ONLY supplied component scale",
    ),
)
UUIDText = Annotated[str, StringConstraints(min_length=32, max_length=45)]
FixtureIdentity = Annotated[str, StringConstraints(min_length=1, max_length=120)]
Position = Annotated[int, Field(ge=1, le=MAX_ENTRIES)]


class Entry(WireInput):
    position: Position
    rank: Position
    investigation_id: UUIDText
    psi_id: FixtureIdentity
    slug: FixtureIdentity | None
    external_experiment_id: FixtureIdentity
    scenario_relevance_score: DecimalText
    catalog_usefulness_score: DecimalText | None
    condition_component: DecimalText
    context_component: DecimalText | None
    rationale: Literal[RATIONALE]


class Delivery(WireInput):
    complete: Literal[True]
    contract_version: Literal[CONTRACT_VERSION]
    delivery_id: Literal[DELIVERY_ID]
    algorithm_version: Literal[RANKING_VERSION]
    dataset_version: FixtureIdentity
    collection_id: FixtureIdentity
    collection_fingerprint: Fingerprint
    identity_version: FixtureIdentity | None
    mapping_version: FixtureIdentity
    scenario_digest: Fingerprint
    material_key: Literal["TEST_MATERIAL_A"]
    pillar: Pillar | None
    origin: Literal["synthetic"]
    review_state: Literal["unreviewed"]
    applicability: Literal[APPLICABILITY]
    caveat: Literal[CAVEAT]
    entries: Annotated[list[Entry], Field(max_length=MAX_ENTRIES)]

    @field_validator("complete", mode="before")
    @classmethod
    def declared_complete(cls, value):
        if value is not True:
            raise ValueError("Complete delivery must be explicitly declared")
        return value


FIXTURE_ROWS = (
    (
        "e1a75331-3f1f-57b8-9042-405ff61dff51",
        "SYNTHETIC-PHASE4-1",
        "synthetic-study-1",
        "TEST_ONLY_EXPERIMENT_1",
        "3.00",
        "0.70",
        None,
    ),
    (
        "afa58280-0d0c-58a3-926a-1499a1e20a96",
        "SYNTHETIC-PHASE4-2",
        "synthetic-study-2",
        "TEST_ONLY_EXPERIMENT_2",
        None,
        "0.70",
        "0",
    ),
)


def fixture_applicable(request: ProviderRequest) -> bool:
    scenario = request.scenario
    return (
        request.test_only
        and request.scope.collection_id == FIXTURE_COLLECTION
        and request.scope.dataset_version == FIXTURE_DATASET
        and request.scope.pillar in {None, "prevention"}
        and scenario.preset_key is None
        and scenario.material is not None
        and scenario.material.key == "TEST_MATERIAL_A"
        and scenario.gravity is not None
        and Decimal(scenario.gravity.value) == 0
        and scenario.oxygen is not None
        and Decimal(scenario.oxygen.value) == 21
        and scenario.oxygen.meaning == "ambient_oxygen_fraction_percent"
        and scenario.pressure is not None
        and Decimal(scenario.pressure.value) == Decimal("14.7")
        and scenario.airflow is not None
        and Decimal(scenario.airflow.value) == 0
    )


class FixedRanking:
    version = RANKING_VERSION

    async def rank(self, request: ProviderRequest) -> bytes | None:
        if not fixture_applicable(request):
            return None
        scope = request.scope
        return json.dumps(
            {
                "complete": True,
                "contractVersion": CONTRACT_VERSION,
                "deliveryId": DELIVERY_ID,
                "algorithmVersion": RANKING_VERSION,
                "datasetVersion": scope.dataset_version,
                "collectionId": scope.collection_id,
                "collectionFingerprint": scope.collection_fingerprint,
                "identityVersion": scope.identity_version,
                "mappingVersion": scope.scenario_mapping_version,
                "scenarioDigest": scope.scenario_digest,
                "materialKey": "TEST_MATERIAL_A",
                "pillar": scope.pillar,
                "origin": "synthetic",
                "reviewState": "unreviewed",
                "applicability": APPLICABILITY,
                "caveat": CAVEAT,
                "entries": [
                    {
                        "position": position,
                        "rank": 1,
                        "investigationId": uid,
                        "psiId": psi,
                        "slug": slug,
                        "externalExperimentId": external,
                        "scenarioRelevanceScore": "70.00",
                        "catalogUsefulnessScore": usefulness,
                        "conditionComponent": condition,
                        "contextComponent": context,
                        "rationale": RATIONALE,
                    }
                    for position, (
                        uid,
                        psi,
                        slug,
                        external,
                        usefulness,
                        condition,
                        context,
                    ) in enumerate(FIXTURE_ROWS, 1)
                ],
            }
        ).encode()


def validate_ranking(
    payload: bytes,
    request: ProviderRequest,
    identities: tuple[InvestigationIdentity, ...],
) -> tuple[Delivery, tuple[RankedInvestigation, ...]]:
    delivery = decode(payload, Delivery)
    scope = request.scope
    if (
        delivery.dataset_version != scope.dataset_version
        or delivery.identity_version != scope.identity_version
        or delivery.mapping_version != scope.scenario_mapping_version
        or delivery.collection_id != scope.collection_id
        or delivery.collection_fingerprint != scope.collection_fingerprint
        or delivery.scenario_digest != scope.scenario_digest
        or delivery.pillar != scope.pillar
    ):
        raise ProviderFailure("PROVIDER_VERSION_CONFLICT", rejected=True)
    if not fixture_applicable(request):
        raise reject()

    known = {identity.investigation_id: identity for identity in identities}
    external = {UUID(row[0]): row[3] for row in FIXTURE_ROWS}
    seen = set()
    ranked = []
    label = FixtureLabel(
        collection_id=scope.collection_id,
        dataset_version=delivery.dataset_version,
        provider_version=delivery.algorithm_version,
    )
    previous_rank = 1
    for position, entry in enumerate(delivery.entries, 1):
        try:
            uid = UUID(entry.investigation_id)
        except ValueError:
            raise reject() from None
        identity = known.get(uid)
        if (
            identity is None
            or uid in seen
            or entry.position != position
            or entry.rank not in {position, previous_rank}
            or entry.psi_id != identity.psi_id
            or entry.slug != identity.slug
            or entry.external_experiment_id != external.get(uid)
            or not _score(entry.scenario_relevance_score, SCALES[0])
            or not _score(entry.catalog_usefulness_score, SCALES[1])
            or not _score(entry.condition_component, SCALES[2])
            or not _score(entry.context_component, SCALES[2])
        ):
            raise reject()
        seen.add(uid)
        previous_rank = entry.rank
        ranked.append(
            RankedInvestigation(
                position=entry.position,
                rank=entry.rank,
                investigation=identity,
                external_experiment_id=entry.external_experiment_id,
                scenario_relevance_score=entry.scenario_relevance_score,
                catalog_usefulness_score=entry.catalog_usefulness_score,
                components=(
                    RankingComponent(
                        name="fixture_condition",
                        value=entry.condition_component,
                        provenance=PROVENANCE,
                    ),
                    RankingComponent(
                        name="fixture_context", value=entry.context_component, provenance=PROVENANCE
                    ),
                ),
                rationale=entry.rationale,
                context=label,
            )
        )
    if seen != external.keys():
        raise reject()
    return delivery, tuple(ranked)


def _score(value: str | None, scale: ScoreScale) -> bool:
    return value is None or Decimal(scale.minimum) <= Decimal(value) <= Decimal(scale.maximum)
