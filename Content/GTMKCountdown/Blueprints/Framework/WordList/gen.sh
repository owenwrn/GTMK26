#!/usr/bin/env bash
set -euo pipefail

base_dir="$(dirname "$(realpath "$0")")"
out_file="$base_dir/../WordList.csv"

{
    echo "---,Word,Mature"
    cat "$base_dir/atebits.txt" "$base_dir/enable1.txt" | \
        sort -u | \
        awk '{print NR","$0",0"}'
} > "$out_file"
