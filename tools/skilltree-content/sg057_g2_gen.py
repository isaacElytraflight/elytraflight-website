#!/usr/bin/env python3
"""SG-057 group 2: eigenvalue core, least-squares core, positive-definite core.

Keeps the ids the audit keeps. Retires moved question ids and does not reuse them.
Deep questions are built with Bank.sym, Bank.order, Bank.find_error, and Bank.multi.
Running this again does nothing once the sentinel question is already live.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import BANK, EXP, Bank, save_explainer, words
from templates import ellipse_axes, matrix_fig, plane_vectors, splane, step_response

SENTINEL = "eigenvalues-diagonalization-r1-q1"


def load(sid, kind):
    folder = BANK if kind == "bank" else EXP
    path = os.path.join(folder, sid + ".json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["_path"] = path
    return data


def dump(data):
    path = data.pop("_path")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def retire(bank, qid):
    for i, q in enumerate(bank["questions"]):
        if q.get("id") == qid:
            gone = bank["questions"].pop(i)
            if not isinstance(gone.get("version"), int):
                gone["version"] = 1
            bank.setdefault("retired_questions", []).append(gone)
            return
    raise SystemExit("missing live question " + qid)


def built(sid, rnd, qid, kind, *args, **kwargs):
    slot = Bank(sid)
    getattr(slot, kind)(rnd, *args, **kwargs)
    item = slot.qs[0]
    item["id"] = qid
    item["version"] = 1
    return item


def retarget(bank, qid, preview):
    for q in bank["questions"]:
        if q.get("id") == qid:
            q["preview"] = preview
            q["version"] = int(q.get("version") or 1) + 1
            return
    raise SystemExit("missing preview question " + qid)


def bump(bank):
    bank["version"] = int(bank.get("version") or 1) + 1


def set_section(exp, heading, body):
    for section in exp["sections"]:
        if section.get("heading") == heading:
            section["body_md"] = body
            return
    raise SystemExit("missing section " + heading)


def save_exp(exp):
    exp["version"] = int(exp.get("version") or 1) + 1
    dump(exp)


def patch_lin_algebra():
    bank = load("lin-algebra-review", "bank")
    for qid in (
        "lin-algebra-review-r2-q1",
        "lin-algebra-review-r2-q2",
        "lin-algebra-review-r3-q2",
        "lin-algebra-review-r3-q3",
        "lin-algebra-review-r4-q3",
    ):
        retire(bank, qid)
    mat = matrix_fig([["3", "-2"], ["5", "1"]], "A matrix and a column")
    tall = matrix_fig([["1", "0"], ["2", "1"], ["0", "3"]], "A tall matrix")
    bank["questions"] += [
        built(
            "lin-algebra-review", 2, "lin-algebra-review-r2-q4", "sym",
            r"A 2 by 2 matrix has entries a, b, c, d in reading order. Write its determinant in the names a, b, c, and d.",
            "a*d-b*c",
            {"a": (-3, 3), "b": (-3, 3), "c": (-3, 3), "d": (-3, 3)},
            r"The determinant of \(\begin{bmatrix} a & b \\ c & d \end{bmatrix}\) is \(ad - bc\). The product \(ad\) is the main diagonal. The product \(bc\) is the other diagonal, and it is subtracted. Swapping those two products changes the sign of the determinant.",
            alternates=["a*d-c*b"],
            fig=mat,
            alt="A 2 by 2 matrix with four letter entries.",
        ),
        built(
            "lin-algebra-review", 2, "lin-algebra-review-r2-q5", "num",
            r"Let \(A = \begin{bmatrix} 3 & -2 \\ 5 & 1 \end{bmatrix}\) and \(v = \begin{bmatrix} 2 \\ 1 \end{bmatrix}\). What is the second entry of \(Av\)?",
            11,
            "",
            r"The second entry is the second row dotted with the column: \(5 \cdot 2 + 1 \cdot 1 = 11\). The first entry is \(3 \cdot 2 + (-2) \cdot 1 = 4\), which is a different row. A matrix-vector product mixes the columns; it does not add the entries of the matrix.",
            fig=mat,
            alt="A 2 by 2 matrix beside a column of height 2.",
        ),
        built(
            "lin-algebra-review", 3, "lin-algebra-review-r3-q4", "find_error",
            "A note claims the rank of a matrix. Exactly one step is false.",
            [
                r"Rank is the number of independent columns.",
                r"A row that is a copy of another row does not raise the rank.",
                r"A matrix with every entry nonzero must have full rank.",
                r"Rank plus the dimension of the null space equals the number of columns.",
            ],
            2,
            r"Nonzero entries do not make columns independent. Two identical nonzero columns still have rank 1. Rank counts independent directions, and rank plus nullity equals the number of columns for any matrix, whether or not an entry is zero.",
            reasons=[
                "Nonzero entries can still be copies of one column.",
                "A copied row does raise the rank.",
                "Rank-nullity holds only for square matrices.",
            ],
            correct_reason=0,
            fig=tall,
            alt="A tall matrix with three rows and two columns.",
        ),
        built(
            "lin-algebra-review", 3, "lin-algebra-review-r3-q5", "multi",
            r"Which statements are true of every matrix \(A\)?",
            [
                r"The null space contains the zero vector.",
                r"A nonzero null vector means the columns are independent.",
                r"The determinant of a square matrix is zero when a nonzero vector is sent to zero.",
                r"Rank is the number of entries in the matrix.",
            ],
            [0, 2],
            r"Zero is always sent to zero, so it is always in the null space. A nonzero null vector is a dependence among the columns, and for a square matrix that is exactly a zero determinant. Rank counts independent columns, not entries.",
            fig=tall,
            alt="A matrix with more rows than columns.",
        ),
        built(
            "lin-algebra-review", 4, "lin-algebra-review-r4-q4", "num",
            r"What is the rank of \(\begin{bmatrix} 1 & 0 \\ 2 & 1 \\ 0 & 3 \end{bmatrix}\)?",
            2,
            "",
            r"The two columns are \((1, 2, 0)\) and \((0, 1, 3)\). Neither is a scalar multiple of the other, so there are two independent columns and the rank is 2. A third row does not add a third column, so the rank cannot be 3.",
            fig=tall,
            alt="A 3 by 2 matrix.",
            preview=["linear-least-squares"],
        ),
    ]
    bump(bank)
    dump(bank)


def patch_eig_modes():
    bank = load("eig-modes", "bank")
    for qid in (
        "eig-modes-r2-q2",
        "eig-modes-r2-q3",
        "eig-modes-r3-q1",
        "eig-modes-r4-q2",
    ):
        retire(bank, qid)
    retarget(bank, "eig-modes-r4-q1", ["lti-stability"])
    pair = splane([(-8, 5), (-8, -5)], [], "A complex conjugate pair")
    bank["questions"] += [
        built(
            "eig-modes", 2, "eig-modes-r2-q4", "num",
            r"A mode has eigenvalue \(-8 + 5j\). What is its time constant?",
            0.125,
            "s",
            r"The time constant is the reciprocal of the decay rate. The decay rate is the absolute value of the real part, which is 8, so the time constant is \(1/8 = 0.125\) s. The imaginary part 5 sets the oscillation. It does not set the time constant.",
            fig=pair,
            alt="A complex conjugate pair in the left half-plane.",
        ),
        built(
            "eig-modes", 2, "eig-modes-r2-q5", "order",
            r"Put these steps in the order you would use to read a complex mode \(\sigma + j\omega\) with \(\sigma < 0\).",
            [
                r"Read the decay rate from the absolute value of the real part.",
                r"Take the time constant as the reciprocal of that decay rate.",
                r"Read the oscillation rate from the imaginary part.",
                r"Keep the conjugate partner, because a real matrix produces both.",
            ],
            r"The real part is the decay. Its absolute value is the rate, and the time constant is the reciprocal of that rate. The imaginary part is the oscillation, in radians per second. A real matrix that has one complex eigenvalue also has the conjugate, so the pair is one oscillatory mode, not two unrelated real modes.",
            fig=pair,
            alt="Two poles symmetric across the real axis.",
        ),
        built(
            "eig-modes", 3, "eig-modes-r3-q4", "find_error",
            r"A note writes the free response of a repeated eigenvalue \(-9\) that has only one independent eigenvector. Exactly one step is false.",
            [
                r"The first solution along that eigenvector is a multiple of \(e^{-9t}\).",
                r"One eigenvector is not a basis of the plane.",
                r"The second solution is another copy of \(e^{-9t}\), with no factor of \(t\).",
                r"The extra factor in the second solution is \(t\).",
            ],
            2,
            r"A repeated eigenvalue with only one eigenvector is a Jordan block. One solution is \(e^{-9t} v\). The second solution has the extra factor \(t\), so it is not a second pure exponential. Two copies of \(e^{-9t}\) would be the diagonalizable case, which needs two independent eigenvectors.",
            reasons=[
                r"A Jordan block brings a factor of \(t\) on the second solution.",
                "The first solution is not an exponential.",
                "One eigenvector is already a basis of the plane.",
            ],
            correct_reason=0,
        ),
        built(
            "eig-modes", 4, "eig-modes-r4-q4", "multi",
            r"Which statements describe a mode of \(\dot x = Ax\)?",
            [
                r"A real eigenvalue \(\lambda\) contributes a factor \(e^{\lambda t}\).",
                r"The time constant of a decaying mode is the imaginary part.",
                r"A complex pair produces an oscillation inside a real exponential envelope.",
                r"A Jordan block for a repeated eigenvalue adds a factor of \(t\).",
            ],
            [0, 2, 3],
            r"A simple real eigenvalue contributes \(e^{\lambda t} v\). A complex pair contributes a damped oscillation, and the envelope rate is the real part. The time constant is the reciprocal of that rate, not the imaginary part. When diagonalization fails, the extra solution carries a factor of \(t\).",
            preview=["linearization"],
        ),
    ]
    bump(bank)
    dump(bank)


def patch_spectral():
    bank = load("spectral-decomposition", "bank")
    for qid in (
        "spectral-decomposition-r1-q2",
        "spectral-decomposition-r2-q2",
        "spectral-decomposition-r2-q3",
        "spectral-decomposition-r3-q2",
        "spectral-decomposition-r3-q3",
        "spectral-decomposition-r4-q1",
    ):
        retire(bank, qid)
    axes = plane_vectors([(1, 1, "u1"), (1, -1, "u2")], "Two perpendicular directions")
    bank["questions"] += [
        built(
            "spectral-decomposition", 1, "spectral-decomposition-r1-q4", "order",
            r"Put these steps in the order you would use to rebuild a symmetric matrix from its orthonormal eigenvectors.",
            [
                r"Place the orthonormal eigenvectors in the columns of \(U\).",
                r"Place the matching eigenvalues on the diagonal of \(D\).",
                r"Form the product \(U D U^T\).",
                r"Check that \(U^T U\) is the identity, so the inverse of \(U\) is the transpose.",
            ],
            r"The columns of \(U\) are the orthonormal eigenvectors, and \(D\) holds the eigenvalues in the same order. The product \(U D U^T\) returns the matrix in the original coordinates. Orthonormal columns are what make the inverse equal to the transpose. The product \(U D U\) would be the wrong third factor.",
            fig=axes,
            alt="Two arrows from the origin at right angles.",
        ),
        built(
            "spectral-decomposition", 2, "spectral-decomposition-r2-q4", "num",
            r"The columns of \(U\) are \((1, 1)/\sqrt{2}\) and \((1, -1)/\sqrt{2}\), and \(D = \mathrm{diag}(12, 4)\). For \(A = U D U^T\), what is the top-left entry of \(A\)?",
            8,
            "",
            r"Each entry of \(A\) is a weighted sum of the eigenvalues, with weights from the matching entries of the columns. The top-left weights are both \(1/2\), so the entry is \((12 + 4)/2 = 8\). It is not the larger eigenvalue by itself, and it is not the sum 16.",
            fig=axes,
            alt="Two perpendicular arrows of equal length.",
        ),
        built(
            "spectral-decomposition", 2, "spectral-decomposition-r2-q5", "sym",
            r"In an orthonormal eigenbasis a symmetric matrix has eigenvalues p and q, and a vector has coordinates a and b. Write the quadratic form in the names p, q, a, and b.",
            "p*a*a+q*b*b",
            {"p": (0.5, 4), "q": (0.5, 4), "a": (-2, 2), "b": (-2, 2)},
            r"Along orthonormal eigenvectors the cross terms vanish, so the form is \(p a^2 + q b^2\). Each eigenvalue multiplies the square of its own coordinate. Adding the eigenvalues, or multiplying them, is the trace or the determinant, not the form.",
            alternates=["a*p*a+b*q*b"],
        ),
        built(
            "spectral-decomposition", 3, "spectral-decomposition-r3-q4", "find_error",
            "A note rebuilds a symmetric matrix from orthonormal eigenvectors. Exactly one step is false.",
            [
                r"The columns of \(U\) are orthonormal eigenvectors.",
                r"\(D\) is the diagonal matrix of eigenvalues, in the same order as the columns.",
                r"Because the columns are orthonormal, \(U^{-1} = U\).",
                r"The matrix factors as \(U D U^T\).",
            ],
            2,
            r"Orthonormal columns mean \(U^T U = I\), so the inverse is the transpose, not \(U\) itself. The product that rebuilds the matrix is \(U D U^T\). Replacing the transpose by \(U\) is a different product.",
            reasons=[
                r"The inverse of an orthonormal \(U\) is \(U^T\), not \(U\).",
                r"\(D\) holds the singular values rather than the eigenvalues.",
                r"The third factor is \(U^{-1}\) written as \(U\).",
            ],
            correct_reason=0,
        ),
        built(
            "spectral-decomposition", 3, "spectral-decomposition-r3-q5", "multi",
            "Which statements are true of a real symmetric matrix?",
            [
                r"It has a full set of real eigenvalues.",
                r"Its eigenvectors can be chosen orthonormal.",
                r"Its inverse is always the transpose.",
                r"In an orthonormal eigenbasis it is diagonal.",
            ],
            [0, 1, 3],
            r"A real symmetric matrix has real eigenvalues and an orthonormal basis of eigenvectors, and in that basis it is the diagonal matrix of those eigenvalues. The transpose is the inverse of the eigenvector matrix, not of the original matrix. A symmetric matrix need not be invertible at all.",
        ),
        built(
            "spectral-decomposition", 4, "spectral-decomposition-r4-q4", "num",
            r"A symmetric matrix has eigenvalues \(-9\) and \(1\). Which eigenvalue has the larger absolute value?",
            -9,
            "",
            r"The absolute values are 9 and 1. The larger absolute value belongs to \(-9\). The eigenvalue that is larger as a signed number is \(1\), and that is a different question. Power iteration follows the eigenvalue of largest magnitude.",
            preview=["power-method-eigenvector"],
        ),
    ]
    bump(bank)
    dump(bank)


def patch_pd():
    bank = load("positive-definite-matrices", "bank")
    for qid in (
        "positive-definite-matrices-r1-q3",
        "positive-definite-matrices-r2-q2",
        "positive-definite-matrices-r2-q3",
    ):
        retire(bank, qid)
    ell = ellipse_axes("A positive level set")
    bank["questions"] += [
        built(
            "positive-definite-matrices", 1, "positive-definite-matrices-r1-q4", "multi",
            "A symmetric matrix has the eigenvalues listed. Which of these sets make the matrix positive definite?",
            [
                r"\(5\) and \(2\)",
                r"\(5\) and \(0\)",
                r"\(5\) and \(-1\)",
                r"\(7\) and \(1\)",
            ],
            [0, 3],
            r"Positive definite means every eigenvalue is positive. Both 5 and 2 are positive, and both 7 and 1 are positive. A zero eigenvalue is the semidefinite boundary, and a negative eigenvalue makes the form negative along that eigenvector.",
            fig=ell,
            alt="An ellipse centered at the origin, longer along the first axis.",
        ),
        built(
            "positive-definite-matrices", 2, "positive-definite-matrices-r2-q4", "order",
            "Put these steps in the order of the eigenvalue test for a symmetric matrix.",
            [
                r"Confirm the matrix is symmetric.",
                r"Compute every eigenvalue.",
                r"Call the matrix positive definite only when every eigenvalue is positive.",
                r"If a zero eigenvalue remains and the others are positive, call it semidefinite instead.",
            ],
            r"The test applies to a symmetric matrix. Positive definite means every eigenvalue is strictly positive. A zero eigenvalue, with the others positive, makes the form vanish on that eigenvector, so the matrix is semidefinite rather than definite. One negative eigenvalue makes the form indefinite.",
            fig=ell,
            alt="An axis-aligned ellipse.",
        ),
        built(
            "positive-definite-matrices", 2, "positive-definite-matrices-r2-q5", "find_error",
            r"A note classifies \(A = \mathrm{diag}(6, 0)\). Exactly one step is false.",
            [
                r"\(A\) is symmetric.",
                r"The eigenvalues are the diagonal entries 6 and 0.",
                r"Both eigenvalues are positive, so \(A\) is positive definite.",
                r"The form is zero on the second axis and positive on the first.",
            ],
            2,
            r"The eigenvalues are 6 and 0. Zero is not positive, so the matrix is positive semidefinite and not positive definite. The form \(6 x_1^2\) vanishes for every vector on the second axis. A positive definite form is positive for every nonzero vector.",
            reasons=[
                "A zero eigenvalue is semidefinite, not definite.",
                "The diagonal entries are not the eigenvalues.",
                "The form is negative on the second axis.",
            ],
            correct_reason=0,
        ),
    ]
    bump(bank)
    dump(bank)


def patch_lls():
    bank = load("linear-least-squares", "bank")
    for qid in (
        "linear-least-squares-r2-q1",
        "linear-least-squares-r3-q1",
        "linear-least-squares-r4-q1",
        "linear-least-squares-r4-q2",
    ):
        retire(bank, qid)
    col = matrix_fig([["2"], ["3"], ["5"]], "One column")
    bank["questions"] += [
        built(
            "linear-least-squares", 2, "linear-least-squares-r2-q4", "order",
            r"The columns of \(A\) are independent. Put these steps in the order you would use to solve the least-squares problem.",
            [
                r"Form the Gram matrix \(A^T A\) and the vector \(A^T b\).",
                r"Solve the normal equations \(A^T A x = A^T b\).",
                r"The solution is unique because the columns are independent.",
                r"The residual \(b - Ax\) is orthogonal to every column of \(A\).",
            ],
            r"Independent columns make \(A^T A\) invertible, so the normal equations have one solution. That solution is the least-squares minimizer, and its residual is orthogonal to the column space. Forming the Gram matrix comes before the solve. Orthogonality is a property of the residual you just computed, not a step that replaces the solve.",
            fig=col,
            alt="A single column of three entries.",
        ),
        built(
            "linear-least-squares", 3, "linear-least-squares-r3-q4", "find_error",
            r"A note solves \(y = \theta u\) from several pairs. Exactly one step is false.",
            [
                r"The normal equation is \(\theta \sum u^2 = \sum u y\).",
                r"When every input equals 1, \(\theta\) is the average of the outputs.",
                r"For arbitrary inputs, \(\theta\) is still the average of the outputs.",
                r"A column that is not all zeros has full column rank, so the minimizer is unique.",
            ],
            2,
            r"The scalar normal equation weights each output by its input. It is the average of the outputs only when every input equals 1, because then \(\sum u^2\) is the number of samples and \(\sum u y\) is the sum of the outputs. Unequal inputs keep the squared inputs as weights.",
            reasons=[
                r"Unequal inputs weight the outputs by \(u\), so the result is not the plain average.",
                r"The normal equation uses \(\sum u\) on the left.",
                "A nonzero column can still be rank zero.",
            ],
            correct_reason=0,
        ),
        built(
            "linear-least-squares", 4, "linear-least-squares-r4-q4", "num",
            r"The pairs \((u, y)\) are \((2, 4)\), \((3, 7)\), and \((5, 8)\), and the model is \(y = \theta u\). What is the least-squares \(\theta\)?",
            69 / 38,
            "",
            r"One column \(a = (2, 3, 5)\) gives \(\theta = (a \cdot y) / (a \cdot a)\). The numerator is \(2 \cdot 4 + 3 \cdot 7 + 5 \cdot 8 = 69\). The denominator is \(4 + 9 + 25 = 38\). So \(\theta = 69/38\). The plain average of the outputs ignores the inputs.",
            fig=col,
            alt="Three input values stacked in one column.",
            preview=["sys-id"],
        ),
        built(
            "linear-least-squares", 4, "linear-least-squares-r4-q5", "mc",
            r"When the columns of \(A\) are independent, the least-squares minimizer is the solution of which equation?",
            [
                r"\(A^T A x = A^T b\)",
                r"\(A x = b\)",
                r"\(A A^T x = b\)",
                r"\(A^T x = b\)",
            ],
            0,
            r"Independent columns make \(A^T A\) invertible, and the minimizer solves the normal equations \(A^T A x = A^T b\). The equation \(Ax = b\) is exact interpolation, which an overdetermined system usually does not have. The products \(AA^T\) and \(A^T x\) have the wrong shapes for a tall \(A\).",
            preview=["least-squares-quadratic"],
        ),
    ]
    bump(bank)
    dump(bank)


def patch_sys_id():
    bank = load("sys-id", "bank")
    for qid in ("sys-id-r1-q3", "sys-id-r3-q1"):
        retire(bank, qid)
    rise = step_response("A settling step", tau=2.4, goal=1.0)
    bank["questions"] += [
        built(
            "sys-id", 1, "sys-id-r1-q4", "num",
            "A first-order step has settled. The output reaches 63 percent of the gap from its start to its settled value at 2.4 seconds. What is the time constant?",
            2.4,
            "s",
            r"For a first-order step, the time constant is the time at which the output has closed 63 percent of the gap. That time is given as 2.4 s, so the time constant is 2.4 s. The 63 percent point is not the settling time, and it is not the reciprocal of 2.4.",
            fig=rise,
            alt="A step response that rises toward a horizontal settled value.",
        ),
        built(
            "sys-id", 3, "sys-id-r3-q4", "num",
            "A fitted model predicts 8 on a held-out input. The measured output on that same input is 5.5. What is the residual, measured minus predicted?",
            -2.5,
            "",
            r"The residual is the measurement minus the prediction: \(5.5 - 8 = -2.5\). The sign says the model is high. Adding the two numbers, or dividing them, is a different comparison. A residual is computed on a record that was not used to choose the parameters, and a large one rejects the fit.",
        ),
    ]
    bump(bank)
    dump(bank)


def patch_preview_targets():
    """Least squares is no longer downstream of these skills. The quadratic reading is."""
    moves = {
        "quadratic-function-minimization": "quadratic-function-minimization-r4-q1",
        "second-order-optimality": "second-order-optimality-r4-q3",
        "convex-optimality-global": "convex-optimality-global-r4-q3",
        "singular-value-decomposition": "singular-value-decomposition-r4-q3",
    }
    for sid, qid in moves.items():
        bank = load(sid, "bank")
        retarget(bank, qid, ["least-squares-quadratic"])
        bump(bank)
        dump(bank)


def write_eigen_core():
    b = Bank("eigenvalues-diagonalization")
    tri = matrix_fig([["5", "1"], ["0", "-2"]], "A triangular matrix")
    full = matrix_fig([["6", "1"], ["2", "5"]], "A 2 by 2 matrix")
    vecs = plane_vectors([(1, 0, "e1"), (1, 1, "v")], "A candidate eigenvector")
    b.mc(
        1,
        r"The eigenvalues of a square matrix \(A\) are the numbers \(\lambda\) for which",
        [
            r"\(Av = \lambda v\) for some nonzero vector \(v\).",
            r"\(Av = \lambda v\) only when \(v = 0\).",
            r"\(A + \lambda I\) is the zero matrix.",
            r"every entry of \(A\) equals \(\lambda\).",
        ],
        0,
        r"An eigenvalue is a stretch factor of a nonzero vector: \(Av = \lambda v\) with \(v \ne 0\). The zero vector satisfies the equation for every \(\lambda\), so it is not an eigenvector. Adding \(\lambda I\) to \(A\) is not the definition, and the entries of \(A\) need not equal \(\lambda\).",
    )
    b.num(
        1,
        r"What is the larger eigenvalue of the triangular matrix \(\begin{bmatrix} 5 & 1 \\ 0 & -2 \end{bmatrix}\)?",
        5,
        "",
        r"A triangular matrix lists its eigenvalues on the diagonal. Those entries are 5 and \(-2\). The larger one is 5. The off-diagonal 1 does not move the eigenvalues of a triangular matrix.",
        fig=tri,
        alt="An upper-triangular 2 by 2 matrix.",
    )
    b.order(
        1,
        "Put these steps in the order you would use to find the eigenvalues of a 2 by 2 matrix and check one of them.",
        [
            r"Compute the trace and the determinant.",
            r"Form \(\lambda^2 - (\mathrm{tr}\, A)\lambda + \det A\).",
            r"Solve that quadratic for \(\lambda\).",
            r"Check \(Av = \lambda v\) for a nonzero \(v\).",
        ],
        r"For a 2 by 2 matrix the characteristic polynomial is \(\lambda^2 - (\mathrm{tr}\, A)\lambda + \det A\). Its roots are the eigenvalues. A root still has to belong to a nonzero vector with \(Av = \lambda v\). The trace and the determinant come before the polynomial, and the polynomial comes before the check.",
        fig=full,
        alt="A 2 by 2 matrix with four numeric entries.",
    )
    b.sym(
        2,
        r"Let \(A = \begin{bmatrix} p & q \\ r & s \end{bmatrix}\). Write \(\det(\lambda I - A)\) in the names p, q, r, s, and l, using l for \(\lambda\).",
        "l*l-(p+s)*l+(p*s-q*r)",
        {"p": (-2, 2), "q": (-2, 2), "r": (-2, 2), "s": (-2, 2), "l": (-2, 2)},
        r"The matrix \(\lambda I - A\) has diagonal entries \(l - p\) and \(l - s\), and off-diagonal entries \(-q\) and \(-r\). Its determinant is \((l - p)(l - s) - qr\), which expands to \(l^2 - (p + s)l + (ps - qr)\). The trace \(p + s\) is subtracted. The product of the diagonal entries of \(A\), minus \(qr\), is the determinant.",
        alternates=["(l-p)*(l-s)-q*r"],
        fig=full,
        alt="A 2 by 2 matrix with letter entries.",
    )
    b.num(
        2,
        r"What is the larger eigenvalue of \(\begin{bmatrix} 6 & 1 \\ 2 & 5 \end{bmatrix}\)?",
        7,
        "",
        r"The trace is 11 and the determinant is \(30 - 2 = 28\). The polynomial is \(\lambda^2 - 11\lambda + 28 = (\lambda - 7)(\lambda - 4)\). The roots are 7 and 4, so the larger eigenvalue is 7. The trace itself is not an eigenvalue.",
        fig=full,
        alt="A 2 by 2 matrix.",
    )
    b.multi(
        2,
        r"Which statements are true when \(A = P D P^{-1}\) and \(D\) is diagonal?",
        [
            r"The diagonal entries of \(D\) are eigenvalues of \(A\).",
            r"The columns of \(P\) are eigenvectors of \(A\).",
            r"\(A\) and \(D\) have different eigenvalues.",
            r"This factorization needs a full set of eigenvectors.",
        ],
        [0, 1, 3],
        r"\(A = P D P^{-1}\) is a change of basis to the columns of \(P\). In that basis the matrix is diagonal, so those columns are eigenvectors and the diagonal entries are the eigenvalues. Similar matrices share their eigenvalues. The factorization exists only when there are enough independent eigenvectors to build \(P\).",
        fig=vecs,
        alt="Two arrows from the origin, one along the first axis.",
    )
    b.find_error(
        3,
        r"A note claims \(\begin{bmatrix} 2 & 1 \\ 0 & 2 \end{bmatrix}\) is diagonalizable. Exactly one step is false.",
        [
            r"The only eigenvalue is 2.",
            r"The equation \((A - 2I)v = 0\) has a one-dimensional solution.",
            r"Two independent eigenvectors exist, one for each copy of the eigenvalue.",
            r"A full set of eigenvectors is required before \(A = P D P^{-1}\).",
        ],
        2,
        r"\(A - 2I = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}\) has rank 1, so its null space has dimension 1. There is only one independent eigenvector. A repeated eigenvalue is not, by itself, a second eigenvector. The matrix is a Jordan block and is not diagonalizable.",
        reasons=[
            "A repeated eigenvalue can have only one eigenvector.",
            "The only eigenvalue is not 2.",
            r"The null space of \(A - 2I\) is the whole plane.",
        ],
        correct_reason=0,
        fig=matrix_fig([["2", "1"], ["0", "2"]], "A repeated diagonal"),
        alt="A triangular matrix with equal diagonal entries.",
    )
    b.num(
        3,
        r"Let \(A = \begin{bmatrix} 3 & 1 \\ 0 & 4 \end{bmatrix}\) and \(v = \begin{bmatrix} 1 \\ 1 \end{bmatrix}\). Which eigenvalue belongs to \(v\)?",
        4,
        "",
        r"\(Av = (4, 4) = 4v\). The eigenvalue is 4. The other diagonal entry, 3, is the other eigenvalue, and \(v\) is not an eigenvector for 3. The first entry of \(Av\) being 4 is the check, not a different eigenvalue.",
        fig=vecs,
        alt="An arrow along the first axis and a second arrow up and to the right.",
    )
    b.mc(
        3,
        "A square matrix fails to be diagonalizable when",
        [
            r"it does not have a full set of independent eigenvectors.",
            r"its trace is negative.",
            r"it is triangular.",
            r"it has a zero entry.",
        ],
        0,
        r"Diagonalizable means \(A = P D P^{-1}\) for an invertible \(P\), and the columns of \(P\) are eigenvectors. That fails exactly when there are too few independent eigenvectors. A triangular matrix can be diagonalizable, a negative trace does not decide it, and a zero entry does not decide it.",
    )
    b.num(
        4,
        r"The eigenvalues of \(\begin{bmatrix} -1 & 4 \\ 0 & -6 \end{bmatrix}\) are real. Which one is closer to zero?",
        -1,
        "",
        r"The matrix is triangular, so the eigenvalues are the diagonal entries \(-1\) and \(-6\). Distances to zero are 1 and 6. The closer eigenvalue is \(-1\). The more negative eigenvalue is \(-6\), which is farther from zero.",
        fig=splane([(-1, 0), (-6, 0)], [], "Two real eigenvalues"),
        alt="Two marks on the negative real axis, one nearer the origin.",
        preview=["eig-modes"],
    )
    b.num(
        4,
        r"What is the larger eigenvalue of the symmetric matrix \(\begin{bmatrix} 8 & 2 \\ 2 & 5 \end{bmatrix}\)?",
        9,
        "",
        r"The trace is 13 and the determinant is \(40 - 4 = 36\). The polynomial is \(\lambda^2 - 13\lambda + 36 = (\lambda - 9)(\lambda - 4)\). The roots are 9 and 4, so the larger eigenvalue is 9. Symmetry says the eigenvectors can be chosen orthonormal. It does not change this polynomial.",
        fig=matrix_fig([["8", "2"], ["2", "5"]], "A symmetric matrix"),
        alt="A symmetric 2 by 2 matrix.",
        preview=["spectral-decomposition"],
    )
    b.mc(
        4,
        r"If \(B = P^{-1} A P\) with \(P\) invertible, what must \(A\) and \(B\) share?",
        [
            r"Their eigenvalues.",
            r"Their eigenvectors, written in the same coordinates.",
            r"Every entry.",
            r"Their null spaces, written in the same coordinates.",
        ],
        0,
        r"Similar matrices represent the same linear map in two bases, so they have the same eigenvalues, the same trace, and the same determinant. The eigenvectors change coordinates with \(P\). The entries change, and a vector in the null space of \(A\) is not automatically that same coordinate vector for \(B\).",
        preview=["positive-definite-matrices"],
    )
    b.save()


def write_lsq():
    b = Bank("least-squares-quadratic")
    curve = matrix_fig([["a", "x"], ["-", "b"]], "A scalar residual")
    b.mc(
        1,
        r"For a residual \(Ax - b\), the normal equations are",
        [
            r"the stationarity condition of the squared residual.",
            r"a requirement that the residual is zero.",
            r"the definition of a singular value.",
            r"true only when \(A\) is square.",
        ],
        0,
        r"The squared length \(\lVert Ax - b \rVert^2\) is a quadratic in \(x\). Its gradient vanishes exactly at the normal equations \(A^T A x = A^T b\). A zero residual is the special case where \(b\) is already in the column space. The same stationarity condition is valid for a tall matrix.",
        fig=curve,
        alt="A column and a right-hand side, written as a residual.",
    )
    b.num(
        1,
        r"The scalar objective \((3x - 9)^2\) is a squared residual. What value of \(x\) makes it stationary?",
        3,
        "",
        r"Expanding is unnecessary. The derivative of \((3x - 9)^2\) is \(2(3x - 9) \cdot 3\), which vanishes when \(3x - 9 = 0\), so \(x = 3\). The stationary value of the objective is 0 here, and that is the objective, not the location of the minimizer.",
    )
    b.order(
        1,
        r"Put these steps in the order that derives the normal equations from \(\lVert Ax - b \rVert^2\).",
        [
            r"Treat the squared residual as a quadratic function of \(x\).",
            r"Differentiate it to get the gradient \(2 A^T(Ax - b)\).",
            r"Set that gradient equal to zero.",
            r"Rewrite the equation as \(A^T A x = A^T b\).",
        ],
        r"The squared residual is a quadratic. Its gradient is \(2 A^T(Ax - b)\). Stationarity sets the gradient to zero, and rearranging produces the normal equations. The gradient formula comes before setting it to zero, and the normal equations are that condition written with the unknown on the left.",
    )
    b.sym(
        2,
        r"A one-row residual is \(a x - b\), with \(a \ne 0\). The stationary point of its square is a function of a and b. Write that \(x\).",
        "b/a",
        {"a": (1, 4), "b": (-3, 3)},
        r"The objective \((ax - b)^2\) has derivative \(2(ax - b)a\). It vanishes at \(x = b/a\). That is the scalar normal equation \(a^2 x = a b\), divided by \(a^2\). The ratio \(a/b\) is the reciprocal of the minimizer.",
        alternates=["(a*b)/(a*a)"],
    )
    b.num(
        2,
        r"The column is \((3, 6)\) and the right-hand side is \((3, 3)\). The least-squares fit is one number \(x\). What is \(x\)?",
        0.6,
        "",
        r"The normal equation is \((9 + 36) x = 9 + 18\), so \(45x = 27\) and \(x = 0.6\). The pseudoinverse of a single column \(a\) applies \(a^T / (a^T a)\) to the right-hand side. Averaging the two right-hand entries gives 3, which ignores the column.",
        fig=matrix_fig([["3"], ["6"]], "A column of two entries"),
        alt="A column with two entries.",
    )
    b.multi(
        2,
        r"The columns of \(A\) are independent, and \(A^+ = (A^T A)^{-1} A^T\). Which statements are true?",
        [
            r"The least-squares minimizer is \(A^+ b\).",
            r"\(A^+ A = I\).",
            r"\(A A^+ = I\) whenever \(A\) has more rows than columns.",
            r"\(A^+\) is the left inverse that the normal equations build.",
        ],
        [0, 1, 3],
        r"Full column rank makes \(A^T A\) invertible, and \(x = A^+ b\) is the minimizer. Then \(A^+ A = I\), so \(A^+\) is a left inverse. For a tall matrix \(A A^+\) is the projection onto the column space, not the identity on the larger space.",
    )
    b.find_error(
        3,
        r"A note writes the pseudoinverse of a tall full-column-rank matrix. Exactly one step is false.",
        [
            r"\(A^+ = (A^T A)^{-1} A^T\).",
            r"The minimizer of the squared residual is \(A^+ b\).",
            r"\(A^+ A = I\).",
            r"\(A A^+ = I\) as well, because the columns are independent.",
        ],
        3,
        r"Independent columns give \(A^+ A = I\). They do not give \(A A^+ = I\) when \(A\) is tall. The product \(A A^+\) projects onto the column space. It is the identity on the whole output space only when the columns also span that space, which a tall matrix cannot do.",
        reasons=[
            r"\(A A^+\) is a projection, not the identity, when \(A\) is tall.",
            r"The formula for \(A^+\) uses \(AA^T\) on a tall matrix.",
            r"\(A^+ A\) fails to be the identity when the columns are independent.",
        ],
        correct_reason=0,
    )
    b.num(
        3,
        r"Let \(A = \begin{bmatrix} 1 \\ 3 \end{bmatrix}\) and \(b = \begin{bmatrix} 2 \\ 6 \end{bmatrix}\). The pseudoinverse fit is one number. What is it?",
        2,
        "",
        r"\(A^T A = 10\) and \(A^T b = 20\), so \(x = 2\). The same value is \(A^+ b\). The right-hand side is exactly twice the column, so the residual is zero and the fit is exact. Dividing the first entries, \(2/1\), happens to agree here. It is not the formula.",
        fig=matrix_fig([["1"], ["3"]], "A column"),
        alt="A column of two entries.",
    )
    b.mc(
        3,
        r"For full column rank, which expression is the least-squares minimizer?",
        [
            r"\((A^T A)^{-1} A^T b\)",
            r"\((A A^T)^{-1} A b\)",
            r"\(A^T A b\)",
            r"\(A^{-1} b\), even when \(A\) is not square",
        ],
        0,
        r"The minimizer is \(A^+ b = (A^T A)^{-1} A^T b\). The Gram matrix that is inverted is the small one, \(A^T A\). The product \(AA^T\) is singular for a tall full-column-rank matrix. A matrix that is not square has no inverse.",
    )
    b.num(
        4,
        r"Three measurements of one unknown are 1, 1, and 16, and the column is a column of ones. What is the least-squares value?",
        6,
        "",
        r"A column of ones makes the normal equation \(3x = 1 + 1 + 16\), so \(x = 6\). That is the average. The squared residual is a quadratic in this one unknown, and the average is its stationary point. The value 16 is one measurement, not the fit.",
        preview=["nonlinear-least-squares"],
    )
    b.mc(
        4,
        "Writing the least-squares minimizer as a pseudoinverse is the same statement as",
        [
            r"solving the normal equations when the columns are independent.",
            r"requiring the residual to be zero.",
            r"replacing a tall matrix by its transpose.",
            r"setting every singular value to 1.",
        ],
        0,
        r"When the columns are independent, \(A^+ b\) is exactly the solution of \(A^T A x = A^T b\). A zero residual is a special case. The transpose of a tall matrix is not a minimizer, and the singular values of \(A\) are not changed by writing the pseudoinverse.",
        preview=["kalman-recursive-least-squares"],
    )
    b.num(
        4,
        r"\(A\) has rows \((1, 0)\), \((1, 0)\), and \((0, 1)\), and \(b = (1, 9, 5)\). The least-squares solution is \((x_1, x_2)\). What is \(x_1\)?",
        5,
        "",
        r"The two columns are orthogonal. The first column sees the first two rows, so \(2 x_1 = 1 + 9\) and \(x_1 = 5\). The second column sees only the last row, so \(x_2 = 5\) as well. The first component is not the average of all three right-hand entries.",
        fig=matrix_fig([["1", "0"], ["1", "0"], ["0", "1"]], "Two orthogonal columns"),
        alt="A 3 by 2 matrix with orthogonal columns.",
        preview=["circle-fitting-least-squares"],
    )
    b.save()


def write_explainers():
    eig_fig = matrix_fig([["13", "0"], ["0", "15"]], "A diagonal matrix")
    save_explainer(
        "eigenvalues-diagonalization",
        "Eigenvalues and diagonalization",
        [
            {
                "heading": "The idea",
                "figure": eig_fig,
                "figure_alt": "A diagonal 2 by 2 matrix.",
                "body_md": r"An eigenvector is a nonzero vector that a matrix only stretches. The stretch factor is the eigenvalue: \(Av = \lambda v\). The zero vector satisfies that equation for every number, so it is excluded. For a 2 by 2 matrix the eigenvalues are the roots of a quadratic built from the trace and the determinant.",
            },
            {
                "heading": "Key equations",
                "body_md": r"The characteristic polynomial is \(\det(\lambda I - A)\). For \(A = \begin{bmatrix} p & q \\ r & s \end{bmatrix}\), \[ \lambda^2 - (p + s)\lambda + (ps - qr) = 0. \] The sum of the roots is the trace. The product of the roots is the determinant. When a full set of eigenvectors exists they are the columns of an invertible \(P\), and \[ A = P D P^{-1} \] with the eigenvalues on the diagonal of \(D\). A triangular matrix lists its eigenvalues on its own diagonal.",
            },
            {
                "heading": "Worked example",
                "body_md": r"Take the diagonal matrix \(\mathrm{diag}(13, 15)\). The characteristic polynomial is \((\lambda - 13)(\lambda - 15)\). The eigenvalues are 13 and 15, which are the diagonal entries. The first standard basis vector is an eigenvector for 13, and the second is an eigenvector for 15. The eigenvector matrix can be the identity, and \(D\) holds 13 and 15. A matrix similar to this one has the same eigenvalues. Its eigenvectors are those two directions written in the other coordinates.",
            },
            {
                "heading": "Common pitfalls",
                "body_md": r"- Adding the trace instead of subtracting it in \(\det(\lambda I - A)\). - Treating a repeated eigenvalue as two eigenvectors. The matrix \(\begin{bmatrix} 2 & 1 \\ 0 & 2 \end{bmatrix}\) has a single eigenvector direction. - Reading an off-diagonal entry of a triangular matrix as an eigenvalue. - Expecting a change of coordinates to change the eigenvalues. It changes the coordinates of the eigenvectors.",
            },
            {
                "heading": "Where this leads",
                "body_md": r"A mode of a linear system is \(e^{\lambda t} v\), and the time constant is read from the real part. A real symmetric matrix has orthonormal eigenvectors and the factorization \(A = U D U^T\). A symmetric matrix is positive definite exactly when every one of these eigenvalues is positive.",
            },
        ],
    )
    # The Jordan pitfall uses the same matrix as a quiz. Replace that sentence
    # so the worked numbers and the pitfall matrix are not a live question.
    exp = load("eigenvalues-diagonalization", "explainer")
    set_section(
        exp,
        "Common pitfalls",
        r"- Adding the trace instead of subtracting it in \(\det(\lambda I - A)\)."
        "\n- Treating a repeated eigenvalue as two eigenvectors. A single off-diagonal 1 above a repeated diagonal entry leaves only one eigenvector direction."
        "\n- Reading an off-diagonal entry of a triangular matrix as an eigenvalue."
        "\n- Expecting a change of coordinates to change the eigenvalues. It changes the coordinates of the eigenvectors.",
    )
    dump(exp)

    lsq_fig = matrix_fig([["4"], ["4"]], "A column used in a fit")
    save_explainer(
        "least-squares-quadratic",
        "Least squares as a quadratic",
        [
            {
                "heading": "The idea",
                "figure": lsq_fig,
                "figure_alt": "A column of two equal entries.",
                "body_md": r"The squared residual \(\lVert Ax - b \rVert^2\) is a quadratic function of \(x\). Its gradient is \(2 A^T(Ax - b)\), and setting that gradient to zero is the normal equation \(A^T A x = A^T b\). When the columns are independent, \(A^T A\) is invertible and the stationary point is the unique minimizer.",
            },
            {
                "heading": "Key equations",
                "body_md": r"Stationarity: \[ A^T A x = A^T b. \] The pseudoinverse of a full-column-rank matrix is \[ A^+ = (A^T A)^{-1} A^T, \] and the minimizer is \(x = A^+ b\). Then \(A^+ A = I\). For a tall matrix, \(A A^+\) is the projection onto the column space rather than the identity. A scalar residual \(ax - b\) has its square stationary at \(x = b/a\).",
            },
            {
                "heading": "Worked example",
                "body_md": r"Take the column \((4, 4)\) and the right-hand side \((8, 14)\). Then \(A^T A = 32\) and \(A^T b = 88\), so the stationary point is \(88/32 = 2.75\). The same number is the pseudoinverse applied to the right-hand side: \(A^+ = (1/8, 1/8)\) and \((1/8) \cdot 8 + (1/8) \cdot 14 = 2.75\). The residual is \((8 - 11, 14 - 11) = (-3, 3)\). It is orthogonal to the column, because \(4 \cdot (-3) + 4 \cdot 3 = 0\). The fit is not exact. The squared length of the residual is 18, which is the value of the quadratic at the stationary point.",
            },
            {
                "heading": "Common pitfalls",
                "body_md": r"- Replacing \(A^T b\) by \(b\) in the stationarity condition. - Inverting \(AA^T\) for a tall full-column-rank matrix. That larger Gram matrix is singular. - Claiming \(A A^+ = I\) just because \(A^+ A = I\). The first product is a projection when there are more rows than columns. - Expecting the gradient of the squared residual to be \(2A(Ax - b)\) with no transpose.",
            },
            {
                "heading": "Where this leads",
                "body_md": r"A model that is nonlinear in its parameters keeps a residual, but the residual is no longer linear in the unknown, so one normal equation is not the whole fit. A recursive update of the same normal equation takes rows one block at a time. Fitting a circle is the same stationarity idea with a different model.",
            },
        ],
    )


def patch_explainers():
    lin = load("lin-algebra-review", "explainer")
    set_section(
        lin,
        "The idea",
        "Rank counts independent directions in a matrix. The null space is every vector the matrix sends to zero. The determinant of a square matrix is zero exactly when that null space contains a nonzero vector. A matrix-vector product is the mixture of the columns given by the entries of the vector.\n\n"
        "For any matrix, rank plus the dimension of the null space equals the number of columns. A row that is a copy of another row does not raise the rank. Elimination makes the count visible: the number of nonzero rows that remain is the rank. None of this depends on a particular plant. Eigenvalues, and a change of basis that diagonalizes a matrix, are the next skill.",
    )
    set_section(
        lin,
        "Key equations",
        r"For \(A = \begin{bmatrix} a & b \\ c & d \end{bmatrix}\), \[ \det A = ad - bc. \] Rank plus nullity equals the number of columns. The product \(Av\) is a linear combination of the columns of \(A\), with weights taken from \(v\). A square matrix has a nonzero null vector exactly when its determinant is zero.",
    )
    set_section(
        lin,
        "Worked example",
        r"Take \(B = \begin{bmatrix} 2 & 6 \\ 1 & 3 \end{bmatrix}\). The second column is three times the first, so the rank is 1 and the determinant is 0. A null vector is \(\begin{bmatrix} 3 \\ -1 \end{bmatrix}\), because \(B\) sends it to zero."
        "\n\n"
        r"Separately, \(C\begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} 7 \\ 8 \end{bmatrix}\) with \(C = \begin{bmatrix} 5 & 1 \\ 2 & 3 \end{bmatrix}\) gives \(x = 1\), \(y = 2\): from \(5x + y = 7\) and \(2x + 3y = 8\), elimination produces \(13y = 26\).",
    )
    set_section(
        lin,
        "Common pitfalls",
        "- Calling a matrix full rank because no entry is zero. Every entry can be nonzero while the rank is 1.\n"
        "- Confusing the column space, which is everything the matrix can produce, with the null space, which is everything the matrix sends to zero.\n"
        "- Adding the diagonal products instead of subtracting them in a 2 by 2 determinant.\n"
        "- Counting rows, rather than independent columns, as the rank of a tall matrix.",
    )
    set_section(
        lin,
        "Where this leads",
        "Reachability stacks input directions and asks whether the rank equals the number of states. Observability stacks output directions and asks the same question. Least squares needs the columns of the data matrix to be independent before the normal equations have one solution. Eigenvalues are the stretch factors of a square matrix, and they are a separate skill.",
    )
    save_exp(lin)

    modes = load("eig-modes", "explainer")
    set_section(
        modes,
        "The idea",
        r"A mode is one piece of the free motion \(\dot x = Ax\). A real eigenvalue \(\lambda\) with eigenvector \(v\) contributes a multiple of \(e^{\lambda t} v\). The time constant of a decaying mode is the reciprocal of the absolute value of the real part. A complex conjugate pair contributes an oscillation at the imaginary part, inside an envelope set by the real part."
        "\n\n"
        r"When a repeated eigenvalue has a full set of eigenvectors, each copy is still a pure exponential. When it does not, the matrix is not diagonalizable, and the missing direction brings a factor of \(t\) in front of \(e^{\lambda t}\). Computing the eigenvalues themselves is the previous skill. This skill reads the motion from an eigenvalue you already have.",
    )
    set_section(
        modes,
        "Key equations",
        r"Free motion: \(x(t) = e^{At} x(0)\). When a full set of eigenvectors exists, \(A = V \Lambda V^{-1}\) and \[ e^{At} = V e^{\Lambda t} V^{-1}. \] A mode \(\sigma + j\omega\) decays at rate \(|\sigma|\) and oscillates at \(\omega\). Its time constant is \(1/|\sigma|\). A Jordan block for a repeated eigenvalue contributes an extra factor of \(t\).",
    )
    set_section(
        modes,
        "Worked example",
        r"A real eigenvalue \(-6\) contributes \(e^{-6t}\). At one second the factor is \(e^{-6} = 0.0025\). The time constant of that mode is the reciprocal of 6. A complex pair \(-7 \pm j4\) decays at rate 7 and oscillates at 4 radians per second. The envelope time constant is the reciprocal of 7. The imaginary part is not the time constant. If \(-6\) were a double eigenvalue with only one eigenvector, the second solution would carry a factor of \(t\) and would not be another copy of \(e^{-6t}\).",
    )
    set_section(
        modes,
        "Common pitfalls",
        "- Reading the time constant from the imaginary part. The imaginary part is the oscillation.\n"
        "- Treating a repeated eigenvalue as automatically diagonalizable. Count the independent eigenvectors.\n"
        r"- Dropping the factor of \(t\) in a Jordan block.\n"
        r"- Computing the matrix exponential entry by entry. Use \(V e^{\Lambda t} V^{-1}\) when the eigenvectors form a basis.",
    )
    set_section(
        modes,
        "Where this leads",
        "Stability of a linear system asks whether every mode decays. Linearization reads the modes of a nonlinear system from the eigenvalues of its derivative at an equilibrium. An unobservable mode is one that does not appear in the output.",
    )
    save_exp(modes)

    spec = load("spectral-decomposition", "explainer")
    set_section(
        spec,
        "The idea",
        r"A real symmetric matrix has real eigenvalues and a full set of eigenvectors that can be chosen orthonormal. Those directions are the axes of the stretch. In that basis the matrix is diagonal, and each diagonal entry is the eigenvalue along one axis."
        "\n\n"
        r"The factorization \(A = U D U^T\) says the same thing in the original coordinates. The factor \(U^T\) writes a vector in the eigenbasis, \(D\) multiplies each coordinate by its eigenvalue, and \(U\) returns to the original coordinates. Orthonormal columns are what make the inverse of \(U\) equal to \(U^T\). Finding the eigenvalues is the previous skill. This skill is the orthonormal basis and the product that rebuilds \(A\).",
    )
    set_section(
        spec,
        "Key equations",
        r"For symmetric \(A\), \[ A = U D U^T, \qquad U^T U = I, \qquad D = \mathrm{diag}(\lambda_1, \ldots, \lambda_n). \] The inverse of \(U\) is \(U^T\). Rebuilding \(A\) is a sum of rank-one pieces \( \lambda_i u_i u_i^T \). On a positive semidefinite matrix the singular values agree with the absolute values of the eigenvalues.",
    )
    set_section(
        spec,
        "Where this leads",
        r"The Rayleigh quotient of a symmetric matrix sits between the smallest and largest eigenvalues and equals an eigenvalue at the matching eigenvector. Singular values of a general matrix are the square roots of the eigenvalues of \(A^T A\). Power iteration follows the eigenvalue of largest magnitude.",
    )
    save_exp(spec)

    pd = load("positive-definite-matrices", "explainer")
    set_section(
        pd,
        "The idea",
        r"A symmetric matrix defines a quadratic form \(x^T A x\). The form is positive definite when that number is positive for every nonzero \(x\), and positive semidefinite when it is only nonnegative. Indefinite means the form takes both signs."
        "\n\n"
        r"The eigenvalue test is the practical version. For a symmetric matrix the form is positive for every nonzero vector exactly when every eigenvalue is positive, and nonnegative for every vector exactly when every eigenvalue is nonnegative. A single negative eigenvalue produces a direction in which the form is negative. A zero eigenvalue, with the others positive, is the semidefinite boundary: the form vanishes on that eigenvector."
        "\n\n"
        r"When every eigenvalue is positive, a positive level set of the form is an ellipse. The longer axis belongs to the smaller eigenvalue.",
    )
    save_exp(pd)

    lls = load("linear-least-squares", "explainer")
    set_section(
        lls,
        "The idea",
        r"An overdetermined linear equation \(Ax \approx b\) usually has no exact solution. Least squares asks for the \(x\) that makes the residual \(Ax - b\) as small as possible in the Euclidean norm. When the columns of \(A\) are independent, that \(x\) is the solution of the normal equations \(A^T A x = A^T b\). The same equation says the residual is orthogonal to every column of \(A\). Geometrically, \(Ax\) is the orthogonal projection of \(b\) onto the column space."
        "\n\n"
        r"The Gram matrix \(A^T A\) is invertible exactly when the columns are independent, and then the minimizer is unique. If the columns are dependent, the normal equations stay consistent but the minimizer is not unique. Setting a gradient of the squared residual to zero is how those equations are derived. That derivation, and the pseudoinverse that writes the same minimizer, is a later skill. This skill is the equation and the rank condition.",
    )
    set_section(
        lls,
        "Where this leads",
        r"Fitting a model that is linear in its parameters uses these normal equations with columns built from the data. Reading a gain and a time constant from step and frequency records is system identification, and the scalar fit \(y = \theta u\) is the same equation. Deriving the normal equations as the stationarity condition of a quadratic, and writing the minimizer as a pseudoinverse, is the next skill.",
    )
    save_exp(lls)

    sysid = load("sys-id", "explainer")
    set_section(
        sysid,
        "The idea",
        "System identification reads a model from input and output records. For a first-order plant the two numbers are the DC gain and the time constant. A step that has settled gives the gain as the ratio of the two settled changes. The time constant is the time the step takes to close 63 percent of that gap. A frequency measurement checks the magnitude of that same one-pole model.\n\n"
        "The arithmetic that solves a residual for parameters that appear linearly is the linear least-squares skill. Here the records decide which numbers you are allowed to read, and a held-out record decides whether to trust them. A small residual on the fitting record can hide a model that fails on a record you did not use.",
    )
    set_section(
        sysid,
        "Key equations",
        r"The DC gain is the settled output change divided by the input change. The magnitude of a one-pole model \(k/(\tau s + 1)\) is \[ \frac{k}{\sqrt{1 + (\omega \tau)^2}}. \] The residual on a sample is the measured output minus the model's prediction. A held-out record is a set of rows that were not used to choose the parameters.",
    )
    set_section(
        sysid,
        "Common pitfalls",
        "- Reading a gain from a step that has not settled.\n"
        "- Calling the 63 percent time a settling time. It is the time constant.\n"
        "- Treating a small residual on the fitting record as a held-out check.\n"
        "- Using a frequency where the magnitude has not moved, and then concluding the time constant could be anything.",
    )
    save_exp(sysid)


def report():
    sids = [
        "lin-algebra-review",
        "eigenvalues-diagonalization",
        "eig-modes",
        "spectral-decomposition",
        "positive-definite-matrices",
        "linear-least-squares",
        "least-squares-quadratic",
        "sys-id",
    ]
    for sid in sids:
        bank = load(sid, "bank")
        counts = {r: 0 for r in (1, 2, 3, 4)}
        deep = 0
        for q in bank["questions"]:
            counts[q["round"]] += 1
            if q["type"] in ("symbolic", "order", "error", "multi"):
                deep += 1
        exp = load(sid, "explainer")
        print(
            f"{sid}: rounds {counts} deep {deep} "
            f"retired {len(bank.get('retired_questions') or [])} words {words(exp['sections'])}"
        )


def main():
    path = os.path.join(BANK, "eigenvalues-diagonalization.json")
    if os.path.exists(path):
        sample = load("eigenvalues-diagonalization", "bank")
        if any(q.get("id") == SENTINEL for q in sample["questions"]):
            print("already applied")
            report()
            return
    patch_lin_algebra()
    patch_eig_modes()
    patch_spectral()
    patch_pd()
    patch_lls()
    patch_sys_id()
    patch_preview_targets()
    write_eigen_core()
    write_lsq()
    write_explainers()
    patch_explainers()
    report()


if __name__ == "__main__":
    main()
