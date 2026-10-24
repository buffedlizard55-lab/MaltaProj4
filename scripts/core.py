"""Fail-closed match identity and probability calculations. No crowd-pick inputs."""
import copy
import json
import math
import re
import unicodedata
from pathlib import Path
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

HOTSPAWN = 'https://play.hotspawn.com/cs2-pickems'
FIXTURES = 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1'
PIN = 'https://guest.api.arcadia.pinnacle.com/0.1'
GAMMA = 'https://gamma-api.polymarket.com'
MAX_AGE = 8 * 3600
IDENTITIES = json.loads((Path(__file__).resolve().parents[1] / 'data/identities.json').read_text())['aliases']

def plain_name(value):
    # Diacritic folding (NFKD + drop combining marks) so "Los Niños" and
    # "LOS NINOS" resolve to one key. Name normalisation only; it never changes a
    # probability and never guesses a suffix. Requested and proven by session
    # ef0969b9 (research/ef0969b9/UNPRICED-FIXTURE-LINES.md section 1).
    if not isinstance(value, str):
        raise ValueError('Team name is not text')
    folded = unicodedata.normalize('NFKD', value).casefold()
    folded = ''.join(c for c in folded if not unicodedata.combining(c))
    return ''.join(c for c in unicodedata.normalize('NFKC', folded) if c.isalnum())

ALIAS_MAP = {plain_name(name):plain_name(item['canonical']) for item in IDENTITIES for name in item['names']}


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
    # No guessed suffix removal. Only explicitly primary-source-verified aliases.
    key=plain_name(value)
    return ALIAS_MAP.get(key,key)


def fresh(timestamp, now):
    try:
        age = (now - dt(timestamp)).total_seconds()
        return -300 <= age < MAX_AGE
    except (TypeError, ValueError, OverflowError, OSError):
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
    data = json.loads(state.string or '')
    if not isinstance(data, dict):
        raise ValueError('Unrecognized Hotspawn hydration schema')
    fixtures, permalinks = None, {}
    for entry in data.values():
        if not isinstance(entry, dict):
            continue
        if entry.get('u', '').endswith('/api/v1/fixtures'):
            if fixtures is not None:
                raise ValueError('Multiple fixture arrays in hydration; scope needs review')
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
        if not isinstance(row, dict):
            raise ValueError('Fixture entry is not an object')
        if row.get('sport_alias') != 'cs2':
            continue
        if row.get('id') is None or not str(row['id']).strip():
            raise ValueError('Fixture ID is missing')
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
        if not isinstance(event, dict):
            continue
        if (event.get('sport') or {}).get('sport') != 'cs2' and not event.get('slug', '').startswith('cs2-'):
            continue
        if event.get('closed') or event.get('live') or event.get('ended'):
            continue
        for m in event.get('markets', []):
            if m.get('sportsMarketType') != 'moneyline':
                continue
            try:
                teams = json.loads(m['outcomes']) if isinstance(m['outcomes'], str) else m['outcomes']
                prices = [float(p) for p in (json.loads(m['outcomePrices']) if isinstance(m['outcomePrices'], str) else m['outcomePrices'])]
                if len(teams) != 2 or len(prices) != 2 or not all(isinstance(t, str) and t.strip() for t in teams):
                    continue
                result.append({'provider': 'Polymarket', 'id': str(m['id']), 'teams': teams,
                    'start': m.get('gameStartTime') or m.get('eventStartTime'),
                    'observed_at': observed_at, 'updated_at': m.get('updatedAt'),
                    'url': 'https://polymarket.com/event/' + event['slug'],
                    'api_url': GAMMA + '/markets/' + str(m['id']),
                    'raw': {k:m.get(k) for k in ('id','question','sportsMarketType','outcomes','outcomePrices','gameStartTime','eventStartTime','updatedAt','active','closed','acceptingOrders','bestBid','bestAsk','liquidity','volume')},
                    'prices': prices, 'market': m,
                    'best_of': int(re.search(r'\(BO(\d+)\)',m.get('question',''),re.I).group(1)) if re.search(r'\(BO(\d+)\)',m.get('question',''),re.I) else None,
                    'team_aliases': [[t, *[x.get('abbreviation','') for x in (event.get('teams') or []) if x.get('name') == t]] for t in teams],
                    'team_metadata': event.get('teams', []),
                    'event': {k:event.get(k) for k in ('id','slug','sport','closed','live','ended','teams')}})
            except (TypeError, ValueError, KeyError):
                continue
    return result


