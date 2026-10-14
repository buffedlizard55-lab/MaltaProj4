'use strict';
(() => {
  const rows = [...document.querySelectorAll('.match-table tbody tr')];
  const search = document.querySelector('#search');
  const status = document.querySelector('#status');
  const tier = document.querySelector('#tier');
  function filter() {
    if (!search) return;
    const q = search.value.trim().toLocaleLowerCase();
    const view = status.value;
    let count = 0;
    for (const row of rows) {
      const matchView = view === 'all' || (view === 'open' && row.dataset.state !== 'locked') || row.dataset.state === view || row.dataset.method === view;
      row.hidden = !(matchView && (tier.value === 'all' || tier.value === row.dataset.tier) && row.dataset.search.toLocaleLowerCase().includes(q));
      if (!row.hidden) count++;
    }
    document.querySelector('#result-count').textContent = `${count} of ${rows.length} source fixtures shown. “Open” is as of the printed refresh time.`;
    document.querySelector('#no-results').hidden = count !== 0;
  }
  function revealHash() {
    if (!location.hash) return;
    const row = document.getElementById(location.hash.slice(1));
    if (row && status) {
      status.value = 'all'; search.value = ''; tier.value = 'all'; filter();
      row.scrollIntoView({block:'start'});
    }
  }
  if (search) {
    const view = new URLSearchParams(location.search).get('view');
    if ([...status.options].some(o => o.value === view)) status.value = view;
    [search,status,tier].forEach(el => el.addEventListener('input', filter));
    document.querySelector('.filters').addEventListener('reset', () => setTimeout(filter, 0));
    filter(); revealHash(); window.addEventListener('hashchange', revealHash);
  }
  function freshness() {
    const age = Date.now() - Date.parse(document.body.dataset.updated);
    const stale = !Number.isFinite(age) || age > 8 * 3600 * 1000 || age < -5 * 60 * 1000;
    document.body.classList.toggle('stale', stale);
    document.querySelector('#stale-notice').hidden = !stale;
    document.querySelector('#freshness').textContent = stale ? 'Stale snapshot' : 'Recent snapshot';
    for (const row of rows) {
      const locked = Date.parse(row.dataset.lock) <= Date.now();
      row.classList.toggle('expired', locked && row.dataset.state !== 'locked');
    }
  }
  freshness(); setInterval(freshness, 60_000);
})();
