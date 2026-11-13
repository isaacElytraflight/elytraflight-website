# Access and secrets

Collaborators get the git repository. They do not get production hosting, the production Supabase project, or the `service_role` key. Isaac holds those. SQL changes are migration files under `skilltree/supabase/migrations/`. Isaac pastes a migration into the Supabase SQL editor himself. Nobody else runs it.

The anon key in `public/skilltree/config.js` is the public client key. It is not dashboard access and it is not the service role.

## Production data

- Do not put a `service_role` key in the repo, in a brief, in a pull request, or in a contributor's environment.
- Do not give a collaborator the production Supabase project. A collaborator who needs to exercise sign-in uses a separate dev project that Isaac creates and seeds with fake data.
- Analytics in the admin page are aggregates. The dashboard function returns them only for accounts on the admin allow-list. Collaborators are not on that list. Flag comments shown there are still learner text. Treat them as private.
- Anyone who will see real learner data signs a confidentiality addendum first. Isaac keeps that addendum. It is not in this repo yet.
- The privacy policy should say that a volunteer may be given a dev project with fake data, and that admin analytics are aggregated. There is no privacy-policy file in this repo. Isaac publishes that sentence.

## Progress rows

The app reads and writes `public.progress` for the signed-in user (`user_id`, `data`, `updated_at`). `skilltree/supabase/migrations/20261112_profiles.sql` reads that table from a security-definer function. Row-level security for the progress table itself is not applied yet.

`skilltree/supabase/migrations/20261113_progress_rls.sql` enables it and replaces policies on `public.progress` with own-row policies for the `authenticated` role. Isaac reads that file and applies it himself. Applying it changes production access. Do not run it from a contributor machine.

## Scanning and dependencies

- `.github/dependabot.yml` opens weekly update pull requests for the npm trees at the repo root, `public/skilltree/tests`, and `skilltree/app/tests`.
- Isaac turns on Dependabot security updates, secret scanning, and push protection in the repository settings. Those switches are not in git.
- Branch protection is documented in [branch-protection.md](branch-protection.md). Leave it off until the first outside contributor.

## Offboarding

When a collaborator leaves, Isaac does this promptly:

- Remove their GitHub access to this repository.
- Rotate the Supabase `service_role` key, the database password, and the anon key if it was ever shared outside `config.js`.
- Rotate Render deploy hooks and any personal access tokens they used.
- Confirm they have no copy of the production project.

The dev project's keys rotate the same way if that person had them.
