// Regression: a missing brace once nested every later phone-first rule inside
// max-height:700px. Verify computed order and real pick/probability placement
// on a short phone and a tall phone, not just stylesheet text.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const server = http.createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://test').pathname)
      .replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) {
      res.writeHead(404); res.end(); return;
    }
    const mime = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
      '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  const report = [];
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(arg => arg !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true,
    });
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    for (const [width, height] of [[320, 568], [390, 844]]) {
      await page.setViewportSize({width, height});
      await page.goto(base + 'index.html');
      const measured = await page.evaluate((shortPhone) => {
        if (shortPhone) {
          // Measure the fresh-page chrome without changing any match value.
          // The committed bootstrap can legitimately be stale on an offline PR.
          document.querySelector('#runtime-stale').hidden = true;
          const strip = document.querySelector('#freshness-strip');
          strip.classList.remove('stale');
          strip.classList.add('live');
        }
        const top = element => element
          ? Math.round(element.getBoundingClientRect().top + scrollY) : null;
        const card = document.querySelector('#picks-at-a-glance .glance-card-mobile');
        const scores = card?.querySelector('.glance-card-scores');
        const answer = scores || card?.querySelector('.glance-card-pick');
        const guide = document.querySelector('details.briefing-more');
        const cta = document.querySelector('#freshness-strip a.fresh-cta');
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          mainDisplay: getComputedStyle(document.querySelector('main')).display,
          cardOrder: getComputedStyle(document.querySelector('#picks-at-a-glance')).order,
          guideOrder: getComputedStyle(guide).order,
          cardTop: top(card),
          answerTop: top(answer),
          numericProbability: Boolean(scores),
          tabTop: top(document.querySelector('.mobile-tabs')),
          ctaHeight: cta?.getBoundingClientRect().height || 0,
          unresolvedSection: Boolean(document.querySelector('#unresolved-limits')),
          unresolvedLink: Boolean(document.querySelector('#freshness-strip a[href="unresolved.html"]')),
        };
      }, height < 700);
      assert.equal(measured.overflow, false, `${width}px horizontal overflow`);
      assert.equal(measured.mainDisplay, 'flex', `${width}px phone-first layout is not active`);
      assert.ok(Number(measured.cardOrder) < Number(measured.guideOrder),
        `${width}px picks must precede the reference guide: ${JSON.stringify(measured)}`);
      assert.ok(measured.cardTop !== null && measured.cardTop < measured.tabTop,
        `${width}px first match is not above the fixed tab bar: ${JSON.stringify(measured)}`);
      assert.ok(measured.answerTop !== null && measured.answerTop < measured.tabTop,
        `${width}px pick/probability answer is not above the fixed tab bar: ${JSON.stringify(measured)}`);
      assert.ok(measured.ctaHeight >= 44, `${width}px pick CTA is too small`);
      assert.ok(measured.unresolvedSection && measured.unresolvedLink,
        `${width}px unresolved limitations must stay linked from the summary`);
      report.push({width, height, ...measured});
    }
    assert.deepEqual(errors, []);
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-cb16f548.json', JSON.stringify(report, null, 2) + '\n');
    console.log('Passed: phone-first computed order, match/probability placement, 44px pick CTA, and unresolved links at 320x568 and 390x844.');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
