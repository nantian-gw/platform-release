# Nightly Test Results — 2026-07-07

| Test | Result |
|------|--------|
| Conformance | 5 passed, 0
0 failed, 0
0 skipped |
| Performance | 4806366 req @ 8010.5967590042455 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 9ms |
| p95       | 11ms |
| p99       | 15ms |
| max       | 79ms |
| mean      | 5ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

