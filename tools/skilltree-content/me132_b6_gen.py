#!/usr/bin/env python3
"""Generate ME 132 batch B6 banks and explainers.

Closed-form answers live here. skilltree/verify_me132_b6.py recomputes them
with determinants, ranks, a Kronecker Lyapunov solve, least squares, and
trigonometry. Do not import this file from the verifier.
"""
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import (
    block_diagram, bode, bode_sketch, ellipse_axes, matrix_fig, plane_vectors,
    root_locus, splane, step_response,
)
from banklib import BANK, EXP, Bank, g, save_explainer, words


def show(x):
    return f"{g(x):.6g}"


def series(blocks, title):
    return block_diagram(blocks, title, input_label="in", output_label="out")


def put_explainer(sid, title, sections):
    for section in sections:
        svg = section.get("figure_svg")
        if svg and "figure" not in section:
            section["figure"] = svg
    save_explainer(sid, title, sections)
    return words(sections)


# ---------------------------------------------------------------------------
# loop shaping
# ---------------------------------------------------------------------------

def bank_loop_shaping():
    b = Bank("loop-shaping")
    lead = series(["lead", "P"], "lead in series with the plant")
    lead_alt = "A lead block followed by a plant block."
    lag = series(["lag", "P"], "lag in series with the plant")
    lag_alt = "A lag block followed by a plant block."
    bode = bode_sketch("magnitude that steepens, then steepens again")
    bode_alt = "A magnitude sketch that falls, then falls more steeply."
    phi = math.degrees(math.asin((3 - 1) / (3 + 1)))
    center = math.sqrt(4 * 16)
    comp = 1 / 0.25
    hf = 1 / 5

    b.mc(1,
         r"A lead compensator is placed near the intended crossover so that",
         [r"its phase bump sits where \(|L|\) crosses 1",
          "the low-frequency gain becomes infinite without a phase change",
          "a right-half-plane zero is cancelled by the new pole",
          "the crossover frequency is guaranteed not to move"], 0,
         r"The peak lead sits at the geometric mean of the zero and the pole. That is the frequency where you want \(|L| = 1\), because phase margin is read there. A lead does not create infinite DC gain, it does not cancel a right-half-plane zero, and its own magnitude usually moves the crossover, which is why the margin is checked again.",
         lead, lead_alt)
    b.num(1,
          r"A lead has its pole three times farther from the origin than its zero. The peak phase it can add, in degrees, is",
          phi, "deg",
          r"With \(\alpha = 3\), \(\sin\phi_m = (\alpha-1)/(\alpha+1) = 1/2\), so \(\phi_m = " + show(phi) + r"\) degrees. Using \(\alpha\) itself, 3, as a degree measure has no meaning. The formula \((\alpha-1)/(\alpha+1)\) is the sine of the angle, not the angle. A lag of the same ratio would contribute a negative phase.",
          bode, bode_alt)
    b.num(1,
          r"A lead zero is at \(4\ \mathrm{rad/s}\) and its pole is at \(16\ \mathrm{rad/s}\). The frequency of peak phase, in rad/s, is",
          center, "rad/s",
          r"The peak is at the geometric mean \(\sqrt{4 \cdot 16} = " + show(center) + r"\). The arithmetic mean \((4+16)/2 = 10\) is not the center of a Bode lead. The difference \(16-4 = 12\) is the gap between the corners, not the frequency of the bump.",
          lead, lead_alt)

    b.sym(2,
          r"A lead zero is at \(z > 0\) and the pole is at \(p > 0\), both measured in rad/s. Write the frequency of peak phase, in the names z and p.",
          "sqrt(z*p)", {"z": (0.4, 8.0), "p": (0.4, 8.0)},
          r"Peak lead sits at the geometric mean \(\sqrt{z p}\). The arithmetic mean \((z+p)/2\) is a different average and is not where \(\phi_m\) occurs. The ratio \(p/z\) is the lead ratio \(\alpha\), not a frequency.",
          alternates=["sqrt(p*z)"],
          fig=bode, alt=bode_alt)
    b.num(2,
          r"At the frequency where you want crossover, the plant magnitude is \(0.25\). The compensator magnitude that makes \(|L| = 1\) there is",
          comp, "1",
          r"\(|L| = |C|\,|P|\). Setting that to 1 gives \(|C| = 1/0.25 = " + show(comp) + r"\). Using the plant magnitude itself, 0.25, would leave \(|L| = 0.0625\). Adding 1 to the plant magnitude is not the required compensator.",
          lead, lead_alt)
    b.order(2,
            r"Put these loop-shaping steps in the order you would do them.",
            ["Read the uncompensated crossover and phase margin.",
             "Choose a lead ratio and center its phase bump on the intended crossover.",
             "Set the gain so the loop crosses over inside that bump.",
             "Add lag or PI below crossover only if the low-frequency gain is still short.",
             "Read the margins again at the crossover you actually got."],
            r"The plant's margin tells you how much phase to buy. The lead is then centered where you want to cross, and the gain is what places the crossing there. Lag and PI come after, below the new crossover, so they do not spend the phase you just added. The last reading is mandatory because every block can move the crossing.",
            lead, lead_alt)

    b.find_error(3,
                 r"A designer writes this argument about a lead. One step is wrong.",
                 [r"The plant crosses over at \(8\ \mathrm{rad/s}\) with phase \(-150^\circ\), so the phase margin is \(30^\circ\).",
                  r"A lead can add \(40^\circ\) at the geometric mean of its zero and pole.",
                  r"Centering that mean at \(0.8\ \mathrm{rad/s}\), a decade below the crossover, adds the full \(40^\circ\) to the phase margin.",
                  r"The lead's magnitude also moves the crossover, so the margin has to be read again after the gain is set."],
                 2,
                 r"The phase bump is local. A decade below crossover, the lead's phase has already fallen well below its peak, so the margin at \(8\ \mathrm{rad/s}\) barely changes. The first two steps are the right readings, and the last step is why you recompute the margin after the gain moves the crossing.",
                 reasons=["The phase bump is local, so a center a decade below crossover does not deliver the peak lead at crossover.",
                          r"A phase of \(-150^\circ\) is already unstable, so the margin is not \(30^\circ\).",
                          "Lead magnitude cannot move a crossover."],
                 correct_reason=0,
                 fig=bode, alt=bode_alt)
    b.mc(3,
         r"A lag \((s+1)/(5s+1)\) is placed well below crossover in order to",
         ["add its peak phase at the crossover",
          "lower the high-frequency loop gain while keeping the DC gain",
          "cancel a right-half-plane pole of the plant",
          "make the slope at crossover steeper by adding a zero there"], 1,
         r"The DC gain of this lag is 1 and the high-frequency gain is \(1/5\), so it can drop the crossover into a friendlier phase region without giving up the low-frequency gain. Its phase is negative, a penalty, not a bump you want at crossover. It does not cancel an unstable pole, and its zero is the higher corner, not a zero parked at crossover.",
         lag, lag_alt)
    b.multi(3,
            r"Which of these are lead networks, with both corners in the open left half-plane and the zero closer to the origin?",
            [r"\((s+2)/(s+10)\)",
             r"\((s+10)/(s+2)\)",
             r"\((s+1)/(s+4)\)",
             r"\((s-3)/(s+9)\)"],
            [0, 2],
            r"\((s+2)/(s+10)\) and \((s+1)/(s+4)\) each put the zero at a smaller magnitude than the pole, and both corners are in the left half-plane. \((s+10)/(s+2)\) is the same corners swapped, which is a lag. \((s-3)/(s+9)\) has a right-half-plane zero, which adds lag rather than lead.",
            splane([(-2, 0), (-10, 0)], [], "two left-half-plane marks"),
            "Two marks on the negative real axis, one closer to the origin than the other.")

    b.num(4,
          r"The lag is \((s+1)/(5s+1)\). Far above both corners, its magnitude approaches",
          hf, "1",
          r"The high-frequency gain is the ratio of the leading coefficients, \(1/5 = " + show(hf) + r"\). The DC gain is 1, which is the value far below both corners. The corner ratio 5 is how many times smaller the high-frequency gain is, not the gain itself.",
          lag, lag_alt, ["fund-limits"])
    b.mc(4,
         r"After the gain is raised so that crossover falls at the lead's geometric center,",
         ["the closed-loop poles stay at the open-loop locations",
          "sensor noise is removed by the lead zero",
          "phase margin must be read at the new crossover, not the old one",
          "a lag is no longer allowed anywhere in the loop"], 2,
         r"Phase margin is the gap from \(-180^\circ\) at whatever frequency now has \(|L| = 1\). Moving the crossing moves that frequency. The lead does not freeze the closed-loop poles at the open-loop poles, it does not filter every sensor noise, and a lag below the new crossover is still a normal second step.",
         lead, lead_alt, ["fund-limits"])
    b.mc(4,
         r"A PI factor \(K_p(s + 1/\tau_i)/s\), used as part of a loop shape,",
         ["is identical to a lead whose pole and zero have been swapped",
          "removes sensor noise above the crossover",
          r"cancels the plant's slowest stable pole for every \(\tau_i\)",
          "puts a pole at the origin, so a constant error integrates away, and a zero that limits the phase loss at crossover"], 3,
         r"The pole at the origin makes the low-frequency loop gain infinite, which is what removes a constant error. The zero at \(-1/\tau_i\) stops that pole from still costing \(90^\circ\) at crossover, provided the zero is placed below the crossing. Swapping a lead's corners produces a lag, not a PI. The PI zero is not a noise filter, and it cancels a plant pole only when you deliberately set \(\tau_i\) to that pole.",
         series(["PI", "P"], "PI in series with the plant"),
         "A PI block followed by a plant block.", ["fund-limits"])
    b.save()


def expl_loop_shaping():
    fig = bode_sketch("a magnitude sketch used while shaping a loop")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A magnitude sketch that starts shallow and then falls more steeply.",
        "body_md": r"""Loop shaping edits the loop transfer \(L(j\omega)\) until three things sit where you want them: the frequency where \(|L|\) crosses 1, the phase margin at that crossing, and the gain at low frequency. The blocks are ordinary. A lead adds phase in a band around one frequency. A lag, or a proportional-integral term, buys low-frequency gain relative to the gain at crossover. The plant itself is not rewritten.

You are drawing \(L\), not naming each closed-loop pole. The closed-loop behavior follows once the crossover and the margins are right, and it follows badly when a right-half-plane zero or a delay spends phase you cannot buy back.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""For a lead with ratio \(\alpha > 1\), zero at \(-z\) and pole at \(-\alpha z\),
\[
\sin\phi_m = \frac{\alpha - 1}{\alpha + 1}, \qquad \omega_m = \sqrt{\alpha}\, z = \sqrt{|z|\,|p|}.
\]
The sine formula is the peak phase, not the phase at every frequency. A lag \((\tau s + 1)/(\beta \tau s + 1)\) with \(\beta > 1\) has high-frequency gain \(1/\beta\). A PI factor \(K_p(s + 1/\tau_i)/s\) has a pole at the origin and a zero you place below crossover.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(\alpha = 7\). Then \((\alpha-1)/(\alpha+1) = 0.75\), and \(\arcsin(0.75)\) is about 48.59 degrees of peak lead. Put the zero at \(1.6\ \mathrm{rad/s}\) and the pole at \(11.2\ \mathrm{rad/s}\). The bump is centered at \(\sqrt{1.6 \cdot 11.2} \approx 4.23\ \mathrm{rad/s}\). Set the gain so \(|L|\) is 1 at that center, then read the phase there again. If the low-frequency gain is still shy of the spec, add a lag whose upper corner is well below \(4.23\ \mathrm{rad/s}\).""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""Swapping the corners turns a lead into a lag and spends phase instead of buying it. The peak formula returns a sine; treating \((\alpha-1)/(\alpha+1)\) as a number of degrees understates a modest lead and overstates a strong one. Centering the bump a decade away from the real crossover delivers almost none of \(\phi_m\) where it counts. And the lead's magnitude moves the crossing, so a margin computed on the bare plant is stale the moment you turn the gain.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""A loop can be shaped only inside the limits set by right-half-plane zeros, unstable poles, and delay. Those bounds say how high the crossover can sit before the phase budget is gone. Shaping past that bound does not fail because the lead formula was wrong. It fails because no stable proper compensator can buy the phase back.""",
    }]
    return put_explainer("loop-shaping", "Loop shaping with lead, lag, and PI", sections)


