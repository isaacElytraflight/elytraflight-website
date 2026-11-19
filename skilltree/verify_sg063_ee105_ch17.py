#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 feedback and op-amp retrofit.

Recomputes symbolic keys, the deep-question decisions, and the sign of every
symbolic key on the corners of its sample box. Does not import the generator.
The swapped items were multiple choice, so this batch adds no new numeric answers.
"""
import itertools
import json
import os

from verify_harness import finish, load_banks

SKILLS = [
    "opamp-models",
    "gbw",
    "inverting",
    "fb-impedance",
    "fb-amp-errors",
]

SYMBOLIC = {
    "opamp-models-r2-q4": "Gm/Cx",
    "gbw-r1-q4": "f*wu",
    "inverting-r1-q4": "-R2/R1",
    "fb-impedance-r1-q4": "Rout/(1+A*f)",
    "fb-amp-errors-r2-q4": "1/(1+a*f)",
}

# Every corner of the sample box must satisfy this. The boxes contain no
# difference of two independent positives, so a key cannot change sign.
SAFE = {
    "opamp-models-r2-q4": lambda v: v > 1e3,
    "gbw-r1-q4": lambda v: v > 100,
    "inverting-r1-q4": lambda v: v < -0.05,
    "fb-impedance-r1-q4": lambda v: v > 0.01,
    "fb-amp-errors-r2-q4": lambda v: 0.005 < v < 0.5,
}

ERRORS = {
    "opamp-models-r3-q4": (2, 0),
    "gbw-r3-q4": (1, 0),
    "inverting-r3-q4": (3, 0),
    "fb-impedance-r3-q4": (2, 0),
    "fb-amp-errors-r3-q4": (1, 0),
}

ORDERS = {
    "opamp-models-r1-q4": 4,
    "gbw-r2-q4": 4,
    "inverting-r1-q5": 4,
    "fb-impedance-r2-q4": 4,
    "fb-amp-errors-r1-q4": 4,
}

RETIRED = {
    "opamp-models": ["opamp-models-r1-q2", "opamp-models-r2-q3", "opamp-models-r3-q1"],
    "gbw": ["gbw-r1-q2", "gbw-r2-q3", "gbw-r3-q3"],
    "inverting": ["inverting-r1-q1", "inverting-r1-q2", "inverting-r3-q1"],
    "fb-impedance": ["fb-impedance-r1-q1", "fb-impedance-r2-q3", "fb-impedance-r3-q3"],
    "fb-amp-errors": ["fb-amp-errors-r2-q3", "fb-amp-errors-r1-q2", "fb-amp-errors-r3-q3"],
}

VERSIONS = {
    "opamp-models": 3,
    "gbw": 5,
    "inverting": 3,
    "fb-impedance": 3,
    "fb-amp-errors": 2,
}

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def question(banks, qid):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            return q
    return None


def corner_values(expr, specs):
    import sympy as sp
    names = [spec["name"] for spec in specs]
    local = {name: sp.Symbol(name) for name in names}
    tree = sp.sympify(expr, locals=local)
    fn = sp.lambdify([local[name] for name in names], tree, "math")
    bounds = [(float(spec["min"]), float(spec["max"])) for spec in specs]
    out = []
    for corner in itertools.product(*bounds):
        out.append(float(fn(*corner)))
    return out


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
        specs = q.get("variables") or []
        try:
            values = corner_values(expr, specs)
        except Exception as exc:
            mismatches.append(f"{qid}: corner check failed ({exc})")
            continue
        if len(values) < 2:
            mismatches.append(f"{qid}: sample box has no corners")
        for value in values:
            if not SAFE[qid](value):
                mismatches.append(f"{qid}: corner value {value} is outside the safe range")
                break
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
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 41:
        mismatches.append(f"grandfather count {len(grandfather)} != 41")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
