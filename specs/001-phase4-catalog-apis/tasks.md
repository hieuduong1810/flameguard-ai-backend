# Tasks: Phase 4 Catalog and Evidence APIs

**Created**: 2026-11-11
**Status**: All executable Phase 4 tasks through T084 completed and verified on 2026-11-12. T078 remains BLOCKED pending actual Frontend acceptance evidence. A fresh Converge assessment is the next review step.
**Input**: [Specification](spec.md), [plan](plan.md), [research](research.md), [read model](data-model.md), [API](contracts/api.md), [OpenAPI](contracts/openapi.json), [seed safety](contracts/seed-demo.md), [handoffs](contracts/team-handoffs.md) and [validation guide](quickstart.md).

## Scope, format and execution gates

The eight groups follow the user's requested organization. Their numbering is local to this Phase 4 backlog; it does not replay completed project Phases 1–2. Story labels retain the specification: US1 discovery; US2 detail/runs/observations; US3 provenance; US4 dashboard; US5 comparison; US6 synthetic development.

Each task uses `- [ ] Tnnn [P?] [USn?] description with exact file paths`. Paths are repository-relative proposed future files, not proof those files exist. `[P]` permits work on different files only after its prerequisites pass; it is not authorization to spawn agents. Shared router/repository/service edits must be serialized.

Before executing behavior tasks: review this backlog, run the separate Analyze consistency step, resolve material findings, obtain applicable implementation authorization and accepted contract examples. Use a feature branch under normal workflow; this generation step stays on the current branch. Separate exact-target approval is required before PostgreSQL/seed writes. Pending Frontend/Data decisions must be recorded honestly, not invented to close a checkbox.

For every behavior task: write meaningful tests first and demonstrate the expected failure where feasible, then implement the smallest change, run relevant checks and record evidence. A task is complete only when its stated outcome and the group's applicable acceptance criteria have executed evidence. Written/skipped tests are not passing tests. A missing database environment blocks that verification, not independent pure work.

Preserve Router → Service → Repository → Database, Poetry, all 21 tables, migrations 0001–0003, existing persistence DTOs and health/ready. No ETL, ingestion pipeline, RAG, predictive algorithm, frontend edit, deployment or full telemetry implementation task is included. Do not modify README or the stable implementation plan as progress logs.

## Group 1 — API contracts and shared DTOs

**Goal**: Lock the proposed wire contract and establish testable public DTO, error and read-transaction boundaries. This is the shared foundation, not project initialization.
**Entry**: Analyze/implementation authorization gates above; current design artifacts available.
**Independent verification**: Pure DTO/validation tests and mocked read/error-boundary tests run without a database. Real transaction behavior is additionally checked in Group 7.

### Tests and acceptance baseline

- [x] T001 Reconcile the 14 operations/30 schemas in `specs/001-phase4-catalog-apis/contracts/openapi.json` with `specs/001-phase4-catalog-apis/contracts/api.md`; record reviewed examples, owner decisions and still-pending consumer gates in `specs/001-phase4-catalog-apis/contracts/review-record.md`. Done when each operation has success/empty/invalid/unavailable coverage and no incompatible decision is silently resolved.
- [x] T002 [P] Write DTO tests in `tests/unit/test_phase4_dtos.py` for exact camelCase aliases, required/null fields, UUID/PSI/slug separation, finite non-exponent Decimal strings, zero versus null, independent origin/review and nested detachable context; assert existing persistence DTO behavior remains unchanged. Depends on T001.
- [x] T003 [P] Write query/error/read-boundary tests in `tests/unit/test_phase4_queries.py`, `tests/unit/test_read_unit_of_work.py` and `tests/contract/test_phase4_errors.py`; cover extra/repeated query keys, bounds, safe 404/422/503/500 shapes, original health/ready behavior and transaction setup before the first query. Depends on T001.

### Shared implementation tasks

- [x] T004 Implement `app/schemas/api/common.py` and package exports in `app/schemas/api/__init__.py`: context, reason-coded unavailable fields, paged envelopes/links, safe errors and exact Decimal serialization; enforce the read-model constraint "Offset >=0, limit 1–100." and separate origin synthetic|real|unknown from reviewState unreviewed|curated|unknown. Depends on T002.
- [x] T005 Implement catalog/query DTOs in `app/schemas/api/catalog.py` and `app/schemas/api/queries.py`: investigation/detail/tag/capability models, default offset 0/limit 20, supported title-asc/runs-desc, maximum 256-character search/equality inputs, literal search and single values per key. Extra keys/unsupported controls fail explicitly. Depends on T003–T004.
- [x] T006 [P] Implement run/condition/measurement/observation DTOs in `app/schemas/api/runs.py` preserving the field rules "Original string gravity; external key not globally unique", "Both numeric/text may exist; no new exclusivity constraint" and "No source FK, origin, review flag or telemetry array" from `data-model.md`; nullable originals stay null and stored unit/status remain unchanged. Depends on T004.
- [x] T007 [P] Implement source/claim/association DTOs in `app/schemas/api/evidence.py`: optional DOI/version/excerpt/run, required locator, association UUIDs and paged sources; preserve "Distinct repeated links preserved; mismatch flagged, not silently erased" and add no direct claim-investigation/measurement-source relation. Depends on T004.
- [x] T008 [P] Implement summary/comparison DTOs in `app/schemas/api/dashboard.py` and `app/schemas/api/comparison.py`: at most three featured investigations, verifiedRunCount=null, null unavailable derivations, and request constraint "Compare accepts 2–3 distinct UUIDs and rejects the whole request on missing identity." Observation page limit is 1–100. Depends on T005–T006.
- [x] T009 Implement service-owned read unit of work in `app/services/unit_of_work.py` and integrate with `app/core/database.py` without replacing `get_db_session`; establish REPEATABLE READ READ ONLY before SQL, execute sequentially per AsyncSession and roll back/close reads. Mock tests must pass; real snapshot proof remains T062. Depends on T003.
- [x] T010 Implement the Phase 4 route-local error boundary in `app/api/phase4_route.py` and shared dependency wiring in `app/api/dependencies.py`; translate only safe errors without exposing DSNs/input/paths and preserve health/ready contracts. Run T002–T003 checks and record results in `specs/001-phase4-catalog-apis/verification.md`. Depends on T004–T009.

**Exit criteria**: DTOs match reviewed formal schemas, reject unsupported inputs, retain exact/null values and expose no new persistence fields; shared unit/contract checks pass. No business endpoint or real scientific verification is claimed by completing this group.

