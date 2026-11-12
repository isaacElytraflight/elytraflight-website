#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB12.

Recomputes each numeric answer from the stated problems. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "optimality-over-convex-set",
    "projection-onto-convex-set",
    "gradient-projection-method",
    "scaled-gradient-projection",
    "affine-scaling-method",
    "primal-dual-interior-point",
    "frank-wolfe-conditional-gradient",
    "power-method-eigenvector",
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


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def question(banks, qid):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            return q
    raise SystemExit("missing " + qid)


def clip_box(point, lo, hi):
    return tuple(min(hi, max(lo, v)) for v in point)


def h_halfspace(z, h_diag, normal, bound):
    """Projection of z onto normal·x <= bound in the diagonal H-norm."""
    hinv = tuple(1.0 / h for h in h_diag)
    excess = dot(normal, z) - bound
    denom = sum(n * hi * n for n, hi in zip(normal, hinv))
    factor = excess / denom
    return tuple(zv - factor * hi * n for zv, hi, n in zip(z, hinv, normal))


def affine_direction(x, cost, row):
    """Primal affine scaling for a single equality row·x = sum(x) style row of ones."""
    x2 = tuple(v * v for v in x)
    normal = sum(a * v for a, v in zip(row, x2))
    rhs = sum(a * v * c for a, v, c in zip(row, x2, cost))
    y = rhs / normal
    reduced = tuple(c - a * y for c, a in zip(cost, row))
    direction = tuple(-v * r for v, r in zip(x2, reduced))
    return y, reduced, direction


