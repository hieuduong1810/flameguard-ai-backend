import pytest
from pydantic import ValidationError

from app.schemas.api.queries import CatalogQuery, SelectionQuery


@pytest.mark.parametrize(
    "values",
    [
        {"q": "x" * 257},
        {"purpose": "x" * 257},
        {"platform": "x" * 257},
        {"sort": "confidence"},
        {"facility": "CIR"},
    ],
)
def test_query_contract_rejects_unsupported_or_oversized(values):
    with pytest.raises(ValidationError):
        CatalogQuery(**values)


def test_summary_has_no_sort_or_page_contract():
    for values in [{"sort": "title-asc"}, {"offset": 0}, {"limit": 20}]:
        with pytest.raises(ValidationError):
            SelectionQuery(**values)
