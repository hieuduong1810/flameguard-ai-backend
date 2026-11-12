import pytest
from pydantic import ValidationError

from app.schemas.api.scenarios import EvaluationRequest, ScenarioInput
from app.services.scenario_interpretation import interpret
from app.services.scenario_persistence import ScenarioStorageError, deserialize, serialize
from tests.fixtures.phase5 import SCENARIO


@pytest.mark.parametrize(
    "value", [True, 0, 0.0, "1e0", "NaN", "Infinity", "-1", "00", "0." + "1" * 33]
)
def test_strict_decimal_originals(value):
    with pytest.raises(ValidationError):
        ScenarioInput.model_validate({"gravity": {"value": value, "unit": "g"}})


@pytest.mark.parametrize(
    "data",
    [
        {"environment_label": "fixture"},
        {"gravity": {"value": "0", "unit": "m/s²"}},
        {"oxygen": {"value": "21", "unit": "%"}},
        {"oxygen": {"value": "101", "unit": "%", "meaning": "ambient_oxygen_fraction_percent"}},
        {"material": {"key": "../unknown"}},
        {"gravity": {"value": "0", "unit": "g", "extra": True}},
    ],
)
def test_reject_ambiguous_units_scope_and_extras(data):
    with pytest.raises(ValidationError):
        ScenarioInput.model_validate(data)


def test_interpret_retains_omission_null_and_exact_lexical_digits():
    request = EvaluationRequest.model_validate(
        {
            "scenario": {
                "environmentLabel": "lunar",
                "pressure": None,
                "gravity": SCENARIO["gravity"],
            }
        }
    )
    interpreted = interpret(request.scenario)
    assert interpreted.original.gravity.value == "0.00"
    assert interpreted.field_states["gravity"] == "supplied"
    assert interpreted.field_states["pressure"] == "null"
    assert interpreted.field_states["airflow"] == "omitted"
    assert interpreted.original.airflow is None
    other = interpret(ScenarioInput.model_validate({"environmentLabel": "lunar"}))
    assert other.digest != interpreted.digest


def test_storage_is_explicit_and_round_trips_the_representable_subset():
    scenario = ScenarioInput.model_validate(SCENARIO)
    row = serialize(scenario)
    assert row.gravity == '{"version":1,"value":"0.00","unit":"g"}'
    assert row.ventilation == '{"version":1,"value":"0","unit":"cm/s"}'
    assert deserialize(row) == scenario


@pytest.mark.parametrize(
    "changes",
    [
        {"gravity": None},
        {"name": None},
        {"description": "context"},
        {"presetKey": None},
        {"material": {"key": "test", "label": "label"}},
    ],
)
def test_storage_rejects_unmappable_inputs(changes):
    with pytest.raises(ScenarioStorageError):
        serialize(ScenarioInput.model_validate(SCENARIO | changes))
