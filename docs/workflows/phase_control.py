"""Fail-closed local checks for the FlameGuard Spec Kit phase workflow.

This helper never provisions or deletes a database. The existing integration
fixtures may create and remove uniquely named databases on a local test server.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
FEATURES = {"5": "specs/phase5-backend", "6": "specs/phase6-backend", "7": "specs/phase7-backend"}
TASK_RE = re.compile(r"^\s*-\s*\[([ xX])\]\s+(T\d{3,})\b", re.MULTILINE)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def phase() -> str:
    value = os.environ.get("FLAMEGUARD_PHASE", "")
    require(value in FEATURES, "FLAMEGUARD_PHASE must be 5, 6, or 7")
    return value


def feature(value: str) -> Path:
    return ROOT / FEATURES[value]


def run_dir(value: str) -> Path:
    run_id = os.environ.get("FLAMEGUARD_RUN_ID", "")
    require(bool(re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id)), "Invalid workflow run ID")
    path = ROOT / ".tools" / "phase-workflow" / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def selected_feature(value: str) -> None:
    selector = ROOT / ".specify" / "feature.json"
    require(selector.is_file(), "Missing .specify/feature.json")
    data = json.loads(selector.read_text(encoding="utf-8"))
    require(
        data.get("feature_directory") == FEATURES[value],
        "Feature selector points to another project phase",
    )
    require(feature(value).is_dir(), "Selected phase feature directory is missing")


def tasks(value: str) -> tuple[str, dict[str, bool]]:
    selected_feature(value)
    path = feature(value) / "tasks.md"
    require(path.is_file(), "Selected phase tasks.md is missing")
    content = path.read_text(encoding="utf-8")
    found: dict[str, bool] = {}
    for match in TASK_RE.finditer(content):
        task_id = match.group(2)
        require(task_id not in found, f"Duplicate task ID: {task_id}")
        found[task_id] = match.group(1).lower() == "x"
    require(bool(found), "No structurally recognized task checkboxes in tasks.md")
    return content, found


def check_tool(name: str, *args: str) -> None:
    try:
        result = subprocess.run(
            [name, *args], cwd=ROOT, capture_output=True, text=True, timeout=20, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"{name} is unavailable") from exc
    require(result.returncode == 0, f"{name} is unavailable or not functional")


def check_test_target() -> None:
    raw = os.environ.get("TEST_DATABASE_URL", "")
    require(bool(raw), "Set TEST_DATABASE_URL for an isolated local PostgreSQL test server")
    url = urlsplit(raw)
    name = url.path.lstrip("/")
    require(url.scheme == "postgresql+asyncpg", "TEST_DATABASE_URL must use postgresql+asyncpg")
    require(
        url.hostname in {"localhost", "127.0.0.1", "::1"},
        "Only a local isolated test server is allowed",
    )
    require(
        bool(re.fullmatch(r"flameguard_test_[a-z0-9_]{1,35}", name)),
        "Use flameguard_test_<suffix> database",
    )
    development = os.environ.get("DATABASE_URL", "")
    if development:
        require(raw != development, "TEST_DATABASE_URL must differ from DATABASE_URL")


def preflight(value: str) -> dict:
    for relative in (
        "AGENTS.md",
        ".specify/memory/constitution.md",
        "docs/backend-implementation-plan.md",
        "docs/roadmap/phase5-7-backlog.md",
        "docs/roadmap/data-integration-pending.md",
        "pyproject.toml",
        ".specify/feature.json",
    ):
        require((ROOT / relative).is_file(), f"Missing required project file: {relative}")
    require(not feature(value).exists(), f"{FEATURES[value]} already exists; resume its prior run")
    check_tool("specify", "--version")
    check_tool("poetry", "--version")
    check_tool("codex", "--version")
    check_test_target()
    return {
        "phase": value,
        "feature": FEATURES[value],
        "codex": "available",
        "test_target": "local-isolated",
    }


def verify_feature(value: str) -> dict:
    selected_feature(value)
    require((feature(value) / "spec.md").is_file(), "Specify did not create spec.md")
    return {"phase": value, "feature": FEATURES[value], "selector_verified": True}


def command(argv: list[str], label: str, timeout: int, directory: Path) -> dict:
    result = subprocess.run(
        argv, cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False
    )
    output = result.stdout + "\n" + result.stderr
    for key in ("DATABASE_URL", "TEST_DATABASE_URL"):
        secret = os.environ.get(key, "")
        if secret:
            output = output.replace(secret, "[REDACTED_DATABASE_URL]")
    log_path = directory / (re.sub(r"[^a-z0-9]+", "-", label.lower()) + ".log")
    log_path.write_text(output, encoding="utf-8")
    return {"check": label, "exit_code": result.returncode}


def junit_counts(path: Path) -> dict:
    if not path.is_file():
        return {"total": 0, "failed": 0, "skipped": 0}
    root = ElementTree.parse(path).getroot()
    cases = root.findall(".//testcase")
    return {
        "total": len(cases),
        "failed": sum(
            bool(case.find("failure") is not None or case.find("error") is not None)
            for case in cases
        ),
        "skipped": sum(case.find("skipped") is not None for case in cases),
    }


def test(value: str) -> dict:
    selected_feature(value)
    check_test_target()
    directory = run_dir(value)
    checks = [
        command(["poetry", "check"], "poetry check", 120, directory),
        command(["poetry", "run", "ruff", "check", "."], "ruff check", 300, directory),
        command(["poetry", "run", "ruff", "format", "--check", "."], "ruff format", 300, directory),
        command(
            ["poetry", "run", "pytest", "-q", f"--junitxml={directory / 'all.xml'}"],
            "all pytest",
            1800,
            directory,
        ),
        command(
            [
                "poetry",
                "run",
                "pytest",
                "-q",
                "-m",
                "integration",
                f"--junitxml={directory / 'integration.xml'}",
            ],
            "PostgreSQL integration pytest",
            1800,
            directory,
        ),
    ]
    all_counts = junit_counts(directory / "all.xml")
    integration = junit_counts(directory / "integration.xml")
    passed = (
        all(item["exit_code"] == 0 for item in checks)
        and all_counts["total"] > 0
        and all_counts["failed"] == 0
        and integration["total"] > 0
        and integration["failed"] == 0
        and integration["skipped"] == 0
    )
    result = {
        "phase": value,
        "passed": passed,
        "checks": checks,
        "all_tests": all_counts,
        "integration_tests": integration,
    }
    (directory / "test-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def test_status(value: str) -> dict:
    directory = run_dir(value)
    result = json.loads((directory / "test-results.json").read_text(encoding="utf-8"))
    require(result.get("passed") is True, "Verification still fails after bounded repairs")
    return {"phase": value, "passed": True}


def snapshot(value: str) -> dict:
    content, found = tasks(value)
    directory = run_dir(value)
    (directory / "tasks-before-converge.md").write_text(content, encoding="utf-8")
    return {
        "phase": value,
        "task_count": len(found),
        "unchecked": sum(not done for done in found.values()),
    }


def blocked_ids(value: str) -> set[str]:
    path = feature(value) / "blocked-dependencies.json"
    if not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, list), "blocked-dependencies.json must be an array")
    ids: set[str] = set()
    for entry in payload:
        require(isinstance(entry, dict), "Each blocker must be an object")
        for key in ("task_id", "owner", "reason", "evidence"):
            require(
                isinstance(entry.get(key), str) and bool(entry[key].strip()),
                f"Blocker missing {key}",
            )
        require(entry["task_id"] not in ids, "Duplicate blocked task ID")
        ids.add(entry["task_id"])
    return ids


def assess(value: str) -> dict:
    directory = run_dir(value)
    before_path = directory / "tasks-before-converge.md"
    require(before_path.is_file(), "Missing pre-convergence task snapshot")
    before = before_path.read_text(encoding="utf-8")
    after, current = tasks(value)
    prior = {match.group(2) for match in TASK_RE.finditer(before)}
    added = sorted(set(current) - prior)
    unchecked = sorted(key for key, done in current.items() if not done)
    blocked = blocked_ids(value)
    require(blocked <= set(unchecked), "Blocked ledger references a completed or unknown task")
    if not after.startswith(before):
        status, retry = "uncertain", False
    elif added:
        status, retry = "new_tasks", True
    elif unchecked and set(unchecked) == blocked:
        status, retry = "blocked_external", False
    elif unchecked:
        status, retry = "uncertain", False
    else:
        status, retry = "converged", False
    result = {
        "phase": value,
        "status": status,
        "retry": retry,
        "added_tasks": added,
        "unchecked_tasks": unchecked,
        "blocked_tasks": sorted(blocked),
    }
    (directory / "assessment.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def report(value: str) -> dict:
    directory = run_dir(value)
    require((feature(value) / "implementation-summary.md").is_file(), "Missing capability summary")
    assessment = json.loads((directory / "assessment.json").read_text(encoding="utf-8"))
    tests = json.loads((directory / "test-results.json").read_text(encoding="utf-8"))
    status = "needs_implementation" if assessment["retry"] else assessment["status"]
    lines = [
        f"# Phase {value} engineering and integration status",
        "",
        f"- Spec Kit feature: `{FEATURES[value]}`",
        f"- Engineering status: **{status}**",
        "- Scientific validation: **not established by this workflow**",
        "- Real Data/AI integration: **requires independent owner evidence**",
        "",
        "## Verification",
        "",
    ]
    for item in tests["checks"]:
        lines.append(f"- `{item['check']}`: exit {item['exit_code']}")
    lines += [
        f"- Full pytest: {tests['all_tests']}",
        f"- PostgreSQL integration pytest: {tests['integration_tests']}",
        "",
        "## Convergence evidence",
        "",
        f"- Added tasks on latest assessment: {assessment['added_tasks']}",
        f"- Remaining unchecked tasks: {assessment['unchecked_tasks']}",
        "",
        "## External dependencies",
        "",
        f"- Blocked task IDs: {assessment['blocked_tasks']}",
        f"- Details: `{FEATURES[value]}/blocked-dependencies.json` (if present)",
        f"- Capability summary: `{FEATURES[value]}/implementation-summary.md`",
        "",
        "Completion requires all recorded tasks checked and no new tasks appended.",
        "It does not establish scientific validity or Frontend/Data/AI acceptance.",
        "",
    ]
    target = feature(value) / "engineering-report.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return {"phase": value, "status": status, "report": target.relative_to(ROOT).as_posix()}


def main() -> None:
    require(len(sys.argv) == 2, "Usage: phase_control.py ACTION")
    value = phase()
    actions = {
        "preflight": preflight,
        "verify-feature": verify_feature,
        "test": test,
        "test-status": test_status,
        "snapshot": snapshot,
        "assess": assess,
        "report": report,
    }
    require(sys.argv[1] in actions, "Unknown action")
    print(json.dumps(actions[sys.argv[1]](value), separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        OSError,
        json.JSONDecodeError,
        ElementTree.ParseError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"Phase workflow check failed: {exc}", file=sys.stderr)
        sys.exit(1)
