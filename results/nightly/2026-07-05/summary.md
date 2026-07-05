# Nightly Test Results — 2026-07-05

| Test | Result |
|------|--------|
| Conformance | 5 passed, 0
0 failed, 0
0 skipped |
| Performance | 4887360 req @ 8145.592451696691 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 8ms |
| p95       | 10ms |
| p99       | 14ms |
| max       | 103ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:v2026.06.3-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

