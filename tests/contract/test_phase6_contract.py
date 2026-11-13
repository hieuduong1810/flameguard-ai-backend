async def test_runtime_unconfigured_returns_unavailable(client):
    result = await client.post("/api/v1/chat/sessions", json={})
    assert result.status_code == 503
    assert result.headers["cache-control"] == "no-store"
    assert result.json()["detail"] == "Runtime storage unavailable"


async def test_input_bounds_and_openapi(client):
    result = await client.post("/api/v1/chat/sessions", json={"extra": True})
    assert result.status_code == 422
    result = await client.get("/api/v1/chat/sessions/not-a-uuid")
    assert result.status_code == 422
    api = (await client.get("/openapi.json")).json()
    assert api["paths"]["/api/v1/chat/sessions"]["post"]["responses"]["201"]
    assert api["paths"]["/api/v1/advisor/assessments"]["post"]["responses"]["200"]
