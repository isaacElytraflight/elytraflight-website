#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB4 banks and explainers.

Skills: convex-functions, convexity-first-order, convexity-second-order,
finite-difference-derivatives, computational-graphs, ad-forward-mode,
ad-reverse-mode, hessian-vector-products-ad, backprop-neural-network.

Closed-form answers live here. skilltree/verify_nlo_nb4.py recomputes the
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
from templates import (
    block_diagram,
    ellipse_axes,
    level_curves_fig,
    matrix_fig,
    plane_vectors,
    plot,
    segment_fig,
)

CHORD = segment_fig("segment between two points")
A_CHORD = "A solid segment joins two marked points on a dashed line."
BOWL = plot(lambda t: 0.12 * t * t + 0.55, 0.0, 2.4, "t", "f", "a curve bending upward")
A_BOWL = "A curve of one variable, drawn on labeled axes."
CUBIC = plot(lambda t: 0.05 * t * t * t + 0.35, 0.0, 2.2, "t", "f", "a sampled curve")
A_CUBIC = "A curve of one variable, drawn on labeled axes."
LEVELS = level_curves_fig("nested ellipses")
A_LEVELS = "Three nested ellipses centered at the origin."
ELL = ellipse_axes("axis-aligned ellipse")
A_ELL = "An ellipse centered at the origin, longer along the first axis."
HESS = matrix_fig([["xx", "xy"], ["yx", "yy"]], "second-derivative positions")
A_HESS = "A 2 by 2 array labeled by second-derivative positions."
GRAPH = block_diagram(["xy", "+ c", "sq", "+ x"], "four elementary steps", output_label="f")
A_GRAPH = "Four blocks in a row, ending at a scalar output."
NET = block_diagram(["lin", "ramp", "out", "loss"], "four network steps", output_label="L")
A_NET = "Four blocks in a row, from a linear step to a loss."
RAY = plane_vectors([(1.2, 0.45, "d")], "one arrow from the origin")
A_RAY = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.15, 0.35, "g"), (0.25, 1.15, "d")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."


def bank_convex():
    b = Bank("convex-functions")
    b.mc(1,
         r"A function \(f\) is convex when, for every weight \(t\) between 0 and 1,",
         [r"\(f\) at a mixture of two points is at most the same mixture of the values",
          r"\(f\) at a mixture of two points is at least the same mixture of the values",
          r"\(f\) at a mixture of two points equals the same mixture of the values, for every \(f\)",
          r"\(f\) needs to be checked only at the two endpoints"],
         0,
         r"Convexity puts the graph on or under the chord. The function of a mixture is at most the mixture of the function values. The opposite inequality is concavity. Equality for every pair is what affine functions do, and that is a special case, not the definition of every convex function. Checking the endpoints alone never sees the chord.",
         CHORD, A_CHORD)
    b.num(1,
          r"Let \(f(t) = t^2\). On the chord from \(t = 1\) to \(t = 5\), what is the height of the chord at the midpoint?",
          13, "1",
          r"The values are \(1\) and \(25\). The midpoint of the chord is their average, \(13\). The function at the midpoint \(t = 3\) is \(9\), which lies under the chord, as convexity requires. Using \(9\) reports the function instead of the chord. The gap \(13 - 9 = 4\) is neither height.",
          BOWL, A_BOWL)
    b.mc(1,
         "Every norm on a real vector space is",
         ["strictly convex",
          "convex, and not strictly convex",
          "convex only inside the unit ball",
          "not convex, because a sphere fails to contain its chords"],
         1,
         r"The triangle inequality and absolute homogeneity give the chord inequality, so every norm is convex. It is not strict: along the ray from the origin to a nonzero vector the norm is linear, so the chord sits on the graph. Restricting attention to the unit ball is a statement about a set, not about the function. A sphere failing to be a convex set does not decide whether the norm, which is a function, is convex.",
         ELL, A_ELL)
    b.multi(2,
            r"Which of these functions are convex on the whole real line?",
            [r"\(f(t) = \lvert t \rvert + 2t\)",
             r"\(f(t) = -t^2\)",
             r"\(f(t) = 4t - 7\)",
             r"\(f(t) = t^3\)",
             r"\(f(t) = \max(t,\ 0)\)"],
            [0, 2, 4],
            r"An absolute value is convex, and adding a linear function keeps convexity. An affine function meets the chord definition with equality, so it is convex. The positive-part function is the maximum of the convex functions \(0\) and \(t\), and a pointwise maximum of convex functions is convex."
            "\n"
            r"• \(-t^2\) bends the other way: its chords lie under the graph."
            "\n"
            r"• \(t^3\) has second derivative \(6t\), which is negative for negative \(t\). It is not convex on the whole line, even though the restriction to nonnegative \(t\) is convex.",
            BOWL, A_BOWL)
    b.num(2,
          r"Let \(f(x, y) = \lvert x \rvert + 2\lvert y \rvert\). For the points \((2, -4)\) and \((-6, 2)\) and the weight \(t = 1/4\) on the second point, what is the right-hand side of the chord inequality?",
          10, "1",
          r"The function values are \(2 + 8 = 10\) and \(6 + 4 = 10\). The combination with weights \(3/4\) and \(1/4\) is \(10\). The mixed point is \((0, -5/2)\), where \(f\) equals \(5\), which is the left-hand side and is smaller. Reporting \(5\) uses the function at the mixture. Reporting \(0\) would treat the two equal values as cancelling.",
          CHORD, A_CHORD)
    b.order(2,
            "Put these steps in the order used to test the chord definition on one pair of points.",
            ["Choose two points in the domain and a weight between 0 and 1.",
             "Form the weighted mixture of the two points.",
             "Evaluate the function at that mixture.",
             "Compare it with the same weights applied to the two function values."],
            r"The definition starts from a pair and a weight, builds one point on the segment, and only then compares function values. Evaluating the function before the mixture exists has nothing to evaluate. Comparing the endpoints with each other never tests the interior of the chord.",
            CHORD, A_CHORD)
    b.sym(3,
          r"Let \(a\) and \(b\) be real. For \(f(t) = a t^2 + b t\), the chord from \(0\) to \(2\) has a height at the midpoint. Write that height as an expression in the names a and b.",
          "2*a+b",
          {"a": (-4, 4), "b": (-4, 4)},
          r"The endpoint values are \(f(0) = 0\) and \(f(2) = 4a + 2b\). Their average is \(2a + b\)."
          "\n"
          r"• \(a + b\) is the function at the midpoint \(t = 1\), not the chord."
          "\n"
          r"• \(4a + 2b\) is the value at the right endpoint."
          "\n"
          r"• \(2a\) drops the linear term.",
          ["b+2*a", "2*(a)+b"],
          fig=BOWL, alt=A_BOWL)
    b.num(3,
          r"Let \(f(t) = t^2\). On the chord from \(0\) to \(4\), with weight \(1/4\) on the right endpoint, by how much does the chord sit above the function?",
          3, "1",
          r"The mixture point is \(1\), and \(f(1) = 1\). The chord height is \((3/4)\cdot 0 + (1/4)\cdot 16 = 4\). The gap is \(4 - 1 = 3\). A strictly convex function has a positive gap like this one whenever the points differ and the weight is strictly between 0 and 1. Reporting \(4\) is the chord alone. Reporting \(1\) is the function alone.",
          BOWL, A_BOWL)
    b.find_error(3,
                 r"A note claims that \(t^3\) is convex on the whole real line. Exactly one step is false.",
                 ["The second derivative of t cubed is 6t.",
                  "That second derivative is nonnegative at every real t.",
                  "A nonnegative second derivative on an open interval implies convexity there.",
                  "Therefore t cubed is convex on the whole real line."],
                 1,
                 r"The second derivative of \(t^3\) really is \(6t\), and a nonnegative second derivative on an open interval really does imply convexity. The false step is the claim that \(6t\) never goes negative. It is negative for every negative \(t\), so the hypothesis of the second-derivative test is not met on the whole line, and the closing sentence does not follow. On the nonnegative half-line the same derivative is nonnegative and the restriction is convex.",
                 ["The second derivative is negative for negative t, so it is not nonnegative everywhere.",
                  "The formula for the second derivative of t cubed is wrong.",
                  "A nonnegative second derivative does not imply convexity."],
                 0,
                 BOWL, A_BOWL)
    b.mc(4,
         "An affine function is",
         ["convex only when its slope vector is nonzero",
          "neither convex nor concave",
          "both convex and concave",
          "strictly convex"],
         2,
         r"An affine function meets the chord identity with equality, so both the convex inequality and the concave inequality hold. A zero slope is still affine, and still both. Equality on every chord is the opposite of strict convexity, which demands a strict inequality for distinct points and an interior weight. A convex program may use an affine objective; the feasible set then decides the geometry.",
         CHORD, A_CHORD, ["optimization-problem-classes"])
    b.num(4,
          r"Let \(f\) be the Euclidean norm on the plane. On the chord from \((3, 0)\) to \((0, 4)\), by how much does the chord sit above \(f\) at the midpoint?",
          1, "1",
          r"The endpoint norms are \(3\) and \(4\), so the chord height is \(3.5\). The midpoint is \((1.5, 2)\), and its Euclidean norm is \(2.5\). The gap is \(1\). Reporting \(2.5\) is the function. Reporting \(3.5\) is the chord. The norm is convex, so the gap cannot be negative. It is not strictly convex on the whole plane, but this particular chord does leave a gap because the two vectors are not nonnegative multiples of one vector.",
          ELL, A_ELL, ["convexity-first-order"])
    b.mc(4,
         "The pointwise maximum of a family of convex functions is",
         ["concave",
          "convex only when every function in the family is strictly convex",
          "not convex, because a maximum introduces a corner",
          "convex"],
         3,
         r"At a mixture, each function sits under its own chord, and the maximum of those values sits under the maximum of the chords. A corner, as in a maximum of linear functions, is allowed. Strict convexity of the pieces is not required: the maximum of two affine functions is convex and not strictly convex. The pointwise minimum can fail, and that is a different operation.",
         LEVELS, A_LEVELS, ["convexity-second-order"])
    b.save()


