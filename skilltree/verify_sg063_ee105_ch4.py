#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 IC-passives retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
from verify_harness import finish, load_banks

SKILLS = [
    "ic-fab",
    "sheet-res",
    "electrostatics",
    "mim-cap",
    "nl-cap",
]

# Keys derived again here, not read from the generator.
SYMBOLIC = {
    "sheet-res-r1-q4": "Rs*L/W",
    "electrostatics-r1-q5": "-s",
    "electrostatics-r2-q4": "Esi*es/eox",
    "mim-cap-r1-q4": "eps*A/t",
    "nl-cap-r1-q4": "2*K*V",
}

# flaw_index, correct_reason. The wrong step is the one that does not follow.
ERRORS = {
    "ic-fab-r2-q4": (3, 0),
    "sheet-res-r3-q5": (3, 0),
    "mim-cap-r2-q4": (3, 0),
    "nl-cap-r1-q5": (3, 0),
}

# Every index that must be selected. All-or-nothing.
MULTI = {
    "ic-fab-r3-q4": [0, 1, 3],
    "sheet-res-r3-q4": [0, 1, 2],
    "nl-cap-r3-q4": [0, 1, 3],
}

RETIRED = {
    "ic-fab": ["ic-fab-r1-q2", "ic-fab-r2-q3", "ic-fab-r3-q2"],
    "sheet-res": ["sheet-res-r1-q1", "sheet-res-r3-q2", "sheet-res-r3-q3"],
    "electrostatics": ["electrostatics-r1-q1", "electrostatics-r1-q2", "electrostatics-r2-q3"],
    "mim-cap": ["mim-cap-r1-q1", "mim-cap-r1-q3", "mim-cap-r2-q3"],
    "nl-cap": ["nl-cap-r1-q1", "nl-cap-r1-q2", "nl-cap-r3-q3"],
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
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
