# Nightly Performance Isolation Design

## Problem

The 2026-06-21 nightly result reports dataplane p99 latency around 13 ms and a
733 ms maximum latency. The raw artifacts show the 600 second Vegeta load test
ran from `2026-06-21T12:38:09Z` to `2026-06-21T12:48:09Z`. The same run log
shows Gateway API conformance creating, updating, and deleting Gateway API
resources during the beginning of that window.

Because the `conformance` and `performance` jobs currently have no dependency
between them, GitHub Actions can run both jobs at the same time. Even though
they use separate Kind clusters, they share the same GitHub-hosted runner class
and both stress Docker, Kind, kubectl, image layers, and the host scheduler.
That makes dataplane p99 hard to attribute.

The 2026-06-21 artifacts also recorded `cpu.avg_m = 0`, `memory.avg_mi = 0`,
and an empty `cpu_mem_samples` list. The workflow starts metrics collection in
one shell step and later calls `wait` in a different shell step, so the load
test result is not reliably tied to the resource sampler. The summary also
always lists `report.yaml` even when that file is not present.

## Goals

- Ensure the dataplane performance job does not overlap with the conformance
  job by making it run after conformance completes, even if conformance fails.
- Add an explicit warmup phase before the measured Vegeta run so connection
  setup and initial dataplane state do not pollute measurement percentiles.
- Keep resource sampling in the same workflow step as the measured load test
  so sampled data is tied to the measurement window.
- Record warmup and measurement durations in `performance.json`.
- Generate the nightly summary so raw artifact links are listed only when the
  artifact was actually copied into `results/nightly/<date>/`.
- Preserve the existing separate Kind clusters and do not change component
  source repositories.

## Non-Goals

- Do not change dataplane runtime, gateway controller behavior, or Gateway API
  conformance test semantics.
- Do not introduce a new performance target service or a different load
  generator.
- Do not make the nightly performance test digest-pinned in this change; the
  workflow still tests the configured image tags, and image digest pinning can
  be handled separately.
- Do not retroactively rewrite existing nightly result directories.

## Design

The `performance` job will declare `needs: conformance` and `if: always()`.
This keeps performance evidence available even when conformance fails, but it
prevents conformance activity from running concurrently with the load test.

The Vegeta step will initialize `/tmp/cpu-mem-samples.json`, start a sampler
background process in the same shell step, run a 60 second warmup attack, then
run the existing 10 minute measured attack. The sampler records dataplane CPU
and memory samples when `kubectl top` is available and leaves the sample file
empty otherwise. The merge step will continue to treat an empty sample file as
no resource data, but `performance.json` will now include `warmup_sec` and
`measurement_sec` to make the measurement window explicit.

The summary generator will build the Raw Data Files section conditionally from
files present in the results directory. `report.yaml`, `run.log`,
`performance.json`, and `vegeta-raw.json` will only be listed when each file is
present. This avoids publishing broken links when a workflow artifact was not
created.

## Expected Behavior

- Nightly conformance still uploads conformance artifacts.
- Nightly performance starts only after the conformance job completes or fails.
- Performance still runs in its own `nightly-perf` Kind cluster.
- Vegeta output in `performance.json` represents the measured 10 minute run
  only, not the warmup.
- `summary.md` can be used to determine which raw files are actually available.

## Acceptance Criteria

- `make setup` succeeds in the `platform-release` worktree.
- A workflow test proves `performance` has `needs: conformance` and
  `if: always()`.
- A workflow test proves the Vegeta command contains a 60 second warmup and a
  10 minute measured run.
- A workflow test proves `performance.json` records `warmup_sec` and
  `measurement_sec`.
- A workflow test proves summary raw file entries are appended conditionally
  instead of always listing `report.yaml`.
- `make test` passes in the `platform-release` worktree.
- `git diff --check` passes in the `platform-release` worktree.
- The main checkout's pre-existing untracked file
  `docs/superpowers/specs/2026-06-20-platform-release-fixes.md` remains
  untouched.
- Sibling component repositories remain unchanged by this task.
