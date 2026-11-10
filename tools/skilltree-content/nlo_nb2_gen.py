#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB2 banks and explainers.

Skills: induced-matrix-norms, frobenius-schatten-norms, open-closed-sets,
compact-sets, level-sets-contours, convex-sets.

Closed-form answers live here. skilltree/verify_nlo_nb2.py recomputes the
numeric ones and does not import this file. Symbolic keys are checked by
the shared harness.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import DEEP_TYPES, Bank, deep_quota, save_explainer
from templates import (
    dented_quad_fig, disk_fig, filled_ellipse_fig, halfspace_fig, level_curves_fig,
    matrix_fig, norm_balls, orthant_fig, segment_fig, two_disks_fig,
)

DISK = disk_fig("disk centered at the origin")
DISKS = two_disks_fig("two separate disks")
LEVELS = level_curves_fig("nested ellipses")
ELL = filled_ellipse_fig("shaded elliptical disk")
DENT = dented_quad_fig("quadrilateral with a pushed-in corner")
HALF = halfspace_fig("line with one side shaded")
SEG = segment_fig("segment lying on a dashed line")
BALLS = norm_balls("nested unit balls")
ORTH = orthant_fig("shaded first quadrant")

A_DISK = "A filled disk centered at the origin."
A_DISKS = "Two filled disks with a gap between them."
A_LEVELS = "Three nested ellipses centered at the origin."
A_ELL = "A shaded ellipse, longer along the first axis."
A_DENT = "A four-sided region with one corner pushed inward."
A_HALF = "A straight boundary, with one side of the plane shaded."
A_SEG = "A solid segment lies on a longer dashed line."
A_BALLS = "A diamond inside a disk inside a square, centered at the origin."
A_ORTH = "The closed first quadrant is shaded."

M14 = matrix_fig([["1", "-4"], ["2", "3"]], "2 by 2 matrix")
A_M14 = "A 2 by 2 matrix with first row 1, -4 and second row 2, 3."
M35 = matrix_fig([["3", "0"], ["0", "-5"]], "diagonal matrix")
A_M35 = "A diagonal 2 by 2 matrix with diagonal entries 3 and -5."
M06 = matrix_fig([["0", "-6"], ["0", "0"]], "matrix with a single nonzero entry")
A_M06 = "A 2 by 2 matrix with a single nonzero entry."
MONES = matrix_fig([["1", "1"], ["1", "1"]], "matrix of ones")
A_ONES = "A 2 by 2 matrix with every entry equal to 1."
M47 = matrix_fig([["4", "0"], ["0", "7"]], "positive diagonal matrix")
A_M47 = "A diagonal 2 by 2 matrix with positive diagonal entries."
MSYM = matrix_fig([["a", "-a"], ["2a", "0"]], "matrix depending on a parameter")
A_SYM = "A 2 by 2 matrix whose entries are written in a parameter a."
M34 = matrix_fig([["3", "0"], ["0", "-4"]], "diagonal matrix with mixed signs")
A_M34 = "A diagonal 2 by 2 matrix. One diagonal entry is negative."
M512 = matrix_fig([["0", "5"], ["12", "0"]], "off-diagonal matrix")
A_M512 = "A 2 by 2 matrix whose nonzero entries sit off the diagonal."
MAB = matrix_fig([["a", "b"], ["0", "0"]], "matrix with a zero row")
A_MAB = "A 2 by 2 matrix whose second row is zero."


def bank_induced():
    b = Bank("induced-matrix-norms")
    b.mc(1,
         r"The matrix norm induced by a vector norm is",
         [r"the largest value of \(\lVert Ax \rVert\) on the vectors with \(\lVert x \rVert = 1\)",
          "the sum of the absolute values of the entries",
          "the product of the singular values",
          "the largest diagonal entry"],
         0,
         r"The induced norm is the operator norm: the greatest stretch of a unit vector, which is also \(\sup_{x \ne 0} \lVert Ax \rVert / \lVert x \rVert\). Adding every absolute entry is not that maximum, and neither is a product of singular values. A diagonal entry is one stretch only when the matching basis vector is a maximizer.",
         M47, A_M47)
    b.num(1,
          r"What is the induced 1-norm of \(A = \begin{bmatrix} 1 & -4 \\ 2 & 3 \end{bmatrix}\)?",
          7, "1",
          r"Absolute column sums are \(\lvert 1 \rvert + \lvert 2 \rvert = 3\) and \(\lvert -4 \rvert + \lvert 3 \rvert = 7\). The induced 1-norm is the larger one, 7. The row sums are both 5, so 5 is the infinity-norm. The trace 4 and the largest entry 4 are not column sums.",
          M14, A_M14)
    b.mc(1,
         r"The infinity-norm induced by the vector infinity-norm equals",
         ["the maximum absolute column sum",
          "the maximum absolute row sum",
          "the Frobenius norm",
          "the largest singular value"],
         1,
         r"Rows are what the infinity-norm inspects: add absolute entries across each row and keep the largest sum. Column sums define the induced 1-norm. The largest singular value is the induced 2-norm. The Frobenius norm uses squares of entries instead of a single row.",
         M14, A_M14)
    b.order(2,
            "Put these steps in the order you would use to compute an induced 1-norm.",
            ["Replace every entry by its absolute value.",
             "Add the absolute values down each column.",
             "Keep the largest of those column sums.",
             "Report that largest sum as the induced 1-norm."],
            r"The induced 1-norm is a maximum of column sums of absolute values, so the absolute values come first, the sums second, and the maximum third. Reporting a row sum instead computes the infinity-norm. Taking the maximum entry before summing misses every column that has two nonzero numbers. The matrix in the figure is only a picture of a 2 by 2 array; the steps do not depend on its particular entries.",
            M14, A_M14)
    b.num(2,
          r"What is the induced infinity-norm of \(A = \begin{bmatrix} 1 & -4 \\ 2 & 3 \end{bmatrix}\)?",
          5, "1",
          r"Absolute row sums are \(\lvert 1 \rvert + \lvert -4 \rvert = 5\) and \(\lvert 2 \rvert + \lvert 3 \rvert = 5\). The induced infinity-norm is 5. The larger column sum is 7, which is the 1-norm of this same matrix. The largest entry is 4, and that entry is not a row sum.",
          M14, A_M14)
    b.num(2,
          r"What is the induced 2-norm of \(A = \begin{bmatrix} 3 & 0 \\ 0 & -5 \end{bmatrix}\)?",
          5, "1",
          r"The singular values of a diagonal matrix are the absolute values of the diagonal entries, here 3 and 5. The induced 2-norm is the larger singular value, 5. The signed entry \(-5\) is not a norm. The sum \(3+5 = 8\) is the nuclear norm, and the square root of \(9+25\) is the Frobenius norm.",
          M35, A_M35)
    b.sym(3,
          r"Let \(a > 0\). Write the induced 1-norm of \(\begin{bmatrix} a & -a \\ 2a & 0 \end{bmatrix}\) as an expression in the name a.",
          "3*a",
          {"a": (0.25, 6)},
          r"With \(a > 0\), the absolute column sums are \(\lvert a \rvert + \lvert 2a \rvert = 3a\) and \(\lvert -a \rvert + 0 = a\). The induced 1-norm is the larger sum, \(3a\)."
          "\n"
          r"• \(2a\) is the common absolute row sum, so it is the infinity-norm of this matrix."
          "\n"
          r"• \(4a\) adds every absolute entry and does not discard the smaller column."
          "\n"
          r"• \(a\) keeps the smaller column and misses the column that holds both \(a\) and \(2a\).",
          ["a+a+a", "(6*a)/2", "3*(a)"],
          fig=MSYM, alt=A_SYM)
    b.num(3,
          r"What is the induced 2-norm of \(A = \begin{bmatrix} 0 & -6 \\ 0 & 0 \end{bmatrix}\)?",
          6, "1",
          r"\(A^T A = \mathrm{diag}(0, 36)\), so the singular values are 0 and 6. The induced 2-norm is 6. The only nonzero entry already has absolute value 6, which happens to match, but the matching reason is the singular value, not the rule that a norm equals its largest entry. A column sum gives the same 6 here and is the 1-norm, a different definition.",
          M06, A_M06)
    b.mc(3,
         r"For an induced matrix norm, which relation holds for every vector \(x\)?",
         [r"\(\lVert Ax \rVert \ge \lVert A \rVert \, \lVert x \rVert\)",
          r"\(\lVert Ax \rVert = \lVert A \rVert + \lVert x \rVert\)",
          r"\(\lVert Ax \rVert \le \lVert A \rVert \, \lVert x \rVert\)",
          r"\(\lVert Ax \rVert \le \lVert A \rVert + \lVert x \rVert\)"],
         2,
         r"The induced norm is defined as the maximum of \(\lVert Ax \rVert / \lVert x \rVert\), so the inequality points that way: the stretch of one particular \(x\) cannot exceed the maximum. The reverse inequality would say every vector attains the maximum. Adding the two norms is not a product bound. A sum on the right is a different estimate and is not the operator-norm inequality.",
         BALLS, A_BALLS)
    b.find_error(4,
                 r"One of these steps is false. Select that step, and the reason it fails. The matrix is \(A = \begin{bmatrix} 1 & 1 \\ 1 & 1 \end{bmatrix}\).",
                 [r"Let \(A\) be the \(2 \times 2\) matrix whose four entries are all 1.",
                  r"The largest absolute entry of \(A\) is 1.",
                  "The induced 2-norm of a matrix equals its largest absolute entry.",
                  r"Applying that rule to \(A\) produces the value 1."],
                 2,
                 r"The largest entry really is 1, and the last step only applies the rule stated just above it. The false step is the rule. The induced 2-norm is the largest singular value. Here \(A\) is symmetric with eigenvalues 2 and 0, because \(A(1,1) = (2,2)\), so the 2-norm is 2 rather than 1. A column-sum formula would compute the 1-norm, which is also 2 for this matrix, and it is not what the flawed step claimed. Singular values are nonnegative, so a sign correction is not the issue.",
                 reasons=["The induced 2-norm is the largest singular value, which is 2 for this matrix, not the largest entry.",
                          "Column sums define the infinity-norm, so the step should have added across a row.",
                          "Singular values of a symmetric matrix are allowed to be negative, and that is the missing sign."],
                 correct_reason=0,
                 fig=MONES, alt=A_ONES, preview=["lipschitz-gradient"])
    b.num(4,
          r"For symmetric \(A\), the gradient of \(\tfrac12 x^T A x\) is \(Ax\), and its Lipschitz constant is the induced 2-norm of \(A\). What is that constant when \(A = \mathrm{diag}(4, 7)\)?",
          7, "1",
          r"The singular values are the absolute eigenvalues 4 and 7, so the induced 2-norm is 7. That is the Lipschitz constant. The other eigenvalue 4 is a stretch in a different direction, not the worst one. The trace 11 adds the eigenvalues, and the determinant 28 multiplies them.",
          M47, A_M47, ["lipschitz-gradient"])
    b.mc(4,
         r"When \(A\) is real and symmetric, the induced 2-norm equals",
         [r"the trace of \(A\)",
          "the smallest eigenvalue, keeping its sign",
          r"the largest entry of \(A\)",
          r"the largest of \(\lvert \lambda \rvert\) over the eigenvalues of \(A\)"],
         3,
         r"A real symmetric matrix has singular values equal to the absolute values of its eigenvalues, and the induced 2-norm keeps the largest of those. A negative eigenvalue still contributes its absolute value: \(\mathrm{diag}(1,-6)\) has 2-norm 6, not \(-6\) and not 1. The trace adds every eigenvalue, and the largest entry need not be an eigenvalue at all. This extreme stretch is the curvature bound a descent argument spends.",
         M35, A_M35, ["descent-lemma"])
    b.save()


