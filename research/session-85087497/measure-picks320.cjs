// Session 85087497: why does the first picks.html row miss the 320x568 fold?
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');
(async () => {
  const root = path.resolve(process.argv[2] || 'public');
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
    browser = await playwright.launch({args: chromium.default.args.filter(a => a !== '--disable-web-security'), executablePath: await chromium.default.executablePath(), headless: true});
    const page = await browser.newPage({viewport: {width: 320, height: 568}});
    for (const slug of ['picks', 'index']) {
      await page.goto(base + slug + '.html');
      const out = await page.evaluate(() => {
        const box = el => { if (!el) return null; const r = el.getBoundingClientRect(); return {top: Math.round(r.top + scrollY), bottom: Math.round(r.bottom + scrollY), h: Math.round(r.height)}; };
        const row = document.querySelector('tr[data-match]');
        const blocks = [...document.querySelectorAll('body > *, main > *')].slice(0, 14).map(el => ({
          tag: el.tagName, cls: (el.className || '').toString().slice(0, 50), id: el.id || '', ...box(el),
          text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 90)}));
        return {
          blocks,
          firstRow: row ? {box: box(row), match: row.getAttribute('data-match'), text: row.textContent.trim().replace(/\s+/g, ' ').slice(0, 240),
            pick: box(row.querySelector('.pick')), prob: box(row.querySelector('.prob-pair, .research-prob')),
            cells: [...row.querySelectorAll('td')].map(td => ({cls: td.className, ...box(td), text: td.textContent.trim().replace(/\s+/g, ' ').slice(0, 70)}))} : null,
          tab: box(document.querySelector('.mobile-tabs')),
          card: box(document.querySelector('#picks-at-a-glance a.glance-card-mobile')),
        };
      });
      console.log('=== ' + slug + ' ===');
      console.log(JSON.stringify(out, null, 1));
    }
  } finally { if (browser) await browser.close(); server.close(); }
})();
