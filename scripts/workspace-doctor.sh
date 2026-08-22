#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON_BIN:-${repo_root}/.venv/bin/python3}"

if [[ -n "${WORKSPACE_ROOT:-}" ]]; then
  workspace_root="${WORKSPACE_ROOT}"
else
  workspace_root="$(cd -- "${repo_root}/.." && pwd)"
  if [[ ! -d "${workspace_root}/gateway/.git" ]]; then
    main_worktree="$(git -C "${repo_root}" worktree list --porcelain | awk '$1 == "worktree" { print $2; exit }')"
    if [[ -n "${main_worktree}" ]]; then
      workspace_root="$(cd -- "${main_worktree}/.." && pwd)"
    fi
  fi
fi

exec "${python_bin}" "${repo_root}/tools/workspace_doctor.py" \
  --registry "${repo_root}/components/components.yaml" \
  --workspace-root "${workspace_root}" \
  "$@"
