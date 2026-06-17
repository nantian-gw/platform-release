# Repository Architecture

`platform-release` is the release coordination repository for the
`nantian-gw` organization. It is the platform-level release authority, not a
source repository for the product itself.

## Responsibilities

This repository owns the release contract for one platform version. In
practice, that means it stores:

- the managed component registry
- immutable platform release manifests
- machine-readable validation summaries
- human-readable conformance and test summaries
- operator scripts and GitHub Actions workflows for validation and promotion

This repository does not own component source code. The source of truth for
implementation still lives in the component repositories.

## Managed Repositories

The current managed repositories are:

- `gateway`
- `dataplane`
- `proto`
- `dashboard`
- `website`
- `helm-charts`

Their canonical repository URLs and validation commands live in
[`components/components.yaml`](../components/components.yaml).

## Release Model

Component versions remain independent. A platform release adds one separate
platform version that locks a specific set of component tags, commits, and
immutable artifacts.

Example:

- component tag: `gateway v2026.06.0-rc1`
- component tag: `dataplane v2026.06.0-rc1`
- platform release: `v2026.06.0-rc1`

A component tag alone does not mean the platform has released. A component only
becomes part of a platform release when it is listed in a platform manifest
under `releases/<platform-version>/manifest.yaml`.

## Repository Layout

The repository is organized around release inputs, release results, and the
tooling that connects them.

### `components/`

- `components.yaml` defines the managed repositories.
- Each component entry records the canonical repository URL plus the validation
  commands that `releasectl` should run.
- `platformChecks` records cross-component checks such as install validation and
  Gateway API conformance.

### `releases/`

Each `releases/<platform-version>/` directory is release input:

- `manifest.yaml` is the immutable platform lockfile
- `release-notes.md` is the human-readable operator/user summary
- `compatibility.yaml` records support and compatibility statements

Candidate and final releases both live here. The manifest status distinguishes
them.

### `results/`

Each `results/<platform-version>/` directory is release evidence:

- `summary.yaml` is the machine-readable verdict
- `test-matrix.md` is the rendered validation matrix
- `conformance.md` is the rendered Gateway API conformance summary
- `artifacts.yaml` indexes external evidence such as the GitHub Actions run URL

### `schemas/`

`manifest.schema.json` and `summary.schema.json` enforce the structure of the
core release metadata files.

### `scripts/`

The repository exposes four operator entrypoints:

- `resolve-release.sh` creates a candidate release tree from component tags and
  published artifact digests
- `run-validation.sh` runs validation for one manifest
- `collect-results.sh` renders Markdown and artifact indexes from one summary
- `promote-release.sh` promotes a passing candidate to a final platform release

### `tools/`

`tools/releasectl.py` implements the actual repository logic used by the shell
wrappers and CI:

- schema validation
- canonical manifest checks
- git checkout of exact component commits
- execution of component and platform validation commands
- result rendering
- candidate promotion

## Workflow Responsibilities

The repository has two GitHub Actions workflows.

### `validate-release`

[`validate-release.yaml`](../.github/workflows/validate-release.yaml) runs on
pull requests and pushes to `main`.

It performs two layers of work:

1. `unit-tests`
   - installs Python dependencies
   - runs the repository pytest suite

2. `release-validation`
   - checks whether any `releases/*/manifest.yaml` files changed
   - skips heavyweight toolchain setup if no release manifests changed
   - installs the required toolchains only when a manifest changed
   - runs validation for each changed manifest
   - uploads `results/` and `.work/` as CI artifacts

This keeps ordinary repository changes cheap while preserving full validation
for actual release input changes.

### `publish-release`

[`publish-release.yaml`](../.github/workflows/publish-release.yaml) is manually
triggered on `main`.

It:

- promotes a passing candidate to a final release tree
- commits the resulting `releases/<final-version>/` and
  `results/<final-version>/` directories
- creates the corresponding git tag
- pushes `main` and the tag
- creates the GitHub Release from the final `release-notes.md`

## Validation Execution Model

Validation is intentionally deterministic:

- the manifest records exact commit SHAs and artifact identities
- `releasectl` clones each repository and checks out the recorded commit
- validation commands come from the component registry, not ad-hoc local state
- platform checks run only after component checks succeed

If a validation command fails, `summary.yaml` is marked failed, the active check
is marked `failed`, and remaining pending checks are marked
`skipped-after-failure`.

## Why This Repository Is Separate

Keeping platform release logic in its own repository has two practical
benefits:

- component repositories can evolve independently
- the platform release state stays explicit, reviewable, and auditable in one
  place

That separation is the core design of `platform-release`.
