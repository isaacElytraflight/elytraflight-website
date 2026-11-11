#!/usr/bin/env python3
"""Generate nonlinear-optimization batch NB5 banks and explainers.

Skills: optimization-problem-formulation, graphical-2d-optimization,
optimization-problem-classes, local-global-minima, existence-of-minimizers,
first-order-optimality, second-order-optimality, stationary-point-classification,
convex-optimality-global, quadratic-function-minimization.

Closed-form answers live here. skilltree/verify_nlo_nb5.py recomputes the
numeric ones and does not import this file. Symbolic keys are checked by
the shared harness.
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
    disk_fig,
    ellipse_axes,
    filled_ellipse_fig,
    halfspace_fig,
    level_curves_fig,
    matrix_fig,
    orthant_fig,
    plane_vectors,
    plot,
    segment_fig,
    simplex_fig,
    two_disks_fig,
)

BOWL = plot(lambda t: 0.16 * (t - 0.3) ** 2 + 0.4, -0.4, 2.2, "t", "f", "a curve bending upward")
A_BOWL = "A curve of one variable, drawn on labeled axes."
WIGGLE = plot(lambda t: 0.22 * (t - 1.15) ** 3 - 0.5 * (t - 1.15) + 1.05, -0.15, 2.5, "t", "f", "a curve with a rise and a dip")
A_WIGGLE = "A curve of one variable, drawn on labeled axes."
SLOPE = plot(lambda t: -0.32 * t + 1.55, 0.0, 2.3, "t", "f", "a decreasing curve")
A_SLOPE = "A curve of one variable, drawn on labeled axes."
GROW = plot(lambda t: 0.18 * (2.1 ** t), 0.0, 2.2, "t", "f", "a rising curve")
A_GROW = "A curve of one variable, drawn on labeled axes."
LEVELS = level_curves_fig("nested ellipses")
A_LEVELS = "Three nested ellipses centered at the origin."
HALF = halfspace_fig("a half-plane")
A_HALF = "A straight boundary with one side shaded."
DISK = disk_fig("a filled disk")
A_DISK = "A filled disk centered on the axes."
TWO = two_disks_fig("two disks")
A_TWO = "Two filled disks with a gap between them."
SEG = segment_fig("a segment")
A_SEG = "A solid segment joins two marked points on a dashed line."
SIMP = simplex_fig("a segment in the first quadrant")
A_SIMP = "A segment joining the two axis intercepts."
HESS = matrix_fig([["a", "b"], ["b", "c"]], "a symmetric array")
A_HESS = "A 2 by 2 array with matching off-diagonal labels."
GRAD = plane_vectors([(1.15, 0.55, "g")], "one arrow from the origin")
A_GRAD = "One arrow leaves the origin in the plane."
PAIR = plane_vectors([(1.2, 0.25, "g"), (-0.15, 1.05, "d")], "two arrows from the origin")
A_PAIR = "Two arrows leave the origin."
ELL = ellipse_axes("axis-aligned ellipse")
A_ELL = "An ellipse centered at the origin, longer along the first axis."
FILL = filled_ellipse_fig("a shaded elliptical disk")
A_FILL = "A shaded elliptical disk centered on the axes."
DENT = dented_quad_fig("a dented quadrilateral")
A_DENT = "A four-sided region with one corner pushed in."
ORTH = orthant_fig("the first quadrant")
A_ORTH = "The closed first quadrant, shaded."


def bank_formulation():
    b = Bank("optimization-problem-formulation")
    b.mc(1,
         "An optimization problem is named by",
         ["a decision vector, an objective, and a feasible set",
          "the objective alone, because the domain is always all of real space",
          "a constraint list with no objective",
          "the optimal value alone"],
         0,
         r"The decision vector is what you may choose, the objective is the quantity you compare, and the feasible set is the choices that are allowed. An objective with no set is not yet a problem: the set might be all of space, a discrete grid, or a region cut out by constraints. A constraint list without an objective has no ranking of the feasible points. The optimal value is a result of the problem, not one of the three pieces that define it.",
         HALF, A_HALF)
    b.num(1,
          r"Each crate uses 3 fasteners and 2 labels. You have 18 fasteners and 10 labels, and you want as many crates as possible. What is the largest whole number of crates?",
          5, "1",
          r"Fasteners allow at most \(18/3 = 6\) crates, and labels allow at most \(10/2 = 5\). Both resources have to hold, so the feasible whole numbers stop at 5. That number is the optimal value of the maximization. Reporting 6 uses only the fasteners. Reporting 18 or 10 reports a stock level, which is data, not the objective. Reporting 0 is feasible and is the worst, not the best.",
          ORTH, A_ORTH)
    b.mc(1,
         r"Maximizing a function \(f\) is the same problem as minimizing",
         [r"\(1/f\), whenever \(f\) is never zero",
          r"\(f\) itself, because a maximizer is always a minimizer",
          r"\(-f\)",
          "the feasible set, leaving the objective unchanged"],
         2,
         r"The values of \(-f\) are the values of \(f\) with the order reversed, so a maximizer of \(f\) is a minimizer of \(-f\) and the optimal values are negatives of each other. The reciprocal does not reverse order on the whole line, and it is undefined at zero. Keeping \(f\) and switching the word from max to min searches for the other end of the range. Changing the feasible set and keeping the objective is a different problem.",
         SLOPE, A_SLOPE)
    b.order(2,
            "Put these steps in the order used to write a maximization as a minimization.",
            ["Name the decision variables and the set they are drawn from.",
             "Write the goal as a function of those variables and replace it by its negative.",
             "Describe the feasible set by every restriction the variables must satisfy.",
             "Keep the optimal value separate from the set of solutions that attain it."],
            r"The variables come first, because both the objective and the constraints are statements about them. The sign flip turns a maximization into a minimization before the constraints are attached. The feasible set is then the part of the variable space that survives every restriction. Only after that split does it make sense to ask which feasible points attain the best value, and what that value is. Starting from the optimal value has nothing to compute yet.",
            SEG, A_SEG)
    b.multi(2,
            r"You minimize \(x^2 + y^2\) over the line \(x + y = 4\). Which statements hold?",
            [r"The decision variable is a vector in the plane.",
             "The problem is unconstrained.",
             "The optimal value is a number, and a solution is a point.",
             r"Minimizing the negative of the objective is maximizing \(x^2 + y^2\).",
             "Every feasible point is a solution."],
            [0, 2, 3],
            r"The unknown is a pair \((x, y)\), so the decision variable lives in the plane. The optimal value is the best number the objective reaches, and a solution is a feasible pair that reaches it. Minimizing \(-(x^2 + y^2)\) is the same search as maximizing \(x^2 + y^2\)."
            "\n"
            r"• The equality \(x + y = 4\) removes most of the plane, so the problem is constrained."
            "\n"
            r"• On that line the squared distance from the origin is not constant. The point \((2, 2)\) is the closest, and \((0, 4)\) is farther, so not every feasible point is a solution.",
            LEVELS, A_LEVELS)
    b.mc(2,
         r"An unconstrained problem whose decision variable lies in \(\mathbb{R}^n\) has feasible set",
         [r"a polyhedron cut out by linear inequalities",
          r"all of \(\mathbb{R}^n\)",
          "a discrete subset of the integers",
          "the empty set"],
         1,
         r"Unconstrained means the only restriction is the space the variable already lives in. For a real vector of length \(n\), that space is \(\mathbb{R}^n\). Linear inequalities cut out a polyhedron and make the problem constrained. An integer restriction makes it discrete. The empty set is an infeasible problem, which is a different failure.",
         ORTH, A_ORTH)
    b.find_error(3,
                 r"A note formulates a price \(p \ge 0\) that maximizes revenue \(r(p) = 12p - 3p^2\). Exactly one step is false.",
                 [r"The decision variable is the price \(p\).",
                  "The feasible set is the nonnegative reals.",
                  r"Maximizing \(r\) is the same problem as minimizing \(r\), because the maximizer and the minimizer coincide.",
                  "A solution is a feasible price, and the optimal value is the revenue at that price."],
                 2,
                 r"The price is the decision variable, and \(p \ge 0\) is the feasible set. When a maximizer exists, the optimal value is the revenue there and the solution is that price. The false step is the claim that maximizing \(r\) is minimizing \(r\). Those two searches run in opposite directions. The minimization with the same solutions is the minimization of \(-r\).",
                 [r"Maximizing \(r\) is minimizing \(-r\), and those two objectives are not the same function.",
                  "The price is not the decision variable.",
                  "The feasible set includes negative prices."],
                 0,
                 SLOPE, A_SLOPE)
    b.num(3,
          r"Minimize \((x - 4)^2 + (y + 1)^2 + 5\) with no constraints. What is the first coordinate of a minimizer?",
          4, "1",
          r"The added 5 does not depend on the decision, so it cannot move the minimizer. Each square is nonnegative and equals zero at \(x = 4\) and \(y = -1\), so that point is the unique minimizer and the optimal value is 5. Reporting \(-1\) gives the second coordinate. Reporting 5 gives the optimal value, which is not a coordinate. Reporting 0 is the squared distance at the minimizer, again not a coordinate.",
          BOWL, A_BOWL)
    b.mc(3,
         "A problem whose decision variable is required to be an integer is",
         ["continuous and unconstrained",
          "infeasible whenever the objective is linear",
          "the same problem as the one with the integer restriction dropped",
          "discrete"],
         3,
         r"An integer restriction puts the decision in a discrete set. Dropping it produces a different, usually larger, feasible set, so the optimal value can only improve or stay the same, and a solution of the relaxed problem need not be a solution of the integer problem. A linear objective does not make an integer problem infeasible. A continuous unconstrained problem allows every real vector.",
         SIMP, A_SIMP)
    b.mc(4,
         r"Minimize \(x + 2y\) over the triangle with vertices \((0, 0)\), \((6, 0)\), and \((0, 3)\). A minimizer is",
         [r"\((0, 0)\)",
          r"\((6, 0)\)",
          r"\((0, 3)\)",
          r"\((2, 1)\)"],
         0,
         r"The objective values at the three vertices are \(0\), \(6\), and \(6\). A linear function on a triangle attains its minimum at a vertex, so the minimizer is \((0, 0)\) and the optimal value is \(0\). The other two vertices tie for the maximum. The centroid \((2, 1)\) has value \(4\), which sits strictly between the minimum and the maximum, so it is not a solution.",
         SIMP, A_SIMP, preview=["graphical-2d-optimization"])
    b.num(4,
          r"Minimize \(3x + 4\) over the feasible set \(\{1, 2, 5\}\). What is the optimal value?",
          7, "1",
          r"The three feasible values are \(3\cdot 1 + 4 = 7\), \(10\), and \(19\). The smallest is 7, attained at \(x = 1\). That number is the optimal value. The point \(x = 1\) is a solution, not the value. The number 19 is the largest feasible value, which would be the answer to the maximization. The number 4 is the constant term, not a feasible objective value.",
          SEG, A_SEG, preview=["optimization-problem-classes"])
    b.mc(4,
         r"For \(f(t) = e^{t}\) on the whole real line, the minimization of \(f\)",
         [r"has a solution at \(t = 0\)",
          "is infeasible",
          "has optimal value 0 and has no solution",
          r"has optimal value 1, attained at \(t = 0\)"],
         2,
         r"Every value \(e^{t}\) is positive, and the values get arbitrarily close to 0 as \(t\) goes to \(-\infty\), so the infimum is 0. No real \(t\) makes the exponential equal 0, so the argmin set is empty: there is an optimal value and no minimizer. The point \(t = 0\) gives the value 1, which is not the infimum. The domain is nonempty, so the problem is feasible.",
         GROW, A_GROW, preview=["local-global-minima"])
    b.save()


def bank_graphical():
    b = Bank("graphical-2d-optimization")
    b.mc(1,
         r"The level lines of the linear objective \(x + 3y\) are",
         ["circles centered at the origin",
          "the feasible set itself",
          r"straight lines of slope \(-1/3\)",
          "parabolas opening upward"],
         2,
         r"A level of \(x + 3y\) is the line \(y = -x/3 + c/3\), so the slope is \(-1/3\). The gradient \((1, 3)\) is perpendicular to those lines and points toward larger values. Circles are the levels of a squared distance. Parabolas are the levels of a quadratic that is not linear. The feasible set is drawn once. The level lines are a separate family that you slide across it.",
         GRAD, A_GRAD)
    b.num(1,
          r"Minimize \(x + y\) over the triangle with vertices \((2, 1)\), \((6, 1)\), and \((2, 5)\). What is the optimal value?",
          3, "1",
          r"The vertex values are \(2 + 1 = 3\), \(6 + 1 = 7\), and \(2 + 5 = 7\). A linear objective on a triangle attains its minimum at a vertex, so the optimal value is 3, at \((2, 1)\). Reporting 7 gives the maximum. Reporting 2 or 1 or 5 or 6 reports a coordinate of a vertex rather than the objective.",
          SIMP, A_SIMP)
    b.mc(1,
         "The contact point of the lowest level line that still meets the feasible set is",
         ["a maximizer",
          "a minimizer, and the level is the optimal value",
          "always the centroid of the feasible set",
          "infeasible, because the line has just left the set"],
         1,
         r"Sliding the level in the direction that decreases the objective, and stopping at the last contact, selects a minimizer. The level at contact is the optimal value. The opposite slide selects a maximizer. The centroid is a special point of a triangle and need not lie on the supporting level. The last contact is feasible by construction. The next parallel line, the one that misses, is the one that has left the set.",
         LEVELS, A_LEVELS)
    b.order(2,
            "Put these steps in the order used to solve a planar problem from a sketch.",
            ["Sketch the feasible set in the plane.",
             "Draw one level line of the objective and mark the direction in which the objective decreases.",
             "Slide that line in the decreasing direction until it is about to leave the feasible set.",
             "Read a contact point as a candidate, and keep the whole contact set if the line lies along an edge."],
            r"The feasible set is the picture you are allowed to land on, so it is drawn first. A single level line shows the shape of the objective, and the decrease direction tells you which way to slide. The last contact is the candidate set. If that contact is one point, you have a unique minimizer. If the level lies along an edge, every point of that edge is a minimizer and they share one optimal value. Comparing coordinates before drawing the set has nothing to compare.",
            HALF, A_HALF)
    b.multi(2,
            r"On the triangle with vertices \((2, 1)\), \((6, 1)\), and \((2, 5)\), which statements hold?",
            [r"\((6, 1)\) minimizes \(y - x\).",
             r"\((2, 1)\) minimizes \(y - x\).",
             r"The optimal value of \(y - x\) is \(-5\).",
             r"\((2, 5)\) minimizes \(x - y\).",
             r"Every vertex minimizes \(y - x\)."],
            [0, 2, 3],
            r"The values of \(y - x\) are \(1 - 2 = -1\) at \((2, 1)\), \(1 - 6 = -5\) at \((6, 1)\), and \(5 - 2 = 3\) at \((2, 5)\). The smallest is \(-5\), at \((6, 1)\) only."
            "\n"
            r"• The values of \(x - y\) are \(1\), \(5\), and \(-3\). The smallest is \(-3\), at \((2, 5)\)."
            "\n"
            r"• \((2, 1)\) is not a minimizer of \(y - x\), and the three vertices do not share one value of \(y - x\).",
            SIMP, A_SIMP)
    b.num(2,
          r"Maximize \(x + y\) over the triangle with vertices \((2, 1)\), \((6, 1)\), and \((2, 5)\). What is the optimal value?",
          7, "1",
          r"The vertex values are 3, 7, and 7. The largest is 7, attained at both \((6, 1)\) and \((2, 5)\), so the maximizer is not unique and the optimal value still is. Reporting 3 gives the minimum. Reporting 6, 2, or 5 reports a coordinate.",
          SIMP, A_SIMP)
    b.find_error(3,
                 r"A note claims that \((6, 1)\) minimizes \(x + y\) on the triangle with vertices \((2, 1)\), \((6, 1)\), and \((2, 5)\). Exactly one step is false.",
                 [r"The level lines of \(x + y\) are the lines \(x + y = c\).",
                  r"Increasing \(c\) moves the line in the direction of the gradient \((1, 1)\).",
                  r"Among the three vertices, \((6, 1)\) gives the smallest value of \(x + y\).",
                  "A vertex where a linear objective is smallest is a minimizer on a triangle."],
                 2,
                 r"The levels really are the lines \(x + y = c\), and the gradient \((1, 1)\) points toward larger \(c\). A linear function on a triangle attains its minimum at a vertex. The false step is the comparison: the values are 3 at \((2, 1)\) and 7 at the other two vertices, so \((6, 1)\) is a maximizer, not the vertex with the smallest value.",
                 [r"\((6, 1)\) has objective 7, and \((2, 1)\) has objective 3, so \((6, 1)\) is not the smallest.",
                  r"The level lines of \(x + y\) are not straight.",
                  "A linear objective on a triangle need not attain its minimum at a vertex."],
                 0,
                 SIMP, A_SIMP)
    b.num(3,
          r"Minimize \(3x + y\) over the rectangle with corners \((1, 2)\), \((4, 2)\), \((4, 6)\), and \((1, 6)\). What is the optimal value?",
          5, "1",
          r"The corner values are \(3 + 2 = 5\), \(12 + 2 = 14\), \(12 + 6 = 18\), and \(3 + 6 = 9\). A linear objective on a rectangle attains its minimum at a corner, so the optimal value is 5, at \((1, 2)\). Reporting 9 gives the other corner on the left edge. Reporting 18 gives the maximum. Reporting 1 or 2 reports a coordinate.",
          ORTH, A_ORTH)
    b.mc(3,
         "When the decreasing level line comes to rest along an entire edge of a polygon,",
         ["only the midpoint of that edge is a minimizer",
          "the problem is infeasible",
          "no minimizer exists",
          "every point of that edge is a minimizer"],
         3,
         r"A linear objective is constant on a level line. If that line contains an edge, every point of the edge has the same objective value, and the neighboring feasible points are worse or equal, so the whole edge is optimal. The midpoint is one of those minimizers, not the only one. The edge is feasible, so the problem is not infeasible, and the minimizers exist.",
         SEG, A_SEG)
    b.num(4,
          r"Minimize \(x + 2y\) over the triangle with vertices \((0, 2)\), \((3, 0)\), and \((4, 3)\). What is the optimal value?",
          3, "1",
          r"The vertex values are \(0 + 4 = 4\), \(3 + 0 = 3\), and \(4 + 6 = 10\). The smallest is 3, at \((3, 0)\). Reporting 4 uses the vertical intercept. Reporting 10 uses the far vertex. Reporting 0 is a coordinate of a vertex, and the objective is not zero anywhere on this triangle.",
          SIMP, A_SIMP, preview=["lp-graphical-solution"])
    b.mc(4,
         "A linear objective on a nonempty polygon with finitely many vertices",
         ["is unbounded below whenever the polygon is bounded",
          "attains its minimum at a vertex, and possibly along a whole edge",
          "always has a unique minimizer",
          "is infeasible"],
         1,
         r"On a nonempty bounded polygon a linear function attains its minimum, and the minimum is attained at a vertex. If the level line happens to contain an edge, the minimizer is that whole edge, so uniqueness can fail. Boundedness prevents the objective from running off to \(-\infty\). A nonempty polygon is feasible.",
         HALF, A_HALF, preview=["lp-graphical-solution"])
    b.mc(4,
         r"Minimize \(-x\) over the closed first quadrant \(x \ge 0\), \(y \ge 0\).",
         ["the minimizer is the origin and the optimal value is 0",
          "the problem is infeasible",
          "the problem is unbounded below and has no minimizer",
          r"the optimal value is 1, attained at \(x = 1\)"],
         2,
         r"The objective \(-x\) decreases without bound as \(x\) grows, and every large positive \(x\) is feasible. There is no lowest level line that still touches the quadrant, so there is no minimizer and the optimal value is \(-\infty\). The origin gives the value 0, which is feasible and not a lower bound. The point \(x = 1\) gives \(-1\), which is worse than the origin and still not a minimum. The quadrant is nonempty.",
         ORTH, A_ORTH, preview=["lp-graphical-solution"])
    b.save()


def bank_classes():
    b = Bank("optimization-problem-classes")
    b.mc(1,
         "A problem is a linear program when",
         ["the objective and every constraint function are affine",
          "the objective is a squared norm and the constraints are linear",
          "the objective is convex and the constraints are arbitrary",
          "the decision variable is required to be a matrix"],
         0,
         r"A linear program has an affine objective and affine equalities and inequalities. A squared norm is a quadratic objective, which makes a quadratic program when the constraints stay affine. Convexity of the objective is the wider class, and it allows constraints that are not affine as long as the feasible set stays convex. The shape of the decision variable, vector or matrix, does not decide the class.",
         HALF, A_HALF)
    b.num(1,
          r"The matrix \(Q = \begin{bmatrix} 2 & 6 \\ 0 & 4 \end{bmatrix}\) and its symmetric part define the same quadratic form. What is one off-diagonal entry of that symmetric part?",
          3, "1",
          r"The quadratic form uses \(x^T Q x = x^T((Q + Q^T)/2) x\). The cross term \(6xy\) is split equally, so each off-diagonal entry of the symmetric part is \(3\). The diagonal entries stay \(2\) and \(4\). Reporting 6 keeps the unsymmetrized upper entry. Reporting 0 uses the lower entry of \(Q\) before the split. Reporting 2 uses a diagonal entry.",
          HESS, A_HESS)
    b.mc(1,
         "A convex optimization problem minimizes a convex objective over",
         ["a nonconvex feasible set",
          "a finite set of integers",
          "a convex feasible set",
          "the complement of a ball"],
         2,
         r"Convexity of the problem needs both pieces: a convex objective and a convex feasible set. A nonconvex set, including the complement of a ball, can hide a local solution that is not global even when the objective is convex. A finite integer set is discrete. It is not a convex set unless it contains only one point.",
         FILL, A_FILL)
    b.multi(2,
            "Which of these are quadratic programs?",
            [r"Minimize \(x^2 + 3y\) subject to \(x + y \le 1\).",
             r"Minimize \(x + y\) subject to \(x^2 + y^2 \le 1\).",
             r"Minimize \(x^2 - 4xy + y^2\) subject to \(x \ge 0\) and \(y \ge 0\).",
             r"Minimize \(\lvert x \rvert + \lvert y \rvert\) subject to \(x + y = 1\).",
             r"Minimize \(\sin x\) subject to \(x \le 2\)."],
            [0, 2],
            r"A quadratic program has a quadratic objective and affine constraints. The first objective is quadratic and the inequality is affine. The third objective is quadratic, indefinite even, and the constraints are affine, so it is a quadratic program that is not convex."
            "\n"
            r"• A linear objective with a disk constraint is not a quadratic program: the constraint is quadratic."
            "\n"
            r"• An absolute-value objective is piecewise linear, not quadratic."
            "\n"
            r"• A sine is neither quadratic nor affine.",
            ELL, A_ELL)
    b.order(2,
            "Put these steps in the order used to classify a smooth problem with inequality constraints.",
            ["Check whether the objective is affine, quadratic, or neither.",
             "Check whether every constraint function is affine.",
             "If the objective is quadratic, replace its matrix by the symmetric part before any eigenvalue test.",
             "Decide convexity from that Hessian on the feasible set, together with convexity of the set."],
            r"The objective's algebraic degree is the first split, because it separates linear programs, quadratic programs, and general nonlinear programs. Affine constraints are what keep a quadratic objective inside the quadratic-program class. The symmetric part is the matrix whose eigenvalues are meaningful, and it does not change the quadratic form. Convexity is the last label: it needs a positive semidefinite Hessian everywhere it is used, and a convex feasible set. Testing eigenvalues before symmetrizing reads a matrix the form does not determine.",
            HESS, A_HESS)
    b.mc(2,
         r"Replacing a square matrix \(Q\) by \((Q + Q^T)/2\) does not change the quadratic form because",
         [r"\(x^T Q x = x^T ((Q + Q^T)/2) x\) for every \(x\)",
          r"the off-diagonal entries of \(Q\) never enter \(x^T Q x\)",
          "every square matrix is already symmetric",
          r"the eigenvalues of \(Q\) and of \(Q^T\) differ by a sign"],
         0,
         r"The skew part \((Q - Q^T)/2\) contributes nothing to \(x^T Q x\), so the symmetric part carries the whole form. Off-diagonal entries do enter, through the cross terms, which is why they are averaged rather than dropped. A general square matrix is not symmetric. \(Q\) and \(Q^T\) have the same eigenvalues, not opposite ones.",
         HESS, A_HESS)
    b.sym(3,
          r"The form \(a x^2 + b xy + c y^2\) comes from a symmetric \(2 \times 2\) matrix. Write the determinant of that matrix as an expression in a, b, and c.",
          "a*c-b^2/4",
          {"a": (-3, 3), "b": (-3, 3), "c": (-3, 3)},
          r"The symmetric matrix is \(\begin{bmatrix} a & b/2 \\ b/2 & c \end{bmatrix}\), because the cross term \(bxy\) is split across the two off-diagonal entries. Its determinant is \(ac - (b/2)^2 = ac - b^2/4\)."
          "\n"
          r"• \(ac - b^2\) forgets to halve the cross term before squaring."
          "\n"
          r"• \(a + c\) is the trace, not the determinant."
          "\n"
          r"• \(ac - b/2\) subtracts the off-diagonal entry instead of its square.",
          ["c*a-b^2/4", "a*c-(b*b)/4", "a*c-(b/2)^2"],
          fig=HESS, alt=A_HESS)
    b.num(3,
          r"The objective \(\tfrac12 x^T A x\) has \(A = \begin{bmatrix} 4 & 2 \\ 2 & 4 \end{bmatrix}\). What is the smaller eigenvalue of the Hessian?",
          2, "1",
          r"With the factor one half and a symmetric \(A\), the Hessian is \(A\). The trace is 8 and the determinant is \(16 - 4 = 12\), so the eigenvalues sum to 8 and multiply to 12. They are 6 and 2. The smaller one is 2, which is positive, so this quadratic is strictly convex. Reporting 6 gives the larger eigenvalue. Reporting 4 gives a diagonal entry. Reporting 12 gives the determinant.",
          ELL, A_ELL)
    b.find_error(3,
                 r"A note claims that minimizing \(x^2 - y^2\) over the unit disk is a convex program. Exactly one step is false.",
                 [r"The objective \(x^2 - y^2\) is a quadratic function.",
                  "The unit disk is a convex set.",
                  r"The Hessian of \(x^2 - y^2\) is positive semidefinite at every point.",
                  "A convex objective on a convex set defines a convex program."],
                 2,
                 r"The objective is quadratic, the unit disk is convex, and a convex objective on a convex set really is a convex program. The false step is the Hessian claim. The Hessian is \(\operatorname{diag}(2, -2)\), which has a negative eigenvalue, so the objective is not convex. The problem is a nonconvex quadratic over a convex set.",
                 ["The Hessian has eigenvalues 2 and -2, so it is not positive semidefinite.",
                  "The unit disk is not a convex set.",
                  r"\(x^2 - y^2\) is not a quadratic."],
                 0,
                 ELL, A_ELL)
    b.mc(4,
         "You can recognize a linear program because",
         ["the objective is a squared residual and the constraints are bounds",
          "the feasible set is a ball",
          "both the objective and the constraints are affine",
          "the Hessian is positive definite and the constraints are linear"],
         2,
         r"Affine data on both the objective and the constraints is the linear-program pattern. A squared residual is a quadratic objective. A ball is a quadratic constraint. A positive definite Hessian with linear constraints is a convex quadratic program, which includes linear programs only in the special case of a zero Hessian.",
         HALF, A_HALF, preview=["lp-standard-form"])
    b.num(4,
          r"A quadratic objective has Hessian \(P = \begin{bmatrix} 5 & 1 \\ 1 & 5 \end{bmatrix}\). What is the smaller eigenvalue of \(P\)?",
          4, "1",
          r"The trace is 10 and the determinant is \(25 - 1 = 24\), so the eigenvalues are the roots of \(\lambda^2 - 10\lambda + 24 = 0\), which factors as \((\lambda - 4)(\lambda - 6) = 0\). The smaller eigenvalue is 4. It is positive, so \(P\) is positive definite and the quadratic is strictly convex. Reporting 6 gives the larger eigenvalue. Reporting 5 gives a diagonal entry. Reporting 1 gives an off-diagonal entry.",
          HESS, A_HESS, preview=["svm-quadratic-program"])
    b.mc(4,
         "A nonconvex quadratic program",
         ["is always unbounded below",
          "is a linear program",
          "has a positive semidefinite Hessian",
          "can have a local minimizer that is not global"],
         3,
         r"An indefinite quadratic can bend up in one direction and down in another, so a point that is best in a neighborhood need not be best on the whole feasible set. The Hessian of a nonconvex quadratic is not positive semidefinite. The objective is not affine, so the problem is not a linear program. A nonconvex quadratic can still be bounded below on a bounded feasible set.",
         DENT, A_DENT, preview=["lp-graphical-solution"])
    b.save()


def bank_local():
    b = Bank("local-global-minima")
    b.mc(1,
         r"A point \(x^\star\) is a global minimizer of \(f\) on a feasible set when",
         [r"\(f(x^\star) \le f(x)\) for every feasible \(x\)",
          r"\(f(x^\star) \le f(x)\) for every feasible \(x\) in some ball around \(x^\star\)",
          r"\(f(x^\star) < f(x)\) for every \(x\) different from \(x^\star\), feasible or not",
          r"the gradient of \(f\) at \(x^\star\) is zero"],
         0,
         r"Global means the comparison runs over the whole feasible set. The same comparison restricted to a ball is the local definition. The strict inequality for every other point, including infeasible ones, is stronger than the definition and uses the wrong set. A zero gradient is a calculus test for an interior candidate. It is not the definition of a minimizer, and it is not required at a boundary minimizer.",
         BOWL, A_BOWL)
    b.num(1,
          r"Let \(f(t) = (t - 2)^2 + 3\) on the whole real line. What is the global minimum value?",
          3, "1",
          r"The square is nonnegative and equals zero at \(t = 2\), so the smallest value is 3, attained at that single point. The minimizer is strict. Reporting 2 gives the minimizer, not the value. Reporting 0 gives the square at the minimizer and drops the added 3. Reporting 7 is \(f(0)\), which is larger.",
          BOWL, A_BOWL)
    b.mc(1,
         r"The minimizer \(t = 2\) of \(f(t) = (t - 2)^2 + 3\) is strict because",
         ["the domain is an open interval",
          "every other real number has a strictly larger value",
          "the value 3 is attained at two different points",
          "the function is negative somewhere"],
         1,
         r"Strict means no other feasible point ties the value. Here \(f(t) - 3 = (t - 2)^2 > 0\) for every \(t \ne 2\). A tie at a second point would make the minimizer non-strict. Openness of the domain is not the reason, and this function is never negative.",
         BOWL, A_BOWL)
    b.multi(2,
            r"Let \(f(t) = (t^2 - 1)^2\) on the real line. Which statements hold?",
            [r"\(t = 1\) is a local minimizer.",
             r"\(t = -1\) is a local minimizer.",
             r"\(t = 0\) is a local minimizer.",
             r"\(t = 2\) is a local minimizer.",
             r"Both \(t = 1\) and \(t = -1\) are global minimizers."],
            [0, 1, 4],
            r"The function is a square, so it is nonnegative, and it equals zero at \(t = \pm 1\). Those two points are global minimizers, and each is strict inside a small enough neighborhood that excludes the other."
            "\n"
            r"• At \(t = 0\) the value is 1, and nearby points toward \(\pm 1\) have smaller values, so \(t = 0\) is not a local minimizer."
            "\n"
            r"• At \(t = 2\) the value is 9. A small step \(h\) to the left gives \(f(2 - h) = (3 - 4h + h^2)^2\), and for every \(0 < h < 4\) that square is strictly less than 9. Every ball around \(t = 2\) contains such a step, so \(t = 2\) is not a local minimizer. The smaller value at the distant point \(t = 1\) is a global comparison and is not the reason.",
            WIGGLE, A_WIGGLE)
    b.order(2,
            "Put these steps in the order used to certify a strict global minimizer.",
            ["Confirm the candidate is feasible.",
             "Evaluate the objective at the candidate.",
             "Show that every other feasible point has a strictly larger value.",
             "Conclude that the argmin set contains that point and no other."],
            r"An infeasible point is not a minimizer, so feasibility comes first. The value at the candidate is the number every other point must beat. The comparison has to cover the whole feasible set, not a neighborhood, because the claim is global, and it has to be strict, because the claim is uniqueness. The argmin conclusion is the last sentence, after the comparison has been made. Checking a neighborhood only certifies a local minimizer.",
            SEG, A_SEG)
    b.num(2,
          r"Let \(f(t) = e^{t} + 4\) on the whole real line. What is the infimum of \(f\)?",
          4, "1",
          r"The exponential is positive and gets arbitrarily close to 0, so \(f\) gets arbitrarily close to 4 and never reaches it or goes below it. The infimum is 4, and it is not a minimum: no minimizer exists. Reporting 5 uses \(f(0) = 1 + 4\). Reporting 1 uses the exponential at 0 and drops the shift.",
          GROW, A_GROW)
    b.find_error(3,
                 r"A note claims that \(f(t) = e^{t}\) attains a minimum on the real line. Exactly one step is false.",
                 [r"\(e^{t}\) is continuous.",
                  r"\(e^{t} > 0\) for every real \(t\).",
                  "The values get arbitrarily close to 0, so 0 is a value of the function.",
                  "A continuous function that attains a value equal to its infimum has a minimizer."],
                 2,
                 r"The exponential is continuous and positive. A continuous function that hits its infimum does have a minimizer. The false step confuses an infimum with a value: getting arbitrarily close to 0 does not mean some input produces 0. The infimum is 0 and the range is the positive reals, so the minimum is not attained.",
                 ["Getting arbitrarily close to 0 is not the same as equaling 0.",
                  r"\(e^{t}\) is not continuous.",
                  "Hitting the infimum does not produce a minimizer."],
                 0,
                 GROW, A_GROW)
    b.mc(3,
         "A non-strict global minimizer is a feasible point where the objective equals the optimal value and",
         ["the gradient is positive",
          "some other feasible point attains the same value",
          "the point fails to be a local minimizer",
          "the feasible set is a single point"],
         1,
         r"Non-strict means the inequality \(f(x^\star) \le f(x)\) holds for every feasible \(x\), and equality holds at some other feasible point. Each of those points is still a global minimizer, and each is a local minimizer. A positive gradient is a different test and is not part of the definition. A one-point feasible set cannot show a tie.",
         SEG, A_SEG)
    b.sym(3,
          r"The global minimizer of \((x - a)^2 + (y - b)^2\) is the point \((a, b)\). Write the squared Euclidean norm of that minimizer as an expression in a and b.",
          "a^2+b^2",
          {"a": (-4, 4), "b": (-4, 4)},
          r"The two squares are nonnegative and vanish together only at \((a, b)\), so that point is the unique global minimizer and the minimum value is 0. Its squared distance to the origin is \(a^2 + b^2\)."
          "\n"
          r"• \(a + b\) adds the coordinates instead of squaring them."
          "\n"
          r"• \((a + b)^2\) expands to \(a^2 + 2ab + b^2\), which is the square of the sum."
          "\n"
          r"• \(a^2 - b^2\) subtracts the second square.",
          ["b^2+a^2", "a*a+b*b"],
          fig=LEVELS, alt=A_LEVELS)
    b.mc(4,
         "A continuous function on a nonempty compact feasible set",
         ["attains a global minimum",
          "has an infimum that is never a value of the function",
          "is unbounded below",
          "has no local minimizer"],
         0,
         r"On a nonempty compact set in real space, a continuous function attains its infimum. That attained value is a global minimum, and every point where it is attained is a global minimizer, hence also a local one. The function is bounded on a compact set, so it cannot run off to \(-\infty\). Non-attainment needs a set that fails to be compact, or a function that fails to be continuous.",
         DISK, A_DISK, preview=["existence-of-minimizers"])
    b.num(4,
          r"Let \(f(t) = t^3 - 3t\) on the real line. The point \(t = 1\) is a local minimizer. What is \(f(1)\)?",
          -2, "1",
          r"Substituting gives \(1 - 3 = -2\). The derivative \(3t^2 - 3\) vanishes at \(t = \pm 1\), and the second derivative \(6t\) is positive at \(t = 1\), so the point is a strict local minimizer. It is not global: \(f(t)\) goes to \(-\infty\) as \(t\) goes to \(-\infty\). Reporting 2 gives \(f(-1)\), the local maximum value. Reporting 1 gives the location, not the value. Reporting \(-3\) drops the cubic term.",
          WIGGLE, A_WIGGLE, preview=["first-order-optimality"])
    b.mc(4,
         "The argmin set of a function",
         ["contains every stationary point",
          "is empty whenever the function is continuous",
          "can contain more than one point",
          "is a single point whenever the infimum is finite"],
         2,
         r"Any number of feasible points may share the optimal value, and then every one of them is a global minimizer. A finite infimum need not be attained, so the set can also be empty, and when it is nonempty it need not be a singleton. Stationary points include local maxima and saddles, which are not minimizers. Continuity does not by itself empty the argmin set.",
         TWO, A_TWO, preview=["convex-optimality-global"])
    b.save()


def bank_existence():
    b = Bank("existence-of-minimizers")
    b.mc(1,
         "A continuous real-valued function on a nonempty compact subset of real space",
         ["attains its minimum and its maximum",
          "is constant",
          "attains its minimum only when the set is a ball",
          "can be unbounded on that set"],
         0,
         r"This is the extreme-value conclusion in real space: continuity plus a nonempty compact domain gives an attained minimum and an attained maximum. The function need not be constant. Compactness is closed and bounded, not a requirement that the set be a ball. A continuous function on a compact set is bounded.",
         DISK, A_DISK)
    b.num(1,
          r"Minimize \((x - 3)^2 + y^2\) over the closed unit disk \(x^2 + y^2 \le 1\). What is the minimum value?",
          4, "1",
          r"The unconstrained bowl opens at \((3, 0)\), which lies outside the disk. On the disk the expression is the squared distance to \((3, 0)\), so the minimum is the squared distance from \((3, 0)\) to the nearest feasible point. That point is \((1, 0)\), and the squared distance is \(4\). Reporting 9 uses the squared distance from the origin to \((3, 0)\) and ignores the disk. Reporting 1 gives a coordinate of the contact point. The value 0 is the unconstrained minimum and is not feasible.",
          DISK, A_DISK)
    b.mc(1,
         r"A function \(f\) on \(\mathbb{R}^n\) is coercive when",
         [r"\(f\) is bounded",
          r"\(f(x)\) tends to \(+\infty\) as \(\lVert x \rVert\) tends to infinity",
          r"\(f\) has a stationary point",
          r"every sublevel set of \(f\) is open"],
         1,
         r"Coercivity is a statement about the behavior at infinity: the function eventually exceeds every height. A bounded function fails it. A stationary point is a derivative fact and can exist without coercivity, as with a sine. Sublevel sets of a continuous function are closed, not open, and coercivity is what makes the low ones bounded.",
         BOWL, A_BOWL)
    b.order(2,
            "Put these checks in the order used to argue that a minimizer exists.",
            ["If the feasible set is empty, stop: no minimizer exists.",
             "If the feasible set is nonempty and compact and the objective is continuous, conclude that a minimizer exists.",
             "If the feasible set is unbounded, test whether the objective tends to infinity as the norm does.",
             "If that coercivity test passes and the objective is continuous, conclude that a minimizer exists."],
            r"Emptiness ends the argument at once. A nonempty compact set is the direct extreme-value case, and it does not need a coercivity test. On an unbounded set the compact-set theorem does not apply, so the next check is whether sublevel sets are bounded, which is what coercivity gives. Only after that check does the unbounded case conclude. Testing coercivity on a set that is already compact is unnecessary, and it is the wrong tool for an empty set.",
            DISK, A_DISK)
    b.multi(2,
            "Which of these functions attain a global minimum on the stated domain?",
            [r"\(f(t) = t^2\) on the real line.",
             r"\(f(t) = e^{t}\) on the real line.",
             r"\(f(t) = t\) on the closed interval \([0, 3]\).",
             r"\(f(t) = t\) on the open interval \((0, 3)\).",
             r"\(f(t) = \sin t\) on the real line."],
            [0, 2, 4],
            r"The square \(t^2\) is continuous and coercive, so it attains the value 0. On the compact interval \([0, 3]\) the identity attains 0 at the endpoint. The sine attains \(-1\)."
            "\n"
            r"• The exponential gets arbitrarily close to 0 and never reaches it."
            "\n"
            r"• On the open interval the values get arbitrarily close to 0 and every positive value is still beaten by a smaller feasible input, so the infimum is not attained."
            "\n"
            r"The sine shows that coercivity is sufficient, not necessary: it attains its minimum without tending to infinity.",
            WIGGLE, A_WIGGLE)
    b.num(2,
          r"Minimize \(t + 1/t\) over \(t > 0\). What is the minimum value?",
          2, "1",
          r"The derivative is \(1 - 1/t^2\), which vanishes at \(t = 1\) on the positive line. The second derivative \(2/t^3\) is positive there, so the critical point is a local minimizer, and the value is \(1 + 1 = 2\). The same conclusion follows from \((\sqrt{t} - 1/\sqrt{t})^2 \ge 0\), which rearranges to \(t + 1/t \ge 2\). As \(t\) approaches 0 or infinity the function tends to infinity, so the local minimizer is global. Reporting 1 gives the location. Reporting 0 is not a value of this function.",
          BOWL, A_BOWL)
    b.find_error(3,
                 r"A note claims that \(e^{-t}\) attains its minimum on the half-line \(t \ge 0\). Exactly one step is false.",
                 [r"\(e^{-t}\) is continuous for every \(t \ge 0\).",
                  r"The half-line \(t \ge 0\) is closed and bounded.",
                  "A continuous function attains its minimum on a nonempty compact set.",
                  "A closed and bounded subset of the real line is compact."],
                 1,
                 r"The exponential is continuous, the extreme-value statement is right, and closed bounded subsets of the line are compact. The false step is the claim that the half-line is bounded. It is closed and unbounded, so the compact-set theorem does not apply. The function decreases toward 0 and never reaches it, so the infimum is not attained.",
                 ["The half-line is closed and unbounded, so it is not compact.",
                  r"\(e^{-t}\) is not continuous.",
                  "A continuous function on a nonempty compact set need not attain its minimum."],
                 0,
                 SLOPE, A_SLOPE)
    b.mc(3,
         "A continuous coercive function on a nonempty closed set",
         ["attains a minimum only if that set is bounded",
          "attains a global minimum",
          "is constant",
          "has every sublevel set empty"],
         1,
         r"Coercivity makes every sublevel set bounded. Continuity makes it closed. A nonempty closed set supplies at least one feasible value, so some sublevel set is nonempty, hence compact, and the function attains its minimum there. The set itself may be unbounded. The function need not be constant. The sublevel set at a feasible height is nonempty.",
         BOWL, A_BOWL)
    b.num(3,
          r"Let \(f(x, y) = x^2 + 4y^2 + 6\) on the plane. What is the global minimum value?",
          6, "1",
          r"Both squares are nonnegative, so \(f \ge 6\), and equality holds at the origin. The function is a polynomial, hence continuous, and it tends to infinity as the norm does, so the lower bound is attained. Reporting 4 uses the coefficient of \(y^2\). Reporting 1 would be the value of a square that this function does not have at the origin. Reporting 10 is \(f(2, 0)\), which is larger.",
          ELL, A_ELL)
    b.mc(4,
         "Existence of a minimizer does not name the point. For a smooth coercive function the minimizer is among",
         ["the stationary points",
          "the points where the function is negative",
          "the boundary of the unit ball, always",
          "the eigenvectors of the Hessian only"],
         0,
         r"A coercive smooth function attains a minimum, and an interior minimizer on an open domain has gradient zero. Finding the stationary points is the next search. The minimum value need not be negative. The unit ball is one compact set, not the location of every minimizer. Eigenvectors describe the Hessian, not the list of candidate points.",
         GRAD, A_GRAD, preview=["stationary-point-classification"])
    b.num(4,
          r"Let \(f(t) = t^4 - 4t\) on the real line. What is the global minimum value?",
          -3, "1",
          r"The derivative is \(4t^3 - 4 = 4(t^3 - 1)\), so the only real stationary point is \(t = 1\). The value there is \(1 - 4 = -3\). The second derivative \(12t^2\) is positive at \(t = 1\), and \(t^4\) dominates as \(\lvert t \rvert\) grows, so the function is coercive and this stationary value is the global minimum. Reporting 1 gives the location. Reporting \(-4\) drops the fourth-power term. Reporting 4 is the derivative coefficient, not a function value at the minimizer.",
          BOWL, A_BOWL, preview=["stationary-point-classification"])
    b.mc(4,
         r"Minimize \(e^{x}\) over the plane. This problem",
         ["has every point as a minimizer",
          "has optimal value 1, attained at the origin",
          "has no global minimizer",
          "has a minimizer at the origin because the gradient vanishes there"],
         2,
         r"For every point, moving left in \(x\) multiplies the value by a number smaller than 1, so no point is a local minimizer and none is global. The infimum is 0 and it is not attained. The origin has value 1 and gradient \((1, 0)\), which is not zero. The exponential is positive, so 1 is not a lower bound.",
         GROW, A_GROW, preview=["stationary-point-classification"])
    b.save()
def bank_first():
    b = Bank("first-order-optimality")
    b.mc(1,
         "At an interior local minimizer of a differentiable function,",
         ["the gradient is the zero vector",
          "the gradient is a feasible descent direction",
          "the function value is zero",
          "the Hessian is the zero matrix"],
         0,
         r"Fermat's necessary condition says that if a differentiable function has a local minimizer in the interior of the feasible set, the gradient there is zero. A nonzero gradient is a direction of increase, and its negative is a descent direction, so the point would not be a local minimizer. The function value need not be zero. The Hessian test is a second-order statement and is not required to vanish.",
         GRAD, A_GRAD)
    b.num(1,
          r"Let \(f(t) = t^3 - 6t^2 + 9t\). The stationary points are \(t = 1\) and \(t = 3\). What is the larger one?",
          3, "1",
          r"The derivative is \(3t^2 - 12t + 9 = 3(t - 1)(t - 3)\), so the stationary points are exactly 1 and 3. The larger is 3. The second derivative \(6t - 12\) is positive there, so \(t = 3\) is a local minimizer, and \(t = 1\) is a local maximizer. Neither fact is needed to name the larger root. Reporting 1 gives the smaller stationary point. Reporting 9 gives the constant term of \(f\), not a root of the derivative. Reporting 6 gives a coefficient.",
          WIGGLE, A_WIGGLE)
    b.mc(1,
         "A stationary point of a differentiable function is",
         ["any local minimizer, including a boundary point where the gradient does not vanish",
          "any point where the gradient is the zero vector",
          "a point where the function is discontinuous",
          "a global minimizer, by definition"],
         1,
         r"Stationary means the gradient vanishes. A boundary minimizer can fail that test, because the feasible set blocks the descent direction, so not every minimizer is stationary. Continuity of the function is a different hypothesis. A stationary point may be a maximizer or a saddle, so it is not a global minimizer by definition.",
         GRAD, A_GRAD)
    b.sym(2,
          r"Write the partial derivative with respect to \(x\) of \(\tfrac12 a x^2 + b x y\) as an expression in a, b, x, and y.",
          "a*x+b*y",
          {"a": (-3, 3), "b": (-3, 3), "x": (-3, 3), "y": (-3, 3)},
          r"Differentiating \(\tfrac12 a x^2\) in \(x\) produces \(a x\). Differentiating \(b x y\) in \(x\), with \(y\) held fixed, produces \(b y\). The sum is \(a x + b y\)."
          "\n"
          r"• \(a x + b\) drops the factor \(y\) on the cross term."
          "\n"
          r"• \(\tfrac12 a x + b y\) differentiates the square incompletely."
          "\n"
          r"• \(2 a x + b y\) treats the leading factor as if the one half were absent.",
          ["b*y+a*x", "a*x+y*b"],
          fig=GRAD, alt=A_GRAD)
    b.order(2,
            "Put these steps in the order used to hunt interior minimizers with Fermat's rule.",
            ["Confirm that the candidate region is the interior of the feasible set.",
             "Set every partial derivative equal to zero.",
             "Solve that system and list the stationary points.",
             "Test each stationary point by other means before calling it a minimizer."],
            r"Fermat's rule applies to interior points, so the interior check comes first. The equations are the vanishing of the partial derivatives. Solving them produces candidates, not yet minimizers: a stationary point may maximize or saddle. A second-order test, a convexity argument, or a direct comparison is the last step. Solving the derivative equations on a boundary point where the rule does not apply can miss the minimizer or condemn a genuine one.",
            GRAD, A_GRAD)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 2y^2 - 4x + 6y\). What is the value of \(f\) at its stationary point?",
          -8.5, "1",
          r"The partial derivatives are \(2x - 4\) and \(4y + 6\). They vanish at \(x = 2\) and \(y = -3/2\). Substituting gives \(4 + 2\cdot(9/4) - 8 + 6\cdot(-3/2) = 4 + 4.5 - 8 - 9 = -8.5\). Reporting 2 gives the first coordinate. Reporting \(-1.5\) gives the second coordinate. Reporting 0 is the gradient's length, not the function value.",
          BOWL, A_BOWL)
    b.multi(3,
            r"Let \(f(t) = t^3 - 3t\). Which statements hold?",
            [r"\(t = 1\) is stationary.",
             r"\(t = -1\) is stationary.",
             r"\(t = 0\) is stationary.",
             r"\(t = 1\) is a local minimizer.",
             r"\(t = 1\) is a global minimizer."],
            [0, 1, 3],
            r"The derivative is \(3t^2 - 3 = 3(t - 1)(t + 1)\), so the stationary points are \(t = \pm 1\). The second derivative \(6t\) is positive at \(t = 1\), so that point is a strict local minimizer, and the value is \(-2\)."
            "\n"
            r"• At \(t = 0\) the derivative equals \(-3\), so the origin is not stationary."
            "\n"
            r"• As \(t\) goes to \(-\infty\), \(f(t)\) goes to \(-\infty\), so the local minimizer is not global.",
            WIGGLE, A_WIGGLE)
    b.find_error(3,
                 r"A note claims that the minimum of \(f(t) = t\) on the interval \([0, 1]\) occurs where the derivative is zero. Exactly one step is false.",
                 [r"\(f\) is differentiable on the open interval \((0, 1)\).",
                  "Fermat's rule says an interior local minimizer has derivative zero.",
                  r"The endpoint \(t = 0\) is an interior point of \([0, 1]\).",
                  "A local minimizer that is not interior need not have derivative zero."],
                 2,
                 r"The function is differentiable on the open interval, Fermat's rule really does require a zero derivative at an interior local minimizer, and a boundary minimizer is exempt from that test. The false step calls the endpoint interior. The minimum on \([0, 1]\) is at \(t = 0\), where the derivative equals 1.",
                 [r"The endpoint \(t = 0\) is on the boundary, not in the open interval.",
                  "Fermat's rule does not mention the derivative.",
                  r"\(f(t) = t\) is not differentiable on \((0, 1)\)."],
                 0,
                 SEG, A_SEG)
    b.mc(3,
         "If the gradient at an interior point is not zero,",
         ["that point is a strict local minimizer",
          "the function is constant",
          "the point is infeasible",
          "that point is not a local minimizer"],
         3,
         r"A nonzero gradient supplies a descent direction, and a short step in that direction stays feasible when the point is interior. The function decreases, so the point is not a local minimizer. A nonzero gradient is the opposite of the derivative of a constant. Interior already means feasible. The point might still be a saddle or a maximizer, but the descent direction alone rules out a local minimum.",
         PAIR, A_PAIR)
    b.sym(4,
          r"For \(p > 0\), write the stationary point of \(\tfrac12 p t^2 + q t\) as an expression in p and q.",
          "-q/p",
          {"p": (0.5, 4), "q": (-4, 4)},
          r"The derivative is \(p t + q\). Setting it to zero gives \(t = -q/p\). The second derivative is the positive number \(p\), so this stationary point is a strict local minimizer. The same algebra is the unique solution of a positive definite one-dimensional quadratic."
          "\n"
          r"• \(q/p\) misses the sign."
          "\n"
          r"• \(-q\) drops the curvature \(p\)."
          "\n"
          r"• \(-p/q\) inverts the ratio.",
          ["-(q/p)", "-1*q/p"],
          fig=BOWL, alt=A_BOWL, preview=["second-order-optimality"])
    b.num(4,
          r"Let \(f(x, y) = (x - 1)^2 + 4(y + 2)^2 + 7\). What is the value at the stationary point?",
          7, "1",
          r"The squares vanish at \(x = 1\) and \(y = -2\), and the gradient is zero there because each square contributes a factor of the same displacement. The value is 7. The Hessian is diagonal with entries 2 and 8, so the stationary point is a strict local minimizer. Reporting 1 or \(-2\) gives a coordinate. Reporting 4 gives the coefficient on the second square.",
          ELL, A_ELL, preview=["convex-optimality-global"])
    b.mc(4,
         "On a smooth equality constraint, the first-order balance at a minimizer is",
         ["a requirement that the objective gradient is zero anyway",
          "a ban on differentiable objectives",
          "a balance between the objective gradient and the constraint gradients",
          "a statement only about discrete variables"],
         2,
         r"An equality constraint removes the interior of the ambient space, so Fermat's rule in the ambient variables need not hold. The replacement is that the objective gradient lies in the span of the constraint gradients: no feasible direction is a descent direction. Forcing the objective gradient itself to vanish is the unconstrained test. Differentiability is what makes the gradient balance available. A discrete variable has no tangent direction to balance.",
         HALF, A_HALF, preview=["lagrange-multiplier-equality"])
    b.save()


def bank_second():
    b = Bank("second-order-optimality")
    b.mc(1,
         "At an interior local minimizer of a twice continuously differentiable function,",
         ["the Hessian is positive semidefinite",
          "the Hessian is positive definite",
          "the Hessian is indefinite",
          "the gradient is a nonzero eigenvector of the Hessian"],
         0,
         r"The second-order necessary condition is positive semidefiniteness of the Hessian. Positive definiteness is sufficient for a strict local minimizer when the gradient also vanishes, and it is not necessary: \(t^4\) has a local minimizer at the origin where the second derivative is zero. An indefinite Hessian produces a saddle, which is not a local minimizer. The gradient at an interior local minimizer is zero, so it is not a nonzero eigenvector.",
         HESS, A_HESS)
    b.num(1,
          r"Let \(f(x, y) = x^2 - y^2\). At the origin, what is the smaller eigenvalue of the Hessian?",
          -2, "1",
          r"The Hessian is \(\operatorname{diag}(2, -2)\). Its eigenvalues are 2 and \(-2\), so the smaller is \(-2\). The origin is stationary, and an indefinite Hessian means it is a saddle, not a local minimizer. Reporting 2 gives the positive eigenvalue. Reporting 0 would be the function value, not an eigenvalue. Reporting \(-1\) is neither eigenvalue.",
          HESS, A_HESS)
    b.mc(1,
         "If the gradient is zero and the Hessian is positive definite at that point,",
         ["the point is a saddle",
          "the point is a strict local minimizer",
          "the point is a local maximizer",
          "the second-order test says nothing"],
         1,
         r"Positive definiteness of the Hessian makes the second-order Taylor model a strict bowl. Together with a zero gradient, that is the standard sufficient condition for a strict local minimizer. A saddle needs eigenvalues of both signs. A local maximizer needs a negative definite Hessian. The test is conclusive in the positive definite case. It goes silent only when a zero eigenvalue appears.",
         BOWL, A_BOWL)
    b.order(2,
            "Put these steps in the order used for the second-order test at interior stationary points.",
            ["Solve the first-order system and list the stationary points.",
             "Compute the Hessian at each stationary point.",
             "Read the eigenvalues of that Hessian.",
             "Call the point a strict local minimizer if every eigenvalue is positive, a saddle if both signs appear, and give no verdict if a zero eigenvalue appears."],
            r"The second-order test is applied at stationary points, so the gradient equations come first. The Hessian is then evaluated at those points, not at a random base point. The eigenvalues sort the quadratic form into positive definite, negative definite, indefinite, or singular. The verdict is the last step, and a zero eigenvalue is a silence of the test rather than a saddle. Reading eigenvalues before imposing stationarity classifies the curvature of a point that may still have a downhill direction.",
            HESS, A_HESS)
    b.multi(2,
            "At a stationary point of a twice continuously differentiable function, which conclusions are valid?",
            ["A positive definite Hessian implies a strict local minimizer.",
             "A negative semidefinite Hessian is necessary at an interior local maximizer.",
             "A positive semidefinite Hessian implies a local minimizer.",
             "An indefinite Hessian implies a saddle.",
             "A zero eigenvalue means the point is not stationary."],
            [0, 1, 3],
            r"Positive definiteness is the sufficient condition for a strict local minimizer once the gradient vanishes. At an interior local maximizer the Hessian is negative semidefinite, by the same necessary condition applied to \(-f\). An indefinite Hessian increases in one direction and decreases in another, which is a saddle."
            "\n"
            r"• Positive semidefiniteness is necessary at a local minimizer and not sufficient. The second derivative of \(t^3\) vanishes at the origin and the origin is not a local minimizer."
            "\n"
            r"• A zero eigenvalue is a statement about the Hessian. Stationarity is a statement about the gradient.",
            HESS, A_HESS)
    b.num(2,
          r"Let \(f(x, y) = 3x^2 + 2xy + 3y^2\). What is the smaller eigenvalue of the Hessian?",
          4, "1",
          r"The Hessian is \(\begin{bmatrix} 6 & 2 \\ 2 & 6 \end{bmatrix}\). Its trace is 12 and its determinant is \(36 - 4 = 32\), so the eigenvalues satisfy \(\lambda^2 - 12\lambda + 32 = 0\), or \((\lambda - 4)(\lambda - 8) = 0\). The smaller is 4. Both are positive, the only stationary point is the origin, and that point is a strict local minimizer. Reporting 8 gives the larger eigenvalue. Reporting 6 gives a diagonal entry. Reporting 2 gives an off-diagonal entry.",
          ELL, A_ELL)
    b.sym(3,
          r"Write the second derivative of \(\tfrac12 a t^2 + \tfrac16 b t^3\) as an expression in a, b, and t.",
          "a+b*t",
          {"a": (-3, 3), "b": (-3, 3), "t": (-3, 3)},
          r"The first derivative is \(a t + \tfrac12 b t^2\). Differentiating again produces \(a + b t\)."
          "\n"
          r"• \(a + \tfrac12 b t\) stops one derivative too early on the cubic term."
          "\n"
          r"• \(b t\) drops the constant second derivative of the quadratic term."
          "\n"
          r"• \(a + b\) evaluates the second derivative at \(t = 1\) and then treats that number as the function.",
          ["b*t+a", "a+t*b"],
          fig=WIGGLE, alt=A_WIGGLE)
    b.find_error(3,
                 r"A note claims that \(f(t) = t^4\) has a saddle at the origin because the second derivative vanishes. Exactly one step is false.",
                 [r"The first derivative of \(t^4\) is \(4t^3\), which is 0 at the origin.",
                  r"The second derivative is \(12t^2\), which is 0 at the origin.",
                  "A vanishing second derivative means the stationary point is a saddle.",
                  "The second-order sufficient test needs a positive second derivative, so a zero second derivative leaves that test silent."],
                 2,
                 r"Both derivative evaluations are right, and a zero second derivative really does leave the sufficient test silent. The false step turns that silence into a saddle. The function \(t^4\) is nonnegative and equals zero only at the origin, so the origin is a strict global minimizer. The second-order test does not see it.",
                 ["A zero second derivative does not decide between a minimizer, a maximizer, and a saddle.",
                  r"The second derivative of \(t^4\) is not \(12t^2\).",
                  r"The first derivative of \(t^4\) does not vanish at the origin."],
                 0,
                 BOWL, A_BOWL)
    b.mc(3,
         r"For \(f(x, y) = x^2\), the Hessian at the origin is positive semidefinite and singular. The right reading is that",
         [r"the origin is a saddle because of the zero eigenvalue",
          r"the origin is a strict local minimizer in the \(y\) direction by the Hessian test",
          r"the second-order sufficient test does not apply, and \(f \ge 0\) still shows that the origin is a minimizer",
          r"the gradient at the origin is \((1, 0)\)"],
         2,
         r"The Hessian is \(\operatorname{diag}(2, 0)\). A zero eigenvalue blocks the sufficient test, and it does not by itself create a saddle. Along the \(y\) axis the function is flat, so the minimizer is not strict, and the Hessian test does not claim a strict decrease in that direction. The gradient is zero, not \((1, 0)\). Nonnegativity of \(x^2\) is the separate reason the origin is a global minimizer.",
         ELL, A_ELL)
    b.num(4,
          r"Let \(f(x, y) = x^3 - 3x + y^2\). The point \((1, 0)\) is a strict local minimizer. What is \(f(1, 0)\)?",
          -2, "1",
          r"Substituting gives \(1 - 3 + 0 = -2\). The gradient is \((3x^2 - 3,\ 2y)\), so the stationary points are \((1, 0)\) and \((-1, 0)\). The Hessian is \(\operatorname{diag}(6x, 2)\). At \(x = 1\) both eigenvalues are positive. At \(x = -1\) they have opposite signs, so that point is a saddle. Reporting 2 gives \(f(-1, 0) = -1 + 3\). Reporting 1 gives a coordinate. Reporting \(-3\) drops the cubic term.",
          WIGGLE, A_WIGGLE, preview=["stationary-point-classification"])
    b.mc(4,
         r"For \(f(x) = \tfrac12 x^T A x + b^T x\) with \(A\) symmetric and positive definite,",
         ["there is a stationary point and it is a maximizer",
          "the Hessian test is inconclusive",
          "no stationary point exists",
          "there is one stationary point and it is a strict global minimizer"],
         3,
         r"The gradient \(A x + b\) vanishes at the unique solution of \(A x = -b\), because a positive definite matrix is invertible. The Hessian is \(A\) everywhere, so the sufficient condition applies and the stationary point is a strict local minimizer. Positive definiteness also makes \(f\) strictly convex and coercive, so the local minimizer is the unique global one. The Hessian test is conclusive, and the critical point is not a maximizer.",
         ELL, A_ELL, preview=["quadratic-function-minimization"])
    b.mc(4,
         r"The least-squares objective \(\lVert Ax - d \rVert^2\) has Hessian \(2A^T A\). At a stationary point of this objective,",
         [r"the Hessian test can certify a strict local minimizer when \(A\) has full column rank",
          r"the Hessian is indefinite for every \(A\)",
          "the objective is unbounded below",
          "a zero residual is required before the point can be a minimizer"],
         0,
         r"The matrix \(A^T A\) is always positive semidefinite, and it is positive definite exactly when \(A\) has full column rank. In that case the sufficient condition says the unique stationary point is a strict local minimizer, and the squared residual is a convex quadratic, so the minimizer is global. A zero residual is the perfect-fit case, not a requirement for optimality. The objective is a square, so it is bounded below by zero.",
         HESS, A_HESS, preview=["linear-least-squares"])
    b.save()


def bank_stationary():
    b = Bank("stationary-point-classification")
    b.mc(1,
         "Classifying the stationary points of a smooth function starts by",
         ["solving the equation that sets the gradient equal to zero",
          "checking compactness before any derivative",
          "integrating the function",
          "replacing the function by its absolute value"],
         0,
         r"A stationary point is defined by a zero gradient, so the list of candidates is the solution set of that equation. Compactness is an existence tool and does not locate the point. Integration recovers a function from a derivative and is not the classification. The absolute value creates new corners and a different function.",
         GRAD, A_GRAD)
    b.num(1,
          r"Let \(f(x, y) = x^2 + y^2 - 2x - 4y\). What is the value at the stationary point?",
          -5, "1",
          r"The gradient is \((2x - 2,\ 2y - 4)\), so the only stationary point is \((1, 2)\). The value is \(1 + 4 - 2 - 8 = -5\). Completing the square gives \((x - 1)^2 + (y - 2)^2 - 5\), which shows the same point is the unique global minimizer. Reporting 1 or 2 gives a coordinate. Reporting 5 drops the sign. Reporting \(-4\) is the linear coefficient on \(y\).",
          BOWL, A_BOWL)
    b.mc(1,
         "An indefinite Hessian at a stationary point means the point is",
         ["a strict local minimizer",
          "a saddle",
          "a strict local maximizer",
          "not stationary"],
         1,
         r"Indefinite means one positive eigenvalue and one negative eigenvalue. The function rises along the first eigenvector and falls along the second, which is a saddle. A local minimizer would need every eigenvalue nonnegative, and a local maximizer would need every eigenvalue nonpositive. The gradient was already set to zero before the Hessian was read, so the point is stationary.",
         PAIR, A_PAIR)
    b.order(2,
            "Put these steps in the order used to classify stationary points and then test a global claim.",
            ["Compute the gradient and set it equal to zero.",
             "Solve for every real stationary point.",
             "Classify each one from the eigenvalues of its Hessian.",
             "Use the values, or coercivity, before calling one of them a global minimizer."],
            r"The candidates are the solutions of the gradient equation, and the list has to be complete before a comparison of values means anything. The Hessian eigenvalues then separate local minima, local maxima, and saddles, with a zero eigenvalue left undecided. A local minimizer becomes global only after a separate argument: the function is coercive, a sublevel set is compact, or every other stationary value is worse and no direction runs off to \(-\infty\). Comparing values before the list is complete can miss a lower stationary point.",
            HESS, A_HESS)
    b.multi(2,
            r"Let \(f(x, y) = x^3 + y^3 - 3x - 3y\). Which statements hold?",
            [r"\((1, 1)\) is a local minimizer.",
             r"\((1, -1)\) is a local minimizer.",
             r"\((-1, -1)\) is a local minimizer.",
             r"\((1, 1)\) is a strict local minimizer."],
            [0, 3],
            r"The gradient vanishes when \(x^2 = 1\) and \(y^2 = 1\), so the four points have coordinates \(\pm 1\). The Hessian is \(\operatorname{diag}(6x, 6y)\)."
            "\n"
            r"• At \((1, 1)\) both eigenvalues are positive, so the point is a strict local minimizer. The value is \(-4\)."
            "\n"
            r"• At \((1, -1)\) and at \((-1, 1)\) the eigenvalues have opposite signs, so both points are saddles."
            "\n"
            r"• At \((-1, -1)\) both eigenvalues are negative, so the point is a strict local maximizer, not a minimizer.",
            LEVELS, A_LEVELS)
    b.num(2,
          r"Let \(f(t) = t^4 - 8t^2\). What is the global minimum value?",
          -16, "1",
          r"The derivative is \(4t^3 - 16t = 4t(t - 2)(t + 2)\), so the stationary points are \(t = 0\) and \(t = \pm 2\). The values are \(0\) and \(16 - 32 = -16\). The second derivative \(12t^2 - 16\) is negative at the origin and positive at \(\pm 2\), so the origin is a local maximizer and the other two points are local minimizers. The fourth power dominates at infinity, so \(-16\) is the global minimum, attained twice. Reporting \(-8\) uses the coefficient. Reporting 0 is the local maximum value. Reporting 2 is a location.",
          WIGGLE, A_WIGGLE)
    b.sym(3,
          r"For \(a \ne 0\), the stationary point of \(\tfrac12 a x^2 + b x + \tfrac12 c y^2 + d y\) has first coordinate \(-b/a\) when \(c \ne 0\) as well. Write that first coordinate as an expression in a and b.",
          "-b/a",
          {"a": (0.5, 4), "b": (-4, 4)},
          r"The partial derivative in \(x\) is \(a x + b\), and it vanishes at \(x = -b/a\). The partial derivative in \(y\) does not enter that coordinate."
          "\n"
          r"• \(b/a\) misses the sign."
          "\n"
          r"• \(-a/b\) inverts the ratio."
          "\n"
          r"• \(-b\) drops the curvature \(a\).",
          ["-(b/a)", "-1*b/a"],
          fig=GRAD, alt=A_GRAD)
    b.find_error(3,
                 r"A note claims that the origin is a local minimizer of \(f(x, y) = x^2 - y^2\). Exactly one step is false.",
                 ["Both partial derivatives vanish at the origin.",
                  "The Hessian at the origin is diagonal with entries 2 and -2.",
                  "A diagonal Hessian with both a positive entry and a negative entry is positive semidefinite.",
                  "Positive semidefiniteness of the Hessian is necessary at an interior local minimizer."],
                 2,
                 r"The gradient really does vanish, the Hessian really is \(\operatorname{diag}(2, -2)\), and a local minimizer really does need a positive semidefinite Hessian. The false step is the semidefinite claim. A negative diagonal entry is a negative eigenvalue, so the Hessian is indefinite and the origin is a saddle.",
                 ["A negative diagonal entry means the Hessian is not positive semidefinite.",
                  "The partial derivatives do not vanish at the origin.",
                  "An interior local minimizer can have an indefinite Hessian."],
                 0,
                 PAIR, A_PAIR)
    b.mc(3,
         r"For \(f(x, y) = x^2 + y^4\), the origin is stationary and the Hessian there is singular. The right reading is that",
         ["the origin is a saddle because of the zero eigenvalue",
          "the origin is a local maximizer",
          "there is no stationary point",
          r"the Hessian test is silent, and nonnegativity of \(f\) shows that the origin is a global minimizer"],
         3,
         r"The gradient is \((2x,\ 4y^3)\), which vanishes only at the origin. The Hessian there is \(\operatorname{diag}(2, 0)\), so the sufficient test does not fire and the zero eigenvalue is not a saddle by itself. The function is a sum of even powers, hence nonnegative, and it equals zero only at the origin. That is a strict global minimizer found without the sufficient test. It is not a maximizer.",
         BOWL, A_BOWL)
    b.num(4,
          r"Let \(f(x, y) = x^2 + y^2 - 6x + 8y\). What is the value at the stationary point?",
          -25, "1",
          r"The gradient is \((2x - 6,\ 2y + 8)\), so the stationary point is \((3, -4)\). The value is \(9 + 16 - 18 - 32 = -25\). Completing the square gives \((x - 3)^2 + (y + 4)^2 - 25\), and the Hessian is twice the identity, so the point is the unique strict global minimizer. Reporting 3 or \(-4\) gives a coordinate. Reporting 25 drops the sign. Reporting \(-6\) is a linear coefficient.",
          ELL, A_ELL, preview=["newton-method-optimization"])
    b.mc(4,
         "A minimizer on a smooth equality constraint",
         ["must be a stationary point of the objective alone",
          "can have a nonzero objective gradient",
          "must have an indefinite Hessian of the objective",
          "cannot be strict"],
         1,
         r"The constraint removes the ambient interior, so the objective gradient need not vanish. It has to be normal to the constraint surface. A nonzero objective gradient is therefore compatible with optimality. The Hessian of the objective alone is not required to be indefinite. Strictness is still possible along the surface.",
         HALF, A_HALF, preview=["lagrange-multiplier-equality"])
    b.multi(4,
            r"Let \(f(x, y) = x^2 - y^2 + 2x\). Which statements hold?",
            [r"\((-1, 0)\) is a local minimizer.",
             r"\((-1, 0)\) is a saddle.",
             "The function has no local minimizer.",
             r"\((-1, 0)\) is a local maximizer."],
            [1, 2],
            r"The gradient is \((2x + 2,\ -2y)\), so the only stationary point is \((-1, 0)\). The Hessian is \(\operatorname{diag}(2, -2)\), which is indefinite, so the point is a saddle and neither a local minimizer nor a local maximizer."
            "\n"
            r"On the open plane every local minimizer of a differentiable function is stationary. The only candidate is a saddle, and \(f\) goes to \(-\infty\) as \(\lvert y \rvert\) grows, so no local minimizer exists.",
            PAIR, A_PAIR, preview=["descent-directions"])
    b.save()


def bank_convex_opt():
    b = Bank("convex-optimality-global")
    b.mc(1,
         r"If \(f\) is differentiable and convex, and the gradient at \(x^\star\) is zero, then",
         [r"\(x^\star\) is a global minimizer",
          r"\(x^\star\) is a saddle",
          r"\(x^\star\) is a local minimizer that may fail to be global",
          r"\(f\) is constant"],
         0,
         r"Convexity puts the graph above every tangent. A zero gradient makes the tangent the constant \(f(x^\star)\), so every other point is at least that high. The stationary point is a global minimizer. It need not be a saddle, and the local-versus-global gap that nonconvex functions have is closed by convexity. A constant function is the special case in which every point is stationary, not a requirement.",
         BOWL, A_BOWL)
    b.num(1,
          r"Let \(f(t) = t^2 - 6t + 10\). What is the global minimum value?",
          1, "1",
          r"The derivative \(2t - 6\) vanishes at \(t = 3\). The value is \(9 - 18 + 10 = 1\). The second derivative is 2, so \(f\) is strictly convex and the stationary point is the unique global minimizer. Completing the square gives \((t - 3)^2 + 1\). Reporting 3 gives the minimizer. Reporting 10 gives the constant term. Reporting 6 gives the linear coefficient.",
          BOWL, A_BOWL)
    b.mc(1,
         "Strict convexity, together with one stationary point, gives",
         ["a whole line of minimizers",
          "a unique global minimizer",
          "a local minimizer that is not global",
          "no minimizer"],
         1,
         r"A stationary point of a differentiable convex function is global. Strict convexity forbids a second point from tying the value, because a tie would put the chord on the graph. The argmin set has one point. A line of minimizers is the non-strict picture, as with a function that is flat in one direction. The stationary point cannot fail to be global, and it is a minimizer, so the set is not empty.",
         BOWL, A_BOWL)
    b.order(2,
            "Put these steps in the order used to certify a global minimizer of a differentiable convex function.",
            ["Check that the objective is convex on a convex domain.",
             "Find a point where the gradient is zero.",
             "Invoke the tangent inequality, which now says every point lies on or above that value.",
             "If the function is strictly convex, conclude that no other point shares the value."],
            r"Convexity is the hypothesis that turns a tangent into a global underestimator, so it is checked first. A zero gradient is the point where that underestimator becomes a constant. The inequality then says the constant is a lower bound, which is global optimality. Uniqueness is a further conclusion and needs the strict inequality on chords. Skipping the convexity check leaves an ordinary stationary point, which may be a saddle.",
            SEG, A_SEG)
    b.multi(2,
            r"Which statements hold for a differentiable convex function on \(\mathbb{R}^n\)?",
            ["Every stationary point is a global minimizer.",
             "Every local minimizer is global.",
             "A stationary point is always unique.",
             "If the function is strictly convex, there is at most one global minimizer.",
             "A positive definite Hessian at one point makes the function convex."],
            [0, 1, 3],
            r"The tangent inequality turns a zero gradient into a global lower bound, so every stationary point is global. A local minimizer of a convex function is global even before differentiability is used. Strict convexity makes a tie impossible, so there is at most one global minimizer."
            "\n"
            r"• A convex function can be constant, or it can be constant along a line, so a stationary point need not be unique."
            "\n"
            r"• One positive definite Hessian controls a neighborhood. Convexity needs the Hessian test, or the tangent test, on the whole domain.",
            ELL, A_ELL)
    b.num(2,
          r"Let \(f(x, y) = x^2 + 3y^2 - 4x + 6y\). What is the value at the stationary point?",
          -7, "1",
          r"The gradient is \((2x - 4,\ 6y + 6)\), so the stationary point is \((2, -1)\). The value is \(4 + 3 - 8 - 6 = -7\). The Hessian is \(\operatorname{diag}(2, 6)\), which is positive definite, so \(f\) is strictly convex and this stationary point is the unique global minimizer. Reporting 2 or \(-1\) gives a coordinate. Reporting 7 drops the sign. Reporting 3 is the coefficient of \(y^2\).",
          ELL, A_ELL)
    b.sym(3,
          r"For \(a > 0\), write the unique global minimizer of \(\tfrac12 a t^2 + b t + c\) as an expression in a and b.",
          "-b/a",
          {"a": (0.5, 4), "b": (-4, 4)},
          r"The derivative is \(a t + b\), so the only stationary point is \(t = -b/a\). The second derivative \(a\) is positive, so the quadratic is strictly convex and the stationary point is the unique global minimizer. The constant \(c\) shifts the value and does not move the minimizer."
          "\n"
          r"• \(b/a\) misses the sign."
          "\n"
          r"• \(-b\) ignores the curvature."
          "\n"
          r"• \(c - b/a\) adds the constant into the location.",
          ["-(b/a)", "-1*b/a"],
          fig=BOWL, alt=A_BOWL)
    b.find_error(3,
                 r"A note claims that the stationary point of \(f(t) = t^3\) is a global minimizer. Exactly one step is false.",
                 [r"The derivative of \(t^3\) is \(3t^2\), which vanishes at the origin.",
                  r"\(t^3\) is convex on the whole real line.",
                  "A stationary point of a differentiable convex function is a global minimizer.",
                  "The argument needs both stationarity and convexity."],
                 1,
                 r"The derivative really vanishes at the origin, a stationary point of a differentiable convex function really is global, and both hypotheses are required. The false step is the convexity claim. The second derivative \(6t\) is negative for negative \(t\), so \(t^3\) is not convex, and the origin is not a local minimizer: the function takes both signs in every neighborhood.",
                 [r"The second derivative \(6t\) is negative for negative \(t\), so \(t^3\) is not convex on the line.",
                  r"The derivative of \(t^3\) does not vanish at the origin.",
                  "A stationary point of a differentiable convex function need not be a global minimizer."],
                 0,
                 WIGGLE, A_WIGGLE)
    b.mc(3,
         r"For \(f(x, y) = x^2\), the stationary points are the \(y\)-axis. The right reading is that",
         ["only the origin is a minimizer",
          "there is no minimizer",
          r"every point \((0, y)\) is a global minimizer, and \(f\) is convex but not strictly convex",
          r"\(f\) is strictly convex"],
         2,
         r"The gradient is \((2x, 0)\), so it vanishes on the whole line \(x = 0\). On that line the function equals 0, and elsewhere it is positive, so every such point is a global minimizer. The Hessian is \(\operatorname{diag}(2, 0)\), positive semidefinite and singular, which matches convexity without strict convexity. A whole line of minimizers is exactly what fails strictness. The origin is one minimizer among many.",
         ELL, A_ELL)
    b.mc(4,
         "A quadratic with a positive definite Hessian",
         ["has a stationary point that is a maximizer",
          "has a unique stationary point, and that point is the unique global minimizer",
          "may fail to be convex",
          "has no gradient"],
         1,
         r"A positive definite Hessian is constant for a quadratic, so the function is strictly convex. The gradient equation is a linear system with an invertible matrix, so there is one stationary point. Strict convexity promotes it to the unique global minimizer. It is not a maximizer. A quadratic is a polynomial, so the gradient exists everywhere.",
         ELL, A_ELL, preview=["quadratic-function-minimization"])
    b.num(4,
          r"Minimize \((x - 2)^2 + (y - 2)^2\) over the half-space \(x \le 0\). What is the minimum value?",
          4, "1",
          r"The unconstrained minimizer is \((2, 2)\), which is not feasible. The objective is the squared distance to that point, and the closest feasible point is \((0, 2)\), where the value is 4. The feasible set is convex and the objective is strictly convex, so this closest point is the unique global minimizer even though the gradient there is \((-4, 0)\), not zero. Reporting 8 adds the two squared shifts as if both coordinates were blocked. Reporting 2 gives a coordinate. Reporting 0 is the unconstrained value and is not feasible.",
          HALF, A_HALF, preview=["optimality-over-convex-set"])
    b.mc(4,
         "The solution of the normal equations for a linear least-squares objective is a global minimizer because",
         ["a zero residual is required for optimality",
          "least squares is nonconvex",
          "that objective is a convex quadratic, so a stationary point is global",
          "the normal equations describe a saddle"],
         2,
         r"The squared residual \(\lVert Ax - d \rVert^2\) has Hessian \(2A^T A\), which is positive semidefinite, so the objective is convex. The normal equations are the stationarity condition. Convexity promotes any solution of them to a global minimizer. A zero residual is the perfect-fit case. The Hessian is never indefinite, so the stationary point is not a saddle.",
         HESS, A_HESS, preview=["linear-least-squares"])
    b.save()


def bank_quadratic():
    b = Bank("quadratic-function-minimization")
    b.mc(1,
         r"For \(f(x) = \tfrac12 x^T A x + b^T x + c\) with \(A\) symmetric, the gradient is",
         [r"\(A x + b\)",
          r"\(A x\)",
          r"\(\tfrac12 A x + b\)",
          r"\(x^T A + c\)"],
         0,
         r"The quadratic term contributes \(A x\) when \(A\) is symmetric, and the linear term contributes \(b\). The constant disappears. Keeping the one half in the gradient double-counts the bookkeeping that the one half was invented to cancel. Dropping \(b\) ignores the linear term. A row \(x^T A\) is the transpose of \(A x\) only in the scalar sense of a dot product, and it is not the column gradient, and \(c\) does not belong in it.",
         HESS, A_HESS)
    b.num(1,
          r"Let \(A = \operatorname{diag}(2, 4)\), \(b = (-2, -8)\), and \(c = 5\), and let \(f(x) = \tfrac12 x^T A x + b^T x + c\). What is the minimum value?",
          -4, "1",
          r"The stationarity equation \(A x = -b\) is \((2x, 4y) = (2, 8)\), so the minimizer is \((1, 2)\). Because \(A\) is positive definite this critical point is the unique global minimizer. The value is \(1^2 + 2\cdot 2^2 - 2\cdot 1 - 8\cdot 2 + 5 = 1 + 8 - 2 - 16 + 5 = -4\). The same number is \(c - \tfrac12 b^T A^{-1} b = 5 - 9\). Reporting 5 gives the constant term. Reporting 1 or 2 gives a coordinate. Reporting 4 drops the sign.",
          ELL, A_ELL)
    b.mc(1,
         r"If the symmetric matrix \(A\) is positive definite, the quadratic has",
         [r"a minimizer only when \(b = 0\)",
          r"exactly one minimizer, the solution of \(A x = -b\)",
          "no lower bound",
          "every point as a minimizer"],
         1,
         r"Positive definiteness makes \(A\) invertible and the function strictly convex and coercive. The gradient equation \(A x + b = 0\) has one solution, and that solution is the unique global minimizer for every \(b\), including a nonzero \(b\). The function tends to infinity at infinity, so it is bounded below. A whole space of minimizers would require a singular Hessian.",
         ELL, A_ELL)
    b.sym(2,
          r"For \(a > 0\), write the global minimum value of \(\tfrac12 a t^2 + b t + c\) as an expression in a, b, and c.",
          "c-b^2/(2*a)",
          {"a": (0.5, 4), "b": (-4, 4), "c": (-4, 4)},
          r"The minimizer is \(t = -b/a\). Substituting and simplifying gives \(c - b^2/(2a)\). The same identity is \(c + \tfrac12 b t^\star\), because \(\tfrac12 a (t^\star)^2 + b t^\star = \tfrac12 b t^\star\) once \(a t^\star = -b\)."
          "\n"
          r"• \(c - b^2/a\) forgets the one half."
          "\n"
          r"• \(c + b^2/(2a)\) has the wrong sign: the linear term lowers a positive definite bowl."
          "\n"
          r"• \(-b/a\) is the minimizer, not the minimum value.",
          ["c-(b*b)/(2*a)", "c-b**2/(2*a)"],
          fig=BOWL, alt=A_BOWL)
    b.order(2,
            "Put these steps in the order used to minimize a quadratic written with a possibly unsymmetric matrix.",
            ["Replace the quadratic matrix by its symmetric part.",
             r"Set the gradient, \(A x + b\), equal to zero.",
             r"If \(A\) is positive definite, solve the linear system \(A x = -b\).",
             r"If \(A\) is only semidefinite, check that \(-b\) lies in the column space before claiming a minimizer."],
            r"The symmetric part is the Hessian the derivative formula uses, and it does not change the function. Stationarity is the linear equation \(A x + b = 0\). Positive definiteness gives existence, uniqueness, and an algorithm: solve the system. Semidefiniteness leaves an existence question, and the system is solvable exactly when \(-b\) is in the column space. Solving before symmetrizing uses a matrix the gradient does not see.",
            HESS, A_HESS)
    b.num(2,
          r"Let \(f(x, y) = x^2 - 4x + 3\), which is the quadratic with Hessian \(\operatorname{diag}(2, 0)\) and linear term \((-4, 0)\). What is the minimum value?",
          -1, "1",
          r"The gradient in \(x\) is \(2x - 4\), and the gradient in \(y\) is 0. Stationarity holds for \(x = 2\) and every \(y\). The value is \(4 - 8 + 3 = -1\), and it does not depend on \(y\). The Hessian is positive semidefinite and \(-b = (4, 0)\) lies in its column space, so minimizers exist and they are not unique. Reporting 2 gives the constrained coordinate. Reporting 3 gives the constant term. Reporting \(-4\) gives the linear coefficient.",
          ELL, A_ELL)
    b.multi(3,
            r"Which of these quadratics, written with a symmetric Hessian \(A\), have a unique global minimizer?",
            [r"\(A = I\) and \(b = (1, -2)\).",
             r"\(A = 0\), \(b = 0\), and \(c = 4\).",
             r"\(A = \operatorname{diag}(2, 0)\) and \(b = (0, 1)\).",
             r"\(A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}\) and \(b = 0\).",
             r"\(A = \operatorname{diag}(1, -1)\) and \(b = 0\)."],
            [0, 3],
            r"The identity is positive definite, so \(A x = -b\) has one solution and it is the unique minimizer. The matrix with eigenvalues 3 and 1 is positive definite as well, and \(b = 0\) puts the minimizer at the origin."
            "\n"
            r"• A zero Hessian and a zero linear term is the constant 4. Every point is a minimizer."
            "\n"
            r"• With \(A = \operatorname{diag}(2, 0)\) and \(b = (0, 1)\), the partial derivative in the second coordinate is 1 and never vanishes, so there is no minimizer."
            "\n"
            r"• Eigenvalues 1 and \(-1\) make an indefinite quadratic, unbounded below, with a saddle at the origin.",
            HESS, A_HESS)
    b.find_error(3,
                 r"A note claims that \(f(x, y) = \tfrac12 x^2 + y\) has a minimizer because its Hessian is positive semidefinite. Exactly one step is false.",
                 ["The Hessian is diagonal with entries 1 and 0, so it is positive semidefinite.",
                  "Positive semidefiniteness makes the quadratic convex.",
                  "Every convex quadratic attains a minimizer, whether or not the linear term lies in the range of the Hessian.",
                  r"The partial derivative with respect to \(y\) equals 1 and never vanishes."],
                 2,
                 r"The Hessian is positive semidefinite, a positive semidefinite Hessian makes a quadratic convex, and the partial derivative in \(y\) really is 1. The false step is the existence claim. Convexity gives a lower bound by any tangent, and it does not guarantee that the bound is attained. Here the linear term \((0, 1)\) is outside the column space, the gradient never vanishes, and sending \(y\) to \(-\infty\) drives \(f\) to \(-\infty\).",
                 ["A convex quadratic attains a minimizer only when the linear term lies in the column space of the Hessian.",
                  "The Hessian of this function is not positive semidefinite.",
                  r"The partial derivative in \(y\) does vanish."],
                 0,
                 SLOPE, A_SLOPE)
    b.mc(3,
         r"A quadratic with symmetric Hessian \(A\) is coercive exactly when",
         [r"\(A\) is positive semidefinite",
          r"\(b\) is zero",
          r"\(A\) is positive definite",
          r"\(c\) is positive"],
         2,
         r"Positive definiteness gives a uniform lower bound \(x^T A x \ge \lambda_{\min} \lVert x \rVert^2\) with \(\lambda_{\min} > 0\), which beats any linear term at infinity. Positive semidefiniteness still allows a direction of zero curvature, and a linear term along that direction, or even a zero linear term, keeps the function from tending to infinity in that direction. The vectors \(b\) and the constant \(c\) never create coercivity on their own.",
         BOWL, A_BOWL)
    b.num(4,
          r"Minimize \((x - 1)^2 + (x - 3)^2\) over the real line. What is the minimum value?",
          2, "1",
          r"Expanding gives \(2x^2 - 8x + 10\). The derivative \(4x - 8\) vanishes at \(x = 2\), and the second derivative is positive. The value is \((2 - 1)^2 + (2 - 3)^2 = 2\). This is a one-parameter least-squares fit of the two numbers 1 and 3, and the normal equation \(2x = 4\) is the same stationarity condition. Reporting 4 gives the sum of squares at \(x = 0\). Reporting 8 gives the linear coefficient. Reporting 1 or 3 gives a data value.",
          BOWL, A_BOWL, preview=["linear-least-squares"])
    b.sym(4,
          r"Along a line, a quadratic restricts to \(\tfrac12 a t^2 + g t\) with \(a > 0\). Write the step \(t\) that minimizes it, as an expression in g and a.",
          "-g/a",
          {"a": (0.5, 4), "g": (-4, 4)},
          r"The derivative in the step is \(a t + g\). It vanishes at \(t = -g/a\). The second derivative \(a\) is positive, so the critical step is a minimum. In several variables the same ratio is \(-g_{\mathrm{dir}} / a_{\mathrm{dir}}\), with \(g_{\mathrm{dir}}\) the directional derivative and \(a_{\mathrm{dir}}\) the directional second derivative."
          "\n"
          r"• \(g/a\) steps uphill."
          "\n"
          r"• \(-g\) ignores the curvature along the line."
          "\n"
          r"• \(-a/g\) inverts the ratio.",
          ["-(g/a)", "-1*g/a"],
          fig=GRAD, alt=A_GRAD, preview=["exact-line-search-quadratic"])
    b.mc(4,
         r"The map \(w \mapsto \tfrac12 \lVert w \rVert^2\) is",
         ["unbounded below",
          "linear",
          "strictly convex, with a unique minimizer at the origin",
          "singular in its Hessian"],
         2,
         r"The Hessian is the identity, which is positive definite, so the function is strictly convex and coercive. The gradient is \(w\), which vanishes only at the origin, and that point is the unique global minimizer. The function is a squared norm, not a linear function, and it is bounded below by zero. The identity is invertible, so the Hessian is not singular.",
         ELL, A_ELL, preview=["svm-quadratic-program"])
    b.save()


def expl_formulation():
    sections = [
        {"heading": "The idea", "figure": HALF, "figure_alt": A_HALF,
         "body_md": r"""An optimization problem is a choice. The decision vector is the object you are allowed to pick. The objective is the number you use to rank those picks. The feasible set is the collection of picks the restrictions leave standing. None of the three is optional. An objective without a set does not say which comparisons are legal, and a set without an objective does not say which feasible point is better.

