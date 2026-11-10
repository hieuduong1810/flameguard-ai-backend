"""Scalar persistence contracts, not frontend projection or scientific validation schemas."""

from datetime import datetime
from decimal import Decimal
from typing import ClassVar
from uuid import UUID

from app.schemas.base import PatchSchema, Schema


class ModelVersionCreate(Schema):
    model_name: str
    version: str
    validation_status: str
    applicability_domain: str | None = None


class ModelVersionUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("model_name", "version", "validation_status")
    )
    model_name: str | None = None
    version: str | None = None
    validation_status: str | None = None
    applicability_domain: str | None = None


class ModelVersionRead(ModelVersionCreate):
    id: UUID


class ModelTrainingRunCreate(Schema):
    model_version_id: UUID
    training_dataset_ref: str
    metrics_ref: str | None = None
    trained_at: datetime


class ModelTrainingRunUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("model_version_id", "training_dataset_ref", "trained_at")
    )
    model_version_id: UUID | None = None
    training_dataset_ref: str | None = None
    metrics_ref: str | None = None
    trained_at: datetime | None = None


class ModelTrainingRunRead(ModelTrainingRunCreate):
    id: UUID


class PredictionResultCreate(Schema):
    scenario_id: UUID
    model_version_id: UUID
    predicted_observable: str
    predicted_value: Decimal
    unit: str
    uncertainty: Decimal | None = None
    applicability_status: str


class PredictionResultUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        (
            "scenario_id",
            "model_version_id",
            "predicted_observable",
            "predicted_value",
            "unit",
            "applicability_status",
        )
    )
    scenario_id: UUID | None = None
    model_version_id: UUID | None = None
    predicted_observable: str | None = None
    predicted_value: Decimal | None = None
    unit: str | None = None
    uncertainty: Decimal | None = None
    applicability_status: str | None = None


class PredictionResultRead(PredictionResultCreate):
    id: UUID
