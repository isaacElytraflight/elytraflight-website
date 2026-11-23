#!/usr/bin/env bash
# Capped search. Defaults: skilltree/, tools/skilltree-content/, docs/, public/skilltree/.
# At most 40 lines, and rg truncates each line at 200 columns.
set -eu

root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"

if [[ $# -lt 1 || -z ${1:-} ]]; then
  echo "usage: find.sh <pattern> [path...]" >&2
  exit 2
fi
if ! command -v rg >/dev/null 2>&1; then
  echo "find.sh: rg is not installed" >&2
  exit 2
fi

pattern=$1
shift
if [[ $# -eq 0 ]]; then
  set -- skilltree tools/skilltree-content docs public/skilltree
fi

# head closes the pipe early. A full page makes rg exit with SIGPIPE (141);
# that is a successful cap, not a search error. Exit 2 only when rg itself errors.
set +e
rg --max-columns 200 --max-columns-preview --no-heading -n -- "$pattern" "$@" | head -n 40
status=${PIPESTATUS[0]}
set -e
if [[ $status -eq 2 ]]; then
  exit 2
fi
