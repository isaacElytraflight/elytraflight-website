// Strict KaTeX for bank questions and explainer sections.
// usage: node tools/skilltree-content/katex_check.cjs file.json ...
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..', '..');
const candidates = [
  path.join(root, 'skilltree/app/tests/node_modules/katex'),
  '/workspace/skilltree/app/tests/node_modules/katex',
  '/tmp/katex-home/node_modules/katex',
];
let katex;
for (const dir of candidates) {
  try { katex = require(dir); break; } catch (e) { /* try the next location */ }
}
if (!katex) {
  console.error('KaTeX: package not found');
  process.exit(1);
}
const chunks = s => {
  const out = [];
  const re = /\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g;
  let m;
  while ((m = re.exec(s))) out.push([m[1] !== undefined ? m[1] : m[2], m[2] !== undefined]);
  return out;
};
let n = 0;
const bad = [];
function check(id, text) {
  if (typeof text !== 'string') return;
  for (const [tex, disp] of chunks(text)) {
    n++;
    try {
      katex.renderToString(tex, {
        throwOnError: true,
        displayMode: disp,
        strict: (code, msg) => { throw new Error('strict ' + code + ': ' + msg); },
      });
    } catch (e) {
      bad.push(id + ' :: ' + tex + ' :: ' + String(e.message).split('\n')[0]);
    }
  }
}
for (const file of process.argv.slice(2)) {
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  for (const q of data.questions || []) {
    check(q.id, q.prompt);
    check(q.id, q.explanation);
    for (const opt of q.options || []) check(q.id, opt);
    for (const step of q.steps || []) check(q.id, step);
    for (const reason of q.reasons || []) check(q.id, reason);
    check(q.id, q.unit || '');
  }
  for (const section of data.sections || []) {
    const id = (data.id || path.basename(file, '.json')) + '#explainer';
    check(id, section.body_md);
    check(id, section.figure_alt || '');
  }
}
console.log(`KaTeX: rendered ${n} math chunks, ${bad.length} errors`);
bad.slice(0, 40).forEach(line => console.log('  ' + line));
process.exit(bad.length ? 1 : 0);
