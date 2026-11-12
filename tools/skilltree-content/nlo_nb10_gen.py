#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB10 banks and explainers.

Skills: newton-method-optimization, newton-local-quadratic-convergence,
newton-globalization, wolfe-conditions, quasi-newton-secant, bfgs-update.

Closed-form answers live here. skilltree/verify_nlo_nb10.py recomputes the
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
COL = matrix_fig([["p"], ["q"]], "a column of two labels")
A_COL = "A column of two labels."

P_LOC = ["newton-local-quadratic-convergence"]
P_GLOB = ["newton-globalization"]
P_SEC = ["quasi-newton-secant"]
P_BFGS = ["bfgs-update"]
P_CG = ["conjugate-gradient-method"]
P_HB = ["heavy-ball-method"]
P_NEST = ["nesterov-accelerated-gradient"]
P_SCALED = ["scaled-gradient-projection"]
P_IP = ["primal-dual-interior-point"]


def bank_newton():
    b = Bank("newton-method-optimization")
    b.mc(
        1,
        r"One Newton step for minimization does which of the following?",
        [
            r"Replace the objective by its quadratic Taylor model and step to where that model's gradient is zero.",
            r"Move a fixed distance along the negative gradient and ignore the Hessian.",
            r"Set the Hessian to zero and stop.",
            r"Step in a direction orthogonal to the gradient.",
        ],
        0,
        r"The quadratic model at the current point uses the value, the gradient, and the Hessian. Its gradient is the true gradient plus the Hessian times the step, so a stationary point of the model solves \(\nabla^2 f(x)\, d = -\nabla f(x)\). A fixed gradient step never consults the Hessian. Setting the Hessian to zero removes the model instead of solving it. A direction orthogonal to the gradient has a zero first-order change, which is not the Newton equation.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"Let \(f(x, y) = 2x^2 + y^2 - 8x + 6y\). At \((1, 1)\), what is the second component of the Newton step?",
        -4,
        "1",
        r"The gradient is \((4x - 8,\ 2y + 6)\) and the Hessian is diagonal with entries \(4\) and \(2\). At \((1, 1)\) the gradient is \((-4,\ 8)\). The second Newton equation is \(2 d_2 = -8\), so \(d_2 = -4\). The first component is \(1\), and the sum \(-3\) is not the second component. Reporting \(4\) drops the minus sign in the Newton equation. Reporting \(8\) is the second gradient entry, not the step.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        1,
        r"An invertible linear change of coordinates is applied to the variables. Which claim about Newton's method is right?",
        [
            r"The iterates transform by that same change of coordinates.",
            r"The method becomes steepest descent in the new coordinates.",
            r"The Hessian is replaced by the identity, so the step is the negative gradient.",
            r"The step is unchanged as a list of numbers, with no transformation.",
        ],
        0,
        r"If the new variables are an invertible affine image of the old ones, the Newton step computed in the new coordinates maps back to the Newton step in the old coordinates. The quadratic model transforms with the chain rule, and the stationary point of the model transforms with the variables. Steepest descent does not: it depends on the Euclidean length of the gradient, which a stretch changes. Replacing the Hessian by the identity is steepest descent with step length 1, not Newton. Leaving the numeric step untransformed ignores the change of coordinates.",
        fig=ELL,
        alt=A_ELL,
    )
    b.order(
        2,
        r"Put these steps of one Newton iteration for minimization in order. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient and the Hessian at the current point.",
            r"Write the linear system that sets the quadratic model's gradient to zero: the Hessian times the step equals the negative gradient.",
            r"Solve that linear system for the step.",
            r"Replace the current point by the point plus the step.",
        ],
        r"The linear system is built from the gradient and the Hessian, so those have to be evaluated first. The system has to be written before it can be solved. The point moves only after the step is known. Rebuilding the model at the new point is the start of the next iteration, not a step that can be swapped with the solve.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which claims about a Newton step for minimization are true?",
        [
            r"On a quadratic with an invertible Hessian, one step lands on the unique stationary point.",
            r"A singular Hessian still determines exactly one Newton step.",
            r"If the Hessian is positive definite and the gradient is not zero, the step is a descent direction.",
            r"On a quadratic whose Hessian is negative definite, the step lands on the maximizer.",
            r"The Newton step is orthogonal to the gradient for every symmetric Hessian.",
        ],
        [0, 2, 3],
        r"A quadratic equals its own second-order model, so the Newton equation is the exact stationarity condition. An invertible Hessian makes that stationary point unique, and one step reaches it."
        "\n"
        r"• A singular Hessian gives either no solution or infinitely many. It does not determine one step."
        "\n"
        r"• With a positive definite Hessian the directional derivative along \(d = -H^{-1} g\) is \(-g^T H^{-1} g\), which is negative when \(g \ne 0\)."
        "\n"
        r"• A negative definite quadratic has a single stationary point, and that point is a maximum. The Newton step still solves for it."
        "\n"
        r"• The directional derivative \(-g^T H^{-1} g\) is zero only in special cases, such as a zero gradient. It is not zero for every symmetric Hessian. At a point where the gradient is \((1, 0)\) and the Hessian is the identity, the step is \((-1, 0)\), and the dot product with the gradient is \(-1\), not \(0\).",
        fig=LEV,
        alt=A_LEV,
    )
    b.sym(
        2,
        r"The gradient entries are \(a\) and \(b\), and the Hessian is diagonal with positive entries \(p\) and \(q\). The sum of the two Newton-step components equals",
        "-a/p-b/q",
        {"a": (-3, 3), "b": (-3, 3), "p": (1, 4), "q": (1, 4)},
        r"Each diagonal equation is \(p\) times the first component equals \(-a\), and \(q\) times the second equals \(-b\). The components are \(-a/p\) and \(-b/q\), so their sum is \(-a/p - b/q\). Every declared name appears. Dropping both minus signs climbs the model. Adding \(p\) and \(q\) in the denominator, as in \(-(a+b)/(p+q)\), mixes the two uncoupled equations. Using \(a/p + b/q\) forgets that the right-hand side is the negative gradient.",
        alternates=["-(a/p)-(b/q)", "-(a/p+b/q)"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        r"A note computes a Newton step for \(f(t) = t^3 - 6t\) at \(t = 2\). Exactly one step is a false claim.",
        [
            r"The derivative \(3t^2 - 6\) equals \(6\) at \(t = 2\).",
            r"The second derivative \(6t\) equals \(12\) at \(t = 2\).",
            r"The Newton equation \(12 d = -6\) gives \(d = -1/2\).",
            r"Replacing that second derivative by \(6\) gives the same step \(-1/2\).",
        ],
        3,
        r"Differentiating \(t^3 - 6t\) gives \(3t^2 - 6\), and at \(t = 2\) that is \(12 - 6 = 6\). Differentiating again gives \(6t\), which equals \(12\) at \(t = 2\). Then \(12 d = -6\), so \(d = -1/2\). The false step replaces \(6t\) by \(6\). That different equation is \(6 d = -6\), so \(d = -1\), not \(-1/2\).",
        [
            r"The second derivative is \(6t\), so replacing \(12\) by \(6\) changes the step from \(-1/2\) to \(-1\).",
            r"The first derivative at \(t = 2\) is not \(6\).",
            r"The equation \(12 d = -6\) does not give \(d = -1/2\).",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"For \(f(t) = t^3 - 6t\) at \(t = 2\), what is the Newton step \(d\)?",
        -0.5,
        "1",
        r"The derivative is \(3t^2 - 6\), so at \(t = 2\) it equals \(6\). The second derivative is \(6t\), so at \(t = 2\) it equals \(12\). Then \(12 d = -6\) and \(d = -1/2\). Reporting \(1/2\) drops the minus sign. Reporting \(-1\) uses \(6\) in place of \(6t\). Reporting \(1.5\) is the updated point \(2 - 1/2\), not the step. Reporting \(12\) is the second derivative.",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        3,
        r"For \(f(t) = -2t^2\) at \(t = 3\), the Newton step lands on a maximizer because",
        [
            r"the second derivative is negative, and the step solves the stationarity equation exactly",
            r"Newton always returns a minimizer, so the landing point minimizes \(f\)",
            r"the second derivative is zero, so every point is stationary",
            r"the step equals the gradient, which points toward a saddle",
        ],
        0,
        r"Here \(f'(t) = -4t\) and \(f''(t) = -4\). At \(t = 3\) the derivative is \(-12\), and \(-4 d = 12\) gives \(d = -3\). The next point is \(0\), where the derivative vanishes. The second derivative is negative everywhere, so that stationary point is a maximum. Newton does not switch to minimization when the curvature is negative. The second derivative is \(-4\), not zero. The step is \(-3\), while the gradient entry is \(-12\).",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        4,
        r"Near a minimizer whose Hessian is positive definite and Lipschitz, the local error of Newton's method is",
        [
            r"bounded by a constant times the square of the previous error",
            r"a fixed fraction of the previous error, with the fraction equal to the condition number",
            r"unchanged, because the Hessian is constant only for quadratics",
            r"the reciprocal of the iteration count, from every starting point",
        ],
        0,
        r"A Lipschitz Hessian makes the remainder of the linear model quadratic in the error. After multiplying by the inverse Hessian, the next error is at most a constant times the square of the current error, once the start is close enough. A fixed fraction of the previous error is a linear rate. The Hessian does not have to be constant for that squared bound; Lipschitz control of its change is enough. A reciprocal of the iteration count is a sublinear pattern, and it is not claimed for every start.",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_LOC,
    )
    b.num(
        4,
        r"Let \(f(t) = 3t^2 - 12t\). At \(t = 0\), the Newton step is a descent direction. What is the directional derivative of \(f\) along that step?",
        -24,
        "1",
        r"The derivative is \(6t - 12\) and the second derivative is \(6\). At \(t = 0\) the derivative is \(-12\), so \(6 d = 12\) and \(d = 2\). The directional derivative is \(-12 \cdot 2 = -24\). The negative sign is what makes the step a descent direction. Reporting \(24\) drops that sign. Reporting \(-12\) is the derivative, not its product with the step. Reporting \(2\) is the step.",
        fig=FALL,
        alt=A_FALL,
        preview=P_GLOB,
    )
    b.mc(
        4,
        r"When forming the Hessian is too expensive, the method that keeps the Newton linear equation but replaces the Hessian by a matrix built from gradient changes is",
        [
            r"a quasi-Newton method, requiring that matrix to satisfy a secant equation",
            r"a simplex pivot on a linear program",
            r"an Armijo test that never forms a direction",
            r"a power iteration for the largest eigenvalue",
        ],
        0,
        r"A quasi-Newton iteration stores an approximation of the Hessian, or of its inverse, and updates it from the step and the change in the gradient. The secant equation asks that approximation to act on the step the way the gradient change does. A simplex pivot changes a basis of a linear program. Armijo accepts or rejects a length after a direction exists. Power iteration multiplies by a matrix to find an eigenvector.",
        fig=MAT,
        alt=A_MAT,
        preview=P_SEC,
    )
    b.save()


def bank_local():
    b = Bank("newton-local-quadratic-convergence")
    b.mc(
        1,
        r"Quadratic convergence of the error means that, eventually,",
        [
            r"the next error is at most a constant times the square of the current error",
            r"the next error is a fixed fraction of the current error, with the fraction in \((0, 1)\)",
            r"the error drops by the same additive amount at every iteration",
            r"the error is the reciprocal of the iteration count and the ratio of successive errors tends to \(1\)",
        ],
        0,
        r"The quadratic pattern is a bound by a constant times the squared error. A fixed fraction of the current error is Q-linear convergence. An additive drop is not a rate on the error ratio. A reciprocal of the iteration count, with successive ratios tending to \(1\), is sublinear.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.num(
        1,
        r"Let \(f'(t) = t(t - 2)\) and \(f''(t) = 2t - 2\), with a minimizer at \(t = 2\). Starting at \(t = 3\), what is the absolute error \(\lvert t_+ - 2\rvert\) after one Newton step?",
        0.25,
        "1",
        r"At \(t = 3\) the derivative is \(3\) and the second derivative is \(4\). The step is \(-3/4\), so the next point is \(3 - 3/4 = 9/4\). The absolute error is \(\lvert 9/4 - 2\rvert = 1/4\). Reporting \(3/4\) is the length of the step, not the distance to \(2\). Reporting \(1\) is the error before the step. Reporting \(3\) is the derivative.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        1,
        r"The local quadratic bound for Newton's method needs which hypothesis at the minimizer, besides a Lipschitz Hessian nearby?",
        [
            r"The Hessian at the minimizer is positive definite.",
            r"The Hessian at the minimizer is singular.",
            r"The gradient at the minimizer is nonzero.",
            r"The objective is linear.",
        ],
        0,
        r"Positive definiteness makes the minimizer a strict local minimizer and keeps the Hessian invertible, so the Newton step exists and the inverse that multiplies the remainder stays bounded nearby. A singular Hessian leaves the step undefined and the bound, which divides by that curvature, does not apply. A nonzero gradient would mean the point is not stationary. A linear objective has a zero Hessian, which is the singular case.",
        fig=ELL,
        alt=A_ELL,
    )
    b.order(
        2,
        r"Put this proof sketch of the local Newton bound in order. Each step uses the result of the step before it.",
        [
            r"Use stationarity to set the gradient at the minimizer to zero.",
            r"Write the gradient at the current point as the integral of the Hessian along the segment from the minimizer.",
            r"Rearrange the Newton update so the next error equals the inverse Hessian times the integral of the Hessian differences along that segment.",
            r"Bound those Hessian differences by the Lipschitz constant, which produces a constant times the squared error.",
        ],
        r"Stationarity removes the gradient at the minimizer, so the integral of the Hessian equals the gradient at the current point. That integral has to be in hand before it can be subtracted from the Hessian times the error. The rearrangement uses the Newton formula and that subtraction. The Lipschitz bound is applied to the difference that the rearrangement isolated. The squared factor appears only after that estimate.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which statements belong to the local quadratic theorem for Newton's method on a smooth objective?",
        [
            r"The Hessian at the minimizer is positive definite.",
            r"The Hessian is Lipschitz in a neighborhood of the minimizer.",
            r"Inside a small enough neighborhood, the next error is at most a constant times the square of the current error.",
            r"The same squared bound holds at every starting point of every smooth function.",
            r"The bound still holds when the Hessian at the minimizer is singular.",
        ],
        [0, 1, 2],
        r"Positive definiteness at the minimizer gives a strict local minimizer and an invertible Hessian."
        "\n"
        r"• A Lipschitz Hessian turns the remainder of the tangent model into a term controlled by the squared distance."
        "\n"
        r"• Those two facts produce a neighborhood in which the next error is at most a constant times the squared error, and the iterates stay in that neighborhood."
        "\n"
        r"• A start outside that neighborhood can diverge or run toward a different stationary point. Smoothness alone does not put every start inside the basin."
        "\n"
        r"• A singular Hessian at the minimizer makes the Newton step undefined there, so the bound, which uses the inverse Hessian, does not apply. For \(f'(t) = t(t-2)\) the second derivative vanishes at \(t = 1\), and no real Newton step exists at that point.",
        fig=LEV,
        alt=A_LEV,
    )
    b.sym(
        2,
        r"A scalar error of size \(z\), a Hessian Lipschitz constant \(L\), and a second derivative \(h\) give the local bound \((L/(2h)) z^2\). That bound equals",
        "(L*z*z)/(2*h)",
        {"L": (0.5, 3), "z": (0.2, 2), "h": (1, 5)},
        r"The integral of a Lipschitz change in the second derivative contributes a factor \(L/2\) times \(z^2\). Dividing by the second derivative \(h\) produces \((L z^2)/(2h)\). Every declared name appears. Using \(L z / h\) is a linear bound, not a squared one. Dropping the \(2\) doubles the estimate. Placing \(h\) in the numerator, as in \(L h z^2 / 2\), inverts the curvature factor.",
        alternates=["L*z**2/(2*h)", "(L/(2*h))*z*z"],
        fig=SLOW,
        alt=A_SLOW,
    )
    b.find_error(
        3,
        r"A note treats \(t = 1\) for \(f'(t) = t(t-2)\) and \(f''(t) = 2t-2\). Exactly one step is a false claim.",
        [
            r"The derivative at \(t = 1\) equals \(-1\).",
            r"The second derivative at \(t = 1\) equals \(0\).",
            r"The Newton step is defined and equals \(1\), because a zero second derivative is replaced by \(1\).",
            r"The local error bound divides by the second derivative, so it does not apply at a point where that derivative is \(0\).",
        ],
        2,
        r"At \(t = 1\) the derivative is \(1 \cdot (1-2) = -1\), and the second derivative is \(2-2 = 0\). Dividing by that second derivative is undefined, so there is no real Newton step. Replacing \(0\) by \(1\) is a different algorithm. The local bound really does divide by the curvature: the factor in front of the squared error contains the reciprocal of the second derivative. That factor is not available where the second derivative vanishes.",
        [
            r"A zero second derivative leaves the Newton step undefined. It is not replaced by \(1\).",
            r"The derivative at \(t = 1\) is not \(-1\).",
            r"The second derivative at \(t = 1\) is not \(0\).",
        ],
        0,
        fig=RISE,
        alt=A_RISE,
    )
    b.num(
        3,
        r"With the same derivatives \(f'(t) = t(t-2)\) and \(f''(t) = 2t-2\), start at \(t = 4\). The minimizer is \(t = 2\). What is the absolute error \(\lvert t_+ - 2\rvert\) after one Newton step?",
        2 / 3,
        "1",
        r"At \(t = 4\) the derivative is \(8\) and the second derivative is \(6\). The step is \(-8/6 = -4/3\), so the next point is \(4 - 4/3 = 8/3\). The absolute error is \(\lvert 8/3 - 2\rvert = 2/3\). Reporting \(4/3\) is the step length. Reporting \(2\) is the error before the step. Reporting \(8/3\) is the next point, not its distance to \(2\).",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        3,
        r"An iteration produces errors \(0.2\), then \(0.01\). The new error divided by the square of the old error equals \(1/4\), and that pattern continues with a bounded constant. The rate is",
        [
            r"quadratic",
            r"only linear, because the errors became smaller",
            r"sublinear, because the ratio of the successive errors is \(1/20\)",
            r"divergent, because the constant \(1/4\) is not zero",
        ],
        0,
        r"A bounded ratio of the new error to the square of the old error is the quadratic pattern. Becoming smaller is also true of linear and sublinear sequences, so the decrease alone does not name the rate. The successive ratio \(0.01/0.2 = 1/20\) would describe a linear rate only if that ratio tended to a positive limit rather than the squared comparison staying bounded. A positive constant in front of the squared error is part of the quadratic bound. Divergence would mean the error fails to go to zero.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        4,
        r"A method that reaches the minimizer of a positive definite quadratic in at most \(n\) steps, rather than by a local squared-error bound, is",
        [
            r"a conjugate-direction method",
            r"a repeat of the local Newton bound at a singular Hessian",
            r"a sublinear gradient guarantee with no curvature",
            r"a line search that stops after one failed trial",
        ],
        0,
        r"Conjugate directions finish a positive definite quadratic in at most as many steps as the dimension, using conjugacy rather than a local squared-error estimate. The local Newton bound needs an invertible Hessian, so it does not start from a singular one. A sublinear gradient guarantee does not claim finite termination. One failed line-search trial is not a method for the quadratic.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_CG,
    )
    b.num(
        4,
        r"The second derivative is \(f''(t) = 2t - 2\). What is the difference quotient \(\lvert f''(5) - f''(2)\rvert / \lvert 5 - 2\rvert\)?",
        2,
        "1",
        r"\(f''(5) = 8\) and \(f''(2) = 2\), so the absolute difference is \(6\). Dividing by the distance \(3\) gives \(2\). That quotient is the Lipschitz constant of this second derivative, because the second derivative is linear with slope \(2\). Reporting \(6\) skips the division. Reporting \(3\) is the distance between the sample points. Reporting \(8\) is \(f''(5)\).",
        fig=SEG,
        alt=A_SEG,
        preview=P_HB,
    )
    b.mc(
        4,
        r"A later first-order scheme keeps a global rate on smooth convex problems and does not need a start inside the Newton basin. That scheme is",
        [
            r"an extrapolated gradient step whose function gap can decay like one over the square of the iteration count",
            r"a Newton step taken from an arbitrary start with no line search",
            r"a method that stops when the Hessian is positive definite",
            r"a single gradient evaluation with no further updates",
        ],
        0,
        r"The extrapolated scheme builds the next point from a gradient step at a shifted location. On smooth convex objectives the gap between the objective value and its minimum is bounded by a constant over the square of the iteration count. That bound is on the function gap, not on the distance to the minimizer. It is a weaker claim than a local squared-error bound, and it does not ask the start to lie in a Newton basin. A bare Newton step from an arbitrary start can leave the region where the quadratic model is faithful. Stopping at the first positive definite Hessian does not produce a rate. One gradient evaluation is a single step, not a rate.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_NEST,
    )
    b.save()


def bank_global():
    b = Bank("newton-globalization")
    b.mc(
        1,
        r"A plain Newton direction can fail to be a descent direction when",
        [
            r"the Hessian is not positive definite",
            r"the Hessian is positive definite and the gradient is not zero",
            r"the step length is shortened below \(1\)",
            r"the objective is a positive definite quadratic",
        ],
        0,
        r"The directional derivative of a Newton step is \(-g^T H^{-1} g\) only when \(H\) is invertible, and that quantity is negative for every nonzero \(g\) when \(H\) is positive definite. If \(H\) has a negative eigenvalue, the same formula can be positive, so the step climbs. Shortening a length cannot repair a direction that climbs: every positive length still increases the model. A positive definite quadratic is the case where the plain Newton step is a descent step and lands on the minimizer.",
        fig=RISE,
        alt=A_RISE,
    )
    b.num(
        1,
        r"At a point where the derivative is \(6\) and the second derivative is \(-2\), a shift \(\mu = 6\) is added before the Newton equation. What is the shifted step?",
        -1.5,
        "1",
        r"The shifted curvature is \(-2 + 6 = 4\). The equation is \(4 d = -6\), so \(d = -3/2\). The unshifted equation \(-2 d = -6\) gives \(d = 3\), which has a positive directional derivative \(6 \cdot 3 = 18\) and is not the shifted step. Reporting \(3/2\) drops the minus sign. Reporting \(4\) is the shifted curvature.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        1,
        r"Damped Newton means",
        [
            r"keep a descent direction and shorten the trial length until a sufficient-decrease test accepts it",
            r"replace the gradient by zero and skip the solve",
            r"take the full Newton step even when the objective increases",
            r"subtract a positive multiple of the identity so the Hessian becomes indefinite",
        ],
        0,
        r"Damping here is a line search on a direction that is already descent. A rejected length is replaced by a shorter one until sufficient decrease holds. Replacing the gradient by zero removes the right-hand side. Taking a full step that increases the objective is the failure damping is meant to avoid. A positive shift is added to the Hessian, not subtracted. Subtracting would push eigenvalues down.",
        fig=FALL,
        alt=A_FALL,
    )
    b.order(
        2,
        r"The Hessian at the current point is not positive definite. Put the steps of one shifted, damped Newton iteration in order. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient and the Hessian at the current point.",
            r"Add a positive multiple of the identity large enough that the shifted Hessian is positive definite.",
            r"Solve the shifted linear system for the direction.",
            r"Shorten the trial length by repeated factors in \((0, 1)\) until the Armijo inequality accepts it.",
            r"Move the point by the accepted length times that direction.",
        ],
        r"The shift is chosen from the Hessian that was just evaluated, so the evaluation comes first. The linear system uses the shifted matrix, so the shift comes before the solve. The trial length is a scalar along the direction that the solve produced. The point moves only after a length has been accepted. Accepting and rejecting are not separate branches in this list: shortening until acceptance is one step, and it has to finish before the move.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"The second derivative is \(-2\). Which shifts \(\mu\) make the shifted curvature \(-2 + \mu\) positive?",
        [
            r"\(\mu = 1\)",
            r"\(\mu = 3\)",
            r"\(\mu = 2\)",
            r"\(\mu = 6\)",
        ],
        [1, 3],
        r"Positive definite curvature in one variable is a positive number, not zero."
        "\n"
        r"• \(\mu = 1\) leaves \(-1\), which is negative."
        "\n"
        r"• \(\mu = 3\) leaves \(1\), which is positive."
        "\n"
        r"• \(\mu = 2\) leaves \(0\). A zero curvature is singular, so the shifted Newton equation does not determine a step."
        "\n"
        r"• \(\mu = 6\) leaves \(4\), which is positive.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.sym(
        2,
        r"A scalar derivative \(g\), second derivative \(h\), and shift \(m\) produce the shifted Newton step",
        "-g/(h+m)",
        {"g": (-5, 5), "h": (-3, 3), "m": (4, 8)},
        r"The shifted equation is \((h+m) d = -g\). The ranges keep \(h+m\) positive, so there is one step, \(d = -g/(h+m)\). Every declared name appears. Using \(-g/h\) ignores the shift. Using \(-g/(h-m)\) subtracts the shift and can destroy the positive curvature the shift was added to create. Using \((h+m)/g\) inverts the equation.",
        alternates=["-(g)/(h+m)", "(-g)/(h+m)"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note shifts a second derivative of \(-3\) by \(\mu = 1\), with derivative \(4\). Exactly one step is a false claim.",
        [
            r"The shifted curvature \(-3 + 1\) equals \(-2\).",
            r"The equation \(-2 d = -4\) gives \(d = 2\).",
            r"The directional derivative \(4 \cdot 2 = 8\) is negative, so the direction is a descent direction.",
            r"The curvature stays nonpositive until the shift is larger than \(3\).",
        ],
        2,
        r"The shifted curvature is \(-2\), and \(-2 d = -4\) does give \(d = 2\). The product of the derivative and that step is \(8\), which is positive, so the objective increases to first order. A descent direction would need a negative directional derivative. The last claim is true: \(-3 + \mu > 0\) forces \(\mu > 3\). The shift \(1\) is too small.",
        [
            r"The product \(4 \cdot 2\) equals \(8\), which is positive, so the direction is not descent.",
            r"The shifted curvature is not \(-2\).",
            r"The equation \(-2 d = -4\) does not give \(d = 2\).",
        ],
        0,
        fig=RISE,
        alt=A_RISE,
    )
    b.num(
        3,
        r"The derivative is \(4\), the second derivative is \(-3\), and the shift is \(\mu = 5\). What is the directional derivative along the shifted Newton step?",
        -8,
        "1",
        r"The shifted curvature is \(-3 + 5 = 2\). Then \(2 d = -4\), so \(d = -2\). The directional derivative is \(4 \cdot (-2) = -8\). The negative sign says the shifted step is a descent direction. Reporting \(8\) drops that sign. Reporting \(-2\) is the step. Reporting \(2\) is the shifted curvature. With the too-small shift \(\mu = 1\), the step would be \(2\) and the directional derivative would be \(8\), which is the quantity this shift avoids.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        3,
        r"Once a shifted Newton direction is a descent direction, Armijo backtracking",
        [
            r"replaces a rejected length \(t\) by \(\beta t\) with \(\beta \in (0, 1)\)",
            r"doubles the length until the objective increases",
            r"flips the sign of the direction after every rejected trial",
            r"removes the shift before the first trial",
        ],
        0,
        r"Backtracking starts from a trial length and multiplies it by a fixed factor in \((0, 1)\) whenever the sufficient-decrease inequality fails. A descent direction guarantees that a short enough trial passes. Doubling the length goes the other way. Flipping the sign turns a descent direction into an ascent direction. The shift is what made the direction a descent direction, so it stays in place during the line search.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        4,
        r"A later method takes a Newton step in a scaled metric and then projects the result onto a convex set. That method is",
        [
            r"a scaled projected step, with the ordinary projected gradient recovered when the scaling is the identity",
            r"a simplex ratio test on a linear program",
            r"a power iteration that ignores the feasible set",
            r"an exact line search along a coordinate axis with no projection",
        ],
        0,
        r"Scaling by a positive definite matrix, such as a shifted Hessian, changes the metric of the step. Projecting in that metric keeps the next point feasible. When the scaling is the identity, the step is an ordinary gradient step before the projection. A simplex ratio test chooses a step that stays nonnegative in a linear program, without a Newton metric. Power iteration looks for an eigenvector. An exact line search on an axis does not project a Newton step.",
        fig=HALF,
        alt=A_HALF,
        preview=P_SCALED,
    )
    b.num(
        4,
        r"The Hessian is diagonal with entries \(-1\) and \(4\). What is the smallest positive integer shift \(\mu\) that makes this Hessian plus \(\mu I\) positive definite?",
        2,
        "1",
        r"The shifted eigenvalues are \(-1 + \mu\) and \(4 + \mu\). Both are positive only when \(\mu > 1\). The smallest positive integer with that property is \(2\): the eigenvalues are then \(1\) and \(6\). The shift \(1\) leaves a zero eigenvalue, which is singular rather than positive definite. The shift \(4\) also works, but it is not the smallest positive integer. Reporting \(-1\) is an eigenvalue of the unshifted matrix.",
        fig=MAT,
        alt=A_MAT,
        preview=P_SCALED,
    )
    b.mc(
        4,
        r"A later root iteration solves a perturbed complementarity system by Newton steps that are kept inside the positive region. That iteration is",
        [
            r"a primal-dual interior step on the perturbed system",
            r"a projected gradient step with no linear solve",
            r"a line search that refuses every positive length",
            r"a shift that makes the Hessian singular on purpose",
        ],
        0,
        r"The perturbed system is a set of nonlinear equations, one block of them from complementarity. A Newton step linearizes that system, and the step is controlled so the iterates stay positive. That is an interior method. A projected gradient step does not solve the perturbed Jacobian system. Refusing every positive length stalls. A shift that creates a zero eigenvalue removes the Newton step instead of keeping it inside the region.",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_IP,
    )
    b.save()


def bank_wolfe():
    b = Bank("wolfe-conditions")
    b.mc(
        1,
        r"The Wolfe conditions on a step length are",
        [
            r"sufficient decrease, plus a curvature test on the new directional derivative",
            r"the single requirement that the step length equal \(1\)",
            r"the requirement that the Hessian equal the identity",
            r"the requirement that the new gradient be exactly zero",
        ],
        0,
        r"Sufficient decrease is the Armijo inequality, with parameter \(c_1 \in (0, 1)\). The curvature test asks the new directional derivative to be at least \(c_2\) times the old one, with \(c_1 < c_2 < 1\). A length of \(1\) can fail either test. The Hessian is not required to be the identity. A zero new gradient would be stationarity of the whole problem, which a line search does not demand.",
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        1,
        r"Let \(f(t) = -t^2\), with start \(t = 1\), direction \(d = 1\), and step length \(1\). The step is \(s = 1\) and the gradient change is \(y\). What is \(y\, s\)?",
        -2,
        "1",
        r"The derivative is \(-2t\). It equals \(-2\) at \(t = 1\) and \(-4\) at \(t = 2\). Then \(y = -4 - (-2) = -2\) and \(s = 1\), so \(y s = -2\). The objective falls from \(-1\) to \(-4\), so a pure decrease test can accept the step, but the curvature product is negative. Reporting \(2\) drops the sign of \(y\). Reporting \(-4\) is the new derivative. Reporting \(-6\) adds the derivatives instead of subtracting them.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        1,
        r"If the old directional derivative is negative, the Wolfe curvature test forces the new directional derivative to be",
        [
            r"at least \(c_2\) times the old one, hence no more negative than that multiple",
            r"strictly more negative than the old one",
            r"exactly zero",
            r"equal to the trace of the Hessian",
        ],
        0,
        r"The test is \(\nabla f(x+td)^T d \ge c_2 \nabla f(x)^T d\) with \(c_2 < 1\). The old directional derivative is negative, and \(c_2\) times it is a larger number (closer to zero, or beyond). The new directional derivative has to reach at least that value. Asking it to be more negative is the opposite inequality. The test does not require a stationary point, and it does not mention the trace.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.order(
        2,
        r"Put this argument that the Wolfe conditions imply \(y^T s > 0\) in order. Each step uses the result of the step before it.",
        [
            r"Start from a descent direction, so the directional derivative \(g\) is negative, and from a step \(s = t d\) with \(t > 0\).",
            r"Apply the curvature inequality: the new directional derivative is at least \(c\) times \(g\), with \(c < 1\).",
            r"Subtract \(g\) from both sides, which produces a difference of directional derivatives at least \((c - 1) g\).",
            r"Multiply by \(t > 0\) to conclude that \(y^T s\) is at least \(t(c-1)g\), hence positive.",
        ],
        r"Curvature compares the new directional derivative with the old one, so the old value and the fact that it is negative have to come first. Subtracting \(g\) uses that inequality and produces the difference that equals \(y^T d\). Multiplying by the positive length \(t\) turns \(y^T d\) into \(y^T s\). The sign of the lower bound uses \(c - 1 < 0\) and \(g < 0\), which are already in the earlier steps. The two comparisons cannot be swapped: the subtraction is the curvature inequality after a rewrite, not a separate test.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Let \(f(t) = t^2\), with start \(t = 2\) and direction \(d = -1\). Use \(c_1 = 1/10\) and \(c_2 = 1/2\). Sufficient decrease uses \(c_1\). Curvature requires the new directional derivative to be at least \(c_2\) times the old one. Which step lengths satisfy both?",
        [
            r"\(1/2\)",
            r"\(1\)",
            r"\(2\)",
            r"\(4\)",
        ],
        [1, 2],
        r"The derivative is \(2t\), so the old directional derivative is \(4 \cdot (-1) = -4\). The new point is \(2 - \alpha\), and the new directional derivative is \(-2(2-\alpha)\)."
        "\n"
        r"• At \(\alpha = 1/2\) the new directional derivative is \(-3\), and \(-3 \ge -2\) fails. Sufficient decrease holds, since \(2.25 \le 3.8\), but curvature does not."
        "\n"
        r"• At \(\alpha = 1\) the new directional derivative is \(-2\), so curvature holds with equality. The value \(1\) is at most \(4 - 0.4 = 3.6\), so decrease holds too."
        "\n"
        r"• At \(\alpha = 2\) the new directional derivative is \(0\), which is greater than \(-2\). The value \(0\) is at most \(4 - 0.8 = 3.2\), so both tests hold."
        "\n"
        r"• At \(\alpha = 4\) the new directional derivative is \(4\), so curvature holds, but the value \(4\) is larger than \(4 - 1.6 = 2.4\), so sufficient decrease fails.",
        fig=LEV,
        alt=A_LEV,
    )
    b.sym(
        2,
        r"A step length \(t > 0\), a curvature parameter \(c \in (0, 1)\), and a negative directional derivative \(g\) produce the Wolfe lower bound \(t(c-1)g\) on \(y^T s\). That bound equals",
        "t*(c-1)*g",
        {"t": (0.2, 3), "c": (0.1, 0.9), "g": (-5, -0.2)},
        r"Curvature says the new directional derivative is at least \(c g\). Subtracting \(g\) leaves a difference at least \((c-1)g\). The gradient change along \(s = t d\) multiplies that difference by \(t\), which is \(t(c-1)g\). Every declared name appears. Because \(c-1\) and \(g\) are both negative, the bound is positive. Using \(t(c+1)g\) has the wrong sign and is negative for these ranges. Using \(t c g\) drops the subtraction of the old directional derivative. Using \((c-1)g/t\) divides by the length instead of multiplying.",
        alternates=["(c-1)*t*g", "g*t*(c-1)"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note checks the length \(1/2\) for \(f(t) = t^2\), start \(t = 2\), direction \(d = -1\), \(c_1 = 1/10\), and \(c_2 = 1/2\). Exactly one step is a false claim.",
        [
            r"The old directional derivative is \(4 \cdot (-1) = -4\).",
            r"The new point is \(1.5\), and the new directional derivative is \(3 \cdot (-1) = -3\).",
            r"Sufficient decrease holds, because the new value \(2.25\) is at most \(4 - 0.2 = 3.8\).",
            r"Curvature holds, because \(-3 \le -2\).",
        ],
        3,
        r"The old directional derivative is \(-4\). The point \(2 + (1/2)(-1) = 1.5\) has derivative \(3\), so the new directional derivative is \(-3\). The Armijo right-hand side is \(4 + (1/10)(1/2)(-4) = 3.8\), and \(2.25 \le 3.8\), so sufficient decrease holds. Curvature asks for \(-3 \ge (1/2)(-4) = -2\). That comparison fails. The inequality \(-3 \le -2\) is true as arithmetic and is the wrong direction for the test.",
        [
            r"Curvature requires the new directional derivative to be at least \(c_2\) times the old one. Here \(-3 < -2\), so the test fails.",
            r"The old directional derivative is not \(-4\).",
            r"Sufficient decrease fails for these values.",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"For \(f(t) = t^2\), start \(t = 2\), direction \(d = -1\), and step length \(1\), what is \(y^T s\)?",
        2,
        "1",
        r"The step is \(s = -1\). The derivative changes from \(4\) at \(t = 2\) to \(2\) at \(t = 1\), so \(y = 2 - 4 = -2\). Then \(y^T s = (-2)(-1) = 2\). Reporting \(-2\) is \(y\), or \(s\), rather than the product. Reporting \(4\) is the old derivative. Reporting \(6\) adds the absolute values of the derivatives.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        3,
        r"The two Wolfe parameters must satisfy",
        [
            r"\(0 < c_1 < c_2 < 1\)",
            r"\(c_2 = 0\) and \(c_1 = 1\)",
            r"\(c_1 > c_2 > 1\)",
            r"\(c_1 < 0\) and \(c_2 > 2\)",
        ],
        0,
        r"Sufficient decrease uses a \(c_1\) strictly between \(0\) and \(1\), so the right-hand side still goes down when the directional derivative is negative, but not as fast as the linear model. Curvature uses a larger \(c_2\) that is still strictly less than \(1\). That gap is what makes \(y^T s\) positive. Setting \(c_1 = 1\) asks for a decrease the linear model itself may not beat on a curved function, and \(c_2 = 0\) does not force the slope to rise. A parameter above \(1\), or a negative \(c_1\), leaves the standard pair.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        r"A positive product \(y^T s\) is the curvature hypothesis used to keep which update positive definite?",
        [
            r"the BFGS update of an inverse Hessian approximation",
            r"a simplex pivot",
            r"a power iteration",
            r"a projection onto a half-space with no gradient change",
        ],
        0,
        r"BFGS divides by \(y^T s\) and preserves positive definiteness when that product is positive and the previous approximation was positive definite. The Wolfe curvature test is one way to guarantee the product. A simplex pivot changes a basis. Power iteration multiplies by a fixed matrix. A half-space projection does not form \(y\).",
        fig=MAT,
        alt=A_MAT,
        preview=P_BFGS,
    )
    b.num(
        4,
        r"For \(f(t) = t^2\), start \(t = 2\), and direction \(d = -1\), the curvature test with \(c_2 = 9/10\) holds only when the step length is at least some positive number. What is that number?",
        0.2,
        "1",
        r"The new directional derivative is \(-4 + 2\alpha\), and the old one is \(-4\). Curvature says \(-4 + 2\alpha \ge (9/10)(-4)\), so \(2\alpha \ge 4 - 3.6 = 0.4\), and \(\alpha \ge 0.2\). Reporting \(0.4\) stops before dividing by \(2\). Reporting \(2\) is the factor in front of \(\alpha\), from the second derivative times the direction. Reporting \(9/10\) is \(c_2\).",
        fig=SEG,
        alt=A_SEG,
        preview=P_BFGS,
    )
    b.mc(
        4,
        r"A line search that keeps only sufficient decrease, and skips the curvature test, can return a step with",
        [
            r"\(y^T s < 0\), which the BFGS positive-definiteness argument excludes",
            r"\(y^T s > 0\) for every objective, including \(f(t) = -t^2\)",
            r"a zero gradient at the new point, for every objective",
            r"an accepted length of \(0\)",
        ],
        0,
        r"On \(f(t) = -t^2\), the step from \(t = 1\) in the direction \(d = 1\) with length \(1\) decreases the objective from \(-1\) to \(-4\), so a sufficient-decrease test can accept it, while \(y s = -2\). BFGS needs a positive product and does not promise to stay positive definite for this step. The same example shows the product is not positive for every objective. The new derivative is \(-4\), not zero. A length of \(0\) does not move, and the line search looks for a positive length.",
        fig=RISE,
        alt=A_RISE,
        preview=P_BFGS,
    )
    b.save()


def bank_secant():
    b = Bank("quasi-newton-secant")
    b.mc(
        1,
        r"The secant equation asks a Hessian approximation \(B\) to satisfy",
        [
            r"\(B s = y\), where \(s\) is the step and \(y\) is the change in the gradient",
            r"\(B = I\) at every iteration",
            r"\(s = 0\) and \(y = 0\)",
            r"\(B\) orthogonal to both \(s\) and \(y\)",
        ],
        0,
        r"Along the step just taken, the gradient change is the action of an average Hessian. The secant equation asks \(B\) to match that action: \(B s = y\). The identity satisfies it only when \(s = y\). A zero step makes \(B s = y\) impossible unless \(y\) is zero too, and a zero step is not a useful update. Orthogonality would make \(B s\) perpendicular to \(s\), while the equation sets \(B s\) equal to \(y\).",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        1,
        r"A scalar step is \(s = -1\) and the gradient change is \(y = -2\). The secant equation \(B s = y\) forces \(B\) to equal",
        2,
        "1",
        r"The equation is \(B \cdot (-1) = -2\), so \(B = 2\). For \(f(t) = t^2\) this is the constant second derivative: a step from \(2\) to \(1\) changes the derivative from \(4\) to \(2\). Reporting \(-2\) keeps the ratio \(y/s\) without canceling the two minus signs. Reporting \(-1\) is the step. Reporting \(1\) is the reciprocal of the absolute step.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        1,
        r"The fundamental theorem along the segment from \(x\) to \(x+s\) says that the gradient change \(y\) equals",
        [
            r"the integral, along the segment, of the Hessian applied to \(s\)",
            r"the gradient at \(x\) alone",
            r"the change in the objective divided by the gradient",
            r"a matrix that is singular at every point of the segment",
        ],
        0,
        r"Integrating the derivative of the gradient along the segment produces \(y = \int_0^1 \nabla^2 f(x + \tau s)\, s\, d\tau\). That is an average Hessian times \(s\). The secant equation replaces the average by a single matrix \(B\). The gradient at the old point is not the change. The objective change is a scalar and is not \(y\). The integral does not claim that every Hessian on the segment is singular.",
        fig=SEG,
        alt=A_SEG,
    )
    b.order(
        2,
        r"Put these steps of one secant update in order. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient at the current point and at the point reached by a step \(s\).",
            r"Subtract those two gradients to form the change \(y\).",
            r"Require the new approximation to send \(s\) to \(y\).",
            r"Use that approximation in place of the Hessian in the Newton linear system.",
        ],
        r"The change \(y\) is a difference of gradients, so both gradients come first. The secant equation names \(y\) on the right-hand side, so \(y\) has to exist before the equation can be imposed. The Newton system uses the approximation that satisfies the equation, so it comes last. Solving a system before the gradients are evaluated would use a model from the wrong point.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"Which scalar pairs \((s, y)\) admit a positive definite approximation \(B\) with \(B s = y\)?",
        [
            r"\(s = 2,\ y = 6\)",
            r"\(s = 2,\ y = -6\)",
            r"\(s = -1,\ y = -2\)",
            r"\(s = 0,\ y = 1\)",
            r"\(s = -4,\ y = -8\)",
        ],
        [0, 2, 4],
        r"In one variable, \(B s = y\) with \(B > 0\) means \(s \ne 0\) and \(y/s > 0\)."
        "\n"
        r"• \(6/2 = 3 > 0\)."
        "\n"
        r"• \(-6/2 = -3 < 0\), so the only solution is negative."
        "\n"
        r"• \((-2)/(-1) = 2 > 0\)."
        "\n"
        r"• \(B \cdot 0 = 1\) has no solution."
        "\n"
        r"• \((-8)/(-4) = 2 > 0\)."
        "\n"
        r"The same sign test is \(y s > 0\). A negative product cannot be \(s B s\) for a positive \(B\).",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.sym(
        2,
        r"For a nonzero scalar step \(s\) and a gradient change \(y\), the secant value \(B\) equals",
        "y/s",
        {"y": (-4, 4), "s": (1, 3)},
        r"The equation \(B s = y\) has one unknown. Dividing by \(s\) gives \(B = y/s\). Both declared names appear. The reciprocal \(s/y\) is the matching inverse approximation, not \(B\). The product \(y s\) is the curvature product, not the secant value. The sum \(y + s\) does not solve \(B s = y\).",
        alternates=["y*(1/s)", "(y)/s"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note builds a Hessian approximation for \(s = (1,\ 0)\) and \(y = (2,\ 0)\). Exactly one step is a false claim.",
        [
            r"The secant equation asks for \(B s = y\).",
            r"The first column of \(B\) must be \((2,\ 0)\).",
            r"This one equation does not constrain the second column of \(B\).",
            r"Therefore \(B\) equals \(\begin{pmatrix} 2 & 0 \\ 0 & 2 \end{pmatrix}\) and no other matrix.",
        ],
        3,
        r"The equation \(B s = y\) with \(s = (1,\ 0)\) reads off the first column, which must be \(y = (2,\ 0)\). The second column is multiplied by the zero component of \(s\), so it is free. The diagonal matrix with \(2\)s on the diagonal is one solution, and so is every matrix whose first column is \((2,\ 0)\), including one whose second column is \((5,\ 7)\). One secant equation is \(n\) conditions on an \(n \times n\) matrix.",
        [
            r"One secant equation fixes only the action of \(B\) on \(s\). The second column can still change.",
            r"The first column is not \((2,\ 0)\).",
            r"The secant equation does not ask for \(B s = y\).",
        ],
        0,
        fig=MAT,
        alt=A_MAT,
    )
    b.num(
        3,
        r"Let \(s = (2,\ 0)\) and \(y = (6,\ 0)\). What is the curvature \((y^T s) / (s^T s)\)?",
        3,
        "1",
        r"The products are \(y^T s = 12\) and \(s^T s = 4\), so the ratio is \(3\). That is the value a scalar secant approximation would take, and it is also \(s^T B s / s^T s\) for any \(B\) with \(B s = y\). Reporting \(12\) skips the division. Reporting \(4\) is \(s^T s\). Reporting \(2\) is the first entry of \(s\).",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        3,
        r"On a quadratic whose Hessian \(H\) is constant, the secant equation is satisfied by",
        [
            r"the true Hessian, for every step \(s\)",
            r"only the identity",
            r"no matrix, because a constant Hessian has \(y = 0\)",
            r"a matrix that ignores \(y\)",
        ],
        0,
        r"A constant Hessian gives \(y = H s\) for every step, by the fundamental theorem or by direct expansion. So \(H\) itself solves \(B s = y\). The identity solves it only when \(H s = s\). The gradient change is \(H s\), which is zero only when \(s\) is in the null space. An approximation that ignores \(y\) cannot enforce the equation.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        4,
        r"Among updates that enforce the secant equation and stay symmetric, the one that preserves positive definiteness when \(y^T s > 0\) is",
        [
            r"the BFGS update",
            r"a replacement of the approximation by a skew-symmetric matrix",
            r"a rule that sets \(y\) to zero after the step",
            r"a projection that forces \(y^T s = 0\)",
        ],
        0,
        r"BFGS is a symmetric rank-two update. It satisfies \(B_+ s = y\), and if the previous matrix is positive definite and \(y^T s > 0\), the new matrix is positive definite. A skew-symmetric matrix has \(s^T B s = 0\), so it cannot represent a positive curvature product. Setting \(y\) to zero destroys the secant equation unless \(s\) is zero. Forcing \(y^T s = 0\) is the case positive definiteness cannot satisfy.",
        fig=MAT,
        alt=A_MAT,
        preview=P_BFGS,
    )
    b.num(
        4,
        r"A scalar approximation currently equals \(4\). The new step is \(s = 1\) and the gradient change is \(y = 2\). What is the secant residual \(y - B s\)?",
        -2,
        "1",
        r"The current approximation predicts \(B s = 4\). The observed change is \(2\), so the residual is \(2 - 4 = -2\). An update that enforces the secant equation has to cancel this residual. Reporting \(2\) is \(y\). Reporting \(4\) is the old prediction. Reporting \(6\) adds them.",
        fig=COL,
        alt=A_COL,
        preview=P_BFGS,
    )
    b.mc(
        4,
        r"If \(y^T s \le 0\), which conclusion follows?",
        [
            r"No positive definite matrix satisfies the secant equation \(B s = y\).",
            r"Every positive definite matrix satisfies \(B s = y\).",
            r"The step \(s\) must be zero.",
            r"The gradient change \(y\) is the zero vector whenever \(s\) is not zero.",
        ],
        0,
        r"If \(B\) is positive definite and \(s \ne 0\), then \(s^T B s > 0\). The secant equation would make that product equal \(s^T y\). A nonpositive \(s^T y\) is therefore impossible. It does not follow that every positive definite matrix works: the equation is a particular action on \(s\). Nor does it follow that \(s\) or \(y\) vanishes. The pair \(s = 1\), \(y = -1\) has a negative product and neither vector is zero.",
        fig=ZIG,
        alt=A_ZIG,
        preview=P_BFGS,
    )
    b.save()


def bank_bfgs():
    b = Bank("bfgs-update")
    b.mc(
        1,
        r"The inverse BFGS update produces a matrix \(W_+\) that satisfies",
        [
            r"\(W_+ y = s\), the secant equation written for an inverse approximation",
            r"\(W_+ = 0\)",
            r"\(W_+ s = 0\) for every step",
            r"\(y^T s = 0\)",
        ],
        0,
        r"If \(B\) approximates the Hessian and \(B s = y\), an inverse approximation should send \(y\) back to \(s\). The BFGS formula is built so that this holds. The zero matrix sends \(y\) to zero, not to \(s\). Sending every step \(s\) to zero is the opposite equation. The formula divides by \(y^T s\), so it needs that product to be nonzero, and the positive-definite case needs it positive.",
        fig=MAT,
        alt=A_MAT,
    )
    b.num(
        1,
        r"Start from the identity. Take \(s = (1,\ 0)\) and \(y = (2,\ 0)\). What is the \((1,1)\) entry of the inverse BFGS update?",
        0.5,
        "1",
        r"Here \(y^T s = 2\) and \(\rho = 1/2\). The matrix \(I - \rho s y^T\) equals \(\begin{pmatrix} 0 & 0 \\ 0 & 1 \end{pmatrix}\). Adding \(\rho s s^T = \begin{pmatrix} 1/2 & 0 \\ 0 & 0 \end{pmatrix}\) produces \(\begin{pmatrix} 1/2 & 0 \\ 0 & 1 \end{pmatrix}\). The \((1,1)\) entry is \(1/2\). The secant check: this matrix times \(y\) equals \(s\). Reporting \(2\) is \(y^T s\). Reporting \(1\) is the untouched \((2,2)\) entry. Reporting \(-1/2\) flips the sign of the rank-one term.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        1,
        r"If the current inverse approximation is positive definite, the BFGS update stays positive definite when",
        [
            r"\(y^T s > 0\)",
            r"\(y^T s = 0\)",
            r"\(y^T s < 0\)",
            r"\(s = 0\)",
        ],
        0,
        r"The update divides by \(y^T s\). When that product is positive and the old approximation is positive definite, the new one is positive definite. A zero product makes the formula undefined. A negative product can introduce a negative eigenvalue. A zero step has \(y^T s = 0\) as well, so there is nothing to update from.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.order(
        2,
        r"Put the steps of one BFGS iteration in order. Each step uses the result of the step before it.",
        [
            r"Apply the current inverse approximation to the negative gradient to get a direction.",
            r"Accept a step length along that direction that satisfies the Wolfe conditions.",
            r"Form the displacement \(s\) and the gradient change \(y\) from that accepted step.",
            r"Set \(\rho\) to the reciprocal of \(y^T s\).",
            r"Replace the inverse approximation by the BFGS formula that uses \(\rho\), \(s\), \(y\), and the previous approximation.",
        ],
        r"The line search needs a direction, and the direction is the inverse approximation times the negative gradient. The displacement and the gradient change are measured on the step that was accepted, so they come after the line search. The reciprocal \(\rho\) divides by \(y^T s\), which uses the pair just formed. The formula names \(\rho\), \(s\), and \(y\), so it comes last. Forming \(y\) before the step is taken would compare gradients at the wrong points.",
        fig=SEG,
        alt=A_SEG,
    )
    b.sym(
        2,
        r"In one variable the inverse BFGS update depends only on the step \(s\) and the gradient change \(y\). The new inverse approximation equals",
        "s/y",
        {"s": (0.5, 2), "y": (1, 4)},
        r"The secant equation for an inverse approximation says the new value times \(y\) equals \(s\). There is only one such number, \(s/y\). The old approximation cancels: the factor in front of it is \(1 - s y / (y s) = 0\). Both declared names appear. The ratio \(y/s\) is the Hessian approximation, not its inverse. The product \(s y\) is not dimensionless in the same way and does not send \(y\) to \(s\). The sum \(s + y\) fails the secant equation whenever \(y \ne 1\).",
        alternates=["s*(1/y)", "(s)/y"],
        fig=COL,
        alt=A_COL,
    )
    b.multi(
        2,
        r"The current inverse approximation is positive definite. Which pairs have \(y^T s > 0\), so the BFGS update is defined and stays positive definite?",
        [
            r"\(s = (1,\ 0),\ y = (2,\ 0)\)",
            r"\(s = (1,\ 0),\ y = (-1,\ 0)\)",
            r"\(s = (1,\ 1),\ y = (1,\ 2)\)",
            r"\(s = (1,\ 0),\ y = (0,\ 1)\)",
            r"\(s = (2, -1),\ y = (0, -2)\)",
        ],
        [0, 2, 4],
        r"The test is the sign of the inner product. The formula is undefined at zero and can lose positive definiteness when the product is negative."
        "\n"
        r"• \((1)(2) + (0)(0) = 2 > 0\)."
        "\n"
        r"• \((1)(-1) = -1 < 0\)."
        "\n"
        r"• \((1)(1) + (1)(2) = 3 > 0\)."
        "\n"
        r"• \((1)(0) + (0)(1) = 0\), so \(\rho\) is undefined."
        "\n"
        r"• \((2)(0) + (-1)(-2) = 2 > 0\).",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.find_error(
        3,
        r"A note runs inverse BFGS from the identity with \(s = (1,\ 0)\) and \(y = (-1,\ 0)\). Exactly one step is a false claim.",
        [
            r"The product \(y^T s\) equals \(-1\).",
            r"The update's \((1,1)\) entry equals \(-1\).",
            r"That diagonal result has a negative eigenvalue.",
            r"The updated matrix is positive definite for every \(y\) and \(s\).",
        ],
        3,
        r"The product is \(( -1)(1) = -1\). With \(\rho = -1\), the rank-one term \(\rho s s^T\) contributes \(-1\) in the \((1,1)\) entry, and the conjugate term contributes nothing there, so the entry is \(-1\). The matrix is \(\begin{pmatrix} -1 & 0 \\ 0 & 1 \end{pmatrix}\), whose eigenvalues are \(-1\) and \(1\). Positive definiteness needs every eigenvalue positive, and the BFGS argument requires \(y^T s > 0\). This pair fails that hypothesis, so the formula does not preserve positive definiteness.",
        [
            r"Positive definiteness of the update needs \(y^T s > 0\). Here the product is \(-1\), and the \((1,1)\) entry is negative.",
            r"The product \(y^T s\) is not \(-1\).",
            r"The \((1,1)\) entry of the update is not \(-1\).",
        ],
        0,
        fig=ZIG,
        alt=A_ZIG,
    )
    b.num(
        3,
        r"Start from the identity. Take \(s = (1,\ 0)\) and \(y = (4,\ 0)\). What is the \((1,1)\) entry of the inverse BFGS update?",
        0.25,
        "1",
        r"Here \(y^T s = 4\) and \(\rho = 1/4\). Then \(\rho s s^T\) has \((1,1)\) entry \(1/4\), and \(I - \rho s y^T\) has a zero in that entry. The updated \((1,1)\) entry is \(1/4\). The secant check: \((1/4) \cdot 4 = 1\), which is the first component of \(s\). Reporting \(4\) is \(y^T s\). Reporting \(1\) would be the entry from a pair with \(y = s\). Reporting \(1/2\) is the entry for \(y = (2,\ 0)\), a different gradient change.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        3,
        r"Locally, successive error ratios of BFGS tend to \(0\). That rate is",
        [
            r"superlinear",
            r"a failure to converge",
            r"the same squared-error bound that Newton's method has, with a universal constant",
            r"sublinear, because the ratios go to \(0\)",
        ],
        0,
        r"Superlinear convergence means the error goes to zero and the ratio of successive errors goes to zero. That is the local claim for BFGS. It is faster than a linear rate, whose ratio tends to a positive constant, and it is weaker than a quadratic bound, which Newton's method has under a Lipschitz Hessian. Tendencies of the ratio toward zero are not divergence. Sublinear convergence is the opposite pattern: the error goes to zero while the successive ratio tends to \(1\).",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        4,
        r"A different Hessian-free method builds conjugate directions from gradients and finishes a positive definite quadratic in at most \(n\) steps. That method is",
        [
            r"the conjugate gradient method",
            r"a BFGS update that stores a dense inverse approximation on every quadratic",
            r"a Newton step with the exact Hessian",
            r"a line search with no direction",
        ],
        0,
        r"Conjugate gradients generate the next direction from the latest gradient and the previous direction. On a positive definite quadratic with exact line searches it reaches the minimizer in at most \(n\) steps, and it does not store an \(n \times n\) inverse Hessian. BFGS does store that approximation. A Newton step with the exact Hessian is not Hessian-free. A line search needs a direction.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_CG,
    )
    b.num(
        4,
        r"An inverse approximation is diagonal with entries \(1/2\) and \(1\), and the gradient is \((2,\ 0)\). The search direction is minus that approximation times the gradient. What is the first component of the direction?",
        -1,
        "1",
        r"The first component of the approximation times the gradient is \((1/2) \cdot 2 = 1\). The search direction flips the sign, so the first component is \(-1\). The second component is \(0\). Reporting \(1\) forgets the minus sign in front of the approximation. Reporting \(-2\) multiplies by the gradient and skips the \(1/2\). Reporting \(1/2\) is the diagonal entry, not the direction.",
        fig=ARR,
        alt=A_ARR,
        preview=P_SCALED,
    )
    b.mc(
        4,
        r"A positive definite inverse approximation \(W\) makes \(d = -W \nabla f\) a descent direction. Using such a \(W\) as the metric of a projected step is the idea of",
        [
            r"a scaled projected step",
            r"a simplex ratio test with no metric",
            r"a power iteration on a skew-symmetric matrix",
            r"a line search that ignores the direction",
        ],
        0,
        r"The direction \(-W g\) has directional derivative \(-g^T W g\), which is negative when \(W\) is positive definite and \(g \ne 0\). A projected method can take that step in the \(W\)-metric and then project. BFGS is one way to keep a positive definite \(W\). A simplex ratio test uses the signs of tableau entries. A skew-symmetric matrix does not give a positive \(g^T W g\). A line search does not replace the metric.",
        fig=HALF,
        alt=A_HALF,
        preview=P_SCALED,
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


def expl_newton():
    save_explainer(
        "newton-method-optimization",
        "Newton's method for minimization",
        _sec(
            r"""Newton's method for minimization does not walk a fixed distance against the gradient. At the current point it replaces the objective by the quadratic Taylor model, using the value, the gradient, and the Hessian, and it steps to a stationary point of that model. Setting the model's gradient to zero is a linear equation. The Hessian times the step equals the negative gradient. The point moves by the step, and the model is rebuilt.

On a quadratic with an invertible Hessian, the model is the objective, so one step reaches the unique stationary point from every start. When that Hessian is positive definite, the stationary point is the minimizer, and the step is a descent direction whenever the gradient is not zero. The directional derivative along the step is the negative of a squared length built from the gradient and the inverse Hessian. When the Hessian is negative definite, the same algebra lands on a maximizer. A singular Hessian does not determine one step.

An invertible affine change of coordinates transforms Newton iterates by that same change. The chain rule transforms the model, and the stationary point transforms with the variables. Steepest descent does not have this property. It treats the Euclidean length of the gradient as special, so a stretch of one coordinate changes which direction it calls steepest.""",
            r"""The Newton equation is
\[
\nabla^2 f(x)\, d = -\nabla f(x).
\]
If the Hessian is positive definite and the gradient is not zero, the directional derivative \(d^T \nabla f(x)\) is negative.""",
            r"""Take \(f(u) = \tfrac{5}{2} u^2 - 15 u\) at \(u = 0\). The derivative is \(5u - 15\), so it equals \(-15\). The second derivative is \(5\). The Newton equation \(5 d = 15\) gives the step \(3\).

The latch step is 3. The updated point is \(3\), and the derivative there is \(0\). The objective was quadratic, so the model was exact and the iteration is finished. A negative second derivative would have produced a step as well, and that step would have aimed at a maximizer of the model rather than a minimizer.""",
            r"""Dropping the minus sign solves the Hessian times the step equals the gradient. On a positive definite model that walks uphill. A second slip is to treat a negative second derivative as a reason to declare the point a minimizer. The algebra still produces a step, and the stationary point of a negative definite model is a maximum. A third is to divide by a zero second derivative. The model is then a straight line with no stationary point.""",
            r"""Close to a minimizer with a positive definite Lipschitz Hessian, the error after a step is bounded by a constant times the square of the previous error. That local rate says nothing about a far start, where the model can increase the objective or point toward a saddle. A line search, or a diagonal shift that restores positive curvature, forces a descent step. When the Hessian is too expensive to form, a matrix built from gradient changes can take its place in the same linear equation.""",
            LEV,
            A_LEV,
        ),
    )


def expl_local():
    save_explainer(
        "newton-local-quadratic-convergence",
        "Local quadratic convergence of Newton",
        _sec(
            r"""Quadratic convergence is a statement about the error, not just about the objective getting smaller. If \(e\) is the error before a step and \(e_+\) is the error after it, the quadratic pattern says that \(\lVert e_+\rVert\) is at most a constant times \(\lVert e\rVert^2\).

Newton earns the squared bound near a minimizer when two hypotheses hold. The Hessian at the minimizer is positive definite, so the point is a strict local minimizer and the Newton step exists. The Hessian is Lipschitz nearby, so its change along a segment is controlled by the length of the segment. Stationarity makes the gradient at the minimizer zero. The gradient at a nearby point is then the integral of the Hessian along the segment. Subtracting that integral from the Hessian at the current point isolates a remainder. The Newton formula multiplies the remainder by the inverse Hessian. The Lipschitz condition turns the remainder into a constant times the squared error.

The constant depends on the inverse Hessian and on the Lipschitz constant. The inequality forces the error to shrink once the start is close enough that the constant times the current error is smaller than \(1\). That neighborhood is the basin. Outside it, the same algebra does not promise that the next point is closer.""",
            r"""With a Hessian Lipschitz constant \(L\) and with \(H\) the Hessian at the current point,
\[
\lVert e_+\rVert \le \frac{L}{2}\, \lVert H^{-1}\rVert\, \lVert e\rVert^2,
\]
once the current point is close enough that \(H\) stays invertible.""",
            r"""Take a derivative \(3t^2 - 12t - 36\), so the second derivative is \(6t - 12\). The root of interest is \(t = 6\), where the second derivative equals \(24\) and is positive. Start at \(t = 9\). The derivative there is \(99\) and the second derivative is \(42\). The step is \(-99/42\), and the next point is \(93/14\).

The spool error is 0.642857. The error before the step was \(3\), and the new error is \(9/14\). A start where the second derivative vanishes would have had no step at all, so it is not a point inside this argument.""",
            r"""Reading a linear rate as quadratic because the error got smaller misses the squared factor. Any convergent sequence gets smaller. A second slip is to apply the bound at a singular Hessian. The factor in front of the squared error contains the inverse Hessian, which does not exist there. A third is to expect the bound from every starting point. The proof produces a neighborhood, not the whole space. A fourth is to forget that a negative definite Hessian can attract Newton just as fast, toward a maximizer. Positive definiteness is what makes the limit a minimizer.""",
            r"""The squared local rate is special to Newton near a nondegenerate minimizer. A conjugate-direction method on a positive definite quadratic finishes in finitely many steps instead, one per dimension in the worst case. Momentum and extrapolated gradient steps keep a global bound on the function gap for smooth convex problems and do not need the start to lie in a Newton basin. That gap bound is slower than a local squared-error guarantee, and those methods ask for less curvature information.""",
            DECAY,
            A_DECAY,
        ),
    )


def expl_global():
    save_explainer(
        "newton-globalization",
        "Globalizing Newton's method",
        _sec(
            r"""A plain Newton step is a descent direction when the Hessian is positive definite and the gradient is not zero. The directional derivative is then the negative of a squared length. When the Hessian has a negative eigenvalue, that guarantee disappears. The Newton equation can point uphill, and shortening the length does not help: every positive step along an uphill direction increases the model.

A diagonal shift repairs the direction. Add a positive multiple of the identity, large enough that every eigenvalue of the shifted Hessian is positive. The shifted equation still has the negative gradient on the right-hand side. Because the matrix is now positive definite, the solution is a descent direction. A shift that only reaches a zero eigenvalue leaves the matrix singular, so it does not determine one step. The shift has to clear zero, not merely touch it.

The direction is then handed to a line search. Damped Newton tries a length and accepts it only when the objective falls at least as much as a fraction of the linear prediction. If the trial fails, the length is multiplied by a fixed factor between \(0\) and \(1\) and tried again. A descent direction guarantees that a short enough trial passes.""",
            r"""With a shift \(\mu > 0\),
\[
(\nabla^2 f(x) + \mu I)\, d = -\nabla f(x).
\]
Armijo then asks for \(f(x + t d) \le f(x) + c\, t\, \nabla f(x)^T d\) with \(c \in (0, 1)\), and a rejected \(t\) is replaced by \(\beta t\).""",
            r"""Suppose the derivative is \(-15\) and the second derivative is \(-1\). The unshifted equation sends the step uphill. Add a shift of \(4\). The shifted curvature is \(3\), and the equation \(3 d = 15\) gives the step \(5\).

The cleat shift step is 5. The directional derivative is the derivative times this step, which is negative, so the shifted direction descends. A shift of \(1\) would have left the curvature at zero and would not have produced a step. Backtracking, if a unit length fails the decrease test, shortens that same direction. It does not flip the sign.""",
            r"""Putting the shift on the right-hand side, instead of on the Hessian, changes the gradient rather than the curvature. A second slip is to accept a zero eigenvalue as positive definite. Singular still means the linear system does not have one solution. A third is to shorten an uphill Newton step and hope the decrease test will pass. On an uphill direction the linear prediction itself increases, and a fraction of that prediction is not a decrease. A fourth is to flip the direction after a rejected trial. The rejection says the length was too long, not that the direction was wrong.""",
            r"""The shifted direction is a scaled gradient step, with the scaling given by the inverse of the shifted Hessian. A projected method can take that step in the same metric and then project onto a convex set. Farther on, an interior iteration linearizes a perturbed complementarity system and keeps the Newton steps inside the positive region. Both are ways to use a tangent step without trusting an unmodified Hessian everywhere.""",
            SLOW,
            A_SLOW,
        ),
    )


def expl_wolfe():
    save_explainer(
        "wolfe-conditions",
        "Wolfe line-search conditions",
        _sec(
            r"""A line search has to do more than make the objective smaller. Sufficient decrease, the Armijo inequality, says the drop is at least a fraction of the drop the linear model predicted. The fraction \(c_1\) sits strictly between \(0\) and \(1\). That test can accept a step whose slope is still steeply negative, or even a step whose slope has become more negative. Later updates that divide by the curvature of the gradient need something stronger.

The curvature test looks at the directional derivative at the new point. It asks that new derivative to be at least \(c_2\) times the old one, with \(c_1 < c_2 < 1\). The old directional derivative of a descent direction is negative, so \(c_2\) times it is less negative. The slope along the step has to rise at least that far, and it does not have to reach zero.

Together the two inequalities force a positive curvature product. Let \(s\) be the step and let \(y\) be the change in the gradient. Curvature says the new directional derivative is at least \(c_2\) times the old one. Subtract the old derivative, multiply by the positive length, and the product \(y^T s\) is bounded below by a positive number. The gap \(c_2 < 1\) and the negative old derivative are what make the lower bound positive. Sufficient decrease alone does not.""",
            r"""With \(0 < c_1 < c_2 < 1\),
\[
f(x+td) \le f(x) + c_1 t \nabla f(x)^T d,
\]
\[
\nabla f(x+td)^T d \ge c_2 \nabla f(x)^T d.
\]
Writing \(s = t d\) and \(y\) for the gradient change, these force \(y^T s > 0\) when the old directional derivative is negative.""",
            r"""Take \(f(t) = 4t^2\), so the derivative is \(8t\). Start at \(t = 3\) and step in the direction \(d = -1\) with length \(1\). The old derivative is \(24\). The new point is \(2\), where the derivative is \(16\). The step \(s\) equals \(-1\), and the gradient change \(y\) equals \(16 - 24\).

The hawser product is 8. The product \(y s\) is positive. A decrease test would also have passed, because the value falls from \(36\) to \(16\). The product, not the decrease, is the quantity a curvature-sensitive update needs. On a function that bends the other way, a decrease test can pass while this product is negative.""",
            r"""Checking curvature with the opposite inequality accepts steps whose slope became steeper. That is the case the test is written to reject. A second slip is to set \(c_2\) below \(c_1\), or to set \(c_2\) at least \(1\). The positive-product argument uses the strict gap between them. A third is to treat a negative curvature product as harmless because the objective fell. An update that divides by that product, or that expects a positive definite Hessian approximation, cannot use the step. A fourth is to require the new directional derivative to be zero. That is an exact line search. Wolfe is weaker, and the weaker test is enough for the sign of \(y^T s\).""",
            r"""The positive product is the hypothesis a BFGS update uses to stay positive definite. A line search that stops at sufficient decrease can return a step whose product is negative, and the update built from that step can lose positive definiteness. Asking for both Wolfe tests before the update is what keeps the curvature hypothesis available.""",
            PAIR,
            A_PAIR,
        ),
    )


def expl_secant():
    save_explainer(
        "quasi-newton-secant",
        "Quasi-Newton methods and the secant equation",
        _sec(
            r"""A quasi-Newton method keeps the Newton linear equation and refuses to form the Hessian. It stores a matrix that is meant to act like the Hessian, or like the inverse Hessian, and it updates that matrix from the step just taken and from the change in the gradient.

The reason a gradient change can stand in for a Hessian is the fundamental theorem along a segment. The difference of gradients between the ends of the step equals the integral of the Hessian along the step, applied to the step. That integral is an average Hessian. The secant equation asks the stored matrix to match the average on this one direction: the matrix times the step equals the gradient change. On a quadratic the average is the true Hessian, so the true Hessian satisfies the equation for every step.

One vector equation does not determine a square matrix. It fixes the action on the step and leaves the action on a complementary subspace free. Many matrices satisfy the same secant equation. Positive definiteness adds another demand. If the matrix is positive definite and the step is not zero, the step and the gradient change must have a positive inner product. A nonpositive product rules out every positive definite solution. The line search that produced the step is what one later update will trust to keep that product positive.""",
            r"""With \(s = x_+ - x\) and \(y = \nabla f(x_+) - \nabla f(x)\),
\[
y = \int_0^1 \nabla^2 f(x + \tau s)\, s\, d\tau, \qquad B s = y.
\]
A positive definite \(B\) can exist only if \(y^T s > 0\). In one variable, \(B = y/s\).""",
            r"""Take a scalar step \(s = 5\) and a gradient change \(y = 20\). The secant equation says \(5 B = 20\).

The reed curvature is 4. The value \(4\) is what a constant second derivative would have been, had the derivative risen by \(20\) over a step of \(5\). A previous guess of some other number leaves a residual, the observed change minus that guess times the step. The next update is built to cancel a residual of this kind. The reciprocal \(5/20\) would be an inverse approximation, not the Hessian approximation.""",
            r"""Swapping the equation to \(B y = s\) stores an inverse approximation and then uses it as if it were a Hessian. A second slip is to treat one secant equation as a full description of the matrix. The second column, in a plane, is invisible to a step that has a zero in that component. A third is to accept a negative curvature product and still expect a positive definite solution. The quadratic form of a positive definite matrix cannot be negative. A fourth is to forget that a constant true Hessian already satisfies the equation. Replacing it is worthwhile when the Hessian is unavailable, not because the equation rejects it.""",
            r"""BFGS picks one symmetric solution of the secant equation and keeps it positive definite when the curvature product is positive. The inverse form of that update is what an iteration applies to the gradient. The secant equation is the constraint. The update formula is one way to meet it.""",
            SEG,
            A_SEG,
        ),
    )


def expl_bfgs():
    save_explainer(
        "bfgs-update",
        "BFGS update",
        _sec(
            r"""BFGS stores an approximation of the inverse Hessian and updates it after every accepted step. The search direction is that approximation times the negative gradient. A line search along the direction produces a displacement \(s\) and a gradient change \(y\). The update is built from the current approximation, from \(s\), from \(y\), and from the reciprocal of the curvature product \(y^T s\).

The formula is a rank-two correction. It is arranged so that the new approximation sends \(y\) to \(s\). That is the secant equation for an inverse: if a Hessian approximation would send \(s\) to \(y\), the inverse approximation sends \(y\) back to \(s\). In one variable there is only one such number, the step divided by the gradient change, and the old approximation cancels.

Positive definiteness carries forward when two things are true. The old approximation is positive definite, and the curvature product is positive. Then the new approximation is positive definite, the next direction is a descent direction, and the formula is defined. A zero product makes the reciprocal undefined. A negative product can put a negative eigenvalue into the update. The Wolfe curvature test is what makes the product positive before the update is formed. Locally, once the approximation is faithful enough, successive error ratios tend to zero. That is superlinear convergence. It is faster than a linear rate and weaker than the squared-error bound of Newton.""",
            r"""With \(\rho = 1/(y^T s)\) and with \(W\) the current inverse approximation,
\[
W_+ = (I - \rho s y^T)\, W\, (I - \rho y s^T) + \rho s s^T.
\]
The new matrix satisfies \(W_+ y = s\). In one variable, \(W_+ = s/y\).""",
            r"""Start from the identity, with \(s = (3,\ 0)\) and \(y = (1,\ 0)\). The curvature product is \(3\), so the reciprocal is \(1/3\). The correction that subtracts a multiple of \(s y^T\) clears the first diagonal entry, and the term built from \(s s^T\) writes \(3\) back into that entry.

The anvil entry is 3. The \((2,2)\) entry stays \(1\). The new matrix times \(y\) equals \(s\), so the inverse secant equation holds. A pair with a negative curvature product would have written a negative number in that entry, and the matrix would not have stayed positive definite.""",
            r"""Using the update when the curvature product is negative, and still calling the result positive definite, contradicts the eigenvalue that the formula can introduce. A second slip is to divide by the product when it is zero. The reciprocal is undefined, so there is no update. A third is to store \(y/s\) and apply it as an inverse. That ratio approximates the Hessian. The inverse approximation is \(s/y\). A fourth is to describe the local BFGS rate as the squared-error bound. Successive ratios tending to zero are superlinear. The squared bound is the Newton claim.""",
            r"""A conjugate-gradient iteration also avoids forming the Hessian. It builds the next direction from the gradient and a previous direction, and on a positive definite quadratic it finishes in at most as many steps as the dimension. A scaled projected step can use a positive definite matrix such as this inverse approximation as its metric. BFGS is one way to keep that matrix current. The other methods spend the same descent idea with a different memory.""",
            MAT,
            A_MAT,
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
    "newton-method-optimization": "The latch step is 3",
    "newton-local-quadratic-convergence": "The spool error is 0.642857",
    "newton-globalization": "The cleat shift step is 5",
    "wolfe-conditions": "The hawser product is 8",
    "quasi-newton-secant": "The reed curvature is 4",
    "bfgs-update": "The anvil entry is 3",
}

LEAKS = {
    "newton-method-optimization": ["-0.5", "-24", "t^3 - 6t"],
    "newton-local-quadratic-convergence": ["0.25", "0.666667", "2/3"],
    "newton-globalization": ["-1.5", "-8"],
    "wolfe-conditions": ["0.2"],
    "quasi-newton-secant": ["y - B s", "-2"],
    "bfgs-update": ["0.5", "0.25", "-1"],
}


def main():
    _balance_mc()
    bank_newton()
    bank_local()
    bank_global()
    bank_wolfe()
    bank_secant()
    bank_bfgs()
    expl_newton()
    expl_local()
    expl_global()
    expl_wolfe()
    expl_secant()
    expl_bfgs()
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
        "course",
    )
    bad = False
    totals = Counter()
    for sid, phrase in MARKERS.items():
        exp = json.load(open(os.path.join(root, "skilltree", "explainers", sid + ".json"), encoding="utf-8"))
        n = doc_words(exp["sections"])
        bank = json.load(open(os.path.join(root, "skilltree", "bank", sid + ".json"), encoding="utf-8"))
        blob = json.dumps(exp) + json.dumps(bank)
        explainer_blob = json.dumps(exp)
        hits = [w for w in banned if w in blob.lower()]
        leaks = [w for w in LEAKS[sid] if w in explainer_blob]
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
        if leaks:
            print("  explainer leaks", leaks)
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
