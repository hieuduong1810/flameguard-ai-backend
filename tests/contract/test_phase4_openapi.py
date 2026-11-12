import json
from pathlib import Path

from app.core.config import Settings
from app.main import create_app

CONTRACT = (
    Path(__file__).resolve().parents[2] / "specs/001-phase4-catalog-apis/contracts/openapi.json"
)


def resolve(node, document):
    while "$ref" in node:
        node = document["components"]["schemas"][node["$ref"].split("/")[-1]]
    return node


def assert_schema(expected, actual, contract, runtime, seen=None):
    expected, actual = resolve(expected, contract), resolve(actual, runtime)
    seen = set() if seen is None else seen
    pair = (id(expected), id(actual))
    if pair in seen:
        return
    seen.add(pair)
    for key in [
        "type",
        "format",
        "enum",
        "const",
        "pattern",
        "minimum",
        "maximum",
        "minItems",
        "maxItems",
        "uniqueItems",
        "additionalProperties",
    ]:
        if key in expected and not isinstance(expected[key], dict):
            assert actual.get(key) == expected[key], (key, expected, actual)
    if "properties" in expected:
        assert set(actual["properties"]) == set(expected["properties"])
        assert set(actual.get("required", [])) == set(expected.get("required", []))
        for key, child in expected["properties"].items():
            assert_schema(child, actual["properties"][key], contract, runtime, seen)
    if "items" in expected:
        assert_schema(expected["items"], actual["items"], contract, runtime, seen)
    if "anyOf" in expected:
        assert len(expected["anyOf"]) == len(actual["anyOf"])
        for left, right in zip(expected["anyOf"], actual["anyOf"], strict=True):
            assert_schema(left, right, contract, runtime, seen)
    if isinstance(expected.get("additionalProperties"), dict):
        assert_schema(
            expected["additionalProperties"],
            actual["additionalProperties"],
            contract,
            runtime,
            seen,
        )


def test_all_runtime_contract_paths_and_output_schemas():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runtime = create_app(Settings(_env_file=None, debug=False)).openapi()
    for path, methods in contract["paths"].items():
        for method, expected in methods.items():
            actual = runtime["paths"]["/api/v1" + path][method]
            assert actual["operationId"] == expected["operationId"]
            actual_params = {p["name"]: p for p in actual.get("parameters", [])}
            assert set(actual_params) == {p["name"] for p in expected.get("parameters", [])}
            for param in expected.get("parameters", []):
                observed = actual_params[param["name"]]
                assert observed["in"] == param["in"] and observed["required"] == param["required"]
                observed_schema = observed["schema"]
                # An omitted optional URL query is represented as null in Pydantic's
                # model schema; URL-supplied values still have the declared string type.
                if param["in"] == "query" and not param["required"] and "anyOf" in observed_schema:
                    observed_schema = next(
                        x for x in observed_schema["anyOf"] if x.get("type") != "null"
                    )
                assert_schema(param["schema"], observed_schema, contract, runtime)
            for code, response in expected["responses"].items():
                assert_schema(
                    response["content"]["application/json"]["schema"],
                    actual["responses"][code]["content"]["application/json"]["schema"],
                    contract,
                    runtime,
                )
            if "requestBody" in expected:
                assert_schema(
                    expected["requestBody"]["content"]["application/json"]["schema"],
                    actual["requestBody"]["content"]["application/json"]["schema"],
                    contract,
                    runtime,
                )
    assert {"/api/v1/health", "/api/v1/ready"} <= set(runtime["paths"])


async def test_documented_error_example_is_real_http_response(client):
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected = contract["paths"]["/investigations"]["get"]["responses"]["422"]["content"][
        "application/json"
    ]["example"]
    response = await client.get("/api/v1/investigations?sort=confidence")
    assert response.status_code == 422
    assert response.json() == expected
