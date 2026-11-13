from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select, text

from app.models import ChatMessage, ChatSession, MessageCitation


class ChatRepository:
    def __init__(self, session):
        self.session = session

    async def session_row(self, identity):
        return await self.session.get(ChatSession, identity)

    async def add_session(self, value):
        row = ChatSession(id=uuid4(), **value.model_dump(), created_at=datetime.now(UTC))
        self.session.add(row)
        await self.session.flush()
        return row

    async def lock(self, identity):
        key = int.from_bytes(identity.bytes[:8], "big", signed=True)
        await self.session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})

    async def history(self, identity, offset, limit):
        return (
            await self.session.scalars(
                select(ChatMessage)
                .where(ChatMessage.chat_session_id == identity)
                .order_by(ChatMessage.created_at, ChatMessage.id)
                .offset(offset)
                .limit(limit)
            )
        ).all()

    async def citations(self, message):
        return (
            await self.session.scalars(
                select(MessageCitation)
                .where(MessageCitation.chat_message_id == message)
                .order_by(MessageCitation.id)
            )
        ).all()

    async def recent(self, identity, limit):
        rows = (
            await self.session.scalars(
                select(ChatMessage)
                .where(ChatMessage.chat_session_id == identity)
                .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
                .limit(limit)
            )
        ).all()
        return list(reversed(rows))

    async def exchange(self, identity, question, answer):
        last = await self.session.scalar(
            select(ChatMessage.created_at)
            .where(ChatMessage.chat_session_id == identity)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        now = datetime.now(UTC)
        if last is not None:
            now = max(now, last + timedelta(microseconds=1))
        user = ChatMessage(
            id=uuid4(), chat_session_id=identity, role="user", body=question, created_at=now
        )
        assistant = ChatMessage(
            id=uuid4(),
            chat_session_id=identity,
            role="assistant",
            body=answer,
            created_at=now + timedelta(microseconds=1),
        )
        self.session.add_all([user, assistant])
        await self.session.flush()
        return user, assistant

    async def add_citations(self, message, citations):
        self.session.add_all(
            [
                MessageCitation(
                    id=uuid4(),
                    chat_message_id=message,
                    source_document_id=item.source_document_id,
                    source_locator=item.source_locator,
                )
                for item in citations
            ]
        )
        await self.session.flush()
