# Team ownership and collaboration contract

Approved project decision: the user owns Backend/Codex delivery and the Data
team owns NASA scientific ingestion/import. The AI team owns AI algorithms and
validation; the Frontend team owns Next.js integration. This document prevents
duplicate implementations and accidental work across repositories.

## Responsibility matrix

| Work | Backend / Codex | Data team | AI team | Frontend team |
| --- | --- | --- | --- | --- |
| FastAPI routes, HTTP errors, DTOs, transaction management | **Owner** | Consult | Consult | Consumer |
| PostgreSQL models and Alembic changes | **Owner (approval required)** | Schema stakeholder | Schema stakeholder | Consumer |
| NASA source discovery, DOI/URL verification, ingest execution | Contract/acceptance | **Owner** | Consult | No |
| Original units, scientific normalization, missing values | Validate contract | **Owner** | Consult | Consumer |
| Source/claim provenance and review records | Persistence/constraints | **Owner of curation** | **Owner of grounding behavior** | Display |
| Dashboard, catalog, comparison endpoints | **Owner** | Curated dataset | Consult | **Owner of UI adapter** |
| Scenario similarity/gap run-level persistence | **Owner of API/logic agreed with scientific reviewers** | Test-run evidence | Scientific review | UI |
| Chat session/message/citation persistence | **Owner** | Source records | RAG results | Session browser state |
| Retrieval, grounding, response composition, model evaluation | Adapter/persistence | Curated corpus | **Owner** | Display |
| Predictive model, training, model-domain/uncertainty evidence | Gate/adapters | Validated dataset | **Owner** | Readiness UI |
| Next.js state, route handling, frontend tests | Contract consultation | No | No | **Owner** |
| Backend deployment, DB migration, server secrets | **Owner** | Data access collaboration | Provider configuration collaboration | Vercel integration |

## Definition of an acceptable Data team handoff

See `contracts/data-handoff.md`: origin/source manifest, field mapping,
units/vocabulary, stable identifiers, curator approval, missing/uncertain data,
deduplication policy, original artifact references, ingestion repeatability,
validation report and explicit open issues. A database row with a URL is
**not** proof that the scientific claim is verified.

Backend may test the import output and ask for corrections but must not
rebuild the whole Data pipeline unless a separately scoped task is approved.

## Definition of an acceptable AI team handoff

See `contracts/ai-backend-interface.md`: validated input/output schema, source
citations with original document IDs and locators, refusal/evidence-gap
behavior, model or prompt version, latency/error modes, scientific evaluation,
and — for predictions — validated applicability and uncertainty methodology.

Backend may add provider adapters/stubs that return **unavailable** when the
team's real integration is absent. It must not imitate a grounded scientific
answer using invented citations, or label a demo equation as a validated model.

## Frontend integration boundaries

- Backend owns `api/v1` JSON contracts; Frontend owns all page/component changes.
- The current frontend `Investigation.id` is a slug, not the database UUID.
- Current frontend store keeps chat in memory; session persistence is a future
  integration feature, not a delivered Phase 2 behavior.
- Public frontend variables may hold only the backend base URL, never secrets.
- Changes affecting both teams require an agreed API example and contract test.

## Escalation rules

Codex may make routine implementation choices within approved contracts. It
must ask the user (or report a blocking cross-team dependency) before:

1. Changing the frozen ERD, relationship cardinality or migration strategy.
2. Redefining public UUID/slug/PSI mapping or removing source provenance.
3. Claiming scientific validation, changing model applicability, or issuing
   safety guidance.
4. Adding authentication, credentials or per-user account flows.
5. Editing the frontend repo or taking over Data/AI team responsibilities.
6. Deploying, pushing, running production migrations, using paid APIs or
   doing any destructive data operation.

Every handoff must name the owner, input artifact, output artifact, acceptance
criteria and readiness/blocking status. Do not count a dependency as complete
just because another team is assigned to it.
