#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <manifest> <summary> <workspace>" >&2
  exit 1
fi

python_bin="${PYTHON_BIN:-.venv/bin/python3}"

"${python_bin}" tools/releasectl.py run-validation \
  --registry components/components.yaml \
  --manifest "$1" \
  --manifest-schema schemas/manifest.schema.json \
  --summary "$2" \
  --summary-schema schemas/summary.schema.json \
  --workspace "$3"
