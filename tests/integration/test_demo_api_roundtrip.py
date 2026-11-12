import json
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.main import create_app
from app.models import Base
from tests.fixtures.phase4 import pagination_manifest
from tests.integration.phase4_fixtures import provision_phase4

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("empty", [False, True])
async def test_independent_large_and_empty_collection(empty):
    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=False)
    manifest = pagination_manifest()
    if empty:
        manifest["collectionId"] = "synthetic-phase4-empty-v1"
        manifest["tables"] = {k: [] for k in manifest["tables"]}
    engine = create_async_engine(db["owner_url"])
    try:
        async with async_sessionmaker(engine)() as s, s.begin():
            for table in Base.metadata.sorted_tables:
                if manifest["tables"][table.name]:
                    rows = manifest["tables"][table.name]
                    # Deliberately reverse UUID insertion order to test ordering.
                    if table.name in {"tag", "investigation_tag"}:
                        rows = sorted(rows, key=lambda r: r["id"], reverse=True)
                    await s.execute(insert(table), rows)
    finally:
        await engine.dispose()
    directory = db["collection"].parent
    fixture_path = directory / "variant.json"
    fixture_path.write_text(json.dumps(manifest, default=str))
    slugs_path = directory / "slugs.json"
    slugs_path.write_text(json.dumps({"collectionId": manifest["collectionId"], "entries": []}))
    config = json.loads(db["collection"].read_text())
    config.update(
        collectionId=manifest["collectionId"], fixture=str(fixture_path), slugs=str(slugs_path)
    )
    db["collection"].write_text(json.dumps(config))
    app = create_app(
        Settings(
            _env_file=None,
            debug=False,
            app_env="test",
            database_url=db["reader_url"].render_as_string(hide_password=False),
            catalog_collection_manifest=str(db["collection"]),
        )
    )
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        page = (await client.get("/api/v1/investigations?limit=100")).json()
        assert page["total"] == (0 if empty else 105)
        if empty:
            assert page["items"] == [] and page["context"]["origin"] == "synthetic"
            summary = (await client.get("/api/v1/dashboard/summary")).json()
            assert summary["investigationCount"] == 0 and summary["sourceCoverage"]["ratio"] is None
            return
        second = (await client.get(page["next"])).json()
        assert len(second["items"]) == 5 and second["next"] is None
        identity = str(manifest["tables"]["investigation"][0]["id"])
        claims = (await client.get(f"/api/v1/investigations/{identity}/claims")).json()
        sources = claims["items"][0]["sources"]
        seen = []
        while True:
            seen.extend(v["id"] for v in sources["items"])
            if not sources["next"]:
                break
            sources = (await client.get(sources["next"])).json()
        assert len(seen) == len(set(seen)) == 105
        detail = (await client.get(f"/api/v1/investigations/{identity}")).json()
        assert detail["tags"]["total"] == 25 and len(detail["tags"]["items"]) == 20
        rest = (await client.get(detail["tags"]["next"])).json()
        direct = (await client.get(f"/api/v1/investigations/{identity}/tags")).json()
        assert direct["items"] == detail["tags"]["items"]
        seen = [tag["id"] for tag in detail["tags"]["items"] + rest["items"]]
        assert len(seen) == len(set(seen)) == 25 and seen == sorted(seen)
        assert rest["next"] is None


@pytest.mark.parametrize("origin", ["unknown", "real", None])
async def test_bound_empty_non_synthetic_http_and_mixing_refusal(origin):
    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=False)
    config = json.loads(db["collection"].read_text(encoding="utf-8"))
    config.pop("fixture")
    config.pop("slugs")
    config["reviewState"] = "unknown"
    if origin is None:
        config.pop("origin")
    else:
        config["origin"] = origin
    db["collection"].write_text(json.dumps(config), encoding="utf-8")
    app = create_app(
        Settings(
            _env_file=None,
            debug=False,
            app_env="test",
            database_url=db["reader_url"].render_as_string(hide_password=False),
            catalog_collection_manifest=str(db["collection"]),
        )
    )
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        for route in ["investigations", "dashboard/summary"]:
            response = await client.get("/api/v1/" + route)
            assert response.status_code == 200, response.text
            value = response.json()
            assert value["context"]["origin"] == (origin or "unknown")
            assert value["context"]["reviewState"] == "unknown"
            assert value.get("total", value.get("investigationCount")) == 0
        # Only this new disposable test DB is mutated; no fallback relabeling.
        engine = create_async_engine(db["owner_url"])
        try:
            async with async_sessionmaker(engine)() as session, session.begin():
                await session.execute(
                    insert(Base.metadata.tables["investigation"]),
                    db["manifest"]["tables"]["investigation"][:1],
                )
        finally:
            await engine.dispose()
        response = await client.get("/api/v1/investigations")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "COLLECTION_SCOPE_INVALID"


