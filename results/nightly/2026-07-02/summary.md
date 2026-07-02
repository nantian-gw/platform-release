# Nightly Test Results — 2026-07-02

| Test | Result |
|------|--------|
| Conformance | 606 passed, 15 failed, 4 skipped |
| Performance | 4670066 req @ 7783.4417859851055 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 4ms |
| p90       | 9ms |
| p95       | 11ms |
| p99       | 15ms |
| max       | 95ms |
| mean      | 5ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution

