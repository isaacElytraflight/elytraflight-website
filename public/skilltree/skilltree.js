(function(){
'use strict';
/* Skillgrove — EE 105 mastery-based skill tree
   Multi-file version: loads skills graph at startup, banks lazily on quiz open */

/* ====================== data loading ====================== */
let DATA = null;       // loaded from skills.*.json
let bankCache = {};    // skill_id -> loaded bank questions
let bankMeta = {};     // skill_id -> {file, hash, questionCount, rounds}
let dataReady = false;
let loadError = null;

async function loadManifest() {
  try {
    const mRes = await fetch('manifest.json');
    if (!mRes.ok) throw new Error(`manifest.json: ${mRes.status}`);
    const manifest = await mRes.json();
    
    const sRes = await fetch(manifest.skills.file);
    if (!sRes.ok) throw new Error(`${manifest.skills.file}: ${sRes.status}`);
    DATA = await sRes.json();
    
    bankMeta = DATA.banks || {};
    dataReady = true;
    return true;
  } catch (e) {
    loadError = e.message || String(e);
    console.error('Skillgrove load error:', e);
    return false;
  }
}

async function fetchBank(skillId) {
  if (bankCache[skillId]) return bankCache[skillId];
  const meta = bankMeta[skillId];
  if (!meta) return null;
  
  try {
    const res = await fetch(meta.file);
    if (!res.ok) throw new Error(`${meta.file}: ${res.status}`);
    const data = await res.json();
    bankCache[skillId] = data.questions || [];
    return bankCache[skillId];
  } catch (e) {
    console.error(`Failed to load bank ${skillId}:`, e);
    throw e;
  }
}

/* ====================== constants & helpers ====================== */
const KEY='skilltree.progress.v1', UIKEY='skilltree.ui.v1';
const TIERS=['Unpracticed','Practiced','Level 1','Level 2','Mastered'];
const FILL=[0,30,55,80,100];
const PALETTE=['#ff6b6b','#ff9f43','#f4b400','#8bc34a','#2ed47a','#14c1a8','#22b8e6','#4c8dff','#7c6cff','#b15cff','#e25ce0','#ff5c9d','#f2784b','#6fae2e','#1fa39a','#5a7bef','#9a63d9','#d9588a'];

let skills, byId, dependents, chNums;

function initData() {
  skills = DATA.skills;
  byId = {};
  skills.forEach(s => byId[s.id] = s);
  dependents = {};
  skills.forEach(s => dependents[s.id] = []);
  skills.forEach(s => s.prereqs.forEach(p => dependents[p].push(s.id)));
  chNums = Object.keys(DATA.chapters).map(Number).sort((a, b) => a - b);
}

const chColor = n => PALETTE[(n - 1) % PALETTE.length];
function hex2rgb(h) { h = h.replace('#', ''); return [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16)) }
const rgba = (h, a) => { const c = hex2rgb(h); return `rgba(${c[0]},${c[1]},${c[2]},${a})` };
const textOn = h => { const c = hex2rgb(h); const l = (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255; return l > 0.62 ? '#1d2433' : '#ffffff' };

const hasBank = id => !!(bankMeta[id] && bankMeta[id].questionCount > 0);
const hasRound = (id, r) => {
  const m = bankMeta[id];
  return m && m.rounds && m.rounds[r] > 0;
};
const roundQsCount = (id, r) => {
  const m = bankMeta[id];
  return (m && m.rounds && m.rounds[r]) || 0;
};
const isPlayable = id => hasRound(id, 1);
let playable = [];

/* ====================== storage ====================== */
let storageOK = true, memStore = null, progress = { version: 1, skills: {} };

function probeStorage() { try { const k = 'skilltree.__probe'; localStorage.setItem(k, '1'); localStorage.removeItem(k); return true } catch (e) { return false } }

function normalizeSkill(o) {
  if (!o || typeof o !== 'object') return null;
  let t = Number(o.tier); if (!Number.isFinite(t)) return null; t = Math.max(0, Math.min(4, Math.round(t)));
  let lp = (o.lastPracticed == null) ? null : Number(o.lastPracticed); if (lp != null && !Number.isFinite(lp)) lp = null;
  const hist = Array.isArray(o.history) ? o.history.filter(h => h && typeof h === 'object' && Number.isFinite(Number(h.t))).slice(-60) : [];
  return { tier: t, lastPracticed: lp, history: hist };
}

function normalizeProgress(raw) {
  if (!raw || typeof raw !== 'object' || raw.version !== 1 || !raw.skills || typeof raw.skills !== 'object' || Array.isArray(raw.skills)) return null;
  const out = { version: 1, skills: {} };
  for (const id of Object.keys(raw.skills)) { const n = normalizeSkill(raw.skills[id]); if (n) out.skills[id] = n; }
  return out;
}

function loadProgress() {
  storageOK = probeStorage();
  if (!storageOK) { showWarn('Browser storage is unavailable here, so progress will be lost when you close this tab. Use Export (top right) to save a backup file.'); return }
  let raw = null;
  try { raw = localStorage.getItem(KEY) } catch (e) { storageOK = false }
  if (!raw) return;
  try {
    const p = normalizeProgress(JSON.parse(raw));
    if (p) { progress = p; return }
  } catch (e) { }
  try { localStorage.setItem(KEY + '.backup-' + Date.now(), raw) } catch (e) { }
  setTimeout(() => toast('Saved progress could not be read; a backup copy was kept and you start fresh.'), 300);
}

function saveProgress() {
  progress.savedAt = Date.now();
  if (storageOK) {
    try { localStorage.setItem(KEY, JSON.stringify(progress)); flashSaved(); return true } catch (e) { storageOK = false; showWarn('Could not save to browser storage. Progress is kept in memory only — Export a backup now.') }
  }
  memStore = JSON.stringify(progress);
  return false;
}

function showWarn(msg) { const w = document.getElementById('warnbar'); w.textContent = '⚠ ' + msg; w.style.display = 'block' }
function flashSaved() { const s = document.getElementById('saveInd'); s.classList.add('on'); clearTimeout(flashSaved.t); flashSaved.t = setTimeout(() => s.classList.remove('on'), 1600) }
const sk = id => progress.skills[id] || (progress.skills[id] = { tier: 0, lastPracticed: null, history: [] });
const tierOf = id => progress.skills[id] ? progress.skills[id].tier : 0;
const lastOf = id => progress.skills[id] ? progress.skills[id].lastPracticed : null;

/* ====================== helpers ====================== */
function el(tag, props, ...kids) {
  const e = document.createElement(tag);
  if (props) for (const k in props) {
    const v = props[k]; if (v == null || v === false) continue;
    if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else if (k === 'math') setMath(e, v); else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (k === 'style') e.style.cssText = v; else e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of kids.flat(Infinity)) { if (c == null || c === false) continue; e.append(c.nodeType ? c : document.createTextNode(String(c))) }
  return e;
}

window.__katexErrors = window.__katexErrors || [];
const MATH_RE = /\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g;

function setMath(node, text) {
  node.textContent = ''; text = text == null ? '' : String(text);
  let last = 0, m; MATH_RE.lastIndex = 0;
  while ((m = MATH_RE.exec(text))) {
    if (m.index > last) node.append(document.createTextNode(text.slice(last, m.index)));
    const disp = m[2] != null, tex = disp ? m[2] : m[1];
    const sp = document.createElement(disp ? 'div' : 'span'); sp.className = disp ? 'mathd' : 'mathi';
    try {
      if (typeof katex === 'undefined') throw new Error('KaTeX not loaded');
      katex.render(tex, sp, { displayMode: disp, throwOnError: true, strict: 'ignore', output: 'htmlAndMathml' });
    } catch (err) { window.__katexErrors.push(String(err && err.message || err) + ' :: ' + tex); sp.textContent = tex; sp.classList.add('matherr') }
    node.append(sp); last = m.index + m[0].length;
  }
  if (last < text.length) node.append(document.createTextNode(text.slice(last)));
  return node;
}

const mathPlain = t => String(t == null ? '' : t).replace(MATH_RE, (_, a, b) => (a != null ? a : b).replace(/\\(mathrm|text|operatorname)\{([^}]*)\}/g, '$2').replace(/\\[a-zA-Z]+\s?/g, s => ({ '\\omega': 'ω', '\\tau': 'τ', '\\pi': 'π', '\\mu': 'µ', '\\Omega': 'Ω', '\\alpha': 'α', '\\beta': 'β', '\\angle': '∠', '\\circ': '°', '\\times': '×', '\\cdot': '·', '\\approx': '≈' })[s.trim()] || '').replace(/[{}]/g, '').replace(/\\[ ,;!]/g, ' '));

function shortMath(s, n) {
  if (s.length <= n) return s;
  let cut = s.slice(0, n - 1);
  const o = cut.lastIndexOf('\\('), c = cut.lastIndexOf('\\)');
  if (o > c) { const end = s.indexOf('\\)', o); cut = (end >= 0 && end + 2 <= n + 40) ? s.slice(0, end + 2) : cut.slice(0, o) }
  return cut.replace(/\s+$/, '') + '…';
}

const SVG_BAD = /^(script|foreignobject|image|iframe|object|embed|use|a|style|audio|video|animate|set|animatemotion|animatetransform)$/i;

function figureNode(q, extraClass) {
  if (!q || !q.figure) return null;
  let svg;
  try {
    const doc = new DOMParser().parseFromString(q.figure, 'image/svg+xml');
    svg = doc.documentElement;
    if (!svg || svg.nodeName.toLowerCase() !== 'svg' || doc.getElementsByTagName('parsererror').length) throw new Error('bad svg');
    for (const n of [...svg.querySelectorAll('*')]) { if (SVG_BAD.test(n.localName)) n.remove() }
    for (const n of [svg, ...svg.querySelectorAll('*')]) {
      for (const at of [...n.attributes]) {
        const k = at.name.toLowerCase(), v = at.value;
        if (k.startsWith('on') || k === 'href' || k === 'xlink:href' || k === 'style' || /(javascript:|data:|url\(|https?:)/i.test(v)) n.removeAttribute(at.name)
      }
    }
    svg = document.importNode(svg, true);
  } catch (e) { window.__katexErrors.push('figure: ' + e.message + ' :: ' + q.id); return null }
  const alt = q.figure_alt || 'Figure';
  svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', alt); svg.setAttribute('focusable', 'false');
  svg.removeAttribute('width'); svg.removeAttribute('height');
  let t = svg.querySelector(':scope > title');
  if (!t) { t = document.createElementNS('http://www.w3.org/2000/svg', 'title'); svg.insertBefore(t, svg.firstChild) }
  t.textContent = alt;
  const vb = (svg.getAttribute('viewBox') || '').split(/[\s,]+/).map(Number);
  const w = vb.length === 4 && vb[2] > 0 ? vb[2] : 360;
  const box = el('figure', { class: 'qfig' + (extraClass ? ' ' + extraClass : ''), 'data-qid': q.id });
  box.style.setProperty('--fw', Math.min(Math.round(w * 1.25), 560) + 'px');
  box.append(svg); return box;
}

const $ = id => document.getElementById(id);

function ago(ts) {
  if (!ts) return 'never';
  const s = Math.max(0, (Date.now() - ts) / 1000);
  if (s < 60) return 'just now'; if (s < 3600) return Math.floor(s / 60) + ' min ago';
  if (s < 86400) return Math.floor(s / 3600) + ' h ago'; const d = Math.floor(s / 86400); return d + (d === 1 ? ' day ago' : ' days ago');
}

const fmtDate = ts => new Date(ts).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
let toastT;
function toast(msg) { const t = $('toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), 3200) }
function colorVars(ch) { const c = chColor(ch); return `--c:${c};--cs:${rgba(c, .5)};--cs2:${rgba(c, .78)};--tc:${textOn(c)};--bg:${rgba(c, .1)};--cb:${rgba(c, .55)}` }

const READY_TIER = 3;
const prereqGaps = id => byId[id].prereqs.filter(p => isPlayable(p) && tierOf(p) < READY_TIER);
function isReady(id) { return isPlayable(id) && tierOf(id) === 0 && prereqGaps(id).length === 0 }
function queue() {
  return skills.filter(s => { const t = tierOf(s.id); return t >= 1 && t <= 3 && hasRound(s.id, t + 1) })
    .sort((a, b) => (lastOf(a.id) || 0) - (lastOf(b.id) || 0) || skills.indexOf(a) - skills.indexOf(b));
}

/* ====================== layout engines ====================== */
const TW = 168, TH = 72, GX = 18, GYR = 46, PAD = 26, HDR = 48, DW = 14, DGAP = 12, BGAP = 46, RGAP = 76, ROWMAX = 3200, WPAD = 40, BMIN = 470;
const LAYKEY = 'skilltree.layout.v1';

function pav(targets, seps, weights) {
  const n = targets.length, off = [0]; for (let i = 1; i < n; i++) off[i] = off[i - 1] + seps[i - 1];
  const bl = [];
  for (let i = 0; i < n; i++) {
    bl.push({ s: weights[i] * (targets[i] - off[i]), W: weights[i], n: 1 });
    while (bl.length > 1 && bl[bl.length - 2].s / bl[bl.length - 2].W > bl[bl.length - 1].s / bl[bl.length - 1].W) {
      const b = bl.pop(), a = bl[bl.length - 1]; a.s += b.s; a.W += b.W; a.n += b.n;
    }
  }
  const out = []; bl.forEach(b => { const m = b.s / b.W; for (let k = 0; k < b.n; k++) out.push(m + off[out.length]) });
  return out;
}

function layeredLayout(ids, edges) {
  const par = {}; ids.forEach(i => par[i] = []); edges.forEach(([p, c]) => par[c].push(p));
  const layerOf = {};
  const L = id => layerOf[id] != null ? layerOf[id] : (layerOf[id] = par[id].length ? 1 + Math.max(...par[id].map(L)) : 0);
  ids.forEach(L);
  const nl = Math.max(0, ...ids.map(i => layerOf[i])) + 1;
  const nodes = [], nid = {};
  const link = (a, b) => { nodes[a].down.push(b); nodes[b].up.push(a) };
  ids.forEach(id => { nid[id] = nodes.length; nodes.push({ id, real: true, layer: layerOf[id], up: [], down: [], w: TW, wt: 1 }) });
  const chains = [];
  edges.forEach(([p, c]) => {
    let prev = nid[p]; const mids = [];
    for (let l = layerOf[p] + 1; l < layerOf[c]; l++) { const k = nodes.length; nodes.push({ real: false, layer: l, up: [], down: [], w: DW, wt: 3 }); mids.push(k); link(prev, k); prev = k }
    link(prev, nid[c]); chains.push({ key: p + '>' + c, mids });
  });
  const pos = new Array(nodes.length).fill(0);
  let ord = Array.from({ length: nl }, () => []);
  const reindex = l => ord[l].forEach((k, i) => pos[k] = i);
  const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
  function init(rev) {
    ord = Array.from({ length: nl }, () => []);
    const ks = nodes.map((_, k) => k).filter(k => nodes[k].real && nodes[k].layer === 0); if (rev) ks.reverse();
    ord[0] = ks; reindex(0);
    for (let l = 1; l < nl; l++) {
      const ks2 = nodes.map((_, k) => k).filter(k => nodes[k].layer === l);
      ord[l] = ks2; ks2.forEach((k, i) => pos[k] = i);
      const key = new Map(ks2.map(k => [k, mean(nodes[k].up.map(m => pos[m]))]));
      ord[l] = ks2.map((k, i) => [k, i]).sort((a, b) => key.get(a[0]) - key.get(b[0]) || a[1] - b[1]).map(a => a[0]); reindex(l);
    }
  }
  function layerCross(l) {
    const es = []; ord[l].forEach(u => nodes[u].down.forEach(v => es.push([pos[u], pos[v]])));
    let c = 0; for (let i = 0; i < es.length; i++) for (let j = i + 1; j < es.length; j++) if ((es[i][0] - es[j][0]) * (es[i][1] - es[j][1]) < 0) c++; return c;
  }
  const total = () => { let c = 0; for (let l = 0; l < nl - 1; l++) c += layerCross(l); return c };
  function sweep(down) {
    for (let s = 0; s < nl - 1; s++) {
      const l = down ? s + 1 : nl - 2 - s, nb = down ? 'up' : 'down';
      const key = new Map(ord[l].map(k => [k, nodes[k][nb].length ? mean(nodes[k][nb].map(m => pos[m])) : pos[k]]));
      ord[l] = ord[l].map((k, i) => [k, i]).sort((a, b) => key.get(a[0]) - key.get(b[0]) || a[1] - b[1]).map(a => a[0]); reindex(l);
    }
  }
  function pairCross(u, v) {
    let c = 0;
    for (const nb of ['up', 'down']) for (const a of nodes[u][nb]) for (const b of nodes[v][nb]) if (pos[a] > pos[b]) c++;
    return c;
  }
  function transpose() {
    let improved = true, guard = 0;
    while (improved && guard++ < 12) {
      improved = false;
      for (let l = 0; l < nl; l++) {
        for (let i = 0; i < ord[l].length - 1; i++) {
          const u = ord[l][i], v = ord[l][i + 1];
          if (pairCross(u, v) > pairCross(v, u)) { ord[l][i] = v; ord[l][i + 1] = u; pos[v] = i; pos[u] = i + 1; improved = true }
        }
      }
    }
  }
  let best = null, bestC = Infinity;
  for (const rev of [false, true]) {
    init(rev);
    for (let it = 0; it < 30; it++) {
      sweep(it % 2 === 0); transpose();
      const c = total(); if (c < bestC) { bestC = c; best = ord.map(a => a.slice()) }
    }
  }
  ord = best; for (let l = 0; l < nl; l++) reindex(l);
  const cx = new Array(nodes.length).fill(0);
  const sepOf = (a, b) => (nodes[a].w + nodes[b].w) / 2 + (nodes[a].real && nodes[b].real ? GX : DGAP);
  ord.forEach(arr => { let x = 0; arr.forEach((k, i) => { if (i) x += sepOf(arr[i - 1], k); cx[k] = x }); const m = (cx[arr[arr.length - 1]] || 0) / 2; arr.forEach(k => cx[k] -= m) });
  const placeLayer = (l, nbOf) => {
    const arr = ord[l]; if (!arr.length) return;
    const t = arr.map(k => { const ns = nbOf(k); return ns.length ? mean(ns.map(m => cx[m])) : cx[k] });
    const seps = arr.slice(1).map((k, i) => sepOf(arr[i], k));
    const out = pav(t, seps, arr.map(k => nodes[k].wt)); arr.forEach((k, i) => cx[k] = out[i]);
  };
  for (let it = 0; it < 10; it++) {
    for (let l = 1; l < nl; l++) placeLayer(l, k => nodes[k].up);
    for (let l = nl - 2; l >= 0; l--) placeLayer(l, k => nodes[k].down);
    for (let l = 0; l < nl; l++) placeLayer(l, k => nodes[k].up.concat(nodes[k].down));
  }
  let minX = Infinity, maxX = -Infinity;
  nodes.forEach((n, k) => { minX = Math.min(minX, cx[k] - n.w / 2); maxX = Math.max(maxX, cx[k] + n.w / 2) });
  const rowY = l => l * (TH + GYR);
  const pp = {}, mids = {};
  ids.forEach(id => { const k = nid[id]; pp[id] = { x: cx[k] - TW / 2 - minX, y: rowY(layerOf[id]) } });
  chains.forEach(c => { if (c.mids.length) mids[c.key] = c.mids.map(k => [cx[k] - minX, rowY(nodes[k].layer) + TH / 2]) });
  return { pos: pp, mids, w: maxX - minX, h: nl * TH + (nl - 1) * GYR, nl, crossings: bestC, layerOf };
}

let allEdges = [];
const layout = { tree: null, grouped: null };

function computeTreeLayout() {
  const r = layeredLayout(skills.map(s => s.id), allEdges);
  const nodes = {}, mids = {};
  for (const id in r.pos) nodes[id] = { x: r.pos[id].x + WPAD, y: (r.h - r.pos[id].y - TH) + WPAD };
  for (const k in r.mids) mids[k] = r.mids[k].map(p => [p[0] + WPAD, (r.h - p[1]) + WPAD]);
  layout.tree = { nodes, mids, blobs: {}, w: r.w + WPAD * 2, h: r.h + WPAD * 2, layers: r.nl, crossings: r.crossings, layerOf: r.layerOf };
}

function computeGroupedLayout() {
  const byCh = {}; skills.forEach(s => (byCh[s.chapter] = byCh[s.chapter] || []).push(s.id));
  const subs = {}, bs = {};
  for (const ch of chNums) {
    const ids = byCh[ch] || [], set = new Set(ids);
    const sub = layeredLayout(ids, allEdges.filter(([p, c]) => set.has(p) && set.has(c)));
    subs[ch] = sub; bs[ch] = { w: Math.max(sub.w + PAD * 2, BMIN), h: HDR + sub.h + PAD + 4 };
  }
  const cpred = {}; chNums.forEach(c => cpred[c] = new Map());
  allEdges.forEach(([p, c]) => { const a = byId[p].chapter, b = byId[c].chapter; if (a !== b) cpred[b].set(a, (cpred[b].get(a) || 0) + 1) });
  const rank = {};
  const R = c => rank[c] != null ? rank[c] : (rank[c] = cpred[c].size ? 1 + Math.max(...[...cpred[c].keys()].map(R)) : 0);
  chNums.forEach(R);
  const gdepth = chNums.map(c => ({ c, d: byCh[c].reduce((a, id) => a + (layout.tree.layerOf[id] || 0), 0) / byCh[c].length }));
  const avgD = {}; gdepth.forEach(o => avgD[o.c] = o.d);
  const maxRank = Math.max(...chNums.map(c => rank[c]));
  const bx = {}, by = {}; let y = 0;
  const center = c => bx[c] + bs[c].w / 2;
  const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
  for (let r = 0; r <= maxRank; r++) {
    let row = chNums.filter(c => rank[c] === r);
    const want = c => { const ps = [...cpred[c].entries()].filter(([p]) => bx[p] != null); return ps.length ? ps.reduce((a, [p, n]) => a + center(p) * n, 0) / ps.reduce((a, [, n]) => a + n, 0) : null };
    row.sort((a, b) => { const wa = want(a), wb = want(b); return (wa == null ? 0 : wa) - (wb == null ? 0 : wb) || avgD[a] - avgD[b] || a - b });
    const subrows = [[]]; let w = 0;
    row.forEach(c => { if (w && w + bs[c].w + BGAP > ROWMAX) { subrows.push([]); w = 0 } subrows[subrows.length - 1].push(c); w += bs[c].w + BGAP });
    subrows.forEach(sr => {
      const wants = sr.map(c => want(c)); const fallback = 0;
      const t = sr.map((c, i) => wants[i] == null ? null : wants[i]);
      const known = t.filter(v => v != null); const base = known.length ? mean(known) : fallback;
      const tgt = t.map(v => v == null ? base : v);
      const seps = sr.slice(1).map((c, i) => (bs[sr[i]].w + bs[c].w) / 2 + BGAP);
      const xs = pav(tgt, seps, sr.map(() => 1));
      let rh = 0; sr.forEach((c, i) => { bx[c] = xs[i] - bs[c].w / 2; by[c] = y; rh = Math.max(rh, bs[c].h) });
      y += rh + RGAP;
    });
  }
  const minX = Math.min(...chNums.map(c => bx[c])), maxX = Math.max(...chNums.map(c => bx[c] + bs[c].w));
  const nodes = {}, mids = {}, blobs = {};
  for (const ch of chNums) {
    const ox = bx[ch] - minX + WPAD, oy = by[ch] + WPAD;
    blobs[ch] = { x: ox, y: oy, w: bs[ch].w, h: bs[ch].h };
    const ix = ox + (bs[ch].w - subs[ch].w) / 2, iy = oy + PAD + 4;
    for (const id in subs[ch].pos) nodes[id] = { x: ix + subs[ch].pos[id].x, y: iy + subs[ch].pos[id].y };
    for (const k in subs[ch].mids) mids[k] = subs[ch].mids[k].map(p => [ix + p[0], iy + p[1]]);
  }
  const M = 26;
  allEdges.forEach(([p, c]) => {
    const cp = byId[p].chapter, cc = byId[c].chapter; if (cp === cc) return;
    const A = blobs[cp], B = blobs[cc], P = nodes[p], Q = nodes[c];
    const sx = P.x + TW / 2, sy = P.y + TH, tx = Q.x + TW / 2, ty = Q.y;
    if (ty <= sy) return;
    const obs = chNums.filter(x => x !== cp && x !== cc).map(x => blobs[x]).filter(o => o.y < ty && o.y + o.h > sy).sort((u, v) => u.y - v.y);
    if (!obs.length) return;
    const bands = [];
    obs.forEach(o => {
      const last = bands[bands.length - 1];
      if (last && o.y < last.y1 + RGAP * .6) { last.y1 = Math.max(last.y1, o.y + o.h); last.iv.push([o.x - M, o.x + o.w + M]) }
      else bands.push({ y0: o.y, y1: o.y + o.h, iv: [[o.x - M, o.x + o.w + M]] })
    });
    const pts = [];
    bands.forEach(bd => {
      const iv = bd.iv.sort((u, v) => u[0] - v[0]).reduce((acc, r) => { const l = acc[acc.length - 1]; if (l && r[0] <= l[1]) l[1] = Math.max(l[1], r[1]); else acc.push([r[0], r[1]]); return acc }, []);
      const ym = (bd.y0 + bd.y1) / 2, f = Math.max(0, Math.min(1, (ym - sy) / (ty - sy)));
      let x = sx + (tx - sx) * f;
      const hit = iv.find(r => x > r[0] && x < r[1]);
      if (hit) { const l = hit[0], r = hit[1]; x = (l < 14 || Math.abs(x - l) > Math.abs(r - x)) ? r : l }
      pts.push([x, Math.max(sy + 8, bd.y0 - RGAP * .35)], [x, Math.min(ty - 8, bd.y1 + RGAP * .35)]);
    });
    mids[p + '>' + c] = pts;
  });
  const allX = []; for (const k in mids) mids[k].forEach(q => allX.push(q[0]));
  const shiftX = Math.max(0, 20 - Math.min(Infinity, ...allX));
  if (shiftX) { for (const id in nodes) nodes[id].x += shiftX; for (const k in mids) mids[k].forEach(q => q[0] += shiftX); for (const c in blobs) blobs[c].x += shiftX }
  const worldW = Math.max(maxX - minX + WPAD * 2, ...allX.map(v => v + WPAD), ...chNums.map(c => blobs[c].x + blobs[c].w + WPAD));
  const worldH = y - RGAP + WPAD * 2;
  for (const id in nodes) nodes[id].y = worldH - nodes[id].y - TH;
  for (const k in mids) mids[k].forEach(q => q[1] = worldH - q[1]);
  for (const c in blobs) blobs[c].y = worldH - blobs[c].y - blobs[c].h;
  layout.grouped = { nodes, mids, blobs, w: worldW, h: worldH, rank };
}

function computeLayouts() { computeTreeLayout(); computeGroupedLayout() }

/* ====================== tree rendering ====================== */
let world, tv, edgesSvg, panel;
const panelOpen = () => panel && panel.classList.contains('open');
let view = { x: 20, y: 20, s: 1 }, selected = null, hoverId = null, quizOpen = false;
let layoutMode = 'tree', curPos = {}, morphRaf = 0;
const filter = { chapter: 0, playable: false, view: 'tree' };
const edgeEls = [];
const drag = { on: false, moved: false, sx: 0, sy: 0, vx: 0, vy: 0 };
const curL = () => layout[layoutMode];
const reducedMotion = () => window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;

function tileTitle(s) { return `${s.name} · Ch ${s.chapter}` }

function buildTile(s, st) {
  const b = el('button', { class: 'tile' + (st ? ' st' : ''), 'data-id': s.id, style: colorVars(s.chapter), type: 'button', title: tileTitle(s) },
    el('span', { class: 'fill' }), el('span', { class: 'nm', text: s.name }),
    el('span', { class: 'meta' }, el('span', { class: 'pips' }, [0, 1, 2, 3].map(() => el('i'))), el('span', { class: 'tl' }), el('span', { class: 'tag' })),
    el('span', { class: 'star', 'aria-hidden': 'true', text: '★' }));
  b.addEventListener('click', () => { if (drag.moved) return; selectSkill(s.id) });
  b.addEventListener('mouseenter', () => { hoverId = s.id; applyEdgeHighlight() });
  b.addEventListener('mouseleave', () => { hoverId = null; applyEdgeHighlight() });
  b.addEventListener('focus', () => { hoverId = s.id; applyEdgeHighlight() });
  b.addEventListener('blur', () => { hoverId = null; applyEdgeHighlight() });
  return b;
}

function refreshTile(b) {
  const id = b.dataset.id, s = byId[id], t = tierOf(id), soon = !isPlayable(id), ready = isReady(id);
  const st = b.classList.contains('st');
  b.className = 'tile' + (st ? ' st' : '') + ' t' + t + (soon ? ' soon' : '') + (ready ? ' ready' : '') + (selected === id ? ' sel' : '');
  b.style.setProperty('--fill', FILL[t] + '%');
  b.querySelectorAll('.pips i').forEach((p, i) => p.classList.toggle('on', t > i));
  b.querySelector('.tl').textContent = soon ? '' : TIERS[t];
  const tag = b.querySelector('.tag'); tag.textContent = soon ? 'SOON' : (ready ? 'READY' : ''); tag.style.display = (soon || ready) ? '' : 'none';
  const gaps = (!soon && t === 0 && !ready) ? prereqGaps(id).length : 0;
  b.title = tileTitle(s) + (soon ? ' · coming soon' : ready ? ' · ready to learn' : gaps ? ` · recommended once prerequisites reach ${TIERS[READY_TIER]}` : '');
  b.setAttribute('aria-label', `${s.name}. Chapter ${s.chapter}. ${soon ? 'Coming soon, no questions yet' : TIERS[t] + (ready ? ', ready to learn' : '')}`);
  b.setAttribute('aria-pressed', selected === id ? 'true' : 'false');
  const dimmed = (filter.chapter && s.chapter !== filter.chapter) || (filter.playable && soon);
  if (dimmed && !st) b.classList.add('dim');
}

function directD(A, B) {
  const ax = A.x + TW / 2, ay = A.y, bx = B.x + TW / 2, by = B.y + TH;
  if (by <= ay - 8) { const d = Math.max(30, (ay - by) * .5); return { d: `M${ax},${ay} C${ax},${ay - d} ${bx},${by + d} ${bx},${by}`, ex: bx, ey: by } }
  const right = B.x > A.x, sx = right ? A.x + TW : A.x, ex = right ? B.x : B.x + TW, sy = A.y + TH / 2, ey = B.y + TH / 2, d = Math.max(40, Math.abs(ex - sx) * .45);
  const dir = right ? 1 : -1;
  return { d: `M${sx},${sy} C${sx + dir * d},${sy} ${ex - dir * d},${ey} ${ex},${ey}`, ex, ey };
}

function routedD(e, L) {
  const A = L.nodes[e.from], B = L.nodes[e.to];
  const mids = L.mids[e.from + '>' + e.to];
  if (!mids) return directD(A, B);
  const pts = [[A.x + TW / 2, A.y], ...mids, [B.x + TW / 2, B.y + TH]];
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 1; i < pts.length; i++) { const a = pts[i - 1], b = pts[i], k = (b[1] - a[1]) * .5; d += ` C${a[0]},${a[1] + k} ${b[0]},${b[1] - k} ${b[0]},${b[1]}` }
  return { d, ex: B.x + TW / 2, ey: B.y + TH };
}

function setEdge(e, r) { e.path.setAttribute('d', r.d); e.dot.setAttribute('cx', r.ex); e.dot.setAttribute('cy', r.ey) }
function sizeWorld(L) { world.style.width = L.w + 'px'; world.style.height = L.h + 'px'; edgesSvg.setAttribute('width', L.w); edgesSvg.setAttribute('height', L.h) }
function placeTiles(pos) { world.querySelectorAll('.tile').forEach(t => { const p = pos[t.dataset.id]; t.style.left = p.x + 'px'; t.style.top = p.y + 'px' }) }

function buildTree() {
  computeLayouts();
  const G = layout.grouped;
  for (const ch of chNums) {
    const b = G.blobs[ch];
    const blob = el('div', { class: 'blob', 'data-ch': ch, style: `left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px;${colorVars(ch)}` },
      el('div', { class: 'hd' }, el('span', { class: 'cpill', text: 'Ch ' + ch }), el('span', { style: 'font-weight:800;font-size:13.5px', text: DATA.chapters[ch] }), el('span', { class: 'ct', 'data-ct': ch })));
    world.insertBefore(blob, edgesSvg);
  }
  const NS = 'http://www.w3.org/2000/svg';
  allEdges.forEach(([p, c]) => {
    const path = document.createElementNS(NS, 'path');
    const dot = document.createElementNS(NS, 'circle'); dot.setAttribute('r', 3.2);
    edgesSvg.append(path, dot); edgeEls.push({ from: p, to: c, path, dot });
  });
  skills.forEach(s => world.append(buildTile(s, false)));
}

function legendBuild() {
  const lg = $('chLegend'); lg.innerHTML = '';
  lg.append(el('summary', {}, 'Chapter colors'));
  const box = el('div', { class: 'lgrid' });
  chNums.forEach(c => box.append(el('button', { class: 'lg', type: 'button', style: colorVars(c), title: 'Highlight chapter ' + c, 'data-ch': c, onclick: () => { const sel = $('chSel'); if (sel) { sel.value = filter.chapter === c ? 0 : c; sel.onchange() } } }, el('i'), el('span', { text: `${c} · ${DATA.chapters[c]}` }))));
  lg.append(box);
}

const MORPH_MS = 600;
function showLayout(mode, animated) {
  cancelAnimationFrame(morphRaf);
  const L = layout[mode], ids = skills.map(s => s.id);
  const from = {}; ids.forEach(id => from[id] = curPos[id] || L.nodes[id]);
  layoutMode = mode; tv.dataset.mode = mode; world.dataset.layout = mode;
  sizeWorld(L);
  document.querySelectorAll('#world .blob').forEach(b => b.classList.toggle('on', mode === 'grouped'));
  const btn = $('btnGroup'); btn.setAttribute('aria-pressed', String(mode === 'grouped'));
  btn.querySelector('.t').textContent = mode === 'grouped' ? 'Ungroup' : 'Group by chapter';
  btn.title = mode === 'grouped' ? 'Back to one homogeneous prerequisite tree' : 'Sort the tree into chapter blocks';
  const finish = () => {
    ids.forEach(id => curPos[id] = { x: L.nodes[id].x, y: L.nodes[id].y });
    placeTiles(curPos); edgeEls.forEach(e => setEdge(e, routedD(e, L)));
    edgesSvg.classList.remove('morph'); world.classList.remove('morphing'); world.dataset.morphing = '0';
  };
  if (!animated || reducedMotion()) { finish(); return }
  world.classList.add('morphing'); world.dataset.morphing = '1'; edgesSvg.classList.add('morph');
  const t0 = performance.now();
  const step = now => {
    const k = Math.min(1, (now - t0) / MORPH_MS), e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    ids.forEach(id => { const a = from[id], b = L.nodes[id]; curPos[id] = { x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e } });
    placeTiles(curPos); edgeEls.forEach(ed => setEdge(ed, directD(curPos[ed.from], curPos[ed.to])));
    if (k < 1) morphRaf = requestAnimationFrame(step); else finish();
  };
  morphRaf = requestAnimationFrame(step);
}

function toggleGroup() {
  const mode = layoutMode === 'tree' ? 'grouped' : 'tree';
  try { localStorage.setItem(LAYKEY, mode) } catch (e) { }
  showLayout(mode, true);
  if (selected && curL().nodes[selected]) focusTile(selected); else goFit();
}

function applyEdgeHighlight() {
  const id = hoverId || selected;
  edgesSvg.classList.toggle('active', !!id);
  edgeEls.forEach(e => {
    const inn = !!id && e.to === id, out = !!id && e.from === id;
    e.path.classList.toggle('in', inn); e.path.classList.toggle('out', out);
    e.dot.classList.toggle('in', inn); e.dot.classList.toggle('out', out);
    const fd = !!filter.chapter && byId[e.from].chapter !== filter.chapter && byId[e.to].chapter !== filter.chapter;
    e.path.classList.toggle('fdim', fd); e.dot.classList.toggle('fdim', fd);
  });
}

function applyView() { world.style.transform = `translate(${view.x}px,${view.y}px) scale(${view.s})` }
function animateView(fn) { world.classList.add('anim'); fn(); clearTimeout(animateView.t); animateView.t = setTimeout(() => world.classList.remove('anim'), 500) }
const MINS = .1;

function fitBox(x, y, w, h, maxS, minS) {
  const vw = tv.clientWidth - (panelOpen() ? 372 : 0), vh = tv.clientHeight, m = 30;
  const s = Math.max(minS || MINS, Math.min(maxS, (vw - m * 2) / w, (vh - m * 2) / h));
  view = { s, x: (vw - w * s) / 2 - x * s, y: Math.max(m - y * s, (vh - h * s) / 2 - y * s) };
}

function bboxOf(ids) {
  const P = curL().nodes; const ps = ids.map(i => P[i]).filter(Boolean);
  const x0 = Math.min(...ps.map(p => p.x)), y0 = Math.min(...ps.map(p => p.y)), x1 = Math.max(...ps.map(p => p.x + TW)), y1 = Math.max(...ps.map(p => p.y + TH));
  return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
}

const HOME_BOTTOM = 84;

function goHome(anim) {
  let box; const L = curL();
  if (layoutMode === 'grouped') {
    const bs = [1, 2].map(c => L.blobs[c]).filter(Boolean);
    const x0 = Math.min(...bs.map(b => b.x)), y0 = Math.min(...bs.map(b => b.y)), x1 = Math.max(...bs.map(b => b.x + b.w)), y1 = Math.max(...bs.map(b => b.y + b.h));
    box = { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  } else {
    const ids = playable.map(s => s.id);
    box = bboxOf(ids.length ? ids : skills.map(s => s.id));
    const bottom = L.h - WPAD; if (bottom > box.y + box.h) { box.h = bottom - box.y }
  }
  const f = () => {
    const vw = tv.clientWidth - (panelOpen() ? 372 : 0), vh = tv.clientHeight;
    view.s = Math.max(layoutMode === 'tree' ? .55 : MINS, Math.min(1, (vw - 60) / box.w, (vh - 30 - HOME_BOTTOM) / box.h));
    view.x = (vw - box.w * view.s) / 2 - box.x * view.s;
    view.y = vh - HOME_BOTTOM - (box.y + box.h) * view.s;
    if (layoutMode === 'tree') view.x = vw / 2 - (box.x + box.w / 2) * view.s;
    applyView();
  };
  anim ? animateView(f) : f();
}

function goFit() { const L = curL(); animateView(() => { fitBox(0, 0, L.w, L.h, 1); applyView() }) }

function zoomAt(f, cx, cy) {
  const ns = Math.max(MINS, Math.min(1.8, view.s * f)), k = ns / view.s;
  view.x = cx - (cx - view.x) * k; view.y = cy - (cy - view.y) * k; view.s = ns; applyView();
}

function focusTile(id) {
  const n = curL().nodes[id]; if (!n) return;
  animateView(() => {
    const vw = tv.clientWidth - (panelOpen() ? 372 : 0), vh = tv.clientHeight;
    view.s = Math.min(1.2, Math.max(view.s, .85)); view.x = vw / 2 - (n.x + TW / 2) * view.s; view.y = vh / 2 - (n.y + TH / 2) * view.s; applyView();
  });
}

function focusChapter(ch) {
  const b = curL().blobs[ch];
  if (layoutMode === 'grouped' && b) { animateView(() => { fitBox(b.x, b.y, b.w, b.h, 1); view.y = 30 - b.y * view.s; applyView() }); return }
  goFit();
}

function clearSelection() { try { const s = window.getSelection && window.getSelection(); s && s.removeAllRanges && s.removeAllRanges() } catch (e) { } }

function setupPanZoom() {
  tv.addEventListener('mousedown', e => { if (e.button === 0 && !e.target.closest('.zoomctl,#chLegend')) e.preventDefault() });
  tv.addEventListener('selectstart', e => e.preventDefault());
  tv.addEventListener('dragstart', e => e.preventDefault());
  tv.addEventListener('pointerdown', e => { if (e.button !== 0) return; drag.on = true; drag.moved = false; drag.sx = e.clientX; drag.sy = e.clientY; drag.vx = view.x; drag.vy = view.y });
  window.addEventListener('pointermove', e => {
    if (!drag.on) return; const dx = e.clientX - drag.sx, dy = e.clientY - drag.sy;
    if (!drag.moved && Math.hypot(dx, dy) > 5) { drag.moved = true; tv.classList.add('drag'); world.classList.remove('anim'); clearSelection() }
    if (drag.moved) { view.x = drag.vx + dx; view.y = drag.vy + dy; applyView(); clearSelection() }
  });
  window.addEventListener('pointerup', () => { if (drag.on) { drag.on = false; tv.classList.remove('drag'); setTimeout(() => drag.moved = false, 0) } });
  tv.addEventListener('wheel', e => {
    e.preventDefault(); world.classList.remove('anim');
    if (e.ctrlKey || e.metaKey) { const r = tv.getBoundingClientRect(); zoomAt(Math.exp(-e.deltaY * (e.deltaMode ? 0.05 : 0.01)), e.clientX - r.left, e.clientY - r.top) }
    else if (e.shiftKey && !e.deltaX) { view.x -= e.deltaY; applyView() }
    else { view.x -= e.deltaX; view.y -= e.deltaY; applyView() }
  }, { passive: false });
  $('zIn').onclick = () => zoomAt(1.2, tv.clientWidth / 2, tv.clientHeight / 2);
  $('zOut').onclick = () => zoomAt(1 / 1.2, tv.clientWidth / 2, tv.clientHeight / 2);
  $('zFit').onclick = goFit; $('zHome').onclick = () => goHome(true);
  $('btnGroup').onclick = toggleGroup;
}

/* ====================== grid view ====================== */
function buildGrid() {
  const g = $('gridView'); g.innerHTML = '';
  for (const ch of chNums) {
    const list = skills.filter(s => s.chapter === ch);
    g.append(el('section', { class: 'gsec', 'data-ch': ch, style: colorVars(ch) },
      el('div', { class: 'hd' }, el('span', { class: 'cpill', text: 'Ch ' + ch }), el('b', { text: DATA.chapters[ch] }), el('span', { class: 'ct', 'data-ct': ch })),
      el('div', { class: 'ggrid' }, list.map(s => buildTile(s, true)))));
  }
}

function applyGridFilter() {
  document.querySelectorAll('#gridView .gsec').forEach(sec => {
    const ch = +sec.dataset.ch; let any = false;
    sec.querySelectorAll('.tile').forEach(t => {
      const hide = filter.playable && !isPlayable(t.dataset.id); t.style.display = hide ? 'none' : ''; if (!hide) any = true;
    });
    sec.style.display = ((filter.chapter && filter.chapter !== ch) || !any) ? 'none' : '';
  });
  document.querySelectorAll('#world .blob').forEach(b => b.classList.toggle('dim', !!filter.chapter && +b.dataset.ch !== filter.chapter));
  document.querySelectorAll('#chLegend .lg').forEach(b => b.classList.toggle('on', +b.dataset.ch === filter.chapter));
}

/* ====================== stats / banner / refresh ====================== */
function refreshAll() {
  document.querySelectorAll('.tile[data-id]').forEach(refreshTile);
  renderStats(); renderBanner(); renderPlanBadge();
  $('qCount').textContent = queue().length;
  document.querySelectorAll('[data-ct]').forEach(e => {
    const ch = +e.dataset.ct; const l = skills.filter(s => s.chapter === ch); const p = l.filter(s => isPlayable(s.id)).length;
    const c = l.filter(s => tierOf(s.id) > 0).length;
    e.textContent = `${c}/${l.length} colored in` + (p ? ` · ${p} playable` : '');
  });
  applyGridFilter(); applyEdgeHighlight();
}

function renderStats() {
  const counts = [0, 0, 0, 0, 0]; skills.forEach(s => counts[tierOf(s.id)]++);
  const pct = skills.reduce((a, s) => a + tierOf(s.id), 0) / (4 * skills.length) * 100;
  const pp = playable.length ? playable.reduce((a, s) => a + tierOf(s.id), 0) / (4 * playable.length) * 100 : 0;
  const f = v => v < 10 ? v.toFixed(1) : String(Math.round(v));
  const st = $('stats'); st.innerHTML = '';
  const nReady = skills.filter(s => isReady(s.id)).length;
  st.append(el('div', { class: 'meter', title: 'Weighted by tier: Practiced = ¼, Level 1 = ½, Level 2 = ¾, Mastered = 1 per skill' },
    el('span', { text: 'Colored in' }), el('b', { id: 'pctTxt', text: f(pct) + '%' }),
    el('span', { class: 'bar' }, el('i', { style: `width:${pct}%` })), el('span', { style: 'font-size:12px;color:var(--ink2);white-space:nowrap', text: `${f(pp)}% of playable` })));
  st.append(el('span', { class: 'sep' }));
  TIERS.forEach((n, i) => st.append(el('span', { class: 'chip', 'data-tier': i, title: i === 0 ? 'Not started yet' : 'Skills at ' + n }, el('span', { class: 'sw t' + i, style: `--f:${FILL[i]}%` }), n, ' ', el('b', { text: counts[i] }))));
  st.append(el('span', { class: 'chip', title: 'Unpracticed skills whose prerequisites are all at Level 2 or Mastered (skills with no prerequisites are ready from the start; coming-soon prerequisites are ignored)' }, el('span', { class: 'sw ready' }), 'Ready to learn ', el('b', { text: nReady })));
  st.append(el('span', { class: 'chip', title: 'No questions written yet' }, el('span', { class: 'sw soon' }), 'Coming soon ', el('b', { text: skills.length - playable.length })));
  const hc = $('hctl'); hc.innerHTML = '';
  const sel = el('select', { id: 'chSel', 'aria-label': 'Filter by chapter' }, el('option', { value: 0, text: 'All chapters' }), chNums.map(c => el('option', { value: c, text: `Ch ${c} · ${DATA.chapters[c]}` })));
  sel.value = filter.chapter;
  sel.onchange = () => { filter.chapter = +sel.value; refreshAll(); if (filter.view === 'tree') { filter.chapter ? focusChapter(filter.chapter) : (layoutMode === 'grouped' ? goHome(true) : goFit()) } };
  const chk = el('input', { type: 'checkbox', id: 'onlyPlay' }); chk.checked = filter.playable; chk.onchange = () => { filter.playable = chk.checked; refreshAll() };
  hc.append(el('div', { class: 'seg', role: 'group', 'aria-label': 'View' },
    el('button', { id: 'vTree', 'aria-pressed': String(filter.view === 'tree'), onclick: () => setView('tree') }, 'Tree'),
    el('button', { id: 'vGrid', 'aria-pressed': String(filter.view === 'grid'), onclick: () => setView('grid') }, 'Grid')),
    sel, el('label', { class: 'chk' }, chk, 'Playable only'));
}

function setView(v) {
  filter.view = v; $('treeView').hidden = v !== 'tree'; $('gridView').hidden = v !== 'grid'; $('btnGroup').hidden = v !== 'tree';
  $('vTree').setAttribute('aria-pressed', String(v === 'tree')); $('vGrid').setAttribute('aria-pressed', String(v === 'grid'));
  try { localStorage.setItem(UIKEY, JSON.stringify({ view: v })) } catch (e) { }
}

let bannerHidden = false;
function short(s, n) { return s.length > n ? s.slice(0, n - 1) + '…' : s }

function renderBanner() {
  const b = $('banner'); b.innerHTML = '';
  if (bannerHidden) { return }
  const ready = skills.filter(s => isReady(s.id)), q = queue();
  const started = skills.some(s => tierOf(s.id) > 0);
  b.append(el('span', {}, el('b', { text: started ? 'Go wide before deep. ' : 'Welcome! ' }),
    started ? 'New skills are recommended once their prerequisites reach Level 2, so go wide rather than racing one branch to Mastered; spaced mastery challenges stick better after a break.'
      : 'Pick a glowing "ready" skill (no prerequisites needed to start), then spread out across the tree. A new skill glows once its prerequisites reach Level 2.'));
  if (ready.length) b.append(el('span', { class: 'rd' }, el('b', { text: 'Ready to learn:' }), ready.slice(0, 2).map(s => el('button', { class: 'pill', style: colorVars(s.chapter), onclick: () => selectSkill(s.id, true), title: s.name }, short(s.name, 24))), ready.length > 2 ? el('span', { text: `+${ready.length - 2} more` }) : null));
  if (q.length) b.append(el('button', { class: 'pill', style: '--c:#ff7a59;--cs:#ffe3da', onclick: openQueue }, `${q.length} mastery challenge${q.length > 1 ? 's' : ''} waiting`));
  b.append(el('button', { class: 'x', 'aria-label': 'Dismiss tip', onclick: () => { bannerHidden = true; renderBanner() } }, '×'));
}

/* ====================== skill panel ====================== */
function selectSkill(id, focus) {
  selected = id;
  document.querySelectorAll('.tile[data-id]').forEach(refreshTile);
  placePanel(); panel.classList.add('open'); panel.setAttribute('aria-hidden', 'false');
  renderPanel(); applyEdgeHighlight();
  if (focus && filter.view === 'tree') focusTile(id);
  if (focus && filter.view === 'grid') { const t = document.querySelector(`#gridView .tile[data-id="${id}"]`); t && t.scrollIntoView({ block: 'center', behavior: 'smooth' }) }
}

function placePanel() { panel.style.top = quizOpen ? '0px' : document.querySelector('main').getBoundingClientRect().top + 'px' }

function closePanel() {
  const was = selected;
  panel.classList.remove('open'); panel.setAttribute('aria-hidden', 'true');
  selected = null; document.querySelectorAll('.tile[data-id]').forEach(refreshTile); applyEdgeHighlight();
  if (was && !quizOpen) { const vis = [...document.querySelectorAll(`.tile[data-id="${was}"]`)].find(x => x.offsetParent); vis && vis.focus({ preventScroll: true }) }
}

function tierPill(id) {
  const s = byId[id], t = tierOf(id);
  return el('button', { class: 'pill', style: colorVars(s.chapter), onclick: () => selectSkill(id, true), title: TIERS[t] + (isPlayable(id) ? '' : ' · coming soon') },
    el('span', { class: 'sw t' + t, style: `--f:${FILL[t]}%;width:14px;height:14px;border-color:${chColor(s.chapter)}` }), short(s.name, 40))
}

const need = n => Math.ceil(n * 2 / 3);

function renderPanel() {
  const id = selected; panel.innerHTML = ''; if (!id) return;
  const s = byId[id], t = tierOf(id), soon = !isPlayable(id), ready = isReady(id);
  const nextR = t + 1, kids = [];
  kids.push(el('button', { class: 'close', 'aria-label': 'Close panel', onclick: closePanel }, '×'));
  kids.push(el('div', { style: colorVars(s.chapter) }, el('span', { class: 'cpill', text: `Ch ${s.chapter} · ${DATA.chapters[s.chapter]}` })));
  kids.push(el('h2', { text: s.name, id: 'panelTitle' }));
  kids.push(el('div', { class: 'kv', text: `Reader section ${s.reader_section || '—'} · id: ${s.id}` }));
  if (soon) kids.push(el('div', { class: 'note soon', role: 'note' }, el('b', { text: 'Coming soon. ' }), "This skill is in the tree, but its questions haven't been written yet, so it can't be practiced in this demo."));
  else {
    kids.push(el('div', { class: 'steps', style: colorVars(s.chapter), role: 'img', 'aria-label': 'Tier: ' + TIERS[t] },
      TIERS.map((n, i) => el('div', { class: 'step' + (i <= t && i > 0 ? ' done' : '') + (i === t ? ' cur' : '') }, el('div', { class: 'dot', text: i > 0 && i <= t ? '✓' : '' }), n))));
    kids.push(el('div', { class: 'kv', id: 'panelTier' }, el('b', { text: 'Tier: ' }), TIERS[t], ready ? ' · ready to learn' : ''));
    kids.push(el('div', { class: 'kv', id: 'panelLast', title: lastOf(id) ? fmtDate(lastOf(id)) : '' }, el('b', { text: 'Last practiced: ' }), lastOf(id) ? `${ago(lastOf(id))} (${fmtDate(lastOf(id))})` : 'never'));
    const gaps = prereqGaps(id), soonP = s.prereqs.filter(p => !isPlayable(p));
    if (t === 0 && ready) kids.push(el('div', { class: 'note ok', id: 'readyNote' }, el('b', { text: 'Ready to learn: ' }), s.prereqs.length && s.prereqs.some(isPlayable) ? 'all its prerequisites are at Level 2 or Mastered.' : 'it has no prerequisites you can practice yet, so you can start right away.'));
    if (gaps.length && t === 0) kids.push(el('div', { class: 'note warn', id: 'prereqNote' }, el('b', { text: 'Gentle heads-up: ' }), `this skill is recommended once its prerequisites reach Level 2. Still to go: ${gaps.map(p => `${byId[p].name} (${TIERS[tierOf(p)]})`).join('; ')}. Nothing is locked, so start whenever you like.`));
    if (soonP.length) kids.push(el('div', { class: 'note info', id: 'soonNote' }, `${soonP.length} prerequisite${soonP.length > 1 ? 's are' : ' is'} coming soon (${soonP.map(p => byId[p].name).join('; ')}). ${soonP.length > 1 ? 'They have' : 'It has'} no questions yet, so ${soonP.length > 1 ? 'they are' : 'it is'} ignored when deciding whether this skill is ready.`));
    if (quizOpen) kids.push(el('div', { class: 'note info', text: 'Finish or leave the current quiz to start something new.' }));
    else if (t < 4) {
      const n = roundQsCount(id, nextR);
      if (!n) kids.push(el('div', { class: 'note soon', text: `Round ${nextR} questions aren't written yet for this skill.` }));
      else if (nextR === 1) {
        kids.push(el('button', { class: 'btn primary', style: 'width:100%;justify-content:center;margin-top:10px;padding:11px', id: 'startBtn', onclick: () => doStartQuiz(id, 1, 'practice') }, `Start Round 1 quiz · ${n} questions`));
        kids.push(el('div', { class: 'kv', style: 'margin-top:6px', text: 'A practice quiz, not a mastery challenge — available any time. Finish it to color the skill in as Practiced.' }));
      } else {
        kids.push(el('button', { class: 'btn hot', style: 'width:100%;justify-content:center;margin-top:10px;padding:11px', id: 'startBtn', onclick: () => doStartQuiz(id, nextR, 'challenge') }, `Start mastery challenge → ${TIERS[nextR]} · ${n} questions`));
        kids.push(el('div', { class: 'kv', style: 'margin-top:6px', text: `Get at least ${need(n)} of ${n} right to level up. If you miss, you keep your tier — no penalty, retry any time.` }));
      }
    } else {
      kids.push(el('div', { class: 'note ok', text: 'Mastered! This skill is fully colored in.' }));
      if (hasRound(id, 4)) kids.push(el('button', { class: 'btn', style: 'width:100%;justify-content:center', id: 'startBtn', onclick: () => doStartQuiz(id, 4, 'review') }, 'Review round 4 (no tier change)'));
    }
  }
  kids.push(el('h3', { text: 'Prerequisites' }));
  kids.push(s.prereqs.length ? el('div', { class: 'chips', id: 'prereqChips' }, s.prereqs.map(tierPill)) : el('div', { class: 'kv', text: 'None — a starting point.' }));
  const deps = dependents[id];
  kids.push(el('h3', { text: 'Leads to' }));
  kids.push(deps.length ? el('div', { class: 'chips' }, deps.map(tierPill)) : el('div', { class: 'kv', text: 'Nothing yet in this draft tree.' }));
  const hist = (progress.skills[id] && progress.skills[id].history || []).slice(-6).reverse();
  if (hist.length) {
    kids.push(el('h3', { text: 'Recent attempts' }));
    kids.push(el('div', { class: 'hist' }, hist.map(h => el('div', {}, `Round ${h.round}: ${h.correct}/${h.total} · `, el('span', { class: h.passed ? 'p' : 'f', text: h.round === 1 ? 'completed' : (h.passed ? 'passed' : 'not yet') }), ` · ${fmtDate(h.t)}`))));
  }
  panel.append(...kids);
  panel.scrollTop = 0;
}

/* ====================== quiz (with lazy bank loading) ====================== */
let quizEl;
let quiz = null;
let bankLoading = false;

function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[a[i], a[j]] = [a[j], a[i]] } return a }
const POSITIONAL = /(all|none|both|neither) of the (above|these|options)|none of these|all of these/i;

function prepareQ(q) {
  const p = { q, chosen: null, text: '', correct: null, done: false };
  if (q.type === 'mc') {
    let perm = q.options.map((_, i) => i);
    if (!q.options.some(o => POSITIONAL.test(o))) perm = shuffle(perm);
    p.perm = perm; p.opts = perm.map(i => q.options[i]); p.ci = perm.indexOf(q.correct_index);
  }
  return p;
}

async function doStartQuiz(id, round, mode) {
  if (bankLoading) return;
  
  const meta = bankMeta[id];
  if (!meta) { toast('No question bank for this skill.'); return; }
  
  if (!bankCache[id]) {
    bankLoading = true;
    renderPanel();
    const btn = $('startBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Loading questions…'; }
    
    try {
      await fetchBank(id);
    } catch (e) {
      bankLoading = false;
      if (btn) { btn.disabled = false; btn.textContent = 'Retry loading'; }
      openModal({
        title: 'Failed to load questions',
        body: el('p', { text: `Could not load the question bank for this skill: ${e.message || e}. Check your network connection and try again.` }),
        actions: [{ label: 'OK' }]
      });
      return;
    }
    bankLoading = false;
  }
  
  const qs = bankCache[id].filter(q => q.round === round);
  if (!qs.length) { toast('No questions for this round.'); return; }
  
  startQuiz(id, round, mode, qs);
}

function startQuiz(id, round, mode, qs) {
  quiz = { id, round, mode, items: qs.map(prepareQ), i: 0, result: null, t0: Date.now() };
  quizOpen = true; quizEl.classList.add('open'); document.body.style.overflow = 'hidden';
  closeModal(); renderPanel(); renderQuiz();
  if (panelOpen()) { panel.classList.remove('open'); panel.setAttribute('aria-hidden', 'true') }
}

function parseNum(s) {
  if (s == null) return NaN;
  s = String(s).trim().replace(/[\u2212\u2013\u2014]/g, '-').replace(/,/g, '').replace(/\s+/g, '').replace(/%$/, '');
  if (!s) return NaN;
  let m = s.match(/^([+-]?(?:\d+\.?\d*|\.\d+))(?:[eE]([+-]?\d+))?$/);
  if (m) return parseFloat(m[1] + (m[2] ? 'e' + m[2] : ''));
  m = s.match(/^([+-]?(?:\d+\.?\d*|\.\d+))[x×*·]10\^?\(?([+-]?\d+)\)?$/i);
  if (m) return parseFloat(m[1] + 'e' + m[2]);
  m = s.match(/^([+-]?\d+\.?\d*)\/(\d+\.?\d*)$/);
  if (m && parseFloat(m[2]) !== 0) return parseFloat(m[1]) / parseFloat(m[2]);
  return NaN;
}

function checkNumeric(q, txt) {
  const x = parseNum(txt); if (!Number.isFinite(x)) return null;
  const a = q.answer, tol = (q.tolerance != null ? q.tolerance : 0.02);
  if (a === 0) return Math.abs(x) <= 1e-6;
  return Math.abs(x - a) <= tol * Math.abs(a) * (1 + 1e-9);
}

function fmtAns(a) {
  if (a === 0) return '0';
  const ab = Math.abs(a);
  if (ab >= 1e6 || ab < 1e-3) { const [m, e] = a.toExponential(3).split('e'); return m.replace(/\.?0+$/, '') + '×10^' + Number(e) }
  return String(Number(a.toPrecision(6)));
}

const answerLine = it => it.q.type === 'mc' ? `Answer: ${'ABCD'[it.ci]}. ${it.opts[it.ci]}` : `Answer: ${fmtAns(it.q.answer)}${it.q.unit && it.q.unit !== '(unitless)' ? ' ' + it.q.unit : ''}`;

function renderQuiz() {
  const Q = quiz; if (!Q) return;
  const s = byId[Q.id]; quizEl.style.cssText = colorVars(s.chapter); quizEl.innerHTML = '';
  const wrap = el('div', { class: 'qwrap' }); quizEl.append(wrap);
  const label = Q.round === 1 ? 'Round 1 · Practice quiz' : `Round ${Q.round} · Mastery challenge → ${TIERS[Q.round]}`;
  wrap.append(el('div', { class: 'qtop' },
    el('button', { class: 'btn small', onclick: leaveQuiz, id: 'qLeave' }, '← Leave'),
    el('h2', { text: s.name }),
    el('span', { class: 'rbadge', id: 'rbadge', text: Q.mode === 'review' ? 'Review · no tier change' : label })));
  if (Q.result) { renderResult(wrap); quizEl.scrollTop = 0; return }
  const n = Q.items.length;
  wrap.append(el('div', { class: 'prog', role: 'img', 'aria-label': `Question ${Q.i + 1} of ${n}` }, Q.items.map((it, i) => el('i', { class: it.done ? (it.correct ? 'ok' : 'no') : (i === Q.i ? 'cur' : '') }))));
  if (Q.mode === 'challenge') wrap.append(el('div', { class: 'kv', id: 'rule', style: 'margin:-6px 0 10px', text: `Mastery challenge: get at least ${need(n)} of ${n} right to reach ${TIERS[Q.round]}. Missing it never costs you a tier.` }));
  else if (Q.mode === 'practice') wrap.append(el('div', { class: 'kv', id: 'rule', style: 'margin:-6px 0 10px', text: 'Practice quiz (not a mastery challenge): finish all questions to color this skill in as Practiced.' }));
  const it = Q.items[Q.i], q = it.q;
  const card = el('div', { class: 'qcard' });
  card.append(el('div', { class: 'qn', text: `Question ${Q.i + 1} of ${n}` }), figureNode(q), el('p', { class: 'qp', math: q.prompt, id: 'qPrompt', 'data-qid': q.id }));
  if (q.type === 'mc') {
    const box = el('div', { class: 'opts', role: 'group', 'aria-labelledby': 'qPrompt' });
    it.opts.forEach((o, i) => {
      let cls = 'opt';
      if (it.done) { if (i === it.ci) cls += ' right'; else if (i === it.chosen) cls += ' wrong' } else if (i === it.chosen) cls += ' sel';
      box.append(el('button', { class: cls, type: 'button', disabled: it.done, 'data-i': i, 'data-o': it.perm ? it.perm[i] : i, onclick: () => answerMC(i) }, el('span', { class: 'k', text: 'ABCD'[i] }), el('span', { class: 'ot', math: o })));
    });
    card.append(box);
  } else {
    const inp = el('input', { type: 'text', id: 'numIn', autocomplete: 'off', spellcheck: 'false', placeholder: 'Type a number', disabled: it.done, 'aria-label': 'Your answer' + (q.unit ? ' in ' + mathPlain(q.unit) : '') });
    inp.value = it.text; inp.addEventListener('input', () => it.text = inp.value);
    inp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); answerNum() } });
    card.append(el('div', { class: 'numrow' }, inp, q.unit && q.unit !== '(unitless)' ? el('span', { class: 'u', math: q.unit }) : null, el('button', { class: 'btn primary', id: 'checkBtn', disabled: it.done, onclick: answerNum }, 'Check')));
    if (!it.done) { card.append(el('div', { class: 'kv', style: 'margin-top:8px', text: `Plain numbers or scientific notation (like 2.5e-3) work. Accepted within ±${((q.tolerance != null ? q.tolerance : .02) * 100).toFixed(0)}%.` })); setTimeout(() => inp.focus(), 0) }
  }
  if (it.done) {
    const ok = it.correct;
    const fb = el('div', { class: 'fb ' + (ok ? 'ok' : 'no'), role: 'status', id: 'feedback' });
    fb.append(el('h4', { text: ok ? '✓ Correct!' : '✗ Not quite' }), el('div', { class: 'ans', math: answerLine(it) }), el('div', { class: 'ex', math: q.explanation || '' }));
    card.append(fb);
    if (Q.round === 4 && q.preview && q.preview.length) {
      card.append(el('div', { class: 'coming', id: 'coming' }, el('b', { text: 'Coming up: ' }), 'this skill feeds into ',
        q.preview.map((p, i) => [i ? ', ' : '', el('button', { class: 'pill', style: colorVars(byId[p].chapter), onclick: () => selectSkill(p, false), title: 'Open this skill' }, byId[p].name)])));
    }
    card.append(el('div', { class: 'qact' }, el('button', { class: 'btn primary', id: 'nextBtn', onclick: nextQ }, Q.i === n - 1 ? 'See results' : 'Next question →')));
  }
  wrap.append(card);
  if (it.done) { const nb = $('nextBtn'); nb && nb.focus({ preventScroll: true }); setTimeout(() => { const f = card.querySelector('.fb'); f && f.scrollIntoView({ block: 'nearest', behavior: 'smooth' }) }, 50) }
}

