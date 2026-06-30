# Nightly Test Results — 2026-06-30

| Test | Result |
|------|--------|
| Conformance | 615 passed, 12 failed, 4 skipped |
| Performance | 5571942 req @ 9286.567127184982 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 7ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 62ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

