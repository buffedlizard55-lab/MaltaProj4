// Session fe7f5de4: measure whether a phone reaches real picks, not just nav.
// The layout clock is pinned to the build's own clock; the other browser suites
// independently exercise real-time expiry and lock withholding.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'data/latest.json'), 'utf8'));
  const buildClock = Date.parse(data.built_at || data.generated_at);
  assert.ok(Number.isFinite(buildClock), 'build clock must be readable');
  const server = http.createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://test').pathname).replace(/^\/MaltaProj4\//, '/');
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
    browser = await playwright.launch({args: chromium.default.args, executablePath: await chromium.default.executablePath(), headless: true});
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(timestamp => { Date.now = () => timestamp; }, buildClock);
    const open = data.matches.filter(m => m.state === 'open');
    for (const width of [320, 390]) {
      await page.setViewportSize({width, height: width === 320 ? 568 : 844});
      await page.goto(base + 'index.html');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `home overflow ${width}`);
      const cta = await page.locator('#freshness-strip .fresh-cta').boundingBox();
      assert.ok(cta && cta.height >= 44 && cta.y + cta.height <= page.viewportSize().height - 60,
        `visible pick-board CTA required at ${width}`);
      const glance = await page.locator('#picks-at-a-glance').boundingBox();
      assert.ok(glance && glance.y < 750, `pick list buried at ${glance?.y}px on ${width}px phone`);
      const cards = page.locator('#picks-at-a-glance .glance-card-mobile');
      assert.equal(await cards.count(), open.length, `every open match needs a home phone card at ${width}`);
      if (open.length) {
        const first = await cards.first().boundingBox();
        assert.ok(first && first.y < 1000, `first actual pick buried at ${first?.y}px on ${width}px phone`);
      }
      await page.locator('#freshness-strip .fresh-cta').click();
      assert.ok(page.url().endsWith('/picks.html'));
      const rows = page.locator('tr[data-match]:visible');
      assert.equal(await rows.count(), open.length, `pick board must contain every open row at ${width}`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `pick board overflow ${width}`);
      if (open.length) {
        const firstRow = await rows.first().boundingBox();
        assert.ok(firstRow && firstRow.y < (width === 320 ? 850 : 750),
          `first full pick/probability row buried at ${firstRow?.y}px on ${width}px phone`);
      }
      for (const match of open) {
        const row = page.locator(`tr[data-match="${match.id}"]`);
        await row.scrollIntoViewIfNeeded();
        assert.equal(await row.count(), 1, `missing ${match.id}`);
        assert.equal(await row.locator('.source-links a[href^="https://"]').count() > 0, true, `official source missing ${match.id}`);
        if (match.probabilities) {
          const percentages = await row.locator('.prob-pair > span').allTextContents();
          assert.equal(percentages.length, 2, `both team percentages required for ${match.id}`);
          assert.ok(percentages.every(text => /^\d+\.\d%$/.test(text.trim())), `bad percentages for ${match.id}: ${percentages}`);
          const pick = (await row.locator('.pick-cell .pick').textContent() || '').trim();
          assert.ok(match.teams.includes(pick), `obvious valid pick required for ${match.id}`);
        } else {
          assert.equal(await row.locator('.prob-pair').count(), 0, `unverified percentage leaked into ${match.id}`);
        }
      }
      report.push({width, home_cta_y: cta.y, home_pick_list_y: glance.y,
        home_first_card_y: open.length ? (await page.goto(base + 'index.html').then(() => cards.first().boundingBox())).y : null,
        open_rows: open.length});
    }
    // Existing deep links must unfold the guide even after the visual reorder.
    for (const id of ['coverage-now', 'start-here', 'exec-banner', 'unresolved-picks']) {
      await page.goto(base + 'index.html#' + id);
      assert.equal(await page.locator('#' + id).isVisible(), true, `deep link ${id} must reveal its target`);
    }
    // The integrated f0814674 safeguard must keep prose and counters in sync
    // when the whole snapshot expires, not only when an individual lock passes.
    for (const pathname of ['index.html', 'unresolved.html']) {
      await page.goto(base + pathname);
      assert.ok(await page.locator('[data-completeness]').count() > 0, `${pathname} needs live completeness prose`);
      await page.evaluate(timestamp => { Date.now = () => timestamp; expire(); }, buildClock + 8 * 3600000 + 1000);
      const prose = await page.locator('[data-completeness]').allTextContents();
      assert.ok(prose.every(text => text.includes('outside its 8-hour evidence window') && text.includes('no current pick is published')),
        `stale prose must withhold current picks on ${pathname}: ${prose}`);
      const picked = page.locator('[data-count="picked"]').first();
      if (await picked.count()) assert.equal((await picked.textContent()).trim(), '0', 'stale picked counter must be zero');
    }
    assert.deepEqual(errors, []);
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-fe7f5de4.json', JSON.stringify(report, null, 2) + '\n');
    console.log('Passed: 320/390px pick placement, all open rows, both team probabilities, official row links, blank safeguards, guide deep links and stale-prose/counter agreement.');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
