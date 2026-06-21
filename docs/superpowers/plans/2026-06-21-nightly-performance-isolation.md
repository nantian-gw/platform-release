# Nightly Performance Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the nightly dataplane performance artifact more trustworthy by preventing conformance overlap, adding warmup/measurement metadata, tying resource sampling to the load window, and avoiding broken raw artifact links.

**Architecture:** Keep the existing GitHub Actions workflow and Kind-based performance test. Add static workflow regression tests, then update `.github/workflows/nightly-conformance-perf.yml` so performance depends on conformance, the Vegeta step performs warmup plus measured load, `performance.json` records the measurement phases, and summary generation conditionally lists raw files that exist.

**Tech Stack:** GitHub Actions YAML, Bash embedded in workflow steps, Python pytest with PyYAML workflow inspection.

---

## Files

- Create: `docs/superpowers/specs/2026-06-21-nightly-performance-isolation.md`
- Create: `docs/superpowers/plans/2026-06-21-nightly-performance-isolation.md`
- Modify: `tests/test_workflows.py`
- Modify: `.github/workflows/nightly-conformance-perf.yml`

## Task 1: Add RED workflow regression tests

- [x] Add a helper to `tests/test_workflows.py`:

```python
def load_workflow(name: str) -> dict:
    workflow = Path(__file__).resolve().parents[1] / ".github/workflows" / name
    return yaml.safe_load(workflow.read_text(encoding="utf-8"))
```

- [x] Refactor `test_validate_release_uses_node24_artifact_upload` to call the helper:

```python
def test_validate_release_uses_node24_artifact_upload() -> None:
    data = load_workflow("validate-release.yaml")
    ...
```

- [x] Add a test proving the performance job is serialized after conformance:

```python
def test_nightly_performance_runs_after_conformance_even_on_failure() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    performance = data["jobs"]["performance"]

    assert performance["needs"] == "conformance"
    assert performance["if"] == "always()"
```

- [x] Add a test proving the Vegeta step has a warmup and measured run:

```python
def test_nightly_performance_uses_warmup_before_measured_vegeta_run() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    vegeta_step = next(step for step in steps if step.get("id") == "vegeta")
    script = vegeta_step["run"]

    assert "vegeta attack -duration=60s" in script
    assert "vegeta attack -duration=10m" in script
    assert "Warmup" in script
```

- [x] Add a test proving phase metadata is written into `performance.json`:

```python
def test_nightly_performance_json_records_warmup_and_measurement_windows() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    merge_step = next(step for step in steps if step.get("name") == "Merge results")
    script = merge_step["run"]

    assert '"warmup_sec": 60' in script
    assert '"measurement_sec": 600' in script
```

- [x] Add a test proving summary raw files are listed conditionally:

```python
def test_nightly_summary_lists_only_present_raw_artifacts() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["commit-results"]["steps"]
    generator_step = next(step for step in steps if step.get("name") == "Generate nightly results")
    script = generator_step["run"]

    assert "append_raw_file" in script
    assert 'append_raw_file "report.yaml"' in script
    assert "- `report.yaml` — Gateway API conformance report" not in script
```

- [x] Run the focused tests and verify RED:

```bash
.venv/bin/python3 -m pytest tests/test_workflows.py -q
```

Expected result: the new tests fail because the workflow does not yet have the new dependency, warmup, phase metadata, or conditional raw artifact listing.

## Task 2: Update nightly workflow behavior

- [x] In `.github/workflows/nightly-conformance-perf.yml`, add this to the `performance` job:

```yaml
    needs: conformance
    if: always()
```

- [x] Replace the separate background metrics step with same-step sampling in the `Run vegeta 5-min load test through dataplane` step:

```bash
: > /tmp/cpu-mem-samples.json
(
  for i in $(seq 0 11); do
    sleep 60
    DATA=$(kubectl top pod -n nantian-gw --no-headers 2>/dev/null | awk '/dataplane/ {print $2,$3; exit}')
    CPU=$(echo "$DATA" | awk '{print $1}' | sed 's/m//')
    MEM=$(echo "$DATA" | awk '{print $2}' | sed 's/Mi//')
    if [[ -n "${CPU}" ]]; then
      echo "t=${i}min cpu=${CPU}m mem=${MEM}Mi"
      echo "{\"minute\":$i,\"cpu_m\":${CPU:-0},\"mem_mi\":${MEM:-0}}," >> /tmp/cpu-mem-samples.json
    fi
  done
) &
METRICS_PID=$!
```

- [x] In the same Vegeta step, run a warmup before the measured attack:

