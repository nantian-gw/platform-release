# Nightly Test Results — 2026-08-27

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 479967 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 7ms | 18ms | 179968 |
| path-users | 2000/s | 2ms | 11ms | 120000 |
| path-orders | 2000/s | 2ms | 10ms | 120000 |
| header-data | 1000/s | 0ms | 2ms | 59999 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-d2226ac37d6546bd819217d5964ee907610ff73f
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

