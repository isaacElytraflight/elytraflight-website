# Optimization models content batches

Skill graph for the course box `eecs127`. Isaac reviews this graph before any batch writes questions (SOP section 4, step 8). The 26 new skills stay coming soon: no banks and no explainers in this change. A skill is eligible for a content batch only when every prerequisite is already playable or sits in an earlier batch, or earlier in the same batch's listed order.

## Course summary

- **Course:** Optimization models in engineering. The selector label is `Optimization Models in Engineering (Berkeley EECS 127)`. The box title is the topic only.
- **Box:** `eecs127` ("Optimization models in engineering", top-level). Eleven topic sub-boxes. No sub-box is named for a week, a lecture, a chapter, or a text.
- **Scope:** a public topic list, used only to decide which skills exist. Wording in names and summaries is original. Recorded as `eecs127-scope` in `docs/sources.md`.
- **Totals:** 26 new skills, all coming soon. 44 existing skills are placed in the box because this course teaches them. 70 skills sit in the box. Three batches, EB1–EB3.

## Topic boxes

| box | title | skills |
|---|---|---|
| `eecs127/models` | Optimization models | `optimization-problem-formulation`, `linear-least-squares`, `local-global-minima` |
| `eecs127/linear-algebra` | Linear algebra | `lin-algebra-review`, `inner-products`, `vector-norms-lp`, `induced-matrix-norms`, `frobenius-schatten-norms`, `gram-schmidt-orthogonalization`, `qr-factorization`, `fundamental-subspaces`, `spectral-decomposition`, `positive-definite-matrices`, `rayleigh-quotient`, `singular-value-decomposition`, `principal-component-analysis`, `low-rank-approximation`, `block-matrix-identities` |
| `eecs127/derivatives` | Derivatives and optimality | `directional-derivative`, `gradient-partial-derivatives`, `jacobian-chain-rule`, `hessian-matrix`, `taylor-approximation-multivariable`, `taylor-exact-mean-value`, `matrix-calculus-gradients`, `first-order-optimality` |
| `eecs127/estimation` | Least squares and estimation | `least-squares-quadratic`, `least-squares-data-fitting`, `quadratic-function-minimization`, `least-squares-perturbation`, `ridge-regression`, `principal-components-regression`, `maximum-likelihood-estimation`, `maximum-a-posteriori-estimation` |
| `eecs127/convexity` | Convexity | `convex-sets`, `convex-functions`, `convexity-first-order`, `convexity-second-order`, `strong-convexity`, `optimization-problem-classes`, `convex-optimality-global`, `convex-reparameterization` |
| `eecs127/gradient-methods` | Gradient methods | `gradient-descent`, `stochastic-gradient-descent`, `lipschitz-gradient`, `descent-lemma`, `convergence-rates`, `gradient-method-convergence`, `projection-affine-halfspace-kkt`, `projection-onto-convex-set`, `gradient-projection-method` |
| `eecs127/duality` | Duality | `lagrange-multiplier-equality`, `lagrangian-duality-lower-bounds`, `strong-duality`, `kkt-conditions`, `convex-conjugate`, `conic-duality` |
| `eecs127/programs` | Convex programs | `lp-standard-form`, `quadratic-program`, `quadratically-constrained-quadratic-program`, `second-order-cone-program`, `semidefinite-program` |
| `eecs127/sparsity` | Sparse regularization | `lasso-regression`, `lasso-stationarity` |
| `eecs127/newton-methods` | Coordinate and Newton methods | `coordinate-descent`, `newton-method-optimization`, `equality-constrained-newton`, `barrier-interior-point` |
| `eecs127/applications` | Support vectors and linear quadratic regulators | `svm-quadratic-program`, `lqr` |

## Optional topics

Included, because each one is one skill of ordinary size:

- Block matrix identities, as `block-matrix-identities`.
- Matrix calculus, as the existing skill `matrix-calculus-gradients`.
- Semidefinite programs, as `semidefinite-program`.
- Conic duality, as `conic-duality`.
- The linear quadratic regulator, as the existing skill `lqr`. Its control prerequisites stay outside this box.
- Infimum versus minimum. It is already inside `local-global-minima` (local and global minimizers, and a minimum versus an infimum). No extra skill.

