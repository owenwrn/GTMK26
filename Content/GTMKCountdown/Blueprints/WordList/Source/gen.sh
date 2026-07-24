#!/usr/bin/env bash
set -euo pipefail

base_dir="$(dirname "$(realpath "$0")")"
out_file="$base_dir/../WordList.csv"

{
    echo "---,Word,Mature"
    "$base_dir/.venv/bin/python" "$base_dir/filter_words.py" \
        "$base_dir/atebits.txt" "$base_dir/enable1.txt" | \
        awk -F, '{print NR","$1","$2}'
} > "$out_file"
