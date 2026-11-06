#!/usr/bin/env python3
"""Warn when SVG geometry falls outside the viewBox.

Checks circles (including radius), line endpoints, rectangle corners, polyline
and polygon points, text anchors, and path commands (including arc bulge).
A hit is a warning. The process exits 1 only when a requested skill has one.

Usage:
  python3 skilltree/figure_bounds.py [--skills a,b] [bank_dir]
"""
import json
import math
import os
import re
import sys
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

def geometry_message(root):
    """Return a short warning, or None when the drawing stays inside the viewBox."""
    raw = root.attrib.get("viewBox")
    if not raw:
        return
    parts = _svg_nums(raw)
    if len(parts) != 4:
        return f"figure viewBox is not four numbers: {raw}"
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
        return f"figure geometry could not be checked: {e}"
    if not hits:
        return None
    def overrun(hit):
        _tag, x, y = hit
        dx = 0 if minx <= x <= maxx else min(abs(x - minx), abs(x - maxx))
        dy = 0 if miny <= y <= maxy else min(abs(y - miny), abs(y - maxy))
        return dx + dy
    tag, x, y = max(hits, key=overrun)
    extra = f" (+{len(hits) - 1} more)" if len(hits) > 1 else ""
    return f"figure {tag} outside viewBox at ({x:.1f}, {y:.1f}){extra}; viewBox {minx:g} {miny:g} {vw:g} {vh:g}"



def scan(bank_dir, skills=None):
    hits = []
    names = sorted(f[:-5] for f in os.listdir(bank_dir) if f.endswith(".json"))
    if skills:
        names = [n for n in names if n in skills]
    for sid in names:
        path = os.path.join(bank_dir, sid + ".json")
        data = json.load(open(path, encoding="utf-8"))
        for q in data.get("questions") or []:
            fig = q.get("figure")
            if not isinstance(fig, str) or not fig.lstrip().startswith("<svg"):
                continue
            try:
                root = ET.fromstring(fig)
            except ET.ParseError as e:
                hits.append((q.get("id", sid), f"figure is not well-formed XML: {e}"))
                continue
            msg = geometry_message(root)
            if msg:
                hits.append((q.get("id", sid), msg))
    return hits


def _skill_of(qid):
    # question ids are {skill}-r{n}-q{k}; a skill may itself contain hyphens
    if "-r" in qid and "-q" in qid:
        return qid.rsplit("-r", 1)[0]
    return qid


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    fail_skills = None
    if "--fail-skills" in argv:
        i = argv.index("--fail-skills")
        fail_skills = {s.strip() for s in argv[i + 1].split(",") if s.strip()}
        del argv[i:i + 2]
    here = os.path.dirname(os.path.abspath(__file__))
    bank = argv[0] if argv else os.path.join(here, "bank")
    hits = scan(bank)
    batch = [h for h in hits if _skill_of(h[0]) in fail_skills] if fail_skills is not None else hits
    elsewhere = sorted({_skill_of(qid) for qid, _msg in hits if fail_skills is not None and _skill_of(qid) not in fail_skills})
    if fail_skills is not None:
        print(f"figure-bounds: {len(hits)} warning(s), {len(batch)} on the batch" + (f"; elsewhere {', '.join(elsewhere)}" if elsewhere else ""))
    else:
        print(f"figure-bounds: {len(hits)} warning(s) on all banks")
    for qid, msg in batch:
        print(f"WARN [{qid}] {msg}")
    return 1 if batch else 0


if __name__ == "__main__":
    sys.exit(main())
