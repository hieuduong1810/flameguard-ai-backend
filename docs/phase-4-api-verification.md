# Phase 4 API implementation and verification

Updated: 2026-11-12. Scope: approved Phase 4 backend and executable convergence remediation, no scientific validation or frontend rollout. Exact commands/results and task traceability are in [the execution record](../specs/001-phase4-catalog-apis/verification.md).

## Implemented surface

All paths below are under /api/v1. Existing /health and /ready remain compatible.

| Method | Path |
| --- | --- |
| GET | /catalog/capabilities |
| GET | /investigations |
| GET | /investigations/by-slug/{slug} |
| GET | /investigations/{investigationId} |
| GET | /investigations/{investigationId}/tags |
| GET | /investigations/{investigationId}/runs |
| GET | /runs/{runId}/conditions |
| GET | /runs/{runId}/measurements |
| GET | /investigations/{investigationId}/measurements |
| GET | /investigations/{investigationId}/sources |
| GET | /investigations/{investigationId}/claims |
| GET | /claims/{claimId}/sources |
| GET | /dashboard/summary |
| POST | /compare |

Router/service/repository boundaries, explicit loading, same-run filtering, stable pages/counts and read-only repeatable-read transactions are exercised against PostgreSQL. Public camelCase DTOs are separate from unchanged persistence schemas. UUID, PSI ID, slug and original document/association identities remain distinct. Exact Decimal strings, zero/null, uncertainty, raw units and all source locators survive projection.

Claim previews and their next links retain every association, including repeated documents and cross-study/mismatched run context. Comparisons show labeled original observations, not pooled averages, scores, deltas, risk or safety conclusions. Verified counts remain unavailable.

## Synthetic operations

scripts/seed_demo_data.py requires explicit opt-in, independent exact-target authorization, dedicated credentials, restricted role and the unchanged approved schema. It inserts only into exclusive disposable targets, locks/rechecks all 21 tables, treats identical data as a no-op and refuses conflicts without overwrite. CLI/seed tests cover concurrency, lock timeout, valid subsets, forced rollback and foreign rows across every approved table.

Real PostgreSQL tests use newly generated test-named databases and separate owner/read roles on the existing Docker test server at loopback port 5433. Existing development/research databases were not seeded, migrated, reset or dropped. Generated test databases/roles are deliberately retained; cleanup is not authorized or performed.

## Preservation and limitations

Protected-file hashes confirm no change to app/models/, existing Alembic revisions, original diagram HTML, README or stable implementation plan. Frontend repository remains unchanged. No ETL, RAG, predictive/scenario algorithm, deployment, commit, push or merge was performed.

Executable admission supports exact synthetic collections, bound empty real/unknown collections, and exact owner-declared non-curated stored-field snapshots. Origin and review remain independent; missing labels stay unknown. All 21 tables are checked using server-side batches of at most 64 rows. Recognized demo content in non-synthetic snapshots, drift and mixed rows refuse admission. This read adapter performs no ETL and does not approve real/curated scientific publication; Data acceptance remains pending.

The remediated wire boundary rejects undeclared snake_case inputs and coerced JSON integers before domain dependencies; normal URL integers and internal DTO construction are preserved. Tag previews match UUID-ordered direct pages. Comparison caveats explicitly describe examined-page label differences, missing/unexamined context and partial scope without pooling, conversion or derived outcomes.

The preceding remediation run passed 392 tests, including 178 PostgreSQL integration tests, in 60.82 seconds. Its earlier focused PostgreSQL pass was 15 passed. Initial connection failures in that run were Docker/PostgreSQL startup issues, resolved before its final full pass.

The Phase 10 implementation completes T083-T084. UUID uniqueness now uses parsed canonical identities across all 21 tables before repository SQL or dictionary indexing. Regressions cover upper-case, unhyphenated, braced and URN spellings, conflicting and identical duplicates, valid single-instance identities, seed refusal before write statements and read-admission refusal. Comparison label warnings now check actual cross-study sets and observable/unit associations. Matching heterogeneous pages and reordered entries retain unknown scientific comparability, while swapped units and actual differences remain explicit.

Latest checks on 2026-11-12 passed `poetry check`, `poetry run ruff check .` and `poetry run ruff format --check .` (168 Python files). Full pytest **441 passed, 0 failed/errors/skipped**, including **185 PostgreSQL integration tests**, in 69.53 seconds. Focused unit/HTTP checks passed 60 tests, followed by four additional valid-UUID spelling cases included in the full suite. Focused PostgreSQL remediation checks passed 8 tests.

All executable tasks through T084 are complete. T078 remains blocked for actual Frontend acceptance evidence. Full telemetry, verified-run policy and scientific derived comparison remain unavailable. A fresh user-invoked Converge review remains pending.
