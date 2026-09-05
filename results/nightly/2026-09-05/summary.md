# Nightly Test Results — 2026-09-05

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 480000 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 1ms | 4ms | 180000 |
| path-users | 2000/s | 0ms | 2ms | 120000 |
| path-orders | 2000/s | 0ms | 2ms | 120000 |
| header-data | 1000/s | 0ms | 1ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-ad4cfc35cffda948e46563f8415083b7c720d68e
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

