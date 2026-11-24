#!/usr/bin/env python3
"""Generate optimization-models batch EB1 banks and explainers.

Skills: qr-factorization, fundamental-subspaces, block-matrix-identities,
principal-component-analysis, low-rank-approximation, least-squares-perturbation,
ridge-regression, principal-components-regression, maximum-likelihood-estimation.

Closed-form answers live here. skilltree/verify_eecs127_eb1.py recomputes the
numeric ones and does not import this file.

Ordering check: every order question was read pair by pair. Adjacent steps
share a value, so swapping two of them leaves the procedure incorrect.
Diagrams are attached only where the item names a matrix, a pair of columns,
or an axis-aligned covariance ellipse. Formula-only prompts have no figure.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import DEEP_TYPES, Bank, deep_quota, save_explainer
from templates import ellipse_axes, matrix_fig, plane_vectors

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IDS = [
    "qr-factorization",
    "fundamental-subspaces",
    "block-matrix-identities",
    "principal-component-analysis",
    "low-rank-approximation",
    "least-squares-perturbation",
    "ridge-regression",
    "principal-components-regression",
    "maximum-likelihood-estimation",
]
VIDEOS = {
    "qr-factorization": {
        "url": "https://www.youtube.com/watch?v=qmRC8mTPGI8",
        "title": "QR Factorization",
    },
    "fundamental-subspaces": {
        "url": "https://www.youtube.com/watch?v=nHlE7EgJFds",
        "title": "The four fundamental subspaces",
    },
    "block-matrix-identities": {
        "url": "https://www.youtube.com/watch?v=_oHHbszze5M",
        "title": "Block multiplication, the block inverse, and the Schur complement",
    },
    "principal-component-analysis": {
        "url": "https://www.youtube.com/watch?v=FgakZw6K1QQ",
        "title": "Directions of greatest spread in a data cloud",
    },
    "low-rank-approximation": {
        "url": "https://www.youtube.com/watch?v=12K5aydB9cQ",
        "title": "Nearest matrix of a given rank",
    },
    "least-squares-perturbation": {
        "url": "https://www.youtube.com/watch?v=a5oQktSURoE",
        "title": "Parent concept: the matrix condition number, and how singular values scale errors",
    },
    "ridge-regression": {
        "url": "https://www.youtube.com/watch?v=Q81RR3yKn30",
        "title": "A squared penalty on the fitted coefficients",
    },
    "principal-components-regression": {
        "url": "https://www.youtube.com/watch?v=SWfucxnOF8c",
        "title": "Least squares in the leading principal-component coordinates",
    },
    "maximum-likelihood-estimation": {
        "url": "https://www.youtube.com/watch?v=XepXtl9YKwc",
        "title": "Choosing parameters that make the observations most likely",
    },
}

M68 = matrix_fig([["6", "3"], ["8", "6"]], "two columns to factor")
A68 = "A 2 by 2 matrix with columns (6, 8) and (3, 6)."
V68 = plane_vectors([(6, 8, "a1"), (3, 6, "a2")], "columns a1 and a2", "x1", "x2")
AV68 = "Two arrows from the origin, labeled a1 and a2."
MLS = matrix_fig([["1", "0"], ["0", "1"], ["1", "1"]], "design with three rows")
ALS = "A 3 by 2 matrix with rows (1, 0), (0, 1), and (1, 1)."
MF = matrix_fig([["1", "2", "0"], ["0", "0", "3"], ["2", "4", "0"]], "rank-two matrix")
AF = "A 3 by 3 matrix. The third row is twice the first, and the middle row is (0, 0, 3)."
MB = matrix_fig([["5", "2"], ["10", "9"]], "scalar blocks")
AB = "A 2 by 2 matrix with entries 5, 2, 10, and 9."
MP = matrix_fig([["1", "2"], ["0", "3"]], "left factor")
AP = "A 2 by 2 matrix with rows (1, 2) and (0, 3)."
MC = matrix_fig([["9", "4"], ["0", "0"]], "diagonal covariance")
AC = "A diagonal 2 by 2 covariance with entries 9 and 4."
ELL = ellipse_axes("covariance ellipse, longer on the first axis")
AELL = "An axis-aligned ellipse centered at the origin and longer along the first axis."
ELLT = ellipse_axes("covariance ellipse, longer on the second axis", rx=46, ry=86)
AELLT = "An axis-aligned ellipse centered at the origin and longer along the second axis."
MSIG = matrix_fig([["6", "0", "0"], ["0", "3", "0"], ["0", "0", "2"]], "singular values on a diagonal")
ASIG = "A diagonal matrix whose diagonal entries are 6, 3, and 2."
MAB = matrix_fig([["1", "0"], ["1", "0"], ["0", "1"]], "two-column design")
AAB = "A 3 by 2 matrix with two copies of the first standard basis row and one copy of the second."


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


def bank_qr():
    b = Bank("qr-factorization")
    b.mc(
        1,
        r"Gram-Schmidt turns the columns of a full-column-rank matrix into orthonormal vectors. In the thin factorization \(A = QR\), those vectors and the coefficients that built them are stored as",
        [
            r"orthonormal columns of \(Q\), and an upper-triangular \(R\) whose diagonal lengths are positive",
            r"orthonormal rows of \(R\), and a lower-triangular \(Q\)",
            r"the eigenvalues of \(A^T A\) on the diagonal of \(Q\)",
            r"a square orthogonal \(Q\) for every shape of \(A\), with \(R\) diagonal",
        ],
        0,
        r"The prerequisite builds one orthonormal vector at a time and records a length and an inner-product coefficient at each step. Thin QR keeps the orthonormal vectors as the columns of \(Q\), so \(Q^T Q = I\), and it keeps the coefficients in an upper-triangular \(R\) with positive diagonal entries. \(R\) is not the orthogonal factor. Eigenvalues of \(A^T A\) are a different factorization. A thin \(Q\) is square only when \(A\) itself is square.",
        V68, AV68,
    )
    b.num(
        1,
        r"Take \(A = \begin{bmatrix} 6 & 3 \\ 8 & 6 \end{bmatrix}\) and the thin QR with positive diagonal. What is the \((1,1)\) entry of \(R\)?",
        10, "(unitless)",
        r"Gram-Schmidt keeps the first column and records its length. \(\lVert(6,8)\rVert = \sqrt{36+64} = 10\), so \(R_{11} = 10\). The inner product of the two columns is \(6\cdot 3+8\cdot 6 = 66\), which is not a length. The second column has length \(\sqrt{9+36} = \sqrt{45}\), and that length is not \(R_{11}\).",
        M68, A68,
    )
    b.mc(
        1,
        r"For a thin \(Q\) with more rows than columns and orthonormal columns, which matrix identity is the one Gram-Schmidt enforces?",
        [
            r"\(Q Q^T = I\)",
            r"\(Q^T Q = I\)",
            r"\(Q^T Q = 0\)",
            r"\(R^T R = I\)",
        ],
        1,
        r"Orthonormal columns mean each column has length 1 and distinct columns have inner product 0. Those are exactly the entries of \(Q^T Q\), so \(Q^T Q = I\). The product \(Q Q^T\) is the projection onto the column space, and it equals \(I\) only when the columns already span the whole row space. A zero product would say the columns are zero. \(R\) carries the lengths, so it is not orthogonal.",
        M68, A68,
    )
    b.order(
        2,
        r"Put these steps in the order that builds the thin QR of a 2-column matrix, with positive diagonal entries in \(R\).",
        [
            "Take the length of the first column and store that positive number as the (1,1) entry of R.",
            "Divide the first column by that length. The result is the first column of Q.",
            "Take the inner product of that Q column with the second column of A, and store it as the (1,2) entry of R.",
            "Subtract that multiple of the Q column from the second column of A, and store the positive length of the remainder as the (2,2) entry of R.",
        ],
        r"Each step uses the number the previous step just produced. The length has to exist before the division. The first Q column has to exist before its inner product with the second column. That inner product is the multiple that is subtracted, and only then does the remainder have a length. Swapping any adjacent pair uses a vector or a coefficient that has not been computed yet.",
        V68, AV68,
    )
    b.num(
        2,
        r"Continue the same factorization of \(A = \begin{bmatrix} 6 & 3 \\ 8 & 6 \end{bmatrix}\). The first column of \(Q\) is \((6,8)/10\). What is the \((1,2)\) entry of \(R\)?",
        6.6, "(unitless)",
        r"That entry is the inner product of the first Q column with the second column of \(A\). \((0.6)(3)+(0.8)(6) = 1.8+4.8 = 6.6\). The length 10 is \(R_{11}\), already used to build the unit vector. The second diagonal entry is the length of what remains after this multiple is removed, not the inner product itself.",
        M68, A68,
    )
    b.num(
        2,
        r"Still for \(A = \begin{bmatrix} 6 & 3 \\ 8 & 6 \end{bmatrix}\) and a positive diagonal. After removing \(6.6\) times the first Q column from \((3,6)\), what is the \((2,2)\) entry of \(R\)?",
        1.2, "(unitless)",
        r"The remainder is \((3,6) - 6.6\cdot(0.6,0.8) = (-0.96, 0.72)\). Its length is \(\sqrt{0.96^2+0.72^2} = \sqrt{1.44} = 1.2\), and the positive-diagonal convention stores that length in \(R_{22}\). The signed first component \(-0.96\) is not a diagonal entry. Leaving the remainder un-normalized would store a vector, not the scalar \(R_{22}\).",
        M68, A68,
    )
    b.sym(
        3,
        r"Let \(a > 0\) and let \(b\) be a real number. The matrix \(\begin{bmatrix} a & b \\ 0 & a \end{bmatrix}\) has the thin QR with positive diagonal. Write the sum of the squares of all four entries of \(R\), as an expression in a and b.",
        "2*a**2 + b**2",
        {"a": (0.5, 3), "b": (-2, 2)},
        r"The first column is \((a,0)\), so \(R_{11} = a\) and the first Q column is \((1,0)\). Its inner product with \((b,a)\) is \(b\), and the remainder \((0,a)\) has length \(a\). Thus \(R = \begin{bmatrix} a & b \\ 0 & a \end{bmatrix}\), and the sum of squares of its entries is \(a^2+b^2+a^2\)."
        "\n"
        r"• \(a^2+b^2\) drops the second diagonal length."
        "\n"
        r"• \(a+b\) adds entries instead of squaring them."
        "\n"
        r"• \(2a+b\) is the sum of the first row, not the sum of squares.",
        ["a**2 + b**2 + a**2", "2*(a*a) + b*b", "(a**2) + (a**2) + (b**2)"],
    )
    b.mc(
        3,
        r"Once \(A = QR\) is known, with \(Q^T Q = I\) and \(R\) upper triangular and invertible, the least-squares minimizer of \(\lVert Ax-b\rVert\) is the solution of",
        [
            r"\(R^T R x = b\)",
            r"\(Q x = b\)",
            r"\(R x = Q^T b\)",
            r"\(R x = Q b\)",
        ],
        2,
        r"Substitute \(A = QR\) into the normal equations. \(A^T A = R^T Q^T Q R = R^T R\) and \(A^T b = R^T Q^T b\). Cancel the invertible \(R^T\) to get \(R x = Q^T b\). Using \(Qb\) forgets the transpose. Solving \(Qx = b\) asks the thin factor to hit \(b\) exactly, which a tall \(Q\) cannot do. \(R^T R x = b\) drops \(Q\) and also replaces \(A^T b\) by \(b\).",
    )
    b.multi(
        3,
        r"Which statements are true of every thin QR factorization of a full-column-rank matrix, with the positive-diagonal convention?",
        [
            r"The columns of \(Q\) are orthonormal.",
            r"\(R\) is square and upper triangular.",
            r"\(Q\) is square whenever \(A\) has more rows than columns.",
            r"The diagonal entries of \(R\) are positive.",
        ],
        [0, 1, 3],
        r"Full column rank lets Gram-Schmidt accept every column, so \(Q\) has one orthonormal column per column of \(A\) and \(R\) is square and upper triangular. The positive-length choice makes each diagonal entry of \(R\) positive. A thin \(Q\) has the same number of columns as \(A\), so it is not square when \(A\) is tall.",
        M68, A68,
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The matrix is \(A = \begin{bmatrix} 6 & 3 \\ 8 & 6 \end{bmatrix}\), factored with a positive diagonal.",
        [
            r"The first column has length 10, so the (1,1) entry of R is 10.",
            r"Dividing that column by 10 produces the first column of Q.",
            r"Because Q is taller than it is wide, the product Q Q^T equals the identity.",
            r"The product of this Q and this R rebuilds A.",
        ],
        2,
        r"The length 10 and the scaling that produces the first Q column are the opening Gram-Schmidt steps, and \(QR\) rebuilds \(A\) by construction. The false step is the product with the factors in the wrong order. Orthonormal columns give \(Q^T Q = I\). When \(Q\) is 2 by 2 in this example the two products agree, but the claimed reason was the tall shape, and that reason is the projection identity \(QQ^T\), not the column identity. For a tall thin factor, \(QQ^T\) is the projection onto the columns and is not \(I\).",
        reasons=[
            "Orthonormal columns mean Q^T Q = I. The product Q Q^T is the identity only when those columns span every row direction.",
            "The diagonal of R has to be negative, so the length step is the one that fails.",
            "R is lower triangular, so Q R cannot rebuild A.",
        ],
        correct_reason=0,
        fig=M68, alt=A68, preview=["linear-least-squares"],
    )
    b.num(
        4,
        r"Solve the least-squares problem for \(A = \begin{bmatrix} 1 & 0 \\ 0 & 1 \\ 1 & 1 \end{bmatrix}\) and \(b = \begin{bmatrix} 1 \\ 1 \\ 0 \end{bmatrix}\) by a thin QR backsolve, or by the normal equations that the backsolve reproduces. What is the first coordinate of the minimizer?",
        1 / 3, "(unitless)",
        r"The columns are independent, so the minimizer is unique. \(A^T A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}\) and \(A^T b = (1,1)\). The solution of \(2x_1+x_2 = 1\) and \(x_1+2x_2 = 1\) is \(x_1 = x_2 = 1/3\). A thin QR with positive diagonal produces the same point, because \(R x = Q^T b\) is the normal equation after canceling \(R^T\). The average of the three observations is \(2/3\), and that average is not a coefficient. The second standard-basis guess \((1,0)\) leaves a residual whose normal equation is not zero.",
        MLS, ALS, ["linear-least-squares"],
    )
    b.mc(
        4,
        r"Why does the triangular backsolve \(R x = Q^T b\) avoid forming the Gram matrix \(A^T A\)?",
        [
            r"Because \(R\) stores eigenvalues, and eigenvalues replace inner products.",
            r"Because \(Q\) is always square, so \(Q^T b\) is a copy of \(b\).",
            r"Because the normal matrix equals \(R^T R\), and a triangular \(R\) can be used directly.",
            r"Because the residual \(Ax-b\) is the zero vector for every \(b\).",
        ],
        2,
        r"From \(A = QR\) and \(Q^T Q = I\), the Gram matrix is \(R^T R\) and the right-hand side is \(R^T Q^T b\). Canceling \(R^T\) leaves a triangular system. The diagonal of \(R\) holds column lengths from Gram-Schmidt, not eigenvalues of a symmetric matrix. A thin \(Q\) need not be square, so \(Q^T b\) is shorter than \(b\). A nonzero residual is the usual case; the backsolve does not require \(b\) to lie in the column space.",
        MLS, ALS, ["linear-least-squares"],
    )
    b.save()


def bank_subspaces():
    b = Bank("fundamental-subspaces")
    b.mc(
        1,
        r"The linear-algebra review gives the nullspace and the rank. The four fundamental subspaces of an \(m\) by \(n\) matrix are",
        [
            r"the column space, the row space, the nullspace, and the left nullspace",
            r"the column space, the nullspace, the set of eigenvalues, and the set of singular values",
            r"two copies of the column space and two copies of the nullspace",
            r"the row space, the determinant, the trace, and the nullspace",
        ],
        0,
        r"Rank-nullity already relates the column space and the nullspace. The four-subspace picture adds the row space, which is the column space of \(A^T\), and the left nullspace, which is the nullspace of \(A^T\). Eigenvalues and singular values are not subspaces of the domain or the codomain. The determinant and the trace are numbers.",
        MF, AF,
    )
    b.num(
        1,
        r"A matrix has 5 columns and rank 3. The review identity is rank plus nullity equals the number of columns. What is the dimension of the nullspace?",
        2, "(unitless)",
        r"Nullity is \(5-3 = 2\). The rank 3 is the dimension of the column space and of the row space, not of the nullspace. The sum \(5+3 = 8\) adds the two ingredients instead of subtracting. A count of 5 would be every column, including the pivot columns.",
    )
    b.mc(
        1,
        r"Inner products say that two vectors are orthogonal when their pairing is zero. For a real matrix \(A\), the nullspace is orthogonal to",
        [
            r"the column space",
            r"the row space",
            r"the left nullspace and to nothing else",
            r"every vector in the codomain",
        ],
        1,
        r"A vector \(x\) is in the nullspace when \(Ax = 0\). Each row of that product is the inner product of \(x\) with a row of \(A\), so \(x\) is orthogonal to every row. The rows span the row space. The column space lives in the other Euclidean space, so it is not the orthogonal partner of the nullspace. The left nullspace is the partner of the column space.",
    )
    b.order(
        2,
        "Put these steps in the order that computes the left-nullspace dimension from a transpose.",
        [
            "Replace the matrix by its transpose.",
            "Row-reduce that transpose and count the nonzero rows. The count is the rank.",
            "Subtract that rank from the number of rows of the original matrix. The difference is the left-nullspace dimension.",
        ],
        r"The transpose has to come first, because the next step row-reduces that transpose rather than the original matrix. The nonzero-row count is the rank, and the subtraction uses that count. Subtracting before the count has no rank to subtract. Row-reducing before transposing computes a rank as well, but it is not the procedure written here: the second step names the transpose.",
        MF, AF,
    )
    b.num(
        2,
        r"A matrix has 4 rows and rank 3. What is the dimension of the left nullspace?",
        1, "(unitless)",
        r"The left nullspace is the nullspace of the transpose, so its dimension is rows minus rank: \(4-3 = 1\). The rank 3 is the dimension of the row space. Columns are not given, so a nullity of the original nullspace is not determined by these two numbers. The product \(4\cdot 3 = 12\) is not a dimension in this count.",
    )
    b.num(
        2,
        r"Let \(A = \begin{bmatrix} 1 & 2 & 0 \\ 0 & 0 & 3 \\ 2 & 4 & 0 \end{bmatrix}\). What is the dimension of its nullspace?",
        1, "(unitless)",
        r"The third row is twice the first, and the middle row is not a multiple of the first, so the rank is 2. Three columns give nullity \(3-2 = 1\). A count of 2 is the rank, not the nullity. A count of 3 would mean every column is dependent. The left-nullspace dimension is also 1 here, but that is rows minus rank, and the question asks for the nullspace.",
        MF, AF,
    )
    b.sym(
        3,
        r"Let \(n\) be the number of columns and let \(k\) be the rank, with \(k < n\). Write the dimension of the nullspace as an expression in n and k.",
        "n - k",
        {"n": (5, 9), "k": (1, 3)},
        r"Rank-nullity says the nullspace dimension is the number of columns minus the rank. The expression is \(n-k\)."
        "\n"
        r"• \(n+k\) adds the rank instead of removing the pivot columns."
        "\n"
        r"• \(k\) is the dimension of the row space."
        "\n"
        r"• \(n\) counts every column, including the pivot columns.",
        ["n+(-k)", "(n)-(k)"],
    )
    b.multi(
        3,
        r"Which orthogonality relations hold for every real matrix?",
        [
            r"The nullspace is orthogonal to the row space.",
            r"The left nullspace is orthogonal to the column space.",
            r"The column space is orthogonal to the row space.",
            r"The left nullspace is orthogonal to the nullspace.",
        ],
        [0, 1],
        r"The two true partners are the ones that share a Euclidean space: nullspace with row space, both in the domain, and left nullspace with column space, both in the codomain. The column space and the row space live in spaces of different dimension whenever the matrix is not square, so they are not an orthogonal pair. The nullspace and the left nullspace likewise sit in different spaces.",
    )
    b.mc(
        3,
        r"A least-squares residual \(b-Ax\) is orthogonal to every column of \(A\). Which subspace contains that residual?",
        [
            r"the row space",
            r"the nullspace",
            r"the column space",
            r"the left nullspace",
        ],
        3,
        r"Orthogonality to every column means the residual is orthogonal to the column space. The orthogonal complement of the column space is the left nullspace. The row space and the nullspace are subspaces of the domain, while the residual is a vector in the codomain, next to \(b\). The column space is the set of vectors \(Ax\), and the residual is the part of \(b\) that is not in that set.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The matrix is \(A = \begin{bmatrix} 1 & 2 & 0 \\ 0 & 0 & 3 \\ 2 & 4 & 0 \end{bmatrix}\).",
        [
            r"The rank of A is 2.",
            r"The nullspace has dimension 3 - 2 = 1.",
            r"The left nullspace is orthogonal to the row space.",
            r"The row space has dimension 2, the same as the rank.",
        ],
        2,
        r"The third row is twice the first and the middle row is independent of it, so the rank is 2. Rank-nullity then gives a one-dimensional nullspace, and the row-space dimension equals the rank. The false step pairs the left nullspace with the row space. The left nullspace is orthogonal to the column space. The nullspace is the subspace orthogonal to the row space.",
        reasons=[
            "The left nullspace is orthogonal to the column space. The nullspace is the one orthogonal to the row space.",
            "The row space is another name for the column space, so the claimed orthogonality is between a subspace and itself.",
            "Rank-nullity subtracts the rank from the number of rows to get the row-space dimension, so the last step is the false one.",
        ],
        correct_reason=0,
        fig=MF, alt=AF, preview=["linear-least-squares"],
    )
    b.num(
        4,
        r"For \(A = \begin{bmatrix} 1 & 2 & 0 \\ 0 & 0 & 3 \\ 2 & 4 & 0 \end{bmatrix}\), the nullspace is one-dimensional. Take the nullspace vector whose second entry is 3. What is its first entry?",
        -6, "(unitless)",
        r"The middle row forces the third coordinate to be 0. The first row then says \(x_1+2x_2 = 0\). With \(x_2 = 3\), the first entry is \(-6\). The vector is \((-6,3,0)\). The choice \(x_1 = 3\) keeps the free variable and ignores the factor 2. The third entry is 0, and 0 is not the first entry. Twice the second entry, without the minus sign, is the third row's relation to the first row, not the nullspace coordinate.",
        MF, AF, ["linear-least-squares"],
    )
    b.mc(
        4,
        r"In a least-squares problem with independent columns, the minimizer can be chosen in the row space. A vector in the nullspace may be added without changing \(Ax\). Which description matches that split?",
        [
            r"The domain splits into the column space and the left nullspace.",
            r"The domain splits into the row space and the nullspace, and these two are orthogonal.",
            r"The codomain splits into the row space and the nullspace.",
            r"The residual lies in the row space, next to the minimizer.",
        ],
        1,
        r"Row space and nullspace are orthogonal complements in the domain. Adding a nullspace vector does not change \(Ax\), and the normal equations put the minimizer in the row space. The column space and the left nullspace split the codomain, which is where \(b\) and the residual live, not where \(x\) lives. The residual is orthogonal to the columns, so it is not in the row space.",
        MF, AF, ["linear-least-squares"],
    )
    b.save()


def bank_blocks():
    b = Bank("block-matrix-identities")
    b.mc(
        1,
        r"The review multiplies matrices by the row-column rule. For blocks that fit, the product \(\begin{bmatrix} A & B \\ C & D \end{bmatrix}\begin{bmatrix} E & F \\ G & H \end{bmatrix}\) equals",
        [
            r"\(\begin{bmatrix} AE+BG & AF+BH \\ CE+DG & CF+DH \end{bmatrix}\)",
            r"\(\begin{bmatrix} AE & BH \\ CG & DH \end{bmatrix}\)",
            r"\(\begin{bmatrix} A+E & B+F \\ C+G & D+H \end{bmatrix}\)",
            r"the matrix of entrywise products of corresponding blocks",
        ],
        0,
        r"Each block row meets each block column, and the products add, just as scalar entries do. The upper-left block is \(AE+BG\), not \(AE\) alone. Adding the blocks is the sum of the two matrices, which is a different operation. Entrywise products ignore the inner dimension that matrix multiplication uses.",
        MP, AP,
    )
    b.num(
        1,
        r"Compute the upper-left entry of \(\begin{bmatrix} 1 & 2 \\ 0 & 3 \end{bmatrix}\begin{bmatrix} 4 & 0 \\ 1 & 5 \end{bmatrix}\).",
        6, "(unitless)",
        r"The upper-left entry is \(1\cdot 4 + 2\cdot 1 = 6\). The product \(1\cdot 4 = 4\) drops the second term. The upper-right entry is \(1\cdot 0+2\cdot 5 = 10\). The lower-left entry is \(0\cdot 4+3\cdot 1 = 3\).",
        MP, AP,
    )
    b.mc(
        1,
        r"When the upper-left block \(A\) is invertible, the Schur complement of \(A\) in \(\begin{bmatrix} A & B \\ C & D \end{bmatrix}\) is",
        [
            r"\(A-BD^{-1}C\), whether or not \(D\) is invertible",
            r"\(D-CA^{-1}B\)",
            r"\(D-AB^{-1}C\)",
            r"\(A^{-1}D-BC\)",
        ],
        1,
        r"The complement of the invertible upper-left block is the lower-right block after the elimination step \(D-CA^{-1}B\). The complement of \(D\) would subtract from \(A\), and it needs \(D\) to be invertible, which is not the hypothesis. Swapping \(A\) with \(B\) uses a block the definition does not invert. Multiplying \(A^{-1}\) by \(D\) is not the elimination correction.",
        MB, AB,
    )
    b.order(
        2,
        "Put these steps in the order that computes the Schur complement of the upper-left block A.",
        [
            "Invert the upper-left block A.",
            "Multiply that inverse on the right by the upper-right block B.",
            "Multiply the lower-left block C on the left of that product.",
            "Subtract the resulting product from the lower-right block D.",
        ],
        r"The inverse has to exist before it can be multiplied by B. That product is what C then multiplies on the left. The subtraction removes the finished product from D, so it is last. Multiplying C by A before inverting A is a different association and is not one of these steps. Subtracting before the product exists leaves nothing to subtract.",
        MB, AB,
    )
    b.num(
        2,
        r"The blocks are the scalars \(A=5\), \(B=2\), \(C=10\), and \(D=9\). What is the Schur complement of \(A\)?",
        5, "(unitless)",
        r"The complement is \(9-10\cdot(1/5)\cdot 2 = 9-4 = 5\). Stopping at \(10/5 = 2\) forgets to multiply by \(B\) and to subtract from \(D\). The difference \(9-2 = 7\) subtracts \(B\) rather than \(CA^{-1}B\). The product \(10\cdot 2 = 20\) never inverts \(A\).",
        MB, AB,
    )
    b.num(
        2,
        r"For those same scalar blocks, the lower-right entry of the inverse is the reciprocal of the Schur complement. What is that entry?",
        0.2, "(unitless)",
        r"The complement is 5, and the lower-right entry of the inverse is \(1/5 = 0.2\). The complement 5 itself sits in the factored block diagonal, not in the inverse. The reciprocal of the block \(A\) is also \(1/5\) in this example, because the complement happens to equal \(A\). The identity being used is the reciprocal of the complement. The product \(5\cdot 9 = 45\) is not an entry of the inverse.",
        MB, AB,
    )
    b.sym(
        3,
        r"Let \(a\), \(b\), \(c\), and \(d\) be the four scalar blocks, with \(a \ne 0\). Write the Schur complement of \(a\) as an expression in a, b, c, and d.",
        "d - (c*b)/a",
        {"a": (1, 4), "b": (-2, 2), "c": (-2, 2), "d": (-2, 3)},
        r"For scalars the complement is \(d-c a^{-1} b\), which is \(d-(c b)/a\)."
        "\n"
        r"• \(d-c-b+a\) treats the blocks as a sum."
        "\n"
        r"• \(d-c\cdot b\) forgets to invert \(a\)."
        "\n"
        r"• \((d-c)/a\) divides the wrong difference and drops \(b\).",
        ["d - c*b/a", "(a*d - c*b)/a", "d - (b*c)/a"],
    )
    b.multi(
        3,
        r"The upper-left block \(A\) is invertible, and \(S = D-CA^{-1}B\) is invertible. Which statements are true?",
        [
            r"The whole block matrix is invertible.",
            r"Its determinant equals \(\det(A)\det(S)\).",
            r"The blocks multiply by the entrywise product.",
            r"The lower-right block of the inverse is \(S^{-1}\).",
        ],
        [0, 1, 3],
        r"Invertibility of \(A\) and of the Schur complement is the block test for invertibility, and the determinant factors as \(\det(A)\det(S)\). The inverse formula puts \(S^{-1}\) in the lower-right corner. Entrywise products are not matrix products.",
        MB, AB,
    )
    b.mc(
        3,
        r"A symmetric block matrix \(\begin{bmatrix} A & B \\ B^T & D \end{bmatrix}\) with \(A\) positive definite is itself positive definite exactly when",
        [
            r"\(D\) is diagonal",
            r"the trace of \(D\) is positive",
            r"the Schur complement \(D-B^T A^{-1} B\) is positive definite",
            r"\(B\) is the zero block",
        ],
        2,
        r"Completing the square in the quadratic form leaves the form of \(A\) plus the form of the Schur complement. Both must be positive definite. A positive trace of \(D\) does not control the complement. \(D\) need not be diagonal. \(B\) may be nonzero; the complement subtracts the correction \(B^T A^{-1} B\) instead of requiring \(B = 0\).",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The blocks are the scalars \(A=5\), \(B=2\), \(C=10\), and \(D=9\).",
        [
            r"The upper-left entry 5 is invertible.",
            r"The Schur complement of that entry is 9 - 10*(1/5)*2.",
            r"That value equals 9 - 1, so the complement is 8.",
            r"The 2 by 2 matrix is invertible because this complement is nonzero.",
        ],
        2,
        r"The entry 5 is invertible, and the complement really is \(9-10\cdot(1/5)\cdot 2\). That product is 4, so the complement is \(9-4 = 5\), not \(9-1\). A nonzero complement is the right invertibility test for this 2 by 2 matrix once the upper-left entry is nonzero. The arithmetic step is the false one.",
        reasons=[
            "The product 10*(1/5)*2 equals 4, so the complement is 5, not 8.",
            "The Schur complement adds the product to D, so the minus sign is the mistake.",
            "A 2 by 2 matrix is invertible exactly when the upper-left entry is nonzero, and the complement is irrelevant.",
        ],
        correct_reason=0,
        fig=MB, alt=AB, preview=["semidefinite-program"],
    )
    b.num(
        4,
        r"Let \(A = \begin{bmatrix} 1 & 0 \\ 0 & 2 \end{bmatrix}\), \(B = \begin{bmatrix} 2 \\ 2 \end{bmatrix}\), \(C = \begin{bmatrix} 1 & 2 \end{bmatrix}\), and \(D = \begin{bmatrix} 11 \end{bmatrix}\). A later semidefinite constraint needs the Schur complement of \(A\). What is that complement?",
        7, "(unitless)",
        r"\(A^{-1} = \mathrm{diag}(1,1/2)\), so \(A^{-1}B = (2,1)\). Then \(C A^{-1} B = 1\cdot 2+2\cdot 1 = 4\), and \(S = 11-4 = 7\). The value 11 is \(D\) before the correction. The product \(2\cdot 2 = 4\) happens to equal the correction, but only after \(A^{-1}\) is applied; subtracting \(B\)'s first entry alone gives \(11-2 = 9\). The determinant of \(A\) is 2, which is not the complement.",
        preview=["semidefinite-program"],
    )
    b.mc(
        4,
        r"A semidefinite constraint can say that a symmetric block matrix is positive semidefinite. When the upper-left block is positive definite, that constraint is the same as a constraint on",
        [
            r"the trace of the upper-left block alone",
            r"the Schur complement of the upper-left block",
            r"the product of all four blocks",
            r"the sum of the off-diagonal blocks",
        ],
        1,
        r"Positive definiteness of the upper-left block together with positive semidefiniteness of its Schur complement is the block test. The trace of one block does not see the coupling. The product of the four blocks is not a congruence. The sum of the off-diagonal blocks cancels in a symmetric matrix only when they are opposites, and that sum is not the complement.",
        preview=["semidefinite-program"],
    )
    b.save()


def bank_pca():
    b = Bank("principal-component-analysis")
    b.mc(
        1,
        r"Spectral decomposition writes a symmetric covariance as \(U D U^T\). Principal component analysis reads the leading principal direction as",
        [
            r"the eigenvector for the smallest eigenvalue of the covariance",
            r"any column of \(U\), because every eigenvalue is a variance of the same size",
            r"the eigenvector for the largest eigenvalue of the covariance",
            r"the diagonal entry of \(D\) itself, which is a vector in the sample space",
        ],
        2,
        r"The eigenvalues of the covariance are variances along the orthonormal eigenvectors. The greatest spread is the largest eigenvalue, and its eigenvector is the leading principal direction. The smallest eigenvalue is the tightest direction. A diagonal entry is the variance, not the direction.",
        ELL, AELL,
    )
    b.num(
        1,
        r"The centered rows are \((-1,2)\), \((-1,-2)\), and \((2,0)\). The covariance is the average of their outer products, dividing by the number of rows. What is its largest eigenvalue?",
        8 / 3, "(unitless)",
        r"The outer products sum to \(\mathrm{diag}(6,8)\), and dividing by 3 gives \(\mathrm{diag}(2,8/3)\). The larger eigenvalue is \(8/3\). The smaller one, 2, is the variance along the first coordinate. The trace \(2+8/3 = 14/3\) adds both variances. The largest centered coordinate has absolute value 2, and that coordinate is not an eigenvalue.",
    )
    b.mc(
        1,
        r"The same leading directions are the leading right singular vectors of the centered data matrix. Those vectors live in",
        [
            r"the sample space, one coordinate per row",
            r"the feature space, one coordinate per column",
            r"the space of eigenvalues of a nonsymmetric data matrix",
            r"the left nullspace of the covariance",
        ],
        1,
        r"If \(Z\) has one row per sample and one column per feature, the right singular vectors are eigenvectors of \(Z^T Z\), which has one entry per pair of features. They are directions in feature space. The left singular vectors have one coordinate per sample. The covariance is symmetric, so its eigenvalues are not a nonsymmetric decomposition. A zero eigenvalue of the covariance is a direction of no spread, not the definition of the leading component.",
        ELL, AELL,
    )
    b.order(
        2,
        "Put these steps in the order that finds the leading principal direction from a table of rows.",
        [
            "Subtract the mean of each column from that column.",
            "Average the outer products of the centered rows. The average is the covariance.",
            "Select the eigenvector of that covariance belonging to its largest eigenvalue.",
            "Scale the selected eigenvector to length 1.",
        ],
        r"The outer products are of the centered rows, so centering comes first. The eigenvector is an eigenvector of that covariance, so the covariance comes before the selection. The scaling step names the selected eigenvector, so it follows the selection. Scaling every vector of the original table before centering does not produce this eigenvector.",
        ELL, AELL,
    )
    b.num(
        2,
        r"The covariance is \(\mathrm{diag}(9,4)\). What is the variance along the unit vector \((3/5,4/5)\)?",
        5.8, "(unitless)",
        r"The variance along a unit vector \(u\) is \(u^T C u\). Here that is \((9)(9/25)+(4)(16/25) = (81+64)/25 = 145/25 = 5.8\). The larger eigenvalue 9 is the variance along \((1,0)\), not along this diagonal direction. The smaller eigenvalue 4 is the variance along \((0,1)\). The sum \(9+4 = 13\) is the trace.",
        MC, AC,
    )
    b.num(
        2,
        r"The covariance is \(\mathrm{diag}(9,4)\). What is the variance along the leading principal direction?",
        9, "(unitless)",
        r"The leading direction is the first coordinate axis, and the variance along it is the larger eigenvalue 9. The other eigenvalue 4 is the second principal variance. Their ratio \(9/4 = 2.25\) compares them and is not itself a variance along the leading axis. The square root \(\sqrt{9} = 3\) would be a singular value of a data matrix only after a further scaling by the number of rows.",
        MC, AC,
    )
    b.sym(
        3,
        r"Let the covariance be \(\mathrm{diag}(p,q)\) with \(p > 0\) and \(q > 0\). Write the variance along the unit vector \((3/5,4/5)\) as an expression in p and q.",
        "(9*p + 16*q)/25",
        {"p": (0.2, 5), "q": (0.2, 5)},
        r"Expand \(u^T C u\). The first coordinate contributes \(p\cdot(3/5)^2 = 9p/25\), and the second contributes \(16q/25\)."
        "\n"
        r"• \(p+q\) is the trace, the sum of the two axis variances."
        "\n"
        r"• \((3p+4q)/5\) weights the eigenvalues by the coordinates instead of by their squares."
        "\n"
        r"• \(9p+16q\) forgets to divide by the squared length of \((3,4)\).",
        ["9*p/25 + 16*q/25", "(9/25)*p + (16/25)*q"],
    )
    b.multi(
        3,
        r"Which statements describe the leading principal directions of a centered data matrix?",
        [
            r"They are leading eigenvectors of the covariance.",
            r"They are leading right singular vectors of the centered data.",
            r"They are leading left singular vectors of the centered data.",
            r"They belong to the smallest eigenvalues of the covariance.",
        ],
        [0, 1],
        r"The covariance \(\tfrac{1}{n} Z^T Z\) and the Gram matrix \(Z^T Z\) share eigenvectors. Those eigenvectors are the right singular vectors of \(Z\). The left singular vectors have one coordinate per row, so they are not feature directions. The smallest eigenvalues are the directions of least spread.",
        ELL, AELL,
    )
    b.mc(
        3,
        r"Centering is part of the definition used here. If the rows are not centered, the leading eigenvector of the average outer product tends to point toward",
        [
            r"the direction of least spread about the mean",
            r"the origin, regardless of the cloud",
            r"the mean of the cloud, rather than the spread about the mean",
            r"the left nullspace of the centered matrix",
        ],
        2,
        r"An uncentered outer product includes the mean. Its leading direction is pulled toward that mean. Centering removes the mean so the eigenvector measures spread. The least-spread direction is the smallest eigenvalue of the centered covariance. The origin is special only when the mean is already there. The left nullspace is a subspace of the sample space, not a feature direction.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The rows are \((0,2)\), \((0,-2)\), and \((3,0)\).",
        [
            r"The sample mean of the three rows is (1, 0).",
            r"Centering is optional here, because the leading eigenvector of the average uncentered outer product is the same direction as the leading eigenvector of the covariance.",
            r"After centering, the covariance is diagonal, with entries 2 and 8/3.",
            r"The leading principal component is the second coordinate direction.",
        ],
        1,
        r"The mean is \((1,0)\). The centered rows are \((-1,2)\), \((-1,-2)\), and \((2,0)\), and their average outer product is \(\mathrm{diag}(2,8/3)\), so the leading direction is the second axis. The uncentered average outer product is \(\mathrm{diag}(3,8/3)\), whose leading direction is the first axis. The two directions disagree, so centering is not optional for this table.",
        reasons=[
            "The uncentered average outer product of these rows leads along the first coordinate, while the centered covariance leads along the second.",
            "The mean is (0, 0), so the centering step used the wrong vector.",
            "The leading component is the smaller diagonal entry, so the last step names the wrong axis.",
        ],
        correct_reason=0,
        preview=["principal-components-regression"],
    )
    b.num(
        4,
        r"A later regression will use principal-component scores. The centered feature row is \((3,-1)\), and the leading direction is \((1,0)\). What is the score of this row on that direction?",
        3, "(unitless)",
        r"The score on a unit direction \(v\) is the inner product of the centered row with \(v\). Here that is \(3\cdot 1+(-1)\cdot 0 = 3\). The second coordinate \(-1\) is the score on \((0,1)\), which is the other axis. The sum of squares \(9+1 = 10\) is the squared distance from the origin, not a coordinate on one axis.",
        preview=["principal-components-regression"],
    )
    b.mc(
        4,
        r"Principal components regression will replace the feature row by a short list of scores. Which scores does that regression keep?",
        [
            r"the scores on the smallest eigenvalues, because those coordinates have been centered",
            r"the scores on the leading principal directions",
            r"the raw, uncentered features, because scores are only a plot",
            r"one score per row index, taken from the left singular vectors",
        ],
        1,
        r"The leading scores are the coordinates along the directions of greatest spread, which is the truncation a low-rank approximation keeps. The smallest eigenvalues are the directions that truncation drops. The raw features still contain the trailing directions. Left singular vectors index samples, not the feature coordinates of one row.",
        ELL, AELL, ["principal-components-regression"],
    )
    b.save()


def bank_lowrank():
    b = Bank("low-rank-approximation")
    b.mc(
        1,
        r"A singular value decomposition writes \(A\) as a sum of rank-one matrices, one per positive singular value. The rank-\(r\) truncation",
        [
            r"replaces every singular value by the largest one",
            r"drops the largest \(r\) singular values and keeps the rest",
            r"keeps the \(r\) largest singular values and sets the others to zero",
            r"keeps every singular vector and sets every singular value to 1",
        ],
        2,
        r"The factorization already orders the pieces by singular value. Truncation keeps the first \(r\) of those pieces and zeros the rest. Dropping the largest pieces throws away the terms the approximation is built from. Setting every remaining value to 1 changes the scale of the pieces that were kept. Copying the largest value into every slot is not a truncation.",
        MSIG, ASIG,
    )
    b.num(
        1,
        r"The singular values are 6, 3, and 2. What is the spectral-norm error of the rank-1 truncation?",
        3, "(unitless)",
        r"In the spectral norm the error equals the first discarded singular value, which is 3. The largest singular value 6 is the norm of \(A\), not of the error. The smallest value 2 is the error of the rank-2 truncation. The sum \(3+2 = 5\) adds every discarded value, which is not the spectral norm.",
        MSIG, ASIG,
    )
    b.mc(
        1,
        r"In the Frobenius norm, the squared error of a rank-\(r\) truncation equals",
        [
            r"the square of the largest singular value",
            r"the sum of the squares of the discarded singular values",
            r"the sum of the discarded singular values, without squares",
            r"the product of all singular values",
        ],
        1,
        r"The Frobenius norm squares every singular value and adds. After truncation, the kept values cancel in the difference, and the discarded values remain. The largest singular value alone is the spectral norm of \(A\). A sum without squares is a nuclear-norm accounting. The product of the singular values is a volume factor, not this error.",
        MSIG, ASIG,
    )
    b.order(
        2,
        "Put these steps in the order that builds the rank-r approximation from a singular value decomposition.",
        [
            "List the singular values from largest to smallest.",
            "Keep the first r values in that list and replace every later singular value by zero.",
            "Rebuild the matrix from the singular vectors that belong to the values you kept.",
        ],
        r"The list has to be ordered before 'the first r' means the largest r. The rebuild uses the values that were kept, so it follows the selection. Rebuilding from every singular vector and then deleting entries is not this procedure. Zeroing values before sorting would zero the wrong end of the list.",
        MSIG, ASIG,
    )
    b.num(
        2,
        r"The singular values are 6, 3, and 2. What is the Frobenius-norm error of the rank-1 truncation?",
        13 ** 0.5, "(unitless)",
        r"The discarded singular values are 3 and 2. The Frobenius error is \(\sqrt{9+4} = \sqrt{13}\). The spectral error is the single value 3. The sum \(3+2 = 5\) is not a Frobenius norm. The kept value 6 does not appear in the error.",
        MSIG, ASIG,
    )
    b.num(
        2,
        r"The singular values are 6, 3, and 2. What is the Frobenius-norm error of the rank-2 truncation?",
        2, "(unitless)",
        r"Only the last singular value is discarded. Its square root of a square is the value itself, so the Frobenius error is 2. The spectral error of this same truncation is also 2, because one discarded value is both the largest discarded value and the square root of the sum of squares of the discarded values. The rank-1 Frobenius error \(\sqrt{13}\) still includes the middle singular value. The sum of all three singular values is 11.",
        MSIG, ASIG,
    )
    b.sym(
        3,
        r"Let the singular values be \(u > 0\) and \(v > 0\). The rank-0 truncation is the zero matrix. Write its Frobenius distance to the original matrix as an expression in u and v.",
        "sqrt(u**2 + v**2)",
        {"u": (0.3, 4), "v": (0.3, 4)},
        r"Every singular value is discarded. The Frobenius norm is the square root of the sum of their squares."
        "\n"
        r"• \(u+v\) is the nuclear norm, not the Frobenius norm."
        "\n"
        r"• \(\max(u,v)\) is the spectral norm."
        "\n"
        r"• \(u^2+v^2\) stops before the square root.",
        ["sqrt(u*u + v*v)", "(u**2 + v**2)**(1/2)"],
    )
    b.multi(
        3,
        r"Which statements are true of the truncation that keeps the \(r\) largest singular values?",
        [
            r"It is a nearest matrix of rank at most \(r\) in the Frobenius norm.",
            r"It is a nearest matrix of rank at most \(r\) in the spectral norm.",
            r"Its spectral-norm error equals the largest discarded singular value.",
            r"Its Frobenius-norm error equals the largest discarded singular value, for every list of singular values.",
        ],
        [0, 1, 2],
        r"The truncation theorem gives both the Frobenius claim and the spectral claim, and the spectral error is exactly the next singular value. The Frobenius error is the square root of a sum of squares. That equals the next singular value only when every later singular value is zero.",
        MSIG, ASIG,
    )
    b.mc(
        3,
        r"If the singular values are 6, 3, and 2, the rank-1 matrix in the truncation is",
        [
            r"6 times the outer product of the first left singular vector and the first right singular vector",
            r"the sum of all three outer products, each scaled by 6",
            r"3 times the outer product of the second pair of singular vectors",
            r"the diagonal matrix of all three singular values",
        ],
        0,
        r"Each term in the decomposition is one singular value times one outer product. The leading term uses the largest value, 6, and the first pair of vectors. Scaling every term by 6 does not zero the smaller values. The middle term is part of the error of the rank-1 approximation, not the approximation. The diagonal matrix of singular values is the middle factor of the decomposition, not the reconstructed matrix, unless the singular vectors are the identity.",
        MSIG, ASIG,
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The singular values are 6, 3, and 2.",
        [
            r"In decreasing order the singular values are 6, 3, and 2.",
            r"The rank-1 truncation keeps 6 and replaces 3 and 2 by 0.",
            r"The spectral-norm error of that truncation equals the square root of 3 squared plus 2 squared.",
            r"The Frobenius-norm error of that truncation equals the square root of 3 squared plus 2 squared.",
        ],
        2,
        r"The ordered list and the decision to keep only 6 are the truncation. The Frobenius error really is \(\sqrt{9+4}\). The spectral error is the first discarded singular value, 3, not that square root. The false step assigns the Frobenius formula to the spectral norm.",
        reasons=[
            "The spectral-norm error equals the first discarded singular value, which is 3, not the square root of the sum of squares.",
            "The spectral-norm error equals the largest singular value, which is 6.",
            "Both norms add the discarded singular values, so the square root is the mistake in the Frobenius step.",
        ],
        correct_reason=0,
        fig=MSIG, alt=ASIG, preview=["principal-components-regression"],
    )
    b.num(
        4,
        r"A later regression keeps only the leading principal component of a centered matrix whose singular values are 6, 3, and 2. What fraction of the squared Frobenius energy is kept?",
        36 / 49, "(unitless)",
        r"Squared Frobenius energy is the sum of squares of the singular values, \(36+9+4 = 49\). The leading piece contributes 36, so the fraction is \(36/49\). The fraction \(45/49\) also keeps the middle value. The fraction \(6/11\) uses the singular values without squaring. The discarded fraction \(13/49\) is the energy the rank-1 truncation throws away.",
        MSIG, ASIG, ["principal-components-regression"],
    )
    b.mc(
        4,
        r"Principal components regression drops the trailing right singular vectors of the centered predictors. That choice is the same as",
        [
            r"replacing the predictor matrix by its rank-\(r\) truncation before reading coordinates",
            r"replacing the predictor matrix by a rank-\(r\) matrix that zeros the largest singular values",
            r"keeping every singular value and dropping the response",
            r"using the left singular vectors as the regression coefficients",
        ],
        0,
        r"The coordinates on the leading right singular vectors are the coordinates in the rank-\(r\) truncation. Zeroing the largest singular values keeps the noise the truncation is meant to drop. The response is the quantity being fitted, not a singular vector to discard. Left singular vectors describe samples, not the coefficient of a feature direction.",
        MSIG, ASIG, ["principal-components-regression"],
    )
    b.save()


def bank_perturb():
    b = Bank("least-squares-perturbation")
    b.mc(
        1,
        r"The induced 2-norm of a full-column-rank matrix is its largest singular value. The least-squares condition number used here is",
        [
            r"the difference of the largest and the smallest singular values",
            r"the ratio of the largest singular value to the smallest",
            r"the square of the largest singular value alone",
            r"the factor \((( \kappa-1)/( \kappa+1))^2\) from exact line search on a quadratic",
        ],
        1,
        r"Both singular values enter. The condition number is \(\sigma_{\max}/\sigma_{\min}\). Their difference is not dimensionless in a way that matches a relative error, and it is not the ratio. The square of \(\sigma_{\max}\) is an eigenvalue of \(A^T A\), not the condition number of \(A\). The squared factor with \((\kappa-1)/(\kappa+1)\) bounds a gradient iteration on a quadratic, which is a different condition number.",
    )
    b.num(
        1,
        r"The singular values of \(A\) are 10 and 2. What is the least-squares condition number \(\sigma_{\max}/\sigma_{\min}\)?",
        5, "(unitless)",
        r"The ratio is \(10/2 = 5\). The difference \(10-2 = 8\) is not the condition number. The product \(10\cdot 2 = 20\) is not a ratio. The condition number of \(A^T A\) would square the ratio and give 25, which is a later question about the normal matrix.",
    )
    b.mc(
        1,
        r"The pseudoinverse of a full-column-rank \(A\) has induced 2-norm",
        [
            r"\(\sigma_{\max}\)",
            r"\(\sigma_{\max}/\sigma_{\min}\)",
            r"\(1/\sigma_{\min}\)",
            r"\(\sigma_{\min}\)",
        ],
        2,
        r"The nonzero singular values of the pseudoinverse are the reciprocals of the singular values of \(A\). The largest of those reciprocals is \(1/\sigma_{\min}\). The norm of \(A\) itself is \(\sigma_{\max}\). The condition number is the product of those two norms, not the norm of the pseudoinverse alone.",
    )
    b.order(
        2,
        r"The residual is zero, \(A\) is fixed, and \(b\) changes. Put these steps in the order that bounds the relative change in the least-squares solution.",
        [
            "Divide the largest singular value by the smallest singular value. Call the quotient kappa.",
            "Multiply kappa by the size of the change in b.",
            "Divide that product by the size of b. The quotient bounds the relative change in x.",
        ],
        r"The ratio of singular values is κ, and the next step multiplies that value by \(\lVert\delta b\rVert\). The division by \(\lVert b\rVert\) uses the product just formed. Dividing the singular values in the opposite order produces \(1/\kappa\), and the later steps would then bound the wrong quantity. Dividing by \(\lVert b\rVert\) before κ exists is not this sequence.",
    )
    b.num(
        2,
        r"The smallest singular value of \(A\) is 0.4, and \(b\) changes by a vector of length 0.2. The change in the least-squares solution has length at most \(1/\sigma_{\min}\) times the change in \(b\). What is that upper bound?",
        0.5, "(unitless)",
        r"The pseudoinverse norm is \(1/0.4 = 2.5\), and \(2.5\cdot 0.2 = 0.5\). The product \(0.4\cdot 0.2 = 0.08\) multiplies by the singular value instead of dividing by it. The change in \(b\) alone, 0.2, is not yet scaled by the pseudoinverse. Twice the change, 0.4, happens to equal \(\sigma_{\min}\) and is not the bound.",
    )
    b.num(
        2,
        r"The condition number is 5, the residual is zero, \(\lVert b\rVert = 4\), and \(\lVert\delta b\rVert = 0.2\). The relative change in \(x\) is at most κ times the relative change in \(b\). What is that upper bound?",
        0.25, "(unitless)",
        r"The relative change in \(b\) is \(0.2/4 = 0.05\), and \(5\cdot 0.05 = 0.25\). The absolute bound \(5\cdot 0.2 = 1\) forgets to divide by \(\lVert b\rVert\). The condition number alone, 5, is not a relative change in \(x\). Dividing the condition number by \(\lVert\delta b\rVert\) gives \(5/0.2 = 25\), which inverts the role of the perturbation.",
    )
    b.sym(
        3,
        r"Let smax and smin be the largest and smallest singular values, both positive. Write the least-squares condition number as an expression in smax and smin.",
        "smax/smin",
        {"smax": (2, 8), "smin": (0.2, 1.5)},
        r"The condition number in this skill is the ratio \(\sigma_{\max}/\sigma_{\min}\)."
        "\n"
        r"• \(\mathrm{smax}-\mathrm{smin}\) is a difference."
        "\n"
        r"• \(\mathrm{smax}\cdot\mathrm{smin}\) is a product."
        "\n"
        r"• \(\mathrm{smax}^2/\mathrm{smin}^2\) is the condition number of \(A^T A\), not of \(A\).",
        ["smax*(1/smin)", "(smax)/(smin)"],
    )
    b.multi(
        3,
        r"The residual is zero and the columns are independent. The relative change in \(x\) is at most κ times the relative size of which perturbations?",
        [
            r"a small change in \(b\), with \(A\) fixed",
            r"a small change in \(A\), with \(b\) fixed",
            r"a change in \(A\) when the residual is not zero, still with only one factor of κ and no worse power",
            r"the gradient-iteration factor \(((κ-1)/(κ+1))^2\), used in place of κ",
        ],
        [0, 1],
        r"With a zero residual, both a change in \(b\) and a change in \(A\) produce a relative change in \(x\) bounded by κ times the relative perturbation. A nonzero residual lets a change in \(A\) act through \((A^T A)^{-1}\) on a term with \(r\), and that term carries \(1/\sigma_{\min}^2\), a square of the condition number. The squared factor \(((κ-1)/(κ+1))^2\) is the exact-line-search factor on a quadratic, not this least-squares ratio.",
    )
    b.mc(
        3,
        r"When the residual is not zero, a small change in \(A\) can move \(x\) through the term \((A^T A)^{-1}(\delta A)^T r\). The normal matrix \(A^T A\) has smallest eigenvalue",
        [
            r"\(\sigma_{\max}\)",
            r"\(\sigma_{\min}^2\)",
            r"\(\sigma_{\max}/\sigma_{\min}\)",
            r"\(\sigma_{\min}\)",
        ],
        1,
        r"The eigenvalues of \(A^T A\) are the squares of the singular values of \(A\). The smallest one is \(\sigma_{\min}^2\), so the inverse can be as large as \(1/\sigma_{\min}^2\). The singular value \(\sigma_{\min}\) is the square root of that eigenvalue. The condition number and \(\sigma_{\max}\) are not eigenvalues of the normal matrix.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The singular values are 10 and 2, and the residual of the least-squares fit is zero.",
        [
            r"The induced 2-norm of A is 10.",
            r"The least-squares condition number is 10/2 = 5.",
            r"This condition number is the same number as ((5-1)/(5+1))^2, the exact-line-search factor on a quadratic.",
            r"A relative change in b, with A fixed and a zero residual, changes x by a relative amount at most 5 times that relative change.",
        ],
        2,
        r"The induced 2-norm is the largest singular value, and the least-squares condition number is the ratio 5. With a zero residual, a relative change in \(b\) is multiplied by at most that ratio. The false step identifies the ratio with \(((κ-1)/(κ+1))^2\). For κ = 5 that factor is \((4/6)^2 = 4/9\), which is not 5. It bounds a different algorithm.",
        reasons=[
            "The singular-value ratio bounds the least-squares map. The squared factor ((kappa-1)/(kappa+1))^2 bounds exact line search on a quadratic.",
            "The condition number is 10-2, so the division step is the false one.",
            "A zero residual removes the condition number, so the last step cannot hold.",
        ],
        correct_reason=0,
        preview=["ridge-regression"],
    )
    b.num(
        4,
        r"Ridge regression will add a positive shift to the normal matrix. For singular values 10 and 2, the condition number of \(A^T A\) is the square of \(\sigma_{\max}/\sigma_{\min}\). What is that condition number?",
        25, "(unitless)",
        r"The eigenvalues of \(A^T A\) are 100 and 4. Their ratio is \(100/4 = 25\), which is \(5^2\). The condition number of \(A\) itself is 5, without the square. The sum of the eigenvalues is 104. The smaller eigenvalue 4 is not a condition number.",
        preview=["ridge-regression"],
    )
    b.mc(
        4,
        r"A large condition number of \(A^T A\) is the reason a later ridge penalty shifts that matrix. The shift \(\lambda I\) with \(\lambda > 0\)",
        [
            r"subtracts \(\lambda\) from every eigenvalue and can make them negative",
            r"adds \(\lambda\) to every eigenvalue of \(A^T A\), including the smallest",
            r"replaces the condition number by \(((κ-1)/(κ+1))^2\)",
            r"sets every singular value of \(A\) equal to 1",
        ],
        1,
        r"The eigenvalues of \(A^T A+\lambda I\) are the eigenvalues of \(A^T A\) plus \(\lambda\). The smallest one moves from \(\sigma_{\min}^2\) to \(\sigma_{\min}^2+\lambda\), which is positive. Subtracting \(\lambda\) is the opposite shift. The line-search factor is not this matrix. Setting singular values to 1 would replace \(A\), not damp the normal matrix.",
        preview=["ridge-regression"],
    )
    b.save()


def bank_ridge():
    b = Bank("ridge-regression")
    b.mc(
        1,
        r"The squared residual \(\lVert Ax-b\rVert^2\) has gradient \(2A^T(Ax-b)\). Ridge adds \(\lambda\lVert x\rVert^2\) with \(\lambda > 0\). Setting the full gradient to zero gives",
        [
            r"\((A^T A+\lambda I)x = A^T b\)",
            r"\((A^T A)x = A^T b+\lambda x\)",
            r"\((A+\lambda I)x = b\)",
            r"\(A^T A x = \lambda A^T b\)",
        ],
        0,
        r"The penalty \(\lambda\lVert x\rVert^2\) contributes \(2\lambda x\) to the gradient. Moving that term to the left adds \(\lambda I\) to \(A^T A\). Leaving \(\lambda x\) on the right of the unshifted normal equation hides the unknown \(x\). Adding \(\lambda I\) to \(A\) is not the gradient of the penalty. Scaling only the right-hand side by \(\lambda\) is a different objective.",
    )
    b.num(
        1,
        r"One coefficient, two observations: the column of \(A\) is \((1,1)\), \(b = (3,1)\), and \(\lambda = 2\). What is the ridge solution?",
        1, "(unitless)",
        r"\(A^T A = 2\) and \(A^T b = 4\). The shifted equation is \((2+2)x = 4\), so \(x = 1\). Ordinary least squares would divide 4 by 2 and give 2. Dividing by \(\lambda\) alone gives \(4/2 = 2\) as well, and it drops the Gram entry. The mean of the observations is 2, which is not the coefficient.",
    )
    b.mc(
        1,
        r"Positive definite matrices are the ones whose eigenvalues are positive. For \(\lambda > 0\), the ridge matrix \(A^T A+\lambda I\) is",
        [
            r"positive definite only when \(A\) already has independent columns",
            r"positive definite whether or not the columns of \(A\) are independent",
            r"singular whenever \(A\) is singular",
            r"indefinite, because \(\lambda I\) subtracts from the eigenvalues",
        ],
        1,
        r"Every eigenvalue of \(A^T A\) is at least 0, and adding \(\lambda > 0\) makes every eigenvalue at least \(\lambda\). Independent columns are not required. A singular \(A\) makes \(A^T A\) singular, but the shift removes that singularity. The shift adds, so it does not make the form indefinite.",
    )
    b.order(
        2,
        "Put these steps in the order that solves a ridge problem with penalty weight lambda.",
        [
            "Form the Gram matrix A^T A and the vector A^T b.",
            "Add lambda to each diagonal entry of that Gram matrix.",
            "Solve the shifted linear system for x.",
        ],
        r"The shift is applied to the Gram matrix, so the Gram matrix comes first. The solve uses the shifted matrix, so it comes after the addition. Adding \(\lambda\) to \(A\) before forming \(A^T A\) is a different algorithm and is not these steps. Solving the unshifted system first produces ordinary least squares, not the system written in the last step.",
        MAB, AAB,
    )
    b.num(
        2,
        r"Let \(A = \begin{bmatrix} 1 & 0 \\ 1 & 0 \\ 0 & 1 \end{bmatrix}\), \(b = \begin{bmatrix} 4 \\ 0 \\ 2 \end{bmatrix}\), and \(\lambda = 1\). What is the second coordinate of the ridge solution?",
        1, "(unitless)",
        r"\(A^T A = \mathrm{diag}(2,1)\) and \(A^T b = (4,2)\). After the shift, the second equation is \((1+1)x_2 = 2\), so \(x_2 = 1\). Ordinary least squares would leave the second diagonal entry at 1 and give \(x_2 = 2\). The first ridge coordinate is \(4/3\), not the second. The observation 2 is the third entry of \(b\), and it is also the second entry of \(A^T b\). The shift leaves that entry alone and changes the diagonal, so the solution's second coordinate is \(2/2 = 1\), not the entry 2 itself.",
        MAB, AAB,
    )
    b.num(
        2,
        r"For the same \(A\), \(b\), and \(\lambda = 1\), what is the first coordinate of the ridge solution?",
        4 / 3, "(unitless)",
        r"The shifted first equation is \((2+1)x_1 = 4\), so \(x_1 = 4/3\). Ordinary least squares divides 4 by 2 and gives 2. The second ridge coordinate is 1. The sum of the two ridge coordinates is \(7/3\), which is not the first coordinate.",
        MAB, AAB,
    )
    b.sym(
        3,
        r"Let \(t > 0\) and \(\mathrm{lam} > 0\). The column of \(A\) is \((t,t)\), the right-hand side is \((t,0)\), and the penalty weight is lam. Write the ridge solution as an expression in t and lam.",
        "t**2/(2*t**2 + lam)",
        {"t": (0.5, 2), "lam": (0.2, 3)},
        r"\(A^T A = 2t^2\) and \(A^T b = t^2\). The shifted scalar equation is \((2t^2+\mathrm{lam})x = t^2\)."
        "\n"
        r"• \(t^2/(2t^2)\) is ordinary least squares, with the penalty left out."
        "\n"
        r"• \(t/(2t+\mathrm{lam})\) cancels only one factor of \(t\) and is a different function."
        "\n"
        r"• \(\mathrm{lam}/(2t^2)\) inverts the roles of the Gram entry and the penalty.",
        ["(t*t)/(2*(t*t)+lam)", "1/(2 + lam/(t*t))"],
    )
    b.multi(
        3,
        r"Which statements match the penalty \(\lVert Ax-b\rVert^2+\lVert\Gamma x\rVert^2\)?",
        [
            r"The stationarity equation is \((A^T A+\Gamma^T\Gamma)x = A^T b\).",
            r"Ridge is the case \(\Gamma = \sqrt{\lambda}\, I\).",
            r"The shift \(\Gamma^T\Gamma\) can be any symmetric positive semidefinite matrix of that form.",
            r"The penalty \(\lVert\Gamma x\rVert^2\) is the same term as \(\lambda\lVert x\rVert_1\).",
        ],
        [0, 1, 2],
        r"The gradient of \(\lVert\Gamma x\rVert^2\) contributes \(2\Gamma^T\Gamma x\), so the normal matrix gains \(\Gamma^T\Gamma\). Choosing \(\Gamma = \sqrt{\lambda}\, I\) recovers \(\lambda I\). Any Gram matrix \(\Gamma^T\Gamma\) is symmetric and positive semidefinite. The absolute penalty \(\lambda\lVert x\rVert_1\) is a different function, and its stationarity condition is not this linear shift.",
    )
    b.mc(
        3,
        r"Compared with ordinary least squares, a ridge solution with \(\lambda > 0\)",
        [
            r"always has a larger Euclidean norm, because the penalty adds a positive term",
            r"is unchanged, because the normal equations already have a unique solution",
            r"cannot be computed unless \(A^T A\) is invertible",
            r"has a smaller or equal Euclidean norm, with equality only in degenerate cases such as a zero right-hand side",
        ],
        3,
        r"The ridge objective charges \(\lambda\lVert x\rVert^2\), so the minimizer does not move farther from the origin than the ordinary minimizer. When the ordinary solution is already zero, both solutions are zero. A positive \(\lambda\) changes a nonzero ordinary solution. The shifted matrix is invertible for \(\lambda > 0\) even when \(A^T A\) is not.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. Here \(A = \begin{bmatrix} 1 & 0 \\ 1 & 0 \\ 0 & 1 \end{bmatrix}\), \(b = \begin{bmatrix} 4 \\ 0 \\ 2 \end{bmatrix}\), and \(\lambda = 1\).",
        [
            r"A^T A = diag(2, 1) and A^T b = (4, 2).",
            r"Adding lambda on the diagonal produces diag(3, 2).",
            r"The ridge minimizer equals the ordinary least-squares minimizer, because a positive lambda does not move the solution.",
            r"Solving the shifted system produces x = (4/3, 1).",
        ],
        2,
        r"The Gram matrix and the shifted diagonal are correct, and the shifted system does solve to \((4/3, 1)\). Ordinary least squares solves \(\mathrm{diag}(2,1)x = (4,2)\) and gets \((2, 2)\), which is a different point. A positive penalty moves a nonzero ordinary solution. The false step is the claim that the minimizer is unchanged.",
        reasons=[
            "Adding lambda I moves the eigenvalues, so the minimizer changes unless the ordinary solution is already zero.",
            "The shift should be added to A before multiplying by A^T, and that is the false step.",
            "The right-hand side should be divided by lambda, so the reported solution is the false step.",
        ],
        correct_reason=0,
        fig=MAB, alt=AAB, preview=["maximum-a-posteriori-estimation"],
    )
    b.num(
        4,
        r"A later absolute penalty is different, but the general squared penalty is still this skill. Take \(A = I\), \(b = (1,3)\), and \(\Gamma = \mathrm{diag}(2,0)\). What is the first coordinate of the minimizer of \(\lVert Ax-b\rVert^2+\lVert\Gamma x\rVert^2\)?",
        0.2, "(unitless)",
        r"\(\Gamma^T\Gamma = \mathrm{diag}(4,0)\), so the shifted matrix is \(\mathrm{diag}(5,1)\). The first equation is \(5x_1 = 1\), hence \(x_1 = 1/5\). The second coordinate stays 3, because \(\Gamma\) does not charge it. Ordinary least squares would leave \(x_1 = 1\). Using \(\Gamma\) instead of \(\Gamma^T\Gamma\) would shift the first diagonal by 2 and give \(1/3\).",
        preview=["lasso-regression"],
    )
    b.mc(
        4,
        r"A Gaussian prior on the coefficients, with mean zero and covariance proportional to \(I/\lambda\), has a negative log density equal to a constant plus \(\lambda\lVert x\rVert^2\). Maximizing likelihood times that prior is",
        [
            r"ordinary least squares, because a prior does not change the maximizer",
            r"an absolute penalty on \(x\)",
            r"the ridge problem with penalty weight \(\lambda\)",
            r"a shift added to \(A\) rather than to \(A^T A\)",
        ],
        2,
        r"The log of a spherical Gaussian prior is a squared Euclidean penalty, up to scaling and an additive constant. Adding it to the squared residual is ridge. An absolute penalty is a different prior, with a Laplacian shape. A prior changes the maximizer whenever \(\lambda > 0\) and the ordinary solution is nonzero. The algebra of the gradient puts the shift on \(A^T A\).",
        preview=["maximum-a-posteriori-estimation"],
    )
    b.save()


def bank_pcr():
    b = Bank("principal-components-regression")
    b.mc(
        1,
        r"Principal component analysis hands you orthonormal directions. Data fitting solves a least-squares problem in its coefficients. Principal components regression",
        [
            r"runs that least-squares fit in the leading principal-component scores",
            r"runs the fit in the trailing principal-component scores and drops the leading ones",
            r"replaces the response by the largest singular value",
            r"stops after choosing the directions and does not fit a coefficient",
        ],
        0,
        r"The directions are the prerequisite. This skill uses them as a new design matrix and fits ordinary least squares there. The trailing directions are the ones a low-rank truncation drops, not the ones the regression keeps. The singular value is a scale of a direction, not a substitute for the response. Choosing directions without a fit is principal component analysis alone.",
    )
    b.num(
        1,
        r"The centered scores on the single kept component are \(2\), \(0\), and \(-2\). The centered response is \(4\), \(1\), and \(-2\). The least-squares coefficient is the inner product of the scores with the response, divided by the squared length of the scores. What is that coefficient?",
        1.5, "(unitless)",
        r"The inner product is \(2\cdot 4+0\cdot 1+(-2)\cdot(-2) = 12\). The squared length is \(4+0+4 = 8\). The coefficient is \(12/8 = 1.5\). The average of the centered response is \(1\), and centering already removed the mean, so the average is not the coefficient. Dividing 12 by the length \(\sqrt{8}\) instead of by the squared length gives a different normalization.",
    )
    b.mc(
        1,
        r"Low-rank approximation says the trailing singular components are the ones to drop. In principal components regression those dropped components",
        [
            r"become the intercept",
            r"are the columns of the reduced design",
            r"are left out of the reduced design",
            r"replace the response",
        ],
        2,
        r"The reduced design keeps the leading scores and omits the trailing ones. The intercept, when the response was centered, is the mean of the response, not a discarded component. The response stays the response.",
    )
    b.order(
        2,
        "Put these steps in the order that fits a principal-components regression.",
        [
            "Subtract each predictor column's mean from that column.",
            "Take the leading principal-component directions of that centered predictor matrix.",
            "Replace each centered predictor row by its coordinates along those directions.",
            "Solve ordinary least squares for the centered response in those coordinates.",
        ],
        r"The directions are computed from the centered predictors, so centering comes first. The coordinates are inner products with those directions, so the directions come before the coordinates. The least-squares solve uses the coordinates as its design, so it is last. Solving least squares on the raw columns is ordinary data fitting, and it is not the last step written here.",
    )
    b.num(
        2,
        r"The kept right singular vector is a unit vector, and the centered predictor matrix has singular value 4 in that direction. The score column is the centered matrix times the singular vector. What is the squared length of the score column?",
        16, "(unitless)",
        r"Multiplying by a unit right singular vector scales the corresponding left direction by the singular value, so the score column has length 4 and squared length 16. The singular value 4 itself is the length, not the squared length. The square root of 4 is 2, which would be a standard deviation only under a further convention about the number of rows. A squared length of 1 would mean the singular vector had been used without the data matrix.",
    )
    b.num(
        2,
        r"That same score column has squared length 16, and its inner product with the centered response is 8. What is the least-squares coefficient on this component?",
        0.5, "(unitless)",
        r"One column has normal equation \(\lVert z\rVert^2\,\theta = z^T y\). Thus \(\theta = 8/16 = 1/2\). Dividing by the singular value 4 instead of by its square gives 2, which treats the score column as if it had length 1. The inner product 8 alone is not a coefficient. The product \(8\cdot 16 = 128\) multiplies the two ingredients.",
    )
    b.sym(
        3,
        r"Let \(p\) be the inner product of one score column with the centered response, and let \(s > 0\) be the singular value of that component. The score column comes from a unit right singular vector. Write the least-squares coefficient as an expression in p and s.",
        "p/(s**2)",
        {"p": (0.5, 4), "s": (0.5, 3)},
        r"The normal equation for one column divides the inner product by the squared length, and that squared length is \(s^2\)."
        "\n"
        r"• \(p/s\) divides by the length rather than by the squared length."
        "\n"
        r"• \(s^2/p\) inverts the coefficient."
        "\n"
        r"• \(p\cdot s^2\) multiplies the two ingredients.",
        ["p/(s*s)", "(p)/(s**2)"],
    )
    b.multi(
        3,
        r"Which statements describe the regression in this skill?",
        [
            r"The design columns are scores on leading principal directions.",
            r"Trailing principal directions are left out of the design.",
            r"The fit uses the smallest principal components and drops the leading ones.",
            r"A prediction in the original units is the centered prediction plus the mean of the response.",
        ],
        [0, 1, 3],
        r"The design is the leading scores, which is the low-rank choice of which directions to keep. The smallest components are the ones left out. Centering the response removes its mean before the fit, so a prediction in the original scale adds that mean back. The coefficients themselves stay in the score coordinates.",
    )
    b.mc(
        3,
        r"If the kept score columns are orthogonal, the least-squares coefficient on one of them",
        [
            r"depends on the other coefficients and requires a joint matrix solve",
            r"equals the inner product of that score column with the response, divided by the squared length of that column",
            r"equals the singular value of that component",
            r"is zero whenever the singular value is positive",
        ],
        1,
        r"Orthogonal columns make the Gram matrix diagonal, so each normal equation stands alone. The coefficient is the inner product divided by the squared length. The singular value is the length of the score column, not the coefficient. A positive singular value says the column is nonzero, so the coefficient is zero only when the response is orthogonal to that column.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The centered predictors have singular values 4 and 1.",
        [
            r"Principal components regression keeps the leading direction and drops the trailing one.",
            r"The kept right singular vector may be scaled to length 1.",
            r"The kept score column has squared length 4, because the singular value is already the Gram entry.",
            r"If that score column has inner product 8 with the centered response, the coefficient is 8/16.",
        ],
        2,
        r"Keeping the leading direction is the low-rank choice, and a right singular vector is a unit vector in the usual decomposition. The score column is the centered matrix times that unit vector, so its length is the singular value 4 and its squared length is 16. The last step divides 8 by 16, which is the correct Gram entry. The false step puts the unsquared singular value in the Gram matrix.",
        reasons=[
            "The score column is the centered matrix times a unit singular vector, so its squared length is the square of the singular value, 16.",
            "Regression keeps the smallest singular value, so the selection step is the false one.",
            "The coefficient divides by the singular value rather than its square, and 8/4 is the right value.",
        ],
        correct_reason=0,
        preview=["lasso-regression"],
    )
    b.num(
        4,
        r"The mean of the response is 5. A new centered predictor has score 2 on the single kept component, and the coefficient on that component is \(1/2\). What is the prediction in the original response scale?",
        6, "(unitless)",
        r"The centered prediction is \(2\cdot(1/2) = 1\). Adding the mean of the response gives \(5+1 = 6\). The score 2 alone forgets the coefficient. The product \(5\cdot 2 = 10\) multiplies the mean by the score. The centered prediction 1 is not yet in the original scale.",
        preview=["lasso-regression"],
    )
    b.mc(
        4,
        r"A later absolute penalty can shrink individual coefficients without first discarding a whole principal direction. Principal components regression, by contrast,",
        [
            r"shrinks every coefficient by the same ridge weight and keeps every direction",
            r"discards the trailing directions and leaves the kept coefficients unpenalized",
            r"replaces the squared residual by an absolute residual",
            r"fits the response in the original features and ignores the principal directions",
        ],
        1,
        r"Once the trailing directions are dropped, the fit on the kept scores is ordinary least squares, with no further penalty. A uniform ridge weight on every original coefficient is ridge regression, which keeps every direction and shrinks them all. An absolute residual would change the loss, not just the coordinates. Ignoring the principal directions is ordinary data fitting.",
        preview=["lasso-regression"],
    )
    b.save()


def bank_mle():
    b = Bank("maximum-likelihood-estimation")
    b.mc(
        1,
        r"A Gaussian random vector is summarized by a mean and a covariance. Independent residuals with equal variance \(\sigma^2\) have covariance \(\sigma^2 I\). For a linear mean \(Ax\), the value of \(x\) that maximizes the density is",
        [
            r"the ordinary least-squares fit",
            r"the fit that maximizes \(\lVert Ax-b\rVert^2\)",
            r"the fit that sets every residual equal to \(\sigma\)",
            r"a different vector for every positive \(\sigma\)",
        ],
        0,
        r"The log density contains \(-\lVert b-Ax\rVert^2/(2\sigma^2)\) plus terms that do not depend on \(x\). Because the factor \(1/(2\sigma^2)\) is positive, maximizing the density minimizes the squared residual. That minimizer is the least-squares fit from data fitting. Maximizing the squared residual would look for the worst fit. Setting residuals equal to \(\sigma\) confuses the noise scale with the mean. The same \(x\) wins for every \(\sigma > 0\).",
    )
    b.num(
        1,
        r"Six independent residuals have sum of squares 18. The maximum-likelihood estimate of their common variance is the sum of squares divided by the number of residuals. What is that estimate?",
        3, "(unitless)",
        r"Divide 18 by 6 to get 3. Dividing by \(6-1 = 5\) is a different unbiased correction, not the maximizer of the Gaussian likelihood. The square root \(\sqrt{3}\) is a standard deviation. Twice the sum of squares, 36, is the piece that sits next to \(1/(2\sigma^2)\) before \(\sigma^2\) is estimated.",
    )
    b.mc(
        1,
        r"Data fitting minimizes \(\lVert Ax-b\rVert^2\). Under this Gaussian model, that minimization is maximum likelihood for \(x\) only when",
        [
            r"the variances are equal. Unequal variances replace it by a weighted sum of squares",
            r"the variances are unequal. Equal variances replace it by a weighted sum of squares",
            r"the noise is Gaussian with a nonzero mean that depends on \(x\) through a prior",
            r"the covariance is a full matrix with no special structure, and the loss is still the plain squared length",
        ],
        0,
        r"Equal diagonal entries let one factor \(1/\sigma^2\) come out of the sum, so the maximizer does not depend on the weights. Unequal variances leave a weighted sum of squares. A prior on \(x\) is a later posterior step, not part of the likelihood. A full covariance produces a quadratic form \(r^T\Sigma^{-1} r\), not the plain squared length.",
    )
    b.order(
        2,
        "Put these steps in the order that shows why equal-variance Gaussian noise recovers least squares.",
        [
            "Subtract the model mean from each observation and stack those differences into the residual.",
            "Write the log likelihood, including the squared length of that residual divided by twice the variance.",
            "Discard every term that does not depend on the coefficient vector.",
            "Minimize the squared length that remains.",
        ],
        r"The log likelihood is written in the residual, so the residual comes first. Discarding terms requires the expression those terms sit in. The squared length that remains is what the last step minimizes, so the discard comes before the minimization. Minimizing the squared length before writing the log likelihood skips the sign that says the likelihood wants the residual small.",
    )
    b.num(
        2,
        r"The sum of squares is 18 and the variance is 3. The residual term in the log likelihood is \(-\) (sum of squares) \(/\) \((2\sigma^2)\). What is that term?",
        -3, "(unitless)",
        r"The term is \(-18/(2\cdot 3) = -18/6 = -3\). The positive value 3 is the variance, not the log-likelihood term. Dropping the 2 in the denominator gives \(-18/3 = -6\). The sum of squares 18 is the numerator before the division.",
    )
    b.num(
        2,
        r"Five independent residuals have sum of squares 20. What is the maximum-likelihood estimate of the common variance?",
        4, "(unitless)",
        r"Divide 20 by 5 to get 4. Dividing by \(5-1 = 4\) gives 5, which is not the Gaussian maximizer. Half of 20 is 10, from the \(1/2\) in the log likelihood, and that half is not the variance estimate. The square root of 20 is the square root of the sum of squares, not a variance.",
    )
    b.sym(
        3,
        r"Let \(r > 0\) be the sum of squares of the residuals and let \(v > 0\) be the common variance. Write the term in the Gaussian log likelihood that contains \(r\), as an expression in r and v.",
        "-r/(2*v)",
        {"r": (0.5, 8), "v": (0.2, 3)},
        r"Each independent Gaussian contributes \(-\) (residual)\(^2/(2v)\). The sum of those numerators is \(r\)."
        "\n"
        r"• \(r/(2v)\) drops the minus sign, so it increases when the fit gets worse."
        "\n"
        r"• \(-r/v\) forgets the 2 in the Gaussian normalization of the square."
        "\n"
        r"• \(-v/(2r)\) swaps the variance and the sum of squares.",
        ["-(r)/(2*v)", "-0.5*r/v", "(-r)/(2*v)"],
    )
    b.multi(
        3,
        r"Select every property the noise must have for ordinary least squares to be the maximum-likelihood estimate of the coefficient vector.",
        [
            r"Gaussian",
            r"independent across observations",
            r"of equal variance",
            r"equipped with a non-flat Gaussian prior on the coefficients",
        ],
        [0, 1, 2],
        r"The derivation uses the Gaussian log density, a diagonal covariance so the joint density is a product, and equal diagonal entries so the product is a single squared length. A non-flat Gaussian prior multiplies the likelihood by an extra factor and produces a ridge penalty. That maximizer is a posterior mode, not the likelihood maximizer.",
    )
    b.mc(
        3,
        r"The maximizer over \(x\) does not depend on the common variance \(\sigma^2\). The maximizer over \(\sigma^2\), once \(x\) is chosen, equals",
        [
            r"the sum of squares divided by the number of observations",
            r"the sum of squares divided by the number of coefficients",
            r"the sum of squares itself",
            r"half the sum of squares, for every sample size",
        ],
        0,
        r"Differentiate the log likelihood in \(v = \sigma^2\). The derivative of \(-\tfrac{m}{2}\log v - r/(2v)\) vanishes at \(v = r/m\). Dividing by the number of coefficients is a different correction. The sum of squares still has the units of a variance times a count. Half the sum of squares matches \(r/m\) only when \(m = 2\).",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails.",
        [
            r"Independent equal-variance Gaussian residuals have covariance sigma squared times I.",
            r"The log likelihood contains the term minus the squared residual length, divided by twice the variance.",
            r"The coefficient vector that maximizes the likelihood therefore maximizes the squared residual length.",
            r"That maximizer of the likelihood is the ordinary least-squares fit.",
        ],
        2,
        r"The covariance and the negative residual term are the Gaussian log density. The least-squares fit maximizes the likelihood because the residual term is negative. The false step turns that minus sign into a maximization of the squared length. The last step names the maximizer of the likelihood, which is least squares, and it does not inherit the reversed inequality.",
        reasons=[
            "The residual term is negative, so the likelihood rises when the squared residual falls. The maximizer minimizes the squared residual.",
            "Equal variance makes the maximizer a weighted fit with unequal weights.",
            "The covariance is sigma times I rather than sigma squared times I, so the first step is the false one.",
        ],
        correct_reason=0,
        preview=["maximum-a-posteriori-estimation"],
    )
    b.num(
        4,
        r"Four observations leave a least-squares residual whose sum of squares is 10. A later prior would change the fitted coefficients. The variance estimate from the likelihood, using this residual, divides the sum of squares by the number of observations. What is that estimate?",
        2.5, "(unitless)",
        r"The Gaussian maximizer for the variance is \(10/4 = 2.5\). Dividing by \(4-1 = 3\) gives \(10/3\), a different correction. The sum of squares 10 still counts four observations. Half of 10 is the numerator of the residual term when the variance is 1, and it is not the variance estimate.",
        preview=["maximum-a-posteriori-estimation"],
    )
    b.mc(
        4,
        r"Adding a zero-mean Gaussian prior on the coefficients multiplies the likelihood by a factor that depends on \(x\). The maximizer of the product is",
        [
            r"still ordinary least squares, because a prior is constant",
            r"a ridge fit, because the log prior is a squared penalty",
            r"a fit that maximizes the squared residual",
            r"the mean of the prior, regardless of the observations",
        ],
        1,
        r"A spherical Gaussian prior has log density equal to a negative squared length of \(x\), up to scaling. Adding that penalty to the least-squares objective is ridge. The prior depends on \(x\), so it is not a constant. It does not reverse the residual term. It pulls toward its mean but does not ignore the observations unless the prior precision goes to infinity.",
        preview=["maximum-a-posteriori-estimation"],
    )
    b.save()


def expl_qr():
    fig = plane_vectors([(3, 4, "a1"), (1, 2, "a2")], "columns used in the factorization", "x1", "x2")
    alt = "Two arrows from the origin, labeled a1 and a2, for the columns (3, 4) and (1, 2)."
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": alt,
         "body_md": r"""Gram-Schmidt already turns an independent list into orthonormal vectors. Thin QR is that process written as a factorization. The columns of \(Q\) are the orthonormal vectors, in the order the columns of \(A\) were accepted. The upper-triangular factor \(R\) stores the inner-product coefficients and the positive lengths that Gram-Schmidt computed. Their product rebuilds the original matrix: \(A = QR\).

