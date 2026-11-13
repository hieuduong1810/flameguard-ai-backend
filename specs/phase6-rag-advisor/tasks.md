# Phase 6 tasks

The owner approved material scope and implementation on 2026-11-13. Engineering
tasks are verified. External acceptance remains pending.

## Foundation

- [x] T001 Inspect focused architecture, Phase 6 backlog and Phase 5 T062 handoff.
- [x] T002 Prepare spec, storage/privacy/API proposal and implementation plan.
- [x] T003 Perform one focused consistency analysis and record findings.
- [x] T004 Record owner approval and implementation authorization in approval.md.
- [x] T005 Implement explicit v2 admission scope with legacy exact-admission tests in app/repositories/collection.py and app/services/collection.py. Covers FR-002/003 and SC-003.
- [x] T006 Add runtime engine, settings and effective permission/target validation in app/core/database.py and focused tests. Covers FR-002.

## US1 Chat persistence

- [x] T007 Add chat DTOs, envelope compatibility and HTTP contract examples in app/schemas/api/chat.py and feature contracts. Covers FR-004/010.
- [x] T008 Implement app/repositories/chat.py and app/services/chat.py with expiry, commit serialization and atomic exchange/citation writes. PostgreSQL tests must verify rollback/concurrency/FKs. Covers FR-005/010 and SC-002.
- [x] T009 Add session/history/message endpoints and HTTPX/OpenAPI tests covering accepted input, unknown/expired sessions and retry semantics. Covers FR-004/010 and SC-001.

## US2 Providers and citations

- [x] T010 Implement detached RAG provider contracts, unavailable/mock configuration, timeout and cancellation in app/integrations/chat/. Covers FR-007/008.
- [x] T011 Validate citation source/scope/locator/excerpt/review and reject source drift before writes in app/services/chat_citations.py. Test forged sources, repeated associations, synthetic labels and legacy messages. Covers FR-006/008 and SC-002.
- [x] T012 Integrate provider outcomes with message routes and sanitize errors. Verify no partial persistence on invalid output and bounded timeout behavior. Covers FR-005/008.

## US3 Advisor

- [x] T013 Add Advisor provider/DTO/service/route reusing Phase 5 evidence context and pillar grouping. Cover all three pillars and missing evidence. Covers FR-009.
- [x] T014 Test Advisor abstention, unavailable, timeout, malformed output and invalid citations through HTTP and isolated PostgreSQL. Covers FR-006/008/009 and SC-001.

## Verification and handoff

- [x] T015 Execute Poetry check, Ruff lint/format, full pytest and isolated PostgreSQL suite. Record counts/skips and Phase 4–5 regression evidence. Covers FR-011 and SC-004.
- [x] T016 Perform focused convergence against FR-001–FR-011 and SC-001–SC-004, append/fix genuine gaps and rerun affected checks.
- [x] T017 Write engineering report, API/operator documentation and updated project status with executed evidence and scoped T062 disposition.
- [ ] T018 External AI/Data scientific corpus/provider acceptance. Remains blocked pending owner evidence.
- [ ] T019 Frontend API/privacy consumer acceptance. Remains blocked pending owner evidence.

Dependency order T004 → T005/T006 → T007/T008/T010/T011 → T009/T012 → T013/T014 → T015/T016/T017. T018/T019 remain external. Test and provider-contract authoring can proceed after approval independently of external delivery.

## Focused audit follow-up

- [x] T020 Extend the internal RAG request with bounded persisted session history, optional investigation identity, current question, corpus/version context and allowed sources. Verify follow-up questions, history bounds and session isolation.
- [x] T021 Add a trusted per-application provider factory/injection boundary. Verify mock/unavailable selection and that injected adapters retain publication/citation gates.
- [x] T022 Derive Advisor gap reasons from Phase 5 pillar totals, page metadata, review labels and provider outcomes. Verify evaluation/admission fingerprint and version consistency before and after provider calls.
- [x] T023 Execute focused, lint, full and isolated PostgreSQL regression checks. Record outcomes and follow-up handoff without changing the approved public API schema.
