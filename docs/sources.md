# Source registry

Licenses were checked on 2026-11-06. A source that is not openly licensed is treated as fully copyrighted: it is read for scope and facts, and none of its wording, problems, parameter sets, or figures is stored in this repo.

Learner-facing text does not name a reader or a textbook. The skill panel renders `sources` as "Further reading", so B1 citations stay in this file and not on the skill records.

## Sources

| id | work | license | use |
|---|---|---|---|
| `fbs-v315` | Karl Johan Åström and Richard M. Murray, *Feedback Systems*, electronic edition v3.1.5 (2020-07-24), http://fbsbook.org. Princeton University Press hardback is a separate edition. | Personal-use manuscript. The front matter says it may not be reproduced without the publisher's consent. Not an open license. | Reference only. Chapter files were fetched locally for the shingle gate and were not committed. |
| `lst-2020` | Richard M. Murray, *Notes on Linear Systems Theory*, draft of 30 October 2020, supplement to the same course. | Creative Commons Attribution-ShareAlike 4.0. The notes' title page states the license. | Second canonical source for `laplace` and `lin-algebra-review`. |
| `hefferon-linalg` | Jim Hefferon, *Linear Algebra*, 4th edition. License page: https://hefferon.net/source.html | GNU Free Documentation License, or Creative Commons Attribution-ShareAlike 3.0 United States, at the reader's choice. | Second canonical source for `lin-algebra-review`. The historical `book.pdf` URL returned 404 on the day of this check, so that file is not in the shingle set. |
| `wb-control` | Wikibooks, *Control Systems* (Feedback Loops, System Modeling, Poles and Zeros, Transfer Functions). | Creative Commons Attribution-ShareAlike. | Second canonical source for `fb-concepts`, `ode-model`, and `min-phase`. |
| `me132-f26` | ME 132 Fall 2026 syllabus and notes. | Not on file. | Scope only. Not a wording source. |

## Section map for B1

The skill graph used to cite 2008 section numbers. The gate used the 2020 chapter files, which renumber some of those topics.

| skill | 2008 pointer that was on the skill | text actually compared |
|---|---|---|
| `fb-concepts` | §§1.1–1.4 | `fbs-intro` §§1.1–1.4, plus the Wikibooks feedback-loop page |
| `ode-model` | §2.1 | `fbs-modeling` chapter 3 (modeling with differential equations), plus the Wikibooks system-modeling page |
| `laplace` | §8.5 | `fbs-xfer` §9.3 (Laplace transforms), plus `lst-sig` |
| `lin-algebra-review` | appendix | `lst-lin` (the 2020 back matter is an index, not a linear-algebra appendix), with Hefferon recorded as the open textbook |
| `min-phase` | §9.4 | `fbs-loop` chapter 10 (minimum phase, all-pass, delay, inverse response). In the 2020 edition, §9.4 is block-diagram algebra, a later batch. |

## optimization

Added for the nonlinear optimization skills. Course notes fix the scope. Wording, problems, parameter sets, and figures in the banks are original.

| id | work | license | use |
|---|---|---|---|
| `boyd-cvx` | Stephen Boyd and Lieven Vandenberghe, *Convex Optimization*, Cambridge University Press, 2004. The authors' PDF is posted for personal download. | Not an open license. | Reference for sets, norms, convexity, and optimality. Not a wording source. |
| `nw-numopt` | Jorge Nocedal and Stephen J. Wright, *Numerical Optimization*, second edition, Springer, 2006. | Not an open license. | Reference for optimality, least squares, and the algorithms in later batches. Not a wording source. |
| `hefferon-linalg` | Already registered above. | GFDL or CC BY-SA 3.0 US. | Open linear-algebra source for eigenvalues, rank, and inner products. |
| `wikibooks-linalg` | Wikibooks, *Linear Algebra* (vector spaces, inner products, eigenvalues). | Creative Commons Attribution-ShareAlike. | Open second source for the NB1 linear-algebra skills. |
| `nlo-notes` | Nonlinear optimization course notes and syllabus. | Not on file as an open license. | Scope only. Not a wording source. |

NB1 uses `hefferon-linalg` and `wikibooks-linalg` for the linear-algebra facts, and `boyd-cvx` (appendix on matrices, norms, and singular values; chapter on convex sets) for the set and norm language. No section of those sources is quoted in the banks or explainers.

NB2 uses the same three references for the next preliminaries layer. `boyd-cvx` supplies the scope for induced norms, the Frobenius and Schatten norms, open and closed sets, compactness in \(\mathbb{R}^n\), sublevel and contour sets, and convex sets. `hefferon-linalg` and `wikibooks-linalg` supply the open linear-algebra reading for singular values and entrywise lengths. No section is quoted, and no exercise or parameter set is reused.

NB3 uses the same references for derivatives. `boyd-cvx` supplies the scope for the gradient, the Hessian, the chain rule, and the Taylor model. `nw-numopt` supplies the scope for the mean-value form and the remainder bound. No section is quoted, and no exercise or parameter set is reused.

NB4 uses the same references for convex functions and for computing derivatives. `boyd-cvx` supplies the scope for the chord definition and the first- and second-order characterizations. `nw-numopt` supplies the scope for finite-difference truncation and round-off, and for automatic differentiation: computational graphs, forward mode, reverse mode, and Hessian-vector products. The small-network skill is reverse mode applied to a two-layer loss. No section is quoted, and no exercise, weight set, or parameter set is reused.

NB5 uses the same references for problem formulation and unconstrained optimality. `boyd-cvx` supplies the scope for the decision variable, the objective, the feasible set, the optimal value, local and global minimizers, and the classes LP, QP, and convex programs. `nw-numopt` supplies the scope for existence on compact or coercive problems, the first- and second-order necessary and sufficient conditions, classification of stationary points, the convex case in which stationarity is global, and minimization of a quadratic. No section is quoted, and no exercise or parameter set is reused.

