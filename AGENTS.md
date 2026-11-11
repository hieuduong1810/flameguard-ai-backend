# FlameGuard AI backend — instructions for Codex and coding agents

These instructions apply to the **backend repository only**. The sibling
`../FlameInFreewall_Tourbillion/` repository is a read-only integration reference
unless its owner explicitly authorizes edits. This is an existing project;
**do not initialize a new FastAPI app, rebuild the database, or replay Phase 1–2**.

## 1. Start here on every task

1. Inspect `git status --short` and the user's requested scope. Preserve unrelated
   or uncommitted changes; never reset, clean, or overwrite them.
2. Read `docs/project-status.md` and `docs/documentation-map.md`.
3. Read the relevant portions of `README.md`,
   `docs/backend-implementation-plan.md`, and the latest phase record.
4. For a database/feature task, inspect the relevant D01–D15 diagram source in
   `docs/diagram/index.html`, the SQLAlchemy models, Alembic revisions, and existing tests.
   Read only the diagrams needed for that task; do not load all diagrams by default.
5. For external boundaries, read `docs/team-ownership.md` and the corresponding
   `docs/contracts/` document. Inspect the sibling frontend's actual components,
   stores, and TypeScript types **read-only**; mock types are not database authority.
6. Confirm whether Spec Kit's `$speckit-*` skills are installed. If not, use the
   manual workflow below and report the missing integration. Never pretend a
   skill or validation ran when it did not.

## 2. Fixed product and architecture constraints

- Research/evidence **demonstration**, not operational spacecraft fire-safety
  certification. Never return an unconditional safe/unsafe verdict.
- Existing architecture: FastAPI, Python, Poetry, SQLAlchemy 2.x async,
  asyncpg/PostgreSQL, Alembic, Pydantic v2, pytest/HTTPX, Ruff; modular monolith.
- The **21-table approved ERD** in `docs/diagram/index.html` and approved physical mapping
  in `docs/phase-2-database-implementation.md` are authoritative. Migrations
  `0001_must_have` → `0002_should_have` → `0003_could_have` exist. Do not invent
  new columns, FK relationships, enum restrictions, or alter migration history
  to satisfy an unapproved frontend display field.
- Internal UUID, external `psi_id` and frontend/public slug are **different IDs**.
  Resolve the mapping explicitly before implementing a detail endpoint.
- Source links, DOI, source locators, original measurements/units/uncertainties,
  unknown/null values, and claim↔source many-to-many relationships must survive
  API projections. A missing measurement is not zero.
- Relevance scores are not fire risk probabilities. Combined scenario coverage
  must be supported by compatible values **within the same test run**, not by
  separate catalog-wide parameter ranges.
- Never turn frontend demo arrays, hard-coded model labels, or invented intervals
  into verified NASA data or validated predictive model results.
- No login or guest credential is approved for this demo. Retain the existing
  three chat tables. A browser-held opaque session identifier is only a demo
  continuity mechanism; it does not provide real user authentication/privacy.
- Keep settings/secrets on the backend; do not expose API keys, DB credentials,
  internal stack traces, or unrestricted production CORS.

## 3. Ownership boundaries

Read `docs/team-ownership.md` before assigning work. In short:

- **Backend + Codex:** HTTP contracts, ORM, migrations after approval,
  repositories, business services, validation, persistence, integration adapters,
  backend tests, and deployment integration.
- **Data team:** NASA source acquisition, source/DOI checking, parsing, scientific
  unit normalization, curation/review, and import execution. Backend owns the
  acceptance tests and compatibility of the agreed handoff, not a replacement
  data pipeline.
- **AI team:** RAG retrieval/answering quality, model training and prediction,
  scientific grounding/uncertainty and AI evaluation. Backend exposes/persists
  versioned interfaces; it must not invent AI algorithms or claim verification.
- **Frontend team:** Next.js UI, integration client/adapters, local chat session
  continuity and frontend tests. Read-only reference for backend tasks.

When work crosses team boundaries, create/adjust a **proposed contract** and
report the owner and dependency; do not silently implement another team's scope.

