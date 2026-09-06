# Nightly Test Results — 2026-09-06

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 475392 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 9ms | 21ms | 175393 |
| path-users | 2000/s | 3ms | 15ms | 119999 |
| path-orders | 2000/s | 3ms | 15ms | 120000 |
| header-data | 1000/s | 0ms | 3ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-9afdb46012b0ff1de5fd58811ac5d8c0a364ae5d
- Data Plane: 

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

