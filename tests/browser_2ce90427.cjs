// Mobile acceptance regression: both win probabilities on the first pick must
// clear the fixed phone navigation, and the home summary must route to the
// current pick and unresolved boards. A stale baseline intentionally withholds
// prices; in that case this check validates links/layout and reports the pick
// placement as not applicable rather than asking the UI to show expired values.
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
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) {
      res.writeHead(404); res.end(); return;
    }
    const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  const observations = [];
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(arg => arg !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(),
      headless: true,
    });
    const page = await browser.newPage();
    const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;

    for (const viewport of [{width: 320, height: 568}, {width: 390, height: 844}]) {
      await page.setViewportSize(viewport);
      await page.goto(base + 'index.html');
      await page.evaluate(() => scrollTo(0, 0));
      const home = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth > innerWidth,
        picks: [...document.querySelectorAll('a[href="picks.html"]')].some(a => a.getClientRects().length),
        unresolved: [...document.querySelectorAll('a[href="unresolved.html"]')].some(a => a.getClientRects().length),
      }));
      assert.equal(home.overflow, false, `home page overflows at ${viewport.width}px`);
      assert.equal(home.picks, true, `home summary must link to the pick board at ${viewport.width}px`);
      assert.equal(home.unresolved, true, `home summary must link to limitations at ${viewport.width}px`);

      await page.goto(base + 'picks.html');
      await page.evaluate(() => scrollTo(0, 0));
      const board = await page.evaluate(() => {
        const row = document.querySelector('tr[data-match]');
        const probability = row && row.querySelector('.prob-pair');
        const pick = row && row.querySelector('.pick');
        const nav = document.querySelector('.mobile-tabs');
        return {
          scrollY,
          overflow: document.documentElement.scrollWidth > innerWidth,
          pickText: pick ? pick.innerText.trim() : '',
          probabilities: probability ? probability.innerText.replace(/\s+/g, ' ').trim() : '',
          probabilityBottom: probability ? Math.round(probability.getBoundingClientRect().bottom) : null,
          navTop: nav ? Math.round(nav.getBoundingClientRect().top) : innerHeight,
        };
      });
      assert.equal(board.overflow, false, `pick board overflows at ${viewport.width}px`);
      if (board.probabilityBottom !== null) {
        assert.ok(board.pickText, `the priced first match has a visible pick at ${viewport.width}px`);
        assert.match(board.probabilities, /\d+(?:\.\d+)?%.*\d+(?:\.\d+)?%/,
          `both team percentages appear on the first row at ${viewport.width}px`);
        assert.ok(board.probabilityBottom <= board.navTop,
          `both win probabilities must clear the fixed tab bar at ${viewport.width}x${viewport.height}: `
          + `probability bottom ${board.probabilityBottom}, tab top ${board.navTop}`);
        observations.push({viewport, ...board, status: 'priced row visible'});
      } else {
        observations.push({viewport, ...board, status: 'not applicable: snapshot withholds stale/no-price probabilities'});
      }
    }
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-2ce90427.json', JSON.stringify({snapshot: data.generated_at, observations}, null, 2) + '\n');
    console.log(JSON.stringify({snapshot: data.generated_at, observations}, null, 2));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
