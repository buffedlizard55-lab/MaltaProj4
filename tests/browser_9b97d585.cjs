// Session 9b97d585: regressions measured on the real generated site.
// 1. Runtime prose must not say "0 of them carry no win probability" when
//    every open row is priced, and singular counts must use singular grammar.
// 2. At 320x568 the first pick and both probabilities must be visible above
//    the fixed phone tab bar. Optional filters remain usable after the board.
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
    const pathname = new URL(req.url, 'http://test').pathname.replace(/^\/MaltaProj4\//, '/');
    const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
    const mime = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml'};
    res.setHeader('content-type', mime[path.extname(file)] || 'text/plain');
    res.end(fs.readFileSync(file));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  const report = {copy: [], phone: []};
  const coverageRow = (id, kind) => ({
    id, state: 'open', start: '2099-01-01T00:00:00Z', lock: '2098-12-31T23:54:00Z',
    expires_at: '2098-12-31T23:54:00Z', priced: kind === 'priced', model: false,
    picked: kind !== 'unresolved', research: kind === 'research',
  });
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true});
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base + 'index.html');
    const scenarios = [
      {name: 'all priced', rows: [coverageRow('a', 'priced'), coverageRow('b', 'priced')],
        expected: 'Every one of the 2 open matches has a pick, and every pick carries a win probability.'},
      {name: 'one research', rows: [coverageRow('a', 'priced'), coverageRow('b', 'research')],
        includes: 'One of them carries no win probability'},
      {name: 'single priced', rows: [coverageRow('a', 'priced')],
        expected: 'The only open match has a pick, and every pick carries a win probability.'},
      {name: 'single research', rows: [coverageRow('a', 'research')], includes: 'It carries no win probability'},
    ];
    for (const scenario of scenarios) {
      const sentence = await page.evaluate(rows => {
        document.body.dataset.observed = new Date().toISOString();
        coverage = rows;
        expire();
        return document.querySelector('[data-completeness]').textContent;
      }, scenario.rows);
      if (scenario.expected) assert.equal(sentence, scenario.expected, scenario.name);
      if (scenario.includes) assert.ok(sentence.includes(scenario.includes), `${scenario.name}: ${sentence}`);
      assert.ok(!sentence.includes('0 of them carry'), `zero-gap prose regression: ${sentence}`);
      report.copy.push({scenario: scenario.name, sentence});
    }

    await page.setViewportSize({width: 320, height: 568});
    await page.goto(base + 'picks.html');
    const phone = await page.evaluate(() => {
      const row = [...document.querySelectorAll('tr[data-match]')].find(item => !item.hidden);
      const box = element => {
        const rect = element.getBoundingClientRect();
        return {top: rect.top + scrollY, bottom: rect.bottom + scrollY, height: rect.height};
      };
      return {
        overflow: document.documentElement.scrollWidth > innerWidth,
        row: box(row), pick: box(row.querySelector('.pick')),
        probability: box(row.querySelector('.prob-pair, .research-prob')),
        filters: box(document.querySelector('.filters')),
        tabbar: box(document.querySelector('.mobile-tabs')),
      };
    });
    assert.equal(phone.overflow, false, '320px horizontal overflow');
    assert.ok(phone.pick.bottom <= phone.tabbar.top,
      `first pick is behind/below the phone tab bar: ${JSON.stringify(phone)}`);
    assert.ok(phone.probability.bottom <= phone.tabbar.top,
      `first probabilities are behind/below the phone tab bar: ${JSON.stringify(phone)}`);
    assert.ok(phone.filters.top > phone.row.top, 'short-phone filters should follow the pick board, not bury it');
    report.phone.push(phone);
    fs.mkdirSync('runtime', {recursive: true});
    await page.screenshot({path: 'runtime/picks-320-9b97d585.png'});

    const firstOpen = data.matches.find(match => match.state === 'open');
    assert.ok(firstOpen, 'fresh candidate must contain an open row for the filter check');
    await page.locator('#search').fill(String(firstOpen.id));
    assert.equal(await page.locator('tr[data-match]:visible').count(), 1, 'match-id filter after the board');
    assert.match(await page.locator('#result-count').textContent(), /^1 match/);
    await page.locator('#reset').click();
    assert.equal(await page.locator('tr[data-match]:visible').count(), data.matches.filter(match => match.state === 'open').length);

    await page.setViewportSize({width: 390, height: 844});
    await page.goto(base + 'picks.html');
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    assert.ok(await page.locator('tr[data-match]:visible .pick').first().isVisible());
    assert.deepEqual(errors, []);
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-9b97d585.json', JSON.stringify(report, null, 2) + '\n');
    console.log('Passed: count-aware runtime summary copy; first pick and both probabilities above the 320x568 phone tab bar; post-board filters and 390px layout.');
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
