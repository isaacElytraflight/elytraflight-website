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
const NPLAY = Object.keys(BANK).length;
const NSOON = SKJ.length - NPLAY;
const ROOTS = SKJ.filter(s => BANK[s.id] && !s.prereqs.some(q => BANK[q])).map(s => s.id).sort();

let browser, results = [], errs = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));

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

  await test(`initial render: 121 skills x2 views, ${121 - NPLAY} coming soon, ${ROOTS.length} ready`, async () => {
    const p = await newPage();
    const r = await p.evaluate(() => ({
      tree: document.querySelectorAll('#world .tile').length,
      grid: document.querySelectorAll('#gridView .tile').length,
      soon: document.querySelectorAll('#world .tile.soon').length,
      ready: [...document.querySelectorAll('#world .tile.ready')].map(t => t.dataset.id).sort(),
      blobs: document.querySelectorAll('.blob').length,
      courseBlobs: document.querySelectorAll('.blob.course').length,
      chapterBlobs: document.querySelectorAll('.blob.chapter').length,
      paths: document.querySelectorAll('#edges path').length,
      title: document.querySelector('h1').textContent
    }));
    assert.deepStrictEqual([r.tree, r.grid, r.soon, r.blobs, r.paths], [121, 121, NSOON, 19, 180]);
    assert.strictEqual(r.courseBlobs, 1, 'should have 1 course blob');
    assert.strictEqual(r.chapterBlobs, 18, 'should have 18 chapter blobs');
    assert.deepStrictEqual(r.ready, ROOTS);
    assert.strictEqual(r.title, 'Skillgrove');
    await p.screenshot({ path: path.join(SHOTS_DIR, '01_tree_home.png') });
    await p._ctx.close();
  });

  await test('coming-soon skill: badge, panel note, cannot start', async () => {
    const p = await newPage();
    await openSkill(p, 'clm');
    const r = await p.evaluate(() => ({
      start: !!document.getElementById('startBtn'),
      txt: document.getElementById('panel').textContent,
      btns: [...document.querySelectorAll('#panel button')].map(b => b.textContent)
    }));
    assert(/Coming soon/.test(r.txt));
    assert(!r.start);
    assert(!r.btns.some(b => /Start/.test(b)), 'no start button ' + r.btns);
    await p.screenshot({ path: path.join(SHOTS_DIR, '02_panel_coming_soon.png') });
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
    assert.strictEqual(tiles, 121, 'should render all 121 skill tiles');
    
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
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '11_explainer_modal.png') });
    
    await p.keyboard.press('Escape');
    await sleep(200);
    await p._ctx.close();
  });

  await test('skill without explainer has no explainer button', async () => {
    const p = await newPage();
    
    const hasExplainer = await p.evaluate(() => window.__skillgrove.explainers.has('clm'));
    assert(!hasExplainer, 'clm should not have an explainer (coming soon skill)');
    
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
    assert.strictEqual(lightModeCount, 121, 'all tiles should have light-mode class');
    
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
    assert.strictEqual(collections.boxCount, 19, 'should have 19 boxes (1 course + 18 chapters)');
    
    assert(collections.courseBox, 'EE105 course box should exist');
    assert.strictEqual(collections.courseBox.kind, 'course');
    assert.strictEqual(collections.courseBox.title, 'EE 105 (UC Berkeley)');
    assert.strictEqual(collections.courseBox.children.length, 18, 'course should have 18 chapter children');
    
    assert.strictEqual(collections.chapterBoxes.length, 18, 'should have 18 chapter boxes');
    
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
    assert.strictEqual(layout.domChapterBlobs, 18, 'DOM should have 18 chapter blobs');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '14_nested_grouped.png') });
    await p._ctx.close();
  });

  await test('collapse/expand: chapter box can be collapsed and expanded', async () => {
    const p = await newPage();
    
    await p.click('#btnGroup');
    await sleep(700);
    
    const before = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const ch1Blob = sg.layout().grouped.blobs['ee105-ch1'];
      return {
        collapsed: sg.collections.collapsed().has('ee105-ch1'),
        height: ch1Blob?.h || 0,
        hasToggle: !!document.querySelector('.blob[data-box="ee105-ch1"] .toggle')
      };
    });
    
    assert(!before.collapsed, 'chapter should start expanded');
    assert(before.height > 100, 'expanded chapter should have significant height');
    assert(before.hasToggle, 'chapter should have toggle button');
    
    await p.evaluate(() => document.querySelector('.blob[data-box="ee105-ch1"] .toggle').click());
    await sleep(300);
    
    const after = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const ch1Blob = sg.layout().grouped.blobs['ee105-ch1'];
      return {
        collapsed: sg.collections.collapsed().has('ee105-ch1'),
        height: ch1Blob?.h || 0,
        hasCollapsedClass: document.querySelector('.blob[data-box="ee105-ch1"]').classList.contains('collapsed')
      };
    });
    
    assert(after.collapsed, 'chapter should be collapsed after toggle');
    assert(after.height < 100, 'collapsed chapter should have small height');
    assert(after.hasCollapsedClass, 'DOM should have collapsed class');
    
    await p.evaluate(() => document.querySelector('.blob[data-box="ee105-ch1"] .toggle').click());
    await sleep(300);
    
    const restored = await p.evaluate(() => {
      const sg = window.__skillgrove;
      return !sg.collections.collapsed().has('ee105-ch1');
    });
    assert(restored, 'chapter should be expanded after second toggle');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '15_collapse_expand.png') });
    await p._ctx.close();
  });

  await test('box picker: filters skills by selected box', async () => {
    const p = await newPage();
    
    const pickerExists = await p.$('#boxPicker');
    assert(pickerExists, 'box picker should exist');
    
    const options = await p.$$eval('#boxPicker option', opts => opts.map(o => ({ value: o.value, text: o.textContent })));
    assert(options.length > 1, 'picker should have multiple options');
    assert.strictEqual(options[0].value, '', 'first option should be All skills');
    assert(options.some(o => o.value === 'ee105-ucb'), 'picker should have EE105 course option');
    assert(options.some(o => o.value === 'ee105-ch2'), 'picker should have chapter options');
    
    await p.select('#boxPicker', 'ee105-ch2');
    await sleep(200);
    
    const filterResult = await p.evaluate(() => {
      const sg = window.__skillgrove;
      const dimmedTiles = document.querySelectorAll('#world .tile.boxdim').length;
      const visibleTiles = document.querySelectorAll('#world .tile:not(.boxdim)').length;
      const ch2Skills = sg.collections.getBoxSkills('ee105-ch2');
      return {
        filterActive: sg.collections.filter() === 'ee105-ch2',
        dimmedTiles,
        visibleTiles,
        ch2SkillCount: ch2Skills.length
      };
    });
    
    assert(filterResult.filterActive, 'filter should be active');
    assert(filterResult.dimmedTiles > 0, 'some tiles should be dimmed');
    assert.strictEqual(filterResult.visibleTiles, filterResult.ch2SkillCount, 'visible tiles should match ch2 skill count');
    
    await p.select('#boxPicker', '');
    await sleep(200);
    
    const cleared = await p.evaluate(() => {
      return document.querySelectorAll('#world .tile.boxdim').length === 0;
    });
    assert(cleared, 'clearing filter should remove all boxdim classes');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '16_box_picker.png') });
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
      masteredHasShimmer: document.querySelector('.tile[data-id="bode"].t4 .light-dot') !== null
    }));
    
    assert(lightsResult.lightsOn, 'lights mode should be on');
    assert(lightsResult.worldHasClass, 'world should have lights-view class');
    assert.strictEqual(lightsResult.lightModeCount, 121, 'all tiles should have light-mode');
    assert(lightsResult.masteredHasShimmer, 'mastered tile should have light-dot');
    
    await p.screenshot({ path: path.join(SHOTS_DIR, '17_lights_nested.png') });
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
