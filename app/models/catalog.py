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
    from app.models.chat import ChatSession
    from app.models.evidence import ClaimSource, SourceDocument
    from app.models.scenarios import ScenarioMatch


class Investigation(UUIDPrimaryKey, Base):
    __tablename__ = "investigation"

    psi_id: Mapped[str] = mapped_column(Text(), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text(), nullable=False)
    research_purpose: Mapped[str | None] = mapped_column(Text(), nullable=True)
    platform: Mapped[str | None] = mapped_column(Text(), nullable=True)

    test_runs: Mapped[list[TestRun]] = relationship(
        "TestRun", back_populates="investigation", lazy="raise"
    )
    source_documents: Mapped[list[SourceDocument]] = relationship(
        "SourceDocument", back_populates="investigation", lazy="raise"
    )
    tag_links: Mapped[list[InvestigationTag]] = relationship(
        "InvestigationTag", back_populates="investigation", lazy="raise"
    )
    chat_sessions: Mapped[list[ChatSession]] = relationship(
        "ChatSession", back_populates="investigation", lazy="raise"
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag", secondary="investigation_tag", viewonly=True, lazy="raise"
    )


class TestRun(UUIDPrimaryKey, Base):
    __tablename__ = "test_run"

    investigation_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("investigation.id"), index=True, nullable=False
    )
    external_run_key: Mapped[str | None] = mapped_column(Text(), nullable=True)
    material_type: Mapped[str | None] = mapped_column(Text(), nullable=True)
    sample_geometry: Mapped[str | None] = mapped_column(Text(), nullable=True)
    gravity: Mapped[str | None] = mapped_column(Text(), nullable=True)

    investigation: Mapped[Investigation] = relationship(
        "Investigation", back_populates="test_runs", lazy="raise"
    )
    conditions: Mapped[list[TestCondition]] = relationship(
        "TestCondition", back_populates="test_run", lazy="raise"
    )
    measurements: Mapped[list[Measurement]] = relationship(
        "Measurement", back_populates="test_run", lazy="raise"
    )
    claim_sources: Mapped[list[ClaimSource]] = relationship(
        "ClaimSource", back_populates="test_run", lazy="raise"
    )
    scenario_matches: Mapped[list[ScenarioMatch]] = relationship(
        "ScenarioMatch", back_populates="test_run", lazy="raise"
    )


class TestCondition(UUIDPrimaryKey, Base):
    __tablename__ = "test_condition"

    test_run_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("test_run.id"), index=True, nullable=False
    )
    variable: Mapped[str] = mapped_column(Text(), nullable=False)
    value_numeric: Mapped[Decimal | None] = mapped_column(Numeric(), nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    unit: Mapped[str | None] = mapped_column(Text(), nullable=True)
    data_status: Mapped[str] = mapped_column(Text(), nullable=False)

    test_run: Mapped[TestRun] = relationship("TestRun", back_populates="conditions", lazy="raise")


class Measurement(UUIDPrimaryKey, Base):
    __tablename__ = "measurement"

    test_run_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("test_run.id"), index=True, nullable=False
    )
    observable: Mapped[str] = mapped_column(Text(), nullable=False)
    measured_value: Mapped[Decimal | None] = mapped_column(Numeric(), nullable=True)
    unit: Mapped[str] = mapped_column(Text(), nullable=False)
    raw_asset_ref: Mapped[str | None] = mapped_column(Text(), nullable=True)
    uncertainty: Mapped[Decimal | None] = mapped_column(Numeric(), nullable=True)

    test_run: Mapped[TestRun] = relationship("TestRun", back_populates="measurements", lazy="raise")


class Tag(UUIDPrimaryKey, Base):
    __tablename__ = "tag"

    slug: Mapped[str] = mapped_column(Text(), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(Text(), nullable=False)
    category: Mapped[str | None] = mapped_column(Text(), nullable=True)

    investigation_links: Mapped[list[InvestigationTag]] = relationship(
        "InvestigationTag", back_populates="tag", lazy="raise"
    )
    investigations: Mapped[list[Investigation]] = relationship(
        "Investigation", secondary="investigation_tag", viewonly=True, lazy="raise"
    )


class InvestigationTag(UUIDPrimaryKey, Base):
    __tablename__ = "investigation_tag"

    investigation_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("investigation.id"), index=True, nullable=False
    )
    tag_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("tag.id"), index=True, nullable=False
    )

    investigation: Mapped[Investigation] = relationship(
        "Investigation", back_populates="tag_links", lazy="raise"
    )
    tag: Mapped[Tag] = relationship("Tag", back_populates="investigation_links", lazy="raise")
