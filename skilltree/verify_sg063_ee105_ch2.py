#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 AC-circuits retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
from verify_harness import finish, load_banks

SKILLS = [
    "tf",
    "phasors",
    "direct-h",
    "pole-zero",
    "rlc",
    "bode",
    "ac-power",
    "bode-circuits",
]

# Keys derived again here, not read from the generator.
SYMBOLIC = {
    "tf-r1-q5": "d/(a*s^2+b*s+c)",
    "phasors-r1-q4": "1/(w*C)",
    "direct-h-r1-q4": "1/sqrt(1+(w*R*C)^2)",
    "pole-zero-r1-q5": "exp(-a*t)",
    "rlc-r1-q4": "1/sqrt(L*C)",
    "bode-r1-q4": "20*ln(K)/ln(10)",
    "ac-power-r1-q5": "Vp^2/(2*R)",
    "bode-circuits-r1-q4": "-1/tau",
}

# flaw_index, correct_reason. The wrong step is the one that does not follow.
ERRORS = {
    "tf-r3-q4": (3, 0),
    "direct-h-r2-q4": (3, 0),
    "pole-zero-r1-q6": (3, 0),
    "rlc-r1-q5": (3, 0),
    "bode-r3-q4": (3, 0),
    "ac-power-r1-q4": (3, 0),
    "bode-circuits-r2-q4": (3, 0),
}

# Every index that must be selected. All-or-nothing.
MULTI = {
    "phasors-r1-q5": [0, 2],
    "rlc-r3-q4": [0, 1, 2],
    "ac-power-r3-q4": [0, 2],
    "bode-circuits-r3-q4": [0, 2],
}

RETIRED = {
    "tf": ["tf-r1-q1", "tf-r1-q2", "tf-r3-q2"],
    "phasors": ["phasors-r1-q1", "phasors-r1-q2", "phasors-r3-q3"],
    "direct-h": ["direct-h-r1-q1", "direct-h-r1-q2", "direct-h-r2-q3"],
    "pole-zero": ["pole-zero-r1-q1", "pole-zero-r1-q2", "pole-zero-r1-q3"],
    "rlc": ["rlc-r1-q1", "rlc-r1-q2", "rlc-r3-q1"],
    "bode": ["bode-r1-q2", "bode-r2-q3", "bode-r3-q2"],
    "ac-power": ["ac-power-r1-q1", "ac-power-r1-q2", "ac-power-r3-q1"],
    "bode-circuits": ["bode-circuits-r1-q1", "bode-circuits-r2-q1", "bode-circuits-r3-q1"],
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
