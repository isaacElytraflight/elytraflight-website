# Nonlinear optimization content batches

Approved skill graph for the course box `nlo-tugraz`. A skill is eligible for a content batch only when every prerequisite is already playable or sits in an earlier batch. NB1 is the first content batch. NB2–NB12 stay in the graph as coming-soon skills until a later batch writes them.

## Course summary
- **Course:** Nonlinear Optimization (NLO), TU Graz, course number 710.021, Institute of Visual Computing. Format: 3VO + 2UE (4.5 + 2.5 ECTS), WS 2026/27.
- **Boxes:** course box `nlo-tugraz` ("Nonlinear Optimization (TU Graz)", top-level). Chapter boxes `nlo-tugraz/l1` through `l12` follow the lecture topics below. Textbook boxes can wait.

## Chapter boxes

| box | title | skills |
|---|---|---|
| `nlo-tugraz/l1` | Problem formulation | `optimization-problem-formulation`, `graphical-2d-optimization`, `optimization-problem-classes`, `svm-quadratic-program` |
| `nlo-tugraz/l2` | Mathematical preliminaries | `lin-algebra-review`, `gaussian-random-vectors`, NB1 (8 skills), NB2 (6 skills) |
| `nlo-tugraz/l3` | Derivatives and automatic differentiation | NB3 (9 skills), NB4 (9 skills) |
| `nlo-tugraz/l4` | Optimality conditions | the seven optimality skills in NB5 |
| `nlo-tugraz/l5` | Linear programming and the simplex method | NB6 (7 skills) |
| `nlo-tugraz/l6` | Lagrange multipliers and duality | `lagrangian-duality-lower-bounds`, `lagrange-multiplier-equality`, `kkt-conditions`, `lp-duality-kkt`, `projection-affine-halfspace-kkt` |
| `nlo-tugraz/l7` | Least squares | `linear-least-squares`, `least-squares-data-fitting`, `nonlinear-least-squares`, `circle-fitting-least-squares` |
| `nlo-tugraz/l8` | Gradient methods | NB8 (11 skills) |
| `nlo-tugraz/l9` | Gauss-Newton and incremental methods | `kalman`, NB9 except `newton-root-finding` |
| `nlo-tugraz/l10` | Newton and quasi-Newton methods | `newton-root-finding`, NB10 (6 skills) |
| `nlo-tugraz/l11` | Accelerated gradient methods | NB11 (5 skills) |
| `nlo-tugraz/l12` | Optimization over a convex set | NB12 (8 skills) |

`lin-algebra-review` keeps its id. Its display title in this graph is "Linear algebra review". `backprop-neural-network` sits in `l3`. `svm-quadratic-program` sits in `l1`.
- **Topics, in lecture order:**
  1. Introduction: problem formulation; LP, QP and convex programs.
  2. Mathematical preliminaries.
  3. Computing derivatives and automatic differentiation. The syllabus lists this under preliminaries.
  4. Optimality conditions.
  5. Linear programming and simplex.
  6. Lagrange multipliers, KKT and LP duality.
  7. Least squares.
  8. Gradient methods: line search and convergence theory.
  9. Gauss-Newton, Levenberg-Marquardt, incremental methods and Kalman filter.
  10. Newton, quasi-Newton, BFGS and Wolfe conditions.
  11. Accelerated methods: CG, heavy ball and Nesterov.
  12. Optimization over a convex set: projection, gradient projection, affine scaling and interior-point methods, Frank-Wolfe, power method.
- **Assessment shape** (from the practicals deck): pen-and-paper only. Partial exam 1 covers preliminaries through least squares (batches NB1–NB7). Partial exam 2 covers gradient methods through convex sets (NB8–NB12). Question banks should favor hand-computable numbers and proof steps turned into decisions.
- **Totals:** 95 new skills. 31 of them are mathematical preliminaries: every preliminaries topic in the syllabus, including computing derivatives and AD. The plan also reuses 1 existing skill (`lin-algebra-review`). There are 12 batches (NB1–NB12) of 5–11 skills each.

