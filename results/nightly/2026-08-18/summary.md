# Nightly Test Results — 2026-08-18

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 479999 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 2ms | 11ms | 180001 |
| path-users | 2000/s | 0ms | 4ms | 119999 |
| path-orders | 2000/s | 0ms | 4ms | 120000 |
| header-data | 1000/s | 0ms | 1ms | 59999 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-2945f124638cd40800b96eded8c24a0ec5c78089
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

