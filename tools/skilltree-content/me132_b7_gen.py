#!/usr/bin/env python3
"""Generate ME 132 batch B7 banks and explainers.

Closed-form answers live here. skilltree/verify_me132_b7.py recomputes the
numeric ones with a characteristic-polynomial match, the sensitivity integral,
and the gradient update. Do not import this file from the verifier.
"""
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import block_diagram, bode, bode_sketch, mass_spring, matrix_fig, splane, step_response
from banklib import BANK, EXP, Bank, g, save_explainer, words


def show(x):
    return f"{g(x):.6g}"


def loop(blocks, title, fb="1", sign="-", inp="r", out="y"):
    return block_diagram(blocks, title, feedback=fb, input_label=inp, output_label=out, feedback_sign=sign)


def put_explainer(sid, title, sections):
    for section in sections:
        svg = section.get("figure_svg")
        if svg and "figure" not in section:
            section["figure"] = svg
    save_explainer(sid, title, sections)
    return words(sections)


# ---------------------------------------------------------------------------
# state feedback
# ---------------------------------------------------------------------------

def bank_state_feedback():
    b = Bank("state-feedback")
    fb = loop(["P"], "state feedback around the plant", fb="K")
    fb_alt = "A plant block with a gain K returned and subtracted."
    poles = splane([(-2, 1.2), (-2, -1.2)], [], "a conjugate pair in the open left half-plane")
    poles_alt = "Two cross marks left of the imaginary axis, mirror images of each other."
    companion = matrix_fig([["0", "1"], ["-3", "-1"]], "controllable companion matrix")
    companion_alt = "A 2 by 2 matrix with a 0 and a 1 on the first row."
    mass = mass_spring("mass, spring, damper, and an applied force")
    mass_alt = "A mass tied to a spring and a damper, with a force arrow."

    k_scalar = (3.0 - (-5.0)) / 2.0
    coeff = 2.0 + 8.0
    k1_can = 12.0 - 3.0
    k1_mass = (16.0 - 3.0) / 0.5

    b.mc(1,
         r"State feedback \(u = -Kx\) on \(\dot{x} = Ax + Bu\) replaces the state matrix with",
         [r"\(A - BK\), so the eigenvalues move when the pair is reachable",
          r"\(A\) itself, because \(K\) only rescales the output",
          r"\(BK\), discarding \(A\)",
          r"\(A + BK\), which adds the gain instead of subtracting it"], 0,
         r"The closed loop is \(\dot{x} = (A - BK)x\) plus whatever reference term you add later. The eigenvalues that move are those of \(A - BK\), and a reachable pair is what lets a single \(K\) put them where you ask. Keeping \(A\), replacing \(A\) by \(BK\), or flipping the sign all describe a different law.",
         fb, fb_alt)
    b.num(1,
          r"The scalar plant is \(\dot{x} = 3x + 2u\). The gain \(K\) that places the closed-loop eigenvalue at \(-5\) is",
          k_scalar, "1",
          r"\(3 - 2K = -5\) gives \(2K = 8\), so \(K = " + show(k_scalar) + r"\). Using \(K = 5\) subtracts 10 and lands at \(-7\). Using \(K = 3/2\) cancels the open-loop 3 and lands at 0. The sign error \(3 + 2K = -5\) asks for \(K = -4\), which is the law \(u = +4x\) rather than \(u = -Kx\).",
          fb, fb_alt)
    b.num(1,
          r"The desired poles are \(-2\) and \(-8\). In the monic polynomial \((s+2)(s+8)\), the coefficient of \(s\) is",
          coeff, "rad/s",
          r"\((s+2)(s+8) = s^2 + 10s + 16\). The coefficient of \(s\) is the sum of the pole magnitudes, " + show(coeff) + r". The product 16 is the constant term. The difference \(8-2 = 6\) is neither coefficient. Leaving the polynomial unexpanded does not change the sum.",
          poles, poles_alt)

    b.sym(2,
          r"A scalar plant is \(\dot{x} = a x + b u\) with \(u = -k x\). Write the closed-loop eigenvalue in the names a, b, and k.",
          "a-b*k", {"a": (0.4, 4.0), "b": (0.4, 3.0), "k": (0.4, 4.0)},
          r"Substituting the law gives \(\dot{x} = (a - b k) x\), so the eigenvalue is \(a - bk\). The product \(bk\) is what the gain moves, and the open-loop \(a\) is still there. \(a + bk\) is the sign error from writing \(u = +kx\). \(a - k\) drops the input coefficient \(b\).",
          alternates=["a-k*b", "-b*k+a"],
          fig=fb, alt=fb_alt)
    b.num(2,
          r"In controllable companion form, \(A = \begin{bmatrix} 0 & 1 \\ -3 & -1 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}\). For the desired polynomial \(s^2 + 7s + 12\), the gain entry on the first state is",
          k1_can, "1",
          r"With \(u = -k_1 x_1 - k_2 x_2\), the closed-loop constant term is \(3 + k_1\) and the coefficient of \(s\) is \(1 + k_2\). Matching 12 gives \(k_1 = " + show(k1_can) + r"\). Matching 7 gives the other entry, \(k_2 = 6\), which is not the one asked. Reporting the desired constant term 12 leaves the open-loop 3 uncancelled.",
          companion, companion_alt)
    b.order(2,
            r"Put these pole-placement steps in the order you would do them for a single input.",
            ["Confirm that the controllability matrix has full rank.",
             "Choose the closed-loop poles and write the desired monic characteristic polynomial.",
             "Write the characteristic polynomial of A - BK with the gain entries unknown.",
             "Match coefficients and solve the linear system for K.",
             "Recompute the eigenvalues of A - BK and compare them with the poles you chose."],
            r"Without full rank there is no \(K\) that hits an arbitrary polynomial, so the rank comes first. The desired polynomial is the target, and \(A - BK\) is the polynomial you can actually shape. Matching coefficients is the solve. The last eigenvalue check catches a sign error in \(u = -Kx\).",
            fb, fb_alt)

    b.find_error(3,
                 r"A 2-state plant has eigenvalues \(+2\) and \(-4\), and its controllability matrix has rank 2. One step of this argument is wrong.",
                 [r"One open-loop eigenvalue is \(+2\), so the uncontrolled system is not asymptotically stable.",
                  "The controllability matrix has rank 2, so the pair is reachable.",
                  r"State feedback cannot move an unstable eigenvalue, so every gain \(K\) leaves the closed loop unstable.",
                  r"A reachable pair can place both eigenvalues of \(A - BK\) in the open left half-plane."],
                 2,
                 r"Reachability is the condition under which \(K\) can move every eigenvalue, including the unstable one. The rank statement and the open-loop reading are right, and the last step is the placement fact the rank buys. The third step treats an open-loop unstable pole as immovable, which is the opposite of what full rank means.",
                 reasons=["Full rank means K can move every eigenvalue, including the unstable one.",
                          "An open-loop pole at +2 means the closed loop is unstable for every K.",
                          "A controllability matrix of rank 2 means the input vector is zero."],
                 correct_reason=0,
                 fig=splane([(2, 0), (-4, 0)], [], "one mark in each half-plane"),
                 alt="One cross in the right half-plane and one cross in the left half-plane.")
    b.mc(3,
         r"Ackermann's formula returns the state-feedback gain when",
         ["the plant has at least two inputs",
          r"there is one input and the pair \((A, B)\) is reachable",
          "every open-loop eigenvalue is already stable",
          r"\(A\) is diagonal, so each state is its own mode"], 1,
         r"The formula solves one row \(K\) from the desired characteristic polynomial, which is a determined system exactly for a single input of full controllability rank. Extra inputs make the gain nonunique. Stability of \(A\) is not required, and a diagonal \(A\) is a special coordinate, not the hypothesis.",
         companion, companion_alt)
    b.multi(3,
            r"Which statements hold for \(u = -Kx\) on a reachable single-input pair?",
            [r"Every eigenvalue of \(A - BK\) can be assigned.",
             "The zeros of the transfer function from the input to a fixed output stay where they were.",
             r"The matrix \(B\) is replaced by \(BK\).",
             r"A positive open-loop eigenvalue makes every choice of \(K\) unstable."],
            [0, 1],
            r"Reachability is exactly the right to assign every eigenvalue of \(A - BK\). For one input, that gain changes the denominator and leaves the zeros of \(C(sI-A)^{-1}B\) in place. \(B\) is still the input matrix; \(BK\) is the rank-one update subtracted from \(A\). An unstable open-loop eigenvalue is one of the eigenvalues you are allowed to move.",
            matrix_fig([["A-BK"]], "closed-loop state matrix"),
            "A single matrix label, A minus B K.")

    b.num(4,
          r"A unit mass is 2, the damper coefficient is 4, and the spring coefficient is 6, so \(A = \begin{bmatrix} 0 & 1 \\ -3 & -2 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ 0.5 \end{bmatrix}\). The desired polynomial is \(s^2 + 4s + 16\). The gain entry on the position state is",
          k1_mass, "1",
          r"The input column scales both gain entries by \(0.5\). The closed-loop constant term is \(3 + 0.5 k_1\). Setting that equal to 16 gives \(k_1 = " + show(k1_mass) + r"\). Forgetting the \(0.5\) and subtracting as if \(B\) ended in 1 produces \(16 - 3 = 13\). The coefficient of \(s\) fixes the velocity gain, \(k_2 = 4\), not the position gain. The desired natural-frequency term 16 is the polynomial coefficient, not the gain.",
          mass, mass_alt, ["integral-action"])
    b.mc(4,
         r"The poles of \(A - BK\) sit where you asked, and a constant reference is added as \(u = -Kx + k_r r\). A nonzero constant error in steady state is removed by",
         [r"raising every entry of \(K\) without bound",
          r"deleting a row of \(C\)",
          "augmenting the state with an integrator on the tracking error",
          r"setting the direct term \(D\) to 1"], 2,
         r"Pole placement fixes the transient of \(A - BK\). A constant reference still has to pass through the DC gain, and that gain is 1 only for a particular \(k_r\). An extra state that integrates \(r - y\) is what forces the steady error to zero when the loop is stable. A larger \(K\) moves the poles again. Deleting part of \(C\) changes what you measure, and \(D\) is a feedthrough, not an integrator.",
         fb, fb_alt, ["integral-action"])
    b.mc(4,
         r"The controllability matrix of a 2-state model has rank 1. State feedback then",
         [r"can still place both eigenvalues, because \(K\) has two entries",
          "makes the unreachable mode unstable even if it started stable",
          "is the same design as an observer gain",
          "can move only the reachable eigenvalue; the other one stays at its open-loop value"], 3,
         r"Each missing rank is a direction \(u\) never enters, and \(A - BK\) shares the unreachable eigenvalue with \(A\). Two entries in \(K\) do not create a new direction. The unreachable eigenvalue keeps the real part it already had. An observer gain is built from \(C\), not from this rank.",
         companion, companion_alt, ["separation"])
    b.save()