The shape is the thin one. If \(A\) is \(m\) by \(n\) with \(m \ge n\) and independent columns, then \(Q\) is \(m\) by \(n\) and \(R\) is \(n\) by \(n\). Orthonormal columns mean \(Q^T Q = I\). They do not mean \(Q Q^T = I\) unless the columns already span every row direction. The positive-length choice puts a positive number on each diagonal entry of \(R\). A negative sign on a diagonal entry can be moved into the matching column of \(Q\), and the product \(QR\) does not change, so the positive convention is a choice rather than a second factorization.

The same arithmetic solves a least-squares problem without forming \(A^T A\). Substitute \(A = QR\) into the normal equations, use \(Q^T Q = I\), and cancel the invertible triangular factor \(R^T\). The minimizer is the solution of the triangular system \(R x = Q^T b\)."""},
        {"heading": "Key equations",
         "body_md": r"""For full column rank,
\[
A = QR, \qquad Q^T Q = I, \qquad R \text{ upper triangular with positive diagonal}.
\]
The first column gives \(R_{11} = \lVert a_1\rVert\) and \(q_1 = a_1/R_{11}\). The next column gives \(R_{12} = q_1^T a_2\) and \(R_{22} = \lVert a_2 - R_{12} q_1\rVert\). The least-squares backsolve is
\[
R x = Q^T b.
\]
That system is equivalent to \(A^T A x = A^T b\). The Gram matrix equals \(R^T R\), so its condition is the square of the condition of \(R\). Forming \(A^T A\) explicitly squares the condition number before the solve. The triangular route keeps the factor \(R\) that Gram-Schmidt already built."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(A = \begin{bmatrix} 3 & 1 \\ 4 & 2 \end{bmatrix}\). The first column has length \(\sqrt{9+16} = 5\), so
\[
q_1 = (3/5,\ 4/5), \qquad R_{11} = 5.
\]
The inner product of \(q_1\) with the second column is \(3/5+8/5 = 11/5\). The remainder is
\[
(1,2) - (11/5)(3/5,\ 4/5) = (-8/25,\ 6/25).
\]
Its length is \(2/5\). Therefore
\[
R = \begin{bmatrix} 5 & 11/5 \\ 0 & 2/5 \end{bmatrix}, \qquad q_2 = (-4/5,\ 3/5).
\]
Both diagonal entries are positive, \(q_1^T q_2 = 0\), and each column of \(Q\) has length 1. Multiplying \(QR\) returns the two columns of \(A\). The length 5 is the first diagonal entry, not the inner product \(11/5\). The second diagonal entry is the length of the remainder, not the second column's original length."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The identity \(Q^T Q = I\) is the one orthonormal columns give. The product \(Q Q^T\) projects onto the column space, and it equals the identity only in the square case. A tall thin factor fails that second identity.

