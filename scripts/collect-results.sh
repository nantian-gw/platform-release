#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "usage: $0 <summary> <matrix> <conformance> <artifacts>" >&2
  exit 1
fi

python_bin="${PYTHON_BIN:-.venv/bin/python3}"

"${python_bin}" tools/releasectl.py collect-results \
  --summary "$1" \
  --matrix "$2" \
  --conformance "$3" \
  --artifacts "$4"
