#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <candidate-version> <final-version>" >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON_BIN:-${repo_root}/.venv/bin/python3}"

"${python_bin}" "${repo_root}/tools/releasectl.py" promote-release \
  --repo-root "${repo_root}" \
  --candidate "$1" \
  --final "$2"
