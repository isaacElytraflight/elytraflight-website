/* Skillgrove progress migration for retired skill ids, to-do items, and scope.
   Works in the browser (window.SkillgroveMigrate) and in Node (module.exports).
   Retired progress moves onto the survivor: higher mastery tier, later practice
   time, and the union of attempt history.    To-do entries follow the same map and,
   when a catalog of live skill ids is provided, entries that no longer exist are
   dropped. A starting tier (`from`, an integer 0–4) is kept when present.
   Running it again changes nothing. */
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

  function normalizeTodoItem(item) {
    if (!item || typeof item !== 'object') return null;
    const type = item.type === 'skill' || item.type === 'challenge' ? item.type : null;
    if (!type || typeof item.id !== 'string' || !item.id) return null;
    const out = { type, id: item.id };
    const from = readTodoFrom(item);
    if (from != null) out.from = from;
    return out;
  }

  function todoEntryChanged(raw, next) {
    if (!raw || typeof raw !== 'object') return true;
    if (raw.type !== next.type || raw.id !== next.id) return true;
    const rawFrom = readTodoFrom(raw);
    const nextFrom = next.from == null ? null : next.from;
    if (rawFrom !== nextFrom) return true;
    if (raw.from !== undefined && rawFrom == null) return true;
    for (const k of Object.keys(raw)) {
      if (k !== 'type' && k !== 'id' && k !== 'from') return true;
    }
    return false;
  }

  function keepHigherFrom(prev, from) {
    if (from == null) return;
    if (prev.from == null || from > prev.from) prev.from = from;
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
      const key = item.type + '\0' + id;
      if (seen.has(key)) {
        changed = true;
        keepHigherFrom(out[seen.get(key)], next.from);
        continue;
      }
      seen.set(key, out.length);
      if (todoEntryChanged(raw, next)) changed = true;
      out.push(next);
    }
    if (out.length !== todo.length) changed = true;
    return changed ? { changed: true, todo: out } : { changed: false };
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
    if (!changed && !todoMig.changed) return { progress, changed: false };
    const next = { ...progress };
    if (changed) next.skills = skills;
    if (todoMig.changed) next.todo = todoMig.todo;
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
    normalizeTodoItem, normalizeScope, mergeScope, mergeProgress, appendTodo, sessionTodoItems
  };
});
