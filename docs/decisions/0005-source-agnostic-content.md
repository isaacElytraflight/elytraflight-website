# 5. Learner-facing content does not name its sources

Date: 2026-11-13
Status: accepted

Recorded from pull request 49. The working rules are [docs/skill-tree-content-SOP.md](../skill-tree-content-SOP.md).

## Context

Skills are concepts, not chapters of a book. Naming a reader, a textbook, a professor, or a week in the product ties a skill to one course and copies the source's framing into the learner's view.

## Decision

Learner-facing text never names a reader, a textbook, lecture notes, slides, a professor or instructor, a university, a week, a lecture, a homework, or a source chapter. That covers stems, choices, explanations, explainers, captions, alt text, titles, descriptions, sub-section names, tooltips, and help text.

Sub-sections are topic names. A course box's `title` is the topic. The course selection tab is the only place that shows `tab_title`, in the form `<Topic course title> (<University> <Course number>)`, or `<Topic> (Generic)` when there is no single source course.

Sources stay in `docs/sources.md` and on the authoring `sources` array. The public build does not copy that array, and the skill panel does not render it. The panel does not show a reader section or a further-reading list.

A new course starts from a real recent syllabus, used for scope only. The wording is not copied. Isaac reviews the graph before content batches start.

Every new bank is at least 25% deep-type questions, and every new or changed skill is checked against the whole graph so the same idea is not added twice under another course.

## Consequences

`tools/skilltree-content/reference_gate.py` fails a banned reference. `deep_quota_gate.py` and `dedupe_gate.py` enforce the two quality bars. The shingle check in `verbatim_gate.py` is still deferred until source texts are available outside the repo. The writing rule is in force now.
