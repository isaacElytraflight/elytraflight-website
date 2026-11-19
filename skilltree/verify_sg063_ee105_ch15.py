#!/usr/bin/env python3
"""Independent check for the SG-063 EE 105 multi-stage amplifier retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import json
import os

from verify_harness import finish, load_banks

SKILLS = [
    "cs-cascade",
    "cs-cascade-freq",
    "cs-cap-load",
    "cascode-amp",
    "cascode-bias",
    "big-circuit",
]

SYMBOLIC = {
    "cs-cascade-r1-q5": "ro*roc/(ro+roc)",
    "cs-cascade-freq-r1-q4": "R1*(Cgs2+Cdb1+Cgd2*(1+gm2*R2))",
    "cs-cap-load-r1-q4": "gm/CL",
    "cascode-amp-r1-q4": "ro1+ro2+gm2*ro1*ro2",
    "cascode-bias-r2-q4": "VT+2*Vov",
    "big-circuit-r3-q4": "(ro3+RL)/(1+gm3*ro3)",
}

ERRORS = {
    "cs-cascade-r3-q4": (3, 0),
    "cs-cascade-freq-r2-q4": (3, 0),
    "cs-cap-load-r2-q4": (3, 0),
    "cascode-amp-r3-q4": (3, 0),
    "cascode-bias-r4-q4": (3, 0),
    "big-circuit-r1-q5": (3, 0),
}

ORDERS = {
    "cs-cascade-r1-q4": 4,
    "cs-cascade-freq-r3-q4": 4,
    "cs-cap-load-r3-q4": 4,
    "cascode-amp-r2-q4": 4,
    "cascode-bias-r1-q4": 4,
    "big-circuit-r1-q4": 4,
}

RETIRED = {
    "cs-cascade": ["cs-cascade-r1-q2", "cs-cascade-r1-q3", "cs-cascade-r3-q1"],
    "cs-cascade-freq": ["cs-cascade-freq-r1-q1", "cs-cascade-freq-r2-q2", "cs-cascade-freq-r3-q1"],
    "cs-cap-load": ["cs-cap-load-r1-q1", "cs-cap-load-r2-q2", "cs-cap-load-r3-q3"],
    "cascode-amp": ["cascode-amp-r1-q1", "cascode-amp-r2-q2", "cascode-amp-r3-q3"],
    "cascode-bias": ["cascode-bias-r1-q1", "cascode-bias-r2-q3", "cascode-bias-r4-q1"],
    "big-circuit": ["big-circuit-r1-q1", "big-circuit-r1-q2", "big-circuit-r3-q1"],
}

VERSIONS = {
    "cs-cascade": 3,
    "cs-cascade-freq": 4,
    "cs-cap-load": 4,
    "cascode-amp": 3,
    "cascode-bias": 3,
    "big-circuit": 3,
}

FIGURE_VERSIONS = {
    "cs-cascade-freq-r1-q2": ("0 0 522 152", 3),
    "cs-cascade-freq-r1-q3": ("0 0 522 152", 3),
    "cs-cascade-freq-r2-q1": ("0 0 522 152", 2),
    "cs-cascade-freq-r3-q2": ("0 0 698 152", 3),
    "cs-cascade-freq-r3-q3": ("0 0 698 152", 3),
    "cs-cascade-freq-r4-q1": ("0 0 522 152", 2),
    "cs-cascade-freq-r4-q3": ("0 0 522 152", 2),
    "cascode-amp-r2-q3": ("0 0 522 152", 3),
    "cascode-amp-r3-q1": ("0 0 522 152", 2),
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
    preview = question(banks, "cascode-bias-r4-q4")
    if preview is None or preview.get("preview") != ["big-circuit"]:
        mismatches.append("cascode-bias-r4-q4: preview was not kept")
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
    if len(grandfather) != 51:
        mismatches.append(f"grandfather count {len(grandfather)} != 51")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
