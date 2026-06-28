from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import jsonschema
import yaml


CANONICAL_CHART_REPO = "https://chart.nantian.dev"


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write content atomically to path using temp file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}-", suffix=".tmp")
    try:
        os.write(fd, content.encode(encoding))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp_path, path)


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(path: Path, payload: dict) -> None:
    atomic_write_text(path, yaml.safe_dump(payload, sort_keys=False))


def load_schema(path: Path) -> dict:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_initial_summary(platform_version: str, registry: dict) -> dict:
    checks: dict[str, dict[str, str]] = {}
    for component in registry["components"].values():
        for check in component["validate"]:
            checks[check["id"]] = {"status": "pending"}
    for check in registry.get("platformChecks", []):
        checks[check["id"]] = {"status": "pending"}
    return {
        "platformVersion": platform_version,
        "status": "pending",
        "checks": checks,
        "artifacts": {},
    }


def validate_release_files(
    registry_path: Path,
    manifest_path: Path,
    manifest_schema_path: Path,
    summary_path: Path,
    summary_schema_path: Path,
) -> tuple[dict, dict, dict]:
    registry = load_yaml(registry_path)
    manifest = load_yaml(manifest_path)
    summary = load_yaml(summary_path)
    jsonschema.validate(manifest, load_schema(manifest_schema_path))
    jsonschema.validate(summary, load_schema(summary_schema_path))

    if manifest["artifacts"]["helmChart"]["repo"] != CANONICAL_CHART_REPO:
        raise ValueError(f"helm chart repo must be {CANONICAL_CHART_REPO}")

    registered = registry["components"]
    manifest_components = manifest["components"]
    if set(manifest_components) != set(registered):
        raise ValueError("manifest components must match the component registry exactly")

    for name, config in registered.items():
        if manifest_components[name]["repo"] != config["repo"]:
            raise ValueError(f"manifest repo mismatch for {name}")

    if manifest["platformVersion"] != summary["platformVersion"]:
        raise ValueError("summary platformVersion must match the manifest")

    for component in registered.values():
        for check in component["validate"]:
            summary["checks"].setdefault(check["id"], {"status": "pending"})
    for check in registry.get("platformChecks", []):
        summary["checks"].setdefault(check["id"], {"status": "pending"})

    return registry, manifest, summary


def run_command(command: str, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=cwd, shell=True, check=True, env={**os.environ, **env} if env else None)


def validation_image_alias(platform_version: str, component: str) -> str:
    return f"nantian-gw-validation/{component}:{platform_version}"


def release_image_aliases(manifest: dict) -> dict[str, tuple[str, str]]:
    images = manifest.get("artifacts", {}).get("containerImages", {})
    aliases: dict[str, tuple[str, str]] = {}
    if gateway_image := images.get("gateway"):
        aliases["CONTROL_PLANE_IMAGE"] = (
            gateway_image,
            validation_image_alias(manifest["platformVersion"], "controlplane"),
        )
    if dataplane_image := images.get("dataplane"):
        aliases["DATA_PLANE_IMAGE"] = (
            dataplane_image,
            validation_image_alias(manifest["platformVersion"], "dataplane"),
        )
    return aliases


def prepare_release_image_alias(source: str, alias: str) -> None:
    print(f"Preparing release image alias: {source} -> {alias}", flush=True)
    subprocess.run(["docker", "pull", "--platform", "linux/amd64", source], check=True)
    subprocess.run(["docker", "tag", source, alias], check=True)


def prepare_release_image_aliases(manifest: dict) -> None:
    for source, alias in release_image_aliases(manifest).values():
        prepare_release_image_alias(source, alias)


def prepare_gateway_smoke_overlay(checkout: Path, manifest: dict) -> None:
    overlay = checkout / "deploy/kubernetes/overlays/kind-conformance"
    aliases = release_image_aliases(manifest)
    if control_plane := aliases.get("CONTROL_PLANE_IMAGE"):
        run_command(f"kustomize edit set image nantian-controlplane={control_plane[1]}", overlay)
    if data_plane := aliases.get("DATA_PLANE_IMAGE"):
        run_command(f"kustomize edit set image nantian-dataplane={data_plane[1]}", overlay)


def platform_check_env(manifest: dict, repo_name: str) -> dict[str, str] | None:
    if repo_name != "gateway":
        return None

    env = {name: alias for name, (_, alias) in release_image_aliases(manifest).items()}
    return env or None


def checkout_repo(repo: str, commit: str, target: Path) -> Path:
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--no-checkout", repo, str(target)], check=True)
    subprocess.run(["git", "fetch", "--depth", "1", "origin", commit], cwd=target, check=True)
    subprocess.run(["git", "checkout", "--detach", commit], cwd=target, check=True)
    return target


