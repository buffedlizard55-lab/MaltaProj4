// Session e86697a6: on 2026-10-24 the live site told a phone reader
// "22 open CS2 match(es) · 0 with a pick · 22 unresolved" while the committed
// snapshot held a sourced pick for all 22 rows — the publisher had stopped and
// the snapshot was outside its eight-hour window. A withheld pick is not an
// unresolved match, so:
//   1. the executive summary must show the withheld count next to the pick
//      count, and link to #withheld-picks on the same page;
//   2. the withheld section must name each held row with its source and reason,
//      and must not be filed under "unresolved";
//   3. both must fit a 320 px phone without sideways scrolling.
// Measured against the build in `public/`, never from prose.
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
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({
    args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true});
  const errors = [];
  const opened = [];
  try {
    for (const width of [320, 390, 412]) {
      const page = await browser.newPage({viewport: {width, height: 844}});
      opened.push(page);
      page.on('pageerror', error => errors.push(`${width}px: ${error.message}`));
      await page.goto(base, {waitUntil: 'load'});
      const measured = await page.evaluate(() => {
        const withheld = document.querySelector('#withheld-picks');
        const link = document.querySelector('a[href="#withheld-picks"]');
        const counts = Object.fromEntries([...document.querySelectorAll('[data-count]')]
          .map(n => [n.dataset.count, n.textContent.trim()]));
        const hosts = [...document.querySelectorAll('#withheld-picks a[href]')]
          .map(a => new URL(a.href).hostname);
        return {
          hasSection: !!withheld,
          heading: withheld ? withheld.querySelector('h3').textContent.trim() : '',
          linkHref: link ? link.getAttribute('href') : null,
          linkText: link ? link.textContent.trim() : null,
          counts,
          hosts: [...new Set(hosts)],
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
          sectionSaysNotUnresolved: withheld ? /not unresolved/i.test(withheld.textContent) : false,
        };
      });
      assert.ok(measured.hasSection, `the executive summary must carry #withheld-picks at ${width}px`);
      assert.ok(measured.linkHref === '#withheld-picks',
        `the withheld count must link to the section on the same page (${measured.linkHref})`);
      assert.ok(/withheld/i.test(measured.linkText || ''), 'the link text must say withheld');
      assert.ok(measured.sectionSaysNotUnresolved,
        'the withheld section must say plainly that these rows are not unresolved');
      for (const host of ['github.com']) {
        assert.ok(measured.hosts.includes(host), `the section must link the ${host} refresh status`);
      }
      assert.ok(measured.scrollWidth <= measured.innerWidth + 1,
        `no sideways scrolling at ${width}px (${measured.scrollWidth} > ${measured.innerWidth})`);

      const unresolvedPage = await browser.newPage({viewport: {width, height: 844}});
      unresolvedPage.on('pageerror', error => errors.push(`${width}px unresolved: ${error.message}`));
      await unresolvedPage.goto(base + 'unresolved.html', {waitUntil: 'load'});
      const unresolved = await unresolvedPage.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        innerWidth: window.innerWidth,
        states: [...document.querySelectorAll('.withheld-vs-unresolved dt')].map(n => n.textContent.trim()),
      }));
      assert.deepEqual(unresolved.states, ['Withheld', 'Unresolved'],
        'the unresolved page must name both no-pick states');
      assert.ok(unresolved.scrollWidth <= unresolved.innerWidth + 1,
        `no sideways scrolling on unresolved.html at ${width}px`);
      opened.push(unresolvedPage);

      // app.js counts a fixture as open only while its lock and start are still
      // ahead of the reader's clock, so the expectation is computed with the same
      // rule rather than from the snapshot's raw row count.
      const now = Date.now();
      const openNow = data.matches.filter(m => m.state === 'open'
        && Date.parse(m.lock) > now && Date.parse(m.start) > now);
      const sourcedNow = openNow.filter(m => m.withheld || m.probabilities !== null || m.pick);
      assert.equal(Number(measured.counts.open), openNow.length, 'the open count must equal the snapshot');
      assert.equal(Number(measured.counts.withheld), sourcedNow.length,
        'every sourced pick that is no longer current must be counted as withheld, never as unresolved');
      console.log(`Passed at ${width}px: withheld=${measured.counts.withheld}/open=${measured.counts.open}, `
        + `heading "${measured.heading}", link "${measured.linkText}", no overflow.`);
    }
    assert.deepEqual(errors, [], `no page errors: ${errors.join('; ')}`);
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-e86697a6.json',
      JSON.stringify({measured_at: new Date().toISOString(), errors}, null, 2) + '\n');
  } finally {
    for (const page of opened) await page.close().catch(() => {});
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
