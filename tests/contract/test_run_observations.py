from uuid import uuid4

import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/runs/not-a-uuid/conditions",
        "/runs/" + str(uuid4()) + "/measurements?limit=101",
        "/investigations/" + str(uuid4()) + "/runs?offset=-1",
    ],
)
async def test_observation_request_validation(client, path):
    response = await client.get("/api/v1" + path)
    assert response.status_code == 422
    assert "items" not in response.json()
