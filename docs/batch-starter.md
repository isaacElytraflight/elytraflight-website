# Content-batch starter

A short pack for an agent writing one content batch for Elytraflight's Skill Tree. The rules live in `docs/skill-tree-content-SOP.md`. This file is the order of work. The batch plan wins if a prompt disagrees with it.

## Cloud-agent environment, search, and merge

First step: `bash tools/skilltree-content/agent_bootstrap.sh`. It installs sympy and numpy when `import` fails, and KaTeX 0.16.47 under `/tmp/katex-home` when that copy is missing. It does not install npm packages at the repo root. `--box <box-id>` prints that box's skills and which of them are in the grandfather `skills` list (`none` when there are none).

The checkout is `/agent/repos/elytraflight-website`. Start with `git fetch origin main && git merge --ff-only origin/main`.

`skilltree/collections.json` is `{version, boxes:[{id, title, skills, ...}]}`. The grandfather key is `skills`. A skill goes in a course or subject box only if that course's materials explicitly teach it, so selecting a course shows only what the course teaches. Prerequisites outside the box are normal and expected, especially with vertically stacked courses; they show as starred outside prerequisites. Never copy a prerequisite into a box to make it self-contained. The full rule is in `docs/skill-tree-content-SOP.md`.

A missing sympy install fails the first generator or verifier on a fresh VM. Do not run `npm install` or `npm ci` at the repo root for content work. That is the Vite app. `katex_check.cjs` already searches `/tmp/katex-home/node_modules/katex`.

Do not commit `__pycache__` or `node_modules`. Before committing: `rm -rf skilltree/__pycache__ tools/skilltree-content/__pycache__`.

Search one file or a narrow glob. An unscoped grep of `tools/`, every `verify_*.py`, or `public/` returns tens of thousands of characters. The published catalog file name is in `public/skilltree/manifest.json`.

Iterate with the slice generator and verifier. On the candidate, run `python3 tools/skilltree-content/run_gates.py --batch <batch-id> --docs` once. See Gates for the `--docs` rewrite. A content-only pull request skips Puppeteer; one short smoke check is enough.

Wait for Bugbot in one loop on `gh api repos/isaacElytraflight/elytraflight-website/commits/$SHA/check-runs` until `Cursor Bugbot` completes. `mergeStateStatus` stays `BLOCKED` / `REVIEW_REQUIRED` because the `main` ruleset requires an approving review. When Bugbot is clean on that head and the pull request is mergeable, `gh pr merge <n> --squash --admin --match-head-commit <sha>`. Without `--admin` the merge fails. Recurring catches: invalid symbolic sample ranges, non-unique order chains, ambiguous wording, a prompt name that differs from the graded name (`K_p` vs `Kp`), and over-strong claims.

## Read in this order

Read each file once. Do not re-read a file you have already read.

1. The batch plan for this subject: `docs/nlo-content-batches.md` or `docs/me132-content-batches.md`. It is the skill list and the scope.
2. `docs/skill-tree-content-SOP.md`, including the brief template in section 12.
3. The newest brief in `docs/briefs/` for the shape of a generated brief. Briefs are generated. Do not edit them by hand.
4. `docs/notation.md` for every area the skills and their prerequisites touch. Add new symbols in the same change.
5. `docs/sources.md` for licenses. Sources are authoring metadata. Learner-facing text never names a reader, textbook, notes, slides, professor, university, week, lecture, homework, or a source chapter. A class name appears only in the course selection tab.
6. `tools/skilltree-content/banklib.py` and `skilltree/verify_harness.py`.
7. The previous batch's generator and verifier as a pattern only. The verifier must not import the generator.
8. The coming-soon records for this batch in `skilltree/ee105_skills_draft.json`, and the playable-count assertions in `public/skilltree/tests/test-content.js`.

## Helpers

`Bank` in `tools/skilltree-content/banklib.py` writes `skilltree/bank/<id>.json`.

- `mc`, `num`: four-option multiple choice, and a nonzero numeric answer with a unit and relative tolerance 0.02.
- `sym(rnd, prompt, answer, variables, explanation, alternates=...)`: symbolic. `variables` is `{name: (min, max)}`. The answer is a plain expression in those names, and it must use every name. `alternates` are equivalent forms. Do not use `e` or `E` as a variable, and do not use a function name (`sqrt`, `abs`, `exp`, `ln`, `log`, `sin`, `cos`, `tan`).
- `order(rnd, prompt, steps, explanation)`: steps in the correct order. The quiz shuffles them.
- `find_error(rnd, prompt, steps, flaw, explanation, reasons=..., correct_reason=...)`: `flaw` is the 0-based index of the one wrong step.
- `multi(rnd, prompt, options, correct, explanation)`: `correct` is every correct index. Grading is all-or-nothing.
- Round 4 needs `preview`, a list of descendant skill ids. A skill with no descendants needs an entry in `LEAF_PREVIEW_ALLOWED` inside `skilltree/validate_bank.py`.
- `save_explainer(sid, title, sections)` writes `skilltree/explainers/<id>.json`. Sections are idea, key equations, worked example, pitfalls, where this leads. 250–500 words, at least one figure, and the worked example uses none of that skill's quiz numbers.

