#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 MOSFET-physics retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = ["mosfet-struct", "nmos-regions", "triode", "square-law", "pmos"]

SYMBOLIC = {
    "mosfet-struct-r1-q4": "W2*L1/(W1*L2)",
    "nmos-regions-r3-q4": "Vgs-Vt",
    "triode-r2-q4": "1/(unCox*WL*Vov)",
    "square-law-r2-q4": "-Cox*(Vgs-Vy-Vt)",
    "pmos-r1-q4": "Vsg-Vtp",
}

ERRORS = {
    "mosfet-struct-r3-q4": (3, 0),
    "nmos-regions-r3-q5": (3, 0),
    "triode-r1-q4": (3, 0),
    "square-law-r1-q4": (3, 0),
    "pmos-r2-q4": (3, 0),
}

RETIRED = {
    "mosfet-struct": ["mosfet-struct-r1-q2", "mosfet-struct-r2-q2", "mosfet-struct-r3-q2"],
    "nmos-regions": ["nmos-regions-r3-q2", "nmos-regions-r2-q2", "nmos-regions-r3-q1"],
    "triode": ["triode-r2-q2", "triode-r3-q3", "triode-r1-q3"],
    "square-law": ["square-law-r2-q1", "square-law-r2-q3", "square-law-r1-q3"],
    "pmos": ["pmos-r1-q1", "pmos-r1-q3", "pmos-r2-q2"],
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
