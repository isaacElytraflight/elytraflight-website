# ME 132 batch B2 step log

For a token review. Sizes are bytes. Token counts are characters divided by 4, rounded. A tool result that was summarized by the runner is counted as what came back, not the file on disk.

## 1. Confirm the base branch

Main does not have `run_gates.py`, `templates.py`, `write_batch_docs.py`, or the SOP. One `git fetch` plus `git ls-tree` (a few hundred bytes back). Branch `cursor/me132-b2-content-8dfd` was created from `cursor/me132-b1-content-8dfd` at `695b767`.

Why: the new PR has to carry the tooling, and main does not have it.

## 2. Read the five skill records

One Python snippet printed id, name, status, prerequisites, summary, and descendants for the five skills. About 2 KB back, ~500 tokens. The skills file was not loaded into the conversation.

Why: round-4 previews have to be real descendants, and `model-method` has none.

## 3. Read the checks the new skills must pass

- `docs/me132-content-batches.md` B2 section, ~1 KB.
- `skilltree/validate_bank.py` around `LEAF_PREVIEW_ALLOWED` and the preview rule, ~3 KB.
- `public/skilltree/tests/test-content.js` count assertions, ~2 KB. Grep, not the whole file.
- `public/skilltree/tests/test.js` lines 1340–1530, ~8 KB, ~2,000 tokens. This was the largest source read. The file is 113 KB; the rest was not read.
- `tools/skilltree-content/templates.py` function signatures only, ~1 KB.
- `tools/skilltree-content/write_batch_docs.py` `main`, ~2 KB. Found that `--batch` would drop B1 from `content-versions.json`.
- `tools/skilltree-content/me132_b1_gen.py` lines 1–80, the bank helper, ~3 KB.
- `tools/skilltree-content/katex_check.cjs` and `run_gates.py` control flow, ~3 KB together.
- Five skill objects in `ee105_skills_draft.json`, ~4 KB, so the `sources` arrays could be deleted without reformatting the file.

No textbook PDF and no extracted source text were opened.

## 4. Graph, tests, and the version writer

Edits, all small:

- Removed `status` and `sources` on the five skills (learner panel would have rendered the textbook names).
- Coming-soon count 51 → 46, bank count 119 → 124. The coming-soon exemplar in the browser test moved from `block-diagram` to `second-order-sys`.
- `model-method` added to `LEAF_PREVIEW_ALLOWED` with `linearization`, `sys-id`, `equilibria`.
- `write_batch_docs.py` now writes versions for every batch file even when `--batch` names one of them.
- Dedupe notes added under B2 in `docs/me132-content-batches.md`.

## 5. Write the generator

`tools/skilltree-content/me132_b2_gen.py`, 57 KB, about 14,000 tokens written. It calls `templates.py` (`block_diagram`, `step_response`, `splane`, `matrix_fig`, `mass_spring`). No new SVG strings.

First run: explainers at 505, 522, and 525 words, over the 500 cap. Two trim passes. A third run passed: 491, 434, 462, 500, 481 by the generator's counter. One option string was not a raw string (`SyntaxWarning` on `\(`); fixed in the same stretch, and the banks were regenerated.

The generator then wrote five banks (~126 KB) and five explainers (~23 KB). Those files were produced on disk, not re-read.

## 6. Independent verifier

`skilltree/verify_me132_b2.py`, 9 KB, about 2,200 tokens written. Closed-loop gains come from a 2-by-2 solve, step responses from RK4, proportional loops from a simulated plant, state-matrix entries from a short RK4 acceleration, equilibria from `numpy.linalg.solve` and eigenvalues from `numpy.linalg.eigvals`.

One run: 40 numeric checks, 0 mismatches, five worked-example strings found. No retry.

`figure_bounds.py` on the batch: 30 warnings, all on the same ten older skills as B1, none on B2.

## 7. Precheck before the gate

KaTeX on the ten new files: 414 chunks, 0 errors. Small output.

`validate_bank.py` with no quiet flag: exit 0, and the full warning list came back. That list is on the order of 20,000 tokens. Schema was already going to run inside `run_gates`, which prints one line. This was the most expensive read of the batch, and it did not change any file.

Graph and domain checks were a few lines each. Both passed.

## 8. The one gate

`python3 tools/skilltree-content/run_gates.py --batch me132-b2 --docs`

11 passed, 0 failed. Wall clock about 148 seconds, almost all Puppeteer. The text that came back was about 1 KB. Docs written by the script: changelog, brief, report, `content-versions.json` (batch field `all`, B1 items still present), `docs/gates/me132-b2.json`.

The report's word counter (it strips math harder than the generator lint) reads 427, 382, 440, 436, 389. Both counters sit inside 250–500. No second gate run.

## 9. Look at the figures and one quiz

A headless Chrome screenshot of every figure on one page hung (the page was 82 KB of SVG and very tall). That Chrome process was killed. A second pass used Puppeteer, one viewport per skill, plus a zoomed set of five figures, plus the live app.

Live app, `http://localhost:5000/skilltree/`:

- All five tiles are playable (not the coming-soon style) and have a start action.
- No further-reading block, and the panel text does not contain a textbook or author name.
- Round 1 of `block-diagram` shows the series blocks 6 and 5, the stem, and four shuffled choices. The stored correct index is still balanced; the page shuffles what the learner sees.

The zoomed feedback loop, the three-block series row, and the state matrix `[[0, 1], [-3, -1]]` sit inside the frame with the minus signs attached to their digits. The contact-sheet screenshots were the weak part: too small to judge, and the image descriptions cost more than the zoomed set.

## 10. This log and the PR

This file is the hand-written exception. The brief, the report, the changelog, and `content-versions.json` were not edited by hand.

## Ranked cost

1. **Generator source, about 14,000 tokens written.** The explanations are most of the 57 KB. A compact table (stem, answer, three distractors, one shared explanation pattern per skill) would cut that, at the cost of thinner wrong-answer text. Worth doing if the next batches stay this size.
2. **The schema precheck, about 20,000 tokens read.** `validate_bank.py` prints every existing warning. Skip it. `run_gates` already runs schema and keeps one line. If a local check is needed, add a `--quiet` that prints the error count only.
3. **Figure contact sheets, a few thousand tokens plus a hung browser.** Screenshot the quiz panel and two or three figures at readable size. Do not lay every figure on one page; Chrome's full-page capture stalls on it.
4. **`test.js` slice, about 2,000 tokens.** The three `block-diagram` lines came from grep. The 200-line read was only to see the assertion wording. Next time, replace from the grep hits.
5. **Explainer word-count retries, two extra generator runs.** Output was a few lines each, so the token cost was small, but the source was rewritten twice. Count words in the draft before the first save, and aim near 400 so the cap is not a surprise. The two counters disagree by about 60 words; pick one and call it from the generator.
6. **Verifier, about 2,200 tokens, one run.** Cheap relative to the generator. Keep it.

What did not get spent, and should stay that way: no textbook text, no shingle gate, no spot audit, no second Puppeteer gate, no read of the full skills JSON or the full `test.js`.
