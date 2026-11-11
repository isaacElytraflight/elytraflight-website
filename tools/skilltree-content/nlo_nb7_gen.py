#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB7 banks and explainers.

Skills: lagrangian-duality-lower-bounds, lagrange-multiplier-equality,
kkt-conditions, lp-duality-kkt, projection-affine-halfspace-kkt,
linear-least-squares, least-squares-data-fitting, nonlinear-least-squares,
circle-fitting-least-squares, svm-quadratic-program.

Closed-form answers live here. skilltree/verify_nlo_nb7.py recomputes the
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
    dented_quad_fig,
    halfspace_fig,
    matrix_fig,
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
HALF = halfspace_fig("a half-plane")
A_HALF = "A straight boundary with one side shaded."
ORTH = orthant_fig("the first quadrant")
A_ORTH = "The closed first quadrant, shaded."
SEG = segment_fig("a segment")
A_SEG = "A solid segment joins two marked points on a dashed line."
SIMP = simplex_fig("a segment in the first quadrant")
A_SIMP = "A segment joining two marked points on the axes."
DENT = dented_quad_fig("a dented quadrilateral")
A_DENT = "A four-sided region with one corner pushed in."
ARR = plane_vectors([(1.15, 0.35, "d")], "one arrow from the origin")
A_ARR = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.05, 0.2, "c"), (-0.35, 0.95, "d")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."
BASIS = matrix_fig([["b", "n"], ["1", "0"]], "a two-column array")
A_BASIS = "A small array with two short rows of labels."

P_KKT = ["kkt-conditions"]
P_DUAL = ["lp-duality-kkt"]
P_PROJ = ["projection-affine-halfspace-kkt"]
P_ONTO = ["projection-onto-convex-set"]
P_GRAD = ["gradient-projection-method"]
P_SCALED = ["scaled-gradient-projection"]
P_AFF = ["affine-scaling-method"]
P_IP = ["primal-dual-interior-point"]
P_FIT = ["least-squares-data-fitting"]
P_NLS = ["nonlinear-least-squares"]
P_KAL = ["kalman-recursive-least-squares"]
P_CIRC = ["circle-fitting-least-squares"]
P_GN = ["gauss-newton-method"]
P_INC = ["incremental-gradient-methods"]
P_LM = ["levenberg-marquardt"]
P_LAG = ["lagrange-multiplier-equality"]


def bank_dual():
    b = Bank("lagrangian-duality-lower-bounds")
    b.mc(
        1,
        r"For a fixed multiplier, the dual function is",
        [
            "the primal objective evaluated only at feasible points",
            "the supremum of the Lagrangian over the decision variable",
            "the infimum of the Lagrangian over the decision variable",
            "always equal to the primal optimal value",
        ],
        2,
        r"The dual function holds the multipliers fixed and minimizes the Lagrangian in the decision variable. A feasible primal value is an upper number on the optimal value, not this construction. The supremum would reverse the problem and need not be a lower bound. Equality with the primal optimal value is strong duality, which needs extra conditions. The dual function itself is only the infimum.",
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        1,
        r"Minimize \(x^2\) subject to \(x \ge 3\). The Lagrangian is \(x^2 + u(3 - x)\) with \(u \ge 0\). What lower bound does \(u = 2\) give?",
        5,
        "1",
        r"Stationarity in \(x\) is \(2x - u = 0\), so \(x = u/2\). Substituting produces the dual function \(3u - u^2/4\). At \(u = 2\) that value is \(6 - 1 = 5\). The primal optimum is \(9\), at \(x = 3\), so \(5\) sits strictly below it, which is what a non-optimal multiplier does. Reporting \(9\) gives the primal value. Reporting \(4\) is \(u^2\). Reporting \(2\) is the multiplier itself.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        1,
        "Weak duality says that every dual-feasible multiplier gives",
        [
            "a lower bound on the primal optimal value",
            "an upper bound on the primal optimal value",
            "a point that is automatically primal feasible",
            "a negative multiplier on every equality",
        ],
        0,
        r"The Lagrangian at a primal-feasible point is at most the objective when inequality multipliers are nonnegative, because each inequality term is nonpositive. Minimizing the Lagrangian can only make the number smaller, so the dual function sits at or below the primal optimal value. It is not an upper bound. The \(x\) that attains the infimum need not satisfy the constraints. Equality multipliers are free. Their sign is not part of dual feasibility.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.order(
        2,
        r"Put these steps in the order that builds the dual of a minimization with inequalities \(g(x) \le 0\). Each step uses the result of the step before it.",
        [
            r"Attach a multiplier \(u\) to \(g\) and form the Lagrangian \(f(x) + u\, g(x)\).",
            r"With that Lagrangian in hand, minimize it in \(x\) while holding \(u\) fixed.",
            r"Keep only the multipliers \(u \ge 0\), the ones dual feasibility allows for this inequality.",
            "Maximize the resulting dual function over those remaining multipliers.",
        ],
        r"The Lagrangian has to exist before it can be minimized in \(x\). That minimization, with the multiplier held fixed, is the dual function, so the sign restriction comes after the function has been formed. Only then does the dual problem maximize it. Maximizing before the infimum would still be a joint problem in \(x\), not the dual. Restricting the sign before the Lagrangian is written does not yet produce a function of \(u\).",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"Minimize \(x^2\) subject to \(x \ge 3\). The primal optimal value is \(9\), and the dual function is \(3u - u^2/4\). Which statements are true?",
        [
            r"At \(u = 4\) the dual function equals \(8\).",
            r"At \(u = 2\) the dual function equals \(9\).",
            r"\(u = -2\) is dual feasible.",
            r"At \(u = 6\) the dual function equals the primal optimal value.",
            r"Every dual-feasible value is at most \(9\).",
        ],
        [0, 3, 4],
        r"Substitute the stated multipliers into \(3u - u^2/4\)."
        "\n"
        r"• \(u = 4\) gives \(12 - 4 = 8\)."
        "\n"
        r"• \(u = 6\) gives \(18 - 9 = 9\), matching the primal value."
        "\n"
        r"• Weak duality puts every value at a nonnegative multiplier at or below \(9\)."
        "\n"
        r"• \(u = 2\) gives \(5\), not \(9\)."
        "\n"
        r"• A negative multiplier is not dual feasible for a \(\le\) constraint written in the Lagrangian as \(u(3-x)\).",
        fig=FALL,
        alt=A_FALL,
    )
    b.sym(
        2,
        r"Minimize \(x^2\) subject to \(x \ge a\), with \(a > 0\). Using the multiplier \(u \ge 0\) on \(a - x\), the dual function equals",
        "a*u-u*u/4",
        {"a": (2, 5), "u": (1, 3)},
        r"The Lagrangian is \(x^2 + u(a - x)\). Its derivative in \(x\) is \(2x - u\), so the infimum occurs at \(x = u/2\). Substituting leaves \(a u - u^2/4\). On the declared ranges this value is finite and positive. Replacing the minus by a plus double-counts the square. Dropping \(a\) leaves only the quadratic term, which is not the infimum. Evaluating the Lagrangian at \(x = a\) instead of at \(x = u/2\) computes a feasible primal number, not the dual function.",
        alternates=["a*u-(u*u)/4", "u*(a-u/4)"],
        fig=HALF,
        alt=A_HALF,
    )
    b.find_error(
        3,
        r"A note derives the dual of minimizing \(x^2\) subject to \(x \ge 3\). Exactly one step is a false claim.",
        [
            r"The Lagrangian is \(x^2 + u(3 - x)\).",
            r"Stationarity in \(x\) gives \(2x - u = 0\), so \(x = u/2\).",
            r"Substituting that \(x\) produces the dual function \(3u + u^2/4\).",
            r"Dual feasibility for this inequality requires \(u \ge 0\).",
        ],
        2,
        r"The Lagrangian and the stationarity equation match \(x^2 + u(3-x)\). Dual feasibility keeps \(u\) nonnegative because the constraint was written as \(3-x \le 0\). The false step is the substitution. \((u/2)^2 + u(3 - u/2) = u^2/4 + 3u - u^2/2 = 3u - u^2/4\). The squared term is subtracted, not added.",
        [
            r"The substitution equals \(3u - u^2/4\). The squared term is subtracted.",
            r"Stationarity should have set \(2x + u = 0\).",
            "Dual feasibility allows a negative multiplier here.",
        ],
        0,
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        3,
        r"The same problem has primal optimal value \(9\). The multiplier \(u = 4\) produces dual value \(8\). What is the duality gap?",
        1,
        "1",
        r"The gap is the primal optimal value minus the dual value, \(9 - 8 = 1\). Both numbers are given by the problem, and weak duality says the difference cannot be negative. Reporting \(8\) or \(9\) repeats one of the two values. Reporting \(17\) adds them. The gap is zero only at a multiplier that attains \(9\), and \(u = 4\) is not that multiplier.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        3,
        "The dual problem, once the dual function is known, is",
        [
            "a joint minimization over the decision variable and the multipliers",
            "a maximization of the dual function over dual-feasible multipliers",
            "a minimization of the dual function over dual-feasible multipliers",
            "a maximization of the primal objective over the feasible set",
        ],
        1,
        r"Building the dual function already minimized out the decision variable. What remains is a maximization over the multipliers that keep the infimum finite and satisfy the sign restrictions. Minimizing the dual function would run away from the primal value. A joint minimization is the Lagrangian problem before the infimum is taken. Maximizing the primal objective is a different problem, and for a minimization primal it is not the dual.",
        fig=DENT,
        alt=A_DENT,
    )
    b.mc(
        4,
        r"An inequality \(g(x) \le 0\) and an equality \(h(x) = 0\) differ, in the dual, by",
        [
            "nothing: both multipliers are required to be negative",
            "the equality multiplier being forced to zero",
            "the inequality being dropped from the Lagrangian",
            "a nonnegative multiplier on the inequality and a free multiplier on the equality",
        ],
        3,
        r"Nonnegativity is what makes the inequality term \(u\, g(x)\) nonpositive at a feasible point, and that is the source of the lower bound. An equality is zero on the feasible set for either sign of its multiplier, so that multiplier stays free. Forcing it to zero deletes the constraint. Dropping the inequality from the Lagrangian deletes the lower-bound term. Requiring both multipliers to be negative reverses the inequality.",
        fig=PAIR,
        alt=A_PAIR,
        preview=P_KKT,
    )
    b.num(
        4,
        r"Minimize \(x^2\) subject to \(x \ge 5\). Using the Lagrangian \(x^2 + u(5 - x)\), what lower bound does \(u = 4\) give?",
        16,
        "1",
        r"The same completion gives the dual function \(5u - u^2/4\). At \(u = 4\) the value is \(20 - 4 = 16\). The unconstrained minimizer of the Lagrangian is \(x = 2\), which is not primal feasible, and that is allowed: the dual function minimizes over every \(x\). The feasible value \(x = 5\) gives the primal number \(25\), which is not this lower bound. Reporting \(4\) gives the multiplier. Reporting \(20\) stops before subtracting the square.",
        fig=FALL,
        alt=A_FALL,
        preview=P_PROJ,
    )
    b.mc(
        4,
        "Applying the same Lagrangian construction to a linear program produces",
        [
            "another linear program, the dual",
            "a nonconvex quadratic program",
            "only the auxiliary problem that searches for a first basis",
            "the reduced-cost vector of one simplex basis, and nothing else",
        ],
        0,
        r"The Lagrangian of a linear objective with linear constraints is linear in the decision variable. Minimizing it in that variable is finite only on a set of linear inequalities in the multipliers, and the resulting dual function is linear. The dual is therefore a linear program. It is not a nonconvex quadratic. The auxiliary start-up problem and a single reduced-cost vector are simplex constructions. They are not the dual program obtained from the Lagrangian.",
        fig=BASIS,
        alt=A_BASIS,
        preview=P_DUAL,
    )
    b.save()