The diagonal of \(R\) holds lengths, so a zero on the diagonal means a column was dependent and the thin factorization with invertible \(R\) has stopped. Skipping the positive-length convention produces a valid product \(QR\) with some negative diagonal entries. Later formulas that take square roots of those entries then need the absolute value.

Least squares does not ask \(Q x = b\). The factor \(Q\) maps coefficients to the column space, and \(b\) need not lie in that space. The right-hand side of the backsolve is \(Q^T b\), a vector with one entry per column."""},
        {"heading": "Where this leads",
         "body_md": r"""The triangular system \(R x = Q^T b\) is the least-squares minimizer the normal equations already describe. Using \(R\) instead of \(A^T A\) reaches that same point without squaring the condition number. The part of \(b\) orthogonal to the columns of \(Q\) is invisible to the backsolve, which is the left-nullspace picture of the residual."""},
    ]
    save_explainer("qr-factorization", "QR factorization", sections)


def expl_subspaces():
    fig = matrix_fig([["1", "2", "3"], ["2", "4", "6"]], "a rank-one matrix")
    alt = "A 2 by 3 matrix whose second row is twice the first."
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": alt,
         "body_md": r"""The linear-algebra review counts the rank and describes the nullspace: the vectors \(x\) with \(Ax = 0\). Rank plus the nullspace dimension equals the number of columns. Inner products add the test for a right angle. The four fundamental subspaces put those two ideas on both \(A\) and \(A^T\).

