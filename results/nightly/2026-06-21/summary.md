# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 590 passed, 0
0 failed, 26 skipped |
| Performance | 4560568 req @ 7600.940858889103 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 8ms |
| p95       | 10ms |
| p99       | 14ms |
| max       | 100ms |
| mean      | 5ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