def bank_lagrange():
    b = Bank("lagrange-multiplier-equality")
    b.mc(
        1,
        "At a minimizer where the constraint gradients are linearly independent, the Lagrange condition says",
        [
            r"the objective gradient is zero and the constraints may be ignored",
            r"the objective gradient is a linear combination of the constraint gradients, and the constraints hold",
            "every constraint gradient is the zero vector",
            "every multiplier is nonnegative",
        ],
        1,
        r"Independence lets the objective gradient be written in the span of the constraint gradients, with the constraints themselves still satisfied. Setting the objective gradient to zero is the unconstrained stationarity test. A zero constraint gradient is a failure of independence, not the conclusion. Nonnegative multipliers belong to inequalities. Equalities leave the multiplier free.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        1,
        r"Minimize \(x^2 + y^2\) subject to \(x + 2y = 5\). The Lagrangian is \(x^2 + y^2 + \lambda(x + 2y - 5)\). What is \(\lambda\) at the minimizer?",
        -2,
        "1",
        r"The partial derivatives give \(2x + \lambda = 0\) and \(2y + 2\lambda = 0\), so \(y = 2x\) and \(\lambda = -2x\). The constraint \(x + 4x = 5\) forces \(x = 1\), \(y = 2\), and \(\lambda = -2\). The objective there is \(5\). Reporting \(2\) drops the sign. Reporting \(1\) or \(5\) reports a coordinate or the objective, not the multiplier. The constraint gradient \((1, 2)\) is not zero, so a multiplier is allowed to exist, and this value is it.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        "Regularity, as used for this multiplier rule, means",
        [
            "the constraint gradients at the point are linearly independent",
            "the objective gradient is zero",
            "the feasible set is a ball",
            "every multiplier is positive",
        ],
        0,
        r"The multiplier rule used here assumes the constraint gradients are linearly independent, so they form a basis for the normal space. A zero objective gradient is a conclusion one might reach, not the hypothesis. The feasible set need not be a ball. Equality multipliers are not required to be positive. Dependence is exactly the case in which a minimizer can fail to have a multiplier.",
        fig=ARR,
        alt=A_ARR,
    )
    b.order(
        2,
        r"Put these steps in the order that solves \(\min x^2 + y^2\) subject to \(x + 2y = 5\) by Lagrange multipliers. Each step uses the previous result.",
        [
            r"Form the Lagrangian \(x^2 + y^2 + \lambda(x + 2y - 5)\).",
            "Differentiate that Lagrangian in the two variables and set both partial derivatives to zero.",
            "Adjoin the original equality to those two stationarity equations.",
            "Solve the three equations for the two variables and the multiplier.",
        ],
        r"The Lagrangian is the function being differentiated, so it comes first. The two partial derivatives are equations in \(x\), \(y\), and \(\lambda\), and they do not yet include the constraint. Adjoining the constraint supplies the third equation. Only the three-equation system determines the numbers. Solving before the constraint is adjoined leaves a free scale. Differentiating the constraint instead of the Lagrangian produces the constraint gradient alone, which is not the stationarity system.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"At \((x, y, \lambda) = (1, 2, -2)\) for \(\min x^2 + y^2\) subject to \(x + 2y = 5\), which claims hold?",
        [
            r"The constraint holds: \(1 + 4 = 5\).",
            r"Stationarity in \(x\) holds: \(2\cdot 1 + (-2) = 0\).",
            r"Stationarity in \(y\) holds: \(2\cdot 2 + 2\cdot(-2) = 0\).",
            r"The constraint gradient \((1, 2)\) is the zero vector.",
            "The multiplier must be nonnegative because the constraint is an equality.",
        ],
        [0, 1, 2],
        r"Each stationarity claim is the corresponding partial derivative of the Lagrangian, and both evaluate to zero. The constraint value is \(5\)."
        "\n"
        r"• The gradient \((1, 2)\) is not zero, so regularity holds at this point."
        "\n"
        r"• An equality does not force its multiplier to be nonnegative. The value \(-2\) is allowed.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.sym(
        2,
        r"Minimize \(p x^2\) subject to \(x = a\), with \(p > 0\). Using the Lagrangian \(p x^2 + \lambda(x - a)\), the multiplier \(\lambda\) equals",
        "-2*p*a",
        {"p": (1, 3), "a": (1, 4)},
        r"Differentiate in \(x\): \(2 p x + \lambda = 0\). The constraint forces \(x = a\), so \(\lambda = -2 p a\). Both names appear because the curvature \(p\) scales the multiplier and the constraint location \(a\) places it. Dropping the factor \(2\) forgets the derivative of the square. A plus sign would be the multiplier for the constraint written as \(a - x\). On the declared ranges the multiplier is negative, matching a positive \(p\) and a positive \(a\).",
        alternates=["-(2*p*a)", "-2*a*p"],
        fig=FALL,
        alt=A_FALL,
    )
    b.find_error(
        3,
        r"A note claims that minimizing \(x\) subject to \(x^2 = 0\) has a Lagrange multiplier. Exactly one step is a false claim.",
        [
            r"The only feasible point is \(x = 0\), so that point is the minimizer.",
            r"The derivative of the objective is \(1\) at every point.",
            r"The derivative of the constraint is \(2x\), which equals \(0\) at \(x = 0\).",
            r"Therefore \(1 + \lambda \cdot 0 = 0\) is solved by \(\lambda = 0\).",
        ],
        3,
        r"The feasible set is a single point, so it is a minimizer, and the two derivatives are correct. Their combination is the scalar equation \(1 = 0\). No number \(\lambda\) solves it. The constraint gradient vanished, which is a failure of regularity, and the multiplier rule does not apply. Claiming that \(\lambda = 0\) works treats a false equation as an identity.",
        [
            r"The equation \(1 = 0\) has no solution, so no multiplier exists.",
            "The objective derivative is the step that is wrong.",
            "The only feasible point is not a minimizer.",
        ],
        0,
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        3,
        r"Minimize \(x^2 + y^2\) subject to \(3x + y = 10\), with Lagrangian \(x^2 + y^2 + \lambda(3x + y - 10)\). What is the objective value at the minimizer?",
        10,
        "1",
        r"Stationarity is \(2x + 3\lambda = 0\) and \(2y + \lambda = 0\), so \(\lambda = -2y\) and \(x = 3y\). The constraint \(9y + y = 10\) gives \(y = 1\), \(x = 3\). The objective is \(9 + 1 = 10\). Reporting \(3\) or \(1\) gives a coordinate. Reporting \(-2\) gives the multiplier \(\lambda = -2y\). The constraint gradient \((3, 1)\) is independent, so this critical point is the multiplier point, and the value follows by substitution.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        3,
        "Geometrically, at a regular equality-constrained minimizer, the objective gradient is",
        [
            "orthogonal to every constraint gradient",
            "necessarily the zero vector",
            "normal to the constraint surface: it lies in the span of the constraint gradients",
            "parallel to every feasible direction, including directions that leave the surface",
        ],
        2,
        r"The stationarity condition puts the objective gradient in the span of the constraint gradients, which is the normal space to the constraint surface. It is orthogonal to the tangent directions, not to the constraint gradients themselves. It is zero only when that span happens to contain zero with a zero multiplier. Feasible directions lie in the tangent space. The gradient is orthogonal to those, rather than parallel to them.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        4,
        r"Replacing an equality by an inequality \(g(x) \le 0\) adds which requirement on its multiplier?",
        [
            r"the multiplier is nonnegative, and it is zero whenever \(g(x) < 0\)",
            "the multiplier stays free and the constraint is dropped",
            "the objective gradient must be zero",
            "the constraint gradient must be zero",
        ],
        0,
        r"An inequality contributes a sign restriction and complementary slackness: the multiplier cannot be negative, and a strict inequality forces the multiplier to zero. The equality case had neither requirement. Dropping the constraint removes it from stationarity. A zero objective gradient and a zero constraint gradient are not the new conditions. The second of those is a regularity failure.",
        fig=HALF,
        alt=A_HALF,
        preview=P_KKT,
    )
    b.num(
        4,
        r"The nearest point on the line \(x + y = 6\) to the origin minimizes \(x^2 + y^2\) subject to that equality. With Lagrangian \(x^2 + y^2 + \lambda(x + y - 6)\), what is \(\lambda\)?",
        -6,
        "1",
        r"Stationarity forces \(2x + \lambda = 0\) and \(2y + \lambda = 0\), so \(x = y\). The line gives \(2x = 6\), hence \(x = y = 3\) and \(\lambda = -6\). Reporting \(3\) gives a coordinate. Reporting \(6\) drops the sign. Reporting \(18\) is the objective \(9 + 9\). This is the equality-constrained projection onto the line, and the multiplier is the coefficient in \(x = -\lambda/2\).",
        fig=SEG,
        alt=A_SEG,
        preview=P_PROJ,
    )
    b.mc(
        4,
        "If the constraint gradients are linearly dependent at a minimizer, the multiplier rule",
        [
            "still produces a multiplier for every smooth objective",
            "can fail: a minimizer need not have any multiplier",
            "forces the objective gradient to be zero",
            "makes every feasible point a minimizer",
        ],
        1,
        r"Independence is a hypothesis, not a decoration. When the constraint gradient vanishes, stationarity can become a false numerical equation, as with minimizing \(x\) subject to \(x^2 = 0\). Dependence does not force the objective gradient to vanish, and it does not make the whole feasible set optimal. The rule simply may have nothing to solve for.",
        fig=DENT,
        alt=A_DENT,
        preview=P_DUAL,
    )
    b.save()


def bank_kkt():
    b = Bank("kkt-conditions")
    b.mc(
        1,
        r"Complementary slackness for an inequality \(g(x) \le 0\) with multiplier \(\nu\) says",
        [
            r"\(\nu = 0\) or \(g(x) = 0\), or both",
            r"both \(\nu > 0\) and \(g(x) < 0\)",
            "the multiplier is always zero",
            "the constraint gradient is zero",
        ],
        0,
        r"The product \(\nu\, g(x)\) is zero, so at least one factor vanishes. Both may vanish. Requiring a positive multiplier and a strict inequality at once is the combination the product forbids. The multiplier is zero only on the inactive branch. A zero constraint gradient is a regularity question, not slackness.",
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        1,
        r"Minimize \((x - 4)^2\) subject to \(x \le 1\). The Lagrangian is \((x - 4)^2 + \nu(x - 1)\) with \(\nu \ge 0\). What is \(\nu\) at the KKT point?",
        6,
        "1",
        r"Stationarity is \(2(x - 4) + \nu = 0\). The branch \(\nu = 0\) forces \(x = 4\), which violates \(x \le 1\). The active branch \(x = 1\) gives \(\nu = 6\), and \(6 \ge 0\). The objective at that point is \(9\), which is not the multiplier. Reporting \(1\) or \(4\) gives a coordinate. Reporting \(9\) gives the objective. Reporting \(0\) is the discarded branch.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        1,
        r"Dual feasibility for an inequality written as \(g(x) \le 0\) means",
        [
            "the multiplier is free",
            "the multiplier is nonpositive",
            "the multiplier is nonnegative",
            "the multiplier equals the objective",
        ],
        2,
        r"The Lagrangian term is \(\nu\, g(x)\). At a feasible point \(g(x) \le 0\), a nonnegative \(\nu\) makes that term nonpositive, which is the lower-bound direction. A free multiplier is the equality case. A nonpositive multiplier would reward a violated constraint. The multiplier is not the objective value.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.order(
        2,
        r"Put these steps in the order that solves the KKT system for \(\min (x - 3)^2\) subject to \(x \le 1\). Each step uses the previous result.",
        [
            r"Write stationarity: \(2(x - 3) + \nu = 0\).",
            r"Split on complementary slackness into the case \(\nu = 0\) and the case \(x = 1\).",
            r"Discard \(\nu = 0\), because the stationarity equation then puts \(x\) at \(3\), which violates \(x \le 1\).",
            r"On the remaining case \(x = 1\), solve stationarity for \(\nu\) and check \(\nu \ge 0\).",
        ],
        r"Stationarity is the equation both cases must obey, so it is written first. Complementary slackness is what splits the cases. The inactive case is tested against primal feasibility and fails. The active case is the one that remains, and dual feasibility is the last sign check on the multiplier it produces. Checking the sign before solving for \(\nu\) does not yet have a number. Keeping \(x = 3\) would accept an infeasible point.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"For \(\min (x - 3)^2\) subject to \(x \le 1\), the candidate is \(x = 1\), \(\nu = 4\). Which KKT conditions hold?",
        [
            r"Stationarity: \(2(1 - 3) + 4 = 0\).",
            r"Primal feasibility: \(1 \le 1\).",
            r"Dual feasibility: \(4 \ge 0\).",
            r"Complementary slackness: \(4 \cdot (1 - 1) = 0\).",
            "The multiplier is zero.",
        ],
        [0, 1, 2, 3],
        r"All four KKT conditions hold at this candidate."
        "\n"
        r"• Stationarity is \(-4 + 4 = 0\)."
        "\n"
        r"• The bound holds with equality, so the point is feasible and the product with \(\nu\) is zero."
        "\n"
        r"• The multiplier \(4\) is nonnegative."
        "\n"
        r"• The multiplier is not zero. The constraint is active, so slackness does not ask it to be.",
        fig=HALF,
        alt=A_HALF,
    )
    b.sym(
        2,
        r"Minimize \((x - a)^2\) subject to \(x \le b\), and suppose the bound is active. Stationarity \(2(x - a) + \nu = 0\) at \(x = b\) gives the multiplier",
        "2*(a-b)",
        {"a": (4, 7), "b": (1, 3)},
        r"Set \(x = b\) in \(2(x - a) + \nu = 0\) and solve: \(\nu = 2(a - b)\). Both names are required because the multiplier measures how far the unconstrained minimizer \(a\) sits beyond the bound \(b\). On the declared ranges \(a > b\), so the multiplier is positive, which is the feasible sign. The opposite sign \(2(b - a)\) would describe a lower bound instead of this upper bound. Forgetting the \(2\) drops the derivative of the square.",
        alternates=["2*a-2*b", "(a-b)*2"],
        fig=FALL,
        alt=A_FALL,
    )
    b.find_error(
        3,
        r"A note runs the KKT cases for \(\min (x - 3)^2\) subject to \(x \le 1\). Exactly one step is a false claim.",
        [
            r"Stationarity says \(2(x - 3) + \nu = 0\).",
            r"Complementary slackness allows the case \(\nu = 0\), which forces \(x = 3\).",
            r"The point \(x = 3\) satisfies \(x \le 1\), so it is the KKT point, with \(\nu = 0\).",
            r"The other case \(x = 1\) gives \(\nu = 4\), which is nonnegative.",
        ],
        2,
        r"Stationarity is right, and the inactive case really does force \(x = 3\). The active case really does give \(\nu = 4 \ge 0\). The false claim is that \(x = 3\) satisfies the inequality. It does not, so that branch is not a KKT point. The surviving point is \(x = 1\).",
        [
            r"\(x = 3\) violates \(x \le 1\), so the inactive branch is not primal feasible.",
            "Stationarity is the false line.",
            r"\(\nu = 4\) is negative, so the active branch fails.",
        ],
        0,
        fig=DENT,
        alt=A_DENT,
    )
    b.num(
        3,
        r"Minimize \(x^2 + y^2\) subject to \(x + y \ge 4\). The Lagrangian is \(x^2 + y^2 + \nu(4 - x - y)\) with \(\nu \ge 0\). What is the objective at the KKT point?",
        8,
        "1",
        r"Stationarity gives \(x = y = \nu/2\). The branch \(\nu = 0\) is the origin, and \(0 \ge 4\) fails. The active branch \(x + y = 4\) with \(x = y\) gives \(x = y = 2\) and \(\nu = 4\). The objective is \(4 + 4 = 8\). Reporting \(2\) or \(4\) gives a coordinate or the multiplier. Reporting \(0\) is the discarded branch. Complementary slackness holds because the constraint is active.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        3,
        r"A point where \(\nu > 0\) and \(g(x) < 0\)",
        [
            "is allowed when the inequality is an equality in disguise",
            "cannot be a KKT point",
            "is required at every KKT point",
            "means the objective is unbounded below",
        ],
        1,
        r"Complementary slackness sets the product to zero. A positive multiplier and a strict inequality make the product nonzero, so the point fails KKT. It is not required. It does not say anything about the objective being unbounded. Calling the inequality an equality does not relax the product. The active branch is the one a positive multiplier is allowed to sit on.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        r"Minimize \((x - 1)^2\) subject to \(0 \le x \le 2\). The unconstrained minimizer \(x = 1\) lies strictly inside the interval. The two inequality multipliers there are",
        [
            "both zero",
            "both positive",
            "one positive and one negative",
            "undefined, because a bound cannot have a multiplier",
        ],
        0,
        r"The point \(x = 1\) is primal feasible and the objective gradient is zero, so stationarity holds with both multipliers equal to zero. Complementary slackness agrees, because neither bound is active. A positive multiplier would require the matching bound to be active. A negative multiplier fails dual feasibility. Bounds are inequalities, so they do have multipliers. Here both multipliers happen to vanish.",
        fig=SEG,
        alt=A_SEG,
        preview=P_DUAL,
    )
    b.num(
        4,
        r"Minimize \((x - 5)^2\) subject to \(x \le 2\), with Lagrangian \((x - 5)^2 + \nu(x - 2)\) and \(\nu \ge 0\). What is the objective value at the KKT point?",
        9,
        "1",
        r"The inactive branch \(\nu = 0\) gives \(x = 5\), outside the half-line. The active point is \(x = 2\), and stationarity gives \(\nu = 6 \ge 0\). The objective is \((2 - 5)^2 = 9\). Reporting \(6\) gives the multiplier. Reporting \(2\) or \(5\) gives a coordinate. The same active point is the projection of \(5\) onto the half-line \(x \le 2\).",
        fig=FALL,
        alt=A_FALL,
        preview=P_PROJ,
    )
    b.mc(
        4,
        r"For \(\min (x - 3)^2\) subject to \(x \le 1\), the candidate \(x = 3\), \(\nu = 0\) fails KKT because",
        [
            "stationarity fails",
            "complementary slackness fails",
            "primal feasibility fails",
            "dual feasibility fails",
        ],
        2,
        r"Stationarity holds: the derivative of \((x - 3)^2\) is zero at \(x = 3\), and the multiplier is zero. The product \(\nu\, g(x)\) is zero, so slackness holds. The multiplier is nonnegative. The point fails because \(3 \le 1\) is false. A KKT point has to be feasible before the other three conditions can certify it.",
        fig=DENT,
        alt=A_DENT,
        preview=P_IP,
    )
    b.save()