def bank_frobenius():
    b = Bank("frobenius-schatten-norms")
    b.mc(1,
         "The Frobenius norm of a real matrix is",
         ["the square root of the sum of the squares of the entries",
          "the sum of the absolute values of the entries",
          "the largest absolute entry",
          "the product of the singular values"],
         0,
         r"Squaring, summing, and taking the square root is the Frobenius norm, and the same number is \(\sqrt{\sum_i \sigma_i^2}\). A sum of absolute entries is not that root. The largest entry is not a norm of this family by itself. The product of the singular values is the absolute value of the determinant when the matrix is square, which is a different summary.",
         M34, A_M34)
    b.num(1,
          r"What is the Frobenius norm of \(A = \begin{bmatrix} 3 & 0 \\ 0 & -4 \end{bmatrix}\)?",
          5, "1",
          r"The squares of the entries are 9 and 16, and \(9+16 = 25\). The Frobenius norm is \(\sqrt{25} = 5\). The singular values are 3 and 4, and \(\sqrt{9+16}\) is the same 5. Their sum 7 is the nuclear norm. The largest one, 4, is the spectral norm.",
          M34, A_M34)
    b.mc(1,
         "The Schatten 1-norm, also called the nuclear norm, equals",
         ["the largest singular value",
          "the square of the largest singular value",
          "the product of the singular values",
          "the sum of the singular values"],
         3,
         r"Schatten norms are \(\ell_p\) norms of the singular-value list. The case \(p = 1\) adds the singular values. The case \(p = \infty\) keeps only the largest. Squaring that largest value, or multiplying the singular values together, is neither the sum nor the max.",
         M34, A_M34)
    b.sym(2,
          r"Write the Frobenius norm of \(\begin{bmatrix} a & b \\ 0 & 0 \end{bmatrix}\) as an expression in the names a and b.",
          "sqrt(a^2 + b^2)",
          {"a": (-4, 4), "b": (-4, 4)},
          r"The only nonzero entries are \(a\) and \(b\). The sum of squares is \(a^2 + b^2\), and the Frobenius norm is the square root of that sum. The same expression is the Euclidean length of the first row."
          "\n"
          r"• \(a^2 + b^2\) stops before the square root, so it is the square of the norm."
          "\n"
          r"• \(\lvert a \rvert + \lvert b \rvert\) is a sum of absolute values, the 1-norm of the first row, not the Frobenius norm."
          "\n"
          r"• \(ab\) multiplies the entries. The zero row does not cancel that mistake.",
          ["sqrt(b^2 + a^2)", "(a^2 + b^2)^(1/2)", "sqrt((a^2) + (b^2))"],
          fig=MAB, alt=A_MAB)
    b.num(2,
          r"The singular values of \(A = \begin{bmatrix} 3 & 0 \\ 0 & -4 \end{bmatrix}\) are 3 and 4. What is the nuclear norm of \(A\)?",
          7, "1",
          r"The nuclear norm adds the singular values: \(3+4 = 7\). The sign on the diagonal entry was already removed when the singular value was formed, so adding \(3+(-4)\) is not the nuclear norm. The Frobenius norm is \(\sqrt{9+16} = 5\), and the spectral norm is 4.",
          M34, A_M34)
    b.num(2,
          r"What is the spectral norm of \(A = \begin{bmatrix} 0 & 5 \\ 12 & 0 \end{bmatrix}\)?",
          12, "1",
          r"\(A^T A = \mathrm{diag}(144, 25)\), so the singular values are 12 and 5. The spectral norm is the Schatten \(\infty\)-norm, the larger singular value, 12. It is also the induced 2-norm. The sum \(12+5 = 17\) is the nuclear norm, and \(\sqrt{144+25} = 13\) is the Frobenius norm.",
          M512, A_M512)
    b.order(3,
            "Put these steps in the order you would use to compute a Frobenius norm from singular values.",
            ["List the singular values, all of them nonnegative.",
             "Square each singular value.",
             "Add those squares.",
             "Take the square root of that sum."],
            r"The Frobenius norm is \(\sqrt{\sum_i \sigma_i^2}\). The singular values are already nonnegative, so the next operations are square, add, and root, in that order. Adding the singular values before squaring computes the nuclear norm instead. Taking the maximum and stopping computes the spectral norm. The root has to come after the sum: the square root of a sum is not the sum of the square roots.",
            M512, A_M512)
    b.num(3,
          r"What is the Frobenius norm of \(A = \begin{bmatrix} 0 & 5 \\ 12 & 0 \end{bmatrix}\)?",
          13, "1",
          r"The squares of the entries are 25 and 144, and \(25+144 = 169 = 13^2\). The Frobenius norm is 13. The singular values 12 and 5 give the same root of the sum of squares. Their maximum is 12, the spectral norm, and their sum is 17, the nuclear norm.",
          M512, A_M512)
    b.multi(3,
            "Which quantities equal the Frobenius norm of every real matrix?",
            ["the square root of the sum of the squares of the entries",
             "the square root of the sum of the squares of the singular values",
             "the sum of the singular values",
             "the largest singular value"],
            [0, 1],
            r"Both entrywise and singular-value formulas define the Frobenius norm, so both are right for every real matrix. The sum of the singular values is the nuclear norm, and it agrees with the Frobenius norm only for special matrices, such as a rank-one matrix with a single nonzero singular value. The largest singular value is the spectral norm, which is at most the Frobenius norm and equal only when at most one singular value is positive.",
            M34, A_M34)
    b.find_error(4,
                 r"One of these steps is false. Select that step, and the reason it fails. The matrix is \(A = \begin{bmatrix} 3 & 0 \\ 0 & -4 \end{bmatrix}\).",
                 ["Let A be the diagonal matrix with diagonal entries 3 and -4.",
                  "The singular values of A are 3 and 4.",
                  "The Frobenius norm is the sum of the singular values.",
                  "Applying that rule to A produces the value 7."],
                 2,
                 r"The singular values are 3 and 4, since a diagonal entry contributes its absolute value. The last step only evaluates the rule above it, so the false step is the identification of the Frobenius norm with that sum. The sum of the singular values is the nuclear norm, 7. The Frobenius norm is \(\sqrt{3^2 + 4^2} = 5\). Putting the sign back onto 4 would describe neither norm. The product \(3 \cdot 4 = 12\) is not the Frobenius norm either.",
                 reasons=["The sum of the singular values is the nuclear norm. The Frobenius norm is the square root of the sum of their squares, which is 5 here.",
                          "The diagonal entry -4 should be added with its sign, so the norm is 3 plus -4.",
                          "The Frobenius norm multiplies the singular values, so the value is 12."],
                 correct_reason=0,
                 fig=M34, alt=A_M34, preview=["linear-least-squares"])
    b.num(4,
          r"The singular values of \(A = \begin{bmatrix} 0 & 5 \\ 12 & 0 \end{bmatrix}\) are 12 and 5. What is the sum of their squares?",
          169, "1",
          r"\(12^2 + 5^2 = 144 + 25 = 169\). That sum is the square of the Frobenius norm, and the Frobenius norm itself is 13. The larger singular value alone is 12, which is the induced 2-norm. The sum of the singular values, without squares, is 17.",
          M512, A_M512, ["induced-matrix-norms"])
    b.mc(4,
         r"For every real matrix \(A\), how do the spectral norm and the Frobenius norm compare?",
         [r"the Frobenius norm is always strictly smaller than the spectral norm",
          "the two norms are equal for every matrix",
          r"the spectral norm is at most the Frobenius norm",
          r"the nuclear norm is at most the spectral norm"],
         2,
         r"The spectral norm is the largest singular value, and the Frobenius norm is the Euclidean norm of the whole list of singular values, so the largest one cannot exceed that Euclidean norm. Equality holds when every other singular value is zero, so the comparison is not always strict and the two norms are not always equal. The nuclear norm adds the singular values, so it is at least the spectral norm, not at most. The spectral norm is also the induced 2-norm, which is why this comparison bounds an operator norm by an entrywise one.",
         M512, A_M512, ["induced-matrix-norms"])
    b.save()


