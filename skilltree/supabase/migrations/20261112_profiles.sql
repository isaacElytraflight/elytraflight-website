-- Elytraflight's Skill Tree profiles (SG-025 through SG-028).
-- Paste this whole script into the Supabase SQL editor. Do not put a service_role key in the app.
--
-- profiles holds the public identity. "Skills completed" is not a column the client can set.
-- public.profile_skills_completed counts Mastered skills (tier >= 4) from that account's
-- synced progress JSON. Public pages and the leaderboard read that count through the
-- functions below. Until this script has been run, the app keeps the profile page local
-- and hides the leaderboard.

create table if not exists public.profiles (
  user_id uuid primary key references auth.users (id) on delete cascade,
  username text not null,
  bio text not null default '',
  is_public boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint profiles_username_lower check (username = lower(username)),
  constraint profiles_username_format check (username ~ '^[a-z0-9](?:[a-z0-9_-]{1,30}[a-z0-9])$'),
  constraint profiles_username_reserved check (username not in (
    'admin', 'api', 'me', 'null', 'profile', 'profiles', 'settings', 'skilltree', 'undefined'
  )),
  constraint profiles_bio_len check (char_length(bio) <= 500)
);

create unique index if not exists profiles_username_key on public.profiles (username);

alter table public.profiles enable row level security;

revoke all on table public.profiles from anon, authenticated;
grant select on table public.profiles to anon, authenticated;
grant insert, update on table public.profiles to authenticated;

drop policy if exists profiles_select_own on public.profiles;
create policy profiles_select_own
  on public.profiles
  for select
  to authenticated
  using (user_id = auth.uid());

drop policy if exists profiles_select_public on public.profiles;
create policy profiles_select_public
  on public.profiles
  for select
  to anon, authenticated
  using (is_public = true);

drop policy if exists profiles_insert_own on public.profiles;
create policy profiles_insert_own
  on public.profiles
  for insert
  to authenticated
  with check (user_id = auth.uid());

drop policy if exists profiles_update_own on public.profiles;
create policy profiles_update_own
  on public.profiles
  for update
  to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- Count Mastered skills from the progress row. Callable only from the
-- security-definer functions below, not from the browser roles directly.
create or replace function public.profile_skills_completed(p_user_id uuid)
returns integer
language sql
stable
security definer
set search_path = public
as $$
  select coalesce((
    select count(*)::integer
    from public.progress pr
    cross join lateral jsonb_each(
      case
        when jsonb_typeof(coalesce(pr.data #> '{progress,skills}', pr.data #> '{skills}')) = 'object'
          then coalesce(pr.data #> '{progress,skills}', pr.data #> '{skills}')
        else '{}'::jsonb
      end
    ) as skill(id, rec)
    where pr.user_id = p_user_id
      and jsonb_typeof(skill.rec) = 'object'
      and coalesce(skill.rec->>'tier', '') ~ '^[0-9]+$'
      and (skill.rec->>'tier')::integer >= 4
  ), 0);
$$;

create or replace function public.profile_lookup(p_username text)
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  uname text := lower(btrim(coalesce(p_username, '')));
  rec public.profiles%rowtype;
begin
  if uname !~ '^[a-z0-9](?:[a-z0-9_-]{1,30}[a-z0-9])$' then
    return jsonb_build_object('status', 'missing');
  end if;
  select * into rec from public.profiles where username = uname;
  if not found then
    return jsonb_build_object('status', 'missing');
  end if;
  if not rec.is_public then
    return jsonb_build_object('status', 'private');
  end if;
  return jsonb_build_object(
    'status', 'public',
    'username', rec.username,
    'bio', rec.bio,
    'joined_at', rec.created_at,
    'skills_completed', public.profile_skills_completed(rec.user_id)
  );
end;
$$;

create or replace function public.public_leaderboard(p_limit integer default 5)
returns table (
  username text,
  skills_completed integer,
  joined_at timestamptz
)
language sql
stable
security definer
set search_path = public
as $$
  select
    p.username,
    public.profile_skills_completed(p.user_id) as skills_completed,
    p.created_at as joined_at
  from public.profiles p
  where p.is_public
  order by skills_completed desc, p.created_at asc, p.username asc
  limit least(greatest(coalesce(p_limit, 5), 1), 20);
$$;

revoke all on function public.profile_skills_completed(uuid) from public, anon, authenticated;
revoke all on function public.profile_lookup(text) from public, anon, authenticated;
revoke all on function public.public_leaderboard(integer) from public, anon, authenticated;

grant execute on function public.profile_lookup(text) to anon, authenticated;
grant execute on function public.public_leaderboard(integer) to anon, authenticated;