def run_validation(
    registry_path: Path,
    manifest_path: Path,
    manifest_schema_path: Path,
    summary_path: Path,
    summary_schema_path: Path,
    workspace: Path,
) -> None:
    registry, manifest, summary = validate_release_files(
        registry_path,
        manifest_path,
        manifest_schema_path,
        summary_path,
        summary_schema_path,
    )
    workspace.mkdir(parents=True, exist_ok=True)
    active_check_id: str | None = None
    release_image_aliases_prepared = False
    gateway_smoke_overlay_prepared = False
    summary["status"] = "pending"
    summary["artifacts"] = {
        key: value
        for key, value in summary.get("artifacts", {}).items()
        if key not in {"failure", "githubRun"}
    }
    for state in summary["checks"].values():
        state["status"] = "pending"

    try:
        for name, config in registry["components"].items():
            component_checks = config["validate"]
            checkout = checkout_repo(config["repo"], manifest["components"][name]["commit"], workspace / name)
            for check in component_checks:
                active_check_id = check["id"]
                run_command(check["run"], checkout)
                summary["checks"][check["id"]]["status"] = "passed"

        for check in registry.get("platformChecks", []):
            active_check_id = check["id"]
            repo_name = check["repo"]
            checkout = workspace / repo_name
            env = platform_check_env(manifest, repo_name)
            if env and not release_image_aliases_prepared:
                prepare_release_image_aliases(manifest)
                release_image_aliases_prepared = True
            if env and repo_name == "gateway" and not gateway_smoke_overlay_prepared:
                prepare_gateway_smoke_overlay(checkout, manifest)
                gateway_smoke_overlay_prepared = True
            run_command(check["run"], checkout, env=env)
            summary["checks"][check["id"]]["status"] = "passed"

        active_check_id = None
        summary["status"] = "passed"
        run_id = os.environ.get("GITHUB_RUN_ID")
        if run_id:
            summary["artifacts"]["githubRun"] = f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{run_id}"
    except subprocess.CalledProcessError as exc:
        summary["status"] = "failed"
        if active_check_id is not None:
            summary["checks"][active_check_id]["status"] = "failed"
        for check_name, state in summary["checks"].items():
            if check_name != active_check_id and state["status"] == "pending":
                summary["checks"][check_name]["status"] = "skipped-after-failure"
        summary["artifacts"]["failure"] = f"command failed with exit code {exc.returncode}"
        dump_yaml(summary_path, summary)
        raise

    dump_yaml(summary_path, summary)


def render_results(summary_path: Path, matrix_path: Path, conformance_path: Path, artifacts_path: Path) -> None:
    summary = load_yaml(summary_path)

    matrix_lines = [
        f"# {summary['platformVersion']} Test Matrix",
        "",
        f"Overall status: `{summary['status']}`",
        "",
        "| Check | Status |",
        "| --- | --- |",
    ]
    for name, payload in summary["checks"].items():
        matrix_lines.append(f"| {name} | {payload['status']} |")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(matrix_path, "\n".join(matrix_lines) + "\n")

    conformance_state = summary["checks"].get("gateway-api-conformance", {"status": "pending"})["status"]
    conformance_lines = [
        f"# {summary['platformVersion']} Conformance",
        "",
        f"Gateway API conformance status: {conformance_state}",
        "",
        "See `summary.yaml` and linked external artifacts for the raw evidence.",
    ]
    atomic_write_text(conformance_path, "\n".join(conformance_lines) + "\n")

    artifacts_index = {
        "githubRun": summary.get("artifacts", {}).get("githubRun", ""),
        "failure": summary.get("artifacts", {}).get("failure", ""),
    }
    dump_yaml(artifacts_path, artifacts_index)


def promote_release(repo_root: Path, candidate_version: str, final_version: str) -> None:
    candidate_release = repo_root / "releases" / candidate_version
    candidate_results = repo_root / "results" / candidate_version
    final_release = repo_root / "releases" / final_version
    final_results = repo_root / "results" / final_version

    summary = load_yaml(candidate_results / "summary.yaml")
    if summary["status"] != "passed":
        raise ValueError("candidate summary status passed is required before promotion")

    if final_release.exists() or final_results.exists():
        raise ValueError("final release already exists")

    shutil.copytree(candidate_release, final_release)
    shutil.copytree(candidate_results, final_results)

    manifest = load_yaml(final_release / "manifest.yaml")
    manifest["platformVersion"] = final_version
    manifest["status"] = "released"
    dump_yaml(final_release / "manifest.yaml", manifest)

    final_summary = load_yaml(final_results / "summary.yaml")
    final_summary["platformVersion"] = final_version
    dump_yaml(final_results / "summary.yaml", final_summary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("run-validation")
    validate_parser.add_argument("--registry", required=True, type=Path)
    validate_parser.add_argument("--manifest", required=True, type=Path)
    validate_parser.add_argument("--manifest-schema", required=True, type=Path)
    validate_parser.add_argument("--summary", required=True, type=Path)
    validate_parser.add_argument("--summary-schema", required=True, type=Path)
    validate_parser.add_argument("--workspace", required=True, type=Path)

    collect_parser = subparsers.add_parser("collect-results")
    collect_parser.add_argument("--summary", required=True, type=Path)
    collect_parser.add_argument("--matrix", required=True, type=Path)
    collect_parser.add_argument("--conformance", required=True, type=Path)
    collect_parser.add_argument("--artifacts", required=True, type=Path)

    promote_parser = subparsers.add_parser("promote-release")
    promote_parser.add_argument("--repo-root", required=True, type=Path)
    promote_parser.add_argument("--candidate", required=True)
    promote_parser.add_argument("--final", required=True)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "run-validation":
        run_validation(
            args.registry,
            args.manifest,
            args.manifest_schema,
            args.summary,
            args.summary_schema,
            args.workspace,
        )
    elif args.command == "collect-results":
        render_results(args.summary, args.matrix, args.conformance, args.artifacts)
    elif args.command == "promote-release":
        promote_release(args.repo_root, args.candidate, args.final)


if __name__ == "__main__":
    main()
