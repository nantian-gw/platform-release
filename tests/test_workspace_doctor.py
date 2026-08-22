from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from tools import workspace_doctor


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def init_repo(path: Path) -> None:
    path.mkdir(parents=True)
    run(["git", "init", "-b", "main"], path)
    run(["git", "config", "user.name", "test"], path)
    run(["git", "config", "user.email", "test@example.com"], path)
    (path / "README.md").write_text("ok\n", encoding="utf-8")
    run(["git", "add", "README.md"], path)
    run(["git", "commit", "-m", "initial"], path)
    run(["git", "branch", "origin/main"], path)


def write_registry(path: Path) -> Path:
    registry = path / "components.yaml"
    registry.write_text(
        yaml.safe_dump(
            {
                "components": {
                    "gateway": {"repo": "https://github.com/nantian-gw/gateway"},
                    "missing": {"repo": "git@github.com:nantian-gw/missing.git"},
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return registry


def test_repo_slug_handles_https_ssh_and_dot_git() -> None:
    assert workspace_doctor.repo_slug("https://github.com/nantian-gw/gateway") == "nantian-gw/gateway"
    assert workspace_doctor.repo_slug("git@github.com:nantian-gw/gateway.git") == "nantian-gw/gateway"


def test_workspace_doctor_reports_dirty_and_missing_components(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"
    gateway = workspace / "gateway"
    init_repo(gateway)
    (gateway / "README.md").write_text("dirty\n", encoding="utf-8")
    registry = write_registry(tmp_path)

    status = workspace_doctor.main(
        [
            "--registry",
            str(registry),
            "--workspace-root",
            str(workspace),
            "--no-actions",
            "--strict",
        ]
    )
    output = capsys.readouterr().out

    assert status == 1
    assert "gateway" in output
    assert "dirty worktree" in output
    assert "missing checkout" in output


def test_workspace_doctor_json_output_is_machine_readable(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"
    init_repo(workspace / "gateway")
    registry = tmp_path / "components.yaml"
    registry.write_text(
        yaml.safe_dump({"components": {"gateway": {"repo": "https://github.com/nantian-gw/gateway"}}}),
        encoding="utf-8",
    )

    status = workspace_doctor.main(
        [
            "--registry",
            str(registry),
            "--workspace-root",
            str(workspace),
            "--no-actions",
            "--json",
            "--strict",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert status == 0
    assert payload[0]["name"] == "gateway"
    assert payload[0]["dirty"] is False
    assert payload[0]["ahead"] == 0
    assert payload[0]["behind"] == 0
