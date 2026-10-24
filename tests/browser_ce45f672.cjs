// Session ce45f672: the home page's first phone screen must say what it is
// (an executive summary), must show the next pick with both teams' win chances
// above the fixed tab bar, and must not grow taller per card than the board it
// replaced. Measured, not assumed: every number below is read from the built
// page with Chromium at the two phone viewports the other suites use.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'data/latest.json'), 'utf8'));
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
  const open = data.matches.filter(m => m.state === 'open');
  const picks = open.filter(m => m.pick && m.probabilities);
  let browser;
  const report = [];
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true});
    const page = await (await browser.newContext()).newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));

    for (const [width, height] of [[320, 568], [390, 844]]) {
      await page.setViewportSize({width, height});
      await page.goto(base + 'index.html');
      const measured = await page.evaluate(() => {
        const box = el => {
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return {y: Math.round(r.top + scrollY), bottom: Math.round(r.bottom + scrollY), height: Math.round(r.height)};
        };
        const cards = [...document.querySelectorAll('#picks-at-a-glance .glance-card-mobile')]
          .filter(card => getComputedStyle(card).display !== 'none');
        const first = cards[0] || null;
        const scores = first ? [...first.querySelectorAll('.glance-card-score')] : [];
        const title = document.querySelector('#freshness-strip .fresh-title');
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          title: box(title),
          titleText: title ? title.textContent.trim() : null,
          tabbar: box(document.querySelector('.mobile-tabs')),
          card: box(first),
          cards: cards.length,
          scores: scores.map(box),
          scoreText: scores.map(node => node.textContent.replace(/\s+/g, ' ').trim()),
          time: first ? (first.querySelector('.glance-card-time') || {}).textContent || null : null,
          pickLabel: first ? (first.querySelector('.glance-card-pick-label') || {}).textContent || null : null,
          cta: box(document.querySelector('#freshness-strip a.fresh-cta')),
          unresolved: box(document.querySelector('#freshness-strip a[href="unresolved.html"]')),
          matchesLink: box(document.querySelector('.mobile-tabs a[href="matches.html"]')),
          picksLink: box(document.querySelector('.mobile-tabs a[href="picks.html"]')),
        };
      });
      report.push({viewport: `${width}x${height}`, ...measured});

      assert.equal(measured.overflow, false, `${width}px home page overflows horizontally`);
      // 1. The first screen names itself as the executive summary.
      assert.equal(measured.titleText, 'Executive summary', `${width}px executive-summary label text`);
      assert.ok(measured.title && measured.title.y < measured.tabbar.y,
        `${width}px the executive-summary label is not on the first screen: ${JSON.stringify(measured.title)}`);
      // 2. The next pick and both teams' win chances are above the fixed tab bar.
      assert.ok(measured.card, `${width}px no phone pick card rendered`);
      assert.ok(measured.card.y < measured.tabbar.y,
        `${width}px the first pick card is below the tab bar: ${JSON.stringify(measured.card)}`);
      assert.equal(measured.scores.length, 2, `${width}px a pick card must print both teams' win chances`);
      for (const score of measured.scores) {
        assert.ok(score && score.bottom <= measured.tabbar.y,
          `${width}px a win probability is hidden behind the tab bar: ${JSON.stringify(measured.scores)}`);
      }
      assert.ok(measured.time && /\d{1,2} \w{3} · \d{2}:\d{2} UTC$/.test(measured.time),
        `${width}px the card must still state its start time, got ${JSON.stringify(measured.time)}`);
      assert.match(measured.pickLabel, /PICK|UNRESOLVED/,
        `${width}px the card must label the pick, got ${JSON.stringify(measured.pickLabel)}`);
      // 3. The in-site routes to the picks, the unresolved section and the rest
      //    of the board are real tap targets on the first screen.
      for (const [name, target] of [['picks CTA', measured.cta], ['unresolved link', measured.unresolved],
        ['picks tab', measured.picksLink], ['matches tab', measured.matchesLink]]) {
        assert.ok(target && target.height >= 44,
          `${width}px the ${name} is not a phone-sized tap target: ${JSON.stringify(target)}`);
      }
      // 4. Density guard: the card may not grow past the measured 246px budget.
      assert.ok(measured.card.height <= 246,
        `${width}px the pick card grew to ${measured.card.height}px, past the 246px phone budget`);
      // 5. Every open match still has a card (coverage is not traded for density).
      assert.equal(measured.cards, open.length,
        `${width}px ${measured.cards} cards for ${open.length} open matches`);

      // The pick board the summary points at is one tap away and carries every
      // open row with its probabilities.
      await page.locator('#freshness-strip a.fresh-cta').click();
      assert.ok(page.url().endsWith('/picks.html'), `${width}px the picks CTA must lead to picks.html`);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false,
        `${width}px picks page overflows horizontally`);
      assert.equal(await page.locator('tr[data-match]:visible').count(), open.length,
        `${width}px the pick board must list every open match`);
    }

    // A phone reader must never see a fabricated number where a pick is missing.
    await page.setViewportSize({width: 320, height: 568});
    await page.goto(base + 'index.html');
    const blanks = await page.evaluate(() => [...document.querySelectorAll('#picks-at-a-glance .glance-card-mobile')]
      .filter(card => card.dataset.glancePriced === '0')
      .map(card => card.textContent));
    assert.ok(blanks.every(text => !/50\/50/.test(text)), 'an unpriced card must never show a 50/50 default');

    assert.deepEqual(errors, []);
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-ce45f672.json', JSON.stringify({picks: picks.length, report}, null, 2) + '\n');
    await page.screenshot({path: 'runtime/index-320-ce45f672.png'});
    console.log('Passed: the phone home page names itself an executive summary, keeps the next pick and both win '
      + 'chances above the tab bar at 320/390px, keeps every in-site route a 44px tap target, holds the 246px card '
      + 'budget and renders one card per open match.');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
