# Nightly Test Results — 2026-08-19

| Test | Result |
|------|--------|
| Conformance | 0 passed, 0 failed, 0 skipped |
| Performance | 450941 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 11ms | 24ms | 150942 |
| path-users | 2000/s | 4ms | 17ms | 120000 |
| path-orders | 2000/s | 4ms | 16ms | 119999 |
| header-data | 1000/s | 1ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-85e1610ca3f3875a7a8f9756289214e855211422
- Data Plane: 

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

