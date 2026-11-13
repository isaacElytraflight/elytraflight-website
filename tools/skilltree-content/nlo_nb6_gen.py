#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB6 banks and explainers.

Skills: lp-standard-form, lp-graphical-solution, polyhedra-extreme-points,
basic-feasible-solutions, simplex-feasible-directions, simplex-method-iteration,
simplex-phase-one.

Closed-form answers live here. skilltree/verify_nlo_nb6.py recomputes the
numeric ones from the same definitions and does not import this file.
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import DEEP_TYPES, Bank, deep_quota, save_explainer
from templates import (
    dented_quad_fig,
    halfspace_fig,
    matrix_fig,
    orthant_fig,
    plane_vectors,
    plot,
    segment_fig,
    simplex_fig,
)

FALL = plot(lambda t: 1.55 - 0.42 * t, 0.0, 2.6, "t", "z", "a line sloping down")
A_FALL = "A straight line sloping downward on labeled axes."
RISE = plot(lambda t: 0.35 * t + 0.45, 0.0, 2.6, "t", "z", "a line sloping up")
A_RISE = "A straight line sloping upward on labeled axes."
HALF = halfspace_fig("a half-plane")
A_HALF = "A straight boundary with one side shaded."
ORTH = orthant_fig("the first quadrant")
A_ORTH = "The closed first quadrant, shaded."
SEG = segment_fig("a segment")
A_SEG = "A solid segment joins two marked points on a dashed line."
SIMP = simplex_fig("a segment in the first quadrant")
A_SIMP = "A segment joining two marked points on the axes."
DENT = dented_quad_fig("a dented quadrilateral")
A_DENT = "A four-sided region with one corner pushed in."
ARR = plane_vectors([(1.15, 0.35, "d")], "one arrow from the origin")
A_ARR = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.05, 0.2, "c"), (-0.35, 0.95, "d")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."
BASIS = matrix_fig([["b", "n"], ["1", "0"]], "a two-column array")
A_BASIS = "A small array with two short rows of labels."

P_STD = ["lp-graphical-solution"]
P_POLY = ["polyhedra-extreme-points"]
P_DUAL = ["lp-duality-kkt"]
P_BFS = ["basic-feasible-solutions"]
P_DIR = ["simplex-feasible-directions"]
P_IT = ["simplex-method-iteration"]
P_PH = ["simplex-phase-one"]
P_FW = ["frank-wolfe-conditional-gradient"]
P_AFF = ["affine-scaling-method"]
P_IP = ["primal-dual-interior-point"]


def bank_standard():
    b = Bank("lp-standard-form")
    b.mc(
        1,
        "Standard form of a linear program is",
        [
            r"maximize \(c^T x\) subject to \(Ax \le b\), with \(x\) free",
            r"minimize \(c^T x\) subject to \(Ax \le b\), with \(x\) free",
            r"minimize \(c^T x\) subject to \(Ax = b\) and \(x \ge 0\)",
            r"minimize \(c^T x\) subject to \(Ax = b\), with \(x\) free",
        ],
        2,
        r"Standard form minimizes a linear cost, forces every constraint to be an equality, and keeps every variable nonnegative. A maximization is the same geometry only after the cost is replaced by its negative, so leaving the word maximize does not match the form. Inequalities are not yet equalities, and a free variable is not yet a nonnegative variable. Both of those are rewritten before the form is standard.",
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        1,
        r"A loader minimizes \(5x - 2y\) subject to \(x + y \le 9\) and \(2x + y \ge 4\), with \(x\) free and \(y \ge 0\). How many nonnegative variables does the standard form use?",
        5,
        "1",
        r"The free variable splits as \(x = u - v\) with \(u, v \ge 0\). The upper bound takes one slack and the lower bound takes one surplus. Together with \(y\), that is five nonnegative variables: \(u\), \(v\), \(y\), the slack, and the surplus. Reporting 2 counts only the original names. Reporting 3 forgets the slack and the surplus. Reporting 4 drops either the split or one of the inequality variables.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        1,
        "A variable that is allowed to be positive or negative is brought into standard form by",
        [
            r"writing it as \(u - v\) with \(u \ge 0\) and \(v \ge 0\)",
            "replacing it by its absolute value inside the cost",
            "adding a slack and leaving the variable free",
            "squaring it so the model stays linear",
        ],
        0,
        r"The difference of two nonnegative variables can represent any real number, and both new variables fit the nonnegative requirement. The absolute value is not linear, so dropping it into the cost leaves the program. A slack converts an inequality; it does not remove the freedom of a variable. Squaring produces a quadratic constraint or cost, which is no longer a linear program.",
        fig=SEG,
        alt=A_SEG,
    )
    b.order(
        2,
        "Put these steps in the order of one conversion into standard form. Each step uses the result of the step before it.",
        [
            "Replace a maximization by minimizing the negative of the objective, before changing any constraint.",
            "With the objective now a minimization, add a nonnegative slack to each remaining upper-bound inequality.",
            "With those upper bounds converted, subtract a nonnegative surplus from each remaining lower-bound inequality.",
            "With every constraint now an equality, replace each free variable by a difference of two nonnegative variables.",
        ],
        r"The sense of the optimization is fixed first, because the standard form is a minimization. Upper bounds are converted next, and the following step refers to those converted bounds, so it cannot come earlier. Lower bounds are then converted by a surplus. Only after every constraint is an equality does the procedure split free variables, because that step is stated to act on the resulting equalities. Splitting a variable before the inequalities are written changes names in constraints that are about to be rewritten anyway, and this procedure does that rewrite first.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        "Which of these programs are already in standard form?",
        [
            r"Minimize \(2x + y\) subject to \(x + y = 3\), \(x \ge 0\), \(y \ge 0\).",
            r"Maximize \(x + y\) subject to \(x + y = 3\), \(x \ge 0\), \(y \ge 0\).",
            r"Minimize \(x\) subject to \(x + y \le 3\), \(x \ge 0\), \(y \ge 0\).",
            r"Minimize \(x - y\) subject to \(x + y = 4\), \(x \ge 0\), and \(y\) free.",
            r"Minimize \(3u + v\) subject to \(u + v = 1\), \(u \ge 0\), \(v \ge 0\).",
        ],
        [0, 4],
        r"Standard form is a minimization, with every constraint an equality and every variable nonnegative. The first program and the last program match that list."
        "\n"
        r"• A maximization is not standard until the cost is negated."
        "\n"
        r"• An inequality is not an equality until a slack or a surplus is introduced."
        "\n"
        r"• A free variable is not nonnegative until it is split.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.mc(
        2,
        r"The inequality \(\lvert 2x - y \rvert \le 6\) is equivalent to which linear description?",
        [
            r"\(2x - y = 6\)",
            r"\(2x - y \le 6\) alone",
            r"\((2x - y)^2 \le 36\), kept as a quadratic inequality",
            r"\(2x - y \le 6\) and \(-2x + y \le 6\)",
        ],
        3,
        r"The absolute value is at most 6 exactly when the expression sits between \(-6\) and \(6\). Those two linear inequalities are the standard-form material: each then receives its own slack. Forcing equality keeps only the upper endpoint. One inequality leaves the lower side open, so \(2x - y = -7\) would still look acceptable. The squared form is equivalent as a set, and it is not linear.",
        fig=HALF,
        alt=A_HALF,
    )
    b.find_error(
        3,
        r"A note converts \(\min -x + 3y\) subject to \(x + 2y \le 8\), \(x - y \ge 1\), with \(x\) free and \(y \ge 0\). Exactly one step is false. The split is \(x = u - v\).",
        [
            r"The objective becomes \(-u + v + 3y\).",
            r"The upper bound becomes \(u - v + 2y + s = 8\) with \(s \ge 0\).",
            r"The lower bound becomes \(u - v - y + t = 1\) with \(t \ge 0\).",
            r"The variables \(u, v, y, s, t\) are all required to be nonnegative.",
        ],
        2,
        r"Negating the split gives \(-x = -(u - v) = -u + v\), so the objective line is right. An upper bound gains a slack, and the sign in front of \(s\) is right. Every new variable in this conversion is nonnegative, including both pieces of \(x\). The false step is the lower bound. A surplus is subtracted, so the equality is \(u - v - y - t = 1\). Writing \(+ t\) lets \(t\) push the left side up and encodes the wrong direction.",
        [
            r"A surplus is subtracted, so the lower bound is \(u - v - y - t = 1\).",
            r"The objective sign on \(v\) is the part that is wrong.",
            "The slack on the upper bound should have been subtracted.",
        ],
        0,
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        3,
        r"The inequality \(4x + y \le 11\) is written with a slack. At \((x, y) = (1, 3)\), what is that slack?",
        4,
        "1",
        r"The slack is the unused room \(11 - 4x - y\). At the given point, \(4 \cdot 1 + 3 = 7\), so the slack is \(11 - 7 = 4\). Reporting 7 gives the left-hand side, which is data of the point, not the slack. Reporting 11 gives the right-hand side. Reporting 1 gives a coordinate.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.sym(
        3,
        r"An inequality \(a x + b y \le p\) is written with a slack. Using the names \(a, x, b, y, p\), that slack equals",
        "p-a*x-b*y",
        {"a": (1, 2), "x": (1, 2), "b": (1, 2), "y": (1, 2), "p": (20, 30)},
        r"The slack is defined by moving the left-hand side to the other side of the inequality: it equals \(p - a x - b y\), and the equality form is \(a x + b y + s = p\). On the declared ranges the slack stays positive, which is the feasible side of this one inequality. Subtracting \(p\) instead, or adding the left-hand side to \(p\), measures the wrong gap. Leaving out one term forgets part of the linear form.",
        alternates=["p-(a*x+b*y)", "-a*x-b*y+p"],
        fig=HALF,
        alt=A_HALF,
    )
    b.mc(
        4,
        r"Maximize \(x + 2y\) subject to \(x + y \le 5\) and \(x, y \ge 0\). Which system is the standard form?",
        [
            r"Minimize \(x + 2y\) subject to \(x + y + s = 5\), all variables nonnegative.",
            r"Minimize \(-x - 2y\) subject to \(x + y + s = 5\), all variables nonnegative.",
            r"Minimize \(-x - 2y\) subject to \(x + y - s = 5\), all variables nonnegative.",
            r"Maximize \(x + 2y\) subject to \(x + y + s = 5\), all variables nonnegative.",
        ],
        1,
        r"The maximization becomes the minimization of \(-x - 2y\). The upper bound receives a slack, so the equality is \(x + y + s = 5\), and \(x, y, s \ge 0\). Keeping the original cost minimizes the wrong direction. A minus in front of the slack is a surplus and encodes \(x + y \ge 5\). Leaving the word maximize means the form is not standard, even though the slack equation is right.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_STD,
    )
    b.num(
        4,
        r"Maximizing \(6x + y\) is rewritten as a minimization of \(-6x - y\). At \((x, y) = (2, 3)\), what is that standard-form objective?",
        -15,
        "1",
        r"The original objective at the point is \(6 \cdot 2 + 3 = 15\). Standard form minimizes the negative, so the value is \(-15\). Reporting 15 keeps the maximization's number. Reporting 12 or 3 reports a product or a coordinate, not the rewritten objective. The feasible set is not involved: the objective value is a property of the point.",
        fig=FALL,
        alt=A_FALL,
        preview=P_POLY,
    )
    b.mc(
        4,
        "One inequality of a linear program receives, in the conversion to standard form,",
        [
            "both a slack and a surplus, so the equality can slide either way",
            "no extra variable, because an inequality is already allowed",
            "either one slack or one surplus, matching the direction of the inequality",
            "a free variable split, whether or not the original variable was free",
        ],
        2,
        r"An upper bound is an equality plus one slack. A lower bound is an equality minus one surplus. Using both on the same inequality adds a redundant degree of freedom and is not the conversion. Leaving the inequality as it stands is a general form, not standard form. A free-variable split is for a variable, not for an inequality.",
        fig=SEG,
        alt=A_SEG,
        preview=P_DUAL,
    )
    b.save()


