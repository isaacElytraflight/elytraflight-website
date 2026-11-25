#!/usr/bin/env python3
"""Generate optimization-models batch EB3 banks and explainers.

Skills: quadratic-program, quadratically-constrained-quadratic-program,
second-order-cone-program, semidefinite-program, conic-duality,
lasso-stationarity, coordinate-descent, equality-constrained-newton,
barrier-interior-point.

Closed-form answers live here. skilltree/verify_eecs127_eb3.py recomputes
the numeric ones and does not import this file.

Ordering check: every order question was read pair by pair. Each step uses
a quantity the previous step produces, so swapping an adjacent pair leaves
the procedure incorrect. Coordinate updates that could be swapped are not
listed as separate steps.

Diagrams: a bowl for the convex quadratic shape; a half-space where the
constraint is affine; a disk where the feasible set is a Euclidean ball;
the 2 by 2 matrix whose eigenvalues are asked; the nonnegative orthant
where the dual cone is the question; the soft-threshold graph where the
flat middle is the question; the log-barrier curve where the wall at the
boundary is the question. Formula-only prompts have no figure.

Overlap, recorded in the pull request, not as new skills: unconstrained
Newton stays newton-method-optimization and is the prerequisite of the
equality system. Coordinate descent is not incremental-gradient-methods.
The log barrier stays the lighter prerequisite of primal-dual-interior-point.
"""
import math
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import DEEP_TYPES, Bank, deep_quota, save_explainer
from templates import disk_fig, halfspace_fig, matrix_fig, orthant_fig, plot

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IDS = [
    "quadratic-program",
    "quadratically-constrained-quadratic-program",
    "second-order-cone-program",
    "semidefinite-program",
    "conic-duality",
    "lasso-stationarity",
    "coordinate-descent",
    "equality-constrained-newton",
    "barrier-interior-point",
]
VIDEOS = {
    "quadratic-program": {
        "url": "https://www.youtube.com/watch?v=kM52hSvBY4k",
        "title": "A quadratic objective with affine constraints",
    },
    "quadratically-constrained-quadratic-program": {
        "url": "https://www.youtube.com/watch?v=SP2-7AG2wfk",
        "title": "Quadratic inequalities that stay convex",
    },
    "second-order-cone-program": {
        "url": "https://www.youtube.com/watch?v=LxR9ZPLDYNE",
        "title": "A Euclidean norm bounded by an affine function",
    },
    "semidefinite-program": {
        "url": "https://www.youtube.com/watch?v=Paqi8_qrTTk",
        "title": "An affine matrix constrained to be positive semidefinite",
    },
    "conic-duality": {
        "url": "https://www.youtube.com/watch?v=NGCAKGZ7pf4",
        "title": "The dual of a cone program",
    },
    "lasso-stationarity": {
        "url": "https://www.youtube.com/watch?v=UyVbIvf-6OA",
        "title": "Stationarity of an absolute penalty, and the soft-threshold map",
    },
    "coordinate-descent": {
        "url": "https://www.youtube.com/watch?v=TiiF3VG_ViU",
        "title": "Minimizing one coordinate while the others stay fixed",
    },
    "equality-constrained-newton": {
        "url": "https://www.youtube.com/watch?v=2lPT8j4D1x0",
        "title": "One Newton step that keeps an equality feasible",
    },
    "barrier-interior-point": {
        "url": "https://www.youtube.com/watch?v=mJGgFwcvcqI",
        "title": "A log barrier whose weight is sent toward zero",
    },
}
PREV = {
    "quadratic-program": [
        "quadratically-constrained-quadratic-program",
        "svm-quadratic-program",
    ],
    "quadratically-constrained-quadratic-program": ["second-order-cone-program"],
    "second-order-cone-program": ["semidefinite-program", "conic-duality"],
    "semidefinite-program": ["largest-inscribed-ellipsoid"],
    "conic-duality": ["primal-dual-interior-point"],
    "lasso-stationarity": ["coordinate-descent"],
    "coordinate-descent": ["lasso-stationarity"],
    "equality-constrained-newton": ["barrier-interior-point"],
    "barrier-interior-point": ["primal-dual-interior-point"],
}

BOWL = plot(lambda x: (x - 2) ** 2 + 1, 0, 4, "x", "f", "a convex quadratic bowl")
ABOWL = "A curve that opens upward. The horizontal axis is labeled x and the vertical axis is labeled f."
HALF = halfspace_fig("one side of an affine inequality")
AHALF = "A straight boundary with one side shaded. The axes are labeled x1 and x2."
DISK = disk_fig("a disk centered at the origin")
ADISK = "A shaded disk centered at the origin. The axes are labeled x1 and x2."
HESS = matrix_fig([["6", "2"], ["2", "3"]], "a symmetric 2 by 2 matrix")
AHESS = "A 2 by 2 matrix with 6 and 3 on the diagonal and 2 in each off-diagonal entry."
ORTH = orthant_fig("the nonnegative orthant")
AORTH = "The closed first quadrant, shaded, with axes labeled x1 and x2."
BLOCK = matrix_fig([["H", "A^T"], ["A", "0"]], "block layout of an equality Newton step")
ABLOCK = (
    "A 2 by 2 block layout. The top-left block is labeled H, the top-right is labeled "
    "A transpose, the bottom-left is labeled A, and the bottom-right is labeled 0."
)


SOFT = plot(lambda z: 0.0 if z < 1.0 else z - 1.0, 0, 3, "z", "x", "a soft-threshold map")
ASOFT = (
    "A curve on axes labeled z and x. It stays on the horizontal axis beside the origin, "
    "then rises in a straight slope."
)
BAR = plot(lambda u: (u + 1.05) - math.log(u + 0.05), 0, 4, "x", "phi", "a log-barrier objective")
ABAR = (
    "A curve on axes labeled x and phi that climbs steeply near the left side of the "
    "window and then rises toward the right."
)


def publish_graph():
    path = os.path.join(ROOT, "skilltree", "ee105_skills_draft.json")
    with open(path, encoding="utf-8") as f:
        graph = json.load(f)
    for skill in graph["skills"]:
        if skill["id"] not in VIDEOS:
            continue
        skill.pop("status", None)
        skill["video"] = VIDEOS[skill["id"]]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=1, ensure_ascii=False)
        f.write("\n")


