// Session 4ed657ce: reproduce the phone/desktop discoverability measurements.
// Usage: node research/session-4ed657ce/measure_mobile.cjs [public-dir]
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve(process.argv[2] || 'public');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'data/latest.json'), 'utf8'));
  const fixed = Date.parse(data.fixtures_observed_at) + 14 * 60 * 1000;
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://test');
    const pathname = decodeURIComponent(url.pathname).replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    const mime = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({args: chromium.default.args.filter(a => a !== '--disable-web-security'), executablePath: await chromium.default.executablePath(), headless: true});
    const report = [];
    const context = await browser.newContext({viewport:{width:320,height:568}});
    await context.addInitScript(fixedTime => {
      const RealDate = Date;
      class FakeDate extends RealDate {
        constructor(...args) { if (args.length === 0) super(fixedTime); else super(...args); }
        static now() { return fixedTime; }
      }
      window.Date = FakeDate;
    }, fixed);
    const page = await context.newPage();
    const errors=[]; page.on('pageerror', e => errors.push(e.message));
    for (const [width, height] of [[320,568],[390,844],[768,1024],[1440,900]]) {
      await page.setViewportSize({width,height});
      const response = await page.goto(base + 'index.html', {waitUntil:'load'});
      assert.equal(response.status(), 200);
      const box = async sel => page.locator(sel).first().boundingBox();
      const exec = await box('#exec-summary');
      const glance = await box('#picks-at-a-glance');
      const firstCard = await box('.glance-card-mobile');
      const limits = await box('#unresolved-limits');
      const folded = await box('#unresolved-summary');
      const strip = await box('#freshness-strip');
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
      const staleVisible = await page.locator('#runtime-stale').isVisible();
      const firstText = (await page.locator('.glance-card-mobile').first().innerText()).replace(/\s+/g,' ').trim();
      const execText = (await page.locator('#exec-summary').innerText()).replace(/\s+/g,' ').trim();
      const hrefs = await page.locator('#exec-summary a').evaluateAll(as => as.map(a => a.getAttribute('href')));
      const tab = await box('.mobile-tabs');
      const quick = await box('#exec-quicknav');
      const answer = await box('.glance-card-mobile .glance-card-scores');
      await page.locator('#exec-summary a[href="#unresolved-summary"]').first().click();
      const foldedVisibleAfter = await page.locator('#unresolved-summary').isVisible();
      const detailsOpen = await page.locator('details.briefing-more').first().getAttribute('open');
      const limitsInExec = hrefs.includes('#unresolved-limits');
      const entry = {
        width, height, execY: exec && Math.round(exec.y), stripY: strip && Math.round(strip.y),
        picksSectionY: glance && Math.round(glance.y), firstCardY: firstCard && Math.round(firstCard.y),
        unresolvedLimitsY: limits && Math.round(limits.y), foldedSummaryY: folded && Math.round(folded.y),
        tabTop: tab && Math.round(tab.y), quickNavY: quick && Math.round(quick.y),
        answerY: answer && Math.round(answer.y), answerAboveTab: !!answer && !!tab && answer.y < tab.y,
        firstCardAboveTab: !!firstCard && !!tab && firstCard.y < tab.y,
        overflow, staleVisible, foldedVisibleAfter, detailsOpen,
        limitsLinkedFromExec: limitsInExec, execHrefs: hrefs,
        firstCardText: firstText, execText, errors: [...errors]
      };
      report.push(entry);
      assert.equal(overflow, false, `${width}px overflow`);
      assert.equal(staleVisible, false, `${width}px false stale notice`);
      assert.equal(errors.length, 0, `${width}px page errors`);
      console.log(`${width}x${height}: strip y=${entry.stripY}, exec y=${entry.execY}, picks y=${entry.picksSectionY}, first card y=${entry.firstCardY}, tab y=${entry.tabTop}, unresolved-limits y=${entry.unresolvedLimitsY}, overflow=${overflow}, stale=${staleVisible}, folded-link-target-visible=${foldedVisibleAfter}, exec-links-limits=${limitsInExec}`);
      console.log(`  first card: ${firstText}`);
      errors.length = 0;
    }
    await context.close();
    fs.writeFileSync('research/session-4ed657ce/mobile-measurements.json', JSON.stringify(report,null,2)+'\n');
    console.log('Wrote research/session-4ed657ce/mobile-measurements.json');
  } finally {
    if (browser) await browser.close();
    await new Promise(r => server.close(r));
  }
})().catch(err => { console.error(err); process.exit(1); });
