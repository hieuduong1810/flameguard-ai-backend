# Phase 6 chat and Advisor verification

Implementation and audit follow-up verified 2026-11-13. This summary was added
to the documentation index on 2026-11-14. The approved backend scope delivers
persistent demo chat, bounded conversational context and structured Advisor
orchestration. The [engineering report](../specs/phase6-rag-advisor/engineering-report.md)
and [verification ledger](../specs/phase6-rag-advisor/verification.md) retain the
detailed implementation and executed evidence.

## Delivered APIs

- POST `/api/v1/chat/sessions`
- GET `/api/v1/chat/sessions/{identity}`
- GET `/api/v1/chat/sessions/{identity}/messages`
- POST `/api/v1/chat/sessions/{identity}/messages`
- POST `/api/v1/advisor/assessments`

Chat persists messages and original-document citations atomically. The provider
receives bounded history from the current session, optional investigation context,
current question, corpus/dataset versions and allowed source references. Advisor
uses Phase 5 prevention, detection and suppression evidence with explicit gaps,
pagination, review status and provider outcomes. Mock outputs carry synthetic
labels. Provider selection supports trusted per-application injection.

## Storage boundary

[ADR-0004](decisions/ADR-0004-runtime-chat-boundary.md) records the accepted
scientific/runtime separation within the same PostgreSQL database. A read-only
scientific connection and a chat INSERT-only runtime connection use distinct
roles. Admission v2 excludes exactly the three chat tables and validates the
remaining scientific collection. The chat portion of Phase 5 T062 is resolved.
Broader scenario-history persistence requires its own approved scope.

## Recorded verification and handoff

The final Phase 6 audit follow-up recorded **572 full-suite tests passed** and
**210 isolated PostgreSQL integration tests passed**, with zero failures/skips.
Poetry check, Ruff lint and Ruff formatting passed. These are the historical
Phase 6 results documented in the engineering report.

T001–T017 and follow-up T020–T023 are complete. **T018 AI/Data acceptance** and
**T019 Frontend acceptance** remain pending. Real provider activation depends on
accepted scientific corpus, review and evaluation requirements. The approved
public-demo session lifetime is 24 hours.

See the [handoff](../specs/phase6-rag-advisor/handoff.md),
[API contracts](../specs/phase6-rag-advisor/contracts.md),
[OpenAPI snapshot](../specs/phase6-rag-advisor/openapi.json) and
[runtime operations](../specs/phase6-rag-advisor/runtime-operations.md).
