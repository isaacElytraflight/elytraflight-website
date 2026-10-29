/* Regenerates the layout screenshots in ../shots/ (run after build_app.py) */
const puppeteer=require('puppeteer-core');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const URL='file:///workspace/skilltree/app/skilltree.html',SH='/workspace/skilltree/app/shots/',KEY='skilltree.progress.v1';
const now=Date.now(),DAY=864e5;
const seed={version:1,skills:{'lti-def':{tier:4,lastPracticed:now-3*DAY,history:[]},'rc-lpf':{tier:3,lastPracticed:now-2*DAY,history:[]},'cx-exp':{tier:3,lastPracticed:now-DAY,history:[]},'impulse-conv':{tier:2,lastPracticed:now-DAY,history:[]},'sinusoid-resp':{tier:1,lastPracticed:now-DAY,history:[]},tf:{tier:1,lastPracticed:now,history:[]}}};
async function page(b,w,h,mode){
  const ctx=await b.createBrowserContext();const p=await ctx.newPage();await p.setViewport({width:w,height:h});
  await p.goto(URL);await p.evaluate((k,s,m)=>{localStorage.setItem(k,JSON.stringify(s));localStorage.setItem('skilltree.layout.v1',m)},KEY,seed,mode);
  await p.reload();await sleep(700);return p;
}
(async()=>{
 const b=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:'new',args:['--no-sandbox']});
 for(const mode of ['tree','grouped']){
   const tag=mode==='tree'?'ungrouped':'grouped';
   // whole picture via the fit-all button (tall viewport so the whole thing is visible at once)
   let p=await page(b,2200,2300,mode);await p.click('#zFit');await sleep(900);
   await p.screenshot({path:SH+(mode==='tree'?'20_tree_ungrouped_whole.png':'21_tree_grouped_whole.png')});await p.close();
   // readable portions
   p=await page(b,1500,950,mode);
   await p.evaluate(()=>document.querySelector('#world .tile[data-id="tf"]').click());await sleep(500);await p.keyboard.press('Escape');await sleep(600);
   const bx=await p.$eval('#world .tile[data-id="pole-zero"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}});
   await p.mouse.move(bx.x,bx.y);await sleep(300);
   await p.screenshot({path:SH+(mode==='tree'?'22_tree_ungrouped_zoom.png':'23_tree_grouped_zoom.png')});
   await p.close();
   // a dense mid-circuit region (many coming-soon skills, long arrows)
   p=await page(b,1500,950,mode);
   await p.mouse.move(700,500);
   await p.keyboard.down('Control');await p.mouse.wheel({deltaY:mode==='tree'?-30:-70});await p.keyboard.up('Control');await sleep(100);
   for(let k=0;k<3;k++){const r=await p.$eval('#world .tile[data-id="cs-intro"]',e=>{const r=e.getBoundingClientRect();return{x:r.x+r.width/2,y:r.y+r.height/2}});await p.mouse.wheel({deltaX:r.x-750,deltaY:r.y-475});await sleep(150)}
   await p.mouse.move(750,475);await sleep(300);
   await p.screenshot({path:SH+(mode==='tree'?'22b_tree_ungrouped_zoom_midcourse.png':'23b_tree_grouped_zoom_midcourse.png')});await p.close();
 }
 // mid-animation frame
 let p=await page(b,1500,950,'tree');await p.click('#zFit');await sleep(700);await p.click('#btnGroup');await sleep(280);
 await p.screenshot({path:SH+'24_morph_midway.png'});await p.close();
 await b.close();
})();
