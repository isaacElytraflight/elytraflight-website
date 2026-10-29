const puppeteer=require('puppeteer-core');
(async()=>{
 const b=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:'new',args:['--no-sandbox','--allow-file-access-from-files']});
 const p=await b.newPage();await p.setViewport({width:1280,height:800});
 const errs=[];p.on('console',m=>{if(['error','warning'].includes(m.type()))errs.push(m.type()+': '+m.text())});p.on('pageerror',e=>errs.push('PAGEERR '+e.message));
 await p.goto('file:///workspace/skilltree/app/skilltree.html');
 await new Promise(r=>setTimeout(r,800));
 await p.screenshot({path:'../shots/tree_v4.png'});
 console.log(errs, await p.evaluate(()=>document.querySelectorAll('.tile').length));
 await b.close();
})();
