// Measure phone geometry of public/index.html (session 174afa4f tuning).
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'data/latest.json'), 'utf8'));
  const buildClock = Date.parse(data.built_at || data.generated_at);
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
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({args: chromium.default.args, executablePath: await chromium.default.executablePath(), headless: true});
  const page = await browser.newPage();
  await page.addInitScript(timestamp => { Date.now = () => timestamp; }, buildClock);
  for (const width of [320, 390]) {
    await page.setViewportSize({width, height: width === 320 ? 568 : 844});
    await page.goto(base + 'index.html');
    const out = await page.evaluate(() => {
      const box = sel => { const el = document.querySelector(sel); if (!el) return null;
        const r = el.getBoundingClientRect(); return {y: Math.round(r.y + scrollY), h: Math.round(r.height)}; };
      return {
        header: box('header'),
        pageHead: box('.page-head'),
        h1: box('.page-head h1'),
        pill: box('.date-pill'),
        freshMain: box('.fresh-main'),
        freshLinks: box('.fresh-links'),
        freshNext: box('.fresh-next'),
        details: box('details.briefing-more'),
        stale: box('#stale-banner'),
        execEyebrow: box('#exec-summary .eyebrow'),
        fresh: box('#freshness-strip'),
        freshCta: box('#freshness-strip .fresh-cta'),
        exec: box('#exec-summary'),
        execAnswer: box('.exec-summary-answer'),
        execCounts: box('.exec-summary-counts'),
        execActions: box('.exec-summary-actions'),
        execSmall: box('#exec-summary .small'),
        glance: box('#picks-at-a-glance'),
        firstCard: box('#picks-at-a-glance .glance-card-mobile'),
        viewportH: innerHeight,
      };
    });
    console.log(width + 'px:', JSON.stringify(out));
  }
  await browser.close();
  server.close();
})().catch(error => { console.error(error); process.exit(1); });
