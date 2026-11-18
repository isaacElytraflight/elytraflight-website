#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 current-mirror retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = ["high-load", "diode-conn", "mirror", "degeneration", "cascode-src", "ref-gen"]

SYMBOLIC = {
    "high-load-r2-q4": "2/(Vov*(lamn+lamp))",
    "diode-conn-r3-q4": "1/sqrt(2*kn*IB)",
    "mirror-r1-q4": "IREF*WL2/WL1",
    "degeneration-r1-q4": "gm/(1+gm*RS)",
    "cascode-src-r2-q4": "1/(gm2*ro2)",
    "ref-gen-r1-q4": "2*(1-1/sqrt(K))/R",
}

ERRORS = {
    "high-load-r3-q4": (3, 0),
    "diode-conn-r2-q4": (3, 0),
    "mirror-r3-q4": (3, 0),
    "degeneration-r2-q4": (3, 0),
    "cascode-src-r1-q5": (3, 0),
    "ref-gen-r2-q5": (3, 0),
}

ORDERS = {
    "high-load-r1-q4": 4,
    "diode-conn-r1-q4": 4,
    "mirror-r2-q4": 4,
    "degeneration-r3-q4": 4,
    "cascode-src-r1-q4": 4,
    "ref-gen-r2-q4": 4,
}

RETIRED = {
    "high-load": ["high-load-r2-q3", "high-load-r1-q1", "high-load-r3-q2"],
    "diode-conn": ["diode-conn-r3-q2", "diode-conn-r1-q1", "diode-conn-r2-q1"],
    "mirror": ["mirror-r1-q3", "mirror-r2-q3", "mirror-r3-q2"],
    "degeneration": ["degeneration-r1-q3", "degeneration-r3-q2", "degeneration-r2-q3"],
    "cascode-src": ["cascode-src-r2-q3", "cascode-src-r1-q2", "cascode-src-r1-q3"],
    "ref-gen": ["ref-gen-r1-q2", "ref-gen-r2-q2", "ref-gen-r2-q3"],
}

VERSIONS = {
    "high-load": 3,
    "diode-conn": 3,
    "mirror": 3,
    "degeneration": 3,
    "cascode-src": 3,
    "ref-gen": 3,
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
    grand_path = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
    with open(grand_path, encoding="utf-8") as f:
        grandfather = json.load(f)["skills"]
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 64:
        mismatches.append(f"grandfather count {len(grandfather)} != 64")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
