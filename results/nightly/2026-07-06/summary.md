# Nightly Test Results — 2026-07-06

| Test | Result |
|------|--------|
| Conformance | 5 passed, 0
0 failed, 0
0 skipped |
| Performance | 5381260 req @ 8968.751943772746 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 8ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 89ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:v2026.06.3-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

