from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings

pytest_plugins = ["tests.postgres_fixtures"]


@pytest.fixture(autouse=True)
def isolated_environment(request, monkeypatch, tmp_path) -> None:
    if request.node.get_closest_marker("integration"):
        return
    # Unit tests must not read real credentials or unrelated host values (DEBUG, etc.).
    for field in Settings.model_fields:
        monkeypatch.delenv(field.upper(), raising=False)
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def app_factory():
    from app.main import create_app

    return create_app


@pytest.fixture
def settings() -> Settings:
    # Explicit values isolate tests from local .env files and developer credentials.
    return Settings(
        _env_file=None,
        app_env="test",
        debug=False,
        api_v1_prefix="/api/v1",
        database_url="postgresql+asyncpg://test:test@localhost:5432/test",
        cors_origins=[
            "http://localhost:3000",
            "https://flame-in-freewall-tourbillion.vercel.app",
        ],
        db_ready_timeout_seconds=0.05,
    )


@pytest.fixture
def application(settings: Settings, app_factory) -> FastAPI:
    return app_factory(settings)


@pytest.fixture
async def client(application: FastAPI) -> AsyncIterator[AsyncClient]:
    # HTTPX ASGITransport does not automatically trigger startup/shutdown.
    async with application.router.lifespan_context(application):
        async with AsyncClient(
            transport=ASGITransport(app=application), base_url="http://test"
        ) as c:
            yield c