def bank_graphical():
    b = Bank("lp-graphical-solution")
    b.mc(
        1,
        "A linear program in the plane is infeasible when",
        [
            "the level lines of the objective are parallel to an edge",
            "the intersection of the constraint half-planes is empty",
            "the feasible set is unbounded",
            "two vertices share the same objective value",
        ],
        1,
        r"Infeasible means there is no point that satisfies every constraint at once, so the painted intersection is empty. Parallel level lines are the pattern of a linear objective and do not decide feasibility. An unbounded set can still contain optimal points, as a half-strip does for a cost that points back toward the strip. A tie between two vertices means more than one minimizer, and the program is feasible.",
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        1,
        r"Minimize \(x + y\) on the parallelogram with vertices \((1, 2)\), \((5, 1)\), \((6, 4)\), and \((2, 5)\). What is the optimal value?",
        3,
        "1",
        r"The vertex values are \(1 + 2 = 3\), \(5 + 1 = 6\), \(6 + 4 = 10\), and \(2 + 5 = 7\). A linear objective on a polygon attains its minimum at a vertex, so the optimal value is 3, at \((1, 2)\) only. Reporting 10 gives the maximum. Reporting 6 or 7 gives another vertex. Reporting 1 or 2 reports a coordinate.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.mc(
        1,
        r"On that same parallelogram, \(x + 4y\) equals 9 at both \((1, 2)\) and \((5, 1)\), and equals 22 at the other two vertices. A minimizer of \(x + 4y\) is",
        [
            r"only the vertex \((1, 2)\)",
            r"only the vertex \((5, 1)\)",
            r"every point of the edge joining \((1, 2)\) and \((5, 1)\)",
            "every point of the parallelogram",
        ],
        2,
        r"The two vertices of that edge tie for the smallest value, and the level line of a linear objective through both of them contains the whole edge. Every point of the edge is a minimizer, and the optimal value is still the single number 9. Neither endpoint is the only minimizer. The opposite edge has value 22, so the rest of the parallelogram is worse.",
        fig=SEG,
        alt=A_SEG,
    )
    b.order(
        2,
        "Put these steps in the order used to classify a planar linear program from a sketch.",
        [
            "Sketch every constraint half-plane and mark their intersection.",
            "If that intersection is empty, stop and report that the program is infeasible.",
            "Only after the intersection is known to be nonempty, draw one level line and an arrow toward smaller objective values.",
            "Move the line in the arrow's direction: an endless move means unbounded, and the last contact otherwise gives the optimal value.",
        ],
        r"The feasible set is the picture you are allowed to land on, so it is drawn first. Emptiness is checked next, because an empty intersection has no contact point to read. The level line is drawn only after that check, which is what the third step says. The slide comes last: it needs both a nonempty set and a direction. Reading a vertex before drawing the set has nothing to read.",
        fig=HALF,
        alt=A_HALF,
    )
    b.multi(
        2,
        r"On the parallelogram with vertices \((1, 2)\), \((5, 1)\), \((6, 4)\), and \((2, 5)\), which statements about \(x + 4y\) hold?",
        [
            "The minimum value is 9.",
            r"Every point of the edge from \((1, 2)\) to \((5, 1)\) is a minimizer.",
            r"\((6, 4)\) is a minimizer.",
            "The program is unbounded.",
            "The maximum value is 22.",
        ],
        [0, 1, 4],
        r"The vertex values are 9, 9, 22, and 22. The minimum is 9 and it is attained along the whole edge where the level line lies. The maximum is 22, attained along the opposite edge. The polygon is bounded, so the program is not an unbounded ray."
        "\n"
        r"• \((6, 4)\) has value 22, which is the maximum, not the minimum.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.num(
        2,
        r"Minimize \(x - 2y\) on the parallelogram with vertices \((1, 2)\), \((5, 1)\), \((6, 4)\), and \((2, 5)\). What is the optimal value?",
        -8,
        "1",
        r"The vertex values are \(1 - 4 = -3\), \(5 - 2 = 3\), \(6 - 8 = -2\), and \(2 - 10 = -8\). The smallest is \(-8\), at \((2, 5)\). Reporting 3 gives the maximum. Reporting \(-3\) or \(-2\) gives a different vertex. Reporting 5 or 2 reports a coordinate of the minimizer rather than the objective.",
        fig=FALL,
        alt=A_FALL,
    )
    b.find_error(
        3,
        r"A note claims that \((5, 1)\) minimizes \(x + y\) on the parallelogram with vertices \((1, 2)\), \((5, 1)\), \((6, 4)\), and \((2, 5)\). Exactly one step is false.",
        [
            r"The level lines of \(x + y\) are the lines \(x + y = c\).",
            "A linear objective on a polygon attains its minimum at a vertex.",
            r"Among the four vertices, \((5, 1)\) gives the smallest value of \(x + y\).",
            "If two adjacent vertices tie, every point of the edge between them is a minimizer.",
        ],
        2,
        r"The levels of a linear function are parallel lines, and a linear function on a polygon attains its minimum at a vertex. A tie along an edge really does fill that edge with minimizers. The comparison is the false step. The values are 3 at \((1, 2)\), 6 at \((5, 1)\), 10 at \((6, 4)\), and 7 at \((2, 5)\). The smallest is 3, so \((5, 1)\) is not a minimizer.",
        [
            r"\((5, 1)\) has objective 6, and \((1, 2)\) has objective 3.",
            r"The level lines of \(x + y\) are circles.",
            "A linear objective on a polygon need not attain its minimum at a vertex.",
        ],
        0,
        fig=SIMP,
        alt=A_SIMP,
    )
    b.num(
        3,
        r"Maximize \(x + 4y\) on the parallelogram with vertices \((1, 2)\), \((5, 1)\), \((6, 4)\), and \((2, 5)\). What is the optimal value?",
        22,
        "1",
        r"The vertex values are 9, 9, 22, and 22. The largest is 22, attained at both \((6, 4)\) and \((2, 5)\), so the maximizer is not unique and the optimal value still is. Reporting 9 gives the minimum. Reporting 6 or 4 or 5 reports a coordinate.",
        fig=RISE,
        alt=A_RISE,
    )
    b.sym(
        3,
        r"The level lines of \(p x + q y\), with \(q \ne 0\), have slope",
        "-p/q",
        {"p": (1, 5), "q": (1, 4)},
        r"A level is \(p x + q y = c\), so \(y = -(p/q) x + c/q\). The slope is \(-p/q\). The gradient \((p, q)\) is perpendicular to those lines and points toward larger values, which is how you know which way to slide. Using \(p/q\) without the minus slopes the line the wrong way. Using \(-q/p\) swaps the two coefficients.",
        alternates=["-(p/q)", "-1*p/q"],
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        4,
        r"Minimize \(x + y\) subject to \(x \ge 1\) and \(y \ge 0\). Which description is right?",
        [
            "The program is infeasible.",
            "The feasible set is a polygon with four vertices.",
            "The feasible set is unbounded, and the optimal value is 1.",
            "The feasible set is unbounded, and the objective is unbounded below.",
        ],
        2,
        r"The constraints leave an unbounded quarter-plane, cut off only by \(x \ge 1\). Along that ray the objective \(x + y\) is at least 1, and the value 1 is attained at \((1, 0)\). The set being unbounded does not make the objective unbounded. The set is nonempty, so the program is feasible. It is not a polygon with a finite vertex list.",
        fig=ORTH,
        alt=A_ORTH,
        preview=["polyhedra-extreme-points"],
    )
    b.num(
        4,
        r"Minimize \(2x + y\) on the parallelogram with vertices \((1, 2)\), \((5, 1)\), \((6, 4)\), and \((2, 5)\). What is the optimal value?",
        4,
        "1",
        r"The vertex values are \(2 + 2 = 4\), \(10 + 1 = 11\), \(12 + 4 = 16\), and \(4 + 5 = 9\). The smallest is 4, at \((1, 2)\). Reporting 16 gives the maximum. Reporting 11 or 9 gives another vertex. Reporting 2 gives a coordinate.",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_IT,
    )
    b.mc(
        4,
        r"The unique minimizer of \(x + y\) on the parallelogram with vertices \((1, 2)\), \((5, 1)\), \((6, 4)\), and \((2, 5)\) is",
        [
            r"\((6, 4)\)",
            r"\((5, 1)\)",
            r"\((2, 5)\)",
            r"\((1, 2)\)",
        ],
        3,
        r"The vertex values are 3, 6, 10, and 7. The unique minimum is 3, at \((1, 2)\). The point \((6, 4)\) is the unique maximizer, with value 10. The other two vertices sit strictly between. The center of the parallelogram is a convex combination of vertices and cannot beat the best vertex for a linear objective.",
        fig=ARR,
        alt=A_ARR,
        preview=P_BFS,
    )
    b.save()


