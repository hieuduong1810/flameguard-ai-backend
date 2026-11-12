import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.repositories.dashboard import summary_counts
from app.schemas.api.queries import SelectionQuery

pytestmark = pytest.mark.integration


async def test_filtered_summary_has_distinct_shared_claim(phase4_db):
    engine = create_async_engine(phase4_db["reader_url"])
    try:
        async with async_sessionmaker(engine)() as s:
            result = await summary_counts(s, SelectionQuery(platform="TEST_PLATFORM"))
            assert result == {
                "investigationCount": 2,
                "runCount": 3,
                "sourceCount": 3,
                "claimCount": 1,
                "withSources": 2,
            }
    finally:
        await engine.dispose()
