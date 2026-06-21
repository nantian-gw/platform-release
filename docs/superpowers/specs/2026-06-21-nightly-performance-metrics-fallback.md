# Nightly Performance Metrics Fallback Spec

## Problem

The `platform-release` nightly performance workflow now isolates the dataplane load test from conformance and records warmup/measurement metadata, but the 2026-06-21 run still produced:

```json
"cpu": {"avg_m": 0, "max_m": 0},
"memory": {"avg_mi": 0, "max_mi": 0},
"cpu_mem_samples": []
```

The current sampler depends only on `kubectl top pod -n nantian-gw`. In the Kind-based nightly cluster, metrics-server is not guaranteed to be installed or ready, so `kubectl top` can fail even while the dataplane pod is running. The sampler writes nothing when that command returns no rows, causing the downstream average/max fields to remain zero.

## Goal

Keep the existing `kubectl top` fast path when metrics-server is available, and add a kubelet Summary API fallback so the nightly performance artifact records dataplane CPU and memory samples in Kind without requiring metrics-server.

## Design

The sampler in `.github/workflows/nightly-conformance-perf.yml` will gain explicit shell helpers:

- `sample_from_kubectl_top`: keeps the existing `kubectl top pod -n nantian-gw` path and parses dataplane pod CPU/memory.
- `dataplane_pod_info`: finds a running dataplane pod using the stable selector `app=nantian-gw-dataplane`, falling back to a pod name containing `dataplane` only if the selector returns nothing.
- `sample_from_kubelet_summary`: finds the dataplane pod node and reads `/api/v1/nodes/${NODE}/proxy/stats/summary` through `kubectl get --raw`.
- `capture_dataplane_sample`: tries `kubectl top` first, then kubelet summary, validates numeric values, logs the sample source, and appends a JSON sample line.

The kubelet summary parser will read pod-level `.cpu.usageNanoCores` and `.memory.workingSetBytes`. If pod-level fields are unavailable, it will sum container-level `.containers[].cpu.usageNanoCores` and `.containers[].memory.workingSetBytes`. CPU will be stored as millicores by dividing nanocores by `1_000_000`; memory will be stored as MiB by dividing bytes by `1_048_576`.

Each sample will keep the existing `minute`, `cpu_m`, and `mem_mi` fields, and add `source` plus `pod` for diagnostics. Existing aggregate jq expressions only read `cpu_m` and `mem_mi`, so `performance.json` remains backward-compatible.

## Acceptance Criteria

- The nightly workflow contains a kubelet Summary API fallback using `kubectl get --raw "/api/v1/nodes/${NODE}/proxy/stats/summary"`.
- The workflow still attempts `kubectl top pod -n nantian-gw` before falling back to kubelet summary.
- The fallback locates dataplane pods using `app=nantian-gw-dataplane`.
- The fallback parses `usageNanoCores` and `workingSetBytes`, converting them to `cpu_m` and `mem_mi`.
- Samples include `source` and `pod` fields for diagnostics while preserving `minute`, `cpu_m`, and `mem_mi`.
- Existing warmup/measurement metadata remains unchanged.
- `tests/test_workflows.py` has regression coverage proving the fallback is present.
- `make test` passes in the `platform-release` worktree.
- `git diff --check` reports no whitespace errors.
- The main checkout `/root/nantian-gw/platform-release` remains unchanged except for the pre-existing untracked `docs/superpowers/specs/2026-06-20-platform-release-fixes.md`.
- Sibling component repositories remain untouched by this task.
