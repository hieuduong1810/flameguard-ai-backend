import asyncpg

from app.api.dependencies import get_read_context


async def test_driver_authentication_error_is_unavailable_and_redacted(client, application, caplog):
    async def fail():
        raise asyncpg.InvalidPasswordError("secret-value private-server")

    application.dependency_overrides[get_read_context] = fail
    response = await client.get("/api/v1/investigations")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATA_UNAVAILABLE"
    assert "secret-value" not in response.text + caplog.text


async def test_invalid_utf8_body_is_invalid_request(client):
    response = await client.post(
        "/api/v1/compare", content=b"\xff", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


async def test_no_query_operations_reject_unknown_query(client):
    response = await client.get("/api/v1/catalog/capabilities?fake=value")
    assert response.status_code == 422
