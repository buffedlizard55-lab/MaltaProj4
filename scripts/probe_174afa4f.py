"""Session 174afa4f: fallback-source probe for rows the featured tiers miss.

Diagnostic only. It runs on the fresh snapshot the harvest just collected and
asks, for exactly the open matches that the strict exchange / sharp-book
tiers did *not* price (no pick, no percentage, or only a documented lower
tier), what the next sources in the users order can still offer:

1. HLTV first -- the public ranking list (does polling it add anything over
   the exact team pages the collector already reads?) and, for a few gap
   rows, the fixture page's bookmaker table (does the serveable HTML carry
   a machine-readable two-way *number* at all?).
2. Esportsbooks / esports betting lines -- a Pinnacle near-miss diagnostic
   (exact pair, wrong start, or missing entirely: distinguishes "not
   offered" from "offered under another start/label" without inventing
   aliases), the BO3 pagination ceiling (did fetch() see every upcoming
   page?), an EGamersWorld *listing* discovery scan for exact bound lines,
   and access probes for Kalshi's public markets API and OddsPortal.

Nothing here is ever a price input: every finding is a dated, hashed
observation for the integration step to judge. Hotspawn is not read for
probabilities (only the already-collected snapshot is), no alias is
guessed, no 50/50 default exists, and every endpoint failure is recorded
instead of raised. Exit code is always 0 unless the snapshot is unreadable.

Usage:
    python -m scripts.probe_174afa4f --snapshot runtime/latest.json \
        --output research/harvest-174afa4f
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from scripts import bo3 as bo3_module
from scripts import books as books_module
from scripts import core
from scripts import refresh as refresh_module

HLTV_RANKING_URL = 'https://www.hltv.org/ranking/teams'
HLTV_FIXTURE_SCAN_LIMIT = 6
EGW_LISTING_URL = 'https://egamersworld.com/counterstrike/matches'
KALSHI_MARKETS_URL = 'https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=200'
ODDSPORTAL_URL = 'https://www.oddsportal.com/esports/counter-strike/'
FEATURED = {'exchange', 'bookmaker'}


def _record(view):
    return {key: view.get(key) for key in
            ('name', 'url', 'request_url', 'http_status', 'observed_at',
             'content_type', 'sha256', 'bytes', 'status', 'error',
             'rate_limit_waits', 'json_body_retries', 'tls_fallback')}


def fetch(src, name, url, as_json=True, headers=None):
    """One probe read. Returns (body|None, endpoint-record); never raises."""
    try:
        body, view = src.get(name, url, as_json=as_json, headers=headers)
        return body, _record(view)
    except Exception as exc:  # probe evidence, not a pipeline failure
        view = dict(src.log[-1]) if src.log else {}
        view.setdefault('status', 'error')
        view.setdefault('error', str(exc))
        return None, _record(view)


def targets(snapshot):
    """Open rows not priced by the featured tiers, grouped by what's missing."""
    out = []
    for match in snapshot.get('matches') or []:
        if match.get('state') != 'open':
            continue
        if match.get('pick') is None:
            kind = 'no pick and no %'
        elif match.get('probabilities') is None:
            kind = 'pick without % (research/model-single tier)'
        elif match.get('method') not in FEATURED:
            kind = 'priced by a lower tier (%s)' % match.get('method')
        else:
            continue
        out.append({'id': str(match.get('id')), 'teams': match.get('teams'),
                    'start': match.get('start'), 'method': match.get('method'),
                    'kind': kind, 'reason': match.get('reason'),
                    'attempts': [{'provider': a.get('provider'), 'status': a.get('status'),
                                  'url': a.get('url')} for a in match.get('attempts') or []
                                 if isinstance(a, dict)]})
    return out


def label_present(text_norm, label):
    return bool(label) and core.norm(label) in text_norm