function answerMC(i) {
  const it = quiz.items[quiz.i]; if (it.done) return;
  it.chosen = i; it.done = true; it.correct = (i === it.ci); renderQuiz();
}

function answerNum() {
  const it = quiz.items[quiz.i]; if (it.done) return;
  const r = checkNumeric(it.q, it.text);
  if (r === null) { const inp = $('numIn'); inp.setAttribute('aria-invalid', 'true'); toast('Enter a number first (like 12.5 or 1e-3).'); inp.focus(); return }
  it.done = true; it.correct = r; renderQuiz();
}

function nextQ() {
  if (quiz.i < quiz.items.length - 1) { quiz.i++; renderQuiz(); quizEl.scrollTop = 0; return }
  finishQuiz();
}

function finishQuiz() {
  const Q = quiz, n = Q.items.length, correct = Q.items.filter(i => i.correct).length;
  const passed = Q.round === 1 ? true : correct >= need(n);
  const before = tierOf(Q.id); let after = before;
  if (Q.mode !== 'review') {
    const rec = sk(Q.id), now = Date.now();
    rec.history.push({ t: now, round: Q.round, correct, total: n, passed }); if (rec.history.length > 60) rec.history.splice(0, rec.history.length - 60);
    rec.lastPracticed = now;
    if (passed && rec.tier < Q.round) rec.tier = Q.round;
    after = rec.tier;
    saveProgress();
    recordTiming(Q.round === 1 ? 'practice' : 'challenge', (Date.now() - Q.t0) / 1000);
  }
  Q.result = { correct, n, passed, before, after };
  refreshAll();
  if (after > before) {
    document.querySelectorAll(`.tile[data-id="${Q.id}"]`).forEach(t => { t.classList.add('pop'); setTimeout(() => t.classList.remove('pop'), 900) });
    confetti();
  }
  renderQuiz();
}