## Group 2 — Synthetic data generator and test fixtures (US6, P1)

**Goal**: Provide deterministic fixtures and a safe, explicit, insert-only `scripts/seed_demo_data.py` for independently authorized isolated databases.
**Entry**: Group 1; reviewed fixture/seed contract. Operator authorization is additionally required before any database execution.
**Independent verification**: Pure target/manifest checks plus CLI tests on approved disposable PostgreSQL: first run inserts expected rows, identical rerun inserts zero, and rejection leaves sentinel data unchanged.

### Tests first

- [x] T011 [P] [US6] Write `tests/unit/test_demo_seed_guards.py` for missing opt-in/env/URL/confirmation/file, production/staging/shared/default-dev refusal, endpoint/role/OID/grant mismatch, connection-option bypass and duplicate/invalid fixture identities. No live connection is needed for preflight denial cases. Depends on Group 1.
- [x] T012 [P] [US6] Write `tests/unit/test_collection_context.py` and `tests/unit/test_demo_manifest.py` for independent origin/review, manifest target binding, deterministic IDs/counts, stale membership, synthetic/real mixing, unknown origin and context on detached/empty projections. Depends on Group 1.
- [x] T013 [P] [US6] Write real seed tests in `tests/integration/test_demo_seed.py`: first run, exact no-op, valid subset completion, altered content/unique collision, unrelated rows across all 21 tables, invalid partial graph, lock contention/concurrent runs and injected rollback. Assert no scientific/sentinel row changes and no automatic migration/cleanup. Test execution waits for T015–T019 and explicit target approval.

### Generator, admission and seed implementation

- [x] T014 [US6] Define deterministic fixture generation in `tests/fixtures/phase4.py` and versioned `data/demo/phase4-v1.json`, `data/demo/slugs-v1.json`, `data/demo/collection.example.json`; include at least four synthetic investigations, exact expected counts, stable timestamps, repeated locators/shared/orphan claims, context mismatch, tied titles, empty children, mixed units and zero/null values. Add a separate larger deterministic pagination variant; no real DOI/NASA attribution. Depends on T011–T012.
- [x] T015 [US6] Add shared helpers in `tests/integration/phase4_fixtures.py` and scoped registration in `tests/integration/conftest.py`; reuse existing test-URL/provisioning safeguards, support committed fixtures plus independent read-only sessions, and produce target-specific test authorization outside Git only within separately approved integration runs. Preserve existing rollback fixtures and retain generated DBs. Depends on T014.
- [x] T016 [US6] Implement `app/repositories/demo_seed.py` with target/schema inspection, all-21-table exact-content checks, deterministic bounded advisory/table locks and FK-ordered plain inserts; no update/delete/upsert/commit or schema mutation. Empty or exact valid subset is admitted; conflicts abort. Depends on T013–T015.
- [x] T017 [US6] Implement `app/services/demo_seed.py`: dedicated DEMO_DATABASE_URL with no DATABASE_URL/.env fallback, explicit development/test environment, independent target authorization, exact endpoint/database/role/OID/owner/grant checks and 0003_could_have shape verification. Commit once after full validation; identical rerun is no-op. Depends on T011,T016.
- [x] T018 [US6] Add thin `scripts/seed_demo_data.py` exposing only the seed contract's opt-in/confirmation/authorization arguments; return safe codes and inserted/already-present counts, never secrets, reset/force/drop flags or startup hooks. It must not authorize its own target. Depends on T017.
- [x] T019 [US6] Implement collection admission/projection in `app/services/collection.py` with read-only inspection delegated to `app/repositories/collection.py`, explicit CATALOG_COLLECTION_MANIFEST settings in `app/core/config.py` and integration in `app/api/dependencies.py`; revalidate synthetic content within each read snapshot, reject drift/mixing with 503, cache only parsed manifests and never infer curated origin. Missing config leaves health/ready intact. Depends on T012,T014,T009–T010.
- [x] T020 [US6] Execute pure checks and, only on an approved target, `tests/integration/test_demo_seed.py`; verify concurrent/idempotent behavior, partial-failure rollback and unchanged schema/sentinels, recording commands/counts/refusals in `specs/001-phase4-catalog-apis/verification.md`. Missing approval/DB support remains blocked evidence, not a pass. Depends on T013–T019.
- [x] T021 [US6] Document fixture IDs/counts, synthetic statuses/example.invalid links, expected invalid cases and repeatability in `data/demo/README.md`; include no actual local target identity, authorization or credentials. Reconcile all generated variants with manifest tests. Depends on T014,T020.

**Exit criteria**: US6 fixture identities/counts are deterministic; every synthetic entity has origin context; opt-in and independent target checks fail closed; no-op/concurrency/atomicity are proven on a permitted target. The normal development database is never a seed destination and no NASA science is asserted.

## Group 3 — Investigation list/detail APIs (US1 and US2, P1)

**Entry**: Groups 1–2 and accepted catalog/identity examples. Pure/mock tests may be authored independently of live target availability.

### US1 — Discovery

- [x] T022 [P] [US1] Write `tests/contract/test_investigation_list.py` for capabilities/list shape, literal whitespace/case search, empty/no-match/past-end pages, unsupported controls, repeated/unknown keys, bounds, unavailable metadata and detached context. Depends on Groups 1–2.
- [x] T023 [P] [US1] Write `tests/integration/test_catalog_queries.py` for real SQL search escaping, same-run material/gravity matching, same-claim status matching, source/tag EXISTS, distinct totals, tied title/run-count ordering and multi-page traversal against expected fixture membership. Depends on Groups 1–2.
- [x] T024 [US1] Add reusable filtered-investigation-ID predicates in `app/repositories/catalog.py`; escape literal LIKE input, normalize exact text matching and combine run predicates in one EXISTS without duplicate joins. Preserve old Phase 2 methods. Depends on T023.
- [x] T025 [US1] Add count/page, grouped run-count sort and bulk bounded first-tag-page queries in `app/repositories/catalog.py`; use default title ascending/C collation plus UUID ties and identical count/page selection. No per-row counts or unbounded child loading. Depends on T024.
- [x] T026 [US1] Implement list/capability orchestration in `app/services/catalog.py`; use admitted read context, supported/unavailable field maps and correct empty/count/page semantics without mock fallbacks. Depends on T022,T025,T019.
- [x] T027 [US1] Register GET /catalog/capabilities and GET /investigations in `app/api/v1/endpoints/catalog.py` and `app/api/v1/router.py`; run US1 contract/SQL checks and record exact evidence in `specs/001-phase4-catalog-apis/verification.md`. Depends on T026.

