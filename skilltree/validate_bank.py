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
_NUM = re.compile(r"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?")
_PATH_TOK = re.compile(r"[AaCcHhLlMmQqSsTtVvZz]|" + _NUM.pattern)

def _svg_nums(s):
    return [float(n) for n in _NUM.findall(s or "")]

def _arc_points(x1, y1, rx, ry, phi_deg, large, sweep, x2, y2):
    """Sample an SVG elliptical arc, including the bulge between the endpoints."""
    if math.hypot(x2 - x1, y2 - y1) < 1e-9 or rx == 0 or ry == 0:
        return [(x2, y2)]
    phi = math.radians(phi_deg % 360.0)
    rx, ry = abs(rx), abs(ry)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cos_p * dx + sin_p * dy
    y1p = -sin_p * dx + cos_p * dy
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        scale = math.sqrt(lam)
        rx *= scale
        ry *= scale
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) if den > 0 else 0.0
    if bool(large) == bool(sweep):
        coef = -coef
    cxp = coef * rx * y1p / ry
    cyp = -coef * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x1 + x2) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (y1 + y2) / 2.0

    def angle(ux, uy, vx, vy):
        dot = ux * vx + uy * vy
        norm = math.hypot(ux, uy) * math.hypot(vx, vy)
        if norm < 1e-12:
            return 0.0
        a = max(-1.0, min(1.0, dot / norm))
        return math.copysign(math.acos(a), ux * vy - uy * vx)

    theta1 = angle(1.0, 0.0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dtheta = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if sweep == 0 and dtheta > 0:
        dtheta -= 2 * math.pi
    elif sweep == 1 and dtheta < 0:
        dtheta += 2 * math.pi
    steps = max(8, int(abs(dtheta) / (math.pi / 12)) + 1)
    pts = []
    for i in range(steps + 1):
        th = theta1 + dtheta * i / steps
        pts.append((
            cx + rx * math.cos(th) * cos_p - ry * math.sin(th) * sin_p,
            cy + rx * math.cos(th) * sin_p + ry * math.sin(th) * cos_p,
        ))
    return pts

def _path_points(d):
    toks = _PATH_TOK.findall(d or "")
    i = 0
    cmd = None
    cx = cy = sx = sy = 0.0
    pts = []

    def is_cmd(t):
        return len(t) == 1 and t.isalpha()

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        if is_cmd(toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in ("Z", "z"):
                cx, cy = sx, sy
                pts.append((cx, cy))
                cmd = None
                continue
        if cmd is None:
            break
        rel = cmd.islower()
        op = cmd.upper()
        if op == "M":
            x, y = num(), num()
            if rel:
                x += cx
                y += cy
            cx, cy = sx, sy = x, y
            pts.append((cx, cy))
            cmd = "l" if rel else "L"
        elif op == "L":
            x, y = num(), num()
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            pts.append((cx, cy))
        elif op == "H":
            x = num()
            cx = x + cx if rel else x
            pts.append((cx, cy))
        elif op == "V":
            y = num()
            cy = y + cy if rel else y
            pts.append((cx, cy))
        elif op == "C":
            args = [num() for _ in range(6)]
            if rel:
                args = [args[k] + (cx if k % 2 == 0 else cy) for k in range(6)]
            pts.extend([(args[0], args[1]), (args[2], args[3]), (args[4], args[5])])
            cx, cy = args[4], args[5]
        elif op in ("S", "Q"):
            args = [num() for _ in range(4)]
            if rel:
                args = [args[k] + (cx if k % 2 == 0 else cy) for k in range(4)]
            pts.extend([(args[0], args[1]), (args[2], args[3])])
            cx, cy = args[2], args[3]
        elif op == "T":
            x, y = num(), num()
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            pts.append((cx, cy))
        elif op == "A":
            rx, ry, phi = num(), num(), num()
            large, sweep = int(num()), int(num())
            x, y = num(), num()
            if rel:
                x += cx
                y += cy
            pts.extend(_arc_points(cx, cy, rx, ry, phi, large, sweep, x, y))
            cx, cy = x, y
        else:
            break
    return pts

def check_figure_geometry(qid, root):
    """Warn when drawn geometry falls outside the viewBox. A warning does not fail the bank."""
    raw = root.attrib.get("viewBox")
    if not raw:
        return
    parts = _svg_nums(raw)
    if len(parts) != 4:
        warn(qid, f"figure viewBox is not four numbers: {raw}")
        return
    minx, miny, vw, vh = parts
    maxx, maxy = minx + vw, miny + vh
    eps = 0.51
    hits = []

    def consider(tag, x, y):
        if x < minx - eps or x > maxx + eps or y < miny - eps or y > maxy + eps:
            hits.append((tag, x, y))

    try:
        for el in root.iter():
            tag = el.tag.split("}")[-1].lower()
            a = el.attrib
            if tag == "line":
                consider(tag, float(a.get("x1", 0)), float(a.get("y1", 0)))
                consider(tag, float(a.get("x2", 0)), float(a.get("y2", 0)))
            elif tag == "circle":
                cx, cy, r = float(a.get("cx", 0)), float(a.get("cy", 0)), float(a.get("r", 0))
                consider(tag, cx - r, cy)
                consider(tag, cx + r, cy)
                consider(tag, cx, cy - r)
                consider(tag, cx, cy + r)
            elif tag == "ellipse":
                cx, cy = float(a.get("cx", 0)), float(a.get("cy", 0))
                rx, ry = float(a.get("rx", 0)), float(a.get("ry", 0))
                consider(tag, cx - rx, cy)
                consider(tag, cx + rx, cy)
                consider(tag, cx, cy - ry)
                consider(tag, cx, cy + ry)
            elif tag == "rect":
                x, y = float(a.get("x", 0)), float(a.get("y", 0))
                w, h = float(a.get("width", 0)), float(a.get("height", 0))
                consider(tag, x, y)
                consider(tag, x + w, y + h)
            elif tag in ("polyline", "polygon"):
                nums = _svg_nums(a.get("points", ""))
                for x, y in zip(nums[0::2], nums[1::2]):
                    consider(tag, x, y)
            elif tag == "text":
                xs, ys = _svg_nums(a.get("x", "")), _svg_nums(a.get("y", ""))
                if xs and ys:
                    for x, y in zip(xs, ys):
                        consider(tag, x, y)
            elif tag == "path":
                for x, y in _path_points(a.get("d", "")):
                    consider(tag, x, y)
    except (ValueError, IndexError, ZeroDivisionError) as e:
        warn(qid, f"figure geometry could not be checked: {e}")
        return
    if not hits:
        return
    def overrun(hit):
        _tag, x, y = hit
        dx = 0 if minx <= x <= maxx else min(abs(x - minx), abs(x - maxx))
        dy = 0 if miny <= y <= maxy else min(abs(y - miny), abs(y - maxy))
        return dx + dy
    tag, x, y = max(hits, key=overrun)
    extra = f" (+{len(hits) - 1} more)" if len(hits) > 1 else ""
    warn(qid, f"figure {tag} outside viewBox at ({x:.1f}, {y:.1f}){extra}; viewBox {minx:g} {miny:g} {vw:g} {vh:g}")

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
    else: check_figure_geometry(qid, root)
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
