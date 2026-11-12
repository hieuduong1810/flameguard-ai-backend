from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.schemas.api.comparison import CompareRequest
from app.services.comparison import ComparisonService
from app.services.errors import Phase4Error


async def test_missing_study_fails_whole_comparison():
    service = ComparisonService(None, {}, {})
    service.repo.bulk_investigations = AsyncMock(return_value=[])
    with pytest.raises(Phase4Error, match="ENTITY_NOT_FOUND"):
        await service.compare(CompareRequest(investigationIds=[uuid4(), uuid4()]))


async def test_comparison_explains_examined_pages_without_scientific_inference():
    from types import SimpleNamespace

    ids = [uuid4(), uuid4()]
    service = ComparisonService(None, {"caveats": []}, {})
    service.repo.bulk_investigations = AsyncMock(return_value=[SimpleNamespace(id=i) for i in ids])
    service.investigation_views = AsyncMock(return_value=[{"id": i} for i in ids])
    pages = [
        {
            "items": [
                {
                    "measurement": {
                        "observable": observable,
                        "unit": unit,
                        "measured_value": value,
                    },
                    "run": {
                        "gravity": None,
                        "material_type": None,
                        "sample_geometry": None,
                        "conditions": {"total": 0},
                    },
                }
            ],
            "total": 2,
            "offset": 0,
            "next": "next",
        }
        for observable, unit, value in [("A", "mm/s", "0"), ("B", "K", None)]
    ]
    service.observations = AsyncMock(side_effect=pages)
    result = await service.compare(CompareRequest(investigationIds=ids))
    caveats = " ".join(result["context"]["caveats"])
    for reason in [
        "OBSERVABLE_LABEL_MISMATCH",
        "UNIT_LABEL_MISMATCH",
        "UNMATCHED_OBSERVABLE",
        "MISSING_VALUE",
        "MISSING_RUN_CONTEXT",
        "CONDITIONS_MISSING",
        "PARTIAL_OBSERVATION_PAGE",
    ]:
        assert reason in caveats
    assert result["studies"][0]["observations"] == pages[0]
    assert result["deltas"] is None and result["highlights"] is None


@pytest.mark.parametrize("change", ["same", "reordered", "unit_swap", "observable", "run"])
def test_mismatch_describes_actual_label_associations(change):
    import copy

    from app.services.comparison import observation_caveats

    items = [
        {
            "measurement": {"observable": name, "unit": unit, "measured_value": value},
            "run": {
                "gravity": gravity,
                "material_type": "M",
                "sample_geometry": "S",
                "conditions": {"total": 1},
            },
        }
        for name, unit, gravity, value in [("A", "K", "g0", "0"), ("B", "mm/s", "g1", None)]
    ]
    other = copy.deepcopy(items)
    if change == "reordered":
        other.reverse()
    elif change == "unit_swap":
        other[0]["measurement"]["unit"], other[1]["measurement"]["unit"] = "mm/s", "K"
    elif change == "observable":
        other[0]["measurement"]["observable"] = "C"
    elif change == "run":
        other[0]["run"]["gravity"] = "g2"
    studies = [
        {"observations": {"items": rows, "offset": 0, "total": 2, "next": None}}
        for rows in [items, other]
    ]
    caveats = " ".join(observation_caveats(studies))
    assert ("OBSERVABLE_LABEL_MISMATCH" in caveats) == (change == "observable")
    assert ("UNIT_LABEL_MISMATCH" in caveats) == (change == "unit_swap")
    assert ("RUN_CONTEXT_LABEL_MISMATCH" in caveats) == (change == "run")
    assert "MISSING_VALUE" in caveats
