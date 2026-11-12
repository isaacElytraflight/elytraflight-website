#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB11 banks and explainers.

Skills: gram-schmidt-orthogonalization, q-conjugate-directions,
conjugate-gradient-method, heavy-ball-method, nesterov-accelerated-gradient.

Closed-form answers live here. skilltree/verify_nlo_nb11.py recomputes the
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
    level_curves_fig,
    mass_spring,
    matrix_fig,
    plane_vectors,
    plot,
    segment_fig,
)

FALL = plot(lambda t: 1.55 - 0.42 * t, 0.0, 2.6, "t", "z", "a line sloping down")
A_FALL = "A straight line sloping downward on labeled axes."
RISE = plot(lambda t: 0.35 * t + 0.45, 0.0, 2.6, "t", "z", "a line sloping up")
A_RISE = "A straight line sloping upward on labeled axes."
DECAY = plot(lambda t: 1.7 * (0.62 ** t), 0.0, 5.5, "k", "e", "a falling curve")
A_DECAY = "A curve that falls toward the horizontal axis."
SLOW = plot(lambda t: 1.55 / (1.0 + 0.18 * t * t), 0.0, 5.5, "k", "gap", "a curve that flattens")
A_SLOW = "A curve that drops at first and then flattens."
ELL = ellipse_axes("a long ellipse")
A_ELL = "An axis-aligned ellipse, longer along the first axis."
LEV = level_curves_fig("nested contours")
A_LEV = "Three nested ellipses around the origin."
SEG = segment_fig("a segment")
A_SEG = "A solid segment joins two marked points on a dashed line."
ARR = plane_vectors([(1.15, 0.35, "v")], "one arrow from the origin")
A_ARR = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.05, 0.2, "u"), (0.35, 1.05, "v")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."
ORTH = plane_vectors([(1.2, 0.15, "u"), (0.15, 1.05, "w")], "two arrows at a wide angle")
A_ORTH = "Two arrows leave the origin in different directions."
MAT = matrix_fig([["p", "0"], ["0", "q"]], "a diagonal array")
A_MAT = "A two-by-two array with labels on the diagonal."
COL = matrix_fig([["a"], ["b"]], "a column of two labels")
A_COL = "A column of two labels."
MASS = mass_spring("a mass with a spring and a damper")
A_MASS = "A mass connected to a spring and a damper, with a force arrow."

P_Q = ["q-conjugate-directions"]
P_CG = ["conjugate-gradient-method"]
P_HB = ["heavy-ball-method"]
P_NE = ["nesterov-accelerated-gradient"]
P_GP = ["gradient-projection-method"]
P_FW = ["frank-wolfe-conditional-gradient"]


