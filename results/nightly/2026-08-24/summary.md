# Nightly Test Results — 2026-08-24

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 449724 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 11ms | 24ms | 149725 |
| path-users | 2000/s | 4ms | 18ms | 120000 |
| path-orders | 2000/s | 5ms | 18ms | 119999 |
| header-data | 1000/s | 1ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-618552e754a59795e22586b6dd0eb702acafa65d
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

