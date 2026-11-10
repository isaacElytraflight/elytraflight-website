#!/usr/bin/env python3
"""Shared question-bank validator for ALL Skillgrove skill banks (merged from validate_bank.py,
batch2a_validate.py and batch2b_validate.py). Checks schema, ids, round structure, MC option positions,
round-4 preview targets (DAG descendants + LEAF_PREVIEW_ALLOWED from batch2a and batch2b), letter references,
LaTeX math delimiters (\\( \\) / \\[ \\] balanced, no '$'), and figure SVG safety (well-formed, viewBox,
no script/foreignObject/image/use/a/style, no on* handlers, no href/URLs).
Figures whose circles, line endpoints, text anchors, or paths fall outside the viewBox are warnings.
Usage: python3 validate_bank.py [bank_dir] [skills.json];  VALIDATE_SKILLS="a,b" limits the set (default ALL).
Exit code 0 = all good."""
import json, os, re, sys, math
from expr import FUNCS, ExprError, free_names, parse as parse_expr

_d = os.path.dirname(os.path.abspath(__file__))
HERE = _d if os.path.isdir(os.path.join(_d, "bank")) else os.path.dirname(_d)   # works from gen/ or the repo root
BANK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "bank")
SKILLS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "ee105_skills_draft.json")

BATCH = None   # default: every bank/*.json (all 55 skills)
# Optional: VALIDATE_SKILLS="a,b,c" checks those skills; VALIDATE_SKILLS=ALL checks every bank/*.json present.
_vs = os.environ.get("VALIDATE_SKILLS", "ALL").strip() or "ALL"
if _vs == "ALL":
    BATCH = sorted(f[:-5] for f in os.listdir(BANK) if f.endswith(".json"))
elif _vs:
    BATCH = [x.strip() for x in _vs.split(",") if x.strip()]

# Skills with NO dependents in the draft DAG: round-4 previews may point to these
# conceptually-later skills instead (they are not DAG descendants; flagged in the report).
LEAF_PREVIEW_ALLOWED = {
    'step-resp': {'octc', 'cs-cap-load', 'slew', 'stability'},
    'freq-char': {'noise-dist', 'opamp-fr', 'fb-errors', 'freq-basics'},
    'rlc':       {'amp-compensation', 'freq-basics', 'opamp-fr'},
    'ac-power':  {'slew', 'datasheet', 'cs-intro'},
    'mos-cv':    {'mos-caps', 'nmos-regions', 'triode', 'mosfet-struct'},
    'mos-fields': {'nmos-regions', 'square-law', 'mos-caps', 'body-effect', 'triode'},
}
# batch2b leaf/conceptual follow-ons (skills with no DAG dependents, or whose natural follow-on is not a DAG descendant)
# batch v2 (66 remaining EE 105 skills): leaf skills and conceptual follow-ons
LEAF_PREVIEW_ALLOWED.update({
    'ic-fab':     {'mosfet-struct'},
    'sheet-res':  {'mos-caps', 'triode', 'square-law'},
    'solar-cell': {'led', 'diode-ss'},
    'led':        {'diode-ss', 'mos-caps'},
})
LEAF_PREVIEW_ALLOWED.update({
    'bias-coupling': {'freq-basics', 'diff-intro', 'cs-cascade'},
    'bias-current': {'datasheet', 'noise-dist'},
    'datasheet':    {'cmrr', 'ft', 'diff-intro'},
    'stability':    {'miller', 'cs-cap-load', 'ft', 'cmrr'},
    'fb-errors':    {'degeneration', 'cd', 'cs-analysis'},
    'fb-impedance': {'cd', 'degeneration', 'cs-analysis', 'two-port'},
    'inverting':    {'miller', 'cs-analysis', 'degeneration', 'cs-brute'},
    'diode-ss':     {'bjt-ss', 'ss-model', 'mos-caps', 'ft', 'bjt-action'},
})

