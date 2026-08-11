# Nightly Test Results — 2026-08-11

| Test | Result |
|------|--------|
| Conformance | no data |
| Performance | 479998 total requests

| Scenario | Rate | p50 | p99 | Requests |
|----------|------|-----|-----|----------|
| simple | 3000/s | 5ms | 16ms | 179998 |
| path-users | 2000/s | 2ms | 8ms | 120000 |
| path-orders | 2000/s | 2ms | 10ms | 120000 |
| header-data | 1000/s | 0ms | 2ms | 60000 |
 |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

