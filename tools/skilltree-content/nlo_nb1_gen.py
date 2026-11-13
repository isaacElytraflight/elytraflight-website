#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB1 banks and explainers.

Skills: rn-important-subsets, spectral-decomposition, positive-definite-matrices,
singular-value-decomposition, rayleigh-quotient, inner-products, vector-norms-lp,
cauchy-schwarz-inequality.

Closed-form answers live here. skilltree/verify_nlo_nb1.py recomputes them
with numpy and does not import this file.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import (
    ellipse_axes, halfspace_fig, matrix_fig, norm_balls, orthant_fig,
    plane_vectors, segment_fig, simplex_fig,
)
from banklib import Bank, save_explainer

ORTH = orthant_fig("shaded first quadrant")
SIMP = simplex_fig("segment between axis intercepts")
HALF = halfspace_fig("line with one side shaded")
SEG = segment_fig("segment lying on a dashed line")
BALLS = norm_balls("nested unit balls")
ELL = ellipse_axes("axis-aligned ellipse")
AXES = plane_vectors([(1.2, 0, "e1"), (0, 1.2, "e2")], "arrows on the axes")
DIAG = plane_vectors([(1, 1, "u"), (1, -1, "w")], "two diagonal arrows")
ANGLE = plane_vectors([(2, 0.4, "x"), (0.4, 1.6, "y")], "two arrows from one origin")
PERP = plane_vectors([(1.6, 0, "x"), (0, 1.4, "y")], "perpendicular arrows")
RAY = plane_vectors([(1.15, 0, "x"), (2.3, 0, "y")], "two horizontal arrows of different lengths")
MAT_S = matrix_fig([["4", "2"], ["2", "4"]], "symmetric 2 by 2 matrix")
MAT_D = matrix_fig([["3", "0"], ["0", "-4"]], "diagonal matrix with a negative entry")
MAT_R = matrix_fig([["1", "1"], ["0", "0"]], "matrix with a zero row")
MAT_Q = matrix_fig([["1", "2"], ["2", "1"]], "symmetric matrix with a large off-diagonal entry")

A_ORTH = "The closed first quadrant is shaded."
A_SIMP = "A segment joins a positive intercept on each axis."
A_HALF = "A straight boundary, with one side of the plane shaded."
A_SEG = "A solid segment lies on a longer dashed line."
A_BALLS = "A diamond inside a disk inside a square, centered at the origin."
A_ELL = "An axis-aligned ellipse, longer along the first axis."
A_AXES = "Two arrows point along the coordinate axes."
A_DIAG = "Two arrows point along opposite diagonals."
A_ANGLE = "Two arrows leave the origin with a gap between them."
A_PERP = "Two arrows leave the origin at a right angle."
A_RAY = "Two arrows of different lengths point along the positive horizontal axis."
A_MAT_S = "A 2 by 2 matrix with equal diagonal entries and equal off-diagonal entries."
A_MAT_D = "A diagonal 2 by 2 matrix. One diagonal entry is negative."
A_MAT_R = "A 2 by 2 matrix whose second row is zero."
A_MAT_Q = "A symmetric 2 by 2 matrix whose off-diagonal entries exceed the diagonal."


def bank_subsets():
    b = Bank("rn-important-subsets")
    b.mc(1,
         r"Which set is the nonnegative orthant of \(\mathbb{R}^n\)?",
         ["every nonnegative vector whose coordinates sum to 1",
          "every vector of Euclidean length 1",
          "one line through the origin",
          "every vector whose coordinates are all at least zero"],
         3,
         r"The nonnegative orthant is \(\{x : x_i \ge 0 \text{ for every } i\}\). The extra constraint that the coordinates sum to 1 cuts out the unit simplex. Length 1 is a sphere. A line is a one-dimensional affine set.",
         ORTH, A_ORTH)
    b.num(1,
          r"How many vertices does the unit simplex \(\{x \ge 0 : x_1+x_2+x_3 = 1\}\) in \(\mathbb{R}^3\) have?",
          3, "1",
          r"The vertices are the three standard basis vectors. Every other point of the simplex is a convex combination of those three, so it is not extreme. Counting the origin as well would describe a different simplex, the one defined by \(x \ge 0\) and \(x_1+x_2+x_3 \le 1\).",
          SIMP, A_SIMP)
    b.mc(1,
         r"A hyperplane in \(\mathbb{R}^n\) is",
         ["the solution set of two independent inequalities",
          "the unit ball of any norm",
          "the set of all \(m \\times n\) matrices",
          "the solution set of one linear equation \(a^T x = \\beta\) with \(a \\ne 0\)"],
         3,
         r"One nontrivial linear equation cuts the dimension by 1, which is a hyperplane. Two inequalities describe a wedge or a slab. A unit ball is curved. A space of matrices is not that flat subset of \(\mathbb{R}^n\).",
         HALF, A_HALF)
    b.mc(2,
         r"The closed line segment from \(a\) to \(b\) is",
         [r"\(\{a + t(b-a) : t \in \mathbb{R}\}\)",
          r"\(\{a + t(b-a) : t \ge 0\}\)",
          r"\(\{a + t(b-a) : t \in [0,1]\}\)",
          r"\(\{x : \lVert x-a \rVert = \lVert x-b \rVert\}\)"],
         2,
         r"The parameter \(t\) runs from 0 to 1, including the endpoints, so the set is closed and bounded. Every real \(t\) is the whole line. \(t \ge 0\) is the ray that starts at \(a\). Equal distance to \(a\) and \(b\) is the perpendicular bisector.",
         SEG, A_SEG)
    b.num(2,
          r"What is the first coordinate of the midpoint of \((2, 8)\) and \((10, 0)\)?",
          6, "1",
          r"The midpoint is \(\frac12(2+10, 8+0) = (6, 4)\). The first coordinate is 6. The second coordinate is 4, and either endpoint alone would give 2 or 10.",
          SEG, A_SEG)
    b.num(2,
          r"What is the sum of the coordinates of \((0.2, 0.5, 0.3)\)?",
          1, "1",
          r"\(0.2+0.5+0.3 = 1\). Together with the nonnegative coordinates, that sum is what places the point on the unit simplex. A sum of \(0.6\) would fall short of the plane, and a sum of \(2\) would overshoot it.",
          SIMP, A_SIMP)
    b.num(3,
          r"What is the affine dimension of a hyperplane in \(\mathbb{R}^4\)?",
          3, "1",
          r"One independent linear equation reduces dimension by 1, so a hyperplane in \(\mathbb{R}^4\) has dimension 3. Dimension 4 would be the whole space. Dimension 1 would be a line, which needs three independent equations in \(\mathbb{R}^4\).",
          HALF, A_HALF)
    b.mc(3,
         r"A matrix in \(\mathbb{R}^{2 \times 3}\) describes a linear map",
         [r"from \(\mathbb{R}^3\) into \(\mathbb{R}^2\)",
          r"from \(\mathbb{R}^2\) into \(\mathbb{R}^3\)",
          r"from \(\mathbb{R}^2\) into \(\mathbb{R}^2\)",
          r"from \(\mathbb{R}^6\) into \(\mathbb{R}^1\)"],
         0,
         r"Columns are the domain dimension and rows are the codomain dimension. A \(2 \times 3\) matrix sends a 3-vector to a 2-vector. Swapping those dimensions describes a \(3 \times 2\) matrix instead.",
         matrix_fig([["a", "b", "c"], ["d", "e", "f"]], "a 2 by 3 matrix"),
         "A matrix with two rows and three columns.")
    b.num(3,
          r"A point moves from \((0, 0)\) to \((5, 20)\) as the parameter \(t\) runs from 0 to 1. At \(t = 1/5\), what is its second coordinate?",
          4, "1",
          r"The point is \((1-t)\) times the start plus \(t\) times the end. At \(t = 1/5\) the second coordinate is \(20/5 = 4\). The first coordinate is 1. The parameter \(t = 4/5\) would land at second coordinate 16.",
          SEG, A_SEG, version=2)
    b.mc(4,
         r"The set \(\{x : \lVert x \rVert_2 \le 1\}\) is",
         ["an open half-space",
          "a closed unit ball of a norm",
          "a hyperplane",
          "the unit simplex"],
         1,
         r"A norm's closed unit ball is every vector whose norm is at most 1. The inequality is not strict, so the sphere is included. The set is curved, so it is not a hyperplane, and the coordinates of a unit vector need not sum to 1.",
         BALLS, A_BALLS, ["vector-norms-lp"])
    b.num(4,
          r"The segment from \((0,0)\) to \((6,10)\) is the set of convex combinations of its endpoints. What is the second coordinate of the combination with weight \(1/2\) on \((6,10)\)?",
          5, "1",
          r"Weight \(1/2\) is the midpoint \((3, 5)\). The second coordinate is 5. Weight \(1\) would give 10, and the first coordinate of the midpoint is 3.",
          SEG, A_SEG, ["convex-sets"])
    b.mc(4,
         r"A sublevel set of a scalar function \(f\) at height \(a\) is",
         [r"\(\{x : f(x) = a\}\)",
          r"the domain of \(f\)",
          r"\(\{x : f(x) \le a\}\)",
          "a hyperplane for every choice of \(f\)"],
         2,
         r"The sublevel set keeps every point whose value is at most \(a\). The equality \(f(x) = a\) is a level set, or contour. The domain is where \(f\) is defined, not where it is small. Only special functions have flat sublevel sets.",
         HALF, A_HALF, ["level-sets-contours"])
    b.save()


