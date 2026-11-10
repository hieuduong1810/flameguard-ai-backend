"""Scalar persistence contracts, not frontend projection or scientific validation schemas."""

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from app.schemas.base import PatchSchema, Schema


class SourceDocumentCreate(Schema):
    investigation_id: UUID
    source_url: str
    doi: str | None = None
    document_type: str
    version: str | None = None
    ingestion_status: str


class SourceDocumentUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("investigation_id", "source_url", "document_type", "ingestion_status")
    )
    investigation_id: UUID | None = None
    source_url: str | None = None
    doi: str | None = None
    document_type: str | None = None
    version: str | None = None
    ingestion_status: str | None = None


class SourceDocumentRead(SourceDocumentCreate):
    id: UUID


class EvidenceClaimCreate(Schema):
    claim_text: str
    evidence_status: str
    review_status: str
    limitation: str | None = None


class EvidenceClaimUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("claim_text", "evidence_status", "review_status")
    )
    claim_text: str | None = None
    evidence_status: str | None = None
    review_status: str | None = None
    limitation: str | None = None


class EvidenceClaimRead(EvidenceClaimCreate):
    id: UUID
    created_at: datetime


class ClaimSourceCreate(Schema):
    claim_id: UUID
    source_document_id: UUID
    test_run_id: UUID | None = None
    source_locator: str
    source_excerpt: str | None = None


class ClaimSourceUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("claim_id", "source_document_id", "source_locator")
    )
    claim_id: UUID | None = None
    source_document_id: UUID | None = None
    test_run_id: UUID | None = None
    source_locator: str | None = None
    source_excerpt: str | None = None


class ClaimSourceRead(ClaimSourceCreate):
    id: UUID


class DocumentChunkCreate(Schema):
    source_document_id: UUID
    chunk_index: int
    source_locator: str
    chunk_text: str
    embedding_ref: str | None = None


class DocumentChunkUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("source_document_id", "chunk_index", "source_locator", "chunk_text")
    )
    source_document_id: UUID | None = None
    chunk_index: int | None = None
    source_locator: str | None = None
    chunk_text: str | None = None
    embedding_ref: str | None = None


class DocumentChunkRead(DocumentChunkCreate):
    id: UUID
