# Nightly Test Results — 2026-08-17

| Test | Result |
|------|--------|
| Conformance | 0 passed, 0 failed, 0 skipped |
| Performance | 472998 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 21ms | 172999 |
| path-users | 2000/s | 3ms | 13ms | 119999 |
| path-orders | 2000/s | 3ms | 12ms | 120000 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-7d50a1d2fde959d5636494d938d3442da81a64ca
- Data Plane: 

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

