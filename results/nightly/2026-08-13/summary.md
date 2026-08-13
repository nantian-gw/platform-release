# Nightly Test Results — 2026-08-13

| Test | Result |
|------|--------|
| Conformance | 616 passed, 0 failed, 21 skipped |
| Performance | 446770 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 11ms | 25ms | 146771 |
| path-users | 2000/s | 5ms | 18ms | 120000 |
| path-orders | 2000/s | 5ms | 19ms | 119999 |
| header-data | 1000/s | 1ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-81b2333ecf6fe94b565f9d66783c3d23b0cbaebd
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

