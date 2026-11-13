import asyncio
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.api.chat import Answer, Citation

HISTORY_MESSAGES = 12
HISTORY_CHARACTERS = 12000
MESSAGE_CHARACTERS = 2000


class ConversationMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    role: str
    text: str = Field(max_length=MESSAGE_CHARACTERS)
    origin: str
    review_status: str


class RagRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    question: str = Field(min_length=1, max_length=4000)
    history: tuple[ConversationMessage, ...] = Field(default=(), max_length=HISTORY_MESSAGES)
    history_truncated: bool = False
    investigation_id: UUID | None = None
    corpus_version: str
    dataset_version: str | None = None
    collection_fingerprint: str
    allowed_sources: tuple[Citation, ...] = Field(max_length=50)

    @model_validator(mode="after")
    def history_budget(self):
        if sum(len(m.text) for m in self.history) > HISTORY_CHARACTERS:
            raise ValueError("Conversation context exceeds history budget")
        return self


class RagProvider(Protocol):
    async def answer(self, request: RagRequest) -> Answer: ...


class AdvisorProvider(Protocol):
    async def advise(self, scenario: dict, evidence: dict) -> Answer: ...


class UnavailableProvider:
    async def answer(self, request: RagRequest):
        return Answer(state="unavailable", text="Evidence provider unavailable.")

    async def advise(self, scenario, evidence):
        return Answer(state="unavailable", text="Advisor provider unavailable.")


class MockProvider:
    async def answer(self, request: RagRequest):
        return Answer(
            state="answered" if request.allowed_sources else "abstained",
            text="TEST_ONLY synthetic transport example."
            if request.allowed_sources
            else "TEST_ONLY no eligible evidence.",
            origin="synthetic",
            review_status="unreviewed",
            provider_version="TEST_ONLY-v1",
            corpus_version=request.corpus_version,
            citations=request.allowed_sources[:1],
        )

    async def advise(self, scenario, evidence):
        return Answer(
            state="abstained",
            text="TEST_ONLY advisor requires reviewed evidence.",
            origin="synthetic",
            review_status="unreviewed",
            provider_version="TEST_ONLY-v1",
        )


async def bounded(call, seconds: float) -> Answer:
    try:
        async with asyncio.timeout(seconds):
            result = Answer.model_validate(await call)
            if len(result.text) > 16000:
                raise ValueError("Provider response exceeds output bound")
            return result
    except TimeoutError:
        return Answer(state="timeout", text="Provider deadline exceeded.")


def select_provider(app):
    """A trusted application factory may register an adapter per app instance."""
    factory = getattr(app.state, "chat_provider_factory", None)
    if factory is None:
        factory = {"mock": MockProvider, "unavailable": UnavailableProvider}[
            app.state.settings.chat_provider
        ]
    return factory()
