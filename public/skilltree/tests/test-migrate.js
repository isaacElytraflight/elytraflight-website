/**
 * Progress migration for retired skill ids.
 * Run: node test-migrate.js
 */
const assert = require('assert');
const { migrateRetiredProgress, combineMigratedProgress, mergeSkillRecords } = require('../migrate.js');

const RETIRED = {
  saturation: 'square-law',
  'bjt-gain': 'bjt-action',
  clm: 'ro',
  'op-point': 'cs-intro',
  'ss-steps': 'ss-model',
  'ss-4term': 'body-effect',
  'body-amp': 'cd',
  'cd-real': 'cd',
  'z-match': 'two-port',
  'mirror-ratio': 'mirror',
  'mirror-ro': 'mirror',
  'cs-miller': 'miller',
  'dm-cm': 'half-circuit',
  'cm-gain': 'cmrr',
  'pmos-ss': 'pmos'
};

const now = 1_700_000_000_000;
const DAY = 86400000;

function skill(tier, lastPracticed, history) {
  return { tier, lastPracticed, history: history || [] };
}

function progress(skills, extra) {
  return { version: 1, savedAt: now - DAY, ...extra, skills };
}

let passed = 0, failed = 0;
function test(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
    passed++;
  } catch (e) {
    console.log(`✗ ${name}`);
    console.error('  ', e.message);
    failed++;
  }
}

console.log('\n=== Retired-id progress migration ===\n');

test('retired-only progress moves onto the survivor', () => {
  const input = progress({ saturation: skill(2, now - 3 * DAY, [{ t: 10, passed: true }]) });
  const { progress: out, changed } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(changed, true);
  assert.strictEqual(out.skills.saturation, undefined);
  assert.strictEqual(out.skills['square-law'].tier, 2);
  assert.strictEqual(out.skills['square-law'].lastPracticed, now - 3 * DAY);
  assert.deepStrictEqual(out.skills['square-law'].history, [{ t: 10, passed: true }]);
  assert.strictEqual(out.savedAt, input.savedAt);
});

test('does not mutate the input record', () => {
  const input = progress({
    saturation: skill(2, now - DAY, [{ t: 1, passed: true }]),
    'square-law': skill(1, now - 2 * DAY, [{ t: 2, passed: false }])
  });
  const snapshot = JSON.parse(JSON.stringify(input));
  migrateRetiredProgress(input, RETIRED);
  assert.deepStrictEqual(input, snapshot);
});

test('keeps the higher tier when the survivor already has progress', () => {
  const input = progress({
    saturation: skill(2, now - DAY, [{ t: 1, passed: true }]),
    'square-law': skill(4, now - 5 * DAY, [{ t: 2, passed: true }])
  });
  const { progress: out } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(out.skills['square-law'].tier, 4);
  assert.strictEqual(out.skills.saturation, undefined);
});

test('retired tier wins when it is higher, without dropping survivor history', () => {
  const input = progress({
    'bjt-gain': skill(4, now - 4 * DAY, [{ t: 1, passed: true }]),
    'bjt-action': skill(1, now - DAY, [{ t: 2, passed: false }])
  });
  const { progress: out } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(out.skills['bjt-action'].tier, 4);
  assert.strictEqual(out.skills['bjt-action'].lastPracticed, now - DAY);
  assert.deepStrictEqual(out.skills['bjt-action'].history.map(h => h.t), [1, 2]);
});

test('latest practice timestamp wins even when it is on the lower tier', () => {
  const input = progress({
    clm: skill(1, now, [{ t: 3, passed: false }]),
    ro: skill(3, now - 2 * DAY, [{ t: 4, passed: true }])
  });
  const { progress: out } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(out.skills.ro.tier, 3);
  assert.strictEqual(out.skills.ro.lastPracticed, now);
});

test('null practice time does not erase a real timestamp', () => {
  const input = progress({
    'op-point': skill(2, null, []),
    'cs-intro': skill(1, now - DAY, [])
  });
  const { progress: out } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(out.skills['cs-intro'].tier, 2);
  assert.strictEqual(out.skills['cs-intro'].lastPracticed, now - DAY);
});

