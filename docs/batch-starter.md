# Content-batch starter

A short pack for an agent writing one content batch for Elytraflight's Skill Tree. The rules live in `docs/skill-tree-content-SOP.md`. This file is the order of work. The batch plan wins if a prompt disagrees with it.

Read `docs/agent-map.md` first. It is the list of exact paths. Do not search the repo to find a file that the map names.

## Reminders

- Recommended video: follow SOP section 14. Search YouTube with `python3 tools/skilltree-content/yt_search.py "<query>"`, not Google. Try at least three queries before giving up: the exact skill name, the plain-words concept, and the topic plus a trusted channel (3Blue1Brown, Steve Brunton, MIT OpenCourseWare, Stanford Online / Boyd, Khan Academy, Brian Douglas, Visually Explained, Gilbert Strang). A lecture segment is fine via `start`. If nothing fits, use a parent-concept video and label it in `title`. Hard rule: reject a video that mainly teaches a different skill in the tree, including when its title names that other skill. When the field is omitted, the pull request body lists the queries tried.
- Pedagogy: follow the SOP pedagogy section for clear wording and direct continuity. Do not restate it here.
- Ordering questions: adjacent steps must be real dependencies, not interchangeable; note the check in the batch self-review. See the SOP.
- Diagrams: only where that item needs one, and labeled for it; note which items got diagrams and why in the self-review. See the SOP.
- Reverse wiring: SOP section 4. A course box holds only skills that course teaches, and every onboarding also adds those skills as prerequisites of existing skills in other courses where the dependency is real.

## Cloud-agent environment, search, and merge

First step: `bash tools/skilltree-content/agent_bootstrap.sh`. It installs sympy and numpy when `import` fails, and KaTeX 0.16.47 under `/tmp/katex-home` when that copy is missing. It does not install npm packages at the repo root. `--box <box-id>` prints that box's skills and which of them are in the grandfather `skills` list (`none` when there are none).

The checkout is `/agent/repos/elytraflight-website`. Start with `git fetch origin main && git merge --ff-only origin/main`.

`skilltree/collections.json` is `{version, boxes:[{id, title, skills, ...}]}`. The grandfather key is `skills`. A skill goes in a course or subject box only if that course's materials explicitly teach it, so selecting a course shows only what the course teaches. Prerequisites outside the box are normal and expected, especially with vertically stacked courses; they show as starred outside prerequisites. Never copy a prerequisite into a box to make it self-contained. The full rule is in `docs/skill-tree-content-SOP.md`.

A missing sympy install fails the first generator or verifier on a fresh VM. Do not run `npm install` or `npm ci` at the repo root for content work. That is the Vite app. `katex_check.cjs` already searches `/tmp/katex-home/node_modules/katex`.

Do not commit `__pycache__` or `node_modules`. Before committing: `rm -rf skilltree/__pycache__ tools/skilltree-content/__pycache__`.

Search with `bash tools/skilltree-content/find.sh <pattern> [path...]`. With no paths it searches only `skilltree/`, `tools/skilltree-content/`, `docs/`, and `public/skilltree/`, and it prints at most 40 lines. Do not run a repo-wide grep. Do not search the web unless the brief asks. The published catalog file name is in `public/skilltree/manifest.json`.

Iterate with the slice generator and verifier. On the candidate, run `python3 tools/skilltree-content/run_gates.py --batch <batch-id> --docs --summary` once. See Gates for the `--docs` rewrite and the summary table. A content-only pull request skips Puppeteer; one short smoke check is enough.

After pushing, run `bash tools/skilltree-content/wait_bugbot.sh <head sha> <pr>` in that same run and do not end the run until it returns. `mergeStateStatus` stays `BLOCKED` / `REVIEW_REQUIRED` because the `main` ruleset requires an approving review. Merge only on `CLEAN` or `SKIPPED`, with the gates passing and the pull request mergeable: `gh pr merge <n> --squash --admin --match-head-commit <sha>`. Without `--admin` the merge fails. On `FINDINGS`, fix and wait again, at most two fix rounds. Recurring catches: invalid symbolic sample ranges, non-unique order chains, ambiguous wording, a prompt name that differs from the graded name (`K_p` vs `Kp`), and over-strong claims.

## Read in this order

Read `docs/agent-map.md` first. Then read each file below once. Do not re-read a file you have already read, and do not re-read a file you just edited. Do not search the web unless the brief asks.

