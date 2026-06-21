# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 621 passed, 11 failed, 4 skipped |
| Performance | 5521818 req @ 9203.02885457569 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 7ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 73ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