def bank_first():
    b = Bank("convexity-first-order")
    b.mc(1,
         r"For a differentiable convex function, the first-order condition says that",
         [r"the gradient vanishes at every point",
          r"the graph lies on or above its tangent",
          r"the Hessian is the identity",
          r"every directional derivative is zero"],
         1,
         r"Differentiable convexity is equivalent to the tangent being a global underestimator: the function at any other point is at least the linear model. A zero gradient is what happens at a minimizer, not at every point. The Hessian is the second-order test. A zero directional derivative in every direction would force the gradient to vanish.",
         BOWL, A_BOWL)
    b.num(1,
          r"Let \(f(x, y) = x^2 + 3y^2\). At \((2, 1)\), what value does the tangent underestimator give at \((0, 2)\)?",
          5, "1",
          r"Here \(f(2, 1) = 7\) and the gradient is \((4, 6)\). The step to \((0, 2)\) is \((-2, 1)\), and the linear term is \(4\cdot(-2) + 6\cdot 1 = -2\). The underestimator is \(7 - 2 = 5\). The function at \((0, 2)\) is \(12\), which lies above \(5\). Reporting \(12\) uses the function. Reporting \(7\) stops at the base value. Reporting \(-2\) is only the linear term.",
          PAIR, A_PAIR)
    b.mc(1,
         r"If \(f\) is differentiable and convex and \(\nabla f(x) = 0\), then",
         [r"\(x\) is a saddle",
          r"\(x\) is a local minimum that need not be global",
          r"\(x\) is a global minimizer",
          r"\(f\) is constant"],
         2,
         r"The tangent inequality with a zero gradient says \(f(y) \ge f(x)\) for every \(y\). That is a global minimum. A saddle would need a direction of increase and a direction of decrease. Without convexity, a zero gradient is only a stationary point. Constancy is the special case of a zero function, not a consequence of one zero gradient.",
         LEVELS, A_LEVELS)
    b.sym(2,
          r"At the base point \(1\), the tangent underestimator of \(a t^2 + b t\), evaluated at a point \(y\), is an expression in the names a, b, and y. Write that expression.",
          "2*a*y+b*y-a",
          {"a": (-3, 3), "b": (-3, 3), "y": (-3, 3)},
          r"The value at \(1\) is \(a + b\), and the derivative there is \(2a + b\). The model is \(a + b + (2a + b)(y - 1)\), which simplifies to \((2a + b)y - a\)."
          "\n"
          r"• \(a y^2 + b y\) is the function itself, not its tangent."
          "\n"
          r"• \(2a + b\) is the slope at the base point, with no value and no step."
          "\n"
          r"• \((2a + b)y\) forgets to subtract \(a\).",
          ["y*(2*a+b)-a", "(2*a+b)*(y-1)+a+b"],
          fig=BOWL, alt=A_BOWL)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 3y^2\). At base point \((2, 1)\), how far is \(f(0, 2)\) above the tangent underestimator?",
          7, "1",
          r"The underestimator at \((0, 2)\) is \(5\), and \(f(0, 2) = 12\). The gap is \(7\). For a convex function this gap is nonnegative. Reporting \(5\) is the tangent value. Reporting \(12\) is the function. The linear term alone is \(-2\), which is not the gap.",
          PAIR, A_PAIR)
    b.order(2,
            "Put these steps in the order used to check the tangent inequality at one pair of points.",
            ["Evaluate the function and the gradient at the base point.",
             "Build the linear model from that value, that gradient, and the step.",
             "Evaluate the function at the comparison point.",
             "Check that the function is at least the linear model."],
            r"The linear model is built from data at the base point, and the comparison uses the function at the other point. The inequality is the last check. Swapping the two points tests a different tangent. Comparing the two function values with no linear term is the chord test, which is a different characterization.",
            BOWL, A_BOWL)
    b.find_error(3,
                 r"A note claims that \(f(t) = -t^2\) satisfies the tangent underestimator inequality at base point \(1\). Exactly one step is false.",
                 ["The derivative of minus t squared is -2t.",
                  "At base point 1 the linear model, evaluated at v, is 1 - 2v.",
                  "At v = 0 the model equals 1 and the function equals 0, and 0 is at least 1.",
                  "A function that meets the tangent inequality everywhere is convex."],
                 2,
                 r"The derivative of \(-t^2\) is \(-2t\). At base \(1\), the value is \(-1\) and the slope is \(-2\), so the model is \(-1 - 2(v - 1) = 1 - 2v\). At \(v = 0\) that model is \(1\) and the function is \(0\). The claim that \(0\) is at least \(1\) is false, so this tangent already fails. The last step states the real theorem and is not the flaw. One failed pair is enough to reject convexity.",
                 ["Zero is not at least one, so this tangent fails as an underestimator.",
                  "The derivative of minus t squared is not -2t.",
                  "The linear model at base point 1 is computed incorrectly."],
                 0,
                 BOWL, A_BOWL)
    b.num(3,
          r"Let \(f(x, y) = x^2 + 3y^2\). At base point \((2, 1)\), what is the linear term \(\nabla f(2, 1)^{T}\bigl((0, 2) - (2, 1)\bigr)\)?",
          -2, "1",
          r"The gradient is \((4, 6)\) and the step is \((-2, 1)\). The inner product is \(-8 + 6 = -2\). The underestimator is the base value \(7\) plus this term, which is \(5\), a different quantity. The function gap \(7\) is the amount by which \(f(0, 2)\) beats the underestimator. The squared length of the step is \(5\), which is not an inner product with the gradient.",
          RAY, A_RAY)
    b.mc(3,
         "A differentiable function can fail the tangent underestimator inequality when",
         ["it is not convex, even if every partial derivative exists and is continuous",
          "it is affine",
          "its gradient is the zero vector at one point and the function is convex",
          "the two points in the comparison are the same point"],
         0,
         r"Continuous partial derivatives give differentiability, and that is not convexity. The function \(-t^2\) is smooth and its tangents cut above the graph. An affine function meets the inequality as equality. A convex function with a zero gradient meets it because every value is at least the base value. Comparing a point with itself gives equality, which does not fail.",
         BOWL, A_BOWL)
    b.multi(4,
            r"Which of these differentiable functions satisfy the tangent underestimator inequality at every pair of real points?",
            [r"\(f(t) = t^2 + 3\)",
             r"\(f(t) = -t^2\)",
             r"\(f(t) = 5t - 2\)",
             r"\(f(t) = t^3\)"],
            [0, 2],
            r"A square plus a constant is strictly convex, so every tangent is a strict underestimator except at the base point. An affine function meets every tangent with equality, which the inequality allows."
            "\n"
            r"• \(-t^2\) has tangents that cross above the graph."
            "\n"
            r"• \(t^3\) fails on the negative half-line. Its tangent at \(0\) is the zero function, and \(t^3\) goes below zero.",
            BOWL, A_BOWL, ["convexity-second-order"])
    b.num(4,
          r"Let \(f(x, y) = x^2 + 3y^2\). Using the base point \((1, 0)\), what value does the tangent underestimator give at \((1, 2)\)?",
          1, "1",
          r"Here \(f(1, 0) = 1\) and the gradient is \((2, 0)\). The step \((0, 2)\) is orthogonal to that gradient, so the linear term vanishes and the underestimator stays \(1\). The function at \((1, 2)\) is \(1 + 12 = 13\), which is above the tangent. Reporting \(13\) uses the function. Reporting \(2\) is the first entry of the gradient, not the model.",
          PAIR, A_PAIR, ["convex-optimality-global"])
    b.mc(4,
         "The tangent inequality is a global statement. It fails to be the definition of a local minimum because",
         [r"a local minimum only controls a neighborhood, and the inequality controls every point",
          r"the inequality never uses the gradient",
          r"a convex function cannot have a minimum",
          r"the inequality requires the Hessian to be indefinite"],
         0,
         r"A local minimum says that nearby points are no smaller. The tangent inequality, once the gradient is zero, says that every point is no smaller. That global conclusion is why a stationary point of a convex function is a global minimizer. The inequality is built from the gradient. Convex functions do have minima when the problem is coercive or constrained well. An indefinite Hessian is a sign of nonconvexity, not a requirement of this inequality.",
         LEVELS, A_LEVELS, ["quadratic-function-minimization"])
    b.save()


def bank_second():
    b = Bank("convexity-second-order")
    b.mc(1,
         r"On an open convex set, a twice continuously differentiable function is convex if and only if",
         [r"the gradient is constant",
          r"the function is a polynomial",
          r"the Hessian is positive semidefinite at every point",
          r"the Hessian is invertible at every point"],
         2,
         r"The second-order test is positive semidefiniteness of the Hessian everywhere on the open convex domain. A constant gradient means the function is affine, which is the zero-Hessian case only. Polynomials need not be convex. Invertibility is positive definiteness or negative definiteness or a mixture, and negative eigenvalues destroy convexity.",
         HESS, A_HESS)
    b.num(1,
          r"Let \(f(x, y) = 3x^2 + 5y^2\). What is the smaller eigenvalue of its Hessian?",
          6, "1",
          r"The Hessian is the diagonal matrix with entries \(6\) and \(10\). Both eigenvalues are those diagonal entries, and the smaller one is \(6\). The larger one is \(10\). The function coefficients \(3\) and \(5\) are half of the second derivatives, because differentiating a square brings a factor \(2\). A positive smaller eigenvalue means the Hessian is positive definite, so \(f\) is strictly convex.",
          ELL, A_ELL)
    b.mc(1,
         "For a quadratic function, the linear term and the constant term",
         ["can destroy convexity even when the Hessian is positive semidefinite",
          "have no effect on whether the quadratic is convex",
          "must both be zero for the quadratic to be convex",
          "decide convexity, and the Hessian does not"],
         1,
         r"The Hessian of a quadratic ignores the linear term and the constant. Positive semidefiniteness of that Hessian is the whole test. A linear function is the case of a zero Hessian, and it is convex. Requiring the linear term to vanish would throw out every affine function.",
         HESS, A_HESS)
    b.sym(2,
          r"The Hessian of \(a x^2 + b x y + c y^2\) is constant. Its quadratic form on the vector \((1, 1)\) is an expression in the names a, b, and c. Write that expression.",
          "2*a+2*b+2*c",
          {"a": (-3, 3), "b": (-3, 3), "c": (-3, 3)},
          r"The second derivatives are \(f_{xx} = 2a\), \(f_{xy} = b\), and \(f_{yy} = 2c\). On \((1, 1)\) the form is \(2a + 2b + 2c\)."
          "\n"
          r"• \(a + b + c\) forgets the factor \(2\) on the pure second derivatives."
          "\n"
          r"• \(2a + 2c\) drops the mixed term."
          "\n"
          r"• \(a x^2 + b x y + c y^2\) is the function, and it still contains the point.",
          ["2*(a+b+c)", "2*c+2*b+2*a"],
          fig=HESS, alt=A_HESS)
    b.num(2,
          r"Let \(H = \begin{bmatrix} 2 & -1 \\ -1 & 2 \end{bmatrix}\). This is the Hessian of a quadratic. What is its smaller eigenvalue?",
          1, "1",
          r"The trace is \(4\) and the determinant is \(4 - 1 = 3\). The eigenvalues are the roots of \(\lambda^2 - 4\lambda + 3 = 0\), so \(\lambda = 1\) and \(\lambda = 3\). The smaller one is \(1\). Both are positive, so the Hessian is positive definite and the quadratic is strictly convex. The trace \(4\) is the sum, not the smaller root. The off-diagonal entry \(-1\) is not an eigenvalue.",
          HESS, A_HESS)
    b.order(2,
            "Put these steps in the order used to apply the second-order convexity test.",
            ["Compute the second partial derivatives.",
             "Assemble them into the Hessian, using symmetry of the mixed partials.",
             "Test whether that Hessian is positive semidefinite at every point of the open convex domain.",
             "Conclude convexity when the test passes everywhere, and reject it when some Hessian has a negative eigenvalue."],
            r"The entries come first, the matrix second, the semidefinite test third, and the convexity conclusion last. A single positive-definite Hessian does not finish the test, because a later point could introduce a negative eigenvalue. Checking the gradient is the first-order characterization, and it is not one of these steps.",
            HESS, A_HESS)
    b.find_error(3,
                 r"A note claims that \(f(x, y) = x^2 - y^2\) is convex on the plane. Exactly one step is false.",
                 ["The Hessian is diagonal, with diagonal entries 2 and -2.",
                  "Both diagonal entries are positive.",
                  "A diagonal matrix with positive diagonal entries is positive definite.",
                  "A positive definite Hessian at every point implies strict convexity."],
                 1,
                 r"The Hessian of \(x^2 - y^2\) is diagonal with entries \(2\) and \(-2\). A diagonal matrix with positive diagonal entries is positive definite, and a positive definite Hessian everywhere does imply strict convexity. The false step is the claim that both diagonal entries are positive. The entry \(-2\) is a negative eigenvalue, so the Hessian is indefinite and the function is not convex. Along \(y\) the function is a downward parabola.",
                 ["One diagonal entry is negative, so the Hessian is not positive semidefinite.",
                  "The Hessian is not diagonal.",
                  "A positive definite Hessian does not imply strict convexity."],
                 0,
                 ELL, A_ELL)
    b.num(3,
          r"Let \(f(x, y) = (x + 2y - 1)^2\). What is the off-diagonal entry of its Hessian?",
          4, "1",
          r"Expanding gives \(x^2 + 4xy + 4y^2 - 2x - 4y + 1\). Differentiating twice, \(f_{xx} = 2\), \(f_{xy} = 4\), and \(f_{yy} = 8\). The off-diagonal entry is \(4\). The Hessian \(\begin{bmatrix} 2 & 4 \\ 4 & 8 \end{bmatrix}\) has eigenvalues \(0\) and \(10\), so it is positive semidefinite and \(f\) is convex, but not strictly convex. Reporting \(2\) or \(8\) names a diagonal entry. The linear coefficients do not appear in the Hessian.",
          HESS, A_HESS)
    b.mc(3,
         "If the Hessian is positive definite at every point of an open convex domain, then the function is",
         ["convex, but never strictly convex",
          "strictly convex",
          "affine",
          "a sum of squares of linear functions, and nothing else"],
         1,
         r"Positive definiteness is stronger than semidefiniteness, and the second-order theorem upgrades the conclusion from convex to strictly convex. An affine function has a zero Hessian, which is semidefinite and not definite. Many strictly convex functions are not sums of squares of affine functions; a square of a nonlinear smooth map can be strictly convex on a region as well. Semidefiniteness alone allows flat directions.",
         ELL, A_ELL)
    b.multi(4,
            r"Which of these functions are convex on the whole plane?",
            [r"\(2x^2 + 3y^2\)",
             r"\(x^2 - y^2\)",
             r"\((x + y)^2\)",
             r"\(-x^2 - y^2\)",
             r"\(5x + 7y\)"],
            [0, 2, 4],
            r"The Hessian of \(2x^2 + 3y^2\) is diagonal with entries \(4\) and \(6\), both positive. The Hessian of \((x + y)^2\) is \(\begin{bmatrix} 2 & 2 \\ 2 & 2 \end{bmatrix}\), which is positive semidefinite of rank one, so the function is convex. The linear function has Hessian zero, which is positive semidefinite."
            "\n"
            r"• \(x^2 - y^2\) is indefinite."
            "\n"
            r"• \(-x^2 - y^2\) is negative definite, so it is concave and not convex.",
            LEVELS, A_LEVELS, ["second-order-optimality"])
    b.num(4,
          r"Let \(f(x) = \lVert Ax - b \rVert^2\) with \(A = \begin{bmatrix} 1 & 0 \\ 0 & 2 \\ 1 & 1 \end{bmatrix}\). The Hessian is \(2A^{T}A\). What is the bottom-right entry of that Hessian?",
          10, "1",
          r"The product \(A^{T}A\) equals \(\begin{bmatrix} 2 & 1 \\ 1 & 5 \end{bmatrix}\), because the second column of \(A\) has squared length \(0 + 4 + 1 = 5\) and inner product \(0 + 0 + 1 = 1\) with the first column. Twice that matrix has bottom-right entry \(10\). The top-left entry of the Hessian is \(4\). A least-squares objective of this form always has a positive semidefinite Hessian, so it is convex whether or not this particular entry is the one you read.",
          HESS, A_HESS, ["quadratic-function-minimization"])
    b.mc(4,
         r"A least-squares objective \(\lVert Ax - b \rVert^2\) is convex because",
         [r"\(b\) is the zero vector",
          r"\(A\) has full column rank",
          r"the objective is linear in \(x\)",
          r"its Hessian \(2A^{T}A\) is positive semidefinite for every real \(A\)"],
         3,
         r"For every real matrix, \(v^{T}(A^{T}A)v = \lVert Av \rVert^2 \ge 0\), so \(A^{T}A\) and \(2A^{T}A\) are positive semidefinite. Rank of \(A\) decides whether the Hessian is definite and whether the minimizer is unique, not whether the function is convex. The objective is quadratic, not linear. The vector \(b\) moves the linear term and does not change the Hessian.",
         ELL, A_ELL, ["convex-optimality-global"])
    b.save()