# ---------------------------------------------------------------------------
# Lyapunov
# ---------------------------------------------------------------------------

def bank_lyapunov():
    b = Bank("lyapunov")
    bowl = ellipse_axes("a quadratic level curve around the origin")
    bowl_alt = "An ellipse centered on the origin, longer along one axis."
    poles = splane([(-2, 0), (-3, 0)], [], "two stable eigenvalues")
    poles_alt = "Two cross marks on the negative real axis."
    p_scalar = 12 / (2 * 3)
    vdot = 2 * 0.5 * (-4 * 0.5)
    p11 = 1.25
    vdot2 = 8 * 1.5 * (-0.5 * 1.5)

    b.mc(1,
         r"A scalar function \(V\) certifies that an equilibrium at the origin is asymptotically stable when",
         [r"\(V\) is positive definite and \(\dot{V}\) along the dynamics is negative definite",
          r"\(V\) is positive at even one point near the origin",
          r"\(\dot{V}\) is positive definite, so trajectories climb the bowl",
          r"\(V\) equals the output \(y\)"], 0,
         r"The bowl has to be positive everywhere except at the origin, and motion has to decrease it. One positive sample does not make \(V\) positive definite. A positive derivative drives trajectories away. The output is not a Lyapunov function unless it happens to meet both tests, which a general \(y\) does not.",
         bowl, bowl_alt)
    b.num(1,
          r"For \(\dot{x} = -3x\), solve \(2(-3)P = -12\). The certificate \(P\) is",
          p_scalar, "1",
          r"\(2 a P = -q\) with \(a = -3\) and \(q = 12\) gives \(-6P = -12\), so \(P = " + show(p_scalar) + r"\). The positive root of the state weight, 12, is \(q\), not \(P\). Flipping the sign of \(a\) would make \(P\) negative, and a negative \(P\) is not a certificate.",
          poles, poles_alt)
    b.num(1,
          r"Take \(V = x^2\) and \(\dot{x} = -4x\). At \(x = 0.5\), \(\dot{V}\) is",
          vdot, "1",
          r"\(\dot{V} = 2x \dot{x} = 2x(-4x) = -8x^2\). At \(x = 0.5\), that is \(-8 \cdot 0.25 = " + show(vdot) + r"\). Dropping the 2 from the chain rule leaves \(-4x^2 = -1\). Using \(+4x\) as the vector field flips the sign and gives \(+2\).",
          bowl, bowl_alt)

    b.sym(2,
          r"For \(\dot{x} = a x\) with \(a < 0\), you pick \(q > 0\) and solve \(2 a P = -q\). Write \(P\) in the names a and q.",
          "-q/(2*a)", {"a": (-4.0, -0.3), "q": (0.4, 6.0)},
          r"Solving \(2 a P = -q\) gives \(P = -q/(2a)\). Because \(a\) is negative, this \(P\) is positive. The reciprocal \( -2a/q \) inverts the certificate. Dropping the 2 leaves a value twice too large.",
          alternates=["q/(-2*a)", "-0.5*q/a"],
          fig=poles, alt=poles_alt)
    b.num(2,
          r"For \(A = \begin{bmatrix} 0 & 1 \\ -2 & -3 \end{bmatrix}\) and \(Q = I\), the solution of \(A^T P + PA = -Q\) has upper-left entry",
          p11, "1",
          r"Write \(P = \begin{bmatrix} p & q \\ q & r \end{bmatrix}\). The equation forces \(q = 1/4\), \(r = 1/4\), and \(p - 3q - 2r = 0\), so \(p = 5/4 = " + show(p11) + r"\). The off-diagonal entry \(1/4\) is not the upper-left entry. The trace of \(A\), which is \(-3\), is not an entry of \(P\).",
          matrix_fig([["0", "1"], ["-2", "-3"]], "a 2 by 2 state matrix"),
          "A 2 by 2 matrix with first row 0, 1 and second row -2, -3.")
    b.order(2,
            r"Put these steps in the order you would use to test a linear system with the Lyapunov equation.",
            ["Choose a symmetric positive definite matrix Q.",
             "Solve A transpose P + P A = -Q for the symmetric unknown P.",
             "Test whether that P is positive definite.",
             "If it is, conclude that the origin of x-dot = A x is asymptotically stable."],
            r"You pick \(Q\) first, because the equation is linear in \(P\) once \(Q\) is known. Solving comes next. Positive definiteness of \(P\) is the test, not an assumption you skip. Only then does the quadratic \(x^T P x\) certify asymptotic stability. Checking \(P\) before solving has nothing to check.",
            bowl, bowl_alt)

    b.find_error(3,
                 r"A note applies \(V(x) = x^2\) to \(\dot{x} = x\). One step is wrong.",
                 [r"\(V(x) = x^2\) is positive for every \(x \ne 0\), and \(V(0) = 0\).",
                  r"Along \(\dot{x} = x\), the derivative is \(\dot{V} = 2x^2\), and that derivative is negative definite.",
                  r"A certificate needs a positive definite \(V\) and a negative definite derivative together.",
                  r"The same \(V\) does certify \(\dot{x} = -x\), where \(\dot{V} = -2x^2\)."],
                 1,
                 r"\(\dot{V} = 2x \cdot x = 2x^2\) is positive, so trajectories climb the bowl. Calling it negative definite reverses the test. \(V\) itself is a fine bowl, the general rule in the next step is right, and the same bowl does certify the stable scalar system \(\dot{x} = -x\).",
                 reasons=["The derivative 2x^2 is positive, so it is not a certificate for this vector field.",
                          "V(x) = x^2 is negative at the origin, so the first step already failed.",
                          "A positive derivative is exactly what asymptotic stability requires."],
                 correct_reason=0,
                 fig=bowl, alt=bowl_alt)
    b.mc(3,
         r"Along a trajectory, \(\dot{V} = 0\) while \(V\) is positive definite. This \(V\)",
         ["proves exponential stability on its own",
          "does not prove asymptotic stability, because the bowl is not strictly decreasing",
          "proves that the origin is unstable",
          r"says that \(V\) fails to be positive definite"], 1,
         r"Asymptotic stability needs the derivative to be negative definite, not merely non-positive. A zero derivative can belong to a conserved oscillation. It does not prove instability either, and it says nothing against the positive definiteness of \(V\).",
         bowl, bowl_alt)
    b.multi(3,
            r"Which of these are Lyapunov certificates for asymptotic stability of the system written with them?",
            [r"\(V = x^2\) along \(\dot{x} = -2x\)",
             r"\(V = -x^2\) along \(\dot{x} = -2x\)",
             r"\(V = x^2\) along \(\dot{x} = 2x\)",
             r"\(V = 3x^2\) along \(\dot{x} = -2x\)"],
            [0, 3],
            r"For \(\dot{x} = -2x\), both \(V = x^2\) and \(V = 3x^2\) are positive definite and their derivatives \(-4x^2\) and \(-12x^2\) are negative definite. \(V = -x^2\) is negative, so it is not a bowl. Along \(\dot{x} = 2x\), the derivative of \(x^2\) is positive, so that pair certifies nothing.",
            poles, poles_alt)

    b.num(4,
          r"Take \(V = 4x^2\) and \(\dot{x} = -0.5 x\). At \(x = 1.5\), \(\dot{V}\) is",
          vdot2, "1",
          r"\(\dot{V} = 8x \dot{x} = 8x(-0.5 x) = -4x^2\). At \(x = 1.5\), \(-4 \cdot 2.25 = " + show(vdot2) + r"\). Using \(V\) itself as the derivative gives \(4 \cdot 2.25 = 9\), the wrong sign and the wrong object. Halving because the vector field has a 0.5 leaves \(-2\), which drops the chain-rule factor.",
          bowl, bowl_alt, ["lqr"])
    b.mc(4,
         r"The matrix \(P\) in \(A^T P + PA = -Q\) is",
         ["the plant gain",
          "an orthogonal matrix you may choose freely",
          "the input matrix of the state equation",
          "the unknown you solve for, and it certifies stability only when it is positive definite"], 3,
         r"\(Q\) is the matrix you choose, positive definite. \(P\) is what the linear equation returns. A positive definite \(P\) makes \(x^T P x\) a Lyapunov function. \(P\) is not the plant, not an arbitrary rotation, and not \(B\).",
         matrix_fig([["p", "q"], ["q", "r"]], "a symmetric unknown matrix"),
         "A symmetric 2 by 2 pattern with a repeated off-diagonal symbol.", ["fb-linearization"])
    b.mc(4,
         r"The Lyapunov equation has a unique solution, but that solution is not positive definite. For \(\dot{x} = Ax\) this means",
         ["the origin is asymptotically stable anyway, because a solution exists",
          r"\(Q\) was illegal, so the test is void",
          "the origin is not asymptotically stable",
          r"every eigenvalue of \(A\) is zero"], 2,
         r"For a linear system the equation produces a positive definite \(P\), for every positive definite \(Q\), exactly when every eigenvalue of \(A\) has a negative real part. A solution that fails to be positive definite means the origin is not asymptotically stable. Existence of some symmetric \(P\) is weaker. The failure does not require every eigenvalue to be zero, and a legal \(Q\) is what made the test meaningful.",
         poles, poles_alt, ["adaptive"])
    b.save()


def expl_lyapunov():
    fig = ellipse_axes("level curve of a quadratic Lyapunov function")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "An ellipse centered at the origin.",
        "body_md": r"""A Lyapunov function is a bowl sitting on the equilibrium. It is zero there and positive everywhere else. If every trajectory walks downhill, the state has nowhere to go but the bottom, and the equilibrium is asymptotically stable. You do not have to solve the differential equation. You only have to check the bowl and the sign of its derivative along the vector field.

For \(\dot{x} = Ax\) the bowl can be a quadratic form \(x^T P x\). The matrix \(P\) is not the plant. It is a certificate you solve for. Positive definiteness of a symmetric matrix, the eigenvalue test and the ellipsoid picture, is the language of that certificate. This skill only asks you to use the test on \(P\).""",
    }, {
        "heading": "Key equations",
        "body_md": r"""Along \(\dot{x} = f(x)\), the chain rule gives \(\dot{V} = (\partial V/\partial x) f(x)\). Asymptotic stability follows when \(V\) is positive definite and \(\dot{V}\) is negative definite. For the linear system, pick a positive definite \(Q\) and solve
\[
A^T P + PA = -Q.
\]
If the solution \(P\) is positive definite, \(V(x) = x^T P x\) has derivative \(-x^T Q x\), and the origin is asymptotically stable. In the scalar case \(2 a P = -q\), so \(P = -q/(2a)\), which is positive only when \(a\) is negative.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(\dot{x} = -0.8 x\) and \(q = 6\). Then \(2(-0.8)P = -6\), so \(1.6 P = 6\) and \(P = 3.75\). The bowl \(V = 3.75 x^2\) is positive definite. Its derivative is \(7.5 x \cdot (-0.8 x) = -6 x^2\), negative for every \(x \ne 0\). The origin is asymptotically stable, which you can also see from the eigenvalue \(-0.8\), but the certificate did not need that shortcut.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""A positive definite \(V\) whose derivative is positive certifies nothing. The sign of \(\dot{V}\) is the whole test. \(\dot{V} \le 0\) that is only semi-definite does not prove asymptotic stability. It allows motion that stays on a level set. Solving the linear equation and forgetting to check that \(P\) is positive definite accepts an unstable \(A\), because an unstable \(A\) still produces a symmetric solution. And \(P\) in this equation is not the plant gain from a block diagram.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""The same quadratic bowl reappears as the value of an infinite-horizon quadratic regulator: the optimal cost decreases along the closed loop, which is why that gain is stabilizing. A feedback linearization is only as stable as the linear target you chose, and that target still needs a certificate. Adaptive updates are often derived so that a joint bowl in the state and the parameter error decreases.""",
    }]
    return put_explainer("lyapunov", "Lyapunov functions and the Lyapunov equation", sections)