The optimal value is the best number the objective attains, or the infimum of the values it takes, when a best point is missing. A solution, also called a minimizer, is a feasible point that attains that number. The two are different kinds of object. One is a number. The other is a point, and there may be several, or none.

Replacing the objective by its negative turns a maximization into a minimization with the same solutions. The feasible set is the whole space when the problem is unconstrained, a proper subset when it is constrained, and a grid such as the integers when the decision is discrete."""},
        {"heading": "Key equations",
         "body_md": r"""The standard shape is
\[
\operatorname{minimize}\ f(x) \quad \text{subject to}\quad x \in \mathcal{X}.
\]
The optimal value is \(p^\star = \inf\{f(x) : x \in \mathcal{X}\}\). A minimizer is any \(x^\star \in \mathcal{X}\) with \(f(x^\star) = p^\star\), and the argmin set is the collection of all such points. Maximizing \(f\) over \(\mathcal{X}\) is minimizing \(-f\) over the same set. If \(\mathcal{X}\) is empty the problem is infeasible and no minimizer exists."""},
        {"heading": "Worked example",
         "body_md": r"""A baker chooses a whole number of loaves and a whole number of rolls. A loaf uses 9 units of flour and a roll uses 4, and 40 units are on hand. Profit is 7 per loaf and 3 per roll, and the goal is to maximize profit. The decision is a pair of nonnegative integers. The minimization form of the objective is the negative of \(7u + 3v\). The feasible set is the pairs with \(9u + 4v \le 40\).

