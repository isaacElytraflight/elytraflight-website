#!/usr/bin/env python3
"""One gate run for a content batch.

  python3 tools/skilltree-content/run_gates.py --batch me132-b1
  python3 tools/skilltree-content/run_gates.py --batch me132-b1 --docs
  python3 tools/skilltree-content/run_gates.py --batch me132-b1 --dry-run
  python3 tools/skilltree-content/run_gates.py --batch me132-b1 --browser
  python3 tools/skilltree-content/run_gates.py --batch me132-b1 --no-browser

Writes docs/gates/<batch>.json. With --docs, regenerates the changelog, brief,
report, and content-versions file from that summary. The shingle gate is not
part of this pipeline.

The browser suite is decided from `git diff` against origin/main. It is
skipped when every changed path is content, and run otherwise. --browser
and --no-browser override that. Content gates always run.
"""
import json
import os
import re
import socket
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
USAGE = (
    "usage: run_gates.py --batch <id> [--docs] [--browser | --no-browser] [--dry-run]"
)

# Banks, explainers, the skill graph, and the files a content batch commits
# with them. The runner's --docs output is included so a normal content PR
# still counts as content-only. App, UI, and build code are not in this set.
CONTENT_PREFIXES = (
    "skilltree/bank/",
    "skilltree/explainers/",
    "skilltree/bank_retired/",
    "skilltree/gen/",
    "public/skilltree/banks/",
    "public/skilltree/explainers/",
    "docs/briefs/",
    "docs/reports/",
    "docs/gates/",
    "docs/batches/",
)
CONTENT_FILES = {
    "skilltree/ee105_skills_draft.json",
    "skilltree/collections.json",
    "skilltree/deep_quota_grandfather.json",
    "public/skilltree/manifest.json",
    "public/skilltree/tests/test-content.js",
    "docs/CHANGELOG.md",
    "docs/content-versions.json",
    "docs/dedupe-decisions.json",
    "docs/notation.md",
    "docs/sources.md",
}
AUTHORING_FILES = {
    "banklib.py",
    "templates.py",
    "figlib.py",
    "qlib.py",
    "o_figs.py",
    "o_latex.py",
}
SHARED_VERIFIERS = {
    "skilltree/verify_harness.py",
    "skilltree/verify_mc.py",
    "skilltree/verify_numeric.py",
}
PUBLISHED_GRAPH = re.compile(
    r"^public/skilltree/(?:skills|collections)\.[0-9a-fA-F]+\.json$"
)


def load_batch(name):
    path = os.path.join(ROOT, "docs", "batches", name + ".json")
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    spec["_path"] = path
    return spec


def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), 1):
            return True
    except OSError:
        return False


def ensure_server():
    if port_open(5000):
        return
    subprocess.run(
        ["tmux", "-f", "/exec-daemon/tmux.portal.conf", "new-session", "-d", "-s", "skilltree-serve",
         "npx", "--yes", "serve", "public", "-l", "5000"],
        cwd=ROOT, check=False,
    )
    for _ in range(40):
        if port_open(5000):
            return
        subprocess.run(["sleep", "0.25"], check=False)
    raise SystemExit("skilltree server did not start on port 5000")


