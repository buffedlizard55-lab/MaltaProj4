"""Session 76712ccc probe: can every open fixture be priced, and what are the day-4 lines?

Two questions this answers with raw, retained evidence rather than assertion:

1. For every open Hotspawn row that still carries **no percentage**, which
   accessible source actually lists that exact fixture? The sweep enumerates
   Pinnacle's live CS2 leagues, pulls each league's matchups, and for any matchup
   whose participants include one of our team labels it keeps the matchup and the
   related straight markets. Polymarket's active CS2 events are enumerated the same
   way the production refresh does it. Neither source is ever asked to guess: a row
   is priced only when the exact two team labels and the exact series market appear
   in the retained payload, and the devig is recomputed here from the raw prices.

2. For the Thunderpick World Championship 2026 playoff picture (day 4 = 17 October:
   two semi-finals; day 5 = 18 October: third-place decider and grand final), the
   raw Pinnacle matchups and straight markets plus HLTV's own event schedule and
   match pages are retained so the published line can be re-derived line by line.

Everything written here is an observation with a receipt: HTTP status, byte length,
SHA-256, observation time (HTTP cache age subtracted) and the archived raw body.
A blocked or empty source is recorded as a finding, never converted into a number.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from scripts.core import FIXTURES, GAMMA, PIN, devig, american, iso, norm
from scripts.refresh import Sources

# Thunderpick World Championship 2026 (HLTV event 8932). Playoff match ids are
# discovered from the event schedule at run time rather than hard-coded, because
# HLTV slugs change once a qualifier is decided.
TWC_EVENT = 8932
TWC_PINNACLE_LEAGUE = 230242  # "CS2 - TP World Championship"

# Pinnacle matchups confirmed by hand before this probe existed (2026-10-16 ~23:5xZ):
#   parent 1638536356 FURIA vs Aurora   starts 2026-10-17T14:00:00Z
#   parent 1638595724 Falcons vs BB Team starts 2026-10-17T17:00:00Z
# The probe re-reads them live and recomputes the devig; the ids are only a hint.
TWC_PARENT_HINTS = (1638536356, 1638595724)

# Esportsbook endpoints measured from a normal egress. Access checks are not
# presented as working odds adapters: the needle scan only reports whether a team
# label appears server-side at all.
BOOK_PROBES = (
    ('GG.BET CS2 page', 'https://gg.bet/en/esports/counter-strike'),
    ('Thunderpick CS2 page', 'https://thunderpick.io/esports/cs2-betting'),
    ('Rivalry CS2 page', 'https://www.rivalry.com/esports/counter-strike'),
    ('EGamersWorld CS2 matches', 'https://egamersworld.com/counterstrike/matches'),
    ('BetExplorer CS2', 'https://www.betexplorer.com/esports/counter-strike/'),
    ('OddsPortal CS2', 'https://www.oddsportal.com/esports/counter-strike/'),
    ('Stake CS2', 'https://stake.com/sports/counter-strike'),
    ('Betway esports CS2', 'https://betway.com/en/sports/grp/esports/counter-strike'),
)

HLTV_PAGES = (
    ('HLTV TWC results', 'https://www.hltv.org/results?event=%d' % TWC_EVENT),
    ('HLTV TWC schedule', 'https://www.hltv.org/events/%d/matches' % TWC_EVENT),
    ('HLTV world ranking', 'https://www.hltv.org/ranking/teams/'),
)


def now_iso():
    return iso(datetime.now(timezone.utc))


def compact_ledger(snapshot):
    """One line per open row: what the board claims and what is still unpriced."""
    rows = []
    for m in snapshot.get('matches') or []:
        rows.append({
            'id': m['id'],
            'teams': m['teams'],
            'competition': m['competition'],
            'start': m['start'],
            'state': m['state'],
            'method': m.get('method'),
            'pick': m.get('pick'),
            'probabilities': m.get('probabilities'),
            'best_of': m.get('best_of'),
            'hltv_url': next((e.get('url') for e in (m.get('evidence') or [])
                              if 'hltv.org' in str(e.get('url') or '')), None) or next(
                (a.get('url') for a in (m.get('attempts') or [])
                 if 'hltv.org/matches/' in str(a.get('url') or '')), None),
            'attempts': [{'provider': a.get('provider'), 'status': a.get('status'),
                          'reason': a.get('reason'), 'url': a.get('url')} for a in (m.get('attempts') or [])],
        })
    rows.sort(key=lambda r: (r['start'] or '', r['id']))
    opens = [r for r in rows if r['state'] == 'open']
    return {
        'rows_total': len(rows),
        'open_total': len(opens),
        'open_priced': [r for r in opens if r['probabilities']],
        'open_unpriced': [r for r in opens if not r['probabilities']],
        'rows': rows,
    }


def archive_raw(src, out, keys):
    """Copy the archived raw body of already-fetched endpoints into the repo.

    ``Sources.get`` writes every response body to ``runtime/sources/<sha256>``.
    Those files are uploaded as CI artifacts but expire, so the bodies that carry
    published numbers are copied next to the receipts that name their hash.
    """
    copied = []
    for record in src.log:
        if record.get('status') != 'ok' or not record.get('sha256'):
            continue
        if keys and record['name'] not in keys:
            continue
        source = None
        for suffix in ('.json', '.html'):
            candidate = Path('runtime/sources') / (record['sha256'] + suffix)
            if candidate.exists():
                source = candidate
                break
        if source is None:
            continue
        target = out / 'raw' / (record['sha256'][:16] + '-' + ''.join(
            ch if ch.isalnum() or ch in '-_' else '_' for ch in record['name'])[:60] + source.suffix)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append({'name': record['name'], 'url': record['url'], 'sha256': record['sha256'],
                       'bytes': record.get('bytes'), 'observed_at': record.get('observed_at'),
                       'file': str(target)})
    return copied


def pinnacle_cs2_sweep(src, tokens):
    """Enumerate every live Pinnacle CS2 league and keep the matchups that touch our teams."""
    leagues, leagues_receipt = src.get('Pinnacle esports leagues', PIN + '/sports/12/leagues')
    cs2 = [l for l in leagues if str(l.get('name') or '').startswith('CS2 - ')]
    wanted = {norm(t) for t in tokens if t}
    per_league, hits = [], []
    for league in sorted(cs2, key=lambda l: str(l.get('name'))):
        name = str(league.get('name'))
        try:
            matchups, receipt = src.get('Pinnacle league matchups ' + name,
                                        '%s/leagues/%s/matchups' % (PIN, league['id']))
        except ValueError as exc:
            per_league.append({'league': name, 'id': league['id'], 'status': 'error', 'reason': str(exc)[:200]})
            continue
        kept = []
        for m in matchups:
            labels = [str(p.get('name') or '') for p in m.get('participants') or []]
            # A parent matchup carries the series participants; a child carries the
            # same participants nested under `parent`. Both shapes are walked.
            nested = [str(p.get('name') or '') for p in ((m.get('parent') or {}).get('participants') or [])]
            names = {norm(x) for x in labels + nested if x}
            if wanted & names:
                kept.append({'id': m.get('id'), 'start': m.get('startTime'), 'type': m.get('type'),
                             'status': m.get('status'), 'best_of': m.get('bestOfX'),
                             'participants': labels, 'parent_id': m.get('parentId'),
                             'parent_participants': nested,
                             'special': (m.get('special') or {}).get('description')})
        per_league.append({'league': name, 'id': league['id'], 'status': 'ok',
                           'matchups_total': len(matchups), 'kept': len(kept),
                           'observed_at': receipt.get('observed_at'), 'sha256': receipt.get('sha256')})
        for item in kept:
            item['league'] = name
            item['league_id'] = league['id']
            hits.append(item)
    return {'leagues_receipt': leagues_receipt, 'cs2_leagues': per_league, 'hits': hits}


def related_markets(src, matchup_id, label):
    """Straight markets attached to one matchup, with the period-0 series moneyline picked out."""
    markets, receipt = src.get('Pinnacle straight markets %s' % label,
                               '%s/matchups/%s/markets/related/straight' % (PIN, matchup_id))
    series = []
    for mk in markets:
        if mk.get('period') in (0, 1) and mk.get('type') == 'moneyline' and not mk.get('isAlternate'):
            prices = mk.get('prices') or []
            if len(prices) != 2 or {p.get('designation') for p in prices} != {'home', 'away'}:
                continue
            values = {p['designation']: p['price'] for p in prices}
            odds = [('home', american(values['home'])), ('away', american(values['away']))]
            probs, margin = devig([o[1] for o in odds])
            series.append({'period': mk.get('period'), 'period_meaning': 'whole series' if mk.get('period') == 0 else 'map 1',
                           'key': mk.get('key'), 'status': mk.get('status'), 'cutoffAt': mk.get('cutoffAt'),
                           'american': {'home': values['home'], 'away': values['away']},
                           'decimal': {'home': round(odds[0][1], 4), 'away': round(odds[1][1], 4)},
                           'probabilities': {'home': round(probs[0], 6), 'away': round(probs[1], 6)},
                           'overround': round(margin, 6), 'version': mk.get('version')})
    return {'markets': markets, 'receipt': receipt, 'series_moneylines': series}


def book_probes(src, needles):
    """Record what each named esportsbook answers server-side, without bypassing anything."""
    out = []
    lowered = [n.lower() for n in needles]
    for label, url in BOOK_PROBES:
        try:
            page, receipt = src.get(label, url, False)
            found = sorted({n for n in lowered if n in page.lower()})
            out.append({'label': label, 'url': url, 'status': 'ok', 'http_status': receipt.get('http_status'),
                        'observed_at': receipt.get('observed_at'), 'sha256': receipt.get('sha256'),
                        'bytes': receipt.get('bytes'), 'team_labels_present': found,
                        'numeric_two_way': False,
                        'note': 'Team labels in server-side HTML only. No two-sided numeric series line is '
                                'extracted here, so this is not a price and never becomes one.' if found else
                                'No team label server-side.'})
        except Exception as exc:  # noqa: BLE001 - blocked source is a finding, not a crash
            record = next((r for r in src.log if r.get('url') == url), {})
            out.append({'label': label, 'url': url, 'status': 'error', 'error': str(exc)[:220],
                        'http_status': record.get('http_status'), 'observed_at': record.get('checked_at')})
    return out


def hltv_pages(src):
    pages = {}
    for label, url in HLTV_PAGES:
        try:
            page, receipt = src.get(label, url, False)
            pages[label] = {'url': url, 'status': 'ok', 'http_status': receipt.get('http_status'),
                            'observed_at': receipt.get('observed_at'), 'sha256': receipt.get('sha256'),
                            'bytes': receipt.get('bytes'), 'text': page}
        except Exception as exc:  # noqa: BLE001
            record = next((r for r in src.log if r.get('url') == url), {})
            pages[label] = {'url': url, 'status': 'error', 'error': str(exc)[:220],
                            'http_status': record.get('http_status'), 'observed_at': record.get('checked_at')}
    return pages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-76712ccc')
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    src = Sources(started)
    report = {'started_at': iso(started), 'steps': []}

    def step(name, fn, path=None, body=None):
        try:
            value = fn()
        except Exception as exc:  # noqa: BLE001 - a blocked source is a finding, not a crash
            report['steps'].append({'step': name, 'status': 'error', 'error': str(exc)[:400],
                                    'checked_at': now_iso()})
            return None
        record = {'step': name, 'status': 'ok', 'error': None, 'checked_at': now_iso()}
        if body is not None:
            target = out / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(body, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
            record['file'] = str(target)
        report['steps'].append(record)
        return value

    snapshot_path = Path(args.snapshot)
    snapshot = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else {'matches': []}
    ledger = step('compact open ledger', lambda: compact_ledger(snapshot), 'ledger.json',
                  body=compact_ledger(snapshot))

    # Every team label on the board, so the Pinnacle sweep is not limited to the rows
    # that are currently unpriced (a later refresh can change which ones those are).
    tokens = []
    for row in ledger['rows']:
        if row['state'] == 'open':
            tokens += list(row['teams'])
    tokens += ['FURIA', 'Aurora', 'Falcons', 'BETBOOM', 'BB Team', 'Legacy', '9z', 'PARIVISION',
               'Ninjas in Pyjamas', 'Heroic']

    sweep = step('Pinnacle CS2 league sweep', lambda: pinnacle_cs2_sweep(src, tokens), 'pinnacle-sweep.json',
                 body=None)
    if sweep:
        step('write Pinnacle sweep', lambda: (out / 'pinnacle-sweep.json').write_text(
            json.dumps(sweep, indent=1, ensure_ascii=False, sort_keys=True) + '\n'), None)

    # Full straight-market read for the sports/12 feed is retained in the production
    # snapshot; here only the leagues that touch our label set are read in full.
    pinned = {}
    for league in (sweep or {}).get('cs2_leagues', []):
        if league.get('status') != 'ok' or not league.get('kept'):
            continue
        try:
            markets, receipt = src.get('Pinnacle league markets ' + league['league'],
                                       '%s/leagues/%s/markets/straight' % (PIN, league['id']))
            pinned[league['league']] = {'league_id': league['id'], 'receipt': receipt,
                                        'moneyline_count': sum(1 for m in markets if m.get('type') == 'moneyline'),
                                        'markets': [m for m in markets if m.get('type') == 'moneyline'
                                                    and m.get('period') in (0, 1) and not m.get('isAlternate')]}
        except Exception as exc:  # noqa: BLE001
            pinned[league['league']] = {'league_id': league['id'], 'error': str(exc)[:200]}
    step('write Pinnacle league moneylines', lambda: (out / 'pinnacle-league-moneylines.json').write_text(
        json.dumps(pinned, indent=1, ensure_ascii=False, sort_keys=True) + '\n'), None)

    # TWC playoffs: read the two semi-final parents plus any other matchup the league lists.
    twc = {'league_id': TWC_PINNACLE_LEAGUE, 'parent_hints': list(TWC_PARENT_HINTS)}
    try:
        matchups, receipt = src.get('Pinnacle TWC matchups', '%s/leagues/%s/matchups' % (PIN, TWC_PINNACLE_LEAGUE))
        twc['matchups_receipt'] = receipt
        parents = {}
        for m in matchups:
            parent = (m.get('parent') or {}).get('id') or (m.get('id') if m.get('type') == 'matchup' else None)
            if parent:
                parents[str(parent)] = (m.get('parent') or {}).get('participants') or m.get('participants')
        twc['parents'] = {k: [p.get('name') for p in v] for k, v in parents.items()}
        markets = {}
        for parent_id in sorted(set(list(parents) + [str(x) for x in TWC_PARENT_HINTS]), key=str):
            try:
                result = related_markets(src, parent_id, 'TWC %s' % parent_id)
                markets[str(parent_id)] = {
                    'teams': [p.get('name') for p in ((parents.get(str(parent_id))) or [])],
                    'receipt': result['receipt'], 'moneyline_count': len(result['markets']),
                    'series_moneylines': result['series_moneylines'],
                    'series_period0': [x for x in result['series_moneylines'] if x['period'] == 0],
                    'raw': result['markets'],
                }
            except Exception as exc:  # noqa: BLE001
                markets[str(parent_id)] = {'error': str(exc)[:200]}
        twc['parents_markets'] = markets
    except Exception as exc:  # noqa: BLE001
        twc['error'] = str(exc)[:300]
    step('write Pinnacle TWC markets', lambda: (out / 'pinnacle-twc.json').write_text(
        json.dumps(twc, indent=1, ensure_ascii=False, sort_keys=True) + '\n'), None)

    # Polymarket: the same enumeration the production refresh performs.
    try:
        sports, sports_receipt = src.get('Polymarket sports registry', GAMMA + '/sports')
        cs2 = [s for s in sports if s.get('sport') == 'cs2']
        events, page_receipts = [], []
        for offset in range(0, 2000, 100):
            params = urlencode({'series_id': cs2[0]['series'], 'active': 'true', 'closed': 'false',
                                'end_date_min': started.strftime('%Y-%m-%dT00:00:00Z'), 'limit': 100,
                                'offset': offset, 'order': 'id', 'ascending': 'true'})
            batch, page_receipt = src.get('Polymarket events page %d' % (offset // 100 + 1),
                                          GAMMA + '/events?' + params)
            page_receipts.append(page_receipt)
            if not isinstance(batch, list):
                raise ValueError('Unexpected Polymarket pagination schema')
            for event in batch:
                events.append({'id': event.get('id'), 'slug': event.get('slug'), 'title': event.get('title'),
                               'markets': [{'id': mk.get('id'), 'question': mk.get('question'),
                                            'outcomes': mk.get('outcomes'), 'outcomePrices': mk.get('outcomePrices'),
                                            'bestBid': mk.get('bestBid'), 'bestAsk': mk.get('bestAsk'),
                                            'spread': mk.get('spread'), 'liquidityNum': mk.get('liquidityNum'),
                                            'acceptingOrders': mk.get('acceptingOrders'),
                                            'gameStartTime': mk.get('gameStartTime'),
                                            'updatedAt': mk.get('updatedAt'),
                                            'api_url': GAMMA + '/markets/' + str(mk.get('id'))}
                                           for mk in event.get('markets') or []]})
            if len(batch) < 100:
                break
        polymarket = {'registry_receipt': sports_receipt, 'page_receipts': page_receipts,
                      'events_total': len(events), 'events': events,
                      'wanted_labels_present': sorted({t for t in tokens
                                                       if any(norm(t) in {norm(x) for x in
                                                                          (json.loads(mk['outcomes'])
                                                                           if isinstance(mk['outcomes'], str)
                                                                           else mk['outcomes'] or [])}
                                                              for e in events for mk in e['markets'])}),
                      'observed_at': now_iso()}
        step('write Polymarket CS2 events', lambda: (out / 'polymarket-cs2-scan.json').write_text(
            json.dumps(polymarket, indent=1, ensure_ascii=False, sort_keys=True) + '\n'), None)
    except Exception as exc:  # noqa: BLE001
        report['steps'].append({'step': 'Polymarket CS2 events', 'status': 'error', 'error': str(exc)[:300],
                                'checked_at': now_iso()})

    hltv = step('HLTV pages', lambda: hltv_pages(src))
    if hltv:
        from bs4 import BeautifulSoup
        steps = []
        # Both the schedule (upcoming) and the results (played) pages list the event's
        # match pages, so every TWC 2026 series is read rather than only the next one.
        for label in ('HLTV TWC schedule', 'HLTV TWC results'):
            page = hltv.get(label)
            if not page or page.get('status') != 'ok':
                continue
            soup = BeautifulSoup(page['text'], 'html.parser')
            for link in soup.select('a[href*="/matches/"]'):
                url = link.get('href') or ''
                if url.startswith('/matches/') and 'thunderpick' in url:
                    steps.append({'url': 'https://www.hltv.org' + url})
        # Match pages for every open row that still carries no percentage, so the
        # identity evidence behind an unresolved row is retained too.
        for row in (ledger.get('open_unpriced') or []):
            url = row.get('hltv_url')
            if url and 'hltv.org/matches/' in url:
                steps.append({'url': url})
        seen = set()
        for link in steps:
            url = link['url']
            if url in seen:
                continue
            seen.add(url)
            match_id = url.split('/matches/')[1].split('/')[0]
            try:
                page, receipt = src.get('HLTV match ' + match_id, url, False)
                (out / ('hltv-%s.html' % match_id)).write_text(page)
                report['steps'].append({'step': 'HLTV match %s' % match_id, 'status': 'ok', 'error': None,
                                        'checked_at': now_iso(), 'file': str(out / ('hltv-%s.html' % match_id)),
                                        'url': url, 'sha256': receipt.get('sha256')})
            except Exception as exc:  # noqa: BLE001
                report['steps'].append({'step': 'HLTV match %s' % match_id, 'status': 'error',
                                        'error': str(exc)[:200], 'checked_at': now_iso(), 'url': url})
        for label, page in hltv.items():
            if page.get('status') == 'ok':
                (out / (''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in label) + '.html')).write_text(page['text'])

    probes = step('esportsbook probes', lambda: book_probes(src, tokens), 'book-probes.json')
    if probes is not None:
        step('write esportsbook probes', lambda: (out / 'book-probes.json').write_text(
            json.dumps(probes, indent=1, ensure_ascii=False, sort_keys=True) + '\n'), None)

    # Hotspawn fixture inventory as read in this same run, for parity checking.
    try:
        fixtures, receipt = src.get('Hotspawn CS2 fixtures (probe)', FIXTURES)
        step('write Hotspawn fixture inventory', lambda: (out / 'hotspawn-fixtures.json').write_text(
            json.dumps({'receipt': receipt, 'count': len(fixtures), 'ids': sorted(str(f.get('id')) for f in fixtures)},
                       indent=1, sort_keys=True) + '\n'), None)
    except Exception as exc:  # noqa: BLE001
        report['steps'].append({'step': 'Hotspawn CS2 fixtures (probe)', 'status': 'error',
                                'error': str(exc)[:300], 'checked_at': now_iso()})

    copied = archive_raw(src, out, None)
    step('write raw archive index', lambda: (out / 'raw-index.json').write_text(
        json.dumps(copied, indent=1, ensure_ascii=False, sort_keys=True) + '\n'), None)

    report['source_log'] = src.log
    report['finished_at'] = now_iso()
    (out / 'probe-report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    ok = sum(1 for s in report['steps'] if s['status'] == 'ok')
    print('probe 76712ccc: %d ok / %d steps, %d raw bodies archived -> %s'
          % (ok, len(report['steps']), len(copied), out))


if __name__ == '__main__':
    main()