## Content rule for all writers
The course materials are **inspiration and scope only**.
- No copying and no close paraphrase.
- Do not reuse their exercises, worked examples, parameter sets or figures. Invent fresh scenarios and numbers, and build figures with our own helpers.
- Learner-facing text stays source-agnostic: no course, professor, textbook, lecture-note or university names.
- Source pointers below are for internal briefs only.

## Dedupe against the existing graph (170 skills)
- **Reused:** `lin-algebra-review` covers rank, null space, eigenvalues and eigenvectors, trace and determinant, and similarity. It is already a neutral core with no prerequisites. It becomes a prerequisite of `spectral-decomposition`, `inner-products`, `basic-feasible-solutions`, `lagrange-multiplier-equality` and `linear-least-squares`. Add it to the NLO course box. Its display title, "Linear algebra for state space", is control-flavored (see open questions).
- **Related, kept separate (no prerequisite edge):**
  - `linearization` (ME132, about equilibria) is separate from `taylor-approximation-multivariable`.
  - `eig-modes` covers eigenvalues of dynamics, not spectral decomposition.
  - `lqr` and `sys-id` are untouched. `lqr` is not given an edge to `quadratic-function-minimization` or `positive-definite-matrices`.
- Every new id was checked for collisions against all 170 existing ids: none collide. All new skills are neutral math or optimization cores. Only `backprop-neural-network` and `svm-quadratic-program` are domain applications (ML), and they sit only in the NLO box. `gaussian-random-vectors` was added later, with SG-056, and does not collide.
- The graph is acyclic (checked) and every batch is prerequisite-closed (checked). Some skills depend on others in the same batch; writers handle those in the listed order.

## SG-056 Kalman core

`kalman` is a course-neutral core, shared by the ME 132 and NLO boxes (and kept in Feedback Systems). It teaches the predict/update recursion, the gain, and the covariance. The model \(x_{k+1}=A x_k+w_k\), \(y_k=C x_k+v_k\) is part of that skill. There is no optimality proof in the core.

- New skill `gaussian-random-vectors` (Gaussian random vectors and covariance, including \(A P A^T\)). Prerequisite: `lin-algebra-review`. It sits in the NLO preliminaries chapter, in ME 132, and in Feedback Systems. Both it and `kalman` are written with ME 132 batch B8, not in an NB batch.
- `kalman` prerequisites are `lin-algebra-review` and `gaussian-random-vectors`. The old edge from `observer` is removed so an optimization learner is not sent through a control-only skill.
- `kalman` is an added prerequisite of `kalman-recursive-least-squares`. That skill stays coming soon and still owns the least-squares derivation.
- `extended-kalman-filter` stays NLO-only, with the single prerequisite `kalman-recursive-least-squares`.
- The minimum-variance reading is the ME 132 skill `kalman-optimal-observer`. It is not in the NLO box.

## Skills
P = mathematical preliminary.


### NB1: NLO preliminaries I: spaces, eigen, SVD, inner products, norms (8 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `rn-important-subsets` | Key subsets of R^n | Vectors in R^n, matrices in R^{m x n}; orthant, unit simplex, lines, segments, hyperplanes, half-spaces as sets | (none) | P |
| `spectral-decomposition` | Spectral decomposition of symmetric matrices | Real eigenvalues, orthonormal eigenvectors, A = U D U^T, rebuilding A from eigenpairs, stretch geometry | `lin-algebra-review` | P |
| `positive-definite-matrices` | Positive (semi)definite matrices | PSD/PD definitions and eigenvalue tests, quadratic-form level sets as ellipses, indefinite case | `spectral-decomposition` | P |
| `singular-value-decomposition` | Singular value decomposition | Full and reduced SVD, link to eigenpairs of A^T A, rotate-stretch-rotate geometry, rank from singular values | `spectral-decomposition` | P |
| `rayleigh-quotient` | Rayleigh quotient and eigenvalue bounds | x^T A x / x^T x lies between lambda_min and lambda_max, attained at eigenvectors; trace/det as eigen sum/product | `spectral-decomposition` | P |
| `inner-products` | Inner products | Inner-product axioms, standard dot product, matrix (Frobenius) inner product, angles and orthogonality | `lin-algebra-review` | P |
| `vector-norms-lp` | Vector norms and l_p norms | Norm axioms; l1, l2, l_inf, general l_p; unit-ball shapes; norm equivalence in finite dimensions | `rn-important-subsets` | P |
| `cauchy-schwarz-inequality` | Cauchy-Schwarz inequality | |<x,y>| <= ||x|| ||y||, equality case, proof via a quadratic in t, uses (angle, triangle inequality) | `inner-products`, `vector-norms-lp` | P |

