import hashlib
import json

from pydantic.alias_generators import to_camel

from app.schemas.api.scenarios import DIMS, Interpretation, ScenarioInput

SCENARIO_MAPPING_VERSION = "scenario-input-v1"


def fingerprint(value):
    data = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def interpret(scenario: ScenarioInput) -> Interpretation:
    states = {
        to_camel(name): (
            "omitted"
            if name not in scenario.model_fields_set
            else "null"
            if getattr(scenario, name) is None
            else "supplied"
        )
        for name in ScenarioInput.model_fields
    }
    return Interpretation(
        original=scenario,
        digest=fingerprint(
            {
                "version": SCENARIO_MAPPING_VERSION,
                "original": scenario.model_dump(mode="json", by_alias=True, exclude_unset=True),
            }
        ),
        field_states=states,
        unavailable_fields=tuple(name for name in DIMS[:-1] if getattr(scenario, name) is None),
    )
