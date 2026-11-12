from sqlalchemy import UniqueConstraint, insert, inspect, text

from app.models import Base
from app.repositories.collection import inspect_fixture
from app.services.errors import Phase4Error


async def lock_and_check_schema(session):
    await session.execute(text("SET LOCAL lock_timeout = '3s'"))
    await session.execute(text("SET LOCAL statement_timeout = '15s'"))
    await session.execute(text("SELECT pg_advisory_xact_lock(641891004)"))
    for table in sorted(Base.metadata.tables):
        await session.execute(text(f'LOCK TABLE "{table}" IN SHARE ROW EXCLUSIVE MODE'))
    version = (
        (await session.execute(text("SELECT version_num FROM alembic_version"))).scalars().all()
    )
    if version != ["0003_could_have"]:
        raise Phase4Error("SCHEMA_MISMATCH")
    columns = (
        await session.execute(
            text("""
        SELECT table_name,column_name,is_nullable,udt_name FROM information_schema.columns
        WHERE table_schema='public' AND table_name <> 'alembic_version'
    """)
        )
    ).all()
    observed = {(t, c): (n == "YES", k) for t, c, n, k in columns}
    types = {
        "UUID": "uuid",
        "CHAR(32)": "uuid",
        "TEXT": "text",
        "NUMERIC": "numeric",
        "DATETIME": "timestamptz",
        "INTEGER": "int4",
    }
    expected = {
        (t.name, c.name): (c.nullable, types[str(c.type).upper()])
        for t in Base.metadata.sorted_tables
        for c in t.columns
    }
    if observed != expected:
        raise Phase4Error("SCHEMA_MISMATCH")
    connection = await session.connection()

    def validate_constraints(sync_connection):
        inspector = inspect(sync_connection)
        names = list(Base.metadata.tables)
        options = {"schema": "public", "filter_names": names}
        primary = inspector.get_multi_pk_constraint(**options)
        foreign = inspector.get_multi_foreign_keys(**options)
        unique = inspector.get_multi_unique_constraints(**options)
        indexes = inspector.get_multi_indexes(**options)
        for table in Base.metadata.sorted_tables:
            key = ("public", table.name)
            if primary[key]["constrained_columns"] != ["id"]:
                return False
            actual_fk = {
                (tuple(f["constrained_columns"]), f["referred_table"], tuple(f["referred_columns"]))
                for f in foreign[key]
            }
            expected_fk = {
                ((f.parent.name,), f.column.table.name, (f.column.name,))
                for f in table.foreign_keys
            }
            if actual_fk != expected_fk:
                return False
            if any(
                f.get("options", {}).get(action) not in {None, "NO ACTION"}
                for f in foreign[key]
                for action in ["ondelete", "onupdate"]
            ):
                return False
            if {tuple(u["column_names"]) for u in unique[key]} != {
                tuple(c.name for c in u.columns)
                for u in table.constraints
                if isinstance(u, UniqueConstraint)
            }:
                return False
            actual_indexes = {tuple(i["column_names"]) for i in indexes[key] if not i["unique"]}
            required_indexes = {
                tuple(c.name for c in i.columns) for i in table.indexes if not i.unique
            }
            if not required_indexes <= actual_indexes:
                return False
        return True

    if not await connection.run_sync(validate_constraints):
        raise Phase4Error("SCHEMA_MISMATCH")
    foreign_writers = (
        await session.execute(
            text("""
        SELECT 1 FROM information_schema.table_privileges
        WHERE table_schema='public' AND grantee <> current_user
          AND privilege_type IN ('INSERT','UPDATE','DELETE','TRUNCATE','TRIGGER') LIMIT 1
    """)
        )
    ).first()
    owners = (
        await session.execute(
            text("""
        SELECT 1 FROM pg_tables WHERE schemaname='public' AND tableowner<>current_user LIMIT 1
    """)
        )
    ).first()
    if foreign_writers or owners:
        raise Phase4Error("TARGET_NOT_AUTHORIZED")


async def insert_missing(session, manifest):
    missing = await inspect_fixture(session, manifest, allow_subset=True)
    counts = {}
    for table in Base.metadata.sorted_tables:
        rows = missing[table.name]
        if rows:
            await session.execute(insert(table), rows)
        counts[table.name] = {
            "inserted": len(rows),
            "alreadyPresent": len(manifest["tables"][table.name]) - len(rows),
        }
    await inspect_fixture(session, manifest)
    return counts
