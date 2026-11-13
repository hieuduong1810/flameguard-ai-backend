# Phase 7 focused convergence

Assessed 2026-11-13 against the approved spec, plan, tasks, owner decision and
Constitution. The scope is the authorized stateless backend feature.

## Acceptance evidence

| Criterion | Implemented evidence | Executed verification |
| --- | --- | --- |
| FR-001 / P7-01 | Readiness gates and explicit unknown/unvalidated states | Contract, registry and gate tests |
| FR-002 / P7-02 | Detached provider call, unavailable/mock and per-app factory | Injection, malformed output, exception, timeout and cancellation tests |
| FR-003 / P7-03 | Existing model/training tables, version-1 metadata and identity binding | PostgreSQL registry and version-conflict tests, unsupported/incomplete declaration tests |
| FR-004 / P7-04 | Supplied domain bounds, exact units, material and oxygen meaning, uncertainty and validation expiry | Domain edge/missing/unit/expiry/interval tests |
| FR-005 / P7-05 | Provider outside read transaction, response identity/unit checks and snapshot recheck | HTTP downstream-state tests and snapshot-drift rejection |
| FR-006 / P7-06 | Approved stateless implementation through scientific reader | All-21-table snapshots after not_ready, conflicts, successful internal mock, invalid response, failure and timeout |
| FR-007 | Admission v1/v2, exact scientific manifest and existing chat permissions | Phase 4–6 regression, Phase 7 admission v2 and rejected manifest/review changes |
| FR-008 | OpenAPI and handoff documentation | OpenAPI operation/error schemas, request fixture and documentation-link checks |
| SC-001 | Every requirement has implementation or explicit external gate | This matrix and T001–T014 |
| SC-002 | Default provider/collection gates prevent scientific publication | Actual public PostgreSQL calls return not_ready with no numeric result |
| SC-003 | Required quality and database checks | Recorded in verification.md |

## Resolved implementation gaps

Focused review added or strengthened registry expiry validation, explicit
OpenAPI error DTOs, provider snapshot echo and identity checks, independent
validation copies, constructed-result revalidation, duplicate/malformed JSON
rejection, both admission versions and database no-write assertions across
successful and failing internal provider paths. These complete existing
T005–T010 criteria. They create no new project phase or external integration.

The internal orchestration harness explicitly replaces readiness only in tests
to exercise downstream outcomes with synthetic fixtures. Production scientific
admission and public mock behavior are tested independently. Those internal
successes provide transport and persistence evidence only.

## Disposition

The authorized backend scope converged after the final verification gates.
There are no remaining unbuilt executable backend requirements in this scope.
No duplicate convergence tasks are appended. T013 and T014 already record the
remaining external acceptance work.

Overall real-data/scientific integration remains pending. Current admission
cannot publish reviewed collections, real dataset-version binding is unavailable,
and a validated real AI provider/model has not been accepted. Those gates retain
`not_ready`. Frontend acceptance is pending. Future persistence needs a separate
owner-approved scope and lossless provenance/storage review.
