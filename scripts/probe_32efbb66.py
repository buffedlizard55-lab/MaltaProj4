"""Session 32efbb66 measurement probe (non-publishing).

Measures, on the runner's egress and through the production ``Sources``
reader (same headers, rate-limit waits, evidence log):

* Kalshi's public no-auth market-data API for the CS2 match-winner series
  ``KXCS2GAME`` — how its open markets encode team names, start times and
  two-sided prices, and how many of the fresh snapshot's open fixtures they
  cover under the project's exact pair + exact UTC start rule.
* SX Bet's documented no-key API — whether an esports/CS2 sport exists, how
  many type-52 (12/moneyline) markets are active, and whether any covers an
  open fixture with a two-sided book.
* HLTV team pages — whether recent completed results are published there in
  parseable markup (the production ``past_results`` parser only reads match
  pages, so a fixture HLTV has no match page for cannot reach the form tier).
* The Thunderpick shell page — any API URL it names (discovery only; BO3.gg
  already relays Thunderpick lines, so no speculative endpoint guessing).

Nothing here prices anything. It writes a JSON report plus bounded raw
samples under ``research/session-32efbb66/`` so any adapter written from it
is built against measured bytes, and prints a rung report for the snapshot.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

from scripts.core import dt, orientation, norm
from scripts.refresh import Sources
from scripts import hltv

KALSHI = 'https://api.elections.kalshi.com/trade-api/v2'
SX = 'https://api.sx.bet'
OUT = Path('research/session-32efbb66')


def sample_keys(rows):
    keys = set()
    for row in rows[:50]:
        if isinstance(row, dict):
            keys |= set(row)
    return sorted(keys)


def rung_report(snapshot):
    lines = ['# Rung report — session 32efbb66 fresh capture', '']
    lines.append('generated_at: `%s` · coverage: `%s` · feed rows: %d'
                 % (snapshot.get('generated_at'), snapshot.get('coverage'), len(snapshot['matches'])))
    opens = [m for m in snapshot['matches'] if m['state'] == 'open']
    lines += ['', '## Open rows (%d)' % len(opens), '']
    for m in opens:
        lines.append('### %s — %s vs %s (%s, %s)' % (m['id'], m['teams'][0], m['teams'][1], m['competition'], m['start']))
        lines.append('- pick: `%s` · method: `%s` · probabilities: `%s`'
                     % (m.get('pick'), m.get('method'), m.get('probabilities')))
        for a in m.get('attempts', []):
            lines.append('  - %s | %s | %s' % (a.get('provider'), a.get('status'), str(a.get('reason'))[:200]))
        lines.append('')
    return '\n'.join(lines) + '\n', opens


def probe_kalshi(src, opens, report):
    section = {'series_ticker': 'KXCS2GAME'}
    try:
        status, _ = src.get('Kalshi exchange status', KALSHI + '/exchange/status')
        section['exchange_status'] = status
    except ValueError as e:
        section['exchange_status_error'] = str(e)[:300]
        report['kalshi'] = section
        return
    markets, cursor = [], None
    for _page in range(5):
        url = KALSHI + '/markets?series_ticker=KXCS2GAME&status=open&limit=1000'
        if cursor:
            url += '&cursor=' + quote(cursor, safe='')
        try:
            body, receipt = src.get('Kalshi KXCS2GAME markets', url)
        except ValueError as e:
            section['markets_error'] = str(e)[:300]
            break
        batch = body.get('markets') if isinstance(body, dict) else None
        if not isinstance(batch, list):
            section['markets_error'] = 'Unexpected schema: %r' % type(body)
            break
        markets += batch
        cursor = body.get('cursor') or None
        section['observed_at'] = receipt['observed_at']
        if not cursor:
            break
    section['open_markets'] = len(markets)
    section['keys'] = sample_keys(markets)
    section['samples'] = markets[:3]
    # Group by event; a match event should hold one binary market per team.
    events = {}
    for mk in markets:
        events.setdefault(mk.get('event_ticker'), []).append(mk)
    section['open_events'] = len(events)
    section['markets_per_event'] = sorted({len(v) for v in events.values()})
    Path(OUT / 'kalshi-markets.json').write_text(json.dumps(markets, indent=1)[:2_000_000])
    # Exact-identity join: team labels must be discoverable in the market
    # record itself; record which fields carry them and the start field.
    joins = []
    for m in opens:
        joins.append({'fixture_id': m['id'], 'teams': m['teams'], 'start': m['start'],
                      'candidates': []})
    for event_ticker, mks in events.items():
        if len(mks) != 2:
            continue
        labels = []
        for mk in mks:
            label = mk.get('yes_sub_title') or mk.get('subtitle') or mk.get('title') or ''
            labels.append(str(label))
        starts = {mk.get('expected_expiration_time') for mk in mks}
        for j, m in zip(joins, opens):
            for start in starts:
                if start and orientation(m, labels, start) is not None:
                    j['candidates'].append({'event_ticker': event_ticker, 'labels': labels,
                                            'start_field': start})
    section['joins_by_subtitle_and_expected_expiration'] = joins
    report['kalshi'] = section


def probe_sx(src, opens, report):
    section = {}
    try:
        sports, _ = src.get('SX Bet sports', SX + '/sports')
    except ValueError as e:
        section['sports_error'] = str(e)[:300]
        report['sx'] = section
        return
    rows = sports.get('data') if isinstance(sports, dict) else sports
    section['sports'] = rows if isinstance(rows, list) else str(type(rows))
    esport_ids = [s.get('sportId') for s in (rows or [])
                  if isinstance(s, dict) and re.search(r'esport|counter|cs2|strike', str(s.get('label') or s.get('name') or ''), re.I)]
    section['esport_sport_ids'] = esport_ids
    markets = []
    for sid in esport_ids:
        try:
            body, receipt = src.get('SX Bet active markets', SX + '/markets/active?sportIds=%s&onlyMainLine=true' % sid)
            batch = (body.get('data') or {}).get('markets') if isinstance(body, dict) else None
            section.setdefault('observed_at', receipt['observed_at'])
            if isinstance(batch, list):
                markets += batch
            else:
                section['markets_shape_%s' % sid] = str(body)[:400]
        except ValueError as e:
            section['markets_error_%s' % sid] = str(e)[:300]
    section['active_markets'] = len(markets)
    section['keys'] = sample_keys(markets)
    section['types'] = sorted({m.get('type') for m in markets if isinstance(m, dict)}, key=str)
    section['samples'] = markets[:3]
    Path(OUT / 'sx-markets.json').write_text(json.dumps(markets, indent=1)[:2_000_000])
    joins = []
    for m in opens:
        hits = []
        for mk in markets:
            teams = [mk.get('teamOneName'), mk.get('teamTwoName')]
            game = mk.get('gameTime')
            if None in teams or game is None:
                continue
            try:
                start = datetime.fromtimestamp(float(game), timezone.utc).isoformat()
            except (TypeError, ValueError, OSError, OverflowError):
                continue
            if orientation(m, teams, start) is not None:
                hits.append({'marketHash': mk.get('marketHash'), 'type': mk.get('type'),
                             'teams': teams, 'start': start, 'status': mk.get('status')})
        joins.append({'fixture_id': m['id'], 'teams': m['teams'], 'start': m['start'], 'candidates': hits})
    section['joins'] = joins
    hashes = [h['marketHash'] for j in joins for h in j['candidates'] if h.get('marketHash')][:10]
    if hashes:
        try:
            body, _ = src.get('SX Bet orders', SX + '/orders?marketHashes=' + ','.join(hashes))
            orders = (body.get('data') or {}).get('orders') if isinstance(body, dict) else None
            section['orders_for_joined'] = {'count': len(orders or []), 'samples': (orders or [])[:4],
                                            'keys': sample_keys(orders or [])}
        except ValueError as e:
            section['orders_error'] = str(e)[:300]
    report['sx'] = section


RESULT_HINT = re.compile(r'result|past-match|recent', re.I)


def probe_hltv_team_pages(src, opens, report):
    section = {'teams': []}
    # Fixtures whose pick is weakest first: no pick, then research-only, then
    # model; plus at most two priced controls. Bounded page budget.
    ranked = sorted(opens, key=lambda m: (0 if not m.get('pick') else
                                           1 if m['probabilities'] is None else
                                           2 if m.get('method') == 'model_vrs' else 3))
    budget = 20
    seen = set()
    for m in ranked:
        for team in m['teams']:
            if budget <= 0 or norm(team) in seen:
                continue
            seen.add(norm(team))
            budget -= 1
            row = {'fixture_id': m['id'], 'team': team}
            try:
                stored = next((r for r in (m.get('hltv_team_pages') or {}).get('teams', [])
                               if norm(r.get('team') or '') == norm(team)), None)
                if stored and stored.get('url'):
                    url = stored['url']
                else:
                    listing, _ = src.get('HLTV team search ' + team, hltv.SEARCH + quote(team), False)
                    candidates = {u: l for u, l in hltv.search_teams(listing).items() if norm(l) == norm(team)}
                    if len(candidates) != 1:
                        row['error'] = '%d exact-label team pages' % len(candidates)
                        section['teams'].append(row)
                        continue
                    url = next(iter(candidates))
                page, receipt = src.get('HLTV team page ' + team, url, False)
                row['url'], row['observed_at'] = url, receipt['observed_at']
                soup = BeautifulSoup(page, 'html.parser')
                row['profile'] = hltv.team_profile(page, team)
                row['match_page_parser_on_team_page'] = hltv.past_results(soup)
                classes = {}
                for el in soup.find_all(True):
                    for cls in el.get('class') or []:
                        if RESULT_HINT.search(cls):
                            classes[cls] = classes.get(cls, 0) + 1
                row['resultish_classes'] = dict(sorted(classes.items(), key=lambda kv: -kv[1])[:40])
                snippets = {}
                for cls in list(classes)[:6]:
                    el = soup.select_one('.' + re.escape(cls).replace('\\ ', ' '))
                    if el is not None:
                        snippets[cls] = str(el)[:6000]
                row['snippets'] = snippets
                slug = re.sub(r'[^a-z0-9]+', '-', norm(team))[:40] or 'team'
                (OUT / ('hltv-team-%s.html' % slug)).write_text(page[:400_000])
            except ValueError as e:
                row['error'] = str(e)[:300]
            section['teams'].append(row)
    report['hltv_team_pages'] = section


def probe_thunderpick_shell(src, report):
    section = {}
    try:
        page, receipt = src.get('Thunderpick CS2 shell', 'https://thunderpick.io/esports/cs2-betting', False)
        section['observed_at'] = receipt['observed_at']
        urls = sorted(set(re.findall(r'https://[A-Za-z0-9._~:/?#\[\]@!$&()*+,;=%-]+', page)))
        section['api_like_urls'] = [u for u in urls if 'api' in u][:60]
        section['relative_api_paths'] = sorted(set(re.findall(r'["\'](/api/[^"\']{1,120})["\']', page)))[:60]
        section['shell_bytes'] = len(page)
    except ValueError as e:
        section['error'] = str(e)[:300]
    report['thunderpick_shell'] = section


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='research/session-32efbb66/snapshot.json')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    snapshot = json.loads(Path(args.snapshot).read_text())
    rungs, opens = rung_report(snapshot)
    (OUT / 'rungs.md').write_text(rungs)
    src = Sources(datetime.now(timezone.utc))
    report = {'probed_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
              'snapshot_generated_at': snapshot.get('generated_at'),
              'open_fixtures': [{'id': m['id'], 'teams': m['teams'], 'start': m['start'],
                                 'pick': m.get('pick'), 'method': m.get('method')} for m in opens]}
    probe_kalshi(src, opens, report)
    probe_sx(src, opens, report)
    probe_hltv_team_pages(src, opens, report)
    probe_thunderpick_shell(src, report)
    report['source_log'] = src.log
    (OUT / 'probe-report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False)[:8_000_000] + '\n')
    print(json.dumps({
        'open': len(opens),
        'open_without_pick': sum(1 for m in opens if not m.get('pick')),
        'kalshi_open_markets': report['kalshi'].get('open_markets'),
        'kalshi_open_events': report['kalshi'].get('open_events'),
        'kalshi_joined_fixtures': sum(1 for j in report['kalshi'].get(
            'joins_by_subtitle_and_expected_expiration', []) if j['candidates']),
        'sx_active_markets': report['sx'].get('active_markets'),
        'sx_joined_fixtures': sum(1 for j in report['sx'].get('joins', []) if j['candidates']),
        'hltv_team_pages_read': sum(1 for r in report['hltv_team_pages']['teams'] if 'url' in r),
    }))


if __name__ == '__main__':
    main()
