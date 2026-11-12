# FlameGuard AI Backend Constitution

## Core Principles

### I. Scientific Integrity and Research Purpose

FlameGuard AI MUST remain a research/evidence demonstration for NASA microgravity combustion.
Outputs MUST distinguish measured, modeled, inferred, preliminary/unreviewed, illustrative
and unknown information where applicable. Agents MUST NOT invent measurements, findings,
DOIs, citations, confidence scores, model validation or uncertainty bounds. Demo equations
and frontend fixtures MUST NOT become verified scientific data. The platform MUST NOT issue
unconditional safe/unsafe verdicts or operational spacecraft fire-safety certification.
Presentation quality is not evidence of scientific validity.

Public NASA datasets MAY be used for engineering rehearsal ahead of the
November 14, 2026 hackathon. The official dataset MUST be evaluated on arrival;
prototype compatibility is not proof of official-data compatibility. Engineering
readiness, real-data integration readiness and scientific validation MUST be
reported separately. Missing scientific data is acceptable and MUST be explicit.
Mock providers MAY support integration testing but MUST NOT masquerade as
verified scientific outputs.

### II. Existing Architecture and Coding Standards

Work MUST extend the existing FastAPI modular monolith, not recreate the project or replay
Phase 1-2. Python compatibility MUST follow `pyproject.toml`. Use typed Pydantic v2 schemas,
SQLAlchemy 2.x async sessions, asyncpg/PostgreSQL and Alembic. Routes own HTTP handling;
services/callers own business workflows and explicit transactions; repositories own queries
and flushes, not commits. Relationships MUST use explicit async-safe loading, not accidental
I/O. New abstractions, workers, frameworks or microservices require an approved concrete need.

### III. Schema Evolution and Original Data Preservation

The 21-table logical ERD in `docs/diagram/index.html` D03-D05 and physical mapping in
`docs/phase-2-database-implementation.md` are the current implemented baseline,
not an immutable final schema. Existing models MUST be preserved unless actual
source data or approved requirements justify a change. Previously applied
Alembic revisions, including `0001_must_have` -> `0002_should_have` ->
`0003_could_have`, MUST NOT be edited, removed, squashed or bypassed.
Prefer adapters, canonical data contracts and lossless transformations before
changing persistence. A necessary change MAY use an additive, versioned
Alembic revision after an explicit user-approved decision and impact analysis
for database, APIs, migrations, imports, tests and downstream consumers.
Review migration and rollback implications before coding. Destructive
migrations and shared-database resets require explicit human approval.

UUIDs, external `psi_id` and public/frontend slugs MUST remain distinct. Claim-document
provenance MUST remain many-to-many through `claim_source`; investigation-tag classification
MUST remain many-to-many through `investigation_tag`. Preserve the three chat tables.
Frontend fields alone do not authorize new columns, enum restrictions, redundant
FKs, credential fields or replacement numeric gravity/airflow columns. Agents
MUST NOT invent fields or scientific meanings to force incoming data into the
baseline. Preserve source identity, original values and units, quality flags,
provenance, review status and independent recoverability of the raw NASA dataset.

### IV. Explicit Team Ownership

Backend/Codex MUST own HTTP contracts, schemas, repositories, approved business services,
validation, persistence, integration adapters, backend tests and deployment integration.
Database changes remain approval gated. The Data Team MUST own NASA acquisition, datasets,
parsing, scientific normalization, data preparation, curation/review and import execution.
The AI Team MUST own retrieval/reasoning, answer composition, models/training/prediction,
grounding quality, uncertainty methodology and AI evaluation. The Frontend Team MUST own
Next.js UI, client adapters, browser state and frontend tests.

Codex MUST NOT independently implement another team's pipeline or edit the frontend.
Use contracts, explicit mocks and acceptance evidence across boundaries. ADR-0001's
Phase 3A Data / Phase 3B Backend compatibility-and-acceptance split MUST apply; a diagram's
logical ingestion or AI box does not reassign ownership.

### V. Contract-First API Development

