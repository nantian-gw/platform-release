# Nightly Test Results — 2026-06-29

| Test | Result |
|------|--------|
| Conformance | 658 passed, 13 failed, 4 skipped |
| Performance | 5630388 req @ 9383.937423277323 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 7ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 76ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

