# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 646 passed, 7 failed, 4 skipped |
| Performance | 4573253 req @ 7622.087143144427 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 8ms |
| p95       | 10ms |
| p99       | 14ms |
| max       | 109ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
