import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "origin",
    ["http://localhost:3000", "https://flame-in-freewall-tourbillion.vercel.app"],
)
async def test_allowed_origins_and_preflight(client: AsyncClient, origin: str) -> None:
    headers = {"Origin": origin}
    response = await client.get("/api/v1/health", headers=headers)
    assert response.headers["access-control-allow-origin"] == origin
    preflight = await client.options(
        "/api/v1/health",
        headers={**headers, "Access-Control-Request-Method": "GET"},
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == origin
    assert "access-control-allow-credentials" not in preflight.headers


async def test_unknown_origin_cannot_read_api_from_browser(client: AsyncClient) -> None:
    headers = {"Origin": "https://untrusted.example"}
    response = await client.get("/api/v1/health", headers=headers)
    assert "access-control-allow-origin" not in response.headers
    preflight = await client.options(
        "/api/v1/health", headers={**headers, "Access-Control-Request-Method": "GET"}
    )
    assert preflight.status_code == 400
    assert "access-control-allow-origin" not in preflight.headers


async def test_unconfigured_method_is_rejected(client: AsyncClient) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "DELETE"},
    )
    assert response.status_code == 400
