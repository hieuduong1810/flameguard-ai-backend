"""Opt-in tests create fresh databases; never clear, drop or migrate the development database."""

import asyncio
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from uuid import uuid4

import asyncpg
import pytest
from sqlalchemy import pool
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import Settings
from tests.erd_reference import ROOT, erd_tables


def validate_test_url(raw: str, development: str) -> URL:
    candidate = make_url(raw)
    dev = make_url(development)
    if (
        candidate.drivername != "postgresql+asyncpg"
        or not candidate.host
        or not candidate.database
        or not re.fullmatch(r"flameguard_test_[a-z0-9_]{1,35}", candidate.database)
        or candidate.database == dev.database
    ):
        raise ValueError("Use a distinct PostgreSQL test database named flameguard_test_<suffix>")
    return candidate


async def connect(url: URL, database: str | None = None):
    return await asyncpg.connect(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database=database or url.database,
        timeout=10,
        command_timeout=15,
    )


@dataclass
class MigratedDatabase:
    url: URL = field(repr=False)
    snapshots: dict[str, set[str]]
    versions: list[str]


@pytest.fixture(scope="session")
def migrated_database() -> Iterator[MigratedDatabase]:
    raw = os.getenv("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("Set TEST_DATABASE_URL for isolated PostgreSQL model/migration tests")
    settings = Settings()
    candidate = validate_test_url(raw, settings.database_url.get_secret_value())
    # Every run starts clean without deleting another run's database or user data.
    url = candidate.set(database=f"{candidate.database}_{uuid4().hex[:8]}")

    async def provision():
        admin = await connect(url, "postgres")
        try:
            # Name is regex-validated and contains only generated lowercase letters/digits/_ .
            await admin.execute(f'CREATE DATABASE "{url.database}"')
        finally:
            await admin.close()
        db = await connect(url)
        try:
            assert (
                await db.fetchval(
                    "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"
                )
                == 0
            )
        finally:
            await db.close()

    asyncio.run(provision())
    snapshots = {}
    versions = []
    for revision in ("0001_must_have", "0002_should_have", "0003_could_have"):
        env = {
            **os.environ,
            "DATABASE_URL": url.render_as_string(hide_password=False),
            "DEBUG": "false",
        }
        completed = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", revision],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if completed.returncode:
            # Do not echo a connection exception that could include credentials.
            pytest.fail(f"Migration {revision} failed in the isolated test database")

        async def snapshot():
            db = await connect(url)
            try:
                tables = await db.fetch(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public' "
                    "AND tablename <> 'alembic_version'"
                )
                version = await db.fetchval("SELECT version_num FROM alembic_version")
                return {row["tablename"] for row in tables}, version
            finally:
                await db.close()

        snapshots[revision], version = asyncio.run(snapshot())
        versions.append(version)
    state = {
        "database": url.database,
        "host": url.host,
        "port": url.port,
        "versions": versions,
        "table_counts": {k: len(v) for k, v in snapshots.items()},
    }
    tools_dir = ROOT / ".tools"
    tools_dir.mkdir(exist_ok=True)
    (tools_dir / "phase2-test-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    yield MigratedDatabase(url, snapshots, versions)

    async def verify_rollback():
        db = await connect(url)
        try:
            return {
                table: await db.fetchval(f'SELECT count(*) FROM "{table}"')
                for table in erd_tables()
            }
        finally:
            await db.close()

    row_counts = asyncio.run(verify_rollback())
    assert all(count == 0 for count in row_counts.values()), "Synthetic test rows escaped rollback"
    state["persisted_test_rows"] = row_counts
    (tools_dir / "phase2-test-state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


@pytest.fixture
async def pg_session(migrated_database):
    engine = create_async_engine(
        migrated_database.url, poolclass=pool.NullPool, hide_parameters=True
    )
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                async with AsyncSession(
                    bind=connection,
                    expire_on_commit=False,
                    join_transaction_mode="create_savepoint",
                ) as session:
                    yield session
            finally:
                if transaction.is_active:
                    await transaction.rollback()
    finally:
        await engine.dispose()
