from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.repositories.phase4_catalog import CatalogReadRepository
from app.schemas.api.queries import PageQuery

pytestmark = pytest.mark.integration


async def test_postgres_original_decimal_and_null(phase4_db):
    engine = create_async_engine(phase4_db["reader_url"])
    try:
        async with async_sessionmaker(engine)() as s:
            rows, total, runs = await CatalogReadRepository(s).observations(
                phase4_db["manifest"]["tables"]["investigation"][0]["id"], PageQuery()
            )
            assert total == 2
            assert {r.measured_value for r in rows} == {
                Decimal("0"),
                Decimal("0.10000000000000000001"),
            }
            assert all(r.uncertainty is None for r in rows)
            assert len(runs) == 2
    finally:
        await engine.dispose()
