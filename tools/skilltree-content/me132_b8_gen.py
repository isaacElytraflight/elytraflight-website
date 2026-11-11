#!/usr/bin/env python3
"""Generate ME 132 batch B8 banks and explainers.

Closed-form answers live here. skilltree/verify_me132_b8.py recomputes the
numeric ones from the scalar Riccati, the covariance map, and the one-step
quadratic. Do not import this file from the verifier.
"""
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import (
    block_diagram, ellipse_axes, filled_ellipse_fig, matrix_fig, parallel_sum,
    plane_vectors, splane, step_response,
)
from banklib import BANK, EXP, Bank, g, save_explainer, words


def show(x):
    return f"{g(x):.6g}"


def loop(blocks, title, fb="1", sign="-", inp="r", out="y"):
    return block_diagram(blocks, title, feedback=fb, input_label=inp, output_label=out, feedback_sign=sign)


def steady_pred(q, r):
    """Positive predicted variance for a=1, c=1. P^2 - q P - q r = 0."""
    return (q + math.sqrt(q * q + 4.0 * q * r)) / 2.0


def lqr_gain(a, b, q, r):
    """Stabilizing scalar gain and the positive Riccati solution."""
    aa = (b * b) / r
    bb = -2.0 * a
    cc = -q
    disc = bb * bb - 4.0 * aa * cc
    p = (-bb + math.sqrt(disc)) / (2.0 * aa)
    return (b / r) * p, p


def kgain(p, c, r):
    return (p * c) / (c * c * p + r)


def joseph(p, ell, c, r):
    return (1.0 - ell * c) ** 2 * p + (ell ** 2) * r


def one_step(x, rho, bound):
    u = -x / (1.0 + rho)
    return max(-bound, min(bound, u)), u


def put_explainer(sid, title, sections):
    for section in sections:
        svg = section.get("figure_svg")
        if svg and "figure" not in section:
            section["figure"] = svg
    save_explainer(sid, title, sections)
    return words(sections)


# ---------------------------------------------------------------------------
# gaussian random vectors
# ---------------------------------------------------------------------------

def bank_gaussian():
    b = Bank("gaussian-random-vectors")
    ell = ellipse_axes("a level curve of a covariance, longer on the first axis")
    ell_alt = "An ellipse centered on the axes, stretched farther along the first coordinate."
    disk = filled_ellipse_fig("a shaded elliptical cloud of a random vector")
    disk_alt = "A shaded ellipse centered at the origin of two axes."
    mat = matrix_fig([["3", "0"], ["0", "5"]], "a diagonal covariance")
    mat_alt = "A 2 by 2 matrix with 3 and 5 on the diagonal and zeros off it."
    img = plane_vectors([(3, 0, "e1"), (0, 2, "e2")], "two axis directions before a linear map")
    img_alt = "Two arrows from the origin, one along each axis."
    cov = matrix_fig([["4", "1"], ["1", "9"]], "a covariance with a nonzero cross term")
    cov_alt = "A 2 by 2 symmetric matrix with 4 and 9 on the diagonal."

    var_scale = 3.0 ** 2 * 4.0
    var_lin = 1.0 ** 2 * 2.0 + 2.0 ** 2 * 5.0
    # A = [[0, 2], [1, 0]], P = diag(3, 5). (APA^T)_11 = 20.
    apa = 2.0 * 5.0 * 2.0
    pred = 0.5 ** 2 * 1.0 + 0.1

    b.mc(1,
         r"The covariance of a random vector \(x\) with mean \(\mu\) is",
         [r"\(\mathbb{E}[(x-\mu)(x-\mu)^T]\), which is symmetric",
          r"\(\mathbb{E}[x]\), the mean itself",
          r"\(\mathbb{E}[x]\,\mathbb{E}[x]^T\), the outer product of the mean",
          r"the matrix \(A\) in a later linear map, before any data"], 0,
         r"Covariance is the expected outer product of the centered vector, so it is symmetric and its diagonal entries are variances. The mean is a different summary. The outer product of the mean is not centered, and a matrix that will later multiply \(x\) is not the covariance of \(x\).",
         ell, ell_alt)
    b.num(1,
          r"A scalar Gaussian has variance 4. An instrument reports \(3\) times that variable. The variance of the report is",
          var_scale, "m2",
          r"A scale factor \(c\) multiplies the variance by \(c^2\). Here \(3^2 \times 4 = " + show(var_scale) + r"\). Multiplying the variance by \(3\) instead of \(9\) leaves the square off. Adding \(3\) to the variance treats the scale as a shift. Reporting \(4\) ignores the instrument.",
          disk, disk_alt)
    b.num(1,
          r"Two components are independent, with variances \(2\) and \(5\). The variance of \(x_1 + 2 x_2\) is",
          var_lin, "m2",
          r"Independence kills the cross term, so the variance is \(1^2 \times 2 + 2^2 \times 5 = " + show(var_lin) + r"\). Using the coefficients without squares gives \(2 + 2 \times 5 = 12\). Adding the variances with no coefficients gives \(7\). The product \(2 \times 5 = 10\) is neither term.",
          mat, mat_alt)

    b.sym(2,
          r"A scalar Gaussian \(z\) has variance \(v\). Write the variance of \(c z\) in the names \(c\) and \(v\).",
          "c*c*v", {"c": (0.4, 3.0), "v": (0.4, 4.0)},
          r"The scale comes out twice because covariance is an outer product: \(\mathrm{Var}(c z) = c^2 v\). The form \(c v\) forgets one factor. The form \(c + v\) treats the scale as a shift, and a shift does not change a variance.",
          alternates=["c**2*v", "v*c*c"],
          fig=ell, alt=ell_alt)
    b.num(2,
          r"Let \(P = \mathrm{diag}(3, 5)\) and \(A = \begin{bmatrix} 0 & 2 \\ 1 & 0 \end{bmatrix}\). The top-left entry of \(A P A^T\) is",
          apa, "m2",
          r"\(A P = \begin{bmatrix} 0 & 10 \\ 3 & 0 \end{bmatrix}\) and \(A^T = \begin{bmatrix} 0 & 1 \\ 2 & 0 \end{bmatrix}\), so the top-left entry is \(10 \times 2 = " + show(apa) + r"\). Stopping at \(A P\) and reading its corner gives \(0\). Using \(A P\) without the transpose and taking the other diagonal entry of \(A P A^T\) gives \(3\), which is the image of the first variance, not this corner.",
          img, img_alt)
    b.order(2,
            r"Put these steps in the order you would use them to get the covariance of \(A x + d\) for a fixed matrix \(A\) and a fixed vector \(d\).",
            ["Drop the added vector d. A constant shift does not change the covariance.",
             "Center x by its mean and form the covariance P.",
             "Multiply on the left by A and on the right by A transpose.",
             "Read the diagonal of that product as the variances of the components."],
            r"A shift changes the mean and not \(P\), so it leaves first. \(P\) is the object the linear map acts on. The image covariance is \(A P A^T\), and only then do the diagonal entries become the new variances. Multiplying by \(A\) before you have \(P\) has nothing to transform.",
            mat, mat_alt)

    b.find_error(3,
                 r"\(x\) is a random vector with covariance \(P\), and \(A\) is a fixed square matrix. One step is wrong.",
                 [r"\(P\) is symmetric, because it is an expected outer product of a centered vector.",
                  r"Each diagonal entry of \(P\) is the variance of one component.",
                  r"The covariance of \(A x\) is \(A P\). The transpose factor cancels because \(A\) is square.",
                  r"Adding a constant vector to \(x\) leaves \(P\) unchanged."],
                 2,
                 r"Square or not, the covariance of \(A x\) is \(A P A^T\). The first two steps are the definition, and a constant shift really does drop out. The third step drops the transpose, which is exactly the factor that puts the second \(A\) on the other side of the outer product.",
                 reasons=["The image covariance is A P A transpose, and a square A does not remove the transpose.",
                          "A square matrix always satisfies A P = P.",
                          "A constant shift replaces P by the outer product of the shift."],
                 correct_reason=0,
                 fig=cov, alt=cov_alt)
    b.mc(3,
         r"For a Gaussian vector, a zero cross-covariance between two components means",
         ["the components have equal variance",
          "the components are independent",
          "the mean of each component is zero",
          "every linear image of the vector is constant"], 1,
         r"Jointly Gaussian and uncorrelated implies independent. Equal variance is a statement about the diagonal. The mean is a separate parameter. A nondegenerate Gaussian still has a spread after a linear map that keeps both directions.",
         disk, disk_alt)
    b.multi(3,
            r"Which statements hold for a covariance \(P\) and a fixed matrix \(A\)?",
            [r"The covariance of \(A x\) is \(A P A^T\).",
             r"Adding a constant vector to \(x\) changes \(P\).",
             "If the vector is Gaussian, uncorrelated components are independent.",
             r"A diagonal entry of \(P\) may be negative and still be a variance."],
            [0, 2],
            r"The linear image sends \(P\) to \(A P A^T\). A constant changes the mean only. For a Gaussian, a zero cross term is independence, not merely a lack of linear correlation. A variance is an expected square, so a diagonal entry cannot be negative.",
            ell, ell_alt)

    b.num(4,
          r"A predicted covariance is about to be formed as \(A P A^T + Q\) with \(A = 0.5\), \(P = 1\), and \(Q = 0.1\), all scalars. The predicted variance is",
          pred, "m2",
          r"\(0.5^2 \times 1 + 0.1 = " + show(pred) + r"\). Dropping the square on \(0.5\) gives \(0.6\). Forgetting \(Q\) leaves \(0.25\). Adding \(A\) itself to \(P\) gives \(1.5\), which is not a covariance update.",
          ell, ell_alt, ["kalman"])
    b.mc(4,
         r"A later recursion predicts a state by multiplying the estimate by \(A\) and the covariance by the same pattern. The covariance piece uses \(A P A^T\) because",
         [r"\(A\) is always symmetric, so \(A P\) is enough",
          r"the mean and the covariance are the same matrix",
          r"the covariance of a linear image is the congruence \(A P A^T\)",
          r"adding process noise replaces \(P\) by \(A\)"], 2,
         r"That identity is the whole content of the linear-image rule, and the predict step is where a filter spends it. Symmetry of \(A\) is not assumed. The mean is a vector. Process noise is added after the congruence, and it does not replace the map.",
         img, img_alt, ["kalman"])
    b.mc(4,
         r"An affine map \(x \mapsto A x + d\) of a Gaussian vector is",
         [r"no longer Gaussian, because a shift breaks the bell shape",
          r"Gaussian only when \(A\) is diagonal",
          r"Gaussian in the mean and uniform in the covariance",
          r"still Gaussian, with mean \(A\mu + d\) and covariance \(A P A^T\)"], 3,
         r"Affine images preserve the Gaussian family. The shift lands in the mean. The matrix lands in the covariance as \(A P A^T\). Diagonal \(A\) is a special case, not the condition, and the covariance is not replaced by a uniform spread.",
         disk, disk_alt, ["kalman"])
    b.save()


# ---------------------------------------------------------------------------
# kalman
# ---------------------------------------------------------------------------

