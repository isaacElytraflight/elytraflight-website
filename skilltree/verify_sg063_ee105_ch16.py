#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 differential-amplifier retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = [
    "diff-intro",
    "diff-dc",
    "half-circuit",
    "cmrr",
    "mirror-load",
]

SYMBOLIC = {
    "diff-intro-r2-q4": "ISS-ID1",
    "diff-dc-r2-q4": "ISS/Vov",
    "half-circuit-r1-q4": "-gm*RD/(1+2*gm*RSS)",
    "cmrr-r1-q4": "(1+2*gm*RSS)/2",
    "mirror-load-r1-q4": "ro2*ro4/(ro2+ro4)",
}

ERRORS = {
    "diff-intro-r1-q5": (2, 0),
    "diff-dc-r3-q4": (2, 0),
    "half-circuit-r2-q4": (3, 0),
    "cmrr-r2-q4": (2, 0),
    "mirror-load-r3-q4": (2, 0),
}

ORDERS = {
    "diff-intro-r1-q4": 4,
    "diff-dc-r1-q4": 4,
    "half-circuit-r1-q5": 4,
    "cmrr-r1-q5": 4,
    "mirror-load-r1-q5": 4,
}

RETIRED = {
    "diff-intro": ["diff-intro-r1-q2", "diff-intro-r1-q1", "diff-intro-r2-q3"],
    "diff-dc": ["diff-dc-r2-q2", "diff-dc-r1-q2", "diff-dc-r3-q1"],
    "half-circuit": ["half-circuit-r1-q3", "half-circuit-r1-q2", "half-circuit-r2-q3"],
    "cmrr": ["cmrr-r1-q1", "cmrr-r1-q3", "cmrr-r2-q2"],
    "mirror-load": ["mirror-load-r1-q3", "mirror-load-r1-q2", "mirror-load-r3-q2"],
}

VERSIONS = {
    "diff-intro": 3,
    "diff-dc": 3,
    "half-circuit": 3,
    "cmrr": 3,
    "mirror-load": 3,
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
    if len(grandfather) != 46:
        mismatches.append(f"grandfather count {len(grandfather)} != 46")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
