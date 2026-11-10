#!/usr/bin/env python3
"""Focused checks for the new question types.

Covers the safe expression parser, SymPy key checks, schema acceptance and
rejection, and the deep-type quota with grandfathering.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "skilltree-content"))

from banklib import DEEP_TYPES, deep_quota  # noqa: E402
from expr import ExprError, Parser, evaluate, grade, parse, tokenize  # noqa: E402
from validator_domain import deep_quota_warnings  # noqa: E402
from verify_harness import check_symbolic  # noqa: E402

VARS = [
    {"name": "l", "min": -4, "max": 4},
    {"name": "t", "min": -5, "max": 5},
    {"name": "d", "min": -4, "max": 4},
]
KEY = "l^2 - t*l + d"


def check(name, cond):
    if not cond:
        raise SystemExit("FAIL " + name)
    print("ok", name)


def test_parser():
    cases = {
        "2+3*4": 14,
        "(2+3)*4": 20,
        "2^3^2": 512,
        "-2^2": -4,
        "2x": None,
        "2x^2": None,
        "sin(pi/2)": 1,
        "ln(e)": 1,
        "2(3+1)": 8,
        "(1+2)(3+4)": 21,
        "sqrt(4)": 2,
        "abs(-3)": 3,
        "1e-3": 0.001,
        "2e+1": 20,
    }
    env = {"x": 3}
    check("2x", evaluate(parse("2x", ["x"]), env) == 6)
    check("2x^2", evaluate(parse("2x^2", ["x"]), env) == 18)
    for src, expect in cases.items():
        if expect is None:
            continue
        names = ["x"] if "x" in src else []
        got = evaluate(parse(src, names), env)
        check(src, got is not None and abs(got - expect) < 1e-9)
    for bad in ["", "2+", "sin(", "foo(1)", "1$", "\\frac{1}{2}"]:
        try:
            parse(bad, ["x"])
        except ExprError:
            check("reject " + bad, True)
        else:
            check("reject " + bad, False)
    check("grade equivalent", grade(KEY, "(l - t)*l + d", VARS, 1e-3) is True)
    check("grade wrong", grade(KEY, "l^2 + t*l + d", VARS, 1e-3) is False)
    check("grade invalid", grade(KEY, "sin(", VARS, 1e-3) is None)
    check("2*e+1 is the constant", abs(evaluate(parse("2*e+1", ["x"]), env) - (2 * math.e + 1)) < 1e-9)
    for bad_name in (["e"], ["E"]):
        try:
            parse("2*e+1", bad_name)
        except ExprError:
            check("reject variable " + bad_name[0], True)
        else:
            check("reject variable " + bad_name[0], False)
    bound = evaluate(Parser(tokenize("2e+1", {"e"})).parse(), {"e": 2})
    check("bound e is not scientific notation", bound == 5)


def test_node_parity():
    script = r"""
