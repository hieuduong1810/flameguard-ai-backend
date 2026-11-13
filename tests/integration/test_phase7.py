import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.api.v1.endpoints.predictions import service
from app.core.config import Settings
from app.integrations.prediction import MockPredictionProvider
from app.main import create_app
from app.models import Base, ModelTrainingRun, ModelVersion
from app.schemas.api.predictions import Readiness
from app.services.predictions import PredictionService
from tests.fixtures.phase7 import MODEL_ID, TRAINING_ID, metadata, request_body
from tests.integration.phase5_fixtures import provision_phase5

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def prediction_db():
    raw = os.environ.get("PHASE4_ADMIN_URL")
    if not raw:
        pytest.skip("Set PHASE4_ADMIN_URL for isolated Phase 7 PostgreSQL tests")

    async def provision():
        db = await provision_phase5(raw)
        model = {
            "id": MODEL_ID,
            "model_name": "TEST_ONLY_transport",
            "version": "TEST_ONLY-v1",
            "validation_status": "TEST_ONLY",
            "applicability_domain": metadata().model_dump_json(),
        }
        training = {
            "id": TRAINING_ID,
            "model_version_id": MODEL_ID,
            "training_dataset_ref": metadata().dataset_version,
            "metrics_ref": metadata().evaluation_ref,
            "trained_at": datetime(2026, 1, 1, tzinfo=UTC),
        }
        engine = create_async_engine(db["owner_url"], hide_parameters=True)
        try:
            async with engine.begin() as connection:
                await connection.execute(insert(ModelVersion), model)
                await connection.execute(insert(ModelTrainingRun), training)
        finally:
            await engine.dispose()
        config = json.loads(db["collection"].read_text("utf-8"))
        fixture = db["collection"].parent / "phase7-fixture.json"
        original = json.loads(await asyncio.to_thread(Path(config["fixture"]).read_text, "utf-8"))
        original["tables"]["model_version"].append(model)
        original["tables"]["model_training_run"].append(training)
        fixture.write_text(
            json.dumps(
                original,
                default=lambda value: (
                    value.isoformat() if isinstance(value, datetime) else str(value)
                ),
            ),
            encoding="utf-8",
        )
        config["fixture"] = str(fixture)
        db["collection"].write_text(json.dumps(config), encoding="utf-8")
        return db

    return asyncio.run(provision())


@pytest.fixture
async def prediction_api(prediction_db, request, tmp_path):
    path = prediction_db["collection"]
    mode = getattr(request, "param", None)
    if mode:
        config = json.loads(path.read_text("utf-8"))
        if mode == "v2":
            config["admissionVersion"] = 2
            config["runtimeTables"] = ["chat_message", "chat_session", "message_citation"]
        elif mode == "reviewed":
            config["reviewState"] = "reviewed"
        elif mode == "manifest_mismatch":
            manifest = json.loads(
                await asyncio.to_thread(Path(config["fixture"]).read_text, "utf-8")
            )
            manifest["tables"]["model_training_run"] = []
            manifest["tables"]["model_version"] = []
            fixture = tmp_path / "mismatch.json"
            fixture.write_text(json.dumps(manifest), encoding="utf-8")
            config["fixture"] = str(fixture)
        path = tmp_path / "collection.json"
        path.write_text(json.dumps(config), encoding="utf-8")
    settings = Settings(
        _env_file=None,
        app_env="test",
        debug=False,
        database_url=prediction_db["reader_url"].render_as_string(hide_password=False),
        catalog_collection_manifest=str(path),
    )
    app = create_app(settings)
    app.state.prediction_provider_factory = MockPredictionProvider
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client


async def database_snapshot(db):
    engine = create_async_engine(db["reader_url"], hide_parameters=True)
    try:
        async with engine.connect() as connection:
            snapshot = {}
            for table in Base.metadata.sorted_tables:
                rows = (
                    (await connection.execute(select(table).order_by(table.c.id))).mappings().all()
                )
                snapshot[table.name] = [dict(row) for row in rows]
            return snapshot
    finally:
        await engine.dispose()


