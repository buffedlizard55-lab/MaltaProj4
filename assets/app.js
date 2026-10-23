'use strict';
// Progressive enhancement only: no third-party requests, accounts, or trackers.
const search = document.querySelector('#search');
const statusFilter = document.querySelector('#status');
const eventFilter = document.querySelector('#event');
const rows = [...document.querySelectorAll('tr[data-match]')];
const ttl = 8 * 3600000;
let coverage = [];
try { coverage = JSON.parse(document.querySelector('#coverage-data')?.textContent || '[]'); } catch { /* Fail closed below. */ }

function filter() {
  const query = (search?.value || '').toLocaleLowerCase().trim();
  const state = statusFilter?.value || 'all';
  const event = eventFilter?.value || 'all';
  let count = 0;
  for (const row of rows) {
    const matchesState = state === 'all' || row.dataset.status === state || (state === 'open' && row.dataset.status !== 'not_open') || (state === 'needs' && row.dataset.needs === '1');
    row.hidden = !(matchesState && row.dataset.search.includes(query) && (event === 'all' || row.dataset.event === event));
    if (!row.hidden) count++;
  }
  const counter = document.querySelector('#result-count');
  if (counter) counter.textContent = `${count} ${count === 1 ? 'match' : 'matches'} shown`;
  const empty = document.querySelector('#filter-empty');
  if (empty) empty.hidden = count !== 0;
}
const requested = new URLSearchParams(location.search).get('status');
if (statusFilter && [...statusFilter.options].some(o => o.value === requested)) statusFilter.value = requested;
[search, statusFilter, eventFilter].forEach(el => el?.addEventListener('input', filter));
document.querySelector('#reset')?.addEventListener('click', () => {
  if (search) search.value = '';
  if (statusFilter) statusFilter.value = 'all';
  if (eventFilter) eventFilter.value = 'all';
  filter();
});