def bank_spectral():
    b = Bank("spectral-decomposition")
    b.mc(1,
         r"A real symmetric matrix",
         ["has real eigenvalues and an orthonormal basis of eigenvectors",
          "can have a non-real eigenvalue",
          "must have 0 as an eigenvalue",
          "must already be diagonal"],
         0,
         r"A real symmetric matrix is orthogonally diagonalizable over the reals, so its eigenvalues are real and its eigenvectors can be chosen orthonormal. A non-real eigenvalue can occur for a real matrix that is not symmetric. The identity is symmetric and its only eigenvalue is 1. Symmetry allows nonzero off-diagonal entries.",
         MAT_S, A_MAT_S)
    b.num(1,
          r"What is the larger eigenvalue of \(A = \begin{bmatrix} 4 & 2 \\ 2 & 4 \end{bmatrix}\)?",
          6, "1",
          r"The characteristic polynomial is \(\lambda^2 - 8\lambda + 12 = (\lambda-6)(\lambda-2)\). The larger root is 6. The trace 8 is the sum of the two eigenvalues, the determinant 12 is their product, and 4 is a diagonal entry rather than an eigenvalue.",
          MAT_S, A_MAT_S)
    b.mc(1,
         r"If the columns of \(U\) are orthonormal eigenvectors of a symmetric matrix \(A\), and \(D\) holds the eigenvalues, then",
         [r"\(A = U + D\)",
          r"\(A = D U\), with no further factor",
          r"\(A = U D\) and the transpose is optional",
          r"\(A = U D U^T\)"],
         3,
         r"Orthonormal columns mean \(U^{-1} = U^T\), so the factorization is \(A = U D U^T\). Adding \(U\) and \(D\) is not a change of basis. Dropping \(U^T\) leaves the coordinates in the eigenbasis.",
         DIAG, A_DIAG)
    b.mc(2,
         r"For \(A = \begin{bmatrix} 4 & 2 \\ 2 & 4 \end{bmatrix}\), the vector \((1,-1)\)",
         ["is not an eigenvector, because its entries differ",
          "is an eigenvector with eigenvalue 6",
          "is an eigenvector with eigenvalue 4",
          "is an eigenvector with eigenvalue 2"],
         3,
         r"\(A(1,-1) = (2,-2) = 2(1,-1)\). The eigenvalue 6 belongs to \((1,1)\), since \(A(1,1) = (6,6)\). The diagonal entry 4 is not that stretch factor.",
         DIAG, A_DIAG)
    b.num(2,
          r"What is \(\det A\) for \(A = \begin{bmatrix} 4 & 2 \\ 2 & 4 \end{bmatrix}\)?",
          12, "1",
          r"\(\det A = 16 - 4 = 12\), which is also the product of the eigenvalues 6 and 2. The trace is 8, and the off-diagonal entry 2 is not the determinant.",
          MAT_S, A_MAT_S)
    b.num(2,
          r"What is the trace of \(A = \begin{bmatrix} 4 & 2 \\ 2 & 4 \end{bmatrix}\)?",
          8, "1",
          r"The trace is \(4+4 = 8\), the same as the sum of the eigenvalues 6 and 2. Their difference is 4, and the off-diagonal entries are not part of the trace.",
          MAT_S, A_MAT_S)
    b.mc(3,
         r"In the factorization \(A = U D U^T\) of a symmetric matrix, the three factors",
         ["translate the vector, then stretch it",
          "stretch in the original coordinates, then rotate twice the same way",
          "add the eigenvalues to the vector",
          "rotate into the eigenbasis, stretch each coordinate by its eigenvalue, and rotate back"],
         3,
         r"\(U^T\) writes the vector in the eigenbasis, \(D\) multiplies each coordinate by its eigenvalue, and \(U\) returns to the original coordinates. There is no translation. Unequal eigenvalues stretch different directions by different factors.",
         DIAG, A_DIAG)
    b.num(3,
          r"Let \(A = \begin{bmatrix} 5 & 0 \\ 0 & 1 \end{bmatrix}\) and \(x = (2, 0)\). What is \(x^T A x\)?",
          20, "1",
          r"Only the first coordinate is nonzero, so \(x^T A x = 5 \cdot 2^2 = 20\). Using the other eigenvalue would give 4. Forgetting to square the coordinate would give 10.",
          AXES, A_AXES)
    b.num(3,
          r"For \(A = \begin{bmatrix} 5 & 0 \\ 0 & 1 \end{bmatrix}\), what eigenvalue belongs to \((0,1)\)?",
          1, "1",
          r"\(A(0,1) = (0,1)\), so the eigenvalue is 1. The other diagonal entry, 5, belongs to \((1,0)\). The trace 6 is the sum of the two eigenvalues.",
          AXES, A_AXES)
    b.mc(4,
         r"A symmetric matrix is positive definite when",
         ["its trace is positive, even if an eigenvalue is negative",
          "every eigenvalue is positive",
          "its determinant is positive and nothing else is required",
          "every entry is positive"],
         1,
         r"For a symmetric matrix, positive definiteness is exactly the condition that every eigenvalue is positive. A positive trace or a positive determinant can hold while an eigenvalue is negative. Positive entries do not control the eigenvalues.",
         ELL, A_ELL, ["positive-definite-matrices"])
    b.num(4,
          r"The symmetric matrix \(A = \begin{bmatrix} 4 & 2 \\ 2 & 4 \end{bmatrix}\) has eigenvalues 6 and 2, both positive. What is its largest singular value?",
          6, "1",
          r"On a positive semidefinite matrix the singular values are the eigenvalues. The largest is 6. The smaller eigenvalue 2 is the other singular value, and the trace 8 is not a singular value.",
          MAT_S, A_MAT_S, ["singular-value-decomposition"])
    b.mc(4,
         r"The Rayleigh quotient \(x^T A x / x^T x\) of a symmetric matrix, evaluated at an eigenvector,",
         ["equals the trace",
          "equals the determinant",
          "equals that eigenvector's eigenvalue",
          "equals 0 for every symmetric matrix"],
         2,
         r"If \(Ax = \lambda x\) and \(x \ne 0\), then \(x^T A x = \lambda\, x^T x\), so the quotient equals \(\lambda\). The trace and the determinant are the sum and the product of all the eigenvalues, not the value on one eigenvector.",
         DIAG, A_DIAG, ["rayleigh-quotient"])
    b.save()


def bank_pd():
    b = Bank("positive-definite-matrices")
    b.mc(1,
         r"A symmetric matrix \(A\) is positive definite when",
         [r"\(x^T A x > 0\) for every \(x \ne 0\)",
          r"\(\det A > 0\), with no other condition",
          "every entry of \(A\) is positive",
          "the trace of \(A\) is positive and nothing else is required"],
         0,
         r"Positive definite means the quadratic form is positive on every nonzero vector. In dimension 2, \(\det A > 0\) also holds for a negative definite matrix. Positive entries and a positive trace do not rule out a negative eigenvalue.",
         ELL, A_ELL)
    b.num(1,
          r"Let \(A = \begin{bmatrix} 2 & 0 \\ 0 & 8 \end{bmatrix}\). What is \((1,1)^T A (1,1)\)?",
          10, "1",
          r"The form is \(2\cdot 1^2 + 8\cdot 1^2 = 10\). Either diagonal entry alone would give 2 or 8. The Euclidean squared length of \((1,1)\) is 2, which ignores the matrix.",
          ELL, A_ELL)
    b.mc(1,
         r"For a symmetric matrix, the eigenvalue test says the matrix is positive definite exactly when",
         ["at least one eigenvalue is positive",
          "the eigenvalues sum to zero",
          "the matrix has a zero eigenvalue",
          "every eigenvalue is positive"],
         3,
         r"The quadratic form is a sum of \(\lambda_i y_i^2\) in the eigenbasis, so it stays positive for every nonzero vector exactly when every \(\lambda_i\) is positive. One positive eigenvalue is not enough. A zero eigenvalue makes the form only semidefinite.",
         AXES, A_AXES)
    b.mc(2,
         r"The symmetric matrix \(\begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}\) is",
         ["positive definite, because the trace is positive",
          "positive semidefinite, because the diagonal entries are positive",
          "indefinite, because its eigenvalues have opposite signs",
          "negative definite, because the off-diagonal entries are the larger ones"],
         2,
         r"The characteristic polynomial is \(\lambda^2 - 2\lambda - 3 = (\lambda-3)(\lambda+1)\). The eigenvalues are 3 and \(-1\), so the form takes both signs. A positive trace or a positive diagonal does not prevent the negative eigenvalue.",
         MAT_Q, A_MAT_Q)
    b.num(2,
          r"What is the smaller eigenvalue of \(\begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}\)?",
          -1, "1",
          r"The roots of \(\lambda^2 - 2\lambda - 3 = 0\) are 3 and \(-1\). The smaller one is \(-1\). The trace 2 is their sum, and the diagonal entry 1 is neither eigenvalue.",
          MAT_Q, A_MAT_Q)
    b.num(2,
          r"What is the determinant of \(\begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}\)?",
          -3, "1",
          r"\(\det = 1 - 4 = -3\), the product of the eigenvalues 3 and \(-1\). The trace is 2. A positive determinant would have required both eigenvalues to share a sign.",
          MAT_Q, A_MAT_Q)
    b.mc(3,
         r"If \(A\) is symmetric positive definite, a level set \(x^T A x = c\) with \(c > 0\) is",
         ["a hyperbola opening along an eigenvector",
          "a pair of lines through the origin",
          "a square aligned with the coordinate axes",
          "an ellipse whose axes lie along the eigenvectors"],
         3,
         r"In the eigenbasis the equation is a sum of \(\lambda_i y_i^2 = c\) with every \(\lambda_i > 0\), which is an ellipsoid. Opposite signs would give a hyperbola. A zero eigenvalue would drop a square term and flatten the set.",
         ELL, A_ELL)
    b.num(3,
          r"The level set \(2 x_1^2 + 8 x_2^2 = 8\) is an ellipse. What is its semi-axis length along \(x_1\)?",
          2, "1",
          r"Divide by 8 to get \(x_1^2/4 + x_2^2/1 = 1\). The semi-axis along \(x_1\) is 2, and the one along \(x_2\) is 1. Swapping them uses the coefficient 8 as if it were the squared length.",
          ELL, A_ELL)
    b.num(3,
          r"Let \(A = \begin{bmatrix} 1 & 0 \\ 0 & 0 \end{bmatrix}\). What is \((3,4)^T A (3,4)\)?",
          9, "1",
          r"\(x^T A x = x_1^2 = 9\). The second coordinate is multiplied by the zero eigenvalue, which is why the form can vanish for a nonzero vector. The squared Euclidean length \(9+16 = 25\) would be the form of the identity, not of this \(A\).",
          AXES, A_AXES)
    b.num(4,
          r"A quadratic \(f(x) = \frac12 x^T A x\) with symmetric \(A\) is convex when \(A\) is positive semidefinite. For \(A = \begin{bmatrix} 9 & 0 \\ 0 & 4 \end{bmatrix}\), what is the smallest eigenvalue?",
          4, "1",
          r"A diagonal matrix lists its eigenvalues on the diagonal. The smaller one is 4, and both are positive, so \(A\) is positive definite and the quadratic is strictly convex. The trace 13 is the sum, not the smaller eigenvalue.",
          ELL, A_ELL, ["convexity-second-order"])
    b.mc(4,
         r"If \(D\) is symmetric positive definite and \(g \ne 0\), the direction \(d = -D g\) satisfies",
         [r"\(g^T d = 0\)",
          r"\(g^T d < 0\)",
          r"\(g^T d > 0\)",
          r"\(D d = 0\)"],
         1,
         r"\(g^T d = -g^T D g < 0\) because \(D\) is positive definite and \(g \ne 0\). That negative directional derivative is what makes \(d\) a descent direction. Orthogonality would give 0, and \(Dd = 0\) would say \(d\) is a null vector.",
         AXES, A_AXES, ["descent-directions"])
    b.mc(4,
         r"The pairing \(\langle u, v \rangle = u^T A v\) is an inner product on \(\mathbb{R}^n\) when the symmetric matrix \(A\) is",
         ["singular",
          "indefinite",
          "positive definite",
          "negative semidefinite"],
         2,
         r"An inner product must give \(\langle u, u \rangle > 0\) for every \(u \ne 0\), which is positive definiteness of \(A\). A singular or indefinite matrix makes the square zero or negative for some nonzero vector. A negative semidefinite matrix reverses the sign.",
         ELL, A_ELL, ["gram-schmidt-orthogonalization"])
    b.save()


