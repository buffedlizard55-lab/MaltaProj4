const fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const {chromium:playwright}=require('playwright-core');const chromium=require('@sparticuz/chromium');
(async()=>{
 const root=path.resolve('public');
 const server=http.createServer((req,res)=>{const p=new URL(req.url,'http://t').pathname.replace(/^\/MaltaProj4\//,'/');const f=path.resolve(root,'.'+p+(p.endsWith('/')?'index.html':''));if(!f.startsWith(root+path.sep)||!fs.existsSync(f)){res.writeHead(404);res.end();return;}res.setHeader('content-type',{'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml'}[path.extname(f)]||'application/json');res.end(fs.readFileSync(f));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}/MaltaProj4/`;
 await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));chromium.setupLambdaEnvironment('/tmp/al2023/lib');
 const b=await playwright.launch({args:chromium.default.args.filter(a=>a!=='--disable-web-security'),executablePath:await chromium.default.executablePath(),headless:true});
 const page=await b.newPage();
 const out={};
 for(const w of [320,390,1440]){
   await page.setViewportSize({width:w,height:w===320?568:w===390?844:900});
   for (const p of ['index.html','picks.html','unresolved.html','matches.html','analysis.html']){
     await page.goto(base+p);
     const data=await page.evaluate(()=>{
       const q=s=>{const el=document.querySelector(s);if(!el)return null;const r=el.getBoundingClientRect();return {y:Math.round(r.y+scrollY),h:Math.round(r.height)};};
       const row=document.querySelector('tr[data-match]:not([hidden])');
       const firstPick=row?{team:(row.querySelector('[data-label="Pick"], td')||{}).innerText, y:Math.round(row.getBoundingClientRect().y+scrollY)}:null;
       return {overflowX:document.documentElement.scrollWidth>innerWidth,
               docH:document.documentElement.scrollHeight,
               tabs:!!document.querySelector('.mobile-tabs'),
               banner:q('#exec-banner'), cta:q('#freshness-strip .fresh-cta'),
               glance:q('#picks-at-a-glance'), unresolved:q('#unresolved-picks'),
               firstTableRow:firstPick,
               fontSize:getComputedStyle(document.body).fontSize,
               tapTargets:Math.min(...[...document.querySelectorAll('header a, .mobile-tabs a')].map(a=>{const r=a.getBoundingClientRect();return Math.min(r.width||999, r.height||999);}))};
     });
     (out[p]=out[p]||{})[w]=data;
   }
 }
 console.log(JSON.stringify(out,null,1));
 await b.close();await new Promise(r=>server.close(r));})();
