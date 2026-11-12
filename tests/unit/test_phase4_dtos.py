from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.api.common import DecimalString
from app.schemas.api.comparison import CompareRequest
from app.schemas.api.queries import CatalogQuery


def test_comparison_size_identity_and_extras():
    from uuid import uuid4

    ids = [str(uuid4()), str(uuid4())]
    assert CompareRequest(investigationIds=ids).observation_limit == 20
    for value in [[], ids[:1], ids * 2, [ids[0], ids[0]]]:
        with pytest.raises(ValidationError):
            CompareRequest(investigationIds=value)
    with pytest.raises(ValidationError):
        CompareRequest(investigationIds=ids, fake=True)


@pytest.mark.parametrize("value", ["0", "-1.25", "0.10000000000000000001"])
def test_decimal_string_preserves_original(value):
    from pydantic import TypeAdapter

    assert TypeAdapter(DecimalString).validate_python(value) == value
    assert str(Decimal(value)) == value


@pytest.mark.parametrize("value", ["NaN", "Infinity", 0.1, "1e9"])
def test_decimal_string_rejects_lossy_or_nonfinite(value):
    from pydantic import TypeAdapter

    with pytest.raises(ValidationError):
        TypeAdapter(DecimalString).validate_python(value)


def test_query_bounds_and_extras():
    assert CatalogQuery().limit == 20
    for data in [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"fake": 1}]:
        with pytest.raises(ValidationError):
            CatalogQuery(**data)
