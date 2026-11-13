#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 MOS-capacitor retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
from verify_harness import finish, load_banks

SKILLS = ["mos-struct", "mos-regions", "vt", "mos-fields", "mos-cv"]

SYMBOLIC = {
    "mos-struct-r1-q4": "eox/tox",
    "mos-regions-r3-q4": "ni*exp(phis/Vt)",
    "vt-r1-q4": "VFB-2*phip+(1/Cox)*sqrt(2*q*es*NA*(-2*phip))",
    "vt-r2-q4": "QB/Cox",
    "mos-fields-r1-q4": "Eox*eox/es",
    "mos-cv-r1-q4": "1/(1/Cox+Xd/es)",
}

ERRORS = {
    "mos-struct-r3-q4": (3, 0),
    "mos-regions-r3-q5": (3, 0),
    "vt-r3-q4": (3, 0),
    "mos-fields-r3-q4": (3, 0),
    "mos-cv-r3-q5": (3, 0),
}

RETIRED = {
    "mos-struct": ["mos-struct-r1-q2", "mos-struct-r2-q3", "mos-struct-r3-q3"],
    "mos-regions": ["mos-regions-r3-q2", "mos-regions-r1-q1", "mos-regions-r3-q1"],
    "vt": ["vt-r1-q1", "vt-r2-q3", "vt-r3-q2"],
    "mos-fields": ["mos-fields-r1-q2", "mos-fields-r2-q3", "mos-fields-r3-q2"],
    "mos-cv": ["mos-cv-r1-q2", "mos-cv-r3-q1", "mos-cv-r3-q3"],
}


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
    if question(banks, "vt-r2-q3") is not None:
        mismatches.append("vt-r2-q3: out-of-bounds figure is still live")
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