def bank_polyhedra():
    b = Bank("polyhedra-extreme-points")
    b.mc(
        1,
        "A point of a set is an extreme point when",
        [
            "it is the midpoint of some segment that stays inside the set",
            "it lies in the interior of the set",
            "it cannot be written as a convex combination of two other points of the set",
            "every nearby point of the set has a larger Euclidean norm",
        ],
        2,
        r"An extreme point is one that never sits strictly between two other points of the set. If \(x = (1 - t) y + t z\) with \(y, z\) in the set, \(y \ne z\), and \(t\) strictly between 0 and 1, then \(x\) is not extreme. A midpoint of a segment in the set is the opposite situation. An interior point of a full-dimensional polyhedron can be averaged in many directions. The norm test describes a different geometric idea and fails for a vertex far from the origin as easily as it fails for one near the origin.",
        fig=DENT,
        alt=A_DENT,
    )
    b.num(
        1,
        r"The point \((4, 0)\) lies on the segment from \((0, 0)\) to \((8, 0)\). What weight on \((8, 0)\) writes \((4, 0)\) as a convex combination of the endpoints?",
        0.5,
        "1",
        r"The combination \((1 - t) (0, 0) + t (8, 0)\) equals \((8t, 0)\). Matching the first coordinate gives \(8t = 4\), so \(t = 1/2\). Reporting 4 or 8 reports a coordinate. Reporting 2 would be the weight if the segment had been parameterized by a different speed. The weight is the fraction of the way from the first endpoint to the second.",
        fig=SEG,
        alt=A_SEG,
    )
    b.mc(
        1,
        "A polyhedron, cut out by finitely many linear inequalities, is convex because",
        [
            "it is a finite set of vertices",
            "it is the intersection of half-spaces, and each half-space is convex",
            "the union of convex sets is always convex",
            "every polyhedron is bounded",
        ],
        1,
        r"Each linear inequality describes a half-space, and a half-space contains the segment between any two of its points. An intersection of convex sets is convex, so the polyhedron is convex. A polyhedron can be unbounded, so boundedness is not the reason. The union of convex sets need not be convex. A polyhedron is not in general a finite set: the edges and the interior, when there is one, are part of the set. The vertices are the extreme points, not the whole set.",
        fig=HALF,
        alt=A_HALF,
    )
    b.order(
        2,
        "Put these steps in the order used to test whether a candidate in the plane is a vertex of a polyhedron.",
        [
            "List the inequalities that hold with equality at the candidate.",
            "Check that those active normals include two independent vectors.",
            "Solve that square system and confirm the candidate is its only solution.",
            "Check that the candidate satisfies every inequality that was not used in the square system.",
        ],
        r"The active set is the data of the test, so it is listed first. Independence of two normals is what makes the active set define a single point rather than a line, and the next step solves that square system. Uniqueness is checked before the unused inequalities, because a point that is not even the unique solution of the active equalities is not a vertex. The unused inequalities are the feasibility check, and they come last. Skipping independence can accept a whole edge as if it were a vertex.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.multi(
        2,
        r"Let \(P\) be the polygon \(x \ge 0\), \(y \ge 0\), \(x + y \le 8\), \(y \le 5\). Which points are extreme points of \(P\)?",
        [
            r"\((0, 0)\)",
            r"\((8, 0)\)",
            r"\((4, 0)\)",
            r"\((3, 5)\)",
            r"\((4, 4)\)",
            r"\((0, 5)\)",
        ],
        [0, 1, 3, 5],
        r"The vertices are the corners \((0, 0)\), \((8, 0)\), \((3, 5)\), and \((0, 5)\). Each is the unique solution of two tight independent inequalities, and each satisfies the remaining inequalities."
        "\n"
        r"• \((4, 0)\) is the midpoint of the bottom edge, so it is a convex combination of \((0, 0)\) and \((8, 0)\)."
        "\n"
        r"• \((4, 4)\) lies on the edge from \((3, 5)\) to \((8, 0)\), strictly between those vertices.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        2,
        r"For a polyhedron \(\{x : Ax = b,\ x \ge 0\}\) whose rows are independent, the extreme points are",
        [
            "exactly the basic feasible solutions",
            "exactly the points where every variable is positive",
            r"exactly the points where \(Ax = b\), with no sign restriction",
            "the midpoints of the edges",
        ],
        0,
        r"With independent rows, a point of this polyhedron is extreme exactly when it is a basic feasible solution: some invertible set of columns carries \(B^{-1} b \ge 0\), and the other variables are zero. A fully positive point is not basic unless there are as many variables as rows. Dropping nonnegativity keeps the affine set, whose points are not extreme. Midpoints of edges are convex combinations, so they are the points that fail the extreme-point test.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.find_error(
        3,
        "A note claims that a polyhedron need not be convex. Exactly one step is false.",
        [
            "A polyhedron is the intersection of finitely many half-spaces.",
            "Each half-space contains the segment between any two of its points.",
            "The intersection of convex sets can miss that segment, so the polyhedron need not be convex.",
            "A set that contains every such segment is convex.",
        ],
        2,
        r"The first step is the definition used here. Each half-space is convex, and the intersection of any family of convex sets is convex: a segment that lives in every piece lives in the intersection. The definition of convexity is exactly that segment property. The false step claims the intersection can lose the segment. That claim is the one that fails, and it is what the note uses to deny convexity.",
        [
            "The intersection of convex sets contains every segment that its pieces contain.",
            "A half-space can fail to contain the segment between two of its points.",
            "A polyhedron is not an intersection of half-spaces.",
        ],
        0,
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        3,
        r"How many extreme points does the polygon \(x \ge 0\), \(y \ge 0\), \(x + y \le 8\), \(y \le 5\) have?",
        4,
        "1",
        r"The corners are \((0, 0)\), \((8, 0)\), \((3, 5)\), and \((0, 5)\). Each pair of tight independent inequalities picks one of them, and no other point is extreme: every other feasible point lies on a segment inside the polygon. Reporting 3 drops a corner. Reporting 5 counts an edge point such as \((4, 0)\). Reporting 8 reports a coordinate of a corner.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.sym(
        3,
        r"The point \((s, 0)\) lies on the segment from \((0, 0)\) to \((p, 0)\) with \(0 < s < p\). The weight on \((p, 0)\) is",
        "s/p",
        {"s": (1, 3), "p": (4, 9)},
        r"The combination \((1 - w) (0, 0) + w (p, 0)\) equals \((w p, 0)\). Matching the first coordinate gives \(w = s/p\). On the declared ranges that weight sits strictly between 0 and 1, so the point is not an endpoint. Using \(p/s\) inverts the fraction and is larger than 1 on these ranges, which is not a convex weight. Using \(s - p\) is a distance, not a weight.",
        alternates=["s*(1/p)", "(s/p)"],
        fig=SEG,
        alt=A_SEG,
    )
    b.num(
        4,
        r"Maximize \(x + 2y\) on the polygon \(x \ge 0\), \(y \ge 0\), \(x + y \le 8\), \(y \le 5\). What is the optimal value?",
        13,
        "1",
        r"The extreme values are 0 at \((0, 0)\), 8 at \((8, 0)\), \(3 + 10 = 13\) at \((3, 5)\), and 10 at \((0, 5)\). A linear objective on a nonempty polygon attains its maximum at an extreme point, so the optimal value is 13. Reporting 10 or 8 gives another vertex. Reporting 0 gives the minimum. Reporting 5 gives the upper bound on \(y\), not the objective.",
        fig=RISE,
        alt=A_RISE,
        preview=P_BFS,
    )
    b.mc(
        4,
        r"The point \((4, 4)\) on the edge from \((3, 5)\) to \((8, 0)\) of the polygon \(x \ge 0\), \(y \ge 0\), \(x + y \le 8\), \(y \le 5\) is",
        [
            "an extreme point, because it lies on the boundary",
            r"infeasible, because it fails \(y \le 5\)",
            "the only maximizer of every linear objective",
            "a convex combination of two other feasible points, hence not extreme",
        ],
        3,
        r"The point sits strictly between two vertices of an edge, so it is a convex combination of feasible points and is not extreme. Being on the boundary is not enough: every edge point is on the boundary. It satisfies \(y = 4 \le 5\) and \(x + y = 8\), so it is feasible. A linear objective that is constant on the edge is maximized at every point of the edge, not only at this one, and a linear objective that increases along the edge is maximized at a vertex.",
        fig=SEG,
        alt=A_SEG,
        preview=P_FW,
    )
    b.mc(
        4,
        r"For \(x_1 + x_2 + x_3 = 6\) with \(x \ge 0\), which point is a basic feasible solution?",
        [
            r"\((2, 2, 2)\)",
            r"\((6, 0, 0)\)",
            r"\((3, 3, 0)\)",
            r"\((4, 4, -2)\)",
        ],
        1,
        r"One equation in three nonnegative variables has basic solutions with a single basic variable equal to 6 and the others zero. The point \((6, 0, 0)\) is one of them, and it is nonnegative. The point \((2, 2, 2)\) meets the equation and has three positive variables, so it is not basic. The point \((3, 3, 0)\) has two positive variables. The point with a negative coordinate is a basic pattern that fails feasibility.",
        fig=BASIS,
        alt=A_BASIS,
        preview=P_DIR,
    )
    b.save()