**US1 independent acceptance**: A stable fixture catalog traverses every matching UUID once, correct totals remain independent of page size, no combined filter uses different runs, and unsupported mock controls return explicit 422 rather than altered semantics.

### US2 — Canonical detail and tags

- [x] T028 [P] [US2] Write `tests/contract/test_investigation_detail.py` for UUID/slug-equivalent identity, distinct psiId, null metadata, detail child links/counts, paged tags, known empty children, invalid UUID and unknown canonical ID/slug. Depends on Groups 1–2.
- [x] T029 [P] [US2] Write `tests/unit/test_slug_manifest.py` for lowercase canonical exact lookup, duplicate/conflicting entries, unknown/noncanonical slug, missing manifest, stale PSI mapping and no title-based generation; assert 404 versus safe 503 behavior. Depends on Groups 1–2.
- [x] T030 [US2] Add scalar detail/PSI lookup, child count and bounded tag traversal queries to `app/repositories/catalog.py`; compute claim counts through documents without loading children or depending on later evidence services. Depends on T025,T028.
- [x] T031 [US2] Add validated manifest resolution and detail projection to `app/services/catalog.py`; preserve UUID/PSI/slug separation, explicit unknown metadata and reviewed slug lifecycle; expose stale mapping as safe unavailable. Depends on T029–T030.
- [x] T032 [US2] Extend `app/api/v1/endpoints/catalog.py` with GET /investigations/by-slug/{slug}, GET /investigations/{investigationId} and GET /investigations/{investigationId}/tags; register static slug routing before UUID routing. Depends on T031.
- [x] T033 [US2] Execute list/detail/slug/tag unit, contract and approved PostgreSQL checks from T022–T032, documenting actual results and any blocked DB evidence in `specs/001-phase4-catalog-apis/verification.md`. Depends on T027,T032.

**US2 detail independent acceptance**: Both lookup methods return the same canonical identity; absent optional fields are unavailable/null; tag/child traversal is bounded; unknown parents differ from empty children and no fake rich display value is produced. Runs/observations are the separate continuation below.

## Group 4 — Runs, measurements, sources and claims APIs

**Entry**: Group 3 detail/identity and Groups 1–2 context. Run and evidence sub-slices can be verified independently using shared fixtures; serialize shared repository/router edits.

### US2 — Runs and original observations (P1)

- [x] T034 [P] [US2] Write `tests/contract/test_run_observations.py` for paged runs/conditions/measurements/investigation observations, external keys, string gravity, exact decimal/zero/null/uncertainty, raw asset limitations, parent 404/empty distinction and origin context. Depends on Group 3.
- [x] T035 [P] [US2] Write `tests/integration/test_run_queries.py` for actual Numeric/UUID/null round trips, numeric and textual conditions together, repeated external keys across investigations, bounded paging/loading and no invented measurement-source linkage. Depends on Group 3.
- [x] T036 [US2] Add parent checks and explicit page/count queries in `app/repositories/catalog.py` for runs, conditions, measurements and investigation-wide Measurement+Run rows; retain existing unbounded methods for compatibility, but do not call them for public pages. Depends on T035,T030.
- [x] T037 [US2] Add run/observation projection methods in `app/services/catalog.py`, preserving original units/values/uncertainty, unknown verification and discoverable condition pages; no numeric gravity conversion, fabricated boolean or telemetry array. Depends on T034,T036.
- [x] T038 [US2] Add `app/api/v1/endpoints/runs.py` and registrations in `app/api/v1/router.py` for the four run/observation collection operations in `contracts/openapi.json`; pass all queries through service/read-unit-of-work boundaries. Depends on T037.
- [x] T039 [US2] Execute US2 run/observation contract and approved SQL tests, including an independent empty parent and multi-page precision cases, recording results in `specs/001-phase4-catalog-apis/verification.md`. Depends on T038.

**US2 observations independent acceptance**: Every original field round-trips without null-to-zero or float loss, all pages are reachable, context remains attached and no raw reference becomes fabricated telemetry or scientific verification.

### US3 — Original sources and complete claim provenance (P1)

- [x] T040 [P] [US3] Write `tests/contract/test_source_claims.py` for source/claim/association pages, DOI/version/limitation/excerpt/run nulls, repeated locators, complete traversal, cross-study ownership/mismatch warnings, safe empty/404 errors and no fabricated bibliographic metadata. Depends on Group 3.
- [x] T041 [P] [US3] Write `tests/integration/test_evidence_queries.py` for distinct claim membership through source documents, shared claims, repeated document associations, optional run, context mismatch, orphan exclusion and association pages larger than 20/100; expected IDs/locators must match fixtures exactly. Depends on Group 3.
- [x] T042 [US3] Extend `app/repositories/evidence.py` with source page/count and distinct claim-ID membership/page queries; derive scope through SourceDocument.investigation_id and never an invented claim/run-owned investigation link. Depends on T041.
- [x] T043 [US3] Add bulk first association-page/window counts and canonical association traversal to `app/repositories/evidence.py`; retain every association UUID, source/run investigation context and exact locator/excerpt without per-claim queries or full-graph loads. Depends on T042.
- [x] T044 [US3] Implement `app/services/evidence.py` projection: source ownership, all active-collection cross-study associations, nullable metadata, explicit contextMismatch and warnings; mismatches/unlinked claims do not grant investigation membership or verification. Do not fetch URLs or invent measurement citations. Depends on T040,T043,T019.
- [x] T045 [US3] Add `app/api/v1/endpoints/evidence.py` and registrations in `app/api/v1/router.py` for investigation sources/claims and /claims/{claimId}/sources; ensure every association is reachable through next links and parent-not-found differs from known empty collections. Depends on T044.
- [x] T046 [US3] Execute US3 contract/approved PostgreSQL checks and reconcile every association ID/locator/ownership across all pages with expected fixtures; record counts and mismatch/orphan evidence in `specs/001-phase4-catalog-apis/verification.md`. Depends on T045.

**US3 independent acceptance**: No source association is lost or collapsed; shared claims count once, original ownership remains explicit, unlinked claims are not assigned by inference, and missing metadata/review never becomes invented findings.

## Group 5 — Dashboard summary API (US4, P2)