const e = require('./public/skilltree/expr.js');
const cases = ['2+3*4','(2+3)*4','2^3^2','-2^2','2x','2x^2','sin(pi/2)','ln(e)','2(3+1)','(1+2)(3+4)','sqrt(4)','abs(-3)','1e-3','2e+1','2*e+1'];
const out = {};
for (const src of cases) {
  const names = src.includes('x') ? ['x'] : [];
  out[src] = e.evaluate(e.parse(src, names), {x: 3});
}
let rejected = false;
try { e.parse('2*e+1', ['e']); } catch (err) { rejected = /reserved/.test(err.message); }
const toks = e.tokenize('2e+1', new Set(['e']));
out.__rejected = rejected;
out.__bound = toks.map(t => (t[0] === 'num' || t[0] === 'name') ? t[1] : t[0]);
process.stdout.write(JSON.stringify(out));
"""
    proc = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr)
    got = json.loads(proc.stdout)
    check("js rejects variable e", got.pop("__rejected") is True)
    check("js bound e is not scientific notation", got.pop("__bound") == [2, "e", "+", 1])
    for src, js in got.items():
        names = ["x"] if "x" in src else []
        py = evaluate(parse(src, names), {"x": 3})
        check("js " + src, py is not None and abs(py - js) < 1e-9)


def test_cas():
    good = {
        "skill_id": "fixture",
        "questions": [{
            "id": "fixture-r1-q1",
            "type": "symbolic",
            "answer": KEY,
            "alternates": ["l**2 - t*l + d", "(l - t)*l + d"],
            "variables": VARS,
            "tolerance": 0.001,
        }],
    }
    bad_alt = json.loads(json.dumps(good))
    bad_alt["questions"][0]["alternates"] = ["l^2 + t*l + d"]
    bad_form = json.loads(json.dumps(good))
    bad_form["questions"][0]["answer"] = "l^"
    mismatches = []
    n = check_symbolic({"fixture": good}, mismatches)
    check("cas count", n == 1 and not mismatches)
    mismatches = []
    check_symbolic({"fixture": bad_alt}, mismatches)
    check("cas alternate", any("not equivalent" in m for m in mismatches))
    mismatches = []
    check_symbolic({"fixture": bad_form}, mismatches)
    check("cas malformed", any("not a valid expression" in m or "SymPy rejected" in m for m in mismatches))
    mismatches = []
    check("cas skip", check_symbolic({"fixture": {"questions": [{"type": "numeric"}]}}, mismatches) == 0)


def numeric_q(sid, rnd, k):
    return {
        "id": f"{sid}-r{rnd}-q{k}",
        "round": rnd,
        "type": "numeric",
        "prompt": "How many?",
        "explanation": "The count is 4 because the two pairs each contribute 2, and adding the pairs is the whole.",
        "answer": 4,
        "unit": "1",
        "tolerance": 0.02,
        "version": 1,
    }


def bank_with(sid, replacement, slot=(1, 1)):
    questions = []
    for rnd in (1, 2, 3, 4):
        for k in (1, 2, 3):
            q = numeric_q(sid, rnd, k)
            if (rnd, k) == slot:
                q = replacement
                q["id"] = f"{sid}-r{rnd}-q{k}"
                q["round"] = rnd
            if rnd == 4:
                q["preview"] = ["later"]
            questions.append(q)
    return {"skill_id": sid, "version": 1, "questions": questions}


def skills_doc(sid):
    return {"skills": [
        {"id": "core", "name": "Core", "chapter": 1, "prereqs": []},
        {"id": sid, "name": "Fixture", "chapter": 1, "prereqs": ["core"]},
        {"id": "later", "name": "Later", "chapter": 1, "prereqs": [sid]},
    ]}


def run_schema(bank):
    tmp = tempfile.mkdtemp(prefix="sg-deep-")
    try:
        sid = bank["skill_id"]
        with open(os.path.join(tmp, sid + ".json"), "w", encoding="utf-8") as f:
            json.dump(bank, f)
        skills = os.path.join(tmp, "skills.json")
        with open(skills, "w", encoding="utf-8") as f:
            json.dump(skills_doc(sid), f)
        env = os.environ.copy()
        env["VALIDATE_SKILLS"] = sid
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "validate_bank.py"), tmp, skills],
            cwd=ROOT, text=True, capture_output=True, env=env,
        )
        return proc.returncode, proc.stdout + proc.stderr
    finally:
        shutil.rmtree(tmp)


def test_schema():
    order = {
        "type": "order",
        "prompt": "Order the steps.",
        "explanation": "First write the matrix, then reduce, then count nonzero rows. Skipping the reduction counts a copied row as new.",
        "steps": ["Write it down.", "Row-reduce.", "Count the nonzero rows."],
    }
    code, text = run_schema(bank_with("fixture", order))
    check("schema order", code == 0)
    error = {
        "type": "error",
        "prompt": "Which step is wrong?",
        "explanation": "The sign on the free variable is the flaw. The rows really are dependent, and the null space really is one-dimensional.",
        "steps": ["The rows are dependent.", "The free variable is the second component.", "The first component equals twice the second.", "A basis vector is (2, -1)."],
        "flaw_index": 2,
        "reasons": ["The pivot relation has the wrong sign.", "The rows are independent."],
        "correct_reason": 0,
    }
    code, text = run_schema(bank_with("fixture", error))
    check("schema error", code == 0)
    multi = {
        "type": "multi",
        "prompt": "Select every property similar matrices share.",
        "explanation": "Eigenvalues, the trace, and the determinant are similarity invariants. Entries and coordinate-wise eigenvectors are not.",
        "options": ["the eigenvalues", "the trace", "the determinant", "every entry"],
        "correct_indices": [0, 1, 2],
    }
    code, text = run_schema(bank_with("fixture", multi))
    check("schema multi", code == 0)
    symbolic = {
        "type": "symbolic",
        "prompt": "Write the polynomial.",
        "explanation": "The characteristic polynomial subtracts the trace times the variable and adds the determinant. The other sign is the common slip.",
        "answer": KEY,
        "variables": VARS,
        "tolerance": 0.001,
        "alternates": ["(l - t)*l + d"],
    }
    code, text = run_schema(bank_with("fixture", symbolic, (3, 2)))
    check("schema symbolic", code == 0)
    broken = dict(symbolic)
    broken["answer"] = "l^2 + t*l + z"
    code, text = run_schema(bank_with("fixture", broken, (3, 2)))
    check("schema bad symbol", code != 0 and "unknown name" in text)
    reserved = dict(symbolic)
    reserved["answer"] = "2*e+1"
    reserved["variables"] = [{"name": "e", "min": 1, "max": 3}]
    code, text = run_schema(bank_with("fixture", reserved, (3, 2)))
    check("schema rejects variable e", code != 0 and "reserved" in text)
    code, text = run_schema(bank_with("fixture", {"type": "mc", "prompt": "x", "explanation": "y" * 70, "options": ["a"], "correct_index": 0}))
    check("schema still rejects short mc", code != 0)


def test_quota():
    check("quota 12", deep_quota(12) == 3)
    check("quota 8", deep_quota(8) == 2)
    check("quota 1", deep_quota(1) == 1)
    check("quota 0", deep_quota(0) == 0)
    check("deep types", set(DEEP_TYPES) == {"symbolic", "order", "error", "multi"})
    tmp = tempfile.mkdtemp(prefix="sg-quota-")
    try:
        old = {"skill_id": "old-skill", "questions": [numeric_q("old-skill", 1, 1)] * 12}
        new = {"skill_id": "new-skill", "questions": [numeric_q("new-skill", 1, 1)] * 12}
        new["questions"][0] = {"type": "order", "steps": ["a", "b", "c"]}
        for bank in (old, new):
            with open(os.path.join(tmp, bank["skill_id"] + ".json"), "w", encoding="utf-8") as f:
                json.dump(bank, f)
        warns = deep_quota_warnings(tmp, {"old-skill"})
        check("grandfather skips", not any("old-skill" in w for w in warns))
        check("new bank flagged", any(w.startswith("new-skill deep-type quota") for w in warns))
        rich = json.loads(json.dumps(new))
        for i, kind in enumerate(("symbolic", "order", "error")):
            rich["questions"][i] = {"type": kind}
        with open(os.path.join(tmp, "new-skill.json"), "w", encoding="utf-8") as f:
            json.dump(rich, f)
        warns = deep_quota_warnings(tmp, {"old-skill"})
        check("three deep passes", not any(w.startswith("new-skill") for w in warns))
        warns = deep_quota_warnings(tmp, {"old-skill", "ghost"})
        check("stale grandfather", any("ghost" in w and "no bank" in w for w in warns))
    finally:
        shutil.rmtree(tmp)


def main():
    test_parser()
    test_node_parity()
    test_cas()
    test_schema()
    test_quota()
    print("deep-type checks passed")


if __name__ == "__main__":
    main()
