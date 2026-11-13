import pytest

from tests.fixtures.phase7 import request_body


async def test_readiness_without_candidate_and_openapi(client):
    response = await client.get("/api/v1/prediction/readiness")
    assert response.status_code == 200
    assert response.json()["reasons"] == ["model_selection_required"]
    assert response.json()["state"] == "not_ready"
    assert response.headers["cache-control"] == "no-store"
    api = (await client.get("/openapi.json")).json()
    paths = api["paths"]
    assert paths["/api/v1/prediction/readiness"]["get"]["operationId"] == "predictionReadiness"
    responses = paths["/api/v1/predictions"]["post"]["responses"]
    assert {"200", "409", "422", "502", "503", "504"} <= responses.keys()
    assert responses["422"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "PredictionError"
    )


@pytest.mark.parametrize("query", ["model_id=bad", "unknown=true", "model_id=a&model_id=b"])
async def test_invalid_readiness_query(client, query):
    response = await client.get(f"/api/v1/prediction/readiness?{query}")
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "INVALID_REQUEST"}}


@pytest.mark.parametrize("mutation", ["float", "unit", "unknown", "missing"])
async def test_invalid_prediction_body(client, mutation):
    body = request_body()
    if mutation == "float":
        body["scenario"]["gravity"]["value"] = 0.1
    elif mutation == "unit":
        body["scenario"]["gravity"]["unit"] = "m/s2"
    elif mutation == "unknown":
        body["secret"] = "private-example"
    else:
        body.pop("modelId")
    response = await client.post("/api/v1/predictions", json=body)
    assert response.status_code == 422
    assert "private-example" not in response.text


async def test_unconfigured_collection_and_body_limit(client):
    response = await client.post("/api/v1/predictions", json=request_body())
    assert response.status_code == 503
    response = await client.post(
        "/api/v1/predictions", content=" " * 33000, headers={"content-type": "application/json"}
    )
    assert response.status_code == 422


@pytest.mark.parametrize("body", [b'{"modelId":"a","modelId":"b"}', b"\xff", b"{"])
async def test_ambiguous_or_malformed_json(client, body):
    response = await client.post(
        "/api/v1/predictions", content=body, headers={"content-type": "application/json"}
    )
    assert response.status_code == 422
