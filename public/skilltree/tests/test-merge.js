/**
 * Unit tests for Skillgrove merge functions.
 * 
 * Run: node test-merge.js
 */
const assert = require('assert');
const { mergeSkillRecords: mergeSkill, mergeProgress, appendTodo, sessionTodoItems, normalizeScope, mergeScope, normalizeExam, mergeExams } = require('../migrate.js');
const Sim = require('../simcore.js');

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
  assert.strictEqual(result.exams, undefined);
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

test('appendTodo keeps the higher starting tier when the same line is merged', () => {
  const low = [{ type: 'challenge', id: 'bode', from: 1 }];
  const high = [{ type: 'challenge', id: 'bode', from: 2 }];
  const up = appendTodo(low, high);
  assert.strictEqual(up.added, 0);
  assert.deepStrictEqual(up.todo, [{ type: 'challenge', id: 'bode', from: 2 }]);
  assert.deepStrictEqual(appendTodo(high, low).todo, [{ type: 'challenge', id: 'bode', from: 2 }]);
  assert.deepStrictEqual(appendTodo([{ type: 'skill', id: 'bode' }], [{ type: 'skill', id: 'bode', from: 0 }]).todo, [
    { type: 'skill', id: 'bode', from: 0 }
  ]);
  const junk = [{ type: 'skill', id: 'bode', from: 1.5, extra: true }];
  assert.deepStrictEqual(appendTodo([], junk).todo, [{ type: 'skill', id: 'bode' }]);
});

test('mergeExams keeps both devices and lets the later save win the same id', () => {
  const local = [{ id: 'a', date: '2026-12-01', box: 'me132' }, { id: 'b', date: '2026-12-02', skills: ['bode'] }];
  const remote = [{ id: 'a', date: '2026-12-15', label: 'Final', skills: ['tf'] }, { id: 'c', date: '2026-11-20', skills: ['tf', 'tf'] }];
  const merged = mergeExams(local, remote, 1, 2);
  assert.deepStrictEqual(merged, [
    { id: 'a', date: '2026-12-15', label: 'Final', skills: ['tf'] },
    { id: 'b', date: '2026-12-02', skills: ['bode'] },
    { id: 'c', date: '2026-11-20', skills: ['tf'] }
  ]);
  assert.deepStrictEqual(mergeExams(local, remote, 5, 2)[0], { id: 'a', date: '2026-12-01', box: 'me132' });
  const withSkills = { version: 1, savedAt: 2, skills: { bode: { tier: 1, lastPracticed: now, history: [] } }, exams: remote };
  const kept = mergeProgress(
    { version: 1, savedAt: 1, skills: { bode: { tier: 1, lastPracticed: now, history: [] } }, exams: local },
    withSkills
  );
  assert.strictEqual(kept.exams[0].date, '2026-12-15');
  assert.strictEqual(mergeProgress(
    { version: 1, skills: { bode: { tier: 1, lastPracticed: now, history: [] } }, exams: local },
    { version: 1, skills: { bode: { tier: 1, lastPracticed: now, history: [] } } }
  ).exams.length, 2);
  assert.strictEqual(normalizeExam({ id: 'x', date: '2026-02-31', box: 'me132' }), null);
  assert.strictEqual(mergeExams(null, null, 0, 0), null);
});

test('study days stop before the exam and sessions spread across them', () => {
  assert.deepStrictEqual(Sim.studyDates('2026-11-12', '2026-11-19'), [
    '2026-11-12', '2026-11-13', '2026-11-14', '2026-11-15', '2026-11-16', '2026-11-17', '2026-11-18'
  ]);
  assert.deepStrictEqual(Sim.studyDates('2026-11-12', '2026-11-13'), ['2026-11-12']);
  assert.deepStrictEqual(Sim.studyDates('2026-11-12', '2026-11-12'), ['2026-11-12']);
  assert.deepStrictEqual(Sim.studyDates('2026-11-12', '2026-11-10'), ['2026-11-12']);
  assert.strictEqual(Sim.studyDayCount('2026-01-01', '2040-01-01'), Sim.MAX_STUDY_DAYS);
  assert.strictEqual(Sim.examCountdown('2026-11-12', '2026-11-18').text, 'Exam in 6 days');
  assert.strictEqual(Sim.examCountdown('2026-11-12', '2026-11-13').text, 'Exam tomorrow');
  assert.strictEqual(Sim.examCountdown('2026-11-12', '2026-11-12').text, 'Exam today');
  assert.strictEqual(Sim.examCountdown('2026-11-12', '2026-11-11').text, 'Exam was yesterday');
  assert.strictEqual(Sim.examCountdown('2026-11-12', '2026-11-10').text, 'Exam was 2 days ago');
  assert.deepStrictEqual(Sim.spreadSessionIndexes(3, 7), [[0], [], [], [1], [], [], [2]]);
  assert.deepStrictEqual(Sim.spreadSessionIndexes(4, 2), [[0, 1], [2, 3]]);
  assert.deepStrictEqual(Sim.spreadSessionIndexes(1, 5), [[0], [], [], [], []]);
  assert.deepStrictEqual(Sim.spreadSessionIndexes(0, 3), [[], [], []]);
  assert.strictEqual(Sim.nextSessionDay(3, 7, 0), 3);
  const items = [
    { type: 'skill', id: 'a' },
    { type: 'challenge', id: 'c' },
    { type: 'challenge', id: 'b' },
    { type: 'skill', id: 'd' }
  ];
  assert.deepStrictEqual(Sim.orderSessionItems(items, { b: 10, c: 50 }), [
    { type: 'skill', id: 'a' },
    { type: 'skill', id: 'd' },
    { type: 'challenge', id: 'b' },
    { type: 'challenge', id: 'c' }
  ]);
  assert.deepStrictEqual(Sim.orderSessionItems(items, {}).filter(it => it.type === 'challenge').map(it => it.id), ['c', 'b']);
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
