import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.repositories.phase4_catalog import CatalogReadRepository
from app.schemas.api.queries import CatalogQuery, PageQuery
from app.services.unit_of_work import read_unit_of_work

pytestmark = pytest.mark.integration


async def test_filter_same_run_not_different_runs(phase4_db):
    engine = create_async_engine(phase4_db["reader_url"])
    try:
        async with async_sessionmaker(engine)() as session, read_unit_of_work(session):
            rows, total = await CatalogReadRepository(session).investigations(
                CatalogQuery(material="TEST_MATERIAL_A", gravityRaw="1g")
            )
            assert total == 1 and rows[0].psi_id == "SYNTHETIC-PHASE4-2"
    finally:
        await engine.dispose()


async def test_preview_matches_ordered_direct_tags(phase4_db):
    engine = create_async_engine(phase4_db["reader_url"])
    try:
        async with async_sessionmaker(engine)() as session, read_unit_of_work(session):
            repo = CatalogReadRepository(session)
            ids = [r["id"] for r in phase4_db["manifest"]["tables"]["investigation"]]
            previews = await repo.tag_previews(ids)
            for identity in ids:
                direct, count = await repo.tags(identity, PageQuery())
                tags, total = previews[identity]
                assert total == count
                assert [r.id for r in tags] == [r.id for r in direct]
    finally:
        await engine.dispose()