# ---------------------------------------------------------------------------
# observability
# ---------------------------------------------------------------------------

def bank_observability():
    b = Bank("observability")
    eye = matrix_fig([["1", "0"], ["0", "1"]], "a full-rank stacked output matrix")
    eye_alt = "A 2 by 2 matrix with ones on the diagonal and zeros off it."
    short = matrix_fig([["1", "0"], ["-2", "0"]], "a stacked output matrix with a zero column")
    short_alt = "A 2 by 2 matrix whose second column is zero."
    axes = plane_vectors([(1.2, 0.2, "C"), (0.3, 1.1, "CA")], "two output directions")
    axes_alt = "Two arrows from the origin pointing in different directions."

    b.mc(1,
         r"A pair \((A, C)\) is observable when",
         ["a finite record of the output determines the initial state",
          "some input can drive every state to the origin",
          r"every eigenvalue of \(A\) has a negative real part",
          r"\(C\) is a row of ones"], 0,
         r"Observability is about the sensor, not the actuator. The output over an interval fixes \(x(0)\) precisely when the stacked matrix of \(C, CA, \ldots\) has full rank. Reachability is the input test. Stability is the eigenvalue test. A row of ones is one particular \(C\), not the definition.",
         axes, axes_alt)
    b.num(1,
          r"For \(A = \begin{bmatrix} 0 & 1 \\ -3 & -4 \end{bmatrix}\) and \(C = \begin{bmatrix} 1 & 0 \end{bmatrix}\), the absolute value of \(\det\begin{bmatrix} C \\ CA \end{bmatrix}\) is",
          1, "1",
          r"\(CA = \begin{bmatrix} 0 & 1 \end{bmatrix}\), so the stacked matrix is the identity and its determinant has absolute value 1. A determinant of 0 would mean a hidden mode. The trace of \(A\), which is \(-4\), is not this determinant.",
          eye, eye_alt)
    b.num(1,
          r"For \(A = \mathrm{diag}(-2, -5)\) and \(C = \begin{bmatrix} 1 & 0 \end{bmatrix}\), the rank of the observability matrix is",
          1, "1",
          r"\(CA = \begin{bmatrix} -2 & 0 \end{bmatrix}\). Both rows are multiples of \(\begin{bmatrix} 1 & 0 \end{bmatrix}\), so the rank is 1, not 2. The second mode is invisible. Rank 0 would require \(C = 0\).",
          short, short_alt)

    b.sym(2,
          r"Let \(A = \begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}\) and \(C = \begin{bmatrix} c & d \end{bmatrix}\). Write \(\det\begin{bmatrix} C \\ CA \end{bmatrix}\) in the names c and d.",
          "c^2 - d^2", {"c": (-3.0, 3.0), "d": (-3.0, 3.0)},
          r"\(CA = \begin{bmatrix} d & c \end{bmatrix}\), so the determinant is \(c^2 - d^2\). The sum \(c^2 + d^2\) would be the determinant of a different stacking, with a sign error in the second row. The product \(cd\) is one entry, not the determinant.",
          alternates=["(c-d)*(c+d)", "c*c - d*d"],
          fig=eye, alt=eye_alt)
    b.num(2,
          r"A three-state \(A = \mathrm{diag}(-1,-2,-3)\) is measured by \(C = \begin{bmatrix} 1 & 0 & 1 \end{bmatrix}\). How many states are unobservable?",
          1, "1",
          r"The rows \(C\), \(CA\), and \(CA^2\) are \(\begin{bmatrix} 1 & 0 & 1 \end{bmatrix}\), \(\begin{bmatrix} -1 & 0 & -3 \end{bmatrix}\), and \(\begin{bmatrix} 1 & 0 & 9 \end{bmatrix}\). The middle column is zero, and the other two columns are independent, so the rank is 2. One state is hidden. Reporting 3 counts every state as hidden. Reporting 0 treats a nonzero \(C\) as a full test.",
          short, short_alt)
    b.order(2,
            r"Put these steps in the order you would use to test observability.",
            ["Form the rows C, CA, and so on up to C A to the n-1.",
             "Stack those rows into one matrix.",
             "Compute the rank of that matrix.",
             "Call the pair observable only when the rank equals the number of states."],
            r"The rows are the output map and its images under \(A\). Stacking them is what makes one matrix. The rank is the number of independent output directions. Full rank, equal to \(n\), is the test. Declaring observability from a nonzero \(C\) skips the rank.",
            axes, axes_alt)

    b.find_error(3,
                 r"A calculation looks at \(\begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}\) as an observability matrix. One step is wrong.",
                 ["The two rows are proportional: the second is twice the first.",
                  "Proportional rows mean the rank is 1, short of a two-state system.",
                  "A nonzero first row means every mode is visible at the output, so the pair is observable.",
                  "An observer gain exists for every mode only when the rank equals the number of states."],
                 2,
                 r"Proportional rows are rank 1, so one direction never reaches the sensor. A nonzero row only shows that something is measured. The first two steps read the matrix correctly, and the last step is the reason the rank has to be \(n\) before every mode can be estimated.",
                 reasons=["A nonzero row is not full rank. Proportional rows leave one mode hidden.",
                          "Proportional rows have rank 2, so the third step is the one that is right.",
                          "The first row being nonzero already contradicts the claim that the rows are proportional."],
                 correct_reason=0,
                 fig=short, alt=short_alt)
    b.mc(3,
         r"Observability of \((A, C)\) is the same rank condition as reachability of",
         [r"\((A, C)\)",
          r"\((A^T, C^T)\)",
          r"\((A, B)\) for every \(B\)",
          r"\((C, A)\), with the factors swapped and not transposed"], 1,
         r"The observability matrix of \((A, C)\) is the transpose of the controllability matrix of \((A^T, C^T)\). Rank is unchanged by transpose, so the tests match. \((A, C)\) is not a reachability pair. Reachability of \((A, B)\) is a different matrix. Swapping to \((C, A)\) without the transpose is not the dual.",
         axes, axes_alt)
    b.multi(3,
            r"Which of these pairs are observable?",
            [r"\(A = \mathrm{diag}(-2,-5)\), \(C = \begin{bmatrix} 1 & 0 \end{bmatrix}\)",
             r"\(A = \mathrm{diag}(-2,-5)\), \(C = \begin{bmatrix} 1 & 1 \end{bmatrix}\)",
             r"\(A = \begin{bmatrix} 0 & 1 \\ -2 & -3 \end{bmatrix}\), \(C = \begin{bmatrix} 1 & 0 \end{bmatrix}\)",
             r"\(A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}\), \(C = \begin{bmatrix} 0 & 1 \end{bmatrix}\)"],
            [1, 2],
            r"A diagonal pair is observable when every mode has a nonzero entry in \(C\). The row \(\begin{bmatrix} 1 & 0 \end{bmatrix}\) misses the second mode, and \(\begin{bmatrix} 1 & 1 \end{bmatrix}\) sees both. The companion pair with \(C = \begin{bmatrix} 1 & 0 \end{bmatrix}\) has observability matrix equal to the identity. Measuring only the velocity of a double integrator leaves the position as a hidden integrator: \(CA = 0\).",
            eye, eye_alt)

    b.num(4,
          r"For \(A = \mathrm{diag}(-1, -4)\) and \(C = \begin{bmatrix} 2 & 5 \end{bmatrix}\), the absolute value of the observability determinant is",
          30, "1",
          r"\(CA = \begin{bmatrix} -2 & -20 \end{bmatrix}\). The determinant is \(2(-20) - 5(-2) = -30\), absolute value 30. The product of the \(C\) entries, 10, drops the images under \(A\). The sum of the diagonal entries of \(A\), \(-5\), is the trace.",
          matrix_fig([["2", "5"], ["-2", "-20"]], "a stacked 2 by 2 output matrix"),
          "A 2 by 2 matrix with first row 2, 5 and second row -2, -20.",
          ["observer"])
    b.mc(4,
         r"A mode that does not appear in any row \(C, CA, \ldots\)",
         ["is always unstable",
          r"can be moved by output injection without changing \(C\)",
          r"can be removed from the input-output map even though it is still an eigenvalue of \(A\)",
          "raises the rank of the observability matrix"], 2,
         r"A hidden mode is invisible at \(y\), so a minimal input-output model deletes it. It remains an eigenvalue of the larger \(A\). Nothing about the rank test forces it to be unstable. Output injection \(A - LC\) cannot move a mode that \(C\) does not see, and a missing direction lowers the rank rather than raising it.",
         short, short_alt, ["observer"])
    b.mc(4,
         r"Observable canonical form is worth building because, when nothing has cancelled,",
         ["every realization in that form has a singular observability matrix",
          "the transfer function gains an extra pole",
          r"reachability is automatic even if \(B = 0\)",
          "the observability matrix is full rank, so an observer gain can be designed"], 3,
         r"The form puts the output map in a coordinate system whose observability matrix is triangular and invertible, as long as no mode was cancelled. A cancelled mode is exactly a drop in rank. The transfer function is unchanged by the coordinate change. Reachability is a property of \(B\), not of this form.",
         eye, eye_alt, ["observer"])
    b.save()


