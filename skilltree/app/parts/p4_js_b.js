
/* ====================== stats / banner / refresh ====================== */
function refreshAll(){
  document.querySelectorAll('.tile[data-id]').forEach(refreshTile);
  renderStats();renderBanner();renderPlanBadge();
  $('qCount').textContent=queue().length;
  document.querySelectorAll('[data-ct]').forEach(e=>{
    const ch=+e.dataset.ct;const l=skills.filter(s=>s.chapter===ch);const p=l.filter(s=>isPlayable(s.id)).length;
    const c=l.filter(s=>tierOf(s.id)>0).length;
    e.textContent=`${c}/${l.length} colored in`+(p?` · ${p} playable`:'');
  });
  applyGridFilter();applyEdgeHighlight();
}
function renderStats(){
  const counts=[0,0,0,0,0];skills.forEach(s=>counts[tierOf(s.id)]++);
  const pct=skills.reduce((a,s)=>a+tierOf(s.id),0)/(4*skills.length)*100;
  const pp=playable.length?playable.reduce((a,s)=>a+tierOf(s.id),0)/(4*playable.length)*100:0;
  const f=v=>v<10?v.toFixed(1):String(Math.round(v));
  const st=$('stats');st.innerHTML='';
  const nReady=skills.filter(s=>isReady(s.id)).length;
  st.append(el('div',{class:'meter',title:'Weighted by tier: Practiced = ¼, Level 1 = ½, Level 2 = ¾, Mastered = 1 per skill'},
    el('span',{text:'Colored in'}),el('b',{id:'pctTxt',text:f(pct)+'%'}),
    el('span',{class:'bar'},el('i',{style:`width:${pct}%`})),el('span',{style:'font-size:12px;color:var(--ink2);white-space:nowrap',text:`${f(pp)}% of playable`})));
  st.append(el('span',{class:'sep'}));
  TIERS.forEach((n,i)=>st.append(el('span',{class:'chip','data-tier':i,title:i===0?'Not started yet':'Skills at '+n},el('span',{class:'sw t'+i,style:`--f:${FILL[i]}%`}),n,' ',el('b',{text:counts[i]}))));
  st.append(el('span',{class:'chip',title:'Unpracticed skills whose prerequisites are all at Level 2 or Mastered (skills with no prerequisites are ready from the start; coming-soon prerequisites are ignored)'},el('span',{class:'sw ready'}),'Ready to learn ',el('b',{text:nReady})));
  st.append(el('span',{class:'chip',title:'No questions written yet'},el('span',{class:'sw soon'}),'Coming soon ',el('b',{text:skills.length-playable.length})));
  const hc=$('hctl');hc.innerHTML='';
  const sel=el('select',{id:'chSel','aria-label':'Filter by chapter'},el('option',{value:0,text:'All chapters'}),chNums.map(c=>el('option',{value:c,text:`Ch ${c} · ${DATA.chapters[c]}`})));
  sel.value=filter.chapter;
  sel.onchange=()=>{filter.chapter=+sel.value;refreshAll();if(filter.view==='tree'){filter.chapter?focusChapter(filter.chapter):(layoutMode==='grouped'?goHome(true):goFit())}};
  const chk=el('input',{type:'checkbox',id:'onlyPlay'});chk.checked=filter.playable;chk.onchange=()=>{filter.playable=chk.checked;refreshAll()};
  hc.append(el('div',{class:'seg',role:'group','aria-label':'View'},
    el('button',{id:'vTree','aria-pressed':String(filter.view==='tree'),onclick:()=>setView('tree')},'Tree'),
    el('button',{id:'vGrid','aria-pressed':String(filter.view==='grid'),onclick:()=>setView('grid')},'Grid')),
    sel,el('label',{class:'chk'},chk,'Playable only'));
}
function setView(v){
  filter.view=v;$('treeView').hidden=v!=='tree';$('gridView').hidden=v!=='grid';$('btnGroup').hidden=v!=='tree';
  $('vTree').setAttribute('aria-pressed',String(v==='tree'));$('vGrid').setAttribute('aria-pressed',String(v==='grid'));
  try{localStorage.setItem(UIKEY,JSON.stringify({view:v}))}catch(e){}
}
let bannerHidden=false;
function short(s,n){return s.length>n?s.slice(0,n-1)+'…':s}
function renderBanner(){
  const b=$('banner');b.innerHTML='';
  if(bannerHidden){return}
  const ready=skills.filter(s=>isReady(s.id)),q=queue();
  const started=skills.some(s=>tierOf(s.id)>0);
  b.append(el('span',{},el('b',{text:started?'Go wide before deep. ':'Welcome! '}),
    started?'New skills are recommended once their prerequisites reach Level 2, so go wide rather than racing one branch to Mastered; spaced mastery challenges stick better after a break.'
           :'Pick a glowing “ready” skill (no prerequisites needed to start), then spread out across the tree. A new skill glows once its prerequisites reach Level 2.'));
  if(ready.length)b.append(el('span',{class:'rd'},el('b',{text:'Ready to learn:'}),ready.slice(0,2).map(s=>el('button',{class:'pill',style:colorVars(s.chapter),onclick:()=>selectSkill(s.id,true),title:s.name},short(s.name,24))),ready.length>2?el('span',{text:`+${ready.length-2} more`}):null));
  if(q.length)b.append(el('button',{class:'pill',style:'--c:#ff7a59;--cs:#ffe3da',onclick:openQueue},`${q.length} mastery challenge${q.length>1?'s':''} waiting`));
  b.append(el('button',{class:'x','aria-label':'Dismiss tip',onclick:()=>{bannerHidden=true;renderBanner()}},'×'));
}

/* ====================== skill panel ====================== */
function selectSkill(id,focus){
  selected=id;
  document.querySelectorAll('.tile[data-id]').forEach(refreshTile);
  placePanel();panel.classList.add('open');panel.setAttribute('aria-hidden','false');
  renderPanel();applyEdgeHighlight();
  if(focus&&filter.view==='tree')focusTile(id);
  if(focus&&filter.view==='grid'){const t=document.querySelector(`#gridView .tile[data-id="${id}"]`);t&&t.scrollIntoView({block:'center',behavior:'smooth'})}
}
function placePanel(){panel.style.top=quizOpen?'0px':document.querySelector('main').getBoundingClientRect().top+'px'}
window.addEventListener('resize',()=>{if(panelOpen())placePanel()});
function closePanel(){
  const was=selected;
  panel.classList.remove('open');panel.setAttribute('aria-hidden','true');
  selected=null;document.querySelectorAll('.tile[data-id]').forEach(refreshTile);applyEdgeHighlight();
  if(was&&!quizOpen){const vis=[...document.querySelectorAll(`.tile[data-id="${was}"]`)].find(x=>x.offsetParent);vis&&vis.focus({preventScroll:true})}
}
function tierPill(id){const s=byId[id],t=tierOf(id);
  return el('button',{class:'pill',style:colorVars(s.chapter),onclick:()=>selectSkill(id,true),title:TIERS[t]+(isPlayable(id)?'':' · coming soon')},
    el('span',{class:'sw t'+t,style:`--f:${FILL[t]}%;width:14px;height:14px;border-color:${chColor(s.chapter)}`}),short(s.name,40))}
