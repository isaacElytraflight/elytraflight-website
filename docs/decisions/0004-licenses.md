# 4. Apache-2.0 for code, CC BY-SA 4.0 for content

Date: 2026-11-12
Status: accepted

Isaac chose these licenses on 2026-11-12. The files shipped in pull request 49. This record does not restate the license text.

## Context

The repository holds code and learning content, plus a few personal pages that are neither. Code needs a patent grant, which Apache-2.0 includes. Learning content should stay share-alike, in line with the open texts already listed as sources. MIT was set aside because it has no patent grant. AGPL-3.0 was the other code option and was not chosen. CC BY-NC-SA was the other content option and was not chosen, because the non-commercial term clashes with share-alike reuse of the sources.

## Decision

- Code, build scripts, tests, and the skill-tree shell (HTML, CSS, and JavaScript, excluding the learning-content JSON) are Apache-2.0. See [LICENSE](../../LICENSE).
- Questions, explanations, explainers, figures, and skill-graph data are CC BY-SA 4.0. See [LICENSE-CONTENT](../../LICENSE-CONTENT).
- [NOTICE](../../NOTICE) says which paths fall under which license, lists the third-party attributions, and notes that some AI-assisted text may not be copyrightable. The licenses cover whatever rights exist. They do not add rights the law does not grant.
- The CS 180 project pages and `public/profile.png` are excluded. They stay all rights reserved.
- The name and logo are not licensed. See [TRADEMARKS.md](../../TRADEMARKS.md).
- Isaac holds the rights now. A later assignment to a successor nonprofit is a separate step. The draft contributor agreement is written so that assignment can happen without collecting new grants. It is not in effect yet. See [docs/legal/CLA.md](../legal/CLA.md).

## Consequences

Do not relicense a path by adding a different header. A change of license is a new decision. Contributors do not commit the excluded personal pages under either open license.