function renderResult(wrap) {
  const Q = quiz, R = Q.result;
  const up = R.after > R.before;
  const card = el('div', { class: 'qcard result' });
  const msg = Q.mode === 'review' ? 'Review done' : up ? (R.after === 4 ? 'Mastered! ★' : `Level up! You're now ${TIERS[R.after]}`) : (Q.round === 1 ? 'Done' : "Not this time — and that's fine");
  card.append(el('div', { class: 'qn', text: Q.mode === 'review' ? 'Review' : (Q.round === 1 ? 'Practice quiz complete' : 'Mastery challenge result') }));
  card.append(el('div', { class: 'big', id: 'score', text: `${R.correct} / ${R.n}` }));
  card.append(el('h3', { style: 'margin:0 0 6px;font-size:21px', id: 'resMsg', text: msg }));
  if (Q.mode === 'challenge' && !R.passed) card.append(el('div', { class: 'kv', id: 'failNote', text: `You needed ${need(R.n)} of ${R.n}. Your tier stays at ${TIERS[R.before]} — read the explanations below and try again whenever you are ready.` }));
  if (Q.mode === 'practice' && R.correct < need(R.n)) card.append(el('div', { class: 'kv', text: 'Practiced is about showing up — but the explanations below are worth another look before you try a mastery challenge.' }));
  if (Q.mode !== 'review') {
    card.append(el('div', { class: 'tu' }, el('span', { class: 'tierchip', text: TIERS[R.before] }), up ? [el('span', { text: '→' }), el('span', { class: 'tierchip', id: 'newTier', text: TIERS[R.after] })] : el('span', { style: 'font-weight:600;color:var(--ink2)', text: '(unchanged)' })));
    card.append(el('div', { class: 'kv', text: storageOK ? 'Progress saved on this device ✓' : 'Progress kept in memory only (storage unavailable) — please Export a backup.' }));
  }
  const recap = el('div', { class: 'recap' });
  Q.items.forEach((it, i) => recap.append(el('div', {}, el('span', { class: 'm ' + (it.correct ? 'ok' : 'no'), text: it.correct ? '✓' : '✗' }), el('span', { math: `Q${i + 1}: ` + shortMath(it.q.prompt, 150) }))));
  card.append(recap);
  const btns = el('div', { class: 'rbtns' });
  btns.append(el('button', { class: 'btn', id: 'resBack', onclick: () => exitQuiz(Q.id) }, 'Back to the tree'));
  if (Q.mode === 'review' || (Q.mode === 'challenge' && !R.passed) || (Q.mode === 'practice' && R.correct < need(R.n))) btns.append(el('button', { class: 'btn', id: 'resRetry', onclick: () => doStartQuiz(Q.id, Q.round, Q.mode) }, 'Try this round again'));
  const qn = queue().filter(x => x.id !== Q.id)[0];
  const rd = skills.filter(x => isReady(x.id))[0];
  if (qn) btns.append(el('button', { class: 'btn hot', id: 'resNextQ', onclick: () => doStartQuiz(qn.id, tierOf(qn.id) + 1, 'challenge') }, `Next in queue: ${short(qn.name, 30)}`));
  if (rd && up) btns.append(el('button', { class: 'btn primary', id: 'resLearn', onclick: () => exitQuiz(rd.id) }, `Learn something new: ${short(rd.name, 26)}`));
  const t = tierOf(Q.id);
  if (up && t < 4 && hasRound(Q.id, t + 1)) btns.append(el('button', { class: 'btn', id: 'resSame', onclick: () => doStartQuiz(Q.id, t + 1, 'challenge') }, 'Challenge this skill again now'));
  card.append(btns);
  if (up && Q.mode !== 'review') card.append(el('div', { class: 'kv', style: 'margin-top:12px', text: 'Tip: spaced practice works best. Go learn something new, and this skill will wait in your mastery queue.' }));
  wrap.append(card);
  const ex = el('div', { style: 'margin-top:18px' });
  ex.append(el('h3', { style: 'margin:0 0 8px;font-size:14px;color:var(--ink2)', text: 'Explanations' }));
  Q.items.forEach((it, i) => ex.append(el('details', { style: 'background:#fff;border-radius:14px;padding:10px 14px;margin:8px 0;border:2px solid var(--line)', open: it.correct ? null : true },
    el('summary', { style: 'cursor:pointer;font-weight:650' }, `${it.correct ? '✓' : '✗'} Q${i + 1}`),
    figureNode(it.q, 'small'), el('p', { class: 'qp', style: 'font-size:14px;margin:8px 0', math: it.q.prompt }),
    el('div', { style: 'font-weight:700', math: answerLine(it) }),
    el('div', { class: 'ex', style: 'white-space:pre-wrap;font-size:13.5px', math: it.q.explanation || '' }))));
  wrap.append(ex);
}