const need=n=>Math.ceil(n*2/3);
function renderPanel(){
  const id=selected;panel.innerHTML='';if(!id)return;
  const s=byId[id],t=tierOf(id),soon=!isPlayable(id),ready=isReady(id);
  const nextR=t+1,kids=[];
  kids.push(el('button',{class:'close','aria-label':'Close panel',onclick:closePanel},'×'));
  kids.push(el('div',{style:colorVars(s.chapter)},el('span',{class:'cpill',text:`Ch ${s.chapter} · ${DATA.chapters[s.chapter]}`})));
  kids.push(el('h2',{text:s.name,id:'panelTitle'}));
  kids.push(el('div',{class:'kv',text:`Reader section ${s.reader_section||'—'} · id: ${s.id}`}));
  if(soon)kids.push(el('div',{class:'note soon',role:'note'},el('b',{text:'Coming soon. '}),'This skill is in the tree, but its questions haven’t been written yet, so it can’t be practiced in this demo.'));
  else{
    kids.push(el('div',{class:'steps',style:colorVars(s.chapter),role:'img','aria-label':'Tier: '+TIERS[t]},
      TIERS.map((n,i)=>el('div',{class:'step'+(i<=t&&i>0?' done':'')+(i===t?' cur':'')},el('div',{class:'dot',text:i>0&&i<=t?'✓':''}),n))));
    kids.push(el('div',{class:'kv',id:'panelTier'},el('b',{text:'Tier: '}),TIERS[t],ready?' · ready to learn':''));
    kids.push(el('div',{class:'kv',id:'panelLast',title:lastOf(id)?fmtDate(lastOf(id)):''},el('b',{text:'Last practiced: '}),lastOf(id)?`${ago(lastOf(id))} (${fmtDate(lastOf(id))})`:'never'));
    const gaps=prereqGaps(id),soonP=s.prereqs.filter(p=>!isPlayable(p));
    if(t===0&&ready)kids.push(el('div',{class:'note ok',id:'readyNote'},el('b',{text:'Ready to learn: '}),s.prereqs.length&&s.prereqs.some(isPlayable)?'all its prerequisites are at Level 2 or Mastered.':'it has no prerequisites you can practice yet, so you can start right away.'));
    if(gaps.length&&t===0)kids.push(el('div',{class:'note warn',id:'prereqNote'},el('b',{text:'Gentle heads-up: '}),`this skill is recommended once its prerequisites reach Level 2. Still to go: ${gaps.map(p=>`${byId[p].name} (${TIERS[tierOf(p)]})`).join('; ')}. Nothing is locked, so start whenever you like.`));
    if(soonP.length)kids.push(el('div',{class:'note info',id:'soonNote'},`${soonP.length} prerequisite${soonP.length>1?'s are':' is'} coming soon (${soonP.map(p=>byId[p].name).join('; ')}). ${soonP.length>1?'They have':'It has'} no questions yet, so ${soonP.length>1?'they are':'it is'} ignored when deciding whether this skill is ready.`));
    if(quizOpen)kids.push(el('div',{class:'note info',text:'Finish or leave the current quiz to start something new.'}));
    else if(t<4){
      const n=roundQs(id,nextR).length;
      if(!n)kids.push(el('div',{class:'note soon',text:`Round ${nextR} questions aren’t written yet for this skill.`}));
      else if(nextR===1){
        kids.push(el('button',{class:'btn primary',style:'width:100%;justify-content:center;margin-top:10px;padding:11px',id:'startBtn',onclick:()=>startQuiz(id,1,'practice')},`Start Round 1 quiz · ${n} questions`));
        kids.push(el('div',{class:'kv',style:'margin-top:6px',text:'A practice quiz, not a mastery challenge — available any time. Finish it to color the skill in as Practiced.'}));
      }else{
        kids.push(el('button',{class:'btn hot',style:'width:100%;justify-content:center;margin-top:10px;padding:11px',id:'startBtn',onclick:()=>startQuiz(id,nextR,'challenge')},`Start mastery challenge → ${TIERS[nextR]} · ${n} questions`));
        kids.push(el('div',{class:'kv',style:'margin-top:6px',text:`Get at least ${need(n)} of ${n} right to level up. If you miss, you keep your tier — no penalty, retry any time.`}));
      }
    }else{
      kids.push(el('div',{class:'note ok',text:'Mastered! This skill is fully colored in.'}));
      if(hasRound(id,4))kids.push(el('button',{class:'btn',style:'width:100%;justify-content:center',id:'startBtn',onclick:()=>startQuiz(id,4,'review')},'Review round 4 (no tier change)'));
    }
  }
  kids.push(el('h3',{text:'Prerequisites'}));
  kids.push(s.prereqs.length?el('div',{class:'chips',id:'prereqChips'},s.prereqs.map(tierPill)):el('div',{class:'kv',text:'None — a starting point.'}));
  const deps=dependents[id];
  kids.push(el('h3',{text:'Leads to'}));
  kids.push(deps.length?el('div',{class:'chips'},deps.map(tierPill)):el('div',{class:'kv',text:'Nothing yet in this draft tree.'}));
  const hist=(progress.skills[id]&&progress.skills[id].history||[]).slice(-6).reverse();
  if(hist.length){kids.push(el('h3',{text:'Recent attempts'}));
    kids.push(el('div',{class:'hist'},hist.map(h=>el('div',{},`Round ${h.round}: ${h.correct}/${h.total} · `,el('span',{class:h.passed?'p':'f',text:h.round===1?'completed':(h.passed?'passed':'not yet')}),` · ${fmtDate(h.t)}`))))}
  panel.append(...kids);
  panel.scrollTop=0;
}

