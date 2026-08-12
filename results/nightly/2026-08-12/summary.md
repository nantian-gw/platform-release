# Nightly Test Results — 2026-08-12

| Test | Result |
|------|--------|
| Conformance | 5 passed, 0 failed, 0 skipped |
| Performance | 479981 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 20ms | 179981 |
| path-users | 2000/s | 2ms | 10ms | 120000 |
| path-orders | 2000/s | 2ms | 12ms | 120000 |
| header-data | 1000/s | 1ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