### NB2: NLO preliminaries II: matrix norms, topology, level sets, convex sets (6 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `induced-matrix-norms` | Induced matrix norms | Operator norm definition, ||Ax|| <= ||A|| ||x||, 1-norm = max column sum, inf-norm = max row sum, 2-norm = sigma_max | `vector-norms-lp`, `singular-value-decomposition` | P |
| `frobenius-schatten-norms` | Frobenius and Schatten norms | Frobenius norm as entrywise l2 and via singular values; Schatten p-norms (nuclear, spectral) | `vector-norms-lp`, `singular-value-decomposition` | P |
| `open-closed-sets` | Open and closed sets in R^n | Open/closed balls, interior points, open and closed sets, boundary and closure | `vector-norms-lp` | P |
| `compact-sets` | Bounded and compact sets | Boundedness, compact = closed and bounded in R^n, typical non-examples | `open-closed-sets` | P |
| `level-sets-contours` | Sublevel sets and contour sets | Lev(f,a) = {f <= a} and Con(f,a) = {f = a}; sketching them for simple f | `rn-important-subsets` | P |
| `convex-sets` | Convex sets | Segment definition, proofs for balls/half-spaces/affine sets, intersections stay convex, non-examples | `rn-important-subsets`, `vector-norms-lp` | P |

### NB3: NLO preliminaries III: multivariable derivatives and Taylor (9 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `directional-derivative` | Directional derivative | f'(x;d) as a one-sided limit along x + t d, computing it from the definition | `rn-important-subsets` | P |
| `gradient-partial-derivatives` | Partial derivatives and the gradient | Partials, gradient vector, f'(x;d) = grad f^T d, negative gradient as steepest local decrease | `directional-derivative` | P |
| `differentiability-multivariable` | Differentiability in several variables | Linear-approximation (little-o) definition, continuous partials suffice, how partials/directional/gradient/differentiable relate, counterexamples | `gradient-partial-derivatives` | P |
| `hessian-matrix` | Second derivatives and the Hessian | Second partials, Hessian matrix, symmetry of mixed partials for C^2 functions | `gradient-partial-derivatives` | P |
| `jacobian-chain-rule` | Jacobian and multivariable chain rule | Jacobian of vector-valued maps, chain rule as Jacobian products, gradient of a composition | `gradient-partial-derivatives` | P |
| `matrix-calculus-gradients` | Gradients of linear and quadratic forms | Index-notation derivation of grad/Hessian of c^T x, ||x||^2, b^T A x, x^T A x (non-symmetric A), ||Ax-b||^2 | `hessian-matrix`, `jacobian-chain-rule` | P |
| `fundamental-theorem-along-segment` | Fundamental theorem of calculus along a segment | f(y)-f(x) and grad f(y)-grad f(x) as integrals along the segment x + t(y-x) | `hessian-matrix` | P |
| `taylor-approximation-multivariable` | First- and second-order Taylor approximations | Linear and quadratic models of f near x with gradient and Hessian, error orders | `hessian-matrix` | P |
| `taylor-exact-mean-value` | Exact Taylor expansions and the mean value theorem | Mean value form and exact second-order expansion with an intermediate point; when approximations become bounds | `taylor-approximation-multivariable`, `fundamental-theorem-along-segment` | P |

