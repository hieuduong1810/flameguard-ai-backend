# Phase 5 team handoff

The Backend-owned engineering contract is available at [HTTP examples](contracts/http.md), [runtime OpenAPI](contracts/openapi.json) and [provider contracts](contracts/providers.md). The selected operation is POST /api/v1/mission/scenarios/evaluate. See [verification](verification.md) for executed commands, counts, criterion-to-test evidence and protected baselines.

## Acceptance still needed

| Task | Owner | Input and required output | Effect |
| --- | --- | --- | --- |
| T056 | Data with Backend | Official dataset and original source inventory → stable dataset, UUID/PSI/slug/external identity mappings and recoverable originals, tested for collisions and drift | Real-data integration remains pending |
| T057 | Data and scientific reviewers | Variable/unit/quality dictionary and run policy → accepted compatibility/review decisions, tolerances, supported scope and same-run corpus | Scientific matching remains unavailable |
| T058 | Data | Versioned ranking export/service → accepted complete examples, identities, score semantics, ties and scope/version failure corpus | Real ranking activation remains pending |
| T059 | Data | Reviewed facts/classification/source mappings → complete provenance, review and mismatch/empty examples | Real pillar evidence remains unavailable |
| T060 | Frontend | HTTP/OpenAPI/replay examples → named reviewer, date, scope and actual client acceptance results | Frontend consumer acceptance remains pending |
| T061 | Data and Frontend | Selected comparison context, accepted scientific eligibility and additive client contract | P5-07 enrichment is deferred |
| T062 | Backend owner | Compatible write target and access/lifecycle requirements → storage impact and writer binding decision | Runtime scenario history and unsupported fields remain blocked |

Phase 4 T078 still requires its own Frontend acceptance evidence. Backend verified the additive contract and existing read behavior with HTTPX and PostgreSQL. AI has no Phase 5 provider deliverable. The bounded next handoff is for Frontend to exercise the contract examples and for Data to deliver the official versioned compatibility corpus.

Scenario storage supports a complete representable subset in the existing table through a trusted transaction. Exact catalog admission uses a SELECT-only role and every declared table. A runtime writer needs a compatible target and lifecycle decision. See [storage mapping](data-model.md).

## T062 foundation for Phase 6

Phase 6 planning must separate immutable scientific collection admission from
mutable runtime application persistence. Scenario history, chat sessions and
messages need a writer and lifecycle that can evolve independently of admitted
scientific snapshots. T062 remains blocked until the Backend owner accepts the
write target, role/access boundaries, retention and transaction ownership, and
reviews effects on existing catalog admission and readers. Choose the physical
storage layout and any justified migration through that impact review. This
handoff records the architectural boundary for later planning.

## Execution evidence

The YAML run `e9cf56f8` failed during reconciliation after a 300-second prompt
timeout. Authorized Phase 5 implementation, verification and three convergence
reviews completed independently through Codex CLI. The
[engineering report](engineering-report.md) records the executed checks and
keeps the failed workflow status visible.

TEST_ONLY records remain synthetic/unreviewed. Claim and association DTOs preserve repeated documents, locators, excerpts and optional run context. Original measurements and uncertainty remain available via the Phase 4 observations APIs. The isolated verification fixtures provisioned fresh retained resources with existing Alembic revisions.
