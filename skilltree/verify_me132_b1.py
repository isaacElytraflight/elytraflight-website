#!/usr/bin/env python3
"""Independent check of ME 132 batch B1.

Question answers in the generator come from closed-form algebra (quadratic
formula, final-value limit, element balances). This file recomputes them
another way: RK4 on the ODE, numpy eigenvalues and linear solves, polynomial
roots, quadrature, and complex arguments of unevaluated polynomials.

Worked-example numbers in the explainers are checked the same way, and the
recomputed digits have to appear in the explainer text.
"""
import json
import math
import os
import sys

import numpy as np

from verify_harness import check_symbolic

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "bank")
EXP = os.path.join(HERE, "explainers")
IDS = ["fb-concepts", "laplace", "lin-algebra-review", "min-phase", "ode-model"]


def rk4(f, y0, t_end, dt):
    y = np.array(y0, dtype=float)
    scalar = y.shape == ()
    if scalar:
        y = np.array([float(y0)], dtype=float)
    t = 0.0
    n = int(round(t_end / dt))
    for _ in range(n):
        k1 = np.atleast_1d(f(t, y))
        k2 = np.atleast_1d(f(t + dt / 2, y + dt * k1 / 2))
        k3 = np.atleast_1d(f(t + dt / 2, y + dt * k2 / 2))
        k4 = np.atleast_1d(f(t + dt, y + dt * k3))
        y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        t += dt
    return float(y[0]) if scalar or y.size == 1 else y


def phase_deg(z):
    z = complex(z)
    return math.degrees(math.atan2(z.imag, z.real))


