# 3. The product name is Elytraflight's Skill Tree

Date: 2026-11-13
Status: accepted

Recorded from pull request 50.

## Context

The learning site needed one public name. Paths under `/skilltree/` were already live and stay.

## Decision

Learner-facing copy and repository text use Elytraflight's Skill Tree. The short form on the tight header button is Skill Tree. The front page line is "Master STEM skills, one node at a time." The page is a general STEM learning site.

The previous one-word product name is retired. `public/skilltree/tests/test-brand.js` fails if that name appears outside its allowlist of internal identifiers. Those identifiers stay so saved progress, the export file, and the admin check keep working. The allowlist is the source of the exact tokens. This record does not spell the retired name, because the brand test scans repository text.

## Consequences

New prose says Elytraflight's Skill Tree. Do not rename the allowlisted identifiers in a documentation change. Renaming them is an app change and needs a migration for saved exports. Neither the Apache license nor CC BY-SA 4.0 grants use of the name or the logo. See [TRADEMARKS.md](../../TRADEMARKS.md).
