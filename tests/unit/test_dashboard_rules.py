from unittest.mock import AsyncMock

import pytest

from app.schemas.api.queries import SelectionQuery
from app.services.dashboard import DashboardService


@pytest.mark.parametrize(
    "denominator,numerator,ratio",
    [(0, 0, None), (4, 2, "0.5"), (3, 1, "0.3333333333333333333333333333")],
)
async def test_link_coverage_is_not_review(monkeypatch, denominator, numerator, ratio):
    monkeypatch.setattr(
        "app.services.dashboard.summary_counts",
        AsyncMock(
            return_value={
                "investigationCount": denominator,
                "runCount": 0,
                "sourceCount": numerator,
                "claimCount": 0,
                "withSources": numerator,
            }
        ),
    )
    service = DashboardService(None, {}, {})
    service.investigations = AsyncMock(return_value={"items": []})
    result = await service.summary(SelectionQuery())
    assert result["sourceCoverage"]["ratio"] == ratio
    assert result["verifiedRunCount"] is None
    assert result["fuelDistribution"] is None
