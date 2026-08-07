# Nightly Test Results — 2026-08-07

| Test | Result |
|------|--------|
| Conformance | 594 passed, 0 failed, 24 skipped |
| Performance | 479999 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 0ms | 4ms | 180000 |
| path-users | 2000/s | 0ms | 2ms | 119999 |
| path-orders | 2000/s | 0ms | 2ms | 120000 |
| header-data | 1000/s | 0ms | 1ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