def probe_hltv_ranking(src, rows):
    body, record = fetch(src, 'HLTV ranking list (probe)', HLTV_RANKING_URL, as_json=False)
    result = {'endpoint': record, 'teams': []}
    if body is None:
        return result
    text_norm = core.norm(re.sub(r'<[^>]+>', ' ', body))
    seen = set()
    for row in rows:
        for label in row['teams'] or []:
            if label in seen:
                continue
            seen.add(label)
            result['teams'].append({'team': label, 'label_on_ranking_page': label_present(text_norm, label)})
    return result


def _hltv_fixture_url(row, snapshot_by_id):
    match = snapshot_by_id.get(row['id']) or {}
    views = (match.get('hltv_context') or {}).get('views') or {}
    url = views.get('url') or (match.get('hltv_context') or {}).get('url')
    if url:
        return url
    for attempt in match.get('attempts') or []:
        if isinstance(attempt, dict) and 'hltv.org/matches/' in str(attempt.get('url') or ''):
            return attempt['url']
    return None


def probe_hltv_fixture_odds_tables(src, rows, snapshot_by_id):
    """Does the serveable fixture HTML carry any two-way numeric odds pair?

    Reports structure only (bookmaker markers, decimal-token counts); even a
    found number is not consumed as a line -- accepting one needs a parser,
    pairing proof and tests first.
    """
    out = []
    decimal_re = re.compile(r'(?<![\d.])[1-9]\d?\.\d{2,3}(?![\d])')
    for row in rows:
        if row['kind'] == 'pick without % (research/model-single tier)':
            pass
        url = _hltv_fixture_url(row, snapshot_by_id)
        if not url or len(out) >= HLTV_FIXTURE_SCAN_LIMIT:
            continue
        body, record = fetch(src, 'HLTV fixture page odds-table scan (probe)', url, as_json=False)
        entry = {'id': row['id'], 'teams': row['teams'], 'endpoint': record}
        if body is not None:
            lowered = body.lower()
            entry['markers'] = {token: (token in lowered) for token in
                                ('betting', 'bookmaker', 'odds', 'ggbet', 'thunderpick', 'bet365')}
            entry['decimal_token_count'] = len(decimal_re.findall(body))
            entry['verdict'] = ('structure scan only; no pair is bound to team labels by this probe, '
                                'so no number on the page is accepted as a line')
        out.append(entry)
    return out


def probe_pinnacle_near_miss(src, rows):
    matchups, mr = fetch(src, 'Pinnacle esports fixtures (probe)', core.PIN + '/sports/12/matchups?withSpecials=false')
    lines, lr = fetch(src, 'Pinnacle esports moneylines (probe)', core.PIN + '/sports/12/markets/straight')
    result = {'endpoints': [mr, lr], 'cs2_matchups': 0, 'findings': []}
    if matchups is None or lines is None:
        return result
    observed = min(mr.get('observed_at') or '', lr.get('observed_at') or '')
    try:
        candidates = core.pinnacle_candidates(matchups, lines, observed)
    except ValueError as exc:
        result['error'] = str(exc)
        return result
    result['cs2_matchups'] = len({c['id'] for c in candidates})
    from scripts import core as _c
    for row in rows:
        fixture = {'teams': row['teams'], 'start': row['start']}
        finding = {'id': row['id'], 'teams': row['teams'], 'start': row['start'],
                   'exact': 0, 'same_pair_other_start': [], 'one_team_same_start': []}
        for cand in candidates:
            order = _c.orientation(fixture, cand.get('teams') or [], cand.get('start'))
            if order:
                finding['exact'] += 1
                continue
            pair = {core.norm(t) for t in cand.get('teams') or []}
            wanted = {core.norm(t) for t in row['teams'] or []}
            if pair == wanted and core.dt(cand.get('start')) != core.dt(row['start']):
                finding['same_pair_other_start'].append(
                    {'teams': cand['teams'], 'start': cand['start'], 'pinnacle_id': cand['id']})
            elif pair & wanted and core.dt(cand.get('start')) == core.dt(row['start']):
                finding['one_team_same_start'].append(
                    {'teams': cand['teams'], 'start': cand['start'], 'pinnacle_id': cand['id']})
        result['findings'].append(finding)
    return result


