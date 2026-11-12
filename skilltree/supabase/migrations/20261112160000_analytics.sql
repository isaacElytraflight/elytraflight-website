-- Skillgrove usage measurement and question flags.
-- Paste this whole script into the Supabase SQL editor. Do not put a service-role key in the app.
--
-- After it runs, set yourself as the owner (Authentication → Users → copy the user UUID,
-- or use the email you sign in with). Replace the address, then run this statement.
-- Zero rows means that person has not signed in yet. Sign in once on the site, then run it again.
--
--   insert into public.skillgrove_admins (user_id)
--   select id from auth.users where email = 'you@example.com'
--   on conflict (user_id) do nothing;
--
--   select user_id from public.skillgrove_admins;
--
-- The internal page is /skilltree/admin.html. It shows aggregates only when
-- public.is_skillgrove_admin() is true for the signed-in user. Everyone else gets nothing.
-- Re-running this script is safe: tables are created if missing, policies are replaced,
-- and the functions are created or replaced. It does not define learner profiles or usernames.

-- ---------------------------------------------------------------------------
-- Admin allow-list. Clients cannot read or write it. Add rows from the SQL editor.
-- ---------------------------------------------------------------------------
create table if not exists public.skillgrove_admins (
  user_id uuid primary key references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);

alter table public.skillgrove_admins enable row level security;

revoke all on table public.skillgrove_admins from anon, authenticated;

-- ---------------------------------------------------------------------------
-- Reusable admin check. Other features may call public.is_skillgrove_admin().
-- True only when the current JWT user is listed in public.skillgrove_admins.
-- Security definer so the caller does not need select access to that table.
-- ---------------------------------------------------------------------------
create or replace function public.is_skillgrove_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $admin$
  select coalesce(auth.uid() is not null and exists (
    select 1 from public.skillgrove_admins where user_id = auth.uid()
  ), false);
$admin$;

revoke all on function public.is_skillgrove_admin() from public, anon, authenticated;
grant execute on function public.is_skillgrove_admin() to anon, authenticated;

comment on function public.is_skillgrove_admin() is
  'True when auth.uid() is listed in skillgrove_admins. Reuse this; do not gate on a shared secret.';

-- ---------------------------------------------------------------------------
-- Usage events. Insert-only for anon and authenticated. No client reads.
-- No IP, user agent, or free-text column. install_id is a random id from the browser.
-- ---------------------------------------------------------------------------
create table if not exists public.analytics_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  install_id uuid not null,
  user_id uuid references auth.users (id) on delete set null,
  kind text not null,
  skill_id text,
  box_id text,
  question_id text,
  mode text,
  round smallint,
  correct boolean,
  choice smallint,
  choices smallint[],
  q_index smallint,
  q_count smallint,
  score smallint,
  n_total smallint,
  passed boolean,
  constraint analytics_events_kind check (
    kind in (
      'session', 'skill_open', 'course_open', 'focus',
      'quiz_start', 'quiz_answer', 'quiz_leave', 'quiz_finish'
    )
  ),
  constraint analytics_events_ids check (
    (skill_id is null or (char_length(skill_id) between 1 and 80 and skill_id ~ '^[A-Za-z0-9_.:/-]+$'))
    and (box_id is null or (char_length(box_id) between 1 and 80 and box_id ~ '^[A-Za-z0-9_.:/-]+$'))
    and (question_id is null or (char_length(question_id) between 1 and 120 and question_id ~ '^[A-Za-z0-9_.:/-]+$'))
  ),
  constraint analytics_events_mode check (
    mode is null or mode in ('practice', 'challenge', 'review', 'all', 'none')
  ),
  constraint analytics_events_round check (round is null or round between 1 and 6),
  constraint analytics_events_choice check (choice is null or choice between 0 and 15),
  constraint analytics_events_choices check (
    choices is null or (
      cardinality(choices) between 1 and 12
      and choices <@ array[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]::smallint[]
    )
  ),
  constraint analytics_events_qindex check (q_index is null or q_index between 0 and 40),
  constraint analytics_events_qcount check (q_count is null or q_count between 1 and 40),
  constraint analytics_events_score check (score is null or score between 0 and 40),
  constraint analytics_events_ntotal check (n_total is null or n_total between 1 and 40),
  constraint analytics_events_shape check (
    (kind = 'session')
    or (kind = 'skill_open' and skill_id is not null)
    or (kind = 'course_open' and box_id is not null)
    or (kind = 'focus')
    or (kind = 'quiz_start' and skill_id is not null)
    or (kind = 'quiz_answer' and skill_id is not null and question_id is not null and correct is not null)
    or (kind = 'quiz_leave' and skill_id is not null and q_index is not null)
    or (kind = 'quiz_finish' and skill_id is not null and score is not null and n_total is not null and passed is not null)
  )
);

