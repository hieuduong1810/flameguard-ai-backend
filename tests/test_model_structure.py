import re
from html import unescape

import pytest
from sqlalchemy import DateTime, Integer, Numeric, Text, UniqueConstraint, Uuid, inspect
from sqlalchemy.orm import configure_mappers

from app.models import Base
from tests.erd_reference import ROOT, approved_nullables, erd_tables


def test_all_21_tables_and_mappers_are_registered() -> None:
    configure_mappers()
    assert len(Base.registry.mappers) == 21
    assert set(Base.metadata.tables) == set(erd_tables())


@pytest.mark.parametrize("table_name, columns", erd_tables().items())
def test_exact_erd_columns_types_keys_and_approved_nullability(table_name, columns) -> None:
    table = Base.metadata.tables[table_name]
    assert set(table.columns.keys()) == set(columns)
    assert [column.name for column in table.primary_key] == ["id"]
    expected_types = {
        "uuid": Uuid,
        "string": Text,
        "decimal": Numeric,
        "int": Integer,
        "datetime": DateTime,
    }
    nullables = approved_nullables()[table_name]
    for name, (kind, key) in columns.items():
        column = table.c[name]
        assert isinstance(column.type, expected_types[kind])
        assert column.nullable == (name in nullables)
        assert bool(column.foreign_keys) == (key == "FK")
        if kind == "decimal":
            assert column.type.precision is None and column.type.scale is None
        elif kind == "datetime":
            assert column.type.timezone
        elif kind == "string":
            assert column.type.length is None
    uniques = {
        tuple(c.name for c in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert uniques == {(name,) for name, (_, key) in columns.items() if key == "UK"}


def test_foreign_keys_follow_erd_cardinality_and_have_indexes() -> None:
    html = (ROOT / "docs/diagram/index.html").read_text(encoding="utf-8")
    diagrams = re.findall(r'<pre class="mermaid">(.*?)</pre>', html, re.S)[2:5]
    expected_pairs = set()
    for diagram in diagrams:
        for parent, child in re.findall(r"^  (\w+) [|o]+[-.]+o\{ (\w+) :", unescape(diagram), re.M):
            expected_pairs.add((parent.lower(), child.lower()))
    actual_pairs = set()
    for table in Base.metadata.tables.values():
        for fk in table.foreign_keys:
            actual_pairs.add((fk.column.table.name, table.name))
            assert fk.ondelete is None and fk.onupdate is None
            assert any(tuple(index.columns) == (fk.parent,) for index in table.indexes)
    assert actual_pairs == expected_pairs
    assert sum(len(t.foreign_keys) for t in Base.metadata.tables.values()) == 21


def test_relationships_do_not_issue_implicit_async_io_or_delete_cascades() -> None:
    configure_mappers()
    for mapper in Base.registry.mappers:
        for relation in mapper.relationships:
            assert relation.lazy == "raise"
            assert "delete" not in relation.cascade
            assert "delete-orphan" not in relation.cascade
            if not relation.viewonly:
                assert relation.back_populates
                inverse = inspect(relation.mapper.class_).relationships[relation.back_populates]
                assert inverse.mapper is mapper


def test_both_many_to_many_views_use_association_tables() -> None:
    from app.models import EvidenceClaim, Investigation, SourceDocument, Tag

    for model, attribute, secondary in [
        (EvidenceClaim, "source_documents", "claim_source"),
        (SourceDocument, "claims", "claim_source"),
        (Investigation, "tags", "investigation_tag"),
        (Tag, "investigations", "investigation_tag"),
    ]:
        relation = inspect(model).relationships[attribute]
        assert relation.secondary.name == secondary
        assert relation.viewonly  # Writes retain association IDs and provenance fields.