def expl_state_feedback():
    fig = loop(["P"], "state feedback, gain returned from the state")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A plant block with a gain returned and subtracted at the input summer.",
        "body_md": r"""State feedback uses the whole state, not only the output. The law \(u = -Kx\) adds a rank-one update, and the closed-loop matrix is \(A - BK\). When the pair \((A, B)\) is reachable, that one row \(K\) can put every eigenvalue of \(A - BK\) on a polynomial you chose. The transient, the damping, and the natural frequency are then properties of the polynomial, not of the open-loop \(A\).

The same gain does not invent a new input direction. A mode that failed the rank test stays where \(A\) put it, for every \(K\). Placement is a statement about eigenvalues. It does not, by itself, make the steady error to a constant reference equal to zero.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""With a single input,
\[
\dot{x} = (A - BK) x, \qquad \det(sI - (A - BK)) = s^n + d_{n-1} s^{n-1} + \cdots + d_0.
\]
You pick the \(d_i\) from the desired poles, expand \(\det(sI - (A-BK))\) with the entries of \(K\) unknown, and match coefficients. For a reachable single-input pair the match has one solution. Ackermann's formula is that solution written as one product, using the desired polynomial and the controllability matrix. In controllable companion form the match is a subtraction: each open-loop coefficient is replaced by the desired one, scaled by the bottom entry of \(B\) when that entry is not 1.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(A = \begin{bmatrix} 0 & 1 \\ -2.4 & -0.7 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ 1.6 \end{bmatrix}\). Ask for \(s^2 + 9.5 s + 18.2\). The closed-loop constant term is \(2.4 + 1.6 k_1\), and the coefficient of \(s\) is \(0.7 + 1.6 k_2\). Then \(1.6 k_1 = 15.8\), so \(k_1 = 9.875\), and \(1.6 k_2 = 8.8\), so \(k_2 = 5.5\). The factor \(1.6\) is the input scale. Dropping it would report \(15.8\) and \(8.8\), which are the gaps in the polynomial, not the gains.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""Writing \(u = +Kx\) flips every correction and solves the wrong sign. In companion form it is easy to match the constant term with the velocity gain and the \(s\) coefficient with the position gain; the constant term belongs to the gain on the undifferentiated state. A desired polynomial that is not monic, or that is written as \((s-p_1)(s-p_2)\) with the sign of a left-half-plane pole dropped, shifts every coefficient. And a short controllability rank does not become full rank because \(K\) has several entries.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""A constant reference still needs a path into the law, and a pure gain \(k_r\) sets the DC map without adding a state. An integrator on the tracking error is the later augmentation that removes a constant error. A quadratic cost picks one particular \(K\) instead of a hand-chosen polynomial. When the state is not measured, the same \(K\) is applied to an estimate, and the closed-loop eigenvalues split into the ones you placed here and the ones the estimator placed.""",
    }]
    return put_explainer("state-feedback", "State feedback and pole placement", sections)


# ---------------------------------------------------------------------------
# observer
# ---------------------------------------------------------------------------

