"""Versioned synthetic records only; this is not a scientific importer."""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from app.models import Base
from app.services.errors import Phase4Error

DEMO_ROOT = Path(__file__).resolve().parents[2] / "data" / "demo"


def canonical(value):
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        text = format(value, "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def fixture_rows(path=None):
    return _manifest_rows(path or DEMO_ROOT / "phase4-v1.json", synthetic=True)


def snapshot_rows(path):
    """Read-only owner-declared snapshot; never imports or grants scientific review."""
    return _manifest_rows(path, synthetic=False)


def unique_rows_by_id(rows):
    """Index UUID identities only after checking their canonical uniqueness."""
    indexed = {}
    for row in rows:
        try:
            identity = row["id"]
            if not isinstance(identity, UUID):
                identity = UUID(identity)
        except (KeyError, ValueError, TypeError, AttributeError):
            raise Phase4Error("DATASET_CONFLICT") from None
        if identity in indexed:
            raise Phase4Error("DATASET_CONFLICT")
        indexed[identity] = row
    return indexed


def _manifest_rows(path, *, synthetic):
    manifest = json.loads(Path(path or DEMO_ROOT / "phase4-v1.json").read_text("utf-8"))
    tables = manifest["tables"]
    origin = manifest.get("origin", "unknown")
    if origin not in ({"synthetic"} if synthetic else {"real", "unknown"}) or set(tables) != set(
        Base.metadata.tables
    ):
        raise Phase4Error("DATASET_CONFLICT")
    known_demo_ids = (
        set()
        if synthetic
        else {r["id"] for rows in fixture_rows()["tables"].values() for r in rows}
    )
    for table in Base.metadata.sorted_tables:
        for row in tables[table.name]:
            if set(row) != set(table.columns.keys()):
                raise Phase4Error("DATASET_CONFLICT")
            for col in table.columns:
                value = row[col.name]
                if value is None:
                    if not col.nullable:
                        raise Phase4Error("DATASET_CONFLICT")
                    continue
                typ = col.type.python_type
                if typ is UUID:
                    row[col.name] = UUID(value)
                elif typ is Decimal:
                    row[col.name] = Decimal(value)
                    if not row[col.name].is_finite():
                        raise Phase4Error("DATASET_CONFLICT")
                elif typ is datetime:
                    row[col.name] = datetime.fromisoformat(value)
                    if row[col.name].tzinfo is None:
                        raise Phase4Error("DATASET_CONFLICT")
                elif not isinstance(value, typ):
                    raise Phase4Error("DATASET_CONFLICT")
                if (
                    synthetic
                    and col.name.endswith("status")
                    and value
                    not in {
                        "TEST_ONLY",
                        "SYNTHETIC_UNREVIEWED",
                    }
                ):
                    raise Phase4Error("DATASET_CONFLICT")
                if (
                    not synthetic
                    and isinstance(value, str)
                    and (
                        value.upper().startswith(
                            ("SYNTHETIC-", "TEST_ONLY", "SYNTHETIC_UNREVIEWED")
                        )
                        or "example.invalid" in value.lower()
                    )
                ):
                    raise Phase4Error("DATASET_CONFLICT")
            if not synthetic and row["id"] in known_demo_ids:
                raise Phase4Error("DATASET_CONFLICT")
        unique_rows_by_id(tables[table.name])
    for table in Base.metadata.sorted_tables:
        for row in tables[table.name]:
            for fk in table.foreign_keys:
                value = row[fk.parent.name]
                valid = {r[fk.column.name] for r in tables[fk.column.table.name]}
                if value is not None and value not in valid:
                    raise Phase4Error("DATASET_CONFLICT")
    for table, field, prefix in [
        ("investigation", "psi_id", "SYNTHETIC-"),
        ("tag", "slug", "synthetic-"),
    ]:
        values = [r[field] for r in tables[table]]
        if len(values) != len(set(values)) or (
            synthetic and any(not v.startswith(prefix) for v in values)
        ):
            raise Phase4Error("DATASET_CONFLICT")
    if synthetic and any(
        r["doi"] is not None or not r["source_url"].startswith("https://example.invalid/")
        for r in tables["source_document"]
    ):
        raise Phase4Error("DATASET_CONFLICT")
    return manifest