**Entry**: Groups 3–4 selection and source/claim semantics; counts contract accepted.
**Independent verification**: Compare summary against the fixture's expected selected investigation/run/document/distinct-claim sets, including empty selection, shared claims and zero denominators.

- [x] T047 [P] [US4] Write `tests/unit/test_dashboard_rules.py` for zero versus unknown counts, coverage decimal/null rules, absent verification/distribution reasons and first-three featured ordering without endorsement. Depends on Groups 3–4.
- [x] T048 [P] [US4] Write `tests/contract/test_dashboard_summary.py` for declared filter scope, entity counts, coverage numerator/denominator/ratio, null verifiedRunCount, unmapped distribution fields, empty results and detached synthetic labels. Depends on Groups 3–4.
- [x] T049 [P] [US4] Write `tests/integration/test_dashboard_queries.py` for filtered investigation selection, grouped related counts, distinct shared claims, document linkage coverage and count agreement across page sizes; prevent join multiplication. Depends on Groups 3–4.
- [x] T050 [US4] Implement `app/repositories/dashboard.py` using the reusable catalog selection and separate aggregates over its selected IDs; document any overlapping tag bucket semantics without pretending they form an exclusive 100% distribution. Depends on T049,T024.
- [x] T051 [US4] Implement `app/services/dashboard.py` with source-linkage—not source-review—coverage, null zero-denominator ratio, unknown verification, unavailable fuel/facility/gravity distributions and default-ordered featured entries. Depends on T047–T050.
- [x] T052 [US4] Add GET /dashboard/summary in `app/api/v1/endpoints/dashboard.py` and `app/api/v1/router.py`, reusing catalog selection filters but rejecting unsupported sort/page controls. Depends on T051.
- [x] T053 [US4] Execute dashboard unit/contract/approved SQL tests and reconcile selected-scope counts with list/run/source/claim endpoints in `specs/001-phase4-catalog-apis/verification.md`; mark unexecuted real-HTTP reconciliation pending T061. Depends on T052.

**Exit criteria**: Counts/coverage describe the selected collection exactly, zero-denominator ratios are unavailable rather than NaN, and total runs/mock classifications never imply verified science.

## Group 6 — Comparison API (US5, P2)

**Entry**: Groups 3–4 identity/observation/provenance behavior and accepted side-by-side contract; does not depend on dashboard completion.
**Independent verification**: Two/three selected studies retain request order and contextual observations; invalid/missing/mixed selections fail wholly and all scientific derivations remain unavailable.

- [x] T054 [P] [US5] Write `tests/unit/test_comparison_rules.py` for 2–3 distinct UUIDs, mixed origin, original-value/unit/context preservation, unknown verification and blocked ratios/deltas/averages/ranks/highlights even when unit strings match. Depends on Groups 3–4.
- [x] T055 [P] [US5] Write `tests/contract/test_comparison.py` for strict body/observation-page limits, 2/3 success order, missing/duplicate/invalid selection failures, empty observations, nested context and not_established/null derived fields. Depends on Groups 3–4.
- [x] T056 [P] [US5] Write `tests/integration/test_comparison_queries.py` for bulk selection/restored order, missing identities, mixed observable units/conditions and bounded per-study observation traversal with exact Numeric/uncertainty fields. Depends on Groups 3–4.
- [x] T057 [US5] Extend `app/repositories/catalog.py` with bulk identity and per-investigation bounded observation queries reusable by comparison; avoid favorable-run selection, unbounded graph loading and outcome aggregates. Depends on T056,T036.
- [x] T058 [US5] Implement `app/services/comparison.py`: reject incomplete/mixed scopes, restore requested order and show labeled originals/context; deltas/highlights=null, comparability=not_established with explicit reasons. No unit conversion or scientific score is added. Depends on T054–T057,T044.
- [x] T059 [US5] Add read-only POST /compare in `app/api/v1/endpoints/comparison.py` and register it in `app/api/v1/router.py`; preserve all canonical request and error semantics and produce no persistence writes. Depends on T058.
- [x] T060 [US5] Execute comparison unit/contract/approved SQL checks and record unchanged DB rows plus original-value/context and blocked-derivation evidence in `specs/001-phase4-catalog-apis/verification.md`. Depends on T059.

**Exit criteria**: Every accepted selection remains complete and ordered; observed values retain unit/run/uncertainty context; unavailable verification cannot be bypassed by status text, apparent DOI or matching units.

## Group 7 — Integration tests and OpenAPI verification

**Goal**: Prove the assembled feature against real PostgreSQL and generated runtime contracts; this does not replace the tests already required inside each slice.
**Entry**: Groups 1–6 behavior complete, reviewed examples and explicit target permissions. Pure OpenAPI checks can be authored before DB permission is available.
**Independent verification**: Execute the six researcher/developer journeys against the running ASGI application and admitted test dataset; distinguish mock, actual PostgreSQL and runtime OpenAPI evidence.

- [x] T061 Write and execute `tests/integration/test_phase4_http_journeys.py` with committed synthetic fixtures and independent read-only sessions from `tests/integration/phase4_fixtures.py`; exercise all 14 operations, cross-endpoint count/provenance reconciliation, empty collections and next-link traversal through the real Router → Service → Repository → Database path. Depends on Groups 1–6.
- [x] T062 Write and execute `tests/integration/test_phase4_read_boundaries.py` for real REPEATABLE READ READ ONLY behavior, snapshot-consistent count/page during a concurrent writer, next-request drift refusal, bounded query counts/loading and no hidden writes; use only approved disposable targets, never modify development data. Depends on T061,T009,T019.
- [x] T063 [P] Implement `tests/contract/test_phase4_openapi.py` comparing generated app.openapi() to `specs/001-phase4-catalog-apis/contracts/openapi.json`: all 14 operations, parameters/limits, required/null fields, aliases, UUID/date formats, decimal strings and 404/422/503/500 models; preserve original health/ready definitions and exercise documented request/response examples rather than regenerate expected output from the app. Depends on Groups 1–6.
- [x] T064 [P] Extend `tests/contract/test_phase4_failure_boundaries.py` with injected connection/timeout/config failures and sensitive dummy inputs to prove sanitized 503/500/422 responses and logs; existing health/ready remains compatible and failures never trigger seeding or empty-success fallback. Do not stop a shared database to simulate faults. Depends on Groups 1–6.
- [x] T065 Write and execute `tests/integration/test_demo_api_roundtrip.py`: invoke the real seed CLI twice on a permitted target, read it through HTTP with a read-only role, verify exact counts/origin, then test authorized isolated drift/sentinel refusal and unchanged rows. Local authorization is produced only by the approved fixture/operator. Depends on T061,T018,T020.
- [x] T066 Run applicable existing schema/migration/config/health regressions from `tests/test_model_structure.py`, `tests/test_migrations.py`, `tests/test_config.py`, `tests/test_health.py` and `tests/integration/test_schema_migrations.py`; record that all 21 models and migrations 0001–0003 remain unchanged in `specs/001-phase4-catalog-apis/verification.md`. No migration authoring or shared-target upgrade. Depends on T061–T065.
- [x] T067 Run Poetry check, Ruff lint/format, relevant and full applicable pytest suites; record exact commands, exit statuses, pass/skip counts, DB authorization scope and unexecuted checks in `specs/001-phase4-catalog-apis/verification.md`. A skipped real DB check is not a pass. Depends on T066.
- [x] T068 Assemble the acceptance evidence matrix for FR-001–FR-030 and SC-001–SC-008 in `specs/001-phase4-catalog-apis/verification.md`, linking every criterion to actual files/tests/results; keep outstanding documentation/consumer gates pending until Group 8, without claiming final convergence. Depends on T067.

