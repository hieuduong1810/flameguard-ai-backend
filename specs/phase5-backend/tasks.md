# Phase 5 backend tasks

The owner authorized all executable Phase 5 work on 2026-11-12. Independent tasks proceed while Data, scientific and Frontend acceptance remains pending. V-01 covers the two supplied local fixture credentials, fresh isolated databases and roles retained for inspection. Read [review-record.md](contracts/review-record.md) for the exact scope.

## Phase 1: Reconciliation and setup

- [X] T001 Capture branch/status, protected hashes, criteria and scope in verification.md.
- [X] T002 Reconcile owner-authorized HTTP/provider examples and external acceptance gates.
- [X] T003 Run read-only Spec Kit Analyze and record coverage and findings.

## Phase 2: Shared providers and context

- [X] T004 Prepare deterministic TEST_ONLY fixtures for complete and split runs, original values, ranking ties and repeated sources.
- [X] T005 Test detached provider contexts, defaults, origin, deadline and cancellation.
- [X] T006 Implement detached immutable provider context and versioned protocols.
- [X] T007 Implement independently unavailable defaults and fixed TEST_ONLY providers.
- [X] T008 Implement server-only composition and bounded acquisition with safe diagnostics.
- [X] T009 Wire the Phase 5 service dependency independently of Phase 4.

## Phase 3: US1 scenario and coverage

- [X] T010 [US1] Test decimal syntax, exact units, bounds, zero/null/omission and strict DTOs.
- [X] T011 [US1] Test same-run support, incompatible/missing/flagged/conflicting evidence, foreign decisions and six dimensions.
- [X] T012 [US1] Test HTTP success, unavailable states and sanitized failures.
- [X] T013 [US1] Test bounded PostgreSQL run/condition reads, exact originals and ordering.
- [X] T014 [US1] Test runtime OpenAPI and Phase 4 preservation.
- [X] T015 [US1] Implement public scenario/run DTOs.
- [X] T016 [US1] Implement detached collection-scoped run/condition reads with caps.
- [X] T017 [US1] Implement explicit interpretation and lexical scenario digest.
- [X] T018 [US1] Implement structural validation for fixture-only same-run decisions.
- [X] T019 [US1] Orchestrate one read-only snapshot and independent providers after read completion.
- [X] T020 [US1] Implement deterministic replay, section bindings and examined-page summary.
- [X] T021 [US1] Register POST /api/v1/mission/scenarios/evaluate and sanitized errors.
- [X] T022 [US1] Generate runtime OpenAPI and reconcile examples.
- [X] T023 [US1] Test read-only lifecycle, failure, drift and rollback against PostgreSQL.
- [X] T024 [US1] Test multi-page repeat traversal, direct final page, empty scope and binding drift.
- [X] T025 [US1] Record US1 evidence and external blockers.

## Phase 4: US2 ranking

- [X] T026 [US2] Test complete ranking delivery identity, versions, order, ties, scale, scope and nulls.
- [X] T027 [US2] Test bounded JSON acquisition, deadline, cancellation and safe failures.
- [X] T028 [US2] Test independent ranking HTTP states and pagination.
- [X] T029 [US2] Define immutable ranking DTOs and explicit score semantics.
- [X] T030 [US2] Validate complete ranking deliveries and canonical identity before paging.
- [X] T031 [US2] Implement fixed deterministic ranking adapter and unavailable default.
- [X] T032 [US2] Project rankings with supplied ordering and delivery binding.
- [X] T033 [US2] Publish ranking contract and runtime schema.
- [X] T034 [US2] Verify ranking identity resolution and replay against PostgreSQL.
- [X] T035 [US2] Record US2 evidence and external Data gate.

## Phase 5: US3 pillar evidence

- [X] T036 [US3] Test explicit classification and document/locator reference validation.
- [X] T037 [US3] Test pillar provenance, empty/unavailable states and repeated associations over HTTP.
- [X] T038 [US3] Test PostgreSQL association traversal, nullable run and context mismatch.
- [X] T039 [US3] Implement explicit versioned classification provider and validator.
- [X] T040 [US3] Implement bounded PostgreSQL claim/source/optional run queries.
- [X] T041 [US3] Project original associations and limitations without new findings.
- [X] T042 [US3] Integrate independently paged pillars and detachable labels.
- [X] T043 [US3] Publish and verify pillar schema and examples.
- [X] T044 [US3] Record US3 provenance evidence and classification gate.

## Phase 6: US4 comparison preservation

