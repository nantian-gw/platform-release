from pathlib import Path

import yaml


def load_workflow(name: str) -> dict:
    workflow = Path(__file__).resolve().parents[1] / ".github/workflows" / name
    return yaml.safe_load(workflow.read_text(encoding="utf-8"))


def test_validate_release_uses_node24_artifact_upload() -> None:
    data = load_workflow("validate-release.yaml")

    upload_refs = []
    for job in data["jobs"].values():
        for step in job["steps"]:
            uses = step.get("uses")
            if uses and uses.startswith("actions/upload-artifact@"):
                upload_refs.append(uses)

    assert upload_refs == ["actions/upload-artifact@v6"]


def test_nightly_performance_runs_after_conformance_even_on_failure() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    performance = data["jobs"]["performance"]

    assert performance["needs"] == "conformance"
    assert performance["if"] == "always()"


def test_nightly_performance_uses_warmup_before_measured_vegeta_run() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    vegeta_step = next(step for step in steps if step.get("id") == "vegeta")
    script = vegeta_step["run"]

    assert "vegeta attack -duration=60s" in script
    assert "vegeta attack -duration=10m" in script
    assert "Warmup" in script


def test_nightly_performance_json_records_warmup_and_measurement_windows() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    merge_step = next(step for step in steps if step.get("name") == "Merge results")
    script = merge_step["run"]

    assert '"warmup_sec": 60' in script
    assert '"measurement_sec": 600' in script


def test_nightly_summary_lists_only_present_raw_artifacts() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["commit-results"]["steps"]
    generator_step = next(step for step in steps if step.get("name") == "Generate nightly results")
    script = generator_step["run"]

    assert "append_raw_file" in script
    assert 'append_raw_file "report.yaml"' in script
    assert "- `report.yaml` — Gateway API conformance report" not in script
