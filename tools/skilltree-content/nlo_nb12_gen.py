#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB12 banks and explainers.

Skills: optimality over a convex set, projection, gradient projection,
scaled projection, affine scaling, primal-dual interior point, Frank-Wolfe,
and the power method.

Closed-form answers live here. skilltree/verify_nlo_nb12.py recomputes the
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

DECAY = plot(lambda t: 1.7 * (0.62 ** t), 0.0, 5.5, "k", "e", "a falling curve")
A_DECAY = "A curve that falls toward the horizontal axis."
SLOW = plot(lambda t: 1.55 / (1.0 + 0.18 * t * t), 0.0, 5.5, "k", "gap", "a curve that flattens")
A_SLOW = "A curve that drops at first and then flattens."
HALF = halfspace_fig("a shaded half-plane")
A_HALF = "A straight boundary with one side shaded."
DISK = disk_fig("a disk at the origin")
A_DISK = "A filled disk centered at the origin."
SIMP = simplex_fig("a segment between the axes")
A_SIMP = "A segment joining the two axis intercepts."
SEG = segment_fig("a segment")
A_SEG = "A solid segment joins two marked points on a dashed line."
BOX = orthant_fig("a shaded quadrant")
A_BOX = "The first quadrant is shaded."
ELL = ellipse_axes("a long ellipse")
A_ELL = "An axis-aligned ellipse, longer along the first axis."
LEV = level_curves_fig("nested contours")
A_LEV = "Three nested ellipses around the origin."
BALLS = norm_balls("three unit balls")
A_BALLS = "A diamond, a disk, and a square, nested at the origin."
ARR = plane_vectors([(1.15, 0.35, "v")], "one arrow from the origin")
A_ARR = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.05, 0.2, "u"), (0.35, 1.05, "v")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."
MAT = matrix_fig([["p", "0"], ["0", "q"]], "a diagonal array")
A_MAT = "A two-by-two array with labels on the diagonal."
COL = matrix_fig([["a"], ["b"]], "a column of two labels")
A_COL = "A column of two labels."

P_PROJ = ["projection-onto-convex-set"]
P_FW = ["frank-wolfe-conditional-gradient"]
P_GP = ["gradient-projection-method"]
P_SC = ["scaled-gradient-projection"]
P_AF = ["affine-scaling-method"]
P_PD = ["primal-dual-interior-point"]
P_POW = ["power-method-eigenvector"]
P_SVD = ["singular-value-decomposition"]


def bank_opt():
    b = Bank("optimality-over-convex-set")
    b.mc(
        1,
        r"For a differentiable objective and a convex feasible set, the variational inequality at a candidate \(x^\star\) says that",
        [
            r"\(\nabla f(x^\star)^T (x - x^\star) \ge 0\) for every feasible \(x\)",
            r"\(\nabla f(x^\star)^T (x - x^\star) \le 0\) for every feasible \(x\)",
            r"\(\nabla f(x^\star) = 0\), even when \(x^\star\) lies on the boundary",
            r"\(\nabla f(x^\star)^T (x - x^\star) \ge 0\) for every \(x\) outside the set",
        ],
        0,
        r"Every feasible step has to look uphill, or flat, to first order, so the gradient pairs nonnegatively with \(x - x^\star\). The opposite sign is the obtuse-angle test for a projection, not this inequality. A boundary minimizer can have a nonzero gradient that points out of the set. Points outside the set are not feasible steps, so the inequality is not a claim about them.",
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        1,
        r"Minimize \(\tfrac12 (t - 5)^2\) on the interval \([-1,\ 2]\). At the candidate \(t = 2\), what is the gradient's product with the feasible step from \(2\) to \(0\)?",
        6,
        "1",
        r"The gradient of \(\tfrac12 (t - 5)^2\) is \(t - 5\). At \(t = 2\) it equals \(-3\). The step from \(2\) to \(0\) is \(-2\). The product is \((-3)(-2) = 6\). Reporting \(-3\) is the gradient. Reporting \(-6\) flips the sign of the inequality. Reporting \(2\) is the candidate, not the product. The positive product is what the variational inequality asks for along this particular step.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"If the variational inequality holds at a point in the interior of the convex set, then",
        [
            r"the gradient there is zero, because every direction and its opposite are feasible",
            r"the gradient may point in any direction, since the set has room around the point",
            r"the point is infeasible",
            r"the objective has to be nonconvex",
        ],
        0,
        r"An interior point has a small ball of feasible steps. A nonnegative pairing in a direction and in its opposite forces each pairing to be zero, so the gradient is zero. That is the unconstrained stationarity test. The point is feasible by the interior assumption. Convexity of the objective is not required for this conclusion.",
        fig=DISK,
        alt=A_DISK,
    )
    b.order(
        2,
        r"Put these steps in the order that checks the variational inequality at one candidate on a convex polygon. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient at the candidate.",
            r"Using that gradient, form its dot product with the vector from the candidate to each vertex.",
            r"Compare each of those dot products with zero.",
            r"Accept the candidate only when every one of those dot products is nonnegative.",
        ],
        r"The dot products use the gradient, so the gradient comes first. The comparisons use those products, so they come after the products are formed. The accept-or-reject decision uses the comparisons. A linear function on a polygon attains its minimum at a vertex, so the products at the vertices decide the inequality for every feasible point. Checking a single edge before the gradient exists is not a reordering of these steps.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Minimize the objective \(x\) on the unit square \([0,\ 1] \times [0,\ 1]\). Which points satisfy the variational inequality?",
        [
            r"\((0,\ 0)\)",
            r"\((0,\ 1)\)",
            r"\((0,\ 1/2)\)",
            r"\((1,\ 1/5)\)",
            r"\((2/5,\ 2/5)\)",
        ],
        [0, 1, 2],
        r"The gradient is \((1,\ 0)\). At a feasible point \(p\), the product with \(x - p\) is the first coordinate of \(x - p\)."
        "\n"
        r"• At \((0,\ 0)\), \((0,\ 1)\), and \((0,\ 1/2)\) that difference of first coordinates is nonnegative everywhere in the square, because every feasible first coordinate is at least \(0\)."
        "\n"
        r"• At \((1,\ 1/5)\) the step back to \((0,\ 1/5)\) has product \(-1\)."
        "\n"
        r"• At \((2/5,\ 2/5)\) the step back to \((0,\ 2/5)\) has product \(-2/5\)."
        "\n"
        r"The whole left edge is optimal for this linear objective. The other two points are not.",
        fig=BOX,
        alt=A_BOX,
    )
    b.sym(
        2,
        r"On the interval from \(0\) to \(a\), with the objective \(\tfrac12 (t - b)^2\), the candidate is the right endpoint \(t = a\). The product of the gradient at \(a\) with the step from \(a\) to \(0\) equals",
        "a*(b-a)",
        {"a": (1, 3), "b": (4, 6)},
        r"The gradient of \(\tfrac12 (t - b)^2\) is \(t - b\). At \(t = a\) it equals \(a - b\). The step from \(a\) to \(0\) is \(-a\). The product is \((a - b)(-a) = a(b - a)\). Both names appear. Using \(a - b\) alone drops the step. Using \(b - a\) alone drops the factor from the step length. Adding \(a + b\) mixes the endpoint with the unconstrained minimizer.",
        alternates=["a*b-a*a", "a*b-a^2"],
        fig=SEG,
        alt=A_SEG,
    )
    b.find_error(
        3,
        r"A note checks \(t = 4\) for \(\min (t - 1)^2\) on \([0,\ 4]\). Exactly one step is a false claim.",
        [
            r"The feasible set is \([0,\ 4]\) and the candidate is the right endpoint \(4\).",
            r"The gradient of \((t - 1)^2\) at \(4\) is \(2(4 - 1) = 6\).",
            r"For every feasible \(t\), the step \(t - 4\) is less than or equal to \(0\).",
            r"The product \(6(t - 4)\) is positive for every \(t < 4\), so the variational inequality holds.",
        ],
        3,
        r"The set and the candidate are as stated. The derivative of \((t - 1)^2\) is \(2(t - 1)\), so the value at \(4\) is \(6\). Feasible steps from the right endpoint point left, so \(t - 4 \le 0\). The product of a positive gradient with a negative step is negative, not positive. The inequality fails, and the minimizer of this convex objective is the left side of the unconstrained minimizer, at \(t = 1\).",
        [
            r"The product \(6(t - 4)\) is negative for \(t < 4\), so the variational inequality does not hold.",
            r"The gradient of \((t - 1)^2\) at \(4\) is not \(6\).",
            r"The endpoint \(4\) is outside the interval.",
        ],
        0,
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        3,
        r"On the interval \([-2,\ 2]\), the objective \(-t^2\) has gradient zero at \(t = 0\). How much larger is the objective at \(0\) than at \(2\)?",
        4,
        "1",
        r"The values are \(f(0) = 0\) and \(f(2) = -4\), so the difference is \(4\). The variational inequality holds at \(0\) because the gradient is zero, but \(2\) is feasible and better. A zero gradient is not a certificate of a minimum when the objective is not convex. Reporting \(-4\) is the endpoint value, not the difference. Reporting \(0\) would be the value at the stationary point.",
        fig=LEV,
        alt=A_LEV,
    )
    b.mc(
        3,
        r"When the objective is convex and the feasible set is convex, the variational inequality is",
        [
            r"sufficient for a global minimizer, because the graph stays above its tangent",
            r"only necessary, and a convex objective can satisfy it at a maximizer",
            r"sufficient for a local minimizer that need not be global",
            r"the same statement as a positive definite Hessian",
        ],
        0,
        r"Convexity puts \(f(x)\) above \(f(x^\star) + \nabla f(x^\star)^T (x - x^\star)\). If every feasible pairing is nonnegative, no feasible point can undercut \(f(x^\star)\). For a convex objective the certificate is global, not merely local. A convex function does not satisfy the inequality at a maximizer unless the function is flat. The Hessian test is a different, second-order statement.",
        fig=LEV,
        alt=A_LEV,
    )
    b.mc(
        4,
        r"A local minimizer of a differentiable objective over a convex set",
        [
            r"satisfies the variational inequality, whether or not the objective is convex",
            r"satisfies the variational inequality only when the objective is convex",
            r"must be a vertex of the set",
            r"must have a zero gradient even when it lies on the boundary",
        ],
        0,
        r"Necessity uses the set's convexity and differentiability: a descent step would contradict a local minimum. Convexity of the objective is what upgrades the inequality from necessary to sufficient. A smooth objective on a disk can be minimized at an interior point or at a non-vertex boundary point. A boundary minimizer can have a nonzero gradient pointing out of the set.",
        fig=DISK,
        alt=A_DISK,
        preview=P_PROJ,
    )
    b.num(
        4,
        r"Minimize \((x - 1)^2 + (y - 4)^2\) on the box \([0,\ 3] \times [0,\ 2]\). At the candidate \((1,\ 2)\), what is the gradient's product with the step from \((1,\ 2)\) to \((0,\ 0)\)?",
        8,
        "1",
        r"The gradient is \((2(x - 1),\ 2(y - 4))\). At \((1,\ 2)\) it equals \((0,\ -4)\). The step to \((0,\ 0)\) is \((-1,\ -2)\). The product is \((-4)(-2) = 8\). The first coordinate does not contribute. Reporting \(-8\) flips the sign. Reporting \(4\) is the absolute value of one gradient entry. The candidate is the point of the box closest to the unconstrained minimizer \((1,\ 4)\), which sits above the box.",
        fig=BOX,
        alt=A_BOX,
        preview=P_PROJ,
    )
    b.mc(
        4,
        r"For a differentiable objective that is not convex, a feasible point that satisfies the variational inequality",
        [
            r"need not be a local minimizer",
            r"is always a global minimizer",
            r"cannot have a zero gradient",
            r"must be a vertex",
        ],
        0,
        r"The inequality is necessary for a local minimum, but it is not sufficient without convexity. The objective \(-t^2\) on an interval has a zero gradient at an interior maximum, so the inequality holds and the point is not a minimizer. Global optimality needs the tangent lower bound that convexity supplies. A zero gradient is allowed, and the point need not be a vertex.",
        fig=HALF,
        alt=A_HALF,
        preview=P_FW,
    )
    b.save()