def probe_bo3_pagination(src):
    body, record = fetch(src, 'BO3 upcoming CS2 page 1 (probe)', bo3_module.page_url(0),
                         headers={'Referer': 'https://bo3.gg/'})
    result = {'endpoint': record, 'page_limit': bo3_module.PAGE_LIMIT}
    if isinstance(body, dict):
        items = body.get('results') or body.get('data') or body.get('matches') or []
        result['first_page_items'] = len(items) if isinstance(items, list) else None
        for key in ('total', 'count', 'total_count', 'meta', 'pagination', 'links'):
            if key in body:
                result[key] = body[key] if not isinstance(body[key], (dict, list)) else json.dumps(body[key])[:500]
        result['payload_keys'] = sorted(body.keys())
    return result


def probe_egw_listing(src, rows):
    body, record = fetch(src, 'EGamersWorld CS2 matches listing (probe)', EGW_LISTING_URL, as_json=False)
    result = {'endpoint': record, 'readings_total': 0, 'exact_bound': []}
    if body is None:
        return result
    readings = books_module.parse_listing(body)
    result['readings_total'] = len(readings)
    for row in rows:
        fixture = {'teams': row['teams'], 'start': row['start']}
        for reading in readings:
            order = core.orientation(fixture, [reading.get('team1'), reading.get('team2')],
                                     reading.get('start'))
            if not order:
                continue
            odds = books_module.listing_odds(reading)
            result['exact_bound'].append({
                'id': row['id'], 'teams': row['teams'],
                'listing': {'team1': reading.get('team1'), 'team2': reading.get('team2'),
                            'start': reading.get('start'), 'odds': odds,
                            'bound_to_labels': reading.get('bound_to_labels')},
                'verdict': ('exact listing reading; it becomes a priced row only through the '
                            'reviewed book-receipts path with this dated observation attached')})
    return result


