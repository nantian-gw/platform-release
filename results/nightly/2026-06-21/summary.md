# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 5 passed, 1 failed, 51 skipped |
| Performance | 7584891 req @ 25282.958362085716 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 1ms |
| p90       | 1ms |
| p95       | 2ms |
| p99       | 2ms |
| max       | 49ms |
| mean      | 1ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