The column space is every vector \(Ax\). It sits in the codomain, which has one coordinate per row. The row space is the column space of \(A^T\). It sits in the domain, which has one coordinate per column. The left nullspace is the nullspace of \(A^T\): the vectors \(y\) with \(A^T y = 0\).

The orthogonality relations pair subspaces that live in the same Euclidean space. In the domain, the nullspace is orthogonal to the row space, and together they span the domain. In the codomain, the left nullspace is orthogonal to the column space, and together they span the codomain. A vector in the column space is not, in general, orthogonal to a vector in the row space, because those two vectors need not even have the same length."""},
        {"heading": "Key equations",
         "body_md": r"""Let \(A\) be \(m\) by \(n\) with rank \(r\). The dimensions are
\[
\dim C(A) = r, \quad \dim C(A^T) = r, \quad \dim N(A) = n-r, \quad \dim N(A^T) = m-r.
\]
Orthogonality is \(N(A) = C(A^T)^\perp\) and \(N(A^T) = C(A)^\perp\). A least-squares residual \(b-Ax\) is orthogonal to every column, so it lies in the left nullspace. The normal equations put a minimizer in the row space. Adding a nullspace vector does not change \(Ax\), which is why a rank-deficient problem has many minimizers and the row-space choice is the one of smallest length."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A = \begin{bmatrix} 1 & 2 & 3 \\ 2 & 4 & 6 \end{bmatrix}\). The second row is twice the first, so the rank is 1. There are 3 columns and 2 rows, so the nullspace has dimension \(3-1 = 2\) and the left nullspace has dimension \(2-1 = 1\).

