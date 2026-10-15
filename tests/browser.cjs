const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');
const {default: AxeBuilder} = require('@axe-core/playwright');

(async()=>{
  const root = path.resolve('public');
  const data = JSON.parse(fs.readFileSync(path.join(root,'data/latest.json'),'utf8'));
  const server = http.createServer((req,res)=>{
    const url = new URL(req.url,'http://test');
    const pathname = decodeURIComponent(url.pathname).replace(/^\/MaltaProj4\//,'/');
    const file = path.resolve(root,'.'+pathname+(pathname.endsWith('/')?'index.html':''));
    if (!file.startsWith(root+path.sep) || !fs.existsSync(file)) {res.writeHead(404);res.end();return;}
    const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'};
    res.setHeader('content-type',mime[path.extname(file)]||'text/plain');res.end(fs.readFileSync(file));
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const base=`http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  const report=[];
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser=await playwright.launch({args:chromium.default.args.filter(a=>a!=='--disable-web-security'),executablePath:await chromium.default.executablePath(),headless:true});
    const context=await browser.newContext();
    const page=await context.newPage();
    const errors=[];page.on('pageerror',err=>errors.push(err.message));
    for (const width of [320,390,768,1440]) {
      await page.setViewportSize({width,height:900});
      for (const slug of ['index','picks','matches','unresolved','review','sources','evidence']) {
        const response=await page.goto(base+slug+'.html');assert.equal(response.status(),200);
        const overflow=await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth);
        assert.equal(overflow,false,`${slug} overflows at ${width}px`);
        const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
        const failures=results.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}));
        report.push({page:slug,width,violations:failures});
        assert.deepEqual(failures,[],`${slug} accessibility at ${width}px: ${JSON.stringify(failures)}`);
      }
    }
    await page.setViewportSize({width:390,height:844});
    await page.goto(base+'matches.html?status=open');
    const openCount=data.matches.filter(m=>m.state==='open' && Date.parse(m.lock)>Date.now() && Date.parse(m.start)>Date.now()).length;
    assert.equal(await page.locator('tr[data-match]:visible').count(),openCount);
    await page.locator('#search').fill('no-such-fixture-xyz');
    assert.equal(await page.locator('tr[data-match]:visible').count(),0);
    assert.equal(await page.locator('#filter-empty').isVisible(),true);
    await page.getByRole('button',{name:'Reset',exact:true}).click();
    assert.equal(await page.locator('tr[data-match]:visible').count(),data.matches.length);
    const first=data.matches[0];
    await page.goto(base+'evidence.html#match-'+first.id);
    assert.equal(await page.locator('#match-'+first.id).getAttribute('open'),'');
    await page.goto(base+'index.html');
    await page.getByRole('link',{name:'View updated picks'}).click();
    assert.ok(page.url().endsWith('/picks.html'));
    await page.goto(base+'index.html');
    await page.screenshot({path:'runtime/mobile.png',fullPage:true});
    await page.setViewportSize({width:1440,height:1100});
    await page.screenshot({path:'runtime/desktop.png',fullPage:true});
    await page.addInitScript(()=>{Date.now=()=>new Date('2099-01-01T00:00:00Z').getTime()});
    await page.goto(base+'picks.html');
    assert.equal(await page.locator('#runtime-stale').isVisible(),true);
    assert.equal(await page.locator('.prob-pair').count(),0,'Expired probabilities must not look actionable');
    assert.equal(await page.locator('.pick-cell .pick').count(),0,'Expired picks must be withheld');
    assert.deepEqual(errors,[]);
    console.log('Passed: 28 page/viewport accessibility scans, 320/390/768/1440px layout, subpath URLs, navigation, filters, evidence anchors and expiry.');
  } finally {
    fs.mkdirSync('runtime',{recursive:true});fs.writeFileSync('runtime/browser-report.json',JSON.stringify(report,null,2));
    if(browser)await browser.close();await new Promise(r=>server.close(r));
  }
})().catch(err=>{console.error(err);process.exit(1)});