def bank_fd():
    b = Bank("finite-difference-derivatives")
    b.mc(1,
         r"The forward difference of a scalar function at \(x\) with step \(h > 0\) is",
         [r"\(\bigl(f(x + h) - f(x)\bigr) / h\)",
          r"\(\bigl(f(x + h) - f(x - h)\bigr) / h\)",
          r"\(\bigl(f(x + h) - f(x)\bigr) / (2h)\)",
          r"\(f(x + h) - f(x)\)"],
         0,
         r"The forward difference uses one neighbor on the positive side and divides by the step. Dividing by \(2h\) belongs to the central difference, and the central difference also samples the other neighbor. Omitting the division leaves a change in value, not a slope. The central numerator over a single \(h\) is twice a slope.",
         CUBIC, A_CUBIC)
    b.num(1,
          r"Let \(f(t) = t^3\). At \(t = 2\) with step \(h = 0.1\), what is the forward difference?",
          12.61, "1",
          r"\(f(2) = 8\) and \(f(2.1) = 9.261\). The quotient is \(1.261 / 0.1 = 12.61\). The true derivative \(3t^2\) at \(2\) is \(12\). The difference is larger by the leading truncation \((h/2) f''(2) = 0.6\), plus a smaller third-derivative term \(0.01\). Reporting \(12\) is the exact derivative. Reporting \(1.261\) forgets to divide by the step.",
          CUBIC, A_CUBIC)
    b.mc(1,
         "The leading truncation error of the central difference is",
         [r"proportional to \(h\), from the second derivative",
          r"proportional to \(1/h\), from round-off",
          r"exactly zero for every smooth function",
          r"proportional to \(h^2\), from the third derivative"],
         3,
         r"Adding the expansions of \(f(x+h)\) and subtracting \(f(x-h)\) cancels the even powers. The first surviving error is the third-derivative term, and dividing by \(2h\) leaves a factor \(h^2\). The second-derivative term is the one the central difference cancels; it is the leading error of the forward difference. Round-off is a separate contribution that grows as the step shrinks. The error is zero for polynomials of degree at most \(2\), not for every smooth function.",
         CUBIC, A_CUBIC)
    b.sym(2,
          r"Let \(a\) and \(h\) be real, with \(h\) nonzero. The forward difference of \(a t^2\) at \(t = 3\), using step \(h\), is an expression in the names a and h. Write that expression.",
          "6*a+a*h",
          {"a": (-4, 4), "h": (0.1, 2)},
          r"The values are \(9a\) and \(a(3 + h)^2\). Their difference, divided by \(h\), simplifies to \(a(6 + h)\)."
          "\n"
          r"• \(6a\) is the exact derivative, missing the truncation \(a h\)."
          "\n"
          r"• \(a(3 + h)^2\) is the shifted function value, not a quotient."
          "\n"
          r"• \(6a + h\) drops the factor \(a\) on the truncation term.",
          ["a*(6+h)", "6*a+h*a"],
          fig=BOWL, alt=A_BOWL)
    b.num(2,
          r"Let \(f(t) = t^3\). At \(t = 2\) with step \(h = 0.1\), what is the central difference?",
          12.01, "1",
          r"\(f(2.1) = 9.261\) and \(f(1.9) = 6.859\). The central quotient divides the difference \(2.402\) by \(0.2\), which is \(12.01\). The exact derivative is \(12\). The forward difference with the same step is \(12.61\), whose error is about sixty times larger. Reporting \(2.402\) forgets the division. Reporting \(12\) is the exact slope.",
          CUBIC, A_CUBIC)
    b.order(2,
            "Put these steps in the order used to choose a finite-difference step.",
            ["Write the truncation error as a power of the step.",
             "Estimate round-off as unit roundoff times a scale of f, divided by the step.",
             "Balance the truncation contribution against the round-off contribution.",
             "Stop shrinking the step once round-off would dominate."],
            r"Truncation falls as the step shrinks, and round-off of a difference quotient grows. The useful step is near where those two contributions meet. Shrinking past that point makes the computed slope worse. Evaluating the function once, with no error model, does not choose a step.",
            CUBIC, A_CUBIC)
    b.num(3,
          r"Let \(f(t) = t^3\). At \(t = 2\) with step \(h = 0.1\), what is the absolute error of the forward difference against the exact derivative?",
          0.61, "1",
          r"The forward difference is \(12.61\) and the exact derivative is \(12\), so the absolute error is \(0.61\). The leading term \((h/2)\cdot 12 = 0.6\) accounts for most of it, and \((h^2/6)\cdot 6 = 0.01\) accounts for the rest. The central difference with this step has absolute error \(0.01\), not \(0.61\). Reporting \(12.61\) is the difference itself.",
          CUBIC, A_CUBIC)
    b.mc(3,
         "If the leading truncation term dominates and the step is halved, the forward-difference error",
         ["drops by a factor of about four",
          "drops by a factor of about two",
          "stays the same, because the derivative does not depend on the step",
          "grows by a factor of about two"],
         1,
         r"The leading forward truncation is proportional to \(h\). Halving a step that is still in the truncation regime halves that error. A factor of four is the central difference, whose leading term carries \(h^2\). The exact derivative is independent of the step, but the error of the approximation is not. The error grows when the step grows, not when it is halved, as long as round-off is still negligible.",
         CUBIC, A_CUBIC)
    b.find_error(3,
                 r"A note claims that the forward difference of \(f(t) = t^2\) is exact for every positive step. Exactly one step is false.",
                 ["The first derivative of t squared is 2t, and the second derivative is 2.",
                  "For this quadratic, the forward difference equals the first derivative plus (h/2) times the second derivative.",
                  "The second derivative of a quadratic is zero.",
                  "Therefore the forward difference of this quadratic is exact."],
                 2,
                 r"The derivatives are \(2t\) and \(2\), and a quadratic has no third or higher derivative, so the forward difference really equals \(f' + (h/2) f''\). The false step says that second derivative is zero. It is the constant \(2\), so the forward difference is \(2t + h\), which depends on the step. The central difference of a quadratic is exact, because it cancels that second-derivative term. The forward difference is not.",
                 ["A quadratic has a constant nonzero second derivative, so the forward difference keeps a term in h.",
                  "The first derivative of t squared is not 2t.",
                  "The forward difference does not involve the second derivative."],
                 0,
                 BOWL, A_BOWL)
    b.num(4,
          r"Let \(f(t) = t^4\). At \(t = 1\) with step \(h = 0.5\), what is the central difference?",
          5, "1",
          r"\(f(1.5) = 5.0625\) and \(f(0.5) = 0.0625\). The central quotient divides \(5\) by \(2\cdot 0.5\), which is \(5\). The exact derivative \(4t^3\) at \(1\) is \(4\). The forward difference \((5.0625 - 1) / 0.5 = 8.125\) is much farther from \(4\). Reporting \(4\) is the exact derivative. Reporting \(5.0625\) is a function value.",
          CUBIC, A_CUBIC, ["heavy-ball-method"])
    b.mc(4,
         "Taking the step extremely small makes a finite difference worse because",
         [r"truncation grows as the step shrinks",
          r"the exact derivative changes with the step",
          r"subtracting two nearly equal function values loses digits, and dividing by a tiny step amplifies that loss",
          r"a central difference is undefined for small steps"],
         2,
         r"Unit roundoff in the function values, divided by the step, grows like \(1/h\). Past the balancing step, that growth beats the improvement in truncation. Truncation itself gets smaller as the step shrinks. The exact derivative does not depend on a numerical step. The central formula is defined for every nonzero step; the trouble is accuracy, not existence.",
         CUBIC, A_CUBIC, ["nesterov-accelerated-gradient"])
    b.mc(4,
         "For a forward difference limited by round-off of size unit roundoff over the step, the step that balances a first-order truncation scales like",
         [r"the square root of unit roundoff",
          r"unit roundoff itself",
          r"the cube root of unit roundoff",
          r"the reciprocal of unit roundoff"],
         0,
         r"Set a constant times \(h\) equal to unit roundoff over \(h\). The balance is a step on the order of the square root of unit roundoff. The cube root is the analogous balance for a central difference, whose truncation carries \(h^2\). Using unit roundoff with no square root is far too small for a forward difference, and the reciprocal is enormous. With unit roundoff \(10^{-8}\), the forward scale is \(10^{-4}\).",
         CUBIC, A_CUBIC, ["heavy-ball-method"])
    b.save()