def bank_proj():
    b = Bank("projection-onto-convex-set")
    b.mc(
        1,
        r"The Euclidean projection \(p\) of a point \(z\) onto a nonempty closed convex set \(\mathcal{C}\) is characterized by",
        [
            r"\((z - p)^T (x - p) \le 0\) for every \(x\) in \(\mathcal{C}\)",
            r"\((z - p)^T (x - p) \ge 0\) for every \(x\) in \(\mathcal{C}\)",
            r"\((z - p)^T (x - p) = 0\) for every \(x\) in \(\mathcal{C}\)",
            r"\(p = z\) whenever \(z\) lies outside \(\mathcal{C}\)",
        ],
        0,
        r"The vector from \(p\) to \(z\) makes an obtuse or right angle with every vector from \(p\) to another feasible point. The opposite sign is the variational inequality for a general objective, before it is specialized to the squared distance. Equality for every feasible \(x\) would force the set to be a singleton. A point outside the set is not its own projection.",
        fig=DISK,
        alt=A_DISK,
    )
    b.num(
        1,
        r"Project \((-1,\ 5)\) onto the box \([0,\ 2] \times [0,\ 2]\). What is the squared Euclidean distance from the point to its projection?",
        10,
        "1",
        r"Each coordinate is clipped to \([0,\ 2]\), so the projection is \((0,\ 2)\). The squared distance is \((-1 - 0)^2 + (5 - 2)^2 = 1 + 9 = 10\). Reporting \(1\) or \(9\) keeps only one squared gap. Reporting \(4\) clips the second coordinate to the wrong end of the interval. The projection is the nearest point of the box, and the squared length is what the Euclidean projection minimizes.",
        fig=BOX,
        alt=A_BOX,
    )
    b.mc(
        1,
        r"If \(z\) already lies in a nonempty closed convex set, the Euclidean projection of \(z\) is",
        [
            r"\(z\) itself",
            r"the origin, after a translation that moves the set",
            r"a different boundary point",
            r"undefined, because the distance is already zero",
        ],
        0,
        r"The distance from \(z\) to \(z\) is zero, and no other point is closer. The obtuse-angle inequality holds because \(z - p = 0\). The origin is the projection of \(z\) only when \(z\) itself is the origin, or when the set forces that result. A zero distance is a valid projection, not a failure of the definition.",
        fig=DISK,
        alt=A_DISK,
    )
    b.order(
        2,
        r"Put these steps in the order that projects a point onto a closed ball, when the point lies outside the ball. Each step uses the result of the step before it.",
        [
            r"Subtract the center from the outside point to get the radial vector.",
            r"Compute the Euclidean length of that radial vector.",
            r"Divide the radius by that length.",
            r"Scale the radial vector by that quotient and add the center.",
        ],
        r"The radial vector is the input to the length, so it comes first. The quotient uses the length, so the length comes before the division. The scaled vector uses the quotient. Adding the center last places the result on the ray from the center through the outside point, at distance equal to the radius. Scaling by the length instead of by the radius over the length lands past the sphere.",
        fig=DISK,
        alt=A_DISK,
    )
    b.multi(
        2,
        r"Let \(p = (1,\ 0)\) be the projection of \(z = (2,\ 0)\) onto the closed unit disk. Which of these points \(x\) satisfy \((z - p)^T (x - p) \le 0\)?",
        [
            r"\((0,\ 0)\)",
            r"\((0,\ 1)\)",
            r"\((1,\ 0)\)",
            r"\((3/5,\ 4/5)\)",
            r"\((2,\ 0)\)",
        ],
        [0, 1, 2, 3],
        r"Here \(z - p = (1,\ 0)\), so the product is the first coordinate of \(x - p\)."
        "\n"
        r"• \((0,\ 0)\) gives \(-1\)."
        "\n"
        r"• \((0,\ 1)\) gives \(-1\)."
        "\n"
        r"• \((1,\ 0)\) gives \(0\)."
        "\n"
        r"• \((3/5,\ 4/5)\) gives \(3/5 - 1 = -2/5\)."
        "\n"
        r"• \((2,\ 0)\) gives \(1\), which is positive."
        "\n"
        r"The inequality is required at every point of the disk, including the projection itself. The outside point \(z\) is not one of those points.",
        fig=DISK,
        alt=A_DISK,
    )
    b.sym(
        2,
        r"The point \((a,\ b)\) lies outside the disk of radius \(r\) centered at the origin. The first coordinate of its Euclidean projection onto that disk equals",
        "r*a/sqrt(a*a+b*b)",
        {"a": (2, 4), "b": (2, 4), "r": (0.2, 0.8)},
        r"The projection is the radius times the unit vector from the origin toward \((a,\ b)\). The first coordinate is \(r a / \sqrt{a^2 + b^2}\). Every name appears. Dropping \(r\) returns a unit-vector coordinate. Dividing by the squared length, instead of the length, is a different scaling. Using \(a + b\) in the numerator mixes the two coordinates.",
        alternates=["r*a/sqrt(a^2+b^2)"],
        fig=DISK,
        alt=A_DISK,
    )
    b.find_error(
        3,
        r"A note projects \((4,\ 1)\) onto the box \([0,\ 2] \times [0,\ 2]\). Exactly one step is a false claim.",
        [
            r"The feasible set is the box \([0,\ 2] \times [0,\ 2]\).",
            r"The first coordinate of \((4,\ 1)\) lies above \(2\), and the second lies in \([0,\ 2]\).",
            r"Clipping replaces an out-of-range coordinate by the nearest endpoint and keeps an in-range coordinate.",
            r"The projection is \((4,\ 1)\).",
        ],
        3,
        r"The set is the stated box. The first coordinate \(4\) is above \(2\), and \(1\) lies between \(0\) and \(2\). Clipping sends the first coordinate to \(2\) and leaves the second at \(1\), so the projection is \((2,\ 1)\). The point \((4,\ 1)\) is outside the box, so it cannot be the projection. Leaving an infeasible point unchanged is the rule only when the point is already feasible.",
        [
            r"The projection is \((2,\ 1)\). The point \((4,\ 1)\) lies outside the box.",
            r"The second coordinate \(1\) does not lie in \([0,\ 2]\).",
            r"Clipping is not the Euclidean projection onto an axis-aligned box.",
        ],
        0,
        fig=BOX,
        alt=A_BOX,
    )
    b.num(
        3,
        r"Project \((6,\ 8)\) onto the disk of radius \(5\) centered at the origin. What is the first coordinate of the projection?",
        3,
        "1",
        r"The point has length \(\sqrt{36 + 64} = 10\), which is outside the disk. The projection is \((5/10)(6,\ 8) = (3,\ 4)\). The first coordinate is \(3\). Reporting \(4\) is the second coordinate. Reporting \(6\) leaves the point unscaled. Reporting \(10\) is the length of the original point. The result lies on the ray from the origin and on the circle.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        3,
        r"The nearest-point projection of every \(z\) is a single point of the set when the set is",
        [
            r"nonempty, closed, and convex",
            r"any nonempty set, including a pair of isolated points",
            r"an open disk that does not contain \(z\)",
            r"a closed disk with two declared projections of the same outside point",
        ],
        0,
        r"Closedness gives existence and convexity gives uniqueness for the Euclidean nearest point. Two isolated points are not convex, and the midpoint of the segment between them is equally close to both. An open disk need not contain its nearest boundary point, so the projection in the set can fail to exist. A closed disk has one projection of each outside point.",
        fig=DISK,
        alt=A_DISK,
    )
    b.mc(
        4,
        r"In the norm \(\lVert v\rVert_H = \sqrt{v^T H v}\) with \(H\) symmetric positive definite, the projection \(p\) of \(z\) satisfies",
        [
            r"\((z - p)^T H (x - p) \le 0\) for every feasible \(x\)",
            r"the Euclidean obtuse-angle test, for every such \(H\)",
            r"\(H p = z\)",
            r"the same point as the Euclidean projection, for every convex set",
        ],
        0,
        r"The angle test is taken in the inner product \(u^T H v\). The Euclidean test is the special case \(H = I\). A positive definite \(H\) that stretches one axis moves the nearest point on a slanted set. Nothing in the inequality says \(H p = z\) unless the set is a singleton at that location.",
        fig=ELL,
        alt=A_ELL,
        preview=P_GP,
    )
    b.num(
        4,
        r"Using \(H = \mathrm{diag}(4,\ 1)\), project \(z = (3,\ 4)\) onto the half-space \(x_1 + x_2 \le 2\). What is the first coordinate of the projection?",
        2,
        "1",
        r"\(H^{-1} = \mathrm{diag}(1/4,\ 1)\) and \(a = (1,\ 1)\). The excess \(a^T z - 2\) equals \(5\). The denominator \(a^T H^{-1} a\) equals \(5/4\), so the multiplier is \(4\). The correction is \(4 H^{-1} a = (1,\ 4)\). The projection is \((3,\ 4) - (1,\ 4) = (2,\ 0)\). The first coordinate is \(2\). The Euclidean projection onto the same half-space is a different point, because it uses \(H = I\). Reporting \(3\) leaves the infeasible point unchanged.",
        fig=HALF,
        alt=A_HALF,
        preview=P_GP,
    )
    b.mc(
        4,
        r"The Euclidean projection of a point onto an axis-aligned box",
        [
            r"clips each coordinate to its own interval",
            r"adds one common constant to every coordinate",
            r"needs a matrix factorization even when the point is already inside",
            r"can land outside the box",
        ],
        0,
        r"The squared Euclidean distance separates across coordinates, and so does the box. Each coordinate is the nearest point of its interval, which is clipping. A common additive shift would preserve differences between coordinates and can leave the box. An interior point is already feasible, so its projection is itself and no factorization is required. The clipped point lies in the box by construction.",
        fig=BOX,
        alt=A_BOX,
        preview=P_GP,
    )
    b.save()