create index if not exists analytics_events_created_at_idx
  on public.analytics_events (created_at desc);
create index if not exists analytics_events_install_idx
  on public.analytics_events (install_id, created_at desc);
create index if not exists analytics_events_kind_idx
  on public.analytics_events (kind);
create index if not exists analytics_events_question_idx
  on public.analytics_events (question_id)
  where kind = 'quiz_answer';

alter table public.analytics_events enable row level security;

revoke all on table public.analytics_events from anon, authenticated;
grant insert on table public.analytics_events to anon, authenticated;

drop policy if exists analytics_events_insert on public.analytics_events;
create policy analytics_events_insert
  on public.analytics_events
  for insert
  to anon, authenticated
  with check (
    install_id is not null
    and (
      (auth.uid() is null and user_id is null)
      or user_id = auth.uid()
    )
  );

create or replace function public.analytics_events_before_insert()
returns trigger
language plpgsql
security definer
set search_path = public
as $events$
declare
  recent_install int;
  recent_all int;
begin
  new.created_at := now();
  if auth.uid() is null then
    new.user_id := null;
  else
    new.user_id := auth.uid();
  end if;
  select count(*) into recent_install
  from public.analytics_events
  where install_id = new.install_id
    and created_at > now() - interval '1 minute';
  if recent_install >= 80 then
    raise exception 'rate limit' using errcode = '54000';
  end if;
  select count(*) into recent_all
  from public.analytics_events
  where created_at > now() - interval '1 minute';
  if recent_all >= 600 then
    raise exception 'rate limit' using errcode = '54000';
  end if;
  return new;
end;
$events$;

drop trigger if exists analytics_events_before_insert on public.analytics_events;
create trigger analytics_events_before_insert
  before insert on public.analytics_events
  for each row execute function public.analytics_events_before_insert();

-- ---------------------------------------------------------------------------
-- Question flags. Insert-only. One flag per install per question.
-- ---------------------------------------------------------------------------
create table if not exists public.analytics_flags (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  install_id uuid not null,
  user_id uuid references auth.users (id) on delete set null,
  skill_id text not null,
  question_id text not null,
  reason text not null,
  comment text,
  constraint analytics_flags_reason check (reason in ('wrong', 'unclear', 'typo', 'figure', 'other')),
  constraint analytics_flags_skill check (
    char_length(skill_id) between 1 and 80 and skill_id ~ '^[A-Za-z0-9_.:/-]+$'
  ),
  constraint analytics_flags_question check (
    char_length(question_id) between 1 and 120 and question_id ~ '^[A-Za-z0-9_.:/-]+$'
  ),
  constraint analytics_flags_comment check (
    comment is null or char_length(btrim(comment)) between 1 and 500
  ),
  constraint analytics_flags_once unique (install_id, question_id)
);

create index if not exists analytics_flags_question_idx
  on public.analytics_flags (question_id);
create index if not exists analytics_flags_install_idx
  on public.analytics_flags (install_id, created_at desc);

