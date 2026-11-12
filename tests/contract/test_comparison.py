from uuid import uuid4

import pytest


@pytest.mark.parametrize(
    "extra", [{"observationLimit": 101}, {"observationOffset": -1}, {"verified": True}]
)
async def test_invalid_comparison_never_touches_data(client, extra):
    response = await client.post(
        "/api/v1/compare", json={"investigationIds": [str(uuid4()), str(uuid4())], **extra}
    )
    assert response.status_code == 422


async def test_malformed_comparison_json_is_safe(client):
    response = await client.post(
        "/api/v1/compare", content="{broken", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "body",
    [
        {"investigation_ids": [str(uuid4()), str(uuid4())]},
        *[
            {"investigationIds": [str(uuid4()), str(uuid4())], "observationLimit": value}
            for value in [True, "2", 2.0]
        ],
        {"investigationIds": [str(uuid4()), str(uuid4())], "observation_offset": 1},
    ],
)
async def test_wire_body_rejected_before_dependency(client, application, body):
    from app.api.dependencies import get_comparison

    def forbidden():
        pytest.fail("Invalid wire input reached the domain dependency")

    application.dependency_overrides[get_comparison] = forbidden
    response = await client.post("/api/v1/compare", json=body)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"


@pytest.mark.parametrize("swap_units", [False, True])
async def test_comparison_label_associations_through_http(client, application, swap_units):
    from unittest.mock import AsyncMock

    from app.api.dependencies import get_comparison
    from app.models import Investigation, Measurement, TestRun
    from app.services.comparison import ComparisonService
    from tests.fixtures.phase4 import comparison_manifest

    manifest = comparison_manifest(swap_units=swap_units)
    tables = manifest["tables"]
    investigations = [Investigation(**row) for row in tables["investigation"][:2]]
    ids = [row.id for row in investigations]
    context = {
        "collectionId": manifest["collectionId"],
        "origin": "synthetic",
        "reviewState": "unreviewed",
        "caveats": ["Synthetic test data"],
    }
    service = ComparisonService(None, context, {})
    service.repo.bulk_investigations = AsyncMock(return_value=investigations)
    service.repo.tag_previews = AsyncMock(return_value={identity: ([], 0) for identity in ids})
    run_rows = [TestRun(**row) for row in tables["test_run"]]
    service.repo.run_children_counts = AsyncMock(
        return_value={row.id: {"conditions": 1, "measurements": 1} for row in run_rows}
    )
    runs = dict(zip([row.id for row in run_rows], await service.run_views(run_rows), strict=True))
    pages = {}
    for identity in ids:
        items = [
            {
                "measurement": service.measurement(Measurement(**row)),
                "run": runs[row["test_run_id"]],
                "context": context,
            }
            for row in tables["measurement"]
            if runs[row["test_run_id"]]["investigation_id"] == identity
        ]
        pages[identity] = service.page(
            items[::-1], len(items), 0, 20, f"/investigations/{identity}/measurements"
        )
    service.observations = AsyncMock(side_effect=lambda identity, query: pages[identity])
    application.dependency_overrides[get_comparison] = lambda: service
    response = await client.post(
        "/api/v1/compare", json={"investigationIds": [str(i) for i in ids]}
    )
    assert response.status_code == 200, response.text
    result = response.json()
    caveats = " ".join(result["context"]["caveats"])
    assert ("UNIT_LABEL_MISMATCH" in caveats) == swap_units
    assert "OBSERVABLE_LABEL_MISMATCH" not in caveats
    assert "RUN_CONTEXT_LABEL_MISMATCH" not in caveats
    assert result["comparability"] == "not_established"
    assert result["deltas"] is None and result["highlights"] is None
    assert [s["investigation"]["id"] for s in result["studies"]] == [str(i) for i in ids]
