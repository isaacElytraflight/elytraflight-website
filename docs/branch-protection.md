# Branch protection on main

These settings can be on now. Agents Isaac runs merge as his GitHub account, and GitHub does not let an account approve its own pull request. So the ruleset gives the **Repository admin** role a bypass. Agents keep self-merging under the Bugbot rule in [CONTRIBUTING.md](../CONTRIBUTING.md), and outside contributors still need Isaac's approving review.

Outside contributors never merge their own pull requests.

Where to find it: repository **Settings → Rules → Rulesets → New ruleset → New branch ruleset**, targeting the default branch. Merge methods are in **Settings → General → Pull Requests**.

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
- Add **Repository admin** to the bypass list, so Isaac and the agents he runs can merge. Do not give outside contributors a bypass.

When the contributor license agreement in `docs/legal/CLA.md` is no longer a draft, also require the CLA Assistant status check. Leave that check off while the file still says DRAFT.

Secret scanning, push protection, and Dependabot are access settings. They are in [security-access-policy.md](security-access-policy.md), not in this branch rule.

## What stays true after protection is on

The self-merge rule in [CONTRIBUTING.md](../CONTRIBUTING.md) still applies to agents Isaac runs. They merge through the admin bypass, and only when Bugbot is clean on the exact head, unless Isaac says otherwise for a specific pull request. Outside contributors still need his review.