/* ====================== quiz ====================== */
const quizEl=$('quiz');
let quiz=null;
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
const POSITIONAL=/(all|none|both|neither) of the (above|these|options)|none of these|all of these/i;
function prepareQ(q){
  const p={q,chosen:null,text:'',correct:null,done:false};
  if(q.type==='mc'){
    let perm=q.options.map((_,i)=>i);
    if(!q.options.some(o=>POSITIONAL.test(o)))perm=shuffle(perm);
    p.perm=perm;p.opts=perm.map(i=>q.options[i]);p.ci=perm.indexOf(q.correct_index);
  }
  return p;
}
function startQuiz(id,round,mode){
  const qs=roundQs(id,round);if(!qs.length)return;
  quiz={id,round,mode,items:qs.map(prepareQ),i:0,result:null,t0:Date.now()};
  quizOpen=true;quizEl.classList.add('open');document.body.style.overflow='hidden';
  closeModal();renderPanel();renderQuiz();
  if(panelOpen()){panel.classList.remove('open');panel.setAttribute('aria-hidden','true')}
}
function parseNum(s){
  if(s==null)return NaN;
  s=String(s).trim().replace(/[\u2212\u2013\u2014]/g,'-').replace(/,/g,'').replace(/\s+/g,'').replace(/%$/,'');
  if(!s)return NaN;
  let m=s.match(/^([+-]?(?:\d+\.?\d*|\.\d+))(?:[eE]([+-]?\d+))?$/);
  if(m)return parseFloat(m[1]+(m[2]?'e'+m[2]:''));
  m=s.match(/^([+-]?(?:\d+\.?\d*|\.\d+))[x×*·]10\^?\(?([+-]?\d+)\)?$/i);
  if(m)return parseFloat(m[1]+'e'+m[2]);
  m=s.match(/^([+-]?\d+\.?\d*)\/(\d+\.?\d*)$/);
  if(m&&parseFloat(m[2])!==0)return parseFloat(m[1])/parseFloat(m[2]);
  return NaN;
}
function checkNumeric(q,txt){
  const x=parseNum(txt);if(!Number.isFinite(x))return null;
  const a=q.answer,tol=(q.tolerance!=null?q.tolerance:0.02);
  if(a===0)return Math.abs(x)<=1e-6;
  return Math.abs(x-a)<=tol*Math.abs(a)*(1+1e-9);
}
function fmtAns(a){
  if(a===0)return '0';
  const ab=Math.abs(a);
  if(ab>=1e6||ab<1e-3){const [m,e]=a.toExponential(3).split('e');return m.replace(/\.?0+$/,'')+'×10^'+Number(e)}
  return String(Number(a.toPrecision(6)));
}
const answerLine=it=>it.q.type==='mc'?`Answer: ${'ABCD'[it.ci]}. ${it.opts[it.ci]}`:`Answer: ${fmtAns(it.q.answer)}${it.q.unit&&it.q.unit!=='(unitless)'?' '+it.q.unit:''}`;
function renderQuiz(){
  const Q=quiz;if(!Q)return;
  const s=byId[Q.id];quizEl.style.cssText=colorVars(s.chapter);quizEl.innerHTML='';
  const wrap=el('div',{class:'qwrap'});quizEl.append(wrap);
  const label=Q.round===1?'Round 1 · Practice quiz':`Round ${Q.round} · Mastery challenge → ${TIERS[Q.round]}`;
  wrap.append(el('div',{class:'qtop'},
    el('button',{class:'btn small',onclick:leaveQuiz,id:'qLeave'},'← Leave'),
    el('h2',{text:s.name}),
    el('span',{class:'rbadge',id:'rbadge',text:Q.mode==='review'?'Review · no tier change':label})));
  if(Q.result){renderResult(wrap);quizEl.scrollTop=0;return}
  const n=Q.items.length;
  wrap.append(el('div',{class:'prog',role:'img','aria-label':`Question ${Q.i+1} of ${n}`},Q.items.map((it,i)=>el('i',{class:it.done?(it.correct?'ok':'no'):(i===Q.i?'cur':'')}))));
  if(Q.mode==='challenge')wrap.append(el('div',{class:'kv',id:'rule',style:'margin:-6px 0 10px',text:`Mastery challenge: get at least ${need(n)} of ${n} right to reach ${TIERS[Q.round]}. Missing it never costs you a tier.`}));
  else if(Q.mode==='practice')wrap.append(el('div',{class:'kv',id:'rule',style:'margin:-6px 0 10px',text:'Practice quiz (not a mastery challenge): finish all questions to color this skill in as Practiced.'}));
  const it=Q.items[Q.i],q=it.q;
  const card=el('div',{class:'qcard'});
  card.append(el('div',{class:'qn',text:`Question ${Q.i+1} of ${n}`}),figureNode(q),el('p',{class:'qp',math:q.prompt,id:'qPrompt','data-qid':q.id}));
  if(q.type==='mc'){
    const box=el('div',{class:'opts',role:'group','aria-labelledby':'qPrompt'});
    it.opts.forEach((o,i)=>{
      let cls='opt';
      if(it.done){if(i===it.ci)cls+=' right';else if(i===it.chosen)cls+=' wrong'}else if(i===it.chosen)cls+=' sel';
      box.append(el('button',{class:cls,type:'button',disabled:it.done,'data-i':i,'data-o':it.perm?it.perm[i]:i,onclick:()=>answerMC(i)},el('span',{class:'k',text:'ABCD'[i]}),el('span',{class:'ot',math:o})));
    });
    card.append(box);
  }else{
    const inp=el('input',{type:'text',id:'numIn',autocomplete:'off',spellcheck:'false',placeholder:'Type a number',disabled:it.done,'aria-label':'Your answer'+(q.unit?' in '+mathPlain(q.unit):'')});
    inp.value=it.text;inp.addEventListener('input',()=>it.text=inp.value);
    inp.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();answerNum()}});
    card.append(el('div',{class:'numrow'},inp,q.unit&&q.unit!=='(unitless)'?el('span',{class:'u',math:q.unit}):null,el('button',{class:'btn primary',id:'checkBtn',disabled:it.done,onclick:answerNum},'Check')));
    if(!it.done){card.append(el('div',{class:'kv',style:'margin-top:8px',text:`Plain numbers or scientific notation (like 2.5e-3) work. Accepted within ±${((q.tolerance!=null?q.tolerance:.02)*100).toFixed(0)}%.`}));setTimeout(()=>inp.focus(),0)}
  }
  if(it.done){
    const ok=it.correct;
    const fb=el('div',{class:'fb '+(ok?'ok':'no'),role:'status',id:'feedback'});
    fb.append(el('h4',{text:ok?'✓ Correct!':'✗ Not quite'}),el('div',{class:'ans',math:answerLine(it)}),el('div',{class:'ex',math:q.explanation||''}));
    card.append(fb);
    if(Q.round===4&&q.preview&&q.preview.length){
      card.append(el('div',{class:'coming',id:'coming'},el('b',{text:'Coming up: '}),'this skill feeds into ',
        q.preview.map((p,i)=>[i?', ':'',el('button',{class:'pill',style:colorVars(byId[p].chapter),onclick:()=>selectSkill(p,false),title:'Open this skill'},byId[p].name)])));
    }
    card.append(el('div',{class:'qact'},el('button',{class:'btn primary',id:'nextBtn',onclick:nextQ},Q.i===n-1?'See results':'Next question →')));
  }
  wrap.append(card);
  if(it.done){const nb=$('nextBtn');nb&&nb.focus({preventScroll:true});setTimeout(()=>{const f=card.querySelector('.fb');f&&f.scrollIntoView({block:'nearest',behavior:'smooth'})},50)}
}
function answerMC(i){
  const it=quiz.items[quiz.i];if(it.done)return;
  it.chosen=i;it.done=true;it.correct=(i===it.ci);renderQuiz();
}
function answerNum(){
  const it=quiz.items[quiz.i];if(it.done)return;
  const r=checkNumeric(it.q,it.text);
  if(r===null){const inp=$('numIn');inp.setAttribute('aria-invalid','true');toast('Enter a number first (like 12.5 or 1e-3).');inp.focus();return}
  it.done=true;it.correct=r;renderQuiz();
}
function nextQ(){
  if(quiz.i<quiz.items.length-1){quiz.i++;renderQuiz();quizEl.scrollTop=0;return}
  finishQuiz();
}
function finishQuiz(){
  const Q=quiz,n=Q.items.length,correct=Q.items.filter(i=>i.correct).length;
  const passed=Q.round===1?true:correct>=need(n);
  const before=tierOf(Q.id);let after=before;
  if(Q.mode!=='review'){
    const rec=sk(Q.id),now=Date.now();
    rec.history.push({t:now,round:Q.round,correct,total:n,passed});if(rec.history.length>60)rec.history.splice(0,rec.history.length-60);
    rec.lastPracticed=now;
    if(passed&&rec.tier<Q.round)rec.tier=Q.round;
    after=rec.tier;
    saveProgress();
    recordTiming(Q.round===1?'practice':'challenge',(Date.now()-Q.t0)/1000);   /* time from opening this quiz to its last answer (under 20 s ignored, capped at 30 min) */
  }
  Q.result={correct,n,passed,before,after};
  refreshAll();
  if(after>before){
    document.querySelectorAll(`.tile[data-id="${Q.id}"]`).forEach(t=>{t.classList.add('pop');setTimeout(()=>t.classList.remove('pop'),900)});
    confetti();
  }
  renderQuiz();
}
function renderResult(wrap){
  const Q=quiz,R=Q.result;
  const up=R.after>R.before;
  const card=el('div',{class:'qcard result'});
  const msg=Q.mode==='review'?'Review done':up?(R.after===4?'Mastered! ★':`Level up! You’re now ${TIERS[R.after]}`):(Q.round===1?'Done':'Not this time — and that’s fine');
  card.append(el('div',{class:'qn',text:Q.mode==='review'?'Review':(Q.round===1?'Practice quiz complete':'Mastery challenge result')}));
  card.append(el('div',{class:'big',id:'score',text:`${R.correct} / ${R.n}`}));
  card.append(el('h3',{style:'margin:0 0 6px;font-size:21px',id:'resMsg',text:msg}));
  if(Q.mode==='challenge'&&!R.passed)card.append(el('div',{class:'kv',id:'failNote',text:`You needed ${need(R.n)} of ${R.n}. Your tier stays at ${TIERS[R.before]} — read the explanations below and try again whenever you’re ready.`}));
  if(Q.mode==='practice'&&R.correct<need(R.n))card.append(el('div',{class:'kv',text:'Practiced is about showing up — but the explanations below are worth another look before you try a mastery challenge.'}));
  if(Q.mode!=='review'){
    card.append(el('div',{class:'tu'},el('span',{class:'tierchip',text:TIERS[R.before]}),up?[el('span',{text:'→'}),el('span',{class:'tierchip',id:'newTier',text:TIERS[R.after]})]:el('span',{style:'font-weight:600;color:var(--ink2)',text:'(unchanged)'})));
    card.append(el('div',{class:'kv',text:storageOK?'Progress saved on this device ✓':'Progress kept in memory only (storage unavailable) — please Export a backup.'}));
  }
  const recap=el('div',{class:'recap'});
  Q.items.forEach((it,i)=>recap.append(el('div',{},el('span',{class:'m '+(it.correct?'ok':'no'),text:it.correct?'✓':'✗'}),el('span',{math:`Q${i+1}: `+shortMath(it.q.prompt,150)}))));
  card.append(recap);
  const btns=el('div',{class:'rbtns'});
  btns.append(el('button',{class:'btn',id:'resBack',onclick:()=>exitQuiz(Q.id)},'Back to the tree'));
  if(Q.mode==='review'||(Q.mode==='challenge'&&!R.passed)||(Q.mode==='practice'&&R.correct<need(R.n)))btns.append(el('button',{class:'btn',id:'resRetry',onclick:()=>startQuiz(Q.id,Q.round,Q.mode)},'Try this round again'));
  const qn=queue().filter(x=>x.id!==Q.id)[0];
  const rd=skills.filter(x=>isReady(x.id))[0];
  if(qn)btns.append(el('button',{class:'btn hot',id:'resNextQ',onclick:()=>startQuiz(qn.id,tierOf(qn.id)+1,'challenge')},`Next in queue: ${short(qn.name,30)}`));
  if(rd&&up)btns.append(el('button',{class:'btn primary',id:'resLearn',onclick:()=>exitQuiz(rd.id)},`Learn something new: ${short(rd.name,26)}`));
  const t=tierOf(Q.id);
  if(up&&t<4&&hasRound(Q.id,t+1))btns.append(el('button',{class:'btn',id:'resSame',onclick:()=>startQuiz(Q.id,t+1,'challenge')},'Challenge this skill again now'));
  card.append(btns);
  if(up&&Q.mode!=='review')card.append(el('div',{class:'kv',style:'margin-top:12px',text:'Tip: spaced practice works best. Go learn something new, and this skill will wait in your mastery queue.'}));
  wrap.append(card);
  const ex=el('div',{style:'margin-top:18px'});
  ex.append(el('h3',{style:'margin:0 0 8px;font-size:14px;color:var(--ink2)',text:'Explanations'}));
  Q.items.forEach((it,i)=>ex.append(el('details',{style:'background:#fff;border-radius:14px;padding:10px 14px;margin:8px 0;border:2px solid var(--line)',open:it.correct?null:true},
    el('summary',{style:'cursor:pointer;font-weight:650'},`${it.correct?'✓':'✗'} Q${i+1}`),
    figureNode(it.q,'small'),el('p',{class:'qp',style:'font-size:14px;margin:8px 0',math:it.q.prompt}),
    el('div',{style:'font-weight:700',math:answerLine(it)}),
    el('div',{class:'ex',style:'white-space:pre-wrap;font-size:13.5px',math:it.q.explanation||''}))));
  wrap.append(ex);
}
function closeQuizUI(){quiz=null;quizOpen=false;quizEl.classList.remove('open');quizEl.innerHTML='';document.body.style.overflow=''}
function exitQuiz(id){closeQuizUI();selectSkill(id,true)}
function leaveQuiz(){
  if(quiz&&quiz.result){exitQuiz(quiz.id);return}
  openModal({title:'Leave this quiz?',body:el('p',{text:'Your answers in this attempt won’t be saved, and your tier stays as it is.'}),actions:[{label:'Keep going'},{label:'Leave quiz',kind:'danger',id:'confirmLeave',onClick:()=>{const id=quiz.id;closeQuizUI();selectSkill(id,false)}}]});
}
function confetti(){
  if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;
  for(let i=0;i<46;i++){
    const d=el('i',{class:'conf',style:`left:${Math.random()*100}vw;background:${PALETTE[i%PALETTE.length]};animation-duration:${1.6+Math.random()*1.6}s;animation-delay:${Math.random()*.4}s;border-radius:${Math.random()>.5?'50%':'2px'}`});
    document.body.append(d);setTimeout(()=>d.remove(),4000);
  }
}

