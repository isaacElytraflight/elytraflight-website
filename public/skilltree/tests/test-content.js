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

test('graph is version 3 with 267 live skills and 16 retired ids', () => {
  assert.strictEqual(graph.version, 3);
  assert.strictEqual(skills.length, 267);
  assert.strictEqual(retiredIds.size, 16);
  assert.strictEqual(retired.margins, 'stability');
  assert.strictEqual(new Set(skills.map(s => s.id)).size, 267, 'skill ids are unique');
  const soon = skills.filter(s => s.status === 'coming-soon');
  assert.strictEqual(soon.length, 36, 'NB1 through NB7 and B5 through B8 together leave 36 skills coming soon');
  const byId = Object.fromEntries(skills.map(s => [s.id, s]));
  assert.strictEqual(byId['lin-algebra-review'].name, 'Linear algebra review');
  assert.strictEqual(byId['lin-algebra-review'].id, 'lin-algebra-review');
  for (const id of ['rn-important-subsets', 'spectral-decomposition', 'positive-definite-matrices', 'singular-value-decomposition', 'rayleigh-quotient', 'inner-products', 'vector-norms-lp', 'cauchy-schwarz-inequality', 'induced-matrix-norms', 'frobenius-schatten-norms', 'open-closed-sets', 'compact-sets', 'level-sets-contours', 'convex-sets', 'directional-derivative', 'gradient-partial-derivatives', 'differentiability-multivariable', 'hessian-matrix', 'jacobian-chain-rule', 'matrix-calculus-gradients', 'fundamental-theorem-along-segment', 'taylor-approximation-multivariable', 'taylor-exact-mean-value', 'convex-functions', 'convexity-first-order', 'convexity-second-order', 'finite-difference-derivatives', 'computational-graphs', 'ad-forward-mode', 'ad-reverse-mode', 'hessian-vector-products-ad', 'backprop-neural-network', 'optimization-problem-formulation', 'graphical-2d-optimization', 'optimization-problem-classes', 'local-global-minima', 'existence-of-minimizers', 'first-order-optimality', 'second-order-optimality', 'stationary-point-classification', 'convex-optimality-global', 'quadratic-function-minimization', 'lp-standard-form', 'lp-graphical-solution', 'polyhedra-extreme-points', 'basic-feasible-solutions', 'simplex-feasible-directions', 'simplex-method-iteration', 'simplex-phase-one', 'lagrangian-duality-lower-bounds', 'lagrange-multiplier-equality', 'kkt-conditions', 'lp-duality-kkt', 'projection-affine-halfspace-kkt', 'linear-least-squares', 'least-squares-data-fitting', 'nonlinear-least-squares', 'circle-fitting-least-squares', 'svm-quadratic-program']) {
    assert.strictEqual(byId[id].status, undefined, id + ' has a bank and is not coming soon');
  }
  for (const id of ['feedforward', 'freq-resp-lti', 'gen-gain-phase', 'linearization', 'lti-stability', 'perf-specs-freq', 'pid-impl', 'pid-tuning', 'realization', 'uncertainty', 'windup']) {
    assert.strictEqual(byId[id].status, undefined, id + ' has a bank and is not coming soon');
  }
  for (const id of ['loop-shaping', 'lyapunov', 'observability', 'reachability', 'robust-stability', 'root-locus', 'sys-id', 'time-delay']) {
    assert.strictEqual(byId[id].status, undefined, id + ' has a bank and is not coming soon');
  }
  for (const id of ['adaptive', 'fund-limits', 'observer', 'robust-perf', 'state-feedback']) {
    assert.strictEqual(byId[id].status, undefined, id + ' has a bank and is not coming soon');
  }
  for (const id of ['fb-linearization', 'gain-scheduling', 'gen-controller', 'integral-action', 'kalman', 'kalman-optimal-observer', 'lqr', 'mpc', 'separation', 'gaussian-random-vectors']) {
    assert.strictEqual(byId[id].status, undefined, id + ' has a bank and is not coming soon');
  }
  assert.strictEqual(byId['kalman'].name, 'Kalman filter');
  assert.deepStrictEqual(byId['kalman'].prereqs, ['lin-algebra-review', 'gaussian-random-vectors']);
  assert.deepStrictEqual(byId['gaussian-random-vectors'].prereqs, ['lin-algebra-review']);
  assert.deepStrictEqual(byId['kalman-optimal-observer'].prereqs, ['kalman', 'observer']);
  assert.ok(byId['kalman-recursive-least-squares'].prereqs.includes('kalman'));
  assert.strictEqual(byId['kalman-recursive-least-squares'].status, 'coming-soon');
  assert.deepStrictEqual(byId['extended-kalman-filter'].prereqs, ['kalman-recursive-least-squares']);
  assert.strictEqual(byId['extended-kalman-filter'].status, 'coming-soon');
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
  assert.strictEqual(Object.keys(banks).length, 231);
  const soon = skills.filter(s => s.status === 'coming-soon');
  assert.strictEqual(soon.length, 36);
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
  assert.strictEqual(Object.keys(explainers).length, 231);
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

test('half-circuit prerequisites match the skills its questions assume', () => {
  const byId = Object.fromEntries(skills.map(s => [s.id, s]));
  assert.deepStrictEqual(byId['half-circuit'].prereqs, [
    'diff-intro',
    'cs-analysis',
    'degeneration',
    'ss-model',
    'lti-def'
  ]);
  assert.deepStrictEqual(byId['diff-intro'].prereqs, ['degeneration']);
  assert.deepStrictEqual(byId['diff-dc'].prereqs, ['diff-intro']);
  assert.deepStrictEqual(byId['cmrr'].prereqs, ['half-circuit', 'mirror']);
  assert.deepStrictEqual(byId['mirror-load'].prereqs, ['diff-intro', 'mirror', 'half-circuit']);
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
  assert.deepStrictEqual(topIds, ['ee105-ucb', 'me132', 'am08', 'nlo-tugraz']);
  const nlo = tops.find(box => box.id === 'nlo-tugraz');
  assert.strictEqual(nlo.title, 'Nonlinear Optimization (TU Graz)');
  assert.strictEqual(nlo.kind, 'course');
  assert.strictEqual(nlo.children.length, 12);
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
  assert.strictEqual(skillsInBox(me132, byId).size, 58);
  assert.strictEqual(skillsInBox(am08, byId).size, 72);
  assert.strictEqual(skillsInBox(nlo, byId).size, 98);
  const nloChapters = collections.boxes.filter(box => (box.skills || []).includes('lin-algebra-review')).map(box => box.id).sort();
  assert.deepStrictEqual(nloChapters, ['am08/ch99', 'nlo-tugraz/l2']);
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
  assert.strictEqual(builtIds.length, 267);
  assert.strictEqual(Object.keys(built.banks).length, 231);
  assert.strictEqual(Object.keys(built.explainers).length, 231);
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
  assert.deepStrictEqual(builtTops, ['ee105-ucb', 'me132', 'am08', 'nlo-tugraz']);
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

test('series block-diagram alt text matches the number of blocks drawn', () => {
  const bank = JSON.parse(fs.readFileSync(path.join(SRC, 'bank', 'block-diagram.json'), 'utf8'));
  const counted = { 2: /\bTwo\b/, 3: /\bThree\b/ };
  for (const q of bank.questions) {
    if (!q.figure) continue;
    const boxes = (q.figure.match(/<rect\b/g) || []).length;
    if (boxes < 2) continue;
    assert(counted[boxes], q.id + ' draws an uncounted ' + boxes + ' blocks');
    assert(counted[boxes].test(q.figure_alt), q.id + ' draws ' + boxes + ' blocks but alt is ' + q.figure_alt);
    if (boxes !== 2) assert(!/\bTwo\b/.test(q.figure_alt), q.id + ' alt still says two blocks');
  }
  for (const id of ['block-diagram-r3-q3', 'block-diagram-r4-q3']) {
    const q = bank.questions.find(item => item.id === id);
    assert.strictEqual(q.version, 2, id + ' alt edit should bump the question version');
    assert.strictEqual((q.figure.match(/<rect\b/g) || []).length, 3, id);
  }
});

function svgTexts(svg) {
  return [...svg.matchAll(/<text x="([^"]+)" y="([^"]+)"[^>]*>([^<]*)<\/text>/g)]
    .map(m => ({ x: Number(m[1]), y: Number(m[2]), t: m[3] }));
}

function svgCircles(svg) {
  return [...svg.matchAll(/<circle cx="([^"]+)" cy="([^"]+)" r="([^"]+)"/g)]
    .map(m => ({ x: Number(m[1]), y: Number(m[2]), r: Number(m[3]) }));
}

function svgLines(svg) {
  return [...svg.matchAll(/<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"/g)]
    .map(m => ({ x1: Number(m[1]), y1: Number(m[2]), x2: Number(m[3]), y2: Number(m[4]) }));
}

test('feedback labels, signs, and disturbance topology match the stems', () => {
  const skills = ['block-diagram', 'first-order-sys', 'onoff-pid-intro'];
  const questions = skills.flatMap(id =>
    JSON.parse(fs.readFileSync(path.join(SRC, 'bank', id + '.json'), 'utf8')).questions);
  const explainers = skills.map(id =>
    JSON.parse(fs.readFileSync(path.join(SRC, 'explainers', id + '.json'), 'utf8')));
  const figures = [
    ...questions.filter(q => q.figure).map(q => ({ id: q.id, svg: q.figure, alt: q.figure_alt || '', version: q.version })),
    ...explainers.flatMap(exp => exp.sections.filter(s => s.figure_svg).map(s => ({
      id: exp.id + ' explainer', svg: s.figure_svg, alt: s.figure_alt || '', version: exp.version,
    }))),
  ];
  const loops = figures.filter(item => /subtract|added at the input|disturbance/.test(item.alt) && /<circle\b/.test(item.svg));
  assert(loops.length >= 8, 'expected the feedback figures from the banks and explainers');
  for (const item of loops) {
    const texts = svgTexts(item.svg);
    const circles = svgCircles(item.svg);
    const junction = circles.reduce((a, b) => (a.x < b.x ? a : b));
    const label = name => texts.find(t => t.t === name);
    const ref = label('r');
    const err = label('e');
    if (ref) assert(ref.x < junction.x, item.id + ' puts r on the wrong side of the summer');
    if (err) assert(err.x > junction.x, item.id + ' puts the error before the summer');
    const returnSign = texts.find(t => (t.t === '−' || t.t === '+') && t.y > junction.y + 8 && Math.abs(t.x - junction.x) < 40);
    const referenceSign = texts.find(t => t.t === '+' && t.y < junction.y - 4 && Math.abs(t.x - junction.x) < 40);
    assert(referenceSign, item.id + ' does not mark the reference input with a plus');
    const upward = svgLines(item.svg).some(ln =>
      Math.abs(ln.x1 - junction.x) < 1.5 && Math.abs(ln.x2 - junction.x) < 1.5 && ln.y1 > ln.y2);
    assert(upward, item.id + ' return arrow does not enter the summer');
    if (/subtract/.test(item.alt)) {
      assert(returnSign && returnSign.t === '−', item.id + ' return is not marked minus');
    }
    if (/added at the input/.test(item.alt)) {
      assert(returnSign && returnSign.t === '+', item.id + ' return is not marked plus');
      assert(!texts.some(t => t.t === '−'), item.id + ' positive loop still shows a minus');
    }
    if (/disturbance/.test(item.alt)) {
      assert(circles.length >= 2 && label('d'), item.id + ' does not draw the output disturbance');
      const rects = [...item.svg.matchAll(/<rect x="([^"]+)"/g)].map(m => Number(m[1]));
      const outputSummer = Math.max(...circles.map(c => c.x));
      assert(outputSummer > Math.max(...rects), item.id + ' adds the disturbance before the forward blocks');
    }
  }
  const walk = questions.find(q => q.id === 'block-diagram-r2-q3');
  assert.strictEqual(walk.version, 3);
  assert(svgTexts(walk.figure).some(t => t.t === 'e'));
  assert(svgTexts(walk.figure).some(t => t.t === 'r'));
  for (const id of ['block-diagram-r3-q2', 'block-diagram-r4-q2', 'onoff-pid-intro-r2-q3']) {
    const q = questions.find(item => item.id === id);
    assert(/disturbance/.test(q.figure_alt), id);
    assert.ok(q.version >= 2, id);
  }
  for (const exp of explainers) {
    if (exp.id === 'first-order-sys') continue;
    assert.ok(exp.version >= 3, exp.id + ' explainer figure should be version 3');
  }
});

test('a disturbance wire has one arrowhead, not two', () => {
  const banks = ['block-diagram', 'onoff-pid-intro'].map(id =>
    JSON.parse(fs.readFileSync(path.join(SRC, 'bank', id + '.json'), 'utf8')));
  const questions = banks.flatMap(bank => bank.questions);
  const expected = {
    'block-diagram-r3-q2': 3,
    'block-diagram-r4-q2': 4,
    'onoff-pid-intro-r2-q3': 4,
  };
  for (const [id, version] of Object.entries(expected)) {
    const q = questions.find(item => item.id === id);
    const tips = [...q.figure.matchAll(/<polygon points="([^"]+)"/g)].map(m => {
      const [x, y] = m[1].split(/[\s,]+/).map(Number);
      return { x, y };
    });
    const mainY = tips.map(t => t.y).sort((a, b) => a - b)[Math.floor(tips.length / 2)];
    const horiz = tips.filter(t => Math.abs(t.y - mainY) < 1.5).map(t => t.x).sort((a, b) => a - b);
    for (let i = 1; i < horiz.length; i++) {
      assert(horiz[i] - horiz[i - 1] >= 40, id + ' has arrowheads ' + (horiz[i] - horiz[i - 1]) + 'px apart');
    }
    assert.strictEqual(q.version, version, id);
  }
});

test('PID terms split from one signal and their outputs add', () => {
  const bank = JSON.parse(fs.readFileSync(path.join(SRC, 'bank', 'onoff-pid-intro.json'), 'utf8'));
  const q = bank.questions.find(item => item.id === 'onoff-pid-intro-r4-q3');
  const rects = [...q.figure.matchAll(/<rect x="([^"]+)" y="([^"]+)"/g)].map(m => ({ x: m[1], y: m[2] }));
  assert.strictEqual(new Set(rects.map(r => r.y)).size, 3, 'the three terms should sit on different rows');
  assert.strictEqual(new Set(rects.map(r => r.x)).size, 1, 'the three terms should share a column');
  const left = Math.min(...rects.map(r => Number(r.x)));
  const fan = svgLines(q.figure).some(ln => ln.x1 === ln.x2 && ln.x1 < left && ln.y1 !== ln.y2);
  assert(fan, 'the three terms should split from one signal');
  assert(/add/.test(q.figure_alt));
  assert(!/in a row/.test(q.figure_alt));
  assert(!/>e<\/text>/.test(q.figure), 'the figure should not name the error and give away the choice');
  assert.strictEqual(q.version, 3);
});

const expr = require('../expr.js');

test('symbolic grader accepts equivalent expressions and rejects others', () => {
  const q = {
    answer: 'l^2 - t*l + d',
    tolerance: 1e-3,
    variables: [
      { name: 'l', min: -4, max: 4 },
      { name: 't', min: -5, max: 5 },
      { name: 'd', min: -4, max: 4 }
    ]
  };
  const rng = () => 0.37;
  assert.strictEqual(expr.grade(q, 'l**2 - t*l + d', rng).ok, true);
  assert.strictEqual(expr.grade(q, '(l - t)*l + d', rng).ok, true);
  assert.strictEqual(expr.grade(q, '2*l', rng).ok, false);
  assert.strictEqual(expr.grade(q, 'sin(', rng).invalid, true);
  assert.strictEqual(expr.evaluate(expr.parse('sin(pi/2)', []), {}), 1);
  assert.strictEqual(expr.evaluate(expr.parse('2x^2', ['x']), { x: 3 }), 18);
  assert.strictEqual(expr.evaluate(expr.parse('-2^2', []), {}), -4);
  assert.strictEqual(expr.evaluate(expr.parse('2^3^2', []), {}), 512);
  assert.strictEqual(expr.evaluate(expr.parse('ln(e)', []), {}), 1);
});

console.log(`\n${passed} passed, ${failed} failed\n`);
process.exit(failed > 0 ? 1 : 0);
