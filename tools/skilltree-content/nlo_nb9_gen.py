#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB9 banks and explainers.

Skills: gauss-newton-method, levenberg-marquardt, incremental-gradient-methods,
kalman-recursive-least-squares, extended-kalman-filter, newton-root-finding.

Closed-form answers live here. skilltree/verify_nlo_nb9.py recomputes the
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

P_LM = ["levenberg-marquardt"]
P_RLS = ["kalman-recursive-least-squares"]
P_EKF = ["extended-kalman-filter"]
P_NOPT = ["newton-method-optimization"]
P_IP = ["primal-dual-interior-point"]
P_GLOB = ["newton-globalization"]
P_ROOT = ["newton-root-finding"]


def bank_gn():
    b = Bank("gauss-newton-method")
    b.mc(
        1,
        r"One Gauss-Newton step on a residual \(r(x)\) does which of the following?",
        [
            r"Replace \(r\) by the linear model \(r + J_r d\) and solve that linear least-squares problem for \(d\).",
            r"Set \(r(x) = 0\) by inspection and stop, without using a Jacobian.",
            r"Replace \(r\) by the Hessian of \(\tfrac12\lVert r\rVert^2\) and stop.",
            r"Step in a direction orthogonal to every row of the Jacobian.",
        ],
        0,
        r"The linear model of the residual is \(r(x) + J_r(x)\, d\). Gauss-Newton chooses \(d\) to minimize the norm of that model, which is a linear least-squares problem with normal equations \(J_r^T J_r\, d = -J_r^T r\). Setting the nonlinear residual to zero is the goal of the iteration, not one step. The Hessian of the sum of squares is a different matrix, and it is not what this step solves. A direction orthogonal to every Jacobian row has a zero first-order change in the residual, so it is not the least-squares step.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"The residual is \(r(t) = (t - 1,\ 2t - 4)\). At \(t = 0\), what is the Gauss-Newton step \(d\) in \(t\)?",
        1.8,
        "1",
        r"At \(t = 0\) the residual is \((-1, -4)\) and the Jacobian column is \((1, 2)\). Then \(J^T J = 1 + 4 = 5\) and \(J^T r = -1 - 8 = -9\), so \(5d = 9\) and \(d = 9/5 = 1.8\). The residual is affine, so this one step is the exact least-squares fit. Reporting \(9\) skips the division by the Gram entry. Reporting \(-1.8\) flips the normal equation. Reporting \(5\) is \(J^T J\) itself, not the step.",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        1,
        r"The Gauss-Newton matrix \(J_r^T J_r\) equals the true Hessian of \(f = \tfrac12\lVert r\rVert^2\) when",
        [
            r"every residual component is affine, or the residual vector is zero",
            r"the Jacobian is singular",
            r"the step length is shorter than one",
            r"the residual is nonlinear and nonzero",
        ],
        0,
        r"The true Hessian is \(J_r^T J_r + \sum_i r_i \nabla^2 r_i\). Each second-derivative term vanishes when that component is affine, and the whole sum vanishes when \(r = 0\). A singular Jacobian does not cancel those terms. A short step is a line-search choice and does not change the Hessian. A nonlinear nonzero residual is exactly the case where the extra term can be nonzero, so the two matrices differ.",
        fig=MAT,
        alt=A_MAT,
    )
    b.order(
        2,
        r"Put these steps of one Gauss-Newton iteration in order. Each step uses the result of the step before it.",
        [
            r"Evaluate the residual \(r\) and its Jacobian \(J_r\) at the current point.",
            r"Form the normal equations \(J_r^T J_r\, d = -J_r^T r\) of the linearized residual.",
            r"Solve those equations for the step \(d\).",
            r"Replace the current point by the point plus \(d\).",
        ],
        r"The residual and the Jacobian have to be known before the normal equations can be written. The equations have to be written before they can be solved. The point moves only after the step is in hand. Solving a model built at the new point would be the next iteration, not this one.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which statements about a Gauss-Newton step are true?",
        [
            r"The step minimizes the norm of the linearized residual.",
            r"If \(J_r\) has full column rank and \(J_r^T r \ne 0\), the step is a descent direction for \(\tfrac12\lVert r\rVert^2\).",
            r"\(J_r^T J_r\) is positive semidefinite for every real Jacobian.",
            r"The linear model keeps the second derivatives of the residual components.",
            r"One step reaches a root of every nonlinear residual.",
        ],
        [0, 1, 2],
        r"The normal equations are the stationarity condition for the linear least-squares model, so the step minimizes that model."
        "\n"
        r"• Full column rank makes \(J_r^T J_r\) positive definite. The directional derivative of \(\tfrac12\lVert r\rVert^2\) along the step is then \(-(J_r^T r)^T (J_r^T J_r)^{-1} (J_r^T r)\), which is negative when the gradient is not zero."
        "\n"
        r"• For every real matrix, \(v^T J_r^T J_r v = \lVert J_r v\rVert^2 \ge 0\), so the Gram matrix is positive semidefinite even when it is singular."
        "\n"
        r"• Second derivatives of the components are exactly the terms Gauss-Newton drops. At \(u = 2\) for \(r(u) = (u^2 - 10,\ 2u - 4)\), that dropped term equals \(-12\), and the true Hessian is \(8\) rather than \(J^T J = 20\)."
        "\n"
        r"• The same point moves by \(1.2\), and the nonlinear residual there is \((0.24,\ 2.4)\), not zero.",
        fig=ELL,
        alt=A_ELL,
    )
    b.sym(
        2,
        r"A scalar parameter has residual entries \(a\) and \(b\), with Jacobian entries \(p\) and \(q\). The Gauss-Newton step equals",
        "-(p*a+q*b)/(p*p+q*q)",
        {"a": (-2, 2), "b": (-2, 2), "p": (1, 3), "q": (1, 3)},
        r"The Gram entry is \(p^2 + q^2\) and the right-hand side of the normal equation is \(-(pa + qb)\), so the step is \(-(pa + qb)/(p^2 + q^2)\). Every declared name appears: \(a\) and \(b\) are the residual entries, and \(p\) and \(q\) are the Jacobian entries. Dropping the minus sign climbs the residual model. Using \(p^2 + q^2\) in the numerator swaps the Gram matrix with the gradient. Replacing the denominator by \(p + q\) adds the rows instead of squaring them.",
        alternates=["-(a*p+b*q)/(p**2+q**2)", "(-p*a-q*b)/(p*p+q*q)"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note computes a Gauss-Newton step for \(r(x) = (x^2 - 5,\ x - 1)\) at \(x = 2\). Exactly one step is a false claim.",
        [
            r"The residual at \(2\) is \((4 - 5,\ 2 - 1) = (-1,\ 1)\).",
            r"The derivative of \(x^2 - 5\) is \(2x\), so the Jacobian at \(2\) is \((4,\ 1)\).",
            r"The derivative of \(x^2 - 5\) may be replaced by \(x\), so the Jacobian at \(2\) is \((2,\ 1)\).",
            r"With the Jacobian \((4,\ 1)\), one has \(J^T J = 17\) and \(J^T r = -3\), so the step is \(3/17\).",
        ],
        2,
        r"The residual \((4 - 5,\ 2 - 1) = (-1,\ 1)\) is correct. Differentiating \(x^2\) produces \(2x\), so the Jacobian at \(2\) is \((4,\ 1)\), and \(4^2 + 1^2 = 17\), \(4\cdot(-1) + 1 = -3\), and the step is \(3/17\). The false step replaces \(2x\) by \(x\). That is a different linear model, and the normal equations built from \((2,\ 1)\) are not the Gauss-Newton step.",
        [
            r"The derivative of \(x^2\) is \(2x\), so the Jacobian at \(2\) is \((4,\ 1)\), not \((2,\ 1)\).",
            r"The residual at \(2\) is not \((-1,\ 1)\).",
            r"For the Jacobian \((4,\ 1)\), the product \(J^T J\) is not \(17\).",
        ],
        0,
        fig=MAT,
        alt=A_MAT,
    )
    b.num(
        3,
        r"The residual is \(r(u) = (u^2 - 10,\ 2u - 4)\). At \(u = 2\), what is the Gauss-Newton step \(d\)?",
        1.2,
        "1",
        r"The residual is \((-6,\ 0)\) and the Jacobian column is \((4,\ 2)\). Then \(J^T J = 16 + 4 = 20\) and \(J^T r = -24\), so \(d = 24/20 = 1.2\). Reporting \(24\) skips the division. Reporting \(-1.2\) flips the sign of the normal equation. Reporting \(20\) is the Gram entry. The updated parameter would be \(3.2\), which is the point plus the step, not the step itself.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        3,
        r"At \(u = 2\) for \(r(u) = (u^2 - 10,\ 2u - 4)\), the true Hessian of \(\tfrac12\lVert r\rVert^2\) and the Gauss-Newton matrix differ because",
        [
            r"the first residual is \(-6\) and its second derivative is \(2\), which contributes \(-12\)",
            r"the Jacobian column \((4,\ 2)\) is orthogonal to the residual",
            r"\(J^T J\) is indefinite",
            r"the second residual component is zero, which removes \(J^T J\)",
        ],
        0,
        r"The extra Hessian term is \(\sum_i r_i\) times the second derivative of component \(i\). Here that is \((-6)\cdot 2 + 0 = -12\). Added to \(J^T J = 20\), the true Hessian is \(8\). The Jacobian is not orthogonal to the residual: their dot product is \(-24\). A Gram matrix is positive semidefinite, and here it equals \(20\), so it is not indefinite. A zero residual component drops that component's second-derivative term; it does not drop \(J^T J\).",
        fig=LEV,
        alt=A_LEV,
    )
    b.mc(
        4,
        r"When \(J_r^T J_r\) is nearly singular, the plain Gauss-Newton step can be very long. The method that adds a positive multiple of the identity before solving is",
        [
            r"a damped Gauss-Newton step",
            r"a simplex pivot on a linear program",
            r"an exact line search that ignores the Jacobian",
            r"a spectral decomposition of the residual",
        ],
        0,
        r"Adding \(\mu I\) with \(\mu > 0\) is the damped step. The shift makes the matrix positive definite, and a large \(\mu\) shortens the step toward steepest descent. A simplex pivot is a basis change for a linear program. An exact line search still needs a direction, and dropping the Jacobian removes the least-squares model. A spectral decomposition reads eigenvalues; it does not build the step.",
        fig=ELL,
        alt=A_ELL,
        preview=P_LM,
    )
    b.num(
        4,
        r"For \(r(u) = (u^2 - 10,\ 2u - 4)\) at \(u = 2\), the Gauss-Newton step is \(1.2\) and \(J^T r = -24\). What is the directional derivative of \(f = \tfrac12\lVert r\rVert^2\) along that step?",
        -28.8,
        "1",
        r"The gradient of \(f\) is \(J^T r = -24\). Along \(d = 1.2\) the directional derivative is \(-24 \cdot 1.2 = -28.8\). The negative sign is what makes the step a descent direction. Reporting \(28.8\) drops that sign. Reporting \(-24\) is the gradient, not its product with the step. Reporting \(1.2\) is the step length.",
        fig=FALL,
        alt=A_FALL,
        preview=P_LM,
    )
    b.mc(
        4,
        r"On a residual that is already affine, one Gauss-Newton step is exact. Applying that step to the old quadratic plus one new linear block is the optimization view of",
        [
            r"the measurement update of a linear recursive least-squares fit",
            r"a phase-one simplex iteration",
            r"an Armijo test with no residual",
            r"a power iteration for the largest eigenvalue",
        ],
        0,
        r"A linear residual makes one Gauss-Newton step exact for the cost it is given. Recursive least squares gives it the old quadratic plus the new block, not the new block by itself, and that step is the Kalman measurement update. A phase-one iteration introduces artificial variables for a linear program. Armijo is a sufficient-decrease test on a step that has already been chosen. Power iteration multiplies by a matrix to find an eigenvector.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_RLS,
    )
    b.save()


def bank_lm():
    b = Bank("levenberg-marquardt")
    b.mc(
        1,
        r"With damping \(\mu > 0\), a Levenberg-Marquardt step solves",
        [
            r"\((J_r^T J_r + \mu I)\, d = -J_r^T r\)",
            r"\(J_r^T J_r\, d = -J_r^T r\), and then discards \(d\) if \(\mu\) is positive",
            r"\(\mu\, d = J_r^T r\)",
            r"\(J_r\, d = 0\) with no use of the residual",
        ],
        0,
        r"The damped normal equations add \(\mu I\) to the Gauss-Newton matrix and keep the same right-hand side \(-J_r^T r\). Dropping the step whenever \(\mu\) is positive would never move. The equation \(\mu d = J_r^T r\) has the wrong sign and omits \(J_r^T J_r\). A step in the null space of \(J_r\) does not reduce the linear model.",
        fig=MAT,
        alt=A_MAT,
    )
    b.num(
        1,
        r"A scalar parameter has \(J^T J = 2\) and \(J^T r = 4\). With damping \(\mu = 2\), what is the Levenberg-Marquardt step \(d\)?",
        -1,
        "1",
        r"The damped equation is \((2 + 2)\, d = -4\), so \(4d = -4\) and \(d = -1\). The undamped Gauss-Newton step would be \(-4/2 = -2\), twice as long. Reporting \(1\) drops the minus sign on the right-hand side. Reporting \(-2\) forgets to add \(\mu\). Reporting \(-4\) stops at the right-hand side.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        1,
        r"As the damping \(\mu\) grows, with \(J^T r \ne 0\), the Levenberg-Marquardt step",
        [
            r"shrinks like \(1/\mu\) and lines up with the negative gradient",
            r"grows without bound",
            r"becomes orthogonal to the gradient",
            r"stops depending on \(\mu\) once \(\mu > 1\)",
        ],
        0,
        r"For large \(\mu\), \((J^T J + \mu I)^{-1}\) is about \(I/\mu\), so \(d \approx -(J^T r)/\mu\). That is a short steepest-descent step. The factor \(1/\mu\) gets smaller, so the step does not grow. The direction stays opposite the gradient rather than perpendicular to it. The formula keeps \(\mu\) in the denominator for every positive value, including values above one.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.order(
        2,
        r"Put an accepted damping update in order. Each step uses the result of the step before it.",
        [
            r"Solve \((J_r^T J_r + \mu I)\, d = -J_r^T r\) at the current damping.",
            r"Compare the true decrease in \(\tfrac12\lVert r\rVert^2\) with the decrease predicted by the linear model.",
            r"Accept the point plus \(d\) because that true decrease is large enough.",
            r"Decrease \(\mu\) for the next iteration after the step has been accepted.",
        ],
        r"The trial step has to exist before its decrease can be compared with the model. Acceptance uses that comparison: the step is kept only when the true decrease is a large enough fraction of the prediction. The damping falls only after that acceptance. A rejected step is the other branch of the same test, and it raises \(\mu\) instead of lowering it. The two branches are alternatives, not successive steps.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which statements about the damping \(\mu\) hold?",
        [
            r"Raising \(\mu\) shortens the step when \(J^T r \ne 0\).",
            r"As \(\mu\) tends to \(0\), the step tends to the Gauss-Newton step when \(J^T J\) is invertible.",
            r"For large \(\mu\) the direction approaches the negative gradient.",
            r"Any \(\mu > 0\) makes \(J^T J + \mu I\) singular.",
            r"\(J^T J + \mu I\) is positive definite for every \(\mu > 0\).",
        ],
        [0, 1, 2, 4],
        r"With \(J^T J = 2\) and \(J^T r = 4\), the step is \(-4/(2 + \mu)\). Its length is \(1\) at \(\mu = 2\) and \(0.5\) at \(\mu = 6\), so a larger damping is a shorter step."
        "\n"
        r"• At \(\mu = 0\) the same formula is \(-4/2 = -2\), the Gauss-Newton step."
        "\n"
        r"• The step is negative and the gradient \(4\) is positive, so the direction is the negative gradient for every \(\mu\), and the large-\(\mu\) reading is the same direction with a vanishing length."
        "\n"
        r"• The scalar \(2 + \mu\) is at least \(2\) when \(\mu > 0\), so the shifted matrix is not singular. In several variables, \(v^T J^T J v + \mu\lVert v\rVert^2 \ge \mu\lVert v\rVert^2 > 0\) for \(v \ne 0\)."
        "\n"
        r"• A positive damping therefore cannot make the shifted matrix singular.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.sym(
        2,
        r"A scalar parameter has residual entries \(a\) and \(b\), Jacobian entries \(p\) and \(q\), and damping \(\mu\). The damped step equals",
        "-(p*a+q*b)/(p*p+q*q+mu)",
        {"a": (-2, 2), "b": (-2, 2), "p": (1, 3), "q": (1, 3), "mu": (0.5, 3)},
        r"The damped Gram entry is \(p^2 + q^2 + \mu\), and the right-hand side is still \(-(pa + qb)\). Every name appears: the residual entries, the Jacobian entries, and the damping. Dropping \(\mu\) is the undamped Gauss-Newton step. Putting \(\mu\) in the numerator treats the damping as a residual. A minus sign on \(\mu\) in the denominator can make the matrix indefinite, which is not this update.",
        alternates=["-(a*p+b*q)/(p**2+q**2+mu)", "(-p*a-q*b)/(p*p+q*q+mu)"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note damps the scalar problem with \(J^T J = 2\) and \(J^T r = 4\), whose objective \(\tfrac12\lVert r\rVert^2\) equals \(5\) at the current point. Exactly one step is a false claim.",
        [
            r"The undamped gradient term is \(J^T r = 4\), and \(J^T J = 2\).",
            r"With \(\mu = 2\) the damped equation gives the step \(d = -1\).",
            r"The objective falls from \(5\) to \(2\), so the step is accepted and the next damping should be larger than \(2\).",
            r"The accepted point is the current point plus \(d\).",
        ],
        2,
        r"The gradient term and the Gram entry match the problem. With \(\mu = 2\) the equation \((2 + 2)d = -4\) gives \(d = -1\). For the residual \((u + 3,\ u + 1)\) at \(u = 0\), the objective is \(5\), and at \(u = -1\) it is \(2\), so the true objective did fall and the step is accepted. An accepted step is a reason to decrease the damping, not to increase it. The accepted point is the old point plus the step.",
        [
            r"An accepted step decreases the damping. Increasing it is the response to a rejected step.",
            r"The objective does not fall from \(5\) to \(2\).",
            r"With \(\mu = 2\) the step is not \(-1\).",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"A scalar parameter has \(J^T J = 2\) and \(J^T r = 4\). With damping \(\mu = 14\), what is the step \(d\)?",
        -0.25,
        "1",
        r"The equation is \((2 + 14)\, d = -4\), so \(16d = -4\) and \(d = -1/4 = -0.25\). Compared with the step \(-1\) at \(\mu = 2\), the larger damping is shorter and still negative. Reporting \(0.25\) drops the sign. Reporting \(-4/14\) forgets to add \(J^T J\). Reporting \(-2\) is the undamped step.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        3,
        r"If \(J_r\) does not have full column rank, a positive damping still produces a step because",
        [
            r"\(J_r^T J_r + \mu I\) is positive definite, so it is invertible, and the step is a descent direction",
            r"the damping sets every residual to zero",
            r"the damping makes the Jacobian square",
            r"a singular Gram matrix is left unchanged",
        ],
        0,
        r"For \(\mu > 0\) and \(v \ne 0\), \(v^T(J_r^T J_r + \mu I)v \ge \mu\lVert v\rVert^2 > 0\). The shifted matrix is positive definite even when \(J_r^T J_r\) is only semidefinite, so the step exists. The directional derivative equals \(-(J_r^T r)^T (J_r^T J_r + \mu I)^{-1}(J_r^T r)\), which is negative when the gradient is not zero. Damping does not zero the residual, and it does not change the shape of \(J_r\). Leaving a singular matrix unchanged is the undamped method, which is the case this shift avoids.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        4,
        r"A diagonal shift added to a Hessian, so that a Newton step for minimization becomes a descent direction, is the same idea as",
        [
            r"the damping term \(\mu I\) in a Levenberg-Marquardt step",
            r"a simplex ratio test",
            r"dropping the gradient and keeping only the residual",
            r"replacing the step by an eigenvalue",
        ],
        0,
        r"Both moves add a positive multiple of the identity to a matrix that may fail to be positive definite. The damped Gauss-Newton matrix and a shifted Hessian then define a descent direction. A ratio test chooses a leaving variable in the simplex method. Dropping the gradient removes the right-hand side of the step equation. An eigenvalue describes a stretch; it is not the shift itself. The damping here is \(\mu\), not an eigenvalue.",
        fig=MAT,
        alt=A_MAT,
        preview=P_GLOB,
    )
    b.num(
        4,
        r"With \(J^T J = 2\), \(J^T r = 4\), and \(\mu = 2\), the step is \(-1\). What is the directional derivative of \(f = \tfrac12\lVert r\rVert^2\) along that step?",
        -4,
        "1",
        r"The gradient is \(4\) and the step is \(-1\), so the directional derivative is \(4 \cdot (-1) = -4\). The same value is \(-16 / (2 + 2)\). Reporting \(4\) drops the step. Reporting \(-1\) is the step, not the derivative. Reporting \(-2\) is the undamped Gauss-Newton step.",
        fig=PAIR,
        alt=A_PAIR,
        preview=P_GLOB,
    )
    b.mc(
        4,
        r"If a damped step barely decreases the true residual beside the linear prediction, the damping update",
        [
            r"rejects the step and increases \(\mu\)",
            r"accepts the step and decreases \(\mu\)",
            r"sets \(\mu\) to zero and keeps the step",
            r"replaces \(\mu\) by the residual norm and skips the comparison",
        ],
        0,
        r"A small ratio of true decrease to predicted decrease says the linear model was optimistic. The trial is rejected and \(\mu\) grows, which shortens the next trial. Accepting and decreasing \(\mu\) is the response when the model agrees with the true decrease. Setting \(\mu\) to zero returns to plain Gauss-Newton on a step the model just failed to justify. The residual norm can be part of the comparison, but it does not replace the increase in damping.",
        fig=RISE,
        alt=A_RISE,
        preview=P_GLOB,
    )
    b.save()


def bank_inc():
    b = Bank("incremental-gradient-methods")
    b.mc(
        1,
        r"An incremental gradient pass on \(f = f_1 + \cdots + f_m\)",
        [
            r"steps on one block gradient at a time and evaluates the next block at the updated point",
            r"sums every block gradient at the original point, then takes one step",
            r"replaces every block by the same gradient and stops",
            r"sets each block gradient to zero before any step",
        ],
        0,
        r"The pass updates the parameter after each block, so later blocks see the new point. Summing every gradient at the original point is the batch step. Reusing one block's gradient for the others ignores the data in those blocks. Setting gradients to zero is the stationarity condition for a minimizer, not the pass.",
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        1,
        r"Let \(f_1(u) = \tfrac12(u - 2)^2\) and \(f_2(u) = \tfrac12(u - 6)^2\). Start at \(u = 0\) and take step length \(1\), with \(f_1\) first. Where does one incremental pass end?",
        6,
        "1",
        r"The block gradients are \(u - 2\) and \(u - 6\). The first update is \(0 - (0 - 2) = 2\). The second, at the new point, is \(2 - (2 - 6) = 6\). The minimizer of the sum is \(4\), so the pass did not stop at a stationary point of \(f_1 + f_2\). Reporting \(2\) stops after the first block. Reporting \(4\) is the minimizer of the sum. Reporting \(8\) is the batch step of length \(1\) from \(0\), which uses both gradients at the original point.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        1,
        r"After the pass of length \(1\) that ends at \(6\), the next pass through the same two quadratics",
        [
            r"returns to \(6\), so the pass endpoint has settled where the full gradient is not zero",
            r"reaches the minimizer \(4\) and stays there",
            r"matches a batch step of length \(1\)",
            r"is undefined because the step length equals one",
        ],
        0,
        r"From \(6\) the first block sends the point to \(6 - (6 - 2) = 2\), and the second sends it back to \(2 - (2 - 6) = 6\). The full gradient at \(6\) is \(4\), not zero. The minimizer of the sum is \(4\), which this constant step never uses as an endpoint. A batch step of length \(1\) from \(0\) ends at \(8\), a different point. Step length \(1\) is a legal step; the second derivative of each block is \(1\), so this step lands on that block's minimizer.",
        fig=ZIG,
        alt=A_ZIG,
    )
    b.order(
        2,
        r"Put one incremental pass in order. Each step uses the result of the step before it.",
        [
            r"Start the pass at the current parameter.",
            r"Subtract the step length times the first block's gradient, evaluated at that point.",
            r"Evaluate the next block's gradient at the updated point, and step again.",
            r"After the last block, keep the updated parameter. It is not the sum of every block gradient at the original point.",
        ],
        r"The pass needs a starting parameter before any block can be evaluated. The first step produces the point at which the next gradient is computed. Later blocks repeat that pattern. The comparison with a batch step is available only after the pass has a final point. Summing every gradient first would be the batch method.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"For \(f_1(u) = \tfrac12(u - 2)^2\) and \(f_2(u) = \tfrac12(u - 6)^2\), which statements about step lengths hold?",
        [
            r"Step length \(1\) makes every later pass end at \(6\), where the full gradient equals \(4\), not zero.",
            r"The repeated-pass endpoint for a constant step \(t \in (0, 2)\) is \(2(4 - t)/(2 - t)\), which tends to the minimizer \(4\) as \(t\) tends to \(0\).",
            r"Steps that tend to \(0\) and whose lengths sum to infinity are the usual requirement for a stationary limit.",
            r"A larger constant step always reaches the minimizer \(4\) in one pass.",
            r"An incremental pass of any positive length matches the batch step of that same length.",
        ],
        [0, 1, 2],
        r"From \(6\), step length \(1\) returns to \(6\), and the full gradient \(2\cdot 6 - 8 = 4\) is not zero."
        "\n"
        r"• A pass of length \(t\) sends \(u\) to \((1 - t)^2 u + t(1 - t)\cdot 2 + t\cdot 6\). The fixed point of that map is \(2(4 - t)/(2 - t)\). At \(t = 1\) it equals \(6\). As \(t\) tends to \(0\) it tends to \(4\)."
        "\n"
        r"• A constant step can sit away from a stationary point. Letting the length tend to zero removes that bias, and an infinite sum of lengths is what still lets the iterates travel. That pair is the usual requirement."
        "\n"
        r"• Step length \(1\) ends at \(6\), not at \(4\). The batch step of length \(1\) from \(0\) ends at \(8\), not at the incremental endpoint \(6\).",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.sym(
        2,
        r"A block gradient equals \(a u + b\). After a step of length \(t\) from the scalar \(u\), the updated value equals",
        "u-t*(a*u+b)",
        {"u": (-2, 4), "t": (0.2, 1.5), "a": (0.5, 2), "b": (-3, 3)},
        r"One block step subtracts \(t\) times the gradient, so the new value is \(u - t(au + b)\). Every name appears: the point, the step length, and the two coefficients of the gradient. Dropping \(t\) subtracts the whole gradient. Using \(u + t(au + b)\) climbs the block. Freezing \(u\) inside the gradient and also adding \(t u\) double-counts the point.",
        alternates=["u*(1-t*a)-t*b", "(1-a*t)*u-b*t"],
        fig=ARR,
        alt=A_ARR,
    )
    b.find_error(
        3,
        r"A note runs the pass of length \(1\) on \(f_1(u) = \tfrac12(u - 2)^2\) and \(f_2(u) = \tfrac12(u - 6)^2\), starting at \(0\), with \(f_1\) first. Exactly one step is a false claim.",
        [
            r"The first block gradient at \(0\) is \(-2\).",
            r"The first update is \(0 - (-2) = 2\).",
            r"The second block gradient is evaluated at the original point \(0\), so it equals \(-6\).",
            r"Evaluated at the updated point \(2\), the second gradient is \(-4\), and the second update is \(2 - (-4) = 6\).",
        ],
        2,
        r"The first gradient \(0 - 2 = -2\) and the first update \(2\) are correct. The second block of an incremental pass is evaluated at \(2\), where the gradient is \(2 - 6 = -4\), and the update is \(6\). Evaluating the second gradient at the original point is the batch construction. That false step is what makes a finite pass differ from a summed gradient.",
        [
            r"The second block is evaluated at the updated point, not at the start of the pass.",
            r"The first gradient at \(0\) is not \(-2\).",
            r"The second gradient at the updated point \(2\) is not \(-4\).",
        ],
        0,
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        3,
        r"On the same two quadratics, start at \(u = 0\) with step length \(1/2\), and take \(f_1\) first. Where does one incremental pass end?",
        3.5,
        "1",
        r"The first update is \(0 - \tfrac12(0 - 2) = 1\). The second is \(1 - \tfrac12(1 - 6) = 1 + 2.5 = 3.5\). The batch step of this same length ends at \(4\), the minimizer. Reporting \(1\) stops after the first block. Reporting \(4\) is that batch result. Reporting \(6\) is the pass of length \(1\).",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        3,
        r"A constant step and a step that tends to zero differ because",
        [
            r"a constant step can settle away from a stationary point, while a vanishing step removes that bias",
            r"a vanishing step is the same update as a batch gradient of fixed length",
            r"a constant step always finishes a smooth sum in one pass",
            r"the order of the blocks never changes a finite step",
        ],
        0,
        r"On the two quadratics, step length \(1\) settles at the pass endpoint \(6\), where the full gradient is \(4\). The fixed endpoint \(2(4 - t)/(2 - t)\) tends to \(4\) only as \(t\) tends to \(0\). A vanishing step is not a batch step of fixed length. A constant step of length \(1\) does not finish at the minimizer. Swapping the two blocks at a finite step changes the intermediate point, so the order matters.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        4,
        r"Recursive least squares, unlike an incremental pass that minimizes each block alone, minimizes",
        [
            r"the old quadratic plus the new linear block, in one Gauss-Newton step",
            r"only the newest block, forgetting every earlier block",
            r"the full gradient with a constant step and no least-squares solve",
            r"a spectral decomposition of the data matrix",
        ],
        0,
        r"The recursive step keeps every earlier block as a quadratic and appends the new linear residual. One Gauss-Newton step finishes that stacked cost. Minimizing only the newest block is a different pass: on \(\tfrac12(u-2)^2\) and \(\tfrac12(u-6)^2\), length \(1\) ends at \(6\), while the joint minimizer is \(4\). A constant-length gradient step is the incremental method itself. A spectral decomposition reads singular values.",
        fig=COL,
        alt=A_COL,
        preview=P_RLS,
    )
    b.num(
        4,
        r"On \(f_1(u) = \tfrac12(u - 2)^2\) and \(f_2(u) = \tfrac12(u - 6)^2\), the batch step of length \(1/2\) from \(u = 0\) uses the full gradient. Where does it land?",
        4,
        "1",
        r"The full gradient is \(2u - 8\), so at \(0\) it equals \(-8\). The second derivative of the sum is \(2\), and length \(1/2\) is the exact Newton step: \(0 - \tfrac12(-8) = 4\). That point is the minimizer. The incremental pass of the same length ends at \(3.5\), not here. Reporting \(-8\) is the gradient. Reporting \(8\) is the batch step of length \(1\).",
        fig=LEV,
        alt=A_LEV,
        preview=P_RLS,
    )
    b.mc(
        4,
        r"If a block residual is nonlinear, the incremental Gauss-Newton step has to rebuild the Jacobian at the updated estimate. Rebuilding it on every new block is what turns recursive least squares into",
        [
            r"an extended update that relinearizes the measurement",
            r"a batch gradient with a fixed Jacobian from the first block",
            r"a simplex basis change",
            r"a step that ignores the new block",
        ],
        0,
        r"A nonlinear measurement has a Jacobian that depends on the estimate. The next block is linearized at the latest estimate, which is the extended update. Keeping the first Jacobian forever is a frozen linear model. A simplex basis change is a pivot in a linear program. Ignoring the new block does not use the measurement that the update exists to include.",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_EKF,
    )
    b.save()


def bank_rls():
    b = Bank("kalman-recursive-least-squares")
    b.mc(
        1,
        r"The optimization reading of one new linear measurement is",
        [
            r"one Gauss-Newton step on the least-squares cost of every block so far, which is the Kalman measurement update",
            r"a fresh derivation of the state predict step \(x \mapsto A x\)",
            r"a replacement for the Kalman gain formula",
            r"a batch gradient on a nonlinear residual",
        ],
        0,
        r"Earlier blocks contribute a quadratic cost summarized by the current estimate and its variance. One new linear residual keeps the whole cost quadratic, so one Gauss-Newton step is exact. The step is a gain times the innovation, and that gain is the measurement update already used by the Kalman filter. The predict step, the state matrix, and the process noise stay with that filter. This skill does not replace the gain formula. A nonlinear residual would not be finished by one linear step.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"A scalar estimate is \(2\) with variance \(4\). A new measurement is \(6\), with row \(1\) and variance \(4\). What is the gain?",
        0.5,
        "1",
        r"The gain is \(P c / (c^2 P + R) = 4\cdot 1 / (1\cdot 4 + 4) = 4/8 = 0.5\). This is the scalar Kalman measurement gain. Reporting \(4\) is the prior variance. Reporting \(1\) would be the gain only if the measurement variance were zero. Reporting \(0.25\) divides by \(P + R\) and then divides by \(P\) again.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        1,
        r"With equal prior and measurement variances and a measurement row of \(1\), the updated estimate is",
        [
            r"the midpoint of the prior estimate and the new measurement",
            r"the prior estimate, ignoring the measurement",
            r"twice the measurement minus the prior",
            r"the measurement divided by the prior variance",
        ],
        0,
        r"The gain is \(P/(P + R)\). Equal positive variances make the gain \(1/2\), so the update is halfway from the prior estimate to the measurement. For the numbers \(2\) and \(6\), that midpoint is \(4\). Ignoring the measurement would need a zero gain. Twice the measurement minus the prior is an extrapolation past the measurement. Dividing the measurement by the variance is not the update.",
        fig=SEG,
        alt=A_SEG,
    )
    b.order(
        2,
        r"Put the least-squares derivation of one measurement update in order. Each step uses the result of the step before it.",
        [
            r"Keep the previous estimate and its variance as the quadratic cost of every earlier linear block.",
            r"Append the new linear measurement and its variance as one more residual block.",
            r"Take one Gauss-Newton step on that stacked cost. The step is exact because the cost is quadratic.",
            r"Read the step as the Kalman measurement gain times the innovation. Leave the predict step with the Kalman filter.",
        ],
        r"The earlier cost has to be in hand before a new block can be appended. The stacked cost has to exist before its Gauss-Newton step can be formed. The gain reading is that step written as a correction. The predict step is not part of this measurement block, so it is not re-derived here.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"For a scalar measurement with row \(1\) and positive variances, which statements hold?",
        [
            r"The gain is strictly between \(0\) and \(1\).",
            r"A smaller measurement variance increases the gain.",
            r"The updated variance is larger than the prior variance.",
            r"The gain and the variance update are the Kalman measurement update.",
            r"This derivation replaces the filter's predict step.",
        ],
        [0, 1, 3],
        r"With row \(1\), the gain is \(P/(P + R)\). Positive \(P\) and \(R\) put it strictly between \(0\) and \(1\). For \(P = 4\) and \(R = 4\) the gain is \(1/2\)."
        "\n"
        r"• Replacing \(R = 4\) by \(R = 1\) raises the gain from \(1/2\) to \(4/5\), so the update moves closer to the measurement."
        "\n"
        r"• The variance update is \((1 - K)P\). With \(K = 1/2\) and \(P = 4\) it equals \(2\), which is smaller than the prior, not larger."
        "\n"
        r"• Those two formulas are the measurement update of the Kalman filter. The predict step is a different part of that filter and is not derived from this least-squares block.",
        fig=BALL,
        alt=A_BALL,
    )
    b.sym(
        2,
        r"A scalar measurement has row \(c\), prior variance \(p\), and measurement variance \(r\). The gain equals",
        "p*c/(c*c*p+r)",
        {"p": (0.5, 4), "c": (0.5, 2), "r": (0.5, 4)},
        r"The innovation variance is \(c^2 p + r\), and the gain is \(p c\) divided by that variance. Every name appears. Swapping \(p\) and \(r\) treats the measurement as the prior. Dropping \(c\) from the numerator is the gain only when the row equals \(1\). Using \(c p + r\) in the denominator adds the row instead of squaring it.",
        alternates=["(p*c)/(p*c*c+r)", "c*p/(p*c**2+r)"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note updates the scalar estimate \(2\), variance \(4\), with measurement \(6\), row \(1\), and variance \(4\). Exactly one step is a false claim.",
        [
            r"The innovation is \(6 - 2 = 4\).",
            r"The gain is \(4/(4 + 4) = 1/2\).",
            r"The updated estimate is \(2 - \tfrac12\cdot 4 = 0\).",
            r"The updated variance is \((1 - \tfrac12)\cdot 4 = 2\).",
        ],
        2,
        r"The innovation \(4\) and the gain \(1/2\) match \(P/(P + R)\). The variance update \((1 - K)P = 2\) is the Kalman measurement update of the variance. The estimate adds the gain times the innovation: \(2 + \tfrac12\cdot 4 = 4\). Subtracting it walks away from the measurement. The measurement is \(6\), and a gain of \(1/2\) should land at the midpoint \(4\).",
        [
            r"The correction is added to the prior. The innovation is the measurement minus the prediction, and the gain times that innovation points toward the measurement.",
            r"The innovation is not \(4\).",
            r"The gain is not \(1/2\).",
        ],
        0,
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        3,
        r"After the update with prior variance \(4\) and gain \(1/2\), what is the updated variance?",
        2,
        "1",
        r"The variance update is \((1 - K c)P\). With \(c = 1\), \(K = 1/2\), and \(P = 4\), this is \(2\). The information form gives the same value: \(1/4 + 1/4 = 1/2\), so the variance is \(2\). Reporting \(4\) keeps the prior. Reporting \(8\) adds the variances. Reporting \(1/2\) is the gain.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        3,
        r"This skill points at the Kalman filter for the gain formula because",
        [
            r"the least-squares step is that filter's measurement update, and the filter already states the recursion",
            r"the least-squares step uses a different gain",
            r"a covariance cannot come from a least-squares cost",
            r"the predict step is the only part derived here",
        ],
        0,
        r"The normal equation of the stacked linear cost produces \(L = P c / (c^2 P + R)\) and the variance \((1 - L c)P\). Those are the measurement update. The derivation here shows why that update minimizes the growing least-squares cost. It does not invent a second gain, and the quadratic cost is exactly where the variance comes from. The predict step is not this block.",
        fig=LEV,
        alt=A_LEV,
    )
    b.mc(
        4,
        r"If the new measurement is a nonlinear function of the estimate, the same update with the Jacobian rebuilt at the current estimate is",
        [
            r"an extended measurement update",
            r"still an exact minimization of the nonlinear cost",
            r"a predict step with process noise",
            r"a batch gradient that waits for every future measurement",
        ],
        0,
        r"A nonlinear measurement is replaced by its linear model at the current estimate, and the linear update runs with that Jacobian in place of the measurement row. That is one Gauss-Newton step on the latest block, not an exact minimization of the nonlinear cost. The predict step propagates the estimate between measurements. Waiting for future measurements would be a batch fit, not this one-block update.",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_EKF,
    )
    b.num(
        4,
        r"The estimate is now \(4\) with variance \(2\). A further measurement is \(7\), with row \(1\) and variance \(2\). What is the updated estimate?",
        5.5,
        "1",
        r"The gain is \(2/(2 + 2) = 1/2\). The innovation is \(7 - 4 = 3\). The update is \(4 + \tfrac12\cdot 3 = 5.5\). The variance would fall to \(1\), which is not what was asked. Reporting \(3\) is the innovation. Reporting \(7\) keeps only the new measurement. Reporting \(4\) ignores it.",
        fig=RISE,
        alt=A_RISE,
        preview=P_EKF,
    )
    b.mc(
        4,
        r"A nonlinear measurement uses the value of the measurement map in the innovation, not only the Jacobian. Forgetting the map and writing the innovation as the reading minus the Jacobian times the estimate is a mistake because",
        [
            r"the linear model is the map at the estimate plus the Jacobian times the displacement, so the innovation subtracts the map",
            r"the Jacobian already equals the measurement map",
            r"the prior variance is the innovation",
            r"a row of \(1\) makes the map and the Jacobian the same for every nonlinear measurement",
        ],
        0,
        r"The first-order model is \(h(\hat x) + J_h(\hat x)\,(x - \hat x)\). The innovation is the reading minus \(h(\hat x)\). Subtracting \(J_h(\hat x)\,\hat x\) instead is correct only when \(h\) is linear through the origin. The Jacobian is a derivative, not the map. The prior variance scales the gain; it is not the innovation. A row of \(1\) is the derivative of \(h(u) = u\), which is linear, not a stand-in for every nonlinear map.",
        fig=COL,
        alt=A_COL,
        preview=P_EKF,
    )
    b.save()


def bank_ekf():
    b = Bank("extended-kalman-filter")
    b.mc(
        1,
        r"One extended measurement update does which of the following?",
        [
            r"Linearize the measurement at the current estimate, then apply one linear gain update with that Jacobian",
            r"Use the measurement map with no derivative",
            r"Keep the Jacobian from the first estimate for every later block",
            r"Replace the innovation by the prior variance",
        ],
        0,
        r"The nonlinear map \(h\) is replaced by \(h(\hat x) + J_h(\hat x)\,(x - \hat x)\). The innovation is the reading minus \(h(\hat x)\), and the gain uses \(J_h(\hat x)\) where a linear update would use the measurement row. A map with no derivative has no linear model to update. A frozen Jacobian ignores the move of the estimate. The prior variance enters the gain, not the innovation.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"A position estimate is \(3\), and the sensor reads the square of position. What is the measurement Jacobian at that estimate?",
        6,
        "1",
        r"The map is \(u^2\), so its derivative is \(2u\). At \(u = 3\) the Jacobian is \(6\). Reporting \(3\) uses the estimate in place of the derivative. Reporting \(9\) is the map \(3^2\), which belongs in the innovation, not in the gain as the Jacobian. Reporting \(2\) is the factor in \(2u\) with the estimate left out.",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        1,
        r"The innovation of a sensor that reads \(u^2\), at an estimate of \(3\), with a reading of \(15\), is",
        [
            r"\(15 - 9 = 6\)",
            r"\(15 - 6 = 9\), using the Jacobian in place of the map",
            r"\(15 - 3 = 12\), subtracting the estimate itself",
            r"the Jacobian \(6\) itself, leaving the reading unused",
        ],
        0,
        r"The innovation subtracts the nonlinear map at the estimate: \(3^2 = 9\), so \(15 - 9 = 6\). Subtracting the Jacobian \(6\) treats the derivative as if it were the predicted reading. Subtracting the estimate treats the sensor as the identity. The Jacobian enters the gain and the variance, not as a substitute for the predicted reading.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.order(
        2,
        r"Put one extended measurement update in order. Each step uses the result of the step before it.",
        [
            r"Evaluate the nonlinear measurement and its Jacobian at the current estimate.",
            r"Form the innovation as the reading minus that measurement value.",
            r"Multiply that innovation by the gain built from the same Jacobian and the two variances.",
            r"Add that product to the estimate. The variance update uses this same gain and Jacobian.",
        ],
        r"The map has to be known before the innovation can subtract it. The correction is the gain times that innovation, so the product cannot be formed until the innovation exists. The estimate then moves by that product, and the variance formula uses the gain inside it. The gain by itself does not need the innovation, which is why the later step is the product, not the gain alone. Linearizing again at the corrected point is the next block.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which statements about an extended measurement update hold?",
        [
            r"The innovation is the reading minus the measurement map at the estimate.",
            r"The Jacobian is evaluated at the current estimate.",
            r"If the measurement map is affine, the update matches the linear measurement update.",
            r"One update exactly minimizes the true nonlinear least-squares cost.",
            r"After the estimate moves, the next block needs a new linearization.",
        ],
        [0, 1, 2, 4],
        r"The linear model is the map plus the Jacobian times the displacement, so the innovation subtracts the map, and the Jacobian is taken where the model was built."
        "\n"
        r"• An affine map has a constant Jacobian, and the map minus that Jacobian times the estimate is the linear residual. The update is then the ordinary linear one."
        "\n"
        r"• For the square sensor at estimate \(3\), prior variance \(1\), reading \(15\), and measurement variance \(12\), the update lands at \(3.75\). The derivative of the true nonlinear cost \(\tfrac12(u-3)^2 + \tfrac1{24}(15-u^2)^2\) there is \(21/128\), not zero, so the nonlinear cost is not minimized."
        "\n"
        r"• The Jacobian of \(u^2\) at \(3.75\) is \(7.5\), not the \(6\) used for the step. The next block has to be linearized again.",
        fig=LEV,
        alt=A_LEV,
    )
    b.sym(
        2,
        r"The prior variance is \(p\), the measurement Jacobian is \(j\), and the measurement variance is \(r\). The extended gain equals",
        "p*j/(j*j*p+r)",
        {"p": (0.5, 4), "j": (0.5, 2), "r": (0.5, 4)},
        r"The Jacobian takes the place of the measurement row. The gain is \(p j / (j^2 p + r)\). Every name appears. Using the reading in place of \(j\) would mix the innovation into the gain. Dropping \(j\) from the numerator is the linear gain only for a row equal to \(1\). Adding \(j\) instead of squaring it is the wrong innovation variance.",
        alternates=["(p*j)/(p*j*j+r)", "j*p/(p*j**2+r)"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        r"A note updates a square-of-position sensor at the estimate \(3\), with prior variance \(1\), reading \(15\), and measurement variance \(12\). Exactly one step is a false claim.",
        [
            r"The map at \(3\) is \(9\), so the innovation for the reading \(15\) is \(6\).",
            r"The derivative of \(u^2\) is \(2u\), so the Jacobian at \(3\) is \(6\).",
            r"The gain may be computed with Jacobian \(3\), the estimate itself.",
            r"With Jacobian \(6\), prior variance \(1\), and measurement variance \(12\), the gain is \(6/48 = 1/8\).",
        ],
        2,
        r"The map \(9\) and the innovation \(6\) are correct, and \(2u\) at \(3\) is \(6\). The innovation variance is \(6^2\cdot 1 + 12 = 48\), so the gain is \(6/48 = 1/8\). Using the estimate \(3\) as the Jacobian is the false step. That substitution builds the gain from the wrong linear model.",
        [
            r"The derivative of \(u^2\) is \(2u\), so the Jacobian at \(3\) is \(6\), not \(3\).",
            r"The innovation for the reading \(15\) is not \(6\).",
            r"With Jacobian \(6\) the gain is not \(1/8\).",
        ],
        0,
        fig=COL,
        alt=A_COL,
    )
    b.num(
        3,
        r"Estimate \(3\), prior variance \(1\), square sensor, reading \(15\), measurement variance \(12\). The gain is \(1/8\) and the innovation is \(6\). What is the updated position?",
        3.75,
        "1",
        r"The correction is the gain times the innovation: \(\tfrac18\cdot 6 = 0.75\). Added to the estimate, the position is \(3.75\). Reporting \(0.75\) stops at the correction. Reporting \(6\) is the innovation. Reporting \(15\) keeps the reading as if it were a position. The variance update is \(0.25\), which is a different quantity.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        3,
        r"The variance update \((1 - K J_h)P\) uses the measurement Jacobian. Replacing \(J_h\) by \(1\) is valid when",
        [
            r"the measurement row really is \(1\), as in a linear sensor that reads position itself",
            r"the sensor reads the square of position",
            r"the gain is positive",
            r"the innovation is zero",
        ],
        0,
        r"The factor \(1\) is the derivative of the identity map. A sensor that reads position has that Jacobian, and the linear variance update \((1 - K)P\) is the special case. The square sensor has Jacobian \(2u\), which equals \(1\) only at \(u = 1/2\). A positive gain does not make the Jacobian equal \(1\). A zero innovation leaves the estimate unmoved and does not change which Jacobian the variance formula uses.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        4,
        r"Solving \(F(x) = 0\) by rebuilding a tangent at every new point is the same linearization idea as an extended update. That root iteration is",
        [
            r"Newton's method for a nonlinear equation",
            r"a batch gradient with a constant step",
            r"a simplex pivot",
            r"a predict step that adds process noise",
        ],
        0,
        r"Newton replaces \(F\) by \(F(x) + J_F(x)\, d\) and solves the linear equation for \(d\). An extended update does the same to a measurement map and then blends the result with the prior. A batch gradient sums block gradients at one point. A simplex pivot changes a basis. A predict step propagates a state; it does not solve a tangent equation for a root.",
        fig=FALL,
        alt=A_FALL,
        preview=P_ROOT,
    )
    b.num(
        4,
        r"For the square sensor at estimate \(3\), with prior variance \(1\), gain \(1/8\), and Jacobian \(6\), what is the updated variance?",
        0.25,
        "1",
        r"The variance update is \((1 - K J_h)P = (1 - \tfrac18\cdot 6)\cdot 1 = 1 - 0.75 = 0.25\). Using \((1 - K)P = 7/8\) pretends the Jacobian is \(1\). Reporting \(1\) keeps the prior variance. Reporting \(0.75\) is the amount removed, not the variance that remains.",
        fig=ELL,
        alt=A_ELL,
        preview=P_ROOT,
    )
    b.mc(
        4,
        r"A Newton root iteration and an extended measurement update share which sensitivity?",
        [
            r"A tangent built at a poor point can send the next guess far from a root of the nonlinear map.",
            r"Both methods finish every nonlinear equation in one step.",
            r"Both ignore the derivative.",
            r"Both require the measurement variance to be zero.",
        ],
        0,
        r"The next point is where the tangent hits the target. If the tangent is a poor picture of the map, that hit can sit far from a root. Neither method finishes a general nonlinear equation in one step: the square sensor's update at \(3.75\) is not a root of the nonlinear stationarity condition. Both methods use the derivative. The measurement variance shapes the gain of the filter update; Newton's method for a root has no measurement variance.",
        fig=ZIG,
        alt=A_ZIG,
        preview=P_ROOT,
    )
    b.save()


def bank_newton():
    b = Bank("newton-root-finding")
    b.mc(
        1,
        r"One Newton step for a root of a map \(F\)",
        [
            r"replaces \(F\) by its tangent and solves that linear equation",
            r"steps by a fixed length along \(F\) without a derivative",
            r"squares \(F\) and minimizes the square with no linearization",
            r"declares every start a root",
        ],
        0,
        r"The tangent equation is \(F(x) + J_F(x)\, d = 0\). The next point is \(x + d\), and the tangent is rebuilt there. A fixed step along \(F\) is not the root of the tangent. Minimizing \(\tfrac12\lVert F\rVert^2\) without linearizing is a different algorithm; when \(J_F\) is square and invertible the Gauss-Newton step on that square happens to match this tangent step. A start is a root only when \(F\) is already zero.",
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        1,
        r"Let \(g(t) = t^2 - 2\). Starting at \(t = 2\), what is the next Newton iterate?",
        1.5,
        "1",
        r"Here \(g(2) = 2\) and \(g'(2) = 4\), so the next point is \(2 - 2/4 = 1.5\). Reporting \(2\) stays at the start. Reporting \(0.5\) is the size of the correction, not the new point. Reporting \(-1.5\) flips the sign of a positive start; the negative root is reached from a negative start, not from this one.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"If the derivative at the current point is zero, the Newton update",
        [
            r"is undefined, because the tangent does not meet the axis at one point",
            r"stays at the current point and calls it a root",
            r"steps by the value of the function",
            r"averages the current point with zero",
        ],
        0,
        r"The step divides by the derivative. A zero derivative is a horizontal tangent, and division by zero leaves no step. A horizontal tangent is not evidence that the point is a root unless the function value is also zero. Stepping by the function value ignores the failed division. Averaging with zero is a different recurrence.",
        fig=HALF,
        alt=A_HALF,
    )
    b.order(
        2,
        r"Put one Newton iteration for \(F(x) = 0\) in order. Each step uses the result of the step before it.",
        [
            r"Evaluate \(F\) and its Jacobian \(J_F\) at the current point.",
            r"Solve the tangent equation \(J_F\, d = -F\).",
            r"Replace the point by the point plus \(d\).",
            r"Rebuild \(F\) and \(J_F\) at the new point before the next solve.",
        ],
        r"The tangent is built from the value and the Jacobian, so those come first. The step is the solution of that tangent equation. The point moves only after the step exists. The next iteration needs a new tangent at the new point; reusing the old Jacobian is a frozen linear model.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"Which statements about the starting point of Newton's method hold?",
        [
            r"Two starts can converge to different roots.",
            r"A start where the derivative is zero has no Newton step.",
            r"A start can move to a root that is not the nearest one.",
            r"Every start reaches the nearest root in one step.",
            r"An affine map with a nonzero slope is solved in one step from every start.",
        ],
        [0, 1, 2, 4],
        r"For \(g(t) = t^2 - 2\), the start \(2\) goes toward the positive root and the start \(-4\) goes toward the negative root."
        "\n"
        r"• A zero derivative makes the tangent horizontal, so the step is undefined."
        "\n"
        r"• For \(g(t) = t^3 - t\), the start \(1/2\) has value \(-3/8\) and derivative \(-1/4\), and the next point is \(1/2 - (-3/8)/(-1/4) = -1\). The roots are \(-1\), \(0\), and \(1\). The nearest roots to \(1/2\) are \(0\) and \(1\), each at distance \(1/2\), and the step landed on \(-1\)."
        "\n"
        r"• That same step shows a single iteration need not reach the nearest root."
        "\n"
        r"• For \(g(t) = 2t - 6\) the update is \(t - (2t - 6)/2 = 3\) from every start.",
        fig=ZIG,
        alt=A_ZIG,
    )
    b.sym(
        2,
        r"At the scalar point \(u\) the map equals \(v\) and the derivative equals \(p\). The next Newton iterate equals",
        "u-v/p",
        {"u": (-2, 4), "v": (-3, 3), "p": (1, 4)},
        r"The tangent is \(v + p(t - u) = 0\), so \(t = u - v/p\). Every name appears. Adding \(v/p\) walks the wrong way along the tangent. Using \(u - p/v\) swaps the value and the derivative. Dropping \(u\) returns only the correction.",
        alternates=["(u*p-v)/p", "u+(-v)/p"],
        fig=ARR,
        alt=A_ARR,
    )
    b.find_error(
        3,
        r"A note takes one Newton step on \(g(t) = t^2 - 2\) at \(t = 2\). Exactly one step is a false claim.",
        [
            r"The value \(g(2)\) equals \(2\).",
            r"The derivative of \(t^2 - 2\) is \(2t\), so \(g'(2) = 4\).",
            r"Using the derivative \(2\) in place of \(4\) is valid, and the update is \(2 - 2/2 = 1\).",
            r"The derivative \(4\) produces the update \(2 - 2/4 = 3/2\).",
        ],
        2,
        r"The value \(4 - 2 = 2\) is correct, and the derivative \(2t\) equals \(4\) at \(t = 2\). Dividing by that derivative produces \(2 - 1/2 = 3/2\). The false step replaces \(2t\) by \(2\), which is the derivative of \(t^2\) with the factor \(t\) dropped. The update \(1\) belongs to that wrong derivative.",
        [
            r"The derivative of \(t^2\) is \(2t\), so at \(t = 2\) it equals \(4\), not \(2\).",
            r"The value \(g(2)\) is not \(2\).",
            r"Dividing by the derivative \(4\) does not produce \(3/2\).",
        ],
        0,
        fig=MAT,
        alt=A_MAT,
    )
    b.num(
        3,
        r"Let \(F(x, y) = (x^2 - 2,\ y - 3)\) at \((2,\ 1)\). The Jacobian is diagonal with entries \(4\) and \(1\). What is the first component of the Newton step?",
        -0.5,
        "1",
        r"The value is \((2,\ -2)\). The first tangent equation is \(4\, d_1 = -2\), so \(d_1 = -1/2\). The second equation is \(d_2 = 2\), and the new point is \((1.5,\ 3)\). Reporting \(1.5\) is the new first coordinate, not the step. Reporting \(2\) is the second component of the step. Reporting \(0.5\) drops the sign.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        3,
        r"For a square invertible Jacobian, the Newton step on \(F(x) = 0\) and the Gauss-Newton step on \(\tfrac12\lVert F\rVert^2\)",
        [
            r"are the same step, because \(J^T J\, d = -J^T F\) reduces to \(J\, d = -F\)",
            r"agree only when \(J\) is singular",
            r"differ by the factor \(\lVert F\rVert\) for every invertible \(J\)",
            r"agree only when \(F\) is orthogonal to every column of \(J\)",
        ],
        0,
        r"Gauss-Newton solves \(J^T J\, d = -J^T F\). If \(J\) is square and invertible, multiply by \((J^T)^{-1}\) and then by \(J^{-1}\) to get \(d = -J^{-1} F\), the Newton root step. A singular \(J\) is the case where the root step is undefined and the least-squares step may still exist. The factor \(\lVert F\rVert\) does not appear once \(J\) is canceled. Orthogonality of \(F\) to the columns would mean \(J^T F = 0\), so both steps would be zero only in that special case, not in general.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        4,
        r"Applying the same tangent step to the equation \(\nabla f(x) = 0\) is",
        [
            r"Newton's method for minimization",
            r"a steepest-descent step with no Hessian",
            r"a Gauss-Newton step that drops every second derivative",
            r"an Armijo test",
        ],
        0,
        r"The gradient equation is a root-finding problem whose Jacobian is the Hessian of \(f\). One tangent step on that equation is the Newton step for minimization. Steepest descent uses only the gradient. Gauss-Newton drops second derivatives of a residual; the minimization Newton step keeps the Hessian. Armijo accepts or rejects a step length after a direction has been chosen.",
        fig=LEV,
        alt=A_LEV,
        preview=P_NOPT,
    )
    b.num(
        4,
        r"Let \(g(t) = t^2 - 2\). Starting at \(t = -4\), what is the next Newton iterate?",
        -2.25,
        "1",
        r"Here \(g(-4) = 14\) and \(g'(-4) = -8\), so the next point is \(-4 - 14/(-8) = -4 + 1.75 = -2.25\). The start is negative and the iterate stays negative, toward the negative root. Reporting \(2.25\) drops the sign. Reporting \(-4\) stays at the start. Reporting \(1.75\) is the correction, not the new point. The positive start \(2\) produced \(1.5\), a different basin.",
        fig=FALL,
        alt=A_FALL,
        preview=P_NOPT,
    )
    b.mc(
        4,
        r"A primal-dual interior-point step on a perturbed KKT system is a Newton step on a root. The system being solved is",
        [
            r"a nonlinear equation in the primal and dual variables, rebuilt at the current point",
            r"a linear program solved by one simplex pivot",
            r"a steepest-descent step on the original inequality constraints alone",
            r"an eigenvalue problem for the constraint matrix",
        ],
        0,
        r"The perturbed complementarity conditions are nonlinear. One interior-point iteration linearizes that system and solves the tangent equation, which is a Newton step on a root. A simplex pivot is a different method for a linear program. Steepest descent does not form the KKT root. An eigenvalue problem is not the perturbed complementarity system.",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_IP,
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


def expl_gn():
    save_explainer(
        "gauss-newton-method",
        "Gauss-Newton method",
        _sec(
            r"""Gauss-Newton minimizes a sum of squared residuals by refusing to solve the nonlinear problem directly. At the current point it replaces the residual vector by its linear model, the value plus the Jacobian times a step, and it chooses the step that makes that model as small as possible in the least-squares sense. The model is a linear least-squares problem, so the step comes from the normal equations. The point then moves by that step, the residual and the Jacobian are rebuilt, and the same linear fit is repeated.

The gradient of \(\tfrac12\lVert r\rVert^2\) is \(J_r^T r\). Whenever the Jacobian has full column rank and this gradient is not zero, the Gauss-Newton step is a descent direction. Its directional derivative equals the negative of a squared norm built from the gradient and the inverse of \(J_r^T J_r\). A short move along the step therefore decreases the sum of squares. Full column rank can fail. The Gram matrix is always positive semidefinite, but it may be singular, and then the normal equations do not determine one step.

Newton's method on the same sum of squares uses a richer Hessian. Besides \(J_r^T J_r\), the true Hessian adds each residual component times the second derivative of that component. Gauss-Newton keeps only the Gram matrix. The dropped term is zero when every component is affine, and it is also zero when the residual itself is zero. A curved residual that is still large makes the two steps differ.""",
            r"""The step solves
\[
J_r^T J_r\, d = -J_r^T r.
\]
The true Hessian of \(\tfrac12\lVert r\rVert^2\) is \(J_r^T J_r + \sum_i r_i \nabla^2 r_i\).""",
            r"""Take the residual \((u^2 - 7,\ u - 4)\) at \(u = 1\). The value is \((-6,\ -3)\) and the Jacobian column is \((2,\ 1)\). The Gram entry is \(4 + 1 = 5\), and the gradient entry is \(2\cdot(-6) + 1\cdot(-3) = -15\). The normal equation \(5d = 15\) gives the step \(3\).

The hatch step is 3. The updated parameter is \(4\). The residual there is \((9,\ 0)\), not zero, so the nonlinear fit is not finished. The linear model was exact only for the tangent, and the square in the first component has already curved away from that tangent.""",
            r"""The normal equation carries a minus sign. Solving \(J^T J\, d = J^T r\) walks up the linear model. A second slip is to invert a singular Gram matrix. Positive semidefinite is not the same as invertible, and a zero column in the Jacobian is enough to make the matrix singular. A third is to expect one step to land on a root of a curved residual. The example moves to a point whose residual is still nonzero. A fourth is to treat \(J_r^T J_r\) as the full Hessian. The missing term is the one that involves second derivatives of the components.""",
            r"""When the Gram matrix is nearly singular, the plain step becomes long and the linear model stops being a trustworthy picture of the residual. Adding a positive multiple of the identity shortens that step and bends it toward steepest descent. That damped step is Levenberg-Marquardt. A different use of the same exact step appears when each new block is already linear: one Gauss-Newton step finishes the block, and chaining those steps is recursive least squares.""",
            COL,
            A_COL,
        ),
    )


def expl_lm():
    save_explainer(
        "levenberg-marquardt",
        "Levenberg-Marquardt method",
        _sec(
            r"""Levenberg-Marquardt keeps the Gauss-Newton model and adds a positive multiple of the identity to the Gram matrix before solving. The shift is called the damping. It does not change the right-hand side, which is still the negative gradient of the sum of squares. What changes is the matrix that converts that gradient into a step.

Two limits explain the blend. As the damping tends to zero, the equation returns to the ordinary Gauss-Newton equation, provided the Gram matrix is invertible. As the damping grows, the inverse of the shifted matrix behaves like the identity divided by the damping. The step then points along the negative gradient, and its length shrinks like one over the damping. Between those limits the direction is a compromise: closer to the least-squares step when the damping is small, and closer to steepest descent when the damping is large.

The shift also repairs a singular Jacobian. The Gram matrix is only positive semidefinite. Adding a positive multiple of the identity makes every nonzero vector see a positive quadratic form, so the matrix is positive definite and the step exists.

The size of the damping is chosen by comparing the linear model with the true residual. A step whose true decrease is a healthy fraction of the decrease the model predicted is accepted, and the damping is reduced so the next step can look more like Gauss-Newton. A step that fails that comparison is rejected, and the damping is increased so the next trial is shorter.""",
            r"""The damped equation is
\[
(J_r^T J_r + \mu I)\, d = -J_r^T r, \qquad \mu > 0.
\]
For large \(\mu\), \(d \approx -(J_r^T r)/\mu\).""",
            r"""Take a scalar parameter whose Jacobian column is \((2,\ 1)\) and whose residual is \((1,\ 1)\). The Gram entry is \(5\) and the gradient entry is \(3\). With damping \(1\) the shifted entry is \(6\), and the step is \(-3/6\).

The cleat step is -0.5. The undamped step would have been \(-3/5\), longer and in the same direction. Raising the damping further shortens the step and does not reverse it. The directional derivative is the gradient times this negative step, so it is negative.""",
            r"""Accepting a bad model and then decreasing the damping does the opposite of the comparison. A rejected step is the one that should increase the damping. A second slip is to put the damping on the right-hand side instead of on the Gram matrix. That changes the gradient rather than the conditioning of the step. A third is to allow a negative damping. The positive-definite guarantee uses a positive shift, and a negative shift can make the matrix indefinite. A fourth is to treat a large damping as a long step. The length falls as the damping rises.""",
            r"""The same diagonal shift is how a Newton step for minimization is forced to be a descent direction when the Hessian is indefinite. There the matrix being shifted is the Hessian rather than a Gram matrix, and a line search can replace the damping test. Both are ways to keep a tangent step inside the region where the model still deserves trust.""",
            SLOW,
            A_SLOW,
        ),
    )


def expl_inc():
    save_explainer(
        "incremental-gradient-methods",
        "Incremental gradient methods",
        _sec(
            r"""An incremental gradient method splits an objective into a sum of blocks and spends the gradient of one block at a time. After each block the parameter moves, and the next block is evaluated at the new point. A batch step does the opposite: it sums every block gradient at the same point and only then moves. At a finite step the two updates are different algorithms, and the order of the blocks matters.

The cost of the incremental pass is that a constant step length need not converge to a stationary point of the sum. On a pair of quadratics the endpoint of a repeated pass can settle at a point where the full gradient is still nonzero. That settled point slides toward a stationary point only as the constant length tends to zero. The usual way to reach a stationary point is therefore a step that tends to zero while the sum of the lengths stays infinite: the vanishing length kills the bias, and the infinite sum still lets the iterates travel.

A batch gradient step on a smooth function has a different budget. If the length stays below twice the reciprocal of a Lipschitz constant, the gradient norms tend to zero with no need to drive the length to zero.""",
            r"""One block updates
\[
x := x - t \nabla f_i(x)
\]
and the next block sees the new \(x\). A batch step uses \(\sum_i \nabla f_i\) at a single point.""",
            r"""Take the blocks \(\tfrac12(u - 9)^2\) and \(\tfrac12(u - 19)^2\), start at \(14\), and use length \(0.4\), with the first block first. The first gradient is \(5\), so the point moves to \(14 - 2 = 12\). The second gradient at \(12\) is \(-7\), so the point moves to \(12 + 2.8\).

The crate reading is 14.8. The full gradient there is \(1.6\), not zero. A batch step would have summed both gradients at \(14\) before moving, and it would not have produced this point. Another pass, started at \(14.8\), evaluates its first gradient at \(14.8\) rather than at \(14\).""",
            r"""Evaluating every later block at the original point is a batch step written one term at a time. The incremental pass is defined by the update in between. A second slip is to expect a constant length to land on the minimizer of the sum. The endpoint of a repeated pass can sit where the full gradient is not zero. A third is to enlarge the length in the hope that one pass will finish the problem. A longer constant step can sit even farther from a stationary point. A fourth is to forget that the order of the blocks changes the intermediate points whenever the length is finite.""",
            r"""Recursive least squares does not minimize each new block by itself. A length-1 pass that jumps to the newest center forgets the earlier blocks and stops there. The recursive step minimizes the old quadratic together with the new block, and one Gauss-Newton step is exact because the stacked cost is quadratic. A nonlinear block is linearized at the current estimate before that stacked step.""",
            SEG,
            A_SEG,
        ),
    )


def expl_rls():
    save_explainer(
        "kalman-recursive-least-squares",
        "Kalman filter as recursive least squares",
        _sec(
            r"""A growing linear least-squares fit does not have to be solved from scratch when one measurement arrives. The measurements already in hand leave a quadratic cost. That cost is summarized by the current estimate and by a variance: the estimate is the minimizer, and the variance is the reciprocal of the curvature. A new linear measurement adds one more squared residual. The stacked cost is still quadratic, so one Gauss-Newton step is exact.

Write the step out and it is a gain times an innovation. The innovation is the new reading minus the reading the current estimate would have produced. The gain is the prior variance times the measurement row, divided by the innovation variance, which is the row times the prior variance times the row, plus the measurement variance. The estimate moves by the gain times the innovation. The variance shrinks by the factor that the gain and the row determine. Those two formulas are the measurement update of the Kalman filter. This skill does not derive them a second time as a filter. It shows that they are the exact minimizer of the growing least-squares cost.

The predict step is a different piece. Propagating the estimate through a state matrix, and inflating the variance by process noise, is not a least-squares block of the kind solved here. That recursion stays with the Kalman filter.""",
            r"""For a scalar row \(c\), prior variance \(P\), and measurement variance \(R\),
\[
L = \frac{P c}{c^2 P + R}.
\]
The estimate adds \(L\) times the innovation. The variance becomes \((1 - L c) P\). This \(L\) is the scalar form of the Kalman gain.""",
            r"""Start from the estimate \(8\) with variance \(9\), and take a measurement \(5\) with row \(1\) and variance \(3\). The gain is \(9/(9 + 3) = 3/4\). The innovation is \(5 - 8 = -3\). The correction is \(3/4\) times \(-3\), which equals \(-9/4\).

The buoy estimate is 5.75. The updated variance is \(1/4\) of \(9\), so \(9/4\). A smaller measurement variance would have raised the gain and pulled the estimate closer to \(5\). The predict step that might have produced the prior \(8\) is not part of this arithmetic.""",
            r"""Subtracting the correction instead of adding it walks away from the measurement. The innovation is already a difference, and the gain is nonnegative for a positive variance and a positive row, so the correction has the sign of the innovation. A second slip is to add the variances to get the new variance. New information shrinks the variance. A third is to re-derive the predict step from this block. The block has no state matrix and no process noise. A fourth is to treat a nonlinear measurement as finished by this same linear step. A curved measurement has to be linearized first.""",
            r"""When the new measurement is nonlinear, the residual is no longer an affine function of the estimate. One Gauss-Newton step is then only the step for the linear model built at the current estimate. Rebuilding that model on every block, with the Jacobian in place of the measurement row and with the innovation measured from the nonlinear map, is the extended update.""",
            HALF,
            A_HALF,
        ),
    )


def expl_ekf():
    save_explainer(
        "extended-kalman-filter",
        "Extended Kalman filter",
        _sec(
            r"""An extended measurement update is the linear update with the measurement rebuilt at the current estimate. The sensor is a nonlinear map. The first-order model of that map is the map's value plus its Jacobian times the displacement from the estimate. The innovation is the reading minus the map's value, not minus the Jacobian times the estimate. The gain is the linear gain with the Jacobian standing where the measurement row would stand. The variance update uses that same Jacobian.

The Jacobian has to be new whenever the estimate moves. A square-law sensor has derivative twice the position, so a correction that changes the position changes the derivative. Using yesterday's Jacobian on today's estimate is a frozen linear model.

The step is exact for the tangent model and the quadratic prior, and only approximate for the curved sensor. If the tangent is a poor picture of the map, the correction can land far from a point that zeros the nonlinear stationarity condition. A position estimate with a square-law reading is the concrete case: each new reading is linearized at the latest position, and the next reading starts over.""",
            r"""With Jacobian \(J_h\) at the estimate,
\[
L = \frac{P J_h}{J_h^2 P + R},
\]
the innovation is the reading minus \(h\) at the estimate, and the variance update is \((1 - L J_h) P\).""",
            r"""Take a position estimate of \(5\) with variance \(1\), and a sensor that reports the square of position. The map equals \(25\) and the Jacobian equals \(10\). A reading of \(45\) with measurement variance \(20\) has innovation \(20\). The innovation variance is \(100 + 20 = 120\), so the gain is \(10/120\). The correction is that gain times \(20\).

The dock position is 6.66667. The Jacobian at this new position is no longer \(10\). The next reading has to be linearized again. The nonlinear cost, prior plus squared sensor residual, does not have zero derivative at this position, because the step minimized the tangent model rather than the curved sensor.""",
            r"""Putting the Jacobian in the innovation, in place of the map, is the linear residual of a map that passes through the origin. A square law does not. A second slip is to use the estimate itself as the Jacobian of \(u^2\). The derivative is twice the estimate. A third is to update the variance with \(1 - L\) when the Jacobian is not \(1\). The factor that multiplies the gain is the Jacobian. A fourth is to keep a single linearization for every later block. The derivative of a nonlinear sensor moves with the estimate.""",
            r"""The same tangent step, pointed at a root of a map rather than at a measurement update, is Newton's method. The next guess is where the tangent hits zero, and a tangent drawn at a poor point can send that guess far away. An extended update has the prior variance to soften the step. A pure root iteration does not, which is why the starting point matters even more there.""",
            LEV,
            A_LEV,
        ),
    )


def expl_newton():
    save_explainer(
        "newton-root-finding",
        "Newton's method for root finding",
        _sec(
            r"""Newton's method looks for a root by replacing the map with its tangent and solving the tangent exactly. In one variable the picture is a graph and a tangent line. The line meets the axis at one point, provided the slope is not zero, and that meeting point is the next guess. The tangent is then redrawn at the new guess. Each iteration throws away the old line.

The algebra is the same in several variables. The Jacobian times the step equals the negative of the map, and the point moves by the step. If the Jacobian is square and invertible, this is also the Gauss-Newton step on the sum of squares of the components, because the Gram matrix can be canceled. If the Jacobian is singular, the tangent does not determine one step. A zero derivative in one variable is the horizontal-tangent case: the line never meets the axis, or it lies on the axis.

The starting point chooses which root is approached, and it can choose a root that is not the nearest. A cubic with three real roots has a start between two of them whose tangent lands on the third. An affine map with a nonzero slope finishes in one step from every start, because the tangent is the map. A tiny slope makes the correction large, so the next guess can leave the neighborhood where the tangent was fair.""",
            r"""The scalar update and the vector step are
\[
t^+ = t - \frac{g(t)}{g'(t)}, \qquad J_F(x)\, d = -F(x).
\]
A zero derivative, or a singular Jacobian, leaves the step undefined.""",
            r"""Take \(g(t) = t^2 - 6\) at \(t = 5\). The value is \(19\) and the derivative is \(10\). The correction is \(19/10\), and the next guess subtracts it from \(5\).

The pier guess is 3.1. The root of this parabola is not \(3.1\). The tangent was drawn at \(5\), where the slope is already steep, and one hit only gets part of the way. Starting on the other side of the axis would follow a negative slope toward the negative root. A start at a point where the derivative vanishes would have no step at all.""",
            r"""Using the derivative of \(t^2\) as \(2\), rather than as \(2t\), divides by the wrong slope and lands at the wrong point. A second slip is to treat a zero derivative as a root. The function value has to vanish as well. A third is to expect the nearest root. The tangent, not the distance to the roots, chooses the next point. A fourth is to reuse the old derivative at the new point. The method rebuilds the tangent because the slope of a curved map has changed.""",
            r"""The same tangent step applied to the gradient equation is Newton's method for minimization. The Jacobian of the gradient is the Hessian, so the step can be attracted to a maximum or a saddle when that Hessian is not positive definite. Farther on, a primal-dual interior-point iteration uses this root step on a perturbed system of complementarity conditions, rebuilding the tangent at every new primal and dual point.""",
            FALL,
            A_FALL,
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
    "gauss-newton-method": "The hatch step is 3",
    "levenberg-marquardt": "The cleat step is -0.5",
    "incremental-gradient-methods": "The crate reading is 14.8",
    "kalman-recursive-least-squares": "The buoy estimate is 5.75",
    "extended-kalman-filter": "The dock position is 6.66667",
    "newton-root-finding": "The pier guess is 3.1",
}


def main():
    _balance_mc()
    bank_gn()
    bank_lm()
    bank_inc()
    bank_rls()
    bank_ekf()
    bank_newton()
    expl_gn()
    expl_lm()
    expl_inc()
    expl_rls()
    expl_ekf()
    expl_newton()
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