### NB4: NLO preliminaries IV: convex functions and computing derivatives (AD) (9 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `convex-functions` | Convex functions | Chord (Jensen) definition, strict convexity, examples from the definition, norms and affine maps | `convex-sets` | P |
| `convexity-first-order` | First-order convexity condition | Tangent plane is a global under-estimator: f(y) >= f(x) + grad f(x)^T (y-x) | `convex-functions`, `gradient-partial-derivatives` | P |
| `convexity-second-order` | Second-order convexity test | Hessian PSD everywhere iff convex (on open convex sets); quadratics and least squares checks | `convexity-first-order`, `positive-definite-matrices`, `matrix-calculus-gradients`, `taylor-exact-mean-value` | P |
| `finite-difference-derivatives` | Finite-difference derivatives | Forward/central differences, truncation vs round-off error, choosing the step size | `gradient-partial-derivatives`, `taylor-approximation-multivariable` | P |
| `computational-graphs` | Computational graphs | Break f into elementary operations with helper variables, draw the graph; symbolic vs numeric vs automatic differentiation | `jacobian-chain-rule` | P |
| `ad-forward-mode` | Forward-mode automatic differentiation | Propagate tangents through the graph to get f'(x;d) = grad f^T d (Jacobian-vector products); cost per direction | `computational-graphs`, `directional-derivative` | P |
| `ad-reverse-mode` | Reverse-mode automatic differentiation | Backward adjoint sweep for the full gradient (vector-Jacobian products); cost, memory, choosing a mode | `computational-graphs` | P |
| `hessian-vector-products-ad` | Hessian-vector products with AD | Forward-over-reverse gives Hessian times d at gradient-like cost; full Hessian from n products | `ad-forward-mode`, `ad-reverse-mode`, `hessian-matrix` | P |
| `backprop-neural-network` | Backpropagation for a small neural network | Reverse-mode AD applied to a two-layer classifier loss; gradients of weights | `ad-reverse-mode` |  |

### NB5: Problem formulation and unconstrained optimality (10 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `optimization-problem-formulation` | Formulating an optimization problem | Decision variables, objective, feasible set, optimal value vs solution, max as min, constrained vs unconstrained, discrete vs continuous | `rn-important-subsets` |  |
| `graphical-2d-optimization` | Solving 2-D problems graphically | Overlay objective level lines on the feasible set, read off and then certify the optimum | `optimization-problem-formulation`, `level-sets-contours` |  |
| `optimization-problem-classes` | LP, QP, convex and nonlinear programs | Recognize LP/QP/convex/nonconvex forms, symmetrizing Q, why convexity makes problems tractable | `optimization-problem-formulation`, `convex-functions` |  |
| `local-global-minima` | Local and global minimizers | Definitions, strict vs non-strict, infimum vs minimum, argmin set | `optimization-problem-formulation`, `open-closed-sets` |  |
| `existence-of-minimizers` | Existence of minimizers | Weierstrass on compact feasible sets, coercivity on unbounded sets, non-attainment examples | `local-global-minima`, `compact-sets`, `level-sets-contours` |  |
| `first-order-optimality` | First-order necessary condition | Fermat's rule, grad f(x*) = 0 at interior local minima, stationary points, why assumptions matter | `local-global-minima`, `gradient-partial-derivatives` |  |
| `second-order-optimality` | Second-order optimality conditions | Necessary (Hessian PSD) and sufficient (Hessian PD) conditions, saddle points, inconclusive singular Hessian | `first-order-optimality`, `positive-definite-matrices`, `taylor-exact-mean-value` |  |
| `stationary-point-classification` | Classifying stationary points | Find all stationary points, classify as min/max/saddle, certify or refute global optimality | `second-order-optimality`, `existence-of-minimizers` |  |
| `convex-optimality-global` | Optimality for convex functions | Stationary implies global minimum for convex f; strict convexity gives uniqueness | `first-order-optimality`, `convexity-first-order` |  |
| `quadratic-function-minimization` | Minimizing quadratic functions | 1/2 x^T A x + b^T x + c: stationary points, PD gives unique minimizer, PSD/singular existence (b in range), coercivity | `matrix-calculus-gradients`, `second-order-optimality`, `convex-optimality-global` |  |