The column space is the span of \((1,2)\). A left-null vector \(y\) satisfies \(y_1+2 y_2 = 0\), so one basis vector is \((2,-1)\). Its inner product with \((1,2)\) is \(2-2 = 0\), which is the orthogonality of the left nullspace and the column space. The row space is the span of \((1,2,3)\). Any nullspace vector is orthogonal to \((1,2,3)\). One such vector is \((-2,1,0)\), and \((-2)(1)+(1)(2)+(0)(3) = 0\).

The dimension count uses rows minus rank for the left nullspace. Using columns minus rank there would report 2, and that is the nullspace dimension instead."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The left nullspace is not the nullspace. One annihilates rows and the other annihilates columns. They live in different spaces whenever \(m \ne n\).

The row space is not automatically orthogonal to the column space. The partners are row space with nullspace, and column space with left nullspace.

The rank equals both the column-space dimension and the row-space dimension. A zero row lowers the rank. It does not by itself name a left-null basis; that basis still has to satisfy \(A^T y = 0\)."""},
        {"heading": "Where this leads",
         "body_md": r"""Least squares uses the split directly. The fitted vector \(Ax\) is the projection of \(b\) onto the column space, the residual lies in the left nullspace, and a minimizer can be taken in the row space. Right singular vectors later span the row space and the nullspace. Left singular vectors span the column space and the left nullspace."""},
    ]
    save_explainer("fundamental-subspaces", "Four fundamental subspaces", sections)


def expl_blocks():
    fig = matrix_fig([["4", "2"], ["6", "11"]], "scalar blocks")
    alt = "A 2 by 2 array with entries 4, 2, 6, and 11."
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": alt,
         "body_md": r"""Matrix multiplication and inversion, from the linear-algebra review, extend to matrices that have been partitioned into blocks. If the blocks fit, the product uses the same row-column rule one level up. The upper-left block of a product is a sum of products of blocks, not a single product and not an entrywise product.

