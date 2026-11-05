#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
runs_dir="$repo_dir/.stocktake_runs"
mkdir -p "$runs_dir"

# A scheduled check and a manual run can arrive close together.
exec 9>"$runs_dir/publish.lock"
flock -x 9

publish_run() (
    local run_id=$1
    local run_dir=$2
    local work_dir origin_url attempt

    test -s "$run_dir/gadi_gdata_stocktake.html"
    test -s "$run_dir/gadi_scratch_stocktake.html"

    # The daily dashboard job also uses the main checkout, so publish separately.
    work_dir=$(mktemp -d "$runs_dir/publish.XXXXXX")
    trap 'rm -rf "$work_dir"' EXIT
    origin_url=$(git -C "$repo_dir" remote get-url origin)
    git clone --shared --no-checkout "$repo_dir" "$work_dir/checkout"
    git -C "$work_dir/checkout" remote set-url origin "$origin_url"
    git -C "$work_dir/checkout" fetch origin main
    git -C "$work_dir/checkout" checkout -B main origin/main

    cp "$run_dir/gadi_gdata_stocktake.html" "$work_dir/checkout/docs/gadi_gdata_stocktake.html"
    cp "$run_dir/gadi_scratch_stocktake.html" "$work_dir/checkout/docs/gadi_scratch_stocktake.html"
    git -C "$work_dir/checkout" add docs/gadi_gdata_stocktake.html docs/gadi_scratch_stocktake.html

    if ! git -C "$work_dir/checkout" diff --cached --quiet; then
        git -C "$work_dir/checkout" commit -m "UPDATE: Gadi stocktakes $run_id"
        for attempt in 1 2 3; do
            if git -C "$work_dir/checkout" push origin HEAD:main; then
                break
            fi
            if (( attempt == 3 )); then
                echo 'Could not push the stocktake commit after three attempts.' >&2
                return 1
            fi
            git -C "$work_dir/checkout" fetch origin main
            git -C "$work_dir/checkout" rebase origin/main
        done
    else
        echo "Stocktake pages from $run_id have not changed."
    fi

    printf '%s\n' "$run_id" > "$runs_dir/last_published"
    touch "$run_dir/published"
    echo "Published both stocktake pages from $run_dir"
)

had_failure=0
for job_file in "$runs_dir"/*/job_id; do
    [[ -e "$job_file" ]] || continue
    run_dir=${job_file%/job_id}
    run_id=${run_dir##*/}

    if [[ -e "$run_dir/published" || -e "$run_dir/failed" || -e "$run_dir/superseded" ]]; then
        continue
    fi

    if [[ -e "$runs_dir/last_published" ]] && [[ "$run_id" < "$(<"$runs_dir/last_published")" ]]; then
        touch "$run_dir/superseded"
        echo "Skipping older stocktake $run_id."
        continue
    fi

    if [[ -e "$run_dir/complete" ]]; then
        publish_run "$run_id" "$run_dir"
    elif [[ -e "$run_dir/exit_status" ]]; then
        echo "PBS scan $(<"$job_file") failed with status $(<"$run_dir/exit_status")." >&2
        touch "$run_dir/failed"
        had_failure=1
    elif qstat "$(<"$job_file")" >/dev/null 2>&1; then
        echo "PBS scan $(<"$job_file") is still queued or running."
    else
        echo "PBS scan $(<"$job_file") disappeared without producing both reports." >&2
        touch "$run_dir/failed"
        had_failure=1
    fi
done

exit "$had_failure"
