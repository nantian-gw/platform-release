# Nightly Test Results — 2026-08-21

| Test | Result |
|------|--------|
| Conformance | 0 passed, 0 failed, 0 skipped |
| Performance | 438296 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 12ms | 27ms | 138297 |
| path-users | 2000/s | 5ms | 19ms | 119999 |
| path-orders | 2000/s | 5ms | 18ms | 120000 |
| header-data | 1000/s | 1ms | 4ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-03491d436aba7e3222029217090eca03359f8656
- Data Plane: 

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