def bank_observer():
    b = Bank("observer")
    model = block_diagram(["model"], "model copy with a correction gain", feedback="L",
                          input_label="u", output_label="xhat", feedback_sign="-")
    model_alt = "A model block with a gain L returned and subtracted."
    poles = splane([(-6, 0), (-10, 0)], [], "two real marks in the open left half-plane")
    poles_alt = "Two cross marks on the negative real axis, one farther left than the other."
    mat = matrix_fig([["0", "1"], ["-4", "-3"]], "a 2-state model matrix")
    mat_alt = "A 2 by 2 matrix with a 0 and a 1 on the first row."
    dual = matrix_fig([["1", "0"]], "an output row that reads the first state")
    dual_alt = "A row matrix with entries 1 and 0."

    ell = (-2.0 - (-9.0)) / 4.0
    coeff = 6.0 + 10.0
    # Verified by matching the characteristic polynomial of A - LC.
    l1 = 9.0
    l2 = 11.0

    b.mc(1,
         r"When the model matches the plant and both are driven by the same \(u\), the estimation error \(\tilde{x} = x - \hat{x}\) obeys",
         [r"\(\dot{\tilde{x}} = (A - LC)\tilde{x}\)",
          r"\(\dot{\tilde{x}} = (A - BK)\tilde{x}\)",
          r"\(\dot{\tilde{x}} = LC \tilde{x}\), with no \(A\) left",
          r"\(\tilde{x} = y\), so the error is the measurement"], 0,
         r"The plant and the model share \(A\), \(B\), and \(u\), so those terms cancel in \(x - \hat{x}\). What remains is the correction \(L\) times the output residual, which produces \(A - LC\). The state-feedback matrix \(A - BK\) is a different design. Dropping \(A\), or calling the measurement itself the error, describes a different equation.",
         model, model_alt)
    b.num(1,
          r"The scalar plant is \(\dot{x} = -2x\), \(y = 4x\). The observer gain that places the error eigenvalue at \(-9\) is",
          ell, "1",
          r"\(-2 - 4L = -9\) gives \(4L = 7\), so \(L = " + show(ell) + r"\). Using \(L = 9/4 = 2.25\) forgets that the output is already scaled by 4 and lands at \(-2 - 9 = -11\). Solving \(-2 - 4L = 0\), which only moves the pole to the origin, gives \(L = -0.5\). Forgetting the output scale and solving \(-2 - L = -9\) produces 7, the gap rather than the gain.",
          model, model_alt)
    b.num(1,
          r"The desired error poles are \(-6\) and \(-10\). In the monic polynomial \((s+6)(s+10)\), the coefficient of \(s\) is",
          coeff, "rad/s",
          r"\((s+6)(s+10) = s^2 + 16s + 60\). The coefficient of \(s\) is " + show(coeff) + r", the sum of the pole magnitudes. The product 60 is the constant term. The gap \(10 - 6 = 4\) is not a coefficient. Using only the faster pole, 10, drops the other one.",
          poles, poles_alt)

    b.sym(2,
          r"A scalar plant is \(\dot{x} = a x\), \(y = c x\), and the observer gain is g. Write the eigenvalue of the estimation-error system in the names a, c, and g.",
          "a-g*c", {"a": (-3.0, 2.0), "c": (0.4, 3.0), "g": (0.4, 3.0)},
          r"The error pole is \(a - g c\). The product \(gc\) is the correction, and \(a\) is still the open-loop coefficient. \(a + gc\) is the sign you get by subtracting the residual in the wrong direction. \(a - g\) drops the output scale \(c\).",
          alternates=["a-c*g", "-g*c+a"],
          fig=model, alt=model_alt)
    b.num(2,
          r"Let \(A = \begin{bmatrix} 0 & 1 \\ -4 & -3 \end{bmatrix}\) and \(C = \begin{bmatrix} 1 & 0 \end{bmatrix}\). The desired error polynomial is \(s^2 + 12s + 32\). The gain entry that multiplies the residual into the first state is",
          l1, "1",
          r"With \(L = \begin{bmatrix} l_1 \\ l_2 \end{bmatrix}\), \(A - LC = \begin{bmatrix} -l_1 & 1 \\ -4 - l_2 & -3 \end{bmatrix}\). The coefficient of \(s\) is \(l_1 + 3\), so \(l_1 = " + show(l1) + r"\). The constant term \(3 l_1 + l_2 + 4\) then fixes \(l_2 = 1\), the other entry. Reporting 12 returns the desired coefficient before the open-loop 3 is removed. Reporting 3 returns that open-loop piece alone.",
          dual, dual_alt)
    b.order(2,
            r"Put these observer-design steps in the order you would do them.",
            ["Confirm that the observability matrix has full rank.",
             "Choose error poles faster than the state-feedback poles already placed, and write their monic polynomial.",
             "Write the characteristic polynomial of A - LC with the gain entries unknown.",
             "Match coefficients and solve for L.",
             "Check the eigenvalues of A - LC, and check that L is not so large that sensor noise dominates the correction."],
            r"Observability is what makes an arbitrary error polynomial attainable, so it comes first. The speed relative to the control poles is a design choice you write down before the algebra. Matching coefficients is the solve. The last check is both algebraic and practical: a correct polynomial can still amplify noise if the gain is huge.",
            model, model_alt)

    b.find_error(3,
                 r"The output is \(y = Cx\), the observability matrix has full rank, and the same \(u\) drives the plant and the model. One step is wrong.",
                 [r"The estimate is corrected by \(L\) times the residual \(y - C\hat{x}\).",
                  "Full rank means the eigenvalues of the error system can be assigned.",
                  r"The estimation-error matrix is \(A - BK\), the matrix state feedback uses.",
                  r"When the model matches, a stable \(A - LC\) drives the estimation error to zero."],
                 2,
                 r"The error matrix is \(A - LC\). State feedback builds \(A - BK\) from the input matrix, and that gain does not appear in the error equation when the model matches. The residual update, the rank hypothesis, and the decay of a stable error system are the right pieces.",
                 reasons=["The error matrix is A - LC, built from the output row, not A - BK.",
                          "Full rank of the observability matrix means the error is already zero.",
                          "The residual should be added with no gain at all."],
                 correct_reason=0,
                 fig=model, alt=model_alt)
    b.mc(3,
         r"A usual reason to place the observer poles faster than the state-feedback poles is that",
         ["the observer then cancels the plant zeros",
          "the estimate settles before a law designed for a known state has to act for long on a bad estimate",
          r"\(A - LC\) has to equal \(A - BK\)",
          r"a faster error pole makes the gain \(L\) zero"], 1,
         r"The control law was derived as \(u = -Kx\). While \(\hat{x}\) is still far from \(x\), that law is being fed the wrong vector. A faster error transient shortens that interval. It does not cancel zeros, it does not force the two matrices to be equal, and a faster pole makes \(L\) larger, not zero.",
         poles, poles_alt)
    b.multi(3,
            r"Which statements hold for a linear observer?",
            [r"If \((A, C)\) is observable, every eigenvalue of \(A - LC\) can be assigned.",
             r"If the model uses the wrong \(B\), the input \(u\) still drives the estimation error.",
             r"A larger \(L\) always reduces the effect of sensor noise on the estimate.",
             r"When \(B\) is not zero, the observer equation needs \(u\) as well as \(y\)."],
            [0, 1, 3],
            r"Observability is the dual of reachability, so a full-rank pair can assign every error eigenvalue. An incorrect \(B\) leaves a term in \(u\) inside the error equation, which is why the model has to see the same command the plant sees. A larger \(L\) amplifies sensor noise. And the copy of the plant is \(\dot{\hat{x}} = A\hat{x} + Bu + L(y - C\hat{x})\), so a nonzero \(B\) makes \(u\) part of the update.",
            mat, mat_alt)

    b.num(4,
          r"Let \(A = \begin{bmatrix} 0 & 1 \\ -6 & -1 \end{bmatrix}\) and \(C = \begin{bmatrix} 0 & 1 \end{bmatrix}\). The desired error polynomial is \(s^2 + 12s + 35\). The gain entry that multiplies the residual into the second state is",
          l2, "1",
          r"\(A - LC = \begin{bmatrix} 0 & 1 - l_1 \\ -6 & -1 - l_2 \end{bmatrix}\). The coefficient of \(s\) is \(1 + l_2\), so \(l_2 = " + show(l2) + r"\). The constant term \(6 - 6 l_1\) fixes the other entry, \(l_1 = -29/6\), which is not this question. Adding the desired coefficient to the open-loop 1, getting 13, counts that 1 twice. Using the constant term 35 as a gain ignores the open-loop \(-6\).",
          mat, mat_alt, ["separation"])
    b.mc(4,
         r"State feedback \(u = -K\hat{x}\) is built from this estimate. The eigenvalues of the combined loop are",
         [r"only the eigenvalues of \(A - BK\)",
          r"only the eigenvalues of \(A - LC\)",
          r"the union of the eigenvalues of \(A - BK\) and of \(A - LC\)",
          r"the eigenvalues of \(A\), unchanged"], 2,
         r"When the model matches, a coordinate change splits the closed loop into the state-feedback block and the error block. The spectrum is the union of the two spectra you placed. Either block alone is only half of that spectrum, and the open-loop \(A\) is what you moved away from.",
         model, model_alt, ["separation"])
    b.mc(4,
         r"A later skill keeps this correction structure but chooses the gain from process-noise and sensor-noise intensities. Compared with the gain in this skill,",
         ["that later gain does not use the output",
          "pole placement is optimal for every noise intensity",
          "the error dynamics stop being linear",
          r"this skill picks \(L\) by placing error poles, and the later skill picks \(L\) from the noise intensities"], 3,
         r"Both designs correct a model with a gain times the output residual. Here the numbers in \(L\) come from a polynomial you chose. The later design computes those numbers from the two noise intensities, and that calculation is not the same as an arbitrary pole list. The error system stays linear for a linear plant. The output is still the signal the correction uses.",
         poles, poles_alt, ["kalman"])
    b.save()