def bank_kalman():
    b = Bank("kalman")
    model = loop(["model"], "a model copy with a correction gain", fb="L", inp="u", out="xhat")
    model_alt = "A model block with a gain L returned and subtracted."
    mat = matrix_fig([["A", "Q"], ["C", "R"]], "the four matrices of a linear filter")
    mat_alt = "A 2 by 2 arrangement of the labels A, Q, C, and R."
    ell = ellipse_axes("a covariance ellipse before a measurement update", rx=78, ry=40)
    ell_alt = "An ellipse centered on the axes, longer along the first coordinate."
    poles = splane([(-1, 0)], [], "one mark on the negative real axis")
    poles_alt = "A single cross on the negative real axis."

    pred = 0.5 ** 2 * 4.0 + 1.0
    gain = kgain(2.0, 1.0, 2.0)
    post = (1.0 - gain * 1.0) * 2.0
    steady = steady_pred(2.0, 4.0)

    b.mc(1,
         r"For \(x_{k+1} = A x_k + w_k\) and \(y_k = C x_k + v_k\), the predict step",
         [r"multiplies the estimate by \(A\) and replaces the covariance by \(A P A^T + Q\), without using \(y_k\)",
          r"subtracts \(y_k\) from the estimate before \(A\) is applied",
          r"replaces the covariance by \(R\) and leaves the estimate fixed",
          r"sets the gain to \(1\) and skips the covariance"], 0,
         r"Predict uses the state model only. The measurement enters in the update, through the innovation. Replacing the covariance by \(R\) throws away both \(A\) and \(Q\). A gain of \(1\) is not a predict step.",
         model, model_alt)
    b.num(1,
          r"A scalar predict uses \(a = 0.5\), a previous variance \(4\), and process variance \(1\). The predicted variance is",
          pred, "m2",
          r"\(a^2 P + Q = 0.25 \times 4 + 1 = " + show(pred) + r"\). Using \(a\) instead of \(a^2\) gives \(3\). Forgetting \(Q\) leaves \(1\). Adding \(a\) to \(Q\) gives \(1.5\).",
          ell, ell_alt)
    b.num(1,
          r"The predicted variance is \(2\), \(c = 1\), and the measurement variance is \(2\). The filter gain is",
          gain, "1",
          r"\(L = P c / (c^2 P + R) = 2 / (2 + 2) = " + show(gain) + r"\). Using \(P / R = 1\) drops the predicted variance from the denominator. Using \(R / P = 1\) inverts the fraction. Subtracting \(R\) from \(P\) gives \(0\), which is not a gain.",
          mat, mat_alt)

    b.sym(2,
          r"A scalar predict maps a variance \(p\) through a coefficient \(a\) and then adds a process variance \(q\). Write the predicted variance in the names \(a\), \(p\), and \(q\).",
          "a*a*p+q", {"a": (0.2, 1.5), "p": (0.4, 4.0), "q": (0.2, 3.0)},
          r"The state scale hits the variance twice, and the process noise is independent of the previous error, so the variances add: \(a^2 p + q\). The form \(a p + q\) drops a factor of \(a\). The form \(a^2 p\) forgets the process noise. Adding \(a\) itself is not a variance.",
          alternates=["a**2*p+q", "q+p*a*a"],
          fig=ell, alt=ell_alt)
    b.num(2,
          r"Continue the scalar update: predicted variance \(2\), gain \(0.5\), and \(c = 1\). The updated variance, using \((1 - L c)\) times the predicted variance, is",
          post, "m2",
          r"\((1 - 0.5 \times 1) \times 2 = " + show(post) + r"\). This simplified product is the one that matches the longer Joseph form when \(L\) is the filter gain. Leaving the variance at \(2\) skips the update. Multiplying by the gain alone gives \(1\), which happens to match here but is the gain, not a general rule. Adding \(R = 2\) to the result gives \(3\).",
          model, model_alt)
    b.order(2,
            r"Put the scalar filter steps in the order they are used when a new measurement arrives.",
            ["Propagate the estimate through the state coefficient a.",
             "Replace the variance by a squared times the old variance, plus the process variance.",
             "Form the gain from the predicted variance, c, and the measurement variance.",
             "Add the gain times the innovation to the predicted estimate.",
             "Multiply the predicted variance by one minus the gain times c."],
            r"The measurement is not available to the predict, so the estimate and the variance move through \(a\) first and the process noise joins the variance there. The gain needs that predicted variance. Only then does the innovation correct the estimate, and the same gain shrinks the variance. Updating before the predict uses a measurement against the wrong prediction.",
            model, model_alt)

    b.find_error(3,
                 r"A scalar filter has just produced a predicted estimate and a predicted variance. One step of the update is wrong.",
                 ["The gain is the predicted variance times c, divided by c squared times that variance plus R.",
                  "The innovation is the measurement minus c times the predicted estimate.",
                  "The estimate is corrected by the gain times the raw measurement, with no predicted output removed.",
                  "With that gain, the updated variance is one minus L c times the predicted variance."],
                 2,
                 r"The correction multiplies the innovation, not the raw measurement. The gain formula, the innovation, and the simplified variance update are the matching trio. Using \(y\) alone would credit the filter for a measurement it had already expected.",
                 reasons=["The correction has to remove the predicted output. The raw measurement is not the innovation.",
                          "The predict step is where the measurement is subtracted.",
                          "The variance update adds R a second time after the gain is applied."],
                 correct_reason=0,
                 fig=mat, alt=mat_alt)
    b.mc(3,
         r"In the scalar gain \(L = P/(P+R)\) with \(c = 1\), sending the measurement variance \(R\) to a very large value",
         [r"sends the gain to \(1\), so the estimate copies the measurement",
          r"sends the gain to \(0\), so the update barely moves the estimate",
          r"leaves the gain at \(1/2\) for every \(P\)",
          r"makes the predicted variance negative"], 1,
         r"A huge \(R\) dominates the denominator, so \(L\) vanishes and the filter trusts the prediction. Copying the measurement is the opposite limit, \(R \to 0\). The gain is \(1/2\) only when \(R = P\). The predicted variance was already fixed before this gain was formed, and it stays nonnegative.",
         ell, ell_alt)
    b.multi(3,
            r"Which statements hold for the recursion \(x_{k+1} = A x_k + w_k\), \(y_k = C x_k + v_k\)?",
            ["The predict step can be computed before the new measurement arrives.",
             r"Adding \(Q\) during the update, and not during the predict, is the same recursion.",
             "A larger measurement variance, at the same predicted covariance, produces a smaller gain.",
             "The predict step subtracts the measurement from the estimate."],
            [0, 2],
            r"Predict needs \(A\), \(Q\), and the previous posterior. It does not need \(y_k\). Process noise enters with the state propagation. The gain formula has \(R\) in the denominator, so a larger \(R\) shrinks \(L\). Subtracting the measurement is the update, and only after a predicted output has been removed.",
            model, model_alt)

    b.num(4,
          r"A scalar steady filter has \(a = 1\), \(c = 1\), process variance \(2\), and measurement variance \(4\). The steady predicted variance is",
          steady, "m2",
          r"At steady state \(L P = q\) and \(L = P/(P+R)\), so \(P^2 - q P - q R = 0\). The positive root is \((2 + \sqrt{4 + 32})/2 = " + show(steady) + r"\). The measurement variance \(4\) is \(R\), not this predicted variance. The process variance \(2\) is what \(L P\) equals, not \(P\). Half of \(R\) is \(2\), which is the check \(L P = q\) once \(L = 1/2\), and it is not \(P\).",
          poles, poles_alt, ["kalman-optimal-observer"])
    b.mc(4,
         r"The same update can be derived later by fitting linear least-squares blocks one at a time. In this skill, that derivation",
         ["is already the proof that the gain has minimum variance",
          r"replaces \(A\) by an identity, so the predict step disappears",
          "is not required. The recursion and the gain formula stand without it",
          r"is what fixes the process variance \(Q\) from a single sample"], 2,
         r"This skill stops at the recursion: predict, gain, update, covariance. A least-squares derivation of the same algebra is a later reading, and so is the claim that the gain minimizes the error variance. Neither one sets \(Q\) from one sample, and neither one deletes the predict step.",
         mat, mat_alt, ["kalman-recursive-least-squares"])
    b.mc(4,
         r"A known command \(B u_k\) is added inside the predict. It changes",
         [r"the predicted covariance, by the outer product \(B u_k u_k^T B^T\)",
          r"the measurement variance \(R\)",
          r"both the estimate and the covariance",
          "the predicted estimate, and not the predicted covariance"], 3,
         r"A known input is a constant shift of the state prediction, and a shift does not change a covariance. The covariance predict stays \(A P A^T + Q\). The command is not noise, so it does not join \(R\) or \(Q\).",
         model, model_alt, ["kalman-optimal-observer"])
    b.save()


# ---------------------------------------------------------------------------
# kalman as optimal observer
# ---------------------------------------------------------------------------

def bank_optimal():
    b = Bank("kalman-optimal-observer")
    model = loop(["model"], "observer correction from a noise model", fb="L", inp="u", out="xhat")
    model_alt = "A model block with a gain L returned and subtracted."
    ell = filled_ellipse_fig("an error cloud before the best linear correction")
    ell_alt = "A shaded ellipse centered at the origin."
    mat = matrix_fig([["Q", "R"]], "process and measurement intensities")
    mat_alt = "A row of two labels, Q and R."
    poles = splane([(-2, 0), (-9, 0)], [], "two real marks, one farther left")
    poles_alt = "Two crosses on the negative real axis, one farther from the origin."

    p1, r1, c1 = 8.0, 2.0, 1.0
    l1 = kgain(p1, c1, r1)
    post1 = (1.0 - l1 * c1) * p1
    p2, r2, c2 = 5.0, 5.0, 1.0
    l_opt = kgain(p2, c2, r2)
    post_opt = joseph(p2, l_opt, c2, r2)
    post_hand = joseph(p2, 0.2, c2, r2)
    gap = post_hand - post_opt
    steady_p = steady_pred(4.0, 3.0)
    steady_l = kgain(steady_p, 1.0, 3.0)
    steady_post = (1.0 - steady_l) * steady_p

    b.mc(1,
         r"Among corrections of the form \(\hat{x} + L(y - C\hat{x})\), the filter gain is the one that",
         ["minimizes the variance of the updated state error",
          r"places the eigenvalues of \(A - L C\) at a polynomial you wrote down first",
          r"makes the updated covariance equal to \(R\)",
          r"minimizes the process variance \(Q\)"], 0,
         r"This skill's claim is the minimum-variance one: the gain from \(P\) and \(R\) is the linear correction with the smallest updated error variance. Pole placement is a different design and can be a worse variance. The updated covariance is not \(R\), and \(Q\) is a model of the noise, not a quantity the gain minimizes.",
         model, model_alt)
    b.num(1,
          r"A scalar predicted variance is \(8\) and the measurement variance is \(2\), with \(c = 1\). The minimum updated variance is",
          post1, "m2",
          r"The minimizing gain is \(8/(8+2) = " + show(l1) + r"\), and the updated variance is \((1 - L) \times 8 = " + show(post1) + r"\). Reporting the gain \(0.8\) answers a different question. Leaving the variance at \(8\) skips the update. Using \(R = 2\) as the updated variance forgets the prior.",
          ell, ell_alt)
    b.num(1,
          r"The same numbers, predicted variance \(8\) and measurement variance \(2\), make the innovation variance \(c^2 P + R\) equal to",
          p1 + r1, "m2",
          r"With \(c = 1\) the innovation variance is \(P + R = " + show(p1 + r1) + r"\). That sum is the denominator of the gain, not the gain and not the posterior. The posterior is \(1.6\). The ratio \(P/R = 4\) is neither.",
          mat, mat_alt)

    b.sym(2,
          r"A scalar predicted variance is \(p\), the output coefficient is \(c\), and the measurement variance is \(r\). Write the gain that minimizes the updated variance, in the names \(p\), \(c\), and \(r\).",
          "p*c/(c*c*p+r)", {"p": (0.4, 4.0), "c": (0.4, 2.5), "r": (0.4, 4.0)},
          r"Differentiate \((1 - L c)^2 p + L^2 r\) and set the derivative to zero. The critical point is \(L = p c / (c^2 p + r)\). The form \(p / r\) drops both \(c\) and the prior in the denominator. The form \(c / r\) drops \(p\). The numerator is the prior times \(c\), not \(c\) alone.",
          alternates=["(p*c)/(c**2*p+r)", "c*p/(p*c*c+r)"],
          fig=mat, alt=mat_alt)
    b.num(2,
          r"Predicted variance \(5\), measurement variance \(5\), \(c = 1\). A hand-picked gain \(0.2\) is compared with the minimizing gain, using \((1-Lc)^2 P + L^2 R\) for both. How much larger is the hand-picked variance?",
          gap, "m2",
          r"The minimizing gain is \(5/(5+5) = " + show(l_opt) + r"\), with variance " + show(post_opt) + r". The hand-picked gain has variance \(0.8^2 \times 5 + 0.2^2 \times 5 = " + show(post_hand) + r"\). The difference is " + show(gap) + r". The simplified product \((1-Lc)P\) is the variance only for the minimizing gain, so using it on \(L = 0.2\) understates that variance. Reporting either variance alone misses the comparison.",
          ell, ell_alt)
    b.order(2,
            r"Put these steps in the order of a scalar minimum-variance calculation.",
            ["Write the updated error as one minus L c times the predicted error, plus L times the measurement noise.",
             "Write the updated variance, including the term L squared times R.",
             "Differentiate that variance with respect to L and set the derivative to zero.",
             "Solve the resulting equation for L.",
             "Substitute that L back into the variance."],
            r"The error expression comes first, because the variance is its second moment. The derivative is how you locate the minimum, and it has to be taken before you can solve for \(L\). Substituting back is the last step: it reports the minimum value, and it is not how you find \(L\).",
            model, model_alt)

    b.find_error(3,
                 r"Someone is comparing a noise-chosen gain with a pole-placed gain. One step is wrong.",
                 ["The filter gain minimizes the updated error variance among linear corrections.",
                  "A different gain can move the error poles and still produce a larger variance.",
                  "Every stable observer gain has the same error variance, because stability is the only requirement.",
                  "The steady filter gain is the observer gain you would use if you wanted the minimum-variance correction."],
                 2,
                 r"Stability says the error decays. It does not say how large the error is while the noise is acting. The variance still depends on the gain, which is why a pole-placed \(L\) and the filter gain are different designs. The other three steps are the comparison this skill is for.",
                 reasons=["Stability fixes the decay of the error, not the variance under noise. The variance still depends on the gain.",
                          "A stable gain is automatically the minimum-variance gain.",
                          "The process variance Q is zero whenever the error poles are stable."],
                 correct_reason=0,
                 fig=poles, alt=poles_alt)
    b.mc(3,
         r"The steady filter, run until the predicted variance stops changing, is",
         [r"the Lyapunov equation \(A^T P + P A = -Q\), with no measurement",
          "an observer whose gain is frozen at the variance-minimizing value",
          r"a state-feedback gain \(K = R^{-1} B^T P\)",
          r"a design that no longer depends on \(R\)"], 1,
         r"At equilibrium the recursion is an observer with one fixed \(L\), and that \(L\) is still the minimizer built from \(Q\) and \(R\). The Lyapunov equation has no measurement update. The control gain uses a different \(R\), the control weight. Dropping \(R\) would be the zero-measurement-noise limit, not the general steady filter.",
         model, model_alt)
    b.multi(3,
            r"Which statements hold for the minimum-variance correction?",
            [r"The scalar gain is \(p c / (c^2 p + r)\).",
             "That gain can be dropped into an observer in place of a hand-chosen polynomial.",
             "A larger process intensity leaves the steady gain unchanged.",
             r"The gain is computed from the unreachable modes of the pair \((A, B)\)."],
            [0, 1],
            r"The scalar formula is the derivative condition. The observer structure is the same correction \(L(y - C\hat{x})\), with this choice of \(L\). A larger \(Q\) feeds the predicted variance and moves the steady gain. Unreachable modes belong to a control rank test, not to this variance.",
            mat, mat_alt)

    b.num(4,
          r"A steady scalar filter has \(a = 1\), \(c = 1\), process variance \(4\), and measurement variance \(3\). The minimum steady updated variance is",
          steady_post, "m2",
          r"The steady predicted variance solves \(P^2 - 4P - 12 = 0\), so \(P = " + show(steady_p) + r"\). The gain is \(P/(P+3) = " + show(steady_l) + r"\), and the updated variance is \((1-L)P = " + show(steady_post) + r"\). Reporting the predicted variance \(6\) stops one step early. Reporting the process variance \(4\) reports \(q\), which equals \(L P\) and is not the posterior. Reporting \(3\) reports the measurement variance.",
          ell, ell_alt, ["gen-controller"])
    b.mc(4,
         r"A regulator gain \(K\) has already been chosen. The variance-minimizing \(L\) from this skill",
         [r"must equal \(K\), or the loop is inconsistent",
          r"replaces \(K\), because one gain can do both jobs",
          r"is chosen from \(Q\) and \(R\), and it does not have to equal \(K\)",
          r"is undefined until \(K\) is copied into the observer"], 2,
         r"The two gains answer different questions. \(K\) places or optimizes the control, and \(L\) minimizes the error variance. They meet later, in one loop, without being forced equal. Copying \(K\) into the observer is a particular choice, not a requirement of this variance.",
         poles, poles_alt, ["gen-controller", "lqr"])
    b.mc(4,
         r"A bound on the command is added, and the linear error variance is no longer the quantity you can freely minimize. The design that takes the bound into the optimization at each sample is",
         ["a longer pole-placement polynomial",
          r"a larger \(R\), which is the same thing as a hard bound",
          r"dropping the observer and using the measurement as the state",
          "a finite-horizon problem that enforces the bound and applies one input"], 3,
         r"A hard bound is a constraint, not a quadratic weight. Raising \(R\) discourages large inputs and still allows them. Pole placement does not see the bound. Replacing the state by the measurement abandons the model. A receding horizon is the later design that keeps the constraint inside the problem.",
         model, model_alt, ["mpc"])
    b.save()


