from decimal import Decimal
from typing import Literal

from app.integrations.scenario_evidence.execution import reject
from app.integrations.scenario_evidence.models import ProviderRequest, RunEvidence
from app.schemas.api.scenarios import DIMS, Dimension, DimensionName, ScenarioInput

POLICY_VERSION = "TEST_ONLY_exact-run-v1"
MAPPING_VERSION = "TEST_ONLY_condition-labels-v1"
VARIABLES = {
    "gravity": "TEST_ONLY_GRAVITY",
    "material": "TEST_ONLY_MATERIAL",
    "pressure": "TEST_ONLY_ABSOLUTE_PRESSURE",
    "airflow": "TEST_ONLY_AIRFLOW",
}
OXYGEN_VARIABLE = {
    "ambient_oxygen_fraction_percent": "TEST_ONLY_AMBIENT_OXYGEN",
    "oxidizer_oxygen_fraction_percent": "TEST_ONLY_OXIDIZER_OXYGEN",
}
OXYGEN_VARIABLES = frozenset(OXYGEN_VARIABLE.values()) | {"TEST_ONLY_OXYGEN"}
FIXTURE_MATERIALS = {"TEST_MATERIAL_A", "TEST_MATERIAL_B"}


def dimension_for(run: RunEvidence, scenario: ScenarioInput, name: DimensionName) -> Dimension:
    target = getattr(scenario, name)
    status = "unknown"
    ids = ()
    if not run.complete:
        reason = "CONDITION_LIMIT_EXCEEDED"
    elif target is None:
        reason = "SCENARIO_CONDITION_MISSING"
    elif name == "material" and target.key not in FIXTURE_MATERIALS:
        reason = "SCENARIO_MATERIAL_UNSUPPORTED"
    else:
        variable = OXYGEN_VARIABLE[target.meaning] if name == "oxygen" else VARIABLES[name]
        rows = tuple(row for row in run.conditions if row.variable == variable)
        ids = tuple(row.condition_id for row in rows)
        unit = None if name == "material" else target.unit
        if not rows:
            reason = (
                "OXYGEN_MEANING_UNSUPPORTED"
                if name == "oxygen"
                and any(row.variable in OXYGEN_VARIABLES for row in run.conditions)
                else "CONDITION_MISSING"
            )
        elif any(row.data_status != "TEST_ONLY" for row in rows):
            reason = "CONDITION_STATUS_UNSUPPORTED"
        elif any(row.unit != unit for row in rows):
            reason = "CONDITION_UNIT_UNSUPPORTED"
        elif any(
            row.value_numeric is not None and not row.value_numeric.is_finite() for row in rows
        ):
            reason = "CONDITION_VALUE_UNSUPPORTED"
        elif len({(row.value_numeric, row.value_text) for row in rows}) != 1:
            reason = "CONTRADICTORY_CONDITIONS"
        else:
            row = rows[0]
            original = row.value_text if name == "material" else row.value_numeric
            contradictory_field = row.value_numeric if name == "material" else row.value_text
            if original is None:
                reason = "CONDITION_VALUE_MISSING"
            elif contradictory_field is not None:
                reason = "CONDITION_VALUE_UNSUPPORTED"
            else:
                expected = target.key if name == "material" else Decimal(target.value)
                status = "support" if original == expected else "mismatch"
                reason = (
                    "TEST_ONLY_EXACT_EQUALITY" if status == "support" else "TEST_ONLY_VALUES_DIFFER"
                )
    return Dimension(
        dimension=name,
        status=status,
        reason_codes=(reason,),
        run_id=run.run.run_id,
        condition_ids=ids,
    )


def combined_for(run: RunEvidence, dimensions: tuple[Dimension, ...]) -> Dimension:
    statuses = {item.status for item in dimensions}
    status: Literal["support", "partial", "mismatch", "unknown"]
    if statuses == {"support"}:
        status, reason = "support", "TEST_ONLY_SAME_RUN"
    elif "support" in statuses:
        status, reason = "partial", "COMBINATION_NOT_SUPPORTED"
    elif statuses == {"mismatch"}:
        status, reason = "mismatch", "COMBINATION_NOT_SUPPORTED"
    else:
        status, reason = "unknown", "COMBINATION_NOT_ESTABLISHED"
    return Dimension(
        dimension="combined",
        status=status,
        reason_codes=(reason,),
        run_id=run.run.run_id,
        condition_ids=tuple(identity for item in dimensions for identity in item.condition_ids),
    )


class ExactFixturePolicy:
    version = POLICY_VERSION
    mapping_version = MAPPING_VERSION

    async def evaluate(self, request: ProviderRequest, runs: tuple[RunEvidence, ...]):
        return tuple(exact_decisions(run, request.scenario) for run in runs)


def exact_decisions(run: RunEvidence, scenario: ScenarioInput):
    dimensions = tuple(dimension_for(run, scenario, name) for name in DIMS[:-1])
    return (*dimensions, combined_for(run, dimensions))


def validate_decisions(
    request: ProviderRequest,
    runs: tuple[RunEvidence, ...],
    supplied,
) -> tuple[tuple[Dimension, ...], ...]:
    if (
        not request.test_only
        or request.scope.rule_version != POLICY_VERSION
        or request.scope.mapping_version != MAPPING_VERSION
        or not isinstance(supplied, tuple)
        or len(supplied) != len(runs)
    ):
        raise reject()
    if len({run.run.run_id for run in runs}) != len(runs):
        raise reject()
    seen = set()
    for run in runs:
        for row in run.conditions:
            if row.run_id != run.run.run_id or row.condition_id in seen:
                raise reject()
            seen.add(row.condition_id)
    # The engineering contract recognizes one declared policy. Verify all claims and
    # references against that policy rather than trusting returned support labels.
    expected = tuple(exact_decisions(run, request.scenario) for run in runs)
    if supplied != expected:
        raise reject()
    return expected
