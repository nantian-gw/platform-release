# Nightly Test Results — 2026-06-21

| Test | Result |
|------|--------|
| Conformance | 476 passed, 4 failed |
| Performance | 1808645 req @ 6028.185549216658 RPS

| Percentile | Latency |
|-----------|---------|
| p50       | 1ms |
| p90       | 10ms |
| p95       | 60ms |
| p99       | 65ms |
| max       | 102ms |
| mean      | 6ms | |

Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:latest
- Data Plane: ghcr.io/nantian-gw/dataplane:latest

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta load test summary
- `vegeta-raw.json` — Raw vegeta latency distribution
