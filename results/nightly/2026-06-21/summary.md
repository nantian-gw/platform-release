# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 476 passed, 4 failed |
| Performance | 6376703 req @ 21255.686348135834 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 1ms |
| p90       | 2ms |
| p95       | 2ms |
| p99       | 3ms |
| max       | 54ms |
| mean      | 1ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
