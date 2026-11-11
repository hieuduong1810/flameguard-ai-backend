# Spec Kit adoption and diagram relocation verification

Date: 2026-11-11. Scope authorized by the project owner: repair diagram paths,
resolve the adoption audit findings, commit and merge into local main.
See ADR-0002 for the decision and preserved boundaries.

## Changes verified

- Canonical HTML is now `docs/diagram/index.html`; all 15 Mermaid downloads remain
  alongside it. HTML bytes match the previous committed source. Mermaid content
  matches after newline normalization and matches each embedded HTML diagram.
- Documentation, ERD-reading tests and export script use the relocated path.
- ADR-0001 and the preparation constitution draft are retained.
- The Constitution has no temporary review comment. The task skill and template
  require proportionate behavior tests; the workflow has explicit evidence gates.
- No application logic, models, migrations, dependency files, frontend or database
  data changed in this maintenance work. No Phase 3 implementation was performed.

## Executed verification

| Check | Result |
| --- | --- |
| `poetry check` | Passed |
| `poetry run ruff check .` | Passed |
| `poetry run ruff format --check .` | Passed; 84 files formatted |
| `poetry run python scripts/export_mermaid_diagrams.py --check` | Passed; all 15 diagrams match |
| `poetry run pytest -q --basetemp <unique temporary directory>` | 128 passed, 100 skipped |
| `specify workflow info speckit` | Passed; local v1.0.2 definition loads with 10 steps |
| Local Markdown link inspection | No missing local Markdown link targets found |
| Token/private-key pattern scan of tracked and eligible untracked files | No matches found; pattern scan is not an exhaustive secret guarantee |
| `git diff --check` | Passed |

Pytest initially failed because the Windows sandbox could not access its temporary
paths. The successful run used the same suite outside the sandbox with a unique
temporary directory. `TEST_DATABASE_URL` was removed only from the test process
and restored afterward. The 100 PostgreSQL-dependent tests were skipped; this is
not a fresh PostgreSQL/migration integration pass. No database-writing tests ran.

The workflow was parsed and inspected, not executed as a new feature. Its manual
gates require real artifacts/results before approval. Cross-team contracts and
historical React/Vite diagram labels remain documented limitations; they are not
scientific validation or permission to modify another team's implementation.
