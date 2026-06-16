import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml

from tools import releasectl


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def registry_payload() -> dict:
    return {
        "components": {
            "gateway": {
                "repo": "https://github.com/nantian-gw/gateway",
                "validate": [
                    {"id": "gateway-build", "run": "make build"},
                    {"id": "gateway-test", "run": "make test"},
                ],
            },
            "dataplane": {
                "repo": "https://github.com/nantian-gw/dataplane",
                "validate": [
                    {"id": "dataplane-build", "run": "cargo build --workspace"},
                ],
            },
        },
        "platformChecks": [
            {"id": "install-validation", "repo": "gateway", "run": "make e2e-smoke"},
            {"id": "gateway-api-conformance", "repo": "gateway", "run": "make conformance"},
        ],
    }


def manifest_payload(chart_repo: str = "https://chart.nantian.dev") -> dict:
    return {
        "platformVersion": "v2026.06.0-rc1",
        "baseRelease": None,
        "status": "candidate",
        "releaseDate": "2026-06-16",
        "components": {
            "gateway": {
                "repo": "https://github.com/nantian-gw/gateway",
                "tag": "gateway-v2026.06.0-rc1",
                "commit": "6a4b1fc102643ef4419eead8305c93e2922c74a4",
            },
            "dataplane": {
                "repo": "https://github.com/nantian-gw/dataplane",
                "tag": "dataplane-v2026.06.0-rc1",
                "commit": "e70d52c12097d3d3b161c8b6e2084ff7413167ef",
            },
        },
        "artifacts": {
            "containerImages": {
                "gateway": "ghcr.io/nantian-gw/gateway@sha256:" + "a" * 64,
                "dataplane": "ghcr.io/nantian-gw/dataplane@sha256:" + "b" * 64,
            },
            "helmChart": {
                "name": "nantian-gw",
                "version": "0.2.3",
                "repo": chart_repo,
            },
        },
    }


def manifest_schema() -> dict:
    return {
        "type": "object",
        "required": ["platformVersion", "status", "releaseDate", "components", "artifacts"],
        "properties": {
            "platformVersion": {"type": "string"},
            "status": {"type": "string"},
            "releaseDate": {"type": "string"},
            "components": {"type": "object"},
            "artifacts": {"type": "object"},
        },
    }


def summary_schema() -> dict:
    return {
        "type": "object",
        "required": ["platformVersion", "status", "checks", "artifacts"],
        "properties": {
            "platformVersion": {"type": "string"},
            "status": {"type": "string"},
            "checks": {"type": "object"},
            "artifacts": {"type": "object"},
        },
    }


def write_release_inputs(
    tmp_path: Path,
    *,
    summary_payload: dict | None = None,
    chart_repo: str = "https://chart.nantian.dev",
) -> tuple[Path, Path, Path, Path, Path]:
    registry = tmp_path / "components/components.yaml"
    manifest = tmp_path / "releases/v2026.06.0-rc1/manifest.yaml"
    summary = tmp_path / "results/v2026.06.0-rc1/summary.yaml"
    manifest_schema_path = tmp_path / "schemas/manifest.schema.json"
    summary_schema_path = tmp_path / "schemas/summary.schema.json"

    write_yaml(registry, registry_payload())
    write_yaml(manifest, manifest_payload(chart_repo=chart_repo))
    write_yaml(
        summary,
        summary_payload
        or {
            "platformVersion": "v2026.06.0-rc1",
            "status": "pending",
            "checks": {},
            "artifacts": {},
        },
    )
    write_json(manifest_schema_path, manifest_schema())
    write_json(summary_schema_path, summary_schema())
    return registry, manifest, manifest_schema_path, summary, summary_schema_path


def test_validate_release_rejects_noncanonical_chart_repo(tmp_path: Path) -> None:
    registry, manifest, manifest_schema_path, summary, summary_schema_path = write_release_inputs(
        tmp_path,
        summary_payload={
            "platformVersion": "v2026.06.0-rc1",
            "status": "pending",
            "checks": {"gateway-build": {"status": "pending"}},
            "artifacts": {},
        },
        chart_repo="https://charts.nantian.dev",
    )

    with pytest.raises(ValueError, match="chart.nantian.dev"):
        releasectl.validate_release_files(
            registry,
            manifest,
            manifest_schema_path,
            summary,
            summary_schema_path,
        )


def test_initial_summary_contains_component_and_platform_checks(tmp_path: Path) -> None:
    summary = releasectl.build_initial_summary("v2026.06.0-rc1", registry_payload())
    assert summary["status"] == "pending"
    assert summary["checks"]["gateway-build"]["status"] == "pending"
    assert summary["checks"]["install-validation"]["status"] == "pending"
    assert summary["checks"]["gateway-api-conformance"]["status"] == "pending"