def record_polymarket_exclusions(fixtures, events, observed_at, source_receipt=None):
    """Explain excluded exact-match event states without ever admitting a quote.

    Operator event flags outrank a market's active/acceptingOrders fields. An
    ended event with a future start is a source inconsistency, not a reason to
    synthesize a pick. Diagnostics are restricted to unresolved exact fixtures.
    """
    for event in events:
        if not isinstance(event, dict) or not event.get('slug', '').startswith('cs2-'):
            continue
        blocked = [key for key in ('closed', 'live', 'ended') if event.get(key)]
        if not blocked:
            continue
        for market in event.get('markets') or []:
            if not isinstance(market, dict) or market.get('sportsMarketType') != 'moneyline':
                continue
            try:
                teams = market.get('outcomes')
                teams = json.loads(teams) if isinstance(teams, str) else teams
                if not isinstance(teams, list) or len(teams) != 2 or not all(isinstance(t, str) for t in teams):
                    continue
                start = market.get('gameStartTime') or market.get('eventStartTime')
                for fixture in fixtures:
                    if fixture.get('state') != 'open' or fixture.get('probabilities') is not None:
                        continue
                    if orientation(fixture, teams, start) is None:
                        continue
                    reason = ('Exact exchange opponent pair and UTC start found, but the parent event is '
                              + ', '.join(key + '=true' for key in blocked)
                              + '. Market active/acceptingOrders cannot override event status; no probability accepted.')
                    attempt = {'provider': 'Polymarket', 'status': 'rejected', 'reason': reason,
                               'url': GAMMA + '/events/' + str(event.get('id', '')),
                               'observed_at': observed_at,
                               'event_status': {key: event.get(key) for key in ('id', 'slug', 'closed', 'live', 'ended')},
                               'market_status': {key: market.get(key) for key in ('id', 'active', 'closed', 'acceptingOrders', 'gameStartTime')}}
                    if source_receipt:
                        attempt['source_receipt'] = source_receipt.copy()
                    fixture['attempts'].append(attempt)
                    if reason not in fixture['flags']:
                        fixture['flags'].append(reason)
            except (ValueError, TypeError, KeyError):
                continue


def quote_polymarket(candidate, order, now, allow_wide=False):
    """Validate a two-sided exchange quote.

    Strict gate: spread <= 25 points and liquidity >= $100.
    ``allow_wide`` is the documented second-chance tier requested for fixtures
    that would otherwise have no pick. It keeps every other gate (market open,
    accepting orders, fresh observation and update, finite two-sided quote,
    liquidity) and only relaxes the spread ceiling, publishing the real spread
    with a low-confidence label. A market below the $100 liquidity floor is
    never accepted, wide or not.
    """
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
    liquidity = float(m.get('liquidity') or 0)
    if not math.isfinite(liquidity) or not math.isfinite(spread):
        raise ValueError('Non-finite exchange liquidity or spread.')
    if liquidity < 100:
        raise ValueError('Exchange liquidity is below $100.')
    # Float-safe comparison: a genuine 25.0-point spread is "no greater than 25".
    if spread > .25 + 1e-9:
        if not allow_wide:
            raise ValueError('Exchange spread exceeds 25 points or liquidity is below $100.')
        if spread > .60 + 1e-9:
            raise ValueError('Exchange spread exceeds the 60-point ceiling for the low-confidence tier.')
    p = [prices[i] / sum(prices) for i in order]
    wide = spread > .25 + 1e-9
    warning = ('Low confidence: wide two-sided quote (spread %.0f points). Market mid only; the true value is uncertain.' % round(spread * 100)) if wide else ('Wide exchange spread; low precision.' if spread > .10 else None)
    return {k: candidate[k] for k in ('provider','id','url','api_url','observed_at','updated_at','raw')} | {
        'probabilities': p, 'spread': spread, 'liquidity': liquidity,
        'warning': warning, 'tier': 'wide_exchange' if wide else 'exchange',
        'event': candidate.get('event'),
        'source_teams': candidate['teams'], 'start': iso(candidate['start'])}


