# v2026.08.0-alpha.1 Release Notes

**Release Date**: 2026-08-13

**Status**: alpha (pre-release)

This is the first alpha release of the v2026.08 cycle. It includes significant
improvements across all components since the v2026.06.0 GA release.

## Highlights

- **Delta xDS**: Incremental configuration delivery between control plane and data plane
- **Conformance**: 594+ tests passing, 0 failures, only mesh tests skipped
- **BackendTLSPolicy**: Unskipped and passing in conformance
- **WebSocket**: Flaky large-payload test stabilized with retry logic
- **Docker builds**: Version tag support for release automation
- **Lint hygiene**: goconst threshold adjusted, constants extracted in resource_kinds.go
- **Dashboard**: Docker build fixed with correct .dockerignore context
- **Dataplane**: Global allocator fix for benchmark tests
- **Helm chart**: `registry.k8s.io/kubectl` for prereq-check, `featureMode=experimental` for AI/Wasm CRDs
- **Docs**: Updated install docs to match actual defaults (installCRDs: true, tag from appVersion)
- **Release notes**: Added experimental mode installation instructions


## Component Tags

- gateway: `v2026.08.0-alpha.1`
- dataplane: `v2026.08.0-alpha.1`
- proto: `v2026.08.0-alpha.1`
- dashboard: `v2026.08.0-alpha.1`
- website: `v2026.08.0-alpha.1`
- helm-charts: `v2026.08.0-alpha.1`

## Installation

```bash
helm repo add nantian-gw https://chart.nantian.dev
helm repo update
helm install nantian-gw nantian-gw/nantian-gw --version 0.4.0-alpha.1 --namespace nantian-gw --create-namespace

# For AI Gateway, Wasm, and experimental features:
# helm install nantian-gw nantian-gw/nantian-gw --version 0.4.0-alpha.1 \
#   --namespace nantian-gw --create-namespace --set featureMode=experimental
```