def bank_bfs():
    b = Bank("basic-feasible-solutions")
    b.mc(
        1,
        r"A basic feasible solution of \(Ax = b\), \(x \ge 0\), with \(A\) of full row rank, is obtained by",
        [
            "setting every variable equal to the matching right-hand side entry",
            "choosing an invertible basis, setting the other variables to zero, and solving, provided the basic variables are nonnegative",
            "choosing any invertible basis and accepting the solution even when a basic variable is negative",
            "setting the basic variables to zero and solving for the nonbasic ones",
        ],
        1,
        r"The basis is an invertible block of columns. The nonbasic variables are set to zero, and the square system \(B x_B = b\) is solved. The result is feasible only when \(x_B \ge 0\). A negative basic variable is a basic solution and not a feasible one. Copying the right-hand side onto every variable ignores the columns. Zeroing the basic variables and solving for the others reverses the definition.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.num(
        1,
        r"For \(x_1 + x_2 + x_3 = 6\) and \(x_1 + 2x_2 + x_4 = 10\), with all variables nonnegative, the basis of columns 1 and 2 gives basic variables \(x_1\) and \(x_2\). What is \(x_2\)?",
        4,
        "1",
        r"The basis matrix is \(\begin{bmatrix} 1 & 1 \\ 1 & 2 \end{bmatrix}\), with determinant 1. Solving gives \(x_1 = 2\) and \(x_2 = 4\), and both are nonnegative, so the point \((2, 4, 0, 0)\) is feasible. Check: \(2 + 4 = 6\) and \(2 + 8 = 10\). Reporting 2 gives \(x_1\). Reporting 6 or 10 gives a right-hand side. Reporting 0 gives a nonbasic variable.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.mc(
        1,
        r"For the same system, columns 1 and 3 produce \(x_1 = 10\) and \(x_3 = -4\). That basis is",
        [
            "a basic feasible solution, because the columns are independent",
            "optimal for every linear objective",
            "infeasible as a point of the original system, because it ignores the equalities",
            "a basic solution that is not feasible, because a basic variable is negative",
        ],
        3,
        r"Independence makes the solution basic: the nonbasic variables are zero and the square system has one solution. Feasibility also needs every variable nonnegative. Here \(x_3 = -4\), so the point is not in the polyhedron. The equalities do hold; that is what the square solve enforces. Optimality is a statement about a cost, and this point is not even feasible.",
        fig=FALL,
        alt=A_FALL,
    )
    b.order(
        2,
        "Put these steps in the order used to build one basic feasible solution. Each step uses the result of the step before it.",
        [
            "Choose as many independent columns as there are rows, and call that set the basis.",
            "With that basis chosen, set every variable outside it to zero.",
            "Only after those nonbasic variables are zero, solve the square system for the basic variables.",
            "Accept the point only after that solve, and only when every basic variable is nonnegative.",
        ],
        r"A basis is a choice of independent columns, so the choice comes first. The next step refers to that basis when it sets the other variables to zero, so the zeros cannot be assigned earlier. The square solve is stated to come only after those zeros, which is the same order as the construction: substitute the nonbasic zeros, then solve \(B x_B = b\). Nonnegativity is applied to the solution just computed. Accepting a negative basic variable skips the last step and leaves the polyhedron.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"For \(x_1 + x_2 + x_3 = 6\) and \(x_1 + 2x_2 + x_4 = 10\), with \(x \ge 0\), which points are basic feasible solutions?",
        [
            r"\((2, 4, 0, 0)\)",
            r"\((6, 0, 0, 4)\)",
            r"\((10, 0, -4, 0)\)",
            r"\((0, 5, 1, 0)\)",
            r"\((3, 3, 0, 1)\)",
            r"\((0, 0, 6, 10)\)",
        ],
        [0, 1, 3, 5],
        r"The feasible bases are columns \(\{1, 2\}\), \(\{1, 4\}\), \(\{2, 3\}\), and \(\{3, 4\}\), with points \((2, 4, 0, 0)\), \((6, 0, 0, 4)\), \((0, 5, 1, 0)\), and \((0, 0, 6, 10)\)."
        "\n"
        r"• \((10, 0, -4, 0)\) solves the equalities with columns 1 and 3, and \(x_3\) is negative."
        "\n"
        r"• \((3, 3, 0, 1)\) satisfies both equalities and has three positive variables, so it is not a basic solution.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.sym(
        2,
        r"A diagonal basis has entries \(a\) and \(d\), and the right-hand side is \((p, q)\), with every name positive. The sum of the two basic variables is",
        "p/a+q/d",
        {"a": (1, 4), "d": (1, 4), "p": (1, 8), "q": (1, 8)},
        r"The square system separates: the first basic variable is \(p/a\) and the second is \(q/d\). Their sum is \(p/a + q/d\). On the declared ranges both terms are positive, so the basis is feasible. Adding \(a\) and \(d\) in the numerator swaps the roles of data and basis entries. Using \(p/a + q/a\) reuses the first pivot for the second row.",
        alternates=["q/d+p/a", "p/a+(q/d)"],
        fig=BASIS,
        alt=A_BASIS,
    )
    b.find_error(
        3,
        r"A note treats columns 2 and 4 of \(x_1 + x_2 + x_3 = 6\), \(x_1 + 2x_2 + x_4 = 10\) as a basic feasible solution. Exactly one step is false.",
        [
            r"The basis matrix is \(\begin{bmatrix} 1 & 0 \\ 2 & 1 \end{bmatrix}\).",
            "Its determinant is 1, so the columns are independent.",
            r"The basic variables are \(x_2 = 6\) and \(x_4 = -2\).",
            "Because the basis is invertible, this solution is a basic feasible solution.",
        ],
        3,
        r"Column 2 is \((1, 2)\) and column 4 is \((0, 1)\), so the matrix and its determinant are right. The solve gives \(x_2 = 6\) and \(x_4 = -2\), with the other variables zero. Invertibility is what makes the solution basic. Feasibility fails because \(x_4\) is negative. The last step treats independence as if it included the sign check.",
        [
            r"\(x_4 = -2\), so the solution is basic and not feasible.",
            "The determinant of that basis matrix is 0.",
            r"The computed \(x_2\) is not 6.",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"For \(x_1 + x_2 + x_3 = 6\) and \(x_1 + 2x_2 + x_4 = 10\), the slack basis uses columns 3 and 4. What is the sum of the basic variables?",
        16,
        "1",
        r"Columns 3 and 4 are the identity, so the basic variables are the right-hand side itself: \(x_3 = 6\) and \(x_4 = 10\). Both are nonnegative. Their sum is 16. Reporting 6 or 10 reports one slack. Reporting 4 reports a basic variable from a different basis. The sum is a convenient check that both slacks were kept.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        3,
        "A standard-form linear program that is feasible, and whose objective is bounded below, attains its optimal value",
        [
            "at a basic feasible solution",
            "only at a point where every variable is positive",
            "only in the relative interior of the feasible set",
            "at a basic solution that is allowed to have negative entries",
        ],
        0,
        r"The feasible set is a nonempty polyhedron with at least one extreme point, and a linear objective that is bounded below attains its minimum at an extreme point. Those extreme points are the basic feasible solutions. A strictly positive point is not needed, and an optimum on an edge can sit at a vertex of that edge. The relative interior is where a nonconstant linear function is never minimal. A basic solution with a negative entry is outside the feasible set, so it cannot be optimal.",
        fig=SIMP,
        alt=A_SIMP,
    )
    b.num(
        4,
        r"For \(x_1 + x_2 + x_3 = 9\) and \(4x_1 + x_2 + x_4 = 12\), with \(x \ge 0\), the basis of columns 1 and 2 is feasible. What is the sum of its basic variables?",
        9,
        "1",
        r"The basis matrix is \(\begin{bmatrix} 1 & 1 \\ 4 & 1 \end{bmatrix}\). Solving gives \(x_1 = 1\) and \(x_2 = 8\), both nonnegative, and the slacks are zero. The sum is 9. Check: \(1 + 8 = 9\) and \(4 + 8 = 12\). Reporting 1 or 8 reports one coordinate. Reporting 12 reports a right-hand side. Reporting 21 adds a right-hand side to a coordinate.",
        fig=BASIS,
        alt=A_BASIS,
        preview=P_DIR,
    )
    b.mc(
        4,
        "A basic feasible solution in which some basic variable equals zero is",
        [
            r"infeasible, because a zero violates \(x \ge 0\)",
            "not basic, because the basis matrix became singular",
            "feasible, and called degenerate",
            "the unique optimum of every linear objective",
        ],
        2,
        r"Nonnegativity allows zeros. A basic variable that lands on zero is still a feasible point, and the basis is called degenerate: more than one basis can describe it, and a later ratio test can take a step of length zero. The basis matrix was chosen invertible, and a zero in the solution does not change that determinant. Degeneracy does not by itself decide optimality.",
        fig=SEG,
        alt=A_SEG,
        preview=P_IT,
    )
    b.mc(
        4,
        r"The slack basis of \(Ax + s = b\), \(x \ge 0\), \(s \ge 0\), with the slacks as the basic variables, is a basic feasible solution when",
        [
            r"\(b\) has at least one negative entry",
            r"\(b \ge 0\)",
            r"\(b = 0\) only",
            "the original variables are free",
        ],
        1,
        r"The slack columns form an identity basis, so the basic solution is \(s = b\) and \(x = 0\). It is feasible exactly when \(b \ge 0\). A negative entry of \(b\) makes that slack negative. The zero vector is the special case \(b = 0\), not the only feasible case. Free original variables would leave the standard form; the test here is only the sign of \(b\).",
        fig=ORTH,
        alt=A_ORTH,
        preview=P_PH,
    )
    b.save()


def bank_directions():
    b = Bank("simplex-feasible-directions")
    b.mc(
        1,
        "For a minimization, a negative reduced cost on a nonbasic variable means",
        [
            "increasing that variable, and moving the basic variables to keep the equalities, decreases the objective",
            "the current basis is optimal",
            "the current basic solution has a negative variable",
            "every feasible step increases the objective",
        ],
        0,
        r"The reduced cost is the slope of the objective along the basic direction that raises the chosen nonbasic variable at rate 1. A negative slope means the objective falls. Optimality for a minimization is the opposite sign pattern: every reduced cost nonnegative. The sign of a reduced cost is not the sign of a basic variable. A positive reduced cost is the direction that raises the objective.",
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        1,
        r"Minimize \(-2x_1 - 3x_2\) subject to \(x_1 + x_2 + x_3 = 7\) and \(2x_1 + x_2 + x_4 = 10\), with \(x \ge 0\). From the slack basis, \(x_2\) has reduced cost \(-3\). What step does the ratio test allow?",
        7,
        "1",
        r"The slack basis has \(x_3 = 7\) and \(x_4 = 10\). The column of \(x_2\) is \((1, 1)\), so the ratios are \(7/1\) and \(10/1\). The smaller is 7, and \(x_3\) hits zero. The new point is \((0, 7, 0, 3)\). Reporting 10 uses the other ratio. Reporting 3 gives the new \(x_4\), not the step. Reporting \(-3\) gives the reduced cost.",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        1,
        "If the basic direction for a negative reduced cost has no negative component, then",
        [
            "the ratio test returns the step 1",
            "the current basis is optimal",
            "every positive step stays feasible, and the objective is unbounded below",
            "the entering column is the zero column",
        ],
        2,
        r"The direction raises the entering variable and does not decrease any basic variable, so \(x + \theta d\) stays nonnegative for every \(\theta \ge 0\). The objective changes at the reduced-cost rate, which is negative, so it falls without bound. There is no finite ratio to compute. Optimality would require every reduced cost to be nonnegative. A zero column would have reduced cost equal to the bare cost coefficient and would not move the basic variables; the hypothesis here is a direction that is nonnegative, not a direction that is zero.",
        fig=RISE,
        alt=A_RISE,
    )
    b.order(
        2,
        "Put these steps in the order used to test one feasible basic direction for a minimization.",
        [
            "Select a nonbasic index whose reduced cost is negative.",
            "Solve for the basic direction that raises that index at rate 1 and keeps the equalities.",
            "If that direction is nonnegative in every basic coordinate, every positive step is feasible and the objective is unbounded below.",
            "If some basic coordinate of the direction is negative, the longest feasible step is the minimum of the positive ratios.",
        ],
        r"The entering column is chosen from the sign of the reduced cost, so that choice comes first. The direction is then computed from the basis. The sign pattern of the direction decides the next branch: a fully nonnegative direction is an unbounded ray, and the ratio test is the other branch, used only when some basic coordinate decreases. Taking a ratio before computing the direction has no column to divide by.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.multi(
        2,
        r"From the slack basis of the program in the previous numeric question, \(x_1\) is the entering variable. Which statements hold?",
        [
            r"The reduced cost of \(x_1\) is \(-2\).",
            "The longest feasible step is 5.",
            r"\(x_3\) reaches zero before \(x_4\).",
            r"The basic direction has second component \(-2\).",
            "The objective increases along this direction.",
        ],
        [0, 1, 3],
        r"The column of \(x_1\) is \((1, 2)\). With a zero basic cost the reduced cost equals the bare cost, \(-2\). The basic direction is \((-1, -2)\). The ratios are \(7/1 = 7\) and \(10/2 = 5\), so the step is 5 and \(x_4\) hits zero first. The objective change is \(5 \cdot (-2) = -10\), a decrease."
        "\n"
        r"• \(x_3\) would hit zero at step 7, which is later than step 5."
        "\n"
        r"• A negative reduced cost means the objective falls, not rises.",
        fig=ARR,
        alt=A_ARR,
    )
    b.sym(
        2,
        r"A one-row basis has multiplier \(u\), the entering column is the number \(a\), and the entering cost coefficient is \(c\). The reduced cost is",
        "c-u*a",
        {"c": (-5, -1), "u": (0.5, 2), "a": (1, 3)},
        r"The simplex multiplier satisfies \(u \cdot a_B = c_B\) on a one-column basis, and the reduced cost of a nonbasic column is \(c - u a\). The same pattern in several rows is \(c_j - c_B^T B^{-1} A_j\). Adding \(u a\) instead of subtracting it prices the column with the wrong sign. Using \(c - u\) forgets the column entry \(a\).",
        alternates=["c-(u*a)", "-u*a+c"],
        fig=BASIS,
        alt=A_BASIS,
    )
    b.find_error(
        3,
        r"A note computes the step for entering \(x_1\) from the slack basis of \(x_1 + x_2 + x_3 = 7\), \(2x_1 + x_2 + x_4 = 10\), minimizing \(-2x_1 - 3x_2\). Exactly one step is false.",
        [
            r"The reduced cost of \(x_1\) is \(-2\), so \(x_1\) may enter.",
            r"The basic direction is \((-1, -2)\).",
            r"The candidate ratios are \(7/1\) and \(10/2\).",
            "The largest feasible step is the larger ratio, which is 7.",
        ],
        3,
        r"The reduced cost, the direction, and the two ratios are right. The ratio test keeps every basic variable nonnegative, so it takes the smaller ratio, \(10/2 = 5\), and \(x_4\) leaves. Taking 7 drives \(x_4\) to \(10 - 2 \cdot 7 = -4\). The largest feasible step is the minimum of the ratios, not the maximum.",
        [
            "The minimum of the ratios 7 and 5 is 5, so the step is 5.",
            r"The reduced cost of \(x_1\) is positive, so \(x_1\) must not enter.",
            r"The basic direction for \(x_1\) is \((1, 2)\), not \((-1, -2)\).",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"In that same slack basis, entering \(x_1\) and taking the ratio-test step changes the objective by how much?",
        -10,
        "1",
        r"The reduced cost is \(-2\) and the step is 5, so the objective changes by \(5 \cdot (-2) = -10\). The new point is \((5, 0, 2, 0)\), and the cost \(-2 \cdot 5 = -10\) agrees. Reporting 5 gives the step. Reporting \(-2\) gives the reduced cost. Reporting 10 drops the sign: the objective falls.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        3,
        "Two nonbasic variables both have negative reduced costs. For the objective to decrease on the next step,",
        [
            "only the more negative one is a legal entering variable",
            "either one may enter",
            "both must enter in the same step",
            "neither may enter until a slack has negative reduced cost",
        ],
        1,
        r"Any negative reduced cost gives a direction of decrease. The rule that picks the most negative cost is one pivot rule. Another rule may pick the other negative cost. Both keep the descent property. A single pivot enters one column, not two. Slack reduced costs are zero while those slacks are basic; the entering variable is nonbasic.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        4,
        r"From the slack basis of \(x_1 + x_2 + x_3 = 7\), \(2x_1 + x_2 + x_4 = 10\), minimizing \(-2x_1 - 3x_2\), what is the reduced cost of \(x_2\)?",
        -3,
        "1",
        r"The slack basis has basic cost zero, so each reduced cost equals the variable's own cost coefficient. The coefficient of \(x_2\) is \(-3\). Reporting \(-2\) gives the reduced cost of \(x_1\). Reporting 3 drops the sign and would say the objective rises. Reporting 7 gives the first right-hand side, which is a basic value, not a slope.",
        fig=BASIS,
        alt=A_BASIS,
        preview=P_IT,
    )
    b.mc(
        4,
        r"Starting from that slack basis and entering \(x_2\) with the ratio-test step, the new basis is",
        [
            r"\(x_2\) and \(x_4\), because \(x_3\) leaves",
            r"\(x_2\) and \(x_3\), because \(x_4\) leaves",
            r"\(x_1\) and \(x_2\)",
            "both slacks, because the step is zero",
        ],
        0,
        r"The column of \(x_2\) is \((1, 1)\), and the basic values are 7 and 10. The ratios are 7 and 10, so \(x_3\) leaves at step 7 and \(x_4\) stays at 3. The new basic pair is \(x_2, x_4\), with point \((0, 7, 0, 3)\). The other slack is the one that leaves. Column \(x_1\) was not the entering column. The step is 7, not zero.",
        fig=ARR,
        alt=A_ARR,
        preview=P_IT,
    )
    b.num(
        4,
        r"At the point reached by that \(x_2\) step, what is the objective value of \(-2x_1 - 3x_2\)?",
        -21,
        "1",
        r"The point is \((0, 7, 0, 3)\). The objective is \(-3 \cdot 7 = -21\). The same number is the old value 0 plus the change \(7 \cdot (-3)\). Reporting \(-3\) gives the reduced cost. Reporting 7 gives the step. Reporting 21 drops the sign.",
        fig=FALL,
        alt=A_FALL,
        preview=P_PH,
    )
    b.save()


def bank_iteration():
    b = Bank("simplex-method-iteration")
    b.mc(
        1,
        "One simplex iteration, when it pivots, changes the basis by",
        [
            "replacing every basic column",
            "adding the entering column and keeping every old basic column",
            "replacing the leaving column by the entering column",
            "replacing the entering column by a slack that was already basic",
        ],
        2,
        r"The basis size stays equal to the number of rows. The leaving variable drops out and the entering variable takes its place. Replacing every column would throw away a feasible basis that only needed one update. Adding a column without removing one makes the block rectangular. A slack that is already basic is not a new entering column.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.num(
        1,
        r"Minimize \(-3x_1 - 4x_2\) subject to \(x_1 + x_2 + x_3 = 6\) and \(x_1 + 2x_2 + x_4 = 8\), with \(x \ge 0\). At the slack basis, what is the most negative reduced cost?",
        -4,
        "1",
        r"The slack basis has basic cost zero, so the reduced costs are the cost coefficients \(-3\) and \(-4\). The more negative one is \(-4\), on \(x_2\). Reporting \(-3\) gives the other reduced cost, which is also improving and is not the most negative. Reporting 4 drops the sign. Reporting 8 gives a right-hand side.",
        fig=FALL,
        alt=A_FALL,
    )
    b.mc(
        1,
        "For a minimization, a basis is optimal when",
        [
            "every nonbasic reduced cost is nonnegative",
            "every nonbasic reduced cost is negative",
            "some basic variable is zero",
            "the entering column has no positive entry",
        ],
        0,
        r"If every reduced cost is nonnegative, no nonbasic increase can decrease the objective, and the current basic feasible solution is optimal. All-negative reduced costs mean every nonbasic column is still improving. A zero basic variable is degeneracy, not optimality. A column with no positive entry, paired with a negative reduced cost, is the unbounded-ray test.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.order(
        2,
        "Put these steps in the order of one simplex iteration for a minimization.",
        [
            "Compute a reduced cost for every nonbasic variable.",
            "If every reduced cost is nonnegative, stop; this basis is optimal.",
            "Otherwise select one entering variable with a negative reduced cost.",
            "If the entering column has no positive entry, stop and report an unbounded ray. Otherwise choose a leaving variable by the minimum ratio.",
            "Replace the leaving column by the entering column and update the basic solution.",
        ],
        r"Reduced costs are the slopes, so they are computed first. The optimality test uses those slopes and comes before any entering choice; the next step says otherwise. The entering variable is then one negative reduced cost. The column test comes next: no positive entry is an unbounded ray, and a positive entry produces the ratio that names the leaving variable. The pivot is the update, and it needs that leaving index. Pivoting before the ratio test does not know which row to use.",
        fig=ARR,
        alt=A_ARR,
    )
    b.multi(
        2,
        r"At the slack basis of \(x_1 + x_2 + x_3 = 6\), \(x_1 + 2x_2 + x_4 = 8\), minimizing \(-3x_1 - 4x_2\), which statements hold?",
        [
            r"\(x_1\) has reduced cost \(-3\).",
            r"\(x_2\) has reduced cost \(-4\).",
            "The basis is already optimal.",
            r"Entering \(x_1\) and entering \(x_2\) are both legal descent steps.",
            "The program is unbounded from this basis.",
        ],
        [0, 1, 3],
        r"Both structural reduced costs are negative, so the basis is not optimal, and either column may enter. The column of \(x_1\) is \((1, 1)\) and the column of \(x_2\) is \((1, 2)\). Each has a positive entry, so the ratio test returns a finite step from this basis."
        "\n"
        r"• A negative reduced cost is an improving direction, so the optimality test fails."
        "\n"
        r"• An unbounded ray needs an improving column with no positive entry. Neither structural column is of that kind here.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.sym(
        2,
        r"One basic variable has value \(p\), and the entering column has a single positive entry \(r\) in that row. The ratio test returns",
        "p/r",
        {"p": (2, 12), "r": (0.5, 4)},
        r"The step that drives this basic variable to zero is \(p/r\). With only one positive entry there is nothing else to compare, so the minimum ratio is that single number. Several positive entries would replace it by the smallest of those ratios. Using \(r/p\) inverts the ratio and is not a step in the units of the entering variable. Using \(p - r\) subtracts a column entry from a basic value.",
        alternates=["(p/r)", "p*(1/r)"],
        fig=BASIS,
        alt=A_BASIS,
    )
    b.find_error(
        3,
        r"A note pivots on \(x_2\) at the slack basis of \(x_1 + x_2 + x_3 = 6\), \(x_1 + 2x_2 + x_4 = 8\), minimizing \(-3x_1 - 4x_2\). Exactly one step is false.",
        [
            r"\(x_2\) has reduced cost \(-4\), so it may enter.",
            r"The entering column is \((1, 2)\).",
            r"The two ratios are \(6/1 = 6\) and \(8/2 = 4\).",
            r"The minimum ratio is 6, so \(x_3\) leaves.",
        ],
        3,
        r"The reduced cost, the column, and both ratios are right. The minimum of 6 and 4 is 4, so \(x_4\) leaves and the step is 4. The new point is \((0, 4, 2, 0)\). Calling 6 the minimum drives the second basic variable to \(8 - 2 \cdot 6 = -4\).",
        [
            r"The minimum of 6 and 4 is 4, so \(x_4\) leaves.",
            r"\(x_2\) has a positive reduced cost and must not enter.",
            r"The column of \(x_2\) is \((1, 1)\), not \((1, 2)\).",
        ],
        0,
        fig=FALL,
        alt=A_FALL,
    )
    b.num(
        3,
        r"From that slack basis, enter \(x_1\) instead and take the ratio-test step. What is the new objective value?",
        -18,
        "1",
        r"The column of \(x_1\) is \((1, 1)\), and the ratios are \(6/1\) and \(8/1\). The step is 6, \(x_3\) leaves, and the new point is \((6, 0, 0, 2)\). The objective is \(-3 \cdot 6 = -18\). The same figure is the change \(6 \cdot (-3)\). Reporting \(-4\) gives the other reduced cost. Reporting 6 gives the step. Reporting \(-3\) gives the reduced cost of \(x_1\).",
        fig=ARR,
        alt=A_ARR,
    )
    b.mc(
        3,
        r"On this slack basis the most-negative rule enters \(x_2\), while another rule may enter \(x_1\). Both rules",
        [
            "declare the basis optimal",
            "declare the program unbounded",
            "are required to enter the same column",
            "produce a step on which the objective does not rise",
        ],
        3,
        r"Each rule selects a negative reduced cost, so each step has negative slope and the objective falls. They need not select the same column: \(-4\) and \(-3\) are both legal. Neither test says the basis is optimal, and neither column is an unbounded ray. The freedom is in the path. A later pivot can still be required after either choice.",
        fig=PAIR,
        alt=A_PAIR,
    )
    b.num(
        4,
        r"Continue from the slack basis of \(x_1 + x_2 + x_3 = 6\), \(x_1 + 2x_2 + x_4 = 8\), minimizing \(-3x_1 - 4x_2\), until every reduced cost is nonnegative. What is the optimal value?",
        -20,
        "1",
        r"One improving path enters \(x_1\) first and reaches \((6, 0, 0, 2)\) with value \(-18\). There the reduced cost of \(x_2\) is \(-1\), the ratios are 6 and 2, and the step 2 reaches \((4, 2, 0, 0)\) with value \(-20\). The slack reduced costs at that basis are positive, so it is optimal. Entering \(x_2\) first reaches value \(-16\) and still needs another pivot; the optimal value does not depend on that choice. Reporting \(-18\) or \(-16\) stops one pivot early. Reporting \(-12\) is \(-3 \cdot 4\) and drops the \(x_2\) term.",
        fig=FALL,
        alt=A_FALL,
        preview=P_PH,
    )
    b.num(
        4,
        r"Minimize \(-2x\) subject to \(x - y + s = 5\) and \(x, y, s \ge 0\). From the slack basis, enter \(x\) and take the ratio-test step. What is the objective at the new point?",
        -10,
        "1",
        r"The slack basis has \(s = 5\). The column of \(x\) is \(1\), so the step is 5 and the new point is \(x = 5\), \(y = 0\), \(s = 0\). The objective is \(-2 \cdot 5 = -10\). Reporting 5 gives the step. Reporting \(-2\) gives the reduced cost. Reporting 0 is the value before the pivot.",
        fig=SEG,
        alt=A_SEG,
        preview=P_PH,
    )
    b.mc(
        4,
        r"At that new point \(x = 5\), the reduced cost of \(y\) is \(-2\) and the updated column of \(y\) is \(-1\). The program is",
        [
            "optimal, because a pivot has already been taken",
            "unbounded below, because the improving column has no positive entry",
            r"infeasible, because \(y\) is still zero",
            r"optimal at objective \(-2\), the reduced cost",
        ],
        1,
        r"A negative reduced cost with no positive column entry is an unbounded ray: increasing \(y\) increases \(x\) at the same rate, the slack stays zero, and the objective \(-2x\) falls forever. A single pivot does not certify optimality. A nonbasic zero is the usual basic pattern and is feasible. The reduced cost is a slope, not the optimal value. The value after the first pivot is \(-10\), and it is not optimal.",
        fig=RISE,
        alt=A_RISE,
        preview=P_PH,
    )
    b.save()


def bank_phase():
    b = Bank("simplex-phase-one")
    b.mc(
        1,
        "Phase I of the simplex method minimizes",
        [
            "the original linear objective, with an extra penalty added to the cost",
            "the sum of the artificial variables",
            "the sum of the original variables",
            "the most negative right-hand side",
        ],
        1,
        r"After the rows are written with a nonnegative right-hand side, each row receives an artificial variable and the auxiliary objective is the sum of those artificials. The original cost is set aside until a feasible basis is known. Minimizing the sum of the original variables is a different program. The right-hand side is data, not the objective.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.num(
        1,
        r"Phase I for \(x + 2y \ge 8\) and \(x + y \ge 3\), with \(x, y \ge 0\), starts from the artificial basis after the surpluses are introduced. What is the initial auxiliary objective?",
        11,
        "1",
        r"The equalities are \(x + 2y - s + a = 8\) and \(x + y - t + r = 3\). The artificial basis sets \(a = 8\) and \(r = 3\). The auxiliary objective is \(a + r = 11\). Reporting 8 or 3 reports one right-hand side. Reporting 5 reports a difference of those two numbers, which is not the objective.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.mc(
        1,
        "A positive optimal value of the auxiliary problem means",
        [
            "the original standard-form system is infeasible",
            "the original system is feasible and the artificials are part of every feasible point",
            "phase I must be restarted with a new objective",
            "the original objective is unbounded below",
        ],
        0,
        r"Every feasible point of the original system gives the artificials the value zero, so the auxiliary optimum is zero whenever the original system is nonempty. A positive auxiliary optimum says no such point exists. It does not say the original objective is unbounded: unboundedness is a question about a nonempty feasible set. Restarting with the same constraints and a new auxiliary cost does not create a feasible point that the first auxiliary problem has already ruled out.",
        fig=HALF,
        alt=A_HALF,
    )
    b.order(
        2,
        "Put these steps in the order used to build and read a phase-I problem.",
        [
            "Put the constraints in equality form and make every right-hand side nonnegative.",
            "Add one artificial variable to each equality and minimize the sum of the artificial variables, setting the original costs aside.",
            "Run the simplex method from the basis consisting of the artificial variables.",
            "If the auxiliary optimum is positive, declare the original program infeasible.",
            "If the auxiliary optimum is zero, drop the artificial variables and keep the resulting basic feasible solution.",
        ],
        r"The sign of the right-hand side is fixed first, so that the artificial basis \(a = b\) is nonnegative. The auxiliary objective is then defined, and the simplex method starts from that artificial basis. The two readings of the optimum come after the method stops: a positive value is infeasibility, and a zero value is a feasible basis of the original system. Reading the optimum before the pivots uses the starting sum, which can be positive even when a later basis drives the artificials to zero.",
        fig=SEG,
        alt=A_SEG,
    )
    b.multi(
        2,
        r"At the artificial basis for \(x + 2y - s + a = 8\) and \(x + y - t + r = 3\), minimizing \(a + r\), which statements hold?",
        [
            r"Both \(a\) and \(r\) are basic.",
            "The auxiliary objective equals 11.",
            r"\(x\) may enter, because its reduced cost is \(-2\).",
            "The original program is already known to be infeasible.",
            r"\(y\) has reduced cost \(-3\).",
        ],
        [0, 1, 2, 4],
        r"The artificial basis is \(a = 8\), \(r = 3\), and the objective is 11. With both artificial costs equal to 1, the reduced cost of a structural column is the negative of its column sum. The column of \(x\) sums to 2 and the column of \(y\) sums to 3, so the reduced costs are \(-2\) and \(-3\). Either may enter."
        "\n"
        r"• A positive starting value does not prove infeasibility. The auxiliary problem may still reach 0.",
        fig=BASIS,
        alt=A_BASIS,
    )
    b.sym(
        2,
        r"Both artificial variables are basic, each with cost 1, and an original column has entries \(a\) and \(b\). The phase-I reduced cost of that column is",
        "-a-b",
        {"a": (0.5, 4), "b": (0.5, 4)},
        r"The original column has cost 0 in phase I. The basic cost is \((1, 1)\), and the basis is the identity, so the reduced cost is \(0 - (a + b) = -a - b\). On the declared ranges this is negative, which is why a column with a positive sum can enter. Using \(a + b\) forgets the minus and would say the auxiliary objective rises. Using \(-a\) drops the second row.",
        alternates=["-(a+b)", "-b-a"],
        fig=PAIR,
        alt=A_PAIR,
    )
    b.find_error(
        3,
        r"A note runs phase I on \(x + y \le 12\) and \(x + y \ge 19\), with \(x, y \ge 0\). Exactly one step is false.",
        [
            "The auxiliary objective is the artificial variable, and the original costs are ignored.",
            "An optimal auxiliary solution has artificial value 7.",
            "The original pair of inequalities is therefore feasible.",
            "A positive auxiliary optimum means no point satisfies both original inequalities.",
        ],
        2,
        r"One artificial is enough on the lower bound once the upper bound has its own slack. The gap between 19 and 12 is 7, and the auxiliary minimum is 7. A positive minimum means the original system is empty. The false step draws the opposite conclusion from that 7. The last step is the right reading of the same number.",
        [
            "An auxiliary optimum of 7 is positive, so the original system is empty.",
            "The auxiliary objective should have included the original costs.",
            "The artificial value 7 means the artificial variable is zero.",
        ],
        0,
        fig=HALF,
        alt=A_HALF,
    )
    b.num(
        3,
        r"For \(x + y \le 12\) and \(x + y \ge 19\), with \(x, y \ge 0\), what is the optimal value of the phase-I problem?",
        7,
        "1",
        r"Write \(x + y + s = 12\) and \(x + y - t + a = 19\). Subtracting gives \(a = s + t + 7\). Every nonnegative \(s\) and \(t\) makes \(a \ge 7\), and \(a = 7\) is attained at \(x = 12\), \(s = 0\), \(t = 0\). The original system would need \(a = 0\), which is impossible. Reporting 19 gives the starting artificial value. Reporting 12 gives the upper bound. Reporting 0 would mean the original system is feasible.",
        fig=DENT,
        alt=A_DENT,
    )
    b.mc(
        3,
        "An auxiliary optimal value of exactly zero means",
        [
            "the original objective is unbounded below",
            "phase I must add a second copy of every artificial variable",
            "the original system has a feasible solution, and the current basic point gives one",
            "every original variable is positive",
        ],
        2,
        r"Zero is the best the artificial sum can be, and it is attained, so the artificials are zero at that basic solution. Dropping them leaves a basic feasible solution of the original equalities. It says nothing about the original objective: that objective is restored only after feasibility is known. A second copy of the artificials would change the system. Some original variables may still be zero; a basic solution often has zeros.",
        fig=ORTH,
        alt=A_ORTH,
    )
    b.num(
        4,
        r"In phase I for \(x + 2y - s + a = 8\) and \(x + y - t + r = 3\), the most negative reduced cost at the artificial basis belongs to \(y\). What step does the ratio test give?",
        3,
        "1",
        r"The column of \(y\) is \((2, 1)\), and the artificial values are 8 and 3. The ratios are \(8/2 = 4\) and \(3/1 = 3\). The step is 3, and \(r\) leaves. The new artificial value is \(8 - 2 \cdot 3 = 2\), with \(y = 3\). Reporting 4 uses the other ratio and would drive \(r\) negative. Reporting 8 or 2 reports an artificial value, not the step.",
        fig=ARR,
        alt=A_ARR,
        preview=P_DUAL,
    )
    b.num(
        4,
        r"Continue that phase-I problem until the auxiliary objective is optimal. In the basic feasible solution that is recovered, what is \(y\)?",
        4,
        "1",
        r"After the first pivot the basis is \(a = 2\), \(y = 3\), and the surplus \(t\) has reduced cost \(-2\). The ratio test gives step 1 and \(a\) leaves. The auxiliary value falls from 2 to 0. The resulting point has \(y = 4\), \(t = 1\), and every artificial equal to zero. Check: \(2 \cdot 4 = 8\) and \(4 - 1 = 3\). Reporting 3 stops at the first pivot. Reporting 2 reports the artificial value there. Reporting 0 reports an artificial variable rather than \(y\).",
        fig=SIMP,
        alt=A_SIMP,
        preview=P_AFF,
    )
    b.mc(
        4,
        "During phase I, the original objective is",
        [
            "added to the artificial sum so that every pivot improves both",
            "ignored, and restored only after a feasible basis of the original system is known",
            "used to break ties in the ratio test",
            "required to be nonnegative before any artificial variable is added",
        ],
        1,
        r"Phase I answers a feasibility question. Its cost is the artificial sum, and the original coefficients are not part of that cost. Mixing the two costs can drive an artificial variable positive in exchange for a better original value, which does not produce a feasible point. The ratio test uses basic values and column entries, not the original cost. The original cost is allowed to have either sign; phase I does not need it.",
        fig=FALL,
        alt=A_FALL,
        preview=P_IP,
    )
    b.save()


def expl_standard():
    sections = [
        {
            "heading": "The idea",
            "figure": HALF,
            "figure_alt": A_HALF,
            "body_md": r"""A linear program asks for the best value of a linear function on a set cut out by linear equalities and inequalities. Standard form is one shape of that question: minimize \(c^T x\), keep every constraint an equality \(Ax = b\), and require \(x \ge 0\). The shape is a rewriting, not a smaller class of problems.

A maximization becomes a minimization when the cost is replaced by its negative. The two programs share their feasible points, and the optimal values are negatives of each other. An upper bound \(a^T x \le \beta\) becomes an equality by adding a slack that records the unused room. A lower bound \(a^T x \ge \beta\) becomes an equality by subtracting a surplus. A variable that may be negative is the difference of two nonnegative variables. An absolute value in a constraint splits into two ordinary linear inequalities.

After those rewrites the feasible set is the original one, described so that a square block of columns can be a basis. The names of the new variables are bookkeeping. What matters is which equalities they create and which signs they are required to keep.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""Standard form is
\[
\text{minimize } c^T x \quad \text{subject to } Ax = b,\ x \ge 0.
\]
An upper bound and a lower bound become
\[
a^T x + s = \beta, \qquad a^T x - s = \beta,
\]
with \(s \ge 0\). A free variable splits as \(x = x^+ - x^-\) with both parts nonnegative. Then \(\lvert x \rvert = x^+ + x^-\) once a basic solution is chosen so that at least one of the two parts is zero, which a nondegenerate basis does on its own.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Take the upper bound \(8x + y \le 41\), and evaluate it at \((x, y) = (2, 6)\). The left-hand side is \(16 + 6 = 22\). The slack is the gap from 22 up to 41.

The ribbon slack is 19. The equality form is \(8x + y + s = 41\) with \(s \ge 0\). At this point \(s = 19\). Moving the same point onto a different right-hand side would change the slack and would not change the rule that defines it. A surplus would have been the wrong extra variable, because the inequality bounds the linear form from above.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""The usual sign error is to add a slack on a lower bound, or to subtract one on an upper bound. The extra variable has to restore equality in the direction the inequality allows. A second error is to keep a maximization and call the form standard. The geometry is the same only after the cost changes sign. A third is to split a free variable and then require the two pieces to sum to zero. That forces both pieces to zero and deletes the variable. Both pieces are nonnegative, and their difference is free. Putting a slack and a surplus on the same inequality adds a needless degree of freedom.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A planar picture of the same program reads the optimum off a polygon, including the cases where the best value is attained on a whole edge, where the set is empty, and where the objective runs off to infinity. In any dimension the feasible set is a polyhedron, and the candidates that matter are its extreme points. Those extreme points are exactly the basic feasible solutions of the standard form written here. The dual linear program is built from this same equality form.""",
        },
    ]
    save_explainer("lp-standard-form", "Linear programs and standard form", sections)


def expl_graphical():
    sections = [
        {
            "heading": "The idea",
            "figure": SIMP,
            "figure_alt": A_SIMP,
            "body_md": r"""A linear program in two variables can be settled with a sketch. Each constraint is a half-plane. The feasible set is their intersection: a polygon, a ray, a line, an empty set, or some unbounded convex piece of the plane. The objective \(c^T x\) has level lines that are parallel, and the gradient \(c\) points toward larger values.

Slide a level line across the feasible set in the direction that decreases the objective, and stop at the last contact. One contact point is a unique minimizer. Contact along a whole edge means every point of that edge is optimal, and they share one optimal value. If the line can travel forever while still touching the set, the objective is unbounded below. If the intersection was empty to begin with, there is no contact and the program is infeasible.

An unbounded feasible set is not the same fact as an unbounded objective. A cost that points back toward the set can still attain a minimum on an unbounded region. The picture separates those two outcomes, and it also separates a unique vertex optimum from an edge of optima.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""A level of \(p x + q y\) is the line \(p x + q y = c\). If \(q \ne 0\), the slope is \(-p/q\). The four outcomes for a linear objective on a convex planar set are: a unique minimizer, a whole convex piece of minimizers (often an edge), an unbounded objective, and an empty feasible set. When the feasible set is a nonempty polygon, both the smallest and the largest value of a linear cost are achieved, and a vertex is always among the points that achieve each one. The optimal value is one number even when several points attain it.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""A shed floor is the triangle with vertices \((7, 11)\), \((15, 11)\), and \((7, 18)\). Minimize \(x + y\). The vertex values are \(7 + 11 = 18\), \(15 + 11 = 26\), and \(7 + 18 = 25\).

The shed level is 18, attained only at \((7, 11)\). The other two vertices are worse, so the minimizer is unique. The same three numbers also show that the maximum on this triangle is 26. Nothing in the interior can beat a vertex for this linear cost, because a value strictly inside the range of the vertices is a convex combination of vertex values.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Reading an interior point, or the centroid of a polygon, as the optimum is the common miss. A nonconstant linear function on a convex set is never minimized in the relative interior. A second miss is to treat an unbounded feasible set as an unbounded program without looking at the cost direction. A third is to report one endpoint of an optimal edge and forget the rest of the edge. The optimal value is still unique.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""The reason a vertex wins is that a linear function on a polyhedron attains its bounds at extreme points, when it attains them at all. Those extreme points are the basic feasible solutions once the program is written with equalities and nonnegative variables. The algebra that walks from one such point to a neighboring one is the simplex iteration. The picture in the plane is the same walk, seen without a tableau.""",
        },
    ]
    save_explainer("lp-graphical-solution", "Graphical LP solution and solution types", sections, version=2)


def expl_polyhedra():
    sections = [
        {
            "heading": "The idea",
            "figure": DENT,
            "figure_alt": A_DENT,
            "body_md": r"""A polyhedron is the set of points that satisfy a finite list of linear inequalities. It may also be written with linear equalities. Each inequality is a half-space, and a half-space contains the segment between any two of its points. An intersection of convex sets is convex, so every polyhedron is convex. The union of two polyhedra need not be.

An extreme point is a point of the set that cannot be written as a strict convex combination of two other points of the set. In the plane, the extreme points of a polygon are the corners. A point in the middle of an edge is the midpoint of a short segment that stays inside the set, so it is not extreme. A vertex, in the sense used here, is a point where enough inequalities are tight, with independent normals, that the point is the unique solution of those equalities, and the remaining inequalities hold.

For a polyhedron written as \(Ax = b\), \(x \ge 0\), with independent rows, these three descriptions name the same points: extreme points, vertices, and basic feasible solutions. A basic feasible solution picks an invertible set of columns, sets the other variables to zero, and keeps \(B^{-1} b \ge 0\).""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""A point \(x\) is not extreme when \(x = (1 - t) y + t z\) for some \(y \ne z\) in the set and some \(t\) strictly between 0 and 1. In a basic feasible solution the basis satisfies
\[
x_B = B^{-1} b \ge 0, \qquad x_N = 0.
\]
A convex weight along a segment from the origin to \((p, 0)\) that lands at \((s, 0)\) is the ratio \(s/p\). The same arithmetic, in higher dimension, is what says an edge point is a combination of the endpoints of that edge.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""The yard is the triangle with vertices \((2, 7)\), \((2, 11)\), and \((10, 7)\), cut out by \(x \ge 2\), \(y \ge 7\), and \(x + 2y \le 24\). Minimize \(x + 9y\). The vertex values are \(2 + 63 = 65\), \(2 + 99 = 101\), and \(10 + 63 = 73\).

The yard value is 65, at \((2, 7)\) only. The point halfway along an edge, for example the midpoint of \((2, 7)\) and \((10, 7)\), is feasible and is not extreme. A linear cost cannot prefer that midpoint to both endpoints.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Calling every boundary point extreme is the usual overcount. Edges are full of boundary points, and only the corners are extreme. A second miss is to expect a polyhedron to be bounded. A half-space is already a polyhedron, and it has no extreme point at all when it is a single half-space of dimension greater than zero. A third is to confuse the intersection property with a union property. Convexity survives intersections and can fail for unions. A fourth, once equalities and nonnegativity are the description, is to accept a solution of \(B x_B = b\) without checking the sign of \(x_B\). That point may leave the polyhedron.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""Constructing a basic feasible solution is the algebra behind the vertex test: pick independent columns, solve, and keep the point only when it is nonnegative. A linear objective that is bounded on a nonempty polyhedron of this form attains its optimum at one of those points. Later, a method that minimizes a linear model over a polyhedron can ask only for an extreme point of that model.""",
        },
    ]
    save_explainer("polyhedra-extreme-points", "Polyhedra and extreme points", sections)


def expl_bfs():
    sections = [
        {
            "heading": "The idea",
            "figure": BASIS,
            "figure_alt": A_BASIS,
            "body_md": r"""Standard form describes the feasible set by \(Ax = b\) and \(x \ge 0\). Assume \(A\) has full row rank, with \(m\) rows and \(n\) columns, and \(n \ge m\). A basis is a choice of \(m\) independent columns, written \(B\). The remaining columns are nonbasic.

Set the nonbasic variables to zero and solve the square system \(B x_B = b\). The solution \(x_B = B^{-1} b\), with zeros elsewhere, is a basic solution. It is a basic feasible solution when \(x_B \ge 0\). A negative entry means the columns were independent and the point is still outside the polyhedron. A zero entry among the basic variables is allowed. The point is feasible, and the basis is called degenerate.

If the feasible set is nonempty, it has at least one basic feasible solution. If in addition the linear objective is bounded below, the minimum is attained, and it is attained at a basic feasible solution. Searching the whole polyhedron can therefore be replaced by searching these points. There are finitely many bases, hence finitely many candidates, though listing all of them is not the practical algorithm.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""With the columns of \(B\) independent,
\[
x_B = B^{-1} b, \qquad x_N = 0.
\]
Feasibility is \(x_B \ge 0\). When \(B\) is diagonal with positive entries \(a\) and \(d\) and the right-hand side is \((p, q)\), the basic variables are \(p/a\) and \(q/d\). The slack basis of \(Ax + s = b\) is the identity on the slack columns, so it is feasible exactly when \(b \ge 0\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Take \(x_1 + 2x_2 + x_3 = 21\) and \(x_1 + x_2 + x_4 = 14\), and choose columns 1 and 2. The basis matrix is \(\begin{bmatrix} 1 & 2 \\ 1 & 1 \end{bmatrix}\), with determinant \(-1\). Solving gives \(x_1 = 7\) and \(x_2 = 7\), both nonnegative, and the slacks are zero.

The bench sum is 14. Check the equalities: \(7 + 14 = 21\) and \(7 + 7 = 14\). A different basis, for example the two slack columns, would give a different feasible point, \(x_3 = 21\) and \(x_4 = 14\). Both points are basic and feasible. Which one is optimal depends on a cost that this construction does not use.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Invertibility is not feasibility. The determinant test and the sign test answer different questions, and both are required. A second miss is to set the basic variables to zero and solve for the others. That reverses the definition and usually violates the equalities. A third is to treat a feasible point with more than \(m\) positive variables as basic. It can be a convex combination of basic feasible solutions, and then it is not extreme. A fourth is to reject a basic variable that equals zero. Zero is nonnegative. The basis is degenerate, and it is still feasible.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""Neighboring bases differ by one column. The edge between the two basic feasible solutions is a feasible direction, and the reduced cost says whether the objective falls along that edge. The ratio test says how far the step can go before a variable hits zero. If no basis is obvious, because the right-hand side is not nonnegative in slack form, an auxiliary problem builds the first basic feasible solution or proves that none exists.""",
        },
    ]
    save_explainer("basic-feasible-solutions", "Constructing basic feasible solutions", sections)


def expl_directions():
    sections = [
        {
            "heading": "The idea",
            "figure": ARR,
            "figure_alt": A_ARR,
            "body_md": r"""A basic feasible solution sits at a corner. A neighboring corner is reached by raising one nonbasic variable and adjusting the basic variables so the equalities still hold. If the entering index is \(j\), the direction \(d\) has a 1 in position \(j\), zeros in the other nonbasic positions, and basic part \(d_B = -B^{-1} A_j\). Then \(A d = 0\), so \(x + \theta d\) stays on the affine set for every step \(\theta\).

The objective changes at the rate \(c^T d\). That rate is the reduced cost \(\bar{c}_j = c_j - c_B^T B^{-1} A_j\). For a minimization, a negative reduced cost means the objective falls as \(\theta\) grows. The step cannot grow forever unless \(d_B\) has no negative component. If some basic coordinate of \(d\) is negative, that coordinate hits zero at a finite step. The longest feasible step is the smallest of those hitting times. That minimum is the ratio test.

If \(d_B \ge 0\) and the reduced cost is negative, every positive step is feasible and the objective is unbounded below. The sign of the reduced cost and the sign pattern of the direction answer different questions: one is about the objective, and the other is about staying inside \(x \ge 0\).""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""The reduced cost and the step are
\[
\bar{c}_j = c_j - c_B^T B^{-1} A_j, \qquad \theta = \min_{i : \bar{a}_{ij} > 0} \frac{\bar{b}_i}{\bar{a}_{ij}},
\]
where \(\bar{a}_j = B^{-1} A_j\) and \(\bar{b} = B^{-1} b\). The basic direction is \(d_B = -\bar{a}_j\). On a single row with multiplier \(u\) and column entry \(a\), the reduced cost collapses to \(c - u a\). The objective change on a feasible step is \(\theta \bar{c}_j\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Minimize \(-6x - y\) subject to \(x + y + s = 9\) and \(x + 2y + t = 17\), starting from the slack basis \(s = 9\), \(t = 17\). The basic cost is zero, so the reduced costs are \(-6\) and \(-1\). Enter \(x\). Its column is \((1, 1)\), and the ratios are \(9/1\) and \(17/1\). The step is 9.

The lane step cuts 54. The objective change is \(9 \cdot (-6) = -54\), so the cost falls by 54. The new point has \(x = 9\) and \(t = 8\), with \(s\) at zero. Entering \(y\) instead would also decrease the cost, at the slower rate \(-1\). Either choice is a descent step. The more negative rate is a pivot rule, not a requirement for correctness of the direction.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Taking the largest ratio instead of the smallest drives some basic variable negative. The test wants the first hitting time, which is the minimum. A second miss is to divide by a nonpositive column entry. Those rows do not block the step. A third is to read a negative reduced cost as unboundedness. Unboundedness also needs a direction that never goes negative. A fourth is to insist on the most negative reduced cost. Any negative reduced cost gives a feasible descent direction. The choice among them changes the path and not the sign of the slope.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""One simplex iteration packages this arithmetic: price the nonbasic columns, stop if every reduced cost is nonnegative, otherwise enter one negative column, stop if the ratio test finds no positive entry, and otherwise pivot on a minimum-ratio row. Repeating that iteration walks along edges. The first basis, when the slack basis is not feasible, comes from an auxiliary problem whose own reduced costs are computed in the same way.""",
        },
    ]
    save_explainer(
        "simplex-feasible-directions",
        "Basic directions, reduced costs, and the ratio test",
        sections,
    )


def expl_iteration():
    sections = [
        {
            "heading": "The idea",
            "figure": FALL,
            "figure_alt": A_FALL,
            "body_md": r"""The simplex method walks from one basic feasible solution to a neighbor with a better objective, until no neighbor is better. For a minimization, the reduced costs are the slopes of those edges. If every reduced cost is nonnegative, the current basis is optimal: raising any nonbasic variable cannot decrease the cost.

If some reduced cost is negative, that column may enter. The ratio test then looks at the positive entries of the updated column. The smallest ratio names the basic variable that hits zero first, and that variable leaves. The basis changes by exactly one column. If the entering column has no positive entry, no basic variable ever hits zero, the step may be arbitrarily long, and the objective is unbounded below.

Which negative reduced cost enters is a pivot rule. The most negative rule is one choice. Any other negative reduced cost is also a descent step. Different rules can take different paths and different numbers of pivots. The optimality test and the unboundedness test stay the same.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""At a basis \(B\), the reduced cost of column \(j\) is \(\bar{c}_j = c_j - c_B^T B^{-1} A_j\), and the updated column is \(\bar{a}_j = B^{-1} A_j\). The leaving row minimizes \(\bar{b}_i / \bar{a}_{ij}\) over positive \(\bar{a}_{ij}\). One blocking row with value \(p\) and positive entry \(r\) gives the ratio \(p/r\). After a step \(\theta\), the objective changes by \(\theta \bar{c}_j\). Optimality is \(\bar{c}_j \ge 0\) for every nonbasic \(j\). Unboundedness is some \(\bar{c}_j < 0\) with every entry of \(\bar{a}_j\) nonpositive.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Minimize \(-2x - 5y\) subject to \(x + y + s = 9\) and \(2x + y + t = 12\), from the slack basis. The reduced costs are \(-2\) and \(-5\). Enter \(y\). Its column is \((1, 1)\), and the ratios are 9 and 12, so the step is 9 and \(s\) leaves. The new point is \(y = 9\), \(t = 3\), with objective \(-45\).

The kiln value is -45. The reduced costs of the nonbasic columns at this basis are positive, so the basis is optimal. Entering \(x\) first would have been a legal descent step as well, with a less negative slope. That path is longer and ends at the same value. The optimum is unique.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""Stopping because a pivot was made is not the optimality test. The test is the sign of every reduced cost after the pivot. A second miss is to take the larger ratio and drive a basic variable negative. The leaving variable is a minimum-ratio row. A third is to treat one negative reduced cost with an all-nonpositive column as an ordinary pivot. There is no leaving variable, and the program is unbounded below. A fourth is to believe the most-negative rule is the only correct entering choice. It is one rule. Descent only needs some negative reduced cost.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""The iteration assumes a basic feasible solution is already in hand. The slack basis supplies one when the right-hand side is nonnegative. When it is not, or when the equalities were built with surpluses, an auxiliary problem with artificial variables either returns a first basis or proves that the original system is empty. That auxiliary problem is itself solved by the iteration just described.""",
        },
    ]
    save_explainer("simplex-method-iteration", "The simplex method", sections)


def expl_phase():
    sections = [
        {
            "heading": "The idea",
            "figure": ORTH,
            "figure_alt": A_ORTH,
            "body_md": r"""The simplex iteration needs a basic feasible solution to start from. A slack basis is feasible only when the right-hand side is nonnegative. A general standard-form system need not offer that basis. Phase I builds an auxiliary linear program whose feasible set is easy and whose optimal value answers the feasibility question.

First write the constraints as equalities and multiply any row with a negative right-hand side by \(-1\), so that \(b \ge 0\). Then add a nonnegative artificial variable to each row, and minimize the sum of the artificial variables. The original cost is ignored. The artificial columns form an identity basis, and \(a = b\) is a basic feasible solution of the auxiliary problem.

Run the ordinary simplex iteration on that auxiliary problem. If the optimal auxiliary value is positive, no point of the original system exists: every original feasible point would have given the artificials the value zero. If the optimal auxiliary value is zero, the artificials are zero at the optimal basis, and dropping them leaves a basic feasible solution of the original program. Phase II then restores the original cost and continues from that basis.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""With \(b \ge 0\), phase I is
\[
\text{minimize } \sum_i a_i \quad \text{subject to } Ax + a = b,\ x \ge 0,\ a \ge 0.
\]
At the artificial basis the reduced cost of an original column with entries \(a\) and \(b\), in a two-row problem, is \(-a - b\). The original system is feasible if and only if the auxiliary optimal value equals 0. A positive optimal value is a certificate of infeasibility, and the certificate does not depend on the original cost.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Consider \(x + y \ge 6\) and \(2x + y \ge 20\), with \(x, y \ge 0\). After surpluses and artificials, the rows are \(x + y - s + a = 6\) and \(2x + y - t + r = 20\). The artificial basis has objective \(6 + 20\).

The dock artificial is 26. The column of \(x\) is \((1, 2)\), so its phase-I reduced cost is \(-3\), and the ratios are \(6/1\) and \(20/2\). The step is 6. One further pivot drives the remaining artificial to zero and leaves the feasible point \(x = 10\), \(y = 0\). The original system is feasible, and this point is a legal start for the original objective. The original costs were never used.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""A positive value at the artificial basis is not infeasibility. It is only the starting value. Infeasibility is a positive value at optimality. A second miss is to fold the original cost into the auxiliary objective. A pivot can then trade a worse artificial sum for a better original cost and stop at a point that is not feasible for the original system. A third is to forget the sign flip on a negative right-hand side. The artificial basis \(a = b\) is feasible only when \(b \ge 0\).""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""With a feasible basis in hand, the original reduced costs take over and the simplex iteration optimizes the cost that the modeler actually cares about. The same standard form is the starting point for the dual linear program, read off from multipliers on the equalities. Other algorithms for linear programs, built from scaled quadratic models or from a perturbed system of equations, assume the same feasible region and do not need this auxiliary basis as their first step.""",
        },
    ]
    save_explainer("simplex-phase-one", "Finding an initial basic feasible solution", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    bank_standard()
    bank_graphical()
    bank_polyhedra()
    bank_bfs()
    bank_directions()
    bank_iteration()
    bank_phase()
    expl_standard()
    expl_graphical()
    expl_polyhedra()
    expl_bfs()
    expl_directions()
    expl_iteration()
    expl_phase()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    banned = (
        "graz",
        "boyd",
        "nocedal",
        "vandenberghe",
        "hefferon",
        "wikibook",
        "textbook",
        "university",
        "professor",
        "lecture",
        "syllabus",
        "cambridge",
        "springer",
    )
    ids = [
        "lp-standard-form",
        "lp-graphical-solution",
        "polyhedra-extreme-points",
        "basic-feasible-solutions",
        "simplex-feasible-directions",
        "simplex-method-iteration",
        "simplex-phase-one",
    ]
    private = {
        "lp-standard-form": "The ribbon slack is 19",
        "lp-graphical-solution": "The shed level is 18",
        "polyhedra-extreme-points": "The yard value is 65",
        "basic-feasible-solutions": "The bench sum is 14",
        "simplex-feasible-directions": "The lane step cuts 54",
        "simplex-method-iteration": "The kiln value is -45",
        "simplex-phase-one": "The dock artificial is 26",
    }
    bad = False
    totals = Counter()
    for sid in ids:
        exp = json.load(open(os.path.join(root, "skilltree", "explainers", sid + ".json"), encoding="utf-8"))
        n = doc_words(exp["sections"])
        bank = json.load(open(os.path.join(root, "skilltree", "bank", sid + ".json"), encoding="utf-8"))
        blob = json.dumps(exp) + json.dumps(bank)
        hits = [w for w in banned if w in blob.lower()]
        figs = sum(1 for q in bank["questions"] if q.get("figure"))
        deep = sum(1 for q in bank["questions"] if q.get("type") in DEEP_TYPES)
        kinds = Counter(q.get("type") for q in bank["questions"])
        totals.update(kinds)
        print(f"{sid}: words {n}, figures {figs}/12, deep {deep}, types {dict(kinds)}")
        if not 250 <= n <= 500:
            print("  word count outside 250-500")
            bad = True
        if hits:
            print("  banned", hits)
            bad = True
        if figs < 9:
            print("  fewer than 9 figures")
            bad = True
        if deep < deep_quota(12):
            print("  deep-type quota miss")
            bad = True
        if private[sid] not in json.dumps(exp):
            print("  worked-example marker missing")
            bad = True
        if private[sid] in json.dumps(bank):
            print("  worked example reused in the bank")
            bad = True
    print("totals", dict(totals))
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