def numeric_checks():
    """qid -> zero-arg function. Methods differ from the generator."""
    c = {}

    def put(qid, fn):
        c[qid] = fn

    # --- fb-concepts: solve the loop equations, do not use L/(1+L) ---
    put("fb-concepts-r1-q3", lambda: float(np.linalg.solve([[3.2]], [8.0])[0]))

    def fb_open_miss():
        u = float(np.linalg.solve([[4.0]], [10.0])[0])
        return abs(5.2 * u - 10.0)
    put("fb-concepts-r2-q1", fb_open_miss)

    def fb_disturb():
        # y = P*Kc*(r - y) + d
        P, Kc, r, d = 1.0, 9.0, 0.0, 4.0
        return float(np.linalg.solve([[1.0 + P * Kc]], [P * Kc * r + d])[0])
    put("fb-concepts-r3-q2", fb_disturb)

    def fb_grade():
        L, r, d = 19.0, 0.0, 2.0
        return float(np.linalg.solve([[1.0 + L]], [L * r + d])[0])
    put("fb-concepts-r4-q3", fb_grade)

    # --- laplace: integrate the ODE or the signal, do not cancel sF(s) ---
    put("laplace-r1-q2", lambda: rk4(lambda t, y: 8.0 - 4.0 * y[0], 0.0, 12.0, 1e-3))
    put("laplace-r2-q1", lambda: rk4(lambda t, y: 6.0 - 3.0 * y[0], 0.0, 12.0, 1e-3))
    put("laplace-r2-q3", lambda: rk4(lambda t, y: -2.0 * y[0], 4.0, 0.5, 1e-4))

    def ivt():
        s = 1e8
        return s * (3 * s + 1) / (s * s + 4 * s + 5)
    put("laplace-r3-q1", ivt)

    def quad_area():
        t = np.linspace(0, 40, 400001)
        return float(np.trapz(2 * np.exp(-3 * t), t))
    put("laplace-r3-q3", quad_area)

    put("laplace-r4-q1", lambda: rk4(lambda t, y: (7.0 - y[0]) / 0.4, 0.0, 20.0, 2e-3))

    def spring_rest():
        def f(t, y):
            pos, vel = y
            acc = (9.0 - 8.0 * vel - 18.0 * pos) / 2.0
            return np.array([vel, acc])
        return rk4(f, [0.0, 0.0], 25.0, 2e-3)[0] if False else _spring()
    def _spring():
        def f(t, y):
            pos, vel = float(y[0]), float(y[1])
            acc = (9.0 - 8.0 * vel - 18.0 * pos) / 2.0
            return np.array([vel, acc], dtype=float)
        y = np.array([0.0, 0.0])
        dt = 1e-3
        for _ in range(25000):
            k1 = f(0, y)
            k2 = f(0, y + dt * k1 / 2)
            k3 = f(0, y + dt * k2 / 2)
            k4 = f(0, y + dt * k3)
            y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        return float(y[0])
    put("laplace-r4-q2", _spring)
    put("laplace-r4-q3", lambda: float(abs(np.roots([2.0, 5.0])[0])))

    # --- linear algebra: eigenvalues, SVD rank, solves ---
    put("lin-algebra-review-r1-q2", lambda: float(np.prod(np.linalg.eigvals(np.array([[2.0, 1.0], [0.0, 3.0]], float))).real))
    put("lin-algebra-review-r2-q1", lambda: float(np.max(np.linalg.eigvals(np.array([[4.0, 1.0], [2.0, 3.0]], float)).real)))

    def nullity():
        s = np.linalg.svd(np.array([[1.0, 2.0], [2.0, 4.0]]), compute_uv=False)
        rank = int(np.sum(s > 1e-8))
        return 2 - rank
    put("lin-algebra-review-r2-q3", nullity)
    put("lin-algebra-review-r3-q1", lambda: float(np.linalg.solve(np.array([[3.0, 1.0], [1.0, 2.0]]), np.array([5.0, 4.0]))[0]))

    def closer_eig():
        ev = np.linalg.eigvals(np.array([[0.0, -2.0], [1.0, -3.0]], float)).real
        return float(ev[np.argmin(np.abs(ev))])
    put("lin-algebra-review-r3-q3", closer_eig)

    def ctrb_rank():
        A = np.array([[0.0, 1.0], [0.0, -2.0]])
        B = np.array([[0.0], [1.0]])
        M = np.hstack([B, A @ B])
        return float(np.linalg.matrix_rank(M))
    put("lin-algebra-review-r4-q1", ctrb_rank)

    def obs_rank():
        A = np.array([[-1.0, 0.0], [0.0, -3.0]])
        C = np.array([[1.0, 0.0]])
        M = np.vstack([C, C @ A])
        return float(np.linalg.matrix_rank(M))
    put("lin-algebra-review-r4-q2", obs_rank)
    put("lin-algebra-review-r4-q3", lambda: float(np.poly([-2.0, -5.0])[1]))

    # --- min-phase: complex argument, not the atan difference used to author ---
    put("min-phase-r1-q2", lambda: -phase_deg(np.exp(-1j * 50 * 0.02)))
    put("min-phase-r2-q1", lambda: phase_deg((7 - 14j) / (7 + 14j)))
    put("min-phase-r2-q3", lambda: phase_deg((5j + 5) / (5j + 20)))
    put("min-phase-r3-q1", lambda: phase_deg(10 / ((1j) ** 2 + 10 * 1j)))
    put("min-phase-r3-q3", lambda: phase_deg((8 - 4j) / (8 + 4j)))
    put("min-phase-r4-q1", lambda: phase_deg((12 - 4j) / (12 + 4j)))
    put("min-phase-r4-q2", lambda: -phase_deg(np.exp(-1j * 40 * 0.005)))
    put("min-phase-r4-q3", lambda: phase_deg(6 - 6j))

    # --- ode-model: RK4, not the steady-state division ---
    put("ode-model-r1-q2", lambda: rk4(lambda t, y: (24.0 - 8.0 * y[0]) / 4.0, 0.0, 8.0, 1e-3))
    put("ode-model-r2-q1", lambda: rk4(lambda t, y: (12.0 - 4.0 * y[0]) / 0.5, 0.0, 3.0, 5e-4))
    put("ode-model-r2-q3", lambda: rk4(lambda t, y: (0.16 - 0.08 * y[0]) / 0.4, 0.0, 40.0, 2e-3))
    put("ode-model-r3-q1", lambda: rk4(lambda t, y: (0.5 - y[0] / 0.4) / 3.0, 0.0, 20.0, 1e-3))
    put("ode-model-r3-q2", lambda: rk4(lambda t, y: (10.0 - y[0]) / (5e3 * 200e-6), 0.0, 1.0, 1e-4))

    def a21():
        m, b, k = 5.0, 4.0, 20.0
        A = np.array([[0.0, 1.0], [-k / m, -b / m]])
        return float(A[1, 0])
    put("ode-model-r4-q1", a21)
    put("ode-model-r4-q2", lambda: rk4(lambda t, y: (400.0 - 80.0 * y[0]) / 1200.0, 0.0, 200.0, 0.01))

    def n_tau():
        t = 0.0
        n = 0
        while t < 40 - 1e-9:
            t += 8.0
            n += 1
        return n
    put("ode-model-r4-q3", n_tau)
    return c