def bank_lpdual():
    b = Bank("lp-duality-kkt")
    b.mc(
        1,
        r"The dual of minimizing \(c^T x\) subject to \(Ax = b\) and \(x \ge 0\) is",
        [
            r"maximize \(b^T y\) subject to \(A^T y \le c\)",
            r"minimize \(b^T y\) subject to \(A^T y \le c\)",
            r"maximize \(c^T y\) subject to \(Ay = b\)",
            r"maximize \(b^T y\) subject to \(A^T y \ge c\)",
        ],
        0,
        r"Stationarity of the Lagrangian solves the inequality multiplier as \(s = c - A^T y\). Dual feasibility \(s \ge 0\) is \(A^T y \le c\). After that substitution the Lagrangian equals \(b^T y\), and the dual maximizes it. Minimizing \(b^T y\) runs in the wrong direction. Swapping \(b\) and \(c\), or reversing the inequality, describes a different program.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.num(
        1,
        r"Minimize \(-3x\) subject to \(x + s = 7\) with \(x, s \ge 0\). The dual is maximize \(7y\) subject to \(y \le -3\) and \(y \le 0\). What is the optimal dual value?",
        -21,
        "1",
        r"The tighter constraint is \(y \le -3\). Maximizing \(7y\) pushes \(y\) up to \(-3\), and the value is \(7 \cdot (-3) = -21\). The primal attains the same number at \(x = 7\), \(s = 0\). Reporting \(21\) drops the sign. Reporting \(-3\) or \(7\) reports the multiplier or the right-hand side. Reporting \(0\) is \(7y\) at \(y = 0\), and that multiplier is dual infeasible because it violates \(y \le -3\).",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        1,
        r"In this standard-form KKT system, the dual slack on column \(j\) is",
        [
            r"the primal variable \(x_j\)",
            r"the residual \((Ax - b)_j\)",
            r"\(c_j - (A^T y)_j\), required to be nonnegative",
            "allowed to be negative at a KKT point",
        ],
        2,
        r"Stationarity rearranges to a nonnegative slack \(s_j = c_j - (A^T y)_j\). That slack is not the primal variable. Complementary slackness ties them together by a product, and they are different numbers. The primal residual \(Ax - b\) is zero at a feasible point. It is not the dual slack. A negative dual slack fails dual feasibility.",
        fig=ARR,
        alt=A_ARR,
    )
    b.order(
        2,
        r"Put these steps in the order that derives the dual of \(\min c^T x\) subject to \(Ax = b\), \(x \ge 0\). Each step uses the previous result.",
        [
            r"Write the Lagrangian \(c^T x + y^T(b - Ax)\) and introduce a nonnegative multiplier for each \(x_j \ge 0\).",
            r"Set the derivative in \(x\) to zero and solve it, obtaining the slack identity \(s = c - A^T y\).",
            r"Impose \(s \ge 0\), which is the dual constraint \(A^T y \le c\).",
            r"Substitute that stationarity relation back into the Lagrangian to obtain the dual objective \(b^T y\), then maximize it.",
        ],
        r"The Lagrangian is the object being differentiated, so it comes first. Stationarity produces the slack formula. Dual feasibility is the sign restriction on that slack, and it is the dual constraint. Only after the coefficient of \(x\) has been eliminated does the Lagrangian collapse to \(b^T y\), which the dual maximizes. Maximizing before eliminating \(x\) is not yet a problem in \(y\) alone. Reversing \(s \ge 0\) would produce the opposite dual inequality.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"For minimize \(-3x\) subject to \(x + s = 7\), \(x, s \ge 0\), consider the dual multiplier \(y = -3\). Which claims hold?",
        [
            r"The dual constraint on \(x\) holds: \(y \le -3\).",
            r"The dual constraint on \(s\) holds: \(y \le 0\).",
            r"The dual objective equals \(-21\).",
            r"\(y = 0\) is dual optimal.",
            r"\(y = -1\) is dual feasible.",
        ],
        [0, 1, 2],
        r"Both dual inequalities hold at \(y = -3\), and \(7 \cdot (-3) = -21\)."
        "\n"
        r"• \(y = 0\) violates \(y \le -3\), so it is dual infeasible and cannot be optimal."
        "\n"
        r"• \(y = -1\) violates \(y \le -3\), so it is not dual feasible.",
        fig=FALL,
        alt=A_FALL,
    )
    b.sym(
        2,
        r"A standard-form column with entries \(a\) and \(b\) and cost \(p\) has dual multiplier \((y, z)\). The dual slack of that column equals",
        "p-a*y-b*z",
        {"a": (1, 2), "b": (1, 2), "y": (0.2, 0.5), "z": (0.2, 0.5), "p": (8, 12)},
        r"The dual inequality is \(a y + b z \le p\), so the slack that complementary slackness multiplies by the primal variable is \(p - a y - b z\). Every name appears: the two column entries, the two multipliers, and the cost. On the declared ranges the slack is positive. Adding the linear form to \(p\) measures the wrong side of the inequality. Omitting one column entry drops part of \(A^T y\).",
        alternates=["p-(a*y+b*z)", "-a*y-b*z+p"],
        fig=BASIS,
        alt=A_BASIS,
    )
    b.find_error(
        3,
        r"A note derives the dual of \(\min c^T x\) subject to \(Ax = b\), \(x \ge 0\). Exactly one step is a false claim.",
        [
            r"The equality \(Ax = b\) is given a free multiplier \(y\).",
            r"Stationarity produces the slack identity \(s = c - A^T y\).",
            r"Dual feasibility is the inequality \(A^T y \ge c\).",
            r"The dual maximizes \(b^T y\).",
        ],
        2,
        r"The equality multiplier is free, and stationarity really does write \(s = c - A^T y\). Substituting a feasible multiplier into the Lagrangian leaves \(b^T y\), which is maximized. The false step reverses the inequality. Nonnegative \(s\) means \(c - A^T y \ge 0\), that is \(A^T y \le c\).",
        [
            r"Nonnegative slack means \(A^T y \le c\), the opposite inequality.",
            "The equality multiplier should have been nonnegative.",
            r"The dual minimizes \(b^T y\).",
        ],
        0,
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        3,
        r"Minimize \(-6x - 2y\) subject to \(x + y + s = 5\) and \(2x + y + t = 8\), with all four variables nonnegative. What is the optimal value?",
        -24,
        "1",
        r"The dual maximizes \(5 y_1 + 8 y_2\) subject to \(y_1 + 2 y_2 \le -6\), \(y_1 + y_2 \le -2\), \(y_1 \le 0\), and \(y_2 \le 0\). The point \(y_1 = 0\), \(y_2 = -3\) is feasible and has value \(-24\). The primal point \(x = 4\), \(y = 0\), \(s = 1\), \(t = 0\) has the same cost, so both are optimal. Reporting \(24\) drops the sign. Reporting \(-12\) is the cost of the feasible but suboptimal point \(x = 2\), \(y = 0\). Reporting \(-3\) is one dual coordinate.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.mc(
        3,
        r"Weak duality for this standard-form pair says that for every primal-feasible \(x\) and dual-feasible \(y\),",
        [
            r"\(b^T y \le c^T x\)",
            r"\(b^T y \ge c^T x\)",
            "the two objectives are equal even when complementary slackness fails",
            "the dual is unbounded whenever the primal is feasible",
        ],
        0,
        r"A feasible pair cannot put the dual objective above the primal cost. The difference \(c^T x - b^T y\) equals the sum of complementary products, which is nonnegative. Equality needs those products to vanish. It is not automatic. A feasible primal makes the dual bounded above, by that same inequality. It does not make the dual unbounded.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        r"A proposed primal point has cost \(-18\), and a proposed dual point has value \(-10\). For a minimization primal,",
        [
            "the two points cannot both be feasible",
            "the pair proves optimality",
            "the primal point is optimal",
            "the dual point is optimal",
        ],
        0,
        r"Weak duality requires the dual value to be at most the primal cost. Here \(-10 > -18\), so the inequality is the wrong way around. At least one of the two points is infeasible. Optimality would need a feasible pair with equal values. Neither number alone is a certificate, because the comparison already forbids the pair.",
        fig=FALL,
        alt=A_FALL,
        preview=P_AFF,
    )
    b.num(
        4,
        r"In the program of minimizing \(-6x - 2y\) subject to \(x + y + s = 5\) and \(2x + y + t = 8\), the point \((x, y, s, t) = (2, 0, 3, 4)\) is primal feasible and \((y_1, y_2) = (0, -3)\) is dual feasible. The duality gap is the primal cost minus the dual objective. What is that gap?",
        12,
        "1",
        r"The primal cost is \(-6 \cdot 2 + (-2) \cdot 0 = -12\). The dual objective is \(5 \cdot 0 + 8 \cdot (-3) = -24\). The gap is \(-12 - (-24) = 12\). Reporting \(-12\) or \(-24\) gives one objective and not the difference. Reporting \(36\) adds the absolute values. The gap is positive, so this primal point is not optimal, even though the dual point happens to be.",
        fig=BASIS,
        alt=A_BASIS,
        preview=P_IP,
    )
    b.mc(
        4,
        "At an optimal standard-form basis, complementary slackness says",
        [
            "every dual slack is positive",
            r"the equality \(Ax = b\) may be dropped",
            "each positive primal variable has zero dual slack",
            "the equality multipliers must be nonnegative",
        ],
        2,
        r"The product of each primal variable with its dual slack is zero, so a positive variable forces that slack to vanish. The other dual slacks may be positive. Those belong to primal zeros. The equality \(Ax = b\) is primal feasibility, not something slackness removes. Equality multipliers are free in the Lagrangian. Nonnegativity is for the inequality slacks, not for \(y\).",
        fig=PAIR,
        alt=A_PAIR,
        preview=P_AFF,
    )
    b.save()


def bank_proj():
    b = Bank("projection-affine-halfspace-kkt")
    b.mc(
        1,
        "The Euclidean projection of a point that already lies in a closed half-space is",
        [
            "the point itself",
            "always the projection of that point onto the bounding hyperplane",
            "the origin",
            "undefined until the multiplier is negative",
        ],
        0,
        r"If the point satisfies the inequality, it is feasible for the projection problem and the objective \(\tfrac12\lVert x - z\rVert^2\) is already zero there. Nothing closer exists. Moving it to the boundary increases the distance. The origin is the projection only when the origin is the nearest feasible point. A negative multiplier is not dual feasible for the inequality, so the projection does not wait for one.",
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        1,
        r"Project \((5, 3)\) onto the half-space \(x \le 2\). The objective is \(\tfrac12\lVert x - z\rVert^2\). What is the squared Euclidean distance from the point to its projection?",
        9,
        "1",
        r"The point has first coordinate \(5 > 2\), so it is outside. Stationarity writes the projection as \((5, 3) - \nu(1, 0)\). The bound forces the first coordinate to \(2\), hence \(\nu = 3\) and the projection is \((2, 3)\). The squared distance is \(3^2 + 0^2 = 9\). Reporting \(3\) gives the multiplier. Reporting \(2\) gives the bound. Reporting \(5\) gives the original coordinate. The second coordinate is unchanged because the normal is \((1, 0)\).",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"For the equality \(a^T x = \beta\) with \(a \ne 0\), stationarity of \(\tfrac12\lVert x - z\rVert^2\) says",
        [
            r"\(x = z\) and the constraint is ignored",
            r"\(a\) must be the zero vector",
            r"\(x - z + \nu a = 0\) for some scalar \(\nu\), with no sign required of \(\nu\)",
            r"\(\nu\) must be nonnegative",
        ],
        2,
        r"The gradient of the squared distance is \(x - z\), and the constraint gradient is \(a\). Stationarity puts their sum, with a free multiplier, at zero. The multiplier is free because the constraint is an equality. Nonnegativity would be the inequality case. Ignoring the constraint leaves \(x = z\), which meets the equality only when \(z\) is already on it. A zero \(a\) is the rank failure the formula excludes.",
        fig=ARR,
        alt=A_ARR,
    )
    b.order(
        2,
        r"Put these steps in the order that projects \(z\) onto the line \(a^T x = \beta\). Each step uses the previous result.",
        [
            r"Check that \(a\) is not the zero vector, so the constraint gradient has full rank.",
            r"Write stationarity as \(x = z - \nu a\).",
            r"Substitute that expression into \(a^T x = \beta\) and solve \(\nu = (a^T z - \beta)/(a^T a)\).",
            r"Insert that multiplier back into \(x = z - \nu a\).",
        ],
        r"The rank check is the license for a multiplier. Stationarity then expresses the unknown point through that multiplier. The equality determines the multiplier, because it is the only remaining scalar equation. Substituting back produces the point. Solving for \(\nu\) before stationarity has not yet related \(x\) to \(z\). Skipping the rank check leaves a zero denominator when \(a = 0\).",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"Project \((5, 3)\) onto \(x \le 2\). The candidate is \((2, 3)\) with multiplier \(\nu = 3\) on \(x - 2 \le 0\). Which claims hold?",
        [
            r"Stationarity: \((2, 3) - (5, 3) + 3(1, 0) = (0, 0)\).",
            r"The candidate lies on the line \(x = 2\).",
            "The multiplier is nonnegative.",
            r"The original point \((5, 3)\) already satisfies \(x \le 2\).",
            "Complementary slackness holds, because the inequality is active.",
        ],
        [0, 1, 2, 4],
        r"The residual \((2, 3) - (5, 3)\) equals \(-3(1, 0)\), which is stationarity with \(\nu = 3\)."
        "\n"
        r"• The first coordinate is the bound, and \(3 \ge 0\)."
        "\n"
        r"• The product of the multiplier with the slack is zero."
        "\n"
        r"• The original point has first coordinate \(5\), so it is outside. That is why the multiplier is not zero.",
        fig=HALF,
        alt=A_HALF,
    )
    b.sym(
        2,
        r"Project the point \((p, q)\) onto the line \(a x + b y = r\). In stationarity the projection is \((p, q) - \nu (a, b)\). The multiplier \(\nu\) equals",
        "(a*p+b*q-r)/(a*a+b*b)",
        {"a": (1, 2), "b": (1, 2), "p": (3, 5), "q": (3, 5), "r": (0.5, 1.5)},
        r"Stationarity is \((p, q) - \nu(a, b)\) on the line. Dot both sides with \((a, b)\): \(a p + b q - \nu(a^2 + b^2) = r\), so \(\nu = (a p + b q - r)/(a^2 + b^2)\). Every name is used. On the declared ranges the denominator is positive and the multiplier is positive. The opposite sign projects to the other side of the line. Dropping the denominator leaves a quantity with the wrong dimension.",
        alternates=["(a*p+b*q-r)/(a**2+b**2)"],
        fig=PAIR,
        alt=A_PAIR,
    )
    b.find_error(
        3,
        r"A note projects \((5, 3)\) onto the half-space \(x \le 2\). Exactly one step is a false claim.",
        [
            r"The trial point has first coordinate \(5 > 2\), so it lies outside the half-space.",
            r"The projection is therefore the projection onto the line \(x = 2\).",
            r"That projection is \((2, 3)\).",
            "The multiplier is negative because the point was outside.",
        ],
        3,
        r"The point is outside, so the inequality is active at the projection, and the projection onto the bounding line is \((2, 3)\). The multiplier in \(x = z - \nu a\) is \(+3\), not a negative number. Outside the half-space the inequality multiplier is nonnegative. A negative multiplier would step to the infeasible side of the line.",
        [
            r"Outside the half-space the inequality multiplier is positive. Here it equals \(3\).",
            r"The point \((5, 3)\) is already inside \(x \le 2\).",
            r"The projection onto the line is not \((2, 3)\).",
        ],
        0,
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        3,
        r"Project \((1, 1)\) onto the line \(x + y = 6\). The objective is \(\tfrac12\lVert x - z\rVert^2\). What is the squared distance from \((1, 1)\) to the projection?",
        8,
        "1",
        r"The normal is \((1, 1)\), with squared length \(2\). The multiplier is \((1 + 1 - 6)/2 = -2\). The projection is \((1, 1) - (-2)(1, 1) = (3, 3)\). The squared distance is \(2^2 + 2^2 = 8\). Reporting \(-2\) gives the multiplier. Reporting \(3\) gives a coordinate of the projection. Reporting \(6\) gives the right-hand side. The negative multiplier is allowed because the constraint is an equality.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        3,
        r"The closed form that uses \((AA^T)^{-1}\) for projection onto \(\{x : Ax = b\}\) requires",
        [
            r"\(A\) to be square",
            r"\(A\) to have full row rank",
            r"\(A\) to have a zero row",
            r"\(b\) to be the zero vector",
        ],
        1,
        r"Full row rank makes \(AA^T\) invertible, which is the Gram matrix of the rows. The matrix \(A\) may be wide. Square is a special case, not the requirement. A zero row drops the rank and makes \(AA^T\) singular. The right-hand side \(b\) can be any compatible vector. It is not required to vanish.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.mc(
        4,
        r"When \(z\) lies strictly outside the half-space \(a^T x \le \beta\), the vector \(z - x^\star\) is",
        [
            r"a positive multiple of \(a\)",
            r"orthogonal to \(a\)",
            "the zero vector",
            r"a negative multiple of \(a\)",
        ],
        0,
        r"Stationarity reads \(z - x^\star = \nu a\) with \(\nu > 0\) when the point is strictly outside and the constraint is active. The residual points along the outward normal \(a\). It is not orthogonal to \(a\). That would be a tangent step. It is not zero, because \(z\) itself is infeasible. A negative multiple would step further outside.",
        fig=ARR,
        alt=A_ARR,
        preview=P_ONTO,
    )
    b.num(
        4,
        r"Project \((6, 2)\) onto the half-space \(x \le 1\). What is the squared distance from the point to its projection?",
        25,
        "1",
        r"The point is outside. The normal is \((1, 0)\), so the projection is \((1, 2)\) and the multiplier is \(5\). The squared distance is \(5^2 = 25\). Reporting \(5\) gives the multiplier. Reporting \(1\) or \(2\) gives a coordinate of the projection. Reporting \(6\) gives the original first coordinate. The second coordinate does not move.",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_GRAD,
    )
    b.mc(
        4,
        r"When \(a^T z > \beta\), the projection of \(z\) onto \(\{x : a^T x \le \beta\}\) equals",
        [
            r"\(z - a\,(a^T z - \beta)/(a^T a)\)",
            r"\(z + a\,(a^T z - \beta)/(a^T a)\)",
            r"the origin, regardless of \(z\)",
            r"\(z\), leaving the point outside the half-space",
        ],
        0,
        r"Outside, the inequality is active and the multiplier \((a^T z - \beta)/(a^T a)\) is positive. Subtracting \(\nu a\) lands on the hyperplane. Adding \(\nu a\) steps the wrong way and stays outside. The origin is not the projection unless the formula says so. Returning \(z\) leaves an infeasible point, which cannot be the minimizer of the distance.",
        fig=HALF,
        alt=A_HALF,
        preview=P_SCALED,
    )
    b.save()



