/**
 * Content integrity for the v2 skill graph, banks, explainers, and collections.
 * Run from anywhere: node public/skilltree/tests/test-content.js
 */
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const REPO = path.join(__dirname, '..', '..', '..');
const SRC = path.join(REPO, 'skilltree');
const PUB = path.join(REPO, 'public', 'skilltree');

const { migrateRetiredProgress } = require('../migrate.js');

const graph = JSON.parse(fs.readFileSync(path.join(SRC, 'ee105_skills_draft.json'), 'utf8'));
const collections = JSON.parse(fs.readFileSync(path.join(SRC, 'collections.json'), 'utf8'));
const skills = graph.skills;
const retired = graph.retired || {};
const skillIds = new Set(skills.map(s => s.id));
const retiredIds = new Set(Object.keys(retired));
const CORES = ['lti-def', 'cx-exp', 'impulse-conv', 'step-resp', 'sinusoid-resp', 'freq-char', 'tf', 'pole-zero', 'bode', 'fb-intro', 'loop-gain', 'fb-errors', 'stability'];
const EE_APPS = ['lti-circuits', 'freq-resp-circuits', 'bode-circuits', 'fb-amp', 'fb-amp-errors', 'amp-compensation'];
const ME_APPS = ['lti-mech', 'loop-margin-design'];

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

function readJsonDir(dir) {
  const out = {};
  for (const file of fs.readdirSync(dir)) {
    if (!file.endsWith('.json')) continue;
    const data = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
    out[file.replace(/\.json$/, '')] = data;
  }
  return out;
}

console.log('\n=== Skillgrove content integrity ===\n');

test('graph is version 3 with 170 live skills and 16 retired ids', () => {
  assert.strictEqual(graph.version, 3);
  assert.strictEqual(skills.length, 170);
  assert.strictEqual(retiredIds.size, 16);
  assert.strictEqual(retired.margins, 'stability');
  assert.strictEqual(new Set(skills.map(s => s.id)).size, 170, 'skill ids are unique');
  const soon = skills.filter(s => s.status === 'coming-soon');
  assert.strictEqual(soon.length, 56, 'retiring margins leaves 56 coming-soon skills');
});

test('every retired id points at a live survivor and is not itself live', () => {
  for (const [oldId, survivorId] of Object.entries(retired)) {
    assert.strictEqual(skillIds.has(oldId), false, oldId + ' is still a live skill');
    assert.strictEqual(skillIds.has(survivorId), true, oldId + ' -> missing ' + survivorId);
    assert.strictEqual(retiredIds.has(survivorId), false, survivorId + ' is also retired');
  }
});

test('playable skills have quiz banks and coming-soon skills do not', () => {
  const banks = readJsonDir(path.join(SRC, 'bank'));
  assert.strictEqual(Object.keys(banks).length, 114);
  const soon = skills.filter(s => s.status === 'coming-soon');
  assert.strictEqual(soon.length, 56);
  for (const skill of skills) {
    const bank = banks[skill.id];
    if (skill.status === 'coming-soon') {
      assert(!bank, skill.id + ' is coming soon and must not have a question bank');
      continue;
    }
    assert(bank, 'missing bank for ' + skill.id);
    assert.strictEqual(bank.skill_id, skill.id);
    assert(Array.isArray(bank.questions) && bank.questions.length > 0, skill.id + ' bank is empty');
    assert(bank.questions.some(q => q.round === 1), skill.id + ' has no round-1 questions');
  }
  for (const id of Object.keys(banks)) {
    assert(skillIds.has(id), 'bank for unknown skill ' + id);
    assert(!retiredIds.has(id), 'bank for retired skill ' + id);
  }
});

test('playable skills have explainers and coming-soon skills do not', () => {
  const explainers = readJsonDir(path.join(SRC, 'explainers'));
  assert.strictEqual(Object.keys(explainers).length, 114);
  for (const skill of skills) {
    const exp = explainers[skill.id];
    if (skill.status === 'coming-soon') {
      assert(!exp, skill.id + ' is coming soon and must not have an explainer');
      continue;
    }
    assert(exp, 'missing explainer for ' + skill.id);
    assert.strictEqual(exp.id, skill.id);
    assert(Array.isArray(exp.sections) && exp.sections.length > 0, skill.id + ' explainer is empty');
  }
  for (const id of Object.keys(explainers)) {
    assert(skillIds.has(id), 'explainer for unknown skill ' + id);
    assert(!retiredIds.has(id), 'explainer for retired skill ' + id);
  }
});

