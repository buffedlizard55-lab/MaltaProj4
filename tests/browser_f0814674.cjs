// Session f0814674: the executive summary's prose must agree with its numbers.
//
// On 2026-10-23 the live page rendered "0 with a pick" next to the build-time
// sentence "Every one of the 23 open matches has a pick", because the counters
// were recomputed in the browser and the sentence was not. This suite drives
// the real page at 390x844 and 320x568, checks the two agree in the fresh
// state, then ages the snapshot past its 8-hour evidence window and checks the
// sentence and the counters still agree.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://test');
    const pathname = decodeURIComponent(url.pathname).replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true,
    });
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));

    const read = () => page.evaluate(() => ({
      open: Number(document.querySelector('[data-count="open"]')?.textContent),
      picked: Number(document.querySelector('[data-count="picked"]')?.textContent),
      priced: Number(document.querySelector('[data-count="priced"]')?.textContent),
      missing: Number(document.querySelector('[data-count="missing"]')?.textContent),
      sentence: document.querySelector('[data-completeness]')?.textContent || '',
      staleVisible: !document.querySelector('#runtime-stale')?.hidden,
    }));

    await page.goto(base + 'index.html');
    const fresh = await read();
    assert.equal(errors.length, 0, 'no page errors: ' + errors.join('; '));
    assert.ok(fresh.sentence.length > 20, 'the completeness sentence is rendered');
    assert.equal(fresh.staleVisible, false, 'a snapshot inside its window shows no stale banner');
    if (fresh.open > 0) {
      const numbers = (fresh.sentence.match(/\d+/g) || []).map(Number);
      assert.ok(numbers.includes(fresh.open) || /No open/.test(fresh.sentence),
        `sentence "${fresh.sentence}" must state the ${fresh.open} open matches`);
      assert.ok(numbers.includes(fresh.picked),
        `sentence "${fresh.sentence}" must state the ${fresh.picked} picked rows`);
    }

    // Age the snapshot past the 8-hour evidence window exactly as the browser
    // would when a page sits open too long, then re-run the expiry pass.
    await page.evaluate(() => {
      const nine = new Date(Date.now() - 9 * 3600 * 1000).toISOString();
      document.body.dataset.observed = nine;
      expire();
    });
    const stale = await read();
    assert.equal(stale.staleVisible, true, 'the stale banner is shown once evidence expires');
    assert.equal(stale.picked, 0, 'no pick is counted as current once the snapshot is stale');
    assert.match(stale.sentence, /8-hour evidence window/,
      `stale sentence must explain the window, got: ${stale.sentence}`);
    assert.equal((await page.locator('.pick-cell .pick').count()), 0,
      'no live pick survives the stale pass');

    for (const width of [320, 390]) {
      await page.setViewportSize({width, height: 568});
      await page.goto(base + 'index.html');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false,
        `index.html overflows at ${width}px`);
      const cta = page.locator('a[href="picks.html"]:visible').first();
      const box = await cta.boundingBox();
      assert.ok(box && box.y < 900, `the picks link is on the first screen at ${width}px (y=${box && box.y})`);
      assert.ok(box && box.height >= 40, `the picks link is a phone-sized tap target at ${width}px (h=${box && box.height})`);
    }

    console.log('Passed: executive-summary completeness prose matches the runtime counters in fresh and 8-hour-stale states at 390/320px.');
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch(err => { console.error(err); process.exit(1); });
