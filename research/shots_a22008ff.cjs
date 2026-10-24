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
  await page.setViewportSize({ width: 390, height: 844 });
  for (const slug of ['index','picks','unresolved']) {
    await page.goto(base + slug + '.html');
    await page.waitForTimeout(400);
    await page.screenshot({ path: `research/shot-${slug}-390.png` });
  }
  await browser.close(); server.close();
  console.log('shots written');
})().catch(e => { console.error(e); process.exit(1); });