alter table public.analytics_flags enable row level security;

revoke all on table public.analytics_flags from anon, authenticated;
grant insert on table public.analytics_flags to anon, authenticated;

drop policy if exists analytics_flags_insert on public.analytics_flags;
create policy analytics_flags_insert
  on public.analytics_flags
  for insert
  to anon, authenticated
  with check (
    install_id is not null
    and (
      (auth.uid() is null and user_id is null)
      or user_id = auth.uid()
    )
  );

create or replace function public.analytics_flags_before_insert()
returns trigger
language plpgsql
security definer
set search_path = public
as $flags$
declare
  recent_install int;
  recent_all int;
begin
  new.created_at := now();
  if auth.uid() is null then
    new.user_id := null;
  else
    new.user_id := auth.uid();
  end if;
  if new.comment is not null then
    new.comment := btrim(new.comment);
    if new.comment = '' then
      new.comment := null;
    elsif char_length(new.comment) > 500 then
      new.comment := left(new.comment, 500);
    end if;
  end if;
  select count(*) into recent_install
  from public.analytics_flags
  where install_id = new.install_id
    and created_at > now() - interval '1 hour';
  if recent_install >= 12 then
    raise exception 'rate limit' using errcode = '54000';
  end if;
  select count(*) into recent_all
  from public.analytics_flags
  where created_at > now() - interval '1 hour';
  if recent_all >= 120 then
    raise exception 'rate limit' using errcode = '54000';
  end if;
  return new;
end;
$flags$;

drop trigger if exists analytics_flags_before_insert on public.analytics_flags;
create trigger analytics_flags_before_insert
  before insert on public.analytics_flags
  for each row execute function public.analytics_flags_before_insert();

-- ---------------------------------------------------------------------------
-- Owner dashboard. Aggregates only. Non-admins get {"ok": false} and no rows.
-- Difficulty: p(correct) below 0.20 or above 0.95, at least 20 attempts.
-- Distractor beats the key: at least 15 attempts, and a never-correct choice
-- has more picks than the choice that is always correct.
-- Many flags: 5 or more flags on that question.
-- ---------------------------------------------------------------------------
create or replace function public.analytics_dashboard()
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $dash$
declare
  result jsonb;
