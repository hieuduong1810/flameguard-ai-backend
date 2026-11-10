"""Scalar persistence contracts, not frontend projection or scientific validation schemas."""

from decimal import Decimal
from typing import ClassVar
from uuid import UUID

from app.schemas.base import PatchSchema, Schema


class ScenarioCreate(Schema):
    name: str
    environment: str
    gravity: str
    oxygen_pct: Decimal
    pressure_psi: Decimal
    material: str
    ventilation: str


class ScenarioUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("name", "environment", "gravity", "oxygen_pct", "pressure_psi", "material", "ventilation")
    )
    name: str | None = None
    environment: str | None = None
    gravity: str | None = None
    oxygen_pct: Decimal | None = None
    pressure_psi: Decimal | None = None
    material: str | None = None
    ventilation: str | None = None


class ScenarioRead(ScenarioCreate):
    id: UUID


class ScenarioMatchCreate(Schema):
    scenario_id: UUID
    test_run_id: UUID
    match_status: str
    score: Decimal | None = None
    explanation: str
    engine_version: str


class ScenarioMatchUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("scenario_id", "test_run_id", "match_status", "explanation", "engine_version")
    )
    scenario_id: UUID | None = None
    test_run_id: UUID | None = None
    match_status: str | None = None
    score: Decimal | None = None
    explanation: str | None = None
    engine_version: str | None = None


class ScenarioMatchRead(ScenarioMatchCreate):
    id: UUID


class MatchDimensionCreate(Schema):
    scenario_match_id: UUID
    variable: str
    match_status: str
    gap_reason: str | None = None


class MatchDimensionUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("scenario_match_id", "variable", "match_status")
    )
    scenario_match_id: UUID | None = None
    variable: str | None = None
    match_status: str | None = None
    gap_reason: str | None = None


class MatchDimensionRead(MatchDimensionCreate):
    id: UUID
