from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from pydantic.alias_generators import to_camel

DimensionName = Literal["gravity", "material", "oxygen", "pressure", "airflow", "combined"]
Pillar = Literal["prevention", "detection", "suppression"]
Origin = Literal["synthetic", "real", "unknown"]
ReviewState = Literal["unreviewed", "unknown"]
SectionState = Literal["evaluated", "unavailable", "rejected"]
Status = Literal["support", "mismatch", "partial", "unknown", "unavailable"]
DIMS: tuple[DimensionName, ...] = (
    "gravity",
    "material",
    "oxygen",
    "pressure",
    "airflow",
    "combined",
)
PILLARS: tuple[Pillar, ...] = ("prevention", "detection", "suppression")
DecimalText = Annotated[
    str, StringConstraints(max_length=64, pattern=r"^(0|[1-9][0-9]*)(\.[0-9]{1,32})?$")
]
Label = Annotated[str, StringConstraints(min_length=1, max_length=120)]
Token = Annotated[
    str, StringConstraints(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
]
Fingerprint = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
MAX_OFFSET = 1_000_000
Offset = Annotated[int, Field(ge=0, le=MAX_OFFSET)]
PageSize = Annotated[int, Field(ge=1, le=100)]


class WireInput(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, extra="forbid", frozen=True, strict=True)


class Output(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, frozen=True)


class Gravity(WireInput):
    value: DecimalText
    unit: Literal["g"]


class Oxygen(WireInput):
    value: DecimalText
    unit: Literal["%"]
    meaning: Literal["ambient_oxygen_fraction_percent", "oxidizer_oxygen_fraction_percent"]

    @field_validator("value")
    @classmethod
    def percentage(cls, value: str) -> str:
        if Decimal(value) > 100:
            raise ValueError("Oxygen percentage exceeds 100")
        return value


class Pressure(WireInput):
    value: DecimalText
    unit: Literal["psia"]


class Airflow(WireInput):
    value: DecimalText
    unit: Literal["cm/s"]


class Material(WireInput):
    key: Token
    label: Label | None = None


class ScenarioInput(WireInput):
    name: Label | None = None
    description: Annotated[str, StringConstraints(max_length=2000)] | None = None
    environment_label: Label | None = None
    preset_key: Token | None = None
    material: Material | None = None
    gravity: Gravity | None = None
    oxygen: Oxygen | None = None
    pressure: Pressure | None = None
    airflow: Airflow | None = None


class Pages(WireInput):
    run_offset: Offset = 0
    ranking_offset: Offset = 0
    evidence_offset: Offset = 0
    limit: PageSize = 20


class Bindings(WireInput):
    scenario_digest: Fingerprint
    collection_fingerprint: Fingerprint
    collection_id: Label
    dataset_version: Label | None
    identity_version: Label | None
    scenario_mapping_version: Label
    mapping_version: Label | None
    rule_version: Label | None
    classification_version: Label | None
    pillar: Pillar | None
    ranking_fingerprint: Fingerprint | None = None
    classification_fingerprint: Fingerprint | None = None


class EvaluationRequest(WireInput):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "scenario": {
                        "name": "TEST_ONLY zero gravity",
                        "material": {"key": "TEST_MATERIAL_A"},
                        "gravity": {"value": "0.00", "unit": "g"},
                        "oxygen": {
                            "value": "21",
                            "unit": "%",
                            "meaning": "ambient_oxygen_fraction_percent",
                        },
                        "pressure": {"value": "14.7", "unit": "psia"},
                        "airflow": {"value": "0", "unit": "cm/s"},
                    },
                    "pages": {"limit": 1},
                }
            ]
        }
    )

    scenario: ScenarioInput
    pillar: Pillar | None = None
    pages: Pages = Pages()
    expected_bindings: Bindings | None = None


class Interpretation(Output):
    original: ScenarioInput
    digest: Fingerprint
    field_states: dict[str, Literal["omitted", "null", "supplied"]]
    unavailable_fields: tuple[DimensionName, ...]


class EvidenceContext(Output):
    collection_id: str
    origin: Origin
    review_state: ReviewState
    caveats: tuple[str, ...]


class FixtureLabel(Output):
    collection_id: str
    dataset_version: str
    provider_version: str
    origin: Literal["synthetic"] = "synthetic"
    review_state: Literal["unreviewed"] = "unreviewed"


class InvestigationIdentity(Output):
    investigation_id: UUID
    psi_id: str
    slug: str | None


