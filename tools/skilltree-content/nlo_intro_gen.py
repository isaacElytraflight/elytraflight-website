#!/usr/bin/env python3
"""Generate the optional nonlinear-optimization introduction banks and explainers.

Skills: calculus of variations and the brachistochrone, the largest ellipsoid
inscribed in a polytope, and trajectory planning as one optimization problem.

Closed-form answers live here. skilltree/verify_nlo_intro.py recomputes the
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
    disk_fig,
    ellipse_axes,
    filled_ellipse_fig,
    halfspace_fig,
    level_curves_fig,
    matrix_fig,
    plane_vectors,
    plot,
    segment_fig,
)

CURVE = plot(lambda t: 1.4 - 0.12 * t * t, 0.0, 3.2, "x", "y", "a curve that drops")
A_CURVE = "A curve that falls as the horizontal coordinate grows."
SEG = segment_fig("a segment")
A_SEG = "A solid segment joins two marked points on a dashed line."
LEV = level_curves_fig("nested contours")
A_LEV = "Three nested ellipses around the origin."
HALF = halfspace_fig("a shaded half-plane")
A_HALF = "A straight boundary with one side shaded."
ELL = ellipse_axes("a long ellipse")
A_ELL = "An axis-aligned ellipse, longer along the first axis."
FILL = filled_ellipse_fig("a shaded elliptical disk")
A_FILL = "A shaded elliptical disk centered in the plane."
MAT = matrix_fig([["p", "0"], ["0", "q"]], "a diagonal array")
A_MAT = "A two-by-two array with labels on the diagonal."
DISK = disk_fig("a disk at the origin")
A_DISK = "A filled disk centered at the origin."
ARR = plane_vectors([(1.1, 0.35, "v")], "one arrow from the origin")
A_ARR = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.05, 0.55, "a"), (1.05, -0.55, "b")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin, one above the axis and one below."

P_LQR = ["lqr"]
P_MPC = ["mpc"]
P_PD = ["primal-dual-interior-point"]


def _sec(idea, eqs, work, pits, leads, fig, alt):
    return [
        {"heading": "The idea", "figure": fig, "figure_alt": alt, "body_md": idea},
        {"heading": "Key equations", "body_md": eqs},
        {"heading": "Worked example", "body_md": work},
        {"heading": "Common pitfalls", "body_md": pits},
        {"heading": "Where this leads", "body_md": leads},
    ]


def bank_cov():
    b = Bank("calculus-of-variations")
    b.mc(
        1,
        r"A calculus-of-variations problem chooses",
        [
            r"a curve, and the score is one number attached to that whole curve",
            r"a finite list of numbers, and the score is an ordinary function of that list",
            r"a matrix, and the score is its largest eigenvalue",
            r"one slope at one point, and the score is that slope",
        ],
        0,
        r"The decision is an admissible curve and the score, called a functional, is a single number for the whole curve. An ordinary objective takes a finite list of numbers. An eigenvalue is a number attached to a matrix. A slope at one point is local data, not the score of the curve.",
        fig=CURVE,
        alt=A_CURVE,
    )
    # L = (y')^2 + 3 y, partial in y' is 2 y'. At y' = 4 the value is 8.
    b.num(
        1,
        r"The integrand is \(L = (y^{\prime})^2 + 3 y\). At a point where the slope \(y^{\prime}\) equals \(4\), what is the partial derivative of \(L\) with respect to \(y^{\prime}\)?",
        2 * 4,
        "1",
        r"Differentiating \((y^{\prime})^2\) with respect to the slope brings down a factor \(2\), and the term \(3 y\) does not depend on the slope, so the partial derivative is \(2 y^{\prime}\). At slope \(4\) that is \(8\). Reporting \(4\) repeats the slope. Reporting \(16\) is the square of the slope. Reporting \(3\) is the coefficient of the height. The factor \(2\) is required.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"The brachistochrone asks for the wire between two fixed points that",
        [
            r"minimizes the travel time of a bead that starts from rest and slides under gravity",
            r"minimizes the length of the wire, which is the straight line",
            r"maximizes the height of the bead at the finish",
            r"makes the slope constant from the start to the finish",
        ],
        0,
        r"The score is travel time. A short wire is not automatically a fast wire, because the bead's speed grows only as it loses height. The straight line minimizes length, which is a different functional. The finish height is fixed by the two endpoints, so it is not a score to maximize. A constant slope is the straight line again, not the time minimizer.",
        fig=CURVE,
        alt=A_CURVE,
    )
    b.order(
        2,
        r"Put these steps in the order that tests one candidate curve for \(\int L\, dx\). Each step uses the result of the step before it.",
        [
            r"Write the integrand \(L\) as an expression in the coordinate, the height, and the slope.",
            r"From that expression, compute the partial derivative of \(L\) with respect to the slope.",
            r"Differentiate the partial derivative just computed with respect to the coordinate, along the candidate.",
            r"Set that derivative equal to the partial derivative of the same integrand with respect to the height, and keep the curve only when equality holds at every interior coordinate.",
        ],
        r"The slope partial is computed from the integrand, so the integrand comes first. The total derivative along the candidate is the derivative of that partial, so it comes next. The keep-or-reject step compares that derivative with the height partial, so it comes last. Computing the height partial before the integrand exists, or differentiating the slope partial before it has been formed, is not a reordering of these steps.",
        fig=CURVE,
        alt=A_CURVE,
    )
    b.multi(
        2,
        r"The Euler-Lagrange equation reduces to 'the partial derivative of \(L\) with respect to the slope is constant' precisely when \(L\) does not depend on the height. Which integrands have that reduction?",
        [
            r"\((y^{\prime})^2 + 4\)",
            r"\(\sqrt{1 + (y^{\prime})^2}\)",
            r"\((y^{\prime})^2 + y^2\)",
            r"\(y\, (y^{\prime})^2\)",
            r"\(x\, (y^{\prime})^2\)",
        ],
        [0, 1, 4],
        r"The height partial is zero exactly when the height does not appear, and then the total derivative of the slope partial vanishes, so the slope partial itself is constant along a stationary curve."
        "\n"
        r"• \((y^{\prime})^2 + 4\) and \(\sqrt{1 + (y^{\prime})^2}\) contain the slope and no height."
        "\n"
        r"• \(x\, (y^{\prime})^2\) contains the coordinate and the slope, but not the height. The slope partial \(2 x y^{\prime}\) is what stays constant. The slope itself need not be constant."
        "\n"
        r"• \((y^{\prime})^2 + y^2\) and \(y\, (y^{\prime})^2\) both contain the height, so the height partial is not identically zero.",
        fig=LEV,
        alt=A_LEV,
    )
    b.sym(
        2,
        r"The integrand is \(\tfrac{a}{2} (y^{\prime})^2 - b y\), with \(a\) and \(b\) positive. On a stationary curve the second derivative of the height equals",
        "-b/a",
        {"a": (1, 3), "b": (1, 5)},
        r"The partial derivative with respect to the slope is \(a y^{\prime}\). Its derivative along the curve is \(a\) times the second derivative. The partial derivative with respect to the height is \(-b\). Setting them equal gives \(a\) times the second derivative equal to \(-b\), so the second derivative equals \(-b/a\). Both names appear. Dropping \(a\) leaves \(-b\). Dropping the minus sign sends the curve the wrong way. Using \(b/a\) without the minus is the negative of the second derivative.",
        alternates=["-(b/a)", "-1*b/a"],
        fig=CURVE,
        alt=A_CURVE,
    )
    b.find_error(
        3,
        r"A note tests the straight line \(y = x\) for the integrand \((y^{\prime})^2 / 2 + 2 y\). Exactly one step is a false claim.",
        [
            r"The integrand is \((y^{\prime})^2 / 2 + 2 y\).",
            r"The partial derivative of the integrand with respect to the slope is the slope itself.",
            r"Along \(y = x\) the slope is \(1\), so the derivative of that partial along the line is \(0\).",
            r"The partial derivative with respect to the height is \(2\), and \(0\) equals \(2\), so the line is stationary.",
        ],
        3,
        r"The integrand is the one stated. Differentiating \(\tfrac12 (y^{\prime})^2\) with respect to the slope produces the slope, and the height term does not contribute. A line of slope \(1\) has a constant slope partial, so its coordinate derivative is \(0\). The height partial is \(2\). Zero and \(2\) are not equal, so the Euler-Lagrange equation fails and the line is not stationary. A stationary curve for this integrand has second derivative \(2\).",
        [
            r"Zero and \(2\) are not equal, so the line is not stationary.",
            r"The partial derivative with respect to the slope is not the slope.",
            r"The line \(y = x\) has a slope other than \(1\).",
        ],
        0,
        fig=SEG,
        alt=A_SEG,
    )
    # y = r (1 - cos theta), r = 3, theta = pi, cos = -1, drop = 6.
    b.num(
        3,
        r"A cycloid is generated by a circle of radius \(3\) meters, with the vertical coordinate measured downward, \(y = 3(1 - \cos\theta)\). What is \(y\) at \(\theta = \pi\)?",
        3 * (1 - (-1)),
        "m",
        r"At \(\theta = \pi\), the cosine equals \(-1\), so \(1 - \cos\theta = 2\) and \(y = 3 \cdot 2 = 6\) meters. That is the bottom of one generating roll. Reporting \(3\) is the radius, which would be the drop at \(\theta = \pi/2\), where the cosine is \(0\). Reporting \(0\) treats the cosine of \(\pi\) as \(1\). The horizontal coordinate at this parameter is \(3\pi\), which is not the vertical drop.",
        fig=CURVE,
        alt=A_CURVE,
    )
    b.mc(
        3,
        r"A bead on the brachistochrone drops steeply at first. The reason a longer wire can beat the straight line is that",
        [
            r"speed grows with the vertical drop, so an early drop buys a faster run over the rest of the wire",
            r"the straight line is not an admissible curve between the two endpoints",
            r"gravity does no work, so travel time depends only on length",
            r"the cycloid is the curve of least length as well as least time",
        ],
        0,
        r"Travel time is the integral of distance divided by speed, and the speed grows like the square root of the height already lost. Spending length on an early drop raises the speed for every later piece. Both the straight line and the cycloid join the same endpoints, so both are admissible. Gravity is what produces the speed. The least-length curve is the straight line, a different functional.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        4,
        r"The cycloid that solves the brachistochrone is traced by",
        [
            r"a point fixed on a circle as the circle rolls along a straight line",
            r"a point moving at constant speed along a straight line",
            r"a point in free fall with no wire at all",
            r"the graph of a quadratic polynomial",
        ],
        0,
        r"That rolling construction is the definition of a cycloid, and it is the time-minimizing wire. Constant speed along a straight line does not lose height first. Free fall is vertical and need not meet the second endpoint. A quadratic is a different curve. The time minimizer is the cycloid.",
        fig=CURVE,
        alt=A_CURVE,
        preview=P_LQR,
    )
    # y = x^2, L = (y')^2 + 5 y. d/dx (2 y') = d/dx (4x) = 4. Height partial 5. Residual 4 - 5 = -1.
    b.num(
        4,
        r"The integrand is \(L = (y^{\prime})^2 + 5 y\), and the candidate is \(y = x^2\). At \(x = 1\), what is the derivative along the curve of the slope partial, minus the height partial?",
        4 - 5,
        "1",
        r"The slope partial is \(2 y^{\prime}\). Along \(y = x^2\) the slope is \(2x\), so the slope partial is \(4x\), and its derivative is \(4\). The height partial is \(5\). The difference is \(4 - 5 = -1\), which is not zero, so this parabola is not stationary for this integrand. Reporting \(4\) stops at the derivative of the slope partial. Reporting \(5\) is the height partial alone. Reporting \(1\) flips the sign of the difference.",
        fig=LEV,
        alt=A_LEV,
        preview=P_MPC,
    )
    b.mc(
        4,
        r"If the integrand does not depend on the height, a stationary curve satisfies",
        [
            r"the partial derivative of the integrand with respect to the slope is constant along the curve",
            r"the slope itself is constant, for every such integrand",
            r"the integrand is constant, whether or not the slope changes",
            r"the height partial equals the slope, with no derivative along the curve",
        ],
        0,
        r"No height in the integrand means the height partial is zero, so the derivative along the curve of the slope partial is zero, and the slope partial is constant. The slope itself is constant only for special integrands, such as a pure square of the slope. The integrand can still change with the coordinate. Comparing the two partials without differentiating the slope partial skips the total derivative in the Euler-Lagrange equation.",
        fig=SEG,
        alt=A_SEG,
        preview=P_LQR,
    )
    b.save()


def bank_ell():
    b = Bank("largest-inscribed-ellipsoid")
    b.mc(
        1,
        r"With \(B\) symmetric positive definite, the set of points \(B u + d\) for \(\lVert u\rVert \le 1\) is",
        [
            r"an ellipsoid centered at \(d\), with its shape fixed by \(B\)",
            r"the unit disk, for every \(B\) and every center \(d\)",
            r"a polygon, because \(B\) is a matrix",
            r"a half-space whose boundary passes through \(d\)",
        ],
        0,
        r"\(B\) maps the unit disk to an elliptical disk, and adding \(d\) moves the center. Different positive definite matrices give different shapes, so the set is not always the unit disk. A matrix image of a disk is not a polygon. A half-space is unbounded, and this set is the image of a bounded disk.",
        fig=FILL,
        alt=A_FILL,
    )
    # B = diag(2, 1), a = (3, 0), d = (1, 4). Ba = (6, 0), length 6, a·d = 3, sum 9.
    b.num(
        1,
        r"Take \(B = \mathrm{diag}(2,\ 1)\), normal \(a = (3,\ 0)\), and center \(d = (1,\ 4)\). What is \(\lVert B a\rVert + a^T d\)?",
        6 + 3,
        "1",
        r"\(B a = (6,\ 0)\), so the length is \(6\). The center term is \(3 \cdot 1 + 0 \cdot 4 = 3\). The sum is \(9\). Reporting \(6\) drops the center term. Reporting \(3\) drops the length. Reporting \(10\) would be a half-space bound, and no bound was given. The containment test compares this sum with the bound. It does not square the length.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        1,
        r"Maximizing \(\log\det B\) over the containment inequalities is a convex problem because",
        [
            r"\(\log\det\) is concave on positive definite matrices, and each containment inequality cuts a convex set",
            r"\(\log\det\) is a linear function of the entries of \(B\)",
            r"the unit disk \(\lVert u\rVert \le 1\) is the decision variable",
            r"every ellipsoid has the same volume, so the objective does not matter",
        ],
        0,
        r"A concave objective, maximized over a convex feasible set, is a convex problem. Equivalently one minimizes \(-\log\det B\), which is convex. The logarithm of the determinant is not linear in the entries. The decision variables are the center and the shape, not a point \(u\) inside the ellipsoid. Different shapes have different determinants, so the volume is the objective.",
        fig=MAT,
        alt=A_MAT,
    )
    b.order(
        2,
        r"Put these steps in the order that checks one half-space \(a^T x \le \beta\) against one ellipsoid. Each step uses the result of the step before it.",
        [
            r"Multiply the shape matrix \(B\) by the outward normal \(a\).",
            r"Take the Euclidean length of the vector that multiplication produced.",
            r"Add the center term \(a^T d\) to that length.",
            r"Keep the half-space only when the sum just obtained is at most the bound \(\beta\).",
        ],
        r"The length is the length of \(B a\), so the product comes first. The center term is added to that length, so the length comes before the sum. The keep-or-reject step compares the sum with the bound, so it comes last. Comparing with \(\beta\) before the sum exists, or taking a length before \(B a\) exists, is not a reordering of these steps.",
        fig=HALF,
        alt=A_HALF,
    )
    b.multi(
        2,
        r"The closed strip \(-2 \le x_1 \le 2\) is the pair of inequalities \(x_1 \le 2\) and \(-x_1 \le 2\). Which ellipsoids \(\{B u + d : \lVert u\rVert \le 1\}\) lie in the strip? \(B\) is diagonal with positive diagonal entries.",
        [
            r"\(B = \mathrm{diag}(1,\ 1)\), \(d = (0,\ 0)\)",
            r"\(B = \mathrm{diag}(1,\ 1)\), \(d = (1.5,\ 0)\)",
            r"\(B = \mathrm{diag}(0.5,\ 3)\), \(d = (1,\ 0)\)",
            r"\(B = \mathrm{diag}(2,\ 0.5)\), \(d = (0,\ 0)\)",
            r"\(B = \mathrm{diag}(1,\ 1)\), \(d = (0,\ 5)\)",
        ],
        [0, 2, 3, 4],
        r"For \(B = \mathrm{diag}(p,\ q)\) with \(p > 0\), the two inequalities reduce to \(p + d_1 \le 2\) and \(p - d_1 \le 2\). The second diagonal entry and the second coordinate of the center do not appear."
        "\n"
        r"• \(\mathrm{diag}(1,\ 1)\) at the origin gives \(1 \le 2\) on both sides."
        "\n"
        r"• \(\mathrm{diag}(0.5,\ 3)\) with \(d_1 = 1\) gives \(1.5 \le 2\) and \(-0.5 \le 2\)."
        "\n"
        r"• \(\mathrm{diag}(2,\ 0.5)\) at the origin meets the bound with equality, which the closed strip allows."
        "\n"
        r"• A center at \((0,\ 5)\) still has \(d_1 = 0\), so the strip, which does not see \(x_2\), still holds."
        "\n"
        r"• \(\mathrm{diag}(1,\ 1)\) with \(d_1 = 1.5\) gives \(2.5 > 2\) on the right-hand face.",
        fig=FILL,
        alt=A_FILL,
    )
    b.sym(
        2,
        r"\(B = \mathrm{diag}(p,\ q)\) with \(p\) and \(q\) positive, the normal is \((1,\ 0)\), and the center is \((c,\ 0)\). The containment left-hand side \(\lVert B a\rVert + a^T d\) equals",
        "p+c",
        {"p": (1, 3), "c": (1, 3)},
        r"\(B a = (p,\ 0)\), and \(p\) is positive, so the length is \(p\). The center term is \(c\). The sum is \(p + c\). The second diagonal entry is multiplied by the zero component of the normal, so \(q\) does not appear. Reporting \(p\) drops the center. Reporting \(q + c\) uses the diagonal entry the normal does not see. Both declared names appear.",
        alternates=["c+p"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        r"A note checks the unit disk, \(B = I\) and \(d = 0\), against the half-space \(x_1 + x_2 \le 1\). Exactly one step is a false claim.",
        [
            r"The product \(B a\) with \(a = (1,\ 1)\) equals \((1,\ 1)\).",
            r"The Euclidean length of \((1,\ 1)\) is \(\sqrt{2}\).",
            r"The center term \(a^T d\) equals \(0\).",
            r"Since \(\sqrt{2} \le 1\), the unit disk lies in the half-space.",
        ],
        3,
        r"\(B\) is the identity, so \(B a = a = (1,\ 1)\). The length \(\sqrt{1^2 + 1^2}\) is \(\sqrt{2}\). The center is the origin, so the center term is \(0\). The containment sum is \(\sqrt{2}\), and \(\sqrt{2} > 1\), so the inequality fails. The unit disk sticks out through the line \(x_1 + x_2 = 1\). The false step is the comparison of \(\sqrt{2}\) with \(1\).",
        [
            r"\(\sqrt{2}\) is greater than \(1\), so the unit disk is not inside the half-space.",
            r"The length of \((1,\ 1)\) is not \(\sqrt{2}\).",
            r"The center term \(a^T d\) is not \(0\).",
        ],
        0,
        fig=HALF,
        alt=A_HALF,
    )
    # B = diag(3, 1), a = (0, 4), d = (2, 1). Ba = (0, 4), length 4, a·d = 4, sum 8.
    b.num(
        3,
        r"Take \(B = \mathrm{diag}(3,\ 1)\), normal \(a = (0,\ 4)\), and center \(d = (2,\ 1)\). What is \(\lVert B a\rVert + a^T d\)?",
        4 + 4,
        "1",
        r"\(B a = (0,\ 4)\), so the length is \(4\). The center term is \(0 \cdot 2 + 4 \cdot 1 = 4\). The sum is \(8\). Reporting \(4\) keeps only one of the two equal terms. Reporting \(16\) squares the length instead of using it. Reporting \(3\) is the unused diagonal entry. The first column of \(B\) is invisible to this normal.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        3,
        r"\(\log\det\) of \(\mathrm{diag}(4,\ 1)\) and of \(\mathrm{diag}(2,\ 2)\) compare as follows.",
        [
            r"They are equal, because both determinants equal \(4\)",
            r"\(\mathrm{diag}(4,\ 1)\) is larger, because of the entry \(4\)",
            r"\(\mathrm{diag}(2,\ 2)\) is larger, because a rounder shape always has larger determinant",
            r"Neither is defined, because a diagonal matrix is not positive definite",
        ],
        0,
        r"The determinant of a positive diagonal matrix is the product of the diagonal entries. Both products equal \(4\), so the logarithms agree and the two ellipsoids have the same volume factor. A single large entry does not raise the determinant if another entry shrinks to compensate. Roundness is not the definition of the determinant. Both matrices have positive diagonal entries, so both are positive definite.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        4,
        r"If \(B\) is symmetric positive semidefinite and singular, the set \(\{B u + d : \lVert u\rVert \le 1\}\) is",
        [
            r"a flat elliptical disk, with volume zero",
            r"a full-dimensional ellipsoid whose volume is still positive",
            r"a half-space",
            r"the whole plane",
        ],
        0,
        r"A singular \(B\) collapses the unit disk onto a lower-dimensional set, so the two-dimensional volume, which tracks \(\det B\), is zero. Positive semidefinite still makes the image an elliptical disk, only a flat one. The image of a bounded disk is bounded, so it is neither a half-space nor the whole plane.",
        fig=FILL,
        alt=A_FILL,
        preview=P_PD,
    )
    # B = diag(1, 2), d = 0.
    # a = (2, 0), bound 5: length 2, slack 3.
    # a = (0, 1), bound 4: Ba = (0, 2), length 2, slack 2.
    # Smaller slack is 2.
    b.num(
        4,
        r"\(B = \mathrm{diag}(1,\ 2)\) and the center is the origin. One face has normal \((2,\ 0)\) and bound \(5\). The other has normal \((0,\ 1)\) and bound \(4\). What is the smaller of the two slacks, bound minus \(\lVert B a\rVert\)?",
        min(5 - 2, 4 - 2),
        "1",
        r"The first product is \((2,\ 0)\), length \(2\), slack \(5 - 2 = 3\). The second product is \((0,\ 2)\), length \(2\), slack \(4 - 2 = 2\). The smaller slack is \(2\). Reporting \(3\) is the looser face. Reporting \(5\) or \(4\) is a bound, not a slack. Adding the slacks gives \(5\), which is not what was asked. The tighter face is the one whose slack is smaller.",
        fig=HALF,
        alt=A_HALF,
        preview=P_PD,
    )
    b.mc(
        4,
        r"The containment inequality \(\lVert B a_i\rVert + a_i^T d \le b_i\) has to hold",
        [
            r"for every inequality that defines the polytope",
            r"for at least one inequality, since the others are then automatic",
            r"only for the inequalities that are active at the center \(d\)",
            r"only when \(B\) is a multiple of the identity",
        ],
        0,
        r"Each inequality is a half-space, and the ellipsoid has to sit in the intersection, so every half-space contributes its own inequality. One satisfied face says nothing about the opposite face. A face that misses the center can still cut the ellipsoid if \(B\) is wide. The same formula uses a general symmetric positive definite \(B\), not only a multiple of the identity.",
        fig=FILL,
        alt=A_FILL,
        preview=P_PD,
    )
    b.save()


def bank_traj():
    b = Bank("trajectory-optimization")
    b.mc(
        1,
        r"After a path is replaced by samples \(x_0,\ldots,x_N\), the decision variable of the optimization problem is",
        [
            r"the list of those samples, together with any control values the transcription keeps free",
            r"the original continuous curve, with no grid",
            r"only the final time, even when the samples are still free",
            r"the radius of an obstacle",
        ],
        0,
        r"Discretizing replaces the curve by finitely many numbers, and those numbers are what the problem chooses. Leaving the decision as a free function is the calculus-of-variations form, which the grid was meant to leave behind. The final time can be one coordinate of the decision, but it is not the whole decision while the samples are free. An obstacle radius is data, unless the problem is explicitly designing the obstacle.",
        fig=SEG,
        alt=A_SEG,
    )
    # Points (0,0), (1,0), (1,2), (4,2). Squared steps 1, 4, 9. Sum 14.
    b.num(
        1,
        r"Samples are \((0,\ 0)\), \((1,\ 0)\), \((1,\ 2)\), and \((4,\ 2)\). What is the smoothness cost, the sum of the squared steps between consecutive samples?",
        1 + 4 + 9,
        "1",
        r"The steps are \((1,\ 0)\), \((0,\ 2)\), and \((3,\ 0)\). Their squared lengths are \(1\), \(4\), and \(9\). The sum is \(14\). Reporting \(9\) keeps only the last square. Reporting \(4\) keeps only the middle square. Reporting \(3\) is the last horizontal step, not its square. The cost adds every squared step, including the vertical one.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"An energy cost on a control sequence \(u_0,\ldots,u_{N-1}\) is",
        [
            r"the sum of the squared controls",
            r"the number of obstacles",
            r"the determinant of a dynamics matrix",
            r"the radius of the smallest obstacle",
        ],
        0,
        r"Energy here means a sum of squares of the controls, one term per interval. The obstacle count and the obstacle radius are data of the constraints, not the cost. A determinant measures volume of a linear map. It is not this cost.",
        fig=ARR,
        alt=A_ARR,
    )
    b.order(
        2,
        r"Put these steps in the order that scores one candidate path and then accepts or rejects it. Each step uses the result of the step before it.",
        [
            r"Read the candidate positions in time order.",
            r"From each position just read and the next one, recover the control on that interval as their difference divided by the time step.",
            r"Square the controls just recovered and add the squares to produce the energy.",
            r"Subtract that energy from the best energy stored so far.",
            r"Accept the candidate only when the difference just computed is positive and every position that entered the energy lies outside the obstacle.",
        ],
        r"The controls are differences of the positions, so the positions come first. The squares use those controls, so they come after the controls are recovered. The subtraction uses the energy sum, so it comes after the sum. The accept-or-reject step uses that difference, so it comes last. Testing the obstacle before the positions are read, or subtracting an energy that has not been added, is not a reordering of these steps.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.multi(
        2,
        r"Which of these feasible sets are nonconvex?",
        [
            r"the outside of a disk, \(\lVert x\rVert \ge 2\)",
            r"the inside of a disk, \(\lVert x\rVert \le 2\)",
            r"the half-space \(x_1 \ge 0\)",
            r"the union of the two intervals \([0,\ 1]\) and \([3,\ 4]\) on the line",
            r"the box \([0,\ 1]\times[0,\ 1]\)",
        ],
        [0, 3],
        r"A set is nonconvex when some segment between its points leaves the set."
        "\n"
        r"• The outside of a disk fails: \((-2,\ 0)\) and \((2,\ 0)\) are both at distance \(2\) from the origin, and the segment between them passes through the origin."
        "\n"
        r"• The union of two disjoint intervals fails: the segment from \(1\) to \(3\) leaves the union."
        "\n"
        r"• A disk, a half-space, and a box are convex. Every segment between their points stays inside.",
        fig=DISK,
        alt=A_DISK,
    )
    b.sym(
        2,
        r"Samples on a line sit at \(0\), at \(s\), and at \(4\). The smoothness cost is \(w\) times the sum of the two squared steps. That cost equals",
        "w*(s^2+(4-s)^2)",
        {"w": (0.5, 2), "s": (0, 3)},
        r"The steps are \(s - 0\) and \(4 - s\). The sum of squares is \(s^2 + (4 - s)^2\), and the weight \(w\) multiplies that sum. Both names appear. Dropping \(w\) leaves the unweighted sum. Using only \(s^2\) drops the second step. Replacing \(4 - s\) by \(4 + s\) points the second step the wrong way.",
        alternates=["w*(s**2+(4-s)**2)", "w*(2*s**2-8*s+16)"],
        fig=SEG,
        alt=A_SEG,
    )
    b.find_error(
        3,
        r"A note averages two paths around a disk of radius \(1\) centered at \((1,\ 0)\). Exactly one step is a false claim.",
        [
            r"Path A uses the samples \((0,\ 0)\), \((1,\ 2)\), and \((2,\ 0)\).",
            r"Path B uses the samples \((0,\ 0)\), \((1,\ -2)\), and \((2,\ 0)\).",
            r"The samplewise average is \((0,\ 0)\), \((1,\ 0)\), and \((2,\ 0)\).",
            r"The middle sample of the average is at distance \(2\) from \((1,\ 0)\), so it lies outside the disk.",
        ],
        3,
        r"The two paths and their samplewise average are as stated. The middle sample of the average is \((1,\ 0)\), the same point as the disk's center, so the distance is \(0\), not \(2\). A disk of radius \(1\) contains that sample. Path A passes through \((1,\ 2)\), at distance \(2\) from the center, and path B through \((1,\ -2)\), also at distance \(2\). Both clear the disk, including the shared endpoints, which sit at distance \(1\). Their average does not. The outside of the disk is not convex.",
        [
            r"The middle sample of the average is the center \((1,\ 0)\), at distance \(0\), so it lies inside the disk.",
            r"Path A does not use the sample \((1,\ 2)\).",
            r"The average of \((1,\ 2)\) and \((1,\ -2)\) is not \((1,\ 0)\).",
        ],
        0,
        fig=PAIR,
        alt=A_PAIR,
    )
    # Controls 2, -1, 2. Sum of squares 4 + 1 + 4 = 9.
    b.num(
        3,
        r"The controls on three intervals are \(2\), \(-1\), and \(2\). What is the energy, the sum of the squared controls?",
        2 ** 2 + (-1) ** 2 + 2 ** 2,
        "1",
        r"The squares are \(4\), \(1\), and \(4\). The sum is \(9\). The sign of the middle control disappears when it is squared. Reporting \(3\) adds the controls themselves, \(2 + (-1) + 2\). Reporting \(4\) keeps a single square. Reporting \(2\) is one control. Energy adds every square.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        3,
        r"Obstacle constraints make a trajectory problem nonconvex because",
        [
            r"the outside of an obstacle is not a convex set: the segment between two clear points can cut through the obstacle",
            r"a sum of squared controls is a nonconvex function",
            r"a linear dynamics constraint \(x_{+} = A x + B u\) is a nonconvex set",
            r"every union of convex sets is convex, and an obstacle is a union",
        ],
        0,
        r"Two paths can clear an obstacle on opposite sides while the segment between them hits the obstacle, so the feasible set is not convex. A sum of squares is convex, not nonconvex. A linear equality is an affine set, which is convex. The outside of one obstacle is the complement of a convex set, not a union of convex sets, and a union of convex sets need not be convex anyway.",
        fig=DISK,
        alt=A_DISK,
    )
    b.mc(
        4,
        r"On a grid of \(N\) intervals with a free time step \(h > 0\), a minimum-time cost is",
        [
            r"\(N h\), the duration of the grid",
            r"the sum of the squared controls",
            r"the number of obstacles",
            r"the determinant of the dynamics matrix",
        ],
        0,
        r"With a fixed interval count, the duration is the count times the step, so minimizing time is minimizing \(h\), or \(N h\). The sum of squared controls is an energy cost. The obstacle count is data. A determinant is not a duration.",
        fig=SEG,
        alt=A_SEG,
        preview=P_MPC,
    )
    # x+ = 2 x + u, x0 = 1, u = (0, 1). x1 = 2, x2 = 5.
    b.num(
        4,
        r"The dynamics are \(x_{k+1} = 2 x_k + u_k\), with \(x_0 = 1\) and controls \(u_0 = 0\), \(u_1 = 1\). What is \(x_2\)?",
        2 * (2 * 1 + 0) + 1,
        "1",
        r"The first step is \(2 \cdot 1 + 0 = 2\). The second step is \(2 \cdot 2 + 1 = 5\). Reporting \(2\) stops at \(x_1\). Reporting \(1\) is the initial state, or the second control. Reporting \(3\) adds the controls to the initial state and forgets the doubling. Each step multiplies the current state by \(2\) before adding the control.",
        fig=ARR,
        alt=A_ARR,
        preview=P_LQR,
    )
    b.mc(
        4,
        r"This transcription, compared with a controller that applies only the first computed input and builds the problem again at the next sample,",
        [
            r"builds one open-loop plan for the whole grid",
            r"replans at every sample, by the definition of the transcription",
            r"cannot include a dynamics constraint",
            r"requires the cost to be a sum of squares",
        ],
        0,
        r"The decision is the whole sequence, chosen once. Replanning at the next sample, and applying only the first input, is a receding-horizon loop wrapped around a transcription of this kind. Dynamics are ordinary constraints of the transcription. The cost can be time or a smoothness sum. It does not have to be a sum of squares.",
        fig=PAIR,
        alt=A_PAIR,
        preview=P_MPC,
    )
    b.save()


def expl_cov():
    save_explainer(
        "calculus-of-variations",
        "Brachistochrone and calculus of variations",
        _sec(
            r"""An ordinary problem picks a finite list of numbers. This problem picks a curve, and the score is one number for the whole curve. That score is a functional.

