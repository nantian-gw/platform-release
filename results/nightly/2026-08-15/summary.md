# Nightly Test Results — 2026-08-15

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 468297 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 22ms | 168297 |
| path-users | 2000/s | 3ms | 15ms | 120000 |
| path-orders | 2000/s | 3ms | 14ms | 120000 |
| header-data | 1000/s | 0ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-92b5c8dd9088475a9b47df127f7dee84605b64bd
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

