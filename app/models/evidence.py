"""Approved ERD entities; physical choices are recorded in docs/database-implementation.md."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as SQLUUID
from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKey, utc_now

if TYPE_CHECKING:
    from app.models.catalog import Investigation, TestRun
    from app.models.chat import MessageCitation


class SourceDocument(UUIDPrimaryKey, Base):
    __tablename__ = "source_document"

    investigation_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("investigation.id"), index=True, nullable=False
    )
    source_url: Mapped[str] = mapped_column(Text(), nullable=False)
    doi: Mapped[str | None] = mapped_column(Text(), nullable=True)
    document_type: Mapped[str] = mapped_column(Text(), nullable=False)
    version: Mapped[str | None] = mapped_column(Text(), nullable=True)
    ingestion_status: Mapped[str] = mapped_column(Text(), nullable=False)

    investigation: Mapped[Investigation] = relationship(
        "Investigation", back_populates="source_documents", lazy="raise"
    )
    claim_links: Mapped[list[ClaimSource]] = relationship(
        "ClaimSource", back_populates="source_document", lazy="raise"
    )
    chunks: Mapped[list[DocumentChunk]] = relationship(
        "DocumentChunk", back_populates="source_document", lazy="raise"
    )
    message_citations: Mapped[list[MessageCitation]] = relationship(
        "MessageCitation", back_populates="source_document", lazy="raise"
    )
    claims: Mapped[list[EvidenceClaim]] = relationship(
        "EvidenceClaim", secondary="claim_source", viewonly=True, lazy="raise"
    )


class EvidenceClaim(UUIDPrimaryKey, Base):
    __tablename__ = "evidence_claim"

    claim_text: Mapped[str] = mapped_column(Text(), nullable=False)
    evidence_status: Mapped[str] = mapped_column(Text(), nullable=False)
    review_status: Mapped[str] = mapped_column(Text(), nullable=False)
    limitation: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    source_links: Mapped[list[ClaimSource]] = relationship(
        "ClaimSource", back_populates="claim", lazy="raise"
    )
    source_documents: Mapped[list[SourceDocument]] = relationship(
        "SourceDocument", secondary="claim_source", viewonly=True, lazy="raise"
    )


class ClaimSource(UUIDPrimaryKey, Base):
    __tablename__ = "claim_source"

    claim_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("evidence_claim.id"), index=True, nullable=False
    )
    source_document_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("source_document.id"), index=True, nullable=False
    )
    test_run_id: Mapped[UUID | None] = mapped_column(
        SQLUUID(), ForeignKey("test_run.id"), index=True, nullable=True
    )
    source_locator: Mapped[str] = mapped_column(Text(), nullable=False)
    source_excerpt: Mapped[str | None] = mapped_column(Text(), nullable=True)

    claim: Mapped[EvidenceClaim] = relationship(
        "EvidenceClaim", back_populates="source_links", lazy="raise"
    )
    source_document: Mapped[SourceDocument] = relationship(
        "SourceDocument", back_populates="claim_links", lazy="raise"
    )
    test_run: Mapped[TestRun | None] = relationship(
        "TestRun", back_populates="claim_sources", lazy="raise"
    )


class DocumentChunk(UUIDPrimaryKey, Base):
    __tablename__ = "document_chunk"

    source_document_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("source_document.id"), index=True, nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer(), nullable=False)
    source_locator: Mapped[str] = mapped_column(Text(), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text(), nullable=False)
    embedding_ref: Mapped[str | None] = mapped_column(Text(), nullable=True)

    source_document: Mapped[SourceDocument] = relationship(
        "SourceDocument", back_populates="chunks", lazy="raise"
    )