def expl_observer():
    fig = block_diagram(["model"], "a model corrected by the output residual", feedback="L",
                        input_label="u", output_label="xhat", feedback_sign="-")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A model block with a gain returned from its output and subtracted.",
        "body_md": r"""An observer is a copy of the model, driven by the same command as the plant, plus a correction when the copy's output disagrees with the measurement. The correction gain is \(L\). If the copy uses the true \(A\), \(B\), and \(C\), the state error \(\tilde{x} = x - \hat{x}\) does not see \(u\) at all. It decays according to \(A - LC\).

Designing \(L\) is pole placement for the pair \((A^\mathsf{T}, C^\mathsf{T})\). Observability is the hypothesis that makes every error polynomial attainable. The estimate is not the measurement. The measurement is one linear combination of the state, and \(L\) reconstructs the rest.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""\[
\dot{\hat{x}} = A\hat{x} + Bu + L(y - C\hat{x}), \qquad \dot{\tilde{x}} = (A - LC)\tilde{x}.
\]
The second equation holds when the model matches and the same \(u\) is used on both sides. You choose a monic polynomial for \(A - LC\), usually with poles a few times faster than the state-feedback poles, expand the determinant, and solve for \(L\). A stable \(A - LC\) sends \(\tilde{x}\) to zero. It does not send sensor noise to zero: a large \(L\) multiplies that noise on its way into the estimate.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take the scalar plant \(\dot{x} = -0.28 x\), \(y = 5x\), and ask for an error pole at \(-8.91\). Then \(-0.28 - 5L = -8.91\), so \(5L = 8.63\) and \(L = 1.726\). The 5 is the output scale. Solving \(-0.28 - L = -8.91\) instead would report 8.63, the gap in the pole, and the error pole would land at \(-0.28 - 5 \times 8.63\), far from \(-8.91\).""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The error matrix is \(A - LC\), not the state-feedback matrix \(A - BK\). Swapping them builds a gain from the wrong vector. The sign of the residual matters: feeding \(C\hat{x} - y\) into a positive \(L\) moves the poles the wrong way. A faster error pole is a choice about settling, not a requirement that \(L\) equal \(K\). And if the model \(B\) is wrong, \(u\) remains inside the error equation, so a gain computed from \(A\) and \(C\) alone no longer describes the decay you will see.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""The estimate is what you substitute into \(u = -K\hat{x}\) when the state is not measured. The combined eigenvalues are then the ones from \(A - BK\) together with the ones from \(A - LC\). A later design keeps the same correction structure and chooses the numbers in \(L\) from process-noise and sensor-noise intensities instead of from a polynomial you wrote down.""",
    }]
    return put_explainer("observer", "Observers and the error gain", sections)


# ---------------------------------------------------------------------------
# fundamental limitations
# ---------------------------------------------------------------------------

def bank_fund_limits():
    b = Bank("fund-limits")
    sens = bode([(0.3, -8), (1, -8), (2, 0), (4, 6), (12, 0)], "sensitivity magnitude, a dip then a hump")
    sens_alt = "A magnitude curve that sits below the axis, crosses up, and comes back."
    sketch = bode_sketch("a magnitude that falls, then falls more steeply")
    sketch_alt = "A magnitude sketch with two downward slopes."
    rhp = splane([(3, 0)], [(11, 0)], "a right-half-plane pole and a right-half-plane zero")
    rhp_alt = "A cross and an open circle, both on the positive real axis, the circle farther out."
    loopfig = loop(["L"], "the loop whose sensitivity is 1 over 1 plus L")
    loop_alt = "A forward block L with unity feedback subtracted."

    peak = math.exp(math.log(4.0) * 2.0 / 4.0)
    integral = math.pi * (1.5 + 3.5)
    hump_w = math.log(2.0) * 9.0 / math.log(8.0)
    window = 20.0 / 2.0 - 2.0 * 2.5

    b.mc(1,
         r"The open loop is stable and \(|L|\) falls at least as fast as \(1/\omega^2\). The integral \(\int_0^{\infty} \ln|S(j\omega)|\,d\omega\) is then",
         [r"zero, so a band where \(|S| < 1\) is paid for by a band where \(|S| > 1\)",
          r"always negative, so feedback reduces \(|S|\) at every frequency",
          "equal to the time delay in seconds",
          "equal to the DC loop gain"], 0,
         r"With no right-half-plane poles and a roll-off of two or more, the signed areas of \(\ln|S|\) cancel. Pushing \(|S|\) below 1 on a band forces it above 1 somewhere else. The integral is not a delay and not a DC gain, and it is not negative for every stable loop: a loop with \(|S| < 1\) everywhere would make the integral negative, which this hypothesis forbids.",
         sens, sens_alt)
    b.num(1,
          r"On a stable loop with the integral equal to zero, \(|S| = 1/4\) on a band of width 2 rad/s, and \(|S|\) is a constant greater than 1 on the next 4 rad/s, and \(|S| = 1\) after that. The constant value on that hump is",
          peak, "1",
          r"The negative area is \(\ln 4 \times 2\). Spread over width 4 it has height \((\ln 4)/2 = \ln 2\), so the hump is " + show(peak) + r". Reporting 4 uses the reciprocal of \(1/4\) and ignores the two widths. Reporting \(1/4\) repeats the dip. Reporting 8 treats the width ratio 2 as a factor on the dip height instead of on the log height.",
          sens, sens_alt)
    b.num(1,
          r"The loop has real right-half-plane poles at 1.5 and 3.5 rad/s, the closed loop is stable, and \(|L|\) falls at least as fast as \(1/\omega^2\). The integral \(\int_0^{\infty} \ln|S(j\omega)|\,d\omega\) equals",
          integral, "rad/s",
          r"The integral equals \(\pi\) times the sum of the real parts, \(\pi(1.5+3.5) = " + show(integral) + r"\). The sum 5 is the factor in front of \(\pi\), not the integral. Twice that sum, 10, would be right for a different constant than \(\pi\). A stable open loop would make the integral 0, and these two poles are what remove that case.",
          rhp, rhp_alt)

    b.sym(2,
          r"The open loop has one real right-half-plane pole at p rad/s, the closed loop is stable, and \(|L|\) falls at least as fast as \(1/\omega^2\). Write \(\int_0^{\infty} \ln|S(j\omega)|\,d\omega\) in the name p. Use pi for \(\pi\).",
          "pi*p", {"p": (0.4, 6.0)},
          r"One real right-half-plane pole contributes its real part times \(\pi\). The integral is \(\pi p\). The product \(2\pi p\) is a full turn, not this integral. The pole alone, \(p\), drops the factor \(\pi\). A right-half-plane zero does not add a term of this kind.",
          alternates=["p*pi"],
          fig=rhp, alt=rhp_alt)
    b.num(2,
          r"The integral of \(\ln|S|\) is zero. \(|S| = 1/2\) on a band of width 9 rad/s, and the recovering hump has height \(|S| = 8\). The width of that hump, in rad/s, is",
          hump_w, "rad/s",
          r"\(\ln(1/2) = -\ln 2\) and \(\ln 8 = 3\ln 2\). The areas cancel when \(9\ln 2 = 3\ln 2 \cdot W\), so \(W = " + show(hump_w) + r"\). Reporting 9 copies the dip width. Reporting 8 copies the hump height. Reporting \(9/2 = 4.5\) uses the dip's factor of 2 and forgets that a height of 8 is three factors of 2 in the log.",
          sens, sens_alt)
    b.order(2,
            r"Put these steps in the order you would use them while choosing a crossover.",
            ["Mark the right-half-plane poles, the right-half-plane zeros, and any time delay.",
             "Keep the intended crossover above the right-half-plane poles, so the loop gain is large enough to stabilize them.",
             "Keep the intended crossover below the right-half-plane zeros, with room before their phase is spent.",
             "Check the sensitivity integral: a deep dip in one band needs a peak in another.",
             "If the lowest right-half-plane zero sits below the highest right-half-plane pole, stop: the two bounds leave no crossover."],
            r"You cannot place a crossover until you know which bounds point up and which point down. The pole is a floor and the zero is a ceiling, so both are checked before the area argument. The integral is the bill for whatever dip you still want. The last step is the case where the floor is above the ceiling and no frequency satisfies both.",
            rhp, rhp_alt)

    b.find_error(3,
                 r"The open loop is stable and rolls off at least as fast as \(1/\omega^2\). One step of this sensitivity argument is wrong.",
                 [r"The integral of \(\ln|S(j\omega)|\) from 0 to \(\infty\) is 0.",
                  r"Holding \(|S|\) at \(0.5\) from 0 to \(5\ \mathrm{rad/s}\) contributes a negative area.",
                  r"Because the total area is 0, \(|S|\) may stay at \(0.5\) at every higher frequency as well.",
                  r"The negative area has to be balanced by a band where \(|S| > 1\)."],
                 2,
                 r"A zero total with a negative piece forces a positive piece. Keeping \(|S|\) at \(0.5\) everywhere would make the whole integral negative, which the roll-off and the stable open loop do not allow. The integral statement, the sign of the dip, and the need for a peak are the right steps.",
                 reasons=["A negative piece of a zero-area integral forces a band where |S| is above 1.",
                          "A stable open loop makes the integral equal to the delay, not zero.",
                          "Holding |S| at 0.5 on a finite band makes every closed loop unstable."],
                 correct_reason=0,
                 fig=sens, alt=sens_alt)
    b.mc(3,
         r"A right-half-plane zero of the plant, left uncancelled so the closed loop can be internally stable,",
         ["is removed by a matching right-half-plane pole in the compensator, and the bandwidth limit goes with it",
          r"forces \(S(z) = 1\) at that zero, so sensitivity cannot be small there",
          r"adds \(\pi z\) to the sensitivity integral of an open-loop-stable plant",
          "forces the crossover to sit above the zero"], 1,
         r"An uncancelled right-half-plane zero of the loop is a point where \(L(z) = 0\), so \(S(z) = 1\). Cancelling it with a compensator pole hides an unstable mode. The \(\pi\) term in the integral belongs to right-half-plane poles, not zeros. The zero is a ceiling on crossover, not a floor.",
         rhp, rhp_alt)
    b.multi(3,
            r"Which statements hold for these limitations?",
            [r"If the sensitivity integral is zero, a band with \(|S| < 1\) forces another band with \(|S| > 1\).",
             r"A right-half-plane pole of the loop increases \(\int \ln|S|\,d\omega\).",
             r"A right-half-plane zero of a stable loop adds that same \(\pi\) term to the integral.",
             "A time delay makes the high-frequency phase more negative, so the same crossover budget gets tighter."],
            [0, 1, 3],
            r"The zero-area case is the waterbed: the dip is paid for by a peak. Right-half-plane poles add \(\pi\) times their real parts. A right-half-plane zero does not add that term; it constrains \(S\) by interpolation instead. Delay spends phase in proportion to frequency, which shrinks the crossover you can still afford.",
            sketch, sketch_alt)

    b.num(4,
          r"Use the design window \(\omega_c \ge 2p\) and \(\omega_c \le z/2\), with a real right-half-plane pole at \(p = 2.5\ \mathrm{rad/s}\) and a real right-half-plane zero at \(z = 20\ \mathrm{rad/s}\). The width of the allowed crossover interval, in rad/s, is",
          window, "rad/s",
          r"The floor is \(2 \times 2.5 = 5\) and the ceiling is \(20/2 = 10\), so the width is " + show(window) + r". Reporting 10 returns the ceiling alone. Reporting 2.5 returns the pole. Reporting 20 returns the zero. The window is the gap between the floor and the ceiling, and it is nonempty here.",
          rhp, rhp_alt, ["robust-perf"])
    b.mc(4,
         r"The right-half-plane pole sits at a higher frequency than the right-half-plane zero. A crossover that stabilizes the pole and still respects the zero",
         ["exists, because the integral turns negative and cancels the conflict",
          "exists as soon as the two singularities are cancelled by the compensator",
          "does not exist: the pole wants the crossover above it and the zero wants the crossover below it",
          "exists at the origin, where both bounds are silent"], 2,
         r"The pole is a floor and the zero is a ceiling. When the floor is above the ceiling, the two inequalities have no common frequency. The integral does not change sign to remove that geometry, and cancelling either singularity with the compensator leaves an unstable hidden mode. The origin is below the pole, so it fails the floor.",
         rhp, rhp_alt, ["robust-stability"])
    b.mc(4,
         r"A performance weight asks \(|S|\) to be small on a wide band. The sensitivity integral says that spec",
         ["can always be met by raising the loop gain at every frequency",
          "is the same statement as the robust-stability test",
          "is automatically met by any stable open loop",
          "can be impossible for a stable proper loop, when the demanded dip has more area than the integral allows"], 3,
         r"The integral fixes the signed area of \(\ln|S|\). A weight that demands a deep, wide dip asks for more negative area than a stable proper loop can spend, and no gain schedule creates that area. Raising the gain everywhere moves the peak; it does not delete it. Robust stability is a test on \(T\) and the uncertainty weight, which is a different inequality.",
         loopfig, loop_alt, ["robust-perf"])
    b.save()