function closeQuizUI() { quiz = null; quizOpen = false; quizEl.classList.remove('open'); quizEl.innerHTML = ''; document.body.style.overflow = '' }
function exitQuiz(id) { closeQuizUI(); selectSkill(id, true) }

function leaveQuiz() {
  if (quiz && quiz.result) { exitQuiz(quiz.id); return }
  openModal({ title: 'Leave this quiz?', body: el('p', { text: "Your answers in this attempt won't be saved, and your tier stays as it is." }), actions: [{ label: 'Keep going' }, { label: 'Leave quiz', kind: 'danger', id: 'confirmLeave', onClick: () => { const id = quiz.id; closeQuizUI(); selectSkill(id, false) } }] });
}

function confetti() {
  if (matchMedia('(prefers-reduced-motion:reduce)').matches) return;
  for (let i = 0; i < 46; i++) {
    const d = el('i', { class: 'conf', style: `left:${Math.random() * 100}vw;background:${PALETTE[i % PALETTE.length]};animation-duration:${1.6 + Math.random() * 1.6}s;animation-delay:${Math.random() * .4}s;border-radius:${Math.random() > .5 ? '50%' : '2px'}` });
    document.body.append(d); setTimeout(() => d.remove(), 4000);
  }
}

/* ====================== modal / queue ====================== */
let mb, mEl;
let modalFocusBack = null;