def bank_svd():
    b = Bank("singular-value-decomposition")
    b.mc(1,
         r"A full singular value decomposition of an \(m \times n\) matrix \(A\) writes",
         [r"\(A = U \Sigma V^T\) with orthogonal \(U\) and \(V\) and a rectangular diagonal \(\Sigma\)",
          r"\(A = U \Sigma U^T\) for every \(A\), symmetric or not",
          r"\(A = V \Sigma\) with no third factor",
          r"\(A = U + \Sigma + V\)"],
         0,
         r"The full decomposition uses square orthogonal factors on both sides and puts the singular values on the diagonal of a rectangular middle factor. \(U \Sigma U^T\) is a spectral factorization, and it needs symmetry. A sum of the three factors is not a factorization.",
         MAT_D, A_MAT_D)
    b.num(1,
          r"What is the largest singular value of \(A = \begin{bmatrix} 3 & 0 \\ 0 & -4 \end{bmatrix}\)?",
          4, "1",
          r"\(A^T A = \mathrm{diag}(9, 16)\), so the singular values are 3 and 4. The largest is 4. The signed eigenvalue \(-4\) keeps a sign that singular values drop. The sum \(3+4 = 7\) is not a singular value.",
          MAT_D, A_MAT_D)
    b.mc(1,
         r"The singular values of \(A\) are",
         ["the eigenvalues of \(A\), including any negative ones",
          "the diagonal entries of \(A\), whether or not \(A\) is diagonal",
          "the row sums of \(A\)",
          "the square roots of the eigenvalues of \(A^T A\)"],
         3,
         r"\(A^T A\) is symmetric positive semidefinite, and the singular values are the square roots of its eigenvalues. Eigenvalues of a nonsymmetric, or signed diagonal, matrix can be negative, so they are not the singular values. Diagonal entries and row sums are different summaries.",
         MAT_D, A_MAT_D)
    b.num(2,
          r"How many nonzero singular values does \(C = \begin{bmatrix} 1 & 1 \\ 0 & 0 \end{bmatrix}\) have?",
          1, "1",
          r"\(C^T C = \begin{bmatrix} 1 & 1 \\ 1 & 1 \end{bmatrix}\) has eigenvalues 2 and 0, so one singular value is positive. That count is the rank. Counting both columns would give 2, which ignores the dependence between them.",
          MAT_R, A_MAT_R)
    b.mc(2,
         r"The geometry of \(A = U \Sigma V^T\) is",
         ["a translation, then a stretch",
          "a stretch along the original axes only",
          "a rotation by \(V^T\), a stretch by the singular values, then a rotation by \(U\)",
          "a single rotation, with no stretch"],
         2,
         r"\(V^T\) changes to the right singular basis, \(\Sigma\) stretches those axes, and \(U\) rotates into the output coordinates. There is no translation. Omitting the stretch would preserve every length.",
         AXES, A_AXES)
    b.num(2,
          r"What is the largest singular value of \(C = \begin{bmatrix} 1 & 1 \\ 0 & 0 \end{bmatrix}\)?",
          math.sqrt(2), "1",
          r"The nonzero eigenvalue of \(C^T C\) is 2, so the singular value is \(\sqrt{2}\). The Frobenius norm \(\sqrt{2}\) happens to agree here because the other singular value is 0. Reporting the eigenvalue 2 skips the square root.",
          MAT_R, A_MAT_R)
    b.mc(3,
         r"The rank of a matrix equals",
         ["the number of rows, even if a row is zero",
          "the number of negative eigenvalues of \(A\)",
          "the product of the singular values",
          "the number of nonzero singular values"],
         3,
         r"Each positive singular value contributes an independent row and column direction. Zero singular values are the dimensions that collapse. A zero row means the rank is smaller than the row count. The product of the singular values is zero whenever the rank is deficient, so the product does not equal the rank.",
         MAT_R, A_MAT_R)
    b.num(3,
          r"For \(A = \begin{bmatrix} 3 & 0 \\ 0 & -4 \end{bmatrix}\), what is the sum of the squares of the singular values?",
          25, "1",
          r"The singular values are 3 and 4, and \(9+16 = 25\). That sum is also the squared Frobenius norm, the sum of the squares of the entries. The product \(12\) and the signed product of the eigenvalues, \(-12\), are different.",
          MAT_D, A_MAT_D)
    b.num(3,
          r"What is the product of the two singular values of \(A = \begin{bmatrix} 3 & 0 \\ 0 & -4 \end{bmatrix}\)?",
          12, "1",
          r"The singular values are 4 and 3, and their product is 12. The product of the eigenvalues is \(3 \cdot (-4) = -12\), which keeps a sign the singular values remove. The sum of the singular values is 7.",
          MAT_D, A_MAT_D)
    b.num(4,
          r"The matrix 2-norm is the largest singular value. What is \(\lVert A \rVert_2\) for \(A = \begin{bmatrix} 3 & 0 \\ 0 & -4 \end{bmatrix}\)?",
          4, "1",
          r"The singular values are 4 and 3, so the operator 2-norm is 4. The smaller singular value 3 is not the operator norm. The Frobenius norm is 5, the square root of \(9+16\).",
          MAT_D, A_MAT_D, ["induced-matrix-norms"])
    b.mc(4,
         r"The squared Frobenius norm of a matrix equals",
         ["the largest singular value",
          "the sum of the squares of the singular values",
          "the product of the singular values",
          "the smallest singular value"],
         1,
         r"Both the entrywise sum of squares and the sum of \(\sigma_i^2\) equal \(\lVert A \rVert_F^2\). The largest singular value is the 2-norm, not the Frobenius norm. The product vanishes whenever a singular value does, even if the matrix is not zero.",
         MAT_D, A_MAT_D, ["frobenius-schatten-norms"])
    b.mc(4,
         r"If a coefficient matrix in a least-squares problem has a zero singular value, then",
         ["the columns are independent and the minimizer is unique",
          "every residual can be made zero",
          "the columns are dependent, so a minimizer need not be unique",
          "the matrix is square and invertible"],
         2,
         r"A zero singular value means a nontrivial null vector, so the columns are dependent. Adding that null vector does not change \(Ax\), and the least-squares minimizer is a whole affine space. Independent columns are exactly the case of a positive smallest singular value.",
         MAT_R, A_MAT_R, ["linear-least-squares"])
    b.save()