def probe_access_and_labels(src, name, url, rows, as_json):
    body, record = fetch(src, name, url, as_json=as_json)
    result = {'endpoint': record, 'labels_present': []}
    if body is None:
        return result
    text = json.dumps(body) if not isinstance(body, str) else re.sub(r'<[^>]+>', ' ', body)
    text_norm = core.norm(text)
    seen = set()
    for row in rows:
        for label in row['teams'] or []:
            if label not in seen and label_present(text_norm, label):
                seen.add(label)
                result['labels_present'].append(label)
    result['note'] = ('label presence is a discovery signal only; it never pairs teams, '
                      'starts or prices, and cannot become a line by itself')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    snapshot = json.loads(args.snapshot.read_bytes())
    snapshot_by_id = {str(m.get('id')): m for m in snapshot.get('matches') or []}
    rows = targets(snapshot)
    now = datetime.now(timezone.utc)
    src = refresh_module.Sources(now)
    report = {
        'schema_version': 1,
        'session': '174afa4f',
        'probed_at': refresh_module.iso(now),
        'snapshot_generated_at': snapshot.get('generated_at'),
        'statement': ('Diagnostic only: no value recorded here is a price input. Hotspawn was '
                      'not read for probabilities; no alias was guessed; nothing defaults to 50/50.'),
        'targets': rows,
        'hltv_ranking_list': probe_hltv_ranking(src, rows),
        'hltv_fixture_odds_tables': probe_hltv_fixture_odds_tables(src, rows, snapshot_by_id),
        'pinnacle_near_miss': probe_pinnacle_near_miss(src, rows),
        'bo3_pagination': probe_bo3_pagination(src),
        'egw_listing_discovery': probe_egw_listing(src, rows),
        'kalshi_access': probe_access_and_labels(src, 'Kalshi public markets API (probe)',
                                                 KALSHI_MARKETS_URL, rows, as_json=True),
        'oddsportal_access': probe_access_and_labels(src, 'OddsPortal CS2 page (probe)',
                                                     ODDSPORTAL_URL, rows, as_json=False),
        'source_log': [_record(entry) for entry in src.log],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'probe.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')

    def status(section):
        record = section.get('endpoint') or {}
        if record.get('status') == 'ok':
            return f"read at `{record.get('observed_at')}` ({record.get('bytes')} bytes, sha `{str(record.get('sha256'))[:12]}…`)"
        return f"not read: {record.get('error')}"

    lines = [
        '# Session 174afa4f — fallback-source probe (diagnostic only)',
        '',
        report['statement'],
        '',
        f"- Probed at `{report['probed_at']}` against snapshot `{report['snapshot_generated_at']}`.",
        f"- Targets (open rows the featured exchange/Pinnacle tiers did not price): **{len(rows)}**",
        '',
        '| ID | Match | Start (UTC) | Current state |',
        '| --- | --- | --- | --- |',
    ]
    for row in rows:
        lines.append(f"| {row['id']} | {' vs '.join(row['teams'] or [])} | {row['start']} | {row['kind']} |")
    lines += [
        '', '## HLTV first', '',
        f"- Ranking list ([official]({HLTV_RANKING_URL})): {status(report['hltv_ranking_list'])}; "
        f"labels present: `{[t['team'] for t in report['hltv_ranking_list']['teams'] if t['label_on_ranking_page']] or 'none'}`. "
        'The collector already reads each exact team page for gap rows; this only measures '
        'whether polling the list would add teams.',
    ]
    for entry in report['hltv_fixture_odds_tables']:
        lines.append(f"- Fixture odds-table scan `{entry['id']}` {' vs '.join(entry['teams'] or [])}: "
                     f"{status(entry)}; markers `{entry.get('markers')}`; "
                     f"decimal tokens `{entry.get('decimal_token_count')}` — {entry.get('verdict', '')}.")
    if not report['hltv_fixture_odds_tables']:
        lines.append('- Fixture odds-table scan: no gap row carried an HLTV fixture-page URL to scan.')
    lines += ['', '## Esportsbooks and esports betting lines', '']
    pin = report['pinnacle_near_miss']
    lines.append(f"- Pinnacle near-miss diagnostic: CS2 matchup candidates `{pin['cs2_matchups']}`; "
                 + '; '.join(f"`{f['id']}` exact={f['exact']} same-pair/other-start={len(f['same_pair_other_start'])} "
                             f"one-team/same-start={len(f['one_team_same_start'])}" for f in pin['findings'] or [])
                 + ('' if pin['findings'] else 'no targets'))
    bo3 = report['bo3_pagination']
    lines.append(f"- BO3 pagination: {status(bo3)}; first-page items `{bo3.get('first_page_items')}` "
                 f"of page limit `{bo3.get('page_limit')}`; payload keys `{bo3.get('payload_keys')}`; "
                 f"total field `{bo3.get('total') or bo3.get('count') or bo3.get('total_count') or 'none published'}`.")
    egw = report['egw_listing_discovery']
    lines.append(f"- EGamersWorld listing discovery ([official]({EGW_LISTING_URL})): {status(egw)}; "
                 f"readings parsed `{egw['readings_total']}`; exact bound readings for targets: `{len(egw['exact_bound'])}`.")
    for hit in egw['exact_bound']:
        lines.append(f"  - `{hit['id']}` {' vs '.join(hit['teams'] or [])}: listing {hit['listing']} — {hit['verdict']}.")
    kal = report['kalshi_access']
    lines.append(f"- Kalshi public markets API ([official]({KALSHI_MARKETS_URL})): {status(kal)}; "
                 f"target labels present `{kal['labels_present'] or 'none'}`.")
    odd = report['oddsportal_access']
    lines.append(f"- OddsPortal ([official]({ODDSPORTAL_URL})): {status(odd)}; "
                 f"target labels present `{odd['labels_present'] or 'none'}`.")
    lines += ['', 'Full hashed endpoint records are in `probe.json`. No price from this probe '
              'was applied to any pick or percentage.']
    (args.output / 'PROBE.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'targets': len(rows),
                      'egw_exact_bound': len(egw['exact_bound']),
                      'pinnacle_cs2_matchups': pin['cs2_matchups']}, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
