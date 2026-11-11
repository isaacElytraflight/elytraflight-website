#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB6.

Recomputes each numeric answer from the linear programs. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json
from itertools import combinations

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "lp-standard-form",
    "lp-graphical-solution",
    "polyhedra-extreme-points",
    "basic-feasible-solutions",
    "simplex-feasible-directions",
    "simplex-method-iteration",
    "simplex-phase-one",
]


def expect_key(mismatches, banks, qid, expression):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            if q.get("answer") != expression:
                mismatches.append(f"{qid}: key {q.get('answer')!r} != {expression!r}")
            return
    mismatches.append(f"{qid}: missing symbolic question")


def need(mismatches, cond, message):
    if not cond:
        mismatches.append(message)


def basic_solution(A, b, basis):
    basis = list(basis)
    xB = np.linalg.solve(A[:, basis], np.asarray(b, dtype=float))
    x = np.zeros(A.shape[1])
    x[basis] = xB
    return x, xB


def reduced_costs(A, c, basis):
    basis = list(basis)
    pi = np.linalg.solve(A[:, basis].T, np.asarray(c, dtype=float)[basis])
    return np.asarray(c, dtype=float) - A.T @ pi


def ratio_step(xB, abar):
    hits = [(float(xB[i] / abar[i]), i) for i in range(len(xB)) if abar[i] > 1e-10]
    if not hits:
        return None
    return min(hits)


def pivot(A, b, c, basis, enter):
    """One simplex pivot. Returns None when the entering column is an unbounded ray."""
    basis = list(basis)
    _, xB = basic_solution(A, b, basis)
    abar = np.linalg.solve(A[:, basis], A[:, enter])
    step = ratio_step(xB, abar)
    if step is None:
        return None
    theta, leave_at = step
    new_basis = list(basis)
    new_basis[leave_at] = enter
    return theta, basis[leave_at], new_basis, abar


def feasible_bases(A, b):
    m = A.shape[0]
    found = []
    for cols in combinations(range(A.shape[1]), m):
        if abs(np.linalg.det(A[:, cols])) < 1e-8:
            continue
        x, xB = basic_solution(A, b, cols)
        found.append((cols, x, bool(np.all(xB >= -1e-8))))
    return found


def vertex_values(vertices, cost):
    return [float(np.dot(cost, v)) for v in vertices]


