"""Day-4 and day-5 TWC 2026 lines, recomputed from retained primary receipts.

Inputs, all already in the repository with their own SHA-256 records:

* ``research/harvest-76712ccc/pinnacle-twc.json``  — Pinnacle's public guest API for
  league 230242 (matchups + related straight markets). The whole-series market is the
  period-0 ``s;0;m`` moneyline; period 1 is map 1 and is labelled as such, never mixed in.
* ``research/harvest-76712ccc/polymarket-cs2-scan.json`` — Polymarket's active CS2 event
  pages, including both semi-final BO3 markets.
* ``data/vrs/standings_global_2026_10_05.md`` + ``data/vrs/meta.json`` — Valve's official
  standings, used with Valve's own formula for our labelled model line (it predates the
  event, which is stated on every row).

Every number is recomputed here from those raw fields with the same helpers the production
pipeline uses (``scripts.core.devig``/``american``, ``scripts.vrs.expected``/``calibrated``).
No value is typed by hand and no source is blended: the market line, the second market and
our model line are published side by side with their own labels.

Usage:
    python scripts/twc_day4_76712ccc.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.core import american, devig
from scripts.vrs import calibrated, expected, parse as parse_standings

ROOT = Path(__file__).resolve().parents[1]

# Semi-final parents in Pinnacle's league 230242 and the Polymarket BO3 market for the
# same two fixtures. Identifiers only: all prices are read from the retained payloads.
SEMIS = (
    {'key': 'semi-1', 'label': 'FURIA vs Aurora', 'pinnacle_parent': '1638536356',
     'polymarket_event': 'cs2-furia-aur1-2026-10-17', 'polymarket_market': 5778024,
     'start_utc': '2026-10-17T14:00:00Z', 'hltv': 'https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026',
     'teams': ['FURIA', 'Aurora'],
     'vrs_labels': {'FURIA': 'FURIA', 'Aurora': 'Aurora'}},
    {'key': 'semi-2', 'label': 'Falcons vs BETBOOM', 'pinnacle_parent': '1638595724',
     'polymarket_event': 'cs2-fal2-bb3-2026-10-17', 'polymarket_market': 5787759,
     'start_utc': '2026-10-17T17:00:00Z', 'hltv': 'https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026',
     'teams': ['Falcons', 'BETBOOM'],
     # Pinnacle labels the same organization "BB Team"; the mapping is registered with the
     # organization's own site in data/identities.json.
     'vrs_labels': {'Falcons': 'Falcons', 'BETBOOM': 'BETBOOM'}},
)


def receipt_fields(record):
    return {k: record.get(k) for k in ('url', 'http_status', 'observed_at', 'sha256', 'cache_age_seconds',
                                       'cache_status') if record}


def pinnacle_series(document, parent_id):
    """The whole-series moneyline and the map-1 moneyline for one parent matchup."""
    data = (document.get('parents_markets') or {}).get(str(parent_id)) or {}
    if 'error' in data:
        raise ValueError('Pinnacle parent %s: %s' % (parent_id, data['error']))
    out = {'teams': data.get('teams'), 'receipt': receipt_fields(data.get('receipt') or {}), 'markets': {}}
    for market in data.get('series_moneylines') or []:
        if market['period'] == 0:
            out['markets']['series'] = market
        elif market['period'] == 1:
            out['markets']['map1'] = market
    if 'series' not in out['markets']:
        raise ValueError('No period-0 (whole series) moneyline retained for parent %s' % parent_id)
    return out


def polymarket_series(document, market_id):
    for event in document.get('events') or []:
        for market in event.get('markets') or []:
            if str(market.get('id')) != str(market_id):
                continue
            raw = market.get('outcomes')
            outcomes = json.loads(raw) if isinstance(raw, str) else raw
            raw_prices = market.get('outcomePrices')
            prices = [float(x) for x in (json.loads(raw_prices) if isinstance(raw_prices, str) else raw_prices)]
            total = sum(prices)
            return {'event_id': event.get('id'), 'event_slug': event.get('slug'),
                    'question': market.get('question'), 'outcomes': outcomes,
                    'prices': prices, 'normalized': [round(x / total, 6) for x in prices],
                    'liquidity': market.get('liquidityNum'), 'spread': market.get('spread'),
                    'accepting_orders': market.get('acceptingOrders'),
                    'updated_at': market.get('updatedAt'), 'game_start': market.get('gameStartTime'),
                    'source': market.get('api_url'), 'observed_at': document.get('observed_at')}
    raise ValueError('Polymarket market %s is not in the retained CS2 scan' % market_id)


def model_line(standings, meta, team_a, team_b):
    rows = {row['name']: row for row in standings['teams']}
    missing = [t for t in (team_a, team_b) if t not in rows]
    if missing:
        raise ValueError('Not in Valve standings: %s' % ', '.join(missing))
    a, b = rows[team_a], rows[team_b]
    raw = expected(a['points'], b['points'])
    p = calibrated(raw)
    return {'teams': [a['name'], b['name']], 'points': [a['points'], b['points']],
            'standings_positions': [a['standing'], b['standing']],
            'rosters': [a['roster'], b['roster']],
            'probabilities': [round(p, 6), round(1 - p, 6)],
            'raw_expected': round(raw, 6), 'calibration_slope': 0.7986,
            'standings_as_of': standings['as_of'], 'source': meta['blob_url'],
            'details': [meta['details_base'] + a['details'], meta['details_base'] + b['details']],
            'note': 'Our originated line: Valve points through Valve\'s own formula and published fit '
                    'slope. Valve\'s file predates the event, so it does not include TWC 2026 results.'}


def decimal_from_american(value):
    return round(american(value), 6)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--harvest', default='research/harvest-76712ccc')
    parser.add_argument('--output', default='research/day4-76712ccc/DAY4-LINES.json')
    parser.add_argument('--markdown', default='research/day4-76712ccc/DAY4-LINES.md')
    args = parser.parse_args()

    harvest = Path(args.harvest)
    pinnacle = json.loads((harvest / 'pinnacle-twc.json').read_text())
    polymarket = json.loads((harvest / 'polymarket-cs2-scan.json').read_text())
    meta = json.loads((ROOT / 'data/vrs/meta.json').read_text())
    standings = parse_standings((ROOT / 'data/vrs' / meta['file']).read_text())

    fixtures = []
    for semi in SEMIS:
        pin = pinnacle_series(pinnacle, semi['pinnacle_parent'])
        series = pin['markets']['series']
        home, away = series['american']['home'], series['american']['away']
        probs, margin = devig([decimal_from_american(home), decimal_from_american(away)])
        pm = polymarket_series(polymarket, semi['polymarket_market'])
        model = model_line(standings, meta, semi['vrs_labels'][semi['teams'][0]], semi['vrs_labels'][semi['teams'][1]])
        entry = {
            'key': semi['key'], 'label': semi['label'], 'teams': semi['teams'], 'start_utc': semi['start_utc'],
            'hltv_match': semi['hltv'], 'best_of': 3,
            'pinnacle': {
                'market': 'whole series (period 0, key s;0;m)', 'status': series['status'],
                'cutoff_at': series['cutoffAt'], 'american': {'home': home, 'away': away},
                'decimal': {'home': decimal_from_american(home), 'away': decimal_from_american(away)},
                'probabilities': {'home': round(probs[0], 6), 'away': round(probs[1], 6)},
                'overround': round(margin, 6), 'receipt': pin['receipt'], 'source_teams': pin['teams']},
            'pinnacle_map1': ({'status': pin['markets']['map1']['status'],
                               'american': pin['markets']['map1']['american'],
                               'probabilities': pin['markets']['map1']['probabilities'],
                               'cutoff_at': pin['markets']['map1']['cutoffAt']}
                              if 'map1' in pin['markets'] else None),
            'polymarket': pm,
            'model': model,
        }
        # Which side each market calls the favourite, so no reader has to infer it.
        entry['favourite'] = {
            'pinnacle': semi['teams'][0] if probs[0] > probs[1] else semi['teams'][1],
            'polymarket': pm['outcomes'][0] if pm['normalized'][0] > pm['normalized'][1] else pm['outcomes'][1],
            'model': model['teams'][0] if model['probabilities'][0] > model['probabilities'][1] else model['teams'][1],
        }
        fixtures.append(entry)

    document = {'generated_from': {
        'pinnacle': receipt_fields(pinnacle.get('matchups_receipt') or {}),
        'polymarket_scan_observed_at': polymarket.get('observed_at'),
        'valve_standings': {'file': meta['file'], 'commit': meta.get('commit'),
                            'blob_url': meta['blob_url'], 'as_of': standings['as_of']}},
        'fixtures': fixtures}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=1, ensure_ascii=False, sort_keys=True) + '\n')

    lines = ['# Day 4 (17 October) Thunderpick World Championship 2026 — lines from retained primary receipts', '',
             'Recomputed by `scripts/twc_day4_76712ccc.py` from the raw payloads listed in',
             '`research/harvest-76712ccc/`. Pinnacle is a whole-series (period 0) two-way moneyline;',
             'Polymarket is a two-sided exchange price normalised to sum to one; the model line is ours,',
             'from Valve\'s official standings of %s (pre-event).' % standings['as_of'], '',
             '| Fixture (UTC start) | Pinnacle series | Pinnacle map 1 | Polymarket series | Our VRS model | Pinnacle favourite |',
             '| --- | --- | --- | --- | --- | --- |']
    for f in fixtures:
        pin = f['pinnacle']['probabilities']
        pm = f['polymarket']['normalized']
        mo = f['model']['probabilities']
        lines.append('| %s — %s (%s) | %s %.1f%% / %s %.1f%% | %s | %s %.1f%% / %s %.1f%% | %s %.1f%% / %s %.1f%% | %s |' % (
            f['teams'][0], f['teams'][1], f['start_utc'],
            f['teams'][0], 100 * pin['home'], f['teams'][1], 100 * pin['away'],
            ('%.1f%% / %.1f%%' % (100 * f['pinnacle_map1']['probabilities']['home'],
                                  100 * f['pinnacle_map1']['probabilities']['away'])
             if f['pinnacle_map1'] else '—'),
            f['polymarket']['outcomes'][0], 100 * pm[0], f['polymarket']['outcomes'][1], 100 * pm[1],
            f['model']['teams'][0], 100 * mo[0], f['model']['teams'][1], 100 * mo[1],
            f['favourite']['pinnacle']))
    lines += ['', 'Overround: %s.' % ', '.join('%s %.2f%%' % (f['label'], 100 * f['pinnacle']['overround'])
                                               for f in fixtures)]
    Path(args.markdown).write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines[6:]))
    print('\nwrote %s and %s' % (out, args.markdown))


if __name__ == '__main__':
    main()