def bank_lls():
    b = Bank("linear-least-squares")
    b.mc(
        1,
        r"When \(A\) has full column rank, the least-squares solution of \(Ax \approx b\) is the solution of",
        [
            r"\(A^T A x = A^T b\)",
            r"\(Ax = b\), which is always a consistent square system",
            r"\(A A^T x = b\)",
            r"\(x = 0\), because the residual must vanish",
        ],
        0,
        r"The gradient of \(\lVert Ax - b\rVert^2\) is \(2 A^T(Ax - b)\). Setting it to zero is the normal equation \(A^T A x = A^T b\). Full column rank makes \(A^T A\) invertible, so there is one solution. The system \(Ax = b\) is overdetermined and need not be consistent. \(AA^T\) is the Gram matrix of the rows, the wrong shape for a tall full-column-rank \(A\). The residual is zero only when \(b\) is in the column space.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.num(
        1,
        r"Four measurements of one unknown are \(2, 4, 6, 8\). The model is that unknown times a column of ones. What is the least-squares value?",
        5,
        "1",
        r"The normal equation is \(4 x = 2 + 4 + 6 + 8 = 20\), so \(x = 5\). That is the average. Reporting \(20\) gives the sum. Reporting \(8\) or \(2\) gives an endpoint. The residual is not zero: the four numbers are not equal. The column of ones has full column rank, so the average is the unique minimizer of the sum of squares.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        1,
        r"\(A^T A\) is positive definite exactly when",
        [
            r"\(A\) has more rows than columns, with no further condition",
            r"\(A\) is square",
            r"\(A\) has full column rank",
            r"\(b\) is the zero vector",
        ],
        2,
        r"\(x^T A^T A x = \lVert Ax\rVert^2\) is positive for every \(x \ne 0\) exactly when \(Ax = 0\) has only the zero solution, which is full column rank. Extra rows do not prevent two columns from being copies of each other. A square matrix can be singular. The right-hand side \(b\) does not enter \(A^T A\).",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.order(
        2,
        r"Put these steps in the order that derives the normal equations for \(\lVert Ax - b\rVert^2\). Each step uses the previous result.",
        [
            r"Write the objective as \((Ax - b)^T(Ax - b)\).",
            r"Differentiate it in \(x\). The gradient is \(2 A^T(Ax - b)\).",
            "Set that gradient equal to zero.",
            r"Cancel the nonzero factor \(2\) and rearrange to \(A^T A x = A^T b\).",
        ],
        r"The objective is expanded before it is differentiated. The gradient is the quantity set to zero. Canceling \(2\) is legal only after that equation exists, and the rearrangement is the normal equation. Setting \(Ax - b = 0\) instead of the gradient to zero demands an exact fit the data may not have. Differentiating before writing the objective has nothing to differentiate.",
        fig=FALL,
        alt=A_FALL,
    )
    b.multi(
        2,
        r"Let \(A\) have rows \((1, 0)\), \((1, 0)\), \((0, 1)\), \((0, 1)\) and let \(b = (3, 5, 2, 6)\). The least-squares solution is \((4, 4)\). Which claims hold?",
        [
            r"\(A^T A x = A^T b\) holds at \((4, 4)\).",
            r"\(Ax\) equals \(b\) exactly.",
            r"The residual is orthogonal to both columns of \(A\).",
            r"\(A\) has full column rank.",
            r"The Hessian of \(\tfrac12\lVert Ax - b\rVert^2\) is singular.",
        ],
        [0, 2, 3],
        r"\(A^T A = 2I\), and \(A^T b = (8, 8)\), so the normal equation gives \((4, 4)\)."
        "\n"
        r"• The residual \((-1, 1, -2, 2)\) dots to zero with each column, which is \(A^T(Ax - b) = 0\)."
        "\n"
        r"• \(A^T A\) is invertible, so the columns are independent and the Hessian \(A^T A\) is not singular."
        "\n"
        r"• \(Ax = (4, 4, 4, 4)\) is not \(b\).",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.sym(
        2,
        r"A single column \((p, q)\) and a right-hand side \((u, v)\) give a scalar unknown. The normal-equation solution equals",
        "(p*u+q*v)/(p*p+q*q)",
        {"p": (1, 3), "q": (1, 3), "u": (1, 4), "v": (1, 4)},
        r"The normal equation is \((p^2 + q^2) x = p u + q v\). The column is nonzero on the declared ranges, so the division is legal and every name is used. This is the same number as the orthogonal projection of \((u, v)\) onto the span of \((p, q)\), divided out to a coefficient. Swapping the denominator for \(p + q\) is not the Gram entry. Dropping a product in the numerator drops one row of \(A^T b\).",
        alternates=["(p*u+q*v)/(p**2+q**2)"],
        fig=ARR,
        alt=A_ARR,
    )
    b.find_error(
        3,
        r"A note derives the normal equations. Exactly one step is a false claim.",
        [
            r"The gradient of \(\lVert Ax - b\rVert^2\) is \(2 A^T(Ax - b)\).",
            r"Setting that gradient to zero is equivalent to \(A^T A x = A^T b\).",
            r"The same equation can be written \(A^T A x = b\).",
            r"Full column rank makes \(A^T A\) invertible.",
        ],
        2,
        r"The gradient formula is right, and clearing it really does produce \(A^T A x = A^T b\). Full column rank really does invert \(A^T A\). The false step replaces \(A^T b\) by \(b\). Those two vectors have different shapes whenever \(A\) is not square, and they are different even when a square \(A\) is invertible. The right-hand side has to be \(A^T b\).",
        [
            r"The right-hand side is \(A^T b\), not \(b\).",
            r"The gradient is \(2A(Ax - b)\), without a transpose.",
            r"Full column rank leaves \(A^T A\) singular.",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"Let \(A\) have rows \((1, 0)\), \((1, 0)\), \((0, 1)\), \((0, 1)\), and let \(b = (3, 5, 2, 6)\). The least-squares solution is \((4, 4)\). What is the squared residual \(\lVert Ax - b\rVert^2\)?",
        10,
        "1",
        r"The fitted vector is \((4, 4, 4, 4)\). The residual is \((-1, 1, -2, 2)\), and the sum of squares is \(1 + 1 + 4 + 4 = 10\). Reporting \(4\) gives a coordinate of the solution. Reporting \(8\) is \(A^T b\)'s common entry. Reporting \(0\) would be an exact fit, and these four numbers are not constant on each column. The normal equation already fixed the solution. This number is only the objective at that solution.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        3,
        r"When \(A\) has full column rank, the least-squares solution is",
        [
            r"\((A^T A)^{-1} A^T b\)",
            r"\(A^T (A A^T)^{-1} b\), the formula for a full-row-rank matrix",
            r"\(A^{-1} b\), whether or not \(A\) is square",
            r"\((A A^T)^{-1} b\)",
        ],
        0,
        r"Full column rank inverts the smaller Gram matrix \(A^T A\), and the solution is \((A^T A)^{-1} A^T b\). The formula with \((AA^T)^{-1}\) belongs to a full-row-rank matrix, which is short and wide. A nonsquare \(A\) has no inverse. \((AA^T)^{-1} b\) is not even the right shape to be an \(x\) in the column space of a tall \(A\).",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.mc(
        4,
        "Which model, with parameters collected in one vector, is linear in those parameters?",
        [
            r"\(y = m t + c\), parameters \((m, c)\)",
            r"\(y = e^{m t}\), parameter \(m\)",
            r"\(y = \sin(m t)\), parameter \(m\)",
            r"\(y = t^{m}\), parameter \(m\)",
        ],
        0,
        r"A line is a dot product of \((m, c)\) with \((t, 1)\). The design matrix does not depend on the parameters. An exponential, a sine, or a power hides the parameter inside a nonlinear function. Those fits are nonlinear least squares. The line, once there are more points than coefficients, is an ordinary normal equation.",
        fig=RISE,
        alt=A_RISE,
        preview=P_FIT,
    )
    b.num(
        4,
        r"Fit \(y = a + b t\) to the three points \((t, y) = (1, 2),\ (2, 3),\ (3, 6)\) by least squares. What is the slope \(b\)?",
        2,
        "1",
        r"The normal matrix is \(\begin{bmatrix} 3 & 6 \\ 6 & 14 \end{bmatrix}\) and the right-hand side is \((11, 26)\). The second unknown comes out to \(2\), and the intercept is \(-1/3\). Check: \(3a + 6b = 11\) becomes \(3a + 12 = 11\) when \(b = 2\), so \(a = -1/3\), and \(6a + 14b = -2 + 28 = 26\). Reporting \(-1/3\) gives the intercept. Reporting \(6\) or \(3\) gives a data coordinate. The fit is not exact, but the slope of the least-squares line is \(2\).",
        fig=SEG,
        alt=A_SEG,
        preview=P_NLS,
    )
    b.mc(
        4,
        r"If the columns of \(A\) are linearly dependent, the normal equations",
        [
            "have no solution",
            "have infinitely many solutions",
            r"keep \(A^T A\) invertible",
            "force the residual to be zero",
        ],
        1,
        r"\(A^T b\) is always in the column space of \(A^T A\), so the normal equations stay consistent. Dependence makes \(A^T A\) singular, and the solution set is a translate of the null space: infinitely many solutions, all with the same residual. The residual is zero only when \(b\) is in the column space of \(A\). Dependence does not force that.",
        fig=DENT,
        alt=A_DENT,
        preview=P_KAL,
    )
    b.save()


def bank_fit():
    b = Bank("least-squares-data-fitting")
    b.mc(
        1,
        "A model is linear in its parameters when, at each fixed input,",
        [
            "the prediction is a linear function of the input",
            "every parameter sits inside an exponential",
            "the prediction is a linear function of the parameter vector",
            "the residual is required to be zero",
        ],
        2,
        r"Linearity is in the parameters, not in the input. A quadratic polynomial in \(t\) is nonlinear as a curve and still linear in its coefficients, because each coefficient multiplies a column that does not depend on the coefficients. An exponential of a parameter is nonlinear in that parameter. An exact residual is interpolation, not the definition of linearity.",
        fig=RISE,
        alt=A_RISE,
    )
    b.num(
        1,
        r"The model \(y = a + b t + c t^2\) is fit by least squares. At least how many distinct input values does it need for the design matrix to have full column rank?",
        3,
        "1",
        r"There are three coefficients, so the design matrix has three columns: \(1\), \(t\), and \(t^2\). A Vandermonde matrix on distinct inputs has full column rank once there are three of them. Two distinct inputs leave the three columns dependent. Reporting \(2\) counts a line, not a quadratic. Reporting \(1\) is a single parameter. Reporting \(6\) doubles the count. More than three points is allowed and is the usual overdetermined fit. Three is the minimum for a unique coefficient vector.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.mc(
        1,
        r"For the model \(a + b t + c t^2\), the design-matrix row at an input \(t\) is",
        [
            r"\((a, b, c)\)",
            r"\((t, t, t)\)",
            r"\((1, t, t^2)\)",
            r"\((1, 1, 1)\)",
        ],
        2,
        r"The prediction is the dot product of \((a, b, c)\) with \((1, t, t^2)\). The row is built from the input alone. Putting the parameters in the row would make the matrix depend on the unknown. Repeating \(t\) three times, or writing a row of ones, describes a different model. At \(t = 2\) the correct row is \((1, 2, 4)\).",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.order(
        2,
        "Put these steps in the order of one linear least-squares fit of a line to a list of points. Each step uses the previous result.",
        [
            "Choose the parameter vector as intercept and slope.",
            r"Build one row \((1, t_i)\) for each point, using that parameterization.",
            r"Stack the rows into \(A\) and stack the measured values into \(b\).",
            r"Solve the normal equations \(A^T A x = A^T b\).",
        ],
        r"The parameter vector decides what a row means, so it comes first. The rows are then filled from the inputs. Stacking produces the matrix and the right-hand side that the normal equation uses. Solving before the matrix exists has no system. Putting the measured \(y\) into the row would mix the data into \(A\) and leave \(b\) empty.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which models are linear in their parameters? The input is \(t\), and the parameters are the named coefficients.",
        [
            r"\(y = a + b t\).",
            r"\(y = a + b t + c t^2\).",
            r"\(y = a e^{b t}\), parameters \(a\) and \(b\).",
            r"\(y = a \sin t + b \cos t\).",
            r"\(y = e^{a + b t}\).",
        ],
        [0, 1, 3],
        r"A prediction that is a dot product of the parameter vector with a vector built only from \(t\) is linear in the parameters."
        "\n"
        r"• The line, the quadratic polynomial, and the sine-cosine combination all have that form."
        "\n"
        r"• \(a e^{b t}\) is nonlinear in \(b\)."
        "\n"
        r"• \(e^{a + b t}\) is nonlinear in both \(a\) and \(b\).",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.sym(
        2,
        r"A model that is linear in its parameters predicts \(a + b t\) at the input \(t\). That prediction equals",
        "a+b*t",
        {"a": (1, 3), "b": (1, 3), "t": (1, 3)},
        r"The prediction is the dot product of \((a, b)\) with \((1, t)\), which is \(a + b t\). All three names appear. On the declared ranges the value is positive. The product \(a b t\) would be bilinear in a way this model is not. The quotient \(a/t + b\) swaps the role of the input. The expression \(a + b + t\) treats the input as another parameter.",
        alternates=["b*t+a", "a+t*b"],
        fig=RISE,
        alt=A_RISE,
    )
    b.find_error(
        3,
        r"A note builds the design matrix of \(y = a + b t + c t^2\). Exactly one step is a false claim.",
        [
            "The model has three parameters, so each row has three entries.",
            r"The row at \(t = 1\) is \((1, 1, 1)\).",
            r"The row at \(t = 2\) is \((1, 2, 2)\).",
            r"For columns \(1\), \(t\), and \(t^2\), three distinct inputs make those columns independent.",
        ],
        2,
        r"Three parameters give three entries, and at \(t = 1\) the powers \(1, t, t^2\) really are \((1, 1, 1)\). Three distinct inputs make a Vandermonde matrix invertible for this polynomial. The false row is the one at \(t = 2\): \(2^2 = 4\), so the row is \((1, 2, 4)\). Writing \(2\) in the last slot repeats the middle column's entry and is not \(t^2\).",
        [
            r"At \(t = 2\) the row is \((1, 2, 4)\), because the last entry is \(t^2\).",
            r"The row at \(t = 1\) should have been \((1, 1, 2)\).",
            "Three distinct inputs leave these three columns dependent.",
        ],
        0,
        fig=BASIS,
        alt=A_BASIS,
    )
    b.num(
        3,
        r"Fit \(y = a + b t\) to \((t, y) = (0, 1),\ (1, 2),\ (2, 5)\). What is the slope \(b\)?",
        2,
        "1",
        r"The normal matrix is \(\begin{bmatrix} 3 & 3 \\ 3 & 5 \end{bmatrix}\) and the right-hand side is \((8, 12)\). Subtracting the equations \(3a + 3b = 8\) and \(3a + 5b = 12\) gives \(2b = 4\), so \(b = 2\). The intercept is \(2/3\). Reporting \(2/3\) gives the intercept. Reporting \(5\) or \(1\) gives a data value. The slope is the coefficient of the column \((0, 1, 2)\).",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        3,
        r"Adding another point whose input \(t\) copies an input already in the design matrix",
        [
            "does not increase the rank of the design matrix",
            "always makes the fit exact",
            "removes one parameter",
            "makes the model nonlinear in its parameters",
        ],
        0,
        r"A repeated input repeats a row, or repeats it with a different measured value. A repeated row is in the span of the existing rows, so the column rank does not rise. The fit becomes exact only if the new measurement agrees with a prediction that was already perfect. The parameter count is a property of the model, not of one extra row. Repeating an input does not move a parameter inside a nonlinear function.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        4,
        r"The geometric circle \((x - a)^2 + (y - b)^2 = r^2\), with parameters \((a, b, r)\), compares with an algebraic rewrite as follows.",
        [
            r"Both forms are linear in \((a, b, r)\).",
            "A circle cannot be fit by least squares at all.",
            r"The geometric form is nonlinear in \((a, b, r)\), and a rewritten form can be linear in a different parameter vector.",
            "The design matrix of a circle is always square.",
        ],
        2,
        r"Expanding the geometric equation produces \(x^2 + y^2\) plus terms linear in new coefficients built from \(a\), \(b\), and \(r^2\). Those new coefficients are what a linear fit estimates. The original \((a, b, r)\) still enter the squared distance nonlinearly. The fit is possible. The design matrix is square only when the number of points equals the number of algebraic parameters. Extra points are the usual case.",
        fig=DENT,
        alt=A_DENT,
        preview=P_CIRC,
    )
    b.num(
        4,
        r"A model \(y = a + b t + c \sin t + d \cos t\) is linear in its parameters. How many parameters does it have?",
        4,
        "1",
        r"The columns are \(1\), \(t\), \(\sin t\), and \(\cos t\). That is four coefficients. Full column rank therefore needs at least four points whose rows are independent, and a sine and a cosine of the same \(t\) are different columns. Reporting \(2\) counts only the trigonometric terms. Reporting \(3\) drops one of them. Reporting \(8\) doubles the list. The input \(t\) is not a parameter.",
        fig=PAIR,
        alt=A_PAIR,
        preview=P_CIRC,
    )
    b.mc(
        4,
        "Once a circle has been rewritten so the unknowns appear linearly, fitting those unknowns is",
        [
            "a linear least-squares problem",
            r"still nonlinear, because \(x^2 + y^2\) is quadratic",
            "a linear program",
            "possible only when every point already lies on one common circle",
        ],
        0,
        r"The squares \(x^2 + y^2\) are computed from the data before the fit. They move to the right-hand side. What remains is linear in the new coefficients, so the normal equations apply. The problem is not a linear program: the objective is a sum of squares, not a linear cost. Points off the circle are allowed. They are why the residual is a sum of squares rather than a square system.",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_CIRC,
    )
    b.save()


def bank_nls():
    b = Bank("nonlinear-least-squares")
    b.mc(
        1,
        "A nonlinear least-squares problem minimizes",
        [
            "a sum of squares of residuals that depend nonlinearly on the parameters",
            "a residual that is linear in the parameters",
            "the residual vector in the 1-norm",
            "one linear equation in one unknown",
        ],
        0,
        r"The objective is a sum of squares. The nonlinearity is in how the residuals depend on the parameters. A residual that is linear in the parameters is ordinary linear least squares. The 1-norm is a different fitting criterion. One linear equation is not a sum of squares and need not be overdetermined.",
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        1,
        r"Let \(r(u, v) = (u^2 + v - 3,\ u + v^2 - 5)\). What is \(\lVert r(1, 1)\rVert^2\)?",
        10,
        "1",
        r"The residual is \((1 + 1 - 3,\ 1 + 1 - 5) = (-1, -3)\). The sum of squares is \(1 + 9 = 10\). Reporting \(4\) adds the two residual entries. Reporting \(3\) or \(1\) gives one absolute entry. The Jacobian is not needed for the objective value. It would be needed for a step that linearizes \(r\).",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        1,
        "The residual Jacobian is shaped as",
        [
            "one row per parameter and one column per residual",
            "a square matrix for every problem",
            "one row per residual and one column per parameter",
            "a matrix whose entries are the residual values",
        ],
        2,
        r"Each residual gets a row, and each parameter gets a column, matching the derivative of that residual with respect to that parameter. Swapping the shape confuses it with the Gram matrix \(J^T J\). The Jacobian is square only when there are as many residuals as parameters. Its entries are derivatives, not the residual values themselves.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.order(
        2,
        "Put these steps in the order that prepares a nonlinear least-squares problem at a current parameter vector. Each step uses the previous result.",
        [
            "Write one residual per measurement, as a function of the parameters.",
            "Differentiate each residual with respect to each parameter.",
            "Stack those derivatives into a Jacobian whose rows follow the residuals.",
            "Evaluate that Jacobian at the current parameter vector.",
        ],
        r"The residuals are the functions being differentiated, so they come first. The derivatives are then arranged so that row \(i\) belongs to residual \(i\). Evaluation is last because the Jacobian of a nonlinear residual depends on the point. Evaluating before the stacking has no matrix. Replacing the derivatives by the residual values produces a vector, not a Jacobian.",
        fig=ARR,
        alt=A_ARR,
    )
    b.multi(
        2,
        "Which residuals are nonlinear in the parameters? Inputs and measured values are fixed numbers.",
        [
            r"\(e^{a t} - y\), parameter \(a\).",
            r"\(a + b t - y\), parameters \(a\) and \(b\).",
            r"\((x - a)^2 + (y - b)^2 - R^2\), parameters \(a\), \(b\), and \(R\).",
            r"\(a \sin t + b \cos t - y\), parameters \(a\) and \(b\).",
            r"\(\sin(a t) - y\), parameter \(a\).",
        ],
        [0, 2, 4],
        r"A residual is nonlinear in a parameter when that parameter sits inside a nonlinear function."
        "\n"
        r"• The exponential of \(a t\), the squared distance with unknown center, and the sine of \(a t\) are nonlinear."
        "\n"
        r"• \(a + b t - y\) is affine in \((a, b)\)."
        "\n"
        r"• \(a \sin t + b \cos t - y\) is affine in \((a, b)\), because \(\sin t\) and \(\cos t\) are fixed columns.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.sym(
        2,
        r"One residual is \(p^2 - s\). Its square, the term it contributes to the least-squares objective, equals",
        "(p*p-s)**2",
        {"p": (2, 4), "s": (0.2, 0.8)},
        r"The objective adds the square of each residual, so this term is \((p^2 - s)^2\). Both names appear. On the declared ranges \(p^2 > s\), and the square is positive. The unsquared residual \(p^2 - s\) is not yet the objective term. Squaring only \(p\), or only \(s\), drops the subtraction inside the residual.",
        alternates=["(p**2-s)**2", "(p*p-s)*(p*p-s)"],
        fig=FALL,
        alt=A_FALL,
    )
    b.find_error(
        3,
        r"A note writes the Jacobian of \(r(u, v) = (u^2 + v - 3,\ u + v^2 - 5)\). Exactly one step is a false claim.",
        [
            r"The derivative of the first residual with respect to \(u\) is \(2u\).",
            r"The derivative of the first residual with respect to \(v\) is \(1\).",
            r"The derivative of the second residual with respect to \(u\) is \(2u\).",
            r"The derivative of the second residual with respect to \(v\) is \(2v\).",
        ],
        2,
        r"The first residual \(u^2 + v - 3\) really does have derivatives \(2u\) and \(1\). The second residual \(u + v^2 - 5\) has derivative \(1\) in \(u\) and \(2v\) in \(v\). The false step copies \(2u\) onto the second residual. That residual is linear in \(u\), so its \(u\)-derivative is \(1\).",
        [
            r"The second residual is linear in \(u\), so that derivative is \(1\), not \(2u\).",
            r"The first residual's derivative in \(v\) is \(2v\).",
            r"The second residual's derivative in \(v\) is \(1\).",
        ],
        0,
        fig=BASIS,
        alt=A_BASIS,
    )
    b.num(
        3,
        r"Using \(r(u, v) = (u^2 + v - 3,\ u + v^2 - 5)\), what is \(\lVert r(2, 1)\rVert^2\)?",
        8,
        "1",
        r"The residual is \((4 + 1 - 3,\ 2 + 1 - 5) = (2, -2)\). The sum of squares is \(4 + 4 = 8\). Reporting \(2\) gives one absolute entry. Reporting \(0\) would mean a root, and neither entry vanishes. Reporting \(16\) squares the sum of the entries instead of summing the squares. The Jacobian at this point is \(\begin{bmatrix} 4 & 1 \\ 1 & 2 \end{bmatrix}\), which is not the objective.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        3,
        "If every residual is affine in the parameters, the nonlinear least-squares problem",
        [
            "reduces to linear least squares",
            "has no Jacobian",
            "cannot use a normal equation",
            "always has a zero residual",
        ],
        0,
        r"An affine residual has a constant Jacobian, and the objective is an ordinary squared linear residual plus a constant shift that can be absorbed into \(b\). The Jacobian exists. It is that constant matrix. The normal equations apply to it. A zero residual still requires \(b\) to lie in the column space. Affinity does not grant that.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        4,
        r"One step that linearizes the residual at the current parameters replaces \(r(x + d)\) by",
        [
            r"\(r(x) + J(x)\, d\)",
            r"\(r(x) + r(x)\, d\)",
            r"the full second-derivative model of the objective, with every second derivative of \(r\) kept",
            r"\(J(x)\, d\), dropping \(r(x)\)",
        ],
        0,
        r"The first-order model of a vector residual is the residual plus the Jacobian times the step. Multiplying by the residual itself is not a derivative. Keeping every second derivative of \(r\) is Newton's method on the objective, a different model. Dropping \(r(x)\) asks the step to fit zero instead of the current residual, which solves the wrong linear least-squares problem.",
        fig=ARR,
        alt=A_ARR,
        preview=P_GN,
    )
    b.num(
        4,
        r"A residual for a circle of radius \(\rho\), centered at \((1, 1)\), at the data point \((4, 1)\), is \((4 - 1)^2 + (1 - 1)^2 - \rho^2\). At \(\rho = 2\), what is that residual?",
        5,
        "1",
        r"The squared distance from the center to the point is \(9 + 0 = 9\). Subtract \(\rho^2 = 4\). The residual is \(5\). Reporting \(9\) forgets the radius term. Reporting \(4\) gives \(\rho^2\). Reporting \(3\) gives the horizontal gap. The residual is not the Euclidean distance minus \(\rho\). It is the algebraic gap of the squared radius, and at this number it equals \(5\).",
        fig=DENT,
        alt=A_DENT,
        preview=P_CIRC,
    )
    b.mc(
        4,
        "If the residual Jacobian at the current point has full column rank, then",
        [
            "the linearized least-squares model in the step has a positive definite Gram matrix",
            "every Jacobian is square",
            "the residual itself must be linear",
            "the Jacobian does not depend on the parameters",
        ],
        0,
        r"Full column rank makes \(J^T J\) positive definite, so the linear least-squares model in the step has one minimizer. The Jacobian can still be tall. Full column rank does not make it square. The residual can be nonlinear. That is why \(J\) had to be evaluated at a point. A constant Jacobian is the affine case, not a consequence of rank.",
        fig=PAIR,
        alt=A_PAIR,
        preview=P_INC,
    )
    b.save()


def bank_circle():
    b = Bank("circle-fitting-least-squares")
    b.mc(
        1,
        r"The algebraic circle equation \(x^2 + y^2 + c x + d y + e = 0\) is",
        [
            r"linear in the parameters \((c, d, e)\)",
            "linear in the geometric parameters (center coordinates and radius)",
            "a constraint with no parameters",
            r"quadratic in the parameter \(c\)",
        ],
        0,
        r"Each of \(c\), \(d\), and \(e\) multiplies data, or stands alone. None of them is squared. The geometric center and radius enter the expanded equation through products and a square, which is why they are not the linear parameters. The equation does have parameters. The quadratic terms are \(x^2\) and \(y^2\), and those are data.",
        fig=DENT,
        alt=A_DENT,
    )
    b.num(
        1,
        r"At the point \((4, 1)\), with parameters \(c = -2\), \(d = -2\), and \(e = -1\), what is the algebraic residual \(x^2 + y^2 + c x + d y + e\)?",
        6,
        "1",
        r"The data term is \(16 + 1 = 17\). The linear terms are \(-2 \cdot 4 + (-2) \cdot 1 = -10\). Adding \(e = -1\) leaves \(17 - 10 - 1 = 6\). Reporting \(17\) stops after the squares. Reporting \(-10\) is only the linear part. Reporting \(-1\) is \(e\). The residual is the number a linear fit would be trying to drive toward zero.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        1,
        r"After \((c, d, e)\) have been fit, the center of the circle is",
        [
            r"\((c, d)\)",
            r"\((-c/2,\ -d/2)\)",
            r"\((c^2,\ d^2)\)",
            r"\((e,\ e)\)",
        ],
        1,
        r"Expanding \((x - a)^2 + (y - b)^2 - r^2\) gives the coefficient \(-2a\) on \(x\) and \(-2b\) on \(y\). Those coefficients are \(c\) and \(d\), so the center is \((-c/2, -d/2)\). Using \((c, d)\) forgets the factor \(-1/2\). Squaring the coefficients, or reading the center from \(e\), assigns the constant term a role it does not have. The constant term carries \(a^2 + b^2 - r^2\).",
        fig=ARR,
        alt=A_ARR,
    )
    b.order(
        2,
        "Put these steps in the order that turns a geometric circle into a linear least-squares fit. Each step uses the previous result.",
        [
            r"Expand \((x - a)^2 + (y - b)^2 - r^2 = 0\).",
            r"Collect \(x^2 + y^2\), the terms linear in \(x\) and in \(y\), and the constant term.",
            r"Rename those collected coefficients as parameters \((c, d, e)\).",
            r"Fit \((c, d, e)\) by linear least squares, then recover the center and the radius from them.",
        ],
        r"The geometric equation is expanded before its terms can be collected. The collected coefficients are the quantities being renamed. The linear fit uses the renamed parameters, and the center and radius are decoded after that fit. Fitting \((a, b, r)\) directly skips the expansion and leaves a nonlinear residual. Recovering the center before the coefficients exist has no \(c\) or \(d\) to convert.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        "In the algebraic circle fit, which quantities are the linear parameters?",
        [
            r"\(c\) in \(x^2 + y^2 + c x + d y + e\).",
            r"\(d\) in that same expression.",
            r"\(e\) in that same expression.",
            r"The radius \(r\) in \((x - a)^2 + (y - b)^2 = r^2\).",
            r"The center coordinate \(a\) in \((x - a)^2\).",
        ],
        [0, 1, 2],
        r"The algebraic expression is a dot product of \((c, d, e)\) with \((x, y, 1)\), plus the data term \(x^2 + y^2\)."
        "\n"
        r"• \(c\), \(d\), and \(e\) are the linear parameters."
        "\n"
        r"• The radius \(r\) is squared in the geometric equation, and the center coordinate \(a\) is squared and also multiplied by \(x\)."
        "\n"
        r"• Neither \(r\) nor \(a\) is a linear parameter of that geometric form.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.sym(
        2,
        r"The center recovered from \((c, d)\) is \((-c/2, -d/2)\), and the constant parameter is \(k\). The squared radius equals",
        "c*c/4+d*d/4-k",
        {"c": (2, 4), "d": (2, 4), "k": (0.2, 0.5)},
        r"The constant term is \(k = a^2 + b^2 - r^2\) with \(a = -c/2\) and \(b = -d/2\). Solving for the squared radius gives \(c^2/4 + d^2/4 - k\). All three names appear. On the declared ranges the value is positive, so a real radius exists. Adding \(k\) instead of subtracting it uses the wrong sign from the expansion. Dropping the fourths forgets that the center coordinates are half the coefficients.",
        alternates=["(c*c+d*d)/4-k", "c**2/4+d**2/4-k"],
        fig=FALL,
        alt=A_FALL,
    )
    b.find_error(
        3,
        r"A note expands \((x - a)^2 + (y - b)^2 - r^2 = 0\). Exactly one step is a false claim.",
        [
            r"The expansion contains \(x^2 - 2 a x + a^2 + y^2 - 2 b y + b^2 - r^2\).",
            r"The coefficient of \(x\) is \(-2a\), so \(c = -2a\).",
            r"The constant term \(e\) equals \(a^2 + b^2 + r^2\).",
            r"The squared radius recovered from a center and a constant term is \(a^2 + b^2 - e\).",
        ],
        2,
        r"The expansion and the identification \(c = -2a\) are correct, and solving \(e = a^2 + b^2 - r^2\) for the squared radius really does give \(a^2 + b^2 - e\). The false claim puts a plus in front of \(r^2\). The radius term was subtracted in the geometric equation, so it is subtracted in \(e\).",
        [
            r"The constant term is \(a^2 + b^2 - r^2\), so the radius term is subtracted.",
            r"The coefficient of \(x\) is \(+2a\).",
            r"The squared radius is \(e - a^2 - b^2\).",
        ],
        0,
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        3,
        r"Parameters \(c = -4\), \(d = -6\), and \(e = 4\) have been fit. What is the squared radius?",
        9,
        "1",
        r"The center is \((2, 3)\). Then \(r^2 = 4 + 9 - 4 = 9\). Reporting \(2\) or \(3\) gives a center coordinate. Reporting \(4\) gives \(e\), or the canceled square. Reporting \(13\) adds \(e\) instead of subtracting it. A positive squared radius is what makes the algebraic solution a real circle.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        3,
        r"The algebraic fit minimizes the sum of squares of \(x^2 + y^2 + c x + d y + e\). That objective is",
        [
            "not the sum of squared geometric distances to the circle, though the unknowns enter it linearly",
            "exactly the sum of squared geometric distances",
            "a linear program",
            "defined only for three points",
        ],
        0,
        r"The geometric residual is the distance from a point to the center, minus the radius. The algebraic residual is a quadratic polynomial in the coordinates. They vanish on the same circle, and they are different away from it. The algebraic objective is still a sum of squares, so it is least squares rather than a linear program, and it accepts any number of points.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        r"Keeping the geometric residual, the distance from the point to the center minus the radius, means the residual in \((a, b, r)\) is",
        [
            r"\(\sqrt{(x - a)^2 + (y - b)^2} - r\)",
            r"\(x^2 + y^2 + c x + d y + e\)",
            r"\(a + b + r\)",
            r"\(x + y\)",
        ],
        0,
        r"The geometric residual subtracts the radius from the Euclidean distance to the center. The algebraic polynomial is the rewritten form, linear in different parameters. A sum of the parameters, or a sum of the coordinates, is neither distance. The geometric residual is nonlinear in \((a, b, r)\), which is why a linear algebra fit uses the other form.",
        fig=ARR,
        alt=A_ARR,
        preview=P_GN,
    )
    b.num(
        4,
        r"At \((5, 1)\), with \(c = -4\), \(d = -2\), and \(e = 3\), what is the algebraic residual \(x^2 + y^2 + c x + d y + e\)?",
        7,
        "1",
        r"The squares sum to \(25 + 1 = 26\). The other terms are \(-4 \cdot 5 + (-2) \cdot 1 + 3 = -20 - 2 + 3 = -19\). The residual is \(26 - 19 = 7\). Reporting \(26\) stops after the squares. Reporting \(-19\) is only the parameter part. Reporting \(5\) is a coordinate. This is one row of the linear least-squares residual for \((c, d, e)\).",
        fig=SEG,
        alt=A_SEG,
        preview=P_LM,
    )
    b.mc(
        4,
        r"With more points than the three algebraic parameters, the linear least-squares solution for \((c, d, e)\) is",
        [
            "undefined, because a circle needs exactly three points",
            "the average of the points, used as the center",
            "the minimizer of the sum of squared algebraic residuals",
            "always a perfect geometric fit, with every geometric residual equal to zero",
        ],
        2,
        r"Extra points make the algebraic system overdetermined. Linear least squares still returns the coefficient vector that minimizes the sum of squared algebraic residuals, provided the design matrix has full column rank. Three points are enough for an interpolating circle, not a maximum. The average of the points is not the algebraic solution. A nonzero algebraic residual generally leaves a nonzero geometric residual as well.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_GN,
    )
    b.save()


def bank_svm():
    b = Bank("svm-quadratic-program")
    b.mc(
        1,
        r"The Euclidean distance from a point \(x\) to the hyperplane \(w^T x + b = 0\) is",
        [
            r"\(\lvert w^T x + b\rvert / \lVert w\rVert\)",
            r"\(\lvert w^T x + b\rvert\)",
            r"\(\lVert w\rVert\)",
            r"\(w^T x\)",
        ],
        0,
        r"The numerator is the absolute residual of the hyperplane equation. Dividing by the norm of \(w\) converts that residual into a Euclidean length. Without the division the number scales when \((w, b)\) is scaled, even though the hyperplane does not move. The norm alone ignores the point. The raw dot product \(w^T x\) ignores both the offset \(b\) and the scaling.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"The hyperplane is \(2 y - 2 = 0\) in the plane, so \(w = (0, 2)\) and \(b = -2\). What is the distance from the point \((5, 4)\)?",
        3,
        "1",
        r"The absolute residual is \(\lvert 0 \cdot 5 + 2 \cdot 4 - 2\rvert = 6\). The norm of \(w\) is \(2\). The distance is \(6/2 = 3\). Reporting \(6\) forgets the normalization. Reporting \(2\) gives the norm. Reporting \(4\) gives a coordinate. The same distance is the geometric margin of a point whose signed residual equals \(6\) and whose weight vector has length \(2\).",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        1,
        r"Normalizing so that the smallest functional margin equals \(1\) turns maximum-margin separation into",
        [
            r"minimize \(\lVert w\rVert\) subject only to correct signs \(y_i(w^T x_i + b) \ge 0\)",
            r"maximize \(\tfrac12\lVert w\rVert^2\) with no constraints",
            r"minimize \(\tfrac12\lVert w\rVert^2\) subject to \(y_i(w^T x_i + b) \ge 1\)",
            r"an unconstrained linear program in \(w\)",
        ],
        2,
        r"After scaling, every point satisfies \(y_i(w^T x_i + b) \ge 1\), and the geometric margin is \(1/\lVert w\rVert\). Maximizing that margin is minimizing \(\tfrac12\lVert w\rVert^2\). A constraint that only asks for the correct sign allows \(\lVert w\rVert\) to approach zero and the margin formula to blow up. Maximizing the squared norm runs the wrong way. The objective is quadratic, so the program is not linear, and it is constrained.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.order(
        2,
        "Put these steps in the order that turns maximum-margin separation into a quadratic program. Each step uses the previous result.",
        [
            r"Write each correctly signed distance as \(y_i(w^T x_i + b)/\lVert w\rVert\).",
            "Maximize the smallest of those distances.",
            r"Scale \((w, b)\) so the smallest functional margin \(y_i(w^T x_i + b)\) equals \(1\).",
            r"The problem is then: minimize \(\tfrac12\lVert w\rVert^2\) subject to those normalized inequalities.",
        ],
        r"The signed distances are the quantities whose minimum is the margin, so they come first. The optimization is that minimum. Scaling uses the freedom to multiply \((w, b)\) by a positive number, which does not change the hyperplane, and it freezes the functional margin at \(1\). Only then is the margin equal to \(1/\lVert w\rVert\), and minimizing the square of the norm is the quadratic program. Minimizing the norm before the normalization still has a scale freedom.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"The normalized problem minimizes \(\tfrac12\lVert w\rVert^2\) subject to \(y_i(w^T x_i + b) \ge 1\). Which claims hold? The unknowns are \((w, b)\).",
        [
            r"The objective is quadratic in the unknowns.",
            "Every constraint is linear in the unknowns.",
            "The Hessian of the objective is positive semidefinite.",
            "The problem is a linear program.",
            r"The bias \(b\) appears in the quadratic objective.",
        ],
        [0, 1, 2],
        r"The objective depends on \(w\) through a square, and each constraint is a linear inequality in \((w, b)\)."
        "\n"
        r"• The Hessian is the identity on the \(w\)-block and zero on \(b\), which is positive semidefinite, so the program is a convex quadratic program."
        "\n"
        r"• A linear program would need a linear objective."
        "\n"
        r"• The bias is absent from \(\tfrac12\lVert w\rVert^2\). It appears only in the constraints.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.sym(
        2,
        r"The squared distance from the point \((x, y)\) to the line \(p x + q y + r = 0\) equals",
        "(p*x+q*y+r)**2/(p*p+q*q)",
        {"p": (1, 2), "q": (1, 2), "x": (1, 2), "y": (1, 2), "r": (1, 2)},
        r"The distance is the absolute residual divided by the norm of \((p, q)\). Squaring it removes the absolute value and gives \((p x + q y + r)^2 / (p^2 + q^2)\). Every name is used. On the declared ranges the denominator is positive and the value is positive. Omitting the square leaves a signed quantity. Omitting the denominator leaves the square of the residual, which scales if the line equation is multiplied through by a constant.",
        alternates=["(p*x+q*y+r)*(p*x+q*y+r)/(p**2+q**2)"],
        fig=HALF,
        alt=A_HALF,
    )
    b.find_error(
        3,
        r"A note rescales a separator whose functional margin on a point is \(4\) and whose weight vector has length \(2\). Exactly one step is a false claim.",
        [
            r"The geometric margin of this point is \(4/2 = 2\).",
            r"Dividing \((w, b)\) by \(4\) makes the functional margin equal to \(1\).",
            r"After that scaling, the new norm of \(w\) is \(2/4 = 1/2\).",
            r"The geometric margin becomes \(1/2\).",
        ],
        3,
        r"The geometric margin is the functional margin divided by the norm, so the first value is \(2\). Dividing \((w, b)\) by \(4\) divides both the functional margin and the norm by \(4\). The new norm is \(1/2\), and the new geometric margin is \(1 / (1/2) = 2\). Scaling does not change it. The false step reports the new norm as if it were the margin.",
        [
            r"Scaling \((w, b)\) leaves the geometric margin unchanged. The new value is \(1/(1/2) = 2\).",
            r"The original geometric margin is \(4\), not \(2\).",
            r"The new norm is \(2\), not \(1/2\).",
        ],
        0,
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        3,
        r"In one dimension, separate the labeled points \((x, y_{\mathrm{label}}) = (3, +1)\) and \((1, -1)\) by minimizing \(\tfrac12 w^2\) subject to \(y(wx + b) \ge 1\). What is the optimal bias \(b\)?",
        -2,
        "1",
        r"The two inequalities are \(3w + b \ge 1\) and \(-w - b \ge 1\). Adding them gives \(2w \ge 2\), so \(w \ge 1\). The objective wants the smallest nonnegative square, hence \(w = 1\). Then \(b = 1 - 3w = -2\), and the second inequality holds with equality as well. Reporting \(1\) gives \(w\). Reporting \(2\) drops the sign of the bias. Reporting \(1/2\) is the optimal objective \(\tfrac12 w^2\). The separating point is \(x = 2\).",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        3,
        r"The normalized hard-margin problem, minimize \(\tfrac12\lVert w\rVert^2\) subject to the linear inequalities \(y_i(w^T x_i + b) \ge 1\), is",
        [
            "a convex quadratic program",
            "a linear program",
            r"a nonconvex program, because \(\lVert w\rVert^2\) is nonconvex",
            "an unconstrained problem",
        ],
        0,
        r"The objective is a convex quadratic, since its Hessian is positive semidefinite, and the constraints are affine. That is a convex quadratic program. A linear program would have a linear objective. The squared norm is convex, not nonconvex. The inequalities are present, so the problem is constrained. Convexity is what makes a local solution a global one.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.mc(
        4,
        "At a hard-margin solution, a point that lies strictly beyond the margin has multiplier zero on its inequality, while a point on the margin may have a positive multiplier. That split is",
        [
            "complementary slackness",
            "an equality multiplier, free in sign",
            "a requirement that the Hessian be zero",
            "a proof that the feasible set is empty",
        ],
        0,
        r"Each inequality is \(1 - y_i(w^T x_i + b) \le 0\). Complementary slackness sets the multiplier times that residual to zero. A strict inequality, a point beyond the margin, forces the multiplier to vanish. A point on the margin may carry a positive multiplier. These constraints are inequalities, so the multiplier is not a free equality multiplier. The Hessian of the objective is not zero, and a solution is a feasible point.",
        fig=HALF,
        alt=A_HALF,
        preview=P_KKT,
    )
    b.num(
        4,
        r"With \(w = (3, 4)\) and \(b = 10\), what is the distance from the point \((2, 1)\) to the hyperplane \(w^T x + b = 0\)?",
        4,
        "1",
        r"The absolute residual is \(\lvert 6 + 4 + 10\rvert = 20\). The norm of \(w\) is \(5\). The distance is \(20/5 = 4\). Reporting \(20\) forgets the division. Reporting \(5\) gives the norm. Reporting \(10\) gives the offset. The same quotient is the geometric margin of a correctly signed point with this residual and this weight vector.",
        fig=PAIR,
        alt=A_PAIR,
        preview=P_LAG,
    )
    b.mc(
        4,
        r"Two separators classify the same points. After both are normalized so the functional margin is \(1\), the quadratic program prefers",
        [
            r"the smaller \(\lVert w\rVert\), which is the larger geometric margin",
            r"the larger \(\lVert w\rVert\)",
            "whichever separator has a quadratic constraint",
            "neither, because both programs are linear programs",
        ],
        0,
        r"Under the normalization, the geometric margin is \(1/\lVert w\rVert\). Minimizing \(\tfrac12\lVert w\rVert^2\) therefore selects the larger margin. The larger norm is the smaller margin. The constraints of this program are linear. The quadratic piece is the objective. Neither program is a linear program.",
        fig=FALL,
        alt=A_FALL,
        preview=P_KKT,
    )
    b.save()


def expl_dual():
    sections = [
        {
            "heading": "The idea",
            "figure": FALL,
            "figure_alt": A_FALL,
            "body_md": r"""A constrained minimization asks for the smallest value of an objective on a feasible set. A lower bound on that value can be built without searching the set. Attach a multiplier to each constraint and form the Lagrangian, which is the objective plus the multipliers times the constraint residuals. For a fixed multiplier, minimize the Lagrangian over every decision vector, feasible or not. The resulting number is the dual function at that multiplier.

If an inequality is written as \(g(x) \le 0\) and its multiplier is nonnegative, then at every feasible point the added term is nonpositive. The Lagrangian there sits at or below the objective. Minimizing the Lagrangian can only push the number lower, so the dual function is a lower bound on the primal optimal value. That comparison is weak duality. An equality residual is zero on the feasible set for either sign of its multiplier, so an equality multiplier is left free.

The dual problem maximizes these lower bounds over multipliers that keep the infimum finite. A multiplier that sends the Lagrangian to negative infinity is discarded. The decision vector that attains the infimum need not be feasible.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""For inequalities \(g(x) \le 0\) and equalities \(h(x) = 0\),
\[
L(x,\lambda,\nu) = f(x) + \lambda^T h(x) + \nu^T g(x),
\]
and the dual function is \(\theta(\lambda,\nu) = \inf_x L(x,\lambda,\nu)\). Dual feasibility includes \(\nu \ge 0\). Weak duality says \(\theta(\lambda,\nu) \le p^\star\) whenever the infimum is finite. For the model problem \(\min x^2\) subject to \(x \ge a > 0\), the dual function in the multiplier \(u\) is \(a u - u^2/4\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Minimize \(t^2\) subject to \(t \ge 6\). The Lagrangian is \(t^2 + v(6 - t)\). The derivative in \(t\) vanishes at \(t = v/2\), and substitution produces \(6v - v^2/4\).

The cistern lower bound is 11. That is the value at \(v = 2\): \(12 - 1 = 11\). The primal optimum is \(36\), at \(t = 6\), so the gap at this multiplier is \(25\). The decision \(t = 1\) that attains the infimum is not feasible. The bound does not require it to be. A better multiplier is \(v = 12\), where the dual function equals \(36\) and the gap closes.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""The usual slip is to evaluate the Lagrangian at a feasible point and call that number the dual function. That evaluation is some value of the Lagrangian, not its infimum. A second slip is to allow a negative multiplier on an inequality written as \(g \le 0\). The added term can then be positive on the feasible set, and the lower-bound argument dies. A third is to treat a finite dual value as a primal solution. The dual value certifies a floor. The primal point, if one is wanted, still has to be checked against the constraints. A fourth is to maximize the Lagrangian in the decision variable. The dual function is an infimum.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""Equalities add a multiplier with no sign restriction, and the stationarity condition that sets the derivative of the Lagrangian to zero is the Lagrange rule, provided the constraint gradients are independent. Inequalities add nonnegativity and complementary slackness. Those four requirements together are the KKT system. The same Lagrangian, applied to a linear program in standard form, collapses to another linear program, the dual. Projection onto a half-space is a tiny inequality problem whose multiplier is exactly this construction.""",
        },
    ]
    save_explainer("lagrangian-duality-lower-bounds", "Lagrangian lower bounds and the dual problem", sections)


def expl_lagrange():
    sections = [
        {
            "heading": "The idea",
            "figure": PAIR,
            "figure_alt": A_PAIR,
            "body_md": r"""An equality constraint cuts the domain down to a surface. A minimizer on that surface cannot be improved by any small move that stays on the surface. The directional derivative of the objective along every tangent direction is therefore zero, which means the objective gradient is orthogonal to the tangent space. The orthogonal complement of the tangent space is the span of the constraint gradients, when those gradients are linearly independent.

Independence is the regularity hypothesis. It says the constraint gradients form a basis for the normal line, or the normal plane, at the point. There is then a unique list of multipliers such that the objective gradient plus the combination of constraint gradients equals zero. That vector equation, together with the original equalities, is the Lagrange system. The multipliers are free in sign. Nothing in an equality prefers one sign.

If regularity fails, the geometry can still have a minimizer while the vector equation has no solution. A constraint gradient that vanishes is the simplest version: stationarity would require the objective gradient itself to be zero, and a minimizer need not have a zero objective gradient. The multiplier rule is a theorem with a hypothesis, not an identity.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""For \(h(x) = 0\) with independent rows of the Jacobian at the point,
\[
\nabla f(x) + J_h(x)^T \lambda = 0, \qquad h(x) = 0.
\]
The Lagrangian \(f(x) + \lambda^T h(x)\) packages the same stationarity condition as an unconstrained derivative in \(x\). For \(\min p x^2\) subject to \(x = a\), the multiplier on \(x - a\) is \(-2 p a\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Minimize \(u^2 + v^2\) subject to \(u + v = 4\). The Lagrangian is \(u^2 + v^2 + \lambda(u + v - 4)\). The derivatives give \(2u + \lambda = 0\) and \(2v + \lambda = 0\), so \(u = v\). The constraint forces \(u = v = 2\).

The pier multiplier is -4. The objective at that point is \(4 + 4 = 8\). The constraint gradient is \((1, 1)\), which is not zero, so regularity holds and the multiplier is entitled to exist. The same system is the nearest-point problem on the line, with the origin as the point being projected.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Dropping the constraint after differentiating leaves a scale freedom: stationarity alone does not pin down the point. The equalities have to be adjoined. A second slip is to insist that an equality multiplier be nonnegative. That sign belongs to an inequality. A third is to treat a dependent constraint gradient as a minor nuisance. Minimizing \(x\) subject to \(x^2 = 0\) has the feasible point \(x = 0\) as its minimizer, the constraint derivative vanishes there, and \(1 + \lambda \cdot 0 = 0\) has no solution. A fourth is to set the objective gradient orthogonal to the constraint gradients. It lies along them.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""An inequality keeps the same stationarity picture on the face where it is active, and it adds a sign on the multiplier plus a product that is zero when the inequality is slack. That package is the KKT system. The nearest point on an affine set is an equality-constrained least-distance problem, so the Lagrange multiplier produces the projection formula. The dual linear program is what the same stationarity relation becomes when every function involved is linear.""",
        },
    ]
    save_explainer("lagrange-multiplier-equality", "Lagrange multipliers for equality constraints", sections)


def expl_kkt():
    sections = [
        {
            "heading": "The idea",
            "figure": HALF,
            "figure_alt": A_HALF,
            "body_md": r"""An inequality can be active at a minimizer, or it can have room to spare. The two situations ask different things of the multiplier. Write each inequality as \(g_i(x) \le 0\). Stationarity still says that the objective gradient is balanced by a combination of the active constraint gradients. A constraint that is slack should not pull on that balance, so its multiplier is zero. A constraint that is active may pull, and the multiplier is then a weight on its gradient.

The sign of the weight is fixed by the inequality direction. With the residual written as \(g_i(x)\), the feasible side is the negative side, and the multiplier is nonnegative. A negative multiplier would push the stationarity equation the wrong way, toward the infeasible side. Complementary slackness is the bookkeeping that covers both situations at once: the product of the multiplier and the residual is zero. Either the residual is zero, or the multiplier is zero, or both.

Primal feasibility and dual feasibility are the remaining two lists. The point has to satisfy every constraint, and every inequality multiplier has to have the legal sign. Equality constraints, if any are present, keep free multipliers and stay in the stationarity equation. A point that fails any one of the four lists is not a KKT point, even if the other three lists are perfect.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""For \(\min f(x)\) subject to \(g(x) \le 0\),
\[
\nabla f(x) + J_g(x)^T \nu = 0, \quad g(x) \le 0, \quad \nu \ge 0, \quad \nu_i g_i(x) = 0.
\]
On an active bound \(x = b\) for \(\min (x - a)^2\), the multiplier is \(2(a - b)\) when the Lagrangian carries \(\nu(x - b)\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Minimize \((t - 9)^2\) subject to \(t \le 4\). Stationarity is \(2(t - 9) + \nu = 0\). The branch \(\nu = 0\) puts \(t\) at \(9\), and \(9 \le 4\) fails. The active branch puts \(t\) at \(4\).

The gate multiplier is 10. Stationarity gives \(2(4 - 9) + \nu = 0\), so \(\nu = 10\), which is nonnegative. The objective is \(25\). Complementary slackness holds because the bound is active. The discarded branch was stationary and dual feasible and still illegal, because it was not primal feasible.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Accepting the inactive branch without checking the inequality is the standard miss. Stationarity and a zero multiplier are not enough. The point has to land inside the feasible set. A second miss is a positive multiplier on a strict inequality. The product is then nonzero. A third is a negative multiplier on an active bound. The sign is part of the system, not a free Lagrange multiplier. A fourth is to stop at the first case that is algebraically convenient. Both cases of the product have to be tried, and each survivor has to pass the lists it has not yet been checked against.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A linear program in standard form is an equality \(Ax = b\) plus the inequalities \(x \ge 0\). Its KKT system is stationarity of the Lagrangian, nonnegativity of both the primal variables and the dual slacks, and complementary products. Eliminating the primal variables leaves the dual linear program. The same four lists, applied to the squared distance to a half-space, produce the projection formula: stay put when the point is inside, and step along the normal when it is outside.""",
        },
    ]
    save_explainer("kkt-conditions", "KKT conditions", sections)


def expl_lpdual():
    sections = [
        {
            "heading": "The idea",
            "figure": BASIS,
            "figure_alt": A_BASIS,
            "body_md": r"""Standard form minimizes a linear cost \(c^T x\) subject to linear equalities \(Ax = b\) and the inequalities \(x \ge 0\). The KKT system of that program is small enough to solve in closed form for the inequality multipliers. Give the equalities a free multiplier \(y\). Give each nonnegative variable a nonnegative slack multiplier. Stationarity says the cost, minus \(A^T y\), equals that nonnegative slack.

The slack formula \(s = c - A^T y\) is a constraint on \(y\) alone once \(s \ge 0\) is imposed: \(A^T y \le c\). Substitute the same formula back into the Lagrangian. Every term that contains \(x\) cancels, and what remains is \(b^T y\). The dual problem maximizes that linear function over the multipliers that satisfy the inequality just obtained. Nothing quadratic survives, because every function in the primal was linear.

Weak duality is the general fact that a dual-feasible value cannot exceed a primal-feasible cost. Here it says \(b^T y \le c^T x\) for every feasible pair. The difference equals a sum of complementary products, so it is nonnegative, and it is zero precisely when complementary slackness holds. A pair with equal objectives and both sides feasible is optimal on both sides.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""The primal and the dual are
\[
\text{minimize } c^T x \text{ subject to } Ax = b,\ x \ge 0,
\]
\[
\text{maximize } b^T y \text{ subject to } A^T y \le c.
\]
The dual slack is \(s = c - A^T y \ge 0\), and complementary slackness is \(x_j s_j = 0\). Weak duality is \(b^T y \le c^T x\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Minimize \(-5x\) subject to \(x + s = 9\) with \(x, s \ge 0\). The dual maximizes \(9y\) subject to \(y \le -5\) and \(y \le 0\).

The barge dual is -45. The tighter bound is \(y \le -5\), and \(9 \cdot (-5) = -45\). The primal attains the same cost at \(x = 9\), \(s = 0\). The products match complementary slackness: the positive primal variable has zero dual slack, and the positive dual slack on \(s\), which equals \(5\), multiplies a zero primal variable. The pair is optimal.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Reversing \(A^T y \le c\) is the usual algebra error. The slack is \(c - A^T y\), and a slack has to be nonnegative, so \(A^T y\) sits below \(c\). A second error is to minimize \(b^T y\). The Lagrangian becomes \(b^T y\) after the infimum in \(x\), and the dual maximizes the lower bound. A third is to call a gap a proof of optimality. A positive gap says at least one of the two points can be improved, or that the pair is not both feasible if the dual value exceeds the primal cost. A fourth is to force the equality multiplier to be nonnegative. Nonnegativity belongs to the inequality slacks.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""The dual inequality \(A^T y \le c\) is the constraint set of several later algorithms that walk through the interior of a linear program, in the primal or in the dual, by following scaled quadratic models. A primal-dual method writes the same KKT system, perturbs the complementary products, and takes a Newton step on that perturbed map. The derivation above is the reason those methods have a dual variable at all.""",
        },
    ]
    save_explainer("lp-duality-kkt", "LP duality from KKT", sections)


def expl_proj():
    sections = [
        {
            "heading": "The idea",
            "figure": HALF,
            "figure_alt": A_HALF,
            "body_md": r"""The Euclidean projection of a point \(z\) onto a closed set is the nearest point of the set. For an affine set \(\{x : Ax = b\}\) and for a half-space \(\{x : a^T x \le \beta\}\), the nearest-point problem is small enough that its KKT system is a formula.

Use the objective \(\tfrac12\lVert x - z\rVert^2\), so the gradient is \(x - z\) with no extra factor of \(2\). On an affine set, stationarity says \(x - z\) is a linear combination of the rows of \(A\). The combination's coefficients are the multipliers, and they are free because the constraints are equalities. Substituting into \(Ax = b\) produces a square linear system in the multipliers. That system is invertible when \(A\) has full row rank, which is the regularity condition for these equalities. The resulting point is the projection.

A half-space has one inequality. If \(z\) is already inside, the projection is \(z\) and the multiplier is zero. If \(z\) is outside, the inequality is active, the multiplier is positive, and the projection is the same point one would have computed on the bounding hyperplane. The residual \(z - x\) then points along the outward normal.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""Onto \(a^T x = \beta\) with \(a \ne 0\),
\[
\nu = \frac{a^T z - \beta}{a^T a}, \qquad x = z - \nu a.
\]
Onto \(a^T x \le \beta\), use that same point when \(a^T z > \beta\), and use \(x = z\) otherwise. Full row rank of a general \(A\) makes \(AA^T\) the invertible matrix in the same role.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Project \((9, 4)\) onto the half-space \(x \le 3\). The first coordinate is \(9 > 3\), so the point is outside and the bound is active. The normal is \((1, 0)\).

The ramp gap is 36. The projection is \((3, 4)\), the multiplier is \(6\), and the squared distance is \(6^2 = 36\). The second coordinate never moves, because the normal has a zero there. Stationarity reads \((3, 4) - (9, 4) + 6(1, 0) = 0\). Had the first coordinate been at most \(3\), the multiplier would have been zero and the gap would have been zero.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Projecting an interior point onto the boundary is the common miss. The interior point is already feasible, and the distance is already zero. A second miss is a negative multiplier when the point is outside an inequality. The step \(z - \nu a\) uses a positive \(\nu\) to come back to the hyperplane. A negative \(\nu\) walks further out. A third is to use the equality formula on a half-space without checking which side \(z\) is on. A fourth is to invert \(AA^T\) when a row of \(A\) is zero. The rank condition is the difference between a formula and a singular matrix.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A general closed convex set still has a nearest point, and the nearest-point relation becomes an inequality about angles rather than a linear formula. The half-space case is the model for that inequality: the residual makes a non-acute angle with every feasible direction. Gradient methods that cannot take a free step replace the trial point by this projection, onto a half-space or onto a more complicated convex set, and the multiplier computed here is the same multiplier the KKT system would have produced.""",
        },
    ]
    save_explainer("projection-affine-halfspace-kkt", "Projection onto affine sets and half-spaces", sections)


def expl_lls():
    sections = [
        {
            "heading": "The idea",
            "figure": RISE,
            "figure_alt": A_RISE,
            "body_md": r"""An overdetermined linear equation \(Ax \approx b\) usually has no exact solution. Least squares asks for the \(x\) that makes the residual \(Ax - b\) as small as possible in the Euclidean norm. The objective \(\lVert Ax - b\rVert^2\) is a quadratic in \(x\). Its gradient is \(2 A^T(Ax - b)\), and its Hessian is \(2 A^T A\).

Setting the gradient to zero produces the normal equations \(A^T A x = A^T b\). The same equation says the residual is orthogonal to every column of \(A\). That is the geometric picture: the residual is perpendicular to the column space, so \(Ax\) is the orthogonal projection of \(b\) onto that subspace.

The Hessian is positive definite exactly when \(A\) has full column rank. Then \(A^T A\) is invertible and the minimizer is unique, \(x = (A^T A)^{-1} A^T b\). If the columns are dependent, \(A^T A\) is singular. The normal equations stay consistent, because \(A^T b\) lies in the column space of \(A^T A\), but the solution is no longer unique. Every solution has the same residual.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""The normal equations and the full-column-rank solution are
\[
A^T A x = A^T b, \qquad x = (A^T A)^{-1} A^T b.
\]
For one column \((p, q)\) and a right-hand side \((u, v)\), the scalar unknown is \((p u + q v)/(p^2 + q^2)\). The residual of the fitted vector is orthogonal to the columns.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Four measurements of one unknown are \(1, 9, 3, 11\), and the column is a column of ones. The normal equation is \(4x = 24\).

The gauge mean is 6. The residual is \((-5, 3, -3, 5)\), and it sums to zero, which is orthogonality against the single column of ones. The squared residual is \(25 + 9 + 9 + 25 = 68\). The fit is unique because a nonzero column has full column rank. It is not an exact fit, and least squares does not pretend that it is.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Replacing \(A^T b\) by \(b\) is the algebra error that breaks the shapes. The right-hand side has to live in the column space of \(A^T\). A second error is to declare \(A^T A\) invertible just because \(A\) is tall. Tall matrices can have repeated columns. A third is to use the full-row-rank formula \((AA^T)^{-1}\) on a tall full-column-rank matrix. That Gram matrix is the large one, and it is singular. A fourth is to expect a zero residual. A zero residual means \(b\) was already in the column space. The normal equations do not require that.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A line or a polynomial is linear least squares once the unknowns are the coefficients and the columns are powers of the input. A residual that depends nonlinearly on the parameters is no longer a single normal equation. Its Jacobian plays the role of \(A\) at the current parameters, and a step of that kind is how later methods move. A recursive update of the same normal equation, one block of rows at a time, is the least-squares form of a linear filter.""",
        },
    ]
    save_explainer("linear-least-squares", "Linear least squares", sections)


def expl_fit():
    sections = [
        {
            "heading": "The idea",
            "figure": RISE,
            "figure_alt": A_RISE,
            "body_md": r"""Data fitting, in the linear case, chooses a model whose prediction at each input is a dot product of a parameter vector with a feature vector. The feature vector may be a nonlinear function of the input. Linearity is required of the parameters. A quadratic polynomial in \(t\) bends as a curve, and it is still linear in the three coefficients of \(1\), \(t\), and \(t^2\).

The design matrix has one row per measurement and one column per parameter. The row is the feature vector. The right-hand side is the list of measured values. Solving the normal equations of that pair is the fit. The columns are independent when the features, evaluated on the inputs, are independent. For a polynomial of degree \(d\), that happens as soon as there are \(d + 1\) distinct inputs. Fewer inputs leave a nontrivial combination of columns at zero, and the coefficient vector is then not unique.

Extra measurements are welcome. They make the system overdetermined, which is the usual least-squares situation. A repeated input copies a row. It can change the right-hand side's influence, and it cannot raise the rank.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""A line has rows \((1, t_i)\). A quadratic has rows \((1, t_i, t_i^2)\). The prediction of a line at a new input \(t\) is \(a + b t\). Through the origin, with rows that are just the inputs, the slope fit to two points \((p, u)\) and \((q, v)\) is \((p u + q v)/(p^2 + q^2)\). The minimum number of distinct inputs for a unique polynomial of degree \(d\) is \(d + 1\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Fit \(y = b t\), a line through the origin, to the two points \((t, y) = (1, 6)\) and \((2, 12)\). There is one parameter. The normal equation is \((1 + 4) b = 6 + 24\).

The chalk slope is 6. Both points lie on \(y = 6 t\), so the residual is zero and the fit is an exact interpolation. A third point off that line would keep the same one-column design and would move the slope. The model stays linear in \(b\) either way. The input \(t\) is not a parameter.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Calling a model nonlinear because the curve bends is the usual mix-up. Bend is about the input. Linearity is about the coefficients. A second miss is a design row that contains the unknown coefficients. The row is built from the input only. A third is to square the input in the wrong slot: at \(t = 2\) the quadratic row is \((1, 2, 4)\), not \((1, 2, 2)\). A fourth is to believe that more parameters can be identified than the number of distinct rows. Rank cannot exceed the number of independent rows.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A circle in center-and-radius form is nonlinear in those three numbers. Expanding the circle equation and renaming the collected coefficients produces a model that is linear in a different parameter vector, with rows built from the point coordinates. That algebraic fit is ordinary linear least squares of the kind written here. Keeping the geometric distance as the residual leaves a nonlinear least-squares problem instead.""",
        },
    ]
    save_explainer("least-squares-data-fitting", "Least-squares data fitting", sections)


def expl_nls():
    sections = [
        {
            "heading": "The idea",
            "figure": FALL,
            "figure_alt": A_FALL,
            "body_md": r"""Some residuals depend on the parameters through a nonlinear function: an exponential of a rate, a sine of a frequency, a squared distance to an unknown center. The fitting criterion can still be a sum of squares. The problem is then nonlinear least squares. There is no single normal equation that finishes the job, because the design matrix itself moves when the parameters move.

What replaces the design matrix, at a chosen parameter vector, is the residual Jacobian. It has one row per residual and one column per parameter, and the entry is the partial derivative of that residual. Evaluating it is a calculus step, not an optimization step. Once it is in hand, the first-order model of the residual at a nearby parameter is the current residual plus the Jacobian times the step. That model is linear in the step, so it can be handed to an ordinary linear least-squares solver. Building the model is part of stating the problem. Iterating it is a later method.

If every residual happens to be affine, the Jacobian is constant and the problem really is linear least squares. The nonlinear name is reserved for the cases where the derivatives still depend on the point.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""The objective is \(\lVert r(x)\rVert^2\). The Jacobian \(J_r(x)\) has entries \(\partial r_i / \partial x_j\). The linear model of a step \(d\) is \(r(x) + J_r(x)\, d\). A single residual \(p^2 - s\) contributes \((p^2 - s)^2\) to the objective. Full column rank of \(J_r(x)\) makes \(J_r(x)^T J_r(x)\) positive definite.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Take the scalar residual pair \(r(w) = (w^2 - 2,\ w - 4)\), and evaluate it at \(w = 3\). The residual vector is \((7, -1)\).

The coil residual is 50. That is \(49 + 1\). The Jacobian is the column \((2w, 1) = (6, 1)\) at this point. It depends on \(w\) through the first entry, which is the sign that the residual is nonlinear. A linear model of a step \(d\) would be \((7, -1) + d(6, 1)\). Solving that small least-squares problem for \(d\) is a later algorithm. The number \(50\) is only the objective.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Copying one residual's derivative onto the next residual is the calculus error. Each row is its own function. A second error is to put parameters down the rows and residuals across the columns. The shape is residuals by parameters, because that is how a Jacobian of a vector map is written. A third is to put the residual values into the Jacobian. Those values belong in \(r(x)\). The Jacobian holds derivatives. A fourth is to drop \(r(x)\) from the linear model and fit \(J d\) to zero. That asks the step to ignore the current misfit.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A method that repeatedly solves the linearized least-squares model is Gauss-Newton. Adding a multiple of the identity to the Gram matrix damps that step when the linear model is a poor local description. A circle can be left in geometric form, with a residual equal to the distance from a point to the center minus the radius. That residual is nonlinear in the center and the radius, and its Jacobian is the one this skill builds. An algebraic rewrite avoids the Jacobian by changing the parameters.""",
        },
    ]
    save_explainer("nonlinear-least-squares", "Nonlinear least-squares problems", sections)


def expl_circle():
    sections = [
        {
            "heading": "The idea",
            "figure": DENT,
            "figure_alt": A_DENT,
            "body_md": r"""A circle in the plane is determined by a center and a radius. Asking those three numbers to match a list of points, in the geometric sense, produces a residual equal to the distance from each point to the center, minus the radius. The center appears inside a square root, or inside a square, and the problem is nonlinear least squares.

Algebra offers a different residual that vanishes on exactly the same circles. Expand \((x - a)^2 + (y - b)^2 - r^2 = 0\). The result is \(x^2 + y^2\) plus a term in \(x\), a term in \(y\), and a constant. Rename the coefficient of \(x\) as \(c\), the coefficient of \(y\) as \(d\), and the constant as \(e\). The equation becomes \(x^2 + y^2 + c x + d y + e = 0\). The new unknowns \((c, d, e)\) appear linearly. The squares of the coordinates are data, and they move to the right-hand side of a linear least-squares problem.

The two objectives agree about which circles pass through the points. They disagree about the cost of a near miss. The algebraic fit is still the right tool when a linear problem is what is wanted, and the geometric fit remains available when the residual must be a length.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""The rename is \(c = -2a\), \(d = -2b\), and \(e = a^2 + b^2 - r^2\). The center is \((-c/2, -d/2)\), and
\[
r^2 = \frac{c^2}{4} + \frac{d^2}{4} - e.
\]
The design row of a point \((x, y)\) is \((x, y, 1)\), and the right-hand side entry is \(-(x^2 + y^2)\). Three independent rows are the minimum for a unique \((c, d, e)\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Take the point \((6, 2)\) and the parameters \(c = -2\), \(d = -6\), \(e = 5\). The squares are \(36 + 4 = 40\). The rest is \(-2 \cdot 6 + (-6) \cdot 2 + 5 = -12 - 12 + 5 = -19\).

The hoop residual is 21. The center decoded from these parameters is \((1, 3)\), and the squared radius is \(1 + 9 - 5 = 5\). The algebraic residual is not zero, so the point is not on that circle. A geometric residual would subtract \(\sqrt{5}\) from the distance between \((6, 2)\) and \((1, 3)\). Those two misfit numbers are not equal.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Putting a plus in front of \(r^2\) inside \(e\) is the expansion error. The geometric equation subtracts \(r^2\), so \(e = a^2 + b^2 - r^2\). A second error is to read the center as \((c, d)\) instead of \((-c/2, -d/2)\). The factor \(-2\) is the derivative of \((x - a)^2\) in \(a\), moved to the other side. A third is to treat the algebraic objective as the sum of squared distances. The two criteria share their zero set and not their values. A fourth is to insist on exactly three points. More points are a rectangular linear least-squares problem.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""If the residual has to be the geometric distance, the parameters \((a, b, r)\) stay nonlinear and the Jacobian of that residual is the starting point of a Gauss-Newton iteration. A damped version of the same iteration is available when the linear model of the residual is not trusted. The algebraic route is the one that stays inside linear least squares, with a design matrix whose rows are the point coordinates and a column of ones.""",
        },
    ]
    save_explainer("circle-fitting-least-squares", "Circle fitting by least squares", sections)


def expl_svm():
    sections = [
        {
            "heading": "The idea",
            "figure": HALF,
            "figure_alt": A_HALF,
            "body_md": r"""A linear separator is a hyperplane \(w^T x + b = 0\). The distance from a point to that hyperplane is the absolute value of \(w^T x + b\), divided by the norm of \(w\). For a point with label \(y_i\) equal to \(+1\) or \(-1\), the signed version \(y_i(w^T x_i + b)/\lVert w\rVert\) is positive when the point is on the correct side. The smallest of those signed distances, over the training points, is the geometric margin.

The hyperplane does not change if \(w\) and \(b\) are multiplied by the same positive number. That freedom can be used to scale the pair until the smallest functional margin \(y_i(w^T x_i + b)\) equals \(1\). After the scaling, the geometric margin is exactly \(1/\lVert w\rVert\). Maximizing the margin is therefore the same as minimizing \(\tfrac12\lVert w\rVert^2\), subject to \(y_i(w^T x_i + b) \ge 1\) for every \(i\).

The objective is a convex quadratic. Each constraint is linear in the unknowns \((w, b)\). The bias does not appear in the objective. It appears in every constraint. The Hessian is the identity on the weight block and zero on the bias, which is positive semidefinite. The program is a convex quadratic program.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""The distance and the normalized program are
\[
\frac{\lvert w^T x + b\rvert}{\lVert w\rVert}, \qquad \text{minimize } \tfrac12\lVert w\rVert^2 \text{ subject to } y_i(w^T x_i + b) \ge 1.
\]
The squared distance from \((x, y)\) to \(p x + q y + r = 0\) is \((p x + q y + r)^2 / (p^2 + q^2)\). Scaling \((w, b)\) does not change a geometric margin.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Take \(w = (3, -4)\) and \(b = 2\), and the point \((4, 1)\). The absolute residual is \(\lvert 12 - 4 + 2\rvert = 10\). The norm of \(w\) is \(5\).

The plaque gap is 2. The distance is \(10/5 = 2\). Multiplying \((w, b)\) by \(2\) would double the residual and double the norm, and the distance would stay \(2\). That is the same cancellation the margin uses. A separator that has already been normalized so the functional margin is \(1\) would report this geometry as a margin of \(1/\lVert w\rVert\), not as the un-normalized residual.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Forgetting to divide by \(\lVert w\rVert\) makes the distance change when the equation of the same hyperplane is scaled. A second slip is to divide \((w, b)\) by the functional margin and then report the new norm as the new geometric margin. The margin is the reciprocal of that norm, and it is unchanged by the scaling. A third is to call the program a linear program. The constraints are linear and the objective is not. A fourth is to put \(b\) into the quadratic objective. The objective is a function of \(w\) only.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""The inequalities \(y_i(w^T x_i + b) \ge 1\) are ordinary inequality constraints, so a minimizer carries nonnegative multipliers and complementary slackness. A point strictly beyond the margin gets a zero multiplier. A point on the margin may get a positive one. Those are the KKT conditions of this quadratic program. An equality-constrained stationarity condition is the same balance of gradients in problems whose constraints are equations rather than one-sided margins.""",
        },
    ]
    save_explainer("svm-quadratic-program", "Support vector machines as a quadratic program", sections)


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


def main():
    _balance_mc()
    bank_dual()
    bank_lagrange()
    bank_kkt()
    bank_lpdual()
    bank_proj()
    bank_lls()
    bank_fit()
    bank_nls()
    bank_circle()
    bank_svm()
    expl_dual()
    expl_lagrange()
    expl_kkt()
    expl_lpdual()
    expl_proj()
    expl_lls()
    expl_fit()
    expl_nls()
    expl_circle()
    expl_svm()
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
    ids = [
        "lagrangian-duality-lower-bounds",
        "lagrange-multiplier-equality",
        "kkt-conditions",
        "lp-duality-kkt",
        "projection-affine-halfspace-kkt",
        "linear-least-squares",
        "least-squares-data-fitting",
        "nonlinear-least-squares",
        "circle-fitting-least-squares",
        "svm-quadratic-program",
    ]
    private = {
        "lagrangian-duality-lower-bounds": "The cistern lower bound is 11",
        "lagrange-multiplier-equality": "The pier multiplier is -4",
        "kkt-conditions": "The gate multiplier is 10",
        "lp-duality-kkt": "The barge dual is -45",
        "projection-affine-halfspace-kkt": "The ramp gap is 36",
        "linear-least-squares": "The gauge mean is 6",
        "least-squares-data-fitting": "The chalk slope is 6",
        "nonlinear-least-squares": "The coil residual is 50",
        "circle-fitting-least-squares": "The hoop residual is 21",
        "svm-quadratic-program": "The plaque gap is 2",
    }
    bad = False
    totals = Counter()
    for sid in ids:
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
        if private[sid] not in json.dumps(exp):
            print("  worked-example marker missing")
            bad = True
        if private[sid] in json.dumps(bank):
            print("  worked example reused in the bank")
            bad = True
    print("totals", dict(totals))
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