def pinnacle_candidates(matchups, lines, observed_at):
    if not isinstance(matchups, list) or not isinstance(lines, list):
        raise ValueError('Unexpected bookmaker array schema')
    index = {}
    for line in lines:
        if line.get('period') == 0 and line.get('type') == 'moneyline' and not line.get('isAlternate'):
            index.setdefault(line.get('matchupId'), []).append(line)
    out = []
    for m in matchups:
        if not m.get('league', {}).get('name', '').startswith('CS2 - ') or m.get('parentId') or m.get('isLive') or m.get('type') != 'matchup':
            continue
        players = {p.get('alignment'):p.get('name') for p in m.get('participants', [])}
        if len(m.get('participants', [])) != 2 or set(players) != {'home','away'} or not all(isinstance(x, str) and x.strip() for x in players.values()):
            continue
        for line in index.get(m['id'], []):
            out.append({'provider': 'Pinnacle', 'id': str(m['id']),
                'teams': [players['home'],players['away']], 'start': m.get('startTime'),
                'observed_at': observed_at, 'url': 'https://www.pinnacle.com/en/esports',
                'api_url': PIN + '/sports/12/markets/straight',
                'raw': {'matchup': {k:m.get(k) for k in ('id','league','participants','startTime','status','isLive','bestOfX','type','parentId')}, 'line': line},
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


BOOK_RECEIPTS = Path(__file__).resolve().parents[1] / 'data/book-receipts.json'


def book_receipts(path=None):
    """Load researched book-listing receipts. A missing or malformed file means
    no receipts: this tier never turns silence into a line."""
    try:
        doc = json.loads(Path(path or BOOK_RECEIPTS).read_text())
    except (OSError, ValueError):
        return []
    if not isinstance(doc, dict) or not isinstance(doc.get('receipts'), list):
        return []
    return doc['receipts']


def book_candidate(receipt):
    """One researched receipt -> one whole-match quote candidate. Fail closed."""
    if not isinstance(receipt, dict):
        raise ValueError('Book receipt is not an object')
    required = ('provider', 'id', 'fixture_id', 'source_teams', 'team_aliases',
                'start', 'odds', 'observed_at', 'url')
    missing = [k for k in required if receipt.get(k) in (None, '')]
    if missing:
        raise ValueError('Book receipt missing fields: ' + ', '.join(missing))
    teams = list(receipt['source_teams'])
    aliases = receipt['team_aliases']
    if len(teams) != 2 or len(aliases) != 2 or not all(isinstance(a, list) and a for a in aliases):
        raise ValueError('Book receipt needs two source labels and two non-empty alias lists')
    if not all(isinstance(t, str) and t.strip() for t in teams):
        raise ValueError('Book receipt source labels must be text')
    odds = receipt['odds']
    if not isinstance(odds, list) or len(odds) != 2:
        raise ValueError('Book receipt needs exactly two decimal odds')
    return {'provider': receipt['provider'], 'id': str(receipt['id']),
        'fixture_id': str(receipt['fixture_id']), 'teams': teams,
        'team_aliases': [list(a) for a in aliases], 'start': receipt['start'],
        'observed_at': receipt['observed_at'], 'url': receipt['url'],
        'api_url': receipt.get('api_url') or receipt['url'],
        'raw': copy.deepcopy(receipt), 'odds': [float(x) for x in odds],
        'best_of': receipt.get('best_of')}


def quote_book(candidate, order, now):
    """De-vig a researched two-way decimal book line. Replayable from raw fields.

    The listing supplies no price-change timestamp, so the observation time is
    what ages out under the same eight-hour evidence window as every other
    quote. Identical decimal odds remain replayable here, but ``book_research_pick``
    retains the resulting 50/50 quote as rejected directional evidence and
    continues to the next rung. A listing with identical *default* odds is
    excluded at research time and recorded in ``rejected_listings``.
    """
    if not fresh(candidate['observed_at'], now):
        raise ValueError('Researched book listing is stale.')
    try:
        if dt(candidate['observed_at']) > dt(candidate['start']):
            raise ValueError('Book listing observation is after the listed start time.')
    except (TypeError, ValueError, OverflowError, OSError) as exc:
        if 'listed start time' in str(exc):
            raise
        raise ValueError('Book listing identity timestamps are unusable.')
    odds = candidate['odds']
    p, margin = devig(odds)
    if not -.02 <= margin <= .25:
        raise ValueError('Bookmaker margin outside validation bounds.')
    return {k: candidate[k] for k in ('provider', 'id', 'url', 'api_url', 'observed_at', 'raw')} | {
        'updated_at': None, 'probabilities': [p[i] for i in order],
        'decimal_odds': [odds[i] for i in order], 'overround': margin,
        'source_teams': candidate['teams'], 'start': iso(candidate['start']),
        'team_aliases': [list(a) for a in candidate['team_aliases']],
        'alias_sources': list((candidate['raw'] or {}).get('alias_sources') or []),
        'warning': 'Researched bookmaker listing; the listing supplies no price-update timestamp. Observation time shown.'}


def calculator_for(provider):
    """The exact calculator that produced (and can replay) a stored quote."""
    return quote_polymarket if provider == 'Polymarket' else (quote_pinnacle if provider == 'Pinnacle' else quote_book)


def book_research_pick(fixture, receipts=None, now=None):
    """Price an open fixture from a researched book-listing receipt, if one
    matches this exact row. Runs before the rank-only tiers so a real listed
    book line always outranks ranking order. The published method is the
    ordinary bookmaker tier; the row flags record that the line was researched
    rather than pulled by an automated adapter."""
    if fixture['probabilities'] is not None or fixture['state'] != 'open' or fixture.get('resolution_blocked'):
        return
    if fixture.get('pick') or fixture.get('evidence'):
        return
    for receipt in (book_receipts() if receipts is None else receipts):
        try:
            candidate = book_candidate(receipt)
        except ValueError as exc:
            fixture['attempts'].append({'provider': 'Book research', 'status': 'error',
                'reason': 'Malformed receipt skipped: ' + str(exc),
                'url': str((receipt or {}).get('url') or BOOK_RECEIPTS)})
            continue
        if candidate['fixture_id'] != str(fixture['id']):
            continue
        comparable = list(candidate['teams'])
        for i, aliases in enumerate(candidate['team_aliases']):
            targets = [t for t in fixture['teams'] if norm(t) in {norm(a) for a in aliases if a}]
            if len(targets) == 1:
                comparable[i] = targets[0]
        order = orientation(fixture, comparable, candidate['start'])
        if order is None:
            fixture['attempts'].append({'provider': 'Book research', 'status': 'unresolved',
                'reason': 'Receipt names this fixture id but not the exact opponent pair and UTC start. No pick invented.',
                'url': candidate['url']})
            continue
        if fixture.get('best_of') is not None and (candidate.get('best_of') is None
                or str(candidate['best_of']) != str(fixture['best_of'])):
            fixture['attempts'].append({'provider': 'Book research', 'status': 'unresolved',
                'reason': 'Known series format does not agree with the researched listing.',
                'url': candidate['url']})
            continue
        try:
            quote = quote_book(candidate, order, now if now is not None else datetime.now(timezone.utc))
        except ValueError as exc:
            fixture['attempts'].append({'provider': 'Book research', 'status': 'unresolved',
                'reason': str(exc), 'url': candidate['url']})
            continue
        if candidate['raw'].get('source_receipts'):
            quote['source_receipts'] = copy.deepcopy(candidate['raw']['source_receipts'])
        p = quote['probabilities']
        if abs(p[0] - p[1]) < .0001:
            fixture['attempts'].append({'provider': 'Book research', 'status': 'unresolved',
                'reason': 'Researched book line is exactly even (50/50); no directional edge. The quote is retained as rejected evidence and research continues.',
                'url': candidate['url'],
                'rejected_quote': dict(quote, notice='Rejected evidence, not a pick or verified probability.')})
            continue
        fixture.update(probabilities=p, fair_odds=[1 / x for x in p],
            pick=fixture['teams'][0 if p[0] > p[1] else 1],
            method='bookmaker_fallback', evidence=[quote], reason=None)
        fixture['flags'].append('Bookmaker line from a researched listing (no automated adapter for this book): ' + quote['warning'])
        fixture['attempts'].append({'provider': 'Book research', 'status': 'resolved',
            'reason': 'Exact fixture id, opponent pair and UTC start verified against the listed two-way book line; probabilities de-vigged by scripts.core.quote_book and replayed by the validator.',
            'url': candidate['url']})
        return


def resolve(fixture, candidates, provider, now, relax=False):
    if fixture['probabilities'] is not None or fixture['state'] != 'open' or fixture.get('resolution_blocked'):
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
        else:
            try:
                if c.get('start') and dt(c['start']) == dt(fixture['start']) and set(map(norm,comparable)) & set(map(norm,fixture['teams'])):
                    near.append(c)
            except (ValueError, TypeError, OverflowError):
                continue
    attempt = {'provider': provider, 'status': 'unresolved', 'url': GAMMA+'/sports' if provider == 'Polymarket' else PIN+'/sports/12/markets/straight'}
    if len(exact) > 1:
        attempt['reason'] = 'Multiple same-team, same-time markets; ambiguous identity. No automatic pick.'
    elif len(exact) == 1:
        c, order = exact[0]
        attempt['url'] = c['api_url']
        quote = None
        try:
            if fixture.get('best_of') is not None and (c.get('best_of') is None or str(c['best_of']) != str(fixture['best_of'])):
                raise ValueError('Known series format does not agree with the external source.')
            try:
                quote = (quote_polymarket if provider == 'Polymarket' else quote_pinnacle)(c, order, now)
            except ValueError as strict_error:
                if provider == 'Polymarket' and relax:
                    # Documented second chance: keep every strict gate except the
                    # spread ceiling, and only for a genuinely two-sided, funded,
                    # fresh, open market. Anything else re-raises.
                    quote = quote_polymarket(c, order, now, allow_wide=True)
                    quote['strict_rejection'] = str(strict_error)
                else:
                    raise
            # Copies: a downstream edit of the snapshot must never change the register.
            quote['identity_sources'] = copy.deepcopy([item for item in IDENTITIES if any(plain_name(t) in {plain_name(n) for n in item['names']} for t in c['teams'])])
            if c.get('source_receipts'):
                quote['source_receipts'] = c['source_receipts']
            p = quote['probabilities']
            # A symmetric quote is evidence of a balanced market, but it cannot
            # answer the requested directional pick. Keep its raw fields in the
            # rejected-quote receipt and continue through HLTV/books/VRS rather
            # than publishing a priced row whose pick must be blank. This applies
            # to both strict and wide markets; a wide midpoint is not upgraded to
            # a real estimate merely because it later acquires a tiny imbalance.
            if abs(p[0] - p[1]) < .0001:
                raise ValueError('Verified prices are exactly even (50/50); no directional edge. '
                                 'The quote is retained as rejected evidence and research continues.')
            if c.get('team_metadata'):
                quote['team_metadata'] = c['team_metadata']
            fixture.update(probabilities=p, fair_odds=[1/x for x in p],
                pick=fixture['teams'][0 if p[0]>p[1] else 1],
                method=('exchange_wide' if quote.get('tier') == 'wide_exchange' else ('exchange' if provider == 'Polymarket' else 'bookmaker_fallback')),
                evidence=[quote], reason=None)
            if quote.get('warning'):
                fixture['flags'].append(quote['warning'])
            attempt.update(status='resolved',reason='Exact pair and UTC start; two-way series winner validated.' + (' Low-confidence spread tier used; strict rejection: ' + quote['strict_rejection'] if quote.get('strict_rejection') else ''))
        except (ValueError, TypeError, KeyError) as e:
            attempt['reason'] = str(e)
            attempt['rejected_quote'] = {k:c.get(k) for k in ('provider','id','teams','start','observed_at','updated_at','raw','api_url','source_receipts')}
            if quote is not None:
                for key in ('probabilities', 'decimal_odds', 'spread', 'liquidity', 'tier', 'warning', 'strict_rejection'):
                    if key in quote:
                        attempt['rejected_quote'][key] = copy.deepcopy(quote[key])
            attempt['rejected_quote']['notice'] = 'Rejected evidence, not a pick or verified probability.'
    elif near:
        attempt.update(reason='Unverified opponent/alias or roster-name mismatch; no fuzzy match used.', candidates=[{'teams': c['teams'],'url':c['api_url']} for c in near])
    else:
        attempt['reason'] = 'No exact team-pair and UTC-start match in retrieved feed.'
    fixture['attempts'].append(attempt)


def _alias_source(fixture_team, hltv_label):
    """Primary link for a registered label mapping, or None. No fuzzy match."""
    if plain_name(hltv_label) == plain_name(fixture_team):
        return None
    alias = next((item for item in IDENTITIES
        if any(plain_name(n) == plain_name(fixture_team) for n in item['names'])
        and any(plain_name(n) == plain_name(hltv_label) for n in item['names'])), None)
    return alias.get('source') if alias else None


def _team_page_rank_rows(fixture):
    """Per-team HLTV world ranks from the clubs' own exact-heading team pages.

    Fallback evidence for a fixture HLTV does not list at all (session
    174afa4f): ``scripts.hltv.team_pages`` already resolves each Hotspawn
    label to exactly one HLTV team page by that page's own heading and
    records ``world_rank`` / ``world_rank_status`` / ``world_rank_source``
    per club, but the rank ladder never read them, so such fixtures could
    end with no pick even while both ranks sat on the row. The pairing
    itself comes from the official Hotspawn fixture; each page proves only
    its own club's rank. Returns one resolved row per fixture team, or
    ``None`` unless *both* pages are present and re-verify here:

    * exactly one stored page per fixture label, on an
      ``https://www.hltv.org/team/`` URL with an observation time;
    * the page heading still normalizes to the fixture label (exact, or a
      registered alias with its primary source);
    * ``ranked`` only with a positive integer rank; ``unranked`` only when
      HLTV stated the absence in words at collection time; anything else is
      ``rank_unknown`` and can never support a one-sided claim.
    """
    pages = fixture.get('hltv_team_pages') or {}
    rows = [r for r in pages.get('teams') or [] if isinstance(r, dict) and r.get('team')]
    if len(rows) != 2:
        return None
    resolved = []
    for team in fixture['teams']:
        hits = [r for r in rows if norm(r['team']) == norm(team)]
        if len(hits) != 1:
            return None
        row = hits[0]
        heading = row.get('label')
        url = row.get('url') or ''
        if not heading or norm(heading) != norm(team) \
                or not str(url).startswith('https://www.hltv.org/team/') \
                or not row.get('observed_at'):
            return None
        rank = row.get('world_rank')
        stated = row.get('world_rank_status')
        base = {'team': team, 'hltv_name': heading,
                'alias_source': _alias_source(team, heading),
                'evidence': 'hltv_team_pages', 'team_page_url': url}
        if stated == 'ranked' and isinstance(rank, int) and rank > 0:
            resolved.append(base | {'hltv_rank': rank,
                'rank_source': row.get('world_rank_source') if isinstance(row.get('world_rank_source'), str) else None,
                'status': 'ranked'})
        elif stated == 'unranked' and rank is None:
            resolved.append(base | {'hltv_rank': None, 'rank_source': None, 'status': 'unranked'})
        else:
            resolved.append(base | {'hltv_rank': None, 'rank_source': None, 'status': 'rank_unknown'})
    return resolved


def rank_resolution(fixture):
    """Map each fixture team to its HLTV world-ranking row, fully sourced.

    The published snapshot must carry the evidence the pick rests on, including
    the HLTV team label when it differs from the Hotspawn label and the primary
    link for that identity mapping. Nothing here guesses a rank or an alias.

    The fixture page's own ranking rows win whenever HLTV published any;
    only when it published none do the clubs' own team pages answer (see
    ``_team_page_rank_rows``), marked ``evidence: hltv_team_pages`` so the
    validators replay them from the team-page record, never as a fixture
    page that does not exist.
    """
    context = fixture.get('hltv_context') or {}
    rows = [r for r in context.get('ranks', []) if isinstance(r, dict) and r.get('team')]
    resolved = []
    for team in fixture['teams']:
        hits = [r for r in rows if norm(r['team']) == norm(team)]
        if len(hits) != 1:
            resolved.append({'team': team, 'hltv_name': None, 'hltv_rank': None,
                'rank_source': None, 'alias_source': None,
                'status': 'ambiguous_rank_rows' if hits else 'no_rank_row'})
            continue
        row = hits[0]
        rank = row.get('hltv_rank')
        resolved.append({'team': team, 'hltv_name': row['team'],
            'hltv_rank': rank if isinstance(rank, int) and rank > 0 else None,
            'rank_source': row.get('source') if isinstance(row.get('source'), str) else None,
            'alias_source': _alias_source(team, row['team']),
            'status': 'ranked' if isinstance(rank, int) and rank > 0 else 'unranked'})
    if rows:
        return context, resolved
    team_rows = _team_page_rank_rows(fixture)
    if team_rows is not None:
        return {}, team_rows
    return context, resolved


def research_rank_pick(fixture, receipts=None, now=None):
    """Last-resort research pick for a fixture with no verified market line.

    First tries a researched two-way book-listing receipt (scripts.core.
    book_research_pick), which publishes ordinary bookmaker probabilities.
    Only when no listed line exists does the rank ladder run. That ladder
    reads HLTV world rankings from an exact-identity HLTV match record
    (same opponent pair and UTC start) when HLTV lists the fixture, or —
    when it does not — from each club's own exact-heading HLTV team page
    (``_team_page_rank_rows``; the pairing is then the official Hotspawn
    fixture itself, and an ``unranked`` side counts only where HLTV states
    the absence in words). It produces two documented cases with no
    probability at all:

    * ``research_rank`` - both teams carry a published HLTV world ranking.
    * ``research_rank_single`` - exactly one team does, and the other team
      is shown without a world ranking by the same HLTV evidence.

    Every case stores the per-team evidence (fixture label, HLTV label, rank,
    ranking link, and the primary link for any label mapping) on the row, so an
    independent audit can re-derive the pick from the snapshot alone. No
    probability, fair odds or rank-to-win formula is ever published here.
    """
    if fixture['probabilities'] is not None or fixture['state'] != 'open' or fixture.get('resolution_blocked'):
        return
    if fixture.get('pick'):
        return
    # A researched two-way book line outranks ranking order: it is a real
    # market price, and the rank tiers below publish no probability at all.
    book_research_pick(fixture, receipts=receipts, now=now)
    if fixture['probabilities'] is not None:
        return
    context, resolved = rank_resolution(fixture)
    team_pages_mode = bool(resolved) and all(r.get('evidence') == 'hltv_team_pages' for r in resolved)
    if team_pages_mode:
        # Stored with the team-page record it was derived from, never as a
        # fixture page: HLTV published no fixture page for this pairing.
        fixture['hltv_team_pages'] = (fixture.get('hltv_team_pages') or {}) | {'resolved_ranks': resolved}
        attempt_url = next((r.get('team_page_url') for r in resolved if r.get('team_page_url')),
                           'https://www.hltv.org/ranking/teams')
    else:
        if context:
            fixture['hltv_context'] = context | {'resolved_ranks': resolved}
        attempt_url = context.get('source') or 'https://www.hltv.org/ranking/teams'
    ranked = [r for r in resolved if r.get('hltv_rank')]
    sourced = all(str(r.get('rank_source') or '').startswith('https://www.hltv.org/') for r in ranked)
    labelled = all(r.get('hltv_name') and (plain_name(r['hltv_name']) == plain_name(r['team'])
        or str(r.get('alias_source') or '').startswith('https://')) for r in ranked)
    if len(ranked) == 2 and sourced and labelled and ranked[0]['hltv_rank'] != ranked[1]['hltv_rank']:
        winner, loser = sorted(ranked, key=lambda r: r['hltv_rank'])
        where = ('on their HLTV team pages; HLTV lists no fixture page for this pairing'
                 if team_pages_mode else 'in the same fixture')
        fixture.update(pick=winner['team'], method='research_rank', probabilities=None, fair_odds=None,
            reason=('No verified market line. Research pick only: %s is HLTV world #%d (%s) against %s at #%d (%s) %s. This is a ranking-order signal, not a market probability.'
                % (winner['team'], winner['hltv_rank'], winner['hltv_name'], loser['team'], loser['hltv_rank'], loser['hltv_name'], where)))
        fixture['flags'].append('Research pick without a market line: qualitative evidence only, no probability published.')
        fixture['attempts'].append({'provider': 'Rank research', 'status': 'resolved',
            'reason': ('Both clubs\' exact HLTV team-page world rankings used; HLTV lists no fixture page for this pairing; no probability derived.'
                       if team_pages_mode else
                       'Exact HLTV fixture identity and both world rankings used; no probability derived.'),
            'url': attempt_url})
        return
    if len(ranked) == 1 and sourced and labelled:
        winner = ranked[0]
        loser = next(r for r in resolved if r is not winner)
        if loser.get('status') not in ('unranked', 'no_rank_row'):
            # Conflicting ranking rows for the other team mean the one-sided
            # claim ("the other team has no published world ranking") is false.
            # A team page that is merely silent about rank ('rank_unknown')
            # blocks the claim the same way: silence is not an absence.
            fixture['attempts'].append({'provider': 'Rank research', 'status': 'unresolved',
                'reason': 'No verified market line and the other team has conflicting or unusable HLTV ranking rows, so the one-sided ranking claim cannot be made. No pick invented.',
                'url': attempt_url})
            return
        absence = ('HLTV states %s has no world rank on its team page; HLTV lists no fixture page for this pairing'
                   % loser['team'] if team_pages_mode else
                   '%s appears in the same HLTV fixture without a world-ranking number' % loser['team'])
        fixture.update(pick=winner['team'], method='research_rank_single', probabilities=None, fair_odds=None,
            reason=('No verified market line. Research pick only: %s is HLTV world #%d (%s) while %s. One-sided ranking evidence, not a market probability, and no percentage is published.'
                % (winner['team'], winner['hltv_rank'], winner['hltv_name'], absence)))
        fixture['flags'].append('Research pick on one-sided ranking evidence (only one team is world-ranked): no probability published.')
        fixture['attempts'].append({'provider': 'Rank research', 'status': 'resolved',
            'reason': ('Exact HLTV team pages: one club world-ranked, the other stated by HLTV to have no world rank. No probability derived.'
                       if team_pages_mode else
                       'Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived.'),
            'url': attempt_url})
        return
    problems = []
    if len(ranked) == 2 and ranked[0]['hltv_rank'] == ranked[1]['hltv_rank']:
        problems.append('both teams share the same world ranking')
    if ranked and not sourced:
        problems.append('a ranking number has no HLTV ranking link')
    if ranked and not labelled:
        problems.append('an HLTV team label differs from the fixture label with no registered identity source')
    if not ranked:
        problems.append('neither team carries a world-ranking number on its HLTV team page'
                        if team_pages_mode else
                        'neither team carries a world-ranking number in this fixture')
    fixture['attempts'].append({'provider': 'Rank research', 'status': 'unresolved',
        'reason': 'No verified market line and no usable HLTV ranking evidence: ' + '; '.join(problems) + '. No pick invented.',
        'url': attempt_url})


# A form comparison needs at least this many completed results on each side
# before "recent form" describes anything at all; below it the fixture stays
# unresolved rather than dressing one match up as a trend.
MIN_FORM_MATCHES = 3
MAX_FORM_WINDOW = 10


def form_resolution(fixture):
    """Map each fixture team to its HLTV recent-results row, fully sourced.

    Reads only the ``form`` and ``head_to_head`` evidence that
    ``scripts.hltv.context`` parsed from the exact-identity match page, and
    maps HLTV labels to fixture labels through the context's own
    ``team_map`` (derived from the exact pair/start check). Returns
    ``(context, resolved, head_to_head)`` where ``resolved`` is one dict per
    fixture team, in fixture order: its label, HLTV label and parsed results
    (most recent first), or an explicit ``status`` saying why it is unusable.
    Nothing here guesses a label, a result or a win.
    """
    context = fixture.get('hltv_context') or {}
    form = context.get('form') if isinstance(context.get('form'), dict) else {}
    team_map = context.get('team_map') if isinstance(context.get('team_map'), dict) else {}
    by_fixture = {}
    for hltv_label, fixture_label in team_map.items():
        if fixture_label in fixture['teams'] and hltv_label in form:
            by_fixture.setdefault(fixture_label, []).append(hltv_label)
    resolved = []
    for team in fixture['teams']:
        hits = by_fixture.get(team, [])
        results = [r for r in (form.get(hits[0]) if len(hits) == 1 else []) or []
                   if isinstance(r, dict) and isinstance(r.get('won'), bool) and r.get('opponent') and r.get('score')]
        if len(hits) == 1 and len(results) >= MIN_FORM_MATCHES:
            resolved.append({'team': team, 'hltv_name': hits[0], 'status': 'form_recorded',
                             'results': results})
            continue
        resolved.append({'team': team,
                         'hltv_name': hits[0] if len(hits) == 1 else None,
                         'status': ('ambiguous_form_rows' if len(hits) > 1
                                    else ('insufficient_results' if hits else 'no_form_row')),
                         'results': results})
    h2h = context.get('head_to_head') if isinstance(context.get('head_to_head'), dict) else None
    mapped_h2h = None
    if h2h and isinstance(h2h.get('teams'), list) and len(h2h['teams']) == 2 \
            and isinstance(h2h.get('wins'), list) and len(h2h['wins']) == 2 \
            and all(isinstance(w, int) and w >= 0 for w in h2h['wins']) \
            and all(label in team_map for label in h2h['teams']):
        mapped_h2h = {'wins': {team_map[h2h['teams'][i]]: h2h['wins'][i] for i in (0, 1)},
                      'overtimes': h2h.get('overtimes') if isinstance(h2h.get('overtimes'), int) else None,
                      'hltv_teams': list(h2h['teams']),
                      'hltv_wins': list(h2h['wins'])}
    return context, resolved, mapped_h2h


def research_form_pick(fixture):
    """Final research pick: HLTV recent form, then lifetime head-to-head.

    This is the last rung of the ladder, for a fixture that no market line, no
    bookmaker listing, no originated VRS model line and no ranking or
    one-sided standings evidence could resolve. It reads the completed
    results HLTV publishes on the fixture's own exact-identity match page:

    * both teams need at least ``MIN_FORM_MATCHES`` parsed results;
    * the comparison window is ``min(results_a, results_b, MAX_FORM_WINDOW)``
      so both sides are judged over the same number of recent matches;
    * more wins in that window is the pick (``basis='recent_form'``);
    * an exact win tie falls to HLTV's lifetime head-to-head series wins for
      this pairing (``basis='head_to_head'``);
    * still tied, or any identity/evidence gap, leaves the fixture
      unresolved with the reason recorded. No coin is flipped.

    The per-team evidence (every result used, win totals, the window and the
    basis) is stored on the row, so the validator and the independent audit
    re-derive the pick from the snapshot alone. Recent form is a weak,
    opponent-agnostic signal: no probability, fair odds or form-to-win
    formula is ever published from it.
    """
    if fixture['probabilities'] is not None or fixture['state'] != 'open' or fixture.get('resolution_blocked'):
        return
    if fixture.get('pick'):
        return
    context, resolved, h2h = form_resolution(fixture)
    source = context.get('source') or 'https://www.hltv.org/matches'
    problems = []
    if not str(context.get('source') or '').startswith('https://www.hltv.org/'):
        problems.append('no HLTV match page with this exact fixture identity was read')
    for row in resolved:
        if row['status'] != 'form_recorded':
            problems.append('%s: %s' % (row['team'], {
                'ambiguous_form_rows': 'more than one HLTV form box maps to this label',
                'insufficient_results': 'fewer than %d completed results on the HLTV match page' % MIN_FORM_MATCHES,
                'no_form_row': 'no recent-results box for this label on the HLTV match page',
            }[row['status']]))
    if problems:
        fixture['attempts'].append({'provider': 'Form research', 'status': 'unresolved',
            'reason': 'No verified market line, model line or ranking evidence, and recent form is unusable: '
                      + '; '.join(problems) + '. No pick invented.',
            'url': source})
        return
    window = min(min(len(r['results']) for r in resolved), MAX_FORM_WINDOW)
    for row in resolved:
        row['results'] = row['results'][:window]
        row['wins'] = sum(1 for r in row['results'] if r['won'])
        row['losses'] = window - row['wins']
        row['window'] = window
    a, b = resolved
    winner = basis = None
    if a['wins'] != b['wins']:
        winner, loser, basis = (a, b, 'recent_form') if a['wins'] > b['wins'] else (b, a, 'recent_form')
    elif h2h and h2h['wins'][a['team']] != h2h['wins'][b['team']]:
        winner, loser, basis = ((a, b, 'head_to_head') if h2h['wins'][a['team']] > h2h['wins'][b['team']]
                                else (b, a, 'head_to_head'))
    if winner is None:
        fixture['attempts'].append({'provider': 'Form research', 'status': 'unresolved',
            'reason': ('No verified market line, model line or ranking evidence; recent form is level at '
                       '%d wins each over the last %d matches%s. No pick invented.'
                       % (a['wins'], window,
                          ' and the lifetime head-to-head is level at %d series wins each' % h2h['wins'][a['team']]
                          if h2h else ' and HLTV publishes no head-to-head summary for this pairing')),
            'url': source})
        return
    detail = {'window': window, 'basis': basis,
              'head_to_head': ({'wins': h2h['wins'], 'overtimes': h2h['overtimes']} if h2h else None)}
    fixture['hltv_context'] = context | {'resolved_form': resolved, 'form_detail': detail}
    if basis == 'recent_form':
        why = ('%s won %d of its last %d completed matches on the HLTV match page against %d of %d for %s'
               % (winner['team'], winner['wins'], window, loser['wins'], window, loser['team']))
    else:
        why = ('recent form is level at %d wins each over the last %d matches, and HLTV\'s lifetime '
               'head-to-head for this pairing favours %s %d series wins to %d'
               % (a['wins'], window, winner['team'], h2h['wins'][winner['team']], h2h['wins'][loser['team']]))
    fixture.update(pick=winner['team'], method='research_form', probabilities=None, fair_odds=None,
        reason=('No verified market line. Research pick only: ' + why + ' (exact fixture page: ' + source + '). '
                'This is a recent-results signal only, not a market probability, and no percentage is published.'))
    fixture['flags'].append('Research pick on HLTV recent form'
                            + ('' if basis == 'recent_form' else ' and head-to-head')
                            + ' (weakest sourced signal; opponent strength is not weighted): no probability published.')
    fixture['attempts'].append({'provider': 'Form research', 'status': 'resolved',
        'reason': 'Exact HLTV fixture identity; recent completed results for both teams compared over a %d-match window%s. No probability derived.'
                  % (window, '' if basis == 'recent_form' else ', level, then settled by the page\'s lifetime head-to-head wins'),
        'url': source})


def research_observation(fixture):
    """Timestamp of the actual ranking/standings evidence, not the build time."""
    if not fixture.get('pick'):
        return None
    method = fixture.get('method') or ''
    if method in ('research_rank', 'research_rank_single', 'research_form'):
        context = fixture.get('hltv_context') or {}
        if context.get('resolved_ranks') or method == 'research_form':
            return context.get('observed_at')
        # Team-page rank evidence ages from the older of its two page reads
        # (hltv_team_pages.observed_at is that minimum by construction).
        pages = fixture.get('hltv_team_pages') or {}
        if pages.get('resolved_ranks'):
            return pages.get('observed_at')
        return context.get('observed_at')
    if method == 'research_vrs_single':
        return (fixture.get('vrs_research') or {}).get('observed_at')
    return None


def pick_deadline(fixture, fixture_observed_at):
    """Single recommendation deadline, shared by build and browser.

    A successful fetch must never extend an older source quote's lifetime.
    Missing required timestamps invalidate a recommendation rather than guessing.
    """
    quotes = fixture.get('evidence') or []
    research = research_observation(fixture)
    if not quotes and research is None:
        return None
    try:
        deadlines = [dt(fixture_observed_at) + timedelta(seconds=MAX_AGE),
                     dt(fixture['start']), dt(fixture['lock'])]
        if not quotes:
            # A qualitative pick has the same lifetime as a priced one. Missing
            # ranking/standings timestamps fail closed, never become perpetual.
            deadlines.append(dt(research) + timedelta(seconds=MAX_AGE))
        for quote in quotes:
            deadlines.append(dt(quote['observed_at']) + timedelta(seconds=MAX_AGE))
            if quote.get('updated_at'):
                deadlines.append(dt(quote['updated_at']) + timedelta(seconds=MAX_AGE))
            if quote['provider'] == 'Pinnacle':
                deadlines.append(dt(quote['raw']['line']['cutoffAt']))
        return iso(min(deadlines))
    except (ValueError, KeyError, TypeError, OverflowError, OSError):
        return None
