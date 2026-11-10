"""Scalar persistence contracts, not frontend projection or scientific validation schemas."""

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from app.schemas.base import PatchSchema, Schema


class ChatSessionCreate(Schema):
    investigation_id: UUID | None = None
    title: str | None = None


class ChatSessionUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(())
    investigation_id: UUID | None = None
    title: str | None = None


class ChatSessionRead(ChatSessionCreate):
    id: UUID
    created_at: datetime


class ChatMessageCreate(Schema):
    chat_session_id: UUID
    role: str
    body: str


class ChatMessageUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(("chat_session_id", "role", "body"))
    chat_session_id: UUID | None = None
    role: str | None = None
    body: str | None = None


class ChatMessageRead(ChatMessageCreate):
    id: UUID
    created_at: datetime


class MessageCitationCreate(Schema):
    chat_message_id: UUID
    source_document_id: UUID
    source_locator: str


class MessageCitationUpdate(PatchSchema):
    non_nullable_fields: ClassVar[frozenset[str]] = frozenset(
        ("chat_message_id", "source_document_id", "source_locator")
    )
    chat_message_id: UUID | None = None
    source_document_id: UUID | None = None
    source_locator: str | None = None


class MessageCitationRead(MessageCitationCreate):
    id: UUID