Folded into a neighbor, because a separate skill would be a second name for the same idea:

- A general squared penalty \(\lVert\Gamma x\rVert^2\) lives in `ridge-regression`. Ridge is the case \(\Gamma = \sqrt{\lambda}\, I\).
- The geometry of the absolute penalty (the diamond and its corners) lives in `lasso-regression`. The calculation is the later skill `lasso-stationarity`.
- The program hierarchy is the existing skill `optimization-problem-classes` plus the chain in `eecs127/programs`. `semidefinite-program` states that the earlier classes embed in it by a Schur complement.

Included as a lighter skill, because the existing skill is a heavier method this course does not teach:

- Barrier interior-point methods, as `barrier-interior-point`. `primal-dual-interior-point` stays in the nonlinear-optimization box. Its chain runs through affine scaling. The new skill does not use that chain. It is a prerequisite of the primal-dual skill, because the barrier method is the lighter interior-point idea and the primal-dual method is the follow-up.

## Reused skills

These already exist. They are placed here only because this course teaches them. Prerequisites that this course does not teach stay outside the box.

| id | where it sits here |
|---|---|
| `optimization-problem-formulation` | Optimization models |
| `linear-least-squares` | Optimization models |
| `local-global-minima` | Optimization models |
| `lin-algebra-review` | Linear algebra |
| `inner-products` | Linear algebra |
| `vector-norms-lp` | Linear algebra |
| `induced-matrix-norms` | Linear algebra |
| `frobenius-schatten-norms` | Linear algebra |
| `gram-schmidt-orthogonalization` | Linear algebra |
| `spectral-decomposition` | Linear algebra |
| `positive-definite-matrices` | Linear algebra |
| `rayleigh-quotient` | Linear algebra |
| `singular-value-decomposition` | Linear algebra |
| `directional-derivative` | Derivatives and optimality |
| `gradient-partial-derivatives` | Derivatives and optimality |
| `jacobian-chain-rule` | Derivatives and optimality |
| `hessian-matrix` | Derivatives and optimality |
| `taylor-approximation-multivariable` | Derivatives and optimality |
| `taylor-exact-mean-value` | Derivatives and optimality |
| `matrix-calculus-gradients` | Derivatives and optimality |
| `first-order-optimality` | Derivatives and optimality |
| `least-squares-quadratic` | Least squares and estimation |
| `least-squares-data-fitting` | Least squares and estimation |
| `quadratic-function-minimization` | Least squares and estimation |
| `convex-sets` | Convexity |
| `convex-functions` | Convexity |
| `convexity-first-order` | Convexity |
| `convexity-second-order` | Convexity |
| `optimization-problem-classes` | Convexity |
| `convex-optimality-global` | Convexity |
| `lipschitz-gradient` | Gradient methods |
| `descent-lemma` | Gradient methods |
| `convergence-rates` | Gradient methods |
| `gradient-method-convergence` | Gradient methods |
| `projection-affine-halfspace-kkt` | Gradient methods |
| `projection-onto-convex-set` | Gradient methods |
| `gradient-projection-method` | Gradient methods |
| `lagrange-multiplier-equality` | Duality |
| `lagrangian-duality-lower-bounds` | Duality |
| `kkt-conditions` | Duality |
| `lp-standard-form` | Convex programs |
| `newton-method-optimization` | Coordinate and Newton methods |
| `svm-quadratic-program` | Support vectors and linear quadratic regulators |
| `lqr` | Support vectors and linear quadratic regulators |

Outside prerequisites, not placed in the box, include `gaussian-random-vectors` (the noise model for maximum likelihood), `eigenvalues-diagonalization`, `second-order-optimality`, `rn-important-subsets`, `descent-method-framework` (the iteration template under gradient descent), `armijo-backtracking`, `sufficient-decrease-lemma` (the decrease bound uses backtracking, which this course does not teach), `fundamental-theorem-along-segment`, `optimality-over-convex-set`, and the state-feedback chain under `lqr`. Simplex, line search, quasi-Newton, automatic differentiation, and `primal-dual-interior-point` stay out.

