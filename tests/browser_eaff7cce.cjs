// A11y scans alone missed the 3,186px trip to the first home-page pick.
// Measure discoverability as well as native-disclosure/hash-link behaviour.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://test').pathname.replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    const mime = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'application/json');
    res.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  const report = [];
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({args: chromium.default.args.filter(a => a !== '--disable-web-security'), executablePath: await chromium.default.executablePath(), headless: true});
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    for (const width of [320, 390]) {
      await page.setViewportSize({width, height: width === 320 ? 568 : 844});
      await page.goto(base + 'index.html');
      const cta = await page.locator('#freshness-strip .fresh-cta').boundingBox();
      assert.ok(cta && cta.height >= 44 && cta.y + cta.height <= page.viewportSize().height - 64,
        `Pick-board CTA must be a first-screen phone tap at ${width}px`);
      const glance = await page.locator('#picks-at-a-glance').boundingBox();
      assert.ok(glance && glance.y < 1700, `First pick list buried at ${glance?.y}px / ${width}px`);
      const height = await page.evaluate(() => document.documentElement.scrollHeight);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      assert.equal(await page.locator('#detailed-summary').getAttribute('open'), null);
      report.push({width, cta_y: cta.y, cta_height: cta.height, first_picks_y: glance.y, page_height: height});
      await page.locator('#freshness-strip .fresh-cta').click();
      assert.ok(page.url().endsWith('/picks.html'));
    }
    // Legacy URLs into folded sections must reveal every ancestor disclosure.
    for (const id of ['unresolved-summary', 'pick-limitations', 'start-here']) {
      await page.goto(base + 'index.html#' + id);
      assert.equal(await page.locator('#' + id).isVisible(), true, `Hidden hash target ${id}`);
      assert.equal(await page.locator('#' + id).evaluate(node => {
        const parents = []; for (let p = node.parentElement; p; p = p.parentElement) if (p.tagName === 'DETAILS') parents.push(p);
        return parents.length > 0 && parents.every(p => p.open);
      }), true, `Every disclosure ancestor of ${id} must open`);
    }
    await page.goto(base + 'index.html');
    const summary = page.locator('#detailed-summary > summary');
    await summary.focus(); await summary.press('Enter');
    assert.equal(await page.locator('#detailed-summary').getAttribute('open'), '');
    await summary.press('Enter');
    assert.equal(await page.locator('#detailed-summary').getAttribute('open'), null);
    await page.goto(base + 'unresolved.html');
    assert.equal(await page.locator('.method-details').getAttribute('open'), null);
    assert.ok(await page.locator('tr[data-match]:visible').count() > 0, 'Research ladder must not hide match records');
    assert.deepEqual(errors, []);
    console.log('Passed: first-screen 44px pick CTA, first list within 1700px at 320/390px, three legacy hidden-anchor reveals, native keyboard disclosures, unresolved records visible.');
  } finally {
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-eaff7cce.json', JSON.stringify(report, null, 2) + '\n');
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
