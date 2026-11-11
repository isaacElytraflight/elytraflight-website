#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB3 banks and explainers.

Skills: directional-derivative, gradient-partial-derivatives,
differentiability-multivariable, hessian-matrix, jacobian-chain-rule,
matrix-calculus-gradients, fundamental-theorem-along-segment,
taylor-approximation-multivariable, taylor-exact-mean-value.

Closed-form answers live here. skilltree/verify_nlo_nb3.py recomputes the
numeric ones and does not import this file. Symbolic keys are checked by
the shared harness.
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import DEEP_TYPES, Bank, deep_quota, save_explainer
from templates import ellipse_axes, level_curves_fig, matrix_fig, plane_vectors, plot, segment_fig

RAY = plane_vectors([(1.4, 0.5, "d")], "one arrow from the origin")
A_RAY = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.3, 0.4, "g"), (-0.4, 1.3, "t")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."
LEVELS = level_curves_fig("nested ellipses")
A_LEVELS = "Three nested ellipses centered at the origin."
SEG = segment_fig("segment on a dashed line")
A_SEG = "A solid segment lies on a longer dashed line."
ELL = ellipse_axes("axis-aligned ellipse")
A_ELL = "An ellipse centered at the origin, longer along the first axis."
SLICE = plot(lambda t: 0.15 * t * t + 0.4, 0.0, 2.4, "t", "g", "slice along a line")
A_SLICE = "A curve of one variable, drawn on labeled axes."
HESS = matrix_fig([["xx", "xy"], ["yx", "yy"]], "second-derivative positions")
A_HESS = "A 2 by 2 array labeled by second-derivative positions."
JAC = matrix_fig([["J11", "J12"], ["J21", "J22"]], "jacobian positions")
A_JAC = "A 2 by 2 array labeled as a Jacobian."
QUAD = matrix_fig([["p", "q"], ["r", "s"]], "a 2 by 2 pattern")
A_QUAD = "A 2 by 2 array with four letter entries."


def bank_directional():
    b = Bank("directional-derivative")
    b.mc(1,
         r"The directional derivative \(f'(x; d)\) is",
         [r"the limit of \([f(x + t d) - f(x)] / t\) as \(t\) decreases to 0",
          r"the two-sided limit of that same quotient as \(t\) tends to 0",
          r"the sum of the partial derivatives at \(x\)",
          r"the length of the direction \(d\)"],
         0,
         r"Only positive steps are used, so the limit is one-sided along the ray. A two-sided limit would ask the slice to be differentiable at 0, which is stronger and can fail at a corner. Adding partial derivatives is a different object, and it needs those partials to exist. The length of \(d\) does not involve \(f\).",
         SLICE, A_SLICE)
    b.num(1,
          r"Let \(f(x, y) = x^2 + 4y\). What is \(f'((3, 1); (1, 0))\)?",
          6, "1",
          r"Along \(x = 3 + t\), \(y = 1\), the difference quotient is \(6 + t\), and the limit is 6. The same value is \(2 \cdot 3 \cdot 1 + 4 \cdot 0\). The partial derivative in \(y\) is 4, and that is the derivative in the direction \((0, 1)\), not in \((1, 0)\). The function value \(9 + 4 = 13\) is not a slope.",
          RAY, A_RAY)
    b.mc(1,
         r"When \(c > 0\) and both derivatives exist, \(f'(x; c d)\) equals",
         [r"\(f'(x; d)\) with no change",
          r"\(c\, f'(x; d)\)",
          r"\(f'(x; d) / c\)",
          r"\(f'(x; d) + c\)"],
         1,
         r"A positive scale runs along the same ray at a different speed, and the difference quotient picks up that factor. Leaving the factor out treats every positive scale as the same direction vector. Dividing by \(c\) runs the scaling backwards. Adding \(c\) is not how a slope transforms.",
         RAY, A_RAY)
    b.order(2,
            r"Put these steps in the order used to compute \(f'(x; d)\) from the definition.",
            ["Form the point x + t d with t positive.",
             "Subtract f(x) from the value at that point.",
             "Divide the difference by t.",
             "Take the limit as t decreases to 0."],
            r"The definition builds one difference quotient and then takes a one-sided limit. The point on the ray has to come first, because the numerator uses it. Division by t comes after the numerator exists. The limit is last. Dividing before subtracting, or sending t to 0 through negative values, computes a different limit.",
            SLICE, A_SLICE)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 4y\). What is \(f'((3, 1); (0, 1))\)?",
          4, "1",
          r"The slice is \(y = 1 + t\) with \(x\) fixed at 3. Then \(f = 9 + 4 + 4t\), so the quotient is 4. The partial derivative in \(x\) at this point is \(2 \cdot 3 = 6\), which belongs to the direction \((1, 0)\). The product \(4 \cdot 1 = 4\) happens to match because the direction's second coordinate is 1; the function value 13 is not the slope.",
          RAY, A_RAY)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 4y\). What is \(f'((3, 1); (2, -1))\)?",
          8, "1",
          r"The formula \(2 x\, d_1 + 4 d_2\) gives \(2 \cdot 3 \cdot 2 + 4 \cdot (-1) = 8\). On the slice, \(f(3 + 2t, 1 - t) = 13 + 8t + 4t^2\), so the quotient tends to 8. Using only the first partial gives 6. Using only the second gives 4. The squared length of the direction is \(4 + 1 = 5\), which is not the slope.",
          PAIR, A_PAIR)
    b.sym(3,
          r"Let \(a\) and \(b\) be real. At \((1, 0)\), the directional derivative of \(a x^2 + b y\) in the direction \((1, 1)\) is an expression in the names a and b. Write that expression.",
          "2*a+b",
          {"a": (-4, 4), "b": (-4, 4)},
          r"The partial derivative in \(x\) is \(2 a x\), which equals \(2a\) at \(x = 1\). The partial derivative in \(y\) is \(b\). The direction \((1, 1)\) adds them, so the derivative is \(2a + b\)."
          "\n"
          r"• \(2a\) drops the second coordinate of the direction."
          "\n"
          r"• \(a + b\) differentiates \(a x^2\) as if it were \(a x\)."
          "\n"
          r"• \(ab\) multiplies the two coefficients. The direction asks for a sum.",
          ["b+2*a", "2*(a)+b"],
          fig=SLICE, alt=A_SLICE)
    b.num(3,
          r"Let \(f(x, y) = x^2 + 4y\). What is \(f'((2, 5); (3, 1))\)?",
          16, "1",
          r"\(2 \cdot 2 \cdot 3 + 4 \cdot 1 = 16\). The function value at \((2, 5)\) is \(4 + 20 = 24\), which is not a slope. The sum of the direction coordinates is 4. The partial derivative in \(x\) alone is 4 at this point, and that would be the answer only for the direction \((1, 0)\).",
          RAY, A_RAY)
    b.mc(3,
         r"For the slice \(g(t) = f(x + t d)\), the directional derivative equals",
         [r"the two-sided derivative \(g'(0)\), even when that limit fails",
          r"the slope of the secant from \(t = -1\) to \(t = 1\)",
          r"the right-hand derivative of \(g\) at 0",
          r"the value \(g(0)\)"],
         2,
         r"Positive \(t\) is the right-hand side of the slice, so the directional derivative is \(g'(0+)\). The two-sided derivative can fail while the right-hand derivative exists. One secant, from \(-1\) to \(1\), is a difference quotient at a fixed step, not the limit. The value \(g(0)\) is \(f(x)\), not a slope.",
         SLICE, A_SLICE)
    b.multi(4,
            "Which statements hold for this one-sided directional derivative?",
            [r"It is a limit of difference quotients as the step decreases to 0.",
             r"For \(c > 0\), the derivative in the direction \(c d\) is \(c\) times the derivative in the direction \(d\), when both exist.",
             "It exists only after a gradient has been shown to exist.",
             "It is always linear in the direction, including at a corner of the slice."],
            [0, 1],
            r"The definition is that one-sided limit, and a positive rescaling multiplies the quotient by the same positive factor. A gradient is a later, stronger object: the directional derivative along one ray can exist with no gradient. At a corner the two opposite rays can both give a positive slope, so the map \(d \mapsto f'(x; d)\) need not be linear. The inner product with a gradient is the case where linearity does hold.",
            PAIR, A_PAIR, ["gradient-partial-derivatives"])
    b.num(4,
          r"What is the directional derivative of \(f(x) = \lvert x \rvert\) at \(0\) in the direction \(3\)?",
          3, "1",
          r"For \(t > 0\), \([\lvert 3t \rvert - 0] / t = 3\). The limit is 3. The direction \(-3\) gives \([\lvert -3t \rvert] / t = 3\) as well, so the two rays do not produce opposite signs. The two-sided derivative of \(\lvert x \rvert\) at 0 does not exist; that is a different limit. Dividing the result by 3 produces the derivative in the unit direction, not in the direction 3.",
          SLICE, A_SLICE, ["ad-forward-mode"])
    b.mc(4,
         r"At a corner of \(\lvert x \rvert\), the one-sided directional derivatives",
         ["fail to exist in every direction",
          "are negative in every direction",
          "are zero in every direction",
          r"can be positive both along \(d\) and along \(-d\)"],
         3,
         r"Leaving 0 in either direction increases \(\lvert x \rvert\), so both one-sided derivatives are positive. They exist. They are not zero, and they are not negative. What fails is the two-sided derivative on the line, and with it any claim that the directional derivative is linear in \(d\). A later differentiability test is what rules this corner out.",
         SLICE, A_SLICE, ["differentiability-multivariable"])
    b.save()


