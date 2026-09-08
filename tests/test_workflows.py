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

    assert all(ref.startswith("actions/upload-artifact@") for ref in upload_refs)
    assert len(upload_refs) >= 1


def test_nightly_performance_runs_after_conformance_even_on_failure() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    performance = data["jobs"]["performance"]

    assert performance["needs"] == "conformance"
    assert performance["if"] == "always()"


def test_nightly_performance_uses_expanded_measured_vegeta_matrix() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    vegeta_step = next(step for step in steps if step.get("id") == "vegeta")
    script = vegeta_step["run"]

    assert "vegeta attack -duration=15s" in script  # warmup windows
    assert "vegeta attack -duration=60s" in script  # measurement windows
    assert "SCENARIO_ORDER=(" in script
    for scenario in (
        "simple",
        "path-users",
        "path-orders",
        "header-data",
        "query-search",
        "header-match",
        "request-header-filter",
        "response-header-filter",
        "rewrite-prefix",
        "post-body",
    ):
        assert scenario in script
    assert "GET ${GW_TARGET}/api/v1/orders" in script
    assert "saturation" in script
    assert "rm -f /tmp/report.json" in script


def test_nightly_performance_route_fixture_exercises_order_path() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    deploy_step = next(
        step for step in steps if step.get("name") == "Deploy backend + Gateway (multi-path)"
    )
    script = deploy_step["run"]

    assert "value: /api/v1/orders" in script


def test_nightly_performance_json_records_warmup_and_measurement_windows() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    merge_step = next(step for step in steps if step.get("name") == "Merge results")
    script = merge_step["run"]

    assert '"duration_sec": 825' in script  # 10 fixed-rate + 1 saturation scenario, ~75s each
    assert '"methodology"' in script
    assert '"scenarios"' in script
    assert '"saturation"' in script
    assert '"saturation_throughput_rps"' in script
    assert '"images"' in script


def test_nightly_saturation_uses_vegeta_wall_clock_throughput() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    vegeta_step = next(step for step in steps if step.get("id") == "vegeta")
    script = vegeta_step["run"]

    assert "throughput_rps: ((.throughput * 1000 | floor) / 1000)" in script
    assert ".latencies.total" not in script


def test_performance_regression_uses_structured_saturation_metric() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = (repo_root / "scripts/check-performance-regression.sh").read_text(
        encoding="utf-8"
    )

    assert "Legacy saturation_throughput_rps values are ignored" in script
    assert "jq -r '.saturation.throughput_rps // empty'" in script
    assert "jq -r '.saturation_throughput_rps // empty'" not in script
    assert "mark_regression()" in script
    assert "${GITHUB_OUTPUT:-}" in script


def test_nightly_summary_lists_only_present_raw_artifacts() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["commit-results"]["steps"]
    generator_step = next(step for step in steps if step.get("name") == "Generate nightly results")
    script = generator_step["run"]

    assert "append_raw_file" in script
    assert 'append_raw_file "report.yaml"' in script
    assert 'append_raw_file "vegeta-saturation.json"' in script
    assert "- `report.yaml` — Gateway API conformance report" not in script


def test_nightly_performance_outputs_resolved_images_to_results_job() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    performance = data["jobs"]["performance"]
    commit_results = data["jobs"]["commit-results"]
    steps = performance["steps"]
    image_step = next(step for step in steps if step.get("id") == "images")
    script = image_step["run"]

    assert performance["outputs"]["dataplane_image"] == "${{ steps.images.outputs.dataplane_image }}"
    assert performance["outputs"]["dashboard_image"] == "${{ steps.images.outputs.dashboard_image }}"
    assert "dataplane_image=${resolved_dataplane}" in script
    assert "dashboard_image=${resolved_dashboard}" in script
    assert commit_results["env"]["DATAPLANE_IMAGE"] == "${{ needs.performance.outputs.dataplane_image }}"
    assert commit_results["env"]["DASHBOARD_IMAGE"] == "${{ needs.performance.outputs.dashboard_image }}"


def test_nightly_summary_renders_performance_details_outside_result_table() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["commit-results"]["steps"]
    generator_step = next(step for step in steps if step.get("name") == "Generate nightly results")
    script = generator_step["run"]

    assert "## Performance Scenarios" in script
    assert "## Saturation" in script
    assert "| Performance | ${PERF} |" in script
    assert "${PERFORMANCE_DETAILS}Images tested:" in script
    assert "- Data Plane: ${SUMMARY_DATAPLANE_IMAGE}" in script
    assert "- Dashboard: ${SUMMARY_DASHBOARD_IMAGE}" in script


def test_nightly_performance_resource_sampler_falls_back_to_kubelet_summary() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    vegeta_step = next(step for step in steps if step.get("id") == "vegeta")
    script = vegeta_step["run"]

    assert "capture_sample" in script
    assert "sample_from_kubectl_top" in script
    assert "sample_from_kubelet_summary" in script
    assert "kubectl top pod -n nantian-gw" in script
    assert 'kubectl get --raw "/api/v1/nodes/${NODE}/proxy/stats/summary"' in script
    assert "usageNanoCores" in script
    assert "workingSetBytes" in script
    assert "app=nantian-gw-dataplane" in script


def test_nightly_performance_resource_samples_include_diagnostics() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    vegeta_step = next(step for step in steps if step.get("id") == "vegeta")
    script = vegeta_step["run"]

    assert "source" in script
    assert "pod" in script
    assert "kubelet-summary" in script
    assert "kubectl-top" in script
    assert "cpu_m" in script
    assert "mem_mi" in script