The pair of 2 loaves and 4 rolls uses \(18 + 16 = 34\) units, which is legal. The baker's recorded profit is 26, from \(7\cdot 2 + 3\cdot 4\). That number is one feasible value of the profit. It is not yet the optimal value, because some other feasible pair might pay more. The optimal value, once it is known, is a single number. The solutions are the pairs that attain it."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The most common mix-up is to report a solution when the question asks for the optimal value, or the reverse. They live in different spaces. A second mix-up is to treat a maximization as a minimization without changing the sign, which searches the wrong end of the range. A finite optimal value does not guarantee that a minimizer exists: the exponential on the line has infimum 0 and never attains it."""},
        {"heading": "Where this leads",
         "body_md": r"""Once the three pieces are named, a planar feasible set can be drawn and the level lines of the objective laid over it. The algebraic shape then sorts the problem into a linear program, a quadratic program, or a convex program. Local and global minimizers are the next definitions."""},
    ]
    save_explainer("optimization-problem-formulation", "Formulating an optimization problem", sections)


def expl_graphical():
    sections = [
        {"heading": "The idea", "figure": LEVELS, "figure_alt": A_LEVELS,
         "body_md": r"""A problem in two variables can be solved by drawing. The feasible set is a region in the plane. A level line of the objective is the curve on which the objective holds one fixed value. For a linear objective those curves are parallel straight lines, perpendicular to the gradient, and the gradient points toward larger values.

You draw one level line, mark the direction of decrease, and slide the line that way. The last position in which the line still touches the feasible set is the supporting level. Every contact point is a minimizer, and the level itself is the optimal value. If the contact is a single vertex, the minimizer is unique. If the level lies along an edge, the whole edge is optimal and the points share one value.

The picture also shows the failures. If the decreasing slide never loses contact, the objective is unbounded below and no minimizer exists. If the feasible set is empty, there is nothing to touch."""},
        {"heading": "Key equations",
         "body_md": r"""A linear objective \(c_1 x + c_2 y\) has level lines \(c_1 x + c_2 y = \gamma\) and gradient \((c_1, c_2)\). On a nonempty polygon the minimum and the maximum are attained, and each is attained at a vertex. The optimal value of a minimization is the smallest vertex value when the contact is a vertex, and it is that same number at every point of an optimal edge. Sliding to increase \(\gamma\) solves the maximization."""},
        {"heading": "Worked example",
         "body_md": r"""A depot serves the triangle with vertices \((1, 5)\), \((7, 2)\), and \((3, 6)\), and the cost to minimize is \(x + 2y\). The three vertex costs are \(1 + 10 = 11\), \(7 + 4 = 11\), and \(3 + 12 = 15\). The lowest vertex cost is shared by the first two vertices.

The level \(x + 2y = 11\) passes through both of those vertices, so it contains the edge that joins them. Every point of that edge is a minimizer. The depot level is 11. The third vertex is worse. The gradient \((1, 2)\) points into the triangle from that edge, which is the increasing side, so the picture agrees with the vertex comparison."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Sliding the level in the gradient direction finds a maximizer. The minimizer sits at the other end of the slide. A second mistake is to report a coordinate of the contact point when the question asks for the level, or to average the vertices and call the centroid optimal. A linear objective is constant on its level and is not improved by moving to the middle of the set. On an unbounded set the slide may never stop. The open segment between 0 and 1, with objective equal to the coordinate, has infimum 0 and no contact point, so the picture of a closed polygon does not apply."""},
        {"heading": "Where this leads",
         "body_md": r"""The vertex conclusion is the geometric reason a linear program is searched at extreme points. The same picture classifies a linear program as having a unique solution, a whole edge of solutions, an empty feasible set, or an unbounded objective. Higher-dimensional linear programs keep the extreme-point fact and replace the drawing by algebra."""},
    ]
    save_explainer("graphical-2d-optimization", "Solving 2-D problems graphically", sections)