def bank_gp():
    b = Bank("gradient-projection-method")
    b.mc(
        1,
        r"A feasible point \(x\) is stationary for a differentiable objective over a closed convex set when, for every step size \(t > 0\),",
        [
            r"\(x\) equals the projection of \(x - t \nabla f(x)\)",
            r"\(x\) equals \(x - t \nabla f(x)\), even if that point lies outside the set",
            r"the projection of \(x\) is the origin",
            r"\(\nabla f(x)\) is a positive multiple of \(x\)",
        ],
        0,
        r"Stationarity is the fixed point of a projected gradient step. If the trial point \(x - t \nabla f(x)\) leaves the set, the projection has to bring it back to the same \(x\). Accepting an infeasible trial point is an ordinary gradient step, not the constrained one. The origin and a sign condition on \(x\) are not the fixed-point test.",
        fig=BOX,
        alt=A_BOX,
    )
    b.num(
        1,
        r"Minimize \((x - 4)^2\) on \([0,\ 2]\), starting at \(0\), with step size \(1\). The gradient at \(0\) is \(-8\). What is the next iterate?",
        2,
        "1",
        r"The trial point is \(0 - 1 \cdot (-8) = 8\). Clipping \(8\) to \([0,\ 2]\) gives \(2\). Reporting \(8\) stops before the projection. Reporting \(-8\) is the gradient. Reporting \(0\) leaves the start unchanged. The right endpoint is the minimizer on this interval, and one projected step from the left endpoint reaches it.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"For a convex objective with an \(L\)-Lipschitz gradient and a constant step \(0 < t \le 1/L\), the projected-gradient bound of order \(1/k\) controls",
        [
            r"the function gap \(f(x_k) - f^\star\)",
            r"the distance \(\lVert x_k - x^\star\rVert\)",
            r"the smallest eigenvalue of the Hessian",
            r"the number of vertices of the feasible set",
        ],
        0,
        r"The standard estimate is \(f(x_k) - f^\star \le \lVert x_0 - x^\star\rVert^2 / (2 t k)\). The quantity on the left is the function gap. The distance to a minimizer need not fall like \(1/k\) unless a stronger hypothesis, such as strong convexity, is added. The bound does not count vertices and does not claim a Hessian eigenvalue.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.order(
        2,
        r"Put these steps in the order of one projected-gradient iteration. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient at the current feasible point.",
            r"Subtract the step size times that gradient from the current point, producing a trial point.",
            r"Project that trial point onto the feasible set.",
            r"Replace the current point by that projection.",
        ],
        r"The trial point uses the gradient, so the gradient is first. The projection uses the trial point. The replacement uses the projection. Projecting the current point before the gradient step does nothing when the current point is already feasible, and it is not a swap of these four steps.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"On the unit square, take one projected step of length \(1\) for the objective \(x\), whose gradient is \((1,\ 0)\). Which points are fixed by that step?",
        [
            r"\((0,\ 0)\)",
            r"\((0,\ 1)\)",
            r"\((0,\ 1/4)\)",
            r"\((1,\ 0)\)",
            r"\((1/2,\ 1/2)\)",
        ],
        [0, 1, 2],
        r"The trial point is \((x - 1,\ y)\), then each coordinate is clipped to \([0,\ 1]\)."
        "\n"
        r"• From \((0,\ 0)\), \((0,\ 1)\), and \((0,\ 1/4)\) the trial has first coordinate \(-1\), and clipping returns the same point."
        "\n"
        r"• From \((1,\ 0)\) the trial is \((0,\ 0)\), whose projection is \((0,\ 0)\)."
        "\n"
        r"• From \((1/2,\ 1/2)\) the trial is \((-1/2,\ 1/2)\), whose projection is \((0,\ 1/2)\)."
        "\n"
        r"The fixed points are the minimizers, the left edge of the square.",
        fig=BOX,
        alt=A_BOX,
    )
    b.sym(
        2,
        r"For the scalar objective \(\tfrac12 a t^2 + b t\), a step of length \(s\) forms a trial point before projection. That trial point equals",
        "t-s*(a*t+b)",
        {"a": (1, 3), "b": (1, 3), "s": (0.2, 0.8), "t": (1, 3)},
        r"The gradient is \(a t + b\). The trial point subtracts \(s\) times that gradient from \(t\). Every name appears. Adding the gradient steps uphill. Dropping \(s\) uses a unit step that the formula does not assume. Using \(a t - b\) flips the linear term.",
        alternates=["t-s*a*t-s*b", "(1-s*a)*t-s*b"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note takes one projected step for \((x - 3)^2 + (y - 1)^2\) on the unit square, starting at \((0,\ 0)\) with step size \(1/2\). Exactly one step is a false claim.",
        [
            r"The gradient at \((0,\ 0)\) is \((-6,\ -2)\).",
            r"The trial point is \((0,\ 0) - \tfrac12 (-6,\ -2) = (3,\ 1)\).",
            r"The feasible set is the unit square \([0,\ 1] \times [0,\ 1]\).",
            r"The next iterate is the trial point \((3,\ 1)\).",
        ],
        3,
        r"The partial derivatives are \(2(x - 3)\) and \(2(y - 1)\), so the gradient at the origin is \((-6,\ -2)\). Subtracting half of that gradient lands at \((3,\ 1)\). The unit square is the stated set. The trial point is outside it. Clipping gives \((1,\ 1)\), which is the next iterate. Accepting \((3,\ 1)\) skips the projection.",
        [
            r"The trial point \((3,\ 1)\) is outside the square. The next iterate is its projection \((1,\ 1)\).",
            r"The gradient at the origin is not \((-6,\ -2)\).",
            r"The arithmetic from \((0,\ 0)\) and step \(1/2\) does not produce \((3,\ 1)\).",
        ],
        0,
        fig=BOX,
        alt=A_BOX,
    )
    b.num(
        3,
        r"The projected-gradient theorem says that the function gap is at most \(\lVert x_0 - x^\star\rVert^2 / (2 t k)\) when its hypotheses hold. With \(\lVert x_0 - x^\star\rVert^2 = 16\), \(t = 1/2\), and \(k = 4\), what is that upper bound?",
        4,
        "1",
        r"The denominator is \(2 \cdot (1/2) \cdot 4 = 4\). The bound is \(16/4 = 4\). This number upper-bounds \(f(x_k) - f^\star\). It is not a measurement of \(\lVert x_k - x^\star\rVert\). Reporting \(16\) stops before the division. Reporting \(8\) uses \(t k\) without the factor \(2\). Reporting \(2\) uses \(t = 1/2\) as if it were the whole denominator.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        3,
        r"When the feasible set is all of \(\mathbb{R}^n\), one projected-gradient step",
        [
            r"reduces to the ordinary gradient step \(x - t \nabla f(x)\)",
            r"still clips every coordinate to \([-1,\ 1]\)",
            r"calls a linear minimization oracle over a simplex",
            r"sets the gradient to zero for every objective in one iteration",
        ],
        0,
        r"The projection onto the whole space is the identity, so the trial point is accepted. Clipping to a box is a different feasible set. A linear minimization oracle is the conditional-gradient step, not this one. One gradient step zeroes the gradient only for special objectives, such as a quadratic whose Newton step happens to match.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        4,
        r"Summing the decrease of projected steps with \(0 < t \le 1/L\), for a convex objective with an \(L\)-Lipschitz gradient, produces",
        [
            r"a function-gap bound of order \(1/k\)",
            r"a quadratic bound on \(\lVert x_k - x^\star\rVert\) for every convex objective",
            r"finite termination on every quadratic",
            r"an increase of the objective at every accepted step",
        ],
        0,
        r"Each accepted step decreases the objective by a multiple of the squared movement, as the sufficient-decrease lemma does in the unconstrained case. Adding those decreases and using convexity bounds the gap by a constant over \(k\). A quadratic distance bound needs strong convexity. Finite termination is a conjugate-direction fact, not a projected-gradient fact. The step is built to decrease the objective when \(t \le 1/L\).",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_SC,
    )
    b.num(
        4,
        r"Minimize \(3x^2\) on \([-2,\ 2]\), starting at \(1\), with step size \(1\). The derivative at \(1\) is \(6\). What is the next iterate?",
        -2,
        "1",
        r"The trial point is \(1 - 1 \cdot 6 = -5\). Clipping \(-5\) to \([-2,\ 2]\) gives \(-2\). Reporting \(-5\) is the trial point, which is outside the interval. Reporting \(1\) skips the step. Reporting \(6\) is the derivative. The second derivative is \(6\), so this step size is longer than \(1/L\). The iteration is still well defined, and the projection is what brings the trial point back to the endpoint.",
        fig=SEG,
        alt=A_SEG,
        preview=P_SC,
    )
    b.mc(
        4,
        r"If the trial point \(x - t \nabla f(x)\) already lies in the feasible set, the projected update",
        [
            r"equals that trial point",
            r"jumps to a farthest vertex instead",
            r"rejects the step and stays at \(x\)",
            r"replaces the gradient by its negative before moving",
        ],
        0,
        r"The projection of a feasible point is itself, so the update is the ordinary gradient step. A vertex step is the conditional-gradient method. The step is rejected only by a line search that tests decrease, not by feasibility of the trial point. The gradient is already subtracted; flipping it again would reverse the direction.",
        fig=DISK,
        alt=A_DISK,
        preview=P_SC,
    )
    b.save()


def bank_scaled():
    b = Bank("scaled-gradient-projection")
    b.mc(
        1,
        r"A scaled projected step with symmetric positive definite \(H\) builds the trial point",
        [
            r"\(x - t H^{-1} \nabla f(x)\), and then projects it onto the set in the \(H\)-norm",
            r"\(x - t H \nabla f(x)\), and then projects it in the Euclidean norm",
            r"\(x + t H^{-1} \nabla f(x)\)",
            r"the minimizer of the linear model \(\nabla f(x)^T s\) over the set",
        ],
        0,
        r"The quadratic model \(\nabla f(x)^T (y - x) + \tfrac{1}{2t} (y - x)^T H (y - x)\) is the squared \(H\)-distance from \(y\) to \(x - t H^{-1} \nabla f(x)\), up to a constant. Multiplying by \(H\) instead of \(H^{-1}\) is a different direction. Adding the scaled gradient steps uphill. Minimizing the linear model is a conditional-gradient step, which does not use \(H\).",
        fig=ELL,
        alt=A_ELL,
    )
    b.num(
        1,
        r"Take \(H = \mathrm{diag}(2,\ 4)\), gradient \((8,\ 4)\), step size \(1\), and the current point \((3,\ 4)\). The set is the box \([0,\ 5] \times [0,\ 5]\). What is the second coordinate of the scaled projected step?",
        3,
        "1",
        r"\(H^{-1} \nabla f = (8/2,\ 4/4) = (4,\ 1)\). The trial point is \((3,\ 4) - (4,\ 1) = (-1,\ 3)\). Clipping to the box gives \((0,\ 3)\). The second coordinate is \(3\). Reporting \(-1\) is the unclipped first coordinate. Reporting \(4\) is the old second coordinate. Reporting \(1\) is the scaled gradient's second entry. Because \(H\) is diagonal and the set is a box, each coordinate clips separately.",
        fig=BOX,
        alt=A_BOX,
    )
    b.mc(
        1,
        r"Projected Newton is the scaled projected step in which",
        [
            r"\(H\) is the Hessian, or a positive definite modification of it, and the step size is \(1\)",
            r"\(H\) is the identity and the step size is \(1/L\)",
            r"the Hessian is ignored and the step is a pure gradient step",
            r"the projection is skipped whenever the Hessian is positive definite",
        ],
        0,
        r"The Newton trial point is \(x - \nabla^2 f(x)^{-1} \nabla f(x)\). Projecting that point in the Hessian norm is one scaled projected step with \(t = 1\). The identity scaling is ordinary projected gradient. A positive definite Hessian makes the model convex, but the trial point can still leave the set, so the projection remains. Skipping it would accept an infeasible Newton point.",
        fig=MAT,
        alt=A_MAT,
    )
    b.order(
        2,
        r"Put these steps in the order of one scaled projected iteration on a box, with a diagonal positive definite scaling. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient at the current point.",
            r"Divide each component of that gradient by the matching diagonal entry of the scaling, then multiply by the step size.",
            r"Subtract the resulting vector from the current point to get the trial point.",
            r"Clip each coordinate of that trial point to the box.",
        ],
        r"The divisions use the gradient components, so the gradient comes first. The trial point subtracts the scaled vector, so that vector has to exist. Clipping uses the trial point. For a diagonal scaling and a box the \(H\)-norm projection is this coordinatewise clip. Clipping the gradient before the division is a different algorithm.",
        fig=MAT,
        alt=A_MAT,
    )
    b.multi(
        2,
        r"Which of these matrices can be the scaling \(H\) in a scaled projected step?",
        [
            r"\(\mathrm{diag}(2,\ 3)\)",
            r"\(\mathrm{diag}(2,\ 0)\)",
            r"\(\begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}\)",
            r"\(\mathrm{diag}(2,\ -1)\)",
            r"\(4 I\)",
        ],
        [0, 2, 4],
        r"The scaling has to be symmetric positive definite, so the model has a unique minimizer and \(H^{-1}\) exists."
        "\n"
        r"• \(\mathrm{diag}(2,\ 3)\) has positive diagonal entries."
        "\n"
        r"• \(\mathrm{diag}(2,\ 0)\) is singular."
        "\n"
        r"• The matrix with \(2\) on the diagonal and \(1\) off it has eigenvalues \(3\) and \(1\)."
        "\n"
        r"• \(\mathrm{diag}(2,\ -1)\) has a negative eigenvalue."
        "\n"
        r"• \(4 I\) is a positive multiple of the identity."
        "\n"
        r"A zero or negative eigenvalue is not a legal scaling.",
        fig=MAT,
        alt=A_MAT,
    )
    b.sym(
        2,
        r"With a diagonal scaling, one coordinate has value \(x\), gradient component \(g\), scaling entry \(h\), and step size \(s\). The trial value of that coordinate, before clipping, equals",
        "x-s*g/h",
        {"x": (1, 3), "g": (1, 3), "h": (1, 4), "s": (0.2, 0.8)},
        r"The corresponding entry of \(H^{-1} \nabla f\) is \(g/h\). The trial coordinate subtracts \(s\) times that entry from \(x\). Every name appears. Multiplying by \(h\) instead of dividing is the action of \(H\), not of \(H^{-1}\). Dropping \(s\) forces a unit step. Adding \(s g / h\) steps uphill.",
        alternates=["x-(s*g)/h", "(h*x-s*g)/h"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note runs projected Newton for \(\tfrac32 x^2\) on the interval \([1,\ 4]\), starting at \(2\). Exactly one step is a false claim.",
        [
            r"At \(x = 2\) the derivative is \(6\) and the second derivative is \(3\).",
            r"The Newton point is \(2 - 6/3 = 0\).",
            r"The Newton point \(0\) lies outside \([1,\ 4]\).",
            r"The projected Newton point is \(0\).",
        ],
        3,
        r"The derivative of \(\tfrac32 x^2\) is \(3x\), so the value at \(2\) is \(6\), and the second derivative is \(3\). The Newton point is \(2 - 6/3 = 0\). That point is outside the interval. In one dimension every positive scaling clips to the same place, so the projection of \(0\) onto \([1,\ 4]\) is \(1\). Reporting \(0\) leaves an infeasible point as the answer.",
        [
            r"The projection of \(0\) onto \([1,\ 4]\) is \(1\), not \(0\).",
            r"The derivative of \(\tfrac32 x^2\) at \(2\) is not \(6\).",
            r"The Newton point \(2 - 6/3\) is not \(0\).",
        ],
        0,
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        3,
        r"Using \(H = \mathrm{diag}(4,\ 1)\), project \(z = (8,\ 4)\) onto the half-space \(x_1 + x_2 \le 2\). What is the first coordinate of the projection?",
        6,
        "1",
        r"The excess \(a^T z - 2\) equals \(10\), and \(a^T H^{-1} a = 5/4\), so the multiplier is \(8\). Then \(8 H^{-1} a = (2,\ 8)\), and \((8,\ 4) - (2,\ 8) = (6,\ -4)\). The first coordinate is \(6\). The correction follows \(H^{-1} a\), not the Euclidean normal \((1,\ 1)\). Reporting \(8\) keeps the infeasible first coordinate. Reporting \(2\) is the size of the first correction, not the landing coordinate.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        3,
        r"When \(H\) is diagonal and the set is an axis-aligned box, the scaled projected step",
        [
            r"clips each trial coordinate \(x_i - t g_i / H_{ii}\) to its interval",
            r"mixes the coordinates through an off-diagonal product before clipping",
            r"is undefined, because a diagonal matrix has no inverse",
            r"returns the Newton point even when that point lies outside the box",
        ],
        0,
        r"A diagonal \(H\)-norm separates, and a box separates, so the nearest point clips each coordinate of the trial vector. Off-diagonal entries would couple the coordinates. A positive diagonal is invertible. If a trial coordinate falls outside its interval, clipping moves it to the endpoint. The unclipped Newton point is kept only when it already lies in the box.",
        fig=BOX,
        alt=A_BOX,
    )
    b.mc(
        4,
        r"If the Newton point lies inside the feasible set, projected Newton",
        [
            r"returns that Newton point, the same step unconstrained Newton would take",
            r"returns the projection of the gradient onto the boundary",
            r"takes a zero step",
            r"replaces the Hessian by the diagonal of its inverse",
        ],
        0,
        r"The projection of a feasible point is itself, in every norm. An interior Newton point is therefore accepted unchanged. Projecting the gradient is a different operation. The step is zero only when the gradient is already zero. The full Hessian, not only its diagonal, defines this trial point.",
        fig=LEV,
        alt=A_LEV,
        preview=P_AF,
    )
    b.num(
        4,
        r"For \(2x^2 - 2x\) on the interval \([0,\ 1]\), start at \(2\). The derivative there is \(6\) and the second derivative is \(4\). What is the projected Newton iterate?",
        0.5,
        "1",
        r"The Newton point is \(2 - 6/4 = 1/2\). The value \(1/2\) lies in \([0,\ 1]\), so the projection leaves it unchanged. Reporting \(2\) skips the step. Reporting \(6/4\) is the length of the Newton step, not the landing point. Reporting \(0\) clips to the wrong end of the interval. Because the Newton point is feasible, projected Newton and unconstrained Newton agree on this step.",
        fig=SEG,
        alt=A_SEG,
        preview=P_AF,
    )
    b.mc(
        4,
        r"With a fixed positive definite scaling, the usual sublinear guarantee of projected gradient still bounds",
        [
            r"the function gap, after the metric is used to define the step",
            r"only the angle between successive gradients",
            r"the duality gap of a linear program",
            r"\(\lVert H\rVert\), independently of the iterates",
        ],
        0,
        r"A fixed positive definite scaling changes the inner product in which the projection is taken. The same decrease argument still bounds \(f(x_k) - f^\star\) by a constant over \(k\), for a smooth convex objective and a short enough step. It does not by itself bound a duality gap, and \(\lVert H\rVert\) is data, not a rate. Projected Newton lets \(H\) change with the iterate, which is a different guarantee.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_AF,
    )
    b.save()


def bank_affine():
    b = Bank("affine-scaling-method")
    b.mc(
        1,
        r"At a strictly positive \(x\) with \(A x = b\), the primal affine-scaling direction for \(\min c^T x\) is",
        [
            r"\(d = -X^2 (c - A^T y)\), with \(X = \mathrm{diag}(x)\) and \(y\) chosen so that \(A d = 0\)",
            r"a simplex edge that drives one coordinate exactly to zero",
            r"\(d = -c\), with the equality \(A x = b\) ignored",
            r"the centering term of a logarithmic barrier, with the cost \(c\) omitted",
        ],
        0,
        r"The dual estimate solves \(A X^2 A^T y = A X^2 c\), and the direction is the negative scaled reduced cost. That choice keeps \(A d = 0\), so the equality constraints stay satisfied. A simplex edge walks along a basic direction and can land on a vertex. The plain vector \(-c\) need not lie in the null space of \(A\). Dropping \(c\) would be a pure centering step, not affine scaling.",
        fig=MAT,
        alt=A_MAT,
    )
    b.num(
        1,
        r"Minimize \(x_1 + 3 x_2\) subject to \(x_1 + x_2 = 4\) and \(x > 0\), starting at \((2,\ 2)\). What is the affine-scaling dual estimate \(y\)?",
        2,
        "1",
        r"\(X^2 = \mathrm{diag}(4,\ 4)\). Then \(A X^2 A^T = 8\) and \(A X^2 c = 4 \cdot 1 + 4 \cdot 3 = 16\), so \(y = 16/8 = 2\). The reduced costs are \((1 - 2,\ 3 - 2) = (-1,\ 1)\). Reporting \(16\) or \(8\) stops before the division. Reporting \(1\) is a cost coefficient. The dual estimate is the scalar that makes the direction feasible for the equality.",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        1,
        r"The primal affine-scaling step length is a fraction \(\gamma \in (0,\ 1)\) of the distance to the boundary so that",
        [
            r"the next point stays strictly positive",
            r"the next point is a vertex",
            r"some coordinate becomes negative",
            r"the equality \(A x = b\) is dropped",
        ],
        0,
        r"The direction formula divides by the coordinates through \(X^{-2}\) on the next round, so a zero coordinate is not allowed. A fraction strictly below \(1\) stops short of the wall. Landing on a vertex is what \(\gamma = 1\) would risk, and it is what the simplex method does on purpose. The direction was built to satisfy \(A d = 0\), so the equality is kept.",
        fig=SEG,
        alt=A_SEG,
    )
    b.order(
        2,
        r"Put these steps in the order of one primal affine-scaling iteration. Each step uses the result of the step before it.",
        [
            r"Build the positive diagonal matrix whose entries are the current interior coordinates.",
            r"Using that diagonal, solve \(A X^2 A^T y = A X^2 c\) for the dual estimate.",
            r"Form the reduced costs \(c - A^T y\) and the direction \(-X^2\) times those costs.",
            r"Step a fraction of the way to the orthant boundary along that direction.",
        ],
        r"The normal equation uses \(X\), so the diagonal comes first. The reduced costs use the dual estimate. The direction uses the reduced costs and the same diagonal. The step length uses the direction, because only a negative component can hit the boundary. Choosing the fraction before the direction exists is not this iteration.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"The current point is positive and the affine-scaling direction is \((2,\ -3,\ 0,\ -1)\). Which coordinates can hit zero if the step length grows?",
        [
            r"the first coordinate",
            r"the second coordinate",
            r"the third coordinate",
            r"the fourth coordinate",
        ],
        [1, 3],
        r"A coordinate decreases only when its direction component is negative."
        "\n"
        r"• The first component is \(2 > 0\), so that coordinate increases."
        "\n"
        r"• The second component is \(-3 < 0\)."
        "\n"
        r"• The third component is \(0\), so that coordinate stays fixed."
        "\n"
        r"• The fourth component is \(-1 < 0\)."
        "\n"
        r"The blocking coordinates are the second and the fourth. The step length is limited by the more restrictive of those two.",
        fig=COL,
        alt=A_COL,
    )
    b.sym(
        2,
        r"One coordinate is \(x > 0\) and its direction component \(d\) is negative. The step length that drives this coordinate exactly to zero equals",
        "-x/d",
        {"x": (1, 4), "d": (-3, -1)},
        r"The updated coordinate is \(x + \alpha d\). Setting it to zero gives \(\alpha = -x/d\). Both names appear, and the value is positive because \(d\) is negative. Using \(x/d\) is negative and would step backward. Using \(-d/x\) inverts the ratio. Adding \(x - d\) is not a step length.",
        alternates=["x/(-d)", "-1*x/d"],
        fig=SEG,
        alt=A_SEG,
    )
    b.find_error(
        3,
        r"A note steps from \((4,\ 2)\) along the direction \((2,\ -2)\). Exactly one step is a false claim.",
        [
            r"The current point is \((4,\ 2)\) and the direction is \((2,\ -2)\).",
            r"The second component of the direction is negative, so the step that drives it to zero has length \(2/2 = 1\).",
            r"Half of that blocking step has length \(1/2\).",
            r"The updated point is \((4,\ 2) - \tfrac12 (2,\ -2) = (3,\ 3)\).",
        ],
        3,
        r"The data in the first step are the ones the note is using. The second coordinate decreases, and \(-2/(-2) = 1\) is the step that hits zero. Half of that step has length \(1/2\). The update adds the direction: \((4,\ 2) + \tfrac12 (2,\ -2) = (5,\ 1)\). Subtracting it walks the wrong way and produces \((3,\ 3)\). That wrong sign increases a cost that the direction was built to decrease.",
        [
            r"The step is added, not subtracted. The updated point is \((5,\ 1)\), not \((3,\ 3)\).",
            r"The blocking step for the second coordinate is not \(1\).",
            r"Half of a blocking step of length \(1\) is not \(1/2\).",
        ],
        0,
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        3,
        r"Continue the problem \(\min x_1 + 3 x_2\) subject to \(x_1 + x_2 = 4\), \(x > 0\), from \((2,\ 2)\). The direction is \((4,\ -4)\). With fraction \(1/2\) of the blocking step, what is the new first coordinate?",
        3,
        "1",
        r"The second component is the one that decreases. The blocking step is \(2/4 = 1/2\). Half of it has length \(1/4\). The new point is \((2,\ 2) + \tfrac14 (4,\ -4) = (3,\ 1)\). The first coordinate is \(3\). Reporting \(1\) is the new second coordinate. Reporting \(1/4\) is the step length. Reporting \(4\) is a direction component. The new point stays on \(x_1 + x_2 = 4\) and stays positive.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        3,
        r"Dual affine scaling",
        [
            r"scales by the dual slacks and steps the multipliers, instead of scaling the primal coordinates",
            r"is the same computation as one simplex pivot",
            r"requires a primal coordinate that is already zero",
            r"drops the equality \(A x = b\)",
        ],
        0,
        r"The dual form keeps the slacks \(s = c - A^T y\) positive and uses a diagonal scaling built from \(s\). The primal form uses the diagonal of \(x\). A simplex pivot moves from vertex to vertex and uses a basis, not an interior scaling. A zero primal coordinate would make the primal scaling undefined. The equality constraints stay in the scaled normal equation.",
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        r"The primal affine-scaling direction is the Newton step for the scaled quadratic model",
        [
            r"minimize \(c^T d + \tfrac12 d^T X^{-2} d\) subject to \(A d = 0\)",
            r"minimize \(\lVert d\rVert\) with no constraints",
            r"a pure centering step that ignores \(c\)",
            r"the conditional-gradient vertex step on the simplex",
        ],
        0,
        r"The quadratic term \(d^T X^{-2} d\) is the squared length in the scaled metric. Its Newton step, projected onto \(A d = 0\), is \(d = -X^2 (c - A^T y)\). An unconstrained shortest vector is zero. Dropping \(c\) removes the linear program from the model. A conditional-gradient step minimizes a linear function over a polytope and does not use this scaling.",
        fig=ELL,
        alt=A_ELL,
        preview=P_PD,
    )
    b.num(
        4,
        r"In that same iteration the new point is \((3,\ 1)\) and the cost is \(c = (1,\ 3)\). What is the cost at the new point?",
        6,
        "1",
        r"The product is \(1 \cdot 3 + 3 \cdot 1 = 6\). The cost at the start \((2,\ 2)\) is \(1 \cdot 2 + 3 \cdot 2 = 8\), so the iteration decreased the objective by \(2\). Reporting \(8\) is the old cost. Reporting \(3\) is a coordinate. Reporting \(4\) is the equality right-hand side, which is unchanged. The decrease is what the negative reduced-cost direction is built to produce.",
        fig=COL,
        alt=A_COL,
        preview=P_PD,
    )
    b.mc(
        4,
        r"Taking the full step that hits the boundary, with fraction \(\gamma = 1\), would",
        [
            r"place a zero in some coordinate, so the next diagonal scaling is undefined",
            r"keep every coordinate bounded away from zero",
            r"be required before the dual estimate can be computed",
            r"make the direction orthogonal to \(c\) for every cost vector",
        ],
        0,
        r"The blocking ratio is exactly the step that zeroes the first coordinate to hit the wall. The next affine-scaling formula needs a positive diagonal, so the iteration stops strictly short of that ratio. The dual estimate is computed from the current positive point, before the step length is chosen. The direction is orthogonal to the rows of \(A\), not in general to \(c\).",
        fig=HALF,
        alt=A_HALF,
        preview=P_PD,
    )
    b.save()


def bank_pd():
    b = Bank("primal-dual-interior-point")
    b.mc(
        1,
        r"For a standard-form linear program, the perturbed KKT system replaces complementary slackness by",
        [
            r"\(x_i s_i = \mu\) for every \(i\), with \(\mu > 0\), \(x > 0\), and \(s > 0\)",
            r"\(x_i s_i = 0\), while allowing some coordinates of \(x\) to be negative",
            r"\(x_i + s_i = \mu\) for every \(i\)",
            r"\(A^T y = 0\), with the cost vector omitted",
        ],
        0,
        r"The primal equality, the dual equality, and the products \(x_i s_i = \mu\) are solved together. Ordinary complementarity is the limit \(\mu \to 0\). A sum \(x_i + s_i\) is a different equation. Negativity would leave the logarithmic neighborhood the iteration stays in. The dual equality still involves the cost.",
        fig=MAT,
        alt=A_MAT,
    )
    b.num(
        1,
        r"Take \(A = (1,\ 1)\), \(b = 6\), \(c = (4,\ 2)\), \(x = (4,\ 2)\), \(y = 0\), and \(s = (4,\ 2)\), with target \(\mu = 8\). The Newton step has \(d_x = (-2,\ 2)\). What is the new first primal coordinate, before any shortening?",
        2,
        "1",
        r"The point is primal feasible because \(4 + 2 = 6\), and dual feasible because \(s = c\). The products are \(16\) and \(4\). The Newton step that equalizes them at \(8\) is \(d_x = (-2,\ 2)\), with no change in \(y\) or \(s\). The new first coordinate is \(4 - 2 = 2\). The new point \((2,\ 4)\) has products \(8\) and \(8\). Reporting \(4\) keeps the old coordinate. Reporting \(-2\) is the step, not the updated coordinate. Reporting \(8\) is the target product.",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        1,
        r"On the central path, the duality gap \(x^T s\) equals",
        [
            r"\(n \mu\)",
            r"\(\mu / n\)",
            r"\(0\) for every positive \(\mu\)",
            r"\(\lVert x\rVert \, \lVert s\rVert\), whether or not the products equal \(\mu\)",
        ],
        0,
        r"If every product \(x_i s_i\) equals \(\mu\), the sum of the products is \(n \mu\). That sum is the duality gap. Dividing by \(n\) would be the average product, which is \(\mu\), not the gap. The gap is zero only in the limit \(\mu \to 0\). The product of the norms is at least the absolute gap, and it equals the gap only in special alignments.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.order(
        2,
        r"Put these steps in the order of one primal-dual iteration. Each step uses the result of the step before it.",
        [
            r"Choose a positive target \(\mu\) and form the primal, dual, and complementarity residuals at the current positive point.",
            r"Solve the Newton linear system on those residuals for the steps in \(x\), \(y\), and \(s\).",
            r"Shorten the common step length so the updated \(x\) and \(s\) stay positive.",
            r"Apply that shortened step, then reduce the target for the next round.",
        ],
        r"The Newton right-hand side contains the residuals, and the complementarity residual contains \(\mu\), so the target comes first. The step length is a fraction of a step that has already been computed. The update uses that shortened step. Reducing \(\mu\) for the next round happens after the point has moved. Shortening a step that has not been solved for is not a reordering of this list.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"A perturbed complementarity condition with target \(\mu = 4\) requires every product \(x_i s_i\) to equal \(4\). Which of these positive pairs \((x,\ s)\) satisfy it?",
        [
            r"\(x = (2,\ 2)\) and \(s = (2,\ 2)\)",
            r"\(x = (4,\ 1)\) and \(s = (1,\ 4)\)",
            r"\(x = (4,\ 4)\) and \(s = (1,\ 1)\)",
            r"\(x = (2,\ 4)\) and \(s = (2,\ 2)\)",
            r"\(x = (4,\ 1)\) and \(s = (1,\ 2)\)",
        ],
        [0, 1, 2],
        r"Each coordinate pair is checked on its own."
        "\n"
        r"• \((2,\ 2)\) with \((2,\ 2)\) gives products \(4\) and \(4\)."
        "\n"
        r"• \((4,\ 1)\) with \((1,\ 4)\) gives products \(4\) and \(4\)."
        "\n"
        r"• \((4,\ 4)\) with \((1,\ 1)\) gives products \(4\) and \(4\)."
        "\n"
        r"• \((2,\ 4)\) with \((2,\ 2)\) gives products \(4\) and \(8\)."
        "\n"
        r"• \((4,\ 1)\) with \((1,\ 2)\) gives products \(4\) and \(2\)."
        "\n"
        r"A single matching product is not enough. Every product has to equal the target.",
        fig=MAT,
        alt=A_MAT,
    )
    b.sym(
        2,
        r"One complementarity residual, for a primal coordinate \(x\), a slack \(s\), and a target \(m\), equals",
        "x*s-m",
        {"x": (1, 4), "s": (1, 4), "m": (1, 4)},
        r"The perturbed equation is \(x s = m\), so the residual is \(x s - m\). Every name appears. The sum \(x + s - m\) is a different residual. The product \(x s\) alone is the complementarity value before the target is subtracted. Negating the product flips the sign of the Newton right-hand side.",
        alternates=["s*x-m", "x*s-1*m"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note takes a Newton step on a perturbed system with \(x = (3,\ 1)\), \(s = (3,\ 1)\), \(b = 4\), \(c = (3,\ 1)\), \(y = 0\), and target \(\mu = 3\). Exactly one step is a false claim.",
        [
            r"The primal residual and the dual residual are both zero.",
            r"The complementarity right-hand sides \(\mu - x_i s_i\) are \(3 - 9 = -6\) and \(3 - 1 = 2\).",
            r"The Newton step has \(d_x = (-2,\ 2)\) and \(d_y = 0\).",
            r"The Newton update adds the opposite of \(d_x\), so the new primal vector is \((5,\ -1)\).",
        ],
        3,
        r"The sums \(3 + 1 = 4\) and \(s = c\) make the primal and dual residuals zero. The products are \(9\) and \(1\), so the right-hand sides are \(-6\) and \(2\). Solving the Newton system gives \(d_x = (-2,\ 2)\) and no dual step. The update adds that step: \((3,\ 1) + (-2,\ 2) = (1,\ 3)\). Adding the opposite produces \((5,\ -1)\), which is not positive and is not the Newton update.",
        [
            r"The step \(d_x\) is added. The new primal vector is \((1,\ 3)\), not \((5,\ -1)\).",
            r"The products are not \(9\) and \(1\).",
            r"The right-hand side \(3 - 9\) is not \(-6\).",
        ],
        0,
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        3,
        r"After the Newton step of the feasible point \(x = (4,\ 2)\), \(s = (4,\ 2)\) with target \(\mu = 8\), the new primal vector is \((2,\ 4)\) and the slacks are unchanged. What is the new duality gap \(x^T s\)?",
        16,
        "1",
        r"The new products are \(2 \cdot 4 = 8\) and \(4 \cdot 2 = 8\). Their sum is \(16\). That is \(n \mu\) with \(n = 2\). The old gap was \(16 + 4 = 20\). Reporting \(8\) is one product, not the sum. Reporting \(20\) is the old gap. Reporting \(4\) is a coordinate. On the central path the gap equals the sum of the products, which the Newton step has just equalized.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        3,
        r"One primal-dual iteration",
        [
            r"takes a Newton step on the perturbed KKT map, then shortens it so \(x\) and \(s\) stay positive",
            r"pivots from one vertex to another",
            r"sets \(\mu = 0\) and never recenters",
            r"updates only the dual multipliers",
        ],
        0,
        r"The perturbed map is nonlinear because of the products \(x_i s_i\). Newton's method linearizes it. A full step can drive a coordinate negative, so the step is shortened. A vertex pivot is the simplex method. Setting \(\mu = 0\) is the predictor, or affine-scaling, direction. The centering target stays positive on a path-following step. The step updates \(x\), \(y\), and \(s\) together.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        4,
        r"Driving the target \(\mu\) toward \(0\) along the central path makes",
        [
            r"the complementarity products, and therefore the duality gap, tend to \(0\)",
            r"the primal residual \(A x - b\) grow",
            r"the iterates leave the positive orthant on the first step",
            r"the Newton Jacobian diagonal for every linear program",
        ],
        0,
        r"On the path every product equals \(\mu\), so the gap \(n \mu\) tends to \(0\) with the target. The path is defined to keep \(A x = b\) and the dual equality, so those residuals stay zero. The points stay positive for every positive \(\mu\). The Jacobian carries the diagonal matrices of \(x\) and \(s\), but also the constraint matrix \(A\), so it is not diagonal in general.",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_FW,
    )
    b.num(
        4,
        r"A central point of a standard-form linear program in \(n = 5\) variables has every product \(x_i s_i\) equal to \(2\). What is the duality gap?",
        10,
        "1",
        r"The gap is the sum of the products, which is \(n \mu = 5 \cdot 2 = 10\). Reporting \(2\) is the common product. Reporting \(5\) is the variable count. Reporting \(2.5\) divides the product by the count instead of multiplying. The gap is the quantity the target \(\mu\) controls. It is not the distance from the current point to a vertex.",
        fig=MAT,
        alt=A_MAT,
        preview=P_FW,
    )
    b.mc(
        4,
        r"A short-step path-following method reaches a duality gap that is a fraction \(\varepsilon\) of the initial gap in a number of Newton steps on the order of",
        [
            r"\(\sqrt{n}\) times a logarithm of \(1/\varepsilon\)",
            r"\(n\) simplex pivots, with no dependence on the gap",
            r"a constant that does not grow with \(n\) or with \(1/\varepsilon\)",
            r"the square of the condition number of \(A\), with no role for the gap",
        ],
        0,
        r"The classical short-step count is a bound on how many Newton steps it takes to shrink the duality gap. The gap, not the Euclidean distance to a vertex, is the quantity inside \(\varepsilon\). A simplex pivot count is a different algorithm and can be exponential. The count grows, slowly, with the number of inequalities and with the requested reduction. The condition number of \(A\) is not the quantity this iteration bound tracks.",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_FW,
    )
    b.save()


def bank_fw():
    b = Bank("frank-wolfe-conditional-gradient")
    b.mc(
        1,
        r"One conditional-gradient step",
        [
            r"minimizes the linear model \(\nabla f(x)^T s\) over the set, then moves from \(x\) toward that \(s\)",
            r"projects \(x - \nabla f(x)\) onto the set",
            r"solves a Newton system with the Hessian",
            r"requires the feasible set to be a Euclidean ball",
        ],
        0,
        r"The linear minimization oracle replaces the projection. The next point is a convex combination of \(x\) and the oracle's answer, so it stays in the set when the set is convex. Projecting a gradient step is the projected-gradient method. A Newton system uses a quadratic model. The oracle is useful on a simplex or an \(\ell_1\) ball, not only on a Euclidean ball.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.num(
        1,
        r"On the simplex \(x + y = 1\), \(x \ge 0\), \(y \ge 0\), start at \((1/2,\ 1/2)\) where the gradient is \((-1,\ 3)\). With step fraction \(1/2\), what is the first coordinate of the next point?",
        0.75,
        "1",
        r"The smaller gradient component is \(-1\), in the first coordinate, so the oracle returns \((1,\ 0)\). The update is \(\tfrac12 (1/2,\ 1/2) + \tfrac12 (1,\ 0) = (3/4,\ 1/4)\). The first coordinate is \(3/4\). Reporting \(1/4\) is the second coordinate. Reporting \(1\) is the oracle's first coordinate, which would be the full step \(\gamma = 1\). Reporting \(-1\) is the gradient component. The oracle minimizes the linear model, so it selects the smaller component.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.mc(
        1,
        r"On the probability simplex, the linear minimization oracle returns",
        [
            r"a standard-basis vector at a smallest gradient component",
            r"a standard-basis vector at a largest gradient component",
            r"the barycenter, for every gradient",
            r"the Euclidean projection of the gradient onto the simplex",
        ],
        0,
        r"A linear function on a polytope attains its minimum at a vertex. On the simplex the vertices are the standard-basis vectors, and the linear value at \(e_i\) is the \(i\)-th gradient component. The minimum is the smallest component. The largest component maximizes the linear model. The barycenter ignores the gradient. A Euclidean projection is a different subproblem.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.order(
        2,
        r"Put these steps in the order of one conditional-gradient iteration. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient at the current feasible point.",
            r"Minimize the linear function defined by that gradient over the feasible set, and call the minimizer \(s\).",
            r"Form the direction from the current point to \(s\).",
            r"Move from the current point by a fraction of that direction, with the fraction in \((0,\ 1]\).",
        ],
        r"The linear function is built from the gradient, so the gradient comes first. The direction points at the oracle's answer, so the oracle comes before the direction. The move uses the direction. An open-loop fraction such as \(2/(k+2)\) still multiplies a direction that has to be formed first. Projecting a gradient step is not one of these steps.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"On the probability simplex in \(\mathbb{R}^3\), the gradient is \((2,\ 2,\ 5)\). Which points minimize the linear model?",
        [
            r"\((1,\ 0,\ 0)\)",
            r"\((0,\ 1,\ 0)\)",
            r"\((0,\ 0,\ 1)\)",
            r"\((1/2,\ 1/2,\ 0)\)",
            r"\((1/2,\ 0,\ 1/2)\)",
        ],
        [0, 1, 3],
        r"The linear value of a point is the gradient's product with that point."
        "\n"
        r"• \((1,\ 0,\ 0)\) and \((0,\ 1,\ 0)\) each give \(2\)."
        "\n"
        r"• \((0,\ 0,\ 1)\) gives \(5\)."
        "\n"
        r"• \((1/2,\ 1/2,\ 0)\) gives \(2\)."
        "\n"
        r"• \((1/2,\ 0,\ 1/2)\) gives \(1 + 5/2 = 7/2\)."
        "\n"
        r"The minimum value is \(2\). Any convex combination of the minimizing vertices is also a minimizer. The oracle may return any of them.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.sym(
        2,
        r"A conditional-gradient update with fraction \(g\) moves a coordinate from \(a\) toward the oracle value \(b\). The new coordinate equals",
        "(1-g)*a+g*b",
        {"a": (-2, 2), "b": (-2, 2), "g": (0.2, 0.8)},
        r"The update is the convex combination \((1 - g) a + g b\). Every name appears. Using \(g a + (1 - g) b\) swaps the current point with the oracle point. Using \(a + b\) drops the fraction. Using \(g (b - a)\) is the displacement, not the new coordinate.",
        alternates=["a+g*(b-a)", "(1-g)*a+b*g"],
        fig=SEG,
        alt=A_SEG,
    )
    b.find_error(
        3,
        r"A note runs the linear oracle on the probability simplex with gradient \((4,\ -1)\). Exactly one step is a false claim.",
        [
            r"The feasible set is the probability simplex in \(\mathbb{R}^2\).",
            r"The gradient components are \(4\) and \(-1\).",
            r"The linear oracle returns \((1,\ 0)\), because \(4\) is the larger component.",
            r"With fraction \(1\), the next point is the oracle's answer.",
        ],
        2,
        r"The simplex and the gradient are as stated. Minimizing the linear model selects the smaller component, which is \(-1\), so the oracle returns \((0,\ 1)\). The vertex \((1,\ 0)\) maximizes the linear model. With fraction \(1\) the next point is whatever the oracle returned, so the fourth step is the right rule applied to the wrong vertex. The false claim is the choice of vertex.",
        [
            r"The oracle minimizes the linear model, so it returns \((0,\ 1)\), the vertex of the smaller component.",
            r"The gradient components are not \(4\) and \(-1\).",
            r"A fraction of \(1\) does not move all the way to the oracle's answer.",
        ],
        0,
        fig=SIMP,
        alt=A_SIMP,
    )
    b.num(
        3,
        r"The open-loop conditional-gradient fraction is \(2/(k + 2)\), with \(k\) counting from \(0\). What is that fraction at \(k = 6\)?",
        0.25,
        "1",
        r"The denominator is \(6 + 2 = 8\), so the fraction is \(2/8 = 1/4\). At \(k = 0\) the same formula equals \(1\), a full step to the oracle's answer. Reporting \(2/6\) uses \(k\) without the shift. Reporting \(1\) is the first fraction, not the fraction at step \(6\). Reporting \(8\) is the denominator. This number is a step fraction. It is not the function gap.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        3,
        r"On the \(\ell_1\) ball, the linear minimization oracle returns",
        [
            r"\(\pm e_i\) at a coordinate of largest gradient magnitude, with the sign opposite the gradient",
            r"the Euclidean projection of \(-\nabla f\) onto the unit disk",
            r"the origin, for every nonzero gradient",
            r"a vector with every coordinate equal to the same nonzero value",
        ],
        0,
        r"The \(\ell_1\) ball's extreme points are the signed standard-basis vectors. The linear value at \(\sigma e_i\) is \(\sigma g_i\), so the minimum uses the most negative product: the largest \(|g_i|\), with \(\sigma = -\mathrm{sign}(g_i)\). A Euclidean projection is the oracle for a disk. The origin has linear value zero, which is worse than a negative value. Equal coordinates are not an extreme point of the \(\ell_1\) ball.",
        fig=BALLS,
        alt=A_BALLS,
    )
    b.mc(
        4,
        r"With fractions \(2/(k + 2)\), the conditional-gradient guarantee of order \(1/k\) bounds",
        [
            r"the function gap \(f(x_k) - f^\star\)",
            r"the distance \(\lVert x_k - x^\star\rVert\)",
            r"the gradient norm alone, with no claim about the gap",
            r"the number of vertices the oracle returns",
        ],
        0,
        r"For a smooth convex objective on a compact convex set, the curvature argument gives \(f(x_k) - f^\star \le 2 C_f / (k + 2)\). The left side is the function gap. The distance to a minimizer can stay large while the gap is small, because the method may approach the optimum along a face. The bound does not count oracle vertices. The gradient norm is controlled only indirectly, through that gap.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_POW,
    )
    b.num(
        4,
        r"On the \(\ell_1\) ball, the gradient is \((3,\ -6,\ 1)\) and the current point is \((1/5,\ -2/5,\ 1/10)\). With fraction \(1/2\), what is the second coordinate of the next point?",
        0.3,
        "1",
        r"The largest magnitude is \(6\), and that component is negative, so the oracle returns \((0,\ 1,\ 0)\). The update is half the current point plus half the oracle point: the second coordinate is \(\tfrac12 (-2/5) + \tfrac12 (1) = 3/10\). Reporting \(-2/5\) keeps the old coordinate. Reporting \(1\) is the oracle's second coordinate. Reporting \(6\) is the gradient magnitude. The first and third coordinates shrink toward zero and do not affect this component.",
        fig=BALLS,
        alt=A_BALLS,
        preview=P_POW,
    )
    b.mc(
        4,
        r"The open-loop fraction \(2/(k + 2)\), with \(k\) counting from \(0\),",
        [
            r"equals \(1\) on the first iteration and decreases toward \(0\)",
            r"stays equal to \(1\) at every iteration",
            r"equals the exact line-search step for every quadratic",
            r"is larger than \(1\) for every \(k \ge 0\)",
        ],
        0,
        r"At \(k = 0\) the fraction is \(2/2 = 1\). The denominator grows with \(k\), so later fractions fall toward \(0\) and stay at most \(1\). A constant fraction of \(1\) would jump to a vertex at every iteration. Exact line search minimizes the objective along the segment and depends on the gradient and the curvature, not only on the counter \(k\).",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_POW,
    )
    b.save()


def bank_power():
    b = Bank("power-method-eigenvector")
    b.mc(
        1,
        r"One power iteration on a symmetric matrix",
        [
            r"replaces the vector by the matrix times the vector, then divides by the Euclidean length",
            r"replaces the vector by its component along the smallest eigenvector",
            r"adds the identity and stops",
            r"minimizes the Rayleigh quotient by projecting a gradient step onto a box",
        ],
        0,
        r"The iteration is \(x_+ = A x / \lVert A x\rVert\). The largest-magnitude eigenvalue dominates the product. The smallest eigenvector is what an inverse iteration, or a shift, is aimed at. Adding the identity changes the eigenvalues. A projected gradient step on a box is a different algorithm. The sphere's linear oracle for \(x^T A x\) returns this same normalization.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"Let \(A = \mathrm{diag}(5,\ 1)\), and start at \((1,\ 1)\). After one multiplication by \(A\), what is the ratio of the second component to the first?",
        0.2,
        "1",
        r"\(A (1,\ 1) = (5,\ 1)\). The ratio of the second component to the first is \(1/5\). Normalization would divide both components by the same length, so the ratio is unchanged. This ratio equals \(|\lambda_2 / \lambda_1|\). It is the factor by which the second-mode coefficient shrinks. It is not the error in the Rayleigh quotient, which scales with the square of this factor. Reporting \(5\) inverts the ratio. Reporting \(1\) is the old ratio.",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        1,
        r"As a conditional-gradient step for \(x^T A x\) on the unit sphere, the linear oracle returns",
        [
            r"the normalization of \(A x\)",
            r"the normalization of \(x\), with \(A\) unused",
            r"a coordinate vector, for every symmetric \(A\)",
            r"the eigenvector of the smallest eigenvalue, in one step, from every start",
        ],
        0,
        r"The gradient of \(x^T A x\) on the sphere points along \(A x\). Maximizing the linear model over the sphere aligns the direction with \(A x\) and then normalizes. Returning \(x\) ignores \(A\). A coordinate vector is the oracle on a simplex, not on a sphere. One step does not finish at the smallest eigenvector. The top direction is the one this oracle approaches.",
        fig=DISK,
        alt=A_DISK,
    )
    b.order(
        2,
        r"Put these steps in the order of one power iteration aimed at the top eigenvector. Each step uses the result of the step before it.",
        [
            r"Choose a nonzero starting vector that is not orthogonal to the top eigenvector.",
            r"Multiply that vector by the symmetric matrix.",
            r"Compute the Euclidean length of the product.",
            r"Divide the product by that length to get the next direction.",
        ],
        r"The product uses the starting vector, so the start comes first. The length uses the product. The division uses both the product and the length. A start orthogonal to the top eigenvector never grows that component, so the later steps cannot create it. Dividing before the product exists is not a reordering of this list.",
        fig=ARR,
        alt=A_ARR,
    )
    b.multi(
        2,
        r"For \(A = \mathrm{diag}(4,\ 1)\), the top eigenvector is along \((1,\ 0)\). Which starting vectors are orthogonal to it, so power iteration stays off that eigenvector?",
        [
            r"\((0,\ 1)\)",
            r"\((0,\ 3)\)",
            r"\((2,\ -1)\)",
            r"\((0,\ -2)\)",
            r"\((1,\ 1)\)",
        ],
        [0, 1, 3],
        r"Orthogonality to \((1,\ 0)\) means the first component is zero."
        "\n"
        r"• \((0,\ 1)\), \((0,\ 3)\), and \((0,\ -2)\) all have first component \(0\). They are multiples of the second eigenvector, and \(A\) keeps them there."
        "\n"
        r"• \((2,\ -1)\) has first component \(2\)."
        "\n"
        r"• \((1,\ 1)\) has first component \(1\)."
        "\n"
        r"A nonzero first component is what the factor \(|\lambda_2 / \lambda_1|\) then shrinks, relative to the top mode.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.sym(
        2,
        r"For \(A = \mathrm{diag}(p,\ q)\) and the vector \((1,\ s)\), the Rayleigh quotient equals",
        "(p+q*s*s)/(1+s*s)",
        {"p": (1, 4), "q": (1, 4), "s": (0.5, 2)},
        r"The quotient is \(x^T A x / x^T x\). The numerator is \(p \cdot 1 + q s^2\), and the denominator is \(1 + s^2\). Every name appears. Using \(p + q\) drops the vector. Using \(p + q s\) forgets the square on the second component. Swapping \(p\) and \(q\) assigns each eigenvalue to the wrong component.",
        alternates=["(p+q*s^2)/(1+s^2)"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        r"A note describes power iteration on \(A = \mathrm{diag}(6,\ 2)\). Exactly one step is a false claim.",
        [
            r"The eigenvalues are \(6\) and \(2\), and \(6\) is the one of larger magnitude.",
            r"Each iteration multiplies the second-mode coefficient by \(|2/6| = 1/3\).",
            r"After three iterations that coefficient ratio has been multiplied by \(1/27\).",
            r"The Rayleigh-quotient error is multiplied by \(1/27\) as well.",
        ],
        3,
        r"The diagonal entries are the eigenvalues, and \(|6| > |2|\). The second coefficient is multiplied by \(\lambda_2 / \lambda_1 = 1/3\) at each step, so three steps multiply it by \(1/27\). The Rayleigh quotient sits between the eigenvalues, and its error is quadratic in the size of the second component. Three steps multiply that error by \((1/3)^6 = 1/729\), not by \(1/27\). The angle and the eigenvalue error are different measures.",
        [
            r"The Rayleigh error scales with the square of the second-mode factor, so three steps multiply it by \(1/729\), not by \(1/27\).",
            r"The second-mode factor is not \(1/3\).",
            r"Three factors of \(1/3\) do not multiply to \(1/27\).",
        ],
        0,
        fig=DECAY,
        alt=A_DECAY,
    )
    b.num(
        3,
        r"For \(A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}\) and the vector \((2,\ 1)\), what is the Rayleigh quotient?",
        2.8,
        "1",
        r"\(A (2,\ 1) = (5,\ 4)\). The numerator is \((2,\ 1) \cdot (5,\ 4) = 14\). The denominator is \(4 + 1 = 5\). The quotient is \(14/5 = 2.8\). The eigenvalues of \(A\) are \(3\) and \(1\), and \(2.8\) lies between them. Reporting \(14\) stops before the division. Reporting \(5\) is the squared length. Reporting \(3\) is the top eigenvalue, which this vector has not reached. The quotient error and the eigenvector angle are different: this value is the quotient itself.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        3,
        r"When \(|\lambda_1| > |\lambda_2|\), the factor \(|\lambda_2 / \lambda_1|\) governs",
        [
            r"how fast the second-mode coefficient, and thus the angle with the top eigenvector, shrinks",
            r"the Rayleigh-quotient error with that same power, rather than its square",
            r"the function-gap bound of projected gradient",
            r"the condition number of a Hessian that this iteration does not form",
        ],
        0,
        r"Writing the start in the eigenbasis, each step multiplies the coefficient of \(v_j\) by \(\lambda_j\). Relative to the top coefficient, the second coefficient is multiplied by \(\lambda_2 / \lambda_1\). That ratio controls the angle. The Rayleigh quotient equals \(\lambda_1\) plus a term quadratic in the second coefficient, so its error uses the square of the factor. Projected gradient and a Hessian condition number are different rates.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        4,
        r"The error in the Rayleigh quotient, measured against the top eigenvalue, shrinks like",
        [
            r"the square of the second-mode factor, because the quotient is quadratic in that contamination",
            r"the first power of \(|\lambda_2 / \lambda_1|\), the same measure as the angle",
            r"a constant, so the quotient never improves",
            r"\(|\lambda_1 / \lambda_2|\), which is larger than \(1\)",
        ],
        0,
        r"If the second coefficient is \(\varepsilon\), the quotient's gap from \(\lambda_1\) is on the order of \(\varepsilon^2\). Each power step multiplies \(\varepsilon\) by \(|\lambda_2 / \lambda_1|\), so the quotient gap is multiplied by the square of that factor. Using the unsquared factor describes the angle, not the eigenvalue error. The reciprocal factor is larger than \(1\) and would describe a growing component. The quotient does improve when the top eigenvalue is strictly dominant.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_SVD,
    )
    b.num(
        4,
        r"Continue \(A = \mathrm{diag}(5,\ 1)\) from \((1,\ 1)\). After two multiplications by \(A\), what is the ratio of the second component to the first?",
        0.04,
        "1",
        r"One multiplication produces \((5,\ 1)\). The second produces \((25,\ 1)\). The ratio is \(1/25 = 0.04\). That is \((|\lambda_2 / \lambda_1|)^2\), the second-mode factor applied twice. Normalization does not change the ratio. Reporting \(0.2\) stops after one multiplication. Reporting \(0.008\) squares the factor an extra time, which is the Rayleigh scaling rather than the component ratio. This number tracks the eigenvector contamination, not the Rayleigh error.",
        fig=COL,
        alt=A_COL,
        preview=P_SVD,
    )
    b.mc(
        4,
        r"The same normalization of a matrix-vector product, applied to \(A^T A\), produces",
        [
            r"a direction that approaches a top right singular vector of \(A\)",
            r"a top left singular vector, without using \(A^T\)",
            r"the smallest eigenvalue of every indefinite matrix in one step",
            r"a vector orthogonal to the leading right singular direction",
        ],
        0,
        r"The eigenvalues of the symmetric matrix \(A^T A\) are the squares of the singular values of \(A\), and the eigenvectors are the right singular vectors. Power iteration on \(A^T A\) therefore approaches a singular vector for the largest singular value. The left singular vectors are the eigenvectors of \(A A^T\). One step does not extract the smallest eigenvalue. The iteration aligns with the leading direction. It does not stay orthogonal to it, unless it was started that way.",
        fig=ELL,
        alt=A_ELL,
        preview=P_SVD,
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


def expl_opt():
    save_explainer(
        "optimality-over-convex-set",
        "Optimality over a convex set",
        _sec(
            r"""A minimizer on a convex set need not have a zero gradient. The set can block the direction you would like to move. What replaces the zero-gradient test is a one-sided statement about feasible moves. From a candidate, every other feasible point has to look uphill, or at least not downhill, to first order.

Pair the gradient at the candidate with the vector from the candidate to any feasible point. The pairing has to be nonnegative. If some feasible point gives a negative pairing, a short step toward that point decreases the objective, so the candidate is not a local minimizer. Convexity of the set is what makes that step legal: the segment between the candidate and the feasible point stays inside the set.

An interior candidate has every direction and its opposite available, so the gradient itself is zero. When the objective is also convex, the inequality is enough for a global minimizer, because the graph stays above its tangent. Without that convexity the tangent test can hold at a maximum.""",
            r"""For differentiable \(f\) and convex \(\mathcal{X}\), a local minimizer \(x^\star\) satisfies
\[
\nabla f(x^\star)^T (x - x^\star) \ge 0 \qquad \text{for every } x \in \mathcal{X}.
\]
If \(f\) is convex, every feasible point that satisfies the inequality is a global minimizer. On a polygon it is enough to test the vertices, because a linear function attains its minimum there.""",
            r"""Take \(f(t) = (t - 7)^2\) on the interval from \(0\) to \(1\), and test the right endpoint. The derivative is \(2(t - 7)\), so at \(1\) it equals \(-12\). The step from \(1\) back to \(0\) is \(-1\). The product is \((-12)(-1)\).

The anchor value is 12. Every feasible step from the right endpoint points left, and the derivative does too, so the product stays nonnegative. The unconstrained minimizer sits to the right of the interval.

The objective \(t^3\) on \([-2,\ 2]\) has a zero derivative at the origin, so the inequality holds, but the value at \(-2\) is \(-8\). The origin is not a minimizer.""",
            r"""A nonnegative pairing means feasible steps are not descent steps. Demanding a zero gradient on the boundary is a second slip: the gradient may point out of the set. Treating the inequality as a global certificate without convexity of the objective is a third. Necessity does not need that convexity. Sufficiency does. Checking one feasible point is not enough. On a polygon every vertex has to be tested.""",
            r"""The squared distance to a fixed point is a convex objective. Its variational inequality is the obtuse-angle test that characterizes the Euclidean projection onto a closed convex set. Projected gradient builds each step so that the inequality is the fixed-point condition. A conditional-gradient step uses the same inequality in linear form: the gradient's product with every feasible direction is tested by minimizing a linear function over the set.""",
            HALF,
            A_HALF,
        ),
    )


def expl_proj():
    save_explainer(
        "projection-onto-convex-set",
        "Projection onto a convex set",
        _sec(
            r"""The projection of a point \(z\) onto a nonempty closed convex set is the nearest point of the set. Closedness gives a nearest point, and convexity makes it unique. The useful form of that fact is an angle test, not a search over the set.

Let \(p\) be the candidate. The vector from \(p\) to \(z\) has to make an obtuse or right angle with the vector from \(p\) to every other point of the set. If some feasible point formed an acute angle, moving from \(p\) toward that point would get closer to \(z\). The test is the variational inequality for the squared distance, whose gradient at \(p\) is \(p - z\).

On an axis-aligned box the squared distance separates by coordinate, and so does the box. Each coordinate of \(z\) is replaced by the nearest endpoint of its interval, or kept when it is already inside. On a closed ball, a point inside is its own projection. A point outside is pulled to the sphere along the ray from the center, at a distance equal to the radius.

A different inner product changes the nearest point. If the squared length is \(v^T H v\) with \(H\) symmetric positive definite, the angle test uses that product. On a box, a diagonal \(H\) still clips coordinate by coordinate. On a half-space the correction follows \(H^{-1} a\), not the Euclidean normal.""",
            r"""With \(p\) the Euclidean projection of \(z\),
\[
(z - p)^T (x - p) \le 0 \qquad \text{for every feasible } x.
\]
Onto the ball of radius \(r\) about \(c\), an outside point lands at \(c + r (z - c)/\lVert z - c\rVert\). In the \(H\)-norm the inequality is \((z - p)^T H (x - p) \le 0\).""",
            r"""Project \(z = (7,\ 2)\) onto the box \([1,\ 4] \times [0,\ 5]\). The first coordinate \(7\) lies above \(4\), so it clips to \(4\). The second coordinate \(2\) already lies between \(0\) and \(5\), so it stays. The projection is \((4,\ 2)\).

The peg coordinate is 4. The squared distance is \((7 - 4)^2 = 9\). Clipping the second coordinate as well would move a feasible coordinate and increase the distance. Against a disk, both coordinates of an outside point scale together. A box does not do that.""",
            r"""The angle inequality runs opposite the general variational inequality, because the gradient of the squared distance is \(p - z\). Averaging coordinates is not a box projection. Clipping is coordinatewise. Scaling onto a sphere by the squared length, instead of the length, is a third slip. An open ball need not contain its nearest boundary point. After the metric changes to \(H\), a half-space correction follows \(H^{-1} a\).""",
            r"""A projected gradient step subtracts a multiple of the gradient and then applies this projection. The fixed point of that map is stationarity on the set. When the metric is a Hessian rather than the identity, the same projection is a projected Newton step. The conditional-gradient method never forms this nearest point. It minimizes a linear model instead.""",
            BOX,
            A_BOX,
        ),
    )


def expl_gp():
    save_explainer(
        "gradient-projection-method",
        "Gradient projection method",
        _sec(
            r"""Projected gradient is ordinary gradient descent with a correction that puts the point back into the set. From a feasible point, subtract a step size times the gradient. That trial point may leave the set. Replace it by its projection. The new point is feasible, because the projection lands in the set.

The same map is a stationarity test. A feasible point is stationary when it equals the projection of itself minus any positive multiple of the gradient. If the gradient step wants to leave, and the projection brings the point back to where it started, there is no feasible descent step. If the trial point is already feasible, the projection does nothing and the iteration is an ordinary gradient step. On the whole space, that is every iteration.

When the gradient is Lipschitz and the step is at most \(1/L\), each accepted step reduces the objective by a multiple of the squared move. For a convex objective those reductions sum to a function-gap bound of order \(1/k\): the gap is at most the squared distance from the start to a minimizer, divided by \(2 t k\). That ceiling bounds \(f(x_k) - f^\star\), not the distance from \(x_k\) to a minimizer.""",
            r"""One iteration is
\[
x_+ = P_{\mathcal{X}}\!\left(x - t \nabla f(x)\right).
\]
Stationarity says \(x\) equals that projection. For convex \(f\) with \(L\)-Lipschitz gradient and \(0 < t \le 1/L\),
\[
f(x_k) - f^\star \le \frac{\lVert x_0 - x^\star\rVert^2}{2 t k}.
\]""",
            r"""Minimize \((x - 8)^2\) on the interval from \(0\) to \(3\), starting at \(1\), with step size \(1/4\). The derivative at \(1\) is \(2(1 - 8) = -14\). The trial point is \(1 - (1/4)(-14) = 1 + 3.5\).

The latch point is 3. The trial value \(4.5\) lies past the interval, and clipping returns the right endpoint. The second derivative is \(2\), so \(1/L = 1/2\) and the step \(1/4\) is inside the safe range. With squared initial distance \(9\), step \(1/3\), and \(k = 3\), the gap ceiling is \(9/2\). That number bounds the function gap.""",
            r"""Skipping the projection accepts an infeasible trial point. Reading the \(O(1/k)\) theorem as a bound on \(\lVert x_k - x^\star\rVert\) is a second slip. It bounds the function gap. A step larger than \(1/L\) does not inherit that ceiling. The fixed-point test does not require a zero gradient on the boundary.""",
            r"""Replacing the Euclidean projection by a projection in a different inner product gives the scaled method. One choice of that inner product is the Hessian, which is projected Newton. A conditional-gradient step never projects the trial point. It minimizes the linear model over the set and walks toward that answer, and its gap bound is also of order \(1/k\).""",
            SEG,
            A_SEG,
        ),
    )


def expl_scaled():
    save_explainer(
        "scaled-gradient-projection",
        "Scaled gradient projection",
        _sec(
            r"""A scaled projected step changes the shape of the quadratic model, not the feasible set. Instead of moving by a multiple of the gradient and projecting in the Euclidean norm, the step minimizes
the linear model plus a squared length measured by a symmetric positive definite matrix \(H\). Completing the square shows that this is an ordinary projection, in the \(H\)-norm, of the trial point \(x - t H^{-1} \nabla f(x)\).

The identity matrix recovers Euclidean projected gradient. A diagonal matrix stretches the coordinates independently. On an axis-aligned box the \(H\)-norm still separates, so the update clips each trial coordinate \(x_i - t g_i / H_{ii}\) to its interval. Off-diagonal entries couple the coordinates, and so does a constraint that mixes them, such as a slanted half-space. There the correction follows \(H^{-1}\) times the normal, and the landing point differs from the Euclidean projection.

Projected Newton takes \(H\) to be the Hessian when it is positive definite, or a positive definite modification when it is not, and takes the step size equal to \(1\). The trial point is the Newton point. If it already lies in the set, the iteration matches unconstrained Newton. If it lies outside, the Hessian-norm projection minimizes the quadratic model over the set.

With a fixed positive definite \(H\), the \(O(1/k)\) statement still bounds the function gap of a smooth convex objective, not the distance to a minimizer. When \(H\) is the Hessian and the Newton point stays feasible, the iteration is Newton's method again.""",
            r"""The trial point and the model are
\[
v = x - t H^{-1} \nabla f(x),
\]
\[
y \in \arg\min_{u \in \mathcal{X}} \nabla f(x)^T (u - x) + \frac{1}{2t} (u - x)^T H (u - x).
\]
The minimizer is the projection of \(v\) onto \(\mathcal{X}\) in the norm \(\sqrt{u^T H u}\). Projected Newton uses the Hessian for \(H\) and \(t = 1\).""",
            r"""Take \(H = \mathrm{diag}(5,\ 1)\), gradient \((10,\ 1)\), step size \(1\), and the point \((5,\ 2)\), on the box \([0,\ 4] \times [0,\ 4]\). The scaled gradient is \((10/5,\ 1/1) = (2,\ 1)\). The trial point is \((5,\ 2) - (2,\ 1)\).

The wedge coordinate is 3. The trial point \((3,\ 1)\) already lies in the box, so clipping changes nothing. Dividing the gradient by the diagonal is \(H^{-1}\). Multiplying by the diagonal is not this method.

For a second derivative of \(8\) and a derivative of \(8\) at the point \(3\), the Newton point is \(2\). On the interval \([0,\ 1]\) the projection is the right endpoint \(1\).""",
            r"""Multiplying the gradient by \(H\) instead of by \(H^{-1}\) points the trial step the wrong way in the metric. A second slip is to clip in the Euclidean norm after a Newton step and call every such clip projected Newton. On a slanted set the nearest point depends on the metric. Dropping the projection whenever the Hessian is positive definite is a third slip. Positive definiteness does not keep the Newton point inside the set. A singular or indefinite matrix is not a legal \(H\).""",
            r"""Affine scaling is this idea inside a linear program. The scaling is the diagonal of the current positive point, the objective is linear, and the projection is onto the affine set \(A d = 0\). The resulting direction is a Newton step on that scaled quadratic model. A primal-dual interior-point step later puts the same Newton idea on a perturbed complementarity system, with both primal and dual variables moving.""",
            ELL,
            A_ELL,
        ),
    )


def expl_affine():
    save_explainer(
        "affine-scaling-method",
        "Affine scaling for linear programs",
        _sec(
            r"""Affine scaling stays in the interior of a standard-form linear program and follows a scaled steepest-descent direction. The objective is linear, so an unscaled steepest step is just a multiple of the cost, and it will usually leave the affine set \(A x = b\). The scaling and a projection put it back.

At a strictly positive \(x\), let \(X\) be the diagonal matrix of those coordinates. The local model minimizes the linear cost plus a squared length \(d^T X^{-2} d\), subject to \(A d = 0\). The squared length is large where a coordinate is small, so the step is reluctant to approach the wall. The minimizer is \(d = -X^2 (c - A^T y)\), where the dual estimate \(y\) solves the scaled normal equation \(A X^2 A^T y = A X^2 c\). That choice is exactly what makes \(A d = 0\).

The direction usually has some negative components. Each of those components reaches zero at the step length \(x_i / |d_i|\). The iteration takes a fraction of the smallest such length, with the fraction strictly below one, so the next point stays positive and the next diagonal is defined. A full step to the wall would zero a coordinate and stop the formula.

The same construction on the dual slacks is dual affine scaling. Neither version is a simplex pivot, which walks an edge and lands on a vertex. Affine scaling cuts through the interior.""",
            r"""With \(X = \mathrm{diag}(x)\) and \(x > 0\),
\[
A X^2 A^T y = A X^2 c, \qquad d = -X^2 (c - A^T y).
\]
The step is \(x + \alpha d\) with \(\alpha = \gamma \min_{d_i < 0} (-x_i / d_i)\) and \(\gamma \in (0,\ 1)\). The model being minimized in \(d\) is \(c^T d + \tfrac12 d^T X^{-2} d\) subject to \(A d = 0\).""",
            r"""Minimize \(x_1 + 2 x_2\) subject to \(x_1 + x_2 = 6\), starting at \((3,\ 3)\). The squared diagonal entries are \(9\) and \(9\). The normal coefficient is \(18\), and the right-hand side is \(9 \cdot 1 + 9 \cdot 2 = 27\). The dual estimate is \(27/18 = 3/2\). The reduced costs are \((1 - 3/2,\ 2 - 3/2) = (-1/2,\ 1/2)\). The direction is \(-9\) times that vector, which is \((9/2,\ -9/2)\).

The ferry coordinate is 4.5. The second component is negative, so the blocking step is \(3 / (9/2) = 2/3\). Half of that step has length \(1/3\). The new point is \((3,\ 3) + (1/3)(9/2,\ -9/2) = (4.5,\ 1.5)\). It stays on the line \(x_1 + x_2 = 6\), and both coordinates stay positive. Subtracting the direction would have moved toward the more expensive vertex.""",
            r"""The direction is added. Subtracting it follows the reduced costs uphill. A second slip is to take the fraction equal to one and then form a new diagonal. A zero coordinate makes \(X^{-2}\) undefined. A third is to forget the dual estimate and step along \(-c\). That vector need not satisfy \(A d = 0\), so the next point leaves the affine set. A fourth is to treat the method as a simplex pivot. No basis is chosen, and the point does not sit at a vertex. Scaling by \(X\) instead of \(X^2\) is a fifth slip. The metric is \(X^{-2}\), so the normal equation uses the square.""",
            r"""Putting a positive target back into the complementarity products, and linearizing the whole perturbed system by Newton, is a primal-dual interior-point step. Affine scaling corresponds to the pure predictor direction in which that target is zero and only the primal scaling is visible. The interior-point step keeps a positive target, moves the slacks as well as \(x\), and shortens the Newton step so both stay positive.""",
            SEG,
            A_SEG,
        ),
    )


def expl_pd():
    save_explainer(
        "primal-dual-interior-point",
        "Primal-dual interior-point methods",
        _sec(
            r"""A primal-dual interior-point step solves a smoothed version of the KKT system, then lets the smoothing shrink. For a standard-form linear program the unsmoothed system asks for primal feasibility, dual feasibility, nonnegative \(x\) and \(s\), and complementary products \(x_i s_i = 0\). The smoothed system keeps the two feasibility equations and replaces the products by \(x_i s_i = \mu\) with a positive target, while \(x\) and \(s\) stay positive.

As the target varies, the solutions form the central path. On the path the duality gap \(x^T s\) equals \(n \mu\). Driving the target to zero drives the gap to zero. The quantity under control is the gap, not the distance to a vertex.

The products make the map nonlinear. One iteration linearizes it by Newton at a positive point, for a chosen target, then shortens the step so the updated \(x\) and \(s\) stay positive.

A short-step path follower reduces the duality gap to a fraction \(\varepsilon\) of its initial value in a number of Newton steps on the order of \(\sqrt{n}\) times a logarithm of \(1/\varepsilon\). That count is about the gap. Affine scaling drops the target to zero. A positive target is what pulls the point back toward the central path.""",
            r"""The perturbed system is
\[
A x = b, \qquad A^T y + s = c, \qquad x_i s_i = \mu,
\]
with \(x > 0\), \(s > 0\), and \(\mu > 0\). The gap on the path is \(x^T s = n \mu\). The step is shortened so the next point stays positive.""",
            r"""Take \(x = (4,\ 1)\), \(s = (4,\ 1)\), \(y = 0\), and a cost equal to the slack, so the primal sum is \(5\) and both feasibility residuals are zero. The products are \(16\) and \(1\). Choose the target \(4\), the product of the two primal coordinates. The Newton step that equalizes the products leaves the slacks and the multiplier alone and sends the primal step to \((-3,\ 3)\).

The new primal vector is \((1,\ 4)\). Both products equal \(4\), and the old gap was \(17\).

The gate gap is 8. The new gap is \(1 \cdot 4 + 4 \cdot 1 = 8\), which is \(2 \cdot 4\). Adding the opposite step lands at \((7,\ -2)\), outside the positive orthant. The quantity that moved from \(20\) to \(8\) is the gap.""",
            r"""A sign error in the Newton update is the usual arithmetic slip: the step is added to the current point. Adding its opposite leaves the positive orthant and undoes the linearization. A second slip is to quote \(n \mu\) as a distance to the optimum. It is the duality gap on the central path. A third is to set the target to zero on every step and still call the result a centering iteration. A zero target is the predictor direction. A fourth is to forget to shorten the step. The linear equations can survive a long step while positivity does not. Every coordinate product has to match the target.""",
            r"""Conditional gradient is a different first-order method on a compact convex set. It never forms this perturbed system. It minimizes a linear model and walks toward a vertex, and its guarantee is a function-gap bound of order \(1/k\). The interior-point count above is a bound on the number of Newton steps that shrink a duality gap. The two statements measure different things, on different problems.""",
            MAT,
            A_MAT,
        ),
    )


def expl_fw():
    save_explainer(
        "frank-wolfe-conditional-gradient",
        "Conditional gradient (Frank-Wolfe) method",
        _sec(
            r"""Conditional gradient, also called Frank-Wolfe, never projects onto the set. It asks a different subproblem: minimize the linear model built from the current gradient. On a polytope the minimum is attained at a vertex, so the subproblem is a linear minimization oracle. The next point is a convex combination of the current point and that vertex. Convexity of the set keeps the combination feasible.

On the probability simplex the vertices are the standard-basis vectors, and the linear value at a vertex is one gradient component. The oracle returns a vertex of a smallest component. If several components tie, any convex combination of those vertices is also a minimizer. On the \(\ell_1\) ball the vertices are the signed basis vectors. The oracle picks a coordinate of largest gradient magnitude and the sign opposite the gradient.

The fraction in the convex combination can be chosen by an exact line search along the segment, or by the open-loop schedule \(2/(k+2)\) with \(k\) counting from zero. The first fraction equals \(1\), a full step to the oracle's answer. Later fractions decrease toward zero and never exceed \(1\).

For a smooth convex objective on a compact convex set, that schedule yields a bound of order \(1/k\) on the function gap. With a curvature constant \(C_f\) the gap is at most \(2 C_f / (k + 2)\). The curvature constant is finite when the gradient is Lipschitz and the set is bounded. The inequality bounds \(f(x_k) - f^\star\), not the distance from \(x_k\) to a minimizer.""",
            r"""The oracle and the update are
\[
s \in \arg\min_{u \in \mathcal{X}} \nabla f(x)^T u, \qquad x_+ = (1 - \gamma) x + \gamma s.
\]
The schedule \(\gamma_k = 2/(k+2)\) gives \(f(x_k) - f^\star \le 2 C_f / (k + 2)\). On the simplex, \(s\) is a basis vector at a smallest gradient component.""",
            r"""On the simplex, start at \((1/5,\ 4/5)\) with gradient \((5,\ -1)\) and fraction \(2/5\). The smaller component is \(-1\), so the oracle returns \((0,\ 1)\). The new point is \(\tfrac35\) of the current point plus \(\tfrac25\) of the oracle point.

The kite weight is 0.4. The new second coordinate is \(\tfrac35 \cdot 4/5 + \tfrac25 = 22/25\). The new first coordinate is \(\tfrac35 \cdot 1/5 = 3/25\). Choosing the larger gradient component would have maximized the linear model.

The fraction \(2/5\) is not the value of \(2/(k+2)\) at \(k = 0\), which is \(1\). The decreasing schedule bounds the function gap.""",
            r"""Selecting the largest gradient component maximizes the linear model. The oracle minimizes it. A second slip is to describe the \(O(1/k)\) result as a bound on \(\lVert x_k - x^\star\rVert\). The inequality bounds the function gap. A third is to project the gradient step and call the result a conditional-gradient step. The subproblem here is linear, not a nearest-point problem. A fourth is to take a fraction larger than \(1\). The combination would leave the segment and can leave the set. A tie for the smallest component makes the whole minimizing face optimal, not a single vertex.""",
            r"""The same linear oracle on the unit sphere, for the objective \(x^T A x\), returns the normalization of \(A x\). That is one step of the power method. The quantity that contracts is the second-mode coefficient, by the factor \(|\lambda_2 / \lambda_1|\). The Rayleigh quotient's error uses the square of that factor. Those are eigenvector and eigenvalue measures, not the function-gap bound of this section.""",
            SIMP,
            A_SIMP,
        ),
    )


def expl_power():
    save_explainer(
        "power-method-eigenvector",
        "Power method for the top eigenvector",
        _sec(
            r"""The power method finds a dominant eigenvector of a symmetric matrix by repeating one multiplication. Start with a nonzero vector that is not orthogonal to the top eigenvector, multiply by the matrix, and divide by the Euclidean length. The same normalization is what the conditional-gradient oracle returns for the objective \(x^T A x\) on the unit sphere: the gradient points along \(A x\), and the linear maximizer on the sphere is the normalization of \(A x\).

Write the start in an orthonormal eigenbasis. Multiplication by \(A\) multiplies the coefficient of each eigenvector by its eigenvalue. Dividing by the length does not change the ratios of those coefficients. If the top eigenvalue is strictly larger in magnitude than the second, the top coefficient pulls ahead. The ratio of the second coefficient to the first is multiplied by \(|\lambda_2 / \lambda_1|\) at every step. That factor governs the angle between the iterate and the top eigenvector.

The Rayleigh quotient is a different error. On a unit vector the weight on a stray mode is the square of that mode's coefficient, so the gap from \(\lambda_1\) scales with the square of \(|\lambda_2 / \lambda_1|\). Quoting the unsquared factor as a Rayleigh error mixes the two measures.

A start orthogonal to the top eigenvector never grows that component. Applying the same iteration to \(A^T A\) approaches a top right singular vector of \(A\).""",
            r"""One step is
\[
x_+ = \frac{A x}{\lVert A x\rVert}.
\]
If \(|\lambda_1| > |\lambda_2|\), the second-mode coefficient is multiplied by \(|\lambda_2 / \lambda_1|\) at each step. The Rayleigh gap from \(\lambda_1\) scales with the square of that factor. The Rayleigh quotient itself is \(x^T A x / x^T x\).""",
            r"""Take \(A = \mathrm{diag}(8,\ 2)\) and the start \((1,\ 1)\). One multiplication produces \((8,\ 2)\). The ratio of the second component to the first falls from \(1\) to \(2/8\).

The mast ratio is 0.25, which is \(|\lambda_2 / \lambda_1| = 2/8\). A second multiplication produces \((64,\ 4)\), and the component ratio is \(1/16\). The Rayleigh gap of a tiny second component \(\varepsilon\) moves like \(\varepsilon^2\), so one step multiplies that gap by \((1/4)^2\).

The quotient of \((8,\ 2)\) is \(520/68\), strictly below the top eigenvalue \(8\). The component ratio \(0.25\) is not that gap.""",
            r"""The factor \(|\lambda_2 / \lambda_1|\) multiplies a mode coefficient and governs an angle. Using it, unsquared, as the Rayleigh error overstates how fast the eigenvalue estimate improves, because the quotient sees the square. A second slip is to invert the factor. \(|\lambda_1 / \lambda_2|\) is larger than one and would describe a growing component. A third is to start in the lower eigenspace and expect the top direction to appear. Multiplication cannot create a missing component. One step is not an exact eigenvector unless the start was already aligned. The contraction is geometric.""",
            r"""Power iteration on \(A^T A\) is the same algorithm pointed at a top right singular vector. The angle contracts by the ratio of the two largest eigenvalues of that product, the squares of the two largest singular values. The Rayleigh quotient of \(A^T A\) estimates a squared singular value and converges with the square of the angle factor.""",
            ARR,
            A_ARR,
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
    "optimality-over-convex-set": "The anchor value is 12",
    "projection-onto-convex-set": "The peg coordinate is 4",
    "gradient-projection-method": "The latch point is 3",
    "scaled-gradient-projection": "The wedge coordinate is 3",
    "affine-scaling-method": "The ferry coordinate is 4.5",
    "primal-dual-interior-point": "The gate gap is 8",
    "frank-wolfe-conditional-gradient": "The kite weight is 0.4",
    "power-method-eigenvector": "The mast ratio is 0.25",
}

LEAKS = {
    "optimality-over-convex-set": ["(t - 5)", "(t - 1)^2", "-t^2", "(y - 4)", "1/5"],
    "projection-onto-convex-set": ["(-1,\\ 5)", "(6,\\ 8)", "diag(4,\\ 1)", "(4,\\ 1)"],
    "gradient-projection-method": ["(x - 4)^2", "3x^2", "(3,\\ 1)", "k = 4"],
    "scaled-gradient-projection": ["diag(2,\\ 4)", "(3/2) x^2", "2x^2 - 2x", "6/4"],
    "affine-scaling-method": ["(2,\\ 2)", "(4,\\ -4)", "(4,\\ 2)", "x_1 + 3 x_2"],
    "primal-dual-interior-point": ["\\mu = 8", "(5,\\ -1)", "n = 5"],
    "frank-wolfe-conditional-gradient": ["k = 6", "(1/2,\\ 1/2)", "(3,\\ -6,\\ 1)", "(4,\\ -1)"],
    "power-method-eigenvector": ["diag(5,\\ 1)", "diag(6,\\ 2)", "14/5", "1/27"],
}


def main():
    _balance_mc()
    bank_opt()
    bank_proj()
    bank_gp()
    bank_scaled()
    bank_affine()
    bank_pd()
    bank_fw()
    bank_power()
    expl_opt()
    expl_proj()
    expl_gp()
    expl_scaled()
    expl_affine()
    expl_pd()
    expl_fw()
    expl_power()
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
