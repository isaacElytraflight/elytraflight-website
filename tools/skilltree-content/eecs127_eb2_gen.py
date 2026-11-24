#!/usr/bin/env python3
"""Generate optimization-models batch EB2 banks and explainers.

Skills: convex-reparameterization, strong-convexity, gradient-descent,
stochastic-gradient-descent, strong-duality, convex-conjugate,
maximum-a-posteriori-estimation, lasso-regression.

Closed-form answers live here. skilltree/verify_eecs127_eb2.py recomputes
the numeric ones and does not import this file.

Ordering check: every order question was read pair by pair. Each step uses
a point, an expression, or a number that the previous step produces, so
swapping an adjacent pair leaves the procedure incorrect.
Diagrams: a bowl where the epigraph, the curvature, the gradient step, or
the conjugate needs the graph; a Hessian matrix where the entries are not
the answer; a half-space where strict feasibility is the question; the
norm balls where the corner geometry is the question. Formula-only prompts
have no figure.
"""
import math
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import DEEP_TYPES, Bank, deep_quota, save_explainer
from templates import ellipse_axes, halfspace_fig, matrix_fig, norm_balls, plot

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IDS = [
    "convex-reparameterization",
    "strong-convexity",
    "gradient-descent",
    "stochastic-gradient-descent",
    "strong-duality",
    "convex-conjugate",
    "maximum-a-posteriori-estimation",
    "lasso-regression",
]
VIDEOS = {
    "convex-reparameterization": {
        "url": "https://www.youtube.com/watch?v=fan8mh0D-4E",
        "title": "Rewriting an objective as an epigraph constraint",
    },
    "strong-convexity": {
        "url": "https://www.youtube.com/watch?v=Clw24Fajnqg",
        "title": "A quadratic lower model of curvature m",
        "start": 1514,
    },
    "gradient-descent": {
        "url": "https://www.youtube.com/watch?v=IHZwWFHWa-w",
        "title": "Stepping opposite the gradient of a cost",
        "start": 415,
    },
    "stochastic-gradient-descent": {
        "url": "https://www.youtube.com/watch?v=UmathvAKj80",
        "title": "An unbiased random gradient and a shrinking step",
    },
    "strong-duality": {
        "url": "https://www.youtube.com/watch?v=bPLNyYFLLT4",
        "title": "When the dual maximum equals the primal minimum",
    },
    "convex-conjugate": {
        "url": "https://www.youtube.com/watch?v=hUUveDyhcEA",
        "title": "The supremum that defines a convex conjugate",
    },
    "maximum-a-posteriori-estimation": {
        "url": "https://www.youtube.com/watch?v=wdWHbYdhfG8",
        "title": "A Gaussian prior whose mode is a squared-penalty fit",
    },
    "lasso-regression": {
        "url": "https://www.youtube.com/watch?v=NGf0voTMlcs",
        "title": "An absolute penalty and the corners of its unit ball",
    },
}

PREV = {
    "convex-reparameterization": ["quadratic-program"],
    "strong-convexity": ["gradient-method-convergence"],
    "gradient-descent": ["stochastic-gradient-descent"],
    "stochastic-gradient-descent": ["incremental-gradient-methods"],
    "strong-duality": ["conic-duality"],
    "convex-conjugate": ["strong-duality"],
    "maximum-a-posteriori-estimation": ["lasso-regression"],
    "lasso-regression": ["lasso-stationarity"],
}

BOWL = plot(lambda x: (x - 2) ** 2 + 1, 0, 4, "x", "f", "a convex bowl")
ABOWL = "A curve that opens upward. The horizontal axis is labeled x and the vertical axis is labeled f."
STEP = plot(lambda x: (x - 4) ** 2, 0, 8, "x", "f", "objective for one gradient step")
ASTEP = "A parabola opening upward on axes labeled x and f."
HESS = matrix_fig([["7", "1"], ["1", "7"]], "Hessian with equal diagonal entries")
AHESS = "A 2 by 2 matrix with 7 on the diagonal and 1 in each off-diagonal entry."
HALF = halfspace_fig("one strict side of a straight constraint")
AHALF = "A straight boundary with one side shaded. The axes are labeled x1 and x2."
BALLS = norm_balls("unit balls of the 1-norm, 2-norm, and infinity-norm")
ABALLS = "Three shapes centered at the origin: a diamond labeled 1, a disk labeled 2, and a square labeled inf."
PRIOR = ellipse_axes("level set of a round Gaussian prior", rx=64, ry=64)
APRIOR = "A circle centered at the origin, with axes labeled x1 and x2."
CONJ = plot(lambda x: x * x, 0, 2.5, "x", "f", "function being conjugated")
ACONJ = "A parabola opening upward, touching the origin, on axes labeled x and f."


def publish_graph():
    path = os.path.join(ROOT, "skilltree", "ee105_skills_draft.json")
    with open(path, encoding="utf-8") as f:
        graph = json.load(f)
    for skill in graph["skills"]:
        if skill["id"] not in VIDEOS:
            continue
        skill.pop("status", None)
        skill["video"] = VIDEOS[skill["id"]]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=1, ensure_ascii=False)
        f.write("\n")


