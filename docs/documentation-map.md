# Documentation map and source-of-truth order

Use this map before a new task. Do not read every document indiscriminately;
follow the route that matches the requested feature.

| Need | Start with | Then inspect |
| --- | --- | --- |
| Coding agent workflow | `../AGENTS.md` | This map, project status, Spec Kit artifacts when installed |
| Project purpose and local setup | `../README.md` | `runbooks/local-development.md` |
| Architecture, current 21-table ERD baseline, roadmap, baseline API proposals | `backend-implementation-plan.md` | `decisions/ADR-0003-schema-evolution-and-hackathon-prototype.md`, original D01–D15 `diagram/index.html` and actual source |
| Approved **physical** DB choices | `phase-2-database-implementation.md` | `../app/models/`, `../alembic/versions/`, tests |
| Implementation history | `phase-1-verification.md`, `phase-2-database-implementation.md` | `project-status.md` for current state |
| Team responsibilities and changes to Phase 3 | `team-ownership.md` | `decisions/ADR-0001-phase3-ownership.md` |
| Frontend integration | `contracts/frontend-backend-api.md` | Sibling frontend `src/types/index.ts`, actual pages/components |
| NASA data ingest/quality | `contracts/data-handoff.md` | D12–D13, evidence/catalog models |
| RAG, chatbot, prediction ownership | `contracts/ai-backend-interface.md` | D11/D14, chat/evidence/prediction models |
| Running and testing locally | `runbooks/local-development.md` | `runbooks/testing-and-release.md` |
| Phase 4 synthetic API delivery and evidence | `phase-4-api-verification.md` | `../specs/001-phase4-catalog-apis/verification.md` |
| Phase 4 isolated demo/seed | `runbooks/phase-4-demo-validation.md` | `../data/demo/README.md` |
| Phase 4 consumer and curated-data gates | `contracts/phase-4-frontend-handoff.md` | `contracts/phase-4-data-handoff.md` |
| Adopting Spec Kit | `runbooks/speckit-adoption.md` | `constitution-draft.md` |

## Source-of-truth precedence

1. **User-approved decisions and task scope.** New decisions that materially
   change schema or API contracts must be recorded explicitly.
2. **Current backend ERD baseline:** `diagram/index.html` D03–D05 defines the
   implemented logical relationships; ADR-0003 governs future evolution.
3. **Current physical schema baseline:** `phase-2-database-implementation.md`
   records the implemented mapping and applied migration history.
4. **Stable target requirements:** `backend-implementation-plan.md`.
5. **Live code and tests:** actual implemented behavior, not proof that all
   future requirements have been met.
6. **Frontend mock types and design plans:** integration consumers/reference;
   never authoritative for unverified scientific facts or DB schema.

When documents disagree, list the conflict and the proposed owner/decision.
Do not silently choose the most recent file, the prettiest UI, or a convenient
placeholder. Phase completion reports document past execution; they do not
override a new user-approved change.

For a new dataset, preserve the raw original and compare its fields, units,
quality flags, provenance and review meaning with the current baseline.
Prefer a lossless adapter and explicit contract. If a migration is justified,
review database/API/import/test/consumer impact and append a versioned Alembic
revision; never edit one already applied. The official hackathon dataset is
evaluated on arrival. Prototype engineering checks, real-data integration and
scientific validation remain separate evidence gates.

## Documentation update rules

- New feature: `specs/<feature>/` once Spec Kit is installed.
- New approved architecture/contract decision: brief ADR in `decisions/`.
- Actual delivery: focused `phase-*.md` record and `project-status.md` update.
- Stable README/architecture plan: modify only with approved scope change.
- Canonical diagrams: preserve `diagram/index.html`; `.mmd` downloads should mirror it.
- Historical Phase 2 and Phase 4 records describe their original scope; do not
  rewrite them to imply that a later schema policy was in force at that time.

The sibling frontend has old HTML diagrams and `docs/superpowers/` implementation
plans. Read them when necessary for UI compatibility, but explicitly label
them as **frontend historical/design references** in backend tasks.