def expl_fund_limits():
    fig = bode([(0.2, -4), (1, -4), (3, 2), (8, 5), (20, 0)], "a sensitivity dip followed by a hump")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A curve below the axis at low frequency, then above the axis, then back toward the axis.",
        "body_md": r"""Feedback can make the sensitivity small on a band you care about, and it cannot make it small on every band at once. For a stable open loop that falls off at least as fast as \(1/\omega^2\), the signed area of \(\ln|S|\) from zero frequency out to infinity is zero. A dip below 1 is paid for by a hump above 1. That trade is the limitation.

Right-half-plane poles and zeros cut the same budget from two other directions. A right-half-plane pole has to be stabilized, which wants the crossover high enough. A right-half-plane zero cannot be cancelled by a stable compensator, and it wants the crossover low enough that its phase has not yet been spent. A delay spends phase in proportion to frequency and tightens the same ceiling.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""When the closed loop is stable and \(|L|\) falls at least as \(1/\omega^2\),
\[
\int_0^{\infty} \ln|S(j\omega)|\,d\omega = \pi \sum_k \mathrm{Re}(p_k),
\]
with the sum over the right-half-plane poles of the loop. No such poles means the integral is 0. At an uncancelled right-half-plane zero \(z\) of the loop, \(L(z) = 0\), so \(S(z) = 1\). The design window used in one of the questions, crossover at least twice a real right-half-plane pole and at most half a real right-half-plane zero, is a stated gap, not a replacement for the integral.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""A single real right-half-plane pole at \(1.7\ \mathrm{rad/s}\) makes the integral \(\pi \times 1.7\), about 5.341. That area is positive, so \(\ln|S|\) cannot be negative everywhere: somewhere \(|S|\) exceeds 1 by enough to pay the 5.341. Separately, suppose the integral is zero, \(|S| = 0.4\) on a band of width 3.5, and the hump is allowed to reach 3.2. The hump width is \(-\ln(0.4)\times 3.5 / \ln(3.2)\), about 2.757. A narrower hump would have to be taller than 3.2.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The factor in front of the pole sum is \(\pi\), not \(2\pi\), and it multiplies real parts, not the imaginary parts of a complex pair. A right-half-plane zero does not add a term to this integral; people who add \(\pi z\) are copying the pole formula onto the wrong singularity. Cancelling that zero with a right-half-plane compensator pole hides an unstable mode, so the interpolation \(S(z) = 1\) is the stable reading. And a hump width is a ratio of logarithms. Using the magnitudes themselves, without the log, balances the wrong areas.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""A robust-performance weight that asks \(|S|\) to be small on a wide band can demand more negative area than the integral contains. The spec is then impossible for every stable proper compensator, before any uncertainty weight is drawn. Robust stability still has to be checked on its own test. The delay that spends the phase in this budget is modeled apart from the integral, as a unit-magnitude block whose phase is \(-\omega\) times the delay.""",
    }]
    return put_explainer("fund-limits", "Sensitivity area, right-half-plane limits", sections)


# ---------------------------------------------------------------------------
# robust performance
# ---------------------------------------------------------------------------