def polygon_vertices(inequalities):
    """Corners of a planar polygon given as (a, b, rhs) for a x + b y <= rhs."""
    lines = []
    for a, b, rhs in inequalities:
        lines.append((float(a), float(b), float(rhs)))
    found = []
    for i, j in combinations(range(len(lines)), 2):
        mat = np.array([[lines[i][0], lines[i][1]], [lines[j][0], lines[j][1]]])
        if abs(np.linalg.det(mat)) < 1e-8:
            continue
        point = np.linalg.solve(mat, [lines[i][2], lines[j][2]])
        if all(a * point[0] + b * point[1] <= rhs + 1e-8 for a, b, rhs in lines):
            key = (round(float(point[0]), 6), round(float(point[1]), 6))
            if key not in found:
                found.append(key)
    return found


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Standard form: free split (2) plus y, one slack, and one surplus.
    expected["lp-standard-form-r1-q2"] = 2 + 1 + 1 + 1
    # Slack of 4x + y <= 11 at (1, 3).
    expected["lp-standard-form-r3-q2"] = 11 - (4 * 1 + 1 * 3)
    # Standard-form objective -6x - y at (2, 3).
    expected["lp-standard-form-r4-q2"] = -6 * 2 - 1 * 3
    # At (4, 2) the lower bound x - y >= 1 has unused room 1. Adding a nonnegative
    # surplus makes the left side even larger, so it cannot restore equality.
    need(
        mismatches,
        (4 - 2) - 1 == 1 and (4 - 2) > 1,
        "standard-form lower bound is not repaired by adding the surplus",
    )

    para = [(1, 2), (5, 1), (6, 4), (2, 5)]
    sum_vals = vertex_values(para, (1, 1))
    diff_vals = vertex_values(para, (1, -2))
    tilt_vals = vertex_values(para, (1, 4))
    weight_vals = vertex_values(para, (2, 1))
    expected["lp-graphical-solution-r1-q2"] = min(sum_vals)
    expected["lp-graphical-solution-r2-q3"] = min(diff_vals)
    expected["lp-graphical-solution-r3-q2"] = max(tilt_vals)
    expected["lp-graphical-solution-r4-q2"] = min(weight_vals)
    need(mismatches, sum_vals[1] != min(sum_vals), "graphical error step is not actually false")
    need(mismatches, tilt_vals[0] == tilt_vals[1] == min(tilt_vals), "edge objective is not constant")
    # min x+y on x >= 1, y >= 0 is 1, and the set is unbounded.
    need(mismatches, 1 + 0 == 1 and 1 + 100 > 1, "unbounded feasible set lost its finite minimum")

    halfspaces = [( -1, 0, 0), (0, -1, 0), (1, 1, 8), (0, 1, 5)]
    corners = polygon_vertices(halfspaces)
    expected["polyhedra-extreme-points-r1-q2"] = 4 / 8
    expected["polyhedra-extreme-points-r3-q2"] = len(corners)
    expected["polyhedra-extreme-points-r4-q1"] = max(vertex_values(corners, (1, 2)))
    edge = (1 - 0.2) * np.array((3.0, 5.0)) + 0.2 * np.array((8.0, 0.0))
    need(mismatches, np.allclose(edge, (4, 4)), "(4, 4) is not a strict convex combination of the edge")

    bfs_A = np.array([[1.0, 1, 1, 0], [1, 2, 0, 1]])
    bfs_b = np.array([6.0, 10])
    x_12, _ = basic_solution(bfs_A, bfs_b, (0, 1))
    expected["basic-feasible-solutions-r1-q2"] = x_12[1]
    slack_x, _ = basic_solution(bfs_A, bfs_b, (2, 3))
    expected["basic-feasible-solutions-r3-q2"] = slack_x[2] + slack_x[3]
    bfs_A2 = np.array([[1.0, 1, 1, 0], [4, 1, 0, 1]])
    x_round4, _ = basic_solution(bfs_A2, [9.0, 12], (0, 1))
    expected["basic-feasible-solutions-r4-q1"] = x_round4[0] + x_round4[1]
    labeled = {cols: (x, ok) for cols, x, ok in feasible_bases(bfs_A, bfs_b)}
    need(mismatches, labeled[(0, 2)][1] is False and labeled[(0, 2)][0][2] < 0, "columns 1 and 3 were feasible")
    need(mismatches, labeled[(1, 3)][1] is False and labeled[(1, 3)][0][3] < 0, "columns 2 and 4 were feasible")
    for cols in ((0, 1), (0, 3), (1, 2), (2, 3)):
        need(mismatches, labeled[cols][1], f"basis {cols} was marked infeasible")

    dir_A = np.array([[1.0, 1, 1, 0], [2, 1, 0, 1]])
    dir_b = np.array([7.0, 10])
    dir_c = np.array([-2.0, -3, 0, 0])
    dir_rc = reduced_costs(dir_A, dir_c, (2, 3))
    step_x2 = pivot(dir_A, dir_b, dir_c, (2, 3), 1)
    step_x1 = pivot(dir_A, dir_b, dir_c, (2, 3), 0)
    expected["simplex-feasible-directions-r1-q2"] = step_x2[0]
    expected["simplex-feasible-directions-r3-q2"] = step_x1[0] * dir_rc[0]
    expected["simplex-feasible-directions-r4-q1"] = dir_rc[1]
    x_after, _ = basic_solution(dir_A, dir_b, step_x2[2])
    expected["simplex-feasible-directions-r4-q3"] = float(dir_c @ x_after)
    need(mismatches, np.allclose(step_x1[3], (1, 2)), "x1 tableau column is not (1, 2)")
    need(mismatches, abs((-step_x1[3][1]) - (-2)) < 1e-8, "basic direction second component is not -2")
    need(mismatches, step_x2[1] == 2 and set(step_x2[2]) == {1, 3}, "x2 pivot did not leave x3")

    it_A = np.array([[1.0, 1, 1, 0], [1, 2, 0, 1]])
    it_b = np.array([6.0, 8])
    it_c = np.array([-3.0, -4, 0, 0])
    it_rc = reduced_costs(it_A, it_c, (2, 3))
    expected["simplex-method-iteration-r1-q2"] = float(np.min(it_rc[:2]))
    step_it_x1 = pivot(it_A, it_b, it_c, (2, 3), 0)
    x_it, _ = basic_solution(it_A, it_b, step_it_x1[2])
    expected["simplex-method-iteration-r3-q2"] = float(it_c @ x_it)
    step_it_x2 = pivot(it_A, it_b, it_c, (2, 3), 1)
    need(mismatches, abs(step_it_x2[0] - 4) < 1e-8 and step_it_x2[1] == 3, "minimum ratio did not leave x4")
    mid_rc = reduced_costs(it_A, it_c, step_it_x1[2])
    follow = pivot(it_A, it_b, it_c, step_it_x1[2], 1)
    x_opt, _ = basic_solution(it_A, it_b, follow[2])
    expected["simplex-method-iteration-r4-q1"] = float(it_c @ x_opt)
    opt_rc = reduced_costs(it_A, it_c, follow[2])
    need(mismatches, mid_rc[1] < 0 and np.all(opt_rc >= -1e-8), "iteration did not reach a nonnegative reduced-cost basis")
    opt_values = []
    for cols, x, ok in feasible_bases(it_A, it_b):
        if ok:
            opt_values.append(float(it_c @ x))
    need(mismatches, abs(min(opt_values) - float(it_c @ x_opt)) < 1e-8, "enumerated optimum disagrees with the pivot path")
    ray_A = np.array([[1.0, -1, 1]])
    ray_b = np.array([5.0])
    ray_c = np.array([-2.0, 0, 0])
    ray_step = pivot(ray_A, ray_b, ray_c, (2,), 0)
    x_ray, _ = basic_solution(ray_A, ray_b, ray_step[2])
    expected["simplex-method-iteration-r4-q2"] = float(ray_c @ x_ray)
    ray_rc = reduced_costs(ray_A, ray_c, ray_step[2])
    ray_col = np.linalg.solve(ray_A[:, ray_step[2]], ray_A[:, 1])
    need(
        mismatches,
        ray_rc[1] < 0 and not np.any(ray_col > 1e-10),
        "updated y column is not an unbounded improving ray",
    )

    ph_A = np.array([
        [1.0, 2, -1, 0, 1, 0],
        [1.0, 1, 0, -1, 0, 1],
    ])
    ph_b = np.array([8.0, 3])
    ph_c = np.array([0.0, 0, 0, 0, 1, 1])
    ph_x0, _ = basic_solution(ph_A, ph_b, (4, 5))
    expected["simplex-phase-one-r1-q2"] = float(ph_c @ ph_x0)
    ph_rc = reduced_costs(ph_A, ph_c, (4, 5))
    need(mismatches, abs(ph_rc[0] + 2) < 1e-8 and abs(ph_rc[1] + 3) < 1e-8, "phase-I reduced costs are not the negative column sums")
    first = pivot(ph_A, ph_b, ph_c, (4, 5), 1)
    expected["simplex-phase-one-r4-q1"] = first[0]
    second = pivot(ph_A, ph_b, ph_c, first[2], 3)
    x_rec, _ = basic_solution(ph_A, ph_b, second[2])
    expected["simplex-phase-one-r4-q2"] = x_rec[1]
    need(mismatches, abs(float(ph_c @ x_rec)) < 1e-8 and x_rec[4] == 0 and x_rec[5] == 0, "phase I did not recover a feasible point")

    bad_A = np.array([
        [1.0, 1, 1, 0, 0],
        [1.0, 1, 0, -1, 1],
    ])
    bad_b = np.array([12.0, 19])
    bad_c = np.array([0.0, 0, 0, 0, 1.0])
    # a - s - t = 7 follows by subtracting the two rows, so the auxiliary minimum is 7.
    gap = float(bad_b[1] - bad_b[0])
    best_aux = min(float(bad_c @ x) for _, x, ok in feasible_bases(bad_A, bad_b) if ok)
    expected["simplex-phase-one-r3-q2"] = best_aux
    need(mismatches, abs(best_aux - gap) < 1e-8 and best_aux > 0, "phase-I infeasible optimum is not the row gap")

    expect_key(mismatches, banks, "lp-standard-form-r3-q3", "p-a*x-b*y")
    expect_key(mismatches, banks, "lp-graphical-solution-r3-q3", "-p/q")
    expect_key(mismatches, banks, "polyhedra-extreme-points-r3-q3", "s/p")
    expect_key(mismatches, banks, "basic-feasible-solutions-r2-q3", "p/a+q/d")
    expect_key(mismatches, banks, "simplex-feasible-directions-r2-q3", "c-u*a")
    expect_key(mismatches, banks, "simplex-method-iteration-r2-q3", "p/r")
    expect_key(mismatches, banks, "simplex-phase-one-r2-q3", "-a-b")

    markers = {
        "lp-standard-form": "The ribbon slack is 19",
        "lp-graphical-solution": "The shed level is 18",
        "polyhedra-extreme-points": "The yard value is 65",
        "basic-feasible-solutions": "The bench sum is 14",
        "simplex-feasible-directions": "The lane step cuts 54",
        "simplex-method-iteration": "The kiln value is -45",
        "simplex-phase-one": "The dock artificial is 26",
    }
    shed = min(vertex_values([(7, 11), (15, 11), (7, 18)], (1, 1)))
    yard = min(vertex_values([(2, 7), (2, 11), (10, 7)], (1, 9)))
    bench_x, _ = basic_solution(
        np.array([[1.0, 2, 1, 0], [1, 1, 0, 1]]),
        [21.0, 14],
        (0, 1),
    )
    lane_A = np.array([[1.0, 1, 1, 0], [1, 2, 0, 1]])
    lane_step = pivot(lane_A, [9.0, 17], [-6.0, -1, 0, 0], (2, 3), 0)
    kiln_A = np.array([[1.0, 1, 1, 0], [2, 1, 0, 1]])
    kiln_c = np.array([-2.0, -5, 0, 0])
    kiln_step = pivot(kiln_A, [9.0, 12], kiln_c, (2, 3), 1)
    kiln_x, _ = basic_solution(kiln_A, [9.0, 12], kiln_step[2])
    dock_A = np.array([
        [1.0, 1, -1, 0, 1, 0],
        [2.0, 1, 0, -1, 0, 1],
    ])
    dock_b = np.array([6.0, 20])
    dock_c = np.array([0.0, 0, 0, 0, 1.0, 1])
    dock_x, _ = basic_solution(dock_A, dock_b, (4, 5))
    dock_first = pivot(dock_A, dock_b, dock_c, (4, 5), 0)
    dock_second = pivot(dock_A, dock_b, dock_c, dock_first[2], 2)
    dock_end, _ = basic_solution(dock_A, dock_b, dock_second[2])
    need(
        mismatches,
        abs(dock_end[0] - 10) < 1e-8 and abs(dock_end[1]) < 1e-8 and abs(float(dock_c @ dock_end)) < 1e-8,
        "dock phase I did not finish at x=10, y=0",
    )
    anchors = {
        "lp-standard-form": 41 - (8 * 2 + 6),
        "lp-graphical-solution": shed,
        "polyhedra-extreme-points": yard,
        "basic-feasible-solutions": float(bench_x[0] + bench_x[1]),
        "simplex-feasible-directions": abs(lane_step[0] * reduced_costs(lane_A, [-6.0, -1, 0, 0], (2, 3))[0]),
        "simplex-method-iteration": float(kiln_c @ kiln_x),
        "simplex-phase-one": float(dock_c @ dock_x),
    }
    bank_blobs = {sid: json.dumps(banks[sid]) for sid in SKILLS}
    for sid, phrase in markers.items():
        if phrase not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {phrase!r}")
        if phrase in bank_blobs[sid]:
            mismatches.append(f"{sid} worked-example phrase reused in the bank")
        rendered = f"{anchors[sid]:.6g}"
        if rendered not in texts[sid]:
            mismatches.append(f"{sid} explainer missing recomputed anchor {rendered}")

    numeric = check_expected(banks, expected, mismatches)
    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