def bank_graph():
    b = Bank("computational-graphs")
    b.mc(1,
         "A computational graph for a scalar formula is",
         ["a picture of the level sets of the formula",
          "a directed acyclic graph whose nodes are elementary operations",
          "the Hessian of the formula",
          "a list of random sample points"],
         1,
         r"Each node is one elementary step, such as an addition or a product, and edges record which values that step reads. The graph is acyclic because a value is computed from earlier values. Level sets are a picture of the function, not of the arithmetic. The Hessian is a matrix of second derivatives. Sample points belong to a numerical check, not to the graph.",
         GRAPH, A_GRAPH)
    b.num(1,
          r"Break \(f(x, y) = (xy + 3)^2 + x\) into the product \(p = xy\), the sum \(s = p + 3\), the square \(q = s^2\), and \(f = q + x\). At \((2, 4)\), what is \(f\)?",
          123, "1",
          r"The product is \(8\), the sum is \(11\), and the square is \(121\). Adding the first input gives \(121 + 2 = 123\). Stopping at the square reports \(121\). Stopping at the sum reports \(11\). The product \(8\) is only the first node.",
          GRAPH, A_GRAPH)
    b.mc(1,
         "Symbolic differentiation, numeric differentiation, and automatic differentiation differ in that",
         ["only numeric differentiation uses the chain rule",
          "only symbolic differentiation can be applied to a product",
          "symbolic builds an expression, numeric samples the function, and automatic applies the chain rule on the evaluated graph",
          "automatic differentiation replaces every operation by a finite difference"],
         2,
         r"Symbolic differentiation rewrites the expression and can suffer expression swell. Numeric differentiation only evaluates the function, then forms a difference quotient, and it carries truncation and round-off. Automatic differentiation keeps the graph, evaluates it, and applies the local derivative of each node, so the result is exact up to round-off of the arithmetic. All three can handle a product. The chain rule is the engine of the symbolic and automatic routes, not of a bare difference quotient.",
         GRAPH, A_GRAPH)
    b.order(2,
            r"Put these steps in the order used to evaluate \(f = (xy + 3)^2 + x\) from its graph.",
            ["Multiply the two inputs.",
             "Add 3 to that product.",
             "Square the sum.",
             "Add the first input to the square."],
            r"Each node reads values that earlier nodes have already produced, so the order is a topological order of the graph. Squaring before the addition would square the product and compute a different function. Adding the first input at the beginning would not match this graph either.",
            GRAPH, A_GRAPH)
    b.num(2,
          r"Using the same graph \(f = (xy + 3)^2 + x\), what is \(f(2, 5)\)?",
          171, "1",
          r"The product is \(10\), the sum is \(13\), and the square is \(169\). Adding the first input gives \(171\). The value at \((2, 4)\) was \(123\), which is this function at a different point. The square \(169\) forgets the final addition. The sum \(13\) is an intermediate node.",
          GRAPH, A_GRAPH)
    b.mc(2,
         "A node may be evaluated when",
         ["every node that it reads has already been evaluated",
          "every node that reads it has already been evaluated",
          "the output value is already known",
          "its local derivative has already been computed"],
         0,
         r"Forward evaluation respects the arrows: a node waits for its inputs. The nodes that read it are downstream and have to wait for it. The output is the last value, not a prerequisite of the first node. Local derivatives are a later pass. They need the primal values, so they do not come first.",
         GRAPH, A_GRAPH)
    b.sym(3,
          r"The output of the graph 'multiply x by y, add a, square the sum, then add x' is an expression in the names x, y, and a. Write that expression.",
          "(x*y+a)*(x*y+a)+x",
          {"x": (-3, 3), "y": (-3, 3), "a": (-3, 3)},
          r"The product plus \(a\), squared, plus the first input, is \((xy + a)^2 + x\)."
          "\n"
          r"• \((xy + a)^2\) stops before the final addition of \(x\)."
          "\n"
          r"• \(xy + a + x\) never squares."
          "\n"
          r"• \((x + y + a)^2 + x\) adds the inputs before multiplying them.",
          ["(x*y+a)**2+x", "x+(x*y+a)**2"],
          fig=GRAPH, alt=A_GRAPH)
    b.num(3,
          r"Using the graph \(f = (xy + 3)^2 + x\), what is the intermediate sum \(s = xy + 3\) at \((1, 7)\)?",
          10, "1",
          r"The product is \(7\), and adding \(3\) gives \(10\). The square of that sum is \(100\), and the output is \(101\). The question asks for the sum, not the output. Reporting \(7\) stops at the product. Reporting \(101\) runs the whole graph.",
          GRAPH, A_GRAPH)
    b.mc(3,
         "Expression swell is a reason to prefer automatic differentiation when",
         ["the function is already a single addition",
          "only one function value is required, and no derivative",
          "the formula is a low-degree polynomial in one variable",
          "the expanded symbolic derivative would be much larger than the graph"],
         3,
         r"The graph stays about as large as the original formula, while the expanded derivative of a long composition can be huge. A single addition has a trivial derivative either way. A bare function value needs no differentiation method. A short polynomial in one variable is cheap symbolically. The advantage shows up when the chain is long.",
         GRAPH, A_GRAPH)
    b.find_error(4,
                 r"Someone evaluates the graph of \(f = (xy + 3)^2 + x\) at a generic input. Exactly one step does not match the graph.",
                 ["Multiply the two inputs and call the product p.",
                  "Add 3 to p and call the sum s.",
                  "Square p and call the result q.",
                  "Add the first input to q and call the result f."],
                 2,
                 r"The graph squares the sum \(s = xy + 3\), not the product. The product, the addition of \(3\), and the final addition of the first input all match the formula. Squaring \(p\) computes \((xy)^2 + x\), which drops the cross terms that the binomial expansion of \((xy + 3)^2\) would have kept.",
                 ["The square should be applied to the sum, not to the product.",
                  "The product of the inputs is the wrong first operation.",
                  "The graph does not add the first input at the end."],
                 0,
                 GRAPH, A_GRAPH, ["ad-forward-mode"])
    b.num(4,
          r"Using the graph \(f = (xy + 3)^2 + x\), what is \(f(1, 7)\)?",
          101, "1",
          r"The sum \(xy + 3\) equals \(10\), its square is \(100\), and adding the first input gives \(101\). The intermediate sum \(10\) is not the output. The square \(100\) forgets the final addition. At \((2, 4)\) the same graph produced \(123\).",
          GRAPH, A_GRAPH, ["ad-reverse-mode"])
    b.mc(4,
         "Once a formula is a computational graph, a derivative can be obtained by",
         ["replacing the graph with its level-set picture",
          "attaching the local derivative of each elementary node and combining them by the chain rule",
          "counting the nodes",
          "evaluating the output and ignoring the intermediate nodes"],
         1,
         r"Each elementary operation has a small derivative, and the multivariable chain rule multiplies those local factors along the graph. That is the step automatic differentiation takes. A level-set picture does not encode the arithmetic. The node count is not a derivative. The output value alone, with the intermediates thrown away, is enough for a finite difference and not enough for an exact chain-rule sweep.",
         GRAPH, A_GRAPH, ["hessian-vector-products-ad"])
    b.save()


def bank_forward():
    b = Bank("ad-forward-mode")
    b.mc(1,
         "Forward-mode automatic differentiation computes a directional derivative by",
         ["finite-differencing the output",
          "building the fully expanded symbolic gradient first",
          "pushing a tangent forward through the graph, beside the primal values",
          "solving a linear system whose matrix is the Hessian"],
         2,
         r"Each node carries its value and a tangent, and the tangent is the directional derivative of that node. One sweep with a chosen input seed returns the directional derivative of the output. A finite difference never uses the local derivatives. The expanded symbolic gradient is a different method. A Hessian linear system is a Newton step, which needs second derivatives.",
         RAY, A_RAY)
    b.num(1,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the forward-mode tangent of the output for the seed \((1, 0)\)?",
          89, "1",
          r"The sum \(s = xy + 3\) equals \(11\). Its tangent is the product rule on \(xy\) with seed \((1, 0)\), which is \(4\). The square has tangent \(2\cdot 11\cdot 4 = 88\). The output adds \(x\), so it adds the seed \(1\), and the output tangent is \(89\). That matches \(\partial f/\partial x = 2(xy + 3)y + 1 = 89\). Reporting \(88\) forgets the tangent of the added \(x\). Reporting \(4\) stops at the product.",
          GRAPH, A_GRAPH)
    b.mc(1,
         r"Where \(f\) is differentiable, the output tangent for an input seed \(d\) equals",
         [r"\(\nabla f(x)^{T} d\)",
          r"\(\nabla f(x)\) itself, for every seed",
          r"the Hessian times \(d\)",
          r"the primal output value"],
         0,
         r"Forward mode returns one directional derivative, and differentiability writes that derivative as the inner product of the gradient with the seed. The gradient itself would require one seed per coordinate, or a reverse sweep. The Hessian times \(d\) is a second-derivative object. The primal value is computed alongside the tangent and is not the tangent.",
         PAIR, A_PAIR)
    b.order(2,
            "Put these steps in the order of one forward sweep.",
            ["Seed the input tangents with the chosen direction.",
             "Visit each node after its parents, carrying the primal value and the tangent.",
             "Apply the local linearization of that node's operation to the parent tangents.",
             "Read the output tangent as the directional derivative."],
            r"The seed is the direction. Each later node needs its parents' values and tangents, then applies the derivative of its own operation. The output tangent is the answer, so it is last. Reading it before the intermediate tangents exist skips the chain rule.",
            GRAPH, A_GRAPH)
    b.num(2,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the forward-mode tangent of the output for the seed \((0, 1)\)?",
          44, "1",
          r"The partial derivative in \(y\) is \(2(xy + 3)x = 2\cdot 11\cdot 2 = 44\). The product \(xy\) has tangent \(x\cdot 1 = 2\), the sum keeps that tangent, and the square multiplies by \(2\cdot 11\), giving \(44\). The final addition of \(x\) adds a zero tangent because the seed has no \(\dot x\). Reporting \(89\) is the other partial derivative. Reporting \(11\) is the primal sum.",
          RAY, A_RAY)
    b.sym(2,
          r"Consider \(f(t) = (a t + b)^2\). The forward-mode tangent at a general \(t\), for the seed \(1\), is an expression in the names a, b, and t. Write that expression.",
          "2*(a*t+b)*a",
          {"a": (-3, 3), "b": (-3, 3), "t": (-3, 3)},
          r"The inside \(a t + b\) has tangent \(a\) when the seed is \(1\). The square multiplies by twice the inside value, so the output tangent is \(2(at + b)a\)."
          "\n"
          r"• \(2(at + b)\) forgets the tangent of the inside."
          "\n"
          r"• \(a\) is only the inside tangent."
          "\n"
          r"• \((at + b)^2\) is the primal value.",
          ["2*a*(a*t+b)", "(2*a)*(a*t+b)"],
          fig=BOWL, alt=A_BOWL)
    b.num(3,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the forward-mode tangent of the output for the seed \((1, 1)\)?",
          133, "1",
          r"The two partial derivatives are \(89\) and \(44\). The seed \((1, 1)\) adds them, giving \(133\). Linearity of the tangent in the seed is the check: the sum of the two earlier seeds is this seed, so the tangents add. Reporting \(89\) or \(44\) drops one coordinate of the seed. The primal value \(123\) is not a tangent.",
          PAIR, A_PAIR)
    b.mc(3,
         r"For a scalar function of \(n\) inputs, forward mode produces the full gradient at a cost of about",
         [r"one sweep, whatever \(n\) is",
          r"\(n^2\) sweeps",
          "one sweep per Hessian entry",
          r"\(n\) sweeps, one seed per input coordinate"],
         3,
         r"Each sweep returns one directional derivative. The coordinate seeds recover the partial derivatives one at a time, so a full gradient costs about \(n\) sweeps. One sweep is enough only for a single direction, which is the whole gradient only when \(n = 1\). A square number of sweeps is the wrong count for first derivatives. Hessian entries are a second-derivative question.",
         GRAPH, A_GRAPH)
    b.find_error(3,
                 r"A forward sweep of \(f = (xy + 3)^2 + x\) at \((2, 4)\) with seed \((1, 0)\) is written out below. Exactly one step is false.",
                 ["The product p = xy has tangent equal to the tangent of x times y, plus x times the tangent of y.",
                  "With this seed that product tangent equals 4.",
                  "The square of the sum s = 11 then has tangent 2 * 11 * 4 = 88.",
                  "The output adds x, so the output tangent stays 88."],
                 3,
                 r"The product rule is right, and the seed \((1, 0)\) makes the product tangent \(1\cdot 4 + 2\cdot 0 = 4\). The square then contributes \(88\). The output is that square plus \(x\), so the output tangent is \(88\) plus the seed of \(x\), which is \(1\). The false step drops that \(1\). The directional derivative is \(89\).",
                 ["The output also adds the tangent of x, so the tangent is 89 rather than 88.",
                  "The product rule for a tangent is wrong.",
                  "The square's tangent should not multiply by 2s."],
                 0,
                 GRAPH, A_GRAPH)
    b.num(4,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((1, 2)\), what is the forward-mode tangent of the output for the seed \((1, 0)\)?",
          21, "1",
          r"The sum \(xy + 3\) equals \(5\). The partial derivative in \(x\) is \(2\cdot 5\cdot 2 + 1 = 21\). The product tangent for this seed is \(2\), the square multiplies by \(2\cdot 5\), giving \(20\), and the added \(x\) contributes \(1\). Reporting \(20\) forgets that last \(1\). At \((2, 4)\) the same seed produced \(89\).",
          RAY, A_RAY, ["hessian-vector-products-ad"])
    b.mc(4,
         "Forward mode is the cheaper choice when",
         ["one scalar output depends on hundreds of inputs and the full gradient is required",
          "there are few inputs and many outputs, and each output needs a directional derivative",
          "the Hessian is required entrywise and there is only one input",
          "only the primal value is required"],
         1,
         r"A forward sweep costs about as much as one function evaluation and returns one directional derivative of every output at once. Few directions and many outputs therefore favor forward mode. A scalar of hundreds of inputs, when the full gradient is required, favors one reverse sweep. A primal value needs no tangent. Entrywise Hessians are a different product.",
         PAIR, A_PAIR, ["hessian-vector-products-ad"])
    b.multi(4,
            "Which statements hold for forward-mode automatic differentiation?",
            ["One sweep with seed d returns the directional derivative in the direction d.",
             "A full gradient of one scalar of n inputs needs n seeds in general.",
             "The output tangent is known before any primal value is computed.",
             "Forward mode avoids the chain rule."],
            [0, 1],
            r"The output tangent is the directional derivative of the seed, and the coordinate seeds recover a gradient in \(n\) sweeps."
            "\n"
            r"• The local linearization uses the primal value, so the tangent does not arrive before the forward evaluation."
            "\n"
            r"• Each node applies the derivative of its operation. That is the chain rule, evaluated rather than expanded.",
            GRAPH, A_GRAPH, ["hessian-vector-products-ad"])
    b.save()