def bank_open():
    b = Bank("open-closed-sets")
    b.mc(1,
         r"A set \(U \subset \mathbb{R}^n\) is open when",
         ["every one of its points is an interior point",
          "it contains its boundary",
          "it is bounded",
          "it contains the origin"],
         0,
         r"Open means the set equals its interior: around every point of the set there is some ball, of positive radius, that stays inside the set. Containing the boundary is the extra demand that makes a set closed, and an open ball does not contain its sphere. Boundedness and the origin are irrelevant. The whole space is open, and so is the empty set.",
         DISK, A_DISK)
    b.num(1,
          r"What is the largest radius of an open ball about \((2, 0)\) that sits inside the open ball of radius 7 about the origin?",
          5, "1",
          r"The center \((2, 0)\) is at distance 2 from the origin, and the outer radius is 7, so the gap is \(7 - 2 = 5\). Any point within distance strictly less than 5 of \((2, 0)\) has norm strictly less than 7, by the triangle inequality. A larger test radius reaches the sphere or beyond it. The distance 2 alone is the distance to the origin, not the room that remains.",
          DISK, A_DISK)
    b.mc(1,
         r"The closed unit ball \(\{x : \lVert x \rVert_2 \le 1\}\) is",
         ["open and not closed",
          "neither open nor closed",
          "both open and closed",
          "closed and not open"],
         3,
         r"The inequality is not strict, so the sphere is included and the set contains its boundary. It is closed. A point on the sphere has no ball that stays inside the set, because every ball around it leaves the unit ball. It is not open. The empty set and the whole space are the usual sets that are both. An open ball, with a strict inequality, is the set that is open and not closed.",
         DISK, A_DISK)
    b.order(2,
            r"Put these steps in order to show that a point \(x\) with \(\lVert x \rVert < R\) is an interior point of the open ball of radius \(R\).",
            [r"Subtract \(\lVert x \rVert\) from \(R\) to get a positive gap.",
             r"Use that gap as the radius of a test ball about \(x\).",
             r"For a point \(y\) of the test ball, bound \(\lVert y \rVert\) by the triangle inequality.",
             r"Check that the bound is strictly less than \(R\), so the test ball lies in the open ball."],
            r"The gap \(R - \lVert x \rVert\) is positive exactly because \(x\) is inside the open ball. That gap is the largest test radius that works. The triangle inequality then says \(\lVert y \rVert \le \lVert y - x \rVert + \lVert x \rVert\), and a strict inequality in the test ball keeps \(\lVert y \rVert < R\). Starting from the triangle inequality before the gap is known does not produce a radius. Using a nonpositive radius would not show an interior point.",
            DISK, A_DISK)
    b.num(2,
          r"In \(\mathbb{R}\), what is the largest radius of an open ball about 4 that lies in the open interval \((1, 8)\)?",
          3, "1",
          r"The distance from 4 to 1 is 3, and the distance from 4 to 8 is 4. The limiting endpoint is the nearer one, so the largest radius is 3. Any open interval of that radius about 4 stays inside \((1, 8)\). The radius 4 would reach 0, which is outside the interval. The length of \((1, 8)\) is 7, which is not the room around the point 4.",
          SEG, A_SEG)
    b.num(2,
          r"In \(\mathbb{R}\), how many points does the closure of the set \(\{1, 1/2, 1/3\}\) contain?",
          4, "1",
          r"The set already has the three points 1, \(1/2\), and \(1/3\). The sequence approaches 0, and 0 is not one of the three, so the closure adds 0 and contains 4 points. Counting only the original three misses the limit. Counting only 0 would replace the set by its missing limit instead of adding that limit.",
          SEG, A_SEG)
    b.multi(3,
            r"Which of these subsets of \(\mathbb{R}^2\) are open?",
            [r"\(\{x : \lVert x \rVert_2 < 2\}\)",
             r"\(\{x : \lVert x \rVert_2 \le 2\}\)",
             r"\(\{x : x_1 > 0\}\)",
             r"the singleton \(\{(0,0)\}\)"],
            [0, 2],
            r"The open disk of radius 2 is open by the ball definition, and the strict half-plane \(x_1 > 0\) is open because a point with first coordinate \(c > 0\) has a ball of radius \(c\) that stays in the half-plane. The closed disk includes its circle, and those boundary points are not interior. A singleton in \(\mathbb{R}^2\) has empty interior: every ball around the origin contains other points.",
            HALF, A_HALF)
    b.num(3,
          r"What is the largest radius of an open ball about \((0, 4)\) that lies in the open half-plane \(\{x : x_2 > 0\}\)?",
          4, "1",
          r"The point is 4 units above the boundary line \(x_2 = 0\). A ball of radius 4 stays strictly above that line, and any larger ball crosses it or touches it. The first coordinate is 0, which is not a distance to the boundary. Twice the height, 8, would be the width of a ball that is already too big.",
          HALF, A_HALF)
    b.find_error(3,
                 "One of these steps is false. Select that step, and the reason it fails.",
                 ["Let C be the closed unit ball, and let x be a point of C on the unit sphere.",
                  "Every ball around x meets C.",
                  "A point of C is interior whenever every ball around it meets C.",
                  "Applying that test to x says that x is an interior point of C."],
                 2,
                 r"The point on the sphere does lie in the closed ball, and every ball around it does meet the closed ball. The last step only applies the test stated just above it. That test is false. An interior point needs some ball that lies entirely inside the set, not a ball that merely meets the set. Every ball around a sphere point also meets the complement, so x is a boundary point. The radius of those balls is positive; that is not what failed. The closed ball is not empty.",
                 reasons=["Meeting the set is not enough for an interior point. A ball around this x always leaves C.",
                          "The ball around x was required to have radius zero, so the step never tested a neighborhood.",
                          "A closed ball is empty, so it has no point of norm 1."],
                 correct_reason=0,
                 fig=DISK, alt=A_DISK)
    b.mc(4,
         r"The open unit ball in \(\mathbb{R}^n\) fails to be compact because",
         ["it is unbounded",
          "it does not contain its boundary",
          "it is empty",
          "it is not convex"],
         1,
         r"The open unit ball is bounded, nonempty, and convex. It leaves out the unit sphere, so it is not closed. In \(\mathbb{R}^n\) a compact set has to be closed and bounded, and the missing boundary is the property that fails. That is the fact a later compactness test spends.",
         DISK, A_DISK, ["compact-sets"])
    b.num(4,
          r"A neighborhood used to define a local minimizer is an open ball. The point \((1, 2)\) lies in the open ball of radius 3 about the origin. What is the squared Euclidean distance from \((1, 2)\) to the origin?",
          5, "1",
          r"The squared distance is \(1^2 + 2^2 = 5\). The distance itself is \(\sqrt{5}\), which is less than 3, so the point really is inside that neighborhood. The sum of the coordinates is 3, and the product is 2. Neither is the squared length. Neighborhoods in a local-minimum definition are open sets of this kind.",
          DISK, A_DISK, ["local-global-minima"])
    b.mc(4,
         r"Which of these sets is both open and closed in \(\mathbb{R}^n\)?",
         ["the open unit ball",
          "a singleton",
          r"the whole space \(\mathbb{R}^n\)",
          r"a line in the plane, when \(n = 2\)"],
         2,
         r"The whole space has empty boundary, so it contains its boundary and every point is interior. It is closed and open. The empty set is the other usual example. An open ball misses its sphere. A singleton and a line in the plane are closed and have empty interior, so they are not open. A closed set that is not compact, such as the whole space, is exactly why a later existence argument asks for something smaller than closedness alone.",
         ORTH, A_ORTH, ["existence-of-minimizers"])
    b.save()


