#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 bipolar-transistor retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = ["bjt-struct", "bjt-iv", "bjt-action", "ebers-moll", "early", "bjt-ss"]

SYMBOLIC = {
    "bjt-struct-r1-q4": "-(IC+IB)",
    "bjt-iv-r3-q4": "beta*IB",
    "bjt-action-r2-q4": "Dn*NE*WE/(Dp*NB*WB)",
    "ebers-moll-r1-q4": "alphaF*IES/alphaR",
    "early-r2-q4": "1+VCE/VA",
    "bjt-ss-r1-q4": "beta/gm",
}

ERRORS = {
    "bjt-struct-r3-q4": (3, 0),
    "bjt-iv-r1-q4": (3, 0),
    "bjt-action-r3-q4": (3, 0),
    "ebers-moll-r3-q4": (3, 0),
    "early-r3-q4": (3, 0),
    "bjt-ss-r2-q4": (3, 0),
}

ORDERS = {
    "bjt-struct-r1-q5": 4,
    "bjt-iv-r2-q4": 4,
    "bjt-action-r1-q4": 4,
    "ebers-moll-r2-q4": 4,
    "early-r1-q4": 4,
    "bjt-ss-r3-q4": 3,
}

RETIRED = {
    "bjt-struct": ["bjt-struct-r1-q2", "bjt-struct-r1-q1", "bjt-struct-r3-q1"],
    "bjt-iv": ["bjt-iv-r3-q1", "bjt-iv-r2-q3", "bjt-iv-r1-q2"],
    "bjt-action": ["bjt-action-r2-q3", "bjt-action-r1-q1", "bjt-action-r3-q2"],
    "ebers-moll": ["ebers-moll-r1-q2", "ebers-moll-r2-q3", "ebers-moll-r3-q3"],
    "early": ["early-r2-q1", "early-r1-q3", "early-r3-q2"],
    "bjt-ss": ["bjt-ss-r1-q3", "bjt-ss-r3-q2", "bjt-ss-r2-q2"],
}

VERSIONS = {
    "bjt-struct": 3,
    "bjt-iv": 3,
    "bjt-action": 4,
    "ebers-moll": 3,
    "early": 3,
    "bjt-ss": 4,
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
    if len(grandfather) != 76:
        mismatches.append(f"grandfather count {len(grandfather)} != 76")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