begin
  if not public.is_skillgrove_admin() then
    return jsonb_build_object('ok', false);
  end if;

  with answers as (
    select question_id, skill_id, correct, choice
    from public.analytics_events
    where kind = 'quiz_answer' and question_id is not null
  ),
  per_q as (
    select question_id,
      min(skill_id) as skill_id,
      count(*)::int as attempts,
      count(*) filter (where correct)::int as correct_n
    from answers
    group by question_id
  ),
  choice_counts as (
    select question_id, choice,
      count(*)::int as picks,
      count(*) filter (where correct)::int as correct_picks
    from answers
    where choice is not null
    group by question_id, choice
  ),
  flag_counts as (
    select question_id,
      min(skill_id) as skill_id,
      count(*)::int as flags,
      count(*) filter (where reason = 'wrong')::int as n_wrong,
      count(*) filter (where reason = 'unclear')::int as n_unclear,
      count(*) filter (where reason = 'typo')::int as n_typo,
      count(*) filter (where reason = 'figure')::int as n_figure,
      count(*) filter (where reason = 'other')::int as n_other
    from public.analytics_flags
    group by question_id
  ),
  merged as (
    select
      coalesce(q.question_id, f.question_id) as question_id,
      coalesce(q.skill_id, f.skill_id) as skill_id,
      coalesce(q.attempts, 0) as attempts,
      coalesce(q.correct_n, 0) as correct_n,
      coalesce(f.flags, 0) as flags,
      coalesce(f.n_wrong, 0) as n_wrong,
      coalesce(f.n_unclear, 0) as n_unclear,
      coalesce(f.n_typo, 0) as n_typo,
      coalesce(f.n_figure, 0) as n_figure,
      coalesce(f.n_other, 0) as n_other
    from per_q q
    full join flag_counts f on f.question_id = q.question_id
  ),
  scored as (
    select m.*,
      case when m.attempts > 0 then round(m.correct_n::numeric / m.attempts, 4) else null end as p_correct,
      case when m.attempts > 0 then round(m.flags::numeric / m.attempts, 4) else null end as flag_rate,
      coalesce((
        select sum(c.picks)::int from choice_counts c
        where c.question_id = m.question_id and c.picks > 0 and c.correct_picks = c.picks
      ), 0) as key_picks,
      coalesce((
        select max(c.picks)::int from choice_counts c
        where c.question_id = m.question_id and c.correct_picks = 0
      ), 0) as top_distractor
    from merged m
  ),
  marked as (
    select s.*,
      (s.attempts >= 15 and s.top_distractor > s.key_picks) as alert_distractor,
      (s.attempts >= 20 and s.p_correct < 0.20) as alert_hard,
      (s.attempts >= 20 and s.p_correct > 0.95) as alert_easy,
      (s.flags >= 5) as alert_flags
    from scored s
  ),
  packed as (
    select m.*,
      coalesce((
        select jsonb_agg(jsonb_build_object(
          'choice', c.choice,
          'picks', c.picks,
          'correct_picks', c.correct_picks
        ) order by c.choice)
        from choice_counts c
        where c.question_id = m.question_id
      ), '[]'::jsonb) as choice_json,
      coalesce((
        select jsonb_agg(tag)
        from unnest(array_remove(array[
          case when m.alert_distractor then 'distractor' end,
          case when m.alert_hard then 'too_hard' end,
          case when m.alert_easy then 'too_easy' end,
          case when m.alert_flags then 'many_flags' end
        ]::text[], null)) as tag
      ), '[]'::jsonb) as alert_json
    from marked m
  )
  select jsonb_build_object(
    'ok', true,
    'thresholds', jsonb_build_object(
      'min_attempts_difficulty', 20,
      'hard_below', 0.20,
      'easy_above', 0.95,
      'min_attempts_distractor', 15,
      'many_flags', 5
    ),
    'usage', jsonb_build_object(
      'installs', (select count(distinct install_id)::int from public.analytics_events),
      'signed_in_users', (select count(distinct user_id)::int from public.analytics_events where user_id is not null),
      'returning_installs', (
        select count(*)::int from (
          select install_id
          from public.analytics_events
          group by install_id
          having count(distinct (created_at at time zone 'utc')::date) >= 2
        ) returning_rows
      ),
      'sessions', (select count(*)::int from public.analytics_events where kind = 'session'),
      'quiz_starts', (select count(*)::int from public.analytics_events where kind = 'quiz_start'),
      'quiz_finishes', (select count(*)::int from public.analytics_events where kind = 'quiz_finish'),
      'quiz_leaves', (select count(*)::int from public.analytics_events where kind = 'quiz_leave'),
      'answers', (select count(*)::int from public.analytics_events where kind = 'quiz_answer'),
      'answer_accuracy', (
        select round(avg(case when correct then 1.0 else 0.0 end)::numeric, 4)
        from public.analytics_events
        where kind = 'quiz_answer' and correct is not null
      ),
      'courses', coalesce((
        select jsonb_agg(jsonb_build_object('id', box_id, 'opens', n) order by n desc)
        from (
          select box_id, count(*)::int as n
          from public.analytics_events
          where kind = 'course_open' and box_id is not null
          group by box_id
          order by n desc
          limit 40
        ) course_rows
      ), '[]'::jsonb),
      'skills', coalesce((
        select jsonb_agg(jsonb_build_object('id', skill_id, 'opens', n) order by n desc)
        from (
          select skill_id, count(*)::int as n
          from public.analytics_events
          where kind = 'skill_open' and skill_id is not null
          group by skill_id
          order by n desc
          limit 40
        ) skill_rows
      ), '[]'::jsonb),
      'focus', coalesce((
        select jsonb_agg(jsonb_build_object('id', focus_id, 'sets', n) order by n desc)
        from (
          select coalesce(box_id, mode, 'focus') as focus_id, count(*)::int as n
          from public.analytics_events
          where kind = 'focus'
          group by coalesce(box_id, mode, 'focus')
          order by n desc
          limit 40
        ) focus_rows
      ), '[]'::jsonb),
      'skill_dropoff', coalesce((
        select jsonb_agg(jsonb_build_object(
          'skill_id', skill_id,
          'question_index', q_index,
          'leaves', n
        ) order by n desc)
        from (
          select skill_id, q_index, count(*)::int as n
          from public.analytics_events
          where kind = 'quiz_leave' and skill_id is not null and q_index is not null
          group by skill_id, q_index
          order by n desc
          limit 40
        ) leave_rows
      ), '[]'::jsonb),
      'course_stops', coalesce((
        select jsonb_agg(jsonb_build_object(
          'box_id', box_id,
          'skill_id', skill_id,
          'learners', n
        ) order by n desc)
        from (
          select box_id, skill_id, count(*)::int as n
          from (
            select distinct on (install_id, box_id) box_id, skill_id
            from public.analytics_events
            where kind = 'skill_open' and box_id is not null and skill_id is not null
            order by install_id, box_id, created_at desc
          ) last_skill
          group by box_id, skill_id
          order by n desc
          limit 40
        ) stop_rows
      ), '[]'::jsonb)
    ),
    'questions', coalesce((
      select jsonb_agg(jsonb_build_object(
        'question_id', question_id,
        'skill_id', skill_id,
        'attempts', attempts,
        'correct', correct_n,
        'p_correct', p_correct,
        'flags', flags,
        'flag_rate', flag_rate,
        'flag_reasons', jsonb_build_object(
          'wrong', n_wrong,
          'unclear', n_unclear,
          'typo', n_typo,
          'figure', n_figure,
          'other', n_other
        ),
        'choices', choice_json,
        'alerts', alert_json
      ) order by attempts desc, question_id)
      from (
        select * from packed
        order by attempts desc, question_id
        limit 25
      ) top_questions
    ), '[]'::jsonb),
    'alerts', coalesce((
      select jsonb_agg(jsonb_build_object(
        'question_id', question_id,
        'skill_id', skill_id,
        'attempts', attempts,
        'correct', correct_n,
        'p_correct', p_correct,
        'flags', flags,
        'flag_rate', flag_rate,
        'flag_reasons', jsonb_build_object(
          'wrong', n_wrong,
          'unclear', n_unclear,
          'typo', n_typo,
          'figure', n_figure,
          'other', n_other
        ),
        'choices', choice_json,
        'alerts', alert_json,
        'comments', comments_json
      ) order by flags desc, attempts desc, question_id)
      from (
        select p.*,
          coalesce((
            select jsonb_agg(snippet order by created_at desc)
            from (
              select left(btrim(comment), 240) as snippet, created_at
              from public.analytics_flags
              where question_id = p.question_id
                and comment is not null
                and btrim(comment) <> ''
              order by created_at desc
              limit 3
            ) recent_comments
          ), '[]'::jsonb) as comments_json
        from packed p
        where p.alert_distractor or p.alert_hard or p.alert_easy or p.alert_flags
        order by p.flags desc, p.attempts desc, p.question_id
        limit 80
      ) alert_rows
    ), '[]'::jsonb)
  ) into result;

  return result;
end;
$dash$;

revoke all on function public.analytics_dashboard() from public, anon, authenticated;
grant execute on function public.analytics_dashboard() to authenticated;

comment on function public.analytics_dashboard() is
  'Aggregated usage and question-stat alerts for skillgrove admins. Returns {"ok": false} for everyone else.';

notify pgrst, 'reload schema';