def expl_classes():
    sections = [
        {"heading": "The idea", "figure": HESS, "figure_alt": A_HESS,
         "body_md": r"""Not every optimization problem is the same kind of object. A linear program has an affine objective and affine constraints. A quadratic program keeps the affine constraints and allows a quadratic objective. A convex program is the wider class in which the objective is a convex function and the feasible set is a convex set. Anything else is a general nonlinear program.

The quadratic case needs one algebraic cleanup. A square matrix and its symmetric part define the same quadratic form, because the skew part contributes nothing to \(x^T Q x\). Eigenvalue tests are run on the symmetric part. If that matrix is positive semidefinite, the quadratic objective is convex. If it is indefinite, the quadratic program is not a convex program, even when every constraint is linear.

Convexity is what makes a local solution enough. On a convex problem every local minimizer is global, so an algorithm that stops at a local solution has solved the problem. A nonconvex quadratic can bend up in one direction and down in another, and a point that is best nearby need not be best on the whole feasible set."""},
        {"heading": "Key equations",
         "body_md": r"""The symmetric part of \(Q\) is \((Q + Q^T)/2\), and \(x^T Q x = x^T ((Q + Q^T)/2) x\). The form \(a x^2 + b xy + c y^2\) belongs to the symmetric matrix with diagonal entries \(a\) and \(c\) and off-diagonal entries \(b/2\). Its determinant is \(ac - b^2/4\). A quadratic objective with a positive semidefinite Hessian, and a convex feasible set, is a convex program. Affine inequalities define a convex set, so a quadratic program is convex exactly when its Hessian is positive semidefinite."""},
        {"heading": "Worked example",
         "body_md": r"""Take the form \(4x^2 + 14 xy + 9y^2\). The cross term is \(14xy\), so the symmetric matrix has off-diagonal entries \(7\) and diagonal entries \(4\) and \(9\). The symmetrized corner is 7. The determinant of that matrix is \(4\cdot 9 - 49 = -13\), which is negative, so the form is indefinite.

The same expression with the cross term removed, \(4x^2 + 9y^2\), has a diagonal Hessian of second derivatives with positive entries, and it is strictly convex. The cross term is the whole difference between a convex quadratic and an indefinite one. Symmetrizing did not create that difference. It only put the form into a matrix whose eigenvalues are allowed to decide."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A linear objective with a quadratic constraint is not a quadratic program. The quadratic piece has to sit in the objective, and the constraints have to stay affine. Reading eigenvalues of an unsymmetrized matrix answers a different question, because those eigenvalues need not even be real. A positive diagonal is not positive semidefiniteness: the matrix with diagonal entries \(2\) and \(2\) and off-diagonal entries \(3\) has a negative determinant. Calling a problem convex because the objective is a square misses the feasible set. The complement of a disk is not convex."""},
        {"heading": "Where this leads",
         "body_md": r"""Linear programs are rewritten in a standard form and then searched at basic feasible solutions. Convex quadratic programs include least-squares fits and the training problem of a linear classifier with a squared-norm objective. The second-order test for a local minimizer uses the same Hessian, and for a convex objective that local test becomes a global one."""},
    ]
    save_explainer("optimization-problem-classes", "LP, QP, convex and nonlinear programs", sections)