# ---------------------------------------------------------------------------
# separation
# ---------------------------------------------------------------------------

def bank_separation():
    b = Bank("separation")
    fb = loop(["P"], "command from the estimate", fb="K", out="y")
    fb_alt = "A plant block with a gain K returned and subtracted."
    poles = splane([(-2, 0), (-3, 0), (-8, 0), (-10, 0)], [], "four real marks in the open left half-plane")
    poles_alt = "Four crosses on the negative real axis, two of them farther left."
    mat = matrix_fig([["A-BK", "0"], ["*", "A-LC"]], "a block-triangular closed loop")
    mat_alt = "A 2 by 2 block matrix with A minus B K and A minus L C on the diagonal."
    obs = loop(["model"], "the estimator driven by the same command", fb="L", inp="u", out="xhat")
    obs_alt = "A model block with a gain L returned and subtracted."

    real_sum = -2.0 - 3.0 - 8.0 - 10.0
    s_coeff = (5.0 - 2.0) + (6.0 - 2.0)  # poles at -(2-5) wait: A=2, BK=5, pole -3; A-LC=2-6=-4. sum of magnitudes 7
    # Compute explicitly:
    pole_k = 2.0 - 1.0 * 5.0
    pole_l = 2.0 - 6.0 * 1.0
    s_coeff = -(pole_k + pole_l)
    pole_k2 = -1.0 - 2.0 * 3.0
    real_sum2 = -1.0 - 4.0 - 6.0 - 6.0

    b.mc(1,
         r"The law \(u = -K\hat{x}\) is applied, and the observer model matches the plant. The eigenvalues of the joint system are",
         [r"the eigenvalues of \(A-BK\) together with the eigenvalues of \(A-LC\)",
          r"only the eigenvalues of \(A-BK\), because \(L\) is hidden inside the observer",
          r"the eigenvalues of \(A\), unchanged by either gain",
          r"the eigenvalues of \(KC\) and of \(LB\)"], 0,
         r"In error coordinates the joint matrix is block triangular, with \(A-BK\) and \(A-LC\) on the diagonal, so the spectra combine. Hiding \(L\) would be true of the reference transfer function, not of the eigenvalues. The open-loop \(A\) is what both gains are there to change. \(KC\) and \(LB\) are not the closed-loop blocks.",
         mat, mat_alt)
    b.num(1,
          r"The regulator poles are \(-2\) and \(-3\). The observer poles are \(-8\) and \(-10\). The sum of all four real parts is",
          real_sum, "rad/s",
          r"The joint spectrum is the union, so the real parts add: \(-2-3-8-10 = " + show(real_sum) + r"\). Adding only the regulator pair gives \(-5\). Adding only the observer pair gives \(-18\). The product of the observer poles is \(80\), which is not a sum of real parts.",
          poles, poles_alt)
    b.num(1,
          r"A scalar plant has \(A = 2\), \(B = 1\), \(K = 5\), \(C = 1\), and \(L = 6\). In the monic polynomial whose roots are the two closed-loop eigenvalues, the coefficient of \(s\) is",
          s_coeff, "rad/s",
          r"The eigenvalues are \(2 - 5 = " + show(pole_k) + r"\) and \(2 - 6 = " + show(pole_l) + r"\). The polynomial is \((s+3)(s+4) = s^2 + 7s + 12\), so the coefficient of \(s\) is " + show(s_coeff) + r". The constant term \(12\) is the product. Either eigenvalue alone is one factor, not the sum. The open-loop value \(2\) is neither root.",
          fb, fb_alt)

    b.sym(2,
          r"A scalar observer uses \(\dot{\hat{x}} = a\hat{x} + b u + l(y - c\hat{x})\). Write the eigenvalue of the estimation error in the names \(a\), \(l\), and \(c\).",
          "a-l*c", {"a": (-2.0, 3.0), "l": (0.4, 4.0), "c": (0.4, 3.0)},
          r"The error \(\tilde{x} = x - \hat{x}\) satisfies \(\dot{\tilde{x}} = (a - l c)\tilde{x}\) when the model matches, so the eigenvalue is \(a - l c\). The form \(a + l c\) is the sign error from adding the residual. The form \(a - l\) drops the output coefficient. The control gain is not in this eigenvalue.",
          alternates=["a-c*l", "-l*c+a"],
          fig=obs, alt=obs_alt)
    b.num(2,
          r"A scalar plant has \(A = -1\), \(B = 2\), and \(K = 3\). The state-feedback eigenvalue of \(A - BK\) is",
          pole_k2, "rad/s",
          r"\(-1 - 2 \times 3 = " + show(pole_k2) + r"\). Forgetting the input coefficient \(2\) gives \(-1 - 3 = -4\). Using \(A + BK\) gives \(-1 + 6 = 5\), the unstable sign error. Reporting \(K = 3\) reports the gain, not the eigenvalue.",
          fb, fb_alt)
    b.order(2,
            r"Put these design steps in the order you would use them for output feedback through an estimate.",
            ["Place the state-feedback gain from the regulator poles.",
             "Place the observer gain from the error poles.",
             "Replace the state in the control law by the estimate.",
             "Drive the observer with the applied command and with the measured output.",
             "Check that the joint eigenvalues are the union of the two sets you placed."],
            r"Each gain is designed for its own matrix, and neither design needs the other number. The law then uses the estimate, and the observer has to see the command that the plant sees, or the error equation picks up a leftover input. The eigenvalue check is last: it confirms the triangular split rather than creating it.",
            mat, mat_alt)

    b.find_error(3,
                 r"The observer model matches the plant, and both gains have been placed. One step is wrong.",
                 [r"The control law uses the estimate, \(u = -K\hat{x}\).",
                  r"The joint eigenvalues are those of \(A-BK\) and those of \(A-LC\).",
                  "Those observer eigenvalues appear in the transfer function from the reference to the output.",
                  "A mismatch between the observer model and the plant removes this clean split."],
                 2,
                 r"With a matching model the error equation is not driven by the reference, so the transfer function from the reference to the output does not contain the observer poles. They are still eigenvalues, and a nonzero initial estimation error does show them in \(y\). The third step confuses those two facts. The other steps are the split and its hypothesis.",
                 reasons=["A matching model keeps the reference out of the error equation, so the reference transfer does not contain the observer poles.",
                          "Observer poles are cancelled only when the model is wrong.",
                          "The reference transfer contains every joint eigenvalue, with no cancellation."],
                 correct_reason=0,
                 fig=poles, alt=poles_alt)
    b.mc(3,
         r"The split into \(A-BK\) and \(A-LC\) fails to stay that simple when",
         ["the two gains were designed by different people",
          r"the observer is built from a different \(A\) or \(C\) than the plant",
          r"the observer poles are faster than the regulator poles",
          r"the state dimension is \(2\)"], 1,
         r"The triangular form uses one \(A\) and one \(C\) in both the plant and the copy. A different model leaves a driving term in the error, and the characteristic polynomial does not factor so cleanly. Who designed the gains is irrelevant. Faster observer poles are a common choice, not a threat to the algebra. Dimension \(2\) is ordinary.",
         obs, obs_alt)
    b.multi(3,
            r"Which statements hold when the observer model matches the plant?",
            [r"\(K\) and \(L\) may be placed separately.",
             "The joint eigenvalues are the union of the two placed sets.",
             "The observer poles have to equal the regulator poles.",
             "A wrong model in the observer keeps the same split."],
            [0, 1],
            r"Separate placement is the content of the principle, and the spectrum is the union. Nothing forces the two sets to coincide. A wrong model is exactly the case where the extra cross term appears and the split is no longer the whole story.",
            mat, mat_alt)

    b.num(4,
          r"Regulator poles \(-1\) and \(-4\), observer poles \(-6\) and \(-6\). The sum of the four real parts, which the joint system must show, is",
          real_sum2, "rad/s",
          r"Union means addition of the real parts: \(-1-4-6-6 = " + show(real_sum2) + r"\). The regulator pair alone sums to \(-5\). The repeated observer pole is \(-6\), not \(-12\), until you count it twice. The product \(24\) of the regulator poles is not this sum.",
          poles, poles_alt, ["gen-controller"])
    b.mc(4,
         r"A feedforward term from the reference is added on top of \(u = -K\hat{x}\). The eigenvalues of \(A-BK\) and \(A-LC\)",
         [r"move, because every new path changes \(A-BK\)",
          r"collapse to the observer poles only",
          "stay where the two gains put them",
          r"become the eigenvalues of the feedforward gain"], 2,
         r"A term \(F r\) enters as an input. It does not change \(A-BK\) or \(A-LC\). Those matrices are the homogeneous part. The feedforward gain is a matrix of a different shape, and it is not a list of eigenvalues. Collapsing the spectrum would mean deleting \(K\), which this term does not do.",
         fb, fb_alt, ["gen-controller"])
    b.mc(4,
         r"After \(K\) and \(L\) are placed for a matching model, a constant reference still needs",
         [r"a second copy of \(K\), because one gain cannot see \(r\)",
          r"the observer poles moved onto the regulator poles",
          r"\(L\) set equal to \(K\)",
          "a path from the reference into the command, chosen for the steady map"], 3,
         r"Pole placement fixes the transient. The steady gain from \(r\) to \(y\) is a separate number, the feedforward or reference scale in the command. A second copy of \(K\) does not create that path. Matching the two pole sets, or setting \(L = K\), is not required for a constant reference.",
         obs, obs_alt, ["gen-controller"])
    b.save()


# ---------------------------------------------------------------------------
# general controller
# ---------------------------------------------------------------------------