**Exit criteria**: All required real-DB/runtime checks have executed evidence or remain explicitly blocked; no unit/mock result is substituted. Full implementation completion is unavailable while required checks fail/skip or applicable owner gates are unresolved.

## Group 8 — Documentation and team handoff

**Goal**: Deliver accurate operating guidance, explicit cross-team boundaries and evidence-backed completion. No external message is sent without explicit instruction.
**Entry**: Slice examples can be prepared earlier; final status/handoff depends on Group 7 actual evidence.
**Independent verification**: A reviewer can trace each surface, original identity/unit/provenance limitation and operational command to the verified contract/evidence without requiring invented approvals.

- [x] T069 [P] Prepare the Frontend packet in `docs/contracts/phase-4-frontend-handoff.md` from accepted examples: UUID/PSI/slug adapter, Decimal originals, unavailable controls/metadata, paged source associations, raw asset limits, synthetic labels and unknown comparison verification. Record owner, status and pending consumer sign-off honestly; do not modify or contact Frontend. Depends on T068.
- [x] T070 [P] Prepare the Data packet in `docs/contracts/phase-4-data-handoff.md`: unchanged schema/identity expectations, origin/unit/status vocabulary needs, original values/uncertainty, source/run mismatch acceptance and scientific verification/telemetry dependencies. Mark Data acceptance pending where absent; no ETL/import task is assigned. Depends on T068.
- [x] T071 Update `specs/001-phase4-catalog-apis/quickstart.md` and `docs/runbooks/phase-4-demo-validation.md` with actually verified setup/read/seed checks, isolated-target prerequisites, expected counts and no-auto-cleanup behavior; distinguish available commands from unresolved environment/team dependencies. Depends on T067,T069–T070.
- [x] T072 Create `docs/phase-4-api-verification.md` and narrowly update `docs/project-status.md` and `docs/documentation-map.md` to match delivered slices, exact execution evidence and open scientific/consumer limitations; do not rewrite Phase 1–2 reports, README or the stable architecture plan. Depends on T068–T071.
- [x] T073 Review Git diff and ignore protections, recording the result in `specs/001-phase4-catalog-apis/verification.md`: no changed models/migrations/diagrams/frontend, no .env/credentials/local authorization/environments/temp artifacts, no fabricated findings and no unrequested scope. Do not stage, commit, push or merge automatically. Depends on T072.
- [x] T074 **Assessment executed on subsequent explicit user request; remediation tasks appended.** Perform final Converge review against `specs/001-phase4-catalog-apis/spec.md`, `plan.md`, `tasks.md` and `verification.md`; close actionable implementation gaps or create scoped remediation entries, identify remaining Data/Frontend owner gates and report bounded completion only when all applicable DoD evidence exists. Stop blocked dependent claims without inventing sign-off. Depends on T069–T073.

**Exit criteria**: Frontend/Data packets and runbook agree with actual behavior, every success criterion has evidence, pending scientific/rollout milestones remain explicit, and Git/secrets/scope checks pass. Owner acceptance cannot be replaced by a checked task.

## Dependencies and execution order

| Group | Required predecessors | Independently verifiable output |
| --- | --- | --- |
| 1 Contracts/shared DTOs | Review + Analyze + implementation authorization | Pure DTO/error/read-boundary contracts |
| 2 Synthetic fixtures/seed | 1; separate approval for DB execution | Deterministic dataset and safe idempotent CLI |
| 3 List/detail | 1–2 | US1 discovery, then US2 canonical detail/tag traversal |
| 4 Runs/evidence | 3 | US2 observation inspection and US3 provenance, separately |
| 5 Dashboard | 3–4 | US4 fixture-exact selected summary |
| 6 Comparison | 3–4; Group 5 not required | US5 contextual 2–3-study inspection |
| 7 Integration/OpenAPI | 1–6 | Real database, HTTP and generated schema evidence |
| 8 Documentation/handoff | 7 for final delivery | Accurate bounded handoff/DoD; examples reviewed earlier |

Dependency graph in plain text: `1 → 2 → 3 → 4 → {5,6} → 7 → 8`. Group 4's run/evidence sub-slices may progress independently after Group 3; shared app/api/v1/router.py edits are serialized. Tests are authored before their behavior; later fixture/helper tasks may be needed to execute a previously written failing test. Such expected red tests do not create reverse implementation dependencies.

## Parallel opportunities and examples

- Shared contracts: T002/T003 after T001; T006/T007 after T004; T008 after T005–T006. Do not edit shared __init__/router files concurrently.
- US6: T011/T012/T013 author separate tests after Group 1. Seed DB execution still waits for explicit target permission and implementation dependencies.
- US1: T022 HTTP contracts and T023 SQL tests use different files; production catalog query edits T024/T025 are sequential.
- US2: T028/T029 detail/manifest tests and later T034/T035 observation tests are separate; catalog service/repository changes are serialized.
- US3: T040/T041 test authoring may run alongside US2 run-test work after Group 3. Evidence queries T042/T043 remain ordered.
- US4: T047/T048/T049 unit/HTTP/SQL test authoring is independent after its predecessors. US5 T054/T055/T056 can run alongside it; dashboard and comparison route registration is serialized.
- Cross-cutting: T063/T064 use separate test files; T069/T070 prepare different handoff packets. None authorizes team contact, deployment or Git mutation.

