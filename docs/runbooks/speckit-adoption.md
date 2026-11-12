# Adopt GitHub Spec Kit with Codex — existing backend repository

**Status:** Installed in this backend repository. Shared `.agents/skills/` and `.specify/`
files belong in Git; secrets, `.env`, environments, local integration packages and
machine-specific configuration remain ignored. Poetry still manages the backend.
The project Constitution is `.specify/memory/constitution.md`; the preparation
`docs/constitution-draft.md` is retained as historical input.

Sections 1-4 below are recovery/setup reference, not instructions to initialize
this existing installation again. Inspect current files and version before any update.

Official sources:

- https://github.github.com/spec-kit/how-to/existing-projects.html
- https://github.github.com/spec-kit/installation.html
- https://github.com/github/spec-kit/blob/main/docs/integrations/codex.md

## 1. Safety before initialization

Run in **`flameguard-ai-backend/`**, not the `NASA/` parent and not the
frontend repository. Preserve all existing code, Phase 1–2 migrations and
diagram HTML. Confirm `git status --short`; review, commit or stash existing
work using your normal team workflow. Create a new integration branch.

```powershell
git status --short
git switch -c docs/spec-kit-codex-adoption
```

If this branch already exists, select a new branch name; do not reset it.
Do not automatically commit/push or touch unrelated changes.

## 2. Install CLI (separate from backend Poetry)

Spec Kit's CLI may use `uv`; **do not replace the backend's Poetry**.
Official install alternatives include `uv tool install specify-cli` and
`pipx install specify-cli`. Python 3.11+ is required by the installer.

```powershell
uv --version
uv tool install specify-cli
specify version
```

If `uv` is missing, follow the official `uv` installation guide (or choose
the documented `pipx` method). If `specify` already exists, inspect its
version instead of blindly installing a second executable.

## 3. Initialize in place — reviewable operation

From the backend root, after saving a known clean state:

```powershell
specify init --here --force --integration codex
git status --short
git diff --stat
git diff
```

`--force` acknowledges that the target directory is nonempty and can replace
conflicting Spec Kit-managed paths. **Inspect the diff**, especially
`.specify/`, `.agents/skills/` and any `.codex/` configuration. Stop if
anything unrelated to the integration changes. Do not erase existing work
to make initialization succeed.

Spec Kit creates the framework and Codex skills; it does **not** automatically
infer a correct constitution or retroactively specify Phase 1–2.

## 4. Initialize constitution through Codex chat

Open Codex with backend root as the working directory. Its official
integration installs `$speckit-*` skills under `.agents/skills/`.
Ask Codex to use:

```text
$speckit-constitution
Read AGENTS.md, docs/constitution-draft.md,
docs/backend-implementation-plan.md, docs/phase-2-database-implementation.md,
docs/team-ownership.md and ADR-0001.
Create the constitution from the existing approved constraints.
Do not invent requirements, schema, data validation, auth or permissions.
Review conflicts and report them before editing code.
```

Review `.specify/memory/constitution.md` for correctness and inspect Git diff.
It must preserve the existing 21-table ERD, Poetry, multi-team ownership,
data/provenance gates and demo chat decision.

This adoption procedure is historical after the Constitution was established.
Do not rerun it for a governance amendment. ADR-0003 now treats the 21-table
ERD as the current baseline and permits reviewed additive schema evolution;
applied Alembic revisions remain immutable.

## 5. Use Spec Kit for the **next bounded feature**, not old phases

Suggested first slice **after Phase 3 handoff/API contracts are agreed**:
Phase 4 catalog list with pagination/filtering over reviewed data, and HTTPX
contract tests with synthetic fixtures when real Data team input is pending.

In Codex chat, run each installed skill separately:

```text
$speckit-specify
$speckit-clarify
$speckit-plan
$speckit-tasks
$speckit-analyze
$speckit-implement
$speckit-converge
```

The user supplies feature intent to `$speckit-specify`; the other steps
operate on the resulting spec and plan. The flow is not a terminal batch
script. Review outputs at each gate. If converge identifies missing tasks,
repeat implement/test/converge until accepted or blocked.

After implementation, run the relevant Poetry checks and record exact results before
Converge. The local `.specify/workflows/speckit/workflow.yml` includes manual Clarify,
Analyze, Test and Converge evidence gates. Reject a gate when required evidence is
missing; remediation returns to the affected artifacts/tasks. Approval alone is not
proof that a check ran.

The tasks skill, tasks template and workflow are intentional project customizations. Integration
manifest hashes retain the installed upstream fingerprints so future updates can
detect local edits. Review and preserve these customizations when upgrading Spec Kit.

## 6. Retention and handoff

- Preserve agreed feature specs, plans, tasks and acceptance evidence under
  the installed Spec Kit conventions.
- Keep current delivery status in `docs/project-status.md` and actual phase
  records; do not retroactively rewrite historic verification.
- Review generated Spec Kit updates before committing; push only with the
  user's authorization.
- If skills are absent or renamed in installed versions, inspect actual
  `.agents/skills/` and official release docs. Do not invent invocation names.
