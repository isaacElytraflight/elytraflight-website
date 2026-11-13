# 2. Question-alert thresholds

Date: 2026-11-12
Status: accepted

## Context

The admin page should surface questions that are too hard, too easy, beaten by a distractor, or flagged often. A handful of attempts is not enough to raise an alert. The numbers live in `skilltree/supabase/migrations/20261112160000_analytics.sql`, and the admin page prints the same defaults.

## Decision

Alerts use these cuts. Attempts and flags are counts. `p_correct` is correct answers divided by attempts.

| Alert | Rule |
|---|---|
| Too hard | at least 20 attempts and `p_correct` under 0.20 |
| Too easy | at least 20 attempts and `p_correct` over 0.95 |
| Distractor | at least 15 attempts and the most-picked wrong choice has more picks than the key |
| Many flags | 5 or more flags on that question |

"Many flags" is a count, not a flag rate. The flag rate is shown next to the count. It does not, by itself, raise the alert.

The dashboard returns these aggregates only when the signed-in user is on the admin allow-list. Everyone else gets nothing.

## Consequences

Changing a cut means changing the SQL and the copy that explains it, then Isaac applies the migration. Do not lower the attempt floors so that a few unlucky answers page the admin. Weekly triage is in the content SOP: fix and bump the version, or retire and replace.