def bank_robust_perf():
    b = Bank("robust-perf")
    weights = bode([(0.2, 6), (1, 6), (3, 0), (10, -8)], "a weight that is large at low frequency")
    weights_alt = "A magnitude that is high at low frequency and then falls."
    loopfig = loop(["P"], "loop under a multiplicative weight", fb="C")
    loop_alt = "A plant block with a controller returned and subtracted."
    both = bode([(0.3, -6), (1, -2), (3, 2), (10, 4)], "sensitivity falling while complementary sensitivity rises")
    both_alt = "A magnitude curve that starts below the axis and finishes above it."
    disk = splane([(-1, 0)], [], "the nominal closed-loop pole")
    disk_alt = "A single cross on the negative real axis."

    s1 = 0.40 + 0.35
    s2 = 1.2 * 0.5
    s3 = 0.5 * 0.9 + 0.4 * 1.1
    room = 1.0 - (0.55 + 0.30)

    b.mc(1,
         r"Robust performance, for a set of plants around a nominal model, means",
         ["the tracking or disturbance spec holds for every plant in the set, not only the nominal one",
          "the nominal loop is stable",
          r"\(|T|\) is below 1 at a single frequency",
          "every weight in the spec is zero"], 0,
         r"Nominal stability and a single-frequency reading of \(|T|\) can both hold while a plant inside the uncertainty set misses the spec. Robust performance is the spec on that whole set. Zero weights would make the spec empty, which is not a performance requirement.",
         loopfig, loop_alt)
    b.num(1,
          r"At one frequency, \(|W_s S| = 0.40\) and \(|W_m T| = 0.35\). The robust-performance quantity \(|W_s S| + |W_m T|\) is",
          s1, "1",
          r"The two nonnegative terms add: \(0.40 + 0.35 = " + show(s1) + r"\). Their product \(0.14\) is not the test. The larger term alone, \(0.40\), is a piece of the sum, and passing each piece is a weaker statement than passing the sum. The difference \(0.05\) has no role in the test.",
          weights, weights_alt)
    b.num(1,
          r"On the nominal plant, \(|S| = 0.5\) and the performance weight is \(|W_s| = 1.2\). The nominal-performance quantity \(|W_s S|\) is",
          s2, "1",
          r"Nominal performance at this frequency is the product \(1.2 \times 0.5 = " + show(s2) + r"\). The sum \(1.7\) adds a weight to a sensitivity as if they were the same kind of number. The ratio \(1.2 / 0.5 = 2.4\) inverts the sensitivity. Reporting \(0.5\) drops the weight that defines the spec.",
          weights, weights_alt)

    b.sym(2,
          r"At one frequency the magnitudes are ws, sm, wm, and tm, in that order: performance weight, sensitivity, multiplicative weight, complementary sensitivity. Write \(|W_s S| + |W_m T|\) in the names ws, sm, wm, and tm.",
          "ws*sm+wm*tm",
          {"ws": (0.15, 1.8), "sm": (0.15, 1.8), "wm": (0.15, 1.8), "tm": (0.15, 1.8)},
          r"Each weight multiplies its own sensitivity. The robust-performance quantity is \(w_s s_m + w_m t_m\). The product of all four is a different expression. Adding the weights to the sensitivities, instead of multiplying, mixes units the test does not add. Swapping partners, \(w_s t_m + w_m s_m\), puts each weight on the wrong function.",
          alternates=["wm*tm+ws*sm", "sm*ws+tm*wm"],
          fig=weights, alt=weights_alt)
    b.num(2,
          r"At the frequency you are checking, \(|W_s| = 0.5\), \(|S| = 0.9\), \(|W_m| = 0.4\), and \(|T| = 1.1\). The quantity \(|W_s S| + |W_m T|\) is",
          s3, "1",
          r"\(0.5 \times 0.9 = 0.45\) and \(0.4 \times 1.1 = 0.44\). The sum is " + show(s3) + r". Adding the four numbers, \(2.9\), treats weights and sensitivities as terms rather than factors. The larger product alone, \(0.45\), drops the uncertainty term. Because \(0.89 < 1\), this one frequency passes; the infinity-norm test still has to hold at every frequency.",
          both, both_alt)
    b.order(2,
            r"Put these checks in the order you would run them for multiplicative uncertainty.",
            ["Confirm the nominal loop is stable.",
             "Check nominal performance, the peak of |W_s S| below 1.",
             "Check robust stability, the peak of |W_m T| below 1.",
             "Check robust performance, the peak of |W_s S| + |W_m T| below 1.",
             "If the sum fails, loosen the performance weight or shrink the uncertainty before raising the loop gain at every frequency."],
            r"An unstable nominal loop makes the later peaks meaningless, so stability is first. Nominal performance and robust stability are the two separate bills. The sum is a stricter bill than either one, so it comes after you know which of the pieces already failed. Raising the gain everywhere is the last resort, and it is often the wrong one, because it shrinks \(S\) and grows \(T\).",
            loopfig, loop_alt)

    b.find_error(3,
                 r"Multiplicative uncertainty, and a performance weight on \(S\). One step is wrong.",
                 [r"The peak of \(|W_m T|\) is \(0.7\), so the robust-stability test passes.",
                  r"The peak of \(|W_s S|\) is \(0.5\), so nominal performance passes.",
                  r"The sum of those peaks is \(1.2\), and the robust-performance test still passes because each piece passed.",
                  r"Robust performance needs the sum itself below 1, so \(1.2\) fails it."],
                 2,
                 r"Each piece below 1 does not put the sum below 1. Here the pieces are \(0.7\) and \(0.5\), and \(1.2 > 1\), so robust performance fails while robust stability and nominal performance pass. The first two readings are the right separate tests, and the last step is the repair.",
                 reasons=["Each piece below 1 does not make the sum below 1, and 1.2 fails the sum.",
                          "A robust-stability pass cancels the performance weight.",
                          "Nominal performance is checked on T, not on S."],
                 correct_reason=0,
                 fig=both, alt=both_alt)
    b.mc(3,
         r"Because \(S + T = 1\) at each frequency,",
         [r"\(|S|\) and \(|T|\) can both be set to 0 by a high gain",
          "a large performance weight and a large uncertainty weight at the same frequency fight each other",
          r"\(|S| + |T|\) is always exactly 1",
          "the identity removes the need for an uncertainty weight"], 1,
         r"\(S + T = 1\) means the two complex values add to 1. They cannot both have small magnitude at the same frequency, so a weight on \(S\) and a weight on \(T\) at that frequency are asking for two things the identity will not give. The sum of the magnitudes is not identically 1. A high gain drives \(S\) toward 0 and \(T\) toward 1, not both toward 0.",
         loopfig, loop_alt)
    b.multi(3,
            r"Which statements hold for the multiplicative robust-performance test?",
            ["Nominal performance can pass while robust performance fails.",
             "Robust stability can pass while robust performance fails.",
             r"If the peak of \(|W_s S| + |W_m T|\) is below 1, then the peaks of \(|W_s S|\) and of \(|W_m T|\) are also below 1.",
             r"Raising the loop gain at every frequency makes both \(S\) and \(T\) smaller."],
            [0, 1, 2],
            r"The sum of two nonnegative functions is at least as large as either one, so a sum below 1 forces each piece below 1, while either piece can sit below 1 with the sum above 1. Raising the loop gain shrinks \(S\) and pushes \(T\) toward 1, so it does not shrink both.",
            weights, weights_alt)

    b.num(4,
          r"At the frequency where \(|W_s S| + |W_m T|\) is largest, the two terms are \(0.55\) and \(0.30\). How far below 1 is that sum?",
          room, "1",
          r"The sum is \(0.85\), and the room under the bound is \(1 - 0.85 = " + show(room) + r"\). Reporting \(0.85\) returns the sum rather than the gap. Reporting \(0.55\) returns one term. Reporting \(0.45\), which is \(1 - 0.55\), is the room under the larger term alone and ignores the \(0.30\) that is also in the sum.",
          both, both_alt, ["loop-shaping"])
    b.mc(4,
         r"The combined bound fails only near the gain crossover. The useful next move is to",
         ["cancel a right-half-plane zero of the plant",
          "declare the nominal plant unstable",
          "trade the crossover in the loop shape, where the performance weight and the uncertainty weight overlap",
          "delete the sensitivity and keep only the complementary sensitivity"], 2,
         r"Near crossover, \(|S|\) and \(|T|\) are both order one, so the two weights are active together. Moving the crossover, or shaping the slope there, is how you separate them. A right-half-plane cancellation would hide an unstable mode. A failed sum is not a proof that the nominal loop is unstable. Dropping \(S\) drops the performance spec the test was written to protect.",
         loopfig, loop_alt, ["loop-shaping"])
    b.mc(4,
         r"The uncertainty is a slow drift of one parameter, not a fixed set you must cover with one controller. Compared with enlarging \(W_m\) until the combined test barely passes,",
         [r"a larger \(W_m\) makes the performance spec easier",
          "robust performance forbids feedback",
          "the estimate should be reset to zero at every sample",
          "an online update of that parameter can be less conservative than one controller built for the whole set"], 3,
         r"A fixed controller that works for every value in a wide set has to satisfy the sum bound for the whole set, which shrinks the performance you can ask for. If the parameter actually drifts and can be estimated while the loop runs, updating the controller from that estimate is a different design, and it is not the same as inflating \(W_m\). A larger weight makes the test harder. The spec does not forbid feedback.",
         disk, disk_alt, ["adaptive"])
    b.save()