/* ====================== modal / queue ====================== */
const mb=$('modalBack'),mEl=$('modal');
let modalFocusBack=null;
function openModal({title,body,actions,wide}){
  modalFocusBack=document.activeElement;
  mEl.innerHTML='';mEl.classList.toggle('wide',!!wide);mEl.append(el('h2',{text:title}),body);
  const acts=el('div',{class:'acts'});
  (actions||[{label:'Close'}]).forEach(a=>acts.append(el('button',{class:'btn '+(a.kind||''),id:a.id||null,onclick:()=>{closeModal();a.onClick&&a.onClick()}},a.label)));
  mEl.append(acts);mb.classList.add('open');
  const f=mEl.querySelector('.acts .btn.primary,.acts .btn.hot')||mEl.querySelector('.acts .btn');f&&f.focus();
}
function closeModal(){if(!mb.classList.contains('open'))return;mb.classList.remove('open');mEl.innerHTML='';try{modalFocusBack&&modalFocusBack.focus&&modalFocusBack.focus()}catch(e){}}
mb.addEventListener('mousedown',e=>{if(e.target===mb)closeModal()});
function openQueue(){
  const q=queue();
  const body=el('div',{id:'queueBody'});
  body.append(el('p',{text:'These skills are Practiced or higher but not yet Mastered. The one you practiced least recently comes first — spacing your reviews out is what makes learning stick. Missing a challenge never drops your tier.'}));
  if(!q.length)body.append(el('div',{class:'note info',text:'Nothing waiting yet. Finish a Round 1 quiz on any skill to start a queue.'}));
  q.forEach((s,i)=>{
    const t=tierOf(s.id);
    body.append(el('div',{class:'qrow'+(i===0?' top':''),'data-id':s.id,style:colorVars(s.chapter)},
      el('span',{class:'rk',text:i+1}),el('span',{class:'dotc'}),
      el('span',{class:'nm'},s.name,el('div',{class:'sm',text:`${TIERS[t]} → ${TIERS[t+1]} · last practiced ${ago(lastOf(s.id))}`})),
      el('button',{class:'btn small '+(i===0?'hot':''),onclick:()=>{closeModal();startQuiz(s.id,t+1,'challenge')}},i===0?'Start top challenge':'Start')));
  });
  const ready=skills.filter(s=>isReady(s.id));
  if(ready.length)body.append(el('div',{class:'note info'},el('b',{text:'Breadth first: '}),`${ready.length} new skill${ready.length>1?'s are':' is'} ready to learn. Picking up a new one now gives your queued skills time to sink in.`));
  openModal({title:'Mastery challenges',body,actions:[{label:'Close'}]});
}
function openHelp(){
  const ul=el('ul',{},
    el('li',{},el('b',{text:'Five tiers: '}),'Unpracticed → Practiced → Level 1 → Level 2 → Mastered. Tiles fill with their chapter’s color as you climb.'),
    el('li',{},el('b',{text:'Round 1 '}),'is a short practice quiz (not a mastery challenge). Finish it to become Practiced.'),
    el('li',{},el('b',{text:'Rounds 2–4 '}),'are mastery challenges: 3 questions, get at least 2 right to move up. Round 2 is harder, round 3 hunts for gotchas, round 4 applies the skill to what comes next.'),
    el('li',{},'Missing a challenge never costs a tier. Retry any time.'),
    el('li',{},'The mastery queue lists unmastered skills, least recently practiced first. Learn broadly first; come back for mastery.'),
    el('li',{},'Prerequisites are guidance, not locks. A new skill glows “ready” once all its prerequisites are at Level 2 or Mastered (prerequisites that are still coming soon are ignored). Lines show what leads to what; click a tile to highlight them.'),
    el('li',{},el('b',{text:'The tree grows upward: '}),'foundations (skills with no prerequisites) sit at the bottom and each skill that builds on them sits above.'),
    el('li',{},el('b',{text:'Learning plan '}),'simulates sessions (practice every ready skill, one mastery challenge per unmastered skill) to estimate how many sessions and how much time it takes to master everything playable. It learns how fast you are from your own timed quizzes.'),
    el('li',{},el('b',{text:'Group by chapter '}),'regroups the one big prerequisite tree into chapter blocks, and Ungroup flows it back.'),
    el('li',{},'Progress autosaves in this browser after every quiz. Use Export for a backup file you can Import later (or on another device).'),
    el('li',{},'Content: EE 105 (Niknejad reader), draft. Only some skills have questions so far; the rest say “coming soon”.'));
  openModal({title:'How Skillgrove works',body:ul,actions:[{label:'Got it',kind:'primary'}]});
}