def expl_local():
    sections = [
        {"heading": "The idea", "figure": WIGGLE, "figure_alt": A_WIGGLE,
         "body_md": r"""A minimizer is a feasible point whose objective value is as small as the comparison set you named. If the comparison set is the whole feasible region, the point is a global minimizer. If the comparison set is the feasible part of some ball around the point, the point is a local minimizer. Every global minimizer is local. The converse is false: a valley can be the lowest point nearby and still sit above some distant valley.

The inequality can be strict or not. A strict minimizer is one that no other point in the comparison set ties. A non-strict minimizer shares its value with at least one other feasible point. A function with two isolated zeros of a square, such as a squared distance from a two-point set, has two strict global minimizers.

The infimum is the greatest lower bound of the values. It is always defined in the extended reals. A minimum is an infimum that the function attains. The argmin set is the set of feasible points where the attained value equals the infimum. That set can be empty, a singleton, or a large set, independently of whether a local minimizer exists somewhere else."""},
        {"heading": "Key equations",
         "body_md": r"""The point \(x^\star\) is a global minimizer when \(x^\star\) is feasible and \(f(x^\star) \le f(x)\) for every feasible \(x\). It is local when the same inequality holds for the feasible points of some ball. Either definition is strict when the inequality is strict for every other point of the comparison set. The optimal value is \(p^\star = \inf f(\mathcal{X})\), and
\[
\operatorname{argmin} f = \{x \in \mathcal{X} : f(x) = p^\star\}.
\]
The set is empty when the infimum is not attained."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(t) = (t^2 - 16)^2 + 28\). The squared factor is nonnegative, so \(f(t) \ge 28\), and equality holds at \(t = 4\) and at \(t = -4\). The shared floor is 28. Both points are global minimizers. Each is also a strict local minimizer, because a small neighborhood of one of them excludes the other and the square is positive in between.

The point \(t = 0\) has value \(256 + 28\), which is much higher, and it is not a minimizer of either kind. The argmin set has two points. Neither minimizer is strict as a global minimizer, because the other one ties it. Strictness depends on which comparison set you named."""},
        {"heading": "Common pitfalls",
         "body_md": r"""A zero gradient is not the definition of a minimizer. It is a later calculus test, and it can hold at a maximizer. Local is not global: the cubic \(t^3 - 3t\) has a local minimizer at \(t = 1\) and is unbounded below. An infimum is not automatically a value of the function. The exponential tends to 0 and never reaches it, so its argmin set on the line is empty even though the infimum is finite. Reporting the minimizer when the question asks for the minimum value mixes a point with a number."""},
        {"heading": "Where this leads",
         "body_md": r"""Existence theorems say when the argmin set is nonempty: a continuous function on a nonempty compact set, or a continuous coercive function on a nonempty closed set. First-order necessary conditions describe interior local minimizers. For a convex function the local and global notions collapse, and a stationary point is already global."""},
    ]
    save_explainer("local-global-minima", "Local and global minimizers", sections)


