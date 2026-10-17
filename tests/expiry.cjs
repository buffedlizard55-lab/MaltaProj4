// Deterministic UI safety tests. Synthetic DOM fixtures stay inside this test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true});
  try {
    const now = Date.parse('2026-10-15T09:00:00Z');
    const scenarios = [
      {name: 'source-update deadline', expires: '2026-10-15T09:00:00Z'},
      {name: 'bookmaker cutoff deadline', expires: '2026-10-15T08:59:59Z'},
      {name: 'malformed deadline', expires: 'unverified'},
      {name: 'source fixture expired', expires: '2026-10-15T12:00:00Z', observed: '2026-10-15T01:00:00Z'},
      {name: 'pick lock', expires: '2026-10-15T09:00:00Z', lock: '2026-10-15T09:00:00Z'},
      {name: 'unresolved rows also lock', expires: null, lock: '2026-10-15T09:00:00Z', unpriced: true},
      {name: 'valid live deadline', expires: '2026-10-15T09:00:01Z', valid: true},
    ];
    const context = await browser.newContext();
    await context.addInitScript(t => {Date.now = () => t;}, now);
    const page = await context.newPage();
    for (const scenario of scenarios) {
      await page.goto('about:blank');
      // setContent does not trigger init scripts; install the test clock explicitly.
      await page.evaluate(t => {Date.now = () => t;}, now);
      const observed = scenario.observed || '2026-10-15T08:00:00Z';
      const lock = scenario.lock || '2026-10-15T11:54:00Z';
      const match = {id: 'TEST_ONLY', state: 'open', start: '2026-10-15T12:00:00Z', lock,
        priced: !scenario.unpriced, expires_at: scenario.expires};
      await page.setContent(`<body data-observed="${observed}">
        <script id="coverage-data" type="application/json">${JSON.stringify([match])}</script>
        <div id="runtime-stale" hidden></div><span data-count="priced"></span>
        <table><tbody><tr data-match="TEST_ONLY" data-status="${scenario.unpriced ? 'unresolved' : 'priced'}"
          data-search="test only" data-event="test" data-start="${match.start}" data-lock="${lock}" data-expires="${scenario.expires}">
          <td><div class="probability">${scenario.unpriced ? '' : '<div class="prob-pair">60% / 40%</div>'}</div></td>
          <td class="pick-cell"><span class="pick">Test only</span></td></tr></tbody></table>
        <div data-next-expires="${scenario.expires}"><span class="pick-big">Test only 60%</span></div>
        <p data-evidence-status data-expires="${scenario.expires}">Current evidence at build</p></body>`);
      await page.addScriptTag({content: fs.readFileSync('site/assets/app.js', 'utf8')});
      assert.equal(await page.locator('.prob-pair').count(), scenario.valid ? 1 : 0, scenario.name);
      if (!scenario.valid) {
        assert.equal(await page.locator('.pick-cell .pick').count(), 0, scenario.name);
        assert.match(await page.locator('.pick-big').innerText(), /withheld/, scenario.name);
        assert.match(await page.locator('[data-evidence-status]').innerText(), /Historical/, scenario.name);
      }
      assert.equal(await page.locator('[data-count=priced]').innerText(), scenario.valid ? '1' : '0', scenario.name);
      if (scenario.lock) assert.equal(await page.locator('tr[data-match]').getAttribute('data-status'), 'not_open');

    }
    for (const scenario of [
      {deadline:'2026-10-15T09:00:00Z', observed:'2026-10-15T08:00:00Z', valid:false},
      {deadline:'2026-10-15T09:00:01Z', observed:'2026-10-15T08:00:00Z', valid:true},
      {deadline:'unverified', observed:'2026-10-15T08:00:00Z', valid:false},
      {deadline:'2026-10-15T10:00:00Z', observed:'2026-10-15T09:06:00Z', valid:false},
    ]) {
      await page.goto('about:blank');
      await page.evaluate(t => {Date.now = () => t;}, now);
      await page.setContent(`<body data-observed="2026-10-15T08:00:00Z">
        <script id="coverage-data" type="application/json">[]</script>
        <div data-research-quote data-research-observed="${scenario.observed}" data-research-expires="${scenario.deadline}">Test quote 65.53%</div></body>`);
      await page.addScriptTag({content: fs.readFileSync('site/assets/app.js','utf8')});
      const text=await page.locator('[data-research-quote]').innerText();
      assert.equal(text.includes('65.53%'),scenario.valid,'Research quote exact-boundary expiry');
      if (!scenario.valid) assert.match(text,/expired or unverified/);
    }
    console.log('Passed: seven board expiry scenarios plus four research-quote boundary/future-clock scenarios.');
  } finally {
    await browser.close();
  }
})().catch(e => {console.error(e); process.exit(1);});
