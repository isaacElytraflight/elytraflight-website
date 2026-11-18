#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 frequency-response retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = ["freq-basics", "cs-brute", "miller", "cd-freq", "cg-freq", "ft", "octc"]

SYMBOLIC = {
    "freq-basics-r3-q4": "1/(2*pi*Cc*(Rleft+Rright))",
    "cs-brute-r2-q4": "Rs*(Cgs+(1+gm*Ro)*Cgd)+Ro*(Cgd+CL)",
    "miller-r1-q4": "ZF/(1-A)",
    "cd-freq-r1-q5": "Cgd+Cgs/(1+gm*R)",
    "cg-freq-r2-q4": "(1+gm*Rs)/(Rs*Cgs)",
    "ft-r2-q4": "gm/(2*pi*(Cgs+Cgd))",
    "octc-r1-q4": "Rs*(1+gm*RL)+RL",
}

ERRORS = {
    "freq-basics-r2-q4": (3, 0),
    "cs-brute-r1-q5": (3, 0),
    "miller-r3-q4": (3, 0),
    "cd-freq-r3-q4": (3, 0),
    "cg-freq-r3-q4": (3, 0),
    "ft-r1-q5": (3, 0),
    "octc-r3-q4": (3, 0),
}

ORDERS = {
    "freq-basics-r1-q4": 4,
    "cs-brute-r1-q4": 4,
    "miller-r1-q5": 4,
    "cd-freq-r1-q4": 4,
    "cg-freq-r1-q4": 4,
    "ft-r1-q4": 4,
    "octc-r1-q5": 4,
}

RETIRED = {
    "freq-basics": ["freq-basics-r1-q1", "freq-basics-r2-q2", "freq-basics-r3-q2"],
    "cs-brute": ["cs-brute-r1-q1", "cs-brute-r1-q3", "cs-brute-r2-q3"],
    "miller": ["miller-r1-q1", "miller-r1-q3", "miller-r3-q3"],
    "cd-freq": ["cd-freq-r1-q1", "cd-freq-r1-q3", "cd-freq-r3-q1"],
    "cg-freq": ["cg-freq-r1-q1", "cg-freq-r2-q3", "cg-freq-r3-q2"],
    "ft": ["ft-r1-q1", "ft-r1-q3", "ft-r2-q2"],
    "octc": ["octc-r1-q1", "octc-r1-q2", "octc-r3-q2"],
}

VERSIONS = {
    "freq-basics": 3,
    "cs-brute": 3,
    "miller": 3,
    "cd-freq": 3,
    "cg-freq": 3,
    "ft": 3,
    "octc": 5,
}

FIGURE_VERSIONS = {
    "cd-freq-r4-q3": ("0 0 698 152", 2),
    "octc-r3-q3": ("0 0 522 152", 2),
    "octc-r4-q1": ("0 0 522 152", 2),
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
    for qid, (view, version) in FIGURE_VERSIONS.items():
        q = question(banks, qid)
        if q is None:
            mismatches.append(qid + ": missing figure fix")
            continue
        if f'viewBox="{view}"' not in (q.get("figure") or ""):
            mismatches.append(qid + ": viewBox was not extended")
        if q.get("version") != version:
            mismatches.append(f"{qid}: figure version {q.get('version')} != {version}")
    grand_path = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
    with open(grand_path, encoding="utf-8") as f:
        grandfather = json.load(f)["skills"]
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 57:
        mismatches.append(f"grandfather count {len(grandfather)} != 57")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
