import json
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, text

from app.integrations.chat import (
    HISTORY_CHARACTERS,
    HISTORY_MESSAGES,
    MESSAGE_CHARACTERS,
    ConversationMessage,
    RagRequest,
    bounded,
    select_provider,
)
from app.models import ClaimSource, EvidenceClaim, Investigation, SourceDocument, TestRun
from app.repositories.chat import ChatRepository
from app.schemas.api.chat import (
    Answer,
    Citation,
    Exchange,
    MessageOutput,
    MessagePage,
    SessionOutput,
)
from app.schemas.api.scenarios import EvidenceContext
from app.services.collection import admit_collection, collection_context
from app.services.scenario_interpretation import fingerprint
from app.services.unit_of_work import read_unit_of_work

ENVELOPE = "flameguard_chat_v1"


def eligible(row):
    if row is None or row.created_at + timedelta(hours=24) <= datetime.now(UTC):
        raise HTTPException(404, "Session unavailable")
    return row


def session_output(row):
    return SessionOutput(
        id=row.id,
        investigation_id=row.investigation_id,
        title=row.title,
        created_at=row.created_at,
        expires_at=row.created_at + timedelta(hours=24),
    )


def validate_citations(answer, allowed, synthetic):
    if answer.origin == "synthetic" and answer.review_status != "unreviewed":
        raise HTTPException(502, "Invalid synthetic review label")
    if answer.origin == "real" or (synthetic and answer.origin != "synthetic" and answer.citations):
        raise HTTPException(502, "Unsupported provider evidence origin")
    if answer.state != "answered" and answer.citations:
        raise HTTPException(502, "Invalid provider citations")
    if any(c not in allowed for c in answer.citations):
        raise HTTPException(502, "Invalid provider citations")
    if answer.state == "answered" and not answer.citations:
        raise HTTPException(502, "Answer requires evidence")


