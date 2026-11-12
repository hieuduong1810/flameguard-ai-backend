"""Lossless scenario storage for a trusted writable session."""

import json
from decimal import Decimal
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Scenario
from app.repositories.scenarios import ScenarioRepository
from app.schemas.api.scenarios import Airflow, Gravity, ScenarioInput

AMBIENT_OXYGEN = "ambient_oxygen_fraction_percent"


class ScenarioStorageError(ValueError):
    pass


def encode_quantity(quantity: Gravity | Airflow) -> str:
    return json.dumps({"version": 1, **quantity.model_dump()}, separators=(",", ":"))


def decode_quantity(raw: str, model: type[Gravity] | type[Airflow]):
    data = json.loads(raw)
    if not isinstance(data, dict) or data.pop("version", None) != 1:
        raise ScenarioStorageError("Unsupported scenario serialization")
    quantity = model.model_validate(data)
    if encode_quantity(quantity) != raw:
        raise ScenarioStorageError("Unsupported scenario serialization")
    return quantity.model_dump()


def serialize(scenario: ScenarioInput) -> Scenario:
    if (
        {"description", "preset_key"} & scenario.model_fields_set
        or any(
            value is None
            for value in (
                scenario.name,
                scenario.environment_label,
                scenario.material,
                scenario.gravity,
                scenario.oxygen,
                scenario.pressure,
                scenario.airflow,
            )
        )
        or "label" in scenario.material.model_fields_set
        or scenario.oxygen.meaning != AMBIENT_OXYGEN
        or "\x00" in scenario.name
        or "\x00" in scenario.environment_label
    ):
        raise ScenarioStorageError("Scenario cannot be represented losslessly")
    return Scenario(
        name=scenario.name,
        environment=scenario.environment_label,
        material=scenario.material.key,
        gravity=encode_quantity(scenario.gravity),
        ventilation=encode_quantity(scenario.airflow),
        oxygen_pct=Decimal(scenario.oxygen.value),
        pressure_psi=Decimal(scenario.pressure.value),
    )


def deserialize(row: Scenario) -> ScenarioInput:
    try:
        return ScenarioInput.model_validate(
            {
                "name": row.name,
                "environmentLabel": row.environment,
                "material": {"key": row.material},
                "gravity": decode_quantity(row.gravity, Gravity),
                "airflow": decode_quantity(row.ventilation, Airflow),
                "oxygen": {
                    "value": format(row.oxygen_pct, "f"),
                    "unit": "%",
                    "meaning": AMBIENT_OXYGEN,
                },
                "pressure": {"value": format(row.pressure_psi, "f"), "unit": "psia"},
            }
        )
    except (ValidationError, ValueError, TypeError):
        raise ScenarioStorageError("Unsupported scenario serialization") from None


async def persist_scenario(session: AsyncSession, scenario: ScenarioInput) -> UUID:
    row = serialize(scenario)
    async with session.begin():
        await ScenarioRepository(session).add_scenario(row)
        await session.refresh(row)
        if deserialize(row).model_dump(exclude_unset=True) != scenario.model_dump(
            exclude_unset=True
        ):
            raise ScenarioStorageError("Scenario did not round-trip exactly")
        identity = row.id
    return identity
