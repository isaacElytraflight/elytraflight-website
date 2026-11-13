-- Row-level security for learner progress.
-- Paste this whole script into the Supabase SQL editor. Do not put a service_role key in the app.
-- Isaac applies this himself after reading it. Applying it changes who can read production progress.
--
-- The progress table already exists. This script does not create it and does not change its columns.
-- The client selects and upserts user_id, data, and updated_at for the signed-in user.
-- After this script, authenticated may read and write only the row whose user_id is auth.uid().
-- anon cannot read or write the table. The table owner still bypasses row-level security,
-- which is why the service_role key stays with Isaac.
-- Security-definer functions owned by a bypass role, including profile_skills_completed, keep working.
-- Every existing policy on public.progress is dropped first so a broader policy cannot remain.

alter table public.progress enable row level security;

revoke all on table public.progress from public, anon, authenticated;
grant select, insert, update on table public.progress to authenticated;

do $$
declare
  pol record;
begin
  for pol in
    select policyname
    from pg_policies
    where schemaname = 'public' and tablename = 'progress'
  loop
    execute format('drop policy if exists %I on public.progress', pol.policyname);
  end loop;
end $$;

create policy progress_select_own
  on public.progress
  for select
  to authenticated
  using (user_id = auth.uid());

create policy progress_insert_own
  on public.progress
  for insert
  to authenticated
  with check (user_id = auth.uid());

create policy progress_update_own
  on public.progress
  for update
  to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());
