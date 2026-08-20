# Nightly Test Results — 2026-08-20

| Test | Result |
|------|--------|
| Conformance | 0 passed, 0 failed, 0 skipped |
| Performance | 473016 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 21ms | 173017 |
| path-users | 2000/s | 3ms | 14ms | 120000 |
| path-orders | 2000/s | 3ms | 13ms | 119999 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-adc0a9d65333440e00b30a1dabd75bef600a8c50
- Data Plane: 

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

