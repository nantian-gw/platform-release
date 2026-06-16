import json
from pathlib import Path

import pytest
import yaml

from tools import releasectl


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


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


def test_validate_release_rejects_noncanonical_chart_repo(tmp_path: Path) -> None:
    registry = tmp_path / "components/components.yaml"
    manifest = tmp_path / "releases/v2026.06.0-rc1/manifest.yaml"
    summary = tmp_path / "results/v2026.06.0-rc1/summary.yaml"
    manifest_schema_path = tmp_path / "schemas/manifest.schema.json"
    summary_schema_path = tmp_path / "schemas/summary.schema.json"

    write_yaml(registry, registry_payload())
    write_yaml(manifest, manifest_payload(chart_repo="https://charts.nantian.dev"))
    write_yaml(
        summary,
        {
            "platformVersion": "v2026.06.0-rc1",
            "status": "pending",
            "checks": {"gateway-build": {"status": "pending"}},
            "artifacts": {},
        },
    )
    manifest_schema_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_schema_path.write_text(json.dumps(manifest_schema()), encoding="utf-8")
    summary_schema_path.write_text(json.dumps(summary_schema()), encoding="utf-8")

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
