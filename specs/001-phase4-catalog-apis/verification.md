# Phase 4 execution and verification record

Current update: **2026-11-12**. All executable tasks through T084 are implemented and verified with 441 passing tests. T078 remains blocked for actual Frontend acceptance. The latest Phase 10 execution record below supplies current results. Earlier sections retain their implementation/review history and test counts. A fresh user-invoked Converge remains the next review step.

## Historical implementation run

Date: 2026-11-11. Status: executable backend implementation verified with synthetic data; consumer/scientific acceptance remains pending. Converge was not started.

## Scope and task status

- T001–T073: completed within the approved backend/synthetic scope; task markers and actual artifact paths are recorded in tasks.md.
- T074: **BLOCKED by explicit user instruction** not to automatically start Converge. No convergence command, completion waiver or invented owner sign-off was performed.
- Frontend adapter/browser acceptance, Data curated delivery/status/unit/verification acceptance and real-data publication remain external pending gates. Handoff tasks create accurate packets, not team approvals or ETL.

## Executed checks

| Check | Result |
| --- | --- |
| poetry check | Passed, exit 0 |
| poetry run ruff check . | Passed, exit 0 |
| poetry run ruff format --check . | Passed, 166 Python files formatted |
| poetry run pytest -q (full suite, explicit test environment) | 371 passed, 0 failed, 0 skipped; 47.70 seconds |
| Integration marker collection | 172 of 371 tests are integration tests; all executed in the full pass |
| Generated runtime OpenAPI vs proposed contract | All 14 Phase 4 operations and 30 canonical schemas checked recursively, including parameters, aliases, required/null fields, Decimal strings and documented errors |
| Live comparison and error examples | HTTP examples exercise seeded UUIDs and exact safe error response |
| Protected-file hash comparison | No changes in models, existing Alembic revisions, original diagram HTML, README or stable implementation plan |
| Git/secret/link scope audit | Recorded after final documentation review; no staging, commit, push, merge or frontend edits |

The full test command was launched through `poetry run python .tools/run_phase4_checks.py -q --tb=short --junitxml=.tools/phase4-full.xml`. That ignored local wrapper obtains existing Docker test credentials in memory, sets TEST_DATABASE_URL/PHASE4_ADMIN_URL and DEBUG=false only for the child process, then executes `poetry run pytest -q` with the listed reporting options and a unique writable --basetemp. Credentials are not printed or versioned. JUnit is ignored local evidence, not a dependency of application code.

Early tests demonstrated the expected missing DTO module before implementation. Later failures exposed missing malformed-URL handling, generic UUID metadata rendering, a test's incomplete comparison context and Windows sandbox temp restrictions; these were corrected and failed checks rerun. The final full suite has no failing or skipped tests. The last test-only async file-read lint correction is additionally checked with its targeted integration tests.

## Database execution and preservation

Tests use existing Docker PostgreSQL on 127.0.0.1:5433 only as an administrative test server. Existing fixtures generate fresh test-named databases for Phase 2 regression. Phase 4 fixtures generate fresh flameguard_test_phase4_<random> databases and dedicated non-superuser owner/SELECT-only roles. Only the existing migrations are applied in those new targets. The seed CLI itself cannot migrate/create/drop a DB or grant roles.

Local development PostgreSQL at port 5432 and all existing scientific/development databases were not seeded, migrated, reset or dropped. Created test databases/roles are retained for inspection under the existing runbook; automatic cleanup is not performed. Private target authorization/config files remain under ignored .tools/.

Seed checks cover exact schema/head, PK/FK/unique/index/null/type preservation, explicit opt-in and independently pinned target/role/OID/ownership/grants, regular-target denial, first run, identical/concurrent no-op, valid subset completion, bounded lock refusal, altered/scientific sentinel preservation, unrelated rows in every one of the 21 tables and whole-transaction rollback after injected failure. All inserts are TEST_ONLY; no real findings/citations are created.

