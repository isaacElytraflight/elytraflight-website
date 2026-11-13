#!/usr/bin/env python3
"""Cross-skill duplicate check for learner-facing text.

Finds contiguous word runs of at least 8 words that appear in two different
skills. Question stems, choices, ordering steps, find-the-error reasons,
explanations, and explainer passages are all compared. An 8-gram on the
verbatim allowlist is not a match.

This is an audit tool. It does not edit content. Do not commit its raw log.

Usage:
  python3 tools/skilltree-content/internal_dup.py \
      --allowlist tools/skilltree-content/verbatim_allowlist.txt \
      --min-run 8
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verbatim_gate import load_allow, normalize, shingles

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK = os.path.join(ROOT, "skilltree", "bank")
EXP = os.path.join(ROOT, "skilltree", "explainers")


def skill_of(item_id):
    if item_id.endswith("#explainer"):
        return item_id[: -len("#explainer")]
    # question ids are <skill>-r<round>-q<n>
    mark = item_id.rfind("-r")
    if mark > 0 and item_id[mark + 2:mark + 3].isdigit():
        return item_id[:mark]
    return item_id


def load_items():
    items = []
    for name in sorted(os.listdir(BANK)):
        if not name.endswith(".json"):
            continue
        bank = json.load(open(os.path.join(BANK, name), encoding="utf-8"))
        sid = bank.get("skill_id") or name[:-5]
        for q in bank.get("questions") or []:
            parts = [q.get("prompt") or ""]
            parts.extend(q.get("options") or [])
            parts.extend(q.get("steps") or [])
            parts.extend(q.get("reasons") or [])
            parts.append(q.get("explanation") or "")
            if q.get("figure_alt"):
                parts.append(q["figure_alt"])
            items.append((q["id"], sid, "\n".join(parts)))
        exp_path = os.path.join(EXP, sid + ".json")
        if os.path.isfile(exp_path):
            exp = json.load(open(exp_path, encoding="utf-8"))
            body = []
            for sec in exp.get("sections") or []:
                body.append(sec.get("heading") or "")
                body.append(sec.get("body_md") or "")
                if sec.get("figure_alt"):
                    body.append(sec["figure_alt"])
            items.append((sid + "#explainer", sid, "\n".join(body)))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allowlist", default="")
    ap.add_argument("--min-run", type=int, default=8)
    ap.add_argument("--show", type=int, default=80)
    args = ap.parse_args()
    allow = load_allow(args.allowlist)
    allow8 = {g for g in allow if len(g) == 8}

    items = load_items()
    words = []
    for item_id, sid, text in items:
        words.append(normalize(text))

    # gram -> list of (item_index, position)
    index = {}
    for i, toks in enumerate(words):
        for pos, gram in enumerate(shingles(toks, 8)):
            if gram in allow8:
                continue
            index.setdefault(gram, []).append((i, pos))

    # (i, j, start_i, start_j) -> run length in words, only at the start of a run
    best = {}
    for gram, hits in index.items():
        if len(hits) < 2:
            continue
        for a in range(len(hits)):
            i, pi = hits[a]
            for b in range(a + 1, len(hits)):
                j, pj = hits[b]
                if items[i][1] == items[j][1]:
                    continue
                # start of a run: previous words differ or are at the edge
                if pi > 0 and pj > 0 and words[i][pi - 1] == words[j][pj - 1]:
                    continue
                k = 0
                while (
                    pi + k < len(words[i])
                    and pj + k < len(words[j])
                    and words[i][pi + k] == words[j][pj + k]
                ):
                    k += 1
                if k >= args.min_run:
                    key = (i, j, pi, pj) if i < j else (j, i, pj, pi)
                    prev = best.get(key, 0)
                    if k > prev:
                        best[key] = k

    runs = sorted(best.items(), key=lambda kv: (-kv[1], items[kv[0][0]][0], items[kv[0][1]][0]))
    by_len = {}
    for (_key, length) in runs:
        by_len[length] = by_len.get(length, 0) + 1
    print(f"items={len(items)} shared_runs={len(runs)} min_run={args.min_run}")
    if by_len:
        print("run_lengths: " + ", ".join(f"{n}:{by_len[n]}" for n in sorted(by_len)))
    print("")
    shown = 0
    for (i, j, pi, pj), length in runs:
        if shown >= args.show:
            break
        phrase = " ".join(words[i][pi:pi + length])
        if len(phrase) > 240:
            phrase = phrase[:240] + "..."
        print(f"RUN {length} {items[i][0]}  <>  {items[j][0]}")
        print(f"    {phrase}")
        shown += 1
    if len(runs) > shown:
        print(f"... {len(runs) - shown} more runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