## Content rule for all writers

Follow `docs/skill-tree-content-SOP.md` sections 1, 2, 5, 14, and 15. The course materials are scope only.

- No copying and no close paraphrase. Do not reuse exercises, worked examples, parameter sets, or figures.
- Learner-facing text names no reader, textbook, notes, slides, professor, university, week, lecture, homework, or source chapter. The selector label is the only place a university and a course number appear.
- Read `docs/notation.md` (area `optimization`) and `docs/sources.md` before writing. New symbols go in the registry in the same change.
- Banks: 4 rounds × 3 auto-graded questions. Round 1 practice. Rounds 2–3 mastery. Round 4 application, with a preview link to a descendant when one exists.
- **Deep-type quota.** At least 25% of each bank, `ceil(3n/12)` (`deep_quota` in `tools/skilltree-content/banklib.py`). A 12-question bank needs 3. Deep types are symbolic, ordering, find-the-error, and multi-select, written with `Bank.sym`, `Bank.order`, `Bank.find_error`, and `Bank.multi`. Do not hand-build those JSON fields. Do not add ids to `skilltree/deep_quota_grandfather.json`.
- **Wording and continuity (SOP section 15).** Define a term before use. One idea per sentence where possible. No trick phrasing. Use the registry's notation. Each explainer opens with a short bridge from its prerequisites, in the same notation. Early questions in a bank use the prerequisite idea, then extend it.
- **Ordering questions.** For every "put these steps in order" question, check each pair of adjacent steps. If two steps can be swapped and the sequence is still correct, the question is ambiguous. Reword so each step depends on the one before it, merge the parallel steps, or drop one. Never accept one of several valid orders. The batch self-review notes this check.
- **Diagrams.** Attach a figure only when that item needs it, or when it shows something the words cannot. Label axes, variables, and parts the text names. No decorative diagram. The self-review lists which items got a figure and why. SOP section 6's figure share applies to items that need a figure.
- **Video.** A recommended video is optional. The coming-soon skills that have one already store `video` on the skill. A later batch does not invent a replacement unless the existing link is wrong. If a new skill has no good video, omit the field. URLs are `youtube.com/watch?v=` or `youtu.be/` with one 11-character id. `start` is a non-negative integer of seconds. Titles must not name a lecture, a chapter number, a university, or a course.
- Explainers: idea, key equations, worked example, pitfalls, where this leads. 250–500 words, at least one figure when a figure is needed, and the worked example uses none of that skill's quiz numbers.
- Gates: `python3 tools/skilltree-content/run_gates.py --batch <id>`. Dedupe against the whole graph. Record a real overlap in `docs/dedupe-decisions.json`.

## Dedupe

Checked against the whole graph. New ids do not collide with live or retired ids.