## Acceptance traceability

| Criteria | Executed evidence |
| --- | --- |
| FR-001, FR-005, FR-028, FR-030 | tests/integration/test_phase4_http_journeys.py; tests/contract/test_phase4_openapi.py; per-surface contract tests; review-record.md |
| FR-002–004, FR-013 | tests/unit/test_slug_manifest.py; tests/contract/test_investigation_detail.py; real UUID/slug detail and bounded tag traversal |
| FR-006–009 | tests/integration/test_catalog_queries.py; filter/page/literal wildcard cases; 105-investigation and 25-tag traversal; query DTO limits |
| FR-010–012 | tests/unit/test_dashboard_rules.py; tests/integration/test_dashboard_queries.py; real HTTP distinct counts, unknown verification and independently empty collection |
| FR-014–016 | tests/integration/test_run_queries.py; real HTTP conditions/observations; exact high-precision Decimal, zero/null/uncertainty, original string gravity and raw references |
| FR-017–020 | tests/integration/test_evidence_queries.py; repeated/shared/orphan/mismatched provenance cases; all 105 associations traversed without loss |
| FR-021–023 | tests/unit/test_comparison_rules.py; tests/contract/test_comparison.py; tests/integration/test_comparison_queries.py; 2–3 selection/order/context and blocked derivations |
| FR-024–027 | tests/unit/test_demo_manifest.py; tests/unit/test_demo_seed_guards.py; tests/integration/test_demo_seed.py; tests/integration/test_demo_api_roundtrip.py |
| FR-029 | Existing regression suite; unchanged protected hashes/schema; no other repository changed |
| SC-001 | All six journeys run with synthetic fixtures; independent empty and large collections; default demo CLI roundtrip |
| SC-002 | Exact fixture membership/counts, deterministic traversal, same-run predicates and filtered summary reconciliation |
| SC-003 | Every eligible association ID/locator/context survives all pages; shared claim remains one claim |
| SC-004 | Synthetic labels on detachable entities, empty/aggregate responses; read admission rejects drift, real/curated publication stays gated |
| SC-005 | Original Decimal strings, zero/null, units and uncertainty retained through real PostgreSQL/API/comparison |
| SC-006 | Ordered valid 2/3 selections, whole-request failures and explicit unavailable scientific deltas/highlights |
| SC-007 | Unsupported controls and unknown verification are explicit; no fallback verified counts or generated scientific scores |
| SC-008 | Backend owner-approved examples are tested and handed off; Frontend consumer acceptance remains PENDING and is not represented as completed rollout |

Snapshot tests prove REPEATABLE READ READ ONLY before the first query, consistent pre-mutation results and refusal on the next drifted read. Query-count tests keep list/tag previews and association retrieval bounded independently of page items/claim count. New operations produce no HTTP-triggered writes.

## Implementation organization and contract reconciliation

Public Pydantic definitions are centralized in app/schemas/api/models.py with domain re-export modules for consistent recursive schemas. Existing CatalogRepository/EvidenceRepository remain unchanged in behavior and export separate read repositories implemented in phase4_catalog.py/phase4_evidence.py. This avoids breaking old eager-loading methods while adding bounded public reads; it is not a new architectural layer.

The initial OpenAPI slug regex implied 422 for noncanonical input, while the higher-priority spec/read model requires a lookup 404. The formal contract now describes canonical spelling without imposing that request regex. Optional URL query schemas use generated null branches to represent omission; supplied values retain the declared bounds. Request/error examples now use the actual deterministic synthetic UUIDs and pre-admission unknown error context. These reconciliations are documented in analysis.md; no scientific or schema requirement is relaxed.

Coverage ratio is a generated catalog linkage ratio with 28-digit decimal arithmetic; numerator/denominator are exposed. It is not an original scientific observation or verification metric. Original observation decimals are never rounded to that precision.

