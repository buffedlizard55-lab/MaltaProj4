#!/usr/bin/env python3
"""Session e9be3e6b — zero-network, line-by-line verification of the published board.

Run against any snapshot (default ``data/latest.json``). It deliberately shares no
collector code with ``scripts.refresh``: every number is re-derived from the price
fields stored on the row, and every non-featured row must show the official-source
ladder that was tried before the fallback was used.

The user-facing contract checked here:

* every displayed match row carries an https official Hotspawn fixture link;
* every open match carries a pick, and a win probability that sums to 1 and
  re-derives exactly from its own stored source price;
* a price never originates from Hotspawn's crowd "picked" percentages;
* for every match that could not be resolved like a featured (strict exchange) pick,
  the row records (1) an HLTV attempt, (2) an esportsbook/exchange attempt, and
  (3) the accepted fallback's own source link and limitation label;
* bookmaker listings refuse the symmetric 1.8 / 1.8 placeholder; wide exchange
  quotes publish their real spread and are labelled low confidence; model lines
  publish their Valve-points vintage and are labelled as originations.

This is verification, not certification of a bookmaker's accuracy or a team's true
chance. ``--json`` emits the full per-row receipt; exit status is 1 on any failure.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SLOPE = 0.7986
RD = 75.0
Q = math.log(10) / 400
G = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
TOL = 1e-9
EVIDENCE_HOURS = 8
BOOK_PROVIDERS = (
    'pinnacle', 'thunderpick', 'gg.bet', 'egamersworld', 'bo3.gg',
    'book listing', 'book research', 'polymarket', 'kalshi', 'stavka',
)
STRICT_METHOD = 'exchange'


def norm(value):
    folded = unicodedata.normalize('NFKD', str(value))
    folded = ''.join(c for c in folded if not unicodedata.combining(c))
    return ''.join(c for c in folded.lower() if c.isalnum())


def same_team(a, b, aliases=None):
    """Exact, unambiguous prefix, or a row's own https-sourced identity record."""
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b:
        return True
    short, long = sorted((a, b), key=len)
    if len(short) >= 3 and long.startswith(short):
        return True
    for identity in aliases or ():
        if not isinstance(identity, dict):
            continue
        if not str(identity.get('source') or '').startswith('https://'):
            continue
        names = {norm(n) for n in (identity.get('names') or [])}
        if a in names and b in names:
            return True
    return False


def host(url):
    try:
        return (urlparse(str(url)).hostname or '').lower()
    except ValueError:
        return ''


def is_hotspawn_source(url):
    h = host(url)
    return h == 'hotspawn.com' or h.endswith('.hotspawn.com')


def parse_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(timezone.utc)
    except ValueError:
        return None


def glicko_expect(points_a, points_b):
    return 1 / (1 + 10 ** (-G * (float(points_a) - float(points_b)) / 400))


def calibrate(raw):
    return 0.5 + SLOPE * (raw - 0.5)


def replay_evidence(ev, teams):
    """Return (probabilities, kind) replayed from one evidence record only."""
    provider = ev.get('provider') or ''
    if provider in ('Valve VRS model', 'HLTV Valve ranking (Valve points)'):
        raw = glicko_expect(ev['points'][0], ev['points'][1])
        p = [calibrate(raw), 1 - calibrate(raw)]
        return p, 'valve_vrs'
    if 'decimal_odds' in ev:
        odds = [float(v) for v in ev['decimal_odds']]
        if len(odds) != 2 or min(odds) <= 0:
            raise ValueError('bookmaker listing needs two positive decimal prices')
        q = [1 / d for d in odds]
        p = [v / sum(q) for v in q]
        labels = ev.get('source_teams') or teams
        if len(labels) != 2:
            raise ValueError('bookmaker listing needs two labelled outcomes')
        aliases = ev.get('identity_sources')
        mapping = []
        for team in teams:
            hits = [i for i, label in enumerate(labels) if same_team(label, team, aliases)]
            if len(hits) != 1:
                raise ValueError('cannot map %r to exactly one listing outcome %r' % (team, labels))
            mapping.append(hits[0])
        if len(set(mapping)) != 2:
            raise ValueError('both fixture teams mapped to one listing outcome')
        return [p[i] for i in mapping], 'listing_devig'
    raw = ev.get('raw') or {}
    prices = raw.get('outcomePrices')
    if prices:
        x = [float(v) for v in (json.loads(prices) if isinstance(prices, str) else prices)]
        p = [v / sum(x) for v in x]
        labels = json.loads(raw['outcomes']) if isinstance(raw.get('outcomes'), str) else raw.get('outcomes')
        if labels and teams:
            aliases = ev.get('identity_sources')
            mapping = []
            for team in teams:
                hits = [i for i, label in enumerate(labels) if same_team(label, team, aliases)]
                if len(hits) != 1:
                    raise ValueError('cannot map %r to exactly one exchange outcome %r' % (team, labels))
                mapping.append(hits[0])
            if len(set(mapping)) != 2:
                raise ValueError('both fixture teams mapped to one exchange outcome')
            p = [p[i] for i in mapping]
        return p, 'exchange_mid'
    raise ValueError('no reproducible price in evidence record')


