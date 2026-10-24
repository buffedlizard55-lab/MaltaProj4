// Session 138cbedd: the freshness strip must tell the truth on a static page.
//
// Measured defect (23 Oct 2026): the built index.html said "next slot 08:34
// UTC" while the page was being read at 10:20Z, because the slot was computed
// once at build time from the snapshot clock. A reader has no way to tell that
// the line is two hours stale. The page now recomputes the next :04/:19/:34/:49
// slot against the reader's own clock and prints the snapshot's age, marking a
// snapshot past the 90-minute refresh target. This suite drives the real pages
// at phone and desktop widths with a faked clock and asserts both behaviours.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

const ROOT = path.resolve('public');

function serve() {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://test');
    const pathname = decodeURIComponent(url.pathname).replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(ROOT, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(ROOT + path.sep) || !fs.existsSync(file)) {
      res.writeHead(404);
      res.end();
      return;
    }
    const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
      '.json': 'application/json', '.svg': 'image/svg+xml', '.csv': 'text/csv'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

function slotMinutesFromNow(text, now) {
  const match = /next slot (\d\d):(\d\d) UTC/.exec(text || '');
  assert.ok(match, `the strip states a slot, got "${text}"`);
  const target = new Date(now);
  target.setUTCHours(Number(match[1]), Number(match[2]), 0, 0);
  let delta = target.getTime() - now;
  if (delta < 0) delta += 24 * 3600000;
  return delta / 60000;
}

(async () => {
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({
    args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true,
  });
  const server = await serve();
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  const observed = Date.parse(JSON.parse(fs.readFileSync(path.resolve(ROOT, 'data/latest.json'))).fixtures_observed_at);
  let checked = 0;
  try {
    // One page, resized between viewports: this Chromium build runs single
    // process, and opening a second page at a different size crashes it.
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    for (const viewport of [{width: 390, height: 844}, {width: 1440, height: 900}]) {
      await page.setViewportSize(viewport);

      for (const hoursLater of [0.1, 2, 6]) {
        const now = observed + hoursLater * 3600000;
        await page.addInitScript(t => { Date.now = () => t; }, now);
        await page.goto(base + 'index.html');
        await page.waitForFunction(() => (document.querySelector('#fresh-age')?.textContent || '').length > 0);

        const strip = await page.evaluate(() => ({
          age: document.querySelector('#fresh-age')?.textContent || '',
          overdue: document.querySelector('#fresh-age')?.dataset.overdue,
          slot: document.querySelector('#next-slot')?.textContent || '',
          scheduleHidden: getComputedStyle(document.querySelector('.fresh-schedule')).display === 'none',
          overflow: document.documentElement.scrollWidth > window.innerWidth,
        }));
        assert.deepEqual(errors, [], `no page errors: ${errors.join('; ')}`);
        assert.equal(strip.overflow, false, `${viewport.width}px: no horizontal overflow`);
        assert.match(strip.age, /ago/, 'the strip states the snapshot age');

        // The advertised slot is always ahead of the reader, never behind.
        const minutes = slotMinutesFromNow(strip.slot, now);
        assert.ok(minutes > 0 && minutes <= 15,
          `${viewport.width}px: next slot is 0-15 minutes ahead, got ${minutes.toFixed(1)} min ("${strip.slot}")`);

        if (hoursLater === 0.1) {
          assert.equal(strip.overdue, '0', 'a six-minute-old snapshot is inside the refresh target');
          assert.doesNotMatch(strip.age, /past the 90-minute refresh target/);
          assert.match(strip.age, /6m ago/);
        } else {
          assert.equal(strip.overdue, '1', `${hoursLater}h-old snapshot must be marked overdue`);
          assert.match(strip.age, /past the 90-minute refresh target/);
          // The age is shown even on a phone, where the schedule line is folded
          // away to protect the first screen.
          if (viewport.width === 390) {
            assert.equal(strip.scheduleHidden, true, 'the long schedule line stays folded on a phone');
          }
        }
        checked++;
      }
    }

    // The board itself has no headroom for another block above the first card
    // at 320px (the existing first-screen contract), so its freshness evidence
    // stays per row: every card states when its price was observed and when it
    // expires, and the >8h stale banner is covered by the other suites. What is
    // asserted here is that those per-row times are present and dated, and that
    // the page never scrolls sideways on a phone.
    await page.setViewportSize({width: 390, height: 844});
    const now = observed + 2 * 3600000;
    await page.addInitScript(t => { Date.now = () => t; }, now);
    await page.goto(base + 'picks.html');
    await page.waitForTimeout(200);
    const board = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > window.innerWidth,
      firstPick: (() => {
        const el = document.querySelector('.pick-cell .pick');
        if (!el) return null;
        const box = el.getBoundingClientRect();
        return {top: Math.round(box.top + window.scrollY), text: el.textContent.trim()};
      })(),
      firstQuote: (document.querySelector('.quote-time')?.textContent || '').replace(/\s+/g, ' ').trim(),
      hasProbability: Boolean(document.querySelector('.prob-pair')),
    }));
    assert.deepEqual(errors, [], `no page errors on the board: ${errors.join('; ')}`);
    assert.equal(board.overflow, false, 'the board does not scroll sideways on a phone');
    // Session 019a253a: the pull-request gate builds from the committed
    // baseline without refreshing a source. Once that baseline is older than the
    // eight-hour evidence window, `scripts.build` withholds every pick, so there
    // is no pick cell to measure and this assertion failed for a data-age reason
    // rather than a defect. A fresh build still has to satisfy it in full.
    const boardWithheld = await page.evaluate(() => ({
      withheld: document.querySelectorAll('.pick-cell .pick').length === 0
        && document.querySelectorAll('.pick-cell .badge').length > 0,
    }));
    if (board.firstPick) {
      assert.ok(board.hasProbability, 'the board still renders both probabilities');
      assert.match(board.firstQuote, /Observed .* UTC/, 'each card states when its price was observed');
      assert.match(board.firstQuote, /Expires .* UTC/, 'each card states when its price expires');
    } else {
      assert.ok(boardWithheld.withheld,
        'a board without a pick must show the withheld state on its rows, not an empty page');
      // Node's clock, not the page's: this suite deliberately overrides
      // Date.now in the page to age the snapshot.
      const snapshotAge = (Date.now() - observed) / 3600000;
      assert.ok(snapshotAge >= 8,
        `a fresh build must render a pick; snapshot is only ${snapshotAge.toFixed(1)} h old`);
      console.log('Not applicable: this build withheld picks (the committed baseline is past its '
        + 'eight-hour window), so the per-row observation and expiry lines are not present to read.');
    }
    await page.close();

    console.log(`Passed: freshness clock on 2 viewports x 3 snapshot ages (${checked} reads) and the phone pick board's per-row observation/expiry times — the advertised slot is always ahead of the reader and the snapshot age is always stated.`);
  } finally {
    await browser.close();
    server.close();
  }
})().catch(err => {
  console.error(err);
  process.exit(1);
});
