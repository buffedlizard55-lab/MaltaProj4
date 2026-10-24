// Session 3c79a355: the live page must be readable, and the CSS must parse.
//
// Two defects are pinned here, both measured on the published board on
// 2026-10-24 before they were repaired.
//
// 1. `assets/style.css` (and its byte-identical copy `site/assets/style.css`)
//    carried an unclosed `@media(max-width:650px) and (max-height:700px){`
//    block. Browsers recover from a missing brace by treating the *rest of the
//    file* as the body of the last at-rule, so 125 lines of phone CSS -- every
//    `body[data-page="index"]` rule that puts the pick cards before the guide,
//    the strip's one-line layout, the card padding -- were silently dead.
//    Measured consequence: the strip's "NEXT PICK FOKUS 78.5%" ran together as
//    inline text ("Next pickFOKUS78.5%") and the first pick card sat at
//    y=791 on a 390x844 phone, i.e. under the fixed tab bar.
// 2. Nothing in the suite asserted where the first pick card is on a phone, so
//    a stylesheet that lost its phone rules still passed every browser test.
//    The assertions below put the card on the first screen, which is the
//    product requirement ("easily readable on a phone").
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

function assertBalanced(css, label) {
  let depth = 0;
  let line = 1;
  let deepest = 0;
  for (const ch of css) {
    if (ch === '\n') line += 1;
    else if (ch === '{') { depth += 1; deepest = Math.max(deepest, depth); }
    else if (ch === '}') {
      depth -= 1;
      assert.ok(depth >= 0, `${label}: unmatched '}' at line ${line}`);
    }
  }
  assert.equal(depth, 0, `${label}: ${depth} unclosed '{' at end of file (an unclosed @media silently disables every rule after it)`);
  // A media query nested three deep is a structural error too: this stylesheet
  // uses at most one level of at-rule nesting.
  assert.ok(deepest <= 2, `${label}: rules nested ${deepest} deep`);
}

(async () => {
  const repo = path.resolve(__dirname, '..');

  // --- static: the two published stylesheet copies parse and are identical ---
  const css = fs.readFileSync(path.join(repo, 'assets/style.css'), 'utf8');
  const siteCss = fs.readFileSync(path.join(repo, 'site/assets/style.css'), 'utf8');
  assertBalanced(css, 'assets/style.css');
  assertBalanced(siteCss, 'site/assets/style.css');
  assert.equal(css, siteCss, 'the two committed stylesheet copies must stay byte-identical');

  // Every selector that must be reachable from a phone is present exactly once
  // at top level, so a future edit cannot leave the pick cards below the guide.
  assert.match(css, /body\[data-page="index"\] main>\*\{order:7\}/,
    'the index page order rules are missing');
  assert.match(css, /body\[data-page="index"\] main>#picks-at-a-glance\{order:4\}/,
    'the pick list must be ordered above the folded guide');

  // --- live: the pick card is on the phone's first screen ---
  const root = path.resolve('public');
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
  const report = [];
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

    for (const [width, height] of [[320, 568], [390, 844]]) {
      await page.setViewportSize({width, height});
      const response = await page.goto(base + 'index.html');
      assert.equal(response.status(), 200);
      const measure = await page.evaluate(() => {
        const card = document.querySelector('#picks-at-a-glance .glance-card-mobile');
        const next = document.querySelector('.fresh-next');
        const link = document.querySelector('.fresh-next-link');
        const tabs = document.querySelector('.mobile-tabs');
        const top = el => (el ? Math.round(el.getBoundingClientRect().top + scrollY) : null);
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          card: top(card),
          nextDisplay: next ? getComputedStyle(next).display : null,
          linkDisplay: link ? getComputedStyle(link).display : null,
          label: next ? getComputedStyle(next.querySelector('.fresh-next-label')).fontSize : null,
          pick: next ? next.querySelector('.fresh-next-pick').textContent.trim() : null,
          prob: next ? next.querySelector('.fresh-next-prob').textContent.trim() : null,
          tabs: top(tabs),
        };
      });
      assert.equal(measure.overflow, false, `${width}px horizontal overflow`);
      assert.ok(measure.card !== null, `${width}px: no pick card rendered`);
      assert.ok(measure.card < height,
        `${width}px: the first pick card is below the first screen (y=${measure.card} >= ${height}); ` +
        'on 2026-10-24 this happened because an unclosed @media block disabled the phone rules');
      // The strip's next pick is a laid-out card, not three inline fragments:
      // the label/pick/percentage were rendered as "Next pickFOKUS78.5%".
      assert.equal(measure.nextDisplay, 'flex', `${width}px: the next-pick block is not laid out`);
      assert.ok(['flex', 'inline-flex'].includes(measure.linkDisplay),
        `${width}px: the next-pick link is not laid out as a flex row (${measure.linkDisplay})`);
      assert.ok(measure.pick && measure.prob, `${width}px: the strip does not name a pick with a percentage`);
      report.push({width, height, ...measure});
    }

    // Both tap targets to the pick board stay on the first screen.
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(base + 'index.html');
    for (const selector of ['#freshness-strip a[href="picks.html"]', '.mobile-tabs a[href="picks.html"]']) {
      const box = await page.locator(selector).first().boundingBox();
      assert.ok(box && box.y < 844, `${selector} must be on the first phone screen`);
      assert.ok(box && box.height >= 40, `${selector} must be a phone-sized tap target (h=${box && box.height})`);
    }
    assert.deepEqual(errors, []);

    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-3c79a355.json', JSON.stringify(report, null, 2) + '\n');
    console.log('Passed: both stylesheet copies parse (balanced braces, one nesting level), the first pick card is on the first screen at 320x568 and 390x844, the strip is laid out as a card, and both picks taps are reachable.');
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch(err => { console.error(err); process.exit(1); });
