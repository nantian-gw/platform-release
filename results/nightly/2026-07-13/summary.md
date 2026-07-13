# Nightly Test Results — 2026-07-13

| Test | Result |
|------|--------|
| Conformance | 594 passed, 3 failed, 10 skipped |
| Performance | 10057866 req @ 16763.1 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 2ms |
| p90       | 4ms |
| p95       | 5ms |
| p99       | 7ms |
| max       | 77ms |
| mean      | 2ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

