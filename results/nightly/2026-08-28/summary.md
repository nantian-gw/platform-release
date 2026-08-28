# Nightly Test Results — 2026-08-28

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 479999 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 6ms | 17ms | 179999 |
| path-users | 2000/s | 2ms | 9ms | 120000 |
| path-orders | 2000/s | 2ms | 9ms | 120000 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-61a507f8810b649e8d94664ceee4fb1b30abb1f4
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

