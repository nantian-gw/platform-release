# Nightly Test Results — 2026-08-02

| Test | Result |
|------|--------|
| Conformance | 540 passed, 32 failed, 10 skipped |
| Performance | 479997 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 8ms | 18ms | 179999 |
| path-users | 2000/s | 2ms | 9ms | 119998 |
| path-orders | 2000/s | 2ms | 10ms | 120000 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

