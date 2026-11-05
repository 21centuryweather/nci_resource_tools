#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_dir"

run_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
log_dir="$repo_dir/.stocktake_logs"
mkdir -p "$log_dir" "$repo_dir/.stocktake_runs"
run_dir="$repo_dir/.stocktake_runs/$run_id"
mkdir "$run_dir"

if ! scan_job=$(qsub \
    -v "STOCKTAKE_RUN_ID=$run_id" \
    -o "$log_dir" -e "$log_dir" \
    scripts/stocktake_scan.pbs); then
    rmdir "$run_dir"
    exit 1
fi

printf '%s\n' "$scan_job" > "$run_dir/job_id"
echo "Submitted rudu scan: $scan_job"
echo "PBS logs: $log_dir"
