# Documentation map and source-of-truth order

Use this map before a new task. Do not read every document indiscriminately;
follow the route that matches the requested feature.

| Need | Start with | Then inspect |
| --- | --- | --- |
| Coding agent workflow | `../AGENTS.md` | This map, project status, Spec Kit artifacts when installed |
| Project purpose and local setup | `../README.md` | `runbooks/local-development.md` |
| Architecture, 21-table ERD, roadmap, baseline API proposals | `backend-implementation-plan.md` | Original D01–D15 `index.html` and actual source |
| Approved **physical** DB choices | `phase-2-database-implementation.md` | `../app/models/`, `../alembic/versions/`, tests |
| Implementation history | `phase-1-verification.md`, `phase-2-database-implementation.md` | `project-status.md` for current state |
| Team responsibilities and changes to Phase 3 | `team-ownership.md` | `decisions/ADR-0001-phase3-ownership.md` |
| Frontend integration | `contracts/frontend-backend-api.md` | Sibling frontend `src/types/index.ts`, actual pages/components |
| NASA data ingest/quality | `contracts/data-handoff.md` | D12–D13, evidence/catalog models |
| RAG, chatbot, prediction ownership | `contracts/ai-backend-interface.md` | D11/D14, chat/evidence/prediction models |
| Running and testing locally | `runbooks/local-development.md` | `runbooks/testing-and-release.md` |
| Adopting Spec Kit | `runbooks/speckit-adoption.md` | `constitution-draft.md` |

## Source-of-truth precedence

1. **User-approved decisions and task scope.** New decisions that materially
   change schema or API contracts must be recorded explicitly.
2. **Approved backend ERD:** `index.html` D03–D05 defines logical relationships.
3. **Approved physical schema mapping:** `phase-2-database-implementation.md`.
4. **Stable target requirements:** `backend-implementation-plan.md`.
5. **Live code and tests:** actual implemented behavior, not proof that all
   future requirements have been met.
6. **Frontend mock types and design plans:** integration consumers/reference;
   never authoritative for unverified scientific facts or DB schema.

When documents disagree, list the conflict and the proposed owner/decision.
Do not silently choose the most recent file, the prettiest UI, or a convenient
placeholder. Phase completion reports document past execution; they do not
override a new user-approved change.

## Documentation update rules

- New feature: `specs/<feature>/` once Spec Kit is installed.
- New approved architecture/contract decision: brief ADR in `decisions/`.
- Actual delivery: focused `phase-*.md` record and `project-status.md` update.
- Stable README/architecture plan: modify only with approved scope change.
- Canonical diagrams: preserve `index.html`; `.mmd` downloads should mirror it.

The sibling frontend has old HTML diagrams and `docs/superpowers/` implementation
plans. Read them when necessary for UI compatibility, but explicitly label
them as **frontend historical/design references** in backend tasks.
