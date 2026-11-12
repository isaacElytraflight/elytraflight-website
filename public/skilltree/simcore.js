/* Skillgrove: Pure, DOM-free learning-plan simulation + timing helpers.
   Loaded as window.SkillSim in the page; the tests also run this exact block under node. */
(function(root){
'use strict';
var READY_TIER=3;
var DEFAULT_MIN=10, MIN_SAMPLES=3, MIN_SEC=20, CAP_SEC=1800, MAX_SAMPLES=200;

function numOr(v,d){v=Number(v);return isFinite(v)&&v>=0?v:d}
function round2(x){return Math.round(x*100)/100}

function simulate(graph,start,opts){
  opts=opts||{};
  var tp=numOr(opts.practiceMin,DEFAULT_MIN),tc=numOr(opts.challengeMin,DEFAULT_MIN);
  var ids=graph.ids.slice(),inSet={};ids.forEach(function(i){inSet[i]=1});
  var pre={},top={},tier={};
  ids.forEach(function(id){
    pre[id]=(graph.prereqs[id]||[]).filter(function(p){return inSet[p]&&p!==id});
    var m=graph.maxTier&&graph.maxTier[id];top[id]=m==null?4:Math.max(0,Math.min(4,m|0));
    var t=(start&&start[id])|0;tier[id]=Math.max(0,Math.min(top[id],t));
  });
  var need=function(p){return Math.min(READY_TIER,top[p])};
  function counts(){var c=[0,0,0,0,0];ids.forEach(function(id){c[tier[id]]++});return c}
  var practicedAt={},reachedAt={};
  ids.forEach(function(id){reachedAt[id]={};for(var t=0;t<=tier[id];t++)reachedAt[id][t]=0});
  var startCounts=counts(),rows=[],cum=0,guard=1000;
  function finished(){return ids.every(function(id){return tier[id]>=top[id]})}
  var out={ok:true,stuck:false,scope:ids.length,startCounts:startCounts,practiceMin:tp,challengeMin:tc};
  while(!finished()){
    if(rows.length>=guard){out.ok=false;out.stuck=true;break}
    var snap={};ids.forEach(function(id){snap[id]=tier[id]});
    var ready=ids.filter(function(id){return snap[id]===0&&top[id]>=1&&pre[id].every(function(p){return snap[p]>=need(p)})});
    var chal=ids.filter(function(id){return snap[id]>=1&&snap[id]<top[id]});
    if(!ready.length&&!chal.length){out.ok=false;out.stuck=true;break}
    var n=rows.length+1;
    ready.forEach(function(id){tier[id]=1;practicedAt[id]=n;reachedAt[id][1]=n});
    var ch=chal.map(function(id){var from=snap[id];tier[id]=from+1;reachedAt[id][from+1]=n;return {id:id,from:from,to:from+1}});
    var minutes=ready.length*tp+ch.length*tc;cum+=minutes;
    rows.push({n:n,practiced:ready,challenges:ch,minutes:round2(minutes),cumulative:round2(cum),tiers:counts()});
  }
  out.rows=rows;out.sessions=rows.length;out.totalMinutes=round2(cum);out.endCounts=counts();
  out.practiceCount=rows.reduce(function(a,r){return a+r.practiced.length},0);
  out.challengeCount=rows.reduce(function(a,r){return a+r.challenges.length},0);
  out.critical={chain:[],sessions:rows.length};
  if(out.ok&&rows.length){
    var finish={};ids.forEach(function(id){finish[id]=reachedAt[id][top[id]]!=null?reachedAt[id][top[id]]:0});
    var last=Math.max.apply(null,ids.map(function(id){return finish[id]}));
    var memo={};
    var trace=function(id){
      if(memo[id])return memo[id];
      var ps=practicedAt[id],best=[id];
      if(ps&&ps>1){
        pre[id].forEach(function(p){
          if(reachedAt[p][need(p)]===ps-1){var c=trace(p).concat([id]);if(c.length>best.length)best=c}
        });
      }
      return memo[id]=best;
    };
    var bestChain=[];
    ids.forEach(function(id){if(finish[id]===last){var c=trace(id);if(c.length>bestChain.length)bestChain=c}});
    out.critical={chain:bestChain,sessions:rows.length};
  }
  return out;
}

function sampleList(l){return Array.isArray(l)?l.filter(function(x){return x&&isFinite(Number(x.s))&&Number(x.s)>=MIN_SEC&&isFinite(Number(x.t))}).map(function(x){return {s:Math.min(CAP_SEC,Math.round(Number(x.s))),t:Number(x.t)}}).slice(-MAX_SAMPLES):[]}

function addSample(list,seconds,t){
  var s=Number(seconds);list=sampleList(list);
  if(!isFinite(s)||s<MIN_SEC)return {list:list,added:false};
  list=list.concat([{s:Math.min(CAP_SEC,Math.round(s)),t:isFinite(Number(t))?Number(t):0}]).slice(-MAX_SAMPLES);
  return {list:list,added:true};
}

function estimate(list,dflt,minN){
  list=sampleList(list);dflt=dflt==null?DEFAULT_MIN:dflt;minN=minN==null?MIN_SAMPLES:minN;
  var n=list.length;
  if(n>=minN){var mean=list.reduce(function(a,x){return a+x.s},0)/n/60;return {minutes:Math.round(mean*10)/10,n:n,source:'measured',need:minN}}
  return {minutes:dflt,n:n,source:'default',need:minN};
}

function normalizeTiming(raw){
  var o={version:1,practice:[],challenge:[],override:{practice:null,challenge:null}};
  if(!raw||typeof raw!=='object')return o;
  o.practice=sampleList(raw.practice);o.challenge=sampleList(raw.challenge);
  var ov=raw.override&&typeof raw.override==='object'?raw.override:{};
  ['practice','challenge'].forEach(function(k){var v=Number(ov[k]);o.override[k]=ov[k]!=null&&isFinite(v)&&v>0&&v<=600?v:null});
  return o;
}

function mergeSamples(a,b){
  var seen={},out=[];
  sampleList(a).concat(sampleList(b)).forEach(function(x){var k=x.t+':'+x.s;if(!seen[k]){seen[k]=1;out.push(x)}});
  return out.sort(function(x,y){return x.t-y.t}).slice(-MAX_SAMPLES);
}

function fmtDuration(min){
  var m=Math.round(min);if(m<60)return m+' min';
  var h=Math.floor(m/60),r=m%60;return h+' h'+(r?' '+r+' min':'');
}

/* Calendar dates are YYYY-MM-DD in the learner's local zone. A far exam is
   spread across at most ten years so a bad date cannot build a huge list. */
var MAX_STUDY_DAYS=3660;

function localISODate(d){
  if(typeof d==='string')return /^\d{4}-\d{2}-\d{2}$/.test(d)?d:'';
  d=d||new Date();
  var y=d.getFullYear(),m=d.getMonth()+1,day=d.getDate();
  return y+'-'+(m<10?'0':'')+m+'-'+(day<10?'0':'')+day;
}

function parseISODate(s){
  var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||'');
  if(!m)return null;
  var y=+m[1],mo=+m[2],d=+m[3];
  var dt=new Date(y,mo-1,d);
  if(dt.getFullYear()!==y||dt.getMonth()!==mo-1||dt.getDate()!==d)return null;
  return dt;
}

function addISODays(s,n){
  var dt=parseISODate(s);
  if(!dt)return '';
  dt.setDate(dt.getDate()+n);
  return localISODate(dt);
}

function daysBetween(a,b){
  var da=parseISODate(a),db=parseISODate(b);
  if(!da||!db)return NaN;
  var ua=Date.UTC(da.getFullYear(),da.getMonth(),da.getDate());
  var ub=Date.UTC(db.getFullYear(),db.getMonth(),db.getDate());
  return Math.round((ub-ua)/86400000);
}

function studyDayCount(today,examDate){
  var diff=daysBetween(today,examDate);
  if(!isFinite(diff))return 0;
  var n=diff>0?diff:1;
  return n>MAX_STUDY_DAYS?MAX_STUDY_DAYS:n;
}

function studyDates(today,examDate){
  var n=studyDayCount(today,examDate),out=[],i;
  for(i=0;i<n;i++)out.push(addISODays(today,i));
  return out;
}

function examCountdown(today,examDate){
  var diff=daysBetween(today,examDate);
  if(!isFinite(diff))return {days:null,text:''};
  if(diff===0)return {days:0,text:'Exam today'};
  if(diff===1)return {days:1,text:'Exam tomorrow'};
  if(diff>1)return {days:diff,text:'Exam in '+diff+' days'};
  var ago=-diff;
  if(ago===1)return {days:diff,text:'Exam was yesterday'};
  return {days:diff,text:'Exam was '+ago+' days ago'};
}

/* Session i lands on a study day. Fewer sessions than days leave gaps so the
   steps stay spaced. More sessions than days pack earlier steps onto earlier days. */
function sessionDayIndex(i,sessionCount,dayCount){
  if(!sessionCount||!dayCount||i<0||i>=sessionCount)return -1;
  if(sessionCount<=dayCount){
    if(sessionCount===1)return 0;
    return Math.round(i*(dayCount-1)/(sessionCount-1));
  }
  return Math.min(dayCount-1,Math.floor(i*dayCount/sessionCount));
}

function sessionsOnDay(sessionCount,dayCount,day){
  var out=[],i;
  for(i=0;i<sessionCount;i++)if(sessionDayIndex(i,sessionCount,dayCount)===day)out.push(i);
  return out;
}

function nextSessionDay(sessionCount,dayCount,afterDay){
  var best=-1,i,d;
  for(i=0;i<sessionCount;i++){
    d=sessionDayIndex(i,sessionCount,dayCount);
    if(d>afterDay&&(best<0||d<best))best=d;
  }
  return best;
}

function spreadSessionIndexes(sessionCount,dayCount){
  var days=[],d,i,day;
  for(d=0;d<dayCount;d++)days.push([]);
  for(i=0;i<sessionCount;i++){
    day=sessionDayIndex(i,sessionCount,dayCount);
    if(day>=0&&day<dayCount)days[day].push(i);
  }
  return days;
}

/* New skills keep the plan's order. Mastery challenges follow the spaced-review
   queue: least recently practiced first. Missing times count as never. */
function orderSessionItems(items,lastPracticed){
  items=Array.isArray(items)?items:[];
  var skills=[],challenges=[],last=lastPracticed||{};
  items.forEach(function(it,i){
    if(!it||(it.type!=='skill'&&it.type!=='challenge')||typeof it.id!=='string'||!it.id)return;
    if(it.type==='challenge')challenges.push({it:it,i:i});
    else skills.push(it);
  });
  challenges.sort(function(a,b){
    var la=Number(last[a.it.id]);if(!isFinite(la))la=0;
    var lb=Number(last[b.it.id]);if(!isFinite(lb))lb=0;
    return la-lb||a.i-b.i;
  });
  return skills.concat(challenges.map(function(c){return c.it}));
}

var api={simulate:simulate,addSample:addSample,estimate:estimate,normalizeTiming:normalizeTiming,mergeSamples:mergeSamples,sampleList:sampleList,fmtDuration:fmtDuration,
  localISODate:localISODate,parseISODate:parseISODate,addISODays:addISODays,daysBetween:daysBetween,
  studyDayCount:studyDayCount,studyDates:studyDates,examCountdown:examCountdown,
  sessionDayIndex:sessionDayIndex,sessionsOnDay:sessionsOnDay,nextSessionDay:nextSessionDay,
  spreadSessionIndexes:spreadSessionIndexes,orderSessionItems:orderSessionItems,
  READY_TIER:READY_TIER,DEFAULT_MIN:DEFAULT_MIN,MIN_SAMPLES:MIN_SAMPLES,MIN_SEC:MIN_SEC,CAP_SEC:CAP_SEC,MAX_SAMPLES:MAX_SAMPLES,MAX_STUDY_DAYS:MAX_STUDY_DAYS};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.SkillSim=api;
})(typeof window!=='undefined'?window:this);
