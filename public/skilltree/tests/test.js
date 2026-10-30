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
  await p.setViewport({ width: 1280, height: 800 });
  p.on('console', m => { if (['error', 'warning'].includes(m.type())) errs.push(m.type() + ': ' + m.text()) });
  p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  if (opts.noStorage) await p.evaluateOnNewDocument(() => { Storage.prototype.setItem = function() { throw new DOMException('denied', 'SecurityError') } });
  
  await p.setRequestInterception(true);
  p.on('request', req => {
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

  await test('collapse toggle hides a box, keeps edges valid, and persists', async () => {
    const p = await newPage();
    
    await p.click('#btnGroup');
    await sleep(700);
    await panTo(p, '.blob[data-box="ee105-ch1"] .toggle');
    
    const before = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const btn = document.querySelector('.blob[data-box="ee105-ch1"] .toggle');
      const chev = btn.querySelector('.chev');
      return {
        collapsed: sg.collections.collapsed().has('ee105-ch1'),
        height: sg.layout().grouped.blobs['ee105-ch1'].h,
        expanded: btn.getAttribute('aria-expanded'),
        label: btn.getAttribute('aria-label'),
        chev: getComputedStyle(chev).transform
      };
    });
    assert(!before.collapsed, 'chapter should start expanded');
    assert(before.height > 100, 'expanded chapter should have significant height');
    assert.strictEqual(before.expanded, 'true');
    assert(/Collapse/.test(before.label));
    assert.strictEqual(before.chev, 'none', 'expanded arrow is not rotated');
    
    await p.click('.blob[data-box="ee105-ch1"] .toggle');
    await sleep(150);
    
    const after = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const blobs = sg.layout().grouped.blobs;
      const chapters = Object.keys(blobs).filter(id => blobs[id].kind === 'chapter').map(id => ({ id, ...blobs[id] }));
      const overlap = chapters.some((a, i) => chapters.some((b, j) => i < j && a.x < b.x + b.w - 1 && b.x < a.x + a.w - 1 && a.y < b.y + b.h - 1 && b.y < a.y + a.h - 1));
      const course = blobs['ee105-ucb'];
      const ch1 = blobs['ee105-ch1'];
      const inside = ch1.x >= course.x - 1 && ch1.y >= course.y - 1 && ch1.x + ch1.w <= course.x + course.w + 1 && ch1.y + ch1.h <= course.y + course.h + 1;
      const skills = sg.collections.getBoxSkills('ee105-ch1');
      const hiddenTiles = skills.filter(id => document.querySelector('#world .tile[data-id="' + id + '"]').classList.contains('collapsed-hide')).length;
      const btn = document.querySelector('.blob[data-box="ee105-ch1"] .toggle');
      const m = new DOMMatrix(getComputedStyle(btn.querySelector('.chev')).transform);
      const paths = [...document.querySelectorAll('#edges path')];
      let visible = 0, hidden = 0, bad = 0;
      paths.forEach(path => {
        const d = path.getAttribute('d') || '';
        if (path.classList.contains('collapsed-hide')) { hidden++; return }
        visible++;
        if (!d || /NaN|Infinity|undefined/.test(d)) bad++;
      });
      return {
        collapsed: sg.collections.collapsed().has('ee105-ch1'),
        height: ch1.h,
        hasClass: document.querySelector('.blob[data-box="ee105-ch1"]').classList.contains('collapsed'),
        expanded: btn.getAttribute('aria-expanded'),
        rotated: Math.abs(m.b + 1) < 0.05 && Math.abs(m.c - 1) < 0.05,
        hiddenTiles, skillCount: skills.length,
        overlap, inside, visible, hidden, bad, edges: paths.length,
        stored: localStorage.getItem('skilltree.collapsed.v1')
      };
    });
    assert(after.collapsed, 'chapter should be collapsed after a real click');
    assert(after.height < 100, 'collapsed chapter should shrink to its header');
    assert(after.hasClass, 'collapsed class should be set');
    assert.strictEqual(after.expanded, 'false');
    assert(after.rotated, 'arrow should rotate to point right');
    assert.strictEqual(after.hiddenTiles, after.skillCount, 'skills inside the chapter should be hidden');
    assert(!after.overlap, 'chapter boxes should not overlap');
    assert(after.inside, 'collapsed chapter should stay inside its course');
    assert.strictEqual(after.bad, 0, 'visible edges should have finite paths');
    assert(after.hidden > 0, 'edges into the collapsed chapter should be hidden');
    assert(after.visible > 0, 'edges between the other chapters should remain');
    assert.strictEqual(after.visible + after.hidden, after.edges);
    assert(/ee105-ch1/.test(after.stored), 'collapsed ids should be stored locally');
    
    await p.reload({ waitUntil: 'networkidle0' });
    await sleep(500);
    const kept = await p.evaluate(() => ({
      pressed: document.querySelector('#btnGroup').getAttribute('aria-pressed'),
      collapsed: window.__skillgrove.collections.collapsed().has('ee105-ch1'),
      expanded: document.querySelector('.blob[data-box="ee105-ch1"] .toggle').getAttribute('aria-expanded')
    }));
    assert.strictEqual(kept.pressed, 'true', 'grouped view should still be on');
    assert(kept.collapsed, 'collapsed chapter should survive reload');
    assert.strictEqual(kept.expanded, 'false');
    
    await p.focus('.blob[data-box="ee105-ch1"] .toggle');
    await p.keyboard.press('Enter');
    await sleep(150);
    const restored = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const shown = sg.collections.getBoxSkills('ee105-ch1').filter(id => !document.querySelector('#world .tile[data-id="' + id + '"]').classList.contains('collapsed-hide')).length;
      return {
        collapsed: sg.collections.collapsed().has('ee105-ch1'),
        expanded: document.querySelector('.blob[data-box="ee105-ch1"] .toggle').getAttribute('aria-expanded'),
        shown
      };
    });
    assert(!restored.collapsed, 'Enter should expand the chapter');
    assert.strictEqual(restored.expanded, 'true');
    assert.strictEqual(restored.shown, (await p.evaluate(() => window.__skillgrove.collections.getBoxSkills('ee105-ch1').length)));
    
    await p.select('#scopePicker', 'ee105-ucb');
    await panTo(p, '.blob.course[data-box="ee105-ucb"] .toggle');
    await p.click('.blob.course[data-box="ee105-ucb"] .toggle');
    await sleep(150);
    const course = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const blob = sg.layout().grouped.blobs['ee105-ucb'];
      const paths = [...document.querySelectorAll('#edges path')];
      const bad = paths.filter(path => !path.classList.contains('collapsed-hide') && /NaN|Infinity|undefined/.test(path.getAttribute('d') || '')).length;
      const visible = paths.filter(path => !path.classList.contains('collapsed-hide')).length;
      return {
        height: blob.h,
        chapters: document.querySelectorAll('.blob.chapter').length,
        hiddenTiles: document.querySelectorAll('#world .tile.collapsed-hide').length,
        tileCount: document.querySelectorAll('#world .tile').length,
        skillCount: sg.collections.getBoxDescendantSkills('ee105-ucb').length,
        expanded: document.querySelector('.blob.course .toggle').getAttribute('aria-expanded'),
        bad, visible
      };
    });
    assert(course.height < 100, 'collapsed course should shrink to its header');
    assert.strictEqual(course.chapters, 0, 'chapter boxes should be removed while the course is collapsed');
    assert.strictEqual(course.hiddenTiles, course.skillCount, 'every EE 105 skill tile should be hidden with the course');
    assert.strictEqual(course.tileCount, course.skillCount, 'the EE 105 scope lays out only that course');
    assert.strictEqual(course.expanded, 'false');
    assert.strictEqual(course.bad, 0);
    assert.strictEqual(course.visible, 0, 'no edge should be left dangling from hidden skills');
    await panTo(p, '.blob.course[data-box="ee105-ucb"]');
    await p.screenshot({ path: path.join(SHOTS_DIR, '15_collapsed_box.png') });
    
    await p.click('.blob.course[data-box="ee105-ucb"] .toggle');
    await sleep(150);
    const back = await p.evaluate(() => document.querySelectorAll('.blob.chapter').length);
    assert.strictEqual(back, 18, 'expanding the course should restore its chapters');
    await p._ctx.close();
  });

  await test('scope selector filters the tree and the learning plan', async () => {
    const p = await newPage();

    const controls = await p.evaluate(() => ({
      selects: [...document.querySelectorAll('#hctl select')].map(e => e.id),
      oldChapter: !!document.getElementById('chSel'),
      oldBox: !!document.getElementById('boxPicker'),
      oldPlan: !!document.getElementById('planScopePicker')
    }));
    assert.deepStrictEqual(controls.selects, ['scopePicker']);
    assert.strictEqual(controls.oldChapter, false, 'the old chapter filter should be gone');
    assert.strictEqual(controls.oldBox, false, 'the old box filter should be gone');
    assert.strictEqual(controls.oldPlan, false);

    const options = await p.$$eval('#scopePicker option', opts => opts.map(o => ({ value: o.value, text: o.textContent })));
    assert.strictEqual(options[0].value, '', 'first option should be Everything');
    assert.strictEqual(options[0].text, 'Everything');
    const courseAt = options.findIndex(o => o.value === 'ee105-ucb');
    const ch1At = options.findIndex(o => o.value === 'ee105-ch1');
    const ch2At = options.findIndex(o => o.value === 'ee105-ch2');
    assert(courseAt > 0, 'picker should list the course from collections');
    assert(ch1At > courseAt && ch2At > ch1At, 'chapters should be nested under their course');
    assert(/Ch 2:/.test(options[ch2At].text), options[ch2At].text);

    await p.click('#btnPlan');
    await sleep(400);
    const allSkillsSessions = await p.$eval('#planSessions', e => parseInt(e.textContent, 10));
    assert(allSkillsSessions > 0, 'all skills should have sessions');
    assert.strictEqual(await p.$('#planScopePicker'), null, 'the plan should not grow a second scope selector');
    assert.strictEqual(await p.$$eval('#modal select', els => els.length), 0);
    await p.keyboard.press('Escape');
    await sleep(200);

    await p.select('#scopePicker', 'ee105-ch2');
    await sleep(200);
    const filterResult = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const dimmedTiles = document.querySelectorAll('#world .tile.boxdim').length;
      const visibleTiles = document.querySelectorAll('#world .tile:not(.boxdim)').length;
      const ch2Skills = sg.collections.getBoxDescendantSkills('ee105-ch2');
      return {
        filterActive: sg.collections.filter() === 'ee105-ch2',
        planScope: sg.collections.scope(),
        stored: localStorage.getItem('skilltree.planscope.v1'),
        dimmedTiles,
        visibleTiles,
        ch2SkillCount: ch2Skills.length
      };
    });
    assert(filterResult.filterActive, 'tree filter should follow the scope');
    assert.strictEqual(filterResult.planScope, 'ee105-ch2', 'plan scope should follow the same selection');
    assert.strictEqual(filterResult.stored, 'ee105-ch2');
    assert(filterResult.dimmedTiles > 0, 'skills outside the chapter should be dimmed');
    assert.strictEqual(filterResult.visibleTiles, filterResult.ch2SkillCount, 'visible tiles should match the chapter');

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
      value: document.getElementById('scopePicker').value,
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      scope: window.__skillgrove.collections.scope()
    }));
    assert.strictEqual(kept.value, 'ee105-ch2', 'scope should survive reload');
    assert.strictEqual(kept.scope, 'ee105-ch2');
    assert(kept.dimmed > 0, 'tree should still be filtered after reload');

    await p.select('#scopePicker', 'ee105-ucb');
    await sleep(150);
    const course = await p.evaluate(() => ({
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      scope: window.__skillgrove.collections.scope()
    }));
    assert.strictEqual(course.scope, 'ee105-ucb');
    assert.strictEqual(course.dimmed, 0, 'every skill in the EE 105 scope stays visible');

    await p.select('#scopePicker', '');
    await sleep(150);
    const cleared = await p.evaluate(() => ({
      dimmed: document.querySelectorAll('#world .tile.boxdim').length,
      stored: localStorage.getItem('skilltree.planscope.v1'),
      scope: window.__skillgrove.collections.scope()
    }));
    assert.strictEqual(cleared.dimmed, 0, 'clearing scope should show every skill');
    assert.strictEqual(cleared.stored, null);
    assert.strictEqual(cleared.scope, null);
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
      await p.select('#scopePicker', 'ee105-ch2');
      await sleep(200);
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
    const options = await p.$$eval('#scopePicker option', opts => opts.map(o => ({ value: o.value, text: o.textContent })));
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
    assert(result.meExtras.includes('gbw'), 'a playable prerequisite outside ME 132 stays in the plan: ' + result.meExtras.join(','));

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
      return {
        boxes: tiles.map(t => t.dataset.box).sort(),
        tiers: tiles.map(t => t.classList.contains('t4')),
        records: Object.keys(stored).filter(id => id === 'bode').length
      };
    });
    assert.deepStrictEqual(shared.boxes, ['am08/ch8', 'ee105-ch2', 'me132/m3']);
    assert(shared.tiers.every(Boolean), 'every bode placement shows the same mastered tier');
    assert.strictEqual(shared.records, 1);
    await p._ctx.close();
  });

  await test('ME 132 and Feedback Systems scopes render for review', async () => {
    const p = await newPage();
    await p.setViewport({ width: 1440, height: 900 });
    const shoot = async (scope, file) => {
      await p.select('#scopePicker', scope);
      await sleep(300);
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
        window.__skillgrove.lights.setScale(Math.max(s, 0.4));
        const world = document.getElementById('world');
        const m = /scale\(([^)]+)\)/.exec(world.style.transform);
        const scale = m ? parseFloat(m[1]) : s;
        world.style.transform = `translate(${x}px,${y}px) scale(${scale})`;
      });
      await sleep(250);
      const view = await p.evaluate(scope => {
        const sg = window.__skillgrove;
        const tiles = [...document.querySelectorAll('#world .tile')];
        const soon = tiles.filter(t => t.classList.contains('soon')).length;
        return {
          scope: sg.collections.scope(),
          title: (sg.collections.boxById()[scope] || {}).title,
          course: document.querySelectorAll('.blob.course.on').length,
          textbook: document.querySelectorAll('.blob.textbook.on').length,
          chapters: document.querySelectorAll('.blob.chapter.on').length,
          tiles: tiles.length,
          soon,
          dimmed: document.querySelectorAll('#world .tile.boxdim').length,
          memberCount: sg.collections.getBoxDescendantSkills(scope).length
        };
      }, scope);
      assert.strictEqual(view.scope, scope);
      assert.strictEqual(view.dimmed, 0, scope + ' should show its own skills without dimming them');
      assert.strictEqual(view.tiles, view.memberCount, scope + ' tile count');
      if (scope === 'me132') {
        assert.strictEqual(view.title, 'ME 132 (UC Berkeley)');
        assert.strictEqual(view.course, 1);
        assert.strictEqual(view.textbook, 0);
        assert.strictEqual(view.chapters, 9);
      } else {
        assert.strictEqual(view.title, 'Feedback Systems');
        assert.strictEqual(view.course, 0);
        assert.strictEqual(view.textbook, 1);
        assert.strictEqual(view.chapters, 13);
      }
      assert(view.soon > 0, scope + ' should show coming-soon skills');
      await p.screenshot({ path: path.join(SHOTS_DIR, file), fullPage: false });
    };
    await shoot('me132', '20_me132_scope.png');
    await shoot('am08', '21_feedback_systems_scope.png');
    await p._ctx.close();
  });

  await test('grouped box headers do not overlap in any scope', async () => {
    const p = await newPage();
    await p.setViewport({ width: 1440, height: 900 });
    await p.click('#btnGroup');
    await sleep(800);

    const overlaps = () => p.evaluate(() => {
      const hits = [];
      const heads = [...document.querySelectorAll('#world .blob.on .hd')].map(hd => {
        const blob = hd.closest('.blob');
        const r = hd.getBoundingClientRect();
        const b = blob.getBoundingClientRect();
        const title = hd.querySelector('.btitle');
        const counter = hd.querySelector('.ct');
        if (r.top < b.top - 1 || r.left < b.left - 1 || r.bottom > b.bottom + 1 || r.right > b.right + 1) {
          hits.push(blob.dataset.box + ' header spills out of its box');
        }
        if (title && counter) {
          const a = title.getBoundingClientRect();
          const c = counter.getBoundingClientRect();
          if (a.right > c.left + 1 && c.right > a.left + 1 && a.bottom > c.top + 1 && c.bottom > a.top + 1) {
            hits.push(blob.dataset.box + ' title overlaps its counter');
          }
        }
        return { id: blob.dataset.box, r };
      });
      for (let i = 0; i < heads.length; i++) {
        for (let j = i + 1; j < heads.length; j++) {
          const a = heads[i].r, c = heads[j].r;
          if (a.right > c.left + 1 && c.right > a.left + 1 && a.bottom > c.top + 1 && c.bottom > a.top + 1) {
            hits.push(heads[i].id + ' ∩ ' + heads[j].id);
          }
        }
      }
      return hits;
    });

    const setCollapsed = async ids => {
      await p.evaluate(want => {
        const sg = window.__skillgrove;
        const have = new Set(sg.collections.collapsed());
        [...have].forEach(id => { if (!want.includes(id)) sg.collections.toggleCollapse(id); });
        want.forEach(id => { if (!sg.collections.collapsed().has(id)) sg.collections.toggleCollapse(id); });
      }, ids);
      await sleep(80);
    };

    const cases = [
      { scope: '', label: 'Everything', chapters: ['ee105-ch10', 'me132/m3', 'am08/ch99'], outer: 'me132' },
      { scope: 'ee105-ucb', label: 'EE 105', chapters: ['ee105-ch10'], outer: 'ee105-ucb' },
      { scope: 'me132', label: 'ME 132', chapters: ['me132/m1', 'me132/m3'], outer: 'me132' },
      { scope: 'am08', label: 'Feedback Systems', chapters: ['am08/ch9', 'am08/ch99'], outer: 'am08' }
    ];
    for (const c of cases) {
      await p.select('#scopePicker', c.scope);
      await sleep(250);
      await setCollapsed([]);
      assert.deepStrictEqual(await overlaps(), [], c.label + ' expanded');
      await setCollapsed(c.chapters);
      assert.deepStrictEqual(await overlaps(), [], c.label + ' with chapters collapsed');
      await setCollapsed([c.outer]);
      assert.deepStrictEqual(await overlaps(), [], c.label + ' with the outer box collapsed');
      await setCollapsed([]);
    }

    await p.select('#scopePicker', 'me132');
    await sleep(250);
    await panTo(p, '.blob[data-box="me132/m1"] .hd');
    await p.screenshot({ path: path.join(SHOTS_DIR, '22_me132_header.png') });
    await p._ctx.close();
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