/* ====================== learning plan (course simulation) ====================== */
const TKEY='skilltree.timing.v1';   /* quiz-duration samples; deliberately NOT part of the progress key/format */
const Sim=window.SkillSim;
let timing=Sim.normalizeTiming(null);
function loadTiming(){try{const r=localStorage.getItem(TKEY);if(r)timing=Sim.normalizeTiming(JSON.parse(r))}catch(e){}}
function saveTiming(){if(!storageOK)return;try{localStorage.setItem(TKEY,JSON.stringify(timing))}catch(e){}}
function recordTiming(kind,seconds){
  const r=Sim.addSample(timing[kind],seconds,Date.now());
  if(r.added){timing[kind]=r.list;saveTiming()}
  return r.added;
}
const planState={scratch:false,open:null};
function planGraph(){
  const ids=playable.map(s=>s.id),prereqs={},maxTier={};
  ids.forEach(id=>{prereqs[id]=byId[id].prereqs.slice();let t=0;while(hasRound(id,t+1))t++;maxTier[id]=t});
  return {ids,prereqs,maxTier};
}
function planEstimates(){
  const out={};
  [['practice','practice'],['challenge','challenge']].forEach(([k])=>{
    const e=Sim.estimate(timing[k]),ov=timing.override[k];
    out[k]={measured:e,used:ov!=null?ov:e.minutes,overridden:ov!=null};
  });
  return out;
}
function runPlan(scratch){
  const g=planGraph(),start={};
  if(!scratch)g.ids.forEach(id=>start[id]=tierOf(id));
  const est=planEstimates();
  return Sim.simulate(g,start,{practiceMin:est.practice.used,challengeMin:est.challenge.used});
}
function renderPlanBadge(){
  const b=$('planCount');if(!b)return;
  const r=runPlan(false);
  b.textContent=r.ok?(r.sessions?r.sessions:'✓'):'?';
  $('btnPlan').title=r.ok?(r.sessions?`About ${r.sessions} more learning session${r.sessions===1?'':'s'} (~${Sim.fmtDuration(r.totalMinutes)}) to master the ${r.scope} playable skills — click for the plan`:`All ${r.scope} playable skills are mastered — nothing left to plan`):'Learning plan';
}
const TIER_COL=['#d5dae6','#ffd36b','#8bd36b','#3cb6c9','#7c6cff'];
const SVGNS='http://www.w3.org/2000/svg';
function sv(tag,attrs,...kids){const e=document.createElementNS(SVGNS,tag);for(const k in attrs||{})e.setAttribute(k,attrs[k]);kids.flat().forEach(c=>{if(c!=null)e.append(typeof c==='string'?document.createTextNode(c):c)});return e}
function fmtMin(m){return Sim.fmtDuration(m)}
function minuteChart(r){
  const W=660,H=210,L=44,R=48,T=14,B=34,n=r.rows.length;
  const nice=m=>4*([5,10,15,20,25,30,40,50,60,75,100,125,150,200,250,300,400,500,750,1000].find(v=>v*4>=m)||2000);
  const maxM=Math.max(10,...r.rows.map(x=>x.minutes)),maxC=nice(Math.max(1,r.totalMinutes));
  const niceMax=nice(maxM),bw=Math.min(34,(W-L-R)/n*.72),step=(W-L-R)/n;
  const y=v=>T+(H-T-B)*(1-v/niceMax),yc=v=>T+(H-T-B)*(1-v/maxC);
  const svg=sv('svg',{viewBox:`0 0 ${W} ${H}`,width:'100%',role:'img',id:'minChart','aria-label':`Minutes per session across ${n} sessions, total ${fmtMin(r.totalMinutes)}`,style:'max-width:'+W+'px;display:block'});
  for(let g=0;g<=4;g++){const v=niceMax*g/4;svg.append(sv('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),stroke:'#e6eaf2'}),sv('text',{x:L-6,y:y(v)+4,'text-anchor':'end','font-size':10,fill:'#8a93a7'},String(Math.round(v))));
    const c=maxC*g/4;svg.append(sv('text',{x:W-R+6,y:yc(c)+4,'font-size':10,fill:'#c2542f'},String(Math.round(c))))}
  svg.append(sv('text',{x:L-6,y:8,'text-anchor':'end','font-size':9.5,fill:'#8a93a7'},'min'),sv('text',{x:W-R+6,y:8,'font-size':9.5,fill:'#c2542f'},'total'));
  const pts=[];
  r.rows.forEach((row,i)=>{
    const cx=L+step*(i+.5),pm=row.practiced.length*r.practiceMin,cm=row.challenges.length*r.challengeMin;
    svg.append(sv('rect',{x:cx-bw/2,y:y(pm+cm),width:bw,height:Math.max(0,y(0)-y(pm+cm)),fill:'#ff9f43',rx:3},sv('title',{},`Session ${row.n}: ${fmtMin(row.minutes)} (${row.practiced.length} new × ${r.practiceMin} min + ${row.challenges.length} challenges × ${r.challengeMin} min)`)));
    if(pm>0)svg.append(sv('rect',{x:cx-bw/2,y:y(pm),width:bw,height:y(0)-y(pm),fill:'#7c6cff',rx:3}));
    if(n<=26||row.n%2===1)svg.append(sv('text',{x:cx,y:H-B+14,'text-anchor':'middle','font-size':10,fill:'#4b566b'},String(row.n)));
    pts.push([cx,yc(row.cumulative)]);
  });
  svg.append(sv('polyline',{points:pts.map(p=>p.join(',')).join(' '),fill:'none',stroke:'#c2542f','stroke-width':2,'stroke-dasharray':'5 3'}));
  pts.forEach(p=>svg.append(sv('circle',{cx:p[0],cy:p[1],r:2.6,fill:'#c2542f'})));
  svg.append(sv('text',{x:(L+W-R)/2,y:H-4,'text-anchor':'middle','font-size':10.5,fill:'#4b566b'},'Session number'));
  return svg;
}
function tierChart(r){
  const W=660,H=200,L=44,R=14,T=12,B=34,cols=[{n:0,tiers:r.startCounts}].concat(r.rows.map(x=>({n:x.n,tiers:x.tiers}))),k=cols.length;
  const step=(W-L-R)/k,bw=Math.min(30,step*.74),tot=r.scope||1;
  const svg=sv('svg',{viewBox:`0 0 ${W} ${H}`,width:'100%',role:'img',id:'tierChart','aria-label':'Number of skills at each tier after each session',style:'max-width:'+W+'px;display:block'});
  const y=v=>T+(H-T-B)*(1-v/tot);
  for(let g=0;g<=4;g++){const v=Math.round(tot*g/4);svg.append(sv('line',{x1:L,x2:W-R,y1:y(v),y2:y(v),stroke:'#e6eaf2'}),sv('text',{x:L-6,y:y(v)+4,'text-anchor':'end','font-size':10,fill:'#8a93a7'},String(v)))}
  cols.forEach((c,i)=>{
    const cx=L+step*(i+.5);let acc=0;
    for(let t=4;t>=0;t--){const v=c.tiers[t];if(!v)continue;
      svg.append(sv('rect',{x:cx-bw/2,y:y(acc+v),width:bw,height:y(acc)-y(acc+v),fill:TIER_COL[t],stroke:'#fff','stroke-width':.6},sv('title',{},`${i===0?'Start':'After session '+c.n}: ${v} skill${v===1?'':'s'} at ${TIERS[t]}`)));acc+=v}
    if(k<=27||i%2===0)svg.append(sv('text',{x:cx,y:H-B+14,'text-anchor':'middle','font-size':10,fill:'#4b566b'},i===0?'start':String(c.n)));
  });
  svg.append(sv('text',{x:(L+W-R)/2,y:H-4,'text-anchor':'middle','font-size':10.5,fill:'#4b566b'},'After session'));
  return svg;
}
function planResults(box){
  box.innerHTML='';
  const r=runPlan(planState.scratch);
  if(!r.ok){box.append(el('div',{class:'note warn',id:'planStuck',text:'The simulation got stuck: some skill can never become ready. This should not happen — please tell Isaac.'}));return}
  const est=planEstimates();
  if(!r.sessions){
    box.append(el('div',{class:'note ok',id:'planDone'},el('b',{text:'0 sessions. '}),`All ${r.scope} playable skills are already Mastered, so there is nothing left to plan. The total will grow when more question banks are added.`));
    return;
  }
  box.append(el('div',{class:'pcards',id:'planCards'},
    el('div',{class:'pc'},el('div',{class:'pn',id:'planSessions',text:r.sessions}),el('div',{class:'pl',text:r.sessions===1?'learning session':'sequential learning sessions'})),
    el('div',{class:'pc'},el('div',{class:'pn',id:'planTotal',text:fmtMin(r.totalMinutes)}),el('div',{class:'pl',text:'total study time'})),
    el('div',{class:'pc'},el('div',{class:'pn sm',id:'planWork',text:`${r.practiceCount} + ${r.challengeCount}`}),el('div',{class:'pl',text:'practice quizzes + mastery challenges'}))));
  const names=r.critical.chain.map(id=>byId[id].name);
  const cp=el('div',{class:'cpath',id:'planCritical'},el('b',{text:'Critical path: '}));
  if(names.length){
    names.forEach((n,i)=>{if(i)cp.append(el('span',{class:'arr',text:' ↑ '}));cp.append(el('span',{class:'cpn',text:n}))});
    cp.append(el('div',{class:'kv',style:'margin-top:5px'},names.length>1
      ?`${names.length} skills deep. A skill can only be practiced in the session after all its prerequisites reached Level 2, and a skill needs 3 more sessions after practice to climb Level 1 → Level 2 → Mastered (one step per session so the spacing sinks in)`+(r.sessions===3*names.length+1?`. That is why the plan takes 3 × ${names.length} + 1 = ${r.sessions} sessions: more study time per session wouldn’t shorten it, only a shallower chain would.`:'.')
      :`This is just the remaining challenges on a single skill (one step up per session).`));
  }
  box.append(cp);
  box.append(el('h3',{class:'ph',text:'Minutes per session'}),minuteChart(r),
    el('div',{class:'lgd'},el('span',{},el('i',{style:'background:#7c6cff'}),'new-skill practice'),el('span',{},el('i',{style:'background:#ff9f43'}),'mastery challenges'),el('span',{},el('i',{style:'background:#c2542f;height:3px;border-radius:2px'}),'cumulative total (right axis)')));
  box.append(el('h3',{class:'ph',text:'Skills at each tier after each session'}),tierChart(r),
    el('div',{class:'lgd'},TIERS.map((n,t)=>el('span',{},el('i',{style:`background:${TIER_COL[t]}`}),n))));
  box.append(el('h3',{class:'ph',text:'Session by session'}));
  const tb=el('table',{class:'ptab',id:'planTable'},el('thead',{},el('tr',{},['#','New skills practiced','Challenges','Session','Total so far','Tiers after (Unp · Pra · L1 · L2 · Mas)'].map(h=>el('th',{text:h})))));
  const body=el('tbody');
  r.rows.forEach(row=>{
    const open=planState.open===row.n;
    const sums=row.tiers.map((v,t)=>v?el('span',{style:`flex:${v};background:${TIER_COL[t]}`,title:`${v} at ${TIERS[t]}`}):null);
    body.append(el('tr',{class:'prow'+(open?' open':''),'data-n':row.n,tabindex:'0',role:'button','aria-expanded':String(open),title:'Click to list the skills',onclick:()=>{planState.open=planState.open===row.n?null:row.n;planResults(box)},onkeydown:e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();e.currentTarget.click()}}},
      el('td',{text:row.n}),el('td',{text:row.practiced.length?String(row.practiced.length):'–'}),el('td',{text:row.challenges.length?String(row.challenges.length):'–'}),el('td',{text:fmtMin(row.minutes)}),el('td',{text:fmtMin(row.cumulative)}),
      el('td',{},el('div',{class:'mini'},sums),el('span',{class:'mt',text:row.tiers.join(' · ')}))));
    if(open){
      body.append(el('tr',{class:'pdet'},el('td',{colspan:6},
        row.practiced.length?el('div',{},el('b',{text:'Practice (Round 1): '}),row.practiced.map(id=>byId[id].name).join('; ')):null,
        row.challenges.length?el('div',{},el('b',{text:'Mastery challenges: '}),row.challenges.map(c=>`${byId[c.id].name} (${TIERS[c.from]} → ${TIERS[c.to]})`).join('; ')):null)));
    }
  });
  tb.append(body);box.append(el('div',{class:'ptabwrap'},tb));
}
function estimateCaption(k,label){
  const e=planEstimates()[k],m=e.measured;
  const unit=k==='practice'?'new-skill practice quiz':'mastery challenge';
  if(e.overridden)return `Using your typed value: ${e.used} min per ${unit}. (${m.source==='measured'?`Your measured average is ${m.minutes} min from ${m.n} sample${m.n===1?'':'s'}`:`No measured average yet — ${m.n} of ${m.need} timed quizzes so far, default ${Sim.DEFAULT_MIN} min`}.)`;
  if(m.source==='measured')return `Using your average: ${m.minutes} min per ${unit} (${m.n} samples).`;
  return `Using default ${Sim.DEFAULT_MIN} min per ${unit}. Your own average replaces it after ${m.need} timed quizzes (${m.n} so far).`;
}
function openPlan(){
  const body=el('div',{id:'planBody'});
  const results=el('div',{id:'planResults'});
  const refreshNotes=()=>{
    $('estNoteP').textContent=estimateCaption('practice');$('estNoteC').textContent=estimateCaption('challenge');
    $('estResetP').hidden=!timing.override.practice;$('estResetC').hidden=!timing.override.challenge;
  };
  body.append(el('p',{class:'pintro',text:'Each simulated learning session: practice every skill that is ready (all its prerequisites at Level 2 or Mastered), and take one mastery challenge on every skill that is practiced but not yet mastered. A skill moves up one step per session — so it never jumps ahead within a session — and we repeat until everything is Mastered.'}));
  body.append(el('div',{class:'note info',id:'planScope'},el('b',{text:'Scope: '}),`only the ${playable.length} playable skills (the ones with questions written) are simulated. The other ${skills.length-playable.length} “coming soon” skills are excluded, so these totals will grow as more question banks are added.`));
  const seg=el('div',{class:'seg',role:'group','aria-label':'Where the simulation starts'},
    el('button',{id:'planCur','aria-pressed':String(!planState.scratch),onclick:()=>setScratch(false)},'From my progress'),
    el('button',{id:'planScr','aria-pressed':String(planState.scratch),onclick:()=>setScratch(true)},'Start from scratch'));
  const setScratch=v=>{planState.scratch=v;planState.open=null;$('planCur').setAttribute('aria-pressed',String(!v));$('planScr').setAttribute('aria-pressed',String(v));$('planStartNote').textContent=v?'Pretending every playable skill is Unpracticed. Your real progress is not touched.':`Starting from your saved progress (${playable.filter(s=>tierOf(s.id)>0).length} of ${playable.length} playable skills already practiced).`;planResults(results)};
  body.append(el('div',{class:'prow2'},seg,el('span',{class:'kv',id:'planStartNote',style:'margin:0'})));
  const mkInp=(k,idIn,idNote,idReset,label)=>{
    const inp=el('input',{type:'number',id:idIn,min:'0.5',max:'600',step:'0.5','aria-label':label});
    const e=planEstimates()[k];inp.value=String(e.used);
    inp.addEventListener('input',()=>{const v=parseFloat(inp.value);if(isFinite(v)&&v>0&&v<=600){timing.override[k]=v;saveTiming();refreshNotes();planResults(results);renderPlanBadge()}});
    const reset=el('button',{class:'btn small',id:idReset,type:'button',onclick:()=>{timing.override[k]=null;saveTiming();inp.value=String(planEstimates()[k].used);refreshNotes();planResults(results);renderPlanBadge()}},'Use my average / default');
    return el('div',{class:'est'},el('label',{for:idIn,text:label}),el('div',{class:'er'},inp,el('span',{text:'min'}),reset),el('div',{class:'kv',id:idNote,style:'margin:2px 0 0'}));
  };
  body.append(el('div',{class:'ests'},mkInp('practice','estPractice','estNoteP','estResetP','Minutes per new-skill practice quiz'),mkInp('challenge','estChallenge','estNoteC','estResetC','Minutes per mastery challenge')));
  body.append(results);
  openModal({title:'Learning plan — how many sessions to master everything?',body,actions:[{label:'Close',kind:'primary'}],wide:true});
  refreshNotes();setScratch(planState.scratch);
}

