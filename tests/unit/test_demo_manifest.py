import json

import pytest

from app.models import Base
from app.services.demo_manifest import DEMO_ROOT, fixture_rows
from app.services.errors import Phase4Error


@pytest.mark.parametrize(
    "kind", ["duplicate_id", "duplicate_psi", "verified", "fake_doi", "bad_fk"]
)
def test_invalid_fixture_rejected_before_connection(tmp_path, kind):
    data = json.loads((DEMO_ROOT / "phase4-v1.json").read_text())
    tables = data["tables"]
    if kind == "duplicate_id":
        tables["investigation"][1]["id"] = tables["investigation"][0]["id"]
    if kind == "duplicate_psi":
        tables["investigation"][1]["psi_id"] = tables["investigation"][0]["psi_id"]
    if kind == "verified":
        tables["evidence_claim"][0]["review_status"] = "Verified"
    if kind == "fake_doi":
        tables["source_document"][0]["doi"] = "10.0000/fake"
    if kind == "bad_fk":
        tables["test_run"][0]["investigation_id"] = "00000000-0000-4000-8000-000000000000"
    path = tmp_path / "fixture.json"
    path.write_text(json.dumps(data))
    with pytest.raises(Phase4Error):
        fixture_rows(path)


@pytest.mark.parametrize("spelling", ["upper", "hex", "braces", "urn"])
@pytest.mark.parametrize("conflicting", [False, True])
def test_canonical_duplicate_uuid_refused(tmp_path, spelling, conflicting):
    from uuid import UUID

    data = json.loads((DEMO_ROOT / "phase4-v1.json").read_text(encoding="utf-8"))
    row = data["tables"]["evidence_claim"][0]
    identity = UUID(row["id"])
    duplicate = {
        **row,
        "id": {
            "upper": str(identity).upper(),
            "hex": identity.hex,
            "braces": "{" + str(identity) + "}",
            "urn": identity.urn,
        }[spelling],
    }
    if conflicting:
        duplicate["claim_text"] = "TEST_ONLY conflicting duplicate"
    data["tables"]["evidence_claim"].append(duplicate)
    path = tmp_path / "duplicate.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(Phase4Error, match="DATASET_CONFLICT"):
        fixture_rows(path)


@pytest.mark.parametrize("table", sorted(Base.metadata.tables))
async def test_repository_refuses_canonical_duplicates_before_sql(table):
    from unittest.mock import AsyncMock
    from uuid import uuid4

    from app.models import Base
    from app.repositories.collection import inspect_fixture

    identity = uuid4()
    manifest = {"tables": {name: [] for name in Base.metadata.tables}}
    manifest["tables"][table] = [{"id": identity}, {"id": str(identity).upper()}]
    session = AsyncMock()
    with pytest.raises(Phase4Error, match="DATASET_CONFLICT"):
        await inspect_fixture(session, manifest, allow_subset=True)
    session.stream.assert_not_called()


@pytest.mark.parametrize("spelling", ["upper", "hex", "braces", "urn"])
def test_single_supported_uuid_spelling_keeps_foreign_keys(tmp_path, spelling):
    from uuid import UUID

    data = json.loads((DEMO_ROOT / "phase4-v1.json").read_text(encoding="utf-8"))
    identity = UUID(data["tables"]["evidence_claim"][0]["id"])
    data["tables"]["evidence_claim"][0]["id"] = {
        "upper": str(identity).upper(),
        "hex": identity.hex,
        "braces": "{" + str(identity) + "}",
        "urn": identity.urn,
    }[spelling]
    path = tmp_path / "single.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    parsed = fixture_rows(path)
    assert parsed["tables"]["evidence_claim"][0]["id"] == identity
    assert any(row["claim_id"] == identity for row in parsed["tables"]["claim_source"])
