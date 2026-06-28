# Nightly Test Results — 2026-06-28

| Test | Result |
|------|--------|
| Conformance | 601 passed, 11 failed, 4 skipped |
| Performance | 4921985 req @ 8203.308507940756 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 8ms |
| p95       | 10ms |
| p99       | 14ms |
| max       | 75ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