def bank_compact():
    b = Bank("compact-sets")
    b.mc(1,
         r"In \(\mathbb{R}^n\), a set is compact when it is",
         ["closed and bounded",
          "open and bounded",
          "closed, whether or not it is bounded",
          "bounded, whether or not it is closed"],
         0,
         r"Heine-Borel says that in \(\mathbb{R}^n\) the compact sets are exactly the sets that are closed and bounded. An open ball is bounded and not closed, so it is not compact. A line is closed and unbounded, so it is not compact either. Either property by itself is not the theorem.",
         DISK, A_DISK)
    b.num(1,
          r"What is the smallest radius \(R\) such that the point \((5, 12)\) lies in the closed ball of radius \(R\) about the origin?",
          13, "1",
          r"The Euclidean norm is \(\sqrt{5^2 + 12^2} = \sqrt{25 + 144} = \sqrt{169} = 13\). That is the smallest such radius. The sum of the coordinates is 17, and the larger coordinate is 12. Either of those is larger than the straight-line distance, so neither is the radius of the smallest origin-centered ball.",
          DISK, A_DISK)
    b.mc(1,
         "The open unit disk is not compact because",
         ["it is unbounded",
          "it fails to be convex",
          "it does not contain its boundary",
          "it contains no points"],
         2,
         r"The open unit disk sits inside the closed unit disk, so it is bounded, and it is a nonempty convex set. The unit circle is a set of limit points that the disk does not contain, so the disk is not closed. In the plane, that missing closedness is enough to lose compactness.",
         DISK, A_DISK)
    b.order(2,
            "Put these steps in order to show that the open unit disk is not compact.",
            ["Name a point on the unit circle.",
             "Note that the point is a limit of points in the disk, and that the point itself is not in the disk.",
             "Conclude that the disk is not closed.",
             r"Apply the characterization in \(\mathbb{R}^n\): a set that is not closed is not compact."],
            r"A concrete boundary point comes first, because the failure of closedness is witnessed by that point. It can be approached from inside the disk and it is not a member, so the disk misses a limit point. Only then does Heine-Borel apply: not closed implies not compact. Declaring the disk unbounded would be a different, and false, reason. Invoking compactness before exhibiting the missing limit point skips the property that actually fails.",
            DISK, A_DISK)
    b.num(2,
          r"What is the smallest radius of a closed ball about the origin that contains the rectangle \([0, 6] \times [0, 8]\)?",
          10, "1",
          r"The farthest corner from the origin is \((6, 8)\), and \(\sqrt{6^2 + 8^2} = \sqrt{36 + 64} = 10\). Every other point of the rectangle is closer. The side lengths 6 and 8 are each too small to cover that corner. The perimeter sum \(2(6+8) = 28\) is not a radius.",
          ORTH, A_ORTH)
    b.num(2,
          "The open unit disk is bounded, and it is not closed. How many of those two Heine-Borel properties does it have?",
          1, "1",
          r"Boundedness holds, because the disk sits inside the closed ball of radius 1. Closedness fails, because the unit circle is missing. Exactly one of the two properties holds. Counting both would treat an open disk as closed. Counting neither would deny that a unit disk is bounded.",
          DISK, A_DISK)
    b.multi(3,
            r"Which of these subsets of \(\mathbb{R}^2\) are compact?",
            ["the closed disk of radius 4",
             "the horizontal axis",
             "the open disk of radius 4",
             "a set of exactly three points"],
            [0, 3],
            r"The closed disk of radius 4 contains its circle and sits inside a ball, so it is closed and bounded. Three points form a finite set: it contains its limit points, and a ball large enough to cover the three points shows it is bounded. The horizontal axis is closed and unbounded. The open disk of radius 4 is bounded and misses its circle, so it is not closed.",
            DISK, A_DISK)
    b.num(3,
          r"What is the smallest \(M\) such that every one of \((1, 2)\), \((4, -2)\), and \((-5, 0)\) has Euclidean norm at most \(M\)?",
          5, "1",
          r"The three norms are \(\sqrt{1+4} = \sqrt{5}\), \(\sqrt{16+4} = \sqrt{20}\), and 5. The largest is 5, from the point \((-5, 0)\). A smaller candidate such as \(\sqrt{20}\) leaves that point out. The sum of the largest coordinates is not the max norm.",
          DISK, A_DISK)
    b.find_error(3,
                 "One of these steps is false. Select that step, and the reason it fails.",
                 ["Let U be the open unit disk in the plane.",
                  "U sits inside the closed disk of radius 1, so U is bounded.",
                  r"In \(\mathbb{R}^n\), boundedness alone is the definition of compactness.",
                  "Applying that definition to U says that U is compact."],
                 2,
                 r"The open unit disk is bounded, and the containment in the closed disk of radius 1 is correct. The last step only applies the definition stated above it. That definition is missing closedness. Heine-Borel needs both closed and bounded, and this disk is not closed. The disk is not unbounded, and a positive radius is allowed in the definition of boundedness.",
                 reasons=[r"Compactness in \(\mathbb{R}^n\) also requires the set to be closed, and this disk omits its boundary.",
                          "The disk is unbounded, because its radius is a positive number.",
                          "Boundedness forbids a finite radius, so the second step already used an illegal ball."],
                 correct_reason=0,
                 fig=DISK, alt=A_DISK)
    b.mc(4,
         r"A continuous real function on a nonempty subset of \(\mathbb{R}^n\) is guaranteed to attain its minimum when the subset is",
         ["any open set",
          "any nonempty compact set",
          "any closed set, bounded or not",
          "any bounded set, closed or not"],
         1,
         r"A continuous function on a nonempty compact set attains its minimum and its maximum. An open interval such as \((0, 1)\) is bounded and the function \(f(x) = x\) has no minimum there. A closed line is closed and unbounded, and a linear function on it is unbounded below. Boundedness without closedness is the open-disk situation. Attainment is the reason compactness shows up in existence arguments.",
         DISK, A_DISK, ["existence-of-minimizers"])
    b.num(4,
          r"On the compact interval \([1, 6]\), the function \(f(x) = (x - 3)^2 + 4\) attains a minimum. What is that minimum value?",
          4, "1",
          r"The square is nonnegative and equals 0 at \(x = 3\), which lies in \([1, 6]\). The minimum value is 4. The value at the left endpoint is \((1-3)^2 + 4 = 8\), and the vertex location 3 is the minimizer rather than the minimum value. A continuous function on a nonempty compact set is entitled to attain a value; this one does.",
          SEG, A_SEG, ["existence-of-minimizers"])
    b.mc(4,
         "Which set is closed and unbounded, and therefore not compact?",
         ["the closed unit ball",
          "a set of two points",
          "the open unit ball",
          "a closed half-space that is not the whole space"],
         3,
         r"A closed half-space contains its boundary hyperplane, so it is closed, and it runs off to infinity in the inward normal direction, so it is unbounded. It is not compact. The closed unit ball and a two-point set are closed and bounded. The open unit ball is bounded and not closed, which is a different way to fail. An unbounded feasible set is why a stationary-point test still needs a separate existence argument.",
         HALF, A_HALF, ["stationary-point-classification"])
    b.save()


