import pytest


@pytest.mark.parametrize("query", ["limit=20", "offset=0", "sort=title-asc", "facility=CIR"])
async def test_summary_rejects_unsupported_scope_options(client, query):
    response = await client.get("/api/v1/dashboard/summary?" + query)
    assert response.status_code == 422