def bank_rayleigh():
    b = Bank("rayleigh-quotient")
    b.mc(1,
         r"For a real symmetric matrix \(A\), the Rayleigh quotient \(R(x) = x^T A x / x^T x\) satisfies",
         [r"\(\lambda_{\min} \le R(x) \le \lambda_{\max}\) for every \(x \ne 0\)",
          r"\(R(x)\) is larger than every eigenvalue",
          r"\(R(x) = 0\) for every unit vector",
          r"\(R(x)\) depends on the length of \(x\)"],
         0,
         r"In the eigenbasis the quotient is a weighted average of the eigenvalues, so it lies between the smallest and the largest. It equals an extreme eigenvalue at the matching eigenvector, not beyond it. Scaling \(x\) cancels in the fraction.",
         ELL, A_ELL)
    b.num(1,
          r"Let \(A = \begin{bmatrix} 4 & 0 \\ 0 & 1 \end{bmatrix}\). What is \(R(1,1)\)?",
          2.5, "1",
          r"\(x^T A x = 4+1 = 5\) and \(x^T x = 2\), so \(R = 5/2 = 2.5\). The larger eigenvalue 4 is the maximum, not the value at \((1,1)\). Forgetting to divide by \(x^T x\) leaves 5.",
          AXES, A_AXES)
    b.mc(1,
         r"On a symmetric matrix, the upper bound \(\lambda_{\max}\) of the Rayleigh quotient is attained",
         ["at every vector of length 1",
          "at an eigenvector belonging to \(\lambda_{\max}\)",
          "only at the zero vector",
          "at a vector orthogonal to every eigenvector"],
         1,
         r"The weighted average of the eigenvalues equals the largest one only when all the weight sits on that eigenvalue, which is the corresponding eigenspace. The zero vector is excluded because the quotient divides by \(x^T x\). A generic unit vector lands strictly between the extremes when the eigenvalues differ.",
         DIAG, A_DIAG)
    b.num(2,
          r"What is the trace of \(\begin{bmatrix} 5 & 1 \\ 1 & 3 \end{bmatrix}\)? The trace equals the sum of the eigenvalues.",
          8, "1",
          r"The trace is \(5+3 = 8\). The off-diagonal entries cancel out of the trace. The determinant is \(15-1 = 14\), the product of the eigenvalues rather than their sum.",
          matrix_fig([["5", "1"], ["1", "3"]], "a symmetric matrix with trace equal to the sum of its diagonal"),
          "A symmetric 2 by 2 matrix with diagonal entries 5 and 3.")
    b.mc(2,
         r"For a symmetric matrix, the determinant equals",
         ["the sum of the eigenvalues",
          "the largest eigenvalue",
          "the product of the eigenvalues",
          "the Rayleigh quotient of the all-ones vector"],
         2,
         r"The characteristic polynomial's constant term makes the determinant the product of the eigenvalues, while the trace is their sum. The Rayleigh quotient of one vector is a single weighted average, not the product.",
         MAT_S, A_MAT_S)
    b.num(2,
          r"What is \(\det \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}\)?",
          3, "1",
          r"\(\det = 4-1 = 3\), the product of the eigenvalues 3 and 1. The trace is 4, the sum of those eigenvalues. The off-diagonal entry 1 is not the determinant.",
          matrix_fig([["2", "1"], ["1", "2"]], "a symmetric matrix"),
          "A symmetric 2 by 2 matrix with 2s on the diagonal.")
    b.mc(3,
         r"Replacing \(x\) by \(3x\) in the Rayleigh quotient",
         ["multiplies the quotient by 3",
          "multiplies the quotient by 9",
          "changes the sign",
          "leaves the quotient unchanged"],
         3,
         r"Both \(x^T A x\) and \(x^T x\) scale by \(9\), so the ratio is invariant. Multiplying by 3 or by 9 would be right for the numerator or the denominator alone, not for the quotient.",
         ANGLE, A_ANGLE)
    b.num(3,
          r"Let \(A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}\). What is \(R(1,0)\)?",
          2, "1",
          r"\(A(1,0) = (2,1)\), so \(x^T A x = 2\) and \(x^T x = 1\). The quotient is 2. The eigenvalues are 3 and 1, and this vector is neither eigenvector. The determinant 3 is the product of the eigenvalues.",
          AXES, A_AXES)
    b.num(3,
          r"For \(A = \begin{bmatrix} 4 & 0 \\ 0 & 1 \end{bmatrix}\), what is \(\lambda_{\max} - \lambda_{\min}\)?",
          3, "1",
          r"The eigenvalues are the diagonal entries 4 and 1, so the gap is 3. Their ratio is 4, and their sum is 5. The gap is the width of the interval that contains every Rayleigh quotient.",
          AXES, A_AXES)
    b.num(4,
          r"For a symmetric positive definite matrix the condition number in the 2-norm is \(\lambda_{\max}/\lambda_{\min}\). What is that ratio for eigenvalues 4 and 1?",
          4, "1",
          r"\(4/1 = 4\). The difference \(3\) is the gap, not the ratio used in the convergence bound for steepest descent. The trace 5 is the sum.",
          ELL, A_ELL, ["condition-number-gradient-rate"])
    b.mc(4,
         r"Power iteration on a symmetric matrix can be read as a method that",
         ["drives the Rayleigh quotient up toward \(\lambda_{\max}\)",
          "computes the determinant in one matrix-vector product",
          "returns a vector orthogonal to the leading eigenvector",
          "applies only to matrices with a zero eigenvalue"],
         0,
         r"Each multiplication by \(A\) emphasizes the largest-eigenvalue component, and the Rayleigh quotient of the resulting vector climbs toward \(\lambda_{\max}\). One product does not yield the determinant. The iteration looks for the leading direction, not a vector orthogonal to it.",
         DIAG, A_DIAG, ["power-method-eigenvector"])
    b.mc(4,
         r"On a strongly convex quadratic, a large spread of eigenvalues makes steepest descent slow. A method that avoids that zigzag by taking conjugate directions is",
         ["a single gradient step of fixed length",
          "the conjugate gradient method",
          "evaluation of the trace",
          "replacement of the matrix by its determinant"],
         1,
         r"Conjugate gradient builds directions that are conjugate in the Hessian inner product and finishes a quadratic in finitely many steps. One gradient step does not cancel the zigzag. The trace and the determinant summarize the eigenvalues but do not generate the directions.",
         ANGLE, A_ANGLE, ["conjugate-gradient-method"])
    b.save()


def bank_inner():
    b = Bank("inner-products")
    b.mc(1,
         r"Which list matches the inner-product axioms on a real vector space?",
         ["symmetry, linearity in the first argument, and \(\\langle x,x \\rangle > 0\) for \(x \\ne 0\)",
          "symmetry, and \(\\langle x,x \\rangle = 0\) for every \(x\)",
          "linearity, but \(\\langle x,y \\rangle = -\\langle y,x \\rangle\)",
          "\(\\langle x,x \\rangle > 0\), with no linearity requirement"],
         0,
         r"A real inner product is symmetric, linear in each slot, and positive on nonzero vectors. Forcing every square to zero destroys positive definiteness. Skew-symmetry would make \(\langle x,x \rangle = 0\). Positivity alone does not give the angle formula.",
         ANGLE, A_ANGLE)
    b.num(1,
          r"What is the dot product \((1,2,3)\cdot(2,0,-1)\)?",
          -1, "1",
          r"\(1\cdot 2 + 2\cdot 0 + 3\cdot(-1) = 2-3 = -1\). Dropping the last term leaves 2. Adding the absolute values gives 6, which is not the dot product.",
          ANGLE, A_ANGLE)
    b.mc(1,
         r"Two nonzero vectors are orthogonal when",
         ["they have the same length",
          "their inner product is zero",
          "their sum has length 1",
          "each has integer coordinates"],
         1,
         r"Orthogonality is \(\langle x, y \rangle = 0\). Equal length is a different condition, and the Cauchy-Schwarz equality case is about parallel vectors, not orthogonal ones. Integer coordinates say nothing about the angle.",
         PERP, A_PERP)
    b.num(2,
          r"The Frobenius inner product sums the products of matching entries. For \(A = \begin{bmatrix} 1 & 0 \\ 2 & 3 \end{bmatrix}\) and \(B = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}\), what is \(\langle A, B \rangle_F\)?",
          4, "1",
          r"The entrywise products are \(1, 0, 0, 3\), and they sum to 4. The same value is \(\mathrm{tr}(A^T B)\). Multiplying the determinants, \(3 \cdot 1 = 3\), is a different operation.",
          matrix_fig([["1", "0"], ["2", "3"]], "a 2 by 2 matrix"),
          "A 2 by 2 matrix with a zero in the first row.")
    b.mc(2,
         r"The cosine of the angle between two nonzero vectors is",
         [r"\(\langle x,y \rangle\)",
          r"\(\lVert x \rVert\,\lVert y \rVert\)",
          r"\(\langle x,y \rangle / (\lVert x \rVert\,\lVert y \rVert)\)",
          r"\(\lVert x+y \rVert\)"],
         2,
         r"The angle formula divides the inner product by the product of the lengths. The inner product alone still carries the lengths. The product of the lengths is the Cauchy-Schwarz upper bound, not the cosine. The length of the sum is the triangle inequality's subject.",
         ANGLE, A_ANGLE)
    b.num(2,
          r"What is \((3,4)\cdot(4,3)\)?",
          24, "1",
          r"\(3\cdot 4 + 4\cdot 3 = 24\). Each vector has length 5, so the product of the lengths is 25, which is the Cauchy-Schwarz bound rather than the inner product. The difference of the coordinates would not produce 24.",
          ANGLE, A_ANGLE)
    b.mc(3,
         r"The Frobenius inner product of two real matrices of the same shape equals",
         ["the product of their determinants",
          "the product of their traces",
          "the largest entry of either matrix",
          r"\(\mathrm{tr}(A^T B)\), the sum of the entrywise products"],
         3,
         r"Summing \(a_{ij} b_{ij}\) is the trace of \(A^T B\). Determinants and traces multiply different summaries of the two matrices. The largest entry ignores every other pair.",
         MAT_S, A_MAT_S)
    b.num(3,
          r"The 2-norm is the square root of the dot product of a vector with itself. What is \(\lVert(3,4)\rVert_2\)?",
          5, "1",
          r"\(\langle x,x \rangle = 9+16 = 25\), so the length is 5. The 1-norm is \(3+4 = 7\). Reporting 25 skips the square root.",
          ANGLE, A_ANGLE)
    b.num(3,
          r"The pairing \(x_1 y_1 - x_2 y_2\) is not an inner product. What value does it give on the second standard basis vector with itself?",
          -1, "1",
          r"The second term flips sign, so the pairing of \((0,1)\) with itself is \(-1\). An inner product would be positive. The ordinary dot product of that vector with itself is \(+1\), which is the sign this formula loses.",
          PERP, A_PERP)
    b.num(4,
          r"Cauchy-Schwarz says \(\lvert(3,4)\cdot(4,3)\rvert\) cannot exceed the product of the lengths. What is that product of lengths?",
          25, "1",
          r"Each vector has length \(\sqrt{9+16} = 5\), so the product is 25. The inner product itself is 24, strictly below the bound, because the vectors are not parallel.",
          ANGLE, A_ANGLE, ["cauchy-schwarz-inequality"])
    b.mc(4,
         r"Gram-Schmidt removes from a new vector the part parallel to the vectors already kept. That parallel part is a multiple of",
         ["the determinant of the two vectors",
          r"\(\langle v, u \rangle / \langle u, u \rangle\) times \(u\)",
          "the sum \(u+v\), regardless of the inner product",
          "a vector orthogonal to every later vector, chosen in advance"],
         1,
         r"The coefficient of \(u\) in \(v\) is the inner product \(\langle v, u \rangle\) divided by \(\langle u, u \rangle\). Subtracting that multiple leaves a vector orthogonal to \(u\). The determinant is an area, not the coefficient. Adding \(u\) and \(v\) does not cancel the parallel part.",
         ANGLE, A_ANGLE, ["gram-schmidt-orthogonalization"])
    b.mc(4,
         r"Directions \(d_i, d_j\) are conjugate for a symmetric positive definite \(Q\) when",
         [r"\(d_i + d_j = 0\)",
          r"\(d_i^T d_j = 1\)",
          r"\(d_i^T Q d_j = 0\)",
          r"\(Q\) is a multiple of the identity and nothing else is true"],
         2,
         r"Conjugacy is orthogonality in the inner product \(\langle u, v \rangle_Q = u^T Q v\). Ordinary orthogonality is the special case \(Q = I\). Opposite directions are linearly dependent, not conjugate, and a dot product of 1 is not the conjugacy condition.",
         PERP, A_PERP, ["q-conjugate-directions"])
    b.save()


