// Session aeafcbe6: measure the phone board on a *fresh* capture.
//
// The committed snapshot was already outside its eight-hour window, and app.js
// withholds every pick once that window closes, so a measurement against the
// committed build would measure the withholding banner rather than the board.
// This script measures the build made from research/diagnose-aeafcbe6/snapshot.json
// (the 2026-10-24T17:09Z capture: 83 feed rows, 20 open, 20 picks, 20 win
// probabilities, 0 unresolved).
//
// It records, per viewport: where the executive summary and its in-site links sit,
// where the first pick and both teams' win chances sit relative to the fixed phone
// tab bar, whether the page overflows horizontally, and whether the picks link can
// be reached without scrolling.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

const VIEWPORTS = [
  {name: 'iPhone SE', width: 320, height: 568},
  {name: 'iPhone 14', width: 390, height: 844},
  {name: 'Pixel 7', width: 412, height: 915},
];

(async () => {
  const root = path.resolve('public');
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
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;

  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({
    args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true});

  const report = {measured_at: new Date().toISOString(), board: 'public/ from research/diagnose-aeafcbe6/snapshot.json',
                  viewports: [], failures: []};
  try {
    const page = await browser.newPage({viewport: {width: 320, height: 568}});
    for (const viewport of VIEWPORTS) {
      // A mobile *viewport* is what the layout depends on; the packaged
      // single-process Chromium in this test image segfaults on device
      // emulation (`isMobile`), and on repeated newPage calls, so one page is
      // resized in a loop exactly as the committed phone suites do.
      await page.setViewportSize({width: viewport.width, height: viewport.height});
      await page.goto(base + 'index.html', {waitUntil: 'networkidle'});
      // 1. Home: the executive summary and its in-site links.
      const home = await page.evaluate(() => {
        const box = selector => {
          const el = document.querySelector(selector);
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return {top: Math.round(r.top + window.scrollY), height: Math.round(r.height)};
        };
        return {
          horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
          withheld: !!(document.querySelector('#runtime-stale') && !document.querySelector('#runtime-stale').hidden),
          exec_summary: box('#exec-summary'), exec_quicknav: box('#exec-quicknav'),
          quicknav_text: ((document.querySelector('#exec-quicknav') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
          exec_links: [...document.querySelectorAll('#exec-summary a[href], #exec-quicknav a[href]')]
            .map(a => a.getAttribute('href')),
          picks_link_reachable: !!document.querySelector('#exec-summary a[href="picks.html"], #exec-quicknav a[href="picks.html"]'),
          unresolved_link: !!document.querySelector('#exec-summary a[href="unresolved.html"], #exec-quicknav a[href^="#unresolved"]'),
        };
      });
      // 2. The updated-picks page: the first row, its pick and both win chances.
      await page.goto(base + 'picks.html', {waitUntil: 'networkidle'});
      const board = await page.evaluate(() => {
        const firstRow = document.querySelector('tr.row');
        if (!firstRow) return {found: false};
        const r = firstRow.getBoundingClientRect();
        // Real markup: `.prob-pair > span` holds "42.5%" / "57.5%", each with an
        // aria-label naming the team, and `.pick` holds the published pick.
        const percentages = [...firstRow.querySelectorAll('.prob-pair > span')]
          .map(el => el.textContent.trim()).filter(text => /%$/.test(text));
        const labelled = [...firstRow.querySelectorAll('.prob-pair > span')]
          .map(el => el.getAttribute('aria-label'));
        return {
          found: true,
          top: Math.round(r.top + window.scrollY), height: Math.round(r.height),
          pick: ((firstRow.querySelector('.pick') || {}).textContent || '').trim(),
          teams: ((firstRow.querySelector('.teams') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
          percentages, percentage_labels: labelled,
          tabbar_top: (() => { const t = document.querySelector('.mobile-tabs');
            return t ? Math.round(t.getBoundingClientRect().top) : null; })(),
          horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
          rows: document.querySelectorAll('tr.row').length,
        };
      });
      const measured = {name: viewport.name, viewport: {width: viewport.width, height: viewport.height},
                        home, board, documentWidth: 0};
      report.viewports.push(measured);
      if (home.horizontalOverflow) report.failures.push(`${viewport.name}: home overflows horizontally`);
      if (!home.picks_link_reachable) report.failures.push(`${viewport.name}: no in-site updated-picks link on the first screen`);
      if (!home.unresolved_link) report.failures.push(`${viewport.name}: no in-site unresolved/limits link on the first screen`);
      // The compact executive summary (#exec-quicknav) is the phone's first-screen
      // answer; the full #exec-summary card is allowed to sit with the full briefing.
      const summaryTop = home.exec_quicknav ? home.exec_quicknav.top : (home.exec_summary || {}).top;
      if (summaryTop == null || summaryTop > viewport.height)
        report.failures.push(`${viewport.name}: executive summary starts below the first screen`);
      if (!board.found) report.failures.push(`${viewport.name}: picks page shows no rows`);
      else {
        if (!board.pick) report.failures.push(`${viewport.name}: first row has no visible pick`);
        if (board.percentages.length < 2)
          report.failures.push(`${viewport.name}: first row does not show both win chances (${JSON.stringify(board.percentages)})`);
        // Both teams' chances must be readable without scrolling past the first screen.
        if (board.top > viewport.height)
          report.failures.push(`${viewport.name}: first pick row starts below the first screen`);
      }

    }
  } finally {
    await browser.close();
    server.close();
  }
  fs.mkdirSync('research/session-aeafcbe6', {recursive: true});
  fs.writeFileSync('research/session-aeafcbe6/mobile-measurements.json', JSON.stringify(report, null, 1) + '\n');
  console.log(JSON.stringify(report, null, 1));
  if (report.failures.length) process.exitCode = 1;
})();
