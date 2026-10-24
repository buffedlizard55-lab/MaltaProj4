// Session caca91b8: browser verification across phone (320x568, 375x812) and
// desktop (1280x800) viewports for the executive summary, subpage links,
// obvious pick + win probability + official https:// source links on every
// open row (or fail-closed withholding when expired), unresolved limitations
// section, and Flagged for Review disclosures.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'data/latest.json'), 'utf8'));
  const reviewNotes = JSON.parse(fs.readFileSync(path.resolve('data/review-notes.json'), 'utf8'));
  const sessionNotes = reviewNotes.filter(n => String(n.id || '').startsWith('session-caca91b8-'));

  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://test');
    const pathname = decodeURIComponent(url.pathname).replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) {
      res.writeHead(404);
      res.end();
      return;
    }
    const mime = {
      '.html': 'text/html; charset=utf-8',
      '.js': 'text/javascript; charset=utf-8',
      '.css': 'text/css; charset=utf-8',
      '.json': 'application/json; charset=utf-8',
      '.svg': 'image/svg+xml',
    };
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;

  const openRows = data.matches.filter(m => m.state === 'open');
  const pricedOpen = openRows.filter(m => m.pick && Array.isArray(m.probabilities));

  let browser;
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(),
      headless: true,
    });
    const page = await (await browser.newContext()).newPage();
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));

    const pagesToCheck = [
      'index.html',
      'picks.html',
      'unresolved.html',
      'matches.html',
      'analysis.html',
      'sources.html',
      'evidence.html',
      'review.html',
    ];

    for (const [width, height] of [[320, 568], [375, 812], [1280, 800]]) {
      await page.setViewportSize({width, height});
      for (const route of pagesToCheck) {
        const resp = await page.goto(base + route, {waitUntil: 'domcontentloaded'});
        assert.equal(resp.status(), 200, `${route} returned HTTP ${resp.status()}`);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
        assert.equal(overflow, false, `${route} overflows horizontally at ${width}x${height}`);
      }
      await page.goto(base + 'methodology.html');
      await page.waitForURL(/sources\.html/);
      assert.match(page.url(), /sources\.html(#method)?$/, 'methodology.html must redirect to sources.html');

      await page.goto(base + 'index.html');
      const home = await page.evaluate(() => {
        const visibleLinks = [...document.querySelectorAll('a[href]')]
          .filter(a => !a.closest('details:not([open])'))
          .map(a => a.getAttribute('href'));
        const unresolvedEl = document.querySelector('#unresolved-picks, #unresolved-summary');
        const cards = [...document.querySelectorAll('#picks-at-a-glance .glance-card-mobile')];
        return {
          visibleLinks,
          hasUnresolvedSection: !!unresolvedEl && !unresolvedEl.closest('details:not([open])'),
          cardCount: cards.length,
          staleHidden: document.querySelector('#runtime-stale')?.hidden ?? true,
        };
      });
      for (const required of ['picks.html', 'unresolved.html', 'matches.html', 'analysis.html', 'review.html', 'sources.html']) {
        assert.ok(
          home.visibleLinks.some(h => h.split('#')[0] === required),
          `index.html (${width}px) missing unfolded executive link to ${required}`
        );
      }
      assert.equal(home.hasUnresolvedSection, true, `index.html (${width}px) missing unfolded unresolved summary`);
      assert.equal(home.cardCount, openRows.length, `index.html (${width}px) card count != open rows`);

      await page.goto(base + 'picks.html');
      const picksCheck = await page.evaluate(() => {
        const rows = [...document.querySelectorAll('main table tbody tr[data-match-id], main table tbody tr')];
        return rows.map(tr => ({
          text: tr.textContent.replace(/\s+/g, ' ').trim(),
          httpsLinks: [...tr.querySelectorAll('a[href^="https://"]')].map(a => a.getAttribute('href')),
        }));
      });
      if (pricedOpen.length > 0) {
        assert.equal(picksCheck.length, openRows.length, `picks.html (${width}px) row count != open rows`);
        for (const r of picksCheck) {
          assert.ok(r.httpsLinks.length >= 1, `picks.html row lacks https:// source link: ${r.text}`);
          assert.match(r.text, /\d+\.\d%/, `picks.html priced row lacks win percentage: ${r.text}`);
        }
      } else {
        assert.equal(home.staleHidden, false, 'expired baseline must display #runtime-stale');
      }
    }

    await page.setViewportSize({width: 1280, height: 800});
    await page.goto(base + 'review.html');
    const reviewInfo = await page.evaluate(ids => {
      const html = document.body.innerHTML;
      const missing = ids.filter(id => !html.includes(id));
      const httpsCount = document.querySelectorAll('main a[href^="https://"]').length;
      return {missing, httpsCount};
    }, sessionNotes.map(n => n.id));
    assert.deepEqual(reviewInfo.missing, [], `review.html missing session notes: ${reviewInfo.missing.join(', ')}`);
    assert.ok(reviewInfo.httpsCount > 0, 'review.html carries no https:// source links');
    assert.deepEqual(pageErrors, [], `Unhandled page errors: ${pageErrors.join('; ')}`);
    console.log(JSON.stringify({
      suite: 'browser_caca91b8',
      open_rows: openRows.length,
      priced_open_rows: pricedOpen.length,
      session_review_notes: sessionNotes.length,
      pages_checked: pagesToCheck.length,
      status: 'ok',
    }));
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})();
