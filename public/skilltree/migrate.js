/* Skillgrove progress migration for retired skill ids.
   Works in the browser (window.SkillgroveMigrate) and in Node (module.exports).
   Retired progress moves onto the survivor: higher mastery tier, later practice
   time, and the union of attempt history. Running it again changes nothing. */
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

  /** Move progress off retired ids. Does not mutate `progress`. */
  function migrateRetiredProgress(progress, retired) {
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

    if (!changed) return { progress, changed: false };
    return { progress: { ...progress, skills }, changed: true };
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

  return { mergeSkillRecords, migrateRetiredProgress, combineMigratedProgress };
});