def expl_robust_perf():
    fig = loop(["P"], "nominal loop, with weights checked on S and T")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A plant block in a negative loop, the controller on the return path.",
        "body_md": r"""Nominal performance says the sensitivity spec holds for the model you wrote down. Robust stability says every plant inside the uncertainty set is still stable. Robust performance says the spec itself holds for every plant in that set, not only for the nominal one.

For multiplicative uncertainty the three statements are three peaks. Nominal performance is the peak of \(|W_s S|\). Robust stability is the peak of \(|W_m T|\). Robust performance is the peak of the sum \(|W_s S| + |W_m T|\). The sum is harder than either piece. A design can pass both pieces and still fail the sum, which is the usual surprise near crossover, where neither sensitivity is small.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""With \(P = P_0(1 + W_m \Delta)\) and \(\|\Delta\|_\infty \le 1\), and a nominal performance spec \(\|W_s S\|_\infty < 1\),
\[
\|W_s S\|_\infty < 1, \qquad \|W_m T\|_\infty < 1, \qquad \||W_s S| + |W_m T|\|_\infty < 1.
\]
The identity \(S + T = 1\) is why the third line is not automatic. The two complex numbers add to 1, so a frequency where both weights are large is a frequency where the sum is in trouble. The weights themselves are the uncertainty model and the spec; this skill only combines them.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""At the frequency you care about, \(|W_s S| = 0.346\) and \(|W_m T| = 0.271\). Each piece is below 1, and the robust-stability and nominal-performance readings pass at this frequency. The sum is 0.617, which also passes, with room \(1 - 0.617 = 0.383\). Move the second term up to \(0.70\) and the sum becomes \(1.046\), which fails, even though \(0.346\) still looks comfortable. The piece you did not add is the one that spends the room.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""Passing each peak separately is not the robust-performance test. The test adds the peaks' ingredients at each frequency and then takes the worst frequency. Multiplying \(|W_s S|\) by \(|W_m T|\) is a different expression and can look fine when the sum is already above 1. And \(|S| + |T|\) is not identically 1; only \(S + T\) is. A high loop gain shrinks \(S\) and drives \(T\) toward 1, so it helps one weight and hurts the other.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""When the sum fails near crossover, the next edit is the loop shape: move the crossing, or change the slope, so the two weights are not large together. A sensitivity integral can also make the performance weight impossible before the uncertainty weight is drawn. If the uncertainty is really one drifting parameter you can estimate online, updating the controller from that estimate can be less conservative than covering the whole set with one fixed law.""",
    }]
    return put_explainer("robust-perf", "Robust performance with weighted S and T", sections)


# ---------------------------------------------------------------------------
# adaptive
# ---------------------------------------------------------------------------

def bank_adaptive():
    b = Bank("adaptive")
    adapt = block_diagram(["adapt", "C", "P"], "an adaptive gain in front of the plant", feedback="1",
                          input_label="r", output_label="y")
    adapt_alt = "Three blocks in series, adapt, C, and P, with unity feedback."
    settle = step_response("a parameter estimate settling toward a constant", tau=1.4, goal=1.0)
    settle_alt = "A curve that rises and levels off."
    plant = loop(["P"], "a proportional loop whose gain uses the estimate", fb="C")
    plant_alt = "A plant block with a controller returned and subtracted."
    reg = matrix_fig([["u", "y"]], "one regressor column and the measured output")
    reg_alt = "A row with two entries, labeled u and y."

    rate = 0.5 * (8.0 - 1.0 * 2.0) * 2.0
    ce = 4.0 / 2.0
    norm = 0.4 * 5.0 * 3.0 / (1.0 + 3.0 ** 2)
    theta_new = 1.5 + 0.2 * 0.5 * 4.0 * 2.0

    b.mc(1,
         r"Adaptive control, as used here, differs from a fixed controller because it",
         ["updates parameters of the control law from signals measured while the loop is running",
          "replaces feedback with a larger constant gain",
          "needs a new sensor for every parameter",
          "adds a second integrator and then freezes every gain"], 0,
         r"The parameter estimate is updated from the input and the output during operation, and the control law uses the current estimate. A larger constant gain is still a fixed controller. The sensors you already have are the input and the output. A second integrator is a different augmentation, and freezing the gains is the opposite of adapting.",
         adapt, adapt_alt)
    b.num(1,
          r"A static gain model predicts \(\hat{y} = \hat{\theta} u\). The command is held at \(u = 2\), the measured output is \(y = 8\), and the estimate is \(\hat{\theta} = 1\). With adaptation gain \(0.5\), the gradient update \(\dot{\hat{\theta}} = \gamma \varepsilon u\) has the value",
          rate, "1/s",
          r"The prediction is \(1 \times 2 = 2\), so the prediction error is \(8 - 2 = 6\). Then \(0.5 \times 6 \times 2 = " + show(rate) + r"\). Dropping the final factor of \(u\) leaves \(0.5 \times 6 = 3\). Using \(y\) in place of the prediction error gives \(0.5 \times 8 \times 2 = 8\). Using the estimate itself as the rate leaves \(1\).",
          reg, reg_alt)
    b.num(1,
          r"Certainty equivalence wants a loop gain of 4. The plant-gain estimate is 2. The controller gain inserted in front of the plant is",
          ce, "1",
          r"The controller gain is the desired loop gain divided by the estimate, \(4 / 2 = " + show(ce) + r"\). The product \(8\) would be right if the estimate multiplied the desired gain instead of scaling it. The desired gain alone, 4, ignores the estimate. The estimate alone, 2, ignores the target. If the estimate later moves, this quotient moves with it.",
          plant, plant_alt)

    b.sym(2,
          r"The gradient update is adaptation gain times prediction error times regressor. Write that product in the names gamma, eps, and uu.",
          "gamma*eps*uu",
          {"gamma": (0.05, 1.5), "eps": (0.2, 4.0), "uu": (0.3, 3.0)},
          r"The instantaneous rate is \(\gamma \varepsilon u\), the product of the three factors. Adding them is not the update. The quotient \(\gamma \varepsilon / u\) is a normalization with the wrong power of the regressor. Dropping \(\varepsilon\) updates from the regressor even when the prediction is already perfect.",
          alternates=["eps*gamma*uu", "uu*eps*gamma"],
          fig=reg, alt=reg_alt)
    b.num(2,
          r"The normalized update is \(\dot{\hat{\theta}} = \gamma \varepsilon u / (1 + u^2)\), with \(\gamma = 0.4\), \(\varepsilon = 5\), and \(u = 3\). The parameter derivative is",
          norm, "1/s",
          r"The numerator is \(0.4 \times 5 \times 3 = 6\). The denominator is \(1 + 9 = 10\). The rate is " + show(norm) + r". Skipping the normalization leaves 6, which is the blow-up the denominator was added to prevent. Using \(1 + u\) instead of \(1 + u^2\) divides by 4 and produces 1.5. Using \(u^2\) alone, without the 1, divides by 9 and produces \(2/3\).",
          settle, settle_alt)
    b.order(2,
            r"Put these steps in the order you would use to put adaptation on a loop.",
            ["Choose a controller whose ideal parameters are a known function of the plant parameters.",
             "Start an estimator from a stated initial guess, using the measured input and output.",
             "Insert the current estimate into the controller as if it were exact.",
             "Keep a normalization or a dead zone so one large sample cannot wind the parameter without bound.",
             "Check that the command is rich enough to move the estimate, and recheck the margins of the adapted loop."],
            r"You need a controller that has a correct setting before you estimate anything. The estimator needs an initial value and the two signals it regresses on. Certainty equivalence is the insertion step, and it comes after there is an estimate to insert. The guard against a huge step comes with the update, not after you have already deployed an unbounded one. Excitation and the margins are the last check, because a converged estimate on a constant input is not evidence about every adaptation gain.",
            adapt, adapt_alt)

    b.find_error(3,
                 r"A plant gain is constant and unknown. The estimate starts at half of that gain. One step is wrong.",
                 ["Certainty equivalence inserts the current estimate into the proportional gain.",
                  "On a noise-free record with a nonzero constant input, this scalar gradient can converge.",
                  "Therefore the closed loop is stable for every adaptation gain, including a very large one.",
                  "A large adaptation gain can move the parameter faster than the plant, so the linear margins no longer describe the loop."],
                 2,
                 r"Convergence of one scalar estimate on a quiet, constant, nonzero input is a special case. It does not license every adaptation gain. A huge gain makes the parameter, and therefore the command, move on a time scale the plant model was not written for, and the margins of the frozen loop do not cover that motion. The insertion step and the warning about a large gain are the right pieces.",
                 reasons=["A special noise-free convergence does not license an arbitrarily large adaptation gain.",
                          "Certainty equivalence means the estimate is ignored by the controller.",
                          "A wrong initial gain means the parameter can never be updated."],
                 correct_reason=0,
                 fig=settle, alt=settle_alt)
    b.mc(3,
         r"After the output has settled, the input is held constant and the prediction error is zero. This gradient update",
         ["keeps moving the estimate at the adaptation gain",
          "stops moving the estimate, so a later drift is invisible until the input changes",
          "is the richest excitation this model can have",
          "replaces the stability check"], 1,
         r"The rate is proportional to the prediction error and to the input. A zero error freezes the estimate even though the input is nonzero. A constant input is a poor excitation for anything beyond one gain, not the richest one. A frozen estimate does not answer whether a large adaptation gain was safe while the error was still moving.",
         reg, reg_alt)
    b.multi(3,
            r"Which statements hold for this introductory adaptive law?",
            ["Certainty equivalence uses the latest estimate as if it were the true parameter.",
             "A table indexed by a measured temperature is the same update as a gradient on the prediction error.",
             "If the prediction error is zero, this gradient update does not move the estimate.",
             r"Dividing by \(1 + u^2\) keeps one large sample from producing an arbitrarily large parameter step."],
            [0, 2, 3],
            r"Certainty equivalence is the plug-in step. A zero prediction error zeros this particular update. The normalization caps the step when \(|u|\) is large. A table driven by a measured temperature is chosen offline and does not use the prediction error, so it is a different mechanism.",
            adapt, adapt_alt)

    b.num(4,
          r"One Euler step of the gradient update uses \(\hat{\theta} = 1.5\), step \(0.2\ \mathrm{s}\), adaptation gain \(0.5\), prediction error \(4\), and regressor \(2\). The updated parameter is",
          theta_new, "1",
          r"The rate is \(0.5 \times 4 \times 2 = 4\). Over \(0.2\ \mathrm{s}\) the parameter moves by \(0.8\), from \(1.5\) to " + show(theta_new) + r". Reporting \(0.8\) returns the step and forgets the value you started from. Reporting \(1.5\) skips the update. Reporting \(4\) is the rate in per-second units, not the new parameter. A step of \(0.2 \times 4 = 0.8\) in the other direction would require a negative error.",
          settle, settle_alt, ["gain-scheduling"])
    b.mc(4,
         r"Compared with fitting the plant once and then freezing the controller,",
         ["a frozen controller cannot use feedback",
          "a one-shot fit cannot produce a gain",
          "adaptation keeps updating after that experiment, which tracks a drift and can also destabilize the loop if the update never turns off",
          "adaptation removes the need for an initial guess"], 2,
         r"A one-shot fit produces a fixed law. Adaptation leaves the update running, so a drifting parameter can be followed, and a gain that never turns off can also push the loop off the margins of that frozen law. The frozen law still uses feedback. The fit does produce a gain. The update still starts from a guess.",
         plant, plant_alt, ["gain-scheduling"])
    b.mc(4,
         r"The uncertainty is a fixed set of plants, not a parameter that drifts while you watch. Then",
         ["an adaptation law is required whenever an uncertainty weight is nonzero",
          "a robust spec forbids feedback",
          "the estimate should be reset to zero after every sample",
          "one controller designed for the whole set can be preferable to an adaptation law that keeps hunting"], 3,
         r"If the unknown does not change, and every plant in the set has to meet the spec with the same controller, a robust design is the matching tool. Adaptation is for a parameter you keep estimating. A nonzero uncertainty weight does not by itself require an online update. The spec does not forbid feedback, and resetting the estimate every sample throws away the only memory the update has.",
         adapt, adapt_alt, ["robust-perf"])
    b.save()


