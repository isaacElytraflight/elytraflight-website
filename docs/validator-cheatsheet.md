# Validator cheat sheet

One page of bank, explainer, and batch rules. Read this instead of `skilltree/validate_bank.py`, `tools/skilltree-content/validate_bank.py`, `run_gates.py`, or any gate module. When a rule in those files changes, update this page in the same change. The schema gate is `skilltree/validate_bank.py`.

## Commands

```bash
python3 tools/skilltree-content/run_gates.py --batch <id> --summary
python3 tools/skilltree-content/dedupe_gate.py --batch <id>
python3 tools/skilltree-content/write_batch_docs.py --batch <id>
```

`--summary` prints the pass/fail table and, on a failure, the last 30 lines of the first failing gate. It also writes `docs/gates/<id>.json`. Add `--docs` to regenerate the changelog, brief, report, and `docs/content-versions.json` (that flag calls `write_batch_docs.py`). Copy `tools/skilltree-content/eecs127_eb1_gen.py` and `skilltree/verify_eecs127_eb1.py` for a new generator and verifier. Leave `nlo_nb2_gen.py`, `skilltree/verify_nlo_nb2.py`, and the `batch2a` / `batch2b` files as history. The verifier must not import the generator.

## Bank shape and ids

A bank is `skilltree/bank/<id>.json`: `skill_id` equal to the filename, integer `version` ≥ 1, and exactly 12 questions, 3 in each round 1–4. `Bank.save` writes that shape. Common fields are `id`, `round`, `type`, `prompt`, `explanation`, `figure`, `figure_alt`, `preview`, `version`. Any other key is an error.

| Error | Fix |
| --- | --- |
| `skill_id mismatch` / `skill id not in skills JSON` | Match the filename, and add the id to the skill graph first. |
| `expected 12 questions` / `round N has M questions, expected 3` | Three questions in each of rounds 1–4. |
| `version should be an int >= 1` | Set an integer version on the bank. |
| `<type> has unexpected field '…'` | Drop the key. It is not in the common set or that type's fields. |
| `empty prompt` / `empty explanation` | Both are non-empty strings. |
| `bad round` | `round` is 1, 2, 3, or 4. |
| `id does not match pattern/round` | Id is `<skill>-r<round>-q<n>`, and the round digit equals `round`. |
| `id set mismatch: missing …, extra …` | With no `retired_questions`, the twelve ids are exactly `q1`–`q3` in each round. |
| `retired question ids are not unique` / `retired question ids reused` | A retired id appears once, and a live question does not take it back. |
| `question ids dropped without retirement` | A removed canonical id stays on `retired_questions` with its old id. The replacement uses a new id (`q4`, `q5`, …). |
| `retired id does not match pattern/round` / `retired question needs version >= 1` | Retired objects use the same id pattern, matching `round`, and an integer version ≥ 1. |
| `duplicate id` | Ids are unique across live and retired questions. |

## Question types

`Bank` in `tools/skilltree-content/banklib.py` writes the fields. Deep types count toward the quota below.

| Type | Helper and fields | Error | Fix |
| --- | --- | --- | --- |
| `mc` | `mc(rnd, prompt, options, correct, …)`. Exactly 4 distinct option strings. `correct_index` is an int 0–3. | `mc needs exactly 4 non-empty string options` / `mc options are not distinct` / `bad correct_index` | Four different strings, index in range. |
| `numeric` | `num(...)` stores a finite nonzero answer (`g()`), a unit, and tolerance `0.02`. Tolerance must sit in `(0, 0.25]`. | `numeric answer must be a finite number` / `answer 0 with relative tolerance is ungradable` / `numeric needs a 'unit' string` / `numeric unit "1" is not a unit; use "(unitless)"` / `bad tolerance` | Nonzero finite answer. Unitless answers use `"(unitless)"`. |
| `symbolic` | `sym(rnd, prompt, answer, variables, explanation, alternates=...)`. `variables` is `{name: (min, max)}`, stored as `{name, min, max}`. Plain expression, not TeX. Default tolerance `1e-3`. | `symbolic needs a text answer` / `symbolic answer must be a plain expression, not TeX` / `symbolic needs a non-empty variables list` / `bad name` / `variable <n> is a function name` / `reserved for the constant e` / `needs min < max` / `symbolic answer does not use …` / `alternate repeats` / `did not parse` | Answer uses every name. Names match `[A-Za-z][A-Za-z0-9_]*` and are not `e`, `E`, or `sqrt`, `abs`, `exp`, `ln`, `log`, `sin`, `cos`, `tan`. `min < max`. Alternates are other plain forms of the same key. |
| `order` | `order(rnd, prompt, steps, …)`. `steps` is the correct order, 3–6 distinct strings. The quiz shuffles them. | `steps needs 3 to 6 non-empty strings` / `steps entries are not distinct` | Three to six different steps. |
| `error` | `find_error(..., steps, flaw, ..., reasons=, correct_reason=)`. `flaw` is the 0-based index of the one wrong step. | `bad flaw_index` / `flaw_index N is outside the steps` / `reasons needs 2 to 5` / `bad correct_reason` / `find_error with reasons needs correct_reason` | `flaw` indexes `steps`. Omit `reasons`, or pass 2–5 reasons and the index of the right one. |
| `multi` | `multi(..., options, correct, …)`. `correct` is every correct index. Grading is all-or-nothing. 3–6 options, at least one wrong. | `multi needs a non-empty correct_indices list` / `correct_indices has duplicates` / `correct_indices is outside the options` / `multi needs at least one wrong option` | Unique in-range indexes, and leave one option out. |

