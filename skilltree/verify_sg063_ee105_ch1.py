#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 chapter 1 retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
from verify_harness import finish, load_banks

SKILLS = [
    "lti-def",
    "rc-lpf",
    "cx-exp",
    "sinusoid-resp",
    "impulse-conv",
    "step-resp",
    "freq-char",
    "lti-circuits",
    "freq-resp-circuits",
]

# Keys derived again here, not read from the generator.
SYMBOLIC = {
    "rc-lpf-r1-q4": "Vf+(Vi-Vf)*exp(-t/tau)",
    "cx-exp-r2-q4": "r*s*cos(a+b)",
    "sinusoid-resp-r1-q4": "1/sqrt(1+(w*tau)^2)",
    "impulse-conv-r1-q5": "x0*h1+x1*h0",
    "step-resp-r2-q4": "(a/b)*(1-exp(-b*t))",
    "freq-char-r1-q5": "20*ln(g)/ln(10)",
    "lti-circuits-r1-q4": "Vs*(1-exp(-t/(R*C)))",
    "freq-resp-circuits-r2-q4": "1/(w*C)",
}

# flaw_index, correct_reason. The wrong step is the one that does not follow.
ERRORS = {
    "lti-def-r3-q4": (3, 0),
    "rc-lpf-r2-q4": (3, 0),
    "cx-exp-r1-q4": (3, 0),
    "sinusoid-resp-r3-q4": (3, 0),
    "step-resp-r1-q5": (3, 0),
    "lti-circuits-r3-q4": (3, 0),
    "freq-resp-circuits-r3-q4": (3, 0),
}

# Every index that must be selected. All-or-nothing.
MULTI = {
    "lti-def-r2-q4": [0, 2],
    "impulse-conv-r2-q4": [0, 2],
    "freq-char-r3-q4": [0, 1, 2],
    "freq-resp-circuits-r1-q4": [0, 1, 2],
}

RETIRED = {
    "lti-def": ["lti-def-r1-q1", "lti-def-r2-q1", "lti-def-r3-q2"],
    "rc-lpf": ["rc-lpf-r1-q1", "rc-lpf-r1-q2", "rc-lpf-r2-q3"],
    "cx-exp": ["cx-exp-r1-q1", "cx-exp-r1-q2", "cx-exp-r2-q2"],
    "sinusoid-resp": ["sinusoid-resp-r1-q2", "sinusoid-resp-r2-q3", "sinusoid-resp-r3-q3"],
    "impulse-conv": ["impulse-conv-r1-q1", "impulse-conv-r1-q2", "impulse-conv-r2-q3"],
    "step-resp": ["step-resp-r1-q1", "step-resp-r1-q3", "step-resp-r2-q3"],
    "freq-char": ["freq-char-r1-q1", "freq-char-r1-q2", "freq-char-r3-q3"],
    "lti-circuits": ["lti-circuits-r1-q1", "lti-circuits-r2-q2", "lti-circuits-r3-q2"],
    "freq-resp-circuits": ["freq-resp-circuits-r1-q3", "freq-resp-circuits-r2-q1", "freq-resp-circuits-r3-q1"],
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