def bank_level():
    b = Bank("level-sets-contours")
    b.mc(1,
         r"The sublevel set of a function \(f\) at height \(a\) is",
         [r"the set where \(f\) equals \(a\)",
          r"the set where \(f\) is at most \(a\)",
          r"the set where \(f\) is at least \(a\)",
          r"the domain of \(f\), whatever \(a\) is"],
         1,
         r"The sublevel set \(\mathrm{lev}(f, a)\) keeps every point whose value is less than or equal to \(a\). Equality alone is the contour set. The opposite inequality is a superlevel set. The domain is where \(f\) is defined, not where it is small.",
         ELL, A_ELL)
    b.num(1,
          r"The sublevel set of \(f(x, y) = x^2 + y^2\) at height 16 is a closed disk. What is its radius?",
          4, "1",
          r"The inequality \(x^2 + y^2 \le 16\) is the closed disk of radius \(\sqrt{16} = 4\). The contour at the same height is the circle of that radius, not a disk of radius 16. The diameter would be 8. The height 16 is the squared radius, not the radius.",
          ELL, A_ELL)
    b.mc(1,
         r"The contour set of \(f(x, y) = x^2 + y^2\) at height 16 is",
         ["the circle of radius 4",
          "the disk of radius 4, including the interior",
          "a single point, the origin",
          "a straight line"],
         0,
         r"A contour set is the equality \(x^2 + y^2 = 16\), a circle of radius 4. The disk, interior included, is the sublevel set at that height. The origin has value 0, so it lies in the sublevel set and not on this contour. A round level set of this \(f\) is not a line.",
         LEVELS, A_LEVELS)
    b.sym(2,
          r"Let \(a > 0\) and \(c > 0\). The sublevel set \(\{t \in \mathbb{R} : c t^2 \le a\}\) is a closed interval. Write its right endpoint as an expression in the names a and c.",
          "sqrt(a/c)",
          {"a": (1, 9), "c": (0.4, 5)},
          r"The inequality \(c t^2 \le a\) rearranges, for \(c > 0\), to \(t^2 \le a/c\). The right endpoint is the positive square root \(\sqrt{a/c}\)."
          "\n"
          r"• \(a/c\) is the square of that endpoint."
          "\n"
          r"• \(\sqrt{a} - \sqrt{c}\) subtracts lengths that are not the two sides of this inequality."
          "\n"
          r"• \(c/a\) inverts the ratio. The function value grows when \(c\) grows, so the sublevel set shrinks.",
          ["(a/c)^(1/2)", "sqrt(a*(1/c))", "(a*(1/c))^(1/2)"],
          fig=SEG, alt=A_SEG)
    b.num(2,
          r"On the contour \(x^2 + 4 y^2 = 16\), what is the largest value of \(y\)?",
          2, "1",
          r"The largest \(y\) occurs where \(x = 0\), so \(4 y^2 = 16\), \(y^2 = 4\), and the positive solution is 2. The positive \(x\)-intercept is 4, which solves \(x^2 = 16\). The height 16 is not a coordinate. The semi-axis in \(y\) is the number asked for.",
          ELL, A_ELL)
    b.order(2,
            r"Put these steps in order to sketch the sublevel set of \(f(x, y) = (x/3)^2 + (y/2)^2\) at height 1.",
            [r"Read the equality \(f(x, y) = 1\) as an ellipse and record its semi-axes.",
             "Draw that ellipse. It is the boundary of the sublevel set.",
             r"Evaluate \(f\) at the origin and compare the value with 1.",
             "Shade the inside of the ellipse, including the boundary, because the inequality is not strict."],
            r"The equality case is the contour, an ellipse with semi-axes 3 and 2, and that curve is the boundary. A test point decides which side belongs to the sublevel set: the origin has value 0, which is below 1, so the inside is the side to shade. The inequality is \(\le\), so the boundary is included. Shading before the test point can fill the outside. Dropping the boundary would draw a strict sublevel set.",
            ELL, A_ELL)
    b.multi(3,
            r"For \(f(x, y) = x^2 + y^2\), which of these points lie in the sublevel set at height 4?",
            [r"\((0, 0)\)",
             r"\((2, 0)\)",
             r"\((3, 1)\)",
             r"\((1, -1)\)"],
            [0, 1, 3],
            r"The values are 0, 4, 10, and 2. The sublevel set keeps values at most 4, so the origin, \((2, 0)\), and \((1, -1)\) belong. The point \((2, 0)\) is on the contour, and a non-strict sublevel set includes its contour. The point \((3, 1)\) has value 10 and is outside. Leaving out the origin would confuse the sublevel set with the contour.",
            LEVELS, A_LEVELS)
    b.num(3,
          r"On the contour \(2x + y = 10\), what is \(y\) when \(x = 3\)?",
          4, "1",
          r"Substitute \(x = 3\): \(6 + y = 10\), so \(y = 4\). The contour of a linear function is a straight line. The value 10 is the height, not the missing coordinate. The intercept on the \(y\)-axis, where \(x = 0\), would be 10. Half of 10 is 5, which forgets the coefficient 2.",
          HALF, A_HALF)
    b.find_error(3,
                 r"One of these steps is false. Select that step, and the reason it fails. The function is \(f(x, y) = x^2 + y^2\).",
                 ["Take the height 4.",
                  "The origin has value 0, which is not equal to 4.",
                  "A sublevel set keeps only the points where the function equals the height.",
                  "Applying that definition to the origin excludes it, because its value is not 4."],
                 2,
                 r"The origin really does have value 0. The last step only applies the definition stated above it, and that definition is the contour set, not the sublevel set. The sublevel set at height 4 is \(x^2 + y^2 \le 4\), which contains the origin. The contour is the circle of radius 2. The origin is a minimum, not a maximum, and the squares are allowed to be added.",
                 reasons=["The sublevel set keeps every point whose value is at most 4, so the origin belongs to it.",
                          "The origin is a maximum of this function, so every sublevel set excludes it.",
                          "Squared coordinates cannot be added, so the value at the origin is not 0."],
                 correct_reason=0,
                 fig=LEVELS, alt=A_LEVELS)
    b.mc(4,
         "When a planar optimization problem is solved by drawing, the objective is shown as",
         ["one feasible vertex",
          "the normal vector of a single constraint",
          "the empty set",
          "a family of contour lines, one line or curve for each height"],
         3,
         r"The drawing overlays contours of the objective on the feasible set and looks for the contour of best height that still touches the feasible set. A vertex is a candidate point, not the picture of the objective. A constraint normal describes the boundary of the feasible set. The empty set would mean there is nothing to draw. Contours are the picture a graphical solve actually uses.",
         LEVELS, A_LEVELS, ["graphical-2d-optimization"])
    b.num(4,
          r"The sublevel set of \(f(x, y) = x^2 + 4 y^2\) at height 36 meets the positive \(y\)-axis at one point. What is that \(y\)-coordinate?",
          3, "1",
          r"On the positive \(y\)-axis, \(x = 0\) and \(4 y^2 = 36\), so \(y^2 = 9\) and \(y = 3\). The positive \(x\)-intercept solves \(x^2 = 36\) and equals 6. The height 36 is not the coordinate. A sublevel set of a continuous coercive function is closed and bounded, which is the compactness a later existence argument uses.",
          ELL, A_ELL, ["existence-of-minimizers"])
    b.mc(4,
         r"The contour set of \(f(x, y) = 3x - y\) at one fixed height is",
         ["a disk",
          "a single point, for every height",
          "a straight line",
          "an ellipse"],
         2,
         r"An equality \(3x - y = a\) is one linear equation, hence a line. It is not a disk or an ellipse, because those come from quadratic equations. A single height does not collapse the line to a point. The sublevel set at the same height is a closed half-plane, which is what a linear constraint looks like in a graphical linear program.",
         HALF, A_HALF, ["lp-graphical-solution"])
    b.save()


