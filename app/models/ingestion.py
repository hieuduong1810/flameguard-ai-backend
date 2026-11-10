"""Approved ERD entities; physical choices are in docs/phase-2-database-implementation.md."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as SQLUUID
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKey


class IngestionJob(UUIDPrimaryKey, Base):
    __tablename__ = "ingestion_job"

    source_uri: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[str] = mapped_column(Text(), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    issues: Mapped[list[ImportIssue]] = relationship(
        "ImportIssue", back_populates="ingestion_job", lazy="raise"
    )


class ImportIssue(UUIDPrimaryKey, Base):
    __tablename__ = "import_issue"

    ingestion_job_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("ingestion_job.id"), index=True, nullable=False
    )
    severity: Mapped[str] = mapped_column(Text(), nullable=False)
    field_name: Mapped[str | None] = mapped_column(Text(), nullable=True)
    explanation: Mapped[str] = mapped_column(Text(), nullable=False)
    review_status: Mapped[str] = mapped_column(Text(), nullable=False)

    ingestion_job: Mapped[IngestionJob] = relationship(
        "IngestionJob", back_populates="issues", lazy="raise"
    )
