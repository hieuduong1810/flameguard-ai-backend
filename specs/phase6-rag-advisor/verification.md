# Phase 6 engineering verification

Prepared 2026-11-13. Owner-approved implementation follows
[approval.md](approval.md) and ADR-0004.

## Criterion evidence

| Requirement | Implemented boundary | Executed evidence |
| --- | --- | --- |
| FR-001 | Existing FastAPI/service/repository/Poetry architecture | Ruff and full regression suite |
| FR-002/003, SC-003 | Explicit v2 fixed runtime scope and separate writer role | PostgreSQL runtime grants, forged exclusions, v1 rejection, scientific tamper, Phase 4–5 reads after chat inserts |
| FR-004/010, SC-001 | Session/message HTTP routes, 24-hour expiry, stable history and privacy envelope | HTTP tests, invalid input, expired session and OpenAPI checks |
| FR-005, SC-002 | Advisory transaction lock, atomic pair/citation flush | Concurrent pairs, injected post-flush failure rollback, exact history round-trip |
| FR-006 | Exact document/locator/excerpt/run association validation | Forged citation, excerpt mismatch, repeated associations and synthetic review tests |
| FR-007/008 | Detached provider DTOs, mock/unavailable, bounded execution | Default unavailable, synthetic abstention, timeout, cancellation and output bound tests |
| FR-009 | Phase 5 evaluation plus per-pillar Advisor invocation | Live Advisor HTTP/OpenAPI test over admitted synthetic evidence |
| FR-011, SC-004 | Full legacy and Phase 6 checks | Command outcomes recorded in engineering-report.md |

The first focused PostgreSQL run had five passes and one failure. Validation
exceptions were incorrectly caught as a generic service error. The handler now
preserves HTTP 422. Nine focused PostgreSQL tests then passed. An additional
live test verifies Phase 4–5 reads after runtime inserts and rejects scientific
snapshot mutations. The initial full run passed 561 tests. The expanded full
run passed 566 tests. Final integration and targeted verification are recorded
in the engineering report.

## Focused convergence

The review covered accepted FR-001–FR-011 and SC-001–SC-004.
It identified and corrected validation-error mapping, legacy plain-text body
handling, malformed envelope rejection, multiset citation checks, synthetic
review labeling, provider output bounds, per-pillar Advisor context and HTTP
cache headers. Scientific admission rejects content changes and expanded
runtime exclusion sets. V1 behavior remains covered by the legacy suite.

External scientific grounding quality, real AI provider activation and Frontend
acceptance require the relevant owners' evidence. Runtime scenario-history
activation remains beyond the chat-only T062 boundary accepted in ADR-0004.

## Focused audit follow-up

T020–T023 cover the owner-requested conversational context, provider injection
and Advisor gap/context fixes. Persisted history is scoped by session UUID in
the database query and projected inside a short runtime transaction before the
provider call. Bounded history and labels are detached from ORM sessions.

Regression tests verify a follow-up receives the original same-session question,
other-session text is absent, investigation identity and scientific versions are
present, and the history count/character budgets hold. A trusted injected adapter
cannot publish a real-origin answer through the existing scientific gate.
Advisor tests distinguish empty, paged, unreviewed, unavailable and abstained
evidence and reject an evaluation/admission version mismatch with HTTP 409.

The first focused invocation recorded eight passes and 13 setup errors because
the local PostgreSQL service was stopped. Docker PostgreSQL completed automatic
recovery, then the same focused checks passed 21 tests with zero failures/skips
in 8.85 seconds. Final full-suite and integration outcomes are recorded in the
engineering report. Public OpenAPI paths, response schemas and status contracts
remain unchanged by this internal-contract follow-up.
