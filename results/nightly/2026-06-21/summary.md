# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 563 passed, 9 failed, 4 skipped |
| Performance | 5120008 req @ 8533.345776524924 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 7ms |
| p95       | 9ms |
| p99       | 12ms |
| max       | 733ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
