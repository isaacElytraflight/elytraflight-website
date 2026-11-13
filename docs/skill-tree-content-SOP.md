---
name: mastery-quiz-content
description: >-
  Use when building or expanding a multi-subject mastery skill graph (any STEM
  subject): onboarding a subject, deduping skills, splitting shared skills into
  neutral cores and domain applications, copyright-safe content, writing quiz
  banks and explainers, verification gates, versioning, learner feedback, and
  shipping.
---
## 1. One global graph, many boxes
- A skill is a real-world concept worth about 20–40 minutes of learning. It exists independently of any course or subject.
- Ids are flat, global, permanent slugs (`kcl`, `bode`, `diode-iv-shockley`). Rename the display name, never the id.
- Name ids descriptively and specifically. Disambiguate by concept, never by course or subject. Avoid obscure acronyms. Check uniqueness, including near-matches, against the whole graph.
- Prerequisite edges connect any two skills. The graph must stay acyclic.
- Boxes are a course plus topic-named sub-sections. The course box's `title` is the topic, and that is what the tree, plan notes, and skill panel show. A class name such as EE 105 lives only in `tab_title`, and only the course selection tab renders it. Sub-sections are named by the topic, the way the Feedback Systems box is, never by a textbook, a source chapter, a week, or a lecture. One skill can sit in many boxes, and boxes never change a skill. Every skill sits in at least one top-level box.
- **Dedupe first (the key rule).** With flat ids, a duplicate splits progress and content. Search every box by id, name, synonyms (`owns` until a skill has a `synonyms` field), and summary. Reuse what exists, add the new box membership and sources, and log each decision.
- **Dedupe gate.** `tools/skilltree-content/dedupe_gate.py` compares each new or changed skill's name, synonyms, and summary with every other skill, using normalized token overlap. It is a hard gate in `run_gates.py`. A hit is a likely duplicate. Resolve it by reusing the existing skill, splitting a neutral core from a domain application, or recording that decision in `docs/dedupe-decisions.json` and naming it in the batch report. Do not record a decision to hide a real duplicate.

### Merging overlaps: neutral cores and domain applications
- **Core.** Any skill in 2+ top-level boxes, or one another box needs as a prerequisite, is a core. A core teaches the idea in domain-neutral terms. Its prerequisites are neutral math or systems skills only, never a skill that lives in just one domain's boxes. A learner in one course must never be forced through another course's domain material (e.g. LTI theory must not require RLC circuits).
- **Applications.** Domain-specific uses of a core get their own skills, with natural descriptive names (e.g. "Op-amp stability and compensation", "Stability margins in control loop design"), not literal "applications to X" labels. Each lists the core plus the domain skills as prerequisites and sits only in that domain's boxes.
- **When overlapping skills merge:** combine the knowledge that works across domains into one core, then split each domain's specifics into its own application skill.
- **Ids and progress.** The existing id stays with the neutral core, so progress stays attached. A merged-away id goes in the `retired` map with a progress migration. New application skills start at zero.
- **Banks and explainers.** Core banks use neutral notation (u, y, G(s), generic units, or several domains mixed so that none is required), with a full bank of neutral questions before shipping. Move domain questions to the application skill by question id, after reading each one, and log the moves. Core explainers may mention domain examples as "for instance", but no step may require domain knowledge.
- **Validator.** Warn when a prerequisite belongs only to top-level boxes that don't contain the skill, and when a skill sits in no box. Fix every warning, or waive it in the CHANGELOG with a reason.

## 2. Sources and copyright
- Ground each skill in two or more canonical sources: open textbooks, standard references, and course materials used with permission. Check each source's license page and record it in `docs/sources.md` and on the skill's `sources` array. That array is authoring metadata. The public build does not copy it, and the skill panel does not render it. Treat anything not openly licensed as fully copyrighted. Every onboarding follows a real recent syllabus or course schedule for scope. Use that schedule to decide which topics exist. Do not copy its wording.
- **Reference, not source.** Read the section, close it, and write from understanding. Never draft with the source open.
- **Paraphrase from understanding.** Read the section, close it, and write in your own words. Do not copy wording, problems, parameter sets, or figures. Standard equations and notation are facts and fine to use.
- **No borrowed problems.** Don't reuse exercises, worked examples, or their parameter sets. Invent scenarios, use fresh numbers, and frame questions differently.
- **Figures.** Never trace, redraw or screenshot a source figure. Generate every figure from our own code, data and labels.
- **No source names in learner-facing content.** Stems, choices, explanations, explainers, figure captions, alt text, skill titles, skill descriptions, chapter names, sub-section names, tooltips, and help text never name a reader, a textbook, lecture notes, slides, a professor or instructor, a university, a week number, a lecture number, a homework or discussion number, or a chapter or section number or name that comes from a source. Class names appear only in the course selection tab. Record citations in the source registry, not in a further-reading line. Never quote the source, show its pages, or ship or link its PDF.
- **Reference gate.** `tools/skilltree-content/reference_gate.py` scans that learner-facing text and fails on a banned reference. It is a hard gate in `run_gates.py`. Exceptions are the pattern notes in `tools/skilltree-content/reference_allowlist.txt`, plus `tab_title`, which the gate skips because it is the course tab label.
- **Shingle gate and spot audit, deferred.** The automated 8-word shingle gate and the manual 10% spot audit are not part of the batch pipeline. They wait for a later cleanup pass.
- **Errata.** Log source errata and use the correct version.

