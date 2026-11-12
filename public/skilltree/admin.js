/* Owner-only usage and question alerts. Renders nothing unless the signed-in user is an admin. */
(function() {
'use strict';

const main = document.getElementById('sgMain');
const who = document.getElementById('sgWho');
let labels = { skills: {}, boxes: {} };
let client = null;

function el(tag, props) {
  const node = document.createElement(tag);
  if (props) Object.keys(props).forEach(key => {
    const value = props[key];
    if (value == null || value === false) return;
    if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else node.setAttribute(key, value === true ? '' : value);
  });
  for (let i = 2; i < arguments.length; i++) {
    const kid = arguments[i];
    if (kid == null || kid === false) continue;
    node.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return node;
}

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

function show(node) {
  clear(main);
  main.append(node);
}

function skillLabel(id) {
  if (id == null || id === '') return '—';
  return labels.skills[id] || id;
}
function boxLabel(id) {
  if (id == null || id === '' || id === 'all') return 'All boxes';
  if (id === 'none') return 'Nothing selected';
  if (id === 'focus') return 'Focus';
  return labels.boxes[id] || id;
}
function num(value) {
  if (value == null || value === '') return '—';
  const n = Number(value);
  return Number.isFinite(n) ? String(n) : '—';
}
function pct(value) {
  if (value == null || value === '') return '—';
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return (Math.round(n * 1000) / 10).toFixed(1) + '%';
}

function stat(label, value) {
  return el('div', { class: 'stat' }, el('b', { text: num(value) }), el('span', { text: label }));
}

function table(headers, rows) {
  const wrap = el('table');
  const head = el('tr');
  headers.forEach(name => head.append(el('th', { text: name })));
  wrap.append(el('thead', null, head));
  const body = el('tbody');
  if (!rows.length) body.append(el('tr', null, el('td', { colspan: String(headers.length), text: 'None yet.' })));
  rows.forEach(cells => {
    const tr = el('tr');
    cells.forEach(cell => tr.append(el('td', { text: cell == null ? '—' : String(cell) })));
    body.append(tr);
  });
  wrap.append(body);
  return wrap;
}

function choiceLine(choice) {
  let role = '';
  if (choice.picks > 0 && choice.correct_picks === choice.picks) role = 'key';
  else if (choice.correct_picks === 0) role = 'distractor';
  const bits = ['Choice ' + choice.choice, num(choice.picks) + ' picks'];
  if (role) bits.push(role);
  return bits.join(' · ');
}

const ALERT_TEXT = {
  distractor: 'A distractor is picked more often than the key',
  too_hard: 'Very hard',
  too_easy: 'Very easy',
  many_flags: 'Many flags'
};

function alertCard(item) {
  const tags = el('div', { class: 'tags' });
  (item.alerts || []).forEach(code => {
    const cls = code === 'too_hard' ? 'tag hard' : code === 'too_easy' ? 'tag easy' : code === 'many_flags' ? 'tag flag' : 'tag';
    tags.append(el('span', { class: cls, text: ALERT_TEXT[code] || code }));
  });
  const card = el('article', { class: 'alert' },
    el('header', null,
      el('h3', { text: (item.question_id || 'Question') + ' · ' + skillLabel(item.skill_id) }),
      el('span', { class: 'meta', text: num(item.attempts) + ' attempts' })),
    tags,
    el('p', { class: 'meta', text: 'Correct ' + pct(item.p_correct) + ' · flags ' + num(item.flags) + ' · flag rate ' + pct(item.flag_rate) }));
  const choices = item.choices || [];
  if (choices.length) {
    const list = el('ul', { class: 'comments' });
    choices.forEach(choice => list.append(el('li', { text: choiceLine(choice) })));
    card.append(list);
  }
  const comments = item.comments || [];
  if (comments.length) {
    const list = el('ul', { class: 'comments' });
    comments.forEach(text => list.append(el('li', { text: text })));
    card.append(list);
  }
  return card;
}

function section(title, node) {
  return el('section', { class: 'card' }, el('h2', { text: title }), node);
}

function renderDashboard(data) {
  const usage = data.usage || {};
  const thresholds = data.thresholds || {};
  const root = el('div', { id: 'sgDash' });
  root.append(el('h2', { text: 'Usage and question alerts', style: 'margin:0 0 12px' }));
  const summary = el('section', { class: 'card', id: 'sgUsage' },
    el('h2', { text: 'Usage' }),
    el('div', { class: 'stats' },
      stat('Installs', usage.installs),
      stat('Returning', usage.returning_installs),
      stat('Signed-in people', usage.signed_in_users),
      stat('Sessions', usage.sessions),
      stat('Quiz starts', usage.quiz_starts),
      stat('Quiz finishes', usage.quiz_finishes),
      stat('Left early', usage.quiz_leaves),
      stat('Answers', usage.answers)));
  const accuracy = el('p', { class: 'meta', text: 'Answer accuracy ' + pct(usage.answer_accuracy) });
  summary.append(accuracy);
  root.append(summary);

  const courses = (usage.courses || []).map(row => [boxLabel(row.id), num(row.opens)]);
  const focus = (usage.focus || []).map(row => [boxLabel(row.id), num(row.sets)]);
  const skills = (usage.skills || []).map(row => [skillLabel(row.id), num(row.opens)]);
  const leaves = (usage.skill_dropoff || []).map(row => [
    skillLabel(row.skill_id),
    'Question ' + (Number(row.question_index) + 1),
    num(row.leaves)
  ]);
  const stops = (usage.course_stops || []).map(row => [boxLabel(row.box_id), skillLabel(row.skill_id), num(row.learners)]);

  const split = el('div', { class: 'split' },
    section('Courses opened', table(['Course', 'Opens'], courses)),
    section('Focus choices', table(['Focus', 'Times'], focus)));
  root.append(split);
  root.append(section('Skills opened', table(['Skill', 'Opens'], skills)));
  root.append(el('div', { class: 'split' },
    section('Where quizzes stop', table(['Skill', 'Stopped on', 'Leaves'], leaves)),
    section('Where a course stops', table(['Course', 'Last skill', 'Learners'], stops))));

  const alerts = el('section', { class: 'card', id: 'sgAlerts' }, el('h2', { text: 'Question alerts' }));
  const items = data.alerts || [];
  if (!items.length) alerts.append(el('p', { class: 'meta', text: 'No alerts.' }));
  items.forEach(item => alerts.append(alertCard(item)));
  const hard = thresholds.hard_below == null ? '20%' : pct(thresholds.hard_below);
  const easy = thresholds.easy_above == null ? '95%' : pct(thresholds.easy_above);
  alerts.append(el('p', { class: 'foot', text:
    'Difficulty alerts need at least ' + num(thresholds.min_attempts_difficulty || 20) +
    ' attempts and a correct rate under ' + hard + ' or over ' + easy +
    '. A distractor alert needs at least ' + num(thresholds.min_attempts_distractor || 15) +
    ' attempts. Many flags means ' + num(thresholds.many_flags || 5) + ' or more.' }));
  root.append(alerts);

  const questions = (data.questions || []).map(row => [
    row.question_id,
    skillLabel(row.skill_id),
    num(row.attempts),
    pct(row.p_correct),
    pct(row.flag_rate),
    (row.choices || []).map(choiceLine).join('; ') || '—',
    (row.alerts || []).map(code => ALERT_TEXT[code] || code).join(', ') || '—'
  ]);
  root.append(section('Question stats', el('div', { class: 'qstats' }, table(
    ['Question', 'Skill', 'Attempts', 'Correct', 'Flag rate', 'Choices', 'Alerts'],
    questions
  ))));
  show(root);
}

function renderEmpty() {
  if (who) who.textContent = '';
  show(el('div', { class: 'empty', id: 'sgEmpty' }, el('p', { text: 'Nothing to show.' })));
}

function renderSignIn() {
  if (who) who.textContent = '';
  const msg = el('p', { class: 'msg', id: 'sgAuthMsg' });
  const email = el('input', { type: 'email', id: 'sgEmail', placeholder: 'you@example.com', autocomplete: 'email', 'aria-label': 'Email' });
  const send = el('button', { class: 'btn primary', type: 'button', id: 'sgSend', text: 'Send magic link' });
  const card = el('section', { class: 'card signin', id: 'sgSign' },
    el('h2', { text: 'Sign in' }),
    el('p', { class: 'lead', text: 'Sign in to continue.' }),
    el('div', { class: 'row' }, email, send),
    msg);
  const cfg = window.SKILLTREE_CONFIG && window.SKILLTREE_CONFIG.auth;
  if (cfg && cfg.googleEnabled) {
    card.insertBefore(el('button', { class: 'btn', type: 'button', id: 'sgGoogle', text: 'Continue with Google' }), msg);
  }
  show(card);
  send.addEventListener('click', async () => {
    msg.className = 'msg';
    const address = email.value.trim();
    if (!address || address.indexOf('@') < 0) {
      msg.className = 'msg bad';
      msg.textContent = 'Enter a valid email.';
      return;
    }
    if (!client) {
      msg.className = 'msg bad';
      msg.textContent = 'Sign-in is unavailable in this session.';
      return;
    }
    send.disabled = true;
    try {
      const { error } = await client.auth.signInWithOtp({
        email: address,
        options: { emailRedirectTo: location.origin + location.pathname }
      });
      if (error) throw error;
      msg.className = 'msg ok';
      msg.textContent = 'Check your email for the sign-in link.';
    } catch (e) {
      send.disabled = false;
      msg.className = 'msg bad';
      msg.textContent = 'Could not send the link.';
    }
  });
  const google = document.getElementById('sgGoogle');
  if (google) google.addEventListener('click', async () => {
    if (!client) return;
    try {
      await client.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: location.origin + location.pathname }
      });
    } catch (e) {
      msg.className = 'msg bad';
      msg.textContent = 'Could not start Google sign-in.';
    }
  });
}