def bank_gradient():
    b = Bank("gradient-partial-derivatives")
    b.mc(1,
         "The gradient of a scalar function is",
         ["the vector whose entries are the partial derivatives",
          "the sum of the partial derivatives",
          "the matrix of second partial derivatives",
          "a unit vector in every case"],
         0,
         r"Each coordinate of the gradient is one partial derivative. Adding those partials collapses the vector to a scalar and loses the direction. Second partials form the Hessian, a later matrix. The gradient has whatever length the partials give it; normalizing it is a separate step.",
         PAIR, A_PAIR)
    b.num(1,
          r"Let \(f(x, y) = x^2 + 4 y^2\). At \((3, 1)\), what is the first entry of \(\nabla f\)?",
          6, "1",
          r"Differentiating in \(x\) gives \(2x\), so the first entry is \(2 \cdot 3 = 6\). The second entry is \(8y = 8\), which is the other coordinate of the gradient. The function value is \(9 + 4 = 13\). Twice the second coordinate of the point is 2, and that is not a partial derivative.",
          ELL, A_ELL)
    b.mc(1,
         r"Where \(f\) is differentiable, \(f'(x; d)\) equals",
         [r"\(\nabla f(x)\) with \(d\) ignored",
          r"\(\nabla f(x)^{T} d\)",
          r"\(\lVert \nabla f(x) \rVert + \lVert d \rVert\)",
          r"the product of the entries of \(\nabla f(x)\)"],
         1,
         r"Differentiability makes the directional derivative linear, and the linear map is the inner product with the gradient. The gradient alone is the derivative in the direction of the first basis vector only when \(d\) is that basis vector. Adding the two lengths is not an inner product. Multiplying the partials together is not one either.",
         PAIR, A_PAIR)
    b.sym(2,
          r"The partial derivative of \(a x y + b y^2\) with respect to \(y\) is an expression in the names a, b, x, and y. Write that expression.",
          "a*x+2*b*y",
          {"a": (-3, 3), "b": (-3, 3), "x": (-3, 3), "y": (-3, 3)},
          r"Hold \(x\) fixed and differentiate in \(y\). The term \(a x y\) contributes \(a x\). The term \(b y^2\) contributes \(2 b y\)."
          "\n"
          r"• \(a y + 2 b y\) differentiates the product as if \(x\) were the variable."
          "\n"
          r"• \(a x + b y\) misses the factor 2 on the square."
          "\n"
          r"• \(a x y + 2 b y\) leaves a factor of \(y\) on the first term.",
          ["2*b*y+a*x", "a*(x)+2*(b*y)"],
          fig=ELL, alt=A_ELL)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 4 y^2\). At \((3, 1)\), what is the second entry of \(\nabla f\)?",
          8, "1",
          r"Differentiating in \(y\) gives \(8y\), so the second entry is 8. The first entry is \(2x = 6\). The function value is 13. The coefficient 4 in front of \(y^2\) is not itself the partial derivative, because the square contributes an extra factor \(2y\).",
          ELL, A_ELL)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 4 y^2\). At \((3, 1)\), what is \(f'((3, 1); (1, 1))\)?",
          14, "1",
          r"The gradient is \((6, 8)\), and the inner product with \((1, 1)\) is \(6 + 8 = 14\). The length of the gradient is 10, which is the slope in the unit direction of the gradient, not in \((1, 1)\). The direction \((1, 1)\) has length \(\sqrt{2}\), so 14 is larger than the steepest unit slope. Either partial alone, 6 or 8, drops one coordinate of the direction.",
          PAIR, A_PAIR)
    b.order(3,
            "Put these steps in the order used to go from partial derivatives to a directional derivative.",
            ["Differentiate f in each coordinate, holding the others fixed.",
             "Stack those partial derivatives into the gradient.",
             "Take the inner product of the gradient with the direction.",
             "Read that scalar as the directional derivative."],
            r"The partial derivatives are the raw material, the gradient is the vector they form, and the directional derivative is the inner product of that vector with the direction. The inner product cannot come before the vector exists. Reading a single partial as the answer skips the direction. Normalizing the gradient is a different request and is not one of these steps.",
            PAIR, A_PAIR)
    b.num(3,
          r"Let \(f(x, y) = x^2 + 4 y^2\). At \((3, 1)\), what is the Euclidean length of \(\nabla f\)?",
          10, "1",
          r"The gradient is \((6, 8)\), and \(\sqrt{36 + 64} = \sqrt{100} = 10\). That length is the rate of increase in the unit direction of the gradient. The sum of the entries is 14, which is the derivative in the direction \((1, 1)\), a vector longer than 1. The larger entry alone is 8. The function value 13 is not a length of the gradient.",
          ELL, A_ELL)
    b.mc(3,
         "The direction of steepest ascent, among unit vectors, is",
         ["the direction in which the directional derivative is zero",
          "any direction whose inner product with the gradient is negative",
          "the gradient divided by its length",
          "the negative of the second partial derivative"],
         2,
         r"On the unit circle the inner product \(\nabla f^{T} d\) is largest when \(d\) points along \(\nabla f\), and the largest value is the length of \(\nabla f\). A zero inner product is tangent to the level set. A negative inner product is a descent direction. One second partial derivative does not pick the direction.",
         LEVELS, A_LEVELS)
    b.multi(4,
            r"Which statements hold where the gradient exists and \(f\) is differentiable?",
            [r"The directional derivative in a direction \(d\) equals the gradient dotted with \(d\).",
             "The slope in the unit direction of the gradient equals the length of the gradient.",
             "The gradient is a unit vector.",
             "A zero directional derivative in one nonzero direction means the gradient is the zero vector."],
            [0, 1],
            r"Differentiability identifies every directional derivative with the inner product, and the Cauchy-Schwarz bound on that inner product is the length of the gradient, attained on the unit vector along the gradient. The gradient has that length only in special cases; in general it is not a unit vector. One zero directional derivative means the gradient is orthogonal to that direction, which is the tangent case, not the zero-gradient case.",
            LEVELS, A_LEVELS, ["hessian-matrix"])
    b.num(4,
          r"Let \(f(x, y) = x^2 + 4 y^2\). At \((1, 2)\), what is \(f'((1, 2); (1, 1))\)?",
          18, "1",
          r"The gradient is \((2, 16)\), and the inner product with \((1, 1)\) is \(2 + 16 = 18\). The function value is \(1 + 16 = 17\). The length of this gradient is \(\sqrt{4 + 256} = \sqrt{260}\), which is not 18. Either coordinate of the gradient, 2 or 16, is the derivative in a coordinate direction, not in \((1, 1)\).",
          PAIR, A_PAIR, ["descent-directions"])
    b.mc(4,
         r"A descent direction \(d\) is recognized by",
         [r"\(\nabla f(x)^{T} d > 0\)",
          r"\(\nabla f(x)^{T} d = \lVert d \rVert\)",
          r"\(\nabla f(x) = d\)",
          r"\(\nabla f(x)^{T} d < 0\)"],
         3,
         r"The first-order change along \(d\) is the inner product of the gradient with \(d\). A negative value means the function decreases for a short step. A positive value is ascent. Equality with the length of \(d\) is not the test, and setting the gradient equal to \(d\) names one particular vector rather than the half-space of descent directions.",
         PAIR, A_PAIR, ["first-order-optimality"])
    b.save()


def bank_diff():
    b = Bank("differentiability-multivariable")
    b.mc(1,
         "Differentiability at a point means that",
         [r"there is a linear map whose remainder is \(o(\lVert h \rVert)\) as \(h \to 0\)",
          "both partial derivatives exist at that single point",
          "every directional derivative exists, with no further requirement",
          "the function is continuous along the two axes"],
         0,
         r"The definition asks for a linear approximation whose error, divided by the length of the step, tends to 0. Partial derivatives at the point are necessary but not sufficient. Directional derivatives in every direction are also not sufficient, because the approximation has to be linear and the little-o limit has to be uniform in the direction. Continuity along the axes is weaker still.",
         LEVELS, A_LEVELS)
    b.num(1,
          r"Let \(f(x, y) = x^2 + 3y\), and let \(L\) be the inner product with \(\nabla f(1, 2)\). For the step \((0.1, 0)\), what is the absolute remainder \(\lvert f(1.1, 2) - f(1, 2) - L(0.1, 0) \rvert\)?",
          0.01, "1",
          r"\(f(1, 2) = 7\) and \(\nabla f(1, 2) = (2, 3)\), so \(L(0.1, 0) = 0.2\). The shifted value is \(1.21 + 6 = 7.21\). The remainder is \(7.21 - 7 - 0.2 = 0.01\). The change in the function, \(0.21\), still includes the linear term. The step length \(0.1\) is the denominator of the little-o quotient, not the remainder.",
          SLICE, A_SLICE)
    b.mc(1,
         "If the partial derivatives exist and are continuous near the point, then",
         ["the function can still fail to be differentiable there",
          "the function is differentiable there",
          "the Hessian exists and is symmetric",
          "every second directional derivative is zero"],
         1,
         r"Continuous partial derivatives on a neighborhood are a sufficient condition for differentiability. They are not necessary, but the implication in this direction holds. Symmetry of the Hessian needs second derivatives. Nothing in the first-derivative hypothesis forces second derivatives to vanish.",
         LEVELS, A_LEVELS)
    b.multi(2,
            "Which implications hold?",
            ["Differentiability implies that the partial derivatives exist.",
             "Continuous partial derivatives on a neighborhood imply differentiability.",
             "Existence of both partial derivatives at the point implies differentiability.",
             "Existence of every directional derivative implies differentiability."],
            [0, 1],
            r"A differentiable function has a linear approximation, and the partial derivatives are that linear map on the basis vectors, so they exist. Continuous partials are the standard sufficient condition. The two converses fail: partials can exist while the little-o remainder does not tend to 0, and directional derivatives can exist in every direction without being linear in the direction.",
            PAIR, A_PAIR)
    b.num(2,
          r"For \(f(x, y) = x^2 + 3y\) at \((1, 2)\) and the step \((0.1, 0)\), the absolute remainder is \(0.01\). What is that remainder divided by the length of the step?",
          0.1, "1",
          r"The step length is \(0.1\), and \(0.01 / 0.1 = 0.1\). The little-o test sends this quotient to 0 as the step shrinks; the value 0.1 is the quotient at this particular step, not the limit. The remainder itself is 0.01. The linear term 0.2 divided by the step length is 2, which is the first partial derivative, not the quotient of the remainder.",
          SLICE, A_SLICE)
    b.num(2,
          r"Let \(f(x, y) = x^2 y\) and let \(L\) be the inner product with \(\nabla f(1, 1)\). For the step \((0.5, 0)\), what is the absolute remainder?",
          0.25, "1",
          r"\(f(1, 1) = 1\) and \(\nabla f(1, 1) = (2, 1)\), so \(L(0.5, 0) = 1\). The shifted value is \(2.25\). The remainder is \(2.25 - 1 - 1 = 0.25\). The change in the function is \(1.25\), which still contains the linear term. Half of the step, \(0.25\), matches the remainder numerically and is not the reason: the remainder is the quadratic leftover \((0.5)^2 \cdot 1\).",
          SLICE, A_SLICE)
    b.find_error(3,
                 r"One step below is false. Select that step, and the reason it fails. The function equals 0 on each axis and equals 1 at every point off both axes.",
                 ["Let f be 0 when x = 0 or y = 0, and let f be 1 at every other point.",
                  "Both partial derivatives of f at the origin exist, and both equal 0.",
                  "Differentiability requires a linear map whose remainder is little-o of the step length.",
                  "Because the partial derivatives exist, that little-o condition holds automatically."],
                 3,
                 r"Along each axis the function is identically 0, so both partial derivatives at the origin are 0. The third step is the definition of differentiability. The false step is the last one. Existence of the partials does not produce the little-o remainder. Along the direction (1, 1) the difference quotient is 1/t, which is unbounded, so no linear map works.",
                 reasons=["Partials can exist while the little-o remainder fails, so their existence is not differentiability.",
                          "The partial derivatives at the origin equal 1, so the second step is the one that fails.",
                          "Differentiability does not use a linear map."],
                 correct_reason=0,
                 fig=PAIR, alt=A_PAIR)
    b.num(3,
          r"Let \(f(x, y) = x^2 y\) at \((1, 1)\) with the step \((0.5, 0)\). The absolute remainder is \(0.25\). What is that remainder divided by the step length?",
          0.5, "1",
          r"The step length is \(0.5\), and \(0.25 / 0.5 = 0.5\). This quotient is what the little-o test studies. The remainder 0.25 is the numerator. The linear prediction at the shifted point is 2, and 2 divided by the step length is 4, which mixes the linear term into the quotient.",
          SLICE, A_SLICE)
    b.mc(3,
         "A function can have a directional derivative in every direction and still fail to be differentiable because",
         ["directional derivatives are never linear maps",
          "the little-o limit is allowed to depend on a choice of basis",
          "those directional derivatives may fail to come from one linear map, or the little-o limit may fail",
          "differentiability forbids directional derivatives"],
         2,
         r"Differentiability needs one linear map that reproduces every directional derivative, plus a remainder that is little-o of the step length. Directional derivatives can exist and still depend on the direction in a nonlinear way, and even a linear family of them can fail the little-o test. They are not automatically nonlinear, and differentiability does not forbid them: it implies them.",
         PAIR, A_PAIR)
    b.order(4,
            "Put these steps in the order used to test the little-o definition at a point.",
            ["Choose the candidate linear map given by the gradient inner product.",
             "Form the remainder: the shifted value, minus the function value, minus the linear map on the step.",
             "Divide that remainder by the length of the step.",
             "Require the quotient to tend to 0 as the step tends to 0."],
            r"The test needs a candidate linear map before it can form a remainder. The remainder is a numerator, and the length of the step is the denominator. The limit is the last demand. Dividing the function value itself by the step length tests a different quotient. Stopping after the partial derivatives exist skips the limit that the definition names.",
            SLICE, A_SLICE, ["taylor-approximation-multivariable"])
    b.num(4,
          r"Let \(f(x, y) = x^2 + y^2\) at the origin, where the gradient is zero. For the step \((0.2, 0)\), what is the absolute remainder of the linear approximation?",
          0.04, "1",
          r"The linear map is zero, so the remainder equals the function value \(0.04\). The step length \(0.2\) is the little-o denominator. The quotient \(0.04 / 0.2 = 0.2\) still tends to 0 if the step is replaced by a smaller multiple, which is why the origin is differentiable for this function. Using \(0.2\) itself as the remainder forgets the square.",
          SLICE, A_SLICE, ["first-order-optimality"])
    b.mc(4,
         "The first-order model used by a later convexity test is available when",
         ["the function is merely continuous",
          "partial derivatives exist at the point, whether or not the little-o limit holds",
          "the Hessian exists",
          "the function is differentiable, so the linear model has a little-o remainder"],
         3,
         r"The tangent inequality compares the function with \(f(x) + \nabla f(x)^{T}(y - x)\). That expression is the linear model from the definition of differentiability. Continuity does not provide a gradient. Partials without the little-o remainder do not make the model a first-order approximation. The Hessian is the second-order object, not the hypothesis this model needs.",
         LEVELS, A_LEVELS, ["convexity-first-order"])
    b.save()


