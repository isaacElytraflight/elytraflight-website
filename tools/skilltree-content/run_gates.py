#!/usr/bin/env python3
"""One gate run for a content batch.

  python3 tools/skilltree-content/run_gates.py --batch me132-b1
  python3 tools/skilltree-content/run_gates.py --batch me132-b1 --docs

Writes docs/gates/<batch>.json. With --docs, regenerates the changelog, brief,
report, and content-versions file from that summary. The shingle gate is not
part of this pipeline.
"""
import json
import os
import socket
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


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


def main():
    args = sys.argv[1:]
    if "--batch" not in args:
        raise SystemExit("usage: run_gates.py --batch me132-b1 [--docs]")
    name = args[args.index("--batch") + 1]
    write_docs = "--docs" in args
    spec = load_batch(name)
    skills = spec["skills"]
    katex_files = []
    for sid in skills:
        katex_files.append(os.path.join("skilltree", "bank", sid + ".json"))
        katex_files.append(os.path.join("skilltree", "explainers", sid + ".json"))
    steps = [
        ("build", [sys.executable, "tools/skilltree-content/build.py"], 120),
        ("schema", [sys.executable, "skilltree/validate_bank.py", "skilltree/bank", "skilltree/ee105_skills_draft.json"], 120),
        ("reference", [sys.executable, "tools/skilltree-content/reference_gate.py"], 120),
        ("graph", [sys.executable, "skilltree/validate_graph.py"], 60),
        ("domain", [sys.executable, "skilltree/validator_domain.py"], 60),
        ("numeric", [sys.executable, spec["verifier"]], 180),
        ("figure-bounds", [sys.executable, "skilltree/figure_bounds.py", "--fail-skills", ",".join(skills)], 120),
        ("katex", ["node", "tools/skilltree-content/katex_check.cjs", *katex_files], 180),
        ("test-content", ["node", "public/skilltree/tests/test-content.js"], 60),
        ("test-merge", ["node", "public/skilltree/tests/test-merge.js"], 60),
        ("test-migrate", ["node", "public/skilltree/tests/test-migrate.js"], 60),
    ]
    ensure_server()
    steps.append(("puppeteer", ["node", "public/skilltree/tests/test.js"], 300))

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