def bank_gen():
    b = Bank("gen-controller")
    two = parallel_sum(["F", "K"], "reference term and estimate term adding into the command", output_label="u")
    two_alt = "Two blocks side by side whose outputs add to form the command."
    fb = loop(["P"], "plant under the combined command", fb="K")
    fb_alt = "A plant block with a gain returned and subtracted."
    obs = loop(["model"], "observer using the applied command", fb="L", inp="u", out="xhat")
    obs_alt = "A model block with a gain L returned and subtracted."
    mat = matrix_fig([["F", "K"]], "a reference gain beside a state gain")
    mat_alt = "A row of two labels, F and K."

    u1 = 4.0 * 1.0 - 1.5 * 2.0
    # a=-2, b=4, K=3, x=r, 0 = a + b F - b K => F = K - a/b
    f1 = 3.0 - (-2.0) / 4.0
    u2 = 2.5 * 2.0 - 0.5 * 3.0
    f4 = 2.5 - (-1.0) / 2.0

    b.mc(1,
         r"A two-degree-of-freedom command built from a reference and an estimate has the shape",
         [r"\(u = F r - K\hat{x}\), with both terms present",
          r"\(u = F r\), and the estimate is only for display",
          r"\(u = -K\hat{x}\), with no separate reference term",
          r"\(u = L(y - r)\)"], 0,
         r"One term carries the reference, and the other carries the estimate. Dropping either term deletes a degree of freedom: pure feedforward has no feedback, and pure \(-\!K\hat{x}\) still needs a scale if a constant reference is to land on the right steady output. An output-error gain \(L\) is an observer correction, not this command.",
         two, two_alt)
    b.num(1,
          r"\(F = 4\), \(r = 1\), \(K = 1.5\), and the estimate is \(2\). The command \(F r - K\hat{x}\) is",
          u1, "1",
          r"\(4 \times 1 - 1.5 \times 2 = " + show(u1) + r"\). Adding the terms instead of subtracting gives \(7\). Using the estimate as if it were the reference gives \(4 \times 2 - 1.5 \times 1 = 6.5\). Reporting \(F = 4\) leaves the estimate out of the command.",
          mat, mat_alt)
    b.num(1,
          r"A scalar plant \(\dot{x} = -2x + 4u\), \(y = x\), uses \(u = F r - K x\) with \(K = 3\). The \(F\) that makes a constant reference satisfy \(y = r\) in steady state is",
          f1, "1",
          r"Steady state says \(0 = -2r + 4(F r - 3r)\), so \(4F = 2 + 12\) and \(F = " + show(f1) + r"\). Copying \(K\) and reporting \(3\) misses the open-loop \(-2/4\). The product \(4 \times 3 = 12\) is the feedback piece before it is divided by \(b\). Setting \(F = 1\) would fit a different plant.",
          fb, fb_alt)

    b.sym(2,
          r"The command is a reference term minus a gain times the estimate. Write it in the names \(f\), \(r\), \(k\), and \(x\).",
          "f*r-k*x", {"f": (0.4, 3.0), "r": (0.4, 3.0), "k": (0.4, 3.0), "x": (0.4, 3.0)},
          r"The two degrees of freedom are exactly those two terms: \(f r - k x\). Adding them, \(f r + k x\), flips the feedback sign. Using \(f r\) alone drops the estimate. Using \(k(r-x)\) forces the two gains to be one number.",
          alternates=["f*r-x*k", "-k*x+f*r"],
          fig=two, alt=two_alt)
    b.num(2,
          r"\(F = 2.5\), \(r = 2\), \(K = 0.5\), and the estimate is \(3\). The command is",
          u2, "1",
          r"\(2.5 \times 2 - 0.5 \times 3 = " + show(u2) + r"\). The sum \(5 + 1.5 = 6.5\) has the feedback sign wrong. Dropping the estimate leaves the feedforward piece \(5\). The gain \(0.5\) is not the command.",
          mat, mat_alt)
    b.order(2,
            r"Put these steps in the order you would build the combined command.",
            ["Design the state-feedback gain for the regulation poles.",
             "Design the observer gain for the estimation poles.",
             "Choose the feedforward gain so a constant reference matches in steady state.",
             "Apply the command as the feedforward term minus the gain times the estimate.",
             "Feed that same command into the observer, along with the measured output."],
            r"The two gains are independent designs. The feedforward number is fixed afterwards from the steady map, using the \(K\) you already have. The command is then assembled, and the observer must be driven by that same command. Driving the observer with a different input leaves a false error.",
            obs, obs_alt)

    b.find_error(3,
                 r"A combined command \(u = F r - K\hat{x}\) is being justified. One step is wrong.",
                 [r"The command has a reference term and an estimate term.",
                  r"\(F\) is chosen from the steady map and does not replace \(K\).",
                  r"Once \(F\) is in place, the observer gain can be set to zero, because the reference no longer needs an estimate.",
                  "The observer is driven by the applied command and by the measured output."],
                 2,
                 r"\(F\) shapes the path from the reference. A disturbance, a bad initial estimate, and any state you do not measure still need the correction. Setting the observer gain to zero freezes the estimate at its open prediction. The other steps are the structure.",
                 reasons=["Feedforward does not estimate the state. Zeroing the observer gain drops the correction of disturbances and of a bad initial estimate.",
                          "A nonzero feedforward gain moves the eigenvalues of A minus B K.",
                          "The observer should be driven by the reference and not by the applied command."],
                 correct_reason=0,
                 fig=obs, alt=obs_alt)
    b.mc(3,
         r"Changing the feedforward gain \(F\), and leaving \(K\) and \(L\) alone,",
         [r"moves every eigenvalue of \(A - BK\)",
          r"does not move the eigenvalues of \(A-BK\) or of \(A-LC\)",
          r"forces \(L\) to be redesigned",
          "deletes the estimate from the command"], 1,
         r"\(F r\) is an input. The homogeneous matrices \(A-BK\) and \(A-LC\) do not contain \(F\). You redesign \(L\) when the error poles or the noise model change, not when the reference scale changes. The estimate term \(-K\hat{x}\) is still in the command.",
         fb, fb_alt)
    b.multi(3,
            r"Which statements hold for \(u = F r - K\hat{x}\)?",
            ["The command depends on the reference and on the estimate.",
             "The feedforward gain is what matches a constant reference in steady state.",
             r"The feedforward gain moves the eigenvalues of \(A-BK\).",
             "The observer can be removed once the feedforward gain is set."],
            [0, 1],
            r"Both terms are the structure. \(F\) is solved from the steady map, and that solve does not edit \(A-BK\). The observer remains the way the estimate is produced. Removing it would require the true state.",
            two, two_alt)

    b.num(4,
          r"A scalar plant \(\dot{x} = -x + 2u\), \(y = x\), uses \(K = 2.5\). The feedforward \(F\) that enforces \(y = r\) in steady state is",
          f4, "1",
          r"\(0 = -r + 2(F r - 2.5 r)\) gives \(2F = 1 + 5\), so \(F = " + show(f4) + r"\). Reporting \(K = 2.5\) misses the plant term \(-a/b = 0.5\). Twice the gain, \(5\), is the feedback contribution before dividing by \(b\). Setting \(F = 1\) fits a plant whose DC map is already \(1\).",
          fb, fb_alt, ["integral-action", "lqr"])
    b.mc(4,
         r"A constant load remains, and \(F\) was computed for the unloaded steady map. The extra state that removes the resulting offset is",
         [r"a second feedforward gain, fitted to the same unloaded model",
          r"a faster observer, with \(L\) doubled",
          "an integrator of the tracking error, with its own gain",
          r"the replacement of \(K\) by \(F\)"], 2,
         r"An integrator of \(r - y\) grows until the offset is gone, provided the augmented loop is stable. Another feedforward number from the unloaded model has the same blind spot. A faster observer estimates the old model more quickly and does not add the missing constant channel. Replacing \(K\) by \(F\) deletes feedback.",
         two, two_alt, ["integral-action"])
    b.mc(4,
         r"You want a different response to the reference without reopening the loop gain. The knob for that, in this structure, is",
         [r"the observer gain \(L\) only",
          r"the open-loop matrix \(A\), edited in place",
          r"the measurement matrix \(C\), with a new sensor",
          r"the feedforward gain \(F\), leaving \(K\) fixed"], 3,
         r"\(F\) scales the reference path and leaves \(A-BK\) alone, which is the loop part of this design. \(L\) changes the error poles, not the reference map's eigenvalues. Editing \(A\) or \(C\) changes the plant you were given.",
         mat, mat_alt, ["mpc"])
    b.save()


# ---------------------------------------------------------------------------
# integral action
# ---------------------------------------------------------------------------

def bank_integral():
    b = Bank("integral-action")
    fb = loop(["P"], "state feedback with an extra integrator", fb="Ki", inp="r", out="y")
    fb_alt = "A plant block with a gain returned and subtracted from the reference."
    mat = matrix_fig([["a", "0"], ["-1", "0"]], "the augmented state matrix before the gain")
    mat_alt = "A 2 by 2 matrix with a and 0 on the first row and -1 and 0 on the second."
    step = step_response("a step settling to the reference", tau=0.8, goal=1.0)
    step_alt = "A smooth curve rising toward a horizontal goal."
    poles = splane([(-1, 0), (-2, 0)], [], "a pair of real closed-loop poles")
    poles_alt = "Two crosses on the negative real axis."

    ki_12 = 2.0
    ki_b = 10.0 / 2.0
    k_aug = (5.0 + 1.0) / 2.0
    xi_ss = 4.0 / 0.5

    b.mc(1,
         r"Integral action in state feedback adds a state whose derivative is the tracking error, so that a stable closed loop",
         ["cannot keep a nonzero constant error",
          "cancels every zero of the plant",
          r"makes \(A - BK\) unnecessary",
          "removes the need for a reachable pair"], 0,
         r"In steady state the derivative of the integrator state is zero, so \(y = r\), and stability is what makes the trajectory arrive there. The plant zeros are a different object. The gain on the original state is still part of the design. Reachability of the augmented pair is still the condition for placing both poles.",
         fb, fb_alt)
    b.num(1,
          r"The plant is \(\dot{x} = u\), \(y = x\), and the desired polynomial is \((s+1)(s+2)\). With \(u = -k x + k_i \xi\) and \(\dot{\xi} = r - y\), the integrator gain \(k_i\) is",
          ki_12, "1",
          r"The closed-loop polynomial is \(s^2 + k s + k_i\). The constant term of \((s+1)(s+2)\) is \(2\), so \(k_i = " + show(ki_12) + r"\). The coefficient of \(s\) is \(3\), which is \(k\), not \(k_i\). The sum \(1+2 = 3\) is that same coefficient. Reporting \(1\) uses only one of the poles.",
          poles, poles_alt)
    b.num(1,
          r"The plant is \(\dot{x} = 2u\), \(y = x\). The desired constant term is \(10\). The integrator gain \(k_i\) is",
          ki_b, "1",
          r"The constant term is \(b k_i = 2 k_i\). Setting that equal to \(10\) gives \(k_i = " + show(ki_b) + r"\). Reporting \(10\) forgets to divide by the input coefficient. Reporting \(20\) multiplies instead. The input coefficient \(2\) is not the gain.",
          mat, mat_alt)

    b.sym(2,
          r"The plant is an integrator \(\dot{x} = b u\). The gain on \(x\) is \(k\). Write the coefficient of \(s\) in the closed-loop polynomial, in the names \(b\) and \(k\).",
          "b*k", {"b": (0.4, 3.0), "k": (0.4, 4.0)},
          r"With \(a = 0\), the coefficient of \(s\) is \(b k\). The constant term is the other one, \(b k_i\), and it is not asked. Reporting \(k\) drops the input coefficient. Reporting \(b + k\) adds the two numbers that multiply.",
          alternates=["k*b"],
          fig=mat, alt=mat_alt)
    b.num(2,
          r"The plant is \(\dot{x} = x + 2u\), \(y = x\). The desired polynomial is \(s^2 + 5s + 8\). The gain \(k\) on \(x\) is",
          k_aug, "1",
          r"The coefficient of \(s\) is \(b k - a = 2k - 1\). Set that equal to \(5\): \(2k = 6\), so \(k = " + show(k_aug) + r"\). The constant term \(8\) fixes \(k_i = 4\), not \(k\). Forgetting the open-loop \(1\) and dividing \(5\) by \(2\) gives \(2.5\). Reporting \(5\) leaves the input coefficient in the polynomial.",
          poles, poles_alt)
    b.order(2,
            r"Put these steps in the order you would add integral action to state feedback.",
            ["Add a state whose derivative is the tracking error.",
             "Write the augmented state matrix and input vector, with a zero column and a zero input entry for the new state.",
             "Choose the poles of the augmented loop.",
             "Solve for the gain on the original state and the gain on the integrator state.",
             "Check that a constant command and a constant load leave only the equilibrium where the error is zero."],
            r"The new state has to exist before its row can be written. The augmented matrices are what you place. The poles are the target of that placement, and the two gains fall out of one solve. The steady-state check is how you confirm the sign of the integrator, and it comes after the gain exists.",
            fb, fb_alt)

    b.find_error(3,
                 r"A constant reference and a constant load act on a loop with an integrator of \(r - y\). One step is wrong.",
                 ["The new state integrates the tracking error.",
                  "In a steady state of a stable loop, that derivative is zero, so the output equals the reference.",
                  "The same zero error is reached even if the augmented loop is unstable, because the integrator keeps winding.",
                  "The gain on the integrator state is chosen together with the gain on the original state."],
                 2,
                 r"An unstable augmented loop does not settle, so the winding does not stop at the cancelling value. Stability is the hypothesis that turns the integrator into zero steady error. The other steps are the construction.",
                 reasons=["An unstable loop does not converge, so the integrator state does not settle at the cancelling value.",
                          "Instability makes the integrator reach zero error faster.",
                          "The integrator gain is fixed at 1 and is not part of the placement."],
                 correct_reason=0,
                 fig=step, alt=step_alt)
    b.mc(3,
         r"A constant reference scale \(k_r\), with no extra state, fails to remove a constant load when",
         ["the closed loop is stable",
          r"the plant gain \(b\) is positive",
          r"\(k_r\) was computed from the unloaded model and the load was not in that model",
          "the state is two-dimensional"], 2,
         r"A fixed \(k_r\) sets one DC number. A load that the model did not include shifts the steady output, and there is no state left to wind up and cancel it. Stability, a positive \(b\), and the state dimension are not the reason that particular scale misses the load.",
         fb, fb_alt)
    b.multi(3,
            r"Which statements hold for the augmented design \(u = -k x + k_i \xi\), \(\dot{\xi} = r - y\)?",
            ["A stable augmented loop drives a constant tracking error to zero.",
             "The gain vector has an entry for the integrator state.",
             "This construction is the derivative term of a three-term output controller.",
             "The integrator removes actuator saturation by itself."],
            [0, 1],
            r"Zero steady error is the stable equilibrium of the integrator. The gain that places the augmented poles has one entry per state, including \(\xi\). The derivative term is a different channel. Saturation of the actuator still winds the integrator unless a separate limit is added.",
            mat, mat_alt)

    b.num(4,
          r"At the steady state the proportional term is zero, the integrator gain is \(0.5\), and the command that cancels a constant load is \(4\). The integrator state is",
          xi_ss, "1",
          r"The command is \(k_i \xi\) once the proportional term is zero, so \(\xi = 4 / 0.5 = " + show(xi_ss) + r"\). The product \(0.5 \times 4 = 2\) multiplies instead of dividing. Reporting the command \(4\) skips the gain. Reporting the gain \(0.5\) skips the command.",
          step, step_alt, ["gen-controller", "mpc"])
    b.mc(4,
         r"The same integrator is placed by a quadratic cost on the augmented state, instead of by naming the polynomial. That design is",
         ["a second copy of the integrator",
          "a gain from a Riccati equation on the augmented matrices",
          r"a schedule indexed by the load",
          "an open-loop cancellation of the load"], 1,
         r"A quadratic cost on the augmented state produces one gain, including the entry on \(\xi\), from the Riccati equation. It does not add another integrator. A schedule would be a table of gains. Open-loop cancellation is feedforward of a measured load, which this cost does not require.",
         poles, poles_alt, ["lqr"])
    b.mc(4,
         r"The actuator saturates and the integrator keeps integrating a nonzero error. The failure mode, and the later fix of clamping or unwinding, belong with",
         [r"a faster choice of the augmented poles",
          r"deleting \(C\) so the error is zero by definition",
          r"raising \(k_i\) without a limit",
          "the saturation of this integrator, handled outside the linear gain"], 3,
         r"Faster poles and a larger \(k_i\) still assume the command that was computed is the command that is applied. Deleting \(C\) hides the error instead of removing it. The linear design has no knowledge of the stop, so the unwind has to be added when the actuator hits it.",
         step, step_alt, ["mpc"])
    b.save()


# ---------------------------------------------------------------------------
# lqr
# ---------------------------------------------------------------------------