def test_render_results_creates_human_readable_reports(tmp_path: Path) -> None:
    summary = {
        "platformVersion": "v2026.06.0-rc1",
        "status": "passed",
        "checks": {
            "gateway-build": {"status": "passed"},
            "gateway-api-conformance": {"status": "passed"},
        },
        "artifacts": {
            "githubRun": "https://github.com/nantian-gw/platform-release/actions/runs/123456789",
        },
    }
    summary_path = tmp_path / "results/v2026.06.0-rc1/summary.yaml"
    write_yaml(summary_path, summary)
    matrix_path = tmp_path / "results/v2026.06.0-rc1/test-matrix.md"
    conformance_path = tmp_path / "results/v2026.06.0-rc1/conformance.md"
    artifacts_path = tmp_path / "results/v2026.06.0-rc1/artifacts.yaml"

    releasectl.render_results(summary_path, matrix_path, conformance_path, artifacts_path)

    assert "| gateway-build | passed |" in matrix_path.read_text(encoding="utf-8")
    assert "Gateway API conformance status: passed" in conformance_path.read_text(encoding="utf-8")
    artifact_index = yaml.safe_load(artifacts_path.read_text(encoding="utf-8"))
    assert artifact_index["githubRun"].endswith("/123456789")


def test_promote_release_requires_passed_summary(tmp_path: Path) -> None:
    releases_root = tmp_path / "releases/v2026.06.0-rc1"
    results_root = tmp_path / "results/v2026.06.0-rc1"
    write_yaml(releases_root / "manifest.yaml", manifest_payload())
    (releases_root / "release-notes.md").write_text("# notes\n", encoding="utf-8")
    write_yaml(results_root / "summary.yaml", {"platformVersion": "v2026.06.0-rc1", "status": "failed", "checks": {}, "artifacts": {}})

    with pytest.raises(ValueError, match="status passed"):
        releasectl.promote_release(tmp_path, "v2026.06.0-rc1", "v2026.06.0")


def test_run_validation_marks_active_failure_and_skips_later_checks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    registry, manifest, manifest_schema_path, summary, summary_schema_path = write_release_inputs(tmp_path)
    workspace = tmp_path / ".work/v2026.06.0-rc1"

    def fake_checkout_repo(repo: str, commit: str, target: Path) -> Path:
        target.mkdir(parents=True, exist_ok=True)
        return target

    def fake_run_command(command: str, cwd: Path) -> None:
        if command == "make test":
            raise subprocess.CalledProcessError(2, command)

    monkeypatch.setattr(releasectl, "checkout_repo", fake_checkout_repo)
    monkeypatch.setattr(releasectl, "run_command", fake_run_command)

    with pytest.raises(subprocess.CalledProcessError):
        releasectl.run_validation(
            registry,
            manifest,
            manifest_schema_path,
            summary,
            summary_schema_path,
            workspace,
        )

    rendered_summary = releasectl.load_yaml(summary)
    assert rendered_summary["status"] == "failed"
    assert rendered_summary["checks"]["gateway-build"]["status"] == "passed"
    assert rendered_summary["checks"]["gateway-test"]["status"] == "failed"
    assert rendered_summary["checks"]["dataplane-build"]["status"] == "skipped-after-failure"
    assert rendered_summary["checks"]["install-validation"]["status"] == "skipped-after-failure"
    assert rendered_summary["checks"]["gateway-api-conformance"]["status"] == "skipped-after-failure"
    assert rendered_summary["artifacts"]["failure"] == "command failed with exit code 2"


def test_run_validation_checkout_failure_does_not_claim_a_validation_check_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, manifest, manifest_schema_path, summary, summary_schema_path = write_release_inputs(tmp_path)
    workspace = tmp_path / ".work/v2026.06.0-rc1"

    def fake_checkout_repo(repo: str, commit: str, target: Path) -> Path:
        raise subprocess.CalledProcessError(128, ["git", "clone", repo, str(target)])

    monkeypatch.setattr(releasectl, "checkout_repo", fake_checkout_repo)

    with pytest.raises(subprocess.CalledProcessError):
        releasectl.run_validation(
            registry,
            manifest,
            manifest_schema_path,
            summary,
            summary_schema_path,
            workspace,
        )

    rendered_summary = releasectl.load_yaml(summary)
    assert rendered_summary["status"] == "failed"
    assert rendered_summary["checks"]["gateway-build"]["status"] == "skipped-after-failure"
    assert rendered_summary["checks"]["gateway-test"]["status"] == "skipped-after-failure"
    assert rendered_summary["checks"]["dataplane-build"]["status"] == "skipped-after-failure"
    assert rendered_summary["checks"]["install-validation"]["status"] == "skipped-after-failure"
    assert rendered_summary["checks"]["gateway-api-conformance"]["status"] == "skipped-after-failure"
    assert rendered_summary["artifacts"]["failure"] == "command failed with exit code 128"


