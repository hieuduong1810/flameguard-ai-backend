import asyncio
import json
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.schemas.api.comparison import CompareRequest
from app.services.comparison import ComparisonService

pytestmark = pytest.mark.integration
CONTRACT_PATH = (
    Path(__file__).resolve().parents[2] / "specs/001-phase4-catalog-apis/contracts/openapi.json"
)


async def test_documented_comparison_example_runs_against_seed(phase4_client):
    contract = json.loads(await asyncio.to_thread(CONTRACT_PATH.read_text, encoding="utf-8"))
    body = contract["paths"]["/compare"]["post"]["requestBody"]["content"]["application/json"][
        "example"
    ]
    response = await phase4_client.post("/api/v1/compare", json=body)
    assert response.status_code == 200, response.text
    assert [r["investigation"]["id"] for r in response.json()["studies"]] == body[
        "investigationIds"
    ]
    caveats = " ".join(response.json()["context"]["caveats"])
    assert "UNIT_LABEL_MISMATCH" in caveats
    assert "CONDITIONS_NOT_EXAMINED" in caveats
    assert response.json()["deltas"] is None


async def test_comparison_partial_pages_are_not_collection_absence(phase4_client, phase4_db):
    ids = [str(r["id"]) for r in phase4_db["manifest"]["tables"]["investigation"][:2]]
    response = await phase4_client.post(
        "/api/v1/compare",
        json={"investigationIds": ids, "observationOffset": 1, "observationLimit": 1},
    )
    assert response.status_code == 200, response.text
    caveats = " ".join(response.json()["context"]["caveats"])
    assert "PARTIAL_OBSERVATION_PAGE" in caveats
    assert "no collection-wide absence" in caveats
    assert response.json()["highlights"] is None


async def test_three_studies_order_and_no_unit_pooling(phase4_db):
    ids = [r["id"] for r in phase4_db["manifest"]["tables"]["investigation"][:3]][::-1]
    engine = create_async_engine(phase4_db["reader_url"])
    try:
        async with async_sessionmaker(engine)() as s:
            result = await ComparisonService(
                s, {"caveats": ["Synthetic, not NASA evidence"]}, {}
            ).compare(CompareRequest(investigationIds=ids))
            assert [v["investigation"]["id"] for v in result["studies"]] == ids
            assert result["deltas"] is None and result["highlights"] is None
            assert result["comparability"] == "not_established"
    finally:
        await engine.dispose()


@pytest.mark.parametrize("swap_units", [False, True])
async def test_matching_heterogeneous_pages_and_actual_unit_swap(swap_units):
    import os

    from httpx import ASGITransport, AsyncClient
    from sqlalchemy import insert

    from app.core.config import Settings
    from app.main import create_app
    from app.models import Base
    from tests.fixtures.phase4 import comparison_manifest
    from tests.integration.phase4_fixtures import provision_phase4

    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=False)
    manifest = comparison_manifest(swap_units=swap_units)
    engine = create_async_engine(db["owner_url"])
    try:
        async with async_sessionmaker(engine)() as session, session.begin():
            for table in Base.metadata.sorted_tables:
                if manifest["tables"][table.name]:
                    await session.execute(insert(table), manifest["tables"][table.name])
    finally:
        await engine.dispose()
    fixture = db["collection"].parent / "comparison.json"
    fixture.write_text(json.dumps(manifest, default=str), encoding="utf-8")
    config = json.loads(db["collection"].read_text(encoding="utf-8"))
    config["fixture"] = str(fixture)
    db["collection"].write_text(json.dumps(config), encoding="utf-8")
    app = create_app(
        Settings(
            _env_file=None,
            debug=False,
            database_url=db["reader_url"].render_as_string(hide_password=False),
            catalog_collection_manifest=str(db["collection"]),
        )
    )
    ids = [str(row["id"]) for row in manifest["tables"]["investigation"][:2]]
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        response = await client.post("/api/v1/compare", json={"investigationIds": ids})
        assert response.status_code == 200, response.text
        result = response.json()
        caveats = " ".join(result["context"]["caveats"])
        assert ("UNIT_LABEL_MISMATCH" in caveats) == swap_units
        assert "OBSERVABLE_LABEL_MISMATCH" not in caveats
        assert "RUN_CONTEXT_LABEL_MISMATCH" not in caveats
        assert result["comparability"] == "not_established"
        assert result["deltas"] is None and result["highlights"] is None
        expected = {str(row["id"]): row for row in manifest["tables"]["measurement"]}
        for study in result["studies"]:
            assert study["observations"]["total"] == 2
            for item in study["observations"]["items"]:
                measurement = item["measurement"]
                original = expected[measurement["id"]]
                assert measurement["unit"] == original["unit"]
                assert measurement["measuredValue"] == format(original["measured_value"], "f")
                uncertainty = original["uncertainty"]
                assert measurement["uncertainty"] == (
                    None if uncertainty is None else format(uncertainty, "f")
                )
                assert item["run"]["id"] == str(original["test_run_id"])