test('two retired ids merge into one survivor that already has progress', () => {
  const input = progress({
    'body-amp': skill(2, now - 3 * DAY, [{ t: 1, passed: true }]),
    'cd-real': skill(4, now - DAY, [{ t: 2, passed: true }]),
    cd: skill(3, now - 2 * DAY, [{ t: 3, passed: false }])
  });
  const { progress: out } = migrateRetiredProgress(input, RETIRED);
  assert.deepStrictEqual(Object.keys(out.skills).sort(), ['cd']);
  assert.strictEqual(out.skills.cd.tier, 4);
  assert.strictEqual(out.skills.cd.lastPracticed, now - DAY);
  assert.deepStrictEqual(out.skills.cd.history.map(h => h.t), [1, 2, 3]);
});

test('duplicate history timestamps are kept once', () => {
  const input = progress({
    'mirror-ratio': skill(2, now, [{ t: 5, passed: true, note: 'a' }]),
    'mirror-ro': skill(2, now - DAY, [{ t: 5, passed: false, note: 'b' }]),
    mirror: skill(1, now - 2 * DAY, [{ t: 6, passed: true }])
  });
  const { progress: out } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(out.skills.mirror.history.length, 2);
  assert.strictEqual(out.skills.mirror.tier, 2);
});

test('history is capped at 60 after the merge', () => {
  const older = Array.from({ length: 40 }, (_, i) => ({ t: i, passed: true }));
  const newer = Array.from({ length: 40 }, (_, i) => ({ t: 1000 + i, passed: true }));
  const input = progress({
    'ss-steps': skill(1, now, older),
    'ss-model': skill(2, now, newer)
  });
  const { progress: out } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(out.skills['ss-model'].history.length, 60);
  assert.strictEqual(out.skills['ss-model'].history[0].t, 20);
  assert.strictEqual(out.skills['ss-model'].history[59].t, 1039);
});

test('unrelated and unknown ids are preserved', () => {
  const input = progress({
    bode: skill(3, now, []),
    'future-skill': skill(1, now - DAY, [])
  });
  const { progress: out, changed } = migrateRetiredProgress(input, RETIRED);
  assert.strictEqual(changed, false);
  assert.strictEqual(out, input);
  assert.strictEqual(out.skills.bode.tier, 3);
  assert.strictEqual(out.skills['future-skill'].tier, 1);
});

test('idempotent: a second pass changes nothing', () => {
  const input = progress({
    saturation: skill(4, now - 2 * DAY, [{ t: 1, passed: true }]),
    'square-law': skill(2, now, [{ t: 2, passed: true }]),
    'pmos-ss': skill(3, now - DAY, [{ t: 3, passed: true }]),
    bode: skill(1, now - 4 * DAY, [])
  });
  const first = migrateRetiredProgress(input, RETIRED);
  const second = migrateRetiredProgress(first.progress, RETIRED);
  assert.strictEqual(first.changed, true);
  assert.strictEqual(second.changed, false);
  assert.strictEqual(second.progress, first.progress);
  assert.deepStrictEqual(second.progress.skills, first.progress.skills);
  assert.strictEqual(first.progress.skills['square-law'].tier, 4);
  assert.strictEqual(first.progress.skills['square-law'].lastPracticed, now);
  assert.strictEqual(first.progress.skills.pmos.tier, 3);
  assert.strictEqual(first.progress.skills.bode.tier, 1);
});

test('chains of retired ids resolve to the final survivor', () => {
  const map = { a: 'b', b: 'c' };
  const input = progress({
    a: skill(1, now - 2 * DAY, [{ t: 1, passed: true }]),
    b: skill(3, now - DAY, [{ t: 2, passed: true }])
  });
  const { progress: out } = migrateRetiredProgress(input, map);
  assert.deepStrictEqual(Object.keys(out.skills), ['c']);
  assert.strictEqual(out.skills.c.tier, 3);
  assert.strictEqual(out.skills.c.lastPracticed, now - DAY);
  const again = migrateRetiredProgress(out, map);
  assert.strictEqual(again.changed, false);
});