def bank_norms():
    b = Bank("vector-norms-lp")
    b.mc(1,
         r"A norm on \(\mathbb{R}^n\) must satisfy",
         [r"\(\lVert x \rVert > 0\) for \(x \ne 0\), \(\lVert c x \rVert = \lvert c \rvert\,\lVert x \rVert\), and the triangle inequality",
          r"\(\lVert x+y \rVert = \lVert x \rVert + \lVert y \rVert\) for every pair",
          r"\(\lVert x \rVert = 0\) for some \(x \ne 0\)",
          r"\(\lVert c x \rVert = c\,\lVert x \rVert\) even when \(c\) is negative"],
         0,
         r"The axioms are positivity, absolute homogeneity, and the triangle inequality. Equality in the triangle inequality is special, not required for every pair. A nonzero vector in the kernel would break positivity. A negative scalar must come out as its absolute value, or the norm could be negative.",
         BALLS, A_BALLS)
    b.num(1,
          r"What is the 1-norm of \((3,-4)\)?",
          7, "1",
          r"\(\lvert 3 \rvert + \lvert -4 \rvert = 7\). The 2-norm is 5, and the infinity-norm is 4. Subtracting the coordinates gives \(-1\), which is not a norm.",
          AXES, A_AXES)
    b.mc(1,
         r"In the plane, the unit balls of the 1-norm, the 2-norm, and the infinity-norm are",
         ["three disks of different radii",
          "a diamond, a disk, and a square",
          "a square, a diamond, and a hyperbola",
          "a single square used for all three"],
         1,
         r"The 1-norm ball is a diamond with vertices on the axes, the 2-norm ball is the round disk, and the infinity-norm ball is the square aligned with the axes. The same radius does not make those three sets coincide. A hyperbola is unbounded, so it cannot be a unit ball.",
         BALLS, A_BALLS)
    b.num(2,
          r"What is the 2-norm of \((3,-4)\)?",
          5, "1",
          r"\(\sqrt{3^2 + (-4)^2} = \sqrt{25} = 5\). The 1-norm is 7, and the infinity-norm is 4. Reporting 25 skips the square root.",
          AXES, A_AXES)
    b.mc(2,
         r"The infinity-norm of a vector is",
         ["the sum of the absolute values of the coordinates",
          "the square root of the sum of squares",
          "the largest absolute coordinate",
          "the product of the coordinates"],
         2,
         r"\(\lVert x \rVert_\infty = \max_i \lvert x_i \rvert\). The sum of absolute values is the 1-norm, and the square root of the sum of squares is the 2-norm. A product is not a norm: it vanishes when any coordinate does.",
         BALLS, A_BALLS)
    b.num(2,
          r"What is the infinity-norm of \((3,-4)\)?",
          4, "1",
          r"The larger absolute coordinate is 4. The 1-norm is 7 and the 2-norm is 5. Averaging the absolute coordinates gives 3.5, which is none of the three norms.",
          AXES, A_AXES)
    b.mc(3,
         r"On a finite-dimensional space, any two norms are equivalent. That means",
         ["the two norms give the same number on every vector",
          "one of them must be the infinity-norm",
          "their unit balls are identical",
          "each is bounded by a constant times the other, and the constants may depend on the dimension"],
         3,
         r"Equivalence is a two-sided comparison with constants, not equality. The 1-norm and the infinity-norm differ on \((1,1)\). Their unit balls have different shapes. The constants grow with dimension: \(\lVert x \rVert_1 \le n \lVert x \rVert_\infty\).",
         BALLS, A_BALLS)
    b.num(3,
          r"What is the 1-norm of \((1,1,1)\)?",
          3, "1",
          r"Three absolute values of 1 sum to 3. The 2-norm is \(\sqrt{3}\), and the infinity-norm is 1. The comparison \(\lVert x \rVert_1 \le \sqrt{n}\,\lVert x \rVert_2\) holds with equality here, since both sides equal 3.",
          AXES, A_AXES)
    b.num(3,
          r"What is the 2-norm of \((1,-1,0)\)?",
          math.sqrt(2), "1",
          r"\(\sqrt{1+1+0} = \sqrt{2}\). The 1-norm is 2, and the infinity-norm is 1. Squaring the 2-norm gives 2, which is the 1-norm of this particular vector, not the 2-norm.",
          AXES, A_AXES)
    b.mc(4,
         r"Cauchy-Schwarz bounds an inner product by the product of 2-norms. One consequence used to prove the triangle inequality is",
         [r"\(\langle x, y \rangle \le \lVert x \rVert_2\,\lVert y \rVert_2\)",
          r"\(\lVert x \rVert_1 = \lVert x \rVert_\infty\) for every \(x\)",
          r"every norm comes from an inner product",
          r"the infinity-norm fails the triangle inequality"],
         0,
         r"The inequality \(\langle x, y \rangle \le \lVert x \rVert_2 \lVert y \rVert_2\) turns \(\lVert x+y \rVert_2^2 = \lVert x \rVert_2^2 + \lVert y \rVert_2^2 + 2\langle x,y \rangle\) into a perfect square. The 1-norm and the infinity-norm are not equal in general. The 1-norm does not come from an inner product, and it still satisfies the triangle inequality.",
         ANGLE, A_ANGLE, ["cauchy-schwarz-inequality"])
    b.num(4,
          r"For \(x = (3,-4)\), the 1-norm is 7 and the infinity-norm is 4. What is \(\lVert x \rVert_1 / \lVert x \rVert_\infty\)?",
          1.75, "1",
          r"\(7/4 = 1.75\). In \(\mathbb{R}^2\) the comparison \(\lVert x \rVert_1 \le 2\lVert x \rVert_\infty\) allows a ratio as large as 2, and 1.75 sits under that. The reciprocal \(4/7\) swaps the two norms.",
          BALLS, A_BALLS, ["induced-matrix-norms"])
    b.mc(4,
         r"The open ball of radius \(r\) about \(x\), in a chosen norm, is",
         [r"\(\{y : \lVert y-x \rVert \le r\}\)",
          r"\(\{y : \lVert y-x \rVert < r\}\)",
          r"\(\{y : \lVert y-x \rVert = r\}\)",
          "a closed half-space"],
         1,
         r"Open means the inequality is strict, so the sphere itself is left out. The nonstrict inequality is the closed ball. Equality is the sphere. A ball of a norm is not a half-space, except in the trivial sense that both are convex.",
         BALLS, A_BALLS, ["open-closed-sets"])
    b.save()