NB6 uses the same references for linear programming. `boyd-cvx` supplies the scope for polyhedra, extreme points, and the geometry of a linear objective on a convex set. `nw-numopt` supplies the scope for standard form, basic feasible solutions, reduced costs, the ratio test, one simplex iteration, and the auxiliary problem that finds a first basis. No section is quoted, and no exercise or parameter set is reused.

NB7 uses the same references for multipliers, duality, and least squares. `boyd-cvx` supplies the scope for the Lagrangian, the dual function as a lower bound, weak duality, the KKT system, the dual of a standard-form linear program, projection onto an affine set and a half-space, and a maximum-margin linear separator written as a convex quadratic program. `nw-numopt` supplies the scope for equality-constrained stationarity and the failure of the multiplier rule without regularity, the normal equations, linear and nonlinear least squares, and an algebraic circle fit. No section is quoted, and no exercise or parameter set is reused.

NB8 uses the same references for gradient methods. `boyd-cvx` supplies the scope for a Lipschitz gradient, the quadratic upper bound, sufficient decrease of a gradient step, and the sublinear guarantee obtained by summing those decreases. `nw-numopt` supplies the scope for descent directions, the general descent iteration, rates of convergence, exact line search on a quadratic, backtracking, the zig-zag of steepest descent, and the condition-number factor on a quadratic. No section is quoted, and no exercise or parameter set is reused.

NB9 uses the same references for Gauss-Newton, damping, block updates, and Newton on a nonlinear equation. `nw-numopt` supplies the scope for a Gauss-Newton step, a damped step, and a Newton iteration for a root. `nlo-notes` supplies the scope for cycling through data blocks and for reading one linear least-squares update as the measurement step of a Kalman filter. `boyd-cvx` supplies the scope for the least-squares objective those steps minimize. No section is quoted, and no exercise or parameter set is reused. The linear filter recursion stays in the Kalman core and is not rewritten here.

NB10 uses the same references for Newton on an objective and for quasi-Newton updates. `nw-numopt` supplies the scope for the Newton step from a quadratic model, local quadratic convergence under a Lipschitz Hessian, diagonal shifts and line searches that restore descent, the Wolfe conditions and the curvature consequence \(y^T s > 0\), the secant equation, and the BFGS inverse update. `boyd-cvx` supplies the scope for the gradient and Hessian of a smooth objective and for positive definite quadratic models. `nlo-notes` supplies the scope for affine invariance and for the attraction of an unmodified Newton step to a maximum or a saddle. No section is quoted, and no exercise or parameter set is reused.

NB11 uses the same references for conjugate directions and acceleration. `nw-numopt` supplies the scope for orthogonalizing a list in a \(Q\)-inner product, \(Q\)-conjugacy and finite termination, the conjugate-gradient direction update, its rate in the condition number, heavy-ball momentum, and an extrapolate-then-step acceleration. `boyd-cvx` supplies the scope for a smooth convex function gap and for the quadratic upper bound an accelerated step relies on. `nlo-notes` supplies the scope for reading the momentum update as a finite-difference discretization of a damped second-order equation. No section is quoted, and no exercise or parameter set is reused. The \(O(1/k^2)\) claim is a bound on \(f(x_k) - f^\star\), not on the distance to a minimizer.

## Section map for B7

Scope only. The skill records already point at the sections. No wording, problems, parameter sets, or figures were taken from them. Learner-facing text does not name the works below.

| skill | scope used |
|---|---|
| `state-feedback` | state feedback \(u = -Kx\), the closed-loop matrix \(A-BK\), and the single-input gain solve |
| `observer` | the correction \(L(y-C\hat{x})\) and the error matrix \(A-LC\) |
| `fund-limits` | the sensitivity integral, right-half-plane poles and zeros, and the bandwidth conflict |
| `robust-perf` | nominal performance, robust stability, and the combined weighted-\(S\) and weighted-\(T\) bound |
| `adaptive` | an online parameter update inserted into the controller. The skill record's pointer is outside the main text and was used only to bound the topic. |

## Section map for B8

Scope only. No wording, problems, parameter sets, or figures were taken from the works below. Learner-facing text does not name them.

| skill | scope used |
|---|---|
| `gaussian-random-vectors` | mean, covariance, and the covariance of an affine image of a Gaussian vector |
| `kalman` | the predict and update recursion, the gain, and the covariance update for a linear model with process and measurement noise. No optimality proof |
| `kalman-optimal-observer` | the same gain as the linear correction of minimum error variance, including the scalar derivative and the steady filter |
| `separation` | the joint eigenvalues of state feedback and an observer, and what a reference does and does not excite |
| `gen-controller` | a command with a reference feedforward term and feedback from an estimate |
| `integral-action` | an extra state that integrates the tracking error inside state feedback |
| `lqr` | a quadratic cost, the algebraic Riccati equation, and the constant gain it produces |
| `mpc` | a finite horizon, constraints, and applying only the first computed input |
| `fb-linearization` | an input map that cancels a known nonlinearity where the input coefficient is nonzero |
| `gain-scheduling` | linear designs at several operating points, interpolated from a measured schedule |

The open readings for the covariance facts are Hefferon and the Wikibooks linear-algebra notes already registered above, used only for the matrix identities. The filter and regulator facts use the same control references already registered for B7, as scope only.

## Errata

No separate errata list was in the v3.1.5 front matter or the back-matter index. Nothing in those files changes the B1 facts (element laws, transform rules, rank and eigenvalues, or the minimum-phase conditions). No erratum was applied.
