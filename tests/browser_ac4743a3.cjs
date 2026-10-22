// Recommendation expiry must work on the phone card, desktop list and queue,
// including qualitative picks. All synthetic inputs are test-only DOM fixtures.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
  chromium.setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({
    args: chromium.default.args.filter(a => a !== '--disable-web-security'),
    executablePath: await chromium.default.executablePath(), headless: true
  });
  const now = Date.parse('2026-10-22T09:00:00Z');
  const scenarios = [
    {name: 'research exact boundary', research: true, deadline: '2026-10-22T09:00:00Z'},
    {name: 'research still live', research: true, deadline: '2026-10-22T09:00:00.001Z', valid: true},
    {name: 'research missing deadline', research: true, deadline: ''},
    {name: 'research malformed deadline', research: true, deadline: 'unverified'},
    {name: 'research global snapshot expired', research: true, deadline: '2026-10-22T10:00:00Z', observed: '2026-10-22T01:00:00Z'},
    {name: 'research lock boundary', research: true, deadline: '2026-10-22T10:00:00Z', lock: '2026-10-22T09:00:00Z'},
    {name: 'priced phone card expired', deadline: '2026-10-22T09:00:00Z'},
    {name: 'priced phone card live', deadline: '2026-10-22T09:00:00.001Z', valid: true}
  ];
  try {
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    for (const scenario of scenarios) {
      await page.goto('about:blank');
      await page.evaluate(t => { Date.now = () => t; }, now);
      const lock = scenario.lock || '2026-10-22T11:54:00Z';
      const start = '2026-10-22T12:00:00Z';
      const observed = scenario.observed || '2026-10-22T08:00:00Z';
      const research = scenario.research ? '1' : '0';
      const priced = scenario.research ? '0' : '1';
      const attrs = `data-glance-lock="${lock}" data-glance-start="${start}" data-glance-expires="${scenario.deadline}" data-glance-research="${research}" data-glance-priced="${priced}"`;
      const match = {state: 'open', lock, start, expires_at: scenario.deadline, picked: true, research: !!scenario.research, priced: !scenario.research};
      await page.setContent(`<body data-observed="${observed}">
        <script id="coverage-data" type="application/json">${JSON.stringify([match])}</script>
        <div id="runtime-stale" hidden></div><div id="freshness-strip" class="live"><span class="fresh-state"></span></div>
        <span data-count="researched"></span><span data-count="picked"></span><span data-count="unresolved"></span>
        <table><tbody><tr data-match="TEST_ONLY" data-status="${scenario.research ? 'research' : 'priced'}"
          data-search="test" data-event="test" data-lock="${lock}" data-start="${start}" data-expires="${scenario.deadline}">
          <td><div class="probability">${scenario.research ? 'No percentage' : '<div class="prob-pair">60% / 40%</div>'}</div></td>
          <td class="pick-cell"><span class="pick">Test only A</span></td></tr></tbody></table>
        <a class="glance-row" ${attrs}><span class="glance-pick">Test only A</span></a>
        <a class="glance-card-mobile" ${attrs}><span class="glance-card-pick-label">PICK</span>
          <span class="glance-card-pick-team">Test only A</span><span class="glance-card-prob">${scenario.research ? 'No percentage' : '60%'}</span>
          ${scenario.research ? '' : '<div class="glance-card-prob-bar"></div>'}</a>
        <a class="queue" ${attrs}><span class="queue-pick">Test only A</span></a>
      </body>`);
      await page.addScriptTag({content: fs.readFileSync('site/assets/app.js', 'utf8')});
      const active = !!scenario.valid;
      assert.equal(await page.locator('.pick-cell .pick').count(), active ? 1 : 0, scenario.name);
      for (const selector of ['.glance-pick', '.glance-card-pick-team', '.queue-pick']) {
        const text = await page.locator(selector).innerText();
        assert.equal(text.includes('Test only A'), active, `${scenario.name}: ${selector}`);
        if (!active) assert.match(text, /Pick closed|withheld/, scenario.name);
      }
      if (!active) {
        assert.equal(await page.locator('.glance-card-prob').innerText(), 'Withheld', scenario.name);
        assert.equal(await page.locator('.glance-card-prob-bar').count(), 0, scenario.name);
      }
      assert.equal(await page.locator('[data-count=picked]').innerText(), active ? '1' : '0', scenario.name);
      assert.equal(await page.locator('[data-count=researched]').innerText(), active && scenario.research ? '1' : '0', scenario.name);
      if (scenario.observed) {
        assert.equal(await page.locator('#freshness-strip').getAttribute('class'), 'stale');
        assert.match(await page.locator('.fresh-state').innerText(), /withheld/);
      }
    }
    console.log('Passed: eight phone/desktop/queue/research expiry and live-count scenarios.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