### NB6: Linear programming and the simplex method (7 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `lp-standard-form` | Linear programs and standard form | General vs standard form; slack/surplus variables, free-variable splitting, absolute values | `optimization-problem-classes` |  |
| `lp-graphical-solution` | Graphical LP solution and solution types | 2-D graphical solve; unique, non-unique, unbounded, infeasible cases | `lp-standard-form`, `graphical-2d-optimization` |  |
| `polyhedra-extreme-points` | Polyhedra and extreme points | Polyhedra are convex; extreme points, vertices, active constraints, basic feasible solutions and their equivalence | `convex-sets`, `lp-standard-form` |  |
| `basic-feasible-solutions` | Constructing basic feasible solutions | Pick a basis B, x_B = B^{-1} b; feasibility check; existence and optimality of extreme points | `polyhedra-extreme-points`, `lin-algebra-review` |  |
| `simplex-feasible-directions` | Basic directions, reduced costs, ratio test | Feasible basic direction, reduced cost vector, step size theta that keeps x >= 0 | `basic-feasible-solutions` |  |
| `simplex-method-iteration` | The simplex method | Full iteration: entering/leaving choice, basis change, optimality and unboundedness tests, pivot rule freedom | `simplex-feasible-directions` |  |
| `simplex-phase-one` | Finding an initial basic feasible solution | Auxiliary (phase I) problem with artificial variables | `simplex-method-iteration` |  |

### NB7: Lagrange multipliers, KKT, least squares (10 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `lagrangian-duality-lower-bounds` | Lagrangian lower bounds and the dual problem | Lagrangian, dual function as a family of lower bounds, dual problem, weak duality, min-max view | `first-order-optimality`, `quadratic-function-minimization` |  |
| `lagrange-multiplier-equality` | Lagrange multipliers for equality constraints | Lagrange multiplier theorem, regularity (independent constraint gradients), geometry, failure example | `first-order-optimality`, `jacobian-chain-rule`, `lin-algebra-review` |  |
| `kkt-conditions` | KKT conditions | Inequality constraints, complementary slackness, nonnegative multipliers, full KKT system | `lagrange-multiplier-equality`, `lagrangian-duality-lower-bounds` |  |
| `lp-duality-kkt` | LP duality from KKT | Lagrangian of a standard-form LP, KKT conditions, deriving the dual LP | `kkt-conditions`, `lp-standard-form` |  |
| `projection-affine-halfspace-kkt` | Projection onto affine sets and half-spaces | Closed-form projections onto {Ax=b} and {a^T x <= b} via KKT; rank condition on A | `kkt-conditions` |  |
| `linear-least-squares` | Linear least squares | Overdetermined Ax ~ b, normal equations, pseudoinverse, full column rank, link to quadratics | `quadratic-function-minimization`, `singular-value-decomposition` |  |
| `least-squares-data-fitting` | Least-squares data fitting | Regression with models linear in parameters (lines, polynomials), minimum data count | `linear-least-squares` |  |
| `nonlinear-least-squares` | Nonlinear least-squares problems | Sum of squared nonlinear residuals, residual Jacobian, examples | `linear-least-squares`, `jacobian-chain-rule` |  |
| `circle-fitting-least-squares` | Circle fitting by least squares | Nonlinear circle-fit formulation and its exact reformulation as a linear LS problem | `nonlinear-least-squares`, `least-squares-data-fitting` |  |
| `svm-quadratic-program` | Support vector machines as a QP | Margin, point-to-hyperplane distance, normalization, identifying the QP data | `optimization-problem-classes`, `quadratic-function-minimization` |  |

