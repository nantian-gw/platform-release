#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON_BIN:-${repo_root}/.venv/bin/python3}"

REPO_ROOT="${repo_root}" "${python_bin}" <<'PY'
import json
import os
from pathlib import Path

import yaml
from jsonschema.validators import Draft202012Validator

repo_root = Path(os.environ["REPO_ROOT"])

for path in sorted(repo_root.rglob("*.yaml")) + sorted(repo_root.rglob("*.yml")):
    if any(part in {".git", ".venv", ".pytest_cache"} for part in path.parts):
        continue
    with path.open(encoding="utf-8") as handle:
        yaml.safe_load(handle)

for path in sorted((repo_root / "schemas").glob("*.schema.json")):
    with path.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)

print("YAML and JSON schema lint passed")
PY

find "${repo_root}/scripts" -name "*.sh" -type f -print0 | xargs -0 -n1 bash -n