def expl_existence():
    sections = [
        {"heading": "The idea", "figure": DISK, "figure_alt": A_DISK,
         "body_md": r"""A lower bound is not the same thing as a point where the bound is achieved. Existence is the question of whether the argmin set is nonempty. Two sufficient situations cover most of the smooth problems in this subject.

The first is compactness. In real space a set is compact when it is closed and bounded. A continuous function on a nonempty compact set attains its minimum and its maximum. The closed unit disk is compact. An open disk is not, and a line is not. The theorem does not say the minimizer is interior. On a disk it often sits on the boundary.

The second situation is an unbounded set, where compactness is unavailable. A continuous function that is coercive, meaning the values tend to infinity as the norm does, still attains a minimum on a nonempty closed set. Coercivity makes the sublevel sets bounded, continuity makes them closed, and a feasible point makes one of them nonempty. Coercivity is sufficient and not necessary. A sine attains its minimum on the line without tending to infinity."""},
        {"heading": "Key equations",
         "body_md": r"""If \(\mathcal{X}\) is nonempty and compact and \(f\) is continuous, there exists \(x^\star \in \mathcal{X}\) with \(f(x^\star) = \inf_{\mathcal{X}} f\). If \(\mathcal{X}\) is nonempty and closed, \(f\) is continuous, and \(f(x) \to +\infty\) as \(\lVert x \rVert \to \infty\) with \(x \in \mathcal{X}\), the same conclusion holds. A sublevel set \(\{x \in \mathcal{X} : f(x) \le f(x_0)\}\) of a coercive continuous function is compact once it is nonempty."""},
        {"heading": "Worked example",
         "body_md": r"""Minimize \((x - 2)^2 + (y + 1)^2 + 11\) over the closed disk of radius 5 centered at the origin. The squares vanish at \((2, -1)\). That point has norm \(\sqrt{5}\), which is less than 5, so it is feasible. The disk minimum is 11, and it is attained at that single interior point.

The same function on the whole plane has the same minimizer, now by coercivity rather than by compactness: the squares dominate at infinity. If the added constant were removed, the minimum value would change and the minimizer would not. If the disk were replaced by its interior, this particular minimizer would remain feasible. A minimizer on the boundary would not survive that opening."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Closed is not enough, and bounded is not enough. The half-line of nonnegative reals is closed and unbounded, and \(e^{-t}\) decreases toward 0 without attaining it. The open interval \((0, 1)\) is bounded and not closed, and the identity has infimum 0 with no minimizer. Applying the compact-set theorem to either set is the usual false step. A stationary point is also not an existence proof. The exponential on the line has no stationary point and no minimizer. A coercive function can have both."""},
        {"heading": "Where this leads",
         "body_md": r"""Once a minimizer is known to exist, the next work is to name it. For a smooth unconstrained problem the candidates are the stationary points, and the second-order test classifies them. Coercivity of a positive definite quadratic is the reason that quadratic has a minimizer before anyone solves the linear system."""},
    ]
    save_explainer("existence-of-minimizers", "Existence of minimizers", sections)