def bank_hessian():
    b = Bank("hessian-matrix")
    b.mc(1,
         "The Hessian of a scalar function is",
         ["the matrix of second partial derivatives",
          "the column of first partial derivatives",
          "the Jacobian of an arbitrary vector-valued map",
          "the sum of the pure second partial derivatives"],
         0,
         r"Each entry is one second partial derivative: row i and column j holds the derivative of the i-th partial with respect to the j-th coordinate. The column of first partials is the gradient. A Jacobian belongs to a vector-valued map; the Hessian is the Jacobian of the gradient. The sum of the diagonal entries is the trace, one number, not the matrix.",
         HESS, A_HESS)
    b.num(1,
          r"Let \(f(x, y) = x^3 y + 2 y^2 + 5 x y\). At \((1, 2)\), what is \(\partial^2 f / \partial x^2\)?",
          12, "1",
          r"The first partial in \(x\) is \(3 x^2 y + 5 y\). Differentiating again in \(x\) gives \(6 x y\), which equals \(6 \cdot 1 \cdot 2 = 12\). The mixed partial \(3 x^2 + 5\) equals 8 at this point. The pure second partial in \(y\) is 4. The first partial in \(x\), evaluated here, is \(6 + 10 = 16\), and that is a first derivative.",
          HESS, A_HESS)
    b.mc(1,
         r"For a function with continuous second partials, the mixed entries satisfy",
         [r"\(\partial^2 f / \partial x \partial y = 0\)",
          r"\(\partial^2 f / \partial x \partial y = \partial^2 f / \partial y \partial x\)",
          r"\(\partial^2 f / \partial x \partial y = \partial f / \partial x\)",
          "the Hessian is diagonal"],
         1,
         r"Continuous second partials may be taken in either order, so the Hessian is symmetric. The mixed entry is not forced to vanish, and it is not equal to a first partial. Symmetry does not force the off-diagonal entries to be zero, so the matrix need not be diagonal.",
         HESS, A_HESS)
    b.sym(2,
          r"For \(f = a x^2 y + b x y^2\), the mixed partial \(\partial^2 f / \partial y \partial x\) is an expression in the names a, b, x, and y. Write that expression.",
          "2*a*x+2*b*y",
          {"a": (-3, 3), "b": (-3, 3), "x": (0.5, 3), "y": (0.5, 3)},
          r"The partial derivative in \(x\) is \(2 a x y + b y^2\). Differentiating that in \(y\) gives \(2 a x + 2 b y\). Differentiating first in \(y\) and then in \(x\) produces the same expression."
          "\n"
          r"• \(2 a x\) drops the second summand."
          "\n"
          r"• \(a x^2 + 2 b x y\) is a first partial, not the mixed second partial."
          "\n"
          r"• \(2 a + 2 b\) differentiates the remaining variables away.",
          ["2*(a*x+b*y)", "2*b*y+2*a*x"],
          fig=HESS, alt=A_HESS)
    b.num(2,
          r"Let \(f(x, y) = x^3 y + 2 y^2 + 5 x y\). At \((1, 2)\), what is the mixed partial \(\partial^2 f / \partial y \partial x\)?",
          8, "1",
          r"From \(3 x^2 y + 5 y\), differentiating in \(y\) gives \(3 x^2 + 5\), which equals 8 at \(x = 1\). The pure second partial in \(x\) is 12, and the pure second partial in \(y\) is 4. The product \(3 \cdot 1 + 5 \cdot 2 = 13\) treats the expression as if both factors were still present after differentiation.",
          HESS, A_HESS)
    b.num(2,
          r"At \((1, 2)\) the Hessian of \(f(x, y) = x^3 y + 2 y^2 + 5 x y\) is \(\begin{bmatrix} 12 & 8 \\ 8 & 4 \end{bmatrix}\). What is \(v^{T} H v\) for \(v = (1, 0)\)?",
          12, "1",
          r"The quadratic form on the first basis vector is the \((1, 1)\) entry, 12. The other diagonal entry is 4, which is the quadratic form on \((0, 1)\). The sum of all four entries is 32, which is the quadratic form on \((1, 1)\). The off-diagonal entry 8 does not appear in \(v^{T} H v\) when the second coordinate of \(v\) is 0.",
          HESS, A_HESS)
    b.find_error(3,
                 r"One step below is false. Select that step, and the reason it fails. The function is \(f(x, y) = x^2 y\).",
                 ["The first partial derivative with respect to x is 2 x y.",
                  "Differentiating that partial derivative with respect to y gives 2 x.",
                  "The first partial derivative with respect to y is x squared.",
                  "Differentiating x squared with respect to x gives x, so the mixed partials disagree."],
                 3,
                 r"The first three steps are the right partial derivatives: \(f_x = 2 x y\), \(f_{xy} = 2 x\), and \(f_y = x^2\). The derivative of \(x^2\) with respect to \(x\) is \(2x\), not \(x\). Both mixed partials equal \(2x\), so they agree. The false step is the differentiation, not a failure of symmetry.",
                 reasons=["The derivative of x squared is 2x, so both mixed partials equal 2x.",
                          "A polynomial is allowed to have mixed partials that disagree.",
                          "The first partial derivative with respect to x should have been x squared."],
                 correct_reason=0,
                 fig=HESS, alt=A_HESS)
    b.num(3,
          r"Using the Hessian \(\begin{bmatrix} 12 & 8 \\ 8 & 4 \end{bmatrix}\) at \((1, 2)\), what is \(v^{T} H v\) for \(v = (1, 1)\)?",
          32, "1",
          r"\(H v = (20, 12)\), and the inner product with \((1, 1)\) is \(20 + 12 = 32\). The same total is \(12 + 8 + 8 + 4\). The trace is \(12 + 4 = 16\), which drops the off-diagonal contributions. The determinant is \(48 - 64 = -16\), a different summary of the matrix.",
          HESS, A_HESS)
    b.mc(3,
         r"The second derivative of \(t \mapsto f(x + t d)\), at \(t = 0\), equals",
         [r"\(\nabla f(x)^{T} d\)",
          r"the trace of the Hessian",
          r"\(d^{T} H_f(x)\, d\)",
          r"\(\lVert H_f(x)\, d \rVert\)"],
         2,
         r"The first derivative of the slice is the gradient dotted with \(d\). Differentiating again brings down the Hessian and leaves the quadratic form \(d^{T} H d\). The trace sums curvatures in the coordinate directions, not in the direction \(d\). The length of \(H d\) is not the second derivative of the slice.",
         SLICE, A_SLICE)
    b.multi(4,
            "Which statements hold for the Hessian?",
            ["When the second partial derivatives are continuous, the Hessian is symmetric.",
             r"The second derivative of the slice \(t \mapsto f(x + t d)\) at 0 is \(d^{T} H d\), when \(H\) exists and is continuous.",
             "The Hessian of a linear function is the identity.",
             "Mixed partials are equal at a point whenever both of them exist there, with no extra hypothesis."],
            [0, 1],
            r"Continuous second partials commute, so the matrix is symmetric, and the slice's second derivative is the quadratic form of that matrix. A linear function has second partials equal to 0, so its Hessian is the zero matrix, not the identity. Equality of mixed partials can fail if the partials exist at a point but are not continuous nearby, so existence alone is not the hypothesis.",
            HESS, A_HESS, ["taylor-approximation-multivariable"])
    b.num(4,
          r"For the Hessian \(\begin{bmatrix} 12 & 8 \\ 8 & 4 \end{bmatrix}\), what is the determinant?",
          -16, "1",
          r"The determinant is \(12 \cdot 4 - 8 \cdot 8 = 48 - 64 = -16\). The product of the diagonal entries is 48, which forgets to subtract the off-diagonal product. The trace is 16. A negative determinant means the two eigenvalues have opposite signs, so the quadratic form is indefinite. The sign is part of the value.",
          HESS, A_HESS, ["matrix-calculus-gradients"])
    b.mc(4,
         "Along a segment, an increment of the gradient can be written with the Hessian because",
         ["the gradient is constant on every segment",
          "the Hessian is always a multiple of the identity",
          "the chain rule differentiates the gradient along the segment and produces the Hessian times the direction",
          "second derivatives do not depend on the point"],
         2,
         r"The fundamental theorem along a segment integrates a derivative. Applied to the gradient, that derivative is the Hessian times the direction of the segment. The gradient is constant only when the Hessian is zero. The Hessian need not be a multiple of the identity, and it is evaluated along the segment, so it can change with the point.",
         SEG, A_SEG, ["fundamental-theorem-along-segment"])
    b.save()


def bank_jacobian():
    b = Bank("jacobian-chain-rule")
    b.mc(1,
         r"For a map \(F\) with \(m\) outputs and \(n\) inputs, the Jacobian is",
         [r"the \(m \times n\) matrix of partial derivatives \(\partial F_i / \partial x_j\)",
          r"the \(n \times m\) matrix with those partials transposed, by definition",
          "the Hessian of each output, stacked in a row",
          "the sum of the output components"],
         0,
         r"Rows correspond to outputs and columns to inputs, so the shape is \(m \times n\). The transpose is a different arrangement and is not the definition used here. Each output has its own gradient, which becomes one row; the Hessian of an output is a further derivative. Adding the components collapses the map to a scalar.",
         JAC, A_JAC)
    b.num(1,
          r"Let \(F(x, y) = (x y,\ x + 2y)\). At \((3, 5)\), what is the \((1, 2)\) entry of the Jacobian?",
          3, "1",
          r"The first output is \(x y\), and its partial derivative in \(y\) is \(x\), which equals 3. The \((1, 1)\) entry is \(y = 5\). The \((2, 1)\) entry is 1, and the \((2, 2)\) entry is 2. The product \(3 \cdot 5 = 15\) is the first output, not a partial derivative.",
          JAC, A_JAC)
    b.mc(1,
         r"The chain rule for \(F \circ G\) says that the Jacobian of the composition is",
         [r"the sum of the two Jacobians",
          r"the Jacobian of \(F\), evaluated at \(G(x)\), times the Jacobian of \(G\) at \(x\)",
          r"the Jacobian of \(G\) times the Jacobian of \(F\), with \(F\) evaluated at \(x\)",
          r"the entrywise product of the two Jacobians"],
         1,
         r"The outer derivative is taken at the inner value, and it stands on the left of the product. Adding Jacobians is the rule for a sum of maps. Swapping the order, or evaluating the outer map at \(x\) instead of at \(G(x)\), uses the wrong point and the wrong multiplication. An entrywise product is not matrix multiplication.",
         JAC, A_JAC)
    b.order(2,
            "Put these steps in the order used to apply the chain rule.",
            ["Evaluate the inner map at the input point.",
             "Build the outer Jacobian at that image.",
             "Build the inner Jacobian at the input point.",
             "Multiply the outer Jacobian by the inner Jacobian."],
            r"The outer Jacobian cannot be evaluated until the image is known, so the inner value comes first and the outer Jacobian comes next. The inner Jacobian uses the original input. The product is last, with the outer factor on the left. Swapping the factors computes a different matrix whenever the sizes differ. Adding the factors is the rule for a sum, not a composition.",
            JAC, A_JAC)
    b.num(2,
          r"Let \(g(t) = (t^2, 3t)\) and \(f(x, y) = x + y^2\). What is the derivative of \(f(g(t))\) at \(t = 2\)?",
          40, "1",
          r"The image is \((4, 6)\), and \(g'(2) = (4, 3)\). The gradient of \(f\) is \((1, 2y)\), so at the image it is \((1, 12)\). The inner product is \(4 + 36 = 40\). The simplified composition is \(t^2 + 9 t^2 = 10 t^2\), whose derivative \(20 t\) also equals 40 at \(t = 2\). The value of the composition, \(10 \cdot 4 = 40\), matches the derivative here and is not the general rule; at a different \(t\) the two numbers separate.",
          SLICE, A_SLICE)
    b.num(2,
          r"The Jacobian of \(F(x, y) = (x y,\ x + 2y)\) at \((3, 5)\) is \(\begin{bmatrix} 5 & 3 \\ 1 & 2 \end{bmatrix}\). What is its determinant?",
          7, "1",
          r"The determinant is \(5 \cdot 2 - 3 \cdot 1 = 7\). The product of the diagonal entries is 10, which does not subtract the other product. The sum of the four entries is 11. The trace is 7 as well for this particular matrix, but the trace is \(5 + 2\), a different operation that happens to match. The determinant formula is the one with the minus sign.",
          JAC, A_JAC)
    b.sym(3,
          r"Let \(f(x, y) = x + y\). The derivative of \(t \mapsto f(a t,\ b t^2)\) is an expression in the names a, b, and t. Write that expression.",
          "a+2*b*t",
          {"a": (-3, 3), "b": (-3, 3), "t": (0.4, 3)},
          r"The inner velocity is \((a, 2 b t)\). The gradient of \(x + y\) is \((1, 1)\). Their inner product is \(a + 2 b t\). The composed function is \(a t + b t^2\), and ordinary differentiation gives the same expression."
          "\n"
          r"• \(a + b t\) misses the 2 from differentiating \(t^2\)."
          "\n"
          r"• \(a t + b t^2\) is the composed function, not its derivative."
          "\n"
          r"• \(2 b t\) drops the contribution of the first coordinate.",
          ["2*b*t+a", "a+(2*b)*t"],
          fig=SLICE, alt=A_SLICE)
    b.num(3,
          r"Using \(J = \begin{bmatrix} 5 & 3 \\ 1 & 2 \end{bmatrix}\), what is the first entry of \(J \begin{bmatrix} 2 \\ 1 \end{bmatrix}\)?",
          13, "1",
          r"The first row dotted with \((2, 1)\) is \(5 \cdot 2 + 3 \cdot 1 = 13\). The second entry of the product is \(1 \cdot 2 + 2 \cdot 1 = 4\). The sum of the first row is 8, which is the product with \((1, 1)\) rather than with \((2, 1)\). The determinant 7 is not an entry of this product.",
          JAC, A_JAC)
    b.mc(3,
         r"If \(f\) is scalar and \(g\) is vector-valued, \(\nabla (f \circ g)(x)\) equals",
         [r"\(J_g(x)\, \nabla f(g(x))\), with no transpose",
          r"\(\nabla f(x)\), ignoring \(g\)",
          r"\(J_g(x)^{T} \nabla f(g(x))\)",
          r"\(J_g(x)^{T} \nabla f(x)\)"],
         2,
         r"The Jacobian of a scalar is a row, and the gradient is that row written as a column. The chain rule therefore puts the transpose of \(J_g\) against the gradient of \(f\), and the gradient of \(f\) is evaluated at \(g(x)\). Without the transpose the shapes disagree when the dimensions differ. Evaluating \(\nabla f\) at \(x\) uses the wrong point.",
         PAIR, A_PAIR)
    b.multi(4,
            "Which statements hold for the Jacobian and the chain rule?",
            [r"The Jacobian of \(F \circ G\) at \(x\) is \(J_F(G(x))\) times \(J_G(x)\).",
             r"The gradient of a scalar composition \(f \circ g\) is \(J_g(x)^{T}\) times the gradient of \(f\) at \(g(x)\).",
             "Jacobians add when the maps are composed.",
             "The chain rule evaluates the outer Jacobian at the original input, not at the image."],
            [0, 1],
            r"Composition multiplies Jacobians, outer at the image on the left. For a scalar outer function the same rule, written with columns, puts a transpose on the inner Jacobian. A sum of maps is what adds Jacobians. The outer factor has to see the point where the outer function is actually being differentiated, which is the image.",
            JAC, A_JAC, ["matrix-calculus-gradients"])
    b.num(4,
          r"Let \(f(x, y) = x + y^2\) and let the path be \((u, 2u)\). What is the derivative of the composition at \(u = 3\)?",
          25, "1",
          r"The image is \((3, 6)\). The path velocity is \((1, 2)\), and the gradient of \(f\) there is \((1, 12)\). The inner product is \(1 + 24 = 25\). The composed function is \(u + 4 u^2\), with derivative \(1 + 8u\), which also equals 25 at \(u = 3\). The value of the composition is \(3 + 36 = 39\), not the slope. Twice the second coordinate, 12, is only the second entry of the gradient.",
          SLICE, A_SLICE, ["computational-graphs"])
    b.mc(4,
         "Newton's method for a square nonlinear system linearizes the map by",
         ["replacing the map with its Hessian",
          "replacing the map with the constant vector F(x)",
          "ignoring the Jacobian and stepping along a coordinate axis",
          "replacing the map with its affine model F(x) + J(x) (z - x)"],
         3,
         r"One Newton step solves the linear equation given by the value and the Jacobian. The Hessian is the derivative of the Jacobian, used when the unknown is a minimizer of a scalar function rather than a root of a map. Holding the value and dropping the Jacobian leaves a constant, which has no root to compute unless it is already zero. A coordinate step is a different algorithm.",
         JAC, A_JAC, ["newton-root-finding"])
    b.save()


