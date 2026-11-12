import json
from unittest.mock import AsyncMock

import pytest

from app.core.config import Settings
from app.services.collection import admit_collection, collection_context
from app.services.demo_manifest import fixture_rows
from app.services.errors import Phase4Error


async def test_missing_configuration_is_not_curated():
    with pytest.raises(Phase4Error):
        await admit_collection(None, Settings(_env_file=None, debug=False))


def test_fixture_is_deterministic_and_never_science():
    first, second = fixture_rows(), fixture_rows()
    assert first == second
    assert len(first["tables"]) == 21
    assert len(first["tables"]["investigation"]) == 4
    assert first["origin"] == "synthetic"
    ctx = collection_context(first)
    assert ctx["origin"] == "synthetic" and ctx["reviewState"] == "unreviewed"
    assert "NASA" in ctx["caveats"][0]


@pytest.mark.parametrize("origin", ["unknown", "real", None])
async def test_bound_empty_non_synthetic_collection(tmp_path, monkeypatch, origin):
    config = {
        "collectionId": "empty-local",
        "reviewState": "unknown",
        "target": {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "databaseOid": 1,
            "readRole": "reader",
        },
    }
    if origin is not None:
        config["origin"] = origin
    path = tmp_path / "collection.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    monkeypatch.setattr(
        "app.services.collection.database_identity",
        AsyncMock(
            return_value={
                "database": "test",
                "databaseOid": 1,
                "role": "reader",
                "superuser": False,
                "canWrite": False,
            }
        ),
    )
    inspection = AsyncMock()
    monkeypatch.setattr("app.services.collection.inspect_fixture", inspection)
    settings = Settings(
        _env_file=None,
        debug=False,
        database_url="postgresql+asyncpg://reader:x@localhost:5432/test",
        catalog_collection_manifest=str(path),
    )
    admitted, slugs = await admit_collection(None, settings)
    context = collection_context(admitted)
    assert context["origin"] == (origin or "unknown")
    assert context["reviewState"] == "unknown" and slugs == {}
    assert all(not rows for rows in inspection.call_args.args[1]["tables"].values())


def test_non_synthetic_snapshot_preserves_raw_status_and_rejects_demo(tmp_path):
    from uuid import uuid4

    from app.services.demo_manifest import snapshot_rows

    manifest = {
        "collectionId": "unreviewed",
        "origin": "unknown",
        "tables": {name: [] for name in fixture_rows()["tables"]},
    }
    manifest["tables"]["investigation"] = [
        {
            "id": str(uuid4()),
            "psi_id": "OWNER-IDENTITY",
            "title": "Unreviewed record",
            "research_purpose": None,
            "platform": None,
        }
    ]
    manifest["tables"]["source_document"] = [
        {
            "id": str(uuid4()),
            "investigation_id": manifest["tables"]["investigation"][0]["id"],
            "source_url": "https://owner.invalid/original",
            "doi": None,
            "document_type": "unknown",
            "version": None,
            "ingestion_status": "OWNER_UNKNOWN",
        }
    ]
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert (
        snapshot_rows(path)["tables"]["source_document"][0]["ingestion_status"] == "OWNER_UNKNOWN"
    )
    manifest["tables"]["investigation"][0]["psi_id"] = "SYNTHETIC-MIXING"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(Phase4Error):
        snapshot_rows(path)


@pytest.mark.parametrize("duplicate", [False, True])
def test_snapshot_uuid_spelling_preserved_without_duplicate_loss(tmp_path, duplicate):
    from uuid import UUID

    from app.models import Base
    from app.services.demo_manifest import snapshot_rows

    identity = UUID("abc12345-0000-4000-8000-000000000001")
    row = {
        "id": str(identity).upper(),
        "psi_id": "LOCAL-UNKNOWN",
        "title": "Local test",
        "platform": None,
        "research_purpose": None,
    }
    manifest = {
        "collectionId": "local-test",
        "origin": "unknown",
        "tables": {name: [] for name in Base.metadata.tables},
    }
    manifest["tables"]["investigation"] = [row]
    if duplicate:
        manifest["tables"]["investigation"].append(
            {**row, "id": identity.hex, "psi_id": "LOCAL-OTHER"}
        )
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    if duplicate:
        with pytest.raises(Phase4Error, match="DATASET_CONFLICT"):
            snapshot_rows(path)
    else:
        assert snapshot_rows(path)["tables"]["investigation"][0]["id"] == identity
