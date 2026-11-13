# Phase 6 material decision proposal

Prepared 2026-11-13. Status APPROVED by the project owner on 2026-11-13
through “duyệt rồi tiến hành làm đi”. Implementation and isolated PostgreSQL
verification are authorized for the proposed scope below.

## Storage boundary for T062

Use the same PostgreSQL database and existing tables/FKs with two SQLAlchemy
engines. `DATABASE_URL` remains the scientific reader. A separate secret runtime
URL selects a role restricted to SELECT/INSERT on `chat_session`, `chat_message`
and `message_citation`, plus SELECT on original source/investigation records
needed for validation. Deny scientific writes, ownership, superuser, role/database
creation and schema creation. Validate effective privileges, including inherited
and PUBLIC grants, and require both connections to identify the same database
OID/server endpoint. Schema/table ownership remains with a separate operator.

Introduce an opt-in v2 admission configuration declaring exactly those three
runtime tables. Validate the remaining 18 tables with the existing exact
membership/value checks and preserve source/review checks. Fingerprints cover
the admitted scientific tables and explicit boundary version. Reject unknown,
missing or expanded runtime exclusions. Legacy configurations retain all-table
checks. Grant the reader SELECT but no write permission on every table.

This logical partition avoids table moves, data copying, cross-database FK
replacement and ORM/migration changes. A separate database would require replacing
the existing source/investigation FKs. A separate schema would require table
moves and coordinated model/migration changes. Those alternatives add impact
beyond the current chat requirement.

Validate source citations first using the admitted snapshot, then recheck source
identity/content against the same scientific scope before committing a response.
FKs protect original IDs at commit. Session-level PostgreSQL advisory transaction
locks serialize message-pair commits. Recheck session eligibility inside the
writer transaction. Close provider calls before acquiring the writer transaction.

Production/local grants and runtime URLs are operator setup. Tests provision
fresh isolated roles/databases and retain them. Rollback disables the runtime
configuration and routes. A v1 manifest on a database containing new runtime rows
continues to reject the mismatch and requires an explicit v2 configuration.

This resolves the chat boundary portion of T062 after approval and verification.
Public scenario-history writer activation, additional mutable tables and
unsupported scenario fields remain separately scoped.

## Privacy and lifetime

Use the existing opaque UUID as a demo continuity identifier. Anyone holding it
can access the session during its lifetime. Accept public research questions only,
with a visible API privacy caveat. Avoid logging bodies, session IDs and citations.
Propose a 24-hour access lifetime based on existing `created_at`, with 404 after
expiry. Stored rows remain until an operator-authorized retention cleanup.
Automatic deletion, user accounts and browser authentication require later scope.
GET responses use `Cache-Control: no-store`.

Persist newly created assistant bodies as a versioned JSON envelope inside the
existing Text column to preserve output state, mock labels and provider versions.
Legacy plain text bodies remain readable with explicit unknown metadata.
Original citation IDs and exact locators stay in `message_citation`.

## Public API proposal

All routes are additive under `/api/v1`.

| Operation | Input and output |
| --- | --- |
| POST `/chat/sessions` | Optional investigation UUID/title → session UUID, creation and expiry times, privacy caveat |
| GET `/chat/sessions/{id}` | Session UUID → scoped session metadata or 404 |
| GET `/chat/sessions/{id}/messages` | Limit 1–100, offset ≥0 → stable created_at/UUID ordered history with citations and metadata |
| POST `/chat/sessions/{id}/messages` | Question 1–4000 chars → committed user/assistant pair with outcome and original citations |
| POST `/advisor/assessments` | Phase 5 scenario input → structured pillar observations, gaps, citations and provider metadata |

Session title is at most 200 characters. Provider timeout defaults to 10 seconds,
bounded by trusted settings. No automatic provider retry. POST message requests
are non-idempotent. A deliberate client retry can create a new exchange. Clients
should read history after an uncertain connection outcome before resubmitting.
Timeout/unavailable/abstention may be persisted as explicit outcome envelopes.
Malformed or invalid-citation answers fail without an exchange write.

## Approval requested

Approve the storage boundary, 24-hour access/retained-row privacy policy, additive
routes, body envelope and POST retry semantics, and authorize implementation and
isolated PostgreSQL verification for that scope. External scientific/consumer
acceptance remains pending evidence from the relevant owners.
