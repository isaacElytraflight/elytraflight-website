"""SVG figures for ME 132 batch B1. Built on the shared figlib helpers.

Alt text describes the drawing. It does not state the quantity the question asks for.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import (
    b2b_arrow, b2b_axes, b2b_box, b2b_circle, b2b_curve, b2b_dot, b2b_ground,
    b2b_line, b2b_poly, b2b_rect, b2b_resistor, b2b_svg, b2b_text, b2b_vsource,
    b2b_wire, b2b_capacitor,
)


def plot(fn, xa, xb, xlabel, ylabel, title, w=340, h=176, zero=False):
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
    return b2b_svg(w, h, body, title)


def _summer(x, y, minus="bottom"):
    body = b2b_circle(x, y, 12)
    body += b2b_line(x - 6, y, x + 6, y, sw=1.1)
    body += b2b_line(x, y - 6, x, y + 6, sw=1.1)
    body += b2b_text(x - 18, y - 10, "+", size=13)
    if minus == "bottom":
        # Sit beside the return wire, not on top of it.
        body += b2b_text(x + 16, y + 20, "\u2212", size=13)
    else:
        body += b2b_text(x + 16, y - 8, "\u2212", size=13)
    return body


def closed_loop(title, disturbance=False, noise=False):
    """Reference, controller, actuator, plant, sensor. Optional d or sensor noise."""
    y = 72
    body = b2b_text(16, y + 4, "r")
    body += b2b_arrow(28, y, 62, y)
    body += _summer(76, y)
    body += b2b_arrow(90, y, 112, y)
    body += b2b_box(112, y - 22, 46, 44, "C")
    body += b2b_arrow(158, y, 176, y)
    body += b2b_box(176, y - 22, 78, 44, "actuator")
    body += b2b_arrow(254, y, 272, y)
    body += b2b_box(272, y - 22, 52, 44, "plant")
    body += b2b_arrow(324, y, 392, y)
    body += b2b_text(404, y + 4, "y", anchor="start")
    # Return path meets the sensor box at its side edges so the label stays clear.
    body += b2b_line(360, y, 360, 150)
    body += b2b_dot(360, y)
    body += b2b_wire(360, 150, 252, 150)
    body += b2b_box(188, 132, 64, 36, "sensor")
    body += b2b_wire(188, 150, 76, 150)
    body += b2b_arrow(76, 150, 76, 86)
    if disturbance:
        body += b2b_arrow(360, 28, 360, 58)
        body += b2b_text(360, 20, "d")
        body += b2b_circle(360, y, 4, fill=True)
    if noise:
        body += b2b_arrow(220, 118, 220, 132)
        body += b2b_text(220, 112, "n")
    return b2b_svg(440, 176, body, title)


def open_loop(title, disturbance=False):
    y = 78
    body = b2b_text(16, y + 4, "r")
    body += b2b_arrow(30, y, 58, y)
    body += b2b_box(58, y - 22, 70, 44, "command")
    body += b2b_arrow(128, y, 156, y)
    body += b2b_box(156, y - 22, 78, 44, "actuator")
    body += b2b_arrow(234, y, 262, y)
    body += b2b_box(262, y - 22, 52, 44, "plant")
    body += b2b_arrow(314, y, 390, y)
    body += b2b_text(402, y + 4, "y", anchor="start")
    if disturbance:
        body += b2b_arrow(348, 28, 348, 64)
        body += b2b_text(348, 20, "d")
        body += b2b_dot(348, y)
    body += b2b_text(210, 150, "no measurement returns", size=11)
    return b2b_svg(440, 170, body, title)


def series_blocks(title):
    y = 70
    body = b2b_arrow(20, y, 50, y)
    body += b2b_box(50, y - 24, 70, 48, "gain 3")
    body += b2b_arrow(120, y, 160, y)
    body += b2b_box(160, y - 24, 70, 48, "gain 4")
    body += b2b_arrow(230, y, 280, y)
    body += b2b_text(292, y + 4, "out", anchor="start")
    return b2b_svg(340, 120, body, title)


def proportional(title):
    y = 74
    body = b2b_text(16, y + 4, "r")
    body += b2b_arrow(30, y, 58, y)
    body += _summer(72, y)
    body += b2b_text(96, y - 16, "e", size=11)
    body += b2b_arrow(86, y, 118, y)
    body += b2b_box(118, y - 22, 64, 44, "Kc")
    body += b2b_arrow(182, y, 230, y)
    body += b2b_text(242, y + 4, "u", anchor="start")
    body += b2b_text(72, 140, "y", size=11)
    body += b2b_arrow(72, 128, 72, 88)
    return b2b_svg(280, 160, body, title)


def bars(title):
    """Qualitative open-loop vs closed-loop movement. No numeric scale."""
    body = b2b_text(70, 22, "open loop", size=12)
    body += b2b_text(210, 22, "closed loop", size=12)
    body += b2b_rect(40, 40, 28, 110, fill=True)
    body += b2b_rect(78, 100, 28, 50, fill=True)
    body += b2b_rect(180, 78, 28, 72, fill=True)
    body += b2b_rect(218, 96, 28, 54, fill=True)
    body += b2b_text(54, 168, "before", size=10)
    body += b2b_text(92, 168, "after", size=10)
    body += b2b_text(194, 168, "before", size=10)
    body += b2b_text(232, 168, "after", size=10)
    body += b2b_line(30, 150, 260, 150)
    return b2b_svg(290, 186, body, title)


def matrix_fig(rows, title):
    body = b2b_text(28, 78, "[", size=28)
    body += b2b_text(168, 78, "]", size=28)
    for i, row in enumerate(rows):
        body += b2b_text(98, 58 + i * 28, "   ".join(row), size=16)
    return b2b_svg(200, 130, body, title)


def vectors(title):
    body = b2b_arrow(30, 120, 150, 40)
    body += b2b_text(156, 38, "v1", anchor="start", size=12)
    body += b2b_arrow(30, 120, 160, 110)
    body += b2b_text(166, 114, "v2", anchor="start", size=12)
    body += b2b_arrow(30, 120, 118, 78, head=7)
    body += b2b_text(124, 68, "v3", anchor="start", size=12)
    return b2b_svg(220, 150, body, title)


def eigen_plane(title):
    body = b2b_arrow(30, 90, 250, 90)
    body += b2b_arrow(140, 150, 140, 20)
    body += b2b_text(246, 106, "Re", size=11)
    body += b2b_text(148, 18, "Im", anchor="start", size=11)
    body += b2b_text(70, 80, "\u00d7", size=16)
    body += b2b_text(190, 80, "\u00d7", size=16)
    return b2b_svg(270, 170, body, title)


def splane(poles, zeros, title, xr=(-8, 4)):
    w, h = 300, 180
    x0, y0 = 150, 90
    sx = 22
    # Break the real axis around marks that sit on it, so a zero is an open circle.
    gaps = []
    for pr, pi in list(poles) + list(zeros):
        if abs(pi) < 0.2:
            gaps.append(x0 + sx * pr)
    gaps.sort()
    x = 20
    body = ""
    for g in gaps:
        if g - 14 > x:
            body += b2b_line(x, y0, g - 14, y0)
        x = g + 14
    body += b2b_arrow(x, y0, 280, y0)
    body += b2b_arrow(x0, 160, x0, 16)
    body += b2b_text(274, y0 + 16, "Re", size=11)
    body += b2b_text(x0 + 8, 14, "Im", anchor="start", size=11)
    for pr, pi in poles:
        x, y = x0 + sx * pr, y0 - sx * pi
        body += b2b_line(x - 5, y - 5, x + 5, y + 5, sw=1.8)
        body += b2b_line(x - 5, y + 5, x + 5, y - 5, sw=1.8)
    for zr, zi in zeros:
        body += b2b_circle(x0 + sx * zr, y0 - sx * zi, 5)
    return b2b_svg(w, h, body, title)


def bode_slope(title):
    """Magnitude falling at one slope, then steeper. The trace stays inside the axes."""
    pts = [(58, 42), (150, 86), (268, 142)]
    body = b2b_axes(50, 156, 250, 126, "log \u03c9", "|H| dB")
    body += b2b_poly(pts, sw=2.2)
    body += b2b_text(96, 52, "\u221220", size=11)
    body += b2b_text(188, 96, "\u221240", size=11)
    return b2b_svg(330, 186, body, title)


def inverse_step(title):
    def y(t):
        return 0.5 - math.exp(-t) + 0.5 * math.exp(-4 * t)
    return plot(y, 0, 4, "t", "y", title, zero=True)


def mass_spring(title):
    body = b2b_rect(16, 36, 14, 100, fill=True)
    body += b2b_line(30, 70, 48, 70)
    body += b2b_poly([(48, 70), (56, 58), (66, 82), (76, 58), (86, 82), (96, 58), (106, 82), (116, 70), (140, 70)])
    body += b2b_text(90, 50, "k", size=12)
    body += b2b_line(30, 112, 78, 112)
    body += b2b_rect(78, 100, 28, 24)
    body += b2b_line(106, 112, 140, 112)
    body += b2b_text(92, 142, "b", size=12)
    body += b2b_rect(140, 48, 64, 80)
    body += b2b_text(172, 94, "m", size=16)
    body += b2b_arrow(204, 88, 250, 88)
    body += b2b_text(258, 92, "F", anchor="start")
    body += b2b_line(30, 148, 230, 148)
    return b2b_svg(280, 168, body, title)


def rotor(title):
    body = b2b_circle(120, 80, 36)
    body += b2b_circle(120, 80, 6, fill=True)
    body += b2b_arrow(156, 80, 210, 80)
    body += b2b_text(218, 84, "\u03c4", anchor="start")
    body += b2b_text(120, 34, "J", size=14)
    body += b2b_text(120, 140, "viscous friction b", size=12)
    return b2b_svg(250, 160, body, title)


def tank(title):
    body = b2b_line(70, 30, 70, 140)
    body += b2b_line(170, 30, 170, 140)
    body += b2b_line(70, 140, 170, 140)
    body += b2b_rect(71, 78, 98, 62, fill=True)
    body += b2b_line(70, 78, 170, 78, dash=True)
    body += b2b_text(150, 74, "h", anchor="end", size=12)
    body += b2b_arrow(110, 16, 110, 40)
    body += b2b_text(124, 28, "q in", anchor="start", size=11)
    body += b2b_arrow(170, 120, 220, 120)
    body += b2b_text(188, 112, "q out", size=11)
    return b2b_svg(250, 168, body, title)


def inductor_h(x, y, L=56):
    n = 4
    lead = 8
    seg = (L - 2 * lead) / n
    body = b2b_line(x, y, x + lead, y)
    d = []
    for i in range(n):
        x1 = x + lead + i * seg
        # upper semicircle, left to right
        d.append(f"M {x1:.1f} {y:.1f} a {seg/2:.1f} {seg/2:.1f} 0 0 1 {seg:.1f} 0")
    body += f'<path d="{" ".join(d)}"/>'
    body += b2b_line(x + L - lead, y, x + L, y)
    return body


def rl_circuit(title):
    body = b2b_vsource(40, 30, 70, "v")
    body += b2b_wire(40, 30, 90, 30)
    body += inductor_h(90, 30, 70)
    body += b2b_text(125, 18, "L", size=12)
    body += b2b_wire(160, 30, 210, 30)
    body += b2b_resistor(210, 30, 60, label="R")
    body += b2b_wire(270, 30, 300, 30, 300, 100, 40, 100)
    body += b2b_ground(170, 100)
    return b2b_svg(320, 140, body, title)


def rc_circuit(title):
    body = b2b_vsource(40, 28, 80, "vs")
    body += b2b_wire(40, 28, 100, 28)
    body += b2b_resistor(100, 28, 70, label="R")
    body += b2b_wire(170, 28, 230, 28, 230, 70)
    body += b2b_capacitor(230, 70, 40, horiz=False, label="C")
    body += b2b_wire(230, 110, 230, 128, 40, 128)
    body += b2b_ground(140, 128)
    return b2b_svg(300, 160, body, title)


def car(title):
    body = b2b_rect(70, 70, 120, 36, r=8)
    body += b2b_rect(96, 48, 60, 24, r=6)
    body += b2b_circle(100, 106, 12)
    body += b2b_circle(164, 106, 12)
    body += b2b_line(40, 120, 250, 120)
    body += b2b_arrow(200, 78, 250, 78)
    body += b2b_text(236, 68, "F", size=12)
    body += b2b_text(130, 92, "m", size=13)
    return b2b_svg(280, 146, body, title)


def step_shape(title, tau=1.0, goal=1.0):
    return plot(lambda t: goal * (1 - math.exp(-t / tau)), 0, 5 * tau, "t", "y", title)


def decay_shape(title):
    return plot(lambda t: math.exp(-t), 0, 4, "t", "y", title)


def sine_shape(title):
    return plot(lambda t: math.sin(t), 0, 2 * math.pi, "t", "sin", title, zero=True)


def delay_blocks(title):
    y = 70
    body = b2b_arrow(16, y, 50, y)
    body += b2b_box(50, y - 24, 90, 48, "delay")
    body += b2b_arrow(140, y, 190, y)
    body += b2b_text(200, y + 4, "y", anchor="start")
    return b2b_svg(240, 120, body, title)
