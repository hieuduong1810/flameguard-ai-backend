# Proposed FlameGuard AI constitution for Spec Kit

**Preparation artifact, not the generated Spec Kit constitution.** After
installing Spec Kit in the backend repo, use `$speckit-constitution` in Codex
to populate `.specify/memory/constitution.md` from these principles and the
actual repository. Review the generated constitution before feature work.

## Principle I — Research truth over impressive demos

Always distinguish measured, modeled, inferred, unreviewed, illustrative and
unknown results. Every scientific assertion requires traceable source
evidence, original citation locator and review context. No fabricated NASA
measurements, model validation, DOI or certainty. Never certify spacecraft
fire safety with this research demo.

## Principle II — Approved data model and provenance

Respect all 21 ERD entities and physical mapping decisions in the Phase 2
record. Preserve UUID/PSI/slugs as distinct IDs; preserve original units and
uncertainty. Claim↔source is many-to-many through `claim_source`. Any schema
change needs an explicit reviewed decision and migration/rollback plan.

## Principle III — Small vertical slices and stable contracts

Use a modular FastAPI monolith with strict API/schema/service/repository
responsibilities. Specify acceptance criteria, finalize versioned public
DTOs with consumers, then implement the smallest end-to-end backend slice.
No premature abstraction or new microservice without approved need.

## Principle IV — One owner per responsibility

Data team owns NASA ingest/curation; AI team owns retrieval/models and their
validation; Frontend owns Next.js; Backend owns API/persistence/integration.
Cross-team outputs require written contracts and acceptance gates, not
duplicate implementations or silent assumptions.

## Principle V — Tests must be real and safe

Use Poetry, Ruff, pytest and HTTPX. DB writes/tests use isolated test DBs;
never reset shared data. Report tests as passed only when actually executed;
record skips, scientific gaps and unavailable dependencies. Inspect migration
SQL and obtain approval before an operation affecting persisted data.

## Principle VI — Scope control and transparent handoff

For nontrivial features, follow specify → clarify → plan → tasks → analyze →
implement → verify → converge. Respect uncommitted work. Do not edit the
frontend, alter frozen diagrams, push/deploy, use paid providers, change auth,
or widen scope without explicit permission. Update status and handoff notes
from demonstrable evidence, not aspiration.

## Status and versioning

This draft reflects the user's approved project context on 2026-11-10.
Constitution version/ratification metadata must be supplied by the installed
Spec Kit template and reviewed before adoption; do not forge approval dates
or claim a generated constitution exists before installation.
