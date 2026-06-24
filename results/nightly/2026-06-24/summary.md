# Nightly Test Results — 2026-06-24

| Test | Result |
|------|--------|
| Conformance | 640 passed, 17 failed, 4 skipped |
| Performance | 4754228 req @ 7923.713465580112 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 9ms |
| p95       | 11ms |
| p99       | 15ms |
| max       | 110ms |
| mean      | 5ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