function openModal({ title, body, actions, wide }) {
  modalFocusBack = document.activeElement;
  mEl.innerHTML = ''; mEl.classList.toggle('wide', !!wide); mEl.append(el('h2', { text: title }), body);
  const acts = el('div', { class: 'acts' });
  (actions || [{ label: 'Close' }]).forEach(a => acts.append(el('button', { class: 'btn ' + (a.kind || ''), id: a.id || null, onclick: () => { closeModal(); a.onClick && a.onClick() } }, a.label)));
  mEl.append(acts); mb.classList.add('open');
  const f = mEl.querySelector('.acts .btn.primary,.acts .btn.hot') || mEl.querySelector('.acts .btn'); f && f.focus();
}

function closeModal() { if (!mb.classList.contains('open')) return; mb.classList.remove('open'); mEl.innerHTML = ''; try { modalFocusBack && modalFocusBack.focus && modalFocusBack.focus() } catch (e) { } }

function openQueue() {
  const q = queue();
  const body = el('div', { id: 'queueBody' });
  body.append(el('p', { text: 'These skills are Practiced or higher but not yet Mastered. The one you practiced least recently comes first — spacing your reviews out is what makes learning stick. Missing a challenge never drops your tier.' }));
  if (!q.length) body.append(el('div', { class: 'note info', text: 'Nothing waiting yet. Finish a Round 1 quiz on any skill to start a queue.' }));
  q.forEach((s, i) => {
    const t = tierOf(s.id);
    body.append(el('div', { class: 'qrow' + (i === 0 ? ' top' : ''), 'data-id': s.id, style: colorVars(s.chapter) },
      el('span', { class: 'rk', text: i + 1 }), el('span', { class: 'dotc' }),
      el('span', { class: 'nm' }, s.name, el('div', { class: 'sm', text: `${TIERS[t]} → ${TIERS[t + 1]} · last practiced ${ago(lastOf(s.id))}` })),
      el('button', { class: 'btn small ' + (i === 0 ? 'hot' : ''), onclick: () => { closeModal(); doStartQuiz(s.id, t + 1, 'challenge') } }, i === 0 ? 'Start top challenge' : 'Start')));
  });
  const ready = skills.filter(s => isReady(s.id));
  if (ready.length) body.append(el('div', { class: 'note info' }, el('b', { text: 'Breadth first: ' }), `${ready.length} new skill${ready.length > 1 ? 's are' : ' is'} ready to learn. Picking up a new one now gives your queued skills time to sink in.`));
  openModal({ title: 'Mastery challenges', body, actions: [{ label: 'Close' }] });
}

