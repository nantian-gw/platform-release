# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 5 passed, 1 failed, 51 skipped |
| Performance | 3657942 req @ 12193.141430824504 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 2ms |
| p90       | 5ms |
| p95       | 6ms |
| p99       | 8ms |
| max       | 93ms |
| mean      | 2ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