## Remaining gates and next action

Only exact synthetic manifest admission is currently enabled. Real/curated Data adapter/publication, approved scientific unit/status/verification rules, full telemetry and Frontend consumer acceptance are pending. Unknown/unavailable behavior is implemented instead of fabricating these deliverables. No scenario matching, ETL, RAG, prediction or deployment was implemented.

Ready for a separately requested speckit-converge review of this bounded backend delivery, with the pending external gates visible. T074 remains unexecuted. No commit, push, merge or deploy was performed.

## Final audit

Final scope audit passed: 73 checked tasks and T074 alone blocked; no protected-file hash changes, broken local Markdown links or high-confidence token/private-key pattern matches. .env, local authorization, runner and JUnit artifacts remain ignored. Staging area is empty; Frontend status is unchanged. The targeted comparison integration recheck after the test-only async file-read lint correction passed 2 tests. See [changed-files.md](changed-files.md) for the full implementation inventory. Pattern scanning is not an exhaustive secret guarantee.

## Convergence remediation execution — 2026-11-12

The user explicitly authorized all executable tasks appended by convergence. The 16-item requirements checklist remains fully checked and unmodified. No extension hook file exists before or after implementation. The frozen schema, existing layers and public response fields remain intact; no new dependency, ETL, scientific algorithm or cross-team implementation is required.

| Finding/task | Implementation and executed evidence |
| --- | --- |
| F1 / T075, FR-027, US6/AC2, SC-004 | `collection.py` and read-only `snapshot_rows` preserve declared real/unknown origin independently of unreviewed/unknown review. Missing labels stay unknown. No snapshot means all 21 tables must be empty. A non-curated snapshot pins exact already stored fields; no import or fallback occurs. `test_collection_context.py` covers unknown/raw status and recognized synthetic refusal. `test_demo_api_roundtrip.py` executes HTTP on fresh empty real/unknown/missing-origin databases, rejects inserted synthetic mixing, preserves unknown source status/null DOI through stored-field reads and refuses curated declaration. |
| F2 / T076, FR-028/030, SC-007 | Route-local public alias checks and strict JSON body validation reject snake_case and boolean/string/float integers before domain dependencies. Internal Python constructors and URL integers are preserved. `test_comparison.py` and `test_investigation_list.py` prove safe rejection before overridden dependencies; PostgreSQL journeys and `test_phase4_openapi.py` retain canonical success/schema equivalence. |
| F3 / T077, FR-022/023, SC-005/006 | Existing comparison context.caveats describes original observable/unit/run-label differences, unmatched page labels, missing values/run metadata, missing or unexamined conditions and partial/unexamined pages. Scope is only returned observations; equal labels never establish comparability. Unit tests and real HTTP/PostgreSQL comparison tests preserve original observation pages and null deltas/highlights. No response schema extension or scientific normalization occurs. |
| F4 / T078, SC-008 | **BLOCKED**: no actual Frontend reviewer/date/accepted scope was supplied. Handoff/review record states required evidence and pending gate. Backend tests cannot substitute for consumer acceptance. No messages, frontend edits or fabricated approval. |
| F5 / T079, FR-009, SC-002 | Tag preview outer SELECT explicitly orders parent/tag UUID. Real repository and shuffled reverse-UUID insertion HTTP tests compare preview with direct page, traverse 25 tags and assert ordered unique loss-free membership. Existing bounded query-count checks remain passing. |
| F6 / T080, plan loading, SC-002/004 | Server-side streaming partitions at most 64 database rows per batch, exact content/identity checks across all 21 tables, early conflict and cursor close on failure. A 257-investigation/257-association PostgreSQL test records bounded batches and exactly 21 admission SELECTs, then proves foreign-row refusal. Snapshot/read-only/drift, precision, provenance and seed safety regressions all execute. The manifest itself remains an in-memory owner-managed allowlist; this change bounds additional database row materialization. |
| F7 / T081, SC-001–008 | Fresh full verification below plus current phase/status/handoff records. SC-008 remains pending actual Frontend acceptance; Data scientific gates are not waived. |
| F8 / T082 | Explicit UTF-8 repair of corrupted dash/arrow/range separators. All 82 task IDs/order/meaning were preserved, then completion markers were updated from actual evidence. Local Markdown targets and task counts checked; no mojibake sequences remain. |

