#!/usr/bin/env python3
"""Independent check for the SG-063 ME 132 LTI, Nyquist, and margins retrofit.

Recomputes symbolic keys and the deep-question decisions in this file.
Does not import the generator. The swapped items were multiple choice, so
this batch adds no new numeric answers.
"""
import os

from verify_harness import finish, load_banks

SKILLS = [
    "lti-stability",
    "freq-resp-lti",
    "nyquist",
    "uncertainty",
    "loop-margin-design",
]

SYMBOLIC = {
    "lti-stability-r3-q4": "a*b",
    "freq-resp-lti-r3-q4": "K/sqrt(a**2 + w**2)",
    "nyquist-r1-q5": "1/d",
    "uncertainty-r1-q4": "P0*(1+Wm)",
}

ERRORS = {
    "lti-stability-r2-q4": (3, 0),
    "freq-resp-lti-r2-q4": (3, 0),
    "nyquist-r2-q4": (3, 0),
    "uncertainty-r3-q4": (3, 0),
    "loop-margin-design-r1-q5": (3, 0),
}

ORDERS = {
    "lti-stability-r1-q4": 4,
    "freq-resp-lti-r1-q4": 4,
    "nyquist-r1-q4": 4,
    "uncertainty-r2-q4": 4,
    "loop-margin-design-r1-q4": 4,
}

MULTIS = {
    "loop-margin-design-r3-q4": [0, 2],
}

RETIRED = {
    "lti-stability": ["lti-stability-r1-q1", "lti-stability-r2-q2", "lti-stability-r3-q1"],
    "freq-resp-lti": ["freq-resp-lti-r1-q1", "freq-resp-lti-r2-q2", "freq-resp-lti-r3-q1"],
    "nyquist": ["nyquist-r1-q1", "nyquist-r1-q2", "nyquist-r2-q3"],
    "uncertainty": ["uncertainty-r1-q1", "uncertainty-r2-q2", "uncertainty-r3-q1"],
    "loop-margin-design": [
        "loop-margin-design-r1-q1",
        "loop-margin-design-r1-q3",
        "loop-margin-design-r3-q3",
    ],
}

VERSIONS = {
    "lti-stability": 2,
    "freq-resp-lti": 2,
    "nyquist": 2,
    "uncertainty": 2,
    "loop-margin-design": 2,
}

HELD = {
    "lti-stability-r1-q2": {"type": "numeric", "version": 1},
    "lti-stability-r3-q3": {"type": "numeric", "version": 2},
    "lti-stability-r4-q2": {"type": "mc", "version": 1},
    "freq-resp-lti-r1-q2": {"type": "numeric", "version": 1},
    "freq-resp-lti-r4-q2": {"type": "mc", "version": 1},
    "nyquist-r1-q3": {"type": "mc", "version": 1},
    "nyquist-r2-q1": {"type": "numeric", "version": 1},
    "nyquist-r3-q2": {"type": "mc", "version": 1},
    "nyquist-r4-q1": {"type": "mc", "version": 1},
    "uncertainty-r1-q2": {"type": "numeric", "version": 1},
    "uncertainty-r4-q2": {"type": "mc", "version": 1},
    "loop-margin-design-r1-q2": {"type": "numeric", "version": None},
    "loop-margin-design-r2-q3": {"type": "mc", "version": None},
    "loop-margin-design-r4-q3": {"type": "mc", "version": None},
}

REMAINING = [
    "app-examples",
    "cauchy-schwarz-inequality",
    "discrete-time",
    "equilibria",
    "feedforward",
    "gen-gain-phase",
    "inner-products",
    "limit-cycles",
    "min-phase",
    "perf-specs-freq",
    "pid-impl",
    "rayleigh-quotient",
    "realization",
    "rn-important-subsets",
    "singular-value-decomposition",
    "ss-solution",
    "ss-to-tf",
    "state-space-model",
    "vector-norms-lp",
]

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
        for spec in q.get("variables") or []:
            if spec["name"] not in q.get("prompt", ""):
                mismatches.append(f"{qid}: prompt omits graded name {spec['name']}")
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
    for qid, idxs in MULTIS.items():
        q = question(banks, qid)
        if q is None or q.get("type") != "multi":
            mismatches.append(qid + ": missing multi-select question")
            continue
        if q.get("correct_indices") != idxs:
            mismatches.append(f"{qid}: indices {q.get('correct_indices')} != {idxs}")
    for qid, spec in HELD.items():
        q = question(banks, qid)
        if q is None:
            mismatches.append(qid + ": held question is no longer live")
            continue
        if q.get("type") != spec["type"] or q.get("version") != spec["version"]:
            mismatches.append(f"{qid}: held type/version changed")
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
        rounds = {}
        for q in banks[sid]["questions"]:
            rounds[q.get("round")] = rounds.get(q.get("round"), 0) + 1
            if q.get("round") == 4 and not q.get("preview"):
                mismatches.append(q["id"] + ": round 4 lost its preview")
        if rounds != {1: 3, 2: 3, 3: 3, 4: 3}:
            mismatches.append(f"{sid}: round counts {rounds}")
    grand_path = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
    with open(grand_path, encoding="utf-8") as f:
        import json
        grandfather = json.load(f)["skills"]
    if grandfather != REMAINING:
        mismatches.append("grandfather list changed beyond this slice")
    if len(grandfather) != len(set(grandfather)):
        mismatches.append("grandfather has duplicate ids")
    if len(grandfather) != 19:
        mismatches.append(f"grandfather count {len(grandfather)} != 19")
    still = sorted(set(SKILLS) & set(grandfather))
    if still:
        mismatches.append("still grandfathered: " + ", ".join(still))
    finish(0, mismatches, banks)


if __name__ == "__main__":
    main()
