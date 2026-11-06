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
- Subjects, courses, textbooks, chapters and paths are boxes (collections) holding ordered lists of skills. One skill can sit in many boxes, and boxes never change a skill. Courses and textbooks are independent top-level boxes, not nested in each other. Every skill sits in at least one top-level box.
- **Dedupe first (the key rule).** With flat ids, a duplicate splits progress and content. Search every box by id, name, synonyms and summary. Reuse what exists, add the new box membership and sources, and log each decision.

### Merging overlaps: neutral cores and domain applications
- **Core.** Any skill in 2+ top-level boxes, or one another box needs as a prerequisite, is a core. A core teaches the idea in domain-neutral terms. Its prerequisites are neutral math or systems skills only, never a skill that lives in just one domain's boxes. A learner in one course must never be forced through another course's domain material (e.g. LTI theory must not require RLC circuits).
- **Applications.** Domain-specific uses of a core get their own skills, with natural descriptive names (e.g. "Op-amp stability and compensation", "Stability margins in control loop design"), not literal "applications to X" labels. Each lists the core plus the domain skills as prerequisites and sits only in that domain's boxes.
- **When overlapping skills merge:** combine the knowledge that works across domains into one core, then split each domain's specifics into its own application skill.
- **Ids and progress.** The existing id stays with the neutral core, so progress stays attached. A merged-away id goes in the `retired` map with a progress migration. New application skills start at zero.
- **Banks and explainers.** Core banks use neutral notation (u, y, G(s), generic units, or several domains mixed so that none is required), with a full bank of neutral questions before shipping. Move domain questions to the application skill by question id, after reading each one, and log the moves. Core explainers may mention domain examples as "for instance", but no step may require domain knowledge.
- **Validator.** Warn when a prerequisite belongs only to top-level boxes that don't contain the skill, and when a skill sits in no box. Fix every warning, or waive it in the CHANGELOG with a reason.

## 2. Sources and copyright
- Ground each skill in two or more canonical sources: open textbooks, standard references, and course materials used with permission. Check each source's license page and record it in a source registry. Treat anything not openly licensed as fully copyrighted. Use course syllabi and notes for scope only.
- **Reference, not source.** Read the section, close it, and write from understanding. Never draft with the source open.
- **Paraphrase from understanding.** Read the section, close it, and write in your own words. Do not copy wording, problems, parameter sets, or figures. Standard equations and notation are facts and fine to use.
- **No borrowed problems.** Don't reuse exercises, worked examples, or their parameter sets. Invent scenarios, use fresh numbers, and frame questions differently.
- **Figures.** Never trace, redraw or screenshot a source figure. Generate every figure from our own code, data and labels.
- **No source names in learner-facing content.** Stems, choices, explanations, explainers, figures, alt text, and the skill panel do not name a reader or a textbook. Record citations in the authoring source registry only. Never quote the source, show its pages, or ship or link its PDF.
- **Shingle gate and spot audit, deferred.** The automated 8-word shingle gate and the manual 10% spot audit are not part of the batch pipeline. They wait for a later cleanup pass.
- **Errata.** Log source errata and use the correct version.

## 3. Notation
- Keep one constants and notation registry keyed by topic area. Areas are tags, not owners.
- When sources conflict, pick one convention and list the aliases.
- Writers read the areas their skills and prerequisites touch. New symbols are added in the same change.

## 4. Onboarding a subject
1. Collect 3–6 syllabi and 2–3 canonical texts, and check their licenses.
2. Draft the concepts, merge them into skills, and dedupe against the whole graph. Split shared skills into cores and applications (see 1).
3. Review granularity: split two-idea skills and merge trivial ones.
4. Set the depth. Wire prerequisites, then check for cycles, orphans and cross-domain prerequisite leaks.
5. Add registry areas and create the course, textbook and chapter boxes. Textbook material outside the course goes in the textbook box.
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
- Types, all auto-graded:
  - **Multiple choice:** 4 options, balanced positions, real-mistake distractors.
  - **Numeric:** non-zero answer, unit, relative tolerance (usually 1–3%).
  - **Later:** multi-select, symbolic expressions graded by evaluating at random points, and step ordering.
- Proofs and concepts become decisions: justify a step, find the flaw, pick a counterexample, trace the code.

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
- **Hard gates.** One command, `python3 tools/skilltree-content/run_gates.py --batch <id>`, runs:
  - the schema, graph, and domain validators
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
Every batch brief states:
- the box, layer and reserved skill ids
- the prerequisites, the registries to read, and the sources (with licenses) and sections
- the bank and explainer specs, and the core/application split
- the gates
- deliverables (content, generator, verifier, patches) and the generated report (counts, gate outputs, dedupe pointer)
- "do not publish"