test('a cycle does not loop and leaves the ids unmoved', () => {
  const input = progress({ a: skill(2, now, []), b: skill(4, now, []) });
  const { progress: out, changed } = migrateRetiredProgress(input, { a: 'b', b: 'a' });
  assert.strictEqual(changed, false);
  assert.strictEqual(out.skills.a.tier, 2);
  assert.strictEqual(out.skills.b.tier, 4);
});

test('null, empty, and already-clean progress are unchanged', () => {
  assert.deepStrictEqual(migrateRetiredProgress(null, RETIRED), { progress: null, changed: false });
  assert.deepStrictEqual(migrateRetiredProgress(undefined, RETIRED), { progress: undefined, changed: false });
  const empty = progress({});
  const res = migrateRetiredProgress(empty, RETIRED);
  assert.strictEqual(res.changed, false);
  assert.strictEqual(res.progress, empty);
  assert.strictEqual(migrateRetiredProgress(progress({ bode: skill(1, now, []) }), null).changed, false);
});

function mergeProgress(local, remote) {
  if (!local || !local.skills) return remote;
  if (!remote || !remote.skills) return local;
  const merged = { version: 1, skills: {} };
  for (const id of new Set([...Object.keys(local.skills), ...Object.keys(remote.skills)])) {
    const m = mergeSkillRecords(local.skills[id], remote.skills[id]);
    if (m) merged.skills[id] = m;
  }
  return merged;
}

test('sync merge migrates both sides before combining, and does not drop either device', () => {
  const local = progress({
    saturation: skill(2, now - 5 * DAY, [{ t: 1, passed: true }]),
    bode: skill(4, now - DAY, [{ t: 9, passed: true }])
  });
  const remote = progress({
    'square-law': skill(3, now - 2 * DAY, [{ t: 2, passed: true }]),
    saturation: skill(1, now, [{ t: 3, passed: false }]),
    'cs-miller': skill(2, now - 3 * DAY, [{ t: 4, passed: true }])
  });
  const once = combineMigratedProgress(local, remote, RETIRED, mergeProgress);
  assert.strictEqual(once.changed, true);
  assert.strictEqual(once.progress.skills.saturation, undefined);
  assert.strictEqual(once.progress.skills['cs-miller'], undefined);
  assert.strictEqual(once.progress.skills['square-law'].tier, 3);
  assert.strictEqual(once.progress.skills['square-law'].lastPracticed, now);
  assert.deepStrictEqual(once.progress.skills['square-law'].history.map(h => h.t), [1, 2, 3]);
  assert.strictEqual(once.progress.skills.miller.tier, 2);
  assert.strictEqual(once.progress.skills.bode.tier, 4);

  const twice = combineMigratedProgress(once.progress, once.progress, RETIRED, mergeProgress);
  assert.strictEqual(twice.changed, false);
  assert.deepStrictEqual(twice.progress.skills, once.progress.skills);
});

test('sync with only a remote retired id still migrates and is idempotent', () => {
  const remote = progress({ 'dm-cm': skill(3, now - DAY, [{ t: 7, passed: true }]) });
  const once = combineMigratedProgress(null, remote, RETIRED, mergeProgress);
  assert.strictEqual(once.progress.skills['half-circuit'].tier, 3);
  assert.strictEqual(once.progress.skills['dm-cm'], undefined);
  const twice = combineMigratedProgress(once.progress, null, RETIRED, mergeProgress);
  assert.strictEqual(twice.changed, false);
  assert.strictEqual(twice.progress.skills['half-circuit'].tier, 3);
});

test('sync does not wipe a survivor when the other device only has a lower retired tier', () => {
  const local = progress({ mirror: skill(4, now - 2 * DAY, [{ t: 1, passed: true }]) });
  const remote = progress({ 'mirror-ro': skill(1, now, [{ t: 2, passed: false }]) });
  const { progress: out } = combineMigratedProgress(local, remote, RETIRED, mergeProgress);
  assert.strictEqual(out.skills.mirror.tier, 4);
  assert.strictEqual(out.skills.mirror.lastPracticed, now);
  assert.deepStrictEqual(out.skills.mirror.history.map(h => h.t), [1, 2]);
  assert.strictEqual(out.skills['mirror-ro'], undefined);
});

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed > 0 ? 1 : 0);