Inversion also reduces to smaller inverses when one diagonal block is invertible. The useful reduction is the Schur complement. In \(\begin{bmatrix} A & B \\ C & D \end{bmatrix}\) with \(A\) invertible, eliminate \(A\) and what remains of the lower-right block is
\[
S = D - C A^{-1} B.
\]
The whole block matrix is invertible exactly when \(S\) is invertible. The lower-right block of the inverse is \(S^{-1}\), and the determinant factors as \(\det(A)\det(S)\).

The same complement tests positive definiteness. For a symmetric block matrix with \(A\) positive definite, the big matrix is positive definite exactly when \(S = D - B^T A^{-1} B\) is positive definite. That is the form a semidefinite constraint uses when it wants a block matrix of this shape to be a positive-semidefinite variable."""},
        {"heading": "Key equations",
         "body_md": r"""The block product is
\[
\begin{bmatrix} A & B \\ C & D \end{bmatrix}
\begin{bmatrix} E & F \\ G & H \end{bmatrix}
=
\begin{bmatrix} AE+BG & AF+BH \\ CE+DG & CF+DH \end{bmatrix}.
\]
With \(A\) and \(S = D-CA^{-1}B\) invertible,
\[
\begin{bmatrix} A & B \\ C & D \end{bmatrix}^{-1}
=
\begin{bmatrix}
A^{-1}+A^{-1} B S^{-1} C A^{-1} & -A^{-1} B S^{-1} \\
-S^{-1} C A^{-1} & S^{-1}
\end{bmatrix}.
\]
The determinant identity is \(\det\begin{bmatrix} A & B \\ C & D \end{bmatrix} = \det(A)\det(S)\). Nothing here requires the blocks to be scalars. The inverses that appear are inverses of \(A\) and of \(S\)."""},
        {"heading": "Worked example",
         "body_md": r"""Take the scalar blocks \(A = 4\), \(B = 2\), \(C = 6\), and \(D = 11\). Then
