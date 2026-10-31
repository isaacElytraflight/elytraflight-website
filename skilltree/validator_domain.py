#!/usr/bin/env python3
"""Domain-leak check for the v3 split, run against a collections file.

A skill is EE-only when it sits in EE 105 and in neither ME 132 nor Feedback
Systems. Warnings:

- rc-lpf or a retired id is still listed in ME 132 or Feedback Systems
- an application skill is missing from its chapter, or sits in the other domain
- a skill inside ME 132 or Feedback Systems has an EE-only skill in its
  prerequisite closure (the leak an ME student would be asked to learn)

Usage: python3 validator_domain.py [collections.json] [skills.json]
Prints "N domain-leak warnings" and exits 0 when every warning is waived.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLLECTIONS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "collections.json")
SKILLS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "ee105_skills_draft.json")

CORES = ["lti-def", "cx-exp", "impulse-conv", "step-resp", "sinusoid-resp", "freq-char",
         "tf", "pole-zero", "bode", "fb-intro", "loop-gain", "fb-errors", "stability"]
# skill -> boxes it must occupy, and boxes it must not
REQUIRED = {
    "lti-circuits": {"ee105-ch1"},
    "freq-resp-circuits": {"ee105-ch1"},
    "bode-circuits": {"ee105-ch2"},
    "fb-amp": {"ee105-ch17"},
    "fb-amp-errors": {"ee105-ch17"},
    "amp-compensation": {"ee105-ch17"},
    "lti-mech": {"me132/m2", "am08/ch2"},
    "loop-margin-design": {"me132/m5", "am08/ch9"},
}
EE_APPS = {"lti-circuits", "freq-resp-circuits", "bode-circuits", "fb-amp", "fb-amp-errors", "amp-compensation"}
ME_APPS = {"lti-mech", "loop-margin-design"}
# Known overlaps that are not leaks. Empty for v3: the split is clean.
WAIVED = set()

def boxes_under(boxes, top):
    by = {b["id"]: b for b in boxes}
    out = set()
    def walk(bid):
        b = by[bid]
        out.add(bid)
        for child in b.get("children") or []:
            walk(child)
    walk(top)
    return out

def main():
    graph = json.load(open(SKILLS, encoding="utf-8"))
    collections = json.load(open(COLLECTIONS, encoding="utf-8"))
    skills = {s["id"]: s for s in graph["skills"]}
    retired = graph.get("retired") or {}
    boxes = collections["boxes"]
    by = {b["id"]: b for b in boxes}
    warns = []
    def warn(msg):
        warns.append(msg)

    me_ids = boxes_under(boxes, "me132")
    am_ids = boxes_under(boxes, "am08")
    ee_ids = boxes_under(boxes, "ee105-ucb")

    def members(ids):
        out = set()
        for bid in ids:
            out.update(by[bid].get("skills") or [])
        return out

    me, am, ee = members(me_ids), members(am_ids), members(ee_ids)
    ee_only = ee - me - am
    homes = {}
    for b in boxes:
        for sid in b.get("skills") or []:
            homes.setdefault(sid, set()).add(b["id"])

    if retired.get("margins") != "stability":
        warn("retired map should send margins to stability")
    if "margins" in skills:
        warn("margins is still a live skill")
    for sid in ("rc-lpf", "margins"):
        bad = sorted(homes.get(sid, set()) & (me_ids | am_ids))
        if bad:
            warn(f"{sid} is still in a non-EE box: {', '.join(bad)}")
    for sid, need in REQUIRED.items():
        got = homes.get(sid, set())
        missing = sorted(need - got)
        if missing:
            warn(f"{sid} missing from {', '.join(missing)}")
        if sid in EE_APPS and got & (me_ids | am_ids):
            warn(f"{sid} is an EE application skill inside ME 132 or Feedback Systems")
        if sid in ME_APPS and got & ee_ids:
            warn(f"{sid} is an ME application skill inside EE 105")
    for sid in CORES:
        if sid not in me:
            warn(f"core skill {sid} is not in the ME 132 box")

    def closure(sid):
        out, stack = set(), list(skills[sid].get("prereqs") or [])
        while stack:
            pre = stack.pop()
            if pre in out:
                continue
            out.add(pre)
            stack.extend(skills[pre].get("prereqs") or [])
        return out

    for sid in sorted(me | am):
        if sid not in skills:
            warn(f"{sid} is listed in a box but missing from the graph")
            continue
        leak = sorted(closure(sid) & ee_only)
        if leak:
            where = "ME 132" if sid in me else "Feedback Systems"
            warn(f"{sid} ({where}) prerequisite closure contains EE-only {', '.join(leak)}")

    unwaived = [w for w in warns if w not in WAIVED]
    print(f"{len(warns)} domain-leak warnings")
    for w in warns:
        tag = "WAIVED" if w in WAIVED else "WARN"
        print(f"{tag} {w}")
    print(f"{len(unwaived)} unwaived warnings")
    return 0 if not unwaived else 1

if __name__ == "__main__":
    sys.exit(main())
