# Nightly Test Results — 2026-08-23

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 449080 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 11ms | 24ms | 149080 |
| path-users | 2000/s | 4ms | 19ms | 120000 |
| path-orders | 2000/s | 4ms | 18ms | 120000 |
| header-data | 1000/s | 1ms | 5ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-3a8cbff4885f4b431222bf5d45a4ab569399d313
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

