# Phase 6 handoff

The owner approved storage, privacy, API and implementation scope on 2026-11-13.
See [contracts](contracts.md), [OpenAPI](openapi.json),
[runtime setup](runtime-operations.md) and [verification](verification.md).

Backend supplies persistent public-demo sessions/messages, atomic citation
storage, detached RAG/Advisor interfaces, explicitly labeled mocks, timeout,
abstention and sanitized failures. The same-database runtime writer preserves
existing source/investigation FKs with a versioned scientific admission boundary.

T062's foundational chat boundary is accepted and implemented through ADR-0004.
Phase 5 scenario-history runtime writes and other mutable table groups remain
subject to a separately scoped lifecycle/writer decision.

| Task | Owner | Outstanding acceptance |
| --- | --- | --- |
| T018 | AI and Data | Real provider, reviewed corpus, retrieval/grounding evaluation, approved source/review semantics and model/corpus versions |
| T019 | Frontend | Session privacy/lifetime/retry handling, API client adaptation and executed consumer acceptance |

Phase 5 T056–T060 remain pending, T061 remains deferred and Phase 4 T078 remains
open. Retained PostgreSQL test databases/roles require exact-target cleanup
authorization. Operator runtime configuration needs the approved grants and v2
manifest. Public research content and redacted access logs are required by the
accepted privacy policy.