Each bounded feature MUST define request/response examples, identity, nullability,
units/precision, pagination/order where relevant, errors, provenance, compatibility and
owner acceptance criteria before business implementation. PROPOSED/CONTRACT DRAFT documents
MUST NOT be treated as agreed interfaces, implementation permission or delivery evidence.
Public DTOs MUST be deliberate projections, not unreviewed exposure of internal ORM fields.

Slug resolution, telemetry serialization and numeric UI gravity/airflow mapping to approved
string fields require explicit decisions, not invented schema changes. Consumer-affecting
contracts MUST be agreed with affected teams and checked with contract tests. Route
availability MUST be demonstrated by code, OpenAPI and executed verification, not roadmap
tables or mock screenshots.

### VI. Evidence Provenance and Scientific Caveats

Scientific responses MUST preserve original document IDs, source URLs, available DOIs,
exact locators, available excerpts, original conditions/measurements/units, uncertainty,
review context and relevant source associations. Unknown/null MUST NOT become zero, a
nominal condition, measured false or an unverified universal claim of absent research.
Foreign-key integrity and publication-looking metadata do not establish scientific review.

Relevance MUST NOT be described as fire-risk probability. Combined coverage MUST use
compatible conditions within a relevant test run, not unrelated catalog-wide ranges.
AI responses MUST provide validated original-source citations or explicit abstention/gaps.
Numeric predictions require AI-owned validated artifacts, versioned training/evaluation
evidence, applicability checks and defensible uncertainty. Missing prerequisites MUST yield
the agreed unavailable/not-validated behavior, never fabricated scientific outputs.

### VII. Executed, Proportionate and Safe Verification

Verification MUST match the changed behavior and accepted criteria. Behavior changes MUST
include meaningful success/failure tests and relevant identity, provenance, unit, null and
contract cases using pytest, pytest-asyncio, HTTPX and Ruff. Distinguish mock, in-process API,
real PostgreSQL, real provider/scientific evaluation and frontend integration evidence.

Database-writing tests MUST use separately approved test-named PostgreSQL targets and the
existing isolation/rollback safeguards. Development/shared research data MUST NOT be reset,
truncated or overwritten for testing. Understand fixture database creation/retention before
running it; cleanup needs separate exact-target authorization. Reports MUST state actual
commands, outcomes, counts, skips and unavailable checks. Written tests, historical passes
and mock results MUST NOT be presented as newly executed or end-to-end verification.

### VIII. Poetry-Owned Dependency Management

Poetry MUST remain the backend dependency/environment manager, using non-package mode,
the in-project `.venv/`, runtime/development dependency groups and a consistent `poetry.lock`.
Project execution MUST use `poetry run`. Backend dependencies MUST NOT move to global
installs, requirements.txt or uv because Spec Kit's separate CLI uses another installer.
Dependency changes MUST be scoped, justified, locked and verified. Local credentials and
environment files MUST remain private.

### IX. Stable Documentation and Honest Status

README and `docs/backend-implementation-plan.md` MUST remain stable baselines, edited only
for explicit user-approved requirement, contract, architecture or roadmap changes.
Preserve `docs/diagram/index.html` unless an architecture revision is authorized; diagram exports
MUST NOT become a competing authority. Phase records preserve execution history;
`docs/project-status.md` tracks genuine delivery state. Contracts MUST state proposed/agreed
status, and material approved deviations MUST have decision records. Preserve the Phase 2
mapping record's path/structure while tests depend on it. Assigned owners, empty tables,
mock responses and target-feature lists MUST NOT be reported as completion evidence.

### X. Git Workflow and Change Management

Tasks MUST begin with scope and Git-status inspection and preserve unrelated/uncommitted
work. Agents MUST NOT reset/clean existing changes, replace the repository or alter unrelated
projects. Commits, pushes, deployment, paid-provider use, production migrations and destructive
data operations require applicable user authorization; do not broaden one approval into
unrelated actions. Secrets, `.env`, `.venv/` and local tools MUST NOT be committed. Review the
diff, scope, compatibility and verification evidence before representing a change as done.

### XI. Spec-Driven Delivery

All future feature development MUST follow Specify -> Clarify when necessary -> Plan ->
Tasks -> Analyze consistency -> Implement -> Test -> Converge. Analysis/planning MUST NOT
be treated as implementation approval or completion. Implement only with applicable feature
authorization, accepted material decisions and satisfied gates. Use documented defaults for
routine choices within approved scope without redundant approval requests.

