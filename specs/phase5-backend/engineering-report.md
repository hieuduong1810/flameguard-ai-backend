# Phase 5 engineering report

**Outcome**: Backend engineering complete for the authorized P5-01–P5-06 mock scope. Real-data, scientific and Frontend acceptance remain open.

## Delivered endpoint and behavior

`POST /api/v1/mission/scenarios/evaluate` accepts an explicit scenario with exact decimal strings and units, optional context and independent pagination. It returns interpreted input, collection/review scope, six-dimensional run coverage, validated rankings and classified pillar evidence. Tests show that one complete fixture run supports all five conditions and that split runs remain partial. The fixture ranking preserves two supplied tied ranks. Four original source associations across three documents remain reachable, including a repeated document, a null run and a context mismatch.

Providers default to unavailable. Trusted server configuration can enable the deterministic TEST_ONLY adapters for admitted synthetic/unreviewed collections. Positive fixture coverage is exact equality under declared test labels. Rankings are pre-authored fixture deliveries. Classification uses explicit original association mappings. Data retains ownership of real ranking computation, scientific policy and review.

The evaluation API uses one PostgreSQL read-only repeatable snapshot and releases the connection before provider work. Replay binds exact stored and manifest originals, scenario interpretation, collection identity and relevant provider content. The trusted persistence service serializes the complete compatible subset into existing columns with exact round-trip verification. Runtime scenario history is pending a writer/lifecycle compatible with exact catalog admission.

## Changed files

| Area | Files |
| --- | --- |
| HTTP and wiring | app/api/phase5_route.py, app/api/v1/endpoints/scenarios.py, app/api/v1/router.py, app/api/dependencies.py, app/core/config.py |
| DTOs, providers and repositories | app/schemas/api/scenarios.py, app/integrations/scenario_evidence/, app/repositories/phase5_scenarios.py, app/repositories/scenarios.py, app/repositories/collection.py |
| Services | app/services/scenarios.py, app/services/scenario_interpretation.py, app/services/scenario_traversal.py, app/services/scenario_rankings.py, app/services/scenario_pillars.py, app/services/scenario_persistence.py, app/services/collection.py |
| Tests | tests/fixtures/phase5.py, tests/unit/test_phase5_scenario.py, tests/unit/test_phase5_providers.py, tests/contract/test_phase5_api.py, tests/integration/phase5_fixtures.py, tests/integration/test_phase5.py, tests/integration/conftest.py |
| Contracts and delivery | specs/phase5-backend/, docs/phase-5-scenario-evidence-verification.md, docs/project-status.md |

## Verification and task disposition

The configured YAML run `e9cf56f8` completed Specify, Plan, Tasks and Analyze.
Its reconciliation prompt exceeded the engine's 300-second timeout on resume.
Execution continued through a direct Codex CLI invocation using these feature
artifacts and the owner's full Phase 5 authorization. Three convergence reviews
were completed through that invocation. The saved YAML run remains failed at
`reconcile`. Its engine status must be distinguished from the verified engineering
result below. Local execution output is retained in
`.tools/phase5-execution.log`.

| Command | Exit | Pass / fail / skip |
| --- | --- | --- |
| `poetry check` | 0 | All set |
| `poetry run ruff check .` | 0 | All checks passed |
| `poetry run ruff format --check .` | 0 | 211 files already formatted |
| `poetry run pytest -q` | 0 | 551 passed, 0 failed, 0 skipped, 81.53 seconds |
| `poetry run pytest -m integration -q` | 0 | 197 passed, 0 failed, 0 skipped, 354 deselected, 76.20 seconds |

T001–T055 and T063–T068 are complete. T056–T060 and T062 remain blocked. T061 is deferred. Phase 4 T078 remains open. See [criterion-to-test evidence](verification.md), [owner and acceptance dependencies](handoff.md) and [runtime OpenAPI](contracts/openapi.json).

The integration runs used both authorized local PostgreSQL fixture paths. Existing revisions were applied only to freshly generated fixture databases, with databases/roles retained for inspection. Phase 5 introduces no model or migration change. The public evaluation makes no database writes. Trusted scenario persistence ran in an isolated fixture transaction.
