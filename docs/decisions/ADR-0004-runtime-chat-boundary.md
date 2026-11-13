# ADR-0004 Runtime chat and scientific collection admission

Accepted by the project owner on 2026-11-13 through approval of the
[Phase 6 material decision proposal](../../specs/phase6-rag-advisor/approval.md).

The scientific catalog remains an immutable admitted collection. Mutable chat
uses its three existing tables in the same PostgreSQL database with a separate
INSERT-limited runtime role and separate engine. Existing source/investigation
foreign keys remain effective. V2 admission explicitly excludes exactly those
three tables from scientific row membership/fingerprints and requires empty
runtime manifest arrays. The remaining 18 tables keep exact validation. V1
admission continues checking all 21 tables.

Effective permissions and same-target identity checks gate runtime requests.
Services own atomic message/citation transactions. Providers run on detached
context outside those transactions. Session-level advisory locks serialize
exchange commits and session expiry is rechecked before writes.

This accepts T062's foundational boundary and enables Phase 6 chat persistence.
Phase 5 public scenario-history activation and other mutable tables require
their own writer/lifecycle scope. Existing migration revisions and ORM models
require no changes for this decision.

Privacy follows the approved public-demo session policy, 24-hour access lifetime,
retained rows pending operator cleanup, and explicit non-idempotent POST sends.
The [operator runbook](../../specs/phase6-rag-advisor/runtime-operations.md)
records grants, v2 configuration and rollback implications.