function openHelp() {
  const ul = el('ul', {},
    el('li', {}, el('b', { text: 'Five tiers: ' }), "Unpracticed → Practiced → Level 1 → Level 2 → Mastered. Tiles fill with their chapter's color as you climb."),
    el('li', {}, el('b', { text: 'Round 1 ' }), 'is a short practice quiz (not a mastery challenge). Finish it to become Practiced.'),
    el('li', {}, el('b', { text: 'Rounds 2–4 ' }), 'are mastery challenges: 3 questions, get at least 2 right to move up. Round 2 is harder, round 3 hunts for gotchas, round 4 applies the skill to what comes next.'),
    el('li', {}, 'Missing a challenge never costs a tier. Retry any time.'),
    el('li', {}, 'The mastery queue lists unmastered skills, least recently practiced first. Learn broadly first; come back for mastery.'),
    el('li', {}, 'Prerequisites are guidance, not locks. A new skill glows "ready" once all its prerequisites are at Level 2 or Mastered (prerequisites that are still coming soon are ignored). Lines show what leads to what; click a tile to highlight them.'),
    el('li', {}, el('b', { text: 'The tree grows upward: ' }), 'foundations (skills with no prerequisites) sit at the bottom and each skill that builds on them sits above.'),
    el('li', {}, el('b', { text: 'Learning plan ' }), 'simulates sessions (practice every ready skill, one mastery challenge per unmastered skill) to estimate how many sessions and how much time it takes to master everything playable. It learns how fast you are from your own timed quizzes.'),
    el('li', {}, el('b', { text: 'Group by chapter ' }), 'regroups the one big prerequisite tree into chapter blocks, and Ungroup flows it back.'),
    el('li', {}, 'Progress autosaves in this browser after every quiz. Use Export for a backup file you can Import later (or on another device).'),
    el('li', {}, 'Content: EE 105 (Niknejad reader), draft. Only some skills have questions so far; the rest say "coming soon".'));
  openModal({ title: 'How Skillgrove works', body: ul, actions: [{ label: 'Got it', kind: 'primary' }] });
}