def test_run_validation_success_marks_component_and_platform_checks_passed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, manifest, manifest_schema_path, summary, summary_schema_path = write_release_inputs(tmp_path)
    workspace = tmp_path / ".work/v2026.06.0-rc1"
    commands: list[tuple[str, Path]] = []

    def fake_checkout_repo(repo: str, commit: str, target: Path) -> Path:
        target.mkdir(parents=True, exist_ok=True)
        return target

    def fake_run_command(command: str, cwd: Path) -> None:
        commands.append((command, cwd))

    monkeypatch.setattr(releasectl, "checkout_repo", fake_checkout_repo)
    monkeypatch.setattr(releasectl, "run_command", fake_run_command)
    monkeypatch.setenv("GITHUB_RUN_ID", "123456789")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "nantian-gw/platform-release")

    releasectl.run_validation(
        registry,
        manifest,
        manifest_schema_path,
        summary,
        summary_schema_path,
        workspace,
    )

    rendered_summary = releasectl.load_yaml(summary)
    assert rendered_summary["status"] == "passed"
    assert rendered_summary["checks"]["gateway-build"]["status"] == "passed"
    assert rendered_summary["checks"]["gateway-test"]["status"] == "passed"
    assert rendered_summary["checks"]["dataplane-build"]["status"] == "passed"
    assert rendered_summary["checks"]["install-validation"]["status"] == "passed"
    assert rendered_summary["checks"]["gateway-api-conformance"]["status"] == "passed"
    assert rendered_summary["artifacts"]["githubRun"] == (
        "https://github.com/nantian-gw/platform-release/actions/runs/123456789"
    )
    assert commands == [
        ("make build", workspace / "gateway"),
        ("make test", workspace / "gateway"),
        ("cargo build --workspace", workspace / "dataplane"),
        ("make e2e-smoke", workspace / "gateway"),
        ("make conformance", workspace / "gateway"),
    ]


def test_checkout_repo_clears_existing_target_before_reclone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "workspace/gateway"
    dirty_file = target / "build/output.txt"
    dirty_file.parent.mkdir(parents=True, exist_ok=True)
    dirty_file.write_text("stale\n", encoding="utf-8")
    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(cmd: list[str], check: bool, cwd: Path | None = None, **_: object) -> None:
        calls.append((cmd, cwd))
        if cmd[:3] == ["git", "clone", "--no-checkout"]:
            assert not target.exists()
            target.mkdir(parents=True, exist_ok=True)
        elif cmd[:2] == ["git", "fetch"]:
            assert cwd == target
            assert target.exists()
        elif cmd[:2] == ["git", "checkout"]:
            assert cwd == target
            assert target.exists()

    monkeypatch.setattr(releasectl.subprocess, "run", fake_run)

    result = releasectl.checkout_repo("https://github.com/nantian-gw/gateway", "deadbeef", target)

    assert result == target
    assert not dirty_file.exists()
    assert calls == [
        (
            ["git", "clone", "--no-checkout", "https://github.com/nantian-gw/gateway", str(target)],
            None,
        ),
        (["git", "fetch", "--depth", "1", "origin", "deadbeef"], target),
        (["git", "checkout", "--detach", "deadbeef"], target),
    ]


def test_collect_results_wrapper_works_from_another_cwd(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    summary = {
        "platformVersion": "v2026.06.0-rc1",
        "status": "passed",
        "checks": {
            "gateway-build": {"status": "passed"},
            "gateway-api-conformance": {"status": "passed"},
        },
        "artifacts": {},
    }
    summary_path = tmp_path / "results/v2026.06.0-rc1/summary.yaml"
    write_yaml(summary_path, summary)
    matrix_path = tmp_path / "results/v2026.06.0-rc1/test-matrix.md"
    conformance_path = tmp_path / "results/v2026.06.0-rc1/conformance.md"
    artifacts_path = tmp_path / "results/v2026.06.0-rc1/artifacts.yaml"
    other_cwd = tmp_path / "elsewhere"
    other_cwd.mkdir()
    env = os.environ.copy()
    env.pop("PYTHON_BIN", None)

    subprocess.run(
        [
            str(repo_root / "scripts/collect-results.sh"),
            str(summary_path),
            str(matrix_path),
            str(conformance_path),
            str(artifacts_path),
        ],
        cwd=other_cwd,
        check=True,
        env=env,
    )

    assert "| gateway-build | passed |" in matrix_path.read_text(encoding="utf-8")
    assert "Gateway API conformance status: passed" in conformance_path.read_text(encoding="utf-8")
