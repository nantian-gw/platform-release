# Nightly Test Results — 2026-07-06

| Test | Result |
|------|--------|
| Conformance | 528 passed, 7 failed, 10 skipped |
| Performance | 6678030 req @ 11130.05200739763 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 6ms |
| p95       | 8ms |
| p99       | 11ms |
| max       | 84ms |
| mean      | 3ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

