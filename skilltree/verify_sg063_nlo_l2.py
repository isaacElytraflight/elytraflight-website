#!/usr/bin/env python3
"""Independent check for the SG-063 mathematical-preliminaries retrofit.

Recomputes symbolic keys, corner signs, and the deep-question decisions.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import itertools
import os

import sympy as sp

from verify_harness import finish, load_banks

SKILLS = [
    "rn-important-subsets",
    "singular-value-decomposition",
    "rayleigh-quotient",
    "inner-products",
    "vector-norms-lp",
    "cauchy-schwarz-inequality",
]

SYMBOLIC = {
    "rn-important-subsets-r2-q4": "(a+b+c+d)/2",
    "singular-value-decomposition-r1-q5": "a**2 + b**2",
    "rayleigh-quotient-r1-q5": "(a+2*c+b)/2",
    "inner-products-r2-q4": "a*c + b*d",
    "vector-norms-lp-r2-q4": "a+b",
    "cauchy-schwarz-inequality-r1-q4": "a**2 + b**2",
}

ERRORS = {
    "rn-important-subsets-r3-q4": (3, 0),
    "singular-value-decomposition-r3-q4": (3, 0),
    "rayleigh-quotient-r2-q4": (3, 0),
    "vector-norms-lp-r1-q5": (3, 0),
    "cauchy-schwarz-inequality-r1-q5": (3, 0),
}

ORDERS = {
    "rn-important-subsets-r1-q4": 4,
    "singular-value-decomposition-r1-q4": 4,
    "rayleigh-quotient-r1-q4": 4,
    "inner-products-r1-q4": 4,
    "vector-norms-lp-r1-q4": 4,
    "cauchy-schwarz-inequality-r2-q4": 4,
}

MULTIS = {
    "inner-products-r1-q5": [0, 1, 2],
}

RETIRED = {
    "rn-important-subsets": [
        "rn-important-subsets-r1-q1",
        "rn-important-subsets-r2-q1",
        "rn-important-subsets-r3-q2",
    ],
    "singular-value-decomposition": [
        "singular-value-decomposition-r1-q1",
        "singular-value-decomposition-r1-q3",
        "singular-value-decomposition-r3-q1",
    ],
    "rayleigh-quotient": [
        "rayleigh-quotient-r1-q1",
        "rayleigh-quotient-r1-q3",
        "rayleigh-quotient-r2-q2",
    ],
    "inner-products": [
        "inner-products-r1-q1",
        "inner-products-r1-q3",
        "inner-products-r2-q2",
    ],
    "vector-norms-lp": [
        "vector-norms-lp-r1-q1",
        "vector-norms-lp-r1-q3",
        "vector-norms-lp-r2-q2",
    ],
    "cauchy-schwarz-inequality": [
        "cauchy-schwarz-inequality-r1-q1",
        "cauchy-schwarz-inequality-r1-q3",
        "cauchy-schwarz-inequality-r2-q2",
    ],
}

VERSIONS = {
    "rn-important-subsets": 4,
    "singular-value-decomposition": 4,
    "rayleigh-quotient": 3,
    "inner-products": 3,
    "vector-norms-lp": 4,
    "cauchy-schwarz-inequality": 3,
}

HELD = {
    "rn-important-subsets-r1-q3": {"type": "mc", "version": 2},
    "rn-important-subsets-r4-q1": {"type": "mc", "version": 2},
    "rn-important-subsets-r4-q2": {"type": "numeric", "version": 2},
    "rn-important-subsets-r4-q3": {"type": "mc", "version": 3},
    "singular-value-decomposition-r2-q2": {"type": "mc", "version": 2},
    "singular-value-decomposition-r4-q1": {"type": "numeric", "version": 1},
    "singular-value-decomposition-r4-q2": {"type": "mc", "version": 1},
    "singular-value-decomposition-r4-q3": {"type": "mc", "version": 3},
    "rayleigh-quotient-r3-q1": {"type": "mc", "version": 2},
    "rayleigh-quotient-r4-q1": {"type": "numeric", "version": 2},
    "rayleigh-quotient-r4-q2": {"type": "mc", "version": 1},
    "rayleigh-quotient-r4-q3": {"type": "mc", "version": 2},
    "inner-products-r3-q1": {"type": "mc", "version": 1},
    "inner-products-r4-q1": {"type": "numeric", "version": 2},
    "inner-products-r4-q2": {"type": "mc", "version": 2},
    "inner-products-r4-q3": {"type": "mc", "version": 1},
    "vector-norms-lp-r3-q1": {"type": "mc", "version": 1},
    "vector-norms-lp-r4-q1": {"type": "mc", "version": 2},
    "vector-norms-lp-r4-q2": {"type": "numeric", "version": 1},
    "vector-norms-lp-r4-q3": {"type": "mc", "version": 2},
    "cauchy-schwarz-inequality-r3-q1": {"type": "mc", "version": 1},
    "cauchy-schwarz-inequality-r4-q1": {"type": "mc", "version": 2},
    "cauchy-schwarz-inequality-r4-q2": {"type": "numeric", "version": 2},
    "cauchy-schwarz-inequality-r4-q3": {"type": "mc", "version": 2},
}

REMAINING = [
    "app-examples",
    "discrete-time",
    "feedforward",
    "gen-gain-phase",
    "limit-cycles",
    "min-phase",
    "perf-specs-freq",
    "pid-impl",
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
    expr = sp.sympify(q["answer"], locals={name: sp.Symbol(name) for name in names})
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
            if name and name not in prompt:
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
        import json
        grandfather = json.load(f)["skills"]
    if grandfather != REMAINING:
        mismatches.append("grandfather list changed beyond this slice")
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 8:
        mismatches.append(f"grandfather count {len(grandfather)} != 8")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
