#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <platform-version>" >&2
  exit 1
fi

platform_version="$1"
version_pattern='^v[0-9]{4}\.[0-9]{2}\.[0-9]+(-rc[0-9]+)?$'

if [[ ! "${platform_version}" =~ ${version_pattern} ]]; then
  echo "platform version must match ${version_pattern}" >&2
  exit 1
fi

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "missing required environment variable: ${name}" >&2
    exit 1
  fi
}

resolve_commit() {
  local repo="$1"
  local tag="$2"
  local sha

  sha="$(git ls-remote --tags "${repo}" "refs/tags/${tag}^{}" | awk '{print $1}')"
  if [[ -z "${sha}" ]]; then
    echo "failed to resolve tag ${tag} in ${repo}" >&2
    exit 1
  fi
  if [[ ! "${sha}" =~ ^[a-f0-9]{40}$ ]]; then
    echo "resolved commit for ${tag} is not a full 40-character SHA: ${sha}" >&2
    exit 1
  fi

  printf '%s\n' "${sha}"
}

require_env GATEWAY_TAG
require_env DATAPLANE_TAG
require_env PROTO_TAG
require_env DASHBOARD_TAG
require_env WEBSITE_TAG
require_env HELM_CHARTS_TAG
require_env GATEWAY_IMAGE_DIGEST
require_env DATAPLANE_IMAGE_DIGEST
require_env HELM_CHART_VERSION

if [[ ! "${GATEWAY_IMAGE_DIGEST}" =~ ^sha256:[a-f0-9]{64}$ ]]; then
  echo "GATEWAY_IMAGE_DIGEST must match sha256:<64 lowercase hex chars>" >&2
  exit 1
fi

if [[ ! "${DATAPLANE_IMAGE_DIGEST}" =~ ^sha256:[a-f0-9]{64}$ ]]; then
  echo "DATAPLANE_IMAGE_DIGEST must match sha256:<64 lowercase hex chars>" >&2
  exit 1
fi

gateway_repo="https://github.com/nantian-gw/gateway"
dataplane_repo="https://github.com/nantian-gw/dataplane"
proto_repo="https://github.com/nantian-gw/proto"
dashboard_repo="https://github.com/nantian-gw/dashboard"
website_repo="https://github.com/nantian-gw/website"
helm_charts_repo="https://github.com/nantian-gw/helm-charts"

gateway_commit="$(resolve_commit "${gateway_repo}" "${GATEWAY_TAG}")"
dataplane_commit="$(resolve_commit "${dataplane_repo}" "${DATAPLANE_TAG}")"
proto_commit="$(resolve_commit "${proto_repo}" "${PROTO_TAG}")"
dashboard_commit="$(resolve_commit "${dashboard_repo}" "${DASHBOARD_TAG}")"
website_commit="$(resolve_commit "${website_repo}" "${WEBSITE_TAG}")"
helm_charts_commit="$(resolve_commit "${helm_charts_repo}" "${HELM_CHARTS_TAG}")"

release_dir="releases/${platform_version}"
results_dir="results/${platform_version}"
release_date="$(date -u +%F)"

mkdir -p "${release_dir}" "${results_dir}"

cat > "${release_dir}/manifest.yaml" <<EOF
platformVersion: ${platform_version}
baseRelease: null
status: candidate
releaseDate: ${release_date}
components:
  gateway:
    repo: ${gateway_repo}
    tag: ${GATEWAY_TAG}
    commit: ${gateway_commit}
  dataplane:
    repo: ${dataplane_repo}
    tag: ${DATAPLANE_TAG}
    commit: ${dataplane_commit}
  proto:
    repo: ${proto_repo}
    tag: ${PROTO_TAG}
    commit: ${proto_commit}
  dashboard:
    repo: ${dashboard_repo}
    tag: ${DASHBOARD_TAG}
    commit: ${dashboard_commit}
  website:
    repo: ${website_repo}
    tag: ${WEBSITE_TAG}
    commit: ${website_commit}
  helm-charts:
    repo: ${helm_charts_repo}
    tag: ${HELM_CHARTS_TAG}
    commit: ${helm_charts_commit}
artifacts:
  containerImages:
    gateway: ghcr.io/nantian-gw/gateway@${GATEWAY_IMAGE_DIGEST}
    dataplane: ghcr.io/nantian-gw/dataplane@${DATAPLANE_IMAGE_DIGEST}
  helmChart:
    name: nantian-gw
    version: ${HELM_CHART_VERSION}
    repo: https://chart.nantian.dev
EOF

cat > "${release_dir}/release-notes.md" <<EOF
# ${platform_version} Release Notes

Status: candidate

## Component Tags

- gateway: \`${GATEWAY_TAG}\`
- dataplane: \`${DATAPLANE_TAG}\`
- proto: \`${PROTO_TAG}\`
- dashboard: \`${DASHBOARD_TAG}\`
- website: \`${WEBSITE_TAG}\`
- helm-charts: \`${HELM_CHARTS_TAG}\`
EOF

cat > "${release_dir}/compatibility.yaml" <<EOF
platformVersion: ${platform_version}
components:
  gateway: ${GATEWAY_TAG}
  dataplane: ${DATAPLANE_TAG}
  proto: ${PROTO_TAG}
  dashboard: ${DASHBOARD_TAG}
  website: ${WEBSITE_TAG}
  helm-charts: ${HELM_CHARTS_TAG}
artifacts:
  helmChartVersion: ${HELM_CHART_VERSION}
EOF

cat > "${results_dir}/summary.yaml" <<EOF
platformVersion: ${platform_version}
status: pending
checks:
  gateway-build:
    status: pending
  gateway-test:
    status: pending
  dataplane-build:
    status: pending
  dataplane-test:
    status: pending
  dataplane-clippy:
    status: pending
  dataplane-fmt:
    status: pending
  proto-generate:
    status: pending
  dashboard-check:
    status: pending
  website-check:
    status: pending
  helm-lint:
    status: pending
  install-validation:
    status: pending
  gateway-api-conformance:
    status: pending
artifacts: {}
EOF

cat > "${results_dir}/conformance.md" <<EOF
# ${platform_version} Conformance

Pending validation. Run \`scripts/run-validation.sh\` and \`scripts/collect-results.sh\` to populate conformance evidence.
EOF

cat > "${results_dir}/test-matrix.md" <<EOF
# ${platform_version} Test Matrix

Pending validation. See \`summary.yaml\` for machine-readable status updates.
EOF

cat > "${results_dir}/artifacts.yaml" <<EOF
githubRun: ""
failure: ""
EOF
