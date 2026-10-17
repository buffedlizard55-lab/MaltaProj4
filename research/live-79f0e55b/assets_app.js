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
  const future = [snapshot + ttl];
  for (const row of rows) {
    const lock = Date.parse(row.dataset.lock);
    const start = Date.parse(row.dataset.start);
    const deadline = Date.parse(row.dataset.expires);
    future.push(lock, start, deadline);
    if (row.dataset.status === 'not_open') continue;
    const closed = (Number.isFinite(lock) && lock <= now) || (Number.isFinite(start) && start <= now);
    const expired = globalStale || !Number.isFinite(deadline) || deadline <= now;
    if (closed || (row.querySelector('.prob-pair') && expired)) {
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
    }
  }
  const hero = document.querySelector('[data-next-expires]');
  if (hero) {
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
  // Counts use the complete snapshot, not just the five featured table rows.
  const open = coverage.filter(m => m.state === 'open' && Date.parse(m.lock) > now && Date.parse(m.start) > now);
  const priced = open.filter(m => !globalStale && m.priced && Date.parse(m.expires_at) > now);
  const researched = open.filter(m => m.research && !m.priced);
  const modelled = priced.filter(m => m.model);
  const counts = {open: open.length, priced: priced.length, researched: researched.length,
    model: modelled.length, market: priced.length - modelled.length,
    unresolved: open.length - priced.length - researched.length,
    percent: open.length ? Math.round(priced.length / open.length * 100) : 0};
  for (const el of document.querySelectorAll('[data-count]')) el.textContent = String(counts[el.dataset.count] ?? '');
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
  if (target?.tagName === 'DETAILS') target.open = true;
}
openEvidence();
addEventListener('hashchange', openEvidence);