### Fresh check results

| Command/check | Actual result |
| --- | --- |
| `poetry check` | Passed, exit 0 |
| `poetry run ruff check .` | Passed, exit 0 |
| `poetry run ruff format --check .` | Passed; 168 files already formatted |
| Focused unit/HTTP remediation tests | 26 passed after fixes |
| `poetry run pytest tests/unit tests/contract -q` with isolated writable basetemp | 88 passed, 0 failed/skipped, 1.78 seconds |
| Focused PostgreSQL catalog/comparison/admission/roundtrip modules | 15 passed, 0 failed/skipped, 16.17 seconds, before adding the final stored-field HTTP case |
| Full `poetry run pytest -q`, explicit isolated PostgreSQL environment | **392 passed, 0 failed/errors/skipped, 60.82 seconds** |
| Full-run JUnit classification | **178 integration tests and 214 other tests**, all executed |
| Protected baseline hashes | No mismatches: models, three existing migration revisions, diagram HTML, README and stable plan unchanged |

The full command was `poetry run python .tools/run_phase4_checks.py -q --tb=short --junitxml=.tools/phase4-remediation-full.xml`; the same private wrapper described above supplies credentials only in process memory and invokes Poetry pytest with a unique writable basetemp. Local evidence and target authorization remain ignored. Initial focused execution found the missing comparison explanations and a regression in unsupported-filter error codes; both were fixed. Docker was initially stopped, then PostgreSQL was still starting; after `pg_isready` reported accepting connections, targeted and full database tests passed. These startup failures are not hidden skipped tests or remaining implementation failures.

Only newly generated test databases/roles on the existing localhost:5433 PostgreSQL server were provisioned/migrated/written. They are retained. Existing development/research data and local port 5432 were not mutated. No schema/model/migration, frontend, commit, push, merge or deployment changes occurred.

Current ledger: 81 checked of 82; T078 is the only blocked task. T074 records the earlier user-invoked convergence assessment that appended these tasks. This Implement pass did not automatically run Converge and does not assert whole-phase convergence. Next action: separately invoke `$speckit-converge` with the external Frontend/Data acceptance gates visible.

## Phase 10 execution — 2026-11-12

The user authorized all remaining executable convergence tasks. The requirements checklist has 16 checked items and zero unchecked items. T083-T084 follow the approved schema, identity, provenance and comparison contracts. The existing public caveat list accommodates the correction. T078 remains blocked for actual Frontend reviewer/date/scope evidence. No extension hook file exists before or after this execution.

### T083 canonical identity acceptance

`unique_rows_by_id` checks parsed UUID identity before returning any UUID-keyed dictionary. The fixture/snapshot parser invokes it after column conversion. Repository admission validates all table identity indexes before its first SQL query. Duplicate spellings therefore cannot silently replace a row or distort inserted/already-present counts.

- `tests/unit/test_demo_manifest.py` rejects identical and conflicting duplicates spelled in upper case, hex without hyphens, braces and URN form. Controls accept each spelling for one claim and preserve its FK references. Repository rejection is parameterized across all 21 approved tables and asserts zero SQL calls.
- `tests/unit/test_collection_context.py` exercises canonical duplicate refusal in unknown-origin snapshots and preserves a valid single uppercase UUID.
- `tests/integration/test_demo_seed.py` checks identical/conflicting canonical duplicates against new empty and already seeded isolated databases. SQL instrumentation proves refusal before INSERT/UPDATE/DELETE. Exact all-table inspection proves the prior contents survive, and failure returns no misleading success counts.
- `tests/integration/test_demo_api_roundtrip.py` verifies safe HTTP refusal for synthetic association duplicates and unknown snapshot source duplicates. The ordinary unknown snapshot read succeeds before the invalid duplicate is added.

