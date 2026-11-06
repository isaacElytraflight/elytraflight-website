#!/usr/bin/env python3
"""Graph checks for the skill draft: live prerequisites, no cycles, every skill in a box.

Usage: python3 skilltree/validate_graph.py [skills.json] [collections.json]
Exit 0 when the graph is usable. Exit 1 on a structural error.
"""
import json
import os
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    skills_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "ee105_skills_draft.json")
    boxes_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "collections.json")
    skills = json.load(open(skills_path, encoding="utf-8"))["skills"]
    boxes = json.load(open(boxes_path, encoding="utf-8"))["boxes"]
    by_id = {s["id"]: s for s in skills}
    retired = set(json.load(open(skills_path, encoding="utf-8")).get("retired") or {})
    # retired may be a list of ids or a map
    if isinstance(retired, dict):
        retired = set(retired)
    errors = []

    visiting, visited = set(), set()

    def walk(sid, stack):
        if sid not in by_id:
            errors.append(f"missing skill {sid}")
            return
        if sid in visited:
            return
        if sid in visiting:
            errors.append("cycle: " + " -> ".join(stack + [sid]))
            return
        visiting.add(sid)
        for pre in by_id[sid].get("prereqs") or []:
            if pre in retired:
                errors.append(f"{sid} prerequisite {pre} is retired")
            elif pre not in by_id:
                errors.append(f"{sid} prerequisite {pre} does not resolve")
            else:
                walk(pre, stack + [sid])
        visiting.discard(sid)
        visited.add(sid)

    for skill in skills:
        walk(skill["id"], [])
    if len(visited) != len(skills):
        errors.append(f"visited {len(visited)} of {len(skills)} skills")

    box_by_id = {b["id"]: b for b in boxes}
    listed = set()
    for box in boxes:
        for sid in box.get("skills") or []:
            if sid not in by_id:
                errors.append(f"{box['id']} lists unknown skill {sid}")
            elif sid in retired:
                errors.append(f"{box['id']} lists retired skill {sid}")
            else:
                listed.add(sid)
        for child in box.get("children") or []:
            if child not in box_by_id:
                errors.append(f"{box['id']} child {child} does not resolve")
    for sid in by_id:
        if sid not in listed:
            errors.append(f"{sid} is not in any box")

    child_ids = {c for b in boxes for c in (b.get("children") or [])}
    tops = [b for b in boxes if b["id"] not in child_ids]

    def members(box):
        out = set(box.get("skills") or [])
        for child in box.get("children") or []:
            out |= members(box_by_id[child])
        return out

    covered = set()
    for top in tops:
        covered |= members(top)
    for sid in by_id:
        if sid not in covered:
            errors.append(f"{sid} is not inside a top-level box")

    if errors:
        print(f"graph: {len(errors)} error(s)")
        for e in errors[:40]:
            print("ERROR", e)
        return 1
    print(f"graph ok: {len(skills)} skills, acyclic, every skill in a top-level box")
    return 0


if __name__ == "__main__":
    sys.exit(main())
