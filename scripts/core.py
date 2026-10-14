"""Fail-closed match identity and probability calculations. No crowd-pick inputs."""
import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from bs4 import BeautifulSoup

HOTSPAWN = 'https://play.hotspawn.com/cs2-pickems'
FIXTURES = 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1'
PIN = 'https://guest.api.arcadia.pinnacle.com/0.1'
GAMMA = 'https://gamma-api.polymarket.com'
MAX_AGE = 8 * 3600


def dt(value):
    if value is None or value == '':
        raise ValueError('Missing timestamp')
    if isinstance(value, (int, float)) or str(value).isdigit():
        return datetime.fromtimestamp(float(value) / 1000, timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamp has no timezone')
    return parsed.astimezone(timezone.utc)


def iso(value):
    return dt(value).isoformat().replace('+00:00', 'Z')


def norm(value):
    # Punctuation and case only. Never strip academy, women, junior or other qualifiers.
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def fresh(timestamp, now):
    try:
        age = (now - dt(timestamp)).total_seconds()
        return -300 <= age <= MAX_AGE
    except (TypeError, ValueError, OverflowError):
        return False


def devig(decimal):
    if len(decimal) != 2 or any(not math.isfinite(x) or x <= 1 for x in decimal):
        raise ValueError('Need two finite decimal odds greater than one')
    implied = [1 / x for x in decimal]
    total = sum(implied)
    return [x / total for x in implied], total - 1


def american(value):
    value = float(value)
    if not math.isfinite(value) or abs(value) < 100:
        raise ValueError('Invalid American line')
    return 1 + (value / 100 if value > 0 else 100 / -value)


def hotspawn_state(html):
    soup = BeautifulSoup(html, 'html.parser')
    state = soup.find('script', id='ng-state')
    if not state:
        raise ValueError('Hotspawn hydration data missing; cannot claim empty lobby')
    data = json.loads(state.string)
    fixtures, permalinks = None, {}
    for entry in data.values():
        if not isinstance(entry, dict):
            continue
        if entry.get('u', '').endswith('/api/v1/fixtures'):
            fixtures = entry['b']
        if entry.get('u', '').endswith('/fixtures/permalinks'):
            permalinks = entry['b'].get('permalinks', {})
    if not isinstance(fixtures, list):
        raise ValueError('Unrecognized Hotspawn fixture schema')
    return fixtures, permalinks


def normalize_fixtures(raw, links, now):
    if not isinstance(raw, list):
        raise ValueError('Expected complete fixture array, not unhandled pagination')
    result, seen = [], set()
    for row in raw:
        if row.get('sport_alias') != 'cs2':
            continue
        ident = str(row['id'])
        if ident in seen:
            raise ValueError('Duplicate fixture ID: ' + ident)
        seen.add(ident)
        teams = [row.get('participants0_name'), row.get('participants1_name')]
        start = iso(row['scheduled_start_time']) if row.get('scheduled_start_time') else None
        lock = iso(row['lock_time']) if row.get('lock_time') else None
        flags = []
        if not all(teams) or len(set(teams)) != 2 or any(norm(t or '') in ('tbd', 'tba', 'unknown') for t in teams):
            flags.append('Team identity unverified or not yet announced.')
        if not start or not lock:
            flags.append('Start or lock time is unverified; no pick issued.')
        if row.get('end_time') and row.get('status') == 'scheduled':
            flags.append('Hotspawn reports scheduled status and an end time simultaneously.')
        state = 'open' if lock and start and dt(lock) > now and dt(start) > now and not row.get('end_time') and not flags and row.get('status') == 'scheduled' else 'not_open'
        if state == 'not_open' and row.get('status') == 'scheduled' and start and dt(start) < now:
            flags.append('Scheduled feed entry is past its start; current match status is unverified.')
        result.append({
            'id': ident, 'teams': teams, 'team_ids': [row.get('participants0_id'), row.get('participants1_id')],
            'competition': row.get('competition_name'), 'tier': row.get('tier'),
            'best_of': row.get('best_of'), 'start': start, 'lock': lock,
            'source_status': row.get('status'), 'state': state,
            'source_url': links.get(ident) or HOTSPAWN, 'feed_url': FIXTURES,
            'flags': flags, 'probabilities': None, 'fair_odds': None, 'pick': None,
            'method': None, 'evidence': [], 'attempts': [], 'reason': None,
        })
    return sorted(result, key=lambda x: (x['start'] or '', x['id']))


def orientation(fixture, teams, start):
    """No fuzzy aliases; only two exact normalized names and exact UTC start."""
    if len(teams) != 2 or not fixture['start'] or not start:
        return None
    try:
        if dt(fixture['start']) != dt(start):
            return None
    except (TypeError, ValueError):
        return None
    a, b = map(norm, fixture['teams'])
    names = list(map(norm, teams))
    if a == b:
        return None
    if names == [a, b]:
        return [0, 1]
    if names == [b, a]:
        return [1, 0]
    return None


def polymarket_candidates(events, observed_at):
    result = []
    for event in events:
        if event.get('sport', {}).get('sport') != 'cs2' and not event.get('slug', '').startswith('cs2-'):
            continue
        if event.get('closed') or event.get('live') or event.get('ended'):
            continue
        for m in event.get('markets', []):
            if m.get('sportsMarketType') != 'moneyline':
                continue
            try:
                teams = json.loads(m['outcomes']) if isinstance(m['outcomes'], str) else m['outcomes']
                prices = [float(p) for p in (json.loads(m['outcomePrices']) if isinstance(m['outcomePrices'], str) else m['outcomePrices'])]
                if len(teams) != 2 or len(prices) != 2:
                    continue
                result.append({'provider': 'Polymarket', 'id': str(m['id']), 'teams': teams,
                    'start': m.get('gameStartTime') or m.get('eventStartTime'),
                    'observed_at': observed_at, 'updated_at': m.get('updatedAt'),
                    'url': 'https://polymarket.com/event/' + event['slug'],
                    'api_url': GAMMA + '/markets/' + str(m['id']),
                    'raw': {k:m.get(k) for k in ('id','question','sportsMarketType','outcomes','outcomePrices','gameStartTime','eventStartTime','updatedAt','active','closed','acceptingOrders','bestBid','bestAsk','liquidity','volume')},
                    'prices': prices, 'market': m,
                    'best_of': int(re.search(r'\(BO(\d+)\)',m.get('question',''),re.I).group(1)) if re.search(r'\(BO(\d+)\)',m.get('question',''),re.I) else None,
                    'team_aliases': [[t, *[x.get('abbreviation','') for x in event.get('teams',[]) if x.get('name') == t]] for t in teams],
                    'team_metadata': event.get('teams', [])})
            except (TypeError, ValueError, KeyError):
                continue
    return result


def quote_polymarket(candidate, order, now):
    m = candidate['market']
    if not m.get('active') or m.get('closed') or not m.get('acceptingOrders'):
        raise ValueError('Exchange market closed, suspended or not accepting orders.')
    if not fresh(candidate['observed_at'], now) or not fresh(candidate['updated_at'], now):
        raise ValueError('Exchange observation or update is older than eight hours.')
    prices = candidate['prices']
    if any(not math.isfinite(p) or not 0 < p < 1 for p in prices) or not .95 <= sum(prices) <= 1.05:
        raise ValueError('Invalid or settled binary prices.')
    bid, ask = m.get('bestBid'), m.get('bestAsk')
    if bid is None or ask is None or not 0 < float(bid) <= float(ask) < 1:
        raise ValueError('Two-sided exchange quote is unavailable.')
    spread = float(ask) - float(bid)
    if spread > .25 or float(m.get('liquidity') or 0) < 100:
        raise ValueError('Exchange spread exceeds 25 points or liquidity is below $100.')
    p = [prices[i] / sum(prices) for i in order]
    return {k: candidate[k] for k in ('provider','id','url','api_url','observed_at','updated_at','raw')} | {
        'probabilities': p, 'spread': spread, 'liquidity': float(m.get('liquidity') or 0),
        'warning': 'Wide exchange spread; low precision.' if spread > .10 else None,
        'source_teams': candidate['teams'], 'start': iso(candidate['start'])}


def pinnacle_candidates(matchups, lines, observed_at):
    index = {}
    for line in lines:
        if line.get('period') == 0 and line.get('type') == 'moneyline' and not line.get('isAlternate'):
            index.setdefault(line.get('matchupId'), []).append(line)
    out = []
    for m in matchups:
        if not m.get('league', {}).get('name', '').startswith('CS2 - ') or m.get('parentId') or m.get('isLive') or m.get('type') != 'matchup':
            continue
        players = {p.get('alignment'):p.get('name') for p in m.get('participants', [])}
        if set(players) != {'home','away'}:
            continue
        for line in index.get(m['id'], []):
            out.append({'provider': 'Pinnacle', 'id': str(m['id']),
                'teams': [players['home'],players['away']], 'start': m.get('startTime'),
                'observed_at': observed_at, 'url': 'https://www.pinnacle.com/en/esports',
                'api_url': PIN + '/sports/12/markets/straight',
                'raw': {'matchup': {k:m.get(k) for k in ('id','league','participants','startTime','status','isLive','bestOfX')}, 'line': line},
                'line': line, 'status': m.get('status'), 'best_of': m.get('bestOfX')})
    return out


def quote_pinnacle(candidate, order, now):
    line = candidate['line']
    if candidate['status'] != 'pending' or line.get('status') != 'open' or not fresh(candidate['observed_at'], now):
        raise ValueError('Bookmaker line is not open/prematch or is stale.')
    if dt(line.get('cutoffAt')) <= now:
        raise ValueError('Bookmaker cutoff has passed.')
    prices = line.get('prices', [])
    if len(prices) != 2 or {p.get('designation') for p in prices} != {'home','away'}:
        raise ValueError('Unverified two-way price alignment.')
    values = {p['designation']:p['price'] for p in prices}
    odds = [american(values['home']), american(values['away'])]
    p, margin = devig(odds)
    if not -.02 <= margin <= .25:
        raise ValueError('Bookmaker margin outside validation bounds.')
    return {k:candidate[k] for k in ('provider','id','url','api_url','observed_at','raw')} | {
        'updated_at': None, 'probabilities': [p[i] for i in order],
        'decimal_odds': [odds[i] for i in order], 'overround': margin,
        'source_teams': candidate['teams'], 'start': iso(candidate['start']),
        'warning': 'Single bookmaker; price update timestamp not supplied. Observation time shown.'}


def resolve(fixture, candidates, provider, now):
    if fixture['probabilities'] is not None or fixture['state'] != 'open':
        return
    exact, near = [], []
    for c in candidates:
        comparable = list(c['teams'])
        for i, aliases in enumerate(c.get('team_aliases', [])):
            targets = [t for t in fixture['teams'] if norm(t) in {norm(a) for a in aliases if a}]
            if len(targets) == 1:
                comparable[i] = targets[0]
        order = orientation(fixture, comparable, c['start'])
        if order is not None:
            exact.append((c, order))
        elif c.get('start') and dt(c['start']) == dt(fixture['start']) and set(map(norm,c['teams'])) & set(map(norm,fixture['teams'])):
            near.append(c)
    attempt = {'provider': provider, 'status': 'unresolved', 'url': GAMMA+'/sports' if provider == 'Polymarket' else PIN+'/sports/12/markets/straight'}
    if len(exact) > 1:
        attempt['reason'] = 'Multiple same-team, same-time markets; ambiguous identity. No automatic pick.'
    elif len(exact) == 1:
        c, order = exact[0]
        attempt['url'] = c['api_url']
        try:
            if fixture.get('best_of') is not None and (c.get('best_of') is None or str(c['best_of']) != str(fixture['best_of'])):
                raise ValueError('Known series format does not agree with the external source.')
            quote = (quote_polymarket if provider == 'Polymarket' else quote_pinnacle)(c, order, now)
            p = quote['probabilities']
            if c.get('team_metadata'):
                quote['team_metadata'] = c['team_metadata']
            fixture.update(probabilities=p, fair_odds=[1/x for x in p],
                pick=None if abs(p[0]-p[1]) < .0001 else fixture['teams'][0 if p[0]>p[1] else 1],
                method='exchange' if provider == 'Polymarket' else 'bookmaker_fallback', evidence=[quote],
                reason='Equal verified prices; no directional edge.' if abs(p[0]-p[1]) < .0001 else None)
            if quote.get('warning'):
                fixture['flags'].append(quote['warning'])
            attempt.update(status='resolved',reason='Exact pair and UTC start; two-way series winner validated.')
        except (ValueError, TypeError, KeyError) as e:
            attempt['reason'] = str(e)
    elif near:
        attempt.update(reason='Unverified opponent/alias or roster-name mismatch; no fuzzy match used.', candidates=[{'teams': c['teams'],'url':c['api_url']} for c in near])
    else:
        attempt['reason'] = 'No exact team-pair and UTC-start match in retrieved feed.'
    fixture['attempts'].append(attempt)
