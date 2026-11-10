from datetime import UTC, datetime
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid", allow_inf_nan=False)

    @field_validator("*", mode="after")
    @classmethod
    def normalize_datetime(cls, value):
        if isinstance(value, datetime):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("Datetime values must include a timezone")
            return value.astimezone(UTC)
        return value


class PatchSchema(Schema):
    """Omitted fields are unchanged; explicit null is valid only for nullable columns."""

    non_nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> Self:
        for name in self.model_fields_set & self.non_nullable_fields:
            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self