/* ====================== export / import / reset ====================== */
function exportProgress(){
  const out={version:1,app:'skillgrove',exportedAt:new Date().toISOString(),skills:progress.skills,timing:{practice:timing.practice,challenge:timing.challenge}};   /* "timing" is optional on import */
  const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
  const a=el('a',{href:URL.createObjectURL(blob),download:`skillgrove-progress-${new Date().toISOString().slice(0,10)}.json`});
  document.body.append(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500);
  toast('Progress exported.');
}
function importFile(file){
  const r=new FileReader();
  r.onerror=()=>toast('Could not read that file.');
  r.onload=()=>{
    let raw;try{raw=JSON.parse(r.result)}catch(e){openModal({title:'Import failed',body:el('p',{id:'impErr',text:'That file isn’t valid JSON.'}),actions:[{label:'OK'}]});return}
    const p=normalizeProgress(raw);
    if(!p){openModal({title:'Import failed',body:el('p',{id:'impErr',text:'That doesn’t look like a Skillgrove progress file (expected version 1 with a “skills” object).'}),actions:[{label:'OK'}]});return}
    const ids=Object.keys(p.skills),known=ids.filter(i=>byId[i]),unknown=ids.length-known.length;
    const impT=(raw.timing&&typeof raw.timing==='object')?Sim.normalizeTiming(raw.timing):null;   /* optional field: older exports simply don't have it */
    const nT=impT?impT.practice.length+impT.challenge.length:0;
    const body=el('div',{},el('p',{text:`The file has progress for ${known.length} skill${known.length===1?'':'s'}`+(unknown?` (${unknown} unknown skill id${unknown>1?'s':''} will be kept but not shown)`:'')+(nT?` and ${nT} quiz-timing sample${nT===1?'':'s'}`:'')+'.'}),
      el('p',{},el('b',{text:'Merge'}),' keeps the higher tier and latest practice time for each skill. ',el('b',{text:'Replace'}),' discards what’s on this device.'));
    openModal({title:'Import progress',body,actions:[{label:'Cancel'},
      {label:'Replace',kind:'danger',id:'impReplace',onClick:()=>{progress=p;if(impT){timing.practice=impT.practice;timing.challenge=impT.challenge;saveTiming()}afterImport('Progress replaced.')}},
      {label:'Merge',kind:'primary',id:'impMerge',onClick:()=>{
        for(const id of ids){const a=progress.skills[id],b=p.skills[id];
          if(!a){progress.skills[id]=b;continue}
          const seen=new Set(a.history.map(h=>h.t));
          const hist=a.history.concat(b.history.filter(h=>!seen.has(h.t))).sort((x,y)=>x.t-y.t).slice(-60);
          progress.skills[id]={tier:Math.max(a.tier,b.tier),lastPracticed:Math.max(a.lastPracticed||0,b.lastPracticed||0)||null,history:hist};
        }
        if(impT){timing.practice=Sim.mergeSamples(timing.practice,impT.practice);timing.challenge=Sim.mergeSamples(timing.challenge,impT.challenge);saveTiming()}
        afterImport('Progress merged.');}}]});
  };
  r.readAsText(file);
}
function afterImport(msg){saveProgress();refreshAll();if(selected)renderPanel();toast(msg)}
function resetProgress(){
  openModal({title:'Reset all progress?',body:el('p',{text:'This erases every tier on this device. Tip: Export first if you might want it back.'}),
    actions:[{label:'Cancel'},{label:'Export first',onClick:exportProgress},{label:'Reset everything',kind:'danger',id:'confirmReset',onClick:()=>{progress={version:1,skills:{}};saveProgress();refreshAll();if(selected)renderPanel();toast('Progress reset.')}}]});
}
$('btnExport').onclick=exportProgress;
$('btnImport').onclick=()=>$('fileIn').click();
$('fileIn').onchange=e=>{const f=e.target.files[0];if(f)importFile(f);e.target.value=''};
$('btnPlan').onclick=openPlan;$('btnReset').onclick=resetProgress;$('btnQueue').onclick=openQueue;$('btnHelp').onclick=openHelp;
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    if(mb.classList.contains('open'))closeModal();
    else if(quizOpen)leaveQuiz();
    else if(panelOpen())closePanel();
    return;
  }
  if(quiz&&!quiz.result&&!mb.classList.contains('open')){
    const it=quiz.items[quiz.i];
    if(it.q.type==='mc'&&!it.done&&/^[1-4a-dA-D]$/.test(e.key)&&!e.ctrlKey&&!e.metaKey&&!e.altKey){const i='1234'.includes(e.key)?+e.key-1:'abcd'.indexOf(e.key.toLowerCase());if(i<it.opts.length)answerMC(i)}
  }
});

/* ====================== init ====================== */
loadProgress();loadTiming();
$('playableNote').textContent=`${playable.length} of ${skills.length} skills playable in this demo`;
buildTree();buildGrid();legendBuild();
try{const u=JSON.parse(localStorage.getItem(UIKEY)||'null');if(u&&u.view==='grid')filter.view='grid'}catch(e){}
let startMode='tree';try{if(localStorage.getItem(LAYKEY)==='grouped')startMode='grouped'}catch(e){}
showLayout(startMode,false);
refreshAll();setView(filter.view);
goHome(false);
window.__skillgrove={version:1,storageOK:()=>storageOK,layout:()=>layout,mode:()=>layoutMode,timing:()=>timing,plan:(scratch)=>runPlan(!!scratch),ready:()=>skills.filter(s=>isReady(s.id)).map(s=>s.id),playableIds:()=>playable.map(s=>s.id),
  /* test hooks for rendering every question (read-only use: no progress is written in review mode) */
  qa:{bank:()=>DATA.bank,prepareQ,renderQuiz,setQuiz:q=>{quiz=q},closeQuizUI,openQuiz:()=>quizEl.classList.add('open'),figureNode,katexErrors:()=>window.__katexErrors}};
})();
</script>
</body>
</html>
