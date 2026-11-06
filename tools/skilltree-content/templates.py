"""Bounds-safe SVG templates for skill figures.

Every template fits its geometry inside the viewBox and checks that with the
figure-bounds scanner before returning. Strokes use currentColor via figlib.

Templates: s-plane, block diagram, mass-spring-damper, matrix, Bode
magnitude/phase, step response, Nyquist, root locus, and a generic plot.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "skilltree"))

from figlib import (
    b2b_arrow, b2b_axes, b2b_box, b2b_circle, b2b_curve, b2b_line, b2b_poly,
    b2b_rect, b2b_svg, b2b_text,
)
from figure_bounds import geometry_message
import xml.etree.ElementTree as ET


def _guard(svg):
    msg = geometry_message(ET.fromstring(svg))
    if msg:
        raise ValueError(msg)
    return svg


def _fit(points, left, right, top, bottom):
    xs = [p[0] for p in points] or [0.0]
    ys = [p[1] for p in points] or [0.0]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax - xmin < 1e-9:
        xmin -= 1.0
        xmax += 1.0
    if ymax - ymin < 1e-9:
        ymin -= 1.0
        ymax += 1.0
    px = 0.08 * (xmax - xmin)
    py = 0.12 * (ymax - ymin)
    xmin -= px
    xmax += px
    ymin -= py
    ymax += py

    def X(x):
        return left + (x - xmin) / (xmax - xmin) * (right - left)

    def Y(y):
        return bottom - (y - ymin) / (ymax - ymin) * (bottom - top)

    return X, Y


def plot(fn, xa, xb, xlabel, ylabel, title, w=340, h=176, zero=False):
    """Generic curve. The y range is taken from the samples and padded into the axes."""
    n = 90
    ys = [fn(xa + (xb - xa) * i / n) for i in range(n + 1)]
    lo, hi = min(ys), max(ys)
    span = hi - lo or 1.0
    lo -= 0.14 * span
    hi += 0.16 * span
    x0, y0 = 46, h - 30
    pw, ph = w - 68, h - 54
    sx = pw / (xb - xa)
    sy = ph / (hi - lo)
    body = b2b_axes(x0, y0, pw, ph, xlabel, ylabel)
    if zero and lo < 0 < hi:
        yz = y0 - sy * (0 - lo)
        body += b2b_line(x0, yz, x0 + pw, yz, dash=True)
    body += b2b_curve(lambda x: fn(x) - lo, xa, xb, x0, y0, sx, sy, n=n, sw=2.2)
    return _guard(b2b_svg(w, h, body, title))


def step_response(title, tau=1.0, goal=1.0, fn=None, t_end=None, zero=False):
    """A step response. Pass fn to draw a different transient; otherwise a first-order rise."""
    if fn is None:
        fn = lambda t, tau=tau, goal=goal: goal * (1 - math.exp(-t / tau))
        t_end = 5 * tau if t_end is None else t_end
    elif t_end is None:
        t_end = 5 * tau
    return plot(fn, 0, t_end, "t", "y", title, zero=zero)


def bode_sketch(title):
    """Qualitative magnitude: one slope, then a steeper one. The trace stays inside the axes."""
    pts = [(58, 42), (150, 86), (268, 142)]
    body = b2b_axes(50, 156, 250, 126, "log \u03c9", "|H| dB")
    body += b2b_poly(pts, sw=2.2)
    body += b2b_text(96, 52, "\u221220", size=11)
    body += b2b_text(188, 96, "\u221240", size=11)
    return _guard(b2b_svg(330, 186, body, title))


def bode(mag, title, phase=None):
    """Bode magnitude and, optionally, phase.

    mag and phase are lists of (frequency, value) in data units. Frequency can
    be linear or logarithmic; the template only auto-fits the numbers it is given.
    """
    w = 340
    # (left, right, top, bottom) in pixels. The frequency label sits 16 px under the axis.
    if phase:
        h = 250
        panes = [(mag, "dB", (54, 300, 28, 108)), (phase, "deg", (54, 300, 148, 220))]
    else:
        h = 186
        panes = [(mag, "dB", (54, 300, 28, 140))]
    body = ""
    for curve, ylabel, (left, right, top, bottom) in panes:
        X, Y = _fit(curve, left, right, top, bottom)
        body += b2b_axes(left, bottom, right - left, bottom - top, "", ylabel)
        body += b2b_poly([(X(x), Y(y)) for x, y in curve], sw=2.2)
        body += b2b_text(right, bottom + 16, "f", anchor="end", size=11)
    return _guard(b2b_svg(w, h, body, title))


def _splane_map(marks, w=300, h=180):
    x0, y0, s = 150.0, 90.0, 22.0

    def outside(x0, y0, s):
        pts = [(20, y0), (280, y0), (x0, 160), (x0, 16), (x0 + 8, 14), (274, y0 + 16)]
        for re, im in marks:
            x, y = x0 + s * re, y0 - s * im
            pts += [(x - 5, y - 5), (x + 5, y + 5), (x - 5, y + 5), (x + 5, y - 5)]
            if abs(im) < 0.2:
                pts += [(x - 14, y), (x + 14, y)]
        return any(px < 0 or px > w or py < 0 or py > h for px, py in pts)

    if not outside(x0, y0, s):
        return x0, y0, s
    res = [0.0] + [float(re) for re, im in marks]
    ims = [0.0] + [float(im) for re, im in marks]
    rmin, rmax = min(res), max(res)
    imin, imax = min(ims), max(ims)
    if rmax - rmin < 1:
        mid = (rmin + rmax) / 2
        rmin, rmax = mid - 1, mid + 1
    if imax - imin < 1:
        mid = (imin + imax) / 2
        imin, imax = mid - 1, mid + 1
    left, right, top, bottom = 40.0, 246.0, 36.0, 148.0
    s = min((right - left) / (rmax - rmin), (bottom - top) / (imax - imin))
    for _ in range(8):
        x0 = (left + right) / 2 - s * (rmin + rmax) / 2
        y0 = (top + bottom) / 2 + s * (imin + imax) / 2
        if not outside(x0, y0, s):
            return x0, y0, s
        s *= 0.85
    return x0, y0, s


def splane(poles, zeros, title):
    """Pole/zero map. Poles are crosses, zeros are open circles. The frame scales to fit."""
    w, h = 300, 180
    marks = list(poles) + list(zeros)
    x0, y0, sx = _splane_map(marks, w, h)
    gaps = []
    for pr, pi in marks:
        if abs(pi) < 0.2:
            gaps.append(x0 + sx * pr)
    gaps.sort()
    x = 20
    body = ""
    for g in gaps:
        if g - 14 > x:
            body += b2b_line(x, y0, g - 14, y0)
        x = max(x, g + 14)
    if x < 280:
        body += b2b_arrow(x, y0, 280, y0)
    body += b2b_arrow(x0, 160, x0, 16)
    body += b2b_text(274, y0 + 16, "Re", size=11)
    body += b2b_text(x0 + 8, 14, "Im", anchor="start", size=11)
    for pr, pi in poles:
        px, py = x0 + sx * pr, y0 - sx * pi
        body += b2b_line(px - 5, py - 5, px + 5, py + 5, sw=1.8)
        body += b2b_line(px - 5, py + 5, px + 5, py - 5, sw=1.8)
    for zr, zi in zeros:
        body += b2b_circle(x0 + sx * zr, y0 - sx * zi, 5)
    return _guard(b2b_svg(w, h, body, title))


def matrix_fig(rows, title):
    """Each row is a list of entries, such as ["0", "-2"]. A preformatted string is drawn as given."""
    body = b2b_text(28, 78, "[", size=28)
    body += b2b_text(168, 78, "]", size=28)
    for i, row in enumerate(rows):
        if isinstance(row, (list, tuple)):
            label = "   ".join(str(entry) for entry in row)
        else:
            label = str(row)
        body += b2b_text(98, 58 + i * 28, label, size=16)
    return _guard(b2b_svg(200, 130, body, title))


def mass_spring(title, spring=True, damper=True):
    """Draw only the elements the question includes. A missing spring or damper is omitted."""
    body = b2b_rect(16, 36, 14, 100, fill=True)
    if spring:
        body += b2b_line(30, 70, 48, 70)
        body += b2b_poly([(48, 70), (56, 58), (66, 82), (76, 58), (86, 82), (96, 58), (106, 82), (116, 70), (140, 70)])
        body += b2b_text(90, 50, "k", size=12)
    if damper:
        body += b2b_line(30, 112, 78, 112)
        body += b2b_rect(78, 100, 28, 24)
        body += b2b_line(106, 112, 140, 112)
        body += b2b_text(92, 142, "b", size=12)
    body += b2b_rect(140, 48, 64, 80)
    body += b2b_text(172, 94, "m", size=16)
    body += b2b_arrow(204, 88, 250, 88)
    body += b2b_text(258, 92, "F", anchor="start")
    body += b2b_line(30, 148, 230, 148)
    return _guard(b2b_svg(280, 168, body, title))


def block_diagram(blocks, title, feedback=None, input_label="", output_label="out", feedback_sign="-",
                  error_label="", disturbance=None):
    """A row of labeled blocks, with an optional feedback loop.

    input_label sits on the arrow that enters the summing junction (the reference).
    error_label sits on the arrow that leaves that junction, before the first block.
    feedback_sign is '-' when the return is subtracted and '+' when it is added.
    Each summer input gets its own sign. disturbance is a label added at the output,
    after the forward blocks and before the feedback pickoff. A call with no
    feedback keeps the original series drawing.
    """
    gap = 36
    box_w = 84
    box_h = 44
    y = 56
    x = 24
    body = ""
    if not feedback:
        if input_label:
            body += b2b_text(x, y + 4, input_label)
            x += 18
        for label in blocks:
            body += b2b_arrow(x, y, x + gap, y)
            x += gap
            body += b2b_box(x, y - box_h / 2, box_w, box_h, label)
            x += box_w
        body += b2b_arrow(x, y, x + gap, y)
        x += gap
        body += b2b_text(x + 4, y + 4, output_label, anchor="start")
        return _guard(b2b_svg(x + 36, 120, body, title))

    if feedback_sign not in ("-", "+"):
        raise ValueError("feedback_sign must be '-' or '+'")
    if disturbance and feedback_sign != "-":
        raise ValueError("an output disturbance is drawn on a negative loop")
    fb = "\u2212" if feedback_sign == "-" else "+"
    y = 78
    radius = 12
    if input_label:
        body += b2b_text(6, y + 4, input_label, anchor="start")
    jx = 64
    body += b2b_arrow(28, y, jx - radius, y)
    body += b2b_circle(jx, y, radius)
    body += b2b_text(jx - 18, y - 16, "+", size=13)
    body += b2b_text(jx - 22, y + 30, fb, size=13)

    x = jx + radius
    first_gap = 56 if error_label else gap
    body += b2b_arrow(x, y, x + first_gap, y)
    if error_label:
        body += b2b_text(x + first_gap / 2, y - 12, error_label, size=13)
    x += first_gap
    n = len(blocks)
    for i, label in enumerate(blocks):
        body += b2b_box(x, y - box_h / 2, box_w, box_h, label)
        x += box_w
        if disturbance and i == n - 1:
            continue
        body += b2b_arrow(x, y, x + gap, y)
        x += gap
    if disturbance:
        # One arrow from the last block into the output summer. The block does not
        # also keep its own outgoing arrowhead on that same wire.
        sx = x + gap + radius
        body += b2b_arrow(x, y, sx - radius, y)
        body += b2b_circle(sx, y, radius)
        body += b2b_text(sx - 22, y - 16, "+", size=13)
        body += b2b_text(sx + 14, y - 28, "+", size=13)
        body += b2b_arrow(sx, y - 50, sx, y - radius)
        body += b2b_text(sx + 16, y - 44, disturbance, anchor="start", size=13)
        x = sx + radius
        body += b2b_arrow(x, y, x + gap, y)
        x += gap
    body += b2b_text(x + 4, y + 4, output_label, anchor="start")
    pick = x - 8
    yb = y + 56
    body += b2b_line(pick, y, pick, yb)
    body += b2b_line(pick, yb, jx, yb)
    body += b2b_arrow(jx, yb, jx, y + radius)
    body += b2b_text((pick + jx) / 2, yb + 16, feedback, size=11)
    return _guard(b2b_svg(x + 40, yb + 30, body, title))


def parallel_sum(blocks, title, output_label="out"):
    """One signal splits into side-by-side blocks whose outputs add."""
    if len(blocks) < 2:
        raise ValueError("parallel_sum needs at least two blocks")
    box_w, box_h = 72, 36
    pitch = box_h + 22
    top = 28
    bus_in = 44
    x_box = 86
    body = ""
    centers = []
    for i, label in enumerate(blocks):
        y = top + i * pitch
        cy = y + box_h / 2
        centers.append(cy)
        body += b2b_arrow(bus_in, cy, x_box, cy)
        body += b2b_box(x_box, y, box_w, box_h, label)
    mid = (centers[0] + centers[-1]) / 2
    body += b2b_arrow(10, mid, bus_in, mid)
    body += b2b_line(bus_in, centers[0], bus_in, centers[-1])
    body += b2b_circle(bus_in, mid, 2.6, fill=True)
    bus_out = x_box + box_w + 28
    for cy in centers:
        body += b2b_line(x_box + box_w, cy, bus_out, cy)
        body += b2b_text(bus_out - 12, cy - 8, "+", size=13)
    body += b2b_line(bus_out, centers[0], bus_out, centers[-1])
    sum_x = bus_out + 36
    body += b2b_arrow(bus_out, mid, sum_x - 12, mid)
    body += b2b_circle(sum_x, mid, 12)
    body += b2b_text(sum_x, mid + 4, "\u03a3", size=13)
    body += b2b_arrow(sum_x + 12, mid, sum_x + 40, mid)
    body += b2b_text(sum_x + 46, mid + 4, output_label, anchor="start")
    height = top + (len(blocks) - 1) * pitch + box_h + 20
    return _guard(b2b_svg(sum_x + 72, height, body, title))


def nyquist(points, title):
    """Nyquist curve in the complex plane, with the critical point marked. points are (re, im)."""
    w, h = 300, 220
    data = [(float(a), float(b)) for a, b in points] + [(-1.0, 0.0), (0.0, 0.0)]
    left, right, top, bottom = 48, 270, 28, 180
    X, Y = _fit(data, left, right, top, bottom)
    body = b2b_arrow(left, Y(0), right, Y(0))
    body += b2b_arrow(X(0), bottom, X(0), top)
    body += b2b_text(right - 4, Y(0) + 14, "Re", anchor="end", size=11)
    body += b2b_text(X(0) + 6, top + 4, "Im", anchor="start", size=11)
    body += b2b_poly([(X(a), Y(b)) for a, b in points], sw=2.2)
    body += b2b_circle(X(-1), Y(0), 4)
    body += b2b_text(X(-1), Y(0) - 10, "\u22121", size=11)
    return _guard(b2b_svg(w, h, body, title))


def root_locus(branches, title, poles=(), zeros=()):
    """Root locus. branches is a list of polylines of (re, im). Poles are crosses, zeros are circles."""
    w, h = 300, 200
    marks = [(0.0, 0.0)]
    for branch in branches:
        marks.extend(branch)
    marks.extend(poles)
    marks.extend(zeros)
    left, right, top, bottom = 40, 270, 24, 168
    X, Y = _fit(marks, left, right, top, bottom)
    body = b2b_arrow(left, Y(0), right, Y(0))
    body += b2b_arrow(X(0), bottom, X(0), top)
    body += b2b_text(right - 4, Y(0) + 14, "Re", anchor="end", size=11)
    body += b2b_text(X(0) + 6, top + 2, "Im", anchor="start", size=11)
    for branch in branches:
        body += b2b_poly([(X(a), Y(b)) for a, b in branch], sw=2.0)
    for pr, pi in poles:
        px, py = X(pr), Y(pi)
        body += b2b_line(px - 5, py - 5, px + 5, py + 5, sw=1.6)
        body += b2b_line(px - 5, py + 5, px + 5, py - 5, sw=1.6)
    for zr, zi in zeros:
        body += b2b_circle(X(zr), Y(zi), 5)
    return _guard(b2b_svg(w, h, body, title))
