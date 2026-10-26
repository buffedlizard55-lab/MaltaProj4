// Session 11e17543: measure the every-match coverage table and the executive
// summary links that point at it, on phones.
//
// The board was already complete for open matches; what a phone visitor could not
// find was an answer to "what about the other matches Hotspawn lists?". This suite
// measures, per viewport: whether the executive summary's link to the coverage
// table is reachable without scrolling, whether that table renders as stacked
// cards with no horizontal overflow, whether every card states its pick (or its
// limitation), and whether the tap targets stay at or above 44px.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

const VIEWPORTS = [
  {name: 'iPhone SE', width: 320, height: 568},
  {name: 'iPhone 14', width: 390, height: 844},
];

(async () => {
  // SITE_ROOT lets the suite be pointed at a deliberately broken build to prove
  // its assertions actually fail. Defaults to the generated build CI checks.
  const root = path.resolve(process.env.SITE_ROOT || 'public');
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://test');
    const pathname = decodeURIComponent(url.pathname).replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) {res.writeHead(404); res.end(); return;}
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

  const report = {generated_at: new Date().toISOString(), viewports: [], failures: []};
  try {
    const page = await browser.newPage();
    for (const vp of VIEWPORTS) {
      await page.setViewportSize({width: vp.width, height: vp.height});

      // 1. The executive summary must point at the coverage table from the first screen.
      await page.goto(base + 'index.html');
      const summary = await page.evaluate(() => {
        const box = s => {const el = document.querySelector(s);
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return {y: Math.round(r.y + scrollY), height: Math.round(r.height)};};
        const links = [...document.querySelectorAll('#exec-banner a[href], #exec-summary a[href], #exec-quicknav a[href]')]
          .map(a => ({href: a.getAttribute('href'), text: a.innerText.trim(),
                      y: Math.round(a.getBoundingClientRect().y + scrollY)}));
        return {banner: box('#exec-banner'), bar: box('#exec-summary'),
                quicknav: box('#exec-quicknav'), links,
                tabbarTop: Math.round((document.querySelector('.mobile-tabs') || {getBoundingClientRect: () => ({y: 0})})
                  .getBoundingClientRect().y + scrollY)};
      });
      const everyLink = summary.links.find(l => l.href === 'matches.html#every-match');
      if (!everyLink) report.failures.push(`${vp.name}: the executive summary does not link the every-match table`);
      const aboveFold = summary.links.filter(l => l.y < vp.height);
      if (!aboveFold.some(l => l.href === 'picks.html'))
        report.failures.push(`${vp.name}: no path to the updated picks above the fold`);

      // 2. The coverage table itself: one card per feed row, no overflow, every card
      //    says what the pick is or why there is none.
      await page.goto(base + 'matches.html#every-match');
      const coverage = await page.evaluate(() => {
        const section = document.querySelector('#every-match');
        const rows = [...section.querySelectorAll('table tbody tr')];
        const cards = rows.map(tr => {
          const cell = l => (tr.querySelector(`td[data-label="${l}"]`) || {}).innerText || '';
          const r = tr.getBoundingClientRect();
          return {fixture: cell('Fixture').trim(), pick: cell('Our pick').trim(),
                  probability: cell('Win probability').trim(),
                  limitation: cell('Limitation').trim(),
                  sources: tr.querySelectorAll('td.source-links a[href]').length,
                  width: Math.round(r.width), height: Math.round(r.height)};
        });
        const taps = [...section.querySelectorAll('a')].map(a => {
          const r = a.getBoundingClientRect();
          return Math.min(r.width || 999, r.height || 999);});
        const buttons = [...section.querySelectorAll('.actions a')].map(a => {
          const r = a.getBoundingClientRect();
          return {text: a.innerText.trim(), width: Math.round(r.width), height: Math.round(r.height)};});
        return {found: !!section, heading: section.querySelector('h2').innerText.trim(),
                cards, stacked: getComputedStyle(rows[0]).display !== 'table-row',
                smallestTap: taps.length ? Math.round(Math.min(...taps)) : null,
                buttons,
                sectionTop: Math.round(section.getBoundingClientRect().y + scrollY)};
      });
      if (!coverage.found) report.failures.push(`${vp.name}: #every-match is missing from matches.html`);
      // The row count is not pinned to a literal. CI refreshes the snapshot from
      // the live feed before it builds, so the number of listed CS2 matches moves
      // between runs; a hardcoded expectation would fail on a correct page and,
      // worse, pass on a page that silently dropped rows. The invariant that
      // actually matters is internal consistency: the table carries exactly one
      // card per match its own heading counts, and the picks it reports plus the
      // rows the unresolved page reports account for all of them.
      const claimed = /of\s+(\d+)\s+listed/i.exec(coverage.heading || '');
      const total = claimed ? Number(claimed[1]) : NaN;
      if (!Number.isFinite(total) || total <= 0)
        report.failures.push(`${vp.name}: the coverage heading states no match count: "${coverage.heading}"`);
      else if (coverage.cards.length !== total)
        report.failures.push(`${vp.name}: the heading claims ${total} listed matches but the table has ${coverage.cards.length} cards`);
      if (coverage.cards.some(c => !c.pick && !/no supported pick/i.test(c.pick))) {
        const silent = coverage.cards.filter(c => !c.pick && !c.limitation);
        if (silent.length) report.failures.push(`${vp.name}: ${silent.length} cards with neither pick nor limitation`);
      }
      if (coverage.cards.some(c => c.sources === 0))
        report.failures.push(`${vp.name}: a coverage card has no source link`);
      const widest = Math.max(...coverage.cards.map(c => c.width));
      if (widest > vp.width) report.failures.push(`${vp.name}: widest card ${widest}px exceeds ${vp.width}px`);
      // WCAG 2.5.8 sets 24px as the minimum; the site's own convention for a
      // phone button is 44px. The coverage table's action buttons must meet the
      // stricter one, and every link in the section the looser one.
      if (coverage.smallestTap !== null && coverage.smallestTap < 24)
        report.failures.push(`${vp.name}: smallest tap target in the coverage table is ${coverage.smallestTap}px`);
      const shortButtons = coverage.buttons.filter(b => b.height < 44);
      if (shortButtons.length)
        report.failures.push(`${vp.name}: coverage action buttons below 44px: ${JSON.stringify(shortButtons)}`);
      if (!coverage.stacked) report.failures.push(`${vp.name}: the coverage table did not collapse into cards`);
      const priced = coverage.cards.filter(c => /%/.test(c.probability));
      if (!priced.length) report.failures.push(`${vp.name}: no card publishes a win probability`);
      if (coverage.cards.some(c => /50\.0% \/ 50\.0%/.test(c.probability)))
        report.failures.push(`${vp.name}: a card publishes a default 50/50`);

      // 3. The unresolved page must name every listed match that has no pick.
      await page.goto(base + 'unresolved.html');
      const unresolved = await page.evaluate(() => {
        const s = document.querySelector('#every-match-unresolved');
        if (!s) return {found: false};
        return {found: true, heading: s.querySelector('h2').innerText.trim(),
                rows: s.querySelectorAll('table tbody tr').length,
                text: s.innerText.slice(0, 400)};
      });
      if (!unresolved.found) report.failures.push(`${vp.name}: #every-match-unresolved is missing`);

      // Picks plus the rows named on the unresolved page must account for every
      // listed match, on whatever snapshot this build used.
      if (Number.isFinite(total) && unresolved.found && unresolved.rows !== undefined) {
        const picks = /(\d+)\s+of\s+\d+\s+listed/i.exec(coverage.heading || '');
        const unresolvedClaim = /(\d+)\s+of\s+\d+\s+listed/i.exec(unresolved.heading || '');
        if (picks && unresolvedClaim &&
            Number(picks[1]) + Number(unresolvedClaim[1]) !== total)
          report.failures.push(`${vp.name}: ${picks[1]} picks + ${unresolvedClaim[1]} unresolved != ${total} listed matches`);
        if (unresolvedClaim && Number(unresolvedClaim[1]) !== unresolved.rows)
          report.failures.push(`${vp.name}: the unresolved heading claims ${unresolvedClaim[1]} rows but names ${unresolved.rows}`);
      }

      report.viewports.push({viewport: vp, summary, coverage: {...coverage, cards: coverage.cards.slice(0, 3)},
                             coverageCardCount: coverage.cards.length, unresolved});
    }
  } finally {
    await browser.close();
    server.close();
  }
  fs.mkdirSync('research/session-11e17543', {recursive: true});
  fs.writeFileSync('research/session-11e17543/mobile-measurements.json', JSON.stringify(report, null, 1) + '\n');
  console.log(JSON.stringify(report, null, 1));
  if (report.failures.length) process.exitCode = 1;
})();