def bank_matrix():
    b = Bank("matrix-calculus-gradients")
    b.mc(1,
         r"The gradient of \(c^{T} x\), with \(c\) constant, is",
         [r"the vector \(c\)",
          r"the scalar \(c^{T} x\)",
          "the zero vector",
          r"the matrix with \(c\) on the diagonal"],
         0,
         r"Each coordinate derivative of a linear form is the matching entry of \(c\), so the gradient is \(c\). The scalar \(c^{T} x\) is the function value. The gradient is zero only when \(c\) is zero. A diagonal matrix would be a Hessian-sized object; the Hessian of a linear form is the zero matrix.",
         QUAD, A_QUAD)
    b.num(1,
          r"Let \(A = \begin{bmatrix} 1 & 3 \\ 0 & 2 \end{bmatrix}\) and \(f(x) = x^{T} A x\). At \(x = (1, 1)\), what is the first entry of \(\nabla f\)?",
          5, "1",
          r"Expanding gives \(x_1^2 + 3 x_1 x_2 + 2 x_2^2\). The partial derivative in \(x_1\) is \(2 x_1 + 3 x_2\), which equals 5 at \((1, 1)\). The formula \((A + A^{T}) x\) gives the same vector \((5, 7)\). Using \(2 A x\) instead, as if \(A\) were symmetric, gives \((10, 6)\), and the first entry of that vector is 10.",
          QUAD, A_QUAD)
    b.mc(1,
         r"For a square \(A\) that is not assumed symmetric, \(\nabla (x^{T} A x)\) equals",
         [r"\(2 A x\)",
          r"\((A + A^{T}) x\)",
          r"\(A x\)",
          r"\(A^{T} A x\)"],
         1,
         r"Differentiating the sum \(\sum_{ij} a_{ij} x_i x_j\) hits each factor once, which produces \(A x\) from one order and \(A^{T} x\) from the other. The factor \(2 A x\) is the special case \(A = A^{T}\). Using \(A x\) alone drops the transpose term. The product \(A^{T} A\) appears in a squared residual, not in \(x^{T} A x\).",
         QUAD, A_QUAD)
    b.sym(2,
          r"Let \(A = \begin{bmatrix} p & q \\ r & s \end{bmatrix}\). The partial derivative of \(x^{T} A x\) with respect to the first coordinate is an expression in the names p, q, r, x, and y, where \(x\) and \(y\) are the two coordinates. Write that expression.",
          "2*p*x+(q+r)*y",
          {"p": (-2, 2), "q": (-2, 2), "r": (-2, 2), "x": (0.5, 2.5), "y": (0.5, 2.5)},
          r"The quadratic is \(p x^2 + (q + r) x y + s y^2\). Differentiating in \(x\) gives \(2 p x + (q + r) y\). The diagonal entry \(s\) multiplies \(y^2\) only, so it does not appear in this partial derivative."
          "\n"
          r"• \(2 p x + q y\) keeps only one of the two off-diagonal contributions."
          "\n"
          r"• \(2 p x + 2 q y\) is the symmetric formula, and it is wrong when \(r\) is not equal to \(q\)."
          "\n"
          r"• \(p x + (q + r) y\) misses the 2 on the square.",
          ["2*p*x+q*y+r*y", "(2*p)*x+(q+r)*y"],
          fig=QUAD, alt=A_QUAD)
    b.num(2,
          r"Let \(A = \begin{bmatrix} 1 & 3 \\ 0 & 2 \end{bmatrix}\) and \(f(x) = x^{T} A x\). At \(x = (1, 1)\), what is the second entry of \(\nabla f\)?",
          7, "1",
          r"The partial derivative in the second coordinate is \(3 x_1 + 4 x_2\), which equals 7. It is the second entry of \((A + A^{T}) x\). The first entry is 5. The second entry of \(2 A x\) is 6, which is the symmetric-formula mistake. The function value is \(1 + 3 + 2 = 6\), not a partial derivative.",
          QUAD, A_QUAD)
    b.num(2,
          r"Let \(A = \begin{bmatrix} 1 & 0 \\ 2 & 1 \end{bmatrix}\), \(b = (1, 0)\), and \(x = (2, 1)\). For \(f(x) = \lVert A x - b \rVert^2\), what is the first entry of \(\nabla f\)?",
          22, "1",
          r"\(A x - b = (1, 5)\). Then \(A^{T}(A x - b) = (11, 5)\), and the gradient is twice that vector, so the first entry is 22. The residual sum of squares is \(1 + 25 = 26\), which is the function value. The second entry of the gradient is 10. Using \(A\) instead of \(A^{T}\) on the residual produces \((1, 7)\), and twice the first entry of that vector is 2.",
          QUAD, A_QUAD)
    b.order(3,
            r"Put these steps in the order used to differentiate \(x^{T} A x\) in coordinates.",
            ["Write the form as a sum of a_ij x_i x_j over both indices.",
             "Differentiate that sum with respect to one coordinate x_k.",
             "Separate the hits on the left factor from the hits on the right factor.",
             "Read the two groups as the matching entries of A x and of A transpose x."],
            r"The sum is the object being differentiated, so it comes first. Differentiation in one coordinate is next. The product rule splits into two groups, and only then can those groups be recognized as \(A x\) and \(A^{T} x\). Starting from \(2 A x\) skips the split and is valid only after \(A\) has been replaced by its symmetric part.",
            QUAD, A_QUAD)
    b.num(3,
          r"For \(A = \begin{bmatrix} 1 & 3 \\ 0 & 2 \end{bmatrix}\), the Hessian of \(x^{T} A x\) is \(A + A^{T}\). What is the \((1, 2)\) entry of that Hessian?",
          3, "1",
          r"\(A + A^{T} = \begin{bmatrix} 2 & 3 \\ 3 & 4 \end{bmatrix}\), so the off-diagonal entry is \(3 + 0 = 3\). Twice the off-diagonal entry of \(A\) is 6, which would be right only if the other off-diagonal entry were also 3. The \((2, 2)\) entry of the Hessian is 4. The \((1, 1)\) entry is 2.",
          QUAD, A_QUAD)
    b.mc(3,
         r"The gradient of \(\lVert x \rVert^2\) is",
         [r"\(x\)",
          r"\(\lVert x \rVert\)",
          r"\(2x\)",
          r"\(x x^{T}\)" ],
         2,
         r"The squared Euclidean length is \(x^{T} x\), and the symmetric-formula gives \(2x\). The vector \(x\) misses the factor 2. The length \(\lVert x \rVert\) is a different function, whose gradient is the unit vector where \(x \ne 0\). The outer product \(x x^{T}\) is a matrix, not the gradient.",
         PAIR, A_PAIR)
    b.find_error(4,
                 r"One step below is false. Select that step, and the reason it fails. Let \(A = \begin{bmatrix} 1 & 4 \\ 0 & 3 \end{bmatrix}\).",
                 ["Let f(x) = x transpose A x.",
                  "A is not symmetric, because its off-diagonal entries are 4 and 0.",
                  "The gradient of x transpose A x is 2 A x for every real square A.",
                  "At x = (1, 1), that formula produces the vector (10, 6)."],
                 2,
                 r"The matrix really is nonsymmetric, and \(2 A (1, 1) = 2(5, 3) = (10, 6)\), so the last step only evaluates the formula above it. The false step is the formula. The gradient is \((A + A^{T}) x\). Here \(A + A^{T} = \begin{bmatrix} 2 & 4 \\ 4 & 6 \end{bmatrix}\), and the product with \((1, 1)\) is \((6, 10)\).",
                 reasons=["The gradient is (A + A transpose) x. The formula 2 A x needs A to be symmetric.",
                          "The matrix is symmetric, so the comparison of off-diagonal entries is the false step.",
                          "The gradient is A x, with no factor 2 and no transpose."],
                 correct_reason=0,
                 fig=QUAD, alt=A_QUAD, preview=["quadratic-function-minimization"])
    b.num(4,
          r"At \(x = (3, 4)\), what is the first entry of the gradient of \(\lVert x \rVert^2\)?",
          6, "1",
          r"The gradient is \(2x\), so the first entry is \(2 \cdot 3 = 6\). The coordinate 3 itself misses the factor 2. The second entry is 8. The function value is \(9 + 16 = 25\). Half of 6 is the coordinate, not the partial derivative.",
          PAIR, A_PAIR, ["convexity-second-order"])
    b.mc(4,
         r"A quadratic \(f(x) = \tfrac12 x^{T} A x + b^{T} x\) with symmetric \(A\) has gradient",
         [r"\(\tfrac12 A x + b\)",
          r"\(A x + b\)",
          r"\(x^{T} A + b^{T}\), kept as a row",
          r"\(A + b\)"],
         1,
         r"The factor one half cancels the 2 from differentiating \(x^{T} A x\) when \(A\) is symmetric, and the linear term contributes \(b\). Leaving the one half in front of \(A x\) double-counts the cancellation. A row is the Jacobian layout, not the column gradient used here. Adding the matrix \(A\) to the vector \(b\) is not a defined gradient.",
         QUAD, A_QUAD, ["quadratic-function-minimization"])
    b.save()


