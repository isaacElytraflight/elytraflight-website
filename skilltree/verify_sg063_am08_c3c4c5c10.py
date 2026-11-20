#!/usr/bin/env python3
"""Independent check for the SG-063 Feedback Systems retrofit, slice of four banks.

Recomputes symbolic keys, corner signs, and the deep-question decisions.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import itertools
import json
import os
import re

import sympy as sp

from verify_harness import finish, load_banks

SKILLS = [
    "app-examples",
    "limit-cycles",
    "discrete-time",
    "pid-impl",
]

SYMBOLIC = {
    "app-examples-r3-q4": "a/b",
    "discrete-time-r2-q4": "exp(-a*b)",
    "pid-impl-r3-q4": "1/(1+a*b)",
}

ERRORS = {
    "app-examples-r2-q4": (3, 0),
    "limit-cycles-r2-q4": (3, 0),
    "discrete-time-r2-q5": (3, 0),
}

ORDERS = {
    "app-examples-r1-q4": 4,
    "limit-cycles-r1-q4": 4,
    "discrete-time-r1-q4": 4,
    "pid-impl-r1-q4": 4,
}

MULTIS = {
    "limit-cycles-r1-q5": [0, 1, 2],
    "pid-impl-r2-q4": [0, 1, 2],
}

RETIRED = {
    "app-examples": [
        "app-examples-r1-q1",
        "app-examples-r2-q1",
        "app-examples-r3-q1",
    ],
    "limit-cycles": [
        "limit-cycles-r1-q1",
        "limit-cycles-r1-q2",
        "limit-cycles-r2-q2",
    ],
    "discrete-time": [
        "discrete-time-r1-q1",
        "discrete-time-r2-q1",
        "discrete-time-r2-q3",
    ],
    "pid-impl": [
        "pid-impl-r1-q1",
        "pid-impl-r2-q2",
        "pid-impl-r3-q1",
    ],
}

VERSIONS = {
    "app-examples": 2,
    "limit-cycles": 2,
    "discrete-time": 2,
    "pid-impl": 2,
}

HELD = {
    "app-examples-r1-q2": {"type": "numeric", "version": 1},
    "app-examples-r1-q3": {"type": "numeric", "version": 1},
    "app-examples-r2-q2": {"type": "numeric", "version": 1},
    "app-examples-r2-q3": {"type": "numeric", "version": 1},
    "app-examples-r3-q2": {"type": "numeric", "version": 1},
    "app-examples-r3-q3": {"type": "numeric", "version": 1},
    "app-examples-r4-q1": {"type": "numeric", "version": 1},
    "app-examples-r4-q2": {"type": "numeric", "version": 1},
    "app-examples-r4-q3": {"type": "mc", "version": 1},
    "limit-cycles-r1-q3": {"type": "mc", "version": 1},
    "limit-cycles-r2-q1": {"type": "mc", "version": 1},
    "limit-cycles-r2-q3": {"type": "mc", "version": 1},
    "limit-cycles-r3-q1": {"type": "mc", "version": 1},
    "limit-cycles-r3-q2": {"type": "mc", "version": 1},
    "limit-cycles-r3-q3": {"type": "numeric", "version": 1},
    "limit-cycles-r4-q1": {"type": "mc", "version": 1},
    "limit-cycles-r4-q2": {"type": "mc", "version": 1},
    "limit-cycles-r4-q3": {"type": "mc", "version": 2},
    "discrete-time-r1-q2": {"type": "numeric", "version": 1},
    "discrete-time-r1-q3": {"type": "numeric", "version": 1},
    "discrete-time-r2-q2": {"type": "numeric", "version": 1},
    "discrete-time-r3-q1": {"type": "numeric", "version": 1},
    "discrete-time-r3-q2": {"type": "numeric", "version": 1},
    "discrete-time-r3-q3": {"type": "mc", "version": 1},
    "discrete-time-r4-q1": {"type": "numeric", "version": 1},
    "discrete-time-r4-q2": {"type": "mc", "version": 1},
    "discrete-time-r4-q3": {"type": "numeric", "version": 1},
    "pid-impl-r1-q2": {"type": "numeric", "version": 1},
    "pid-impl-r1-q3": {"type": "numeric", "version": 1},
    "pid-impl-r2-q1": {"type": "numeric", "version": 1},
    "pid-impl-r2-q3": {"type": "numeric", "version": 1},
    "pid-impl-r3-q2": {"type": "numeric", "version": 1},
    "pid-impl-r3-q3": {"type": "numeric", "version": 1},
    "pid-impl-r4-q1": {"type": "numeric", "version": 1},
    "pid-impl-r4-q2": {"type": "mc", "version": 1},
    "pid-impl-r4-q3": {"type": "numeric", "version": 1},
}

REMAINING = [
    "feedforward",
    "gen-gain-phase",
    "min-phase",
    "perf-specs-freq",
]

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def question(banks, qid):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            return q
    return None


def corner_signs(q, mismatches):
    """Every corner of the sample box keeps the key finite and positive."""
    specs = q.get("variables") or []
    names = []
    bounds = []
    for spec in specs:
        name = spec.get("name")
        lo, hi = float(spec["min"]), float(spec["max"])
        if lo <= 0 or hi <= lo:
            mismatches.append(f"{q['id']}: range for {name} is not a positive interval")
            return
        names.append(name)
        bounds.append((lo, hi))
    local = {name: sp.Symbol(name) for name in names}
    local["exp"] = sp.exp
    expr = sp.parse_expr(q["answer"], local_dict=local)
    for corner in itertools.product(*bounds):
        value = complex(expr.subs(dict(zip(names, corner))))
        if abs(value.imag) > 1e-9 or not (value.real > 0) or value.real != value.real:
            mismatches.append(f"{q['id']}: corner {corner} gives {value}")
            return


def main():
    banks = load_banks(SKILLS)
    mismatches = []
    for qid, expr in SYMBOLIC.items():
        q = question(banks, qid)
        if q is None:
            mismatches.append(qid + ": missing symbolic question")
            continue
        if q.get("type") != "symbolic":
            mismatches.append(qid + ": not symbolic")
        if q.get("answer") != expr:
            mismatches.append(f"{qid}: key {q.get('answer')!r} != {expr!r}")
        else:
            corner_signs(q, mismatches)
        prompt = q.get("prompt") or ""
        for spec in q.get("variables") or []:
            name = spec.get("name")
            if name and re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", prompt) is None:
                mismatches.append(f"{qid}: prompt does not contain graded name {name}")
    for qid, (flaw, reason) in ERRORS.items():
        q = question(banks, qid)
        if q is None or q.get("type") != "error":
            mismatches.append(qid + ": missing find-the-error question")
            continue
        if q.get("flaw_index") != flaw:
            mismatches.append(f"{qid}: flaw {q.get('flaw_index')} != {flaw}")
        if q.get("correct_reason") != reason:
            mismatches.append(f"{qid}: reason {q.get('correct_reason')} != {reason}")
        if len(q.get("steps") or []) != 4:
            mismatches.append(f"{qid}: expected 4 steps")
    for qid, nsteps in ORDERS.items():
        q = question(banks, qid)
        if q is None or q.get("type") != "order":
            mismatches.append(qid + ": missing ordering question")
            continue
        if len(q.get("steps") or []) != nsteps:
            mismatches.append(f"{qid}: {len(q.get('steps') or [])} steps != {nsteps}")
        blob = " ".join(q.get("steps") or [])
        if blob.count("previous step") < nsteps - 1:
            mismatches.append(f"{qid}: ordering chain does not cite the previous step")
    for qid, idxs in MULTIS.items():
        q = question(banks, qid)
        if q is None or q.get("type") != "multi":
            mismatches.append(qid + ": missing multi-select question")
            continue
        if q.get("correct_indices") != idxs:
            mismatches.append(f"{qid}: indices {q.get('correct_indices')} != {idxs}")
    for qid, spec in HELD.items():
        q = question(banks, qid)
        if q is None:
            mismatches.append(qid + ": held question is no longer live")
            continue
        if q.get("type") != spec["type"] or q.get("version") != spec["version"]:
            mismatches.append(f"{qid}: held type/version changed")
    for sid, old_ids in RETIRED.items():
        live_ids = [q["id"] for q in banks[sid]["questions"]]
        live = set(live_ids)
        retired = [q["id"] for q in banks[sid].get("retired_questions") or []]
        if len(live_ids) != len(live):
            mismatches.append(f"{sid}: duplicate live ids")
        if len(retired) != len(set(retired)):
            mismatches.append(f"{sid}: duplicate retired ids")
        if sorted(retired) != sorted(old_ids):
            mismatches.append(f"{sid}: retired {retired} != {old_ids}")
        overlap = sorted(set(retired) & live)
        if overlap:
            mismatches.append(f"{sid}: reused {overlap}")
        deep = sum(1 for q in banks[sid]["questions"] if q.get("type") in ("symbolic", "order", "error", "multi"))
        if deep < 3:
            mismatches.append(f"{sid}: only {deep} deep questions")
        if banks[sid].get("version") != VERSIONS[sid]:
            mismatches.append(f"{sid}: bank version {banks[sid].get('version')} != {VERSIONS[sid]}")
        rounds = {}
        for q in banks[sid]["questions"]:
            rounds[q.get("round")] = rounds.get(q.get("round"), 0) + 1
            if q.get("round") == 4 and not q.get("preview"):
                mismatches.append(q["id"] + ": round 4 lost its preview")
        if rounds != {1: 3, 2: 3, 3: 3, 4: 3}:
            mismatches.append(f"{sid}: round counts {rounds}")
    grand_path = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
    with open(grand_path, encoding="utf-8") as f:
        grandfather = json.load(f)["skills"]
    if grandfather != REMAINING:
        mismatches.append("grandfather list changed beyond this slice: " + ", ".join(grandfather))
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 4:
        mismatches.append(f"grandfather count {len(grandfather)} != 4")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    owners = {}
    batch_dir = os.path.join(ROOT, "docs", "batches")
    for name in sorted(os.listdir(batch_dir)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(batch_dir, name), encoding="utf-8") as f:
            spec = json.load(f)
        for sid in spec.get("skills") or []:
            owners.setdefault(sid, []).append(name)
    for sid in SKILLS:
        got = owners.get(sid) or []
        if got != ["sg063-am08-c3c4c5c10.json"]:
            mismatches.append(f"{sid}: batch files {got}")
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
