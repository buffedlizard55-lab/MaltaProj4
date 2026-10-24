// Session a22008ff mobile/desktop measurement of the built board.
// Serves ./public over http (the real Pages path shape), then reports where the
// executive summary links, the first pick card and its percentages land.
const { chromium: playwright } = require('playwright-core');
const chromium = require('@sparticuz/chromium');
const path = require('node:path');
const http = require('node:http');
const fs = require('node:fs');

(async () => {
  const root = path.resolve('public');
  const server = http.createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://t').pathname);
    const file = path.resolve(root, '.' + pathname);
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + server.address().port + '/';
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({
    args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(),
    headless: true,
  });
  console.error('launched');
  const out = {};
  const page = await browser.newPage();
  for (const [w, h] of [[320, 568], [390, 844], [412, 915], [768, 1024], [1440, 900]]) {
    await page.setViewportSize({ width: w, height: h });
    await page.goto(base + 'index.html');
    await page.waitForTimeout(350);
    const picksPage = {};
    {
    out[w + 'x' + h] = await page.evaluate(() => {
      const box = sel => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { y: Math.round(r.top + window.scrollY), h: Math.round(r.height) };
      };
      const links = [...document.querySelectorAll('#exec-summary a, #exec-quicknav a')].map(a => ({
        text: a.textContent.trim(), href: a.getAttribute('href'),
      }));
      const firstCard = document.querySelector('.glance-list li > a, .glance-list li a');
      const numbers = firstCard ? firstCard.querySelectorAll('.numbers') : [];
      return {
        quicknav: box('#exec-quicknav'),
        execSummary: box('#exec-summary'),
        firstCard: box('.glance-list li > a, .glance-list li a'),
        firstCardNumbers: numbers.length ? Math.round(numbers[0].getBoundingClientRect().top + window.scrollY) : null,
        mobileTabs: box('.mobile-tabs'),
        staleBannerVisible: document.querySelector('#runtime-stale') ? !document.querySelector('#runtime-stale').hidden : null,
        cardCount: document.querySelectorAll('.glance-list li').length,
        links,
        overflow: document.documentElement.scrollWidth > window.innerWidth,
      };
    });
    }
    await page.goto(base + 'picks.html');
    await page.waitForTimeout(250);
    out[w + 'x' + h].picksPage = await page.evaluate(() => {
      const card = document.querySelector('tr[data-match]');
      const r = card ? card.getBoundingClientRect() : null;
      return { firstRowY: r ? Math.round(r.top + window.scrollY) : null,
               rows: document.querySelectorAll('tr[data-match]').length,
               overflow: document.documentElement.scrollWidth > window.innerWidth };
    });
    console.error('measured', w, h);
  }
  await browser.close();
  server.close();
  fs.writeFileSync('research/measure_a22008ff.json', JSON.stringify(out, null, 1) + '\n');
  console.log(JSON.stringify(out, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