async def test_unknown_snapshot_stored_fields_and_curated_gate():
    from uuid import uuid4

    from app.services.demo_manifest import snapshot_rows

    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=False)
    identity, document = str(uuid4()), str(uuid4())
    snapshot = {
        "collectionId": "unknown-local-test",
        "origin": "unknown",
        "tables": {name: [] for name in Base.metadata.tables},
    }
    snapshot["tables"]["investigation"] = [
        {
            "id": identity,
            "psi_id": "LOCAL-UNREVIEWED",
            "title": "Local test record; no scientific finding",
            "platform": None,
            "research_purpose": None,
        }
    ]
    snapshot["tables"]["source_document"] = [
        {
            "id": document,
            "investigation_id": identity,
            "source_url": "https://unreviewed.invalid/document",
            "doi": None,
            "version": None,
            "document_type": "NOT_REVIEWED",
            "ingestion_status": "OWNER_STATUS_UNKNOWN",
        }
    ]
    path = db["collection"].parent / "snapshot.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    typed = snapshot_rows(path)
    engine = create_async_engine(db["owner_url"])
    try:
        async with async_sessionmaker(engine)() as session, session.begin():
            for table in Base.metadata.sorted_tables:
                if typed["tables"][table.name]:
                    await session.execute(insert(table), typed["tables"][table.name])
    finally:
        await engine.dispose()
    config = json.loads(db["collection"].read_text(encoding="utf-8"))
    config.pop("fixture")
    config.pop("slugs")
    config.update(
        collectionId=snapshot["collectionId"],
        origin="unknown",
        reviewState="unreviewed",
        snapshot=str(path),
    )
    db["collection"].write_text(json.dumps(config), encoding="utf-8")
    app = create_app(
        Settings(
            _env_file=None,
            debug=False,
            database_url=db["reader_url"].render_as_string(hide_password=False),
            catalog_collection_manifest=str(db["collection"]),
        )
    )
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        detail = await client.get(f"/api/v1/investigations/{identity}")
        assert detail.status_code == 200, detail.text
        assert detail.json()["slug"] is None and detail.json()["psiId"] == "LOCAL-UNREVIEWED"
        response = await client.get(f"/api/v1/investigations/{identity}/sources")
        assert response.status_code == 200, response.text
        source = response.json()["items"][0]
        assert source["ingestionStatus"] == "OWNER_STATUS_UNKNOWN"
        assert source["doi"] is None and source["context"]["origin"] == "unknown"
        assert source["context"]["reviewState"] == "unreviewed"
        duplicate = {**snapshot["tables"]["source_document"][0], "id": document.upper()}
        snapshot["tables"]["source_document"].append(duplicate)
        path.write_text(json.dumps(snapshot), encoding="utf-8")
        response = await client.get(f"/api/v1/investigations/{identity}/sources")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "COLLECTION_SCOPE_INVALID"
        snapshot["tables"]["source_document"].pop()
        path.write_text(json.dumps(snapshot), encoding="utf-8")
        config["reviewState"] = "curated"
        db["collection"].write_text(json.dumps(config), encoding="utf-8")
        assert (await client.get("/api/v1/investigations")).status_code == 503


async def test_synthetic_duplicate_manifest_is_not_admitted(phase4_db, tmp_path):
    import copy

    manifest = copy.deepcopy(phase4_db["manifest"])
    row = manifest["tables"]["claim_source"][0]
    manifest["tables"]["claim_source"].append({**row, "id": str(row["id"]).upper()})
    fixture = tmp_path / "duplicate.json"
    fixture.write_text(json.dumps(manifest, default=str), encoding="utf-8")
    config = json.loads(phase4_db["collection"].read_text(encoding="utf-8"))
    config["fixture"] = str(fixture)
    path = tmp_path / "collection.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    app = create_app(
        Settings(
            _env_file=None,
            debug=False,
            database_url=phase4_db["reader_url"].render_as_string(hide_password=False),
            catalog_collection_manifest=str(path),
        )
    )
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        response = await client.get("/api/v1/investigations")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "COLLECTION_SCOPE_INVALID"