class ChatService:
    def __init__(self, app, provider=None):
        self.app = app
        self.settings = app.state.settings
        self.runtime = app.state.runtime_database
        self.provider = provider if provider is not None else select_provider(app)

    def require_runtime(self):
        if self.runtime is None:
            raise HTTPException(503, "Runtime storage unavailable")

    async def context(self, investigation=None):
        async with self.app.state.database.session_factory() as session, read_unit_of_work(session):
            config, slugs = await admit_collection(session, self.settings, capture_content=True)
            config["phase6CollectionFingerprint"] = fingerprint(
                {
                    "version": 1,
                    "storedContent": config["phase5ContentHash"],
                    "context": EvidenceContext.model_validate(
                        collection_context(config)
                    ).model_dump(mode="json"),
                    "slugs": slugs,
                }
            )
            if config.get("admissionVersion") != 2:
                raise HTTPException(503, "Runtime admission requires v2")
            if investigation and await session.get(Investigation, investigation) is None:
                raise HTTPException(404, "Investigation unavailable")
            stmt = (
                select(ClaimSource, SourceDocument, EvidenceClaim, TestRun)
                .join(SourceDocument, ClaimSource.source_document_id == SourceDocument.id)
                .join(EvidenceClaim, ClaimSource.claim_id == EvidenceClaim.id)
                .outerjoin(TestRun, ClaimSource.test_run_id == TestRun.id)
                .order_by(ClaimSource.id)
            )
            if investigation:
                stmt = stmt.where(SourceDocument.investigation_id == investigation)
            # Only synthetic/unreviewed evidence is currently admitted. Real grounding
            # requires an accepted corpus/review policy before publication.
            citations = []
            if config["origin"] == "synthetic":
                rows = (await session.execute(stmt.limit(50))).all()
                for link, doc, _claim, run in rows:
                    if run is not None and run.investigation_id != doc.investigation_id:
                        continue
                    citations.append(
                        Citation(
                            source_document_id=doc.id,
                            source_locator=link.source_locator,
                            source_excerpt=link.source_excerpt,
                            test_run_id=link.test_run_id,
                        )
                    )
            oid = await session.scalar(
                text("SELECT oid FROM pg_database WHERE datname=current_database()")
            )
            return config, tuple(citations), oid

    async def writer(self, session, oid):
        await self.runtime.validate(session)
        actual = await session.scalar(
            text("SELECT oid FROM pg_database WHERE datname=current_database()")
        )
        if actual != oid:
            raise HTTPException(503, "Runtime database identity mismatch")

    async def create(self, value):
        self.require_runtime()
        _, _, oid = await self.context(value.investigation_id)
        async with self.runtime.session_factory() as session, session.begin():
            await self.writer(session, oid)
            return session_output(await ChatRepository(session).add_session(value))

    async def get(self, identity):
        self.require_runtime()
        _, _, oid = await self.context()
        async with self.runtime.session_factory() as session, session.begin():
            await self.writer(session, oid)
            return session_output(eligible(await ChatRepository(session).session_row(identity)))

    async def project(self, repo, row):
        answer = Answer(state="answered", text=row.body)
        envelope = False
        if row.role == "assistant":
            try:
                value = json.loads(row.body)
            except ValueError:
                value = None
            if isinstance(value, dict) and value.get("format") == ENVELOPE:
                try:
                    answer = Answer.model_validate(value["answer"])
                    envelope = True
                except (ValueError, TypeError, KeyError):
                    raise HTTPException(500, "Stored response unavailable") from None
        saved = await repo.citations(row.id)
        if envelope:
            if sorted(
                (str(c.source_document_id), c.source_locator) for c in answer.citations
            ) != sorted((str(c.source_document_id), c.source_locator) for c in saved):
                raise HTTPException(500, "Stored citations unavailable")
        elif saved:
            answer = answer.model_copy(
                update={
                    "citations": tuple(
                        Citation(
                            source_document_id=c.source_document_id, source_locator=c.source_locator
                        )
                        for c in saved
                    )
                }
            )
        return MessageOutput(id=row.id, role=row.role, created_at=row.created_at, answer=answer)

    async def history(self, identity, offset, limit):
        self.require_runtime()
        _, _, oid = await self.context()
        async with self.runtime.session_factory() as session, session.begin():
            await self.writer(session, oid)
            repo = ChatRepository(session)
            eligible(await repo.session_row(identity))
            return MessagePage(
                items=[
                    await self.project(repo, r) for r in await repo.history(identity, offset, limit)
                ],
                offset=offset,
                limit=limit,
            )

    async def send(self, identity, question):
        info = await self.get(identity)
        config, sources, oid = await self.context(info.investigation_id)
        async with self.runtime.session_factory() as session, session.begin():
            await self.writer(session, oid)
            repo = ChatRepository(session)
            eligible(await repo.session_row(identity))
            rows = await repo.recent(identity, HISTORY_MESSAGES + 1)
            truncated = len(rows) > HISTORY_MESSAGES
            rows = rows[-HISTORY_MESSAGES:]
            history = []
            remaining = HISTORY_CHARACTERS
            for row in reversed(rows):
                message = await self.project(repo, row)
                value = message.answer.text[: min(MESSAGE_CHARACTERS, remaining)]
                truncated = truncated or len(value) < len(message.answer.text)
                if not remaining:
                    break
                history.append(
                    ConversationMessage(
                        role=message.role,
                        text=value,
                        origin=message.answer.origin,
                        review_status=message.answer.review_status,
                    )
                )
                remaining -= len(value)
        provider_request = RagRequest(
            question=question,
            history=tuple(reversed(history)),
            history_truncated=truncated,
            investigation_id=info.investigation_id,
            corpus_version=config["phase5ContentHash"],
            dataset_version=config["phase5DatasetVersion"],
            collection_fingerprint=config["phase6CollectionFingerprint"],
            allowed_sources=sources,
        )
        try:
            answer = await bounded(
                self.provider.answer(provider_request),
                self.settings.chat_timeout_seconds,
            )
        except Exception:
            raise HTTPException(502, "Provider response unavailable") from None
        validate_citations(answer, sources, config["origin"] == "synthetic")
        current, current_sources, _ = await self.context(info.investigation_id)
        if (
            current["phase6CollectionFingerprint"] != config["phase6CollectionFingerprint"]
            or current_sources != sources
        ):
            raise HTTPException(409, "Evidence changed during request")
        async with self.runtime.session_factory() as session, session.begin():
            await self.writer(session, oid)
            repo = ChatRepository(session)
            await repo.lock(identity)
            eligible(await repo.session_row(identity))
            user, assistant = await repo.exchange(
                identity,
                question,
                json.dumps({"format": ENVELOPE, "answer": answer.model_dump(mode="json")}),
            )
            await repo.add_citations(assistant.id, answer.citations)
            return Exchange(
                user=await self.project(repo, user), assistant=await self.project(repo, assistant)
            )
