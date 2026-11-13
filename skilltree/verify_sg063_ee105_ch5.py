#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 PN-equilibrium retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
from verify_harness import finish, load_banks

SKILLS = [
    "carrier-pot",
    "pn-overview",
    "depl-approx",
    "contact-pot",
    "rev-bias",
    "junction-cap",
]

# Keys derived again here, not read from the generator.
SYMBOLIC = {
    "carrier-pot-r1-q4": "Vt*ln(10)",
    "carrier-pot-r2-q4": "exp(dphi/Vt)",
    "pn-overview-r2-q4": "p-n+ND-NA",
    "depl-approx-r3-q4": "NA/ND",
    "contact-pot-r3-q4": "Vt*ln(NA*ND/(ni*ni))",
    "rev-bias-r3-q4": "sqrt(1-VD/phibi)",
    "junction-cap-r1-q4": "eps/Xd",
}

# flaw_index, correct_reason. The wrong step is the one that does not follow.
ERRORS = {
    "carrier-pot-r3-q4": (3, 0),
    "pn-overview-r2-q5": (3, 0),
    "depl-approx-r3-q5": (3, 0),
    "contact-pot-r1-q4": (3, 0),
    "rev-bias-r1-q5": (3, 0),
    "junction-cap-r2-q4": (3, 0),
}

# Every index that must be selected. All-or-nothing.
MULTI = {
    "contact-pot-r3-q5": [0, 1, 3],
}

RETIRED = {
    "carrier-pot": ["carrier-pot-r1-q3", "carrier-pot-r2-q3", "carrier-pot-r3-q3"],
    "pn-overview": ["pn-overview-r2-q3", "pn-overview-r2-q1", "pn-overview-r1-q2"],
    "depl-approx": ["depl-approx-r1-q1", "depl-approx-r3-q1", "depl-approx-r3-q3"],
    "contact-pot": ["contact-pot-r3-q1", "contact-pot-r3-q3", "contact-pot-r1-q3"],
    "rev-bias": ["rev-bias-r1-q1", "rev-bias-r1-q3", "rev-bias-r3-q1"],
    "junction-cap": ["junction-cap-r1-q3", "junction-cap-r2-q3", "junction-cap-r3-q3"],
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
    for qid, idxs in MULTI.items():
        q = question(banks, qid)
        if q is None or q.get("type") != "multi":
            mismatches.append(qid + ": missing multi-select question")
            continue
        if sorted(q.get("correct_indices") or []) != sorted(idxs):
            mismatches.append(f"{qid}: indices {q.get('correct_indices')} != {idxs}")
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
    q = question(banks, "rev-bias-r3-q3")
    if q is None or q.get("version") != 2:
        mismatches.append("rev-bias-r3-q3: figure edit should be version 2")
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