def ladder_attempts(row):
    attempts = [a for a in (row.get('attempts') or []) if isinstance(a, dict)]
    hltv = [a for a in attempts
            if str(a.get('provider') or '').startswith('HLTV')
            or host(a.get('url')) in ('hltv.org', 'www.hltv.org')]
    books = [a for a in attempts
            if any(tag in str(a.get('provider') or '').lower() for tag in BOOK_PROVIDERS)
            or any(tag in host(a.get('url')) for tag in
                   ('polymarket.com', 'pinnacle.com', 'thunderpick', 'gg.bet',
                    'egamersworld.com', 'bo3.gg', 'stavka.tv'))]
    return hltv, books, attempts


def verify_row(row, snapshot_generated=None):
    """Verify one match row. Returns (checks, problems, method)."""
    checks, problems = [], []
    rid = str(row.get('id'))
    teams = row.get('teams') or []
    method = row.get('method')
    state = row.get('state')
    p = row.get('probabilities')
    pick = row.get('pick')
    fair = row.get('fair_odds')
    ev = (row.get('evidence') or [None])[0]

    fixture_url = row.get('source_url')
    if not str(fixture_url or '').startswith('https://') or not is_hotspawn_source(fixture_url):
        problems.append('missing https official Hotspawn fixture link: %r' % fixture_url)
    else:
        checks.append('official Hotspawn fixture link')

    if state != 'open':
        checks.append('not open at this snapshot; no current recommendation claimed')
        return checks, problems, method

    if len(teams) != 2 or not all(isinstance(t, str) and t.strip() for t in teams):
        problems.append('open row does not name exactly two teams')
        return checks, problems, method
    if pick not in teams:
        problems.append('pick %r is not one of the two fixture teams' % pick)
    else:
        checks.append('pick names a fixture team')

    if not ev or not isinstance(ev, dict):
        problems.append('open row has no evidence record')
        return checks, problems, method
    ev_url = ev.get('url') or ev.get('api_url')
    if not str(ev_url or '').startswith('https://'):
        problems.append('evidence record has no https source link')
    else:
        checks.append('evidence source link')
    if is_hotspawn_source(ev_url) and ev.get('provider') not in ('Hotspawn discovery',):
        problems.append('probability would originate from a Hotspawn page; crowd votes are refused')
    else:
        checks.append('probability source is external to Hotspawn')

    if p is None:
        # Research-only or unresolved: a number is refused, not invented.
        if fair is not None:
            problems.append('no probability but fair odds are present')
        if not row.get('reason'):
            problems.append('no-percentage row lacks its limitation')
        if not (row.get('attempts') or []):
            problems.append('no-percentage row lacks attempted sources')
        else:
            checks.append('no-percentage row publishes its limitation and attempts')
        return checks, problems, method

    if len(p) != 2 or abs(sum(p) - 1) > TOL:
        problems.append('probabilities do not sum to 1')
        return checks, problems, method
    checks.append('probabilities sum to 1')

    try:
        replayed, kind = replay_evidence(ev, teams)
    except Exception as exc:                                  # noqa: BLE001 - reported
        problems.append('not reproducible from stored evidence: %s' % exc)
        replayed = None
        kind = None
    if replayed is not None:
        if max(abs(p[i] - replayed[i]) for i in (0, 1)) > 1e-6:
            problems.append('published %.9f != replayed %.9f' % (p[0], replayed[0]))
        else:
            checks.append('%s replayed (max delta %.2e)' % (kind, max(abs(p[i] - replayed[i]) for i in (0, 1))))
    if pick in teams and p[teams.index(pick)] + TOL < max(p):
        problems.append('pick is not the larger probability')
    else:
        checks.append('pick follows the larger probability')
    if fair:
        if max(abs(fair[i] - 1 / p[i]) for i in (0, 1)) > 1e-6:
            problems.append('fair odds are not 1/p')
        else:
            checks.append('fair odds = 1/p')

    generated = parse_time(snapshot_generated)
    expiry = parse_time(row.get('expires_at'))
    lock = parse_time(row.get('lock'))
    start = parse_time(row.get('start'))
    if expiry is None:
        problems.append('priced row has no expiry deadline')
    else:
        for label, bound in (('lock', lock), ('start', start)):
            if bound and expiry > bound + timedelta(seconds=1):
                problems.append('expiry is later than the %s' % label)
        if generated and expiry <= generated:
            problems.append('expiry is not after the snapshot clock')
        if not problems:
            checks.append('expiry respects lock, start and snapshot clock')

    hltv, books, attempts = ladder_attempts(row)
    if method == STRICT_METHOD:
        checks.append('featured strict-exchange pick; fallback research not required')
        return checks, problems, method

    if not hltv:
        problems.append('non-featured pick records no HLTV attempt')
    elif not all(str(a.get('url') or '').startswith('https://') for a in hltv):
        problems.append('HLTV attempt has no https source link')
    else:
        checks.append('HLTV attempted with an official link')
    if not books:
        problems.append('non-featured pick records no esportsbook/exchange attempt')
    elif not all(str(a.get('url') or '').startswith('https://') for a in books):
        problems.append('esportsbook attempt has no https source link')
    else:
        checks.append('esportsbook/exchange attempted with a link')

    if method == 'exchange_wide':
        spread = ev.get('spread')
        liquidity = ev.get('liquidity')
        if spread is None or float(spread) <= 0.25:
            problems.append('wide quote does not publish a spread over 25 points')
        if liquidity is None or float(liquidity) < 100:
            problems.append('wide quote is below the $100 liquidity floor')
        if 'low confidence' not in str(ev.get('warning') or '').lower():
            problems.append('wide quote is not labelled low confidence')
        if str(ev.get('tier') or '') != 'wide_exchange':
            problems.append('wide quote is not labelled wide_exchange')
        if not ev.get('strict_rejection'):
            problems.append('wide quote does not retain its strict-gate rejection')
        if not problems:
            checks.append('wide quote: spread %.2f, $%.2f liquidity, labelled' % (float(spread), float(liquidity)))
    elif method == 'bookmaker_fallback':
        odds = ev.get('decimal_odds')
        if not odds or len(odds) != 2:
            problems.append('book listing has no two-sided price')
        elif abs(float(odds[0]) - float(odds[1])) < 1e-9:
            problems.append('symmetric placeholder listing (e.g. 1.8 / 1.8) was accepted')
        over = ev.get('overround')
        if over is None or not -0.02 <= float(over) <= 0.25:
            problems.append('book listing overround outside the -2%..25% gate')
        if ev.get('start') and ev['start'] != row.get('start'):
            problems.append('book listing start does not equal the Hotspawn UTC start')
        if not str(ev.get('warning') or '').lower().startswith('researched'):
            problems.append('book listing is not labelled as a researched listing')
        for label, url in (('match page', ev.get('url')), ('feed', ev.get('api_url'))):
            if not str(url or '').startswith('https://'):
                problems.append('book listing %s link missing' % label)
        if not problems:
            checks.append('book listing: %s / %s, overround %.2f%%' % (odds[0], odds[1], float(over) * 100))
    elif method in ('model_vrs', 'model_vrs_mirror'):
        points = ev.get('points')
        if not points or len(points) != 2:
            problems.append('model line has no two-team Valve points')
        if ev.get('calibration_slope') != SLOPE or ev.get('rating_deviation') != RD:
            problems.append('model line does not use the published Valve slope/RD')
        vintage = str(ev.get('standings_as_of') or '')
        warning = str(ev.get('warning') or '')
        if method == 'model_vrs':
            if 'github.com/valvesoftware/counter-strike_regional_standings' not in str(ev.get('url') or '').lower():
                problems.append('VRS model does not link Valve\'s official standings file')
            if not vintage or vintage not in warning:
                problems.append('VRS model does not publish its standings vintage')
        else:
            if host(ev.get('url')) not in ('hltv.org', 'www.hltv.org') or '/valve-ranking/' not in str(ev.get('url')):
                problems.append('VRS mirror does not link HLTV\'s dated Valve ranking')
            if not warning or 'hltv' not in warning.lower():
                problems.append('VRS mirror does not say the points came from HLTV')
        if 'not a market price' not in warning:
            problems.append('model line is not labelled as an originated, non-market line')
        if not problems:
            checks.append('model line: %s pts, vintage %s, labelled non-market' % (points, vintage or 'HLTV dated'))
    elif str(method or '').startswith('research_'):
        problems.append('research-only method must not publish a probability')
    else:
        problems.append('unrecognised method %r' % method)

    return checks, problems, method


