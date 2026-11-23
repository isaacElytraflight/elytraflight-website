#!/usr/bin/env python3
"""Add the optimization-models course box and its coming-soon skills.

Idempotent: re-running replaces the new skills and the course boxes, and
leaves every other skill and box as they are. New skills ship with no banks.

  python3 tools/skilltree-content/eecs127_graph_gen.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GRAPH = os.path.join(ROOT, "skilltree", "ee105_skills_draft.json")
BOXES = os.path.join(ROOT, "skilltree", "collections.json")

REF = "reference only"
SCOPE = "scope only"


def sources(*refs):
    return [{"ref": ref, "use": REF if ref != "eecs127-scope" else SCOPE} for ref in refs]


def skill(sid, name, summary, prereqs, refs, video=None):
    row = {
        "id": sid,
        "name": name,
        "summary": summary,
        "prereqs": prereqs,
        "status": "coming-soon",
        "sources": sources(*refs),
    }
    if video:
        row["video"] = video
    return row


def watch(vid, title, start=None):
    video = {"url": "https://www.youtube.com/watch?v=" + vid, "title": title}
    if start is not None:
        video["start"] = start
    return video


NEW = [
    skill(
        "qr-factorization",
        "QR factorization",
        "Factor a full-column-rank matrix as an orthonormal factor times an upper-triangular factor by orthogonalizing its columns.",
        ["gram-schmidt-orthogonalization"],
        ("hefferon-linalg", "wikibooks-linalg", "eecs127-scope"),
        watch("cmqWm_jeZ0o", "Orthonormal columns by the Gram-Schmidt process"),
    ),
    skill(
        "fundamental-subspaces",
        "Four fundamental subspaces",
        "Split a matrix into its column space, row space, nullspace, and left nullspace, and use the two orthogonality relations among them.",
        ["lin-algebra-review", "inner-products"],
        ("hefferon-linalg", "wikibooks-linalg", "eecs127-scope"),
        watch("uQhTuRlWMxw", "Column space and null space of a linear map"),
    ),
    skill(
        "block-matrix-identities",
        "Block matrix identities",
        "Multiply and invert a two-by-two block matrix, and reduce the inverse with the Schur complement of an invertible block.",
        ["lin-algebra-review"],
        ("hefferon-linalg", "boyd-cvx", "eecs127-scope"),
    ),
    skill(
        "principal-component-analysis",
        "Principal component analysis",
        "Take the leading eigenvectors of a covariance, or the leading right singular vectors of centered data, as the directions of greatest spread.",
        ["spectral-decomposition", "singular-value-decomposition"],
        ("boyd-cvx", "hefferon-linalg", "eecs127-scope"),
        watch("FgakZw6K1QQ", "Directions of greatest spread in a data cloud"),
    ),
    skill(
        "low-rank-approximation",
        "Low-rank approximation",
        "Keep the largest singular values and zero the rest. That truncation is the nearest matrix of a given rank in the Frobenius norm and in the spectral norm.",
        ["singular-value-decomposition"],
        ("boyd-cvx", "hefferon-linalg", "eecs127-scope"),
        watch("nbBvuuNVfco", "Singular vectors and a truncated matrix approximation"),
    ),
    skill(
        "least-squares-perturbation",
        "Perturbation of least squares",
        "Bound how a change in the data matrix or the right-hand side moves a least-squares solution, using the ratio of the largest singular value to the smallest.",
        ["linear-least-squares", "singular-value-decomposition", "induced-matrix-norms"],
        ("nw-numopt", "boyd-cvx", "eecs127-scope"),
    ),
    skill(
        "ridge-regression",
        "Ridge regression",
        "Add a squared penalty on the coefficients, or a general squared penalty on a linear image of them, and solve the shifted normal equations.",
        ["least-squares-quadratic", "positive-definite-matrices"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
        watch("Q81RR3yKn30", "A squared penalty on the fitted coefficients"),
    ),
    skill(
        "principal-components-regression",
        "Principal components regression",
        "Replace the columns by the leading principal components, then solve an ordinary least-squares problem in that smaller coordinate.",
        ["principal-component-analysis", "low-rank-approximation", "least-squares-data-fitting"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "maximum-likelihood-estimation",
        "Maximum likelihood estimation",
        "Maximize the Gaussian density of the residuals. For independent equal-variance noise, that maximizer is the least-squares fit.",
        ["least-squares-data-fitting", "gaussian-random-vectors"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
        watch("XepXtl9YKwc", "Choosing parameters that make the observations most likely"),
    ),
    skill(
        "convex-reparameterization",
        "Reparameterizing a convex problem",
        "Change variables, move a constraint into the objective, or rewrite a problem so the same decisions are easier to recognize as convex.",
        ["optimization-problem-classes", "convex-functions"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "strong-convexity",
        "Strong convexity",
        "Add a quadratic bowl of curvature m under a convex function, and test it by a Hessian that stays at least m times the identity.",
        ["convexity-second-order", "positive-definite-matrices"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "gradient-descent",
        "Gradient descent",
        "Step in the direction opposite the gradient with length 1/L, and see why that step decreases a function with a Lipschitz gradient.",
        ["lipschitz-gradient", "descent-lemma"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
        watch("IHZwWFHWa-w", "Stepping opposite the gradient of a cost", start=415),
    ),
    skill(
        "stochastic-gradient-descent",
        "Stochastic gradient descent",
        "Replace the full gradient by an unbiased random draw from the data, and shrink the step length so the noise averages out.",
        ["gradient-descent"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "strong-duality",
        "Strong duality",
        "Name when the dual maximum equals the primal minimum, including a relative-interior constraint qualification that forces a zero gap.",
        ["lagrangian-duality-lower-bounds"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "convex-conjugate",
        "Convex conjugates",
        "Form the conjugate as the supremum of linear underestimators of a function, and use it to evaluate a dual function.",
        ["convex-functions", "lagrangian-duality-lower-bounds"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "maximum-a-posteriori-estimation",
        "Maximum a posteriori estimation",
        "Multiply a Gaussian likelihood by a Gaussian prior. The maximizer is a ridge fit, and the prior variance sets the penalty weight.",
        ["maximum-likelihood-estimation", "ridge-regression"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "lasso-regression",
        "Lasso regression",
        "Replace the squared penalty by an absolute-value penalty, and read sparsity off the corners of that penalty's unit ball.",
        ["ridge-regression", "vector-norms-lp"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
        watch("Xm2C_gTAl8c", "Why an absolute penalty prefers corners"),
    ),
    skill(
        "quadratic-program",
        "Convex quadratic programs",
        "Write a quadratic objective with affine equalities and inequalities, and keep the program convex when the Hessian is positive semidefinite.",
        ["optimization-problem-classes", "quadratic-function-minimization"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "quadratically-constrained-quadratic-program",
        "Quadratically constrained quadratic programs",
        "Allow quadratic inequality constraints, and keep each constraint convex when its Hessian is positive semidefinite.",
        ["quadratic-program"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "second-order-cone-program",
        "Second-order cone programs",
        "Constrain a Euclidean norm of an affine map by an affine upper bound, and recognize a convex quadratic constraint as one case.",
        ["quadratically-constrained-quadratic-program", "vector-norms-lp"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "semidefinite-program",
        "Semidefinite programs",
        "Constrain a symmetric affine matrix to be positive semidefinite. Linear, quadratic, and second-order-cone programs embed in this form by a Schur complement.",
        ["second-order-cone-program", "positive-definite-matrices", "block-matrix-identities"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "conic-duality",
        "Conic duality",
        "Write the dual of a cone program by swapping each cone for its dual cone, and compare the primal and dual values.",
        ["strong-duality", "second-order-cone-program"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "lasso-stationarity",
        "Lasso stationarity and soft thresholding",
        "Write stationarity with a subdifferential of the absolute penalty, and reduce it to soft thresholding when the columns are orthonormal.",
        ["lasso-regression", "convex-optimality-global"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "coordinate-descent",
        "Coordinate descent",
        "Minimize along one coordinate while the others stay fixed, and use one pass of that update on a separable absolute penalty.",
        ["gradient-descent", "lasso-regression"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
    skill(
        "equality-constrained-newton",
        "Newton's method with equality constraints",
        "Solve one Newton step on an equality-constrained problem as a single linear system in the step and the multiplier.",
        ["newton-method-optimization", "lagrange-multiplier-equality"],
        ("boyd-cvx", "nw-numopt", "eecs127-scope"),
    ),
]

CHAPTERS = [
    (
        "eecs127/models",
        "Optimization models",
        53,
        [
            "optimization-problem-formulation",
            "linear-least-squares",
            "local-global-minima",
        ],
    ),
    (
        "eecs127/linear-algebra",
        "Linear algebra",
        54,
        [
            "lin-algebra-review",
            "inner-products",
            "vector-norms-lp",
            "induced-matrix-norms",
            "frobenius-schatten-norms",
            "gram-schmidt-orthogonalization",
            "qr-factorization",
            "fundamental-subspaces",
            "spectral-decomposition",
            "positive-definite-matrices",
            "rayleigh-quotient",
            "singular-value-decomposition",
            "principal-component-analysis",
            "low-rank-approximation",
            "block-matrix-identities",
        ],
    ),
    (
        "eecs127/derivatives",
        "Derivatives and optimality",
        55,
        [
            "directional-derivative",
            "gradient-partial-derivatives",
            "jacobian-chain-rule",
            "hessian-matrix",
            "taylor-approximation-multivariable",
            "taylor-exact-mean-value",
            "matrix-calculus-gradients",
            "first-order-optimality",
        ],
    ),
    (
        "eecs127/estimation",
        "Least squares and estimation",
        56,
        [
            "least-squares-quadratic",
            "least-squares-data-fitting",
            "quadratic-function-minimization",
            "least-squares-perturbation",
            "ridge-regression",
            "principal-components-regression",
            "maximum-likelihood-estimation",
            "maximum-a-posteriori-estimation",
        ],
    ),
    (
        "eecs127/convexity",
        "Convexity",
        57,
        [
            "convex-sets",
            "convex-functions",
            "convexity-first-order",
            "convexity-second-order",
            "strong-convexity",
            "optimization-problem-classes",
            "convex-optimality-global",
            "convex-reparameterization",
        ],
    ),
    (
        "eecs127/gradient-methods",
        "Gradient methods",
        58,
        [
            "lipschitz-gradient",
            "descent-lemma",
            "sufficient-decrease-lemma",
            "convergence-rates",
            "gradient-descent",
            "gradient-method-convergence",
            "stochastic-gradient-descent",
            "projection-affine-halfspace-kkt",
            "projection-onto-convex-set",
            "gradient-projection-method",
        ],
    ),
    (
        "eecs127/duality",
        "Duality",
        59,
        [
            "lagrange-multiplier-equality",
            "lagrangian-duality-lower-bounds",
            "strong-duality",
            "kkt-conditions",
            "convex-conjugate",
            "conic-duality",
        ],
    ),
    (
        "eecs127/programs",
        "Convex programs",
        60,
        [
            "lp-standard-form",
            "quadratic-program",
            "quadratically-constrained-quadratic-program",
            "second-order-cone-program",
            "semidefinite-program",
        ],
    ),
    (
        "eecs127/sparsity",
        "Sparse regularization",
        61,
        [
            "lasso-regression",
            "lasso-stationarity",
        ],
    ),
    (
        "eecs127/newton-methods",
        "Coordinate and Newton methods",
        62,
        [
            "coordinate-descent",
            "newton-method-optimization",
            "equality-constrained-newton",
        ],
    ),
    (
        "eecs127/applications",
        "Support vectors and linear quadratic regulators",
        63,
        [
            "svm-quadratic-program",
            "lqr",
        ],
    ),
]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, data, indent):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def main():
    graph = load(GRAPH)
    retired = set(graph.get("retired") or {})
    by_id = {skill["id"]: skill for skill in graph["skills"]}
    new_ids = [row["id"] for row in NEW]
    if len(new_ids) != len(set(new_ids)):
        raise SystemExit("duplicate new id")
    for sid in new_ids:
        if sid in retired:
            raise SystemExit("new id is retired: " + sid)
    for row in NEW:
        for pre in row["prereqs"]:
            if pre not in by_id and pre not in new_ids:
                raise SystemExit(row["id"] + " missing prereq " + pre)
            if pre in retired:
                raise SystemExit(row["id"] + " uses retired " + pre)
    kept = [skill for skill in graph["skills"] if skill["id"] not in set(new_ids)]
    graph["skills"] = kept + NEW

    collections = load(BOXES)
    known = {skill["id"] for skill in graph["skills"]}
    chapter_ids = []
    chapters = []
    seen = set()
    for cid, title, color, skills in CHAPTERS:
        for sid in skills:
            if sid not in known:
                raise SystemExit(cid + " lists unknown " + sid)
            if sid in seen:
                raise SystemExit(sid + " is in two EECS 127 chapters")
            seen.add(sid)
        chapter_ids.append(cid)
        chapters.append({
            "id": cid,
            "title": title,
            "kind": "chapter",
            "children": [],
            "skills": skills,
            "color_index": color,
        })
    course = {
        "id": "eecs127",
        "title": "Optimization models in engineering",
        "kind": "course",
        "children": chapter_ids,
        "skills": [],
        "top_level": True,
        "tab_title": "Optimization Models in Engineering (Berkeley EECS 127)",
    }
    drop = set(chapter_ids) | {"eecs127"}
    collections["boxes"] = [box for box in collections["boxes"] if box["id"] not in drop]
    collections["boxes"].append(course)
    collections["boxes"].extend(chapters)
    dump(GRAPH, graph, 1)
    dump(BOXES, collections, 2)
    print(f"wrote {len(NEW)} coming-soon skills and {len(chapters)} topic boxes ({len(seen)} skills in the course)")


if __name__ == "__main__":
    main()
