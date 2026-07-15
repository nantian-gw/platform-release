# Nightly Test Results — 2026-07-15

| Test | Result |
|------|--------|
| Conformance | 528 passed, 7 failed, 9 skipped |
| Performance | 5602729 req @ 9337.9 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 7ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 96ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