- **Reused, not copied:** the 44 skills in the table above. `qr-factorization` is new because `gram-schmidt-orthogonalization` orthogonalizes vectors and does not factor a matrix. `low-rank-approximation` is new because `singular-value-decomposition` stops at the factorization. `lasso-regression` is new because `vector-norms-lp` draws the balls and does not state the penalized problem. `quadratic-program` is new because `optimization-problem-classes` only recognizes the class, `quadratic-function-minimization` is unconstrained, and `svm-quadratic-program` is the separator application.
- **Distinct, recorded:** `gradient-descent` and `stochastic-gradient-descent` in `docs/dedupe-decisions.json`. The full step is the prerequisite of the random step.
- **Kept separate, no edge from the new skill back to the old one:**
  - `stochastic-gradient-descent` versus `incremental-gradient-methods`. One draws a random subset. The other cycles through fixed blocks. The random step does not require the block skill. The block skill does list `gradient-descent`, because it compares a pass over blocks with the full gradient step.
  - `gradient-descent` versus `descent-method-framework` and versus `gradient-method-convergence`. The new skill is only the fixed-step choice: the direction opposite the gradient, and one positive length. The framework already separates direction, length, and the stopping test, so it is the prerequisite and it stays outside the box. The convergence skill is the later rate. `sufficient-decrease-lemma` states the decrease and now lists the method as a prerequisite. `armijo-backtracking` is not pulled into this box.
  - `ridge-regression` versus `linear-least-squares` and versus `levenberg-marquardt`. Ridge penalizes the coefficients of a fit. The damping shift on a Gauss-Newton step is a different matrix.
  - `strong-duality` versus `lagrangian-duality-lower-bounds`. The existing skill is the lower bound. The new skill is the zero gap.
  - `equality-constrained-newton` versus `newton-method-optimization` and versus `lagrange-multiplier-equality`. The new skill is the joint linear system. The other two stay prerequisites.
  - `principal-component-analysis` versus `principal-components-regression`. One chooses directions. The other regresses in those coordinates.
  - `lqr` versus `quadratic-function-minimization`. No new edge. The regulator stays the control skill it already is.
  - `condition-number-gradient-rate` is exact line search on a quadratic. It does not use the fixed-step method or the least-squares condition.
  - `lp-duality-kkt` derives the linear-program dual from KKT. It does not take the general zero-gap theorem as a prerequisite.

## Reverse wiring

These existing skills stay in their own boxes. Each new prerequisite is a skill this course adds, and the existing skill is the next thing a learner does with it. `heavy-ball-method`, `nesterov-accelerated-gradient`, and `gradient-method-convergence` already reach `gradient-descent` through `sufficient-decrease-lemma`, so they do not get a second edge.

| existing skill | added prerequisite | why |
|---|---|---|
| `sufficient-decrease-lemma` | `gradient-descent` | The lemma is the decrease of a gradient step. The step has to come first. |
| `incremental-gradient-methods` | `gradient-descent` | A pass over data blocks is compared with the full gradient step. |
| `gradient-projection-method` | `gradient-descent` | The projected iteration is that step, followed by a projection. |
| `svm-quadratic-program` | `quadratic-program` | The separator is built as a convex quadratic program, not only named as one. |
| `primal-dual-interior-point` | `barrier-interior-point` | The barrier method is the lighter interior-point idea. The primal-dual method follows it. |
| `mpc` | `quadratic-program` | A short look-ahead with a quadratic cost is a convex quadratic program. |
| `levenberg-marquardt` | `ridge-regression` | The damping term is a ridge shift on the Gauss-Newton normal equations. |
| `kalman-recursive-least-squares` | `maximum-a-posteriori-estimation` | The Kalman update is the posterior mode of a linear Gaussian model. |

## Skills

### EB1: Factorizations, sensitivity, ridge, likelihood (9 skills)

Every prerequisite is already playable, except `principal-components-regression`, which follows the two skills listed above it.

| id | title | scope | prereqs |
|---|---|---|---|
| `qr-factorization` | QR factorization | Orthonormal columns times an upper-triangular factor | `gram-schmidt-orthogonalization` |
| `fundamental-subspaces` | Four fundamental subspaces | Column space, row space, both nullspaces, and the orthogonality relations | `lin-algebra-review`, `inner-products` |
| `block-matrix-identities` | Block matrix identities | Block product, block inverse, Schur complement | `lin-algebra-review` |
| `principal-component-analysis` | Principal component analysis | Leading covariance eigenvectors, or leading right singular vectors of centered data | `spectral-decomposition`, `singular-value-decomposition` |
| `low-rank-approximation` | Low-rank approximation | Truncated singular values; nearest matrix of that rank | `singular-value-decomposition` |
| `least-squares-perturbation` | Perturbation of least squares | How changes in \(A\) and \(b\) move the solution | `linear-least-squares`, `singular-value-decomposition`, `induced-matrix-norms` |
| `ridge-regression` | Ridge regression | Squared penalty and the general penalty \(\lVert\Gamma x\rVert^2\); shifted normal equations | `least-squares-quadratic`, `positive-definite-matrices` |
| `principal-components-regression` | Principal components regression | Least squares in the leading principal-component coordinates | `principal-component-analysis`, `low-rank-approximation`, `least-squares-data-fitting` |
| `maximum-likelihood-estimation` | Maximum likelihood estimation | Gaussian residuals; equal variance recovers least squares | `least-squares-data-fitting`, `gaussian-random-vectors` |