\[
S = 11 - 6\cdot(1/4)\cdot 2 = 11 - 3 = 8.
\]
The lower-right entry of the inverse is \(1/8\). The determinant of the 2 by 2 matrix is \(4\cdot 8 = 32\). Direct expansion gives \(4\cdot 11 - 2\cdot 6 = 44-12 = 32\), the same number.

The product \(6\cdot 2 = 12\) is not yet the correction, because \(A\) has not been inverted. Dividing by 4 produces the 3 that is subtracted from 11. Forgetting the subtraction and reporting 11 leaves the original lower-right block in place. The complement is 8, not 11 and not 3."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Block multiplication is not entrywise, and it is not commutative. \(AE+BG\) uses \(B\) with \(G\) and \(A\) with \(E\). Swapping those pairs is a different product.

The Schur complement of \(A\) subtracts from \(D\). The complement of \(D\), when \(D\) is the invertible block instead, subtracts from \(A\) and uses \(D^{-1}\). Naming the wrong block inverts the wrong factor.

A singular \(A\) does not by itself make the whole matrix singular. The test above assumes \(A\) is invertible so that \(S\) is defined. If \(A\) is singular, swap the roles or use a different block factorization. Positive definiteness needs the complement to be positive definite, not merely nonzero. A negative complement of a positive definite \(A\) makes the big matrix indefinite."""},
        {"heading": "Where this leads",
         "body_md": r"""Semidefinite programs constrain a symmetric matrix, often built from blocks, to be positive semidefinite. The Schur complement turns one such constraint into a smaller one when a diagonal block is positive definite. The same identity simplifies the inverse of a block Hessian in a Newton step and the covariance of a conditional Gaussian. In each case the arithmetic is the elimination step already written here: invert one block, correct the other, and read the inverse or the definiteness test from the complement."""},
    ]
    save_explainer("block-matrix-identities", "Block matrix identities", sections)


def expl_pca():
    sections = [
        {"heading": "The idea", "figure": ELLT, "figure_alt": AELLT,
         "body_md": r"""Spectral decomposition writes a real symmetric matrix as \(U D U^T\) with orthonormal eigenvectors. Singular value decomposition writes a rectangular matrix as \(U\Sigma V^T\). Principal component analysis applies those two factorizations to a cloud of data.

Put one sample in each row and one feature in each column. Subtract the mean of each column. Call the centered matrix \(Z\). The covariance used here is the average of the outer products of the rows,
\[
C = \tfrac{1}{n} Z^T Z.
\]
This \(C\) is symmetric and positive semidefinite. Its eigenvectors are orthogonal, and its eigenvalues are variances along those directions. The leading principal direction is the eigenvector for the largest eigenvalue. Equivalently, it is the leading right singular vector of \(Z\). The right singular vectors live in feature space. The left singular vectors live in sample space and are not the principal directions of the features.

Centering matters. The average outer product of the raw rows includes the mean. Its leading eigenvector is pulled toward that mean. After centering, the eigenvector measures spread about the mean."""},
        {"heading": "Key equations",
         "body_md": r"""If \(Z = U\Sigma V^T\) is a singular value decomposition, then
\[
Z^T Z = V\Sigma^T\Sigma V^T,
\]
so the columns of \(V\) are eigenvectors of the covariance, up to the positive factor \(1/n\) that scales every eigenvalue and does not change the eigenvectors. The variance along a unit vector \(u\) is \(u^T C u\). Along a unit eigenvector it equals the matching eigenvalue. The score of a centered row \(z\) on a unit principal direction \(v\) is the inner product \(z^T v\). Those scores are the coordinates a later regression will treat as a new design."""},
        {"heading": "Worked example",
         "body_md": r"""The rows are \((1,0)\), \((3,0)\), and \((2,3)\). Their mean is \((2,1)\). The centered rows are \((-1,-1)\), \((1,-1)\), and \((0,2)\). The outer products sum to \(\mathrm{diag}(2,6)\), and dividing by 3 gives
\[
C = \mathrm{diag}(2/3,\ 2).
\]
The larger eigenvalue is 2, on the second coordinate. The leading principal direction is \((0,1)\), and the variance along it is 2. The variance along \((1,0)\) is \(2/3\), which is real spread but not the leading one.

The uncentered average outer product is not this \(C\). It mixes in the mean \((2,1)\). Using it would answer a question about distance from the origin, not about spread. The score of the centered row \((0,2)\) on \((0,1)\) is 2."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The leading direction belongs to the largest eigenvalue. The smallest eigenvalue is the thinnest direction.

Right singular vectors are the feature directions. Left singular vectors have one entry per sample. Swapping them writes a vector in the wrong space.

Dividing by \(n-1\) instead of \(n\) scales every eigenvalue and does not change the directions. This skill divides by the number of rows. The principal direction is defined up to sign. Scores flip sign with the vector, so a later inner product has to use the same choice."""},
        {"heading": "Where this leads",
         "body_md": r"""Low-rank approximation keeps the largest singular pieces and zeros the rest. For centered data those pieces are the leading principal components. Principal components regression fits least squares in the scores on the first few of them."""},
    ]
    save_explainer("principal-component-analysis", "Principal component analysis", sections)


def expl_lowrank():
    fig = matrix_fig([["8", "0", "0"], ["0", "5", "0"], ["0", "0", "1"]], "three singular values")
    alt = "A diagonal matrix whose diagonal entries are 8, 5, and 1."
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": alt,
         "body_md": r"""Singular value decomposition already factors a matrix as a sum of rank-one pieces. If \(A = U\Sigma V^T\), and the diagonal of \(\Sigma\) holds \(\sigma_1 \ge \sigma_2 \ge \cdots \ge 0\), then
\[
A = \sum_i \sigma_i\, u_i v_i^T.
\]
Low-rank approximation keeps the first \(r\) terms and sets the later singular values to zero. Call the result \(A_r\). It has rank at most \(r\). Among all matrices of rank at most \(r\), it is a nearest matrix to \(A\) in the Frobenius norm, and also a nearest matrix in the spectral norm.

The errors have short formulas. The spectral norm of \(A-A_r\) equals the first discarded singular value \(\sigma_{r+1}\). The Frobenius norm equals the square root of the sum of the squares of the discarded singular values. Those two numbers agree when only one singular value is discarded. They disagree as soon as two or more positive singular values are dropped, because the Frobenius norm then adds more than one square.

This is a statement about the truncation, not a new factorization. The singular vectors stay the ones the decomposition already produced."""},
        {"heading": "Key equations",
         "body_md": r"""With \(\sigma_1 \ge \cdots \ge \sigma_n \ge 0\),
\[
\lVert A-A_r\rVert_2 = \sigma_{r+1}, \qquad
\lVert A-A_r\rVert_F = \sqrt{\sum_{i>r} \sigma_i^2}.
\]
The squared Frobenius energy \(\sum_i \sigma_i^2\) splits into the kept part and the discarded part. The fraction kept by the rank-\(r\) truncation is the kept sum of squares divided by the total sum of squares. The zero matrix is the rank-0 truncation, and its Frobenius distance to \(A\) is \(\lVert A\rVert_F\). The spectral norm of \(A\) itself is \(\sigma_1\), which is the error of the rank-0 truncation in that norm."""},
        {"heading": "Worked example",
         "body_md": r"""Suppose the singular values are 8, 5, and 1. The rank-1 truncation keeps 8 and discards 5 and 1. The spectral error is 5. The Frobenius error is
\[
\sqrt{25+1} = \sqrt{26}.
\]
The rank-2 truncation discards only 1, so both the spectral error and the Frobenius error equal 1. The squared energy is \(64+25+1 = 90\). The rank-1 truncation keeps \(64/90\) of it.

Reporting \(\sqrt{26}\) as the spectral error assigns the Frobenius formula to the wrong norm. Reporting 8 as the rank-1 error reports the piece that was kept. The nearest rank-1 matrix is the first outer product scaled by 8, not the original matrix with small entries manually rounded off."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The spectral error is the next singular value, not the square root of a sum of squares. The Frobenius norm adds the squares of the discarded values and then takes a square root. Adding the discarded values without squares is a different norm.

Dropping the largest singular values is the opposite truncation. It is far from \(A\) in both norms. This skill claims the Frobenius norm and the spectral norm only. A sign flip on both singular vectors of one term cancels in the outer product, so it does not change the truncation."""},
        {"heading": "Where this leads",
         "body_md": r"""For centered data, the leading right singular vectors are the principal components. Keeping \(r\) of them is the rank-\(r\) truncation. Principal components regression uses those coordinates as a design and runs least squares. The fraction of squared Frobenius energy that is kept is how much of the predictor cloud that regression still sees."""},
    ]
    save_explainer("low-rank-approximation", "Low-rank approximation", sections)


def expl_perturb():
    fig = matrix_fig([["9", "0"], ["0", "3"]], "two singular values")
    alt = "A diagonal matrix whose diagonal entries are 9 and 3."
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": alt,
         "body_md": r"""Linear least squares finds \(x\) by the normal equations when the columns are independent. The singular value decomposition supplies the two numbers that say how stable that \(x\) is. The induced 2-norm of \(A\) is \(\sigma_{\max}\). The induced 2-norm of the pseudoinverse is \(1/\sigma_{\min}\). Their product is the least-squares condition number
\[
\kappa = \sigma_{\max}/\sigma_{\min}.
\]
It is not the exact-line-search factor \(((κ-1)/(κ+1))^2\). That factor bounds a gradient iteration on a quadratic. The ratio of singular values bounds how a change in the least-squares data moves the solution.

When the residual is zero and \(b\) changes by \(\delta b\), with \(A\) fixed,
\[
\frac{\lVert\delta x\rVert}{\lVert x\rVert} \le \kappa\, \frac{\lVert\delta b\rVert}{\lVert b\rVert}.
\]
The same single factor \(\kappa\) bounds a small relative change in \(A\) when the residual is zero. A nonzero residual is less forgiving. Differentiating the normal equations produces a term \((A^T A)^{-1}(\delta A)^T r\). The smallest eigenvalue of \(A^T A\) is \(\sigma_{\min}^2\), so that term can be as large as a constant times \(\lVert\delta A\rVert\,\lVert r\rVert/\sigma_{\min}^2\). Relative to \(\lVert A\rVert^2\), this is a factor \(\kappa^2\).

The condition number of the normal matrix \(A^T A\) is exactly \(\kappa^2\). Forming \(A^T A\) before solving squares the condition number that \(A\) already had."""},
        {"heading": "Key equations",
         "body_md": r"""For full column rank,
\[
\lVert A\rVert_2 = \sigma_{\max}, \qquad \lVert A^+\rVert_2 = 1/\sigma_{\min}, \qquad \kappa(A) = \sigma_{\max}/\sigma_{\min}.
\]
A change in \(b\) alone moves the solution by \(\delta x = A^+ \delta b\), so \(\lVert\delta x\rVert \le \lVert\delta b\rVert/\sigma_{\min}\). The eigenvalues of \(A^T A\) are \(\sigma_i^2\), and
\[
\kappa(A^T A) = \kappa(A)^2.
\]
Ridge regression adds \(\lambda I\) to \(A^T A\). Each eigenvalue grows by \(\lambda\), and the smallest one moves from \(\sigma_{\min}^2\) to \(\sigma_{\min}^2+\lambda\). That is why a penalty can calm a large condition number. The penalty does not change the definition of \(\kappa(A)\) itself."""},
        {"heading": "Worked example",
         "body_md": r"""Suppose the singular values are 9 and 3. Then \(\kappa = 9/3 = 3\), and the condition number of \(A^T A\) is \(9\). The pseudoinverse norm is \(1/3\).

