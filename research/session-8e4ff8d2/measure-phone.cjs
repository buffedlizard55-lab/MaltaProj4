// Session 8e4ff8d2 — phone measurement of the built board it publishes.
//
// Not part of `npm run test:browser` (that suite is the gate; this is the
// receipt). Measures the exact question the brief asks — can the pick and both
// win percentages be read on a phone without scrolling past the fixed tab bar —
// on the build in public/, and writes research/session-8e4ff8d2/mobile-measurements.json.
//
// Run after `python -m scripts.build --data data/latest.json`:
//   node research/session-8e4ff8d2/measure-phone.cjs
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
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
                  '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;

  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({
    args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true});

  const report = {
    measured_at: new Date().toISOString(),
    snapshot_generated_at: data.generated_at,
    snapshot_fixtures_observed_at: data.fixtures_observed_at,
    open_rows: data.matches.filter(m => m.state === 'open').length,
    board: 'public/ built from data/latest.json',
    viewports: [], failures: [],
  };
  const page = await browser.newPage();
  for (const [width, height] of [[320, 568], [390, 844], [412, 915]]) {
    await page.setViewportSize({width, height});
    await page.goto(base + 'index.html');
    const home = await page.evaluate(() => {
      const top = selector =>
        document.querySelector(selector)?.getBoundingClientRect().top ?? null;
      const topAt = element => element ? Math.round(element.getBoundingClientRect().top) : null;
      return {
        horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
        picks_link_reachable: !!document.querySelector('a[href="picks.html"]'),
        unresolved_link: !!document.querySelector('a[href="unresolved.html"]'),
        quicknav_top: topAt(document.querySelector('#exec-quicknav')),
        first_glance_card_top: top('#picks-at-a-glance .glance-card, #picks-at-a-glance a'),
      };
    });
    await page.goto(base + 'picks.html');
    const board = await page.evaluate(() => {
      const row = document.querySelector('tr[data-match]');
      const rect = element => {
        const box = element.getBoundingClientRect();
        return {top: Math.round(box.top + scrollY), bottom: Math.round(box.bottom + scrollY)};
      };
      const tab = document.querySelector('.mobile-tabs');
      return {
        horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
        rows: document.querySelectorAll('tr[data-match]').length,
        teams: row?.querySelector('.teams')?.innerText.replace(/\s+/g, ' ').trim() || null,
        pick: row?.querySelector('.pick')?.innerText.trim() || null,
        pick_box: row?.querySelector('.pick') ? rect(row.querySelector('.pick')) : null,
        probability_box: row?.querySelector('.prob-pair') ? rect(row.querySelector('.prob-pair')) : null,
        probabilities: [...(row?.querySelectorAll('.prob-pair span') || [])].map(n => n.innerText.trim()),
        tab_bar_top: tab ? Math.round(tab.getBoundingClientRect().top + scrollY) : null,
      };
    });
    const fold = board.tab_bar_top ?? height;
    const clear = board.pick_box !== null && board.pick_box.bottom <= fold
      && board.probability_box !== null && board.probability_box.bottom <= fold;
    if (!clear) report.failures.push(`first pick or its percentages fall below the tab bar at ${width}x${height}`);
    if (board.horizontalOverflow || home.horizontalOverflow) report.failures.push(`horizontal overflow at ${width}x${height}`);
    report.viewports.push({viewport: `${width}x${height}`, home, board,
      first_pick_and_both_percentages_above_tab_bar: clear});
  }
  fs.writeFileSync('research/session-8e4ff8d2/mobile-measurements.json',
                   JSON.stringify(report, null, 1) + '\n');
  console.log(JSON.stringify({failures: report.failures,
    viewports: report.viewports.map(v => [v.viewport, v.board.pick_box, v.board.probability_box, v.board.tab_bar_top])}, null, 1));
  await browser.close();
  server.close();
})();