def expl_observability():
    fig = matrix_fig([["c", "0"], ["0", "c"]], "a triangular observability pattern")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A 2 by 2 matrix with matching diagonal symbols and zeros off the diagonal.",
        "body_md": r"""Observability asks whether the sensor can see every state. If a finite record of \(y\) determines \(x(0)\), the pair is observable. The test stacks the output row \(C\) on top of \(CA\), \(CA^2\), and so on. Full rank means the only state that produces zero output for all time is the zero state. A short rank means a hidden mode: an eigenvalue of \(A\) that never reaches the measurement.

This is the dual of reachability. The input test stacks columns \(B, AB, \ldots\). The output test stacks rows. A coordinate change preserves the rank, just as it preserves reachability.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""For \(n\) states,
\[
\mathcal{O} = \begin{bmatrix} C \\ CA \\ \vdots \\ CA^{n-1} \end{bmatrix}.
\]
The pair is observable when \(\mathrm{rank}\,\mathcal{O} = n\). Equivalently, \((A^T, C^T)\) passes the reachability rank test. In observable canonical form the stacked matrix is triangular. A cancelled factor in a transfer function is a mode that is hidden or unreachable, so a minimal realization has dropped it.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Let \(A = \mathrm{diag}(-0.35, -1.7)\) and \(C = \begin{bmatrix} 0 & 6 \end{bmatrix}\). Then \(CA = \begin{bmatrix} 0 & -10.2 \end{bmatrix}\). Both rows have a zero in the first column, so the mode at \(-0.35\) produces no output and no derivative of the output. That column is a hidden direction. Changing the sensor to \(C = \begin{bmatrix} 6 & 6 \end{bmatrix}\) fills the column, and every mode then reaches the measurement.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""A nonzero \(C\) is not a full test. Two proportional rows still have rank 1. The dual uses the transpose: \((A^T, C^T)\), not \((C, A)\) with the factors merely swapped. A hidden mode need not be unstable. It is simply absent from \(y\), which is why a transfer function can have lower degree than the state matrix you started with. And the canonical form is full rank only when nothing was cancelled.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""An observer copies the model and corrects it with a gain times \(y - C\hat{x}\). That gain can put the error eigenvalues anywhere you like only when the pair is observable. A hidden mode stays where \(A\) put it, and no choice of the gain will move it. Designing the gain is the next skill.""",
    }]
    return put_explainer("observability", "Observability and the output rank test", sections)


# ---------------------------------------------------------------------------
# reachability
# ---------------------------------------------------------------------------

def bank_reachability():
    b = Bank("reachability")
    arrows = plane_vectors([(0.2, 1.0, "B"), (1.1, -0.4, "AB")], "two input directions")
    arrows_alt = "Two arrows from the origin pointing in different directions."
    full = matrix_fig([["0", "1"], ["1", "-5"]], "a 2 by 2 controllability matrix")
    full_alt = "A 2 by 2 matrix with first row 0, 1 and second row 1, -5."
    short = matrix_fig([["2", "-2"], ["0", "0"]], "a controllability matrix with a zero row")
    short_alt = "A 2 by 2 matrix whose second row is zero."
    det4 = abs(float(np_det_reach4()))

    b.mc(1,
         r"A pair \((A, B)\) is reachable when",
         ["some input steers any state to any other state in finite time",
          r"every eigenvalue of \(A\) is stable",
          "the output record determines the initial state",
          r"\(B\) is square"], 0,
         r"Reachability is an input property: the columns \(B, AB, \ldots, A^{n-1}B\) have to span the whole state space. Stability is a different test. Observability is the output test. A square \(B\) is neither necessary nor sufficient.",
         arrows, arrows_alt)
    b.num(1,
          r"For \(A = \begin{bmatrix} 0 & 1 \\ -2 & -5 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}\), the absolute value of \(\det\begin{bmatrix} B & AB \end{bmatrix}\) is",
          1, "1",
          r"\(AB = \begin{bmatrix} 1 \\ -5 \end{bmatrix}\), so the matrix is \(\begin{bmatrix} 0 & 1 \\ 1 & -5 \end{bmatrix}\) and the determinant is \(-1\). The absolute value is 1. A value of 0 would mean the columns are dependent. The trace of \(A\), \(-5\), is not this determinant.",
          full, full_alt)
    b.num(1,
          r"For \(A = \mathrm{diag}(-1, -3)\) and \(B = \begin{bmatrix} 2 \\ 0 \end{bmatrix}\), the rank of \(\begin{bmatrix} B & AB \end{bmatrix}\) is",
          1, "1",
          r"\(AB = \begin{bmatrix} -2 \\ 0 \end{bmatrix}\), a multiple of \(B\). The second row is zero, so the rank is 1. The second mode is never driven. Rank 2 would need a nonzero entry in that mode. Rank 0 would need \(B = 0\).",
          short, short_alt)

    b.sym(2,
          r"Let \(A = \begin{bmatrix} 0 & a \\ 0 & 0 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ b \end{bmatrix}\). Write \(\det\begin{bmatrix} B & AB \end{bmatrix}\) in the names a and b.",
          "-a*b^2", {"a": (-3.0, 3.0), "b": (0.4, 3.0)},
          r"\(AB = \begin{bmatrix} a b \\ 0 \end{bmatrix}\), so the determinant is \(-a b^2\). The sign flip \(a b^2\) is the other order of the columns. The product \(ab\) drops a factor of \(b\) and is not the determinant.",
          alternates=["-a*b*b", "-(a*b^2)"],
          fig=full, alt=full_alt)
    b.num(2,
          r"\(A = \mathrm{diag}(-2,-3,-4)\) and \(B\) is the column \((1, 0, 1)\). How many states are unreachable?",
          1, "1",
          r"The columns are \((1,0,1)\), \((-2,0,-4)\), and \((4,0,16)\). The middle entry is always 0, and the first and third columns are independent, so the rank is 2. One state is unreachable. Reporting 3 treats the zero column-entry as a total loss. Reporting 0 treats a nonzero \(B\) as a full test.",
          short, short_alt)
    b.order(2,
            r"Put these steps in the order you would use to test reachability.",
            ["Form the columns B, AB, and so on up to A to the n-1 times B.",
             "Place those columns side by side in one matrix.",
             "Compute the rank of that matrix.",
             "Call the pair reachable only when the rank equals the number of states."],
            r"The columns are the directions the input can produce in one, two, and further steps. Side by side, they are the controllability matrix. The rank counts independent directions. Full rank is the test. Stopping at a nonzero \(B\) misses a mode that \(B\) never touches.",
            arrows, arrows_alt)

    b.find_error(3,
                 r"A note treats \(\begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}\) as a controllability matrix. One step is wrong.",
                 ["The second column is twice the first, so the columns are dependent.",
                  "Dependent columns mean the rank is 1 for this two-column matrix.",
                  "Dependent columns mean the rank is 2, so the pair is reachable.",
                  "State feedback can move every eigenvalue only when the rank equals the number of states."],
                 2,
                 r"A repeated column does not add a direction. The rank is 1, not 2, so one state cannot be steered. The dependence is real, the rank count in the second step is right, and the last step is why the shortage matters for pole placement.",
                 reasons=["Dependent columns leave the rank short of n, so the pair is not reachable.",
                          "A repeated column raises the rank, so the third step is correct.",
                          "Reachability does not care about rank once B is nonzero."],
                 correct_reason=0,
                 fig=short, alt=short_alt)
    b.mc(3,
         r"After a coordinate change \(z = T^{-1} x\) with \(T\) invertible, reachability",
         ["can appear even though the original pair was unreachable",
          r"is unchanged, because the new controllability matrix is \(T^{-1}\) times the old one",
          r"requires the eigenvalues of \(A\) to move",
          "holds only in controllable canonical form"], 1,
         r"The new columns are \(T^{-1} B\), \(T^{-1} AB\), and so on, which is \(T^{-1}\) times the old matrix. An invertible factor preserves rank. It cannot create a direction that was missing, it does not move eigenvalues, and the rank test is not restricted to one coordinate system.",
         arrows, arrows_alt)
    b.multi(3,
            r"Which of these pairs are reachable?",
            [r"\(A = \mathrm{diag}(-1,-4)\), \(B = \begin{bmatrix} 1 \\ 0 \end{bmatrix}\)",
             r"\(A = \begin{bmatrix} 0 & 1 \\ -2 & -3 \end{bmatrix}\), \(B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}\)",
             r"\(A = \mathrm{diag}(-1,-4)\), \(B = \begin{bmatrix} 1 \\ 1 \end{bmatrix}\)",
             r"\(A = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}\), \(B = \begin{bmatrix} 1 \\ 0 \end{bmatrix}\)"],
            [1, 2],
            r"A diagonal pair is reachable only when \(B\) has a nonzero entry in every mode. The column \((1,0)\) misses the second mode, and \((1,1)\) hits both. The companion pair with \(B\) at the bottom is the controllable form, and its controllability matrix has determinant \(-1\). Driving only the position equation of a double integrator gives \(AB = 0\), so the rank is 1.",
            arrows, arrows_alt)

    b.num(4,
          r"A mass has \(A = \begin{bmatrix} 0 & 1 \\ 0 & -0.4 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ 2.5 \end{bmatrix}\). The absolute value of \(\det\begin{bmatrix} B & AB \end{bmatrix}\) is",
          det4, "1",
          r"\(AB = \begin{bmatrix} 2.5 \\ -1 \end{bmatrix}\). The determinant is \(-2.5 \cdot 2.5 = -6.25\), absolute value " + show(det4) + r". A zero determinant would say the force cannot produce both position and velocity. Using only the 2.5 entry of \(B\) ignores \(AB\).",
          full, full_alt, ["state-feedback"])
    b.mc(4,
         r"An unreachable mode, under any state feedback \(u = -Kx\),",
         ["moves to whatever eigenvalue you write into the desired polynomial",
          "becomes observable",
          "stays at its open-loop eigenvalue",
          r"is removed from \(A\) by the gain"], 2,
         r"State feedback changes \(A\) only in the directions \(B\) can see. An unreachable eigenvalue is not among them, so it stays put. The desired polynomial cannot include a move you have no actuator for. The mode does not become observable, because observability is about \(C\), and \(K\) does not delete the row of \(A\).",
         short, short_alt, ["state-feedback"])
    b.mc(4,
         r"A transfer-function pole that was cancelled, then kept anyway as an extra state,",
         [r"is always reachable from \(B\)",
          "raises the rank of every controllability matrix to the unreduced degree",
          "changes the DC gain",
          "is unreachable or unobservable, so the realization is not minimal"], 3,
         r"Cancellation means that state does not appear in the input-output map. It is hidden from the input, from the output, or from both. Keeping it makes a non-minimal realization. It does not raise the controllability rank, and deleting it does not change the DC gain of the transfer function that remains.",
         splane([(-1, 0), (-4, 0)], [(-4, 0)], "a pole and a zero on top of each other"),
         "A cross and a circle at the same place on the negative real axis, plus another cross.",
         ["state-feedback"])
    b.save()


def np_det_reach4():
    """Absolute determinant is filled by the caller. This returns the signed det."""
    return -6.25


def expl_reachability():
    fig = plane_vectors([(0.3, 1.0, "B"), (1.2, 0.2, "AB")], "input image and one step under A")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "Two arrows from the origin in clearly different directions.",
        "body_md": r"""Reachability asks whether the input can stir every state. For a linear system the answer is a rank. Line up \(B\), \(AB\), and so on until you have \(n\) blocks. If those columns span \(\mathbb{R}^n\), some input takes any state to any other state in finite time. If the rank \(r\) is short, only an \(r\)-dimensional subspace can be steered. The missing directions are modes the actuator never touches.

The same test is often called controllability. For the continuous-time models in this graph the two words name one rank condition. A coordinate change with an invertible \(T\) multiplies the matrix by \(T^{-1}\) and does not change the rank.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""The controllability matrix is
\[
\mathcal{C} = \begin{bmatrix} B & AB & \cdots & A^{n-1}B \end{bmatrix}.
\]
The pair is reachable when \(\mathrm{rank}\,\mathcal{C} = n\). For two states that is a nonzero determinant. In controllable canonical form the matrix is triangular and invertible, provided no factor was cancelled. A cancelled mode kept as an extra state is unreachable or unobservable.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(A = \begin{bmatrix} 0 & 1 \\ -7.5 & -0.8 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ 1.6 \end{bmatrix}\). Then \(AB = \begin{bmatrix} 1.6 \\ -1.28 \end{bmatrix}\), and
\[
\mathcal{C} = \begin{bmatrix} 0 & 1.6 \\ 1.6 & -1.28 \end{bmatrix}.
\]
The determinant is \(-2.56\). The columns point in different directions, so the pair is reachable. The \(1.6\) in \(B\) scales both columns and does not, by itself, decide the rank. A zero in the top entry of \(B\) is the usual companion pattern, not a missing direction.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""A nonzero \(B\) is not full rank. Two proportional columns still leave a hole. The determinant test is only for a square controllability matrix. In larger systems you count the rank. An unreachable mode is not automatically unstable, and state feedback cannot move it. Coordinate changes do not repair a short rank. And building a canonical form from a transfer function, which an earlier skill does, is not the same as testing the rank of a model you already have.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""State feedback \(u = -Kx\) can place every eigenvalue of \(A - BK\) only when the pair is reachable. The gain is a row you solve for so that the closed-loop characteristic polynomial matches a polynomial you chose. If the rank is short, the unreachable eigenvalues stay where \(A\) put them, no matter what \(K\) you write down.""",
    }]
    return put_explainer("reachability", "Reachability and the input rank test", sections)


