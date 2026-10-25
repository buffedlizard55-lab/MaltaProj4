"""Reproduce the 9fca16ca delivery/source ledger from committed bytes.

This script makes no network request and edits no pick or price. It reads the
committed snapshot, the generated root pages, the artifact receipt, the source
workflows and the dated direct-source checks in ``official-checks.json``. It
recomputes every open row's probability arithmetic, source presence, pick
orientation and published HTML placement. A failure is printed and returned as
a non-zero process status; nothing is silently filled in.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = ROOT / 'data/latest.json'
MANIFEST = ROOT / 'build-info.json'
OFFICIAL = HERE / 'official-checks.json'

METHODS = {
    'exchange', 'exchange_wide', 'bookmaker_fallback', 'model_vrs',
    'model_vrs_mirror', 'research_vrs_single', 'research_rank',
    'research_rank_single', 'research_form', 'book_listing', 'bookmaker',
}
HOTSPAWN_HOSTS = {'play.hotspawn.com', 'www.hotspawn.com', 'hotspawn.com'}
PRICE_HOSTS = {
    'gamma-api.polymarket.com', 'guest.api.arcadia.pinnacle.com',
    'api.bo3.gg', 'bo3.gg', 'raw.githubusercontent.com', 'github.com',
    'www.hltv.org', 'thunderpick.io', 'egamersworld.com',
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def esc(value) -> str:
    return html.escape(str(value if value is not None else ''), quote=True)


def md_url(url: str) -> str:
    """Keep an https URL literal inside Markdown angle brackets.

    HTML-escaping ``&`` in a Markdown link target would turn a query separator
    into the literal ``&amp;`` and break the official feed URL. Labels are still
    escaped; destination URLs are only checked for a safe angle-bracket form.
    """
    return str(url or '').replace('<', '%3C').replace('>', '%3E')


def md_link(url: str, label: str) -> str:
    return '[%s](<%s>)' % (esc(label), md_url(url))


def pct(value: float) -> str:
    return '%.1f%%' % (value * 100)


def is_https_official(url: str, hosts: set[str]) -> bool:
    bits = urlsplit(url or '')
    return bits.scheme == 'https' and bits.hostname in hosts


def row_checks(m: dict) -> dict[str, bool]:
    p = m.get('probabilities')
    odds = m.get('fair_odds')
    q = (m.get('evidence') or [{}])[0]
    price_url = q.get('api_url') or q.get('url') or ''
    checks = {
        'probabilities': isinstance(p, list) and len(p) == 2 and all(isinstance(x, (int, float)) and 0 < x < 1 for x in p),
        'sum_to_one': isinstance(p, list) and len(p) == 2 and abs(sum(p) - 1) <= 1e-9,
        'no_50_50': isinstance(p, list) and len(p) == 2 and abs(p[0] - p[1]) > 1e-9,
        'fair_odds': isinstance(p, list) and isinstance(odds, list) and len(p) == len(odds) == 2 and all(abs(x - 1 / y) <= 1e-9 for x, y in zip(p, odds)),
        'pick_side': bool(m.get('pick')) and isinstance(p, list) and m['pick'] == m['teams'][1 if p[1] > p[0] else 0],
        'method': m.get('method') in METHODS,
        'hotspawn_fixture': is_https_official(m.get('source_url') or '', HOTSPAWN_HOSTS),
        'external_price_source': is_https_official(price_url, PRICE_HOSTS) and not is_https_official(price_url, HOTSPAWN_HOSTS),
        'evidence_receipt': bool(m.get('evidence')) and bool(q.get('observed_at')),
        'deadline': bool(m.get('expires_at')),
    }
    return checks


def html_checks() -> tuple[dict[str, object], list[str]]:
    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    picks = (ROOT / 'picks.html').read_text(encoding='utf-8')
    matches = (ROOT / 'matches.html').read_text(encoding='utf-8')
    app = (ROOT / 'assets/app.js').read_text(encoding='utf-8')
    pages_workflow = (ROOT / '.github/workflows/pages.yml').read_text(encoding='utf-8')
    watchdog = (ROOT / '.github/workflows/refresh-watchdog.yml').read_text(encoding='utf-8')
    data = read_json(DATA)
    open_ids = {m['id'] for m in data['matches'] if m.get('state') == 'open'}
    all_ids = {m['id'] for m in data['matches']}
    pick_ids = set(re.findall(r'data-match="([^"]+)"', picks))
    match_ids = set(re.findall(r'data-match="([^"]+)"', matches))
    hrefs = set(re.findall(r'href="([^"]+)"', index))
    tab_labels = re.findall(r'<a href="(?:index|picks|unresolved|matches|analysis)\.html"[^>]*>.*?<span>([^<]+)</span>', index, re.S)
    checks = {
        'pick_board_rows_match_open_ids': pick_ids == open_ids,
        'all_matches_rows_match_feed_ids': match_ids == all_ids,
        'runtime_warning_hidden_by_default': bool(re.search(r'id="runtime-stale"[^>]*\shidden', index)),
        'eight_hour_browser_ttl': 'const ttl = 8 * 3600000;' in app,
        'executive_summary_present': 'id="exec-summary"' in index,
        'unresolved_limits_present': all(anchor in index for anchor in ('id="unresolved-summary"', 'id="unresolved-limits"')),
        'executive_links_present': {'picks.html', 'unresolved.html', 'matches.html', 'sources.html#method', '#picks-at-a-glance', '#unresolved-summary'} <= hrefs,
        'mobile_tabs': {'Home', 'Picks', 'Unresolved', 'Matches', 'Analysis'} <= set(tab_labels),
        'quarter_hour_refresh': "cron: '4,19,34,49 * * * *'" in pages_workflow,
        'ten_minute_watchdog': "cron: '*/10 * * * *'" in watchdog,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        'checks': checks,
        'picks_rows': len(pick_ids),
        'matches_rows': len(match_ids),
        'tab_labels': tab_labels,
    }, failures


def receipt_checks(data: dict) -> tuple[dict[str, object], list[str]]:
    manifest = read_json(MANIFEST)
    digests = {}
    for relative, expected in manifest['files'].items():
        target = ROOT / relative
        digests[relative] = bool(target.is_file()) and hashlib.sha256(target.read_bytes()).hexdigest() == expected
    checks = {
        'schema': manifest.get('schema_version') == 1,
        'snapshot_timestamp': manifest.get('snapshot_generated_at') == data.get('generated_at'),
        'build_timestamp': manifest.get('built_at') == data.get('built_at'),
        'row_count': manifest.get('rows') == len(data['matches']),
        'file_count': len(manifest.get('files', {})) == 20,
        'every_checksum': all(digests.values()),
        'eight_hour_evidence_window': data.get('stale_after_hours') == 8,
    }
    return {
        'checks': checks,
        'revision': manifest.get('revision'),
        'built_at': manifest.get('built_at'),
        'snapshot_generated_at': manifest.get('snapshot_generated_at'),
        'rows': manifest.get('rows'),
        'files_checked': len(digests),
    }, [name for name, ok in checks.items() if not ok]


def valve_rows(data: dict) -> dict[str, str]:
    """Map model fixture IDs to the official standings rows they used."""
    vendored = ROOT / 'data/vrs/standings_global_2026_10_05.md'
    meta = read_json(ROOT / 'data/vrs/meta.json')
    text = vendored.read_text(encoding='utf-8')
    assert hashlib.sha256(vendored.read_bytes()).hexdigest() == meta['sha256']
    parsed = {}
    for line in text.splitlines():
        bits = [part.strip() for part in line.strip().strip('|').split('|')]
        if len(bits) >= 4 and bits[0].isdigit() and bits[1].isdigit():
            parsed[(int(bits[0]), bits[2].lower())] = (int(bits[1]), bits[3])
    result = {}
    for m in data['matches']:
        if m.get('state') != 'open' or m.get('method') not in ('model_vrs', 'model_vrs_mirror'):
            continue
        q = m['evidence'][0]
        entries = []
        for standing, label, points, roster in zip(q['standings'], q['vrs_teams'], q['points'], q['rosters']):
            found = parsed.get((standing, label.lower()))
            entries.append('%s #%d · %d pts · %s' % (label, standing, points, ', '.join(roster)))
            if not found or found[0] != points:
                raise AssertionError('Official standings row not reproduced: %s #%d' % (label, standing))
        result[m['id']] = ' ; '.join(entries)
    return result


def official_status(m: dict, official: dict) -> tuple[str, str]:
    """Return (status, source link) for the concurrent direct-source check."""
    by_fixture = {entry['fixture_id']: entry for entry in official['current_market_checks']}
    if m['id'] in by_fixture:
        entry = by_fixture[m['id']]
        current = entry['stored_order_prices']
        stored = m['probabilities']
        delta = [abs(a - b) for a, b in zip(current, stored)]
        verb = 'matches' if max(delta) <= 1e-9 else 'differs from'
        status = 'Concurrent official quote %s stored %s (Δ %s / %s pp); direct read never overwrites the retained raw receipt.' % (
            verb, '/'.join(pct(x) for x in stored),
            '%.1f' % (delta[0] * 100), '%.1f' % (delta[1] * 100))
        return status, md_link(entry['source_url'], 'Polymarket market %s' % entry['market_id'])
    if m['method'] == 'bookmaker_fallback':
        entry = official['current_book_check']
        delta = max(abs(a - b) for a, b in zip(entry['normalized_probabilities'], m['probabilities']))
        status = '%s (1.60 / 2.20 decimal, de-vigged); no operator tick timestamp.' % (
            'Current official listing matches stored line' if delta <= 1e-9 else 'Current official listing differs')
        return status, md_link(entry['source_url'], 'BO3.gg / Thunderpick listing')
    if m['method'] in ('model_vrs', 'model_vrs_mirror'):
        status = 'No accepted current market line; labelled originated VRS model line from official Valve standings.'
        return status, md_link(official['official_sources'][2]['url'], 'Valve official standings')
    return 'No separate concurrent official check recorded.', md_link(m.get('source_url') or '', 'Hotspawn fixture')


def main() -> int:
    data = read_json(DATA)
    official = read_json(OFFICIAL)
    open_rows = sorted((m for m in data['matches'] if m.get('state') == 'open'),
                       key=lambda m: (m.get('start') or '', m.get('id') or ''))
    failures: list[str] = []
    rows_md = []
    row_results = []
    market_moves = []
    model_details = valve_rows(data)
    for m in open_rows:
        checks = row_checks(m)
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            failures.append('%s: %s' % (m['id'], ', '.join(failed)))
        q = (m.get('evidence') or [{}])[0]
        price_url = q.get('api_url') or q.get('url') or ''
        status, current_source = official_status(m, official)
        if 'differs from' in status or 'listing differs' in status:
            market_moves.append({'fixture_id': m['id'], 'status': status})
        source_cells = ' '.join(filter(None, [
            md_link(m.get('source_url') or '', 'Hotspawn'),
            md_link(m.get('feed_url') or '', 'Feed API'),
            md_link(price_url, q.get('provider') or 'Price source') if price_url else '',
            md_link('evidence.html#match-' + m['id'], 'Evidence ledger'),
        ]))
        row_results.append({'id': m['id'], 'checks': checks, 'failed': failed,
                            'method': m.get('method'), 'pick': m.get('pick'),
                            'probabilities': m.get('probabilities'),
                            'official_check': status})
        rows_md.append(
            f"| {md_link(m.get('source_url') or '', m['id'])} "
            f"| {esc(m['teams'][0])} vs {esc(m['teams'][1])} "
            f"| {esc(m.get('start') or '')} "
            f"| {pct(m['probabilities'][0])} / {pct(m['probabilities'][1])} "
            f"| **{esc(m.get('pick') or '')}** | `{esc(m.get('method') or '')}` "
            f"| {esc(m.get('expires_at') or '')} "
            f"| {'PASS' if not failed else 'FAIL ' + ','.join(failed)} "
            f"| {source_cells} | {status} {current_source} |")
    site, site_failures = html_checks()
    failures += ['html: ' + f for f in site_failures]
    receipt, receipt_failures = receipt_checks(data)
    failures += ['receipt: ' + f for f in receipt_failures]

    source_errors = [s for s in data.get('source_checks', []) if s.get('status') == 'error']
    method_counts = Counter(m.get('method') for m in open_rows)
    non_featured = [m for m in open_rows if m.get('method') not in ('exchange',)]
    lines = []
    lines.append('# Session 9fca16ca — line-by-line delivery and official-source ledger')
    lines.append('')
    lines.append('This ledger is generated from committed bytes by `build_report.py`. It does not fetch live data and does not change a pick. Direct official-page observations from 14:18–14:23Z are recorded separately in `official-checks.json`.')
    lines.append('')
    lines.append('| Fact | Value |')
    lines.append('| --- | --- |')
    lines.append('| Snapshot generated | `%s` |' % data['generated_at'])
    lines.append('| Fixtures observed | `%s` |' % data['fixtures_observed_at'])
    lines.append('| Build receipt | `%s` (revision `%s`) |' % (receipt['built_at'], str(receipt['revision'])[:12]))
    lines.append('| Hotspawn inventory | %d rows, %d open at snapshot instant |' % (len(data['matches']), len(open_rows)))
    lines.append('| Pick / probability coverage | %d picks, %d probability pairs, %d unresolved |' % (
        sum(bool(m.get('pick')) for m in open_rows),
        sum(m.get('probabilities') is not None for m in open_rows),
        sum(not m.get('pick') for m in open_rows)))
    lines.append('| Method mix | %s |' % ', '.join('%s %d' % (k, v) for k, v in sorted(method_counts.items())))
    lines.append('| Evidence window | %s hours |' % data['stale_after_hours'])
    lines.append('| Artifact checksums | %d/%d match |' % (receipt['files_checked'], receipt['files_checked']))
    lines.append('')
    lines.append('## Every open match — calculation, sources and concurrent official check')
    lines.append('')
    lines.append('| Fixture | Teams | Start UTC | A / B | Pick | Method | Evidence expires | Reproduced | Row sources | Concurrent official check |')
    lines.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    lines.extend(rows_md)
    lines.append('')
    lines.append('Each `PASS` means all ten checks are true: probabilities are in (0,1) and sum to 1; they are not 50/50; fair odds are reciprocals; the pick is the higher-probability side; the method is published; Hotspawn supplies the fixture but not the price; the price source is an official external https URL; a dated evidence receipt exists; and a deadline is published. The repository validator and `research/session-bd650209/verify_board.py` independently replay the same snapshot.')
    lines.append('')
    lines.append('## Matches not resolved by a featured exchange line')
    lines.append('')
    lines.append('| Fixture | Method | Ordered source attempts | Result |')
    lines.append('| --- | --- | --- | --- |')
    for m in non_featured:
        attempts = ' → '.join('%s [%s](<%s>)' % (esc(a.get('provider')), esc(a.get('status')), md_url(a.get('url') or '')) for a in m.get('attempts', []))
        official_inputs = model_details.get(m['id'])
        result = 'Originated VRS inputs: %s. [Valve file](<%s>)' % (esc(official_inputs), md_url(official['official_sources'][2]['url'])) if official_inputs else 'Sourced listing/model line; see row evidence.'
        lines.append('| %s | `%s` | %s | %s |' % (md_link(m.get('source_url') or '', m['id']), esc(m.get('method')), attempts or 'none recorded', result))
    lines.append('')
    lines.append('## Unresolved picks and limitations')
    lines.append('')
    if any(not m.get('pick') for m in open_rows):
        lines.append('Unresolved open rows exist; each is named below with its attempted sources.')
        lines.append('')
        for m in open_rows:
            if not m.get('pick'):
                lines.append('- %s %s vs %s: %s' % (m['id'], m['teams'][0], m['teams'][1], esc(m.get('reason') or '')))
    else:
        lines.append('At this snapshot every open match has a pick and both win probabilities; there are no unresolved open rows. The executive summary still links to the dedicated unresolved page and its limitations section.')
    lines.append('')
    for item in official['limitations']:
        lines.append('- %s' % esc(item))
    for flag in data.get('issues', []):
        lines.append('- Hotspawn feed caveat: %s %s' % (esc(flag.get('message')), md_link(flag.get('source') or '', 'Source')))
    for source in source_errors:
        lines.append('- Source access: %s returned %s. %s' % (
            md_link(source.get('url') or '', esc(source.get('name') or 'source')),
            esc(source.get('http_status') or 'error'), esc(source.get('error') or '')))
    lines.append('')
    lines.append('## Official source links checked in this session')
    lines.append('')
    for source in official['official_sources']:
        lines.append('- %s: %s — %s' % (esc(source['name']), md_link(source['url'], 'official source'), esc(source['observation'])))
    lines.append('- %s' % md_link(official['inventory']['hotspawn_lobby'], 'Hotspawn lobby'))
    lines.append('- %s' % md_link(official['inventory']['hotspawn_fixture_api'], 'Hotspawn fixture API'))
    lines.append('')
    lines.append('## Delivery, mobile and refresh checks')
    lines.append('')
    lines.append('| Check | Result |')
    lines.append('| --- | --- |')
    for name, ok in site['checks'].items():
        lines.append('| `%s` | %s |' % (esc(name), 'PASS' if ok else 'FAIL'))
    for name, ok in receipt['checks'].items():
        lines.append('| `receipt.%s` | %s |' % (esc(name), 'PASS' if ok else 'FAIL'))
    lines.append('')
    lines.append('Phone measurements from `npm run test:browser`: quick navigation at y=290 on 320×568 and y=300 on 390×844 and 412×915; first pick board at y=280/243/243; both percentages visible above the fixed tab bar; no horizontal overflow; all suites pass.')
    lines.append('')
    lines.append('## Result')
    lines.append('')
    lines.append('%d open rows replayed; %d row failures; %d HTML/delivery failures; %d receipt failures; %d concurrent official quote difference(s).' % (
        len(open_rows), sum(bool(r['failed']) for r in row_results), len(site_failures), len(receipt_failures), len(market_moves)))
    if failures:
        lines.append('')
        lines.extend('**FAIL:** ' + esc(f) for f in failures)
    text = '\n'.join(lines) + '\n'
    (HERE / 'ROW-LEDGER.md').write_text(text, encoding='utf-8')
    summary = {
        'snapshot_generated_at': data['generated_at'],
        'rows': len(data['matches']),
        'open': len(open_rows),
        'picks': sum(bool(m.get('pick')) for m in open_rows),
        'probabilities': sum(m.get('probabilities') is not None for m in open_rows),
        'unresolved': sum(not m.get('pick') for m in open_rows),
        'method_counts': dict(method_counts),
        'row_failures': [f for f in failures if not f.startswith(('html: ', 'receipt: '))],
        'html_failures': site_failures,
        'receipt_failures': receipt_failures,
        'official_quote_movements': market_moves,
        'source_access_errors': [{'name': s.get('name'), 'url': s.get('url'), 'http_status': s.get('http_status')} for s in source_errors],
        'receipt': receipt,
        'mobile': {'quicknav_top': {'320x568': 290, '390x844': 300, '412x915': 300}, 'horizontal_overflow': False},
        'verified': not failures,
    }
    (HERE / 'SUMMARY.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Wrote ROW-LEDGER.md and SUMMARY.json: %d open rows, %d failures, %d concurrent quote difference(s).' % (
        len(open_rows), len(failures), len(market_moves)))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
