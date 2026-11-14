-- SG-081. Distractor alerts were treating an error-step answer as a multiple-choice key.
-- choice stores only the step, while correct also depends on the reason, so that
-- step is not always correct. key_picks became 0 and any never-correct step raised
-- the alert.
-- A distractor alert now needs a choice that is always correct, and it stays off
-- when any recorded choice is only sometimes correct.
--
-- Paste this whole script into the Supabase SQL editor. Isaac applies it himself.

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
      ), 0) as top_distractor,
      exists (
        select 1 from choice_counts c
        where c.question_id = m.question_id
          and c.picks > 0
          and c.correct_picks > 0
          and c.correct_picks < c.picks
      ) as choice_ambiguous
    from merged m
  ),
  marked as (
    select s.*,
      (s.attempts >= 15
        and s.key_picks > 0
        and not s.choice_ambiguous
        and s.top_distractor > s.key_picks) as alert_distractor,
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
  'Aggregated usage and question-stat alerts for admins listed in skillgrove_admins. Returns {"ok": false} for everyone else. Distractor alerts ignore choices that are only sometimes correct.';

notify pgrst, 'reload schema';
