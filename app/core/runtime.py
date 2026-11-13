from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base
from app.repositories.collection import RUNTIME_TABLES


class RuntimeDatabase:
    def __init__(self, settings):
        raw = settings.runtime_database_url.get_secret_value()
        reader = make_url(settings.database_url.get_secret_value())
        writer = make_url(raw)
        if (reader.host, reader.port or 5432, reader.database) != (
            writer.host,
            writer.port or 5432,
            writer.database,
        ):
            raise ValueError("Runtime database must match scientific database")
        self.engine = create_async_engine(raw, hide_parameters=True, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def validate(self, session):
        unsafe = await session.scalar(
            text("""
            SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolbypassrls OR rolreplication
              OR has_schema_privilege(current_user, 'public', 'CREATE')
              OR has_database_privilege(current_user,current_database(),'CREATE')
              OR EXISTS(SELECT 1 FROM pg_roles other WHERE other.rolname<>current_user
                 AND pg_has_role(current_user,other.oid,'MEMBER'))
            FROM pg_roles WHERE rolname=current_user
        """)
        )
        if unsafe:
            raise ValueError("Unsafe runtime role")
        for table in Base.metadata.tables:
            permissions = (
                (
                    await session.execute(
                        text("""
                SELECT has_table_privilege(current_user,:table,'SELECT') AS readable,
                has_table_privilege(current_user,:table,'INSERT') AS insertable,
                has_table_privilege(current_user,:table,
                  'UPDATE,DELETE,TRUNCATE,TRIGGER') AS mutable,
                pg_get_userbyid(c.relowner)=current_user AS owner
                FROM pg_class c WHERE c.oid=to_regclass(:table)
            """),
                        {"table": "public." + table},
                    )
                )
                .mappings()
                .one()
            )
            if permissions["owner"] or permissions["mutable"]:
                raise ValueError("Unsafe runtime table privileges")
            if permissions["insertable"] != (table in RUNTIME_TABLES):
                raise ValueError("Unexpected runtime write scope")
            if table in RUNTIME_TABLES and not permissions["readable"]:
                raise ValueError("Missing runtime read privilege")

    async def close(self):
        await self.engine.dispose()
