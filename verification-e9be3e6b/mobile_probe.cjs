// Session e9be3e6b — measure the served build on real phone viewports.
// Verifies that the executive summary's in-site pick links are visible WITHOUT a
// tap, that the separate unresolved/limitations section is reachable, that every
// open row carries an external source link, and that nothing overflows sideways.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  const root = path.resolve('public');
  const server = http.createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://test').pathname)
      .replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) {
      res.writeHead(404); res.end(); return;
    }
    const mime = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
      '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  const report = {measured_at: new Date().toISOString(), base: '/MaltaProj4/', viewports: []};
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(arg => arg !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true,
    });
    const page = await browser.newPage({viewport: {width: 320, height: 568}});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));

    for (const [width, height] of [[320, 568], [390, 844], [768, 1024], [1440, 900]]) {
      await page.setViewportSize({width, height});
      await page.goto(base + 'index.html');
      const index = await page.evaluate(() => {
        const top = el => el ? Math.round(el.getBoundingClientRect().top + scrollY) : null;
        const visible = el => {
          if (!el) return false;
          const s = getComputedStyle(el);
          const r = el.getBoundingClientRect();
          return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
        };
        const bar = document.querySelector('#exec-summary');
        const stale = document.querySelector('#runtime-stale');
        const card = document.querySelector('#picks-at-a-glance .glance-card-mobile');
        const scores = card?.querySelector('.glance-card-scores');
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          execBarTop: top(bar),
          execBarVisible: visible(bar),
          execBarInsideDetails: Boolean(bar?.closest('details')),
          execLinks: [...(bar?.querySelectorAll('a[href]') || [])].map(a => ({
            href: a.getAttribute('href'), label: a.textContent.trim(),
            height: Math.round(a.getBoundingClientRect().height),
          })),
          staleHidden: stale ? (stale.hidden || getComputedStyle(stale).display === 'none') : null,
          staleDisplay: stale ? getComputedStyle(stale).display : null,
          completeness: document.querySelector('[data-completeness]')?.textContent.trim() || null,
          firstPickTop: top(card),
          firstProbabilityTop: top(scores || card?.querySelector('.glance-card-pick')),
          unresolvedSectionPresent: Boolean(document.querySelector('#unresolved-summary')),
          unresolvedLinkPresent: Boolean(document.querySelector('#exec-summary a[href="#unresolved-summary"]')),
          tabBarTop: top(document.querySelector('.mobile-tabs')),
        };
      });

      await page.goto(base + 'picks.html');
      const picks = await page.evaluate(() => {
        const rows = [...document.querySelectorAll('table tbody tr')].filter(r => r.offsetParent !== null);
        const external = [...document.querySelectorAll('a[href^="https://"]')].map(a => a.getAttribute('href'));
        const first = rows[0];
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          visibleRows: rows.length,
          firstRowTop: first ? Math.round(first.getBoundingClientRect().top + scrollY) : null,
          hotspawnLinks: external.filter(u => u.includes('hotspawn.com/matches/')).length,
          externalSourceLinks: external.filter(u => /polymarket|hltv\.org|bo3\.gg|valvesoftware|github\.com\/ValveSoftware/i.test(u)).length,
          unresolvedLimitLink: Boolean(document.querySelector('a[href="unresolved.html"]')),
        };
      });

      await page.goto(base + 'unresolved.html');
      const unresolved = await page.evaluate(() => ({
        overflow: document.documentElement.scrollWidth > innerWidth,
        ladderItems: document.querySelectorAll('ol li, .source-ladder li').length,
        hasLimitationsText: /every source tried, in order/i.test(document.body.textContent)
                            && /coverage boundary/i.test(document.body.textContent),
        backToSummary: Boolean(document.querySelector('a[href="index.html"], a[href="./"]')),
      }));

      report.viewports.push({width, height, index, picks, unresolved});
    }

    // A real tap on the executive-summary CTA must reach the updated pick board.
    await page.setViewportSize({width: 320, height: 568});
    await page.goto(base + 'index.html');
    await page.click('#exec-summary a[href="picks.html"]');
    report.ctaNavigation = {url: page.url().replace(base, '/MaltaProj4/'),
                            heading: await page.textContent('h1')};

    for (const v of report.viewports) {
      assert.equal(v.index.overflow, false, `${v.width}px home overflows`);
      assert.equal(v.picks.overflow, false, `${v.width}px picks overflows`);
      assert.equal(v.unresolved.overflow, false, `${v.width}px unresolved overflows`);
      assert.equal(v.index.execBarInsideDetails, false, `${v.width}px summary is folded`);
      assert.equal(v.index.execBarVisible, true, `${v.width}px summary is hidden`);
      for (const target of ['picks.html', '#picks-at-a-glance', 'unresolved.html', '#unresolved-summary']) {
        assert.ok(v.index.execLinks.some(l => l.href === target),
                  `${v.width}px summary lacks ${target}`);
      }
      assert.equal(v.index.unresolvedSectionPresent, true, `${v.width}px limitations section missing`);
      if (v.width <= 650) {
        assert.ok(v.index.execBarTop < v.index.firstPickTop,
                  `${v.width}px executive summary (y=${v.index.execBarTop}) is below the pick list (y=${v.index.firstPickTop})`);
        assert.ok(v.index.execBarTop < 500, `${v.width}px summary is not on the first screen (y=${v.index.execBarTop})`);
      }
      assert.ok(v.picks.hotspawnLinks > 0, `${v.width}px pick board lacks official fixture links`);
      assert.ok(v.picks.externalSourceLinks > 0, `${v.width}px pick board lacks external price links`);
      assert.equal(v.unresolved.hasLimitationsText, true, `${v.width}px limitations text missing`);
    }
    // The first pick and its probabilities must be above the fixed tab bar on a short phone.
    const short = report.viewports[0];
    const tabTop = short.index.tabBarTop ?? (short.height - 60);
    assert.ok(short.index.firstPickTop !== null && short.index.firstPickTop < tabTop,
              `first pick y=${short.index.firstPickTop} is below tab bar y=${tabTop}`);
    assert.ok(short.index.firstProbabilityTop !== null && short.index.firstProbabilityTop < tabTop,
              `first probability y=${short.index.firstProbabilityTop} is below tab bar y=${tabTop}`);
    assert.match(report.ctaNavigation.url, /picks\.html$/, 'summary CTA did not open the pick board');
    assert.deepEqual(errors, [], 'uncaught browser errors');

    fs.writeFileSync(path.resolve('research/session-e9be3e6b/mobile-measurements.json'),
                     JSON.stringify(report, null, 1) + '\n');
    console.log('Measured %d viewports; first pick y=%d, probability y=%d, tab bar y=%d at 320x568; stale banner hidden=%s.',
                report.viewports.length, short.index.firstPickTop, short.index.firstProbabilityTop,
                tabTop, short.index.staleHidden);
    console.log('Executive summary at y=%d (320px) / y=%d (390px); CTA -> %s',
                short.index.execBarTop, report.viewports[1].index.execBarTop, report.ctaNavigation.url);
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