def bank_reparam():
    b = Bank("convex-reparameterization")
    p = PREV["convex-reparameterization"]
    b.mc(
        1,
        r"A convex objective \(f\) is already recognized as convex. The epigraph form of minimizing \(f(x)\) is",
        [
            r"minimize \(t\) subject to \(f(x)\le t\)",
            r"maximize \(t\) subject to \(f(x)\le t\)",
            r"minimize \(t\) subject to \(f(x)\ge t\)",
            r"minimize \(f(x)+t\) with no constraint on \(t\)",
        ],
        0,
        r"The epigraph introduces a new scalar that is forced to sit above the graph, and the objective becomes that scalar. Minimizing \(t\) subject to \(f(x)\le t\) has the same optimal value as minimizing \(f\). Maximizing \(t\) runs the wrong direction. The reversed inequality \(f(x)\ge t\) puts \(t\) under the graph. Adding \(t\) to \(f\) without a constraint does not lift the graph.",
        BOWL, ABOWL,
    )
    b.num(
        1,
        r"The epigraph form minimizes \(t\) subject to \((x-4)^2+7\le t\). What is the optimal \(t\)?",
        7, "(unitless)",
        r"The smallest feasible \(t\) is the smallest value of \((x-4)^2+7\). The square is 0 at \(x=4\), so the minimum is 7, and \(t=7\) is attained. The unconstrained minimizer \(x=4\) is a decision, not the optimal value. The number 4 is that decision. A value such as 11 adds an extra constant that the expression does not have.",
    )
    b.mc(
        1,
        r"The objective \(f\) is convex, and the new variable \(y\) is related to the old decision by an affine map \(x=By+d\). The reparameterized objective \(g(y)=f(By+d)\) is",
        [
            r"convex only when \(B\) is a square orthogonal matrix",
            r"not convex, because a change of variables always destroys the chord test",
            r"convex, for every matrix \(B\) and every vector \(d\)",
            r"convex only when \(B\) is invertible",
        ],
        2,
        r"An affine image preserves the chord test: a chord in \(y\) maps to a chord in \(x=By+d\), and \(f\) lies under its chords. Orthogonality is not required. Invertibility is not required either; a non-square \(B\) still gives a convex \(g\). A nonlinear substitution can break the chord test, but this substitution is affine.",
    )
    b.order(
        2,
        r"Put these steps in the order that moves a constraint into the objective and then lifts that objective into an epigraph. Each step uses the object the previous step just built.",
        [
            "Write the feasible set as the set where its indicator is zero, and positive infinity outside.",
            "Add that indicator to the objective and drop the explicit constraint, leaving an unconstrained problem.",
            "Introduce a scalar t that must be at least as large as that new objective.",
            "Minimize t. The optimal t equals the optimal value of the constrained problem you started with.",
        ],
        r"The indicator has to be defined before it can be added. The sum has to exist before a scalar can be required to sit above it. That scalar has to be the decision before minimizing it reports the optimal value. Swapping an adjacent pair uses an indicator, a sum, or a scalar that has not been built yet.",
    )
    b.num(
        2,
        r"Minimize \((2x-5)^2+(2x-1)^2\). The change of variables \(y=2x\) rewrites the objective as \((y-5)^2+(y-1)^2\). What is the minimizer in the original variable \(x\)?",
        1.5, "(unitless)",
        r"The derivative of \((y-5)^2+(y-1)^2\) is \(4y-12\), which is zero at \(y=3\). Then \(x=y/2=1.5\). Reporting 3 leaves the answer in the new variable. The optimal value is \((3-5)^2+(3-1)^2=8\), which is a value, not the minimizer. The second critical-point formula \(y=5\) uses only one of the two squares.",
    )
    b.num(
        2,
        r"The constraint \(x\ge 4\) is moved into the objective by an indicator that is 0 on that ray and \(+\infty\) outside it. The smooth part is \((x-1)^2\). What is the minimum value of the resulting objective?",
        9, "(unitless)",
        r"The square \((x-1)^2\) is smallest at \(x=1\), which lies outside the ray, so the indicator is infinite there. On the ray the square decreases as \(x\) decreases, and the smallest feasible \(x\) is 4. The value is \((4-1)^2=9\), and the indicator contributes 0 at that point. Reporting 0 keeps only the indicator. Reporting 1 is the infeasible unconstrained minimizer.",
    )
    b.sym(
        3,
        r"Let \(a>0\) and let \(b\ne 0\). Define \(f(z)=a z^2\), which is convex, and set \(z=by+c\). Write the reparameterized objective \(g(y)=f(by+c)\) as an expression in \(a\), \(b\), \(c\), and \(y\).",
        "a*(b*y+c)**2",
        {"a": (0.5, 3), "b": (0.5, 2), "c": (-2, 2), "y": (-2, 2)},
        r"Substitute the affine expression into \(f\). One factor of \(a\) stays in front, and the inside of the square is \(by+c\), not \(y\) alone."
        "\n"
        r"• \(a y^2\) drops the change of variables."
        "\n"
        r"• \((by+c)^2\) drops the curvature \(a\)."
        "\n"
        r"• \(a(by+c)\) forgets the square.",
        ["a*(b*y+c)*(b*y+c)", "a*((b*y+c)**2)"],
    )
    b.mc(
        3,
        r"The absolute value \(f(u)=\lvert u\rvert\) is convex. Which substitution can produce an objective that fails the chord test?",
        [
            r"the affine substitution \(u=2y+3\)",
            r"the nonlinear substitution \(u=y^2-1\)",
            r"the translation \(u=y-4\)",
            r"the scaling \(u=-y\)",
        ],
        1,
        r"Affine maps preserve convexity, so \(u=2y+3\), \(u=y-4\), and \(u=-y\) all leave an absolute value of an affine function, which is still convex. The substitution \(u=y^2-1\) is not affine. The resulting \(g(y)=\lvert y^2-1\rvert\) satisfies \(g(-1)=g(1)=0\) but \(g(0)=1\), so the graph at the midpoint sits above the chord.",
    )
    b.multi(
        3,
        r"Which rewrites have the same optimal value as minimizing \((x-2)^2\) subject to \(x\ge 0\)?",
        [
            r"Minimize \(t\) subject to \((x-2)^2\le t\) and \(x\ge 0\).",
            r"Minimize \((x-2)^2+I(x)\), where \(I\) is 0 for \(x\ge 0\) and \(+\infty\) otherwise.",
            r"Minimize \((x-2)^2+t\) with \(t\) free and no constraint.",
            r"Minimize \(t\) subject to \((x-2)^2\ge t\) and \(x\ge 0\).",
        ],
        [0, 1],
        r"The original optimal value is \(0\), attained at \(x=2\). The epigraph form has that same value: its minimizer is the pair \((x,t)=(2,0)\), so \(t\) equals the value and the decision \(x\) matches. The indicator form keeps the minimizer \(x=2\) and the value \(0\). Adding a free \(t\) to the square leaves \(t\) unbounded below. The reversed epigraph inequality asks \(t\) to sit under the square, so the optimal \(t\) runs off to \(-\infty\).",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The problem is to minimize \(x^2+4\) subject to \(x\le 3\).",
        [
            r"The objective \(x^2+4\) is convex and the set \(x\le 3\) is convex, so the problem is convex.",
            r"The indicator of \(x\le 3\) is 0 on that set and \(+\infty\) outside it, so minimizing \(x^2+4\) plus the indicator has the same minimizers.",
            r"The epigraph form minimizes \(t\) subject to \(x^2+4\ge t\) and \(x\le 3\).",
            r"For the epigraph form written with the inequality in the correct direction, the optimal \(t\) equals the optimal value of the original problem.",
        ],
        2,
        r"The objective and the half-line are both convex, and the indicator rewrite does not change the minimizers. The epigraph inequality runs the other way: \(t\) has to sit above \(x^2+4\), so the correct relation is \(x^2+4\le t\). With that direction, the optimal \(t\) is the optimal value. The step that reverses the inequality is the false one.",
        reasons=[
            "The epigraph requires t to sit above the objective, so the inequality is x^2+4 <= t.",
            "The indicator should be zero outside the set and infinite on it.",
            "The objective x^2+4 fails the chord test, so the problem is not convex.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Minimize \((x-6)^2+(y-2)^2\) subject to \(x+y=4\) by the substitution \(x=4-y\). What is the optimal value?",
        8, "(unitless)",
        r"The substitution produces \((4-y-6)^2+(y-2)^2=(y+2)^2+(y-2)^2=2y^2+8\). The square \(2y^2\) is smallest at \(y=0\), and the value there is 8. The matching \(x\) is 4, which is a decision, not the value. Stopping at the expression \(2y^2+8\) without minimizing leaves a function rather than the number 8. The unconstrained minimum of the original objective, ignoring \(x+y=4\), is 0 at \((6,2)\), and that point is not feasible.",
        preview=p,
    )
    b.mc(
        4,
        r"Why is the epigraph form useful once a problem is already known to be convex?",
        [
            r"It replaces the feasible set by the empty set.",
            r"It makes the Hessian the new objective.",
            r"It removes every constraint, including the epigraph inequality.",
            r"The objective becomes the scalar \(t\), and convexity sits in the inequality \(f(x)\le t\).",
        ],
        3,
        r"A linear objective is easy to recognize, and \(f(x)\le t\) describes a convex set exactly when \(f\) is convex. The feasible set is not emptied. The Hessian is a test for convexity, not the new objective. The epigraph inequality is a constraint; dropping it would leave \(t\) unbounded below.",
        preview=p,
    )
    b.save()


def bank_strong():
    b = Bank("strong-convexity")
    p = PREV["strong-convexity"]
    b.mc(
        1,
        r"Ordinary convexity says the graph lies above its tangents. Strong convexity with modulus \(m>0\) strengthens that statement by",
        [
            r"adding the bowl \(\tfrac{m}{2}\lVert y-x\rVert^2\) under the tangent",
            r"replacing the gradient by the zero vector",
            r"requiring the Hessian to be the zero matrix",
            r"subtracting \(\tfrac{m}{2}\lVert y-x\rVert^2\) from the tangent, so the lower model bends down",
        ],
        0,
        r"The first-order convexity inequality is the tangent underestimator. The strong form keeps that tangent and adds a quadratic bowl of curvature \(m\). Setting the gradient to zero is stationarity, a different statement. A zero Hessian is the boundary case \(m=0\), not a positive modulus. Subtracting the bowl bends the model the wrong way and is not a lower bound for a convex function.",
    )
    b.num(
        1,
        r"Let \(f(x,y)=2x^2+5y^2\). The Hessian is constant. What is the largest \(m\) such that \(f\) is \(m\)-strongly convex?",
        4, "(unitless)",
        r"The second derivatives are \(f_{xx}=4\), \(f_{yy}=10\), and the mixed derivative is 0, so the Hessian is \(\mathrm{diag}(4,10)\). The largest modulus is the smaller eigenvalue, which is 4. The larger eigenvalue 10 is an upper curvature, not the modulus. The sum 14 adds the two curvatures. The product 40 is not an eigenvalue.",
    )
    b.mc(
        1,
        r"A twice differentiable function has Hessian eigenvalues 2 and 9 at every point. Which statement is the strong-convexity test?",
        [
            r"The function is \(m\)-strongly convex only for \(m=9\).",
            r"The function is not strongly convex for any positive \(m\).",
            r"The function is \(m\)-strongly convex for every \(m\) with \(0<m\le 2\), and 2 is the largest such modulus.",
            r"The function is \(m\)-strongly convex for every \(m\ge 2\).",
        ],
        2,
        r"The Hessian test \(H_f\succeq m I\) holds for a positive modulus exactly when every eigenvalue is at least \(m\). Both 2 and 9 are at least \(m\) when \(0<m\le 2\). The largest such modulus is the smaller eigenvalue, 2. A nonpositive number is not a strong-convexity modulus. The eigenvalue 9 does not work as a modulus, because the other direction has curvature 2. Requiring \(m\ge 2\) selects moduli that are too large.",
    )
    b.order(
        2,
        r"Put these steps in the order that tests a candidate modulus of a twice differentiable function. Each step uses the matrix or the number produced by the step before it.",
        [
            "Compute the Hessian of the objective.",
            "Find the smallest eigenvalue of that Hessian.",
            "Compare the candidate modulus with that smallest eigenvalue.",
            "Accept the candidate only when it does not exceed the smallest eigenvalue.",
        ],
        r"The eigenvalue is a number computed from the Hessian, so the Hessian comes first. The comparison needs that eigenvalue. The accept-or-reject decision needs the comparison. Swapping an adjacent pair uses a matrix or a number that has not been computed yet.",
    )
    b.num(
        2,
        r"Let \(f(x,y)=2x^2+5y^2\), which is \(4\)-strongly convex and no more. From the base point \((0,0)\), what value does the quadratic lower model of curvature \(4\) take at \((1,2)\)?",
        10, "(unitless)",
        r"At the origin, \(f\) and \(\nabla f\) are both 0. The displacement \((1,2)\) has squared length \(1+4=5\). The bowl contributes \(\tfrac{4}{2}\cdot 5=10\). The true value \(f(1,2)=2+20=22\) lies above the model, so 22 is not the model. Using curvature 10, the larger eigenvalue, would contribute \(\tfrac{10}{2}\cdot 5=25\), which is not a lower model of modulus 4.",
    )
    b.num(
        2,
        r"The Hessian \(\begin{bmatrix} 7 & 1 \\ 1 & 7 \end{bmatrix}\) is constant. What is the largest strong-convexity modulus of the quadratic with this Hessian?",
        6, "(unitless)",
        r"The eigenvalues solve \((7-\lambda)^2-1=0\), so \(7-\lambda=\pm 1\). The roots are 8 and 6. The largest modulus is the smaller one, 6. The trace 14 is the sum of the eigenvalues. The diagonal entry 7 is their average. The larger root 8 is not a modulus the other direction can support.",
        HESS, AHESS,
    )
    b.sym(
        3,
        r"Let \(f(x)=\tfrac{a}{2}x^2\) with \(a>0\), so the second derivative is the constant \(a\). Write the quadratic lower model of curvature \(a\), based at \(p\) and evaluated at \(q\), as an expression in \(a\), \(p\), and \(q\).",
        "(a/2)*p**2 + a*p*(q-p) + (a/2)*(q-p)**2",
        {"a": (0.5, 3), "p": (-1.5, 1.5), "q": (-1.5, 1.5)},
        r"The model is \(f(p)+f'(p)(q-p)+\tfrac{a}{2}(q-p)^2\). Here \(f(p)=\tfrac{a}{2}p^2\) and \(f'(p)=ap\). Because the curvature of \(f\) is exactly \(a\), the expression simplifies to \(\tfrac{a}{2}q^2\), but the expanded model is the form the definition writes."
        "\n"
        r"• \(\tfrac{a}{2}p^2\) stops at the base value and never moves to \(q\)."
        "\n"
        r"• \(a(q-p)\) is only the linear term."
        "\n"
        r"• \(\tfrac{a}{2}(q-p)^2\) drops the tangent.",
        ["(a/2)*q**2", "a*q**2/2"],
    )
    b.mc(
        3,
        r"A function that is \(4\)-strongly convex is also",
        [
            r"not convex, because a positive modulus replaces the tangent test",
            r"\(m\)-strongly convex for every \(m\) with \(0<m\le 4\), and convex in the ordinary sense",
            r"\(9\)-strongly convex, because a larger modulus is a weaker demand",
            r"a quadratic, because only quadratics can be strongly convex",
        ],
        1,
        r"The inequality for modulus 4 includes the bowl of every smaller positive curvature, and the case \(m=0\) is ordinary convexity. A larger modulus is a stronger demand, so 9 need not hold. The exponential plus a square can be strongly convex without being a pure quadratic. The tangent test is kept and then strengthened; it is not replaced.",
    )
    b.multi(
        3,
        r"Which functions are \(2\)-strongly convex on the whole real line?",
        [
            r"\(f(x)=x^2\), whose second derivative is 2",
            r"\(f(x)=3x^2\), whose second derivative is 6",
            r"\(f(x)=\tfrac12 x^2\), whose second derivative is 1",
            r"\(f(x)=e^x\), whose second derivative is \(e^x\)",
        ],
        [0, 1],
        r"The Hessian test asks for a second derivative at least 2 everywhere. The second derivative 2 meets the test, and 6 exceeds it. The second derivative 1 falls short. The second derivative \(e^x\) drops below 2 for every negative enough \(x\), so that function is convex but not 2-strongly convex on the whole line.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The objective is \(f(x,y)=x^2+4y^2\).",
        [
            r"The Hessian is diagonal, with entries 2 and 8.",
            r"The smaller eigenvalue of that Hessian is 2.",
            r"Because the larger eigenvalue is 8, the largest strong-convexity modulus is 8.",
            r"The function is \(m\)-strongly convex for every positive \(m\) that does not exceed the smaller eigenvalue.",
        ],
        2,
        r"Differentiating twice gives a diagonal Hessian with entries 2 and 8, so the smaller eigenvalue is 2. A modulus has to fit every direction, including the direction of curvature 2. The larger eigenvalue is not a modulus. Every positive \(m\le 2\) does satisfy \(H_f\succeq m I\).",
        reasons=[
            "The modulus cannot exceed the smallest eigenvalue. The larger eigenvalue is not the strong-convexity modulus.",
            "The Hessian of x^2+4y^2 is not diagonal.",
            "The strong-convexity modulus is the sum of the eigenvalues.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Let \(f(x)=e^x+x^2\). Then \(f''(x)=e^x+2\ge 2\), so \(f\) is \(2\)-strongly convex. From the base point \(0\), what value does the quadratic lower model of curvature \(2\) take at \(1\)?",
        3, "(unitless)",
        r"\(f(0)=1\) and \(f'(0)=1\). The model is \(1+1\cdot(1-0)+\tfrac{2}{2}(1-0)^2=3\). The true value \(f(1)=e+1\) is larger than 3, which is what a lower model allows. Using the curvature \(e+2\) at \(x=1\) in place of the uniform modulus 2 would build a different, tighter model. The base value 1 alone forgets the tangent and the bowl.",
        preview=p,
    )
    b.mc(
        4,
        r"For a twice differentiable \(f\), why is \(H_f(x)\succeq m I\) at every \(x\) the same statement as \(m\)-strong convexity?",
        [
            r"Because the trace of the Hessian equals \(m\).",
            r"Because the gradient must be the zero vector.",
            r"Because the determinant of the Hessian equals \(m\).",
            r"Because \(v^T H_f(x) v\ge m\lVert v\rVert^2\) for every \(v\), which is the curvature form of the quadratic lower model.",
        ],
        3,
        r"The matrix inequality \(H_f-m I\succeq 0\) means every Rayleigh quotient of \(H_f\) is at least \(m\). That quadratic-form bound is the second-derivative version of adding \(\tfrac{m}{2}\lVert y-x\rVert^2\) under the tangent. The trace and the determinant are symmetric functions of the eigenvalues, not the smallest one. A zero gradient is stationarity, not a curvature bound.",
        preview=p,
    )
    b.save()


def bank_gd():
    b = Bank("gradient-descent")
    p = PREV["gradient-descent"]
    b.mc(
        1,
        r"The descent framework already separates a direction, a step length, and a stopping test. Fixed-step gradient descent chooses",
        [
            r"the direction \(-\nabla f(x)\) and one positive length \(t\) that stays the same at every iteration",
            r"the direction \(+\nabla f(x)\) and a positive length",
            r"the Newton direction \(-\,H_f(x)^{-1}\nabla f(x)\)",
            r"a random vector whose average equals \(-\nabla f(x)\)",
        ],
        0,
        r"The direction opposite the gradient has negative inner product with the gradient, so it is a descent direction. The length in this skill is a fixed positive number, not a line search and not a rate. Adding the gradient walks uphill. The Newton direction uses the Hessian. A random vector whose mean is the gradient is a later method.",
        STEP, ASTEP,
    )
    b.num(
        1,
        r"Let \(f(x)=(x-4)^2\). Take the fixed step length \(t=0.25\), and start at \(x=0\). What is the point after one gradient step?",
        2, "(unitless)",
        r"The derivative is \(2(x-4)\), so at \(0\) it equals \(-8\). The update subtracts \(0.25\cdot(-8)\) and lands at \(2\). Adding the gradient instead of subtracting it lands at \(-2\). The minimizer \(4\) is where the derivative is zero; one step of this length does not reach it. The derivative \(-8\) is not the next point.",
    )
    b.mc(
        1,
        r"Across iterations, what stays fixed, and what is recomputed?",
        [
            r"The gradient stays the same vector, and the length is recomputed from a line search.",
            r"Both the length and the gradient are frozen at their values from the first iteration.",
            r"The length stays the same positive number, and the gradient is recomputed at the new point.",
            r"The length must be \(1\), because a fixed step has no other legal value.",
        ],
        2,
        r"Fixed step means one chosen \(t>0\) is reused. The direction is the negative gradient at the current point, so the gradient changes whenever the point changes. A line search would recompute the length, which this skill does not do. Freezing the first gradient as well would walk in a straight line. The value of \(t\) may be any positive number; this skill does not set it from a smoothness constant.",
    )
    b.order(
        2,
        r"Put these steps in the order of one fixed-step gradient iteration, and of the handoff to the next iteration. Each step uses the vector or the point the previous step produced.",
        [
            "Evaluate the gradient at the current point.",
            "Multiply that gradient by the fixed positive step length.",
            "Subtract the product from the current point.",
            "Store the difference as the current point before any later gradient is evaluated.",
        ],
        r"The product needs the gradient. The subtraction needs the product. The stored point is that difference, and the next gradient is evaluated only after the store. Swapping an adjacent pair multiplies, subtracts, or stores a vector that has not been computed yet.",
    )
    b.num(
        2,
        r"Continue \(f(x)=(x-4)^2\) with the same fixed length \(t=0.25\). The first step from \(0\) landed at \(2\). What is the point after the second step?",
        3, "(unitless)",
        r"The derivative at \(2\) is \(2(2-4)=-4\). Subtract \(0.25\cdot(-4)\) from \(2\) to land at \(3\). The first landing \(2\) is not reused as the answer. The minimizer is still \(4\), and this length has not reached it. Adding the gradient at \(2\) would move from \(2\) to \(1\), which is uphill.",
    )
    b.num(
        2,
        r"Let \(f(x,y)=x^2+3y^2\), with gradient \((2x,6y)\). Start at \((1,1)\) and take one step of length \(0.25\). What is the second coordinate of the new point?",
        -0.5, "(unitless)",
        r"The second partial at \((1,1)\) is \(6\). The update subtracts \(0.25\cdot 6=1.5\) from \(1\), which lands at \(-0.5\). The first coordinate becomes \(1-0.25\cdot 2=0.5\), a different coordinate. The step length \(0.25\) is not a coordinate. Leaving the second coordinate at \(1\) would mean the second partial had been ignored.",
    )
    b.sym(
        3,
        r"Let \(f(x)=\tfrac{a}{2}x^2\) with \(a>0\). Start at \(s\) and take one gradient step of fixed length \(t>0\). Write the new point as an expression in \(a\), \(t\), and \(s\).",
        "s*(1-a*t)",
        {"a": (0.4, 1.5), "t": (0.1, 0.4), "s": (0.5, 2)},
        r"The derivative at \(s\) is \(a s\). Subtracting \(t\) times that derivative gives \(s-t a s\), which factors as \(s(1-at)\)."
        "\n"
        r"• \(s+at\) adds a length instead of subtracting the gradient."
        "\n"
        r"• \(s-t\) forgets that the gradient still carries the factor \(a s\)."
        "\n"
        r"• \(1-at\) drops the starting point.",
        ["s-t*a*s", "s-a*t*s"],
    )
    b.mc(
        3,
        r"At a point where \(\nabla f(x)\ne 0\), which vector is a descent direction for a differentiable \(f\)?",
        [
            r"\(\nabla f(x)\), because the gradient points toward the minimizer",
            r"\(-\nabla f(x)\), because its inner product with the gradient is negative",
            r"the zero vector, because a zero step is always feasible",
            r"\(H_f(x)\nabla f(x)\), for an arbitrary Hessian",
        ],
        1,
        r"A direction \(d\) is a descent direction when \(\nabla f(x)^T d<0\). The choice \(d=-\nabla f(x)\) gives \(-\lVert\nabla f(x)\rVert^2<0\) whenever the gradient is nonzero. The gradient itself has positive inner product with itself, so it is uphill. The zero vector has inner product 0, so it is not a descent direction. Multiplying by an arbitrary Hessian need not produce a negative inner product.",
    )
    b.multi(
        3,
        r"Which updates are fixed-step gradient descent on a differentiable objective?",
        [
            r"Subtract a constant positive length times the gradient at the current point.",
            r"Reuse that same positive length at every iteration, recomputing only the gradient.",
            r"Subtract a constant length times the inverse Hessian times the gradient.",
            r"Subtract a constant length times a random vector whose mean is the gradient.",
        ],
        [0, 1],
        r"The iteration is fully specified by the current gradient and one fixed positive length. Reusing that length is the fixed-step part. The inverse-Hessian product is a Newton step. A random vector whose mean is the gradient is not the gradient this skill subtracts.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The objective is \(f(x)=x^2\), the start is \(3\), and the fixed length is \(0.25\).",
        [
            r"The derivative at 3 is 6.",
            r"Multiplying that derivative by the step length produces 1.5.",
            r"The next point is 3+1.5, which equals 4.5.",
            r"The same length 0.25 is the length used at the following iteration.",
        ],
        2,
        r"The derivative of \(x^2\) at 3 is 6, and \(0.25\cdot 6=1.5\). The update subtracts that product, so the next point is \(3-1.5=1.5\). Adding it walks uphill, from 3 to 4.5. The length stays 0.25 at the next iteration; only the derivative is recomputed.",
        reasons=[
            "The update subtracts the step times the gradient. Adding it moves uphill, from 3 to 4.5.",
            "The derivative of x^2 at 3 is 3, so the first step is the one that fails.",
            "A fixed-step method recomputes the length from a line search at every iteration.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Let \(f(x,y)=(x-2)^2+2(y-1)^2\), with gradient \(\bigl(2(x-2),\,4(y-1)\bigr)\). Start at \((0,0)\) and take two steps of fixed length \(0.25\). What is the first coordinate after the second step?",
        1.5, "(unitless)",
        r"At \((0,0)\) the gradient is \((-4,-4)\), so one step lands at \((1,1)\). At \((1,1)\) the gradient is \((-2,0)\). Subtracting \(0.25\cdot(-2,0)\) moves the first coordinate from 1 to 1.5 and leaves the second coordinate at 1. The minimizer is \((2,1)\), which this length has not reached. The second coordinate after two steps is 1, not the coordinate this question asks for.",
        preview=p,
    )
    b.mc(
        4,
        r"This iteration is specified by the current gradient and one fixed positive length. Which claim stays inside that specification?",
        [
            r"The length must equal the reciprocal of a Lipschitz constant, or the iteration is not gradient descent.",
            r"Two steps are always enough to reach a minimizer.",
            r"The gradient is replaced by a random draw at every iteration.",
            r"Any fixed positive length defines the iteration. A guarantee that the objective decreases is a later fact, and it needs a bound this skill does not use.",
        ],
        3,
        r"Writing \(x_+=x-t\nabla f(x)\) with a constant \(t>0\) does not require a Lipschitz constant. That constant enters only when a later argument bounds the decrease. Nothing here says two steps finish the problem. A random draw in place of the gradient is a different iteration.",
        preview=p,
    )
    b.save()


def bank_sgd():
    b = Bank("stochastic-gradient-descent")
    p = PREV["stochastic-gradient-descent"]
    b.mc(
        1,
        r"Gradient descent subtracts a full gradient. A stochastic step replaces that gradient by a random vector \(g\). The draw is unbiased when",
        [
            r"the conditional expectation of \(g\) given the current point equals the full gradient",
            r"every draw equals the full gradient",
            r"the draw equals the Hessian times the gradient",
            r"the draw is unbiased only when it is orthogonal to the full gradient",
        ],
        0,
        r"Unbiased means the average of the random vector, at a fixed point, is the full gradient. Individual draws may point elsewhere. Requiring every draw to match the gradient removes the randomness. The Hessian product is a Newton ingredient. An orthogonal draw would have the wrong expectation unless the gradient is zero.",
    )
    b.num(
        1,
        r"At \(x=0\), the loss \((x-2)^2\) has derivative \(-4\) and the loss \((x-8)^2\) has derivative \(-16\). One of the two losses is drawn with equal probability, and the objective is their average. What is the expected value of the random derivative?",
        -10, "(unitless)",
        r"The expected draw is the average of the two derivatives, \((-4-16)/2=-10\). That matches the derivative of the average objective, \(2x-10\), at \(x=0\). The sum \(-20\) forgets to divide by two. Either single draw, \(-4\) or \(-16\), is a possible outcome, not the expectation.",
    )
    b.mc(
        1,
        r"The step length in this method, compared with the fixed length of gradient descent,",
        [
            r"grows at every iteration, so later noise is amplified",
            r"stays exactly equal to 1",
            r"shrinks from one iteration to the next, and stays positive",
            r"is recomputed by an exact line search on the full objective",
        ],
        2,
        r"A shrinking positive length multiplies later noisy draws by a smaller number. A growing length would amplify the noise. The length is not frozen at 1. An exact line search on the full objective would spend a full gradient, which is the cost this method avoids.",
    )
    b.order(
        2,
        r"Put these steps in the order of one stochastic iteration that uses the current length, then shrinks it. The subtraction uses the length from before the shrink.",
        [
            "Draw one data term.",
            "Evaluate that term's gradient at the current point.",
            "Subtract the current step length times that gradient from the current point.",
            "After that subtraction, replace the step length by half its value.",
        ],
        r"The gradient needs the term that was drawn. The subtraction needs that gradient and the length that is still current. Halving before the subtraction would feed the new length into this iteration, so the shrink comes after the subtraction. Swapping an adjacent pair evaluates, subtracts, or shrinks an object that is not ready.",
    )
    b.num(
        2,
        r"Start at \(x=0\) with step length \(0.5\). Draw the loss \((x-2)^2\), whose derivative at \(0\) is \(-4\). What is the point after this one stochastic step?",
        2, "(unitless)",
        r"The update subtracts \(0.5\cdot(-4)\) from \(0\), which lands at \(2\). The other loss has derivative \(-16\) at \(0\), and a step along that draw would land at \(8\). The expected derivative \(-10\) would land at \(5\), which is the full gradient step, not this draw. The derivative \(-4\) is not the next point.",
    )
    b.num(
        2,
        r"A stochastic step has just landed at \(x=2\), and the step length is now \(0.25\). Draw the loss \((x-8)^2\). Its derivative at \(2\) is \(2(2-8)\). What is the point after this step?",
        5, "(unitless)",
        r"The derivative is \(-12\). Subtract \(0.25\cdot(-12)\) from \(2\) to land at \(5\). Keeping the old length \(0.5\) would subtract \(0.5\cdot(-12)\) and land at \(8\). The derivative \(-12\) is not the next point. A full gradient at \(2\) is \(2\cdot 2-10=-6\), and a step of length \(0.25\) along \(-6\) would land at \(3.5\), a different update.",
    )
    b.sym(
        3,
        r"Two equally likely draws have values \(p\) and \(q\). Write the expected draw as an expression in \(p\) and \(q\).",
        "(p+q)/2",
        {"p": (-4, 4), "q": (-4, 4)},
        r"Equal probability means the expectation is the arithmetic mean. Both draws appear, and the factor one half is required."
        "\n"
        r"• \(p+q\) is the sum, twice the mean."
        "\n"
        r"• \(pq\) is a product, not an average."
        "\n"
        r"• \(p-q\) cancels the two draws instead of averaging them.",
        ["0.5*(p+q)", "(1/2)*(p+q)", "p/2+q/2"],
    )
    b.mc(
        3,
        r"A single draw differs from the full gradient, and the step taken along that draw increases the full objective. What does that event say?",
        [
            r"The draw was biased, because a descent method cannot increase the objective.",
            r"The draw can still be unbiased. Unbiasedness constrains the average of the draws, not each one, and one unlucky step can increase the full objective.",
            r"The full gradient was computed incorrectly, because every random draw decreases the objective.",
            r"The step length must have been zero.",
        ],
        1,
        r"Unbiasedness is a statement about the conditional expectation. One draw may point uphill for the full objective, especially when the length is not tiny. That event does not by itself show bias. It also does not show that the full gradient was miscomputed, and it does not force the length to be zero.",
    )
    b.multi(
        3,
        r"Which statements describe the random gradient and the step length in this method?",
        [
            r"The conditional expectation of the random gradient equals the full gradient.",
            r"A single draw can differ from the full gradient.",
            r"Every draw equals the full gradient.",
            r"The step length shrinks from one iteration to the next and stays positive.",
        ],
        [0, 1, 3],
        r"The expectation matches the full gradient, while a single draw need not. The length used here shrinks and stays positive. Requiring every draw to equal the full gradient describes ordinary gradient descent, not this method.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. At \(x=0\) the two equally likely derivatives are \(-4\) and \(-16\), and the full gradient is their average.",
        [
            r"Each draw is one of those two derivatives.",
            r"The expected draw is -10, which equals the full gradient.",
            r"A step of length 0.5 along the derivative -4 moves from 0 to 2.",
            r"Because the expected gradient is -10, every draw equals -10.",
        ],
        3,
        r"The two derivatives and their average \(-10\) are the unbiased pair, and the step along \(-4\) really does land at \(2\). The expectation does not force every draw to equal \(-10\). The draws \(-4\) and \(-16\) are the counterexamples sitting in the first step.",
        reasons=[
            "Unbiased means the average of the draws equals the full gradient. A single draw can be -4 or -16.",
            "The step along -4 does not land at 2.",
            "The expected gradient is the sum of the two draws, not the average.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"From \(x=0\) with length \(0.5\), the draw \(-4\) lands at \(2\) and the draw \(-16\) lands at \(8\). The two draws are equally likely. What is the average of the two possible next points?",
        5, "(unitless)",
        r"The average of the landings is \((2+8)/2=5\). The full gradient is \(-10\), and the full step \(0-0.5\cdot(-10)\) also lands at \(5\). That match is the unbiasedness of a step whose length is not random. The landing \(2\) is only one of the two outcomes. The sum \(10\) forgets to divide by two.",
        preview=p,
    )
    b.mc(
        4,
        r"A pass that always updates on block 1, then on block 2, using the updated point for the next block, is a different method. How does the random step here differ?",
        [
            r"It cycles through a fixed list and never draws at random.",
            r"It uses the full gradient on every iteration.",
            r"It requires the blocks to be visited in one fixed order.",
            r"It draws a term at random, with an expectation equal to the full gradient, instead of walking a fixed list in order.",
        ],
        3,
        r"The fixed cyclic pass is the incremental method. This method draws a term so that the conditional expectation equals the full gradient, and it shrinks the length. It does not commit to one order of blocks, and it does not evaluate the full gradient on every iteration.",
        preview=p,
    )
    b.save()


def bank_dual():
    b = Bank("strong-duality")
    p = PREV["strong-duality"]
    b.mc(
        1,
        r"The dual function is already a lower bound on the primal optimal value \(p^\star\). Strong duality is the case in which",
        [
            r"the maximum of the dual function equals \(p^\star\)",
            r"every dual value is strictly less than \(p^\star\)",
            r"the primal problem is infeasible",
            r"the dual function is identically zero",
        ],
        0,
        r"Weak duality says each dual value is at most \(p^\star\). Strong duality says the best dual value closes that gap. A gap that stays strict is the failure of strong duality. An infeasible primal has \(p^\star=+\infty\), which is not the definition. A zero dual function is one particular function, not the equality of the two optimal values.",
    )
    b.num(
        1,
        r"Minimize \((x-5)^2\) subject to \(x\le 1\). The unconstrained minimizer \(x=5\) is infeasible. What is the primal optimal value?",
        16, "(unitless)",
        r"On \(x\le 1\) the square \((x-5)^2\) is smallest at the endpoint \(x=1\), and the value is \(16\). The unconstrained value \(0\) is not feasible. The distance \(5-1=4\) is the amount the constraint moves the decision, not the objective value. The endpoint \(1\) is the minimizer, not the value.",
    )
    b.mc(
        1,
        r"For a convex problem with one inequality constraint, the relative-interior constraint qualification used here is",
        [
            r"a requirement that every feasible point be a minimizer",
            r"a requirement that the inequality be an equality at every feasible point",
            r"the existence of a point that satisfies the inequality strictly",
            r"a requirement that the dual function be nonconvex",
        ],
        2,
        r"Strict feasibility is the relative-interior condition for a single inequality: some point lies in the open side, not only on the boundary. It is a sufficient condition, together with convexity, for a zero gap. It does not say every feasible point is optimal, and it does not force the inequality to be tight everywhere. The dual function is concave by construction; the qualification does not ask it to be nonconvex.",
        HALF, AHALF,
    )
    b.order(
        2,
        r"Put these steps in the order that turns a strictly feasible convex problem into a reported dual maximum. Each step uses the conclusion or the number from the step before it.",
        [
            "Exhibit a point that satisfies the inequality strictly.",
            "Using that point together with convexity, conclude that the dual maximum equals the primal optimal value.",
            "Because those two optimal values are equal, evaluate the objective at a feasible minimizer and treat that number as the dual maximum.",
            "Check one allowed multiplier that is not the maximizer: its dual value lies strictly below the number from the previous step.",
        ],
        r"The zero-gap conclusion needs the strict point. Treating the primal value as the dual maximum needs that conclusion. The comparison with a non-optimal multiplier needs the common number. Swapping an adjacent pair cites a point, an equality, or a number that has not been established.",
    )
    b.num(
        2,
        r"Minimize \((x-5)^2\) subject to \(x\le 1\). Write the constraint as \(x-1\le 0\), so the Lagrangian is \((x-5)^2+\lambda(x-1)\) with \(\lambda\ge 0\). The dual function is \(4\lambda-\lambda^2/4\). What is the optimal multiplier?",
        8, "(unitless)",
        r"The derivative of \(4\lambda-\lambda^2/4\) is \(4-\lambda/2\), which is zero at \(\lambda=8\). The second derivative is negative, so this critical point is a maximum. The primal value is \(16\), and the dual function at \(8\) equals \(32-16=16\), the same number. The endpoint \(x=1\) is the primal minimizer, not the multiplier. The distance \(4\) is \(5-1\), and the multiplier is twice that distance.",
    )
    b.num(
        2,
        r"Minimize \((x-1)^2\) subject to \(x\ge 4\). The Lagrangian is \((x-1)^2+\lambda(4-x)\) with \(\lambda\ge 0\). Stationarity gives \(x=1+\lambda/2\), and the dual function is \(3\lambda-\lambda^2/4\). What is the optimal multiplier?",
        6, "(unitless)",
        r"The derivative \(3-\lambda/2\) is zero at \(\lambda=6\). The dual value there is \(18-9=9\), which equals the primal value \((4-1)^2=9\). The feasible endpoint \(4\) is the primal minimizer, not the multiplier. Using \(\lambda=3\), the coefficient in the linear term, does not set the derivative to zero.",
    )
    b.sym(
        3,
        r"Minimize \((x-a)^2\) subject to \(x\le b\), with \(a>b\). The optimal multiplier is a positive number that depends on \(a\) and \(b\). Write it as an expression in \(a\) and \(b\).",
        "2*(a-b)",
        {"a": (4, 7), "b": (0, 2)},
        r"The constraint \(x-b\le 0\) has Lagrangian \((x-a)^2+\lambda(x-b)\). Stationarity puts \(x=a-\lambda/2\). Substituting and maximizing the resulting quadratic in \(\lambda\) gives \(\lambda=2(a-b)\). The primal value \((a-b)^2\) is a different expression."
        "\n"
        r"• \(a-b\) is the distance, half of the multiplier."
        "\n"
        r"• \((a-b)^2\) is the primal optimal value."
        "\n"
        r"• \(a+b\) adds the two parameters.",
        ["2*a-2*b", "(a-b)*2"],
    )
    b.mc(
        3,
        r"A convex problem has a point that satisfies the inequality strictly. Which conclusion is justified?",
        [
            r"The duality gap is zero.",
            r"The gap must stay positive, because a strict point makes the constraint redundant.",
            r"Weak duality fails, so a dual value can exceed \(p^\star\).",
            r"The primal objective must be linear.",
        ],
        0,
        r"For a convex problem, a strictly feasible point is a sufficient constraint qualification for a zero gap. It does not cancel weak duality, and it does not force the objective to be linear. A strict point does not by itself make the constraint redundant; the minimizer may still lie on the boundary.",
    )
    b.multi(
        3,
        r"Which statements are true whenever strong duality holds?",
        [
            r"The dual maximum equals the primal minimum.",
            r"Every dual-feasible value is still at most the primal minimum.",
            r"Every feasible primal point is a minimizer.",
            r"The gap stays positive.",
        ],
        [0, 1],
        r"Strong duality is the equality of the two optimal values. Weak duality still says every dual value is a lower bound. The equality does not make every feasible point optimal, and it is the opposite of a gap that stays positive.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The problem is to minimize \((x-5)^2\) subject to \(x\le 1\). The point \(x=0\) satisfies the inequality strictly, the primal optimal value is \(16\), and the dual function is \(4\lambda-\lambda^2/4\).",
        [
            r"The point x=0 satisfies x<1, so a strictly feasible point exists.",
            r"The objective and the constraint are convex, so the gap is zero.",
            r"The dual maximum is therefore 16.",
            r"The multiplier 8 gives the dual value 8, so a gap of 8 remains.",
        ],
        3,
        r"The point \(x=0\) is strictly feasible, the problem is convex, and the gap is zero, so the dual maximum equals the primal value \(16\). At \(\lambda=8\) the dual function equals \(4\cdot 8-64/4=16\), not \(8\). The number \(8\) is the multiplier.",
        reasons=[
            "At multiplier 8 the dual function equals 16, the same as the primal value. The number 8 is the multiplier, not the dual value.",
            "The point x=0 is not strictly feasible.",
            "A convex problem with a strictly feasible point cannot have a zero gap.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Keep minimizing \((x-5)^2\) subject to \(x\le 1\), with dual function \(4\lambda-\lambda^2/4\) for \(\lambda\ge 0\). The optimal multiplier is \(8\). What is the dual value at the non-optimal multiplier \(\lambda=4\)?",
        12, "(unitless)",
        r"Substitute \(\lambda=4\): \(4\cdot 4-16/4=16-4=12\). This is a lower bound, and it is strictly below the primal value \(16\). The optimal dual value is \(16\), attained at \(\lambda=8\), not at \(\lambda=4\). The multiplier \(4\) is not the dual value. Reporting \(16\) evaluates the function at the maximizer instead of at \(4\).",
        preview=p,
    )
    b.mc(
        4,
        r"The gap is zero and both the primal minimum and the dual maximum are attained. A feasible point whose objective equals that common number is",
        [
            r"only a dual-feasible multiplier",
            r"infeasible by definition",
            r"a primal minimizer",
            r"a point where the objective equals twice \(p^\star\)",
        ],
        2,
        r"Any feasible point has objective at least \(p^\star\). If its objective equals \(p^\star\), it is a minimizer. The common number is not twice \(p^\star\). Matching \(p^\star\) does not by itself name a multiplier; the multiplier is the dual variable. The point was assumed feasible.",
        preview=p,
    )
    b.save()


def bank_conj():
    b = Bank("convex-conjugate")
    p = PREV["convex-conjugate"]
    b.mc(
        1,
        r"The conjugate of a function \(f\) at a slope \(y\) is",
        [
            r"\(\sup_x\bigl(y^T x-f(x)\bigr)\)",
            r"\(\inf_x\bigl(y^T x+f(x)\bigr)\)",
            r"the gradient \(\nabla f(y)\)",
            r"the Hessian of \(f\) at \(y\)",
        ],
        0,
        r"The conjugate is the supremum of slope-\(y\) linear functions minus \(f\). That is the largest intercept gap of an affine underestimator with slope \(y\). An infimum of \(y^T x+f(x)\) has the wrong sign and the wrong extremum. The gradient and the Hessian are derivatives of \(f\), not this supremum.",
        CONJ, ACONJ,
    )
    b.num(
        1,
        r"Let \(f(x)=x^2\). The conjugate is \(f^\star(y)=y^2/4\). What is \(f^\star(6)\)?",
        9, "(unitless)",
        r"The expression \(6x-x^2\) has derivative \(6-2x\), zero at \(x=3\). The value is \(18-9=9\), and \(6^2/4=9\). The critical point \(3\) is not the conjugate. The product \(6\cdot 3=18\) forgets to subtract \(x^2\). The square \(36\) forgets to divide by \(4\).",
    )
    b.mc(
        1,
        r"Let \(f(x)=\lvert x\rvert\). Its conjugate \(f^\star(y)\) is",
        [
            r"equal to \(\lvert y\rvert\) for every \(y\)",
            r"equal to \(0\) for every \(y\)",
            r"equal to \(0\) when \(\lvert y\rvert\le 1\), and \(+\infty\) when \(\lvert y\rvert>1\)",
            r"equal to \(y^2/4\) for every \(y\)",
        ],
        2,
        r"For \(\lvert y\rvert\le 1\), the expression \(yx-\lvert x\rvert\) is at most \(0\), and it equals \(0\) at \(x=0\). For \(\lvert y\rvert>1\), sending \(x\) to infinity in the sign of \(y\) makes the expression unbounded, so the supremum is \(+\infty\). The conjugate is not a copy of \(\lvert y\rvert\), and it is not the quadratic conjugate \(y^2/4\).",
    )
    b.order(
        2,
        r"Put these steps in the order that computes the conjugate of a smooth strictly convex \(f\) at a slope \(y\). Each step uses the expression or the critical point from the step before it.",
        [
            "Form the expression given by the slope times x, minus f(x).",
            "Set the derivative of that expression, with respect to x, equal to zero, and solve for x.",
            "Substitute that critical x back into the expression from the first step.",
            "Simplify the substitution. The simplified value is the conjugate at that slope.",
        ],
        r"The derivative is taken of the expression, so the expression comes first. The substitution needs the critical \(x\). The simplified value is the result of that substitution. Swapping an adjacent pair differentiates, substitutes, or simplifies an object that has not been built.",
    )
    b.num(
        2,
        r"Let \(f(x)=2x^2\). Then \(f^\star(y)=y^2/8\). What is \(f^\star(4)\)?",
        2, "(unitless)",
        r"The expression \(4x-2x^2\) has derivative \(4-4x\), zero at \(x=1\). The value is \(4-2=2\), and \(16/8=2\). The formula \(y^2/4\) belongs to the conjugate of \(x^2\), and it would report \(4\) here. The critical point \(1\) is not the conjugate.",
    )
    b.num(
        2,
        r"Let \(f(x)=e^x\). For \(y>0\) the conjugate is \(y\ln y-y\). What is \(f^\star(1)\)?",
        -1, "(unitless)",
        r"At \(y=1\), \(1\cdot\ln 1-1=0-1=-1\). The same value comes from maximizing \(x-e^x\): the derivative \(1-e^x\) is zero at \(x=0\), and the value is \(0-1=-1\). The number \(0\) is the critical \(x\), not the conjugate. The number \(1\) is the slope.",
    )
    b.sym(
        3,
        r"Let \(f(x)=\tfrac{a}{2}x^2\) with \(a>0\). The conjugate at the slope \(y\) is a quadratic in \(y\). Write \(f^\star(y)\) as an expression in \(a\) and \(y\).",
        "y**2/(2*a)",
        {"a": (0.5, 3), "y": (-3, 3)},
        r"Maximize \(yx-\tfrac{a}{2}x^2\). The critical point is \(x=y/a\), and the value is \(y^2/(2a)\)."
        "\n"
        r"• \(y^2/(2)\) drops \(a\)."
        "\n"
        r"• \(a y^2/2\) is \(f(y)\), not the conjugate."
        "\n"
        r"• \(y/a\) is the critical \(x\), not the supremum.",
        ["(y*y)/(2*a)", "y**2/2/a"],
    )
    b.mc(
        3,
        r"The indicator of the set \(\{0\}\) is \(0\) at \(x=0\) and \(+\infty\) elsewhere. Its conjugate is",
        [
            r"the zero function, because the supremum is taken only at \(x=0\) and the value there is \(0\)",
            r"\(+\infty\) at every slope, because the indicator is already infinite somewhere",
            r"the indicator of \(\{0\}\) again",
            r"the absolute value \(\lvert y\rvert\)",
        ],
        0,
        r"The supremum that defines the conjugate only sees the one point where the indicator is finite. At \(x=0\), \(y\cdot 0-0=0\) for every slope, so the conjugate is the zero function. Infinity elsewhere does not contribute to a supremum once a finite point exists. The conjugate of this indicator is not the indicator itself, and it is not an absolute value.",
    )
    b.multi(
        3,
        r"Let \(f(x)=x^2\), so \(f^\star(y)=y^2/4\). Which statements are true?",
        [
            r"\(f^\star(2)=1\).",
            r"\(f^\star(0)=0\).",
            r"\(f^\star(2)=2\).",
            r"\(f^\star(y)\) is finite for every real \(y\).",
        ],
        [0, 1, 3],
        r"\(2^2/4=1\) and \(0^2/4=0\). The value at slope \(2\) is not \(2\). A square over \(4\) is finite at every real slope. The conjugate of the absolute value is the function that becomes infinite; this quadratic is not that function.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The function is \(f(x)=x^2\), and the slope is \(6\).",
        [
            r"The expression inside the supremum is 6x-x^2.",
            r"Its derivative is 6-2x, which is zero at x=3.",
            r"The value at x=3 is 18-9, which equals 9.",
            r"The second derivative of 6x-x^2 is +2, so x=3 is a minimum and the conjugate is not 9.",
        ],
        3,
        r"The expression, the critical point \(x=3\), and the value \(9\) are correct. The second derivative of \(6x-x^2\) is \(-2\), so the critical point is a maximum. The conjugate equals that maximum, \(9\).",
        reasons=[
            "The second derivative of 6x-x^2 is -2, so x=3 is a maximum and the conjugate equals 9.",
            "The derivative 6-2x is zero at x=6, not at x=3.",
            "The value 18-9 equals 12, not 9.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Let \(f(x)=e^x\). For \(y>0\), \(f^\star(y)=y\ln y-y\). What is \(f^\star(2)\)?",
        2 * math.log(2) - 2, "(unitless)",
        r"Substitute the slope \(2\): \(2\ln 2-2\). The critical point of \(2x-e^x\) solves \(2=e^x\), so \(x=\ln 2\), and the value is \(2\ln 2-e^{\ln 2}=2\ln 2-2\). The number \(\ln 2\) is that critical \(x\), not the conjugate. The value at slope \(1\) is \(-1\), a different slope. Reporting \(2\) keeps only the slope.",
        preview=p,
    )
    b.mc(
        4,
        r"A dual function often equals a conjugate, up to a sign. Which reading matches that role?",
        [
            r"The conjugate replaces the primal objective by its gradient.",
            r"The conjugate is defined only for linear objectives, so a nonlinear \(f\) has no conjugate.",
            r"The conjugate is always the zero function.",
            r"Minimizing \(f(x)+s\, x\) over \(x\) produces a number that is the negative of a conjugate at the slope \(-s\).",
        ],
        3,
        r"The infimum of \(f(x)+s x\) equals \(-\sup_x\bigl((-s)x-f(x)\bigr)\), which is \(-f^\star(-s)\). That is why a dual function built from a Lagrangian can be a conjugate. The conjugate is not the gradient, it is defined for nonlinear \(f\), and it is not always zero.",
        preview=p,
    )
    b.save()


def bank_map():
    b = Bank("maximum-a-posteriori-estimation")
    p = PREV["maximum-a-posteriori-estimation"]
    b.mc(
        1,
        r"Maximum likelihood maximizes the density of the observations given the coefficient. Maximum a posteriori estimation changes that problem by",
        [
            r"multiplying the likelihood by a prior density and maximizing the product",
            r"dropping the observations and maximizing the residual",
            r"replacing the Gaussian noise by a deterministic constraint",
            r"minimizing the prior and ignoring the likelihood",
        ],
        0,
        r"The posterior mode maximizes likelihood times prior, or equivalently minimizes the sum of the two negative logs. Dropping the observations leaves only the prior. A deterministic constraint is a different model. Ignoring the likelihood is not the posterior.",
    )
    b.num(
        1,
        r"Two observations are \(2\) and \(4\). The noise variance and the prior variance are both \(1\), and the prior mean is \(0\). The penalty weight is the noise variance divided by the prior variance. What is the posterior mode?",
        2, "(unitless)",
        r"The weight is \(1/1=1\). The posterior mode is \((2+4)/(2+1)=2\). The maximum-likelihood estimate is the average \(3\), which drops the penalty. The mode of the zero-mean Gaussian prior is \(0\), the prior mean, and that number ignores the observations. The sum \(6\) is not divided by \(2+1\).",
    )
    b.mc(
        1,
        r"The noise variance is \(\sigma^2\) and the prior variance is \(\tau^2\). The ridge weight on a zero-mean prior is",
        [
            r"\(\tau^2/\sigma^2\)",
            r"\(\sigma^2+\tau^2\)",
            r"\(\sigma^2/\tau^2\)",
            r"\(\sigma\tau\)",
        ],
        2,
        r"The negative log of the Gaussian likelihood carries \(1/(2\sigma^2)\) on the residual, and the negative log of the prior carries \(1/(2\tau^2)\) on \(x^2\). Dividing through by \(1/(2\sigma^2)\) leaves the residual sum of squares plus \((\sigma^2/\tau^2) x^2\). The reciprocal ratio swaps the two variances. The sum and the product are different combinations.",
    )
    b.order(
        2,
        r"Put these steps in the order that builds the posterior mode for a Gaussian likelihood and a Gaussian prior. Each step uses the density or the expression from the step before it.",
        [
            "Write the Gaussian density of the observations given the coefficient.",
            "Multiply that density by the Gaussian prior density.",
            "Take the negative logarithm of the product, which adds a residual sum of squares to a squared penalty.",
            "Minimize that sum. The minimizer is the posterior mode, and the penalty weight is the noise variance divided by the prior variance.",
        ],
        r"The product needs the likelihood. The negative log needs the product. The minimization needs the sum that the negative log just produced, and the weight is read from that sum. Swapping an adjacent pair multiplies, transforms, or minimizes an expression that has not been built.",
    )
    b.num(
        2,
        r"Three observations are each equal to \(6\). The noise variance is \(4\) and the prior variance is \(1\), so the penalty weight is \(4\). The prior mean is \(0\). What is the posterior mode?",
        18 / 7, "(unitless)",
        r"The sum of the observations is \(18\), and there are \(3\) of them. The mode is \(18/(3+4)=18/7\). The maximum-likelihood estimate is \(6\), which is the average with a zero penalty. The prior mean \(0\) would be the mode only in the limit of an infinite penalty. Dividing \(18\) by \(4\) uses the penalty weight and forgets the three observations.",
    )
    b.num(
        2,
        r"The observations are again \(2\) and \(4\), the penalty weight is \(1\), and the prior mean is \(2\) rather than \(0\). The mode minimizes \((2-x)^2+(4-x)^2+(x-2)^2\). What is that mode?",
        8 / 3, "(unitless)",
        r"The closed form with a prior mean is \((\text{sum of observations}+\lambda\mu)/(n+\lambda)=(6+1\cdot 2)/(2+1)=8/3\). The zero-mean formula would divide \(6\) by \(3\) and report \(2\), dropping the prior mean. The average of the observations is \(3\), which is the maximum-likelihood estimate. The prior mean \(2\) alone ignores the observations.",
    )
    b.sym(
        3,
        r"The observations sum to \(s\), there are \(n\) of them, the penalty weight is \(v>0\), and the prior mean is \(0\). Write the posterior mode as an expression in \(s\), \(n\), and \(v\).",
        "s/(n+v)",
        {"s": (1, 12), "n": (1, 5), "v": (0.5, 3)},
        r"Stationarity of \(\sum(y_i-x)^2+v x^2\) is \(s-n x+v x=0\), so \(x=s/(n+v)\)."
        "\n"
        r"• \(s/n\) is the maximum-likelihood average, the case \(v=0\)."
        "\n"
        r"• \(s/v\) drops the observations' count."
        "\n"
        r"• \(n+v\) is the denominator, not the mode.",
        ["s/(v+n)", "(s)/(n+v)"],
    )
    b.mc(
        3,
        r"The prior mean is \(0\). What happens to the posterior mode as the prior variance tends to infinity, with the noise variance held fixed?",
        [
            r"The mode tends to \(0\), because a vague prior is a stronger penalty.",
            r"The mode tends to the maximum-likelihood estimate, because the penalty weight tends to \(0\).",
            r"The mode tends to infinity for every data set.",
            r"The likelihood is deleted from the problem.",
        ],
        1,
        r"The weight \(\sigma^2/\tau^2\) tends to \(0\) as \(\tau^2\) grows, so the ridge problem tends to ordinary least squares, which is the maximum-likelihood estimate. A vague prior is a weaker penalty, not a stronger one. The mode stays at the least-squares fit; it does not run off to infinity just because the prior widened. The likelihood remains the data term.",
    )
    b.multi(
        3,
        r"Which statements describe this Gaussian-prior posterior mode?",
        [
            r"The penalty weight equals the noise variance divided by the prior variance.",
            r"With prior mean \(0\), the mode minimizes the squared residual plus that weight times \(x^2\).",
            r"For every finite prior variance, the mode ignores the prior and equals the maximum-likelihood estimate.",
            r"A larger prior variance makes the penalty weight smaller.",
        ],
        [0, 1, 3],
        r"The weight is \(\sigma^2/\tau^2\), and the zero-mean objective is the ridge problem with that weight. Increasing \(\tau^2\) decreases the weight. A finite prior variance changes the estimate; only the infinite-variance limit recovers maximum likelihood.",
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The observations are \(2\) and \(4\), both variances are \(1\), and the prior mean is \(0\).",
        [
            r"The penalty weight is 1.",
            r"The ridge objective is (2-x)^2+(4-x)^2+x^2.",
            r"The minimizer is (2+4)/(2+1), which equals 2.",
            r"Maximum likelihood uses the same penalty, so its estimate is also 2.",
        ],
        3,
        r"The weight, the ridge objective, and the minimizer \(2\) are the posterior mode. Maximum likelihood drops the prior, so the penalty weight is \(0\) and the estimate is the average \((2+4)/2=3\).",
        reasons=[
            "Maximum likelihood drops the prior. The penalty weight is 0 and the estimate is the average, 3.",
            "The penalty weight is 2, not 1.",
            "The ridge minimizer of this objective is not 2.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Four observations are each equal to \(5\). The noise variance is \(4\), the prior variance is \(1\), and the prior mean is \(1\). The penalty weight is \(4\). What is the posterior mode?",
        3, "(unitless)",
        r"The sum of the observations is \(20\). With weight \(4\) and prior mean \(1\), the mode is \((20+4\cdot 1)/(4+4)=24/8=3\). The maximum-likelihood estimate is \(5\). The prior mean \(1\) alone ignores the data. The zero-mean formula would divide \(20\) by \(8\) and report \(2.5\), dropping the shift \(4\cdot 1\).",
        preview=p,
    )
    b.mc(
        4,
        r"For this linear model with Gaussian noise and a Gaussian prior, the posterior is Gaussian. Which point does the squared penalty compute?",
        [
            r"A point that is neither the posterior mode nor the posterior mean.",
            r"The posterior mean only, and the mode is a different point.",
            r"The maximum-likelihood estimate, for every finite prior variance.",
            r"The posterior mode, which coincides with the posterior mean because the posterior is Gaussian.",
        ],
        3,
        r"A Gaussian density is unimodal and symmetric, so its mode and its mean are the same point. The ridge solution is that point. A non-Gaussian prior could separate the mode from the mean; this prior does not. A finite prior variance moves the point away from the maximum-likelihood estimate.",
        preview=p,
    )
    b.save()


def bank_lasso():
    b = Bank("lasso-regression")
    p = PREV["lasso-regression"]
    b.mc(
        1,
        r"Ridge penalizes \(\lambda\lVert x\rVert^2\). The lasso replaces that penalty by",
        [
            r"\(\lambda\lVert x\rVert_1\), the penalty weight times the sum of absolute coordinates",
            r"\(\lambda\lVert x\rVert_2\), with the same squared objective as ridge",
            r"a penalty that is zero at every nonzero vector",
            r"the squared penalty on a subset of coordinates chosen in advance",
        ],
        0,
        r"The lasso objective in this skill is \(\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1\). The Euclidean norm without the square is a different penalty. A penalty that vanishes on nonzero vectors would not charge large coefficients. Dropping coordinates before fitting is a different restriction; the absolute penalty can produce zeros as an outcome.",
        BALLS, ABALLS,
    )
    b.num(
        1,
        r"The penalty weight is \(3\), and the coefficient vector is \((2,-1,0)\). What is the value of the absolute penalty \(\lambda\lVert x\rVert_1\), not including a residual?",
        9, "(unitless)",
        r"The sum of absolute coordinates is \(2+1+0=3\). Times the weight \(3\) this is \(9\). The squared Euclidean penalty would be \(3(4+1+0)=15\), which is the ridge penalty on the same vector. The count of nonzeros is \(2\), not the penalty. Forgetting the weight reports \(3\).",
    )
    b.mc(
        1,
        r"In the plane, the unit ball of the absolute-value norm is a diamond. Where do its corners sit?",
        [
            r"At the four points where both coordinates have absolute value \(1/2\).",
            r"On a circle of radius \(1\).",
            r"On the coordinate axes, at \((\pm 1,0)\) and \((0,\pm 1)\).",
            r"Only at the origin.",
        ],
        2,
        r"The diamond \(\lvert x_1\rvert+\lvert x_2\rvert\le 1\) meets the axes at \((\pm 1,0)\) and \((0,\pm 1)\), and those are the corners. Each of those points has a zero coordinate. The points \((\pm 1/2,\pm 1/2)\) are midpoints of the edges. The Euclidean ball is the disk, a different norm. The origin is the center, not a corner.",
        BALLS, ABALLS,
    )
    b.order(
        2,
        r"Put these steps in the order that scores two candidate coefficient vectors for \(\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1\). Each step uses the vector or the number from the step before it. The comparison is only a comparison; it does not claim either candidate is the minimizer.",
        [
            "Compute the residual at the first candidate.",
            "Square the Euclidean length of that residual.",
            "Add the penalty weight times the sum of absolute coordinates of the same candidate.",
            "Repeat those three operations at the second candidate, and keep the candidate whose total is smaller.",
        ],
        r"The squared length needs the residual. The penalty is added to that squared length. The comparison needs the first total before the second candidate can be judged against it. Swapping an adjacent pair squares, adds, or compares a number that has not been computed.",
    )
    b.num(
        2,
        r"Let \(A\) be the identity, \(b=(3,1/2)\), and \(\lambda=2\). The objective is \(\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1\). What is the objective at \(x=(3,0)\)?",
        6.25, "(unitless)",
        r"The residual is \((0,-1/2)\), and its squared length is \(1/4\). The absolute penalty is \(2\cdot 3=6\). The total is \(6.25\). The residual square \(0.25\) alone drops the penalty. The penalty \(6\) alone drops the residual. The point \((3,1/2)\) has residual \(0\) and penalty \(2\cdot 3.5=7\), a different candidate.",
    )
    b.num(
        2,
        r"Use the same identity design, the same \(b=(3,1/2)\), and the same weight \(\lambda=2\). What is the objective at \(x=(3,1/2)\)?",
        7, "(unitless)",
        r"The residual is zero, so the objective equals the absolute penalty \(2\bigl(3+1/2\bigr)=7\). The sparse candidate \((3,0)\) scores \(6.25\), which is smaller, but this question asks for the value at \((3,1/2)\). Reporting \(0\) keeps only the residual. Reporting \(3.5\) is the sum of absolute coordinates before the weight.",
    )
    b.sym(
        3,
        r"Let the penalty weight be \(\lambda\), written \(\mathrm{lam}\) in the answer box, and let \(u>0\) and \(v>0\). The coefficient vector is \((u,-v)\). Write the absolute penalty \(\mathrm{lam}\,\lVert x\rVert_1\), not the residual, as an expression in \(\mathrm{lam}\), \(u\), and \(v\).",
        "lam*(u+v)",
        {"lam": (0.5, 3), "u": (0.5, 4), "v": (0.5, 4)},
        r"Both coordinates are nonzero and the second is negative, so the sum of absolute values is \(u+v\). The weight multiplies that sum."
        "\n"
        r"• \(u+v\) drops the weight."
        "\n"
        r"• \(\mathrm{lam}(u-v)\) subtracts the coordinates instead of adding their absolute values."
        "\n"
        r"• \(\mathrm{lam}(u^2+v^2)\) is a squared penalty.",
        ["lam*u+lam*v", "(u+v)*lam"],
    )
    b.mc(
        3,
        r"A residual contour expands about the ordinary least-squares point until it first touches a diamond of the absolute penalty. A touch at a corner means",
        [
            r"every coordinate of the coefficient vector is nonzero",
            r"the coefficient vector at that corner has a zero coordinate",
            r"the absolute penalty was actually a squared penalty",
            r"the residual must be the zero vector",
        ],
        1,
        r"The corners of the diamond lie on the coordinate axes, so at least one coordinate is zero. A touch in the middle of an edge can have all coordinates nonzero. The diamond is the absolute penalty, not the disk of the squared penalty. The residual is zero only when the unconstrained least-squares point is already feasible for that penalty level, which a first touch at a corner does not require.",
    )
    b.multi(
        3,
        r"Which points are corners of the unit ball \(\lvert x_1\rvert+\lvert x_2\rvert\le 1\)?",
        [
            r"\((1,0)\)",
            r"\((0,-1)\)",
            r"\((1/2,1/2)\)",
            r"\((1,1)\)",
        ],
        [0, 1],
        r"The corners are the axis intercepts \((\pm 1,0)\) and \((0,\pm 1)\). The point \((1/2,1/2)\) lies in the middle of an edge: the absolute norm equals \(1\), but both coordinates are nonzero and the set is flat there. The point \((1,1)\) has absolute norm \(2\), so it lies outside the unit ball.",
        BALLS, ABALLS,
    )
    b.find_error(
        4,
        r"One step below is false. Select that step, and the reason it fails. The objective is \(\lVert x-b\rVert^2+\lVert x\rVert_1\) with \(b=(4,1)\), so the weight is \(1\) and \(A\) is the identity.",
        [
            r"At (4,0) the squared residual is 1 and the absolute penalty is 4, so the objective is 5.",
            r"At (4,1) the squared residual is 0 and the absolute penalty is 5, so the objective is 5.",
            r"The two candidates have the same objective value.",
            r"The tie means the diamond has no corners, so (4,0) is not a sparse vector.",
        ],
        3,
        r"Both candidates score \(5\), so they tie. A tie does not change the shape of the absolute-penalty ball. The vector \((4,0)\) still has a zero coordinate, and the diamond still has corners on the axes.",
        reasons=[
            "Equal objective values do not remove the corners of the diamond. The vector (4, 0) still has a zero coordinate.",
            "The objective at (4, 0) is 4, not 5.",
            "The squared residual at (4, 1) is 1, not 0.",
        ],
        correct_reason=0,
        preview=p,
    )
    b.num(
        4,
        r"Let \(A=\begin{bmatrix} 1 & 1 \\ 1 & 0 \end{bmatrix}\), \(b=(3,1)\), and \(\lambda=2\). The objective is \(\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1\). What is the objective at the sparse point \(x=(1,0)\)?",
        6, "(unitless)",
        r"\(Ax=(1,1)\), so the residual is \((2,0)\) and the squared length is \(4\). The absolute penalty is \(2\cdot 1=2\). The total is \(6\). The dense point \(x=(1,2)\) has residual \(0\) and penalty \(2\cdot 3=6\), also a total of \(6\), but this question asks for the sparse point. Reporting \(4\) drops the penalty. Reporting \(2\) drops the residual.",
        preview=p,
    )
    b.mc(
        4,
        r"This skill writes the penalized problem and reads sparsity off the corners of the absolute-penalty ball. Which task belongs to a later skill?",
        [
            r"Naming the objective \(\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1\).",
            r"Recognizing that a corner of the diamond has a zero coordinate.",
            r"Comparing the absolute penalty with the squared penalty of ridge.",
            r"Writing the subdifferential stationarity condition and reducing it, for orthonormal columns, to a thresholding map.",
        ],
        3,
        r"The objective, the corners, and the comparison with the squared penalty are this skill. The stationarity condition for the absolute penalty, and the thresholding map it becomes when the columns are orthonormal, are the later calculation. This skill stops at the problem and the geometry.",
        preview=p,
    )
    b.save()


def expl_reparam():
    sections = [
        {"heading": "The idea", "figure": BOWL, "figure_alt": ABOWL,
         "body_md": r"""Problem classes already say when an objective and a constraint set make a convex program. Convex functions already pass the chord test. This skill rewrites a problem so that those two facts are easier to see. Each rewrite keeps the optimal value. An indicator also keeps the same minimizers. The epigraph form adds a new variable, so its minimizer is a pair.

Three rewrites cover the skill. An affine change of variables \(x=By+d\) keeps convexity: a chord in the new variable maps to a chord in the old one, and the old objective lies under its chords. A nonlinear substitution need not. The absolute value of \(y^2-1\) sits above the chord that joins its zeros.

The epigraph form replaces "minimize \(f(x)\)" by "minimize \(t\) subject to \(f(x)\le t\)". The new objective is the scalar \(t\). Convexity of \(f\) becomes convexity of the inequality. Moving a constraint into the objective uses an indicator: \(0\) on the feasible set and \(+\infty\) outside it. Adding the indicator and dropping the explicit constraint leaves an unconstrained problem with the same minimizers."""},
        {"heading": "Key equations",
         "body_md": r"""Affine reparameterization: if \(f\) is convex then so is \(g(y)=f(By+d)\), for every matrix \(B\) and every vector \(d\). The epigraph form is
\[
\text{minimize } t \quad\text{subject to}\quad f(x)\le t.
\]
The indicator form of minimizing \(f\) over a set \(\mathcal{C}\) is the unconstrained problem of minimizing \(f(x)+I_{\mathcal{C}}(x)\). These three rewrites preserve the optimal value. They do not preserve it under an arbitrary nonlinear change of variables."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(f(w)=(w-15)^2+11\). The square is zero at \(w=15\), so the smallest value is 11. The epigraph form minimizes \(t\) subject to \((w-15)^2+11\le t\), and the optimal \(t\) is 11. The decision \(w=15\) is feasible for any constraint that contains 15, such as \(w\le 30\), so that constraint does not raise the value.

A different constraint does raise it. Minimize \((w-20)^2\) subject to \(w\ge 27\), by moving the ray into an indicator. The unconstrained minimizer \(w=20\) is outside the ray, where the indicator is infinite. On the ray the square is smallest at the endpoint \(w=27\). The value 49 is \((27-20)^2\), and the indicator contributes 0 there."""},
        {"heading": "Pitfalls",
         "body_md": r"""The epigraph inequality points up: \(t\) sits above \(f\), not under it. Reversing it makes the optimal \(t\) run to \(-\infty\).

An indicator is infinite outside the set, not inside it. Swapping those two values turns the feasible set into the place the objective refuses to go.

Affine reparameterization does not need an invertible map. A wide or a narrow \(B\) still preserves convexity. What fails is a nonlinear substitution, and even then only sometimes: the failure has to be checked, not assumed.

The new scalar \(t\) is the objective. Adding \(t\) to \(f\) without a constraint is a different and usually unbounded problem."""},
        {"heading": "Where this leads",
         "body_md": r"""A quadratic objective with affine constraints is a quadratic program once the rewrite has made that shape obvious. The epigraph is how a convex objective becomes a convex inequality under a linear objective. The same pattern later embeds quadratic constraints and second-order-cone constraints into a larger convex family. The indicator is the bridge from an explicit constraint to an unconstrained convex objective."""},
    ]
    save_explainer("convex-reparameterization", "Reparameterizing a convex problem", sections)


def expl_strong():
    sections = [
        {"heading": "The idea", "figure": BOWL, "figure_alt": ABOWL,
         "body_md": r"""Second-order convexity says the Hessian is positive semidefinite: the graph bends up, or at least does not bend down. Positive definite matrices are the test for a matrix that curves up in every direction. Strong convexity asks for a uniform amount of that upward bend.

The first-order picture starts from the tangent underestimator that ordinary convexity already gives. Strong convexity adds a bowl of curvature \(m>0\) under that tangent. The graph has to stay above the tangent plus \(\tfrac{m}{2}\lVert y-x\rVert^2\). A larger \(m\) is a stronger demand. Every smaller positive modulus remains valid, and the case \(m=0\) is ordinary convexity.

For a twice differentiable function the test is matrix-valued. The Hessian minus \(m I\) has to be positive semidefinite at every point. That is the same as asking the smallest eigenvalue of the Hessian to be at least \(m\). The largest legal \(m\) is that smallest eigenvalue, not the largest one."""},
        {"heading": "Key equations",
         "body_md": r"""The quadratic lower model of curvature \(m\) is
\[
f(y)\ge f(x)+\nabla f(x)^T(y-x)+\tfrac{m}{2}\lVert y-x\rVert^2.
\]
When \(f\) is twice differentiable this holds for every pair of points exactly when \(H_f(x)\succeq m I\) everywhere, equivalently \(\lambda_{\min}(H_f(x))\ge m\). A constant Hessian makes the test a single eigenvalue computation."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(t)=9t^2\). The second derivative is the constant 18, so the largest modulus is 18, and the lower model of that curvature is exact. From the base point \(1\) to the point \(2\), the function value is 9 and the derivative is 18. The model is
\[
9+18\cdot 1+\tfrac{18}{2}\cdot 1^2.
\]
That sum equals 36. The true value \(f(2)=9\cdot 4\) equals 36 as well, which is what an exactly quadratic function does when the modulus matches the second derivative. Using a modulus larger than 18 would put the model above \(f\), so it would no longer be a lower model."""},
        {"heading": "Pitfalls",
         "body_md": r"""The modulus is limited by the smallest eigenvalue. The largest eigenvalue is an upper curvature. Using it as \(m\) fails in the flat direction.

A function that meets the test for one modulus also meets it for every smaller positive modulus. The largest modulus is the most informative one, not the only legal one.

The lower model is not the function, unless the function is a quadratic whose Hessian is exactly \(m I\). When the Hessian is not a multiple of the identity, the model of curvature equal to the smallest eigenvalue lies strictly below the graph except along that flattest direction.

The exponential \(e^x\) is convex, but its second derivative tends to 0 as \(x\) goes to \(-\infty\), so no positive \(m\) works on the whole line."""},
        {"heading": "Where this leads",
         "body_md": r"""Convergence arguments for gradient methods use this modulus as the strong-convexity constant in a rate. This skill stops at the definition and the Hessian test. It does not choose a step length, and it does not claim a rate. The Lipschitz bound on the gradient is a different constant, an upper curvature, and it lives with the decrease estimates rather than here."""},
    ]
    save_explainer("strong-convexity", "Strong convexity", sections)


def expl_gd():
    sections = [
        {"heading": "The idea", "figure": STEP, "figure_alt": ASTEP,
         "body_md": r"""A general descent method already separates three choices: a direction, a positive step length, and a stopping test. Gradient descent makes the first two choices explicit and leaves the stopping test alone. The direction is the negative gradient at the current point. The length is one positive number, reused at every iteration.

The negative gradient is a descent direction whenever it is not zero, because its inner product with the gradient is minus the squared length of the gradient. Adding the gradient instead of subtracting it walks uphill. The gradient itself is recomputed after each step, because it belongs to the new point. The length is not recomputed.

This skill does not set the length from a Lipschitz constant, and it does not claim that the objective decreases by a stated amount. Those facts need a smoothness bound that is proved later. Any fixed positive length defines the iteration."""},
        {"heading": "Key equations",
         "body_md": r"""One step is
\[
x_+=x-t\nabla f(x), \qquad t>0.
\]
For \(f(x)=\tfrac{a}{2}x^2\) the derivative at a start \(s\) is \(a s\), so one step lands at \(s(1-at)\). In several variables the same formula subtracts \(t\) times the gradient vector, coordinate by coordinate. The Newton step, which multiplies by an inverse Hessian, is a different direction."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(u)=(u-8)^2\), start at \(15\), and take the fixed length \(1/6\). The derivative at \(15\) is \(2\cdot 7=14\). One step subtracts \((1/6)\cdot 14\) from \(15\). The next point is \(38/3\).

The minimizer is \(8\), where the derivative is zero. This single step does not land there. A second step would recompute the derivative at \(38/3\) and subtract the same length times that new derivative. Adding \(14/6\) instead of subtracting it would move from \(15\) to a point farther from \(8\)."""},
        {"heading": "Pitfalls",
         "body_md": r"""The sign is part of the method. Subtract the scaled gradient. The length \(t\) is positive; a negative length would flip the direction back uphill.

The length stays fixed. Recomputing it by a line search is a different method, even though the direction is still the negative gradient. Freezing the gradient as well as the length walks in a straight line and is not the iteration.

Do not import a rate. Two steps are not "enough" in general, and the length is not required to be the reciprocal of a Lipschitz constant. A random vector in place of the gradient is the stochastic method, not this one."""},
        {"heading": "Where this leads",
         "body_md": r"""The next change replaces the full gradient by an unbiased random draw and lets the length shrink. That is a different iteration, even though the algebra is still "subtract a vector times a length." A decrease bound for the fixed-step method needs a Lipschitz gradient and comes later. On a convex constraint set the same direction is followed by a projection, which is again a later method. The direction and the fixed length are the whole of this skill."""},
    ]
    save_explainer("gradient-descent", "Gradient descent", sections)


def expl_sgd():
    sections = [
        {"heading": "The idea", "figure": BOWL, "figure_alt": ABOWL,
         "body_md": r"""Gradient descent subtracts the full gradient and reuses one positive length. Stochastic gradient descent keeps the subtraction and changes both ingredients. The vector it subtracts is a random draw whose conditional expectation, given the current point, equals the full gradient. The length shrinks from one iteration to the next and stays positive.

Unbiased does not mean that every draw equals the full gradient. One draw can point a different way, and a step along that draw can increase the full objective. The guarantee is about the average of the draws. When the length is not itself random, the average of the possible next points equals the point a full gradient step would have reached.

The shrink is part of the method as defined here. A fixed length leaves the noise at full strength forever. This skill does not prove a rate for the shrinking schedule. It only requires that later steps use a smaller positive length."""},
        {"heading": "Key equations",
         "body_md": r"""If \(g\) is the random vector,
\[
\mathbb{E}[g\mid x]=\nabla f(x), \qquad x_+=x-t g, \qquad t>0,
\]
and the next iteration uses a smaller positive length. For two equally likely derivatives \(p\) and \(q\), the expected draw is \((p+q)/2\). That average is what must equal the full gradient. A pass that always visits a fixed list of blocks, in one order, is a different method: it does not draw."""},
        {"heading": "Worked example",
         "body_md": r"""At \(x=7\), the loss \((x-5)^2\) has derivative \(4\) and the loss \((x-11)^2\) has derivative \(-8\). The average of those two draws is \(-2\), which is the derivative of the averaged objective at \(7\).

Take the length \(0.1\). The first draw lands at \(7-0.1\cdot 4=6.6\). The second draw lands at \(7-0.1\cdot(-8)=7.8\). The average landing 7.2 equals the full gradient step \(7-0.1\cdot(-2)\). Neither landing equals \(7.2\) by itself. After the step, the length used on the next draw is smaller than \(0.1\)."""},
        {"heading": "Pitfalls",
         "body_md": r"""An increase in the full objective on one draw is not evidence of bias. Bias would mean the average of the draws, at a fixed point, differs from the full gradient.

Do not replace the average by the sum. Two equally likely numbers are averaged, not added. Do not replace the average by one of the draws and call that draw the expectation.

The cyclic pass over a fixed list uses the updated point for the next block and never flips a coin. Calling that pass a random gradient confuses the two methods. This method also does not keep the length fixed. The fixed length belongs to the full-gradient iteration."""},
        {"heading": "Where this leads",
         "body_md": r"""The neighbor is the incremental pass: the same subtraction, but the terms arrive in a fixed order rather than as an unbiased draw. Rates for the random method need a schedule whose lengths shrink in a controlled way, and those rates are not part of this skill. The full-gradient decrease bound does not apply unchanged, because that bound uses the true gradient at every step."""},
    ]
    save_explainer("stochastic-gradient-descent", "Stochastic gradient descent", sections)


def expl_dual():
    sections = [
        {"heading": "The idea", "figure": HALF, "figure_alt": AHALF,
         "body_md": r"""The Lagrangian dual already turns a constrained problem into a lower bound. For a multiplier that is allowed by the sign rule, the dual function is at most the primal optimal value \(p^\star\). That inequality is weak duality. Strong duality is the case in which the best lower bound equals \(p^\star\): the gap is zero.

A zero gap is not automatic. Convexity of the problem is part of the sufficient condition used here, and so is a constraint qualification. For one inequality, the qualification is relative interior in the simplest form: some point satisfies the inequality strictly, not only on the boundary. Together, convexity and that strict point force the dual maximum to equal \(p^\star\).

The condition is sufficient, not necessary. Failing to find a strict point does not by itself prove that a gap remains. Finding one, in a convex problem, does prove that the gap is zero."""},
        {"heading": "Key equations",
         "body_md": r"""Strong duality is \(\sup \theta = p^\star\), where \(\theta\) is the dual function. For
\[
\text{minimize }(x-a)^2 \quad\text{subject to}\quad x\le b,
\]
with \(a>b\), the optimal multiplier is \(2(a-b)\) and the common optimal value is \((a-b)^2\). A non-optimal multiplier still produces a dual value, and that value lies at or below \(p^\star\). Strict inequality there is weak duality at a multiplier that is not a maximizer."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \((x-7)^2\) subject to \(x\le 2\). The point \(x=0\) satisfies the inequality strictly, and both the objective and the half-line are convex, so the gap is zero. The primal minimizer on the half-line is the endpoint \(x=2\), and the primal value is \(25\).

The optimal multiplier is \(2(7-2)=10\). The dual function of this upper-bound constraint is \(5\lambda-\lambda^2/4\). At \(\lambda=10\) that expression equals \(50-25=25\). The dual value 25 matches the primal value. At a smaller multiplier the dual value drops below \(25\), which is a valid lower bound and not the maximum."""},
        {"heading": "Pitfalls",
         "body_md": r"""Do not confuse the multiplier with the dual value. The multiplier is the dual variable. The dual value is the number the dual function returns at that multiplier, and at the optimum that number equals \(p^\star\), not the multiplier itself.

A strict point is not the minimizer. It is only a witness that the inequality can be satisfied strictly. The minimizer of a square pulled toward a point outside a half-line still sits on the boundary.

Weak duality does not disappear when the gap is zero. Every dual value is still a lower bound. What changes is that the best one meets \(p^\star\).

The qualification used here is for a convex problem. A strict point in a nonconvex problem does not grant the same conclusion."""},
        {"heading": "Where this leads",
         "body_md": r"""Once the gap is zero and both sides attain their values, a feasible point whose objective equals that common number is a primal minimizer, and an optimal multiplier is a dual maximizer. Conic duality is the same equality in a problem whose constraint is membership in a cone: the dual constraint uses the dual cone. The zero-gap fact is the piece this skill contributes. The cone arithmetic is later."""},
    ]
    save_explainer("strong-duality", "Strong duality", sections)


def expl_conj():
    sections = [
        {"heading": "The idea", "figure": CONJ, "figure_alt": ACONJ,
         "body_md": r"""Convex functions lie above their tangents. A dual function is an infimum of a Lagrangian, and that infimum is often the best affine underestimator of a particular shape. The conjugate packages the same idea as a function of the slope.

At a slope \(y\), the conjugate is the supremum of \(y^T x-f(x)\). Rearranged, \(f(x)\ge y^T x-f^\star(y)\) for every \(x\). The right-hand side is an affine function of slope \(y\), and \(f^\star(y)\) is exactly large enough that the inequality holds everywhere. If the supremum is infinite, no finite affine function of that slope stays under the graph.

The calculus is a one-dimensional maximization when \(f\) is smooth and strictly convex. Differentiate \(yx-f(x)\) in \(x\), solve, and substitute. The second derivative in \(x\) has to be negative at that critical point, otherwise the critical point is not the supremum."""},
        {"heading": "Key equations",
         "body_md": r"""\[
f^\star(y)=\sup_x\bigl(y^T x-f(x)\bigr).
\]
For \(f(x)=\tfrac{a}{2}x^2\) with \(a>0\), the conjugate is \(y^2/(2a)\). For \(f(x)=e^x\) and \(y>0\), the conjugate is \(y\ln y-y\). For \(f(x)=\lvert x\rvert\), the conjugate is \(0\) on \([-1,1]\) and \(+\infty\) outside that interval. The infimum of \(f(x)+s x\) equals \(-f^\star(-s)\). That identity is why a dual function can be a conjugate."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(x)=5x^2\). The expression \(y x-5x^2\) has derivative \(y-10x\), zero at \(x=y/10\). Substituting that critical point produces \(y^2/20\). At the slope \(10\), the critical \(x\) is \(1\) and the value is \(100/20=5\).

The second derivative of \(yx-5x^2\) is \(-10\), so the critical point is a maximum and the value really is the conjugate. The formula \(y^2/4\) belongs to the conjugate of \(x^2\), not of \(5x^2\). Using it at slope \(10\) would report \(25\), five times the correct value."""},
        {"heading": "Pitfalls",
         "body_md": r"""The conjugate is a function of the slope, not the critical \(x\) that attains the supremum. Reporting that critical point answers a different question.

The second-derivative sign is easy to flip. The expression inside the supremum is linear minus \(f\). If \(f\) curves up, that expression curves down, and the critical point is a maximum.

A finite indicator does not make the conjugate infinite. The indicator of \(\{0\}\) is infinite almost everywhere, and its conjugate is the zero function, because the supremum only sees \(x=0\).

The conjugate of \(\lvert x\rvert\) is not \(\lvert y\rvert\). It is the function that is zero on the unit interval of slopes and infinite outside."""},
        {"heading": "Where this leads",
         "body_md": r"""Strong duality says the best dual value equals \(p^\star\). When the dual function is a conjugate, that statement becomes an equality between \(p^\star\) and a number computed from the conjugate. The computation in this skill is the supremum. The proof that the gap is zero stays with the constraint qualification."""},
    ]
    save_explainer("convex-conjugate", "Convex conjugates", sections)


def expl_map():
    sections = [
        {"heading": "The idea", "figure": PRIOR, "figure_alt": APRIOR,
         "body_md": r"""Maximum likelihood, for independent Gaussian noise of equal variance, is least squares: the maximizer of the likelihood is the minimizer of the squared residual. Ridge adds a squared penalty on the coefficient and solves the shifted normal equations. Maximum a posteriori estimation is the sentence that connects them.

Multiply the Gaussian likelihood by a Gaussian prior, and maximize the product. The maximizer is the posterior mode. With prior mean \(\mu\) and prior variance \(\tau^2\), and with noise variance \(\sigma^2\), the negative log of the product is a residual sum of squares plus a squared distance to \(\mu\). The weight on that distance is \(\sigma^2/\tau^2\).

When \(\mu=0\), the problem is ridge with that weight. A larger prior variance weakens the penalty and moves the mode toward the maximum-likelihood estimate. For this linear Gaussian model the posterior is Gaussian, so the mode and the mean are the same point."""},
        {"heading": "Key equations",
         "body_md": r"""With \(n\) observations that sum to \(s\), weight \(\lambda=\sigma^2/\tau^2\), and prior mean \(\mu\),
\[
x=\frac{s+\lambda\mu}{n+\lambda}.
\]
The zero-mean case is \(x=s/(n+\lambda)\). The maximum-likelihood estimate is the same formula with \(\lambda=0\). The objective being minimized is \(\sum_i(y_i-x)^2+\lambda(x-\mu)^2\). Both variances have to be positive for the weight to be defined and finite."""},
        {"heading": "Worked example",
         "body_md": r"""The observations are \(10\) and \(14\). The noise variance is \(1\) and the prior variance is \(2\), so the weight is \(1/2\). The prior mean is \(0\). The sum of the observations is \(24\), and
\[
x=\frac{24}{2+1/2}=\frac{24}{2.5}.
\]
That quotient equals 9.6. The maximum-likelihood estimate is the average \(12\), which is what the formula gives when the weight is \(0\). The prior pulls \(12\) toward \(0\), and it does not pull all the way to \(0\), because two observations still carry weight \(2\) against the penalty weight \(1/2\)."""},
        {"heading": "Pitfalls",
         "body_md": r"""The weight is noise variance over prior variance, not the reciprocal. A tight prior (small \(\tau^2\)) is a heavy penalty.

The prior mean enters as \(\lambda\mu\) in the numerator. Using the zero-mean formula when \(\mu\) is not zero drops that shift and pulls the mode toward the origin too far.

Maximum likelihood is not the posterior mode at a finite prior variance. It is the limit as the prior variance tends to infinity.

For a Gaussian posterior the mode and the mean coincide. That coincidence is special to this prior. It is not a reason to ignore the penalty."""},
        {"heading": "Where this leads",
         "body_md": r"""An absolute penalty is what appears when the prior's negative log is an absolute value rather than a square. The mode is then a lasso fit, and the geometry of that penalty can set coordinates exactly to zero. The likelihood term does not change: independent Gaussian noise of equal variance is still a squared residual. Only the prior changes. The corner geometry of the absolute penalty is the next objective, not a second derivation of this Gaussian case."""},
    ]
    save_explainer("maximum-a-posteriori-estimation", "Maximum a posteriori estimation", sections)


def expl_lasso():
    sections = [
        {"heading": "The idea", "figure": BALLS, "figure_alt": ABALLS,
         "body_md": r"""Ridge keeps a squared residual and adds \(\lambda\lVert x\rVert^2\). The unit ball of that penalty is a disk, smooth and without corners. The absolute-value ball is a diamond. The lasso puts that diamond into the fitting problem.

The objective is \(\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1\). The absolute penalty is \(\lambda\) times the sum of absolute coordinates. Its unit ball in the plane has corners on the axes, and each corner has a zero coordinate.

Expand a residual contour until it first touches a diamond of the penalty. A touch at a corner is a coefficient vector with a zero in it. That is the geometric reason an absolute penalty can return a sparse vector. A touch in the middle of an edge need not. The picture explains the preference. It does not, by itself, compute the minimizer."""},
        {"heading": "Key equations",
         "body_md": r"""\[
\lVert Ax-b\rVert^2+\lambda\lVert x\rVert_1, \qquad \lambda>0.
\]
At a stated vector the objective is the squared residual length plus \(\lambda\) times the sum of absolute coordinates. For \(x=(u,-v)\) with \(u>0\) and \(v>0\), the penalty term is \(\lambda(u+v)\). The squared penalty on the same vector would be \(\lambda(u^2+v^2)\), which is ridge, not the lasso. Comparing two candidates means scoring this sum at each of them. The smaller score is the better of those two, not necessarily the minimizer."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(A=\mathrm{diag}(3,3)\), \(b=(3,6)\), and \(\lambda=2\). At \(x=(1,0)\) the image \(Ax\) is \((3,0)\), so the residual is \((0,6)\) and the squared length is \(36\). The absolute penalty is \(2\cdot 1=2\). The objective equals 38.

At \(x=(1,2)\) the residual is zero and the absolute penalty is \(2\cdot 3=6\), so the objective is \(6\). The dense point scores better. A corner is a candidate the diamond makes available. It is not an automatic winner: here the residual saved by the second coordinate is worth more than the extra penalty. The unit-ball picture still says the corners are the sparse points. It does not say every problem's minimizer is a corner at every penalty weight."""},
        {"heading": "Pitfalls",
         "body_md": r"""Do not square the coordinates inside an absolute penalty, and do not drop the weight. The squared penalty is ridge. Forgetting the weight reports only the sum of absolute coordinates.

A tie between a sparse candidate and a dense candidate does not remove the corners of the diamond. Equal scores mean the two vectors are equally good. The sparse one is still sparse.

Edge midpoints of the unit diamond lie on the boundary and are not corners. This objective has no leading one half on the residual. Inserting one would rescale the penalty relative to a later stationarity formula."""},
        {"heading": "Where this leads",
         "body_md": r"""Stationarity for the absolute penalty uses a subdifferential, because the absolute value is not differentiable at zero. When the columns of \(A\) are orthonormal, that stationarity condition reduces to a thresholding map. The threshold and the subdifferential are the later skill. Coordinate descent is a different follow-up: it minimizes in one coordinate at a time, which fits an absolute penalty that separates across coordinates. Both of those calculations start from the objective written here."""},
    ]
    save_explainer("lasso-regression", "Lasso regression", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    publish_graph()
    bank_reparam()
    bank_strong()
    bank_gd()
    bank_sgd()
    bank_dual()
    bank_conj()
    bank_map()
    bank_lasso()
    expl_reparam()
    expl_strong()
    expl_gd()
    expl_sgd()
    expl_dual()
    expl_conj()
    expl_map()
    expl_lasso()
    banned = (
        "boyd", "nocedal", "vandenberghe", "textbook", "university", "professor",
        "lecture", "syllabus", "berkeley", "stanford", "slater", "fenchel",
        "tibshirani",
    )
    private = {
        "convex-reparameterization": "value 49",
        "strong-convexity": "equals 36",
        "gradient-descent": "38/3",
        "stochastic-gradient-descent": "average landing 7.2",
        "strong-duality": "dual value 25",
        "convex-conjugate": "y^2/20",
        "maximum-a-posteriori-estimation": "equals 9.6",
        "lasso-regression": "equals 38",
    }
    bad = False
    for sid in IDS:
        exp = json.load(open(os.path.join(ROOT, "skilltree", "explainers", sid + ".json"), encoding="utf-8"))
        bank = json.load(open(os.path.join(ROOT, "skilltree", "bank", sid + ".json"), encoding="utf-8"))
        n = doc_words(exp["sections"])
        blob = json.dumps(exp) + json.dumps(bank)
        hits = [w for w in banned if w in blob.lower()]
        deep = sum(1 for q in bank["questions"] if q.get("type") in DEEP_TYPES)
        print(f"{sid}: words {n}, deep {deep}/12")
        if not 250 <= n <= 500:
            print("  word count outside 250-500")
            bad = True
        if hits:
            print("  banned", hits)
            bad = True
        if deep < deep_quota(12):
            print("  deep-type quota miss")
            bad = True
        if private[sid] not in json.dumps(exp):
            print("  worked-example marker missing", private[sid])
            bad = True
        if private[sid] in json.dumps(bank):
            print("  worked example reused in the bank")
            bad = True
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
