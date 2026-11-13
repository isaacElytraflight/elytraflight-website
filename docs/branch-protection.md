# Branch protection on main

Do not enable these settings yet. Cloud agents squash-merge their own pull requests when Bugbot is clean on that head. Required reviews on `main` would block that flow.

Turn this on before the first merge from an outside contributor. Until then, only Isaac and the agents he runs merge to `main`. Outside contributors do not merge their own pull requests, even while protection is off.

## Settings to enable

In the repository settings for `main`:

- Require a pull request before merging.
- Require one approving review. Isaac is the reviewer for outside contributors. Dismiss stale approvals when new commits are pushed.
- Require the status check `Cursor Bugbot` to pass. The check must be green on the commit that is merged.
- Require branches to be up to date before merging.
- Require conversation resolution.
- Allow squash merges. Turn off merge commits and rebase merges, so each pull request is one commit on `main`.
- Do not allow force pushes.
- Do not allow deletions.
- Restrict who can push to `main`. Outside contributors open pull requests. They do not push to `main`.
- Do not give outside contributors a bypass. Isaac can keep admin bypass for an urgent fix.

When the contributor license agreement in `docs/legal/CLA.md` is no longer a draft, also require the CLA Assistant status check. Leave that check off while the file still says DRAFT.

Secret scanning, push protection, and Dependabot are access settings. They are in [security-access-policy.md](security-access-policy.md), not in this branch rule.

## What stays true after protection is on

The self-merge rule in [CONTRIBUTING.md](../CONTRIBUTING.md) is for agents Isaac runs, and it depends on those agents being allowed to merge. If protection blocks them, Isaac merges agent pull requests himself, or he grants only those agents a bypass. Outside contributors still need his review.
