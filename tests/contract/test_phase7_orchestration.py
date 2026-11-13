"""Internal synthetic orchestration harness. Public scientific gates stay closed.

Only this test service replaces readiness to reach downstream HTTP outcomes.
Production admission and readiness are exercised separately against PostgreSQL.
"""

import asyncio

import pytest

from app.api.v1.endpoints.predictions import service
from app.integrations.prediction import MockPredictionProvider
from app.schemas.api.predictions import Readiness
from app.services.predictions import PredictionService
from tests.fixtures.phase7 import MODEL_ID, metadata, request_body


class InternalFixtureService(PredictionService):
    async def snapshot(self, model_id):
        return ({}, {}, metadata(), {}, "a" * 64)

    def assessment(self, model_id, snapshot):
        return Readiness(
            state="ready",
            reasons=[],
            model_id=MODEL_ID,
            model_version="TEST_ONLY-v1",
            dataset_version=metadata().dataset_version,
            origin="synthetic",
            limitations=list(metadata().limitations),
        )


@pytest.fixture
def internal_service(application):
    instance = InternalFixtureService(None, application.state.settings, MockPredictionProvider())
    application.dependency_overrides[service] = lambda: instance
    yield instance
    application.dependency_overrides.clear()


async def test_internal_synthetic_success(client, internal_service):
    response = await client.post("/api/v1/predictions", json=request_body())
    assert response.status_code == 200
    assert response.json()["result"]["origin"] == "synthetic"


@pytest.mark.parametrize("field", ["gravity", "oxygen", "pressure", "airflow", "material"])
async def test_unsupported_missing_conditions(client, internal_service, field):
    body = request_body()
    body["scenario"].pop(field)
    response = await client.post("/api/v1/predictions", json=body)
    assert response.status_code == 200
    assert response.json()["state"] == "unsupported"
    assert f"{field}_missing" in response.json()["reasons"]
    assert response.json()["result"] is None


@pytest.mark.parametrize("mode,status", [("timeout", 504), ("invalid", 502), ("failure", 503)])
async def test_http_provider_errors(client, internal_service, mode, status):
    class Provider:
        origin = "synthetic"

        async def predict(self, call):
            if mode == "timeout":
                await asyncio.sleep(1)
            if mode == "invalid":
                return {"private": "provider-secret"}
            raise RuntimeError("provider-secret")

    internal_service.provider = Provider()
    internal_service.settings.prediction_timeout_seconds = 0.001
    response = await client.post("/api/v1/predictions", json=request_body())
    assert response.status_code == status
    assert "provider-secret" not in response.text


async def test_snapshot_drift_discards_result(client, internal_service):
    snapshots = 0

    async def snapshot(model_id):
        nonlocal snapshots
        snapshots += 1
        return ({}, {}, metadata(), {}, ("a" if snapshots == 1 else "b") * 64)

    internal_service.snapshot = snapshot
    response = await client.post("/api/v1/predictions", json=request_body())
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "VERSION_CONFLICT"
