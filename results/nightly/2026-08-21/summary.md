# Nightly Test Results — 2026-08-21

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 465863 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 10ms | 23ms | 165865 |
| path-users | 2000/s | 3ms | 13ms | 119998 |
| path-orders | 2000/s | 3ms | 14ms | 120000 |
| header-data | 1000/s | 0ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-bb974c7c20c071107522812749be8d4753eb7b65
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