def bank_reverse():
    b = Bank("ad-reverse-mode")
    b.mc(1,
         "Reverse-mode automatic differentiation computes a gradient by",
         ["accumulating adjoints from the output back toward the inputs",
          "pushing one tangent from the inputs all the way to the output, once",
          "replacing each node by a central difference",
          "forming the symbolic derivative and then canceling terms by hand"],
         0,
         r"After the forward values are known, each node receives an adjoint, the partial derivative of the scalar output with respect to that node. The adjoint is sent back to the parents through the local derivative. One forward tangent is forward mode. Central differences are numeric differentiation. Hand cancellation is symbolic differentiation.",
         GRAPH, A_GRAPH)
    b.num(1,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the reverse-mode adjoint of the input \(x\)?",
          89, "1",
          r"The output adjoint is \(1\). The square \(s^2\) with \(s = 11\) sends adjoint \(22\) back to \(s\), and that adjoint reaches the product \(xy\). The product sends \(22 \cdot y = 88\) to \(x\), and the final addition of \(x\) sends another \(1\). The total is \(89\), which is \(\partial f/\partial x\). Reporting \(88\) keeps only the path through the product. Reporting \(22\) stops at the adjoint of the sum.",
          GRAPH, A_GRAPH)
    b.mc(1,
         r"The adjoint \(\bar v\) of a node \(v\) means",
         [r"the forward tangent of \(v\)",
          r"the primal value of \(v\)",
          r"the partial derivative of the scalar output with respect to \(v\)",
          r"the number of parents of \(v\)"],
         2,
         r"By definition the adjoint is how the output changes when that node is nudged, with the graph otherwise fixed. The forward tangent is a different seed, propagating in the other direction. The primal value is what the forward pass stored. The parent count is the shape of the graph, not a derivative.",
         GRAPH, A_GRAPH)
    b.order(2,
            "Put these steps in the order of a reverse sweep for a scalar output.",
            ["Run the forward evaluation and store each node value.",
             "Seed the output adjoint with 1.",
             "Visit nodes from the output back toward the inputs.",
             "Add each local derivative times the node adjoint into the adjoints of the parents."],
            r"Reverse mode needs the primal values, then a unit adjoint on the output, then a backward topological order. Each visit distributes the adjoint to the parents. Seeding the output before the forward values exist leaves the local derivatives without numbers. Visiting in forward order is the tangent sweep.",
            GRAPH, A_GRAPH)
    b.num(2,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the reverse-mode adjoint of the input \(y\)?",
          44, "1",
          r"The sum \(s = 11\) has adjoint \(2\cdot 11\cdot 1 = 22\). The product \(xy\) sends \(22\cdot x = 44\) to \(y\). There is no other edge into \(y\), so the adjoint is \(44\), matching \(\partial f/\partial y\). The adjoint of \(x\) is \(89\), because \(x\) also appears in the final addition. Reporting \(22\) stops one node too early.",
          RAY, A_RAY)
    b.sym(2,
          r"For \(f(x, y) = (xy + a)^2\), the reverse-mode adjoint of the input \(x\) is an expression in the names x, y, and a. Write that expression.",
          "2*(x*y+a)*y",
          {"x": (-3, 3), "y": (-3, 3), "a": (-3, 3)},
          r"The inside \(s = xy + a\) has adjoint \(2s\) when the output adjoint is \(1\). The product then multiplies that adjoint by \(y\) on the way to \(x\)."
          "\n"
          r"• \(2(xy + a)x\) is the adjoint of \(y\), not of \(x\)."
          "\n"
          r"• \(2(xy + a)\) stops before the product rule sends the adjoint onto an input."
          "\n"
          r"• \((xy + a)^2\) is the primal value.",
          ["2*y*(x*y+a)", "y*2*(x*y+a)"],
          fig=GRAPH, alt=A_GRAPH)
    b.num(3,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((1, 2)\), what is the reverse-mode adjoint of the input \(y\)?",
          10, "1",
          r"The sum \(s = xy + 3\) equals \(5\), so its adjoint is \(2\cdot 5 = 10\). The product sends \(10\cdot x = 10\) to \(y\). The same number is \(\partial f/\partial y = 2sx = 10\). The adjoint of \(x\) at this point is \(2\cdot 5\cdot 2 + 1 = 21\). Reporting \(5\) is the primal sum.",
          RAY, A_RAY)
    b.find_error(3,
                 r"A reverse sweep of \(f = (xy + 3)^2 + x\) at \((2, 4)\) is written out below. Exactly one step is false.",
                 ["The forward value of the sum s = xy + 3 is 11.",
                  "The adjoint of s is 2 * 11 * 1 = 22.",
                  "The product sends 22 * y = 88 into the adjoint of x.",
                  "The final adjoint of x is 88, because x appears only in the product."],
                 3,
                 r"The forward sum, the adjoint \(22\), and the contribution \(88\) through the product are all correct. The false step says \(x\) appears only in the product. The output also adds \(x\), and that edge contributes \(1\). The adjoint of \(x\) is \(89\). Dropping a path is the usual reverse-mode mistake when a variable is used twice.",
                 ["x is also added at the output, so its adjoint is 89 rather than 88.",
                  "The adjoint of a square is not twice the inside value.",
                  "The forward value of the sum is not 11."],
                 0,
                 GRAPH, A_GRAPH)
    b.mc(3,
         "The practical cost of reverse mode, compared with a single function evaluation, is that",
         ["it needs about n extra full evaluations for n inputs",
          "it needs one backward sweep and storage, or recomputation, of the forward values",
          "it needs no forward values at all",
          "it costs about n squared function evaluations"],
         1,
         r"The backward sweep is a small constant times one function evaluation, once the forward values are available for the local derivatives. Storing them is the memory cost. Recomputing them is the time alternative. A factor of \(n\) is the forward-mode price of a full gradient. A square factor is not the reverse-mode price. The local derivatives are numbers computed from the forward values, so those values cannot be skipped.",
         GRAPH, A_GRAPH)
    b.num(4,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the adjoint of the intermediate sum \(s = xy + 3\)?",
          22, "1",
          r"The output adjoint is \(1\), and \(s\) is squared, so the adjoint of \(s\) is \(2\cdot 11\cdot 1 = 22\). That adjoint later splits into \(88\) for \(x\) through the product and \(44\) for \(y\). The adjoint of \(x\) is \(89\), not \(22\). The primal sum is \(11\).",
          GRAPH, A_GRAPH, ["hessian-vector-products-ad"])
    b.mc(4,
         "Reverse mode is the cheaper route to a full gradient when",
         ["the map has many outputs and one input",
          "only one directional derivative is required",
          "the function is a single multiplication",
          "one scalar depends on many inputs"],
         3,
         r"One reverse sweep returns every partial derivative of one scalar. Many inputs and one output is the case where that beats \(n\) forward sweeps. Many outputs with one input favor forward mode, which differentiates every output in one tangent. A single directional derivative is one forward seed. A single multiplication is too small for the choice to matter.",
         PAIR, A_PAIR, ["backprop-neural-network"])
    b.multi(4,
            "Which statements hold for reverse-mode automatic differentiation of a scalar output?",
            ["One reverse sweep yields every partial derivative of that output.",
             "The forward values have to be stored or recomputed.",
             "Reverse mode is always cheaper than forward mode, including a function of one input.",
             "Adjoints move from a node back to its parents."],
            [0, 1, 3],
            r"The sweep returns the full gradient, it needs the primal trace, and each adjoint is distributed to the parents through the local derivative."
            "\n"
            r"• With a single input the two modes do essentially the same work. Reverse mode is not universally cheaper. It wins when the output is a scalar and the input is wide.",
            GRAPH, A_GRAPH, ["backprop-neural-network"])
    b.save()


def bank_hvp():
    b = Bank("hessian-vector-products-ad")
    b.mc(1,
         r"A Hessian-vector product \(H_f(x)\, d\) can be computed without forming \(H_f(x)\) by",
         ["finite-differencing every entry of the Hessian separately",
          "running forward mode on a reverse-mode gradient, in the direction d",
          "reading the gradient and calling it the Hessian",
          "replacing the Hessian by the identity"],
         1,
         r"The gradient is a vector-valued function of \(x\). Forward mode applied to that function, with seed \(d\), returns the derivative of the gradient in the direction \(d\), which is the Hessian times \(d\). Forming every entry is the expensive route this product avoids. The gradient is not the Hessian. The identity is a different matrix.",
         HESS, A_HESS)
    b.num(1,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the first entry of the Hessian times \((1, 0)\)?",
          32, "1",
          r"The Hessian is \(\begin{bmatrix} 32 & 38 \\ 38 & 8 \end{bmatrix}\). Times \((1, 0)\) it returns the first column, whose first entry is \(32\). That entry is \(\partial^2 f/\partial x^2 = 2y^2 = 32\). The second entry of the same product is \(38\). The gradient entry \(89\) is a first derivative, not a second derivative.",
          HESS, A_HESS)
    b.mc(1,
         r"If \(g(x) = \nabla f(x)\), the product \(H_f(x)\, d\) equals",
         [r"\(g(x)\) dotted with \(d\)",
          r"\(f(x + d) - f(x)\)",
          r"the adjoint of \(f\) with no direction",
          r"the directional derivative of \(g\) in the direction \(d\)"],
         3,
         r"Differentiating the gradient map in the direction \(d\) is exactly the definition of the Jacobian of \(g\) times \(d\), and that Jacobian is the Hessian. The inner product of the gradient with \(d\) is a first directional derivative of \(f\). A plain function difference is a finite-difference approximation of a first derivative. An adjoint with no direction is the gradient.",
         PAIR, A_PAIR)
    b.sym(2,
          r"Let \(f(x, y) = a x^2 + b y^2\). For a direction \((u, v)\), the sum of the two entries of the Hessian times that direction is an expression in the names a, b, u, and v. Write that expression.",
          "2*a*u+2*b*v",
          {"a": (-3, 3), "b": (-3, 3), "u": (-3, 3), "v": (-3, 3)},
          r"The Hessian is diagonal with entries \(2a\) and \(2b\). Times \((u, v)\) it is \((2au,\ 2bv)\), and the sum of those entries is \(2au + 2bv\)."
          "\n"
          r"• \(2au\) is only the first entry."
          "\n"
          r"• \(a u^2 + b v^2\) is the function, not a Hessian-vector product."
          "\n"
          r"• \(2a + 2b\) ignores the direction.",
          ["2*(a*u+b*v)", "2*b*v+2*a*u"],
          fig=HESS, alt=A_HESS)
    b.num(2,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the second entry of the Hessian times \((1, 0)\)?",
          38, "1",
          r"The first column is \((32, 38)\). The second entry is the mixed partial \(2(2xy + 3) = 2(16 + 3) = 38\). The bottom-right entry \(8\) is \(2x^2\), and it multiplies the second coordinate of the direction, which is zero in this product. Reporting \(32\) is the other entry of the same product. Reporting \(8\) is the unused diagonal entry.",
          HESS, A_HESS)
    b.order(2,
            "Put these steps in the order of a forward-over-reverse Hessian-vector product.",
            ["Evaluate the function and store the forward trace.",
             "Run a reverse sweep so the gradient is itself a computation.",
             "Seed a forward tangent on that gradient computation, in the direction d.",
             "Read the tangent of the gradient as the Hessian times d."],
            r"Reverse mode first turns the gradient into values and local derivatives. Forward mode then differentiates that vector map in the direction \(d\). The tangent of the gradient is the product. Seeding the tangent before the gradient computation exists skips the reverse sweep. The product is the last object, not the first.",
            GRAPH, A_GRAPH)
    b.num(3,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), what is the first entry of the Hessian times \((1, 1)\)?",
          70, "1",
          r"The two columns are \((32, 38)\) and \((38, 8)\). Their sum is \((70, 46)\). The first entry is \(32 + 38 = 70\). The second entry of the same product is \(46\). The quadratic form \(d^{T} H d\) for this direction is \(70 + 46 = 116\), which adds both entries. Reporting \(32\) uses only the first column.",
          HESS, A_HESS)
    b.find_error(3,
                 r"A note multiplies the Hessian of \(f = (xy + 3)^2 + x\) at \((2, 4)\) by \((1, 0)\). Exactly one step is false.",
                 ["The Hessian at that point has rows (32, 38) and (38, 8).",
                  "The product with (1, 0) is the first column.",
                  "The first column is (32, 8).",
                  "A forward-over-reverse sweep returns that same product without writing the other column."],
                 2,
                 r"The Hessian entries are right, and multiplication by \((1, 0)\) really returns the first column. A forward-over-reverse sweep returns the product without forming the other column. The false step swaps the off-diagonal \(38\) with the other diagonal entry \(8\). The first column is \((32, 38)\).",
                 ["The first column is (32, 38). The entry 8 is the other diagonal entry.",
                  "The Hessian rows are wrong.",
                  "Multiplying by (1, 0) does not return a column."],
                 0,
                 HESS, A_HESS)
    b.mc(3,
         r"The full Hessian of a scalar function of \(n\) inputs can be recovered from",
         ["about n Hessian-vector products, one per coordinate direction",
          "one Hessian-vector product",
          "n squared function evaluations and no derivatives",
          "a single reverse sweep"],
         0,
         r"The product with the \(i\)th coordinate vector is the \(i\)th column. Those \(n\) columns are the matrix. One product is one column, or one linear combination of columns. A reverse sweep returns the gradient, which is first-order. Filling the matrix by function values alone is possible with finite differences and costs far more than \(n\) gradient-like products.",
         HESS, A_HESS)
    b.num(4,
          r"Let \(f(x, y) = (xy + 3)^2 + x\). At \((2, 4)\), for \(d = (1, 1)\), what is \(d^{T} H_f d\)?",
          116, "1",
          r"The product \(H d\) is \((70, 46)\). The inner product with \(d\) is \(70 + 46 = 116\). That scalar is also the second directional derivative of \(f\). Reporting \(70\) or \(46\) stops at one entry of the product. Reporting \(133\) is the first directional derivative \(\nabla f^{T} d\), not the second.",
          PAIR, A_PAIR, ["newton-method-optimization"])
    b.mc(4,
         "Large-scale Newton methods ask for Hessian-vector products because",
         ["the Newton step is the gradient itself",
          "forming the Hessian is cheaper than one product",
          "an iterative linear solver needs only matrix-vector products with the Hessian",
          "the Hessian of a nonlinear function is always diagonal"],
         2,
         r"The Newton step solves \(H_f(x)\, d = -\nabla f(x)\). Conjugate gradients and related solvers never need \(H_f\) except through products \(H_f v\). Forming the dense matrix costs about \(n\) products and then stores \(n^2\) entries, which is the expense the product form avoids. The Newton step is not the gradient. A general Hessian is not diagonal.",
         HESS, A_HESS, ["conjugate-gradient-method"])
    b.multi(4,
            "Which statements describe a Hessian-vector product?",
            ["Forward-over-reverse returns the Hessian times d at a cost comparable to one gradient.",
             "Reverse-over-forward, with the direction held constant, also returns the Hessian times that direction.",
             "The product is the directional derivative of the gradient.",
             "One product returns every entry of the Hessian."],
            [0, 1, 2],
            r"Forward mode on the gradient, or reverse mode on the scalar directional derivative with a fixed direction, both return \(H d\). That vector is the directional derivative of the gradient, and the cost stays on the order of one gradient."
            "\n"
            r"• One product returns one vector. The full matrix takes a product for each column.",
            PAIR, A_PAIR, ["second-order-optimality"])
    b.save()