def bank_gs():
    b = Bank("gram-schmidt-orthogonalization")
    b.mc(
        1,
        r"One Gram-Schmidt step, after some orthogonal vectors have already been accepted, does which of the following?",
        [
            r"Subtract from the new vector its projections onto the orthogonal vectors already accepted.",
            r"Replace the new vector by the sum of the vectors already accepted.",
            r"Divide every coordinate of the new vector by the same constant and stop.",
            r"Swap two coordinates of the new vector so that the dot product changes sign.",
        ],
        0,
        r"The coefficient of an accepted vector \(u\) is the inner product of the new vector with \(u\), divided by the squared length of \(u\). Subtracting those multiples leaves a vector orthogonal to every accepted \(u\). Adding the accepted vectors builds a sum, not a remainder. Dividing by one constant rescales the new vector and does not cancel a projection. Swapping coordinates is not the projection formula.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        1,
        r"Using the dot product, orthogonalize \((3,\ 1)\) against the already accepted vector \((1,\ 2)\). What is the first component of the result?",
        2,
        "1",
        r"The inner product is \(3\cdot 1 + 1\cdot 2 = 5\), and the squared length of \((1,\ 2)\) is \(1 + 4 = 5\). The coefficient is \(5/5 = 1\). The result is \((3,\ 1) - 1\cdot(1,\ 2) = (2,\ -1)\). The first component is \(2\). Reporting \(-1\) is the second component. Reporting \(1\) is the coefficient, not a component of the remainder. Reporting \(5\) is the inner product before the division.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        1,
        r"For a symmetric matrix \(Q\), the product \(x^T Q y\) is an inner product on \(\mathbb{R}^n\) when",
        [
            r"\(Q\) is positive definite, so \(x^T Q x > 0\) for every \(x \ne 0\)",
            r"\(Q\) is symmetric, including when some eigenvalue is negative",
            r"\(Q\) is singular, so at least one vector has squared length zero",
            r"\(Q\) has a negative trace, regardless of its eigenvalues",
        ],
        0,
        r"Symmetry makes \(x^T Q y\) symmetric and bilinear. Positive definiteness makes the squared length positive for every nonzero vector, which is the remaining inner-product axiom. A negative eigenvalue makes some squared length negative, so the product is not an inner product. A singular \(Q\) gives a nonzero vector with squared length zero. The trace is the sum of the eigenvalues and does not replace the sign test on each of them.",
        fig=MAT,
        alt=A_MAT,
    )
    b.order(
        2,
        r"Put these steps in the order that orthogonalizes a second vector against a first one. Each step uses the result of the step before it.",
        [
            r"Keep the first input vector as the first orthogonal vector.",
            r"Using that orthogonal vector, compute its inner product with the next input and its own squared length.",
            r"Divide that inner product by that squared length, and subtract the resulting multiple of the orthogonal vector from the next input.",
            r"Keep that difference as the next orthogonal vector.",
        ],
        r"The inner product and the squared length are taken with the vector that was kept, so that vector has to be chosen first. The coefficient is their quotient, so both numbers have to exist before the subtraction. The difference is defined by that subtraction, so it cannot be kept before the subtraction is formed. Projecting onto the original second input, instead of onto the vector already kept, is a different calculation and is not a swap of these steps.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which of these pairs are orthogonal in the dot product?",
        [
            r"\((1,\ -2)\) and \((4,\ 2)\)",
            r"\((2,\ 3)\) and \((3,\ -2)\)",
            r"\((1,\ 1)\) and \((2,\ -1)\)",
            r"\((0,\ 5)\) and \((3,\ 0)\)",
            r"\((2,\ 2)\) and \((1,\ 1)\)",
        ],
        [0, 1, 3],
        r"Orthogonality is a zero dot product."
        "\n"
        r"• \((1,\ -2)\cdot(4,\ 2) = 4 - 4 = 0\)."
        "\n"
        r"• \((2,\ 3)\cdot(3,\ -2) = 6 - 6 = 0\)."
        "\n"
        r"• \((1,\ 1)\cdot(2,\ -1) = 2 - 1 = 1\)."
        "\n"
        r"• \((0,\ 5)\cdot(3,\ 0) = 0\)."
        "\n"
        r"• \((2,\ 2)\cdot(1,\ 1) = 4\)."
        "\n"
        r"The third and fifth pairs are not orthogonal.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.sym(
        2,
        r"In the dot product, the accepted vector is \((a,\ b)\) and the next input is \((c,\ d)\). The coefficient of \((a,\ b)\) that is subtracted equals",
        "(a*c+b*d)/(a*a+b*b)",
        {"a": (1, 3), "b": (1, 3), "c": (-2, 2), "d": (-2, 2)},
        r"The coefficient is the inner product \(ac + bd\) divided by the squared length \(a^2 + b^2\). Every declared name appears. Subtracting the inner product without the division is the mistake of treating \((a,\ b)\) as a unit vector. Adding the squared length in the numerator, as in \((ac + bd + a^2 + b^2)/(a^2 + b^2)\), mixes the coefficient with \(1\). The product \(ac + bd\) alone is the inner product, not the coefficient.",
        alternates=["(a*c+b*d)/(a^2+b^2)", "(c*a+d*b)/(a*a+b*b)"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note orthogonalizes \((6,\ 4)\) against \((2,\ 0)\) in the dot product. Exactly one step is a false claim.",
        [
            r"The accepted vector is \((2,\ 0)\).",
            r"The inner product of \((6,\ 4)\) with \((2,\ 0)\) is \(12\), and the squared length of \((2,\ 0)\) is \(4\).",
            r"The coefficient is \(12/4 = 3\).",
            r"The orthogonal result is \((6,\ 4) - 3\cdot(2,\ 0) = (6,\ 4)\).",
        ],
        3,
        r"The accepted vector is the one already kept, \((2,\ 0)\). The inner product is \(12 + 0 = 12\), and the squared length is \(4\). The coefficient is \(3\). Subtracting does change the vector: \(3\cdot(2,\ 0) = (6,\ 0)\), and \((6,\ 4) - (6,\ 0) = (0,\ 4)\). The last step writes the original input again, which is what you get if the subtraction is skipped. The dot product of \((2,\ 0)\) with \((6,\ 4)\) is \(12\), not \(0\).",
        [
            r"The subtraction was skipped: \((6,\ 4) - 3\cdot(2,\ 0)\) equals \((0,\ 4)\), not \((6,\ 4)\).",
            r"The inner product of \((6,\ 4)\) and \((2,\ 0)\) is not \(12\).",
            r"The quotient \(12/4\) is not \(3\).",
        ],
        0,
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        3,
        r"Let the inner product be \(x^T Q y\) with \(Q = \mathrm{diag}(4,\ 1)\). Orthogonalize \((2,\ 5)\) against \((1,\ 0)\). What is the second component of the result?",
        5,
        "1",
        r"\(Q(1,\ 0) = (4,\ 0)\), so the inner product is \((2,\ 5)\cdot(4,\ 0) = 8\). The squared length of \((1,\ 0)\) is \(4\). The coefficient is \(2\). The result is \((2,\ 5) - 2\cdot(1,\ 0) = (0,\ 5)\). The second component is \(5\). Reporting \(0\) is the first component, and a zero answer is not this component. Reporting \(2\) is the coefficient. Reporting \(8\) is the inner product. The second row of \(Q\) never enters this subtraction, because the accepted vector has a zero there.",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        3,
        r"If the input list is linearly dependent, Gram-Schmidt",
        [
            r"produces a zero remainder at the dependent vector, so that remainder is not a new direction",
            r"still produces one nonzero orthogonal vector per input vector",
            r"makes the inner product fail to be bilinear",
            r"replaces the first vector by zero and keeps the later ones",
        ],
        0,
        r"A vector in the span of those already accepted has inner products that reproduce it exactly, so the remainder is zero. A zero vector cannot be used as a later direction, and it cannot be normalized. Dependence does not create extra nonzero vectors. The inner product is unchanged by which list you feed it. The first vector of an independent prefix stays as it is. The zero appears at the dependent position.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        4,
        r"Running Gram-Schmidt in the inner product \(x^T Q y\), with \(Q\) symmetric positive definite, produces vectors that satisfy",
        [
            r"\(d_i^T Q d_j = 0\) for \(i \ne j\), which is \(Q\)-conjugacy",
            r"\(d_i^T d_j = 0\) for \(i \ne j\), for every positive definite \(Q\)",
            r"\(d_i^T Q d_j = 1\) for \(i \ne j\)",
            r"\(Q d_i = d_i\), so every result is an eigenvector of eigenvalue \(1\)",
        ],
        0,
        r"The algorithm enforces orthogonality in the inner product it was given. For \(x^T Q y\) that statement is \(d_i^T Q d_j = 0\). Euclidean orthogonality is the special case \(Q = I\). A positive definite \(Q\) that stretches one axis leaves the Euclidean dot product of the results nonzero in general. The products are zero, not \(1\). Nothing in the subtraction forces \(Q d_i = d_i\).",
        fig=ELL,
        alt=A_ELL,
        preview=P_Q,
    )
    b.num(
        4,
        r"In the dot product, the orthogonal vectors already accepted are \(u_1 = (1,\ 0,\ 0)\) and \(u_2 = (0,\ 1,\ 0)\). For the new input \((2,\ 3,\ 4)\), what is the coefficient of \(u_2\)?",
        3,
        "1",
        r"The coefficient of \(u_2\) is the dot product \((2,\ 3,\ 4)\cdot(0,\ 1,\ 0) = 3\), divided by \(\lVert u_2\rVert^2 = 1\), so it equals \(3\). The coefficient of \(u_1\) is \(2\), and the remainder is \((0,\ 0,\ 4)\). Reporting \(2\) uses \(u_1\). Reporting \(4\) is the third component of the remainder, not the coefficient of \(u_2\). Reporting \(1\) is the squared length of \(u_2\).",
        fig=COL,
        alt=A_COL,
        preview=P_Q,
    )
    b.mc(
        4,
        r"After a \(Q\)-orthogonal list has been built, scaling one vector by a nonzero constant",
        [
            r"preserves \(d_i^T Q d_j = 0\), so the list stays \(Q\)-conjugate",
            r"destroys conjugacy, because the product scales by that constant",
            r"forces every later conjugate-gradient direction to equal the negative gradient",
            r"replaces \(Q\) by \(Q\) times that constant",
        ],
        0,
        r"If \(d_i^T Q d_j = 0\), then \((c d_i)^T Q d_j = c\cdot 0 = 0\). Conjugacy is unchanged. The exact step length along the scaled direction changes, and the displacement, length times direction, does not. Scaling does not set later coefficients to zero, and it does not alter \(Q\). A conjugate-gradient iteration still has to build its directions. It inherits the conjugacy relation, not a command to ignore previous directions.",
        fig=LEV,
        alt=A_LEV,
        preview=P_CG,
    )
    b.save()


def bank_cd():
    b = Bank("q-conjugate-directions")
    b.mc(
        1,
        r"Two directions are \(Q\)-conjugate when",
        [
            r"\(d_1^T Q d_2 = 0\), with \(Q\) the symmetric positive definite Hessian",
            r"\(d_1^T d_2 = 0\), for every symmetric positive definite \(Q\)",
            r"\(d_1 + d_2 = 0\), so the directions are opposites",
            r"\(Q d_1 = Q d_2\), so the directions have the same image",
        ],
        0,
        r"Conjugacy is orthogonality in the inner product \(x^T Q y\). The Euclidean condition \(d_1^T d_2 = 0\) agrees with it for every direction pair only when \(Q\) is a multiple of the identity. Opposite directions have product \(-d_1^T Q d_1\), which is negative, not zero. Equal images do not make the product \(d_1^T Q d_2\) zero.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        1,
        r"Let \(Q = \mathrm{diag}(3,\ 1)\), \(d_1 = (1,\ 1)\), and \(d_2 = (1,\ 2)\). What is \(d_1^T Q d_2\)?",
        5,
        "1",
        r"\(Q d_2 = (3,\ 2)\), so the product is \(1\cdot 3 + 1\cdot 2 = 5\). The directions are not \(Q\)-conjugate. Reporting \(0\) would be conjugacy, and this pair does not have it. Reporting \(3\) keeps only the first term. Reporting \(2\) keeps only the second. Reporting \(4\) is \(1\cdot 3 + 1\cdot 1\), which replaces the second component of \(d_2\) by \(1\).",
        fig=MAT,
        alt=A_MAT,
    )
    b.mc(
        1,
        r"On a positive definite quadratic in \(n\) variables, exact line search along \(n\) \(Q\)-conjugate directions",
        [
            r"reaches the minimizer in at most \(n\) steps, from any start",
            r"reaches the minimizer only when the directions are also Euclidean-orthogonal",
            r"needs a further \(n\) steps, because each direction is used twice",
            r"stops after one step, because the first exact search already zeros the gradient",
        ],
        0,
        r"The error before the run can be expanded in the conjugate directions. The exact step on one direction cancels that direction's coefficient, and conjugacy keeps later steps from restoring it. After every coefficient is gone, the error is zero. Euclidean orthogonality is not required. Each direction is used once. The first search zeros the gradient along that one direction, not in the whole space, unless \(n = 1\).",
        fig=ELL,
        alt=A_ELL,
    )
    b.order(
        2,
        r"Put these steps of one conjugate-direction iteration in order. The directions are already built. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient at the current point.",
            r"Using that gradient, form the numerator as its negative dot product with the next conjugate direction, and form the denominator as that direction's curvature \(d^T Q d\).",
            r"Divide that numerator by that denominator to obtain the step length.",
            r"Add that step length times the direction to the current point.",
        ],
        r"The numerator contains the gradient, so the gradient is computed first. The step length is the quotient of the two quantities formed from that gradient and from the direction, so it comes after both exist. The point moves by the length times the direction, which cannot be formed before the length. Computing the curvature before the gradient would split the second step. The written numerator still needs the gradient, so that split is not an alternative order of these four steps.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Let \(Q = \mathrm{diag}(2,\ 8)\). Which pairs are \(Q\)-conjugate?",
        [
            r"\((4,\ 1)\) and \((2,\ -1)\)",
            r"\((1,\ 1)\) and \((4,\ -1)\)",
            r"\((2,\ 0)\) and \((0,\ 3)\)",
            r"\((1,\ 2)\) and \((4,\ 1)\)",
            r"\((1,\ -1)\) and \((8,\ 2)\)",
        ],
        [1, 2, 4],
        r"The product is the first components times \(2\), plus the second components times \(8\)."
        "\n"
        r"• \((4,\ 1)\) and \((2,\ -1)\): \(2\cdot 4\cdot 2 + 8\cdot 1\cdot(-1) = 16 - 8 = 8\)."
        "\n"
        r"• \((1,\ 1)\) and \((4,\ -1)\): \(2\cdot 1\cdot 4 + 8\cdot 1\cdot(-1) = 8 - 8 = 0\)."
        "\n"
        r"• \((2,\ 0)\) and \((0,\ 3)\): both terms are \(0\)."
        "\n"
        r"• \((1,\ 2)\) and \((4,\ 1)\): \(2\cdot 1\cdot 4 + 8\cdot 2\cdot 1 = 8 + 16 = 24\)."
        "\n"
        r"• \((1,\ -1)\) and \((8,\ 2)\): \(2\cdot 1\cdot 8 + 8\cdot(-1)\cdot 2 = 16 - 16 = 0\)."
        "\n"
        r"The first and fourth pairs are not conjugate.",
        fig=MAT,
        alt=A_MAT,
    )
    b.sym(
        2,
        r"The Hessian is diagonal with positive entries \(a\) and \(b\). The gradient is \((g,\ h)\) and the direction is \((u,\ v)\). The exact line-search step length equals",
        "-(g*u+h*v)/(a*u*u+b*v*v)",
        {"a": (1, 3), "b": (1, 3), "u": (1, 3), "v": (1, 3), "g": (-2, 2), "h": (-2, 2)},
        r"The step length is the negative directional derivative divided by the curvature. The directional derivative is \(gu + hv\). The curvature is \(a u^2 + b v^2\), because \(Q\) is diagonal. Every declared name appears. Dropping the leading minus sign walks the wrong way along a descent direction. Dividing by \(u^2 + v^2\) replaces the Hessian by the identity. Using \(g\) and \(h\) in the denominator, as in \(-(gu+hv)/(g^2+h^2)\), is a steepest-descent length written on the wrong vectors.",
        alternates=["-(g*u+h*v)/(a*u^2+b*v^2)", "(-g*u-h*v)/(a*u*u+b*v*v)"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note claims that two directions are \(Q\)-conjugate. Exactly one step is a false claim.",
        [
            r"\(Q\) is diagonal with entries \(4\) and \(1\).",
            r"The directions are \((1,\ 2)\) and \((1,\ -1)\).",
            r"Their product is \(4\cdot 1\cdot 1 + 1\cdot 2\cdot(-1) = 2\).",
            r"Because that product equals \(2\), the directions are \(Q\)-conjugate.",
        ],
        3,
        r"The diagonal entries are \(4\) and \(1\), and the directions are the ones stated. The product expands to \(4 - 2 = 2\). Conjugacy requires the product to be \(0\). A product of \(2\) is evidence against conjugacy, not for it. The second term would need to be \(-4\), not \(-2\), before this particular first term cancelled, and that would be a different second component.",
        [
            r"\(Q\)-conjugacy requires the product to be \(0\). A product of \(2\) means the directions are not conjugate.",
            r"The expansion \(4\cdot 1\cdot 1 + 1\cdot 2\cdot(-1)\) is not \(2\).",
            r"\(Q\) is not diagonal with entries \(4\) and \(1\).",
        ],
        0,
        fig=ORTH,
        alt=A_ORTH,
    )
    b.num(
        3,
        r"Let \(Q = \mathrm{diag}(3,\ 1)\). At a point where the gradient is \((6,\ 4)\), the direction \(d = (-1,\ 1)\) is a descent direction. What is the exact step length?",
        0.5,
        "1",
        r"The directional derivative is \(6\cdot(-1) + 4\cdot 1 = -2\). The curvature is \(d^T Q d = (-1,\ 1)\cdot(-3,\ 1) = 3 + 1 = 4\). The step length is \(-(-2)/4 = 1/2\). Reporting \(-1/2\) drops the minus in front of the directional derivative and walks uphill. Reporting \(2\) divides \(4\) by \(2\) in the wrong arrangement. Reporting \(4\) is the curvature.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        3,
        r"During conjugate-direction search, an exact step on direction \(d\) removes the component of the error along \(d\). A later conjugate direction does not put that component back because",
        [
            r"the cross term \(d^T Q d_{\mathrm{later}}\) is zero, so the later step does not change the coefficient of \(d\)",
            r"the later direction is a scalar multiple of \(d\)",
            r"the gradient is zero after the first step, so later steps have length zero",
            r"exact line search forces every direction to be the negative gradient",
        ],
        0,
        r"Expand the error in the conjugate basis. The function along one direction is a parabola in that coefficient alone, precisely because the cross terms vanish. The exact step sets that coefficient to zero, and a later direction, being conjugate, has no cross term with which to revive it. A later direction that is a multiple of \(d\) is not a new conjugate direction. The gradient after the first step is orthogonal to \(d\) and is otherwise free. Exact search does not change the given direction into the negative gradient.",
        fig=LEV,
        alt=A_LEV,
    )
    b.mc(
        4,
        r"The conjugate-gradient iteration differs from a conjugate-direction run that is handed its directions in advance because conjugate gradient",
        [
            r"builds each new direction from the latest gradient and the previous direction",
            r"replaces exact line search by a fixed step of length \(1\)",
            r"drops \(Q\)-conjugacy and keeps only Euclidean orthogonality",
            r"forms and factors the Hessian at every iteration",
        ],
        0,
        r"Conjugate gradient still takes an exact line search on a quadratic, and the coefficient in the direction update is chosen so the new direction is \(Q\)-conjugate to the previous one. The directions are not supplied as a separate list. They are generated from gradients. A fixed length of \(1\) is not the exact search. Euclidean orthogonality of successive gradients is a consequence, not a replacement for conjugacy. The iteration multiplies by \(Q\). It does not factor \(Q\).",
        fig=ARR,
        alt=A_ARR,
        preview=P_CG,
    )
    b.num(
        4,
        r"Let \(f(x) = \tfrac12 x^T Q x + b^T x\) with \(Q = \mathrm{diag}(2,\ 6)\) and \(b = (4,\ -6)\). Start at \((0,\ 0)\) and take an exact step along \(d = (-1,\ 0)\). What is the second component of the new gradient?",
        -6,
        "1",
        r"The gradient is \(Qx + b\), so at the origin it is \((4,\ -6)\). The directional derivative along \(d\) is \(-4\), and the curvature is \(2\), so the step length is \(2\). The new point is \((-2,\ 0)\). The new gradient is \(Q(-2,\ 0) + b = (-4,\ 0) + (4,\ -6) = (0,\ -6)\). The second component is \(-6\). Its dot product with \(d\) is \(0\), which is what the exact search enforces. Reporting \(0\) is the first component. Reporting \(-4\) is the first component of \(Q\) times the new point, before \(b\) is added. Reporting \(2\) is the step length.",
        fig=FALL,
        alt=A_FALL,
        preview=P_CG,
    )
    b.mc(
        4,
        r"Successive steepest-descent directions are Euclidean-orthogonal under exact line search. That fact becomes \(Q\)-conjugacy for every pair of such directions when",
        [
            r"\(Q\) is a positive multiple of the identity, and in that case one exact steepest step already finishes",
            r"\(Q\) is any positive definite matrix, because orthogonality never involves \(Q\)",
            r"the condition number is large, because a long ellipse makes right angles into conjugacy",
            r"the step length is \(1\), regardless of \(Q\)",
        ],
        0,
        r"Conjugacy is \(d_i^T Q d_j = 0\). Euclidean orthogonality is \(d_i^T d_j = 0\). These agree for all pairs when \(Q\) is a multiple of the identity. In that case the level sets are spheres and one exact steepest step reaches the center, so there is no second direction. A general positive definite \(Q\) inserts itself into the product and the two conditions split. A large condition number makes the zigzag worse. It does not turn a Euclidean right angle into conjugacy. The step length is not what inserts \(Q\).",
        fig=ELL,
        alt=A_ELL,
        preview=P_CG,
    )
    b.save()


def bank_cg():
    b = Bank("conjugate-gradient-method")
    b.mc(
        1,
        r"On a quadratic, the conjugate-gradient direction is",
        [
            r"the negative gradient on the first iteration, and thereafter the negative gradient plus a multiple of the previous direction",
            r"always the negative gradient, with the multiple forced to zero",
            r"the Newton step, requiring the Hessian to be factored",
            r"a fixed vector chosen before the first gradient is evaluated",
        ],
        0,
        r"The first direction has no previous direction to add, so it is the negative gradient. Each later direction is \(-\nabla f + \beta d_{\mathrm{prev}}\), and \(\beta\) is chosen so the new direction is \(Q\)-conjugate to the previous one. Forcing \(\beta = 0\) forever is steepest descent. The Newton step solves a linear system with the Hessian. The direction is recomputed from the gradient. It is not frozen in advance.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"The previous gradient is \((3,\ 0)\) and the new gradient is \((0,\ 2)\). The squared-norm formula gives \(\beta\) as the new squared length divided by the old squared length. What is \(\beta\)?",
        4 / 9,
        "1",
        r"The new squared length is \(0 + 4 = 4\). The old squared length is \(9 + 0 = 9\). The ratio is \(4/9\). Reporting \(9/4\) inverts the ratio. Reporting \(2/3\) divides the lengths instead of the squared lengths. Reporting \(4\) forgets the division by \(9\). The two gradients are orthogonal, which is what this iteration produces, and that fact is not itself the value of \(\beta\).",
        fig=COL,
        alt=A_COL,
    )
    b.mc(
        1,
        r"In exact arithmetic, conjugate gradient on a positive definite quadratic of dimension \(n\)",
        [
            r"reaches the minimizer in at most \(n\) iterations, with one multiplication by \(Q\) per iteration",
            r"reaches the minimizer in one iteration, for every \(n\)",
            r"needs a matrix factorization whose cost grows like \(n^3\) at every iteration",
            r"can require more than \(n\) iterations even when every product is exact",
        ],
        0,
        r"Each iteration adds one new conjugate direction, and \(n\) conjugate directions with exact line search finish the quadratic. The work in an iteration is the product of \(Q\) with a vector, plus a few vector updates. One iteration finishes only the one-dimensional case. A factorization is what this recursion avoids. Past \(n\) steps there is no new conjugate direction left. In exact arithmetic the gradient is already zero.",
        fig=MAT,
        alt=A_MAT,
    )
    b.order(
        2,
        r"Put these steps of one later conjugate-gradient iteration in order. Each step uses the result of the step before it.",
        [
            r"Evaluate the gradient at the new point.",
            r"Divide the squared length of that new gradient by the squared length of the previous gradient. Call the quotient \(\beta\).",
            r"Using that \(\beta\), add \(\beta\) times the previous direction to the negative of the new gradient.",
            r"Using that new direction, take the exact line-search step and replace the current point.",
        ],
        r"The quotient uses the new gradient, so the gradient comes first. The direction update uses that quotient, so it comes after the division. The line search walks along the direction just built, so the point cannot move before the direction exists. There is no branch in this later iteration: the previous direction is already there, and the first-iteration shortcut that skips \(\beta\) is a different iteration.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which claims about conjugate gradient on a positive definite quadratic are true?",
        [
            r"The first direction equals the negative gradient.",
            r"Each later multiple is chosen so the new direction is \(Q\)-conjugate to the previous direction.",
            r"Every iteration factors the Hessian.",
            r"Exact arithmetic reaches the minimizer in at most \(n\) steps in dimension \(n\).",
            r"The multiple is zero at every iteration, so every direction is the negative gradient.",
        ],
        [0, 1, 3],
        r"The first direction has nothing to combine with, so it is \(-\nabla f\)."
        "\n"
        r"• The later update is \(-\nabla f + \beta d\), and \(\beta\) is the value that makes the \(Q\)-product with the previous direction vanish."
        "\n"
        r"• A factorization is not part of the iteration. The product with \(Q\) is."
        "\n"
        r"• At most \(n\) conjugate directions exist in an \(n\)-dimensional space, and exact search along all of them finishes a positive definite quadratic."
        "\n"
        r"• A zero multiple at every iteration would be steepest descent. The multiple is zero on the first iteration and is not required to stay zero.",
        fig=ELL,
        alt=A_ELL,
    )
    b.sym(
        2,
        r"The Hessian is diagonal with positive entries \(a\) and \(b\). The gradient is \((p,\ q)\), and the first direction is the negative gradient. The exact step length along that direction equals",
        "(p*p+q*q)/(a*p*p+b*q*q)",
        {"a": (1, 3), "b": (1, 3), "p": (1, 3), "q": (1, 3)},
        r"The direction is \((-p,\ -q)\). The numerator of the exact length is the negative of the directional derivative, which equals \(p^2 + q^2\). The curvature is \(a p^2 + b q^2\). Every declared name appears. The reciprocal \((a p^2 + b q^2)/(p^2 + q^2)\) inverts the length. Dropping \(a\) and \(b\), which leaves \(1\), treats the Hessian as the identity. Using \(p + q\) in place of the squared length drops the squares.",
        alternates=["(p^2+q^2)/(a*p^2+b*q^2)", "(p*p+q*q)/(a*p^2+b*q^2)"],
        fig=MAT,
        alt=A_MAT,
    )
    b.find_error(
        3,
        r"A note builds the next conjugate-gradient direction from gradients \((0,\ 6)\) and \((3,\ 0)\), whose previous direction was the negative of \((3,\ 0)\). Exactly one step is a false claim.",
        [
            r"The new gradient is \((0,\ 6)\) and the old gradient is \((3,\ 0)\).",
            r"The squared lengths are \(36\) and \(9\).",
            r"The squared-norm formula gives \(\beta = 36/9 = 4\).",
            r"The next direction is \(-(0,\ 6) + 4\cdot(3,\ 0) = (12,\ -6)\).",
        ],
        3,
        r"The gradients and the squared lengths are as stated, and \(36/9 = 4\). The direction update adds \(\beta\) times the previous direction, not \(\beta\) times the previous gradient. The previous direction is \((-3,\ 0)\). The next direction is \((0,\ -6) + 4\cdot(-3,\ 0) = (-12,\ -6)\). The displayed vector \((12,\ -6)\) is what the opposite sign in that slot produces. The arithmetic of \(-(0,\ 6) + 4\cdot(3,\ 0)\) really is \((12,\ -6)\). That vector is just not the direction.",
        [
            r"The update adds \(\beta\) times the previous direction. That direction is \((-3,\ 0)\), so the result is \((-12,\ -6)\), not \((12,\ -6)\).",
            r"The squared length of \((0,\ 6)\) is not \(36\).",
            r"\(36/9\) is not \(4\).",
        ],
        0,
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        3,
        r"The gradient is \((4,\ 2)\) and \(Q = \mathrm{diag}(1,\ 2)\). The first direction is the negative gradient. What is the exact step length?",
        20 / 24,
        "1",
        r"The squared gradient length is \(16 + 4 = 20\). The curvature of the negative gradient equals the curvature of the gradient, \( (4,\ 2)\cdot(4,\ 4) = 16 + 8 = 24 \). The length is \(20/24 = 5/6\). Reporting \(24/20\) inverts the quotient. Reporting \(20\) drops the curvature. Reporting \(1\) would be the length if \(Q\) were the identity and the same cancellation happened, which it does not: the second diagonal entry is \(2\), and that is why the curvature is \(24\) rather than \(20\).",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        3,
        r"The standard conjugate-gradient bound, for condition number \(\kappa\), says that the \(Q\)-norm of the error after \(k\) steps is at most",
        [
            r"\(2\big((\sqrt{\kappa}-1)/(\sqrt{\kappa}+1)\big)^k\) times the initial \(Q\)-norm error",
            r"\(((\kappa-1)/(\kappa+1))^2\) times the previous function gap, which is the steepest-descent guarantee",
            r"a constant times the square of the previous error, from any start",
            r"\(1/k\), as a bound on the distance to the minimizer for every smooth convex function",
        ],
        0,
        r"The conjugate-gradient factor uses the square root of \(\kappa\), and the quantity it multiplies is the \(Q\)-norm of the error. The leading \(2\) is part of that bound. The unsquared-root factor \(((\kappa-1)/(\kappa+1))^2\) is the steepest-descent bound on the function gap, a different claim. A constant times the squared error is the local Newton claim. A reciprocal of \(k\) is a sublinear pattern and is not this bound.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        4,
        r"The same direction update, used on a smooth objective that is not quadratic, is nonlinear conjugate gradient. What is lost?",
        [
            r"Finite termination in at most \(n\) steps. The conjugacy that proved it used a constant Hessian.",
            r"The ability to evaluate a gradient.",
            r"Every use of the previous direction, so the update collapses to the Newton step.",
            r"The step length, which must then be exactly \(1\).",
        ],
        0,
        r"The finite-termination argument expands the error in directions that are conjugate with respect to one fixed positive definite Hessian. A nonquadratic objective has a changing Hessian, so that expansion does not close after \(n\) steps. The gradient is still what the update uses. The previous direction is still added. The step length is still chosen by a line search. It is not frozen at \(1\). Restarts are a practical response to the lost termination, not a proof that termination remains.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_HB,
    )
    b.num(
        4,
        r"For condition number \(\kappa = 4\), the base \((\sqrt{\kappa}-1)/(\sqrt{\kappa}+1)\) in the conjugate-gradient error bound equals",
        (2 - 1) / (2 + 1),
        "1",
        r"\(\sqrt{4} = 2\), so the base is \((2-1)/(2+1) = 1/3\). Reporting \((4-1)/(4+1) = 4/5\) uses \(\kappa\) without the square root. That is the steepest-descent shape, not this one. Reporting \(1/9\) squares the base, which is the heavy-ball momentum coefficient for this condition number, not the conjugate-gradient base. Reporting \(2\) is \(\sqrt{\kappa}\). The leading \(2\) in the full bound is a multiplier in front of the power of this base. It is not the base.",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_NE,
    )
    b.mc(
        4,
        r"A momentum method that adds a fraction of the previous displacement, instead of building a \(Q\)-conjugate direction, is",
        [
            r"the heavy-ball update, which reads the gradient at the current point",
            r"a simplex pivot, which swaps one basic column",
            r"a Newton step, which solves the Hessian against the gradient",
            r"an exact line search that is required to stop at a conjugate direction",
        ],
        0,
        r"Heavy ball steps from the current point along the negative gradient and then adds a multiple of the previous displacement. It does not enforce \(d^T Q d_{\mathrm{prev}} = 0\). A simplex pivot changes a basis of a linear program. Newton uses the Hessian as a linear operator. Exact line search chooses a length along a direction that already exists. It does not by itself create conjugacy.",
        fig=MASS,
        alt=A_MASS,
        preview=P_HB,
    )
    b.save()


def bank_hb():
    b = Bank("heavy-ball-method")
    b.mc(
        1,
        r"One heavy-ball step computes the next point as",
        [
            r"the current point, minus a step size times the gradient at the current point, plus a momentum coefficient times the previous displacement",
            r"the current point minus a step size times the gradient at an extrapolated point",
            r"the Newton step, with the momentum coefficient equal to the inverse Hessian",
            r"the previous point, ignoring the current gradient",
        ],
        0,
        r"The update is \(x - \alpha \nabla f(x) + \beta (x - x_{\mathrm{prev}})\). The gradient is read at \(x\). Reading it at the extrapolated point \(x + \beta(x - x_{\mathrm{prev}})\) is the accelerated scheme that splits extrapolation from the gradient. The momentum coefficient is a scalar, not a matrix, and the update does not solve a Hessian system. Dropping the gradient leaves only the momentum term.",
        fig=MASS,
        alt=A_MASS,
    )
    b.num(
        1,
        r"Take \(x = (3,\ 1)\), \(x_{\mathrm{prev}} = (1,\ 1)\), \(\nabla f(x) = (2,\ 4)\), step size \(1/2\), and momentum coefficient \(1/2\). What is the second component of the next point?",
        -1,
        "1",
        r"The gradient contribution is \((1,\ 2)\). The displacement is \((2,\ 0)\), and half of it is \((1,\ 0)\). The next point is \((3,\ 1) - (1,\ 2) + (1,\ 0) = (3,\ -1)\). The second component is \(-1\). Reporting \(3\) is the first component. Reporting \(1\) leaves the second component at its old value and never subtracts the gradient. Reporting \(-3\) subtracts the full gradient entry \(4\) instead of half of it, since \(1 - 4 = -3\). The displacement has second component \(0\), so the momentum term does not change the second component.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.mc(
        1,
        r"The heavy-ball update is a finite-difference step for the differential equation",
        [
            r"\(\ddot x + \gamma \dot x + \nabla f(x) = 0\), a damped second-order equation",
            r"\(\dot x = -\nabla f(x)\), which has no second derivative to discretize",
            r"\(\ddot x = 0\), so the gradient is absent",
            r"\(\dot x + \nabla^2 f(x)\, x = 0\), a linear system for the Hessian",
        ],
        0,
        r"The second derivative supplies inertia and the first-derivative term supplies friction. Replacing them by a second difference and a backward difference, then clearing \(h^2\), produces a gradient step plus a multiple of the previous displacement. The first-order equation \(\dot x = -\nabla f(x)\) discretizes to gradient descent with no momentum term. Setting the gradient to zero removes the force. The Hessian does not appear as a coefficient in this discretization.",
        fig=MASS,
        alt=A_MASS,
    )
    b.order(
        2,
        r"Put these steps in the order that turns \(\ddot x + \gamma \dot x + \nabla f(x) = 0\) into the heavy-ball update. Each step uses the equation produced by the step before it.",
        [
            r"Replace the second derivative by the second difference \((x_{\mathrm{next}} - 2x + x_{\mathrm{prev}})/h^2\), and leave the first derivative in the equation.",
            r"In that substituted equation, replace the remaining first derivative by the backward difference \((x - x_{\mathrm{prev}})/h\).",
            r"Multiply the fully substituted equation by \(h^2\), so \(x_{\mathrm{next}}\) appears without a denominator.",
            r"From that cleared equation, move every term other than \(x_{\mathrm{next}}\) to the other side.",
        ],
        r"The second substitution is applied to the equation that still contains the first derivative, so it follows the second-difference replacement. Multiplying by \(h^2\) is what clears both denominators, and it needs both replacements to be present. Solving for \(x_{\mathrm{next}}\) is the rearrangement of that cleared equation. Swapping the two derivative replacements would leave the second step without the equation the first step was defined to produce.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which claims about the heavy-ball update are true?",
        [
            r"The momentum term is \(\beta\) times the previous displacement \(x - x_{\mathrm{prev}}\).",
            r"Setting \(\beta = 0\) leaves a gradient step from the current point.",
            r"The gradient is evaluated at the extrapolated point \(x + \beta(x - x_{\mathrm{prev}})\).",
            r"A nonzero \(\beta\) carries part of the previous displacement into the next point.",
            r"Each iteration inverts the Hessian.",
        ],
        [0, 1, 3],
        r"The update adds \(\beta(x - x_{\mathrm{prev}})\) after a gradient step from \(x\)."
        "\n"
        r"• With \(\beta = 0\) the displacement term drops, and the step is \(x - \alpha \nabla f(x)\)."
        "\n"
        r"• Evaluating the gradient at the extrapolated point is the other accelerated scheme. Heavy ball evaluates it at \(x\)."
        "\n"
        r"• Whenever \(\beta \ne 0\) and the displacement is nonzero, that displacement contributes to the next point."
        "\n"
        r"• The Hessian is not formed or inverted. The gradient is a vector, and \(\alpha\) and \(\beta\) are scalars.",
        fig=MASS,
        alt=A_MASS,
    )
    b.sym(
        2,
        r"The current position is the scalar \(a\), the previous position is \(b\), the gradient there is \(g\), the step size is \(s\), and the momentum coefficient is \(m\). The next position equals",
        "a-s*g+m*(a-b)",
        {"a": (-2, 2), "b": (-2, 2), "g": (0.5, 2), "s": (0.25, 1.5), "m": (0.2, 0.8)},
        r"Subtract the scaled gradient from the current position, then add the momentum coefficient times the displacement \(a - b\). Every declared name appears. Subtracting the momentum term, \(a - s g - m(a - b)\), flips the inertia. Evaluating a different gradient is not a change to this expression: here \(g\) is the gradient at the current position. Dropping \(m(a - b)\) is the plain gradient step.",
        alternates=["a-s*g+m*a-m*b", "(1+m)*a-m*b-s*g"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note takes a heavy-ball step from position \(4\), with previous position \(1\), gradient \(2\), step size \(1\), and momentum coefficient \(1/2\). Exactly one step is a false claim.",
        [
            r"The previous displacement is \(4 - 1 = 3\).",
            r"The gradient contribution is \(1\cdot 2 = 2\).",
            r"The momentum contribution is \(\tfrac{1}{2} \cdot 3 = 1.5\).",
            r"The next position is \(4 - 2 - 1.5 = 0.5\).",
        ],
        3,
        r"The displacement, the gradient contribution, and the momentum contribution are all as stated. The momentum term is added: \(4 - 2 + 1.5 = 3.5\). Subtracting it treats friction as if it reversed the previous displacement. The arithmetic \(4 - 2 - 1.5 = 0.5\) is the arithmetic of that reversed sign. It is not the update.",
        [
            r"The momentum term is added. The next position is \(4 - 2 + 1.5 = 3.5\), not \(0.5\).",
            r"The displacement \(4 - 1\) is not \(3\).",
            r"Half of \(3\) is not \(1.5\).",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"The Hessian eigenvalues lie between \(\mu = 1\) and \(L = 4\). The heavy-ball momentum coefficient \(\big((\sqrt{L}-\sqrt{\mu})/(\sqrt{L}+\sqrt{\mu})\big)^2\) equals",
        ((2 - 1) / (2 + 1)) ** 2,
        "1",
        r"\(\sqrt{4} = 2\) and \(\sqrt{1} = 1\), so the ratio is \(1/3\) and its square is \(1/9\). Reporting \(1/3\) stops before the square. Reporting \((4-1)/(4+1) = 3/5\) uses the condition number without the square root. Reporting \(4/9\) is the matching step size \(4/(\sqrt{L}+\sqrt{\mu})^2\), not the momentum coefficient. Those two parameters agree only for other endpoint pairs.",
        fig=DECAY,
        alt=A_DECAY,
    )
    b.mc(
        3,
        r"With those tuned parameters on a quadratic, the heavy-ball guarantee says that",
        [
            r"after \(k\) steps the distance to the minimizer is at most a constant times \(((\sqrt{\kappa}-1)/(\sqrt{\kappa}+1))^k\) times the initial distance",
            r"the function gap is multiplied each step by \(((\kappa-1)/(\kappa+1))^2\), the steepest-descent factor",
            r"the function gap is \(O(1/k^2)\), with no strong-convexity assumption",
            r"the gradient is zero after one step for every condition number",
        ],
        0,
        r"The tuned factor uses \(\sqrt{\kappa}\), and the bound is on the distance after \(k\) steps. The distance need not fall at every single step, because the inertia can overshoot. The factor \(((\kappa-1)/(\kappa+1))^2\) is the exact-line-search steepest-descent bound on the function gap, a different quantity. An \(O(1/k^2)\) function-gap bound is the accelerated-gradient claim for smooth convex objectives, and it does not use the eigenvalue window \([\mu, L]\). One step zeros the gradient only in special cases, such as a multiple of the identity under exact steepest search.",
        fig=ELL,
        alt=A_ELL,
    )
    b.mc(
        4,
        r"The accelerated update that extrapolates first and then reads the gradient at the extrapolated point, rather than at the current point, is",
        [
            r"Nesterov's scheme. Heavy ball reads the gradient before that extrapolation is used as the evaluation point.",
            r"still heavy ball, because both formulas contain a momentum coefficient",
            r"the conjugate-gradient direction update",
            r"a Newton step with a diagonal shift",
        ],
        0,
        r"Both updates contain a multiple of the previous displacement. The difference is the point at which the gradient is evaluated. Heavy ball uses \(\nabla f(x)\). The extrapolated scheme uses \(\nabla f\) at \(x + \beta(x - x_{\mathrm{prev}})\). Sharing a momentum coefficient does not make the two evaluation points the same. Conjugate gradient builds a direction by a multiple of the previous direction, using conjugacy. A shifted Newton step solves a linear system.",
        fig=ARR,
        alt=A_ARR,
        preview=P_NE,
    )
    b.num(
        4,
        r"The Hessian eigenvalues lie between \(\mu = 1\) and \(L = 4\). The heavy-ball step size \(4/(\sqrt{L}+\sqrt{\mu})^2\) equals",
        4 / (2 + 1) ** 2,
        "1",
        r"\(\sqrt{4} + \sqrt{1} = 3\), and \(4/3^2 = 4/9\). Reporting \(1/9\) is the momentum coefficient \(\big((2-1)/(2+1)\big)^2\) for the same endpoints. Reporting \(4/3\) forgets to square the sum. Reporting \(1/4\) uses \(L\) in the denominator as if the step size were \(1/L\), which is a gradient-descent choice and not this formula.",
        fig=DECAY,
        alt=A_DECAY,
        preview=P_NE,
    )
    b.mc(
        4,
        r"In the discretization of \(\ddot x + \gamma \dot x + \nabla f(x) = 0\) with step \(h > 0\), the momentum coefficient is \(1 - \gamma h\). Increasing the friction \(\gamma\), while keeping \(h\) fixed,",
        [
            r"decreases that coefficient, and the coefficient becomes negative once \(\gamma h > 1\)",
            r"increases the coefficient, because friction adds inertia",
            r"leaves the coefficient at \(1\), because \(h\) did not change",
            r"replaces the gradient step by a Newton step",
        ],
        0,
        r"The cleared equation gives the step size \(h^2\) in front of the gradient and the coefficient \(1 - \gamma h\) in front of the previous displacement. The derivative of that coefficient with respect to \(\gamma\) is \(-h\), which is negative. Past \(\gamma h = 1\) the coefficient changes sign. Friction is the first-derivative term, not an added inertia. Holding \(h\) fixed does not hold \(1 - \gamma h\) fixed when \(\gamma\) changes. The gradient term stays a scaled gradient. It does not become a Hessian solve.",
        fig=MASS,
        alt=A_MASS,
        preview=P_NE,
    )
    b.save()


def bank_ne():
    b = Bank("nesterov-accelerated-gradient")
    b.mc(
        1,
        r"One Nesterov step does which of the following?",
        [
            r"Extrapolate from the previous displacement, evaluate the gradient there, and step from that extrapolated point.",
            r"Evaluate the gradient at the current point, then add the momentum term.",
            r"Solve the Hessian against the gradient at the current point.",
            r"Project the current point onto a constraint set before any gradient is computed.",
        ],
        0,
        r"The extrapolated point is \(y = x + \beta(x - x_{\mathrm{prev}})\). The gradient is \(\nabla f(y)\), and the next point is \(y - \alpha \nabla f(y)\). Evaluating the gradient at \(x\) and then adding momentum is heavy ball. A Hessian solve is Newton. A projection is a later method for a constrained set. It is not this step.",
        fig=ARR,
        alt=A_ARR,
    )
    b.num(
        1,
        r"The current point is \((4,\ 2)\), the previous point is \((0,\ 2)\), and the momentum coefficient is \(3/4\). What is the first component of the extrapolated point, before the gradient is evaluated?",
        7,
        "1",
        r"The displacement is \((4,\ 0)\). Three quarters of it is \((3,\ 0)\). The extrapolated point is \((4,\ 2) + (3,\ 0) = (7,\ 2)\). The first component is \(7\). Reporting \(4\) stops at the current point. Reporting \(3\) is the momentum contribution, not the extrapolated coordinate. Reporting \(2\) is the second component, which the displacement does not change.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        r"Heavy ball and Nesterov's update both use a momentum coefficient. The distinction is that Nesterov",
        [
            r"evaluates the gradient at the extrapolated point, while heavy ball evaluates it at the current point",
            r"drops the momentum term and keeps only a gradient step",
            r"evaluates the gradient at the previous point, before the current point is known",
            r"replaces the gradient by the Hessian times the displacement",
        ],
        0,
        r"Write heavy ball as \(x + \beta(x - x_{\mathrm{prev}}) - \alpha \nabla f(x)\). The same extrapolation appears, and the gradient is still \(\nabla f(x)\). Nesterov puts \(\nabla f\) at the extrapolated point instead. The momentum term is present in both. The previous point is used to form the displacement. It is not the point where this gradient is read. The Hessian is not part of either update.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.order(
        2,
        r"Put these steps of one Nesterov iteration in order. Each step uses the result of the step before it.",
        [
            r"Subtract the previous point from the current point to obtain the displacement.",
            r"Add the momentum coefficient times that displacement to the current point. Call the sum the extrapolated point.",
            r"Evaluate the gradient at that extrapolated point.",
            r"Subtract the step size times that gradient from the extrapolated point to obtain the next point.",
        ],
        r"The extrapolated point is the current point plus a multiple of the displacement, so the displacement comes first. The gradient is evaluated at the extrapolated point, so that point has to exist. The subtraction that produces the next point uses that gradient, so it is last. Evaluating the gradient at the current point would be heavy ball, and it is not a reordering of these four steps.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"Which claims about Nesterov's \(O(1/k^2)\) guarantee are true?",
        [
            r"It bounds the function gap \(f(x_k) - f^\star\).",
            r"The bound is of order \(1/k^2\).",
            r"It bounds the distance \(\lVert x_k - x^\star\rVert\) by a constant over \(k^2\).",
            r"It uses convexity of \(f\) and a Lipschitz gradient.",
            r"It requires the Hessian to be positive definite at every point.",
        ],
        [0, 1, 3],
        r"The classical guarantee controls how far the value is above the minimum, and that gap is at most a constant times \(1/k^2\)."
        "\n"
        r"• The same sentence is not a bound on the distance to a minimizer. Distance can behave differently from the gap."
        "\n"
        r"• The argument uses a convex function, so the graph sits above its tangents, and a Lipschitz gradient, so a quadratic upper bound is available."
        "\n"
        r"• A positive definite Hessian is a stronger curvature assumption than this gap bound uses. The \(O(1/k^2)\) result does not assume it. Strong convexity is what produces a linear rate instead.",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.sym(
        2,
        r"The current position is the scalar \(a\), the previous position is \(b\), and the momentum coefficient is \(m\). The extrapolated position, before the gradient step, equals",
        "a+m*(a-b)",
        {"a": (-2, 2), "b": (-2, 2), "m": (0.2, 0.8)},
        r"Add the coefficient times the displacement \(a - b\) to the current position. Every declared name appears. The gradient step has not been applied yet, so a gradient symbol does not belong in this expression. Subtracting \(m(a - b)\) extrapolates in the opposite direction. The heavy-ball position \(a - s g + m(a - b)\) already includes a gradient term, and \(g\) is not one of the declared names here.",
        alternates=["(1+m)*a-m*b", "a*(1+m)-b*m"],
        fig=COL,
        alt=A_COL,
    )
    b.find_error(
        3,
        r"A note runs one Nesterov step from position \(5\), with previous position \(1\), momentum coefficient \(1/2\), and step size \(1\). The gradient at the current position is \(2\), and the gradient at the extrapolated position is \(4\). Exactly one step is a false claim.",
        [
            r"The extrapolated position is \(5 + \tfrac12(5 - 1) = 7\).",
            r"The gradient at that extrapolated position equals \(4\).",
            r"The step subtracts \(1\) times the gradient at the extrapolated position.",
            r"The next position is \(7 - 2 = 5\).",
        ],
        3,
        r"The displacement is \(4\), half of it is \(2\), and the extrapolated position is \(7\). The gradient there is \(4\), and the step size is \(1\), so the next position is \(7 - 4 = 3\). Subtracting \(2\) uses the gradient at the current position, which is the heavy-ball reading. The arithmetic \(7 - 2 = 5\) is that other update. It is not this one.",
        [
            r"The gradient at the extrapolated position is \(4\), so the next position is \(7 - 4 = 3\). Subtracting \(2\) reads the gradient at the current position.",
            r"The extrapolated position is not \(7\).",
            r"The gradient at the extrapolated position is not \(4\).",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"The gap bound used here is \(2 L \lVert x_0 - x^\star\rVert^2 / (k+1)^2\). With \(L = 5\), \(\lVert x_0 - x^\star\rVert^2 = 4\), and \(k = 4\), what is the bound?",
        2 * 5 * 4 / 25,
        "1",
        r"The numerator is \(2\cdot 5\cdot 4 = 40\). The denominator is \((4+1)^2 = 25\). The bound is \(40/25 = 1.6\). This number bounds the function gap \(f(x_4) - f^\star\). It is not a bound on the distance. The squared distance \(4\) was an input, not the value of the bound. Reporting \(40\) drops the denominator. Reporting \(4\) repeats that squared distance. Reporting \(2.5\) uses \(k^2 = 16\) in the denominator instead of \((k+1)^2 = 25\).",
        fig=SLOW,
        alt=A_SLOW,
    )
    b.mc(
        3,
        r"With the coefficient \((k-1)/(k+2)\) at iteration \(k\), the first iteration \(k = 1\)",
        [
            r"has coefficient \(0\), so the extrapolated point is the current point and the step is an ordinary gradient step",
            r"has coefficient \(1\), so the step skips the gradient",
            r"has coefficient \(1/2\), for every later schedule as well",
            r"is undefined, because the denominator \(k+2\) is zero",
        ],
        0,
        r"Substitute \(k = 1\): the numerator is \(0\) and the denominator is \(3\), so the coefficient is \(0\). The extrapolated point equals the current point, and the update subtracts the step size times the gradient there. A coefficient of \(1\) would require \(k - 1 = k + 2\). The value \(1/2\) is \((k-1)/(k+2)\) at \(k = 4\), not at \(k = 1\). The denominator \(3\) is not zero.",
        fig=RISE,
        alt=A_RISE,
    )
    b.mc(
        4,
        r"For a smooth convex objective, the gap after \(k\) Nesterov steps is \(O(1/k^2)\). The matching guarantee for plain gradient descent, from summing decrease inequalities, is",
        [
            r"\(O(1/k)\) on the function gap",
            r"\(O(1/k^2)\) on the distance to the minimizer",
            r"a squared-error bound, as in Newton near a nondegenerate minimizer",
            r"finite termination in \(n\) steps for every smooth convex function",
        ],
        0,
        r"Summing a decrease of order \(\lVert\nabla f\rVert^2\) produces a function-gap bound of order \(1/k\) for gradient descent. Nesterov's argument improves the exponent on that gap to \(2\). Neither of those sentences is a bound on distance of order \(1/k^2\). A squared-error bound is local Newton. Finite termination in \(n\) steps is the conjugate-direction fact for a positive definite quadratic, not a claim about every smooth convex function.",
        fig=SLOW,
        alt=A_SLOW,
        preview=P_GP,
    )
    b.num(
        4,
        r"The momentum coefficient \((k-1)/(k+2)\) at iteration \(k = 7\) equals",
        (7 - 1) / (7 + 2),
        "1",
        r"The numerator is \(6\) and the denominator is \(9\), so the coefficient is \(2/3\). Reporting \(7/9\) uses \(k\) in the numerator. Reporting \(6/7\) uses \(k\) in the denominator. Reporting \(0\) is the coefficient at \(k = 1\), where the numerator vanishes. The coefficient changes with \(k\). A constant momentum coefficient is a different choice.",
        fig=RISE,
        alt=A_RISE,
        preview=P_FW,
    )
    b.mc(
        4,
        r"The step size \(1/L\) in the smooth convex gap argument is tied to the descent lemma because",
        [
            r"the lemma supplies a quadratic upper bound of curvature \(L\), and \(1/L\) is the exact step on that upper bound",
            r"the lemma requires the Hessian to be singular",
            r"\(L\) is the momentum coefficient \((k-1)/(k+2)\)",
            r"the lemma bounds the distance \(\lVert x_k - x^\star\rVert\) by \(1/k^2\) directly",
        ],
        0,
        r"A Lipschitz gradient with constant \(L\) puts \(f\) under the quadratic \(f(y) + \nabla f(y)^T(z-y) + (L/2)\lVert z-y\rVert^2\). The minimizer of that quadratic in \(z\) is the step \(y - (1/L)\nabla f(y)\). The gap proof uses that upper bound. The lemma does not ask the Hessian to be singular. \(L\) is a curvature constant, not the scheduled momentum coefficient. The \(O(1/k^2)\) conclusion of the full argument is a bound on the function gap, not a distance bound read off the lemma alone.",
        fig=LEV,
        alt=A_LEV,
        preview=P_GP,
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


def expl_gs():
    save_explainer(
        "gram-schmidt-orthogonalization",
        "Gram-Schmidt orthogonalization",
        _sec(
            r"""Gram-Schmidt turns an independent list into an orthogonal list, one vector at a time. The first vector is kept. From each later vector, subtract its projections onto the vectors already accepted. The remainder is orthogonal to every accepted vector. The coefficient of an accepted vector \(u\) in the new vector \(v\) is the inner product of \(v\) and \(u\), divided by the squared length of \(u\).

The same arithmetic belongs to any inner product. Only the meaning of the product and of the squared length changes. When the product is \(x^T Q y\) with \(Q\) symmetric positive definite, the squared length is \(x^T Q x\). The vectors that come out then satisfy \(d_i^T Q d_j = 0\). That relation is called \(Q\)-conjugacy. Positive definiteness is what makes the squared length positive for every nonzero vector, so the division is legal.

Independence is what keeps every remainder nonzero. A vector that already lies in the span of the accepted ones is reproduced exactly by its projections, and the remainder vanishes. A zero remainder is not a new direction.""",
            r"""With an accepted vector \(u\) and a new vector \(v\),
\[
c = \frac{\langle v, u\rangle}{\langle u, u\rangle}, \qquad w = v - c\, u.
\]
For the product \(x^T Q y\), both the numerator and the denominator use that product. Then \(w^T Q u = 0\).""",
            r"""Take the dot product, the first vector \((4,\ 0)\), and the next vector \((6,\ 8)\). The inner product is \(24\) and the squared length of the first vector is \(16\). The coefficient is \(24/16\).

The keel coefficient is 1.5. Subtracting \(1.5\) times \((4,\ 0)\) from \((6,\ 8)\) leaves \((0,\ 8)\). The dot product of \((4,\ 0)\) with \((0,\ 8)\) is \(0\), so the two results are orthogonal. Scaling the first result to unit length would multiply this zero by a constant and leave it zero.""",
            r"""Using the inner product itself as the coefficient skips the division by the squared length. That over-subtracts whenever the accepted vector is not a unit vector. A second slip is to subtract a multiple of the new vector instead of a multiple of the accepted one. A third is to feed an indefinite symmetric matrix into \(x^T Q y\) and still call the result an inner product. Some nonzero vector then has a negative squared length. A fourth is to expect a nonzero remainder from a dependent list. Dependence is the case in which some remainder is zero. A fifth is to project onto the original inputs after they have stopped being orthogonal. The coefficients use the orthogonal vectors already accepted.""",
            r"""A list with \(d_i^T Q d_j = 0\) is a conjugate set for the quadratic whose Hessian is \(Q\). Exact line search along a full conjugate set reaches the minimizer of that quadratic in finitely many steps. Conjugate gradient builds the same kind of directions from gradients, instead of orthogonalizing a list that was chosen in advance.""",
            PAIR,
            A_PAIR,
        ),
    )


def expl_cd():
    save_explainer(
        "q-conjugate-directions",
        "Conjugate directions",
        _sec(
            r"""Two directions are \(Q\)-conjugate when their product through \(Q\) vanishes. The matrix \(Q\) is symmetric positive definite and is the Hessian of the quadratic under study. Euclidean orthogonality is the special case in which \(Q\) is the identity. A stretch that makes \(Q\) a non-scalar diagonal matrix splits the two conditions: a right angle on the page need not be conjugacy, and a conjugate pair need not meet at a right angle.

The conjugate-direction method is handed such a set and takes an exact line search along each direction in turn. On a quadratic, the restriction to a line is a parabola. The exact step sits at the bottom of that parabola. Because the directions are conjugate, the parabola in one coefficient does not contain the other coefficients. Each search removes one coefficient of the error, and later searches do not restore it.

In dimension \(n\) there are \(n\) coefficients. After at most \(n\) searches every coefficient is zero, so the point is the minimizer. The count does not depend on the condition number. The condition number changes how a method that lacks conjugacy behaves. It does not change this finite count.""",
            r"""Conjugacy and the exact step are
\[
d_i^T Q d_j = 0\ (i\ne j), \qquad t = -\frac{\nabla f(x)^T d}{d^T Q d}.
\]
The gradient of \(\tfrac{1}{2} x^T Q x + b^T x\) is \(Qx + b\). After the step, the new gradient is orthogonal to \(d\).""",
            r"""Let \(Q = \mathrm{diag}(1,\ 3)\), let the gradient be \((8,\ 1)\), and let the direction be \((-2,\ 0)\). The directional derivative is \(8\cdot(-2) = -16\). The curvature is \((-2)\cdot 1\cdot(-2) = 4\). The step length is \(16/4\).

The spar step is 4. The direction is a descent direction because the directional derivative is negative, and the positive curvature makes the parabola open upward. A second direction conjugate to this one would need a product of zero against \(Q\). The first standard-basis direction already has that product equal to zero against \((0,\ 1)\), since the off-diagonal entries are zero.""",
            r"""Calling a Euclidean right angle conjugacy omits \(Q\). The product that has to vanish is \(d_i^T Q d_j\). A second slip is to drop the minus sign in the step length. The directional derivative of a descent direction is already negative, and the minus sign turns the length positive. A third is to divide by \(d^T d\) when \(Q\) is not the identity. The curvature is \(d^T Q d\). A fourth is to expect the gradient to vanish after one search in a plane. The new gradient is orthogonal to the direction just used. The other component can still be large. A fifth is to expect the finite count to fail when the condition number is large. The count is the dimension.""",
            r"""Conjugate gradient does not ask for the directions in advance. It builds the next direction from the new gradient and a multiple of the previous direction, and the multiple is the one that restores conjugacy. On a positive definite quadratic the finite termination remains. The multiple is what replaces the list.""",
            ELL,
            A_ELL,
        ),
    )


def expl_cg():
    save_explainer(
        "conjugate-gradient-method",
        "Conjugate gradient method",
        _sec(
            r"""Conjugate gradient keeps the exact line search of the conjugate-direction method and manufactures the directions as it goes. The first direction is the negative gradient. After a step, the new direction is the negative of the new gradient, plus a multiple of the direction just used. The multiple is chosen so the new direction is \(Q\)-conjugate to the previous one.

For a quadratic, that multiple is the ratio of successive squared gradient lengths. The new squared length goes in the numerator. The old squared length goes in the denominator. The first iteration has no previous direction, so there is nothing to multiply and the formula is not used.

Each iteration's expensive work is one product of \(Q\) with a vector. A few vector additions finish the update. The Hessian is never factored. In exact arithmetic a positive definite quadratic of dimension \(n\) is finished in at most \(n\) iterations, because each iteration contributes one new conjugate direction and \(n\) of them span the space.

The condition number \(\kappa\) still describes the shape. The bound on the \(Q\)-norm of the error after \(k\) steps carries the factor \(2\big((\sqrt{\kappa}-1)/(\sqrt{\kappa}+1)\big)^k\). The square root is the improvement over a factor built from \(\kappa\) itself. Steepest descent's guarantee is a different sentence: it bounds the function gap by a square of \((\kappa-1)/(\kappa+1)\).""",
            r"""With \(g\) the gradient at the current point and \(g_+\) the gradient after the step,
\[
\beta = \frac{\lVert g_+\rVert^2}{\lVert g\rVert^2}, \qquad d_+ = -g_+ + \beta d.
\]
The first direction is \(d = -g\). The \(Q\)-norm error bound uses the base \((\sqrt{\kappa}-1)/(\sqrt{\kappa}+1)\).""",
            r"""Take an old gradient \((2,\ 2)\) and a new gradient \((1,\ 2)\). The new squared length is \(1 + 4 = 5\). The old squared length is \(4 + 4 = 8\). The ratio is \(5/8\).

The cleat weight is 0.625. The previous direction, if it was the negative of the old gradient, is \((-2,\ -2)\). The new direction is \(-(1,\ 2) + 0.625\cdot(-2,\ -2)\). The ratio uses squared lengths. Dividing the square roots of those lengths would be a different number.""",
            r"""Inverting the squared-norm ratio puts the old gradient on top and produces a multiple that does not cancel the \(Q\)-product. A second slip is to add the multiple of the old gradient instead of the multiple of the old direction. On the first iteration those two vectors are opposites, so the sign of the carried term flips. A third is to quote the steepest-descent factor \(((\kappa-1)/(\kappa+1))^2\) as if it were the conjugate-gradient factor. The conjugate-gradient base takes a square root before the subtraction, and it multiplies a \(Q\)-norm error, with a leading \(2\). A fourth is to expect termination in \(n\) steps on a nonquadratic objective. The proof used one fixed Hessian. A changing Hessian removes the finite count, which is why a nonlinear run is often restarted.""",
            r"""Heavy ball spends the same wish for a faster ill-conditioned rate on a different mechanism: a fraction of the previous displacement, with the gradient read at the current point. The extrapolated scheme reads the gradient after the momentum shift. Neither one builds a conjugate direction. Both are aimed at the slow factor that steepest descent suffers when \(\kappa\) is large.""",
            DECAY,
            A_DECAY,
        ),
    )


def expl_hb():
    save_explainer(
        "heavy-ball-method",
        "Heavy-ball momentum",
        _sec(
            r"""Heavy ball adds inertia to a gradient step. The next point is the current point, minus a step size times the gradient at the current point, plus a momentum coefficient times the displacement from the previous point to the current one. Setting the coefficient to zero recovers an ordinary gradient step. A nonzero coefficient keeps part of the previous move alive.

The formula is the finite-difference image of a damped mechanical equation. A mass has a second derivative, friction has a first derivative, and the gradient is the force pulling toward lower values: the second derivative plus a positive multiple of the first derivative plus the gradient equals zero. Replace the second derivative by a second difference over a spacing \(h\), replace the first derivative by a backward difference, and multiply through by \(h^2\). The gradient is multiplied by \(h^2\), and the previous displacement is multiplied by \(1\) minus the friction coefficient times \(h\).

On a quadratic whose Hessian eigenvalues lie between \(\mu\) and \(L\), two fixed choices match that shape. The step size is \(4\) over \((\sqrt{L}+\sqrt{\mu})^2\). The momentum coefficient is the square of \((\sqrt{L}-\sqrt{\mu})/(\sqrt{L}+\sqrt{\mu})\). Where \(\kappa = L/\mu\), the distance after \(k\) steps is at most a constant times \(((\sqrt{\kappa}-1)/(\sqrt{\kappa}+1))^k\) times the initial distance. Inertia can overshoot, so the distance need not fall at every step. Steepest descent's factor \(((\kappa-1)/(\kappa+1))^2\) bounds the function gap instead, and it has no square root.""",
            r"""The update and the tuned parameters are
\[
x_+ = x - \alpha \nabla f(x) + \beta (x - x_{\mathrm{prev}}),
\]
\[
\alpha = \frac{4}{(\sqrt{L}+\sqrt{\mu})^2}, \qquad \beta = \left(\frac{\sqrt{L}-\sqrt{\mu}}{\sqrt{L}+\sqrt{\mu}}\right)^2.
\]
From the differential equation, \(\alpha = h^2\) and \(\beta = 1 - \gamma h\).""",
            r"""Start at position \(6\), with previous position \(3\), gradient \(3\), step size \(1\), and momentum coefficient \(0.2\). The displacement is \(3\). The gradient contribution is \(3\). The momentum contribution is \(0.2\cdot 3 = 0.6\). The next position is \(6 - 3 + 0.6\).

The drum position is 3.6. The momentum term was added. Subtracting it would have landed at \(2.4\), which is a different update. For eigenvalues between \(1\) and \(16\), the tuned momentum coefficient is \((3/5)^2 = 0.36\), and the tuned step size is \(4/25 = 0.16\). Those parameters are not the \(0.2\) and \(1\) of the scalar step above.""",
            r"""Subtracting the momentum term reverses the previous displacement. The derivation adds it. A second slip is to evaluate the gradient at the extrapolated point and still call the result heavy ball. That evaluation point belongs to the extrapolated scheme. A third is to quote \(((\kappa-1)/(\kappa+1))^2\) as the heavy-ball distance factor. The distance factor uses a square root, and it is not squared again to produce the momentum coefficient. The momentum coefficient is the square of that root factor. The distance factor itself is not squared. A fourth is to forget that \(1 - \gamma h\) becomes negative when the friction times the spacing exceeds \(1\). The algebra does not protect the sign.""",
            r"""The extrapolated scheme uses the same displacement and reads the gradient after the extrapolation, at the shifted point, rather than at the current point. Its classical guarantee on a smooth convex objective is a bound on the function gap of order \(1/k^2\). That sentence is not a distance bound, and it does not need the strong-convexity window \([\mu, L]\) that the linear heavy-ball factor uses.""",
            MASS,
            A_MASS,
        ),
    )


def expl_ne():
    save_explainer(
        "nesterov-accelerated-gradient",
        "Nesterov's accelerated gradient",
        _sec(
            r"""Nesterov's iteration moves the point where the gradient is read. First form the displacement from the previous point to the current point, and step past the current point by a coefficient times that displacement. Call the landing place the extrapolated point. Then evaluate the gradient there, and subtract a step size times that gradient from the extrapolated point.

Heavy ball uses the same displacement, but it subtracts the gradient at the current point. The formulas agree only when the coefficient is zero or the two gradients match.

On a convex objective with an \(L\)-Lipschitz gradient, a scheduled coefficient \((k-1)/(k+2)\) gives a bound on the function gap \(f(x_k) - f^\star\) of order \(1/k^2\). One explicit form is \(2 L \lVert x_0 - x^\star\rVert^2 / (k+1)^2\). The quantity on the left is the gap. The distance to a minimizer is not what this inequality controls. The argument uses convexity, so tangents stay under the graph, and the descent lemma, so a quadratic of curvature \(L\) stays above the graph. It does not need a positive definite Hessian. Strong convexity is a stronger hypothesis and produces a linear rate instead.

At iteration \(k = 1\) the scheduled coefficient is zero, because the numerator is zero. The first step is an ordinary gradient step. Later coefficients grow toward \(1\) and keep changing. A constant coefficient is a different choice.""",
            r"""With coefficient \(\beta\),
\[
y = x + \beta (x - x_{\mathrm{prev}}), \qquad x_+ = y - \alpha \nabla f(y).
\]
The gap satisfies \(f(x_k) - f^\star = O(1/k^2)\) for smooth convex \(f\). The step \(\alpha = 1/L\) is the minimizer of the descent-lemma upper bound.""",
            r"""Take the current position \(9\), the previous position \(3\), and the coefficient \(1/3\). The displacement is \(6\). One third of it is \(2\). The extrapolated position is \(9 + 2\).

The buoy point is 11. A gradient of \(2\) at that extrapolated position, with step size \(1/2\), moves the point to \(11 - 1 = 10\). Reading a different gradient at the unshifted position would be the heavy-ball evaluation. The schedule at iteration \(5\) has coefficient \((5-1)/(5+2) = 4/7\), which is not the coefficient used in this step.""",
            r"""Reading the gradient at the current point, after having formed the extrapolated point and then ignored it, is heavy ball. The subtraction has to use the gradient at the extrapolated point. A second slip is to describe the \(O(1/k^2)\) result as a bound on \(\lVert x_k - x^\star\rVert\). The inequality bounds \(f(x_k) - f^\star\). A third is to require a positive definite Hessian for that gap bound. Convexity and a Lipschitz gradient are the hypotheses. A fourth is to freeze the coefficient at its first value. The first value is zero, and the schedule changes it. A fifth is to put \(k\) in the denominator of the explicit bound instead of \(k+1\).""",
            r"""The descent lemma is also the quadratic upper bound a projected gradient step minimizes before it projects onto a convex set. Farther on, a conditional-gradient step minimizes a linear model over the set instead of projecting, and it too carries a function-gap bound. That bound is of order \(1/k\), not \(1/k^2\). The extrapolation here is what improves the exponent, and it does so for the gap.""",
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
    "gram-schmidt-orthogonalization": "The keel coefficient is 1.5",
    "q-conjugate-directions": "The spar step is 4",
    "conjugate-gradient-method": "The cleat weight is 0.625",
    "heavy-ball-method": "The drum position is 3.6",
    "nesterov-accelerated-gradient": "The buoy point is 11",
}

LEAKS = {
    "gram-schmidt-orthogonalization": ["(3, 1)", "(2, 5)", "(2, 3, 4)", "12/4"],
    "q-conjugate-directions": ["(6, 4)", "(1, -1)", "diag(3, 1)"],
    "conjugate-gradient-method": ["4/9", "5/6", "(0, 6)", "0.833333"],
    "heavy-ball-method": ["1/9", "4/9", "(2, 4)"],
    "nesterov-accelerated-gradient": ["0.75", "40/25", "k = 7"],
}


def main():
    _balance_mc()
    bank_gs()
    bank_cd()
    bank_cg()
    bank_hb()
    bank_ne()
    expl_gs()
    expl_cd()
    expl_cg()
    expl_hb()
    expl_ne()
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
