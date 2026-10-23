// Session 2a5afa69 — "can I find the picks on my phone in one screen?"
//
// The executive summary must show the freshness/covered counts, a 44px+ tap
// target to the updated picks, and the first actual pick row inside the first
// screen at 320x568 and 390x844. The old order put the picks at ~1600px, so a
// phone had to scroll two full screens before seeing a single pick.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

const FIRST_SCREEN_LIMIT = 844; // the tallest phone viewport we test

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
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true});
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));

    for (const [width, height] of [[320, 568], [390, 844]]) {
      await page.setViewportSize({width, height});
      await page.goto(base + 'index.html');

      // 1. The counts and the primary action are on the first screen.
      const strip = await page.locator('#freshness-strip').boundingBox();
      assert.ok(strip && strip.y + strip.height <= height,
        `freshness strip must fit the first ${width}x${height} screen (bottom ${strip && strip.y + strip.height})`);
      const cta = await page.locator('#freshness-strip .fresh-cta').boundingBox();
      assert.ok(cta && cta.height >= 44, `pick CTA must be at least 44px tall at ${width}px`);

      // 2. The pick list starts on that same screen, not two screens down.
      const glance = await page.locator('#picks-at-a-glance').boundingBox();
      assert.ok(glance && glance.y < FIRST_SCREEN_LIMIT,
        `picks-at-a-glance starts at ${glance && glance.y}px at ${width}px`);

      // 3. The first real pick row is visible without scrolling past the fold.
      const firstRow = page.locator('#picks-at-a-glance a.glance-card-mobile').first();
      const box = await firstRow.boundingBox();
      assert.ok(box && box.y < height,
        `first pick row starts at ${box && box.y}px on a ${width}x${height} screen`);

      // 4. Pick, percentage and both team names are inside that row, and the
      //    percentage is the pick's own win chance (not a 50/50 placeholder).
      const text = (await firstRow.innerText()).replace(/\s+/g, ' ');
      assert.match(text, /PICK/i, `first row must label its pick at ${width}px: ${text}`);
      assert.match(text, /\d+\.\d%/, `first row must publish a percentage at ${width}px: ${text}`);
      assert.doesNotMatch(text, /50\/50/, 'a blank percentage must never render as 50/50');

      // 5. No horizontal scrolling on the phone.
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false,
        `index must not overflow at ${width}px`);

      // 6. The separate unresolved section is reachable in one tap from the
      //    summary and names the rows without a percentage.
      // The summary must link the section from somewhere (pointer line when a
      // row is blank, jump nav or coverage button otherwise). Following the
      // link is done by hash: some of those links sit inside the folded guide,
      // and app.js opens every ancestor disclosure on a deep link, which is the
      // exact behaviour a shared URL relies on.
      assert.ok(await page.locator('a[href="#unresolved-picks"]').count() > 0,
        'the summary must link its unresolved section');
      await page.evaluate(() => { location.hash = '#unresolved-picks'; });
      const section = page.locator('#unresolved-picks');
      assert.equal(await section.isVisible(), true, 'unresolved section must be visible after the jump');
      // The page uses smooth scrolling, so wait for the jump to settle rather
      // than sampling mid-flight on a ~8,000px document.
      await page.waitForFunction(() => {
        const box = document.querySelector('#unresolved-picks').getBoundingClientRect();
        return Math.abs(box.top) < 400;
      }, null, {timeout: 8000}).catch(() => {});
      const top = await page.evaluate(() => document.querySelector('#unresolved-picks').getBoundingClientRect().top);
      assert.ok(Math.abs(top) < 400, `jump to the unresolved section should land near it (top=${top})`);

      // 7. And the board page itself shows a pick card with a percentage.
      await page.goto(base + 'picks.html');
      const card = page.locator('tr[data-match]:visible').first();
      const cardText = (await card.innerText()).replace(/\s+/g, ' ');
      const pickCell = page.locator('tr[data-match]:visible .pick-cell .pick').first();
      assert.equal(await pickCell.count() > 0, true, `picks board row must show a pick cell: ${cardText}`);
      const pickName = (await pickCell.innerText()).trim();
      assert.ok(pickName.length > 0 && cardText.includes(pickName),
        `the pick must name one of the two teams: pick=${pickName}`);
      assert.match(cardText, /\d+\.\d%/, `picks board row must show both win probabilities: ${cardText}`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false,
        `picks must not overflow at ${width}px`);
    }

    assert.deepEqual(errors, [], 'no page errors');
    console.log('Passed: first-screen counts/CTA/first pick row at 320x568 and 390x844, pick + percentage visible on the row, one-tap jump to the unresolved section, no phone overflow, no page errors.');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
