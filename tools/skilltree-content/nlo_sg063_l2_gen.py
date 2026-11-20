#!/usr/bin/env python3
"""SG-063 mathematical preliminaries, linear algebra section.

Scope is nlo-tugraz/l2 intersected with the grandfather list. That
intersection is exactly six banks: rn-important-subsets,
singular-value-decomposition, rayleigh-quotient, inner-products,
vector-norms-lp, cauchy-schwarz-inequality. The other eleven skills in
that section are not grandfathered. Nothing is added to the grandfather list.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and positive.
No key is a difference of two independent positives. Every denominator is a
positive constant, so it is bounded away from zero. Prompt names are the
graded identifiers (a, b, c, not a_1).
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "rn-important-subsets",
    "singular-value-decomposition",
    "rayleigh-quotient",
    "inner-products",
    "vector-norms-lp",
    "cauchy-schwarz-inequality",
]


def qnum(qid):
    return int(qid.rsplit("-q", 1)[1])


def fresh(rnd, kind, *args, **kwargs):
    built = Bank("_slot")
    getattr(built, kind)(rnd, *args, **kwargs)
    item = built.qs[0]
    item.pop("id", None)
    item["version"] = 1
    return item


def swaps_for(sid):
    """(old mc id, replacement) in the order that assigns the next free ids."""
    if sid == "rn-important-subsets":
        return [
            ("rn-important-subsets-r1-q1", fresh(
                1, "order",
                r"Order how the unit simplex sits inside the nonnegative orthant of \(\mathbb{R}^n\), for an integer \(n \ge 1\). Each step after the first uses the result of the step before it.",
                [
                    r"Start from \(\mathbb{R}^n\): every real n-tuple. No coordinate constraint has been applied yet.",
                    r"Keep only the vectors from the previous step whose every coordinate is at least zero. That set is the nonnegative orthant.",
                    r"From the orthant in the previous step, keep only the vectors whose coordinates sum to 1. That set is the unit simplex.",
                    r"The vertices of the simplex from the previous step are the n standard basis vectors. The orthant from the second step properly contains that simplex, because the zero vector is in the orthant and its coordinates sum to 0, not to 1.",
                ],
                r"The nonnegative orthant is every vector with nonnegative coordinates. The unit simplex adds the requirement that the coordinates sum to 1, so its vertices are the standard basis vectors and the origin stays in the orthant but not in the simplex. The set where the coordinates sum to at most 1 is a different simplex and does include the origin. A line through two points is not this cut.",
            )),
            ("rn-important-subsets-r2-q1", fresh(
                2, "sym",
                r"a, b, c, and d are positive. Write the sum of the two coordinates of the midpoint of (a, b) and (c, d). Use a, b, c, and d.",
                "(a+b+c+d)/2",
                {"a": (0.25, 18), "b": (0.25, 18), "c": (0.25, 18), "d": (0.25, 18)},
                r"The midpoint uses the parameter 1/2, so its coordinates are (a+c)/2 and (b+d)/2. Those two averages sum to (a+b+c+d)/2. The sum of the four endpoint coordinates, without the 1/2, is twice the midpoint sum. Half of one endpoint is not the midpoint. The parameter 1/2 itself is not a coordinate sum.",
                alternates=["(a+c+b+d)/2", "(a+b+c+d)*2**(-1)", "(1/2)*(a+b+c+d)"],
            )),
            ("rn-important-subsets-r3-q2", fresh(
                3, "find_error",
                r"A worked solution describes the linear map given by a matrix with 2 rows and 3 columns. Exactly one step is wrong.",
                [
                    r"A matrix with 2 rows and 3 columns belongs to \(\mathbb{R}^{2 \times 3}\).",
                    r"Left-multiplication by that matrix sends a column vector to another column vector.",
                    r"The column vector has one entry per column of the matrix, so the domain is \(\mathbb{R}^3\).",
                    r"The matrix maps \(\mathbb{R}^2\) into \(\mathbb{R}^3\), because the smaller dimension is always the domain.",
                ],
                3,
                r"Columns are the domain dimension and rows are the codomain dimension. A 2 by 3 matrix sends a 3-vector to a 2-vector. The smaller count is not automatically the domain. A 3 by 2 matrix is the swapped map. The set of all 2 by 3 matrices is not itself the domain.",
                reasons=[
                    r"Rows give the codomain and columns give the domain, so a 2 by 3 matrix maps \(\mathbb{R}^3\) into \(\mathbb{R}^2\).",
                    r"The smaller dimension is the domain, so a 2 by 3 matrix maps \(\mathbb{R}^2\) into \(\mathbb{R}^3\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "singular-value-decomposition":
        return [
            ("singular-value-decomposition-r1-q1", fresh(
                1, "order",
                r"Order the action of a square factorization \(A = U \Sigma V^T\), with \(U\) and \(V\) real orthogonal and \(\Sigma\) diagonal. Each step after the first uses the result of the step before it.",
                [
                    r"Start with a vector x in the domain of the square matrix A, so x has one entry for each column of A.",
                    r"Multiply the vector from the previous step by \(V^T\). Because V is orthogonal, this writes x in the right singular basis and does not change its Euclidean length.",
                    r"Multiply the coordinate vector from the previous step by the diagonal matrix \(\Sigma\). The i-th coordinate is multiplied by the i-th diagonal entry of \(\Sigma\). That diagonal entry is a singular value, and every singular value is nonnegative.",
                    r"Multiply the scaled vector from the previous step by the orthogonal matrix U. The product is A x. The origin stays at the origin, because each of the three factors is linear.",
                ],
                r"The factorization applies \(V^T\), then the nonnegative diagonal stretch \(\Sigma\), then U. The product is A x, and there is no translation. \(U \Sigma U^T\) is a spectral factorization and needs a symmetric matrix. Adding the three factors is not the factorization. Dropping \(\Sigma\) would preserve every Euclidean length.",
            )),
            ("singular-value-decomposition-r1-q3", fresh(
                1, "sym",
                r"a and b are positive. A diagonal matrix has diagonal entries a and b. Write the sum of the squares of its singular values. Use a and b.",
                "a**2 + b**2",
                {"a": (0.25, 18), "b": (0.25, 18)},
                r"The singular values of a diagonal matrix are the absolute values of its diagonal entries. Both entries are positive, so the singular values are a and b and the sum of their squares is a**2 + b**2. That sum is also the squared Frobenius norm. The square of the sum, (a+b)**2, adds the cross term 2*a*b. The product a*b is not a sum of squares. A negative diagonal entry would still contribute its square, but both entries here are positive.",
                alternates=["a*a + b*b", "b**2 + a**2", "(a**2)+(b**2)"],
            )),
            ("singular-value-decomposition-r3-q1", fresh(
                3, "find_error",
                r"A worked solution states general rules about the singular values of a real matrix. Exactly one rule is false.",
                [
                    r"The singular values are the square roots of the eigenvalues of \(A^T A\), so every singular value is nonnegative.",
                    r"Each zero singular value has a right singular vector in the kernel of A.",
                    r"The rank equals the number of nonzero singular values, counting multiplicity.",
                    r"The rank of every real matrix equals the product of its singular values.",
                ],
                3,
                r"The rank counts the positive singular values. The product of the singular values is zero whenever the rank is deficient, and it is not the rank when every singular value is positive either: singular values 2 and 3 have product 6 and rank 2. A zero row makes the rank smaller than the row count. The product of the eigenvalues of A is the determinant, which can be negative, and it is not this count.",
                reasons=[
                    r"Rank counts nonzero singular values. The product of those singular values is a different number, and it is zero whenever the matrix is rank deficient.",
                    r"The product of the singular values equals the rank of every real matrix.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "rayleigh-quotient":
        return [
            ("rayleigh-quotient-r1-q1", fresh(
                1, "order",
                r"Order why the Rayleigh quotient of a real symmetric matrix lies between its smallest and largest eigenvalues. Each step after the first uses the result of the step before it.",
                [
                    r"A real symmetric matrix has an orthonormal basis of eigenvectors and real eigenvalues. Let \(\lambda_{\max}\) denote the largest eigenvalue.",
                    r"Expand a nonzero vector x in the basis from the previous step. The squared coefficients are nonnegative and sum to \(x^T x\).",
                    r"Using those squared coefficients, \(x^T A x\) equals the sum of each eigenvalue times its squared coefficient. Dividing by \(x^T x\) makes the Rayleigh quotient a weighted average of the eigenvalues.",
                    r"The weighted average from the previous step equals \(\lambda_{\max}\) exactly when every positive weight sits on \(\lambda_{\max}\), so x is an eigenvector for \(\lambda_{\max}\). The zero vector is excluded, because that division is by \(x^T x\).",
                ],
                r"In an orthonormal eigenbasis the Rayleigh quotient is a weighted average of the real eigenvalues, so it lies between the extreme eigenvalues and equals the largest one only on that eigenspace. It is not strictly larger than every eigenvalue. Scaling x cancels in the fraction. The trace is the sum of the eigenvalues, and the determinant is their product. Neither one is this weighted average at a generic vector.",
            )),
            ("rayleigh-quotient-r1-q3", fresh(
                1, "sym",
                r"Let A be real symmetric, with diagonal entries a and b and with both off-diagonal entries equal to c. a, b, and c are positive. Write the Rayleigh quotient of the vector (1, 1). Use a, b, and c.",
                "(a+2*c+b)/2",
                {"a": (0.25, 18), "b": (0.25, 18), "c": (0.25, 18)},
                r"The quadratic form of (1, 1) is a + 2*c + b, and the squared length of (1, 1) is 2, so the quotient is (a+2*c+b)/2. The cross term is 2*c because each off-diagonal entry contributes once. a+b drops the off-diagonal entries. a+c+b counts only one of them. (a+2*c+b) without the division by 2 is the quadratic form, not the quotient. The product a*b*c is not this value.",
                alternates=["(a+b+2*c)/2", "(a+2*c+b)*2**(-1)", "(1/2)*(a+b+2*c)"],
            )),
            ("rayleigh-quotient-r2-q2", fresh(
                2, "find_error",
                r"A worked solution records general facts about a real symmetric matrix and its Rayleigh quotient. Exactly one step is wrong.",
                [
                    r"The eigenvalues are real, and the trace equals their sum.",
                    r"The determinant equals the product of the eigenvalues.",
                    r"For every nonzero vector, the Rayleigh quotient is at least the smallest eigenvalue and at most the largest eigenvalue.",
                    r"The Rayleigh quotient of every nonzero vector is strictly larger than every eigenvalue.",
                ],
                3,
                r"The quotient is a weighted average of the eigenvalues, so it cannot be strictly larger than the largest one. It equals that largest eigenvalue at a matching eigenvector. The trace is the sum of the eigenvalues, and the determinant is their product. The zero vector is excluded because the quotient divides by \(x^T x\). A 1 by 1 matrix already fails the strict claim, because the quotient equals its only eigenvalue.",
                reasons=[
                    r"The quotient is a weighted average of the eigenvalues, so it is at most the largest eigenvalue and is not strictly larger than every eigenvalue.",
                    r"The quotient is always strictly larger than every eigenvalue, because the denominator \(x^T x\) is positive.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "inner-products":
        return [
            ("inner-products-r1-q1", fresh(
                1, "order",
                r"Order how the axioms of a real inner product produce the norm and the cosine. Each step after the first uses the result of the step before it.",
                [
                    r"On a real vector space, an inner product is symmetric, linear in its first argument, and strictly positive on every nonzero vector.",
                    r"Swap arguments with the symmetry from the previous step, apply first-argument linearity, and swap back. The second argument is linear as well.",
                    r"Use the second-argument linearity from the previous step: the inner product of x with 2x equals 2 times the inner product of x with itself. Call the inner product of x with itself the squared norm. Positivity from the first step makes that square positive for every nonzero x, so its nonnegative square root, the norm, is positive too.",
                    r"Divide the inner product of two nonzero vectors by the product of their norms from the previous step. The quotient is the cosine of the angle between them, and the quotient is zero exactly when the vectors are orthogonal.",
                ],
                r"A real inner product is symmetric and linear in each argument, and positive on nonzero vectors. The induced norm is the nonnegative square root of the self inner product. The cosine divides the inner product by the product of the norms, and that cosine is zero exactly for orthogonal nonzero vectors. Equal lengths are a different condition. Skew-symmetry would force every self inner product to be zero.",
            )),
            ("inner-products-r1-q3", fresh(
                1, "multi",
                r"Which statements about real inner products are true? Select every correct statement.",
                [
                    r"Two nonzero vectors are orthogonal exactly when their inner product is zero.",
                    r"On \(\mathbb{R}^2\), the pairing \(x_1 y_1 - x_2 y_2\) is negative when both vectors are (0, 1), so that pairing is not an inner product.",
                    r"For two nonzero vectors, the cosine of the angle between them equals their inner product divided by the product of their norms.",
                    r"A real inner product is skew-symmetric, so the inner product of every vector with itself is zero.",
                ],
                [0, 1, 2],
                r"Orthogonality of nonzero vectors is a zero inner product. The pairing \(x_1 y_1 - x_2 y_2\) gives \(-1\) on (0, 1) with itself, so it fails positivity. The cosine divides the inner product by the product of the norms. A real inner product is symmetric, not skew-symmetric, and the self inner product is zero only for the zero vector. Equal lengths are not the definition of orthogonality.",
            )),
            ("inner-products-r2-q2", fresh(
                2, "sym",
                r"a, b, c, and d are positive. Write the dot product of the vectors (a, b) and (c, d). Use a, b, c, and d.",
                "a*c + b*d",
                {"a": (0.25, 18), "b": (0.25, 18), "c": (0.25, 18), "d": (0.25, 18)},
                r"The dot product multiplies matching coordinates and adds: a*c + b*d. a*b + c*d pairs coordinates from the same vector. a*c*b*d multiplies all four numbers instead of adding the two products. a+c+b+d adds the coordinates and is not an inner product. The product of the two Euclidean lengths is the Cauchy-Schwarz upper bound, not the inner product.",
                alternates=["c*a + d*b", "a*c + d*b", "b*d + a*c"],
            )),
        ]
    if sid == "vector-norms-lp":
        return [
            ("vector-norms-lp-r1-q1", fresh(
                1, "order",
                r"Order the comparison of the 1-norm, the 2-norm, and the infinity-norm of one vector. Each step after the first uses the result of the step before it.",
                [
                    r"Replace each coordinate of a vector x by its absolute value. A negative coordinate changes sign. A positive coordinate stays positive. Zero stays zero.",
                    r"Add the absolute values from the previous step. That sum is the 1-norm of x.",
                    r"The largest of the absolute values from the first step is the infinity-norm. It is at most the sum from the previous step, because every term in that sum is nonnegative.",
                    r"Take the square root of the sum of the squares of the absolute values from the first step. That square root is the 2-norm. It is at least the infinity-norm named in the previous step, and it is at most the 1-norm from the second step.",
                ],
                r"The 1-norm adds absolute coordinates, the infinity-norm keeps the largest absolute coordinate, and the 2-norm is the Euclidean length. For every real vector the infinity-norm is at most the 2-norm, and the 2-norm is at most the 1-norm. Equality of the triangle inequality for every pair is not a norm axiom. A negative scalar comes out of a norm as its absolute value.",
            )),
            ("vector-norms-lp-r1-q3", fresh(
                1, "find_error",
                r"A worked solution describes the closed unit balls in the plane. Exactly one step is wrong.",
                [
                    r"The set of vectors with 1-norm at most 1 is the diamond whose vertices are the four unit points on the two axes.",
                    r"The set of vectors with 2-norm at most 1 is the disk of radius 1 centered at the origin.",
                    r"The set of vectors with infinity-norm at most 1 is the square with sides parallel to the axes, running from \(-1\) to \(1\) in each coordinate.",
                    r"Those three sets are the same square, because equivalence of norms on a finite-dimensional space forces their unit balls to coincide.",
                ],
                3,
                r"The plane unit balls are a diamond, a disk, and an axis-aligned square. Equivalence means each norm is at most a constant times the other, and those constants may depend on the dimension. It does not make the balls the same set. On (1, 1) the 1-norm is 2 and the infinity-norm is 1. A hyperbola is unbounded, so it is not a unit ball.",
                reasons=[
                    r"Equivalence supplies constants relating the norms. The three unit balls have different shapes, so they are not the same square.",
                    r"Equivalence of norms means the unit balls are identical, so the diamond, the disk, and the square are the same set.",
                ],
                correct_reason=0,
            )),
            ("vector-norms-lp-r2-q2", fresh(
                2, "sym",
                r"a and b are positive. Write the 1-norm of the vector (a, -b). Use a and b.",
                "a+b",
                {"a": (0.25, 18), "b": (0.25, 18)},
                r"The 1-norm adds the absolute coordinates. The coordinates are a and -b, both of whose absolute values are the positive numbers a and b, so the 1-norm is a+b. a-b subtracts and can be smaller than either absolute value. a*b is a product, and it is not a norm of this vector. The larger of a and b is the infinity-norm, not the 1-norm. The Euclidean length is the square root of a**2 + b**2.",
                alternates=["b+a", "(a)+(b)"],
            )),
        ]
    if sid == "cauchy-schwarz-inequality":
        return [
            ("cauchy-schwarz-inequality-r1-q1", fresh(
                1, "sym",
                r"a and b are positive. Write the absolute value of the inner product of the vector (a, b) with itself. Use a and b.",
                "a**2 + b**2",
                {"a": (0.25, 18), "b": (0.25, 18)},
                r"The inner product of (a, b) with itself is a*a + b*b, which is nonnegative, so the absolute value is a**2 + b**2. That is also the square of the Euclidean length. The product a*b is one term of the expansion of (a+b)**2, not the self inner product. a+b adds the coordinates. The Cauchy-Schwarz bound for this pair equals the same a**2 + b**2, because the two vectors are identical, but the question asks for the absolute inner product.",
                alternates=["a*a + b*b", "b**2 + a**2", "(a**2)+(b**2)"],
            )),
            ("cauchy-schwarz-inequality-r1-q3", fresh(
                1, "find_error",
                r"A worked solution applies Cauchy-Schwarz in a real inner product space. Exactly one step is wrong.",
                [
                    r"The absolute inner product of any two vectors is at most the product of their norms.",
                    r"For nonzero vectors, equality holds exactly when one vector is a scalar multiple of the other.",
                    r"Expanding the squared norm of x+y produces the squared norm of x, plus the squared norm of y, plus twice the inner product, and that cross term is at most twice the product of the norms.",
                    r"Therefore the norm of x+y equals the product of the norms of x and of y, for every pair of vectors.",
                ],
                3,
                r"The cross term is at most twice the product of the norms, and that estimate produces the triangle inequality: the norm of a sum is at most the sum of the norms. It does not produce equality with the product of the norms. Equality in Cauchy-Schwarz, for nonzero vectors, holds exactly when one vector is a scalar multiple of the other, not when the vectors are orthogonal. Orthogonal nonzero vectors have inner product 0, which is strictly below the positive product of the lengths.",
                reasons=[
                    r"The expansion and the bound on the cross term give the triangle inequality. The norm of a sum is not equal to the product of the norms for every pair.",
                    r"Cauchy-Schwarz upgrades the cross term to a product, so the norm of every sum equals the product of the norms.",
                ],
                correct_reason=0,
            )),
            ("cauchy-schwarz-inequality-r2-q2", fresh(
                2, "order",
                r"Order a proof of Cauchy-Schwarz for a real inner product, with y nonzero. Each step after the first uses the result of the step before it.",
                [
                    r"For every real scalar t, the squared length q(t) of x + t y is at least zero.",
                    r"Expand the square from the previous step: q(t) equals the squared norm of y, times t squared, plus 2 t times the inner product of x and y, plus the squared norm of x.",
                    r"The expansion from the previous step has leading coefficient equal to the squared norm of y. That coefficient is positive because y is nonzero, so q is a quadratic, and a quadratic that stays nonnegative for every t has discriminant at most zero.",
                    r"The discriminant of the quadratic from the previous step is 4 times the square of the inner product, minus 4 times the product of the squared norms. That discriminant is at most zero, which is Cauchy-Schwarz. Equality holds if and only if the quadratic touches zero, which happens if and only if x is a scalar multiple of y.",
                ],
                r"A square length never goes negative, so the quadratic in t has a nonpositive discriminant. That discriminant condition is Cauchy-Schwarz. Equality holds precisely when the quadratic touches zero, hence when x is a scalar multiple of the nonzero vector y. Orthogonal nonzero vectors have inner product 0 and a positive product of lengths, so equality fails for them. The polynomial is quadratic, not cubic, once y is nonzero.",
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def apply_skill(sid):
    path = os.path.join(BANK_DIR, sid + ".json")
    with open(path, encoding="utf-8") as f:
        bank = json.load(f)
    live = {q["id"]: i for i, q in enumerate(bank["questions"])}
    retired = list(bank.get("retired_questions") or [])
    changed = False
    for old_id, new in swaps_for(sid):
        if old_id not in live:
            continue
        idx = live[old_id]
        old = bank["questions"][idx]
        if old.get("type") != "mc":
            raise SystemExit(old_id + " is no longer multiple choice")
        rnd = old["round"]
        used = []
        for q in bank["questions"]:
            if q.get("round") == rnd:
                used.append(qnum(q["id"]))
        for q in retired:
            if q.get("round") == rnd:
                used.append(qnum(q["id"]))
        number = max(used) + 1
        new = dict(new)
        new["id"] = f"{sid}-r{rnd}-q{number}"
        new["round"] = rnd
        new["version"] = 1
        if not isinstance(old.get("version"), int):
            old["version"] = 1
        retired.append(old)
        bank["questions"][idx] = new
        live[new["id"]] = idx
        del live[old_id]
        changed = True
    if not changed:
        print(sid, "already swapped")
        return
    bank["retired_questions"] = retired
    bank["version"] = int(bank.get("version") or 1) + 1
    seen = []
    for q in bank["questions"] + retired:
        if q["id"] in seen:
            raise SystemExit(sid + " duplicate id " + q["id"])
        seen.append(q["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)
        f.write("\n")
    deep = sum(1 for q in bank["questions"] if q["type"] in ("symbolic", "order", "error", "multi"))
    figs = sum(1 for q in bank["questions"] if q.get("figure"))
    print(f"{sid} version {bank['version']}: {deep}/{len(bank['questions'])} deep, {figs} figures, retired {len(retired)}")


def drop_grandfather():
    with open(GRAND, encoding="utf-8") as f:
        data = json.load(f)
    before = len(data["skills"])
    if len(data["skills"]) != len(set(data["skills"])):
        raise SystemExit("grandfather already has duplicate ids")
    drop = set(SKILLS)
    missing = sorted(drop - set(data["skills"]))
    if missing:
        raise SystemExit("not on the grandfather list: " + ", ".join(missing))
    data["skills"] = [sid for sid in data["skills"] if sid not in drop]
    if len(data["skills"]) != len(set(data["skills"])):
        raise SystemExit("grandfather gained a duplicate")
    added = set(data["skills"]) - set(json.load(open(GRAND, encoding="utf-8"))["skills"])
    if added:
        raise SystemExit("grandfather gained ids: " + ", ".join(sorted(added)))
    with open(GRAND, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("grandfather", before, "->", len(data["skills"]))


def main():
    for sid in SKILLS:
        apply_skill(sid)
    drop_grandfather()


if __name__ == "__main__":
    main()