A bead starts from rest and slides under gravity from a fixed point to a lower fixed point. The shortest wire is the straight line, and it is admissible. It is not the fastest. Speed grows only as the bead loses height, and the time is distance divided by speed, added along the wire. A wire that drops steeply at first pays extra length and then runs faster. The wire that wins is a cycloid, traced by a point on a circle as the circle rolls along a straight line.

Stationarity is the first-order idea moved from a point to a curve. A stationary curve cannot be improved by a small wiggle that keeps the endpoints fixed. Arc length and a bending energy are the same kind of score, with different integrands.""",
            r"""Write the score as an integral of an integrand \(L\) that may depend on the coordinate \(x\), the height \(y\), and the slope \(y^{\prime}\). A stationary curve satisfies the Euler-Lagrange equation
\[
\frac{d}{dx}\frac{\partial L}{\partial y^{\prime}} = \frac{\partial L}{\partial y}
\]
at every interior point. If \(L\) does not depend on \(y\), the right-hand side is zero, so \(\partial L/\partial y^{\prime}\) is constant along the curve. The cycloid from a circle of radius \(r\), with height measured downward, is \(x = r(\theta - \sin\theta)\) and \(y = r(1 - \cos\theta)\).""",
            r"""Take the integrand to be half the square of the slope, minus \(9\) times the height. The partial derivative with respect to the slope is the slope itself. Differentiating that along the curve produces the second derivative. The partial derivative with respect to the height is \(-9\). The Euler-Lagrange equation says the second derivative equals \(-9\).