### NB8: Gradient methods: line search and convergence (11 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `descent-directions` | Descent directions | grad f^T d < 0, small steps decrease f (proof), d = -D grad f with D PD | `gradient-partial-derivatives`, `positive-definite-matrices`, `taylor-approximation-multivariable` |  |
| `descent-method-framework` | General descent methods | Iterate x+ = x + t d; choices of direction (steepest, scaled, Newton, Gauss-Newton), step size, stopping test | `descent-directions` |  |
| `convergence-rates` | Rates of convergence | Linear, superlinear, sublinear, quadratic definitions; example sequences; log-scale plots | `vector-norms-lp` |  |
| `exact-line-search-quadratic` | Exact line search on quadratics | Closed-form optimal step t = -g^T d / d^T A d along a descent direction | `descent-method-framework`, `quadratic-function-minimization` |  |
| `armijo-backtracking` | Armijo backtracking line search | Sufficient-decrease condition, backtracking loop, why a small step always qualifies | `descent-method-framework`, `taylor-approximation-multivariable` |  |
| `gradient-zigzag` | Zig-zagging of steepest descent | Successive steps orthogonal under exact line search; why ill-conditioning causes zig-zag | `exact-line-search-quadratic` |  |
| `condition-number-gradient-rate` | Condition number and gradient-descent rate | Kantorovich bound, linear rate ((kappa-1)/(kappa+1))^2 on quadratics, condition number | `exact-line-search-quadratic`, `convergence-rates`, `rayleigh-quotient` |  |
| `lipschitz-gradient` | Lipschitz-continuous gradients | L-smoothness, bound via Hessian operator norm, L for least squares | `induced-matrix-norms`, `fundamental-theorem-along-segment` |  |
| `descent-lemma` | The descent lemma | Quadratic upper bound f(y) <= f(x) + g^T(y-x) + L/2 ||y-x||^2, proof and picture | `lipschitz-gradient` |  |
| `sufficient-decrease-lemma` | Sufficient decrease lemma | Decrease per gradient step for t < 2/L; relation to Armijo parameter | `descent-lemma`, `armijo-backtracking` |  |
| `gradient-method-convergence` | Convergence of the gradient method | Gradient norm to zero, sublinear rate in general, effect of step-size rule | `sufficient-decrease-lemma`, `convergence-rates` |  |

### NB9: Gauss-Newton, incremental methods, Kalman filter, root finding (6 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `gauss-newton-method` | Gauss-Newton method | Linearize residuals, solve a linear LS subproblem each step, relation to Newton | `nonlinear-least-squares`, `descent-method-framework`, `taylor-approximation-multivariable` |  |
| `levenberg-marquardt` | Levenberg-Marquardt method | Damped Gauss-Newton, blending toward gradient descent, choosing the damping | `gauss-newton-method` |  |
| `incremental-gradient-methods` | Incremental gradient methods | Cycle through data blocks instead of full gradients; step-size behavior vs batch | `descent-method-framework`, `nonlinear-least-squares` |  |
| `kalman-recursive-least-squares` | Kalman filter as recursive least squares | Incremental Gauss-Newton on linear LS blocks yields the Kalman update recursion. `kalman` is already playable from ME 132 B8; this row still does not write it | `kalman`, `incremental-gradient-methods`, `linear-least-squares`, `gauss-newton-method` |  |
| `extended-kalman-filter` | Extended Kalman filter | Relinearize nonlinear measurement models at each block; localization-style use | `kalman-recursive-least-squares` |  |
| `newton-root-finding` | Newton's method for root finding | Solve g(x)=0 by repeated linearization, 1-D picture, starting-point sensitivity | `jacobian-chain-rule` |  |