/* ====================== learning plan (course simulation) ====================== */
const TKEY = 'skilltree.timing.v1';
const Sim = window.SkillSim;
let timing;

function loadTiming() { timing = Sim.normalizeTiming(null); try { const r = localStorage.getItem(TKEY); if (r) timing = Sim.normalizeTiming(JSON.parse(r)) } catch (e) { } }
function saveTiming() { if (!storageOK) return; try { localStorage.setItem(TKEY, JSON.stringify(timing)) } catch (e) { } }

function recordTiming(kind, seconds) {
  const r = Sim.addSample(timing[kind], seconds, Date.now());
  if (r.added) { timing[kind] = r.list; saveTiming() }
  return r.added;
}

const planState = { scratch: false, open: null };

function planGraph() {
  const ids = playable.map(s => s.id), prereqs = {}, maxTier = {};
  ids.forEach(id => { prereqs[id] = byId[id].prereqs.slice(); let t = 0; while (hasRound(id, t + 1)) t++; maxTier[id] = t });
  return { ids, prereqs, maxTier };
}

function planEstimates() {
  const out = {};
  [['practice', 'practice'], ['challenge', 'challenge']].forEach(([k]) => {
    const e = Sim.estimate(timing[k]), ov = timing.override[k];
    out[k] = { measured: e, used: ov != null ? ov : e.minutes, overridden: ov != null };
  });
  return out;
}

function runPlan(scratch) {
  const g = planGraph(), start = {};
  if (!scratch) g.ids.forEach(id => start[id] = tierOf(id));
  const est = planEstimates();
  return Sim.simulate(g, start, { practiceMin: est.practice.used, challengeMin: est.challenge.used });
}

function renderPlanBadge() {
  const b = $('planCount'); if (!b) return;
  const r = runPlan(false);
  b.textContent = r.ok ? (r.sessions ? r.sessions : '✓') : '?';
  $('btnPlan').title = r.ok ? (r.sessions ? `About ${r.sessions} more learning session${r.sessions === 1 ? '' : 's'} (~${Sim.fmtDuration(r.totalMinutes)}) to master the ${r.scope} playable skills — click for the plan` : `All ${r.scope} playable skills are mastered — nothing left to plan`) : 'Learning plan';
}

const TIER_COL = ['#d5dae6', '#ffd36b', '#8bd36b', '#3cb6c9', '#7c6cff'];
const SVGNS = 'http://www.w3.org/2000/svg';
function sv(tag, attrs, ...kids) { const e = document.createElementNS(SVGNS, tag); for (const k in attrs || {}) e.setAttribute(k, attrs[k]); kids.flat().forEach(c => { if (c != null) e.append(typeof c === 'string' ? document.createTextNode(c) : c) }); return e }
function fmtMin(m) { return Sim.fmtDuration(m) }

function minuteChart(r) {
  const W = 660, H = 210, L = 44, R = 48, T = 14, B = 34, n = r.rows.length;
  const nice = m => 4 * ([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 200, 250, 300, 400, 500, 750, 1000].find(v => v * 4 >= m) || 2000);
  const maxM = Math.max(10, ...r.rows.map(x => x.minutes)), maxC = nice(Math.max(1, r.totalMinutes));
  const niceMax = nice(maxM), bw = Math.min(34, (W - L - R) / n * .72), step = (W - L - R) / n;
  const y = v => T + (H - T - B) * (1 - v / niceMax), yc = v => T + (H - T - B) * (1 - v / maxC);
  const svg = sv('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', role: 'img', id: 'minChart', 'aria-label': `Minutes per session across ${n} sessions, total ${fmtMin(r.totalMinutes)}`, style: 'max-width:' + W + 'px;display:block' });
  for (let g = 0; g <= 4; g++) {
    const v = niceMax * g / 4; svg.append(sv('line', { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: '#e6eaf2' }), sv('text', { x: L - 6, y: y(v) + 4, 'text-anchor': 'end', 'font-size': 10, fill: '#8a93a7' }, String(Math.round(v))));
    const c = maxC * g / 4; svg.append(sv('text', { x: W - R + 6, y: yc(c) + 4, 'font-size': 10, fill: '#c2542f' }, String(Math.round(c))))
  }
  svg.append(sv('text', { x: L - 6, y: 8, 'text-anchor': 'end', 'font-size': 9.5, fill: '#8a93a7' }, 'min'), sv('text', { x: W - R + 6, y: 8, 'font-size': 9.5, fill: '#c2542f' }, 'total'));
  const pts = [];
  r.rows.forEach((row, i) => {
    const cx = L + step * (i + .5), pm = row.practiced.length * r.practiceMin, cm = row.challenges.length * r.challengeMin;
    svg.append(sv('rect', { x: cx - bw / 2, y: y(pm + cm), width: bw, height: Math.max(0, y(0) - y(pm + cm)), fill: '#ff9f43', rx: 3 }, sv('title', {}, `Session ${row.n}: ${fmtMin(row.minutes)} (${row.practiced.length} new × ${r.practiceMin} min + ${row.challenges.length} challenges × ${r.challengeMin} min)`)));
    if (pm > 0) svg.append(sv('rect', { x: cx - bw / 2, y: y(pm), width: bw, height: y(0) - y(pm), fill: '#7c6cff', rx: 3 }));
    if (n <= 26 || row.n % 2 === 1) svg.append(sv('text', { x: cx, y: H - B + 14, 'text-anchor': 'middle', 'font-size': 10, fill: '#4b566b' }, String(row.n)));
    pts.push([cx, yc(row.cumulative)]);
  });
  svg.append(sv('polyline', { points: pts.map(p => p.join(',')).join(' '), fill: 'none', stroke: '#c2542f', 'stroke-width': 2, 'stroke-dasharray': '5 3' }));
  pts.forEach(p => svg.append(sv('circle', { cx: p[0], cy: p[1], r: 2.6, fill: '#c2542f' })));
  svg.append(sv('text', { x: (L + W - R) / 2, y: H - 4, 'text-anchor': 'middle', 'font-size': 10.5, fill: '#4b566b' }, 'Session number'));
  return svg;
}

function tierChart(r) {
  const W = 660, H = 200, L = 44, R = 14, T = 12, B = 34, cols = [{ n: 0, tiers: r.startCounts }].concat(r.rows.map(x => ({ n: x.n, tiers: x.tiers }))), k = cols.length;
  const step = (W - L - R) / k, bw = Math.min(30, step * .74), tot = r.scope || 1;
  const svg = sv('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', role: 'img', id: 'tierChart', 'aria-label': 'Number of skills at each tier after each session', style: 'max-width:' + W + 'px;display:block' });
  const y = v => T + (H - T - B) * (1 - v / tot);
  for (let g = 0; g <= 4; g++) { const v = Math.round(tot * g / 4); svg.append(sv('line', { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: '#e6eaf2' }), sv('text', { x: L - 6, y: y(v) + 4, 'text-anchor': 'end', 'font-size': 10, fill: '#8a93a7' }, String(v))) }
  cols.forEach((c, i) => {
    const cx = L + step * (i + .5); let acc = 0;
    for (let t = 4; t >= 0; t--) {
      const v = c.tiers[t]; if (!v) continue;
      svg.append(sv('rect', { x: cx - bw / 2, y: y(acc + v), width: bw, height: y(acc) - y(acc + v), fill: TIER_COL[t], stroke: '#fff', 'stroke-width': .6 }, sv('title', {}, `${i === 0 ? 'Start' : 'After session ' + c.n}: ${v} skill${v === 1 ? '' : 's'} at ${TIERS[t]}`))); acc += v
    }
    if (k <= 27 || i % 2 === 0) svg.append(sv('text', { x: cx, y: H - B + 14, 'text-anchor': 'middle', 'font-size': 10, fill: '#4b566b' }, i === 0 ? 'start' : String(c.n)));
  });
  svg.append(sv('text', { x: (L + W - R) / 2, y: H - 4, 'text-anchor': 'middle', 'font-size': 10.5, fill: '#4b566b' }, 'After session'));
  return svg;
}

function planResults(box) {
  box.innerHTML = '';
  const r = runPlan(planState.scratch);
  if (!r.ok) { box.append(el('div', { class: 'note warn', id: 'planStuck', text: 'The simulation got stuck: some skill can never become ready. This should not happen — please tell Isaac.' })); return }
  const est = planEstimates();
  if (!r.sessions) {
    box.append(el('div', { class: 'note ok', id: 'planDone' }, el('b', { text: '0 sessions. ' }), `All ${r.scope} playable skills are already Mastered, so there is nothing left to plan. The total will grow when more question banks are added.`));
    return;
  }
  box.append(el('div', { class: 'pcards', id: 'planCards' },
    el('div', { class: 'pc' }, el('div', { class: 'pn', id: 'planSessions', text: r.sessions }), el('div', { class: 'pl', text: r.sessions === 1 ? 'learning session' : 'sequential learning sessions' })),
    el('div', { class: 'pc' }, el('div', { class: 'pn', id: 'planTotal', text: fmtMin(r.totalMinutes) }), el('div', { class: 'pl', text: 'total study time' })),
    el('div', { class: 'pc' }, el('div', { class: 'pn sm', id: 'planWork', text: `${r.practiceCount} + ${r.challengeCount}` }), el('div', { class: 'pl', text: 'practice quizzes + mastery challenges' }))));
  const names = r.critical.chain.map(id => byId[id].name);
  const cp = el('div', { class: 'cpath', id: 'planCritical' }, el('b', { text: 'Critical path: ' }));
  if (names.length) {
    names.forEach((n, i) => { if (i) cp.append(el('span', { class: 'arr', text: ' ↑ ' })); cp.append(el('span', { class: 'cpn', text: n })) });
    cp.append(el('div', { class: 'kv', style: 'margin-top:5px' }, names.length > 1
      ? `${names.length} skills deep. A skill can only be practiced in the session after all its prerequisites reached Level 2, and a skill needs 3 more sessions after practice to climb Level 1 → Level 2 → Mastered (one step per session so the spacing sinks in)` + (r.sessions === 3 * names.length + 1 ? `. That is why the plan takes 3 × ${names.length} + 1 = ${r.sessions} sessions: more study time per session wouldn't shorten it, only a shallower chain would.` : '.')
      : `This is just the remaining challenges on a single skill (one step up per session).`));
  }
  box.append(cp);
  box.append(el('h3', { class: 'ph', text: 'Minutes per session' }), minuteChart(r),
    el('div', { class: 'lgd' }, el('span', {}, el('i', { style: 'background:#7c6cff' }), 'new-skill practice'), el('span', {}, el('i', { style: 'background:#ff9f43' }), 'mastery challenges'), el('span', {}, el('i', { style: 'background:#c2542f;height:3px;border-radius:2px' }), 'cumulative total (right axis)')));
  box.append(el('h3', { class: 'ph', text: 'Skills at each tier after each session' }), tierChart(r),
    el('div', { class: 'lgd' }, TIERS.map((n, t) => el('span', {}, el('i', { style: `background:${TIER_COL[t]}` }), n))));
  box.append(el('h3', { class: 'ph', text: 'Session by session' }));
  const tb = el('table', { class: 'ptab', id: 'planTable' }, el('thead', {}, el('tr', {}, ['#', 'New skills practiced', 'Challenges', 'Session', 'Total so far', 'Tiers after (Unp · Pra · L1 · L2 · Mas)'].map(h => el('th', { text: h })))));
  const body = el('tbody');
  r.rows.forEach(row => {
    const open = planState.open === row.n;
    const sums = row.tiers.map((v, t) => v ? el('span', { style: `flex:${v};background:${TIER_COL[t]}`, title: `${v} at ${TIERS[t]}` }) : null);
    body.append(el('tr', { class: 'prow' + (open ? ' open' : ''), 'data-n': row.n, tabindex: '0', role: 'button', 'aria-expanded': String(open), title: 'Click to list the skills', onclick: () => { planState.open = planState.open === row.n ? null : row.n; planResults(box) }, onkeydown: e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.currentTarget.click() } } },
      el('td', { text: row.n }), el('td', { text: row.practiced.length ? String(row.practiced.length) : '–' }), el('td', { text: row.challenges.length ? String(row.challenges.length) : '–' }), el('td', { text: fmtMin(row.minutes) }), el('td', { text: fmtMin(row.cumulative) }),
      el('td', {}, el('div', { class: 'mini' }, sums), el('span', { class: 'mt', text: row.tiers.join(' · ') }))));
    if (open) {
      body.append(el('tr', { class: 'pdet' }, el('td', { colspan: 6 },
        row.practiced.length ? el('div', {}, el('b', { text: 'Practice (Round 1): ' }), row.practiced.map(id => byId[id].name).join('; ')) : null,
        row.challenges.length ? el('div', {}, el('b', { text: 'Mastery challenges: ' }), row.challenges.map(c => `${byId[c.id].name} (${TIERS[c.from]} → ${TIERS[c.to]})`).join('; ')) : null)));
    }
  });
  tb.append(body); box.append(el('div', { class: 'ptabwrap' }, tb));
}

