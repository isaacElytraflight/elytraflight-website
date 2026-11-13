#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 PN-currents retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
from verify_harness import finish, load_banks

SKILLS = [
    "diode-qual",
    "excess-carriers",
    "continuity",
    "minority-profile",
    "diode-iv",
    "diode-ss",
    "solar-cell",
    "led",
]

SYMBOLIC = {
    "diode-qual-r2-q4": "phibi-VD",
    "excess-carriers-r1-q4": "p-p0",
    "excess-carriers-r2-q4": "1/(cp*NT)",
    "continuity-r1-q4": "dp0*exp(-x/Lp)",
    "continuity-r1-q5": "sqrt(Dp*taup)",
    "minority-profile-r1-q4": "pn0*exp(VD/Vt)",
    "minority-profile-r3-q5": "q*Dp*dp/W",
    "diode-iv-r1-q4": "IS*(exp(VD/(n*Vt))-1)",
    "diode-iv-r2-q4": "n*Vt*ln(10)",
    "diode-iv-r3-q4": "Vt*ln(2)",
    "diode-ss-r1-q4": "ID/Vt",
    "solar-cell-r3-q4": "Vt*ln(tau*GL*ND/(ni*ni))",
    "led-r3-q4": "h*c/lam",
}

ERRORS = {
    "diode-qual-r1-q5": (3, 0),
    "excess-carriers-r3-q4": (3, 0),
    "continuity-r3-q4": (3, 0),
    "minority-profile-r3-q4": (3, 0),
    "diode-ss-r1-q5": (3, 0),
    "solar-cell-r1-q4": (3, 0),
    "led-r1-q5": (3, 0),
}

MULTI = {
    "diode-ss-r2-q4": [0, 1, 3],
}

RETIRED = {
    "diode-qual": ["diode-qual-r2-q1", "diode-qual-r1-q1", "diode-qual-r1-q2"],
    "excess-carriers": ["excess-carriers-r1-q1", "excess-carriers-r2-q3", "excess-carriers-r3-q3"],
    "continuity": ["continuity-r1-q2", "continuity-r1-q3", "continuity-r3-q3"],
    "minority-profile": ["minority-profile-r1-q2", "minority-profile-r3-q1", "minority-profile-r3-q3"],
    "diode-iv": ["diode-iv-r1-q1", "diode-iv-r2-q3", "diode-iv-r3-q1"],
    "diode-ss": ["diode-ss-r1-q1", "diode-ss-r1-q3", "diode-ss-r2-q3"],
    "solar-cell": ["solar-cell-r3-q1", "solar-cell-r1-q3", "solar-cell-r2-q2"],
    "led": ["led-r3-q3", "led-r1-q1", "led-r1-q3"],
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
