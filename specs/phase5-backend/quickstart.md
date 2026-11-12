# Phase 5 engineering quickstart

Use the fixture-backed request from [HTTP contract](contracts/http.md). Run `poetry run pytest -q tests/contract/test_phase5_api.py` for HTTPX/lifespan tests and `poetry run pytest -m integration -q tests/integration/test_phase5.py` for isolated PostgreSQL verification. The latter requires the approved local fixture targets described in the [testing runbook](../../docs/runbooks/testing-and-release.md).

Start with zero offsets and limit 1. Save the response's coverage, ranking or pillar nextRequest descriptor and replay the original scenario/pillar with that descriptor. Compare two complete traversals, check final-page scope and confirm changed scenario or snapshot causes 409. Inspect the runtime path, schemas and fixed error responses in [OpenAPI](contracts/openapi.json).

Unavailable providers are the default. Explicit fixture composition is documented in the implementation summary. Confirm TEST_ONLY labels, original association IDs and the absence of scientific conclusions. These checks exercise backend engineering.
