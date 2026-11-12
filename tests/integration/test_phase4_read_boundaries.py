import os

import pytest
from sqlalchemy import event, insert, text, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.models import Investigation
from app.schemas.api.queries import CatalogQuery
from app.services.catalog import CatalogService
from app.services.collection import admit_collection, collection_context
from app.services.errors import Phase4Error
from app.services.unit_of_work import read_unit_of_work
from tests.integration.phase4_fixtures import provision_phase4

pytestmark = pytest.mark.integration


async def test_association_queries_do_not_grow_per_claim(phase4_db):
    from app.repositories.phase4_evidence import EvidenceReadRepository

    engine = create_async_engine(phase4_db["reader_url"])
    queries = []

    def count(*args):
        queries.append(1)

    event.listen(engine.sync_engine, "before_cursor_execute", count)
    try:
        async with async_sessionmaker(engine)() as s:
            await s.connection()
            ids = [r["id"] for r in phase4_db["manifest"]["tables"]["evidence_claim"]]
            repo = EvidenceReadRepository(s)
            queries.clear()
            await repo.associations(ids[:1])
            first = len(queries)
            queries.clear()
            await repo.associations(ids)
            assert len(queries) == first == 2
    finally:
        await engine.dispose()


async def test_page_query_count_is_bounded(phase4_db):
    engine = create_async_engine(phase4_db["reader_url"])
    counts = []

    def count(*args):
        counts.append(1)

    event.listen(engine.sync_engine, "before_cursor_execute", count)
    try:
        for limit in [1, 4]:
            async with async_sessionmaker(engine)() as session:
                async with read_unit_of_work(session):
                    before = len(counts)
                    service = CatalogService(session, {}, {})
                    result = await service.investigations(CatalogQuery(limit=limit))
                    assert result["total"] == 4
                    current = len(counts) - before
                    if limit == 1:
                        initial = current
                    else:
                        assert current == initial
    finally:
        await engine.dispose()


async def test_real_readonly_transaction_rejects_writes(phase4_db):
    engine = create_async_engine(phase4_db["reader_url"])
    try:
        async with async_sessionmaker(engine)() as session:
            with pytest.raises(DBAPIError):
                async with read_unit_of_work(session):
                    assert await session.scalar(text("SHOW transaction_read_only")) == "on"
                    assert (
                        await session.scalar(text("SHOW transaction_isolation"))
                        == "repeatable read"
                    )
                    await session.execute(
                        update(Investigation).values(title="TEST_ONLY forbidden write")
                    )
            assert not session.in_transaction()
    finally:
        await engine.dispose()


async def test_snapshot_consistent_then_next_request_refuses_drift():
    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"])
    reader = create_async_engine(db["reader_url"])
    writer = create_async_engine(db["owner_url"])
    settings = Settings(
        _env_file=None,
        debug=False,
        database_url=db["reader_url"].render_as_string(hide_password=False),
        catalog_collection_manifest=str(db["collection"]),
    )
    identity = db["manifest"]["tables"]["investigation"][0]["id"]
    original = db["manifest"]["tables"]["investigation"][0]["title"]
    try:
        async with async_sessionmaker(reader)() as session:
            async with read_unit_of_work(session):
                config, slugs = await admit_collection(session, settings)
                async with async_sessionmaker(writer)() as mutation, mutation.begin():
                    await mutation.execute(
                        update(Investigation)
                        .where(Investigation.id == identity)
                        .values(title="TEST_ONLY drift")
                    )
                detail = await CatalogService(session, collection_context(config), slugs).detail(
                    identity
                )
                assert detail["title"] == original
            async with read_unit_of_work(session):
                with pytest.raises(Phase4Error, match="COLLECTION_SCOPE_INVALID"):
                    await admit_collection(session, settings)
    finally:
        await reader.dispose()
        await writer.dispose()


async def test_admission_batches_all_tables_and_refuses_foreign_rows(monkeypatch):
    from uuid import uuid4

    from app.models import Base
    from app.repositories.collection import ADMISSION_BATCH_SIZE, inspect_fixture
    from tests.fixtures.phase4 import pagination_manifest

    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=False)
    manifest = pagination_manifest(investigations=257, associations=257)
    writer = create_async_engine(db["owner_url"])
    reader = create_async_engine(db["reader_url"])
    batches, tables, queries = [], [], []
    original_stream = __import__(
        "sqlalchemy.ext.asyncio", fromlist=["AsyncSession"]
    ).AsyncSession.stream

    class ObservedResult:
        def __init__(self, result):
            self.result = result

        def mappings(self):
            return self

        async def partitions(self, size):
            async for batch in self.result.mappings().partitions(size):
                batches.append(len(batch))
                yield batch

        async def close(self):
            await self.result.close()

    async def observed_stream(session, statement, *args, **kwargs):
        tables.append(statement.get_final_froms()[0].name)
        assert statement.get_execution_options()["yield_per"] == ADMISSION_BATCH_SIZE
        return ObservedResult(await original_stream(session, statement, *args, **kwargs))

    def count(*args):
        queries.append(1)

    monkeypatch.setattr("sqlalchemy.ext.asyncio.AsyncSession.stream", observed_stream)
    event.listen(reader.sync_engine, "before_cursor_execute", count)
    try:
        async with async_sessionmaker(writer)() as session, session.begin():
            for table in Base.metadata.sorted_tables:
                if manifest["tables"][table.name]:
                    await session.execute(insert(table), manifest["tables"][table.name])
        async with async_sessionmaker(reader)() as session, read_unit_of_work(session):
            queries.clear()
            await inspect_fixture(session, manifest)
            assert len(queries) == len(tables) == 21
            assert set(tables) == set(Base.metadata.tables)
            assert max(batches) == ADMISSION_BATCH_SIZE and len(batches) > 9
        async with async_sessionmaker(writer)() as session, session.begin():
            await session.execute(
                insert(Investigation),
                [
                    {
                        "id": uuid4(),
                        "psi_id": "SYNTHETIC-FOREIGN",
                        "title": "TEST_ONLY foreign",
                        "research_purpose": None,
                        "platform": None,
                    }
                ],
            )
        async with async_sessionmaker(reader)() as session, read_unit_of_work(session):
            with pytest.raises(Phase4Error, match="DATASET_CONFLICT"):
                await inspect_fixture(session, manifest)
    finally:
        await writer.dispose()
        await reader.dispose()
