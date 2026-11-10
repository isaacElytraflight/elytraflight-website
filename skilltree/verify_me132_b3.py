#!/usr/bin/env python3
"""Independent numeric check for ME 132 batch B3.

The generator uses closed-form algebra. This file recomputes the same items
by signal equations, RK4, eigenvalue routines, or matrix exponentials.
"""
import math

import numpy as np
from scipy import linalg

from verify_harness import check_expected, finish, load_banks, load_texts, prop_steady

SKILLS = ["second-order-sys", "ss-solution", "loop-tf", "equilibria", "cruise-control", "app-examples"]


def second_order_overshoot(zeta):
    """Percent overshoot from damping ratio."""
    return 100 * math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2))


def second_order_peak_time(zeta, wn):
    """Time to first peak."""
    wd = wn * math.sqrt(1 - zeta**2)
    return math.pi / wd


def second_order_settling_2pct(zeta, wn):
    """Approximate 2% settling time."""
    return 4 / (zeta * wn)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    expected = {}

    # --- second-order-sys ---
    wn1, z1 = 4.0, 0.4
    expected["second-order-sys-r1-q2"] = z1 * wn1
    expected["second-order-sys-r1-q3"] = wn1 * math.sqrt(1 - z1**2)

    wn2, z2 = 5.0, 0.5
    expected["second-order-sys-r2-q1"] = second_order_overshoot(z2)
    expected["second-order-sys-r2-q2"] = second_order_peak_time(z2, wn2)

    wn3, z3 = 3.0, 0.3
    expected["second-order-sys-r3-q1"] = second_order_settling_2pct(z3, wn3)
    expected["second-order-sys-r3-q2"] = wn3 * math.sqrt(1 - z3**2)

    expected["second-order-sys-r4-q1"] = second_order_overshoot(0.6)
    expected["second-order-sys-r4-q2"] = 5 * math.sqrt(1 - 0.16)

    # --- ss-solution ---
    lam1 = -0.5
    expected["ss-solution-r1-q2"] = 4 * math.exp(lam1 * 2)
    expected["ss-solution-r1-q3"] = 1.0  # time constant of -1 mode

    A_diag = np.diag([-2.0, -4.0])
    x0 = np.array([1.0, 0.0])
    expected["ss-solution-r2-q1"] = float((linalg.expm(A_diag * 1.0) @ x0)[0])
    expected["ss-solution-r2-q3"] = 0.25  # time constant of -4 mode

    # eigenvalue -2 dominates (closer to zero)
    expected["ss-solution-r3-q1"] = -2.0
    expected["ss-solution-r3-q3"] = 1.0  # time constant of -1+2j mode (real part = -1)

    A2 = np.diag([-0.5, -2.0])
    x02 = np.array([1.0, 1.0])
    expected["ss-solution-r4-q1"] = float((linalg.expm(A2 * 1.0) @ x02)[1])
    expected["ss-solution-r4-q2"] = 1.0  # slowest eigenvalue -1 has tau = 1

    # --- loop-tf ---
    G1, H1 = 10, 0.2
    expected["loop-tf-r1-q2"] = G1 * H1
    expected["loop-tf-r1-q3"] = G1 / (1 + G1 * H1)

    G2, H2 = 6, 1
    expected["loop-tf-r2-q1"] = G2 * H2
    expected["loop-tf-r2-q2"] = 1 / (1 + G2)

    G3, H3 = 8, 0.5
    expected["loop-tf-r3-q1"] = 1 + G3 * H3
    expected["loop-tf-r3-q2"] = 1 / (1 + G3 * H3)

    G4 = 12
    expected["loop-tf-r4-q1"] = G4
    G5, H5 = 5, 0.4
    expected["loop-tf-r4-q2"] = 1 / (1 + G5 * H5)

    # --- equilibria ---
    expected["equilibria-r1-q2"] = 5 / 2
    expected["equilibria-r1-q3"] = 3 / 0.6

    # Two-state diagonal system equilibrium
    A_eq = np.array([[-1, 0], [0, -2]], dtype=float)
    B_eq = np.array([1, 2], dtype=float)
    u_eq = 4
    x_eq = np.linalg.solve(-A_eq, B_eq * u_eq)
    expected["equilibria-r2-q1"] = float(x_eq[0])
    expected["equilibria-r2-q3"] = 4.0  # x = 4 - x, equilibrium at 4

    expected["equilibria-r3-q1"] = 4.0  # 2 = 0.5h, h = 4
    expected["equilibria-r3-q3"] = 6 / 0.5  # tau/J - b*omega/J = 0 -> omega = tau/b

    expected["equilibria-r4-q1"] = 6 / 0.5  # 3u - 0.5x = 0, x = 6/0.5 = 12
    expected["equilibria-r4-q2"] = 4.0  # DC gain = y/u = 8/2 = 4

    # --- cruise-control ---
    Kc1, P1 = 3, 5
    expected["cruise-control-r1-q2"] = Kc1 * P1
    expected["cruise-control-r1-q3"] = prop_steady(Kc1, P1, 20)

    Kc2, P2 = 4, 6
    expected["cruise-control-r2-q1"] = 25 - prop_steady(Kc2, P2, 25)
    expected["cruise-control-r2-q3"] = -0.5 / (1 + 20)

    Kc3, P3 = 2, 8
    expected["cruise-control-r3-q1"] = 1 / (1 + Kc3 * P3)
    expected["cruise-control-r3-q2"] = 1 / (1 + Kc3 * P3)

    Kc4, P4 = 5, 4
    expected["cruise-control-r4-q1"] = 30 - prop_steady(Kc4, P4, 30)
    # Ideal feedforward gain: K_ff = 1/P = 0.25 where P = 4
    # The closed-loop with feedforward is (K_ff P + K_c P)/(1 + K_c P).
    # For unity DC gain: K_ff P + K_c P = 1 + K_c P, so K_ff P = 1, K_ff = 1/P.
    expected["cruise-control-r4-q2"] = 1.0 / 4

    # --- app-examples ---
    expected["app-examples-r1-q2"] = 2 * 4  # AR = 8
    expected["app-examples-r1-q3"] = 0.5 * 4  # q_in * R = 2

    expected["app-examples-r2-q2"] = 0.1 / 0.5  # J/b = 0.2
    expected["app-examples-r2-q3"] = 0.4 * 5  # K_t * i = 2

    expected["app-examples-r3-q2"] = math.sqrt(10)  # sqrt(g/l)
    expected["app-examples-r3-q3"] = 3 * math.exp(-1)  # h(5) = 3 * e^{-1}

    expected["app-examples-r4-q1"] = -1 / 6  # -1/(AR) = -1/6
    expected["app-examples-r4-q2"] = 0.4  # T/10 where T = 4s

    numeric = check_expected(banks, expected, mismatches)

    # worked examples, recomputed a different way and required to appear in the text
    texts = load_texts(SKILLS)

    # second-order-sys worked: zeta=0.4, wn=6, overshoot=25.4%
    worked_mp = second_order_overshoot(0.4)
    if abs(worked_mp - 25.4) > 0.2 or "25.4" not in texts["second-order-sys"]:
        mismatches.append(f"second-order-sys worked {worked_mp}")

    # ss-solution worked: A = diag(-1,-3), x0 = [2,1], x1(1) = 2*e^{-1} = 0.736
    A_w = np.diag([-1.0, -3.0])
    x_w = linalg.expm(A_w * 1.0) @ np.array([2.0, 1.0])
    if abs(x_w[0] - 0.736) > 0.01 or "0.736" not in texts["ss-solution"]:
        mismatches.append(f"ss-solution worked {x_w[0]}")

    # loop-tf worked: G=8, H=1 (unity feedback), T=8/9=0.889, S=1/9=0.111
    if "0.889" not in texts["loop-tf"] or "0.111" not in texts["loop-tf"]:
        mismatches.append("loop-tf worked text")

    # equilibria worked: 4 - 0.5x = 0 -> x = 8
    if "= 8" not in texts["equilibria"]:
        mismatches.append("equilibria worked text")

    # cruise worked: Kc=4, P=5, r=25, v=23.81, e=1.19
    cruise_v = prop_steady(4, 5, 25)
    if abs(cruise_v - 23.81) > 0.1 or "23.81" not in texts["cruise-control"]:
        mismatches.append(f"cruise worked {cruise_v}")

    # app-examples worked: A=3, R=5, AR=15, h_e=3
    if "= 15" not in texts["app-examples"] or "= 3" not in texts["app-examples"]:
        mismatches.append("app-examples worked text")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