- [X] T045 [US4] Run focused Phase 4 comparison preservation regressions including context and null derived values.
- [X] T046 [US4] Record comparison preservation and deferred enrichment.

## Phase 7: Verification and handoff

- [X] T047 Test adversarial provider failures, sanitation, and independent sections.
- [X] T048 Verify authorization and privileges, then execute PostgreSQL fixtures and regressions.
- [X] T049 Execute Poetry check, Ruff checks and full pytest, recording exact outcomes.
- [X] T050 Execute the HTTP/lifespan/OpenAPI quickstart and repeat traversal.
- [X] T051 Produce team handoff, engineering report and implementation summary.
- [X] T052 Run Spec Kit Converge across all criteria, and implement/test any appended engineering gaps.
- [X] T053 Review scope, protected files, links and whitespace.
- [X] T054 Update the Phase 5 phase record and live project status after verification.

- [X] T055 Implement and verify the lossless compatible subset of scenario persistence in a trusted service transaction (FR-018, SC-006).

## Phase 8: External acceptance and deferred work

- [ ] T056 Data and Backend accept official dataset/identity manifests and raw recovery, D-01. Evidence required: versioned export and mapping/identity collision corpus. Blocks real P5-01–P5-06.
- [ ] T057 Data and scientific reviewers accept variable/quality mapping and same-run methodology, D-02/D-03. Evidence required: reviewed policy, applicable units/tolerances and publication eligibility corpus. Blocks real coverage.
- [ ] T058 Data accepts the real ranking export/service and its score semantics, D-04. Evidence required: complete versioned delivery, identities, exact applicability and rejection corpus. Blocks real rankings.
- [ ] T059 Data accepts reviewed pillar classifications/facts/sources, D-05. Evidence required: source/locator and review corpus. Blocks real pillar evidence.
- [ ] T060 Frontend accepts F-01 consumer contract and integration. Evidence required: named reviewer/date/scope and actual consumer test results. Phase 4 T078 remains independent and open.
- [ ] T061 Data and Frontend accept P5-07 optional comparison eligibility explanation, D-03/F-02. Evidence required: scientific and additive consumer policies. Deferred.
- [ ] T062 Backend owner selects a runtime storage lifecycle/writer binding compatible with exact catalog admission. Evidence required: approved write target, access/retention and impact for Phase 4 readers. Extra scenario fields require separately justified lossless mapping or schema approval.

## Dependencies and acceptance mapping

T001–T003 precede implementation. T004–T009 supply shared providers; T010–T025 establish US1, T026–T035 add US2, and T036–T044 add US3. T045–T046 can execute independently. T055 can execute independently of the public route and uses an isolated writable fixture. T047–T054 verify the combined scope. T056–T062 never gate mock engineering execution.

| Criteria | Tasks |
| --- | --- |
| FR-001, FR-016, SC-006 | T014, T045–T049, T053–T055 |
| FR-002, FR-003, FR-014, FR-018, SC-001 | T010, T012, T015, T017, T021–T022, T025, T047, T055 |
| FR-004–FR-006, SC-002 | T011, T013, T016, T018–T020, T023–T025 |
| FR-007, FR-015, SC-003 | T013, T020, T024, T026, T032, T034, T038, T043, T050 |
| FR-008–FR-010, SC-004 | T026–T035 |
| FR-011–FR-012, SC-005 | T036–T044 |
| FR-013, FR-014, FR-017, SC-007 | T004–T012, T023, T027–T028, T037, T047, T050–T054 |

## Phase 9: Convergence

- [X] T063 Reject foreign or duplicate run and condition records at the policy boundary and guard non-finite originals before comparison per FR-004–FR-006 and SC-002 (partial).
- [X] T064 Bind pillar continuation to canonical classification content, independently of ranking, per FR-007, FR-011 and FR-015 (partial).
- [X] T065 Bind ranking to its own scenario interpretation version and apply only section-relevant provider bindings; disclose exhaustion of the public offset ceiling per FR-007, FR-009 and FR-015 (partial).
- [X] T066 Verify original Phase 4 comparison observations and explicit limits through the Phase 5 fixture app, and route trusted scenario persistence flush through the existing repository per SC-006 and Constitution II (partial).

## Phase 10: Convergence

- [X] T067 Include exact admitted manifest originals in the replay fingerprint and verify a source-only decimal scale change against PostgreSQL per FR-007, FR-012 and FR-015 (partial).
- [X] T068 Exercise cancellation inside an active read transaction and default-unavailable responses using the live isolated app per FR-013–FR-014 and SC-007 (partial).
