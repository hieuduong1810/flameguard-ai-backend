import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import text

from app.core.config import Settings
from app.core.database import Database, get_db_session


async def test_session_dependency_exits_context_on_failure() -> None:
    session = AsyncMock()
    session_context = AsyncMock()
    session_context.__aenter__.return_value = session
    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(database=SimpleNamespace(session_factory=lambda: session_context))
        )
    )
    dependency = get_db_session(request)
    assert await anext(dependency) is session
    with pytest.raises(RuntimeError, match="service failure"):
        await dependency.athrow(RuntimeError("service failure"))
    session_context.__aexit__.assert_awaited_once()
    assert session_context.__aexit__.call_args.args[0] is RuntimeError
    session.commit.assert_not_awaited()


@pytest.mark.integration
async def test_postgres_connectivity_and_session_cleanup() -> None:
    if os.getenv("RUN_DB_INTEGRATION") != "1":
        pytest.skip("Set RUN_DB_INTEGRATION=1 with PostgreSQL running to opt in")
    database = Database(Settings())
    try:
        async with database.session_factory() as session:
            assert (await session.execute(text("SELECT 1"))).scalar_one() == 1
        # New session proves the previous context returned its connection to the pool.
        async with database.session_factory() as session:
            assert (await session.execute(text("SELECT 1"))).scalar_one() == 1
    finally:
        await database.close()
