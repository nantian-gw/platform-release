# Nightly Performance Metrics Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make nightly dataplane CPU and memory samples work in Kind even when metrics-server and `kubectl top` are unavailable.

**Architecture:** Keep resource sampling inside the Vegeta step so it aligns with the measured load window. Add shell helper functions that try `kubectl top` first, then fall back to kubelet Summary API via the Kubernetes API server node proxy. Preserve the existing `cpu_m` and `mem_mi` sample schema while adding diagnostic `source` and `pod` fields.

**Tech Stack:** GitHub Actions YAML, Bash, `kubectl`, `jq`, pytest static workflow tests.

---

## Files

- Create: `docs/superpowers/specs/2026-06-21-nightly-performance-metrics-fallback.md`
- Create: `docs/superpowers/plans/2026-06-21-nightly-performance-metrics-fallback.md`
- Modify: `tests/test_workflows.py`
- Modify: `.github/workflows/nightly-conformance-perf.yml`

## Task 1: Add RED workflow tests

- [x] Add this test to `tests/test_workflows.py`:

```python
def test_nightly_performance_resource_sampler_falls_back_to_kubelet_summary() -> None:
    data = load_workflow("nightly-conformance-perf.yml")
    steps = data["jobs"]["performance"]["steps"]
    vegeta_step = next(step for step in steps if step.get("id") == "vegeta")
    script = vegeta_step["run"]

    assert "capture_dataplane_sample" in script
    assert "sample_from_kubectl_top" in script
    assert "sample_from_kubelet_summary" in script
    assert "kubectl top pod -n nantian-gw" in script
    assert 'kubectl get --raw "/api/v1/nodes/${NODE}/proxy/stats/summary"' in script
    assert "usageNanoCores" in script
    assert "workingSetBytes" in script
    assert "app=nantian-gw-dataplane" in script
```

- [x] Add this test to `tests/test_workflows.py`:

```python
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
```

- [x] Run the focused tests and verify RED:

```bash
.venv/bin/python3 -m pytest tests/test_workflows.py -q
```

Expected result: the new tests fail because the workflow does not yet define the fallback helpers or diagnostic sample fields.

## Task 2: Implement kubelet Summary API fallback

- [x] In `.github/workflows/nightly-conformance-perf.yml`, replace the inline sampler body inside the Vegeta step with these helper functions before the background loop:

```bash
sample_from_kubectl_top() {
  kubectl top pod -n nantian-gw --no-headers 2>/dev/null |
    awk '/dataplane/ {print $1,$2,$3; exit}' |
    awk 'NF >= 3 {
      cpu=$2
      mem=$3
      gsub(/m$/, "", cpu)
      if (mem ~ /Ki$/) {
        gsub(/Ki$/, "", mem)
        mem=int(mem / 1024)
      } else if (mem ~ /Mi$/) {
        gsub(/Mi$/, "", mem)
      } else if (mem ~ /Gi$/) {
        gsub(/Gi$/, "", mem)
        mem=int(mem * 1024)
      }
      print $1, int(cpu), int(mem)
    }'
}

dataplane_pod_info() {
  local info
  info=$(kubectl get pod -n nantian-gw -l app=nantian-gw-dataplane -o json 2>/dev/null |
    jq -r '.items[]? | select(.status.phase == "Running") | [.metadata.name, .spec.nodeName] | @tsv' |
    head -1)
  if [[ -n "${info}" ]]; then
    printf '%s\n' "${info}"
    return 0
  fi

  kubectl get pod -n nantian-gw -o json 2>/dev/null |
    jq -r '.items[]? | select(.status.phase == "Running") | select(.metadata.name | contains("dataplane")) | [.metadata.name, .spec.nodeName] | @tsv' |
    head -1
}

sample_from_kubelet_summary() {
  local info POD NODE
  info=$(dataplane_pod_info)
  if [[ -z "${info}" ]]; then
    return 1
  fi

  POD=$(echo "${info}" | awk '{print $1}')
  NODE=$(echo "${info}" | awk '{print $2}')
  if [[ -z "${POD}" || -z "${NODE}" ]]; then
    return 1
  fi

  kubectl get --raw "/api/v1/nodes/${NODE}/proxy/stats/summary" 2>/dev/null |
    jq -r --arg ns "nantian-gw" --arg pod "${POD}" '
      .pods[]?
      | select(.podRef.namespace == $ns and .podRef.name == $pod) as $pod_stats
      | [
          $pod_stats.podRef.name,
          ((($pod_stats.cpu.usageNanoCores // ([$pod_stats.containers[]?.cpu.usageNanoCores // 0] | add) // 0) / 1000000) | floor),
          ((($pod_stats.memory.workingSetBytes // ([$pod_stats.containers[]?.memory.workingSetBytes // 0] | add) // 0) / 1048576) | floor)
        ]
      | @tsv
    ' |
    head -1
}

capture_dataplane_sample() {
  local minute="$1"
  local source="kubectl-top"
  local sample POD CPU MEM

  sample=$(sample_from_kubectl_top || true)
  if [[ -z "${sample}" ]]; then
    source="kubelet-summary"
    sample=$(sample_from_kubelet_summary || true)
  fi

  if [[ -z "${sample}" ]]; then
    echo "t=${minute}min cpu/memory unavailable from kubectl top and kubelet summary"
    return 0
  fi

  read -r POD CPU MEM <<<"${sample}"
  if ! [[ "${CPU}" =~ ^[0-9]+$ && "${MEM}" =~ ^[0-9]+$ ]]; then
    echo "t=${minute}min invalid cpu/memory sample from ${source}: ${sample}"
    return 0
  fi

  echo "t=${minute}min source=${source} pod=${POD} cpu=${CPU}m mem=${MEM}Mi"
  printf '%s,\n' "$(jq -nc \
    --argjson minute "${minute}" \
    --arg source "${source}" \
    --arg pod "${POD}" \
    --argjson cpu_m "${CPU}" \
    --argjson mem_mi "${MEM}" \
    '{minute:$minute,source:$source,pod:$pod,cpu_m:$cpu_m,mem_mi:$mem_mi}')" >> /tmp/cpu-mem-samples.json
}
```

