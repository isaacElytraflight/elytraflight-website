(function(){
'use strict';
/* Skillgrove — mastery-based skill tree for undergraduate STEM courses
   Multi-file version: loads skills graph at startup, banks lazily on quiz open */

/* ====================== base URL detection ====================== */
const BASE_URL = (function() {
  const scripts = document.getElementsByTagName('script');
  for (let i = scripts.length - 1; i >= 0; i--) {
    const src = scripts[i].src;
    if (src && src.includes('skilltree.js')) {
      return src.replace(/skilltree\.js.*$/, '');
    }
  }
  const p = location.pathname;
  if (p.indexOf('/skilltree') === 0) {
    return location.origin + p.replace(/\/skilltree\/?.*/, '/skilltree/');
  }
  return '';
})();

/* ====================== data loading ====================== */
let DATA = null;       // loaded from skills.*.json
let COLLECTIONS = null; // loaded from collections.*.json
let bankCache = {};    // skill_id -> loaded bank questions
let bankMeta = {};     // skill_id -> {file, hash, questionCount, rounds}
let explainerCache = {};  // skill_id -> loaded explainer
let explainerMeta = {};   // skill_id -> {file, hash, sectionCount}
let boxById = {};      // box_id -> box object
let skillToBoxes = {}; // skill_id -> [box_ids] (all boxes containing this skill)
let parentOfBox = {};  // box_id -> parent box_id
let dataReady = false;
let loadError = null;

async function loadManifest() {
  try {
    const mRes = await fetch(BASE_URL + 'manifest.json');
    if (!mRes.ok) throw new Error(`manifest.json: ${mRes.status}`);
    const manifest = await mRes.json();
    
    const sRes = await fetch(BASE_URL + manifest.skills.file);
    if (!sRes.ok) throw new Error(`${manifest.skills.file}: ${sRes.status}`);
    DATA = await sRes.json();
    
    if (manifest.collections) {
      const cRes = await fetch(BASE_URL + manifest.collections.file);
      if (cRes.ok) {
        COLLECTIONS = await cRes.json();
        initCollections();
      }
    }
    
    bankMeta = DATA.banks || {};
    explainerMeta = DATA.explainers || {};
    dataReady = true;
    return true;
  } catch (e) {
    loadError = e.message || String(e);
    console.error('Skillgrove load error:', e);
    return false;
  }
}

function initCollections() {
  if (!COLLECTIONS || !COLLECTIONS.boxes) return;
  boxById = {};
  skillToBoxes = {};
  parentOfBox = {};
  
  for (const box of COLLECTIONS.boxes) {
    boxById[box.id] = box;
    for (const sid of (box.skills || [])) {
      if (!skillToBoxes[sid]) skillToBoxes[sid] = [];
      skillToBoxes[sid].push(box.id);
    }
    for (const cid of (box.children || [])) parentOfBox[cid] = box.id;
  }
}

function getSkillBox(skillId) {
  const boxIds = skillToBoxes[skillId];
  if (!boxIds || boxIds.length === 0) return null;
  return boxById[boxIds[0]];
}

function getSkillColorIndex(skillId) {
  const chapters = chaptersFor(skillId, filter && filter.box);
  const box = chapters.find(b => b.color_index != null) || getSkillBox(skillId);
  if (box && box.color_index != null) return box.color_index;
  const s = byId[skillId];
  return (s && s.chapter) || 1;
}

async function fetchBank(skillId) {
  if (bankCache[skillId]) return bankCache[skillId];
  const meta = bankMeta[skillId];
  if (!meta) return null;
  
  try {
    const res = await fetch(BASE_URL + meta.file);
    if (!res.ok) throw new Error(`${meta.file}: ${res.status}`);
    const data = await res.json();
    bankCache[skillId] = data.questions || [];
    return bankCache[skillId];
  } catch (e) {
    console.error(`Failed to load bank ${skillId}:`, e);
    throw e;
  }
}

async function fetchExplainer(skillId) {
  if (explainerCache[skillId]) return explainerCache[skillId];
  const meta = explainerMeta[skillId];
  if (!meta) return null;
  
  try {
    const res = await fetch(BASE_URL + meta.file);
    if (!res.ok) throw new Error(`${meta.file}: ${res.status}`);
    const data = await res.json();
    explainerCache[skillId] = data;
    return data;
  } catch (e) {
    console.error(`Failed to load explainer ${skillId}:`, e);
    throw e;
  }
}

/* ====================== constants & helpers ====================== */
const KEY='skilltree.progress.v1', UIKEY='skilltree.ui.v1';
const PLAN_SCOPE_KEY='skilltree.planscope.v1';
const COLLAPSE_KEY='skilltree.collapsed.v1';
const TIERS=['Unpracticed','Practiced','Level 1','Level 2','Mastered'];
const FILL=[0,30,55,80,100];
const PALETTE=['#ff6b6b','#ff9f43','#f4b400','#8bc34a','#2ed47a','#14c1a8','#22b8e6','#4c8dff','#7c6cff','#b15cff','#e25ce0','#ff5c9d','#f2784b','#6fae2e','#1fa39a','#5a7bef','#9a63d9','#d9588a'];

let skills, byId, dependents, chNums;

function initData() {
  skills = DATA.skills;
  byId = {};
  skills.forEach(s => byId[s.id] = s);
  dependents = {};
  skills.forEach(s => { if (!s.prereqs) s.prereqs = []; dependents[s.id] = []; });
  skills.forEach(s => s.prereqs.forEach(p => { if (dependents[p]) dependents[p].push(s.id); }));
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
const hasExplainer = id => !!(explainerMeta[id] && explainerMeta[id].sectionCount > 0);
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

function applyRetirement(p) {
  if (!p || !window.SkillgroveMigrate) return { progress: p, changed: false };
  return window.SkillgroveMigrate.migrateRetiredProgress(p, (DATA && DATA.retired) || {});
}

function loadProgress() {
  storageOK = probeStorage();
  if (!storageOK) { showWarn('Browser storage is unavailable here, so progress will be lost when you close this tab. Use Export (top right) to save a backup file.'); return }
  let raw = null;
  try { raw = localStorage.getItem(KEY) } catch (e) { storageOK = false }
  if (!raw) return;
  try {
    const p = normalizeProgress(JSON.parse(raw));
    if (p) {
      const mig = applyRetirement(p);
      progress = mig.progress;
      if (mig.changed) saveProgress();
      return;
    }
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
function colorVars(ch) { const c = chColor(ch || 1); return `--c:${c};--cs:${rgba(c, .5)};--cs2:${rgba(c, .78)};--tc:${textOn(c)};--bg:${rgba(c, .1)};--cb:${rgba(c, .55)}` }
function colorOf(id) { return colorVars(getSkillColorIndex(id)); }

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

function topLevelBoxes() {
  if (!COLLECTIONS || !COLLECTIONS.boxes) return [];
  const childIds = new Set();
  COLLECTIONS.boxes.forEach(b => (b.children || []).forEach(id => childIds.add(id)));
  return COLLECTIONS.boxes.filter(b => !childIds.has(b.id));
}

function scopeRootId(boxId) {
  let cur = boxId;
  const seen = new Set();
  while (cur && parentOfBox[cur] && !seen.has(cur)) {
    seen.add(cur);
    cur = parentOfBox[cur];
  }
  return cur || boxId;
}

function layoutRoot() {
  return filter.box ? scopeRootId(filter.box) : null;
}

function isDescendantBox(boxId, ancestorId) {
  let cur = boxId;
  const seen = new Set();
  while (cur && !seen.has(cur)) {
    if (cur === ancestorId) return true;
    seen.add(cur);
    cur = parentOfBox[cur];
  }
  return false;
}

function visibleContainers() {
  const tops = topLevelBoxes();
  const root = layoutRoot();
  if (!root) return tops;
  return tops.filter(b => b.id === root);
}

function chapterBoxesOf(container) {
  const out = [];
  (container.children || []).forEach(id => {
    const b = boxById[id];
    if (!b) return;
    if (b.kind === 'chapter') out.push(b);
    else chapterBoxesOf(b).forEach(ch => out.push(ch));
  });
  return out;
}

function allChapterBoxes() {
  const out = [];
  topLevelBoxes().forEach(t => chapterBoxesOf(t).forEach(ch => out.push(ch)));
  return out;
}

function chaptersFor(skillId, scopeBoxId) {
  const chapters = (skillToBoxes[skillId] || []).map(id => boxById[id]).filter(b => b && b.kind === 'chapter');
  if (!scopeBoxId) return chapters;
  const root = scopeRootId(scopeBoxId);
  const inRoot = chapters.filter(b => scopeRootId(b.id) === root);
  if (parentOfBox[scopeBoxId]) {
    const exact = inRoot.filter(b => b.id === scopeBoxId);
    if (exact.length) return exact;
  }
  return inRoot;
}

function chapterLabel(skillId) {
  const chs = chaptersFor(skillId, filter.box);
  if (!chs.length) {
    const s = byId[skillId];
    if (s && s.chapter && DATA.chapters && DATA.chapters[s.chapter]) return 'Chapter ' + s.chapter + ': ' + DATA.chapters[s.chapter];
    return 'Skill';
  }
  if (chs.length === 1) return chs[0].title;
  return chs.map(b => b.title).join(' · ');
}

function chapterPillText(box) {
  const m = /^Chapter\s+(\d+)/.exec(box.title || '');
  if (m) return 'Ch ' + m[1];
  const tail = (box.id || '').split('/').pop();
  return tail ? tail.toUpperCase() : '§';
}

function layoutSkillIds() {
  const root = layoutRoot();
  if (!root) return skills.map(s => s.id);
  const ids = new Set(getBoxDescendantSkills(root));
  return skills.map(s => s.id).filter(id => ids.has(id));
}

function tileInScope(tile) {
  if (!filter.box) return true;
  const boxId = tile.dataset.box;
  if (boxId) return boxId === filter.box || isDescendantBox(boxId, filter.box);
  return skillInBox(tile.dataset.id, filter.box);
}

function computeTreeLayout() {
  const ids = layoutSkillIds();
  const idset = new Set(ids);
  const edges = allEdges.filter(([p, c]) => idset.has(p) && idset.has(c));
  const r = ids.length ? layeredLayout(ids, edges) : { pos: {}, mids: {}, w: 200, h: 120, nl: 0, crossings: 0, layerOf: {} };
  const nodes = {}, mids = {};
  for (const id in r.pos) nodes[id] = { x: r.pos[id].x + WPAD, y: (r.h - r.pos[id].y - TH) + WPAD };
  for (const k in r.mids) mids[k] = r.mids[k].map(pt => [pt[0] + WPAD, (r.h - pt[1]) + WPAD]);
  layout.tree = {
    nodes, mids, blobs: {}, w: Math.max((r.w || 0) + WPAD * 2, 200), h: Math.max((r.h || 0) + WPAD * 2, 120),
    layers: r.nl, crossings: r.crossings, layerOf: r.layerOf || {},
    edges: edges.map(([p, c]) => ({ from: p, to: c, fromKey: p, toKey: c }))
  };
}

function layoutOneContainer(container) {
  const COLLAPSED_H = 64, COURSE_PAD = 20, INNER_GAP = 14;
  const chapters = chapterBoxesOf(container);
  const places = [];
  chapters.forEach(ch => (ch.skills || []).forEach(id => { if (byId[id]) places.push({ skillId: id, boxId: ch.id }); }));
  const kind = container.kind === 'textbook' ? 'textbook' : 'course';
  if (collapsedBoxes.has(container.id)) {
    return {
      nodes: {}, mids: {}, places, edges: [],
      blobs: { [container.id]: { x: 0, y: 0, w: BMIN, h: COLLAPSED_H, kind, boxId: container.id, children: [] } },
      w: BMIN, h: COLLAPSED_H
    };
  }
  const subs = {}, bs = {}, chapterIds = [];
  for (const chBox of chapters) {
    const chId = chBox.id;
    chapterIds.push(chId);
    const ids = (chBox.skills || []).filter(id => byId[id]);
    const set = new Set(ids);
    const collapsed = boxOrAncestorCollapsed(chId);
    const sub = ids.length ? layeredLayout(ids, allEdges.filter(([p, c]) => set.has(p) && set.has(c))) : { pos: {}, mids: {}, w: 0, h: 0 };
    subs[chId] = collapsed ? { pos: {}, mids: {}, w: sub.w || 0, h: 0 } : sub;
    bs[chId] = { w: Math.max((sub.w || 0) + PAD * 2, BMIN), h: (collapsed || !ids.length) ? COLLAPSED_H : (HDR + sub.h + PAD + 4) };
  }
  const chOf = {};
  chapters.forEach(ch => (ch.skills || []).forEach(id => { if (byId[id]) chOf[id] = ch.id; }));
  const cpred = {};
  chapterIds.forEach(c => cpred[c] = new Map());
  allEdges.forEach(([p, c]) => {
    const ka = chOf[p], kb = chOf[c];
    if (ka && kb && ka !== kb && cpred[kb] && cpred[ka]) cpred[kb].set(ka, (cpred[kb].get(ka) || 0) + 1);
  });
  const rank = {}, visiting = new Set();
  const R = c => {
    if (rank[c] != null) return rank[c];
    if (visiting.has(c)) return 0;
    visiting.add(c);
    let rnk = 0;
    if (cpred[c]) for (const p of cpred[c].keys()) rnk = Math.max(rnk, 1 + R(p));
    visiting.delete(c);
    rank[c] = rnk;
    return rnk;
  };
  chapterIds.forEach(R);
  const avgD = {};
  chapterIds.forEach(key => {
    const ids = (boxById[key].skills || []).filter(id => byId[id]);
    const layers = (layout.tree && layout.tree.layerOf) || {};
    avgD[key] = ids.length ? ids.reduce((a, id) => a + (layers[id] || 0), 0) / ids.length : 0;
  });
  const maxRank = chapterIds.length ? Math.max(0, ...chapterIds.map(c => rank[c] || 0)) : 0;
  const bx = {}, by = {}; let y = 0;
  const center = c => bx[c] + bs[c].w / 2;
  const mean = a => a.length ? a.reduce((x, yy) => x + yy, 0) / a.length : 0;
  for (let r = 0; r <= maxRank; r++) {
    const row = chapterIds.filter(c => rank[c] === r);
    const want = c => {
      const ps = cpred[c] ? [...cpred[c].entries()].filter(([p]) => bx[p] != null) : [];
      return ps.length ? ps.reduce((a, [p, n]) => a + center(p) * n, 0) / ps.reduce((a, [, n]) => a + n, 0) : null;
    };
    row.sort((a, b) => {
      const wa = want(a), wb = want(b);
      return (wa == null ? 0 : wa) - (wb == null ? 0 : wb) || avgD[a] - avgD[b] || String(a).localeCompare(String(b));
    });
    const subrows = [[]]; let w = 0;
    row.forEach(c => {
      if (w && w + bs[c].w + BGAP > ROWMAX) { subrows.push([]); w = 0 }
      subrows[subrows.length - 1].push(c); w += bs[c].w + BGAP;
    });
    subrows.forEach(sr => {
      const wants = sr.map(c => want(c));
      const known = wants.filter(v => v != null);
      const base = known.length ? mean(known) : 0;
      const tgt = wants.map(v => v == null ? base : v);
      const seps = sr.slice(1).map((c, i) => (bs[sr[i]].w + bs[c].w) / 2 + BGAP);
      const xs = pav(tgt, seps, sr.map(() => 1));
      let rh = 0;
      sr.forEach((c, i) => { bx[c] = xs[i] - bs[c].w / 2; by[c] = y; rh = Math.max(rh, bs[c].h) });
      y += rh + RGAP;
    });
  }
  const allKeys = chapterIds.filter(c => bx[c] != null);
  const minX = allKeys.length ? Math.min(...allKeys.map(c => bx[c])) : 0;
  const maxX = allKeys.length ? Math.max(...allKeys.map(c => bx[c] + bs[c].w)) : BMIN;
  const nodes = {}, mids = {}, blobs = {};
  for (const key of allKeys) {
    const ox = bx[key] - minX + WPAD, oy = by[key] + WPAD;
    const ch = boxById[key].color_index || 1;
    blobs[key] = { x: ox, y: oy, w: bs[key].w, h: bs[key].h, ch, kind: 'chapter', boxId: key };
    if (subs[key] && subs[key].pos && !collapsedBoxes.has(key)) {
      const ix = ox + (bs[key].w - subs[key].w) / 2, iy = oy + PAD + 4;
      for (const id in subs[key].pos) nodes[id] = { x: ix + subs[key].pos[id].x, y: iy + subs[key].pos[id].y };
      for (const k in subs[key].mids) mids[k] = subs[key].mids[k].map(pt => [ix + pt[0], iy + pt[1]]);
    }
  }
  if (allKeys.length) {
    const cx0 = Math.min(...allKeys.map(id => blobs[id].x)) - COURSE_PAD;
    const cy0 = Math.min(...allKeys.map(id => blobs[id].y)) - HDR - INNER_GAP;
    const cx1 = Math.max(...allKeys.map(id => blobs[id].x + blobs[id].w)) + COURSE_PAD;
    const cy1 = Math.max(...allKeys.map(id => blobs[id].y + blobs[id].h)) + COURSE_PAD;
    blobs[container.id] = { x: cx0, y: cy0, w: cx1 - cx0, h: cy1 - cy0, kind, boxId: container.id, children: allKeys.slice() };
  }
  const M = 26, edges = [];
  allEdges.forEach(([p, c]) => {
    const kp = chOf[p], kc = chOf[c];
    if (!kp || !kc) return;
    edges.push({ from: p, to: c, fromBox: kp, toBox: kc });
    if (kp === kc || !nodes[p] || !nodes[c]) return;
    const A = blobs[kp], B = blobs[kc], P = nodes[p], Q = nodes[c];
    if (!A || !B) return;
    const sx = P.x + TW / 2, sy = P.y + TH, tx = Q.x + TW / 2, ty = Q.y;
    if (ty <= sy) return;
    const obs = allKeys.filter(x => x !== kp && x !== kc).map(x => blobs[x]).filter(o => o.y < ty && o.y + o.h > sy).sort((u, v) => u.y - v.y);
    if (!obs.length) return;
    const bands = [];
    obs.forEach(o => {
      const last = bands[bands.length - 1];
      if (last && o.y < last.y1 + RGAP * .6) { last.y1 = Math.max(last.y1, o.y + o.h); last.iv.push([o.x - M, o.x + o.w + M]); }
      else bands.push({ y0: o.y, y1: o.y + o.h, iv: [[o.x - M, o.x + o.w + M]] });
    });
    const pts = [];
    bands.forEach(bd => {
      const iv = bd.iv.sort((u, v) => u[0] - v[0]).reduce((acc, rng) => { const l = acc[acc.length - 1]; if (l && rng[0] <= l[1]) l[1] = Math.max(l[1], rng[1]); else acc.push([rng[0], rng[1]]); return acc; }, []);
      const ym = (bd.y0 + bd.y1) / 2, f = Math.max(0, Math.min(1, (ym - sy) / (ty - sy)));
      let x = sx + (tx - sx) * f;
      const hit = iv.find(rng => x > rng[0] && x < rng[1]);
      if (hit) { const l = hit[0], rr = hit[1]; x = (l < 14 || Math.abs(x - l) > Math.abs(rr - x)) ? rr : l; }
      pts.push([x, Math.max(sy + 8, bd.y0 - RGAP * .35)], [x, Math.min(ty - 8, bd.y1 + RGAP * .35)]);
    });
    mids[p + '>' + c] = pts;
  });
  const allX = [];
  for (const k in mids) mids[k].forEach(q => allX.push(q[0]));
  const blobXs = Object.values(blobs).map(b => b.x);
  const shiftX = Math.max(0, 20 - Math.min(Infinity, ...allX.concat(blobXs.length ? blobXs : [0])));
  if (shiftX) {
    for (const id in nodes) nodes[id].x += shiftX;
    for (const k in mids) mids[k].forEach(q => q[0] += shiftX);
    for (const c in blobs) blobs[c].x += shiftX;
  }
  const worldW = Math.max(maxX - minX + WPAD * 2, ...allX.map(v => v + WPAD), ...Object.values(blobs).map(b => b.x + b.w + WPAD), BMIN);
  const worldH = Math.max(1, (y > RGAP ? y - RGAP : y) + WPAD * 2);
  for (const id in nodes) nodes[id].y = worldH - nodes[id].y - TH;
  for (const k in mids) mids[k].forEach(q => q[1] = worldH - q[1]);
  for (const c in blobs) blobs[c].y = worldH - blobs[c].y - blobs[c].h;
  let minY = 0;
  Object.values(blobs).forEach(b => { if (b.y < minY) minY = b.y; });
  Object.values(nodes).forEach(n => { if (n.y < minY) minY = n.y; });
  if (minY < 0) {
    const shift = -minY + 8;
    for (const id in nodes) nodes[id].y += shift;
    for (const k in mids) mids[k].forEach(q => q[1] += shift);
    for (const c in blobs) blobs[c].y += shift;
  }
  const h = Math.max(worldH, ...Object.values(blobs).map(b => b.y + b.h + 8), ...Object.values(nodes).map(n => n.y + TH + 8), COLLAPSED_H);
  const w = Math.max(worldW, ...Object.values(blobs).map(b => b.x + b.w + 8), BMIN);
  return { nodes, mids, blobs, places, edges, w, h };
}

function computeGroupedLayout() {
  const containers = visibleContainers();
  const nodes = {}, mids = {}, blobs = {}, places = [], edges = [];
  let yOff = 0, maxW = 0;
  const GAP = 72;
  containers.forEach(container => {
    const local = layoutOneContainer(container);
    for (const k in local.blobs) {
      const b = local.blobs[k];
      blobs[k] = Object.assign({}, b, { x: b.x, y: b.y + yOff });
    }
    local.places.forEach(p => {
      const key = p.boxId + '|' + p.skillId;
      const pos = local.nodes[p.skillId];
      if (pos) nodes[key] = { x: pos.x, y: pos.y + yOff };
      if (pos && nodes[p.skillId] == null) nodes[p.skillId] = nodes[key];
      places.push({ key, skillId: p.skillId, boxId: p.boxId });
    });
    local.edges.forEach(e => {
      const fk = e.fromBox + '|' + e.from, tk = e.toBox + '|' + e.to;
      edges.push({ from: e.from, to: e.to, fromKey: fk, toKey: tk });
      const mk = e.from + '>' + e.to;
      if (local.mids[mk]) mids[fk + '>' + tk] = local.mids[mk].map(pt => [pt[0], pt[1] + yOff]);
    });
    yOff += local.h + GAP;
    maxW = Math.max(maxW, local.w);
  });
  layout.grouped = {
    nodes, mids, blobs, places, edges,
    w: Math.max(maxW, 200), h: Math.max(yOff, 120), useNested: containers.length > 0, rank: {}
  };
}

function computeLayouts() { computeTreeLayout(); computeGroupedLayout() }

/* ====================== tree rendering ====================== */
let world, tv, edgesSvg, panel;
const panelOpen = () => panel && panel.classList.contains('open');
let view = { x: 20, y: 20, s: 1 }, selected = null, hoverId = null, quizOpen = false;
let layoutMode = 'tree', curPos = {}, morphRaf = 0;
const filter = { playable: false, view: 'tree', box: null };
const collapsedBoxes = new Set();
const edgeEls = [];
const drag = { on: false, moved: false, sx: 0, sy: 0, vx: 0, vy: 0 };
const curL = () => layout[layoutMode];
const reducedMotion = () => window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;

function getBoxSkills(boxId) {
  const box = boxById[boxId];
  if (!box) return [];
  return (box.skills || []).filter(id => byId[id]);
}

function getBoxDescendantSkills(boxId) {
  const box = boxById[boxId];
  if (!box) return [];
  const direct = (box.skills || []).filter(id => byId[id]);
  const childSkills = (box.children || []).flatMap(cid => getBoxDescendantSkills(cid));
  return [...new Set([...direct, ...childSkills])];
}

function skillInBox(skillId, boxId) {
  const boxes = skillToBoxes[skillId] || [];
  if (boxes.includes(boxId)) return true;
  const box = boxById[boxId];
  if (box && box.children) {
    return box.children.some(cid => skillInBox(skillId, cid));
  }
  return false;
}

function labelForTile(s, tile) {
  const boxId = tile && tile.dataset.box;
  if (boxId && boxById[boxId]) return boxById[boxId].title;
  return chapterLabel(s.id);
}

function tileTitle(s, tile) { return `${s.name} · ${labelForTile(s, tile)}` }

function buildTile(s, st, boxId) {
  const shimmerDelay = (Math.random() * 4 + 1).toFixed(2) + 's';
  const ci = (boxId && boxById[boxId] && boxById[boxId].color_index != null) ? boxById[boxId].color_index : getSkillColorIndex(s.id);
  const b = el('button', { class: 'tile' + (st ? ' st' : ''), 'data-id': s.id, style: colorVars(ci) + `;--shimmer-delay:${shimmerDelay}`, type: 'button', title: s.name },
    el('span', { class: 'fill' }), el('span', { class: 'nm name', text: s.name }),
    el('span', { class: 'meta sub' }, el('span', { class: 'pips' }, [0, 1, 2, 3].map(() => el('i'))), el('span', { class: 'tl' }), el('span', { class: 'tag' })),
    el('span', { class: 'star', 'aria-hidden': 'true', text: '★' }),
    el('span', { class: 'extstar', 'aria-hidden': 'true', text: '☆' }),
    el('span', { class: 'light', 'aria-hidden': 'true' }, el('span', { class: 'light-dot' })));
  if (boxId) b.dataset.box = boxId;
  b.addEventListener('click', () => { if (drag.moved) return; selectSkill(s.id) });
  b.addEventListener('mouseenter', () => { hoverId = s.id; applyEdgeHighlight() });
  b.addEventListener('mouseleave', () => { hoverId = null; applyEdgeHighlight() });
  b.addEventListener('focus', () => { hoverId = s.id; applyEdgeHighlight() });
  b.addEventListener('blur', () => { hoverId = null; applyEdgeHighlight() });
  return b;
}

function isOutsidePrereq(id) {
  if (!filter.box || skillInBox(id, filter.box)) return false;
  const inside = getBoxDescendantSkills(filter.box);
  return inside.some(sid => byId[sid] && byId[sid].prereqs.includes(id));
}

function refreshTile(b) {
  const id = b.dataset.id, s = byId[id], t = tierOf(id), soon = !isPlayable(id), ready = isReady(id);
  const st = b.classList.contains('st');
  const boxDimmed = !tileInScope(b);
  const outside = isOutsidePrereq(id);
  const lightMode = b.classList.contains('light-mode');
  const hidden = !st && skillHiddenByCollapse(id, b.dataset.box || null);
  b.className = 'tile' + (st ? ' st' : '') + ' t' + t + (soon ? ' soon' : '') + (ready ? ' ready' : '') + (selected === id ? ' sel' : '') + (boxDimmed ? ' boxdim' : '') + (outside ? ' ext-prereq' : '') + (lightMode ? ' light-mode' : '') + (hidden ? ' collapsed-hide' : '');
  b.style.setProperty('--fill', FILL[t] + '%');
  b.querySelectorAll('.pips i').forEach((p, i) => p.classList.toggle('on', t > i));
  b.querySelector('.tl').textContent = soon ? '' : TIERS[t];
  const tag = b.querySelector('.tag'); tag.textContent = soon ? 'SOON' : (ready ? 'READY' : ''); tag.style.display = (soon || ready) ? '' : 'none';
  const gaps = (!soon && t === 0 && !ready) ? prereqGaps(id).length : 0;
  const label = labelForTile(s, b);
  b.title = `${s.name} · ${label}` + (soon ? ' · coming soon' : ready ? ' · ready to learn' : gaps ? ` · recommended once prerequisites reach ${TIERS[READY_TIER]}` : '') + (outside ? ' · prerequisite outside this scope' : '');
  b.setAttribute('aria-label', `${s.name}. ${label}. ${soon ? 'Coming soon, no questions yet' : TIERS[t] + (ready ? ', ready to learn' : '')}${outside ? '. Prerequisite outside this scope' : ''}`);
  b.setAttribute('aria-pressed', selected === id ? 'true' : 'false');
  if (filter.playable && soon && !st) b.classList.add('dim');
}

function directD(A, B) {
  const ax = A.x + TW / 2, ay = A.y, bx = B.x + TW / 2, by = B.y + TH;
  if (by <= ay - 8) { const d = Math.max(30, (ay - by) * .5); return { d: `M${ax},${ay} C${ax},${ay - d} ${bx},${by + d} ${bx},${by}`, ex: bx, ey: by } }
  const right = B.x > A.x, sx = right ? A.x + TW : A.x, ex = right ? B.x : B.x + TW, sy = A.y + TH / 2, ey = B.y + TH / 2, d = Math.max(40, Math.abs(ex - sx) * .45);
  const dir = right ? 1 : -1;
  return { d: `M${sx},${sy} C${sx + dir * d},${sy} ${ex - dir * d},${ey} ${ex},${ey}`, ex, ey };
}

function routedD(e, L) {
  const fromKey = e.fromKey || e.from, toKey = e.toKey || e.to;
  const A = L.nodes[fromKey], B = L.nodes[toKey];
  if (!A || !B) return { d: '', ex: 0, ey: 0 };
  const mids = L.mids[fromKey + '>' + toKey];
  if (!mids) return directD(A, B);
  const pts = [[A.x + TW / 2, A.y], ...mids, [B.x + TW / 2, B.y + TH]];
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 1; i < pts.length; i++) { const a = pts[i - 1], b = pts[i], k = (b[1] - a[1]) * .5; d += ` C${a[0]},${a[1] + k} ${b[0]},${b[1] - k} ${b[0]},${b[1]}` }
  return { d, ex: B.x + TW / 2, ey: B.y + TH };
}

function setEdge(e, r) { e.path.setAttribute('d', r.d); e.dot.setAttribute('cx', r.ex); e.dot.setAttribute('cy', r.ey) }
function sizeWorld(L) { world.style.width = L.w + 'px'; world.style.height = L.h + 'px'; edgesSvg.setAttribute('width', L.w); edgesSvg.setAttribute('height', L.h) }
function placeTiles(pos) {
  world.querySelectorAll('.tile').forEach(t => {
    const key = t.dataset.place || t.dataset.id;
    const p = pos[key];
    if (!p) return;
    t.style.left = p.x + 'px';
    t.style.top = p.y + 'px';
  });
}

function boxOrAncestorCollapsed(boxId) {
  let cur = boxId;
  while (cur) {
    if (collapsedBoxes.has(cur)) return true;
    cur = parentOfBox[cur];
  }
  return false;
}

function skillHiddenByCollapse(id, boxId) {
  if (layoutMode !== 'grouped' || filter.view !== 'tree') return false;
  if (boxId) return boxOrAncestorCollapsed(boxId);
  return false;
}

function edgeHidden(e) {
  if (layoutMode !== 'grouped' || filter.view !== 'tree') return false;
  const fromBox = e.fromKey && e.fromKey.includes('|') ? e.fromKey.split('|')[0] : null;
  const toBox = e.toKey && e.toKey.includes('|') ? e.toKey.split('|')[0] : null;
  if (fromBox && boxOrAncestorCollapsed(fromBox)) return true;
  if (toBox && boxOrAncestorCollapsed(toBox)) return true;
  return false;
}

function syncTiles() {
  const want = new Map();
  if (layoutMode === 'grouped' && layout.grouped && layout.grouped.places) {
    layout.grouped.places.forEach(p => want.set(p.key, p));
  } else {
    layoutSkillIds().forEach(id => want.set(id, { key: id, skillId: id, boxId: null }));
  }
  world.querySelectorAll('.tile:not(.st)').forEach(t => {
    const key = t.dataset.place || t.dataset.id;
    if (!want.has(key)) t.remove();
  });
  want.forEach(p => {
    const existing = p.boxId
      ? world.querySelector('.tile[data-place="' + p.key.replace(/"/g, '') + '"]')
      : world.querySelector('.tile[data-id="' + p.skillId + '"]:not([data-place])');
    if (existing) return;
    const tile = buildTile(byId[p.skillId], false, p.boxId);
    if (p.boxId) tile.dataset.place = p.key;
    world.append(tile);
  });
  world.querySelectorAll('.tile:not(.st)').forEach(refreshTile);
}

function syncEdges() {
  edgeEls.splice(0).forEach(e => { e.path.remove(); e.dot.remove(); });
  const NS = 'http://www.w3.org/2000/svg';
  const list = layoutMode === 'grouped' ? ((layout.grouped && layout.grouped.edges) || []) : ((layout.tree && layout.tree.edges) || []);
  list.forEach(e => {
    const path = document.createElementNS(NS, 'path');
    const dot = document.createElementNS(NS, 'circle');
    dot.setAttribute('r', '3.2');
    edgesSvg.append(path, dot);
    edgeEls.push({ from: e.from, to: e.to, fromKey: e.fromKey, toKey: e.toKey, path, dot });
  });
}

function syncCollapsedTiles() {
  document.querySelectorAll('#world .tile').forEach(t => {
    t.classList.toggle('collapsed-hide', skillHiddenByCollapse(t.dataset.id, t.dataset.box || null));
  });
}

function boxForChapter(ch) {
  if (!COLLECTIONS || !COLLECTIONS.boxes) return null;
  return COLLECTIONS.boxes.find(b => b.kind === 'chapter' && (b.color_index === ch || b.id === 'ee105-ch' + ch)) || null;
}

function loadCollapsed() {
  collapsedBoxes.clear();
  try {
    const raw = JSON.parse(localStorage.getItem(COLLAPSE_KEY) || '[]');
    if (!Array.isArray(raw)) return;
    raw.forEach(id => { if (typeof id === 'string' && boxById[id]) collapsedBoxes.add(id); });
  } catch (e) { }
}

function saveCollapsed() {
  try { localStorage.setItem(COLLAPSE_KEY, JSON.stringify([...collapsedBoxes])); } catch (e) { }
}

function toggleBoxCollapse(boxId) {
  if (!boxById[boxId]) return;
  if (collapsedBoxes.has(boxId)) collapsedBoxes.delete(boxId);
  else collapsedBoxes.add(boxId);
  saveCollapsed();
  rebuildGroupedLayout();
  const btn = document.querySelector('.blob[data-box="' + (window.CSS && CSS.escape ? CSS.escape(boxId) : boxId) + '"] .toggle');
  if (btn) btn.focus();
}

function collapseButton(boxId, title) {
  const isCollapsed = collapsedBoxes.has(boxId);
  return el('button', {
    class: 'toggle',
    type: 'button',
    'aria-expanded': String(!isCollapsed),
    'aria-label': (isCollapsed ? 'Expand ' : 'Collapse ') + title,
    onclick: e => { e.stopPropagation(); e.preventDefault(); toggleBoxCollapse(boxId); },
    onpointerdown: e => e.stopPropagation(),
    onmousedown: e => e.stopPropagation()
  }, el('span', { class: 'chev', 'aria-hidden': 'true', text: '▼' }));
}

function rebuildGroupedLayout() {
  computeGroupedLayout();
  updateBlobsDOM();
  if (layoutMode === 'grouped') {
    showLayout('grouped', false);
    refreshAll();
  }
}

function updateBlobsDOM() {
  document.querySelectorAll('#world .blob').forEach(b => b.remove());
  const G = layout.grouped;
  if (!G) return;
  const containers = [];
  for (const key in G.blobs) {
    const b = G.blobs[key];
    if (b.kind === 'course' || b.kind === 'textbook') { containers.push(key); continue; }
    const box = b.boxId && boxById[b.boxId];
    const ch = b.ch || 1;
    const title = box ? box.title : ('Ch ' + ch);
    const isCollapsed = b.boxId && collapsedBoxes.has(b.boxId);
    const blob = el('div', {
      class: 'blob chapter' + (isCollapsed ? ' collapsed' : ''),
      'data-ch': ch,
      'data-box': b.boxId || '',
      style: `left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px;${colorVars(ch)}`
    });
    const hd = el('div', { class: 'hd' });
    if (b.boxId) hd.append(collapseButton(b.boxId, title));
    hd.append(
      el('span', { class: 'cpill', text: box ? chapterPillText(box) : ('Ch ' + ch) }),
      el('span', { style: 'font-weight:800;font-size:13.5px', text: title.replace(/^Chapter \d+:\s*/, '') }),
      el('span', { class: 'ct', 'data-ct': b.boxId || '' })
    );
    blob.append(hd);
    world.insertBefore(blob, edgesSvg);
  }
  containers.forEach(id => {
    const b = G.blobs[id];
    const box = boxById[id];
    if (!box) return;
    const isCollapsed = collapsedBoxes.has(id);
    const textbook = b.kind === 'textbook';
    const blob = el('div', {
      class: 'blob ' + (textbook ? 'textbook' : 'course') + (isCollapsed ? ' collapsed' : ''),
      'data-box': id,
      style: `left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px;border-color:${textbook ? '#7c6cff' : PALETTE[0]};background:${textbook ? 'rgba(124,108,255,.08)' : 'rgba(255,244,214,.15)'}`
    });
    const hd = el('div', { class: 'hd' });
    hd.append(
      collapseButton(id, box.title),
      el('span', { class: 'cpill', style: `background:${textbook ? '#7c6cff' : PALETTE[0]};color:#fff`, text: textbook ? '📘' : '📚' }),
      el('span', { style: 'font-weight:800;font-size:15px', text: box.title })
    );
    blob.append(hd);
    world.insertBefore(blob, edgesSvg);
  });
}

function buildTree() {
  computeLayouts();
  updateBlobsDOM();
}

function legendBuild() {
  const lg = $('chLegend'); lg.innerHTML = '';
  lg.append(el('summary', {}, 'Chapter colors'));
  const box = el('div', { class: 'lgrid' });
  const chapters = visibleContainers().flatMap(chapterBoxesOf);
  (chapters.length ? chapters : allChapterBoxes()).forEach(ch => box.append(el('button', {
    class: 'lg', type: 'button', style: colorVars(ch.color_index || 1), title: ch.title, 'data-box': ch.id,
    onclick: () => setScope(filter.box === ch.id ? null : ch.id, { focus: true })
  }, el('i'), el('span', { text: `${chapterPillText(ch)} · ${ch.title.replace(/^Chapter\s+\d+:\s*/, '')}` }))));
  lg.append(box);
}

const MORPH_MS = 600;
function showLayout(mode, animated) {
  cancelAnimationFrame(morphRaf);
  layoutMode = mode;
  syncTiles();
  syncEdges();
  const L = layout[mode];
  const tiles = [...world.querySelectorAll('.tile')];
  const keys = tiles.map(t => t.dataset.place || t.dataset.id);
  const from = {};
  keys.forEach((key, i) => {
    const id = tiles[i].dataset.id;
    from[key] = curPos[key] || curPos[id] || L.nodes[key] || L.nodes[id] || { x: 0, y: 0 };
  });
  tv.dataset.mode = mode; world.dataset.layout = mode;
  sizeWorld(L);
  
  document.querySelectorAll('#world .blob').forEach(b => {
    const isGrouped = mode === 'grouped';
    b.classList.toggle('on', isGrouped);
    
    if (isGrouped) {
      const boxId = b.dataset.box;
      const key = boxId || +b.dataset.ch;
      const blobData = L.blobs[key];
      if (blobData) {
        b.style.left = blobData.x + 'px';
        b.style.top = blobData.y + 'px';
        b.style.width = blobData.w + 'px';
        b.style.height = blobData.h + 'px';
      }
    }
  });
  
  const btn = $('btnGroup'); btn.setAttribute('aria-pressed', String(mode === 'grouped'));
  btn.querySelector('.t').textContent = mode === 'grouped' ? 'Ungroup' : 'Group by course';
  btn.title = mode === 'grouped' ? 'Back to one homogeneous prerequisite tree' : 'Sort the tree into course and chapter blocks';
  
  const drawEdges = (useRouted) => {
    edgeEls.forEach(e => {
      const hide = edgeHidden(e);
      e.path.classList.toggle('collapsed-hide', hide);
      e.dot.classList.toggle('collapsed-hide', hide);
      if (hide) return;
      const fromKey = e.fromKey || e.from, toKey = e.toKey || e.to;
      const from = useRouted ? L.nodes[fromKey] : (curPos[fromKey] || L.nodes[fromKey]);
      const to = useRouted ? L.nodes[toKey] : (curPos[toKey] || L.nodes[toKey]);
      if (from && to) setEdge(e, useRouted ? routedD(e, L) : directD(from, to));
    });
  };
  const finish = () => {
    keys.forEach(key => {
      const pos = L.nodes[key];
      if (pos) curPos[key] = { x: pos.x, y: pos.y };
    });
    placeTiles(curPos);
    drawEdges(true);
    edgesSvg.classList.remove('morph'); world.classList.remove('morphing'); world.dataset.morphing = '0';
    applyBoxFilter();
  };
  syncCollapsedTiles();
  if (!animated || reducedMotion()) { finish(); return }
  world.classList.add('morphing'); world.dataset.morphing = '1'; edgesSvg.classList.add('morph');
  const t0 = performance.now();
  const step = now => {
    const k = Math.min(1, (now - t0) / MORPH_MS), e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    keys.forEach(key => {
      const tile = world.querySelector(key.includes('|') ? '.tile[data-place="' + key + '"]' : '.tile[data-id="' + key + '"]:not([data-place])');
      const a = from[key], b = L.nodes[key];
      if (a && b && !(tile && skillHiddenByCollapse(tile.dataset.id, tile.dataset.box || null))) curPos[key] = { x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e };
    });
    placeTiles(curPos);
    drawEdges(false);
    if (k < 1) morphRaf = requestAnimationFrame(step); else finish();
  };
  morphRaf = requestAnimationFrame(step);
}

function applyBoxFilter() {
  const boxId = filter.box;
  if (!boxId) {
    document.querySelectorAll('#world .tile').forEach(t => t.classList.remove('boxdim'));
    document.querySelectorAll('#world .blob').forEach(b => b.classList.remove('boxdim'));
    return;
  }
  
  document.querySelectorAll('#world .tile').forEach(t => {
    t.classList.toggle('boxdim', !tileInScope(t));
  });
  
  document.querySelectorAll('#world .blob').forEach(b => {
    const blobBoxId = b.dataset.box;
    if (!blobBoxId) {
      b.classList.remove('boxdim');
      return;
    }
    const related = blobBoxId === boxId || isDescendantBox(blobBoxId, boxId) || isDescendantBox(boxId, blobBoxId);
    b.classList.toggle('boxdim', !related);
  });
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
    const fd = !!(filter.box && !skillInBox(e.from, filter.box) && !skillInBox(e.to, filter.box));
    e.path.classList.toggle('fdim', fd); e.dot.classList.toggle('fdim', fd);
    const hide = edgeHidden(e);
    e.path.classList.toggle('collapsed-hide', hide); e.dot.classList.toggle('collapsed-hide', hide);
  });
}

const LIGHTS_THRESHOLD = 0.38;
let lightsMode = false;

function applyView() {
  world.style.transform = `translate(${view.x}px,${view.y}px) scale(${view.s})`;
  const shouldLights = view.s < LIGHTS_THRESHOLD;
  if (shouldLights !== lightsMode) {
    lightsMode = shouldLights;
    world.classList.toggle('lights-view', lightsMode);
    world.querySelectorAll('.tile').forEach(t => t.classList.toggle('light-mode', lightsMode));
  }
}
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
    const blobKeys = Object.keys(L.blobs);
    const bs = blobKeys.map(k => L.blobs[k]).filter(Boolean);
    if (bs.length === 0) { goFit(); return; }
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

function focusScope() {
  if (filter.view !== 'tree') return;
  if (!filter.box) { layoutMode === 'grouped' ? goHome(true) : goFit(); return }
  const L = curL();
  const blob = L.blobs && L.blobs[filter.box];
  if (layoutMode === 'grouped' && blob) {
    animateView(() => { fitBox(blob.x, blob.y, blob.w, blob.h, 1); applyView() });
    return;
  }
  const ids = getBoxDescendantSkills(filter.box).filter(id => L.nodes[id]);
  if (!ids.length) { goFit(); return }
  const box = bboxOf(ids);
  animateView(() => { fitBox(box.x, box.y, box.w, box.h, 1.1); applyView() });
}

function clearSelection() { try { const s = window.getSelection && window.getSelection(); s && s.removeAllRanges && s.removeAllRanges() } catch (e) { } }

function setupPanZoom() {
  tv.addEventListener('mousedown', e => { if (e.button === 0 && !e.target.closest('.zoomctl,#chLegend,.toggle')) e.preventDefault() });
  tv.addEventListener('selectstart', e => e.preventDefault());
  tv.addEventListener('dragstart', e => e.preventDefault());
  tv.addEventListener('pointerdown', e => { if (e.button !== 0 || e.target.closest('.toggle')) return; drag.on = true; drag.moved = false; drag.sx = e.clientX; drag.sy = e.clientY; drag.vx = view.x; drag.vy = view.y });
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
  for (const ch of allChapterBoxes()) {
    const list = (ch.skills || []).filter(id => byId[id]).map(id => byId[id]);
    g.append(el('section', { class: 'gsec', 'data-box': ch.id, style: colorVars(ch.color_index || 1) },
      el('div', { class: 'hd' }, el('span', { class: 'cpill', text: chapterPillText(ch) }), el('b', { text: ch.title }), el('span', { class: 'ct', 'data-ct': ch.id })),
      el('div', { class: 'ggrid' }, list.map(s => buildTile(s, true, ch.id)))));
  }
}

function applyGridFilter() {
  document.querySelectorAll('#gridView .gsec').forEach(sec => {
    let any = false;
    sec.querySelectorAll('.tile').forEach(t => {
      const hide = (filter.playable && !isPlayable(t.dataset.id)) || !tileInScope(t);
      t.style.display = hide ? 'none' : ''; if (!hide) any = true;
    });
    sec.style.display = any ? '' : 'none';
  });
  document.querySelectorAll('#chLegend .lg').forEach(b => {
    b.classList.toggle('on', !!(filter.box && b.dataset.box === filter.box));
  });
}

/* ====================== stats / banner / refresh ====================== */
function scopeOptionLabel(box, depth) {
  let title = box.title || box.id;
  if (box.kind === 'chapter') title = title.replace(/^Chapter\s+(\d+):\s*/, 'Ch $1: ');
  return (depth > 0 ? '  '.repeat(depth) + '└ ' : '') + title;
}

function fillScopeSelect(select) {
  select.append(el('option', { value: '', text: 'Everything' }));
  if (!COLLECTIONS || !COLLECTIONS.boxes) return;
  const childIds = new Set();
  COLLECTIONS.boxes.forEach(b => (b.children || []).forEach(id => childIds.add(id)));
  const walk = (box, depth) => {
    select.append(el('option', { value: box.id, text: scopeOptionLabel(box, depth) }));
    for (const cid of box.children || []) {
      const child = boxById[cid];
      if (child) walk(child, depth + 1);
    }
  };
  COLLECTIONS.boxes.filter(b => !childIds.has(b.id)).forEach(b => walk(b, 0));
}

function scopeNoteText() {
  const scopeBox = planState.scope ? boxById[planState.scope] : null;
  const scopeSkills = planState.scope ? getBoxDescendantSkills(planState.scope).filter(id => isPlayable(id)) : playable.map(s => s.id);
  const scopeName = scopeBox ? scopeBox.title : 'Everything';
  return planState.scope
    ? `Planning for ${scopeSkills.length} playable skill${scopeSkills.length === 1 ? '' : 's'} in "${scopeName}". Prerequisites outside this scope will be included to Level 2.`
    : `Planning for Everything: ${playable.length} playable skills. Coming-soon skills (${skills.length - playable.length}) are excluded.`;
}

function refreshOpenPlan() {
  const results = $('planResults');
  if (!results) return;
  planState.open = null;
  const note = $('planScopeNote');
  if (note) note.textContent = scopeNoteText();
  planResults(results);
}

function setScope(boxId, opts) {
  const id = boxId && boxById[boxId] ? boxId : null;
  const prev = layoutRoot();
  filter.box = id;
  planState.scope = id;
  savePlanScope();
  if (prev !== layoutRoot()) {
    computeLayouts();
    updateBlobsDOM();
    legendBuild();
    showLayout(layoutMode, false);
  }
  refreshAll();
  refreshOpenPlan();
  if (opts && opts.focus && filter.view === 'tree') focusScope();
}

function refreshAll() {
  document.querySelectorAll('.tile[data-id]').forEach(refreshTile);
  renderStats(); renderBanner(); renderPlanBadge();
  $('qCount').textContent = queue().length;
  document.querySelectorAll('[data-ct]').forEach(e => {
    const box = boxById[e.dataset.ct];
    if (!box) return;
    const l = (box.skills || []).filter(id => byId[id]);
    const p = l.filter(id => isPlayable(id)).length;
    const c = l.filter(id => tierOf(id) > 0).length;
    e.textContent = `${c}/${l.length} colored in` + (p ? ` · ${p} playable` : '');
  });
  applyBoxFilter(); applyGridFilter(); applyEdgeHighlight();
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
  
  const scopePicker = el('select', { id: 'scopePicker', 'aria-label': 'Scope: Everything, a course, or a chapter' });
  fillScopeSelect(scopePicker);
  scopePicker.value = filter.box || '';
  scopePicker.onchange = () => setScope(scopePicker.value || null, { focus: true });
  const chk = el('input', { type: 'checkbox', id: 'onlyPlay' }); chk.checked = filter.playable; chk.onchange = () => { filter.playable = chk.checked; refreshAll() };
  hc.append(el('div', { class: 'seg', role: 'group', 'aria-label': 'View' },
    el('button', { id: 'vTree', 'aria-pressed': String(filter.view === 'tree'), onclick: () => setView('tree') }, 'Tree'),
    el('button', { id: 'vGrid', 'aria-pressed': String(filter.view === 'grid'), onclick: () => setView('grid') }, 'Grid')),
    el('label', { class: 'scope-label', for: 'scopePicker', text: 'Scope' }),
    scopePicker, el('label', { class: 'chk' }, chk, 'Playable only'));
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
  if (ready.length) b.append(el('span', { class: 'rd' }, el('b', { text: 'Ready to learn:' }), ready.slice(0, 2).map(s => el('button', { class: 'pill', style: colorOf(s.id), onclick: () => selectSkill(s.id, true), title: s.name }, short(s.name, 24))), ready.length > 2 ? el('span', { text: `+${ready.length - 2} more` }) : null));
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
  const outside = !!(filter.box && !skillInBox(id, filter.box));
  return el('button', { class: 'pill' + (outside ? ' ext' : ''), style: colorOf(id), onclick: () => selectSkill(id, true), title: TIERS[t] + (isPlayable(id) ? '' : ' · coming soon') + (outside ? ' · prerequisite outside this scope' : '') },
    el('span', { class: 'sw t' + t, style: `--f:${FILL[t]}%;width:14px;height:14px;border-color:${chColor(getSkillColorIndex(id))}` }), (outside ? '☆ ' : '') + short(s.name, 40))
}

const need = n => Math.ceil(n * 2 / 3);

function renderPanel() {
  const id = selected; panel.innerHTML = ''; if (!id) return;
  const s = byId[id], t = tierOf(id), soon = !isPlayable(id), ready = isReady(id);
  const nextR = t + 1, kids = [];
  kids.push(el('button', { class: 'close', 'aria-label': 'Close panel', onclick: closePanel }, '×'));
  kids.push(el('div', { style: colorOf(id) }, el('span', { class: 'cpill', id: 'panelChapter', text: chapterLabel(id) })));
  kids.push(el('h2', { text: s.name, id: 'panelTitle' }));
  kids.push(el('div', { class: 'kv', text: (s.reader_section ? `Reader section ${s.reader_section} · ` : '') + `id: ${s.id}` }));
  if (s.summary) kids.push(el('p', { class: 'kv', id: 'skillSummary', text: s.summary }));
  const boxNames = (skillToBoxes[id] || []).map(bid => boxById[bid] && boxById[bid].title).filter(Boolean);
  if (boxNames.length) kids.push(el('div', { class: 'kv', id: 'boxList', text: 'Boxes: ' + boxNames.join(' · ') }));
  if (s.sources && s.sources.length) kids.push(el('div', { class: 'kv', id: 'furtherReading', text: 'Further reading: ' + s.sources.map(src => src.ref + (src.section ? ', ' + src.section : '')).join('; ') }));
  if (soon) kids.push(el('div', { class: 'note soon', role: 'note' }, el('b', { text: 'Coming soon. ' }), "This skill is in the tree, but its questions haven't been written yet, so it can't be practiced in this demo."));
  else {
    kids.push(el('div', { class: 'steps', style: colorOf(s.id), role: 'img', 'aria-label': 'Tier: ' + TIERS[t] },
      TIERS.map((n, i) => el('div', { class: 'step' + (i <= t && i > 0 ? ' done' : '') + (i === t ? ' cur' : '') }, el('div', { class: 'dot', text: i > 0 && i <= t ? '✓' : '' }), n))));
    kids.push(el('div', { class: 'kv', id: 'panelTier' }, el('b', { text: 'Tier: ' }), TIERS[t], ready ? ' · ready to learn' : ''));
    kids.push(el('div', { class: 'kv', id: 'panelLast', title: lastOf(id) ? fmtDate(lastOf(id)) : '' }, el('b', { text: 'Last practiced: ' }), lastOf(id) ? `${ago(lastOf(id))} (${fmtDate(lastOf(id))})` : 'never'));
    if (hasExplainer(id)) {
      kids.push(el('button', { class: 'btn explainer-btn', style: 'width:100%;justify-content:center;margin-top:10px', id: 'explainerBtn', onclick: () => openExplainer(id) }, el('span', { class: 'exp-icon', 'aria-hidden': 'true', text: '📖' }), t === 0 ? 'Read first' : 'Explainer'));
    }
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
  const s = byId[Q.id]; quizEl.style.cssText = colorOf(s.id); quizEl.innerHTML = '';
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
        q.preview.map((p, i) => [i ? ', ' : '', el('button', { class: 'pill', style: colorOf(p), onclick: () => selectSkill(p, false), title: 'Open this skill' }, byId[p].name)])));
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

/* ====================== explainer modal ====================== */
let explainerLoading = false;

function renderMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n- /g, '</p><ul><li>')
    .replace(/\n(\d+)\. /g, '</p><ol><li>')
    .replace(/<\/li>\n- /g, '</li><li>')
    .replace(/<\/li>\n(\d+)\. /g, '</li><li>')
    .replace(/<li>([^<]*?)(?=<\/p>|$)/g, (m, c) => `<li>${c}</li></ul>`)
    .replace(/<li>([^<]*?)(?=<\/p>|$)/g, (m, c) => `<li>${c}</li></ol>`);
}

function renderExplainerSection(sec) {
  const div = el('div', { class: 'exp-section' });
  div.append(el('h3', { text: sec.heading }));
  
  const body = el('div', { class: 'exp-body' });
  setMath(body, sec.body_md);
  div.append(body);
  
  if (sec.figure) {
    const fig = figureNode({ figure: sec.figure, figure_alt: sec.figure_alt, id: 'exp-fig' });
    if (fig) div.append(fig);
  }
  
  return div;
}

async function openExplainer(skillId) {
  if (explainerLoading) return;
  
  const s = byId[skillId];
  if (!s) return;
  
  if (!explainerCache[skillId]) {
    explainerLoading = true;
    const btn = $('explainerBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Loading…'; }
    
    try {
      await fetchExplainer(skillId);
    } catch (e) {
      explainerLoading = false;
      if (btn) { btn.disabled = false; btn.textContent = 'Read first'; }
      openModal({
        title: 'Failed to load explainer',
        body: el('p', { text: `Could not load the explainer: ${e.message || e}` }),
        actions: [{ label: 'OK' }]
      });
      return;
    }
    explainerLoading = false;
    if (btn) { btn.disabled = false; btn.textContent = 'Read first'; }
  }
  
  const exp = explainerCache[skillId];
  if (!exp || !exp.sections) return;
  
  const body = el('div', { class: 'explainer-body', id: 'explainerContent' });
  exp.sections.forEach(sec => body.append(renderExplainerSection(sec)));
  
  openModal({
    title: exp.title || s.name,
    body,
    actions: [{ label: 'Close', kind: 'primary' }],
    wide: true
  });
}

function openQueue() {
  const q = queue();
  const body = el('div', { id: 'queueBody' });
  body.append(el('p', { text: 'These skills are Practiced or higher but not yet Mastered. The one you practiced least recently comes first — spacing your reviews out is what makes learning stick. Missing a challenge never drops your tier.' }));
  if (!q.length) body.append(el('div', { class: 'note info', text: 'Nothing waiting yet. Finish a Round 1 quiz on any skill to start a queue.' }));
  q.forEach((s, i) => {
    const t = tierOf(s.id);
    body.append(el('div', { class: 'qrow' + (i === 0 ? ' top' : ''), 'data-id': s.id, style: colorOf(s.id) },
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
    el('li', {}, el('b', { text: 'Scope ' }), 'limits both the tree and the learning plan to Everything, one course or textbook, or one chapter. A skill can sit in several boxes, and progress is one record per skill. Prerequisites from outside that scope stay in the plan and are marked with a star.'),
    el('li', {}, el('b', { text: 'Group by course ' }), 'regroups the tree into course and chapter blocks. The arrow on a block collapses its contents, and Ungroup flows it back.'),
    el('li', {}, 'Progress autosaves in this browser after every quiz. Use Export for a backup file you can Import later (or on another device).'),
    el('li', {}, 'Skills are organized into courses and chapters. Some skills have questions; the rest say "coming soon".'));
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

const planState = { scratch: false, open: null, scope: null };

function loadPlanScope() {
  try { const s = localStorage.getItem(PLAN_SCOPE_KEY); if (s) planState.scope = s } catch (e) { }
}
function savePlanScope() {
  try { if (planState.scope) localStorage.setItem(PLAN_SCOPE_KEY, planState.scope); else localStorage.removeItem(PLAN_SCOPE_KEY) } catch (e) { }
}

function planGraph(scopeBoxId) {
  let targetIds;
  let extras = new Set();
  
  if (scopeBoxId && boxById[scopeBoxId]) {
    const inBox = new Set(getBoxDescendantSkills(scopeBoxId));
    targetIds = playable.filter(s => inBox.has(s.id)).map(s => s.id);
    
    const needPrereqs = id => {
      const ps = byId[id].prereqs.filter(p => isPlayable(p) && !inBox.has(p));
      ps.forEach(p => { extras.add(p); needPrereqs(p) });
    };
    targetIds.forEach(needPrereqs);
    
    targetIds = targetIds.concat([...extras]);
  } else {
    targetIds = playable.map(s => s.id);
  }
  
  const ids = targetIds, prereqs = {}, maxTier = {};
  ids.forEach(id => {
    prereqs[id] = byId[id].prereqs.filter(p => ids.includes(p));
    let t = 0; while (hasRound(id, t + 1)) t++;
    if (extras.has(id)) {
      maxTier[id] = Math.min(READY_TIER, t);
    } else {
      maxTier[id] = t;
    }
  });
  return { ids, prereqs, maxTier, extras: [...extras] };
}

function planEstimates() {
  const out = {};
  [['practice', 'practice'], ['challenge', 'challenge']].forEach(([k]) => {
    const e = Sim.estimate(timing[k]), ov = timing.override[k];
    out[k] = { measured: e, used: ov != null ? ov : e.minutes, overridden: ov != null };
  });
  return out;
}

function runPlan(scratch, scopeBoxId) {
  const g = planGraph(scopeBoxId), start = {};
  if (!scratch) g.ids.forEach(id => start[id] = tierOf(id));
  const est = planEstimates();
  const result = Sim.simulate(g, start, { practiceMin: est.practice.used, challengeMin: est.challenge.used });
  result.extras = g.extras || [];
  result.scopeBoxId = scopeBoxId;
  return result;
}

function renderPlanBadge() {
  const b = $('planCount'); if (!b) return;
  const r = runPlan(false, planState.scope);
  b.textContent = r.ok ? (r.sessions ? r.sessions : '✓') : '?';
  const scopeBox = planState.scope ? boxById[planState.scope] : null;
  const where = scopeBox ? ` in ${scopeBox.title}` : '';
  $('btnPlan').title = r.ok ? (r.sessions ? `About ${r.sessions} more learning session${r.sessions === 1 ? '' : 's'} (~${Sim.fmtDuration(r.totalMinutes)}) to master the ${r.scope} playable skills${where} — click for the plan` : `All ${r.scope} playable skills${where} are mastered — nothing left to plan`) : 'Learning plan';
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
  const r = runPlan(planState.scratch, planState.scope);
  const extraSet = new Set(r.extras || []);
  const scopeBox = planState.scope ? boxById[planState.scope] : null;
  const scopeName = scopeBox ? scopeBox.title : 'Everything';
  
  if (!r.ok) { box.append(el('div', { class: 'note warn', id: 'planStuck', text: 'The simulation got stuck: some skill can never become ready. This should not happen — please tell Isaac.' })); return }
  const est = planEstimates();
  if (!r.sessions) {
    const inBoxCount = r.scope - r.extras.length;
    box.append(el('div', { class: 'note ok', id: 'planDone' }, el('b', { text: '0 sessions. ' }), 
      scopeBox ? `All ${inBoxCount} playable skills in "${scopeName}" are already Mastered, so there is nothing left to plan.`
        : `All ${r.scope} playable skills are already Mastered, so there is nothing left to plan. The total will grow when more question banks are added.`));
    return;
  }
  
  if (r.extras.length) {
    box.append(el('div', { class: 'note info', id: 'planExtras' }, 
      el('b', { text: 'Prerequisites outside scope: ' }), 
      `${r.extras.length} skill${r.extras.length === 1 ? '' : 's'} from outside "${scopeName}" ${r.extras.length === 1 ? 'is' : 'are'} included as ${r.extras.length === 1 ? 'a ' : ''}prerequisite${r.extras.length === 1 ? '' : 's'} (practiced to Level 2 for readiness): ${r.extras.map(id => byId[id].name).join(', ')}.`));
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
  const fmtSkillName = id => byId[id].name + (extraSet.has(id) ? ' ★' : '');
  r.rows.forEach(row => {
    const open = planState.open === row.n;
    const sums = row.tiers.map((v, t) => v ? el('span', { style: `flex:${v};background:${TIER_COL[t]}`, title: `${v} at ${TIERS[t]}` }) : null);
    body.append(el('tr', { class: 'prow' + (open ? ' open' : ''), 'data-n': row.n, tabindex: '0', role: 'button', 'aria-expanded': String(open), title: 'Click to list the skills', onclick: () => { planState.open = planState.open === row.n ? null : row.n; planResults(box) }, onkeydown: e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.currentTarget.click() } } },
      el('td', { text: row.n }), el('td', { text: row.practiced.length ? String(row.practiced.length) : '–' }), el('td', { text: row.challenges.length ? String(row.challenges.length) : '–' }), el('td', { text: fmtMin(row.minutes) }), el('td', { text: fmtMin(row.cumulative) }),
      el('td', {}, el('div', { class: 'mini' }, sums), el('span', { class: 'mt', text: row.tiers.join(' · ') }))));
    if (open) {
      body.append(el('tr', { class: 'pdet' }, el('td', { colspan: 6 },
        row.practiced.length ? el('div', {}, el('b', { text: 'Practice (Round 1): ' }), row.practiced.map(fmtSkillName).join('; ')) : null,
        row.challenges.length ? el('div', {}, el('b', { text: 'Mastery challenges: ' }), row.challenges.map(c => `${fmtSkillName(c.id)} (${TIERS[c.from]} → ${TIERS[c.to]})`).join('; ')) : null,
        r.extras.length && (row.practiced.some(id => extraSet.has(id)) || row.challenges.some(c => extraSet.has(c.id))) ? el('div', { class: 'kv', style: 'margin-top:4px;font-size:11px' }, '★ = prerequisite outside selected scope') : null)));
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
  body.append(el('div', { class: 'kv', id: 'planScopeNote', style: 'margin:0 0 12px' }));
  
  const seg = el('div', { class: 'seg', role: 'group', 'aria-label': 'Where the simulation starts' },
    el('button', { id: 'planCur', 'aria-pressed': String(!planState.scratch), onclick: () => setScratch(false) }, 'From my progress'),
    el('button', { id: 'planScr', 'aria-pressed': String(planState.scratch), onclick: () => setScratch(true) }, 'Start from scratch'));
  const setScratch = v => { planState.scratch = v; planState.open = null; $('planCur').setAttribute('aria-pressed', String(!v)); $('planScr').setAttribute('aria-pressed', String(v)); $('planStartNote').textContent = v ? 'Pretending every skill in scope is Unpracticed. Your real progress is not touched.' : `Starting from your saved progress.`; planResults(results) };
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
  refreshNotes(); $('planScopeNote').textContent = scopeNoteText(); setScratch(planState.scratch);
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
    const normalized = normalizeProgress(raw);
    if (!normalized) { openModal({ title: 'Import failed', body: el('p', { id: 'impErr', text: "That doesn't look like a Skillgrove progress file (expected version 1 with a \"skills\" object)." }), actions: [{ label: 'OK' }] }); return }
    const p = applyRetirement(normalized).progress;
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
  loadPlanScope();
  if (planState.scope && !boxById[planState.scope]) { planState.scope = null; savePlanScope(); }
  filter.box = planState.scope || null;
  loadCollapsed();
  $('playableNote').textContent = `${playable.length} of ${skills.length} skills ready`;
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
    version: 1, storageOK: () => storageOK, layout: () => layout, mode: () => layoutMode, timing: () => timing,
    plan: (scratch, scope) => runPlan(!!scratch, scope), planState: () => planState,
    ready: () => skills.filter(s => isReady(s.id)).map(s => s.id), playableIds: () => playable.map(s => s.id),
    retired: () => (DATA && DATA.retired) || {},
    qa: { bankMeta: () => bankMeta, bankCache: () => bankCache, fetchBank, prepareQ, renderQuiz, setQuiz: q => { quiz = q }, closeQuizUI, openQuiz: () => quizEl.classList.add('open'), figureNode, katexErrors: () => window.__katexErrors },
    explainers: { meta: () => explainerMeta, cache: () => explainerCache, fetch: fetchExplainer, has: hasExplainer, open: openExplainer },
    lights: { mode: () => lightsMode, threshold: LIGHTS_THRESHOLD, setScale: s => { view.s = s; applyView(); } },
    collections: { 
      data: () => COLLECTIONS, boxById: () => boxById, skillToBoxes: () => skillToBoxes, getSkillBox, getSkillColorIndex,
      collapsed: () => collapsedBoxes, toggleCollapse: toggleBoxCollapse, filter: () => filter.box, setFilter: boxId => setScope(boxId), scope: () => planState.scope,
      getBoxSkills, getBoxDescendantSkills, skillInBox
    },
    queue,
    openModal, toast, reloadProgress: loadProgress, reloadTiming: loadTiming, refreshAll, toggleGroup
  };
  
  if (window.SkillgroveAuth) {
    window.SkillgroveAuth.init();
  }
}

init();
})();
