"""Approved ERD entities; physical choices are recorded in docs/database-implementation.md."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as SQLUUID
from sqlalchemy import DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.scenarios import Scenario


class ModelVersion(UUIDPrimaryKey, Base):
    __tablename__ = "model_version"

    model_name: Mapped[str] = mapped_column(Text(), nullable=False)
    version: Mapped[str] = mapped_column(Text(), nullable=False)
    validation_status: Mapped[str] = mapped_column(Text(), nullable=False)
    applicability_domain: Mapped[str | None] = mapped_column(Text(), nullable=True)

    training_runs: Mapped[list[ModelTrainingRun]] = relationship(
        "ModelTrainingRun", back_populates="model_version", lazy="raise"
    )
    predictions: Mapped[list[PredictionResult]] = relationship(
        "PredictionResult", back_populates="model_version", lazy="raise"
    )


class ModelTrainingRun(UUIDPrimaryKey, Base):
    __tablename__ = "model_training_run"

    model_version_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("model_version.id"), index=True, nullable=False
    )
    training_dataset_ref: Mapped[str] = mapped_column(Text(), nullable=False)
    metrics_ref: Mapped[str | None] = mapped_column(Text(), nullable=True)
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    model_version: Mapped[ModelVersion] = relationship(
        "ModelVersion", back_populates="training_runs", lazy="raise"
    )


class PredictionResult(UUIDPrimaryKey, Base):
    __tablename__ = "prediction_result"

    scenario_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("scenario.id"), index=True, nullable=False
    )
    model_version_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("model_version.id"), index=True, nullable=False
    )
    predicted_observable: Mapped[str] = mapped_column(Text(), nullable=False)
    predicted_value: Mapped[Decimal] = mapped_column(Numeric(), nullable=False)
    unit: Mapped[str] = mapped_column(Text(), nullable=False)
    uncertainty: Mapped[Decimal | None] = mapped_column(Numeric(), nullable=True)
    applicability_status: Mapped[str] = mapped_column(Text(), nullable=False)

    model_version: Mapped[ModelVersion] = relationship(
        "ModelVersion", back_populates="predictions", lazy="raise"
    )
    scenario: Mapped[Scenario] = relationship(
        "Scenario", back_populates="predictions", lazy="raise"
    )
