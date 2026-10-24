const { chromium: playwright } = require('playwright-core');
const chromium = require('@sparticuz/chromium');
const path = require('node:path'), http = require('node:http'), fs = require('node:fs');
(async () => {
  const root = path.resolve('public');
  const server = http.createServer((req, res) => {
    const p = decodeURIComponent(new URL(req.url, 'http://t').pathname);
    const f = path.resolve(root, '.' + p);
    if (!f.startsWith(root + path.sep) || !fs.existsSync(f)) { res.writeHead(404); res.end(); return; }
    const mime = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(f)] || 'text/plain'); res.end(fs.readFileSync(f));
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + server.address().port + '/';
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({ args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true });
  const page = await browser.newPage();
  for (const [w, h] of [[320, 844], [320, 568]]) {
    await page.setViewportSize({ width: w, height: h });
    await page.goto(base + 'picks.html');
    await page.waitForTimeout(300);
    const blocks = await page.evaluate(() => {
      const out = [];
      const top = el => Math.round(el.getBoundingClientRect().top + window.scrollY);
      document.querySelectorAll('main > *, main > section > *, .filters, .filters > *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.height > 0) out.push({tag: el.tagName.toLowerCase(), cls: el.className || '', id: el.id || '', y: top(el), h: Math.round(r.height)});
      });
      const pick = document.querySelector('tr[data-match] .pick');
      out.push({tag: 'FIRST-PICK', y: pick ? top(pick) : null});
      const prob = document.querySelector('tr[data-match] .prob-pair');
      out.push({tag: 'FIRST-PROB', y: prob ? top(prob) : null});
      return out;
    });
    console.log(w + 'x' + h, JSON.stringify(blocks, null, 0));
  }
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
