# Focused consistency analysis

Performed 2026-11-13 against existing collection admission, chat models, Phase 5
handoff, Constitution and Phase 6 backlog. This analysis covers planning artifacts.

| Finding | Disposition |
| --- | --- |
| Mutable chat rows break current exact all-table admission | Explicit opt-in v2 partition with fixed three-table runtime set proposed. Owner approval required. Legacy path retained. |
| Separate databases break existing PostgreSQL source/investigation FKs | Same database with restricted roles proposed. Physical schema stays in place. |
| Chat metadata exceeds existing role/body schema | Versioned Text envelope proposed with legacy plain-text projection. Owner approval required. |
| Session UUID gives continuity but has no authenticated owner | Public demo scope, 24-hour access and retained-row disclosure proposed. Owner approval required. |
| No stable idempotency field in current schema | Explicit non-idempotent POST proposed. No automatic retry. Owner approval required. |
| Mock citations could appear scientifically reviewed | Require synthetic/unreviewed labels and original admitted associations. Real provider publication remains gated. |
| Long provider calls can hold DB transactions | Detached context before provider calls, short writer transaction after validation. |
| T062 also covers wider scenario/runtime persistence | Proposed closure scoped to Phase 6 chat boundary. Wider writer activation retains a separate dependency. |

FR-001–FR-011 map to T005–T017. SC-001–SC-004 map to HTTP,
rollback/admission and executed-suite tasks. The owner subsequently approved the material decisions in
[approval.md](approval.md). Implementation and focused convergence evidence
are recorded in [verification.md](verification.md).
