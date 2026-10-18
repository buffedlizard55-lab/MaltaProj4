"""Day-5 live-evidence probe for session f659a6e2 (research only, never publishes).

Why this exists
---------------
The authoring sandbox reaches GitHub and package registries only, so every line
quoted in this session's final-day analysis has to be *retrieved*, not recalled.
This script runs on a GitHub Actions runner with normal outbound access and
writes the raw, dated evidence into ``research/harvest-f659a6e2/`` so each number
published for Sunday 18 October 2026 can be re-checked line by line against the
response it came from.

What makes this session different from the earlier day-5 work
------------------------------------------------------------
Sessions cc88483d / e0fd5a32 / f4e34907 closed on 17 October with **no exchange
line** for either Sunday fixture: Pinnacle did not list the event, Polymarket had
no head-to-head market at 20:20-20:22Z, and the only two-way prices were single
Thunderpick document reads whose quote blocks expire 2026-10-18T04:20:54Z.
Polymarket created both day-5 events at 20:55Z on 17 October
(``cs2-aur1-fal2-2026-10-18`` id 1207556 and ``cs2-furia-bb3-2026-10-18`` id
1207558), i.e. *after* those sessions captured their evidence. This probe
therefore re-reads the operator directly and records the whole-match moneyline
gate fields (``sportsMarketType``, outcomes, prices, bid/ask, spread, liquidity,
``acceptingOrders``, ``gameStartTime``, ``updatedAt``) instead of relying on a
book's rendered page.

What it does
------------
1. Summarises the open rows of the snapshot produced by ``scripts.refresh``.
2. Reads the two day-5 Polymarket events and their whole-match moneyline markets
   by slug, with every field the acceptance gate in ``scripts.core`` inspects.
3. Runs the full active CS2 event scan (same pagination as production) so any
   *other* new day-5 market is captured too, not just the two expected slugs.
4. Reads Pinnacle's public esports fixtures/moneylines filtered to the team names
   on our open rows plus the TWC 2026 participants.
5. Reads HLTV: the Thunderpick World Championship results page (days 1-4 series
   re-verification), the event schedule, both Sunday match pages, and the match
   page of every open row that still has no percentage.
6. Probes the named esportsbooks, including the two Thunderpick day-5 market
   pages the earlier sessions read by hand, and records HTTP status plus any
   server-side decimal odds rather than guessing.
7. Writes a compact digest (JSON + Markdown) of the day-5 findings.

Every step is individually guarded: a source that refuses access is recorded as a
limitation with its status code, never silently skipped and never presented as
"no odds available". Nothing here writes a probability by hand.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from scripts.core import FIXTURES, GAMMA, PIN, dt, iso, norm
from scripts.refresh import Sources
from scripts.probe_621776e4 import (compact_ledger, embedded_line_hunt, hltv_event_matches,
                                    hltv_match, hltv_results, hltv_upcoming, now_iso,
                                    trim_pinnacle, trim_polymarket)

TWC_EVENT = 8932
# Both Sunday fixtures, identified on HLTV by sessions cc88483d/e0fd5a32 on 17 October:
# 2399416 Aurora-Falcons (third place, 11:30Z) and 2399417 FURIA-BETBOOM (final, 15:00Z).
DAY5_HLTV_IDS = ('2399416', '2399417')
# Polymarket slugs discovered from the operator's own public search endpoint on
# 2026-10-18 (event ids 1207556 and 1207558, both created 2026-10-17T20:55Z).
DAY5_MARKET_SLUGS = ('cs2-aur1-fal2-2026-10-18', 'cs2-furia-bb3-2026-10-18')
DAY5_EVENT_IDS = ('1207556', '1207558')
# Slug -> HLTV match id. The identity pairing is not inferred here: it is the
# mapping sessions cc88483d/e0fd5a32 recorded on 17 October from the HLTV match
# pages themselves (2399416 Aurora vs Falcons 11:30Z, 2399417 FURIA vs BETBOOM
# 15:00Z), and this probe re-reads both pages and both markets and re-checks that
# the operator's own `gameStartTime` equals the HLTV `data-unix` clock before the
# digest calls them the same fixture.
DAY5_SLUG_TO_HLTV = {'cs2-aur1-fal2-2026-10-18': '2399416',
                     'cs2-furia-bb3-2026-10-18': '2399417'}
# The exact pages the earlier sessions read by document retrieval; re-observed here
# so the record says what the book answered *this* run, not what it answered at 20:20Z.
BOOK_PROBES = (
    ('Thunderpick third-place market page',
     'https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/aurora-vs-falcons/2843582'),
    ('Thunderpick grand-final market page',
     'https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/furia-vs-bb-team/2843592'),
    ('Thunderpick CS2 page', 'https://thunderpick.io/esports/cs2-betting'),
    ('GG.BET CS2 page', 'https://gg.bet/en/esports/counter-strike'),
    ('Rivalry CS2 page', 'https://www.rivalry.com/esports/counter-strike'),
    ('EGamersWorld CS2 matches', 'https://egamersworld.com/counterstrike/matches'),
    ('Pinnacle esports page', 'https://www.pinnacle.com/en/esports'),
)
# Market fields the acceptance gate inspects; captured verbatim so the gate can be
# replayed offline against this receipt.
MARKET_FIELDS = ('id', 'question', 'slug', 'sportsMarketType', 'groupItemTitle', 'outcomes',
                 'outcomePrices', 'bestBid', 'bestAsk', 'lastTradePrice', 'spread', 'liquidity',
                 'liquidityNum', 'volume', 'volumeNum', 'active', 'closed', 'archived',
                 'acceptingOrders', 'gameStartTime', 'eventStartTime', 'startDate', 'endDate',
                 'updatedAt', 'createdAt', 'conditionId', 'enableOrderBook', 'orderPriceMinTickSize')
EVENT_FIELDS = ('id', 'slug', 'ticker', 'title', 'active', 'closed', 'archived', 'live', 'ended',
                'liquidity', 'volume', 'openInterest', 'startDate', 'endDate', 'createdAt',
                'updatedAt', 'startTime', 'eventDate', 'score', 'period', 'seriesSlug',
                'eventMetadata', 'teams')


def trim_market(market):
    """One market as the gate sees it, with a resolvable API URL."""
    out = {key: market.get(key) for key in MARKET_FIELDS}
    out['api_url'] = GAMMA + '/markets/' + str(market.get('id'))
    for key in ('outcomes', 'outcomePrices'):
        value = out.get(key)
        if isinstance(value, str):
            try:
                out[key + '_parsed'] = json.loads(value)
            except ValueError:
                out[key + '_parsed'] = None
    prices = out.get('outcomePrices_parsed')
    if isinstance(prices, list) and len(prices) == 2:
        try:
            floats = [float(p) for p in prices]
        except (TypeError, ValueError):
            floats = None
        if floats and all(p > 0 for p in floats):
            total = sum(floats)
            out['normalized'] = [p / total for p in floats]
            out['fair_decimal'] = [total / p for p in floats]
            out['price_sum'] = total
    return out


def gamma_market_by_slug(src, slug):
    url = GAMMA + '/markets?' + urlencode({'slug': slug})
    batch, receipt = src.get('Polymarket market slug %s' % slug, url)
    if not isinstance(batch, list):
        raise ValueError('Unexpected Polymarket market schema for slug %s' % slug)
    return {'slug': slug, 'url': url, 'receipt': receipt, 'count': len(batch),
            'markets': [trim_market(m) for m in batch if isinstance(m, dict)]}


def gamma_event(src, event_id):
    url = GAMMA + '/events/' + str(event_id)
    event, receipt = src.get('Polymarket event %s' % event_id, url)
    if not isinstance(event, dict):
        raise ValueError('Unexpected Polymarket event schema for %s' % event_id)
    trimmed = {key: event.get(key) for key in EVENT_FIELDS}
    trimmed['url'] = url
    trimmed['public_url'] = 'https://polymarket.com/event/' + str(event.get('slug') or '')
    trimmed['receipt'] = receipt
    trimmed['markets'] = [trim_market(m) for m in event.get('markets') or [] if isinstance(m, dict)]
    return trimmed


def hotspawn_inventory(src, now):
    """The official fixture feed, plus the questions this session has to answer.

    ``rows`` is deliberately trimmed to the fields the collector itself uses; the
    full response stays in the refresh snapshot's source receipts.
    """
    raw, receipt = src.get('Hotspawn CS2 fixtures', FIXTURES)
    if not isinstance(raw, list):
        raise ValueError('Expected a complete fixture array')
    rows = []
    for row in raw:
        if not isinstance(row, dict) or row.get('sport_alias') != 'cs2':
            continue
        start = iso(row['scheduled_start_time']) if row.get('scheduled_start_time') else None
        lock = iso(row['lock_time']) if row.get('lock_time') else None
        rows.append({
            'id': str(row.get('id')),
            'competition_id': row.get('competition_id'),
            'competition_name': row.get('competition_name'),
            'tier': row.get('tier'),
            'status': row.get('status'),
            'stage': row.get('stage'),
            'best_of': row.get('best_of'),
            'series_format': row.get('series_format'),
            'offered_points': row.get('offered_points'),
            'base_points': row.get('base_points'),
            'points_breakdown': row.get('points_breakdown'),
            'scheduled_start_time': row.get('scheduled_start_time'),
            'start': start,
            'lock': lock,
            'end_time': row.get('end_time'),
            'total_picks': row.get('total_picks'),
            'teams': [row.get('participants0_name'), row.get('participants1_name')],
            'team_ids': [row.get('participants0_id'), row.get('participants1_id')],
            'picked_percent': [row.get('participants0_picked_percent'), row.get('participants1_picked_percent')],
        })
    twc = [r for r in rows if 'thunderpick world championship' in str(r['competition_name'] or '').casefold()]
    day5 = [r for r in rows if str(r['start'] or '').startswith('2026-10-18')]
    open_rows = [r for r in rows
                 if r['lock'] and r['start'] and dt(r['lock']) > now and dt(r['start']) > now
                 and not r['end_time'] and r['status'] == 'scheduled'
                 and all(r['teams']) and len(set(r['teams'])) == 2
                 and not any(norm(t or '') in ('tbd', 'tba', 'unknown') for t in r['teams'])]
    return {
        'url': FIXTURES, 'receipt': receipt, 'observed_at': receipt['observed_at'],
        'rows_returned': len(rows),
        'rows_open_by_collector_rule': len(open_rows),
        'open_ids': [r['id'] for r in open_rows],
        'twc_rows': twc,
        'twc_main_event_rows': [r for r in twc
                                if 'south american' not in str(r['competition_name'] or '').casefold()],
        'rows_starting_2026_10_18': day5,
        'rows': rows,
    }


def day5_digest(inventory, gamma_markets, gamma_events, pinnacle, hltv_pages, results, books):
    """A compact, dated answer to 'what is the day-5 line and where does it come from'."""
    out = {'generated_at': now_iso(), 'fixtures': []}
    by_slug = {g['slug']: g for g in gamma_markets}
    for slug in DAY5_MARKET_SLUGS:
        found = by_slug.get(slug)
        markets = (found or {}).get('markets') or []
        moneyline = next((m for m in markets if m.get('sportsMarketType') == 'moneyline'), None)
        event = next((e for e in gamma_events if str(e.get('slug')) == slug), None)
        hltv_id = DAY5_SLUG_TO_HLTV.get(slug)
        hltv = next((p for p in hltv_pages if p and p.get('url') and
                     '/matches/%s/' % hltv_id in p['url']), None) if hltv_id else None
        # Re-check the pairing from the two sources' own machine-readable clocks
        # instead of trusting the recorded mapping.
        crosscheck = {'hltv_match_id': hltv_id, 'hltv_url': (hltv or {}).get('url'),
                      'hltv_start_unix': (hltv or {}).get('start_unix'),
                      'hltv_start_utc': (hltv or {}).get('start_utc'),
                      'hltv_teams': (hltv or {}).get('teams'),
                      'hltv_format': (hltv or {}).get('format'),
                      'market_game_start_time': (moneyline or {}).get('gameStartTime'),
                      'market_event_start_time': (moneyline or {}).get('eventStartTime'),
                      'event_start_time': (event or {}).get('startTime'),
                      'market_outcomes': (moneyline or {}).get('outcomes_parsed'),
                      'market_question': (moneyline or {}).get('question')}
        try:
            market_utc = dt(str((moneyline or {}).get('eventStartTime') or ''))
            hltv_unix = (hltv or {}).get('start_unix')
            crosscheck['start_times_agree'] = bool(
                hltv_unix and market_utc and int(hltv_unix) // 1000 == int(market_utc.timestamp()))
        except (TypeError, ValueError):
            crosscheck['start_times_agree'] = None
        entry = {
            'polymarket_slug': slug,
            'polymarket_market': moneyline,
            'polymarket_event': ({key: (event or {}).get(key) for key in
                                  ('id', 'slug', 'title', 'active', 'closed', 'live', 'ended',
                                   'startTime', 'eventDate', 'score', 'period', 'updatedAt')}
                                 if event else None),
            'hltv': ({key: hltv.get(key) for key in
                      ('url', 'teams', 'start_utc', 'start_unix', 'format', 'ranks', 'lineups',
                       'betting', 'observed_at', 'http_status')} if hltv else None),
            'on_hotspawn_board': None,
            'hotspawn_row': None,
            'thunderpick_page': None,
            'start_crosscheck': crosscheck,
        }
        pairs = set()
        if moneyline and moneyline.get('outcomes_parsed'):
            pairs = {norm(t) for t in moneyline['outcomes_parsed']}
        for row in (inventory or {}).get('rows') or []:
            if pairs and pairs <= {norm(t or '') for t in row['teams']}:
                entry['hotspawn_row'] = row
                entry['on_hotspawn_board'] = True
                break
        if entry['hotspawn_row'] is None:
            entry['on_hotspawn_board'] = False
        for probe in books or []:
            if probe.get('label', '').startswith('Thunderpick') and probe.get('url', '').endswith(
                    ('2843582', '2843592')):
                wants = '2843582' if 'aur1' in slug else '2843592'
                if wants in probe.get('url', ''):
                    entry['thunderpick_page'] = {key: probe.get(key) for key in
                                                 ('label', 'url', 'status', 'http_status', 'observed_at',
                                                  'server_side_odds')}
        out['fixtures'].append(entry)
    out['pinnacle_summary'] = ({'matchups_total': pinnacle.get('matchups_total'),
                                 'lines_total': pinnacle.get('lines_total'),
                                 'matchups_kept': len(pinnacle.get('matchups') or []),
                                 'matchups': pinnacle.get('matchups'),
                                 'lines': pinnacle.get('lines')} if pinnacle else None)
    out['hltv_results_days'] = ([{'date': d.get('date'), 'count': len(d.get('results') or []),
                                  'results': d.get('results')} for d in (results or {}).get('days') or []]
                                if results else None)
    out['book_probes'] = books
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-f659a6e2')
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    src = Sources(started)
    report = {'started_at': iso(started), 'session': 'f659a6e2', 'steps': []}

    def step(name, fn, path):
        try:
            value = fn()
        except Exception as exc:  # noqa: BLE001 - a blocked source is a finding, not a crash
            record = {'step': name, 'status': 'error', 'error': str(exc)[:400], 'file': None,
                      'checked_at': now_iso()}
            report['steps'].append(record)
            print('[error] %s: %s' % (name, record['error']))
            return None
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
        report['steps'].append({'step': name, 'status': 'ok', 'error': None, 'file': str(target),
                                'checked_at': now_iso()})
        print('[ok] %s -> %s' % (name, target))
        return value

    snapshot = json.loads(Path(args.snapshot).read_text()) if Path(args.snapshot).exists() else None
    ledger = step('compact open ledger', lambda: compact_ledger(snapshot), 'ledger.json') if snapshot else None

    inventory = step('Hotspawn official fixture inventory', lambda: hotspawn_inventory(src, started),
                     'hotspawn-inventory.json')

    gamma_markets = []
    for slug in DAY5_MARKET_SLUGS:
        value = step('Polymarket moneyline slug %s' % slug, lambda s=slug: gamma_market_by_slug(src, s),
                     'polymarket/day5-%s.json' % slug)
        if value:
            gamma_markets.append(value)

    gamma_events = []
    for event_id in DAY5_EVENT_IDS:
        value = step('Polymarket event %s' % event_id, lambda e=event_id: gamma_event(src, e),
                     'polymarket/event-%s.json' % event_id)
        if value:
            gamma_events.append(value)

    step('Polymarket active CS2 events (full scan)', lambda: trim_polymarket(src, started),
         'polymarket-active-cs2.json')

    tokens = []
    if ledger:
        for row in ledger['unpriced']:
            tokens += row['teams']
    tokens += ['FURIA', 'Aurora', 'Aurora Gaming', 'Falcons', 'Team Falcons', 'BETBOOM', 'BetBoom Team',
               'BB Team', 'Legacy', '9z', 'PARIVISION', 'Ninjas in Pyjamas']
    pinnacle = step('Pinnacle esports lines (filtered)', lambda: trim_pinnacle(src, tokens),
                    'pinnacle-esports.json')

    step('HLTV upcoming matches', lambda: hltv_upcoming(src), 'hltv-upcoming.json')
    results = step('HLTV Thunderpick WC results (days 1-4 re-verification)',
                   lambda: hltv_results(src, TWC_EVENT), 'hltv-twc-results.json')
    event_page = step('HLTV event %d schedule' % TWC_EVENT, lambda: hltv_event_matches(src, TWC_EVENT),
                      'hltv-twc-schedule.json')

    hltv_pages = []
    if event_page:
        for link in event_page['links']:
            match_id = link['url'].split('/matches/')[-1].split('/')[0]
            if match_id not in DAY5_HLTV_IDS:
                continue
            value = step('HLTV day-5 match %s' % match_id,
                         lambda u=link['url'], i=match_id: hltv_match(src, u, 'HLTV match %s' % i),
                         'hltv-twc-%s.json' % match_id)
            if value:
                hltv_pages.append(value)

    if ledger:
        for row in ledger['unpriced']:
            url = row.get('hltv_url')
            if not url:
                continue
            step('HLTV unpriced row %s' % row['id'],
                 lambda u=url, r=row: hltv_match(src, u, 'HLTV match for %s' % r['id']),
                 'hltv-unpriced-%s.json' % row['id'])

    needles = ['FURIA', 'Aurora', 'Falcons', 'BetBoom', 'BETBOOM']
    books = []
    for label, url in BOOK_PROBES:
        try:
            page, receipt = src.get(label, url, False)
            books.append({'label': label, 'url': url, 'status': 'ok',
                          'http_status': receipt.get('http_status'), 'observed_at': receipt['observed_at'],
                          'retrieved_at': receipt.get('retrieved_at'), 'sha256': receipt.get('sha256'),
                          'bytes': len(page),
                          'server_side_odds': embedded_line_hunt(page, needles)})
        except Exception as exc:  # noqa: BLE001
            record = next((r for r in src.log if r.get('url') == url), {})
            books.append({'label': label, 'url': url, 'status': 'error',
                          'http_status': record.get('http_status'), 'error': str(exc)[:300],
                          'observed_at': record.get('observed_at')})
    (out / 'book-probes.json').write_text(json.dumps(books, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    report['steps'].append({'step': 'esportsbook probes', 'status': 'ok', 'error': None,
                            'file': str(out / 'book-probes.json'), 'checked_at': now_iso()})

    digest = day5_digest(inventory, gamma_markets, gamma_events, pinnacle, hltv_pages, results, books)
    (out / 'DAY5-DIGEST.json').write_text(json.dumps(digest, indent=1, ensure_ascii=False, sort_keys=True) + '\n')

    lines = ['# Day-5 live evidence digest (session f659a6e2)', '',
             'Captured on a GitHub Actions runner; every value below is a field read from the',
             'response named beside it. Generated %s.' % digest['generated_at'], '']
    for fixture in digest['fixtures']:
        market = fixture.get('polymarket_market') or {}
        outcomes = market.get('outcomes_parsed') or []
        normalized = market.get('normalized') or []
        lines += [
            '## %s' % (fixture.get('polymarket_slug') or 'unknown'),
            '',
            '- Polymarket market: `%s` · type `%s` · [API](%s)' % (
                market.get('id'), market.get('sportsMarketType'), market.get('api_url')),
            '- Question: %s' % market.get('question'),
            '- Outcomes/prices as published: %s / %s' % (outcomes, market.get('outcomePrices_parsed')),
            '- Normalized (sum %s): %s' % (market.get('price_sum'),
                                           ['%.4f' % p for p in normalized] if normalized else None),
            '- Fair decimal: %s' % (['%.3f' % d for d in market['fair_decimal']]
                                    if market.get('fair_decimal') else None),
            '- Gate fields: bid %s ask %s spread %s liquidity %s acceptingOrders %s active %s closed %s' % (
                market.get('bestBid'), market.get('bestAsk'), market.get('spread'),
                market.get('liquidityNum'), market.get('acceptingOrders'), market.get('active'),
                market.get('closed')),
            '- Start: market `%s` · event `%s`' % (market.get('gameStartTime'),
                                                   (fixture.get('polymarket_event') or {}).get('startTime')),
            '- Start-time cross-check against HLTV: %s' % json.dumps(fixture.get('start_crosscheck'), sort_keys=True),
            '- Event flags: %s' % json.dumps(fixture.get('polymarket_event'), sort_keys=True),
            '- Market updatedAt: %s' % market.get('updatedAt'),
            '- On the Hotspawn board at this observation: **%s**' % fixture.get('on_hotspawn_board'),
            '- Hotspawn row: %s' % json.dumps(fixture.get('hotspawn_row'), sort_keys=True),
            '- HLTV: %s' % json.dumps(fixture.get('hltv'), sort_keys=True),
            '- Thunderpick page re-observation: %s' % json.dumps(fixture.get('thunderpick_page'), sort_keys=True),
            '',
        ]
    lines += ['## Inventory', '',
              '- Fixture feed rows returned: %s (observed %s)' % (
                  (inventory or {}).get('rows_returned'), (inventory or {}).get('observed_at')),
              '- Rows open by the collector rule: %s' % (inventory or {}).get('rows_open_by_collector_rule'),
              '- Main Thunderpick World Championship 2026 rows on the board: %s' % json.dumps(
                  (inventory or {}).get('twc_main_event_rows'), sort_keys=True),
              '- Rows starting 2026-10-18: %s' % json.dumps(
                  [{'id': r['id'], 'teams': r['teams'], 'competition_name': r['competition_name'],
                    'start': r['start'], 'tier': r['tier']}
                   for r in (inventory or {}).get('rows_starting_2026_10_18') or []], sort_keys=True),
              '', '## Esportsbook probes', '']
    for probe in digest['book_probes'] or []:
        lines.append('- %s: status `%s` HTTP `%s` observed %s%s' % (
            probe.get('label'), probe.get('status'), probe.get('http_status'), probe.get('observed_at'),
            '' if probe.get('status') == 'ok' else ' error=%s' % probe.get('error')))
        odds = probe.get('server_side_odds') or {}
        if odds:
            lines.append('  - decimal odds in server HTML: %s (needle hits %s, %s bytes)' % (
                odds.get('decimal_odds_anywhere'), odds.get('needle_hits'), odds.get('bytes')))
    lines += ['', '## HLTV results re-read (event %d)' % TWC_EVENT, '']
    for day in digest['hltv_results_days'] or []:
        lines.append('- %s: %d series' % (day.get('date'), day.get('count')))
        for result in day.get('results') or []:
            lines.append('  - %s %s %s · %s' % (' vs '.join(result['teams']), result['score'],
                                                result.get('map') or '', result['url']))
    lines += ['', '## Source receipts', '',
              '| Step | Status | File | Checked (UTC) |', '| --- | --- | --- | --- |']
    for step_row in report['steps']:
        lines.append('| %s | %s | %s | %s |' % (step_row['step'], step_row['status'],
                                                 step_row.get('file') or step_row.get('error') or '',
                                                 step_row['checked_at']))
    (out / 'DAY5-DIGEST.md').write_text('\n'.join(lines) + '\n')
    (out / 'probe-report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    print(json.dumps({'steps': len(report['steps']),
                      'errors': [s['step'] for s in report['steps'] if s['status'] != 'ok'],
                      'output': str(out)}, indent=1))


if __name__ == '__main__':
    main()
