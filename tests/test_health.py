import asyncio
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db_session


async def test_health_does_not_request_a_database_session(
    application: FastAPI, client: AsyncClient
) -> None:
    def forbidden_session() -> None:
        pytest.fail("Liveness must never acquire a database session")

    application.dependency_overrides[get_db_session] = forbidden_session
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "flameguard-ai-backend"}


async def test_ready_checks_select_one(application: FastAPI, client: AsyncClient) -> None:
    session = AsyncMock()
    application.dependency_overrides[get_db_session] = lambda: session
    response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "flameguard-ai-backend",
        "database": "ok",
    }
    session.execute.assert_awaited_once()
    assert str(session.execute.call_args.args[0]) == "SELECT 1"


@pytest.mark.parametrize("error_type", [SQLAlchemyError, ConnectionRefusedError, TimeoutError])
async def test_ready_unavailable_is_sanitized(
    application: FastAPI, client: AsyncClient, error_type: type[Exception], caplog
) -> None:
    session = AsyncMock()
    session.execute.side_effect = error_type("postgresql://user:secret-password@private-host/db")
    application.dependency_overrides[get_db_session] = lambda: session
    response = await client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "service": "flameguard-ai-backend",
        "database": "unavailable",
    }
    assert "secret-password" not in response.text + caplog.text
    assert "private-host" not in response.text + caplog.text
    assert (await client.get("/api/v1/health")).status_code == 200


async def test_ready_times_out_a_stalled_query(application: FastAPI, client: AsyncClient) -> None:
    cancelled = asyncio.Event()

    async def stalled_query(_query) -> None:
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    session = AsyncMock()
    session.execute.side_effect = stalled_query
    application.dependency_overrides[get_db_session] = lambda: session
    response = await asyncio.wait_for(client.get("/api/v1/ready"), timeout=1)
    assert response.status_code == 503
    assert cancelled.is_set()