def bank_ftc():
    b = Bank("fundamental-theorem-along-segment")
    b.mc(1,
         r"For a differentiable \(f\), the increment \(f(y) - f(x)\) equals",
         [r"the integral from 0 to 1 of \(\nabla f(x + t(y - x))^{T}(y - x)\, dt\)",
          r"the gradient at \(x\), with no integral",
          r"the integral of \(f\) itself along the segment",
          r"the value of \(f\) at the midpoint"],
         0,
         r"Restrict \(f\) to the segment, apply the chain rule, and integrate the resulting ordinary derivative. The integrand is the moving gradient dotted with the fixed direction \(y - x\). The gradient at the single point \(x\) is the first-order approximation, not the exact increment. Integrating \(f\) itself, or reading the midpoint, answers a different question.",
         SEG, A_SEG)
    b.num(1,
          r"Let \(f(x, y) = x^2 + 3y\). What is \(f(2, 1) - f(0, 0)\)?",
          7, "1",
          r"\(f(2, 1) = 4 + 3 = 7\) and \(f(0, 0) = 0\), so the increment is 7. The same number is the integral of \(\nabla f \cdot (2, 1)\) along the segment. The gradient at the end is \((4, 3)\), and its first entry 4 is not the increment. The direction's first coordinate is 2.",
          SEG, A_SEG)
    b.mc(1,
         "The same theorem applied to the gradient says that",
         [r"\(\nabla f(y) - \nabla f(x)\) is the integral of the Hessian times \((y - x)\)",
          r"the Hessian is the integral of the gradient",
          "the gradient increment equals the function increment",
          "the integral reduces to a difference only on a coordinate axis"],
         0,
         r"Each component of the gradient is a scalar function, so the segment theorem applies to it. The derivative of the gradient is the Hessian, and the chain rule multiplies that Hessian by the direction. The Hessian is not an integral of the gradient. A gradient increment and a function increment have different shapes. The parametrization works for every segment, not only axis-aligned ones.",
         SEG, A_SEG)
    b.order(2,
            "Put these steps in the order used to prove the segment form of the fundamental theorem.",
            ["Parametrize the segment by x + t (y - x), with t from 0 to 1.",
             "Restrict f to that parametrization.",
             "Differentiate the restriction by the chain rule.",
             "Integrate that derivative from 0 to 1."],
            r"The parametrization creates an ordinary function of one variable. The restriction names that function, the chain rule differentiates it, and the one-variable fundamental theorem integrates the derivative back to the increment. Integrating before differentiating has nothing to integrate yet. Using a gradient at the endpoints only, with no integral, is the mean-value shortcut rather than this identity.",
            SEG, A_SEG)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 3y\). The gradient difference \(\nabla f(2, 1) - \nabla f(0, 0)\) has first entry",
          4, "1",
          r"The gradient is \((2x, 3)\). At \((2, 1)\) it is \((4, 3)\), and at the origin it is \((0, 3)\). The difference is \((4, 0)\), so the first entry is 4. The function increment is 7. The second entry of the gradient difference is 0 because the second partial derivative is constant. The product \(2 \cdot 2 = 4\) matches the first entry and is the derivative of \(x^2\).",
          SEG, A_SEG)
    b.num(2,
          r"For \(f(x, y) = x^2 + 3y\), on the segment from \((0, 0)\) to \((2, 1)\), what is the integrand \(\nabla f^{T}(y - x)\) at \(t = 0\)?",
          3, "1",
          r"At \(t = 0\) the point is the origin, the gradient is \((0, 3)\), and the direction is \((2, 1)\). The inner product is 3. At \(t = 1\) the integrand is \((4, 3) \cdot (2, 1) = 11\). The integral of the whole integrand is the function increment 7, which sits between 3 and 11. The first coordinate of the direction is 2.",
          SEG, A_SEG)
    b.sym(3,
          r"Let \(f(u) = a u^2\) on the line. The increment from \(0\) to \(b\) is an expression in the names a and b. Write that expression.",
          "a*b^2",
          {"a": (-3, 3), "b": (0.5, 3)},
          r"\(f(b) - f(0) = a b^2\). The gradient is \(2 a u\), and the direction of the segment is \(b\). Integrating \(2 a (t b)\, b\) from 0 to 1 gives \(2 a b^2 \int_0^1 t\, dt = a b^2\)."
          "\n"
          r"• \(2 a b\) is the derivative at the right endpoint, not the increment."
          "\n"
          r"• \(a b\) misses one factor of \(b\)."
          "\n"
          r"• \(2 a b^2\) stops before the integral of \(t\) supplies the factor one half.",
          ["a*(b*b)", "(a*b)*b"],
          fig=SLICE, alt=A_SLICE)
    b.num(3,
          r"Let \(\phi(s) = s^2\). What is \(\phi(4) - \phi(1)\)?",
          15, "1",
          r"\(16 - 1 = 15\). The derivative is \(2s\), and the segment from 1 to 4 has direction 3, so the integrand is \(2(1 + 3t) \cdot 3 = 6 + 18 t\). Integrating from 0 to 1 gives \(6 + 9 = 15\). The length of the segment is 3. The derivative at the right end is 8.",
          SLICE, A_SLICE)
    b.mc(3,
         "The integral identity for the function increment requires",
         ["the Hessian at every point of the segment",
          "the function to be constant",
          "a gradient that exists along the segment and is continuous enough to integrate",
          "the two endpoints to be equal"],
         2,
         r"The proof differentiates the restriction, so the gradient has to exist along the segment, and it has to be nice enough that the one-variable fundamental theorem applies. The Hessian is the extra ingredient for a gradient increment, not for a function increment. A constant function makes the identity trivial, and it is not a hypothesis. Equal endpoints make both sides zero.",
         SEG, A_SEG)
    b.multi(4,
            "Which statements hold when the derivatives in question exist and are continuous on the segment?",
            [r"\(f(y) - f(x)\) equals the integral of \(\nabla f(x + t(y - x))^{T}(y - x)\) from 0 to 1.",
             r"\(\nabla f(y) - \nabla f(x)\) equals the integral of \(H_f(x + t(y - x))\,(y - x)\) from 0 to 1.",
             "The integrand is constant whenever the function is not linear.",
             "The identity requires the segment to be parallel to a coordinate axis."],
            [0, 1],
            r"Both identities are the ordinary fundamental theorem on the parametrized segment, once for \(f\) and once for each component of the gradient. The integrand is constant when the differentiated object is linear, not when it fails to be linear. The parametrization \(x + t(y - x)\) covers every segment.",
            SEG, A_SEG, ["taylor-exact-mean-value"])
    b.num(4,
          r"Let \(f(x, y) = x^2 + y^2\). The difference \(\nabla f(3, 1) - \nabla f(1, 0)\) has second entry",
          2, "1",
          r"The gradient is \((2x, 2y)\). At \((3, 1)\) it is \((6, 2)\), and at \((1, 0)\) it is \((2, 0)\). The difference is \((4, 2)\), so the second entry is 2. The first entry of the difference is 4. The function increment is \(10 - 1 = 9\). Twice the second coordinate of the end point is 2, which matches because the start had second coordinate 0.",
          SEG, A_SEG, ["lipschitz-gradient"])
    b.mc(4,
         "A secant equation for a Hessian approximation uses this theorem by",
         ["setting the Hessian equal to the identity",
          "replacing the gradient increment by the function increment",
          "ignoring the step and matching function values only",
          "asking the model Hessian to reproduce the integrated gradient change along the step"],
         3,
         r"Integrating \(H (y - x)\) along the segment produces \(\nabla f(y) - \nabla f(x)\). A quasi-Newton update chooses a matrix that matches that identity when the integrand is replaced by a constant matrix. The identity matrix matches it only for a quadratic with that Hessian. The function increment is the scalar identity, not the gradient identity. Function values alone do not determine the secant.",
         SEG, A_SEG, ["quasi-newton-secant"])
    b.save()


def bank_taylor():
    b = Bank("taylor-approximation-multivariable")
    b.mc(1,
         r"The first-order Taylor model at \(x\) is",
         [r"\(f(x) + \nabla f(x)^{T}(y - x)\)",
          r"\(f(y)\)",
          r"\(\nabla f(x)\)",
          r"\(f(x) + \tfrac12 (y - x)^{T} H(x)\, (y - x)\)"],
         0,
         r"The model copies the value and the directional slopes at \(x\). It is a function of the new point \(y\), not the number \(f(y)\), which is what the model is trying to approximate. The gradient alone is not the model. The quadratic term belongs to the second-order model; the first-order model stops before it.",
         LEVELS, A_LEVELS)
    b.num(1,
          r"Let \(f(x, y) = x^3 + 2 x y\). At \((1, 1)\), with step \((1, -1)\), what is the first-order Taylor model?",
          6, "1",
          r"\(f(1, 1) = 3\) and \(\nabla f(1, 1) = (5, 2)\). The linear term is \(5 - 2 = 3\), so the model is \(3 + 3 = 6\). The function value at the new point \((2, 0)\) is 8. The quadratic term is 1, and the second-order model is 7. The gradient's first entry, 5, is not the model.",
          LEVELS, A_LEVELS)
    b.mc(1,
         "The second-order model adds, on top of the linear model,",
         [r"another copy of the linear term",
          r"\(\tfrac12 (y - x)^{T} H_f(x)\, (y - x)\)",
          r"\((y - x)^{T} H_f(x)\, (y - x)\), with no one half",
          r"the Hessian itself, as a matrix-valued answer"],
         1,
         r"The quadratic term carries the factor one half so that a further differentiation recovers the Hessian. Doubling the linear term is not that correction. Dropping the one half doubles the quadratic contribution. The model is scalar, like \(f\); the Hessian is the coefficient, not the value of the model.",
         ELL, A_ELL)
    b.sym(2,
          r"Suppose the Hessian is \(2a\) times the identity and the step is \((u, v)\). The quadratic term \(\tfrac12 h^{T} H h\) is an expression in the names a, u, and v. Write that expression.",
          "a*(u^2+v^2)",
          {"a": (0.3, 3), "u": (-2.5, 2.5), "v": (-2.5, 2.5)},
          r"The quadratic form \(h^{T} H h\) equals \(2a(u^2 + v^2)\). The factor one half cancels the 2, leaving \(a(u^2 + v^2)\)."
          "\n"
          r"• \(2a(u^2 + v^2)\) forgets the one half."
          "\n"
          r"• \(a(u + v)^2\) expands into cross terms the diagonal Hessian does not have."
          "\n"
          r"• \(a(u^2 + v^2)/2\) applies the one half a second time.",
          ["a*u^2+a*v^2", "(a)*(u^2+v^2)"],
          fig=ELL, alt=A_ELL)
    b.num(2,
          r"For \(f(x, y) = x^3 + 2 x y\) at \((1, 1)\) with step \((1, -1)\), what is the second-order Taylor model?",
          7, "1",
          r"The linear model is 6. The Hessian is \(\begin{bmatrix} 6 & 2 \\ 2 & 0 \end{bmatrix}\), and \(H h = (4, 2)\). Then \(h^{T} H h = 2\), and half of that is 1. The second-order model is \(6 + 1 = 7\). The true value at \((2, 0)\) is 8. The linear model 6 drops the quadratic term. Twice the quadratic term, added to 6, would be 8 and would have omitted the one half.",
          ELL, A_ELL)
    b.num(2,
          r"For the same \(f\), point, and step, the true value at the new point is 8 and the first-order model is 6. What is the absolute linear error?",
          2, "1",
          r"The absolute difference is \(\lvert 8 - 6 \rvert = 2\). The second-order model is 7, so its absolute error is 1. The quadratic term itself is 1, which is not the linear error. The true value 8 still includes every term of the function.",
          LEVELS, A_LEVELS)
    b.order(3,
            "Put these steps in the order the second-order model is built, from the constant term through the quadratic term.",
            ["Fix the expansion point and the step that leaves it.",
             "Take the function value at the expansion point as the constant term.",
             "Add the gradient at that point, dotted with the step.",
             "Add one half of the Hessian quadratic form at that point."],
            r"The model is written constant term, then linear term, then quadratic term, all of them evaluated at the expansion point. The step has to be chosen before it can be dotted with the gradient. The Hessian term comes last because it is the second-order correction. Evaluating the Hessian at the new point instead of the expansion point is a different expansion.",
            ELL, A_ELL)
    b.num(3,
          r"For \(f(x, y) = x^3 + 2 x y\) at \((1, 1)\) with step \((1, -1)\), what is the quadratic term \(\tfrac12 h^{T} H h\)?",
          1, "1",
          r"\(H h = (4, 2)\) and \(h^{T} H h = 2\). Half of 2 is 1. The full quadratic form, without the one half, is 2, and that 2 is also the absolute linear error for this step. The linear term is 3. Adding the quadratic term to the linear model produces 7, which is the whole model rather than the quadratic term.",
          ELL, A_ELL)
    b.mc(3,
         r"As the step \(h\) tends to 0, the error of the second-order model is",
         [r"proportional to \(\lVert h \rVert\), in general",
          r"equal to the linear term",
          r"\(o(\lVert h \rVert^2)\) when the second derivatives are continuous",
          r"independent of \(h\)"],
         2,
         r"Matching value, gradient, and Hessian cancels the terms through order 2, so the error is little-o of the squared length. An error proportional to the length is what a constant approximation can leave. The linear term is part of the model, not the error. The error depends on the step; a bound that ignores the step cannot hold for every step unless the function is a quadratic of degree at most 2 and the model is exact.",
         SLICE, A_SLICE)
    b.multi(4,
            "Which statements hold for these models?",
            [r"The first-order model is \(f(x) + \nabla f(x)^{T}(y - x)\).",
             r"The second-order model adds \(\tfrac12 (y - x)^{T} H_f(x)\, (y - x)\).",
             "The linear-model error is always smaller than the quadratic-model error.",
             "Dropping the one half leaves the quadratic term unchanged."],
            [0, 1],
            r"Those two displays are the models. The quadratic model uses one more derivative, but a particular step can still make its numerical error larger; the little-o statement is about small steps, not about every comparison of two numbers. Dropping the one half doubles the quadratic term, because the Hessian quadratic form is exactly twice the term that belongs in the model.",
            ELL, A_ELL, ["taylor-exact-mean-value"])
    b.num(4,
          r"For \(f(x, y) = x^3 + 2 x y\), what is \(f(2, 0)\)?",
          8, "1",
          r"\(2^3 + 2 \cdot 2 \cdot 0 = 8\). This is the value the models were approximating. The first-order model is 6 and the second-order model is 7. The linear error is 2 and the quadratic-term contribution is 1. None of those model numbers is the function value.",
          LEVELS, A_LEVELS, ["newton-method-optimization"])
    b.mc(4,
         "A backtracking line search uses the linear model to",
         ["require the step to increase the function",
          "replace the function by its Hessian",
          "accept any positive step without a test",
          "demand that the actual decrease be at least a fraction of the linear prediction"],
         3,
         r"The linear prediction along a descent direction is negative. An Armijo test asks the true decrease to cover a fixed fraction of that predicted decrease. An increase would be the opposite demand. The Hessian enters a quadratic model, not this first-order test. Accepting every positive step needs no model at all.",
         SLICE, A_SLICE, ["armijo-backtracking"])
    b.save()


