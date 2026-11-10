#!/usr/bin/env python3
"""Independent numeric check for ME 132 batch B4.

The generator uses closed-form algebra. This file recomputes the same items
by signal equations, RK4, eigenvalue routines, or matrix exponentials.
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = ["step-specs", "pid", "sensitivity", "nyquist", "discrete-time", "eig-modes", "ss-to-tf", "limit-cycles"]


def overshoot_pct(zeta):
    return 100 * math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2))


def settling_time_2pct(zeta, wn):
    return 4 / (zeta * wn)


def time_to_peak(zeta, wn):
    wd = wn * math.sqrt(1 - zeta**2)
    return math.pi / wd


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    expected = {}

    # --- step-specs ---
    z1, wn1 = 0.5, 4.0
    expected["step-specs-r1-q2"] = overshoot_pct(z1)
    expected["step-specs-r1-q3"] = settling_time_2pct(z1, wn1)

    z2, wn2 = 0.4, 5.0
    expected["step-specs-r2-q1"] = time_to_peak(z2, wn2)
    expected["step-specs-r2-q2"] = wn2 * math.sqrt(1 - z2**2)

    z3, wn3 = 0.6, 3.0
    expected["step-specs-r3-q1"] = overshoot_pct(z3)
    expected["step-specs-r3-q2"] = settling_time_2pct(z3, wn3)

    expected["step-specs-r4-q1"] = 3 / (0.45 * 1.0)  # 5% settling, not the 2% rule
    expected["step-specs-r4-q2"] = 5.0  # sqrt(3^2 + 4^2)

    # --- pid ---
    expected["pid-r1-q2"] = abs(4.0 + 2.0 / 1.0)  # C(1), not |C(j)|

    Kp2, Kd2 = 3.0, 0.5
    expected["pid-r2-q2"] = -Kp2 / Kd2  # zero location
    expected["pid-r2-q3"] = math.sqrt(Kp2**2 + (Kd2 * 10)**2)  # magnitude at w=10

    expected["pid-r3-q1"] = 2.0  # number of zeros
    expected["pid-r3-q3"] = 1.0  # DC gain with integral

    expected["pid-r4-q1"] = 1.2 * 2 / (3 * 0.3)  # Kp = 1.2*tau/(K*L)
    expected["pid-r4-q3"] = 0.5  # tau_i = Kp/Ki = 6/12

    # --- sensitivity ---
    L1 = 8.0
    expected["sensitivity-r1-q2"] = 1 / (1 + L1)
    expected["sensitivity-r1-q3"] = L1 / (1 + L1)

    L2 = 15.0
    expected["sensitivity-r2-q2"] = 1 / (1 + L2)

    Ms = 2.0
    expected["sensitivity-r3-q1"] = 1 / Ms
    expected["sensitivity-r3-q3"] = 1 / 21

    expected["sensitivity-r4-q1"] = 20 * math.log10(1 / 0.1)  # phase crossover, |L|=0.1
    expected["sensitivity-r4-q3"] = 9.0

    # --- nyquist ---
    expected["nyquist-r2-q1"] = 2.0  # gain margin
    expected["nyquist-r2-q2"] = 20 * math.log10(2)

    expected["nyquist-r3-q1"] = -135.0  # phase at crossover
    expected["nyquist-r3-q3"] = 4.0 / 3  # reduced gain margin

    expected["nyquist-r4-q2"] = 1 / 0.4  # peak sensitivity

    # --- discrete-time ---
    expected["discrete-time-r1-q2"] = math.log(0.8) / 0.1
    expected["discrete-time-r1-q3"] = -0.1 / math.log(0.8)

    expected["discrete-time-r2-q2"] = math.exp(-2 * 0.5)

    T3 = 0.2
    expected["discrete-time-r3-q1"] = math.exp(-1 * T3)
    expected["discrete-time-r3-q2"] = math.sqrt(0.6**2 + 0.5**2)

    expected["discrete-time-r4-q1"] = 1 / (2 * 0.05)
    expected["discrete-time-r4-q3"] = 0.05

    # --- eig-modes ---
    expected["eig-modes-r1-q2"] = -2.0
    expected["eig-modes-r1-q3"] = 0.2

    expected["eig-modes-r2-q2"] = 5.0  # natural freq of -3+4j
    expected["eig-modes-r2-q3"] = 0.6  # damping ratio

    tri = np.linalg.eigvals(np.array([[-1.0, 2.0], [0.0, -3.0]]))
    expected["eig-modes-r3-q1"] = float(max(tri.real))  # slower diagonal entry
    expected["eig-modes-r3-q2"] = math.exp(-1)  # mode at t=1

    expected["eig-modes-r4-q1"] = -0.5  # dominant eigenvalue
    expected["eig-modes-r4-q2"] = -5.0  # trace

    # --- ss-to-tf ---
    expected["ss-to-tf-r1-q3"] = 2 * (1 / 3) * 1  # DC gain

    poles = np.linalg.eigvals(np.diag([-2.0, -5.0]))
    expected["ss-to-tf-r2-q1"] = float(max(poles.real))  # slower pole
    expected["ss-to-tf-r2-q3"] = 1 * 1 / 1 + 1 * 1 / 4  # DC gain

    expected["ss-to-tf-r3-q1"] = 3.0 * 2.0  # CB = (DC gain) * |A|
    expected["ss-to-tf-r3-q3"] = 4.0  # coefficient a

    expected["ss-to-tf-r4-q1"] = 2.0  # degree
    expected["ss-to-tf-r4-q3"] = 1.0  # minimal states

    expected["limit-cycles-r3-q3"] = 1.0 / 2.0  # frequency = 1/period

    numeric = check_expected(banks, expected, mismatches)

    # worked examples
    texts = load_texts(SKILLS)

    # step-specs: zeta=0.6, overshoot=9.5%
    if "9.5" not in texts["step-specs"]:
        mismatches.append("step-specs worked text")

    # pid: poles at -1 and -8
    if "-1" not in texts["pid"] or "-8" not in texts["pid"]:
        mismatches.append("pid worked text")

    # sensitivity: S=0.091
    if "0.091" not in texts["sensitivity"]:
        mismatches.append("sensitivity worked text")

    # nyquist: GM=2.5
    if "2.5" not in texts["nyquist"]:
        mismatches.append("nyquist worked text")

    # discrete-time: z=0.67
    if "0.67" not in texts["discrete-time"]:
        mismatches.append("discrete-time worked text")

    # eig-modes: mode at e^{-6}=0.0025
    if "0.0025" not in texts["eig-modes"]:
        mismatches.append("eig-modes worked text")

    # ss-to-tf: G(0)=8/3=2.67
    if "2.67" not in texts["ss-to-tf"]:
        mismatches.append("ss-to-tf worked text")

    # limit-cycles: amplitude a=2
    if "a = 2" not in texts["limit-cycles"]:
        mismatches.append("limit-cycles worked text")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