## 3. Notation
- Keep one constants and notation registry keyed by topic area. Areas are tags, not owners.
- When sources conflict, pick one convention and list the aliases.
- Writers read the areas their skills and prerequisites touch. New symbols are added in the same change.

## 4. Onboarding a subject
1. Start from a real recent syllabus or course schedule and use it for scope. Check the licenses of any canonical texts used beside it. Those texts stay in the source registry.
2. Draft the concepts, merge them into skills, and dedupe against the whole graph. Split shared skills into cores and applications (see 1).
3. Review granularity: split two-idea skills and merge trivial ones.
4. Set the depth. Wire prerequisites, then check for cycles, orphans and cross-domain prerequisite leaks.
5. Add registry areas and create the course box plus topic-named sub-section boxes. Do not name a box after a textbook, a source chapter, a week, or a lecture. A topic that sits outside one course still gets a topic title, as Feedback Systems does.
6. Optionally ship the tree first as "coming soon" skills with no banks, so the owner can review it.
7. Extend the figure library for the subject.
8. Get an expert review of the graph.
9. Order batches breadth-first.

## 5. Question banks
- Fixed structure, e.g. 4 rounds × 3 questions:
  - round 1 is practice
  - middle rounds are spaced mastery challenges (pass at 2 of 3; failing never lowers a level)
  - the final round asks application questions with preview links to descendant skills
- Explanations work the answer and say why tempting wrong answers fail. No option letters.
- Types, all auto-graded. Each one is simply correct or incorrect. Mastery thresholds do not change.
  - **Multiple choice:** 4 options, balanced positions, real-mistake distractors.
  - **Numeric:** non-zero answer, unit, relative tolerance (usually 1–3%).
  - **Symbolic:** the learner types an expression in the declared variables. The app grades it by evaluating that expression and the key at several random points inside the declared ranges, within a relative tolerance. The parser does not use eval. List equivalent forms in `alternates`. The verifier checks the key and those forms with SymPy. Variable names cannot be `e`, `E`, or a function name. `e` is the constant, and `2e-3` is scientific notation.
  - **Ordering:** shuffled steps of a derivation or procedure. The learner restores the correct order. All-or-nothing.
  - **Find-the-error:** a short derivation with exactly one flawed step. The learner picks that step, and a reason when reasons are given. All-or-nothing.
  - **Multi-select:** choose every correct option. All-or-nothing.
- **Deep-type quota (hard rule).** Every bank needs at least 25% deep-type questions, rounded up: `ceil(3n/12)`, which is `deep_quota(n)` in `banklib.py`. A 12-question bank needs 3. The deep types are the ones newer batches already use: symbolic, ordering, find-the-error, and multi-select. They are how a proof or a concept becomes a decision: justify a step, find the flaw, pick a counterexample, trace a procedure, or finish a multi-step application. `tools/skilltree-content/deep_quota_gate.py` fails a bank under that line. It is a hard gate in `run_gates.py`. The same check also runs inside the domain validator.
- Banks in `skilltree/deep_quota_grandfather.json` were written before the quota. They stay on that list until SG-063 rebuilds them. Do not add ids. A wording fix does not take a bank off the list. When SG-063, or an earlier full rewrite, replaces the bank with deep questions, remove its id.
- Author deep questions with `Bank.sym`, `Bank.order`, `Bank.find_error`, and `Bank.multi` in `tools/skilltree-content/banklib.py`. Do not hand-build those JSON fields.

## 6. Figures and math
- Figures on at least 50% of questions (aim for 75%) and in every explainer.
- Build them from `tools/skilltree-content/templates.py` (s-plane, block diagram, mass-spring-damper, matrix, Bode, step response, Nyquist, root locus, generic plot). The templates fit themselves to the viewBox. Extend that library for a shape it does not have.
- Sanitize SVG: well-formed, viewBox, size cap, no scripts, embeds, links, styles, handlers or URLs.
- Alt text on every figure. Neither the figure nor the alt text reveals the answer.
- Use one math delimiter convention with no `$`, and render in strict mode. Use raw strings in code.

