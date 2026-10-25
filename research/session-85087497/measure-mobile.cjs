// Session 85087497: measure the first phone screen of the built landing page.
// Reports (does not assert) where the executive summary, its pick links and the
// first pick card land at common phone sizes, plus tap-target and overflow facts.
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
  const out = [];
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({args: chromium.default.args.filter(a => a !== '--disable-web-security'), executablePath: await chromium.default.executablePath(), headless: true});
    const page = await (await browser.newContext()).newPage();
    for (const [w, h] of [[320, 568], [390, 844], [412, 915]]) {
      for (const slug of ['index', 'picks', 'unresolved']) {
        await page.setViewportSize({width: w, height: h});
        await page.goto(base + slug + '.html');
        const m = await page.evaluate(({slug}) => {
          const y = sel => { const el = document.querySelector(sel); if (!el) return null; const r = el.getBoundingClientRect(); return {top: Math.round(r.top), height: Math.round(r.height), visible: r.height > 0 && getComputedStyle(el).display !== 'none'}; };
          const text = sel => { const el = document.querySelector(sel); return el ? el.textContent.trim().replace(/\s+/g, ' ').slice(0, 160) : null; };
          const tap = [...document.querySelectorAll('a,button')].filter(a => { const r = a.getBoundingClientRect(); return r.height > 0 && r.top >= 0 && r.top < innerHeight; })
            .map(a => { const r = a.getBoundingClientRect(); return {label: a.textContent.trim().replace(/\s+/g, ' ').slice(0, 40), href: a.getAttribute('href'), h: Math.round(r.height)}; });
          const small = tap.filter(t => t.h < 24);
          return {
            slug, overflow: document.documentElement.scrollWidth > innerWidth,
            scrollHeight: document.documentElement.scrollHeight,
            sections: {
              freshStrip: y('.fresh-strip'), execBar: y('#exec-summary'), execQuicknav: y('#exec-quicknav'),
              glance: y('#picks-at-a-glance'), firstGlanceCard: y('#picks-at-a-glance .card, #picks-at-a-glance li, #picks-at-a-glance a'),
              unresolvedSummary: y('#unresolved-summary'), unresolvedLimits: y('#unresolved-limits'),
              tabbar: y('.tabbar, nav.bottom, [class*="tab"]'),
            },
            execQuicknavText: text('#exec-quicknav'),
            firstScreenLinks: tap.slice(0, 14), smallTargetsOnFirstScreen: small.length,
            bodyFont: getComputedStyle(document.body).fontSize,
          };
        }, {slug});
        out.push({viewport: `${w}x${h}`, ...m});
      }
    }
    console.log(JSON.stringify(out, null, 1));
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})();
