from unittest.mock import AsyncMock

import pytest

from app.services.catalog import CatalogService
from app.services.errors import Phase4Error


async def test_unknown_and_noncanonical_slug_are_not_guessed():
    service = CatalogService(None, {}, {"SYNTHETIC-1": "synthetic-one"})
    for slug in ["missing", "SYNTHETIC-ONE", "synthetic title"]:
        with pytest.raises(Phase4Error, match="ENTITY_NOT_FOUND"):
            await service.by_slug(slug)


async def test_stale_slug_is_unavailable_not_fake():
    service = CatalogService(None, {}, {"SYNTHETIC-1": "synthetic-one"})
    service.repo.by_psi = AsyncMock(return_value=None)
    with pytest.raises(Phase4Error, match="IDENTITY_MAPPING_UNAVAILABLE"):
        await service.by_slug("synthetic-one")