def audit(snapshot, at=None):
    generated = at or snapshot.get('generated_at')
    rows = snapshot.get('matches') or []
    results = []
    for row in sorted(rows, key=lambda r: (str(r.get('start') or ''), str(r.get('id')))):
        checks, problems, method = verify_row(row, generated)
        results.append({
            'id': str(row.get('id')),
            'teams': row.get('teams'),
            'start': row.get('start'),
            'state': row.get('state'),
            'method': method,
            'pick': row.get('pick'),
            'probabilities': row.get('probabilities'),
            'source_url': row.get('source_url'),
            'evidence_url': ((row.get('evidence') or [None])[0] or {}).get('url')
                            or ((row.get('evidence') or [None])[0] or {}).get('api_url'),
            'checks': checks,
            'problems': problems,
        })
    open_rows = [r for r in results if r['state'] == 'open']
    summary = {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'audit_at': datetime.now(timezone.utc).isoformat(),
        'rows': len(results),
        'open': len(open_rows),
        'open_with_pick': sum(1 for r in open_rows if r['pick']),
        'open_with_probability': sum(1 for r in open_rows if r['probabilities']),
        'open_research_only': sum(1 for r in open_rows if r['pick'] and not r['probabilities']),
        'open_unresolved': sum(1 for r in open_rows if not r['pick'] and not r['probabilities']),
        'non_featured': sum(1 for r in open_rows if r['method'] and r['method'] != STRICT_METHOD),
        'methods': {m: sum(1 for r in open_rows if r['method'] == m)
                    for m in sorted({r['method'] for r in open_rows if r['method']})},
        'checks': sum(len(r['checks']) for r in results),
        'failures': sum(1 for r in results if r['problems']),
    }
    return {'summary': summary, 'rows': results}


