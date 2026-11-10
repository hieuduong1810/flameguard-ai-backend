"""Approved ERD entities; physical choices are recorded in docs/database-implementation.md."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as SQLUUID
from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.catalog import TestRun
    from app.models.prediction import PredictionResult


class Scenario(UUIDPrimaryKey, Base):
    __tablename__ = "scenario"

    name: Mapped[str] = mapped_column(Text(), nullable=False)
    environment: Mapped[str] = mapped_column(Text(), nullable=False)
    gravity: Mapped[str] = mapped_column(Text(), nullable=False)
    oxygen_pct: Mapped[Decimal] = mapped_column(Numeric(), nullable=False)
    pressure_psi: Mapped[Decimal] = mapped_column(Numeric(), nullable=False)
    material: Mapped[str] = mapped_column(Text(), nullable=False)
    ventilation: Mapped[str] = mapped_column(Text(), nullable=False)

    matches: Mapped[list[ScenarioMatch]] = relationship(
        "ScenarioMatch", back_populates="scenario", lazy="raise"
    )
    predictions: Mapped[list[PredictionResult]] = relationship(
        "PredictionResult", back_populates="scenario", lazy="raise"
    )


class ScenarioMatch(UUIDPrimaryKey, Base):
    __tablename__ = "scenario_match"

    scenario_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("scenario.id"), index=True, nullable=False
    )
    test_run_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("test_run.id"), index=True, nullable=False
    )
    match_status: Mapped[str] = mapped_column(Text(), nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric(), nullable=True)
    explanation: Mapped[str] = mapped_column(Text(), nullable=False)
    engine_version: Mapped[str] = mapped_column(Text(), nullable=False)

    scenario: Mapped[Scenario] = relationship("Scenario", back_populates="matches", lazy="raise")
    test_run: Mapped[TestRun] = relationship(
        "TestRun", back_populates="scenario_matches", lazy="raise"
    )
    dimensions: Mapped[list[MatchDimension]] = relationship(
        "MatchDimension", back_populates="scenario_match", lazy="raise"
    )


class MatchDimension(UUIDPrimaryKey, Base):
    __tablename__ = "match_dimension"

    scenario_match_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("scenario_match.id"), index=True, nullable=False
    )
    variable: Mapped[str] = mapped_column(Text(), nullable=False)
    match_status: Mapped[str] = mapped_column(Text(), nullable=False)
    gap_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)

    scenario_match: Mapped[ScenarioMatch] = relationship(
        "ScenarioMatch", back_populates="dimensions", lazy="raise"
    )