def expl_first():
    sections = [
        {"heading": "The idea", "figure": GRAD, "figure_alt": A_GRAD,
         "body_md": r"""A differentiable function cannot have a local minimizer at an interior point where the gradient is nonzero. The negative gradient is a descent direction, and a short step in that direction stays inside the feasible set and lowers the value. The necessary condition is Fermat's rule: at an interior local minimizer the gradient is the zero vector.

A point where the gradient vanishes is called stationary. The rule says every interior local minimizer is stationary. It does not say every stationary point is a minimizer. A stationary point may be a local maximizer or a saddle, and a local minimizer need not be global. The rule is a filter. It produces a list of candidates, and some other test has to sort the list.

The interior hypothesis is doing real work. On a closed interval the minimum of a linear function sits at an endpoint, where the derivative need not vanish. The descent direction points out of the set, so the feasible points nearby are not lower. Constrained problems replace the zero-gradient equation by a balance against the constraint gradients. Forcing the objective gradient to vanish anyway is the unconstrained test applied in the wrong place."""},
        {"heading": "Key equations",
         "body_md": r"""If \(x^\star\) is an interior local minimizer and \(f\) is differentiable there, then \(\nabla f(x^\star) = 0\). In one variable this is \(f'(t^\star) = 0\). A point is stationary when that equation holds. If \(\nabla f(x) \ne 0\) and \(x\) is interior, then \(x\) is not a local minimizer. For \(f(x) = \tfrac12 x^T A x + b^T x\) with \(A\) symmetric, stationarity is the linear equation \(A x + b = 0\)."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(t) = (t - 5)^2 + 9\). The derivative is \(2(t - 5)\), which vanishes at \(t = 5\) and nowhere else. The interior slope vanishes at height 9, because \(f(5) = 9\). The second derivative is the positive constant 2, so the stationary point is a strict local minimizer. The function is a square plus a constant, so the same point is the unique global minimizer and the minimum value is 9.

A different base point, say \(t = 1\), has derivative \(2(1 - 5) = -8\), which is not zero. That point is interior and is not a minimizer. Moving a little to the right decreases the function. The constant 9 never enters the derivative, so it cannot create or destroy stationarity."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Setting the derivative to zero at a boundary point can miss the minimizer, as with \(f(t) = t\) on \([0, 1]\), whose minimum is at 0 and whose derivative is 1. The opposite mistake is to treat every stationary point as a minimizer. The cubic \(t^3 - 3t\) is stationary at \(t = \pm 1\), and only one of those points is a local minimizer, and that one is not global. A third mistake is to solve the derivative equation and report a coordinate when the question asks for the function value, or the reverse."""},
        {"heading": "Where this leads",
         "body_md": r"""The second-order test reads the Hessian at each stationary point and sorts minimizers, maximizers, and saddles. For a convex function the first-order condition is already sufficient for a global minimizer. On an equality constraint the same idea becomes a linear dependence between the objective gradient and the constraint gradients."""},
    ]
    save_explainer("first-order-optimality", "First-order necessary condition", sections)