The anchor curvature is -9. A straight line has second derivative zero, so it is not stationary for this integrand.

A cycloid from a circle of radius \(10\), a quarter turn from the start, drops a height equal to that radius. The bead drop is 10. Length does not settle the time comparison with the straight line.""",
            r"""Setting an ordinary derivative to zero at one point misses an equation that has to hold along the graph. Minimizing length and calling the result the fastest wire mixes two functionals. The least-length curve is the straight line. Comparing the two partial derivatives without differentiating the slope partial skips the total derivative. Some integrands have no stationary curve: a height partial that is a nonzero constant cannot match a slope partial that does not depend on the slope.""",
            r"""A quadratic cost on a linear motion, over an infinite horizon, replaces the free curve by a feedback gain. A finite grid of positions is an open-loop transcription of the same stationarity idea, and rebuilding that grid at every sample is a receding-horizon controller. Later skills do not require the cycloid.""",
            CURVE,
            A_CURVE,
        ),
    )


def expl_ell():
    save_explainer(
        "largest-inscribed-ellipsoid",
        "Largest inscribed ellipsoid",
        _sec(
            r"""A positive definite matrix already draws ellipses as level sets of a quadratic form. This problem uses the other picture. Apply a symmetric positive definite matrix \(B\) to the unit disk, then translate by a center \(d\). The image is an elliptical disk. Its area is proportional to \(\det B\).

