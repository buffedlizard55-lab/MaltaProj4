// Session 28e4f2a1: measure the executive-summary pick directory on real phones.
//
// The user's requirement is that a visitor on a phone can find where the picks
// for the matches are, read every category, and see how many matches each one
// produced - without a horizontal scroll, a clipped cell, or a cell hidden
// behind the fixed bottom tab bar. This suite measures the generated artifact
// (public/) at three phone sizes and fails on any of those.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium: playwright} = require('playwright-core');
const chromium = require('@sparticuz/chromium');

const VIEWPORTS = [{name: 'iPhone SE', width: 320, height: 568},
                   {name: 'iPhone 14', width: 390, height: 844},
                   {name: 'Pixel 7', width: 412, height: 915}];

(async () => {
  const root = path.resolve('public');
  const data = JSON.parse(fs.readFileSync(path.join(root, 'data/latest.json'), 'utf8'));
  const openCount = data.matches.filter(m => m.state === 'open').length;
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
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/MaltaProj4/`;
  let browser;
  const report = {measured_at: new Date().toISOString(), artifact: 'public/', open_matches: openCount,
                  viewports: [], failures: []};
  try {
    await chromium.inflate(path.resolve('node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
    chromium.setupLambdaEnvironment('/tmp/al2023/lib');
    browser = await playwright.launch({
      args: chromium.default.args.filter(a => a !== '--disable-web-security'),
      executablePath: await chromium.default.executablePath(), headless: true});
    const page = await browser.newPage({viewport: {width: 320, height: 568}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));

    for (const viewport of VIEWPORTS) {
      await page.setViewportSize({width: viewport.width, height: viewport.height});
      for (const slug of ['index', 'unresolved']) {
        const response = await page.goto(base + slug + '.html');
        assert.equal(response.status(), 200);
        // The stylesheet enables smooth scrolling, so the scroll must be made
        // instant and given a frame before anything is hit-tested.
        const found = await page.evaluate(() => {
          const directory = document.querySelector('#picks-directory');
          if (!directory) return false;
          document.documentElement.style.scrollBehavior = 'auto';
          directory.querySelector('tbody tr').scrollIntoView({block: 'center', behavior: 'instant'});
          return true;
        });
        assert.equal(found, true, `${slug}: pick directory missing at ${viewport.width}px`);
        await page.waitForTimeout(80);
        const measured = await page.evaluate(() => {
          const directory = document.querySelector('#picks-directory');
          if (!directory) return {missing: true};
          const tabs = document.querySelector('.mobile-tabs');
          const tabTop = tabs ? tabs.getBoundingClientRect().top : Infinity;
          const rows = [...directory.querySelectorAll('tbody tr')].map(tr => ({
            step: tr.getAttribute('data-directory-step'),
            cells: [...tr.querySelectorAll('td')].map(td => {
              const rect = td.getBoundingClientRect();
              const style = getComputedStyle(td);
              return {text: (td.textContent || '').trim().slice(0, 60),
                      height: Math.round(rect.height), width: Math.round(rect.width),
                      display: style.display, visibility: style.visibility,
                      ariaHidden: td.getAttribute('aria-hidden')};
            }),
            // A cell that reaches below the tab bar is a cell a phone cannot read.
            bottom: Math.round(tr.getBoundingClientRect().bottom),
          }));
          const firstRow = directory.querySelector('tbody tr');
          const firstCount = firstRow ? firstRow.querySelectorAll('td')[1] : null;
          const box = firstCount ? firstCount.getBoundingClientRect() : null;
          const hit = box ? document.elementFromPoint(
            Math.min(box.left + box.width / 2, innerWidth - 2),
            Math.min(box.top + box.height / 2, innerHeight - 2)) : null;
          const totals = [...directory.querySelectorAll('tbody tr')]
            .filter(tr => tr.getAttribute('data-directory-step') !== 'total')
            .reduce((sum, tr) => sum + Number((tr.querySelectorAll('td')[1] || {textContent: '0'}).textContent.trim()), 0);
          const pressed = directory.querySelector('.directory-jump');
          return {
            overflow: document.documentElement.scrollWidth > innerWidth,
            rows,
            total_sum: totals,
            total_row: Number((directory.querySelector('tr[data-directory-step="total"] td:nth-child(2)') || {textContent: '0'}).textContent.trim()),
            in_summary: Boolean(document.querySelector('#unresolved-limits #picks-directory')),
            hit_tag: hit ? (hit.tagName + (hit.className && typeof hit.className === 'string' ? '.' + hit.className.split(' ')[0] : '')) : null,
            tab_top: tabTop,
            count_cell_covered: !!(box && hit && !firstCount.contains(hit) && hit !== firstCount),
            count_cell_below_tabbar: !!(box && box.top > tabTop),
            jump: pressed ? pressed.getAttribute('href') : null,
            destinations: [...new Set([...directory.querySelectorAll('a[href]')].map(a => a.getAttribute('href')))]
          };
        });
        assert.equal(measured.missing, undefined, `${slug}: pick directory missing at ${viewport.width}px`);
        assert.equal(measured.overflow, false, `${slug}: horizontal overflow at ${viewport.width}px`);
        // Seven published ladder steps that price a row, one "no pick" row and a
        // total row: 9 <tbody> rows, every one of them measured above.
        assert.equal(measured.rows.length, 9, `${slug}: expected 8 category rows + a total row`);
        for (const row of measured.rows) {
          for (const [index, cell] of row.cells.entries()) {
            assert.notEqual(cell.display, 'none', `${slug} ${row.step} cell ${index} is display:none at ${viewport.width}px`);
            assert.notEqual(cell.visibility, 'hidden', `${slug} ${row.step} cell ${index} is invisible at ${viewport.width}px`);
            assert.ok(cell.height > 0 && cell.width > 0, `${slug} ${row.step} cell ${index} has no box at ${viewport.width}px`);
            assert.ok(cell.text.length > 0, `${slug} ${row.step} cell ${index} is empty at ${viewport.width}px`);
          }
        }
        assert.equal(measured.count_cell_covered, false,
          `${slug}: the first count is covered by another element (the tab bar) at ${viewport.width}px`);
        assert.equal(measured.count_cell_below_tabbar, false,
          `${slug}: the first count is below the tab bar at ${viewport.width}px`);
        assert.equal(measured.total_sum, measured.total_row,
          `${slug}: category counts do not add up to the published total at ${viewport.width}px`);
        assert.equal(measured.total_row, openCount,
          `${slug}: the published total is not this snapshot's open count at ${viewport.width}px`);
        if (slug === 'index') {
          assert.equal(measured.in_summary, true, 'the directory must be inside the executive summary');
        } else {
          assert.equal(measured.jump, '#unresolved-rows', 'the unresolved page must offer a one-tap jump');
          await page.click('.directory-jump');
          await page.waitForTimeout(120);
          const hash = await page.evaluate(() => location.hash);
          assert.equal(hash, '#unresolved-rows', 'the jump link must move to the match rows');
          const rowsTop = await page.evaluate(() => {
            const marker = document.querySelector('#unresolved-rows');
            return Math.round(marker.getBoundingClientRect().top);
          });
          assert.ok(rowsTop < 220, `the jump must land on the rows (top ${rowsTop}px at ${viewport.width}px)`);
        }
        report.viewports.push({...viewport, page: slug, ...measured});
      }
    }
    assert.deepEqual(errors, [], 'no page errors');
    report.failures = [];
    console.log(JSON.stringify(report, null, 1));
  } catch (error) {
    report.failures = [error.message];
    fs.writeFileSync(path.join('research', 'session-28e4f2a1', 'phone-directory-failure.json'),
                     JSON.stringify(report, null, 1));
    throw error;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
    fs.writeFileSync(path.join('research', 'session-28e4f2a1', 'phone-directory-measurements.json'),
                     JSON.stringify(report, null, 1));
  }
})().catch(error => { console.error(error); process.exit(1); });