Feature artifacts MUST follow installed Spec Kit conventions under `specs/<feature>/`.
Do not invent retrospective specs for completed Phase 1-2. Invoke installed `$speckit-*`
skills in Codex chat, not as shell commands. Report absent/failing integration honestly and
use only a permitted documented fallback. The gates below apply despite generic boilerplate.

### XII. Definition of Done

A bounded delivery MUST meet its accepted criteria, owned scope, contract/scientific gates,
consistency analysis, required executed verification and reviewed diff before being called
done. Each criterion MUST have identifiable evidence. Required missing/failed checks prevent
an unqualified completion claim. Handoffs MUST name what works, blocked items, owners and
next actions. A completed synthetic adapter/contract slice MUST NOT imply real ingestion,
AI validation, frontend rollout or overall phase completion. Apply the checklist below.

### XIII. Cross-Team Dependencies and Escalation

Each dependency MUST identify owner, input artifact, output/interface, acceptance criteria
and readiness/blocking evidence. Within an authorized feature, Backend MAY prepare owned
contracts, clearly synthetic fixtures and unavailable-provider adapters. It MUST NOT invent
upstream data or implement AI/Data/Frontend work independently to hide missing handoffs.

Escalate material schema/migration, identity/API, authentication/privacy, scientific/domain,
ownership, deployment cost/risk and permission decisions to the user and affected owner.
Report the exact blocker, affected files/contract, safe options, trade-offs and recommendation.
Block only dependent actions and continue independent authorized work. Do not bypass
permission denials or scientific evidence gates.

## Operational Boundaries and Engineering Standards

- Work MUST remain in the existing backend. The sibling frontend is a read-only reference
  unless its owner explicitly authorizes the requested edit.
- Liveness MUST be independent of database availability. Readiness MUST be bounded;
  engine/session cleanup MUST follow the existing application/request lifecycle.
- Configuration MUST remain environment driven. Failures MUST be sanitized; credentials,
  connection strings, provider keys and internal stack traces MUST NOT leak. Production
  debug MUST be disabled and production CORS MUST use explicit allowed origins.
- No login or guest credential is approved for the demo. Opaque browser-held session IDs
  provide continuity, not authenticated ownership/privacy. Session creation, history,
  retention and errors require agreed AI/Backend/Frontend contracts; do not infer new identity
  or credential fields. Preserve `chat_session`, `chat_message` and `message_citation`.
- Before an authorized migration/import, confirm target, revision/state, approved scope and
  rollback implications. Do not automatically upgrade/downgrade/stamp, drop/truncate, delete
  volumes or remove test databases as troubleshooting. Startup table creation MUST NOT
  replace Alembic. Documentation-only work MUST NOT launch Docker or alter database state
  merely to satisfy a checklist.
- Data acceptance MUST check identity, units/vocabulary, nulls, duplicates, review meaning,
  original assets and claim/document/run context. Shared/development imports need separately
  approved execution; Backend acceptance does not transfer Data pipeline ownership.
- AI interfaces MUST cover versioned input/output, known source IDs/locators, abstention and
  unsupported/unavailable states, latency/errors, grounding evaluation and prediction domain/
  uncertainty. Backend mock acceptance does not validate AI or authorize algorithm development.
- Phase 3 is an external Data handoff plus Backend compatibility/acceptance boundary.
  A Constitution update is not permission to implement ingestion or another feature.

## Spec-Driven Workflow and Delivery Gates

### Feature Lifecycle

Record entry evidence, deliverables, verification and exit decision at each stage. Clarify
MAY be skipped only with a record that no material question remains. Analyze precedes
implementation; Test is AGENTS.md's Verify step; Handoff is part of Converge. Spec Kit
plan-template research/design phases are feature-local, not a replay of project Phase 1-2.

