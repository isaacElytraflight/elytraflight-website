# Content changelog

One entry per batch. Ids do not change. A content edit bumps that item's version. `docs/content-versions.json` stores `(id, version)` for the items in a shipped batch.

## B1 — 2026-11-06

Box: ME 132 and the Feedback Systems collection. Layer: the five skills whose prerequisites were already playable.

Shipped, each at bank version 1, each question at version 1:

- `fb-concepts`
- `laplace` (explainer version 2)
- `lin-algebra-review`
- `min-phase` (explainer version 2)
- `ode-model`

Explainers for `fb-concepts`, `lin-algebra-review`, and `ode-model` are version 1.

Edits after the first draft, which bumped the explainer version:

- `laplace` explainer. The growth condition on the integral was rewritten so it no longer tracked a source sentence. Version 2.
- `min-phase` explainer. The definition no longer says that a minimum-phase system has the smallest phase lag of all systems with the same magnitude curve. Version 2.

Dedupe: no new slug, no retirement, no split. Details are in `docs/me132-content-batches.md`.

Citations are in `docs/sources.md`. They are not on the skill records, because the panel prints `sources` as learner-facing further reading. No erratum was applied.

Domain-validator warnings: none. Nothing to waive.

The verbatim gate log is `docs/gates/b1-verbatim.log`. Zero failures. Four number flags were reviewed there and left as original problems.

Figure fixes after review. Each edited question is version 2:

- `min-phase-r4-q1`. The zero sat at x = 414, outside a 300-wide viewBox. The s-plane frame now scales so that zero and the real-axis break stay inside.
- `min-phase-r2-q2`. The pole at −8 was drawn at about x = −26 and clipped. The same frame puts it inside.
- `ode-model-r1-q2`. The stem says there is no spring. The figure draws the damper only.
- `ode-model-r2-q2`. The stem says there is no damper. The figure draws the spring only.
- `lin-algebra-review-r3-q3`, `lin-algebra-review-r4-q1`, and `lin-algebra-review-r4-q2`. Matrix figures take a list of entries, so a minus sign stays with its digit.

`skilltree/validate_bank.py` warns when a circle, line endpoint, text anchor, or path falls outside the viewBox. B1 has no such warnings. Older banks do, and those figures were left as they were.
