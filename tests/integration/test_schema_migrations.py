import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect

from app.models import Base
from tests.erd_reference import erd_tables
from tests.postgres_fixtures import validate_test_url

pytestmark = pytest.mark.integration


def test_clean_database_upgrades_through_all_three_groups(migrated_database) -> None:
    assert [len(tables) for tables in migrated_database.snapshots.values()] == [9, 16, 21]
    assert migrated_database.versions == ["0001_must_have", "0002_should_have", "0003_could_have"]
    assert migrated_database.snapshots["0003_could_have"] == set(erd_tables())
    assert "alembic_version" not in migrated_database.snapshots["0003_could_have"]


async def test_live_schema_matches_models_including_fk_unique_indexes_and_nulls(pg_session):
    connection = await pg_session.connection()

    def verify(sync_connection):
        inspector = inspect(sync_connection)
        tables = set(inspector.get_table_names()) - {"alembic_version"}
        assert tables == set(Base.metadata.tables)
        for name in tables:
            model_table = Base.metadata.tables[name]
            actual_columns = {column["name"]: column for column in inspector.get_columns(name)}
            assert set(actual_columns) == set(model_table.c.keys())
            for column in model_table.c:
                assert actual_columns[column.name]["nullable"] == column.nullable
            assert inspector.get_pk_constraint(name)["constrained_columns"] == ["id"]
            actual_fks = {
                (
                    tuple(fk["constrained_columns"]),
                    fk["referred_table"],
                    tuple(fk["referred_columns"]),
                )
                for fk in inspector.get_foreign_keys(name)
            }
            expected_fks = {
                ((fk.parent.name,), fk.column.table.name, (fk.column.name,))
                for fk in model_table.foreign_keys
            }
            assert actual_fks == expected_fks
            actual_unique = {
                tuple(u["column_names"]) for u in inspector.get_unique_constraints(name)
            }
            expected_unique = (
                {("psi_id",)}
                if name == "investigation"
                else ({("slug",)} if name == "tag" else set())
            )
            assert actual_unique == expected_unique
            actual_indexes = {tuple(i["column_names"]) for i in inspector.get_indexes(name)}
            assert {(fk.parent.name,) for fk in model_table.foreign_keys} <= actual_indexes
        context = MigrationContext.configure(sync_connection, opts={"compare_type": True})
        assert compare_metadata(context, Base.metadata) == []

    await connection.run_sync(verify)


@pytest.mark.parametrize(
    "raw",
    [
        "postgresql+asyncpg://user:pass@localhost/flameguard",
        "postgresql+asyncpg://user:pass@localhost/not_a_test_database",
        "sqlite:///flameguard_test_schema",
    ],
)
def test_test_database_guard_rejects_unsafe_targets(raw):
    with pytest.raises(ValueError):
        validate_test_url(raw, "postgresql+asyncpg://user:pass@localhost/flameguard")