| Stage | Entry criteria | Deliverables | Verification | Exit criteria |
| --- | --- | --- | --- | --- |
| Specify | Bounded user outcome; repository/status/ownership context read | `spec.md`: scope/non-goals, stories/examples, acceptance criteria, explicit testing, science/privacy constraints and dependencies | Compare with Constitution, AGENTS.md, ERD and contract status | Reviewable scope, material unknowns named; no implementation |
| Clarify when necessary | Spec and material ambiguity/conflict | Recorded owner answers/approved decisions; authorized contract/ADR updates, or no-clarification-needed record | Check schema, identity, science, security, ownership and consumers | Blocking choices resolved; otherwise dependent action blocked without guessing |
| Plan | Bounded spec and necessary decisions | `plan.md`: existing-layer reuse, DTOs, queries/loading, transactions, adapters/errors, tests, rollback and Constitution Check | Check ownership, contracts, schema, permissions and science before research and after design | Feasible owned approach, explicit dependency/approval gates; no inferred coding permission |
| Tasks | Consistent spec and plan | `tasks.md`: reviewable ordered contract, implementation, test, docs and verification tasks with criteria/done references | Trace every accepted criterion to tasks/evidence; include required tests explicitly | No uncovered requirements; work order and blocked dependencies clear |
| Analyze consistency | Spec, plan, tasks and relevant contracts exist | Findings with requirement/owner references and dispositions | Check contradictions, gaps, scope, provenance, schema/API drift and Constitution compliance | No unresolved violation/material blocker affects implementation slice |
| Implement | Applicable feature authorization, decisions and preceding gates satisfied | Owned, scoped implementation and associated tests/docs | Compare diff with approved artifacts; inspect async, transactions, errors, provenance and compatibility | Planned slice implemented without hidden scope expansion; not yet declared complete |
| Test / Verify | Implemented slice and authorized test environments | Exact commands, outcomes/counts/skips and acceptance evidence | Run relevant lint/format/unit/API/integration checks; distinguish mocks, real providers/data and missing environments | Required checks pass; required failed/unavailable checks remain explicitly blocked |
| Converge / Handoff | Implementation, verification and accepted artifacts | Criterion-to-evidence assessment; remediation tasks or scoped completion report/status/phase record | Compare spec-plan-tasks-code-contracts-Constitution, review diff and dependency owners | No actionable gap remains and DoD met; otherwise return to approved tasks/implementation and repeat |

### Constitution Check and Completion Checklist

Plans and consistency reviews MUST check: research integrity; justified schema
evolution and immutable applied revisions; lossless source/contract mapping;
ownership; agreed contract/identity/unit/null semantics; async layers/transactions; Poetry;
safe test targets; secret/auth/CORS constraints; documentation and scope authorization.
Violations require reported remediation or an explicit approved governance/requirement
change; a generic complexity-justification table cannot waive Constitution rules.

A delivery is done only when all applicable items have evidence:

- Accepted criteria map to implemented files and executed verification.
- Spec, plan, tasks, contracts and code agree; Analyze/Converge gaps are closed.
- Schema/history, original diagrams, unrelated work and ownership boundaries are preserved,
  except for specific authorized changes with decision/migration records.
- Relevant success/failure, identity, units, null, provenance and integration checks pass;
  non-applicable/skipped checks are explained and required missing checks remain blocked.
- Scientific/demo/provider limitations and cross-team acceptance are stated accurately,
  without inflated claims of validation, end-to-end delivery or project-wide completion.
- Diff review covers secrets, compatibility and unintended changes. Delivery/status records
  reflect actual outcomes; stable baselines are not progress logs.
- Handoff names files, verification, authorized data/migration effects, unfinished owners
  and next action. Commit, push and deployment remain separately authorized.

## Governance

This is the first populated Constitution, version 1.0.0, established from the user's
2026-11-10 request and approved project context. The preparation draft is input, not a
previous ratified version. This document governs Spec Kit work within existing project
authority; it MUST NOT silently override AGENTS.md, user scope or approved schema/ownership.

The owner-directed 2026-11-12 amendment changes Principle III from finalized
schema preservation to reviewed schema evolution and expands Principle I with
hackathon prototype evidence rules. Version 2.0.0 marks this material principle
redefinition. ADR-0003 records the rationale, impact gates and limits. The
amendment changes governance only; it authorizes no feature implementation,
data import, migration execution or scientific validation claim.