def bank_cs():
    b = Bank("cauchy-schwarz-inequality")
    b.mc(1,
         r"Cauchy-Schwarz says that for an inner product and its norm,",
         [r"\(\lvert\langle x,y \rangle\rvert \le \lVert x \rVert\,\lVert y \rVert\)",
          r"\(\langle x,y \rangle = \lVert x \rVert + \lVert y \rVert\)",
          r"\(\lVert x+y \rVert = \lVert x \rVert + \lVert y \rVert\) for every pair",
          r"\(\langle x,y \rangle \ge \lVert x \rVert\,\lVert y \rVert\)"],
         0,
         r"The inner product cannot exceed the product of the lengths in absolute value. Equality with the sum of the lengths is not the statement. Equality in the triangle inequality holds only for special pairs. Reversing the inequality would fail as soon as the vectors are short.",
         ANGLE, A_ANGLE)
    b.num(1,
          r"For \(x = (1,2)\) and \(y = (2,1)\), Cauchy-Schwarz bounds the absolute inner product by \(\lVert x \rVert_2\,\lVert y \rVert_2\). What is that bound?",
          5, "1",
          r"Each length is \(\sqrt{5}\), so the product is 5. The inner product itself is 4, which is strictly smaller because the vectors are not parallel. Adding the lengths gives \(2\sqrt{5}\), a different comparison.",
          ANGLE, A_ANGLE)
    b.mc(1,
         r"Equality holds in Cauchy-Schwarz for nonzero vectors exactly when",
         ["the vectors are orthogonal",
          "one is a scalar multiple of the other",
          "both vectors have length 1 and are orthogonal",
          "the vectors have different lengths"],
         1,
         r"The quadratic \(\lVert x + t y \rVert^2\) touches zero only when \(x + t y = 0\) for some \(t\), which is linear dependence. Orthogonal nonzero vectors have inner product 0, and the bound is positive, so equality fails. Different lengths do not prevent one vector from being a multiple of the other.",
         ANGLE, A_ANGLE)
    b.num(2,
          r"What is \((1,2)\cdot(2,1)\)?",
          4, "1",
          r"\(1\cdot 2 + 2\cdot 1 = 4\). The Cauchy-Schwarz bound for this pair is 5, and each squared length is 5. The value 4 is the inner product, not the bound.",
          ANGLE, A_ANGLE)
    b.mc(2,
         r"One proof of Cauchy-Schwarz looks at \(q(t) = \lVert x + t y \rVert^2\). The inequality follows because",
         ["\(q(t)\) is negative for every \(t\)",
          "\(q(t)\) is a cubic polynomial",
          "\(q(t) \ge 0\) for every \(t\), so its discriminant is at most zero",
          "\(q(t)\) does not depend on \(t\)"],
         2,
         r"A square length is never negative, so the quadratic \(q\) stays nonnegative and cannot have two distinct real roots. Its discriminant is \(4\langle x,y \rangle^2 - 4\lVert x \rVert^2\lVert y \rVert^2\), and that quantity is at most zero. A cubic would be the wrong degree, and \(q\) does depend on \(t\) when \(y \ne 0\).",
         ANGLE, A_ANGLE)
    b.num(2,
          r"What is the 2-norm of \((3,0)+(0,4)\)?",
          5, "1",
          r"The sum is \((3,4)\), whose length is \(\sqrt{9+16} = 5\). The triangle inequality only says the length is at most \(3+4 = 7\). The inner product of the two summands is 0, so this pair is orthogonal and the bound is not tight.",
          PERP, A_PERP)
    b.mc(3,
         r"Cauchy-Schwarz implies the triangle inequality because",
         [r"\(\lVert x+y \rVert^2 = \lVert x \rVert^2 + \lVert y \rVert^2 + 2\langle x,y \rangle\) and \(\langle x,y \rangle \le \lVert x \rVert\,\lVert y \rVert\)",
          r"\(\langle x,y \rangle\) is always zero",
          r"\(\lVert x+y \rVert = \lVert x \rVert\,\lVert y \rVert\)",
          r"the 1-norm and the 2-norm are equal"],
         0,
         r"Expanding the square produces the cross term \(2\langle x,y \rangle\). Replacing it by the Cauchy-Schwarz upper bound factors the right-hand side as \((\lVert x \rVert + \lVert y \rVert)^2\). The cross term is zero only for orthogonal vectors. The norms are not equal in general.",
         PERP, A_PERP)
    b.num(3,
          r"For the parallel vectors \((2,0)\) and \((6,0)\), what is \(\lvert\langle x,y \rangle\rvert / (\lVert x \rVert_2\,\lVert y \rVert_2)\)?",
          1, "1",
          r"The inner product is 12 and the lengths are 2 and 6, so the ratio is 1. Equality is the Cauchy-Schwarz conclusion for linearly dependent vectors. A ratio of 12 would skip the division by the lengths.",
          RAY, A_RAY)
    b.num(3,
          r"Cauchy-Schwarz implies \(\lVert(3,0)+(0,4)\rVert_2 \le \lVert(3,0)\rVert_2 + \lVert(0,4)\rVert_2\). What is the right-hand side?",
          7, "1",
          r"The lengths are 3 and 4, so the triangle bound is 7. The actual length of the sum is 5, which is smaller because the vectors are orthogonal rather than parallel.",
          PERP, A_PERP)
    b.mc(4,
         r"The operator norm of a matrix satisfies \(\lVert Ax \rVert_2 \le \lVert A \rVert_F\,\lVert x \rVert_2\). The step that turns the rows of \(A\) into that comparison is",
         ["Cauchy-Schwarz on each row",
          "the claim that every matrix is diagonal",
          "replacing the 2-norm by the square of the 2-norm",
          "setting every singular value equal to 1"],
         0,
         r"Each coordinate of \(Ax\) is a dot product of a row with \(x\), and Cauchy-Schwarz bounds it by the row's Euclidean length times \(\lVert x \rVert_2\). Summing the squares of those bounds produces the Frobenius norm. The matrix need not be diagonal, and the singular values need not equal 1.",
         MAT_R, A_MAT_R, ["induced-matrix-norms"])
    b.num(4,
          r"The 2-norm defines the open balls used for open sets. What is \(\lVert(1,2)\rVert_2\)?",
          math.sqrt(5), "1",
          r"\(\sqrt{1+4} = \sqrt{5}\). The 1-norm is 3, and the infinity-norm is 2. The ball of radius \(\sqrt{5}\) about the origin is the smallest centered 2-norm ball that reaches \((1,2)\).",
          ANGLE, A_ANGLE, ["open-closed-sets"])
    b.mc(4,
         r"A convergence rate compares successive errors with a norm. Cauchy-Schwarz is used along the way when",
         ["the error is required to be a matrix determinant",
          "an inner-product cross term has to be absorbed into a sum of squares",
          "every rate is automatically quadratic",
          "the zero vector is treated as an eigenvector"],
         1,
         r"Rates are statements about a norm of an error. When that norm comes from an inner product, a cross term is estimated by Cauchy-Schwarz and then absorbed. The inequality does not by itself decide whether a rate is linear or quadratic.",
         ANGLE, A_ANGLE, ["convergence-rates"])
    b.save()


def expl_subsets():
    fig = SIMP
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": A_SIMP,
         "body_md": r"""A vector in \(\mathbb{R}^n\) is an ordered list of \(n\) real numbers. An \(m \times n\) matrix is a linear map that sends such a list to a list of length \(m\): the column count is the input dimension and the row count is the output dimension.

Optimization builds its feasible sets from a short menu of these pieces. The nonnegative orthant keeps every coordinate nonnegative. A hyperplane is the solution set of one linear equation \(a^T x = \beta\) with \(a \ne 0\), so it has dimension \(n-1\). A closed half-space keeps one side of a hyperplane, including the boundary when the inequality is not strict. The line through two points lets a real parameter run without restriction. The segment stops that parameter at the endpoints. The unit simplex is the set of nonnegative vectors whose coordinates sum to 1. Those are the weights in a convex combination of \(n\) points."""},
        {"heading": "Key equations",
         "body_md": r"""The line through \(a\) and \(b\) is \(a + t(b-a)\) for \(t \in \mathbb{R}\). The closed segment uses \(t \in [0,1]\). A hyperplane is \(a^T x = \beta\). The matching closed half-space is \(a^T x \le \beta\). The unit simplex in \(\mathbb{R}^n\) is
\[
\{x : x \ge 0,\ 1^T x = 1\}.
\]
The nonnegative orthant drops the sum constraint and keeps only \(x \ge 0\). A \(2 \times 3\) matrix acts on column vectors in \(\mathbb{R}^3\)."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(a = (4, 8)\) and \(b = (10, 16)\). The midpoint uses \(t = 1/2\), so it is the midpoint \((7, 12)\). The same formula with \(t = 2\) leaves the segment and lands at \((16, 24)\), which is on the line and not on the segment.

The point \((7, 12)\) is not on the unit simplex of \(\mathbb{R}^2\), because its coordinates sum to 19 rather than 1. It does lie in the nonnegative orthant. The equation \(x_1 + x_2 = 19\) is a hyperplane, and the midpoint lies on it. The inequality \(x_1 + x_2 \le 19\) is the closed half-space on one side of that hyperplane."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The unit simplex is not the whole orthant: the coordinates also have to sum to 1. A segment is not a line, because the parameter stops at the endpoints. A strict inequality defines an open half-space and leaves the boundary out. The shape of a matrix is not symmetric in the two dimensions: swapping rows and columns swaps the domain and the codomain. The simplex of vectors with \(x \ge 0\) and \(1^T x \le 1\) includes the origin, so it is a different set."""},
        {"heading": "Where this leads",
         "body_md": r"""Norms turn the same geometry into unit balls: a diamond, a disk, or a square, depending on the norm. Convex sets are defined by keeping the whole segment between any two of their points, and half-spaces pass that test. Sublevel sets cut the space with a function value instead of a linear equation. Directional derivatives then walk along a segment and ask how a function changes."""},
    ]
    save_explainer("rn-important-subsets", "Key subsets of R^n", sections)


def expl_spectral():
    sections = [
        {"heading": "The idea", "figure": DIAG, "figure_alt": A_DIAG,
         "body_md": r"""A real symmetric matrix acts by stretching, not by rotating in a way that creates complex eigenvalues. It has a full set of real eigenvalues, and the eigenvectors can be chosen orthonormal. Those directions are the axes of the stretch. In that basis the matrix is diagonal, and each diagonal entry is the factor applied to one axis.

The factorization \(A = U D U^T\) says the same thing in the original coordinates. The factor \(U^T\) writes a vector in the eigenbasis, \(D\) multiplies each coordinate by its eigenvalue, and \(U\) rotates back. Because the columns of \(U\) are orthonormal, the inverse of \(U\) is the transpose. Rebuilding \(A\) is then a sum of rank-one pieces, one per eigenpair: each piece is an eigenvalue times the outer product of a unit eigenvector with itself."""},
        {"heading": "Key equations",
         "body_md": r"""For symmetric \(A\),
\[
A = U D U^T, \qquad U^T U = I, \qquad D = \mathrm{diag}(\lambda_1,\ldots,\lambda_n).
\]
The trace equals the sum of the eigenvalues, and the determinant equals their product. A nonzero vector \(v\) is an eigenvector when \(Av = \lambda v\). For a \(2 \times 2\) matrix the characteristic polynomial is \(\lambda^2 - (\mathrm{tr}\, A)\lambda + \det A\). On a positive semidefinite matrix the singular values agree with the eigenvalues."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A = \begin{bmatrix} 11 & 0 \\ 0 & 3 \end{bmatrix}\). The matrix is already diagonal, so the eigenbasis is the coordinate basis. The eigenvalues are 11 and 3. Their sum is the trace, 14, and their product is the determinant, 33.

Check the stretches. \(A(1,0) = 11(1,0)\) and \(A(0,1) = 3(0,1)\). The factorization is trivial: \(U\) is the identity and \(D\) holds 11 and 3. A vector such as \((1,1)\) is not an eigenvector, because \(A(1,1) = (11, 3)\) is not a scalar multiple of \((1,1)\). The two eigenvalues remain 11 and 3."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The identity \(A = U D U^{-1}\) is true for any diagonalizable matrix, but the transpose form needs orthonormal columns. A symmetric matrix can have nonzero off-diagonal entries and still be simple to diagonalize. The diagonal entries are not the eigenvalues unless the matrix is already diagonal. The zero vector satisfies \(A0 = \lambda 0\) for every \(\lambda\), so it is excluded from the definition of an eigenvector. Complex non-real eigenvalues do not occur for real symmetric matrices."""},
        {"heading": "Where this leads",
         "body_md": r"""Positive definite matrices are the symmetric matrices whose eigenvalues are all positive, and their quadratic-form level sets are ellipsoids aligned with the eigenvectors. Singular values of a general matrix are the square roots of the eigenvalues of \(A^T A\). The Rayleigh quotient sits between the smallest and largest eigenvalues and equals them at the matching eigenvectors."""},
    ]
    save_explainer("spectral-decomposition", "Spectral decomposition of symmetric matrices", sections)


