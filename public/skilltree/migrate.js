/* Elytraflight's Skill Tree progress migration for retired skill ids, to-do items, scope, and exam dates.
   Works in the browser (window.SkillgroveMigrate) and in Node (module.exports).
   Retired progress moves onto the survivor: higher mastery tier, later practice
   time, and the union of attempt history.    To-do entries follow the same map and,
   when a catalog of live skill ids is provided, entries that no longer exist are
   dropped. A starting tier (`from`, an integer 0–4) is kept when present.
   Running it again changes nothing. A to-do line may carry source: 'plan'.
   A saved exam plan (progress.savedPlan) is kept; the newer createdAt wins. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SkillgroveMigrate = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function mergeSkillRecords(local, remote) {
    if (!local && !remote) return null;
    if (!local) return remote;
    if (!remote) return local;

    const seenT = new Set();
    const mergedHist = [];
    const allHist = [...(local.history || []), ...(remote.history || [])];
    allHist.sort((a, b) => a.t - b.t);
    for (const h of allHist) {
      if (!seenT.has(h.t)) {
        seenT.add(h.t);
        mergedHist.push(h);
      }
    }

    return {
      tier: Math.max(local.tier || 0, remote.tier || 0),
      lastPracticed: Math.max(local.lastPracticed || 0, remote.lastPracticed || 0) || null,
      history: mergedHist.slice(-60)
    };
  }

  function cloneSkill(skill) {
    if (!skill || typeof skill !== 'object') return skill;
    return {
      tier: skill.tier,
      lastPracticed: skill.lastPracticed,
      history: Array.isArray(skill.history) ? skill.history.map(h => (h && typeof h === 'object' ? { ...h } : h)) : []
    };
  }

  function resolveSurvivor(id, retired) {
    const seen = new Set();
    let cur = id;
    while (retired[cur] && retired[cur] !== cur && !seen.has(cur)) {
      seen.add(cur);
      cur = retired[cur];
    }
    return cur;
  }

  /** Starting tier stored on a to-do line. Null when missing or not an integer 0–4. */
  function readTodoFrom(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const n = raw.from;
    if (typeof n !== 'number' || !Number.isInteger(n) || n < 0 || n > 4) return null;
    return n;
  }

  function readTodoSource(raw) {
    if (!raw || typeof raw !== 'object') return null;
    return raw.source === 'plan' ? 'plan' : null;
  }

  function normalizeTodoItem(item) {
    if (!item || typeof item !== 'object') return null;
    const type = item.type === 'skill' || item.type === 'challenge' ? item.type : null;
    if (!type || typeof item.id !== 'string' || !item.id) return null;
    const out = { type, id: item.id };
    const from = readTodoFrom(item);
    if (from != null) out.from = from;
    const source = readTodoSource(item);
    if (source) out.source = source;
    return out;
  }

  function todoEntryChanged(raw, next) {
    if (!raw || typeof raw !== 'object') return true;
    if (raw.type !== next.type || raw.id !== next.id) return true;
    const rawFrom = readTodoFrom(raw);
    const nextFrom = next.from == null ? null : next.from;
    if (rawFrom !== nextFrom) return true;
    if (raw.from !== undefined && rawFrom == null) return true;
    const rawSource = readTodoSource(raw);
    const nextSource = next.source === 'plan' ? 'plan' : null;
    if (rawSource !== nextSource) return true;
    if (raw.source !== undefined && rawSource == null) return true;
    for (const k of Object.keys(raw)) {
      if (k !== 'type' && k !== 'id' && k !== 'from' && k !== 'source') return true;
    }
    return false;
  }

  function keepHigherFrom(prev, from) {
    if (from == null) return;
    if (prev.from == null || from > prev.from) prev.from = from;
  }

  function keepPlanSource(prev, source) {
    if (source === 'plan') prev.source = 'plan';
  }

  function todoKey(item) { return item.type + '\0' + item.id; }

  /** Latest multi-select scope. Null when the value is absent or unreadable. */
  function normalizeScope(scope) {
    if (scope == null || scope === '') return null;
    if (typeof scope === 'string') return { v: 2, boxes: [scope] };
    if (Array.isArray(scope)) return { v: 2, boxes: scope.filter(x => typeof x === 'string' && x) };
    if (typeof scope !== 'object') return null;
    if (scope.all === true) return { v: 2, all: true };
    if (Array.isArray(scope.boxes)) return { v: 2, boxes: scope.boxes.filter(x => typeof x === 'string' && x) };
    return null;
  }

  /** Prefer the scope saved later. A missing side keeps the side that has one. */
  function mergeScope(local, remote) {
    const l = normalizeScope(local && local.scope);
    const r = normalizeScope(remote && remote.scope);
    if (!l) return r;
    if (!r) return l;
    const lt = Number(local && local.savedAt) || 0;
    const rt = Number(remote && remote.savedAt) || 0;
    return rt > lt ? r : l;
  }

  /**
   * Append `items` to `list`, keeping order and skipping duplicates.
   * Does not mutate `list`.
   */
  function appendTodo(list, items) {
    const out = [];
    const seen = new Map();
    let added = 0;
    const push = (raw, isNew) => {
      const item = normalizeTodoItem(raw);
      if (!item) return;
      const key = todoKey(item);
      if (seen.has(key)) {
        keepHigherFrom(out[seen.get(key)], item.from);
        keepPlanSource(out[seen.get(key)], item.source);
        return;
      }
      seen.set(key, out.length);
      out.push(item);
      if (isNew) added++;
    };
    (Array.isArray(list) ? list : []).forEach(item => push(item, false));
    (Array.isArray(items) ? items : []).forEach(item => push(item, true));
    return { todo: out, added };
  }

  /**
   * First learning-session items: new skills, then mastery challenges.
   * `skipIds` (ids with no questions, or anything else to leave out) are omitted.
   */
  function sessionTodoItems(row, skipIds) {
    const skip = skipIds == null ? null : (skipIds instanceof Set ? skipIds : new Set(skipIds));
    const items = [];
    const push = (type, id) => {
      if (typeof id !== 'string' || !id) return;
      if (skip && skip.has(id)) return;
      items.push({ type, id });
    };
    const practiced = row && Array.isArray(row.practiced) ? row.practiced : [];
    const challenges = row && Array.isArray(row.challenges) ? row.challenges : [];
    practiced.forEach(id => push('skill', id));
    challenges.forEach(c => push('challenge', typeof c === 'string' ? c : (c && c.id)));
    return items;
  }

  /**
   * Map retired to-do ids onto survivors and drop entries that are no longer
   * a live skill when `knownIds` is provided. Does not mutate `todo`.
   */
  function migrateTodoField(todo, retired, knownIds) {
    if (todo == null) return { changed: false };
    if (!Array.isArray(todo)) return { changed: true, todo: [] };
    const map = retired && typeof retired === 'object' ? retired : {};
    const known = knownIds == null ? null : (knownIds instanceof Set ? knownIds : new Set(knownIds));
    const out = [];
    const seen = new Map();
    let changed = false;
    for (const raw of todo) {
      const item = normalizeTodoItem(raw);
      if (!item) { changed = true; continue; }
      const id = resolveSurvivor(item.id, map);
      if (id !== item.id) changed = true;
      if (known && !known.has(id)) { changed = true; continue; }
      const next = { type: item.type, id };
      if (item.from != null) next.from = item.from;
      if (item.source === 'plan') next.source = 'plan';
      const key = item.type + '\0' + id;
      if (seen.has(key)) {
        changed = true;
        keepHigherFrom(out[seen.get(key)], next.from);
        keepPlanSource(out[seen.get(key)], next.source);
        continue;
      }
      seen.set(key, out.length);
      if (todoEntryChanged(raw, next)) changed = true;
      out.push(next);
    }
    if (out.length !== todo.length) changed = true;
    return changed ? { changed: true, todo: out } : { changed: false };
  }

  /** One exam date. A course exam stores `box`. A skill exam stores `skills`. */
  function normalizeExam(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
    let id = typeof raw.id === 'string' ? raw.id.trim() : '';
    if (!id) return null;
    id = id.slice(0, 80);
    const date = typeof raw.date === 'string' ? raw.date : '';
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return null;
    const parts = date.split('-');
    const y = +parts[0], mo = +parts[1], d = +parts[2];
    const dt = new Date(y, mo - 1, d);
    if (dt.getFullYear() !== y || dt.getMonth() !== mo - 1 || dt.getDate() !== d) return null;
    const label = typeof raw.label === 'string' ? raw.label.trim().slice(0, 80) : '';
    const box = typeof raw.box === 'string' ? raw.box.trim().slice(0, 120) : '';
    const out = { id, date };
    if (label) out.label = label;
    if (box) { out.box = box; return out; }
    const skills = [];
    const seen = new Set();
    if (Array.isArray(raw.skills)) {
      for (const sid of raw.skills) {
        if (typeof sid !== 'string') continue;
        const s = sid.trim();
        if (!s || s.length > 120 || seen.has(s)) continue;
        if (skills.length >= 400) break;
        seen.add(s);
        skills.push(s);
      }
    }
    if (!skills.length) return null;
    out.skills = skills;
    return out;
  }

  function normalizeExams(list) {
    if (list == null) return null;
    if (!Array.isArray(list)) return [];
    const out = [];
    const seen = new Set();
    for (const raw of list) {
      const ex = normalizeExam(raw);
      if (!ex || seen.has(ex.id)) continue;
      if (out.length >= 30) break;
      seen.add(ex.id);
      out.push(ex);
    }
    return out;
  }

  function examShapeChanged(raw, next) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return true;
    const keys = Object.keys(raw);
    const want = Object.keys(next);
    if (keys.length !== want.length) return true;
    for (let i = 0; i < keys.length; i++) {
      if (keys[i] !== want[i]) return true;
      const rv = raw[keys[i]], sv = next[keys[i]];
      if (keys[i] === 'skills') {
        if (!Array.isArray(rv) || rv.length !== sv.length) return true;
        for (let j = 0; j < sv.length; j++) if (rv[j] !== sv[j]) return true;
      } else if (rv !== sv) return true;
    }
    return false;
  }

  /**
   * Map retired skill ids on chosen-skill exams and drop entries that are no
   * longer a live skill when `knownIds` is provided. Course exams keep `box`.
   */
  function migrateExamField(exams, retired, knownIds) {
    if (exams == null) return { changed: false };
    if (!Array.isArray(exams)) return { changed: true, exams: [] };
    const map = retired && typeof retired === 'object' ? retired : {};
    const known = knownIds == null ? null : (knownIds instanceof Set ? knownIds : new Set(knownIds));
    const out = [];
    const seenId = new Set();
    let changed = false;
    for (const raw of exams) {
      const ex = normalizeExam(raw);
      if (!ex || seenId.has(ex.id)) { changed = true; continue; }
      seenId.add(ex.id);
      if (ex.skills) {
        const skills = [];
        const seen = new Set();
        for (const sid of ex.skills) {
          const id = resolveSurvivor(sid, map);
          if (id !== sid) changed = true;
          if (known && !known.has(id)) { changed = true; continue; }
          if (seen.has(id)) { changed = true; continue; }
          seen.add(id);
          skills.push(id);
        }
        if (!skills.length) { changed = true; continue; }
        ex.skills = skills;
      }
      if (examShapeChanged(raw, ex)) changed = true;
      if (out.length >= 30) { changed = true; break; }
      out.push(ex);
    }
    if (out.length !== exams.length) changed = true;
    if (!changed) return { changed: false };
    return { changed: true, exams: out };
  }

  /**
   * Union exam dates by id. Local order, then new remote ids.
   * The later save wins when both devices have the same id.
   */
  function mergeExams(localList, remoteList, localAt, remoteAt) {
    const local = normalizeExams(localList);
    const remote = normalizeExams(remoteList);
    if (local == null && remote == null) return null;
    const l = local || [];
    const r = remote || [];
    if (!l.length && !r.length) return null;
    const remoteNewer = (Number(remoteAt) || 0) > (Number(localAt) || 0);
    const chosen = new Map();
    l.forEach(ex => chosen.set(ex.id, ex));
    r.forEach(ex => {
      if (!chosen.has(ex.id) || remoteNewer) chosen.set(ex.id, ex);
    });
    const out = [];
    const seen = new Set();
    l.forEach(ex => {
      if (seen.has(ex.id)) return;
      seen.add(ex.id);
      out.push(chosen.get(ex.id));
    });
    r.forEach(ex => {
      if (seen.has(ex.id)) return;
      seen.add(ex.id);
      out.push(chosen.get(ex.id));
    });
    return out.length ? out.slice(0, 30) : null;
  }

  function finiteNum(n) {
    const x = Number(n);
    return Number.isFinite(x) ? x : null;
  }

  function normalizeCount5(raw) {
    if (!Array.isArray(raw) || raw.length !== 5) return null;
    const out = [];
    for (const n of raw) {
      if (typeof n !== 'number' || !Number.isInteger(n) || n < 0) return null;
      out.push(n);
    }
    return out;
  }

  function normalizePlanItem(raw) {
    const item = normalizeTodoItem(raw);
    if (!item) return null;
    delete item.source;
    if (item.from == null) {
      if (item.type === 'skill') item.from = 0;
      else return null;
    }
    return item;
  }

  /**
   * Saved blended exam plan. Keeps the chart snapshot (minutes, tiers, totals)
   * so the plan tab can draw without simulating again.
   */
  function normalizeSavedPlan(raw) {
    if (raw == null) return null;
    if (typeof raw !== 'object' || Array.isArray(raw)) return null;
    const createdAt = Number(raw.createdAt);
    if (!Number.isFinite(createdAt)) return null;
    const exams = [];
    const seenExam = new Set();
    if (Array.isArray(raw.exams)) {
      for (const ex of raw.exams) {
        if (!ex || typeof ex !== 'object') continue;
        const id = typeof ex.id === 'string' ? ex.id.trim().slice(0, 80) : '';
        const date = typeof ex.date === 'string' ? ex.date : '';
        if (!id || !/^\d{4}-\d{2}-\d{2}$/.test(date) || seenExam.has(id)) continue;
        seenExam.add(id);
        const snap = { id, date };
        if (typeof ex.label === 'string' && ex.label.trim()) snap.label = ex.label.trim().slice(0, 80);
        if (typeof ex.box === 'string' && ex.box.trim()) snap.box = ex.box.trim().slice(0, 120);
        else if (Array.isArray(ex.skills)) {
          const skills = [];
          const seen = new Set();
          for (const sid of ex.skills) {
            if (typeof sid !== 'string') continue;
            const s = sid.trim();
            if (!s || s.length > 120 || seen.has(s)) continue;
            seen.add(s);
            skills.push(s);
            if (skills.length >= 400) break;
          }
          if (skills.length) snap.skills = skills;
        }
        exams.push(snap);
        if (exams.length >= 30) break;
      }
    }
    const sessions = [];
    if (Array.isArray(raw.sessions)) {
      for (const s of raw.sessions) {
        if (!s || typeof s !== 'object' || sessions.length >= 5000) continue;
        const date = typeof s.date === 'string' ? s.date : '';
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) continue;
        const items = [];
        const seenItem = new Set();
        if (Array.isArray(s.items)) {
          for (const it of s.items) {
            const norm = normalizePlanItem(it);
            if (!norm) continue;
            const key = norm.type + '\0' + norm.id + '\0' + norm.from;
            if (seenItem.has(key)) continue;
            seenItem.add(key);
            items.push(norm);
            if (items.length >= 400) break;
          }
        }
        const session = { n: sessions.length + 1, date, items };
        if (typeof s.examId === 'string' && s.examId.trim()) session.examId = s.examId.trim().slice(0, 80);
        const minutes = finiteNum(s.minutes);
        if (minutes != null && minutes >= 0) session.minutes = Math.round(minutes * 100) / 100;
        const cumulative = finiteNum(s.cumulative);
        if (cumulative != null && cumulative >= 0) session.cumulative = Math.round(cumulative * 100) / 100;
        const tiers = normalizeCount5(s.tiers);
        if (tiers) session.tiers = tiers.slice();
        sessions.push(session);
      }
    }
    const out = { createdAt, exams, sessions };
    const practiceMin = finiteNum(raw.practiceMin);
    const challengeMin = finiteNum(raw.challengeMin);
    if (practiceMin != null && practiceMin >= 0) out.practiceMin = practiceMin;
    if (challengeMin != null && challengeMin >= 0) out.challengeMin = challengeMin;
    const startCounts = normalizeCount5(raw.startCounts);
    if (startCounts) out.startCounts = startCounts;
    if (typeof raw.scope === 'number' && Number.isInteger(raw.scope) && raw.scope >= 0) out.scope = raw.scope;
    if (Array.isArray(raw.extras)) {
      const extras = [];
      const seen = new Set();
      for (const id of raw.extras) {
        if (typeof id !== 'string' || !id || id.length > 120 || seen.has(id)) continue;
        seen.add(id);
        extras.push(id);
        if (extras.length >= 400) break;
      }
      if (extras.length) out.extras = extras;
    }
    if (raw.totals && typeof raw.totals === 'object') {
      const totals = {};
      ['sessions', 'practiceCount', 'challengeCount'].forEach(k => {
        const n = finiteNum(raw.totals[k]);
        if (n != null && n >= 0) totals[k] = Math.round(n);
      });
      const totalMinutes = finiteNum(raw.totals.totalMinutes);
      if (totalMinutes != null && totalMinutes >= 0) totals.totalMinutes = Math.round(totalMinutes * 100) / 100;
      if (Object.keys(totals).length) out.totals = totals;
    }
    return out;
  }

  /** The later createdAt wins. A missing side keeps the side that has a plan. */
  function mergeSavedPlan(local, remote) {
    const l = normalizeSavedPlan(local && local.savedPlan);
    const r = normalizeSavedPlan(remote && remote.savedPlan);
    if (!l) return r;
    if (!r) return l;
    return Number(r.createdAt) > Number(l.createdAt) ? r : l;
  }

  function migrateSavedPlanField(savedPlan, retired, knownIds) {
    if (savedPlan == null) return { changed: false };
    const norm = normalizeSavedPlan(savedPlan);
    if (!norm) return { changed: true, savedPlan: null };
    const map = retired && typeof retired === 'object' ? retired : {};
    const known = knownIds == null ? null : (knownIds instanceof Set ? knownIds : new Set(knownIds));
    let changed = false;
    const remap = id => {
      const next = resolveSurvivor(id, map);
      if (next !== id) changed = true;
      return next;
    };
    const sessions = norm.sessions.map(s => {
      const items = [];
      const seen = new Set();
      for (const it of s.items) {
        const id = remap(it.id);
        if (known && !known.has(id)) { changed = true; continue; }
        const key = it.type + '\0' + id + '\0' + it.from;
        if (seen.has(key)) { changed = true; continue; }
        seen.add(key);
        items.push({ type: it.type, id, from: it.from });
      }
      if (items.length !== s.items.length) changed = true;
      const session = { n: s.n, date: s.date, items };
      if (s.examId) session.examId = s.examId;
      if (s.minutes != null) session.minutes = s.minutes;
      if (s.cumulative != null) session.cumulative = s.cumulative;
      if (s.tiers) session.tiers = s.tiers.slice();
      return session;
    });
    const exams = [];
    for (const ex of norm.exams) {
      const next = { id: ex.id, date: ex.date };
      if (ex.label) next.label = ex.label;
      if (ex.box) {
        next.box = ex.box;
        exams.push(next);
        continue;
      }
      if (ex.skills) {
        const skills = [];
        const seen = new Set();
        for (const sid of ex.skills) {
          const id = remap(sid);
          if (known && !known.has(id)) { changed = true; continue; }
          if (seen.has(id)) { changed = true; continue; }
          seen.add(id);
          skills.push(id);
        }
        if (skills.length !== ex.skills.length) changed = true;
        if (skills.length) next.skills = skills;
      }
      exams.push(next);
    }
    let extras = null;
    if (norm.extras) {
      extras = [];
      const seen = new Set();
      for (const id0 of norm.extras) {
        const id = remap(id0);
        if (known && !known.has(id)) { changed = true; continue; }
        if (seen.has(id)) { changed = true; continue; }
        seen.add(id);
        extras.push(id);
      }
      if (extras.length !== norm.extras.length) changed = true;
    }
    const cleaned = {
      createdAt: norm.createdAt,
      exams,
      sessions
    };
    if (norm.practiceMin != null) cleaned.practiceMin = norm.practiceMin;
    if (norm.challengeMin != null) cleaned.challengeMin = norm.challengeMin;
    if (norm.startCounts) cleaned.startCounts = norm.startCounts.slice();
    if (norm.scope != null) cleaned.scope = norm.scope;
    if (extras && extras.length) cleaned.extras = extras;
    if (norm.totals) cleaned.totals = Object.assign({}, norm.totals);
    if (JSON.stringify(cleaned) !== JSON.stringify(norm)) changed = true;
    if (JSON.stringify(norm) !== JSON.stringify(savedPlan)) changed = true;
    if (!changed) return { changed: false };
    return { changed: true, savedPlan: cleaned };
  }

  /** Move progress off retired ids. Does not mutate `progress`.
      Pass `knownIds` (array or Set of live skill ids) to drop to-do entries
      whose ids were removed. Omit it to keep unknown ids. */
  function migrateRetiredProgress(progress, retired, knownIds) {
    if (!progress || typeof progress !== 'object' || !progress.skills || typeof progress.skills !== 'object' || Array.isArray(progress.skills)) {
      return { progress, changed: false };
    }
    const map = retired && typeof retired === 'object' ? retired : {};
    const src = progress.skills;
    const skills = {};
    for (const id of Object.keys(src)) skills[id] = cloneSkill(src[id]);

    let changed = false;
    for (const id of Object.keys(src)) {
      const dest = resolveSurvivor(id, map);
      if (dest === id) continue;
      changed = true;
      const incoming = skills[id];
      delete skills[id];
      if (incoming == null) continue;
      if (skills[dest] == null) skills[dest] = incoming;
      else skills[dest] = mergeSkillRecords(skills[dest], incoming);
    }

    const todoMig = migrateTodoField(progress.todo, map, knownIds);
    const examMig = migrateExamField(progress.exams, map, knownIds);
    const planMig = migrateSavedPlanField(progress.savedPlan, map, knownIds);
    if (!changed && !todoMig.changed && !examMig.changed && !planMig.changed) return { progress, changed: false };
    const next = { ...progress };
    if (changed) next.skills = skills;
    if (todoMig.changed) next.todo = todoMig.todo;
    if (examMig.changed) next.exams = examMig.exams;
    if (planMig.changed) {
      if (planMig.savedPlan) next.savedPlan = planMig.savedPlan;
      else delete next.savedPlan;
    }
    return { progress: next, changed: true };
  }

  /**
   * Cross-device merge. Skills keep the higher tier. To-do lists concatenate
   * (local order, then new remote items). Scope keeps the later save.
   * A null side is returned unchanged so older callers stay valid.
   */
  function mergeProgress(local, remote) {
    if (!local || !local.skills) return remote;
    if (!remote || !remote.skills) return local;

    const merged = { version: 1, skills: {} };
    const allIds = new Set([...Object.keys(local.skills), ...Object.keys(remote.skills)]);
    for (const id of allIds) {
      const m = mergeSkillRecords(local.skills[id], remote.skills[id]);
      if (m) merged.skills[id] = m;
    }
    if (Array.isArray(local.todo) || Array.isArray(remote.todo)) {
      merged.todo = appendTodo(local.todo, remote.todo).todo;
    }
    const scope = mergeScope(local, remote);
    if (scope) merged.scope = scope;
    const exams = mergeExams(local.exams, remote.exams, local.savedAt, remote.savedAt);
    if (exams) merged.exams = exams;
    const savedPlan = mergeSavedPlan(local, remote);
    if (savedPlan) merged.savedPlan = savedPlan;
    const lt = Number(local.savedAt);
    const rt = Number(remote.savedAt);
    if (Number.isFinite(lt) || Number.isFinite(rt)) {
      merged.savedAt = Math.max(Number.isFinite(lt) ? lt : 0, Number.isFinite(rt) ? rt : 0);
    }
    return merged;
  }

  /**
   * Migrate each side of a local/remote sync, then merge.
   * `mergeProgress` is the existing cross-device merge (null-safe).
   */
  function combineMigratedProgress(local, remote, retired, mergeProgress) {
    const l = migrateRetiredProgress(local, retired);
    const r = migrateRetiredProgress(remote, retired);
    const merged = mergeProgress(l.progress, r.progress);
    const again = migrateRetiredProgress(merged, retired);
    return {
      progress: again.progress,
      changed: !!(l.changed || r.changed || again.changed)
    };
  }

  return {
    mergeSkillRecords, migrateRetiredProgress, combineMigratedProgress,
    normalizeTodoItem, normalizeScope, mergeScope, mergeProgress, appendTodo, sessionTodoItems,
    normalizeExam, normalizeExams, mergeExams, normalizeSavedPlan, mergeSavedPlan
  };
});