def bank_exact():
    b = Bank("taylor-exact-mean-value")
    b.mc(1,
         "The mean value theorem on a segment says that",
         [r"\(f(y) - f(x) = \nabla f(z)^{T}(y - x)\) for some \(z\) strictly between \(x\) and \(y\)",
          r"the same identity with \(z\) always equal to \(x\)",
          r"the same identity with \(z\) always equal to the midpoint",
          "the increment equals the Hessian quadratic form"],
         0,
         r"There is at least one intermediate point where the gradient matches the secant. The endpoint \(x\) works for every pair only when \(f\) is linear. The midpoint is one candidate, not the point the theorem guarantees. The Hessian quadratic form is the second-order exact term, not the first-order mean value identity.",
         SEG, A_SEG)
    b.num(1,
          r"Let \(f(t) = t^3\) on the segment from 0 to 2. The mean value theorem supplies a point where \(f'(z)\) equals the secant slope. What is that slope \(f'(z)\)?",
          4, "1",
          r"The increment is \(8 - 0 = 8\) and the length is 2, so the secant slope is 4. Thus \(f'(z) = 3z^2 = 4\). The increment 8 is not the slope. The second derivative at the right end is \(6 \cdot 2 = 12\). The length 2 is the denominator of the secant.",
          SLICE, A_SLICE)
    b.mc(1,
         "The exact second-order expansion places the Hessian",
         ["at the expansion point, with no remainder",
          "at an intermediate point of the segment",
          "at the far endpoint only",
          "at the origin, regardless of the segment"],
         1,
         r"The second-order form with an intermediate Hessian is an identity, not an approximation. Evaluating the Hessian at the expansion point produces the Taylor model, whose error is not zero in general. The far endpoint is not the point the identity names. The origin is relevant only when the segment happens to put the intermediate point there.",
         SEG, A_SEG)
    b.order(2,
            "Put these steps in the order used to turn the exact expansion into a remainder bound.",
            ["Start from the exact second-order expansion, with the Hessian at an intermediate point.",
             "Subtract the first-order model, leaving one half of a quadratic form.",
             "Bound that quadratic form using a number M that bounds the Hessian.",
             "Conclude that the absolute remainder is at most (M/2) times the squared step length."],
            r"The identity comes first. Subtracting the linear model isolates the quadratic term. The norm bound on the Hessian replaces the unknown intermediate matrix, and the factor one half stays in front of \(M \lVert h \rVert^2\). Using \(M\) without the one half doubles the bound. Bounding by the smallest eigenvalue instead of an upper bound on the Hessian can point the inequality the wrong way.",
            SEG, A_SEG)
    b.num(2,
          r"Let \(f(t) = t^3\) on \([0, 2]\). Suppose \(\lvert f''(t) \rvert \le 12\) on this segment. For the linear model at 0, what is the remainder bound \((M/2) h^2\) with \(M = 12\) and \(h = 2\)?",
          24, "1",
          r"\((12 / 2) \cdot 4 = 24\). The actual increment is 8, which is inside the bound. The product \(M \cdot h = 24\) matches this number and is not the formula; \(M \cdot h^2 = 48\) forgets the one half, and \((M/2) \cdot h = 12\) forgets the square. The secant slope 4 is the mean-value derivative, not the bound.",
          SLICE, A_SLICE)
    b.num(2,
          r"On \([0, 2]\), \(\lvert f''(t) \rvert\) for \(f(t) = t^3\) is largest at the right endpoint. What is that largest value?",
          12, "1",
          r"\(f''(t) = 6t\), so on \([0, 2]\) the maximum absolute value is \(6 \cdot 2 = 12\). The first derivative at the right end is \(3 \cdot 4 = 12\) as well, a coincidence of this cubic; the bound uses the second derivative. Half of 12 is 6, which is the coefficient in \(f''\) rather than the maximum. The increment 8 is smaller than this \(M\).",
          SLICE, A_SLICE)
    b.sym(3,
          r"A remainder bound has the form \((M/2) r^2\), where \(r\) is the step length and \(M\) bounds the Hessian. Write that bound as an expression in the names M and r.",
          "M*r^2/2",
          {"M": (0.3, 5), "r": (0.3, 4)},
          r"The quadratic form is at most \(M r^2\), and the exact expansion carries a factor one half, so the absolute remainder is at most \(M r^2 / 2\)."
          "\n"
          r"• \(M r^2\) drops the one half."
          "\n"
          r"• \(M r / 2\) forgets that the length is squared."
          "\n"
          r"• \(M + r^2 / 2\) adds the bound to the length instead of scaling.",
          ["(M*r^2)/2", "M*(r^2)/2"],
          fig=SLICE, alt=A_SLICE)
    b.num(3,
          r"Let \(f(x, y) = x^2\). In the exact second-order expansion from \((0, 0)\) to \((3, 1)\), what is the quadratic term \(\tfrac12 h^{T} H(z) h\)?",
          9, "1",
          r"The Hessian of \(x^2\) is constant, with a 2 in the \((1, 1)\) entry and zeros elsewhere. The step is \((3, 1)\), so \(\tfrac12 \cdot 2 \cdot 9 = 9\). The linear term at the origin is 0, and \(f(3, 1) = 9\), so the quadratic term accounts for the whole increment. The value \(3\) forgets the square. Adding the unused coordinate, \(9 + 1\), treats \(f\) as \(x^2 + y^2\).",
          ELL, A_ELL)
    b.mc(3,
         "An approximation becomes a bound when",
         ["the intermediate point is replaced by the expansion point and the error is ignored",
          "the Hessian is known only at the expansion point",
          "an upper bound on the Hessian along the segment replaces the unknown intermediate Hessian",
          "the function is assumed linear"],
         2,
         r"The exact expansion still contains an unknown point. Replacing the Hessian quadratic form by its worst case on the segment produces an inequality. Dropping the remainder leaves an approximation. The Hessian at the single expansion point does not control the intermediate point. A linear function has a zero remainder, which is a bound, but it is a special case rather than the device that creates the bound.",
         SEG, A_SEG)
    b.multi(4,
            "Which statements hold?",
            ["Some point of the open segment makes the function increment equal the gradient there dotted with the step.",
             r"If the Hessian operator norm is at most \(M\) along the segment, the absolute linear remainder is at most \((M/2)\) times the squared step length.",
             "The intermediate point is always the midpoint.",
             r"The smallest eigenvalue of the Hessian can replace \(M\) in that upper bound."],
            [0, 1],
            r"The first statement is the mean value theorem, and the second is the remainder bound obtained by estimating the exact quadratic term. The midpoint satisfies the theorem only for special functions. The smallest eigenvalue lower-bounds a quadratic form; an upper bound needs a number at least as large as the operator norm, so the smallest eigenvalue points the wrong way whenever the Hessian is not a multiple of the identity.",
            SEG, A_SEG, ["second-order-optimality"])
    b.num(4,
          r"Let \(f(x, y) = 3 x^2\), whose Hessian has operator norm 6. From \((0, 0)\) to \((1, 2)\), what is the remainder bound \((M/2)\lVert h \rVert^2\) with \(M = 6\)?",
          15, "1",
          r"The squared step length is \(1 + 4 = 5\), and \((6 / 2) \cdot 5 = 15\). The function value at the end is 3, which sits under the bound. Using \(M\) without the one half gives 30. Using the step length instead of its square gives \((M/2) \sqrt{5}\), which is not 15. The operator norm 6 alone is not the bound.",
          ELL, A_ELL, ["convexity-second-order"])
    b.mc(4,
         "A second-order necessary condition at an interior minimizer uses the exact expansion to conclude that",
         ["the gradient is a unit vector",
          "the Hessian is negative definite",
          "the function is constant",
          "the Hessian is positive semidefinite"],
         3,
         r"If a direction had a negative Hessian quadratic form, the exact second-order term would make the function decrease along that direction, contradicting a local minimum. The Hessian is therefore positive semidefinite. Positive definiteness is a sufficient condition, not the necessary one. The gradient at an interior minimizer is zero, not a unit vector. Constancy is stronger than a local minimum.",
         ELL, A_ELL, ["second-order-optimality"])
    b.save()


def expl_directional():
    sections = [
        {"heading": "The idea", "figure": SLICE, "figure_alt": A_SLICE,
         "body_md": r"""A directional derivative asks how a scalar function changes when you leave a point along one chosen ray. Fix a point \(x\) and a direction \(d\). For a small positive number \(t\), the point \(x + t d\) lies on that ray. Subtract the old value from the new one and divide by \(t\). The directional derivative is the limit of those quotients as \(t\) decreases to 0.

The limit is one-sided on purpose. Negative \(t\) would walk the opposite ray. The slice \(g(t) = f(x + t d)\) is an ordinary function of one variable, and the directional derivative is the right-hand derivative of that slice at 0, when the right-hand derivative exists.

No gradient is required to ask the question. A corner in the slice can still have a right-hand slope. Scaling \(d\) by a positive number scales the derivative by the same number, because the parametrization got faster. At a corner the opposite ray can climb as well, so the derivative need not be linear in the direction. When a gradient exists and the function is differentiable, this slope agrees with the inner product of the gradient and the direction."""},
        {"heading": "Key equations",
         "body_md": r"""The definition is the one-sided limit
\[
f'(x; d) = \lim_{t \downarrow 0} \frac{f(x + t d) - f(x)}{t},
\]
when the limit exists. If \(c > 0\) and both sides exist, then \(f'(x; c d) = c\, f'(x; d)\). Where \(f\) is differentiable,
\[
f'(x; d) = \nabla f(x)^{T} d.
\]
The right-hand side is linear in \(d\). The definition by itself does not promise that linearity."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(x, y) = 5x + y^2\) through (4, -1), and take the direction \((0, 2)\). The value at the point is \(20 + 1 = 21\). Along the ray the second coordinate is \(-1 + 2t\), so
\[
f(4,\ -1 + 2t) = 20 + ( -1 + 2t )^2 = 21 - 4t + 4t^2.
\]
The difference quotient is \(-4 + 4t\), and the limit is \(-4\). The first coordinate never moved, so the linear term \(5x\) contributed nothing to the slope. The factor 2 in the direction doubled the ordinary \(y\)-derivative, which is \(2y = -2\) at this point: \(2 \cdot (-2) = -4\)."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A two-sided limit is a stronger demand, and it is the wrong one for this definition. Dividing by the length of \(d\) answers a different question, the derivative in a unit direction. At a corner of an absolute value, both opposite directions can give a positive derivative, so you cannot recover one of them by negating the other. Reading the function value, or the sum of the direction's coordinates, does not produce a slope."""},
        {"heading": "Where this leads",
         "body_md": r"""Partial derivatives are the directional derivatives along the coordinate directions, and the gradient packages them so that every directional derivative is an inner product. Automatic differentiation in forward mode propagates exactly this directional derivative through a computation. A descent method later asks the inner product with the gradient to be negative, which is a sign restriction on this slope."""},
    ]
    save_explainer("directional-derivative", "Directional derivative", sections)


