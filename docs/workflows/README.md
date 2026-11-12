# FlameGuard backend phase workflow

`flameguard-phase.yml` is a local [GitHub Spec Kit Workflow YAML](https://github.github.com/spec-kit/workflows/overview.html), not a GitHub Actions workflow. It selects one **project** phase (5, 6 or 7), creates its own Spec Kit feature, runs Specify → Plan → Tasks → Analyze → approved Implement → Test → Converge, and writes an engineering report. The workflow never interprets headings such as `## Phase 1: Setup` inside `tasks.md` as the project phase.

## Prerequisites

- Run in the backend repository root with `specify` 1.3.3 or a compatible version, Poetry, Python, and a working `codex` CLI on `PATH`. The project's Codex integration is registered in `.specify/integration.json`, but registration alone does not prove that `codex exec` works.
- Set `TEST_DATABASE_URL` to a **separately approved local PostgreSQL test server** URL using `postgresql+asyncpg://.../flameguard_test_<suffix>`. The backend integration fixtures create and remove unique child databases under this test prefix; the configured development/shared database must not be used. The workflow checks the name and local host before any agent step, but the operator must confirm that the server is dedicated to tests and the account has `CREATEDB`.
- Keep `DATABASE_URL` pointed at the intended development target. Review `git status --short` and preserve existing work. Phase 4's current `.specify/feature.json` selector will change to the new feature when Specify runs.
- The backlog is proposed, not blanket approval for every contract or scientific decision. Review the generated spec/plan/tasks at the mandatory implementation gate. Approve only the decision-complete backend scope. The workflow does not authorize breaking API changes, schema migrations, destructive operations or scientific validation claims.

At setup time on 2026-11-12, `specify --version` reported **1.3.3** and `specify integration list` registered Codex as default. `codex --version` failed because this machine's `nvm` has no active Node.js version. Install/activate an appropriate Node.js version and verify `codex --version` and `codex exec --help` before a real run. The workflow's preflight fails before Specify if Codex is still unavailable.

## One command per phase

In PowerShell, from `flameguard-ai-backend` after setting the isolated test URL:

```powershell
specify workflow run docs/workflows/flameguard-phase.yml -i phase=5 --json
specify workflow run docs/workflows/flameguard-phase.yml -i phase=6 --json
specify workflow run docs/workflows/flameguard-phase.yml -i phase=7 --json
```

Run **one** of those commands for the requested phase; do not run all three together. Each phase's deterministic feature path is `specs/phase<phase>-backend`, and `phase_control.py verify-feature` checks `.specify/feature.json` after Specify. An existing feature path makes a new run fail; resume the prior run instead. Run phases in dependency order when work depends on a prior phase's accepted contracts.

The engine pauses once for review of spec, plan, tasks and Analyze findings. At that gate, inspect the artifacts and approve only the authorized backend work. The workflow otherwise continues automatically until tests fail, an agent reports a material blocker, convergence cannot be determined safely, or the retry limit is reached. This is one **workflow invocation**, with a required human decision where the Constitution calls for it; it is not a promise of unattended implementation.

## What it does and checks

1. Preflight checks the phase enum, required repository files, available Specify/Poetry/Codex commands, absent target feature and local test URL. The selected phase comes only from the input.
2. Codex reads the Constitution, architecture, contracts, roadmap and relevant existing code. Specify creates one feature. Plan and Tasks stay in its scope. Analyze runs before and after routine artifact reconciliation.
3. The implementation gate asks for authorization of the concrete feature artifacts. Codex then processes every executable task, leaving external dependencies unchecked in `blocked-dependencies.json` with `task_id`, `owner`, `reason` and `evidence`.
4. The helper runs `poetry check`, `poetry run ruff check .`, `poetry run ruff format --check .`, the full `poetry run pytest -q` suite, and a second `poetry run pytest -q -m integration` pass. It requires nonzero integration test count, zero integration skips, zero failures, and successful exits. Codex can repair implementation-related failures and rerun checks up to three times per convergence cycle. JUnit counts, exit codes and local redacted logs are stored under `.tools/phase-workflow/<run-id>/`.
5. Converge may append tasks. The helper compares the exact pre/post `tasks.md` bytes and task checkbox IDs. Newly appended tasks cause another implementation/test/converge cycle, up to three total cycles. Existing task edits or unclassified unchecked tasks produce **uncertain**, never a green result. Explicitly blocked external tasks produce **blocked_external**, not scientific completion.
6. The feature receives `implementation-summary.md` for capabilities/endpoints and `engineering-report.md` for test counts, task status and external blockers. The report separates engineering checks from real Data/AI integration and scientific validation.

The machine-readable assessment does **not** parse prose such as “converged” from Codex output. It relies on task structure, the explicit blocker ledger and test reports. It can detect recorded gaps; it cannot prove that an agent discovered every scientific or contractual gap. Owner acceptance remains separate.

## Resume and failure recovery

```powershell
specify workflow status <run-id> --json
specify workflow resume <run-id> --json
```

Use the `run_id` from the initial JSON output. Fix the concrete failure first: activate Codex, restore a missing prerequisite, resolve an approved decision, repair the implementation, or provide a functioning isolated test database. A failed or paused run resumes completed steps from Spec Kit state; do not start another run for the same feature. If an agent stopped because a material decision is missing, record the owner decision in the relevant contract/ADR before resuming. A test failure that remains after three repair attempts stops before Converge. A bounded loop with new tasks remaining or uncertain assessment produces a report and review gate; do not approve it as “converged.”

The workflow does not commit, push, merge, approve a PR, deploy, import NASA data, alter the Frontend/Data Team repositories, reset a database, or run production changes. Existing Alembic revisions remain immutable. A justified additive migration still requires the impact analysis and approval in AGENTS.md and the Constitution.

## Validation and limitations

- The installed CLI accepted the YAML schema and started a local-file workflow in a disposable test directory. It failed at the first preflight on missing project files; no agent or Phase 5 work ran. The first step's failure is expected in that disposable project.
- The helper is Python code referenced by the YAML, so a raw YAML copy alone is insufficient. Keep these three files together. Shell `run` fields are fixed commands with `strict: true`; phase and run ID enter through validated environment bindings. Inspect this helper and any active workflow overlay before running it.
- End-to-end Codex dispatch and integration testing are **not yet verified** on this machine because `codex --version` fails. The current environment cannot reliably run the requested autopilot. Once Node/Codex is repaired, exercise a harmless disposable project or worktree with a minimal feature before using a real phase. `specify workflow run` validates and executes; it is not a dry-run validator.
- A workflow gate and paused/failed run are intentional outcomes when requirements or external evidence are incomplete. The supported fallback meanwhile is the project's existing gated Spec Kit workflow (`specify workflow run speckit ...`) or manual Codex `$speckit-*` commands, retaining the same approval and test requirements.

References: [workflow API](https://github.github.com/spec-kit/workflows/api.html), [step types and strict shell](https://github.github.com/spec-kit/workflow-steps/types.html), [workflow development and validation](https://github.github.com/spec-kit/workflows/developing.html), [Codex integration](https://github.github.com/spec-kit/integrations/codex.html).
