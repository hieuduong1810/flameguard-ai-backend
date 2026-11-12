"""Creates new, retained test databases only. No existing database is reset or dropped."""

import asyncio
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import asyncpg
import pytest
from sqlalchemy.engine import make_url

from app.services.demo_manifest import DEMO_ROOT, fixture_rows
from app.services.demo_seed import seed

ROOT = Path(__file__).resolve().parents[2]


async def provision_phase4(admin_raw, *, populate=True):
    admin = make_url(admin_raw)
    suffix = uuid4().hex[:10]
    database, owner, reader = (
        f"flameguard_test_phase4_{suffix}",
        f"fg4_o_{suffix}",
        f"fg4_r_{suffix}",
    )
    password = secrets.token_hex(24)
    conn = await asyncpg.connect(
        host=admin.host,
        port=admin.port,
        user=admin.username,
        password=admin.password,
        database="postgres",
    )
    try:
        for role in [owner, reader]:
            await conn.execute(
                f'CREATE ROLE "{role}" LOGIN NOSUPERUSER NOCREATEDB '
                f"NOCREATEROLE PASSWORD '{password}'"
            )
        await conn.execute(f'CREATE DATABASE "{database}" OWNER "{owner}"')
        await conn.execute(f'REVOKE CONNECT ON DATABASE "{database}" FROM PUBLIC')
        await conn.execute(f'GRANT CONNECT ON DATABASE "{database}" TO "{reader}"')
    finally:
        await conn.close()
    owner_url = admin.set(username=owner, password=password, database=database)
    reader_url = owner_url.set(username=reader)
    env = {
        **os.environ,
        "DATABASE_URL": owner_url.render_as_string(hide_password=False),
        "DEBUG": "false",
    }
    result = await asyncio.to_thread(
        subprocess.run,
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, "Isolated Phase 4 migration failed (credentials redacted)"
    conn = await asyncpg.connect(
        host=admin.host, port=admin.port, user=owner, password=password, database=database
    )
    try:
        await conn.execute(f'GRANT USAGE ON SCHEMA public TO "{reader}"')
        await conn.execute(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{reader}"')
        oid = await conn.fetchval("SELECT oid FROM pg_database WHERE datname=current_database()")
    finally:
        await conn.close()
    directory = ROOT / ".tools" / database
    directory.mkdir()
    authorization = {
        "host": admin.host,
        "port": admin.port,
        "database": database,
        "role": owner,
        "databaseOid": oid,
        "owner": owner,
        "environment": "test",
        "exclusiveDisposable": True,
        "collectionId": "synthetic-phase4-v1",
    }
    auth_path = directory / "authorization.json"
    auth_path.write_text(json.dumps(authorization), encoding="utf-8")
    initial = (
        await seed(
            owner_url.render_as_string(hide_password=False), "test", True, database, auth_path
        )
        if populate
        else None
    )
    collection = {
        "collectionId": "synthetic-phase4-v1",
        "origin": "synthetic",
        "reviewState": "unreviewed",
        "fixture": str(DEMO_ROOT / "phase4-v1.json"),
        "slugs": str(DEMO_ROOT / "slugs-v1.json"),
        "target": {
            "host": admin.host,
            "port": admin.port,
            "database": database,
            "databaseOid": oid,
            "readRole": reader,
        },
    }
    collection_path = directory / "collection.json"
    collection_path.write_text(json.dumps(collection), encoding="utf-8")
    return {
        "owner_url": owner_url,
        "reader_url": reader_url,
        "authorization": auth_path,
        "collection": collection_path,
        "initial": initial,
        "manifest": fixture_rows(),
    }


@pytest.fixture(scope="session")
def phase4_db():
    raw = os.environ.get("PHASE4_ADMIN_URL")
    if not raw:
        pytest.skip("Set PHASE4_ADMIN_URL for isolated Phase 4 PostgreSQL verification")
    return asyncio.run(provision_phase4(raw))


@pytest.fixture
async def phase4_client(phase4_db):
    from httpx import ASGITransport, AsyncClient

    from app.core.config import Settings
    from app.main import create_app

    settings = Settings(
        _env_file=None,
        debug=False,
        app_env="test",
        database_url=phase4_db["reader_url"].render_as_string(hide_password=False),
        catalog_collection_manifest=str(phase4_db["collection"]),
    )
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