Math in `prompt` and `explanation` uses balanced, non-nested `\(` `\)` or `\[` `\]`. `$` is an error: `'$' math delimiter` / `nested/unclosed math delimiter` / `unbalanced math delimiter` / `unclosed math delimiter`. A letter reference (`option A`) is a warning: `explanation may refer to options by letter`. An explanation under 60 characters warns `very short explanation`.

The numeric gate runs `docs/batches/<id>.json` → `verifier`. Every numeric question needs a row in `check_expected`, and `finish(banks=...)` checks symbolic keys. `0 mismatches` is the pass line. `numeric question has no independent check`, `check has no numeric question`, `bank X != recomputed Y`, `alternate '…' is not equivalent to the key`, and `key is not finite on the declared ranges` mean the verifier and the bank disagree, or a sample range hits a singularity. Widen the range away from the pole, or fix the expression.

## Deep-type quota

At least 25% of the bank, `deep_quota(n) = ceil(3n/12)`, must be `symbolic`, `order`, `error`, or `multi`. A 12-question bank needs 3. `FAILED deep-quota gate` / `<id> deep-type quota: F deep question(s), need N in a 12-question bank` — add deep questions until the count meets the quota. `skilltree/deep_quota_grandfather.json` stays, and its `skills` array stays empty. Do not add ids. A wording-only edit does not take a bank off that list.

## Preview and leaves

Round 4 needs a non-empty `preview` list of other skill ids. Each id is a DAG descendant, or it is listed for this skill in `LEAF_PREVIEW_ALLOWED` inside `skilltree/validate_bank.py`. `preview only allowed in round 4` — drop `preview` on rounds 1–3. `round 4 needs non-empty 'preview' list` — add descendant ids. `preview '<id>' is not a later skill (no prereq path from …)` — point at a real later skill, or, when the skill has no dependents, add that skill and its follow-ons to `LEAF_PREVIEW_ALLOWED`. `preview points at the skill itself` and `preview id '…' not in skills JSON` — use a different live id. A conceptual follow-on warns and still passes: `preview '…' is a conceptual (non-DAG) follow-on`.

## Figures, bounds, and labels

`figure` is an SVG string starting with `<svg`, under 60,000 characters, with a `viewBox`, and a non-empty `figure_alt`. Forbidden: `script`, `foreignObject`, `image`, `iframe`, `object`, `embed`, `use`, `a`, `style`, `on*` attributes, `href`, and any URL. Errors: `figure must be an SVG string starting with <svg`, `figure <svg> needs a viewBox`, `figure contains forbidden <tag>`, `figure has href`, `figure too large`, `figure_alt without figure`. Missing alt is a warning: `figure without figure_alt`.

`figure-bounds` fails the batch when geometry leaves the viewBox (0.51 slack): line endpoints, circle and ellipse extents, rectangle corners, polyline and polygon points, path commands including arc bulge, and **text anchors** (labels). `figure line outside viewBox at (x, y) (+N more); viewBox …` — move the point or enlarge the viewBox. Axis titles drawn about 16px outside the plot need that padding inside the viewBox. The schema step only warns; the figure-bounds step fails.

Feedback figures (the `test-content` labeling checks) put `r` left of the summing junction and `e` to its right, mark the reference `+`, and mark the return `−` when the alt says subtract or `+` when it says added at the input. A disturbance is a second summer **after** the forward blocks, labeled `d`, with arrowheads at least 40px apart. Alt text names the block count it draws (`Two` / `Three`) and does not reveal the answer.

## Reference gate

