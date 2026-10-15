// Independent acceptance test. Run from an installed/built implementation root:
// node /path/to/verification-95b588c2/expiry-regression.cjs
// Uses only retained source-backed rows, never publishes synthetic picks.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {createRequire} = require('node:module');
const requireTarget = createRequire(path.resolve('package.json'));
const {chromium: playwright} = requireTarget('playwright-core');
const chromium = requireTarget('@sparticuz/chromium');
(async () => {
  const root = path.resolve('public');
  const data = JSON.parse(fs.readFileSync(path.join(root,'data/latest.json')));
  const limit = 8 * 3600000;
  const fixture = data.matches.find(m => {
    const q = m.evidence[0];
    if (!m.probabilities || !q?.updated_at) return false;
    const boundary = Date.parse(q.updated_at) + limit + 1000;
    return Date.parse(q.observed_at) + limit > boundary &&
      Date.parse(data.fixtures_observed_at) + limit > boundary &&
      Date.parse(m.lock) > boundary;
  });
  assert.ok(fixture, 'Need a retained priced row whose source-update TTL precedes observation TTL and lock');
  const q = fixture.evidence[0];
  const clock = Date.parse(q.updated_at) + limit + 1000;
  const server = http.createServer((req,res) => {
    const file = path.resolve(root, '.' + new URL(req.url, 'http://test').pathname);
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file)) {res.writeHead(404).end(); return;}
    res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css'})[path.extname(file)] || 'application/octet-stream');
    res.end(fs.readFileSync(file));
  });
  await new Promise(r => server.listen(0,'127.0.0.1',r));
  let browser;
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({args:chromium.default.args.filter(a=>a!=='--disable-web-security'),executablePath:await chromium.default.executablePath(),headless:true});
    const page = await browser.newPage({viewport:{width:390,height:844}});
    await page.addInitScript(t => { Date.now = () => t; }, clock);
    await page.goto(`http://127.0.0.1:${server.address().port}/picks.html`);
    const row = page.locator(`tr[data-match="${fixture.id}"]`);
    const count = await row.locator('.prob-pair').count();
    console.log(JSON.stringify({id:fixture.id,teams:fixture.teams,browser_time:new Date(clock).toISOString(),observed_at:q.observed_at,updated_at:q.updated_at,lock:fixture.lock,remaining_probability_displays:count},null,2));
    assert.equal(count,0,'Source-update TTL expired: browser must withhold probability even while observation and fixture TTL remain fresh');
    console.log('PASS: independent update-time expiry gate');
  } finally {
    if (browser) await browser.close();
    await new Promise(r=>server.close(r));
  }
})().catch(e=>{console.error(e);process.exitCode=1});
