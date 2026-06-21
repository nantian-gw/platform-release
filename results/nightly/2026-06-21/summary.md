# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 476 passed, 4 failed |
| Performance | 10964368 req @ 6091.297543274003 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 1ms |
| p90       | 21ms |
| p95       | 49ms |
| p99       | 60ms |
| max       | 84ms |
| mean      | 6ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
