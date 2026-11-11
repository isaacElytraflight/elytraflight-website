#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB8 banks and explainers.

Skills: descent-directions, descent-method-framework, convergence-rates,
exact-line-search-quadratic, armijo-backtracking, gradient-zigzag,
condition-number-gradient-rate, lipschitz-gradient, descent-lemma,
sufficient-decrease-lemma, gradient-method-convergence.

Closed-form answers live here. skilltree/verify_nlo_nb8.py recomputes the
numeric ones and does not import this file.
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import DEEP_TYPES, Bank, deep_quota, save_explainer
from templates import (
    ellipse_axes,
    halfspace_fig,
    level_curves_fig,
    matrix_fig,
    norm_balls,
    orthant_fig,
    plane_vectors,
    plot,
    segment_fig,
    simplex_fig,
)

FALL = plot(lambda t: 1.55 - 0.42 * t, 0.0, 2.6, "t", "z", "a line sloping down")
A_FALL = "A straight line sloping downward on labeled axes."
RISE = plot(lambda t: 0.35 * t + 0.45, 0.0, 2.6, "t", "z", "a line sloping up")
A_RISE = "A straight line sloping upward on labeled axes."
DECAY = plot(lambda t: 1.7 * (0.62 ** t), 0.0, 5.5, "k", "e", "a falling curve")
A_DECAY = "A curve that falls toward the horizontal axis."
SLOW = plot(lambda t: 1.55 / (1.0 + 0.55 * t), 0.0, 5.5, "k", "e", "a slowly falling curve")
A_SLOW = "A curve that drops at first and then flattens."
HALF = halfspace_fig("a half-plane")
A_HALF = "A straight boundary with one side shaded."
ORTH = orthant_fig("the first quadrant")
A_ORTH = "The closed first quadrant, shaded."
SEG = segment_fig("a segment")
A_SEG = "A solid segment joins two marked points on a dashed line."
SIMP = simplex_fig("a segment in the first quadrant")
A_SIMP = "A segment joining two marked points on the axes."
ELL = ellipse_axes("a long ellipse")
A_ELL = "An axis-aligned ellipse, longer along the first axis."
LEV = level_curves_fig("nested contours")
A_LEV = "Three nested ellipses around the origin."
BALL = norm_balls("three unit balls")
A_BALL = "A diamond, a disk, and a square centered at the origin."
ARR = plane_vectors([(1.15, 0.35, "d")], "one arrow from the origin")
A_ARR = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.05, 0.2, "g"), (-0.85, 0.55, "d")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."
ZIG = plane_vectors([(1.1, 0.15, "d"), (0.2, -0.95, "n")], "two nearly perpendicular arrows")
A_ZIG = "Two arrows leave the origin in different directions."
MAT = matrix_fig([["a", "0"], ["0", "b"]], "a diagonal array")
A_MAT = "A two-by-two array with labels on the diagonal."

P_FRAME = ["descent-method-framework"]
P_EXACT = ["exact-line-search-quadratic"]
P_ARM = ["armijo-backtracking"]
P_ZIG = ["gradient-zigzag"]
P_COND = ["condition-number-gradient-rate"]
P_RATE = ["convergence-rates"]
P_GCONV = ["gradient-method-convergence"]
P_NEWT = ["newton-local-quadratic-convergence"]
P_QCONJ = ["q-conjugate-directions"]
P_SUFF = ["sufficient-decrease-lemma"]
P_WOLFE = ["wolfe-conditions"]
P_NGLOB = ["newton-globalization"]
P_GN = ["gauss-newton-method"]
P_LIPS = ["lipschitz-gradient"]
P_DLEM = ["descent-lemma"]
P_NEST = ["nesterov-accelerated-gradient"]
P_FW = ["frank-wolfe-conditional-gradient"]
P_GPROJ = ["gradient-projection-method"]
P_CG = ["conjugate-gradient-method"]
P_HB = ["heavy-ball-method"]


def bank_descent():
    b = Bank("descent-directions")
    b.mc(
        1,
        r"At a point where \(f\) is differentiable, a vector \(d\) is a descent direction when",
        [
            r"\(\nabla f(x)^T d < 0\)",
            r"\(\nabla f(x)^T d = 0\)",
            r"\(\nabla f(x)^T d > 0\)",
            r"\(d\) is a multiple of the all-ones vector",
        ],
        0,
        r"The directional derivative is the dot product \(\nabla f(x)^T d\). A strict negative value means the first-order model decreases along \(d\), which is the definition of a descent direction. A zero dot product is a tangent direction of the model, and a positive dot product is an ascent direction. Being a multiple of the all-ones vector says nothing about \(f\).",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"Let \(\nabla f(x) = (3, 1)\) and \(d = (-2, 1)\). What is the directional derivative \(\nabla f(x)^T d\)?",
        -5,
        "1",
        r"The dot product is \(3 \cdot (-2) + 1 \cdot 1 = -6 + 1 = -5\). The value is negative, so \(d\) is a descent direction, but the question asks for the derivative itself. Reporting \(5\) drops the sign. Reporting \(-6\) stops after the first term. Reporting \(1\) is the second component of \(d\).",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        1,
        r"If \(\nabla f(x)^T d < 0\), the first-order expansion implies that",
        [
            r"\(f(x + t d) < f(x)\) for every \(t > 0\)",
            r"\(f(x + t d) < f(x)\) for all sufficiently small \(t > 0\)",
            r"\(x\) is a local minimizer",
            r"the Hessian at \(x\) is positive definite",
        ],
        1,
        r"Write \(f(x + t d) = f(x) + t\, \nabla f(x)^T d + o(t)\). The linear term is negative and dominates the remainder when \(t > 0\) is small enough, so the function drops. A long step can turn back up, so the decrease is not guaranteed for every positive \(t\). A negative directional derivative means \(x\) is not a local minimizer. The Hessian is not involved in this first-order argument.",
        fig=FALL,
        alt=A_FALL,
    )
    b.order(
        2,
        r"Put these steps in the order that proves a negative directional derivative produces a decrease for a short step. Each step uses the result of the step before it.",
        [
            r"Expand \(f(x + t d) = f(x) + t\, \nabla f(x)^T d + o(t)\) as \(t \to 0\).",
            r"Divide the change in \(f\) by \(t > 0\), leaving \(\nabla f(x)^T d + o(1)\).",
            r"For small \(t > 0\) the negative directional derivative dominates, so the difference quotient is negative.",
            r"Multiply that negative quotient by \(t > 0\) to conclude \(f(x + t d) < f(x)\).",
        ],
        r"The expansion has to be written before it can be divided by the step. The divided form is what the little-o term no longer hides, so the sign of the directional derivative can be read off only after that division. The function decrease is the difference quotient multiplied back by the positive step, which preserves the inequality. Multiplying before the sign is known does not yet prove a decrease.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Let \(\nabla f(x) = (1, -2)\). Which of these vectors are descent directions at \(x\)?",
        [
            r"\(d = (-1, 0)\)",
            r"\(d = (2, 1)\)",
            r"\(d = (1, 1)\)",
            r"\(d = (4, 1)\)",
            r"\(d = (-3, -1)\)",
        ],
        [0, 2, 4],
        r"A descent direction needs a strictly negative dot product with \((1, -2)\)."
        "\n"
        r"• \((-1, 0)\) gives \(-1\)."
        "\n"
        r"• \((1, 1)\) gives \(1 - 2 = -1\)."
        "\n"
        r"• \((-3, -1)\) gives \(-3 + 2 = -1\)."
        "\n"
        r"• \((2, 1)\) gives \(2 - 2 = 0\), which is not strict."
        "\n"
        r"• \((4, 1)\) gives \(4 - 2 = 2\), an ascent direction.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.sym(
        2,
        r"The gradient is \((p, q)\) and the direction is \((-p, r)\). The directional derivative equals",
        "-p*p+q*r",
        {"p": (1, 3), "q": (1, 3), "r": (-2, 2)},
        r"The dot product is \(p \cdot (-p) + q \cdot r = -p^2 + q r\). Every declared name appears: \(p\) from the first components, and \(q\) and \(r\) from the second. Dropping the minus sign turns the square into an ascent contribution. Using \(p \cdot r\) instead of \(q \cdot r\) pairs the wrong components. Replacing \(r\) by \(-p\) computes the steepest-descent derivative \(-p^2 - q^2\), which is a different direction.",
        alternates=["q*r-p*p", "q*r-p**2"],
        fig=ARR,
        alt=A_ARR,
    )
    b.find_error(
        3,
        r"A note checks \(d = (1, -1)\) for \(f(x_1, x_2) = x_1^2 + 2 x_2\) at \((1, 0)\). Exactly one step is a false claim.",
        [
            r"The gradient is \((2 x_1, 2)\), so it equals \((2, 2)\) at \((1, 0)\).",
            r"The directional derivative is \(2 \cdot 1 + 2 \cdot (-1) = 0\).",
            r"A directional derivative of zero means \(d\) is a descent direction.",
            r"The direction \(-\nabla f = (-2, -2)\) has directional derivative \(-8\), so it is a descent direction.",
        ],
        2,
        r"The partial derivatives of \(x_1^2 + 2 x_2\) are \((2 x_1, 2)\), and at \((1, 0)\) that is \((2, 2)\). The dot product with \((1, -1)\) is \(2 - 2 = 0\). The negative gradient \((-2, -2)\) dots with \((2, 2)\) to give \(-8 < 0\), so that direction does descend. The false step is the reading of the zero: a descent direction requires a strictly negative directional derivative. Zero means the first-order model is flat along \(d\).",
        [
            r"A zero directional derivative is not the strict inequality that defines a descent direction.",
            r"The gradient at \((1, 0)\) is not \((2, 2)\).",
            r"The dot product \(2 - 2\) is not zero.",
        ],
        0,
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        3,
        r"Let \(\nabla f(x) = (1, -2)\) and let \(D = \mathrm{diag}(2, 3)\), which is positive definite. For \(d = -D \nabla f(x)\), what is \(\nabla f(x)^T d\)?",
        -14,
        "1",
        r"First \(D \nabla f = (2, -6)\), so \(d = (-2, 6)\). The directional derivative is \(1 \cdot (-2) + (-2) \cdot 6 = -2 - 12 = -14\). The same number is \(-\nabla f^T D \nabla f = -(2 + 12)\). Reporting \(14\) drops the minus that makes the direction a descent direction. Reporting \(-2\) is only the first term. Reporting \(6\) is a component of \(d\).",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        3,
        r"If \(D\) is symmetric positive definite and \(\nabla f(x) \ne 0\), the vector \(d = -D \nabla f(x)\) is a descent direction because",
        [
            r"\(D\) has determinant zero",
            r"\(\nabla f(x)^T d = -\nabla f(x)^T D \nabla f(x) < 0\)",
            r"\(d\) is orthogonal to the gradient",
            r"every positive definite matrix has negative eigenvalues",
        ],
        1,
        r"Substitute the direction: the directional derivative equals \(-\nabla f^T D \nabla f\). Positive definiteness makes that quadratic form positive whenever the gradient is nonzero, so the directional derivative is negative. A positive definite matrix has positive eigenvalues and a nonzero determinant. The direction \(-D \nabla f\) is orthogonal to the gradient only in special cases, not in general.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        4,
        "Once a descent direction has been chosen, the next decision in a descent iteration is",
        [
            "to replace the gradient by the Hessian and stop",
            "to choose a step length along that direction",
            "to set the gradient to zero by hand",
            "to discard the direction and use a simplex basis instead",
        ],
        1,
        r"A descent direction says which way a short move decreases the first-order model. The iteration still has to choose how far to go. That choice is the step length. Setting the gradient to zero is the optimality condition at a minimizer, not the next algorithmic step. A simplex basis is a construction for a linear program. The Hessian may be used later to build a different direction, and it does not replace the step-length decision.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_FRAME,
    )
    b.num(
        4,
        r"Let \(\nabla f(x) = (6, 1)\) and \(d = (-1, 2)\). What is \(\nabla f(x)^T d\)?",
        -4,
        "1",
        r"The dot product is \(6 \cdot (-1) + 1 \cdot 2 = -6 + 2 = -4\). The negative value says \(d\) is a descent direction. Reporting \(4\) drops the sign. Reporting \(-6\) ignores the second term. Reporting \(8\) is the product of the two second components with the wrong sign pattern, \(1 \cdot 2\) added to \(6\) instead of subtracted.",
        fig=ARR,
        alt=A_ARR,
        preview=P_EXACT,
    )
    b.mc(
        4,
        "A line-search rule such as a sufficient-decrease test is applied",
        [
            "before the gradient is computed",
            "to a direction that has already been chosen",
            "only when the Hessian is indefinite",
            "in place of checking that the directional derivative is negative",
        ],
        1,
        r"The sufficient-decrease test compares function values along a ray \(x + t d\). That ray exists only after \(d\) has been chosen. The gradient is an input to the direction, so it is computed first. An indefinite Hessian can still leave a descent direction available, and the line search does not wait for that case. The line search does not replace the sign check: the sign check is what makes a small enough step able to pass.",
        fig=FALL,
        alt=A_FALL,
        preview=P_ARM,
    )
    b.save()


def bank_framework():
    b = Bank("descent-method-framework")
    b.mc(
        1,
        "A general descent iteration updates the point by",
        [
            r"\(x^+ = x + t d\) with a step length \(t > 0\) and a descent direction \(d\)",
            r"\(x^+ = \nabla f(x)\)",
            r"\(x^+ = x\) whenever the gradient is nonzero",
            r"\(x^+ = t\, \nabla f(x)\) with \(t > 0\)",
        ],
        0,
        r"The iteration separates three choices: a descent direction, a positive step length, and a stopping test. The update that uses the first two is \(x^+ = x + t d\). Replacing \(x\) by the gradient changes the meaning of the vector. Leaving \(x\) fixed does not move. Adding a positive multiple of the gradient walks uphill.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"Take \(x = (2, 1)\), \(d = (-4, 2)\), and step length \(t = 1/2\). What is the squared Euclidean length of the displacement \(t d\)?",
        5,
        "1",
        r"The displacement is \((1/2)(-4, 2) = (-2, 1)\). Its squared length is \(4 + 1 = 5\). Equivalently, \(t^2 \lVert d\rVert^2 = (1/4)(16 + 4) = 5\). Reporting \(20\) is \(\lVert d\rVert^2\) before the step length. Reporting \(2\) is the absolute value of one component. Reporting \(\sqrt{5}\) is the length, not the squared length.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        1,
        "A typical stopping test for this iteration is",
        [
            r"the gradient norm is small",
            r"the chosen direction fails \(\nabla f^T d < 0\)",
            r"the step length is required to be an integer",
            r"the objective is replaced by a constraint",
        ],
        0,
        r"The direction is built so that the directional derivative is negative. That is an input to the step, not a reason to stop. Stopping looks at progress: a small gradient norm means the first-order model has nowhere useful to go. The step length is a positive real number. Replacing the objective by a constraint changes the problem.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.order(
        2,
        "Put one iteration in the order a descent method carries it out. Each step uses the result of the step before it.",
        [
            "Compute the gradient at the current point.",
            "Build a descent direction from that gradient.",
            "Select a positive step length along the direction.",
            "Replace the point by the point plus the step length times the direction.",
            "Apply a stopping test, such as a small gradient norm at the new point.",
        ],
        r"The gradient is the raw material for the direction, so it comes first. The step length is a distance along a direction that already exists. The update can be formed only after both are known, and the stopping test looks at the point that update produced. Testing for a stop before the gradient exists has nothing to measure. Choosing the step length before the direction does not define the ray.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"The gradient at the current point is nonzero. Which of these are legitimate descent directions for the iteration?",
        [
            r"Steepest descent, \(d = -\nabla f(x)\).",
            r"The gradient itself, \(d = \nabla f(x)\).",
            r"A Newton direction \(d = -H^{-1} \nabla f(x)\) when the Hessian \(H\) is positive definite.",
            r"The zero vector.",
            r"A scaled direction \(d = -D \nabla f(x)\) with \(D\) symmetric positive definite.",
        ],
        [0, 2, 4],
        r"Each legitimate choice has a negative directional derivative."
        "\n"
        r"• \(d = -\nabla f\) gives \(-\lVert\nabla f\rVert^2 < 0\)."
        "\n"
        r"• Newton with a positive definite Hessian gives \(-\nabla f^T H^{-1} \nabla f < 0\)."
        "\n"
        r"• A positive definite scaling \(D\) gives \(-\nabla f^T D \nabla f < 0\)."
        "\n"
        r"• \(d = \nabla f\) gives \(\lVert\nabla f\rVert^2 > 0\), an ascent direction."
        "\n"
        r"• The zero vector has directional derivative \(0\), so it is not a descent direction.",
        fig=ELL,
        alt=A_ELL,
    )
    b.sym(
        2,
        r"The current first coordinate is \(a\), the step length is \(t\), and the first component of the direction is \(b\). The next first coordinate equals",
        "a+t*b",
        {"a": (-2, 4), "t": (0.2, 2), "b": (-3, -0.2)},
        r"The update is componentwise. The first coordinate of \(x + t d\) is \(a + t b\). All three names appear: the old coordinate, the step length, and the direction component. Subtracting \(t b\) walks against the direction. Replacing the product by a sum \(a + t + b\) adds quantities that do not share a meaning. Using \(a \cdot t\) drops the direction.",
        alternates=["a+b*t", "t*b+a"],
        fig=ARR,
        alt=A_ARR,
    )
    b.find_error(
        3,
        r"A note takes one steepest-descent step from \(x = (4, 1)\) where \(\nabla f(x) = (2, -2)\). Exactly one step is a false claim.",
        [
            r"The gradient at the current point is \((2, -2)\).",
            r"Steepest descent uses the direction \(d = -\nabla f(x) = (-2, 2)\).",
            r"With step length \(1\), the next point is \((4, 1) + (2, -2) = (6, -1)\).",
            r"The directional derivative of this steepest direction is \(-8\), which is negative.",
        ],
        2,
        r"The gradient is given as \((2, -2)\). Steepest descent negates it, so \(d = (-2, 2)\). The directional derivative is \(2 \cdot (-2) + (-2) \cdot 2 = -8\). The false step adds the gradient instead of the steepest direction. The point \(x + 1 \cdot d\) is \((4, 1) + (-2, 2) = (2, 3)\), not \((6, -1)\).",
        [
            r"The update added the gradient. The steepest step adds the negative gradient.",
            r"Steepest descent should have used \(d = \nabla f(x)\).",
            r"The directional derivative of \(-\nabla f\) is positive here.",
        ],
        0,
        fig=ZIG,
        alt=A_ZIG,
    )
    b.num(
        3,
        r"A stopping rule looks at \(\nabla f(x) = (3, 4)\). What is the Euclidean norm of this gradient?",
        5,
        "1",
        r"The squared norm is \(9 + 16 = 25\), so the norm is \(5\). Reporting \(25\) stops at the square. Reporting \(7\) adds the components. Reporting \(12\) is their product. The test compares this norm with a tolerance. The value \(5\) is what gets compared.",
        fig=BALL,
        alt=A_BALL,
    )
    b.mc(
        3,
        "The Gauss-Newton direction and the Newton direction differ in what they invert:",
        [
            r"Gauss-Newton inverts a residual Gram matrix, while Newton inverts the Hessian of \(f\)",
            r"both invert the same Hessian of \(f\)",
            r"Gauss-Newton inverts the Hessian, while Newton uses the negative gradient with no matrix",
            r"neither uses the gradient",
        ],
        0,
        r"Newton builds \(d = -H_f(x)^{-1} \nabla f(x)\) from the Hessian of the objective. Gauss-Newton is aimed at a sum of squares. It linearizes the residual and inverts the Gram matrix of the residual Jacobian, which is the Hessian of the least-squares objective with the second-derivative term left out. Both directions still use the gradient. Steepest descent is the method that uses no matrix.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        4,
        "On a smooth quadratic with a positive definite Hessian, the exact step length along a fixed direction is",
        [
            "always equal to 1",
            "the minimizer of the objective restricted to that line",
            "the reciprocal of the gradient norm, for every direction",
            "illegal, because a quadratic has no line search",
        ],
        1,
        r"Restricting a quadratic to the line \(x + t d\) produces a parabola in the scalar \(t\). The exact step length is the \(t\) that minimizes that parabola. It equals 1 only for special directions, such as a pure Newton step on a quadratic. The reciprocal of the gradient norm is a different normalization. A quadratic is exactly the case where the line search has a closed form.",
        fig=ELL,
        alt=A_ELL,
        preview=P_EXACT,
    )
    b.num(
        4,
        r"From \(x = (0, 5)\), take \(d = (-2, -1)\) and \(t = 3\). What is the squared Euclidean length of the displacement?",
        45,
        "1",
        r"The displacement is \(3(-2, -1) = (-6, -3)\). Its squared length is \(36 + 9 = 45\). Equivalently, \(t^2 \lVert d\rVert^2 = 9 \cdot 5 = 45\). Reporting \(5\) is \(\lVert d\rVert^2\). Reporting \(9\) is \(t^2\). Reporting \(-6\) is one component of the displacement, and the squared length is positive.",
        fig=ARR,
        alt=A_ARR,
        preview=P_ARM,
    )
    b.mc(
        4,
        "A Gauss-Newton step fits into this framework as",
        [
            "a stopping test that ignores the residual",
            "one choice of descent direction, built from a linearized residual",
            "a requirement that the step length equal the condition number",
            "a replacement for the objective by a linear program",
        ],
        1,
        r"The framework keeps the update \(x^+ = x + t d\). Gauss-Newton supplies a particular \(d\), by solving a linear least-squares model of the residual. The step length is still free, and a stopping test is still applied. The condition number is not the step length. The objective stays a sum of squares.",
        fig=LEV,
        alt=A_LEV,
        preview=P_GN,
    )
    b.save()


