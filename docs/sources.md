# Source registry

Licenses were checked on 2026-11-06. A source that is not openly licensed is treated as fully copyrighted: it is read for scope and facts, and none of its wording, problems, parameter sets, or figures is stored in this repo.

Learner-facing text does not name a reader or a textbook. The skill panel renders `sources` as "Further reading", so B1 citations stay in this file and not on the skill records.

## Sources

| id | work | license | use |
|---|---|---|---|
| `fbs-v315` | Karl Johan Åström and Richard M. Murray, *Feedback Systems*, electronic edition v3.1.5 (2020-07-24), http://fbsbook.org. Princeton University Press hardback is a separate edition. | Personal-use manuscript. The front matter says it may not be reproduced without the publisher's consent. Not an open license. | Reference only. Chapter files were fetched locally for the shingle gate and were not committed. |
| `lst-2020` | Richard M. Murray, *Notes on Linear Systems Theory*, draft of 30 October 2020, supplement to the same course. | Creative Commons Attribution-ShareAlike 4.0. The notes' title page states the license. | Second canonical source for `laplace` and `lin-algebra-review`. |
| `hefferon-linalg` | Jim Hefferon, *Linear Algebra*, 4th edition. License page: https://hefferon.net/source.html | GNU Free Documentation License, or Creative Commons Attribution-ShareAlike 3.0 United States, at the reader's choice. | Second canonical source for `lin-algebra-review`. The historical `book.pdf` URL returned 404 on the day of this check, so that file is not in the shingle set. |
| `wb-control` | Wikibooks, *Control Systems* (Feedback Loops, System Modeling, Poles and Zeros, Transfer Functions). | Creative Commons Attribution-ShareAlike. | Second canonical source for `fb-concepts`, `ode-model`, and `min-phase`. |
| `me132-f26` | ME 132 Fall 2026 syllabus and notes. | Not on file. | Scope only. Not a wording source. |

## Section map for B1

The skill graph used to cite 2008 section numbers. The gate used the 2020 chapter files, which renumber some of those topics.

| skill | 2008 pointer that was on the skill | text actually compared |
|---|---|---|
| `fb-concepts` | §§1.1–1.4 | `fbs-intro` §§1.1–1.4, plus the Wikibooks feedback-loop page |
| `ode-model` | §2.1 | `fbs-modeling` chapter 3 (modeling with differential equations), plus the Wikibooks system-modeling page |
| `laplace` | §8.5 | `fbs-xfer` §9.3 (Laplace transforms), plus `lst-sig` |
| `lin-algebra-review` | appendix | `lst-lin` (the 2020 back matter is an index, not a linear-algebra appendix), with Hefferon recorded as the open textbook |
| `min-phase` | §9.4 | `fbs-loop` chapter 10 (minimum phase, all-pass, delay, inverse response). In the 2020 edition, §9.4 is block-diagram algebra, a later batch. |

## Errata

No separate errata list was in the v3.1.5 front matter or the back-matter index. Nothing in those files changes the B1 facts (element laws, transform rules, rank and eigenvalues, or the minimum-phase conditions). No erratum was applied.
