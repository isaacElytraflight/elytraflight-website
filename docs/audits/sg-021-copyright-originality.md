# SG-021 copyright and originality audit

Audit date: 2026-11-13. Scope is every bank and explainer: 270 skills, 3240 questions, 270 explainers, 3510 learner items. Raw shingle logs and source texts were not committed.

## Coverage

The no-verbatim gate compared every learner item with the openly licensed sources named in `docs/sources.md`. Each source file was plain text, and each file ended with a boundary token so a shingle could not run from one file into the next.

| Source id | Text checked | Normalized tokens |
| --- | --- | --- |
| `lst-2020` | Murray, Notes on Linear Systems Theory, draft 30 Oct 2020 (CC BY-SA 4.0) | 26,155 words in the extract |
| `hefferon-linalg` | Hefferon, Linear Algebra, 4th ed. (GFDL or CC BY-SA 3.0 US), from `jheffero.w3.uvm.edu` | 200,050 words |
| `hefferon-answers` | Hefferon answer book, same site and license | 153,286 words |
| `wb-control` | Wikibooks Control Systems, full book (CC BY-SA), 65 content pages | 68,720 words |
| `wikibooks-linalg` | Wikibooks Linear Algebra, full book (CC BY-SA), 220 pages | 327,628 words |

The gate loaded those five files as 600,919 normalized tokens, 499,874 eight-grams, and 535,647 twelve-grams. The allowlist in `tools/skilltree-content/verbatim_allowlist.txt` contributed 0 eight-grams.

Copyrighted sources were not downloaded and were not part of the corpus. `docs/sources.md` marks them as scope only: Feedback Systems (Åström and Murray), Boyd and Vandenberghe, Nocedal and Wright, the ME 132 notes, the NLO notes, and the EE 105 reader.

Every docs batch was included, and so was every skill that is not in a docs batch:

- `me132-b1` through `me132-b8`
- `nlo-intro`, `nlo-nb1` through `nlo-nb12`
- EE 105 chapters 1–18, for skills that no docs batch lists
- `lti-mech` and `loop-margin-design`, which sit in ME 132 and are not in a docs batch

## Verbatim gate

Command shape: `python3 tools/skilltree-content/verbatim_gate.py` against the five source files, for all 270 skills. Ordering steps and find-the-error reasons are included. The gate is still not called from `run_gates.py`.

Result on all 3510 items: **0 fails**, 2346 pass, 1164 number flags. Every item had 0% eight-gram overlap and a longest source run of 0. Exit code 0.

The number flags are the gate's soft signal: three or more numbers from one source sentence appear in the same order in the item, and at least one number is outside {0, 1, 2}. Against books this large, small-integer triples such as (1, 2, 3) and (2, 2, 4) collide constantly. A pass over the flags whose numbers were distinctive (a number at least 10, a nontrivial decimal, or a longer run containing a number at least 6) left 140 items. The matching source sentences were exercise labels, matrix indexes, "20 log", coin problems, and similar collisions. The learner prompts for the suspicious tuples are different problems (a chord of a norm, a mass-spring, a lambda-tuning example). **No verbatim rewrite.**

## Internal duplicates

`tools/skilltree-content/internal_dup.py` finds a contiguous word run of at least 8 words that appears in two different skills. It compares prompts, choices, steps, reasons, explanations, figure alt text, and explainer sections. It does not edit content.

After the rewrites below, a recount of cross-skill runs was:

| Field | Pairs with a run of at least 8 words | Pairs with a run of at least 12 words |
| --- | --- | --- |
| prompt | 1491 | (included in the 150 below) |
| explanation | 127 | |
| explainer | 39 | |
| all three | | 150 |

Most prompt runs are the shared instruction frame ("put these steps in the order you would use", "one of these steps is false"). Figure-alt paragraphs that describe the same schematic (the MOS high-frequency model, the PN junction charge boxes) are the same picture described the same way, and they were left as they are. Parallel drills that change the numbers and keep the setup sentence were left as they are. Examples: the two projection questions with \(z = (3, 4)\) and \(z = (8, 4)\), and the graphical-optimization explanations that share a sentence about drawing the feasible set first.

These copies were not the shared frame. One side was rewritten. The concept, the key, and the difficulty stayed the same. Ids stayed the same. Each edited item's version is 2, except `step-specs-r2-q1`, which is 3 after a review fix of its distractor sentence.