def bank_rates():
    b = Bank("convergence-rates")
    b.mc(
        1,
        r"A sequence of errors \(e_k \to 0\) converges linearly when the successive ratios \(e_{k+1}/e_k\) tend to a limit \(\mu\) with",
        [
            r"\(\mu > 1\)",
            r"\(\mu = 0\)",
            r"\(0 < \mu < 1\)",
            r"\(\mu = 1\)",
        ],
        2,
        r"Linear convergence means the error shrinks by a factor that settles strictly between 0 and 1. A limit above 1 would make the error grow. A limit of 0 is superlinear, which is faster than linear. A limit of 1, with the error still going to 0, is the sublinear pattern of sequences such as \(1/k\).",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.num(
        1,
        r"Three successive errors are \(0.9\), \(0.45\), and \(0.225\). What is the constant successive ratio \(e_{k+1}/e_k\)?",
        0.5,
        "1",
        r"Divide \(0.45\) by \(0.9\), or \(0.225\) by \(0.45\). Both quotients are \(1/2\). The sequence is linear with rate \(1/2\). Reporting \(2\) inverts the ratio. Reporting \(0.225\) repeats the last error. Reporting \(0.9\) repeats the first.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        1,
        r"The errors \(e_k = 1/k\) for \(k \ge 1\) go to zero. Their convergence is",
        [
            r"quadratic, because the errors are a rational function of \(k\)",
            "linear, because they decrease at every step",
            "superlinear, because they have no constant factor",
            "sublinear, because the successive ratios tend to 1",
        ],
        3,
        r"The ratio \((1/(k+1))/(1/k) = k/(k+1)\) tends to 1. The errors go to zero, but not by a factor bounded below 1, so the rate is sublinear. Decreasing at every step is not enough for a linear rate. Superlinear convergence requires the ratio to tend to 0. A rational formula is not the definition of a quadratic rate.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.order(
        2,
        "Put these checks in the order you would apply them to a positive error sequence that tends to zero and might be linear, superlinear, or quadratic. Each step uses the result of the step before it.",
        [
            "Confirm that the errors tend to zero.",
            "Form the successive ratios of one error over the previous error.",
            "If those ratios tend to a limit strictly between 0 and 1, classify the rate as linear.",
            "If those ratios tend to 0, form the ratios of one error over the square of the previous error.",
            "If the ratios against the square stay bounded, classify the rate as quadratic.",
        ],
        r"A rate is a statement about an error that tends to zero, so that check comes first. The successive ratios are the next measurement, and a limit strictly inside \((0, 1)\) already classifies the sequence as linear. Only a ratio limit of 0 opens the superlinear case, and the square in the denominator is the further test that separates quadratic from merely superlinear. Squaring before the successive ratios are known skips the linear case.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.multi(
        2,
        r"Which of these positive sequences converge to zero superlinearly?",
        [
            r"\(e_k = (1/2)^k\)",
            r"\(e_k = (1/2)^{k^2}\)",
            r"\(e_k = 1/k\)",
            r"\(e_k = 1/k!\)",
            r"\(e_k = (9/10)^k\)",
        ],
        [1, 3],
        r"Superlinear convergence means the successive ratio tends to 0."
        "\n"
        r"• \((1/2)^{k^2}\) has ratio \((1/2)^{2k+1}\), which tends to 0."
        "\n"
        r"• \(1/k!\) has ratio \(1/(k+1)\), which tends to 0."
        "\n"
        r"• \((1/2)^k\) has ratio \(1/2\), a linear rate."
        "\n"
        r"• \(1/k\) has ratio tending to 1, a sublinear rate."
        "\n"
        r"• \((9/10)^k\) has ratio \(9/10\), also linear.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.sym(
        2,
        r"The errors obey \(e_{k+1} = c\, e_k\) with \(0 < c < 1\), and \(e_0 = a\). The error \(e_3\) equals",
        "a*c**3",
        {"a": (0.1, 0.8), "c": (0.2, 0.8)},
        r"Apply the recurrence three times: \(e_1 = c a\), \(e_2 = c^2 a\), and \(e_3 = c^3 a\). Both names are required. The product \(a \cdot c\) is only \(e_1\). The power \(c^3\) drops the starting error. The power \(a^3 c\) swaps the roles of the starting error and the rate.",
        alternates=["a*c*c*c", "a*c^3"],
        fig=DECAY,
        alt=A_DECAY,
    )
    b.find_error(
        3,
        r"A note classifies the errors \(1\), \(1/2\), \(1/4\), \(1/8\), and so on. Exactly one step is a false claim.",
        [
            r"The errors are positive and tend to 0.",
            r"Every successive ratio \(e_{k+1}/e_k\) equals \(1/2\).",
            r"A constant ratio strictly between 0 and 1 means the convergence is linear.",
            r"That same constant ratio means the convergence is quadratic.",
        ],
        3,
        r"Halving at every step sends the errors to 0, and the ratio is the constant \(1/2\), which lies in \((0, 1)\). That is linear convergence. It is not quadratic. The quadratic test looks at \(e_{k+1}/e_k^2 = (1/2)/e_k\), and that quantity grows without bound as the error shrinks. A bounded quadratic ratio would have to stay finite.",
        [
            r"The ratio against the square of the error is unbounded, so the rate is not quadratic.",
            r"The successive ratio is not \(1/2\).",
            r"A constant ratio in \((0, 1)\) is superlinear rather than linear.",
        ],
        0,
        fig=DECAY,
        alt=A_DECAY,
    )
    b.num(
        3,
        r"The errors begin \(1/2\), \(1/4\), \(1/16\). This is the start of \(e_{k+1} = e_k^2\). What is \(e_2 / e_1^2\)?",
        1,
        "1",
        r"Index them as \(e_0 = 1/2\), \(e_1 = 1/4\), \(e_2 = 1/16\). Then \(e_1^2 = 1/16\), and the ratio is \(1\). The same value is \(e_1 / e_0^2\). A quadratic rate allows this ratio to stay bounded. Here it equals 1 at every step. Reporting \(1/4\) is the successive ratio \(e_2/e_1\), which is the superlinear test rather than the quadratic one. Reporting \(1/16\) repeats \(e_2\).",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        3,
        r"On a plot of \(\log e_k\) against the iteration index, linear convergence looks like",
        [
            "a horizontal line",
            "a straight line with negative slope",
            "a curve that becomes vertical in a single step and then stops",
            "a straight line with positive slope",
        ],
        1,
        r"If \(e_{k+1} = \mu e_k\) with \(0 < \mu < 1\), then \(\log e_k = \log e_0 + k \log \mu\). The slope \(\log \mu\) is negative, so the plot is a descending straight line. A horizontal line would be a constant error. A positive slope would be growth. A single vertical drop is not the picture of a constant factor applied at every iteration.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        4,
        "Quadratic convergence of an error sequence implies",
        [
            "the successive ratios tend to 0, so the convergence is also superlinear",
            r"the successive ratios tend to a limit in \((0, 1)\), and no faster",
            "the errors are bounded away from zero",
            "the errors form an arithmetic progression",
        ],
        0,
        r"A bounded ratio \(e_{k+1}/e_k^2\) forces \(e_{k+1}/e_k = O(e_k)\) to tend to 0 whenever the error tends to 0. Quadratic convergence is therefore superlinear. A successive-ratio limit in \((0, 1)\) is linear and is strictly slower. An arithmetic progression of errors does not go to zero unless the common difference is zero.",
        fig=FALL,
        alt=A_FALL,
        preview=P_NEWT,
    )
    b.num(
        4,
        r"Two successive errors are \(0.05\) and \(0.01\), and the same ratio continues. What is \(e_{k+1}/e_k\)?",
        0.2,
        "1",
        r"Divide \(0.01\) by \(0.05\). The quotient is \(1/5 = 0.2\). That constant in \((0, 1)\) is a linear rate. Reporting \(5\) inverts the ratio. Reporting \(0.04\) is the difference of the two errors. Reporting \(0.01\) repeats the later error.",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_COND,
    )
    b.mc(
        4,
        r"For a smooth objective that is bounded below, the general gradient method is described by a sublinear guarantee. That name means",
        [
            r"the best squared gradient norm seen so far decays like \(1/k\), slower than a fixed factor each step",
            r"the error is squared at every iteration",
            r"the iterates reach the minimizer in one step",
            r"the successive errors grow by a factor greater than 1",
        ],
        0,
        r"A \(1/k\) bound on the smallest squared gradient norm goes to zero, and the ratio of successive bounds tends to 1. That is sublinear. Squaring the error every iteration would be a quadratic rate, which this general guarantee does not give. One-step termination is finite convergence. A factor greater than 1 is divergence.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_GCONV,
    )
    b.save()


def bank_exact():
    b = Bank("exact-line-search-quadratic")
    b.mc(
        1,
        r"For \(f(x) = \tfrac12 x^T A x + b^T x\) with \(A\) symmetric positive definite, the exact step from \(x\) along a direction \(d \ne 0\) is",
        [
            r"\(t = -\nabla f(x)^T d \,/\, (d^T A d)\)",
            r"\(t = \nabla f(x)^T d \,/\, (d^T d)\)",
            r"\(t = -d^T A d\)",
            r"\(t = 1\) for every direction",
        ],
        0,
        r"The restriction \(\varphi(t) = f(x + t d)\) has derivative \(\nabla f(x)^T d + t\, d^T A d\). Set that derivative to zero and solve. The denominator \(d^T A d\) is the curvature, and it is positive. Dividing by \(d^T d\) forgets the Hessian. The numerator without a denominator is not a step length. The step equals 1 only for special directions.",
        fig=ELL,
        alt=A_ELL,
    )
    b.num(
        1,
        r"Let \(A = \mathrm{diag}(2, 2)\), \(\nabla f(x) = (4, 2)\), and \(d = (-4, -2)\). What is the exact step length?",
        0.5,
        "1",
        r"The numerator is \(-\nabla f^T d = -((4)(-4) + (2)(-2)) = 20\). The denominator is \(d^T A d = 2 \cdot 16 + 2 \cdot 4 = 40\). The step is \(20/40 = 1/2\). This direction is steepest descent, and \(A = 2I\) makes every steepest step equal to \(1/2\). Reporting \(2\) inverts the ratio. Reporting \(20\) stops at the numerator. Reporting \(-1/2\) keeps a minus that the formula has already removed.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        1,
        r"In that formula the denominator \(d^T A d\) is positive, when \(A\) is positive definite and \(d \ne 0\), so the critical point on the line is",
        [
            "a maximum of the restriction",
            "a minimum of the restriction",
            "a point where the restriction is constant",
            "independent of the gradient",
        ],
        1,
        r"The second derivative of the restriction is \(d^T A d\). Positive definiteness makes it positive, so the critical point is a minimum. A maximum would need a negative second derivative. The restriction is constant only when both the slope and the curvature vanish, and the curvature does not. The location of the critical point still uses the directional derivative in the numerator.",
        fig=LEV,
        alt=A_LEV,
    )
    b.order(
        2,
        r"Put these steps in the order that derives the exact step on \(f(x) = \tfrac12 x^T A x + b^T x\). Each step uses the result of the step before it.",
        [
            r"Restrict \(f\) to the line by defining \(\varphi(t) = f(x + t d)\).",
            r"Differentiate to get \(\varphi'(t) = \nabla f(x)^T d + t\, d^T A d\).",
            r"Set that derivative equal to zero.",
            r"Solve for the step \(t = -\nabla f(x)^T d \,/\, (d^T A d)\).",
        ],
        r"The scalar function has to exist before it has a derivative. The derivative is the expression that gets set to zero, and the closed form is the algebra that follows that equation. Solving before the derivative is written does not yet have an equation. Setting the second derivative to zero would fix nothing about \(t\), because the curvature does not depend on \(t\).",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Let \(A = \mathrm{diag}(2, 2)\), \(\nabla f(x) = (4, 0)\), and \(d = (-2, 0)\). Which statements are true?",
        [
            r"The exact step length is \(1\).",
            r"The exact step length is \(1/2\).",
            r"\(\nabla f(x)^T d = -8\).",
            r"\(d^T A d = 4\).",
            r"Every positive step length decreases \(f\).",
        ],
        [0, 2],
        r"Here \(\nabla f^T d = -8\) and \(d^T A d = 2 \cdot 4 = 8\), so the exact step is \(8/8 = 1\)."
        "\n"
        r"• The step \(1\) matches that quotient, and the directional derivative is \(-8\)."
        "\n"
        r"• The step \(1/2\) would be right for a different curvature."
        "\n"
        r"• The curvature is \(8\), not \(4\)."
        "\n"
        r"• The restriction changes by \(-8 t + 4 t^2\), which is negative only for \(t \in (0, 2)\). A step longer than \(2\) increases \(f\).",
        fig=ELL,
        alt=A_ELL,
    )
    b.sym(
        2,
        r"Let \(A = \mathrm{diag}(a, b)\) with \(a > 0\) and \(b > 0\), let the gradient be \((p, q)\), and let the direction be \((u, v) \ne 0\). The exact step length equals",
        "-(p*u+q*v)/(a*u*u+b*v*v)",
        {"p": (1, 4), "q": (1, 4), "u": (-3, -0.5), "v": (-3, -0.5), "a": (1, 4), "b": (1, 4)},
        r"The numerator of the step is the negative directional derivative \(-(p u + q v)\). The denominator is the curvature \(a u^2 + b v^2\). All five names appear. Dropping the leading minus sign selects the maximizer of the upward parabola with the slope flipped. Using \(u^2 + v^2\) in the denominator ignores the diagonal entries of \(A\). Using \(a p^2 + b q^2\) puts the gradient in the curvature slot.",
        alternates=["(-p*u-q*v)/(a*u*u+b*v*v)", "-(p*u+q*v)/(a*u**2+b*v**2)"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        r"A note computes the exact step for \(A = \mathrm{diag}(2, 8)\), gradient \((2, 4)\), and direction \((-1, -1)\). Exactly one step is a false claim.",
        [
            r"The directional derivative at step \(0\) is \(\nabla f^T d = -6\).",
            r"The curvature along \(d\) is \(d^T A d = 10\).",
            r"The line derivative \(-6 + 10 t\) is zero at \(t = 0.6\).",
            r"The exact line search therefore selects \(t = -0.6\).",
        ],
        3,
        r"The directional derivative is \(2 \cdot (-1) + 4 \cdot (-1) = -6\). The curvature is \(2 \cdot 1 + 8 \cdot 1 = 10\). Setting \(-6 + 10 t = 0\) gives \(t = 0.6\). The formula \(t = -(\nabla f^T d)/(d^T A d)\) equals \(-(-6)/10 = 0.6\). The false step puts a minus on that positive root. A negative step would move against the descent direction.",
        [
            r"The root of the line derivative is \(+0.6\). The extra minus sign reverses the step.",
            r"The curvature \(d^T A d\) is not \(10\).",
            r"The directional derivative is not \(-6\).",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"Let \(A = \mathrm{diag}(2, 6)\), \(\nabla f(x) = (4, 3)\), and \(d = (-2, -1)\). What is the exact step length?",
        11 / 14,
        "1",
        r"The numerator is \(-(4 \cdot (-2) + 3 \cdot (-1)) = 11\). The denominator is \(2 \cdot 4 + 6 \cdot 1 = 14\). The step is \(11/14\). Reporting \(14/11\) inverts the ratio. Reporting \(11\) stops at the numerator. Reporting \(-11/14\) keeps a sign the leading minus has already handled.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        3,
        r"When the direction is steepest descent, \(d = -\nabla f(x)\), the exact-step formula simplifies to",
        [
            r"\(t = \lVert\nabla f(x)\rVert^2 \,/\, (\nabla f(x)^T A \nabla f(x))\)",
            r"\(t = \nabla f(x)^T A \nabla f(x)\)",
            r"\(t = -\lVert\nabla f(x)\rVert^2\)",
            r"\(t = 1/\lVert\nabla f(x)\rVert\)",
        ],
        0,
        r"Substitute \(d = -\nabla f\). The numerator \(-\nabla f^T d\) becomes \(\lVert\nabla f\rVert^2\). The denominator \(d^T A d\) becomes \(\nabla f^T A \nabla f\). The curvature alone is not a step length. A leading minus on the squared norm would step backward. The reciprocal of the norm is a different normalization and does not use \(A\).",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        4,
        r"After an exact line search along \(d\), the new gradient satisfies",
        [
            r"\(\nabla f(x^+)^T d = 0\)",
            r"\(\nabla f(x^+) = d\)",
            r"\(\nabla f(x^+) = 0\) in every dimension",
            r"\(\nabla f(x^+)^T d = \nabla f(x)^T d\)",
        ],
        0,
        r"The exact step sets the derivative of the restriction to zero, and that derivative is the new gradient dotted with \(d\). The new gradient equals \(d\) only by coincidence. It equals zero only when the line search happened to land on the minimizer of the whole function. Keeping the old directional derivative would mean the slope never changed, which is the opposite of what the critical-point equation enforces.",
        fig=ZIG,
        alt=A_ZIG,
        preview=P_ZIG,
    )
    b.num(
        4,
        r"Let \(A = \mathrm{diag}(1, 3)\), \(\nabla f(x) = (3, 3)\), and \(d = (-1, -1)\). What is the exact step length?",
        1.5,
        "1",
        r"The numerator is \(-(3 \cdot (-1) + 3 \cdot (-1)) = 6\). The denominator is \(1 \cdot 1 + 3 \cdot 1 = 4\). The step is \(6/4 = 3/2\). Reporting \(4/6\) inverts the ratio. Reporting \(6\) is the numerator. Reporting \(2/3\) is the steepest-descent step for a different matrix that was not given here.",
        fig=LEV,
        alt=A_LEV,
        preview=P_COND,
    )
    b.mc(
        4,
        "Repeating steepest descent with this exact step on a quadratic produces a linear rate governed by",
        [
            r"the smallest entry of \(b\)",
            "the condition number of the Hessian",
            "the number of negative components in the gradient",
            "the value of the objective at the origin only",
        ],
        1,
        r"The classical bound on the excess uses \(\kappa = \lambda_{\max}(A)/\lambda_{\min}(A)\), the condition number of the Hessian. The factor is \(((\kappa - 1)/(\kappa + 1))^2\). The vector \(b\) shifts the minimizer and does not set that ratio. Signs of gradient entries change from step to step. The objective value at the origin is one number, not the rate.",
        fig=ELL,
        alt=A_ELL,
        preview=P_QCONJ,
    )
    b.save()


def bank_armijo():
    b = Bank("armijo-backtracking")
    b.mc(
        1,
        r"The Armijo sufficient-decrease condition, for a step length \(t > 0\) and a parameter \(c \in (0, 1)\), accepts \(t\) when",
        [
            r"\(f(x + t d) \le f(x) + c\, t\, \nabla f(x)^T d\)",
            r"\(f(x + t d) \ge f(x) + t\, \nabla f(x)^T d\)",
            r"\(f(x + t d) = f(x)\)",
            r"\(t\) is larger than \(1\)",
        ],
        0,
        r"Armijo asks the function to fall at least as far as the fraction \(c\) of the directional derivative predicts. Because that derivative is negative and \(c < 1\), the right-hand side lies above the tangent line and below \(f(x)\). The opposite inequality would accept steps that increase \(f\). Equality with the old value is only the boundary case \(c = 0\), which is not a useful test. The step length is not required to exceed 1.",
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        1,
        r"Let \(f(u) = u^2\), so \(f'(u) = 2u\). At \(u = 2\), with \(d = -1\), \(c = 1/4\), and trial step \(t = 1\), what is the Armijo right-hand side \(f(u) + c\, t\, f'(u)\, d\)?",
        3,
        "1",
        r"Here \(f(2) = 4\) and the directional derivative is \(4 \cdot (-1) = -4\). The right-hand side is \(4 + (1/4) \cdot 1 \cdot (-4) = 3\). The trial point is \(u = 1\), where \(f = 1\), and \(1 \le 3\), so the step is accepted. The question asks for the right-hand side, not the new function value. Reporting \(4\) is the old value. Reporting \(1\) is \(f\) at the trial point. Reporting \(-4\) is the directional derivative.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"Backtracking multiplies a rejected trial step by a fixed factor \(\beta \in (0, 1)\). For a descent direction, a short enough trial is accepted because",
        [
            r"the first-order term dominates and \(c < 1\) makes the comparison slope strictly shallower than the tangent",
            r"a positive definite Hessian is required before any trial can pass",
            r"the factor \(\beta\) is larger than 1, so the trials grow",
            r"the directional derivative is positive",
        ],
        0,
        r"The expansion is \(f(x) + t \nabla f^T d + o(t)\). The Armijo line uses the same first-order term multiplied by \(c < 1\). With \(\nabla f^T d < 0\), the function starts out below that shallower line, so a small \(t\) passes. No Hessian hypothesis enters this argument. The factor \(\beta\) is smaller than 1, and the directional derivative of a descent direction is negative.",
        fig=FALL,
        alt=A_FALL,
    )
    b.order(
        2,
        r"Put the backtracking loop in the order it runs. Each step uses the result of the step before it.",
        [
            r"Set the trial step to an initial length \(t_0 > 0\), with parameters \(c \in (0, 1)\) and \(\beta \in (0, 1)\).",
            r"Compare \(f(x + t d)\) with \(f(x) + c\, t\, \nabla f(x)^T d\).",
            r"If the sufficient-decrease inequality fails, replace the trial step by \(\beta t\).",
            r"Repeat the comparison until the inequality holds, then accept that trial.",
        ],
        r"The first trial has to be chosen before it can be tested. The test is the Armijo comparison. Only a failure changes the trial, and the change is a multiplication by \(\beta\). Acceptance is the comparison succeeding, so it cannot come before a comparison has been made. Shrinking the step before the first test would skip a trial that might already have been long enough.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"Let \(f(u) = u^2\) at \(u = 3\), with \(d = -1\) and \(c = 1/2\). The directional derivative is \(-6\). Which trial steps satisfy the Armijo inequality?",
        [
            r"\(t = 1\)",
            r"\(t = 4\)",
            r"\(t = 2\)",
            r"\(t = 5\)",
            r"\(t = 3\)",
        ],
        [0, 2, 4],
        r"The right-hand side is \(9 - 3t\), and \(f(3 - t) = (3 - t)^2\). The inequality \((3 - t)^2 \le 9 - 3t\) simplifies to \(t(t - 3) \le 0\), so \(t \in [0, 3]\)."
        "\n"
        r"• The trials \(1\), \(2\), and \(3\) lie in that interval."
        "\n"
        r"• The trials \(4\) and \(5\) lie beyond it, so they are rejected."
        "\n"
        r"Equality at \(t = 3\) is allowed, because the test uses \(\le\).",
        fig=FALL,
        alt=A_FALL,
    )
    b.sym(
        2,
        r"The current value is \(f_0\), the Armijo parameter is \(c\), the trial step is \(t\), and the directional derivative \(\nabla f^T d\) equals \(s\). The Armijo right-hand side equals",
        "f0+c*t*s",
        {"f0": (1, 8), "c": (0.05, 0.4), "t": (0.2, 2), "s": (-5, -0.2)},
        r"The right-hand side is the current value plus \(c\) times the step times the directional derivative. All four names appear. Using \(f_0 + t s\) sets \(c = 1\) and demands the full linear prediction, which a curved function need not meet. Using \(f_0 + c s\) drops the step length. Subtracting \(c t s\) when \(s\) is already the signed derivative flips a decrease into an increase.",
        alternates=["f0+t*c*s", "f0+s*c*t"],
        fig=SEG,
        alt=A_SEG,
    )
    b.find_error(
        3,
        r"A note states the backtracking test. Exactly one step is a false claim.",
        [
            r"The parameters satisfy \(0 < c < 1\) and \(0 < \beta < 1\).",
            r"The trial point is \(x + t d\) with \(d\) a descent direction.",
            r"The trial is accepted when \(f(x + t d)\) is at least \(f(x) + c\, t\, \nabla f(x)^T d\).",
            r"A rejected trial is replaced by \(\beta t\).",
        ],
        2,
        r"The parameter ranges and the trial point are the standard setup, and a rejection shrinks the step by \(\beta\). The false step reverses the inequality. Sufficient decrease accepts the trial when the new value is at most the right-hand side. The reversed test would accept a step that failed to fall far enough, and it would reject a step that fell even more.",
        [
            r"Acceptance uses \(\le\). The note required the function to sit above the comparison value.",
            r"The shrinkage factor \(\beta\) is required to be larger than 1.",
            r"The direction in the trial point is required to be an ascent direction.",
        ],
        0,
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        3,
        r"Continue \(f(u) = u^2\) at \(u = 2\), with \(d = -1\), \(c = 1/4\), and \(\beta = 1/2\). Start at trial step \(4\), and backtrack until Armijo holds. What step length is accepted?",
        2,
        "1",
        r"The directional derivative is \(-4\), and \(f(2) = 4\). At \(t = 4\) the new value is \(f(-2) = 4\) and the right-hand side is \(4 + (1/4) \cdot 4 \cdot (-4) = 0\), so \(4 \le 0\) fails. At \(t = 2\) the new value is \(f(0) = 0\) and the right-hand side is \(4 - 2 = 2\), so \(0 \le 2\) holds. The accepted step is \(2\). Reporting \(4\) is the rejected start. Reporting \(1\) is the following trial, which also passes but is never tested. Reporting \(0\) is the point that was reached, not the step length.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.mc(
        3,
        r"Making the parameter \(c\) smaller, while keeping it positive, makes the Armijo test",
        [
            "harder, because the comparison line drops faster",
            "easier, because the comparison line drops more slowly",
            "equivalent to requiring an exact line search",
            "independent of the directional derivative",
        ],
        1,
        r"The right-hand side is \(f(x) + c t \nabla f^T d\). With a negative directional derivative, a smaller positive \(c\) subtracts less, so the right-hand side is higher and more trials pass. A larger \(c\), closer to 1, demands a decrease closer to the full linear prediction and is harder. Exact line search asks for a zero derivative along the line, which is a different condition. The directional derivative is still the slope of the comparison.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        4,
        r"The same sufficient-decrease idea, applied to a pure gradient step \(d = -\nabla f\), produces a decrease of size at least a positive multiple of \(\lVert\nabla f\rVert^2\) when the step is shorter than",
        [
            r"twice the reciprocal of a Lipschitz constant of the gradient",
            r"the condition number",
            r"the objective value",
            r"the dimension of \(x\)",
        ],
        0,
        r"If the gradient is Lipschitz with constant \(L\), a gradient step of length \(t \in (0, 2/L)\) is guaranteed to decrease \(f\) by at least \(t(1 - L t/2)\lVert\nabla f\rVert^2\). That upper limit on \(t\) is what makes the coefficient positive. The condition number governs a different, linear rate on quadratics. The objective value and the dimension do not set this step restriction.",
        fig=FALL,
        alt=A_FALL,
        preview=P_SUFF,
    )
    b.num(
        4,
        r"At a scalar point, \(f = 1\), the directional derivative is \(-5\), \(c = 1/5\), and \(t = 2\). How far below \(f\) does the Armijo right-hand side sit? Report that positive gap.",
        2,
        "1",
        r"The right-hand side is \(1 + (1/5) \cdot 2 \cdot (-5) = 1 - 2 = -1\). It sits \(1 - (-1) = 2\) below the current value. Equivalently, the gap is \(-c t\) times the directional derivative, which is \((1/5) \cdot 2 \cdot 5 = 2\). Reporting \(-1\) gives the right-hand side itself. Reporting \(1\) is the current value. Reporting \(5\) is the absolute directional derivative.",
        fig=SEG,
        alt=A_SEG,
        preview=P_WOLFE,
    )
    b.mc(
        4,
        "A Newton step that has been shortened by this backtracking loop is",
        [
            "no longer using the Hessian at all",
            "a damped Newton iteration: the direction stays Newton and the step length is reduced until sufficient decrease holds",
            "the simplex method",
            "an exact line search on a nonquadratic model, with no further test",
        ],
        1,
        r"Backtracking does not change the direction. It only reduces \(t\) in \(x + t d\). When \(d\) is the Newton direction, the result is a damped Newton step. The Hessian was used to build \(d\). The simplex method is a different iteration. An exact line search would minimize the restriction, which backtracking does not claim to do.",
        fig=ELL,
        alt=A_ELL,
        preview=P_NGLOB,
    )
    b.save()


def bank_zigzag():
    b = Bank("gradient-zigzag")
    b.mc(
        1,
        "With exact line search, successive steepest-descent directions are orthogonal because",
        [
            r"the new gradient is orthogonal to the old gradient",
            r"the Hessian is always a multiple of the identity",
            r"the step length is always 1",
            r"the two directions are parallel by construction",
        ],
        0,
        r"Exact line search makes the new gradient orthogonal to the step just taken. For steepest descent that step is the negative of the old gradient, so the new gradient is orthogonal to the old one. The next steepest direction, the negative of the new gradient, is therefore orthogonal to the previous direction. The Hessian need not be a multiple of the identity. That special case actually finishes in one step. The step length is not constantly 1, and orthogonal directions are not parallel.",
        fig=ZIG,
        alt=A_ZIG,
    )
    b.num(
        1,
        r"Let \(f(x) = \tfrac12 x^T A x\) with \(A = \mathrm{diag}(1, 2)\), and start at \(x = (2, 1)\). The gradient is \((2, 2)\). What exact steepest-descent step length is taken?",
        2 / 3,
        "1",
        r"For \(d = -\nabla f\), the step is \(\lVert\nabla f\rVert^2 / (\nabla f^T A \nabla f)\). The squared norm is \(8\). Then \(A \nabla f = (2, 4)\) and the curvature is \(4 + 8 = 12\). The step is \(8/12 = 2/3\). Reporting \(12/8\) inverts the ratio. Reporting \(8\) is the squared norm. Reporting \(1\) would be the step for \(A = I\), which this diagonal is not.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        1,
        "On a long, thin elliptical level set, steepest descent zigzags because",
        [
            r"each step is perpendicular to the contour and the next contour crossing is almost back along the thin direction",
            r"the gradient is constant on an ellipse",
            r"exact line search forces consecutive steps to be parallel",
            r"a round level set, with equal eigenvalues, produces the most zigzags",
        ],
        0,
        r"The negative gradient is perpendicular to the level set. On a very elongated ellipse that perpendicular hits the opposite side quickly, and the new perpendicular is almost a reversal. The gradient changes from point to point on an ellipse. Exact line search makes consecutive steepest steps orthogonal, not parallel. Equal eigenvalues make the level sets round, and one exact steepest step reaches the center.",
        fig=LEV,
        alt=A_LEV,
    )
    b.order(
        2,
        "Put these steps in the order that shows successive steepest directions are orthogonal. Each step uses the result of the step before it.",
        [
            r"Exact line search sets the derivative of \(f\) along the step to zero.",
            "That derivative is the new gradient dotted with the step direction.",
            "The steepest direction just used was the negative of the old gradient.",
            "The new gradient is therefore orthogonal to the old gradient.",
            "The next steepest direction, the negative of the new gradient, is orthogonal to the previous step.",
        ],
        r"The line search is what produces a zero derivative, and that derivative is the new orthogonality relation. Identifying the step with the old negative gradient turns orthogonality to the step into orthogonality of the two gradients. The next direction is defined from the new gradient, so it inherits that right angle. Claiming the directions are orthogonal before the line search has set the derivative skips the only fact that forces the angle.",
        fig=ZIG,
        alt=A_ZIG,
    )
    b.multi(
        2,
        "Which of these pairs of successive steepest directions are orthogonal?",
        [
            r"\((-1, 2)\) and \((2, 1)\)",
            r"\((1, 1)\) and \((1, -1)\)",
            r"\((2, 0)\) and \((1, 1)\)",
            r"\((3, -1)\) and \((1, 3)\)",
            r"\((1, 2)\) and \((2, 2)\)",
        ],
        [0, 1, 3],
        r"Orthogonality is a zero dot product."
        "\n"
        r"• \((-1, 2)\cdot(2, 1) = -2 + 2 = 0\)."
        "\n"
        r"• \((1, 1)\cdot(1, -1) = 1 - 1 = 0\)."
        "\n"
        r"• \((3, -1)\cdot(1, 3) = 3 - 3 = 0\)."
        "\n"
        r"• \((2, 0)\cdot(1, 1) = 2\)."
        "\n"
        r"• \((1, 2)\cdot(2, 2) = 6\)."
        "\n"
        r"The last two pairs are not orthogonal.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.sym(
        2,
        r"The Hessian is \(p\) times the identity, and the nonzero gradient is \((u, v)\). The exact steepest-descent step length equals",
        "(u*u+v*v)/(p*(u*u+v*v))",
        {"p": (1, 4), "u": (0.5, 2), "v": (0.5, 2)},
        r"The general steepest step is \(\lVert g\rVert^2 / (g^T A g)\). With \(A = p I\), the denominator is \(p(u^2 + v^2)\), so the ratio collapses to \(1/p\). All three names appear before that cancellation. Leaving \(p\) out of the denominator is the step for the identity Hessian. Using \(p\) in the numerator inverts the step. The product \(u v\) is not the squared norm.",
        alternates=["1/p", "(u**2+v**2)/(p*u**2+p*v**2)"],
        fig=ZIG,
        alt=A_ZIG,
    )
    b.find_error(
        3,
        "A note explains the turn in steepest descent. Exactly one step is a false claim.",
        [
            "Exact line search makes the new gradient orthogonal to the step just taken.",
            "For steepest descent that step is the negative gradient, so successive gradients are orthogonal.",
            "Euclidean orthogonality of those gradients is the same as conjugacy with respect to every positive definite Hessian.",
            r"Without conjugacy, steepest descent need not reach the minimizer in \(n\) steps.",
        ],
        2,
        r"Exact line search gives \(\nabla f(x^+)^T d = 0\), and \(d = -\nabla f(x)\) turns that into orthogonality of successive gradients. Conjugacy of two directions is \(d_i^T A d_j = 0\). Euclidean orthogonality is \(d_i^T d_j = 0\). Those agree for every positive definite \(A\) only when \(A\) is a multiple of the identity. In that special case the method finishes in one step. In general, orthogonality does not give the finite termination that conjugacy gives, so the last step stands.",
        [
            r"Conjugacy is \(d_i^T A d_j = 0\). Euclidean orthogonality does not include \(A\).",
            r"Exact line search does not make the new gradient orthogonal to the step.",
            r"Steepest descent with exact line search reaches every quadratic minimizer in one step, in every dimension.",
        ],
        0,
        fig=ELL,
        alt=A_ELL,
    )
    b.num(
        3,
        r"Let \(A = \mathrm{diag}(2, 6)\) and start steepest descent with exact line search at \(x = (3, 1)\), where the gradient is \((6, 6)\). The step length is \(1/4\), and the next point is \((3/2, -1/2)\). What is the squared Euclidean norm of the new gradient?",
        18,
        "1",
        r"The new gradient is \(A\) times the new point, \((2 \cdot 3/2,\ 6 \cdot (-1/2)) = (3, -3)\). Its squared norm is \(9 + 9 = 18\). The old gradient \((6, 6)\) dots with \((3, -3)\) to give 0, which is the orthogonality this step is built on. Reporting \(72\) repeats the old squared norm. Reporting \(9\) is only one of the two squares. Reporting \(0\) is that dot product, not the squared norm.",
        fig=ZIG,
        alt=A_ZIG,
    )
    b.mc(
        3,
        "The zigzag becomes more severe when the condition number of the Hessian grows, because",
        [
            r"the level sets become longer relative to their width, so each perpendicular step overshoots the long axis",
            r"the level sets become circles",
            r"the exact step length tends to infinity for a fixed gradient",
            r"successive gradients stop being orthogonal",
        ],
        0,
        r"A large ratio of extreme eigenvalues stretches the elliptical level sets. The geometry of the perpendicular steps then folds into a tight zigzag, and the contraction factor moves toward 1. Equal eigenvalues make circles, which are the mild case. The exact step for a fixed gradient stays finite. Orthogonality of successive gradients holds for every positive definite Hessian, including a well-conditioned one.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        4,
        "The linear rate that measures this zigzag on a quadratic is a function of",
        [
            r"the condition number \(\kappa = \lambda_{\max}/\lambda_{\min}\)",
            r"the trace of the Hessian alone, with no ratio",
            r"the starting objective value alone",
            r"the number of zero components in the first gradient",
        ],
        0,
        r"The excess contracts by at most \(((\kappa - 1)/(\kappa + 1))^2\). The trace is the sum of the eigenvalues, and two Hessians with the same trace can have very different ratios. The starting value scales the excess and does not set the factor. Sparsity of the first gradient is an accident of the coordinates.",
        fig=LEV,
        alt=A_LEV,
        preview=P_COND,
    )
    b.num(
        4,
        r"Let \(A = \mathrm{diag}(1, 5)\) and start at \(x = (5, 1)\), where the gradient is \((5, 5)\). What exact steepest-descent step length is taken?",
        1 / 3,
        "1",
        r"The squared gradient norm is \(50\). Then \(A \nabla f = (5, 25)\) and the curvature is \(25 + 125 = 150\). The step is \(50/150 = 1/3\). Reporting \(3\) inverts the ratio. Reporting \(150\) is the curvature. Reporting \(1\) would require the curvature to equal the squared norm, which would mean \(A\) is the identity on the span of the gradient.",
        fig=FALL,
        alt=A_FALL,
        preview=P_QCONJ,
    )
    b.mc(
        4,
        "Conjugate directions improve on this zigzag by replacing Euclidean orthogonality with",
        [
            r"\(d_i^T A d_j = 0\), which gives finite termination on a quadratic",
            r"\(d_i = d_j\) for every pair",
            r"a requirement that every step length equal the condition number",
            r"dropping the line search",
        ],
        0,
        r"Conjugacy uses the Hessian in the inner product. On a positive definite quadratic, a set of \(n\) conjugate directions with exact line search reaches the minimizer in at most \(n\) steps. Repeating one direction cannot span the space. The condition number is not a step length. The line search is still what picks the coefficient of each direction.",
        fig=MAT,
        alt=A_MAT,
        preview=P_QCONJ,
    )
    b.save()


def bank_condition():
    b = Bank("condition-number-gradient-rate")
    b.mc(
        1,
        r"For steepest descent with exact line search on \(f(x) = \tfrac12 x^T A x + b^T x\), with \(A\) positive definite and \(\kappa = \lambda_{\max}(A)/\lambda_{\min}(A)\), the excess \(f - f^\star\) contracts by at most",
        [
            r"\(((\kappa - 1)/(\kappa + 1))^2\)",
            r"\((\kappa - 1)/(\kappa + 1)\), with no square",
            r"\(\kappa\) itself",
            r"\(1/\kappa^2\)",
        ],
        0,
        r"The classical bound multiplies the excess by \(((\kappa - 1)/(\kappa + 1))^2\). The unsquared factor bounds the error in the \(A\)-norm, and the excess is half the square of that norm, so the excess carries the square. Using \(\kappa\) itself is larger than 1 for \(\kappa > 1\) and cannot be a contraction. The factor \(1/\kappa^2\) is a different estimate and is not this bound.",
        fig=ELL,
        alt=A_ELL,
    )
    b.num(
        1,
        r"The Hessian eigenvalues are \(1\) and \(3\), so \(\kappa = 3\). What is the contraction factor \(((\kappa - 1)/(\kappa + 1))^2\)?",
        0.25,
        "1",
        r"The ratio is \((3 - 1)/(3 + 1) = 1/2\), and the factor on the excess is the square, \(1/4\). Reporting \(1/2\) stops before the square. Reporting \(3\) is the condition number. Reporting \(2\) is \(\kappa - 1\).",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        1,
        r"As \(\kappa\) increases from \(1\), this factor",
        [
            r"increases toward \(1\), so the guaranteed linear rate gets slower",
            r"decreases toward \(0\), so the guarantee gets faster",
            r"stays equal to \(\kappa\)",
            r"becomes negative",
        ],
        0,
        r"At \(\kappa = 1\) the factor is \(0\), which matches one-step termination on a multiple of the identity. As \(\kappa\) grows, \((\kappa - 1)/(\kappa + 1)\) grows toward \(1\), and so does its square. A larger factor is a slower guarantee. The factor is not equal to \(\kappa\), and both \(\kappa - 1\) and \(\kappa + 1\) are positive for \(\kappa > 1\), so the factor stays positive.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.order(
        2,
        "Put these steps in the order that turns eigenvalues into a bound on the next excess. Each step uses the result of the step before it.",
        [
            "Read off the largest and smallest eigenvalues of the positive definite Hessian.",
            r"Form the condition number \(\kappa\) as their ratio.",
            r"Square the quotient \((\kappa - 1)/(\kappa + 1)\).",
            "Multiply the current excess by that square to bound the excess at the next exact steepest step.",
        ],
        r"The eigenvalues are the inputs. Their ratio is \(\kappa\), and the contraction factor is built from that ratio by subtracting, adding, dividing, and squaring. Only then is the factor applied to the excess. Squaring before the condition number exists has nothing to square. Multiplying the excess by an eigenvalue, rather than by the factor, is a different quantity.",
        fig=MAT,
        alt=A_MAT,
    )
    b.multi(
        2,
        r"The contraction factor on the excess is at most \(1/4\). Which of these Hessian eigenvalue pairs qualify?",
        [
            r"\(1\) and \(2\)",
            r"\(2\) and \(6\)",
            r"\(1\) and \(9\)",
            r"\(4\) and \(4\)",
            r"\(1\) and \(7\)",
        ],
        [0, 1, 3],
        r"The factor \(((\kappa - 1)/(\kappa + 1))^2\) is at most \(1/4\) exactly when \(\kappa \le 3\)."
        "\n"
        r"• Eigenvalues \(1, 2\) give \(\kappa = 2\)."
        "\n"
        r"• Eigenvalues \(2, 6\) give \(\kappa = 3\), and the factor equals \(1/4\)."
        "\n"
        r"• Eigenvalues \(4, 4\) give \(\kappa = 1\), and the factor is \(0\)."
        "\n"
        r"• Eigenvalues \(1, 9\) give \(\kappa = 9\), and the factor is \(0.64\)."
        "\n"
        r"• Eigenvalues \(1, 7\) give \(\kappa = 7\), and the factor is \(0.5625\).",
        fig=ELL,
        alt=A_ELL,
    )
    b.sym(
        2,
        r"The current excess is \(\mathrm{gap} > 0\) and the condition number is \(r > 1\). The bound on the next excess equals",
        "gap*((r-1)/(r+1))**2",
        {"gap": (0.2, 5), "r": (1.2, 8)},
        r"Multiply the excess by the squared factor. Both names appear. Dropping the square leaves the \(A\)-norm factor, which is the wrong power for the excess. Using \((r + 1)/(r - 1)\) inverts the factor and produces a number larger than 1. Subtracting the factor from the excess, instead of multiplying, is a different operation.",
        alternates=["gap*(r-1)**2/(r+1)**2", "((r-1)/(r+1))**2*gap"],
        fig=DECAY,
        alt=A_DECAY,
    )
    b.find_error(
        3,
        r"A note treats \(\kappa = 3\). Exactly one step is a false claim.",
        [
            r"The condition number is \(\lambda_{\max}/\lambda_{\min} = 3\).",
            r"\((\kappa - 1)/(\kappa + 1) = 1/2\).",
            r"The contraction factor for the excess \(f - f^\star\) is \(1/2\).",
            r"Increasing \(\kappa\) moves the factor toward \(1\), which is a slower guarantee.",
        ],
        2,
        r"The ratio of eigenvalues is \(3\), and \((3 - 1)/(3 + 1) = 1/2\). The excess is quadratic in the \(A\)-norm error, so the factor on the excess is the square, \(1/4\). The false step stops at \(1/2\). The last step is the right monotonicity: a larger condition number pushes the factor toward 1.",
        [
            r"The excess picks up the square, so the factor is \(1/4\), not \(1/2\).",
            r"\((\kappa - 1)/(\kappa + 1)\) is not \(1/2\) when \(\kappa = 3\).",
            r"A larger condition number makes the factor smaller.",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"The condition number is \(5\), and the current excess is \(9\). What is the bound on the next excess?",
        4,
        "1",
        r"The unsquared quotient is \((5 - 1)/(5 + 1) = 2/3\). Its square is \(4/9\). Then \(9 \cdot (4/9) = 4\). Reporting \(6\) uses \(2/3\) without the square, since \(9 \cdot 2/3 = 6\). Reporting \(5\) is the condition number. Reporting \(9\) leaves the excess unchanged.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        3,
        r"When the factor \(((\kappa - 1)/(\kappa + 1))^2\) lies in \((0, 1)\), the bound is a statement of",
        [
            "quadratic convergence",
            "linear convergence of the excess",
            "failure to converge",
            r"finite termination in two steps for every \(\kappa\)",
        ],
        1,
        r"Multiplying the excess by the same number in \((0, 1)\) at every step is linear convergence. Quadratic convergence would square the error. A factor in \((0, 1)\) still goes to zero, so it is not a failure. Finite termination for every condition number is false. It happens for the factor \(0\), which is the case \(\kappa = 1\).",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        4,
        "Conjugate gradients improve the dependence on this condition number by",
        [
            r"building conjugate directions, with a faster guarantee in \(\kappa\) than steepest descent",
            r"replacing \(\kappa\) by \(\kappa^2\) in the same steepest-descent factor",
            r"using a step length equal to \(\kappa\)",
            r"ignoring the Hessian entirely",
        ],
        0,
        r"The steepest-descent factor approaches \(1\) like \(1 - 2/\kappa\). Conjugate gradients use an inner product built from the Hessian and have a contraction that behaves like \(((\sqrt{\kappa} - 1)/(\sqrt{\kappa} + 1))^2\), which is much closer to zero for large \(\kappa\). Squaring \(\kappa\) inside the steepest factor would make the bound worse. The step length is not \(\kappa\). The Hessian is exactly what the conjugacy uses.",
        fig=ELL,
        alt=A_ELL,
        preview=P_CG,
    )
    b.num(
        4,
        r"The Hessian eigenvalues are \(2\) and \(8\). What is the contraction factor on the excess?",
        0.36,
        "1",
        r"The condition number is \(8/2 = 4\). Then \((4 - 1)/(4 + 1) = 3/5\), and the square is \(9/25 = 0.36\). Reporting \(0.6\) stops before the square. Reporting \(4\) is the condition number. Reporting \(0.25\) is the factor for \(\kappa = 3\), not for \(\kappa = 4\).",
        fig=MAT,
        alt=A_MAT,
        preview=P_HB,
    )
    b.mc(
        4,
        "A momentum step such as the heavy-ball update uses this condition number to",
        [
            r"choose a momentum weight that improves on the steepest-descent factor",
            r"set the objective equal to \(\kappa\)",
            r"force every eigenvalue of the Hessian to equal 1",
            r"replace the gradient by the zero vector",
        ],
        0,
        r"The heavy-ball iteration adds a multiple of the previous step. On a quadratic, that weight can be chosen from \(\kappa\), and the resulting rate beats \(((\kappa - 1)/(\kappa + 1))^2\). The objective is not set equal to \(\kappa\). The eigenvalues stay whatever the Hessian has. The gradient is still evaluated.",
        fig=LEV,
        alt=A_LEV,
        preview=P_HB,
    )
    b.save()


def bank_lipschitz():
    b = Bank("lipschitz-gradient")
    b.mc(
        1,
        r"The gradient of \(f\) is Lipschitz continuous with constant \(L\) when, for every pair of points,",
        [
            r"\(\lVert\nabla f(y) - \nabla f(x)\rVert \le L \lVert y - x\rVert\)",
            r"\(\lVert\nabla f(y) - \nabla f(x)\rVert \ge L \lVert y - x\rVert\)",
            r"\(f(y) = f(x)\)",
            r"the Hessian is the zero matrix",
        ],
        0,
        r"Lipschitz continuity of the gradient bounds how fast the gradient can change. The inequality runs from the gradient difference to \(L\) times the distance. The reversed inequality would be a lower bound on the change. Equal function values are a different condition. A zero Hessian gives \(L = 0\), which is the special case of an affine function, not the definition.",
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        1,
        r"Let \(f(x_1, x_2) = 3 x_1^2 + x_2^2\). The Hessian is \(\mathrm{diag}(6, 2)\). What Lipschitz constant of the gradient is given by the induced 2-norm of this Hessian?",
        6,
        "1",
        r"For a symmetric matrix the induced 2-norm is the largest absolute eigenvalue. Here the eigenvalues are \(6\) and \(2\), so the norm is \(6\). A constant Hessian equal to that matrix makes \(6\) a sharp Lipschitz constant of the gradient. Reporting \(2\) uses the smaller eigenvalue. Reporting \(8\) adds them. Reporting \(12\) doubles the larger one.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        1,
        r"If the induced 2-norm of the Hessian is at most \(L\) at every point of a convex domain, then",
        [
            r"\(L\) is a Lipschitz constant of the gradient",
            r"\(L\) is a Lipschitz constant only when it is smaller than every eigenvalue",
            r"the gradient is constant",
            r"\(f\) is necessarily a linear program",
        ],
        0,
        r"The fundamental theorem along the segment writes the gradient difference as an integral of Hessian-vector products. Bounding each product by the induced norm produces \(\lVert\nabla f(y) - \nabla f(x)\rVert \le L \lVert y - x\rVert\). A constant smaller than the norm is not enough. The gradient is constant only for \(L = 0\). A bound on the Hessian does not make the objective linear.",
        fig=ELL,
        alt=A_ELL,
    )
    b.order(
        2,
        "Put these steps in the order that produces a Lipschitz constant from a twice differentiable objective. Each step uses the result of the step before it.",
        [
            r"Form the Hessian of \(f\).",
            "At each point, compute the induced 2-norm of that Hessian.",
            r"Choose \(L\) at least as large as every one of those norms.",
            r"Use that \(L\) as a Lipschitz constant of the gradient.",
        ],
        r"The Hessian is the derivative of the gradient, so it comes first. The induced norm turns the matrix into a scalar bound at each point. A single \(L\) has to dominate all of those scalars before it can be called a Lipschitz constant on the whole domain. Choosing \(L\) before the norms are known has nothing to dominate.",
        fig=MAT,
        alt=A_MAT,
    )
    b.multi(
        2,
        r"The induced 2-norm of the Hessian equals \(5\) at every point. Which numbers are valid Lipschitz constants of the gradient?",
        [
            r"\(5\)",
            r"\(4\)",
            r"\(7\)",
            r"\(5.5\)",
            r"\(1\)",
        ],
        [0, 2, 3],
        r"Any number at least \(5\) works, and a smaller number does not dominate the Hessian norm."
        "\n"
        r"• \(5\), \(5.5\), and \(7\) are large enough."
        "\n"
        r"• \(4\) and \(1\) are strictly below \(5\), so neither is a Lipschitz constant for this gradient.",
        fig=BALL,
        alt=A_BALL,
    )
    b.sym(
        2,
        r"Let \(f(x) = \tfrac12 \lVert A x - b\rVert^2\) with the single column \(A = (p, q)\). The Hessian is the scalar \(p^2 + q^2\). A sharp Lipschitz constant of the gradient equals",
        "p*p+q*q",
        {"p": (1, 3), "q": (1, 3)},
        r"The Hessian of \(\tfrac12 \lVert A x - b\rVert^2\) is \(A^T A\). For one column that product is \(p^2 + q^2\), and a \(1 \times 1\) positive semidefinite Hessian has induced norm equal to itself. Both names appear. The sum \(p + q\) forgets the squares. The product \(p q\) is an off-diagonal entry that this one-column Gram matrix does not have. Doubling the sum would be the Hessian of \(\lVert A x - b\rVert^2\) without the one-half.",
        alternates=["p**2+q**2", "q*q+p*p"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        r"A note reads a constant Hessian with eigenvalues \(2\) and \(8\). Exactly one step is a false claim.",
        [
            r"The Hessian is symmetric, with eigenvalues \(2\) and \(8\).",
            r"Its induced 2-norm is the largest absolute eigenvalue, which is \(8\).",
            r"The Lipschitz constant of the gradient is the smallest eigenvalue, \(2\).",
            r"Any number at least \(8\), for instance \(10\), is also a Lipschitz constant of this gradient.",
        ],
        2,
        r"A symmetric matrix has induced 2-norm equal to its spectral radius, here \(8\). That norm is a sharp Lipschitz constant, and every larger number is also valid. The false step uses the smaller eigenvalue. The value \(2\) does not dominate a Hessian that stretches by \(8\).",
        [
            r"The smallest eigenvalue does not dominate the Hessian. The induced norm is \(8\).",
            r"The induced 2-norm is the smallest eigenvalue.",
            r"A number larger than \(8\) cannot be a Lipschitz constant.",
        ],
        0,
        fig=ELL,
        alt=A_ELL,
    )
    b.num(
        3,
        r"Let \(f(x) = \tfrac12 \lVert A x - b\rVert^2\) with \(A = \begin{bmatrix} 2 & 0 \\ 0 & 1 \\ 1 & 0 \end{bmatrix}\). The Gram matrix \(A^T A\) equals \(\mathrm{diag}(5, 1)\). What is a sharp Lipschitz constant of the gradient?",
        5,
        "1",
        r"The Hessian is \(A^T A\), with eigenvalues \(5\) and \(1\). The induced 2-norm is \(5\), and that is the sharp Lipschitz constant. The same number is the square of the largest singular value of \(A\): the column norms lead to singular values \(\sqrt{5}\) and \(1\), and \((\sqrt{5})^2 = 5\). Reporting \(1\) uses the smaller eigenvalue. Reporting \(6\) adds the diagonal entries. Reporting \(\sqrt{5}\) stops at the singular value and forgets the square.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        3,
        r"For \(f(x) = \tfrac12 \lVert A x - b\rVert^2\), a sharp Lipschitz constant of the gradient is",
        [
            r"\(\lVert A\rVert_2^2\)",
            r"\(\lVert A\rVert_2\)",
            r"the smallest singular value of \(A\)",
            r"\(\lVert b\rVert\)",
        ],
        0,
        r"The Hessian is \(A^T A\), whose eigenvalues are the squares of the singular values of \(A\). The induced 2-norm of the Hessian is therefore \(\sigma_{\max}(A)^2 = \lVert A\rVert_2^2\). The singular value without the square is the norm of \(A\), not of \(A^T A\). The smallest singular value bounds nothing from above. The vector \(b\) shifts the residual and does not appear in the Hessian.",
        fig=BALL,
        alt=A_BALL,
    )
    b.mc(
        4,
        "A quadratic upper bound that uses this Lipschitz constant is",
        [
            r"the descent lemma, \(f(y) \le f(x) + \nabla f(x)^T(y - x) + (L/2)\lVert y - x\rVert^2\)",
            r"the first-order convexity inequality, which runs the other way",
            r"a statement that \(f\) is constant",
            r"the normal equations of a linear program",
        ],
        0,
        r"Once the gradient is Lipschitz with constant \(L\), integrating the remainder produces a quadratic upper model with coefficient \(L/2\). That upper bound is the descent lemma. First-order convexity is a linear lower bound and does not use \(L\). The upper model does not force \(f\) to be constant. The normal equations are a stationarity condition for least squares.",
        fig=LEV,
        alt=A_LEV,
        preview=P_DLEM,
    )
    b.num(
        4,
        r"Let \(f(t) = 2 t^2\), so \(f'(t) = 4t\). What is \(\lvert f'(3) - f'(1)\rvert \,/\, \lvert 3 - 1\rvert\)?",
        4,
        "1",
        r"The derivatives are \(f'(3) = 12\) and \(f'(1) = 4\). The absolute difference is \(8\), and the distance is \(2\), so the quotient is \(4\). The second derivative is the constant \(4\), which is why every such quotient equals \(4\). Reporting \(8\) stops before dividing by the distance. Reporting \(2\) is the distance. Reporting \(12\) is one derivative.",
        fig=RISE,
        alt=A_RISE,
        preview=P_NEWT,
    )
    b.mc(
        4,
        "A local quadratic rate for Newton's method asks this Lipschitz idea of",
        [
            r"the Hessian, so the derivative of the Newton map stays controlled near a minimizer",
            r"the objective value alone, with no derivative",
            r"a line-search parameter \(c > 1\)",
            r"the simplex ratio test",
        ],
        0,
        r"The standard local analysis assumes the Hessian itself is Lipschitz near a point where it is positive definite. That bounds how fast the Newton correction changes, and it is what produces the quadratic rate. The objective value is not the object of that hypothesis. An Armijo parameter is at most 1. The simplex ratio test belongs to linear programming.",
        fig=FALL,
        alt=A_FALL,
        preview=P_NEWT,
    )
    b.save()


def bank_descent_lemma():
    b = Bank("descent-lemma")
    b.mc(
        1,
        r"If the gradient is Lipschitz with constant \(L\), the descent lemma says",
        [
            r"\(f(y) \le f(x) + \nabla f(x)^T(y - x) + (L/2)\lVert y - x\rVert^2\)",
            r"\(f(y) \ge f(x) + \nabla f(x)^T(y - x) + (L/2)\lVert y - x\rVert^2\)",
            r"\(f(y) \le f(x) + (L/2)\lVert y - x\rVert^2\), with no linear term",
            r"\(f(y) = f(x)\) for every \(y\)",
        ],
        0,
        r"The lemma is an upper bound: the linear model plus a quadratic penalty of coefficient \(L/2\). The reversed inequality is not what Lipschitz continuity of the gradient gives. Dropping the linear term is valid only when the gradient vanishes. The bound does not force \(f\) to be constant.",
        fig=LEV,
        alt=A_LEV,
    )
    b.num(
        1,
        r"Let \(f(t) = 2 t^2\), which has Lipschitz constant \(L = 4\) for its derivative. At \(t = 1\), \(f = 2\) and \(f' = 4\). What upper bound does the descent lemma give at \(t = 2\)?",
        8,
        "1",
        r"The step is \(d = 1\). The bound is \(2 + 4 \cdot 1 + (4/2) \cdot 1^2 = 2 + 4 + 2 = 8\). The true value \(f(2) = 8\) meets the bound, which is what a sharp constant does for this quadratic. Reporting \(6\) forgets the quadratic term. Reporting \(2\) is the old value. Reporting \(4\) is the derivative.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        1,
        "The descent lemma needs a Lipschitz gradient. It does not need",
        [
            r"convexity of \(f\)",
            r"differentiability of \(f\)",
            r"a finite constant \(L\)",
            r"the points to be joined by a segment",
        ],
        0,
        r"The proof integrates the gradient along the segment and bounds the change in the gradient by \(L\). Convexity is a different hypothesis and produces a lower bound, not this upper bound. Differentiability is already part of having a gradient. The constant has to be finite, and the segment is the path the integral uses.",
        fig=SEG,
        alt=A_SEG,
    )
    b.order(
        2,
        "Put these steps in the order of the proof of the descent lemma. Each step uses the result of the step before it.",
        [
            r"Write \(f(y) - f(x)\) as the integral of \(\nabla f(x + t(y - x))^T(y - x)\) for \(t\) from \(0\) to \(1\).",
            r"Split the integrand into \(\nabla f(x)^T(y - x)\) plus the change in the gradient.",
            r"Bound that change by \(L t \lVert y - x\rVert^2\), using the Lipschitz condition.",
            r"Integrate the bound in \(t\) from \(0\) to \(1\) to produce the term \((L/2)\lVert y - x\rVert^2\).",
        ],
        r"The integral representation comes first. Splitting off the known gradient leaves the remainder that the Lipschitz condition can bound. The factor \(t\) in that bound is what integrates to \(1/2\). Integrating before the bound exists does not yet produce \(L/2\).",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Let \(f(t) = t^2\), whose derivative has sharp Lipschitz constant \(L = 2\). Which statements are true?",
        [
            r"With \(L = 2\), the descent-lemma upper bound equals \(f(y)\) for every \(y\).",
            r"Replacing \(L\) by \(1\) makes the bound fail for some \(y\).",
            r"Replacing \(L\) by \(4\) keeps a valid upper bound.",
            r"The bound does not use the gradient.",
            r"\(L = 0\) is a valid Lipschitz constant of this derivative.",
        ],
        [0, 1, 2],
        r"For a quadratic whose Hessian equals \(L\), the descent lemma is an equality."
        "\n"
        r"• With \(L = 2\), the upper bound simplifies to \(y^2\), which is \(f(y)\)."
        "\n"
        r"• At \(x = 1\) and \(y = 3\), the bound with \(L = 1\) is \(1 + 2 \cdot 2 + (1/2) \cdot 4 = 7\), while \(f(3) = 9\)."
        "\n"
        r"• Any larger constant, including \(4\), still dominates the Hessian norm."
        "\n"
        r"• The linear term is the gradient. Dropping it is a different expression."
        "\n"
        r"• \(L = 0\) would require a constant derivative, and \(f'(t) = 2t\) is not constant.",
        fig=LEV,
        alt=A_LEV,
    )
    b.sym(
        2,
        r"The value \(f(x)\) is \(f_0\), the directional derivative along a step of length \(h\) is \(g \cdot h\) with slope \(g\), and the Lipschitz constant is \(\mathrm{ell}\). The descent-lemma upper bound equals",
        "f0+g*h+ell*h*h/2",
        {"f0": (0, 4), "g": (-2, 2), "h": (0.5, 2), "ell": (1, 4)},
        r"The bound is the current value, plus the linear term \(g h\), plus \((\mathrm{ell}/2) h^2\). All four names appear. Using \(\mathrm{ell}\, h^2\) without the one-half doubles the quadratic term. Dropping \(g h\) erases the slope. Subtracting the quadratic term produces a lower model, which is not the lemma.",
        alternates=["f0+g*h+(ell/2)*h*h", "f0+h*g+ell*h**2/2"],
        fig=RISE,
        alt=A_RISE,
    )
    b.find_error(
        3,
        "A note records the descent lemma. Exactly one step is a false claim.",
        [
            r"The first-order term in the upper bound is \(\nabla f(x)^T(y - x)\).",
            r"Along the segment, the gradient changes by at most \(L t \lVert y - x\rVert\) in norm.",
            r"Integrating that bound from \(t = 0\) to \(t = 1\) produces the coefficient \(L/2\).",
            r"The descent lemma therefore bounds the remainder by \(L \lVert y - x\rVert^2\), with no factor \(1/2\).",
        ],
        3,
        r"The linear term is the gradient at \(x\). The Lipschitz condition contributes a factor \(t\) inside the integral, and \(\int_0^1 t\, dt = 1/2\). The false step drops that one-half and writes \(L\) in front of the squared distance. The integral of a constant \(L\), with no factor \(t\), is what would have produced a bare \(L\).",
        [
            r"The integral of \(t\) from 0 to 1 is \(1/2\). The coefficient is \(L/2\), not \(L\).",
            r"The linear term is not the gradient inner product.",
            r"The Lipschitz bound on the gradient change does not grow with \(t\).",
        ],
        0,
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        3,
        r"Continue \(f(t) = 2 t^2\) with \(L = 4\). At \(t = 2\), \(f = 8\) and \(f' = 8\). What upper bound does the descent lemma give at \(t = 3\)?",
        18,
        "1",
        r"The step is \(d = 1\). The bound is \(8 + 8 \cdot 1 + (4/2) \cdot 1 = 18\). The true value \(f(3) = 18\) matches it. Reporting \(16\) forgets the quadratic term. Reporting \(8\) is the old value. Reporting \(26\) uses the derivative \(16\) of a different function, \(4 t^2\), in place of \(f' = 8\).",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        3,
        "Compared with the tangent lower bound that convexity gives, the descent lemma",
        [
            r"runs the other way: it is an upper bound, and the extra term is quadratic",
            r"is the same inequality",
            r"requires the Hessian to be indefinite",
            r"does not involve the gradient",
        ],
        0,
        r"Convexity says \(f(y) \ge f(x) + \nabla f(x)^T(y - x)\). The descent lemma says \(f(y)\) is at most that same linear expression plus \((L/2)\lVert y - x\rVert^2\). One is a lower bound and the other is an upper bound. An indefinite Hessian is not the hypothesis. The gradient is the linear term in both.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        r"A gradient step \(y = x - t \nabla f(x)\) plugged into the descent lemma produces a guaranteed decrease when",
        [
            r"\(0 < t < 2/L\)",
            r"\(t > 2/L\)",
            r"\(t\) equals the condition number",
            r"the gradient is zero",
        ],
        0,
        r"Substitute \(y - x = -t \nabla f\). The upper bound becomes \(f(x) - t(1 - L t/2)\lVert\nabla f\rVert^2\). The coefficient \(1 - L t/2\) is positive precisely when \(t < 2/L\). A longer step can make the upper bound increase. The condition number is not this threshold. A zero gradient makes the decrease zero, which is not the interesting case.",
        fig=FALL,
        alt=A_FALL,
        preview=P_SUFF,
    )
    b.num(
        4,
        r"Now let \(f(t) = t^2\) with \(L = 2\). At \(t = 2\), \(f = 4\) and \(f' = 4\). What upper bound does the descent lemma give at \(t = 5\)?",
        25,
        "1",
        r"The step is \(d = 3\). The bound is \(4 + 4 \cdot 3 + (2/2) \cdot 9 = 4 + 12 + 9 = 25\). The true value \(f(5) = 25\) meets it. Reporting \(16\) stops after the linear term. Reporting \(13\) adds the step length to the old value. Reporting \(4\) is the old value.",
        fig=RISE,
        alt=A_RISE,
        preview=P_NEST,
    )
    b.mc(
        4,
        "A conditional-gradient step minimizes a linear model over a set and then uses the descent lemma to",
        [
            r"choose a step length that keeps a guaranteed decrease of the smooth objective",
            r"prove the feasible set is a simplex",
            r"remove the Lipschitz constant from the argument",
            r"replace the objective by a constraint",
        ],
        0,
        r"The linear minimization produces a direction. The descent lemma turns a step along that direction into an upper bound on the new value, and a standard step-length rule makes the bound decrease. The geometry of the feasible set is a separate hypothesis. The Lipschitz constant stays in the estimate. The objective is not replaced.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_FW,
    )
    b.save()


def bank_sufficient():
    b = Bank("sufficient-decrease-lemma")
    b.mc(
        1,
        r"For a gradient step of length \(t\) and a gradient Lipschitz constant \(L\), the sufficient-decrease lemma gives",
        [
            r"\(f(x) - f(x - t \nabla f(x)) \ge t(1 - L t/2)\lVert\nabla f(x)\rVert^2\) when \(0 < t < 2/L\)",
            r"an increase of size \(t \lVert\nabla f(x)\rVert^2\) for every \(t > 0\)",
            r"\(f(x - t \nabla f(x)) = f(x)\) for every \(t\)",
            r"a decrease only when \(t > 2/L\)",
        ],
        0,
        r"Insert \(y = x - t \nabla f\) into the descent lemma. The linear term contributes \(-t \lVert\nabla f\rVert^2\) and the quadratic term contributes \((L/2) t^2 \lVert\nabla f\rVert^2\). The difference is \(t(1 - L t/2)\lVert\nabla f\rVert^2\), which is positive for \(t \in (0, 2/L)\). A longer step can make the coefficient negative. The function value is not frozen.",
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        1,
        r"Let \(L = 4\), \(t = 1/4\), and \(\lVert\nabla f\rVert^2 = 16\). What decrease does the lemma guarantee?",
        2,
        "1",
        r"The coefficient is \(t(1 - L t/2) = (1/4)(1 - 4 \cdot (1/4) / 2) = (1/4)(1 - 1/2) = 1/8\). Then \((1/8) \cdot 16 = 2\). Reporting \(16\) is the squared gradient norm. Reporting \(4\) is \(L\). Reporting \(1/8\) is the coefficient before it multiplies the squared norm.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"Among constant steps, the coefficient \(t(1 - L t/2)\) is largest at",
        [
            r"\(t = 1/L\), where the coefficient equals \(1/(2L)\)",
            r"\(t = 2/L\), where the coefficient equals \(1/L\)",
            r"\(t = L\), where the coefficient equals \(L\)",
            r"\(t = 0\), where the coefficient equals \(1\)",
        ],
        0,
        r"The map \(t \mapsto t - (L/2) t^2\) is a downward parabola. Its vertex is at \(t = 1/L\), and the value there is \(1/(2L)\). At \(t = 2/L\) the coefficient is zero, so the lemma guarantees nothing. The step \(t = L\) is far past \(2/L\) whenever \(L > \sqrt{2}\), and it is not the vertex in any case. At \(t = 0\) the coefficient is zero.",
        fig=LEV,
        alt=A_LEV,
    )
    b.order(
        2,
        "Put these steps in the order that derives the sufficient decrease of a gradient step. Each step uses the result of the step before it.",
        [
            r"Insert \(y = x - t \nabla f(x)\) into the descent lemma.",
            r"Simplify the linear term to \(-t \lVert\nabla f(x)\rVert^2\).",
            r"Simplify the quadratic term to \((L/2) t^2 \lVert\nabla f(x)\rVert^2\).",
            r"Factor the decrease as \(t(1 - L t/2)\lVert\nabla f(x)\rVert^2\).",
            r"Conclude that the decrease is positive when \(0 < t < 2/L\).",
        ],
        r"The descent lemma is the inequality being specialized, so the gradient step has to be substituted first. The linear term and then the quadratic term are what that substitution produces. Factoring collects them, and the sign of the collected coefficient is the last reading. Declaring a range for \(t\) before the coefficient exists has nothing to sign.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"Let \(L = 4\). Which step lengths make the lemma guarantee a strict decrease of a gradient step with nonzero gradient?",
        [
            r"\(t = 1/4\)",
            r"\(t = 1/2\)",
            r"\(t = 1\)",
            r"\(t = 1/10\)",
            r"\(t = 2/5\)",
        ],
        [0, 3, 4],
        r"The coefficient \(t(1 - 4 t/2) = t(1 - 2t)\) is positive for \(0 < t < 1/2\)."
        "\n"
        r"• The steps \(1/4\), \(1/10\), and \(2/5\) lie in that open interval."
        "\n"
        r"• The step \(1/2\) equals \(2/L\), so the guaranteed decrease is zero."
        "\n"
        r"• The step \(1\) is larger than \(1/2\), so the coefficient is negative and the lemma gives no decrease.",
        fig=FALL,
        alt=A_FALL,
    )
    b.sym(
        2,
        r"The step length is \(t\), the Lipschitz constant is \(\mathrm{ell}\), and the squared gradient norm is \(s\). The decrease guaranteed by the lemma equals",
        "t*(1-ell*t/2)*s",
        {"t": (0.05, 0.4), "ell": (1, 3), "s": (0.5, 4)},
        r"The factored decrease is \(t(1 - \mathrm{ell}\, t/2)\) times the squared gradient norm. All three names appear. Dropping the term \(\mathrm{ell}\, t/2\) leaves the pure linear prediction \(t s\), which the quadratic remainder can spoil. Using \(t(1 + \mathrm{ell}\, t/2) s\) adds the remainder instead of subtracting it. Dividing by \(s\) reports a coefficient rather than a decrease.",
        alternates=["(t-ell*t*t/2)*s", "s*t*(1-ell*t/2)"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        "A note derives the decrease of a gradient step from the descent lemma. Exactly one step is a false claim.",
        [
            r"The descent lemma supplies an upper bound on \(f(x - t \nabla f)\).",
            r"The linear term contributes \(-t \lVert\nabla f\rVert^2\).",
            r"The quadratic term contributes \((L/2) t^2 \lVert\nabla f\rVert^2\).",
            r"The guaranteed decrease is therefore \(t(1 + L t/2)\lVert\nabla f\rVert^2\).",
        ],
        3,
        r"The substitution into an upper bound is the right starting point, the linear contribution is \(-t \lVert\nabla f\rVert^2\), and the quadratic contribution is \((L/2) t^2 \lVert\nabla f\rVert^2\). Subtracting the new upper bound from \(f(x)\) produces \(t \lVert\nabla f\rVert^2 - (L/2) t^2 \lVert\nabla f\rVert^2\), which factors as \(t(1 - L t/2)\lVert\nabla f\rVert^2\). The false step adds the quadratic term instead of subtracting it.",
        [
            r"The quadratic term is subtracted. The factor is \(1 - L t/2\), not \(1 + L t/2\).",
            r"The linear term contributes \(+t \lVert\nabla f\rVert^2\).",
            r"The descent lemma is a lower bound on the new value.",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"Let \(L = 5\), \(t = 1/5\), and \(\lVert\nabla f\rVert^2 = 10\). What decrease does the lemma guarantee?",
        1,
        "1",
        r"The coefficient is \((1/5)(1 - 5 \cdot (1/5) / 2) = (1/5)(1/2) = 1/10\). Then \((1/10) \cdot 10 = 1\). This is the step \(t = 1/L\), whose coefficient is \(1/(2L) = 1/10\). Reporting \(10\) is the squared norm. Reporting \(5\) is \(L\). Reporting \(1/10\) is the coefficient alone.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        3,
        r"For the direction \(d = -\nabla f\), the descent-lemma decrease implies the Armijo test with parameter \(c \in (0, 1)\) whenever",
        [
            r"\(t \le 2(1 - c)/L\)",
            r"\(t \ge 2/L\)",
            r"\(c > 1\)",
            r"the gradient norm equals \(c\)",
        ],
        0,
        r"Armijo along \(d = -\nabla f\) asks for a decrease of at least \(c t \lVert\nabla f\rVert^2\). The lemma supplies \(t(1 - L t/2)\lVert\nabla f\rVert^2\). The lemma's coefficient is at least \(c t\) when \(1 - L t/2 \ge c\), which rearranges to \(t \le 2(1 - c)/L\). A step past \(2/L\) is outside the lemma's decrease regime. The parameter \(c\) stays below 1. The gradient norm is not \(c\).",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        "Summing this decrease along a sequence of gradient steps is the start of",
        [
            r"a convergence argument: the sum of the squared gradient norms stays bounded",
            r"a proof that the step length must grow",
            r"the simplex ratio test",
            r"a proof that the Hessian is indefinite",
        ],
        0,
        r"Each step removes at least a fixed multiple of \(\lVert\nabla f\rVert^2\) from the function value. If \(f\) is bounded below, the sum of those decreases is finite, so the sum of the squared gradient norms is finite. That is the opening of the convergence argument. It does not force the step length to grow. The ratio test and an indefinite Hessian are different subjects.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_GCONV,
    )
    b.num(
        4,
        r"Let \(L = 5\). What is \(2/L\), the step length at which the lemma's guaranteed decrease drops to zero?",
        0.4,
        "1",
        r"Divide \(2\) by \(5\). The threshold is \(0.4\). For every \(t \in (0, 0.4)\) the coefficient \(t(1 - L t/2)\) is positive, and at \(t = 0.4\) it is zero. Reporting \(5\) is \(L\). Reporting \(0.2\) is \(1/L\), the step that maximizes the coefficient rather than the step that kills it. Reporting \(2.5\) is \(L/2\).",
        fig=FALL,
        alt=A_FALL,
        preview=P_GPROJ,
    )
    b.mc(
        4,
        "A projected gradient step keeps this decrease when the projection is",
        [
            r"nonexpansive, so the same Lipschitz argument still controls the accepted step",
            r"allowed to increase distances without any change to the proof",
            r"replaced by an unconstrained Newton step",
            r"computed from a simplex basis of a linear program",
        ],
        0,
        r"The sufficient-decrease algebra uses the length of the step that was actually taken. A Euclidean projection does not increase distances, so a projected step is no longer than the unprojected gradient step it came from, and the same \(L\) still closes the estimate. A map that stretches distances would need a new argument. Newton and the simplex method are different iterations.",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_GPROJ,
    )
    b.save()


def bank_grad_conv():
    b = Bank("gradient-method-convergence")
    b.mc(
        1,
        r"With a constant step \(t \in (0, 2/L)\) and \(f\) bounded below, the gradient method satisfies",
        [
            r"\(\lVert\nabla f(x_k)\rVert \to 0\)",
            r"\(\lVert\nabla f(x_k)\rVert\) stays equal to its starting value",
            r"the iterates reach a minimizer in a fixed number of steps for every smooth \(f\)",
            r"the function values increase at every step",
        ],
        0,
        r"Each step removes a positive multiple of the squared gradient norm, and the sum of those removals cannot exceed the gap down to a lower bound. The sum of the squared norms is therefore finite, which forces the norms themselves to zero. They do not stay constant. Finite termination is a special property of some quadratics, not of every smooth function. The function values decrease.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.num(
        1,
        r"Use the constant step \(t = 1/L\) with \(L = 2\). The gap from \(f(x_0)\) down to a lower bound is \(3\). Over the first \(6\) steps, what is the lemma's upper bound on the smallest squared gradient norm?",
        2,
        "1",
        r"At \(t = 1/L\) each step decreases \(f\) by at least \(\lVert\nabla f\rVert^2/(2L)\). Summing and using the gap produces \(\min_{i < 6} \lVert\nabla f(x_i)\rVert^2 \le 2 L \cdot 3 / 6 = 12/6 = 2\). Reporting \(3\) is the gap. Reporting \(6\) is the step count. Reporting \(12\) stops before dividing by the number of steps.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        1,
        r"The bound \(\min_{i < k} \lVert\nabla f(x_i)\rVert^2 \le C/k\) is called sublinear because",
        [
            r"a \(1/k\) envelope goes to zero more slowly than a fixed factor strictly below \(1\)",
            r"the gradient norm is squared at every iteration",
            r"the iterates diverge",
            r"the bound is a quadratic rate",
        ],
        0,
        r"Linear convergence would multiply the error by the same \(\mu \in (0, 1)\) every step. A \(1/k\) upper envelope has successive ratios tending to 1, which is the sublinear pattern. Squaring the error every step would be quadratic. The bound goes to zero, so it is not a divergence statement.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.order(
        2,
        "Put the convergence argument in order. Each step uses the result of the step before it.",
        [
            r"Apply the sufficient-decrease inequality at every iterate, with a step in \((0, 2/L)\).",
            "Sum the inequalities so the function values telescope.",
            r"Bound that sum by the gap from the first value down to a lower bound on \(f\).",
            "Conclude that the sum of the squared gradient norms is finite.",
            r"Deduce that the gradient norms tend to zero, and that the smallest squared norm so far is \(O(1/k)\).",
        ],
        r"Sufficient decrease is the inequality being summed. Telescoping turns the sum of decreases into a difference of function values, and a lower bound on \(f\) caps that difference. A finite sum of nonnegative terms forces the general term to zero, and the average of the first \(k\) terms is what produces the \(1/k\) bound. Claiming the rate before the sum is bounded has no constant to divide by.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.multi(
        2,
        r"The objective is smooth with Lipschitz constant \(L\), bounded below, and the step is a constant \(t \in (0, 2/L)\). Which conclusions follow from summing the decreases?",
        [
            r"The gradient norms tend to zero.",
            r"The function values are monotonically nonincreasing.",
            r"The iterates reach a minimizer after finitely many steps, for every such objective.",
            r"The smallest squared gradient norm over the first \(k\) steps is \(O(1/k)\).",
            r"The excess over the optimal value converges quadratically.",
        ],
        [0, 1, 3],
        r"The summed decrease controls gradients and the direction of the function values."
        "\n"
        r"• A finite sum of squared norms forces the norms to zero."
        "\n"
        r"• Each coefficient \(t(1 - L t/2)\) is positive, so the function does not increase."
        "\n"
        r"• The smallest squared norm is at most a constant over \(k\)."
        "\n"
        r"• Finite termination is not implied. A smooth function can descend forever."
        "\n"
        r"• Quadratic convergence of the excess is a stronger local property and is not this estimate.",
        fig=FALL,
        alt=A_FALL,
    )
    b.sym(
        2,
        r"The step is \(t = 1/\mathrm{ell}\), the gap from the start down to a lower bound is \(\mathrm{gap}\), and \(m\) steps have been taken. The bound on the smallest squared gradient norm equals",
        "2*ell*gap/m",
        {"ell": (1, 5), "gap": (0.4, 4), "m": (2, 20)},
        r"Each step contributes a decrease of at least \(s/(2\,\mathrm{ell})\) when the squared gradient norm is \(s\). Summing \(m\) steps and charging them all to the gap produces \(m \cdot s_{\min} / (2\,\mathrm{ell}) \le \mathrm{gap}\), so \(s_{\min} \le 2\,\mathrm{ell}\,\mathrm{gap}/m\). All three names appear. Dropping the \(2\) understates the bound. Multiplying by \(m\) instead of dividing sends the bound the wrong way in the step count. Using \(\mathrm{ell}^2\) is a different scaling.",
        alternates=["(2*ell*gap)/m", "2*gap*ell/m"],
        fig=SLOW,
        alt=A_SLOW,
    )
    b.find_error(
        3,
        "A note reads the summed decrease. Exactly one step is a false claim.",
        [
            r"Each step with \(t \in (0, 2/L)\) removes at least a fixed positive multiple of \(\lVert\nabla f\rVert^2\).",
            r"Summing those decreases bounds the sum of the squared gradient norms.",
            r"The smallest squared gradient norm in the first \(k\) steps is \(O(1/k)\).",
            r"That \(1/k\) bound is a linear rate.",
        ],
        3,
        r"The decrease, the finite sum, and the \(1/k\) bound on the best squared norm are the theorem. A linear rate would be a factor \(\mu \in (0, 1)\) at every step. The ratio of \(1/(k+1)\) to \(1/k\) tends to 1, so the envelope is sublinear. On a strongly convex quadratic a different argument can give a linear rate. This summation does not.",
        [
            r"A \(1/k\) envelope is sublinear. Linear convergence would shrink by a fixed factor below 1.",
            r"The sum of the decreases does not control the squared gradient norms.",
            r"The coefficient of \(\lVert\nabla f\rVert^2\) is negative throughout \((0, 2/L)\).",
        ],
        0,
        fig=DECAY,
        alt=A_DECAY,
    )
    b.num(
        3,
        r"Use \(t = 1/L\) with \(L = 4\). The gap down to a lower bound is \(2\). Over the first \(4\) steps, what is the upper bound on the smallest squared gradient norm?",
        4,
        "1",
        r"The bound is \(2 L \cdot \mathrm{gap} / k = 2 \cdot 4 \cdot 2 / 4 = 4\). Reporting \(2\) is the gap. Reporting \(8\) is \(2L\), which leaves the gap out. Reporting \(16\) is the numerator \(2 \cdot 4 \cdot 2\) before dividing by the step count.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        3,
        r"If the constant step satisfies \(t \ge 2/L\), this argument",
        [
            r"no longer guarantees decrease, and the iteration can diverge",
            r"gives a faster \(1/k^2\) rate for every smooth function",
            r"forces the gradient to vanish in one step",
            r"makes the Lipschitz constant equal to zero",
        ],
        0,
        r"At \(t = 2/L\) the coefficient \(t(1 - L t/2)\) is zero, and beyond it the coefficient is negative, so the upper bound from the descent lemma can increase. The scalar \(f(u) = u^2/2\) has \(L = 1\), and the step \(t = 3\) sends \(u\) to \(-2u\), which grows. A \(1/k^2\) rate needs a different algorithm. One-step vanishing and a zero Lipschitz constant are not consequences of a long step.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        4,
        "Adding a momentum term, as in the heavy-ball method, is a way to",
        [
            r"improve on the \(1/k\) gradient bound for the quadratics whose condition number made steepest descent slow",
            r"remove the need for a gradient",
            r"make every step length equal to \(2/L\)",
            r"replace the objective by a linear function",
        ],
        0,
        r"The heavy-ball update mixes the new gradient step with the previous displacement. On a quadratic, the mix can be tuned from the condition number and beats the steepest-descent factor. The gradient is still required. The safe steepest step \(1/L\) is not replaced by the boundary step \(2/L\). The objective stays the one being minimized.",
        fig=ELL,
        alt=A_ELL,
        preview=P_HB,
    )
    b.num(
        4,
        r"Use \(t = 1/L\) with \(L = 3\). The gap down to a lower bound is \(2\). Over the first \(4\) steps, what is the upper bound on the smallest squared gradient norm?",
        3,
        "1",
        r"The bound is \(2 \cdot 3 \cdot 2 / 4 = 3\). Reporting \(2\) is the gap. Reporting \(4\) is the step count. Reporting \(12\) is the numerator \(2 \cdot 3 \cdot 2\) before dividing by \(4\).",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_NEST,
    )
    b.mc(
        4,
        r"Nesterov's acceleration changes the \(1/k\) picture, on convex objectives, to",
        [
            r"an \(O(1/k^2)\) guarantee on the function gap",
            r"finite termination for every smooth function",
            r"a requirement that the Lipschitz constant be unknown",
            r"a divergent iteration whenever the gradient is Lipschitz",
        ],
        0,
        r"The accelerated scheme evaluates the gradient at an extrapolated point and chooses weights so that the function gap is \(O(1/k^2)\) for convex \(L\)-smooth objectives. That is faster than the \(O(1/k)\) gradient bound of plain gradient descent, and it is not finite termination. The scheme uses \(L\). It is built to converge under the same Lipschitz hypothesis.",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_NEST,
    )
    b.save()


def _sec(idea, eqs, work, pits, leads, fig, alt):
    return [
        {"heading": "The idea", "figure": fig, "figure_alt": alt, "body_md": idea},
        {"heading": "Key equations", "body_md": eqs},
        {"heading": "Worked example", "body_md": work},
        {"heading": "Common pitfalls", "body_md": pits},
        {"heading": "Where this leads", "body_md": leads},
    ]


def expl_descent():
    save_explainer(
        "descent-directions",
        "Descent directions",
        _sec(
            r"""A vector \(d\) is a descent direction at \(x\) when the directional derivative is strictly negative. For a differentiable objective that derivative is the dot product of the gradient with \(d\). A negative value means the first-order model of \(f\) decreases as you leave \(x\) along \(d\). The model is enough to control a short step, even though a long step may later turn uphill.

Write the expansion \(f(x + t d) = f(x) + t\, \nabla f(x)^T d + o(t)\) as \(t\) tends to zero. Divide the change in \(f\) by the positive step. The remainder becomes negligible beside a fixed negative number, so the difference quotient stays negative for every sufficiently small \(t\). Multiplying back by that positive step shows that \(f\) itself drops.

The same dot product covers scaled directions. If \(D\) is symmetric positive definite and the gradient is not zero, the vector \(d = -D \nabla f(x)\) has directional derivative \(-\nabla f(x)^T D \nabla f(x)\). The quadratic form is positive, so the derivative is negative. Steepest descent is the case where \(D\) is the identity. A diagonal matrix with positive entries rescales the coordinates. A Newton direction uses the inverse Hessian when that inverse is positive definite. In every one of those cases the test is the same sign.""",
            r"""The test and the scaled construction are
\[
\nabla f(x)^T d < 0, \qquad d = -D \nabla f(x)
\]
with \(D\) symmetric positive definite. The directional derivative of that scaled direction is \(-\nabla f(x)^T D \nabla f(x)\).""",
            r"""Take the gradient \((5, -1)\) and the direction \((-3, 1)\). The dot product is \(5 \cdot (-3) + (-1) \cdot 1 = -15 - 1\).

The dock slope is -16. The sign is negative, so the direction is a descent direction, and a short enough step decreases \(f\). The negative gradient would have been \((-5, 1)\), a different vector. Its directional derivative is \(-(25 + 1) = -26\), also negative, and typically steeper. The number \(-16\) is only the test for the direction that was proposed.""",
            r"""Reading a zero dot product as a descent direction is the usual slip. The definition asks for a strict inequality, and a zero derivative means the first-order model is flat. A second slip is to drop the minus sign in \(d = -D \nabla f\) and then still call the result a descent direction. Without the minus, the quadratic form \(\nabla f^T D \nabla f\) is positive and the step climbs. A third is to demand the decrease for every positive step length. The first-order argument only controls a sufficiently short step. A fourth is to treat positive definiteness as optional. If \(D\) has a negative eigenvalue, \(-D \nabla f\) can point uphill for some gradients.""",
            r"""A descent iteration still has to choose the step length and a stopping test. The update is the current point plus a positive multiple of \(d\). On a quadratic the multiple that minimizes the objective along the line has a closed form. A sufficient-decrease test accepts a trial length without finding that exact minimizer. Both of those rules start from a direction that has already passed the sign test.""",
            PAIR,
            A_PAIR,
        ),
    )


def expl_framework():
    save_explainer(
        "descent-method-framework",
        "General descent methods",
        _sec(
            r"""A descent method is an iteration with three separate decisions. At the current point, compute the gradient. From that gradient, build a direction whose directional derivative is negative. Then choose a positive step length, and replace the point by the point plus the step length times the direction. After the update, apply a stopping test. A small gradient norm is the usual test, because a vanishing gradient means the first-order model has nowhere useful to go.

The direction is where the methods differ. Steepest descent takes the negative gradient. A scaled method takes \(-D \nabla f\) with a positive definite \(D\), which stretches the coordinates before the step. Newton's method takes \(-H^{-1} \nabla f\) when the Hessian is positive definite, so the direction solves the quadratic model exactly. Gauss-Newton is the least-squares relative of that idea: it linearizes the residual and solves a linear least-squares subproblem, which inverts a Gram matrix of the residual Jacobian rather than the full Hessian of the objective.

The step length is an independent choice. It may be a fixed number, the exact minimizer of the objective along the line, or the result of a backtracking loop. Stopping is independent again. None of these choices changes the shape of the update. They only fill in the direction, the length, and the decision to halt.""",
            r"""The update, a steepest direction, and a Newton direction are
\[
x^+ = x + t d, \qquad d = -\nabla f(x), \qquad d = -H_f(x)^{-1} \nabla f(x).
\]
The step length satisfies \(t > 0\), and \(d\) is a descent direction.""",
            r"""Start at \((8, 1)\) with direction \((-1, 2)\) and step length \(1\). The new point is \((8, 1) + (-1, 2) = (7, 3)\).

The crate coordinate is 7. The squared length of the displacement is \(1 + 4 = 5\), which is \(t^2\) times the squared length of the direction. Whether this direction was steepest, scaled, or Newton is a separate question. The update rule does not ask. It only adds the accepted step. A stopping test would then look at the gradient at \((7, 3)\), not at the old point.""",
            r"""Adding the gradient instead of its negative is the sign error that turns the iteration into ascent. The framework asks for a descent direction, and the gradient itself has a positive directional derivative whenever it is nonzero. A second miss is to treat the step length as part of the direction. Scaling \(d\) by two and then using \(t = 1\) is the same ray as the original \(d\) with \(t = 2\), so the two decisions have to be stated together. A third is to stop because a direction was found. Finding a direction is the start of the iteration, not evidence that the gradient is small. A fourth is to invert the Hessian when it is indefinite and still call the result a descent direction. Negative curvature can make \(-\nabla f^T H^{-1} \nabla f\) positive.""",
            r"""On a positive definite quadratic the step along a fixed direction has a closed form. A sufficient-decrease test accepts a trial that falls enough without finding that exact minimizer. Gauss-Newton sits in the same loop as one more way to build \(d\), from a linearized residual.""",
            ARR,
            A_ARR,
        ),
    )


def expl_rates():
    save_explainer(
        "convergence-rates",
        "Rates of convergence",
        _sec(
            r"""A rate describes how fast a sequence of nonnegative errors tends to zero. The first measurement is the successive ratio, the next error divided by the current one. If those ratios tend to a limit strictly between zero and one, the convergence is linear: each error is eventually a fixed fraction of the one before it. On a plot of the logarithm of the error against the iteration count, that pattern is a straight line with negative slope.

If the successive ratios tend to zero, the convergence is superlinear. It is faster than every linear rate. The finer test divides the next error by the square of the current error. When that second family of ratios stays bounded, the convergence is quadratic. Quadratic convergence implies superlinear convergence, because a bounded ratio against the square forces the ordinary ratio to vanish with the error.

If the errors tend to zero but the successive ratios tend to one, the convergence is sublinear. The sequence \(1/k\) is the standard example. Its errors decrease at every step, and the ratio \(k/(k+1)\) still climbs to one. Decreasing is not, by itself, a linear rate. A ratio bigger than one would be growth, not convergence.""",
            r"""For an error sequence \(e_k \to 0\), the names line up with the limits
\[
\frac{e_{k+1}}{e_k} \to \mu \in (0, 1), \qquad \frac{e_{k+1}}{e_k} \to 0, \qquad \frac{e_{k+1}}{e_k^2} \text{ bounded}.
\]
Those are linear, superlinear, and quadratic. A ratio limit of \(1\) is sublinear.""",
            r"""Suppose two successive errors are \(0.64\) and \(0.08\), and the same ratio continues. Divide the later error by the earlier one.

The beacon ratio is 0.125. A constant ratio strictly between zero and one is a linear rate. The next error would be \(0.08 \cdot 0.125 = 0.01\). The ratio against the square is \(0.08 / 0.64^2 = 0.08 / 0.4096\), which grows as the errors shrink if the ordinary ratio stays constant, so this sequence is not quadratic. A quadratic sequence such as repeated squaring drives the ordinary ratio to zero.""",
            r"""Calling every decreasing sequence linear is the common overstatement. Linear convergence needs the ratio to settle strictly below one. A second slip is to call a constant ratio quadratic. The quadratic test puts the previous error squared in the denominator, and a pure geometric sequence fails that test. A third is to forget that quadratic convergence is also superlinear. Once the squared ratio is bounded and the error tends to zero, the ordinary ratio tends to zero. A fourth is to read a horizontal line on the log plot as a fast rate. A horizontal line is a constant error.""",
            r"""Steepest descent on a quadratic has a linear guarantee whose factor is built from the condition number of the Hessian. The general gradient method, with only a Lipschitz gradient and a lower bound on the objective, has a sublinear guarantee: the best squared gradient norm seen in the first \(k\) steps is on the order of \(1/k\). Newton's method, near a minimizer with a positive definite Hessian, is the algorithm whose local rate is quadratic.""",
            DECAY,
            A_DECAY,
        ),
    )


def expl_exact():
    save_explainer(
        "exact-line-search-quadratic",
        "Exact line search on quadratics",
        _sec(
            r"""Restrict a quadratic to a line and the objective becomes a parabola in one variable. Write \(f(x) = \tfrac12 x^T A x + b^T x\) with \(A\) symmetric, and set \(\varphi(t) = f(x + t d)\). Differentiating under the quadratic gives \(\varphi'(t) = \nabla f(x)^T d + t\, d^T A d\). The gradient that appears here is \(A x + b\), and the curvature along \(d\) is the same matrix \(A\) that is the Hessian.

If \(A\) is positive definite and \(d\) is not zero, the curvature \(d^T A d\) is positive, so the parabola opens upward and the critical point is a minimum. Set the derivative to zero and solve for the step. The result is the negative directional derivative divided by the curvature. For a descent direction the directional derivative is negative, so the step that comes out is positive. The formula does not ask the direction to be steepest. Any fixed \(d\) has its own exact step.

When the direction is the negative gradient, the numerator becomes the squared gradient norm and the denominator becomes \(\nabla f^T A \nabla f\). After the step is taken, the derivative of the restriction is zero. That is the same statement as the new gradient being orthogonal to \(d\).""",
            r"""The exact step and its steepest special case are
\[
t = -\frac{\nabla f(x)^T d}{d^T A d}, \qquad t = \frac{\lVert\nabla f(x)\rVert^2}{\nabla f(x)^T A \nabla f(x)}.
\]
The second formula is the first one with \(d = -\nabla f(x)\).""",
            r"""Take \(A\) equal to the identity, the gradient \((3, 0)\), and the direction \((-1, 0)\). The directional derivative is \(-3\). The curvature is \(1\). The exact step is \(3\).

The winch step is 3. The new point moves three units along \((-1, 0)\). The line derivative \(-3 + t\) is zero at that step, and it is negative for every shorter positive step. A step of \(4\) would already have passed the bottom of the parabola. The same arithmetic with a steeper curvature would have produced a shorter step.""",
            r"""Forgetting the minus sign in front of the directional derivative sends the step backward along a descent direction. The directional derivative is already negative, and the leading minus turns it positive. A second slip is to divide by \(d^T d\) when the Hessian is not the identity. The curvature is \(d^T A d\). A third is to report a negative step after the algebra has produced a positive root. A fourth is to expect the new gradient to vanish in every coordinate. Exact line search only makes the new gradient orthogonal to \(d\). The rest of the gradient can still be large, which is why the iteration continues.""",
            r"""Orthogonality of the new gradient to the step is the geometric reason steepest descent zigzags on a long ellipse: the next negative gradient is perpendicular to the one just used. The size of that zigzag is governed by the condition number of \(A\). Conjugate directions keep an exact line search and replace Euclidean orthogonality by \(d_i^T A d_j = 0\), which is what produces finite termination on a quadratic.""",
            ELL,
            A_ELL,
        ),
    )


def expl_armijo():
    save_explainer(
        "armijo-backtracking",
        "Armijo backtracking line search",
        _sec(
            r"""An exact line search minimizes the objective along a ray. Many iterations only need a step that decreases the objective enough. The Armijo test makes that idea numeric. Fix a parameter \(c\) strictly between zero and one, and accept a trial length \(t > 0\) when the new value sits at or below the current value plus \(c\) times \(t\) times the directional derivative.

Because the directional derivative of a descent direction is negative, the right-hand side is smaller than the current value. It is also larger than the pure tangent prediction, since \(c < 1\) and the slope is negative: the comparison line falls more slowly than the tangent. The first-order expansion says the function tracks the tangent for a short step, so it starts out below the shallower comparison line. A sufficiently small trial is therefore accepted. No Hessian is required for that argument.

Backtracking uses the fact. Start at a trial length \(t_0\). If the inequality fails, replace the trial by \(\beta t\) with a fixed factor \(\beta\) strictly between zero and one, and test again. The trials shrink geometrically, and the first-order argument says the loop cannot reject every one of them.""",
            r"""The accepted step satisfies
\[
f(x + t d) \le f(x) + c\, t\, \nabla f(x)^T d, \qquad 0 < c < 1.
\]
A rejected trial is replaced by \(\beta t\) with \(0 < \beta < 1\).""",
            r"""Let \(f(u) = u^2\) at \(u = 5\), so the value is \(25\) and the derivative is \(10\). Take \(d = -1\), the parameter \(c = 0.1\), and the trial \(t = 6\). The directional derivative is \(-10\). The right-hand side is \(25 + 0.1 \cdot 6 \cdot (-10) = 25 - 6 = 19\). The trial point is \(u = -1\), where the function equals \(1\), and \(1\) is below \(19\).

The latch value is 19. The test accepts this trial. A much longer trial could fail the same test even though the direction descends, because the parabola turns upward. Backtracking would then halve, or otherwise shrink, the trial and test again.""",
            r"""Reversing the inequality accepts steps that have not fallen far enough and rejects steps that have fallen further. The test is an upper bound on the new value. A second slip is to set \(c\) bigger than one. The comparison line would then drop faster than the tangent, and a smooth function with a nonzero second derivative will fail the test for every small step. A third is to multiply a rejected trial by a factor bigger than one. That lengthens the step and walks away from the short-step regime that the proof uses. A fourth is to treat a passing trial as the exact minimizer along the line. Armijo only claims sufficient decrease.""",
            r"""When the direction is the negative gradient and the gradient is Lipschitz with constant \(L\), every step shorter than \(2(1 - c)/L\) is guaranteed to pass Armijo. That link is the sufficient-decrease lemma. The same backtracking loop damps a Newton direction: the direction stays the Newton step, and the length shrinks until the inequality holds. Adding a curvature condition on top of Armijo produces the Wolfe pair of tests, which quasi-Newton updates use to keep a positive definite approximation.""",
            FALL,
            A_FALL,
        ),
    )


def expl_zigzag():
    save_explainer(
        "gradient-zigzag",
        "Zig-zagging of steepest descent",
        _sec(
            r"""Steepest descent steps along the negative gradient, and an exact line search walks that ray until the derivative of the restriction is zero. The derivative of the restriction is the new gradient dotted with the step. The step was the old negative gradient, so the new gradient is orthogonal to the old gradient. The next steepest direction, the negative of the new gradient, is therefore orthogonal to the direction just used. Successive exact steepest steps meet at a right angle.

On a round level set the story ends immediately. If the Hessian is a positive multiple of the identity, one exact steepest step lands on the minimizer and the next gradient is zero. There is no second direction to turn into. On a long ellipse the right angle is expensive. The negative gradient is perpendicular to the contour. A very flat ellipse is crossed by that perpendicular almost at once, and the new perpendicular points nearly back along the long axis. The path zigzags, and each step buys only a little progress toward the center.

Euclidean orthogonality is not conjugacy. Conjugacy of two directions is a zero of \(d_i^T A d_j\). The zigzag identity is a zero of \(d_i^T d_j\). Those agree for every positive definite Hessian only when the Hessian is a multiple of the identity, which is the case with no zigzag. In general, right angles do not give finite termination.""",
            r"""Exact line search gives \(\nabla f(x^+)^T d = 0\). For \(d = -\nabla f(x)\),
\[
\nabla f(x^+)^T \nabla f(x) = 0.
\]
The exact steepest step on \(A\) is \(\lVert\nabla f\rVert^2 / (\nabla f^T A \nabla f)\).""",
            r"""Take \(A = \mathrm{diag}(1, 3)\) and start at \((6, 2)\). The gradient is \((6, 6)\). Its squared norm is \(72\), and \(A\) times the gradient is \((6, 18)\), whose dot product with the gradient is \(36 + 108 = 144\). The exact step is \(72/144 = 1/2\). The next point is \((6, 2) - (1/2)(6, 6) = (3, -1)\).

The spar coordinate is 3. The new gradient is \((3, -3)\), and its dot product with \((6, 6)\) is zero. The path has made a right angle. The eigenvalues \(1\) and \(3\) are different, so the new gradient is not zero and a second step still has somewhere to go.""",
            r"""Expecting finite termination from Euclidean orthogonality mixes this fact up with conjugacy. The right angle holds for every positive definite quadratic, and termination in \(n\) steps does not. A second slip is to say the method zigzags most on a circle. Equal eigenvalues finish in one step. A third is to drop the exact line search and still claim the right angle. A fourth is to treat a zero dot product of the two gradients as a zero gradient. Both vectors can be long and still be perpendicular.""",
            r"""The amount of progress per zigzag is controlled by the condition number, the ratio of the extreme eigenvalues. The excess contracts by at most the square of \((\kappa - 1)/(\kappa + 1)\). Conjugate directions keep the exact line search and change the orthogonality to \(d_i^T A d_j = 0\). That single change is what makes a quadratic finish in at most \(n\) steps, which is the opening of the conjugate-gradient method.""",
            ZIG,
            A_ZIG,
        ),
    )


def expl_condition():
    save_explainer(
        "condition-number-gradient-rate",
        "Condition number and gradient-descent rate",
        _sec(
            r"""On a positive definite quadratic, steepest descent with exact line search has a linear rate that depends only on the shape of the Hessian. Let \(\kappa\) be the ratio of the largest eigenvalue to the smallest. The excess of the objective over its minimum is multiplied, at every step, by a factor no larger than \(((\kappa - 1)/(\kappa + 1))^2\).

The square is there because the excess equals half the squared \(A\)-norm of the error. The \(A\)-norm of the error contracts by the unsquared quotient \((\kappa - 1)/(\kappa + 1)\). Squaring that quotient produces the factor on the excess. When \(\kappa = 1\), the factor is zero: the level sets are spheres and one exact steepest step finishes the problem. As \(\kappa\) grows, the quotient grows toward one and the guarantee becomes slower. A badly stretched ellipse is exactly a large condition number.

The bound is a worst-case statement over starting points. A lucky start on the long axis can do better. The factor cannot be improved in general, because there are starts that meet it. It is also a statement about this algorithm. A method that builds conjugate directions replaces \(\kappa\) by a milder function of \(\kappa\) and keeps a linear rate with a smaller factor.""",
            r"""With \(\kappa = \lambda_{\max}(A)/\lambda_{\min}(A)\),
\[
f(x^+) - f^\star \le \left(\frac{\kappa - 1}{\kappa + 1}\right)^2 \bigl(f(x) - f^\star\bigr).
\]
The unsquared quotient bounds the error in the \(A\)-norm.""",
            r"""Take \(\kappa = 3/2\). The unsquared quotient is \((1/2) / (5/2) = 1/5\). The factor on the excess is the square of that quotient.

The hoist factor is 0.04. An excess of \(50\) would be guaranteed to fall to at most \(2\) at the next exact steepest step. The same eigenvalues in the opposite order give the same ratio, because \(\kappa\) uses the larger over the smaller. Forgetting the square would have left the factor \(0.2\), which is the contraction of the \(A\)-norm error rather than of the excess.""",
            r"""Dropping the square is the arithmetic error that confuses the two norms. The excess carries the square. The \(A\)-norm error carries the unsquared quotient. A second slip is to use the sum of the eigenvalues in place of their ratio. Two Hessians with the same trace can have very different condition numbers. A third is to treat a factor close to one as a fast rate. Closer to one is slower. A fourth is to apply the factor to a step that is not exact steepest descent. The bound is proved for that pair of choices. A fixed short step has a different estimate.""",
            r"""Conjugate gradients keep a linear rate and improve the factor to a function of \(\sqrt{\kappa}\) rather than of \(\kappa\). Heavy-ball momentum uses the same condition number to choose the weight on the previous step, and on a quadratic that weight beats the steepest-descent factor. Both methods are later because they start from the rate this bound makes visible.""",
            ELL,
            A_ELL,
        ),
    )


def expl_lipschitz():
    save_explainer(
        "lipschitz-gradient",
        "Lipschitz-continuous gradients",
        _sec(
            r"""A gradient is Lipschitz continuous with constant \(L\) when it cannot change faster than \(L\) times the distance between the points. The inequality bounds the norm of the difference of gradients by \(L\) times the norm of the difference of the points. Any larger number is also a valid constant. A smaller number than the best one is not.

For a twice differentiable objective the Hessian is the derivative of the gradient. On a convex domain, if the induced 2-norm of the Hessian is at most \(L\) everywhere, the fundamental theorem along the segment turns that matrix bound into the Lipschitz inequality for the gradient. For a symmetric Hessian the induced 2-norm is the largest absolute eigenvalue. A constant Hessian therefore contributes its spectral radius, and every larger number works as well.

Least squares fits the same pattern. The objective \(\tfrac12 \lVert A x - b\rVert^2\) has Hessian \(A^T A\). The eigenvalues of that Gram matrix are the squares of the singular values of \(A\), so a sharp Lipschitz constant is the square of the largest singular value, which is \(\lVert A\rVert_2^2\). The vector \(b\) moves the residual and does not appear in the Hessian.""",
            r"""The definition and the Hessian test are
\[
\lVert\nabla f(y) - \nabla f(x)\rVert \le L \lVert y - x\rVert, \qquad L \ge \sup_x \lVert H_f(x)\rVert_2.
\]
For \(f(x) = \tfrac12 \lVert A x - b\rVert^2\), a sharp constant is \(\lVert A\rVert_2^2\).""",
            r"""Let \(f(t) = 6 t^2\). The derivative is \(12 t\), and the second derivative is the constant \(12\). The difference of derivatives between two points, divided by the distance, equals \(12\) every time.

The cable constant is 12. A candidate constant of \(9\) would fail, because the derivative changes twelve times as fast as the input. A candidate of \(20\) would succeed, and it would be loose. The same reading on a diagonal Hessian uses the larger diagonal entry, not the smaller one and not their sum.""",
            r"""Using the smallest eigenvalue as the Lipschitz constant is the reversal of the induced norm. The induced 2-norm takes the largest absolute eigenvalue, because that is the greatest stretch. A second slip is to forget the square for least squares and report a singular value. The Hessian is \(A^T A\), so the singular value is squared. A third is to treat a valid constant as unique. Every larger number is valid. The sharp one is the smallest number that works. A fourth is to divide by the distance and then call the quotient a function value. The quotient bounds the gradient, not \(f\).""",
            r"""The descent lemma turns this constant into a quadratic upper bound on \(f\), with coefficient \(L/2\) in front of the squared step. That upper bound is the tool behind every later guarantee for the gradient method. A local quadratic rate for Newton's method asks the same Lipschitz idea of the Hessian itself, so that the Newton correction cannot change too fast near the minimizer.""",
            SEG,
            A_SEG,
        ),
    )


def expl_lemma():
    save_explainer(
        "descent-lemma",
        "The descent lemma",
        _sec(
            r"""The descent lemma is a global upper bound for a function whose gradient is Lipschitz with constant \(L\). It says that \(f(y)\) sits at or below the tangent model at \(x\), plus a quadratic penalty \((L/2)\) times the squared distance from \(x\) to \(y\). Convexity, when it holds, gives a lower bound by the tangent alone. The descent lemma runs the other way and needs no convexity. Its hypothesis is the Lipschitz gradient.

The proof starts from the fundamental theorem along the segment. The difference \(f(y) - f(x)\) is the integral of the directional derivative of \(f\) at the intermediate points. Split that derivative into the gradient at \(x\) plus the change in the gradient. The change is at most \(L\) times the distance already traveled along the segment, which contributes a factor of the integration variable \(t\). Integrating \(t\) from zero to one produces one-half, and that one-half is the coefficient in the lemma.

When the Hessian is the constant \(L\) in one dimension, the inequality is an equality. The quadratic penalty is then exactly the remainder of the Taylor expansion. A larger constant still gives a valid upper bound. A smaller constant does not, and a single pair of points is enough to see the failure.""",
            r"""The bound is
\[
f(y) \le f(x) + \nabla f(x)^T(y - x) + \frac{L}{2}\lVert y - x\rVert^2.
\]
The integral of \(t\) from \(0\) to \(1\) is what produces the factor \(1/2\).""",
            r"""Let \(f(t) = t^2\), so \(L = 2\), and compare the point \(t = 1\) with the point \(t = 4\). The value at the start is \(1\), the derivative is \(2\), and the step is \(3\). The bound is \(1 + 2 \cdot 3 + (2/2) \cdot 9 = 1 + 6 + 9\).

The loft bound is 16. The true value at \(t = 4\) is \(16\), so the bound is sharp for this \(L\). From \(t = 0\) to \(t = 2\) with the constant replaced by \(1\), the bound falls to \(2\) while \(f(2) = 4\), so the inequality fails. The factor one-half is doing real work in the quadratic term.""",
            r"""Writing \(L\) instead of \(L/2\) is the error the integral is designed to prevent. The integrand carries a factor \(t\), and the average of \(t\) on the unit interval is one-half. A second slip is to reverse the inequality and treat the lemma as a convexity statement. Convexity has no \(L\) and points the other way. A third is to drop the linear term. That is legal only at a stationary point. A fourth is to apply the bound with a constant smaller than the induced norm of the Hessian. The lemma inherits whatever gap the Lipschitz constant had.""",
            r"""Substitute a gradient step \(x - t \nabla f(x)\) into the upper bound and the linear and quadratic terms combine into a decrease of size \(t(1 - L t/2)\) times the squared gradient norm. That is the sufficient-decrease lemma, and it is positive for steps shorter than \(2/L\). The same upper bound picks step lengths for an accelerated gradient iteration and for a conditional-gradient step over a compact convex set.""",
            LEV,
            A_LEV,
        ),
    )


def expl_sufficient():
    save_explainer(
        "sufficient-decrease-lemma",
        "Sufficient decrease lemma",
        _sec(
            r"""Take the descent lemma and aim it at a pure gradient step. The new point is the old point minus \(t\) times the gradient. The displacement is \(-t \nabla f\), so the linear term in the upper bound is \(-t\) times the squared gradient norm. The quadratic penalty contributes \((L/2) t^2\) times the same squared norm. Subtracting the upper bound from the old value produces a guaranteed decrease of \(t(1 - L t/2)\) times \(\lVert\nabla f\rVert^2\).

The coefficient is positive exactly when the step lies strictly between zero and \(2/L\). At the right endpoint the guarantee drops to zero. Past that endpoint the algebra no longer promises a decrease, and a long gradient step can diverge. Among the constant steps inside the interval, the coefficient \(t - (L/2) t^2\) is a downward parabola. Its maximum is at \(t = 1/L\), where the decrease is at least the squared gradient norm divided by \(2L\).

The same decrease is an Armijo certificate. Along the negative gradient, Armijo with parameter \(c\) asks for a decrease of at least \(c t\) times the squared norm. The lemma meets that request whenever \(1 - L t/2\) is at least \(c\), which is the step restriction \(t \le 2(1 - c)/L\). Backtracking can therefore stop: a short enough trial is not merely acceptable in the limit, it is covered by an explicit bound.""",
            r"""For \(0 < t < 2/L\),
\[
f(x) - f(x - t \nabla f(x)) \ge t\Bigl(1 - \frac{L t}{2}\Bigr) \lVert\nabla f(x)\rVert^2.
\]
At \(t = 1/L\) the coefficient equals \(1/(2L)\). Armijo with parameter \(c\) holds for \(t \le 2(1 - c)/L\).""",
            r"""Let \(L = 6\), take the step \(t = 1/6\), and let the squared gradient norm be \(36\). This step is \(1/L\). The coefficient is \((1/6)(1 - 6 \cdot (1/6) / 2) = (1/6)(1/2) = 1/12\). Multiply by the squared norm.

The ramp drop is 3. The lemma promises that the objective falls by at least \(3\), whatever the rest of \(f\) looks like, as long as the Lipschitz constant really is \(6\). The boundary step \(2/L = 1/3\) would have promised a drop of zero. A step of \(1/L\) is the constant choice that makes the promise as large as this argument allows.""",
            r"""Adding the quadratic term instead of subtracting it replaces \(1 - L t/2\) by \(1 + L t/2\) and invents a decrease that the upper bound does not give. A second slip is to call \(t = 2/L\) a strict decrease. The coefficient there is zero. A third is to maximize the coefficient at \(t = 2/L\). The vertex of the parabola is at half of that, \(t = 1/L\). A fourth is to match Armijo with \(c = 1\) for a positive step. The rearrangement \(t \le 2(1 - c)/L\) collapses to \(t \le 0\) when \(c = 1\). The lemma does not promise the full linear prediction.""",
            r"""Summing the inequality over many steps bounds the sum of the squared gradient norms by the gap in the objective. That sum is the start of the convergence proof for the gradient method. The same decrease survives projection onto a convex set when the projection does not increase distances, which is why a projected gradient step can quote this lemma with the same \(L\).""",
            FALL,
            A_FALL,
        ),
    )


def expl_grad_conv():
    save_explainer(
        "gradient-method-convergence",
        "Convergence of the gradient method",
        _sec(
            r"""Fix a step length in the open interval from zero to \(2/L\), and assume the objective is bounded from below. Every gradient step then removes at least a fixed positive multiple of the squared gradient norm from the function value. The function values are therefore monotonically nonincreasing. They cannot fall forever by fixed chunks unless those chunks shrink, and the only way for the chunks to shrink is for the gradient norms to shrink.

Sum the decreases. The function values telescope, and the whole sum is at most the gap from the starting value down to a lower bound. The sum of the squared gradient norms is therefore finite. A general term of a convergent series of nonnegative numbers tends to zero, so the gradient norms tend to zero. Spread the same sum across the first \(k\) steps and the smallest squared norm in that window is at most a constant over \(k\).

That \(1/k\) envelope is sublinear. A linear rate would multiply the error by a fixed factor strictly below one. The general smooth case gives neither that factor, nor finite termination, nor a quadratic excess. Those stronger rates need more structure. If the constant step is \(1/L\), the constant in the \(1/k\) bound is \(2L\) times the initial gap.""",
            r"""For the step \(t = 1/L\) and a lower bound \(f^\star\),
\[
\min_{i < k} \lVert\nabla f(x_i)\rVert^2 \le \frac{2L\bigl(f(x_0) - f^\star\bigr)}{k}.
\]
Any fixed \(t \in (0, 2/L)\) gives the same shape with a different constant. The gradient norms tend to zero.""",
            r"""Take \(L = 5\), a gap of \(6\) from the start down to a lower bound, and the step \(t = 1/L\). After \(10\) steps the bound on the smallest squared gradient norm is \(2 \cdot 5 \cdot 6 / 10\).

The trail bound is 6. Some earlier gradient may have been larger. The claim is only that the best one so far has squared norm at most \(6\). Doubling the number of steps would cut this particular upper bound in half. The bound is not a promise that the last gradient, rather than the smallest one, has already reached \(6\).""",
            r"""Calling the \(1/k\) bound a linear rate confuses two definitions. Linear convergence is a constant factor strictly below one. A \(1/k\) envelope has ratios tending to one. A second slip is to quote the bound for a step longer than \(2/L\). At that length the decrease coefficient is no longer positive, and the scalar \(u^2/2\) with step \(3\) already diverges. A third is to read the bound as finite termination. A sum of many tiny decreases can stay finite while the iteration continues forever. A fourth is to claim quadratic convergence of the function gap from this summation alone. The summation does not square the error.""",
            r"""Momentum methods exist because this rate is slow when the Hessian is badly conditioned. The heavy-ball iteration adds a multiple of the previous step, and on a quadratic the multiple can be chosen from the condition number so that the linear factor beats steepest descent. Nesterov's scheme evaluates the gradient at an extrapolated point and, for convex objectives with a Lipschitz gradient, improves the function-gap guarantee from \(1/k\) to \(1/k^2\).""",
            SLOW,
            A_SLOW,
        ),
    )


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def _balance_mc():
    """Spread multiple-choice keys across the four positions."""
    counts = [0, 0, 0, 0]
    original = Bank.mc

    def mc(self, rnd, prompt, options, correct, explanation, **kwargs):
        best_idx, best_rot = None, 0
        for rot in range(4):
            idx = (correct - rot) % 4
            if best_idx is None or counts[idx] < counts[best_idx]:
                best_idx, best_rot = idx, rot
        counts[best_idx] += 1
        if best_rot:
            options = options[best_rot:] + options[:best_rot]
            correct = (correct - best_rot) % 4
        return original(self, rnd, prompt, options, correct, explanation, **kwargs)

    Bank.mc = mc


MARKERS = {
    "descent-directions": "The dock slope is -16",
    "descent-method-framework": "The crate coordinate is 7",
    "convergence-rates": "The beacon ratio is 0.125",
    "exact-line-search-quadratic": "The winch step is 3",
    "armijo-backtracking": "The latch value is 19",
    "gradient-zigzag": "The spar coordinate is 3",
    "condition-number-gradient-rate": "The hoist factor is 0.04",
    "lipschitz-gradient": "The cable constant is 12",
    "descent-lemma": "The loft bound is 16",
    "sufficient-decrease-lemma": "The ramp drop is 3",
    "gradient-method-convergence": "The trail bound is 6",
}


def main():
    _balance_mc()
    bank_descent()
    bank_framework()
    bank_rates()
    bank_exact()
    bank_armijo()
    bank_zigzag()
    bank_condition()
    bank_lipschitz()
    bank_descent_lemma()
    bank_sufficient()
    bank_grad_conv()
    expl_descent()
    expl_framework()
    expl_rates()
    expl_exact()
    expl_armijo()
    expl_zigzag()
    expl_condition()
    expl_lipschitz()
    expl_lemma()
    expl_sufficient()
    expl_grad_conv()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    banned = (
        "graz",
        "boyd",
        "nocedal",
        "vandenberghe",
        "hefferon",
        "wikibook",
        "textbook",
        "university",
        "professor",
        "lecture",
        "syllabus",
        "cambridge",
        "springer",
    )
    bad = False
    totals = Counter()
    for sid, phrase in MARKERS.items():
        exp = json.load(open(os.path.join(root, "skilltree", "explainers", sid + ".json"), encoding="utf-8"))
        n = doc_words(exp["sections"])
        bank = json.load(open(os.path.join(root, "skilltree", "bank", sid + ".json"), encoding="utf-8"))
        blob = json.dumps(exp) + json.dumps(bank)
        hits = [w for w in banned if w in blob.lower()]
        figs = sum(1 for q in bank["questions"] if q.get("figure"))
        deep = sum(1 for q in bank["questions"] if q.get("type") in DEEP_TYPES)
        kinds = Counter(q.get("type") for q in bank["questions"])
        totals.update(kinds)
        print(f"{sid}: words {n}, figures {figs}/12, deep {deep}, types {dict(kinds)}")
        if not 250 <= n <= 500:
            print("  word count outside 250-500")
            bad = True
        if hits:
            print("  banned", hits)
            bad = True
        if figs < 9:
            print("  fewer than 9 figures")
            bad = True
        if deep < deep_quota(12):
            print("  deep-type quota miss")
            bad = True
        if phrase not in json.dumps(exp):
            print("  worked-example marker missing")
            bad = True
        if phrase in json.dumps(bank):
            print("  worked example reused in the bank")
            bad = True
    print("totals", dict(totals))
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