### EB2: Convexity, gradient steps, duality, the lasso problem (8 skills)

| id | title | scope | prereqs |
|---|---|---|---|
| `convex-reparameterization` | Reparameterizing a convex problem | Change of variables, epigraph, moving a constraint into the objective | `optimization-problem-classes`, `convex-functions` |
| `strong-convexity` | Strong convexity | Quadratic lower model of curvature \(m\); Hessian at least \(m I\) | `convexity-second-order`, `positive-definite-matrices` |
| `gradient-descent` | Gradient descent | Fixed step opposite the gradient. Smoothness and the rate come later | `descent-method-framework` |
| `stochastic-gradient-descent` | Stochastic gradient descent | Unbiased random gradient, shrinking step | `gradient-descent` |
| `strong-duality` | Strong duality | Zero gap, and a relative-interior constraint qualification | `lagrangian-duality-lower-bounds` |
| `convex-conjugate` | Convex conjugates | Supremum of linear underestimators; dual functions | `convex-functions`, `lagrangian-duality-lower-bounds` |
| `maximum-a-posteriori-estimation` | Maximum a posteriori estimation | Gaussian prior; the mode is a ridge fit | `maximum-likelihood-estimation`, `ridge-regression` |
| `lasso-regression` | Lasso regression | Absolute penalty, and sparsity at the corners of its unit ball | `ridge-regression`, `vector-norms-lp` |

### EB3: Cone programs, lasso stationarity, coordinate and Newton steps (9 skills)

Listed so each skill's new prerequisites appear earlier in this batch or in EB1–EB2.

| id | title | scope | prereqs |
|---|---|---|---|
| `quadratic-program` | Convex quadratic programs | Quadratic objective, affine constraints, positive semidefinite Hessian | `optimization-problem-classes`, `quadratic-function-minimization` |
| `quadratically-constrained-quadratic-program` | Quadratically constrained quadratic programs | Quadratic inequalities that stay convex | `quadratic-program` |
| `second-order-cone-program` | Second-order cone programs | A Euclidean norm of an affine map, bounded by an affine function | `quadratically-constrained-quadratic-program`, `vector-norms-lp` |
| `semidefinite-program` | Semidefinite programs | A positive-semidefinite affine matrix; earlier classes embed by a Schur complement | `second-order-cone-program`, `positive-definite-matrices`, `block-matrix-identities` |
| `conic-duality` | Conic duality | Dual cone, and the dual of a cone program | `strong-duality`, `second-order-cone-program` |
| `lasso-stationarity` | Lasso stationarity and soft thresholding | Subdifferential stationarity. For orthonormal columns the map is soft thresholding at \(\lambda/2\), matching \(\lVert Ax-b\rVert^2 + \lambda \lVert x\rVert_1\) with no leading \(1/2\) | `lasso-regression`, `convex-optimality-global` |
| `coordinate-descent` | Coordinate descent | One coordinate at a time; one pass on a separable absolute penalty | `gradient-descent`, `lasso-regression` |
| `equality-constrained-newton` | Newton's method with equality constraints | One linear system in the step and the multiplier | `newton-method-optimization`, `lagrange-multiplier-equality` |
| `barrier-interior-point` | Barrier interior-point method | Log barrier, weight sent to zero, Newton on the equality-constrained barrier problem | `equality-constrained-newton`, `kkt-conditions` |

Each bank in EB1–EB3 needs at least 25% deep questions. For the usual 12-question bank that is 3, among symbolic, ordering, find-the-error, and multi-select.