LEAF_PREVIEW_ALLOWED.update({   # batches 4-9 (post-merge): leaf skills -> conceptual follow-ons
    'pmos':        {'high-load', 'cs-analysis', 'mirror-load', 'cascode-bias'},
    'bjt-ss':      {'cs-analysis', 'ft', 'cd', 'diff-intro'},
    'ft':          {'miller', 'cs-cascade-freq', 'cd-freq', 'octc'},
    'ref-gen':     {'cascode-bias', 'big-circuit', 'offset'},
    'amp-choice':  {'cascode-amp', 'big-circuit', 'cs-cascade'},
    'high-load':   {'cascode-src', 'mirror-load', 'cascode-amp'},
    'cascode-src': {'cascode-amp', 'cascode-bias'},
    'diff-dc':     {'half-circuit', 'cmrr', 'mirror-load'},
    'cg-freq':     {'cascode-amp', 'octc'},
    'mirror-load': {'offset', 'opamp-models', 'gbw'},
    'cd-freq':     {'big-circuit', 'octc'},
    'cs-cascade-freq': {'gbw', 'amp-compensation', 'opamp-fr'},
    'octc':        {'opamp-fr', 'amp-compensation', 'cascode-amp'},
    'cs-cap-load': {'amp-compensation', 'opamp-fr', 'gbw'},
    'cascode-bias': {'opamp-models', 'big-circuit'},
    'big-circuit': {'opamp-models', 'mirror-load', 'noise-dist'},
})

errors, warns = [], []
# v3 application leaves
LEAF_PREVIEW_ALLOWED.update({"lti-circuits": ["cs-cap-load", "octc", "slew"], "freq-resp-circuits": ["noise-dist", "opamp-fr", "two-port"], "bode-circuits": ["freq-basics", "gbw", "rlc"], "fb-amp": ["fb-amp-errors", "fb-impedance", "gbw", "inverting"], "fb-amp-errors": ["cd", "cs-analysis", "degeneration", "opamp-fr"], "amp-compensation": ["cs-cap-load", "miller", "opamp-fr"], "lti-mech": ["cruise-control", "second-order-sys", "sys-id"], "loop-margin-design": ["loop-shaping", "robust-stability", "time-delay"]})
LEAF_PREVIEW_ALLOWED.update({
    # model-method has no dependents. Round 4 names the later modeling skills.
    "model-method": ["linearization", "sys-id", "equilibria"],
})
LEAF_PREVIEW_ALLOWED.update({
    # ME132 B3 skills: leaf skills with conceptual follow-ons
    "app-examples": ["realization", "discrete-time", "linearization"],
    "cruise-control": ["pid-tuning", "feedforward", "gain-scheduling"],
})
LEAF_PREVIEW_ALLOWED.update({
    # ME132 B5 leaves: no dependents in the graph.
    "gen-gain-phase": ["robust-stability", "lyapunov", "adaptive"],
    "pid-impl": ["time-delay", "integral-action", "mpc"],
    "pid-tuning": ["loop-shaping", "gain-scheduling", "robust-perf"],
    "windup": ["integral-action", "mpc", "pid-impl"],
})
LEAF_PREVIEW_ALLOWED.update({
    # ME132 B4 skills: leaf skills with conceptual follow-ons
    "discrete-time": ["freq-resp-lti", "time-delay", "pid-impl"],
    "eig-modes": ["realization", "lin-algebra-review", "observability"],
    "limit-cycles": ["lyapunov", "gen-gain-phase", "adaptive"],
})
LEAF_PREVIEW_ALLOWED.update({
    # Cauchy-Schwarz has no dependents. Round 4 names later uses of the inequality.
    "cauchy-schwarz-inequality": ["induced-matrix-norms", "open-closed-sets", "convergence-rates"],
})
LEAF_PREVIEW_ALLOWED = {k: set(v) for k, v in LEAF_PREVIEW_ALLOWED.items()}
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
n_q = n_mc = n_num = n_sym = n_order = n_errq = n_multi = 0
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
from figure_bounds import geometry_message

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
    else:
        msg = geometry_message(root)
        if msg: warn(qid, msg)
    for el in root.iter():
        tag = el.tag.split("}")[-1].lower()
        if tag in ("script", "foreignobject", "image", "iframe", "object", "embed", "use", "a", "style"): err(qid, f"figure contains forbidden <{tag}>")
        for k, v in el.attrib.items():
            kl = k.split("}")[-1].lower()
            if kl.startswith("on"): err(qid, f"figure has event-handler attribute {k}")
            if kl == "href": err(qid, "figure has href")
            if re.search(r"(https?:|//|javascript:|data:|url\()", str(v), re.I): err(qid, f"figure attribute {k} references external/URL content")
