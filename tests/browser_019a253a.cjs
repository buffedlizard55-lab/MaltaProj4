// Session 019a253a: the phone is the way this board is actually read, and two
// measured defects made that harder than the tests claimed.
//
// 1. `site/assets/style.css` had one unclosed `@media(max-width:650px) and
//    (max-height:700px)` block. CSS error recovery closes an unclosed block at
//    end of file, so every rule after it - the whole phone stylesheet from the
//    2026-10-23 sessions onward - only applied on screens 700px tall or less.
//    Measured with this Chromium build on the 2026-10-24T05:55Z snapshot, the
//    first pick card on the executive summary sat at y=723 on a 390x844 phone
//    and y=705 at 412x915; closing the block puts it at y=324 on both, with no
//    horizontal overflow. The brace is closed now, and `scripts.validate` plus
//    the stylesheet-integrity test in tests/test_session_019a253a.py fail if it
//    ever reopens.
// 2. The executive summary must answer "where are the updated picks?" without a
//    tap, and the fallback ladder that explains a pick for a match no book prices
//    has to be readable on a phone rather than a desktop-only table.
//
// Everything below is measured, not asserted from prose.
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
    const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
      '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  const measured = [];
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true,
    });
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));

    for (const [width, height] of [[320, 568], [390, 844], [412, 915]]) {
      await page.setViewportSize({width, height});
      await page.goto(base + 'index.html');
      const read = await page.evaluate(() => {
        const top = selector => {
          const element = document.querySelector(selector);
          if (!element) return null;
          return Math.round(element.getBoundingClientRect().top + scrollY);
        };
        const strip = document.querySelector('#freshness-strip');
        const card = document.querySelector('#picks-at-a-glance a.glance-card-mobile');
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          card: top('#picks-at-a-glance a.glance-card-mobile'),
          headline: top('main > .page-head'),
          stripDisplay: strip ? getComputedStyle(strip).display : null,
          cardIsLink: card ? card.getAttribute('href') : null,
          picksLinks: [...document.querySelectorAll('a[href="picks.html"]')].length,
        };
      });
      assert.equal(read.overflow, false, `index overflows at ${width}x${height}`);
      assert.ok(read.card !== null, `the summary renders a pick card at ${width}x${height}`);
      // The contract this file exists for: the first pick is readable without
      // scrolling on every common phone size, at both short and tall heights.
      assert.ok(read.card <= 520,
        `the first pick card must be near the top at ${width}x${height} (measured y=${read.card})`);
      assert.ok(read.picksLinks > 0, `the picks list is linked from the summary at ${width}x${height}`);
      measured.push({viewport: `${width}x${height}`, firstCardTop: read.card});

      await page.goto(base + 'picks.html');
      const board = await page.evaluate(() => {
        const row = document.querySelector('tr[data-match]');
        const pick = row && row.querySelector('.pick');
        const probability = row && row.querySelector('.prob-pair, .research-prob');
        const rect = element => {
          const box = element.getBoundingClientRect();
          return {top: Math.round(box.top + scrollY), bottom: Math.round(box.bottom + scrollY)};
        };
        const tab = document.querySelector('.mobile-tabs');
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          pick: pick ? rect(pick) : null,
          probability: probability ? rect(probability) : null,
          tab: tab ? rect(tab) : null,
        };
      });
      assert.equal(board.overflow, false, `picks board overflows at ${width}x${height}`);
      if (board.pick) {
        const fold = board.tab ? board.tab.top : height;
        assert.ok(board.pick.bottom <= fold,
          `the first pick must clear the phone tab bar at ${width}x${height}`);
        assert.ok(board.probability && board.probability.bottom <= fold,
          `the first probabilities must clear the tab bar at ${width}x${height}`);
      }
    }

    // The fallback ladder is inside the summary and readable at 390px: every
    // rung, the per-rung count, and an in-site link to the full list.
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(base + 'index.html');
    const ladder = await page.evaluate(() => {
      const section = document.querySelector('#unresolved-limits');
      if (!section) return null;
      const box = section.getBoundingClientRect();
      return {
        text: section.innerText.replace(/\s+/g, ' '),
        counts: [...section.querySelectorAll('[data-ladder-count]')].map(n => `${n.dataset.ladderCount}=${n.textContent.trim()}`),
        width: Math.round(box.width),
        links: [...section.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
      };
    });
    assert.ok(ladder, 'the executive summary carries the unresolved/limitations section');
    for (const rung of ['Polymarket exchange line', 'HLTV fixture identity', 'Pinnacle esports moneyline',
      'Wide exchange quote', 'Researched bookmaker listing', 'Our own VRS model line',
      'HLTV’s dated Valve ranking', 'Research pick, no percentage']) {
      assert.ok(ladder.text.includes(rung), `the ladder must name the "${rung}" rung`);
    }
    assert.ok(ladder.counts.length >= 9, `every rung publishes a count: ${ladder.counts.join(' ')}`);
    assert.ok(ladder.links.includes('unresolved.html'), 'the section links to the full unresolved page');
    assert.ok(ladder.links.includes('https://www.hltv.org/matches'), 'the section links HLTV');
    assert.ok(ladder.width <= 390, 'the section fits a 390px phone without sideways scrolling');

    const openRows = data.matches.filter(row => row.state === 'open').length;
    // Unresolved is a real partition of the board, not a missing fixture.
    // Excluding `none` makes a legitimate source outage fail publication.
    const counted = ladder.counts
      .reduce((total, item) => total + Number(item.split('=')[1]), 0);
    assert.equal(counted, openRows, 'the ladder counts must add up to the open matches');

    assert.deepEqual(errors, [], `no page errors: ${errors.join('; ')}`);
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-019a253a.json',
      JSON.stringify({measured, ladder: ladder.counts, openRows}, null, 2) + '\n');
    console.log(`Passed: phone-first summary on 3 viewports (${measured.map(m => m.viewport + ' y=' + m.firstCardTop).join(', ')}), `
      + `pick board clear of the tab bar, and the ${ladder.counts.length}-rung fallback ladder with counts totalling ${counted}.`);
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
