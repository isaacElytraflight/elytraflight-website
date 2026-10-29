/* usage: node shot.js <out.png> [--mode tree|grouped] [--w 1500] [--h 950] [--fit] [--plan] [--scratch] [--seed file.json] [--eval "js"]
   Takes ONE screenshot of the built app after the requested set-up. */
const puppeteer=require('puppeteer-core'),fs=require('fs');const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const a=process.argv.slice(2);const out=a[0];const opt=n=>{const i=a.indexOf('--'+n);return i<0?null:(a[i+1]&&!a[i+1].startsWith('--')?a[i+1]:true)};
(async()=>{
 const b=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:'new',args:['--no-sandbox']});
 const errs=[];const ctx=await b.createBrowserContext();const p=await ctx.newPage();
 await p.setViewport({width:+(opt('w')||1500),height:+(opt('h')||950)});
 p.on('console',m=>{if(['error','warning'].includes(m.type()))errs.push(m.text())});p.on('pageerror',e=>errs.push('PAGEERR '+e.message));
 await p.goto('file:///workspace/skilltree/app/skilltree.html');
 const seed=opt('seed');
 await p.evaluate((m,s)=>{localStorage.setItem('skilltree.layout.v1',m);if(s)localStorage.setItem('skilltree.progress.v1',s)},opt('mode')||'tree',seed?fs.readFileSync(seed,'utf8'):null);
 await p.reload();await sleep(700);
 if(opt('fit')){await p.click('#zFit');await sleep(900)}
 if(opt('plan')){await p.click('#btnPlan');await sleep(400);if(opt('scratch')){await p.click('#planScr');await sleep(300)}}
 if(opt('eval')){await p.evaluate(opt('eval'));await sleep(400)}
 await p.screenshot({path:out});
 console.log('errs',JSON.stringify(errs));await b.close();
})();