A polytope is an intersection of half-spaces. The ellipsoid sits inside when it sits in every half-space. On the unit disk, a linear function peaks at a value equal to the length of its coefficient vector, so the worst point of the ellipsoid in the direction \(a_i\) is the center term plus the length of \(B a_i\). That sum has to fit under the bound.

Among the ellipsoids that fit, the largest maximizes \(\log\det B\). That logarithm is concave on positive definite matrices, and each containment inequality describes a convex set of pairs \((B,\ d)\). Maximizing a concave function over a convex set is a convex problem. A singular \(B\) flattens the disk and drops the determinant to zero.""",
            r"""The ellipsoid and the containment test are
\[
\mathcal{E} = \{B u + d : \lVert u\rVert \le 1\},
\]
\[
\lVert B a_i\rVert + a_i^T d \le b_i \quad\text{for every face } i.
\]
\(B\) is symmetric positive definite. The volume objective is \(\log\det B\). On a positive diagonal matrix the determinant is the product of the diagonal entries, so two diagonal shapes with the same product have the same volume factor.""",
            r"""Take \(B = \mathrm{diag}(7,\ 3)\), the center at the origin, and the normal \((1,\ 0)\). The product \(B a\) is \((7,\ 0)\), the length is \(7\), and the center term is zero.