def bank_lqr():
    b = Bank("lqr")
    fb = loop(["P"], "state feedback from a quadratic cost", fb="K")
    fb_alt = "A plant block with a gain K returned and subtracted."
    poles = splane([(-2, 0)], [], "a closed-loop pole on the negative real axis")
    poles_alt = "One cross on the negative real axis."
    mat = matrix_fig([["Q", "R"]], "a state weight beside a control weight")
    mat_alt = "A row of two labels, Q and R."
    curve = step_response("a cheap-control response settling quickly", tau=0.45, goal=1.0)
    curve_alt = "A curve that rises and levels off."

    k_int = lqr_gain(0.0, 1.0, 4.0, 1.0)[0]
    k_int2 = lqr_gain(0.0, 1.0, 9.0, 4.0)[0]
    k_uns, p_uns = lqr_gain(1.0, 1.0, 3.0, 1.0)
    k_big = lqr_gain(0.0, 1.0, 36.0, 4.0)[0]

    b.mc(1,
         r"A linear quadratic regulator chooses the gain \(K\) by",
         ["minimizing a quadratic cost in the state and the command",
          "copying the open-loop eigenvalues",
          r"setting \(K = B\), with no weights",
          r"cancelling every entry of \(A\) by hand"], 0,
         r"The design starts from the cost, and the gain is whatever that cost selects. Copying the open-loop eigenvalues does nothing. \(K = B\) ignores both weights. Cancelling \(A\) entrywise is not the Riccati solution, even though the closed loop does move the eigenvalues.",
         fb, fb_alt)
    b.num(1,
          r"For \(\dot{x} = u\), state weight \(4\), and control weight \(1\), the regulator gain is",
          k_int, "1",
          r"The scalar integrator has \(K = \sqrt{q/r} = \sqrt{4/1} = " + show(k_int) + r"\). The ratio \(q/r = 4\) without the square root is the square of the gain. The reciprocal \(\sqrt{r/q} = 0.5\) inverts the weights. The sum \(4+1 = 5\) is neither weight's job.",
          mat, mat_alt)
    b.num(1,
          r"For the same integrator \(\dot{x} = u\), state weight \(9\), and control weight \(4\), the gain is",
          k_int2, "1",
          r"\(K = \sqrt{9/4} = " + show(k_int2) + r"\). The Riccati solution \(P = \sqrt{q r} = 6\) is not the gain; dividing by \(r\) is what turns it into \(K\). Reporting \(9\) or \(4\) reports a weight.",
          curve, curve_alt)

    b.sym(2,
          r"For \(\dot{x} = u\), write the regulator gain in the names \(q\) and \(r\), the state weight and the control weight.",
          "sqrt(q/r)", {"q": (0.4, 4.0), "r": (0.4, 4.0)},
          r"The Riccati solution is \(\sqrt{q r}\) and the gain divides by \(r\), leaving \(\sqrt{q/r}\). The ratio \(q/r\) misses the root. The reciprocal root \(\sqrt{r/q}\) swaps the weights. The product \(q r\) is the square of \(P\), not the gain.",
          alternates=["(q/r)**(1/2)"],
          fig=mat, alt=mat_alt)
    b.num(2,
          r"For \(\dot{x} = x + u\), state weight \(3\), and control weight \(1\), the positive Riccati solution gives the gain",
          k_uns, "1",
          r"The scalar equation is \(p^2 - 2p - 3 = 0\), so the positive solution is \(p = 3\) and \(K = " + show(k_uns) + r"\). The negative root \(-1\) is not a positive cost matrix. Reporting the state weight \(3\) happens to match \(K\) here because \(b = r = 1\), and the check is the closed-loop eigenvalue \(1 - 3 = -2\), not the weight. Using \(K = a = 1\) only cancels the open-loop term and leaves a pole at \(0\).",
          poles, poles_alt)
    b.order(2,
            r"Put these regulator steps in the order you would do them.",
            ["Choose the state weight and the control weight.",
             "Solve the algebraic Riccati equation for the cost matrix.",
             "Set the gain to the inverse of the control weight times B transpose times that matrix.",
             "Check that A minus B K is stable.",
             "Read a larger control weight as a reason to use less command, not more."],
            r"The weights define the cost, so they come before the equation. The Riccati solution is the matrix the gain formula consumes. The stability check is the property that solution is supposed to deliver. Reading the weight is how you explain the number you got, and it is not a substitute for the solve.",
            fb, fb_alt)

    b.find_error(3,
                 r"A reachable pair and positive weights are already in hand. One step is wrong.",
                 [r"The cost weights the state with \(Q\) and the command with \(R\).",
                  r"The gain is \(R^{-1} B^T P\), with \(P\) from the Riccati equation.",
                  r"Increasing \(R\) makes the command more expensive, so the optimal gain gets larger.",
                  r"The closed loop is \(A-BK\), and the positive solution makes it stable under the usual definiteness conditions."],
                 2,
                 r"A larger \(R\) penalizes the command, so the minimizer uses less of it and the gain gets smaller. The cost, the formula, and the stability claim are the design. The third step has the comparative static backwards.",
                 reasons=["A larger control weight penalizes the command, so the minimizing gain gets smaller.",
                          "A larger R increases Q by the same factor.",
                          "The Riccati equation does not involve R."],
                 correct_reason=0,
                 fig=mat, alt=mat_alt)
    b.mc(3,
         r"On an infinite horizon with no explicit constraint, the regulator gain is",
         [r"recomputed from scratch at every time, with a shrinking horizon",
          "a constant matrix, from one algebraic Riccati equation",
          r"equal to the open-loop \(A\)",
          "defined only for a single sample"], 1,
         r"Time-invariant weights and an infinite horizon make the gain constant. Recomputing on a shrinking horizon is a finite-horizon problem. The gain is not \(A\). A single sample is a one-step problem, not this limit.",
         curve, curve_alt)
    b.multi(3,
            r"Which statements hold for the infinite-horizon regulator?",
            ["The gain depends on both the state weight and the control weight.",
             "A larger state weight pushes the design to keep that state smaller.",
             "The algebraic Riccati equation is the Lyapunov equation with the quadratic gain term removed and nothing put in its place.",
             "The optimal gain grows when the control weight grows."],
            [0, 1],
            r"Both weights enter the gain. Penalizing a state more is what a larger \(Q\) does. The Riccati equation is the Lyapunov equation plus the term that contains the gain, so deleting that term is a different equation. A larger control weight shrinks the gain.",
            fb, fb_alt)

    b.num(4,
          r"For \(\dot{x} = u\), state weight \(36\), and control weight \(4\), the gain is",
          k_big, "1",
          r"\(K = \sqrt{36/4} = " + show(k_big) + r"\). The root of the product \(\sqrt{36 \times 4} = 12\) is \(P\), and the gain is \(P/R = 3\). Reporting \(36\) or \(4\) reports a weight. The difference \(36 - 4 = 32\) is not a gain.",
          mat, mat_alt, ["mpc"])
    b.mc(4,
         r"A hard limit on the command is required, and a quadratic weight is not a substitute for it. The design that enforces the limit is",
         [r"a larger control weight, which is the same as a hard stop",
          r"the Lyapunov equation with \(Q\) set to zero",
          "a finite-horizon problem that treats the limit as a constraint",
          "the open-loop matrix, left unchanged"], 2,
         r"A weight makes large commands expensive and still allows them. A constraint removes the illegal values from the problem, which a receding horizon can do at each sample. The Lyapunov equation does not choose \(K\). Leaving \(A\) unchanged applies no control.",
         curve, curve_alt, ["mpc"])
    b.mc(4,
         r"The same plant is augmented with an integrator of the tracking error before the cost is written. The regulator then",
         [r"drops the integrator, because a quadratic cost cannot see an extra state",
          r"uses the control weight as the integrator gain with no solve",
          r"is undefined, because the augmented \(A\) has an eigenvalue at \(0\)",
          "returns a gain that includes an entry for the integrator state"], 3,
         r"The cost is written on whatever state you hand it, including the integrator state, and the gain has one entry per state. An eigenvalue at \(0\) in the open loop is allowed when the pair stays reachable and the weights keep the solution positive. The control weight is not itself the integrator gain.",
         poles, poles_alt, ["integral-action"])
    b.save()


# ---------------------------------------------------------------------------
# mpc
# ---------------------------------------------------------------------------

def bank_mpc():
    b = Bank("mpc")
    fb = loop(["P"], "a command held for one sample", fb="1")
    fb_alt = "A plant block with the output returned and subtracted."
    step = step_response("a predicted output over a short horizon", tau=1.2, goal=1.0, t_end=4.0)
    step_alt = "A curve that rises toward a level and stops at a finite time."
    mat = matrix_fig([["N", "u"]], "a horizon length beside a command")
    mat_alt = "A row with the labels N and u."
    bounds = splane([(-1, 0)], [], "a sample pole inside the stable half")
    bounds_alt = "One cross on the negative real axis."

    look = 4.0 * 0.5
    applied, raw = one_step(6.0, 2.0, 1.0)
    free, _ = one_step(5.0, 4.0, 100.0)
    bound_u, raw4 = one_step(9.0, 2.0, 1.5)

    b.mc(1,
         r"Model predictive control, at each sample,",
         ["solves a finite-horizon problem and applies only the first input",
          "applies the entire computed sequence with no further measurement",
          r"uses the infinite-horizon gain and ignores constraints",
          "replaces the model by a constant"], 0,
         r"The horizon is recomputed from the latest state, and only the first move is kept. Applying the whole sequence is open-loop optimal control. The infinite-horizon unconstrained gain is the quadratic regulator. A constant has no prediction.",
         step, step_alt)
    b.num(1,
          r"The horizon is \(4\) samples and the sample period is \(0.5\) seconds. The look-ahead time is",
          look, "s",
          r"Four samples of half a second cover " + show(look) + r" seconds. The sample count \(4\) is not a time. The period \(0.5\) is one step. Adding them gives \(4.5\), which mixes a count with a time.",
          mat, mat_alt)
    b.num(1,
          r"One step minimizes \((x+u)^2 + 2 u^2\) with \(x = 6\) and \(|u| \le 1\). The applied command is",
          applied, "1",
          r"The unconstrained minimizer is \(-x/(1+2) = -2\). The bound cuts it to " + show(applied) + r". Reporting \(-2\) ignores the constraint. Reporting \(1\) takes the positive end of the interval, opposite the sign of the unconstrained move. Reporting \(x = 6\) reports the state.",
          fb, fb_alt)

    b.sym(2,
          r"One unconstrained step minimizes \((x+u)^2 + r u^2\). Write the minimizing \(u\) in the names \(x\) and \(r\).",
          "-x/(1+r)", {"x": (0.5, 4.0), "r": (0.3, 3.0)},
          r"The derivative in \(u\) is \(2(x+u) + 2 r u = 0\), so \(u = -x/(1+r)\). The form \(-x/r\) drops the state penalty's share of the denominator. The form \(x/(1+r)\) has the sign that increases the predicted state instead of decreasing it. The form \(-x\) ignores the weight.",
          alternates=["-x/(r+1)", "(-1)*x/(1+r)"],
          fig=mat, alt=mat_alt)
    b.num(2,
          r"One unconstrained step minimizes \((x+u)^2 + 4 u^2\) with \(x = 5\). The command is",
          free, "1",
          r"\(u = -5/(1+4) = " + show(free) + r"\). Dividing by the weight alone gives \(-5/4 = -1.25\). The positive value \(1\) has the wrong sign. Reporting \(5\) reports the state.",
          step, step_alt)
    b.order(2,
            r"Put these receding-horizon steps in the order they happen at a sample.",
            ["Predict the state over the horizon from the current state.",
             "Write the cost and the constraints on that prediction.",
             "Solve for the whole input sequence.",
             "Apply only the first input.",
             "At the next sample, rebuild the problem from the new state."],
            r"The prediction needs the current state before a cost can be written on it. The solve comes after the problem exists, and it returns a sequence. Only the first entry is applied. The next sample does not reuse that sequence; it starts again. Applying the rest of the sequence would skip the last step.",
            fb, fb_alt)

    b.find_error(3,
                 r"A horizon of several steps has just been solved. One step of the implementation is wrong.",
                 ["The solver looked ahead from the state measured at this sample.",
                  "Constraints on the command were included in that finite problem.",
                  "The whole input sequence is then applied, with no new measurement, until the horizon ends.",
                  "The problem is built again at the next sample from the new state."],
                 2,
                 r"Keeping the whole sequence is open-loop. The receding implementation throws the tail away and resolves. The look-ahead, the constraints, and the rebuild are the parts that make the method closed loop.",
                 reasons=["Applying the whole sequence ignores every later measurement. Only the first input is kept.",
                          "The horizon length is the number of inputs that must be applied.",
                          "Constraints are enforced by deleting the model."],
                 correct_reason=0,
                 fig=step, alt=step_alt)
    b.mc(3,
         r"Lengthening the horizon, with the same model and the same constraints,",
         [r"always leaves the first input unchanged",
          "lets the plan see further, and costs a larger optimization",
          r"removes the need to measure the state",
          "turns the problem into an infinite-horizon unconstrained regulator"], 1,
         r"A longer window can change the first move, because the plan feels constraints and costs that used to lie past the end. The state is still the initial condition. The infinite unconstrained problem is a different limit, not a longer copy of a constrained one.",
         bounds, bounds_alt)
    b.multi(3,
            r"Which statements hold for one sample of a receding-horizon controller?",
            ["Constraints can limit the command inside the finite problem.",
             "Only the first computed input is applied.",
             "The horizon is infinite and unconstrained, which is what separates this method from a quadratic regulator.",
             "The model is discarded after the first sample and never used again."],
            [0, 1],
            r"The finite problem is allowed to contain bounds, and the implementation keeps the first input. An infinite unconstrained horizon is the regulator, the method this one is being distinguished from. The model is used again at the next sample.",
            mat, mat_alt)

    b.num(4,
          r"One step minimizes \((x+u)^2 + 2 u^2\) with \(x = 9\) and \(|u| \le 1.5\). The applied command is",
          bound_u, "1",
          r"The unconstrained command is \(-9/3 = " + show(raw4) + r"\). The bound at \(1.5\) cuts it to " + show(bound_u) + r". Reporting \(-3\) ignores the stop. Reporting \(1.5\) flips the sign. Reporting \(9\) reports the state.",
          fb, fb_alt, ["lqr"])
    b.mc(4,
         r"With no constraints and an infinite horizon, the same quadratic cost produces",
         ["a new finite sequence at every sample",
          r"a gain that changes because the horizon shrinks",
          r"a gain from one algebraic Riccati equation, applied as \(u = -Kx\)",
          "an infeasible problem"], 2,
         r"That limit is the regulator: one constant gain, no constraint to enforce. A new sequence and a shrinking horizon are the finite problem. The infinite problem is feasible for the usual positive weights.",
         bounds, bounds_alt, ["lqr"])
    b.mc(4,
         r"The model used for the horizon is a linearization that was exact only at one operating point, and the operating point moves. A table of linear designs indexed by a measurement of that point is",
         [r"the same finite-horizon solve, with a longer \(N\)",
          r"an integrator added inside the horizon",
          r"a reason to drop the constraints",
          "a scheduled family of controllers, not a single receding solve"], 3,
         r"A schedule stores gains against a measured variable. It does not lengthen \(N\), and it does not add an integrator. The constraints, if you still want them, belong to the predictive problem, not to the existence of the table.",
         step, step_alt, ["adaptive"])
    b.save()


# ---------------------------------------------------------------------------
# feedback linearization
# ---------------------------------------------------------------------------