def pd_equal_products(x, mu):
    """Newton dx for A=(1,1), s=x, y=0, target mu = x1*x2, which keeps s fixed."""
    # Derived: dx1 = x2 - x1 when mu = x1*x2 and s = x.
    dx1 = x[1] - x[0]
    return (dx1, -dx1)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    for sid, text in texts.items():
        if "The anchor value is 12" in text and sid != "optimality-over-convex-set":
            mismatches.append(sid + " borrowed the optimality worked example")
    expected = {}

    # Optimality. Gradient of 1/2 (t-5)^2 at t=2 is -3. Product with (0-2) is 6.
    grad_end = 2 - 5
    expected["optimality-over-convex-set-r1-q2"] = grad_end * (0 - 2)
    need(mismatches, grad_end == -3, "endpoint gradient was not -3")
    # -t^2 on [-2, 2]: f(0) - f(2) = 4.
    expected["optimality-over-convex-set-r3-q2"] = 0 - (-(2 ** 2))
    # Box objective (x-1)^2+(y-4)^2 at (1, 2). Gradient (0, -4). Step to (0, 0).
    g_box = (2 * (1 - 1), 2 * (2 - 4))
    step_box = (0 - 1, 0 - 2)
    expected["optimality-over-convex-set-r4-q2"] = dot(g_box, step_box)
    need(mismatches, g_box == (0, -4) and dot(g_box, step_box) == 8, "box product drifted")
    # Unit-square linear objective x. VI holds exactly on the left edge.
    opt_points = [(0, 0), (0, 1), (0, 0.5), (1, 0.2), (0.4, 0.4)]

    def vi_left(p):
        # gradient (1, 0). Min of (x - p0) over the square is -p0, since x>=0.
        return p[0] == 0

    opt_yes = [i for i, p in enumerate(opt_points) if vi_left(p)]
    need(mismatches, opt_yes == [0, 1, 2], f"square VI indices {opt_yes}")
    need(
        mismatches,
        question(banks, "optimality-over-convex-set-r2-q2")["correct_indices"] == [0, 1, 2],
        "square VI multi indices",
    )
    # Flaw: 6*(t-4) is negative for t<4.
    need(mismatches, 6 * (0 - 4) < 0, "the note's product is not negative")
    need(
        mismatches,
        question(banks, "optimality-over-convex-set-r3-q1")["flaw_index"] == 3,
        "optimality flaw index",
    )

    # Projection. Box clip of (-1, 5) onto [0, 2]^2.
    proj_box = clip_box((-1, 5), 0, 2)
    expected["projection-onto-convex-set-r1-q2"] = sum((a - b) ** 2 for a, b in zip((-1, 5), proj_box))
    need(mismatches, proj_box == (0, 2), f"box projection {proj_box}")
    # Ball radius 5 through (6, 8).
    zx, zy = 6, 8
    length = (zx ** 2 + zy ** 2) ** 0.5
    expected["projection-onto-convex-set-r3-q2"] = 5 * zx / length
    need(mismatches, abs(length - 10) < 1e-12, "ball length was not 10")
    # Scaled half-space, H=diag(4, 1), z=(3, 4), x+y<=2.
    scaled = h_halfspace((3, 4), (4, 1), (1, 1), 2)
    expected["projection-onto-convex-set-r4-q2"] = scaled[0]
    need(mismatches, abs(scaled[0] - 2) < 1e-12 and abs(scaled[1]) < 1e-12, f"scaled halfspace {scaled}")
    # Obtuse products for z=(2,0), p=(1,0).
    zp = (1, 0)
    samples = [(0, 0), (0, 1), (1, 0), (0.6, 0.8), (2, 0)]
    obtuse = [i for i, x in enumerate(samples) if dot(zp, (x[0] - 1, x[1] - 0)) <= 1e-12]
    need(mismatches, obtuse == [0, 1, 2, 3], f"obtuse indices {obtuse}")
    need(
        mismatches,
        question(banks, "projection-onto-convex-set-r2-q2")["correct_indices"] == [0, 1, 2, 3],
        "obtuse multi indices",
    )
    # The note's clip of (4, 1) onto [0, 2]^2 is (2, 1), not (4, 1).
    need(mismatches, clip_box((4, 1), 0, 2) == (2, 1), "box clip note")
    need(
        mismatches,
        question(banks, "projection-onto-convex-set-r3-q1")["flaw_index"] == 3,
        "projection flaw index",
    )

    # Gradient projection. (x-4)^2 on [0, 2] from 0 with step 1. Derivative -8.
    trial = 0 - 1 * (-8)
    expected["gradient-projection-method-r1-q2"] = min(2, max(0, trial))
    need(mismatches, trial == 8, "trial was not 8")
    # Gap ceiling ||x0-x*||^2 / (2 t k).
    expected["gradient-projection-method-r3-q2"] = 16 / (2 * 0.5 * 4)
    # 3x^2 on [-2, 2] from 1 with step 1. Derivative 6.
    trial_r4 = 1 - 1 * 6
    expected["gradient-projection-method-r4-q2"] = min(2, max(-2, trial_r4))
    need(mismatches, trial_r4 == -5, "second trial was not -5")
    # Fixed points of the unit-square step for objective x, step 1.
    def gp_fixed(p):
        trial_p = (p[0] - 1, p[1])
        landed = clip_box(trial_p, 0, 1)
        return landed == p

    gp_pts = [(0, 0), (0, 1), (0, 0.25), (1, 0), (0.5, 0.5)]
    gp_yes = [i for i, p in enumerate(gp_pts) if gp_fixed(p)]
    need(mismatches, gp_yes == [0, 1, 2], f"fixed-point indices {gp_yes}")
    need(
        mismatches,
        question(banks, "gradient-projection-method-r2-q2")["correct_indices"] == [0, 1, 2],
        "fixed-point multi indices",
    )
    # Note: trial (3, 1) on the unit square clips to (1, 1).
    need(mismatches, clip_box((3, 1), 0, 1) == (1, 1), "projected step note")
    need(
        mismatches,
        question(banks, "gradient-projection-method-r3-q1")["flaw_index"] == 3,
        "gradient-projection flaw index",
    )

    # Scaled box. H=diag(2, 4), g=(8, 4), x=(3, 4), t=1, box [0, 5]^2.
    trial_s = (3 - 1 * 8 / 2, 4 - 1 * 4 / 4)
    landed_s = clip_box(trial_s, 0, 5)
    expected["scaled-gradient-projection-r1-q2"] = landed_s[1]
    need(mismatches, trial_s == (-1, 3) and landed_s == (0, 3), f"scaled box {trial_s}")
    # Half-space H=diag(4, 1), z=(8, 4), x+y<=2.
    scaled_b = h_halfspace((8, 4), (4, 1), (1, 1), 2)
    expected["scaled-gradient-projection-r3-q2"] = scaled_b[0]
    need(mismatches, abs(scaled_b[0] - 6) < 1e-12 and abs(scaled_b[1] + 4) < 1e-12, f"scaled b {scaled_b}")
    # Projected Newton for 2x^2 - 2x at 2, onto [0, 1]. Derivative 6, second derivative 4.
    newton = 2 - 6 / 4
    expected["scaled-gradient-projection-r4-q2"] = min(1, max(0, newton))
    need(mismatches, abs(newton - 0.5) < 1e-12, "Newton point was not 1/2")
    # Positive definite scalings: diag(2,3), singular, [[2,1],[1,2]], diag(2,-1), 4I.
    def spd_sym(vals):
        return all(v > 0 for v in vals)

    spd_flags = [
        spd_sym((2, 3)),
        spd_sym((2, 0)),
        spd_sym((3, 1)),  # eigenvalues of [[2,1],[1,2]]
        spd_sym((2, -1)),
        spd_sym((4, 4)),
    ]
    need(mismatches, [i for i, ok in enumerate(spd_flags) if ok] == [0, 2, 4], f"spd flags {spd_flags}")
    need(
        mismatches,
        question(banks, "scaled-gradient-projection-r2-q2")["correct_indices"] == [0, 2, 4],
        "scaling multi indices",
    )
    # Note: Newton point 0 of (3/2) x^2 projects to 1 on [1, 4].
    need(mismatches, min(4, max(1, 0)) == 1, "projected Newton note")
    need(
        mismatches,
        question(banks, "scaled-gradient-projection-r3-q1")["flaw_index"] == 3,
        "scaled flaw index",
    )

    # Affine scaling. min x1+3 x2, x1+x2=4, start (2, 2).
    y_af, reduced_af, dir_af = affine_direction((2, 2), (1, 3), (1, 1))
    expected["affine-scaling-method-r1-q2"] = y_af
    blocking = min(-x / d for x, d in zip((2, 2), dir_af) if d < 0)
    alpha = 0.5 * blocking
    new_af = tuple(x + alpha * d for x, d in zip((2, 2), dir_af))
    expected["affine-scaling-method-r3-q2"] = new_af[0]
    expected["affine-scaling-method-r4-q2"] = dot((1, 3), new_af)
    need(
        mismatches,
        abs(y_af - 2) < 1e-12 and dir_af == (4, -4) and new_af == (3, 1),
        f"affine step {y_af, dir_af, new_af}",
    )
    direction_hits = (2, -3, 0, -1)
    hit_idx = [i for i, d in enumerate(direction_hits) if d < 0]
    need(mismatches, hit_idx == [1, 3], f"blocking coordinates {hit_idx}")
    need(
        mismatches,
        question(banks, "affine-scaling-method-r2-q2")["correct_indices"] == [1, 3],
        "affine multi indices",
    )
    # Note: from (4, 2) along (2, -2), half the blocking step is added, not subtracted.
    block_note = -2 / -2
    added = (4 + 0.5 * block_note * 2, 2 + 0.5 * block_note * -2)
    subtracted = (4 - 0.5 * 2, 2 - 0.5 * -2)
    need(mismatches, added == (5, 1) and subtracted == (3, 3), f"affine note {added, subtracted}")
    need(
        mismatches,
        question(banks, "affine-scaling-method-r3-q1")["flaw_index"] == 3,
        "affine flaw index",
    )

    # Primal-dual. x=s=(4, 2), mu=8. dx = (2-4, 4-2) = (-2, 2).
    dx = pd_equal_products((4, 2), 8)
    new_x = (4 + dx[0], 2 + dx[1])
    expected["primal-dual-interior-point-r1-q2"] = new_x[0]
    new_s = (4, 2)
    expected["primal-dual-interior-point-r3-q2"] = new_x[0] * new_s[0] + new_x[1] * new_s[1]
    expected["primal-dual-interior-point-r4-q2"] = 5 * 2
    need(mismatches, dx == (-2, 2) and new_x == (2, 4), f"pd step {dx, new_x}")
    need(mismatches, abs(8 - 4 * 2) < 1e-12, "target was not the product of the coordinates")
    pairs = [
        ((2, 2), (2, 2)),
        ((4, 1), (1, 4)),
        ((4, 4), (1, 1)),
        ((2, 4), (2, 2)),
        ((4, 1), (1, 2)),
    ]
    centered = [i for i, (xv, sv) in enumerate(pairs) if all(abs(a * b - 4) < 1e-12 for a, b in zip(xv, sv))]
    need(mismatches, centered == [0, 1, 2], f"central pairs {centered}")
    need(
        mismatches,
        question(banks, "primal-dual-interior-point-r2-q2")["correct_indices"] == [0, 1, 2],
        "central multi indices",
    )
    # Note: x=(3, 1), s=(3, 1), mu=3. dx=(-2, 2). Adding it gives (1, 3), not (5, -1).
    dx_note = pd_equal_products((3, 1), 3)
    updated = (3 + dx_note[0], 1 + dx_note[1])
    flipped = (3 - dx_note[0], 1 - dx_note[1])
    need(mismatches, dx_note == (-2, 2) and updated == (1, 3) and flipped == (5, -1), f"pd note {updated}")
    need(
        mismatches,
        question(banks, "primal-dual-interior-point-r3-q1")["flaw_index"] == 3,
        "primal-dual flaw index",
    )

    # Frank-Wolfe. Gradient (-1, 3) on the simplex, fraction 1/2, from (1/2, 1/2).
    # Smaller component is the first, so s=(1, 0).
    fw = tuple(0.5 * a + 0.5 * b for a, b in zip((0.5, 0.5), (1, 0)))
    expected["frank-wolfe-conditional-gradient-r1-q2"] = fw[0]
    expected["frank-wolfe-conditional-gradient-r3-q2"] = 2 / (6 + 2)
    # l1 ball, gradient (3, -6, 1), s=(0, 1, 0), fraction 1/2.
    l1_now = (0.2, -0.4, 0.1)
    l1_vertex = (0, 1, 0)
    l1_next = tuple(0.5 * a + 0.5 * b for a, b in zip(l1_now, l1_vertex))
    expected["frank-wolfe-conditional-gradient-r4-q2"] = l1_next[1]
    need(mismatches, fw == (0.75, 0.25) and abs(l1_next[1] - 0.3) < 1e-12, f"fw points {fw, l1_next}")
    grad_simplex = (2, 2, 5)
    fw_pts = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (0.5, 0.5, 0), (0.5, 0, 0.5)]
    fw_vals = [dot(grad_simplex, p) for p in fw_pts]
    fw_yes = [i for i, v in enumerate(fw_vals) if abs(v - min(fw_vals)) < 1e-12]
    need(mismatches, fw_yes == [0, 1, 3], f"oracle indices {fw_yes} values {fw_vals}")
    need(
        mismatches,
        question(banks, "frank-wolfe-conditional-gradient-r2-q2")["correct_indices"] == [0, 1, 3],
        "frank-wolfe multi indices",
    )
    # Note picks the larger component 4 over -1.
    need(mismatches, min(4, -1) == -1, "oracle should select -1")
    need(
        mismatches,
        question(banks, "frank-wolfe-conditional-gradient-r3-q1")["flaw_index"] == 2,
        "frank-wolfe flaw index",
    )

    # Power method. diag(5, 1) from (1, 1).
    ratio1 = 1 / 5
    expected["power-method-eigenvector-r1-q2"] = ratio1
    expected["power-method-eigenvector-r4-q2"] = ratio1 ** 2
    # Rayleigh of [[2, 1], [1, 2]] at (2, 1).
    vec = (2, 1)
    image = (2 * 2 + 1, 1 * 2 + 2 * 1)
    expected["power-method-eigenvector-r3-q2"] = dot(vec, image) / dot(vec, vec)
    need(mismatches, image == (5, 4), f"image {image}")
    axis = [(0, 1), (0, 3), (2, -1), (0, -2), (1, 1)]
    orth = [i for i, v in enumerate(axis) if v[0] == 0]
    need(mismatches, orth == [0, 1, 3], f"orthogonal starts {orth}")
    need(
        mismatches,
        question(banks, "power-method-eigenvector-r2-q2")["correct_indices"] == [0, 1, 3],
        "power multi indices",
    )
    # Rayleigh error scales with the square: three factors of 1/3 give 1/27 on the coefficient
    # and 1/729 on the squared error. The note claims 1/27 for the Rayleigh error.
    need(mismatches, abs((1 / 3) ** 3 - 1 / 27) < 1e-12, "three mode factors")
    need(mismatches, abs((1 / 3) ** 6 - 1 / 729) < 1e-12, "squared Rayleigh factor")
    need(
        mismatches,
        question(banks, "power-method-eigenvector-r3-q1")["flaw_index"] == 3,
        "power flaw index",
    )

    expect_key(mismatches, banks, "optimality-over-convex-set-r2-q3", "a*(b-a)")
    expect_key(mismatches, banks, "projection-onto-convex-set-r2-q3", "r*a/sqrt(a*a+b*b)")
    expect_key(mismatches, banks, "gradient-projection-method-r2-q3", "t-s*(a*t+b)")
    expect_key(mismatches, banks, "scaled-gradient-projection-r2-q3", "x-s*g/h")
    expect_key(mismatches, banks, "affine-scaling-method-r2-q3", "-x/d")
    expect_key(mismatches, banks, "primal-dual-interior-point-r2-q3", "x*s-m")
    expect_key(mismatches, banks, "frank-wolfe-conditional-gradient-r2-q3", "(1-g)*a+g*b")
    expect_key(mismatches, banks, "power-method-eigenvector-r2-q3", "(p+q*s*s)/(1+s*s)")

    # Worked examples stay out of the banks. Spot-check one number from each.
    for sid, banned in (
        ("optimality-over-convex-set", "anchor value is 12"),
        ("projection-onto-convex-set", "peg coordinate is 4"),
        ("gradient-projection-method", "latch point is 3"),
        ("scaled-gradient-projection", "wedge coordinate is 3"),
        ("affine-scaling-method", "ferry coordinate is 4.5"),
        ("primal-dual-interior-point", "gate gap is 8"),
        ("frank-wolfe-conditional-gradient", "kite weight is 0.4"),
        ("power-method-eigenvector", "mast ratio is 0.25"),
    ):
        blob = json.dumps(banks[sid])
        if banned in blob:
            mismatches.append(sid + " repeats its worked example")

    numeric = check_expected(banks, expected, mismatches)
    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
