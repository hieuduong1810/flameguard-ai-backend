from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.api.dependencies import get_evidence
from app.services.evidence import EvidenceService


@pytest.mark.parametrize(
    "path",
    [
        "/investigations/" + str(uuid4()) + "/sources",
        "/investigations/" + str(uuid4()) + "/claims",
        "/claims/" + str(uuid4()) + "/sources",
    ],
)
async def test_missing_evidence_parent_is_not_empty_success(client, application, path):
    service = EvidenceService(None, {}, {})
    service.repo.get = AsyncMock(return_value=None)
    application.dependency_overrides[get_evidence] = lambda: service
    response = await client.get("/api/v1" + path)
    assert response.status_code == 404
