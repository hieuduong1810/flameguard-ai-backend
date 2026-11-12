from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings


async def test_documentation_preserves_phase_one_routes(client: AsyncClient) -> None:
    assert (await client.get("/docs")).status_code == 200
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert {"/api/v1/health", "/api/v1/ready"} <= set(response.json()["paths"])
    assert "503" in response.json()["paths"]["/api/v1/ready"]["get"]["responses"]


async def test_environment_prefix_and_title(settings: Settings, app_factory) -> None:
    application = app_factory(
        settings.model_copy(update={"app_name": "Test", "api_v1_prefix": "/v2"})
    )
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        assert (await client.get("/v2/health")).status_code == 200
        assert (await client.get("/api/v1/health")).status_code == 404
        assert (await client.get("/openapi.json")).json()["info"]["title"] == "Test"


async def test_lifespan_disposes_engine_even_after_failure(settings: Settings, app_factory) -> None:
    database = AsyncMock()
    with patch("app.main.Database", return_value=database):
        application = app_factory(settings)
        try:
            async with application.router.lifespan_context(application):
                assert application.state.database is database
                raise RuntimeError("simulate lifespan failure")
        except RuntimeError:
            pass
    database.close.assert_awaited_once()


async def test_unhandled_error_is_sanitized(application: FastAPI, caplog) -> None:
    @application.get("/test-error", include_in_schema=False)
    async def fail() -> None:
        raise RuntimeError("secret-password private-host")

    transport = ASGITransport(app=application, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/test-error")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "secret-password" not in response.text + caplog.text


async def test_missing_route_keeps_standard_404(client: AsyncClient) -> None:
    assert (await client.get("/missing")).status_code == 404