The anchor length is 7. The second diagonal entry never enters, because the normal has a zero in that slot. The determinant of this \(B\) is the product of the diagonal entries.

The anchor determinant is 21. A diagonal shape with the same product has the same volume factor and, along this normal, a different containment length.""",
            r"""Checking one face and skipping the others leaves the ellipsoid free to poke through the rest of the polytope. Dropping the center term, or dropping the length, tests only half of the sum. Squaring the length is a third slip: the support of the unit disk is the length itself. Treating \(\log\det\) as linear in the entries of \(B\) confuses a product of eigenvalues with a sum. A singular \(B\) is not a full ellipsoid. Its determinant is zero and the set is flat.""",
            r"""The containment inequalities are convex and the volume objective is concave, so the fitting problem is a convex program. A primal-dual interior-point method can solve a convex program of this size. Later skills do not require the fitting problem. The picture of an ellipsoid as the image of the unit disk is the part worth keeping.""",
            FILL,
            A_FILL,
        ),
    )


def expl_traj():
    save_explainer(
        "trajectory-optimization",
        "Trajectory planning as optimization",
        _sec(
            r"""A path is a curve, and a control sequence is a function of time. The transcription replaces either one by a finite list: a position at each sample, and a control on each interval if the controls stay free. That list is the decision variable. The objective is a sum over the samples. The constraints link one sample to the next and keep the path off whatever it must not touch.