LETTER_REF = re.compile(r"\b(option|choice|answer)\s+\(?[A-D]\)?\b|\(\s*[A-D]\s*\)\s*(is|are)|\bchoice\s+[A-D]\b", re.I)
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
COMMON_FIELDS = {"id", "round", "type", "prompt", "explanation", "figure", "figure_alt", "preview", "version"}
TYPE_FIELDS = {
    "mc": {"options", "correct_index"},
    "numeric": {"answer", "unit", "tolerance"},
    "symbolic": {"answer", "variables", "tolerance", "alternates"},
    "order": {"steps"},
    "error": {"steps", "flaw_index", "reasons", "correct_reason"},
    "multi": {"options", "correct_indices"},
}

def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)

def check_text(qid, field, text):
    if not isinstance(text, str) or not text.strip():
        err(qid, f"empty {field}")
        return False
    if LATEX.search(text):
        err(qid, f"'$' math delimiter in {field}")
    check_delims(qid, field, text)
    return True

def check_string_list(qid, field, values, lo, hi, distinct=True):
    if not (isinstance(values, list) and lo <= len(values) <= hi and all(isinstance(x, str) and x.strip() for x in values)):
        err(qid, f"{field} needs {lo} to {hi} non-empty strings")
        return False
    for i, text in enumerate(values):
        check_text(qid, f"{field}[{i}]", text)
    if distinct and len(set(x.strip() for x in values)) != len(values):
        err(qid, f"{field} entries are not distinct")
    return True

def check_symbolic(qid, q):
    answer = q.get("answer")
    if not (isinstance(answer, str) and answer.strip()):
        err(qid, "symbolic needs a text answer")
        answer = ""
    elif "\\" in answer or "$" in answer:
        err(qid, "symbolic answer must be a plain expression, not TeX")
    specs = q.get("variables")
    names = []
    if not isinstance(specs, list) or not specs:
        err(qid, "symbolic needs a non-empty variables list")
    else:
        for i, spec in enumerate(specs):
            if not isinstance(spec, dict):
                err(qid, f"variables[{i}] must be an object")
                continue
            name = spec.get("name")
            if not (isinstance(name, str) and NAME_RE.fullmatch(name)):
                err(qid, f"variables[{i}] has a bad name")
                continue
            if name in FUNCS:
                err(qid, f"variable {name} is a function name")
            if name in ("e", "E"):
                err(qid, f"variable {name} is reserved for the constant e and for scientific notation")
            if name in names:
                err(qid, f"duplicate variable {name}")
            names.append(name)
            lo, hi = spec.get("min"), spec.get("max")
            if not (isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and not isinstance(lo, bool) and not isinstance(hi, bool) and math.isfinite(lo) and math.isfinite(hi) and lo < hi):
                err(qid, f"variable {name} needs min < max")
    tol = q.get("tolerance")
    if not (isinstance(tol, (int, float)) and not isinstance(tol, bool) and 0 < tol <= 0.25):
        err(qid, f"bad tolerance {tol}")
    alts = q.get("alternates", [])
    if alts is None:
        alts = []
    if not isinstance(alts, list) or not all(isinstance(x, str) and x.strip() for x in alts):
        err(qid, "alternates must be a list of non-empty strings")
        alts = []
    seen = set()
    if isinstance(answer, str):
        seen.add(re.sub(r"\s+", "", answer))
    for alt in alts:
        if "\\" in alt or "$" in alt:
            err(qid, "alternate must be a plain expression, not TeX")
        key = re.sub(r"\s+", "", alt)
        if key in seen:
            err(qid, "alternate repeats the key or another alternate")
        seen.add(key)
    if names and isinstance(answer, str) and answer.strip() and "\\" not in answer and "$" not in answer:
        try:
            ast = parse_expr(answer, names)
        except ExprError as exc:
            err(qid, f"symbolic answer did not parse: {exc}")
        else:
            missing = [name for name in names if name not in free_names(ast)]
            if missing:
                err(qid, "symbolic answer does not use " + ", ".join(missing))
        for alt in alts:
            if "\\" in alt or "$" in alt:
                continue
            try:
                parse_expr(alt, names)
            except ExprError as exc:
                err(qid, f"alternate did not parse: {exc}")

