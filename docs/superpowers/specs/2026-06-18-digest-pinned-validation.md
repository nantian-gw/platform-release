# Digest-Pinned Validation Spec

## Problem

`run-validation` validates component source checkouts at the manifest commits, but platform checks such as `make e2e-smoke` and `make conformance` run from the gateway checkout without injecting the release manifest image artifacts. Gateway's Makefile defaults the runtime images to `ghcr.io/nantian-gw/*:latest`, so validation evidence can pass against mutable `latest` images instead of the image digests recorded in the manifest.

This breaks the release evidence contract for `v2026.06.0-rc4`: conformance and install validation must prove the candidate manifest artifacts, not whatever `latest` points to at validation time.

## Requirements

- `run-validation` must pull `manifest.artifacts.containerImages.gateway` and retag it to an immutable local validation alias before gateway platform checks.
- `run-validation` must pull `manifest.artifacts.containerImages.dataplane` and retag it to an immutable local validation alias before gateway platform checks.
- `run-validation` must pass `CONTROL_PLANE_IMAGE` and `DATA_PLANE_IMAGE` as those local validation aliases to gateway platform checks.
- The local validation aliases must be derived from `manifest.platformVersion`, so logs can correlate them to the release candidate while avoiding mutable public tags.
- `run-validation` must not require a dashboard digest because the current manifest schema does not record one.
- Existing component validation commands must retain current behavior.
- Summary status handling must remain unchanged for success, active failure, and checkout failure.
- Validation evidence for `v2026.06.0-rc4` must be regenerated after the fix.

## Acceptance Criteria

- `tests/test_releasectl.py` contains a regression test proving release image digest aliases are prepared from the manifest and `make e2e-smoke` / `make conformance` receive those alias image environment variables.
- The new regression test fails before the implementation change and passes after it.
- `make test` passes in the `platform-release` repository.
- `git diff --check` reports no whitespace errors.
- `./scripts/run-validation.sh releases/v2026.06.0-rc4/manifest.yaml results/v2026.06.0-rc4/summary.yaml .work/v2026.06.0-rc4` passes after removing the stale `.work/v2026.06.0-rc4` validation workspace.
- Validation logs show `ghcr.io/nantian-gw/nantian-controlplane@sha256:5bcb94c10a7bf6e83d89b31928cba7a620ed78e5530b057bfe0ea5af7d098379` and `ghcr.io/nantian-gw/dataplane@sha256:162a5c1b2166653b79684eb8ce25b0063c5d959d95e94e608f13eb04855c605f` are pulled and retagged to local validation aliases before the gateway platform checks.
- `./scripts/collect-results.sh results/v2026.06.0-rc4/summary.yaml results/v2026.06.0-rc4/test-matrix.md results/v2026.06.0-rc4/conformance.md results/v2026.06.0-rc4/artifacts.yaml` regenerates result reports.
- `results/v2026.06.0-rc4/summary.yaml` reports `status: passed` and `gateway-api-conformance: passed`.
- No component repository worktrees (`gateway`, `dataplane`, `proto`, `dashboard`, `website`, `helm-charts`) are modified by this platform-release fix.
