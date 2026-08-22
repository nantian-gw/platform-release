# Nightly Test Results — 2026-08-22

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 473562 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 22ms | 173562 |
| path-users | 2000/s | 3ms | 12ms | 120000 |
| path-orders | 2000/s | 3ms | 13ms | 120000 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-ee8ccc3638709fb5304e215c60f63f64697e8495
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

