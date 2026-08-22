from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ActionWorkflow:
    workflow: str
    status: str
    conclusion: str
    sha: str
    updated_at: str
    url: str


@dataclass
class ComponentHealth:
    name: str
    repo: str
    path: str
    exists: bool
    git_repo: bool
    branch: str = ""
    head: str = ""
    dirty: bool = False
    ahead: int | None = None
    behind: int | None = None
    upstream: str = "origin/main"
    actions: list[ActionWorkflow] | None = None
    problems: list[str] | None = None


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def repo_slug(repo_url: str) -> str:
    value = repo_url.strip()
    if value.startswith("git@github.com:"):
        value = value.removeprefix("git@github.com:")
    elif value.startswith("https://github.com/"):
        value = value.removeprefix("https://github.com/")
    if value.endswith(".git"):
        value = value[:-4]
    return value


def load_components(registry: Path) -> dict[str, Any]:
    payload = yaml.safe_load(registry.read_text(encoding="utf-8"))
    components = payload.get("components") if isinstance(payload, dict) else None
    if not isinstance(components, dict) or not components:
        raise ValueError(f"component registry has no components: {registry}")
    return components


def latest_actions(slug: str) -> list[ActionWorkflow]:
    if shutil.which("gh") is None:
        return []
    proc = run(
        [
            "gh",
            "run",
            "list",
            "--repo",
            slug,
            "--branch",
            "main",
            "--limit",
            "30",
            "--json",
            "workflowName,status,conclusion,headSha,updatedAt,url",
        ]
    )
    if proc.returncode != 0:
        return [
            ActionWorkflow(
                workflow="<gh unavailable>",
                status="unknown",
                conclusion="failure",
                sha="",
                updated_at="",
                url=proc.stderr.strip(),
            )
        ]
    runs = json.loads(proc.stdout or "[]")
    by_workflow: dict[str, dict[str, Any]] = {}
    for item in runs:
        workflow = item.get("workflowName") or "<unknown>"
        current = by_workflow.get(workflow)
        if current is None or (item.get("updatedAt") or "") > (current.get("updatedAt") or ""):
            by_workflow[workflow] = item
    return [
        ActionWorkflow(
            workflow=name,
            status=item.get("status") or "unknown",
            conclusion=item.get("conclusion") or "-",
            sha=(item.get("headSha") or "")[:7],
            updated_at=item.get("updatedAt") or "",
            url=item.get("url") or "",
        )
        for name, item in sorted(by_workflow.items())
    ]


def inspect_component(
    name: str,
    repo: str,
    path: Path,
    *,
    fetch: bool,
    include_actions: bool,
) -> ComponentHealth:
    problems: list[str] = []
    health = ComponentHealth(
        name=name,
        repo=repo,
        path=str(path),
        exists=path.exists(),
        git_repo=False,
        problems=problems,
    )
    if not path.exists():
        problems.append("missing checkout")
        return health

    if run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"]).returncode != 0:
        problems.append("not a git repository")
        return health

    health.git_repo = True
    if fetch:
        run(["git", "-C", str(path), "fetch", "origin", "main", "--prune"])

    health.branch = run(["git", "-C", str(path), "branch", "--show-current"]).stdout.strip()
    health.head = run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"]).stdout.strip()
    status = run(["git", "-C", str(path), "status", "--porcelain"]).stdout.strip()
    health.dirty = bool(status)
    if health.dirty:
        problems.append("dirty worktree")

    if run(["git", "-C", str(path), "rev-parse", "--verify", "origin/main"]).returncode == 0:
        counts = run(["git", "-C", str(path), "rev-list", "--left-right", "--count", "HEAD...origin/main"]).stdout.split()
        if len(counts) == 2:
            health.ahead = int(counts[0])
            health.behind = int(counts[1])
            if health.ahead:
                problems.append(f"ahead of origin/main by {health.ahead}")
            if health.behind:
                problems.append(f"behind origin/main by {health.behind}")
    else:
        problems.append("origin/main not available")

    if include_actions:
        health.actions = latest_actions(repo_slug(repo))
        for workflow in health.actions:
            if workflow.status != "completed" or workflow.conclusion not in {"success", "skipped"}:
                problems.append(f"workflow {workflow.workflow} is {workflow.status}/{workflow.conclusion}")

    return health


def render_table(health: list[ComponentHealth], *, include_actions: bool) -> str:
    rows = [
        "component | branch | head | dirty | ahead | behind | actions | problems",
        "--- | --- | --- | --- | ---: | ---: | --- | ---",
    ]
    for item in health:
        if not item.exists or not item.git_repo:
            branch = head = "-"
            dirty = "-"
            ahead = behind = "-"
        else:
            branch = item.branch or "(detached)"
            head = item.head
            dirty = "yes" if item.dirty else "no"
            ahead = "-" if item.ahead is None else str(item.ahead)
            behind = "-" if item.behind is None else str(item.behind)
        if include_actions and item.actions is not None:
            if not item.actions:
                actions = "n/a"
            else:
                bad = [a for a in item.actions if a.status != "completed" or a.conclusion not in {"success", "skipped"}]
                actions = "ok" if not bad else f"{len(bad)} issue(s)"
        else:
            actions = "skipped"
        problems = "; ".join(item.problems or []) or "-"
        rows.append(f"{item.name} | {branch} | {head} | {dirty} | {ahead} | {behind} | {actions} | {problems}")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect Nantian workspace component health.")
    parser.add_argument("--registry", type=Path, default=Path("components/components.yaml"))
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd().parent)
    parser.add_argument("--fetch", action="store_true", help="Fetch origin/main before calculating ahead/behind.")
    parser.add_argument("--no-actions", action="store_true", help="Skip GitHub Actions status lookup.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any component has problems.")
    args = parser.parse_args(argv)

    components = load_components(args.registry)
    health = [
        inspect_component(
            name,
            str(meta.get("repo", "")),
            args.workspace_root / name,
            fetch=args.fetch,
            include_actions=not args.no_actions,
        )
        for name, meta in components.items()
    ]

    if args.json:
        print(json.dumps([asdict(item) for item in health], indent=2, sort_keys=True))
    else:
        print(render_table(health, include_actions=not args.no_actions))

    has_problems = any(item.problems for item in health)
    return 1 if args.strict and has_problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