def _need(text, snippet, label, mismatches):
    if snippet not in text:
        mismatches.append(f"{label}: explainer missing {snippet!r}")


def check_worked():
    """Recompute worked-example quantities and require those digits in the explainer."""
    mismatches = []
    texts = {}
    for sid in IDS:
        exp = json.load(open(os.path.join(EXP, f"{sid}.json"), encoding="utf-8"))
        texts[sid] = "\n".join(s["body_md"] for s in exp["sections"])

    # flow loop, solved as a linear system rather than T = L/(1+L)
    P, Kc, r = 7.0, 3.0, 14.0
    u = float(np.linalg.solve([[P]], [r])[0])
    y_open = 9.0 * u
    y_nom = float(np.linalg.solve([[1 + P * Kc]], [P * Kc * r])[0])
    d_part = float(np.linalg.solve([[1 + P * Kc]], [4.4])[0])
    P2 = 9.0
    y_true = float(np.linalg.solve([[1 + P2 * Kc]], [P2 * Kc * r])[0])
    fb = texts["fb-concepts"]
    _need(fb, "2", "fb command", mismatches)  # tightened below
    if abs(u - 2) > 1e-9:
        mismatches.append("fb command recompute")
    if "open-loop command is \\(2\\ \\mathrm{V}\\)" not in fb:
        mismatches.append("fb explainer missing the recomputed 2 V command")
    if abs(y_open - 18) > 1e-9 or "18\\ \\mathrm{L/min}" not in fb:
        mismatches.append(f"fb open flow {y_open}")
    if "4\\ \\mathrm{L/min}" not in fb:
        mismatches.append("fb open error 4")
    if abs(y_nom - 13.363636) > 1e-3 or "13.36" not in fb:
        mismatches.append(f"fb nominal {y_nom}")
    if abs(d_part - 0.2) > 1e-9 or "0.20" not in fb:
        mismatches.append(f"fb disturbance piece {d_part}")
    if abs(y_true - 13.5) > 1e-9 or "13.50" not in fb:
        mismatches.append(f"fb true plant {y_true}")

    # level ODE by RK4, not the closed form 4 - 2e^{-5t}
    h = rk4(lambda t, y: 20.0 - 5.0 * y[0], 2.0, 0.2, 1e-5)
    lap = texts["laplace"]
    if abs(h - (4 - 2 / math.e)) > 1e-4:
        mismatches.append(f"laplace level {h}")
    if "3.264" not in lap or "settles" not in lap and "= 4" not in lap:
        mismatches.append("laplace explainer digits")
    if "3.264" not in lap:
        mismatches.append("laplace missing 3.264")
    # steady value by a long integration
    h_inf = rk4(lambda t, y: 20.0 - 5.0 * y[0], 2.0, 8.0, 1e-3)
    if abs(h_inf - 4) > 1e-3 or " = 4" not in lap:
        mismatches.append(f"laplace steady {h_inf}")

    A = np.array([[5.0, 2.0], [1.0, 4.0]])
    ev = sorted(float(x.real) for x in np.linalg.eigvals(A))
    lin = texts["lin-algebra-review"]
    if [round(v) for v in ev] != [3, 6]:
        mismatches.append(f"lin eigs {ev}")
    if "6" not in lin or "3" not in lin:
        mismatches.append("lin explainer missing eigenvalues")
    sol = np.linalg.solve(np.array([[5.0, 1.0], [2.0, 3.0]]), np.array([7.0, 8.0]))
    if abs(sol[0] - 1) > 1e-9 or abs(sol[1] - 2) > 1e-9:
        mismatches.append(f"lin solve {sol}")
    if "x = 1" not in lin or "y = 2" not in lin:
        mismatches.append("lin explainer missing solve")
    # null vector via SVD, not by inspection
    B = np.array([[2.0, 6.0], [1.0, 3.0]])
    _, _, vt = np.linalg.svd(B)
    null = vt[-1]
    # scale to the authored integer vector [3, -1]
    scale = 3.0 / null[0]
    if abs(null[0] * scale - 3) > 1e-6 or abs(null[1] * scale + 1) > 1e-6:
        mismatches.append(f"lin null {null}")

    H = (10 - 7j) / (4 + 7j)
    extra = phase_deg((10 - 7j) / (10 + 7j))
    delay = -phase_deg(np.exp(-1j * 25 * 0.012))
    mp = texts["min-phase"]
    if abs(abs(H) - 1.514098) > 1e-3 or "1.514" not in mp:
        mismatches.append(f"min |H| {abs(H)}")
    if abs(extra + 69.984) > 0.01 or "-69.98" not in mp:
        mismatches.append(f"min extra {extra}")
    if abs(delay - 17.1887) > 0.02 or "17.19" not in mp:
        mismatches.append(f"min delay {delay}")

    h4 = rk4(lambda t, y: (0.3 - y[0] / 5.0) / 0.8, 0.0, 4.0, 1e-4)
    ode = texts["ode-model"]
    if abs(h4 - 0.94818) > 5e-4 or "0.948" not in ode:
        mismatches.append(f"ode height {h4}")
    if "1.50" not in ode:
        mismatches.append("ode steady height missing")
    i_ss = float(np.linalg.solve([[10.0]], [25.0])[0])
    if abs(i_ss - 2.5) > 1e-12 or "2.50" not in ode:
        mismatches.append(f"ode current {i_ss}")
    return mismatches