def check_order(qid, q):
    check_string_list(qid, "steps", q.get("steps"), 3, 6)

def check_error(qid, q):
    steps = q.get("steps")
    ok = check_string_list(qid, "steps", steps, 3, 6)
    flaw = q.get("flaw_index")
    if not is_int(flaw):
        err(qid, f"bad flaw_index {flaw}")
    elif ok and not (0 <= flaw < len(steps)):
        err(qid, f"flaw_index {flaw} is outside the steps")
    if "reasons" not in q and "correct_reason" not in q:
        return
    reasons = q.get("reasons")
    if not check_string_list(qid, "reasons", reasons, 2, 5):
        return
    cr = q.get("correct_reason")
    if not (is_int(cr) and 0 <= cr < len(reasons)):
        err(qid, f"bad correct_reason {cr}")

def check_multi(qid, q):
    options = q.get("options")
    if not check_string_list(qid, "options", options, 3, 6):
        return
    idxs = q.get("correct_indices")
    if not (isinstance(idxs, list) and idxs and all(is_int(i) for i in idxs)):
        err(qid, "multi needs a non-empty correct_indices list")
        return
    if len(set(idxs)) != len(idxs):
        err(qid, "correct_indices has duplicates")
    if any(i < 0 or i >= len(options) for i in idxs):
        err(qid, "correct_indices is outside the options")
    if len(idxs) >= len(options):
        err(qid, "multi needs at least one wrong option")

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
    if not (isinstance(d.get("version"), int) and d.get("version") >= 1): err(sid, f"version should be an int >= 1, got {d.get('version')}")
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
        if t not in TYPE_FIELDS:
            err(qid, f"bad type {t}")
        else:
            for extra in sorted(k for k in q if k not in COMMON_FIELDS and k not in TYPE_FIELDS[t]):
                err(qid, f"{t} has unexpected field '{extra}'")
        if t == "mc":
            n_mc += 1
            o = q.get("options")
            if not (isinstance(o, list) and len(o) == 4 and all(isinstance(x, str) and x.strip() for x in o)):
                err(qid, "mc needs exactly 4 non-empty string options")
            elif len(set(x.strip() for x in o)) != 4:
                err(qid, "mc options are not distinct")
            ci = q.get("correct_index")
            if not (is_int(ci) and 0 <= ci <= 3):
                err(qid, f"bad correct_index {ci}")
            else:
                pos_counts[ci] += 1
        elif t == "numeric":
            n_num += 1
            a = q.get("answer")
            if not (isinstance(a, (int, float)) and not isinstance(a, bool) and math.isfinite(a)): err(qid, "numeric answer must be a finite number")
            if not (isinstance(q.get("unit"), str)): err(qid, "numeric needs a 'unit' string")
            tol = q.get("tolerance")
            if not (isinstance(tol, (int, float)) and not isinstance(tol, bool) and 0 < tol <= 0.25): err(qid, f"bad tolerance {tol}")
            if isinstance(a, (int, float)) and not isinstance(a, bool) and a == 0: err(qid, "answer 0 with relative tolerance is ungradable")
        elif t == "symbolic":
            n_sym += 1
            check_symbolic(qid, q)
        elif t == "order":
            n_order += 1
            check_order(qid, q)
        elif t == "error":
            n_errq += 1
            check_error(qid, q)
        elif t == "multi":
            n_multi += 1
            check_multi(qid, q)
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

print(f"Checked {len(BATCH)} skills, {n_q} questions ({n_mc} mc, {n_num} numeric, {n_sym} symbolic, {n_order} order, {n_errq} find-the-error, {n_multi} multi).")
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