## 7. Explainers
- Sections: idea, key equations, worked example, pitfalls, where this leads.
- 250–500 words, at least one figure, the registry's notation.
- Nothing from any quiz question appears in the worked example.

## 8. Versioning
- Ids are stable forever. Any content edit bumps the item's version, and history stores (id, version).
- Retire items; never delete them. A retired skill maps to its survivor, with a progress migration that keeps the higher tier and the latest practice time and is idempotent.
- Changelog per batch.

## 9. Throughput
- A coordinator splits the work into batches of 5–15 skills (one breadth-first layer of a box, prerequisites done) and reserves new ids up front.
- Parallel writers get a fixed brief and own disjoint files; shared-file changes come back as patches.
- **One fresh agent per batch.** Start each future batch in a new agent. Do not continue from another batch's transcript. Stay on subscription-included Grok-native models. Do not switch to Auto, a third-party model, paid fallback, extra reviewers, raised caps, or prepaid credits. If included usage cannot run the batch, stop and report that blocker.
- **Shared writers, thin verifiers.** Do not paste a new copy of the bank writer or the numeric-check loop. `tools/skilltree-content/banklib.py` writes the bank and explainer (B1 keeps its own word counter and copies `sym`, `order`, `find_error`, and `multi` off this class). `skilltree/verify_harness.py` loads banks, checks every numeric answer against values computed in the batch file, checks every symbolic key with SymPy, and prints the usual `0 mismatches` line. The command stays `python3 skilltree/verify_me132_bN.py`. Pass the loaded banks to `finish` so the symbolic check runs. Answer formulas stay in that batch file and must not be imported from the generator. RK4 and the proportional-loop simulation live in the harness because B2 and B3 both used them as an independent method.
- The repeated block is that writer and that check loop. B2 and B3 are not a shared 1117-line program: the longest identical run is the writer (about 60 lines). Do not rewrite an already shipped bank just to share code. B1's verifier stays as it is; its checks are functions, not a table of expected numbers.
- **Tests.** While fixing, run the batch verifier and any other check the edit can break. Run `python3 tools/skilltree-content/run_gates.py --batch <id> --docs` once on the candidate you intend to push. If a later edit can change schema, figures, math, or the browser suite, run the full command again. Do not report a gate result from an older commit.
- **Bugbot.** Use the repository's existing review. Do not start a paid reviewer. Fix valid findings, then allow one more review of that head. If valid findings remain after that second review, stop and report them. Do not merge to get past them.
- **Logs.** Do not commit scratch files, terminal logs, or screenshots from the run. Summarize in the report. Leave long command output in the tool log instead of pasting it. Do not poll CI or review; subscribe once and wait.
- **Hard gates.** One command, `python3 tools/skilltree-content/run_gates.py --batch <id>`, runs:
  - the schema, graph, and domain validators
  - the reference gate (`reference_gate.py`)
  - the deep-type quota (`deep_quota_gate.py`, at least 25%)
  - the dedupe gate (`dedupe_gate.py`)
  - the batch's independent numeric verifier (0 mismatches)
  - the figure-bounds check
  - strict math rendering
  - `test-content`, `test-merge`, `test-migrate`, and the Puppeteer suite
- The shingle gate and the 10% spot audit are deferred. They are not part of this command.
- The writer looks at rendered previews.

## 10. Learner feedback loop
- A flag button on every question: wrong, unclear, typo, figure, other.
- Track per-question p-correct, distractor choices and flag rate.
- Alert on extreme difficulty, a distractor beating the key, or a high flag rate.
- Triage weekly: fix and bump the version, or retire and replace.

## 11. Ship
- Build into hashed content files plus a manifest, and load them lazily.
- Content changes get their own pull requests. If merging deploys, check the live site afterwards.
- Never put secrets in briefs or repos.

## 12. Brief template
Start from `docs/batch-starter.md`. It is the read order, the helper APIs (`banklib` and `verify_harness`), the gate command, where generated files live, the deep-type quota, the review procedure, and the efficiency rules.
Every batch brief states:
- the box, layer and reserved skill ids
- the prerequisites, the registries to read, and the sources with their licenses. Section numbers stay in the source registry. They are not learner-facing text
- the bank and explainer specs, and the core/application split
- the deep-type quota: at least 25% (`deep_quota(n)`, `ceil(3n/12)`) among symbolic, ordering, find-the-error, and multi-select (`Bank.sym`, `Bank.order`, `Bank.find_error`, `Bank.multi` in `banklib.py`). The grandfather list in `skilltree/deep_quota_grandfather.json` is pending SG-063 and is not a reason to skip the quota on a new bank
- the dedupe check against the whole graph, and where a resolved overlap is recorded
- the gates, including the reference gate, the deep-quota gate, and the dedupe gate
- deliverables (content, generator, verifier, patches) and the generated report (counts, gate outputs, dedupe pointer)
- "do not publish"
