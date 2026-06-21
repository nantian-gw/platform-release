# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 507 passed, 8 failed, 26 skipped |
| Performance | 4682633 req @ 7804.38972117495 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 8ms |
| p95       | 10ms |
| p99       | 13ms |
| max       | 225ms |
| mean      | 4ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