def one_line(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("Built to "):
            return "content files written"
    for ln in reversed(lines):
        if ln.startswith(("OK:", "FAILED", "graph", "figure-bounds", "KaTeX", "numeric", "0 mismatches")):
            return ln
    if any("passed" in ln and "failed" in ln for ln in lines):
        for ln in reversed(lines):
            if "passed" in ln and "failed" in ln:
                return ln
    return lines[-1] if lines else "(no output)"


def run(cmd, timeout):
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    text = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, text


def norm_path(path):
    path = (path or "").replace("\\", "/").strip()
    if path.startswith("./"):
        path = path[2:]
    return path


def is_authoring_source(path):
    prefix = "tools/skilltree-content/"
    if not path.startswith(prefix):
        return False
    name = path[len(prefix):]
    if "/" in name:
        return False
    if name in AUTHORING_FILES or name.endswith("_gen.py"):
        return True
    return name.endswith(".py") and name.startswith(("s_", "batch2", "nlo_", "me132_", "ee105_"))


def is_content_path(path):
    """True for banks, explainers, the skill graph, and their sources."""
    path = norm_path(path)
    if not path or path.startswith("../") or "/../" in path:
        return False
    if path in CONTENT_FILES or any(path.startswith(prefix) for prefix in CONTENT_PREFIXES):
        return True
    if PUBLISHED_GRAPH.match(path):
        return True
    if path.startswith("skilltree/verify_") and path.endswith(".py") and path not in SHARED_VERIFIERS:
        return True
    return is_authoring_source(path)


def _git_lines(args):
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        return None
    return [norm_path(ln) for ln in proc.stdout.splitlines() if ln.strip()]


def changed_paths():
    """Tracked changes against origin/main, plus uncommitted and untracked files."""
    parts = [
        _git_lines(["git", "diff", "--name-only", "origin/main...HEAD"]),
        _git_lines(["git", "diff", "--name-only", "HEAD"]),
        _git_lines(["git", "ls-files", "--others", "--exclude-standard"]),
    ]
    if any(part is None for part in parts):
        return None
    found = []
    seen = set()
    for part in parts:
        for path in part:
            if path and path not in seen:
                seen.add(path)
                found.append(path)
    return found


def is_bytecode(path):
    path = norm_path(path)
    return path.endswith(".pyc") or "/__pycache__/" in path or path.endswith("__pycache__")


def decide_browser(paths, override):
    """Return (run_suite, why).

    override is None, "browser", or "no-browser". paths is a list, or None
    when the diff against origin/main could not be read. Bytecode is ignored.
    """
    if override == "browser":
        return True, "--browser override; running the browser suite"
    if override == "no-browser":
        return False, "--no-browser override; skipping the browser suite"
    if paths is None:
        return True, "could not read git diff against origin/main; running the browser suite"
    paths = [path for path in paths if not is_bytecode(path)]
    if not paths:
        return False, "no changed paths against origin/main; skipping the browser suite"
    other = [path for path in paths if not is_content_path(path)]
    if not other:
        return False, f"every changed path is content-only ({len(paths)} files)"
    shown = ", ".join(other[:12])
    if len(other) > 12:
        shown += f" (+{len(other) - 12} more)"
    return True, "non-content paths: " + shown


def parse_args(argv):
    if "--batch" not in argv:
        raise SystemExit(USAGE)
    batch_at = argv.index("--batch")
    if batch_at + 1 >= len(argv):
        raise SystemExit(USAGE)
    if "--browser" in argv and "--no-browser" in argv:
        raise SystemExit("pass only one of --browser or --no-browser")
    if "--browser" in argv:
        override = "browser"
    elif "--no-browser" in argv:
        override = "no-browser"
    else:
        override = None
    return argv[batch_at + 1], "--docs" in argv, "--dry-run" in argv, override


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    name, write_docs, dry_run, override = parse_args(argv)
    run_browser, why = decide_browser(changed_paths(), override)
    print(f"browser suite: {'run' if run_browser else 'skip'} - {why}")
    if dry_run:
        print("dry run: not executing gates")
        return 0
    spec = load_batch(name)
    skills = spec["skills"]
    katex_files = []
    for sid in skills:
        katex_files.append(os.path.join("skilltree", "bank", sid + ".json"))
        katex_files.append(os.path.join("skilltree", "explainers", sid + ".json"))
    steps = [
        ("build", [sys.executable, "tools/skilltree-content/build.py"], 120),
        ("schema", [sys.executable, "skilltree/validate_bank.py", "skilltree/bank", "skilltree/ee105_skills_draft.json"], 120),
        ("video", [sys.executable, "tools/skilltree-content/video_gate.py"], 60),
        ("reference", [sys.executable, "tools/skilltree-content/reference_gate.py"], 120),
        ("graph", [sys.executable, "skilltree/validate_graph.py"], 60),
        ("domain", [sys.executable, "skilltree/validator_domain.py"], 60),
        ("deep-quota", [sys.executable, "tools/skilltree-content/deep_quota_gate.py"], 60),
        ("dedupe", [sys.executable, "tools/skilltree-content/dedupe_gate.py", "--batch", name], 60),
        ("numeric", [sys.executable, spec["verifier"]], 180),
        ("figure-bounds", [sys.executable, "skilltree/figure_bounds.py", "--fail-skills", ",".join(skills)], 120),
        ("katex", ["node", "tools/skilltree-content/katex_check.cjs", *katex_files], 180),
        ("test-content", ["node", "public/skilltree/tests/test-content.js"], 60),
        ("test-merge", ["node", "public/skilltree/tests/test-merge.js"], 60),
        ("test-migrate", ["node", "public/skilltree/tests/test-migrate.js"], 60),
    ]
    # The browser suite is about 70 cases and has finished in just over 5 minutes
    # on a cold headless Chrome. 300s was killing a run that then passed on its own.
    if run_browser:
        ensure_server()
        steps.append(("puppeteer", ["node", "public/skilltree/tests/test.js"], 480))

    results = []
    failed = 0
    for step, cmd, timeout in steps:
        code, text = run(cmd, timeout)
        ok = code == 0
        failed += 0 if ok else 1
        summary = one_line(text)
        results.append({"name": step, "ok": ok, "summary": summary})
        print(f"{'PASS' if ok else 'FAIL'} {step:<16} {summary}")
        if not ok and step == "build":
            break
    print(f"{len(results) - failed} passed, {failed} failed")
    if not run_browser:
        results.append({"name": "puppeteer", "ok": True, "skipped": True, "summary": why})
        print(f"SKIP {'puppeteer':<16} {why}")
    out = {"batch": name, "ok": failed == 0, "steps": results}
    gate_path = os.path.join(ROOT, "docs", "gates", name + ".json")
    os.makedirs(os.path.dirname(gate_path), exist_ok=True)
    with open(gate_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    if write_docs:
        subprocess.run([sys.executable, "tools/skilltree-content/write_batch_docs.py", "--batch", name], cwd=ROOT, check=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
