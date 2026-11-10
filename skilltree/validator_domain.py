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

Also enforces the deep-type quota on banks that are not in
deep_quota_grandfather.json. That list is the banks written before SG-062.
Do not add ids to it. A rewritten bank should be removed; a later retrofit
removes the rest. New banks need ceil(3n/12) questions of type symbolic,
order, error, or multi.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_TOOLS = os.path.join(HERE, "..", "tools", "skilltree-content")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
from banklib import DEEP_TYPES, deep_quota
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

def deep_quota_warnings(bank_dir, grandfather):
    """Quota misses for banks that are not grandfathered.

    grandfather is a set of skill ids written before the quota. A listed id
    with no bank file is also reported, so the list cannot drift.
    """
    warns = []
    if not os.path.isdir(bank_dir):
        return [f"question bank directory missing: {bank_dir}"]
    seen = set()
    for fn in sorted(os.listdir(bank_dir)):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(bank_dir, fn)
        try:
            bank = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            warns.append(f"{fn} is not valid JSON ({exc})")
            continue
        sid = bank.get("skill_id") or fn[:-5]
        seen.add(sid)
        if sid in grandfather:
            continue
        qs = bank.get("questions")
        if not isinstance(qs, list):
            warns.append(f"{sid} deep-type quota: questions are missing")
            continue
        found = sum(1 for q in qs if isinstance(q, dict) and q.get("type") in DEEP_TYPES)
        need = deep_quota(len(qs))
        if found < need:
            warns.append(
                f"{sid} deep-type quota: {found} deep question(s), need {need} "
                f"in a {len(qs)}-question bank (symbolic, order, error, multi)"
            )
    for sid in sorted(set(grandfather) - seen):
        warns.append(f"{sid} is on the deep-quota grandfather list but has no bank")
    return warns


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

    grandfather = None
    grand_path = os.path.join(HERE, "deep_quota_grandfather.json")
    try:
        gdata = json.load(open(grand_path, encoding="utf-8"))
        if not isinstance(gdata.get("skills"), list) or not all(isinstance(x, str) for x in gdata["skills"]):
            raise ValueError("skills must be a list of ids")
        grandfather = set(gdata["skills"])
    except Exception as exc:
        warn(f"deep-quota grandfather list could not be read: {exc}")
    if grandfather is not None:
        for msg in deep_quota_warnings(os.path.join(HERE, "bank"), grandfather):
            warn(msg)

    unwaived = [w for w in warns if w not in WAIVED]
    print(f"{len(warns)} domain-leak warnings")
    for w in warns:
        tag = "WAIVED" if w in WAIVED else "WARN"
        print(f"{tag} {w}")
    print(f"{len(unwaived)} unwaived warnings")
    return 0 if not unwaived else 1

if __name__ == "__main__":
    sys.exit(main())
