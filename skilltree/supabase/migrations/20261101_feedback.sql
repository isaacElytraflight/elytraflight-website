-- Elytraflight's Skill Tree feedback.
-- Run this whole script in the Supabase SQL editor. Do not use the service_role key in the app.
-- anon and authenticated may insert one row. They cannot select, update, or delete.

create table if not exists public.feedback (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  user_id uuid references auth.users (id) on delete set null,
  message text not null check (char_length(trim(message)) between 1 and 4000),
  category text check (category is null or category in ('bug', 'suggestion')),
  page text check (page is null or char_length(page) <= 2000),
  context jsonb,
  app_version text check (app_version is null or char_length(app_version) <= 40)
);

alter table public.feedback enable row level security;

revoke all on table public.feedback from anon, authenticated;
grant insert on table public.feedback to anon, authenticated;

drop policy if exists feedback_insert_own on public.feedback;
create policy feedback_insert_own
  on public.feedback
  for insert
  to anon, authenticated
  with check (
    (auth.uid() is null and user_id is null)
    or (user_id = auth.uid())
  );
