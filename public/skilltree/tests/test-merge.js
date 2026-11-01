/**
 * Unit tests for Skillgrove merge functions.
 * 
 * Run: node test-merge.js
 */
const assert = require('assert');
const { mergeSkillRecords: mergeSkill, mergeProgress, appendTodo, sessionTodoItems, normalizeScope, mergeScope } = require('../migrate.js');

const mergeTiming = (local, remote) => {
  if (!local) return remote;
  if (!remote) return local;
  
  const merged = {};
  for (const key of ['practice', 'challenge']) {
    const lArr = Array.isArray(local[key]) ? local[key] : [];
    const rArr = Array.isArray(remote[key]) ? remote[key] : [];
    const seen = new Set(lArr.map(s => s.t));
    merged[key] = [...lArr, ...rArr.filter(s => !seen.has(s.t))].sort((a, b) => a.t - b.t).slice(-50);
  }
  return merged;
};

const now = Date.now();
const DAY = 86400000;

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

console.log('\n=== Merge Function Unit Tests ===\n');

test('mergeSkill: null + null = null', () => {
  assert.strictEqual(mergeSkill(null, null), null);
});

test('mergeSkill: local only returns local', () => {
  const local = { tier: 2, lastPracticed: now, history: [] };
  const result = mergeSkill(local, null);
  assert.deepStrictEqual(result, local);
});

test('mergeSkill: remote only returns remote', () => {
  const remote = { tier: 3, lastPracticed: now, history: [] };
  const result = mergeSkill(null, remote);
  assert.deepStrictEqual(result, remote);
});

test('mergeSkill: keeps higher tier', () => {
  const local = { tier: 2, lastPracticed: now - DAY, history: [] };
  const remote = { tier: 4, lastPracticed: now - 2 * DAY, history: [] };
  const result = mergeSkill(local, remote);
  assert.strictEqual(result.tier, 4);
});

test('mergeSkill: keeps latest lastPracticed', () => {
  const local = { tier: 2, lastPracticed: now - DAY, history: [] };
  const remote = { tier: 1, lastPracticed: now, history: [] };
  const result = mergeSkill(local, remote);
  assert.strictEqual(result.lastPracticed, now);
});

test('mergeSkill: merges and dedupes history by timestamp', () => {
  const local = { tier: 2, lastPracticed: now, history: [
    { t: now - 3 * DAY, passed: true },
    { t: now - DAY, passed: false }
  ]};
  const remote = { tier: 2, lastPracticed: now, history: [
    { t: now - 2 * DAY, passed: true },
    { t: now - DAY, passed: false }
  ]};
  const result = mergeSkill(local, remote);
  assert.strictEqual(result.history.length, 3);
  assert.deepStrictEqual(result.history.map(h => h.t), [now - 3 * DAY, now - 2 * DAY, now - DAY]);
});

test('mergeSkill: limits history to 60 entries', () => {
  const makeHistory = (start, count) => Array.from({ length: count }, (_, i) => ({ t: start + i * 1000, passed: true }));
  const local = { tier: 2, lastPracticed: now, history: makeHistory(0, 40) };
  const remote = { tier: 2, lastPracticed: now, history: makeHistory(40000, 40) };
  const result = mergeSkill(local, remote);
  assert.strictEqual(result.history.length, 60);
});

test('mergeProgress: null local returns remote', () => {
  const remote = { version: 1, skills: { bode: { tier: 2, lastPracticed: now, history: [] } } };
  const result = mergeProgress(null, remote);
  assert.deepStrictEqual(result, remote);
});

test('mergeProgress: null remote returns local', () => {
  const local = { version: 1, skills: { bode: { tier: 2, lastPracticed: now, history: [] } } };
  const result = mergeProgress(local, null);
  assert.deepStrictEqual(result, local);
});

test('mergeProgress: merges skills from both', () => {
  const local = { version: 1, skills: { 
    bode: { tier: 2, lastPracticed: now - DAY, history: [] },
    tf: { tier: 1, lastPracticed: now, history: [] }
  }};
  const remote = { version: 1, skills: { 
    bode: { tier: 3, lastPracticed: now, history: [] },
    phasors: { tier: 4, lastPracticed: now, history: [] }
  }};
  const result = mergeProgress(local, remote);
  assert.strictEqual(Object.keys(result.skills).length, 3);
  assert.strictEqual(result.skills.bode.tier, 3);
  assert.strictEqual(result.skills.tf.tier, 1);
  assert.strictEqual(result.skills.phasors.tier, 4);
});

test('mergeTiming: null local returns remote', () => {
  const remote = { practice: [{ t: now, d: 10 }], challenge: [] };
  const result = mergeTiming(null, remote);
  assert.deepStrictEqual(result, remote);
});

test('mergeTiming: null remote returns local', () => {
  const local = { practice: [{ t: now, d: 10 }], challenge: [] };
  const result = mergeTiming(local, null);
  assert.deepStrictEqual(result, local);
});