- [x] Replace the sampler loop body with:

```bash
for i in $(seq 0 11); do
  sleep 60
  capture_dataplane_sample "$i"
done
```

- [x] Run the focused workflow tests and verify GREEN:

```bash
.venv/bin/python3 -m pytest tests/test_workflows.py -q
```

Expected result: all workflow tests pass.

## Task 3: Verify, record, and commit

- [x] Run full tests:

```bash
make test
```

Expected result: all tests pass.

- [x] Run whitespace validation:

```bash
git diff --check
```

Expected result: exits 0.

- [x] Confirm the main checkout pre-existing untracked file remains untouched:

```bash
git -C /root/nantian-gw/platform-release status --short
```

Expected result: still shows only `?? docs/superpowers/specs/2026-06-20-platform-release-fixes.md`.

- [x] Confirm sibling component repositories have no new changes from this task:

```bash
for repo in /root/nantian-gw/gateway /root/nantian-gw/dataplane /root/nantian-gw/dashboard /root/nantian-gw/website /root/nantian-gw/proto /root/nantian-gw/helm-charts; do
  git -C "$repo" status --short
done
```

Expected result: no new changes caused by this task. Pre-existing unrelated changes may still appear.

- [x] Update this Execution Record with exact command outputs.

- [x] Commit:

```bash
git add .github/workflows/nightly-conformance-perf.yml \
  tests/test_workflows.py \
  docs/superpowers/specs/2026-06-21-nightly-performance-metrics-fallback.md \
  docs/superpowers/plans/2026-06-21-nightly-performance-metrics-fallback.md
git commit -m "fix(ci): sample nightly dataplane resources without metrics-server"
```

## Execution Record

- Baseline: `make setup && make test`
  - Result: exit 0; `20 passed in 0.59s`.
- RED: `.venv/bin/python3 -m pytest tests/test_workflows.py -q`
  - Result: exit 1; `2 failed, 5 passed in 0.10s`.
  - Expected failures:
    - `test_nightly_performance_resource_sampler_falls_back_to_kubelet_summary` missing `capture_dataplane_sample`.
    - `test_nightly_performance_resource_samples_include_diagnostics` missing `source`.
- GREEN: `.venv/bin/python3 -m pytest tests/test_workflows.py -q`
  - Result: exit 0; `7 passed in 0.09s`.
- Embedded shell syntax check:

```bash
.venv/bin/python3 - <<'PY'
from pathlib import Path
import subprocess
import yaml
workflow = yaml.safe_load(Path('.github/workflows/nightly-conformance-perf.yml').read_text())
steps = workflow['jobs']['performance']['steps']
script = next(step['run'] for step in steps if step.get('id') == 'vegeta')
proc = subprocess.run(['bash', '-n'], input=script, text=True, capture_output=True)
if proc.returncode != 0:
    print(proc.stdout)
    print(proc.stderr)
raise SystemExit(proc.returncode)
PY
```

  - Result: exit 0.
- Kubelet summary jq pod-level conversion sample:
  - Command parsed `usageNanoCores=12345678` and `workingSetBytes=268435456`.
  - Result: exit 0; output `nantian-gw-dataplane-abc	12	256`.
- Kubelet summary jq container-level fallback sample:
  - Command summed container `usageNanoCores` values `11000000 + 22000000` and memory `134217728 + 67108864`.
  - Result: exit 0; output `nantian-gw-dataplane-def	33	192`.
- Full test: `make test`
  - Result: exit 0; `22 passed in 0.59s`.
- Whitespace: `git diff --check`
  - Result: exit 0; no whitespace errors reported.
- Main checkout boundary: `git -C /root/nantian-gw/platform-release status --short`
  - Result: only the pre-existing `?? docs/superpowers/specs/2026-06-20-platform-release-fixes.md`.
- Sibling repository boundary:

```bash
for repo in /root/nantian-gw/gateway /root/nantian-gw/dataplane /root/nantian-gw/dashboard /root/nantian-gw/website /root/nantian-gw/proto /root/nantian-gw/helm-charts; do
  git -C "$repo" status --short
done
```

  - Result: no changes from this task. Observed pre-existing unrelated gateway/dataplane untracked files and website `.astro` modifications.
