import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.repositories.phase4_evidence import EvidenceReadRepository

pytestmark = pytest.mark.integration


async def test_distinct_claims_and_repeated_associations(phase4_db):
    engine = create_async_engine(phase4_db["reader_url"])
    try:
        async with async_sessionmaker(engine)() as s:
            repo = EvidenceReadRepository(s)
            claims = (
                await s.scalars(
                    repo.claims(phase4_db["manifest"]["tables"]["investigation"][0]["id"])
                )
            ).all()
            assert len(claims) == 1
            rows, counts = await repo.associations([claims[0].id])
            assert len(rows) == counts[claims[0].id] == 4
            assert len({r[1].id for r in rows}) == 3
    finally:
        await engine.dispose()
