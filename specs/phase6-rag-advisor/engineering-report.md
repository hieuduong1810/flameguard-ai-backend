# Phase 6 engineering report

Verified 2026-11-13 on `feat/phase6-rag-advisor` after owner approval.
Backend/mock engineering is complete for the approved scope.

## Delivered API

- POST `/api/v1/chat/sessions`
- GET `/api/v1/chat/sessions/{identity}`
- GET `/api/v1/chat/sessions/{identity}/messages`
- POST `/api/v1/chat/sessions/{identity}/messages`
- POST `/api/v1/advisor/assessments`

Chat supports public-demo session lifetime, stable paged history, atomic
user/assistant/citation persistence, concurrent commits, legacy plain-text
history, explicit outcomes and original citation validation. Provider calls
receive detached bounded context and run outside writer transactions. Advisor
invokes its provider per pillar using Phase 5 evidence and returns gaps/context.
Default providers are unavailable. Fixed mock output is synthetic/unreviewed.

## T062 architecture

ADR-0004 records the approved same-database scientific/runtime boundary. The
SELECT-only reader and INSERT-only chat writer use separate engines. V2 admission
excludes exactly the three chat tables with empty runtime manifest arrays.
Exact validation covers the remaining 18 tables. V1 retains all-table validation.
Existing source/investigation FKs remain effective. Runtime validation checks
same configured endpoint/database OID and effective role/table privileges.

The chat portion of T062 is resolved. Wider scenario-history writer activation
remains separately scoped. No ORM model or Alembic revision changed.

## Files

New implementation lives in `app/core/runtime.py`, `app/repositories/chat.py`,
`app/services/chat.py`, `app/integrations/chat.py`, `app/schemas/api/chat.py` and
`app/api/v1/endpoints/chat.py`. Existing settings, application lifespan, router,
collection repository and collection service integrate the runtime boundary.

New tests live in `tests/unit/test_phase6_providers.py`,
`tests/contract/test_phase6_contract.py` and `tests/integration/test_phase6.py`.
This feature folder contains specification, approval, plan, task ledger,
contracts, generated OpenAPI, operations, verification and handoff.
Documentation changes also include ADR-0004, project status/documentation map
and a scoped update to the Phase 5 T062 handoff.

## Executed verification

| Check | Result |
| --- | --- |
| `poetry check` | Exit 0 |
| `poetry run ruff check .` | Exit 0 |
| `poetry run ruff format --check .` | Exit 0 |
| `poetry run pytest -q --tb=short` | 566 passed, zero failures/skips, 103.60 seconds |
| `poetry run pytest -q -m integration --tb=short` | 207 passed, zero failures/skips, 359 deselected, 94.77 seconds |
| Final focused Phase 6 tests after cache-header correction | 15 passed, zero failures/skips, 8.43 seconds |

The PostgreSQL fixtures used approved loopback 5433 test-named targets and
generated retained databases/roles. Sandboxed pytest stopped responding, so
the executed checks used the approved process escalation. No additional Codex
CLI session or YAML workflow was used.

## Convergence and readiness

T001–T017 are complete. Focused convergence fixes and criterion mapping are in
[verification.md](verification.md). Engineering readiness covers transport,
orchestration, validation and persistence with mocked engines. External
integration readiness remains pending T018 AI/Data scientific evaluation and
T019 Frontend consumer acceptance. Real provider adapters require accepted
scientific corpus/review semantics before activation.

The access policy is public demo continuity for 24 hours. Stored rows remain
pending authorized operator cleanup. POST sends are non-idempotent. See
[operations](runtime-operations.md) for credentials/grants, admission configuration
and log redaction. Phase 5 external gates and Phase 4 T078 remain open.

## Focused Phase 6 audit follow-up

Completed T020–T023 in the existing single-conversation workflow. The internal
RAG request now includes bounded persisted history for the current session,
optional investigation UUID, current question, corpus/dataset versions,
collection fingerprint and currently allowed source references. History retains
chronological order, origin/review labels and an explicit truncation flag. Limits
are 12 messages, 2,000 characters per message and 12,000 total characters.

A trusted per-application provider factory or explicit ChatService injection
supports future adapters. Unavailable/mock defaults and scientific/citation
validation remain active for injected providers. No real AI adapter was added.

Advisor gaps now derive from Phase 5 pillar totals, current page contents,
pagination metadata, original reason codes and review labels. They distinguish
empty evidence, partial/paged evidence, unreviewed evidence, provider absence,
abstention and timeout. Fingerprint, dataset/identity versions and collection
context are checked against the Phase 5 evaluation before provider calls and
again before returning. Public OpenAPI paths, schemas and statuses were compared
with the approved snapshot and remain equal.

Changed implementation files for this follow-up are `app/integrations/chat.py`,
`app/repositories/chat.py`, `app/services/chat.py`, the focused helper
`app/services/advisor.py` and `app/api/v1/endpoints/chat.py`. Regression additions
are in `tests/unit/test_phase6_providers.py` and `tests/integration/test_phase6.py`.
Existing tasks, contracts, verification and this report record the handoff.

| Follow-up verification | Passed | Failed/errors | Skipped | Notes |
| --- | --- | --- | --- | --- |
| Initial focused invocation | 8 | 13 setup errors | 0 | Local Docker PostgreSQL stopped; no code assertions failed |
| Focused Phase 6 regression after service recovery | 21 | 0 | 0 | 8.85 seconds |
| `poetry check` | Exit 0 | 0 | 0 | All set |
| `poetry run ruff check .` | Exit 0 | 0 | 0 | All checks passed |
| `poetry run ruff format --check .` | Exit 0 | 0 | 0 | 236 files already formatted |
| `poetry run pytest -q --tb=short` | 572 | 0 | 0 | 73.71 seconds |
| `poetry run pytest -q -m integration --tb=short` | 210 | 0 | 0 | 362 deselected, 71.21 seconds |

PostgreSQL checks used the existing approved isolated loopback 5433 fixture
targets with fresh retained resources. Docker completed automatic recovery
before the successful runs. External T018 and T019 remain pending. Engineering
readiness includes these audit fixes. External scientific/consumer readiness
continues to require the owner evidence recorded in the original handoff.
