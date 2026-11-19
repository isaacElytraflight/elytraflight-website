#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 op-amp non-ideality retrofit.

Recomputes symbolic keys, the deep-question decisions, and the sign of every
symbolic key on the corners of its sample box. Does not import the generator.
The swapped items were multiple choice, so this batch adds no new numeric answers.
"""
import itertools
import json
import os

from verify_harness import finish, load_banks

SKILLS = [
    "offset",
    "bias-current",
    "opamp-fr",
    "slew",
    "noise-dist",
    "datasheet",
]

SYMBOLIC = {
    "offset-r3-q4": "Vos*(1+R2/R1)",
    "bias-current-r1-q4": "R1*R2/(R1+R2)",
    "opamp-fr-r1-q5": "wu/(1+R2/R1)",
    "slew-r2-q4": "SR/(2*pi*Vp)",
    "noise-dist-r1-q4": "en*sqrt(B)",
    "datasheet-r1-q4": "GBW/G",
}

# Every corner of the sample box must satisfy this. The boxes contain no
# difference of two independent positives, so a key cannot change sign.
SAFE = {
    "offset-r3-q4": lambda v: v > 1e-4,
    "bias-current-r1-q4": lambda v: 20 < v < 50000,
    "opamp-fr-r1-q5": lambda v: v > 1000,
    "slew-r2-q4": lambda v: v > 1000,
    "noise-dist-r1-q4": lambda v: v > 1e-8,
    "datasheet-r1-q4": lambda v: 1e4 < v < 5e8,
}

ERRORS = {
    "offset-r2-q4": (2, 0),
    "bias-current-r3-q4": (2, 0),
    "opamp-fr-r3-q4": (2, 0),
    "slew-r1-q5": (2, 0),
    "noise-dist-r2-q4": (2, 0),
    "datasheet-r4-q4": (2, 0),
}

ORDERS = {
    "offset-r1-q4": 4,
    "bias-current-r2-q4": 4,
    "opamp-fr-r1-q4": 4,
    "slew-r1-q4": 4,
    "noise-dist-r1-q5": 4,
    "datasheet-r3-q4": 4,
}

RETIRED = {
    "offset": ["offset-r1-q1", "offset-r2-q3", "offset-r3-q1"],
    "bias-current": ["bias-current-r1-q1", "bias-current-r2-q3", "bias-current-r3-q3"],
    "opamp-fr": ["opamp-fr-r1-q1", "opamp-fr-r1-q3", "opamp-fr-r3-q1"],
    "slew": ["slew-r1-q1", "slew-r1-q3", "slew-r2-q3"],
    "noise-dist": ["noise-dist-r1-q2", "noise-dist-r1-q1", "noise-dist-r2-q3"],
    "datasheet": ["datasheet-r1-q1", "datasheet-r3-q3", "datasheet-r4-q3"],
}

VERSIONS = {
    "offset": 3,
    "bias-current": 3,
    "opamp-fr": 3,
    "slew": 3,
    "noise-dist": 3,
    "datasheet": 3,
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
    if "pi" not in local:
        local["pi"] = sp.pi
    local["sqrt"] = sp.sqrt
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
        for spec in specs:
            if not (float(spec["min"]) > 0 and float(spec["max"]) > float(spec["min"])):
                mismatches.append(f"{qid}: range for {spec.get('name')} is not strictly positive")
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
            fig = q.get("figure") or ""
            if 'viewBox="0 0 340 135"' in fig:
                mismatches.append(q["id"] + ": figure axis label still outside the viewBox")
        if rounds != {1: 3, 2: 3, 3: 3, 4: 3}:
            mismatches.append(f"{sid}: round counts {rounds}")
    datasheet_r4 = question(banks, "datasheet-r4-q4")
    if datasheet_r4 is None or datasheet_r4.get("preview") != ["diff-intro"]:
        mismatches.append("datasheet-r4-q4 lost the diff-intro preview")
    grand_path = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
    with open(grand_path, encoding="utf-8") as f:
        grandfather = json.load(f)["skills"]
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 35:
        mismatches.append(f"grandfather count {len(grandfather)} != 35")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