def bank_convex():
    b = Bank("convex-sets")
    b.mc(1,
         r"A set \(C\) is convex when",
         ["it is a union of two balls",
          "it contains the origin",
          r"the segment between any two of its points lies in \(C\)",
          "it is bounded"],
         2,
         r"Convexity is the segment test: for every pair of points in \(C\) and every weight \(t \in [0, 1]\), the combination \((1-t)x + ty\) is in \(C\). A union of two balls can fail that test. The origin is not required, and a half-space is convex and unbounded.",
         SEG, A_SEG)
    b.num(1,
          r"What is the first coordinate of the midpoint of \((2, 10)\) and \((8, 4)\)?",
          5, "1",
          r"The midpoint is \(\tfrac12(2+8, 10+4) = (5, 7)\). The first coordinate is 5. The second coordinate is 7. Either endpoint alone would give 2 or 8. If a convex set contains both endpoints, it contains this midpoint.",
          SEG, A_SEG)
    b.mc(1,
         "Which operation preserves convexity for every family of convex sets?",
         ["intersection",
          "union",
          "taking the boundary",
          "taking the complement"],
         0,
         r"A point in the intersection lies in every set of the family, so the segment between two such points lies in every set, hence in the intersection. A union of two disjoint disks fails, because a bridge between them leaves both disks. The boundary of a disk is a circle, which is not convex. The complement of a disk is not convex either.",
         DISKS, A_DISKS)
    b.order(2,
            r"Put these steps in order to prove that a closed half-space \(\{x : a^T x \le b\}\) is convex.",
            [r"Take two points \(x\) and \(y\) in the half-space, and a weight \(t \in [0, 1]\).",
             r"Form the combination \(z = (1-t)x + ty\).",
             r"Split \(a^T z\) into \((1-t)\, a^T x + t\, a^T y\).",
             r"Replace each of \(a^T x\) and \(a^T y\) by its upper bound \(b\).",
             r"Simplify \((1-t)b + tb\) to \(b\), which is the half-space inequality for \(z\).",],
            r"The combination has to be built before its image under \(a^T\) can be expanded. The expansion is a weighted average of two numbers that are each at most \(b\), so the average is at most \(b\). The algebra \((1-t)b + tb = b\) is the last simplification. Bounding before the combination exists has nothing to bound. Replacing the upper bound \(b\) by a sum \(a^T x + a^T y\) would be a looser and different claim.",
            HALF, A_HALF)
    b.num(2,
          r"On the segment from \((0, 0)\) to \((8, 12)\), the point at \(t = 1/4\) has what second coordinate?",
          3, "1",
          r"The point is \((1-t)(0, 0) + t(8, 12)\). At \(t = 1/4\) the second coordinate is \(12/4 = 3\). The first coordinate is 2. The endpoint value 12 would be \(t = 1\). A convex set that contains both endpoints contains this point.",
          SEG, A_SEG)
    b.num(2,
          r"Both \((2, 1)\) and \((4, 3)\) lie in \(\{x : x_1 + 2 x_2 \le 10\}\). What is the left-hand side at their midpoint?",
          7, "1",
          r"The midpoint is \((3, 2)\). The left-hand side is \(3 + 2 \cdot 2 = 7\), which is at most 10, so the midpoint stays in the half-space. At the first point the left-hand side is 4, and at the second it is 10. The average of 4 and 10 is also 7, which is the same computation because the constraint is linear.",
          HALF, A_HALF)
    b.multi(3,
            "Which of these sets are convex?",
            ["a closed half-space",
             "an open ball of any norm",
             "the union of two disjoint closed disks",
             "a hyperplane",
             "the circle that bounds a disk"],
            [0, 1, 3],
            r"A closed half-space passes the segment test because a linear inequality is preserved by averages. An open ball of any norm does too: the triangle inequality and absolute homogeneity keep a combination inside the ball. A hyperplane is an affine set, and affine sets are convex. The union of two disjoint disks fails as soon as the segment between them crosses the gap. A circle fails because the chord between two of its points leaves the circle.",
            DISKS, A_DISKS)
    b.num(3,
          r"A convex set that contains \((0, 0)\), \((8, 0)\), and \((0, 8)\) contains the combination with weights \(1/2\), \(1/4\), and \(1/4\) in that order. What is the first coordinate of that combination?",
          2, "1",
          r"The combination is \(\tfrac12(0, 0) + \tfrac14(8, 0) + \tfrac14(0, 8) = (2, 2)\). The first coordinate is 2. The second coordinate is also 2, from the third point. The weight \(1/2\) on the origin contributes nothing. Convexity for pairs extends to any finite convex combination, which is why this point has to belong to the set.",
          SEG, A_SEG)
    b.find_error(3,
                 "One of these steps is false. Select that step, and the reason it fails.",
                 ["Let A and B be closed disks with a gap between them.",
                  "Each of A and B is convex.",
                  "A union of convex sets is convex, because a segment that starts and ends in one of them stays in that one.",
                  "Applying that claim to A and B says that their union is convex."],
                 2,
                 r"Each disk is convex, and a segment that starts and ends inside one disk does stay there. The last step only applies the general claim above it. That claim is false: convexity of the union also requires segments that start in one disk and end in the other. Those segments cross the gap and leave the union. The disks themselves are convex, so the failure is not in the first geometric step, and the union is not empty.",
                 reasons=["A segment from a point of A to a point of B can cross the gap and leave the union.",
                          "Disks are not convex, so the claim that each disk is convex is the false step.",
                          "The union of two nonempty sets is empty, so the last step has no set to discuss."],
                 correct_reason=0,
                 fig=DISKS, alt=A_DISKS)
    b.mc(4,
         "A polyhedron, defined by finitely many linear inequalities, is",
         ["never convex, because it has vertices",
          "convex, because it is an intersection of half-spaces",
          "open, because every linear inequality is strict",
          "a ball, because it is bounded whenever it is nonempty"],
         1,
         r"Each linear inequality describes a half-space, and an intersection of half-spaces is convex. Vertices do not cancel that. The inequalities that define a polyhedron are closed, not strict. A polyhedron can be unbounded, so it is not a ball in general. Extreme points of that convex set are the next object.",
         HALF, A_HALF, ["polyhedra-extreme-points"])
    b.num(4,
          r"Both \((0, 0)\) and \((4, 2)\) lie in \(\{x : x_1 + 2 x_2 \le 8, \; x \ge 0\}\). What is \(x_1 + 2 x_2\) at their midpoint?",
          4, "1",
          r"The midpoint is \((2, 1)\), and \(2 + 2 \cdot 1 = 4\), which is at most 8. The endpoint \((4, 2)\) gives 8, and the origin gives 0. The average of those two values is 4, matching the linear constraint. The segment test is what later lets a local minimizer over a convex set be global.",
          SEG, A_SEG, ["optimality-over-convex-set"])
    b.mc(4,
         "The domain of a convex function has to be",
         ["any open set, convex or not",
          "a union of sublevel sets, with no further restriction",
          "the set of its local minimizers",
          "a convex set"],
         3,
         r"The chord definition compares values at the endpoints of a segment with the value at the combination, so the combination has to lie in the domain. The domain is therefore a convex set. An open nonconvex set cannot be a domain. Sublevel sets of a convex function are convex, but the domain is the set on which the function is defined, not a union chosen after the fact. Local minimizers are a subset of the domain.",
         DENT, A_DENT, ["convex-functions"])
    b.save()


def expl_induced():
    sections = [
        {"heading": "The idea", "figure": BALLS, "figure_alt": A_BALLS,
         "body_md": r"""A vector norm measures the length of one vector. A matrix asks a different question: how much can multiplication by \(A\) stretch a vector? The induced norm, also called the operator norm, is the largest stretch. Take every vector of length 1, apply \(A\), and keep the longest result. Equivalently, look at \(\lVert Ax \rVert / \lVert x \rVert\) for \(x \ne 0\) and take the supremum. The vector norm in the numerator and the vector norm in the denominator are the same one, so each vector norm produces its own matrix norm.

That definition immediately gives the inequality \(\lVert Ax \rVert \le \lVert A \rVert \, \lVert x \rVert\). One particular vector cannot stretch more than the worst vector. The identity matrix has induced norm 1, and a product of matrices satisfies \(\lVert AB \rVert \le \lVert A \rVert \, \lVert B \rVert\).

Three cases have short formulas. The induced 1-norm is the largest absolute column sum. The induced infinity-norm is the largest absolute row sum. The induced 2-norm is the largest singular value of \(A\). For a real symmetric matrix, that singular value is the largest absolute eigenvalue."""},
        {"heading": "Key equations",
         "body_md": r"""\[
\lVert A \rVert = \max_{\lVert x \rVert = 1} \lVert Ax \rVert, \qquad \lVert Ax \rVert \le \lVert A \rVert \, \lVert x \rVert.
\]
With absolute values taken entrywise,
\[
\lVert A \rVert_1 = \max_j \sum_i \lvert a_{ij} \rvert, \qquad \lVert A \rVert_\infty = \max_i \sum_j \lvert a_{ij} \rvert, \qquad \lVert A \rVert_2 = \sigma_{\max}(A).
\]
The 2-norm is also \(\sqrt{\lambda_{\max}(A^T A)}\). On a real symmetric matrix it equals \(\max_i \lvert \lambda_i(A) \rvert\)."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A\) have rows \((8, 0, 0)\) and \((1, 1, 1)\). Absolute column sums are \(8+1 = 9\), \(0+1 = 1\), and \(0+1 = 1\). The induced 1-norm is 9. Absolute row sums are 8 and \(1+1+1 = 3\). The induced infinity-norm is 8.

The two numbers disagree, which is ordinary: column sums and row sums inspect different directions. The induced 2-norm is a third quantity, the largest singular value of this same matrix. It is not defined as the larger of 9 and 8, and it is not equal to the largest entry 8 either. Each formula has to be used for the norm it names."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Swapping rows and columns swaps the 1-norm and the infinity-norm. Taking the largest absolute entry is not an induced norm; the matrix of all ones has largest entry 1 and induced 2-norm 2. A negative eigenvalue still contributes its absolute value to the 2-norm. The Frobenius norm, built from squares of entries, is a genuine matrix norm, but it is not the operator norm induced by the vector 2-norm, and it is at least as large as that operator norm."""},
        {"heading": "Where this leads",
         "body_md": r"""If a gradient is Lipschitz, the Lipschitz constant can be read as an induced norm of a Hessian. For the quadratic \(\tfrac12 x^T A x\) with symmetric \(A\), that constant is exactly \(\lVert A \rVert_2\). A descent lemma then turns the constant into a quadratic upper bound on the function. The Frobenius norm is a different size, useful as a comparison because it sits above the induced 2-norm and is easy to compute from the entries."""},
    ]
    save_explainer("induced-matrix-norms", "Induced matrix norms", sections)


