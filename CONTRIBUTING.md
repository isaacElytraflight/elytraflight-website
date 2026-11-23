# Contributing

Elytraflight's Skill Tree is the learning site at [elytraflight.com/skilltree/](https://www.elytraflight.com/skilltree/). The site shell is a Vite app. The skill tree itself is the static app in `public/skilltree/`, built from `skilltree/` and `tools/skilltree-content/`.

Open roadmap work is a GitHub issue per id, titled `[SG-xxx] <title>`. GitHub Issues are the source of truth for status. The old roadmap spreadsheet is a frozen archive, and [docs/roadmap.md](docs/roadmap.md) is background only.

## Writing content

Read [docs/skill-tree-content-SOP.md](docs/skill-tree-content-SOP.md) before you open a content pull request. It is the full rulebook. This section is the short version, and the SOP wins if the two ever disagree.

The workflow:

1. Pick an open Content issue, or open one with the Content form. A new course needs Isaac to accept its skill graph before any batch starts (SOP section 4).
2. Start from [docs/agent-map.md](docs/agent-map.md), then [docs/batch-starter.md](docs/batch-starter.md). The map is the path list. The starter gives the read order, the helper APIs, and where generated files go.
3. Write banks and explainers with the helpers in `tools/skilltree-content/banklib.py`. Do not hand-build question JSON, and do not hand-edit the hashed files the build writes.
4. Run `python3 tools/skilltree-content/run_gates.py --batch <id> --summary` once on the commit you intend to push. A content-only diff still runs every content gate (schema, the no-source-references gate, the 25% deep-type quota, dedupe, and the reference checks) and skips the full browser suite. The suite runs when any changed path is not content, including app or UI code (`public/skilltree/*.js`, `*.css`, `*.html`) or the app or build code. `--browser` forces the suite. `--no-browser` skips it. `--summary` prints a pass/fail table instead of the per-gate log.
5. Smoke-check in a browser on every pull request, content or UI: load the tree, open one changed skill, and take 1–2 screenshots.
6. Open the pull request with `Refs #N`, or `Closes #N` when it finishes the issue.

The hard rules:

