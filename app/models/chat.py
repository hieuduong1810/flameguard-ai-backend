"""Approved ERD entities; physical choices are recorded in docs/database-implementation.md."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as SQLUUID
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKey, utc_now

if TYPE_CHECKING:
    from app.models.catalog import Investigation
    from app.models.evidence import SourceDocument


class ChatSession(UUIDPrimaryKey, Base):
    __tablename__ = "chat_session"

    investigation_id: Mapped[UUID | None] = mapped_column(
        SQLUUID(), ForeignKey("investigation.id"), index=True, nullable=True
    )
    title: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    investigation: Mapped[Investigation | None] = relationship(
        "Investigation", back_populates="chat_sessions", lazy="raise"
    )
    messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage", back_populates="session", lazy="raise"
    )


class ChatMessage(UUIDPrimaryKey, Base):
    __tablename__ = "chat_message"

    chat_session_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("chat_session.id"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(Text(), nullable=False)
    body: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    session: Mapped[ChatSession] = relationship(
        "ChatSession", back_populates="messages", lazy="raise"
    )
    citations: Mapped[list[MessageCitation]] = relationship(
        "MessageCitation", back_populates="message", lazy="raise"
    )


class MessageCitation(UUIDPrimaryKey, Base):
    __tablename__ = "message_citation"

    chat_message_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("chat_message.id"), index=True, nullable=False
    )
    source_document_id: Mapped[UUID] = mapped_column(
        SQLUUID(), ForeignKey("source_document.id"), index=True, nullable=False
    )
    source_locator: Mapped[str] = mapped_column(Text(), nullable=False)

    message: Mapped[ChatMessage] = relationship(
        "ChatMessage", back_populates="citations", lazy="raise"
    )
    source_document: Mapped[SourceDocument] = relationship(
        "SourceDocument", back_populates="message_citations", lazy="raise"
    )
