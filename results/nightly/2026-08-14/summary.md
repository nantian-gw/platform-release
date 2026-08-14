# Nightly Test Results — 2026-08-14

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 448530 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 11ms | 25ms | 148531 |
| path-users | 2000/s | 5ms | 22ms | 119999 |
| path-orders | 2000/s | 4ms | 20ms | 120000 |
| header-data | 1000/s | 1ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-a0d8c4b18c82ee3f81c6bbeaf0dc5cdb667d3806
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

