#!/usr/bin/env python3
"""[batch2a copy of validate_bank.py: + figure/figure_alt checks, LaTeX-delimiter balance, VALIDATE_SKILLS env, leaf preview whitelist for mos-cv/mos-fields]
Validate the EE 105 question bank in /workspace/skilltree/bank against ee105_skills_draft.json.
Usage: python3 validate_bank.py [bank_dir] [skills_json]
Exit code 0 = all good."""
import json, os, re, sys, math

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "bank")
SKILLS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "ee105_skills_draft.json")

BATCH = ['lti-def','rc-lpf','cx-exp','sinusoid-resp','impulse-conv','step-resp','freq-char',
         'tf','phasors','direct-h','pole-zero','rlc','bode','ac-power']
# Optional: VALIDATE_SKILLS="a,b,c" checks those skills; VALIDATE_SKILLS=ALL checks every bank/*.json present.
_vs = os.environ.get("VALIDATE_SKILLS", "").strip()
if _vs == "ALL":
    BATCH = sorted(f[:-5] for f in os.listdir(BANK) if f.endswith(".json"))
elif _vs:
    BATCH = [x.strip() for x in _vs.split(",") if x.strip()]

# Skills with NO dependents in the draft DAG: round-4 previews may point to these
# conceptually-later skills instead (they are not DAG descendants; flagged in the report).
LEAF_PREVIEW_ALLOWED = {
    'step-resp': {'octc', 'cs-cap-load', 'slew', 'stability'},
    'freq-char': {'noise-dist', 'opamp-fr', 'fb-errors', 'freq-basics'},
    'rlc':       {'stability', 'freq-basics', 'opamp-fr'},
    'ac-power':  {'slew', 'datasheet', 'op-point'},
    'mos-cv':    {'mos-caps', 'nmos-regions', 'triode', 'mosfet-struct'},
    'mos-fields': {'nmos-regions', 'saturation', 'mos-caps', 'body-effect', 'triode'},
}

errors, warns = [], []
def err(sid, msg): errors.append(f"[{sid}] {msg}")
def warn(sid, msg): warns.append(f"[{sid}] {msg}")

try:
    sk = json.load(open(SKILLS))
except Exception as e:
    print("cannot read skills json:", e); sys.exit(2)
skills = {s['id']: s for s in sk['skills']}

# descendants (skills that have X as a direct or indirect prerequisite)
children = {i: set() for i in skills}
for s in skills.values():
    for p in s['prereqs']:
        children[p].add(s['id'])
def descendants(x):
    out, stack = set(), [x]
    while stack:
        for c in children[stack.pop()]:
            if c not in out:
                out.add(c); stack.append(c)
    return out

ids_seen = set()
n_q = n_mc = n_num = 0
pos_counts = [0]*4
LATEX = re.compile(r"\$")   # '$' math delimiters are not allowed; use \( ... \) and \[ ... \]
def check_delims(qid, field, v):
    # math delimiters must be balanced, non-nested, in order
    toks = re.findall(r"\\\(|\\\)|\\\[|\\\]", v)
    state = None
    for t in toks:
        if t in ("\\(", "\\["):
            if state is not None: err(qid, f"nested/unclosed math delimiter in {field}"); return
            state = t
        else:
            if (state, t) not in (("\\(", "\\)"), ("\\[", "\\]")): err(qid, f"unbalanced math delimiter in {field}"); return
            state = None
    if state is not None: err(qid, f"unclosed math delimiter in {field}")
import xml.etree.ElementTree as ET
def check_figure(qid, q):
    fg = q.get("figure"); alt = q.get("figure_alt")
    if fg is None:
        if alt is not None: err(qid, "figure_alt without figure")
        return
    if not (isinstance(fg, str) and fg.lstrip().startswith("<svg")): err(qid, "figure must be an SVG string starting with <svg"); return
    if not (isinstance(alt, str) and alt.strip()): warn(qid, "figure without figure_alt")
    if len(fg) > 60000: err(qid, "figure too large")
    try: root = ET.fromstring(fg)
    except Exception as e: err(qid, f"figure is not well-formed XML: {e}"); return
    if not root.tag.endswith("svg"): err(qid, "figure root is not <svg>"); return
    if "viewBox" not in root.attrib: err(qid, "figure <svg> needs a viewBox")
    for el in root.iter():
        tag = el.tag.split("}")[-1].lower()
        if tag in ("script", "foreignobject", "image", "iframe", "object", "embed", "use", "a", "style"): err(qid, f"figure contains forbidden <{tag}>")
        for k, v in el.attrib.items():
            kl = k.split("}")[-1].lower()
            if kl.startswith("on"): err(qid, f"figure has event-handler attribute {k}")
            if kl == "href": err(qid, "figure has href")
            if re.search(r"(https?:|//|javascript:|data:|url\()", str(v), re.I): err(qid, f"figure attribute {k} references external/URL content")
LETTER_REF = re.compile(r"\b(option|choice|answer)\s+\(?[A-D]\)?\b|\(\s*[A-D]\s*\)\s*(is|are)|\bchoice\s+[A-D]\b", re.I)

