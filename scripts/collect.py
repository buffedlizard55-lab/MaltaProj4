"""Public-source ingestion. No login, crowd-pick percentages, or invented observations."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/data'
LOBBY = 'https://play.hotspawn.com/cs2-pickems'
VALVE = 'https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings'
BOOKS = [
    ('HLTV', 'https://www.hltv.org/matches'),
    ('GG.BET', 'https://gg.bet/en/esports/counter-strike'),
    ('Thunderpick', 'https://thunderpick.io/esports/cs2'),
    ('Pinnacle', 'https://www.pinnacle.com/en/esports-hub/cs2'),
    ('Rivalry', 'https://www.rivalry.com/esports/counter-strike-betting'),
]


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_time(value):
    if value is None or value == '':
        return None
    if str(value).isdigit():
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc)
    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Unverified timezone')
    return dt.astimezone(timezone.utc)


def norm(name):
    # Do not remove academy, women, region, ex-, or gaming suffixes.
    return ' '.join(unicodedata.normalize('NFKC', name).casefold().split())


def pair_normalize(values):
    if len(values) != 2 or any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('Invalid two-sided prices')
    p = values[0] / sum(values)
    return [round(p, 6), round(1 - p, 6)]


def no_vig(odds):
    if any(not math.isfinite(o) or o <= 1 for o in odds):
        raise ValueError('Invalid decimal odds')
    return pair_normalize([1 / o for o in odds])


def rating_probability(points):
    # Our conservative model: published points, fixed RD=350 (not a measured team RD).
    # Valve's public Glicko expected-score function; deliberately not called bookmaker odds.
    q = math.log(10) / 400
    g = 1 / math.sqrt(1 + 3 * q * q * 350**2 / math.pi**2)
    p = 1 / (1 + 10 ** (g * (points[1] - points[0]) / 400))
    return [round(p, 6), round(1 - p, 6)]


class Client:
    def __init__(self, now):
        self.now = now
        self.audit = []
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'HotspawnCoverage/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'

    def get(self, url, label, raw=False):
        entry = {'name': label, 'url': url, 'checked_at': iso(self.now)}
        self.audit.append(entry)
        try:
            headers = {}
            if url.startswith('https://api.github.com/'):
                headers['Accept'] = 'application/vnd.github.raw+json' if raw else 'application/vnd.github+json'
                if os.environ.get('GH_TOKEN'):
                    headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
            r = self.session.get(url, timeout=35, headers=headers)
            entry['http_status'] = r.status_code
            entry['sha256'] = hashlib.sha256(r.content).hexdigest()
            r.raise_for_status()
            entry['status'] = 'retrieved'
            return r.text
        except requests.RequestException as exc:
            entry['status'] = 'unavailable'
            # No request headers or credentials are ever written to the public report.
            entry['detail'] = f'{type(exc).__name__}: public source request failed'
            return None


def parse_hotspawn(html):
    soup = BeautifulSoup(html, 'html.parser')
    state = soup.select_one('script#ng-state')
    if not state:
        raise ValueError('Hotspawn structured state missing; coverage cannot be verified')
    blocks = [v for v in json.loads(state.text).values() if isinstance(v, dict) and 'b' in v]
    fixture_blocks = [v for v in blocks if v.get('u', '').endswith('/api/v1/fixtures')]
    if len(fixture_blocks) != 1 or not isinstance(fixture_blocks[0]['b'], list):
        raise ValueError('Unexpected fixture response; refusing partial coverage')
    raw = fixture_blocks[0]['b']
    fixtures = [r for r in raw if r.get('sport_alias') == 'cs2']
    if len({str(r['id']) for r in fixtures}) != len(fixtures):
        raise ValueError('Duplicate fixture IDs')
    if not fixtures:
        raise ValueError('Empty fixture list needs review; retaining previous data')
    counts = re.findall(r'All tiers\s*\((\d+)\)', soup.get_text(' ', strip=True))
    advertised = int(counts[0]) if counts else None
    if advertised is not None and advertised != len(fixtures):
        raise ValueError(f'Coverage mismatch: lobby {advertised}, extracted {len(fixtures)}')
    permalinks = {}
    for v in blocks:
        if isinstance(v['b'], dict):
            permalinks.update(v['b'].get('permalinks', {}))
    # Preserve only inputs actually used. Crowd percentages never enter our dataset/model.
    keys = ['id', 'sport_alias', 'competition_name', 'status', 'scheduled_start_time',
            'lock_time', 'end_time', 'tier', 'best_of', 'participants0_id',
            'participants0_name', 'participants1_id', 'participants1_name']
    clean = [{k: r.get(k) for k in keys} for r in fixtures]
    return clean, permalinks, advertised


def parse_rankings(text):
    rows = {}
    for line in text.splitlines():
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 6 or not parts[1].isdigit() or not parts[2].isdigit():
            continue
        key = norm(parts[3])
        rows.setdefault(key, []).append({'name': parts[3], 'points': int(parts[2]), 'roster': parts[4]})
    # Duplicate organization names = ambiguous roster, no silent choice.
    return {k: v[0] for k, v in rows.items() if len(v) == 1}


def fetch_rankings(client, now):
    listing = client.get(f'{VALVE}/contents/live/{now.year}', 'Valve standings index')
    if not listing:
        return {}, None, None
    candidates = []
    for f in json.loads(listing):
        match = re.fullmatch(r'standings_global_(\d{4}_\d{2}_\d{2})\.md', f.get('name', ''))
        if match:
            date = datetime.strptime(match[1], '%Y_%m_%d').replace(tzinfo=timezone.utc)
            if date <= now:
                candidates.append((date, f))
    if not candidates:
        return {}, None, None
    date, f = max(candidates, key=lambda p: p[0])
    text = client.get(f['url'], 'Valve global standings', raw=True)
    if not text:
        return {}, None, None
    (DATA / 'evidence/valve-standings.md').write_text(text)
    return parse_rankings(text), f['html_url'], iso(date)


def fetch_events(client, now):
    sports = client.get('https://gamma-api.polymarket.com/sports', 'Polymarket sports metadata')
    if not sports:
        return []
    sport = next((s for s in json.loads(sports) if s.get('sport') == 'cs2'), None)
    if not sport or not sport.get('series'):
        raise ValueError('CS2 series ID not available from official metadata')
    events, seen = [], set()
    for offset in range(0, 5000, 100):
        params = {'series_id': sport['series'], 'closed': 'false', 'limit': 100, 'offset': offset,
                  'end_date_min': iso(now - timedelta(days=1))}
        text = client.get('https://gamma-api.polymarket.com/events?' + urlencode(params), 'Polymarket CS2 events')
        if text is None:
            raise ValueError('Incomplete market pagination; no market probabilities published')
        page = json.loads(text)
        if not isinstance(page, list):
            raise ValueError('Unexpected market schema')
        ids = [str(e['id']) for e in page]
        if seen.intersection(ids):
            raise ValueError('Market pagination repeated IDs')
        seen.update(ids)
        events.extend(page)
        if len(page) < 100:
            return events
    raise ValueError('Market page safety limit hit; coverage incomplete')


def matching_market(row, events, now):
    wanted = [norm(n) for n in row['teams']]
    candidates = []
    rejected = []
    for event in events:
        if not event.get('slug', '').startswith('cs2-') or event.get('closed') or event.get('live') or event.get('ended'):
            continue
        for m in event.get('markets', []):
            if m.get('sportsMarketType') != 'moneyline':
                continue
            try:
                outcomes = json.loads(m['outcomes']) if isinstance(m['outcomes'], str) else m['outcomes']
                names = [norm(n) for n in outcomes]
                if len(names) != 2 or set(names) != set(wanted) or len(set(names)) != 2:
                    continue
                start = parse_time(m.get('gameStartTime') or m.get('eventStartTime'))
                if not start or abs((start - parse_time(row['start_at'])).total_seconds()) > 3600:
                    continue
                url = 'https://polymarket.com/event/' + event['slug']
                if m.get('closed') or not m.get('active') or not m.get('acceptingOrders'):
                    rejected.append('Matching moneyline is closed or not accepting orders.')
                    continue
                updated = parse_time(m.get('updatedAt'))
                if not updated or not -300 <= (now - updated).total_seconds() <= 8 * 3600:
                    rejected.append('Matching market timestamp is missing or older than eight hours.')
                    continue
                prices = json.loads(m['outcomePrices']) if isinstance(m['outcomePrices'], str) else m['outcomePrices']
                prices = [float(prices[names.index(n)]) for n in wanted]
                if any(not 0 < p < 1 for p in prices):
                    rejected.append('Market is resolved, suspended, or has invalid prices.')
                    continue
                if not 0.9 <= sum(prices) <= 1.1:
                    rejected.append('Two-sided prices are inconsistent.')
                    continue
                # Reject empty books rather than mistake a seeded 50/50 for evidence.
                liquidity = float(m.get('liquidityNum') or m.get('liquidity') or 0)
                if liquidity <= 0:
                    rejected.append('No positive market liquidity reported.')
                    continue
                candidates.append({'probabilities': pair_normalize(prices), 'prices': prices,
                                   'url': url, 'id': str(m['id']), 'updated_at': iso(updated),
                                   'start_at': iso(start), 'outcomes': outcomes, 'liquidity': liquidity,
                                   'question': m.get('question'), 'source': 'Polymarket',
                                   'api_url': 'https://gamma-api.polymarket.com/markets/' + str(m['id'])})
            except (KeyError, ValueError, TypeError, OverflowError):
                rejected.append('Market input schema invalid; rejected.')
    if len(candidates) > 1:
        return None, 'Multiple matching moneylines; identity needs review.'
    return (candidates[0], None) if candidates else (None, ' '.join(sorted(set(rejected))) or 'No exact two-team, same-time, open CS2 series moneyline found.')


def assemble(fixtures, links, advertised, events, ranks, rank_url, rank_date, now, audits):
    matches = []
    for f in fixtures:
        names = [f.get(f'participants{i}_name') for i in range(2)]
        start, lock = parse_time(f.get('scheduled_start_time')), parse_time(f.get('lock_time'))
        row = {'id': str(f['id']), 'teams': names, 'tournament': f.get('competition_name'),
               'tier': f.get('tier'), 'best_of': f.get('best_of'),
               'start_at': iso(start) if start else None, 'lock_at': iso(lock) if lock else None,
               'source_status': f.get('status'), 'fixture_source': links.get(str(f['id'])) or LOBBY,
               'fixture_verified_at': iso(now), 'probabilities': None, 'pick': None,
               'method': None, 'evidence': [], 'limitations': [], 'attempts': [], 'flags': []}
        if not start or not lock or any(not n or norm(n) in ('tbd', 'tba', 'unknown') for n in names):
            row['state'] = 'unresolved'
            row['limitations'].append('Team identity, start time, or lock time is unverified.')
        elif lock <= now or f.get('end_time'):
            row['state'] = 'locked'
            row['limitations'].append('Lock time has passed or an end time is present. No retrospective pre-match pick invented.')
            if f.get('status') == 'scheduled' and (f.get('end_time') or start < now - timedelta(days=1)):
                row['flags'].append('Hotspawn still labels this past/ended fixture scheduled.')
        else:
            market, issue = matching_market(row, events, now)
            row['attempts'].append({'source': 'Polymarket', 'url': 'https://polymarket.com/esports/cs2',
                                    'result': 'Accepted series moneyline.' if market else issue})
            if market:
                row['state'], row['method'] = 'priced', 'market'
                row['probabilities'] = market['probabilities']
                row['evidence'] = [market]
                row['limitations'].append('Single prediction-market reference; not a multi-book consensus or calibrated win forecast. Fees, spreads and settlement rules differ from pick’em rules.')
                if market['liquidity'] < 1000:
                    row['flags'].append('Thin market: reported liquidity below $1,000.')
            else:
                # Source attempts happen in this order only for unresolved featured-market matches.
                for name, url in BOOKS:
                    audit = next((a for a in audits if a['name'] == name), {})
                    row['attempts'].append({'source': name, 'url': url,
                        'result': audit.get('detail', 'No validated two-sided series odds extracted.')})
                found = [ranks.get(norm(n)) for n in names]
                recent = rank_date and 0 <= (now - parse_time(rank_date)).days <= 35
                if all(found) and recent:
                    row['state'], row['method'] = 'priced', 'model'
                    row['probabilities'] = rating_probability([r['points'] for r in found])
                    row['evidence'] = [{'source': 'Valve global standings', 'url': rank_url,
                                        'as_of': rank_date, 'ratings': found, 'model': 'VRS-Glicko conservative v1; fixed RD 350'}]
                    row['limitations'].append('Research fallback, not betting odds. Organization-name match only; current roster continuity, veto, format and form are unverified. Fixed RD=350 is a model assumption. Not independently calibrated.')
                    row['flags'].append('Model-only probability: source points verified; forecast and current roster not verified.')
                else:
                    row['state'] = 'unresolved'
                    missing = [names[i] for i, r in enumerate(found) if not r]
                    row['limitations'].append('No usable external moneyline. ' + ('No unique exact-name Valve rating for: ' + ', '.join(missing) + '.' if missing else 'Valve ranking date missing or over 35 days old.'))
                    row['limitations'].append('Blocked or unavailable betting sources do not prove that no bookmaker covers this match. No 50/50 placeholder assigned.')
            if row['probabilities']:
                a, b = row['probabilities']
                row['pick'] = names[0 if a > b else 1] if a != b else None
                if a == b:
                    row['limitations'].append('Equal estimates: no directional pick.')
        matches.append(row)
    matches.sort(key=lambda r: (r['start_at'] or '', r['id']))
    return {'schema_version': 1, 'generated_at': iso(now), 'fixture_checked_at': iso(now),
            'refresh_hours': 6, 'coverage': {'source': LOBBY, 'advertised': advertised,
            'collected': len(fixtures), 'status': 'count-matched' if advertised == len(fixtures) else 'count-unverified',
            'scope': 'All CS2 fixtures embedded in the public lobby response, including past rows; not all global CS2 matches.'},
            'source_audit': audits, 'matches': matches, 'issues': []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true', help='Rebuild from captured official responses for tests only')
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'evidence').mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    client = Client(now)
    previous_path = DATA / 'snapshot.json'
    try:
        if args.offline:
            html = (ROOT / 'data/diagnostics/hotspawn.html').read_text()
            now = datetime(2026, 10, 14, 4, 47, tzinfo=timezone.utc)
            client.now = now
        else:
            html = client.get(LOBBY, 'Hotspawn CS2 lobby')
        if html is None:
            raise ValueError('Hotspawn unavailable; current coverage cannot be confirmed')
        fixtures, links, advertised = parse_hotspawn(html)
    except (ValueError, KeyError, TypeError) as exc:
        if not previous_path.exists():
            raise
        previous = json.loads(previous_path.read_text())
        previous['generated_at'] = iso(now)
        previous['coverage']['status'] = 'stale'
        previous['issues'] = [str(exc)]
        previous['source_audit'] = client.audit
        # Keep original per-row observation times; blank every actionable probability.
        for row in previous['matches']:
            row['probabilities'], row['pick'], row['method'] = None, None, None
            row['state'] = 'locked' if row['lock_at'] and parse_time(row['lock_at']) <= now else 'unresolved'
            row['limitations'] = ['Source refresh failed; previous fixture retained as stale.']
        previous_path.write_text(json.dumps(previous, indent=2) + '\n')
        return
    problems = []
    if args.offline:
        events_path = ROOT / 'data/diagnostics/events.html'
        events = json.loads(events_path.read_text()) if events_path.exists() else []
        ranks = parse_rankings((ROOT / 'research/valve.md').read_text())
        rank_url = 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/master/live/2026/standings_global_2026_10_05.md'
        rank_date = '2026-10-05T00:00:00Z'
        (DATA / 'evidence/valve-standings.md').write_text((ROOT / 'research/valve.md').read_text())
    else:
        try:
            events = fetch_events(client, now)
        except (ValueError, KeyError, TypeError) as exc:
            events = []
            problems.append(str(exc))
        ranks, rank_url, rank_date = {}, None, None
    needs_fallback = []
    for f in fixtures:
        if f.get('lock_time') and parse_time(f['lock_time']) > now and not f.get('end_time'):
            minimal = {'teams': [f.get('participants0_name') or '', f.get('participants1_name') or ''],
                       'start_at': iso(parse_time(f['scheduled_start_time']))}
            if not matching_market(minimal, events, now)[0]:
                needs_fallback.append(f['id'])
    if needs_fallback:
        for name, url in BOOKS:
            if args.offline:
                headers = (ROOT / 'data/diagnostics' / ({'HLTV': 'hltv', 'GG.BET': 'ggbet'}.get(name, name.lower()) + '.headers')).read_text()
                status = re.findall(r'HTTP/\S+ (\d+)', headers)[-1]
                client.audit.append({'name': name, 'url': url, 'checked_at': iso(now), 'http_status': int(status)})
                text = None if status != '200' else ''
            else:
                text = client.get(url, name)
            a = client.audit[-1]
            a['status'] = 'unavailable' if text is None else 'no-validated-lines'
            a['detail'] = (f'HTTP {a.get("http_status", "request failure")}; public page unavailable from runner.' if text is None else
                           'Public page retrieved, but no validated two-sided match-winner feed available to this adapter. No odds inferred from ads, polls or placeholders.')
        if not args.offline:
            try:
                ranks, rank_url, rank_date = fetch_rankings(client, now)
            except (ValueError, KeyError, TypeError) as exc:
                problems.append('Valve source schema unavailable: ' + str(exc))
    snapshot = assemble(fixtures, links, advertised, events, ranks, rank_url, rank_date, now, client.audit)
    snapshot['issues'] = problems
    if args.offline:
        snapshot['issues'].append('Captured-response development build; automated live refresh pending.')
    (DATA / 'evidence/fixtures.json').write_text(json.dumps({'source': LOBBY, 'observed_at': iso(now), 'fixtures': fixtures}, indent=2) + '\n')
    previous_path.write_text(json.dumps(snapshot, indent=2) + '\n')
    print(json.dumps({'rows': len(snapshot['matches']), 'priced': sum(r['state'] == 'priced' for r in snapshot['matches']),
                      'unresolved': sum(r['state'] == 'unresolved' for r in snapshot['matches'])}))


if __name__ == '__main__':
    main()
