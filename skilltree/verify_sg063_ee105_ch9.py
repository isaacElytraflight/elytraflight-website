#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 MOS small-signal retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = ["cs-intro", "gm", "ro", "ss-model"]

SYMBOLIC = {
    "cs-intro-r1-q4": "(VDD-VDS)/RD",
    "gm-r1-q4": "sqrt(ID2/ID1)",
    "ro-r2-q4": "-1/lam",
    "ss-model-r3-q4": "vg-vs",
}

ERRORS = {
    "cs-intro-r2-q4": (3, 0),
    "gm-r3-q4": (3, 0),
    "ro-r3-q4": (3, 0),
    "ss-model-r1-q5": (3, 0),
}

RETIRED = {
    "cs-intro": ["cs-intro-r1-q3", "cs-intro-r1-q2", "cs-intro-r2-q3"],
    "gm": ["gm-r1-q2", "gm-r2-q1", "gm-r3-q2"],
    "ro": ["ro-r2-q3", "ro-r1-q1", "ro-r3-q2"],
    "ss-model": ["ss-model-r3-q1", "ss-model-r1-q1", "ss-model-r1-q2"],
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
    for sid, old_ids in RETIRED.items():
        live = {q["id"] for q in banks[sid]["questions"]}
        retired = [q["id"] for q in banks[sid].get("retired_questions") or []]
        if sorted(retired) != sorted(old_ids):
            mismatches.append(f"{sid}: retired {retired} != {old_ids}")
        overlap = sorted(set(retired) & live)
        if overlap:
            mismatches.append(f"{sid}: reused {overlap}")
        deep = sum(1 for q in banks[sid]["questions"] if q.get("type") in ("symbolic", "order", "error", "multi"))
        if deep < 3:
            mismatches.append(f"{sid}: only {deep} deep questions")
    grand_path = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
    with open(grand_path, encoding="utf-8") as f:
        grandfather = json.load(f)["skills"]
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
