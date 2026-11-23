#!/usr/bin/env bash
# Idempotent content-agent setup. Quiet. Never runs npm install at the repo root.
set -euo pipefail

root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"

if ! python3 -c 'import sympy, numpy' >/dev/null 2>&1; then
  PIP_DISABLE_PIP_VERSION_CHECK=1 python3 -m pip install --user -q --no-warn-script-location sympy numpy
  python3 -c 'import sympy, numpy' >/dev/null 2>&1
fi

if ! python3 -c 'import scipy' >/dev/null 2>&1; then
  # Keep an already importable numpy. A bare `pip install scipy` currently
  # upgrades numpy to 2.5, which removes np.trapz and fails the numeric gate.
  numpy_pin=$(python3 - <<'PY'
try:
    import numpy
except Exception:
    raise SystemExit(0)
print(numpy.__version__)
PY
)
  if [[ -n ${numpy_pin:-} ]]; then
    PIP_DISABLE_PIP_VERSION_CHECK=1 python3 -m pip install --user -q --no-warn-script-location "numpy==${numpy_pin}" scipy
  else
    PIP_DISABLE_PIP_VERSION_CHECK=1 python3 -m pip install --user -q --no-warn-script-location scipy
  fi
  python3 -c 'import scipy' >/dev/null 2>&1
fi

if [[ ! -d /tmp/katex-home/node_modules/katex ]]; then
  # Run outside the repo so npm cannot write a root node_modules or package.json.
  (cd /tmp && npm install --prefix /tmp/katex-home katex@0.16.47 --no-audit --no-fund --silent)
fi
[[ -d /tmp/katex-home/node_modules/katex ]]

if [[ ! -d public/skilltree/tests/node_modules/puppeteer-core ]]; then
  npm install --prefix public/skilltree/tests --no-audit --no-fund
fi
[[ -d public/skilltree/tests/node_modules/puppeteer-core ]]

if [[ $# -eq 0 ]]; then
  exit 0
fi
if [[ $# -ne 2 || $1 != "--box" || -z $2 ]]; then
  echo "usage: agent_bootstrap.sh [--box <box-id>]" >&2
  exit 2
fi

python3 - "$2" <<'PY'
import json
import sys

box_id = sys.argv[1]
with open("skilltree/collections.json", encoding="utf-8") as handle:
    collections = json.load(handle)
match = next((box for box in collections.get("boxes", []) if box.get("id") == box_id), None)
if match is None:
    sys.exit(f"unknown box: {box_id}")
skills = list(match.get("skills") or [])
with open("skilltree/deep_quota_grandfather.json", encoding="utf-8") as handle:
    grandfather = json.load(handle)
listed = set(grandfather.get("skills") or [])
print("skills: " + (", ".join(skills) if skills else "none"))
hit = [skill for skill in skills if skill in listed]
print("grandfather: " + (", ".join(hit) if hit else "none"))
PY