## Requirement and success-criterion traceability

| Requirements | Primary task coverage |
| --- | --- |
| FR-001 read surfaces | T027,T032,T038,T045,T052,T059,T061 |
| FR-002 identity | T002,T005–T007,T028–T032,T055 |
| FR-003 slug manifest | T014,T029,T031,T069 |
| FR-004 missing display metadata | T005,T022,T026,T028,T031 |
| FR-005 capabilities/adapter | T001,T022,T026–T027,T069 |
| FR-006 search | T022–T025 |
| FR-007 filtering | T023–T025,T049–T050 |
| FR-008 unsupported mappings | T003,T005,T022,T026,T069 |
| FR-009 bounded pages/counts | T004–T005,T023,T025,T030,T035–T036,T041–T043,T062 |
| FR-010 counts/coverage | T047–T053,T061 |
| FR-011 featured/distributions | T047–T052 |
| FR-012 unknown verification | T008,T047–T053,T054,T058 |
| FR-013 detail | T028–T033 |
| FR-014 original runs/conditions | T006,T034–T039 |
| FR-015 measurements/precision | T002,T006,T034–T039,T056–T060 |
| FR-016 raw references/no telemetry | T006,T034,T037,T069–T070 |
| FR-017 original documents | T007,T040–T046 |
| FR-018 all source associations | T007,T040–T046,T061 |
| FR-019 derived membership/mismatch | T041–T046,T061 |
| FR-020 limitations/orphans | T040–T046,T061,T070 |
| FR-021 comparison input/order | T008,T054–T060 |
| FR-022 contextual observations | T034–T039,T054–T060 |
| FR-023 no scientific derivations | T008,T054–T060,T069–T070 |
| FR-024 fixture coverage | T011–T015,T021 |
| FR-025 synthetic identity/context | T002,T012,T014,T019–T021,T061,T065 |
| FR-026 explicit safe seed | T011,T013,T015–T020,T065 |
| FR-027 no curated inference | T012,T019,T061,T065,T070 |
| FR-028 sanitized failures | T003,T010,T011,T018,T022,T055,T064 |
| FR-029 preserved boundaries | T001,T009,T066,T073–T074 |
| FR-030 reviewed examples/tests | T001,all story test tasks,T061–T074 |
| SC-001 six journeys | T020,T033,T039,T046,T053,T060–T061,T068 |
| SC-002 exact membership/counts | T023,T025,T033,T049–T053,T061 |
| SC-003 complete provenance | T040–T046,T061 |
| SC-004 origin separation | T012,T019–T020,T061,T065 |
| SC-005 original zero/null/unit/uncertainty | T002,T034–T039,T054–T060,T061 |
| SC-006 valid/invalid comparisons | T054–T060,T061 |
| SC-007 explicit unsupported/unknown | T003,T022,T026,T047–T060,T064 |
| SC-008 reviewed consumer examples | T001,T069,T071,T074; actual acceptance remains owner evidence |

## Implementation strategy and review checkpoint

Suggested MVP: Groups 1–2 plus Group 3 US1 (through T027), with its real-query/HTTP evidence and relevant Group 7 checks run early. It delivers safe synthetic Explorer discovery; it does not claim full Phase 4 completion. Add US2 detail/observations and US3 provenance next, then dashboard/comparison, full integration and handoff. Run only authorized checks at each increment, and repeat Analyze after material design changes.

Task counts: Group 1 = 10; Group 2 = 11; Group 3 = 12; Group 4 = 13; Group 5 = 7; Group 6 = 7; Group 7 = 8; Group 8 = 6. Total = 74. Primary story labels: US1 = 6; US2 = 12; US3 = 7; US4 = 7; US5 = 7; US6 = 11; shared/cross-cutting = 24. Cross-cutting tasks also verify multiple stories.

This generation step ends with review of this document. No task is marked complete, and no application code, fixture data, database, branch, staging area or commit is changed by generating it. Recommended next Spec Kit step is Analyze consistency; implementation still requires a subsequent instruction.

## Implementation execution record — 2026-11-11

See [verification.md](verification.md) for final commands/results and criterion evidence. Backend executable tasks are complete; Frontend/Data approvals are recorded as pending, not fabricated. The historical generation/review instructions above describe their original stage; the later user instruction authorized implementation and isolated tests. T074 remains unexecuted.


## Phase 9: Convergence

Assessment date: 2026-11-11. Outcome: **tasks_appended; Phase 4 has NOT converged**.

Numbering continues after the existing delivery Groups 1-8. This section is appended without rewriting any earlier text, task ID, checkbox or historical execution claim. The current user-invoked Converge supersedes the earlier prohibition on automatically starting it; the old T074 line is preserved under the append-only rule and is not fresh evidence that this review was blocked.

Scope reviewed: 30 functional requirements, 8 success criteria, 28 story acceptance scenarios, 11 listed edge cases, all 74 existing tasks, 12 technical decision areas and 13 Constitution principles. Findings: 2 contradicts and 6 partial; 4 HIGH, 3 MEDIUM, 1 LOW; no observed CRITICAL finding or unrequested feature. The previous 371-pass/0-skip result is historical execution evidence, not a new run or proof of complete specification coverage.

Read-only reproduction: canonical and snake_case comparison bodies, boolean/string observationLimit values and gravity_raw query names all reached a mocked domain service instead of rejecting contract-invalid forms. Both unknown and real admission were rejected before row handling, even with a matching read-only identity. Tag preview's outer SELECT has zero ordering clauses. A comparison probe with different observable/unit labels returned only the generic not_established caveat. Source inspection confirms whole-table .all() admission, pending Frontend acceptance and 105 mojibake sequences in the pre-existing task text. No database writes or application changes were made by this convergence assessment.

### Remaining tasks, highest severity first

