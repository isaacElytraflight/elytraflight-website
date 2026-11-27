#!/usr/bin/env python3
"""Independent check for the SG-063 ME 132 first- and second-order retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = [
    "laplace",
    "step-specs",
    "pid",
    "windup",
    "pid-tuning",
]

SYMBOLIC = {
    "laplace-r1-q4": "A/s",
    "step-specs-r3-q4": "1/(1+K)",
    "pid-r2-q4": "Kp/Kd",
    "windup-r2-q4": "-excess/Tt",
    "pid-tuning-r2-q4": "1.2*tau/(K*L)",
}

ERRORS = {
    "laplace-r2-q4": (3, 0),
    "step-specs-r2-q4": (3, 0),
    "pid-r1-q5": (3, 0),
    "windup-r3-q4": (3, 0),
}

ORDERS = {
    "laplace-r1-q5": 4,
    "step-specs-r1-q4": 4,
    "pid-r1-q4": 4,
    "windup-r1-q4": 4,
    "pid-tuning-r1-q4": 3,
}

MULTIS = {
    "pid-tuning-r3-q4": [0, 2],
}

RETIRED = {
    "laplace": ["laplace-r1-q1", "laplace-r1-q3", "laplace-r2-q2"],
    "step-specs": ["step-specs-r1-q1", "step-specs-r2-q3", "step-specs-r3-q3"],
    "pid": ["pid-r1-q1", "pid-r1-q3", "pid-r2-q1"],
    "windup": ["windup-r1-q1", "windup-r2-q2", "windup-r3-q1"],
    "pid-tuning": ["pid-tuning-r1-q1", "pid-tuning-r2-q2", "pid-tuning-r3-q1"],
}

VERSIONS = {
    "laplace": 3,
    "step-specs": 2,
    "pid": 2,
    "windup": 2,
    "pid-tuning": 3,
}

HELD = {
    "laplace-r2-q3": {"type": "numeric", "version": 2},
    "laplace-r3-q2": {"type": "mc", "version": 1},
    "laplace-r4-q1": {"type": "numeric", "version": 2},
    "laplace-r4-q2": {"type": "numeric", "version": 1},
    "laplace-r4-q3": {"type": "numeric", "version": 1},
    "step-specs-r1-q2": {"type": "numeric", "version": 2},
    "step-specs-r1-q3": {"type": "numeric", "version": 2},
    "step-specs-r2-q1": {"type": "numeric", "version": 3},
    "step-specs-r4-q1": {"type": "numeric", "version": 2},
    "step-specs-r4-q3": {"type": "mc", "version": 2},
    "pid-r1-q2": {"type": "numeric", "version": 2},
    "pid-r3-q2": {"type": "mc", "version": 1},
    "pid-r4-q1": {"type": "numeric", "version": 2},
    "pid-r4-q2": {"type": "mc", "version": 1},
    "windup-r4-q2": {"type": "mc", "version": 1},
    "pid-tuning-r2-q3": {"type": "numeric", "version": 2},
    "pid-tuning-r4-q2": {"type": "mc", "version": 1},
}

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def question(banks, qid):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            return q
    return None


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
        grandfather = json.load(f)["skills"]
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 24:
        mismatches.append(f"grandfather count {len(grandfather)} != 24")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
