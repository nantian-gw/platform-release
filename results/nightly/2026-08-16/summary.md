# Nightly Test Results — 2026-08-16

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 456360 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 10ms | 23ms | 156362 |
| path-users | 2000/s | 4ms | 16ms | 119998 |
| path-orders | 2000/s | 4ms | 16ms | 120000 |
| header-data | 1000/s | 1ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-29ce0cff4601d1ed9df9bbca7653ac7a7302f060
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

