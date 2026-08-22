# Platform Release

`platform-release` is the release coordination repository for the `nantian-gw`
GitHub organization.

It does not contain product source code. It contains:

- the managed component registry
- immutable platform release manifests
- validation results and conformance summaries
- operator scripts and GitHub Actions workflows

## Managed Repositories

- `https://github.com/nantian-gw/gateway`
- `https://github.com/nantian-gw/dataplane`
- `https://github.com/nantian-gw/proto`
- `https://github.com/nantian-gw/dashboard`
- `https://github.com/nantian-gw/website`
- `https://github.com/nantian-gw/helm-charts`

## Layout

```text
components/  managed repository registry and canonical validation commands
releases/    immutable candidate and final release inputs
results/     machine-readable and human-readable release evidence
schemas/     JSON schemas for manifests and summaries
scripts/     operator entrypoints
tools/       Python helpers used by scripts and CI
```

## Read More

- [Repository Architecture](docs/architecture.md)
- [Release Process](docs/release-process.md)

## Quickstart

```bash
make setup
make test
make lint
make doctor
```

`make doctor` inspects the sibling component checkouts listed in `components/components.yaml`, reports dirty/ahead/behind state, and summarizes latest main-branch GitHub Actions status. Use `scripts/workspace-doctor.sh --no-actions --strict` when you need a local-only gate without GitHub API calls.

From the repository root, after component tags and published artifacts exist,
you can generate a candidate release tree, run validation, and render the
human-readable results:

```bash
./scripts/resolve-release.sh v2026.06.0-rc1
./scripts/run-validation.sh releases/v2026.06.0-rc1/manifest.yaml results/v2026.06.0-rc1/summary.yaml .work/v2026.06.0-rc1
./scripts/collect-results.sh results/v2026.06.0-rc1/summary.yaml results/v2026.06.0-rc1/test-matrix.md results/v2026.06.0-rc1/conformance.md results/v2026.06.0-rc1/artifacts.yaml
```