def expl_adaptive():
    fig = block_diagram(["adapt", "C", "P"], "estimate, controller, plant", feedback="1",
                        input_label="r", output_label="y")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "Three series blocks labeled adapt, C, and P, with the output returned and subtracted.",
        "body_md": r"""Adaptive control updates a parameter of the controller while the loop is running, using the input and the output you already measure. The update in this skill is a gradient on a prediction error. Certainty equivalence then inserts the latest estimate into the control law as if the estimate were exact.

That is a different job from fitting a model once on a recorded experiment and freezing the result. It is also different from a table indexed by a measured temperature or speed: that table is built offline and does not look at the prediction error. The adaptive law looks at the error, and it stops moving when the error is zero.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""For a model that is linear in a parameter, \(\hat{y} = \hat{\theta} u\), the prediction error is \(\varepsilon = y - \hat{\theta} u\) and the gradient update is
\[
\dot{\hat{\theta}} = \gamma \varepsilon u, \qquad \dot{\hat{\theta}} = \frac{\gamma \varepsilon u}{1 + u^2}.
\]
The second form keeps one large \(u\) from producing an arbitrarily large step. If the desired loop gain is \(k_\star\) and the plant gain estimate is \(\hat{\theta}\), certainty equivalence uses the controller gain \(k_\star / \hat{\theta}\). One Euler step over \(\Delta t\) adds \(\Delta t\) times the rate to the current estimate.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(\gamma = 0.13\), a measurement \(y = 4.6\), an estimate \(\hat{\theta} = 1.2\), and a regressor \(u = 1.8\). The prediction is \(1.2 \times 1.8 = 2.16\), so \(\varepsilon = 4.6 - 2.16 = 2.44\). The un-normalized rate is \(0.13 \times 2.44 \times 1.8 = 0.571\) per second, to three decimals. The same numbers with the normalization divide by \(1 + 1.8^2 = 4.24\), and the rate drops to about \(0.135\). The normalization is doing the work on a regressor that is no longer small.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The product uses the prediction error, not the raw output. Once the prediction matches, this gradient is zero even if the input is large, so a parameter that drifts later is invisible until the input moves and the error returns. A noise-free convergence on a constant input does not mean every adaptation gain is safe: a huge \(\gamma\) moves the command faster than the plant model was written for. And dividing by \(u\) instead of by \(1 + u^2\) blows up at the moment the input crosses zero, which is the sample you most wanted to ignore.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""If the parameter is really a measured operating condition, a scheduled gain can replace the online gradient. If the unknown is a fixed set rather than a drift, one controller built so the spec holds on the whole set can be calmer than an estimate that keeps hunting. Either way the loop still needs a margin check at the gains the update can actually reach, not only at the initial guess.""",
    }]
    return put_explainer("adaptive", "Adaptive control from a running estimate", sections)


def lint():
    banned = re.compile(
        r"niknejad|åström|aström|astrom|murray|feedback systems|ziegler|nichols|\breader\b|§|"
        r"\b(university|professor|textbook|syllabus|berkeley)\b",
        re.I,
    )
    skills = ["adaptive", "fund-limits", "observer", "robust-perf", "state-feedback"]
    problems = []
    for sid in skills:
        bank = json.load(open(os.path.join(BANK, f"{sid}.json"), encoding="utf-8"))
        exp = json.load(open(os.path.join(EXP, f"{sid}.json"), encoding="utf-8"))
        nfig = 0
        idxs = []
        deep = 0
        for q in bank["questions"]:
            blob = json.dumps(q, ensure_ascii=False)
            if banned.search(blob):
                problems.append(f"{q['id']} banned wording")
            if q.get("figure"):
                nfig += 1
            if q["type"] == "mc":
                idxs.append(q["correct_index"])
            if q["type"] in ("symbolic", "order", "error", "multi"):
                deep += 1
        if nfig < 9:
            problems.append(f"{sid} only {nfig} figures")
        if deep < 3:
            problems.append(f"{sid} deep {deep}")
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
        print(f"{sid}: questions {len(bank['questions'])}, figures {nfig}, deep {deep}, MC idx {idxs}, explainer words {wc}")
    if problems:
        print("LINT FAIL")
        for item in problems:
            print(" ", item)
        sys.exit(1)
    print("lint ok")


def main():
    bank_state_feedback()
    bank_observer()
    bank_fund_limits()
    bank_robust_perf()
    bank_adaptive()
    print(
        "words",
        expl_state_feedback(),
        expl_observer(),
        expl_fund_limits(),
        expl_robust_perf(),
        expl_adaptive(),
    )
    lint()


if __name__ == "__main__":
    main()
