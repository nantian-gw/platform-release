# Nightly Test Results — 2026-08-01

| Test | Result |
|------|--------|
| Conformance | 599 passed, 29 failed, 5 skipped |
| Performance | 479987 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 5ms | 15ms | 179987 |
| path-users | 2000/s | 2ms | 10ms | 120000 |
| path-orders | 2000/s | 2ms | 11ms | 120000 |
| header-data | 1000/s | 0ms | 2ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

