# Nightly Test Results — 2026-07-19

| Test | Result |
|------|--------|
| Conformance | 481 passed, 7 failed, 27 skipped |
| Performance | 7903303 req @ 13172.2 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 2ms |
| p90       | 5ms |
| p95       | 6ms |
| p99       | 9ms |
| max       | 63ms |
| mean      | 3ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

