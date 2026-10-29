(function(){
'use strict';
/* ====================== constants & data ====================== */
const KEY='skilltree.progress.v1', UIKEY='skilltree.ui.v1';
const TIERS=['Unpracticed','Practiced','Level 1','Level 2','Mastered'];
const FILL=[0,30,55,80,100];
const PALETTE=['#ff6b6b','#ff9f43','#f4b400','#8bc34a','#2ed47a','#14c1a8','#22b8e6','#4c8dff','#7c6cff','#b15cff','#e25ce0','#ff5c9d','#f2784b','#6fae2e','#1fa39a','#5a7bef','#9a63d9','#d9588a'];
const skills=DATA.skills, byId={}; skills.forEach(s=>byId[s.id]=s);
const dependents={}; skills.forEach(s=>dependents[s.id]=[]); skills.forEach(s=>s.prereqs.forEach(p=>dependents[p].push(s.id)));
const bank=DATA.bank||{};
const chNums=Object.keys(DATA.chapters).map(Number).sort((a,b)=>a-b);
const chColor=n=>PALETTE[(n-1)%PALETTE.length];
function hex2rgb(h){h=h.replace('#','');return [0,2,4].map(i=>parseInt(h.substr(i,2),16))}
const rgba=(h,a)=>{const c=hex2rgb(h);return `rgba(${c[0]},${c[1]},${c[2]},${a})`};
const textOn=h=>{const c=hex2rgb(h);const l=(0.299*c[0]+0.587*c[1]+0.114*c[2])/255;return l>0.62?'#1d2433':'#ffffff'};
const hasBank=id=>!!(bank[id]&&bank[id].questions&&bank[id].questions.length);
const hasRound=(id,r)=>hasBank(id)&&bank[id].questions.some(q=>q.round===r);
const roundQs=(id,r)=>hasBank(id)?bank[id].questions.filter(q=>q.round===r):[];
const isPlayable=id=>hasRound(id,1);
const playable=skills.filter(s=>isPlayable(s.id));

/* ====================== storage ====================== */
let storageOK=true, memStore=null, progress={version:1,skills:{}};
function probeStorage(){try{const k='skilltree.__probe';localStorage.setItem(k,'1');localStorage.removeItem(k);return true}catch(e){return false}}
function normalizeSkill(o){
  if(!o||typeof o!=='object')return null;
  let t=Number(o.tier); if(!Number.isFinite(t))return null; t=Math.max(0,Math.min(4,Math.round(t)));
  let lp=(o.lastPracticed==null)?null:Number(o.lastPracticed); if(lp!=null&&!Number.isFinite(lp))lp=null;
  const hist=Array.isArray(o.history)?o.history.filter(h=>h&&typeof h==='object'&&Number.isFinite(Number(h.t))).slice(-60):[];
  return {tier:t,lastPracticed:lp,history:hist};
}
function normalizeProgress(raw){
  if(!raw||typeof raw!=='object'||raw.version!==1||!raw.skills||typeof raw.skills!=='object'||Array.isArray(raw.skills))return null;
  const out={version:1,skills:{}};
  for(const id of Object.keys(raw.skills)){const n=normalizeSkill(raw.skills[id]); if(n)out.skills[id]=n;}
  return out;
}
function loadProgress(){
  storageOK=probeStorage();
  if(!storageOK){showWarn('Browser storage is unavailable here, so progress will be lost when you close this tab. Use Export (top right) to save a backup file.');return}
  let raw=null;
  try{raw=localStorage.getItem(KEY)}catch(e){storageOK=false}
  if(!raw)return;
  try{
    const p=normalizeProgress(JSON.parse(raw));
    if(p){progress=p;return}
  }catch(e){}
  try{localStorage.setItem(KEY+'.backup-'+Date.now(),raw)}catch(e){}
  setTimeout(()=>toast('Saved progress could not be read; a backup copy was kept and you start fresh.'),300);
}
function saveProgress(){
  progress.savedAt=Date.now();
  if(storageOK){
    try{localStorage.setItem(KEY,JSON.stringify(progress));flashSaved();return true}catch(e){storageOK=false;showWarn('Could not save to browser storage. Progress is kept in memory only — Export a backup now.')}
  }
  memStore=JSON.stringify(progress);
  return false;
}
function showWarn(msg){const w=document.getElementById('warnbar');w.textContent='⚠ '+msg;w.style.display='block'}
function flashSaved(){const s=document.getElementById('saveInd');s.classList.add('on');clearTimeout(flashSaved.t);flashSaved.t=setTimeout(()=>s.classList.remove('on'),1600)}
const sk=id=>progress.skills[id]||(progress.skills[id]={tier:0,lastPracticed:null,history:[]});
const tierOf=id=>progress.skills[id]?progress.skills[id].tier:0;
const lastOf=id=>progress.skills[id]?progress.skills[id].lastPracticed:null;

/* ====================== helpers ====================== */
function el(tag,props,...kids){
  const e=document.createElement(tag);
  if(props)for(const k in props){const v=props[k];if(v==null||v===false)continue;
    if(k==='class')e.className=v;else if(k==='text')e.textContent=v;else if(k==='math')setMath(e,v);else if(k.startsWith('on'))e.addEventListener(k.slice(2),v);
    else if(k==='style')e.style.cssText=v;else e.setAttribute(k,v===true?'':v);}
  for(const c of kids.flat(Infinity)){if(c==null||c===false)continue;e.append(c.nodeType?c:document.createTextNode(String(c)))}
  return e;
}
/* ---- math (KaTeX, inlined) + figures ---- */
window.__katexErrors=window.__katexErrors||[];
const MATH_RE=/\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g;
function setMath(node,text){
  node.textContent='';text=text==null?'':String(text);
  let last=0,m;MATH_RE.lastIndex=0;
  while((m=MATH_RE.exec(text))){
    if(m.index>last)node.append(document.createTextNode(text.slice(last,m.index)));
    const disp=m[2]!=null,tex=disp?m[2]:m[1];
    const sp=document.createElement(disp?'div':'span');sp.className=disp?'mathd':'mathi';
    try{
      if(typeof katex==='undefined')throw new Error('KaTeX not loaded');
      katex.render(tex,sp,{displayMode:disp,throwOnError:true,strict:'ignore',output:'htmlAndMathml'});
    }catch(err){window.__katexErrors.push(String(err&&err.message||err)+' :: '+tex);sp.textContent=tex;sp.classList.add('matherr')}
    node.append(sp);last=m.index+m[0].length;
  }
  if(last<text.length)node.append(document.createTextNode(text.slice(last)));
  return node;
}
/* plain-text version (for titles, aria labels, truncated snippets) */
const mathPlain=t=>String(t==null?'':t).replace(MATH_RE,(_,a,b)=>(a!=null?a:b).replace(/\\(mathrm|text|operatorname)\{([^}]*)\}/g,'$2').replace(/\\[a-zA-Z]+\s?/g,s=>({'\\omega':'ω','\\tau':'τ','\\pi':'π','\\mu':'µ','\\Omega':'Ω','\\alpha':'α','\\beta':'β','\\angle':'∠','\\circ':'°','\\times':'×','\\cdot':'·','\\approx':'≈'})[s.trim()]||'').replace(/[{}]/g,'').replace(/\\[ ,;!]/g,' '));
/* shorten without cutting inside a \( ... \) span */
function shortMath(s,n){
  if(s.length<=n)return s;
  let cut=s.slice(0,n-1);
  const o=cut.lastIndexOf('\\('),c=cut.lastIndexOf('\\)');
  if(o>c){const end=s.indexOf('\\)',o);cut=(end>=0&&end+2<=n+40)?s.slice(0,end+2):cut.slice(0,o)}
  return cut.replace(/\s+$/,'')+'…';
}
const SVG_BAD=/^(script|foreignobject|image|iframe|object|embed|use|a|style|audio|video|animate|set|animatemotion|animatetransform)$/i;
function figureNode(q,extraClass){
  if(!q||!q.figure)return null;
  let svg;
  try{
    const doc=new DOMParser().parseFromString(q.figure,'image/svg+xml');
    svg=doc.documentElement;
    if(!svg||svg.nodeName.toLowerCase()!=='svg'||doc.getElementsByTagName('parsererror').length)throw new Error('bad svg');
    for(const n of [...svg.querySelectorAll('*')]){if(SVG_BAD.test(n.localName))n.remove()}
    for(const n of [svg,...svg.querySelectorAll('*')]){
      for(const at of [...n.attributes]){const k=at.name.toLowerCase(),v=at.value;
        if(k.startsWith('on')||k==='href'||k==='xlink:href'||k==='style'||/(javascript:|data:|url\(|https?:)/i.test(v))n.removeAttribute(at.name)}
    }
    svg=document.importNode(svg,true);
  }catch(e){window.__katexErrors.push('figure: '+e.message+' :: '+q.id);return null}
  const alt=q.figure_alt||'Figure';
  svg.setAttribute('role','img');svg.setAttribute('aria-label',alt);svg.setAttribute('focusable','false');
  svg.removeAttribute('width');svg.removeAttribute('height');
  let t=svg.querySelector(':scope > title');
  if(!t){t=document.createElementNS('http://www.w3.org/2000/svg','title');svg.insertBefore(t,svg.firstChild)}
  t.textContent=alt;
  const vb=(svg.getAttribute('viewBox')||'').split(/[\s,]+/).map(Number);
  const w=vb.length===4&&vb[2]>0?vb[2]:360;
  const box=el('figure',{class:'qfig'+(extraClass?' '+extraClass:''),'data-qid':q.id});
  box.style.setProperty('--fw',Math.min(Math.round(w*1.25),560)+'px');
  box.append(svg);return box;
}
const $=id=>document.getElementById(id);
function ago(ts){
  if(!ts)return 'never';
  const s=Math.max(0,(Date.now()-ts)/1000);
  if(s<60)return 'just now'; if(s<3600)return Math.floor(s/60)+' min ago';
  if(s<86400)return Math.floor(s/3600)+' h ago'; const d=Math.floor(s/86400); return d+(d===1?' day ago':' days ago');
}
const fmtDate=ts=>new Date(ts).toLocaleString([], {month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
let toastT;
function toast(msg){const t=$('toast');t.textContent=msg;t.classList.add('show');clearTimeout(toastT);toastT=setTimeout(()=>t.classList.remove('show'),3200)}
function colorVars(ch){const c=chColor(ch);return `--c:${c};--cs:${rgba(c,.5)};--cs2:${rgba(c,.78)};--tc:${textOn(c)};--bg:${rgba(c,.1)};--cb:${rgba(c,.55)}`}
/* A new skill is only recommended ("ready to learn") once ALL its prerequisites are at Level 2 or Mastered.
   Prerequisites that are still coming soon (no questions yet) can never get there, so they are ignored. */
const READY_TIER=3;
const prereqGaps=id=>byId[id].prereqs.filter(p=>isPlayable(p)&&tierOf(p)<READY_TIER);
function isReady(id){return isPlayable(id)&&tierOf(id)===0&&prereqGaps(id).length===0}
function queue(){
  return skills.filter(s=>{const t=tierOf(s.id);return t>=1&&t<=3&&hasRound(s.id,t+1)})
    .sort((a,b)=>(lastOf(a.id)||0)-(lastOf(b.id)||0)||skills.indexOf(a)-skills.indexOf(b));
}

/* ====================== layout engines ====================== */
const TW=168,TH=72,GX=18,GYR=46,PAD=26,HDR=48,DW=14,DGAP=12,BGAP=46,RGAP=76,ROWMAX=3200,WPAD=40,BMIN=470;
const LAYKEY='skilltree.layout.v1';   /* UI-only preference, separate from progress */

/* weighted isotonic placement: centers keep their order, neighbours keep a minimum distance,
   and the total weighted squared distance from the wanted centers is minimal (pool-adjacent-violators) */
function pav(targets,seps,weights){
  const n=targets.length,off=[0];for(let i=1;i<n;i++)off[i]=off[i-1]+seps[i-1];
  const bl=[];
  for(let i=0;i<n;i++){
    bl.push({s:weights[i]*(targets[i]-off[i]),W:weights[i],n:1});
    while(bl.length>1&&bl[bl.length-2].s/bl[bl.length-2].W>bl[bl.length-1].s/bl[bl.length-1].W){
      const b=bl.pop(),a=bl[bl.length-1];a.s+=b.s;a.W+=b.W;a.n+=b.n;
    }
  }
  const out=[];bl.forEach(b=>{const m=b.s/b.W;for(let k=0;k<b.n;k++)out.push(m+off[out.length])});
  return out;
}
/* Layered (Sugiyama-style) layout: longest-path layers, dummy nodes on long edges,
   barycenter sweeps + transposition to cut crossings, then priority x-placement. */
function layeredLayout(ids,edges){
  const par={};ids.forEach(i=>par[i]=[]);edges.forEach(([p,c])=>par[c].push(p));
  const layerOf={};
  const L=id=>layerOf[id]!=null?layerOf[id]:(layerOf[id]=par[id].length?1+Math.max(...par[id].map(L)):0);
  ids.forEach(L);
  const nl=Math.max(0,...ids.map(i=>layerOf[i]))+1;
  const nodes=[],nid={};
  const link=(a,b)=>{nodes[a].down.push(b);nodes[b].up.push(a)};
  ids.forEach(id=>{nid[id]=nodes.length;nodes.push({id,real:true,layer:layerOf[id],up:[],down:[],w:TW,wt:1})});
  const chains=[];
  edges.forEach(([p,c])=>{
    let prev=nid[p];const mids=[];
    for(let l=layerOf[p]+1;l<layerOf[c];l++){const k=nodes.length;nodes.push({real:false,layer:l,up:[],down:[],w:DW,wt:3});mids.push(k);link(prev,k);prev=k}
    link(prev,nid[c]);chains.push({key:p+'>'+c,mids});
  });
  const pos=new Array(nodes.length).fill(0);
  let ord=Array.from({length:nl},()=>[]);
  const reindex=l=>ord[l].forEach((k,i)=>pos[k]=i);
  const mean=a=>a.reduce((x,y)=>x+y,0)/a.length;
  function init(rev){
    ord=Array.from({length:nl},()=>[]);
    const ks=nodes.map((_,k)=>k).filter(k=>nodes[k].real&&nodes[k].layer===0);if(rev)ks.reverse();
    ord[0]=ks;reindex(0);
    for(let l=1;l<nl;l++){ // first placement: barycenter of the layer above
      const ks2=nodes.map((_,k)=>k).filter(k=>nodes[k].layer===l);
      ord[l]=ks2;ks2.forEach((k,i)=>pos[k]=i);
      const key=new Map(ks2.map(k=>[k,mean(nodes[k].up.map(m=>pos[m]))]));
      ord[l]=ks2.map((k,i)=>[k,i]).sort((a,b)=>key.get(a[0])-key.get(b[0])||a[1]-b[1]).map(a=>a[0]);reindex(l);
    }
  }
  function layerCross(l){
    const es=[];ord[l].forEach(u=>nodes[u].down.forEach(v=>es.push([pos[u],pos[v]])));
    let c=0;for(let i=0;i<es.length;i++)for(let j=i+1;j<es.length;j++)if((es[i][0]-es[j][0])*(es[i][1]-es[j][1])<0)c++;return c;
  }
  const total=()=>{let c=0;for(let l=0;l<nl-1;l++)c+=layerCross(l);return c};
  function sweep(down){
    for(let s=0;s<nl-1;s++){
      const l=down?s+1:nl-2-s,nb=down?'up':'down';
      const key=new Map(ord[l].map(k=>[k,nodes[k][nb].length?mean(nodes[k][nb].map(m=>pos[m])):pos[k]]));
      ord[l]=ord[l].map((k,i)=>[k,i]).sort((a,b)=>key.get(a[0])-key.get(b[0])||a[1]-b[1]).map(a=>a[0]);reindex(l);
    }
  }
  function pairCross(u,v){ // crossings between u (left) and v (right) with all their neighbours
    let c=0;
    for(const nb of ['up','down'])for(const a of nodes[u][nb])for(const b of nodes[v][nb])if(pos[a]>pos[b])c++;
    return c;
  }
  function transpose(){
    let improved=true,guard=0;
    while(improved&&guard++<12){
      improved=false;
      for(let l=0;l<nl;l++){
        for(let i=0;i<ord[l].length-1;i++){
          const u=ord[l][i],v=ord[l][i+1];
          if(pairCross(u,v)>pairCross(v,u)){ord[l][i]=v;ord[l][i+1]=u;pos[v]=i;pos[u]=i+1;improved=true}
        }
      }
    }
  }
  let best=null,bestC=Infinity;
  for(const rev of [false,true]){
    init(rev);
    for(let it=0;it<30;it++){
      sweep(it%2===0);transpose();
      const c=total();if(c<bestC){bestC=c;best=ord.map(a=>a.slice())}
    }
  }
  ord=best;for(let l=0;l<nl;l++)reindex(l);
  /* x placement */
  const cx=new Array(nodes.length).fill(0);
  const sepOf=(a,b)=>(nodes[a].w+nodes[b].w)/2+(nodes[a].real&&nodes[b].real?GX:DGAP);
  ord.forEach(arr=>{let x=0;arr.forEach((k,i)=>{if(i)x+=sepOf(arr[i-1],k);cx[k]=x});const m=(cx[arr[arr.length-1]]||0)/2;arr.forEach(k=>cx[k]-=m)});
  const placeLayer=(l,nbOf)=>{
    const arr=ord[l];if(!arr.length)return;
    const t=arr.map(k=>{const ns=nbOf(k);return ns.length?mean(ns.map(m=>cx[m])):cx[k]});
    const seps=arr.slice(1).map((k,i)=>sepOf(arr[i],k));
    const out=pav(t,seps,arr.map(k=>nodes[k].wt));arr.forEach((k,i)=>cx[k]=out[i]);
  };
  for(let it=0;it<10;it++){
    for(let l=1;l<nl;l++)placeLayer(l,k=>nodes[k].up);
    for(let l=nl-2;l>=0;l--)placeLayer(l,k=>nodes[k].down);
    for(let l=0;l<nl;l++)placeLayer(l,k=>nodes[k].up.concat(nodes[k].down));
  }
  let minX=Infinity,maxX=-Infinity;
  nodes.forEach((n,k)=>{minX=Math.min(minX,cx[k]-n.w/2);maxX=Math.max(maxX,cx[k]+n.w/2)});
  const rowY=l=>l*(TH+GYR);
  const pp={},mids={};
  ids.forEach(id=>{const k=nid[id];pp[id]={x:cx[k]-TW/2-minX,y:rowY(layerOf[id])}});
  chains.forEach(c=>{if(c.mids.length)mids[c.key]=c.mids.map(k=>[cx[k]-minX,rowY(nodes[k].layer)+TH/2])});
  return {pos:pp,mids,w:maxX-minX,h:nl*TH+(nl-1)*GYR,nl,crossings:bestC,layerOf};
}
const allEdges=[];skills.forEach(s=>s.prereqs.forEach(p=>allEdges.push([p,s.id])));
const layout={tree:null,grouped:null};
function computeTreeLayout(){
  const r=layeredLayout(skills.map(s=>s.id),allEdges);
  const nodes={},mids={};
  /* the layered layout is computed root-first top-down; flip it so foundations (layer 0) sit at the BOTTOM and dependents grow upward */
  for(const id in r.pos)nodes[id]={x:r.pos[id].x+WPAD,y:(r.h-r.pos[id].y-TH)+WPAD};
  for(const k in r.mids)mids[k]=r.mids[k].map(p=>[p[0]+WPAD,(r.h-p[1])+WPAD]);
  layout.tree={nodes,mids,blobs:{},w:r.w+WPAD*2,h:r.h+WPAD*2,layers:r.nl,crossings:r.crossings,layerOf:r.layerOf};
}
function computeGroupedLayout(){
  const byCh={};skills.forEach(s=>(byCh[s.chapter]=byCh[s.chapter]||[]).push(s.id));
  const subs={},bs={};
  for(const ch of chNums){
    const ids=byCh[ch]||[],set=new Set(ids);
    const sub=layeredLayout(ids,allEdges.filter(([p,c])=>set.has(p)&&set.has(c)));
    subs[ch]=sub;bs[ch]={w:Math.max(sub.w+PAD*2,BMIN),h:HDR+sub.h+PAD+4};
  }
  /* chapter-level dependency graph -> rank (blocks only ever sit below the blocks they depend on) */
  const cpred={};chNums.forEach(c=>cpred[c]=new Map());
  allEdges.forEach(([p,c])=>{const a=byId[p].chapter,b=byId[c].chapter;if(a!==b)cpred[b].set(a,(cpred[b].get(a)||0)+1)});
  const rank={};
  const R=c=>rank[c]!=null?rank[c]:(rank[c]=cpred[c].size?1+Math.max(...[...cpred[c].keys()].map(R)):0);
  chNums.forEach(R);
  const gdepth=chNums.map(c=>({c,d:byCh[c].reduce((a,id)=>a+(layout.tree.layerOf[id]||0),0)/byCh[c].length}));
  const avgD={};gdepth.forEach(o=>avgD[o.c]=o.d);
  const maxRank=Math.max(...chNums.map(c=>rank[c]));
  const bx={},by={};let y=0;
  const center=c=>bx[c]+bs[c].w/2;
  const mean=a=>a.reduce((x,y)=>x+y,0)/a.length;
  for(let r=0;r<=maxRank;r++){
    let row=chNums.filter(c=>rank[c]===r);
    const want=c=>{const ps=[...cpred[c].entries()].filter(([p])=>bx[p]!=null);return ps.length?ps.reduce((a,[p,n])=>a+center(p)*n,0)/ps.reduce((a,[,n])=>a+n,0):null};
    row.sort((a,b)=>{const wa=want(a),wb=want(b);return (wa==null?0:wa)-(wb==null?0:wb)||avgD[a]-avgD[b]||a-b});
    /* wrap into sub-rows if the row would be too wide */
    const subrows=[[]];let w=0;
    row.forEach(c=>{if(w&&w+bs[c].w+BGAP>ROWMAX){subrows.push([]);w=0}subrows[subrows.length-1].push(c);w+=bs[c].w+BGAP});
    subrows.forEach(sr=>{
      const wants=sr.map(c=>want(c));const fallback=0;
      const t=sr.map((c,i)=>wants[i]==null?null:wants[i]);
      /* blocks without a wanted position follow their neighbours */
      let acc=0;const tt=sr.map((c,i)=>{if(t[i]!=null)return t[i];return null});
      const known=tt.filter(v=>v!=null);const base=known.length?mean(known):fallback;
      const tgt=tt.map(v=>v==null?base:v);
      const seps=sr.slice(1).map((c,i)=>(bs[sr[i]].w+bs[c].w)/2+BGAP);
      const xs=pav(tgt,seps,sr.map(()=>1));
      let rh=0;sr.forEach((c,i)=>{bx[c]=xs[i]-bs[c].w/2;by[c]=y;rh=Math.max(rh,bs[c].h)});
      y+=rh+RGAP;
    });
  }
  const minX=Math.min(...chNums.map(c=>bx[c])),maxX=Math.max(...chNums.map(c=>bx[c]+bs[c].w));
  const nodes={},mids={},blobs={};
  for(const ch of chNums){
    const ox=bx[ch]-minX+WPAD,oy=by[ch]+WPAD;
    blobs[ch]={x:ox,y:oy,w:bs[ch].w,h:bs[ch].h};
    const ix=ox+(bs[ch].w-subs[ch].w)/2,iy=oy+PAD+4;   /* working frame is top-down with the header strip at the bottom; flipped below so the header ends up on top */
    for(const id in subs[ch].pos)nodes[id]={x:ix+subs[ch].pos[id].x,y:iy+subs[ch].pos[id].y};
    for(const k in subs[ch].mids)mids[k]=subs[ch].mids[k].map(p=>[ix+p[0],iy+p[1]]);
  }
  /* long cross-chapter arrows (they skip over other blocks) are routed through free channels beside those blocks */
  const M=26;
  allEdges.forEach(([p,c])=>{
    const cp=byId[p].chapter,cc=byId[c].chapter;if(cp===cc)return;
    const A=blobs[cp],B=blobs[cc],P=nodes[p],Q=nodes[c];
    const sx=P.x+TW/2,sy=P.y+TH,tx=Q.x+TW/2,ty=Q.y;
    if(ty<=sy)return;
    const obs=chNums.filter(x=>x!==cp&&x!==cc).map(x=>blobs[x]).filter(o=>o.y<ty&&o.y+o.h>sy).sort((u,v)=>u.y-v.y);
    if(!obs.length)return;
    const bands=[];
    obs.forEach(o=>{const last=bands[bands.length-1];
      if(last&&o.y<last.y1+RGAP*.6){last.y1=Math.max(last.y1,o.y+o.h);last.iv.push([o.x-M,o.x+o.w+M])}
      else bands.push({y0:o.y,y1:o.y+o.h,iv:[[o.x-M,o.x+o.w+M]]})});
    const pts=[];
    bands.forEach(bd=>{
      const iv=bd.iv.sort((u,v)=>u[0]-v[0]).reduce((acc,r)=>{const l=acc[acc.length-1];if(l&&r[0]<=l[1])l[1]=Math.max(l[1],r[1]);else acc.push([r[0],r[1]]);return acc},[]);
      const ym=(bd.y0+bd.y1)/2,f=Math.max(0,Math.min(1,(ym-sy)/(ty-sy)));
      let x=sx+(tx-sx)*f;
      const hit=iv.find(r=>x>r[0]&&x<r[1]);
      if(hit){const l=hit[0],r=hit[1];x=(l<14||Math.abs(x-l)>Math.abs(r-x))?r:l}
      pts.push([x,Math.max(sy+8,bd.y0-RGAP*.35)],[x,Math.min(ty-8,bd.y1+RGAP*.35)]);
    });
    mids[p+'>'+c]=pts;
  });
  const allX=[];for(const k in mids)mids[k].forEach(q=>allX.push(q[0]));
  const shiftX=Math.max(0,20-Math.min(Infinity,...allX));
  if(shiftX){for(const id in nodes)nodes[id].x+=shiftX;for(const k in mids)mids[k].forEach(q=>q[0]+=shiftX);for(const c in blobs)blobs[c].x+=shiftX}
  const worldW=Math.max(maxX-minX+WPAD*2,...allX.map(v=>v+WPAD),...chNums.map(c=>blobs[c].x+blobs[c].w+WPAD));
  const worldH=y-RGAP+WPAD*2;
  /* flip vertically: chapter blocks with no dependencies (rank 0) at the bottom, blocks that build on them above; inside every block the layers are bottom-up too */
  for(const id in nodes)nodes[id].y=worldH-nodes[id].y-TH;
  for(const k in mids)mids[k].forEach(q=>q[1]=worldH-q[1]);
  for(const c in blobs)blobs[c].y=worldH-blobs[c].y-blobs[c].h;
  layout.grouped={nodes,mids,blobs,w:worldW,h:worldH,rank};
}
function computeLayouts(){computeTreeLayout();computeGroupedLayout()}

/* ====================== tree rendering ====================== */
const world=$('world'),tv=$('treeView'),edgesSvg=$('edges'),panel=$('panel');
const panelOpen=()=>panel.classList.contains('open');
let view={x:20,y:20,s:1},selected=null,hoverId=null,quizOpen=false;
let layoutMode='tree',curPos={},morphRaf=0;
const filter={chapter:0,playable:false,view:'tree'};
const edgeEls=[];
const drag={on:false,moved:false,sx:0,sy:0,vx:0,vy:0};
const curL=()=>layout[layoutMode];
const reducedMotion=()=>window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches;
function tileTitle(s){return `${s.name} · Ch ${s.chapter}`}
function buildTile(s,st){
  const b=el('button',{class:'tile'+(st?' st':''),'data-id':s.id,style:colorVars(s.chapter),type:'button',title:tileTitle(s)},
    el('span',{class:'fill'}),el('span',{class:'nm',text:s.name}),
    el('span',{class:'meta'},el('span',{class:'pips'},[0,1,2,3].map(()=>el('i'))),el('span',{class:'tl'}),el('span',{class:'tag'})),
    el('span',{class:'star','aria-hidden':'true',text:'★'}));
  b.addEventListener('click',()=>{if(drag.moved)return;selectSkill(s.id)});
  b.addEventListener('mouseenter',()=>{hoverId=s.id;applyEdgeHighlight()});
  b.addEventListener('mouseleave',()=>{hoverId=null;applyEdgeHighlight()});
  b.addEventListener('focus',()=>{hoverId=s.id;applyEdgeHighlight()});
  b.addEventListener('blur',()=>{hoverId=null;applyEdgeHighlight()});
  return b;
}
function refreshTile(b){
  const id=b.dataset.id,s=byId[id],t=tierOf(id),soon=!isPlayable(id),ready=isReady(id);
  const st=b.classList.contains('st');
  b.className='tile'+(st?' st':'')+' t'+t+(soon?' soon':'')+(ready?' ready':'')+(selected===id?' sel':'');
  b.style.setProperty('--fill',FILL[t]+'%');
  b.querySelectorAll('.pips i').forEach((p,i)=>p.classList.toggle('on',t>i));
  b.querySelector('.tl').textContent=soon?'':TIERS[t];
  const tag=b.querySelector('.tag');tag.textContent=soon?'SOON':(ready?'READY':'');tag.style.display=(soon||ready)?'':'none';
  const gaps=(!soon&&t===0&&!ready)?prereqGaps(id).length:0;
  b.title=tileTitle(s)+(soon?' · coming soon':ready?' · ready to learn':gaps?` · recommended once prerequisites reach ${TIERS[READY_TIER]}`:'');
  b.setAttribute('aria-label',`${s.name}. Chapter ${s.chapter}. ${soon?'Coming soon, no questions yet':TIERS[t]+(ready?', ready to learn':'')}`);
  b.setAttribute('aria-pressed',selected===id?'true':'false');
  const dimmed=(filter.chapter&&s.chapter!==filter.chapter)||(filter.playable&&soon);
  if(dimmed&&!st)b.classList.add('dim');
}
/* edges: direct curve (used while tiles are moving) and routed polyline-through-dummies curve */
function directD(A,B){
  /* the tree grows upward: an arrow leaves the TOP of the prerequisite and enters the BOTTOM of the skill that builds on it */
  const ax=A.x+TW/2,ay=A.y,bx=B.x+TW/2,by=B.y+TH;
  if(by<=ay-8){const d=Math.max(30,(ay-by)*.5);return {d:`M${ax},${ay} C${ax},${ay-d} ${bx},${by+d} ${bx},${by}`,ex:bx,ey:by}}
  const right=B.x>A.x, sx=right?A.x+TW:A.x, ex=right?B.x:B.x+TW, sy=A.y+TH/2, ey=B.y+TH/2, d=Math.max(40,Math.abs(ex-sx)*.45);
  const dir=right?1:-1;
  return {d:`M${sx},${sy} C${sx+dir*d},${sy} ${ex-dir*d},${ey} ${ex},${ey}`,ex,ey};
}
function routedD(e,L){
  const A=L.nodes[e.from],B=L.nodes[e.to];
  const mids=L.mids[e.from+'>'+e.to];
  if(!mids)return directD(A,B);
  const pts=[[A.x+TW/2,A.y],...mids,[B.x+TW/2,B.y+TH]];
  let d=`M${pts[0][0]},${pts[0][1]}`;
  for(let i=1;i<pts.length;i++){const a=pts[i-1],b=pts[i],k=(b[1]-a[1])*.5;d+=` C${a[0]},${a[1]+k} ${b[0]},${b[1]-k} ${b[0]},${b[1]}`}
  return {d,ex:B.x+TW/2,ey:B.y+TH};
}
function setEdge(e,r){e.path.setAttribute('d',r.d);e.dot.setAttribute('cx',r.ex);e.dot.setAttribute('cy',r.ey)}
function sizeWorld(L){world.style.width=L.w+'px';world.style.height=L.h+'px';edgesSvg.setAttribute('width',L.w);edgesSvg.setAttribute('height',L.h)}
function placeTiles(pos){
  world.querySelectorAll('.tile').forEach(t=>{const p=pos[t.dataset.id];t.style.left=p.x+'px';t.style.top=p.y+'px'});
}
function buildTree(){
  computeLayouts();
  const G=layout.grouped;
  for(const ch of chNums){
    const b=G.blobs[ch];
    const blob=el('div',{class:'blob','data-ch':ch,style:`left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px;${colorVars(ch)}`},
      el('div',{class:'hd'},el('span',{class:'cpill',text:'Ch '+ch}),el('span',{style:'font-weight:800;font-size:13.5px',text:DATA.chapters[ch]}),el('span',{class:'ct','data-ct':ch})));
    world.insertBefore(blob,edgesSvg);
  }
  const NS='http://www.w3.org/2000/svg';
  allEdges.forEach(([p,c])=>{
    const path=document.createElementNS(NS,'path');
    const dot=document.createElementNS(NS,'circle');dot.setAttribute('r',3.2);
    edgesSvg.append(path,dot);edgeEls.push({from:p,to:c,path,dot});
  });
  skills.forEach(s=>world.append(buildTile(s,false)));
}
function legendBuild(){
  const lg=$('chLegend');lg.innerHTML='';
  lg.append(el('summary',{},'Chapter colors'));
  const box=el('div',{class:'lgrid'});
  chNums.forEach(c=>box.append(el('button',{class:'lg',type:'button',style:colorVars(c),title:'Highlight chapter '+c,'data-ch':c,onclick:()=>{const sel=$('chSel');if(sel){sel.value=filter.chapter===c?0:c;sel.onchange()}}},el('i'),el('span',{text:`${c} · ${DATA.chapters[c]}`}))));
  lg.append(box);
}
/* show a layout; animated=true glides every tile to its new place (~600 ms) */
const MORPH_MS=600;
function showLayout(mode,animated){
  cancelAnimationFrame(morphRaf);
  const L=layout[mode],ids=skills.map(s=>s.id);
  const from={};ids.forEach(id=>from[id]=curPos[id]||L.nodes[id]);
  layoutMode=mode;tv.dataset.mode=mode;world.dataset.layout=mode;
  sizeWorld(L);
  document.querySelectorAll('#world .blob').forEach(b=>b.classList.toggle('on',mode==='grouped'));
  const btn=$('btnGroup');btn.setAttribute('aria-pressed',String(mode==='grouped'));
  btn.querySelector('.t').textContent=mode==='grouped'?'Ungroup':'Group by chapter';
  btn.title=mode==='grouped'?'Back to one homogeneous prerequisite tree':'Sort the tree into chapter blocks';
  const finish=()=>{
    ids.forEach(id=>curPos[id]={x:L.nodes[id].x,y:L.nodes[id].y});
    placeTiles(curPos);edgeEls.forEach(e=>setEdge(e,routedD(e,L)));
    edgesSvg.classList.remove('morph');world.classList.remove('morphing');world.dataset.morphing='0';
  };
  if(!animated||reducedMotion()){finish();return}
  world.classList.add('morphing');world.dataset.morphing='1';edgesSvg.classList.add('morph');
  const t0=performance.now();
  const step=now=>{
    const k=Math.min(1,(now-t0)/MORPH_MS),e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;
    ids.forEach(id=>{const a=from[id],b=L.nodes[id];curPos[id]={x:a.x+(b.x-a.x)*e,y:a.y+(b.y-a.y)*e}});
    placeTiles(curPos);edgeEls.forEach(ed=>setEdge(ed,directD(curPos[ed.from],curPos[ed.to])));
    if(k<1)morphRaf=requestAnimationFrame(step);else finish();
  };
  morphRaf=requestAnimationFrame(step);
}
function toggleGroup(){
  const mode=layoutMode==='tree'?'grouped':'tree';
  try{localStorage.setItem(LAYKEY,mode)}catch(e){}
  showLayout(mode,true);
  if(selected&&curL().nodes[selected])focusTile(selected);else goFit();
}
function applyEdgeHighlight(){
  const id=hoverId||selected;
  edgesSvg.classList.toggle('active',!!id);
  edgeEls.forEach(e=>{
    const inn=!!id&&e.to===id,out=!!id&&e.from===id;
    e.path.classList.toggle('in',inn);e.path.classList.toggle('out',out);
    e.dot.classList.toggle('in',inn);e.dot.classList.toggle('out',out);
    const fd=!!filter.chapter&&byId[e.from].chapter!==filter.chapter&&byId[e.to].chapter!==filter.chapter;
    e.path.classList.toggle('fdim',fd);e.dot.classList.toggle('fdim',fd);
  });
}
function applyView(){world.style.transform=`translate(${view.x}px,${view.y}px) scale(${view.s})`}
function animateView(fn){world.classList.add('anim');fn();clearTimeout(animateView.t);animateView.t=setTimeout(()=>world.classList.remove('anim'),500)}
const MINS=.1;
function fitBox(x,y,w,h,maxS,minS){
  const vw=tv.clientWidth-(panelOpen()?372:0),vh=tv.clientHeight,m=30;
  const s=Math.max(minS||MINS,Math.min(maxS,(vw-m*2)/w,(vh-m*2)/h));
  view={s,x:(vw-w*s)/2-x*s,y:Math.max(m-y*s,(vh-h*s)/2-y*s)};
}
function bboxOf(ids){
  const P=curL().nodes;const ps=ids.map(i=>P[i]).filter(Boolean);
  const x0=Math.min(...ps.map(p=>p.x)),y0=Math.min(...ps.map(p=>p.y)),x1=Math.max(...ps.map(p=>p.x+TW)),y1=Math.max(...ps.map(p=>p.y+TH));
  return {x:x0,y:y0,w:x1-x0,h:y1-y0};
}
const HOME_BOTTOM=84;   /* keep the roots clear of the zoom buttons / legend sitting along the bottom edge */
function goHome(anim){
  /* the foundations live at the BOTTOM now: home frames the playable starting skills and anchors the bottom of the tree to the bottom of the screen */
  let box;const L=curL();
  if(layoutMode==='grouped'){
    const bs=[1,2].map(c=>L.blobs[c]).filter(Boolean);
    const x0=Math.min(...bs.map(b=>b.x)),y0=Math.min(...bs.map(b=>b.y)),x1=Math.max(...bs.map(b=>b.x+b.w)),y1=Math.max(...bs.map(b=>b.y+b.h));
    box={x:x0,y:y0,w:x1-x0,h:y1-y0};
  }else{
    const ids=playable.map(s=>s.id);
    box=bboxOf(ids.length?ids:skills.map(s=>s.id));
    const bottom=L.h-WPAD;if(bottom>box.y+box.h){box.h=bottom-box.y}   /* include the whole bottom row of roots */
  }
  const f=()=>{
    const vw=tv.clientWidth-(panelOpen()?372:0),vh=tv.clientHeight;
    view.s=Math.max(layoutMode==='tree'?.55:MINS,Math.min(1,(vw-60)/box.w,(vh-30-HOME_BOTTOM)/box.h));
    view.x=(vw-box.w*view.s)/2-box.x*view.s;
    view.y=vh-HOME_BOTTOM-(box.y+box.h)*view.s;
    if(layoutMode==='tree')view.x=vw/2-(box.x+box.w/2)*view.s;
    applyView();
  };
  anim?animateView(f):f();
}
function goFit(){const L=curL();animateView(()=>{fitBox(0,0,L.w,L.h,1);applyView()})}
function zoomAt(f,cx,cy){
  const ns=Math.max(MINS,Math.min(1.8,view.s*f)),k=ns/view.s;
  view.x=cx-(cx-view.x)*k;view.y=cy-(cy-view.y)*k;view.s=ns;applyView();
}
function focusTile(id){
  const n=curL().nodes[id];if(!n)return;
  animateView(()=>{
    const vw=tv.clientWidth-(panelOpen()?372:0),vh=tv.clientHeight;
    view.s=Math.min(1.2,Math.max(view.s,.85));view.x=vw/2-(n.x+TW/2)*view.s;view.y=vh/2-(n.y+TH/2)*view.s;applyView();
  });
}
function focusChapter(ch){
  const b=curL().blobs[ch];
  if(layoutMode==='grouped'&&b){animateView(()=>{fitBox(b.x,b.y,b.w,b.h,1);view.y=30-b.y*view.s;applyView()});return}
  goFit();
}
/* ---- pan / zoom; dragging must never select text ---- */
function clearSelection(){try{const s=window.getSelection&&window.getSelection();s&&s.removeAllRanges&&s.removeAllRanges()}catch(e){}}
tv.addEventListener('mousedown',e=>{if(e.button===0&&!e.target.closest('.zoomctl,#chLegend'))e.preventDefault()});   /* no text-selection / native drag start */
tv.addEventListener('selectstart',e=>e.preventDefault());
tv.addEventListener('dragstart',e=>e.preventDefault());
tv.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag.on=true;drag.moved=false;drag.sx=e.clientX;drag.sy=e.clientY;drag.vx=view.x;drag.vy=view.y});
window.addEventListener('pointermove',e=>{
  if(!drag.on)return;const dx=e.clientX-drag.sx,dy=e.clientY-drag.sy;
  if(!drag.moved&&Math.hypot(dx,dy)>5){drag.moved=true;tv.classList.add('drag');world.classList.remove('anim');clearSelection()}
  if(drag.moved){view.x=drag.vx+dx;view.y=drag.vy+dy;applyView();clearSelection()}
});
window.addEventListener('pointerup',()=>{if(drag.on){drag.on=false;tv.classList.remove('drag');setTimeout(()=>drag.moved=false,0)}});
tv.addEventListener('wheel',e=>{
  e.preventDefault();world.classList.remove('anim');
  if(e.ctrlKey||e.metaKey){const r=tv.getBoundingClientRect();zoomAt(Math.exp(-e.deltaY*(e.deltaMode?0.05:0.01)),e.clientX-r.left,e.clientY-r.top)}
  else if(e.shiftKey&&!e.deltaX){view.x-=e.deltaY;applyView()}
  else{view.x-=e.deltaX;view.y-=e.deltaY;applyView()}
},{passive:false});
$('zIn').onclick=()=>zoomAt(1.2,tv.clientWidth/2,tv.clientHeight/2);
$('zOut').onclick=()=>zoomAt(1/1.2,tv.clientWidth/2,tv.clientHeight/2);
$('zFit').onclick=goFit;$('zHome').onclick=()=>goHome(true);
$('btnGroup').onclick=toggleGroup;

/* ====================== grid view ====================== */
function buildGrid(){
  const g=$('gridView');g.innerHTML='';
  for(const ch of chNums){
    const list=skills.filter(s=>s.chapter===ch);
    g.append(el('section',{class:'gsec','data-ch':ch,style:colorVars(ch)},
      el('div',{class:'hd'},el('span',{class:'cpill',text:'Ch '+ch}),el('b',{text:DATA.chapters[ch]}),el('span',{class:'ct','data-ct':ch})),
      el('div',{class:'ggrid'},list.map(s=>buildTile(s,true)))));
  }
}
function applyGridFilter(){
  document.querySelectorAll('#gridView .gsec').forEach(sec=>{
    const ch=+sec.dataset.ch;let any=false;
    sec.querySelectorAll('.tile').forEach(t=>{
      const hide=filter.playable&&!isPlayable(t.dataset.id);t.style.display=hide?'none':'';if(!hide)any=true;
    });
    sec.style.display=((filter.chapter&&filter.chapter!==ch)||!any)?'none':'';
  });
  document.querySelectorAll('#world .blob').forEach(b=>b.classList.toggle('dim',!!filter.chapter&&+b.dataset.ch!==filter.chapter));
  document.querySelectorAll('#chLegend .lg').forEach(b=>b.classList.toggle('on',+b.dataset.ch===filter.chapter));
}
