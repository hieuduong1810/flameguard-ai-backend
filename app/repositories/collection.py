import json

from sqlalchemy import select, text

from app.models import Base
from app.services.demo_manifest import canonical, unique_rows_by_id
from app.services.errors import Phase4Error

ADMISSION_BATCH_SIZE = 64
RUNTIME_TABLES = frozenset({"chat_session", "chat_message", "message_citation"})


async def database_identity(session):
    return dict(
        (
            await session.execute(
                text("""
        SELECT current_database() AS database, current_user AS role,
               d.oid::bigint AS "databaseOid", pg_get_userbyid(d.datdba) AS owner,
               r.rolsuper AS superuser,
               EXISTS(SELECT 1 FROM pg_tables p WHERE p.schemaname='public'
                 AND has_table_privilege(current_user,
                   quote_ident(p.schemaname)||'.'||quote_ident(p.tablename),
                   'INSERT,UPDATE,DELETE,TRUNCATE')) AS "canWrite"
        FROM pg_database d JOIN pg_roles r ON r.rolname=current_user
        WHERE d.datname=current_database()
    """)
            )
        )
        .mappings()
        .one()
    )


async def inspect_fixture(
    session, manifest, *, allow_subset=False, content_hash=None, runtime_tables=frozenset()
):
    """Exact read-side membership validation, including unused approved tables."""
    # Validate the whole manifest before SQL or any UUID-keyed lookup can lose rows.
    indexed = {name: unique_rows_by_id(rows) for name, rows in manifest["tables"].items()}
    missing = {}
    for table in Base.metadata.sorted_tables:
        if table.name in runtime_tables:
            if indexed[table.name]:
                raise Phase4Error("DATASET_CONFLICT")
            continue
        expected = indexed[table.name]
        # Server-side cursor: DB content is never buffered as a whole table.
        # Remove matched identities, keeping only the already-loaded manifest.
        statement = select(table)
        if content_hash is not None:
            statement = statement.order_by(table.c.id)
        stream = await session.stream(statement.execution_options(yield_per=ADMISSION_BATCH_SIZE))
        try:
            async for batch in stream.mappings().partitions(ADMISSION_BATCH_SIZE):
                for row in batch:
                    exp = expected.pop(row["id"], None)
                    if exp is None or any(canonical(row[k]) != canonical(exp[k]) for k in exp):
                        raise Phase4Error("DATASET_CONFLICT")
                    if content_hash is not None:
                        original = json.dumps(
                            [table.name, dict(row), exp], sort_keys=True, default=str
                        )
                        content_hash.update(original.encode("utf-8"))
        finally:
            await stream.close()
        missing[table.name] = list(expected.values())
        if missing[table.name] and not allow_subset:
            raise Phase4Error("DATASET_CONFLICT")
    return missing