# ---------------------------------------------------------------------------
# robust stability
# ---------------------------------------------------------------------------

def bank_robust():
    b = Bank("robust-stability")
    disk = bode_sketch("a loop magnitude used for a robust-stability check")
    disk_alt = "A magnitude sketch that falls, then falls more steeply."
    blocks = series(["P0", "Wm"], "nominal plant with a weight in series")
    blocks_alt = "A nominal plant block followed by a weight block."
    peak = 1 / 1.6
    product = 0.5 * 1.4
    worst = max(0.3 * 2, 0.9 * 0.5)
    room = 1 / 0.5

    b.mc(1,
         r"For \(P = P_0(1 + W_m \Delta)\) with \(\|\Delta\|_\infty \le 1\) and a stable nominal loop, a sufficient robust-stability test is",
         [r"\(|T W_m| < 1\) at every frequency",
          r"\(|S| < 1\) at every frequency",
          r"the plant and the model have the same DC gain",
          r"the phase margin is at least \(30^\circ\)"], 0,
         r"The complementary sensitivity \(T\) maps a relative plant error into a loop perturbation. Keeping \(|T W_m|\) strictly below 1 at every frequency keeps that perturbation inside the small-gain disk. Sensitivity \(S\) is the other closed-loop map. Matching DC gains says nothing at crossover. A phase margin is a nominal number, not a disk test.",
         disk, disk_alt)
    b.num(1,
          r"\(|T|\) peaks at \(1.6\). The largest constant \(|W_m|\) that still passes the strict small-gain test is",
          peak, "1",
          r"The product has to stay below 1, so \(|W_m| < 1/1.6 = " + show(peak) + r"\). The peak of \(|T|\) itself, 1.6, is already larger than 1 and would fail for any weight of that size. Allowing the product to equal 1 is the boundary the strict test does not accept.",
          disk, disk_alt)
    b.num(1,
          r"At one frequency, \(|T| = 0.5\) and \(|W_m| = 1.4\). The product \(|T W_m|\) there is",
          product, "1",
          r"The test multiplies the two magnitudes: \(0.5 \cdot 1.4 = " + show(product) + r"\). That is below 1, so this frequency passes. Adding the two numbers gives 1.9, which is not the small-gain product. Dividing them gives \(1.4/0.5 = 2.8\), the reciprocal of a different arrangement.",
          blocks, blocks_alt)

    b.sym(2,
          r"\(|T|\) peaks at a positive number \(t\). Write the largest \(|W_m|\) that keeps the strict test \(|T W_m| < 1\), as an expression in t.",
          "1/t", {"t": (0.25, 4.0)},
          r"A constant weight passes at every frequency only when it is smaller than \(1/t\). The product \(t\) itself is the peak of \(|T|\), not the allowed weight. The square \(t^2\) has no role in this bound.",
          alternates=["t^-1", "1/(t)"],
          fig=disk, alt=disk_alt)
    b.num(2,
          r"Two frequencies give the products \(0.3 \cdot 2\) and \(0.9 \cdot 0.5\). The number the small-gain test compares with 1 is the larger one, which is",
          worst, "1",
          r"The test is a peak over frequency. \(0.3 \cdot 2 = 0.6\) and \(0.9 \cdot 0.5 = 0.45\), so the peak is " + show(worst) + r". The smaller product, 0.45, is a frequency that passes more easily. The average of the two products is not what \(\|\cdot\|_\infty\) reads.",
          disk, disk_alt)
    b.order(2,
            r"Put these steps in the order you would use to apply the multiplicative robust-stability test.",
            ["Confirm that the nominal loop is stable.",
             "Form the complementary sensitivity T of that nominal loop.",
             "Multiply |T| by the multiplicative weight |W_m| at each frequency.",
             "Pass the test only when that product stays strictly below 1 at every frequency."],
            r"An unstable nominal loop is already a failure, before any disk is drawn. \(T\) is the map the weight multiplies. The product is the quantity the small-gain theorem bounds. The last step is strict: a peak of exactly 1 is not a pass. Checking the weight before you know the loop is stable skips the hypothesis the theorem uses.",
            blocks, blocks_alt)

    b.find_error(3,
                 r"A note looks at a loop whose peak of \(|T W_m|\) is \(1.2\). One step is wrong.",
                 [r"The nominal loop is stable, and \(P = P_0(1 + W_m \Delta)\) with \(\|\Delta\|_\infty \le 1\).",
                  r"The peak product \(1.2\) is greater than 1, so the sufficient test does not pass.",
                  r"Because the test fails, every plant in the disk is unstable.",
                  r"A sufficient test that does not pass leaves the disk undecided: some plants in it may still be stable."],
                 2,
                 r"Failing a sufficient test does not prove the opposite. The peak above 1 says this particular certificate did not go through. It does not say every \(\Delta\) destabilizes the loop. The setup and the arithmetic in the first two steps are right, and the last step is the correct reading of a failed sufficient condition.",
                 reasons=["A failed sufficient test is inconclusive. It does not prove every plant in the disk is unstable.",
                          "A peak of 1.2 still passes, because the test allows any finite product.",
                          "Nominal stability is not required before the product is formed."],
                 correct_reason=0,
                 fig=disk, alt=disk_alt)
    b.mc(3,
         r"The small-gain test passes at low frequency and fails near crossover. The disk",
         ["is robustly stable, because the low-frequency gain is what sets the margins",
          "has not been certified, because the test has to hold at every frequency",
          "is robustly stable as long as the failure is only a few percent",
          "is unstable at every plant inside it"], 1,
         r"\(\|T W_m\|_\infty\) is the peak over all \(\omega\). One failing frequency rejects the certificate. Low-frequency success does not cover crossover. A small overshoot of the bound is still a failed strict test, and a failed test does not prove every plant is unstable.",
         disk, disk_alt)
    b.multi(3,
            r"The nominal loop is stable. Which of these peak products \(|T W_m|\) pass the strict small-gain test?",
            ["0.7", "1.4", "0.95", "1"],
            [0, 2],
            r"The test asks for a peak strictly below 1. Both 0.7 and 0.95 pass. 1.4 fails. A peak of exactly 1 is the boundary the strict inequality does not include.",
            blocks, blocks_alt)

    b.num(4,
          r"The peak of \(|T W_m|\) is currently \(0.5\). The largest factor you can multiply \(|W_m|\) by, and still pass the strict test, is",
          room, "1",
          r"The product scales with the weight. It reaches 1 when the weight has grown by \(1/0.5 = " + show(room) + r"\). The strict test wants a factor smaller than that. Doubling the weight once more, a factor of 4, would push the peak to 2.",
          disk, disk_alt, ["robust-perf"])
    b.mc(4,
         r"The product \(|T W_m|\) stays below 1, but the nominal loop is unstable. The small-gain theorem",
         ["certifies every plant in the disk, because the product is what matters",
          "certifies the nominal plant and nothing else",
          "does not apply, because it assumes the nominal loop is stable",
          "becomes a necessary and sufficient test in this case"], 2,
         r"The theorem starts from a stable nominal loop and a small enough perturbation. An unstable nominal loop has already failed, and a small product does not repair it. The test does not become necessary and sufficient just because the nominal loop is unstable.",
         blocks, blocks_alt, ["robust-perf"])
    b.mc(4,
         r"A robust-performance question, after robust stability is settled, asks whether",
         ["the open-loop poles can be renamed",
          r"the Nyquist plot can be drawn without \(T\)",
          "every plant in the disk has the same phase margin number",
          "the tracking error stays inside its bound for every plant in the disk, not only for the nominal plant"], 3,
         r"Robust stability keeps every plant in the disk stable. Robust performance asks for the error bound on that whole set. Renaming poles is not a performance test. The phase margin is one nominal number, not the disk's tracking spec.",
         disk, disk_alt, ["robust-perf"])
    b.save()


def expl_robust():
    fig = bode_sketch("magnitude sketch for a robust-stability weight")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A magnitude sketch that starts shallow and then falls more steeply.",
        "body_md": r"""Robust stability asks whether every plant in a set, not only the model you designed on, keeps the loop stable. The set used here is a disk around a nominal plant \(P_0\): \(P = P_0(1 + W_m \Delta)\) with \(\|\Delta\|_\infty \le 1\). The weight \(W_m\) says how large a relative error you are allowing at each frequency. It was built in an earlier skill. This skill uses it.

The test is sufficient. If it passes, every plant in the disk gives a stable loop. If it fails, you have not proved that some plant is unstable. You have only learned that this certificate was too coarse.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""Let \(T = L/(1+L)\) be the complementary sensitivity of the nominal loop, and assume that loop is stable. Then
\[
\|T W_m\|_\infty < 1
\]
is enough for robust stability. In words, \(|T(j\omega) W_m(j\omega)| < 1\) at every \(\omega\). The largest constant weight that survives a peak of \(|T|\) equal to \(t\) is anything strictly below \(1/t\).""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Suppose \(|T|\) peaks at 0.48 and, at that same frequency, the weight you are considering has magnitude 0.85. The product is \(0.48 \cdot 0.85 = 0.408\), which is below 1. If every other frequency is no worse, the strict test passes and the disk is robustly stable. The same peak would cross 1 if the weight grew past \(1/0.48\). The test would then stop certifying the disk, without by itself proving that a plant inside it is unstable.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""A product of 1 is not a pass. The inequality is strict. A failure is not a proof that every plant is unstable. The theorem also refuses to start from an unstable nominal loop, no matter how small the weight is. And the peak is over every frequency: a comfortable margin at low frequency does not cancel a failure near crossover. Do not rebuild the weight here. Use the \(W_m\) you were given and test \(T\) against it.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""Stability of every plant in the disk is the first half of a robust design. The next question is whether the tracking error, or another performance signal, stays inside its bound for every one of those plants. That is robust performance, and it uses a second weight on the error. A loop that is robustly stable can still miss that bound.""",
    }]
    return put_explainer("robust-stability", "Robust stability and the small-gain test", sections)


# ---------------------------------------------------------------------------
# root locus
# ---------------------------------------------------------------------------

