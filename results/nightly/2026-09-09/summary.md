# Nightly Test Results — 2026-09-09

| Test | Result |
|------|--------|
| Conformance | 615 passed, 0 failed, 22 skipped |
| Performance | 801506 fixed-rate requests, success rate 1, saturation 50.015 RPS |

## Performance Scenarios

| Scenario | Rate | p50 | p95 | p99 | Requests | Success |
|----------|------|-----|-----|-----|----------|---------|
| simple | 3000/s | 9ms | 17ms | 22ms | 171506 | 1 |
| path-users | 2000/s | 3ms | 7ms | 12ms | 120000 | 1 |
| path-orders | 2000/s | 3ms | 7ms | 12ms | 120000 | 1 |
| header-data | 1000/s | 0ms | 1ms | 3ms | 60000 | 1 |
| query-search | 1000/s | 0ms | 1ms | 3ms | 60000 | 1 |
| header-match | 1000/s | 0ms | 1ms | 3ms | 60000 | 1 |
| request-header-filter | 1000/s | 0ms | 1ms | 3ms | 60000 | 1 |
| response-header-filter | 1000/s | 0ms | 1ms | 3ms | 60000 | 1 |
| rewrite-prefix | 1000/s | 0ms | 1ms | 3ms | 60000 | 1 |
| post-body | 500/s | 1ms | 1ms | 2ms | 30000 | 1 |

## Saturation

| Throughput | p50 | p95 | p99 | Requests | Success |
|------------|-----|-----|-----|----------|---------|
| 50.015 RPS | 1ms | 1ms | 1ms | 3000 | 1 |
Images tested:
- Control Plane: ghcr.io/nantian-gw/nantian-controlplane:ci-03f67d41a4dfcef72f1fc536f65419fd2618f3ed
- Data Plane: ghcr.io/nantian-gw/dataplane:sha-29beb12-amd64
- Dashboard: ghcr.io/nantian-gw/dashboard@sha256:f913109dd5c964a48877de15797e1a2e9f08008e978c5ede53fc2ca9be8c601a

## Raw Data Files
- `report.yaml` — Gateway API conformance report
- `run.log` — Full conformance test output
- `performance.json` — Vegeta dataplane load test summary
- `vegeta-raw.json` — Fixed-rate Vegeta scenario summaries
- `vegeta-saturation.json` — Saturation Vegeta max-throughput summary