A time cost, on a grid with a fixed interval count and a free step \(h\), is the duration. An energy cost is the sum of the squared controls. A smoothness cost is the sum of the squared steps between consecutive positions.

Dynamics are constraints. A simple link says the next position equals this position plus the step times the control. A feasible list has to satisfy the link on every interval.

An obstacle is different. Staying outside a disk means the distance from the sample to the center is at least the radius. Two points can sit on opposite sides, both clear, while the segment between them runs through the disk. The feasible set is then not convex, even when the cost is a sum of squares and the dynamics are linear.""",
            r"""One transcription is
\[
\begin{aligned}
& \text{minimize} && \sum_k \lVert u_k\rVert^2 \\
& \text{subject to} && x_{k+1} = x_k + h u_k, \\
&&& \lVert x_k - c\rVert \ge r.
\end{aligned}
\]
The same pattern with \(\sum_k \lVert x_{k+1} - x_k\rVert^2\) is a smoothness cost. With a free step \(h\) and a fixed interval count \(N\), a time cost is \(N h\). The outside of the disk is the constraint that makes the feasible set nonconvex.""",
            r"""Take positions \((8,\ 0)\), \((16,\ 0)\), and \((16,\ 7)\). The steps are \((8,\ 0)\) and \((0,\ 7)\). The squared lengths are \(64\) and \(49\).