for sid in BATCH:
    path = os.path.join(BANK, f"{sid}.json")
    if not os.path.exists(path):
        err(sid, "file missing"); continue
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        err(sid, f"invalid JSON: {e}"); continue
    if sid not in skills: err(sid, "skill id not in skills JSON")
    if d.get("skill_id") != sid: err(sid, f"skill_id mismatch: {d.get('skill_id')}")
    if d.get("version") != 1: err(sid, f"version should be 1, got {d.get('version')}")
    qs = d.get("questions")
    if not isinstance(qs, list) or len(qs) != 12:
        err(sid, f"expected 12 questions, got {len(qs) if isinstance(qs, list) else 'none'}")
        if not isinstance(qs, list): continue
    per_round = {1: 0, 2: 0, 3: 0, 4: 0}
    expected_ids = {f"{sid}-r{r}-q{k}" for r in range(1, 5) for k in range(1, 4)}
    got_ids = {q.get("id") for q in qs}
    if got_ids != expected_ids:
        err(sid, f"id set mismatch: missing {sorted(expected_ids - got_ids)}, extra {sorted(x for x in got_ids - expected_ids if x)}")
    allowed_prev = descendants(sid) | LEAF_PREVIEW_ALLOWED.get(sid, set())
    for q in qs:
        n_q += 1
        qid = q.get("id", "<no id>")
        if qid in ids_seen: err(sid, f"duplicate id {qid}")
        ids_seen.add(qid)
        r = q.get("round")
        if r not in (1, 2, 3, 4): err(qid, f"bad round {r}"); continue
        per_round[r] += 1
        m = re.fullmatch(rf"{re.escape(sid)}-r(\d)-q(\d)", str(qid))
        if not m or int(m.group(1)) != r: err(qid, "id does not match pattern/round")
        for fld in ("prompt", "explanation"):
            v = q.get(fld)
            if not isinstance(v, str) or not v.strip(): err(qid, f"empty {fld}")
        if isinstance(q.get("explanation"), str) and len(q["explanation"]) < 60:
            warn(qid, "very short explanation")
        for fld in ("prompt", "explanation"):
            v = q.get(fld, "")
            if isinstance(v, str) and LATEX.search(v): err(qid, f"'$' math delimiter in {fld}")
            if isinstance(v, str): check_delims(qid, fld, v)
        if isinstance(q.get("explanation"), str) and LETTER_REF.search(q["explanation"]):
            warn(qid, "explanation may refer to options by letter")
        check_figure(qid, q)
        t = q.get("type")
        if t == "mc":
            n_mc += 1
            o = q.get("options")
            if not (isinstance(o, list) and len(o) == 4 and all(isinstance(x, str) and x.strip() for x in o)):
                err(qid, "mc needs exactly 4 non-empty string options")
            elif len(set(x.strip() for x in o)) != 4:
                err(qid, "mc options are not distinct")
            ci = q.get("correct_index")
            if not (isinstance(ci, int) and not isinstance(ci, bool) and 0 <= ci <= 3):
                err(qid, f"bad correct_index {ci}")
            else:
                pos_counts[ci] += 1
            for bad in ("answer", "unit", "tolerance"):
                if bad in q: err(qid, f"mc has numeric field '{bad}'")
        elif t == "numeric":
            n_num += 1
            a = q.get("answer")
            if not (isinstance(a, (int, float)) and not isinstance(a, bool) and math.isfinite(a)): err(qid, "numeric answer must be a finite number")
            if not (isinstance(q.get("unit"), str)): err(qid, "numeric needs a 'unit' string")
            tol = q.get("tolerance")
            if not (isinstance(tol, (int, float)) and 0 < tol <= 0.25): err(qid, f"bad tolerance {tol}")
            if isinstance(a, (int, float)) and a == 0: err(qid, "answer 0 with relative tolerance is ungradable")
            for bad in ("options", "correct_index"):
                if bad in q: err(qid, f"numeric has mc field '{bad}'")
        else:
            err(qid, f"bad type {t}")
        if r == 4:
            pv = q.get("preview")
            if not (isinstance(pv, list) and pv and all(isinstance(x, str) for x in pv)):
                err(qid, "round 4 needs non-empty 'preview' list")
            else:
                for x in pv:
                    if x not in skills: err(qid, f"preview id '{x}' not in skills JSON")
                    elif x == sid: err(qid, "preview points at the skill itself")
                    elif x not in allowed_prev:
                        err(qid, f"preview '{x}' is not a later skill (no prereq path from {sid})")
                    elif x not in descendants(sid):
                        warn(qid, f"preview '{x}' is a conceptual (non-DAG) follow-on; {sid} has no dependents in the JSON")
        else:
            if "preview" in q: err(qid, "preview only allowed in round 4")
    for r in (1, 2, 3, 4):
        if per_round[r] != 3: err(sid, f"round {r} has {per_round[r]} questions, expected 3")

print(f"Checked {len(BATCH)} skills, {n_q} questions ({n_mc} mc, {n_num} numeric).")
print(f"mc correct_index distribution (0..3): {pos_counts}")
seen_w = {}
for w in warns:
    seen_w[w] = 1
for w in seen_w: print("WARN ", w)
if errors:
    for e in errors: print("ERROR", e)
    print(f"FAILED with {len(errors)} error(s)")
    sys.exit(1)
print("OK: all checks passed" + (f" ({len(warns)} warning(s))" if warns else ""))
