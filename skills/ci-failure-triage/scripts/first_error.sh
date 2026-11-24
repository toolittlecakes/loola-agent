#!/usr/bin/env bash
# Print the first error-looking line of a CI log with 5 lines of context before and 20 after.
set -euo pipefail
line=$(grep -n -m1 -i -E '\b(err!|(error|fail(ed|ure)?|traceback|panic)\b)' "$1" | cut -d: -f1) || {
  echo "No error-looking lines in $1"; exit 1; }
sed -n "$((line > 5 ? line - 5 : 1)),$((line + 20))p" "$1"
