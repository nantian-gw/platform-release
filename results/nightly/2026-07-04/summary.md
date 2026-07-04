# Nightly Test Results — 2026-07-04

| Test | Result |
|------|--------|
| Conformance | 638 passed, 9 failed, 4 skipped |
| Performance | 4691762 req @ 7819.603862068881 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 9ms |
| p95       | 11ms |
| p99       | 15ms |
| max       | 73ms |
| mean      | 5ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