- **No source references in learner text.** Stems, choices, explanations, explainers, captions, alt text, and names never mention a reader, a textbook, notes, slides, a professor, a university, a week or lecture number, or a source chapter. The reference gate fails the batch if they do. Only a course selector label (`tab_title`) may name a university and a course number.
- **Topic names only.** Boxes and sub-sections are named for their topic, never for a textbook, a chapter, a week, or a lecture.
- **At least 25% deep-type questions per bank.** Deep types are symbolic, ordering, find-the-error, and multi-select. The quota is `ceil(3n/12)`, so a 12-question bank needs 3. The deep-quota gate enforces it.
- **Dedupe against the whole graph.** Before adding a skill, check every course. Reuse an existing skill, split a neutral core from a domain application, or record the call in `docs/dedupe-decisions.json`.
- **Verified answers and figures.** Every numeric and symbolic answer is checked by the batch's independent verifier (0 mismatches). Figures come from `tools/skilltree-content/templates.py`, have alt text, and do not give the answer away.
- **Write it yourself.** No copied wording, problems, parameter sets, or figures. See [Copyright](#copyright).
- **Ids are permanent.** An edit bumps the item's version. Retire items instead of deleting them.

Notation is in [docs/notation.md](docs/notation.md). Past decisions are in [docs/decisions/](docs/decisions/).

## Setup

```bash
git clone https://github.com/isaacElytraflight/elytraflight-website.git
cd elytraflight-website
npm install
npm run dev
```

The marketing site is at [http://localhost:5173](http://localhost:5173).

The skill tree is static files. From the repo root:

```bash
npx serve public -l 5000
```

Open [http://localhost:5000/skilltree/](http://localhost:5000/skilltree/). UI tests expect that URL.

You need Node.js for the site and the skill-tree tests, and Python 3 with `numpy` and `sympy` for content gates. Puppeteer tests need Chrome or Chromium. Do not install a production credential. The anon key already in `public/skilltree/config.js` is the public client key.

`npm run build` typechecks the site, builds it, and writes the profile fallback pages. See [docs/decisions/0001-render-profile-rewrite.md](docs/decisions/0001-render-profile-rewrite.md).

## Tests and gates

Run the checks that cover what you changed.

Skill-tree unit tests, from the repo root:

```bash
node public/skilltree/tests/test-merge.js
node public/skilltree/tests/test-migrate.js
node public/skilltree/tests/test-content.js
node public/skilltree/tests/test-brand.js
node public/skilltree/tests/test-profile-fallbacks.mjs
python3 skilltree/test_deep_types.py
```

`test-brand.js` fails if the retired product name appears outside a fixed list of internal identifiers.

UI tests need the server on port 5000 and a browser:

```bash
cd public/skilltree/tests && npm install
cd ../../..
SKILLTREE_URL=http://localhost:5000/skilltree/ node public/skilltree/tests/test.js
```

A content batch has one gate command. Run it once on the commit you intend to push:

```bash
python3 tools/skilltree-content/run_gates.py --batch <id> --summary
```

Add `--summary` to print a pass/fail table instead of every gate's log line. When a gate fails, the table is followed by that first failure's last 30 lines. The gate file is the same either way.

That runs the build, schema, video URL, reference, graph, domain, deep-quota, dedupe, numeric verifier, figure bounds, strict KaTeX, `test-content`, `test-merge`, and `test-migrate`. The full Puppeteer suite is skipped when every path changed against `origin/main` is content (question banks, explainers, the skill graph, and their sources), and it runs otherwise. `--browser` and `--no-browser` override that, and the command prints why. There is no separate content CI workflow. This command is the gate. Add `--docs` only when that batch should regenerate the changelog, the brief, the report, and `docs/content-versions.json`. Every pull request, content or UI, still ends with one short browser smoke check: load the tree, open one changed skill, and take 1–2 screenshots.

`tools/skilltree-content/verbatim_gate.py` is the shingle check for copied wording. It is not part of `run_gates.py` yet, because the source texts stay outside the repo. The copyright rules below apply whether or not that command is running.

## Branches and pull requests

- Branch from `main`. One concern per pull request.
- Use the pull request template. Fill in how you checked the change.
- Do not commit scratch files, terminal logs, or screenshots.
- Do not commit secrets, learner data, or a file you are not allowed to redistribute.
- Content changes follow [docs/skill-tree-content-SOP.md](docs/skill-tree-content-SOP.md) and [docs/batch-starter.md](docs/batch-starter.md). Do not hand-edit the hashed files under `public/skilltree/banks/`, `public/skilltree/explainers/`, or `skills.<hash>.json`. The content build writes those.
- SQL goes in a new file under `skilltree/supabase/migrations/`. Isaac applies it. Do not run it against production.

## Bugbot and merging

Cursor Bugbot is the review on this repository. Do not start a paid reviewer.

Agents follow this in the same run that opened the pull request. Do not end the run while it is waiting.

- Read [docs/agent-map.md](docs/agent-map.md) before searching the repo. Search with `bash tools/skilltree-content/find.sh <pattern> [path...]`. Do not run a repo-wide grep. Do not re-read a file you just edited. Do not search the web unless the brief asks.
- Read gate output from `python3 tools/skilltree-content/run_gates.py --batch <id> --summary`. Add `--docs` when that batch should regenerate the changelog, the brief, the report, and `docs/content-versions.json`.
- After pushing, run `bash tools/skilltree-content/wait_bugbot.sh <head sha> <pr>` and wait until it prints a line. Always pass the PR number. It polls the `Cursor Bugbot` check every 30 seconds for up to 30 minutes, and each poll also checks issue comments for `BUGBOT_TOO_LARGE_TO_REVIEW`.
- Merge only when that line is `CLEAN` or `SKIPPED`, the gates passed, and the pull request is mergeable:

```bash
gh pr merge <n> --squash --admin --match-head-commit <sha>
```

- On `FINDINGS`, fix them, push, and run `wait_bugbot.sh` again. At most two fix rounds. If findings remain after the second fix round, or the line is `TIMEOUT` or `TOO_LARGE` (exit 3), do not merge. Stop and report to the owner.

`CLEAN` means the check finished with no findings. `SKIPPED` means the check completed as skipped. A check-run result that says the pull request is too large to review is `FINDINGS`, not `CLEAN` or `SKIPPED`. `TOO_LARGE` (exit 3) means Bugbot posted that the pull request is too large and created no check-run. Do not merge. Stop and report to the owner.

Mechanical bank edits (small, predictable, scripted changes across existing banks, e.g. normalizing a field value, with no new questions or wording changes) skip Bugbot: merge with `--squash --admin --match-head-commit <sha>` once `run_gates.py --summary` passes and the PR is mergeable, and say "Bugbot skipped: mechanical bank edit" in the PR body. Bugbot still runs for code, tooling and new or reworded content.

Agents Isaac runs may self-merge under that rule. Outside contributors do not merge their own pull requests. Isaac reviews those.

Branch protection on `main` uses a ruleset with an admin bypass, so agents Isaac runs can still self-merge. The settings are in [docs/branch-protection.md](docs/branch-protection.md). Do not change them yourself.

## Copyright

Write the contribution yourself. You may use facts, standard formulas, and a list of topic names. Do not copy or closely paraphrase a textbook, a reader, slides, homework, an exam, or a solution site. Do not commit those files, and do not reuse a real exam question or a real homework question.

An open source is allowed only when its license is compatible with this repo. Record the license in `docs/sources.md` and, for a skill, on the authoring `sources` array. Attribution stays in that metadata. It does not go in learner-facing text.

Learner-facing text does not name a reader, a textbook, lecture notes, slides, a professor or instructor, a university, a week, a lecture, a homework, or a source chapter. The only exception is a course selector label (`tab_title`), which may be `<Topic course title> (<University> <Course number>)`, or `<Topic> (Generic)` when there is no single source course. The published skill panel does not show a reader section or a further-reading list. Do not add them back.

If a model drafted or edited text, say so in the pull request. Some of that text may not be copyrightable. [NOTICE](NOTICE) covers whatever rights exist.

A takedown request goes to the contact Isaac publishes. Until that address is in the repo, open a GitHub issue and Isaac handles it. Registering a DMCA agent is his step, not a contributor's.

The content rules in full are in [docs/skill-tree-content-SOP.md](docs/skill-tree-content-SOP.md). Decisions are in [docs/decisions/](docs/decisions/).

## Access

Follow [docs/security-access-policy.md](docs/security-access-policy.md). Repository access is not production access. Never ask for or commit a `service_role` key.

## Contributor terms

Outbound code is Apache-2.0 ([LICENSE](LICENSE)). Learning content is CC BY-SA 4.0 ([LICENSE-CONTENT](LICENSE-CONTENT)). Neither license grants the name or the logo ([TRADEMARKS.md](TRADEMARKS.md)).

The inbound contributor agreement is [docs/legal/CLA.md](docs/legal/CLA.md). It is a **draft**. It is not in effect, and you are not asked to sign it yet. The plain-language notes and the CLA Assistant steps for Isaac are in [docs/legal/contributor-terms.md](docs/legal/contributor-terms.md).

## Issues and labels

Use the Bug, Feature, and Content forms. Labels are defined in [docs/labels.md](docs/labels.md) and [`.github/labels.yml`](.github/labels.yml). Apply one type, one area, one priority, and one size.