function estimateCaption(k, label) {
  const e = planEstimates()[k], m = e.measured;
  const unit = k === 'practice' ? 'new-skill practice quiz' : 'mastery challenge';
  if (e.overridden) return `Using your typed value: ${e.used} min per ${unit}. (${m.source === 'measured' ? `Your measured average is ${m.minutes} min from ${m.n} sample${m.n === 1 ? '' : 's'}` : `No measured average yet — ${m.n} of ${m.need} timed quizzes so far, default ${Sim.DEFAULT_MIN} min`}.)`;
  if (m.source === 'measured') return `Using your average: ${m.minutes} min per ${unit} (${m.n} samples).`;
  return `Using default ${Sim.DEFAULT_MIN} min per ${unit}. Your own average replaces it after ${m.need} timed quizzes (${m.n} so far).`;
}

function openPlan() {
  const body = el('div', { id: 'planBody' });
  const results = el('div', { id: 'planResults' });
  const refreshNotes = () => {
    $('estNoteP').textContent = estimateCaption('practice'); $('estNoteC').textContent = estimateCaption('challenge');
    $('estResetP').hidden = !timing.override.practice; $('estResetC').hidden = !timing.override.challenge;
  };
  body.append(el('p', { class: 'pintro', text: 'Each simulated learning session: practice every skill that is ready (all its prerequisites at Level 2 or Mastered), and take one mastery challenge on every skill that is practiced but not yet mastered. A skill moves up one step per session — so it never jumps ahead within a session — and we repeat until everything is Mastered.' }));
  body.append(el('div', { class: 'note info', id: 'planScope' }, el('b', { text: 'Scope: ' }), `only the ${playable.length} playable skills (the ones with questions written) are simulated. The other ${skills.length - playable.length} "coming soon" skills are excluded, so these totals will grow as more question banks are added.`));
  const seg = el('div', { class: 'seg', role: 'group', 'aria-label': 'Where the simulation starts' },
    el('button', { id: 'planCur', 'aria-pressed': String(!planState.scratch), onclick: () => setScratch(false) }, 'From my progress'),
    el('button', { id: 'planScr', 'aria-pressed': String(planState.scratch), onclick: () => setScratch(true) }, 'Start from scratch'));
  const setScratch = v => { planState.scratch = v; planState.open = null; $('planCur').setAttribute('aria-pressed', String(!v)); $('planScr').setAttribute('aria-pressed', String(v)); $('planStartNote').textContent = v ? 'Pretending every playable skill is Unpracticed. Your real progress is not touched.' : `Starting from your saved progress (${playable.filter(s => tierOf(s.id) > 0).length} of ${playable.length} playable skills already practiced).`; planResults(results) };
  body.append(el('div', { class: 'prow2' }, seg, el('span', { class: 'kv', id: 'planStartNote', style: 'margin:0' })));
  const mkInp = (k, idIn, idNote, idReset, label) => {
    const inp = el('input', { type: 'number', id: idIn, min: '0.5', max: '600', step: '0.5', 'aria-label': label });
    const e = planEstimates()[k]; inp.value = String(e.used);
    inp.addEventListener('input', () => { const v = parseFloat(inp.value); if (isFinite(v) && v > 0 && v <= 600) { timing.override[k] = v; saveTiming(); refreshNotes(); planResults(results); renderPlanBadge() } });
    const reset = el('button', { class: 'btn small', id: idReset, type: 'button', onclick: () => { timing.override[k] = null; saveTiming(); inp.value = String(planEstimates()[k].used); refreshNotes(); planResults(results); renderPlanBadge() } }, 'Use my average / default');
    return el('div', { class: 'est' }, el('label', { for: idIn, text: label }), el('div', { class: 'er' }, inp, el('span', { text: 'min' }), reset), el('div', { class: 'kv', id: idNote, style: 'margin:2px 0 0' }));
  };
  body.append(el('div', { class: 'ests' }, mkInp('practice', 'estPractice', 'estNoteP', 'estResetP', 'Minutes per new-skill practice quiz'), mkInp('challenge', 'estChallenge', 'estNoteC', 'estResetC', 'Minutes per mastery challenge')));
  body.append(results);
  openModal({ title: 'Learning plan — how many sessions to master everything?', body, actions: [{ label: 'Close', kind: 'primary' }], wide: true });
  refreshNotes(); setScratch(planState.scratch);
}

/* ====================== export / import / reset ====================== */
function exportProgress() {
  const out = { version: 1, app: 'skillgrove', exportedAt: new Date().toISOString(), skills: progress.skills, timing: { practice: timing.practice, challenge: timing.challenge } };
  const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
  const a = el('a', { href: URL.createObjectURL(blob), download: `skillgrove-progress-${new Date().toISOString().slice(0, 10)}.json` });
  document.body.append(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove() }, 500);
  toast('Progress exported.');
}

function importFile(file) {
  const r = new FileReader();
  r.onerror = () => toast('Could not read that file.');
  r.onload = () => {
    let raw; try { raw = JSON.parse(r.result) } catch (e) { openModal({ title: 'Import failed', body: el('p', { id: 'impErr', text: "That file isn't valid JSON." }), actions: [{ label: 'OK' }] }); return }
    const p = normalizeProgress(raw);
    if (!p) { openModal({ title: 'Import failed', body: el('p', { id: 'impErr', text: "That doesn't look like a Skillgrove progress file (expected version 1 with a \"skills\" object)." }), actions: [{ label: 'OK' }] }); return }
    const ids = Object.keys(p.skills), known = ids.filter(i => byId[i]), unknown = ids.length - known.length;
    const impT = (raw.timing && typeof raw.timing === 'object') ? Sim.normalizeTiming(raw.timing) : null;
    const nT = impT ? impT.practice.length + impT.challenge.length : 0;
    const body = el('div', {}, el('p', { text: `The file has progress for ${known.length} skill${known.length === 1 ? '' : 's'}` + (unknown ? ` (${unknown} unknown skill id${unknown > 1 ? 's' : ''} will be kept but not shown)` : '') + (nT ? ` and ${nT} quiz-timing sample${nT === 1 ? '' : 's'}` : '') + '.' }),
      el('p', {}, el('b', { text: 'Merge' }), ' keeps the higher tier and latest practice time for each skill. ', el('b', { text: 'Replace' }), " discards what's on this device."));
    openModal({
      title: 'Import progress', body, actions: [{ label: 'Cancel' },
      { label: 'Replace', kind: 'danger', id: 'impReplace', onClick: () => { progress = p; if (impT) { timing.practice = impT.practice; timing.challenge = impT.challenge; saveTiming() } afterImport('Progress replaced.') } },
      {
        label: 'Merge', kind: 'primary', id: 'impMerge', onClick: () => {
          for (const id of ids) {
            const a = progress.skills[id], b = p.skills[id];
            if (!a) { progress.skills[id] = b; continue }
            const seen = new Set(a.history.map(h => h.t));
            const hist = a.history.concat(b.history.filter(h => !seen.has(h.t))).sort((x, y) => x.t - y.t).slice(-60);
            progress.skills[id] = { tier: Math.max(a.tier, b.tier), lastPracticed: Math.max(a.lastPracticed || 0, b.lastPracticed || 0) || null, history: hist };
          }
          if (impT) { timing.practice = Sim.mergeSamples(timing.practice, impT.practice); timing.challenge = Sim.mergeSamples(timing.challenge, impT.challenge); saveTiming() }
          afterImport('Progress merged.');
        }
      }]
    });
  };
  r.readAsText(file);
}

function afterImport(msg) { saveProgress(); refreshAll(); if (selected) renderPanel(); toast(msg) }

function resetProgress() {
  openModal({
    title: 'Reset all progress?', body: el('p', { text: 'This erases every tier on this device. Tip: Export first if you might want it back.' }),
    actions: [{ label: 'Cancel' }, { label: 'Export first', onClick: exportProgress }, { label: 'Reset everything', kind: 'danger', id: 'confirmReset', onClick: () => { progress = { version: 1, skills: {} }; saveProgress(); refreshAll(); if (selected) renderPanel(); toast('Progress reset.') } }]
  });
}

/* ====================== keyboard ====================== */
function setupKeyboard() {
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if (mb.classList.contains('open')) closeModal();
      else if (quizOpen) leaveQuiz();
      else if (panelOpen()) closePanel();
      return;
    }
    if (quiz && !quiz.result && !mb.classList.contains('open')) {
      const it = quiz.items[quiz.i];
      if (it.q.type === 'mc' && !it.done && /^[1-4a-dA-D]$/.test(e.key) && !e.ctrlKey && !e.metaKey && !e.altKey) { const i = '1234'.includes(e.key) ? +e.key - 1 : 'abcd'.indexOf(e.key.toLowerCase()); if (i < it.opts.length) answerMC(i) }
    }
  });
}

/* ====================== init ====================== */
async function init() {
  const loading = $('loadingOverlay');
  
  const ok = await loadManifest();
  
  if (!ok) {
    loading.innerHTML = `<div style="text-align:center;padding:40px"><h2 style="color:#e5484d">Failed to load</h2><p>${loadError}</p><button class="btn primary" onclick="location.reload()">Retry</button></div>`;
    return;
  }
  
  loading.remove();
  
  initData();
  playable = skills.filter(s => isPlayable(s.id));
  allEdges = []; skills.forEach(s => s.prereqs.forEach(p => allEdges.push([p, s.id])));
  
  world = $('world');
  tv = $('treeView');
  edgesSvg = $('edges');
  panel = $('panel');
  quizEl = $('quiz');
  mb = $('modalBack');
  mEl = $('modal');
  
  loadProgress();
  loadTiming();
  $('playableNote').textContent = `${playable.length} of ${skills.length} skills playable`;
  buildTree(); buildGrid(); legendBuild();
  
  try { const u = JSON.parse(localStorage.getItem(UIKEY) || 'null'); if (u && u.view === 'grid') filter.view = 'grid' } catch (e) { }
  let startMode = 'tree'; try { if (localStorage.getItem(LAYKEY) === 'grouped') startMode = 'grouped' } catch (e) { }
  showLayout(startMode, false);
  refreshAll(); setView(filter.view);
  goHome(false);
  
  setupPanZoom();
  setupKeyboard();
  
  $('btnExport').onclick = exportProgress;
  $('btnImport').onclick = () => $('fileIn').click();
  $('fileIn').onchange = e => { const f = e.target.files[0]; if (f) importFile(f); e.target.value = '' };
  $('btnPlan').onclick = openPlan;
  $('btnReset').onclick = resetProgress;
  $('btnQueue').onclick = openQueue;
  $('btnHelp').onclick = openHelp;
  mb.addEventListener('mousedown', e => { if (e.target === mb) closeModal() });
  window.addEventListener('resize', () => { if (panelOpen()) placePanel() });
  
  window.__skillgrove = {
    version: 1, storageOK: () => storageOK, layout: () => layout, mode: () => layoutMode, timing: () => timing, plan: (scratch) => runPlan(!!scratch), ready: () => skills.filter(s => isReady(s.id)).map(s => s.id), playableIds: () => playable.map(s => s.id),
    qa: { bankMeta: () => bankMeta, bankCache: () => bankCache, fetchBank, prepareQ, renderQuiz, setQuiz: q => { quiz = q }, closeQuizUI, openQuiz: () => quizEl.classList.add('open'), figureNode, katexErrors: () => window.__katexErrors },
    openModal, toast, reloadProgress: loadProgress, reloadTiming: loadTiming, refreshAll
  };
  
  if (window.SkillgroveAuth) {
    window.SkillgroveAuth.init();
  }
}

init();
})();
