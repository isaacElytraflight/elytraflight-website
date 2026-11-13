/**
 * Learner-facing and repo text must not contain the retired product name.
 * Internal identifiers stay. Run: node test-brand.js
 */
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const REPO = path.join(__dirname, '..', '..', '..');
const NEEDLE = 'skill' + 'grove';
const SKIP_DIRS = new Set(['node_modules', '.git', 'build', 'dist', 'shots']);

// Identifiers the running app, export format, SQL, and tests still use.
const ALLOW = [
  '__' + NEEDLE,
  'SkillgroveAuth',
  'SkillgroveMigrate',
  'SkillgroveTelemetry',
  'is_' + NEEDLE + '_admin',
  NEEDLE + '_admins',
  "app:'" + NEEDLE + "'",
  "app: '" + NEEDLE + "'",
  'SKILLGROVE_TODO_SHOT',
  NEEDLE + '-ui',
  NEEDLE + '-flag-question.png',
  NEEDLE + '-usage-setting.png',
  NEEDLE + '-admin-dashboard.png',
];

function strip(text) {
  let out = text;
  for (const token of ALLOW) {
    out = out.split(token).join('');
  }
  return out;
}

function walk(dir, files) {
  for (const name of fs.readdirSync(dir)) {
    if (SKIP_DIRS.has(name)) continue;
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) walk(full, files);
    else if (stat.isFile()) files.push(full);
  }
}

const files = [];
walk(REPO, files);

const textExt = new Set([
  '.html', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.css', '.json', '.md',
  '.py', '.sql', '.yml', '.yaml', '.txt', '.svg', '.xml',
]);

let hits = [];
for (const file of files) {
  const rel = path.relative(REPO, file);
  const base = path.basename(file);
  if (base.toLowerCase().includes(NEEDLE)) {
    hits.push(rel + ' (filename)');
  }
  if (!textExt.has(path.extname(file).toLowerCase())) continue;
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch (e) {
    continue;
  }
  const left = strip(text);
  const re = new RegExp(NEEDLE, 'ig');
  let match;
  while ((match = re.exec(left))) {
    const start = Math.max(0, match.index - 40);
    const end = Math.min(left.length, match.index + NEEDLE.length + 40);
    hits.push(rel + ': ' + JSON.stringify(left.slice(start, end)));
    if (hits.length > 20) break;
  }
  if (hits.length > 20) break;
}

assert.deepStrictEqual(hits, [], 'retired product name is still visible:\n' + hits.join('\n'));
console.log('brand check ok (' + files.length + ' files)');
