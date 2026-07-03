#!/usr/bin/env bash
# Performance regression gating for nightly benchmarks.
# Compares today's results against a rolling baseline (median of last 7 days).
# Exits non-zero if throughput drops >15% or P99 latency increases >20%.
set -euo pipefail

RESULTS_DIR="${RESULTS_DIR:-results/nightly}"
THROUGHPUT_THRESHOLD="${THROUGHPUT_THRESHOLD:-15}"  # percent
P99_THRESHOLD="${P99_THRESHOLD:-20}"                  # percent
BASELINE_DAYS="${BASELINE_DAYS:-7}"

today=$(date -u +%Y-%m-%d)
today_file="${RESULTS_DIR}/${today}/performance.json"

if [[ ! -f "$today_file" ]]; then
  echo "No performance data for today ($today), skipping regression check."
  exit 0
fi

today_rps=$(jq -r '.throughput_rps' "$today_file")
today_p99=$(jq -r '.latency.p99_ms' "$today_file")
today_success=$(jq -r '.success_rate' "$today_file")

echo "Today ($today): throughput=${today_rps} RPS, P99=${today_p99}ms, success_rate=${today_success}"

# Collect baseline data from last N days
baseline_rps=()
baseline_p99=()

for days_ago in $(seq 1 "$BASELINE_DAYS"); do
  date_str=$(date -u -d "$days_ago days ago" +%Y-%m-%d 2>/dev/null || date -u -v-"${days_ago}"d +%Y-%m-%d)
  file="${RESULTS_DIR}/${date_str}/performance.json"
  if [[ -f "$file" ]]; then
    rps=$(jq -r '.throughput_rps' "$file" 2>/dev/null || echo "")
    p99=$(jq -r '.latency.p99_ms' "$file" 2>/dev/null || echo "")
    if [[ -n "$rps" && "$rps" != "null" ]]; then
      baseline_rps+=("$rps")
    fi
    if [[ -n "$p99" && "$p99" != "null" ]]; then
      baseline_p99+=("$p99")
    fi
  fi
done

if [[ ${#baseline_rps[@]} -eq 0 ]]; then
  echo "No baseline data available (need at least 1 prior day). Skipping regression check."
  exit 0
fi

# Calculate median of baseline
median_rps=$(printf '%s\n' "${baseline_rps[@]}" | sort -n | awk '{a[NR]=$1} END{if (NR%2==1) print a[(NR+1)/2]; else print (a[NR/2]+a[NR/2+1])/2}')
median_p99=$(printf '%s\n' "${baseline_p99[@]}" | sort -n | awk '{a[NR]=$1} END{if (NR%2==1) print a[(NR+1)/2]; else print (a[NR/2]+a[NR/2+1])/2}')

echo "Baseline (median of ${#baseline_rps[@]} days): throughput=${median_rps} RPS, P99=${median_p99}ms"

# Check throughput regression
rps_change=$(awk "BEGIN {printf \"%.1f\", (($today_rps - $median_rps) / $median_rps) * 100}")
if (( $(awk "BEGIN {print ($rps_change < -$THROUGHPUT_THRESHOLD)}") )); then
  echo "::error::Throughput regression: ${rps_change}% (threshold: -${THROUGHPUT_THRESHOLD}%)"
  echo "regression=true" >> "$GITHUB_OUTPUT"
  REGRESSION=true
else
  echo "Throughput change: ${rps_change}% (within threshold)"
fi

# Check P99 regression
p99_change=$(awk "BEGIN {printf \"%.1f\", (($today_p99 - $median_p99) / $median_p99) * 100}")
if (( $(awk "BEGIN {print ($p99_change > $P99_THRESHOLD)}") )); then
  echo "::error::P99 latency regression: +${p99_change}% (threshold: +${P99_THRESHOLD}%)"
  echo "regression=true" >> "$GITHUB_OUTPUT"
  REGRESSION=true
else
  echo "P99 latency change: ${p99_change}% (within threshold)"
fi

# Check success rate
if (( $(awk "BEGIN {print ($today_success < 0.999)}") )); then
  echo "::error::Success rate dropped below 99.9%: ${today_success}"
  REGRESSION=true
fi

if [[ "${REGRESSION:-false}" == "true" ]]; then
  echo ""
  echo "=== PERFORMANCE REGRESSION DETECTED ==="
  echo "  Throughput: ${today_rps} RPS (baseline: ${median_rps}, change: ${rps_change}%)"
  echo "  P99:        ${today_p99}ms (baseline: ${median_p99}ms, change: +${p99_change}%)"
  exit 1
fi

echo ""
echo "=== Performance within baseline ==="
exit 0