class RunIdentity(Output):
    run_id: UUID
    external_run_key: str | None
    investigation: InvestigationIdentity
    material_type: str | None
    sample_geometry: str | None
    gravity: str | None


class OriginalCondition(Output):
    condition_id: UUID
    run_id: UUID
    variable: str
    value_numeric: Decimal | None
    value_text: str | None
    unit: str | None
    data_status: str
    uncertainty: None = None
    source_locator: None = None


class ConditionEvidence(OriginalCondition):
    context: FixtureLabel


class Dimension(Output):
    dimension: DimensionName
    status: Status
    reason_codes: tuple[str, ...]
    run_id: UUID | None = None
    condition_ids: tuple[UUID, ...] = ()


class RunEvaluation(Output):
    run: RunIdentity
    dimensions: Annotated[tuple[Dimension, ...], Field(min_length=6, max_length=6)]
    conditions: tuple[ConditionEvidence, ...]
    required_conditions_complete: bool
    context: FixtureLabel


class NextRequest(Output):
    pages: Pages
    expected_bindings: Bindings


class Page(Output):
    offset: int
    limit: int
    total: int
    next_request: NextRequest | None
    continuation_limited: bool


class Coverage(Output):
    state: SectionState
    reason_codes: tuple[str, ...]
    items: tuple[RunEvaluation, ...] | None
    dimensions: Annotated[tuple[Dimension, ...], Field(min_length=6, max_length=6)]
    page: Page | None
    examined_runs: int
    required_conditions_complete: bool | None
    collection_traversal_complete: bool
    summary_scope: Literal["examined_page"] = "examined_page"
    collection_conclusion: None = None


class ScoreScale(Output):
    kind: Literal["scenario_relevance", "catalog_usefulness", "fixture_component"]
    minimum: str
    maximum: str
    meaning: str


class RankingComponent(Output):
    name: str
    value: str | None
    provenance: str


class RankedInvestigation(Output):
    position: int
    rank: int
    investigation: InvestigationIdentity
    external_experiment_id: str
    scenario_relevance_score: str
    catalog_usefulness_score: str | None
    components: tuple[RankingComponent, ...]
    rationale: str
    context: FixtureLabel


class Rankings(Output):
    state: SectionState
    reason_codes: tuple[str, ...]
    items: tuple[RankedInvestigation, ...] | None = None
    page: Page | None = None
    delivery_id: str | None = None
    contract_version: str | None = None
    algorithm_version: str | None = None
    dataset_version: str | None = None
    identity_version: str | None = None
    mapping_version: str | None = None
    material_key: str | None = None
    applicability: str | None = None
    caveats: tuple[str, ...] = ()
    scales: tuple[ScoreScale, ...] = ()


class OriginalClaim(Output):
    claim_id: UUID
    claim_text: str
    evidence_status: str
    review_status: str
    limitation: str | None
    context: FixtureLabel


class OriginalDocument(Output):
    source_document_id: UUID
    investigation_id: UUID
    source_url: str
    doi: str | None
    document_type: str
    version: str | None
    ingestion_status: str
    context: FixtureLabel


class PillarAssociation(Output):
    association_id: UUID
    pillar: Pillar
    claim: OriginalClaim
    document: OriginalDocument
    test_run_id: UUID | None
    run_investigation_id: UUID | None
    source_locator: str
    source_excerpt: str | None
    reason_codes: tuple[str, ...]
    context: FixtureLabel


class PillarGroup(Output):
    pillar: Pillar
    total: int
    items: tuple[PillarAssociation, ...]
    reason_codes: tuple[str, ...]
    context: FixtureLabel


class PillarEvidence(Output):
    state: SectionState
    reason_codes: tuple[str, ...]
    groups: tuple[PillarGroup, ...] | None = None
    page: Page | None = None


class Evaluation(Output):
    scenario: Interpretation
    context: EvidenceContext
    scope: Bindings
    coverage: Coverage
    rankings: Rankings
    pillar_evidence: PillarEvidence


class EvaluationErrorDetail(Output):
    code: Literal[
        "INVALID_REQUEST",
        "VERSION_CONFLICT",
        "DATA_UNAVAILABLE",
        "COLLECTION_SCOPE_INVALID",
        "INTERNAL_ERROR",
    ]
    message: str
    fields: tuple[str, ...] = ()
    supported_values: tuple[str, ...] = ()


class EvaluationError(Output):
    error: EvaluationErrorDetail
    context: EvidenceContext