let expiryTimer;
function expire() {
  clearTimeout(expiryTimer);
  const now = Date.now();
  const snapshot = Date.parse(document.body.dataset.observed);
  const globalStale = !Number.isFinite(snapshot) || now - snapshot >= ttl || snapshot - now > 300000;
  const warning = document.querySelector('#runtime-stale');
  if (warning) warning.hidden = !globalStale;
  const strip = document.querySelector('#freshness-strip');
  if (strip) {
    strip.classList.toggle('stale', globalStale);
    strip.classList.toggle('live', !globalStale);
    const state = strip.querySelector('.fresh-state');
    if (state) state.textContent = globalStale
      ? 'Snapshot expired or timestamp unverified: all current picks are withheld'
      : 'Snapshot inside its 8-hour evidence window';
  }
  const future = [snapshot + ttl];
  for (const row of rows) {
    const lock = Date.parse(row.dataset.lock);
    const start = Date.parse(row.dataset.start);
    const deadline = Date.parse(row.dataset.expires);
    future.push(lock, start, deadline);
    if (row.dataset.status === 'not_open') continue;
    const closed = (Number.isFinite(lock) && lock <= now) || (Number.isFinite(start) && start <= now);
    const expired = globalStale || !Number.isFinite(deadline) || deadline <= now;
    const recommendation = row.querySelector('.prob-pair, .pick-cell .pick');
    if (closed || (recommendation && expired)) {
      const probability = row.querySelector('.probability');
      if (probability) {
        probability.replaceChildren();
        probability.setAttribute('role', 'group');
        probability.setAttribute('aria-label', 'Probability withheld: evidence expired or pick locked');
      }
      const pick = row.querySelector('.pick-cell');
      if (pick) {
        const note = document.createElement('span');
        note.className = 'badge warning';
        note.textContent = closed ? 'Pick closed' : 'Expired · pick withheld';
        pick.replaceChildren(note);
      }
      const reasons = row.querySelector('.review-reason ul');
      if (reasons && !reasons.querySelector('[data-runtime-reason]')) {
        const reason = document.createElement('li');
        reason.dataset.runtimeReason = '';
        reason.textContent = closed ? 'The sourced pick lock or match start has passed.' : 'A source freshness deadline or bookmaker cutoff passed after this page was built. Historical evidence is not a current recommendation.';
        reasons.prepend(reason);
      }
      row.classList.add('live-expired');
      row.dataset.status = closed ? 'not_open' : 'unresolved';
      // An open row with expired evidence now belongs in the no-percentage filter.
      // A row whose pick lock passed is closed and must not be counted there.
      row.dataset.needs = closed ? '0' : '1';
    }
  }
  // Picks-at-a-glance rows carry the same deadlines as their table rows: a
  // locked match or an expired price must not keep showing a live pick here.
  for (const item of document.querySelectorAll('[data-glance-expires]')) {
    const lock = Date.parse(item.dataset.glanceLock);
    const start = Date.parse(item.dataset.glanceStart);
    const deadline = Date.parse(item.dataset.glanceExpires);
    future.push(lock, start, deadline);
    const closed = (Number.isFinite(lock) && lock <= now) || (Number.isFinite(start) && start <= now);
    const expired = globalStale || !Number.isFinite(deadline) || deadline <= now;
    if (closed || ((item.dataset.glancePriced === '1' || item.dataset.glanceResearch === '1') && expired)) {
      const message = closed ? 'Pick closed' : 'Expired · pick withheld';
      for (const pick of item.querySelectorAll('.glance-pick, .glance-card-pick-team, .queue-pick, .unresolved-pick')) {
        pick.textContent = message;
      }
      // Phone cards have different markup from the desktop glance list. Clear
      // their percentage and bar too, not just a desktop-only .glance-pick.
      const probability = item.querySelector('.glance-card-prob');
      if (probability) probability.textContent = 'Withheld';
      item.querySelector('.glance-card-prob-bar')?.remove();
      const label = item.querySelector('.glance-card-pick-label');
      if (label) label.textContent = 'NOT CURRENT';
      item.classList.add('live-expired');
    }
  }
  for (const hero of document.querySelectorAll('[data-next-expires]')) {
    const deadline = Date.parse(hero.dataset.nextExpires);
    future.push(deadline);
    if (globalStale || !Number.isFinite(deadline) || deadline <= now) {
      const target = hero.querySelector('.pick-big');
      if (target) target.textContent = 'Pick withheld · refresh pending';
    }
  }
  for (const label of document.querySelectorAll('[data-evidence-status]')) {
    const deadline = Date.parse(label.dataset.expires);
    if (globalStale || !Number.isFinite(deadline) || deadline <= now) {
      label.textContent = 'Historical evidence only — not a current pick.';
    }
    future.push(deadline);
  }
  // Research quotes have their own dated receipt, never a perpetual static price.
  for (const quote of document.querySelectorAll('[data-research-quote]')) {
    const observed = Date.parse(quote.dataset.researchObserved);
    const deadline = Date.parse(quote.dataset.researchExpires);
    future.push(deadline);
    if (!Number.isFinite(observed) || !Number.isFinite(deadline) || observed - now > 300000 || deadline <= now) {
      const note = document.createElement('p');
      note.className = 'notice info';
      note.textContent = 'Research quote expired or unverified. No current probability is published here; open the current picks board or the dated historical receipt.';
      quote.replaceChildren(note);
      quote.hidden = false;
    }
  }
  // Counts use the complete snapshot, not just the five featured table rows.
  const open = coverage.filter(m => m.state === 'open' && Date.parse(m.lock) > now && Date.parse(m.start) > now);
  const priced = open.filter(m => !globalStale && m.priced && Date.parse(m.expires_at) > now);
  const researched = open.filter(m => !globalStale && m.research && !m.priced && Date.parse(m.expires_at) > now);
  const modelled = priced.filter(m => m.model);
  const counts = {open: open.length, priced: priced.length, researched: researched.length,
    picked: [...priced, ...researched].filter(m => m.picked).length,
    model: modelled.length, market: priced.length - modelled.length,
    missing: open.length - priced.length,
    unresolved: open.length - priced.length - researched.length,
    percent: open.length ? Math.round(priced.length / open.length * 100) : 0};
  for (const el of document.querySelectorAll('[data-count]')) el.textContent = String(counts[el.dataset.count] ?? '');
  // The prose that says "every open match has a pick" is written at build time.
  // Without this the counters could read "0 with a pick" while the sentence next
  // to them still claimed 23 picks -- exactly the contradiction a phone reader
  // saw on 2026-10-23. Rewrite it from the same runtime counts as the numbers.
  for (const el of document.querySelectorAll('[data-completeness]')) {
    let sentence;
    if (globalStale) {
      sentence = 'This snapshot is outside its 8-hour evidence window, so no current pick is published until the next successful refresh. The numbered evidence below is historical.';
    } else if (!counts.open) {
      sentence = 'No open CS2 fixture at the last check.';
    } else if (counts.unresolved === 0 && counts.missing === counts.researched) {
      sentence = `Every one of the ${counts.open} open matches has a pick. ${counts.researched} of them carry no win probability because no verified two-way line or two-team model input exists — the reason for each is listed below.`;
    } else if (counts.unresolved === 0) {
      sentence = `Every one of the ${counts.open} open matches has a pick, and every pick carries a win probability.`;
    } else {
      sentence = `${counts.picked} of ${counts.open} open matches have a pick; ${counts.unresolved} have no supported pick and ${counts.researched} carry a research pick without a percentage. The reason for each is listed below.`;
    }
    el.textContent = sentence;
  }
  for (const m of coverage) future.push(Date.parse(m.lock), Date.parse(m.start), Date.parse(m.expires_at));
  if (rows.length) filter();
  const next = Math.min(...future.filter(t => Number.isFinite(t) && t > now), now + 60000);
  expiryTimer = setTimeout(expire, Math.max(25, next - now + 1));
}
expire();
addEventListener('pageshow', expire);
document.addEventListener('visibilitychange', () => { if (!document.hidden) expire(); });

function openEvidence() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target) return;
  // Old summary anchors remain useful after duplicate detail tables are folded.
  // Reveal every ancestor disclosure, not just evidence-ledger DETAILS targets.
  let opened = false;
  for (let node = target; node; node = node.parentElement) {
    if (node.tagName === 'DETAILS' && !node.open) { node.open = true; opened = true; }
  }
  if (opened) target.scrollIntoView({block: 'start'});
}
openEvidence();
addEventListener('hashchange', openEvidence);