def bank_root_locus():
    b = Bank("root-locus")
    branch = root_locus(
        [[(0, 0), (-3, 0), (-6, 0)]],
        "a real-axis branch between two poles",
        poles=[(0, 0), (-6, 0)],
    )
    branch_alt = "A real-axis segment joining two pole marks, with the imaginary axis marked."
    triple = root_locus(
        [],
        "three real poles",
        poles=[(-1, 0), (-4, 0), (-7, 0)],
    )
    triple_alt = "Three pole marks on the negative real axis."
    pair = root_locus(
        [],
        "a complex conjugate pair",
        poles=[(-2, 2), (-2, -2)],
    )
    pair_alt = "Two pole marks, one above the real axis and one below, at the same real part."
    marked = splane([(0, 0), (-2, 0), (-8, 0)], [(-4, 0)], "three poles and one zero")
    marked_alt = "Three crosses and one circle on the real axis."
    k_break = 9.0
    centroid = (-1 + -4 + -7) / 3
    asymptote = 180.0 / 3
    departure = 180.0 - 90.0

    b.mc(1,
         r"For positive gain, a root-locus branch",
         ["starts at an open-loop pole and ends at an open-loop zero or at infinity",
          "starts at an open-loop zero and ends at an open-loop pole",
          "stays on the imaginary axis for every gain",
          "exists only for systems with no zeros"], 0,
         r"At \(K = 0\) the closed-loop poles are the open-loop poles, so each branch starts there. As \(K\) grows, a branch ends at a zero or, if there are more poles than zeros, runs to infinity along an asymptote. The opposite direction is the negative-gain locus. Branches are not confined to the imaginary axis, and zeros are allowed.",
         branch, branch_alt)
    b.num(1,
          r"The plant is \(1/(s(s+6))\). At the breakaway on the real axis, the positive gain \(K\) is",
          k_break, "1",
          r"The closed-loop equation is \(s(s+6) + K = 0\), so \(K = -s(s+6)\). Setting the derivative \(-2s - 6\) to zero puts the breakaway at \(s = -3\), and \(K = 3 \cdot 3 = " + show(k_break) + r"\). The point \(-3\) is the location, not the gain. The pole spacing 6 is not the gain either.",
          branch, branch_alt)
    b.num(1,
          r"Open-loop poles sit at \(-1\), \(-4\), and \(-7\), with no zeros. The centroid of the asymptotes is",
          centroid, "1",
          r"With three poles and no zeros, the centroid is \((-1-4-7)/3 = " + show(centroid) + r"\). The average of the two outer poles, \((-1-7)/2 = -4\), happens to match here, but the rule uses every pole and zero. The middle pole \(-4\) is one mark, not automatically the centroid.",
          triple, triple_alt)

    b.sym(2,
          r"Two real poles sit at the signed locations \(p\) and \(q\), and there are no zeros. Write the centroid of the asymptotes in the names p and q.",
          "(p+q)/2", {"p": (-8.0, -0.2), "q": (-8.0, -0.2)},
          r"The centroid is \((\sum p - \sum z)/(n-m)\). Here that is \((p+q)/2\). The difference \(p-q\) is the gap between the poles, not the center. The product \(pq\) is the constant term of the polynomial, not the centroid.",
          alternates=["0.5*(p+q)", "(q+p)/2"],
          fig=triple, alt=triple_alt)
    b.num(2,
          r"A positive-gain locus has three more poles than zeros. The smallest positive asymptote angle, in degrees, is",
          asymptote, "deg",
          r"The angles are \((2q+1)180^\circ/(n-m)\). For \(n-m = 3\) the smallest positive one is \(180/3 = " + show(asymptote) + r"\) degrees. The even spacing \(360/3 = 120\) belongs to a different count. An angle of \(90^\circ\) would be the first asymptote of a four-pole excess.",
          triple, triple_alt)
    b.order(2,
            r"Put these steps in the order you would use to start a positive-gain root-locus sketch.",
            ["Mark the open-loop poles and zeros.",
             "Mark the real-axis segments that have an odd count of real poles and zeros to their right.",
             "Draw the asymptotes from the centroid at the odd multiples of 180 degrees over the pole excess.",
             "Place breakaways and departure angles, then sketch each branch from its pole to a zero or to infinity."],
            r"The poles and zeros are the endpoints, so they come first. The real-axis rule uses those marks. Asymptotes need the same count of poles and zeros. Breakaways and departures are local refinements you add before you draw the branches. Drawing the branches before the endpoints have been marked has nothing to connect.",
            branch, branch_alt)

    b.find_error(3,
                 r"A sketch of a plant with poles at \(0\) and \(-4\), and no zeros, claims the following. One step is wrong.",
                 [r"There are two poles and no zeros, so two branches run to infinity.",
                  r"The centroid is \((0 + (-4))/2 = -2\).",
                  r"For positive gain the asymptotes leave that centroid at \(0^\circ\) and \(180^\circ\).",
                  r"The positive-gain angles are the odd multiples of \(180^\circ/(n-m)\), which here are \(90^\circ\) and \(270^\circ\)."],
                 2,
                 r"Two branches and a centroid at \(-2\) are right. Positive-gain asymptotes use odd multiples of \(180^\circ/(n-m)\), so \(90^\circ\) and \(270^\circ\). The angles \(0^\circ\) and \(180^\circ\) are the even multiples, which belong to negative gain. The last step states the rule that the third step broke.",
                 reasons=["Positive-gain asymptotes are the odd multiples of 180 degrees over the pole excess, not 0 and 180.",
                          "A two-pole plant has one asymptote, so the first step is the flawed one.",
                          "The centroid of poles at 0 and -4 is 0, so the second step is the flawed one."],
                 correct_reason=0,
                 fig=branch, alt=branch_alt)
    b.mc(3,
         r"A test point on the real axis lies on the positive-gain locus when",
         ["every open-loop pole is to its left",
          "the number of real poles and zeros to its right is odd",
          "it is exactly halfway between two poles",
          "the point is in the right half-plane"], 1,
         r"Count real poles and real zeros strictly to the right of the test point. An odd count means the angle contribution is \(180^\circ\), which is what positive gain needs. Poles to the left do not enter that count. The midpoint is a breakaway only when the gain derivative vanishes there. The right half-plane is not the rule.",
         marked, marked_alt)
    b.multi(3,
            r"Poles are at \(0\), \(-2\), and \(-8\), and there is a zero at \(-4\). Which of these real points lie on the positive-gain locus?",
            [r"\(-1\)", r"\(-3\)", r"\(-6\)", r"\(-10\)"],
            [0, 2],
            r"Count real poles and zeros to the right. At \(-1\) only the pole at 0 is to the right, an odd count, so it is on the locus. At \(-3\) the pole at 0 and the pole at \(-2\) give an even count. At \(-6\) those two poles plus the zero at \(-4\) give three, which is odd. At \(-10\) all four marks are to the right, an even count.",
            marked, marked_alt)

    b.num(4,
          r"A complex pole sits at \(-2+j2\), its conjugate is the only other open-loop pole, and there are no zeros. The positive-gain departure angle from \(-2+j2\), in degrees, is",
          departure, "deg",
          r"The vector from the conjugate up to \(-2+j2\) is vertical, so its angle is \(90^\circ\). Departure is \(180^\circ\) minus the angles of the other poles, plus the angles of the zeros. With no zeros that is \(180 - 90 = " + show(departure) + r"\) degrees. Using \(180 + 90\) adds the conjugate instead of subtracting it.",
          pair, pair_alt, ["loop-shaping"])
    b.mc(4,
         r"A branch that crosses the imaginary axis as gain increases",
         ["stays stable for every larger gain",
          "has met a zero, so it stops",
          "marks a gain past which that closed-loop pole is unstable",
          "is an asymptote and cannot be a finite branch"], 2,
         r"Closed-loop poles in the right half-plane are unstable. The crossing is the gain where that pole's real part changes sign. Larger gain does not bring it back unless another rule says so. The branch can cross without ending on a zero, and a finite branch is allowed to be the one that crosses.",
         pair, pair_alt, ["fund-limits"])
    b.mc(4,
         r"A root-locus sketch is the right picture when you want to see",
         [r"the Nyquist plot's encirclements of \(-1\)",
          "the Bode phase at one frequency",
          "the delay margin in seconds",
          "how every closed-loop pole moves as one gain runs from zero to infinity"], 3,
         r"The locus is parameterized by that gain. Bode and Nyquist freeze the gain and sweep frequency. Delay margin is a frequency-domain number. The locus is the gain sweep of the closed-loop poles.",
         branch, branch_alt, ["robust-stability"])
    b.save()


def expl_root_locus():
    fig = root_locus(
        [[(-1.5, 0), (-5, 0), (-8.5, 0)]],
        "a breakaway between two real poles",
        poles=[(-1.5, 0), (-8.5, 0)],
    )
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A real-axis segment joining two pole marks.",
        "body_md": r"""The root locus draws the closed-loop poles as one gain \(K\) runs from zero to infinity. Each branch starts at an open-loop pole, because that is where the closed-loop poles sit when \(K = 0\). It ends at an open-loop zero, or it runs to infinity when there are more poles than zeros.

You sketch it from a few rules instead of solving the characteristic equation at every gain. The real-axis rule, the asymptotes, the breakaway points, and the departure angles are enough to see whether a branch is heading into the right half-plane.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""Positive gain means \(1 + KG(s) = 0\). A real test point is on that locus when an odd number of real poles and zeros lie to its right. With \(n\) poles and \(m\) zeros the asymptote angles are
\[
\frac{(2q+1)\,180^\circ}{n-m},
\]
and they meet at the centroid \((\sum p - \sum z)/(n-m)\). A breakaway on the real axis is a repeated root, where \(dK/ds = 0\). The departure angle from a pole is \(180^\circ\) minus the angles of the vectors from the other poles, plus the angles of the vectors from the zeros.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take poles at \(-1.5\) and \(-8.5\), and no zeros. They meet on the real axis at the midpoint \(-5\). The gain on \(1/((s+1.5)(s+8.5))\) is \(K = -(s+1.5)(s+8.5)\). At \(s = -5\) that product of distances is \(3.5 \cdot 3.5\), so \(K = 17.5\). Past that gain the two branches leave the real axis as a complex pair. The centroid of the asymptotes is the same point, \(-5\), and the positive-gain asymptotes are the vertical lines through it.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The angles \(0^\circ\) and \(180^\circ\) for a two-pole excess are the negative-gain locus. Positive gain uses the odd multiples, \(90^\circ\) and \(270^\circ\). The real-axis count includes zeros, not only poles, and it counts marks to the right, not to the left. A departure angle forgets a zero's contribution if you only subtract pole angles. And the locus shows poles against gain. It does not replace a Nyquist plot, which sweeps frequency at a fixed gain.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""Seeing where a branch crosses the imaginary axis tells you the gain a loop shape cannot exceed. Lead and lag then move that picture by adding their own poles and zeros. The same crossing is one way to meet the bandwidth limits that right-half-plane zeros and delays impose, and a disk of plant uncertainty is stable only when every nearby locus stays in the left half-plane.""",
    }]
    return put_explainer("root-locus", "Root locus rules", sections)


# ---------------------------------------------------------------------------
# system identification
# ---------------------------------------------------------------------------

