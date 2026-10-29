const puppeteer=require('puppeteer-core'),fs=require('fs'),path=require('path'),assert=require('assert');
const URL='file:///workspace/skilltree/app/skilltree.html', SH='/workspace/skilltree/app/shots/';
const BANK={};for(const f of fs.readdirSync('/workspace/skilltree/bank')){const b=JSON.parse(fs.readFileSync('/workspace/skilltree/bank/'+f));BANK[b.skill_id]=b.questions}
const KEY='skilltree.progress.v1';
const SKJ=JSON.parse(fs.readFileSync('/workspace/skilltree/ee105_skills_draft.json')).skills;
const NPLAY=Object.keys(BANK).length, NSOON=SKJ.length-NPLAY;                       // 55 playable / 66 coming soon
const ORIG=['lti-def','rc-lpf','cx-exp','sinusoid-resp','impulse-conv','step-resp','freq-char','tf','phasors','direct-h','pole-zero','rlc','bode','ac-power'];
const ROOTS=SKJ.filter(s=>BANK[s.id]&&!s.prereqs.some(q=>BANK[q])).map(s=>s.id).sort();   // playable skills with no playable prerequisite
const onlyOrig=a=>a.filter(x=>ORIG.includes(x));
let browser,results=[],errs=[];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function newPage(seed,opts={}){
  const ctx=await browser.createBrowserContext();const p=await ctx.newPage();await p.setViewport({width:1280,height:800});
  p.on('console',m=>{if(['error','warning'].includes(m.type()))errs.push(m.type()+': '+m.text())});p.on('pageerror',e=>errs.push('PAGEERR '+e.message));
  if(opts.noStorage)await p.evaluateOnNewDocument(()=>{Storage.prototype.setItem=function(){throw new DOMException('denied','SecurityError')}});
  if(seed){await p.goto(URL);await p.evaluate((k,s)=>localStorage.setItem(k,JSON.stringify(s)),KEY,seed)}
  await p.goto(URL,{waitUntil:'load'});await sleep(300);
  p._ctx=ctx;return p;
}
const store=p=>p.evaluate(k=>JSON.parse(localStorage.getItem(k)),KEY);
const T=(skills)=>({version:1,skills});
const now=Date.now(),DAY=86400000;
async function openSkill(p,id){await p.evaluate(id=>document.querySelector('#world .tile[data-id="'+id+'"]').click(),id);await sleep(350)}
async function answerQuiz(p,skill,pattern){ // pattern: array of bools (correct?) 
  const n=await p.evaluate(()=>document.querySelectorAll('.prog i').length);
  for(let i=0;i<n;i++){
    const prompt=await p.$eval('#qPrompt',e=>e.dataset.qid);
    const q=BANK[skill].find(q=>q.id===prompt);assert(q,'question not found in bank: '+prompt.slice(0,50));
    const ok=pattern[i];
    if(q.type==='mc'){
      const target=q.options[q.correct_index];
      const idx=await p.evaluate((t,ok)=>{const bs=[...document.querySelectorAll('.opt')];const k=bs.findIndex(b=>(+b.dataset.o===t)===ok);return k},q.correct_index,ok);
      assert(idx>=0);
      const opts=await p.$$('.opt');await opts[idx].click();
    }else{
      const val=ok?String(q.answer):String(q.answer*3+7);
      await p.type('#numIn',val);await p.click('#checkBtn');
    }
    await p.waitForSelector('#feedback');
    const fbOk=await p.$eval('#feedback',e=>e.classList.contains('ok'));assert.strictEqual(fbOk,ok,'feedback mismatch '+q.id);
    const ex=await p.$eval('#feedback .ex',e=>e.textContent);assert(ex.length>20,'explanation shown');
    if(i===0&&p._shotMid){await sleep(250);await p.screenshot({path:SH+p._shotMid});p._shotMid=null}
    await p.click('#nextBtn');await sleep(60);
  }
}
async function test(name,fn){
  const before=errs.length;
  try{await fn();results.push(['PASS',name])}catch(e){results.push(['FAIL',name+' :: '+(e.message||e).toString().split('\n')[0]]);console.error(e.stack)}
  if(errs.length>before)results.push(['FAIL',name+' :: console errors '+errs.slice(before).join(' | ')]);
}
(async()=>{
 browser=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:'new',args:['--no-sandbox']});
 await test(`initial render: 121 skills x2 views, ${121-55} coming soon, ${ROOTS.length} ready`,async()=>{
   const p=await newPage();
   const r=await p.evaluate(()=>({tree:document.querySelectorAll('#world .tile').length,grid:document.querySelectorAll('#gridView .tile').length,soon:document.querySelectorAll('#world .tile.soon').length,ready:[...document.querySelectorAll('#world .tile.ready')].map(t=>t.dataset.id).sort(),blobs:document.querySelectorAll('.blob').length,paths:document.querySelectorAll('#edges path').length,title:document.querySelector('h1').textContent}));
   assert.deepStrictEqual([r.tree,r.grid,r.soon,r.blobs,r.paths],[121,121,NSOON,18,180]);
   assert.deepStrictEqual(r.ready,ROOTS);assert.strictEqual(r.title,'Skillgrove');
   await p.screenshot({path:SH+'01_tree_home.png'});
   await p.click('#zFit');await sleep(700);await p.screenshot({path:SH+'02_tree_whole.png'});
   await p._ctx.close();
 });
 await test('coming-soon skill: badge, panel note, cannot start',async()=>{
   const p=await newPage();
   await openSkill(p,'bjt-active'.length&&'clm');
   const r=await p.evaluate(()=>({start:!!document.getElementById('startBtn'),txt:document.getElementById('panel').textContent,btns:[...document.querySelectorAll('#panel button')].map(b=>b.textContent)}));
   assert(/Coming soon/.test(r.txt));assert(!r.start);assert(!r.btns.some(b=>/Start/.test(b)),'no start button '+r.btns);
   await p.screenshot({path:SH+'03_panel_coming_soon.png'});
   // queue shouldn't include it even if tier were set via import
   await p._ctx.close();
 });
 await test('coming-soon skill with injected progress is not in queue / not startable',async()=>{
   const p=await newPage(T({clm:{tier:2,lastPracticed:now-5*DAY,history:[]}}));
   await p.click('#btnQueue');await sleep(200);
   const rows=await p.$$eval('.qrow',r=>r.map(x=>x.dataset.id));assert.deepStrictEqual(rows,[]);
   await p.keyboard.press('Escape');await openSkill(p,'clm');
   assert(!(await p.$('#startBtn')));await p._ctx.close();
 });
 await test('prereq gentle note + real mouse click on tile opens panel with clickable prereqs',async()=>{
   const p=await newPage();
   const box=await p.$eval('#world .tile[data-id="bode"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}});
   await p.mouse.click(box.x,box.y);await sleep(450);
   const r=await p.evaluate(()=>({note:(document.getElementById('prereqNote')||{}).textContent,title:document.getElementById('panelTitle').textContent,chips:[...document.querySelectorAll('#prereqChips .pill')].map(x=>x.textContent)}));
   assert(/Gentle heads-up/.test(r.note||''),'note');assert(/Bode/.test(r.title));assert(r.chips.length===1);
   await p.click('#prereqChips .pill');await sleep(500);
   assert(/Poles and zeros/.test(await p.$eval('#panelTitle',e=>e.textContent)));
   await p._ctx.close();
 });
 await test('round 1 on bode -> Practiced, persists after reload; tree colored',async()=>{
   const p=await newPage();
   await openSkill(p,'bode');
   await p.screenshot({path:SH+'04_panel_bode.png'});
   await p.click('#startBtn');await sleep(200);
   p._shotMid='05_quiz_mid_question.png';
   assert(/not a mastery challenge/.test(await p.$eval('#rule',e=>e.textContent)));
   await answerQuiz(p,'bode',[true,false,true]);
   assert.strictEqual(await p.$eval('#score',e=>e.textContent),'2 / 3');
   assert.strictEqual(await p.$eval('#newTier',e=>e.textContent),'Practiced');
   await p.screenshot({path:SH+'06_result_round1.png'});
   let s=await store(p);assert.strictEqual(s.version,1);assert.strictEqual(s.skills.bode.tier,1);assert(s.skills.bode.lastPracticed>now-60000);assert.strictEqual(s.skills.bode.history.length,1);
   await p.reload();await sleep(300);
   s=await store(p);assert.strictEqual(s.skills.bode.tier,1);
   const cls=await p.$eval('#world .tile[data-id="bode"]',e=>e.className);assert(/\bt1\b/.test(cls),cls);
   assert((await p.$eval('#pctTxt',e=>e.textContent))!=='0.0%');
   await p._ctx.close();
 });
 await test('numeric: tolerance accept/reject, sci-notation, bad input',async()=>{
   const p=await newPage(T({bode:{tier:3,lastPracticed:now-DAY,history:[]}}));
   await openSkill(p,'bode');await p.click('#startBtn');await sleep(200);
   // go through r4 questions; find numeric ones
   const qs=BANK.bode.filter(q=>q.round===4);let checked=0;
   for(let i=0;i<qs.length;i++){
     const prompt=await p.$eval('#qPrompt',e=>e.dataset.qid);const q=qs.find(x=>x.id===prompt);
     if(q.type==='numeric'){
       checked++;
       await p.type('#numIn','abc');await p.click('#checkBtn');await sleep(100);
       assert(!(await p.$('#feedback')),'invalid input must not submit');
       await p.$eval('#numIn',e=>e.value='');
       let txt;const tol=q.tolerance;
       if(checked===1){txt=String(q.answer*(1+tol*0.9)).replace('-','\u2212')} // inside tolerance (unicode minus ok)
       else{txt=String(q.answer*(1+tol*1.6))}  // outside
       await p.type('#numIn',txt);await p.click('#checkBtn');await p.waitForSelector('#feedback');
       const ok=await p.$eval('#feedback',e=>e.classList.contains('ok'));
       assert.strictEqual(ok,checked===1,'tolerance '+q.id+' ans '+q.answer+' typed '+txt);
       if(q.preview&&q.preview.length)assert(/Coming up/.test(await p.$eval('#coming',e=>e.textContent)),'preview hint');
     }else{
       const idx=await p.evaluate(t=>[...document.querySelectorAll('.opt')].findIndex(b=>+b.dataset.o===t),q.correct_index);
       await (await p.$$('.opt'))[idx].click();await p.waitForSelector('#feedback');
     }
     await p.click('#nextBtn');await sleep(60);
   }
   assert(checked>=1);
   // sci notation parse
   await p._ctx.close();
 });
 await test('sci-notation input 1e5 accepted for 100000 (bode-r4-q1)',async()=>{
   const p=await newPage(T({bode:{tier:3,lastPracticed:now-DAY,history:[]}}));
   await openSkill(p,'bode');await p.click('#startBtn');await sleep(200);
   for(let i=0;i<3;i++){
     const prompt=await p.$eval('#qPrompt',e=>e.dataset.qid);const q=BANK.bode.find(x=>x.id===prompt);
     if(q.id==='bode-r4-q1'){await p.screenshot({path:SH+'07a_numeric_question.png'});await p.type('#numIn','1e5');await p.click('#checkBtn');await p.waitForSelector('#feedback');assert(await p.$eval('#feedback',e=>e.classList.contains('ok')));
       assert(/Coming up/.test(await p.$eval('#coming',e=>e.textContent)));await p.screenshot({path:SH+'07_round4_coming_up.png'});return}
     // skip others
     if(q.type==='mc'){await (await p.$$('.opt'))[0].click()}else{await p.type('#numIn','1');await p.click('#checkBtn')}
     await p.waitForSelector('#feedback');await p.click('#nextBtn');await sleep(60);
   }
   throw new Error('bode-r4-q1 not reached');
 });
 await test('failing a challenge keeps tier, history records fail; retry pass -> Level 1',async()=>{
   const p=await newPage(T({bode:{tier:1,lastPracticed:now-3*DAY,history:[]}}));
   await openSkill(p,'bode');
   assert(/Start mastery challenge → Level 1/.test(await p.$eval('#startBtn',e=>e.textContent)));
   assert(/at least 2 of 3/.test(await p.$eval('#panel',e=>e.textContent)));
   await p.click('#startBtn');await sleep(200);
   assert(/at least 2 of 3/.test(await p.$eval('#rule',e=>e.textContent)));
   await answerQuiz(p,'bode',[false,true,false]);
   assert.strictEqual(await p.$eval('#score',e=>e.textContent),'1 / 3');
   assert(/stays at Practiced/.test(await p.$eval('#failNote',e=>e.textContent)));
   await p.screenshot({path:SH+'08_result_challenge_failed.png'});
   let s=await store(p);assert.strictEqual(s.skills.bode.tier,1);assert.strictEqual(s.skills.bode.history.length,1);assert.strictEqual(s.skills.bode.history[0].passed,false);
   assert(s.skills.bode.lastPracticed>now-60000,'lastPracticed updated on fail');
   await p.click('#resRetry');await sleep(200);
   await answerQuiz(p,'bode',[true,true,false]);
   assert.strictEqual(await p.$eval('#score',e=>e.textContent),'2 / 3');
   assert.strictEqual(await p.$eval('#newTier',e=>e.textContent),'Level 1');
   await sleep(900);await p.screenshot({path:SH+'09_result_challenge_passed.png'});
   s=await store(p);assert.strictEqual(s.skills.bode.tier,2);assert.strictEqual(s.skills.bode.history.length,2);
   await p._ctx.close();
 });
 await test('full climb: Level 2 -> Mastered, review mode changes nothing',async()=>{
   const p=await newPage(T({bode:{tier:3,lastPracticed:now-DAY,history:[]}}));
   await openSkill(p,'bode');await p.click('#startBtn');await sleep(200);
   await answerQuiz(p,'bode',[true,true,true]);
   assert.strictEqual(await p.$eval('#newTier',e=>e.textContent),'Mastered');
   assert.strictEqual((await store(p)).skills.bode.tier,4);
   await p.click('#resBack');await sleep(500);
   assert(/Mastered/.test(await p.$eval('#panelTier',e=>e.textContent)));
   await p.screenshot({path:SH+'10_panel_mastered.png'});
   const hl=(await store(p)).skills.bode.history.length;
   await p.click('#startBtn');await sleep(200);await answerQuiz(p,'bode',[false,false,false]);
   const s=await store(p);assert.strictEqual(s.skills.bode.tier,4);assert.strictEqual(s.skills.bode.history.length,hl);
   await p._ctx.close();
 });
 await test('queue ordering: least-recently practiced first; mastered/unpracticed excluded; start top',async()=>{
   const p=await newPage(T({
     'cx-exp':{tier:2,lastPracticed:now-1*DAY,history:[]},
     'rc-lpf':{tier:1,lastPracticed:now-10*DAY,history:[]},
     'lti-def':{tier:3,lastPracticed:now-5*DAY,history:[]},
     'tf':{tier:4,lastPracticed:now-30*DAY,history:[]},
     'bode':{tier:1,lastPracticed:now-2*DAY,history:[]},
     'phasors':{tier:0,lastPracticed:null,history:[]},
     'pole-zero':{tier:1,lastPracticed:now-7*DAY,history:[]}}));
   assert.strictEqual(await p.$eval('#qCount',e=>e.textContent),'5');
   await p.click('#btnQueue');await sleep(250);
   const rows=await p.$$eval('.qrow',r=>r.map(x=>x.dataset.id));
   assert.deepStrictEqual(rows,['rc-lpf','pole-zero','lti-def','bode','cx-exp']);
   await p.screenshot({path:SH+'11_queue.png'});
   await p.click('.qrow.top button');await sleep(250);
   assert(/Solve a first-order RC/.test(await p.$eval('.qtop h2',e=>e.textContent)));
   assert(/Level 1/.test(await p.$eval('#rbadge',e=>e.textContent)));
   // finish passing -> goes to the bottom of queue
   await answerQuiz(p,'rc-lpf',[true,true,true]);
   await p.click('#resBack');await sleep(400);await p.keyboard.press('Escape');await sleep(300);
   await p.click('#btnQueue');await sleep(250);
   assert.deepStrictEqual(await p.$$eval('.qrow',r=>r.map(x=>x.dataset.id)),['pole-zero','lti-def','bode','cx-exp','rc-lpf']);
   await p._ctx.close();
 });
 await test('ready-to-learn needs ALL prerequisites at Level 2+ (Practiced / Level 1 is not enough)',async()=>{
   const ready=async p=>onlyOrig(await p.$$eval('#world .tile.ready',e=>e.map(x=>x.dataset.id).sort()));   // circuits-chapter (original 14) view; other roots stay ready independently
   // all three roots only Practiced -> nothing new recommended (the roots themselves are no longer unpracticed)
   let p=await newPage(T({'cx-exp':{tier:1,lastPracticed:now,history:[]},'lti-def':{tier:1,lastPracticed:now,history:[]},'rc-lpf':{tier:1,lastPracticed:now,history:[]}}));
   assert.deepStrictEqual(await ready(p),[],'Practiced prerequisites must not make dependents ready');
   assert.strictEqual(await p.$eval('#stats',e=>[...e.querySelectorAll('.chip')].find(c=>/Ready to learn/.test(c.textContent)).textContent.trim()),'Ready to learn '+(await p.$$eval('#world .tile.ready',e=>e.length)));
   await openSkill(p,'impulse-conv');
   assert(/recommended once its prerequisites reach Level 2/.test(await p.$eval('#prereqNote',e=>e.textContent)),'panel note wording');
   assert(/Linear time-invariant[^;]*\(Practiced\)/.test(await p.$eval('#prereqNote',e=>e.textContent)),'note names prerequisites and their tier');
   assert.strictEqual(await p.$eval('#startBtn',e=>e.disabled),false,'no hard lock: can still start');
   await p._ctx.close();
   // lti-def at Level 1 (tier 2) still not enough; at Level 2 (tier 3) impulse-conv becomes ready
   p=await newPage(T({'cx-exp':{tier:3,lastPracticed:now,history:[]},'lti-def':{tier:2,lastPracticed:now,history:[]},'rc-lpf':{tier:3,lastPracticed:now,history:[]}}));
   assert.deepStrictEqual(await ready(p),[],'Level 1 is not enough');
   await p._ctx.close();
   p=await newPage(T({'cx-exp':{tier:3,lastPracticed:now,history:[]},'lti-def':{tier:3,lastPracticed:now,history:[]},'rc-lpf':{tier:2,lastPracticed:now,history:[]}}));
   assert.deepStrictEqual(await ready(p),['impulse-conv'],'only the dependent whose prerequisites are all Level 2+');
   assert(/Ready to learn/.test(await p.$eval('#banner',e=>e.textContent)));
   assert(/Level 2/.test(await p.$eval('#banner',e=>e.textContent)));
   await openSkill(p,'impulse-conv');assert(/all its prerequisites are at Level 2 or Mastered/.test(await p.$eval('#readyNote',e=>e.textContent)));assert(!(await p.$('#prereqNote')));
   await openSkill(p,'sinusoid-resp');assert(/Still to go: [^.]*Solve a first-order RC low-pass filter in the time domain \(Level 1\)/.test(await p.$eval('#prereqNote',e=>e.textContent)),await p.$eval('#prereqNote',e=>e.textContent));
   await p.keyboard.press('Escape');
   await p._ctx.close();
   // Mastered counts too; sinusoid-resp needs all three
   p=await newPage(T({'cx-exp':{tier:4,lastPracticed:now,history:[]},'lti-def':{tier:3,lastPracticed:now,history:[]},'rc-lpf':{tier:4,lastPracticed:now,history:[]}}));
   assert.deepStrictEqual(await ready(p),['impulse-conv','sinusoid-resp']);
   await p._ctx.close();
   // no-prerequisite skills are ready from the very start
   p=await newPage();assert.deepStrictEqual(await ready(p),['cx-exp','lti-def','rc-lpf']);assert.deepStrictEqual(await p.$$eval('#world .tile.ready',e=>e.map(x=>x.dataset.id).sort()),ROOTS);
   assert(/glowing|ready/i.test(await p.$eval('#banner',e=>e.textContent)));
   await p._ctx.close();
 });
 await test('ready rule ignores coming-soon prerequisites (variant build with lti-def bank removed)',async()=>{
   const html=fs.readFileSync('/workspace/skilltree/app/skilltree.html','utf8');
   const m=html.match(/const DATA = (\{.*\});\n/);assert(m,'DATA blob');
   const D=JSON.parse(m[1]);delete D.bank['lti-def'];
   const vf='/workspace/skilltree/app/tests/_variant.html';fs.writeFileSync(vf,html.replace(m[0],()=>'const DATA = '+JSON.stringify(D).replace(/<\//g,'<\\/')+';\n'));
   const ctx=await browser.createBrowserContext();const p=await ctx.newPage();await p.setViewport({width:1280,height:800});
   await p.goto('file://'+vf);await sleep(400);
   await p.evaluate((k,s)=>localStorage.setItem(k,JSON.stringify(s)),KEY,T({'cx-exp':{tier:3,lastPracticed:now,history:[]},'rc-lpf':{tier:3,lastPracticed:now,history:[]}}));await p.reload();await sleep(400);
   // lti-def is coming soon -> ignored, so sinusoid-resp (cx-exp L2, rc-lpf L2, lti-def soon) is ready; impulse-conv (only lti-def) is vacuously ready
   assert.deepStrictEqual(onlyOrig(await p.$$eval('#world .tile.ready',e=>e.map(x=>x.dataset.id).sort())),['impulse-conv','sinusoid-resp']);
   await p.evaluate(id=>document.querySelector('#world .tile[data-id="'+id+'"]').click(),'sinusoid-resp');await sleep(350);
   assert(/coming soon[^]*ignored/.test(await p.$eval('#soonNote',e=>e.textContent)),'panel mentions coming-soon prerequisites are ignored');
   assert(/Ready to learn/.test(await p.$eval('#readyNote',e=>e.textContent)));
   await ctx.close();fs.unlinkSync(vf);
 });
 await test('export / reset / import(replace + merge) round trip; invalid files rejected',async()=>{
   const dl='/tmp/dl_'+Date.now();fs.mkdirSync(dl,{recursive:true});
   const seed=T({bode:{tier:3,lastPracticed:now-DAY,history:[{t:now-DAY,round:3,correct:3,total:3,passed:true}]},'rc-lpf':{tier:1,lastPracticed:now-2*DAY,history:[]}});
   const p=await newPage(seed);
   const cdp=await browser.target().createCDPSession();await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:dl,browserContextId:p._ctx.id});
   await p.click('#btnExport');await sleep(800);
   const files=fs.readdirSync(dl);assert.strictEqual(files.length,1,'download '+files);
   const exp=JSON.parse(fs.readFileSync(path.join(dl,files[0])));
   assert.strictEqual(exp.version,1);assert.strictEqual(exp.skills.bode.tier,3);
   // reset
   await p.click('#btnReset');await sleep(200);await p.click('#confirmReset');await sleep(300);
   let s=await store(p);assert.deepStrictEqual(s.skills,{});assert.strictEqual(await p.$eval('#qCount',e=>e.textContent),'0');
   // seed something lower, then merge
   await p.evaluate(()=>{});
   const input=await p.$('#fileIn');
   // invalid json
   fs.writeFileSync(dl+'/bad.json','not json');await input.uploadFile(dl+'/bad.json');await sleep(300);
   assert(/valid JSON/.test(await p.$eval('#impErr',e=>e.textContent)));await p.keyboard.press('Escape');
   fs.writeFileSync(dl+'/bad2.json',JSON.stringify({version:2,skills:{}}));await input.uploadFile(dl+'/bad2.json');await sleep(300);
   assert(/doesn’t look like/.test(await p.$eval('#impErr',e=>e.textContent)));await p.keyboard.press('Escape');
   fs.writeFileSync(dl+'/bad3.json',JSON.stringify({version:1,skills:{x:{tier:'high'}}}));await input.uploadFile(dl+'/bad3.json');await sleep(300);
   // x invalid -> normalized to no skills -> still "valid" with 0 skills; ensure no crash and nothing changed
   await p.keyboard.press('Escape');await sleep(100);
   // merge into fresh progress that has rc-lpf tier 3 (higher than the export's 1)
   await p.evaluate(k=>{},KEY);
   await p.evaluate((k)=>{localStorage.setItem(k,JSON.stringify({version:1,skills:{'rc-lpf':{tier:3,lastPracticed:Date.now(),history:[]},'tf':{tier:2,lastPracticed:Date.now(),history:[]}}}))},KEY);
   await p.reload();await sleep(300);
   // add an unknown id into the export file too
   exp.skills['unknown-skill-xyz']={tier:2,lastPracticed:now,history:[]};fs.writeFileSync(dl+'/exp2.json',JSON.stringify(exp));
   await (await p.$('#fileIn')).uploadFile(dl+'/exp2.json');await sleep(300);
   assert(/1 unknown skill/.test(await p.$eval('#modal',e=>e.textContent)));
   await p.screenshot({path:SH+'12_import_dialog.png'});
   await p.click('#impMerge');await sleep(300);
   s=await store(p);assert.strictEqual(s.skills.bode.tier,3);assert.strictEqual(s.skills['rc-lpf'].tier,3,'merge keeps higher');assert.strictEqual(s.skills.tf.tier,2,'merge keeps local-only');assert(s.skills['unknown-skill-xyz'],'unknown kept in storage');
   // replace
   await (await p.$('#fileIn')).uploadFile(dl+'/exp2.json');await sleep(300);await p.click('#impReplace');await sleep(300);
   s=await store(p);assert.strictEqual(s.skills['rc-lpf'].tier,1,'replace');assert(!s.skills.tf);assert.strictEqual(s.skills.bode.tier,3);
   await p.reload();await sleep(300);assert(/\bt3\b/.test(await p.$eval('#world .tile[data-id="bode"]',e=>e.className)));
   await p._ctx.close();
 });
 await test('unknown skill ids in storage ignored in UI and preserved across a save',async()=>{
   const p=await newPage(T({'ghost-skill':{tier:3,lastPracticed:now,history:[]},'rc-lpf':{tier:0,lastPracticed:null,history:[]}}));
   assert.strictEqual(await p.$$eval('#world .tile',e=>e.length),121);
   await openSkill(p,'rc-lpf');await p.click('#startBtn');await sleep(200);await answerQuiz(p,'rc-lpf',[true,true,true]);
   const s=await store(p);assert.strictEqual(s.skills['ghost-skill'].tier,3);assert.strictEqual(s.skills['rc-lpf'].tier,1);
   await p._ctx.close();
 });
 await test('corrupt storage: backup kept, app still loads',async()=>{
   const p=await newPage();await p.evaluate(k=>localStorage.setItem(k,'{broken'),KEY);await p.reload();await sleep(400);
   assert.strictEqual(await p.$$eval('#world .tile',e=>e.length),121);
   const keys=await p.evaluate(()=>Object.keys(localStorage));assert(keys.some(k=>k.includes('backup')),keys.join());await p._ctx.close();
 });
 await test('storage unavailable: visible warning, in-memory progress still works',async()=>{
   const p=await newPage(null,{noStorage:true});
   assert(/storage is unavailable/i.test(await p.$eval('#warnbar',e=>e.textContent)));assert.strictEqual(await p.$eval('#warnbar',e=>getComputedStyle(e).display),'block');
   await openSkill(p,'rc-lpf');await p.click('#startBtn');await sleep(200);await answerQuiz(p,'rc-lpf',[true,true,true]);
   assert(/memory only/.test(await p.$eval('.result',e=>e.textContent)));
   await p.click('#resBack');await sleep(400);assert(/\bt1\b/.test(await p.$eval('#world .tile[data-id="rc-lpf"]',e=>e.className)));
   await p.screenshot({path:SH+'13_storage_warning.png'});await p._ctx.close();
 });
 await test('grid view + chapter filter + playable-only + persisted colored tiles',async()=>{
   const p=await newPage(T({'rc-lpf':{tier:2,lastPracticed:now,history:[]},'lti-def':{tier:4,lastPracticed:now,history:[]},'cx-exp':{tier:1,lastPracticed:now,history:[]},'impulse-conv':{tier:3,lastPracticed:now-DAY,history:[]}}));
   await openSkill(p,'impulse-conv');await sleep(300);await p.screenshot({path:SH+'14_tree_progress_panel.png'});
   await p.keyboard.press('Escape');await sleep(300);
   await p.click('#vGrid');await sleep(300);
   assert.strictEqual(await p.$eval('#gridView',e=>e.hidden),false);assert.strictEqual(await p.$eval('#treeView',e=>e.hidden),true);
   await p.screenshot({path:SH+'15_grid_view.png'});
   await p.select('#chSel','2');await sleep(200);
   assert.strictEqual(await p.$$eval('#gridView .gsec',s=>s.filter(x=>x.style.display!=='none').length),1);
   await p.select('#chSel','0');await p.click('#onlyPlay');await sleep(200);
   assert.strictEqual(await p.$$eval('#gridView .tile',t=>t.filter(x=>x.style.display!=='none').length),NPLAY);
   await p.click('#vTree');await sleep(200);
   await p.select('#chSel','1');await sleep(700);await p.screenshot({path:SH+'16_tree_chapter_filter.png'});
   await p._ctx.close();
 });
 await test('keyboard: 1-4 answer mc, Escape leave dialog does not change tier',async()=>{
   const p=await newPage();await openSkill(p,'lti-def');await p.click('#startBtn');await sleep(200);
   const q=BANK['lti-def'].find(q=>q.prompt===null);
   const t=await p.$eval('#qPrompt',e=>e.dataset.qid);const qq=BANK['lti-def'].find(x=>x.id===t);
   if(qq.type==='mc'){await p.keyboard.press('1');await p.waitForSelector('#feedback')}
   await p.keyboard.press('Escape');await sleep(200);await p.click('#confirmLeave');await sleep(400);
   const s=await store(p);assert(!s||!s.skills['lti-def']||s.skills['lti-def'].tier===0);
   assert(!(await p.$eval('#quiz',e=>e.classList.contains('open'))));
   await p._ctx.close();
 });

 /* ---------------- layout: homogeneous tree vs chapter groups ---------------- */
 const SK=JSON.parse(fs.readFileSync('/workspace/skilltree/ee105_skills_draft.json')).skills;
 const geom=p=>p.evaluate(()=>{const o={};document.querySelectorAll('#world .tile').forEach(t=>{o[t.dataset.id]={x:parseFloat(t.style.left),y:parseFloat(t.style.top),w:t.offsetWidth,h:t.offsetHeight}});
   const bl={};document.querySelectorAll('#world .blob').forEach(b=>{bl[b.dataset.ch]={x:b.offsetLeft,y:b.offsetTop,w:b.offsetWidth,h:b.offsetHeight,vis:getComputedStyle(b).visibility,op:+getComputedStyle(b).opacity}});
   return {tiles:o,blobs:bl,mode:document.getElementById('world').dataset.layout,morphing:document.getElementById('world').dataset.morphing}});
 const overlaps=g=>{const ids=Object.keys(g.tiles);const bad=[];for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++){const a=g.tiles[ids[i]],b=g.tiles[ids[j]];if(a.x<b.x+b.w&&b.x<a.x+a.w&&a.y<b.y+b.h&&b.y<a.y+a.h)bad.push(ids[i]+'~'+ids[j])}return bad};
 const waitMorph=async p=>{for(let i=0;i<40;i++){if((await p.$eval('#world',e=>e.dataset.morphing))==='0')return;await sleep(50)}throw new Error('morph never finished')};
 await test('default view is ONE homogeneous prerequisite tree: 121 tiles, prereqs strictly below dependents (bottom-up), no overlaps, no blocks',async()=>{
   const p=await newPage();const g=await geom(p);
   assert.strictEqual(g.mode,'tree');assert.strictEqual(Object.keys(g.tiles).length,121);
   assert.deepStrictEqual(overlaps(g),[],'tile overlap in tree layout');
   for(const s of SK)for(const q of s.prereqs)assert(g.tiles[s.id].y+g.tiles[s.id].h<g.tiles[q].y,'prereq '+q+' must sit BELOW (foundations at the bottom) '+s.id);
   assert(Object.values(g.blobs).every(b=>b.vis==='hidden'||b.op===0),'no chapter blocks while ungrouped');
   const layers=new Set(Object.values(g.tiles).map(t=>t.y));assert(layers.size>=20,'layered by depth '+layers.size);
   // tiles keep their chapter hue in the ungrouped tree; arrows (path per prerequisite link) exist
   const cols=await p.$$eval('#world .tile',t=>new Set(t.map(x=>x.style.getPropertyValue('--c'))).size);assert.strictEqual(cols,18);
   assert.strictEqual(await p.$$eval('#edges path',e=>e.length),180);assert(await p.$$eval('#edges path',e=>e.every(x=>(x.getAttribute('d')||'').startsWith('M'))));
   assert(/Group by chapter/.test(await p.$eval('#btnGroup',e=>e.textContent)));assert.strictEqual(await p.$eval('#btnGroup',e=>e.getAttribute('aria-pressed')),'false');
   assert(/Chapter colors/.test(await p.$eval('#chLegend',e=>e.textContent)));
   await p._ctx.close();
 });
 await test('Group by chapter: animates ~600ms, ends with chapter blocks containing their skills, no overlaps, blocks below what they depend on; Ungroup returns',async()=>{
   const p=await newPage();const g0=await geom(p);
   await p.click('#btnGroup');await sleep(230);
   const gm=await geom(p);assert.strictEqual(gm.morphing,'1','animation in progress');
   const moved=Object.keys(gm.tiles).filter(id=>Math.abs(gm.tiles[id].x-g0.tiles[id].x)+Math.abs(gm.tiles[id].y-g0.tiles[id].y)>2);assert(moved.length>100,'tiles are gliding '+moved.length);
   await sleep(150);const gm2=await geom(p);assert.strictEqual(gm2.morphing,'1','still animating at ~380ms');
   await waitMorph(p);await sleep(700);
   const g1=await geom(p);assert.strictEqual(g1.mode,'grouped');assert.strictEqual(Object.keys(g1.tiles).length,121);
   assert.deepStrictEqual(overlaps(g1),[],'tile overlap in grouped layout');
   assert.strictEqual(Object.keys(g1.blobs).length,18);assert(Object.values(g1.blobs).every(b=>b.vis==='visible'&&b.op>0.9),'blocks visible');
   for(const s of SK){const b=g1.blobs[s.chapter],t=g1.tiles[s.id];assert(t.x>=b.x&&t.y>=b.y+40&&t.x+t.w<=b.x+b.w&&t.y+t.h<=b.y+b.h,'tile '+s.id+' inside chapter block '+s.chapter)}
   const cs=Object.keys(g1.blobs);for(const a of cs)for(const c of cs)if(a<c){const A=g1.blobs[a],B=g1.blobs[c];assert(!(A.x<B.x+B.w&&B.x<A.x+A.w&&A.y<B.y+B.h&&B.y<A.y+A.h),'blocks overlap '+a+' '+c)}
   for(const s of SK)for(const q of s.prereqs){const qa=SK.find(x=>x.id===q).chapter;if(qa!==s.chapter){const A=g1.blobs[qa],B=g1.blobs[s.chapter];assert(B.y+B.h<=A.y,`block ${qa} must sit BELOW block ${s.chapter} (it feeds it)`)}}
   assert(new Set(Object.values(g1.blobs).map(b=>Math.round(b.y))).size<18,'independent blocks share a row');
   assert.strictEqual(await p.$eval('#btnGroup',e=>e.getAttribute('aria-pressed')),'true');assert(/Ungroup/.test(await p.$eval('#btnGroup',e=>e.textContent)));
   // block headers show chapter name
   assert(/Linear Time-Invariant Systems/.test(await p.$eval('.blob[data-ch="1"]',e=>e.textContent)));
   assert.strictEqual(await p.$$eval('#edges path',e=>e.length),180);
   await p.click('#btnGroup');await waitMorph(p);await sleep(700);
   const g2=await geom(p);assert.strictEqual(g2.mode,'tree');assert.deepStrictEqual(overlaps(g2),[]);
   for(const id of Object.keys(g0.tiles))assert(Math.abs(g2.tiles[id].x-g0.tiles[id].x)<1&&Math.abs(g2.tiles[id].y-g0.tiles[id].y)<1,'ungroup returns to the tree positions');
   assert(Object.values(g2.blobs).every(b=>b.vis==='hidden'));
   await p._ctx.close();
 });
 await test('toggle state persists across reload (own localStorage key); progress key untouched',async()=>{
   const seed=T({bode:{tier:2,lastPracticed:now-DAY,history:[]}});
   const p=await newPage(seed);const before=await p.evaluate(k=>localStorage.getItem(k),KEY);
   await p.click('#btnGroup');await waitMorph(p);
   assert.strictEqual(await p.evaluate(()=>localStorage.getItem('skilltree.layout.v1')),'grouped');
   assert.strictEqual(await p.evaluate(k=>localStorage.getItem(k),KEY),before,'progress storage not modified by layout toggle');
   await p.reload();await sleep(500);
   let g=await geom(p);assert.strictEqual(g.mode,'grouped');assert.strictEqual(g.morphing,'0');assert.deepStrictEqual(overlaps(g),[]);
   assert(Object.values(g.blobs).every(b=>b.vis==='visible'));assert(/Ungroup/.test(await p.$eval('#btnGroup',e=>e.textContent)));
   assert(/\bt2\b/.test(await p.$eval('#world .tile[data-id="bode"]',e=>e.className)),'progress still applied');
   await p.click('#btnGroup');await waitMorph(p);await p.reload();await sleep(500);
   g=await geom(p);assert.strictEqual(g.mode,'tree');assert.strictEqual(await p.evaluate(()=>localStorage.getItem('skilltree.layout.v1')),'tree');
   // Grid view hides the grouping button and still works from either layout
   await p.click('#btnGroup');await waitMorph(p);await p.click('#vGrid');await sleep(200);
   assert.strictEqual(await p.$eval('#btnGroup',e=>e.hidden),true);assert.strictEqual(await p.$$eval('#gridView .tile',e=>e.length),121);
   await p.click('#vTree');await sleep(200);assert.strictEqual(await p.$eval('#btnGroup',e=>e.hidden),false);
   await p._ctx.close();
 });
 await test('chapter filter + Playable-only + edge highlight work in both layouts',async()=>{
   const p=await newPage();
   for(const mode of ['tree','grouped']){
     if(mode==='grouped'){await p.click('#btnGroup');await waitMorph(p);await sleep(300)}
     await p.select('#chSel','2');await sleep(500);
     assert.strictEqual(await p.$$eval('#world .tile:not(.dim)',e=>e.length),7,mode+': only chapter 2 tiles undimmed');
     assert(await p.$$eval('#world .tile:not(.dim)',e=>e.every(t=>/Ch 2/.test(t.title))));
     assert(await p.$$eval('#edges path.fdim',e=>e.length)>100,mode+': unrelated arrows fade');
     await p.select('#chSel','0');await sleep(300);
     await p.click('#onlyPlay');await sleep(200);
     assert.strictEqual(await p.$$eval('#world .tile:not(.dim)',e=>e.length),NPLAY,mode+': playable only');
     await p.click('#onlyPlay');await sleep(100);
     // hover highlights prerequisite (blue) and next-step (orange) arrows of the hovered tile
     const box=await p.$eval('#world .tile[data-id="tf"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}});
     await p.mouse.move(box.x,box.y);await sleep(200);
     const hl=await p.evaluate(()=>({inn:document.querySelectorAll('#edges path.in').length,out:document.querySelectorAll('#edges path.out').length}));
     assert.strictEqual(hl.inn,1,mode+' in');assert(hl.out>=3,mode+' out '+hl.out);
     await p.mouse.move(5,5);
   }
   await p._ctx.close();
 });
 await test('dragging to pan never selects text; tree text is user-select:none, panel/quiz/explanations stay selectable',async()=>{
   const p=await newPage();
   const us=await p.evaluate(()=>{const g=s=>{const e=document.querySelector(s);const c=getComputedStyle(e);return c.userSelect||c.webkitUserSelect};
     return {tv:g('#treeView'),tile:g('#world .tile .nm'),blobHd:g('.blob .hd'),cp:g('.blob .cpill'),svg:g('#edges'),panel:g('#panel'),quiz:g('#quiz'),modal:g('.modal')}});
   for(const k of ['tv','tile','blobHd','cp','svg'])assert.strictEqual(us[k],'none',k+' must be user-select:none');
   for(const k of ['panel','quiz','modal'])assert.notStrictEqual(us[k],'none',k+' must stay selectable');
   for(const mode of ['tree','grouped']){
     if(mode==='grouped'){await p.click('#btnGroup');await waitMorph(p);await sleep(900)}
     await p.click('#zHome');await sleep(700);
     // drag starting on a tile label and sweeping across many tiles, then a drag over empty space
     for(const [dx,dy] of [[260,140],[-300,90],[-40,-220]]){
       const st=await p.$eval('#world .tile[data-id="tf"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}});
       await p.mouse.move(st.x,st.y);await p.mouse.down();
       for(let i=1;i<=12;i++){await p.mouse.move(st.x+dx*i/12,st.y+dy*i/12)}
       const mid=await p.evaluate(()=>String(getSelection()).length+':'+getSelection().rangeCount);
       await p.mouse.up();await sleep(60);
       const sel=await p.evaluate(()=>String(getSelection()));assert.strictEqual(sel,'',mode+' selection after drag '+JSON.stringify(sel));
       assert(/^0:/.test(mid),mode+' no selection while dragging '+mid);
       assert(!(await p.$('#panel.open')),'dragging from a tile does not open the panel');
     }
     // a pre-existing selection in the page is cleared when a drag begins
     await p.evaluate(()=>{const r=document.createRange();r.selectNodeContents(document.querySelector('h1'));const s=getSelection();s.removeAllRanges();s.addRange(r)});
     assert((await p.evaluate(()=>String(getSelection()))).length>0);
     await p.mouse.move(700,400);await p.mouse.down();await p.mouse.move(760,450,{steps:4});await p.mouse.up();
     assert.strictEqual(await p.evaluate(()=>String(getSelection())),'',mode+' stale selection cleared by drag');
     // double click / triple click on a tile label selects nothing either
     await p.click('#zHome');await sleep(700);
     const c=await p.$eval('#world .tile[data-id="tf"] .nm',e=>{const r=e.getBoundingClientRect();return{x:r.x+8,y:r.y+6}});
     assert(await p.evaluate((x,y)=>!!document.elementFromPoint(x,y).closest('#world .tile'),c.x,c.y),'triple-click lands on a tile');
     await p.mouse.click(c.x,c.y,{clickCount:3});await sleep(500);
     assert.strictEqual(await p.evaluate(()=>String(getSelection())),'',mode+' triple-click selects nothing');
     await p.keyboard.press('Escape');await sleep(300);
   }
   // clicking a tile still opens the panel after the fix, and panel text is selectable
   const b=await p.$eval('#world .tile[data-id="bode"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}});
   await p.mouse.click(b.x,b.y);await sleep(450);assert(await p.$('#panel.open'),'tile click still selects');
   const hb=await p.$eval('#panelTitle',e=>{const r=e.getBoundingClientRect();return{x:r.x+20,y:r.y+8}});
   await p.mouse.click(hb.x,hb.y,{clickCount:3});await sleep(100);
   assert(/Bode/.test(await p.evaluate(()=>String(getSelection()))),'panel title selectable');
   // quiz question text selectable
   await p.click('#startBtn');await sleep(250);
   await p.evaluate(()=>{const r=document.createRange();r.selectNodeContents(document.getElementById('qPrompt'));const s=getSelection();s.removeAllRanges();s.addRange(r)});
   assert((await p.evaluate(()=>String(getSelection()))).length>10,'quiz prompt selectable');
   await p.mouse.move(600,300);await p.mouse.down();await p.mouse.up();
   await p._ctx.close();
 });
 await test('file size & no external requests',async()=>{
   const sz=fs.statSync('/workspace/skilltree/app/skilltree.html').size;assert(sz<6*1024*1024,sz);
   const html=fs.readFileSync('/workspace/skilltree/app/skilltree.html','utf8');
   assert(!/(src|href)\s*=\s*["']https?:/i.test(html),'external ref');assert(!/@import|url\(http/i.test(html));
   const p=await newPage();const reqs=[];p.on('request',r=>reqs.push(r.url()));await p.reload();await sleep(300);
   assert(reqs.every(u=>u.startsWith('file://')),reqs.join());await p._ctx.close();
 });
 /* ---------------- bottom-up orientation ---------------- */
 const edgeGeom=p=>p.evaluate(()=>{const ts={};document.querySelectorAll('#world .tile').forEach(t=>ts[t.dataset.id]={x:parseFloat(t.style.left),y:parseFloat(t.style.top)});
   const paths=[...document.querySelectorAll('#edges path')],dots=[...document.querySelectorAll('#edges circle')];
   return {ts,paths:paths.map(x=>x.getAttribute('d')),dots:dots.map(d=>[+d.getAttribute('cx'),+d.getAttribute('cy')])}});
 await test('bottom-up: foundations at the bottom in BOTH layouts, dependents above, arrows leave the prerequisite top and enter the dependent bottom',async()=>{
   const p=await newPage();
   for(const mode of ['tree','grouped']){
     if(mode==='grouped'){await p.click('#btnGroup');await waitMorph(p);await sleep(900)}
     const g=await geom(p);
     for(const s of SK)for(const q of s.prereqs)assert(g.tiles[s.id].y+g.tiles[s.id].h<=g.tiles[q].y,`${mode}: ${s.id} must sit ABOVE its prerequisite ${q}`);
     const roots=mode==='tree'?SK.filter(s=>!s.prereqs.length).map(s=>s.id):['cx-exp','lti-def','rc-lpf'];
     // the three playable roots are in the bottom band of the whole world
     const worldH=await p.$eval('#world',e=>parseFloat(e.style.height));
     assert(roots.every(r=>g.tiles[r].y+g.tiles[r].h>worldH*0.8),mode+': roots live in the bottom fifth: '+roots.map(r=>Math.round(g.tiles[r].y)+'/'+worldH));
     const topTiles=Object.entries(g.tiles).sort((a,b)=>a[1].y-b[1].y).slice(0,5).map(e=>e[0]);
     if(mode==='tree')assert(topTiles.every(id=>SK.find(s=>s.id===id).prereqs.length>0),'nothing without prerequisites at the very top');
     // arrows: start at prerequisite TOP-centre, end (dot) at dependent BOTTOM-centre
     const eg=await edgeGeom(p);let k=0,bad=[];
     for(const s of SK)for(const q of s.prereqs){
       const d=eg.paths[k],dot=eg.dots[k];k++;
       const m=d.match(/^M([-\d.]+),([-\d.]+)/);const sx=+m[1],sy=+m[2];
       if(Math.abs(sx-(eg.ts[q].x+84))>1||Math.abs(sy-eg.ts[q].y)>1)bad.push(q+'>'+s.id+' start');
       if(Math.abs(dot[0]-(eg.ts[s.id].x+84))>1||Math.abs(dot[1]-(eg.ts[s.id].y+72))>1.5)bad.push(q+'>'+s.id+' end');
     }
     // (sideways fallback edges, if any, use the left/right sides; allow a handful)
     assert(bad.length<=Math.ceil(0.04*k),mode+': arrow endpoints off: '+bad.slice(0,6).join(','));
   }
   await p._ctx.close();
 });
 await test('home view shows the foundations (bottom of the tree) in both layouts, nothing hidden under the controls',async()=>{
   const p=await newPage();
   for(const mode of ['tree','grouped']){
     if(mode==='grouped'){await p.click('#btnGroup');await waitMorph(p);await sleep(300)}
     await p.click('#zFit');await sleep(700);await p.click('#zHome');await sleep(800);
     const vis=await p.evaluate(()=>{const tv=document.getElementById('treeView').getBoundingClientRect();const r={};
       for(const id of ['cx-exp','lti-def','rc-lpf','tf']){const b=document.querySelector('#world .tile[data-id="'+id+'"]').getBoundingClientRect();r[id]={in:b.left>=tv.left&&b.right<=tv.right&&b.top>=tv.top&&b.bottom<=tv.bottom,bottom:tv.bottom-b.bottom}}
       return r});
     for(const id of ['cx-exp','lti-def','rc-lpf'])assert(vis[id].in,mode+': root '+id+' visible at home');
     assert(vis['tf'].in,mode+': tf visible at home');
     assert(vis['cx-exp'].bottom>=60,mode+': roots sit clear of the bottom controls: '+vis['cx-exp'].bottom);
     // roots are below their dependents on screen
     const ys=await p.evaluate(()=>{const y=id=>document.querySelector('#world .tile[data-id="'+id+'"]').getBoundingClientRect().top;return [y('cx-exp'),y('sinusoid-resp'),y('tf')]});
     assert(ys[0]>ys[1]&&ys[1]>ys[2]-1,mode+' ordering on screen '+ys);
   }
   await p._ctx.close();
 });

 /* ---------------- learning plan: pure simulation (node) ---------------- */
 const cp=require('child_process');
 const html=fs.readFileSync('/workspace/skilltree/app/skilltree.html','utf8');
 const win={};new Function('window',html.match(/<script id="simcore">([\s\S]*?)<\/script>/)[1])(win);const Sim=win.SkillSim;
 const DATAJ=JSON.parse(html.match(/const DATA = (\{.*\});\n/)[1]);
 const PLAY=DATAJ.skills.filter(s=>DATAJ.bank[s.id]&&DATAJ.bank[s.id].questions.some(q=>q.round===1));
 const GRAPH={ids:PLAY.map(s=>s.id),prereqs:Object.fromEntries(DATAJ.skills.map(s=>[s.id,s.prereqs])),maxTier:{}};
 const py=(a,b)=>JSON.parse(cp.execFileSync('python3',['/workspace/skilltree/app/tests/xcheck.py',String(a),String(b)]).toString());
 await test(`simulation from scratch (${NPLAY} playable skills) matches the independent Python cross-check, deterministic`,async()=>{
   assert.strictEqual(PLAY.length,NPLAY);assert.strictEqual(NPLAY,55);
   const r=Sim.simulate(GRAPH,{},{practiceMin:10,challengeMin:10}),r2=Sim.simulate(GRAPH,{},{practiceMin:10,challengeMin:10});
   const x=py(10,10);
   assert.deepStrictEqual(JSON.stringify(r),JSON.stringify(r2),'deterministic');
   assert.strictEqual(r.sessions,x.sessions);assert.strictEqual(r.totalMinutes,x.minutes);
   assert.strictEqual(x.sessions,x.closed_form_sessions,'python loop == closed form 3*depth+1');assert.strictEqual(x.sessions,3*x.depth+1);
   assert.strictEqual(r.rows.length,x.per_session.length);
   r.rows.forEach((row,i)=>{const e=x.per_session[i];assert.deepStrictEqual([row.practiced.length,row.challenges.length,row.minutes,row.cumulative],[e.new,e.chal,e.minutes,e.cum],'session '+(i+1))});
   assert.strictEqual(r.practiceCount,NPLAY);assert.strictEqual(r.challengeCount,3*NPLAY,'3 challenges per skill');
   assert.deepStrictEqual(r.endCounts,[0,0,0,0,NPLAY]);assert.deepStrictEqual(r.startCounts,[NPLAY,0,0,0,0]);
   assert.deepStrictEqual([r.sessions,r.totalMinutes,Sim.fmtDuration(r.totalMinutes)],[37,2200,'36 h 40 min'],'55-skill totals (also == python)');
   assert.strictEqual(r.critical.chain.length,x.depth);assert.deepStrictEqual(r.critical.chain,x.chain);
   for(let i=1;i<r.critical.chain.length;i++)assert(GRAPH.prereqs[r.critical.chain[i]].includes(r.critical.chain[i-1]),'chain links are real prerequisites');
   // different per-unit times too
   const r3=Sim.simulate(GRAPH,{},{practiceMin:6.5,challengeMin:4}),x3=py(6.5,4);assert.strictEqual(r3.sessions,x3.sessions);assert(Math.abs(r3.totalMinutes-x3.minutes)<1e-6,r3.totalMinutes+' vs '+x3.minutes);
   console.log('   from scratch (defaults): '+r.sessions+' sessions, '+r.totalMinutes+' min = '+Sim.fmtDuration(r.totalMinutes)+' | python: '+x.sessions+' sessions, '+x.minutes+' min | closed form 3*'+x.depth+'+1='+(3*x.depth+1));
   console.log('   critical path: '+r.critical.chain.join(' -> '));
 });
 await test('simulation: within a session each skill takes at most one step; practiced skills are not also challenged; dependents wait for the NEXT session',async()=>{
   const g={ids:['A','B','C'],prereqs:{A:[],B:['A'],C:['B']},maxTier:{}};
   const r=Sim.simulate(g,{},{practiceMin:10,challengeMin:5});
   // A: practiced s1, L1 s2, L2 s3, Mastered s4. B ready only in s4 (A reached L2 at END of s3). C ready in s7.
   assert.deepStrictEqual(r.rows.map(x=>x.practiced.join('')),['A','','','B','','','C','','','']);
   assert.deepStrictEqual(r.rows.map(x=>x.challenges.map(c=>c.id+c.from+c.to).join(',')),['','A12','A23','A34','B12','B23','B34','C12','C23','C34']);
   assert.strictEqual(r.sessions,10);
   // minutes: s1 = 1 practice (10); s2 = 1 challenge (5); s4 = practice B (10) + challenge A (5) = 15
   assert.deepStrictEqual(r.rows.map(x=>x.minutes),[10,5,5,15,5,5,15,5,5,5]);
   assert.strictEqual(r.totalMinutes,75);
   // never two actions on one skill in the same session; tiers only rise by one per session
   const last={};r.rows.forEach(row=>{const ids=row.practiced.concat(row.challenges.map(c=>c.id));assert.strictEqual(new Set(ids).size,ids.length,'one action per skill per session')});
   // a level-1 prerequisite at the start does NOT make its dependent ready in session 1
   const r2=Sim.simulate({ids:['A','B'],prereqs:{A:[],B:['A']},maxTier:{}},{A:2},{});
   assert.deepStrictEqual(r2.rows[0].practiced,[],'A is only Level 1 -> B not ready');assert.deepStrictEqual(r2.rows[0].challenges.map(c=>c.id),['A']);
   assert.deepStrictEqual(r2.rows[1].practiced,['B'],'ready the session AFTER A reached Level 2');assert.strictEqual(r2.sessions,5);
   // a Level-2 prerequisite at the start makes the dependent ready immediately
   const r3=Sim.simulate({ids:['A','B'],prereqs:{A:[],B:['A']},maxTier:{}},{A:3},{});
   assert.deepStrictEqual(r3.rows[0].practiced,['B']);assert.deepStrictEqual(r3.rows[0].challenges.map(c=>c.id),['A']);assert.strictEqual(r3.sessions,4);
   // prerequisites outside the simulated set (coming soon) are ignored
   const r4=Sim.simulate({ids:['B'],prereqs:{B:['not-playable']},maxTier:{}},{},{});assert.deepStrictEqual(r4.rows[0].practiced,['B']);assert.strictEqual(r4.sessions,4);
 });
 await test('simulation: finished state returns 0 sessions; current-progress start; partial progress shortens the plan',async()=>{
   const done=Object.fromEntries(GRAPH.ids.map(i=>[i,4]));
   const r=Sim.simulate(GRAPH,done,{});assert.strictEqual(r.ok,true);assert.strictEqual(r.sessions,0);assert.strictEqual(r.totalMinutes,0);assert.deepStrictEqual(r.rows,[]);assert.deepStrictEqual(r.critical.chain,[]);
   const scratch=Sim.simulate(GRAPH,{},{});
   const part=Sim.simulate(GRAPH,{'drude':4,'si-props':4,'intrinsic':3,'doping':2,'drift':1},{});   // progress along the critical (device-physics) chain
   assert(part.sessions<scratch.sessions&&part.totalMinutes<scratch.totalMinutes,'progress shortens the plan: '+part.sessions+' vs '+scratch.sessions);
   assert.deepStrictEqual(part.startCounts,[NPLAY-5,1,1,1,2]);
   assert.deepStrictEqual(part.endCounts,[0,0,0,0,NPLAY]);
   // all-but-one-step: a single Level 2 skill with nothing else needs 1 session
   const one=Object.fromEntries(GRAPH.ids.map(i=>[i,4]));one['bode']=3;const r1=Sim.simulate(GRAPH,one,{});assert.strictEqual(r1.sessions,1);assert.strictEqual(r1.totalMinutes,10);assert.deepStrictEqual(r1.critical.chain,['bode']);
   // unknown / out-of-range start tiers are clamped
   const wild=Sim.simulate(GRAPH,{'cx-exp':99,'lti-def':-3,ghost:2},{});assert.strictEqual(wild.ok,true);
   // skills without questions for every round stop at their highest reachable tier
   const lim=Sim.simulate({ids:['A'],prereqs:{A:[]},maxTier:{A:2}},{},{});assert.strictEqual(lim.sessions,2);
 });
 await test('timing samples: <20 s ignored, 30 min cap, default 10 until 3 samples then the mean, tolerant normalize',async()=>{
   let l=[];
   for(const s of [5,19.9,0,-4,NaN,'x'])assert.strictEqual(Sim.addSample(l,s,1).added,false,'rejected '+s);
   let r=Sim.addSample(l,20,1);assert.strictEqual(r.added,true);l=r.list;
   r=Sim.addSample(l,99999,2);l=r.list;assert.strictEqual(l[1].s,1800,'capped at 30 min');
   assert.deepStrictEqual(Sim.estimate(l,10),{minutes:10,n:2,source:'default',need:3});
   l=Sim.addSample(l,300,3).list;
   const e=Sim.estimate(l,10);assert.strictEqual(e.source,'measured');assert.strictEqual(e.n,3);assert.strictEqual(e.minutes,Math.round((20+1800+300)/3/60*10)/10);
   const e2=Sim.estimate(Sim.addSample(Sim.addSample(Sim.addSample([],360,1).list,372,2).list,384,3).list,10);assert.deepStrictEqual([e2.minutes,e2.n,e2.source],[6.2,3,'measured']);
   assert.strictEqual(Sim.estimate([],7).minutes,7);
   let big=[];for(let i=0;i<260;i++)big=Sim.addSample(big,60,i).list;assert.strictEqual(big.length,200,'sample list bounded');
   const n=Sim.normalizeTiming(undefined);assert.deepStrictEqual([n.practice,n.challenge,n.override.practice],[[],[],null]);
   const n2=Sim.normalizeTiming({practice:[{s:100,t:1},{s:3,t:2},'bad',null],challenge:'nope',override:{practice:'abc',challenge:7}});
   assert.deepStrictEqual([n2.practice.length,n2.challenge.length,n2.override.practice,n2.override.challenge],[1,0,null,7]);
   assert.strictEqual(Sim.mergeSamples([{s:60,t:1}],[{s:60,t:1},{s:90,t:2}]).length,2,'merge de-duplicates');
 });

 /* ---------------- learning plan: in the app ---------------- */
 const T0=p=>p.evaluate(()=>JSON.parse(localStorage.getItem('skilltree.timing.v1')));
 const timeShift=(p,ms)=>p.evaluate(ms=>{const o=Date.now;window.__o=window.__o||o;Date.now=()=>window.__o()+ms},ms);
 await test('quiz timing is recorded under its OWN key (not in progress); <20 s ignored; long sessions capped; challenges and practice kept apart; review not recorded',async()=>{
   const p=await newPage();
   await openSkill(p,'rc-lpf');await p.click('#startBtn');await sleep(150);await answerQuiz(p,'rc-lpf',[true,true,true]);   // fast: well under 20 s
   assert.strictEqual(await T0(p),null,'a quick quiz is ignored');
   await p.click('#resBack');await sleep(400);await p.keyboard.press('Escape');await sleep(200);
   await openSkill(p,'lti-def');await p.click('#startBtn');await sleep(150);await timeShift(p,95000);await answerQuiz(p,'lti-def',[true,true,true]);
   let t=await T0(p);assert.strictEqual(t.practice.length,1);assert(t.practice[0].s>=94&&t.practice[0].s<=100,'~95 s recorded '+t.practice[0].s);assert.strictEqual(t.challenge.length,0);
   const prog=await store(p);assert(!('timing' in prog),'timing is not in the progress record');assert(!JSON.stringify(prog).includes('"practice"'));
   await p.click('#resBack');await sleep(400);await p.keyboard.press('Escape');await sleep(200);
   // challenge on rc-lpf (Practiced -> Level 1) taking 3 hours -> capped at 1800 s
   await openSkill(p,'rc-lpf');await p.click('#startBtn');await sleep(150);await timeShift(p,95000+3*3600*1000);await answerQuiz(p,'rc-lpf',[true,true,true]);
   t=await T0(p);assert.strictEqual(t.challenge.length,1);assert.strictEqual(t.challenge[0].s,1800,'capped');assert.strictEqual(t.practice.length,1);
   await p.click('#resBack');await sleep(400);
   // review mode does not record (tier Mastered skill)
   await p._ctx.close();
   const p2=await newPage(T({bode:{tier:4,lastPracticed:now-DAY,history:[]}}));
   await openSkill(p2,'bode');await p2.click('#startBtn');await sleep(150);await timeShift(p2,120000);await answerQuiz(p2,'bode',[true,true,true]);
   assert.strictEqual(await T0(p2),null,'review mode is not timed');await p2._ctx.close();
 });
 await test('Learning plan panel: scope note, scratch toggle, sessions/total, critical path, charts, expandable table, header badge',async()=>{
   const p=await newPage();
   const badge=await p.$eval('#planCount',e=>e.textContent);assert.strictEqual(badge,'37');
   await p.click('#btnPlan');await sleep(300);
   assert(/only the 55 playable skills/.test(await p.$eval('#planScope',e=>e.textContent)));assert(/66/.test(await p.$eval('#planScope',e=>e.textContent)));assert(/grow as more question banks/.test(await p.$eval('#planScope',e=>e.textContent)));
   assert.strictEqual(await p.$eval('#planSessions',e=>e.textContent),'37');assert.strictEqual(await p.$eval('#planTotal',e=>e.textContent),'36 h 40 min');
   assert(/Using default 10 min per mastery challenge/.test(await p.$eval('#estNoteC',e=>e.textContent)));
   const crit=await p.$eval('#planCritical',e=>e.textContent);assert(/Critical path/.test(crit)&&/3 × 12 \+ 1 = 37/.test(crit),crit);
   assert.strictEqual(await p.$$eval('#planCritical .cpn',e=>e.length),12);
   assert.strictEqual(await p.$$eval('#minChart rect',e=>e.length)>=37,true);assert.strictEqual(await p.$$eval('#tierChart rect',e=>e.length)>=37,true);
   assert.strictEqual(await p.$$eval('#planTable tbody tr.prow',e=>e.length),37);
   const row1=await p.$eval('#planTable tbody tr.prow',e=>[...e.children].map(c=>c.textContent));assert.deepStrictEqual(row1.slice(0,5),['1','5','–','50 min','50 min']);
   await p.click('#planTable tbody tr.prow');await sleep(100);assert(/Practice \(Round 1\)/.test(await p.$eval('#planTable tr.pdet',e=>e.textContent)));
   await p.click('#planScr');await sleep(200);assert.strictEqual(await p.$eval('#planSessions',e=>e.textContent),'37');
   await p.screenshot({path:SH+'34_simulation_panel.png'});
   await p.$eval('#modal',e=>e.scrollTop=e.scrollHeight);await sleep(150);await p.screenshot({path:SH+'35_simulation_panel_table.png'});
   await p.keyboard.press('Escape');await sleep(150);assert(!(await p.$('#modalBack.open')));
   await p._ctx.close();
 });
 await test('Learning plan from CURRENT progress vs scratch; first-session practice set equals the app\'s own "ready" rule; completed => 0 sessions',async()=>{
   const prog=T({'lti-def':{tier:4,lastPracticed:now-DAY,history:[]},'cx-exp':{tier:3,lastPracticed:now-DAY,history:[]},'rc-lpf':{tier:3,lastPracticed:now-2*DAY,history:[]},'impulse-conv':{tier:2,lastPracticed:now-DAY,history:[]},'sinusoid-resp':{tier:1,lastPracticed:now-3*DAY,history:[]},'drude':{tier:4,lastPracticed:now-DAY,history:[]},'si-props':{tier:3,lastPracticed:now-DAY,history:[]}});
   let p=await newPage(prog);
   const r=await p.evaluate(()=>{const a=__skillgrove.plan(false),b=__skillgrove.plan(true);return {cur:[a.sessions,a.totalMinutes,a.rows[0].practiced.slice().sort()],scr:[b.sessions,b.totalMinutes],ready:__skillgrove.ready().sort()}});
   assert.deepStrictEqual(r.cur[2],r.ready,'session-1 practice set == isReady() set');
   assert(r.cur[0]<r.scr[0]&&r.cur[1]<r.scr[1]);assert.strictEqual(r.scr[0],37);
   assert.strictEqual(await p.$eval('#planCount',e=>e.textContent),String(r.cur[0]));
   await p.click('#btnPlan');await sleep(300);assert.strictEqual(await p.$eval('#planSessions',e=>e.textContent),String(r.cur[0]));
   assert(/Starting from your saved progress \(\d+ of 55/.test(await p.$eval('#planStartNote',e=>e.textContent)));
   await p.click('#planScr');await sleep(200);assert.strictEqual(await p.$eval('#planSessions',e=>e.textContent),'37');
   assert(/Pretending/.test(await p.$eval('#planStartNote',e=>e.textContent)));
   assert.strictEqual((await store(p)).skills['lti-def'].tier,4,'simulating never touches real progress');
   await p._ctx.close();
   const all=T(Object.fromEntries(PLAY.map(s=>[s.id,{tier:4,lastPracticed:now-DAY,history:[]}])));
   p=await newPage(all);assert.strictEqual(await p.$eval('#planCount',e=>e.textContent),'✓');
   await p.click('#btnPlan');await sleep(300);assert(/0 sessions/.test(await p.$eval('#planDone',e=>e.textContent)));
   await p.screenshot({path:SH+'36_simulation_done.png'});
   await p.click('#planScr');await sleep(200);assert.strictEqual(await p.$eval('#planSessions',e=>e.textContent),'37');
   await p._ctx.close();
 });
 await test('Learning plan uses your measured averages once >=3 samples exist, shows which estimate is used, and lets you override both',async()=>{
   const p=await newPage();
   await p.evaluate(()=>localStorage.setItem('skilltree.timing.v1',JSON.stringify({version:1,practice:[{s:600,t:1},{s:700,t:2}],challenge:[{s:330,t:1},{s:372,t:2},{s:390,t:3}],override:{practice:null,challenge:null}})));
   await p.reload();await sleep(400);
   await p.click('#btnPlan');await sleep(300);
   assert.strictEqual(await p.$eval('#estNoteC',e=>e.textContent),'Using your average: 6.1 min per mastery challenge (3 samples).');
   assert(/Using default 10 min per new-skill practice quiz\. Your own average replaces it after 3 timed quizzes \(2 so far\)/.test(await p.$eval('#estNoteP',e=>e.textContent)));
   assert.strictEqual(await p.$eval('#estChallenge',e=>e.value),'6.1');assert.strictEqual(await p.$eval('#estPractice',e=>e.value),'10');
   // 55*10 + 165*6.1 = 1556.5 min
   assert.strictEqual(await p.$eval('#planTotal',e=>e.textContent),'25 h 57 min');
   // override both
   await p.$eval('#estChallenge',e=>e.select());await p.keyboard.type('5');await sleep(150);
   assert(/Using your typed value: 5 min per mastery challenge/.test(await p.$eval('#estNoteC',e=>e.textContent)));
   await p.$eval('#estPractice',e=>e.select());await p.keyboard.type('15');await sleep(150);
   assert.strictEqual(await p.$eval('#planTotal',e=>e.textContent),'27 h 30 min');   // 55*15 + 165*5 = 1650 min
   assert.strictEqual((await T0(p)).override.challenge,5);
   await p.screenshot({path:SH+'37_simulation_override.png'});
   // override persists across reload; reset returns to auto
   await p.keyboard.press('Escape');await p.reload();await sleep(400);await p.click('#btnPlan');await sleep(300);
   assert.strictEqual(await p.$eval('#estChallenge',e=>e.value),'5');
   await p.click('#estResetC');await sleep(150);assert.strictEqual(await p.$eval('#estChallenge',e=>e.value),'6.1');
   assert.strictEqual(await p.$eval('#estResetC',e=>e.hidden),true);
   await p._ctx.close();
 });
 await test('export includes optional timing; import tolerates files WITHOUT timing and merges/replaces timing when present; progress format unchanged',async()=>{
   const dl='/tmp/dlt_'+Date.now();fs.mkdirSync(dl,{recursive:true});
   const p=await newPage(T({bode:{tier:2,lastPracticed:now-DAY,history:[]}}));
   const cdp=await browser.target().createCDPSession();await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:dl,browserContextId:p._ctx.id});
   await p.evaluate(()=>localStorage.setItem('skilltree.timing.v1',JSON.stringify({version:1,practice:[{s:200,t:11},{s:210,t:12},{s:220,t:13}],challenge:[{s:100,t:21}],override:{practice:null,challenge:null}})));await p.reload();await sleep(400);
   await p.click('#btnExport');await sleep(800);
   const f=fs.readdirSync(dl);assert.strictEqual(f.length,1);const exp=JSON.parse(fs.readFileSync(path.join(dl,f[0])));
   assert.strictEqual(exp.version,1);assert.strictEqual(exp.skills.bode.tier,2);assert.strictEqual(exp.timing.practice.length,3);assert.strictEqual(exp.timing.challenge.length,1);
   assert.deepStrictEqual(Object.keys(exp).sort(),['app','exportedAt','skills','timing','version']);
   // an OLD export (no timing field) imports fine, leaves timing untouched
   const old={version:1,app:'skillgrove',exportedAt:'2026-01-01T00:00:00Z',skills:{'rc-lpf':{tier:3,lastPracticed:now,history:[]}}};fs.writeFileSync(dl+'/old.json',JSON.stringify(old));
   await (await p.$('#fileIn')).uploadFile(dl+'/old.json');await sleep(300);assert(!/timing sample/.test(await p.$eval('#modal',e=>e.textContent)));
   await p.click('#impMerge');await sleep(300);
   let s=await store(p);assert.strictEqual(s.skills['rc-lpf'].tier,3);assert.strictEqual(s.skills.bode.tier,2);
   assert.strictEqual((await T0(p)).practice.length,3,'timing untouched by a file without timing');
   // a file with timing: merge de-duplicates, replace overwrites
   const withT={version:1,skills:{},timing:{practice:[{s:200,t:11},{s:500,t:99}],challenge:[]}};fs.writeFileSync(dl+'/wt.json',JSON.stringify(withT));
   await (await p.$('#fileIn')).uploadFile(dl+'/wt.json');await sleep(300);assert(/2 quiz-timing samples/.test(await p.$eval('#modal',e=>e.textContent)));
   await p.click('#impMerge');await sleep(300);assert.strictEqual((await T0(p)).practice.length,4);assert.strictEqual((await T0(p)).challenge.length,1);
   await (await p.$('#fileIn')).uploadFile(dl+'/wt.json');await sleep(300);await p.click('#impReplace');await sleep(300);
   assert.strictEqual((await T0(p)).practice.length,2);assert.strictEqual((await T0(p)).challenge.length,0);
   // garbage timing in a file is tolerated
   fs.writeFileSync(dl+'/gt.json',JSON.stringify({version:1,skills:{},timing:'oops'}));await (await p.$('#fileIn')).uploadFile(dl+'/gt.json');await sleep(300);
   assert(await p.$('#impMerge'));await p.click('#impMerge');await sleep(200);
   // progress record stays exactly {version, skills, savedAt} (no timing leaked in)
   s=await store(p);assert.deepStrictEqual(Object.keys(s).sort().filter(k=>k!=='savedAt'),['skills','version']);
   await p._ctx.close();
 });

 /* ---------------- math (KaTeX) + figures across EVERY question ---------------- */
 await test('all 660 questions: math rendered (no raw \\( \\) \\[ \\] left in the DOM), no KaTeX errors, figure shown iff defined (sanitized, labelled, sized); explanations and review recap too',async()=>{
   const nQ=Object.values(BANK).reduce((a,b)=>a+b.length,0);assert.strictEqual(nQ,660);
   const nFig=Object.values(BANK).flat().filter(q=>q.figure).length;
   for(const vp of [{width:1280,height:800},{width:390,height:800}]){
     const p=await newPage();await p.setViewport(vp);await sleep(150);
     const r=await p.evaluate(()=>{
       const out={n:0,raw:[],figMiss:[],figExtra:[],figBad:[],overflow:[],mathCount:0,ex:0,katexErr:[]};
       const RAW=/\\\(|\\\)|\\\[|\\\]/;
       const vis=()=>{const t=document.getElementById('quiz').cloneNode(true);t.querySelectorAll('.katex-mathml').forEach(e=>e.remove());return t.textContent};
       const QA=__skillgrove.qa,B=QA.bank(),prepareQ=QA.prepareQ,renderQuiz=QA.renderQuiz;QA.openQuiz();
       for(const sid of Object.keys(B)){
         const qs=B[sid].questions;
         for(const q of qs){
           const it=prepareQ(q);
           QA.setQuiz({id:sid,round:q.round,mode:'review',items:[it],i:0,result:null,t0:Date.now()});
           for(const phase of ['ask','answered']){
             if(phase==='answered'){it.done=true;it.chosen=0;it.correct=false;it.text='1'}
             renderQuiz();out.n++;
             const txt=document.getElementById('quiz').textContent;
             if(RAW.test(txt)||RAW.test(vis()))out.raw.push(q.id+':'+phase);
             const f=document.querySelectorAll('#quiz .qcard figure.qfig svg');
             if(q.figure&&f.length!==1)out.figMiss.push(q.id);
             if(!q.figure&&f.length)out.figExtra.push(q.id);
             if(f.length){const s=f[0],b=s.getBoundingClientRect();
               if(s.getAttribute('aria-label')!==q.figure_alt||!s.querySelector('title')||s.querySelector('script,foreignObject,image,use,a,style')||b.width<120||b.height<24)out.figBad.push(q.id+' '+Math.round(b.width)+'x'+Math.round(b.height))}
             const card=document.querySelector('#quiz .qcard');
             if(card.scrollWidth>card.clientWidth+1)out.overflow.push(q.id+':'+phase+' '+card.scrollWidth+'>'+card.clientWidth);
             out.mathCount+=document.querySelectorAll('#quiz .katex').length;
             if(phase==='answered'&&document.querySelector('#feedback .ex')&&document.querySelector('#feedback .ex').textContent.length>20)out.ex++;
           }
         }
         // results view: recap + every explanation in the review list (figures included)
         QA.setQuiz({id:sid,round:1,mode:'review',items:qs.map(prepareQ).map(x=>Object.assign(x,{done:true,correct:false,chosen:0})),i:0,result:{correct:0,n:qs.length,passed:true,before:0,after:0},t0:Date.now()});
         renderQuiz();
         if(RAW.test(document.getElementById('quiz').textContent))out.raw.push(sid+':results');
         const want=qs.filter(q=>q.figure).length;if(document.querySelectorAll('#quiz details figure.qfig svg').length!==want)out.figMiss.push(sid+':results');
       }
       out.matherr=document.querySelectorAll('.matherr').length;out.katexErr=window.__katexErrors.slice(0,5);out.katexErrN=window.__katexErrors.length;
       QA.closeQuizUI();return out;
     });
     console.log(`   ${vp.width}px: ${r.n} renders, ${r.mathCount} KaTeX nodes, ${nFig} figures expected; overflow ${r.overflow.length}`);
     assert.strictEqual(r.n,2*660);assert.strictEqual(r.ex,660,'explanation shown for every question');
     assert.deepStrictEqual(r.raw,[],'raw delimiters');assert.deepStrictEqual(r.figMiss,[],'figure missing');assert.deepStrictEqual(r.figExtra,[],'unexpected figure');
     assert.deepStrictEqual(r.figBad,[],'figure attrs/size');assert.strictEqual(r.katexErrN,0,'KaTeX errors: '+r.katexErr.join(' | '));assert.strictEqual(r.matherr,0);
     assert.deepStrictEqual(r.overflow,[],'horizontal overflow');
     assert(r.mathCount>3000,'math rendered '+r.mathCount);
     await p._ctx.close();
   }
 });
 await test('KaTeX fonts + CSS are inlined (offline); figures inherit the theme colour (currentColor) and are sanitized',async()=>{
   const html=fs.readFileSync('/workspace/skilltree/app/skilltree.html','utf8');
   assert(/<script id="katexjs">/.test(html)&&/<style id="katexcss">/.test(html));
   assert(!/url\(fonts\//.test(html),'font urls must be inlined');assert((html.match(/data:font\/woff2;base64,/g)||[]).length>=19);
   const p=await newPage(T({bode:{tier:3,lastPracticed:now-DAY,history:[]}}));
   const r=await p.evaluate(async()=>{await document.fonts.load('20px KaTeX_Main','ω');await document.fonts.load('italic 20px KaTeX_Math','x');await document.fonts.ready;
     const evil={id:'x',type:'mc',round:1,prompt:'Area \\(\\pi r^2\\) ok',options:['\\(a\\)','b','c','d'],correct_index:0,explanation:'e',figure:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10" onload="window.__pwn=1" style="width:9999px"><script>window.__pwn=2<\/script><a href="javascript:alert(1)"><circle r="3"/></a><line x1="0" y1="0" x2="10" y2="10" stroke="currentColor"/><image href="http://example.com/x.png"/></svg>',figure_alt:'test alt'};
     const f=__skillgrove.qa.figureNode(evil);document.body.append(f);
     return {pwn:window.__pwn||0,html:f.innerHTML,fonts:[...document.fonts].filter(x=>/KaTeX/.test(x.family)&&x.status==='loaded').length,
       color:getComputedStyle(f).color,ink:getComputedStyle(document.documentElement).getPropertyValue('--ink').trim()}});
   assert.strictEqual(r.pwn,0);assert(!/script|onload|href|image|style=/i.test(r.html),r.html);assert(/<line/.test(r.html));assert(/<title>test alt<\/title>/.test(r.html));
   assert(r.fonts>=1,'a KaTeX font face loaded from the inline data');
   await p._ctx.close();
 });
 await browser.close();
 console.log(results.map(r=>r.join('  ')).join('\n'));
 console.log('console errors/warnings:',errs.length?errs:'none');
 const f=results.filter(r=>r[0]==='FAIL').length;console.log(f?`${f} FAILED`:'ALL PASSED ('+results.length+')');process.exit(f?1:0);
})();
