import asyncio
import json
import os
import subprocess
import sys

import pytest
from sqlalchemy import func, insert, select, text, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base, Investigation
from app.repositories.collection import inspect_fixture
from app.services.demo_seed import seed
from app.services.errors import Phase4Error
from tests.integration.phase4_fixtures import ROOT, provision_phase4

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("target_table", sorted(Base.metadata.tables))
async def test_unexpected_row_in_each_of_21_tables_is_refused(phase4_db, target_table):
    import copy
    from datetime import UTC, datetime
    from decimal import Decimal
    from uuid import UUID, uuid5

    expected = copy.deepcopy(phase4_db["manifest"])
    engine = create_async_engine(phase4_db["owner_url"])
    namespace = UUID("4980f2bb-8b06-4c24-a0b2-1040de3c52dc")
    try:
        async with async_sessionmaker(engine)() as s:

            async def parent(table):
                if expected["tables"][table.name]:
                    return expected["tables"][table.name][0]["id"]
                row = await extra(table)
                expected["tables"][table.name].append(row)
                return row["id"]

            async def extra(table):
                row = {}
                for col in table.columns:
                    if col.primary_key:
                        row[col.name] = uuid5(namespace, "foreign-" + table.name)
                    elif col.foreign_keys:
                        row[col.name] = await parent(next(iter(col.foreign_keys)).column.table)
                    elif col.nullable:
                        row[col.name] = None
                    elif col.type.python_type is Decimal:
                        row[col.name] = Decimal("0")
                    elif col.type.python_type is datetime:
                        row[col.name] = datetime(2020, 1, 1, tzinfo=UTC)
                    elif col.type.python_type is int:
                        row[col.name] = 0
                    else:
                        row[col.name] = "TEST_ONLY_FOREIGN_" + table.name
                await s.execute(insert(table), row)
                return row

            await extra(Base.metadata.tables[target_table])
            with pytest.raises(Phase4Error, match="DATASET_CONFLICT"):
                await inspect_fixture(s, expected)
            await s.rollback()
    finally:
        await engine.dispose()


async def reseed(db):
    return await seed(
        db["owner_url"].render_as_string(hide_password=False),
        "test",
        True,
        db["owner_url"].database,
        db["authorization"],
    )


