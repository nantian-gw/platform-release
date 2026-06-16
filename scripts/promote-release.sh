#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <candidate-version> <final-version>" >&2
  exit 1
fi

python_bin="${PYTHON_BIN:-.venv/bin/python3}"

"${python_bin}" tools/releasectl.py promote-release \
  --repo-root . \
  --candidate "$1" \
  --final "$2"