- [x] T075 [US6] **HIGH F1** Restore the approved non-synthetic read states in `app/services/collection.py`, `app/repositories/collection.py` and `app/api/dependencies.py` per FR-027, US6/AC2 and plan/read-model collection semantics (contradicts). Admit explicitly bound unknown/unreviewed empty collections as honest 200/empty results; design and implement stored-field reads that preserve declared origin without assuming curated status. Keep synthetic membership checks and reject mixed origins. Curated publication stays BLOCKED until actual Data acceptance; do not implement ETL, import data, invent review vocabulary or change the ERD. Acceptance: add pure and isolated PostgreSQL/HTTP regressions in `tests/unit/test_collection_context.py` and `tests/integration/test_demo_api_roundtrip.py` for empty unknown/real environments, unknown status, missing origin and synthetic mixing; retained synthetic behavior passes and no record is silently relabeled or loaded as fallback. Required owner decisions must be recorded rather than guessed.
- [x] T076 **HIGH F2** Enforce the approved wire input contract at `app/api/phase4_route.py`, `app/schemas/api/queries.py` and `app/schemas/api/comparison.py` / `app/schemas/api/models.py` per FR-028, FR-030, T003 and T063 (contradicts). Keep internal Python population separate from public camelCase-only validation; reject undeclared snake_case body/query keys and JSON booleans/numeric strings for integer body fields while retaining normal URL integer parsing. Acceptance: in `tests/contract/test_comparison.py`, `tests/contract/test_investigation_list.py` and `tests/contract/test_phase4_openapi.py`, contract-invalid investigation_ids/gravity_raw/observationLimit=true/observationLimit="2" return safe 422 before any repository/domain call; canonical UUID bodies and valid camelCase query requests still succeed and generated schemas agree with actual HTTP behavior. No storage DTO compatibility change.
- [x] T077 [US5] **HIGH F3** Make known mismatch/unmatched/missing-context reasons explicit in `app/services/comparison.py` and the reviewed comparison response projection per FR-022, US5/AC2-4, T054 and T058 (partial). Distinguish different original observable/unit labels, missing values/conditions and unexamined or partial page context instead of only returning a generic caveat. Scope explanations to the observations actually examined; absence on one page is not collection-wide absence. Use the existing caveat/availability surfaces or obtain review for any necessary public contract extension. Do not infer physical equivalence from equal labels, convert units, pool values, compute scientific outcomes or enable verified counts. Acceptance: add unit, HTTP and isolated PostgreSQL cases in `tests/unit/test_comparison_rules.py`, `tests/contract/test_comparison.py` and `tests/integration/test_comparison_queries.py`; original values/uncertainty/IDs/pages remain intact and all derived outcomes stay unavailable.
- [ ] T078 **HIGH F4 - BLOCKED: external Frontend review evidence required.** Complete the consumer acceptance gate in `docs/contracts/phase-4-frontend-handoff.md` and `specs/001-phase4-catalog-apis/contracts/review-record.md` per SC-008, FR-003/030 and the spec's Frontend dependency (partial). Obtain owner-supplied or explicitly authorized Frontend feedback for identity/slug, unavailable fields/controls, exact decimals and full provenance examples; record actual reviewer/date/accepted scope and resolve any backend-owned contract corrections with tests. Until evidence is available, keep the gate pending and do not claim full Phase 4/consumer convergence. Do not fabricate acceptance, modify the Frontend repository or send team messages without explicit instruction. This task does not block independent T075-T077 or T079-T080 work.
- [x] T079 [US2] **MEDIUM F5** Give bounded tag previews deterministic outer ordering in `app/repositories/phase4_catalog.py` per FR-009, T025/T030 and the plan's UUID-ordered child pages (partial). row_number ordering inside the subquery is not a guarantee of outer result order; explicitly order the returned parent/tag rows consistently with `/investigations/{id}/tags`. Acceptance: add repository and real HTTP tests in `tests/integration/test_catalog_queries.py` and `tests/integration/test_demo_api_roundtrip.py` using shuffled tag insertion and more than one preview page; preview IDs and subsequent pages are stable, ordered and duplicate/loss-free with bounded query counts.
- [x] T080 **MEDIUM F6** Bound synthetic admission's materialization in `app/repositories/collection.py` and its caller in `app/services/collection.py` per plan performance/loading constraints and T019/T062 (partial). Replace unrestricted full-table `.mappings().all()` loading with bounded streaming/chunks or SQL-side identity/content checks and early foreign-row refusal. Preserve exact original-value/content comparison, all-21-table coverage, repeatable-read snapshot safety and fail-closed origin checks; do not weaken admission to counts alone or cached stale approval. Acceptance: add isolated PostgreSQL tests in `tests/integration/test_phase4_read_boundaries.py` for larger manifests and unexpected rows, demonstrate bounded batches/materialization, retain no per-entity query growth, and keep seed/readonly/precision/provenance regressions passing.
- [x] T081 **MEDIUM F7** Revalidate the corrected implementation and reconcile evidence in `specs/001-phase4-catalog-apis/verification.md`, `docs/phase-4-api-verification.md` and `docs/project-status.md` per T068/T072 and SC-001-SC-008 (partial). After executable fixes, run Poetry check, Ruff check/format, the relevant contract probes and full pytest with real isolated PostgreSQL; record exact commands/pass/fail/skip counts and map each finding to its regression evidence. Preserve historical results as history, distinguish blocked consumer/scientific gates and update task completion claims only when proven. A fresh user-invoked Converge is still required before reporting convergence; do not auto-commit, push, merge, deploy or silently waive T078. Depends on executable T075-T077 and T079-T080; external T078 may remain explicitly pending.
- [x] T082 **LOW F8** Repair the existing mojibake/question-mark separators in `specs/001-phase4-catalog-apis/tasks.md` per documentation readability and task traceability obligations (partial). Use explicit UTF-8 reads/writes and recover intended ranges/arrows from the existing IDs and approved spec/plan, rather than blindly replacing all question marks. Acceptance: preserve every task ID/order/checkbox/requirement meaning and this appended section, remove the observed corrupt sequences, validate Markdown links and task counts, and ensure subsequent task-ledger updates do not reintroduce encoding damage. This future implementation task may repair text; this Converge invocation itself does not rewrite earlier bytes.

### Next execution and acceptance gates

Run the next authorized `$speckit-implement` pass for T075-T077 and T079-T082, respecting each task's tests and scope. Record T078 as BLOCKED until actual Frontend acceptance evidence arrives; no Data Team ETL or scientific algorithm is a remediation task. Scientific status/unit review and full telemetry remain their existing external/deferred gates. Re-run `$speckit-converge` after fixes and evidence updates. Until then, the green historical suite and checked earlier tasks do not establish convergence.


## Remediation execution record - 2026-11-12

T075, T076, T077, T079, T080, T081 and T082 are complete with executed regression evidence in [verification.md](verification.md). T074 records the previous user-invoked assessment, not a new automatic convergence run. T078 remains BLOCKED: actual Frontend reviewer/date/accepted scope has not been supplied. This gate is not waived by the implementation request.