def bank_fb_lin():
    b = Bank("fb-linearization")
    fb = loop(["P"], "an inner cancellation around a nonlinear plant", fb="g")
    fb_alt = "A plant block with a gain returned and subtracted."
    step = step_response("the linear closed loop after cancellation", tau=0.6, goal=1.0)
    step_alt = "A smooth rise toward a steady level."
    poles = splane([(-2, 0)], [], "the pole assigned after cancellation")
    poles_alt = "One cross on the negative real axis."
    mass = plane_vectors([(1.5, 0.4, "x")], "a state at which the input coefficient is checked")
    mass_alt = "One arrow from the origin into the first quadrant."

    u_hold = (0.0 - 3.0 ** 2) / 2.0
    u_fast = (-8.0 - 8.0) / 4.0
    u_sing = (-2.0 - 1.0) / 0.5
    u_out = (-3.0 - 4.5) / 1.5

    b.mc(1,
         r"For \(\dot{x} = f(x) + g(x) u\) with \(g(x) \neq 0\), the input that leaves \(\dot{x} = v\) is",
         [r"\(u = (v - f(x))/g(x)\), an identity along those trajectories",
          r"the Jacobian of \(f\) at an equilibrium, with \(u\) left unchanged",
          r"\(u = v\), ignoring \(f\) and \(g\)",
          r"\(u = f(x) g(x)\), a product instead of a quotient"], 0,
         r"Substitute and the \(f\) terms cancel, leaving \(v\), wherever \(g\) is nonzero. The Jacobian is a different, local approximation. Setting \(u = v\) leaves \(f + g v\). The product \(f g\) does not cancel \(f\).",
         fb, fb_alt)
    b.num(1,
          r"At \(x = 3\), \(f(x) = x^2\) and \(g(x) = 2\). The input that holds \(\dot{x} = 0\) is",
          u_hold, "1",
          r"\(u = (0 - 9)/2 = " + show(u_hold) + r"\). The sign error \((0+9)/2 = 4.5\) adds \(f\) instead of cancelling it. Dividing by \(x\) instead of by \(g\) gives \(-3\). Reporting \(f = 9\) reports the drift, not the input.",
          mass, mass_alt)
    b.num(1,
          r"\(f(x) = 8\), \(g(x) = 4\), and the new input is \(v = -8\). The cancelling command is",
          u_fast, "1",
          r"\(u = (-8 - 8)/4 = " + show(u_fast) + r"\). Cancelling only \(f\) and ignoring \(v\) gives \(-2\). Using \(v - f\) without dividing gives \(-16\). The positive quotient \(4\) adds the two terms before dividing.",
          step, step_alt)

    b.sym(2,
          r"Write the scalar input that turns \(\dot{x} = f + g u\) into \(\dot{x} = v\), in the names \(v\), \(f\), and \(g\).",
          "(v-f)/g", {"v": (-3.0, 3.0), "f": (-2.0, 3.0), "g": (0.4, 3.0)},
          r"Solving \(f + g u = v\) for \(u\) gives \((v - f)/g\). The form \((v + f)/g\) doubles the drift instead of removing it. The form \(v - f\) forgets to divide by the input coefficient. The form \(v/g\) leaves \(f\) in the dynamics.",
          alternates=["(v-f)*g**(-1)", "v/g-f/g"],
          fig=fb, alt=fb_alt)
    b.num(2,
          r"At a state where \(f = 1\) and \(g = 0.5\), the new input is \(v = -2\). The command is",
          u_sing, "1",
          r"\(u = (-2 - 1)/0.5 = " + show(u_sing) + r"\). Dividing by \(1\) instead of by \(g\) gives \(-3\). The sign error \((-2+1)/0.5 = -2\) does not cancel \(f\). Reporting \(g = 0.5\) reports the coefficient that must stay nonzero, not the command.",
          mass, mass_alt)
    b.order(2,
            r"Put these steps in the order you would linearize a scalar plant by feedback.",
            ["Write the dynamics as f of x plus g of x times u.",
             "Check that g of x is nonzero on the region you will use.",
             "Choose u so that f plus g u equals the new input v.",
             "Design v as a linear state feedback.",
             "Confirm that the closed loop is that linear system on the region where g stayed nonzero."],
            r"You cannot cancel a vector field you have not written down. The division is illegal where \(g\) vanishes, so that check precedes the formula. The outer gain is designed on the linear system you just built, and the last check is where that identity holds. Designing \(v\) before the cancellation has no linear plant to place.",
            poles, poles_alt)

    b.find_error(3,
                 r"A scalar plant is being rewritten by an input map. One step is wrong.",
                 [r"The law \(u = (v - f(x))/g(x)\) is an identity wherever \(g(x)\) is nonzero.",
                  r"After that substitution the system is \(\dot{x} = v\), not a remainder term.",
                  "This is the Jacobian linearization, so it is valid only in a small ball around one equilibrium.",
                  r"The outer choice \(v = -k x\) then places the pole of that linear system."],
                 2,
                 r"The Jacobian is a first-order approximation at one point. The cancellation is an equality along trajectories, including far from any chosen equilibrium, until \(g\) hits zero. The other steps are that identity and the linear design that sits on top of it.",
                 reasons=["The Jacobian is a local approximation. This cancellation is an identity wherever g is nonzero, not a small-ball model.",
                          "Feedback linearization is valid only at the equilibrium where f is zero.",
                          "The outer gain v is not allowed to be linear."],
                 correct_reason=0,
                 fig=poles, alt=poles_alt)
    b.mc(3,
         r"The cancellation formula is undefined when",
         [r"\(f(x)\) is larger than \(1\)",
          r"\(g(x) = 0\)",
          "the outer gain is negative",
          r"\(v\) is chosen as \(-kx\)"], 1,
         r"The formula divides by \(g(x)\). A large drift is legal and is exactly what gets cancelled. A negative outer gain is an ordinary stable choice. Setting \(v = -kx\) is the linear design, not a singularity.",
         mass, mass_alt)
    b.multi(3,
            r"Which statements hold for \(u = (v - f(x))/g(x)\)?",
            [r"The cancellation is exact on the set where \(g(x)\) is nonzero.",
             r"The outer loop can be an ordinary linear state feedback in \(v\).",
             r"The construction only replaces \(f\) by its Jacobian.",
             r"A zero of \(g\) can be ignored by skipping the division."],
            [0, 1],
            r"Exactness is the point of the identity, and the outer design is linear by construction. The Jacobian is the other skill. A zero of \(g\) is where this law stops, not a point you skip.",
            fb, fb_alt)

    b.num(4,
          r"At \(x = 1.5\), \(f(x) = 4.5\) and \(g(x) = 1.5\). The command that enforces \(\dot{x} = -2x\) is",
          u_out, "1",
          r"The target derivative is \(-2 \times 1.5 = -3\), so \(u = (-3 - 4.5)/1.5 = " + show(u_out) + r"\). Using \(v = -2\) instead of \(v = -2x\) gives \((-2-4.5)/1.5 = -4.333\). Cancelling \(f\) only, with \(v = 0\), gives \(-3\). Reporting \(g = 1.5\) reports the coefficient.",
          step, step_alt, ["gain-scheduling"])
    b.mc(4,
         r"\(g(x)\) changes sign across the region you care about, so one cancellation law cannot cover it. A practical substitute is",
         [r"the Jacobian at a single equilibrium, used globally",
          r"setting \(g\) to \(1\) everywhere",
          "several linear designs, interpolated from a measured operating condition",
          r"deleting \(f\) from the model"], 2,
         r"Where the cancellation is singular or changes character, designers often fall back on linear models at several points and blend the gains with a measurement. One Jacobian is local. Setting \(g = 1\) or deleting \(f\) invents a different plant.",
         fb, fb_alt, ["gain-scheduling"])
    b.mc(4,
         r"The cancelling command demanded by the formula lies past the actuator limit. The design that can refuse that command is",
         [r"a larger outer gain, which reduces the required input",
          r"the Jacobian, which never asks for a large input",
          r"ignoring \(g(x)\) in the formula",
          "a finite-horizon problem whose constraints include the actuator limit"], 3,
         r"A larger outer gain usually asks for more input, not less. The Jacobian is an approximation and does not enforce a limit. Dropping \(g\) destroys the cancellation. A constrained horizon can mark the illegal inputs as infeasible and pick a legal one.",
         step, step_alt, ["mpc"])
    b.save()


# ---------------------------------------------------------------------------
# gain scheduling
# ---------------------------------------------------------------------------

def bank_schedule():
    b = Bank("gain-scheduling")
    fb = loop(["P"], "a gain that depends on a measured schedule", fb="K(rho)")
    fb_alt = "A plant block with a gain returned and subtracted."
    curve = step_response("a response at one frozen operating point", tau=1.1, goal=1.0)
    curve_alt = "A curve rising toward a steady level."
    mat = matrix_fig([["K0", "K1"]], "two designed gains to interpolate")
    mat_alt = "A row of two gain labels."
    pts = plane_vectors([(0, 2, "a"), (1, 8, "b")], "two designed gains at the ends of a schedule")
    pts_alt = "Two arrows of different lengths, both in the first quadrant."

    k_mid = 2.0 + (8.0 - 2.0) * (2.5 / 10.0)
    k_frac = 1.0 + (5.0 - 1.0) * ((6.0 - 4.0) / (12.0 - 4.0))
    k_s = (1.0 - 0.25) * 4.0 + 0.25 * 12.0
    k_half = 0.5 * 6.0 + 0.5 * 14.0

    b.mc(1,
         r"Gain scheduling builds",
         ["several linear controllers and interpolates them with a measured variable",
          "one parameter updated from the prediction error while the loop runs",
          "a single linearization, used at every operating point",
          r"an input that cancels \(f(x)\) exactly"], 0,
         r"The schedule is measured, and the gains were designed offline at chosen points. An online update from the prediction error is adaptation. One linearization is one controller. Exact cancellation is feedback linearization, which this table does not perform.",
         fb, fb_alt)
    b.num(1,
          r"The gain is \(2\) at schedule value \(0\) and \(8\) at schedule value \(10\). Linear interpolation at schedule value \(2.5\) gives",
          k_mid, "1",
          r"The fraction of the way from \(0\) to \(10\) is \(0.25\), so the gain is \(2 + 0.25 \times 6 = " + show(k_mid) + r"\). The average of the endpoints is \(5\), which would be the value at \(5\), not at \(2.5\). Reporting \(8\) jumps to the far design. Reporting \(2.5\) reports the schedule value.",
          pts, pts_alt)
    b.num(1,
          r"The gain is \(1\) at schedule value \(4\) and \(5\) at schedule value \(12\). At schedule value \(6\) the interpolated gain is",
          k_frac, "1",
          r"The fraction is \((6-4)/(12-4) = 0.25\), so the gain is \(1 + 0.25 \times 4 = " + show(k_frac) + r"\). Using the schedule value \(6\) as a fraction of \(12\) gives \(1 + 0.5 \times 4 = 3\). The midpoint of the gains is \(3\), which sits at schedule value \(8\). Reporting \(5\) uses the far design.",
          mat, mat_alt)

    b.sym(2,
          r"A weight \(s\) between \(0\) and \(1\) blends gains \(a\) and \(b\). Write the blend in the names \(s\), \(a\), and \(b\).",
          "(1-s)*a+s*b", {"s": (0.05, 0.95), "a": (0.4, 4.0), "b": (0.4, 4.0)},
          r"The near gain keeps the weight \(1-s\) and the far gain keeps \(s\). The form \(s a + (1-s) b\) swaps the ends. The form \(a + b\) adds the designs. The form \(s(a+b)\) scales the sum and does not recover \(a\) at \(s = 0\).",
          alternates=["a+s*(b-a)", "s*b+(1-s)*a"],
          fig=mat, alt=mat_alt)
    b.num(2,
          r"The blend weight on the second gain is \(0.25\), the first gain is \(4\), and the second gain is \(12\). The interpolated gain is",
          k_s, "1",
          r"\((1-0.25)\times 4 + 0.25\times 12 = " + show(k_s) + r"\). Swapping the weights gives \(0.25\times 4 + 0.75\times 12 = 10\). The difference of the gains is \(8\). The second gain \(12\) is the value at weight \(1\).",
          curve, curve_alt)
    b.order(2,
            r"Put these scheduling steps in the order you would do them.",
            ["Choose operating points that cover the range of the schedule.",
             "Linearize the plant at each chosen point.",
             "Design a linear controller at each point.",
             "Name the measured variable that will select the point.",
             "Interpolate the gains from that measurement, and check a move between the points."],
            r"The points define where you are willing to design. The linear model at each point is the plant that design sees. The measured variable is what the implementation actually has, and interpolation is useless until the designs exist. The check between the points is where a frozen-parameter hope can fail, so it comes last.",
            fb, fb_alt)

    b.find_error(3,
                 r"A schedule of linear controllers has been built. One step is wrong.",
                 ["Each linear controller was designed at one operating point.",
                  "The schedule variable is measured, and the gains are interpolated from it.",
                  "If that variable moves quickly, the frozen design is still exact, because each instant has some local model.",
                  "A parameter updated from the prediction error, with no measured schedule, is a different mechanism."],
                 2,
                 r"A fast schedule makes the rate of the operating point part of the dynamics. A design that freezes the parameter misses that rate, so the interpolation is not exact at every speed. The other steps distinguish the table from an adaptive update and describe how the table is built.",
                 reasons=["A fast schedule adds the rate of the operating point. A frozen design misses that rate.",
                          "A measured schedule is updated from the prediction error.",
                          "Interpolation is exact for every speed because the points were linear."],
                 correct_reason=0,
                 fig=curve, alt=curve_alt)
    b.mc(3,
         r"The difference between this table and an adaptive update is that",
         [r"adaptation also indexes a gain by a measured temperature or speed",
          "the table uses a measurement, while adaptation moves a parameter from the prediction error",
          r"the table is recomputed from \(y - \hat{y}\) at every sample",
          "the two mechanisms are the same recursion"], 1,
         r"A schedule does not look at the prediction error. An adaptive law does, and it does not need a measured operating condition. Recomputing the table from the error would be adaptation. The recursions are different.",
         fb, fb_alt)
    b.multi(3,
            r"Which statements hold for a gain schedule?",
            ["The variable that selects the gain is measured.",
             "More than one operating point is designed for.",
             "The gains are moved by the prediction error while the loop runs.",
             "A single linearization at one equilibrium is already a schedule."],
            [0, 1],
            r"Measurement and a family of designs are the definition. The prediction error is the adaptive signal, not this one. One linearization is one controller, with nothing to interpolate.",
            mat, mat_alt)

    b.num(4,
          r"Gains \(6\) and \(14\) sit at the ends of a schedule interval, and the measurement is halfway between them. The interpolated gain is",
          k_half, "1",
          r"Halfway is weight \(1/2\) on each design: \((6+14)/2 = " + show(k_half) + r"\). The difference \(14-6 = 8\) is the gap, not the blend. Reporting \(6\) or \(14\) stays at an end. Twice the halfway value is \(20\), which is outside both designs.",
          pts, pts_alt, ["adaptive"])
    b.mc(4,
         r"The schedule measurement freezes. The controller you are running is",
         [r"still a blend that changes with the prediction error",
          r"an exact cancellation of the nonlinearity",
          "the single linear design that belongs to that frozen value",
          "undefined, because a schedule needs motion"], 2,
         r"A frozen measurement selects one column of the table. It does not start an adaptive update, and it does not cancel a nonlinearity. The design at that point remains defined when the point stops moving.",
         curve, curve_alt, ["adaptive", "mpc"])
    b.mc(4,
         r"Between the design points the frozen linear models are only a hope. A method that re-solves a constrained problem from the current state, instead of blending gains, is",
         [r"the same schedule with more points",
          r"an integrator on the schedule variable",
          r"a larger spacing between the design points",
          "a receding-horizon controller on a model you trust at the current state"], 3,
         r"More points improve a table and are still a table. An integrator on the schedule variable is not a control law for the plant. Wider spacing makes the hope worse. A horizon that starts from the measured state is a different architecture.",
         step_response("a short predicted transient", tau=0.7, goal=0.8),
         "A curve rising toward a level below the top of the axes.",
         ["mpc"])
    b.save()