@pytest.mark.parametrize("populate", [False, True])
@pytest.mark.parametrize("conflicting", [False, True])
async def test_seed_rejects_canonical_duplicates_before_insert(monkeypatch, populate, conflicting):
    import copy

    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=populate)
    manifest = copy.deepcopy(db["manifest"])
    duplicate = copy.deepcopy(manifest["tables"]["evidence_claim"][0])
    duplicate["id"] = str(duplicate["id"]).upper()
    if conflicting:
        duplicate["claim_text"] = "TEST_ONLY conflicting identity"
    manifest["tables"]["evidence_claim"].append(duplicate)
    monkeypatch.setattr("app.services.demo_seed.fixture_rows", lambda: manifest)
    writes = []

    def observe(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            writes.append(statement)

    event.listen(Engine, "before_cursor_execute", observe)
    try:
        with pytest.raises(Phase4Error, match="DATASET_CONFLICT"):
            await reseed(db)
        assert writes == []
    finally:
        event.remove(Engine, "before_cursor_execute", observe)
    expected = copy.deepcopy(db["manifest"])
    if not populate:
        expected["tables"] = {name: [] for name in Base.metadata.tables}
    engine = create_async_engine(db["owner_url"])
    try:
        async with async_sessionmaker(engine)() as session:
            await inspect_fixture(session, expected)
    finally:
        await engine.dispose()


async def test_seed_first_run_and_identical_concurrent_noops(phase4_db):
    expected = sum(len(v) for v in phase4_db["manifest"]["tables"].values())
    assert sum(v["inserted"] for v in phase4_db["initial"]["tables"].values()) == expected
    results = await asyncio.gather(reseed(phase4_db), reseed(phase4_db))
    assert all(sum(v["inserted"] for v in r["tables"].values()) == 0 for r in results)


async def test_cli_noop_and_missing_optin(phase4_db):
    env = {
        **os.environ,
        "APP_ENV": "test",
        "DEMO_DATABASE_URL": phase4_db["owner_url"].render_as_string(hide_password=False),
    }
    args = [
        sys.executable,
        str(ROOT / "scripts/seed_demo_data.py"),
        "--confirm-database",
        phase4_db["owner_url"].database,
        "--target-authorization",
        str(phase4_db["authorization"]),
    ]
    for optin, code in [(False, 1), (True, 0)]:
        result = await asyncio.to_thread(
            subprocess.run,
            args + (["--allow-synthetic"] if optin else []),
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == code
        body = json.loads(result.stdout)
        if optin:
            assert sum(v["inserted"] for v in body["tables"].values()) == 0
        else:
            assert body["error"] == "TARGET_NOT_AUTHORIZED"
        assert phase4_db["owner_url"].password not in result.stdout + result.stderr


async def test_owner_oid_and_role_mismatch_rejected(phase4_db, tmp_path):
    original = json.loads(phase4_db["authorization"].read_text())
    for key, value in [("databaseOid", 0), ("role", "wrong"), ("owner", "wrong")]:
        path = tmp_path / (key + ".json")
        path.write_text(json.dumps({**original, key: value}))
        with pytest.raises(Phase4Error, match="TARGET_NOT_AUTHORIZED"):
            await seed(
                phase4_db["owner_url"].render_as_string(hide_password=False),
                "test",
                True,
                phase4_db["owner_url"].database,
                path,
            )


@pytest.mark.parametrize("kind", ["altered_fixture", "unrelated_record"])
async def test_seed_conflict_preserves_existing_data(kind):
    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"])
    engine = create_async_engine(db["owner_url"], hide_parameters=True)
    session_factory = async_sessionmaker(engine)
    try:
        async with session_factory() as s, s.begin():
            if kind == "altered_fixture":
                await s.execute(
                    update(Investigation)
                    .where(Investigation.id == db["manifest"]["tables"]["investigation"][0]["id"])
                    .values(title="TEST_ONLY altered sentinel")
                )
            else:
                await s.execute(
                    insert(Investigation).values(
                        psi_id="TEST_ONLY_FOREIGN_SENTINEL", title="Not part of demo"
                    )
                )
        with pytest.raises(Phase4Error, match="DATASET_CONFLICT"):
            await reseed(db)
        async with session_factory() as s:
            titles = (await s.scalars(select(Investigation.title))).all()
            assert (
                ("TEST_ONLY altered sentinel" in titles)
                if kind == "altered_fixture"
                else ("Not part of demo" in titles)
            )
    finally:
        await engine.dispose()


async def test_mid_insert_failure_rolls_back_entire_seed(monkeypatch):
    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=False)

    async def fail(session, manifest):
        await session.execute(insert(Investigation), manifest["tables"]["investigation"][:1])
        raise RuntimeError("simulated internal failure")

    monkeypatch.setattr("app.services.demo_seed.insert_missing", fail)
    with pytest.raises(Phase4Error, match="SEED_FAILED"):
        await reseed(db)
    engine = create_async_engine(db["owner_url"], hide_parameters=True)
    try:
        async with async_sessionmaker(engine)() as s:
            for table in Base.metadata.sorted_tables:
                assert await s.scalar(select(func.count()).select_from(table)) == 0
    finally:
        await engine.dispose()


async def test_valid_subset_completion():
    db = await provision_phase4(os.environ["PHASE4_ADMIN_URL"], populate=False)
    engine = create_async_engine(db["owner_url"], hide_parameters=True)
    try:
        async with async_sessionmaker(engine)() as s, s.begin():
            await s.execute(insert(Investigation), db["manifest"]["tables"]["investigation"][:1])
        result = await reseed(db)
        assert result["tables"]["investigation"] == {"inserted": 3, "alreadyPresent": 1}
    finally:
        await engine.dispose()


async def test_lock_contention_is_bounded(phase4_db):
    engine = create_async_engine(phase4_db["owner_url"], hide_parameters=True)
    try:
        async with async_sessionmaker(engine)() as s:
            await s.execute(text("SELECT pg_advisory_xact_lock(641891004)"))
            with pytest.raises(Phase4Error, match="LOCK_TIMEOUT"):
                await reseed(phase4_db)
            await s.rollback()
    finally:
        await engine.dispose()
