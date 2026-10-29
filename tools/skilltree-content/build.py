#!/usr/bin/env python3
"""
Build script for Skillgrove multi-file app.

Reads:
  - skilltree/ee105_skills_draft.json (skill graph)
  - skilltree/bank/*.json (question banks)

Outputs to public/skilltree/:
  - skills.json (graph + metadata for simulator, loaded at startup)
  - banks/<skill-id>.<hash>.json (individual bank files, lazy loaded)
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

def sha256_short(data: bytes, length: int = 8) -> str:
    return hashlib.sha256(data).hexdigest()[:length]

def normalize_bank_question(q: dict) -> dict:
    """Keep only the fields needed for the app."""
    keep = ("id", "round", "type", "prompt", "options", "correct_index",
            "answer", "unit", "tolerance", "explanation", "preview", "figure", "figure_alt")
    return {k: q[k] for k in keep if k in q}

def main():
    skills_file = SRC / "ee105_skills_draft.json"
    bank_dir = SRC / "bank"
    
    if not skills_file.exists():
        print(f"Error: {skills_file} not found", file=sys.stderr)
        sys.exit(1)
    
    data = json.loads(skills_file.read_text(encoding="utf-8"))
    skills = data["skills"]
    skill_ids = {s["id"] for s in skills}
    
    BANKS_OUT.mkdir(parents=True, exist_ok=True)
    
    banks_meta = {}  # skill_id -> {version, questionCount, hash, file}
    playable_ids = []
    
    for bank_file in sorted(bank_dir.glob("*.json")):
        bank = json.loads(bank_file.read_text(encoding="utf-8"))
        sid = bank["skill_id"]
        
        if sid not in skill_ids:
            print(f"Warning: bank {bank_file.name} for unknown skill {sid}; skipped", file=sys.stderr)
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
    
    skills_out = {
        "course": data.get("course", "EE 105"),
        "source": data.get("source", ""),
        "version": data.get("version"),
        "chapters": data["chapters"],
        "skills": [
            {k: s[k] for k in ("id", "name", "chapter", "reader_section", "prereqs")}
            for s in skills
        ],
        "banks": banks_meta,
        "playable": sorted(playable_ids),
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
        "banks": banks_meta,
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    total_bank_size = sum((BANKS_OUT / f"{sid}.{m['hash']}.json").stat().st_size for sid, m in banks_meta.items())
    print(f"Built to {OUT}:")
    print(f"  - {skills_filename}: {len(skills_bytes):,} bytes ({len(skills)} skills, {len(playable_ids)} playable)")
    print(f"  - {len(banks_meta)} bank files: {total_bank_size:,} bytes total")
    print(f"  - manifest.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
