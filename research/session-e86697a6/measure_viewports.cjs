const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium:playwright}=require('playwright-core');const chromium=require('@sparticuz/chromium');
(async()=>{
 const root=path.resolve('public');
 const server=http.createServer((req,res)=>{const url=new URL(req.url,'http://t');const p=decodeURIComponent(url.pathname);const f=path.resolve(root,'.'+p+(p.endsWith('/')?'index.html':''));if(!f.startsWith(root+path.sep)||!fs.existsSync(f)){res.writeHead(404);res.end();return;}const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'};res.setHeader('content-type',mime[path.extname(f)]||'text/plain');res.end(fs.readFileSync(f));});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}/`;
 await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
 chromium.setupLambdaEnvironment('/tmp/al2023/lib');
 const browser=await playwright.launch({args:chromium.default.args.filter(a=>a!=='--disable-web-security'),executablePath:await chromium.default.executablePath(),headless:true});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 for(const [w,h] of [[320,568],[390,844],[412,915]]){
   await page.setViewportSize({width:w,height:h});
   await page.goto(base+'index.html');
   const r=await page.evaluate(()=>{const top=s=>{const el=document.querySelector(s);return el?Math.round(el.getBoundingClientRect().top+scrollY):null;};
     const txt=s=>{const el=document.querySelector(s);return el?el.textContent.trim().slice(0,240):null;};
     return {overflow:document.documentElement.scrollWidth>innerWidth,
      quicknav:top('#exec-quicknav'), quicknavText:txt('#exec-quicknav'),
      strip:top('#freshness-strip'), firstCard:top('#picks-at-a-glance a.glance-card-mobile'),
      withheld:top('#withheld-picks'), unresolved:top('#unresolved-picks'),
      withheldText:txt('#withheld-picks'), counts:[...document.querySelectorAll('[data-count]')].slice(0,8).map(e=>e.dataset.count+'='+e.textContent),
      tabbar:top('nav.tabbar')||top('.mobile-tabbar')||null, viewportInner:innerHeight};});
   console.log(JSON.stringify({w,h,...r},null,0));
 }
 await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