def expl_frobenius():
    fig = matrix_fig([["6", "0"], ["0", "-8"]], "diagonal matrix with entries 6 and -8")
    alt = "A diagonal 2 by 2 matrix with diagonal entries 6 and -8."
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": alt,
         "body_md": r"""The Frobenius norm treats a matrix as a long vector. Square every entry, add, and take the square root. The same number has a singular-value form: square the singular values, add, and take the square root. The two descriptions agree because the squared Frobenius norm equals the sum of the squares of the singular values.

Schatten norms apply an \(\ell_p\) norm to the list of singular values. The Schatten 2-norm is the Frobenius norm. The Schatten 1-norm is the nuclear norm, the sum of the singular values. The Schatten infinity-norm is the spectral norm, the largest singular value, which is also the induced 2-norm.

These are nested. The largest singular value cannot exceed the Euclidean norm of the list, and the Euclidean norm cannot exceed the sum. So the spectral norm is at most the Frobenius norm, which is at most the nuclear norm. Equality holds throughout when the matrix has at most one positive singular value."""},
        {"heading": "Key equations",
         "body_md": r"""\[
\lVert A \rVert_F = \sqrt{\sum_{ij} a_{ij}^2} = \sqrt{\sum_i \sigma_i^2}.
\]
The Schatten \(p\)-norm is \(\bigl(\sum_i \sigma_i^p\bigr)^{1/p}\) for \(1 \le p < \infty\), and the largest singular value when \(p = \infty\). In particular the nuclear norm is \(\sum_i \sigma_i\) and the spectral norm is \(\sigma_{\max}(A)\). For every real matrix, \(\lVert A \rVert_2 \le \lVert A \rVert_F \le \lVert A \rVert_{S_1}\)."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A = \mathrm{diag}(6, -8)\). The singular values are the absolute diagonal entries 6 and 8. The Frobenius norm is \(\sqrt{36 + 64} = \sqrt{100}\), so the Frobenius norm is 10. The nuclear norm is 14, the sum of those singular values. The spectral norm is 8.

The negative sign on the second diagonal entry never enters these three numbers. Using \(6 + (-8)\) would not be a Schatten norm. The gap between 8, 10, and 14 is the usual strict nesting for a matrix with two positive singular values."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The nuclear norm adds singular values. It does not add signed eigenvalues, and it does not add absolute entries of a matrix that is not already diagonal in a singular-vector basis. The spectral norm is not the spectral radius unless the matrix is symmetric, in which case the two agree after absolute values. For a nonsymmetric matrix the spectral radius can be smaller than every singular value. Leaving out the square root in the Frobenius formula produces the square of the norm."""},
        {"heading": "Where this leads",
         "body_md": r"""A linear least-squares residual is a Euclidean length of a vector of errors, which is a Frobenius norm when the residual is written as a matrix. The induced 2-norm remains the operator size, and the comparison \(\lVert A \rVert_2 \le \lVert A \rVert_F\) lets an entrywise calculation stand in for that operator size when a rough bound is enough. The nuclear norm is the Schatten norm that penalizes every singular value, not only the largest."""},
    ]
    save_explainer("frobenius-schatten-norms", "Frobenius and Schatten norms", sections)


def expl_open():
    sections = [
        {"heading": "The idea", "figure": DISK, "figure_alt": A_DISK,
         "body_md": r"""Open and closed describe how a set sits relative to its edge. Fix a norm on \(\mathbb{R}^n\). The open ball of radius \(r > 0\) about \(x\) is every point whose distance to \(x\) is strictly less than \(r\). The closed ball uses \(\le\) and therefore includes the sphere.

A point of a set is an interior point when some open ball about it lies entirely in the set. The set is open when every one of its points is interior. A limit point is a point that every ball meets the set in some other point. The set is closed when it contains all of its limit points. Equivalently, its complement is open, and equivalently it contains its boundary.

The boundary is the set of points where every ball meets both the set and the complement. The closure is the set with its boundary added. The empty set and the whole space are both open and closed. Plenty of sets are neither: a half-open interval contains one endpoint and misses the other."""},
        {"heading": "Key equations",
         "body_md": r"""\[
B(x, r) = \{y : \lVert y - x \rVert < r\}, \qquad \overline{B}(x, r) = \{y : \lVert y - x \rVert \le r\}.
\]
The interior of \(S\) is the largest open set contained in \(S\). The closure of \(S\) is the smallest closed set containing \(S\). A point \(x\) is interior to an open ball of radius \(R\) when the gap \(R - \lVert x - c \rVert\) is positive, and that gap is a legal radius for a test ball. In finite dimension, equivalent norms determine the same open sets."""},
        {"heading": "Worked example",
         "body_md": r"""Take the open ball of radius 6 about \((1, 2)\), and the point \((1, 5)\). The distance between them is \(\lvert 5 - 2 \rvert = 3\). Subtracting that distance from the radius leaves the gap, so the gap is 3. Any point within distance strictly less than 3 of \((1, 5)\) stays inside the original ball, so \((1, 5)\) is interior.

The matching closed ball of radius 6 contains the sphere. A point at distance exactly 6 from \((1, 2)\) belongs to the closed ball and to no open ball inside it. The closed ball is closed, and it is not open. Replacing the radius 6 by a strict inequality drops that sphere and produces an open set."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A ball that merely meets the set does not prove an interior point. The whole ball has to fit. Closed does not mean bounded: a line in the plane is closed and unbounded, and a closed half-space is too. Open does not mean the inequality that defines the set looks strict in every description. Finite unions of open sets are open, and so are arbitrary unions. An infinite intersection of open sets can be a single point, which is not open. In \(\mathbb{R}\), a nonempty finite set is closed and not open."""},
        {"heading": "Where this leads",
         "body_md": r"""Compactness in \(\mathbb{R}^n\) asks for closed and bounded together, so an open ball is the standard bounded set that fails. A local minimizer is defined with a neighborhood, and a neighborhood is an open ball. Existence of a minimizer on an unbounded set needs a substitute for compactness, because the whole space is closed and still too large. The boundary and the closure are the language those arguments use."""},
    ]
    save_explainer("open-closed-sets", "Open and closed sets in R^n", sections)


def expl_compact():
    sections = [
        {"heading": "The idea", "figure": DISK, "figure_alt": A_DISK,
         "body_md": r"""A set is bounded when some ball, of finite radius, contains it. Equivalently, the distances from the origin to its points have a finite upper bound. Boundedness alone does not keep limit points. Closedness alone does not prevent the set from running off to infinity.

In \(\mathbb{R}^n\) the two properties together are compactness. This is the Heine-Borel theorem: a subset of Euclidean space is compact exactly when it is closed and bounded. A closed ball, a sphere, a closed rectangle, and any finite set are compact. An open ball is bounded and not closed. A line, a closed half-space, and the integers are closed and unbounded.

One reason to care is attainment. A continuous real-valued function on a nonempty compact set reaches its minimum and its maximum. Drop either closedness or boundedness and a continuous function can have an infimum it never reaches."""},
        {"heading": "Key equations",
         "body_md": r"""\(S\) is bounded when there exist a center \(c\) and a radius \(R < \infty\) with \(S \subset \overline{B}(c, R)\). In \(\mathbb{R}^n\),
\[
S \text{ is compact} \iff S \text{ is closed and bounded}.
\]
A continuous \(f\) on a nonempty compact \(S\) attains \(\min_S f\) and \(\max_S f\). A closed subset of a compact set is compact. A finite union of compact sets is compact. The continuous image of a compact set is compact."""},
        {"heading": "Worked example",
         "body_md": r"""The rectangle \([0, 8] \times [0, 15]\) contains its boundary, so it is closed. Its farthest point from the origin is the corner \((8, 15)\), and
\[
\sqrt{8^2 + 15^2} = \sqrt{64 + 225} = \sqrt{289} = 17.
\]
The corner distance is 17, so the rectangle sits in the closed ball of radius 17 and is bounded. It is compact.

The open rectangle \((0, 8) \times (0, 15)\) is still bounded by that same ball. It misses the corner and the edges, so it is not closed and not compact. A continuous function on the open rectangle can approach a value on the missing edge and never reach it."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Bounded does not imply compact. The open unit disk is the counterexample, and so is \(\{1/n : n = 1, 2, \ldots\}\), which is bounded and misses its limit 0. Closed does not imply compact: the integers are closed in \(\mathbb{R}\) and unbounded. In infinite-dimensional spaces, closed and bounded is no longer enough, so the Euclidean statement should not be copied into a space of functions. A finite set is compact even when the points are far apart. The radius only has to be large enough to cover them."""},
        {"heading": "Where this leads",
         "body_md": r"""Existence of a minimizer is the payoff. On a nonempty compact feasible set, a continuous objective attains its minimum. On an unbounded set the same conclusion needs a coercivity argument, often read off sublevel sets. Classifying stationary points still does not by itself produce a minimizer when the domain fails to be compact. The closed-and-bounded test is the first check."""},
    ]
    save_explainer("compact-sets", "Bounded and compact sets", sections)