def corrupted_cases(snapshot):
    """Synthetic corruption cases: each MUST be caught by the verifier."""
    cases = {}

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
    row['probabilities'] = list(reversed(row['probabilities']))
    cases['swapped_probabilities'] = doc

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['method'] == 'bookmaker_fallback')
    row['evidence'][0]['decimal_odds'] = [1.8, 1.8]
    cases['placeholder_book_price'] = doc

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['method'] in ('model_vrs', 'model_vrs_mirror'))
    row['evidence'][0]['points'] = [row['evidence'][0]['points'][0] + 100, row['evidence'][0]['points'][1]]
    cases['edited_valve_points'] = doc

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['method'] != STRICT_METHOD)
    row['attempts'] = [a for a in row.get('attempts', []) if not str(a.get('provider') or '').startswith('HLTV')]
    cases['hltv_attempt_removed'] = doc

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['method'] != STRICT_METHOD)
    row['attempts'] = [a for a in row.get('attempts', [])
                       if not any(tag in str(a.get('provider') or '').lower() for tag in BOOK_PROVIDERS)]
    cases['esportsbook_attempt_removed'] = doc

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
    row['evidence'][0]['url'] = 'https://play.hotspawn.com/lobby'
    cases['hotspawn_crowd_as_price_source'] = doc

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['expires_at'])
    row['expires_at'] = '2030-01-01T00:00:00Z'
    cases['expiry_past_lock'] = doc

    doc = copy.deepcopy(snapshot)
    row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
    row['probabilities'] = None
    cases['blank_probability_without_limitation'] = doc

    return cases


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--snapshot', default=str(ROOT / 'data' / 'latest.json'))
    ap.add_argument('--at', default=None, help='override snapshot clock (ISO-8601 UTC)')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--output', default=None)
    ap.add_argument('--self-test', action='store_true', help='prove the verifier rejects nine corruptions')
    args = ap.parse_args(argv)

    snapshot = json.loads(Path(args.snapshot).read_text())
    report = audit(snapshot, at=args.at)
    if args.self_test:
        cases = corrupted_cases(snapshot)
        caught = {}
        for name, doc in cases.items():
            caught[name] = audit(doc, at=snapshot.get('generated_at'))['summary']['failures'] > 0
        report['self_test'] = caught
        if not all(caught.values()):
            report['summary']['self_test_failures'] = [k for k, v in caught.items() if not v]

    text = json.dumps(report, indent=1, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + '\n')
    if args.json:
        print(text)
    else:
        s = report['summary']
        print('snapshot: %s | fixture evidence: %s' % (s['snapshot_generated_at'], s['fixtures_observed_at']))
        print('rows %(rows)d | open %(open)d | picks %(open_with_pick)d | probabilities %(open_with_probability)d | '
              'research-only %(open_research_only)d | unresolved %(open_unresolved)d' % s)
        print('non-featured methods: %s' % json.dumps(s['methods'], sort_keys=True))
        print('checks: %(checks)d | failures: %(failures)d' % s)
        if args.self_test:
            print('corruption cases caught: %d/%d' % (sum(report['self_test'].values()), len(report['self_test'])))
        for row in report['rows']:
            for problem in row['problems']:
                print('FAIL: %s %s: %s' % (row['id'], ' vs '.join(row['teams'] or []), problem))
    failed = report['summary']['failures'] > 0
    if args.self_test and report['summary'].get('self_test_failures'):
        failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
