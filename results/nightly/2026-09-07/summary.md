# Nightly Test Results — 2026-09-07

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 465748 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 10ms | 23ms | 165749 |
| path-users | 2000/s | 3ms | 12ms | 120000 |
| path-orders | 2000/s | 3ms | 13ms | 119999 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-7e0f8f8ba95b17dc52628e401e9a5d5bbcfb73ec
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

