# Release Process

This document describes the current operator flow for creating, validating, and
publishing a platform release from this repository.

## Prerequisites

Before creating a platform candidate, the component releases must already
exist:

- component tags must be pushed in the managed repositories
- published image digests must be known for `gateway` and `dataplane`
- the Helm chart version must already be decided

For local work, bootstrap the repository toolchain first:

```bash
make setup
make test
```

## 1. Create A Candidate Release Tree

Use `scripts/resolve-release.sh` to create the candidate release input and the
initial result skeleton.

Example:

```bash
export GATEWAY_TAG=v2026.06.0-rc1
export DATAPLANE_TAG=v2026.06.0-rc1
export PROTO_TAG=v2026.06.0-rc1
export DASHBOARD_TAG=v2026.06.0-rc1
export WEBSITE_TAG=v2026.06.0-rc1
export HELM_CHARTS_TAG=v2026.06.0-rc1
export GATEWAY_IMAGE_DIGEST=sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
export DATAPLANE_IMAGE_DIGEST=sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
export HELM_CHART_VERSION=0.2.3

./scripts/resolve-release.sh v2026.06.0-rc1
```

`resolve-release.sh` does the following:

- validates the platform version format
- validates that required environment variables are present
- resolves exact commits for each component tag
- writes `releases/<version>/manifest.yaml`
- writes `releases/<version>/release-notes.md`
- writes `releases/<version>/compatibility.yaml`
- creates the initial `results/<version>/` files

The script refuses to overwrite an existing `releases/<version>/` or
`results/<version>/` tree.

## 2. Validate The Candidate

Run validation against the new manifest:

```bash
./scripts/run-validation.sh \
  releases/v2026.06.0-rc1/manifest.yaml \
  results/v2026.06.0-rc1/summary.yaml \
  .work/v2026.06.0-rc1
```

This calls `tools/releasectl.py run-validation`, which:

- validates the manifest and summary against the repository schemas
- checks that manifest component entries exactly match the component registry
- enforces the canonical Helm chart repository `https://chart.nantian.dev`
- clones each managed repository at the exact commit recorded in the manifest
- runs the component validation commands from `components/components.yaml`
- runs the platform checks after component checks pass
- writes the final machine-readable verdict to `summary.yaml`

If one check fails, the failing check is marked `failed` and later pending
checks become `skipped-after-failure`.

## 3. Render Human-Readable Results

After validation, render the Markdown outputs and artifact index:

```bash
./scripts/collect-results.sh \
  results/v2026.06.0-rc1/summary.yaml \
  results/v2026.06.0-rc1/test-matrix.md \
  results/v2026.06.0-rc1/conformance.md \
  results/v2026.06.0-rc1/artifacts.yaml
```

This produces:

- `test-matrix.md` with one row per check
- `conformance.md` with the Gateway API conformance status
- `artifacts.yaml` with the GitHub Actions run URL and failure summary, when
  available

## 4. CI Validation Behavior

The repository workflow [`validate-release.yaml`](../.github/workflows/validate-release.yaml)
automates the same validation path for repository changes.

Key behavior:

- it always runs repository unit tests
- it only installs Go, Rust, Node.js, Helm, kubectl, kind, and kustomize when
  a `releases/*/manifest.yaml` file changed
- it validates each changed manifest and uploads `results/` plus `.work/` as
  artifacts

That means documentation-only or workflow-only changes do not trigger heavy
release validation work unless they also change release input.

## 5. Promote A Passing Candidate

Once `results/<candidate-version>/summary.yaml` reports `status: passed`, the
candidate can be promoted.

Local command:

```bash
./scripts/promote-release.sh v2026.06.0-rc1 v2026.06.0
```

This calls `tools/releasectl.py promote-release`, which:

- verifies the candidate summary status is `passed`
- copies `releases/<candidate>/` to `releases/<final>/`
- copies `results/<candidate>/` to `results/<final>/`
- rewrites the final manifest status to `released`
- rewrites the final summary `platformVersion`

The promotion command refuses to overwrite an existing final release tree.

## 6. Publish The Final Release

The repository provides a manual GitHub Actions workflow,
[`publish-release.yaml`](../.github/workflows/publish-release.yaml), to publish
the final release from `main`.

Inputs:

- `candidate_version`
- `final_version`

The workflow:

- runs the promotion logic
- commits the new final `releases/` and `results/` directories
- creates the corresponding git tag
- pushes `main`
- pushes the tag
- creates the GitHub Release using `releases/<final-version>/release-notes.md`

## Resulting Artifacts

After a complete successful release flow, the repository contains both the
platform input and the evidence:

- `releases/<final-version>/` is the published release contract
- `results/<final-version>/` is the published validation evidence

The external publication surfaces are:

- the repository `main` branch history
- the release git tag
- the GitHub Release entry for the final version

That combination makes the platform release reproducible and auditable.
