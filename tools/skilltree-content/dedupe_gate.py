#!/usr/bin/env python3
"""Warn when a new or changed skill looks like one that already exists.

Compares each checked skill's name, synonyms (`synonyms` or `owns`), and
summary with every other skill. A hit is a normalized token Jaccard on the
name of at least 0.6 with two shared words, or a Jaccard of at least 0.5 on
the combined text with five shared words.

Resolve a hit by reusing the existing skill, splitting a neutral core from a
domain application, or recording a distinct decision in
docs/dedupe-decisions.json. A decision is not a way to hide a real duplicate.

  python3 tools/skilltree-content/dedupe_gate.py
  python3 tools/skilltree-content/dedupe_gate.py --batch me132-b1
  python3 tools/skilltree-content/dedupe_gate.py --skills kalman,observer
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GRAPH = os.path.join(ROOT, "skilltree", "ee105_skills_draft.json")
DECISIONS = os.path.join(ROOT, "docs", "dedupe-decisions.json")
NAME_J = 0.6
NAME_SHARED = 2
FULL_J = 0.5
FULL_SHARED = 5
STOP = set(
    "a an the of and or to in for with on from by its their into over under "
    "than then this that these those using use via per as is are be".split()
)


def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in STOP and len(w) > 1]


def synonym_text(skill):
    raw = skill.get("synonyms")
    if raw is None:
        raw = skill.get("owns") or ""
    if isinstance(raw, list):
        return " ".join(str(part) for part in raw)
    return str(raw)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def decisions():
    if not os.path.isfile(DECISIONS):
        return set()
    data = load_json(DECISIONS)
    done = set()
    for pair in data.get("pairs") or []:
        ids = pair.get("ids") or []
        if len(ids) == 2 and pair.get("resolution") in ("reuse", "split", "distinct"):
            done.add(tuple(sorted(ids)))
    return done


def skill_rows(skills):
    rows = []
    for skill in skills:
        name = tokens(skill.get("name"))
        full = tokens(" ".join([
            skill.get("name") or "",
            synonym_text(skill),
            skill.get("summary") or "",
        ]))
        rows.append({
            "id": skill["id"],
            "name": skill.get("name") or skill["id"],
            "name_set": set(name),
            "full_set": set(full),
        })
    return rows


def overlaps(rows, focus, resolved):
    by_id = {row["id"]: row for row in rows}
    hits = []
    for sid in focus:
        left = by_id.get(sid)
        if left is None:
            hits.append((sid, None, 0, 0, "missing from the skill graph"))
            continue
        for right in rows:
            if right["id"] == sid:
                continue
            key = tuple(sorted((sid, right["id"])))
            if key in resolved:
                continue
            shared_name = len(left["name_set"] & right["name_set"])
            name_j = shared_name / len(left["name_set"] | right["name_set"]) if left["name_set"] and right["name_set"] else 0
            shared_full = len(left["full_set"] & right["full_set"])
            full_j = shared_full / len(left["full_set"] | right["full_set"]) if left["full_set"] and right["full_set"] else 0
            name_hit = name_j >= NAME_J and shared_name >= NAME_SHARED
            full_hit = full_j >= FULL_J and shared_full >= FULL_SHARED
            if name_hit or full_hit:
                hits.append((sid, right["id"], name_j, full_j, right["name"]))
    return hits


def focus_ids(argv, all_ids):
    if "--batch" in argv:
        name = argv[argv.index("--batch") + 1]
        spec = load_json(os.path.join(ROOT, "docs", "batches", name + ".json"))
        return spec["skills"]
    if "--skills" in argv:
        raw = argv[argv.index("--skills") + 1]
        return [part.strip() for part in raw.split(",") if part.strip()]
    return all_ids


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    skills = load_json(GRAPH)["skills"]
    rows = skill_rows(skills)
    focus = focus_ids(argv, [row["id"] for row in rows])
    hits = overlaps(rows, focus, decisions())
    if hits:
        print(f"FAILED dedupe gate: {len(hits)} likely overlap(s)")
        for sid, other, name_j, full_j, title in hits:
            if other is None:
                print(f"  {sid}: {title}")
            else:
                print(f"  {sid} ~ {other} (name {name_j:.2f}, text {full_j:.2f}): {title}")
        print("Resolve by reusing the skill, splitting a core from an application, or recording the pair in docs/dedupe-decisions.json.")
        return 1
    print(f"OK: dedupe gate, 0 unresolved overlaps ({len(focus)} skills checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