def bank_backprop():
    b = Bank("backprop-neural-network")
    b.mc(1,
         "Backpropagation on a network loss is",
         ["forward-mode differentiation with one seed per weight",
          "a finite difference for each weight",
          "reverse-mode automatic differentiation on the network graph",
          "the second-order convexity test applied to the weights"],
         2,
         r"The loss is a scalar and the weights are many inputs, so one reverse sweep produces every weight gradient. Forward mode would spend a sweep per weight. Finite differences would spend extra evaluations and add truncation. The second-order test is a statement about Hessians, not the algorithm that computes a gradient.",
         NET, A_NET)
    b.num(1,
          r"A scalar network uses a positive-part activation. With input \(3\), first weight \(2\), first bias \(-1\), output weight \(4\), output bias \(1\), and target \(11\), the prediction is \(21\). For the loss \(\tfrac12(\hat y - y)^2\), what is the partial derivative of the loss with respect to the output weight?",
          50, "1",
          r"The residual is \(21 - 11 = 10\), and that is the adjoint of the prediction for this half-square loss. The hidden value is \(5\), so the output weight receives \(10\cdot 5 = 50\). Twice that, \(100\), would be the derivative of the square without the one half. The adjoint of the prediction, \(10\), has not yet been multiplied by the hidden value. The first-layer weight receives \(120\), which is a different parameter.",
          NET, A_NET)
    b.mc(1,
         "On a positive input, the local derivative of the positive-part activation is",
         ["1",
          "0",
          "equal to the input",
          "equal to the upstream adjoint"],
         0,
         r"The positive-part function agrees with the identity on positive numbers, so its derivative there is \(1\). It is \(0\) on negative numbers, which blocks the upstream adjoint. The derivative is not the input itself, and it is not the adjoint. The adjoint of the pre-activation is the hidden adjoint multiplied by this local factor.",
         NET, A_NET)
    b.order(2,
            "Put these steps in the order of backpropagation through a two-layer network.",
            ["Evaluate the forward pass and store the pre-activation, the hidden value, and the prediction.",
             "Seed the loss and obtain the adjoint of the prediction from the residual.",
             "Send that adjoint through the output weight to the hidden unit.",
             "Multiply by the activation derivative and by the input to reach the first weight."],
            r"Reverse mode needs the forward values first. The residual seeds the prediction, the output weight carries that adjoint to the hidden unit, and the activation derivative then opens or blocks the path to the first weight. Multiplying by the input is the last local factor, because the first weight enters as weight times input.",
            NET, A_NET)
    b.num(2,
          r"Use the same network and the same half-square loss: input \(3\), first weight \(2\), first bias \(-1\), output weight \(4\), output bias \(1\), target \(11\). The pre-activation is positive. What is the partial derivative of the loss with respect to the first weight?",
          120, "1",
          r"The prediction adjoint is \(10\). Times the output weight \(4\), the hidden adjoint is \(40\). The positive-part derivative is \(1\), and the input is \(3\), so the first weight receives \(40\cdot 3 = 120\). The output weight receives \(50\). Stopping at the hidden adjoint reports \(40\). Using a zero activation derivative would report \(0\), which is the blocked case and not this one.",
          NET, A_NET)
    b.sym(2,
          r"For the scalar loss \(\tfrac12 (w t - y)^2\), the derivative with respect to \(w\) is an expression in the names w, t, and y. Write that expression.",
          "(w*t-y)*t",
          {"w": (-3, 3), "t": (0.5, 3), "y": (-3, 3)},
          r"The residual is \(wt - y\), and the half square makes that residual the adjoint of the prediction. The weight enters multiplied by \(t\), so the derivative is the residual times \(t\)."
          "\n"
          r"• \((wt - y) w\) differentiates in the input instead of the weight."
          "\n"
          r"• \(wt - y\) stops before multiplying by the other factor."
          "\n"
          r"• \(\tfrac12 (wt - y)^2\) is the loss, not its derivative.",
          ["t*(w*t-y)", "w*t*t-y*t"],
          fig=NET, alt=A_NET)
    b.num(3,
          r"Use the same network and half-square loss: input \(3\), first weight \(2\), first bias \(-1\), output weight \(4\), output bias \(1\), target \(11\). The pre-activation is positive. What is the partial derivative of the loss with respect to the first bias?",
          40, "1",
          r"The hidden adjoint is \(40\), and the positive-part derivative is \(1\). A bias enters with local factor \(1\), so its partial derivative equals that pre-activation adjoint, \(40\). The first weight multiplies the same adjoint by the input \(3\) and gets \(120\). The output bias gets the prediction adjoint \(10\), because the output bias also has local factor \(1\) on a different node.",
          NET, A_NET)
    b.find_error(3,
                 r"Backpropagation of the half-square loss on this network is written out below. The prediction is \(21\), the target is \(11\), the output weight is \(4\), the hidden value is \(5\), and the pre-activation is \(5\). Exactly one step is false.",
                 ["The adjoint of the prediction is 10.",
                  "The adjoint of the hidden unit is 10 times 4, which is 40.",
                  "The pre-activation is positive, so the positive-part derivative is 0.",
                  "The adjoint of the first weight equals the pre-activation adjoint times the input."],
                 2,
                 r"The residual \(10\) is the prediction adjoint, and times the output weight it is the hidden adjoint \(40\). The first weight really does receive the pre-activation adjoint times the input. The false step gives the positive-part function derivative \(0\) on a positive pre-activation. The derivative there is \(1\). Derivative \(0\) is the negative side, and it would block the first-layer weights.",
                 ["A positive pre-activation has positive-part derivative 1, not 0.",
                  "The prediction adjoint should be twice the residual.",
                  "The hidden adjoint should be the prediction adjoint times the hidden value."],
                 0,
                 NET, A_NET)
    b.mc(3,
         "If the pre-activation is negative, the positive-part activation blocks the gradient of",
         ["the output bias only",
          "the output weight only",
          "every weight, including the output weight",
          "the first-layer weights, while the output layer still sees a zero hidden value"],
         3,
         r"A negative pre-activation has local derivative \(0\), so the adjoint that reaches the hidden unit is multiplied by zero before it touches the first weight and the first bias. The output weight's local factor is the hidden value, which is also zero, so that weight's partial derivative is zero too, but for a different reason: the stored hidden value, not the activation derivative. The output bias has local factor \(1\) and still receives the prediction adjoint. The claim that every parameter is blocked forgets the output bias.",
         NET, A_NET)
    b.num(4,
          r"A second network uses input \(2\), first weight \(3\), first bias \(0\), output weight \(-1\), output bias \(8\), and target \(-4\). The pre-activation is positive and the prediction is \(2\). For the half-square loss, what is the partial derivative with respect to the first weight?",
          -12, "1",
          r"The residual is \(2 - (-4) = 6\). Times the output weight \(-1\), the hidden adjoint is \(-6\). The activation derivative is \(1\) and the input is \(2\), so the first weight receives \(-12\). The output weight receives \(6\cdot 6 = 36\), using the hidden value \(6\). Reporting \(12\) drops the sign of the output weight. Reporting \(-6\) stops at the hidden adjoint.",
          NET, A_NET, ["nonlinear-least-squares"])
    b.mc(4,
         "One backward sweep on this loss returns",
         ["only the gradient with respect to the output weight",
          "the gradient with respect to every weight and bias",
          "the Hessian of the loss",
          "a new set of weights that minimizes the loss"],
         1,
         r"The scalar loss has one adjoint, and the reverse sweep distributes it to every parameter. Stopping at the output weight leaves the first layer without a gradient. The Hessian would take a second differentiation, such as a Hessian-vector product. The sweep computes a gradient. It does not by itself choose a step or a minimizer.",
         NET, A_NET, ["descent-directions"])
    b.multi(4,
            "For the half-square loss on this two-layer network, which quantities does one reverse sweep produce?",
            ["the partial derivative of the loss with respect to the first weight",
             "the partial derivative of the loss with respect to the output weight",
             "every entry of the Hessian of the loss",
             "the partial derivative of the loss with respect to the first bias"],
            [0, 1, 3],
            r"A reverse sweep on a scalar loss returns the full gradient. Both layer weights and the first bias are coordinates of that gradient."
            "\n"
            r"• The Hessian is a matrix of second derivatives. One reverse sweep does not fill it. A further forward sweep on the gradient would return Hessian-vector products.",
            NET, A_NET, ["incremental-gradient-methods"])
    b.save()


def expl_convex():
    sections = [
        {"heading": "The idea", "figure": BOWL, "figure_alt": A_BOWL,
         "body_md": r"""A convex function bends the way a bowl does, but the definition does not mention derivatives. Take any two points in the domain and any weight between \(0\) and \(1\). The point that sits that fraction of the way from the first point to the second has to be in the domain, so the domain itself is a convex set. The function at that intermediate point is at most the same weighted average of the two function values. Drawn in one variable, the graph lies on or under the chord.

Equality for every chord is the affine case, and affine functions are convex. Strict convexity asks for a strict inequality whenever the points are distinct and the weight is strictly between the endpoints. A norm is convex by the triangle inequality, and it is not strictly convex, because it is linear on each ray from the origin.

The definition is stable under operations that optimization uses. A nonnegative multiple of a convex function is convex. A sum of convex functions is convex. The pointwise maximum of convex functions is convex, corners included. An affine substitution, \(x \mapsto Ax + b\), preserves convexity."""},
        {"heading": "Key equations",
         "body_md": r"""For every \(x, y\) in the domain and every \(t \in [0, 1]\),
\[
f\bigl((1 - t)x + ty\bigr) \le (1 - t)\, f(x) + t\, f(y).
\]
The inequality is strict, for \(t \in (0, 1)\) and \(x \ne y\), when \(f\) is strictly convex. If \(f\) and \(g\) are convex and \(c \ge 0\), then \(cf + g\) is convex, and so is \(x \mapsto f(Ax + b)\). The pointwise maximum of any family of convex functions is convex."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(t) = t^2\) and the chord from \(6\) to \(12\). The sample chord height is 90, the average of 36 and 144. The midpoint of the inputs is \(9\), and \(f(9) = 81\), which is under the chord by \(9\). The same gap is \(\bigl((12 - 6)/2\bigr)^2\). A square opens upward, so every such gap is positive and the function is strictly convex. Collapsing the two endpoints onto one point would make the gap zero, which the definition still allows."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The opposite inequality is concavity. A function can be both, and then it is affine. Strict convexity is not implied by convexity: the absolute value is convex, and the chord from \(-1\) to \(1\) sits strictly above the graph, but the chord from \(1\) to \(3\) lies on the graph. A corner is allowed. What is not allowed is a dent that lets some chord dip below the graph, as \(t^3\) does on the whole line. The pointwise minimum of convex functions need not be convex."""},
        {"heading": "Where this leads",
         "body_md": r"""Differentiable convex functions are exactly the functions whose tangents are global underestimators. Twice differentiable convex functions are exactly the functions whose Hessian is positive semidefinite everywhere on an open convex domain. Those two tests are easier to check than the chord definition, and they are equivalent to it under the extra smoothness. A convex objective is what makes a local minimizer global."""},
    ]
    save_explainer("convex-functions", "Convex functions", sections)


