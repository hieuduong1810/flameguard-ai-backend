"""Public Phase 4 contracts. Independent of ORM/persistence schemas."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator, model_validator
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="forbid", allow_inf_nan=False
    )

    @field_validator("*", mode="after")
    @classmethod
    def utc_originals(cls, value):
        if isinstance(value, datetime):
            if value.utcoffset() is None:
                raise ValueError("Timestamp must include timezone")
            return value.astimezone(UTC)
        return value


DecimalString = Annotated[StrictStr, Field(pattern="^-?(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?$")]
UnavailableFields = dict[
    str,
    Literal[
        "MISSING_SOURCE_DATA",
        "UNSUPPORTED_MAPPING",
        "VERIFICATION_NOT_ESTABLISHED",
        "SCIENTIFIC_COMPARISON_NOT_APPROVED",
        "NO_DENOMINATOR",
        "ASSET_CONTRACT_PENDING",
    ],
]


class TagPage(ApiModel):
    items: list[Tag]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class Error(ApiModel):
    error: ErrorError
    context: Context


class ErrorError(ApiModel):
    code: str
    message: str
    fields: list[str]
    supported_values: list[str]


class Comparison(ApiModel):
    studies: Annotated[list[ComparisonStudy], Field(min_length=2, max_length=3)]
    deltas: None
    highlights: None
    comparability: Literal["not_established"]
    unavailable_fields: UnavailableFields
    context: Context


class ComparisonStudy(ApiModel):
    investigation: Investigation
    observations: ObservationPage
    context: Context


class CompareRequest(ApiModel):
    investigation_ids: Annotated[
        list[UUID], Field(min_length=2, max_length=3, json_schema_extra={"uniqueItems": True})
    ]
    observation_offset: Annotated[int, Field(ge=0)] = 0
    observation_limit: Annotated[int, Field(ge=1, le=100)] = 20

    @model_validator(mode="after")
    def distinct_ids(self):
        if len(set(self.investigation_ids)) != len(self.investigation_ids):
            raise ValueError("Investigation IDs must be distinct")
        return self


class Capabilities(ApiModel):
    supported_filters: list[str]
    supported_sorts: list[str]
    unsupported_filters: list[str]
    unsupported_sorts: list[str]
    unavailable_display_fields: list[str]
    max_page_size: Literal[100]
    context: Context


class Dashboard(ApiModel):
    selection: dict[str, str]
    investigation_count: Annotated[int, Field(ge=0)]
    run_count: Annotated[int, Field(ge=0)]
    claim_count: Annotated[int, Field(ge=0)]
    source_count: Annotated[int, Field(ge=0)]
    verified_run_count: None
    source_coverage: Coverage
    fuel_distribution: None
    facility_distribution: None
    gravity_distribution: None
    featured_investigations: Annotated[list[Investigation], Field(max_length=3)]
    unavailable_fields: UnavailableFields
    context: Context


class Coverage(ApiModel):
    numerator: Annotated[int, Field(ge=0)]
    denominator: Annotated[int, Field(ge=0)]
    ratio: DecimalString | None


class ClaimPage(ApiModel):
    items: list[Claim]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class Claim(ApiModel):
    id: UUID
    claim_text: str
    evidence_status: str
    review_status: str
    limitation: str | None
    created_at: datetime
    sources: ClaimSourcePage
    context: Context


class ClaimSourcePage(ApiModel):
    items: list[ClaimSource]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class SourcePage(ApiModel):
    items: list[Source]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class ObservationPage(ApiModel):
    items: list[Observation]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class MeasurementPage(ApiModel):
    items: list[Measurement]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class ConditionPage(ApiModel):
    items: list[Condition]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class RunPage(ApiModel):
    items: list[Run]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class InvestigationPage(ApiModel):
    items: list[Investigation]
    total: Annotated[int, Field(ge=0)]
    offset: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    next: str | None
    context: Context


class ClaimSource(ApiModel):
    id: UUID
    claim_id: UUID
    source: Source
    test_run_id: UUID | None
    run_investigation_id: UUID | None
    source_locator: str
    source_excerpt: str | None
    context_mismatch: bool
    context: Context


class Source(ApiModel):
    id: UUID
    investigation_id: UUID
    source_url: str
    doi: str | None
    document_type: str
    version: str | None
    ingestion_status: str
    context: Context


class Observation(ApiModel):
    measurement: Measurement
    run: Run
    context: Context


class Measurement(ApiModel):
    id: UUID
    test_run_id: UUID
    observable: str
    measured_value: DecimalString | None
    unit: str
    raw_asset_ref: str | None
    uncertainty: DecimalString | None
    unavailable_fields: UnavailableFields
    context: Context


class Condition(ApiModel):
    id: UUID
    test_run_id: UUID
    variable: str
    value_numeric: DecimalString | None
    value_text: str | None
    unit: str | None
    data_status: str
    context: Context


class Run(ApiModel):
    id: UUID
    investigation_id: UUID
    external_run_key: str | None
    material_type: str | None
    sample_geometry: str | None
    gravity: str | None
    verification: Literal["unknown"]
    unavailable_fields: UnavailableFields
    conditions: CollectionLink
    measurements: CollectionLink
    context: Context


class InvestigationDetail(ApiModel):
    id: UUID
    psi_id: str
    slug: str | None
    title: str
    research_purpose: str | None
    platform: str | None
    tags: TagPage
    unavailable_fields: UnavailableFields
    context: Context
    runs: CollectionLink
    sources: CollectionLink
    claims: CollectionLink


class Investigation(ApiModel):
    id: UUID
    psi_id: str
    slug: str | None
    title: str
    research_purpose: str | None
    platform: str | None
    tags: TagPage
    unavailable_fields: UnavailableFields
    context: Context


class Tag(ApiModel):
    id: UUID
    slug: str
    label: str
    category: str | None
    context: Context


class CollectionLink(ApiModel):
    href: str
    total: Annotated[int, Field(ge=0)]


class Context(ApiModel):
    collection_id: str
    origin: Literal["synthetic", "real", "unknown"]
    review_state: Literal["unreviewed", "curated", "unknown"]
    caveats: list[str]


for _model in list(globals().values()):
    if isinstance(_model, type) and issubclass(_model, ApiModel):
        _model.model_rebuild()
