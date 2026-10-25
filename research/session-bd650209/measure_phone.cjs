// Session bd650209: first-hand phone measurements of the built board.
// Serves ./public over a real HTTP origin, opens the executive summary and the
// pick board at three phone viewports, and records what a reader actually sees:
// where the executive summary sits, where the first pick card is, whether the
// first pick's two percentages are above the fixed tab bar, and whether any
// page scrolls sideways. Numbers in the delivery report come from this file.
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
  await new Promise(r => server.listen(0, '0.0.0.0', r));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({
    args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true,
  });
  const page = await browser.newPage();
  const out = [];
  for (const [width, height] of [[320, 568], [390, 844], [414, 896]]) {
    await page.setViewportSize({width, height});
    await page.goto(base + 'index.html');
    const summary = await page.evaluate(() => {
      const pick = (sel) => { const el = document.querySelector(sel); if (!el) return null;
        const r = el.getBoundingClientRect(); return {top: Math.round(r.top), height: Math.round(r.height)}; };
      const bar = document.querySelector('.exec-quicknav, #exec-summary');
      const tabs = document.querySelector('.mobile-tabs');
      return {quicknav: pick('.exec-quicknav'), execBar: pick('#exec-summary'), firstCard: pick('.pick-card, tr[data-match]'),
              tabs: tabs ? Math.round(tabs.getBoundingClientRect().top) : null,
              innerText: (bar && bar.innerText || '').replace(/\s+/g, ' ').slice(0, 220)};
    });
    await page.goto(base + 'picks.html');
    const board = await page.evaluate(() => {
      const first = document.querySelector('tr[data-match]');
      const tabs = document.querySelector('.mobile-tabs');
      const pairs = [...document.querySelectorAll('tr[data-match] .prob-pair')].slice(0, 3)
        .map(el => el.innerText.replace(/\s+/g, ' ').trim());
      const firstRect = first && first.getBoundingClientRect();
      const probRect = first && first.querySelector('.prob-pair') && first.querySelector('.prob-pair').getBoundingClientRect();
      return {rows: document.querySelectorAll('tr[data-match]').length,
              firstRowTop: firstRect ? Math.round(firstRect.top) : null,
              firstProbPairBottom: probRect ? Math.round(probRect.bottom) : null,
              tabsTop: tabs ? Math.round(tabs.getBoundingClientRect().top) : null,
              firstThreePairs: pairs,
              overflow: document.documentElement.scrollWidth > window.innerWidth};
    });
    out.push({viewport: `${width}x${height}`, index: summary, picks: board});
  }
  await browser.close();
  server.close();
  fs.mkdirSync('research/session-bd650209', {recursive: true});
  fs.writeFileSync('research/session-bd650209/phone-measurements.json', JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
})().catch(err => { console.error(err); process.exit(1); });