def expl_gradient():
    sections = [
        {"heading": "The idea", "figure": PAIR, "figure_alt": A_PAIR,
         "body_md": r"""A partial derivative holds every coordinate fixed except one, and it differentiates in the remaining coordinate. Do that once for each coordinate and stack the results. The column you get is the gradient.

The gradient is the direction in which the first-order increase is largest. On a unit vector the inner product of the gradient with that vector is at most the length of the gradient, and the bound is attained when the unit vector points along the gradient. The opposite unit vector is the direction of steepest decrease, with slope equal to the negative of that length.

Where the function is differentiable, the directional derivative in an arbitrary direction is the inner product of the gradient with that direction. A direction orthogonal to the gradient has directional derivative zero. In the plane, those directions are tangent to the level curve through the point."""},
        {"heading": "Key equations",
         "body_md": r"""In coordinates,
\[
\nabla f(x) = \Bigl( \frac{\partial f}{\partial x_1},\ \ldots,\ \frac{\partial f}{\partial x_n} \Bigr)^{T}.
\]
The directional-derivative identity and the steepest-slope fact are
\[
f'(x; d) = \nabla f(x)^{T} d, \qquad \max_{\lVert d \rVert = 1} \nabla f(x)^{T} d = \lVert \nabla f(x) \rVert.
\]
The Jacobian of a scalar function is the row \(\nabla f(x)^{T}\). The column is the form used when the next sentence dots the gradient with a direction."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(x, y) = x^2 + y^2\) at the point \((8, 15)\). The partial derivatives are \(2x\) and \(2y\), so the gradient is \((16, 30)\). Its squared length is \(256 + 900 = 1156\), and
\[
\sqrt{1156} = 34.
\]
The length 34 is the steepest unit slope at this point. The inner product with \((1, 0)\) is only 16, the ordinary partial derivative in \(x\). The direction \((-15, 8)\) is orthogonal to \((16, 30)\) after a short check of the cross-multiples, so the directional derivative in that direction is 0. That direction stays on the level circle through the point, to first order."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The gradient is not automatically a unit vector. Dividing by its length is a second step, used only when a unit direction is required. The sum of the partial derivatives is the directional derivative in the all-ones direction, which usually has length greater than 1, so that sum is larger than the steepest unit slope. A single partial derivative is the full directional derivative only for a coordinate direction. One vanishing directional derivative means orthogonality, not a zero gradient."""},
        {"heading": "Where this leads",
         "body_md": r"""The Hessian is the Jacobian of this gradient, entry by entry. A first-order necessary condition for an interior minimum sets the gradient to zero. A descent direction is any vector whose inner product with the gradient is negative, and the negative gradient itself is the steepest such direction among unit vectors."""},
    ]
    save_explainer("gradient-partial-derivatives", "Partial derivatives and the gradient", sections)


def expl_diff():
    sections = [
        {"heading": "The idea", "figure": LEVELS, "figure_alt": A_LEVELS,
         "body_md": r"""Differentiability in several variables is a statement about a linear approximation, not merely about the existence of partial derivatives. At a point \(x\) there must be a linear map \(L\) such that the error in \(f(x) + L(h)\) is little-o of the step length. Dividing that error by \(\lVert h \rVert\) has to produce a quotient that tends to 0 as \(h\) tends to 0, from every direction at once.

If this happens, the partial derivatives exist and equal \(L\) on the coordinate directions, and every directional derivative exists and equals \(L(d)\). The linear map is then the inner product with the gradient. Continuous partial derivatives on a neighborhood are enough to guarantee the little-o condition, so they are a convenient sufficient test.

The converses fail. Partials can exist at a point while the quotient does not tend to 0. Directional derivatives can exist in every direction and still refuse to line up as one linear map. Either failure means the function is not differentiable at the point, even if it is continuous there."""},
        {"heading": "Key equations",
         "body_md": r"""The definition asks for a linear \(L\) with
\[
f(x + h) = f(x) + L(h) + r(h), \qquad \frac{r(h)}{\lVert h \rVert} \to 0 \text{ as } h \to 0.
\]
When \(f\) is differentiable, \(L(h) = \nabla f(x)^{T} h\). Continuous partial derivatives near \(x\) imply that such an \(L\) exists. Differentiability implies existence of the partial derivatives. Existence of the partial derivatives does not imply differentiability."""},
        {"heading": "Worked example",
         "body_md": r"""Use checkpoint (2, 7) for \(f(x, y) = x^2 + x y\). The value is \(4 + 14 = 18\). The gradient is \((2x + y,\ x) = (11, 2)\). For the step \((0.3, 0.6)\),
\[
f(2.3,\ 7.6) = 5.29 + 17.48 = 22.77.
\]
The linear prediction is \(18 + 11 \cdot 0.3 + 2 \cdot 0.6 = 22.5\). The absolute remainder is \(0.27\). The step length is \(\sqrt{0.45}\), about \(0.67\), and the quotient of remainder over length is about \(0.40\). Shrinking the step by a factor of ten would shrink a quadratic remainder by about a factor of one hundred, which is the little-o pattern. The partial derivatives here are continuous, so the definition is satisfied even though this particular quotient is not yet small."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Checking the two partial derivatives at the point is not the full test. Axis continuity is not the full test either. A directional derivative in one direction, or even in every direction, can exist while the remainder fails to be little-o, or while the map on directions fails to be linear. The quotient that must tend to 0 uses the remainder after the linear term has been removed. Dividing the function change by the step length still contains the derivative and does not go to 0."""},
        {"heading": "Where this leads",
         "body_md": r"""The first-order Taylor model is this linear approximation, and its error statement is the little-o condition written again. A first-order necessary condition for a minimum needs a genuine gradient, so it needs differentiability rather than partials alone. The tangent inequality for a convex function is the same linear model, promoted from a local approximation to a global lower bound."""},
    ]
    save_explainer("differentiability-multivariable", "Differentiability in several variables", sections)


def expl_hessian():
    sections = [
        {"heading": "The idea", "figure": HESS, "figure_alt": A_HESS,
         "body_md": r"""The gradient records first derivatives. Differentiate it again and the result is a matrix. The entry in row \(i\) and column \(j\) is the partial derivative of the \(i\)-th partial derivative with respect to the \(j\)-th coordinate. That matrix is the Hessian.

When the second partial derivatives are continuous, the order of differentiation does not matter, so the Hessian is symmetric. A polynomial has continuous derivatives of every order, and its mixed partials agree. There are functions whose mixed partials exist at a point and disagree, so the continuity hypothesis is not decorative.

The Hessian measures curvature. For a direction \(d\), the second derivative of the slice \(t \mapsto f(x + t d)\) at \(t = 0\) is the quadratic form \(d^{T} H d\). A positive value means the slice is convex upward along that line. The trace and the determinant summarize the matrix, but the quadratic form is the number the slice actually feels."""},
        {"heading": "Key equations",
         "body_md": r"""The entries and the slice curvature are
\[
(H_f)_{ij} = \frac{\partial^2 f}{\partial x_i \partial x_j}, \qquad \frac{d^2}{dt^2} f(x + t d)\Big|_{t=0} = d^{T} H_f(x)\, d.
\]
If the second partials are continuous, then \(H_f(x)^{T} = H_f(x)\). The Hessian is the Jacobian of the gradient map. A linear function has Hessian equal to the zero matrix."""},
        {"heading": "Worked example",
         "body_md": r"""At the sample point (7, 9), let \(f(x, y) = x^2 y\). The first partials are \(2 x y = 126\) and \(x^2 = 49\). Differentiating again, the pure second partial in \(x\) is \(2y = 18\), the mixed partial is \(2x = 14\), and the pure second partial in \(y\) is 0. The Hessian is
\[
\begin{bmatrix} 18 & 14 \\ 14 & 0 \end{bmatrix}.
\]
On \(v = (1, 1)\) the quadratic form is \(18 + 14 + 14 + 0 = 46\). Both differentiation orders produced the mixed entry 14."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The gradient is not the Hessian. The trace is not the quadratic form on an arbitrary vector; it is the sum of the quadratic forms on the coordinate directions. Forgetting a factor from a product rule makes mixed partials look unequal when the function is a polynomial and they are equal. A linear function has second derivatives equal to zero, so its Hessian is the zero matrix rather than the identity. The determinant's sign says whether the quadratic form is indefinite, and dropping the minus in the \(2 \times 2\) determinant formula loses that sign."""},
        {"heading": "Where this leads",
         "body_md": r"""The second-order Taylor model uses this quadratic form, with a factor one half. The fundamental theorem along a segment writes a gradient increment as an integral of the Hessian times the direction. Matrix calculus then specializes the Hessian for \(x^{T} A x\), where symmetry of \(A\) decides whether the factor in the gradient is \(2A\) or \(A + A^{T}\)."""},
    ]
    save_explainer("hessian-matrix", "Second derivatives and the Hessian", sections)


def expl_jacobian():
    sections = [
        {"heading": "The idea", "figure": JAC, "figure_alt": A_JAC,
         "body_md": r"""A vector-valued map has one scalar output per row. The Jacobian is the matrix whose \(i\)-th row is the gradient of the \(i\)-th output, written as a row. If there are \(m\) outputs and \(n\) inputs, the matrix is \(m \times n\). For a single output the Jacobian is the gradient transposed into a row.

The chain rule multiplies these matrices. For a composition, evaluate the outer Jacobian at the image of the inner map, evaluate the inner Jacobian at the original input, and multiply with the outer factor on the left. The image point matters: the outer derivative has no reason to be evaluated at the original input.

When the outer function is scalar, the same multiplication writes the gradient of the composition as the transpose of the inner Jacobian times the outer gradient at the image. The transpose appears because this page keeps gradients as columns and Jacobians with outputs as rows."""},
        {"heading": "Key equations",
         "body_md": r"""The entry and the two chain-rule forms are
\[
(J_F)_{ij} = \frac{\partial F_i}{\partial x_j}, \qquad J_{F \circ G}(x) = J_F(G(x))\, J_G(x),
\]
\[
\nabla (f \circ g)(x) = J_g(x)^{T}\, \nabla f(g(x)).
\]
The first product is \(m \times n\) when \(F\) has \(m\) outputs and \(G\) has \(n\) inputs. The transpose keeps the scalar chain rule the same shape as a column gradient."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(F(x, y) = (x + y,\ 6x)\) and let the inner map send \(t\) to \((6 + t,\ -2 + t)\). At \(t = 0\) the image is the inner point (6, -2), and the inner velocity is \((1, 1)\). The Jacobian of \(F\) is constant,
\[
J_F = \begin{bmatrix} 1 & 1 \\ 6 & 0 \end{bmatrix}.
\]
The product with the velocity is \((2, 6)\). The first output along the path is \((6 + t) + (-2 + t) = 4 + 2t\), whose derivative is 2, matching the first entry. The second output is \(6(6 + t)\), whose derivative is 6, matching the second entry. The outer Jacobian did not need a special point because it is constant, but the chain rule still evaluates it at the image."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Rows and columns are part of the definition. Transposing by habit changes the shape. The outer Jacobian is evaluated at the image, not at the input. Matrix multiplication is not entrywise multiplication, and composition does not add Jacobians; addition is the rule for a sum of maps. For a scalar outer function, dropping the transpose on the inner Jacobian disagrees with the column convention as soon as the dimensions differ."""},
        {"heading": "Where this leads",
         "body_md": r"""Gradients of \(x^{T} A x\) and of a squared residual are chain-rule calculations with these shapes. A computational graph applies the same product one elementary step at a time. Newton's method for a nonlinear system solves the linear model \(F(x) + J_F(x)(z - x) = 0\), which is this Jacobian used as the derivative of a map."""},
    ]
    save_explainer("jacobian-chain-rule", "Jacobian and multivariable chain rule", sections)


