import asyncio
import ipaddress
import json
import re
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError, DBAPIError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.repositories.collection import database_identity
from app.repositories.demo_seed import insert_missing, lock_and_check_schema
from app.services.demo_manifest import fixture_rows
from app.services.errors import Phase4Error


def authorize_target(
    raw, environment, opt_in, confirmation, authorization, regular_database_url=None
):
    try:
        u = make_url(raw)
        if regular_database_url:
            regular = make_url(regular_database_url)
            if (u.host, u.port or 5432, u.database) == (
                regular.host,
                regular.port or 5432,
                regular.database,
            ):
                raise ValueError
        allowed = (
            environment in {"development", "test"}
            and opt_in
            and u.drivername == "postgresql+asyncpg"
            and not u.query
            and ipaddress.ip_address(u.host).is_loopback
            and re.fullmatch(r"flameguard_(demo|test)_[a-z0-9_]{1,50}", u.database)
            and confirmation == u.database
            and authorization["exclusiveDisposable"] is True
            and authorization["environment"] == environment
            and authorization["host"] == u.host
            and authorization["port"] == (u.port or 5432)
            and authorization["database"] == u.database
            and authorization["role"] == u.username
        )
        if not allowed:
            raise ValueError
        return u
    except (ValueError, TypeError, KeyError, AttributeError, ArgumentError):
        raise Phase4Error("TARGET_NOT_AUTHORIZED") from None


async def seed(
    raw, environment, opt_in, confirmation, authorization_path, regular_database_url=None
):
    try:
        authorization = json.loads(
            await asyncio.to_thread(Path(authorization_path).read_text, "utf-8")
        )
        u = authorize_target(
            raw, environment, opt_in, confirmation, authorization, regular_database_url
        )
        manifest = await asyncio.to_thread(fixture_rows)
        engine = create_async_engine(u, hide_parameters=True, connect_args={"timeout": 5})
        try:
            async with async_sessionmaker(engine)() as session, session.begin():
                identity = await database_identity(session)
                if (
                    identity["superuser"]
                    or identity["databaseOid"] != authorization["databaseOid"]
                    or identity["owner"] != authorization["owner"]
                    or identity["owner"] != identity["role"]
                    or authorization["collectionId"] != manifest["collectionId"]
                ):
                    raise Phase4Error("TARGET_NOT_AUTHORIZED")
                await lock_and_check_schema(session)
                counts = await insert_missing(session, manifest)
            return {"collectionId": manifest["collectionId"], "tables": counts}
        finally:
            await engine.dispose()
    except Phase4Error:
        raise
    except DBAPIError as exc:
        state = getattr(exc.orig, "sqlstate", "")
        code = {
            "55P03": "LOCK_TIMEOUT",
            "57014": "LOCK_TIMEOUT",
            "42P01": "SCHEMA_MISMATCH",
            "42703": "SCHEMA_MISMATCH",
            "42501": "TARGET_NOT_AUTHORIZED",
        }.get(state, "SEED_FAILED")
        raise Phase4Error(code) from None
    except Exception:
        raise Phase4Error("SEED_FAILED") from None
