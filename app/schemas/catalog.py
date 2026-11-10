"""Scalar persistence contracts, not frontend projection or scientific validation schemas."""

from decimal import Decimal
from typing import ClassVar
from uuid import UUID

from app.schemas.base import PatchSchema, Schema


class InvestigationCreate(Schema):
    psi_id: str
    title: str
    research_purpose: str | None = None
    platform: str | None = None


class InvestigationUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(("psi_id", "title"))
    psi_id: str | None = None
    title: str | None = None
    research_purpose: str | None = None
    platform: str | None = None


class InvestigationRead(InvestigationCreate):
    id: UUID


class TestRunCreate(Schema):
    investigation_id: UUID
    external_run_key: str | None = None
    material_type: str | None = None
    sample_geometry: str | None = None
    gravity: str | None = None


class TestRunUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(("investigation_id",))
    investigation_id: UUID | None = None
    external_run_key: str | None = None
    material_type: str | None = None
    sample_geometry: str | None = None
    gravity: str | None = None


class TestRunRead(TestRunCreate):
    id: UUID


class TestConditionCreate(Schema):
    test_run_id: UUID
    variable: str
    value_numeric: Decimal | None = None
    value_text: str | None = None
    unit: str | None = None
    data_status: str


class TestConditionUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("test_run_id", "variable", "data_status")
    )
    test_run_id: UUID | None = None
    variable: str | None = None
    value_numeric: Decimal | None = None
    value_text: str | None = None
    unit: str | None = None
    data_status: str | None = None


class TestConditionRead(TestConditionCreate):
    id: UUID


class MeasurementCreate(Schema):
    test_run_id: UUID
    observable: str
    measured_value: Decimal | None = None
    unit: str
    raw_asset_ref: str | None = None
    uncertainty: Decimal | None = None


class MeasurementUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(("test_run_id", "observable", "unit"))
    test_run_id: UUID | None = None
    observable: str | None = None
    measured_value: Decimal | None = None
    unit: str | None = None
    raw_asset_ref: str | None = None
    uncertainty: Decimal | None = None


class MeasurementRead(MeasurementCreate):
    id: UUID


class TagCreate(Schema):
    slug: str
    label: str
    category: str | None = None


class TagUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(("slug", "label"))
    slug: str | None = None
    label: str | None = None
    category: str | None = None


class TagRead(TagCreate):
    id: UUID


class InvestigationTagCreate(Schema):
    investigation_id: UUID
    tag_id: UUID


class InvestigationTagUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(("investigation_id", "tag_id"))
    investigation_id: UUID | None = None
    tag_id: UUID | None = None


class InvestigationTagRead(InvestigationTagCreate):
    id: UUID