Current ledger: 82 tasks, 81 checked, one blocked (T078). The earlier implementation/convergence sections are historical records, including their original task counts and scope. UTF-8 separator repairs preserved task IDs, order and meaning; checkbox changes here reflect executed work. Full suite: 392 passed, 0 failed/errors/skipped; 178 PostgreSQL integration and 214 other tests. Poetry check and Ruff lint/format passed. Models/migrations/diagram/README/stable-plan hashes match the protected baseline. No existing research database or Frontend repository was modified; newly generated test databases/roles are retained.

Next: separately request `$speckit-converge` to assess the fixes and the visible external acceptance gate. No convergence, commit, push, merge or deployment was automatically performed by this Implement pass.


## Phase 10: Convergence

Assessment date 2026-11-12. Outcome **tasks_appended**. Phase 4 has not converged.

This assessment covers all 30 functional requirements, 8 success criteria, 28 story acceptance scenarios, 11 edge cases, 82 existing tasks, 12 technical decision areas and 13 Constitution principles. Three partial findings remain, with two HIGH and one MEDIUM. Two require new implementation tasks below. The existing HIGH Frontend acceptance finding remains assigned to T078 and is not duplicated here. No additional missing, contradicts, unrequested or CRITICAL finding was identified in the reviewed scope.

Read-only in-memory reproductions confirm both new findings. The synthetic manifest parser accepts uppercase and unhyphenated spellings of an already present claim UUID, producing three claim rows with only two distinct canonical identities. inspect_fixture then builds a dictionary keyed by UUID and plans only two claim rows for an empty mocked target. Separately, two complete observation pages with identical A/K and B/mm/s entries receive OBSERVABLE_LABEL_MISMATCH and UNIT_LABEL_MISMATCH because the comparison helper tests union cardinality rather than actual cross-page label differences.

The corrected public HTTP boundary was also rechecked with ASGI dependency overrides. Snake_case body/query keys and boolean/string JSON integers return 422 before domain access. Canonical requests reach the mocked service. Source review confirms explicit outer tag ordering, 64-row database streaming batches, all-21-table admission, non-curated empty/stored-field reads, original provenance and unavailable scientific outcomes. The existing 392-pass result, including 178 PostgreSQL integration tests, is evidence from the preceding Implement run. This assessment ran read-only Python/ASGI probes and did not rerun the full pytest suite.

### Remaining implementation tasks

- [x] T083 [US6] **HIGH F1** Reject duplicate canonical UUID identities in `app/services/demo_manifest.py` and `app/repositories/collection.py` per FR-002, FR-024, FR-026, SC-002, T011-T012, T016-T019 and T075 (partial). Parse identity values before uniqueness checks and prevent UUID-keyed dictionaries from silently collapsing two manifest rows. Cover both synthetic fixtures and non-synthetic read snapshots across the approved tables. Preserve supported single-instance UUID spellings and distinct PSI/slug/source identities. Acceptance requires regression cases in `tests/unit/test_demo_manifest.py` and `tests/unit/test_collection_context.py` for identical and conflicting rows whose UUID strings differ only by case, hyphens or another supported UUID spelling, plus appropriate seed/read-admission cases in `tests/integration/test_demo_seed.py` and `tests/integration/test_demo_api_roundtrip.py`. Invalid duplicates must produce safe refusal before inserts and before successful read admission, with existing rows unchanged and no misleading inserted/already-present counts. Run the relevant unit/HTTP/isolated PostgreSQL checks and record actual evidence in `specs/001-phase4-catalog-apis/verification.md`. No schema change, new import interface or cleanup operation is needed.

- [x] T084 [US5] **MEDIUM F2** Correct cross-study label mismatch explanations in `app/services/comparison.py` per FR-022, US5/AC2-4, T058 and T077 (partial). Compare the original observable/unit associations and stored run-metadata labels at their stated scope. Identical heterogeneous pages must not be described as having cross-study label differences merely because their union contains multiple values. Keep genuine missing/unmatched/different-label explanations and partial-page scope explicit. Equal strings must continue to leave scientific comparability not_established. Acceptance requires matched multi-observable/multi-unit pages, reordered equivalent pages, matching heterogeneous run metadata, actual unit/observable/run-label differences, null values and partial pages in `tests/unit/test_comparison_rules.py`, `tests/contract/test_comparison.py` and `tests/integration/test_comparison_queries.py`. Original values, units, uncertainty, identities and pagination must survive unchanged and all derived outcomes must remain unavailable. After T083 and T084 fixes, run Poetry check, Ruff lint/format and the full suite with actual isolated PostgreSQL, then reconcile `specs/001-phase4-catalog-apis/verification.md`, `docs/phase-4-api-verification.md` and `docs/project-status.md` with exact results and pending T078 evidence.

### Existing external dependency and handoff

T078 remains **BLOCKED** for actual Frontend reviewer/date/accepted-scope evidence under SC-008 and FR-003/030. Its existing task and handoff packet continue to own that work. Data curated publication, scientific verification and telemetry remain the already documented external or deferred boundaries.

The ledger now contains 84 tasks, with 81 checked, two new executable tasks and T078 pending external acceptance. Earlier completion statements describe their recorded execution stages. Run `$speckit-implement` for T083-T084, then request a follow-up `$speckit-converge` assessment with the acceptance gate visible.


## Phase 10 implementation execution record - 2026-11-12

T083 and T084 are complete. Canonical UUID uniqueness is checked across all 21 tables before repository SQL and before dictionaries can collapse rows. Synthetic fixture and unknown snapshot parsers reject duplicate UUID spellings while preserving valid single-instance spellings and FK references. Comparison caveats compare actual cross-page label sets and observable/unit associations, retaining page scope and unavailable derived outcomes.

The new unit regressions reproduced both findings before implementation. Final verification passed Poetry check, Ruff lint/format (168 files) and the full pytest suite with actual isolated PostgreSQL. Result **441 passed, 0 failed/errors/skipped**, including **185 integration tests and 256 other tests**, in 69.53 seconds. The focused PostgreSQL remediation pass was 8 passed. See [verification.md](verification.md) for commands, acceptance evidence and changed files.

Current ledger **83 of 84 tasks checked**. T078 is the sole remaining task and remains blocked for actual Frontend reviewer/date/accepted-scope evidence. The earlier counts and findings describe previous review stages. Models, migrations, diagram, README and stable plan hashes match the protected baseline. Generated test databases/roles are retained under the testing runbook. A new user-invoked Converge remains the next review step.