```bash
kubectl run vegeta -n nantian-gw --image=peterevans/vegeta:latest --rm --attach --restart=Never -- \
  sh -c "printf 'GET http://${GW_SVC}/\n' > /tmp/targets && \
    echo 'Warmup: 60s' >&2 && \
    vegeta attack -duration=60s -rate=0 -max-workers=50 -targets=/tmp/targets >/tmp/vegeta-warmup.bin && \
    vegeta report /tmp/vegeta-warmup.bin >&2 && \
    echo 'Measurement: 10m' >&2 && \
    vegeta attack -duration=10m -rate=0 -max-workers=50 -targets=/tmp/targets | vegeta report -type=json" \
  > /tmp/vegeta-output.json 2>/tmp/vegeta-stderr.txt || true
```

- [x] After the Vegeta command, stop the sampler:

```bash
kill "${METRICS_PID}" 2>/dev/null || true
wait "${METRICS_PID}" 2>/dev/null || true
```

- [x] In `performance.json`, add:

```json
"warmup_sec": 60,
"measurement_sec": 600,
```

- [x] In the summary generator, add a helper before writing `summary.md`:

```bash
raw_files=""
append_raw_file() {
  local file="$1"
  local description="$2"
  if [[ -f "${RESULTS_DIR}/${file}" ]]; then
    raw_files="${raw_files}- \`${file}\` — ${description}"$'\n'
  fi
}
append_raw_file "report.yaml" "Gateway API conformance report"
append_raw_file "run.log" "Full conformance test output"
append_raw_file "performance.json" "Vegeta dataplane load test summary"
append_raw_file "vegeta-raw.json" "Raw vegeta latency distribution"
if [[ -z "${raw_files}" ]]; then
  raw_files="- No raw data files were produced"$'\n'
fi
```

- [x] Replace the hard-coded Raw Data Files list with:

```bash
${raw_files}
```

- [x] Run focused workflow tests and verify GREEN:

```bash
.venv/bin/python3 -m pytest tests/test_workflows.py -q
```

Expected result: all workflow tests pass.

## Task 3: Verify and commit

- [x] Run full repository tests:

```bash
make test
```

Expected result: all tests pass.

- [x] Run diff whitespace validation:

```bash
git diff --check
```

Expected result: exits 0.

- [x] Confirm the main checkout pre-existing untracked file remains untouched:

```bash
git -C /root/nantian-gw/platform-release status --short
```

Expected result: still shows only the pre-existing `?? docs/superpowers/specs/2026-06-20-platform-release-fixes.md`.

- [x] Confirm sibling component repositories are unchanged by this task:

```bash
for repo in /root/nantian-gw/gateway /root/nantian-gw/dataplane /root/nantian-gw/dashboard /root/nantian-gw/website /root/nantian-gw/proto /root/nantian-gw/helm-charts; do
  git -C "$repo" status --short
done
```

Expected result: no new changes caused by this task. Pre-existing unrelated changes may still appear.

- [ ] Commit:

```bash
git add .github/workflows/nightly-conformance-perf.yml \
  tests/test_workflows.py \
  docs/superpowers/specs/2026-06-21-nightly-performance-isolation.md \
  docs/superpowers/plans/2026-06-21-nightly-performance-isolation.md
git commit -m "fix(ci): isolate nightly performance load test"
```

## Execution Record

- `make setup && make test`
  - Result before implementation: exit 0; `16 passed in 0.57s`.
- `.venv/bin/python3 -m pytest tests/test_workflows.py -q`
  - RED result before workflow changes: exit 1; `4 failed, 1 passed`.
- `.venv/bin/python3 -m pytest tests/test_workflows.py -q`
  - GREEN result after workflow changes: exit 0; `5 passed in 0.06s`.
- `make test`
  - Result: exit 0; `20 passed in 0.57s`.
- `git diff --check`
  - Result: exit 0; no whitespace errors reported.
- `git -C /root/nantian-gw/platform-release status --short`
  - Result: only the pre-existing `?? docs/superpowers/specs/2026-06-20-platform-release-fixes.md` was present in the main checkout.
- `for repo in /root/nantian-gw/gateway /root/nantian-gw/dataplane /root/nantian-gw/dashboard /root/nantian-gw/website /root/nantian-gw/proto /root/nantian-gw/helm-charts; do printf '%s\n' "$repo"; git -C "$repo" status --short; done`
  - Result: no changes from this task were present in sibling component repositories; observed pre-existing unrelated untracked gateway/dataplane files and pre-existing website `.astro` modifications.
