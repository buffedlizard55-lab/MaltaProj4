/* Session 5717f7d9 — independent mobile render probe.
 * Serves the committed repository root (the legacy main:/ Pages bytes) and
 * drives headless Chromium at real phone widths. Independent of the shared
 * tests/browser*.cjs suites; writes a dated JSON receipt next to this file.
 */
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium: playwright } = require('playwright-core');
const chromium = require('@sparticuz/chromium');

const ROOT = path.resolve(__dirname, '..', '..');

const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon' };
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://test');
  let pathname = decodeURIComponent(url.pathname).replace(/^\/MaltaProj4\//, '/');
  const file = path.resolve(ROOT, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
  if (!file.startsWith(ROOT + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
  res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
  res.end(fs.readFileSync(file));
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/`;
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  // The Lambda build's --single-process/--no-zygote mode crashes under this
  // Debian sandbox; run the same binary with the normal multi-process model.
  const drop = new Set(['--single-process', '--no-zygote', '--no-startup-window', '--in-process-gpu']);
  const args = chromium.default.args
    .filter(a => !drop.has(a.split('=')[0]) && a !== '--disable-web-security')
    .concat(['--no-sandbox', '--disable-gpu', '--headless=new']);
  const browser = await playwright.launch({
    args,
    executablePath: await chromium.default.executablePath(),
    headless: true,
  });
  const receipt = { run_at: new Date().toISOString(), viewports: [], errors: [] };
  try {
    for (const width of [320, 390, 412]) {
      const pg = await browser.newPage();
      await pg.setViewportSize({ width, height: 800 });
      pg.on('pageerror', e => receipt.errors.push(`${width} ${e.message}`));
      const vp = { width, checks: [] };

      // Executive summary
      let resp = await pg.goto(base + 'index.html');
      assert.equal(resp.status(), 200);
      vp.checks.push({ page: 'index', status: resp.status() });
      const overflow = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
      const quicknav = await pg.locator('#exec-quicknav').boundingBox();
      const tabs = await pg.locator('nav.mobile-tabs').boundingBox();
      const quickLink = await pg.locator('#exec-quicknav a[href^="picks.html"]').first().boundingBox();
      vp.checks.push({
        page: 'index', horizontal_overflow: overflow,
        quicknav_top: quicknav ? Math.round(quicknav.y) : null,
        updated_picks_link_above_fold: quickLink ? quickLink.y < 800 : false,
        mobile_tabs_present: !!tabs,
      });

      // Pick board: first priced row shows both teams' percentages and the pick
      resp = await pg.goto(base + 'picks.html');
      assert.equal(resp.status(), 200);
      const pickOverflow = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
      const firstRow = pg.locator('tr[data-match][data-status="priced"]').first();
      const rowText = await firstRow.innerText();
      const pct = (rowText.match(/\d+(?:\.\d+)?%/g) || []).length;
      const rowBox = await firstRow.boundingBox();
      vp.checks.push({
        page: 'picks', status: resp.status(), horizontal_overflow: pickOverflow,
        first_priced_row_percentages: pct, first_row_top: rowBox ? Math.round(rowBox.y) : null,
        first_row_names_pick: rowText.replace(/\s+/g, ' ').slice(0, 160),
      });

      // Unresolved page renders at zero and the phone tab bar works
      resp = await pg.goto(base + 'unresolved.html');
      assert.equal(resp.status(), 200);
      const unOverflow = await pg.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
      const unTabs = await pg.locator('nav.mobile-tabs a').count();
      vp.checks.push({ page: 'unresolved', status: resp.status(), horizontal_overflow: unOverflow, tab_links: unTabs });

      receipt.viewports.push(vp);
      await pg.close();
    }
    fs.writeFileSync(path.join(__dirname, 'mobile-probe.json'), JSON.stringify(receipt, null, 2));
    console.log(JSON.stringify(receipt, null, 2));
  } finally {
    await browser.close();
    server.close();
  }
})().catch(err => { console.error(err); process.exit(1); });
