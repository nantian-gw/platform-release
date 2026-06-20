# Nightly Conformance + Performance Workflow

**Date**: 2026-06-20
**Scope**: New GitHub Actions workflow in platform-release

## Goal

Daily automated conformance and performance testing against pre-built `latest` images, with results committed back to the repo for historical tracking.

## Design

### Workflow: `nightly-conformance-perf.yml`

**Triggers**: `schedule` (daily 02:00 UTC) + `workflow_dispatch`
**Permissions**: `contents: write` (to commit results), `packages: read` (to pull images)

### Jobs

| Job | Runtime | Description |
|-----|---------|-------------|
| conformance | 75 min | Gateway API conformance (standard + all-features) |
| performance | 30 min | HTTP load test via `hey` |
| commit-results | 2 min | Commit results to `results/nightly/<date>/` |

### Results Storage

```
results/nightly/
├── 2026-06-21/
│   ├── conformance-report.yaml
│   ├── performance.json
│   └── summary.md
├── 2026-06-22/
│   └── ...
```

### Conformance Job Steps

1. Checkout `nantian-gw/gateway` (for conformance tests + deploy scripts)
2. Install kind, kubectl, Gateway API CRDs
3. Create kind cluster
4. Pull `latest` images, load into kind
5. Deploy with kustomize (kind-conformance overlay)
6. Run `go test -tags=conformance ./conformance/`
7. Upload report artifact

### Performance Job Steps

1. Checkout `nantian-gw/gateway`
2. Install kind + kubectl + `hey`
3. Create kind cluster
4. Pull `latest` images, deploy same as conformance
5. Run hey load test (10k requests, 50 concurrent)
6. Parse hey JSON output into performance.json
7. Upload artifact

### Commit-Results Job Steps

1. Download both artifacts
2. Create `results/nightly/<date>/` directory
3. Generate `summary.md`
4. Commit and push to main

## Acceptance

- Workflow triggers on schedule and manual dispatch
- Results committed to `results/nightly/` with date-based directories
- Conformance YAML report saved
- Performance JSON with latency/throughput saved
- Summary markdown with pass/fail and key metrics
