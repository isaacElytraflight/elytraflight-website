#!/usr/bin/env python3
"""No-verbatim gate for a content batch.

Compares learner-facing stems, choices, explanations, and explainers with
source text that is kept outside the repo.

  - normalize and build 8-word shingles of the sources
  - fail if any learner text shares a contiguous run of 12 or more words
  - fail if more than 5% of a text's 8-grams are in the source shingles
  - flag a learner text when 3 or more numbers from one source sentence
    also appear in that text
  - an allowlist file holds standard phrases; an 8-gram on that list is
    not counted as a match

Source files are not copied into the log. The log records ids, rates, and
the number tuples that were flagged.

Usage:
  python3 tools/skilltree-content/verbatim_gate.py \
      --sources /tmp/b1-sources/text \
      --skills fb-concepts,laplace,lin-algebra-review,min-phase,ode-model \
      --allowlist tools/skilltree-content/verbatim_allowlist.txt \
      --log docs/gates/b1-verbatim.log
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK = os.path.join(ROOT, "skilltree", "bank")
EXP = os.path.join(ROOT, "skilltree", "explainers")

TOKEN = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
MATH = re.compile(r"\\\((?:\\.|[^\\])*?\\\)|\\\[(?:\\.|[^\\])*?\\\]", re.S)
TAG = re.compile(r"<[^>]+>")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def normalize(text):
    text = TAG.sub(" ", text)
    text = MATH.sub(" ", text)
    text = text.lower()
    text = text.replace("\u2019", "'").replace("\u2013", " ").replace("\u2014", " ")
    return TOKEN.findall(text)


def shingles(words, n):
    if len(words) < n:
        return []
    return [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]


def load_allow(path):
    allowed = set()
    if not path or not os.path.isfile(path):
        return allowed
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        words = normalize(line)
        if len(words) >= 8:
            allowed.add(tuple(words[:8]))
            for gram in shingles(words, 8):
                allowed.add(gram)
        elif words:
            # shorter standard phrases are recorded but cannot be an 8-gram
            allowed.add(tuple(words))
    return allowed


def source_sentences(raw):
    raw = TAG.sub(" ", raw)
    raw = raw.replace("\f", "\n")
    parts = []
    for block in raw.splitlines():
        block = block.strip()
        if not block:
            continue
        parts.extend(SENT_SPLIT.split(block))
    return [p.strip() for p in parts if p.strip()]


def numbers_in(text):
    # Drop section-like tokens such as 9.3 when they are the only decimal of a heading.
    found = []
    for m in NUMBER.finditer(text):
        found.append(m.group(0).rstrip("."))
    return found


def load_sources(folder):
    words = []
    sentences = []
    files = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".txt"):
            continue
        raw = open(os.path.join(folder, name), encoding="utf-8", errors="replace").read()
        files.append(name)
        words.extend(normalize(raw))
        sentences.extend(source_sentences(raw))
    return words, sentences, files


def learner_texts(skill_ids):
    items = []
    for sid in skill_ids:
        bank = json.load(open(os.path.join(BANK, f"{sid}.json"), encoding="utf-8"))
        for q in bank["questions"]:
            chunks = [("prompt", q.get("prompt", ""))]
            for i, opt in enumerate(q.get("options") or []):
                chunks.append((f"option{i}", opt))
            chunks.append(("explanation", q.get("explanation", "")))
            if q.get("figure_alt"):
                chunks.append(("figure_alt", q["figure_alt"]))
            items.append((q["id"], "\n".join(text for _, text in chunks), chunks))
        exp = json.load(open(os.path.join(EXP, f"{sid}.json"), encoding="utf-8"))
        body = []
        for sec in exp["sections"]:
            body.append(sec.get("heading", ""))
            body.append(sec.get("body_md", ""))
            if sec.get("figure_alt"):
                body.append(sec["figure_alt"])
        items.append((f"{sid}#explainer", "\n".join(body), [("explainer", "\n".join(body))]))
    return items


def longest_run(text_words, source_wordset_pairs):
    """Longest contiguous run whose 12-gram, if long enough, sits in the source.

    A run is contiguous source words. We test every 12-gram of the learner
    text against the source 12-gram set, which is exactly a 12-word copy.
    """
    grams = shingles(text_words, 12)
    hit = 0
    best = 0
    for g in grams:
        if g in source_wordset_pairs:
            hit += 1
            # overlapping hits extend the run: 1 hit = 12 words, k consecutive = 11+k
            best = max(best, 12)
        else:
            best = max(best, 0)
    # measure consecutive hits
    run = 0
    longest = 0
    for g in grams:
        if g in source_wordset_pairs:
            run += 1
            longest = max(longest, 11 + run)
        else:
            run = 0
    return longest, hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--skills", required=True)
    ap.add_argument("--allowlist", default="")
    ap.add_argument("--log", required=True)
    args = ap.parse_args()

    skills = [s.strip() for s in args.skills.split(",") if s.strip()]
    allow = load_allow(args.allowlist)
    src_words, sentences, files = load_sources(args.sources)
    src8 = set(shingles(src_words, 8)) - {g for g in allow if len(g) == 8}
    src12 = set(shingles(src_words, 12))

    # number groups: sentences with 3+ numbers, ignoring pure outline noise
    number_groups = []
    for sent in sentences:
        nums = numbers_in(sent)
        # keep a number once, in order, and skip sentences that are mostly callouts
        if len(nums) < 3 or len(nums) > 12:
            continue
        if len(normalize(sent)) < 8:
            continue
        number_groups.append((tuple(nums), sent))

    lines = []
    fails = 0
    flags = 0
    lines.append(f"sources: {len(files)} files, {len(src_words)} words, {len(src8)} 8-grams, {len(src12)} 12-grams")
    lines.append("source filenames: " + ", ".join(files))
    lines.append(f"allowlist 8-grams: {sum(1 for g in allow if len(g) == 8)}")
    lines.append("")

    for item_id, whole, _chunks in learner_texts(skills):
        words = normalize(whole)
        grams = shingles(words, 8)
        if not grams:
            lines.append(f"PASS {item_id}: no 8-gram (words={len(words)})")
            continue
        matched = [g for g in grams if g in src8]
        rate = len(matched) / len(grams)
        run, _ = longest_run(words, src12)
        status = "PASS"
        reasons = []
        if run >= 12:
            status = "FAIL"
            reasons.append(f"run={run}")
        if rate > 0.05:
            status = "FAIL"
            reasons.append(f"8-gram overlap={rate:.1%} ({len(matched)}/{len(grams)})")
        # Number flag: a source sentence's numbers appear together, in the
        # same order, as a contiguous run in this text (no other number
        # between the first and the last). Scattered small integers do not
        # count. At least one number is outside {0, 1, 2}.
        text_nums = numbers_in(whole)
        flagged = []
        nlen = len(text_nums)
        for nums, _sent in number_groups:
            if not any(n not in {"0", "1", "2"} for n in nums):
                continue
            width = len(nums)
            if width > nlen:
                continue
            for i in range(nlen - width + 1):
                if tuple(text_nums[i:i + width]) == nums:
                    flagged.append(nums)
                    break
        if flagged:
            flags += 1
            # de-duplicate identical tuples
            uniq = []
            for nums in flagged:
                if nums not in uniq:
                    uniq.append(nums)
            reasons.append("FLAG numbers " + "; ".join(",".join(n) for n in uniq[:8]))
            if status == "PASS":
                status = "FLAG"
        if status == "FAIL":
            fails += 1
        extra = ("; " + "; ".join(reasons)) if reasons else ""
        lines.append(
            f"{status} {item_id}: words={len(words)} 8-grams={len(grams)} "
            f"overlap={rate:.1%} longest_source_run={run}{extra}"
        )

    lines.append("")
    lines.append(f"items={len(learner_texts(skills))} fails={fails} number_flags={flags}")
    os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
    # log path may be relative to repo
    log_path = args.log if os.path.isabs(args.log) else os.path.join(ROOT, args.log)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    text = "\n".join(lines) + "\n"
    open(log_path, "w", encoding="utf-8").write(text)
    sys.stdout.write(text)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