## 4. Feature development workflow — mandatory

For each bounded feature, follow this order. Spec Kit, when installed, provides
`$speckit-specify`, `$speckit-clarify`, `$speckit-plan`, `$speckit-tasks`,
`$speckit-analyze`, `$speckit-implement`, `$speckit-converge` (and constitution
setup). Invoke these in **Codex chat**, never as shell commands.

1. **Specify:** State user outcome, scope/non-goals, inputs/outputs, examples,
   acceptance criteria, safety/provenance requirements, and team dependencies.
   No implementation yet. Use `specs/<feature>/spec.md` after Spec Kit setup.
2. **Clarify:** Compare against current code, ERD, API and data contracts. Resolve
   routine choices using documented defaults. Ask the user only for choices
   affecting schema, API compatibility, security, scientific claims, ownership,
   deployment cost/risk, or other material requirements.
3. **Plan:** Choose existing layers, DTOs, queries, transaction ownership,
   external adapters, error semantics, test plan, and rollback strategy where
   relevant. Explicitly identify blockers from Data/AI/Frontend teams.
4. **Tasks:** Break into reviewable, dependency-ordered tasks. Include contract,
   implementation, tests, docs and verification tasks. Give each clear done criteria.
5. **Analyze:** Check spec–plan–tasks consistency and existing contracts before
   coding. Stop on incompatible decisions; do not silently add columns or fake data.
6. **Implement:** Modify only owned backend files needed by the approved task.
   Use Poetry and existing idioms; services own transactions, repositories flush
   but do not commit. Write tests for behavior, failures, provenance and units.
7. **Verify:** Run relevant checks in §5, inspect Git diff and record exact
   results. Never substitute a test written but not executed for a passing test.
8. **Converge:** Compare every acceptance criterion with demonstrable evidence,
   create tasks for gaps and repeat until done or blocked. Report missing test
   environments or upstream data honestly. A single green unit test is not E2E.
9. **Handoff:** Summarize changed files, what is working, test commands/results,
   what is blocked, team handoffs, migrations (if any), and recommended next task.
   Keep `docs/project-status.md` current for genuine delivery state only.

Do not generate full retrospective Spec Kit specs for Phase 1–2. Their existing
phase reports already record the completed foundation. Begin a new spec for
the **next bounded approved change**.

## 5. Verification and safe database behavior

Run from the backend repository root:

```powershell
poetry check
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -q
```

The default test suite can skip PostgreSQL-dependent tests. A real DB pass is
only proven when `TEST_DATABASE_URL` points to a separately approved,
disposable **test-named** PostgreSQL target with the role required by existing
fixtures. Follow `docs/runbooks/testing-and-release.md` before executing it.

- Inspect migrations and the selected database URL before an upgrade.
- Do not run `alembic upgrade`, downgrade, stamp, drop/truncate, remove Docker
  volumes, or delete test databases as an automatic troubleshooting step.
- Never run write/destructive tests on the development or shared research DB.
- Do not commit/push, deploy, buy services or touch secrets without user approval.
- Do not change `docs/diagram/index.html` without an approved architecture revision.

## 6. Documentation change policy

- `README.md` and `docs/backend-implementation-plan.md` are **stable baselines**;
  change only for explicit approved requirements/contracts/roadmap changes.
- `docs/diagram/index.html` is the original approved design. Standalone `.mmd` files,
  where provided, are faithful exports for download, not a separate authority.
- `docs/phase-*.md` record delivery/evidence, not speculative completion.
- `docs/contracts/` distinguish **proposed** from **agreed** contracts; no
  interface becomes final merely because it appears in a document.
- `docs/decisions/` records material approved deviations from the baseline.
- Keep past Phase 2 record in place: tests currently read its physical mapping.

## 7. What to do when blocked

Give the user: (a) exact blocker, (b) files/contract affected, (c) safe options
and trade-offs, (d) recommendation. Stop only the blocked action. Continue
other approved, non-destructive tasks when independent. Never bypass permission
denials or scientific evidence gates.
