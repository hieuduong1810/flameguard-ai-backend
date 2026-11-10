import importlib
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from tests.erd_reference import approved_nullables, erd_tables

DOMAINS = {
    "catalog": "investigation test_run test_condition measurement tag investigation_tag",
    "evidence": "source_document evidence_claim claim_source document_chunk",
    "scenarios": "scenario scenario_match match_dimension",
    "chat": "chat_session chat_message message_citation",
    "prediction": "model_version model_training_run prediction_result",
    "ingestion": "ingestion_job import_issue",
}
TABLE_MODULES = {name: domain for domain, tables in DOMAINS.items() for name in tables.split()}


def schema_for(table, suffix):
    name = "".join(part.title() for part in table.split("_")) + suffix
    return getattr(importlib.import_module(f"app.schemas.{TABLE_MODULES[table]}"), name)


def sample_values(table):
    values = {}
    for name, (kind, _) in erd_tables()[table].items():
        values[name] = {
            "uuid": uuid4(),
            "string": "TEST_ONLY_NOT_SCIENTIFIC_DATA",
            "decimal": Decimal("0.12345678901234567890123456789"),
            "int": 0,
            "datetime": datetime(2020, 1, 1, tzinfo=UTC),
        }[kind]
    return values


@pytest.mark.parametrize("table", erd_tables())
def test_create_and_attribute_read_contracts_for_every_entity(table) -> None:
    columns = erd_tables()[table]
    create = schema_for(table, "Create")
    read = schema_for(table, "Read")
    values = sample_values(table)
    create_values = {k: v for k, v in values.items() if k not in {"id", "created_at"}}
    assert set(create.model_fields) == set(columns) - {"id", "created_at"}
    assert set(read.model_fields) == set(columns)
    payload = create.model_validate(create_values)
    assert payload.model_dump() == create_values
    response = read.model_validate(SimpleNamespace(**values))
    assert response.model_dump() == values
    if any(kind == "decimal" for kind, _ in columns.values()):
        # Decimal JSON serialization preserves the original significant digits as a string.
        assert "0.12345678901234567890123456789" in response.model_dump_json()


@pytest.mark.parametrize("table", erd_tables())
def test_patch_omission_and_explicit_null_follow_approved_columns(table) -> None:
    update = schema_for(table, "Update")
    assert update().model_dump(exclude_unset=True) == {}
    nullable = approved_nullables()[table]
    for name in update.model_fields:
        if name in nullable:
            assert update.model_validate({name: None}).model_dump(exclude_unset=True) == {
                name: None
            }
        else:
            with pytest.raises(ValidationError, match="cannot be null"):
                update.model_validate({name: None})


@pytest.mark.parametrize("table", erd_tables())
def test_create_requires_nonnullable_inputs_and_rejects_invented_fields(table) -> None:
    create = schema_for(table, "Create")
    nullable = approved_nullables()[table]
    values = {k: v for k, v in sample_values(table).items() if k in create.model_fields}
    for name in create.model_fields:
        if name not in nullable:
            incomplete = {k: v for k, v in values.items() if k != name}
            with pytest.raises(ValidationError):
                create.model_validate(incomplete)
    with pytest.raises(ValidationError, match="Extra inputs"):
        create.model_validate({**values, "invented_field": "not in the ERD"})


def test_schema_rejects_naive_event_times_and_nonfinite_scientific_values() -> None:
    from app.schemas.ingestion import IngestionJobCreate
    from app.schemas.scenarios import ScenarioCreate

    with pytest.raises(ValidationError, match="timezone"):
        IngestionJobCreate(
            source_uri="test-only", status="pending", started_at=datetime(2020, 1, 1)
        )
    values = {k: v for k, v in sample_values("scenario").items() if k != "id"}
    with pytest.raises(ValidationError):
        ScenarioCreate(**{**values, "oxygen_pct": Decimal("NaN")})
