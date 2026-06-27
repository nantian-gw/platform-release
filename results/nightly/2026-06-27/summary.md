# Nightly Test Results — 2026-06-27

| Test | Result |
|------|--------|
| Conformance | 600 passed, 12 failed, 4 skipped |
| Performance | 7581055 req @ 12635.088328097278 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 2ms |
| p90       | 5ms |
| p95       | 6ms |
| p99       | 9ms |
| max       | 71ms |
| mean      | 3ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

