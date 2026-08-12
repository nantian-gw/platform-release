# Nightly Test Results — 2026-08-12

| Test | Result |
|------|--------|
| Conformance | 594 passed, 0 failed, 24 skipped |
| Performance | 477160 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 21ms | 177160 |
| path-users | 2000/s | 3ms | 14ms | 120000 |
| path-orders | 2000/s | 3ms | 13ms | 120000 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-a25254a12c29a5b33d1bff4bb8e47005ce27bada
- Data Plane: 

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