### NB10: Newton and quasi-Newton (BFGS) (6 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `newton-method-optimization` | Newton's method for minimization | Step from the quadratic Taylor model, affine invariance, attraction to maxima/saddles | `newton-root-finding`, `descent-method-framework`, `taylor-approximation-multivariable` |  |
| `newton-local-quadratic-convergence` | Local quadratic convergence of Newton | Theorem and proof sketch with Lipschitz Hessian; basin of attraction | `newton-method-optimization`, `convergence-rates`, `lipschitz-gradient` |  |
| `newton-globalization` | Globalizing Newton's method | Damped Newton with line search, Hessian modifications (diagonal shifts) to force descent | `newton-method-optimization`, `armijo-backtracking`, `positive-definite-matrices` |  |
| `wolfe-conditions` | Wolfe line-search conditions | Sufficient decrease plus curvature condition; why it guarantees y^T s > 0 | `armijo-backtracking` |  |
| `quasi-newton-secant` | Quasi-Newton methods and the secant equation | Approximate the Hessian from gradient differences; secant equation from the FTC | `newton-method-optimization`, `fundamental-theorem-along-segment` |  |
| `bfgs-update` | BFGS update | BFGS formula (inverse form), positive definiteness under curvature condition, superlinear behavior | `quasi-newton-secant`, `wolfe-conditions` |  |

### NB11: Accelerated gradient methods (CG, heavy ball, Nesterov) (5 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `gram-schmidt-orthogonalization` | Gram-Schmidt orthogonalization | Orthogonalize independent vectors in any inner product, including x^T Q y | `inner-products`, `positive-definite-matrices` |  |
| `q-conjugate-directions` | Conjugate directions | Q-conjugacy, conjugate-direction method, finite termination on quadratics | `gram-schmidt-orthogonalization`, `exact-line-search-quadratic` |  |
| `conjugate-gradient-method` | Conjugate gradient method | CG recursion from gradients, cost, rate in terms of condition number, nonlinear CG | `q-conjugate-directions`, `condition-number-gradient-rate` |  |
| `heavy-ball-method` | Heavy-ball momentum | Momentum update from discretizing a damped second-order ODE, rate vs gradient descent | `gradient-method-convergence`, `condition-number-gradient-rate`, `finite-difference-derivatives` |  |
| `nesterov-accelerated-gradient` | Nesterov's accelerated gradient | Extrapolate-then-step scheme, difference from heavy ball, O(1/k^2) rate | `heavy-ball-method`, `descent-lemma` |  |

### NB12: Optimization over a convex set (8 skills)

| id | title | scope | prereqs | P |
|---|---|---|---|---|
| `optimality-over-convex-set` | Optimality over a convex set | Variational inequality grad f(x*)^T (x - x*) >= 0, local=global for convex f, nonconvex failure | `convex-sets`, `first-order-optimality`, `convex-optimality-global` |  |
| `projection-onto-convex-set` | Projection onto a convex set | Projection theorem, obtuse-angle characterization, projections onto lines, balls, boxes, half-spaces, other metrics | `optimality-over-convex-set`, `projection-affine-halfspace-kkt` |  |
| `gradient-projection-method` | Gradient projection method | Fixed-point stationarity x = P(x - t grad f), algorithm, step sizes, sufficient decrease and convergence | `projection-onto-convex-set`, `sufficient-decrease-lemma` |  |
| `scaled-gradient-projection` | Scaled gradient projection | Projection in a scaled metric; projected Newton as a special case | `gradient-projection-method`, `newton-method-optimization` |  |
| `affine-scaling-method` | Affine scaling for linear programs | LP as a sequence of scaled QPs, primal and dual affine scaling, link to Newton | `scaled-gradient-projection`, `lp-duality-kkt` |  |
| `primal-dual-interior-point` | Primal-dual interior-point methods | Perturbed KKT system for LP solved by Newton steps, central path idea | `affine-scaling-method`, `newton-root-finding` |  |
| `frank-wolfe-conditional-gradient` | Conditional gradient (Frank-Wolfe) method | Linear minimization oracle over l1 ball / simplex, step-size rules, sublinear convergence | `optimality-over-convex-set`, `polyhedra-extreme-points`, `descent-lemma` |  |
| `power-method-eigenvector` | Power method for the top eigenvector | Power iteration as conditional gradient on the Rayleigh quotient | `frank-wolfe-conditional-gradient`, `rayleigh-quotient` |  |
