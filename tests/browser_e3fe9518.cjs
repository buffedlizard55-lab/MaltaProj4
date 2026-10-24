// Read-only mobile acceptance: actual two-team values, source-class labels,
// executive-summary links, one-tap evidence, and real expiry (no DOM overrides).
// Default: public/ under the GitHub Pages subpath at the snapshot's own clock.
// SITE=https://... VERIFY_LIVE=1 checks the real published site/device clock.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

(async () => {
  let server, browser;
  const report = {clock: process.env.VERIFY_LIVE ? 'actual_device_time' : 'snapshot_time_not_live',
    checked_at: new Date().toISOString(), passed: false, viewports: [], firstCardMeasurements: []};
  try {
    let base = process.env.SITE;
    if (!base) {
      const root = path.resolve('public');
      server = http.createServer((req, res) => {
        const pathname = decodeURIComponent(new URL(req.url, 'http://test').pathname)
          .replace(/^\/MaltaProj4\//, '/');
        const file = path.resolve(root, '.' + pathname + (pathname.endsWith('/') ? 'index.html' : ''));
        if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
          res.writeHead(404); res.end(); return;
        }
        res.setHeader('content-type', {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
          '.json': 'application/json', '.svg': 'image/svg+xml'}[path.extname(file)] || 'text/plain');
        res.end(fs.readFileSync(file));
      });
      await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
      base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
    }
    base = base.replace(/\/?$/, '/');
    report.site = base;
    const response = await fetch(base + 'data/latest.json');
    assert.equal(response.status, 200);
    const snapshotBytes = Buffer.from(await response.arrayBuffer());
    report.snapshot_sha256 = crypto.createHash('sha256').update(snapshotBytes).digest('hex');
    const snapshot = JSON.parse(snapshotBytes.toString('utf8'));
    const offsetMinutes = Number(process.env.CANONICAL_OFFSET_MINUTES || 0);
    assert.ok(Number.isFinite(offsetMinutes) && offsetMinutes >= 0 && offsetMinutes < 480);
    if (process.env.VERIFY_LIVE) assert.equal(offsetMinutes, 0, 'A live check must never use a simulated clock offset');
    report.canonical_offset_minutes = offsetMinutes;
    const clock = process.env.VERIFY_LIVE ? Date.now()
      : Date.parse(snapshot.generated_at) + offsetMinutes * 60000;
    const inventoryFresh = clock - Date.parse(snapshot.fixtures_observed_at) < 8 * 3600000;
    const open = snapshot.matches.filter(m => m.state === 'open'
      && Math.min(Date.parse(m.start), Date.parse(m.lock)) > clock);
    const actionable = open.filter(m => inventoryFresh && m.pick && Date.parse(m.expires_at) > clock);
    Object.assign(report, {snapshot: snapshot.generated_at, inventoryFresh, open: open.length, actionable: actionable.length});
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({args: chromium.default.args.filter(arg => arg !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true});
    const context = await browser.newContext();
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.clock.install({time: new Date(clock)});
    for (const [width, height] of [[320, 568], [390, 844], [768, 1024], [1440, 900]]) {
      await page.setViewportSize({width, height});
      for (const slug of ['index', 'picks', 'matches', 'unresolved', 'review', 'sources']) {
        assert.equal((await page.goto(base + slug + '.html')).status(), 200);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false,
          `${slug}: overflow at ${width}px`);
        assert.equal(await page.locator('h1').count(), 1);
      }
      await page.goto(base + 'index.html');
      // The named executive summary links to all requested destinations, even
      // when phone-first order places the match list before the full summary.
      for (const target of ['picks.html', 'matches.html', 'unresolved.html', 'review.html']) {
        assert.ok(await page.locator(`#exec-summary a[href="${target}"]`).count() > 0,
          `Missing executive-summary destination ${target}`);
      }
      assert.ok(await page.locator('#unresolved-limits').count() > 0);
      assert.ok(await page.locator('#unresolved-picks').count() > 0);
      if (width <= 650) {
        const cta = page.locator('#freshness-strip a.fresh-cta');
        const ctaBox = await cta.boundingBox();
        assert.ok(ctaBox && ctaBox.height >= 44 && ctaBox.y >= 0 && ctaBox.y + ctaBox.height <= height,
          `First-screen updated-picks CTA at ${width}px: ${JSON.stringify(ctaBox)}`);
        assert.ok(await page.locator('.mobile-tabs a[href="picks.html"]').isVisible());
        // Every current card, not just the featured card, prints both source
        // teams' shares and explicitly marks our chosen side.
        for (const match of actionable.filter(m => m.probabilities !== null)) {
          const card = page.locator(`.glance-card-mobile[href="evidence.html#match-${match.id}"]`);
          assert.equal(await card.count(), 1, `Missing phone card ${match.id}`);
          const scores = card.locator('.glance-card-score');
          assert.equal(await scores.count(), 2);
          for (let i = 0; i < 2; i++) {
            const text = await scores.nth(i).innerText();
            assert.ok(text.includes(match.teams[i]), `Team order changed in ${match.id}`);
            assert.ok(text.includes((100 * match.probabilities[i]).toFixed(1) + '%'),
              `Probability differs from source record for ${match.id}`);
          }
          assert.equal(await card.locator('.glance-card-pick-team').innerText(), match.pick);
          const meta = await card.locator('.glance-card-meta').innerText();
          if (match.method.startsWith('model_vrs')) assert.match(meta, /model/i);
          if (match.method === 'exchange_wide') assert.match(meta, /low confidence/i);
          if ((match.evidence[0]?.provider || '').includes('via BO3')) assert.match(meta, /listing/i);
        }
        if (actionable.length) {
          const first = page.locator(`.glance-card-mobile[href="evidence.html#match-${actionable[0].id}"]`);
          const answer = await first.locator('.glance-card-scores, .glance-card-pick').last().boundingBox();
          const nav = await page.locator('.mobile-tabs').boundingBox();
          report.firstCardMeasurements.push({width, height, match: actionable[0].id, answer, nav});
          assert.ok(answer && nav && answer.y + answer.height <= nav.y,
            `Both first-pick shares must fit above bottom nav: ${JSON.stringify({width, answer, nav})}`);
          await first.click();
          assert.ok(page.url().endsWith('evidence.html#match-' + actionable[0].id));
          assert.equal(await page.locator('#match-' + actionable[0].id).getAttribute('open'), '');
        }
      }
      assert.deepEqual(errors, []);
      report.viewports.push({width, height, verified: true});
    }
    // Advance to a genuinely expired clock. No warning is hidden and no DOM
    // value is replaced by the test to manufacture a "fresh" screen.
    const expired = page;
    await expired.setViewportSize({width: 390, height: 844});
    await expired.clock.setFixedTime(new Date(Date.parse(snapshot.fixtures_observed_at) + 8 * 3600000 + 1));
    await expired.goto(base + 'index.html');
    assert.equal(await expired.locator('#runtime-stale').isVisible(), true);
    const phoneShares = await expired.locator('.glance-card-prob, .glance-card-other-prob').allTextContents();
    assert.ok(phoneShares.every(text => !/\d\s*%/.test(text)), 'Expired phone percentages remain actionable');
    await expired.goto(base + 'picks.html');
    assert.equal(await expired.locator('.prob-pair').count(), 0);
    assert.equal(await expired.locator('.pick-cell .pick').count(), 0);
    report.expiryVerified = true;
    if (process.env.VERIFY_LIVE) {
      assert.ok(inventoryFresh, 'Live snapshot is expired; do not claim the deployment is current');
    }
    report.passed = true;
    console.log('Passed: every phone card agrees with the source snapshot, primary/listing/model labels, first-screen pick links, one-tap evidence and genuine expiry.');
  } catch (error) {
    report.error = error.message;
    throw error;
  } finally {
    fs.mkdirSync('runtime', {recursive: true});
    fs.writeFileSync('runtime/browser-e3fe9518.json', JSON.stringify(report, null, 2) + '\n');
    if (process.env.VERIFY_LIVE) {
      const message = JSON.stringify(report).replaceAll('%', '%25').replaceAll('\r', '%0D').replaceAll('\n', '%0A');
      console.log(`::${report.passed ? 'notice' : 'error'} title=e3fe9518-live-mobile-receipt::${message}`);
    }
    if (browser) await browser.close();
    if (server) await new Promise(resolve => server.close(resolve));
  }
})().catch(error => {console.error(error); process.exit(1);});
