#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "usage: $0 <summary> <matrix> <conformance> <artifacts>" >&2
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON_BIN:-${repo_root}/.venv/bin/python3}"

"${python_bin}" "${repo_root}/tools/releasectl.py" collect-results \
  --summary "$1" \
  --matrix "$2" \
  --conformance "$3" \
  --artifacts "$4"