test('mergeTiming: dedupes by timestamp', () => {
  const local = { practice: [{ t: 1000, d: 10 }, { t: 2000, d: 15 }], challenge: [] };
  const remote = { practice: [{ t: 2000, d: 15 }, { t: 3000, d: 20 }], challenge: [] };
  const result = mergeTiming(local, remote);
  assert.strictEqual(result.practice.length, 3);
  assert.deepStrictEqual(result.practice.map(s => s.t), [1000, 2000, 3000]);
});

test('mergeProgress: keeps an older save that has no todo or scope', () => {
  const local = { version: 1, skills: { bode: { tier: 1, lastPracticed: now, history: [] } } };
  const remote = { version: 1, skills: { tf: { tier: 2, lastPracticed: now, history: [] } } };
  const result = mergeProgress(local, remote);
  assert.strictEqual(result.todo, undefined);
  assert.strictEqual(result.scope, undefined);
  assert.strictEqual(result.skills.bode.tier, 1);
  assert.strictEqual(result.skills.tf.tier, 2);
});

test('mergeProgress: concatenates todo lists, local order first, and dedupes', () => {
  const local = { version: 1, savedAt: now - DAY, skills: { bode: { tier: 1, lastPracticed: now, history: [] } },
    todo: [{ type: 'skill', id: 'bode' }, { type: 'challenge', id: 'tf' }] };
  const remote = { version: 1, savedAt: now, skills: { bode: { tier: 2, lastPracticed: now, history: [] } },
    todo: [{ type: 'challenge', id: 'tf' }, { type: 'skill', id: 'phasors' }] };
  const result = mergeProgress(local, remote);
  assert.deepStrictEqual(result.todo, [
    { type: 'skill', id: 'bode' },
    { type: 'challenge', id: 'tf' },
    { type: 'skill', id: 'phasors' }
  ]);
  assert.strictEqual(result.skills.bode.tier, 2);
});

test('mergeProgress: newer savedAt wins the scope, and a missing scope does not wipe one', () => {
  const older = { version: 1, savedAt: now - DAY, scope: { v: 2, boxes: ['ee105-ch2'] }, skills: { bode: { tier: 1, lastPracticed: now, history: [] } } };
  const newer = { version: 1, savedAt: now, scope: { v: 2, all: true }, skills: { bode: { tier: 1, lastPracticed: now, history: [] } } };
  assert.deepStrictEqual(mergeProgress(older, newer).scope, { v: 2, all: true });
  assert.deepStrictEqual(mergeProgress(newer, older).scope, { v: 2, all: true });
  const noScope = { version: 1, savedAt: now + DAY, skills: { bode: { tier: 1, lastPracticed: now, history: [] } } };
  assert.deepStrictEqual(mergeProgress(older, noScope).scope, { v: 2, boxes: ['ee105-ch2'] });
  assert.deepStrictEqual(normalizeScope('ee105-ch2'), { v: 2, boxes: ['ee105-ch2'] });
  assert.strictEqual(mergeScope(null, null), null);
});

test('session queue: skills before challenges, skip ids, append dedupes without mutating', () => {
  const row = {
    practiced: ['soon', 'alpha', 'beta'],
    challenges: [{ id: 'gamma', from: 1, to: 2 }, { id: 'soon' }, 'beta']
  };
  const items = sessionTodoItems(row, new Set(['soon']));
  assert.deepStrictEqual(items, [
    { type: 'skill', id: 'alpha' },
    { type: 'skill', id: 'beta' },
    { type: 'challenge', id: 'gamma' },
    { type: 'challenge', id: 'beta' }
  ]);
  const existing = [{ type: 'skill', id: 'alpha' }];
  const snapshot = JSON.parse(JSON.stringify(existing));
  const { todo, added } = appendTodo(existing, items);
  assert.strictEqual(added, 3);
  assert.deepStrictEqual(existing, snapshot);
  assert.deepStrictEqual(todo, [
    { type: 'skill', id: 'alpha' },
    { type: 'skill', id: 'beta' },
    { type: 'challenge', id: 'gamma' },
    { type: 'challenge', id: 'beta' }
  ]);
  assert.strictEqual(appendTodo(todo, items).added, 0);
});

test('mergeTiming: limits to 50 entries per category', () => {
  const makeSamples = (start, count) => Array.from({ length: count }, (_, i) => ({ t: start + i, d: 10 }));
  const local = { practice: makeSamples(0, 30), challenge: makeSamples(0, 30) };
  const remote = { practice: makeSamples(30, 30), challenge: makeSamples(30, 30) };
  const result = mergeTiming(local, remote);
  assert.strictEqual(result.practice.length, 50);
  assert.strictEqual(result.challenge.length, 50);
});

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed > 0 ? 1 : 0);
