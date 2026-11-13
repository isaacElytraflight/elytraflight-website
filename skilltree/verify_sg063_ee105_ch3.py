#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 semiconductor retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
from verify_harness import finish, load_banks

SKILLS = [
    "drude",
    "si-props",
    "intrinsic",
    "doping",
    "drift",
    "diffusion",
    "total-current",
]

# Keys derived again here, not read from the generator.
SYMBOLIC = {
    "drude-r1-q5": "mu*F",
    "intrinsic-r2-q4": "k*n*p",
    "doping-r2-q4": "p-n+ND-NA",
    "diffusion-r1-q5": "q*Dn*gn",
    "total-current-r1-q4": "q*n*mun*F+q*Dn*gn",
}

# flaw_index, correct_reason. The wrong step is the one that does not follow.
ERRORS = {
    "drude-r3-q4": (3, 0),
    "si-props-r3-q4": (3, 0),
    "intrinsic-r3-q4": (3, 0),
    "doping-r3-q5": (3, 0),
    "drift-r2-q4": (3, 0),
    "diffusion-r3-q4": (3, 0),
}

# Every index that must be selected. All-or-nothing.
MULTI = {
    "si-props-r1-q5": [0, 1, 3],
    "doping-r3-q4": [0, 1, 3],
    "drift-r3-q4": [0, 1, 3],
    "total-current-r1-q5": [0, 1, 2],
}

RETIRED = {
    "drude": ["drude-r1-q1", "drude-r1-q3", "drude-r3-q3"],
    "si-props": ["si-props-r1-q1", "si-props-r1-q2", "si-props-r3-q1"],
    "intrinsic": ["intrinsic-r1-q3", "intrinsic-r2-q3", "intrinsic-r3-q3"],
    "doping": ["doping-r2-q3", "doping-r3-q1", "doping-r3-q3"],
    "drift": ["drift-r1-q2", "drift-r2-q3", "drift-r3-q2"],
    "diffusion": ["diffusion-r1-q1", "diffusion-r1-q3", "diffusion-r3-q2"],
    "total-current": ["total-current-r1-q1", "total-current-r1-q3", "total-current-r3-q1"],
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
