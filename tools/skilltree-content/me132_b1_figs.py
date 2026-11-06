"""SVG figures for ME 132 batch B1. Shared shapes come from templates.py.

Alt text describes the drawing. It does not state the quantity the question asks for.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import (
    b2b_arrow, b2b_box, b2b_circle, b2b_dot, b2b_ground,
    b2b_line, b2b_rect, b2b_resistor, b2b_svg, b2b_text, b2b_vsource,
    b2b_wire, b2b_capacitor,
)
from templates import (
    block_diagram, bode_sketch as bode_slope, mass_spring, matrix_fig, plot,
    splane, step_response,
)


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
    return block_diagram(["gain 3", "gain 4"], title, output_label="out")


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


def inverse_step(title):
    def y(t):
        return 0.5 - math.exp(-t) + 0.5 * math.exp(-4 * t)
    return plot(y, 0, 4, "t", "y", title, zero=True)


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
    return step_response(title, tau=tau, goal=goal)


def decay_shape(title):
    return plot(lambda t: math.exp(-t), 0, 4, "t", "y", title)


def sine_shape(title):
    return plot(lambda t: math.sin(t), 0, 2 * math.pi, "t", "sin", title, zero=True)


def delay_blocks(title):
    return block_diagram(["delay"], title, output_label="y")