def expl_second():
    sections = [
        {"heading": "The idea", "figure": HESS, "figure_alt": A_HESS,
         "body_md": r"""Stationarity is not a verdict. The second-order test reads the curvature at a stationary point and, in the definite cases, finishes the classification. The necessary condition says that an interior local minimizer has a positive semidefinite Hessian. A negative eigenvalue would be a direction of decrease, which an interior local minimizer cannot have. The matching necessary condition for a local maximizer is a negative semidefinite Hessian.

The sufficient condition is stricter. If the gradient vanishes and the Hessian is positive definite, the second-order Taylor model is a strict bowl, and the point is a strict local minimizer. Negative definite curvature gives a strict local maximizer. An indefinite Hessian, with both a positive and a negative eigenvalue, gives a saddle: the function rises in one direction and falls in another.

A zero eigenvalue makes the sufficient test silent. The point might be a minimizer, like the origin of \(t^4\) or of \(x^2\), or it might not, like the origin of \(t^3\). Silence is not a saddle. The necessary condition still allows the zero eigenvalue. Positive semidefiniteness is necessary and not sufficient."""},
        {"heading": "Key equations",
         "body_md": r"""At an interior local minimizer, \(H_f(x^\star)\) is positive semidefinite. If \(\nabla f(x^\star) = 0\) and \(H_f(x^\star)\) is positive definite, then \(x^\star\) is a strict local minimizer. If the Hessian is indefinite, \(x^\star\) is a saddle. In one variable the two curvature tests are \(f''(t^\star) \ge 0\) as necessary, and \(f''(t^\star) > 0\) as sufficient. A vanishing second derivative decides neither question."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(x, y) = x^2 - y^2 + 8\). The gradient is \((2x, -2y)\), so the only stationary point is the origin. The Hessian is diagonal with entries 2 and \(-2\). The eigenvalues have opposite signs, so the origin is a saddle. The saddle height is 8, the value of the added constant.

Along the \(x\) axis the function is \(x^2 + 8\), which lies above 8. Along the \(y\) axis it is \(-y^2 + 8\), which lies below 8. That pair of directions is the whole second-order classification. Moving the constant would move the height and would not change the Hessian, the stationary point, or the saddle verdict."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Positive definiteness is sufficient, and people promote it to a necessary condition. The function \(t^4\) has a strict minimizer where the second derivative is zero, so necessity stops at semidefiniteness. The reverse promotion is also wrong: a positive semidefinite Hessian does not imply a minimizer, because \(t^3\) has a vanishing second derivative at a point that is not a local minimizer. A zero eigenvalue is not a saddle and not a loss of stationarity. Stationarity was already imposed. Finally, a strict local minimizer from this test need not be global unless the function is convex or coercive."""},
        {"heading": "Where this leads",
         "body_md": r"""Classifying every stationary point is this test applied to the whole list, followed by a global argument. For a quadratic the Hessian is constant, so one matrix decides the local picture everywhere, and positive definiteness gives a unique global minimizer. Least squares is the quadratic whose Hessian is twice a Gram matrix."""},
    ]
    save_explainer("second-order-optimality", "Second-order optimality conditions", sections)


def expl_stationary():
    sections = [
        {"heading": "The idea", "figure": WIGGLE, "figure_alt": A_WIGGLE,
         "body_md": r"""Classification is a complete pass over the stationary points, not a check of one favorite candidate. You compute the gradient, set it equal to zero, and solve the system for every real solution. Each solution then gets a Hessian test. Positive definite means a strict local minimizer. Negative definite means a strict local maximizer. Indefinite means a saddle. A zero eigenvalue means the second-order test has nothing to say, and the point has to be settled by the sign of the function or by a higher-order look.

A local label is not a global label. After the list is classified, a global claim needs an extra reason. Coercivity, or a compact sublevel set, says a global minimizer exists, and it must be one of the local minimizers you found, because every interior minimizer is stationary. Comparing the values at the local minimizers then names the global ones.

The same discipline catches a false global claim. A note that stops at the first point where the gradient vanishes has not looked at the other solutions, and it has not checked the behavior at infinity."""},
        {"heading": "Key equations",
         "body_md": r"""Solve \(\nabla f(x) = 0\). At each solution evaluate the eigenvalues of \(H_f\). The point is a strict local minimizer when every eigenvalue is positive, a strict local maximizer when every eigenvalue is negative, and a saddle when both signs appear. For a coercive smooth function the global minimum value is the smallest value of \(f\) on the local-minimizer list. If that list is empty, a coercive function is not what you have."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(x, y) = x^2 + 2y^2 - 6x + 4y + 24\). The gradient is \((2x - 6,\ 4y + 4)\), so the only stationary point is \((3, -1)\). The Hessian is diagonal with entries 2 and 4, both positive, so the point is a strict local minimizer. The function is a sum of squares plus a constant after completing the square, and it tends to infinity at infinity.

The classified height is 13. The arithmetic is \(9 + 2 - 18 - 4 + 24\). There is no second stationary point to compare, and coercivity says this local value is the global minimum. A zero eigenvalue would have blocked that sentence and forced a look at the flat direction."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Stopping after one root of the gradient equation misses a lower one. The polynomial \(t^4 - 8t^2\) has a local maximum at the origin and two global minimizers at the opposite roots, and the origin is the root most people see first. Treating a zero eigenvalue as a saddle is the other standard error. The function \(x^2 + y^4\) is stationary only at the origin, the Hessian there is singular, and the origin is a strict global minimizer because the function is nonnegative. An indefinite Hessian really is a saddle. A singular one is a question mark."""},
        {"heading": "Where this leads",
         "body_md": r"""Newton's method for minimization solves the same gradient equation by linearizing it, and it can converge to a saddle as easily as to a minimizer. The classification is what says which arrival is useful. On a constraint the points you classify are stationary for a Lagrangian, and the objective gradient itself may be nonzero."""},
    ]
    save_explainer("stationary-point-classification", "Classifying stationary points", sections)


def expl_convex_opt():
    sections = [
        {"heading": "The idea", "figure": BOWL, "figure_alt": A_BOWL,
         "body_md": r"""Convexity changes what a stationary point is worth. For a general smooth function, a zero gradient is only a candidate. For a differentiable convex function, the graph lies above every tangent. At a point where the gradient vanishes, the tangent is the horizontal line at the function value, so every other point of the domain lies on or above that line. The stationary point is a global minimizer.

The same conclusion can be reached from the local side. A local minimizer of a convex function is global, with or without a derivative. Differentiability adds the convenient test: find a stationary point, and you are done. There is no second valley hiding somewhere else.

Strict convexity adds uniqueness. If two distinct points shared the minimum value, the chord between them would lie on the graph, and strict convexity forbids that. A strictly convex differentiable function has at most one stationary point, and if it has one, that point is the unique global minimizer. A convex function that is not strict can have a whole line of minimizers, as a square of a single linear form does."""},
        {"heading": "Key equations",
         "body_md": r"""If \(f\) is differentiable and convex and \(\nabla f(x^\star) = 0\), then \(f(y) \ge f(x^\star)\) for every \(y\) in the domain. The reason is the tangent inequality
\[
f(y) \ge f(x^\star) + \nabla f(x^\star)^T (y - x^\star) = f(x^\star).
\]
If \(f\) is strictly convex, the minimizer is unique. A positive definite Hessian everywhere implies strict convexity. A positive semidefinite Hessian everywhere implies convexity and allows a nontrivial argmin set."""},
        {"heading": "Worked example",
         "body_md": r"""Let \(f(t) = 2t^2 - 8t + 23\). The derivative is \(4t - 8\), which vanishes at \(t = 2\). The second derivative is the positive constant 4, so \(f\) is strictly convex and the stationary point is the unique global minimizer. The convex floor is 15, because \(f(2) = 8 - 16 + 23\).

Completing the square tells the same story: \(f(t) = 2(t - 2)^2 + 15\). The constant 23 moved the floor and did not move the minimizer. If the leading coefficient were zero, the function would be affine, still convex, and a stationary point would exist only in the degenerate case of a zero slope, where every point is a minimizer."""},
        {"heading": "Common pitfalls",
         "body_md": r"""The convexity hypothesis is not optional. The derivative of \(t^3\) vanishes at the origin, and \(t^3\) is not convex, and the origin is not a minimizer. Quoting the theorem without the hypothesis is the usual false proof. A second mistake is to expect uniqueness from convexity alone. The function \(x^2\) on the plane is convex, stationary on the whole second axis, and every one of those points is a global minimizer. Strict convexity is the extra ingredient. A positive definite Hessian at a single point does not make the function convex on its domain."""},
        {"heading": "Where this leads",
         "body_md": r"""A positive definite quadratic is the cleanest case: one linear system, one solution, and a theorem that says the solution is the unique global minimizer. On a convex feasible set the zero-gradient test is replaced by a variational inequality, and convexity of the objective again promotes that first-order condition to global optimality. Least squares is a convex quadratic, so the normal equations are enough."""},
    ]
    save_explainer("convex-optimality-global", "Optimality for convex functions", sections)


def expl_quadratic():
    sections = [
        {"heading": "The idea", "figure": ELL, "figure_alt": A_ELL,
         "body_md": r"""A quadratic is the function a symmetric matrix, a linear term, and a constant can build: one half of \(x^T A x\), plus \(b^T x\), plus \(c\). The one half is a bookkeeping choice. It makes the gradient equal to \(A x + b\) and the Hessian equal to \(A\), with no extra factor of two to carry around. If a model is handed to you with an unsymmetric matrix, replace that matrix by its symmetric part before doing anything else. The function does not change.

Stationarity is the linear system \(A x = -b\). When \(A\) is positive definite the system has one solution, the function is strictly convex and coercive, and that solution is the unique global minimizer. The minimum value is \(c\) minus one half of \(b^T A^{-1} b\).

When \(A\) is only positive semidefinite the function is still convex, and a minimizer exists exactly when \(-b\) lies in the column space of \(A\). If it does, the solutions form an affine subspace parallel to the null space, and they all share one value. If it does not, the linear term points into a flat direction and the function is unbounded below. An indefinite \(A\) is unbounded below in every case."""},
        {"heading": "Key equations",
         "body_md": r"""With \(A\) symmetric,
\[
\nabla f(x) = A x + b, \qquad H_f(x) = A.
\]
The minimizer of a positive definite quadratic is \(x^\star = -A^{-1} b\), and
\[
f(x^\star) = c - \tfrac12 b^T A^{-1} b.
\]
The quadratic is coercive exactly when \(A\) is positive definite. Along a line, the restriction \(\tfrac12 a t^2 + g t\) with \(a > 0\) is minimized at \(t = -g/a\)."""},
        {"heading": "Worked example",
         "body_md": r"""Take \(A = \operatorname{diag}(2, 2)\), \(b = (-6, -2)\), and \(c = 29\). The system \(A x = -b\) reads \((2x, 2y) = (6, 2)\), so the minimizer is \((3, 1)\). The Hessian is positive definite, and there are no other candidates.

The solved quadratic floor is 19. One check is the value formula: \(A^{-1} b = (-3, -1)\), the dot product \(b^T A^{-1} b\) equals 20, and \(29 - 10 = 19\). The direct substitution \(9 + 1 - 18 - 2 + 29\) gives the same number. Changing \(c\) would shift the floor and would leave the minimizer where it is."""},
        {"heading": "Common pitfalls",
         "body_md": r"""Positive semidefinite is not enough for existence. The function \(\tfrac12 x^2 + y\) has a positive semidefinite Hessian and is unbounded below, because the linear term in \(y\) never meets a restoring force. The false theorem is "convex implies the minimum is attained." Convexity supplies the tangent lower bound. Attainment is the column-space condition, or coercivity. A second mistake is to keep a factor of one half in the gradient after it was already used to simplify the derivative of the quadratic term. A third is to read eigenvalues of an unsymmetric matrix and call them the curvature."""},
        {"heading": "Where this leads",
         "body_md": r"""Linear least squares is this quadratic with Hessian twice a Gram matrix, and the normal equations are \(A x = -b\) in that notation. An exact line search on a quadratic restricts the function to a line and uses the one-dimensional minimizer \(-g/a\). A convex quadratic with linear constraints is the model behind a support-vector objective once the constraints are restored."""},
    ]
    save_explainer("quadratic-function-minimization", "Minimizing quadratic functions", sections)


def doc_words(sections):
    text = "\n".join(s.get("body_md") or "" for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


def main():
    bank_formulation()
    bank_graphical()
    bank_classes()
    bank_local()
    bank_existence()
    bank_first()
    bank_second()
    bank_stationary()
    bank_convex_opt()
    bank_quadratic()
    expl_formulation()
    expl_graphical()
    expl_classes()
    expl_local()
    expl_existence()
    expl_first()
    expl_second()
    expl_stationary()
    expl_convex_opt()
    expl_quadratic()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    banned = ("graz", "boyd", "nocedal", "vandenberghe", "hefferon", "wikibook",
              "textbook", "university", "professor", "lecture", "syllabus", "cambridge", "springer")
    ids = [
        "optimization-problem-formulation",
        "graphical-2d-optimization",
        "optimization-problem-classes",
        "local-global-minima",
        "existence-of-minimizers",
        "first-order-optimality",
        "second-order-optimality",
        "stationary-point-classification",
        "convex-optimality-global",
        "quadratic-function-minimization",
    ]
    private = {
        "optimization-problem-formulation": "The baker's recorded profit is 26",
        "graphical-2d-optimization": "The depot level is 11",
        "optimization-problem-classes": "The symmetrized corner is 7",
        "local-global-minima": "The shared floor is 28",
        "existence-of-minimizers": "The disk minimum is 11",
        "first-order-optimality": "The interior slope vanishes at height 9",
        "second-order-optimality": "The saddle height is 8",
        "stationary-point-classification": "The classified height is 13",
        "convex-optimality-global": "The convex floor is 15",
        "quadratic-function-minimization": "The solved quadratic floor is 19",
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