| Item | Course | What was copied | Decision |
| --- | --- | --- | --- |
| `rn-important-subsets-r3-q3` | nlo-tugraz | Same stem and numbers as `convex-sets-r2-q2` (segment from (0, 0) to (8, 12) at \(t = 1/4\)) | Rewritten to the segment from (0, 0) to (5, 20) at \(t = 1/5\). Answer is now 4. |
| `step-specs-r1-q2` | me132 and am08 | Same percent-overshoot explanation as `second-order-sys-r2-q1` | Explanation rewritten. Answer stays 16.3034. |
| `step-specs-r4-q3` | me132 and am08 | Same stem and explanation as `second-order-sys-r4-q3` | Stem and explanation rewritten. Options and key stay. |
| `step-specs-r1-q3` | me132 and am08 | 27-word explanation run with `second-order-sys-r3-q1` | Explanation rewritten. Answer stays 2. |
| `step-specs-r2-q1` | me132 and am08 | 15-word explanation run with `second-order-sys-r2-q2` | Explanation rewritten. Answer stays 0.685552. Version 3 after a review fix of the distractor sentence. |
| `step-specs-r3-q1` | me132 and am08 | 16-word explanation run with `second-order-sys-r4-q1` | Explanation rewritten. Answer stays 9.47802. |
| `newton-method-optimization-r4-q2` | nlo-tugraz | 22-word explanation run with `gauss-newton-method-r4-q2` | Explanation rewritten. Answer stays −24. |
| `lp-graphical-solution` explainer | nlo-tugraz | 17-word sentence also in the `graphical-2d-optimization` explainer | That sentence rewritten. Explainer version is 2. |

`step-specs` is one skill in both the ME 132 box and the Feedback Systems box, so those five questions are one edit, counted once.

## Spot audit

Sample rule, seed `20261113`: in each group, draw one question from every skill, then fill at random until the sample is at least 10% of that group's questions. Groups are the 21 docs batches, the 18 EE 105 chapters for skills outside those batches, and the two unbatched ME 132 skills. That is 341 questions out of 3240.

The sampled prompts in ME 132, Feedback Systems, and the NLO batches do not use a textbook's worked-example numbers, problem sequence, or definition wording. Cruise-control numbers, matrix entries, and tuning constants do not match the distinctive examples those books are known for (the 1000 kg cruise car, Rosenbrock, the illumination problem). No rewrite came out of that part of the sample.

The EE 105 sample is different. Of the 341 questions, 35 name "the reader" or cite a numbered equation or section, and all 35 are in EE 105. A full-corpus search, not only the sample, found the same pattern:

| Signal in learner-facing text | Items |
| --- | --- |
| the word "reader" | 314 items, 93 skills, all in `ee105-ucb` |
| a section citation such as "Sec. 18.6" | 114 items |
| a table citation | 1 item (`led`, the reader's Table 6.1) |

Concrete failures, not just the word:

- `mos-struct` repeats a worked example's built-in voltage, including the reader's quoted −0.952 V.
- `opamp-fr` cites "Reader Eq. 18.15".
- `si-props` quotes the reader's conductivity table.
- `slew-r4-q1` points at "the ADA4891 (reader Sec. 18.6)".

The SOP forbids source names in stems, choices, explanations, explainers, figures, and alt text. These 314 items failed that rule on the tree this audit started from (`56e1d1f`). While this branch was open, main landed the source-agnostic pass (`cecdab7`, pull request 49), which removes those citations. After rebasing onto that commit, a scan of `skilltree/bank` and `skilltree/explainers` finds no "reader". This pull request does not reintroduce one. The 314-item rewrite is not left as a follow-up.

Equation-number strings also appeared in 204 items on that older tree. Many of those were the same reader citations. The reference gate now fails a numbered "Eq." or "Sec." in learner-facing text, and it is part of the batch gate below.

## Counts

| Course | Flagged | Fixed |
| --- | --- | --- |
| `ee105-ucb` | 314 reader-name items (93 skills) on `56e1d1f` | removed on main by pull request 49, before this branch was rebased; this change adds no EE 105 wording |
| `me132` | 5 copied `step-specs` items (shared skill) | 5 |
| `am08` | the same 5 `step-specs` items | 5 (same edits) |
| `nlo-tugraz` | 2 questions and 1 explainer | 2 questions and 1 explainer |

Verbatim fails fixed: 0. Unintentional cross-skill copies fixed: 8 items. Source-name failures found on the starting tree: 314, already removed on main.

## Gates

`python3 tools/skilltree-content/run_gates.py --batch <id> --docs` was run for every batch whose bank or explainer changed: `me132-b4`, `nlo-nb1`, `nlo-nb6`, and `nlo-nb10`. After the rebase onto main, that command also runs the source-reference gate, the deep-quota gate, and the dedupe gate. Schema, graph, and domain scan the whole tree. Each of those four runs passed build, schema, reference, graph, domain (0 unwaived warnings), deep-quota, dedupe, numeric (`0 mismatches`), figure-bounds (0 warnings on the batch), strict KaTeX, `test-content`, `test-merge`, `test-migrate`, and the Puppeteer suite (79 passed, 0 failed). `node public/skilltree/tests/test-brand.js` passed.

A post-edit shingle check of the rewritten skills and their twins (`step-specs`, `second-order-sys`, `rn-important-subsets`, `convex-sets`, `newton-method-optimization`, `gauss-newton-method`, `lp-graphical-solution`, `graphical-2d-optimization`) was 0 fails. The browser-suite timeout in `run_gates.py` is 480 seconds. The suite itself takes a little over 5 minutes here, and 300 seconds was cutting off a run that then passed.
