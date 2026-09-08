# Nightly Test Results — 2026-09-08

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 462063 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 10ms | 24ms | 162063 |
| path-users | 2000/s | 3ms | 17ms | 120000 |
| path-orders | 2000/s | 4ms | 19ms | 120000 |
| header-data | 1000/s | 0ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-52c3273bc2e699fd7b1259757d4eb4b822e9cc13
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

