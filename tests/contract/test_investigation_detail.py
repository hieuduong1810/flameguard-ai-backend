from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.api.dependencies import get_catalog
from app.services.catalog import CatalogService


@pytest.mark.parametrize(
    "path", ["/investigations/" + str(uuid4()), "/investigations/by-slug/UNKNOWN"]
)
async def test_absent_identity_never_becomes_demo(client, application, path):
    service = CatalogService(None, {}, {})
    service.repo.get = AsyncMock(return_value=None)
    application.dependency_overrides[get_catalog] = lambda: service
    response = await client.get("/api/v1" + path)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ENTITY_NOT_FOUND"