async def test_public_readiness_and_stateless_calls(prediction_api, prediction_db):
    before = await database_snapshot(prediction_db)
    response = await prediction_api.get(
        "/api/v1/prediction/readiness", params={"model_id": str(MODEL_ID)}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "not_ready"
    assert body["datasetVersion"] == "TEST_ONLY_fixture-v1"
    assert body["capabilities"] == metadata().observables
    assert "model_unvalidated" in body["reasons"]
    assert "scientific_collection_unreviewed" in body["reasons"]
    response = await prediction_api.post("/api/v1/predictions", json=request_body())
    assert response.status_code == 200
    assert response.json()["state"] == "not_ready"
    assert response.json()["result"] is None
    assert await database_snapshot(prediction_db) == before


@pytest.mark.parametrize("field", ["expectedModelVersion", "expectedDatasetVersion"])
async def test_version_conflict_no_writes(prediction_api, prediction_db, field):
    before = await database_snapshot(prediction_db)
    body = request_body()
    body[field] = "TEST_ONLY-other"
    response = await prediction_api.post("/api/v1/predictions", json=body)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "VERSION_CONFLICT"
    assert await database_snapshot(prediction_db) == before


async def test_unknown_model(prediction_api):
    response = await prediction_api.get(
        "/api/v1/prediction/readiness", params={"model_id": str(uuid4())}
    )
    assert response.status_code == 200
    assert "model_unavailable" in response.json()["reasons"]


async def test_reader_has_no_write_grants(prediction_db):
    engine = create_async_engine(prediction_db["reader_url"], hide_parameters=True)
    try:
        async with engine.connect() as connection:
            assert not (
                await connection.execute(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM pg_tables WHERE schemaname='public' "
                        "AND has_table_privilege(current_user, "
                        "quote_ident(schemaname)||'.'||quote_ident(tablename), "
                        "'INSERT,UPDATE,DELETE,TRUNCATE'))"
                    )
                )
            ).scalar_one()
    finally:
        await engine.dispose()


async def test_existing_read_apis_still_admit_collection(prediction_api):
    for path in ("/api/v1/investigations", "/api/v1/dashboard/summary"):
        response = await prediction_api.get(path)
        assert response.status_code == 200


@pytest.mark.parametrize("prediction_api", ["v2"], indirect=True)
async def test_admission_v2_backward_compatibility(prediction_api):
    response = await prediction_api.get(
        "/api/v1/prediction/readiness", params={"model_id": str(MODEL_ID)}
    )
    assert response.status_code == 200
    assert response.json()["state"] == "not_ready"


@pytest.mark.parametrize("prediction_api", ["reviewed", "manifest_mismatch"], indirect=True)
async def test_scientific_admission_remains_exact(prediction_api, prediction_db):
    before = await database_snapshot(prediction_db)
    response = await prediction_api.post("/api/v1/predictions", json=request_body())
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "COLLECTION_SCOPE_INVALID"
    assert await database_snapshot(prediction_db) == before


@pytest.mark.parametrize(
    "mode,status", [("success", 200), ("invalid", 502), ("failure", 503), ("timeout", 504)]
)
async def test_internal_provider_paths_write_no_tables(prediction_db, mode, status):
    # Only this internal test overrides readiness to reach provider outcomes.
    # Real read-only transactions and exact collection admission still execute.
    class InternalService(PredictionService):
        def assessment(self, model_id, snapshot):
            return Readiness(
                state="ready",
                reasons=[],
                model_id=MODEL_ID,
                model_version="TEST_ONLY-v1",
                dataset_version=metadata().dataset_version,
                origin="synthetic",
            )

    class FixtureProvider(MockPredictionProvider):
        async def predict(self, call):
            if mode == "timeout":
                await asyncio.sleep(1)
            if mode == "invalid":
                return {}
            if mode == "failure":
                raise RuntimeError("TEST_ONLY unavailable fixture")
            return await super().predict(call)

    settings = Settings(
        _env_file=None,
        debug=False,
        app_env="test",
        prediction_timeout_seconds=0.01,
        database_url=prediction_db["reader_url"].render_as_string(hide_password=False),
        catalog_collection_manifest=str(prediction_db["collection"]),
    )
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        instance = InternalService(app.state.database.session_factory, settings, FixtureProvider())
        app.dependency_overrides[service] = lambda: instance
        before = await database_snapshot(prediction_db)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/predictions", json=request_body())
        assert response.status_code == status
        if mode == "success":
            assert response.json()["result"]["origin"] == "synthetic"
        assert await database_snapshot(prediction_db) == before