def expl_gaussian():
    fig = ellipse_axes("covariance level curve of a two-component vector")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "An ellipse centered on two axes, longer along the first coordinate.",
        "body_md": r"""A Gaussian random vector is summarized by a mean and a covariance. The mean is where the cloud sits. The covariance is the expected outer product of the centered vector, so it is symmetric, its diagonal entries are variances, and a negative diagonal entry is impossible. For a Gaussian, a zero cross term is stronger than it is for a general random vector: the components are independent, not merely uncorrelated.

A fixed matrix acts on this summary in a definite way. If \(y = A x + d\), the shift \(d\) moves the mean and does nothing to the covariance. The matrix hits the covariance from both sides, because the outer product has a factor of \(x\) on each side. The image is still Gaussian.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""With \(\mu = \mathbb{E}[x]\) and \(P = \mathbb{E}[(x-\mu)(x-\mu)^T]\),
\[
\mathbb{E}[A x + d] = A\mu + d, \qquad \mathrm{Cov}(A x + d) = A P A^T.
\]
A scalar scale is the same rule: the variance of \(c z\) is \(c^2\) times the variance of \(z\). A sum of independent components adds the weighted variances and has no cross term. The trace of \(P\) is the sum of the component variances, in any coordinate, because a trace is invariant under a cyclic swap and the diagonal is what you read off after you have formed \(A P A^T\).""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take a zero-mean scalar whose variance is \(0.4\), and form \(1.7\) times it. The variance of the product is \(1.7^2 \times 0.4 = 1.156\). Shifting the result by \(0.9\) leaves \(1.156\) alone and moves the mean to \(0.9\). The same arithmetic in two dimensions is the congruence: a diagonal \(P\) is stretched by the squares of the row entries of \(A\), and a nonzero off-diagonal of \(A\) mixes the two original variances into both new ones.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The scale factor is squared. Using it once is the rule for the mean, not for the covariance. Dropping the transpose in \(A P A^T\) is the same mistake in matrix form, and it is still a mistake when \(A\) is square. A constant is not noise: its outer product does not get added to \(P\). And a zero cross term means independence only in the Gaussian case. Outside that family it means the linear correlation is zero, which is a weaker sentence.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""A linear predictor multiplies a covariance by \(A\) on the left and by \(A^T\) on the right, then adds the covariance of whatever noise entered the step. That is the predict half of a recursive filter. The update half will shrink the same matrix when a measurement arrives. Both steps are the identity on this page, applied to a running estimate of \(P\) rather than to a single random draw.""",
    }]
    return put_explainer("gaussian-random-vectors", "Gaussian random vectors", sections)


def expl_kalman():
    fig = loop(["model"], "predict, then a correction from the innovation", fb="L", inp="u", out="xhat")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A model block with a gain returned and subtracted.",
        "body_md": r"""The filter keeps two objects: an estimate of the state, and a covariance that says how large the error is likely to be. The model is
\[
x_{k+1} = A x_k + w_k, \qquad y_k = C x_k + v_k,
\]
with \(w_k\) and \(v_k\) independent of each other and of the past, and with covariances \(Q\) and \(R\).

Predict pushes the estimate through \(A\) and the covariance through the congruence \(A P A^T\), then adds \(Q\). Update looks at the innovation, the measurement minus the output the estimate expected, and mixes that innovation in with a gain built from the predicted covariance and from \(R\). A known command is added in the predict and does not touch the covariance, because a known shift is not noise.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""Write \(P^-\) for the predicted covariance and \(\hat{x}^-\) for the predicted estimate. Then
\[
\hat{x}^- = A\hat{x}, \qquad P^- = A P A^T + Q,
\]
\[
L = P^- C^T (C P^- C^T + R)^{-1},
\]
\[
\hat{x} = \hat{x}^- + L(y - C\hat{x}^-), \qquad P = (I - L C) P^-.
\]
The last product is the simplified covariance update, and it matches the longer form \((I-LC)P^-(I-LC)^T + L R L^T\) when \(L\) is this gain. In the scalar case with \(c = 1\), the gain is \(P^-/(P^- + R)\), which falls toward \(0\) as \(R\) grows and rises toward \(1\) as \(R\) shrinks.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take a scalar coefficient \(0.8\), a previous variance \(1.25\), and a process variance \(0.07\). The predicted variance is \(0.8^2 \times 1.25 + 0.07 = 0.87\). A measurement variance of \(0.87\) on top of that prediction would cut the gain to one half, and the simplified update would leave a posterior variance of half of \(0.87\). The arithmetic is the same when the numbers are matrices: the congruence first, the process covariance second, the gain third.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The predict step does not see the new measurement. Subtracting \(y\) before \(A\) is applied uses the innovation against the wrong prediction. Adding \(Q\) in the update instead of in the predict moves the process noise to the wrong side of the gain. Correcting with the raw measurement, rather than with the innovation, credits the filter for a part of \(y\) it had already expected. And the simplified product \((I-LC)P^-\) is not the error covariance of an arbitrary gain. It belongs to this \(L\).""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""Nothing on this page proves that the gain is the minimum-variance linear correction. That reading is a separate argument, by differentiating the updated variance or by a projection. A different later argument builds the same algebra as a recursive least-squares fit on successive blocks. Both of those start from the recursion written here. They do not replace the order of the steps.""",
    }]
    return put_explainer("kalman", "Kalman filter", sections)


def expl_optimal():
    fig = filled_ellipse_fig("error cloud that a linear correction is about to shrink")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A shaded ellipse centered at the origin of two axes.",
        "body_md": r"""The filter gain is not an arbitrary stable observer gain. Among corrections that add a matrix times the innovation, it is the one with the smallest updated error variance. A pole-placed gain can decay quickly and still leave a larger cloud, because decay and variance answer different questions.

The structure that receives the gain is the observer you already know: a copy of the model, plus a correction from the output residual. This skill only changes how the correction is chosen. The intensities \(Q\) and \(R\) replace the hand-written polynomial.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""For a scalar predicted variance \(p\), output coefficient \(c\), and measurement variance \(r\), a trial gain \(L\) leaves the updated variance
\[
(1 - L c)^2 p + L^2 r.
\]
The derivative in \(L\) vanishes at
\[
L = \frac{p c}{c^2 p + r},
\]
and the minimum value equals \((1 - L c) p\). That equality is special to the minimizing gain. A hand-picked gain has to be scored with the two-term expression, or the comparison is dishonest.

In steady state the predicted variance stops moving. The gain freezes, and the copy of the model with that frozen gain is an observer.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take a predicted variance \(2.25\) and a measurement variance \(0.75\), with \(c = 1\). The minimizing gain is \(2.25 / (2.25 + 0.75) = 0.75\). The updated variance is \((1 - 0.75) \times 2.25 = 0.5625\). A guess of \(0.3\) has to be scored as \((1-0.3)^2 \times 2.25 + 0.3^2 \times 0.75\), which is larger. The gap is the whole point of the derivative condition: a nearby gain is legal and worse.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""Stability of \(A - L C\) does not freeze the variance. Every stable gain has its own cloud. Using the simplified product \((1-Lc)p\) on a gain that did not come from the formula understates that gain's variance, because the simplified product has already used the optimality condition to cancel a term. Swapping the names \(Q\) and \(R\) with the weights of a quadratic regulator produces a similar-looking equation and a different gain. The regulator penalizes the command. This design describes the noise.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""The gain from this page can be placed next to a state-feedback gain that was chosen for the regulator poles or for a quadratic cost. The two gains do not have to be equal. A later combined command uses both, and a constraint on the actuator is a different problem again: a variance formula will not enforce a hard bound. A horizon that carries the bound explicitly is the design that does.""",
    }]
    return put_explainer("kalman-optimal-observer", "Kalman filter as an optimal observer", sections)


def expl_separation():
    fig = matrix_fig([["A-BK", "0"], ["*", "A-LC"]], "block-triangular joint matrix")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A block matrix with two diagonal blocks and a zero in the upper right.",
        "body_md": r"""Output feedback through an estimate uses the control law \(u = -K\hat{x}\), while a copy of the model produces \(\hat{x}\) from the applied command and the measured output. When that copy uses the same \(A\), \(B\), and \(C\) as the plant, the joint system is block triangular in the coordinates \((x, x-\hat{x})\).

One diagonal block is \(A - BK\). The other is \(A - LC\). The eigenvalues are the union of the two sets, so each gain can be designed as if the other did not exist. That is the split. It is a statement about eigenvalues, not a statement that every signal in the loop shows both sets.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""With a matching model and \(u = -K\hat{x}\),
\[
\frac{d}{dt}\begin{bmatrix} x \\ \tilde{x} \end{bmatrix}
=
\begin{bmatrix} A-BK & BK \\ 0 & A-LC \end{bmatrix}
\begin{bmatrix} x \\ \tilde{x} \end{bmatrix}
\]
plus a reference term that enters the first block only, when the reference is added the same way in the plant and in the copy. The characteristic polynomial is \(\det(sI - (A-BK))\) times \(\det(sI - (A-LC))\). A scalar plant makes the two eigenvalues \(a - b k\) and \(a - l c\).""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Place a regulator eigenvalue at \(-1.15\) and an observer eigenvalue at \(-3.55\). The joint characteristic polynomial is \((s+1.15)(s+3.55)\). The sum of the real parts is \(-1.15-3.55 = -4.70\), which is just the sum of the two numbers you placed. Nothing in that arithmetic asks the two marks to sit on top of each other. A second design that moved only the observer mark would change one factor and leave the regulator factor where it was.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The transfer function from the reference to the output, started from a zero estimation error, does not contain the observer poles. They cancel. A nonzero initial estimation error does show them in the output, because the error drives the state through \(BK\). Saying that the observer poles "appear in the step response" without saying which initial condition is the usual mix-up.

The split also fails quietly when the observer is built from a different \(A\) or \(C\). The error equation then has a driving term, and the characteristic polynomial does not factor into the two designs you wrote down.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""The two gains fix the transient. A constant reference still needs a coefficient in front of it if the steady output is supposed to equal that reference. Adding that coefficient, and leaving the estimate in the command, is the two-degree-of-freedom structure. The eigenvalues you placed here do not move when that coefficient changes, because it enters as an input rather than as a change to \(K\) or \(L\).""",
    }]
    return put_explainer("separation", "Output feedback and the separation principle", sections)


def expl_gen():
    fig = parallel_sum(["F", "K"], "reference term and estimate term", output_label="u")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "Two blocks side by side whose outputs add to form a command.",
        "body_md": r"""A combined command has two jobs that a single gain does poorly. One job is the response to the reference. The other is the response to disturbances and to a wrong initial estimate. The structure that separates them is
\[
u = F r - K \hat{x}.
\]
\(K\) and the observer gain are the feedback design. \(F\) is a feedforward scale from the reference. Changing \(F\) does not move \(A-BK\) or \(A-LC\), because \(F r\) enters as an input.

The observer has to be driven by the command that is actually applied. A copy that sees a different input accumulates a false residual.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""For a scalar plant \(\dot{x} = a x + b u\), \(y = x\), and \(u = F r - K x\) in steady state with \(x = r\),
\[
0 = a + b F - b K, \qquad F = K - a/b.
\]
The same \(F\) is used with an estimate in place of \(x\) once the observer is running. The homogeneous eigenvalues stay at \(a - b K\) and at \(a - l c\). \(F\) is absent from both.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(F = 1.15\), a reference \(2.4\), a gain \(0.35\), and an estimate \(1.6\). The command is \(1.15 \times 2.4 - 0.35 \times 1.6 = 2.76 - 0.56 = 2.2\). Dropping the estimate would have applied \(2.76\), which is the feedforward piece alone and is not the command this structure defines. The estimate term is small here because the estimate is moderate and the gain on it is moderate. It is still the term that rejects a disturbance \(F\) does not know about.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""Setting the observer gain to zero once \(F\) exists leaves the estimate at its open prediction. The reference path does not estimate the state, and it does not see a load that was absent from the steady-state solve. Driving the observer with \(r\) instead of with \(u\) inserts a different input into the copy than into the plant, and the error equation is no longer homogeneous. Forcing \(F\) and \(K\) to be the same number throws away the freedom the structure was built to provide.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""If a constant load remains after \(F\) was computed from the unloaded model, an integrator of the tracking error grows until the offset is gone, provided the augmented loop is stable. If the command has to respect a hard limit, a horizon can refuse the illegal values that \(F r - K\hat{x}\) would otherwise request. Neither addition moves the fact that \(F\) and \(K\) are different coefficients.""",
    }]
    return put_explainer("gen-controller", "General controller structure", sections)


