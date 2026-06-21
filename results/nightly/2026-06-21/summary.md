# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 652 passed, 8 failed, 4 skipped |
| Performance | 4998463 req @ 8330.759508478548 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 8ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 416ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

