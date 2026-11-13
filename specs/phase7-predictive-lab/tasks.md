# Phase 7 tasks

## Preparation

- [x] T001 Reuse preflight and confirm competition permission, Phase 7 branch and Phase 6 baseline.
- [x] T002 Create feature spec/plan and concrete stateless/API proposal covering P7-01–P7-06.
- [x] T003 Perform one focused consistency analysis and record material gates.
- [x] T004 Record owner scope/API approval and implementation authorization.

## Backend slices

- [x] T005 Define prediction DTOs, versioned AI metadata and detached provider contracts. Cover P7-01–P7-04 with null/unit/version validation tests.
- [x] T006 Implement read-only ModelVersion/ModelTrainingRun queries and scientific admission binding. Test registry absence, unknown metadata and version identity.
- [x] T007 Implement unavailable and fixed synthetic providers with per-app injection, timeout/failure/output validation tests. Cover P7-02/P7-05.
- [x] T008 Implement readiness/applicability gates using supplied artifact/domain/uncertainty declarations. Test unsupported/missing conditions, units, material, gravity, pressure, oxygen and validation state. Cover P7-01/P7-03/P7-04.
- [x] T009 Implement approved GET/POST routes and stateless orchestration. Add HTTP/OpenAPI tests for readiness, unsupported, drift and provider errors. Cover P7-01/P7-05.
- [x] T010 Verify P7-06 no-write decision using isolated PostgreSQL tests, permission/collection checks, registry/scenario/prediction row invariants and Phase 4–6 regressions.

## Verification and handoff

- [x] T011 Run required Poetry/Ruff/full/PostgreSQL checks, fix failures and record counts/skips.
- [x] T012 Perform focused convergence, fix genuine gaps and produce OpenAPI, provider/configuration/frontend handoff, engineering/verification reports and current project status.
- [ ] T013 External AI/Data acceptance of real model/provider, evaluation, uncertainty and official dataset compatibility. Pending owner evidence.
- [ ] T014 External Frontend acceptance of readiness/execution behavior and display states. Pending owner evidence.

T004 gates implementation. T005 → T006/T007 → T008/T009 → T010/T011 → T012.
T013/T014 remain external acceptance. Conditional prediction persistence needs a
new approved storage scope and is assessed through T010 in this stateless feature.