async function loadLabels() {
  try {
    const manifestRes = await fetch(new URL('manifest.json', location.href));
    if (!manifestRes.ok) return;
    const manifest = await manifestRes.json();
    if (manifest.skills && manifest.skills.file) {
      const data = await fetch(new URL(manifest.skills.file, location.href)).then(r => r.json());
      (data.skills || []).forEach(skill => {
        if (skill && skill.id) labels.skills[skill.id] = skill.name || skill.id;
      });
    }
    if (manifest.collections && manifest.collections.file) {
      const data = await fetch(new URL(manifest.collections.file, location.href)).then(r => r.json());
      (data.boxes || []).forEach(box => {
        if (box && box.id) labels.boxes[box.id] = box.title || box.id;
      });
    }
  } catch (e) { }
}

async function loadDashboard(token, anonKey, url) {
  let res;
  try {
    res = await fetch(String(url).replace(/\/$/, '') + '/rest/v1/rpc/analytics_dashboard', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: anonKey,
        Authorization: 'Bearer ' + token
      },
      body: '{}',
      referrerPolicy: 'no-referrer'
    });
  } catch (e) {
    return null;
  }
  if (!res.ok) return null;
  let data = null;
  try { data = await res.json(); } catch (e) { return null; }
  if (typeof data === 'string') {
    try { data = JSON.parse(data); } catch (e) { return null; }
  }
  if (!data || data.ok !== true) return null;
  return data;
}

async function boot() {
  const cfg = window.SKILLTREE_CONFIG && window.SKILLTREE_CONFIG.supabase;
  if (!cfg || !cfg.url || !cfg.anonKey || !window.supabase) {
    renderEmpty();
    return;
  }
  try {
    client = window.supabase.createClient(cfg.url, cfg.anonKey);
  } catch (e) {
    client = null;
  }
  let session = null;
  if (client) {
    try {
      const { data } = await client.auth.getSession();
      session = data && data.session;
    } catch (e) { session = null; }
  }
  if (!session || !session.access_token) {
    renderSignIn();
    return;
  }
  if (who && session.user && session.user.email) who.textContent = session.user.email;
  const data = await loadDashboard(session.access_token, cfg.anonKey, cfg.url);
  if (!data) {
    renderEmpty();
    return;
  }
  await loadLabels();
  renderDashboard(data);
}

boot();
})();
