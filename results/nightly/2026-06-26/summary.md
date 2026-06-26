# Nightly Test Results — 2026-06-26

| Test | Result |
|------|--------|
| Conformance | 649 passed, 9 failed, 4 skipped |
| Performance | 5398130 req @ 8996.890244069653 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 8ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 61ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