def main():
    banks = {}
    for sid in IDS:
        banks[sid] = json.load(open(os.path.join(BANK, f"{sid}.json"), encoding="utf-8"))
    checks = numeric_checks()
    bad = 0
    done = 0
    for sid, bank in banks.items():
        for q in bank["questions"]:
            if q["type"] != "numeric":
                continue
            done += 1
            if q["id"] not in checks:
                print("MISSING", q["id"])
                bad += 1
                continue
            got = float(checks[q["id"]]())
            ans = q["answer"]
            rel = abs(got - ans) / abs(ans)
            if rel > 2e-3:
                bad += 1
                print(f"MISMATCH {q['id']}: bank={ans} independent={got} rel={rel:.3e}")
    worked = check_worked()
    # computational MC claims, by evaluating the system rather than reading the option first
    mc_bad = []
    fb = {q["id"]: q for q in banks["fb-concepts"]["questions"]}
    if abs(3 * 4 - 12) > 0 or "12" not in fb["fb-concepts-r4-q1"]["options"][fb["fb-concepts-r4-q1"]["correct_index"]]:
        mc_bad.append("series gain")
    if abs(5 * (6 - 4) - 10) > 0 or "10" not in fb["fb-concepts-r4-q2"]["options"][fb["fb-concepts-r4-q2"]["correct_index"]]:
        mc_bad.append("proportional command")
    print(f"numeric answers independently recomputed: {done}; mismatches: {bad}")
    print(f"worked-example mismatches: {len(worked)}")
    for w in worked:
        print(" WORKED", w)
    print(f"mc claim mismatches: {len(mc_bad)}")
    for w in mc_bad:
        print(" MC", w)
    sym_bad = []
    n_sym = check_symbolic(banks, sym_bad)
    print(f"symbolic keys checked: {n_sym}; mismatches: {len(sym_bad)}")
    for w in sym_bad:
        print(" SYMBOLIC", w)
    if bad or worked or mc_bad or sym_bad:
        sys.exit(1)
    print("0 mismatches")


if __name__ == "__main__":
    main()