def expl_pd():
    sections = [
        {"heading": "The idea", "figure": ELL, "figure_alt": A_ELL,
         "body_md": r"""A symmetric matrix defines a quadratic form \(x^T A x\). The form is positive definite when that number is positive for every nonzero \(x\), and positive semidefinite when it is only nonnegative. Indefinite means the form takes both signs.

The eigenvalue test is the practical version. In an orthonormal eigenbasis the form becomes a sum of \(\lambda_i y_i^2\). Every term is nonnegative for every \(y\) exactly when every eigenvalue is nonnegative, and every term is positive for \(y \ne 0\) exactly when every eigenvalue is positive. A single negative eigenvalue produces a direction in which the form is negative.

When every eigenvalue is positive, a positive level set of the form is an ellipsoid. Its axes lie along the eigenvectors, and a large eigenvalue makes the ellipsoid short in that direction, because the same budget \(c\) is spent faster."""},
        {"heading": "Key equations",
         "body_md": r"""\(A\) is positive definite when \(x^T A x > 0\) for all \(x \ne 0\), and positive semidefinite when \(x^T A x \ge 0\) for all \(x\). Equivalently, every eigenvalue is positive, or every eigenvalue is nonnegative. For the diagonal case \(A = \mathrm{diag}(\alpha, \beta)\) with \(\alpha, \beta > 0\),
\[
\alpha x_1^2 + \beta x_2^2 = c
\]
is an ellipse with semi-axes \(\sqrt{c/\alpha}\) and \(\sqrt{c/\beta}\). A negative determinant of a \(2 \times 2\) symmetric matrix means the eigenvalues have opposite signs."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A = \mathrm{diag}(3, 12)\). Both diagonal entries are positive, so both eigenvalues are positive and \(A\) is positive definite. At \((1,1)\) the quadratic form equals 15.

The level set \(3 x_1^2 + 12 x_2^2 = 27\) divides through by 27 to give \(x_1^2/9 + x_2^2/2.25 = 1\). The semi-axis along \(x_1\) has length 3. The semi-axis along \(x_2\) has length 1.5, the square root of \(2.25\). The shorter axis is the one with the larger eigenvalue, 12 rather than 3."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A positive determinant is not enough: a \(2 \times 2\) negative definite matrix also has positive determinant, and its trace is negative. Positive entries do not imply positive eigenvalues. A zero eigenvalue is the boundary between definite and semidefinite; the form vanishes on that eigenvector. The ellipse axes follow the eigenvectors, which need not be the coordinate axes when \(A\) has off-diagonal entries. Leading principal minors are an alternative test, and skipping one of them can accept an indefinite matrix."""},
        {"heading": "Where this leads",
         "body_md": r"""A twice differentiable function is convex on an open convex set when its Hessian is positive semidefinite everywhere. A positive definite matrix also supplies descent directions: if \(D\) is positive definite and \(g \ne 0\), then \(g^T(-Dg) < 0\). The same hypothesis makes \(u^T A v\) an inner product, which is the pairing used to talk about conjugacy of search directions."""},
    ]
    save_explainer("positive-definite-matrices", "Positive (semi)definite matrices", sections)


def expl_svd():
    sections = [
        {"heading": "The idea", "figure": AXES, "figure_alt": A_AXES,
         "body_md": r"""Singular value decomposition extends the stretch picture from symmetric matrices to every real matrix. Any \(A\) factors as \(U \Sigma V^T\). The orthogonal matrix \(V^T\) rotates the input into a special basis, the diagonal factor \(\Sigma\) stretches those axes by nonnegative singular values, and the orthogonal matrix \(U\) rotates the result into the output space.

The singular values are not the eigenvalues of a nonsymmetric \(A\). They are the square roots of the eigenvalues of the symmetric positive semidefinite matrix \(A^T A\). A negative eigenvalue of \(A\) itself contributes only its absolute value. The number of positive singular values is the rank. A zero singular value is a direction that \(A\) collapses, which is a nontrivial null vector of \(A\).

The reduced decomposition keeps only the positive singular values and the matching columns of \(U\) and \(V\). The full decomposition pads \(\Sigma\) out to the shape of \(A\) and keeps square orthogonal factors."""},
        {"heading": "Key equations",
         "body_md": r"""\[
A = U \Sigma V^T, \qquad \sigma_i = \sqrt{\lambda_i(A^T A)}.
\]
The squares of the singular values sum to the squared Frobenius norm, which is also the sum of the squares of the entries. The largest singular value is the matrix 2-norm. The rank is the number of nonzero singular values. On a symmetric positive semidefinite matrix, the singular values and the eigenvalues agree."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A = \begin{bmatrix} 0 & 6 \\ 0 & 0 \end{bmatrix}\). Then \(A^T A = \mathrm{diag}(0, 36)\). The eigenvalues are 0 and 36, so the singular values are 0 and 6. There is one nonzero singular value, and the rank is 1.

The largest singular value is the singular value 6. It is also the 2-norm and the Frobenius norm, because the other singular value does not contribute to the sum of squares. The columns are dependent: the first column is zero. A reduced decomposition keeps a single diagonal entry equal to 6 and drops the collapsed direction."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Do not read signed eigenvalues as singular values. A diagonal entry of \(-4\) produces the singular value 4. The spectral factorization \(U D U^T\) needs a symmetric matrix; a general matrix needs two different orthogonal factors. The product of the singular values is zero whenever the matrix is rank deficient, so that product is not the rank. Padding a reduced factorization back to a full one requires orthonormal columns in the padded directions, not zero columns."""},
        {"heading": "Where this leads",
         "body_md": r"""The matrix 2-norm is the largest singular value, while the 1-norm and the infinity-norm have entrywise formulas as a maximum column sum and a maximum row sum. The Frobenius norm and the other Schatten norms are symmetric functions of the singular values. In linear least squares, a zero singular value means the columns are dependent and the minimizer is not unique."""},
    ]
    save_explainer("singular-value-decomposition", "Singular value decomposition", sections)


def expl_rayleigh():
    sections = [
        {"heading": "The idea", "figure": ELL, "figure_alt": A_ELL,
         "body_md": r"""The Rayleigh quotient turns a symmetric matrix into a scalar function on nonzero vectors,
\[
R(x) = \frac{x^T A x}{x^T x}.
\]
Scaling \(x\) does not change \(R\), because the numerator and the denominator scale by the same factor. In an eigenbasis, \(R\) is a weighted average of the eigenvalues, with weights equal to the squared coordinates of the unit vector. An average sits between the smallest and the largest number being averaged. So every value of \(R\) lies between \(\lambda_{\min}\) and \(\lambda_{\max}\).

The bounds are achieved. At a unit eigenvector the quotient collapses to that eigenvalue. The trace is the sum of all the eigenvalues, and the determinant is their product. Those two summaries do not replace the quotient: the quotient inspects one direction at a time."""},
        {"heading": "Key equations",
         "body_md": r"""For symmetric \(A\) and \(x \ne 0\),
\[
\lambda_{\min} \le R(x) \le \lambda_{\max}.
\]
If \(Av = \lambda v\) and \(v \ne 0\), then \(R(v) = \lambda\). Also \(\mathrm{tr}\, A = \sum_i \lambda_i\) and \(\det A = \prod_i \lambda_i\). For a symmetric positive definite matrix the 2-norm condition number is the ratio \(\lambda_{\max}/\lambda_{\min}\), which is the ratio of the extreme values of \(R\) on the unit sphere."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A = \mathrm{diag}(7, 5)\). The eigenvalues are 7 and 5, so every Rayleigh quotient lies between 5 and 7. At \((1,1)\),
\[
R(1,1) = \frac{7+5}{2} = 6.
\]
The quotient equals 6. It is strictly between the eigenvalues because \((1,1)\) has weight on both axes. At \((1,0)\) the quotient equals 7, the larger eigenvalue, and at \((0,1)\) it equals 5. The trace is 12 and the determinant is 35. Neither of those numbers is the value of \(R\) at \((1,1)\)."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Forgetting to divide by \(x^T x\) computes the quadratic form, not the quotient. The quotient does not depend on the length of \(x\), so normalizing is optional as long as the division is there. The trace is the sum of the eigenvalues, not the value of \(R\) at a generic vector. The upper bound is not attained at every unit vector, only on the top eigenspace. The zero vector is excluded because the denominator would vanish."""},
        {"heading": "Where this leads",
         "body_md": r"""The condition number \(\lambda_{\max}/\lambda_{\min}\) controls how fast steepest descent can converge on a quadratic, because the level sets are ellipses whose aspect ratio is that condition number. Power iteration multiplies by \(A\) and renormalizes, which pushes the Rayleigh quotient up toward the largest eigenvalue. Conjugate gradient is the method that stops paying that full condition-number penalty on a quadratic."""},
    ]
    save_explainer("rayleigh-quotient", "Rayleigh quotient and eigenvalue bounds", sections)


