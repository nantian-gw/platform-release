#!/usr/bin/env bash
# Cleanup old nightly run.log files older than RETENTION_DAYS (default 30).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DRY_RUN="${DRY_RUN:-false}"

results_dir="$REPO_ROOT/results"

if [[ ! -d "$results_dir" ]]; then
  echo "results directory not found: $results_dir" >&2
  exit 0
fi

cutoff_date="$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d 2>/dev/null || date -v-"${RETENTION_DAYS}"d +%Y-%m-%d)"
echo "Cleaning run.log files older than $cutoff_date ($RETENTION_DAYS days)"
echo "Mode: ${DRY_RUN:+dry-run}${DRY_RUN:-live}"

count=0
total_size=0

while IFS= read -r -d '' logfile; do
  dir_date="$(basename "$(dirname "$logfile")")"

  if [[ "$dir_date" < "$cutoff_date" ]]; then
    size="$(stat -c%s "$logfile" 2>/dev/null || stat -f%z "$logfile" 2>/dev/null || echo 0)"
    echo "  would remove: $logfile ($(numfmt --to=iec "$size" 2>/dev/null || echo "${size}B"))"

    if [[ "$DRY_RUN" != "true" ]]; then
      rm -f "$logfile"
      # Remove empty parent directory
      parent="$(dirname "$logfile")"
      rmdir "$parent" 2>/dev/null || true
    fi

    count=$((count + 1))
    total_size=$((total_size + size))
  fi
done < <(find "$results_dir" -name "run.log" -type f -print0 2>/dev/null || true)

if [[ $count -eq 0 ]]; then
  echo "No files to clean"
else
  echo "Cleaned $count files ($(numfmt --to=iec "$total_size" 2>/dev/null || echo "${total_size}B"))"
fi
