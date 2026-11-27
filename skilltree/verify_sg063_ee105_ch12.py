#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 single-stage amplifier retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = ["two-port", "bias-coupling", "cs-analysis", "cg", "cd", "amp-choice"]

SYMBOLIC = {
    "two-port-r2-q4": "-Gm*Rout",
    "bias-coupling-r1-q4": "1/(omega*C)",
    "cs-analysis-r3-q4": "2*VRD/Vov",
    "cg-r3-q4": "1/(gm+gmb)",
    "cd-r2-q4": "1/(gm+gmb)",
    "amp-choice-r3-q4": "1/Rmatch",
}

ERRORS = {
    "two-port-r3-q4": (3, 0),
    "bias-coupling-r1-q5": (3, 0),
    "cs-analysis-r1-q4": (3, 0),
    "cg-r2-q4": (3, 0),
    "cd-r3-q4": (3, 0),
    "amp-choice-r2-q4": (3, 0),
}

ORDERS = {
    "two-port-r1-q4": 4,
    "bias-coupling-r2-q4": 4,
    "cs-analysis-r2-q4": 4,
    "cg-r3-q5": 4,
    "cd-r1-q4": 4,
    "amp-choice-r1-q4": 4,
}

RETIRED = {
    "two-port": ["two-port-r2-q2", "two-port-r1-q1", "two-port-r3-q2"],
    "bias-coupling": ["bias-coupling-r1-q2", "bias-coupling-r2-q3", "bias-coupling-r1-q1"],
    "cs-analysis": ["cs-analysis-r3-q1", "cs-analysis-r2-q2", "cs-analysis-r1-q2"],
    "cg": ["cg-r3-q3", "cg-r3-q2", "cg-r2-q2"],
    "cd": ["cd-r2-q2", "cd-r1-q2", "cd-r3-q2"],
    "amp-choice": ["amp-choice-r3-q2", "amp-choice-r1-q1", "amp-choice-r2-q2"],
}

VERSIONS = {
    "two-port": 3,
    "bias-coupling": 3,
    "cs-analysis": 3,
    "cg": 3,
    "cd": 3,
    "amp-choice": 3,
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
    grand_path = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
    with open(grand_path, encoding="utf-8") as f:
        grandfather = json.load(f)["skills"]
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 70:
        mismatches.append(f"grandfather count {len(grandfather)} != 70")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