def bank_sys_id():
    b = Bank("sys-id")
    step = step_response("a held step and its settling output", tau=1.2, goal=2.5, t_end=8)
    step_alt = "A step in the input and an output that rises toward a constant."
    fit = bode([(0.2, 12), (1, 8), (3, 2), (8, -6)], "a measured magnitude that rolls off")
    fit_alt = "A magnitude curve that is flat at low frequency and then falls."
    gain = 10 / 4
    theta = (1 * 2 + 2 * 4 + 3 * 7) / (1 + 4 + 9)
    mag = 6 / math.sqrt(1 + 4)
    residual = 11.4 - 2.5 * 4

    b.mc(1,
         r"A held step that has clearly settled identifies",
         ["the DC gain, as the ratio of the two settled changes",
          "every pole, including poles far above the length of the record",
          "the phase margin of a loop you have not closed",
          "a unique state-space realization"], 0,
         r"Once both records have stopped moving, their change ratio is the DC gain of a stable plant. A fast pole can finish long before the first sample you kept, so the step does not name it. Phase margin needs a loop. Many state-space models share one input-output gain.",
         step, step_alt)
    b.num(1,
          r"A held input step changes by 4, and the settled output changes by 10. The DC gain is",
          gain, "1",
          r"The gain is the ratio of the settled changes, \(10/4 = " + show(gain) + r"\). The output change alone, 10, still has the input size in it. The sum \(10+4 = 14\) is not a gain.",
          step, step_alt)
    b.num(1,
          r"Three pairs \((u, y)\) are \((1, 2)\), \((2, 4)\), and \((3, 7)\), and the model is \(y = \theta u\) with no offset. The least-squares \(\theta\) is",
          theta, "1",
          r"The through-origin formula is \(\theta = \sum uy / \sum u^2\). The numerator is \(1\cdot 2 + 2\cdot 4 + 3\cdot 7 = 31\) and the denominator is \(1+4+9 = 14\), so \(\theta = " + show(theta) + r"\). Averaging the three ratios \(2, 2, 7/3\) weights the points differently. Dividing the sums \(\sum y / \sum u = 13/6\) is not the normal equation.",
          step, step_alt)

    b.sym(2,
          r"A first-order model has DC gain \(k > 0\) and time constant \(\tau > 0\). Write its magnitude at frequency \(w > 0\), in the names k, w, and tau.",
          "k/sqrt(1+(w*tau)^2)", {"k": (0.3, 5.0), "w": (0.2, 5.0), "tau": (0.2, 4.0)},
          r"The magnitude of \(k/(\tau s + 1)\) on \(s = jw\) is \(k/\sqrt{1+(w\tau)^2}\). Dropping the square root leaves the square of the denominator and is not the modulus. The product \(k w \tau\) is not a magnitude.",
          alternates=["k/(1+(w*tau)^2)^0.5"],
          fig=fit, alt=fit_alt)
    b.num(2,
          r"A one-pole model has DC gain 6, and at the frequency you measured, \(\omega \tau = 2\). The magnitude \(|G(j\omega)|\) is",
          mag, "1",
          r"\(|G| = 6/\sqrt{1+2^2} = 6/\sqrt{5} = " + show(mag) + r"\). The DC gain 6 is the magnitude only at \(\omega = 0\). Dividing by \(1+2 = 3\) gives 2, which drops the square and the square root.",
          fit, fit_alt)
    b.order(2,
            r"Put these steps in the order you would use to fit a first-order model from a step and a frequency check.",
            ["Hold a step long enough that the output stops moving, and read the DC gain from the two settled changes.",
             "Read a time constant from the rising record, or from the frequency where the magnitude has fallen by 3 dB.",
             "Predict the record with that model and look at the residual.",
             "Check the same model on a record you did not use to pick the numbers."],
            r"The settled step gives the gain only after the transient has died. The time constant comes next, from the shape or from the corner. A residual on the fitting record shows whether the model misses something systematic. A held-out record is the check that the fit was not just memorizing the first experiment. Reading a time constant before the record has settled mixes the gain into the transient.",
            step, step_alt)

    b.find_error(3,
                 r"A fit uses the pairs \((1, 3)\), \((3, 7)\), and \((5, 9)\) in the model \(y = \theta u\). One step is wrong.",
                 [r"The normal equation for a line through the origin is \(\theta \sum u^2 = \sum uy\).",
                  r"Here \(\sum u^2 = 1+9+25 = 35\) and \(\sum uy = 3+21+45 = 69\).",
                  r"Therefore \(\theta = 35/69\).",
                  r"A residual is the measured \(y\) minus \(\theta u\), and a held-out pair can still reject this \(\theta\)."],
                 2,
                 r"The normal equation and the two sums are right: \(35\theta = 69\), so \(\theta = 69/35\), not \(35/69\). Inverting the fraction swaps the estimate with its reciprocal. The last step is the right definition of a residual and of a held-out check.",
                 reasons=["The normal equation gives theta = (sum u y) / (sum u squared), the reciprocal of the fraction in that step.",
                          "The sums 35 and 69 are swapped, so the second step is the flawed one.",
                          "A residual is theta times u, so the last step is the flawed one."],
                 correct_reason=0,
                 fig=step, alt=step_alt)
    b.mc(3,
         r"A least-squares fit can hide a bad model when",
         ["the residual on the fitting record is large and systematic",
          "the residual on the fitting record is small, but a held-out record is large",
          "the regressor matrix has more rows than columns",
          "the parameters appear linearly"], 1,
         r"The fit minimizes the residual on the records it sees. A small fitting residual only says the model matched those rows. A held-out record that the model misses is the warning. Extra rows are what make the problem overdetermined, which is the usual case. Linearity in the parameters is what lets least squares apply. It is not a failure.",
         step, step_alt)
    b.multi(3,
            r"Which of these experiments can identify the DC gain of a stable plant?",
            ["A step held until the output settles, using the ratio of the two changes",
             "One sample taken during a short pulse, before anything has settled",
             "The low-frequency magnitude of a measured frequency response, where the phase is near zero",
             "The height of a resonant peak"],
            [0, 2],
            r"A settled step ratio is the DC gain, and so is the low-frequency magnitude when the phase is near zero and the plant is stable. One sample of a pulse still contains the transient. A resonant peak is a mid-band feature, not the gain at \(\omega = 0\).",
            fit, fit_alt)

    b.num(4,
          r"A model with gain \(2.5\) predicts \(10\) for an input of \(4\). The measured output is \(11.4\). The residual is",
          residual, "1",
          r"The residual is measured minus predicted, \(11.4 - 10 = " + show(residual) + r"\). The prediction 10 is not the residual. The input 4 is the regressor, not the error.",
          step, step_alt, ["adaptive"])
    b.mc(4,
         r"A step test that looks first-order can still be wrong because",
         ["least squares cannot fit a gain",
          "a settled record has no DC gain",
          "a fast pole can die before the samples you kept, so the record never shows it",
          "the normal equations require the output to be a sinusoid"], 2,
         r"A pole that is much faster than the sample interval finishes inside the first step of the record. The gain you read is real, and the missing pole is not. Least squares can fit the gain. A settled record is exactly where the DC gain lives. The normal equations do not ask for a sine wave.",
         step, step_alt, ["adaptive"])
    b.mc(4,
         r"An adaptive update, once you have a model that is linear in its parameters,",
         ["replaces the experiment with a single offline matrix inverse and then freezes the parameters",
          "needs the plant to be a static gain",
          "throws away the regressor and keeps only the residual sign",
          "can keep revising those parameters as new input and output samples arrive"], 3,
         r"Adaptation is the same linear-in-parameters model with the fit allowed to move. New rows of the regressor keep arriving, and the parameter estimate is updated instead of being frozen after one batch. The plant can be dynamic. The residual is more than its sign, and the regressor is the object the update multiplies.",
         fit, fit_alt, ["adaptive"])
    b.save()


def expl_sys_id():
    fig = step_response("a step record used to read a gain", tau=0.8, goal=1.8, t_end=6)
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "An output that rises smoothly and levels off.",
        "body_md": r"""System identification turns input and output records into a model. The model in this skill is linear in its parameters, so the fit is a least-squares problem. A first-order plant is the running example: one number for the DC gain and one number for the time constant. The same arithmetic fits any model you can write as \(y = \Phi \theta\), with a regressor \(\Phi\) built from the records.

A step that has settled is enough for the gain. It is a poor instrument for a fast pole, which can vanish before your samples start. A frequency sweep sees that pole as a change in magnitude and phase. Either way, the residual and a held-out record decide whether the model is any good.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""A line through the origin, \(y = \theta u\), has the scalar normal equation \(\theta = \sum uy / \sum u^2\). With several parameters the same statement is \(\Phi^T \Phi \theta = \Phi^T y\). The magnitude of a one-pole model \(k/(\tau s + 1)\) is
\[
\frac{k}{\sqrt{1 + (\omega \tau)^2}}.
\]
The residual on a sample is the measured output minus the model's prediction. A held-out record is a set of rows that were not used to choose \(\theta\).""",
    }, {
        "heading": "Worked example",
        "body_md": r"""A candidate model has gain 1.8. On a fresh input of 3.5 it predicts \(1.8 \cdot 3.5 = 6.3\). The measured output on that same input is 6.45, so the residual is \(6.45 - 6.3 = 0.15\). That one sample is small beside the prediction, which is encouraging, and it is not a proof. A second held-out record with a residual that is large and shaped like the input would still reject the gain.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""Inverting the normal equation, \(\sum u^2 / \sum uy\), returns the reciprocal of the gain. Averaging the ratios \(y/u\) is a different estimator from the least-squares formula. Reading a time constant from a step that has not settled mixes the unknown gain into the slope. And a small residual on the fitting record does not protect you from a fast pole the experiment never excited. The data matrix in this skill is \(\Phi\). It is not the state matrix of a realization.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""A batch fit freezes \(\theta\) when the records end. An adaptive law keeps the same linear parameterization and updates \(\theta\) as new samples arrive, using the residual as the driving signal. The experiment design does not go away. If the regressor never sees a mode, the update cannot invent it.""",
    }]
    return put_explainer("sys-id", "Identifying a model from input and output records", sections)


# ---------------------------------------------------------------------------
# time delay
# ---------------------------------------------------------------------------

