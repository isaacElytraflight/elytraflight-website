/* Skillgrove usage measurement and question flags.
   Anonymous install id, plus the signed-in user id when there is one.
   No third-party tracker, no fingerprint, no IP. Events are batched.
   If the tables are not there yet, this queues locally and stays quiet. */
(function() {
'use strict';

const PRIVACY_KEY = 'skilltree.privacy.v1';
const INSTALL_KEY = 'skilltree.install.v1';
const EVENT_KEY = 'skilltree.events.q.v1';
const FLAG_KEY = 'skilltree.flags.q.v1';
const FLUSH_MS = 4000;
const BATCH = 20;
const EVENT_CAP = 100;
const FLAG_CAP = 30;
const ID_RE = /^[A-Za-z0-9_.:/-]+$/;
const REASONS = ['wrong', 'unclear', 'typo', 'figure', 'other'];
const REASON_LABEL = { wrong: 'Wrong', unclear: 'Unclear', typo: 'Typo', figure: 'Figure', other: 'Other' };

let queue = [];
let flagQueue = [];
let timer = null;
let flushing = Promise.resolve();
let serverOff = false;
let flagsOff = false;
let started = false;
let listening = false;
let sessionSent = false;
let memInstall = null;
let live = null;
let flagDraft = null;

function storageGet(key) {
  try { return localStorage.getItem(key); } catch (e) { return null; }
}
function storageSet(key, value) {
  try { localStorage.setItem(key, value); return true; } catch (e) { return false; }
}
function storageRemove(key) {
  try { localStorage.removeItem(key); } catch (e) { }
}

function uuid() {
  try {
    if (window.crypto && typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  } catch (e) { }
  const bytes = new Uint8Array(16);
  if (window.crypto && crypto.getRandomValues) crypto.getRandomValues(bytes);
  else return null;
  bytes[6] = (bytes[6] & 15) | 64;
  bytes[8] = (bytes[8] & 63) | 128;
  const hex = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
  return hex.slice(0, 8) + '-' + hex.slice(8, 12) + '-' + hex.slice(12, 16) + '-' + hex.slice(16, 20) + '-' + hex.slice(20);
}

function installId() {
  const existing = storageGet(INSTALL_KEY);
  if (existing && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(existing)) return existing;
  if (!memInstall) memInstall = uuid();
  if (!memInstall) return null;
  storageSet(INSTALL_KEY, memInstall);
  return memInstall;
}

function userId() {
  try {
    const auth = window.SkillgroveAuth;
    const user = auth && auth.getUser && auth.getUser();
    return user && user.id ? user.id : null;
  } catch (e) { return null; }
}

function browserOptOut() {
  try {
    const dnt = navigator.doNotTrack || window.doNotTrack || navigator.msDoNotTrack;
    if (dnt === '1' || dnt === 'yes') return true;
    if (navigator.globalPrivacyControl === true) return true;
  } catch (e) { }
  return false;
}

function usageChoice() {
  try {
    const raw = JSON.parse(storageGet(PRIVACY_KEY) || 'null');
    if (raw && raw.usage === false) return false;
    if (raw && raw.usage === true) return true;
  } catch (e) { }
  return null;
}

function trackingAllowed() {
  if (browserOptOut()) return false;
  return usageChoice() !== false;
}

function persistEvents() {
  storageSet(EVENT_KEY, JSON.stringify(queue.slice(-EVENT_CAP)));
}
function persistFlags() {
  storageSet(FLAG_KEY, JSON.stringify(flagQueue.slice(-FLAG_CAP)));
}
function loadQueue() {
  try {
    const raw = JSON.parse(storageGet(EVENT_KEY) || '[]');
    if (Array.isArray(raw)) queue = raw.filter(row => row && typeof row === 'object').slice(-EVENT_CAP);
  } catch (e) { queue = []; }
  try {
    const raw = JSON.parse(storageGet(FLAG_KEY) || '[]');
    if (Array.isArray(raw)) flagQueue = raw.filter(row => row && typeof row === 'object').slice(-FLAG_CAP);
  } catch (e) { flagQueue = []; }
}

function putId(row, key, value, max) {
  if (value == null || value === '') return true;
  const text = String(value);
  if (text.length > max || !ID_RE.test(text)) return false;
  row[key] = text;
  return true;
}
function putInt(row, key, value, min, max) {
  if (value == null || value === '') return true;
  const n = Number(value);
  if (!Number.isInteger(n) || n < min || n > max) return false;
  row[key] = n;
  return true;
}

function cleanRow(partial) {
  if (!partial || typeof partial !== 'object') return null;
  const kind = partial.kind;
  const allowed = {
    session: 1, skill_open: 1, course_open: 1, focus: 1,
    quiz_start: 1, quiz_answer: 1, quiz_leave: 1, quiz_finish: 1
  };
  if (!allowed[kind]) return null;
  const id = installId();
  if (!id) return null;
  const row = { kind: kind, install_id: id, user_id: userId() };
  if (!putId(row, 'skill_id', partial.skill_id, 80)) return null;
  if (!putId(row, 'box_id', partial.box_id, 80)) return null;
  if (!putId(row, 'question_id', partial.question_id, 120)) return null;
  if (kind === 'focus' && (partial.mode === 'all' || partial.mode === 'none')) row.mode = partial.mode;
  else if (partial.mode === 'practice' || partial.mode === 'challenge' || partial.mode === 'review') row.mode = partial.mode;
  if (!putInt(row, 'round', partial.round, 1, 6)) return null;
  if (!putInt(row, 'choice', partial.choice, 0, 15)) return null;
  if (!putInt(row, 'q_index', partial.q_index, 0, 40)) return null;
  if (!putInt(row, 'q_count', partial.q_count, 1, 40)) return null;
  if (!putInt(row, 'score', partial.score, 0, 40)) return null;
  if (!putInt(row, 'n_total', partial.n_total, 1, 40)) return null;
  if (typeof partial.correct === 'boolean') row.correct = partial.correct;
  if (typeof partial.passed === 'boolean') row.passed = partial.passed;
  if (Array.isArray(partial.choices) && partial.choices.length) {
    if (partial.choices.length > 12) return null;
    const choices = [];
    for (let i = 0; i < partial.choices.length; i++) {
      const n = Number(partial.choices[i]);
      if (!Number.isInteger(n) || n < 0 || n > 15) return null;
      choices.push(n);
    }
    row.choices = choices;
  }
  if (kind === 'skill_open' && !row.skill_id) return null;
  if (kind === 'course_open' && !row.box_id) return null;
  if (kind === 'quiz_start' && !row.skill_id) return null;
  if (kind === 'quiz_answer' && (!row.skill_id || !row.question_id || typeof row.correct !== 'boolean')) return null;
  if (kind === 'quiz_leave' && (!row.skill_id || row.q_index == null)) return null;
  if (kind === 'quiz_finish' && (!row.skill_id || row.score == null || row.n_total == null || typeof row.passed !== 'boolean')) return null;
  return row;
}

function cleanFlag(partial) {
  if (!partial || REASONS.indexOf(partial.reason) < 0) return null;
  const id = installId();
  if (!id) return null;
  const skill = partial.skill_id == null ? '' : String(partial.skill_id);
  const question = partial.question_id == null ? '' : String(partial.question_id);
  if (!skill || skill.length > 80 || !ID_RE.test(skill)) return null;
  if (!question || question.length > 120 || !ID_RE.test(question)) return null;
  const row = {
    install_id: id,
    user_id: userId(),
    skill_id: skill,
    question_id: question,
    reason: partial.reason
  };
  const comment = partial.comment == null ? '' : String(partial.comment).trim();
  if (comment) {
    if (comment.length > 500) return null;
    row.comment = comment;
  }
  return row;
}

function cfgClient() {
  const cfg = window.SKILLTREE_CONFIG && window.SKILLTREE_CONFIG.supabase;
  if (!cfg || !cfg.url || !cfg.anonKey) return null;
  return cfg;
}

async function authToken(cfg) {
  let token = cfg.anonKey;
  try {
    const auth = window.SkillgroveAuth;
    const sb = auth && auth.client && auth.client();
    if (sb && sb.auth && sb.auth.getSession) {
      const { data } = await sb.auth.getSession();
      if (data && data.session && data.session.access_token) token = data.session.access_token;
    }
  } catch (e) { }
  return token;
}

async function postTable(table, rows, opts) {
  const cfg = cfgClient();
  if (!cfg || !rows || !rows.length) return { ok: false, kind: 'unavailable' };
  const token = await authToken(cfg);
  let res;
  try {
    res = await fetch(String(cfg.url).replace(/\/$/, '') + '/rest/v1/' + table, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: cfg.anonKey,
        Authorization: 'Bearer ' + token,
        Prefer: 'return=minimal'
      },
      body: JSON.stringify(rows),
      referrerPolicy: 'no-referrer',
      keepalive: !!(opts && opts.keepalive)
    });
  } catch (e) {
    return { ok: false, kind: 'network' };
  }
  if (res.ok) return { ok: true };
  let body = {};
  try { body = await res.json(); } catch (e) { body = {}; }
  const code = String(body.code || '');
  const message = String(body.message || body.details || '').toLowerCase();
  if (res.status === 409 || code === '23505') return { ok: false, kind: 'duplicate' };
  if (code === '54000' || message.includes('rate limit')) return { ok: false, kind: 'rate' };
  const missing = res.status === 404 || code === 'PGRST205' || code === '42P01' || code === 'PGRST204'
    || message.includes('schema cache') || message.includes('does not exist') || message.includes('could not find the table');
  if (missing) return { ok: false, kind: 'missing' };
  return { ok: false, kind: 'error' };
}

function schedule(ms) {
  if (timer || serverOff || !trackingAllowed()) return;
  timer = setTimeout(() => { timer = null; flush().catch(function() {}); }, ms == null ? FLUSH_MS : ms);
}

function stamp(rows) {
  const uid = userId();
  const iid = installId();
  rows.forEach(row => {
    row.user_id = uid;
    if (iid) row.install_id = iid;
  });
}

async function flushNow(opts) {
  if (!trackingAllowed()) {
    queue = [];
    persistEvents();
    return;
  }
  if (serverOff || !queue.length) return;
  const batch = queue.splice(0, BATCH);
  stamp(batch);
  persistEvents();
  const result = await postTable('analytics_events', batch, opts);
  if (result.ok || result.kind === 'duplicate') {
    if (queue.length) schedule(400);
    return;
  }
  queue = batch.concat(queue).slice(-EVENT_CAP);
  persistEvents();
  if (result.kind === 'missing' || result.kind === 'unavailable') {
    serverOff = true;
    return;
  }
  schedule(result.kind === 'rate' ? 60000 : 20000);
}

function flush(opts) {
  if (timer) { clearTimeout(timer); timer = null; }
  const run = flushing.then(() => flushNow(opts));
  flushing = run.then(() => {}, () => {});
  return run;
}

function enqueue(partial) {
  if (!trackingAllowed()) return;
  const row = cleanRow(partial);
  if (!row) return;
  queue.push(row);
  if (queue.length > EVENT_CAP) queue.splice(0, queue.length - EVENT_CAP);
  persistEvents();
  if (serverOff) return;
  if (queue.length >= BATCH) flush().catch(function() {});
  else schedule();
}

function ensureSession() {
  if (sessionSent || !trackingAllowed()) return;
  sessionSent = true;
  enqueue({ kind: 'session' });
}

function rememberFlag(row) {
  flagQueue = flagQueue.filter(item => item.question_id !== row.question_id);
  flagQueue.push(row);
  if (flagQueue.length > FLAG_CAP) flagQueue.splice(0, flagQueue.length - FLAG_CAP);
  persistFlags();
}

async function flushFlags() {
  if (flagsOff || !flagQueue.length) return;
  const batch = flagQueue.slice();
  stamp(batch);
  const result = await postTable('analytics_flags', batch);
  if (result.ok || result.kind === 'duplicate') {
    const sent = new Set(batch.map(row => row.question_id));
    flagQueue = flagQueue.filter(row => !sent.has(row.question_id));
    persistFlags();
    return;
  }
  if (result.kind === 'missing' || result.kind === 'unavailable') flagsOff = true;
}

async function submitFlag(partial) {
  const row = cleanFlag(partial);
  if (!row) return 'invalid';
  if (flagsOff) {
    rememberFlag(row);
    return 'queued';
  }
  const result = await postTable('analytics_flags', [row]);
  if (result.ok || result.kind === 'duplicate') return 'sent';
  rememberFlag(row);
  if (result.kind === 'missing' || result.kind === 'unavailable') flagsOff = true;
  return 'queued';
}

function boxes() {
  try {
    const data = window.__skillgrove && window.__skillgrove.collections && window.__skillgrove.collections.data();
    return (data && data.boxes) || [];
  } catch (e) { return []; }
}
function boxMaps() {
  const list = boxes();
  const byId = {};
  const parent = {};
  list.forEach(box => {
    if (!box || !box.id) return;
    byId[box.id] = box;
    (box.children || []).forEach(id => { parent[id] = box.id; });
  });
  return { byId, parent };
}
function courseOfBox(id) {
  const maps = boxMaps();
  let cur = id;
  const seen = {};
  while (cur && !seen[cur]) {
    seen[cur] = true;
    const box = maps.byId[cur];
    if (box && box.kind === 'course') return cur;
    cur = maps.parent[cur];
  }
  return null;
}
function courseForSkill(skillId) {
  let ids = [];
  try {
    const map = window.__skillgrove.collections.skillToBoxes();
    ids = (map && map[skillId]) || [];
  } catch (e) { ids = []; }
  const found = [];
  ids.forEach(id => {
    const course = courseOfBox(id);
    if (course && found.indexOf(course) < 0) found.push(course);
  });
  if (!found.length) return null;
  let selected = [];
  try { selected = window.__skillgrove.collections.selected() || []; } catch (e) { selected = []; }
  for (let i = 0; i < found.length; i++) if (selected.indexOf(found[i]) >= 0) return found[i];
  return found[0];
}
function courseIds() {
  return boxes().filter(box => box && box.kind === 'course' && box.id).map(box => box.id);
}

function onFocus(detail) {
  if (detail.all) {
    enqueue({ kind: 'focus', mode: 'all' });
    courseIds().forEach(id => enqueue({ kind: 'course_open', box_id: id }));
    return;
  }
  const list = Array.isArray(detail.boxes) ? detail.boxes : [];
  if (!list.length) {
    enqueue({ kind: 'focus', mode: 'none' });
    return;
  }
  const courses = [];
  list.forEach(id => {
    enqueue({ kind: 'focus', box_id: id });
    const course = courseOfBox(id) || (boxes().some(box => box.id === id && box.kind === 'course') ? id : null);
    if (course && courses.indexOf(course) < 0) courses.push(course);
  });
  courses.forEach(id => enqueue({ kind: 'course_open', box_id: id }));
}

function onAppEvent(type, detail) {
  detail = detail || {};
  if (type === 'quiz_start') {
    live = {
      skill_id: detail.skill_id,
      round: detail.round,
      mode: detail.mode,
      q_count: detail.q_count,
      q_index: 0
    };
  } else if (type === 'quiz_finish' || type === 'quiz_leave') {
    live = null;
  }
  if (!trackingAllowed()) return;
  if (type === 'skill_open' && detail.skill_id) {
    const row = { kind: 'skill_open', skill_id: detail.skill_id };
    const course = courseForSkill(detail.skill_id);
    if (course) row.box_id = course;
    enqueue(row);
  } else if (type === 'focus') onFocus(detail);
  else if (type === 'quiz_start') enqueue({
    kind: 'quiz_start', skill_id: detail.skill_id, round: detail.round, mode: detail.mode, q_count: detail.q_count
  });
  else if (type === 'quiz_answer') enqueue({
    kind: 'quiz_answer',
    skill_id: detail.skill_id,
    question_id: detail.question_id,
    round: detail.round,
    mode: detail.mode,
    correct: detail.correct,
    choice: detail.choice,
    choices: detail.choices,
    q_index: detail.q_index,
    q_count: detail.q_count
  });
  else if (type === 'quiz_leave') enqueue({
    kind: 'quiz_leave',
    skill_id: detail.skill_id,
    round: detail.round,
    mode: detail.mode,
    q_index: detail.q_index,
    q_count: detail.q_count
  });
  else if (type === 'quiz_finish') enqueue({
    kind: 'quiz_finish',
    skill_id: detail.skill_id,
    round: detail.round,
    mode: detail.mode,
    score: detail.score,
    n_total: detail.n_total,
    passed: detail.passed
  });
}

function currentQuiz() {
  try {
    const api = window.__skillgrove && window.__skillgrove.telemetry;
    return api && api.quiz ? api.quiz() : null;
  } catch (e) { return null; }
}

function noteQuizLeave() {
  if (!live || !trackingAllowed()) return;
  const fresh = currentQuiz();
  const src = fresh || live;
  enqueue({
    kind: 'quiz_leave',
    skill_id: src.skill_id,
    round: src.round,
    mode: src.mode,
    q_index: src.q_index,
    q_count: src.q_count
  });
  live = null;
}
function onPageHide() {
  noteQuizLeave();
  flush({ keepalive: true }).catch(function() {});
}
function onVisibility() {
  if (document.visibilityState === 'hidden') flush({ keepalive: true }).catch(function() {});
}

function privacyNote(el) {
  if (!el) return;
  if (browserOptOut()) el.textContent = 'Your browser asks not to be tracked, so usage measurement stays off.';
  else el.textContent = 'Anonymous counts of courses, skills, and quizzes on this device. No third-party trackers.';
}

function syncPrivacyControl() {
  const input = document.getElementById('usageMeasure');
  const label = document.getElementById('usageOptLabel');
  const note = document.getElementById('usageNote');
  privacyNote(note);
  if (!input) return;
  const blocked = browserOptOut();
  input.checked = !blocked && trackingAllowed();
  input.disabled = blocked;
  if (label) label.setAttribute('aria-checked', input.checked ? 'true' : 'false');
}

function onPrivacyChange() {
  const input = document.getElementById('usageMeasure');
  const label = document.getElementById('usageOptLabel');
  if (!input || input.disabled) return;
  storageSet(PRIVACY_KEY, JSON.stringify({ usage: !!input.checked }));
  if (label) label.setAttribute('aria-checked', input.checked ? 'true' : 'false');
  if (!input.checked) {
    sessionSent = false;
    queue = [];
    persistEvents();
    if (timer) { clearTimeout(timer); timer = null; }
    return;
  }
  serverOff = false;
  ensureSession();
}

function ensurePrivacyControl() {
  const host = document.querySelector('#profileEditor .profile-tools');
  if (!host || document.getElementById('usageMeasure')) {
    syncPrivacyControl();
    return;
  }
  const label = document.createElement('label');
  label.className = 'menu-check';
  label.id = 'usageOptLabel';
  const input = document.createElement('input');
  input.type = 'checkbox';
  input.id = 'usageMeasure';
  const span = document.createElement('span');
  span.textContent = 'Usage measurement';
  label.append(input, span);
  const note = document.createElement('p');
  note.className = 'menu-note';
  note.id = 'usageNote';
  host.insertAdjacentElement('afterend', note);
  host.insertAdjacentElement('afterend', label);
  input.addEventListener('change', onPrivacyChange);
  syncPrivacyControl();
}

function dismissFlag(form) {
  if (!form) return;
  form.hidden = true;
  const block = form.closest('.qflag-block');
  const btn = block && block.querySelector('.qflag-btn');
  if (btn) btn.setAttribute('aria-expanded', 'false');
  const radio = form.querySelector('input[type="radio"]');
  const qid = radio && radio.name ? radio.name.replace(/^flagReason-/, '') : '';
  if (!flagDraft || flagDraft.flagged) return;
  const saved = String(flagDraft.questionId == null ? '' : flagDraft.questionId).replace(/[^A-Za-z0-9_-]/g, '');
  if (saved === qid) flagDraft.open = false;
}
function rememberFlagDraft(questionId, form, btn, area) {
  const picked = form.querySelector('input[type="radio"]:checked');
  flagDraft = {
    questionId: questionId,
    open: !form.hidden,
    reason: picked ? picked.value : '',
    comment: area.value,
    flagged: !!btn.disabled
  };
}
function flagControl(questionId, skillId, primary) {
  const wrap = document.createElement('div');
  wrap.className = 'qflag-block';
  const saved = flagDraft && flagDraft.questionId === questionId ? flagDraft : null;
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn small qflag-btn';
  btn.textContent = saved && saved.flagged ? 'Flagged' : 'Flag question';
  btn.disabled = !!(saved && saved.flagged);
  btn.setAttribute('aria-expanded', 'false');
  if (primary) btn.id = 'flagBtn';
  const form = document.createElement('div');
  form.className = 'qflag-form';
  form.hidden = true;
  const prompt = document.createElement('p');
  prompt.textContent = 'What should we look at?';
  const reasons = document.createElement('div');
  reasons.className = 'qflag-reasons';
  reasons.setAttribute('role', 'radiogroup');
  reasons.setAttribute('aria-label', 'Reason');
  const group = 'flagReason-' + String(questionId == null ? '' : questionId).replace(/[^A-Za-z0-9_-]/g, '');
  REASONS.forEach(reason => {
    const lab = document.createElement('label');
    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = group;
    radio.value = reason;
    const text = document.createElement('span');
    text.textContent = REASON_LABEL[reason];
    lab.append(radio, text);
    reasons.append(lab);
  });
  const area = document.createElement('textarea');
  area.maxLength = 500;
  area.rows = 2;
  area.placeholder = 'Optional note';
  area.setAttribute('aria-label', 'Optional note');
  if (primary) area.id = 'flagComment';
  if (saved && !saved.flagged) {
    form.hidden = !saved.open;
    btn.setAttribute('aria-expanded', saved.open ? 'true' : 'false');
    if (saved.reason) {
      const radios = reasons.querySelectorAll('input[type="radio"]');
      for (let i = 0; i < radios.length; i++) if (radios[i].value === saved.reason) radios[i].checked = true;
    }
    area.value = saved.comment || '';
  }
  const row = document.createElement('div');
  row.className = 'qflag-row';
  const status = document.createElement('span');
  status.className = 'qflag-status';
  const send = document.createElement('button');
  send.type = 'button';
  send.className = 'btn small primary';
  send.textContent = 'Send flag';
  if (primary) send.id = 'flagSend';
  row.append(status, send);
  form.append(prompt, reasons, area, row);
  btn.addEventListener('click', () => {
    if (btn.disabled) return;
    form.hidden = !form.hidden;
    btn.setAttribute('aria-expanded', form.hidden ? 'false' : 'true');
    rememberFlagDraft(questionId, form, btn, area);
    if (!form.hidden) {
      const first = form.querySelector('input[type="radio"]');
      if (first) first.focus();
    }
  });
  reasons.addEventListener('change', () => rememberFlagDraft(questionId, form, btn, area));
  area.addEventListener('input', () => rememberFlagDraft(questionId, form, btn, area));
  send.addEventListener('click', async () => {
    const picked = form.querySelector('input[type="radio"]:checked');
    if (!picked) {
      status.className = 'qflag-status bad';
      status.textContent = 'Pick a reason.';
      return;
    }
    send.disabled = true;
    const outcome = await submitFlag({
      skill_id: skillId,
      question_id: questionId,
      reason: picked.value,
      comment: area.value
    });
    if (outcome === 'invalid') {
      send.disabled = false;
      status.className = 'qflag-status bad';
      status.textContent = 'That note is too long.';
      return;
    }
    if (outcome === 'drop') {
      send.disabled = false;
      status.className = 'qflag-status bad';
      status.textContent = 'Try again later.';
      return;
    }
    form.hidden = true;
    btn.disabled = true;
    btn.textContent = 'Flagged';
    btn.setAttribute('aria-expanded', 'false');
    flagDraft = { questionId: questionId, open: false, reason: '', comment: '', flagged: true };
  });
  wrap.append(btn, form);
  return wrap;
}

function attachApp() {
  if (listening) return;
  try {
    const sg = window.__skillgrove;
    if (sg && sg.telemetry && sg.telemetry.on) {
      sg.telemetry.on(onAppEvent);
      listening = true;
    }
  } catch (e) { }
}

function start() {
  ensurePrivacyControl();
  const first = !started;
  if (first) {
    started = true;
    loadQueue();
    window.addEventListener('pagehide', onPageHide);
    document.addEventListener('visibilitychange', onVisibility);
  }
  attachApp();
  const sendFlags = () => { flushFlags().catch(function() {}); };
  if (!first) {
    sendFlags();
    return;
  }
  if (!trackingAllowed()) {
    queue = [];
    persistEvents();
    sendFlags();
    return;
  }
  ensureSession();
  sendFlags();
}

ensurePrivacyControl();

window.SkillgroveTelemetry = {
  start: start,
  flush: flush,
  flagControl: flagControl,
  dismissFlag: dismissFlag,
  trackingAllowed: trackingAllowed
};

if (window.__skillgrove) start();
})();
