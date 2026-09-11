from pathlib import Path

import yaml


def load_registry() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    return yaml.safe_load((repo_root / "components/components.yaml").read_text(encoding="utf-8"))


def validation_commands(registry: dict, component: str) -> dict[str, str]:
    entries = registry["components"][component]["validate"]
    return {entry["id"]: entry["run"] for entry in entries}


def test_proto_validation_covers_generation_lint_and_format() -> None:
    commands = validation_commands(load_registry(), "proto")

    assert commands["proto-generate"] == "make generate"
    assert commands["proto-lint"] == "buf lint"
    assert commands["proto-format"] == "buf format -d --exit-code"


def test_helm_validation_covers_lint_and_template_render() -> None:
    commands = validation_commands(load_registry(), "helm-charts")

    assert commands["helm-lint"] == "helm lint charts/nantian-gw"
    assert commands["helm-template"] == "helm template --debug charts/nantian-gw"

