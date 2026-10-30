#!/usr/bin/env python3
"""
Build script for Skillgrove multi-file app.

Reads:
  - skilltree/ee105_skills_draft.json (skill graph)
  - skilltree/collections.json (box/collection hierarchy)
  - skilltree/bank/*.json (question banks)
  - skilltree/explainers/*.json (skill explainers)

Outputs to public/skilltree/:
  - skills.json (graph + metadata for simulator, loaded at startup)
  - collections.<hash>.json (box hierarchy, loaded at startup)
  - banks/<skill-id>.<hash>.json (individual bank files, lazy loaded)
  - explainers/<skill-id>.<hash>.json (individual explainer files, lazy loaded)
  - manifest.json (content hashes for cache busting)
"""
import json
import hashlib
import os
import sys
import shutil
from pathlib import Path

REPO = Path(__file__).parent.parent.parent
SRC = REPO / "skilltree"
OUT = REPO / "public" / "skilltree"
BANKS_OUT = OUT / "banks"
EXPLAINERS_OUT = OUT / "explainers"

def sha256_short(data: bytes, length: int = 8) -> str:
    return hashlib.sha256(data).hexdigest()[:length]

def normalize_bank_question(q: dict) -> dict:
    """Keep only the fields needed for the app."""
    keep = ("id", "round", "type", "prompt", "options", "correct_index",
            "answer", "unit", "tolerance", "explanation", "preview", "figure", "figure_alt")
    return {k: q[k] for k in keep if k in q}

def clear_stale_outputs():
    """Drop previously hashed content so retired banks are not still served."""
    BANKS_OUT.mkdir(parents=True, exist_ok=True)
    EXPLAINERS_OUT.mkdir(parents=True, exist_ok=True)
    for folder in (BANKS_OUT, EXPLAINERS_OUT):
        for path in folder.glob("*.json"):
            path.unlink()
    for pattern in ("skills.*.json", "collections.*.json"):
        for path in OUT.glob(pattern):
            path.unlink()