def expl_integral():
    fig = loop(["P"], "an integrator beside the state feedback", fb="ki", inp="r", out="y")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A plant block with a gain returned and subtracted from a reference.",
        "body_md": r"""A constant reference scale can set the steady output for one known load. A load the model did not include shifts that steady value, and a fixed scale has no state left to notice. Integral action adds a state whose derivative is the tracking error. In any steady state that derivative is zero, so the output equals the reference. Stability of the augmented loop is what makes the trajectory arrive at that steady state. An unstable augmented loop winds and does not settle.

The new state is estimated or measured like any other state, and the gain vector grows by one entry.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""With \(\dot{\xi} = r - y\) and \(y = x\) for a scalar plant \(\dot{x} = a x + b u\),
\[
u = -k x + k_i \xi.
\]
The closed-loop polynomial is
\[
s^2 + (b k - a) s + b k_i.
\]
The coefficient of \(s\) fixes \(k\). The constant term fixes \(k_i\). The sign in front of \(k_i\) is the one that makes a positive accumulated error raise the command on a plant with \(b > 0\). The augmented pair still has to be reachable, or those two coefficients cannot be assigned independently.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(a = 0.4\), \(b = 1.25\), and ask for the polynomial \(s^2 + 3.4 s + 1.875\). The coefficient of \(s\) says \(1.25 k - 0.4 = 3.4\), so \(1.25 k = 3.8\) and \(k = 3.04\). The constant term says \(1.25 k_i = 1.875\), so \(k_i = 1.5\). Forgetting the open-loop \(0.4\) would divide \(3.4\) by \(1.25\) and report a gain that is short by \(0.4/1.25\).""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The constant term belongs to \(k_i\), and the coefficient of \(s\) belongs to \(k\). Swapping them places the wrong polynomial. The input coefficient \(b\) scales both gains. Leaving it out reports a gap in the polynomial as if it were already a gain. A positive \(k_i\) with the integrator written as \(\dot{\xi} = y - r\) flips the feedback and pushes a positive error the wrong way. And the linear gain does not know about an actuator stop: once the command saturates, the integrator keeps winding unless something extra clamps it.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""The same augmented matrices can be handed to a quadratic cost. The gain that comes back still has an entry for \(\xi\), chosen by a Riccati equation instead of by a named polynomial. A hard limit on the command is still outside that cost. A horizon that carries the limit as a constraint is the design that can refuse the request the integrator would otherwise keep making.""",
    }]
    return put_explainer("integral-action", "Integral action in state feedback", sections)


def expl_lqr():
    fig = loop(["P"], "constant gain from a quadratic cost", fb="K")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A plant block with a gain returned and subtracted.",
        "body_md": r"""Pole placement asks you to name the closed-loop polynomial. A quadratic regulator asks you to name a cost, and it returns the gain that minimizes that cost. The infinite-horizon cost with constant weights produces a constant gain. There is one algebraic equation to solve, not a new gain at each time.

The state weight says which directions are expensive to leave large. The control weight says which commands are expensive to use. A larger control weight buys a smaller gain. A larger state weight buys a more aggressive one. Neither weight is a hard limit.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""The cost is \(\int_0^{\infty} (x^T Q x + u^T R u)\, dt\), and the gain is \(K = R^{-1} B^T P\), where \(P\) solves
\[
A^T P + P A - P B R^{-1} B^T P + Q = 0.
\]
For the scalar integrator \(\dot{x} = u\) this collapses to \(K = \sqrt{q/r}\). For \(\dot{x} = a x + b u\) the scalar equation is a quadratic in \(P\), and the positive root is the one that stabilizes \(a - b K\) when the weights are positive and the pair is reachable. The negative root is not a cost matrix.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""For \(\dot{x} = u\) with state weight \(1.69\) and control weight \(0.25\), the gain is \(\sqrt{1.69/0.25} = \sqrt{6.76} = 2.6\). The Riccati solution itself is \(\sqrt{1.69 \times 0.25} = 0.65\), and dividing by the control weight recovers \(0.65/0.25 = 2.6\). Reporting \(0.65\) reports \(P\). Reporting \(6.76\) reports the ratio inside the square root, before the root is taken.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The comparative static on \(R\) runs backward if you think of a larger weight as permission to use more command. It is a penalty. The Riccati equation is not the Lyapunov equation: it carries the extra term that contains the gain, and deleting that term answers a stability question you were not asked. On a scalar plant it is also easy to return \(P\) when the question asked for \(K\), or to keep the negative root because it satisfies the same quadratic.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""A hard bound on the command is not a large \(R\). The weight still allows every real number, and it only makes the large ones expensive. A finite horizon with the bound written as a constraint is the design that can mark those commands illegal. The same cost can also be written on a state that has already been augmented with an integrator. The gain then has one more entry, and the algebra is unchanged.""",
    }]
    return put_explainer("lqr", "Linear quadratic regulator", sections)


def expl_mpc():
    fig = step_response("a prediction that stops at the horizon", tau=0.9, goal=1.0, t_end=3.2)
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A curve that rises and is cut off at a finite time.",
        "body_md": r"""A predictive controller writes a finite-horizon problem at the current state, solves it, and applies only the first input. At the next sample it throws the rest of the sequence away and starts again from the new state. That last habit is what makes the method closed loop. Applying the whole sequence would be an open-loop plan that never looks at another measurement.

The horizon can carry constraints. A bound on the command is a constraint, not a weight. The quadratic regulator is the different limit: infinite horizon, no constraint, and one constant gain.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""A one-step scalar illustration minimizes \((x+u)^2 + \rho u^2\). The derivative in \(u\) vanishes at
\[
u = -\frac{x}{1+\rho}.
\]
If the command must also lie in an interval, and the cost is convex, the constrained minimizer is that unconstrained value clipped to the interval. A longer horizon replaces this one square by a sum of predicted stage costs, with the model rolling the state forward, and the same rule applies to the implementation: keep the first input only.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(x = 5.61\) and \(\rho = 0.6\), with no constraint. The command is \(-5.61 / 1.6 = -3.50625\). A bound \(|u| \le 2.8\) would clip that command to \(-2.8\), because \(3.50625\) sits past the stop. The unconstrained number and the clipped number are different questions. Reporting \(5.61\) reports the state.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""The sign of the one-step command is negative when \(x\) is positive and the predicted state is \(x+u\): you are pulling the state back. Clipping to the positive end of a symmetric interval doubles the error. Dividing by \(\rho\) alone drops the \(1\) that came from the state penalty. And a longer horizon is not free: the first input can change, because the plan now feels costs and constraints that used to sit past the end of the window.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""If the model is only trustworthy near one operating condition, a table of linear controllers indexed by a measurement is a different architecture from one horizon on a single model. If the cost is quadratic, the horizon infinite, and the constraints absent, the first input collapses to the constant regulator gain. Knowing which of those limits you are in is how you decide whether the extra optimization at each sample is doing any work.""",
    }]
    return put_explainer("mpc", "Model predictive control", sections)


def expl_fb_lin():
    fig = step_response("linear closed loop after an exact cancellation", tau=0.55, goal=1.0)
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "A smooth curve rising toward a steady level.",
        "body_md": r"""Feedback linearization rewrites a control-affine plant by an input map. For \(\dot{x} = f(x) + g(x) u\) with \(g(x) \neq 0\), the choice
\[
u = (v - f(x))/g(x)
\]
is an identity: after the substitution, \(\dot{x} = v\) exactly, including far from any equilibrium. It is not the Jacobian. The Jacobian approximates \(f\) near one resting point and leaves a remainder. This cancellation has no remainder on the set where \(g\) stays away from zero.

The new input \(v\) is then designed as an ordinary linear state feedback. The poles you assign are the poles of that exact linear system.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""Solving \(f + g u = v\) for the command gives the display above. With \(v = -k x\) the closed loop is \(\dot{x} = -k x\), so the pole sits at \(-k\), wherever the cancellation was valid. The formula divides by \(g(x)\). A root of \(g\) is not a point you skip. It is a point where this particular law stops being defined, even if the original differential equation is perfectly regular there.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Take \(f = 0.65\), \(g = 0.4\), and a requested derivative \(v = -0.3\). The command is \((-0.3 - 0.65)/0.4 = -0.95/0.4 = -2.375\). Adding \(f\) instead of subtracting it would flip the drift and produce a positive command of the same size. Forgetting to divide by \(0.4\) would report \(-0.95\), which is a derivative gap, not a command. The coefficient \(0.4\) has to stay nonzero for the division to mean anything.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""Calling this construction a Jacobian linearization imports the small-ball warning that belongs to the other skill and hides the exact identity. The opposite mistake is to trust the identity on a region where \(g\) changes sign or hits zero. A large outer gain does not shrink the required command. It usually increases the \(v\) you are asking the cancellation to produce, and the actuator may be unable to supply the result. Setting \(g\) to \(1\) by hand invents a plant you do not have.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""Where a single cancellation cannot cover the region, a family of linear designs at chosen operating points can be interpolated from a measured schedule. Where the cancelling command would violate an actuator limit, a finite-horizon problem can mark that command illegal and pick a feasible one. Both of those are different architectures. They start from the admission that the identity on this page has a boundary.""",
    }]
    return put_explainer("fb-linearization", "Feedback linearization", sections)


def expl_schedule():
    fig = plane_vectors([(0.2, 1.4, "a"), (1.0, 3.9, "b")], "two gains at the ends of a schedule")
    sections = [{
        "heading": "The idea",
        "figure_svg": fig,
        "figure_alt": "Two arrows of different lengths in the first quadrant.",
        "body_md": r"""Gain scheduling designs a linear controller at each of several operating points, then interpolates the gains with a variable you measure. The measurement might be a speed, a temperature, or a position. It is not the prediction error. An adaptive law moves a parameter from that error and does not need a measured schedule. A single linearization is one controller, with nothing to blend.

The designs are computed offline. At run time the only arithmetic is the blend, plus the linear controller the blend selected.""",
    }, {
        "heading": "Key equations",
        "body_md": r"""On an interval between two designs \(a\) and \(b\), a weight \(s\) between \(0\) and \(1\) gives
\[
K = (1-s) a + s b = a + s(b-a).
\]
At \(s = 0\) this is the first design. At \(s = 1\) it is the second. Halfway is the average. The weight is the fraction of the way along the measured schedule, not the schedule value itself and not the prediction error.""",
    }, {
        "heading": "Worked example",
        "body_md": r"""Blend weight \(0.3\) on the second gain, with endpoint gains \(1.4\) and \(3.9\). The result is \(0.7 \times 1.4 + 0.3 \times 3.9 = 0.98 + 1.17 = 2.15\). Swapping the weights would put \(0.3\) on \(1.4\) and \(0.7\) on \(3.9\), which is the blend at weight \(0.7\) and is a different point on the same segment. The gap \(3.9 - 1.4 = 2.5\) is the length of the segment, not the value at this weight.""",
    }, {
        "heading": "Common pitfalls",
        "body_md": r"""A frozen-parameter design misses the rate of the schedule. If the measured variable moves quickly, each instant still has a local model, and that fact does not make the interpolation exact: the derivative of the operating point is part of the dynamics and was never in the frozen linearizations. Using the schedule value as if it were already a weight between \(0\) and \(1\) blends the wrong pair. And updating the table from \(y - \hat{y}\) is adaptation, even if someone still calls the result a schedule.""",
    }, {
        "heading": "Where this leads",
        "body_md": r"""If the operating condition is not measured, the online update from the prediction error is the mechanism that remains. If the difficulty is a hard constraint rather than a moving linear model, a receding horizon on a model you trust at the current state replaces the blend by a fresh optimization. Checking a trajectory that travels between the design points is how you find out which of those you actually needed.""",
    }]
    return put_explainer("gain-scheduling", "Gain scheduling", sections)


def lint():
    banned = re.compile(
        r"niknejad|åström|aström|astrom|murray|feedback systems|ziegler|nichols|\breader\b|§|"
        r"\b(university|professor|textbook|syllabus|berkeley)\b",
        re.I,
    )
    skills = [
        "fb-linearization", "gain-scheduling", "gen-controller", "integral-action",
        "gaussian-random-vectors", "kalman", "kalman-optimal-observer", "lqr", "mpc", "separation",
    ]
    problems = []
    for sid in skills:
        bank = json.load(open(os.path.join(BANK, f"{sid}.json"), encoding="utf-8"))
        exp = json.load(open(os.path.join(EXP, f"{sid}.json"), encoding="utf-8"))
        nfig = 0
        idxs = []
        deep = 0
        for q in bank["questions"]:
            blob = json.dumps(q, ensure_ascii=False)
            if banned.search(blob):
                problems.append(f"{q['id']} banned wording")
            if q.get("figure"):
                nfig += 1
            if q["type"] == "mc":
                idxs.append(q["correct_index"])
            if q["type"] in ("symbolic", "order", "error", "multi"):
                deep += 1
        if nfig < 9:
            problems.append(f"{sid} only {nfig} figures")
        if deep < 3:
            problems.append(f"{sid} deep {deep}")
        if len(idxs) % 4 == 0 and idxs:
            counts = Counter(idxs)
            if len(counts) != 4 or len(set(counts.values())) != 1:
                problems.append(f"{sid} MC positions {dict(counts)}")
        wc = words(exp["sections"])
        if not (250 <= wc <= 500):
            problems.append(f"{sid} explainer words {wc}")
        blob = json.dumps(exp, ensure_ascii=False)
        if banned.search(re.sub(r"<svg[\s\S]*?</svg>", "", blob)):
            problems.append(f"{sid} explainer banned wording")
        print(f"{sid}: questions {len(bank['questions'])}, figures {nfig}, deep {deep}, MC idx {idxs}, explainer words {wc}")
    if problems:
        print("LINT FAIL")
        for item in problems:
            print(" ", item)
        sys.exit(1)
    print("lint ok")


def main():
    bank_gaussian()
    bank_kalman()
    bank_optimal()
    bank_separation()
    bank_gen()
    bank_integral()
    bank_lqr()
    bank_mpc()
    bank_fb_lin()
    bank_schedule()
    print(
        "words",
        expl_gaussian(),
        expl_kalman(),
        expl_optimal(),
        expl_separation(),
        expl_gen(),
        expl_integral(),
        expl_lqr(),
        expl_mpc(),
        expl_fb_lin(),
        expl_schedule(),
    )
    lint()


if __name__ == "__main__":
    main()
