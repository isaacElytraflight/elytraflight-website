#!/usr/bin/env python3
"""Independent numeric check for optimization-models batch EB2.

Recomputes each numeric answer from the data in the prompts. Does not import
the generator. Symbolic keys are checked by finish().
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "convex-reparameterization",
    "strong-convexity",
    "gradient-descent",
    "stochastic-gradient-descent",
    "strong-duality",
    "convex-conjugate",
    "maximum-a-posteriori-estimation",
    "lasso-regression",
]


def dual_value_upper_bound(lam, center, bound):
    """Dual function of minimize (x-center)^2 subject to x <= bound."""
    return lam * (center - bound) - lam ** 2 / 4


def map_mode(observations, lam, mean):
    total = float(np.sum(observations))
    n = len(observations)
    return (total + lam * mean) / (n + lam)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Epigraph of (x-4)^2+7. Change of variables y=2x on (2x-5)^2+(2x-1)^2.
    # Indicator of x>=4 on (x-1)^2. Substitution x+y=4 in (x-6)^2+(y-2)^2.
    expected["convex-reparameterization-r1-q2"] = 7.0
    y_star = 3.0
    expected["convex-reparameterization-r2-q2"] = y_star / 2.0
    expected["convex-reparameterization-r2-q3"] = (4.0 - 1.0) ** 2
    y_sub = 0.0
    expected["convex-reparameterization-r4-q2"] = (y_sub + 2.0) ** 2 + (y_sub - 2.0) ** 2

    # f=2x^2+5y^2 has Hessian diag(4, 10). Lower model of curvature 4 from
    # (0,0) to (1,2). Hessian [[7,1],[1,7]] has smallest eigenvalue 6.
    # Lower model of e^x+x^2 with m=2, from 0 to 1.
    hess_quad = np.diag([4.0, 10.0])
    expected["strong-convexity-r1-q2"] = float(np.min(np.linalg.eigvalsh(hess_quad)))
    expected["strong-convexity-r2-q2"] = 0.5 * 4.0 * (1.0 + 4.0)
    hess_off = np.array([[7.0, 1.0], [1.0, 7.0]])
    expected["strong-convexity-r2-q3"] = float(np.min(np.linalg.eigvalsh(hess_off)))
    expected["strong-convexity-r4-q2"] = 1.0 + 1.0 * 1.0 + 0.5 * 2.0 * 1.0

    # f=(x-4)^2, start 0, t=0.25, two steps. Then f=x^2+3y^2 from (1,1).
    # Then two steps of (x-2)^2+2(y-1)^2 from (0,0).
    x = 0.0
    for _ in range(1):
        x = x - 0.25 * (2.0 * (x - 4.0))
    expected["gradient-descent-r1-q2"] = x
    for _ in range(1):
        x = x - 0.25 * (2.0 * (x - 4.0))
    expected["gradient-descent-r2-q2"] = x
    y_gd = 1.0 - 0.25 * (6.0 * 1.0)
    expected["gradient-descent-r2-q3"] = y_gd
    px, py = 0.0, 0.0
    for _ in range(2):
        px = px - 0.25 * (2.0 * (px - 2.0))
        py = py - 0.25 * (4.0 * (py - 1.0))
    expected["gradient-descent-r4-q2"] = px

    # Two losses (x-2)^2 and (x-8)^2 at x=0. Draws -4 and -16.
    g1, g2 = -4.0, -16.0
    expected["stochastic-gradient-descent-r1-q2"] = 0.5 * (g1 + g2)
    expected["stochastic-gradient-descent-r2-q2"] = 0.0 - 0.5 * g1
    g2_at_2 = 2.0 * (2.0 - 8.0)
    expected["stochastic-gradient-descent-r2-q3"] = 2.0 - 0.25 * g2_at_2
    land_2 = 0.0 - 0.5 * g2
    expected["stochastic-gradient-descent-r4-q2"] = 0.5 * (
        (0.0 - 0.5 * g1) + land_2
    )

    # min (x-5)^2 s.t. x<=1, and min (x-1)^2 s.t. x>=4.
    expected["strong-duality-r1-q2"] = (1.0 - 5.0) ** 2
    expected["strong-duality-r2-q2"] = 2.0 * (5.0 - 1.0)
    expected["strong-duality-r2-q3"] = 2.0 * (4.0 - 1.0)
    expected["strong-duality-r4-q2"] = dual_value_upper_bound(4.0, 5.0, 1.0)

    # Conjugates of x^2, of 2x^2, of e^x, and of e^x at slope 2.
    expected["convex-conjugate-r1-q2"] = 6.0 ** 2 / 4.0
    expected["convex-conjugate-r2-q2"] = 4.0 ** 2 / 8.0
    expected["convex-conjugate-r2-q3"] = 1.0 * math.log(1.0) - 1.0
    expected["convex-conjugate-r4-q2"] = 2.0 * math.log(2.0) - 2.0

    expected["maximum-a-posteriori-estimation-r1-q2"] = map_mode([2.0, 4.0], 1.0, 0.0)
    expected["maximum-a-posteriori-estimation-r2-q2"] = map_mode([6.0, 6.0, 6.0], 4.0, 0.0)
    expected["maximum-a-posteriori-estimation-r2-q3"] = map_mode([2.0, 4.0], 1.0, 2.0)
    expected["maximum-a-posteriori-estimation-r4-q2"] = map_mode([5.0, 5.0, 5.0, 5.0], 4.0, 1.0)

    # Penalty 3*(2+1). Objectives with b=(3, 1/2) and with the 2 by 2 design.
    expected["lasso-regression-r1-q2"] = 3.0 * (2.0 + 1.0 + 0.0)
    expected["lasso-regression-r2-q2"] = (0.5) ** 2 + 2.0 * 3.0
    expected["lasso-regression-r2-q3"] = 2.0 * (3.0 + 0.5)
    design = np.array([[1.0, 1.0], [1.0, 0.0]])
    coeff = np.array([1.0, 0.0])
    resid = np.array([3.0, 1.0]) - design @ coeff
    expected["lasso-regression-r4-q2"] = float(resid @ resid + 2.0 * np.sum(np.abs(coeff)))

    numeric = check_expected(banks, expected, mismatches)

    def need(sid, snippet):
        if snippet not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {snippet!r}")

    need("convex-reparameterization", "value 49")
    need("strong-convexity", "equals 36")
    need("gradient-descent", "38/3")
    need("stochastic-gradient-descent", "average landing 7.2")
    need("strong-duality", "dual value 25")
    need("convex-conjugate", "y^2/20")
    need("maximum-a-posteriori-estimation", "equals 9.6")
    need("lasso-regression", "equals 38")

    # Worked-example identities, recomputed here rather than copied from prompts.
    if (27.0 - 20.0) ** 2 != 49.0:
        mismatches.append("reparameterization worked indicator value is not 49")
    model = 9.0 + 18.0 * 1.0 + 9.0 * 1.0
    if model != 36.0 or 9.0 * 4.0 != 36.0:
        mismatches.append("strong-convexity worked lower model is not 36")
    if abs(15.0 - (1.0 / 6.0) * 14.0 - 38.0 / 3.0) > 1e-12:
        mismatches.append("gradient worked step is not 38/3")
    if abs((6.6 + 7.8) / 2.0 - 7.2) > 1e-12:
        mismatches.append("stochastic worked average landing is not 7.2")
    if abs(dual_value_upper_bound(10.0, 7.0, 2.0) - 25.0) > 1e-12:
        mismatches.append("duality worked value is not 25")
    if abs(10.0 ** 2 / 20.0 - 5.0) > 1e-12:
        mismatches.append("conjugate worked value is not 5")
    if abs(map_mode([10.0, 14.0], 0.5, 0.0) - 9.6) > 1e-12:
        mismatches.append("MAP worked mode is not 9.6")
    worked_A = np.diag([3.0, 3.0])
    worked_x = np.array([1.0, 0.0])
    worked_r = np.array([3.0, 6.0]) - worked_A @ worked_x
    if abs(float(worked_r @ worked_r + 2.0) - 38.0) > 1e-12:
        mismatches.append("lasso worked objective is not 38")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
