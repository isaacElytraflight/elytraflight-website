#!/usr/bin/env bash
# Block until the Cursor Bugbot check on <sha> completes.
# Prints one line: CLEAN, FINDINGS ..., SKIPPED, or TIMEOUT.
# Exit 0 clean or skipped, 1 findings, 2 timeout or bad usage.
set -eu

if [[ $# -lt 1 || $# -gt 2 || -z ${1:-} ]]; then
  echo "usage: wait_bugbot.sh <sha> [pr-number]" >&2
  exit 2
fi
sha=$1
pr=${2:-}
if [[ -n $pr && ! $pr =~ ^[0-9]+$ ]]; then
  echo "usage: wait_bugbot.sh <sha> [pr-number]" >&2
  exit 2
fi

repo=isaacElytraflight/elytraflight-website
deadline=$(( $(date +%s) + 1800 ))

# stdin is the script. The check-run JSON is argv[2], because a heredoc
# would otherwise consume the pipe this function is fed.
classify() {
  python3 - "$sha" "$1" <<'PY'
import json
import sys

sha = sys.argv[1].lower()
raw = sys.argv[2].strip()
if not raw:
    print("WAIT")
    raise SystemExit
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print("WAIT")
    raise SystemExit
if not isinstance(data, dict) or "check_runs" not in data:
    print("WAIT")
    raise SystemExit
runs = [run for run in data.get("check_runs") or [] if run.get("name") == "Cursor Bugbot"]
if not runs:
    print("WAIT")
    raise SystemExit
runs.sort(key=lambda run: run.get("started_at") or "", reverse=True)
run = runs[0]
if (run.get("status") or "").lower() != "completed":
    print("WAIT")
    raise SystemExit
conclusion = (run.get("conclusion") or "").lower()
if conclusion in {"cancelled", "timed_out", "stale"}:
    print("WAIT")
    raise SystemExit
output = run.get("output") or {}
title = output.get("title") or ""
summary = output.get("summary") or ""
blob = (title + "\n" + summary).lower()

def flat(text, limit=None):
    text = text or ""
    if limit is not None:
        text = text[:limit]
    return " ".join(text.split())

def findings_line():
    print("FINDINGS\t" + flat(title) + "\t" + flat(summary, 500))

# GitHub's conclusion decides. A success run is CLEAN unless its own
# summary states a finding the repo refuses to merge: too large to review,
# or "potential issue". Loose words such as "found" and "issue" do not.
# A non-success conclusion is never CLEAN, even if the text says
# "no issues found".
explicit_finding = (
    "too large to review" in blob
    or "too big to review" in blob
    or "potential issue" in blob
)
if conclusion == "skipped":
    print("SKIPPED")
elif conclusion == "success" and not explicit_finding:
    print("CLEAN")
else:
    findings_line()
PY
}

comments_for_sha() {
  local tmp
  tmp=$(mktemp)
  if ! gh api --paginate "repos/${repo}/pulls/${pr}/comments?per_page=100" >"$tmp" 2>/dev/null; then
    rm -f "$tmp"
    printf '%s' "unavailable"
    return
  fi
  python3 - "$sha" "$tmp" <<'PY' || { rm -f "$tmp"; printf '%s' "unavailable"; return; }
import json
import sys

sha = sys.argv[1].lower()
raw = open(sys.argv[2], encoding="utf-8").read().strip()
if not raw:
    print("none")
    raise SystemExit
decoder = json.JSONDecoder()
items = []
blob = raw.lstrip()
parsed = False
while blob:
    blob = blob.lstrip()
    if not blob:
        break
    try:
        value, end = decoder.raw_decode(blob)
    except json.JSONDecodeError:
        parsed = False
        break
    parsed = True
    if isinstance(value, list):
        items.extend(value)
    elif isinstance(value, dict) and "message" in value and "commit_id" not in value:
        print("unavailable")
        raise SystemExit
    else:
        items.append(value)
    blob = blob[end:]
if not parsed:
    print("unavailable")
    raise SystemExit
parts = []
for comment in items:
    if not isinstance(comment, dict):
        continue
    commit = (comment.get("commit_id") or "").lower()
    if not commit:
        continue
    same = commit == sha or (
        len(sha) >= 7 and (commit.startswith(sha) or sha.startswith(commit))
    )
    if not same:
        continue
    path = comment.get("path") or ""
    line = comment.get("line")
    if line is None:
        line = comment.get("original_line")
    loc = path if line is None else f"{path}:{line}"
    body = " ".join((comment.get("body") or "").split())
    if len(body) > 500:
        body = body[:500]
    login = ((comment.get("user") or {}).get("login") or "")
    parts.append(" ".join(bit for bit in (login, loc, body) if bit))
print(" || ".join(parts) if parts else "none")
PY
  rm -f "$tmp"
}

while true; do
  now=$(date +%s)
  if (( now >= deadline )); then
    echo TIMEOUT
    exit 2
  fi
  payload=$(gh api "repos/${repo}/commits/${sha}/check-runs?check_name=Cursor%20Bugbot&per_page=100" 2>/dev/null || true)
  line=$(classify "$payload" || true)
  kind=${line%%$'\t'*}
  case $kind in
    CLEAN|SKIPPED)
      echo "$kind"
      exit 0
      ;;
    FINDINGS)
      title=${line#*$'\t'}
      summary=${title#*$'\t'}
      title=${title%%$'\t'*}
      if [[ -n $pr ]]; then
        echo "FINDINGS title=${title} summary=${summary} comments=$(comments_for_sha)"
      else
        echo "FINDINGS title=${title} summary=${summary}"
      fi
      exit 1
      ;;
  esac
  remain=$(( deadline - $(date +%s) ))
  if (( remain <= 0 )); then
    echo TIMEOUT
    exit 2
  fi
  if (( remain > 30 )); then
    remain=30
  fi
  sleep "$remain"
done
