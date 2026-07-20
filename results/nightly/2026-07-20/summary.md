# Nightly Test Results — 2026-07-20

| Test | Result |
|------|--------|
| Conformance | 503 passed, 5 failed, 27 skipped |
| Performance | 5413969 req @ 9023.3 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 3ms |
| p90       | 8ms |
| p95       | 9ms |
| p99       | 13ms |
| max       | 65ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest-amd64

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

