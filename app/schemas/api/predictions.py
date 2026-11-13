"""Prediction transport and owner-declared metadata. No scientific defaults."""

from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints, model_validator
from pydantic.alias_generators import to_camel

from app.schemas.api.scenarios import Label, Output, ScenarioInput

Number = Annotated[
    str, StringConstraints(max_length=64, pattern=r"^-?(0|[1-9][0-9]*)(\.[0-9]{1,32})?$")
]


class Declaration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, revalidate_instances="always")


class Range(Declaration):
    minimum: Number
    maximum: Number
    unit: Label

    @model_validator(mode="after")
    def ordered(self):
        if Decimal(self.minimum) > Decimal(self.maximum):
            raise ValueError("Reversed domain bounds")
        return self


class ModelMetadata(Declaration):
    schema_version: Literal[1]
    artifact_ref: Label
    training_run_id: UUID
    dataset_version: Label
    evaluation_ref: Label
    uncertainty_ref: Label
    validation_expires_at: AwareDatetime
    materials: tuple[Label, ...] = Field(min_length=1, max_length=100)
    gravity: Range
    oxygen: Range
    oxygen_meaning: Literal["ambient_oxygen_fraction_percent", "oxidizer_oxygen_fraction_percent"]
    pressure: Range
    airflow: Range
    observables: dict[Label, Label] = Field(min_length=1, max_length=30)
    limitations: tuple[Label, ...] = Field(min_length=1, max_length=30)


class PredictionRequest(Output):
    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True, frozen=True
    )
    model_id: UUID
    expected_model_version: Label
    expected_dataset_version: Label
    observable: Label
    scenario: ScenarioInput


class Readiness(Output):
    state: Literal["ready", "not_ready"] = "not_ready"
    reasons: list[str]
    model_id: UUID | None = None
    model_version: str | None = None
    dataset_version: str | None = None
    origin: Literal["synthetic", "real", "unknown"] = "unknown"
    capabilities: dict[str, str] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)


class Uncertainty(Declaration):
    lower: Number
    upper: Number
    method_ref: Label

    @model_validator(mode="after")
    def ordered(self):
        if Decimal(self.lower) > Decimal(self.upper):
            raise ValueError("Reversed uncertainty bounds")
        return self


class ProviderResult(Declaration):
    model_id: UUID
    model_version: Label
    dataset_version: Label
    observable: Label
    value: Number
    unit: Label
    origin: Literal["synthetic", "real"]
    provider_version: Label
    collection_fingerprint: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    uncertainty: Uncertainty
    limitations: tuple[Label, ...] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def interval(self):
        if (
            not Decimal(self.uncertainty.lower)
            <= Decimal(self.value)
            <= Decimal(self.uncertainty.upper)
        ):
            raise ValueError("Value outside supplied uncertainty bounds")
        return self


class PredictionResponse(Output):
    state: Literal["not_ready", "unsupported", "predicted"]
    readiness: Readiness
    reasons: list[str]
    result: ProviderResult | None = None


class PredictionErrorDetail(Output):
    code: str


class PredictionError(Output):
    error: PredictionErrorDetail
