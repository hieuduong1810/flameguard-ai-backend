# Phase 6 Chat and structured Advisor

Branch `feat/phase6-rag-advisor`. Prepared 2026-11-13.
Storage, privacy, API and implementation scope approved by the owner on
2026-11-13. Backend/mock implementation verified for that scope.

## User scenarios and acceptance

### US1 Persistent demonstration conversation (P1)

A caller creates an opaque session, submits a bounded question and reads paged
messages. A second request retrieves committed history. An expired or unknown
session returns 404. Concurrent requests retain complete user/assistant pairs.
A failed write leaves neither a partial answer nor orphan citations.

### US2 Evidence-grounded provider boundary (P1)

Backend validates provider output against the admitted original sources and
exact claim-source associations. Unknown documents, locators, excerpts or
cross-investigation references are rejected. Synthetic responses carry mock
origin and review labels through HTTP and history. Provider timeout and absence
produce explicit outcomes. The AI Team supplies future retrieval and reasoning.

### US3 Prevention, Detection and Suppression Advisor (P2)

A scenario evaluation supplies explicit pillar evidence to an Advisor provider.
The response contains observations, gaps, caveats and validated original source
references per pillar. Empty or unsupported evidence produces abstention.
The mock uses fixed labeled examples and the existing Phase 5 evidence boundary.

## Functional requirements

- FR-001 Reuse FastAPI, Poetry, async SQLAlchemy and Router → Service → Repository.
- FR-002 Resolve T062 through an explicitly versioned scientific/runtime admission
  boundary and least-privilege roles before enabling chat writes.
- FR-003 Preserve legacy 21-table admission and Phase 4–5 API behavior.
- FR-004 Create/read sessions and create/page messages using the proposed HTTP
  contract. Preserve original document UUIDs and citation locators.
- FR-005 Persist a validated user/assistant exchange and citations atomically.
  Serialize commits per session. Provider calls occur outside database transactions.
- FR-006 Validate session investigation scope, source membership, exact locators,
  excerpts and review/origin eligibility before committing provider output.
- FR-007 Configure unavailable/mock/real providers only through trusted settings.
  Supply contracts for real adapters and default to unavailable until configured.
- FR-008 Return answered, abstained, unavailable or timeout outcomes with provider,
  corpus and model version metadata where supplied. Reject malformed output with
  a sanitized error. Mock output stays synthetic and unreviewed.
- FR-009 Reuse Phase 5 scenario input and pillar evidence for structured Advisor.
- FR-010 Enforce the accepted privacy/retention and non-idempotent POST policy.
- FR-011 Verify HTTP/OpenAPI, rollback, permissions, source provenance, concurrency,
  cancellation, missing data and Phase 4–5 regressions on isolated PostgreSQL.

## Success criteria

- SC-001 All accepted endpoint examples and error paths have executed HTTP tests.
- SC-002 Invalid citations and failed writes leave no persisted partial exchange.
- SC-003 Runtime chat inserts leave v2 scientific admission/fingerprint unchanged,
  while scientific tampering fails admission. Legacy admission stays exact.
- SC-004 Required lint, full pytest and PostgreSQL tests execute with counts/skips
  recorded. Mock tests prove backend behavior only.

## Scope and dependencies

Backend owns orchestration, validation, persistence and provider mocks. Real AI
evaluation, curated corpus acceptance and Frontend acceptance remain external
tasks. Phase 5 T056–T060, T061 deferred and Phase 4 T078 retain their status.
T062 may close only for the explicitly accepted Phase 6 storage scope.

Material decisions and implementation authorization are recorded in
[approval.md](approval.md). Scientific algorithms and prediction remain AI-owned.
