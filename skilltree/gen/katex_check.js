// Render every \( \) / \[ \] chunk of the given bank JSON files with KaTeX in strict mode.
// usage: node katex_check.js bank1.json bank2.json ...   (exit 1 on any error/warning)
const katex=require('/workspace/skilltree/app/tests/node_modules/katex');const fs=require('fs');
let n=0,bad=[];
const chunks=s=>{const out=[];const re=/\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g;let m;while((m=re.exec(s)))out.push([m[1]!==undefined?m[1]:m[2],m[2]!==undefined]);return out};
for(const f of process.argv.slice(2)){
  const b=JSON.parse(fs.readFileSync(f,'utf8'));
  for(const q of b.questions){
    const texts=[q.prompt,q.explanation,...(q.options||[]),q.unit||''];
    for(const t of texts)for(const [tex,disp] of chunks(t)){n++;
      try{katex.renderToString(tex,{throwOnError:true,displayMode:disp,strict:(code,msg)=>{throw new Error('strict '+code+': '+msg)}})}catch(e){bad.push(q.id+' :: '+tex+' :: '+e.message.split('\n')[0])}}
  }
}
console.log(`KaTeX: rendered ${n} math chunks, ${bad.length} errors`);bad.slice(0,80).forEach(x=>console.log('  ',x));process.exit(bad.length?1:0);