### T084 comparison explanation acceptance

Cross-page observable and run-metadata warnings now use actual set differences. Unit warnings also compare original observable-to-unit associations, which detects a unit swap even when both pages contain the same overall set of units. Equal label sets retain comparability=not_established. Missing values, missing/unexamined context, unmatched labels and partial-page caveats remain explicit.

- `tests/unit/test_comparison_rules.py` covers matching heterogeneous pages, reversed order, swapped units, actual observable/run-label differences and null values. Earlier missing-context/partial-page regressions remain passing.
- `tests/contract/test_comparison.py` exercises the real comparison service through HTTP with controlled repository projections, retaining ordered identities and null derived outcomes for matching and swapped-unit pages.
- `tests/integration/test_comparison_queries.py` exercises actual PostgreSQL and admitted HTTP projections for matching heterogeneous metadata and swapped observable/unit associations. Original measured values, uncertainty, units, run IDs and page totals are checked against the synthetic manifest.

### Executed verification

| Check | Result |
| --- | --- |
| Initial new unit regressions before fixes | Reproduced the canonical-UUID and false-mismatch findings, 34 failed / 15 passed |
| Focused unit/HTTP regressions after fixes | 60 passed, followed by 4 valid-UUID spelling controls included in the final full run |
| Focused real PostgreSQL remediation tests | 8 passed, 0 failed/skipped, 14.75 seconds |
| `poetry check` | Passed, exit 0 |
| `poetry run ruff check .` | Passed, exit 0 |
| `poetry run ruff format --check .` | Passed, 168 files formatted |
| Full pytest with actual isolated PostgreSQL | **441 passed, 0 failed/errors/skipped, 69.53 seconds** |
| Full-run JUnit evidence | **185 integration tests and 256 other tests**, all executed |
| Protected baseline hashes | All match for models, existing migrations, original diagram, README and stable implementation plan |

The full command was `poetry run python .tools/run_phase4_checks.py -q --tb=short --junitxml=.tools/phase10-full.xml`. The focused database command selected the four parametrized canonical-seed cases, unknown snapshot roundtrip, synthetic duplicate admission and two matching/swapped-unit comparison cases, using the same wrapper and `.tools/phase10-targeted.xml`. Docker/PostgreSQL readiness succeeded before database execution. As in the earlier runs, the wrapper invokes Poetry pytest with private in-memory credentials and a unique writable temporary directory.

All database provisioning, migrations and writes targeted newly generated isolated test databases on localhost:5433. The fixtures retain those databases and roles. Local target files and reports remain under ignored paths. Scientific curated publication, Frontend consumer acceptance and deferred telemetry retain their recorded gates.

### Files changed in this implementation pass

- Application changes cover `app/services/demo_manifest.py`, `app/repositories/collection.py` and `app/services/comparison.py`.
- Test changes cover `tests/unit/test_demo_manifest.py`, `tests/unit/test_collection_context.py`, `tests/unit/test_comparison_rules.py`, `tests/fixtures/phase4.py`, `tests/contract/test_comparison.py`, `tests/integration/test_demo_seed.py`, `tests/integration/test_demo_api_roundtrip.py` and `tests/integration/test_comparison_queries.py`.
- Delivery records cover `specs/001-phase4-catalog-apis/tasks.md`, this verification record, `docs/phase-4-api-verification.md` and `docs/project-status.md`.

Current ledger has **83 of 84 tasks checked**. T083-T084 are complete. T078 is the remaining blocked task. The next review step is a user-invoked `$speckit-converge` assessment.