def expl_first():
    sections = [
        {"heading": "The idea", "figure": BOWL, "figure_alt": A_BOWL,
         "body_md": r"""The chord definition of convexity does not mention a derivative. When the function is differentiable there is an equivalent picture: every tangent lies under the graph, not only near the point of tangency but at every point of the domain. The linear model built from the value and the gradient is a global underestimator.

This is stronger than a local linear approximation. A smooth nonconvex function still has a tangent, and that tangent is a good approximation nearby, but somewhere else the graph can cross below it. Convexity forbids that crossing.

The inequality also explains minimizers. If the gradient at a point is the zero vector, the underestimator is the constant equal to the function value, so every other point is at least that high. A stationary point of a differentiable convex function is a global minimizer. Strict convexity upgrades that conclusion to a unique minimizer."""},
        {"heading": "Key equations",
         "body_md": r"""If \(f\) is differentiable on an open convex set, it is convex if and only if every pair of points satisfies
\[
f(y) \ge f(x) + \nabla f(x)^{T} (y - x).
\]
The right-hand side is the first-order Taylor model. The gap \(f(y) - f(x) - \nabla f(x)^{T}(y - x)\) is nonnegative. When the gradient at \(x\) is zero, the inequality says \(f(y) \ge f(x)\) for every \(y\) in the domain."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(t) = t^2\) at the base point \(5\). The value is \(25\) and the derivative is \(10\). At the comparison point \(8\) the step is \(3\), so the tangent value is 55, equal to \(25 + 30\). The function there is \(64\), and the gap above the tangent is \(9\). The same calculation at the base point itself returns the value \(25\), so the gap is zero on the point of tangency. Moving the comparison point to \(0\) gives the model \(25 + 10\cdot(0 - 5) = -25\), and the function value \(0\) is still above that tangent."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The inequality runs the opposite way from the chord inequality. The chord says the function is below the secant. The tangent test says the function is above the tangent. Both describe the same bowl. Dropping the gradient term leaves a comparison of function values, which is not the test. A zero gradient without convexity is only a stationary point: it may be a maximum or a saddle. The test needs the gradient at the base point, so it does not apply to a function that merely has directional derivatives along some rays."""},
        {"heading": "Where this leads",
         "body_md": r"""The second-order test replaces this inequality, for a twice differentiable function, by positive semidefiniteness of the Hessian. The first-order inequality is also the reason a descent method can certify optimality: once the gradient is zero, convexity promotes the stationary point to a global solution. On a convex feasible set the same idea becomes a variational inequality, using the gradient only against feasible steps."""},
    ]
    save_explainer("convexity-first-order", "First-order convexity condition", sections)


def expl_second():
    sections = [
        {"heading": "The idea", "figure": HESS, "figure_alt": A_HESS,
         "body_md": r"""For a function with continuous second partial derivatives, convexity can be read from the Hessian. On an open convex domain the function is convex exactly when that matrix is positive semidefinite at every point, and strictly convex when the matrix is positive definite at every point.

In one variable this is the familiar second-derivative test: the second derivative is nonnegative everywhere. In several variables an eigenvalue can hide off the diagonal, so checking the diagonal entries is not enough. The quadratic form of the Hessian has to be nonnegative in every direction.

A quadratic function has a constant Hessian. Its linear term and its constant term do not appear there, so they do not affect convexity. A least-squares objective \(\lVert Ax - b \rVert^2\) has Hessian \(2A^{T}A\), which is positive semidefinite for every real \(A\). Every linear least-squares problem is a convex quadratic."""},
        {"heading": "Key equations",
         "body_md": r"""On an open convex set, a \(C^2\) function is convex if and only if \(v^{T} H_f(x)\, v \ge 0\) for every point \(x\) and every direction \(v\). It is strictly convex if \(v^{T} H_f(x)\, v > 0\) whenever \(v \ne 0\). For \(f(x) = \tfrac12 x^{T} A x + b^{T} x + c\) with \(A\) symmetric, the Hessian is \(A\), so convexity is positive semidefiniteness of \(A\). The gradient \(Ax + b\) does not enter that test."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(x, y) = 7x^2 + 9y^2\). Differentiating twice gives the constant Hessian with Hessian entries 14 and 18 on the diagonal and zeros off it. Both eigenvalues are positive, so the Hessian is positive definite and \(f\) is strictly convex. Adding a linear function such as \(3x - y\) does not change either second derivative. The new function is still strictly convex, and its minimizer moves, but the second-order test does not need the new linear coefficients."""},
        {"heading": "Common pitfalls",
         "body_md": r"""One positive definite Hessian is not the test. A function can bend up at the origin and bend down far away. The matrix has to be checked on the whole domain. A positive determinant, or a positive trace, is not semidefiniteness: the matrix with diagonal entries \(2\) and \(-2\) has negative determinant and is indefinite, and a matrix with eigenvalues \(3\) and \(-1\) has positive trace and is still indefinite. Positive semidefiniteness allows a zero eigenvalue. The function is then convex and not strictly convex, like a square of one linear form in the plane."""},
        {"heading": "Where this leads",
         "body_md": r"""At an interior local minimizer the same matrix is positive semidefinite, as a necessary condition, and positive definiteness together with a zero gradient is sufficient for a strict local minimizer. For a convex function those local facts become global. Quadratic objectives are minimized by solving one linear system when the Hessian is positive definite, and the second-order test is what justifies that solve."""},
    ]
    save_explainer("convexity-second-order", "Second-order convexity test", sections)


def expl_fd():
    sections = [
        {"heading": "The idea", "figure": CUBIC, "figure_alt": A_CUBIC,
         "body_md": r"""A derivative is a limit of difference quotients. A finite difference stops at one small step and uses the quotient as an approximation. The forward difference looks only to the right. The central difference looks the same distance to the right and to the left and averages the two slopes.

Taylor's theorem with remainder says what that approximation misses. The forward difference of a smooth function equals the derivative plus a term proportional to the step times the second derivative, plus higher powers of the step. The central difference cancels that second-derivative term. Its first error is proportional to the square of the step times the third derivative.

Shrinking the step therefore cuts truncation. It also subtracts two function values that are closer and closer, then divides by a smaller number. Floating-point round-off, divided by the step, grows. A useful step balances the falling truncation against the rising round-off. Past that balance, a smaller step makes the computed slope worse."""},
        {"heading": "Key equations",
         "body_md": r"""With step \(h > 0\),
\[
\delta_+ f(x) = \frac{f(x + h) - f(x)}{h}, \qquad \delta_c f(x) = \frac{f(x + h) - f(x - h)}{2h}.
\]
The forward truncation begins with \((h/2) f''(x)\). The central truncation begins with \((h^2/6) f'''(x)\). Round-off of either quotient is on the order of \(\varepsilon_{\mathrm{mach}}\) times a scale of \(f\), divided by \(h\). Balancing \(h\) against \(\varepsilon_{\mathrm{mach}}/h\) puts the forward step near \(\sqrt{\varepsilon_{\mathrm{mach}}}\). Balancing \(h^2\) against \(\varepsilon_{\mathrm{mach}}/h\) puts the central step near the cube root of unit roundoff."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(t) = t^3\) at \(t = 4\) with step \(0.2\). The exact derivative is \(48\). The forward sample \(f(4.2) = 74.088\) gives the quotient \(50.44\). The left sample \(f(3.8) = 54.872\), and the central value is 48.04, from \((74.088 - 54.872) / 0.4\). The forward error is \(2.44\), most of it the predicted \((h/2) f''(4) = 2.4\). The central error is \(0.04\), matching \((h^2/6)\) times the constant third derivative \(6\). Halving this step would roughly halve the forward error and cut the central error by about four, until round-off takes over."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Dividing a central numerator by \(h\) instead of \(2h\) doubles the slope. Forgetting to divide at all reports a change in value. The forward difference of a quadratic is not exact: the second derivative is a nonzero constant, so a term proportional to the step remains. The central difference of a quadratic is exact. A smaller step is not automatically a better step. When the two function values agree to every stored digit, the quotient is noise."""},
        {"heading": "Where this leads",
         "body_md": r"""Finite differences are the numeric way to get a derivative when the formula is available only as a subroutine. They are also the truncation analysis behind some accelerated gradient updates that mix a step with a previous step. Automatic differentiation later removes the truncation by applying the chain rule to each elementary operation, and the round-off that remains is ordinary floating-point round-off rather than a difference of nearly equal values."""},
    ]
    save_explainer("finite-difference-derivatives", "Finite-difference derivatives", sections)


def expl_graph():
    sections = [
        {"heading": "The idea", "figure": GRAPH, "figure_alt": A_GRAPH,
         "body_md": r"""A long formula is a sequence of elementary steps. A computational graph makes that sequence explicit. Each node is one operation, such as a product, a sum, or a square, and each edge says which earlier value the operation reads. The graph is directed and acyclic: a value is computed from values that already exist.

Evaluating the graph is a forward pass in topological order. Intermediate nodes are not optional bookkeeping. They are the values a later derivative rule will need.

Three ways of differentiating sit on this picture. Symbolic differentiation rewrites the expression, and the rewritten expression can be much larger than the graph. Numeric differentiation ignores the graph and samples the output. Automatic differentiation keeps the graph, evaluates it, and applies the derivative of each elementary node. The chain rule is then arithmetic on numbers, not algebra on a swollen expression."""},
        {"heading": "Key equations",
         "body_md": r"""A node \(v = \varphi(u, w)\) is ready when \(u\) and \(w\) are known. The local pieces used later are the partial derivatives of \(\varphi\). For a product, those pieces are the two factors. For a sum, they are \(1\). For a square, the piece is twice the input. The output of a graph with several nodes is the composition of these maps, and the multivariable chain rule multiplies the local pieces along each path from an input to the output."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(x, y) = (x + y)x + 5\), which is a product of a sum with the first input, then a shift. At the inner point (6, -2) the sum is 4, the product is \(24\), and the output is \(29\). The same arithmetic in a different order, adding \(5\) before the product, would compute \((4 + 5)\cdot 6 = 54\) and would be a different function. The graph fixes the order. Symbolic differentiation of this short example is easy. The same discipline, product then sum then square, is what keeps a long composition from being expanded by hand."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Evaluating a node before its parents is not a rearrangement. It reads a number that does not exist yet. Squaring the wrong parent computes a different formula, even if every operation type is one the graph contains. Counting nodes does not produce a derivative. Throwing away the intermediate values leaves a subroutine, which is enough for a finite difference and not enough for an exact chain-rule sweep. A cyclic graph would not be a straight-line evaluation."""},
        {"heading": "Where this leads",
         "body_md": r"""Forward mode pushes a tangent along the same order as the evaluation. Reverse mode walks the arrows backward and accumulates an adjoint on each node. Both are the chain rule on this graph. The choice between them is about how many inputs and outputs you have, not about a different notion of derivative. Hessian-vector products are a second pass on the same idea."""},
    ]
    save_explainer("computational-graphs", "Computational graphs", sections)


