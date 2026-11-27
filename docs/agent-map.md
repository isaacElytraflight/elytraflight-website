# Skill Tree agent map

Read this file once before opening anything else. Then open only the path you need. Search with `bash tools/skilltree-content/find.sh <pattern> [path...]`. Do not grep the whole repo.

A content batch reads `docs/validator-cheatsheet.md` next. That page is the bank, explainer, and gate rules. Do not open `skilltree/validate_bank.py`, `tools/skilltree-content/validate_bank.py`, `run_gates.py`, `write_batch_docs.py`, or a gate module to learn a rule.

## UI

The live sidebar is the to-do list (`#todoBook`), the course scope picker, and the skill panel (`#panel`). Edit the three served files. No generator writes them.

| Path | What it is |
| --- | --- |
| `public/skilltree/index.html` | Served page. Sidebar markup: `#todoBook`, `#panel`. Edit in place. |
| `public/skilltree/skilltree.js` | Served app script: to-do sidebar, course scope picker, skill panel, quiz. Zoomed-out lights mode is painted by `#treeCanvas` (culled dots, edges, and course shapes); the DOM cards stay for hits and accessibility. Edit in place. |
| `public/skilltree/skilltree.css` | Served layout for the sidebar, tree, and panel. Edit in place. |
| `skilltree/app/template.html` | Offline demo page, including the `#panel` sidebar. Not what the site serves. |
| `skilltree/app/parts/p3_js_a.js` | Demo script, first half (storage, tree, quiz). The site does not load this file. |
| `skilltree/app/parts/p4_js_b.js` | Demo script, second half (stats, panel refresh, import). The site does not load this file. |
| `skilltree/app/parts/p1_css.html` | Demo CSS fragment for the same panel. |
| `skilltree/app/parts/p2_body.html` | Demo body, including the `#panel` aside. |
| `skilltree/app/parts/p2b_simcore.html` | Demo learning-plan simulator script. |
| `skilltree/app/parts/p1k_katex.html` | Demo KaTeX, inlined for offline math. |
| `skilltree/app/build_app.py` | Rebuilds the demo only. |

**Cache bust.** `index.html` loads `skilltree.js?v=<hash>` and `simcore.js?v=<hash>`. Any PR that changes one of those scripts must set its `?v=` to the first 8 hex characters of the file's sha256 (`sha256sum public/skilltree/skilltree.js | cut -c1-8`). Any PR that touches `index.html` must also run `node public/skilltree/tests/test-profile-fallbacks.mjs` (under a second).

`python3 skilltree/app/build_app.py` reads `skilltree/app/template.html` plus `skilltree/bank/*.json` and writes `skilltree/app/skilltree.html`. It does not write `public/skilltree/skilltree.js`.

`python3 skilltree/app/make_katex_part.py` rewrites `skilltree/app/parts/p1k_katex.html`.

## Data

| Path | What it is |
| --- | --- |
| `skilltree/ee105_skills_draft.json` | Skill graph: ids, names, prerequisites, optional `video`. |
| `skilltree/collections.json` | Course and topic boxes (`boxes[].id`, `title`, `skills`). |
| `skilltree/bank/<id>.json` | Question bank for one skill. This is the bank folder to edit. |
| `skilltree/explainers/<id>.json` | Explainer for one skill. |
| `skilltree/deep_quota_grandfather.json` | Grandfather list. The `skills` array stays empty. |

## Generators and gates