def bank_time_delay():
    b = Bank("time-delay")
    phase_pts = [(w, -w * 0.03 * 180 / math.pi) for w in (1, 3, 6, 9, 12)]
    phase = bode([(1, 0), (12, 0)], "flat magnitude and a falling phase", phase=phase_pts)
    phase_alt = "A flat magnitude trace and a phase trace that falls as frequency rises."
    pade = splane([(-8, 0)], [(8, 0)], "a Padé pole and zero")
    pade_alt = "A cross in the left half-plane and a circle in the right half-plane, equally far from the origin."
    blocks = series(["delay", "P"], "a delay in series with the plant")
    blocks_alt = "A delay block followed by a plant block."
    lag_deg = 0.04 * 10 * 180 / math.pi
    pole = -2 / 0.25
    margin = (50 * math.pi / 180) / 8
    mag = 1.0

    b.mc(1,
         r"A pure delay of \(T_d\) seconds has the transfer function",
         [r"\(e^{-s T_d}\), with magnitude 1 at every frequency",
          r"\(1/(T_d s + 1)\), a left-half-plane pole",
          r"\(e^{+s T_d}\), a growing exponential",
          r"a sample-and-hold with period \(T_d\)"], 0,
         r"The delay shifts the signal and does not change its size, so the magnitude is 1 and the phase is \(-\omega T_d\) radians. A real pole would change the magnitude. The growing exponential is the advance, not the delay. A sample period is a discrete-time quantity and is not this transfer function.",
         blocks, blocks_alt)
    b.num(1,
          r"A delay of \(0.04\) seconds is read at \(10\ \mathrm{rad/s}\). The phase lag, as a positive number of degrees, is",
          lag_deg, "deg",
          r"The phase is \(-\omega T_d\) radians. The lag is \(0.04 \cdot 10 = 0.4\) radians, which is \(0.4 \cdot 180/\pi = " + show(lag_deg) + r"\) degrees. Reporting 0.4 as degrees skips the conversion. Reporting \(\omega T_d\) in radians is the right angle only when the unit asked for is radians.",
          phase, phase_alt)
    b.num(1,
          r"The first-order Padé model of a \(0.25\) second delay has its pole at",
          pole, "rad/s",
          r"The model is \((1 - s T_d/2)/(1 + s T_d/2)\). The pole is at \(-2/T_d = -2/0.25 = " + show(pole) + r"\). The zero is the mirror, at \(+8\), in the right half-plane. The delay itself, 0.25, is not a pole.",
          pade, pade_alt)

    b.sym(2,
          r"Write the phase, in radians, of \(e^{-s T_d}\) at frequency \(w\), in the names w and td. \(T_d\) is the name td.",
          "-w*td", {"w": (0.2, 5.0), "td": (0.2, 5.0)},
          r"On \(s = jw\) the exponent is \(-jw\cdot td\), so the phase is \(-w\cdot td\) radians. The positive product \(w\cdot td\) is the lag, not the signed phase. Dividing by \(w\) returns the delay, which is not an angle.",
          alternates=["-(w*td)", "-td*w"],
          fig=phase, alt=phase_alt)
    b.num(2,
          r"A loop has a phase margin of \(50^\circ\) at a crossover of \(8\ \mathrm{rad/s}\). The delay margin, in seconds, is",
          margin, "s",
          r"Convert the margin to radians before dividing by the crossover. \(50 \cdot \pi/180\) radians, divided by 8, is " + show(margin) + r" seconds. Dividing the degree number by the crossover, \(50/8 = 6.25\), treats degrees as radians and overstates the delay the loop can tolerate.",
          blocks, blocks_alt)
    b.order(2,
            r"Put these steps in the order you would use to check how much delay a loop can take.",
            ["Read the phase margin and the crossover frequency of the delay-free loop.",
             "Convert the phase margin from degrees to radians.",
             "Divide that radian margin by the crossover frequency.",
             "Treat the result as the extra delay that uses up the margin."],
            r"The margin and the crossover are the two measurements. Degrees have to become radians because the delay formula multiplies \(\omega\) by seconds and gets radians. Dividing then converts that angle into a time. The last step is what the number means. Dividing degrees by the crossover skips the conversion and quotes a time that is too long by \(180/\pi\).",
            phase, phase_alt)

    b.find_error(3,
                 r"A calculation treats a delay of \(0.2\) seconds at \(5\ \mathrm{rad/s}\). One step is wrong.",
                 [r"The transfer function of the delay is \(e^{-s T_d}\).",
                  r"Its magnitude at every finite frequency is 1.",
                  r"At this frequency the phase is \(-1\) degree.",
                  r"A first-order Padé model of the same delay has a right-half-plane zero and a left-half-plane pole."],
                 2,
                 r"\(\omega T_d = 5 \cdot 0.2 = 1\) radian, not 1 degree. The phase is \(-1\) radian, about \(-57.3\) degrees. The transfer function and the unit magnitude are right, and the Padé model does have a right-half-plane zero.",
                 reasons=["The product omega times the delay is in radians. Calling that number a degree understates the lag by 180/pi.",
                          "A delay has magnitude 0, so the second step is the flawed one.",
                          "The Padé model has a left-half-plane zero, so the last step is the flawed one."],
                 correct_reason=0,
                 fig=phase, alt=phase_alt)
    b.mc(3,
         r"Compared with the pure delay, the first-order Padé model",
         ["matches the delay's phase at every frequency and adds no zero",
          r"matches the magnitude of 1 at every frequency, and matches the phase only near \(\omega = 0\)",
          "is unstable, because it has a right-half-plane zero",
          "replaces the delay by a sample period"], 1,
         r"The first-order model is an all-pass: magnitude 1 everywhere, like the delay. Its phase matches \(-\omega T_d\) for small \(\omega T_d\) and then levels off, while the pure delay's lag grows without bound. A right-half-plane zero does not make the model itself unstable. The pole is in the left half-plane. A sample period is a different object.",
         pade, pade_alt)
    b.multi(3,
            r"Which statements about a pure delay \(e^{-s T_d}\) are true?",
            ["Its magnitude is 1 at every finite frequency",
             "Its phase lag grows without bound as the frequency grows",
             "It adds a left-half-plane pole to the plant",
             "Its first-order Padé model has a right-half-plane zero"],
            [0, 1, 3],
            r"The magnitude is identically 1, and the phase \(-\omega T_d\) runs to \(-\infty\) as \(\omega\) grows. The delay is not a rational pole. The first-order Padé replacement does have a zero at \(+2/T_d\).",
            blocks, blocks_alt)

    b.num(4,
          r"At \(20\ \mathrm{rad/s}\), a delay of \(0.15\) seconds has magnitude",
          mag, "1",
          r"\(e^{-j\omega T_d}\) lies on the unit circle, so the magnitude is " + show(mag) + r" at every frequency, including \(20\ \mathrm{rad/s}\). The phase lag \(20 \cdot 0.15 = 3\) radians is an angle, not a magnitude. A magnitude of \(e^{-3}\) would be right for a real exponential, not for a pure phase shift.",
          phase, phase_alt, ["fund-limits"])
    b.mc(4,
         r"Extra delay in a loop that was already near \(-180^\circ\) at crossover",
         [r"raises the phase margin by \(\omega_c T_d\)",
          "leaves the phase margin alone, because the magnitude is still 1",
          r"spends phase margin at the rate of \(\omega_c\) radians per second of delay",
          "cancels a right-half-plane zero of the plant"], 2,
         r"Phase falls by \(\omega T_d\) radians. At crossover that subtraction comes straight out of the phase margin, and the magnitude being 1 does not put the phase back. The shift is a loss, not a raise. A delay does not cancel a right-half-plane zero.",
         blocks, blocks_alt, ["loop-shaping"])
    b.mc(4,
         r"A delay makes a robust-stability disk harder to certify because",
         [r"it increases \(|T|\) at low frequency without bound",
          "it removes the nominal loop's stability assumption",
          r"it adds a pole at \(-1/T_d\) that the weight must cover",
          r"the extra phase lag pushes the nominal loop toward the stability boundary, so less room is left for \(|T W_m|\)"], 3,
         r"Delay spends phase and can force \(|T|\) to stay large near the new, fragile crossover. The weight then has less room under the small-gain bound. Delay does not make the low-frequency complementary sensitivity grow without bound, it is not automatically an unstable nominal loop, and it is not a pole at \(-1/T_d\).",
         pade, pade_alt, ["robust-stability"])
    b.save()


def expl_time_delay():
    fig = bode(
        [(1, 0), (12, 0)],
        "unit magnitude and a phase that falls in proportion to frequency",
        phase=[(w, -w * 0.12 * 180 / math.pi) for w in (1, 3, 6, 9, 12)],
    )
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A flat magnitude trace and a phase trace that falls as frequency rises.",
        "body_md": r"""A pure delay holds the signal for \(T_d\) seconds and then releases it unchanged. Nothing about the shape is filtered. In the Laplace domain that hold is a factor \(e^{-s T_d}\). On the frequency axis the magnitude is exactly 1, and the phase is a straight lag proportional to frequency.

The symbol \(T_d\) is the delay. It is not a sample period, and it is not a disturbance. Loops feel the lag at crossover, where a few degrees decide the phase margin. A rational stand-in, the Padé model, is what you use when a design tool wants poles and zeros.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""\[
e^{-j\omega T_d} = 1 \cdot e^{-j\omega T_d}.
\]
The phase in radians is \(-\omega T_d\). In degrees, multiply by \(180/\pi\). The first-order Padé model is
\[
\frac{1 - s T_d/2}{1 + s T_d/2},
\]
with a pole at \(-2/T_d\) and a zero at \(+2/T_d\). It is an all-pass. The delay margin of a loop is the phase margin, in radians, divided by the crossover frequency.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(T_d = 0.12\) seconds and read it at \(3\ \mathrm{rad/s}\). The phase is \(-0.36\) radians, which is about \(-20.63\) degrees. The first-order Padé model of this same delay puts its pole at \(-2/0.12 \approx -16.67\ \mathrm{rad/s}\) and its zero at the mirror image, about \(+16.67\ \mathrm{rad/s}\). Near the origin the rational phase tracks the pure delay. Far above the pole the rational phase levels off, while the pure delay keeps falling.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The product \(\omega T_d\) is in radians. Quoting it as degrees understates the lag by \(180/\pi\). The delay margin has the same trap: divide the margin in radians, not in degrees, by \(\omega_c\). A Padé zero in the right half-plane does not mean the approximation is an unstable system. The pole is in the left half-plane and the magnitude is 1. And a sample period, the \(T\) in \(z = e^{sT}\), shifts a sequence by one tick. It is not this transport delay.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""Delay is one of the hard limits on how high a crossover you can ask for. Loop shaping can spend lead to buy some of the phase back, and then the delay spends it again in proportion to the new crossover. The same lag eats the room in a robust-stability test, because a loop that is already close to \(-180^\circ\) has little \(|T|\) left to give a plant disk.""",
    }]
    return put_explainer("time-delay", "Time delay and the Padé model", sections)


def lint():
    banned = re.compile(
        r"niknejad|åström|aström|astrom|murray|feedback systems|ziegler|nichols|\breader\b|§|"
        r"\b(university|professor|textbook|syllabus|berkeley)\b",
        re.I,
    )
    skills = [
        "loop-shaping", "lyapunov", "observability", "reachability",
        "robust-stability", "root-locus", "sys-id", "time-delay",
    ]
    problems = []
    for sid in skills:
        bank = json.load(open(os.path.join(BANK, f"{sid}.json"), encoding="utf-8"))
        exp = json.load(open(os.path.join(EXP, f"{sid}.json"), encoding="utf-8"))
        nfig = 0
        idxs = []
        for q in bank["questions"]:
            blob = json.dumps(q, ensure_ascii=False)
            if banned.search(blob):
                problems.append(f"{q['id']} banned wording")
            if q.get("figure"):
                nfig += 1
            if q["type"] == "mc":
                idxs.append(q["correct_index"])
        if nfig < 9:
            problems.append(f"{sid} only {nfig} figures")
        if len(idxs) % 4 == 0 and idxs:
            counts = Counter(idxs)
            if len(counts) != 4 or len(set(counts.values())) != 1:
                problems.append(f"{sid} MC positions {dict(counts)}")
        wc = words(exp["sections"])
        if not (250 <= wc <= 500):
            problems.append(f"{sid} explainer words {wc}")
        blob = json.dumps(exp, ensure_ascii=False)
        if banned.search(re.sub(r"<svg[\s\S]*?</svg>", "", blob)):
            problems.append(f"{sid} explainer banned wording")
        print(f"{sid}: questions {len(bank['questions'])}, figures {nfig}, MC idx {idxs}, explainer words {wc}")
    if problems:
        print("LINT FAIL")
        for item in problems:
            print(" ", item)
        sys.exit(1)
    print("lint ok")


def main():
    bank_loop_shaping()
    bank_lyapunov()
    bank_observability()
    bank_reachability()
    bank_robust()
    bank_root_locus()
    bank_sys_id()
    bank_time_delay()
    print(
        "words",
        expl_loop_shaping(),
        expl_lyapunov(),
        expl_observability(),
        expl_reachability(),
        expl_robust(),
        expl_root_locus(),
        expl_sys_id(),
        expl_time_delay(),
    )
    lint()


if __name__ == "__main__":
    main()
