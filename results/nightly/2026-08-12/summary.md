# Nightly Test Results — 2026-08-12

| Test | Result |
|------|--------|
| Conformance | 595 passed, 0 failed, 24 skipped |
| Performance | 475329 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 21ms | 175329 |
| path-users | 2000/s | 3ms | 14ms | 120000 |
| path-orders | 2000/s | 3ms | 15ms | 120000 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-3dfe185dfff493357f2218a5beccb85935e77155
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

