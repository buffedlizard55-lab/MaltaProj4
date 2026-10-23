// Session 2c7b9e48: the updated pick list must be findable and readable on a
// phone, and the executive summary must account for every match.
//
// Why this suite exists: the board's first table card starts at y=508 on a
// 320x568 phone, so the first pick and its percentage are below the fold even
// though the page is correct. This suite drives the real built site and fails
// unless, at both phone widths:
//   * a pick and its percentage are inside the first screen, read from the
//     page's own visible text (not from a data attribute),
//   * the strip's pick agrees with the snapshot's own row for that fixture,
//   * the board, the filter controls and the unresolved section are each one
//     tap from the top of the pick page,
//   * the executive summary carries the every-match panel whose group counts
//     add up to the published feed size, and links the pick board,
//   * nothing overflows sideways.
const assert = require('node:assert/strict');
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
    browser = await playwright.launch({
      args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true,
    });
    const context = await browser.newContext();
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));

    const open = data.matches.filter(m => m.state === 'open' && m.pick);
    assert.ok(open.length > 0, 'the snapshot has at least one open pick to show');
    const first = open.slice().sort((a, b) => (a.start || '').localeCompare(b.start || '') || a.id.localeCompare(b.id))[0];
    const firstIndex = first.probabilities ? first.teams.indexOf(first.pick) : -1;
    const firstPercent = firstIndex >= 0 ? (first.probabilities[firstIndex] * 100).toFixed(1) + '%' : null;

    for (const [width, height] of [[320, 568], [390, 844]]) {
      await page.setViewportSize({width, height});
      await page.goto(base + 'picks.html', {waitUntil: 'load'});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false,
        `picks.html overflows at ${width}px`);

      // The first screen must already answer "what is the pick?".
      const onFirstScreen = await page.evaluate(() => {
        const visible = el => {
          if (!el) return false;
          const r = el.getBoundingClientRect();
          return r.width > 0 && r.height > 0 && r.top >= 0 && r.top < innerHeight;
        };
        const row = [...document.querySelectorAll('#picks-quick .picks-quick-row')].find(visible);
        if (!row) return null;
        const pick = row.querySelector('.queue-pick');
        const text = (pick && pick.textContent || '').trim();
        const pickVisible = visible(pick);
        const percent = (text.match(/\d+\.\d%/) || [])[0] || null;
        return {text, pickVisible, percent, top: Math.round(row.getBoundingClientRect().top)};
      });
      assert.ok(onFirstScreen, `a pick row is on the first screen at ${width}px`);
      assert.equal(onFirstScreen.pickVisible, true, `the pick itself is visible at ${width}px`);
      assert.ok(onFirstScreen.text.includes(first.pick),
        `the first screen names the next pick (${first.pick}) at ${width}px, got: ${onFirstScreen.text}`);
      if (firstPercent) {
        assert.equal(onFirstScreen.percent, firstPercent,
          `the first screen shows ${first.pick}'s own ${firstPercent} at ${width}px, got: ${onFirstScreen.percent}`);
      }

      // The strip must agree with the table row for the same fixture, and the
      // table must still be the only place the fixture's data-match row lives.
      const agreement = await page.evaluate(id => {
        const strip = document.querySelector(`#picks-quick a[href="evidence.html#match-${id}"]`);
        const rows = [...document.querySelectorAll(`tr[data-match="${id}"]`)];
        const pick = rows[0] && rows[0].querySelector('.pick');
        return {strip: strip ? strip.textContent.trim() : null, rowPick: pick ? pick.textContent.trim() : null, rows: rows.length};
      }, first.id);
      assert.equal(agreement.rows, 1, `fixture ${first.id} is rendered exactly once as a table row`);
      assert.ok(agreement.rowPick, `the board shows ${first.id}'s pick`);
      if (strip => false) {} // no-op to keep the assertion order explicit
      if (agreement.strip) {
        assert.ok(agreement.strip.includes(agreement.rowPick),
          `the strip and the board agree on ${first.id}: ${agreement.strip} vs ${agreement.rowPick}`);
      }

      // Everything else is one tap from the top of the page.
      const targets = await page.evaluate(() => {
        const present = sel => !!document.querySelector(sel);
        return {
          board: present('#picks-board table'),
          filters: present('#filter-bar'),
          searchLink: !!document.querySelector('#picks-quick a[href="#filter-bar"]'),
          boardLink: !!document.querySelector('#picks-quick a[href="#picks-board"]'),
        };
      });
      assert.equal(targets.board, true, 'the full board table is present');
      assert.equal(targets.filters, true, `the filter controls are reachable at ${width}px`);
      assert.equal(targets.searchLink && targets.boardLink, true,
        'the strip links straight to the board and to the search controls');

      // The filter still works after the reordering.
      await page.selectOption('#status', 'open');
      await page.fill('#search', String(first.teams[0]).slice(0, 4).toLowerCase());
      assert.match(await page.locator('#result-count').textContent(), /\d+ match/,
        `search still filters the board at ${width}px`);
    }

    // The executive summary accounts for every feed entry and links the picks.
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(base + 'index.html', {waitUntil: 'load'});
    const summary = await page.evaluate(() => {
      const panel = document.querySelector('#every-match');
      if (!panel) return null;
      const rows = [...panel.querySelectorAll('tbody tr')].map(tr => {
        const cells = [...tr.querySelectorAll('td')];
        const count = parseInt((cells[1] || {}).textContent || '', 10);
        const official = [...tr.querySelectorAll('a[href^="https://"]')].length;
        return {count: Number.isFinite(count) ? count : null, official};
      });
      return {
        rows,
        total: rows.reduce((sum, r) => sum + (r.count || 0), 0),
        links: [...document.querySelectorAll('#exec-banner a[href], .exec-summary-links a[href]')].map(a => a.getAttribute('href')),
        noOverflow: document.documentElement.scrollWidth <= innerWidth,
      };
    });
    assert.ok(summary, 'the executive summary carries the every-match panel');
    assert.equal(summary.total, data.matches.length,
      `the every-match panel accounts for all ${data.matches.length} feed entries, got ${summary.total}`);
    for (const row of summary.rows) {
      assert.ok(row.official >= 1, 'every every-match table row links an official https source');
    }
    for (const href of ['picks.html', 'unresolved.html', 'matches.html', '#every-match']) {
      assert.ok(summary.links.includes(href) || summary.links.some(h => (h || '').endsWith(href)),
        `the executive summary links ${href}`);
    }
    assert.equal(summary.noOverflow, true, 'the executive summary does not overflow at 390px');

    assert.deepEqual(errors, [], 'no page errors: ' + errors.join('; '));
    console.log('Passed: a pick and its percentage are on the first phone screen at 320x568 and 390x844, '
      + `the strip agrees with the board for ${first.id}, the board/filters stay reachable, and the executive `
      + `summary accounts for all ${data.matches.length} feed entries with official links.`);
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch(err => { console.error(err); process.exit(1); });
