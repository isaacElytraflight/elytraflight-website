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

const graph = JSON.parse(fs.readFileSync(path.join(SRC, 'ee105_skills_draft.json'), 'utf8'));
const collections = JSON.parse(fs.readFileSync(path.join(SRC, 'collections.json'), 'utf8'));
const skills = graph.skills;
const retired = graph.retired || {};
const skillIds = new Set(skills.map(s => s.id));
const retiredIds = new Set(Object.keys(retired));

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

test('graph is version 2 with 106 live skills and 15 retired ids', () => {
  assert.strictEqual(graph.version, 2);
  assert.strictEqual(skills.length, 106);
  assert.strictEqual(retiredIds.size, 15);
  assert.strictEqual(new Set(skills.map(s => s.id)).size, 106, 'skill ids are unique');
});

test('every retired id points at a live survivor and is not itself live', () => {
  for (const [oldId, survivorId] of Object.entries(retired)) {
    assert.strictEqual(skillIds.has(oldId), false, oldId + ' is still a live skill');
    assert.strictEqual(skillIds.has(survivorId), true, oldId + ' -> missing ' + survivorId);
    assert.strictEqual(retiredIds.has(survivorId), false, survivorId + ' is also retired');
  }
});

test('every graph skill has a quiz bank whose skill_id matches', () => {
  const banks = readJsonDir(path.join(SRC, 'bank'));
  assert.strictEqual(Object.keys(banks).length, 106);
  for (const skill of skills) {
    const bank = banks[skill.id];
    assert(bank, 'missing bank for ' + skill.id);
    assert.strictEqual(bank.skill_id, skill.id);
    assert(Array.isArray(bank.questions) && bank.questions.length > 0, skill.id + ' bank is empty');
  }
  for (const id of Object.keys(banks)) {
    assert(skillIds.has(id), 'bank for unknown skill ' + id);
    assert(!retiredIds.has(id), 'bank for retired skill ' + id);
  }
});

test('every graph skill has an explainer', () => {
  const explainers = readJsonDir(path.join(SRC, 'explainers'));
  assert.strictEqual(Object.keys(explainers).length, 106);
  for (const skill of skills) {
    const exp = explainers[skill.id];
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

test('collections reference no retired ids and every listed skill exists', () => {
  const seen = new Set();
  for (const box of collections.boxes) {
    assert(!retiredIds.has(box.id), 'box id is a retired skill id: ' + box.id);
    for (const sid of box.skills || []) {
      assert(skillIds.has(sid), box.id + ' lists unknown skill ' + sid);
      assert(!retiredIds.has(sid), box.id + ' lists retired skill ' + sid);
      seen.add(sid);
    }
    for (const child of box.children || []) {
      assert(!retiredIds.has(child), box.id + ' child ' + child + ' is a retired skill id');
    }
  }
  for (const id of skillIds) assert(seen.has(id), 'live skill missing from collections: ' + id);
});

test('no retired id is referenced by the built app payload', () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(PUB, 'manifest.json'), 'utf8'));
  const built = JSON.parse(fs.readFileSync(path.join(PUB, manifest.skills.file), 'utf8'));
  assert.deepStrictEqual(built.retired, retired);
  const builtIds = built.skills.map(s => s.id);
  assert.strictEqual(builtIds.length, 106);
  for (const id of builtIds) {
    assert(!retiredIds.has(id), 'built graph still contains ' + id);
    for (const pre of built.skills.find(s => s.id === id).prereqs) {
      assert(builtIds.includes(pre), id + ' prereq ' + pre + ' missing from built graph');
      assert(!retiredIds.has(pre), id + ' prereq ' + pre + ' is retired');
    }
    assert(built.banks[id], 'built manifest missing bank for ' + id);
    assert(fs.existsSync(path.join(PUB, built.banks[id].file)), 'missing ' + built.banks[id].file);
    assert(built.explainers[id], 'built manifest missing explainer for ' + id);
    assert(fs.existsSync(path.join(PUB, built.explainers[id].file)), 'missing ' + built.explainers[id].file);
  }
  for (const id of Object.keys(built.banks)) assert(!retiredIds.has(id), 'built bank for retired ' + id);
  const builtCollections = JSON.parse(fs.readFileSync(path.join(PUB, manifest.collections.file), 'utf8'));
  for (const box of builtCollections.boxes) {
    for (const sid of box.skills || []) {
      assert(builtIds.includes(sid), 'built collection lists unknown ' + sid);
      assert(!retiredIds.has(sid), 'built collection lists retired ' + sid);
    }
  }
});

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed > 0 ? 1 : 0);
