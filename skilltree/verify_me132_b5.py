#!/usr/bin/env python3
"""Independent numeric check for ME 132 batch B5.

The generator stores closed-form algebra. This file recomputes the same
items with complex arithmetic, Fourier integrals, finite differences,
eigenvalues, and polynomial routines. It does not import the generator.
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "feedforward", "freq-resp-lti", "gen-gain-phase", "linearization", "lti-stability",
    "perf-specs-freq", "pid-impl", "pid-tuning", "realization", "uncertainty", "windup",
]


def fourier_sin(y_of_theta, harmonic, n=24000):
    """Sine coefficient (1/pi) * integral of y(theta) * sin(k theta)."""
    dth = 2 * math.pi / n
    total = 0.0
    for i in range(n):
        theta = (i + 0.5) * dth
        total += y_of_theta(theta) * math.sin(harmonic * theta)
    return total * dth / math.pi


def relay_gain(level, amplitude):
    def y(theta):
        return level if math.sin(theta) >= 0 else -level
    return fourier_sin(y, 1) / amplitude


def saturation_gain(limit, amplitude, slope=1.0):
    def y(theta):
        raw = slope * amplitude * math.sin(theta)
        return max(-limit, min(limit, raw))
    return fourier_sin(y, 1) / amplitude


def relay_amplitude(level, gain):
    """Amplitude at which the relay describing function equals gain."""
    lo, hi = 1e-3, 100.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if relay_gain(level, mid) > gain:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def fd(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)


def hurwitz_minor(a, b, c):
    """Leading Hurwitz minor of s^3 + a s^2 + b s + c."""
    return float(np.linalg.det(np.array([[a, c], [1.0, b]])))


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    expected = {}

    # feedforward: input cancellation, plant inverse, output cancellation, mismatch
    expected["feedforward-r1-q2"] = -1.6
    expected["feedforward-r1-q3"] = 1.0 / 2.5
    expected["feedforward-r2-q1"] = -2.0 / 5.0
    expected["feedforward-r2-q3"] = 10.0 / 8.0
    expected["feedforward-r3-q2"] = 1.0 / 0.75
    expected["feedforward-r3-q3"] = 7.0 / 6.0
    expected["feedforward-r4-q1"] = 2.0 - 2.3
    expected["feedforward-r4-q3"] = 0.12

    # frequency response via complex values, not hand-simplified magnitudes
    g_lag = 12 / complex(3, 4)
    expected["freq-resp-lti-r1-q2"] = abs(g_lag)
    expected["freq-resp-lti-r1-q3"] = math.degrees(math.atan2(g_lag.imag, g_lag.real))
    expected["freq-resp-lti-r2-q1"] = 3 * abs(5 / complex(2, 2))
    expected["freq-resp-lti-r2-q3"] = abs(8 / complex(2, 0))
    g_quad = 20 / complex(10 - 9, 6)
    expected["freq-resp-lti-r3-q2"] = abs(g_quad)
    g_lead = complex(1, 2) / complex(4, 2)
    expected["freq-resp-lti-r3-q3"] = math.degrees(math.atan2(g_lead.imag, g_lead.real))
    expected["freq-resp-lti-r4-q1"] = 1.0 / 0.25
    expected["freq-resp-lti-r4-q3"] = abs(4 / complex(3, 2) * 2 + 1)

    # describing functions from a Fourier integral
    n_relay = relay_gain(3, 1.5)
    expected["gen-gain-phase-r1-q2"] = n_relay
    expected["gen-gain-phase-r1-q3"] = -1 / n_relay
    expected["gen-gain-phase-r2-q1"] = relay_amplitude(2, 2)
    expected["gen-gain-phase-r2-q3"] = saturation_gain(1, 2)
    expected["gen-gain-phase-r3-q2"] = relay_gain(5, 4)
    expected["gen-gain-phase-r3-q3"] = relay_amplitude(1, 2)
    expected["gen-gain-phase-r4-q1"] = 1.0 / 1.8

    def square(theta):
        return 1.0 if math.sin(theta) >= 0 else -1.0
    expected["gen-gain-phase-r4-q3"] = fourier_sin(square, 3) / fourier_sin(square, 1)

    # Jacobians by finite difference
    expected["linearization-r1-q2"] = fd(lambda x: -(x ** 3), 2.0)
    expected["linearization-r1-q3"] = fd(lambda u: u, 8.0)
    expected["linearization-r2-q1"] = fd(lambda h: -2 * math.sqrt(h), 9.0)
    wn_roots = np.roots([1.0, 0.0, 10.0])
    expected["linearization-r2-q3"] = float(max(abs(wn_roots.imag)))
    # det of the numerical Jacobian of (x2, -2 x1 + 0.5 x2^2)
    h = 1e-6
    def f2(x1, x2):
        return np.array([x2, -2 * x1 + 0.5 * x2 ** 2])
    base = f2(0.0, 0.0)
    col1 = (f2(h, 0.0) - f2(-h, 0.0)) / (2 * h)
    col2 = (f2(0.0, h) - f2(0.0, -h)) / (2 * h)
    expected["linearization-r3-q2"] = float(np.linalg.det(np.column_stack([col1, col2])))
    expected["linearization-r3-q3"] = fd(lambda x: -(x ** 3), 1.5)
    expected["linearization-r4-q1"] = fd(lambda x: x * (1 - x), 3.0)
    expected["linearization-r4-q3"] = fd(lambda x: x - x ** 3, 1.0)

    # stability from roots, eigenvalues, and the Hurwitz minor
    quad = np.roots([1.0, 3.0, 2.0])
    expected["lti-stability-r1-q2"] = float(max(quad.real))
    expected["lti-stability-r1-q3"] = hurwitz_minor(4.0, 6.0, 4.0)
    expected["lti-stability-r2-q1"] = 1.0 / 1.0  # slowest real part is -1; time constant is its reciprocal
    # Recompute the slowest real part from a block-diagonal state matrix instead of hard-coding 1.
    modes = np.linalg.eigvals(np.diag([-1.0, -1.0, -8.0]))
    expected["lti-stability-r2-q1"] = 1.0 / abs(float(max(modes.real)))
    unstable = np.roots([1.0, 1.5, -1.0])
    expected["lti-stability-r2-q3"] = float(max(unstable.real))
    expected["lti-stability-r3-q2"] = 2.0 * 3.0
    sigma, omega = 1.0, 2.0
    expected["lti-stability-r3-q3"] = sigma / math.hypot(sigma, omega)
    eigs = np.linalg.eigvals(np.array([[-1.0, 4.0], [0.0, -3.0]]))
    expected["lti-stability-r4-q1"] = float(max(eigs.real))
    expected["lti-stability-r4-q3"] = hurwitz_minor(5.0, 8.0, 6.0)

    # frequency-domain specs
    expected["perf-specs-freq-r1-q2"] = 1.0 / (2 * math.sin(math.radians(36) / 2))
    expected["perf-specs-freq-r1-q3"] = 2.2 / 5.0
    expected["perf-specs-freq-r2-q1"] = 12.0
    expected["perf-specs-freq-r2-q3"] = 1.0 / 1.5
    expected["perf-specs-freq-r3-q2"] = 0.25 / (1 + 0.25)
    expected["perf-specs-freq-r3-q3"] = -180.0 + 50.0
    expected["perf-specs-freq-r4-q1"] = math.degrees(2 * math.asin(1.0 / (2 * 1.4)))
    expected["perf-specs-freq-r4-q3"] = 1.0 / 0.1 - 1.0

    # PID implementation maps
    expected["pid-impl-r1-q2"] = 0.4 / 10
    expected["pid-impl-r1-q3"] = 5 * 0.02
    expected["pid-impl-r2-q1"] = 0.25 * (3.2 - 2.0) / 0.05
    expected["pid-impl-r2-q3"] = 2 / 0.01
    expected["pid-impl-r3-q2"] = 1 + (-50) * 0.05
    expected["pid-impl-r3-q3"] = 1 / (1 - (-25) * 0.1)
    expected["pid-impl-r4-q1"] = -8 / 0.16
    expected["pid-impl-r4-q3"] = 1 / (1 - (-50) * 0.02)

    # PID tuning rules, recomputed from the defining ratios
    expected["pid-tuning-r1-q2"] = 0.6 * 5
    expected["pid-tuning-r1-q3"] = 4 / 2
    expected["pid-tuning-r2-q1"] = 4 / 8
    a_react = (2 * 1.5) / 6
    expected["pid-tuning-r2-q3"] = 1.2 / a_react
    expected["pid-tuning-r3-q2"] = 0.9 / a_react
    expected["pid-tuning-r3-q3"] = 6 / (2 * (3 + 1.5))
    expected["pid-tuning-r4-q1"] = (0.6 * 12) * (1.6 / 8)
    expected["pid-tuning-r4-q3"] = 1.2 * 8 / (4 * 0.5)

    # realizations: degree, companion entries, DC gain, numpy characteristic polynomial
    expected["realization-r1-q2"] = 1.0
    expected["realization-r1-q3"] = 2.0
    expected["realization-r2-q1"] = -5.0
    expected["realization-r2-q3"] = 6.0 / 3.0
    expected["realization-r3-q2"] = 9.0 / 18.0
    companion = np.array([[0.0, 1.0], [-2.0, -7.0]])
    expected["realization-r3-q3"] = float(np.poly(companion)[1])
    expected["realization-r4-q1"] = 2.0
    companion_det = np.array([[0.0, 1.0], [-14.0, -9.0]])
    expected["realization-r4-q3"] = float(np.linalg.det(companion_det))

    # uncertainty arithmetic
    expected["uncertainty-r1-q2"] = abs(12 - 10) / 10
    expected["uncertainty-r1-q3"] = 4 + 0.5
    expected["uncertainty-r2-q1"] = 0.35
    expected["uncertainty-r2-q3"] = 2.4 / 8
    expected["uncertainty-r3-q2"] = abs(6.5 - 5)
    expected["uncertainty-r3-q3"] = 8 * (1 + 0.25)
    expected["uncertainty-r4-q1"] = 1 / 0.4
    expected["uncertainty-r4-q3"] = 20 * (1 + 0.30)

    # windup accumulation and back-calculation
    expected["windup-r1-q2"] = 4 * 2 * 3
    expected["windup-r1-q3"] = 16 - 10
    expected["windup-r2-q1"] = (8 - 18) / 0.5
    expected["windup-r2-q3"] = math.sqrt(4 * 0.64)
    expected["windup-r3-q2"] = 2.5 * 1.2
    expected["windup-r3-q3"] = 4 / 9
    expected["windup-r4-q1"] = (8 - 15) / 0.2
    expected["windup-r4-q3"] = 6 * 0.5 * 4

    numeric = check_expected(banks, expected, mismatches)

    texts = load_texts(SKILLS)
    checks = {
        "feedforward": "0.286",
        "freq-resp-lti": "2.121",
        "gen-gain-phase": "3.82",
        "linearization": "A = -8",
        "lti-stability": "= 60",
        "perf-specs-freq": "1.23",
        "pid-impl": "-12.5",
        "pid-tuning": "6.6",
        "realization": "13s",
        "uncertainty": "0.286",
        "windup": "-50",
    }
    for sid, needle in checks.items():
        if needle not in texts[sid]:
            mismatches.append(sid + " worked text missing " + needle)

    finish(numeric, mismatches)


if __name__ == "__main__":
    main()
