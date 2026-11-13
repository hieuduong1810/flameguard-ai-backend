from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def reject_nul(cls, value):
        if isinstance(value, str) and "\x00" in value:
            raise ValueError("NUL characters are unsupported")
        return value


class SessionInput(ChatInput):
    investigation_id: UUID | None = None
    title: str | None = Field(default=None, max_length=200)


class Question(ChatInput):
    question: str = Field(min_length=1, max_length=4000, pattern=r"\S")


class SessionOutput(BaseModel):
    id: UUID
    investigation_id: UUID | None
    title: str | None
    created_at: datetime
    expires_at: datetime
    privacy: str = (
        "Public research demo. Session ID holders can access history for 24 hours. "
        "Rows are retained pending operator cleanup."
    )


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_document_id: UUID
    source_locator: str = Field(min_length=1, max_length=2000)
    source_excerpt: str | None = None
    test_run_id: UUID | None = None


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    state: Literal["answered", "abstained", "unavailable", "timeout"]
    text: str
    origin: Literal["synthetic", "unknown", "real"] = "unknown"
    review_status: Literal["unreviewed", "unknown"] = "unknown"
    provider_version: str | None = None
    model_version: str | None = None
    corpus_version: str | None = None
    citations: tuple[Citation, ...] = Field(default=(), max_length=50)


class MessageOutput(BaseModel):
    id: UUID
    role: str
    created_at: datetime
    answer: Answer


class MessagePage(BaseModel):
    items: list[MessageOutput]
    offset: int
    limit: int


class Exchange(BaseModel):
    user: MessageOutput
    assistant: MessageOutput


class AdvisorOutput(BaseModel):
    pillars: dict[str, Answer]
    gaps: dict[str, tuple[str, ...]]
    context: dict