test('every prerequisite resolves to a live skill and the graph is acyclic', () => {
  const visiting = new Set();
  const visited = new Set();
  function walk(id, stack) {
    assert(skillIds.has(id), 'missing skill ' + id);
    if (visited.has(id)) return;
    assert(!visiting.has(id), 'cycle: ' + stack.concat(id).join(' -> '));
    visiting.add(id);
    const skill = skills.find(s => s.id === id);
    assert(Array.isArray(skill.prereqs), id + ' has no prereqs array');
    for (const pre of skill.prereqs) {
      assert(!retiredIds.has(pre), id + ' prerequisite ' + pre + ' is retired');
      assert(skillIds.has(pre), id + ' prerequisite ' + pre + ' does not resolve');
      walk(pre, stack.concat(id));
    }
    visiting.delete(id);
    visited.add(id);
  }
  for (const skill of skills) walk(skill.id, []);
  assert.strictEqual(visited.size, skills.length);
});

function topLevelBoxes(boxes) {
  const childIds = new Set();
  for (const box of boxes) for (const child of box.children || []) childIds.add(child);
  return boxes.filter(box => !childIds.has(box.id));
}

function skillsInBox(box, byId) {
  const out = new Set(box.skills || []);
  for (const child of box.children || []) {
    const nested = byId[child];
    assert(nested, 'missing child box ' + child);
    for (const id of skillsInBox(nested, byId)) out.add(id);
  }
  return out;
}

test('collections reference no retired ids and every skill sits in a top-level box', () => {
  const byId = Object.fromEntries(collections.boxes.map(box => [box.id, box]));
  const seen = new Set();
  for (const box of collections.boxes) {
    assert(!retiredIds.has(box.id), 'box id is a retired skill id: ' + box.id);
    for (const sid of box.skills || []) {
      assert(skillIds.has(sid), box.id + ' lists unknown skill ' + sid);
      assert(!retiredIds.has(sid), box.id + ' lists retired skill ' + sid);
      seen.add(sid);
    }
    for (const child of box.children || []) {
      assert(byId[child], box.id + ' child ' + child + ' does not resolve');
      assert(!retiredIds.has(child), box.id + ' child ' + child + ' is a retired skill id');
    }
  }
  for (const id of skillIds) assert(seen.has(id), 'live skill missing from collections: ' + id);

  const tops = topLevelBoxes(collections.boxes);
  const topIds = tops.map(box => box.id);
  assert.deepStrictEqual(topIds, ['ee105-ucb', 'me132', 'am08']);
  const me132 = tops.find(box => box.id === 'me132');
  const am08 = tops.find(box => box.id === 'am08');
  assert.strictEqual(me132.title, 'ME 132 (UC Berkeley)');
  assert.strictEqual(me132.kind, 'course');
  assert.strictEqual(me132.children.length, 9);
  assert.strictEqual(am08.title, 'Feedback Systems');
  assert.strictEqual(am08.kind, 'textbook');
  assert.strictEqual(am08.children.length, 13);
  assert(!me132.children.includes('am08') && !am08.children.includes('me132'), 'the two new boxes must stay independent');

  const covered = new Set();
  for (const top of tops) {
    const members = skillsInBox(top, byId);
    const chapters = (top.children || []).map(id => byId[id]);
    const seenInTop = new Set();
    for (const chapter of chapters) {
      for (const sid of chapter.skills || []) {
        assert(!seenInTop.has(sid), sid + ' is in two chapters of ' + top.id);
        seenInTop.add(sid);
      }
    }
    for (const sid of members) covered.add(sid);
  }
  for (const id of skillIds) assert(covered.has(id), 'skill missing from every top-level box: ' + id);
  assert.strictEqual(skillsInBox(me132, byId).size, 56);
  assert.strictEqual(skillsInBox(am08, byId).size, 71);
  for (const shared of ['tf', 'bode', 'fb-intro', 'stability']) {
    const boxes = collections.boxes.filter(box => (box.skills || []).includes(shared)).map(box => box.id);
    assert(boxes.some(id => id.startsWith('ee105-')), shared + ' should stay in EE 105');
    assert(boxes.some(id => id.startsWith('me132/')), shared + ' should appear in ME 132');
    assert(boxes.some(id => id.startsWith('am08/')), shared + ' should appear in Feedback Systems');
  }
  for (const eeOnly of ['rc-lpf', ...EE_APPS]) {
    const boxes = collections.boxes.filter(box => (box.skills || []).includes(eeOnly)).map(box => box.id);
    assert(boxes.some(id => id.startsWith('ee105-')), eeOnly + ' should stay in EE 105');
    assert(!boxes.some(id => id.startsWith('me132/') || id.startsWith('am08/')), eeOnly + ' is EE-only: ' + boxes.join(','));
  }
  const chapterOf = {
    'lti-circuits': 'ee105-ch1',
    'freq-resp-circuits': 'ee105-ch1',
    'bode-circuits': 'ee105-ch2',
    'fb-amp': 'ee105-ch17',
    'fb-amp-errors': 'ee105-ch17',
    'amp-compensation': 'ee105-ch17',
    'lti-mech': ['me132/m2', 'am08/ch2'],
    'loop-margin-design': ['me132/m5', 'am08/ch9']
  };
  for (const [sid, homes] of Object.entries(chapterOf)) {
    const boxes = collections.boxes.filter(box => (box.skills || []).includes(sid)).map(box => box.id).sort();
    assert.deepStrictEqual(boxes, [].concat(homes).sort(), sid + ' boxes ' + boxes.join(','));
  }
});

