import asyncio
import json
import os
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings
from app.main import create_app
from app.models import TestCondition, TestRun
from app.services.demo_manifest import DEMO_ROOT
from tests.fixtures.phase5 import CONDITIONS
from tests.integration.phase4_fixtures import provision_phase4
from tests.postgres_fixtures import validate_test_url

COMPLETE_RUN = UUID("b8f882f6-6fde-5b18-a505-f668bdc12c42")
OXYGEN_RUN = UUID("f5b4d793-3cd5-5571-ac49-8246a1daea3e")
PRESSURE_RUN = UUID("f04922ad-2fbf-5afe-ba7e-bc5a01b9149f")


async def provision_phase5(raw):
    validate_test_url(raw, Settings().database_url.get_secret_value())
    db = await provision_phase4(raw)
    originals = json.loads((DEMO_ROOT / "phase4-v1.json").read_text(encoding="utf-8"))
    rows = []
    for run, conditions in (
        (COMPLETE_RUN, CONDITIONS),
        (OXYGEN_RUN, CONDITIONS[:3]),
        (PRESSURE_RUN, CONDITIONS[3:]),
    ):
        for variable, value, text, unit in conditions:
            rows.append(
                {
                    "id": UUID(int=len(rows) + 1),
                    "test_run_id": run,
                    "variable": variable,
                    "value_numeric": value,
                    "value_text": text,
                    "unit": unit,
                    "data_status": "TEST_ONLY",
                }
            )
    engine = create_async_engine(db["owner_url"], hide_parameters=True)
    try:
        async with engine.begin() as conn:
            await conn.execute(insert(TestCondition), rows)
            await conn.execute(
                update(TestRun)
                .where(TestRun.id == COMPLETE_RUN)
                .values(sample_geometry="TEST_ONLY inverse flame")
            )
    finally:
        await engine.dispose()
    originals["tables"]["test_condition"].extend(rows)
    for run in originals["tables"]["test_run"]:
        if run["id"] == str(COMPLETE_RUN):
            run["sample_geometry"] = "TEST_ONLY inverse flame"
    fixture = db["collection"].with_name("phase5-fixture.json")
    fixture.write_text(json.dumps(originals, default=str), encoding="utf-8")
    config = json.loads(db["collection"].read_text(encoding="utf-8"))
    config["fixture"] = str(fixture)
    db["collection"].write_text(json.dumps(config), encoding="utf-8")
    return db


@pytest.fixture(scope="session")
def phase5_db():
    raw = os.environ.get("PHASE4_ADMIN_URL")
    if not raw:
        pytest.skip("Set PHASE4_ADMIN_URL for isolated Phase 5 PostgreSQL verification")
    return asyncio.run(provision_phase5(raw))


@pytest.fixture
async def phase5_api(phase5_db):
    settings = Settings(
        _env_file=None,
        debug=False,
        app_env="test",
        scenario_test_providers=True,
        database_url=phase5_db["reader_url"].render_as_string(hide_password=False),
        catalog_collection_manifest=str(phase5_db["collection"]),
    )
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, app