The anchor smoothness is 113. Starting at \(8\) and adding a control \(7\) lands at \(15\).

The anchor landing is 15. A disk of radius \(3\) at \((8,\ 0)\) leaves the samples \((8,\ 7)\) and \((8,\ -7)\) clear, since each is \(7\) units from the center. Their midpoint is the center. The anchor gap is 7, and the averaged sample does not clear the disk.""",
            r"""Leaving the decision as a free function, after the grid is chosen, mixes this transcription with a problem in the calculus of variations. Calling a sum of squares nonconvex puts the defect in the wrong place. A sum of squares is convex. The obstacle is what fails the segment test. A linear dynamics link is an affine constraint, hence convex. Averaging two feasible paths and expecting the average to stay feasible is the test the obstacle fails. Time and energy are different objectives until a sentence says how they combine.""",
            r"""Applying only the first control, then building the problem again at the next sample, is a receding-horizon controller. This transcription is one open-loop plan for the whole grid. A quadratic cost on a linear model, with no obstacle, reduces further to a feedback gain. Later skills do not require the transcription.""",
            PAIR,
            A_PAIR,
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
    "calculus-of-variations": "The anchor curvature is -9",
    "largest-inscribed-ellipsoid": "The anchor length is 7",
    "trajectory-optimization": "The anchor smoothness is 113",
}

LEAKS = {
    "calculus-of-variations": [
        "(y^{\\prime})^2 + 3 y",
        "radius \\(3\\)",
        "(y^{\\prime})^2 + 5 y",
        "0 equals 2",
    ],
    "largest-inscribed-ellipsoid": [
        "\\mathrm{diag}(2,\\ 1)",
        "\\mathrm{diag}(3,\\ 1)",
        "\\mathrm{diag}(1,\\ 2)",
        "\\sqrt{2} \\le 1",
    ],
    "trajectory-optimization": [
        "(4,\\ 2)",
        "u_0 = 0",
        "radius \\(1\\)",
        "(1,\\ 2)",
    ],
}


def main():
    _balance_mc()
    bank_cov()
    bank_ell()
    bank_traj()
    expl_cov()
    expl_ell()
    expl_traj()
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
        raw = "\n".join(s.get("body_md") or "" for s in exp["sections"])
        blob = raw + json.dumps(bank)
        hits = [w for w in banned if w in blob.lower()]
        leaks = [w for w in LEAKS[sid] if w in raw]
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
