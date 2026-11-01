/**
 * Tests for Skillgrove multi-file app.
 * 
 * Run with a local server:
 *   cd /workspace && npx serve public -l 5000 &
 *   cd public/skilltree/tests && npm install && node test.js
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const zlib = require('zlib');

const BASE_URL = process.env.SKILLTREE_URL || 'http://localhost:5000/skilltree/';
const SHOTS_DIR = path.join(__dirname, 'shots');

const BANK_DIR = path.join(__dirname, '..', '..', '..', 'skilltree', 'bank');
const BANK = {};
for (const f of fs.readdirSync(BANK_DIR)) {
  if (f.endsWith('.json')) {
    const b = JSON.parse(fs.readFileSync(path.join(BANK_DIR, f)));
    BANK[b.skill_id] = b.questions;
  }
}

const KEY = 'skilltree.progress.v1';
const SKJ = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'skilltree', 'ee105_skills_draft.json'))).skills;
const COLLECTIONS = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'skilltree', 'collections.json')));
const NSKILL = SKJ.length;
const NPLAY = Object.keys(BANK).length;
const NSOON = SKJ.length - NPLAY;
const EDGES = SKJ.reduce((n, s) => n + s.prereqs.length, 0);
const ROOTS = SKJ.filter(s => BANK[s.id] && !s.prereqs.some(q => BANK[q])).map(s => s.id).sort();
const CHAPTERS = COLLECTIONS.boxes.filter(b => b.kind === 'chapter');
const GRID = CHAPTERS.reduce((n, b) => n + (b.skills || []).length, 0);
const NBOX = COLLECTIONS.boxes.length;
const NCHAPTER = CHAPTERS.length;
const NCOURSE = COLLECTIONS.boxes.filter(b => b.kind === 'course').length;
const NTEXTBOOK = COLLECTIONS.boxes.filter(b => b.kind === 'textbook').length;
const NBLOB = NBOX;

let browser, results = [], errs = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function pickBoxes(p, ids) {
  await p.evaluate(ids => {
    const panel = document.getElementById('scopePanel');
    if (panel.hidden) document.getElementById('scopeToggle').click();
    document.getElementById('scopeNone').click();
    const want = new Set(ids);
    document.querySelectorAll('#scopePicker input[type=checkbox]').forEach(inp => {
      if (want.has(inp.value)) inp.click();
    });
  }, ids);
  await sleep(250);
}

async function panTo(p, selector) {
  const box = await p.evaluate(sel => {
    const node = document.querySelector(sel);
    if (!node) throw new Error('missing ' + sel);
    const world = document.getElementById('world');
    const tv = document.getElementById('treeView');
    world.classList.remove('anim');
    world.style.transition = 'none';
    world.style.transform = 'translate(0px,0px) scale(1)';
    void world.offsetWidth;
    const br = node.getBoundingClientRect();
    const vr = tv.getBoundingClientRect();
    const dx = (vr.left + vr.width / 2) - (br.left + br.width / 2);
    const dy = (vr.top + Math.min(180, vr.height / 3)) - (br.top + br.height / 2);
    world.style.transform = `translate(${dx}px, ${dy}px) scale(1)`;
    void world.offsetWidth;
    const at = node.getBoundingClientRect();
    return { w: at.width, h: at.height, x: at.x, y: at.y };
  }, selector);
  assert(box.w >= 20 && box.h >= 20, 'control should be on screen at full size, got ' + box.w + 'x' + box.h);
}

async function newPage(seed, opts = {}) {
  const ctx = await browser.createBrowserContext();
  const p = await ctx.newPage();
  await p.setViewport(opts.viewport || { width: 1280, height: 800 });
  p.on('console', m => { if (['error', 'warning'].includes(m.type())) errs.push(m.type() + ': ' + m.text()) });
  p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  if (opts.noStorage) await p.evaluateOnNewDocument(() => { Storage.prototype.setItem = function() { throw new DOMException('denied', 'SecurityError') } });
  
  p._feedbackPosts = [];
  p._feedbackMode = opts.feedbackMode || 'ok';
  await p.setRequestInterception(true);
  p.on('request', req => {
    if (req.url().includes('/rest/v1/feedback')) {
      const cors = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'apikey, authorization, content-type, prefer, accept',
        'Access-Control-Max-Age': '600'
      };
      if (req.method() === 'OPTIONS') {
        req.respond({ status: 204, headers: cors, body: '' });
        return;
      }
      p._feedbackPosts.push({
        method: req.method(),
        url: req.url(),
        body: req.postData(),
        headers: req.headers()
      });
      if (p._feedbackMode === 'missing') {
        req.respond({
          status: 404,
          contentType: 'application/json',
          headers: cors,
          body: JSON.stringify({ code: 'PGRST205', message: "Could not find the table 'public.feedback' in the schema cache" })
        });
        return;
      }
      if (p._feedbackMode === 'down') {
        req.respond({ status: 500, contentType: 'application/json', headers: cors, body: JSON.stringify({ message: 'db down' }) });
        return;
      }
      req.respond({ status: 201, contentType: 'application/json', headers: cors, body: '' });
      return;
    }
    if (req.url().includes('supabase.min.js')) {
      req.respond({
        status: 200,
        contentType: 'application/javascript',
        body: `window.supabase = { createClient: () => window.__supabaseMock };`
      });
    } else {
      req.continue();
    }
  });
  
  await p.evaluateOnNewDocument((session) => {
    window.__oauthCalls = [];
    window.__supabaseMock = {
      auth: {
        getSession: async () => ({ data: { session } }),
        signInWithOtp: async () => ({ error: null }),
        signInWithOAuth: async (opts) => { window.__oauthCalls.push(opts); return { error: null }; },
        signOut: async () => ({}),
        onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } })
      },
      from: () => ({
        select: () => ({ eq: () => ({ maybeSingle: async () => ({ data: null, error: null }) }) }),
        upsert: async () => ({ error: null })
      })
    };
  }, opts.session || null);
  
  if (seed) {
    await p.goto(BASE_URL);
    await p.waitForSelector('body');
    await p.evaluate((k, s) => localStorage.setItem(k, JSON.stringify(s)), KEY, seed);
  }
  
  await p.goto(BASE_URL, { waitUntil: 'networkidle0', timeout: 30000 });
  await sleep(500);
  p._ctx = ctx;
  return p;
}

function decodePNG(buf) {
  buf = Buffer.from(buf);
  let p = 8, width = 0, height = 0, colorType = 6;
  const idat = [];
  while (p < buf.length) {
    const len = buf.readUInt32BE(p); p += 4;
    const type = buf.toString('ascii', p, p + 4); p += 4;
    const data = buf.subarray(p, p + len); p += len + 4;
    if (type === 'IHDR') { width = data.readUInt32BE(0); height = data.readUInt32BE(4); colorType = data[9]; }
    else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
  }
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const bpp = colorType === 6 ? 4 : 3;
  const out = Buffer.alloc(width * height * 4);
  let s = 0, d = 0;
  let prev = Buffer.alloc(width * bpp);
  const paeth = (a, b, c) => {
    const pa = Math.abs(b - c), pb = Math.abs(a - c), pc = Math.abs(a + b - 2 * c);
    return pa <= pb && pa <= pc ? a : pb <= pc ? b : c;
  };
  for (let y = 0; y < height; y++) {
    const filter = raw[s++];
    const row = Buffer.from(raw.subarray(s, s + width * bpp));
    s += width * bpp;
    for (let i = 0; i < row.length; i++) {
      const left = i >= bpp ? row[i - bpp] : 0;
      const up = prev[i];
      const ul = i >= bpp ? prev[i - bpp] : 0;
      if (filter === 1) row[i] = (row[i] + left) & 255;
      else if (filter === 2) row[i] = (row[i] + up) & 255;
      else if (filter === 3) row[i] = (row[i] + ((left + up) >> 1)) & 255;
      else if (filter === 4) row[i] = (row[i] + paeth(left, up, ul)) & 255;
    }
    prev = row;
    if (bpp === 4) { row.copy(out, d); d += row.length; }
    else for (let i = 0; i < width; i++) { out[d++] = row[i * 3]; out[d++] = row[i * 3 + 1]; out[d++] = row[i * 3 + 2]; out[d++] = 255; }
  }
  return { width, height, data: out };
}

function pixelDiffCount(a, b) {
  const A = decodePNG(a), B = decodePNG(b);
  assert.strictEqual(A.width, B.width);
  assert.strictEqual(A.height, B.height);
  let n = 0;
  for (let i = 0; i < A.data.length; i += 4) {
    if (Math.abs(A.data[i] - B.data[i]) + Math.abs(A.data[i + 1] - B.data[i + 1]) + Math.abs(A.data[i + 2] - B.data[i + 2]) > 12) n++;
  }
  return { n, pixels: A.width * A.height };
}

const store = p => p.evaluate(k => JSON.parse(localStorage.getItem(k)), KEY);
const T = (skills) => ({ version: 1, skills });
const now = Date.now(), DAY = 86400000;

async function openSkill(p, id) {
  await p.evaluate(id => document.querySelector('#world .tile[data-id="' + id + '"]').click(), id);
  await sleep(350);
}

async function answerQuiz(p, skill, pattern) {
  const n = await p.evaluate(() => document.querySelectorAll('.prog i').length);
  for (let i = 0; i < n; i++) {
    const prompt = await p.$eval('#qPrompt', e => e.dataset.qid);
    const q = BANK[skill].find(q => q.id === prompt);
    assert(q, 'question not found in bank: ' + prompt.slice(0, 50));
    const ok = pattern[i];
    if (q.type === 'mc') {
      const idx = await p.evaluate((t, ok) => {
        const bs = [...document.querySelectorAll('.opt')];
        const k = bs.findIndex(b => (+b.dataset.o === t) === ok);
        return k;
      }, q.correct_index, ok);
      assert(idx >= 0);
      const opts = await p.$$('.opt');
      await opts[idx].click();
    } else {
      const val = ok ? String(q.answer) : String(q.answer * 3 + 7);
      await p.type('#numIn', val);
      await p.click('#checkBtn');
    }
    await p.waitForSelector('#feedback', { timeout: 10000 });
    const fbOk = await p.$eval('#feedback', e => e.classList.contains('ok'));
    assert.strictEqual(fbOk, ok, 'feedback mismatch ' + q.id);
    await p.click('#nextBtn');
    await sleep(60);
  }
}

async function test(name, fn) {
  const before = errs.length;
  try {
    await fn();
    results.push(['PASS', name]);
  } catch (e) {
    results.push(['FAIL', name + ' :: ' + (e.message || e).toString().split('\n')[0]]);
    console.error(e.stack);
  }
  const newErrs = errs.slice(before).filter(e => 
    !e.includes('favicon') && 
    !e.includes('404') && 
    !e.includes('blob:fake')
  );
  if (newErrs.length > 0) results.push(['FAIL', name + ' :: console errors ' + newErrs.join(' | ')]);
}

(async () => {
  if (!fs.existsSync(SHOTS_DIR)) fs.mkdirSync(SHOTS_DIR, { recursive: true });
  
  browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  await test(`initial render: ${NSKILL} skills x2 views, ${NSOON} coming soon, ${ROOTS.length} ready`, async () => {
    const p = await newPage();
    const r = await p.evaluate(() => ({
      tree: document.querySelectorAll('#world .tile').length,
      grid: document.querySelectorAll('#gridView .tile').length,
      soon: document.querySelectorAll('#world .tile.soon').length,
      ready: [...document.querySelectorAll('#world .tile.ready')].map(t => t.dataset.id).sort(),
      blobs: document.querySelectorAll('.blob').length,
      courseBlobs: document.querySelectorAll('.blob.course').length,
      textbookBlobs: document.querySelectorAll('.blob.textbook').length,
      chapterBlobs: document.querySelectorAll('.blob.chapter').length,
      paths: document.querySelectorAll('#edges path').length,
      title: document.querySelector('h1').textContent
    }));
    assert.deepStrictEqual([r.tree, r.grid, r.soon, r.blobs, r.paths], [NSKILL, GRID, NSOON, NBLOB, EDGES]);
    assert.strictEqual(r.courseBlobs, NCOURSE, 'should have one blob per course');
    assert.strictEqual(r.textbookBlobs, NTEXTBOOK, 'Feedback Systems is its own textbook blob');
    assert.strictEqual(r.chapterBlobs, NCHAPTER, 'should have one blob per chapter');
    assert.deepStrictEqual(r.ready, ROOTS);
    assert.strictEqual(r.title, 'Skillgrove');
    await p.screenshot({ path: path.join(SHOTS_DIR, '01_tree_home.png') });
    await p._ctx.close();
  });

  await test('coming-soon skills cannot start; skills with banks can', async () => {
    const p = await newPage();
    const soon = await p.$$eval('#world .tile.soon', els => els.map(e => e.dataset.id));
    assert.strictEqual(soon.length, NSOON);
    const legend = await p.$eval('#stats', e => e.textContent);
    assert(legend.includes('Coming soon'), legend);
    if (soon.length) {
      await openSkill(p, soon[0]);
      const txt = await p.$eval('#panel', e => e.textContent);
      assert(/Coming soon/.test(txt));
      assert(!(await p.$('#startBtn')));
      await p.screenshot({ path: path.join(SHOTS_DIR, '02_panel_coming_soon.png') });
    } else {
      await openSkill(p, 'ro');
      assert(await p.$('#startBtn'), 'a skill with a bank can start');
      assert(!/Coming soon/.test(await p.$eval('#panel', e => e.textContent)));
      await p.screenshot({ path: path.join(SHOTS_DIR, '02_panel_playable.png') });
    }
    await p._ctx.close();
  });

  await test('round 1 on bode -> Practiced, persists after reload; tree colored', async () => {
    const p = await newPage();
    await openSkill(p, 'bode');
    await p.screenshot({ path: path.join(SHOTS_DIR, '03_panel_bode.png') });
    await p.click('#startBtn');
    await sleep(1000);
    
    await p.waitForSelector('.prog', { timeout: 10000 });
    assert(/not a mastery challenge/.test(await p.$eval('#rule', e => e.textContent)));
    await answerQuiz(p, 'bode', [true, false, true]);
    assert.strictEqual(await p.$eval('#score', e => e.textContent), '2 / 3');
    assert.strictEqual(await p.$eval('#newTier', e => e.textContent), 'Practiced');
    await p.screenshot({ path: path.join(SHOTS_DIR, '04_result_round1.png') });
    
    let s = await store(p);
    assert.strictEqual(s.version, 1);
    assert.strictEqual(s.skills.bode.tier, 1);
    assert(s.skills.bode.lastPracticed > now - 60000);
    assert.strictEqual(s.skills.bode.history.length, 1);
    
    await p.reload();
    await sleep(500);
    s = await store(p);
    assert.strictEqual(s.skills.bode.tier, 1);
    
    const cls = await p.$eval('#world .tile[data-id="bode"]', e => e.className);
    assert(/\bt1\b/.test(cls), cls);
    assert((await p.$eval('#pctTxt', e => e.textContent)) !== '0.0%');
    await p._ctx.close();
  });

  await test('failing a challenge keeps tier, history records fail; retry pass -> Level 1', async () => {
    const p = await newPage(T({ bode: { tier: 1, lastPracticed: now - 3 * DAY, history: [] } }));
    await openSkill(p, 'bode');
    assert(/Start mastery challenge → Level 1/.test(await p.$eval('#startBtn', e => e.textContent)));
    await p.click('#startBtn');
    await sleep(1000);
    
    await p.waitForSelector('.prog', { timeout: 10000 });
    assert(/at least 2 of 3/.test(await p.$eval('#rule', e => e.textContent)));
    await answerQuiz(p, 'bode', [false, true, false]);
    assert.strictEqual(await p.$eval('#score', e => e.textContent), '1 / 3');
    assert(/stays at Practiced/.test(await p.$eval('#failNote', e => e.textContent)));
    
    let s = await store(p);
    assert.strictEqual(s.skills.bode.tier, 1);
    assert.strictEqual(s.skills.bode.history.length, 1);
    assert.strictEqual(s.skills.bode.history[0].passed, false);
    
    await p.click('#resRetry');
    await sleep(1000);
    await p.waitForSelector('.prog', { timeout: 10000 });
    await answerQuiz(p, 'bode', [true, true, false]);
    assert.strictEqual(await p.$eval('#score', e => e.textContent), '2 / 3');
    assert.strictEqual(await p.$eval('#newTier', e => e.textContent), 'Level 1');
    
    s = await store(p);
    assert.strictEqual(s.skills.bode.tier, 2);
    assert.strictEqual(s.skills.bode.history.length, 2);
    await p._ctx.close();
  });

  await test('full climb: Level 2 -> Mastered, review mode changes nothing', async () => {
    const p = await newPage(T({ bode: { tier: 3, lastPracticed: now - DAY, history: [] } }));
    await openSkill(p, 'bode');
    await p.click('#startBtn');
    await sleep(1000);
    await p.waitForSelector('.prog', { timeout: 10000 });
    await answerQuiz(p, 'bode', [true, true, true]);
    assert.strictEqual(await p.$eval('#newTier', e => e.textContent), 'Mastered');
    assert.strictEqual((await store(p)).skills.bode.tier, 4);
    await p.click('#resBack');
    await sleep(500);
    assert(/Mastered/.test(await p.$eval('#panelTier', e => e.textContent)));
    await p.screenshot({ path: path.join(SHOTS_DIR, '05_panel_mastered.png') });
    
    const hl = (await store(p)).skills.bode.history.length;
    await p.click('#startBtn');
    await sleep(1000);
    await p.waitForSelector('.prog', { timeout: 10000 });
    await answerQuiz(p, 'bode', [false, false, false]);
    const s = await store(p);
    assert.strictEqual(s.skills.bode.tier, 4);
    assert.strictEqual(s.skills.bode.history.length, hl);
    await p._ctx.close();
  });

  await test('queue ordering: least-recently practiced first; mastered/unpracticed excluded', async () => {
    const p = await newPage(T({
      'cx-exp': { tier: 2, lastPracticed: now - 1 * DAY, history: [] },
      'rc-lpf': { tier: 1, lastPracticed: now - 10 * DAY, history: [] },
      'lti-def': { tier: 3, lastPracticed: now - 5 * DAY, history: [] },
      'tf': { tier: 4, lastPracticed: now - 30 * DAY, history: [] },
      'bode': { tier: 1, lastPracticed: now - 2 * DAY, history: [] },
      'phasors': { tier: 0, lastPracticed: null, history: [] },
      'pole-zero': { tier: 1, lastPracticed: now - 7 * DAY, history: [] }
    }));
    assert.strictEqual(await p.$eval('#qCount', e => e.textContent), '5');
    await p.click('#btnQueue');
    await sleep(250);
    const rows = await p.$$eval('.qrow', r => r.map(x => x.dataset.id));
    assert.deepStrictEqual(rows, ['rc-lpf', 'pole-zero', 'lti-def', 'bode', 'cx-exp']);
    await p.screenshot({ path: path.join(SHOTS_DIR, '06_queue.png') });
    await p._ctx.close();
  });

  await test('export / import merge', async () => {
    const p = await newPage(T({ bode: { tier: 2, lastPracticed: now - 2 * DAY, history: [] } }));
    const exported = await p.evaluate(() => {
      return new Promise(resolve => {
        const orig = URL.createObjectURL;
        URL.createObjectURL = blob => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.readAsText(blob);
          return 'blob:fake';
        };
        document.getElementById('btnExport').click();
        URL.createObjectURL = orig;
      });
    });
    const exp = JSON.parse(exported);
    assert.strictEqual(exp.skills.bode.tier, 2);
    
    exp.skills['lti-def'] = { tier: 3, lastPracticed: now - 1 * DAY, history: [] };
    exp.skills.bode.tier = 1;
    
    const p2 = await newPage(T({ bode: { tier: 2, lastPracticed: now - 2 * DAY, history: [] } }));
    await p2.evaluate(data => {
      const blob = new Blob([data], { type: 'application/json' });
      const file = new File([blob], 'test.json', { type: 'application/json' });
      const dt = new DataTransfer();
      dt.items.add(file);
      const input = document.getElementById('fileIn');
      input.files = dt.files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }, JSON.stringify(exp));
    await sleep(500);
    await p2.click('#impMerge');
    await sleep(300);
    
    const s = await store(p2);
    assert.strictEqual(s.skills.bode.tier, 2);
    assert.strictEqual(s.skills['lti-def'].tier, 3);
    
    await p._ctx.close();
    await p2._ctx.close();
  });

  await test('layout toggle grouped <-> tree persists and animates', async () => {
    const p = await newPage();
    assert.strictEqual(await p.$eval('#btnGroup', e => e.getAttribute('aria-pressed')), 'false');
    await p.click('#btnGroup');
    await sleep(700);
    assert.strictEqual(await p.$eval('#btnGroup', e => e.getAttribute('aria-pressed')), 'true');
    const grouped = await p.evaluate(() => localStorage.getItem('skilltree.layout.v1'));
    assert.strictEqual(grouped, 'grouped');
    await p.screenshot({ path: path.join(SHOTS_DIR, '07_grouped.png') });
    
    await p.reload();
    await sleep(500);
    assert.strictEqual(await p.$eval('#btnGroup', e => e.getAttribute('aria-pressed')), 'true');
    await p._ctx.close();
  });

  await test('learning plan modal with charts', async () => {
    const p = await newPage(T({
      'cx-exp': { tier: 1, lastPracticed: now - 1 * DAY, history: [] },
      'lti-def': { tier: 2, lastPracticed: now - 2 * DAY, history: [] }
    }));
    await p.click('#btnPlan');
    await sleep(500);
    assert(await p.$('#planSessions'));
    assert(await p.$('#minChart'));
    assert(await p.$('#tierChart'));
    await p.screenshot({ path: path.join(SHOTS_DIR, '08_plan.png') });
    await p.keyboard.press('Escape');
    await p._ctx.close();
  });

  await test('non-trailing-slash URL loads correctly (base URL fix)', async () => {
    const noSlashUrl = BASE_URL.replace(/\/$/, '');
    const ctx = await browser.createBrowserContext();
    const p = await ctx.newPage();
    await p.setViewport({ width: 1280, height: 800 });
    p.on('console', m => { if (['error', 'warning'].includes(m.type())) errs.push(m.type() + ': ' + m.text()) });
    p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
    
    await p.setRequestInterception(true);
    p.on('request', req => {
      if (req.url().includes('supabase.min.js')) {
        req.respond({ status: 200, contentType: 'application/javascript', body: `window.supabase={createClient:()=>window.__supabaseMock};` });
      } else req.continue();
    });
    
    await p.evaluateOnNewDocument(() => {
      window.__supabaseMock = {
        auth: {
          getSession: async () => ({ data: { session: null } }),
          signInWithOtp: async () => ({ error: null }),
          signInWithOAuth: async () => ({ error: null }),
          signOut: async () => ({}),
          onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } })
        },
        from: () => ({
          select: () => ({ eq: () => ({ maybeSingle: async () => ({ data: null, error: null }) }) }),
          upsert: async () => ({ error: null })
        })
      };
    });
    
    await p.goto(noSlashUrl, { waitUntil: 'networkidle0', timeout: 30000 });
    await sleep(800);
    
    const loadingGone = await p.evaluate(() => !document.getElementById('loadingOverlay'));
    assert(loadingGone, 'loading overlay should be removed after data loads');
    
    const tiles = await p.evaluate(() => document.querySelectorAll('#world .tile').length);
    assert.strictEqual(tiles, NSKILL, 'should render every skill tile');
    
    const title = await p.$eval('h1', e => e.textContent);
    assert.strictEqual(title, 'Skillgrove');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '09_no_trailing_slash.png') });
    await ctx.close();
  });

  await test('Google OAuth button renders and calls signInWithOAuth', async () => {
    const ctx = await browser.createBrowserContext();
    const p = await ctx.newPage();
    await p.setViewport({ width: 1280, height: 800 });
    p.on('console', m => { if (['error', 'warning'].includes(m.type())) errs.push(m.type() + ': ' + m.text()) });
    p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
    
    await p.setRequestInterception(true);
    p.on('request', req => {
      if (req.url().includes('supabase.min.js')) {
        req.respond({ status: 200, contentType: 'application/javascript', body: `window.supabase={createClient:()=>window.__supabaseMock};` });
      } else req.continue();
    });
    
    await p.evaluateOnNewDocument(() => {
      window.__oauthCalls = [];
      window.__supabaseMock = {
        auth: {
          getSession: async () => ({ data: { session: null } }),
          signInWithOtp: async () => ({ error: null }),
          signInWithOAuth: async (opts) => { window.__oauthCalls.push(opts); return { error: null }; },
          signOut: async () => ({}),
          onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } })
        },
        from: () => ({
          select: () => ({ eq: () => ({ maybeSingle: async () => ({ data: null, error: null }) }) }),
          upsert: async () => ({ error: null })
        })
      };
    });
    
    await p.goto(BASE_URL, { waitUntil: 'networkidle0', timeout: 30000 });
    await sleep(500);
    
    await p.click('#btnSignIn');
    await sleep(300);
    
    const googleBtnExists = await p.$('#btnGoogleSignIn');
    assert(googleBtnExists, 'Google sign-in button should render when googleEnabled is true');
    
    const googleBtnText = await p.$eval('#btnGoogleSignIn', e => e.textContent.trim());
    assert(/Google/i.test(googleBtnText), 'Button should mention Google');
    
    await p.click('#btnGoogleSignIn');
    await sleep(200);
    
    const oauthCalls = await p.evaluate(() => window.__oauthCalls);
    assert.strictEqual(oauthCalls.length, 1, 'signInWithOAuth should be called once');
    assert.strictEqual(oauthCalls[0].provider, 'google', 'provider should be google');
    assert(oauthCalls[0].options.redirectTo.endsWith('/skilltree/'), 'redirectTo should end with /skilltree/');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '10_google_oauth_modal.png') });
    await ctx.close();
  });

  await test('explainer button shows for skills with explainers, opens modal with content', async () => {
    const p = await newPage();
    
    await openSkill(p, 'bode');
    await sleep(300);
    
    const explainerBtn = await p.$('#explainerBtn');
    assert(explainerBtn, 'explainer button should exist for bode skill');
    
    const btnText = await p.$eval('#explainerBtn', e => e.textContent);
    assert(/Read first|Explainer/i.test(btnText), 'button should say Read first or Explainer');
    
    await explainerBtn.click();
    await sleep(800);
    
    const modalOpen = await p.$eval('#modalBack', e => e.classList.contains('open'));
    assert(modalOpen, 'modal should be open');
    
    const explainerContent = await p.$('#explainerContent');
    assert(explainerContent, 'explainer content should be present');
    
    const sections = await p.$$eval('.exp-section', els => els.length);
    assert(sections >= 1, 'should have at least one section');
    
    const hasKatex = await p.$eval('.explainer-body', e => e.querySelector('.katex') !== null);
    assert(hasKatex, 'should render KaTeX math');
    const hasFig = await p.$('#explainerContent .qfig svg');
    assert(hasFig, 'explainer diagram should render');
    const katexErrs = await p.evaluate(() => (window.__katexErrors || []).slice());
    assert.deepStrictEqual(katexErrs, [], 'KaTeX errors: ' + katexErrs.join(' | '));
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '11_explainer_modal.png') });
    
    await p.keyboard.press('Escape');
    await sleep(200);
    await p._ctx.close();
  });

  await test('skill without explainer has no explainer button', async () => {
    const p = await newPage();
    
    const retired = await p.evaluate(() => window.__skillgrove.retired());
    assert.strictEqual(retired.clm, 'ro', 'retired map should send clm to ro');
    assert.strictEqual(retired.margins, 'stability', 'retired map should send margins to stability');
    const hasExplainer = await p.evaluate(() => window.__skillgrove.explainers.has('clm'));
    assert(!hasExplainer, 'retired id clm should not have an explainer');
    
    await p._ctx.close();
  });

  await test('lights mode activates when zoomed out below threshold', async () => {
    const p = await newPage(T({
      'bode': { tier: 4, lastPracticed: now - DAY, history: [] },
      'phasors': { tier: 4, lastPracticed: now - 2 * DAY, history: [] },
      'lti-def': { tier: 3, lastPracticed: now - DAY, history: [] },
      'cx-exp': { tier: 2, lastPracticed: now - DAY, history: [] },
      'rc-lpf': { tier: 1, lastPracticed: now - DAY, history: [] }
    }));
    
    const threshold = await p.evaluate(() => window.__skillgrove.lights.threshold);
    assert(typeof threshold === 'number', 'threshold should be a number');
    
    let lightsOn = await p.evaluate(() => window.__skillgrove.lights.mode());
    assert(!lightsOn, 'lights mode should be off at normal zoom');
    
    await p.evaluate(() => window.__skillgrove.lights.setScale(0.25));
    await sleep(100);
    
    lightsOn = await p.evaluate(() => window.__skillgrove.lights.mode());
    assert(lightsOn, 'lights mode should be on when zoomed out');
    
    const worldHasClass = await p.$eval('#world', e => e.classList.contains('lights-view'));
    assert(worldHasClass, 'world should have lights-view class');
    
    const lightModeCount = await p.$$eval('#world .tile.light-mode', els => els.length);
    assert.strictEqual(lightModeCount, NSKILL, 'all tiles should have light-mode class');
    
    const lightDot = await p.$('.tile.t4 .light-dot');
    assert(lightDot, 'mastered tile should have light-dot element');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '12_lights_mode.png') });
    
    await p.evaluate(() => window.__skillgrove.lights.setScale(0.8));
    await sleep(100);
    
    lightsOn = await p.evaluate(() => window.__skillgrove.lights.mode());
    assert(!lightsOn, 'lights mode should turn off when zoomed back in');
    
    await p._ctx.close();
  });

  await test('lights mode hover does not repaint the tree or change its pixels', async () => {
    const p = await newPage();
    await p.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(400);

    const target = await p.evaluate(() => {
      window.__skillgrove.lights.setScale(0.25);
      const s = 0.25;
      const tv = document.getElementById('treeView');
      const world = document.getElementById('world');
      const tiles = [...document.querySelectorAll('#world .tile')];
      tiles.sort((a, b) => parseFloat(a.style.top) - parseFloat(b.style.top) || parseFloat(a.style.left) - parseFloat(b.style.left));
      const tile = tiles[Math.floor(tiles.length * 0.45)];
      const wx = parseFloat(tile.style.left) + 84;
      const wy = parseFloat(tile.style.top) + 36;
      const vr = tv.getBoundingClientRect();
      world.style.transform = `translate(${vr.width / 2 - wx * s}px,${vr.height / 2 - wy * s}px) scale(${s})`;
      document.getAnimations().forEach(a => a.pause());
      const r = tile.getBoundingClientRect();
      window.__treeMut = [];
      const mo = new MutationObserver(recs => {
        for (const rec of recs) {
          window.__treeMut.push({
            type: rec.type,
            target: rec.target.id || rec.target.className || rec.target.nodeName,
            attr: rec.attributeName,
            added: rec.addedNodes.length,
            removed: rec.removedNodes.length
          });
        }
      });
      mo.observe(world, { subtree: true, attributes: true, childList: true });
      return { id: tile.dataset.id, x: r.x + r.width / 2, y: r.y + r.height / 2, lights: window.__skillgrove.lights.mode() };
    });
    assert(target.lights, 'lights mode should be on');
    const hit = await p.evaluate((x, y) => {
      const el = document.elementFromPoint(x, y);
      const tile = el && el.closest ? el.closest('.tile') : null;
      return tile ? tile.dataset.id : null;
    }, target.x, target.y);
    assert.strictEqual(hit, target.id, 'pointer should be over the skill dot');

    const tree = await p.$('#treeView');
    const before = await tree.screenshot({ type: 'png' });
    await p.tracing.start({ categories: ['devtools.timeline'] });
    await p.mouse.move(target.x, target.y);
    await sleep(280);
    const traceBuf = await p.tracing.stop();
    const during = await tree.screenshot({ type: 'png' });
    await sleep(200);
    const after = await tree.screenshot({ type: 'png' });
    fs.writeFileSync(path.join(SHOTS_DIR, '12b_lights_hover.png'), after);

    const paints = JSON.parse(Buffer.from(traceBuf).toString('utf8')).traceEvents.filter(e => e.name === 'Paint');
    const exploded = paints.filter(e => {
      const c = e.args.data.clip;
      const w = Math.abs(c[2] - c[0]);
      return e.args.data.nodeName !== '#document' && w > 8000;
    }).map(e => e.args.data.nodeName);
    assert.deepStrictEqual(exploded, [], 'hover should not repaint the world or edge layer: ' + exploded.join(', '));

    const mut = await p.evaluate(() => window.__treeMut);
    const structural = mut.filter(m => m.type === 'childList' && (m.added || m.removed));
    assert.deepStrictEqual(structural, [], 'hover should not rebuild the tree');
    assert.strictEqual(mut.length, 0, 'hover should not restyle the tree: ' + JSON.stringify(mut.slice(0, 6)));

    const hoverState = await p.evaluate(() => {
      const tile = document.querySelector('#world .tile:hover');
      const cs = tile ? getComputedStyle(tile) : null;
      return {
        active: document.getElementById('edges').classList.contains('active'),
        transform: cs ? cs.transform : null,
        background: cs ? cs.backgroundColor : null
      };
    });
    assert.strictEqual(hoverState.active, false, 'lights mode should not highlight every edge');
    assert.strictEqual(hoverState.transform, 'none');
    assert.strictEqual(hoverState.background, 'rgba(0, 0, 0, 0)');

    const mid = pixelDiffCount(before, during);
    const end = pixelDiffCount(before, after);
    assert.strictEqual(mid.n, 0, `hover frame changed ${mid.n} of ${mid.pixels} tree pixels`);
    assert.strictEqual(end.n, 0, `settled hover changed ${end.n} of ${end.pixels} tree pixels`);

    await p.mouse.move(4, 4);
    const zoomed = await p.evaluate((id) => {
      window.__skillgrove.lights.setScale(1);
      const s = 1;
      const tv = document.getElementById('treeView');
      const world = document.getElementById('world');
      const tile = document.querySelector('#world .tile[data-id="' + id + '"]');
      const wx = parseFloat(tile.style.left) + 84;
      const wy = parseFloat(tile.style.top) + 36;
      const vr = tv.getBoundingClientRect();
      world.style.transform = `translate(${vr.width / 2 - wx * s}px,${vr.height / 2 - wy * s}px) scale(${s})`;
      const r = tile.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, lights: window.__skillgrove.lights.mode() };
    }, target.id);
    assert.strictEqual(zoomed.lights, false);
    await p.mouse.move(zoomed.x, zoomed.y);
    await sleep(50);
    const highlighted = await p.evaluate(() => ({
      active: document.getElementById('edges').classList.contains('active'),
      marked: document.querySelectorAll('#edges path.in, #edges path.out').length
    }));
    assert.strictEqual(highlighted.active, true, 'zoomed-in hover should still highlight edges');
    assert(highlighted.marked > 0, 'zoomed-in hover should mark the connected edges');

    await p._ctx.close();
  });

  await test('collections: EE105 course with 18 chapter boxes loads correctly', async () => {
    const p = await newPage();
    
    const collections = await p.evaluate(() => {
      const sg = window.__skillgrove;
      if (!sg || !sg.collections) return null;
      return {
        boxCount: Object.keys(sg.collections.boxById()).length,
        courseBox: sg.collections.boxById()['ee105-ucb'],
        chapterBoxes: Object.values(sg.collections.boxById()).filter(b => b.kind === 'chapter'),
        skillMappings: sg.collections.skillToBoxes()
      };
    });
    
    assert(collections, 'collections should be loaded');
    assert.strictEqual(collections.boxCount, NBOX, 'should have every course, textbook, and chapter box');
    
    assert(collections.courseBox, 'EE105 course box should exist');
    assert.strictEqual(collections.courseBox.kind, 'course');
    assert.strictEqual(collections.courseBox.title, 'EE 105 (UC Berkeley)');
    assert.strictEqual(collections.courseBox.children.length, 18, 'course should have 18 chapter children');
    
    assert.strictEqual(collections.chapterBoxes.length, NCHAPTER, 'should have a chapter box for every chapter');
    
    const bodeBoxes = collections.skillMappings['bode'];
    assert(bodeBoxes, 'bode skill should be mapped to boxes');
    assert(bodeBoxes.includes('ee105-ch2'), 'bode should be in chapter 2');
    
    await p._ctx.close();
  });

  await test('collections: getSkillColorIndex returns box color_index', async () => {
    const p = await newPage();
    
    const colorTests = await p.evaluate(() => {
      const sg = window.__skillgrove;
      if (!sg || !sg.collections) return null;
      
      return {
        bodeColor: sg.collections.getSkillColorIndex('bode'),
        phasorsColor: sg.collections.getSkillColorIndex('phasors'),
        ch2Box: sg.collections.boxById()['ee105-ch2'],
        ltiColor: sg.collections.getSkillColorIndex('lti-def'),
        ch1Box: sg.collections.boxById()['ee105-ch1']
      };
    });
    
    assert(colorTests, 'color tests should run');
    assert.strictEqual(colorTests.bodeColor, 2, 'bode should get color_index 2 from chapter 2');
    assert.strictEqual(colorTests.phasorsColor, 2, 'phasors should get color_index 2 from chapter 2');
    assert.strictEqual(colorTests.ch2Box.color_index, 2, 'chapter 2 box should have color_index 2');
    assert.strictEqual(colorTests.ltiColor, 1, 'lti-def should get color_index 1 from chapter 1');
    assert.strictEqual(colorTests.ch1Box.color_index, 1, 'chapter 1 box should have color_index 1');
    
    await p._ctx.close();
  });

  await test('rebranded header shows Skillgrove name and STEM tagline', async () => {
    const p = await newPage();
    
    const header = await p.evaluate(() => ({
      h1: document.querySelector('h1').textContent,
      sub: document.querySelector('.sub').textContent,
      title: document.title,
      metaDesc: document.querySelector('meta[name="description"]').content,
      btnGroup: document.querySelector('#btnGroup .t').textContent
    }));
    
    assert.strictEqual(header.h1, 'Skillgrove', 'h1 should say Skillgrove');
    assert(/Master STEM skills/i.test(header.sub), 'subtitle should mention STEM skills');
    assert(/one node at a time/i.test(header.sub), 'subtitle should have tagline');
    assert(/Skillgrove/i.test(header.title), 'page title should mention Skillgrove');
    assert(/STEM/i.test(header.metaDesc), 'meta description should mention STEM');
    assert(/Group by course/i.test(header.btnGroup), 'group button should say "Group by course"');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '13_rebranded_header.png') });
    await p._ctx.close();
  });

  await test('nested grouped view: course box contains chapter boxes', async () => {
    const p = await newPage();
    
    await p.click('#btnGroup');
    await sleep(700);
    
    const layout = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const grouped = sg.layout().grouped;
      const courseBlob = grouped.blobs['ee105-ucb'];
      const ch1Blob = grouped.blobs['ee105-ch1'];
      const ch2Blob = grouped.blobs['ee105-ch2'];
      return {
        hasNested: grouped.useNested,
        courseBlob: courseBlob ? { x: courseBlob.x, y: courseBlob.y, w: courseBlob.w, h: courseBlob.h, kind: courseBlob.kind } : null,
        ch1Blob: ch1Blob ? { x: ch1Blob.x, y: ch1Blob.y, w: ch1Blob.w, h: ch1Blob.h } : null,
        ch2Blob: ch2Blob ? { x: ch2Blob.x, y: ch2Blob.y, w: ch2Blob.w, h: ch2Blob.h } : null,
        domCourseBlob: !!document.querySelector('.blob.course[data-box="ee105-ucb"]'),
        domChapterBlobs: document.querySelectorAll('.blob.chapter').length
      };
    });
    
    assert(layout.hasNested, 'should use nested layout');
    assert(layout.courseBlob, 'course blob should exist');
    assert.strictEqual(layout.courseBlob.kind, 'course', 'course blob should have kind=course');
    assert(layout.ch1Blob, 'chapter 1 blob should exist');
    assert(layout.ch2Blob, 'chapter 2 blob should exist');
    assert(layout.domCourseBlob, 'DOM should have course blob element');
    assert.strictEqual(layout.domChapterBlobs, NCHAPTER, 'DOM should have a chapter blob for every chapter');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '14_nested_grouped.png') });
    await p._ctx.close();
  });

  await test('scope selector filters the tree and the learning plan', async () => {
    const p = await newPage();

    const controls = await p.evaluate(() => ({
      selects: [...document.querySelectorAll('#hctl select')].map(e => e.id),
      picker: document.getElementById('scopePicker') && document.getElementById('scopePicker').tagName,
      oldChapter: !!document.getElementById('chSel'),
      oldBox: !!document.getElementById('boxPicker'),
      oldPlan: !!document.getElementById('planScopePicker'),
      all: !!document.getElementById('scopeAll'),
      none: !!document.getElementById('scopeNone')
    }));
    assert.deepStrictEqual(controls.selects, [], 'the single scope dropdown should be gone');
    assert.strictEqual(controls.picker, 'DIV');
    assert.strictEqual(controls.oldChapter, false, 'the old chapter filter should be gone');
    assert.strictEqual(controls.oldBox, false, 'the old box filter should be gone');
    assert.strictEqual(controls.oldPlan, false);
    assert(controls.all && controls.none, 'All and None shortcuts should be present');

    const options = await p.$$eval('#scopePicker .scope-row', rows => rows.map(row => ({
      value: row.querySelector('input').value,
      text: row.querySelector('span').textContent,
      depth: row.classList.contains('depth')
    })));
    const courseAt = options.findIndex(o => o.value === 'ee105-ucb');
    const ch1At = options.findIndex(o => o.value === 'ee105-ch1');
    const ch2At = options.findIndex(o => o.value === 'ee105-ch2');
    assert(courseAt >= 0, 'picker should list the course from collections');
    assert(ch1At > courseAt && ch2At > ch1At, 'chapters should be nested under their course');
    assert(options[ch1At].depth && options[ch2At].depth);
    assert(!options[courseAt].depth);
    assert(/Ch 2:/.test(options[ch2At].text), options[ch2At].text);
    assert.strictEqual(options.length, NBOX);

    await p.click('#btnPlan');
    await sleep(400);
    const allSkillsSessions = await p.$eval('#planSessions', e => parseInt(e.textContent, 10));
    assert(allSkillsSessions > 0, 'all skills should have sessions');
    assert.strictEqual(await p.$('#planScopePicker'), null, 'the plan should not grow a second scope selector');
    assert.strictEqual(await p.$$eval('#modal select', els => els.length), 0);
    await p.keyboard.press('Escape');
    await sleep(200);

    await pickBoxes(p, ['ee105-ch2']);
    const filterResult = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const dimmedTiles = document.querySelectorAll('#world .tile.boxdim').length;
      const visibleTiles = document.querySelectorAll('#world .tile:not(.boxdim)').length;
      const ch2Skills = sg.collections.getBoxDescendantSkills('ee105-ch2');
      const drawn = [...document.querySelectorAll('#regions .blob')].map(b => b.dataset.box);
      return {
        filterActive: JSON.stringify(sg.collections.filter()) === JSON.stringify(['ee105-ch2']),
        planScope: sg.collections.scope(),
        stored: localStorage.getItem('skilltree.planscope.v1'),
        dimmedTiles,
        visibleTiles,
        ch2SkillCount: ch2Skills.length,
        drawn,
        tileCount: document.querySelectorAll('#world .tile').length
      };
    });
    assert(filterResult.filterActive, 'tree filter should follow the scope');
    assert.deepStrictEqual(filterResult.planScope, ['ee105-ch2'], 'plan scope should follow the same selection');
    assert.deepStrictEqual(JSON.parse(filterResult.stored), { v: 2, boxes: ['ee105-ch2'] });
    assert(filterResult.dimmedTiles > 0, 'skills outside the chapter should be dimmed');
    assert.strictEqual(filterResult.visibleTiles, filterResult.ch2SkillCount, 'undimmed tiles should match the chapter');
    assert.strictEqual(filterResult.tileCount, NSKILL, 'out-of-scope skills stay on the tree');
    assert.deepStrictEqual(filterResult.drawn, ['ee105-ch2']);

    await p.click('#btnPlan');
    await sleep(400);
    const ch2Plan = await p.evaluate(() => ({
      sessions: parseInt(document.getElementById('planSessions').textContent, 10),
      note: document.getElementById('planScopeNote').textContent,
      extras: (document.getElementById('planExtras') || {}).textContent || ''
    }));
    assert(ch2Plan.sessions > 0, 'chapter scope should still have a plan');
    assert(ch2Plan.sessions <= allSkillsSessions, 'chapter plan should be no larger than the full plan');
    assert(/Chapter 2/.test(ch2Plan.note), ch2Plan.note);
    assert(/outside this scope/i.test(ch2Plan.note));
    if (ch2Plan.extras) assert(/prerequisite.*outside/i.test(ch2Plan.extras));
    await p.keyboard.press('Escape');
    await sleep(200);

    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(500);
    const kept = await p.evaluate(() => ({
      checked: [...document.querySelectorAll('#scopePicker input:checked')].map(i => i.value),
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      scope: window.__skillgrove.collections.scope()
    }));
    assert.deepStrictEqual(kept.checked, ['ee105-ch2'], 'scope should survive reload');
    assert.deepStrictEqual(kept.scope, ['ee105-ch2']);
    assert(kept.dimmed > 0, 'tree should still be filtered after reload');

    await pickBoxes(p, ['ee105-ucb']);
    const course = await p.evaluate(() => ({
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      bright: document.querySelectorAll('#world .tile:not(.boxdim)').length,
      scope: window.__skillgrove.collections.scope(),
      members: window.__skillgrove.collections.getBoxDescendantSkills('ee105-ucb').length,
      drawn: [...document.querySelectorAll('#regions .blob')].map(b => b.dataset.box)
    }));
    assert.deepStrictEqual(course.scope, ['ee105-ucb']);
    assert.strictEqual(course.bright, course.members, 'every EE 105 skill stays undimmed');
    assert(course.dimmed > 0, 'skills outside EE 105 stay visible but dimmed');
    assert.deepStrictEqual(course.drawn, ['ee105-ucb']);

    await p.click('#scopeAll');
    await sleep(150);
    const cleared = await p.evaluate(() => ({
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      stored: JSON.parse(localStorage.getItem('skilltree.planscope.v1')),
      scope: window.__skillgrove.collections.scope(),
      blobs: document.querySelectorAll('.blob').length
    }));
    assert.strictEqual(cleared.dimmed, 0, 'All should show every skill');
    assert.deepStrictEqual(cleared.stored, { v: 2, all: true });
    assert.strictEqual(cleared.scope, null);
    assert.strictEqual(cleared.blobs, NBOX);
    await p.screenshot({ path: path.join(SHOTS_DIR, '16_scope_selector.png') });
    await p._ctx.close();
  });

  await test('multi-box skills: skill in multiple boxes handled correctly', async () => {
    const p = await newPage();
    
    const multiBoxTest = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const ltiDef = sg.collections.skillToBoxes()['lti-def'];
      const bode = sg.collections.skillToBoxes()['bode'];
      
      const inCh1 = sg.collections.skillInBox('lti-def', 'ee105-ch1');
      const inCourse = sg.collections.skillInBox('lti-def', 'ee105-ucb');
      const notInCh2 = !sg.collections.skillInBox('lti-def', 'ee105-ch2');
      
      return {
        ltiDefBoxes: ltiDef,
        bodeBoxes: bode,
        inCh1,
        inCourse,
        notInCh2
      };
    });
    
    assert(Array.isArray(multiBoxTest.ltiDefBoxes), 'lti-def should have box array');
    assert(multiBoxTest.ltiDefBoxes.includes('ee105-ch1'), 'lti-def should be in ch1');
    assert(multiBoxTest.bodeBoxes.includes('ee105-ch2'), 'bode should be in ch2');
    assert(multiBoxTest.inCh1, 'skillInBox should return true for direct membership');
    assert(multiBoxTest.inCourse, 'skillInBox should return true for parent course');
    assert(multiBoxTest.notInCh2, 'skillInBox should return false for wrong chapter');
    
    await p._ctx.close();
  });

  await test('lights mode works with nested boxes', async () => {
    const p = await newPage(T({
      'bode': { tier: 4, lastPracticed: now - DAY, history: [] },
      'phasors': { tier: 4, lastPracticed: now - 2 * DAY, history: [] }
    }));
    
    await p.click('#btnGroup');
    await sleep(700);
    
    await p.evaluate(() => window.__skillgrove.lights.setScale(0.25));
    await sleep(100);
    
    const lightsResult = await p.evaluate(() => ({
      lightsOn: window.__skillgrove.lights.mode(),
      worldHasClass: document.querySelector('#world').classList.contains('lights-view'),
      lightModeCount: document.querySelectorAll('#world .tile.light-mode').length,
      tileCount: document.querySelectorAll('#world .tile').length,
      masteredHasShimmer: document.querySelector('.tile[data-id="bode"].t4 .light-dot') !== null
    }));
    
    assert(lightsResult.lightsOn, 'lights mode should be on');
    assert(lightsResult.worldHasClass, 'world should have lights-view class');
    assert.strictEqual(lightsResult.lightModeCount, lightsResult.tileCount, 'all tiles should have light-mode');
    assert(lightsResult.masteredHasShimmer, 'mastered tile should have light-dot');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '17_lights_nested.png') });
    await p._ctx.close();
  });

  await test('quiz prompt renders LaTeX and the question diagram', async () => {
    const p = await newPage();
    await openSkill(p, 'square-law');
    await p.click('#startBtn');
    await p.waitForSelector('#qPrompt .katex', { timeout: 10000 });
    const fig = await p.$('#quiz .qfig svg');
    assert(fig, 'question diagram should render as SVG');
    const label = await p.$eval('#quiz .qfig svg', e => e.getAttribute('aria-label'));
    assert(label && label.length > 0, 'diagram should keep its label');
    const katexErrs = await p.evaluate(() => (window.__katexErrors || []).slice());
    assert.deepStrictEqual(katexErrs, [], 'KaTeX errors: ' + katexErrs.join(' | '));
    await p.screenshot({ path: path.join(SHOTS_DIR, '18_quiz_latex_figure.png') });
    await p._ctx.close();
  });

  await test('local progress on retired ids moves to the survivor and stays there', async () => {
    const p = await newPage(T({
      saturation: { tier: 2, lastPracticed: now - 5 * DAY, history: [{ t: now - 5 * DAY, round: 2, correct: 2, total: 3, passed: true }] },
      'square-law': { tier: 4, lastPracticed: now - DAY, history: [{ t: now - DAY, round: 4, correct: 3, total: 3, passed: true }] },
      'bjt-gain': { tier: 3, lastPracticed: now - 2 * DAY, history: [{ t: now - 2 * DAY, round: 3, correct: 2, total: 3, passed: true }] },
      margins: { tier: 2, lastPracticed: now - 4 * DAY, history: [{ t: now - 4 * DAY, round: 2, correct: 2, total: 3, passed: true }] },
      'not-a-skill': { tier: 1, lastPracticed: now - 3 * DAY, history: [] }
    }));
    const s = await store(p);
    assert.strictEqual(s.skills.saturation, undefined);
    assert.strictEqual(s.skills['bjt-gain'], undefined);
    assert.strictEqual(s.skills['square-law'].tier, 4, 'survivor keeps the higher tier');
    assert.strictEqual(s.skills['square-law'].lastPracticed, now - DAY, 'later practice time wins');
    assert.strictEqual(s.skills['square-law'].history.length, 2, 'both histories are kept');
    assert.strictEqual(s.skills['bjt-action'].tier, 3);
    assert.strictEqual(s.skills['bjt-action'].lastPracticed, now - 2 * DAY);
    assert.strictEqual(s.skills.margins, undefined);
    assert.strictEqual(s.skills.stability.tier, 2, 'margins progress merges into stability');
    assert.strictEqual(s.skills.stability.lastPracticed, now - 4 * DAY);
    assert.strictEqual(s.skills['lti-circuits'], undefined, 'a new application skill starts at zero');
    assert.strictEqual(s.skills['not-a-skill'].tier, 1, 'unrelated ids are preserved');

    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(500);
    const again = await store(p);
    assert.strictEqual(again.skills.saturation, undefined);
    assert.deepStrictEqual(again.skills['square-law'], s.skills['square-law']);
    assert.deepStrictEqual(again.skills['bjt-action'], s.skills['bjt-action']);
    await p._ctx.close();
  });

  await test('signed-in sync migrates retired ids on both devices before merging', async () => {
    const p = await newPage();
    const result = await p.evaluate((now) => {
      const retired = window.__skillgrove.retired();
      const merge = window.SkillgroveAuth.mergeProgress;
      const day = 86400000;
      const local = { version: 1, skills: {
        saturation: { tier: 2, lastPracticed: now - 5 * day, history: [{ t: 1, passed: true }] },
        'body-amp': { tier: 1, lastPracticed: now - 9 * day, history: [{ t: 4, passed: false }] }
      }};
      const remote = { version: 1, skills: {
        'square-law': { tier: 1, lastPracticed: now - 8 * day, history: [{ t: 2, passed: true }] },
        saturation: { tier: 3, lastPracticed: now - day, history: [{ t: 3, passed: true }] },
        'cd-real': { tier: 4, lastPracticed: now - 2 * day, history: [{ t: 5, passed: true }] }
      }};
      const once = window.SkillgroveMigrate.combineMigratedProgress(local, remote, retired, merge);
      const twice = window.SkillgroveMigrate.combineMigratedProgress(once.progress, once.progress, retired, merge);
      return {
        keys: Object.keys(once.progress.skills).sort(),
        square: once.progress.skills['square-law'],
        cd: once.progress.skills.cd,
        changed: once.changed,
        again: twice.changed,
        same: JSON.stringify(twice.progress.skills) === JSON.stringify(once.progress.skills)
      };
    }, now);
    assert.deepStrictEqual(result.keys, ['cd', 'square-law']);
    assert.strictEqual(result.square.tier, 3);
    assert.strictEqual(result.square.lastPracticed, now - DAY);
    assert.strictEqual(result.square.history.length, 3);
    assert.strictEqual(result.cd.tier, 4);
    assert.strictEqual(result.cd.lastPracticed, now - 2 * DAY);
    assert.strictEqual(result.changed, true);
    assert.strictEqual(result.again, false);
    assert.strictEqual(result.same, true);
    await p._ctx.close();
  });

  await test('learning plan includes out-of-box prerequisites with star marker', async () => {
    const p = await newPage();
    
    const prereqTest = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const ch2Skills = sg.collections.getBoxDescendantSkills('ee105-ch2');
      
      const allPlayable = sg.playableIds();
      const ch2Playable = ch2Skills.filter(id => allPlayable.includes(id));
      
      const r = sg.plan(true, 'ee105-ch2');
      return {
        ch2PlayableCount: ch2Playable.length,
        planScope: r.scope,
        extras: r.extras || [],
        ok: r.ok,
        hasExtras: (r.extras || []).length > 0
      };
    });
    
    assert(prereqTest.ok, 'plan should succeed');
    assert(prereqTest.planScope > prereqTest.ch2PlayableCount || prereqTest.hasExtras, 
      'plan scope should include extras or be larger than ch2 playable count');
    
    if (prereqTest.hasExtras) {
      await pickBoxes(p, ['ee105-ch2']);
      await p.click('#btnPlan');
      await sleep(400);
      
      const extrasNote = await p.$('#planExtras');
      if (extrasNote) {
        const text = await p.$eval('#planExtras', e => e.textContent);
        assert(/prerequisite.*outside/i.test(text), 'should show prerequisites outside scope note');
      }
      
      await p.screenshot({ path: path.join(SHOTS_DIR, '19_plan_prereq_extras.png') });
    }

    await p._ctx.close();
  });

  await test('scope selector lists ME 132 and Feedback Systems as independent choices', async () => {
    const p = await newPage();
    const options = await p.$$eval('#scopePicker .scope-row', rows => rows.map(row => ({
      value: row.querySelector('input').value,
      text: row.querySelector('span').textContent
    })));
    const me = options.find(o => o.value === 'me132');
    const book = options.find(o => o.value === 'am08');
    assert(me, 'selector should list ME 132');
    assert(book, 'selector should list Feedback Systems');
    assert.strictEqual(me.text, 'ME 132 (UC Berkeley)');
    assert.strictEqual(book.text, 'Feedback Systems');
    assert(!/^[ \u00a0└]/.test(me.text) && !/^[ \u00a0└]/.test(book.text), 'both new boxes are top-level choices');
    const meAt = options.findIndex(o => o.value === 'me132');
    const bookAt = options.findIndex(o => o.value === 'am08');
    const eeAt = options.findIndex(o => o.value === 'ee105-ucb');
    assert(eeAt >= 0 && meAt > eeAt && bookAt > meAt, 'the three scopes are siblings, in collection order');
    const meChapters = options.filter(o => o.value.startsWith('me132/'));
    const bookChapters = options.filter(o => o.value.startsWith('am08/'));
    assert.strictEqual(meChapters.length, 9);
    assert.strictEqual(bookChapters.length, 13);
    assert(bookChapters.some(o => o.value === 'am08/ch99' && /Beyond the book/.test(o.text)));
    assert(meChapters.every(o => o.text.includes('└')));
    assert(bookChapters.every(o => o.text.includes('└')));
    const nesting = await p.evaluate(() => {
      const boxes = window.__skillgrove.collections.data().boxes;
      const me = boxes.find(b => b.id === 'me132');
      const book = boxes.find(b => b.id === 'am08');
      return {
        meKind: me.kind,
        bookKind: book.kind,
        meHoldsBook: (me.children || []).includes('am08'),
        bookHoldsMe: (book.children || []).includes('me132')
      };
    });
    assert.strictEqual(nesting.meKind, 'course');
    assert.strictEqual(nesting.bookKind, 'textbook');
    assert.strictEqual(nesting.meHoldsBook, false);
    assert.strictEqual(nesting.bookHoldsMe, false);
    await p._ctx.close();
  });

  await test('coming-soon skills stay out of readiness and the learning plan', async () => {
    const p = await newPage();
    const result = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const playable = new Set(sg.playableIds());
      const ready = sg.ready();
      const full = sg.plan(true, null);
      const me = sg.plan(true, 'me132');
      const book = sg.plan(true, 'am08');
      const practiced = rows => new Set((rows || []).flatMap(row => row.practiced || []));
      const challenged = rows => new Set((rows || []).flatMap(row => (row.challenges || []).map(c => c.id)));
      const used = plan => {
        const ids = new Set([...practiced(plan.rows), ...challenged(plan.rows), ...(plan.extras || []), ...(plan.critical && plan.critical.chain || [])]);
        return [...ids];
      };
      const fullIds = used(full);
      const meIds = used(me);
      const bookIds = used(book);
      const soon = 'fb-concepts';
      return {
        readySoon: ready.filter(id => !playable.has(id)),
        fullSoon: fullIds.filter(id => !playable.has(id)),
        meSoon: meIds.filter(id => !playable.has(id)),
        bookSoon: bookIds.filter(id => !playable.has(id)),
        fullCount: full.scope,
        playableCount: playable.size,
        fullOk: full.ok,
        meOk: me.ok,
        bookOk: book.ok,
        meHasSoon: meIds.includes(soon),
        meExtras: me.extras || [],
        readyHasSoon: ready.includes(soon),
        queueHasSoon: sg.queue().some(s => s.id === soon || !playable.has(s.id))
      };
    });
    assert.strictEqual(result.fullOk, true, 'full plan should succeed');
    assert.strictEqual(result.meOk, true, 'ME 132 plan should succeed');
    assert.strictEqual(result.bookOk, true, 'Feedback Systems plan should succeed');
    assert.strictEqual(result.fullCount, result.playableCount, 'the plan covers playable skills only');
    assert.deepStrictEqual(result.readySoon, [], 'readiness ignores coming-soon skills');
    assert.deepStrictEqual(result.fullSoon, [], 'coming-soon skills are excluded from the plan');
    assert.deepStrictEqual(result.meSoon, []);
    assert.deepStrictEqual(result.bookSoon, []);
    assert.strictEqual(result.meHasSoon, false);
    assert.strictEqual(result.readyHasSoon, false);
    assert.strictEqual(result.queueHasSoon, false, 'the recommender queue stays on playable skills');
    assert.deepStrictEqual(result.meExtras, [], 'every playable prerequisite of an ME 132 skill sits inside ME 132: ' + result.meExtras.join(','));

    await openSkill(p, 'fb-concepts');
    const panel = await p.evaluate(() => ({
      text: document.getElementById('panel').textContent,
      label: document.querySelector('#world .tile[data-id="fb-concepts"]').getAttribute('aria-label'),
      title: document.querySelector('#world .tile[data-id="fb-concepts"]').title,
      soon: document.querySelector('#world .tile[data-id="fb-concepts"]').classList.contains('soon'),
      start: !!document.getElementById('startBtn')
    }));
    assert(panel.soon, 'fb-concepts should use the coming-soon tile style');
    assert(/Coming soon/.test(panel.text));
    assert(/coming soon/.test(panel.title));
    assert(/Coming soon, no questions yet/.test(panel.label));
    assert.strictEqual(panel.start, false);
    await p._ctx.close();
  });

  await test('shared skills keep one progress record across boxes', async () => {
    const p = await newPage(T({
      bode: { tier: 4, lastPracticed: now - DAY, history: [] }
    }));
    await p.click('#btnGroup');
    await sleep(700);
    const shared = await p.evaluate(() => {
      const tiles = [...document.querySelectorAll('#world .tile[data-id="bode"]')];
      const stored = JSON.parse(localStorage.getItem('skilltree.progress.v1')).skills;
      const boxes = window.__skillgrove.collections.skillToBoxes()['bode'].slice().sort();
      return {
        tiles: tiles.length,
        tiers: tiles.map(t => t.classList.contains('t4')),
        records: Object.keys(stored).filter(id => id === 'bode').length,
        boxes
      };
    });
    assert.strictEqual(shared.tiles, 1, 'a shared skill is one tile');
    assert.deepStrictEqual(shared.boxes, ['am08/ch8', 'ee105-ch2', 'me132/m3']);
    assert(shared.tiers.every(Boolean), 'the single bode tile shows the mastered tier');
    assert.strictEqual(shared.records, 1);
    await p._ctx.close();
  });

  await test('ME 132 and Feedback Systems scopes render for review', async () => {
    const p = await newPage();
    await p.setViewport({ width: 1440, height: 900 });
    const shoot = async (scope, file) => {
      await pickBoxes(p, [scope]);
      const grouped = await p.$eval('#btnGroup', b => b.getAttribute('aria-pressed') === 'true');
      if (!grouped) {
        await p.click('#btnGroup');
        await sleep(800);
      }
      await p.evaluate(() => {
        const L = window.__skillgrove.layout().grouped;
        const box = Object.values(L.blobs).find(b => b.kind === 'course' || b.kind === 'textbook');
        const tv = document.getElementById('treeView');
        const vw = tv.clientWidth, vh = tv.clientHeight;
        const sliceH = Math.min(box.h, 1280);
        const s = Math.min(0.72, (vw - 48) / box.w, (vh - 36) / sliceH);
        const x = (vw - box.w * s) / 2 - box.x * s;
        const y = 16 - box.y * s;
        const world = document.getElementById('world');
        world.classList.remove('anim');
        world.style.transition = 'none';
        world.style.transform = `translate(${x}px,${y}px) scale(${s})`;
      });
      await sleep(250);
      const view = await p.evaluate(scope => {
        const sg = window.__skillgrove;
        const tiles = [...document.querySelectorAll('#world .tile')];
        const soon = tiles.filter(t => t.classList.contains('soon')).length;
        const bright = tiles.filter(t => !t.classList.contains('boxdim')).length;
        return {
          scope: sg.collections.scope(),
          title: (sg.collections.boxById()[scope] || {}).title,
          course: document.querySelectorAll('.blob.course.on').length,
          textbook: document.querySelectorAll('.blob.textbook.on').length,
          chapters: document.querySelectorAll('.blob.chapter.on').length,
          tiles: tiles.length,
          soon,
          bright,
          dimmed: document.querySelectorAll('#world .tile.boxdim').length,
          memberCount: sg.collections.getBoxDescendantSkills(scope).length,
          soonLabel: (document.querySelector('#world .tile.soon .tag') || {}).textContent || ''
        };
      }, scope);
      assert.deepStrictEqual(view.scope, [scope]);
      assert.strictEqual(view.bright, view.memberCount, scope + ' members stay undimmed');
      assert.strictEqual(view.tiles, NSKILL, scope + ' still draws every skill once');
      assert.strictEqual(view.dimmed, NSKILL - view.memberCount);
      if (scope === 'me132') {
        assert.strictEqual(view.title, 'ME 132 (UC Berkeley)');
        assert.strictEqual(view.course, 1);
        assert.strictEqual(view.textbook, 0);
        assert.strictEqual(view.chapters, 0, 'unselected chapters are not drawn');
      } else {
        assert.strictEqual(view.title, 'Feedback Systems');
        assert.strictEqual(view.course, 0);
        assert.strictEqual(view.textbook, 1);
        assert.strictEqual(view.chapters, 0, 'unselected chapters are not drawn');
      }
      assert(view.soon > 0, scope + ' should show coming-soon skills');
      assert.strictEqual(view.soonLabel, 'SOON');
      await p.screenshot({ path: path.join(SHOTS_DIR, file), fullPage: false });
    };
    await shoot('me132', '20_me132_scope.png');
    await shoot('am08', '21_feedback_systems_scope.png');
    await p._ctx.close();
  });

  await test('each skill renders exactly one tile', async () => {
    const p = await newPage();
    const tree = await p.evaluate(() => {
      const ids = [...document.querySelectorAll('#world .tile')].map(t => t.dataset.id);
      const counts = {};
      ids.forEach(id => { counts[id] = (counts[id] || 0) + 1; });
      const dupes = Object.keys(counts).filter(id => counts[id] !== 1);
      return {
        tiles: ids.length,
        dupes,
        toggles: document.querySelectorAll('#world .toggle, #regions .toggle').length,
        soon: document.querySelector('#world .tile[data-id="fb-concepts"] .tag').textContent
      };
    });
    assert.strictEqual(tree.tiles, NSKILL);
    assert.deepStrictEqual(tree.dupes, []);
    assert.strictEqual(tree.toggles, 0, 'collapse arrows are gone');
    assert.strictEqual(tree.soon, 'SOON');
    await p.click('#btnGroup');
    await sleep(700);
    const grouped = await p.evaluate(() => {
      const ids = [...document.querySelectorAll('#world .tile')].map(t => t.dataset.id);
      const counts = {};
      ids.forEach(id => { counts[id] = (counts[id] || 0) + 1; });
      return {
        tiles: ids.length,
        dupes: Object.keys(counts).filter(id => counts[id] !== 1),
        bode: document.querySelectorAll('#world .tile[data-id="bode"]').length
      };
    });
    assert.strictEqual(grouped.tiles, NSKILL);
    assert.deepStrictEqual(grouped.dupes, []);
    assert.strictEqual(grouped.bode, 1);
    await p.click('#btnGroup');
    await sleep(400);
    const back = await p.evaluate(() => document.querySelector('#world').dataset.layout);
    assert.strictEqual(back, 'tree', 'Ungroup restores the prerequisite tree');
    await p._ctx.close();
  });

  await test('selected regions contain their members and labels stay clear', async () => {
    const p = await newPage();
    await p.setViewport({ width: 1440, height: 900 });
    await p.click('#btnGroup');
    await sleep(800);

    const geometry = () => p.evaluate(() => {
      const world = document.getElementById('world');
      world.classList.remove('anim');
      world.style.transition = 'none';
      world.style.transform = 'translate(0px,0px) scale(1)';
      void world.offsetWidth;
      const sg = window.__skillgrove;
      const L = sg.layout().grouped;
      const inside = (poly, x, y) => {
        let c = false;
        for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
          const xi = poly[i][0], yi = poly[i][1], xj = poly[j][0], yj = poly[j][1];
          if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / ((yj - yi) || 1e-9) + xi)) c = !c;
        }
        return c;
      };
      const outside = [];
      const selected = sg.collections.selected();
      selected.forEach(id => {
        const blob = L.blobs[id];
        if (!blob) { outside.push(id + ' has no region'); return; }
        sg.collections.getBoxDescendantSkills(id).forEach(sid => {
          const n = L.nodes[sid];
          if (!n) { outside.push(sid + ' missing from ' + id); return; }
          const corners = [[n.x + 2, n.y + 2], [n.x + 166, n.y + 2], [n.x + 2, n.y + 70], [n.x + 166, n.y + 70]];
          if (!corners.every(([x, y]) => inside(blob.points, x, y))) outside.push(sid + ' outside ' + id);
        });
      });
      const hit = (a, b) => {
        const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        return w > 1 && h > 1;
      };
      const labels = [...document.querySelectorAll('.region-label')].map(n => ({ id: n.dataset.box, r: n.getBoundingClientRect() }));
      const tiles = [...document.querySelectorAll('#world .tile')].map(n => n.getBoundingClientRect());
      const labelHits = [];
      for (let i = 0; i < labels.length; i++) {
        for (let j = i + 1; j < labels.length; j++) {
          if (hit(labels[i].r, labels[j].r)) labelHits.push(labels[i].id + ' ∩ ' + labels[j].id);
        }
        if (tiles.some(t => hit(labels[i].r, t))) labelHits.push(labels[i].id + ' overlaps a tile');
      }
      const nesting = [];
      selected.forEach(id => {
        const box = sg.collections.boxById()[id];
        const parentId = (box && (sg.collections.data().boxes.find(b => (b.children || []).includes(id)) || {}).id) || null;
        if (!parentId || !selected.includes(parentId)) return;
        const parent = L.blobs[parentId], child = L.blobs[id];
        if (!parent || !child) { nesting.push(id + ' missing parent region'); return; }
        const cx = child.points.reduce((s, pt) => s + pt[0], 0) / child.points.length;
        const cy = child.points.reduce((s, pt) => s + pt[1], 0) / child.points.length;
        const tucked = child.points.every(([x, y]) => {
          const dx = cx - x, dy = cy - y, len = Math.hypot(dx, dy) || 1;
          return inside(parent.points, x + dx / len * 3, y + dy / len * 3);
        });
        if (!tucked) nesting.push(id + ' escapes ' + parentId);
      });
      return {
        outside: outside.slice(0, 8),
        outsideCount: outside.length,
        labelHits: labelHits.slice(0, 8),
        labelHitCount: labelHits.length,
        nesting: nesting.slice(0, 8),
        nestingCount: nesting.length,
        regions: selected.filter(id => L.blobs[id]).length,
        selected: selected.length
      };
    });

    const frame = async () => {
      await p.evaluate(() => {
        const panel = document.getElementById('scopePanel');
        if (panel && !panel.hidden) document.getElementById('scopeToggle').click();
        const L = window.__skillgrove.layout().grouped;
        const blobs = Object.values(L.blobs);
        const x0 = Math.min(...blobs.map(b => b.x)), y0 = Math.min(...blobs.map(b => b.y));
        const x1 = Math.max(...blobs.map(b => b.x + b.w)), y1 = Math.max(...blobs.map(b => b.y + b.h));
        const tv = document.getElementById('treeView');
        const pad = 16;
        const s = Math.min((tv.clientWidth - pad * 2) / (x1 - x0), (tv.clientHeight - pad * 2) / (y1 - y0));
        const world = document.getElementById('world');
        world.classList.remove('anim');
        world.style.transition = 'none';
        world.style.transform = `translate(${pad - x0 * s}px, ${pad - y0 * s}px) scale(${s})`;
      });
      await sleep(200);
    };

    let geo = await geometry();
    assert.strictEqual(geo.selected, NBOX, 'everything starts selected');
    assert.strictEqual(geo.regions, NBOX);
    assert.strictEqual(geo.outsideCount, 0, 'member outside its region: ' + geo.outside.join(', '));
    assert.strictEqual(geo.labelHitCount, 0, 'label collision: ' + geo.labelHits.join(', '));
    assert.strictEqual(geo.nestingCount, 0, 'chapter escaped its course: ' + geo.nesting.join(', '));
    await frame();
    await p.screenshot({ path: path.join(SHOTS_DIR, '24_everything_selected.png') });

    await pickBoxes(p, ['ee105-ucb', 'me132']);
    await sleep(400);
    geo = await geometry();
    assert.deepStrictEqual(await p.evaluate(() => window.__skillgrove.collections.selected()), ['ee105-ucb', 'me132']);
    assert.strictEqual(geo.regions, 2);
    assert.strictEqual(geo.outsideCount, 0, 'member outside its region: ' + geo.outside.join(', '));
    assert.strictEqual(geo.labelHitCount, 0, 'label collision: ' + geo.labelHits.join(', '));
    const overlap = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const both = sg.collections.getBoxDescendantSkills('ee105-ucb').filter(id => sg.collections.skillInBox(id, 'me132'));
      const L = sg.layout().grouped;
      const ee = L.blobs['ee105-ucb'], me = L.blobs['me132'];
      const inside = (poly, x, y) => {
        let c = false;
        for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
          const xi = poly[i][0], yi = poly[i][1], xj = poly[j][0], yj = poly[j][1];
          if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / ((yj - yi) || 1e-9) + xi)) c = !c;
        }
        return c;
      };
      const sharedInside = both.filter(id => {
        const n = L.nodes[id];
        const x = n.x + 84, y = n.y + 36;
        return inside(ee.points, x, y) && inside(me.points, x, y);
      });
      return { both: both.length, sharedInside: sharedInside.length, dimmed: document.querySelectorAll('#world .tile.boxdim').length };
    });
    assert(overlap.both > 0, 'EE 105 and ME 132 share skills');
    assert.strictEqual(overlap.sharedInside, overlap.both, 'shared skills sit in both regions');
    assert(overlap.dimmed > 0, 'skills outside both courses are dimmed');
    await frame();
    await p.screenshot({ path: path.join(SHOTS_DIR, '23_ee_me_overlap.png') });
    await p._ctx.close();
  });

  await test('multi-select drives the drawn regions and the plan union', async () => {
    const p = await newPage();
    await p.click('#btnGroup');
    await sleep(700);
    await pickBoxes(p, ['ee105-ucb', 'me132']);
    const drawn = await p.evaluate(() => ({
      regions: [...document.querySelectorAll('#regions .blob')].map(b => b.dataset.box).sort(),
      scope: window.__skillgrove.collections.scope(),
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      tiles: document.querySelectorAll('#world .tile').length
    }));
    assert.deepStrictEqual(drawn.regions, ['ee105-ucb', 'me132']);
    assert.deepStrictEqual(drawn.scope, ['ee105-ucb', 'me132']);
    assert.strictEqual(drawn.tiles, NSKILL);
    assert(drawn.dimmed > 0);

    const union = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const ids = new Set([...sg.collections.getBoxDescendantSkills('ee105-ucb'), ...sg.collections.getBoxDescendantSkills('me132')]);
      const playable = new Set(sg.playableIds());
      const inUnion = [...ids].filter(id => playable.has(id));
      const plan = sg.plan(true, ['ee105-ucb', 'me132']);
      const single = sg.plan(true, 'ee105-ucb');
      return {
        inUnion: inUnion.length,
        scope: plan.scope,
        extras: plan.extras || [],
        ok: plan.ok,
        sessions: plan.sessions,
        singleSessions: single.sessions
      };
    });
    assert.strictEqual(union.ok, true);
    assert(union.sessions > 0);
    assert(union.sessions >= union.singleSessions, 'the union plan is at least as large as one course');
    assert.strictEqual(union.scope, union.inUnion + union.extras.length, 'plan scope is the union plus out-of-scope prerequisites');
    union.extras.forEach(id => {
      assert(!drawn.regions.includes(id));
    });

    await p.click('#btnPlan');
    await sleep(400);
    const note = await p.$eval('#planScopeNote', e => e.textContent);
    assert(/EE 105/.test(note) && /ME 132/.test(note), note);
    assert.strictEqual(await p.$('#planEmpty'), null);
    await p.keyboard.press('Escape');
    await sleep(150);

    await p.evaluate(() => document.getElementById('scopeNone').click());
    await sleep(200);
    const none = await p.evaluate(() => ({
      regions: document.querySelectorAll('#regions .blob').length,
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      scope: window.__skillgrove.collections.scope(),
      tiles: document.querySelectorAll('#world .tile').length
    }));
    assert.strictEqual(none.regions, 0);
    assert.strictEqual(none.dimmed, NSKILL);
    assert.deepStrictEqual(none.scope, []);
    assert.strictEqual(none.tiles, NSKILL);
    await p.click('#btnPlan');
    await sleep(300);
    const empty = await p.$eval('#planEmpty', e => e.textContent);
    assert(/No boxes selected/.test(empty));
    await p._ctx.close();
  });

  await test('scope selection persists across reloads and migrates a saved single scope', async () => {
    const p = await newPage();
    await p.evaluate(() => localStorage.setItem('skilltree.planscope.v1', 'ee105-ch2'));
    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(500);
    const migrated = await p.evaluate(() => ({
      checked: [...document.querySelectorAll('#scopePicker input:checked')].map(i => i.value),
      scope: window.__skillgrove.collections.scope(),
      drawn: [...document.querySelectorAll('#regions .blob')].map(b => b.dataset.box),
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      stored: localStorage.getItem('skilltree.planscope.v1')
    }));
    assert.deepStrictEqual(migrated.checked, ['ee105-ch2'], 'an old single-scope value selects that box');
    assert.deepStrictEqual(migrated.scope, ['ee105-ch2']);
    assert.deepStrictEqual(migrated.drawn, ['ee105-ch2']);
    assert(migrated.dimmed > 0);
    assert.strictEqual(migrated.stored, 'ee105-ch2', 'the old value is kept until the selection changes');

    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(400);
    const still = await p.evaluate(() => window.__skillgrove.collections.scope());
    assert.deepStrictEqual(still, ['ee105-ch2']);

    await pickBoxes(p, ['ee105-ucb', 'me132']);
    const saved = await p.evaluate(() => localStorage.getItem('skilltree.planscope.v1'));
    assert.deepStrictEqual(JSON.parse(saved), { v: 2, boxes: ['ee105-ucb', 'me132'] });
    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(500);
    const kept = await p.evaluate(() => ({
      checked: [...document.querySelectorAll('#scopePicker input:checked')].map(i => i.value),
      scope: window.__skillgrove.collections.scope(),
      regions: [...document.querySelectorAll('#regions .blob')].map(b => b.dataset.box).sort()
    }));
    assert.deepStrictEqual(kept.checked, ['ee105-ucb', 'me132']);
    assert.deepStrictEqual(kept.scope, ['ee105-ucb', 'me132']);
    assert.deepStrictEqual(kept.regions, ['ee105-ucb', 'me132']);
    await p._ctx.close();
  });

  const ART = process.env.SKILLTREE_SHOTS || path.join(__dirname, 'shots');

  async function shot(p, name) {
    await p.evaluate(() => { const t = document.getElementById('toast'); if (t) t.classList.remove('show'); });
    const book = await p.$('#todoBook');
    await book.screenshot({ path: path.join(ART, name) });
  }

  await test('to-do list starts empty, adds and removes skills and challenges, and persists', async () => {
    const p = await newPage(T({ bode: { tier: 1, lastPracticed: now - DAY, history: [] } }));
    assert.strictEqual(await p.$('#banner .rd'), null, 'the top-bar ready queue should be gone');
    const welcome = await p.$eval('#banner', e => e.textContent);
    assert(!/Ready to learn:/.test(welcome));
    assert.strictEqual(await p.$eval('#todoBook', e => e.classList.contains('collapsed')), false);
    assert.strictEqual(await p.$eval('#todoCount', e => e.textContent), '0');
    assert.strictEqual(await p.$eval('#todoPaper', e => e.textContent), 'Nothing here yet.');
    await shot(p, 'todo_desktop_empty.png');

    await openSkill(p, 'bode');
    await p.waitForSelector('#addTodoSkill');
    await p.waitForSelector('#addTodoChallenge');
    await p.$eval('#addTodoSkill', e => e.scrollIntoView({ block: 'center' }));
    await p.click('#addTodoSkill');
    await sleep(200);
    assert.strictEqual(await p.$eval('#addTodoSkill', e => e.disabled), true);
    assert(/Already on your to-do list/.test(await p.$eval('#addTodoSkill', e => e.textContent)));
    await p.$eval('#addTodoChallenge', e => e.scrollIntoView({ block: 'center' }));
    await p.click('#addTodoChallenge');
    await sleep(200);
    assert.strictEqual(await p.$eval('#addTodoChallenge', e => e.disabled), true);

    await p.click('#btnQueue');
    await sleep(200);
    const queueAdd = await p.$$eval('.qrow', rows => rows.map(row => ({
      id: row.dataset.id,
      added: row.querySelector('.todo-add') ? row.querySelector('.todo-add').disabled : null
    })));
    const bodeRow = queueAdd.find(r => r.id === 'bode');
    assert(bodeRow && bodeRow.added === true, 'the open mastery challenge shows as already added');
    await p.keyboard.press('Escape');
    await sleep(150);

    const listed = await p.evaluate(() => window.__skillgrove.todo.list());
    assert.deepStrictEqual(listed, [
      { type: 'skill', id: 'bode' },
      { type: 'challenge', id: 'bode' }
    ]);
    await p.evaluate(() => document.querySelector('#panel .close').click());
    await sleep(200);
    await shot(p, 'todo_desktop_filled.png');

    await p.click('#todoPaper .todo-line[data-type="skill"] .todo-hit');
    await sleep(300);
    assert.strictEqual(await p.$eval('#panelTitle', e => e.textContent.length > 0), true);
    assert.strictEqual(await p.$eval('#panel', e => e.classList.contains('open')), true);
    await p.evaluate(() => document.querySelector('#panel .close').click());
    await sleep(150);
    await p.click('#todoPaper .todo-line[data-type="challenge"] .todo-hit');
    await p.waitForSelector('#quiz.open #qPrompt', { timeout: 10000 });
    assert.strictEqual(await p.$eval('#addTodoQuiz', e => e.disabled), true);
    await p.click('#qLeave');
    await sleep(200);
    const leaveOpen = await p.$('#confirmLeave');
    if (leaveOpen) { await p.click('#confirmLeave'); await sleep(250); }

    await p.click('#todoEdit');
    await sleep(100);
    assert.strictEqual(await p.$eval('#todoEdit', e => e.textContent), 'Done');
    await shot(p, 'todo_desktop_edit.png');
    const grip = await p.$('.todo-line[data-type="skill"] .todo-grip');
    const challenge = await p.$('.todo-line[data-type="challenge"]');
    const gbox = await grip.boundingBox();
    const cbox = await challenge.boundingBox();
    await p.mouse.move(gbox.x + gbox.width / 2, gbox.y + gbox.height / 2);
    await p.mouse.down();
    await p.mouse.move(cbox.x + cbox.width / 2, cbox.y + cbox.height + 6, { steps: 10 });
    await p.mouse.up();
    await sleep(200);
    const moved = await p.evaluate(() => window.__skillgrove.todo.list());
    assert.deepStrictEqual(moved, [
      { type: 'challenge', id: 'bode' },
      { type: 'skill', id: 'bode' }
    ], 'drag moves the skill after the challenge');

    await p.click('.todo-line[data-type="skill"] .todo-remove');
    await sleep(150);
    assert.deepStrictEqual(await p.evaluate(() => window.__skillgrove.todo.list()), [
      { type: 'challenge', id: 'bode' }
    ]);
    await p.click('#todoEdit');

    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(500);
    assert.deepStrictEqual(await p.evaluate(() => window.__skillgrove.todo.list()), [
      { type: 'challenge', id: 'bode' }
    ]);
    const saved = await store(p);
    assert.strictEqual(saved.skills.bode.tier, 1);
    assert.deepStrictEqual(saved.todo, [{ type: 'challenge', id: 'bode' }]);
    await p._ctx.close();
  });

  await test('queue next session appends skills then challenges, skips dupes and coming-soon', async () => {
    const p = await newPage(T({ bode: { tier: 1, lastPracticed: now - DAY, history: [] } }));
    const soonId = await p.$eval('#world .tile.soon', e => e.dataset.id);
    await openSkill(p, soonId);
    await p.$eval('#addTodoSkill', e => e.scrollIntoView({ block: 'center' }));
    await p.click('#addTodoSkill');
    await sleep(150);
    const plan = await p.evaluate(() => {
      const row = window.__skillgrove.plan(false).rows[0];
      const playable = new Set(window.__skillgrove.playableIds());
      const items = [];
      row.practiced.forEach(id => { if (playable.has(id)) items.push({ type: 'skill', id }); });
      row.challenges.forEach(c => { if (playable.has(c.id)) items.push({ type: 'challenge', id: c.id }); });
      return { items, practiced: row.practiced.length, challenges: row.challenges.length };
    });
    assert(plan.practiced > 0, 'the first session should practice ready skills');
    assert(plan.challenges > 0, 'the seeded tier should add a mastery challenge');
    const firstChallenge = plan.items.findIndex(it => it.type === 'challenge');
    const lastSkill = plan.items.map(it => it.type).lastIndexOf('skill');
    assert(lastSkill < firstChallenge, 'new skills come before mastery challenges');
    const anchor = plan.items[0];
    await p.evaluate(item => window.__skillgrove.todo.add(item.type, item.id), anchor);
    await sleep(100);
    await p.click('#todoQueueSession');
    await sleep(250);
    const after = await p.evaluate(() => window.__skillgrove.todo.list());
    const playable = new Set(await p.evaluate(() => window.__skillgrove.playableIds()));
    assert.deepStrictEqual(after[0], { type: 'skill', id: soonId });
    assert.deepStrictEqual(after[1], anchor);
    const appended = after.slice(2);
    assert.deepStrictEqual(appended, plan.items.filter(it => !(it.type === anchor.type && it.id === anchor.id)));
    assert(after.filter(it => it.id === soonId).length === 1, 'a coming-soon skill is not queued again');
    assert(appended.every(it => playable.has(it.id)), 'queued items are playable');
    assert.strictEqual(after.filter(it => it.type === anchor.type && it.id === anchor.id).length, 1);
    await p.click('#todoQueueSession');
    await sleep(200);
    assert.deepStrictEqual(await p.evaluate(() => window.__skillgrove.todo.list()), after, 'a second queue adds nothing new');
    await p._ctx.close();
  });

  await test('old progress without todo or scope still loads, and retired todo ids are cleaned', async () => {
    const old = await newPage(T({ bode: { tier: 2, lastPracticed: now - DAY, history: [] } }));
    assert.deepStrictEqual(await old.evaluate(() => window.__skillgrove.todo.list()), []);
    assert.strictEqual((await store(old)).skills.bode.tier, 2);
    assert.strictEqual(await old.$('#todoQueueSession') !== null, true);
    await old._ctx.close();

    const seed = T({ bode: { tier: 1, lastPracticed: now, history: [] } });
    seed.todo = [
      { type: 'skill', id: 'saturation' },
      { type: 'challenge', id: 'bjt-gain' },
      { type: 'skill', id: 'gone-skill' },
      { type: 'skill', id: 'bode' },
      { type: 'skill', id: 'saturation' }
    ];
    seed.scope = { v: 2, boxes: ['ee105-ch2'] };
    const p = await newPage(seed);
    assert.deepStrictEqual(await p.evaluate(() => window.__skillgrove.todo.list()), [
      { type: 'skill', id: 'square-law' },
      { type: 'challenge', id: 'bjt-action' },
      { type: 'skill', id: 'bode' }
    ]);
    assert.deepStrictEqual(await p.evaluate(() => window.__skillgrove.collections.scope()), ['ee105-ch2']);
    const disk = await store(p);
    assert.strictEqual(disk.skills.saturation, undefined);
    assert.strictEqual(disk.todo.some(it => it.id === 'gone-skill' || it.id === 'saturation'), false);
    await p._ctx.close();
  });

  await test('scope in the progress file restores on load and beats a stale legacy key', async () => {
    const p = await newPage();
    await pickBoxes(p, ['ee105-ch2', 'me132']);
    const stored = await store(p);
    assert.ok(stored.scope && stored.scope.boxes.includes('ee105-ch2') && stored.scope.boxes.includes('me132'));
    assert.strictEqual(stored.scope.boxes.includes('ee105-ucb'), false);
    await p.evaluate(() => localStorage.setItem('skilltree.planscope.v1', JSON.stringify({ v: 2, boxes: ['ee105-ucb'] })));
    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(500);
    const scope = await p.evaluate(() => window.__skillgrove.collections.scope());
    assert.deepStrictEqual(scope, (await store(p)).scope.boxes);
    assert.ok(scope.includes('ee105-ch2') && scope.includes('me132'));
    assert.strictEqual(scope.includes('ee105-ucb'), false);

    await p.evaluate(() => {
      const cur = JSON.parse(localStorage.getItem('skilltree.progress.v1'));
      cur.scope = { v: 2, boxes: ['me132'] };
      cur.savedAt = Date.now();
      localStorage.setItem('skilltree.progress.v1', JSON.stringify(cur));
      localStorage.removeItem('skilltree.planscope.v1');
      window.__skillgrove.reloadProgress();
    });
    await sleep(300);
    assert.deepStrictEqual(await p.evaluate(() => window.__skillgrove.collections.scope()), ['me132']);
    await p._ctx.close();
  });

  await test('to-do notebook collapses on a phone and still edits', async () => {
    const p = await newPage(T({ bode: { tier: 1, lastPracticed: now - DAY, history: [] } }), { viewport: { width: 390, height: 844, isMobile: true, hasTouch: true } });
    assert.strictEqual(await p.$eval('#todoBook', e => e.classList.contains('collapsed')), true);
    await shot(p, 'todo_mobile_collapsed.png');
    await p.click('#todoToggle');
    await sleep(150);
    assert.strictEqual(await p.$eval('#todoBook', e => e.classList.contains('collapsed')), false);
    assert(/Nothing here yet/.test(await p.$eval('#todoPaper', e => e.textContent)));
    await shot(p, 'todo_mobile_empty.png');
    await p.click('#todoQueueSession');
    await sleep(300);
    const n = await p.evaluate(() => window.__skillgrove.todo.list().length);
    assert(n > 1, 'queueing a session fills the notebook');
    await shot(p, 'todo_mobile_filled.png');
    await p.click('#todoEdit');
    await sleep(100);
    assert(await p.$('.todo-remove'));
    await shot(p, 'todo_mobile_edit.png');
    const before = await p.evaluate(() => window.__skillgrove.todo.list().length);
    await p.click('.todo-remove');
    await sleep(150);
    assert.strictEqual(await p.evaluate(() => window.__skillgrove.todo.list().length), before - 1);
    await p._ctx.close();
  });

  await test('unpracticed count excludes coming-soon skills', async () => {
    const p = await newPage(T({ bode: { tier: 1, lastPracticed: now - DAY, history: [] } }));
    const stats = await p.evaluate(() => ({
      unpracticed: document.querySelector('#stats .chip[data-tier="0"] b').textContent,
      soon: document.querySelector('#stats .chip[data-stat="soon"] b').textContent,
      banner: document.getElementById('banner').textContent,
      wide: document.body.innerText.includes('Go wide before deep'),
      waiting: /mastery challenge/i.test(document.getElementById('strip').innerText)
    }));
    assert.strictEqual(stats.unpracticed, String(NPLAY - 1));
    assert.strictEqual(stats.soon, String(NSOON));
    assert.strictEqual(Number(stats.unpracticed) + 1 + Number(stats.soon), NSKILL);
    assert(/Report a bug \/ give feedback for Skillgrove/.test(stats.banner));
    assert.strictEqual(stats.wide, false);
    assert.strictEqual(stats.waiting, false);
    await p._ctx.close();
  });

  await test('settings menu keeps export, import, and the reset confirm', async () => {
    const p = await newPage(T({ bode: { tier: 2, lastPracticed: now - DAY, history: [] } }));
    assert.strictEqual(await p.$eval('#settingsPanel', e => e.hidden), true);
    assert.strictEqual(await p.$('#hrow #btnExport, header > .hrow > #btnExport'), null);
    await p.click('#btnSettings');
    await sleep(100);
    assert.strictEqual(await p.$eval('#settingsPanel', e => e.hidden), false);
    assert.strictEqual(await p.$eval('#btnSettings', e => e.getAttribute('aria-expanded')), 'true');
    for (const id of ['#btnExport', '#btnImport', '#btnReset']) assert(await p.$(id), id);
    await p.click('#btnReset');
    await sleep(150);
    assert(await p.$('#confirmReset'));
    await p.keyboard.press('Escape');
    await sleep(100);
    assert.strictEqual((await store(p)).skills.bode.tier, 2);
    await p.click('#btnSettings');
    await sleep(80);
    await p.click('#btnReset');
    await sleep(150);
    await p.click('#confirmReset');
    await sleep(200);
    const after = await store(p);
    assert.deepStrictEqual(after.skills, {});
    assert.deepStrictEqual(after.todo, []);
    await p._ctx.close();
  });

  async function sendFeedback(p, text, category) {
    await p.click('#btnFeedback');
    await p.waitForSelector('#fbMessage');
    await p.type('#fbMessage', text);
    if (category) await p.select('#fbCategory', category);
    await p.click('#fbSubmit');
    await sleep(300);
  }

  await test('feedback from a guest stores message, category, page, and context', async () => {
    const p = await newPage();
    await openSkill(p, 'half-circuit');
    await sendFeedback(p, 'The half-circuit figure is cramped.', 'bug');
    assert.strictEqual(p._feedbackPosts.length, 1);
    const post = p._feedbackPosts[0];
    const row = JSON.parse(post.body);
    const anon = await p.evaluate(() => window.SKILLTREE_CONFIG.supabase.anonKey);
    assert.strictEqual(post.method, 'POST');
    assert.strictEqual(post.headers.apikey, anon);
    assert.strictEqual(post.headers.authorization, 'Bearer ' + anon);
    assert(/return=minimal/.test(post.headers.prefer));
    assert(!/service_role/i.test(post.body + JSON.stringify(post.headers)));
    assert.strictEqual(row.user_id, null);
    assert.strictEqual(row.message, 'The half-circuit figure is cramped.');
    assert.strictEqual(row.category, 'bug');
    assert.strictEqual(row.app_version, '1.2.0');
    assert(/skilltree/.test(row.page));
    assert.strictEqual(row.page.includes('#'), false);
    assert.strictEqual(row.context.skill_id, 'half-circuit');
    assert(/half circuits/i.test(row.context.skill_name));
    assert(row.context.user_agent);
    assert.strictEqual(await p.$('#fbMessage'), null);
    assert(/feedback was sent/.test(await p.$eval('#toast', e => e.textContent)));
    await p._ctx.close();
  });

  await test('feedback category is optional and a missing table fails gently', async () => {
    const guest = await newPage();
    await sendFeedback(guest, 'Please add a search box.');
    const row = JSON.parse(guest._feedbackPosts[0].body);
    assert.strictEqual(row.category, null);
    assert.strictEqual(row.context.skill_id, null);
    await guest.click('#btnFeedback');
    await guest.waitForSelector('#fbSubmit');
    await guest.click('#fbSubmit');
    await sleep(150);
    assert.strictEqual(guest._feedbackPosts.length, 1);
    assert(/Write a short message/.test(await guest.$eval('#fbError', e => e.textContent)));
    await guest._ctx.close();

    const missing = await newPage(null, { feedbackMode: 'missing' });
    await sendFeedback(missing, 'This should not crash.');
    assert(/isn't set up on the server yet/.test(await missing.$eval('#fbError', e => e.textContent)));
    assert(await missing.$('#fbMessage'));
    const errsBefore = errs.length;
    assert.strictEqual(errs.slice(errsBefore).length, 0);
    await missing._ctx.close();
  });

  await test('signed-in feedback uses that user id and access token', async () => {
    const session = {
      access_token: 'user-access-token',
      user: { id: '11111111-1111-4111-8111-111111111111', email: 'ada@example.com' }
    };
    const p = await newPage(null, { session });
    await sendFeedback(p, 'Signed-in note', 'suggestion');
    const post = p._feedbackPosts[0];
    const row = JSON.parse(post.body);
    const anon = await p.evaluate(() => window.SKILLTREE_CONFIG.supabase.anonKey);
    assert.strictEqual(post.headers.apikey, anon);
    assert.strictEqual(post.headers.authorization, 'Bearer user-access-token');
    assert.strictEqual(row.user_id, session.user.id);
    assert.strictEqual(row.category, 'suggestion');
    await p._ctx.close();
  });

  const UI_DIR = '/opt/cursor/artifacts/skillgrove-ui';
  fs.mkdirSync(UI_DIR, { recursive: true });
  async function shootUi(p, name) {
    await p.evaluate(() => { const t = document.getElementById('toast'); if (t) t.classList.remove('show'); });
    await p.screenshot({ path: path.join(UI_DIR, name) });
  }
  await test('screenshots of the top bar, feedback modal, and settings menu', async () => {
    for (const vp of [
      { name: 'desktop', viewport: { width: 1280, height: 800 } },
      { name: 'mobile', viewport: { width: 390, height: 844, isMobile: true, hasTouch: true } }
    ]) {
      const p = await newPage(null, { viewport: vp.viewport });
      const top = await p.evaluate(() => {
        const strip = document.getElementById('strip').getBoundingClientRect();
        return { x: 0, y: 0, width: Math.ceil(strip.width), height: Math.ceil(strip.bottom) };
      });
      await p.screenshot({ path: path.join(UI_DIR, `topbar-${vp.name}.png`), clip: top });
      await p.click('#btnFeedback');
      await p.waitForSelector('#fbMessage');
      await p.type('#fbMessage', 'The tree is hard to pan on a phone.');
      await shootUi(p, `feedback-${vp.name}.png`);
      await p.keyboard.press('Escape');
      await sleep(150);
      await p.click('#btnSettings');
      await p.waitForSelector('#settingsPanel:not([hidden])');
      await sleep(100);
      await shootUi(p, `settings-${vp.name}.png`);
      await p._ctx.close();
    }
  });

  await browser.close();

  console.log('\n=== Test Results ===\n');
  let passed = 0, failed = 0;
  for (const [status, name] of results) {
    console.log(`${status === 'PASS' ? '✓' : '✗'} ${name}`);
    if (status === 'PASS') passed++;
    else failed++;
  }
  console.log(`\n${passed} passed, ${failed} failed\n`);
  
  process.exit(failed > 0 ? 1 : 0);
})();
