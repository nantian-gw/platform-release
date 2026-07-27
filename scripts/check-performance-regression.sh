#!/usr/bin/env bash
# Performance regression gating for nightly benchmarks.
# Compares today's results against a rolling baseline (median of last 7 days).
# Exits non-zero if P99 latency increases >20%, CPU usage increases >30%,
# memory usage increases >25%, max throughput drops >15%, or success rate
# drops below 99.9%.
#
# Multi-scenario fixed-rate tests measure compliance (can the gateway handle
# the declared rate?). The saturation scenario (saturation_throughput_rps in
# performance.json) measures max throughput with unbounded concurrency — this
# is the primary throughput regression signal.
set -euo pipefail

RESULTS_DIR="${RESULTS_DIR:-results/nightly}"
P99_THRESHOLD="${P99_THRESHOLD:-20}"                  # percent
CPU_THRESHOLD="${CPU_THRESHOLD:-30}"                  # percent
MEMORY_THRESHOLD="${MEMORY_THRESHOLD:-25}"            # percent
THROUGHPUT_THRESHOLD="${THROUGHPUT_THRESHOLD:-15}"    # percent
BASELINE_DAYS="${BASELINE_DAYS:-7}"

today=$(date -u +%Y-%m-%d)
today_file="${RESULTS_DIR}/${today}/performance.json"

if [[ ! -f "$today_file" ]]; then
  echo "No performance data for today ($today), skipping regression check."
  exit 0
fi

# Extract metrics from today's performance.json.
# Supports both legacy format (throughput_rps, latency.p99_ms, success_rate)
# and multi-scenario format (total_requests, scenarios[], success_rate).
get_p99() {
  local file="$1"
  # Try multi-scenario format first: max P99 across all scenarios
  local p99
  p99=$(jq -r '[.scenarios[]?.p99 // empty] | if length > 0 then max else empty end' "$file" 2>/dev/null)
  if [[ -n "$p99" && "$p99" != "null" && "$p99" != "" ]]; then
    echo "$p99"
    return
  fi
  # Fall back to legacy format
  jq -r '.latency.p99_ms // empty' "$file" 2>/dev/null
}

get_success_rate() {
  jq -r '.success_rate // empty' "$1" 2>/dev/null
}

get_cpu_avg() {
  jq -r '.cpu.avg_m // empty' "$1" 2>/dev/null
}

get_mem_avg() {
  jq -r '.memory.avg_mi // empty' "$1" 2>/dev/null
}

get_saturation_rps() {
  jq -r '.saturation_throughput_rps // empty' "$1" 2>/dev/null
}

today_p99=$(get_p99 "$today_file")
today_success=$(get_success_rate "$today_file")
today_cpu=$(get_cpu_avg "$today_file")
today_mem=$(get_mem_avg "$today_file")
today_tput=$(get_saturation_rps "$today_file")

echo "Today ($today): P99=${today_p99}ms, success_rate=${today_success}, CPU=${today_cpu}m, Mem=${today_mem}Mi, SaturationRPS=${today_tput:-N/A}"

# Collect baseline data from last N days
baseline_p99=()
baseline_cpu=()
baseline_mem=()
baseline_tput=()

for days_ago in $(seq 1 "$BASELINE_DAYS"); do
  date_str=$(date -u -d "$days_ago days ago" +%Y-%m-%d 2>/dev/null || date -u -v-"${days_ago}"d +%Y-%m-%d)
  file="${RESULTS_DIR}/${date_str}/performance.json"
  if [[ -f "$file" ]]; then
    p99=$(get_p99 "$file")
    cpu=$(get_cpu_avg "$file")
    mem=$(get_mem_avg "$file")
    tput=$(get_saturation_rps "$file")
    if [[ -n "$p99" && "$p99" != "null" && "$p99" != "" ]]; then
      baseline_p99+=("$p99")
    fi
    if [[ -n "$cpu" && "$cpu" != "null" && "$cpu" != "" ]]; then
      baseline_cpu+=("$cpu")
    fi
    if [[ -n "$mem" && "$mem" != "null" && "$mem" != "" ]]; then
      baseline_mem+=("$mem")
    fi
    if [[ -n "$tput" && "$tput" != "null" && "$tput" != "" ]]; then
      baseline_tput+=("$tput")
    fi
  fi
done