def main():
    skills_file = SRC / "ee105_skills_draft.json"
    bank_dir = SRC / "bank"
    
    if not skills_file.exists():
        print(f"Error: {skills_file} not found", file=sys.stderr)
        sys.exit(1)
    
    data = json.loads(skills_file.read_text(encoding="utf-8"))
    skills = data["skills"]
    skill_ids = {s["id"] for s in skills}
    retired = data.get("retired") or {}
    if not isinstance(retired, dict):
        print("Error: retired must be an object of {oldId: survivorId}", file=sys.stderr)
        sys.exit(1)
    errors = 0
    for old_id, survivor_id in retired.items():
        if old_id in skill_ids:
            print(f"Error: retired id {old_id} is still a live skill", file=sys.stderr)
            errors += 1
        if survivor_id not in skill_ids:
            print(f"Error: retired id {old_id} maps to unknown skill {survivor_id}", file=sys.stderr)
            errors += 1
    for skill in skills:
        for prereq in skill.get("prereqs") or []:
            if prereq not in skill_ids or prereq in retired:
                print(f"Error: skill {skill['id']} has unresolved prerequisite {prereq}", file=sys.stderr)
                errors += 1
    if errors:
        sys.exit(1)

    clear_stale_outputs()
    
    banks_meta = {}  # skill_id -> {version, questionCount, hash, file}
    explainers_meta = {}  # skill_id -> {hash, file, sectionCount}
    playable_ids = []
    
    for bank_file in sorted(bank_dir.glob("*.json")):
        bank = json.loads(bank_file.read_text(encoding="utf-8"))
        sid = bank["skill_id"]
        
        if sid not in skill_ids or sid in retired:
            print(f"Error: bank {bank_file.name} for unknown or retired skill {sid}", file=sys.stderr)
            errors += 1
            continue
        
        questions = [normalize_bank_question(q) for q in bank["questions"]]
        
        for q in questions:
            assert q["type"] in ("mc", "numeric"), f"{q['id']}: invalid type"
            assert q["round"] in (1, 2, 3, 4), f"{q['id']}: invalid round"
            if q["type"] == "mc":
                assert len(q.get("options", [])) >= 2, f"{q['id']}: mc needs options"
                assert 0 <= q.get("correct_index", -1) < len(q["options"]), f"{q['id']}: invalid correct_index"
            else:
                assert isinstance(q.get("answer"), (int, float)), f"{q['id']}: numeric needs answer"
        
        bank_data = {
            "skill_id": sid,
            "version": bank.get("version", 1),
            "questions": questions
        }
        
        bank_json = json.dumps(bank_data, ensure_ascii=False, separators=(",", ":"))
        bank_bytes = bank_json.encode("utf-8")
        content_hash = sha256_short(bank_bytes)
        
        out_name = f"{sid}.{content_hash}.json"
        (BANKS_OUT / out_name).write_bytes(bank_bytes)
        
        round_counts = {}
        for q in questions:
            r = q["round"]
            round_counts[r] = round_counts.get(r, 0) + 1
        
        banks_meta[sid] = {
            "version": bank_data["version"],
            "questionCount": len(questions),
            "rounds": round_counts,
            "hash": content_hash,
            "file": f"banks/{out_name}"
        }
        
        if round_counts.get(1, 0) > 0:
            playable_ids.append(sid)
    
    # Process explainers
    explainer_dir = SRC / "explainers"
    if explainer_dir.exists():
        for explainer_file in sorted(explainer_dir.glob("*.json")):
            explainer = json.loads(explainer_file.read_text(encoding="utf-8"))
            sid = explainer["id"]
            
            if sid not in skill_ids or sid in retired:
                print(f"Error: explainer {explainer_file.name} for unknown or retired skill {sid}", file=sys.stderr)
                errors += 1
                continue
            
            explainer_data = {
                "id": sid,
                "title": explainer.get("title", ""),
                "sections": explainer.get("sections", [])
            }
            
            explainer_json = json.dumps(explainer_data, ensure_ascii=False, separators=(",", ":"))
            explainer_bytes = explainer_json.encode("utf-8")
            content_hash = sha256_short(explainer_bytes)
            
            out_name = f"{sid}.{content_hash}.json"
            (EXPLAINERS_OUT / out_name).write_bytes(explainer_bytes)
            
            explainers_meta[sid] = {
                "hash": content_hash,
                "file": f"explainers/{out_name}",
                "sectionCount": len(explainer_data["sections"])
            }
    
    # Process collections
    collections_file = SRC / "collections.json"
    collections_meta = None
    if collections_file.exists():
        collections_data = json.loads(collections_file.read_text(encoding="utf-8"))
        
        # Validate box references
        box_ids = {b["id"] for b in collections_data["boxes"]}
        for box in collections_data["boxes"]:
            for child_id in box.get("children", []):
                if child_id not in box_ids:
                    print(f"Warning: box {box['id']} references unknown child {child_id}", file=sys.stderr)
            for sid in box.get("skills", []):
                if sid not in skill_ids or sid in retired:
                    print(f"Error: box {box['id']} references unknown or retired skill {sid}", file=sys.stderr)
                    errors += 1
        
        collections_json = json.dumps(collections_data, ensure_ascii=False, separators=(",", ":"))
        collections_bytes = collections_json.encode("utf-8")
        collections_hash = sha256_short(collections_bytes)
        collections_filename = f"collections.{collections_hash}.json"
        (OUT / collections_filename).write_bytes(collections_bytes)
        
        collections_meta = {
            "file": collections_filename,
            "hash": collections_hash,
            "boxCount": len(collections_data["boxes"])
        }
    
    def public_skill(s):
        out = {"id": s["id"], "name": s["name"], "prereqs": s.get("prereqs") or []}
        if s.get("chapter") is not None:
            out["chapter"] = s["chapter"]
        if s.get("reader_section"):
            out["reader_section"] = s["reader_section"]
        if s.get("summary"):
            out["summary"] = s["summary"]
        if s.get("sources"):
            out["sources"] = s["sources"]
        if s.get("status"):
            out["status"] = s["status"]
        return out

    skills_out = {
        "course": data.get("course", "EE 105"),
        "source": data.get("source", ""),
        "version": data.get("version"),
        "chapters": data.get("chapters") or {},
        "skills": [public_skill(s) for s in skills],
        "banks": banks_meta,
        "explainers": explainers_meta,
        "playable": sorted(playable_ids),
        "retired": retired,
    }
    
    skills_json = json.dumps(skills_out, ensure_ascii=False, separators=(",", ":"))
    skills_bytes = skills_json.encode("utf-8")
    skills_hash = sha256_short(skills_bytes)
    skills_filename = f"skills.{skills_hash}.json"
    (OUT / skills_filename).write_bytes(skills_bytes)
    
    manifest = {
        "version": 1,
        "generated": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "skills": {
            "file": skills_filename,
            "hash": skills_hash,
        },
        "collections": collections_meta,
        "banks": banks_meta,
        "explainers": explainers_meta,
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    total_bank_size = sum((BANKS_OUT / f"{sid}.{m['hash']}.json").stat().st_size for sid, m in banks_meta.items())
    total_explainer_size = sum((EXPLAINERS_OUT / f"{sid}.{m['hash']}.json").stat().st_size for sid, m in explainers_meta.items()) if explainers_meta else 0
    print(f"Built to {OUT}:")
    print(f"  - {skills_filename}: {len(skills_bytes):,} bytes ({len(skills)} skills, {len(playable_ids)} playable)")
    if collections_meta:
        print(f"  - {collections_filename}: {len(collections_bytes):,} bytes ({collections_meta['boxCount']} boxes)")
    print(f"  - {len(banks_meta)} bank files: {total_bank_size:,} bytes total")
    print(f"  - {len(explainers_meta)} explainer files: {total_explainer_size:,} bytes total")
    print(f"  - manifest.json")
    print(f"  - retired map: {len(retired)} ids")
    if errors:
        print(f"Error: {errors} content problem(s)", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