Learner-facing text names no source. `FAILED reference gate: N hit(s)` then `<kind>: <file> <pointer>: <snippet>`. Kinds and the usual cause: `reader`; `textbook` or "the book"; `lecture` (`lecture 3`, `lecture notes`, `in lecture`); `slides` (`the slides`, `slide 3` — a bare "slides" is the motion verb); `week` / `chapter_num` / `section_num` (`week 2`, `chapter 3`, `section 1.2`, `fig. 1`, `eq. 2`); `homework` (`hw 3`, `discussion 1`); `professor` (professor, instructor, lecturer); `university` (Berkeley, Stanford, Caltech, UCLA, Graz, Princeton, MIT); `course_code` (`EE 105`, `EECS 127`, `ME 132`); `author` (Niknejad, Sedra, Åström); `further_reading`. Fix: delete the source words. Citations stay in `docs/sources.md`. A course name is allowed only as an exact `tab_title` on the allowlist (`Microelectronic Devices and Circuits (Berkeley EE 105)`, `Dynamic Systems and Feedback (Berkeley ME 132)`, `Feedback Systems (Generic)`, `Nonlinear Optimization (TU Graz)`, `Optimization Models in Engineering (Berkeley EECS 127)`). The bare string `EECS 127` fails. A professor or textbook still fails inside a selector label.

## KaTeX

`katex` renders every `\(` `\)` and `\[` `\]` in prompts, explanations, options, steps, reasons, units, and explainer `body_md` and `figure_alt`, in strict mode. `KaTeX: package not found` — run `bash tools/skilltree-content/agent_bootstrap.sh`. `KaTeX: rendered N math chunks, M errors` plus `<id> :: <tex> :: strict …` — the chunk is not KaTeX. Fix the command or the delimiter. Symbolic `answer` strings stay plain text, not TeX.

## Video

`video` on a skill is optional. When present it is `{url, title?, start?}`. `url` is `http(s)://youtube.com/watch?v=<11>` or `youtu.be/<11>` (optional `www.`). `start` is an integer ≥ 0. `title` is a non-empty string. `ERROR <id>: video.url must be a youtube.com/watch or youtu.be link` / `video id must be 11 characters` / `video.start must be a non-negative integer` / `video.title must be a non-empty string` / `video has unknown fields` — fix that field or omit `video`.

## Explainer, graph, and the other gates

`save_explainer(sid, title, sections)` writes `skilltree/explainers/<id>.json` with `id`, `title`, integer `version`, and sections. Each section has `heading` and `body_md`, plus optional `figure` (SVG) and `figure_alt`. Use five headings: The idea, Key equations, Worked example, Pitfalls, Where this leads. Authoring target is 250–500 words, at least one figure, and a worked example that uses none of that skill's quiz numbers. `missing explainer for <id>` / `<id> explainer is empty` — a playable skill has a non-empty explainer; a coming-soon skill has neither a bank nor an explainer.

`graph`: `cycle: …`, `<id> prerequisite <pre> is retired` / `does not resolve`, `<id> is not in any box`, `<id> is not inside a top-level box`. Every new skill has live prerequisites and sits in a chapter of a top-level course box. `domain` fails when an ME 132 or Feedback Systems skill's prerequisite closure contains an EE-only skill, or an application skill sits in the wrong chapter. `test-content` asserts 300 live skills, 283 banks, 283 explainers, and 17 coming-soon ids. A new playable skill updates those counts and the coming-soon list in `public/skilltree/tests/test-content.js`.

## Dedupe

`FAILED dedupe gate: N likely overlap(s)` then `<id> ~ <other> (name 0.xx, text 0.xx): <title>`. A hit is a name Jaccard ≥ 0.6 with two shared words, or a Jaccard ≥ 0.5 on name + synonyms (`synonyms` or `owns`) + summary with five shared words. Reuse the existing skill, split a neutral core from a domain application, or record the pair in `docs/dedupe-decisions.json` (`ids` of length 2, `resolution` of `reuse`, `split`, or `distinct`). `<id>: missing from the skill graph` — the batch lists an id the graph does not have.

## What `write_batch_docs.py` needs and produces

Input is `docs/batches/<id>.json`: `id`, `label`, `box`, `skills`, `areas`, `sources`, `notation`, `plan`, and `verifier` (the last is what `run_gates.py` runs). Optional `cores`. Every skill needs a bank, an explainer, and a graph row. `docs/gates/<id>.json` is optional; without it the report says `No gate summary yet`.

It writes, and overwrites, `docs/briefs/<id>.md`, `docs/reports/<id>.md`, `docs/CHANGELOG.md`, and `docs/content-versions.json`. The changelog and the version list are rebuilt from **every** `docs/batches/*.json`. Do not edit those four by hand. Versions are each question id, each retired id, and `<skill>#explainer`.
