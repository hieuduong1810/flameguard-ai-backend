# ADR-0003: Schema evolution and hackathon prototype evidence

- Status: Accepted by the project owner for architecture governance
- Date: 2026-11-12

## Context

The existing 21-table PostgreSQL ERD was designed and implemented for a public
NASA dataset prototype. The official hackathon dataset is expected on
November 14, 2026 and may have a substantially different structure. The
project needs a rule for evaluating it without losing scientific context or
rewriting previously applied migrations.

## Decision

- The 21-table ERD, current models and Phase 2 physical mapping are the
  implemented baseline, not an immutable final design.
- Preserve existing models and migrations unless actual source data or approved
  requirements justify a change. Prefer canonical data contracts, adapters and
  lossless transformations first. Never invent fields or scientific meanings
  to force incoming data into existing columns.
- A necessary schema change must be additive and use a new, versioned Alembic
  revision after impact analysis of database state, APIs, migrations, imports,
  tests and downstream consumers. Previously applied revisions must never be
  edited. Destructive migrations and shared-database resets require explicit
  human approval.
- Preserve source identity, original values and units, quality flags,
  provenance and review status. Keep the raw NASA dataset independently
  recoverable. Missing scientific data remains explicit rather than fabricated.
- Public NASA data is used for engineering rehearsal. Evaluate the official
  dataset on arrival. Engineering readiness, real-data integration readiness
  and scientific validation are distinct claims. Mock providers may support
  integration tests but must never masquerade as verified scientific outputs.

## Consequences and scope

Future Phase 3B contracts must record a field-level mapping, loss analysis,
identity and unit rules, source manifest, acceptance evidence and migration
decision before any import. Database and consumer changes need separate
implementation authorization. The original diagrams, Phase 2 report and
Phase 4 specification remain historical baselines for their delivered scopes;
this policy does not retroactively change them.

This ADR changes governance documents only. It does not authorize ETL,
application code, database migrations, data operations, Frontend changes,
model claims, deployment, commit or push.
