'use strict';
// Filtering enhances server-rendered tables; all evidence remains usable without JS.
const search = document.querySelector('#search');
const statusFilter = document.querySelector('#status');
const eventFilter = document.querySelector('#event');
const rows = [...document.querySelectorAll('tr[data-match]')];
function filter() {
  const query = (search?.value || '').toLocaleLowerCase();
  const state = statusFilter?.value || 'all';
  const event = eventFilter?.value || 'all';
  let count = 0;
  for (const row of rows) {
    const matchesState = state === 'all' || row.dataset.status === state || (state === 'open' && row.dataset.status !== 'not_open');
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
[search,statusFilter,eventFilter].forEach(el => el?.addEventListener('input', filter));
document.querySelector('#reset')?.addEventListener('click', () => {
  if (search) search.value = '';
  if (statusFilter) statusFilter.value = 'all';
  if (eventFilter) eventFilter.value = 'all';
  filter();
});
if (rows.length) filter();
function expire() {
  const now = Date.now();
  const snapshot = Date.parse(document.body.dataset.observed);
  const globalStale = !Number.isFinite(snapshot) || now - snapshot > 8 * 3600000;
  const warning = document.querySelector('#runtime-stale');
  if (warning) warning.hidden = !globalStale;
  for (const row of rows) {
    const lock = Date.parse(row.dataset.lock);
    const evidence = Date.parse(row.dataset.evidence);
    const stale = !Number.isFinite(evidence) || now - evidence > 8*3600000;
    if (row.dataset.status === 'not_open' || !row.querySelector('.prob-pair')) continue;
    if (globalStale || stale || (Number.isFinite(lock) && lock <= now)) {
      const probability = row.querySelector('.probability');
      const pick = row.querySelector('.pick-cell');
      if (probability) probability.replaceChildren();
      if (pick) {
        const note = document.createElement('span');
        note.className = 'badge warning';
        note.textContent = lock <= now ? 'Lock time passed' : 'Stale • pick withheld';
        pick.replaceChildren(note);
      }
      row.classList.add('live-expired');
      row.dataset.status = lock <= now ? 'not_open' : 'unresolved';
    }
  }
  // Hero is also a recommendation, not an exemption from freshness/lock rules.
  const hero = document.querySelector('[data-next-lock]');
  if (hero && (globalStale || Date.parse(hero.dataset.nextLock) <= now || now-Date.parse(hero.dataset.nextEvidence)>8*3600000)) {
    const target = hero.querySelector('.pick-big');
    if (target) target.textContent = 'Refresh pending';
  }
  if (rows.length) filter();
}
expire();
setInterval(expire,60000);
// Direct evidence anchors open the native disclosure automatically.
function openEvidence() {
  const target = document.getElementById(location.hash.slice(1));
  if (target?.tagName === 'DETAILS') target.open = true;
}
openEvidence();
addEventListener('hashchange',openEvidence);
