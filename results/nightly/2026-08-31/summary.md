# Nightly Test Results — 2026-08-31

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 479998 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 2ms | 8ms | 179998 |
| path-users | 2000/s | 0ms | 3ms | 120000 |
| path-orders | 2000/s | 0ms | 3ms | 120000 |
| header-data | 1000/s | 0ms | 1ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-7dc8cfc362b7a29ca8fdc0e09a9e52475dfe5c25
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

