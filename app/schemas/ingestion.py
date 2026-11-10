"""Scalar persistence contracts, not frontend projection or scientific validation schemas."""

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from app.schemas.base import PatchSchema, Schema


class IngestionJobCreate(Schema):
    source_uri: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None


class IngestionJobUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("source_uri", "status", "started_at")
    )
    source_uri: str | None = None
    status: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class IngestionJobRead(IngestionJobCreate):
    id: UUID


class ImportIssueCreate(Schema):
    ingestion_job_id: UUID
    severity: str
    field_name: str | None = None
    explanation: str
    review_status: str


class ImportIssueUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("ingestion_job_id", "severity", "explanation", "review_status")
    )
    ingestion_job_id: UUID | None = None
    severity: str | None = None
    field_name: str | None = None
    explanation: str | None = None
    review_status: str | None = None


class ImportIssueRead(ImportIssueCreate):
    id: UUID