| Path | What it is |
| --- | --- |
| `tools/skilltree-content/build.py` | Writes the served content files. Run this after bank, explainer, or graph edits. |
| `tools/skilltree-content/run_gates.py` | One gate run. `--summary` prints the pass/fail table. |
| `tools/skilltree-content/banklib.py` | `Bank` helpers that write `skilltree/bank/<id>.json`. |
| `tools/skilltree-content/templates.py` | Figure templates. |
| `tools/skilltree-content/agent_bootstrap.sh` | Installs sympy, numpy, and KaTeX on a fresh VM. On a fresh VM this runs automatically via .cursor/environment.json; run_gates.py also self-bootstraps. Run it manually before any generator or test if needed. |
| `tools/skilltree-content/find.sh` | Capped search. Use this instead of a repo-wide grep. |
| `tools/skilltree-content/wait_bugbot.sh` | Blocks until the `Cursor Bugbot` check on a sha completes. Always pass the PR number. On `TOO_LARGE` (exit 3) do not merge; stop and report to the owner. |
| `tools/skilltree-content/video_gate.py` | Video URL gate. |
| `tools/skilltree-content/reference_gate.py` | No source names in learner-facing text. |
| `tools/skilltree-content/deep_quota_gate.py` | At least 25% deep-type questions. |
| `tools/skilltree-content/dedupe_gate.py` | Cross-skill name and summary overlap. |
| `tools/skilltree-content/*_gen.py` | One generator per content batch. Run `python3 tools/skilltree-content/<batch>_gen.py`. New batches copy `eecs127_eb1_gen.py`. |
| `skilltree/validate_bank.py` | Bank schema. Rules are in `docs/validator-cheatsheet.md`. Do not open this file to learn them. |
| `skilltree/validate_graph.py` | Graph cycles, orphans, box membership. |
| `skilltree/validator_domain.py` | Domain validator, including the deep-type quota. |
| `skilltree/figure_bounds.py` | Figure size gate. |
| `skilltree/verify_harness.py` | Shared numeric and symbolic checker. Batch verifiers are `skilltree/verify_<batch>.py`. New batches copy `skilltree/verify_eecs127_eb1.py`. |

New batches copy `tools/skilltree-content/eecs127_eb1_gen.py` and `skilltree/verify_eecs127_eb1.py`. Leave `nlo_nb2_gen.py`, `skilltree/verify_nlo_nb2.py`, and the `batch2a` / `batch2b` files as history. The verifier must not import the generator.

Always pass the pull request number to `wait_bugbot.sh`. On `TOO_LARGE` (exit 3) do not merge; stop and report to the owner.

Mechanical bank edits (small, predictable, scripted changes across existing banks, e.g. normalizing a field value, with no new questions or wording changes) skip Bugbot: merge with `--squash --admin --match-head-commit <sha>` once `run_gates.py --summary` passes and the PR is mergeable, and say "Bugbot skipped: mechanical bank edit" in the PR body. Bugbot still runs for code, tooling and new or reworded content.

## Docs

| Path | What it is |
| --- | --- |
| `docs/agent-map.md` | This map. Read it first. |
| `docs/validator-cheatsheet.md` | Bank, explainer, and gate rules, each with the error and the fix. Read this instead of validator or gate source. |
| `docs/skill-tree-content-SOP.md` | Full content rules. The SOP wins over the starter. |
| `docs/batch-starter.md` | Order of work for one batch, including the merge step. |
| `CONTRIBUTING.md` | Contributor setup and the agent merge rule. |

## Rebuild

Served content, after any edit under `skilltree/bank/`, `skilltree/explainers/`, `skilltree/ee105_skills_draft.json`, or `skilltree/collections.json`:

```bash
python3 tools/skilltree-content/build.py
```

That writes `public/skilltree/manifest.json`, `public/skilltree/skills.<hash>.json`, `public/skilltree/collections.<hash>.json`, `public/skilltree/banks/<id>.<hash>.json`, and `public/skilltree/explainers/<id>.<hash>.json`. Do not edit those files by hand. Do not grep `public/skilltree/banks/` or `public/skilltree/explainers/`. `.rgignore` hides them, including from `find.sh`.

The served UI (`public/skilltree/skilltree.js`, `index.html`, `skilltree.css`) is not a build product. Edit it directly.

The offline demo is the other rebuild: `python3 skilltree/app/build_app.py` writes `skilltree/app/skilltree.html`.