Use `docs/documentation-map.md` precedence: explicit user-approved decisions/scope;
current logical ERD baseline; current physical mapping; stable requirements; live code/tests as
behavior evidence; frontend mock types/design as consumer reference only. AGENTS.md supplies
repository operating instructions. Draft contracts are not approved decisions. When sources
conflict, report exact statements, owner, impact and needed decision; stop affected work
rather than silently selecting the newest file or convenient interpretation.

Amendments MUST record rationale, affected principles/contracts, compatibility/migration
implications, applicable owner/user approval and follow-up scope. Review against AGENTS.md,
source precedence, ownership and existing architecture/schema. Version by MAJOR for
incompatible principle removal/redefinition, MINOR for added/materially expanded guidance,
and PATCH for non-semantic clarification. Preserve original ratification; set Last Amended
to the amendment date in YYYY-MM-DD format. Routine phase completion is not an amendment.

Feature plans/reviews MUST check compliance, and Converge MUST recheck it. Templates/skills
consume this document at runtime; generic examples do not authorize project reinitialization,
schema invention, skipped required tests or cross-team implementation. Adoption/amendment
does not itself authorize code, schema, data, template, commit, deployment or paid-service work.

### Reconciliation Items and Unresolved Interfaces

- The project tasks template requires proportionate tests for behavior changes. Documentation-only
  changes may use link/content verification with an explicit rationale. The local workflow includes
  manual Clarify, Analyze, Test and Converge gates; approval requires recorded evidence, not a
  claim that the workflow automatically executed those checks.
- Spec Kit is installed under `.agents/skills/` and `.specify/`. The adoption runbook distinguishes
  the current installation from recovery instructions; do not repeat initialization by default.
- D01/D02 retain React/Vite labels, while the frontend reference is Next.js. A diagram
  correction is a project-owner decision; neither frontend rewrite nor diagram edits are
  authorized here. Preserve backend architecture and the consumer boundary.
- Slug identity, Data format/unit/status/review vocabulary, telemetry assets and AI/provider/
  streaming/demo-session contracts remain proposed/open in their source documents. Adoption
  MUST NOT invent values or team sign-off. Owner/user agreement and acceptance criteria gate
  their dependent implementation, not establishment of this governance baseline.
- The original ERD and Phase 2 mapping remain historical and implemented baselines.
  ADR-0003 governs future schema evolution; it does not retroactively revise Phase 2
  evidence or authorize a Phase 3B import, migration or official-dataset claim.

The initial baseline was prepared for commit on 2026-11-11 with user-authorized diagram
relocation and template/workflow alignment; see
[adoption decision](../../docs/decisions/ADR-0002-speckit-adoption-and-diagram-location.md).
These changes preserve scientific, schema and ownership requirements.

### Source References

- [Repository instructions](../../AGENTS.md), [project guide](../../README.md),
  [dependency configuration](../../pyproject.toml).
- [Documentation map](../../docs/documentation-map.md),
  [status index](../../docs/project-status.md),
  [preparation draft](../../docs/constitution-draft.md).
- [Architecture/roadmap](../../docs/backend-implementation-plan.md),
  [original diagrams/ERD](../../docs/diagram/index.html),
  [Phase 1 evidence](../../docs/phase-1-verification.md),
  [physical schema and Phase 2 evidence](../../docs/phase-2-database-implementation.md).
- [Team ownership](../../docs/team-ownership.md),
  [accepted Phase 3 ownership ADR](../../docs/decisions/ADR-0001-phase3-ownership.md).
- [Frontend contract draft](../../docs/contracts/frontend-backend-api.md),
  [Data handoff draft](../../docs/contracts/data-handoff.md),
  [AI interface draft](../../docs/contracts/ai-backend-interface.md).
- [Local development](../../docs/runbooks/local-development.md),
  [testing/release](../../docs/runbooks/testing-and-release.md),
  [Spec Kit adoption context](../../docs/runbooks/speckit-adoption.md).
- [Schema evolution and hackathon prototype policy](../../docs/decisions/ADR-0003-schema-evolution-and-hackathon-prototype.md).

**Version**: 2.0.0 | **Ratified**: 2026-11-10 | **Last Amended**: 2026-11-12
