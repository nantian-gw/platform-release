# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 476 passed, 4 failed |
| Performance | 10977329 req @ 6098.465834792967 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 1ms |
| p90       | 31ms |
| p95       | 36ms |
| p99       | 43ms |
| max       | 82ms |
| mean      | 6ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