def expl_level():
    sections = [
        {"heading": "The idea", "figure": LEVELS, "figure_alt": A_LEVELS,
         "body_md": r"""A function \(f\) of several variables is hard to plot as a surface. Two flat pictures carry most of the shape. The sublevel set at height \(a\), written \(\mathrm{lev}(f, a)\), is every point where \(f(x) \le a\). The contour set, or level set, at height \(a\), written \(\mathrm{con}(f, a)\), is every point where \(f(x) = a\).

For a continuous \(f\), the contour is often the boundary of the sublevel set, and the sublevel set is the contour together with the side where \(f\) is smaller. A test point decides the side. The origin is the usual test point for a function that vanishes there.

The pictures are familiar in the plane. For \(x^2 + y^2\), sublevel sets are closed disks and contours are circles. For a linear function, contours are parallel lines and sublevel sets are closed half-planes. For \(x^2 + 4 y^2\), the contours are ellipses. The height changes the size and, for many functions, not the type of the picture."""},
        {"heading": "Key equations",
         "body_md": r"""\[
\mathrm{lev}(f, a) = \{x : f(x) \le a\}, \qquad \mathrm{con}(f, a) = \{x : f(x) = a\}.
\]
If \(f(x) = \lVert x \rVert_2^2\), then \(\mathrm{lev}(f, a)\) is the closed disk of radius \(\sqrt{a}\) for \(a > 0\), and the contour is the circle of that radius. If \(f(x) = c^T x\), the contour at height \(a\) is a hyperplane and the sublevel set is a closed half-space. A strict sublevel set uses \(<\) and drops the contour."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(x, y) = (x/5)^2 + (y/3)^2\). At height 1 the equality is an ellipse. The semi-axes are 5 and 3: the positive intercepts are \((5, 0)\) and \((0, 3)\). The origin has \(f(0, 0) = 0\), which is below 1, so the sublevel set is the elliptical disk, boundary included.

The point \((5, 0)\) has value 1, so it lies on the contour and also in the sublevel set. The point \((5, 3)\) has value \(1 + 1 = 2\), which is above 1, so it is in neither set at this height. Raising the height above 1 scales both semi-axes by the same factor."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A sublevel set is not the contour. The contour has empty interior for the examples above, while the sublevel set is a filled region. The inequality \(\le\) includes the contour; a strict inequality does not. For \(x^2 + y^2\), the height is the square of the radius, so a height of 16 gives radius 4, not radius 16. A linear contour is a line even when the picture is drawn next to an ellipse from a different function. The test point can fail: if the test point is above the height, the sublevel set is the other side, or it may be empty."""},
        {"heading": "Where this leads",
         "body_md": r"""A planar optimization problem is solved by laying contours of the objective over the feasible set and reading the best height that still touches it. The same pictures, drawn for a linear objective, are the graphical method for a linear program. For existence, a continuous function that grows at infinity has bounded sublevel sets, and those sets are closed, hence compact. A minimum is then attained on each nonempty one."""},
    ]
    save_explainer("level-sets-contours", "Sublevel sets and contour sets", sections)


def expl_convex():
    sections = [
        {"heading": "The idea", "figure": SEG, "figure_alt": A_SEG,
         "body_md": r"""A set is convex when it contains the segment between any two of its points. If \(x\) and \(y\) are in the set and \(t\) is between 0 and 1, the combination \((1-t)x + ty\) has to be in the set. The endpoints themselves are the cases \(t = 0\) and \(t = 1\). Nothing in the definition requires the origin, a bound, or an open interior.

The sets that pass are the ones optimization uses constantly. Every ball of every norm is convex, open or closed. Every half-space is convex, open or closed. Every affine set is convex: subspaces, lines, and hyperplanes. An intersection of any family of convex sets is convex, so a set cut out by several linear inequalities is convex. A union is not safe. Two disks with a gap between them are each convex, and their union is not, because a bridge across the gap leaves both disks.

A finite convex combination stays in a convex set as well. Weights that are nonnegative and sum to 1, on any number of points of the set, produce another point of the set. The two-point definition is the one to check; the finite version follows from it."""},
        {"heading": "Key equations",
         "body_md": r"""\(C\) is convex when \(x, y \in C\) and \(t \in [0, 1]\) imply \((1-t)x + ty \in C\). For a closed half-space,
\[
a^T\bigl((1-t)x + ty\bigr) = (1-t)\, a^T x + t\, a^T y \le (1-t)b + tb = b.
\]
For a ball of a norm, the same combination satisfies the triangle inequality, so the ball is convex. If every set in a family is convex, the intersection is convex."""},
        {"heading": "Worked example",
         "body_md": r"""Consider the half-space \(x_1 + 3 x_2 \le 12\). The point \((6, 0)\) gives left-hand side 6. The point \((0, 4)\) gives 12. Both points belong. Their midpoint is \((3, 2)\), and
\[
3 + 3 \cdot 2 = 9.
\]
The left-hand side is 9, which is still at most 12. The same 9 is the average of 6 and 12, because the constraint is linear: the value at a midpoint is the midpoint of the values. A point such as \((6, 4)\) gives \(6 + 12 = 18\), which is outside. The segment from \((6, 0)\) to \((0, 4)\) never reaches that outside point."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A union of convex sets need not be convex. The argument that each piece contains its own segments forgets segments that jump from one piece to the other. A circle, the boundary of a disk, is not convex: the chord cuts through the interior. Requiring the origin is a different property, and an affine line that misses the origin is still convex. An intersection preserves convexity even when infinitely many sets are involved. A quadratic constraint can destroy it. The disk \(x^2 + y^2 \le 1\) is convex, while the outside \(x^2 + y^2 \ge 1\) is not."""},
        {"heading": "Where this leads",
         "body_md": r"""A polyhedron is an intersection of finitely many half-spaces, hence convex, and its extreme points are the vertices a simplex method uses. The domain of a convex function has to be a convex set, because the chord definition evaluates the function along segments. Over a convex feasible set, a local minimizer of a convex objective is global, and the proof moves along the segment from the local minimizer to any other feasible point."""},
    ]
    save_explainer("convex-sets", "Convex sets", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    bank_induced()
    bank_frobenius()
    bank_open()
    bank_compact()
    bank_level()
    bank_convex()
    expl_induced()
    expl_frobenius()
    expl_open()
    expl_compact()
    expl_level()
    expl_convex()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    banned = ("graz", "boyd", "nocedal", "vandenberghe", "hefferon", "wikibook",
              "textbook", "university", "professor", "lecture", "syllabus", "cambridge", "springer")
    ids = [
        "induced-matrix-norms", "frobenius-schatten-norms", "open-closed-sets",
        "compact-sets", "level-sets-contours", "convex-sets",
    ]
    # Scenarios used only in worked examples. They must not reappear as quiz data.
    private = {
        "induced-matrix-norms": "(8, 0, 0)",
        "frobenius-schatten-norms": "Frobenius norm is 10",
        "open-closed-sets": "radius 6 about",
        "compact-sets": "corner distance is 17",
        "level-sets-contours": "(x/5)^2",
        "convex-sets": "left-hand side is 9",
    }
    bad = False
    for sid in ids:
        exp = json.load(open(os.path.join(root, "skilltree", "explainers", sid + ".json"), encoding="utf-8"))
        n = doc_words(exp["sections"])
        bank = json.load(open(os.path.join(root, "skilltree", "bank", sid + ".json"), encoding="utf-8"))
        blob = json.dumps(exp) + json.dumps(bank)
        hits = [w for w in banned if w in blob.lower()]
        figs = sum(1 for q in bank["questions"] if q.get("figure"))
        deep = sum(1 for q in bank["questions"] if q.get("type") in DEEP_TYPES)
        print(f"{sid}: words {n}, figures {figs}/12, deep {deep}")
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
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
