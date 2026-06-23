#!/usr/bin/env bash
set -euo pipefail

dry_run=false
candidate=""
final=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      dry_run=true
      shift
      ;;
    *)
      if [[ -z "${candidate}" ]]; then
        candidate="$1"
      elif [[ -z "${final}" ]]; then
        final="$1"
      else
        echo "unexpected argument: $1" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "${candidate}" || -z "${final}" ]]; then
  echo "usage: $0 [--dry-run] <candidate-version> <final-version>" >&2
  exit 1
fi

candidate_version="${candidate#v}"
final_version="${final#v}"

echo "Promoting release: v${candidate_version} → v${final_version}"
if [[ "${dry_run}" == "true" ]]; then
  echo "[DRY RUN] No changes will be made."
  exit 0
fi

echo -n "Proceed? [y/N] "
read -r confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
  echo "Aborted."
  exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
python_bin="${PYTHON_BIN:-${repo_root}/.venv/bin/python3}"

"${python_bin}" "${repo_root}/tools/releasectl.py" promote-release \
  --repo-root "${repo_root}" \
  --candidate "${candidate}" \
  --final "${final}"
