# Nightly Test Results — 2026-07-04

| Test | Result |
|------|--------|
| Conformance | 667 passed, 8 failed, 4 skipped |
| Performance | 7461739 req @ 12436.214137470482 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 2ms |
| p90       | 5ms |
| p95       | 7ms |
| p99       | 9ms |
| max       | 367ms |
| mean      | 3ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:v2026.06.1-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

