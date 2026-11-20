#!/usr/bin/env python3
"""SG-063 state space and realizations, and nonlinear equilibria.

Scope is me132/m6 and me132/m8 intersected with the grandfather list.
That intersection is exactly five banks: state-space-model, ss-solution,
ss-to-tf, realization, equilibria. impulse-conv, lin-algebra-review,
eigenvalues-diagonalization, eig-modes, local-linear-approximation,
linearization, fb-linearization, and gain-scheduling sit in those sections
and are not grandfathered. Nothing is added to the grandfather list.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and positive.
No key is a difference of two independent positives. Every denominator is one
declared variable, or a sum of declared variables, and is bounded away from
zero. Prompt names are the graded identifiers (b0, not b_0).
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "state-space-model",
    "ss-solution",
    "ss-to-tf",
    "realization",
    "equilibria",
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
    if sid == "state-space-model":
        return [
            ("state-space-model-r1-q1", fresh(
                1, "order",
                r"Order the state count for one scalar linear equation whose leading coefficient is nonzero. Each step after the first uses the result of the step before it.",
                [
                    r"Solve the equation so the highest derivative of y stands alone on the left, and call that derivative order n.",
                    r"List the initial values the equation from the previous step needs: y and every derivative of y of order strictly less than n. That list has n numbers.",
                    r"Assign one state to each number listed in the previous step. Fewer states would drop an initial value, and the equation does not need an extra state.",
                    r"The length of the state list from the previous step is the dimension of x. The entries of A are coefficients, so do not square that length and call the square a state count.",
                ],
                r"An nth-order scalar equation needs n initial values, so this state vector has n entries. One equation can still hide several derivatives. A and B are the coefficient matrices, not a count of states. The number of entries in A is n squared, which counts coefficients.",
            )),
            ("state-space-model-r2-q2", fresh(
                2, "sym",
                r"A scalar linear state model reads its output as C times the state x, plus D times the input u. Write that output. Use C, x, D, and u.",
                "C*x + D*u",
                {"C": (0.25, 18), "x": (0.25, 18), "D": (0.25, 18), "u": (0.25, 18)},
                r"The output equation is C*x + D*u. C*x drops the direct term. A*x + B*u is the state equation, not the output. Swapping the state and the output inverts the definition. D is the feedthrough, not a second copy of B.",
                alternates=["D*u + C*x", "(C*x)+(D*u)"],
            )),
            ("state-space-model-r3-q2", fresh(
                3, "find_error",
                r"A worked solution changes coordinates in a linear state model. T is a constant invertible matrix and x = T z. Exactly one step is wrong.",
                [
                    r"The new coordinate z is defined by x = T z, and T is a constant invertible matrix.",
                    r"Differentiating that definition and substituting \(\dot{x} = A x + B u\) produces the new state matrix \(T^{-1} A T\).",
                    r"\(T^{-1} A T\) is similar to A, so it has the same eigenvalues, with the same algebraic and geometric multiplicities.",
                    r"Those eigenvalues are replaced by the eigenvalues of T, because z is a different basis.",
                ],
                3,
                r"Similarity preserves the eigenvalues of A, including multiplicities. The eigenvalues of T are not the modes. The entries of A do change in general, and B is transformed as well. It is not forced to become the identity.",
                reasons=[
                    r"Similarity keeps the eigenvalues of A. The eigenvalues of T are not the modes of the model.",
                    r"The new state matrix equals T, so the modes move to the eigenvalues of T.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ss-solution":
        return [
            ("ss-solution-r1-q1", fresh(
                1, "order",
                r"Order the free response of \(\dot{x} = A x\) when A is diagonal, with diagonal entries \(\lambda_1\) and \(\lambda_2\). Each step after the first uses the result of the step before it.",
                [
                    r"Read \(\lambda_1\) and \(\lambda_2\) from the diagonal. The off-diagonal zeros mean neither state equation contains the other state.",
                    r"Exponentiate each diagonal entry from the previous step, times t, and place the two results on a diagonal. That matrix is \(e^{At}\).",
                    r"Multiply the matrix from the previous step by the initial state. Each entry of the product uses only the matching initial entry and its own exponential.",
                    r"Stop at the product from the previous step. That product is the free response. A nonzero input would add a convolution on top of it, and the convolution is not part of the free response.",
                ],
                r"The free response is \(e^{At} x(0)\). For a diagonal A the exponential is the diagonal of the scalar exponentials, and each mode stays in its own coordinate. A x(0) is one derivative, not the time evolution. x(0) + A t is a ramp. A single factor \(e^{-t}\) assumes both eigenvalues are \(-1\).",
            )),
            ("ss-solution-r2-q2", fresh(
                2, "sym",
                r"A real mode has eigenvalue -a, with a positive. Write its time constant, the time at which the mode has been multiplied by 1/e. Use a.",
                "1/a",
                {"a": (0.2, 20)},
                r"The mode is e to the power -a*t, which equals e to the power -1 when t = 1/a. The time constant is 1/a, not a and not -a. 1/a squared is the square of that time. The imaginary part of a complex eigenvalue sets the oscillation, not this decay time.",
                alternates=["a**(-1)", "1/(a)"],
            )),
            ("ss-solution-r3-q2", fresh(
                3, "find_error",
                r"A worked solution describes the free response when every eigenvalue of A has a negative real part. Exactly one step is wrong.",
                [
                    r"Every eigenvalue of A has a strictly negative real part.",
                    r"A mode is then a decaying exponential or a decaying oscillation, and a Jordan block only multiplies that factor by a power of t.",
                    r"Every such mode tends to the origin as t grows, so the free response tends to the origin from every initial state.",
                    r"The same eigenvalue hypothesis makes the response to a nonzero constant input grow without bound.",
                ],
                3,
                r"Negative real parts make every free mode decay, including a factor of a power of t from a Jordan block. A constant input then settles at the equilibrium \(-A^{-1} B u\). It does not grow. A positive real part is what makes a mode grow. A purely imaginary eigenvalue is what keeps a constant-amplitude oscillation.",
                reasons=[
                    r"Negative real parts make every free mode decay, and a constant input then settles at an equilibrium instead of growing.",
                    r"A nonzero constant input adds B u at every instant, so the state grows without bound under that hypothesis.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ss-to-tf":
        return [
            ("ss-to-tf-r1-q1", fresh(
                1, "sym",
                r"A scalar state model has state coefficient -p, input coefficient B, output coefficient C, and direct term 0. p, B, C, and the Laplace variable s are positive. Write G(s). Use C, B, p, and s.",
                "C*B/(s+p)",
                {"C": (0.2, 16), "B": (0.2, 16), "p": (0.2, 16), "s": (0.2, 16)},
                r"The scalar resolvent is 1/(s - (-p)) = 1/(s+p), and G(s) = C*B/(s+p) when the direct term is 0. C/(s+p) drops B. B/(s+p) drops C. C*B/(s-p) flips the sign in the denominator and moves the pole. A*B*C + s adds the matrices instead of forming the resolvent.",
                alternates=["B*C/(s+p)", "C*B/(p+s)", "(C*B)*(s+p)**(-1)"],
            )),
            ("ss-to-tf-r1-q2", fresh(
                1, "order",
                r"Order how the poles of a minimal single-input single-output realization are read from A. Each step after the first uses the result of the step before it.",
                [
                    r"Start from a minimal realization, so the degree of G equals the number of states and every eigenvalue of A is a pole of G.",
                    r"Build the matrix s I minus the A of the realization named in the previous step.",
                    r"Take the determinant of the matrix from the previous step. That determinant is the characteristic polynomial.",
                    r"The roots of the polynomial from the previous step are the poles of G. Minimality, from the first step, means none of those roots cancel.",
                ],
                r"For a minimal realization the poles are exactly the eigenvalues of A, which are the roots of det(s I - A). The diagonal entries are those eigenvalues only when A is already diagonal. det(B) and the eigenvalues of C are not the pole polynomial. A non-minimal realization can cancel a root, which is why the first step requires minimality.",
            )),
            ("ss-to-tf-r2-q2", fresh(
                2, "find_error",
                r"A worked solution describes a single-input single-output realization in which one factor cancels. Exactly one step is wrong.",
                [
                    r"The cancelled factor is an eigenvalue of A, and it is not a pole of G.",
                    r"That hidden eigenvalue is unreachable, unobservable, or both.",
                    r"The realization is not minimal, and the degree of G is strictly smaller than the number of states.",
                    r"A minimal realization can hide that same eigenvalue, because minimality only requires the input coefficient B to be nonzero.",
                ],
                3,
                r"A cancelled eigenvalue is absent from G, so the realization is not minimal and the degree of G is smaller than the state dimension. Minimality means every eigenvalue is a pole of G. A nonzero B can still leave a mode unreachable or unobservable. The hidden mode need not be the slowest one.",
                reasons=[
                    r"Minimality means every eigenvalue is a pole of G. A nonzero B can still leave a mode unreachable or unobservable.",
                    r"Minimality only needs a nonzero B, so a minimal realization may still cancel an unobservable mode.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "realization":
        return [
            ("realization-r1-q1", fresh(
                1, "order",
                r"Order a minimal realization of a proper single-input single-output rational transfer function. Each step after the first uses the result of the step before it.",
                [
                    r"Write the numerator and the denominator as polynomials in s.",
                    r"Cancel every common factor of the two polynomials from the previous step, and keep every factor that sits in only one of them.",
                    r"Read the degree of the denominator left by the previous step. A minimal realization uses exactly that many states.",
                    r"Build a controllable or observable companion whose dimension is the degree from the previous step. Do not put a cancelled factor back in as an extra state.",
                ],
                r"A minimal realization has one state per pole that remains after cancellation. Counting the written denominator before cancellation inflates the model. The inverse of G is a different system. Poles alone do not fix the zeros or the gain, so the companion still has to carry the numerator that survived the second step.",
            )),
            ("realization-r2-q2", fresh(
                2, "sym",
                r"A strictly proper transfer function has numerator constant term b0 and monic-denominator constant term a0. Both are positive. Write the DC gain. Use b0 and a0.",
                "b0/a0",
                {"b0": (0.25, 24), "a0": (0.25, 24)},
                r"At s = 0 every positive power of s drops out, so the DC gain is b0/a0. a0/b0 inverts the ratio. b0*a0 multiplies the two constant terms and is not a gain. b0 + a0 adds them. The ratio of the leading coefficients is the high-frequency coefficient, and it is zero for a strictly proper transfer function.",
                alternates=["b0*a0**(-1)", "(1/a0)*b0"],
            )),
            ("realization-r3-q1", fresh(
                3, "find_error",
                r"A worked solution compares observable canonical form with controllable canonical form of the same strictly proper G, after cancellation. Exactly one step is wrong.",
                [
                    r"Both forms realize that same G, so they have the same poles.",
                    r"In controllable form the denominator coefficients sit in the last row of A. In observable form those coefficients sit in a column.",
                    r"Zeros are allowed in both forms. Controllable form carries them in C, and observable form carries them in B.",
                    r"Observable form exists only when G has no zeros, because a zero would make that column singular.",
                ],
                3,
                r"The two companion forms are transposes, up to which vector carries the numerator. They realize the same G and have the same poles. Zeros move into C or into B. They do not delete observable form, and they do not make the companion column singular.",
                reasons=[
                    r"Both companion forms allow zeros. A zero changes C or B and does not remove observable form.",
                    r"A zero makes the observable companion singular, so only controllable form can realize a transfer function that has a zero.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "equilibria":
        return [
            ("equilibria-r1-q1", fresh(
                1, "sym",
                r"The scalar rate is a - b*x, with a and b positive and the input held constant. Write the equilibrium value of x. Use a and b.",
                "a/b",
                {"a": (0.25, 20), "b": (0.25, 20)},
                r"Set a - b*x equal to zero and solve. The resting value is a/b. b/a inverts the ratio. a*b multiplies the two coefficients. a - b is not the root, and it can be negative while the equilibrium of this rate stays positive. The origin is an equilibrium only when a is zero, which it is not.",
                alternates=["a*b**(-1)", "(1/b)*a"],
            )),
            ("equilibria-r2-q2", fresh(
                2, "order",
                r"Order the equilibrium of the linear model \(\dot{x} = A x + B u\) with a constant input, and then the stability test. Each step after the first uses the result of the step before it.",
                [
                    r"Hold u fixed. An equilibrium is a state at which the rate is zero, and that state need not be the origin.",
                    r"Set A x + B u equal to zero, using the constant input from the previous step, and solve for the state.",
                    r"When A is invertible, the solution of the previous step is the single state \(-A^{-1} B u\).",
                    r"When every eigenvalue of the A inverted in the previous step has a negative real part, the state converges to that single equilibrium from every initial state.",
                ],
                r"Negative real parts make every mode decay, so a linear model converges to \(-A^{-1} B u\) from every initial state. A positive real part makes a mode grow. A purely imaginary eigenvalue keeps an oscillation and is not this test. The equilibrium itself need not be the origin, and the input need not be zero.",
            )),
            ("equilibria-r3-q2", fresh(
                3, "multi",
                r"Which statements about equilibria are true? Select every correct statement.",
                [
                    r"With the input held constant, an equilibrium is any state at which the rate is zero. That state does not have to be the origin.",
                    r"The only real numbers x that satisfy x*(1 - x) = 0 are x = 0 and x = 1.",
                    r"If \(\dot{x} = A x + B u\) and every eigenvalue of A has a negative real part, a constant input makes the state converge to the equilibrium from every initial state.",
                    r"A linear model sustains an isolated limit cycle whenever A has a purely imaginary eigenvalue.",
                ],
                [0, 1, 2],
                r"The rate is zero at an equilibrium, and the resting state follows the input. x*(1 - x) = 0 only at 0 and 1. A linear model with every eigenvalue in the open left half-plane converges to its equilibrium from every initial state. A purely imaginary eigenvalue of a linear model gives a continuum of periodic orbits, not an isolated limit cycle. Isolated cycles need nonlinearity.",
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
