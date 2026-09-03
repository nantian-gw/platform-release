# Nightly Test Results — 2026-09-03

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 479957 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 20ms | 179973 |
| path-users | 2000/s | 3ms | 12ms | 120000 |
| path-orders | 2000/s | 3ms | 12ms | 119984 |
| header-data | 1000/s | 1ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-4243c4e0922f9fc2775520de718fe9f9f945e563
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