1. `docs/agent-map.md`. Paths and rebuild commands.
2. The batch plan for this subject: `docs/nlo-content-batches.md` or `docs/me132-content-batches.md`. It is the skill list and the scope.
3. `docs/skill-tree-content-SOP.md`, including the brief template in section 12.
4. The newest brief in `docs/briefs/` for the shape of a generated brief. Briefs are generated. Do not edit them by hand.
5. `docs/notation.md` for every area the skills and their prerequisites touch. Add new symbols in the same change.
6. `docs/sources.md` for licenses. Sources are authoring metadata. Learner-facing text never names a reader, textbook, notes, slides, professor, university, week, lecture, homework, or a source chapter. A class name appears only in the course selection tab.
7. `tools/skilltree-content/banklib.py` and `skilltree/verify_harness.py`.
8. The previous batch's generator and verifier as a pattern only. The verifier must not import the generator.
9. The coming-soon records for this batch in `skilltree/ee105_skills_draft.json`, and the playable-count assertions in `public/skilltree/tests/test-content.js`.

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
python3 tools/skilltree-content/run_gates.py --batch <id> --docs --summary
```

`--summary` is the gate output to read. It runs the same gates, writes the same `docs/gates/<id>.json`, and prints a pass/fail table. When a gate fails, it also prints that first failure's last 30 lines. Omit `--summary` only when you need every gate's one-line detail.

That command runs the build, schema, video URL, reference, graph, domain, deep-quota, dedupe, numeric verifier, figure bounds, strict KaTeX, test-content, test-merge, and test-migrate gates. A content-only diff still runs those gates, including schema validation, the no-source-references gate, the 25% deep-type quota, dedupe, and the reference checks, and skips the full Puppeteer suite. The suite runs when any changed path is not content, including app or UI code (`public/skilltree/*.js`, `*.css`, `*.html`) or the app or build code. `--browser` forces it. `--no-browser` skips it. Without `--summary`, the command prints that decision. With `--summary`, a skipped suite is a `SKIP` row. There is no separate CI workflow for content; this runner is the gate. `--docs` regenerates the changelog, the brief, and the report, and rewrites all of `docs/content-versions.json` from every `docs/batches/*.json`. A large diff, including pre-existing `bjt-ss` duplicate rows, is expected and is not a regression. After a text-only review fix, run only the focused check for what changed, not the full gate run again. Run the full command again only if the later edit is not content-only.

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

After the pull request is open, wait in the same run. Do not end the run until this command returns:

```
bash tools/skilltree-content/wait_bugbot.sh <head sha> <pr>
```

It polls `gh api repos/isaacElytraflight/elytraflight-website/commits/<sha>/check-runs` every 30 seconds for up to 30 minutes, and prints one line: `CLEAN`, `FINDINGS`, `SKIPPED`, or `TIMEOUT`. With a pull request number it adds that check's title, the first 500 characters of its summary, and the inline review comments on that sha.

Merge only on `CLEAN` or `SKIPPED`, and only when the gates passed and the pull request is mergeable. Pass that head sha:

```
gh pr merge <n> --squash --admin --match-head-commit <sha>
```

The repository deletes the head branch. `CLEAN` means the check finished with no findings. `SKIPPED` means the check completed as skipped. A result that says the pull request is too large to review is `FINDINGS`, not `CLEAN` or `SKIPPED`.

On `FINDINGS`, fix them, push, and run `wait_bugbot.sh` again. At most two fix rounds. A text-only fix does not need another full gate run. If findings are still open after the second fix round, or the line is `TIMEOUT`, do not merge. Stop and report the result.

If the pull request is not mergeable because of conflicts, merge the base branch in, regenerate the generated files, re-run the gates, and wait for Bugbot again. That counts as a fix round.

Outside contributors do not self-merge. Branch protection on `main` uses a ruleset with an admin bypass (see `docs/branch-protection.md`), so this self-merge path keeps working.

## Efficiency

- Read `docs/agent-map.md` first. Do not re-read a file you just edited.
- Never grep or glob over `public/skilltree/banks`, `public/skilltree/explainers`, or the whole repo. Use `bash tools/skilltree-content/find.sh`.
- Do not search the web unless the brief asks.
- Use the shared helpers. Do not paste a new bank writer or numeric-check loop.
- Focused tests while working, then one `run_gates.py --batch <id> --docs --summary` at the end. Read that table, not a full gate log.
- After pushing, run `wait_bugbot.sh <head sha> <pr>` in the same run and do not end the run until it returns.
- Commit no scratch files, terminal logs, or screenshots from the run.
- One short browser smoke check on every pull request, content or UI: load the tree, open one changed skill, and take 1–2 screenshots. That check is not the full browser suite.