if [[ ${#baseline_p99[@]} -eq 0 ]]; then
  echo "No baseline data available (need at least 1 prior day). Skipping regression check."
  exit 0
fi

# Calculate median of baseline
median_p99=$(printf '%s\n' "${baseline_p99[@]}" | sort -n | awk '{a[NR]=$1} END{if (NR%2==1) print a[(NR+1)/2]; else print (a[NR/2]+a[NR/2+1])/2}')
median_cpu=$(printf '%s\n' "${baseline_cpu[@]}" | sort -n | awk '{a[NR]=$1} END{if (NR%2==1) print a[(NR+1)/2]; else print (a[NR/2]+a[NR/2+1])/2}')
median_mem=$(printf '%s\n' "${baseline_mem[@]}" | sort -n | awk '{a[NR]=$1} END{if (NR%2==1) print a[(NR+1)/2]; else print (a[NR/2]+a[NR/2+1])/2}')
median_tput=$(printf '%s\n' "${baseline_tput[@]}" | sort -n | awk '{a[NR]=$1} END{if (NR%2==1) print a[(NR+1)/2]; else print (a[NR/2]+a[NR/2+1])/2}')

echo "Baseline (median of ${#baseline_p99[@]} days): P99=${median_p99}ms, CPU=${median_cpu}m, Mem=${median_mem}Mi, SaturationRPS=${median_tput:-N/A}"

REGRESSION=false

# Check P99 regression
if [[ -n "$today_p99" && "$today_p99" != "null" && -n "$median_p99" ]]; then
  p99_change=$(awk "BEGIN {printf \"%.1f\", (($today_p99 - $median_p99) / $median_p99) * 100}")
  if (( $(awk "BEGIN {print ($p99_change > $P99_THRESHOLD)}") )); then
    echo "::error::P99 latency regression: +${p99_change}% (threshold: +${P99_THRESHOLD}%)"
    echo "regression=true" >> "$GITHUB_OUTPUT"
    REGRESSION=true
  else
    echo "P99 latency change: ${p99_change}% (within threshold)"
  fi
else
  echo "P99: insufficient data for comparison (today=${today_p99}, baseline_median=${median_p99:-N/A})"
fi

# Check success rate
if [[ -n "$today_success" && "$today_success" != "null" ]]; then
  if (( $(awk "BEGIN {print ($today_success < 0.999)}") )); then
    echo "::error::Success rate dropped below 99.9%: ${today_success}"
    echo "regression=true" >> "$GITHUB_OUTPUT"
    REGRESSION=true
  else
    echo "Success rate: ${today_success} (>= 99.9%)"
  fi
fi

# Check CPU regression (increase > threshold = regression)
if [[ -n "$today_cpu" && "$today_cpu" != "null" && -n "$median_cpu" && "$median_cpu" != "0" ]]; then
  cpu_change=$(awk "BEGIN {printf \"%.1f\", (($today_cpu - $median_cpu) / $median_cpu) * 100}")
  if (( $(awk "BEGIN {print ($cpu_change > $CPU_THRESHOLD)}") )); then
    echo "::error::CPU regression: +${cpu_change}% (threshold: +${CPU_THRESHOLD}%)"
    echo "regression=true" >> "$GITHUB_OUTPUT"
    REGRESSION=true
  else
    echo "CPU change: ${cpu_change}% (within threshold)"
  fi
else
  echo "CPU: insufficient data for comparison"
fi

# Check memory regression (increase > threshold = regression)
if [[ -n "$today_mem" && "$today_mem" != "null" && -n "$median_mem" && "$median_mem" != "0" ]]; then
  mem_change=$(awk "BEGIN {printf \"%.1f\", (($today_mem - $median_mem) / $median_mem) * 100}")
  if (( $(awk "BEGIN {print ($mem_change > $MEMORY_THRESHOLD)}") )); then
    echo "::error::Memory regression: +${mem_change}% (threshold: +${MEMORY_THRESHOLD}%)"
    echo "regression=true" >> "$GITHUB_OUTPUT"
    REGRESSION=true
  else
    echo "Memory change: ${mem_change}% (within threshold)"
  fi
else
  echo "Memory: insufficient data for comparison"
fi

# Check throughput regression (decrease > threshold = regression)
if [[ -n "$today_tput" && "$today_tput" != "null" && -n "$median_tput" && "$median_tput" != "0" ]]; then
  if (( $(awk "BEGIN {print ($today_tput < $median_tput)}") )); then
    tput_change=$(awk "BEGIN {printf \"%.1f\", (($median_tput - $today_tput) / $median_tput) * 100}")
    if (( $(awk "BEGIN {print ($tput_change > $THROUGHPUT_THRESHOLD)}") )); then
      echo "::error::Throughput regression: -${tput_change}% (threshold: -${THROUGHPUT_THRESHOLD}%)"
      echo "regression=true" >> "$GITHUB_OUTPUT"
      REGRESSION=true
    else
      echo "Throughput change: -${tput_change}% (within threshold)"
    fi
  else
    echo "Throughput: ${today_tput} RPS (>= baseline ${median_tput})"
  fi
else
  echo "Throughput: insufficient data for comparison (today=${today_tput:-N/A}, baseline_median=${median_tput:-N/A})"
fi

if [[ "${REGRESSION}" == "true" ]]; then
  echo ""
  echo "=== PERFORMANCE REGRESSION DETECTED ==="
  echo "  P99:     ${today_p99}ms (baseline median: ${median_p99}ms, change: ${p99_change:-N/A}%)"
  echo "  CPU:     ${today_cpu}m (baseline median: ${median_cpu}m, change: ${cpu_change:-N/A}%)"
  echo "  Memory:  ${today_mem}Mi (baseline median: ${median_mem}Mi, change: ${mem_change:-N/A}%)"
  echo "  Throughput: ${today_tput:-N/A} RPS (baseline median: ${median_tput:-N/A}, change: ${tput_change:-N/A}%)"
  exit 1
fi

echo ""
echo "=== Performance within baseline ==="
exit 0
