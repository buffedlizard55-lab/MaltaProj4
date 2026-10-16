"""Live-evidence probe for session 621776e4 (research only, never publishes).

Why this exists
---------------
The authoring sandbox reaches GitHub and package registries only, so every
external line quoted in this session's analysis has to be *retrieved*, not
recalled. This script runs on a GitHub Actions runner with normal outbound
access and writes the raw, dated evidence into ``research/harvest-621776e4/``
so that each number published in the day-4 analysis can be re-checked
line-by-line against the response it came from.

What it does
------------
1. Summarises the open rows of a snapshot produced by ``scripts.refresh`` into
   a compact ledger (id, teams, competition, start, pick, probabilities,
   method) so the priced/unpriced split is readable without the full JSON.
2. Dumps the trimmed active Polymarket CS2 event list (event slug, market id,
   question, outcomes, prices, bid/ask, liquidity, spread, timestamps).
3. Dumps Pinnacle esports matchups and moneylines restricted to the team
   names that appear on our open rows plus the Thunderpick World Championship
   participants.
4. Reads HLTV: the event results page for the Thunderpick World Championship,
   the upcoming-match list, and - for the playoff fixtures and every open row
   that still has no probability - the match page itself, extracting the odds
   comparison table (bookmaker, two decimal odds, bookmaker link), the series
   format, the machine-readable clock, world-ranking badges and lineups.
5. Re-observes the EGamersWorld book listings already recorded in
   ``data/book-receipts.json`` and probes the other esportsbook endpoints the
   project has named, recording HTTP status rather than guessing.

Every step is individually guarded: a source that refuses access is recorded
as a limitation with its status code, never silently skipped and never
presented as "no odds available".
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from scripts.core import FIXTURES, GAMMA, PIN, dt, iso, norm
from scripts.refresh import Sources

HLTV = 'https://www.hltv.org'
# Thunderpick World Championship 2026 (HLTV event 8932) playoff fixtures, whose
# pages are read here so the day-4 analysis quotes retrieved evidence.
TWC_EVENT = 8932
BOOK_PROBES = (
    ('GG.BET CS2 page', 'https://gg.bet/en/esports/counter-strike'),
    ('Thunderpick CS2 page', 'https://thunderpick.io/esports/cs2-betting'),
    ('Rivalry CS2 page', 'https://www.rivalry.com/esports/counter-strike'),
    ('EGamersWorld CS2 matches', 'https://egamersworld.com/counterstrike/matches'),
)
DECIMAL = re.compile(r'^\d{1,3}\.\d{1,3}$')


def now_iso():
    return iso(datetime.now(timezone.utc))


def compact_ledger(snapshot):
    """One line per row, priced first, with everything needed to re-derive it."""
    rows = []
    for m in snapshot.get('matches') or []:
        rows.append({
            'id': m['id'],
            'teams': m['teams'],
            'competition': m['competition'],
            'start': m['start'],
            'lock': m.get('lock'),
            'state': m['state'],
            'pick': m.get('pick'),
            'probabilities': m.get('probabilities'),
            'fair_odds': m.get('fair_odds'),
            'method': m.get('method'),
            'best_of': m.get('best_of'),
            'expires_at': m.get('expires_at'),
            'hltv_url': (m.get('hltv_context') or {}).get('source'),
            'hltv_betting_rows': (m.get('hltv_context') or {}).get('numeric_quote_rows'),
            'attempt_providers': [a.get('provider') for a in m.get('attempts') or []],
        })
    open_rows = [r for r in rows if r['state'] == 'open']
    unpriced = [r for r in open_rows if r['probabilities'] is None]
    return {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'coverage': snapshot.get('coverage'),
        'rows_total': len(rows),
        'rows_open': len(open_rows),
        'rows_open_priced': len(open_rows) - len(unpriced),
        'rows_open_unpriced': len(unpriced),
        'rows_open_pick_no_percentage': [r['id'] for r in unpriced if r['pick']],
        'rows_open_no_pick': [r['id'] for r in unpriced if not r['pick']],
        'unpriced': unpriced,
        'rows': rows,
    }


def trim_polymarket(src, now):
    sports, receipt = src.get('Polymarket sports registry', GAMMA + '/sports')
    cs2 = [s for s in sports if s.get('sport') == 'cs2']
    if len(cs2) != 1:
        raise ValueError('CS2 registry is ambiguous or absent')
    events, pages = [], []
    seen = set()
    for offset in range(0, 5000, 100):
        params = urlencode({'series_id': cs2[0]['series'], 'active': 'true', 'closed': 'false',
                            'end_date_min': now.strftime('%Y-%m-%dT00:00:00Z'), 'limit': 100,
                            'offset': offset, 'order': 'id', 'ascending': 'true'})
        batch, page_receipt = src.get('Polymarket events page %d' % (offset // 100 + 1), GAMMA + '/events?' + params)
        pages.append(page_receipt)
        if not isinstance(batch, list):
            raise ValueError('Unexpected Polymarket pagination schema')
        if {str(e['id']) for e in batch} & seen:
            raise ValueError('Repeated exchange event page')
        seen |= {str(e['id']) for e in batch}
        for event in batch:
            series = event.get('series')
            if isinstance(series, list):
                series = ', '.join(str((s or {}).get('title')) for s in series if isinstance(s, dict))
            elif isinstance(series, dict):
                series = series.get('title')
            events.append({
                'id': event.get('id'),
                'slug': event.get('slug'),
                'title': event.get('title'),
                'series': series,
                'markets': [{
                    'id': mk.get('id'),
                    'question': mk.get('question'),
                    'slug': mk.get('slug'),
                    'outcomes': mk.get('outcomes'),
                    'outcomePrices': mk.get('outcomePrices'),
                    'bestBid': mk.get('bestBid'),
                    'bestAsk': mk.get('bestAsk'),
                    'lastTradePrice': mk.get('lastTradePrice'),
                    'liquidity': mk.get('liquidity'),
                    'liquidityNum': mk.get('liquidityNum'),
                    'spread': mk.get('spread'),
                    'active': mk.get('active'),
                    'closed': mk.get('closed'),
                    'acceptingOrders': mk.get('acceptingOrders'),
                    'gameStartTime': mk.get('gameStartTime'),
                    'updatedAt': mk.get('updatedAt'),
                    'startDate': mk.get('startDate'),
                    'endDate': mk.get('endDate'),
                    'api_url': GAMMA + '/markets/' + str(mk.get('id')),
                } for mk in event.get('markets') or []],
            })
        if len(batch) < 100:
            break
    return {'registry_receipt': receipt, 'page_receipts': pages, 'events': events}


def trim_pinnacle(src, tokens):
    matchups, mr = src.get('Pinnacle esports fixtures', PIN + '/sports/12/matchups?withSpecials=false')
    lines, lr = src.get('Pinnacle esports moneylines', PIN + '/sports/12/markets/straight')
    wanted = {norm(t) for t in tokens if t}

    def keep(matchup):
        names = [norm(p.get('name') or '') for p in matchup.get('participants') or []]
        return bool(wanted & set(names))

    kept = [m for m in matchups if keep(m)]
    kept_ids = {m.get('id') for m in kept}
    kept_lines = [l for l in lines if l.get('matchupId') in kept_ids]
    return {'matchup_receipt': mr, 'line_receipt': lr,
            'matchups_total': len(matchups), 'lines_total': len(lines),
            'matchups': kept, 'lines': kept_lines}


def hltv_betting_table(html):
    """The odds-comparison rows exactly as HLTV lists them, with the book link."""
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    for row in soup.select('.match-betting-list tr.provider'):
        cells = row.find_all('td', recursive=False)
        if len(cells) < 3:
            continue
        values = [c.get_text(' ', strip=True) for c in cells]
        odds = [v for v in values[1:] if DECIMAL.fullmatch(v)]
        if len(odds) != 2:
            continue
        anchor = cells[0].select_one('a[href]')
        rows.append({
            'bookmaker': cells[0].get_text(' ', strip=True) or (anchor.get('title') if anchor else None),
            'bookmaker_href': (HLTV + anchor['href']) if anchor and anchor['href'].startswith('/') else (anchor['href'] if anchor else None),
            'odds': [float(v) for v in odds],
        })
    return rows


def hltv_match(src, url, label):
    page, receipt = src.get(label, url, False)
    soup = BeautifulSoup(page, 'html.parser')
    clock = soup.select_one('.timeAndEvent .time[data-unix]')
    teams = [t.get_text(strip=True) for t in soup.select('.team1-gradient .teamName, .team2-gradient .teamName')]
    info = soup.select_one('.timeAndEvent .preformatted-text, .timeAndEvent .pad')
    ranks = []
    for el in soup.select('.teamRanking'):
        team = el.parent.select_one('a[href^="/team/"]')
        rank = el.select_one('.hltv-ranking')
        vrs = el.select_one('a.vrs-ranking')
        match = re.search(r'#(\d+)', rank.get_text()) if rank else None
        vrs_match = re.search(r'#(\d+)', vrs.get_text()) if vrs else None
        badge = el.select_one('.ranking-badge.unranked')
        ranks.append({'team': team.get_text(strip=True) if team else None,
                      'team_href': (HLTV + team['href']) if team and team['href'].startswith('/') else None,
                      'hltv_rank': int(match.group(1)) if match else None,
                      'unranked_badge': bool(badge is not None and 'unranked' in badge.get_text().casefold()),
                      'vrs_rank': int(vrs_match.group(1)) if vrs_match else None})
    lineups = []
    for box in soup.select('div.lineups div.lineup'):
        head = box.select_one('.box-headline a[href^="/team/"]') or box.select_one('.box-headline .text-ellipsis')
        players = [p.get_text(strip=True) for p in box.select('td.player .player-compare .text-ellipsis')]
        if head is None or not players:
            continue
        lineups.append({'team': head.get_text(strip=True), 'players': list(dict.fromkeys(players))[:8]})
    return {
        'url': url,
        'observed_at': receipt['observed_at'],
        'retrieved_at': receipt['retrieved_at'],
        'http_status': receipt.get('http_status'),
        'sha256': receipt.get('sha256'),
        'displayed_clock': clock.get_text(' ', strip=True) if clock else None,
        'start_unix': clock['data-unix'] if clock is not None and clock.get('data-unix') else None,
        'start_utc': iso(clock['data-unix']) if clock is not None and clock.get('data-unix') else None,
        'teams': teams,
        'format': info.get_text(' ', strip=True) if info else None,
        'betting': hltv_betting_table(page),
        'ranks': ranks,
        'lineups': lineups,
    }


def hltv_results(src, event_id):
    url = HLTV + '/results?event=%d' % event_id
    page, receipt = src.get('HLTV results for event %d' % event_id, url, False)
    soup = BeautifulSoup(page, 'html.parser')
    days = []
    for section in soup.select('.result-con'):
        day = section.select_one('.standard-headline')
        results = []
        for row in section.select('a.a-reset'):
            teams = [t.get_text(strip=True) for t in row.select('.team')]
            score = row.select_one('.result-score')
            if len(teams) != 2 or score is None:
                continue
            results.append({'teams': teams, 'score': score.get_text(strip=True),
                            'map': (row.select_one('.map-text') or {}).get_text(strip=True) if row.select_one('.map-text') else None,
                            'url': HLTV + row['href']})
        if results:
            days.append({'date': day.get_text(' ', strip=True) if day else None, 'results': results})
    return {'url': url, 'observed_at': receipt['observed_at'], 'retrieved_at': receipt['retrieved_at'],
            'http_status': receipt.get('http_status'), 'days': days}


def hltv_upcoming(src):
    page, receipt = src.get('HLTV upcoming matches', HLTV + '/matches', False)
    soup = BeautifulSoup(page, 'html.parser')
    found = []
    for anchor in soup.select('a.match-teams[href^="/matches/"]'):
        teams = [t.get_text(strip=True) for t in anchor.select('.match-teamname')]
        stamp = anchor.parent.select_one('.match-time[data-unix]')
        if len(teams) != 2 or stamp is None:
            continue
        found.append({'teams': teams, 'start_unix': stamp['data-unix'], 'start_utc': iso(stamp['data-unix']),
                      'url': HLTV + anchor['href']})
    return {'url': HLTV + '/matches', 'observed_at': receipt['observed_at'],
            'retrieved_at': receipt['retrieved_at'], 'http_status': receipt.get('http_status'),
            'count': len(found), 'matches': found}


def hltv_event_matches(src, event_id):
    """Every fixture link on an event's schedule page, with its own slug.

    HLTV answers ``/matches/<id>`` with HTTP 404; the full slug is required, and
    a decider's slug changes once the qualifier is decided, so the slugs are
    read from the event page rather than assembled.
    """
    url = HLTV + '/events/%d/matches' % event_id
    page, receipt = src.get('HLTV event %d matches' % event_id, url, False)
    soup = BeautifulSoup(page, 'html.parser')
    links = []
    seen = set()
    for anchor in soup.select('a[href^="/matches/"]'):
        href = anchor['href'].split('?')[0]
        if href in seen or href.count('/') < 3:
            continue
        seen.add(href)
        links.append({'url': HLTV + href, 'text': re.sub(r'\s+', ' ', anchor.get_text(' ', strip=True))[:200]})
    return {'url': url, 'observed_at': receipt['observed_at'], 'retrieved_at': receipt['retrieved_at'],
            'http_status': receipt.get('http_status'), 'count': len(links), 'links': links}


def embedded_line_hunt(html, needles):
    """Server-side evidence of a price, or the finding that there is none.

    JavaScript-rendered sportsbooks serve a page with no decimal odds in the
    HTML. That is recorded as a retrieval limitation, not as "no odds offered".
    """
    text = re.sub(r'\s+', ' ', html)
    hits = []
    for needle in needles:
        for match in re.finditer(re.escape(needle), text):
            window = text[max(0, match.start() - 120):match.start() + 220]
            if re.search(r'\b\d\.\d{2}\b', window):
                hits.append({'needle': needle, 'window': window})
    return {'needle_hits': len(hits), 'windows': hits[:20],
            'decimal_odds_anywhere': bool(re.search(r'\b[1-9]\.\d{2}\b', text)),
            'bytes': len(html)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-621776e4')
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    src = Sources(started)
    report = {'started_at': iso(started), 'steps': []}

    def step(name, fn, path):
        try:
            value = fn()
        except Exception as exc:  # noqa: BLE001 - a blocked source is a finding, not a crash
            report['steps'].append({'step': name, 'status': 'error', 'error': str(exc)[:400], 'file': None,
                                    'checked_at': now_iso()})
            return None
        target = out / path
        target.write_text(json.dumps(value, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
        report['steps'].append({'step': name, 'status': 'ok', 'error': None, 'file': str(target),
                                'checked_at': now_iso()})
        return value

    snapshot = json.loads(Path(args.snapshot).read_text()) if Path(args.snapshot).exists() else None
    ledger = None
    if snapshot:
        ledger = step('compact open ledger', lambda: compact_ledger(snapshot), 'ledger.json')

    step('Polymarket active CS2 events', lambda: trim_polymarket(src, started), 'polymarket-active-cs2.json')

    tokens = []
    if ledger:
        for row in ledger['unpriced']:
            tokens += row['teams']
    tokens += ['FURIA', 'Aurora', 'Falcons', 'BETBOOM', 'Legacy', '9z', 'PARIVISION', 'Ninjas in Pyjamas']
    step('Pinnacle esports lines (filtered)', lambda: trim_pinnacle(src, tokens), 'pinnacle-esports.json')

    step('HLTV upcoming matches', lambda: hltv_upcoming(src), 'hltv-upcoming.json')
    step('HLTV Thunderpick WC results', lambda: hltv_results(src, TWC_EVENT), 'hltv-twc-results.json')

    # HLTV answers /matches/<id> with 404: the full slug is mandatory, and a
    # decider's slug changes once the qualifier is decided, so the playoff pages
    # are discovered from the event schedule rather than assembled from ids.
    event_page = step('HLTV event %d schedule' % TWC_EVENT, lambda: hltv_event_matches(src, TWC_EVENT),
                      'hltv-twc-schedule.json')
    if event_page:
        for link in event_page['links']:
            match_id = link['url'].split('/matches/')[-1].split('/')[0]
            step('HLTV match %s' % match_id, lambda u=link['url'], i=match_id: hltv_match(src, u, 'HLTV match %s' % i),
                 'hltv-twc-%s.json' % match_id)

    # Match pages for every open row that still carries no percentage: this is
    # the raw material for the HLTV odds-comparison book tier.
    if ledger:
        for row in ledger['unpriced']:
            url = row.get('hltv_url')
            if not url:
                continue
            step('HLTV unpriced row %s' % row['id'], lambda u=url, r=row: hltv_match(src, u, 'HLTV match for %s' % r['id']),
                 'hltv-unpriced-%s.json' % row['id'])

    # Book probes: record what each named esportsbook actually answers.
    needles = ['FURIA', 'Aurora', 'Falcons', 'BetBoom', 'BETBOOM', 'Legacy']
    probes = []
    for label, url in BOOK_PROBES:
        try:
            page, receipt = src.get(label, url, False)
            probes.append({'label': label, 'url': url, 'status': 'ok',
                           'http_status': receipt.get('http_status'), 'observed_at': receipt['observed_at'],
                           'sha256': receipt.get('sha256'),
                           'server_side_odds': embedded_line_hunt(page, needles)})
        except Exception as exc:  # noqa: BLE001
            record = next((r for r in src.log if r.get('url') == url), {})
            probes.append({'label': label, 'url': url, 'status': 'error',
                           'http_status': record.get('http_status'), 'error': str(exc)[:300],
                           'observed_at': record.get('observed_at')})
    # Re-observe the receipts already published so the eight-hour window is
    # re-established on every refresh instead of expiring by hand.
    receipts_path = Path('data/book-receipts.json')
    reobserved = []
    if receipts_path.exists():
        for receipt in json.loads(receipts_path.read_text()).get('receipts', []):
            url = receipt.get('url')
            if not url:
                continue
            try:
                page, record = src.get('Book listing %s' % receipt.get('id'), url, False)
                soup = BeautifulSoup(page, 'html.parser')
                numbers = [t.get_text(' ', strip=True) for t in soup.select('table td, .odds, [class*="odds"]')]
                decimals = [v for v in numbers if DECIMAL.fullmatch(v)]
                reobserved.append({'id': receipt.get('id'), 'fixture_id': receipt.get('fixture_id'),
                                   'url': url, 'status': 'ok', 'http_status': record.get('http_status'),
                                   'observed_at': record['observed_at'],
                                   'recorded_odds': receipt.get('odds'),
                                   'decimals_on_page': decimals[:20],
                                   'page_text_excerpt': re.sub(r'\s+', ' ', soup.get_text(' '))[:600]})
            except Exception as exc:  # noqa: BLE001
                record = next((r for r in src.log if r.get('url') == url), {})
                reobserved.append({'id': receipt.get('id'), 'fixture_id': receipt.get('fixture_id'), 'url': url,
                                   'status': 'error', 'http_status': record.get('http_status'),
                                   'error': str(exc)[:300]})
    (out / 'book-probes.json').write_text(json.dumps({'probes': probes, 'receipt_reobservations': reobserved},
                                                     indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    report['steps'].append({'step': 'book probes and receipt re-observation', 'status': 'ok',
                            'error': None, 'file': str(out / 'book-probes.json'), 'checked_at': now_iso()})

    report['finished_at'] = iso(datetime.now(timezone.utc))
    report['source_checks'] = src.log
    report['fixture_api'] = FIXTURES
    (out / 'probe-report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    print(json.dumps({'steps': [{k: s[k] for k in ('step', 'status', 'error')} for s in report['steps']],
                      'ledger': ({k: ledger[k] for k in ('rows_open', 'rows_open_priced', 'rows_open_unpriced',
                                                         'rows_open_pick_no_percentage', 'rows_open_no_pick')}
                                 if ledger else None)}, indent=1))


if __name__ == '__main__':
    main()
