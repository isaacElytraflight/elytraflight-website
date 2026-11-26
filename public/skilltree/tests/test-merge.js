/**
 * Unit tests for Elytraflight's Skill Tree merge functions.
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

test('blended exam plans interleave and never pass an exam date', () => {
  const today = '2026-11-20';
  const eeDate = '2026-11-27';
  const meDate = '2026-12-04';
  const eeRows = [0, 1, 2, 3].map(i => ({ practiced: ['shared', 'ee' + i], challenges: [{ id: 'eeC' + i, from: 1 }] }));
  const meRows = [0, 1, 2, 3].map(i => ({ practiced: ['shared', 'me' + i], challenges: [{ id: 'meC' + i, from: 1 }] }));
  const sessions = Sim.mergeExamSessionPlans([
    { examId: 'ee105', examDate: eeDate, savedIndex: 0, today, rows: eeRows },
    { examId: 'me132', examDate: meDate, savedIndex: 1, today, rows: meRows }
  ]);
  const ee = sessions.filter(s => s.examId === 'ee105');
  const me = sessions.filter(s => s.examId === 'me132');
  assert(ee.length > 0 && me.length > 0);
  assert(ee.every(s => s.date < eeDate), 'an EE105 session lands on or after its exam');
  assert(me.every(s => s.date < meDate), 'an ME132 session lands on or after its exam');
  assert(me.some(s => s.date <= ee[ee.length - 1].date), 'ME132 should appear before EE105 is finished');
  assert.strictEqual(me[0].date, ee[0].date, 'both exams start on the early study days');
  const shared = sessions.filter(s => s.items.some(it => it.type === 'skill' && it.id === 'shared'));
  assert.strictEqual(shared.length, 1);
  assert.strictEqual(shared[0].examId, 'ee105');
  const dates = sessions.map(s => s.date);
  const sorted = dates.slice().sort();
  assert.deepStrictEqual(dates, sorted, 'sessions are ordered by date');
});

test('plan pace covers behind, today, caught up, and ahead', () => {
  const today = '2026-11-20';
  assert.deepStrictEqual(Sim.planPaceStatus([{ date: '2026-11-19', complete: false }, { date: '2026-11-18', complete: false }], today), {
    kind: 'behind', n: 2, text: '2 sessions behind'
  });
  assert.strictEqual(Sim.planPaceStatus([{ date: '2026-11-19', complete: false }], today).text, '1 session behind');
  assert.deepStrictEqual(Sim.planPaceStatus([{ date: today, complete: false }, { date: today, complete: false }], today), {
    kind: 'today', n: 2, text: '2 sessions left to complete today'
  });
  assert.strictEqual(Sim.planPaceStatus([{ date: today, complete: false }], today).text, '1 session left to complete today');
  assert.deepStrictEqual(Sim.planPaceStatus([{ date: '2026-11-19', complete: true }, { date: today, complete: true }], today), {
    kind: 'caught', n: 0, text: '✓ all caught up!'
  });
  assert.deepStrictEqual(Sim.planPaceStatus([{ date: '2026-11-21', complete: true }, { date: '2026-11-22', complete: true }], today), {
    kind: 'ahead', n: 2, text: '⭐ 2 sessions ahead'
  });
  assert.strictEqual(Sim.planPaceStatus([{ date: '2026-11-21', complete: true }], today).text, '⭐ 1 session ahead');
  assert.strictEqual(Sim.planPaceStatus([
    { date: '2026-11-19', complete: false },
    { date: today, complete: false },
    { date: '2026-11-21', complete: true }
  ], today).kind, 'behind', 'behind wins over today and ahead');
});

test('a saved plan stays fresh when an exam date simply passes', () => {
  const saved = [
    { id: 'ee', date: '2026-11-27', box: 'ee105-ucb' },
    { id: 'me', date: '2026-12-04', box: 'me132', label: 'Final' }
  ];
  const later = '2026-11-28';
  assert.strictEqual(Sim.savedExamPlanStale(saved, [
    { id: 'ee', date: '2026-11-27', box: 'ee105-ucb' },
    { id: 'me', date: '2026-12-04', box: 'me132', label: 'Midterm' }
  ], later), false, 'the passed exam drops out, and a label change does not stale the plan');
  assert.strictEqual(Sim.savedExamPlanStale(saved, [
    { id: 'me', date: '2026-12-04', skills: ['bode'] }
  ], later), true, 'editing the remaining exam still stales the plan');
  assert.strictEqual(Sim.savedExamPlanStale(saved, [
    { id: 'me', date: '2026-12-04', box: 'me132' },
    { id: 'quiz', date: '2026-12-01', box: 'me132' }
  ], later), true, 'adding an exam still stales the plan');
  assert.strictEqual(Sim.savedExamPlanStale(saved, saved, '2026-11-20'), false);
});

test('merge keeps the newer saved plan and does not drop a plan source', () => {
  const older = {
    version: 1, savedAt: 1,
    skills: { bode: { tier: 1, lastPracticed: now, history: [] } },
    todo: [{ type: 'skill', id: 'bode', source: 'plan', from: 0 }],
    savedPlan: { createdAt: 10, exams: [{ id: 'a', date: '2026-12-01', box: 'me132' }], sessions: [] }
  };
  const newer = {
    version: 1, savedAt: 2,
    skills: { bode: { tier: 1, lastPracticed: now, history: [] } },
    todo: [{ type: 'challenge', id: 'tf' }],
    savedPlan: {
      createdAt: 20,
      exams: [{ id: 'b', date: '2026-12-15', skills: ['tf'] }],
      sessions: [{ n: 1, date: '2026-12-01', examId: 'b', items: [{ type: 'challenge', id: 'tf', from: 1 }] }]
    }
  };
  const merged = mergeProgress(older, newer);
  assert.strictEqual(merged.savedPlan.createdAt, 20);
  assert.strictEqual(merged.savedPlan.exams[0].id, 'b');
  assert.strictEqual(merged.savedPlan.sessions[0].items[0].from, 1);
  assert.deepStrictEqual(merged.todo, [
    { type: 'skill', id: 'bode', from: 0, source: 'plan' },
    { type: 'challenge', id: 'tf' }
  ]);
  assert.strictEqual(mergeProgress(newer, older).savedPlan.createdAt, 20);
  const kept = appendTodo([{ type: 'skill', id: 'bode' }], [{ type: 'skill', id: 'bode', source: 'plan', from: 0 }]);
  assert.deepStrictEqual(kept.todo, [{ type: 'skill', id: 'bode', from: 0, source: 'plan' }]);
  assert.strictEqual(kept.added, 0);
});

test('structured row layers practice the shallowest ready skills first', () => {
  const graph = {
    ids: ['low', 'high', 'child'],
    prereqs: { low: [], high: [], child: ['low'] },
    maxTier: { low: 1, high: 1, child: 1 }
  };
  const open = Sim.simulate(graph, {}, { practiceMin: 1, challengeMin: 1 });
  assert.deepStrictEqual(open.rows[0].practiced.slice().sort(), ['high', 'low']);
  const structured = Sim.simulate(graph, {}, {
    practiceMin: 1, challengeMin: 1,
    rowLayers: { low: 0, high: 4, child: 1 }
  });
  assert.deepStrictEqual(structured.rows[0].practiced, ['low']);
  const rowOf = id => structured.rows.find(r => r.practiced.indexOf(id) >= 0);
  const lowRow = rowOf('low'), childRow = rowOf('child'), highRow = rowOf('high');
  assert(lowRow && childRow && highRow);
  assert(lowRow.n < childRow.n, 'the child waits until its prerequisite has been practiced');
  assert(childRow.n < highRow.n, 'a deeper ready skill waits for ready skills on shallower rows');
  const waited = Sim.simulate({
    ids: ['root', 'filler', 'child'],
    prereqs: { root: [], filler: [], child: ['root'] },
    maxTier: { root: 1, filler: 1, child: 1 }
  }, {}, { practiceMin: 1, challengeMin: 1, rowLayers: { root: 0, filler: 1, child: 5 } });
  assert.deepStrictEqual(waited.critical.chain, ['root', 'child']);
  const openChain = Sim.simulate({
    ids: ['a', 'b'],
    prereqs: { a: [], b: ['a'] },
    maxTier: { a: 1, b: 1 }
  }, {}, { practiceMin: 1, challengeMin: 1 });
  assert.deepStrictEqual(openChain.critical.chain, ['a', 'b']);
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