test('margins progress merges into stability and new application skills start at zero', () => {
  const input = {
    version: 1,
    savedAt: 5,
    skills: {
      margins: { tier: 3, lastPracticed: 20, history: [{ t: 4, passed: true }] },
      stability: { tier: 1, lastPracticed: 10, history: [{ t: 2, passed: false }] },
      bode: { tier: 2, lastPracticed: 8, history: [] }
    }
  };
  const { progress, changed } = migrateRetiredProgress(input, retired);
  assert.strictEqual(changed, true);
  assert.strictEqual(progress.skills.margins, undefined);
  assert.strictEqual(progress.skills.stability.tier, 3);
  assert.strictEqual(progress.skills.stability.lastPracticed, 20);
  assert.deepStrictEqual(progress.skills.stability.history.map(h => h.t), [2, 4]);
  assert.strictEqual(progress.skills.bode.tier, 2);
  for (const id of [...EE_APPS, ...ME_APPS]) {
    assert.strictEqual(progress.skills[id], undefined, id + ' starts with no progress record');
  }
  const again = migrateRetiredProgress(progress, retired);
  assert.strictEqual(again.changed, false);
});

test('from the ME 132 box, no core skill prerequisite closure contains an EE-only skill', () => {
  const byId = Object.fromEntries(collections.boxes.map(box => [box.id, box]));
  const me = skillsInBox(byId.me132, byId);
  const ee = skillsInBox(byId['ee105-ucb'], byId);
  const eeOnly = new Set([...ee].filter(id => !me.has(id)));
  const prereqs = Object.fromEntries(skills.map(s => [s.id, s.prereqs]));
  function closure(id) {
    const out = new Set();
    const stack = prereqs[id].slice();
    while (stack.length) {
      const pre = stack.pop();
      if (out.has(pre)) continue;
      out.add(pre);
      for (const next of prereqs[pre]) stack.push(next);
    }
    return out;
  }
  for (const id of CORES) {
    assert(me.has(id), id + ' is in the ME 132 box');
    const leak = [...closure(id)].filter(pre => eeOnly.has(pre));
    assert.deepStrictEqual(leak, [], id + ' closure includes an EE-only skill: ' + leak.join(', '));
  }
});

test('no retired id is referenced by the built app payload', () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(PUB, 'manifest.json'), 'utf8'));
  const built = JSON.parse(fs.readFileSync(path.join(PUB, manifest.skills.file), 'utf8'));
  assert.deepStrictEqual(built.retired, retired);
  const builtIds = built.skills.map(s => s.id);
  assert.strictEqual(builtIds.length, 170);
  assert.strictEqual(Object.keys(built.banks).length, 114);
  assert.strictEqual(Object.keys(built.explainers).length, 114);
  for (const id of builtIds) {
    assert(!retiredIds.has(id), 'built graph still contains ' + id);
    const skill = built.skills.find(s => s.id === id);
    for (const pre of skill.prereqs) {
      assert(builtIds.includes(pre), id + ' prereq ' + pre + ' missing from built graph');
      assert(!retiredIds.has(pre), id + ' prereq ' + pre + ' is retired');
    }
    if (skill.status === 'coming-soon') {
      assert(!built.banks[id], 'coming-soon skill has a built bank: ' + id);
      assert(!built.explainers[id], 'coming-soon skill has a built explainer: ' + id);
      continue;
    }
    assert(built.banks[id], 'built manifest missing bank for ' + id);
    assert(fs.existsSync(path.join(PUB, built.banks[id].file)), 'missing ' + built.banks[id].file);
    assert(built.explainers[id], 'built manifest missing explainer for ' + id);
    assert(fs.existsSync(path.join(PUB, built.explainers[id].file)), 'missing ' + built.explainers[id].file);
  }
  for (const id of Object.keys(built.banks)) assert(!retiredIds.has(id), 'built bank for retired ' + id);
  const builtCollections = JSON.parse(fs.readFileSync(path.join(PUB, manifest.collections.file), 'utf8'));
  const builtById = Object.fromEntries(builtCollections.boxes.map(box => [box.id, box]));
  const builtTops = topLevelBoxes(builtCollections.boxes).map(box => box.id);
  assert.deepStrictEqual(builtTops, ['ee105-ucb', 'me132', 'am08']);
  const covered = new Set();
  for (const topId of builtTops) for (const sid of skillsInBox(builtById[topId], builtById)) covered.add(sid);
  for (const id of builtIds) assert(covered.has(id), 'built skill missing from top-level boxes: ' + id);
  for (const box of builtCollections.boxes) {
    for (const sid of box.skills || []) {
      assert(builtIds.includes(sid), 'built collection lists unknown ' + sid);
      assert(!retiredIds.has(sid), 'built collection lists retired ' + sid);
    }
  }
});

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed > 0 ? 1 : 0);