def expl_matrix():
    sections = [
        {"heading": "The idea", "figure": QUAD, "figure_alt": A_QUAD,
         "body_md": r"""Several functions in optimization are built from a constant vector and a constant matrix. Their gradients have short formulas, and the formulas are easier to remember after one differentiation in coordinates.

A linear form \(c^{T} x\) has gradient \(c\). The squared Euclidean length \(\lVert x \rVert^2 = x^{T} x\) has gradient \(2x\). A quadratic form \(x^{T} A x\) is more careful. If \(A\) is not symmetric, each of \(x\) on the left and \(x\) on the right contributes, and the gradient is \((A + A^{T}) x\). If \(A\) is symmetric, \(A + A^{T} = 2A\), and the gradient collapses to \(2 A x\).

The squared residual \(\lVert A x - b \rVert^2\) is a composition. The residual is linear, the outer function is a squared length, and the chain rule produces \(2 A^{T}(A x - b)\). The transpose sits on \(A\) because the Jacobian of \(x \mapsto A x\) is \(A\), and the scalar chain rule transposes it."""},
        {"heading": "Key equations",
         "body_md": r"""With \(c\), \(b\), and \(A\) constant,
\[
\nabla (c^{T} x) = c, \qquad \nabla \lVert x \rVert^2 = 2x, \qquad \nabla (x^{T} A x) = (A + A^{T}) x.
\]
When \(A\) is symmetric, \(\nabla (\tfrac12 x^{T} A x + b^{T} x) = A x + b\), and the Hessian is \(A\). For a residual,
\[
\nabla \lVert A x - b \rVert^2 = 2 A^{T} (A x - b).
\]
The Hessian of \(x^{T} A x\) is \(A + A^{T}\), which is symmetric even when \(A\) is not."""},
        {"heading": "Worked example",
         "body_md": r"""A linear form with data (9, -2) has gradient \((9, -2)\), at every point. For a nonsymmetric quadratic, take \(A = \begin{bmatrix} 0 & 8 \\ 1 & 0 \end{bmatrix}\). Then
\[
A + A^{T} = \begin{bmatrix} 0 & 9 \\ 9 & 0 \end{bmatrix}.
\]
At \((4, 8)\) the product \((A + A^{T}) x\) equals \((72, 36)\). Expanding the form gives \(9 x y\), whose partial derivatives \(9y\) and \(9x\) equal 72 and 36 at that point. The symmetric shortcut \(2 A x\) would have used the wrong matrix: \(2 A (4, 8) = 2(64, 4) = (128, 8)\), which matches neither partial derivative."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The factor \(2 A x\) is not the gradient of \(x^{T} A x\) unless \(A\) is symmetric. Replacing \(A\) by its symmetric part first, or using \(A + A^{T}\), is the repair. The residual gradient carries \(A^{T}\) on the left of the residual, not \(A\). The Hessian of a linear form is zero, not the identity. A one-half in front of a symmetric quadratic cancels the 2 in the gradient and leaves \(A x\), so dropping or keeping that one half changes the formula."""},
        {"heading": "Where this leads",
         "body_md": r"""Minimizing \(\tfrac12 x^{T} A x + b^{T} x\) with symmetric \(A\) is the linear equation \(A x + b = 0\), and positive definiteness of \(A\) decides uniqueness. The second-order convexity test reads the same Hessian. Least squares is the residual case, with normal equations built from \(A^{T} A\)."""},
    ]
    save_explainer("matrix-calculus-gradients", "Gradients of linear and quadratic forms", sections)


def expl_ftc():
    sections = [
        {"heading": "The idea", "figure": SEG, "figure_alt": A_SEG,
         "body_md": r"""The ordinary fundamental theorem says that a derivative integrated from one end of an interval to the other recovers the increment of the function. The same fact applies to a function of several variables once the domain of integration is reduced to a segment.

Parametrize the segment from \(x\) to \(y\) by \(x + t(y - x)\), with \(t\) running from 0 to 1. The composition of \(f\) with that parametrization is an ordinary function of \(t\). Its derivative, by the chain rule, is the gradient at the moving point dotted with the fixed vector \(y - x\). Integrating that derivative from 0 to 1 recovers \(f(y) - f(x)\).

Apply the same argument to each component of the gradient. The derivative of the gradient is the Hessian, so the integrand becomes the Hessian at the moving point times \(y - x\). The integral recovers the gradient increment. Nothing in the parametrization requires the segment to be parallel to an axis."""},
        {"heading": "Key equations",
         "body_md": r"""With the gradient continuous on the segment,
\[
f(y) - f(x) = \int_0^1 \nabla f\bigl(x + t(y - x)\bigr)^{T} (y - x)\, dt.
\]
With the Hessian continuous on the segment,
\[
\nabla f(y) - \nabla f(x) = \int_0^1 H_f\bigl(x + t(y - x)\bigr)\, (y - x)\, dt.
\]
If the integrand is constant, the integral collapses to that constant. A linear \(f\) makes the first integrand constant. A quadratic \(f\) makes the second integrand constant."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(x, y) = x + y^2\) along the vertical segment at x = 8, from height 6 to height 11. The endpoints give
\[
f(8, 11) - f(8, 6) = (8 + 121) - (8 + 36) = 85.
\]
The direction is \((0, 5)\) and the gradient is \((1, 2y)\). Their inner product is \(10 y\). Along the segment, \(y = 6 + 5t\), so the integrand is \(10(6 + 5t) = 60 + 50 t\). Integrating from 0 to 1 gives \(60 + 25 = 85\), matching the increment. The first coordinate cancelled because the segment does not move in \(x\)."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The integrand is not \(f\) itself, and it is not the gradient alone. The direction \(y - x\) stays outside the gradient as a dot factor. Evaluating the gradient only at the endpoints gives a mean-value statement after an extra argument; it is not this integral identity. A gradient increment needs the Hessian in the integrand. An axis-aligned picture is only a picture: the same algebra covers a slanted segment."""},
        {"heading": "Where this leads",
         "body_md": r"""The exact Taylor expansion with an intermediate Hessian is what you get by writing the remainder of the linear model through this integral and then applying the mean value theorem. A Lipschitz gradient is the case where the Hessian factor is bounded, so the integral produces a quadratic upper bound. A secant equation asks a constant matrix to reproduce the integrated gradient change."""},
    ]
    save_explainer("fundamental-theorem-along-segment", "Fundamental theorem of calculus along a segment", sections)


def expl_taylor():
    sections = [
        {"heading": "The idea", "figure": ELL, "figure_alt": A_ELL,
         "body_md": r"""A Taylor model replaces a function near a chosen point by a polynomial that matches its derivatives there. The first-order model matches the value and the gradient. Its graph is the tangent affine approximation. The second-order model also matches the Hessian, so the slice in every direction matches curvature as well as slope.

Both models are functions of the new point. They are built entirely from information at the expansion point. The factor one half in front of the Hessian term is what makes a further differentiation return the Hessian rather than twice the Hessian.

The errors shrink at different rates. After the value and the gradient have been matched, the error of the linear model is little-o of the step length. After the Hessian has been matched too, and the second derivatives are continuous, the error of the quadratic model is little-o of the squared step length. Those statements are about small steps. At one particular step the quadratic model can still miss by more than the linear model."""},
        {"heading": "Key equations",
         "body_md": r"""With \(h = y - x\),
\[
T_1(y) = f(x) + \nabla f(x)^{T} h, \qquad T_2(y) = T_1(y) + \tfrac12 h^{T} H_f(x)\, h.
\]
If \(f\) is differentiable, \(f(y) - T_1(y) = o(\lVert h \rVert)\). If the second partials are continuous, \(f(y) - T_2(y) = o(\lVert h \rVert^2)\). On a quadratic polynomial, \(T_2\) is exact."""},
        {"heading": "Worked example",
         "body_md": r"""On the cubic slice at x = 2, let \(f(x, y) = y^3 + x\), expanded at \((2, 3)\) with step \((0, -1)\). The value is \(27 + 2 = 29\). The gradient is \((1, 3 y^2) = (1, 27)\), so the linear term is \(-27\). The only nonzero second partial is \(\partial^2 f / \partial y^2 = 6y = 18\), and the quadratic term is \(\tfrac12 \cdot 18 \cdot 1 = 9\). The second-order model is
\[
29 - 27 + 9 = 11.
\]
The function at the new point \((2, 2)\) is \(8 + 2 = 10\). The model used derivatives only at the expansion point. A cubic is allowed to miss the model at a step of this length."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Dropping the one half doubles the quadratic term and makes the Hessian of the model twice the Hessian of \(f\). Evaluating the gradient or the Hessian at the new point is a different formula, closer to an exact expansion with an intermediate point. The linear model is not the gradient; the gradient is only the coefficient of the step. Little-o statements do not rank the two models at one fixed step."""},
        {"heading": "Where this leads",
         "body_md": r"""The exact second-order expansion keeps the same shape and moves the Hessian to an intermediate point, which is how a bound is proved. Newton's method minimizes the quadratic model and solves \(H d = -\nabla f\). A backtracking line search uses only the linear model, and it accepts a step whose true decrease covers a fraction of the predicted linear decrease."""},
    ]
    save_explainer("taylor-approximation-multivariable", "First- and second-order Taylor approximations", sections)


def expl_exact():
    sections = [
        {"heading": "The idea", "figure": SEG, "figure_alt": A_SEG,
         "body_md": r"""An approximation becomes an identity when the leftover derivative is evaluated at the right intermediate point. On a segment, the mean value theorem says the function increment equals the gradient at some strict intermediate point, dotted with the step. The point depends on the two ends and on the function. It is not always the midpoint, and it is not the expansion point unless the function is linear.

The second-order identity keeps the value and the gradient at the expansion point, and it places the Hessian at an intermediate point. The formula looks like the second-order Taylor model, with one change of address for the Hessian. Because the intermediate point is unknown, the identity does not compute a number by itself. It becomes a bound when the Hessian term is replaced by something larger that does not depend on the unknown point.

If the operator norm of the Hessian is at most \(M\) everywhere on the segment, the quadratic form is at most \(M\) times the squared step length. The factor one half remains, so the absolute error of the linear model is at most \((M/2)\) times that squared length."""},
        {"heading": "Key equations",
         "body_md": r"""For some \(z\) on the open segment from \(x\) to \(y\), and \(h = y - x\),
\[
f(y) - f(x) = \nabla f(z)^{T} h,
\]
\[
f(y) = f(x) + \nabla f(x)^{T} h + \tfrac12 h^{T} H_f(z)\, h.
\]
If \(\lVert H_f \rVert \le M\) along the segment, then
\[
\bigl\lvert f(y) - f(x) - \nabla f(x)^{T} h \bigr\rvert \le \tfrac{M}{2} \lVert h \rVert^2.
\]
The norm on the Hessian is the operator norm induced by the vector norm in the bound."""},
        {"heading": "Worked example",
         "body_md": r"""Consider the fourth power on a segment of length 3. Let \(f(t) = t^4\) from 0 to 3. The increment is 81, so the mean value theorem says \(f'(z) \cdot 3 = 81\), hence \(f'(z) = 27\). Since \(f'(t) = 4 t^3\), the intermediate point satisfies \(4 z^3 = 27\). The second derivative is \(12 t^2\), and its largest value on the segment is \(12 \cdot 9 = 108\). The linear model at 0 is 0, because \(f'(0) = 0\). The remainder bound with \(M = 108\) and step 3 is
\[
\tfrac{108}{2} \cdot 9 = 486,
\]
and the actual increment 81 sits strictly under that bound. The intermediate point for the first-order statement is not the midpoint 1.5, because \(4 \cdot (1.5)^3\) is not 27."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The intermediate point is existential. You may not replace it by the midpoint, the expansion point, or the far end without a separate reason. The remainder bound uses an upper bound on the Hessian, such as the operator norm. The smallest eigenvalue bounds the quadratic form from below and can make an upper bound false. Forgetting the one half, or forgetting to square the step length, changes the formula. On a quadratic the second-order identity is exact for every intermediate point, because the Hessian is constant; that special case is not the general location of \(z\)."""},
        {"heading": "Where this leads",
         "body_md": r"""A second-order necessary condition argues from the exact expansion: a negative curvature direction would decrease the function, so a local minimizer has a positive semidefinite Hessian. A second-order sufficient condition asks for a positive definite Hessian so the quadratic term dominates. Convexity of a twice differentiable function is the positive-semidefinite Hessian everywhere, which turns the linear model into a global underestimator rather than a local approximation."""},
    ]
    save_explainer("taylor-exact-mean-value", "Exact Taylor expansions and the mean value theorem", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    bank_directional()
    bank_gradient()
    bank_diff()
    bank_hessian()
    bank_jacobian()
    bank_matrix()
    bank_ftc()
    bank_taylor()
    bank_exact()
    expl_directional()
    expl_gradient()
    expl_diff()
    expl_hessian()
    expl_jacobian()
    expl_matrix()
    expl_ftc()
    expl_taylor()
    expl_exact()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    banned = ("graz", "boyd", "nocedal", "vandenberghe", "hefferon", "wikibook",
              "textbook", "university", "professor", "lecture", "syllabus", "cambridge", "springer")
    ids = [
        "directional-derivative", "gradient-partial-derivatives", "differentiability-multivariable",
        "hessian-matrix", "jacobian-chain-rule", "matrix-calculus-gradients",
        "fundamental-theorem-along-segment", "taylor-approximation-multivariable",
        "taylor-exact-mean-value",
    ]
    private = {
        "directional-derivative": "through (4, -1)",
        "gradient-partial-derivatives": "length 34",
        "differentiability-multivariable": "checkpoint (2, 7)",
        "hessian-matrix": "sample point (7, 9)",
        "jacobian-chain-rule": "inner point (6, -2)",
        "matrix-calculus-gradients": "data (9, -2)",
        "fundamental-theorem-along-segment": "vertical segment at x = 8",
        "taylor-approximation-multivariable": "cubic slice at x = 2",
        "taylor-exact-mean-value": "fourth power on a segment of length 3",
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
