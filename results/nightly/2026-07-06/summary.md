# Nightly Test Results — 2026-07-06

| Test | Result |
|------|--------|
| Conformance | 649 passed, 8 failed, 4 skipped |
| Performance | 5528109 req @ 9213.514148932341 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 7ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 70ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

