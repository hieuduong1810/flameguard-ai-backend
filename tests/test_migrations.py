from io import StringIO

from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic import command
from app.core.config import get_settings
from tests.erd_reference import ROOT, erd_tables


def test_three_ordered_revisions_cover_every_approved_entity(monkeypatch) -> None:
    config = Config(str(ROOT / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    assert scripts.get_heads() == ["0003_could_have"]
    assert [(r.revision, r.down_revision) for r in reversed(list(scripts.walk_revisions()))] == [
        ("0001_must_have", None),
        ("0002_should_have", "0001_must_have"),
        ("0003_could_have", "0002_should_have"),
    ]
    monkeypatch.setenv("DEBUG", "false")
    get_settings.cache_clear()
    output = StringIO()
    config.output_buffer = output
    try:
        command.upgrade(config, "head", sql=True)
    finally:
        get_settings.cache_clear()
    sql = output.getvalue()
    for table in erd_tables():
        assert sql.count(f"CREATE TABLE {table} (") == 1
    assert "0003_could_have" in sql
    assert "INSERT INTO investigation " not in sql


def test_revision_sql_creates_parents_before_children(monkeypatch) -> None:
    from app.models import Base

    config = Config(str(ROOT / "alembic.ini"))
    config.output_buffer = StringIO()
    monkeypatch.setenv("DEBUG", "false")
    get_settings.cache_clear()
    try:
        command.upgrade(config, "head", sql=True)
    finally:
        get_settings.cache_clear()
    sql = config.output_buffer.getvalue()
    for table in Base.metadata.tables.values():
        for fk in table.foreign_keys:
            assert sql.index(f"CREATE TABLE {fk.column.table.name} (") < sql.index(
                f"CREATE TABLE {table.name} ("
            )
