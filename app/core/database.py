from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


class Database:
    """One engine per application lifespan; sessions are scoped to individual requests."""

    def __init__(self, settings: Settings) -> None:
        self.engine = create_async_engine(
            settings.database_url.get_secret_value(),
            echo=False,
            hide_parameters=True,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=2,
            pool_timeout=settings.db_ready_timeout_seconds,
            connect_args={"timeout": settings.db_connect_timeout_seconds},
        )
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def close(self) -> None:
        await self.engine.dispose()


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Close sessions and roll back uncommitted work; services own explicit commits."""
    database: Database = request.app.state.database
    async with database.session_factory() as session:
        yield session