def bank_qp():
    b = Bank("quadratic-program")
    p = PREV["quadratic-program"]
    b.mc(
        1,
        r"An unconstrained quadratic is minimized from the linear system given by its Hessian. The same quadratic, now with affine equalities and inequalities, is a convex quadratic program when the Hessian is",
        [
            r"negative definite, so every eigenvalue is negative",
            r"positive semidefinite, so every eigenvalue is nonnegative",
            r"invertible, whether or not an eigenvalue is negative",
            r"the zero matrix only, with every squared term removed",
        ],
        1,
        r"Affine constraints describe a convex set. The quadratic objective passes the second-order test exactly when its Hessian is positive semidefinite. A negative eigenvalue makes the objective nonconvex, and invertibility does not repair that eigenvalue. The zero Hessian is allowed, because it is positive semidefinite, but it is not the only allowed Hessian.",
        BOWL, ABOWL,
    )
    b.num(
        1,
        r"Minimize \(x^2+y^2\) subject to \(x+y=4\). What is the optimal value?",
        8, "(unitless)",
        r"The objective is a round bowl centered at the origin, and the constraint is the line \(x+y=4\). The point on that line closest to the origin is \((2,2)\), where the value is \(4+4=8\). The unconstrained minimizer is the origin, and it is not feasible. The number 4 is the sum of the coordinates, not the objective value. A value of 16 would be \(x^2+y^2\) at an endpoint such as \((4,0)\), which is feasible but not minimal.",
    )
    b.mc(
        1,
        r"Which constraint keeps this quadratic objective inside a quadratic program, rather than moving it into a problem with a curved constraint?",
        [
            r"\(x^2+y^2\le 4\)",
            r"\(xy\le 1\)",
            r"\(2x+y\le 4\)",
            r"\(\lvert x\rvert^2+\lvert y\rvert^2\le 9\)",
        ],
        2,
        r"A quadratic program allows affine equalities and inequalities only. The inequality \(2x+y\le 4\) is a half-space, so it is affine. The disk \(x^2+y^2\le 4\) and the squared-absolute disk are quadratic constraints. The product \(xy\le 1\) is quadratic and not affine.",
        HALF, AHALF,
    )
    b.order(
        2,
        r"Put these steps in the order that minimizes \((x-2)^2+(y-1)^2\) subject to \(x+y=6\). Each step uses the expression the previous step produced.",
        [
            "Substitute y = 6 - x into the objective, using the equality x+y=6.",
            "Expand that substitution into the single-variable function (x-2)^2+(5-x)^2.",
            "Differentiate that function of x and set the derivative 4x-14 equal to zero.",
            "Solve 4x-14=0 to get x=3.5, then recover y=6-x=2.5.",
        ],
        r"The equality has to be solved for y before it can be substituted. The substituted expression has to be expanded before its derivative is the specific linear polynomial 4x-14. That derivative has to be set to zero before it is solved, and y is recovered from the x that solve produces. Swapping an adjacent pair uses a polynomial that has not been built yet.",
    )
    b.num(
        2,
        r"Minimize \((x-1)^2+(y-4)^2\) subject to \(x+y=7\). What is the optimal value?",
        2, "(unitless)",
        r"Substitute \(y=7-x\). The objective becomes \((x-1)^2+(3-x)^2\). Its derivative is \(4x-8\), which vanishes at \(x=2\), so \(y=5\). The value is \((2-1)^2+(5-4)^2=2\). The number 7 is the constraint sum. The point \((1,4)\) has value 0 but is not feasible, because \(1+4\neq 7\). Stopping at \(x=2\) reports a decision rather than the value.",
    )
    b.num(
        2,
        r"Minimize \(4x^2\) subject to \(x\ge 3\). The coefficient 4 is positive. What is the optimal value?",
        36, "(unitless)",
        r"The parabola \(4x^2\) decreases as \(x\) moves toward 0. The constraint stops that move at \(x=3\), and the value there is \(4\cdot 9=36\). The number 3 is the decision, not the value. The number 4 is the coefficient. The unconstrained minimizer \(x=0\) has value 0 and is not feasible.",
    )
    b.sym(
        3,
        r"Let \(a>0\). The program minimizes \(\tfrac12 a(x-c)^2\) subject to the equality \(x=b\). Write the optimal value in \(a\), \(b\), and \(c\).",
        "a*(b-c)**2/2",
        {"a": (0.5, 3), "b": (-2, 2), "c": (-2, 2)},
        r"The equality fixes the only decision at \(x=b\). Substitute that point into the objective. One factor of \(a/2\) stays in front, and the inside of the square is the distance from \(b\) to \(c\)."
        "\n"
        r"• \(a(b-c)^2\) drops the one half."
        "\n"
        r"• \((b-c)^2/2\) drops the curvature \(a\)."
        "\n"
        r"• \(a(b-c)/2\) forgets the square.",
        ["(a/2)*(b-c)**2", "0.5*a*(b-c)**2"],
    )
    b.mc(
        3,
        r"A quadratic objective has diagonal Hessian entries 4 and 0, and every constraint is affine. The program is",
        [
            r"not convex, because a zero eigenvalue is a negative curvature",
            r"strictly convex, because a zero eigenvalue still separates level sets",
            r"convex, because both diagonal entries are nonnegative",
            r"unbounded below on every affine line",
        ],
        2,
        r"A diagonal Hessian is positive semidefinite exactly when every diagonal entry is nonnegative. Both 4 and 0 pass, so the objective is convex and the affine constraints keep the program convex. A zero eigenvalue is not negative curvature, and it does prevent strict convexity. The objective \(2x^2\) is bounded below by 0, so it is not unbounded on every line.",
    )
    b.multi(
        3,
        r"Which of these are convex quadratic programs?",
        [
            r"Minimize \(x^2+y^2\) subject to \(2x+y\le 4\).",
            r"Minimize \(x^2-y^2\) subject to \(x+y=0\).",
            r"Minimize \(x^2\) subject to \(x^2\le 1\).",
            r"Minimize \((x-2)^2+(y+1)^2\) subject to \(x+y=1\) and \(x\ge 0\).",
        ],
        [0, 3],
        r"The first objective has Hessian \(2I\), which is positive definite, and the constraint is a half-space. The fourth objective is a sum of squares, and both constraints are affine. The second Hessian has a negative eigenvalue, so the objective is not convex. The third constraint is a quadratic inequality, so the program is not a quadratic program.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The program minimizes \(x^2+y^2\) subject to \(x+y=2\).",
        [
            r"The Hessian of \(x^2+y^2\) is \(2I\), whose eigenvalues are positive, so the objective is convex.",
            r"The constraint \(x+y=2\) is affine.",
            r"A positive definite Hessian means the program is not convex, because convexity requires a negative eigenvalue.",
            r"On this affine line the minimizer is the feasible point where the gradient is parallel to \((1,1)\).",
        ],
        2,
        r"The Hessian \(2I\) is positive definite, so the objective is convex, and an affine equality keeps the program a convex quadratic program. The gradient of \(x^2+y^2\) is \((2x,2y)\). At \((1,1)\) it is parallel to the constraint normal \((1,1)\), and that point lies on the line. The false step reverses the eigenvalue test.",
        reasons=[
            "Convexity needs every eigenvalue nonnegative, and a positive definite Hessian passes that test.",
            "The equality x+y=2 is a quadratic constraint, so this is not a quadratic program.",
            "The Hessian 2I has a negative eigenvalue.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Minimize \(x^2+(y-5)^2\) subject to \(x+2y=5\). What is the optimal value?",
        5, "(unitless)",
        r"Substitute \(y=(5-x)/2\). The objective becomes \(x^2+(x+5)^2/4\). Its derivative is \((5x+5)/2\), which vanishes at \(x=-1\), so \(y=3\). The point satisfies \( -1+6=5\), and the value is \(1+(3-5)^2=5\). The unconstrained point \((0,5)\) has value 0 and misses the line, because \(0+10\neq 5\). The number \(-1\) is a decision, not the value.",
        preview=p,
    )
    b.mc(
        4,
        r"A maximum-margin linear separator minimizes \(\tfrac12\lVert w\rVert^2\) subject to one affine inequality per labeled point. That program is",
        [
            r"a nonconvex quadratic program, because the Hessian of \(\tfrac12\lVert w\rVert^2\) is indefinite",
            r"a linearly constrained problem whose objective is not quadratic",
            r"a convex quadratic program: the Hessian is the identity, and the constraints are affine",
            r"unconstrained, because the inequalities can be deleted without changing the minimizer",
        ],
        2,
        r"The objective \(\tfrac12\lVert w\rVert^2\) has Hessian equal to the identity, which is positive definite, so it is a strictly convex quadratic. Each labeled-point inequality is affine in the weights. Deleting those inequalities would leave the zero vector, which is not a separator. The Hessian is not indefinite.",
        preview=p,
    )
    b.save()


def bank_qcqp():
    b = Bank("quadratically-constrained-quadratic-program")
    p = PREV["quadratically-constrained-quadratic-program"]
    b.mc(
        1,
        r"A convex quadratic program allows only affine constraints. Which added constraint keeps the program convex?",
        [
            r"\(x^2-y^2\le 1\), whose Hessian has a negative eigenvalue",
            r"\(-x^2-y^2\le -1\), the outside of the unit disk",
            r"\((x-1)^2+(y-2)^2\le 9\), a disk",
            r"\(xy\le 1\), with an indefinite Hessian",
        ],
        2,
        r"A quadratic inequality \(g(x)\le 0\) describes a convex set when the Hessian of \(g\) is positive semidefinite. The disk is a sum of squares, so its Hessian is positive semidefinite. A negative eigenvalue, the outside of a disk, and the product \(xy\) all fail that test.",
        DISK, ADISK,
    )
    b.num(
        1,
        r"Minimize \((x-6)^2\) subject to \(x^2\le 4\). What is the optimal value?",
        16, "(unitless)",
        r"The constraint is the interval \([-2,2]\). The parabola \((x-6)^2\) decreases as \(x\) increases toward 6, so the best feasible point is the right endpoint \(x=2\). The value is \((2-6)^2=16\). The number 6 is the unconstrained decision, and it is not feasible. The number 4 is the right-hand side of the constraint, not the objective value. The left endpoint \(x=-2\) gives \(({-2}-6)^2=64\), which is worse.",
    )
    b.mc(
        1,
        r"The objective of a quadratic program is already convex, and its constraints are affine. You add one quadratic inequality. The new program stays convex when",
        [
            r"the new left-hand side has a positive semidefinite Hessian",
            r"the new left-hand side has a negative eigenvalue",
            r"the new constraint is the outside of a disk",
            r"the new constraint uses a square, regardless of the sign of the Hessian",
        ],
        0,
        r"Convexity of a sublevel set \(\{x:g(x)\le 0\}\) follows when \(g\) is a convex function. For a quadratic \(g\), that is the positive-semidefinite test on its Hessian. A negative eigenvalue makes \(g\) nonconvex. The outside of a disk is a superlevel set of a convex square, and it is not convex. Using a square is not enough: the sign of the Hessian matters.",
    )
    b.order(
        2,
        r"Put these steps in the order that decides whether a program with quadratic inequalities is a convex quadratically constrained quadratic program. Each step uses the object the previous step named.",
        [
            "Write every constraint with a quadratic function on the left of a less-than-or-equal sign.",
            "Read the Hessian of the objective and the Hessian of each of those left-hand sides.",
            "Accept the program as convex only when every one of those Hessians is positive semidefinite.",
            "Treat a minimizer of an accepted program as a global minimizer.",
        ],
        r"The left-hand sides have to be written before their Hessians are the matrices being tested. Those Hessians have to be read before the positive-semidefinite test can accept or reject them. Acceptance has to come before a minimizer is called global. Swapping an adjacent pair tests a matrix or a status that has not been produced yet.",
    )
    b.num(
        2,
        r"Minimize \((x-5)^2+(y-5)^2\) subject to \((x-2)^2+(y-1)^2\le 9\). The unconstrained point lies outside the disk. What is the optimal value?",
        4, "(unitless)",
        r"The feasible set is the disk of radius 3 centered at \((2,1)\). The point \((5,5)\) lies at distance \(\sqrt{3^2+4^2}=5\) from the center, so it is outside. The nearest feasible point is 2 units closer, on the segment from the center to \((5,5)\). The squared distance from \((5,5)\) to that point is \(2^2=4\). The radius 3 is not the objective value. The center is feasible and scores \((2-5)^2+(1-5)^2=25\), which is worse than 4.",
        DISK, ADISK,
    )
    b.num(
        2,
        r"Minimize \((x-1)^2+(y-1)^2\) subject to \((x-4)^2+(y-5)^2\le 4\). The unconstrained point lies outside the disk. What is the optimal value?",
        9, "(unitless)",
        r"The disk has center \((4,5)\) and radius 2. The point \((1,1)\) is at distance 5 from the center, because the offset is \((-3,-4)\). The gap from the point to the disk is \(5-2=3\), and the squared gap is 9. The squared distance all the way to the center is 25, which scores the center, not the boundary point that the objective prefers. The radius 2 is the constraint, not the objective value.",
    )
    b.sym(
        3,
        r"Let \(c>m+\sqrt{s}\) with \(s>0\). Minimize \((x-c)^2\) subject to \((x-m)^2\le s\). Write the optimal value in \(c\), \(m\), and \(s\).",
        "(c-m-sqrt(s))**2",
        {"c": (4, 6), "m": (0.2, 1), "s": (0.25, 1)},
        r"The constraint is the interval centered at \(m\) with radius \(\sqrt{s}\). Because \(c\) lies to the right of that interval, the best feasible point is the right endpoint \(m+\sqrt{s}\). The optimal value is the square of the gap from \(c\) to that endpoint."
        "\n"
        r"• \((c-m)^2\) forgets the radius."
        "\n"
        r"• \((c-m-s)^2\) subtracts \(s\) instead of its square root."
        "\n"
        r"• \(c-m-\sqrt{s}\) is the gap, not the objective value.",
        ["(c-(m+sqrt(s)))**2", "(c-m-sqrt(s))*(c-m-sqrt(s))"],
    )
    b.mc(
        3,
        r"The inequality \(x^2-4y\le 0\) is the set where \(y\) sits above a square. Its Hessian in \((x,y)\) is diagonal with entries 2 and 0. This constraint is",
        [
            r"not convex, because one diagonal entry is zero",
            r"not convex, because a square is curved",
            r"convex, because both diagonal entries are nonnegative",
            r"a half-space, because the boundary is a straight line",
        ],
        2,
        r"The left-hand side \(x^2-4y\) has Hessian \(\mathrm{diag}(2,0)\), which is positive semidefinite, so the sublevel set is convex. A zero eigenvalue does not spoil that test. The boundary is a parabola, not a straight line, but a curved boundary can still enclose a convex set. The epigraph of a convex function is the picture of that fact.",
    )
    b.multi(
        3,
        r"Which inequalities are convex quadratic constraints?",
        [
            r"\((x-1)^2+(y+2)^2\le 8\)",
            r"\(-x^2-y^2\le -1\)",
            r"\((2x+y-1)^2\le 9\)",
            r"\(xy\le 1\)",
        ],
        [0, 2],
        r"The disk is a sum of squares, so its Hessian is positive semidefinite. The square of an affine function has a rank-one positive-semidefinite Hessian, and its sublevel set is a closed slab between two parallel lines. The inequality \(-x^2-y^2\le -1\) is the outside of the unit disk, and the Hessian is negative definite. The product \(xy\) has an indefinite Hessian, so its sublevel set is not convex.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The constraint under discussion is \(x^2\ge 4\).",
        [
            r"The set \(x^2\ge 4\) contains \(-3\) and \(3\) but not \(0\).",
            r"The chord from \(-3\) to \(3\) therefore leaves the set, so the set is not convex.",
            r"Writing the set as \(4-x^2\le 0\) produces a left-hand side whose second derivative is negative, and a negative second derivative means that left-hand side is convex.",
            r"A convex quadratic constraint would instead need a positive semidefinite Hessian on the left of a less-than-or-equal sign.",
        ],
        2,
        r"The set is the outside of an interval, and the chord test fails, so it is not convex. The rewritten left-hand side \(4-x^2\) has second derivative \(-2\), which means it is concave, not convex. A convex quadratic constraint needs the opposite curvature test. The false step swaps that sign.",
        reasons=[
            "A negative second derivative means the left-hand side is concave, not convex.",
            "The points -3 and 3 are not both feasible.",
            "The chord from -3 to 3 stays inside the set.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Minimize \((x-8)^2+y^2\) subject to \(x^2+y^2\le 9\). The unconstrained point lies outside the disk. What is the optimal value?",
        25, "(unitless)",
        r"The feasible set is the disk of radius 3 centered at the origin. The point \((8,0)\) is at distance 8 from the origin, so the gap to the disk is \(8-3=5\). The squared gap is 25. The nearest feasible point is \((3,0)\), and \((3-8)^2=25\). The squared distance to the origin is 64, which is the score of the center, not of the boundary point the objective prefers. The radius 3 is not the objective value.",
        DISK, ADISK,
        preview=p,
    )
    b.mc(
        4,
        r"The disk \(\lVert(x,y)\rVert\le 3\) is a convex quadratic constraint. It is also the special case of a later form in which a Euclidean norm is bounded by an affine function. That later form is",
        [
            r"an equality-constrained Newton step",
            r"a second-order-cone constraint, here with a constant upper bound",
            r"a semidefinite constraint on a nonsymmetric matrix",
            r"an absolute penalty added to a squared residual",
        ],
        1,
        r"The inequality \(\lVert(x,y)\rVert\le 3\) already has a Euclidean norm on the left and an affine function, the constant 3, on the right. That is a second-order-cone constraint. A Newton step is an algorithm, not this constraint. A semidefinite constraint asks a symmetric matrix to be positive semidefinite. An absolute penalty is an objective term, not this disk.",
        preview=p,
    )
    b.save()


def bank_socp():
    b = Bank("second-order-cone-program")
    p = PREV["second-order-cone-program"]
    b.mc(
        1,
        r"A Euclidean norm is nonnegative. Which inequality is already a second-order-cone constraint, a norm of an affine map bounded by an affine function?",
        [
            r"\(\lVert(x,y)\rVert^2\le 4\)",
            r"\(\lVert(x,y)\rVert\le x^2\)",
            r"\(\lVert(2x+1,\ y-3)\rVert\le 4-x\)",
            r"\(x+y\le \lVert(x,y)\rVert\)",
        ],
        2,
        r"The third inequality has an affine map inside the norm and an affine upper bound. Squaring the norm changes the form, even when a constant bound would make it equivalent. A squared upper bound is not affine. The reversed inequality, a norm bounded from below by an affine function, is not this constraint and is not convex.",
    )
    b.num(
        1,
        r"What is the smallest \(t\) such that \(\lVert(3,-4)\rVert\le t\)?",
        5, "(unitless)",
        r"The Euclidean norm of \((3,-4)\) is \(\sqrt{9+16}=5\), so the smallest feasible \(t\) is 5. The sum of absolute coordinates is 7, which is a different norm. The larger coordinate 4 is not the Euclidean length. A negative \(t\) cannot bound a norm.",
        DISK, ADISK,
    )
    b.mc(
        1,
        r"The constraint \(\lVert(x,y)\rVert\le x-4\) is infeasible for some \(x\) even before \(y\) is chosen. It is infeasible whenever",
        [
            r"\(x-4>0\), because a positive upper bound cannot dominate a norm",
            r"\(x-4<0\), because a norm cannot be less than or equal to a negative number",
            r"\(y=0\), because the norm then equals \(\lvert x\rvert\)",
            r"\(x>4\), because the upper bound then grows",
        ],
        1,
        r"A Euclidean norm is at least 0. If the affine upper bound is negative, no vector satisfies the inequality. A positive upper bound can be feasible, for example at a small \((x,y)\). Setting \(y=0\) does not by itself make the constraint infeasible. Growth of the upper bound makes feasibility easier, not harder.",
    )
    b.order(
        2,
        r"Put these steps in the order that turns the quadratic inequality \(x^2\le t\) into one second-order-cone constraint. Each step rewrites the claim the previous step produced.",
        [
            "Start from the quadratic inequality x^2 <= t.",
            "Rewrite it as the squared comparison (2x)^2+(t-1)^2 <= (t+1)^2.",
            "Take nonnegative square roots, which requires the right-hand side t+1 to be nonnegative.",
            "Write the second-order-cone constraint ||(2x, t-1)|| <= t+1.",
        ],
        r"The squared comparison is the expansion of this particular quadratic inequality, so it comes second. The square root is taken of that comparison, so it comes third, and the cone inequality is what the root says, so it comes last. Expanding the squared comparison recovers \(4x^2\le 4t\), which is the inequality you started with. Swapping an adjacent pair roots or names a comparison that is not there yet.",
    )
    b.num(
        2,
        r"For \(x=3\) and \(t=9\), the cone form of \(x^2\le t\) is \(\lVert(2x,\ t-1)\rVert\le t+1\). What is the value of the norm on the left?",
        10, "(unitless)",
        r"The left-hand vector is \((6,8)\), and \(\sqrt{36+64}=10\). The right-hand side is \(t+1=10\), so this point is on the boundary of \(x^2\le t\), because \(9=9\). The coordinate 6 is one entry, not the norm. The sum \(6+8=14\) is not the Euclidean norm.",
    )
    b.num(
        2,
        r"Minimize \(t\) subject to \(\lVert(x,y)\rVert\le t\) and \(x+y=6\). What is the optimal \(t\)?",
        3 * math.sqrt(2), "(unitless)",
        r"The smallest \(t\) is the Euclidean distance from the origin to the line \(x+y=6\). The nearest point is \((3,3)\), and its norm is \(\sqrt{18}=3\sqrt{2}\). The intercept 6 is the value of \(x\) when \(y=0\), and that feasible point has a larger norm. The sum \(x+y\) is fixed at 6 and is not the Euclidean norm.",
    )
    b.sym(
        3,
        r"The second-order-cone constraint \(\lVert(ax+u,\ bx+v)\rVert\le t\) has an affine map inside the norm. Write the left-hand side in \(a\), \(b\), \(x\), \(u\), and \(v\).",
        "sqrt((a*x+u)**2+(b*x+v)**2)",
        {"a": (0.5, 2), "b": (-2, 2), "x": (-2, 2), "u": (-2, 2), "v": (0.5, 2)},
        r"The left-hand side is the Euclidean norm of the two affine expressions. Square each one, add, and take the square root. The upper bound \(t\) is not part of the left-hand side."
        "\n"
        r"• \((ax+u)^2+(bx+v)^2\) stops before the square root."
        "\n"
        r"• \(\lvert ax+u\rvert+\lvert bx+v\rvert\) is the 1-norm."
        "\n"
        r"• \(\sqrt{(ax)^2+(bx)^2}\) drops the translations \(u\) and \(v\).",
    )
    b.mc(
        3,
        r"Which point is feasible for \(\lVert(x,y)\rVert\le 2x+1\)?",
        [
            r"\((x,y)=(-1,0)\), where the upper bound is \(-1\)",
            r"\((x,y)=(0,3)\), where the norm is 3 and the upper bound is 1",
            r"\((x,y)=(1,1)\), where the norm is \(\sqrt{2}\) and the upper bound is 3",
            r"\((x,y)=(0,0)\) is infeasible because the upper bound is positive",
        ],
        2,
        r"At \((1,1)\) the norm \(\sqrt{2}\) is about 1.41, and the upper bound is 3, so the inequality holds. At \((-1,0)\) the upper bound is negative, which a norm cannot meet. At \((0,3)\) the norm is 3 and the upper bound is 1. The origin has norm 0 and upper bound 1, so it is feasible. A positive upper bound is not a reason to reject the origin.",
    )
    b.multi(
        3,
        r"Which inequalities are second-order-cone constraints as written, with a Euclidean norm of an affine map on the left and an affine upper bound on the right?",
        [
            r"\(\lVert(2x+1,\ y-4)\rVert\le 3x+5\)",
            r"\(\lVert(x,y)\rVert^2\le 4\)",
            r"\(x+y\le \lVert(x,y)\rVert\)",
            r"\(\lVert(x-y,\ 2)\rVert\le 1\)",
        ],
        [0, 3],
        r"The first inequality has an affine vector inside the norm and an affine upper bound. The fourth has the same shape, with a constant second coordinate and a constant upper bound. Squaring the norm leaves a quadratic inequality, which is not yet the cone form. The reversed inequality bounds the norm from below and is not convex.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The constraint is \(\lVert(x,y)\rVert\le x-3\).",
        [
            r"A feasible point needs \(x-3\ge 0\), because the left side is a norm.",
            r"Wherever \(x-3\ge 0\), squaring both sides gives \(x^2+y^2\le (x-3)^2\).",
            r"Squaring both sides is valid for every real \(x\), including values below 3, because both sides of any inequality may be squared.",
            r"At \(x=0\) the upper bound is \(-3\), so no choice of \(y\) is feasible.",
        ],
        2,
        r"The norm is nonnegative, so a negative upper bound is immediately infeasible, and \(x=0\) is such a point. Where the upper bound is nonnegative, both sides are nonnegative and squaring preserves the inequality. Squaring is not valid on the infeasible side: a negative number and a positive norm do not keep their order after an even power. The false step drops that sign check.",
        reasons=[
            "Squaring preserves the inequality only when both sides are nonnegative, and a norm is never less than or equal to a negative number.",
            "The upper bound x-3 is always nonnegative.",
            "At x=0 the upper bound is positive, so y=0 is feasible.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"The one-dimensional cone constraint \(\lvert 3x-1\rvert\le 5\) is a Euclidean norm of an affine expression, bounded by a constant. What is the largest feasible \(x\)?",
        2, "(unitless)",
        r"The inequality says \(-5\le 3x-1\le 5\). The right half is \(3x\le 6\), so \(x\le 2\). The left half is \(3x\ge -4\), so \(x\ge -4/3\). The largest feasible \(x\) is 2. At that point \(3\cdot 2-1=5\), so the bound is met. The lower endpoint \(-4/3\) is the other end, not the largest \(x\). The number 5 is the upper bound on the absolute value, not the decision.",
        preview=p,
    )
    b.mc(
        4,
        r"A convex quadratic constraint such as \(x^2\le t\) can be rewritten as one second-order-cone inequality. A later program instead asks a symmetric affine matrix to be positive semidefinite, and it can embed this cone by a block complement. That later program is",
        [
            r"an unconstrained quadratic minimization",
            r"a semidefinite program",
            r"a coordinate update on an absolute penalty",
            r"a gradient step with a fixed length",
        ],
        1,
        r"The positive-semidefinite constraint on an affine symmetric matrix is a semidefinite program. The block complement that turns \(t\ge x^2\) into a 2 by 2 matrix constraint is how this cone sits inside that program. An unconstrained quadratic has no cone constraint. A coordinate update and a gradient step are algorithms, not this matrix form.",
        preview=p,
    )
    b.save()


def bank_sdp():
    b = Bank("semidefinite-program")
    p = PREV["semidefinite-program"]
    b.mc(
        1,
        r"A symmetric matrix is positive semidefinite when \(z^T M z\ge 0\) for every \(z\). For the 2 by 2 matrix \(\begin{bmatrix} a & b \\ b & c \end{bmatrix}\), that property holds exactly when",
        [
            r"\(a\ge 0\), \(c\ge 0\), and \(ac\ge b^2\)",
            r"\(a\ge 0\) and \(c\ge 0\), with no condition on \(b\)",
            r"\(ac\ge b^2\), even if \(a\) is negative",
            r"\(b\ge 0\), with no condition on the diagonal",
        ],
        0,
        r"Both diagonal entries must be nonnegative, and the determinant test \(ac-b^2\ge 0\) must hold as well. Nonnegative diagonal entries alone miss a large off-diagonal entry. The product test alone misses a negative diagonal. The sign of the off-diagonal entry is not the test: \(b\) is squared in \(ac\ge b^2\).",
    )
    b.num(
        1,
        r"For \(M=\begin{bmatrix} 4 & 1 \\ 1 & 4 \end{bmatrix}\), compute the determinant gap \(ac-b^2\).",
        15, "(unitless)",
        r"Here \(a=4\), \(b=1\), and \(c=4\), so \(ac-b^2=16-1=15\). Both diagonal entries are positive and the gap is positive, so \(M\) is positive definite. The product \(ac=16\) forgets to subtract \(b^2\). The trace \(a+c=8\) is a different symmetric function. The off-diagonal entry 1 is not the gap.",
    )
    b.mc(
        1,
        r"The matrix \(\begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}\) has determinant \(1-4=-3\). It is",
        [
            r"positive semidefinite, because both diagonal entries are positive",
            r"not positive semidefinite, because the determinant is negative",
            r"positive semidefinite, because the off-diagonal entries are positive",
            r"undefined as a semidefinite constraint, because the matrix is symmetric",
        ],
        1,
        r"Positive diagonal entries are necessary and not sufficient. Here \(ac-b^2=-3<0\), so one eigenvalue is negative and the matrix is not positive semidefinite. The sign of the off-diagonal entries does not replace the determinant test. Symmetry is required for this constraint, and this matrix has it. The failure is the determinant, not the symmetry.",
    )
    b.order(
        2,
        r"Put these steps in the order that turns \(t\ge x^2\) into a 2 by 2 semidefinite constraint by a block complement. Each step uses the matrix or the complement the previous step built.",
        [
            "Place t, x, and the number 1 into the symmetric matrix with t and 1 on the diagonal and x off the diagonal.",
            "Using the bottom-right entry 1, form the complement t-x^2.",
            "Require that complement to be nonnegative, and keep the bottom-right entry positive.",
            "Conclude that the matrix constraint holds exactly when t >= x^2.",
        ],
        r"The matrix has to be filled before the complement of its leading entry is \(t-x^2\). That complement has to be formed before it can be required to be nonnegative. The conclusion \(t\ge x^2\) is what that requirement says, because the bottom-right entry is the positive number 1. Swapping an adjacent pair uses a complement or a conclusion that has not been formed.",
    )
    b.num(
        2,
        r"What is the smallest \(t\) such that \(\begin{bmatrix} t & 3 \\ 3 & 4 \end{bmatrix}\) is positive semidefinite?",
        2.25, "(unitless)",
        r"The bottom-right entry 4 is positive. The diagonal test also needs \(t\ge 0\), and the determinant test needs \(4t\ge 9\), so \(t\ge 9/4=2.25\). That lower bound is already positive, so it is the smallest feasible \(t\). The number 3 is the off-diagonal entry. The number 4 is the fixed diagonal entry. The product \(3\cdot 4=12\) is not the bound on \(t\).",
    )
    b.num(
        2,
        r"What is the smaller eigenvalue of \(\begin{bmatrix} 6 & 2 \\ 2 & 3 \end{bmatrix}\)?",
        2, "(unitless)",
        r"The trace is 9 and the determinant is \(18-4=14\). The eigenvalues are the roots of \(\lambda^2-9\lambda+14=0\), which factors as \((\lambda-7)(\lambda-2)=0\). The roots are 7 and 2, so the smaller one is 2. Both are positive, and the matrix is positive definite. The trace 9 is the sum of the eigenvalues, not the smaller one. The off-diagonal entry 2 happens to equal the smaller eigenvalue in this matrix; the factorization is what identifies it.",
        HESS, AHESS,
    )
    b.sym(
        3,
        r"Let \(p>0\). What is the smallest \(t\) such that \(\begin{bmatrix} t & s \\ s & p \end{bmatrix}\) is positive semidefinite? Write it in \(s\) and \(p\).",
        "s**2/p",
        {"s": (-2, 2), "p": (0.5, 3)},
        r"The entry \(p\) is already positive. The determinant test says \(tp\ge s^2\), so \(t\ge s^2/p\). That quotient is nonnegative, so it also meets \(t\ge 0\). It is the smallest feasible \(t\)."
        "\n"
        r"• \(s^2\) forgets to divide by \(p\)."
        "\n"
        r"• \(p/s^2\) inverts the ratio."
        "\n"
        r"• \(s/p\) drops a factor of \(s\).",
        ["(s*s)/p", "s*s/p"],
    )
    b.mc(
        3,
        r"A semidefinite constraint asks an affine matrix to be positive semidefinite. The matrix in that constraint must be",
        [
            r"symmetric, because the quadratic form does not see the skew part",
            r"triangular, with zeros below the diagonal",
            r"a permutation matrix",
            r"nonsymmetric, so that the off-diagonal entries can differ",
        ],
        0,
        r"The quadratic form \(z^T M z\) depends only on the symmetric part of \(M\). The semidefinite constraint is stated for a symmetric matrix, and each coefficient matrix in the affine expression is symmetric. A triangular pattern, a permutation, or a nonsymmetric pair of off-diagonal entries is a different requirement.",
    )
    b.multi(
        3,
        r"Which of these symmetric matrices are positive semidefinite?",
        [
            r"\(\begin{bmatrix} 2 & 0 \\ 0 & 5 \end{bmatrix}\)",
            r"\(\begin{bmatrix} 2 & 3 \\ 3 & 2 \end{bmatrix}\)",
            r"\(\begin{bmatrix} 0 & 0 \\ 0 & 0 \end{bmatrix}\)",
            r"\(\begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}\)",
        ],
        [0, 2],
        r"The first matrix is diagonal with positive entries, so both eigenvalues are positive. The zero matrix gives \(z^T 0 z=0\), which meets \(\ge 0\), so it is positive semidefinite. The second has determinant \(4-9<0\), so one eigenvalue is negative. The fourth has a negative diagonal entry, so the corresponding standard-basis vector produces a negative square.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The matrix is \(\begin{bmatrix} t & 2 \\ 2 & 1 \end{bmatrix}\).",
        [
            r"The matrix is symmetric.",
            r"The bottom-right entry equals 1, which is positive.",
            r"The complement relative to that entry is \(t-4\), so \(t\ge 4\) is required.",
            r"The matrix is positive semidefinite as soon as \(t\ge 0\), because the top-left entry is the only one that can fail.",
        ],
        3,
        r"Symmetry holds, the pivot 1 is positive, and the complement is \(t-2^2/1=t-4\). Nonnegativity of that complement is \(t\ge 4\), which is stronger than \(t\ge 0\). At \(t=0\) the determinant gap is \(-4\), so the matrix is not positive semidefinite. The false step drops the complement.",
        reasons=[
            "The complement t-4 must be nonnegative, so t>=0 is not enough.",
            "The matrix is not symmetric.",
            "The bottom-right entry is negative, so the complement is undefined.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"What is the smallest \(t\) such that \(\begin{bmatrix} t & 6 \\ 6 & 2 \end{bmatrix}\) is positive semidefinite?",
        18, "(unitless)",
        r"The bottom-right entry 2 is positive. The determinant test requires \(2t\ge 36\), so \(t\ge 18\). That bound is positive, so the diagonal test \(t\ge 0\) does not raise it. The off-diagonal entry 6 is not the bound. The product \(6\cdot 2=12\) forgets that the complement divides \(6^2\) by 2.",
        preview=p,
    )
    b.mc(
        4,
        r"A later problem chooses a positive definite shape matrix for the largest ellipsoid that fits inside a list of half-spaces. That problem is not itself the general spectrahedron. The shared piece is",
        [
            r"a free nonsymmetric matrix with no definiteness requirement",
            r"a positive definite matrix used as a decision, which this skill tests with a semidefinite constraint",
            r"an absolute penalty on the center of the ellipsoid",
            r"a fixed-step gradient iteration",
        ],
        1,
        r"The shape matrix has to be positive definite for the ellipsoid to have positive volume in every direction. Positive-definiteness is the strict form of the semidefinite constraint this skill studies. The ellipsoid problem adds a volume objective and half-space inequalities. It does not use an absolute penalty or a gradient iteration as the definition of the shape.",
        preview=p,
    )
    b.save()


def bank_conic():
    b = Bank("conic-duality")
    p = PREV["conic-duality"]
    b.mc(
        1,
        r"Strong duality says a zero gap can hold when a constraint qualification is met. For a cone program, the dual replaces the cone \(K\) by its dual cone. A vector \(s\) lies in that dual cone when",
        [
            r"\(s^T z\ge 0\) for every \(z\) in \(K\)",
            r"\(s^T z\le 0\) for every \(z\) in \(K\)",
            r"\(s\) is orthogonal to every vector in \(K\)",
            r"\(s\) has the same Euclidean length as some vector in \(K\)",
        ],
        0,
        r"The dual cone is the set of vectors that make a nonnegative inner product with every vector of \(K\). The opposite sign describes the dual of \(-K\). Orthogonality would force the inner product to be zero, which is stronger than \(\ge 0\). Equal length is not a cone condition.",
        ORTH, AORTH,
    )
    b.num(
        1,
        r"Minimize \(3x+4y\) subject to \(x+y=5\) and \(x\ge 0\), \(y\ge 0\). What is the optimal value?",
        15, "(unitless)",
        r"Both coefficients are positive, and \(x\) is the cheaper one. Put the whole right-hand side on \(x\): \(x=5\), \(y=0\), and the cost is \(3\cdot 5=15\). Using only \(y\) costs \(4\cdot 5=20\), which is worse. The right-hand side 5 is not the cost. A negative variable would leave the orthant.",
    )
    b.mc(
        1,
        r"The nonnegative orthant is the cone \(K=\{z:z\ge 0\}\). Its dual cone is",
        [
            r"the nonpositive orthant",
            r"the nonnegative orthant, so this cone is self-dual",
            r"the whole space, because every inner product is free",
            r"the origin only",
        ],
        1,
        r"A vector \(s\) satisfies \(s^T z\ge 0\) for every \(z\ge 0\) exactly when every coordinate of \(s\) is nonnegative. If a coordinate of \(s\) is negative, the corresponding standard-basis vector in \(K\) makes the inner product negative. So the dual cone is the orthant itself.",
        ORTH, AORTH,
    )
    b.order(
        2,
        r"Put these steps in the order that proves weak duality for a feasible pair. The primal point \(x\) lies in \(K\) and satisfies \(Ax=b\). The dual pair satisfies \(A^T y+s=c\) with \(s\) in the dual cone. Each step uses the identity the previous step wrote.",
        [
            "Start from the primal cost c^T x and the dual cost b^T y.",
            "Replace c by A^T y + s inside c^T x.",
            "Replace Ax by b inside y^T A x, using Ax=b.",
            "Conclude that c^T x - b^T y equals s^T x, which is nonnegative.",
        ],
        r"The two costs have to be named before \(c\) is replaced. The replacement produces \(y^T A x+s^T x\), and only then does \(Ax=b\) turn \(y^T A x\) into \(b^T y\). The gap identity is what remains. Nonnegativity uses \(s\) in the dual cone and \(x\) in \(K\), which the last step is allowed to use because those memberships were given before the algebra. Swapping an adjacent pair cancels a term that has not been substituted.",
    )
    b.num(
        2,
        r"Minimize \(2x+5y\) subject to \(x+y=3\) and \(x\ge 0\), \(y\ge 0\). The dual maximizes \(3z\) subject to \(z\le 2\) and \(z\le 5\). What is the optimal dual multiplier \(z\)?",
        2, "(unitless)",
        r"The dual constraints are \(z\le 2\) and \(z\le 5\), so the tighter one is \(z\le 2\). The objective \(3z\) increases with \(z\), and the best feasible multiplier is \(z=2\). The other bound \(z=5\) violates \(z\le 2\). The primal optimal value is \(2\cdot 3=6\), which matches \(3\cdot 2\), but the question asks for the multiplier. The right-hand side 3 is not \(z\).",
    )
    b.num(
        2,
        r"Take \(c=(4,1)\), \(x=(1,3)\), \(A=(1,\ 1)\), \(b=4\), \(y=1\), and \(s=(3,0)\). Then \(Ax=b\) and \(A^T y+s=c\), and both \(x\) and \(s\) lie in the nonnegative orthant. What is \(c^T x-b^T y\)?",
        3, "(unitless)",
        r"The primal cost is \(4\cdot 1+1\cdot 3=7\). The dual cost is \(4\cdot 1=4\). The difference is 3. The same number is \(s^T x=3\cdot 1+0\cdot 3\). Weak duality says this gap is nonnegative, and here it equals 3. The multiplier \(y=1\) is not the gap. The right-hand side \(b=4\) is the dual objective, not the gap.",
    )
    b.sym(
        3,
        r"In one coordinate the dual equality is \(a y+s=c\). Solve it for the dual-cone slack \(s\), as an expression in \(c\), \(a\), and \(y\).",
        "c-a*y",
        {"c": (-2, 2), "a": (0.5, 2), "y": (-2, 2)},
        r"The equality says the cost coefficient splits into the equality contribution \(ay\) and the slack \(s\). Subtract \(ay\) from \(c\). For the nonnegative orthant this slack still has to be nonnegative before the pair is dual feasible. The expression itself is only the equality."
        "\n"
        r"• \(c+ay\) adds the term that should be moved."
        "\n"
        r"• \(a y-c\) swaps the sign."
        "\n"
        r"• \(c/a-y\) divides as if the equality were a product set to zero.",
        ["c-(a*y)", "-a*y+c"],
    )
    b.mc(
        3,
        r"The second-order cone \(\{(u,t):\lVert u\rVert\le t\}\) and the positive-semidefinite cone are both self-dual. Which cone below is not equal to its dual?",
        [
            r"the nonnegative orthant",
            r"the second-order cone",
            r"the positive-semidefinite cone",
            r"the cone that contains only the origin in \(\mathbb{R}\)",
        ],
        3,
        r"A vector \(s\) makes a nonnegative product with the only member of \(\{0\}\) for every \(s\). The dual of the origin is the whole line, which is larger than the origin. The orthant, the second-order cone, and the positive-semidefinite cone each coincide with their duals, which is why their dual constraints have the same shape as the primal cone constraints.",
    )
    b.multi(
        3,
        r"Which statements are true for a cone program over the nonnegative orthant?",
        [
            r"A feasible pair with primal value 8 and dual value 5 satisfies weak duality.",
            r"A feasible pair with primal value 4 and dual value 4 has zero gap.",
            r"A feasible pair can have primal value 3 and dual value 6.",
            r"The vector \(s=(-1,\ 2)\) lies in the dual cone.",
        ],
        [0, 1],
        r"Weak duality says every dual feasible value is at most every primal feasible value. Both \(5\le 8\) and \(4\le 4\) agree with that, and equal values are a zero gap. A dual value 6 above a primal value 3 would contradict the inequality, so that pair cannot both be feasible. A negative coordinate keeps \(s\) out of the dual orthant: the first standard basis vector in the primal cone makes the inner product \(-1\).",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails.",
        [
            r"A vector \(s\) is in the dual cone when \(s^T z\ge 0\) for every \(z\) in the primal cone.",
            r"For the nonnegative orthant, that test holds exactly when every coordinate of \(s\) is nonnegative.",
            r"Therefore \(s=(-1,\ 2)\) lies in the dual of the nonnegative orthant.",
            r"For a feasible pair with \(A^T y+s=c\) and \(Ax=b\), the gap \(c^T x-b^T y\) equals \(s^T x\).",
        ],
        2,
        r"The dual-cone test and the orthant specialization are right, and the gap identity is the weak-duality algebra. The vector \((-1,2)\) fails the coordinate test in the first coordinate. Its inner product with \((1,0)\) is \(-1\), so it is not in the dual orthant. The false step accepts that vector anyway.",
        reasons=[
            "The first coordinate of s is negative, so s is not in the dual orthant.",
            "The dual cone requires s^T z <= 0 for every z in the primal cone.",
            "The gap identity uses s^T x with the opposite sign.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Minimize \(4x+y\) subject to \(x+y=2\) and \(x\ge 0\), \(y\ge 0\). What is the optimal value?",
        2, "(unitless)",
        r"The coefficient of \(y\) is 1 and the coefficient of \(x\) is 4, so \(y\) is cheaper. Put the whole right-hand side on \(y\): \(y=2\), \(x=0\), and the cost is 2. Using only \(x\) costs 8. The dual multiplier is at most 1, and the dual objective \(2z\) reaches 2 at \(z=1\), matching the primal. The right-hand side is the optimal value here only because the cheaper coefficient is 1.",
        preview=p,
    )
    b.mc(
        4,
        r"A later interior method keeps a dual-cone multiplier and drives a gap down by Newton steps on a perturbed multiplier system. The certificate that method tracks is the one built here. What does conic duality contribute to that method?",
        [
            r"It deletes the dual cone and keeps only the primal equalities.",
            r"It supplies the dual cone and the gap \(s^T x\), which the later method drives toward zero.",
            r"It replaces every cone by a sphere of radius 1.",
            r"It shows that every cone program is infeasible.",
        ],
        1,
        r"The dual cone is the membership constraint on \(s\), and \(s^T x\) is the gap between a feasible primal cost and a feasible dual cost. A later interior method keeps that certificate and drives the gap down. It does not delete the dual cone, replace the cone by a sphere, or declare every cone program infeasible.",
        preview=p,
    )
    b.save()


def bank_lasso():
    b = Bank("lasso-stationarity")
    p = PREV["lasso-stationarity"]
    b.mc(
        1,
        r"The lasso objective uses \(\lambda\lVert x\rVert_1\) with no leading one half on the squared residual. The absolute value \(\lvert t\rvert\) is not differentiable at 0. Its subdifferential there is",
        [
            r"the single number 0",
            r"the interval \([-1,\ 1]\)",
            r"empty, because a corner has no slope",
            r"the two-point set \(\{-1,\ 1\}\), excluding the slopes in between",
        ],
        1,
        r"Every slope between the left derivative \(-1\) and the right derivative \(1\) is a subgradient at the corner. The subdifferential is the whole interval. It contains 0, but it is not only 0. It is not empty, and it is not only the two endpoints.",
        SOFT, ASOFT,
    )
    b.num(
        1,
        r"The penalty weight is \(\lambda=2\), so the soft-threshold level is \(\lambda/2=1\). The input coordinate is \(z=4\). What is the soft-thresholded coordinate?",
        3, "(unitless)",
        r"Because \(4>1\), the positive branch applies: \(4-1=3\). Subtracting the full weight 2 would give 2, which is the formula for an objective that carries a leading one half. The input 4 is not the output. A result of 0 would require \(\lvert z\rvert\le 1\).",
    )
    b.mc(
        1,
        r"Why is the threshold \(\lambda/2\) rather than \(\lambda\), for \(\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1\) with orthonormal columns?",
        [
            r"The square on the residual contributes a factor 2 in the gradient, and that factor divides \(\lambda\).",
            r"The absolute penalty is squared, so the weight is halved.",
            r"Orthonormal columns force every singular value to equal \(\lambda\).",
            r"The subdifferential of \(\lvert t\rvert\) at a positive \(t\) is \(1/2\).",
        ],
        0,
        r"The gradient of \(\lVert Ax-b\rVert^2\) carries a 2. With \(A^T A=I\) the stationarity condition is \(2(x-z)+\lambda s=0\), so a positive coordinate solves as \(x=z-\lambda/2\). The absolute penalty is not squared. Orthonormal columns make \(A^T A=I\), not a statement about \(\lambda\). The subdifferential of \(\lvert t\rvert\) for \(t>0\) is 1, not \(1/2\).",
    )
    b.order(
        2,
        r"Put these steps in the order that derives the positive branch of the soft-threshold map. The objective in this coordinate is \((x-z)^2+\lambda\lvert x\rvert\), with \(\lambda>0\). Each step uses the equation the previous step wrote.",
        [
            "Write stationarity as 2(x-z)+lambda s = 0, with s in the subdifferential of |x|.",
            "Assume the solution is positive, which forces s=1.",
            "Solve the stationarity equation to get x = z - lambda/2.",
            "Keep that value only when it is positive, that is, only when z > lambda/2.",
        ],
        r"Stationarity has to be written before the sign assumption specializes \(s\). The assumption \(s=1\) has to be in the equation before it is solved for \(x\). The solved value has to exist before it is tested for consistency with the sign assumption. Swapping an adjacent pair uses a sign or a formula that has not been derived.",
    )
    b.num(
        2,
        r"The penalty weight is \(\lambda=2\), so the threshold is 1. The input coordinate is \(z=-4\). What is the soft-thresholded coordinate?",
        -3, "(unitless)",
        r"Because \(-4<-1\), the negative branch applies: \(-4+1=-3\). The positive branch \(z-\lambda/2\) would give \(-5\), which is more negative and does not match the subdifferential \(-1\). The input \(-4\) is not the output. A result of 0 would require the input to lie in \([-1,1]\).",
    )
    b.num(
        2,
        r"The columns are orthonormal, \(\lambda=2\), and \(z=A^T b=(5,\ 0.25)\). What is the first soft-thresholded coordinate?",
        4, "(unitless)",
        r"The threshold is \(\lambda/2=1\). The first input 5 is larger than 1, so it becomes \(5-1=4\). The second input 0.25 lies inside \([-1,1]\), so that coordinate becomes 0. Reporting 5 leaves the first coordinate unshrunk. Reporting 0.25 returns an input instead of the first output. Subtracting \(\lambda\) rather than \(\lambda/2\) would turn 5 into 3.",
    )
    b.sym(
        3,
        r"Let \(z>\lambda/2>0\). For the positive branch of \(\lVert x-z\rVert^2+\lambda\lvert x\rvert\) in one coordinate, write the minimizer in \(z\) and \(\lambda\). Use the name lam for \(\lambda\).",
        "z-lam/2",
        {"z": (2, 5), "lam": (0.2, 1)},
        r"Stationarity at a positive coordinate is \(2(x-z)+\mathrm{lam}=0\), because the subdifferential equals 1 and the square contributes the 2. Solve for \(x\). The declared ranges keep \(z>\mathrm{lam}/2\), so this positive branch is the minimizer."
        "\n"
        r"• \(z-\mathrm{lam}\) subtracts the full weight."
        "\n"
        r"• \(z+\mathrm{lam}/2\) moves away from zero."
        "\n"
        r"• \(\mathrm{lam}/2\) drops the data term \(z\).",
        ["z-(lam/2)", "(2*z-lam)/2"],
    )
    b.mc(
        3,
        r"The columns of \(A\) are not orthonormal. Which claim stays true?",
        [
            r"The minimizer is still the soft-threshold of \(A^T b\) at level \(\lambda/2\).",
            r"Stationarity is still \(0\in 2A^T(Ax-b)+\lambda\,\partial\lVert x\rVert_1\), but it does not reduce to that componentwise map.",
            r"The absolute value becomes differentiable at 0 when the columns fail to be orthonormal.",
            r"The objective drops the factor 2 in the residual gradient.",
        ],
        1,
        r"Differentiating the squared residual always produces the factor 2 and the map \(A^T(Ax-b)\). The subdifferential of the absolute penalty does not depend on \(A\). Orthonormality is what replaces \(A^T A x\) by \(x\) and lets each coordinate separate into a soft threshold of \(A^T b\). Without it, that closed form is gone, and the corner of the absolute value is still not differentiable.",
    )
    b.multi(
        3,
        r"The penalty weight is \(\lambda=4\), so the threshold is 2. Which inputs are sent to a nonzero soft-threshold value?",
        [
            r"\(z=5\)",
            r"\(z=-2.5\)",
            r"\(z=2\)",
            r"\(z=1\)",
        ],
        [0, 1],
        r"An input is unchanged in sign and reduced by 2 when its absolute value is strictly larger than 2. The input 5 becomes 3. The input \(-2.5\) becomes \(-0.5\). The input 2 meets the threshold and becomes 0. The input 1 lies inside the interval and becomes 0. Equality with the threshold is the boundary of the zero set, not a nonzero output.",
        SOFT, ASOFT,
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. One coordinate minimizes \((x-z)^2+\lambda\lvert x\rvert\) with \(z=5\) and \(\lambda=2\).",
        [
            r"Stationarity says \(2(x-z)+\lambda s=0\) with \(s\) in the subdifferential of \(\lvert x\rvert\).",
            r"If \(x>0\), then \(s=1\), so \(x=z-\lambda/2\).",
            r"With these numbers the positive formula gives \(x=5-2=3\).",
            r"The consistent positive value is \(x=4\), and it is positive, so the assumption \(x>0\) holds.",
        ],
        2,
        r"The stationarity equation and the positive branch \(x=z-\lambda/2\) are right. Here \(\lambda/2=1\), so \(x=5-1=4\), which is positive and consistent. Subtracting the full weight 2 is the formula for a different scaling of the square. The false step uses that other formula. The last step states the consistent value.",
        reasons=[
            "The threshold is lambda/2, so the positive value is 5-1, not 5-2.",
            "The subdifferential at a positive coordinate is 0.",
            "The factor 2 in the stationarity equation should be dropped.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Let \(A=\begin{bmatrix} 0 & 1 \\ 1 & 0 \end{bmatrix}\), so the columns are orthonormal, and let \(b=(6,\ 1)\) and \(\lambda=4\). What is the second coordinate of the soft-thresholded minimizer?",
        4, "(unitless)",
        r"Because \(A^T=A\), the vector \(z=A^T b\) equals \((1,\ 6)\). The threshold is \(\lambda/2=2\). The first input 1 lies inside \([-2,2]\), so that coordinate is 0. The second input 6 becomes \(6-2=4\). Reporting 6 leaves the second coordinate unshrunk. Reporting 1 returns an input. Subtracting \(\lambda=4\) from 6 would give 2, which is the wrong threshold.",
        preview=p,
    )
    b.mc(
        4,
        r"When the columns are not orthonormal, the same absolute penalty still separates across coordinates once the other coordinates are frozen. The exact minimization in one frozen-coordinate problem is a soft threshold of a partial residual. The skill that carries out those one-coordinate minimizations is",
        [
            r"a full gradient step on every coordinate at once",
            r"coordinate descent",
            r"an equality-constrained Newton step",
            r"a semidefinite embedding of the penalty",
        ],
        1,
        r"Freezing every coordinate but one leaves a scalar absolute-penalty problem, and its minimizer is a soft threshold. Doing that once per coordinate is a pass of coordinate descent. A gradient step moves every coordinate by a fixed multiple of a slope and does not solve the scalar problem exactly. A Newton step on equalities and a semidefinite embedding are different constructions.",
        preview=p,
    )
    b.save()


def bank_coord():
    b = Bank("coordinate-descent")
    p = PREV["coordinate-descent"]
    b.mc(
        1,
        r"A gradient step subtracts a fixed multiple of the full gradient, so every coordinate moves together. Coordinate descent instead",
        [
            r"minimizes in one coordinate while the others stay fixed",
            r"moves every coordinate by the same fixed length",
            r"replaces the objective by a random subset of its terms and keeps every coordinate free",
            r"requires the gradient to be zero before the first update",
        ],
        0,
        r"One coordinate is free and the rest are data for that scalar problem. A common fixed length is a gradient step, not an exact coordinate minimization. A random subset of terms, with every coordinate still free, is a stochastic or incremental gradient step. The gradient need not vanish before the first update; the update is how a descent method searches.",
    )
    b.num(
        1,
        r"Minimize \((x-6)^2+(y-1)^2+4(\lvert x\rvert+\lvert y\rvert)\) by one pass of exact coordinate minimization. The objective separates. What is the resulting \(x\)?",
        4, "(unitless)",
        r"The penalty weight is 4, so each coordinate is soft-thresholded at 2. The \(x\) center 6 is larger than 2, so \(x=6-2=4\). The \(y\) center 1 lies inside \([-2,2]\), so \(y\) becomes 0. Because the coordinates do not appear together, the order of the two updates does not change these values, and a second pass stays put. Reporting 6 leaves \(x\) unshrunk. Reporting 0 returns the \(y\) result.",
    )
    b.mc(
        1,
        r"The objective \((x-2)^2+(y+3)^2+5(\lvert x\rvert+\lvert y\rvert)\) separates across coordinates. One pass of exact coordinate minimization",
        [
            r"cannot move both coordinates, because a pass is allowed to touch only one of them",
            r"reaches the minimizer, and a second pass does not move either coordinate",
            r"reaches the minimizer only when the two updates are done in one prescribed order",
            r"stops at the first coordinate whose subdifferential contains 0, and leaves the other unchanged",
        ],
        1,
        r"Each scalar problem ignores the other coordinate. Updating each one exactly, once, sets both to their soft-threshold values. Either order produces the same pair, so a prescribed order is not required for correctness. A pass through a separable problem is not limited to a single coordinate. A second pass sees the same scalar problems and stays put.",
    )
    b.order(
        2,
        r"Put these steps in the order of one exact coordinate update for \((x+y-2)^2+(x-4)^2\), updating \(x\) while \(y\) is frozen. Each step uses the value the previous step fixed.",
        [
            "Freeze y at its current value and leave x free.",
            "Write the objective as a function of x alone, with that frozen y inside (x+y-2).",
            "Minimize that function of x.",
            "Replace x by the minimizer just obtained.",
        ],
        r"The frozen value has to be chosen before it can be substituted. The scalar function has to exist before it is minimized. The minimizer has to be known before \(x\) is replaced by it. Swapping an adjacent pair minimizes or substitutes a quantity that has not been fixed. The later update of \(y\) is a new pass step and is not one of these four.",
    )
    b.num(
        2,
        r"Start at \((0,0)\) and minimize \((x+y)^2+(x-4)^2\) by exact coordinate descent, updating \(x\) first and then \(y\). What is \(y\) after that one pass?",
        -2, "(unitless)",
        r"With \(y\) frozen at 0 the objective in \(x\) is \(x^2+(x-4)^2\), whose derivative \(4x-8\) vanishes at \(x=2\). With \(x\) then frozen at 2 the objective in \(y\) is \((2+y)^2\), whose minimizer is \(y=-2\). The partial derivative in \(x\) at \((2,-2)\) equals \(-4\), not 0, so the pass has not reached a stationary point. Reporting 2 returns the updated \(x\). Reporting 0 leaves the start.",
    )
    b.num(
        2,
        r"Minimize \((x-1)^2+(y-8)^2+6(\lvert x\rvert+\lvert y\rvert)\) by one exact coordinate pass. The objective separates. What is the resulting \(y\)?",
        5, "(unitless)",
        r"The threshold is \(6/2=3\). The center 8 is larger than 3, so \(y=8-3=5\). The center 1 lies inside \([-3,3]\), so \(x\) becomes 0. Reporting 8 leaves \(y\) unshrunk. Reporting 3 returns the threshold. Reporting 1 returns the \(x\) center.",
    )
    b.sym(
        3,
        r"One coordinate has the scalar objective \(a(t-c)^2+\lambda\lvert t\rvert\) with \(a>0\) and \(c>\lambda/(2a)\). Write the minimizer in \(a\), \(c\), and \(\lambda\). Use the name lam for \(\lambda\).",
        "c-lam/(2*a)",
        {"a": (0.5, 2), "c": (3, 6), "lam": (0.2, 1)},
        r"At a positive minimizer the stationarity condition is \(2a(t-c)+\mathrm{lam}=0\). Solve for \(t\). The declared ranges keep \(c>\mathrm{lam}/(2a)\), so the positive branch is consistent."
        "\n"
        r"• \(c-\mathrm{lam}/2\) drops the curvature \(a\)."
        "\n"
        r"• \(c-\mathrm{lam}/a\) drops the 2 from the square."
        "\n"
        r"• \(c+\mathrm{lam}/(2a)\) moves away from zero.",
        ["c-(lam/(2*a))", "(2*a*c-lam)/(2*a)"],
    )
    b.mc(
        3,
        r"Along one coordinate, a gradient step of fixed length \(t\) subtracts \(t\) times the partial derivative. An exact coordinate update instead",
        [
            r"uses that same fixed \(t\) on every coordinate and never solves a one-dimensional minimizer",
            r"chooses the coordinate value that minimizes the scalar function, which agrees with a gradient step only for a special length",
            r"requires the partial derivative to be undefined",
            r"moves a different coordinate from the one that was selected",
        ],
        1,
        r"Exact minimization picks the best value of the free coordinate. For a smooth square, that value equals a gradient step only when the length is the exact line-search length \(1\) over the second derivative. A fixed length chosen in advance is not that update. The partial derivative is used when it exists, and the selected coordinate is the one that moves.",
    )
    b.multi(
        3,
        r"Which objectives are minimized by one pass of exact coordinate updates, from any start?",
        [
            r"\((x-1)^2+(y+2)^2+3(\lvert x\rvert+\lvert y\rvert)\)",
            r"\((x+y)^2+(x-4)^2\)",
            r"\(\lvert x\rvert+(y-3)^2\)",
            r"\((x+y-2)^2+(y-1)^2\)",
        ],
        [0, 2],
        r"The first objective separates into a function of \(x\) plus a function of \(y\), and so does the third. One exact minimization of each coordinate finishes the problem. The second objective couples \(x\) and \(y\). From \((0,0)\), updating \(x\) then \(y\) lands at \((2,-2)\), where the partial derivative in \(x\) is \(-4\), not 0. The fourth couples the variables as well. From \((0,0)\), updating \(x\) then \(y\) lands at \((2,\ 0.5)\), where the partial derivative in \(x\) is 1, not 0.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The start is \((0,0)\), the objective is \((x+y)^2+(x-4)^2\), and the pass updates \(x\) and then \(y\).",
        [
            r"Freezing \(y\) at 0 and minimizing in \(x\) produces \(x=2\).",
            r"Freezing \(x\) at 2 and minimizing in \(y\) produces \(y=-2\).",
            r"At \((2,-2)\) the partial derivative with respect to \(x\) equals 0, so the point is stationary.",
            r"A later pass is still required when a partial derivative at the new point is nonzero.",
        ],
        2,
        r"The two coordinate minimizations are right: \(x=2\) and then \(y=-2\). The partial derivative in \(x\) is \(2(x+y)+2(x-4)\). At \((2,-2)\) it equals \(-4\), not 0. The point is therefore not stationary, and another pass can still move \(x\). The false step claims that partial derivative vanishes.",
        reasons=[
            "The partial derivative in x at (2, -2) equals -4, not 0.",
            "Freezing y at 0 does not produce x=2.",
            "The partial derivative in y is the one that equals -4 at this point.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Minimize \((x+2)^2+(y-7)^2+2(\lvert x\rvert+\lvert y\rvert)\) by one exact coordinate pass. The objective separates. What is the resulting \(x\)?",
        -1, "(unitless)",
        r"The threshold is \(2/2=1\). The center \(-2\) satisfies \(-2<-1\), so \(x=-2+1=-1\). The center 7 becomes \(7-1=6\). Reporting \(-2\) leaves \(x\) unshrunk. Reporting 6 returns \(y\). Reporting 1 returns the threshold.",
        preview=p,
    )
    b.mc(
        4,
        r"Each exact coordinate update of \((t-z)^2+\lambda\lvert t\rvert\) is the soft-threshold map at level \(\lambda/2\). That identity is the stationarity condition of the absolute penalty. Coordinate descent uses it when",
        [
            r"the columns are orthonormal only, and otherwise the scalar problem has no minimizer",
            r"other coordinates are frozen, including inside a residual that still depends on them",
            r"the absolute value is replaced by a square before the update",
            r"every coordinate is updated by the same gradient entry",
        ],
        1,
        r"Freezing the other coordinates leaves a scalar problem whose data term may still contain those frozen values. The minimizer of that scalar absolute-penalty problem is a soft threshold of the resulting center, whether or not a design matrix has orthonormal columns. Replacing the absolute value by a square is a different penalty. A shared gradient entry is a gradient step, not this exact update.",
        preview=p,
    )
    b.save()


def bank_newton():
    b = Bank("equality-constrained-newton")
    p = PREV["equality-constrained-newton"]
    b.mc(
        1,
        r"An unconstrained Newton step solves \(H d=-\nabla f\). On the equality \(Ax=b\), at a feasible point, the step and the multiplier instead come from",
        [
            r"the same unconstrained system, followed by discarding any component that violates \(Ad=0\)",
            r"one linear system whose unknowns are the step and the multiplier",
            r"a separate minimization in each coordinate of \(x\), ignoring \(A\)",
            r"the gradient alone, with the Hessian replaced by the identity",
        ],
        1,
        r"The feasible Newton step is the solution of the block system with \(H\) and \(A\) together. Discarding the infeasible part of an unconstrained step is a projection, and it is not this linear system. Coordinate minimization and a gradient step use different directions. The multiplier is an unknown of the same system as the step.",
        BLOCK, ABLOCK,
    )
    b.num(
        1,
        r"Minimize \(x^2+y^2\) subject to \(x+y=4\), starting from the feasible point \((0,4)\). The Hessian is \(2I\) and the gradient there is \((0,8)\). What is the new \(x\)-coordinate after one Newton step?",
        2, "(unitless)",
        r"The system is \(2\,dx+\nu=0\), \(2\,dy+\nu=-8\), and \(dx+dy=0\). Then \(\nu=-2\,dx\) and \(dy=-dx\), so \(-2\,dx-2\,dx=-8\) and \(dx=2\). The new \(x\)-coordinate is \(0+2=2\), and the new point is \((2,2)\). The unconstrained Newton step would change only \(y\) and land at the origin, which misses the line. The start \(x=0\) is not the new coordinate.",
    )
    b.mc(
        1,
        r"The current point already satisfies \(Ax=b\). In the Newton system for \(\min f\) subject to that equality, the block of the right-hand side that multiplies the constraint rows is",
        [
            r"\(b-Ax\), which is nonzero at a feasible point",
            r"the gradient of \(f\)",
            r"the zero vector, because the linearized equality is \(Ad=0\)",
            r"the Hessian applied to the gradient",
        ],
        2,
        r"Feasibility means \(Ax=b\). The linearization of the equality at a feasible point says the step stays in the nullspace of \(A\), so the constraint block on the right-hand side is 0. The residual \(b-Ax\) would appear if the current point were infeasible. The gradient occupies the first block of the right-hand side, with a minus sign. The Hessian sits on the left.",
    )
    b.order(
        2,
        r"Put these steps in the order of one equality-constrained Newton iteration at a feasible point. Each step uses the matrices the previous step evaluated.",
        [
            "Evaluate the gradient and the Hessian at the current feasible point.",
            "Assemble the block system with those derivatives, the constraint matrix, and a zero block on the right of the constraint rows.",
            "Solve that system for the step and the multiplier.",
            "Add the step to the current point.",
        ],
        r"The derivatives have to be evaluated before they can be placed in the system. The system has to be assembled before it is solved. The step has to be known before it is added to the point. Swapping an adjacent pair solves or assembles an object that has not been built.",
    )
    b.num(
        2,
        r"Minimize \(x^2+y^2\) subject to \(x+2y=6\), starting from the feasible point \((6,0)\). The Hessian is \(2I\) and the gradient there is \((12,\ 0)\). What is the new \(y\)-coordinate after one Newton step?",
        2.4, "(unitless)",
        r"The system is \(2\,dx+\nu=-12\), \(2\,dy+2\nu=0\), and \(dx+2\,dy=0\). The second equation says \(dy=-\nu\). Substitution gives \(dx=-24/5\) and \(dy=12/5=2.4\). The new \(y\)-coordinate is \(0+2.4=2.4\), and the new \(x\)-coordinate is \(6-4.8=1.2\), which satisfies \(1.2+4.8=6\). The start \(y=0\) is feasible but not optimal. The gradient entry 12 is not the new coordinate.",
    )
    b.num(
        2,
        r"In the Newton step for \(x^2+y^2\) subject to \(x+y=4\) at the feasible point \((0,4)\), what is the multiplier?",
        -4, "(unitless)",
        r"The same system that produced the step \(dx=2\), \(dy=-2\) gives \(\nu=-2\,dx=-4\). The stationarity row \(2\,dx+\nu=0\) is the check. The multiplier is not the constraint value 4, and it is not the step component 2. The sign is negative because the gradient of the objective at the new point points opposite the constraint normal used in this layout.",
    )
    b.sym(
        3,
        r"Minimize \(\tfrac12 p x^2+\tfrac12 q y^2\) subject to \(x+y=b\), with \(p>0\) and \(q>0\). Start at the feasible point \((b,\ 0)\) and take one Newton step. Write the new \(x\)-coordinate in \(p\), \(q\), and \(b\).",
        "b*q/(p+q)",
        {"p": (0.5, 3), "q": (0.5, 3), "b": (0.5, 2)},
        r"The Hessian is diagonal with entries \(p\) and \(q\). At \((b,0)\) the gradient is \((pb,\ 0)\). Solving the block system yields the step \(dx=-pb/(p+q)\), so the new \(x\)-coordinate is \(b q/(p+q)\). A quadratic with a positive definite Hessian finishes in one constrained Newton step, and this value is the minimizer."
        "\n"
        r"• \(b p/(p+q)\) is the new \(y\)-coordinate, not the new \(x\)."
        "\n"
        r"• \(b q/p\) drops \(q\) from the denominator."
        "\n"
        r"• \(b\) leaves the start unchanged.",
        ["(b*q)/(p+q)", "q*b/(p+q)"],
    )
    b.mc(
        3,
        r"The constraint matrix \(A\) has full row rank. The block Newton matrix is nonsingular when the Hessian is",
        [
            r"positive definite on the nullspace of \(A\), even if some infeasible direction has zero curvature",
            r"singular in a feasible direction as well as in an infeasible one",
            r"negative definite on the nullspace of \(A\)",
            r"replaced by the zero matrix",
        ],
        0,
        r"The step is required to lie in the nullspace of \(A\). Curvature is needed on that subspace, together with full row rank of \(A\), for the block matrix to be invertible. Zero curvature on a direction that violates the constraint does not by itself make the feasible system singular. Negative curvature on the nullspace, or a zero Hessian, fails the test.",
    )
    b.multi(
        3,
        r"The equality is \(x+y=4\). At which points is the constraint block of the Newton right-hand side equal to zero?",
        [
            r"\((1,\ 3)\)",
            r"\((4,\ 0)\)",
            r"\((0,\ 0)\)",
            r"\((2,\ 1)\)",
        ],
        [0, 1],
        r"That block is zero exactly at feasible points, where \(x+y=4\). Both \((1,3)\) and \((4,0)\) lie on the line. The origin sums to 0, and \((2,1)\) sums to 3. An infeasible point uses \(b-Ax\) on the right-hand side instead of zero.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The problem is \(\min x^2+y^2\) subject to \(x+y=4\), at the feasible point \((0,4)\).",
        [
            r"The gradient at \((0,4)\) is \((0,\ 8)\).",
            r"The unconstrained Newton equation \(2I\,d=-(0,\ 8)\) gives \(d=(0,\ -4)\).",
            r"The point \((0,\ 0)\) satisfies \(x+y=4\), so this unconstrained step is feasible.",
            r"A feasible step has to satisfy \(dx+dy=0\).",
        ],
        2,
        r"The gradient and the unconstrained solve are right, and a feasible step really does satisfy \(dx+dy=0\). The unconstrained step ends at \((0,0)\), and \(0+0\neq 4\). It is not feasible. The constrained system keeps the step on the line and lands at \((2,2)\). The false step claims the origin is on the line.",
        reasons=[
            "The sum of the coordinates at (0, 0) is 0, not 4.",
            "The gradient at (0, 4) is not (0, 8).",
            "A feasible step is allowed to leave the line x+y=4.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Minimize \(x^2+y^2\) subject to \(x+y=2\), starting from the feasible point \((0,2)\). The Hessian is \(2I\) and the gradient there is \((0,\ 4)\). What is the new \(x\)-coordinate after one Newton step?",
        1, "(unitless)",
        r"The system is \(2\,dx+\nu=0\), \(2\,dy+\nu=-4\), and \(dx+dy=0\). Then \(dx=1\) and \(dy=-1\). The new \(x\)-coordinate is 1, and the new point \((1,1)\) lies on the line. Its objective value is 2. The unconstrained step would land at the origin, which is not feasible. The start \(x=0\) is not the new coordinate.",
        preview=p,
    )
    b.mc(
        4,
        r"A log barrier adds a smooth term to the objective and keeps the equalities. The Newton step on that modified problem uses the same block system, with one change. Which change?",
        [
            r"The Hessian and the gradient are those of the barrier objective, not those of the original \(f\).",
            r"The constraint matrix \(A\) is deleted.",
            r"The multiplier is removed from the unknown list.",
            r"The right-hand side of a feasible equality becomes the barrier weight.",
        ],
        0,
        r"The equalities stay, so \(A\) and the multiplier stay in the system. At a feasible point the constraint block of the right-hand side is still zero. What changes is the objective whose gradient and Hessian fill the first block: it is the original objective plus the barrier term. The barrier weight is a coefficient in that term, not the equality residual.",
        preview=p,
    )
    b.save()


def bank_barrier():
    b = Bank("barrier-interior-point")
    p = PREV["barrier-interior-point"]
    b.mc(
        1,
        r"An inequality \(g(x)\le 0\) is folded into the objective by a log barrier of weight \(w>0\). The barrier term is defined",
        [
            r"on the whole space, including points where \(g(x)>0\)",
            r"only where \(g(x)<0\), and \(w\) is later sent toward 0",
            r"only at the boundary \(g(x)=0\), where the log is zero",
            r"only where \(g(x)<0\), and \(w\) is sent to infinity to recover the constrained minimizer",
        ],
        1,
        r"The logarithm needs a positive argument, so it is applied to \(-g(x)\) and only the strict interior is allowed. The weight starts positive and is driven toward 0, which lets the minimizer of the barrier problem approach the boundary when the constrained solution lies there. The log is undefined on the boundary, not zero. Sending \(w\) to infinity pushes the point farther inside, away from a boundary solution.",
        BAR, ABAR,
    )
    b.num(
        1,
        r"Minimize \(x\) subject to \(x\ge 2\), with barrier weight \(w=6\). The barrier objective is \(x-6\log(x-2)\) for \(x>2\). What is its minimizer?",
        8, "(unitless)",
        r"The derivative is \(1-6/(x-2)\). It vanishes when \(x-2=6\), so \(x=8\). The constrained infimum is the boundary 2, which is the limit as the weight tends to 0, not the minimizer at weight 6. The weight 6 is the distance from the bound, not the decision itself. A sign error in the derivative would push \(x\) the other way and would not produce a positive distance.",
    )
    b.mc(
        1,
        r"For \(\min x\) subject to \(x\ge a\), the barrier minimizer is \(a+w\). Increasing the weight \(w\)",
        [
            r"moves the minimizer toward the boundary \(x=a\)",
            r"leaves the minimizer at \(x=a\) for every finite \(w\)",
            r"moves the minimizer farther into the interior",
            r"makes the logarithm defined on the infeasible side \(x<a\)",
        ],
        2,
        r"The stationary point sits \(w\) units to the right of \(a\). A larger weight is a stronger push away from the boundary, so the minimizer moves deeper into \(x>a\). The boundary itself is the limit of small weights, and it is not attained at a positive weight. The logarithm stays undefined for \(x<a\).",
    )
    b.order(
        2,
        r"Put these steps in the order of one iteration at a fixed barrier weight, with equalities kept. Each step uses the function the previous step built.",
        [
            "Restrict attention to the strict interior, where every inequality is strictly negative, so each logarithm is defined.",
            "Form the barrier objective by subtracting the current weight times the sum of those logarithms from the original objective.",
            "Evaluate the gradient and the Hessian of that barrier objective.",
            "Solve the equality-constrained Newton system with that gradient and Hessian, and take the step.",
        ],
        r"The logarithms have to be defined before they can be subtracted from the objective. The barrier objective has to exist before its derivatives are evaluated. Those derivatives have to be in hand before the Newton system can use them. Swapping an adjacent pair differentiates or solves a function that has not been built. Decreasing the weight is a later iteration, not one of these four steps.",
    )
    b.num(
        2,
        r"Minimize \(y\) subject to \(0<y<8\), with barrier weight \(w=3\). The barrier objective is \(y-3\log y-3\log(8-y)\). What is its minimizer?",
        2, "(unitless)",
        r"The derivative is \(1-3/y+3/(8-y)\). At \(y=2\) it equals \(1-3/2+3/6=0\). The other critical point of the cleared equation lies outside \((0,8)\). The center of the interval is 4, where the two log forces cancel and the derivative of \(y\) is still 1, so 4 is not stationary. The constrained infimum is the endpoint 0, which is not in the domain of the log.",
    )
    b.num(
        2,
        r"Minimize \((x-10)^2\) subject to \(x\le 2\), with barrier weight \(w=18\). The barrier objective is \((x-10)^2-18\log(2-x)\) for \(x<2\). What is its minimizer?",
        1, "(unitless)",
        r"The derivative is \(2(x-10)+18/(2-x)\). At \(x=1\) it equals \(2(-9)+18/1=0\). The constrained minimizer of the original problem is the boundary \(x=2\), which the log cannot attain. The unconstrained minimizer \(x=10\) is far outside the feasible side. The weight 18 is the number that places the stationary point at \(x=1\), not the decision itself.",
    )
    b.sym(
        3,
        r"Minimize \(x\) subject to \(x\ge a\), with barrier weight \(w>0\). Write the minimizer of \(x-w\log(x-a)\) in \(a\) and \(w\).",
        "a+w",
        {"a": (-2, 2), "w": (0.2, 3)},
        r"The derivative is \(1-w/(x-a)\). Set it to zero and solve \(x-a=w\). The minimizer lies \(w\) units into the interior from the bound \(a\)."
        "\n"
        r"• \(a-w\) lies outside the domain when \(w>0\)."
        "\n"
        r"• \(w\) drops the bound."
        "\n"
        r"• \(a\) is the boundary, where the logarithm is undefined.",
        ["w+a", "a-(-w)"],
    )
    b.mc(
        3,
        r"The original objective is convex, and each inequality is convex. For \(w>0\), the barrier objective stays convex because",
        [
            r"\(-\log(-g)\) is convex on the strict interior whenever \(g\) is convex and negative there",
            r"the logarithm is concave, so subtracting it always destroys convexity",
            r"a barrier is a nonconvex penalty by definition",
            r"convexity holds only after \(w\) reaches 0",
        ],
        0,
        r"On the region where a convex \(g\) is negative, \(-\log(-g)\) is convex, and a positive multiple of it stays convex. Adding it to a convex objective preserves convexity. Concavity of \(\log\) on the positive reals is why the minus sign is present: the composition is what restores convexity. The barrier is not a nonconvex penalty, and the convexity claim is for each positive weight, not only for the limit.",
    )
    b.multi(
        3,
        r"For \(\min x\) subject to \(x\ge 2\), the barrier minimizer at weight \(w\) is \(2+w\). Which pairs \((w,\ x)\) match that minimizer?",
        [
            r"\(w=3\), \(x=5\)",
            r"\(w=1\), \(x=3\)",
            r"\(w=4\), \(x=4\)",
            r"\(w=2\), \(x=2\)",
        ],
        [0, 1],
        r"The identity is \(x=2+w\). Weight 3 gives 5, and weight 1 gives 3. Weight 4 would give 6, not 4. Weight 2 would give 4, and \(x=2\) is the boundary, where the logarithm is undefined. A pair that lands on the boundary is not a barrier minimizer at a positive weight.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The problem is \(\min x\) subject to \(x\ge 1\), at barrier weight 2.",
        [
            r"The inequality is \(g(x)=1-x\le 0\), and the strict interior is \(x>1\).",
            r"The barrier objective at weight 2 is \(x-2\log(x-1)\).",
            r"Its derivative is \(1+2/(x-1)\), and that derivative equals 0 at \(x=3\).",
            r"The stationary point of \(x-2\log(x-1)\) is \(x=3\).",
        ],
        2,
        r"The constraint rewrite and the barrier objective are right, and \(x=3\) really does solve \(1-2/(x-1)=0\). The displayed derivative has the wrong sign on the second term. At \(x=3\) the wrong derivative equals \(1+1=2\), not 0. The false step both flips the sign and claims a root it does not have.",
        reasons=[
            "The derivative of x - 2 log(x-1) is 1 - 2/(x-1), which is 0 at x=3. The plus sign is the error.",
            "The strict interior of x >= 1 is x < 1.",
            "The barrier objective at weight 2 adds the logarithm instead of subtracting it.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Minimize \(x\) subject to \(x\ge 5\), with barrier weight \(w=4\). What is the minimizer of \(x-4\log(x-5)\)?",
        9, "(unitless)",
        r"The derivative \(1-4/(x-5)\) vanishes when \(x-5=4\), so \(x=9\). The boundary 5 is the constrained infimum and is not attained at this positive weight. The weight 4 is the gap, not the decision. Adding the weight to the wrong side of the bound would give \(5-4=1\), which is not in the domain.",
        preview=p,
    )
    b.mc(
        4,
        r"This method sends the barrier weight to 0 and re-solves an equality-constrained Newton problem at the new weight. A heavier follow-up keeps multipliers explicit. What is driven to 0 here?",
        [
            r"the coefficient of the log terms",
            r"a product of a primal slack and a multiplier, set equal to a common positive value at every iteration",
            r"the equality residual, by deleting the equalities",
            r"the Hessian of the original objective",
        ],
        0,
        r"The weight in front of the sum of logarithms is the quantity this method decreases. A method that instead holds a product of a slack and a multiplier at a common positive value, and applies Newton to that perturbed system, is the heavier follow-up. This method keeps the equalities and does not delete them, and it uses the Hessian of the barrier objective rather than driving the original Hessian to zero.",
        preview=p,
    )
    b.save()


def expl_qp():
    sections = [
        {"heading": "The idea", "figure": BOWL, "figure_alt": ABOWL,
         "body_md": r"""An unconstrained quadratic is minimized by one linear system, the gradient set to zero. A quadratic program keeps that objective and cuts the space with affine constraints. Each equality is a flat, and each inequality is a half-space. The bowl does not change. Only the feasible set changes.

Write the objective as \(\tfrac12 x^T H x+q^T x+r\) with \(H\) symmetric. The gradient is \(Hx+q\). The program is convex when \(H\) is positive semidefinite, because that is the second-order test for the objective, and an affine set is convex. A positive definite \(H\) makes the objective strictly convex, so a minimizer is unique when one exists. A zero eigenvalue still leaves the program convex. The minimizer need not be unique in that case.

A curved constraint, such as a disk, is not allowed in this form. That constraint is the next program."""},
        {"heading": "Key equations",
         "body_md": r"""\[
\min_x\ \tfrac12 x^T H x+q^T x+r
\quad\text{subject to}\quad
Ax=b,\quad Gx\le h,
\]
with \(H\) symmetric. Convexity is \(H\succeq 0\). On a single equality \(x+y=s\), substitute \(y=s-x\) and minimize the resulting function of one variable. The substitution is legal because the equality is affine. The same idea, eliminating affine equalities, is what an unconstrained quadratic solver does after the constraints have been removed."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \((x-9)^2+(y-2)^2\) subject to \(x+y=5\). Substitute \(y=5-x\). The objective becomes \((x-9)^2+(3-x)^2\). The derivative is \(4x-24\), which vanishes at \(x=6\), so \(y=-1\). The point lies on the line because \(6+(-1)=5\). The value is
\[
(6-9)^2+(-1-2)^2=9+9=18.
\]
The optimal value equals 18. The unconstrained point \((9,2)\) scores 0 and misses the line, because \(9+2\neq 5\). The nearest point on the line is the one the derivative found, not the intercept."""},
        {"heading": "Pitfalls",
         "body_md": r"""A negative eigenvalue makes the objective nonconvex even when every constraint is affine. Invertibility of \(H\) does not replace the eigenvalue test.

The number you get by ignoring the constraints is the unconstrained minimizer. It is feasible only when it happens to satisfy them. Otherwise it is not a candidate.

A quadratic inequality is a different program. Do not call a disk constraint a quadratic program. A linear objective is the special case \(H=0\), which is positive semidefinite, so it is a convex quadratic program whose square term is absent. The zero matrix is allowed. It is not a negative curvature."""},
        {"heading": "Where this leads",
         "body_md": r"""The next constraint shape is a convex quadratic inequality, a disk or a slab cut by a squared affine function. After that, a Euclidean norm bounded by an affine function is the cone form of the same idea, and a positive-semidefinite matrix constraint is the widest of the four.

A maximum-margin linear separator is already a convex quadratic program: the objective is \(\tfrac12\lVert w\rVert^2\), and each labeled point contributes an affine inequality. The separator is an application of this form, not a new class."""},
    ]
    save_explainer("quadratic-program", "Convex quadratic programs", sections)


def expl_qcqp():
    sections = [
        {"heading": "The idea", "figure": DISK, "figure_alt": ADISK,
         "body_md": r"""A quadratic program stops at flat constraints. A quadratically constrained quadratic program allows the inequalities themselves to be quadratic, and it stays convex only when each of those inequalities cuts a convex set.

Write a constraint as \(g(x)\le 0\) with \(g\) quadratic. The set is convex when \(g\) is a convex function, which for a quadratic is the positive-semidefinite test on the Hessian of \(g\). A disk is the model case: a sum of squares has a positive-semidefinite Hessian, and the inside of the disk is convex. The outside of the same disk reverses the inequality and is not convex. A product constraint such as \(xy\le 1\) has an indefinite Hessian and fails the same test.

The objective is still a convex quadratic. Convexity of the whole program needs the objective and every inequality."""},
        {"heading": "Key equations",
         "body_md": r"""A constraint \(\tfrac12 x^T P x+q^T x+r\le 0\) is a convex constraint when \(P\succeq 0\). The disk
\[
(x-c_1)^2+(y-c_2)^2\le \rho^2
\]
is the case \(P=2I\). If the unconstrained minimizer of a convex objective lies outside the disk, the constrained minimizer is on the boundary, and the optimal value is the squared distance from that unconstrained point to the disk. The gap is the distance to the center, minus the radius, when the point is outside."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \((x-10)^2\) subject to \((x-1)^2\le 9\). The constraint is the interval centered at 1 with radius 3, so the feasible set is \([-2,\ 4]\). The parabola opens upward around 10, which lies to the right of the interval. The best feasible point is the right endpoint \(x=4\). The value is
\[
(4-10)^2=36.
\]
The optimal value equals 36. The center \(x=1\) is feasible and scores \((1-10)^2=81\), which is worse. The unconstrained point \(x=10\) scores 0 and is not feasible, because \((10-1)^2=81>9\)."""},
        {"heading": "Pitfalls",
         "body_md": r"""A negative eigenvalue in a constraint Hessian is not a harmless curve. It makes the feasible set fail the chord test. The outside of a disk is the usual picture: two feasible points can have a midpoint that falls in the hole.

Squaring a norm inequality is legal only when the side you square is nonnegative. A constraint written as a square from the start is already a quadratic inequality. Do not treat it as affine.

The zero eigenvalue is still positive semidefinite. A slab between two parallel lines, the square of one affine function, is a convex constraint even though its Hessian is singular."""},
        {"heading": "Where this leads",
         "body_md": r"""A Euclidean ball is both a convex quadratic constraint and a second-order-cone constraint, because a norm bounded by a constant is an affine upper bound. The cone form also allows the upper bound to tilt, which a single squared inequality hides less clearly. The cone program is the next description of this same disk, and of the tilted versions of it."""},
    ]
    save_explainer("quadratically-constrained-quadratic-program", "Quadratically constrained quadratic programs", sections)


def expl_socp():
    sections = [
        {"heading": "The idea", "figure": DISK, "figure_alt": ADISK,
         "body_md": r"""A second-order-cone constraint bounds a Euclidean norm of an affine map by another affine function:
\[
\lVert Fx+g\rVert\le c^T x+d.
\]
The left side is nonnegative, so a feasible point must make the right side nonnegative too. A constant right side is a ball. A tilting right side moves the center and the radius together. The reversed inequality, a norm bounded from below, is not convex and is not this constraint.

A convex quadratic inequality is one case, after an algebraic rewrite. The model rewrite turns \(x^2\le t\) into
\[
\lVert(2x,\ t-1)\rVert\le t+1.
\]
Expanding the square of both sides recovers \(x^2\le t\), and the right side of the cone form is affine in \((x,t)\). The disk you already know is the cone constraint with a constant bound."""},
        {"heading": "Key equations",
         "body_md": r"""The Euclidean norm is \(\lVert u\rVert=\sqrt{u^T u}\). The smallest \(t\) with \(\lVert u\rVert\le t\) is the norm itself. On a line \(x+y=s\) with \(s>0\), the smallest norm is the distance from the origin to the line, attained at the symmetric point and equal to \(s/\sqrt{2}\).

Squaring both sides of a cone inequality preserves it only where the affine upper bound is nonnegative. On that side the cone inequality and the quadratic inequality describe the same points. Where the upper bound is negative, the cone inequality is simply infeasible."""},
        {"heading": "Worked example",
         "body_md": r"""The smallest \(t\) such that \(\lVert(9,12)\rVert\le t\) is the norm of that vector:
\[
\sqrt{81+144}=\sqrt{225}=15.
\]
The smallest \(t\) equals 15. The same point as a squared inequality is \(81+144\le t^2\), which forces \(t\ge 15\) once \(t\ge 0\) is remembered. The 1-norm of \((9,12)\) is 21, a larger number and a different constraint. The cone constraint uses the Euclidean norm, the square root of the sum of squares, not the sum of absolute values."""},
        {"heading": "Pitfalls",
         "body_md": r"""Do not square first and ask questions later. If the affine side is negative, the squared form can look algebraically neat while the original inequality is impossible.

A squared norm on the left, \(\lVert u\rVert^2\le 4\), is a convex quadratic constraint and is equivalent to a cone constraint, but it is not yet written as one. The cone form has the norm itself, not its square, on the left.

The 1-norm and the Euclidean norm agree on the axes and disagree elsewhere. A diamond constraint is not this cone."""},
        {"heading": "Where this leads",
         "body_md": r"""The same quadratic inequality embeds in a positive-semidefinite matrix by a block complement. The matrix \(\begin{bmatrix} t & x \\ x & 1 \end{bmatrix}\) is positive semidefinite exactly when \(t\ge x^2\). That matrix constraint is a semidefinite program, the next and widest cone in this chain. The dual of a cone program, including this one, replaces the cone by its dual cone. The second-order cone is self-dual, so the dual constraint has the same shape."""},
    ]
    save_explainer("second-order-cone-program", "Second-order cone programs", sections)


def expl_sdp():
    sections = [
        {"heading": "The idea", "figure": HESS, "figure_alt": AHESS,
         "body_md": r"""A semidefinite program asks a symmetric matrix that depends affinely on the decision to be positive semidefinite. The feasible set is a spectrahedron. Linear inequalities, convex quadratic inequalities, and second-order-cone inequalities all embed in this form. The embedding of a quadratic inequality uses a block complement.

For a 2 by 2 symmetric matrix the test is concrete. Both diagonal entries must be nonnegative, and their product must be at least the square of the off-diagonal entry. Equivalently, both eigenvalues are nonnegative. A negative determinant means the eigenvalues have opposite signs, so the matrix is not positive semidefinite even if the diagonal looks fine.

The matrix in the constraint is symmetric. A quadratic form does not see the skew part of a nonsymmetric matrix, and the program is stated with symmetric coefficients."""},
        {"heading": "Key equations",
         "body_md": r"""\[
\begin{bmatrix} a & b \\ b & c \end{bmatrix}\succeq 0
\quad\Longleftrightarrow\quad
a\ge 0,\quad c\ge 0,\quad ac\ge b^2.
\]
The block complement of \(t\ge x^2\) is the matrix with \(t\) and \(1\) on the diagonal and \(x\) off the diagonal. Its complement relative to the entry 1 is \(t-x^2\). With that entry positive, the matrix is positive semidefinite exactly when the complement is nonnegative.

The zero matrix is positive semidefinite, because every quadratic form on it is 0. It is not positive definite."""},
        {"heading": "Worked example",
         "body_md": r"""Find the smallest \(t\) such that \(\begin{bmatrix} t & 5 \\ 5 & 4 \end{bmatrix}\) is positive semidefinite. The entry 4 is positive. The product test says \(4t\ge 25\), so \(t\ge 25/4\). That bound is already positive, so the diagonal requirement \(t\ge 0\) does not raise it. The smallest \(t\) is \(25/4\).

At that value the determinant gap is 0, so the matrix is singular and still positive semidefinite. One eigenvalue is 0 and the other is positive. A smaller trial value makes the determinant negative and produces a negative eigenvalue."""},
        {"heading": "Pitfalls",
         "body_md": r"""Nonnegative diagonal entries are not enough. The matrix with 1 on the diagonal and 2 off the diagonal has determinant \(-3\) and is not positive semidefinite.

Do not drop the complement. For \(\begin{bmatrix} t & 2 \\ 2 & 1 \end{bmatrix}\) the condition \(t\ge 0\) leaves \(t=0\) looking legal, but the complement is \(t-4\), so the real bound is \(t\ge 4\).

The off-diagonal sign does not matter, because the test squares that entry. A negative off-diagonal entry is the same constraint as its positive twin."""},
        {"heading": "Where this leads",
         "body_md": r"""A positive definite shape matrix appears again when an ellipsoid is fitted inside half-spaces. That problem maximizes a volume and keeps a norm constraint for each half-space. It is a different skill. The shared piece is the definite matrix, not a second copy of the general spectrahedron.

The dual of a semidefinite constraint uses the dual of the positive-semidefinite cone. That cone is self-dual, which is a fact of conic duality rather than a new matrix test."""},
    ]
    save_explainer("semidefinite-program", "Semidefinite programs", sections)


def expl_conic():
    sections = [
        {"heading": "The idea", "figure": ORTH, "figure_alt": AORTH,
         "body_md": r"""Weak duality says a dual feasible value is a lower bound on the primal optimal value. Strong duality says the bound is tight when a relative-interior constraint qualification holds. A cone program makes the dual explicit. The primal cone is replaced by its dual cone, the set of vectors that make a nonnegative inner product with every primal-cone vector.

The standard pair used here is
\[
\min\ c^T x\quad\text{subject to}\quad Ax=b,\ x\in K,
\]
and
\[
\max\ b^T y\quad\text{subject to}\quad A^T y+s=c,\ s\in K^\star.
\]
For a feasible pair the gap \(c^T x-b^T y\) equals \(s^T x\), which is nonnegative precisely because \(s\) is in the dual cone and \(x\) is in \(K\).

The nonnegative orthant, the second-order cone, and the positive-semidefinite cone are self-dual. Their dual constraints have the same shape as the primal cone constraints. The cone that contains only the origin is not self-dual: its dual is the whole space."""},
        {"heading": "Key equations",
         "body_md": r"""\[
K^\star=\{s:s^T z\ge 0\text{ for every }z\in K\}.
\]
On the nonnegative orthant, \(s\) is dual feasible exactly when \(s\ge 0\). If the primal is \(\min c^T x\) subject to \(1^T x=\beta\) and \(x\ge 0\), with \(\beta>0\) and every coefficient of \(c\) positive, the optimum puts \(\beta\) on a cheapest coordinate. The dual multiplier cannot exceed the cheapest coefficient, and the dual objective \(\beta z\) meets the primal value there."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \(5x+2y\) subject to \(x+2y=6\) and \(x\ge 0\), \(y\ge 0\). Substitute \(x=6-2y\). The cost becomes \(5(6-2y)+2y=30-8y\), which decreases as \(y\) grows. The largest feasible \(y\) is 3, where \(x=0\). The cost is \(30-24=6\).

The dual maximizes \(6z\) subject to \(z\le 5\) and \(2z\le 2\), so \(z\le 1\). The best multiplier is \(z=1\), and the dual objective is 6. The matching dual value is 6. The gap is zero. The more expensive variable \(x\) is the one the optimum sets to zero."""},
        {"heading": "Pitfalls",
         "body_md": r"""The dual-cone inequality is \(\ge 0\), not \(\le 0\). The opposite sign describes the dual of the negated cone.

A negative coordinate keeps a vector out of the dual orthant, no matter how large the other coordinates are. One negative inner product with a standard basis vector is enough.

A dual value larger than a primal value means the pair is not both feasible. Weak duality forbids that arrangement. Equal values are allowed: they are a zero gap, not a contradiction.

Self-duality is special. Do not assume an arbitrary cone equals its dual."""},
        {"heading": "Where this leads",
         "body_md": r"""An interior method keeps a dual-cone multiplier and drives the gap \(s^T x\) down. The heavier form of that method takes Newton steps on a perturbed multiplier system and stays near a path of strictly positive products. The cone certificate itself is the object built here. The algorithm that drives it is the later method, and it already has the log barrier as its lighter predecessor."""},
    ]
    save_explainer("conic-duality", "Conic duality", sections)


def expl_lasso():
    sections = [
        {"heading": "The idea", "figure": SOFT, "figure_alt": ASOFT,
         "body_md": r"""The lasso objective is a squared residual plus an absolute penalty, with no leading one half on the square. The absolute value is not differentiable at zero, so stationarity uses a subdifferential. The subdifferential of \(\lvert t\rvert\) is the sign of \(t\) when \(t\neq 0\), and the whole interval \([-1,\ 1]\) at \(t=0\).

The gradient of \(\lVert Ax-b\rVert^2\) is \(2A^T(Ax-b)\). Stationarity says
\[
0\in 2A^T(Ax-b)+\lambda\,\partial\lVert x\rVert_1.
\]
When the columns of \(A\) are orthonormal, \(A^T A=I\) and \(z=A^T b\) turn this into a separate scalar condition on each coordinate. The solution is the soft-threshold map at level \(\lambda/2\):
\[
x_i=\mathrm{sign}(z_i)\max(\lvert z_i\rvert-\lambda/2,\ 0).
\]
The factor 2 in the residual gradient is why the threshold is \(\lambda/2\) and not \(\lambda\). The flat middle of the map is the set of inputs that land on zero."""},
        {"heading": "Key equations",
         "body_md": r"""For one coordinate with center \(z\) and weight \(\lambda>0\), the scalar objective is \((x-z)^2+\lambda\lvert x\rvert\). If \(z>\lambda/2\), then \(x=z-\lambda/2\). If \(z<-\lambda/2\), then \(x=z+\lambda/2\). If \(\lvert z\rvert\le\lambda/2\), then \(x=0\), and the subdifferential element \(s=2z/\lambda\) lies in \([-1,\ 1]\).

Without orthonormal columns the inclusion \(0\in 2A^T(Ax-b)+\lambda\,\partial\lVert x\rVert_1\) is still the stationarity condition. It no longer separates into a soft threshold of \(A^T b\)."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(A=I\), \(b=(9,\ -1)\), and \(\lambda=4\). Then \(z=b\) and the threshold is 2. The first input 9 is larger than 2, so the first coordinate is \(9-2=7\). The second input \(-1\) lies in \([-2,\ 2]\), so the second coordinate is 0. The kept coordinate equals 7, and the other coordinate is wiped out.

Subtracting the full weight 4 from 9 would give 5, which is the threshold for an objective that puts a one half in front of the square. This objective has no such one half. The second coordinate is zero because its input lost to the threshold, not because the penalty deleted every small coordinate by a different rule."""},
        {"heading": "Pitfalls",
         "body_md": r"""Do not use the threshold \(\lambda\) unless the square carries a leading one half. The gradient of the square, not a convention about the penalty, produces the 2.

The endpoint \(\lvert z\rvert=\lambda/2\) maps to zero. It is not a tiny nonzero value. The subdifferential at zero is the whole interval, so every input inside the threshold is explained by some slope in \([-1,\ 1]\).

Orthonormality is a hypothesis, not a minor simplification you can ignore. A non-orthogonal column couples the coordinates through \(A^T A\). The stationarity inclusion survives. The closed form does not."""},
        {"heading": "Where this leads",
         "body_md": r"""When the columns are not orthonormal, freeze every coordinate but one. The scalar piece that remains is still an absolute penalty plus a square in that coordinate, and its minimizer is a soft threshold of a center that depends on the frozen coordinates. One sweep of those exact minimizations is coordinate descent. The map derived here is the update that sweep uses. The sweep itself is the next skill."""},
    ]
    save_explainer("lasso-stationarity", "Lasso stationarity and soft thresholding", sections)


def expl_coord():
    sections = [
        {"heading": "The idea", "figure": SOFT, "figure_alt": ASOFT,
         "body_md": r"""A gradient step looks at every partial derivative and moves every coordinate at once, by one fixed length. Coordinate descent picks one coordinate, freezes the others, and minimizes the resulting scalar function exactly. Then it moves to another coordinate.

If the objective is a sum of functions of single coordinates, those scalar problems do not interact. One pass, in any order, reaches the minimizer, and a second pass does not move. An absolute penalty that adds \(\lambda\lvert x_i\rvert\) separately for each \(i\) is this kind of objective. Each update is the soft-threshold map at level \(\lambda/2\) when the smooth piece is a plain square \((t-c)^2\).

A coupled objective is different. The frozen values appear inside the scalar function, so the minimizer of one coordinate depends on the others. One pass can leave a partial derivative nonzero. Further passes keep going. That is still coordinate descent. It is just not finished."""},
        {"heading": "Key equations",
         "body_md": r"""For \(a>0\) and \(c>\lambda/(2a)\), the scalar
\[
a(t-c)^2+\lambda\lvert t\rvert
\]
is minimized at \(t=c-\lambda/(2a)\). The curvature \(a\) sits in the denominator because the derivative of the square contributes \(2a\).

On a coupled smooth example, freeze, differentiate the scalar function, and solve. The partial derivative of the full objective, evaluated after the pass, is the test that the pass finished. A nonzero partial derivative means another update of that coordinate will move."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \((x-11)^2+(y+6)^2+4(\lvert x\rvert+\lvert y\rvert)\). The weight is 4, so the threshold is 2. The center 11 is larger than 2, so the \(x\) update returns \(11-2=9\). The center \(-6\) satisfies \(-6<-2\), so the \(y\) update returns \(-6+2=-4\). The first coordinate lands on 9.

The two squares do not share variables, and the penalty is a sum of absolute coordinates. Either order produces \((9,\ -4)\), and a second pass sees the same scalar problems. A gradient step of some fixed length from the same start would move both coordinates by multiples of the partial derivatives, and those landings are not automatically the soft-threshold values."""},
        {"heading": "Pitfalls",
         "body_md": r"""Do not list "update \(x\)" and "update \(y\)" as a unique order when the objective separates. Both orders are correct. The ordered object is the work inside one coordinate: freeze, form the scalar function, minimize it, then write the new coordinate.

A coupled square can look finished because one partial derivative vanished. Check the other ones. In \((x+y)^2+(x-4)^2\), one pass from the origin that updates \(x\) and then \(y\) lands at \((2,-2)\), where the partial derivative in \(x\) is \(-4\).

Exact minimization is not a fixed-length gradient step. They agree only when the length equals one over the scalar second derivative."""},
        {"heading": "Where this leads",
         "body_md": r"""The scalar absolute-penalty minimizer is the soft-threshold map from the stationarity condition. Coordinate descent is that map applied with the other coordinates held fixed, including when a residual still depends on them. The stationarity skill derives the map for orthonormal columns. This skill applies the scalar map one coordinate at a time when the problem does not separate in closed form.

A pass over blocks of data, with every coordinate still free, is a different method. It compares a block gradient with the full gradient. It does not freeze coordinates of the decision."""},
    ]
    save_explainer("coordinate-descent", "Coordinate descent", sections)


def expl_newton():
    sections = [
        {"heading": "The idea", "figure": BLOCK, "figure_alt": ABLOCK,
         "body_md": r"""An unconstrained Newton step minimizes the quadratic model of \(f\). It solves \(H d=-\nabla f\), where \(H\) is the Hessian. On an equality \(Ax=b\) the step also has to keep the point feasible. At a point that already lies on the equality, the linearization says \(Ad=0\).

The multiplier \(\nu\) of the equality and the step \(d\) are unknowns of one linear system:
\[
\begin{bmatrix} H & A^T \\ A & 0 \end{bmatrix}
\begin{bmatrix} d \\ \nu \end{bmatrix}
=
\begin{bmatrix} -\nabla f \\ 0 \end{bmatrix}.
\]
The top block is stationarity of the quadratic model plus the constraint force \(A^T\nu\). The bottom block is \(Ad=0\). Adding \(d\) to a feasible point stays on \(Ax=b\).

If \(H\) is positive definite on the nullspace of \(A\), and \(A\) has full row rank, this matrix is nonsingular. Curvature in a direction that violates the equality is not required. A quadratic with that curvature finishes in one step."""},
        {"heading": "Key equations",
         "body_md": r"""For \(f=x^2+y^2\) the Hessian is \(2I\) and the gradient is \((2x,\ 2y)\). On \(x+y=s\) at a feasible start, the three equations are
\[
2\,dx+\nu=-\nabla_x f,\qquad 2\,dy+\nu=-\nabla_y f,\qquad dx+dy=0.
\]
The third equation forces the step along the line. The unconstrained system drops the third equation and the multiplier, and its landing point is feasible only by accident.

For \(\tfrac12 p x^2+\tfrac12 q y^2\) on \(x+y=b\), started at \((b,0)\), one step lands at \(x=bq/(p+q)\) and \(y=bp/(p+q)\). The coordinate with the smaller curvature takes more of the right-hand side."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \(x^2+y^2\) subject to \(x+y=10\), starting at \((0,10)\). The gradient is \((0,\ 20)\). The system is \(2\,dx+\nu=0\), \(2\,dy+\nu=-20\), and \(dx+dy=0\). Then \(\nu=-2\,dx\) and \(dy=-dx\), so \(-4\,dx=-20\) and \(dx=5\). The new point is \((5,\ 5)\), and the multiplier equals -10.

The point \((5,5)\) lies on the line and is the minimizer, because the objective is quadratic and the Hessian is positive definite. The unconstrained Newton step from the same start subtracts \((0,\ 10)\) and lands at the origin, where the coordinates sum to 0, not 10."""},
        {"heading": "Pitfalls",
         "body_md": r"""Do not take the unconstrained step and then hope. At a feasible point the unconstrained step is feasible only when it already satisfies \(Ad=0\).

The right-hand side of the constraint block is zero only at a feasible point. If \(Ax\neq b\), that block is the residual \(b-Ax\), and the formula with a zero there does not apply.

A zero eigenvalue of \(H\) in an infeasible direction can be harmless. A zero eigenvalue in a feasible direction makes the block matrix singular, and the step is no longer defined as a unique solution. Negative curvature on the feasible subspace is a different failure: the quadratic model is then unbounded below on the equality."""},
        {"heading": "Where this leads",
         "body_md": r"""A log barrier changes the objective and keeps the equalities. The same block system is solved with the gradient and the Hessian of the barrier objective. The constraint matrix stays. The multiplier stays. Only the first block's derivatives change.

That is the Newton iteration inside a barrier method. The barrier weight, and the decision to send it toward zero, belong to the barrier skill. This skill is the linear system those iterations call."""},
    ]
    save_explainer("equality-constrained-newton", "Newton's method with equality constraints", sections)


def expl_barrier():
    sections = [
        {"heading": "The idea", "figure": BAR, "figure_alt": ABAR,
         "body_md": r"""An inequality \(g(x)\le 0\) is not an equality, so it does not go into the Newton system as a hard row. A barrier method folds it into the objective. On the strict interior, where \(g(x)<0\), the barrier objective is
\[
f(x)-w\sum_i\log(-g_i(x)),\qquad w>0.
\]
The logarithm tends to \(-\infty\) as \(g_i\) approaches the boundary from inside, so the minus sign builds a wall. The minimizer at a positive weight stays strictly feasible. Sending \(w\) toward 0 lowers the wall and lets the minimizer approach a constrained solution that lies on the boundary.

Equalities are kept. Each iteration forms this objective at the current weight, evaluates its gradient and Hessian, and takes one equality-constrained Newton step. Then the weight is decreased and the objective is rebuilt. The Newton system is the one you already have. The derivatives in its first block are the barrier derivatives."""},
        {"heading": "Key equations",
         "body_md": r"""For \(\min x\) subject to \(x\ge a\), the barrier objective is \(x-w\log(x-a)\) on \(x>a\). The derivative \(1-w/(x-a)\) vanishes at
\[
x=a+w.
\]
A larger weight sits farther inside. The boundary \(x=a\) is the limit of small weights, and the logarithm is undefined there.

If the original objective is convex and each \(g_i\) is convex, then \(-\log(-g_i)\) is convex on the strict interior. A positive weight keeps the barrier objective convex, so the Newton step is aimed at a convex problem."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \((x-16)^2\) subject to \(x\le 11\), at barrier weight 72. The domain is \(x<11\), and the barrier objective is \((x-16)^2-72\log(11-x)\). The derivative is \(2(x-16)+72/(11-x)\). At \(x=7\),
\[
2(7-16)+72/(11-7)=-18+18=0.
\]
The barrier minimizer sits at 7. The weight is 72. The constrained minimizer of the original quadratic is the boundary \(x=11\), which the logarithm cannot attain. The unconstrained minimizer \(x=16\) lies outside the feasible side. The interior point 7 is where the pull toward 16 balances the wall at 11, at this particular weight."""},
        {"heading": "Pitfalls",
         "body_md": r"""The sign in front of the log is a minus. Plus a log would reward the boundary and the derivative would not have an interior zero for a linear objective that wants to decrease.

Do not evaluate the log on the boundary or outside. The expression is undefined there. A claimed stationary point with \(g(x)=0\) is not a barrier minimizer at a positive weight.

Decreasing \(w\) moves toward the constrained solution. Increasing \(w\) moves deeper inside. The two directions are easy to swap because both change a positive coefficient.

The barrier objective's Hessian, not the original Hessian, is what the Newton system sees. Using \(\nabla f\) and \(H_f\) alone ignores the wall."""},
        {"heading": "Where this leads",
         "body_md": r"""A heavier interior method keeps a multiplier for each inequality and replaces complementary slackness by a perturbed product, a slack times a multiplier set near a small positive value. Newton is then applied to that perturbed system, and the products are driven down together. That method is the follow-up. This one never forms those products. It decreases the coefficient of the logarithms and calls the equality-constrained Newton step on the barrier objective."""},
    ]
    save_explainer("barrier-interior-point", "Barrier interior-point method", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    publish_graph()
    bank_qp()
    bank_qcqp()
    bank_socp()
    bank_sdp()
    bank_conic()
    bank_lasso()
    bank_coord()
    bank_newton()
    bank_barrier()
    expl_qp()
    expl_qcqp()
    expl_socp()
    expl_sdp()
    expl_conic()
    expl_lasso()
    expl_coord()
    expl_newton()
    expl_barrier()
    banned = (
        "boyd", "nocedal", "vandenberghe", "textbook", "university", "professor",
        "lecture", "syllabus", "berkeley", "stanford", "slater", "fenchel",
        "tibshirani", "homework", "chapter",
    )
    private = {
        "quadratic-program": "equals 18",
        "quadratically-constrained-quadratic-program": "equals 36",
        "second-order-cone-program": "equals 15",
        "semidefinite-program": "25/4",
        "conic-duality": "matching dual value is 6",
        "lasso-stationarity": "equals 7",
        "coordinate-descent": "lands on 9",
        "equality-constrained-newton": "multiplier equals -10",
        "barrier-interior-point": "weight is 72",
    }
    bad = False
    for sid in IDS:
        exp = json.load(open(os.path.join(ROOT, "skilltree", "explainers", sid + ".json"), encoding="utf-8"))
        bank = json.load(open(os.path.join(ROOT, "skilltree", "bank", sid + ".json"), encoding="utf-8"))
        n = doc_words(exp["sections"])
        blob = json.dumps(exp) + json.dumps(bank)
        hits = [w for w in banned if w in blob.lower()]
        deep = sum(1 for q in bank["questions"] if q.get("type") in DEEP_TYPES)
        print(f"{sid}: words {n}, deep {deep}/12")
        if not 250 <= n <= 500:
            print("  word count outside 250-500")
            bad = True
        if hits:
            print("  banned", hits)
            bad = True
        if deep < deep_quota(12):
            print("  deep-type quota miss")
            bad = True
        if private[sid] not in json.dumps(exp):
            print("  worked-example marker missing", private[sid])
            bad = True
        if private[sid] in json.dumps(bank):
            print("  worked example reused in the bank", private[sid])
            bad = True
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
