#!/usr/bin/env python3
"""Independent cross-check of the learning-plan simulation (does not share code with the JS).
Reads the prerequisite graph straight from ../../ee105_skills_draft.json and the playable set from ../../bank/*.json.
Prints JSON: {sessions, minutes, depth, closed_form, chain, per_session:[...]} for a from-scratch start.
Usage: python3 xcheck.py [practice_min] [challenge_min]"""
import json, glob, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
tp = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
tc = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
skills = json.load(open(os.path.join(ROOT, "ee105_skills_draft.json")))["skills"]
play = set()
for f in glob.glob(os.path.join(ROOT, "bank", "*.json")):
    b = json.load(open(f))
    if any(q["round"] == 1 for q in b["questions"]):
        play.add(b["skill_id"])
pre = {s["id"]: [p for p in s["prereqs"] if p in play] for s in skills if s["id"] in play}

# (1) closed form: a skill is practiced in session depth(s)*3-2 ... i.e. P(s)=1 for roots, P(s)=max(P(p))+3
P = {}
def practiced_session(s):
    if s not in P:
        P[s] = 1 if not pre[s] else max(practiced_session(p) for p in pre[s]) + 3
    return P[s]
for s in pre: practiced_session(s)
closed = max(P.values()) + 3            # +3 more sessions: Level 1, Level 2, Mastered
depth = max((P[s] - 1) // 3 + 1 for s in pre)

# (2) brute-force session loop written separately
tier = {s: 0 for s in pre}
sessions = 0; minutes = 0.0; per = []
while any(t < 4 for t in tier.values()):
    start = dict(tier)
    new = [s for s in pre if start[s] == 0 and all(start[p] >= 3 for p in pre[s])]
    chal = [s for s in pre if 1 <= start[s] <= 3]
    for s in new: tier[s] = 1
    for s in chal: tier[s] += 1
    sessions += 1
    m = len(new) * tp + len(chal) * tc; minutes += m
    per.append({"n": sessions, "new": len(new), "chal": len(chal), "minutes": m, "cum": minutes})
    assert sessions < 500

# (3) longest prerequisite chain (names)
def longest(s):
    best = [s]
    for p in pre[s]:
        c = longest(p) + [s]
        if len(c) > len(best): best = c
    return best
chain = max((longest(s) for s in pre), key=len)
print(json.dumps({"playable": len(pre), "sessions": sessions, "minutes": minutes, "closed_form_sessions": closed,
                  "depth": depth, "chain": chain, "per_session": per}))
