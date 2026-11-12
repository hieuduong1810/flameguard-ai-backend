import pytest


@pytest.mark.parametrize("query", ["fuel=solid", "facility=CIR", "gravity=0g", "sort=confidence"])
async def test_unmapped_controls_are_explicit(client, query):
    response = await client.get("/api/v1/investigations?" + query)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNSUPPORTED_CAPABILITY"


async def test_repeated_query_not_silently_selected(client):
    response = await client.get("/api/v1/investigations?q=one&q=two")
    assert response.status_code == 422


@pytest.mark.parametrize("key", ["gravity_raw", "source_type", "evidence_status", "review_status"])
async def test_snake_case_query_rejected_before_dependency(client, application, key):
    from app.api.dependencies import get_catalog

    def forbidden():
        pytest.fail("Invalid wire query reached the domain dependency")

    application.dependency_overrides[get_catalog] = forbidden
    response = await client.get(f"/api/v1/investigations?{key}=x")
    assert response.status_code == 422