def expl_inner():
    sections = [
        {"heading": "The idea", "figure": ANGLE, "figure_alt": A_ANGLE,
         "body_md": r"""An inner product is a way of multiplying two vectors and getting a scalar, with three rules. It is linear in each argument, symmetric for real vectors, and positive when a nonzero vector is paired with itself. The ordinary dot product is the standard example. The Frobenius product does the same job for matrices: multiply matching entries and add, which is also the trace of \(A^T B\).

The inner product measures angle. Nonzero vectors are orthogonal when the pairing is zero. The cosine of the angle is the inner product divided by the product of the lengths. The length itself is recovered by taking the square root of the inner product of a vector with itself. That length is a norm, and it is the 2-norm when the inner product is the dot product.

Not every bilinear formula works. If a pairing can be negative on a vector with itself, it violates positivity and cannot define a length."""},
        {"heading": "Key equations",
         "body_md": r"""For the dot product, \(\langle x, y \rangle = x^T y\) and \(\lVert x \rVert_2 = \sqrt{x^T x}\). The angle satisfies
\[
\cos\theta = \frac{\langle x, y \rangle}{\lVert x \rVert\,\lVert y \rVert}
\]
when both vectors are nonzero. Orthogonal means \(\langle x, y \rangle = 0\). The Frobenius product is \(\langle A, B \rangle_F = \sum_{ij} a_{ij} b_{ij} = \mathrm{tr}(A^T B)\)."""},
        {"heading": "Worked example",
         "body_md": r"""The vectors \((3,2)\) and \((2,-3)\) have dot product 0. They are orthogonal, even though neither is an axis vector. Each has squared length \(9+4 = 13\).

Separately, take
\[
A = \begin{bmatrix} 6 & 1 \\ 0 & 2 \end{bmatrix}, \qquad
B = \begin{bmatrix} 1 & 0 \\ 4 & 1 \end{bmatrix}.
\]
The entrywise products are 6, 0, 0, and 2. The Frobenius inner product has value 8. The trace formula \(\mathrm{tr}(A^T B)\) gives the same 8. The product of the two determinants is a different number and is not the inner product."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Orthogonality is not equal length. A positive dot product means an acute angle, not orthogonality. The Frobenius product is not the product of determinants or the product of traces. A formula such as \(x_1 y_1 - x_2 y_2\) is bilinear and symmetric, but it gives a negative square on the second basis vector, so it is not an inner product. The zero vector is orthogonal to everything, and it is excluded when an angle is computed because the lengths in the denominator vanish."""},
        {"heading": "Where this leads",
         "body_md": r"""Cauchy-Schwarz says the absolute inner product cannot exceed the product of the lengths, with equality exactly for parallel vectors. Gram-Schmidt uses the coefficient \(\langle v, u \rangle / \langle u, u \rangle\) to subtract the part of \(v\) parallel to \(u\). When the inner product is \(u^T Q v\) for a positive definite \(Q\), that same orthogonality is called conjugacy and is the geometry behind conjugate directions."""},
    ]
    save_explainer("inner-products", "Inner products", sections)


def expl_norms():
    sections = [
        {"heading": "The idea", "figure": BALLS, "figure_alt": A_BALLS,
         "body_md": r"""A norm measures the size of a vector. Three rules define it. A nonzero vector has positive size. Scaling a vector by \(c\) scales the size by \(\lvert c \rvert\), so a negative scalar does not make the size negative. The triangle inequality says a sum is at most the sum of the sizes.

The usual \(\ell_p\) family all satisfy those rules. The 1-norm adds the absolute coordinates. The 2-norm is the ordinary Euclidean length. The infinity-norm keeps only the largest absolute coordinate. The general \(\ell_p\) norm takes the \(p\)-th root of the sum of \(p\)-th powers of the absolute coordinates. As \(p\) grows, that expression approaches the infinity-norm.

The unit ball, the set of vectors with norm at most 1, shows the difference in shape. The 1-norm ball is a diamond, the 2-norm ball is a disk, and the infinity-norm ball is a square. In finite dimension the shapes differ but the norms are equivalent: each is bounded by a constant times any other. The constants can grow with the dimension. Equivalence is not equality."""},
        {"heading": "Key equations",
         "body_md": r"""For \(x \in \mathbb{R}^n\),
\[
\lVert x \rVert_1 = \sum_i \lvert x_i \rvert, \qquad
\lVert x \rVert_2 = \sqrt{\sum_i x_i^2}, \qquad
\lVert x \rVert_\infty = \max_i \lvert x_i \rvert.
\]
Useful comparisons are \(\lVert x \rVert_\infty \le \lVert x \rVert_2 \le \lVert x \rVert_1 \le \sqrt{n}\,\lVert x \rVert_2 \le n\,\lVert x \rVert_\infty\). The open ball of radius \(r\) about \(x\) is the strict inequality \(\lVert y - x \rVert < r\)."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(x = (6, -8)\). The absolute coordinates are 6 and 8. Their sum is 14, so the 1-norm is the sum of absolutes 14. The Euclidean length is \(\sqrt{36+64} = \sqrt{100}\), so the length is 10. The larger absolute coordinate is 8, so the infinity-norm is 8.

The ratio of the 1-norm to the infinity-norm is \(14/8 = 1.75\). In \(\mathbb{R}^2\) that ratio cannot exceed 2, and this vector does not reach the bound because the two absolute coordinates are not equal. The 2-norm sits between them: \(8 < 10 < 14\)."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A norm of a sum is not always the sum of the norms. That equality holds for the 1-norm only in special sign patterns, and for the 2-norm when the vectors are nonnegative multiples of one vector. Homogeneity uses the absolute value of the scalar. In infinite dimension, equivalence can fail; the finite-dimensional statement does not transfer unchanged. The unit ball of the infinity-norm is a square, not a disk, so drawing one ball for every norm misstates the geometry."""},
        {"heading": "Where this leads",
         "body_md": r"""Cauchy-Schwarz is a statement about the 2-norm that comes from the dot product, and it is the step that proves the triangle inequality for that norm. Induced matrix norms measure how much a matrix can stretch a vector, using a vector norm in the definition. Open and closed sets are defined with balls of a norm, and equivalence of norms means they determine the same open sets."""},
    ]
    save_explainer("vector-norms-lp", "Vector norms and l_p norms", sections)


def expl_cs():
    sections = [
        {"heading": "The idea", "figure": ANGLE, "figure_alt": A_ANGLE,
         "body_md": r"""Cauchy-Schwarz limits how large an inner product can be. For any vectors,
\[
\lvert\langle x, y \rangle\rvert \le \lVert x \rVert\,\lVert y \rVert,
\]
where the norm is the one induced by the inner product. The geometric reading is that the absolute cosine of an angle cannot exceed 1. The algebraic reading is that a square length cannot be negative.

Equality is informative. It holds when one vector is a scalar multiple of the other, including the case where either vector is zero. Orthogonal nonzero vectors do not give equality: their inner product is zero while the right-hand side is positive. So equality detects parallel vectors, not perpendicular ones.

The same bound proves the triangle inequality. Expand \(\lVert x+y \rVert^2\), replace the cross term by its Cauchy-Schwarz upper bound, and the right-hand side becomes \((\lVert x \rVert + \lVert y \rVert)^2\). Taking square roots gives \(\lVert x+y \rVert \le \lVert x \rVert + \lVert y \rVert\)."""},
        {"heading": "Key equations",
         "body_md": r"""The inequality is \(\lvert\langle x,y \rangle\rvert \le \lVert x \rVert\,\lVert y \rVert\). One proof uses the quadratic
\[
q(t) = \lVert y \rVert^2\, t^2 + 2\langle x,y \rangle\, t + \lVert x \rVert^2 = \lVert x + t y \rVert^2 \ge 0.
\]
A quadratic that never goes negative has a nonpositive discriminant, and that discriminant condition is Cauchy-Schwarz. Equality holds when \(x\) and \(y\) are linearly dependent."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(x = (3,1)\) and \(y = (1,3)\). The inner product is 6. Each squared length is \(9+1 = 10\), so each length is \(\sqrt{10}\) and the product of the lengths is 10. Cauchy-Schwarz says the absolute inner product cannot exceed that product. Here the inner product 6 is strictly below the product 10, because neither vector is a multiple of the other.

The ratio \(6/10 = 0.6\) is the cosine of the angle. If \(y\) were replaced by \((6,2)\), a positive multiple of \(x\), the ratio would rise to 1 and equality would hold."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The inequality bounds the absolute value. A negative inner product is still fine, and the bound applies to its magnitude. Equality is not the orthogonal case. Dropping the absolute value and writing \(\langle x,y \rangle \le \lVert x \rVert\,\lVert y \rVert\) is true, but the matching lower bound needs the minus sign. The triangle inequality is a consequence, not a replacement: \(\lVert x+y \rVert\) can be strictly smaller than the sum of the lengths. Applying the result to a pairing that is not an inner product is not justified."""},
        {"heading": "Where this leads",
         "body_md": r"""Each row of a matrix dotted with a vector is an inner product, so Cauchy-Schwarz bounds \(\lVert Ax \rVert_2\) by the Frobenius norm of \(A\) times \(\lVert x \rVert_2\). That comparison is the doorway to induced matrix norms. The 2-norm also defines the balls used for open sets. When a later convergence argument expands a squared norm and has to absorb a cross term, this inequality is the estimate it uses."""},
    ]
    save_explainer("cauchy-schwarz-inequality", "Cauchy-Schwarz inequality", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    bank_subsets()
    bank_spectral()
    bank_pd()
    bank_svd()
    bank_rayleigh()
    bank_inner()
    bank_norms()
    bank_cs()
    expl_subsets()
    expl_spectral()
    expl_pd()
    expl_svd()
    expl_rayleigh()
    expl_inner()
    expl_norms()
    expl_cs()
    # Word counts are checked by reading the files back, so a short explainer fails here.
    import json
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    banned = ("graz", "boyd", "nocedal", "vandenberghe", "hefferon", "wikibook",
              "textbook", "university", "professor", "lecture", "syllabus", "cambridge", "springer")
    ids = [
        "rn-important-subsets", "spectral-decomposition", "positive-definite-matrices",
        "singular-value-decomposition", "rayleigh-quotient", "inner-products",
        "vector-norms-lp", "cauchy-schwarz-inequality",
    ]
    bad = False
    for sid in ids:
        exp = json.load(open(os.path.join(root, "skilltree", "explainers", sid + ".json"), encoding="utf-8"))
        n = doc_words(exp["sections"])
        bank = json.load(open(os.path.join(root, "skilltree", "bank", sid + ".json"), encoding="utf-8"))
        blob = json.dumps(exp) + json.dumps(bank)
        low = blob.lower()
        hits = [w for w in banned if w in low]
        figs = sum(1 for q in bank["questions"] if q.get("figure"))
        print(f"{sid}: words {n}, figures {figs}/12")
        if not 250 <= n <= 500:
            print("  word count outside 250-500")
            bad = True
        if hits:
            print("  banned", hits)
            bad = True
        if figs < 9:
            print("  fewer than 9 figures")
            bad = True
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
