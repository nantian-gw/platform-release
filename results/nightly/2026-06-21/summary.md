# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 476 passed, 4 failed |
| Performance | 1820109 req @ 6067.00586027351 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 1ms |
| p90       | 18ms |
| p95       | 52ms |
| p99       | 62ms |
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
