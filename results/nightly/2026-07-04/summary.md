# Nightly Test Results — 2026-07-04

| Test | Result |
|------|--------|
| Conformance | 665 passed, 10 failed, 4 skipped |
| Performance | 4780998 req @ 7968.328392270222 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 9ms |
| p95       | 11ms |
| p99       | 15ms |
| max       | 68ms |
| mean      | 5ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:v2026.06.3-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

