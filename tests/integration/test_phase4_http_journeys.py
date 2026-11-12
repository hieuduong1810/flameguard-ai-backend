from uuid import uuid4

import pytest

pytestmark = pytest.mark.integration


async def get_ok(client, path):
    response = await client.get("/api/v1" + path)
    assert response.status_code == 200, (path, response.text)
    return response.json()


async def test_all_read_surfaces_and_provenance(phase4_client, phase4_db):
    client = phase4_client
    cap = await get_ok(client, "/catalog/capabilities")
    assert cap["context"]["origin"] == "synthetic"
    listing = await get_ok(client, "/investigations?limit=2")
    assert listing["total"] == 4 and len(listing["items"]) == 2
    seen = [v["id"] for v in listing["items"]]
    while listing["next"]:
        response = await client.get(listing["next"])
        assert response.status_code == 200
        listing = response.json()
        seen += [v["id"] for v in listing["items"]]
    assert len(seen) == len(set(seen)) == 4
    inv = phase4_db["manifest"]["tables"]["investigation"][0]
    identity = str(inv["id"])
    detail = await get_ok(client, "/investigations/" + identity)
    slug_detail = await get_ok(client, "/investigations/by-slug/" + detail["slug"])
    assert detail["id"] == slug_detail["id"] and detail["psiId"] != identity
    assert detail["context"]["origin"] == "synthetic"
    await get_ok(client, f"/investigations/{identity}/tags")
    runs = await get_ok(client, f"/investigations/{identity}/runs")
    assert runs["total"] == 2
    for run in runs["items"]:
        assert run["verification"] == "unknown"
        await get_ok(client, f"/runs/{run['id']}/conditions")
        await get_ok(client, f"/runs/{run['id']}/measurements")
    observations = await get_ok(client, f"/investigations/{identity}/measurements")
    assert {v["measurement"]["measuredValue"] for v in observations["items"]} == {
        "0",
        "0.10000000000000000001",
    }
    sources = await get_ok(client, f"/investigations/{identity}/sources")
    assert sources["total"] == 2 and all(v["doi"] is None for v in sources["items"])
    claims = await get_ok(client, f"/investigations/{identity}/claims")
    assert claims["total"] == 1
    claim = claims["items"][0]
    links = await get_ok(client, f"/claims/{claim['id']}/sources?limit=1")
    collected = links["items"][:]
    while links["next"]:
        links = (await client.get(links["next"])).json()
        collected += links["items"]
    assert len(collected) == len({v["id"] for v in collected}) == 4
    assert any(v["contextMismatch"] for v in collected)
    assert any(v["testRunId"] is None for v in collected)
    summary = await get_ok(client, "/dashboard/summary")
    assert [
        summary[k] for k in ["investigationCount", "runCount", "sourceCount", "claimCount"]
    ] == [4, 4, 3, 1]
    assert summary["verifiedRunCount"] is None and summary["sourceCoverage"]["numerator"] == 2
    comparison = await client.post("/api/v1/compare", json={"investigationIds": seen[:2]})
    assert comparison.status_code == 200, comparison.text
    assert [v["investigation"]["id"] for v in comparison.json()["studies"]] == seen[:2]
    assert comparison.json()["deltas"] is None


@pytest.mark.parametrize(
    "query,total",
    [
        ("q=SYNTHETIC-PHASE4", 4),
        ("q=%25", 0),
        ("q=_", 3),
        ("material=TEST_MATERIAL_A&gravityRaw=1g", 1),
        ("platform=TEST_PLATFORM", 2),
        ("evidenceStatus=TEST_ONLY&reviewStatus=SYNTHETIC_UNREVIEWED", 2),
        ("sourceType=TEST_ONLY", 2),
        ("tag=synthetic-phase4-tag", 2),
        ("sort=runs-desc", 4),
        ("q=not-present", 0),
        ("q=%20%20", 4),
    ],
)
async def test_filter_membership(phase4_client, query, total):
    data = await get_ok(phase4_client, "/investigations?" + query)
    assert data["total"] == total


@pytest.mark.parametrize(
    "path,status",
    [
        ("/investigations?limit=0", 422),
        ("/investigations?limit=101", 422),
        ("/investigations?offset=-1", 422),
        ("/investigations?sort=confidence", 422),
        ("/investigations?facility=CIR", 422),
        ("/investigations?unknown=secret", 422),
        ("/investigations?limit=1&limit=2", 422),
        ("/investigations/not-a-uuid", 422),
        ("/investigations/" + str(uuid4()), 404),
        ("/investigations/by-slug/missing", 404),
    ],
)
async def test_safe_invalid_requests(phase4_client, path, status):
    response = await phase4_client.get("/api/v1" + path)
    assert response.status_code == status, response.text
    assert set(response.json()) == {"error", "context"}
    assert "secret" not in response.text


async def test_empty_children_and_zero_denominator(phase4_client, phase4_db):
    identity = str(phase4_db["manifest"]["tables"]["investigation"][3]["id"])
    for child in ["runs", "sources", "claims", "measurements", "tags"]:
        data = await get_ok(phase4_client, f"/investigations/{identity}/{child}")
        assert data["total"] == 0 and data["items"] == []
    summary = await get_ok(phase4_client, "/dashboard/summary?q=absent")
    assert summary["investigationCount"] == 0 and summary["sourceCoverage"]["ratio"] is None


@pytest.mark.parametrize("selection", [[], [str(uuid4())], [str(uuid4())] * 2, [str(uuid4())] * 4])
async def test_comparison_rejects_invalid_selection(phase4_client, selection):
    result = await phase4_client.post("/api/v1/compare", json={"investigationIds": selection})
    assert result.status_code == 422


async def test_comparison_missing_identity(phase4_client):
    result = await phase4_client.post(
        "/api/v1/compare", json={"investigationIds": [str(uuid4()), str(uuid4())]}
    )
    assert result.status_code == 404
