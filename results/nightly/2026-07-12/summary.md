# Nightly Test Results — 2026-07-12

| Test | Result |
|------|--------|
| Conformance | no data |
| Performance | 7481569 req @ 12469.2 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 2ms |
| p90       | 5ms |
| p95       | 6ms |
| p99       | 9ms |
| max       | 73ms |
| mean      | 3ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