`deep_quota(n)` is `ceil(3n/12)`, at least 25% rounded up. A 12-question bank needs at least 3 questions of type symbolic, order, error, or multi.

`skilltree/verify_harness.py` loads banks, checks every numeric answer against values computed in the batch verifier, checks every symbolic key with SymPy, and prints `0 mismatches`. Pass the loaded banks to `finish`. Answer formulas stay in `skilltree/verify_<batch>.py`. Do not import the generator.

Figures come from `tools/skilltree-content/templates.py`. Alt text does not reveal the answer. Aim for a figure on at least three quarters of the questions.

## Gates

While fixing, run the batch verifier and any check the edit can break:

```
python3 tools/skilltree-content/<batch>_gen.py
python3 skilltree/verify_<batch>.py
```

On the candidate you intend to push, run once:

```
python3 tools/skilltree-content/run_gates.py --batch <id> --docs
```

That command runs the build, schema, reference, graph, domain, deep-quota, dedupe, numeric verifier, figure bounds, strict KaTeX, test-content, test-merge, and test-migrate gates. A content-only diff still runs those gates, including schema validation, the no-source-references gate, the 25% deep-type quota, dedupe, and the reference checks, and skips the full Puppeteer suite. The suite runs when any changed path is not content, including app or UI code (`public/skilltree/*.js`, `*.css`, `*.html`) or the app or build code. `--browser` forces it. `--no-browser` skips it. The command prints the decision. There is no separate CI workflow for content; this runner is the gate. `--docs` regenerates the changelog, the brief, and the report, and rewrites all of `docs/content-versions.json` from every `docs/batches/*.json`. A large diff, including pre-existing `bjt-ss` duplicate rows, is expected and is not a regression. After a text-only review fix, run only the focused check for what changed, not the full gate run again. Run the full command again only if the later edit is not content-only.

## Generated files

`tools/skilltree-content/build.py` writes hashed files:

- `public/skilltree/banks/`
- `public/skilltree/explainers/`
- `public/skilltree/skills.<hash>.json`
- `public/skilltree/collections.<hash>.json`

Never grep or glob those directories, or the whole repo. `.rgignore` excludes them. Search the source banks in `skilltree/bank/` and `skilltree/explainers/`, and search specific source directories.

## Deep-type quota

At least 25% of the bank (`deep_quota(n)`) is symbolic, ordering, find-the-error, or multi-select. `deep_quota_gate.py` fails a bank under that line. SG-063 ([#55](https://github.com/isaacElytraflight/elytraflight-website/issues/55)) is complete and closed. `skilltree/deep_quota_grandfather.json` stays, and its `skills` list is empty. Keep the file and the gate. Do not add ids.

## Dedupe

`dedupe_gate.py` compares this batch's names, synonyms (`owns` or `synonyms`), and summaries with every other skill. A warning means the skill is probably already in the graph. Reuse it, split a neutral core from a domain application, or record the resolution in `docs/dedupe-decisions.json`. The batch report points at that decision.

## Review and merge

Use the repository's Cursor Bugbot review. Do not start a paid reviewer. The rule for people is in `CONTRIBUTING.md`.

After the pull request is open, wait for Bugbot on the latest head with one blocking command: a single shell loop that sleeps and checks until that check completes, with a generous timeout. Do not poll in separate commands.

If Bugbot reports findings, fix them, push, and wait again the same way. At most two fix rounds. A text-only fix does not need another full gate run.

Squash-merge into the base branch only when Bugbot is clean on that exact head sha and the pull request is mergeable. Pass that head sha. The repository deletes the head branch. Clean means the check finished with no findings. A result that says the pull request is too large to review is not clean.

If Bugbot says the pull request is too large to review, or findings are still open after the second review, do not merge. Stop and report them.

If the pull request is not mergeable because of conflicts, merge the base branch in, regenerate the generated files, re-run the gates, and wait for Bugbot again. That counts as a fix round.

Outside contributors do not self-merge. Branch protection on `main` uses a ruleset with an admin bypass (see `docs/branch-protection.md`), so this self-merge path keeps working.

## Efficiency

- Never grep or glob over `public/skilltree/banks`, `public/skilltree/explainers`, or the whole repo. Target specific source directories and files.
- Read each file once.
- Use the shared helpers. Do not paste a new bank writer or numeric-check loop.
- Focused tests while working, then one `run_gates.py --batch <id> --docs` at the end.
- Commit no scratch files, terminal logs, or screenshots from the run.
- One short browser smoke check on every pull request, content or UI: load the tree, open one changed skill, and take 1–2 screenshots. That check is not the full browser suite.
