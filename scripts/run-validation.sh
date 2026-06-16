#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <manifest> <summary> <workspace>" >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON_BIN:-${repo_root}/.venv/bin/python3}"

"${python_bin}" "${repo_root}/tools/releasectl.py" run-validation \
  --registry "${repo_root}/components/components.yaml" \
  --manifest "$1" \
  --manifest-schema "${repo_root}/schemas/manifest.schema.json" \
  --summary "$2" \
  --summary-schema "${repo_root}/schemas/summary.schema.json" \
  --workspace "$3"