def expl_forward():
    sections = [
        {"heading": "The idea", "figure": RAY, "figure_alt": A_RAY,
         "body_md": r"""Forward-mode automatic differentiation carries a tangent next to every value in a computational graph. You choose a direction \(d\) and seed the inputs with it. Each later node receives the tangents of its parents and applies the derivative of its own operation. The tangent that arrives at the output is the directional derivative of the output in the direction \(d\).

The primal value is computed in the same visit. The local derivative of a product or a square depends on that value, so the tangent does not run ahead of the evaluation. One sweep costs about as much as one evaluation of the function, and it returns one directional derivative of every output at once.

If the output is a single scalar of \(n\) inputs and you want the full gradient, you repeat the sweep with each coordinate direction. That is about \(n\) function evaluations. Forward mode is the cheap choice when there are few directions and many outputs."""},
        {"heading": "Key equations",
         "body_md": r"""Write \(\dot v\) for the tangent of a node \(v\). A sum adds tangents. A product obeys \(\dot{(uv)} = \dot u\, v + u\, \dot v\). A square obeys \(\dot{(s^2)} = 2s\, \dot s\). At a differentiable scalar output,
\[
\dot f = \nabla f(x)^{T} d,
\]
where \(d\) is the input seed. The map \(d \mapsto \dot f\) is linear. Seeding the first coordinate vector returns the first partial derivative."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(x, y) = x^2 + xy + 5\) at \((6, -2)\), and seed the direction \((1, 1)\). The partial derivative in \(x\) is \(2x + y = 10\), and the partial derivative in \(y\) is \(x = 6\). The tangent total is 16, their sum. On the graph, the product \(xy\) has tangent \(\dot x\, y + x\, \dot y = 1\cdot(-2) + 6\cdot 1 = 4\), and the square of \(x\) has tangent \(2\cdot 6\cdot 1 = 12\). Adding those tangents and the zero tangent of the constant again gives \(16\). A seed with a zero in the second coordinate would have returned only \(10\)."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The product rule is the usual place to drop a term. Using \(\dot u\, v\) and forgetting \(u\, \dot v\) is a wrong local linearization, and every downstream tangent inherits it. A variable that is used twice must contribute a tangent on every edge. Adding a constant has tangent zero, but adding an input does not. The output tangent is not the primal output. For a wide scalar function, repeating forward sweeps to fill the gradient does much more work than one reverse sweep."""},
        {"heading": "Where this leads",
         "body_md": r"""The same tangent arithmetic, applied not to \(f\) but to its gradient, returns the Hessian times the seed. That forward-over-reverse product is the second-derivative tool used by large Newton and conjugate-gradient steps. Forward mode on the original function remains the right tool for a single directional derivative and for a map with many outputs."""},
    ]
    save_explainer("ad-forward-mode", "Forward-mode automatic differentiation", sections)


def expl_reverse():
    sections = [
        {"heading": "The idea", "figure": GRAPH, "figure_alt": A_GRAPH,
         "body_md": r"""Reverse-mode automatic differentiation computes the gradient of a scalar by walking a computational graph backward. The forward pass is run first, and every node value is stored. The output then receives adjoint \(1\), meaning the derivative of the output with respect to itself. Each node pushes its adjoint back to its parents, multiplied by the local partial derivative.

If a parent is used by several nodes, the contributions add. A variable that appears twice in the formula gets an adjoint from every use. When the sweep reaches the inputs, their adjoints are the partial derivatives of the output. One sweep produces all of them.

The arithmetic is a small constant times one function evaluation. The extra cost is memory for the forward trace, or extra time if those values are recomputed. For one scalar that depends on many inputs, this is much cheaper than one forward sweep per input."""},
        {"heading": "Key equations",
         "body_md": r"""The adjoint of a node \(v\) is \(\bar v = \partial f / \partial v\). The output is seeded with \(\bar f = 1\). A sum sends its adjoint unchanged to each summand. A product \(p = uv\) sends \(\bar p\, v\) to \(u\) and \(\bar p\, u\) to \(v\). A square \(q = s^2\) sends \(2s\, \bar q\) to \(s\). If \(x\) is used in two places, the two contributions to \(\bar x\) are added. At the end, \(\bar x_i = \partial f / \partial x_i\)."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(x, y) = x^2 + xy + 5\) at \((8, -2)\). The forward values are \(x^2 = 64\) and \(xy = -16\). Seed the output with adjoint \(1\). The square sends \(2\cdot 8\cdot 1 = 16\) toward \(x\). The product sends \(y\cdot 1 = -2\) toward \(x\) and \(x\cdot 1 = 8\) toward \(y\). Adding the two contributions to \(x\) gives the adjoint pair 14 and 8: \(\partial f/\partial x = 16 - 2 = 14\), and \(\partial f/\partial y = 8\). Dropping the product's contribution to \(x\) would have left \(16\), which is only the square."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The sweep cannot start until the forward values exist, because the local factors \(2s\), \(u\), and \(v\) are primal numbers. Forgetting one path into a variable that is used twice drops part of the partial derivative. Seeding the output with the output value, instead of with \(1\), scales the whole gradient by that value. Reverse mode is not automatically cheaper than forward mode for a function of one input. The two modes do about the same work in that case. Reverse mode wins when the input is wide and the output is a scalar."""},
        {"heading": "Where this leads",
         "body_md": r"""Training a model is this sweep on a scalar loss: the weights are the wide input, and the loss is the scalar output. Applying forward mode to the reverse-mode gradient, with a direction \(d\), returns the Hessian times \(d\) without forming the Hessian. That product is the next tool when a second-order method needs curvature and the parameter vector is long."""},
    ]
    save_explainer("ad-reverse-mode", "Reverse-mode automatic differentiation", sections)


def expl_hvp():
    sections = [
        {"heading": "The idea", "figure": HESS, "figure_alt": A_HESS,
         "body_md": r"""The Hessian is the derivative of the gradient. Multiplying it by a direction \(d\) is therefore the directional derivative of the gradient map. Automatic differentiation can take that derivative without writing the matrix down.

The usual arrangement is forward-over-reverse. A reverse sweep builds the gradient, with its own computational graph. A forward sweep then pushes the seed \(d\) through that graph. The tangent of the gradient is \(H_f(x)\, d\). Reverse-over-forward does the same job when the direction is held constant: forward mode builds the scalar \(\nabla f(x)^{T} d\), and a reverse sweep differentiates that scalar with respect to \(x\).

Either product costs about as much as one gradient. The full matrix is \(n\) such products, one per column. A method that only needs curvature in particular directions never forms those columns."""},
        {"heading": "Key equations",
         "body_md": r"""If \(g(x) = \nabla f(x)\), then \(g'(x)\, d = H_f(x)\, d\). Forward-over-reverse evaluates that directional derivative. With \(d\) independent of \(x\),
\[
\nabla_x \bigl(\nabla f(x)^{T} d\bigr) = H_f(x)\, d
\]
as well, which is reverse-over-forward. The quadratic form \(d^{T} H_f(x)\, d\) is the second directional derivative of \(f\), obtained from one product and one inner product. The \(i\)th column of the Hessian is the product with the \(i\)th coordinate vector."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(x, y) = 3x^2 + xy\). The Hessian is constant, with first row \((6, 1)\) and second row \((1, 0)\). For the direction \((2, -1)\) the product entries 11 and 2 are \(6\cdot 2 + 1\cdot(-1) = 11\) and \(1\cdot 2 + 0\cdot(-1) = 2\). The quadratic form on this direction is \(2\cdot 11 + (-1)\cdot 2 = 20\). A forward difference of the gradient in this direction, divided by a small step, approaches \((11, 2)\) and does not produce the other column. One direction yields one vector."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The product \(H d\) is not the gradient and not the first directional derivative \(\nabla f^{T} d\). Those are first-order. Reading the first column as the diagonal of the matrix swaps the off-diagonal entry with a diagonal entry that the direction did not select. One product does not fill the matrix. Forming every entry by finite differences costs many more function evaluations than \(n\) gradient-like products, and it adds truncation. If the direction depends on \(x\) and you differentiate it as well, reverse-over-forward picks up extra terms that are not \(H d\)."""},
        {"heading": "Where this leads",
         "body_md": r"""Newton's method solves \(H_f(x)\, d = -\nabla f(x)\). An iterative solver for that system needs only products with \(H_f(x)\). Conjugate gradients are built for exactly that interface. The second-order optimality test, by contrast, wants to know whether the Hessian is positive semidefinite. Products can probe that question along chosen directions, while the full matrix remains the direct certificate."""},
    ]
    save_explainer("hessian-vector-products-ad", "Hessian-vector products with automatic differentiation", sections)


def expl_backprop():
    sections = [
        {"heading": "The idea", "figure": NET, "figure_alt": A_NET,
         "body_md": r"""A small neural network is a computational graph with a scalar loss at the end and the weights among the inputs. Backpropagation is reverse-mode automatic differentiation on that graph. One backward sweep returns the partial derivative of the loss with respect to every weight and bias.

Consider a two-layer map with a positive-part activation in the hidden layer. The first affine step produces a pre-activation. The activation leaves it unchanged when it is positive and replaces it by zero when it is negative. A second affine step produces the prediction. The loss used here is half the square of the prediction minus the target, so the adjoint of the prediction is the residual.

The positive-part function has local derivative \(1\) on a positive pre-activation and local derivative \(0\) on a negative one. A zero local derivative blocks the adjoint before it reaches the first-layer weights. The output bias is upstream of that gate and still receives a gradient."""},
        {"heading": "Key equations",
         "body_md": r"""Write \(z = w_1 t + b_1\), \(h = \max(z, 0)\), and \(\hat y = w_2 h + b_2\). With \(L = \tfrac12 (\hat y - y)^2\),
\[
\bar{\hat y} = \hat y - y, \quad \frac{\partial L}{\partial w_2} = \bar{\hat y}\, h, \quad \bar h = \bar{\hat y}\, w_2.
\]
If \(z > 0\), then \(\partial L/\partial w_1 = \bar h\, t\) and \(\partial L/\partial b_1 = \bar h\). If \(z < 0\), both of those first-layer derivatives are zero, while \(\partial L/\partial b_2 = \bar{\hat y}\) remains."""},
        {"heading": "Worked example",
         "body_md": r"""Take input \(8\), first weight \(1\), first bias \(-1\), output weight \(3\), output bias \(-5\), and target \(4\). The pre-activation is \(7\), so the hidden value is \(7\) and the prediction is \(3\cdot 7 - 5 = 16\). The residual is \(12\). The output weight receives \(12\cdot 7 = 84\). The hidden adjoint is \(12\cdot 3 = 36\). The activation derivative is \(1\), and the first-layer gradient is 288, from \(36\cdot 8\). The first bias receives \(36\). Had the first bias been \(-10\), the pre-activation would have been negative, the hidden value would have been zero, and both layer weights would have received no gradient from this example."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Using the square without the one half doubles every adjoint, because the residual is then multiplied by two. Forgetting a second use of a weight drops part of its gradient. Treating a positive pre-activation as a blocked unit sets the wrong local derivative: the derivative is \(1\) on that side and \(0\) on the other side. The output weight's factor is the stored hidden value, which is a different zero from the activation derivative. One sweep does not produce the Hessian and does not update the weights. It only fills the gradient."""},
        {"heading": "Where this leads",
         "body_md": r"""The gradient this sweep returns is the one a descent method consumes. A sum of losses over many examples is the same sweep on each example, or one sweep on the summed graph. Nonlinear least squares is the same square loss with a residual that need not come from a network. Hessian-vector products, built by differentiating this gradient in one direction, are what a second-order step would ask for next."""},
    ]
    save_explainer("backprop-neural-network", "Backpropagation for a small neural network", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    bank_convex()
    bank_first()
    bank_second()
    bank_fd()
    bank_graph()
    bank_forward()
    bank_reverse()
    bank_hvp()
    bank_backprop()
    expl_convex()
    expl_first()
    expl_second()
    expl_fd()
    expl_graph()
    expl_forward()
    expl_reverse()
    expl_hvp()
    expl_backprop()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    banned = ("graz", "boyd", "nocedal", "vandenberghe", "hefferon", "wikibook",
              "textbook", "university", "professor", "lecture", "syllabus", "cambridge", "springer")
    ids = [
        "convex-functions", "convexity-first-order", "convexity-second-order",
        "finite-difference-derivatives", "computational-graphs", "ad-forward-mode",
        "ad-reverse-mode", "hessian-vector-products-ad", "backprop-neural-network",
    ]
    private = {
        "convex-functions": "sample chord height is 90",
        "convexity-first-order": "tangent value is 55",
        "convexity-second-order": "Hessian entries 14 and 18",
        "finite-difference-derivatives": "central value is 48.04",
        "computational-graphs": "inner point (6, -2)",
        "ad-forward-mode": "tangent total is 16",
        "ad-reverse-mode": "adjoint pair 14 and 8",
        "hessian-vector-products-ad": "product entries 11 and 2",
        "backprop-neural-network": "first-layer gradient is 288",
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
