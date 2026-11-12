import pytest

from app.api.dependencies import get_read_context
from app.services.errors import Phase4Error


@pytest.mark.parametrize(
    "path",
    [
        "/investigations?fake=sensitive",
        "/investigations?limit=0",
        "/investigations?sort=confidence",
        "/investigations/not-uuid",
    ],
)
async def test_validation_precedes_database(client, path):
    response = await client.get("/api/v1" + path)
    assert response.status_code == 422
    assert "sensitive" not in response.text


@pytest.mark.parametrize(
    "exception,status",
    [
        (Phase4Error("DATA_UNAVAILABLE"), 503),
        (RuntimeError("sensitive-password private-host"), 500),
        (ConnectionRefusedError("sensitive-password private-host"), 503),
    ],
)
async def test_route_error_boundary_sanitizes(client, application, caplog, exception, status):
    async def fail():
        raise exception

    application.dependency_overrides[get_read_context] = fail
    response = await client.get("/api/v1/investigations")
    assert response.status_code == status
    assert "sensitive-password" not in response.text + caplog.text
    assert "private-host" not in response.text + caplog.text


async def test_no_implicit_synthetic_loading(client):
    response = await client.get("/api/v1/investigations")
    assert response.status_code == 503
    assert response.json()["context"]["origin"] == "unknown"