Take a zero residual, \(\lVert b\rVert = 9\), and a perturbation with \(\lVert\delta b\rVert = 0.3\). The relative change in \(b\) is \(0.3/9 = 1/30\). The bound on the relative change in \(x\) is
\[
3\cdot(1/30) = 1/10.
\]
The absolute bound from the pseudoinverse alone is \((1/3)(0.3) = 0.1\). These are upper bounds, not a prediction that the change will be exactly \(0.1\). Using the difference \(9-3 = 6\) in place of the ratio 3 applies the wrong combination of the two singular values. Using \(((3-1)/(3+1))^2 = 1/4\) imports the line-search factor, which is not \(\kappa\)."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The condition number of \(A\) and the condition number of \(A^T A\) differ by a square. Copying a bound from one onto the other is off by a factor \(\kappa\).

A zero residual is a hypothesis in the single-factor bounds. If \(b\) is far from the column space, a change in \(A\) can pick up the \(\kappa^2\) term.

The induced 2-norm is \(\sigma_{\max}\), not the difference of the extreme singular values and not the Frobenius norm. The condition ratio uses only the largest and the smallest."""},
        {"heading": "Where this leads",
         "body_md": r"""Ridge regression is the standard repair when \(\kappa(A^T A)\) is large. Adding \(\lambda I\) lifts \(\sigma_{\min}^2\). The triangular factor from a QR factorization is another way to solve the unperturbed problem without squaring \(\kappa\), but it does not by itself shrink a large condition number. The condition number remains a property of \(A\). Principal-component regression drops the small singular directions outright, which is a harder version of the same idea: remove the \(\sigma_{\min}\) that made \(\kappa\) large, then fit in the directions that remain."""},
    ]
    save_explainer("least-squares-perturbation", "Perturbation of least squares", sections)


def expl_ridge():
    sections = [
        {"heading": "The idea", "figure": ELL, "figure_alt": AELL,
         "body_md": r"""Least squares as a quadratic sets the gradient of \(\lVert Ax-b\rVert^2\) to zero and obtains the normal equations \(A^T A x = A^T b\). That Gram matrix is positive definite exactly when the columns are independent. Ridge keeps the same residual and adds a squared penalty on the coefficients,
\[
\lVert Ax-b\rVert^2 + \lambda\lVert x\rVert^2, \qquad \lambda > 0.
\]
The gradient of the penalty is \(2\lambda x\). Stationarity becomes
\[
(A^T A+\lambda I)x = A^T b.
\]
The new matrix is positive definite for every \(\lambda > 0\), even when the columns of \(A\) are dependent. Every eigenvalue of \(A^T A\) grows by \(\lambda\), so the smallest one is at least \(\lambda\).

A more general penalty charges a linear image of \(x\). The objective \(\lVert Ax-b\rVert^2+\lVert\Gamma x\rVert^2\) has stationarity equation \((A^T A+\Gamma^T\Gamma)x = A^T b\). Ridge is the special case \(\Gamma = \sqrt{\lambda}\, I\). The matrix \(\Gamma^T\Gamma\) is an arbitrary symmetric positive semidefinite shift of this Gram form. It is not an absolute penalty. The absolute penalty \(\lambda\lVert x\rVert_1\) is a different objective, with a different stationarity condition.

The penalty pulls the solution toward the origin. A nonzero ordinary least-squares solution moves closer to zero when \(\lambda\) increases. If the ordinary solution is already zero, the ridge solution stays there."""},
        {"heading": "Key equations",
         "body_md": r"""\[
(A^T A+\lambda I)x = A^T b, \qquad
(A^T A+\Gamma^T\Gamma)x = A^T b.
\]
If \(A\) has singular values \(\sigma_i\), the eigenvalues of the ridge matrix are \(\sigma_i^2+\lambda\). The condition number of that matrix is \((\sigma_{\max}^2+\lambda)/(\sigma_{\min}^2+\lambda)\), which is smaller than \(\sigma_{\max}^2/\sigma_{\min}^2\) whenever \(\lambda > 0\) and \(\sigma_{\max} > \sigma_{\min}\). For a single coefficient and a column \(a\), the solution is the scalar
\[
x = \frac{a^T b}{\lVert a\rVert^2+\lambda}.
\]
Ordinary least squares is the same formula with \(\lambda = 0\), and it requires \(\lVert a\rVert \ne 0\)."""},
        {"heading": "Worked example",
         "body_md": r"""Let
\[
A = \begin{bmatrix} 2 & 0 \\ 2 & 0 \\ 0 & 3 \end{bmatrix}, \qquad
b = \begin{bmatrix} 2 \\ 2 \\ 3 \end{bmatrix}, \qquad \lambda = 2.
\]
Then \(A^T A = \mathrm{diag}(8,9)\) and \(A^T b = (8,9)\). The ridge matrix is \(\mathrm{diag}(10,11)\), so
\[
x = (8/10,\ 9/11) = (0.8,\ 9/11).
\]
Ordinary least squares would have divided by 8 and by 9, giving \((1,1)\). Both coordinates moved toward zero. The second coordinate did move, even though the second column of \(A\) was already a multiple of a standard basis vector. The penalty does not skip a column that happens to be orthogonal to the other columns. It shifts every diagonal entry."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The shift belongs on \(A^T A\), not on \(A\). Adding \(\lambda I\) to a rectangular \(A\) is not even the same shape. Adding it before the product \(A^T A\) produces \((A+\lambda I)^T(A+\lambda I)\), which expands into cross terms the ridge objective does not have.

The general penalty contributes \(\Gamma^T\Gamma\), not \(\Gamma\). A rectangular \(\Gamma\) cannot be added to the square Gram matrix. The product \(\Gamma^T\Gamma\) is square and symmetric.

Ridge is not the damping term on a Gauss-Newton step. That damping shifts a Jacobian Gram matrix inside an iterative method for a nonlinear residual. The objective here is an ordinary linear residual plus a penalty on the coefficients, solved in one linear system. Using the line-search condition factor in place of \(\lambda\) mixes two unrelated parameters."""},
        {"heading": "Where this leads",
         "body_md": r"""A zero-mean Gaussian prior on the coefficients has a negative log density equal to a squared penalty. Maximizing likelihood times that prior is ridge. That posterior step is maximum a posteriori estimation. Replacing the squared penalty by an absolute penalty gives the lasso, which can set coefficients exactly to zero. Principal components regression is a different repair for a large condition number: it deletes trailing directions instead of shrinking every coefficient. The general \(\Gamma\) lets the penalty charge some linear combinations and leave others alone, which is the bridge from plain ridge to a structured prior."""},
    ]
    save_explainer("ridge-regression", "Ridge regression", sections)


def expl_pcr():
    sections = [
        {"heading": "The idea", "figure": ELL, "figure_alt": AELL,
         "body_md": r"""Principal component analysis produces orthonormal directions of greatest spread. Low-rank approximation keeps the leading singular pieces. Data fitting solves least squares in its coefficients. Principal components regression stacks those three facts.

Center the predictor columns and take the first \(r\) principal directions. Replace each centered row by its scores on those directions. Center the response, and solve ordinary least squares in the score coordinates. A prediction in the original scale adds the mean of the response back.

A score column built from a unit right singular vector has length equal to the matching singular value, so the Gram entry is the square of that singular value. Orthogonal scores make each coefficient an inner product divided by that squared length. The trailing directions are left out. The kept coefficients are unpenalized."""},
        {"heading": "Key equations",
         "body_md": r"""Let \(Z\) be the centered predictor matrix, \(V_r\) the leading right singular vectors, and \(y_c\) the centered response. The reduced design and the coefficient solve are
\[
W = Z V_r, \qquad W^T W\,\theta = W^T y_c.
\]
When column \(j\) of \(W\) comes from a unit singular vector with singular value \(s_j\),
\[
\lVert w_j\rVert^2 = s_j^2, \qquad \theta_j = \frac{w_j^T y_c}{s_j^2}.
\]
A new centered row \(z\) predicts \(z^T V_r\,\theta\) in centered response units. Adding the mean of the response returns to the original scale. Dropping a component sets its coefficient to zero by leaving its column out of \(W\)."""},
        {"heading": "Worked example",
         "body_md": r"""Suppose the centered scores on one kept component are \(1\), \(-1\), and \(0\), and the centered response is \(1\), \(-1\), and \(0\). The inner product is \(2\) and the squared length is \(2\), so the coefficient is \(1\).

The centered prediction at a score of \(1\) is \(1\). Add the mean of the response after that product to return to the original scale. The squared length is 2, so the singular value would be \(\sqrt{2}\) if these scores came from a unit right singular vector. Dividing the inner product by \(\sqrt{2}\) instead of by 2 uses the length where the normal equation wants the squared length."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Keeping the smallest principal components reverses the truncation. Those directions are the ones a low-rank approximation discards.

The Gram entry is \(s^2\), not \(s\). Dividing by \(s\) is off by a factor \(s\).

The coefficients fit the centered response. Add the mean of the response back before reporting a prediction in the original units. This regression does not shrink the kept coefficients. A squared penalty would. Mixing \(\lambda I\) into \(W^T W\) is ridge in the score coordinates, a different problem."""},
        {"heading": "Where this leads",
         "body_md": r"""An absolute penalty, the lasso, can set individual coefficients to zero without first discarding an entire principal direction. Ridge shrinks every direction and deletes none. Principal components regression is the hard version: a direction is in the design or it is absent, and the kept coefficients are ordinary least squares. Maximum likelihood with equal-variance Gaussian noise is exactly that ordinary least squares problem on whatever design you hand it. The design here happens to be a score matrix. The likelihood statement does not change."""},
    ]
    save_explainer("principal-components-regression", "Principal components regression", sections)


def expl_mle():
    fig = ellipse_axes("equal-variance level set", rx=64, ry=64)
    alt = "A circle centered at the origin, the level set of an equal-variance residual penalty."
    sections = [
        {"heading": "The idea", "figure": fig, "figure_alt": alt,
         "body_md": r"""Data fitting already minimizes the squared length of a residual \(b-Ax\). A Gaussian random vector is determined by a mean and a covariance. Put those together. If the observations are Gaussian with mean \(Ax\) and covariance \(\sigma^2 I\), the density of the sample is a product of one-dimensional Gaussians, all with the same variance.

The log of that density is
\[
-\frac{m}{2}\log(2\pi) - \frac{m}{2}\log(\sigma^2) - \frac{1}{2\sigma^2}\lVert b-Ax\rVert^2.
\]
Only the last term depends on \(x\). The factor \(1/(2\sigma^2)\) is positive, so the log density is largest when the squared residual is smallest. The maximizer in \(x\) is the ordinary least-squares fit, for every \(\sigma > 0\).

The maximizer in \(\sigma^2\), after \(x\) is chosen, is the sum of squares divided by the number of observations \(m\). Dividing by \(m-1\) is a different correction. It is not the maximizer of this likelihood.

Unequal variances change the story. The log density becomes a weighted sum of squares, and the maximizer is weighted least squares. A prior on \(x\) is not part of the likelihood. Multiplying by a Gaussian prior produces a posterior mode, which is a ridge problem when the prior is spherical. That step comes later."""},
        {"heading": "Key equations",
         "body_md": r"""For independent residuals with variance \(v > 0\) and sum of squares \(r = \lVert b-Ax\rVert^2\),
\[
\ell(x,v) = -\frac{m}{2}\log(2\pi) - \frac{m}{2}\log v - \frac{r}{2v}.
\]
Maximizing in \(x\) is minimizing \(r\). Maximizing in \(v\) gives \(v = r/m\). The residual term \(-r/(2v)\) is the only term that sees the fit. A sign error there turns the maximizer into the worst squared residual. The covariance \(\sigma^2 I\) is a scalar matrix. A nondiagonal covariance replaces \(r\) by \(r^T \Sigma^{-1} r\)."""},
        {"heading": "Worked example",
         "body_md": r"""Five residuals have squares \(1\), \(1\), \(1\), \(1\), and \(21\). The sum of squares is \(25\), and \(m = 5\), so the maximum-likelihood variance is \(25/5 = 5\). The residual term in the log likelihood, at that variance, is
\[
-25/(2\cdot 5) = -2.5.
\]
If the variance is regarded as known and equal to 5, the maximizer over the coefficients still minimizes the sum of squares. Changing the known variance to 10 multiplies the residual term by \(1/2\) and does not move its minimizer. The estimate 5 is \(r/m\). Dividing 25 by \(5-1 = 4\) gives \(6.25\), which answers a different estimation rule. The square root \(\sqrt{5}\) is a standard deviation, not the variance the likelihood maximizes."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The least-squares fit maximizes the likelihood. It does not maximize the squared residual. The minus sign in \(-r/(2v)\) is why the two problems agree.

The variance estimate divides by the number of observations, not by the number of coefficients. Equal variance is required for the unweighted sum of squares. Unequal diagonal variances leave weights \(1/v_i\).

A Gaussian prior on the coefficients is not a statement about the noise. The likelihood maximizer ignores it. The posterior maximizer does not."""},
        {"heading": "Where this leads",
         "body_md": r"""Maximum a posteriori estimation multiplies the likelihood by a prior and maximizes the product. A spherical Gaussian prior adds \(\lambda\lVert x\rVert^2\) and turns the least-squares problem into ridge. An absolute prior turns it into the lasso. The likelihood piece stays the squared residual derived here, as long as the noise stays independent, Gaussian, and equally variable. Principal components regression does not change that likelihood. It only replaces \(A\) by a score matrix before the same minimization."""},
    ]
    save_explainer("maximum-likelihood-estimation", "Maximum likelihood estimation", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    publish_graph()
    bank_qr()
    bank_subspaces()
    bank_blocks()
    bank_pca()
    bank_lowrank()
    bank_perturb()
    bank_ridge()
    bank_pcr()
    bank_mle()
    expl_qr()
    expl_subspaces()
    expl_blocks()
    expl_pca()
    expl_lowrank()
    expl_perturb()
    expl_ridge()
    expl_pcr()
    expl_mle()
    banned = (
        "boyd", "nocedal", "vandenberghe", "hefferon", "wikibook", "textbook",
        "university", "professor", "lecture", "syllabus", "strang", "berkeley",
        "stanford", "trefethen", "golub",
    )
    private = {
        "qr-factorization": "11/5",
        "fundamental-subspaces": "(-2,1,0)",
        "block-matrix-identities": "11 - 3",
        "principal-component-analysis": "larger eigenvalue is 2",
        "low-rank-approximation": "sqrt{26}",
        "least-squares-perturbation": "1/30",
        "ridge-regression": "9/11",
        "principal-components-regression": "would be $\\sqrt{2}$",
        "maximum-likelihood-estimation": "6.25",
    }
    # The PCR marker is written in TeX in the explainer. Check a plain fragment.
    private["principal-components-regression"] = "Dividing the inner product by"
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
            print("  worked example reused in the bank")
            bad = True
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
