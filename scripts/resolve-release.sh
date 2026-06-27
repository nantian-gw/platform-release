#!/usr/bin/env bash
set -euo pipefail

tmp="$(mktemp -d)"
trap 'rm -rf "${tmp}"' EXIT

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <platform-version>" >&2
  exit 1
fi

platform_version="$1"
version_pattern='^v[0-9]{4}\.[0-9]{2}\.[0-9]+(-rc[0-9]+)?$'
python_bin="${PYTHON_BIN:-.venv/bin/python3}"

if [[ ! "${platform_version}" =~ ${version_pattern} ]]; then
  echo "platform version must match ${version_pattern}" >&2
  exit 1
fi

release_dir="releases/${platform_version}"
results_dir="results/${platform_version}"

if [[ -e "${release_dir}" || -e "${results_dir}" ]]; then
  echo "release evidence already exists for ${platform_version}; refusing to overwrite ${release_dir} or ${results_dir}" >&2
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

gateway_commit=""
dataplane_commit=""
proto_commit=""
dashboard_commit=""
website_commit=""
helm_charts_commit=""

resolve_commit "${gateway_repo}" "${GATEWAY_TAG}" >"${tmp}/gateway_commit" &
pid_gateway=$!
resolve_commit "${dataplane_repo}" "${DATAPLANE_TAG}" >"${tmp}/dataplane_commit" &
pid_dataplane=$!
resolve_commit "${proto_repo}" "${PROTO_TAG}" >"${tmp}/proto_commit" &
pid_proto=$!
resolve_commit "${dashboard_repo}" "${DASHBOARD_TAG}" >"${tmp}/dashboard_commit" &
pid_dashboard=$!
resolve_commit "${website_repo}" "${WEBSITE_TAG}" >"${tmp}/website_commit" &
pid_website=$!
resolve_commit "${helm_charts_repo}" "${HELM_CHARTS_TAG}" >"${tmp}/helm_charts_commit" &
pid_helm=$!

failed=false
for pid in ${pid_gateway} ${pid_dataplane} ${pid_proto} ${pid_dashboard} ${pid_website} ${pid_helm}; do
  if ! wait "${pid}"; then
    failed=true
  fi
done
if [[ "${failed}" == "true" ]]; then
  echo "one or more tag resolutions failed" >&2
  exit 1
fi

gateway_commit="$(cat "${tmp}/gateway_commit")"
dataplane_commit="$(cat "${tmp}/dataplane_commit")"
proto_commit="$(cat "${tmp}/proto_commit")"
dashboard_commit="$(cat "${tmp}/dashboard_commit")"
website_commit="$(cat "${tmp}/website_commit")"
helm_charts_commit="$(cat "${tmp}/helm_charts_commit")"

release_date="$(date -u +%F)"

mkdir -p "${release_dir}" "${results_dir}"

cat > "${release_dir}/manifest.yaml" <<EOF
platformVersion: ${platform_version}
baseRelease: null
status: candidate
releaseDate: "${release_date}"
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
    gateway: ghcr.io/nantian-gw/nantian-controlplane@${GATEWAY_IMAGE_DIGEST}
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
compatibility:
  gateway:
    dataplane: ${DATAPLANE_TAG}
    proto: ${PROTO_TAG}
  helmChart:
    chartVersion: ${HELM_CHART_VERSION}
EOF

"${python_bin}" - <<PY
from pathlib import Path
from tools import releasectl

registry = releasectl.load_yaml(Path("components/components.yaml"))
summary = releasectl.build_initial_summary("${platform_version}", registry)
releasectl.dump_yaml(Path("${results_dir}/summary.yaml"), summary)
PY

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
