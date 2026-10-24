"""Re-observe researched book-listing receipts from their own listing pages.

Why this exists
---------------
``data/book-receipts.json`` holds dated observations of two-way bookmaker odds
read from a listing page (the ``bookmaker_fallback`` tier in ``scripts.core``).
Those observations age out under the project's eight-hour evidence window, so a
fixture would fall back to the originated model line even while the book page
still publishes the same price. This module lets the scheduled refresh *re-read*
the exact listing URL and renew the observation — but only when the live page
re-confirms all three identity facts and an asymmetric two-way pair:

* the explicit structured name pair (EGW JSON-LD or canonical STAVKA Nuxt) maps to the receipt's teams through the
  receipt's own alias lists (``scripts.core.norm``), never fuzzy matching;
* the structured, timezone-aware start equals the receipt's stored UTC start exactly;
* the page shows an asymmetric two-way decimal pair bound to those teams
  (``team1 od1 Make a bet od2``). The identical placeholder pair 1.8/1.8 that
  this listing serves when no bookmaker data exists is a parse miss: the
  observation is left stale, never renewed.

A markup change is therefore a recorded parse miss (the receipt keeps its old
observation time and simply expires), never a guessed price. The re-observed
receipt copy — including the new odds and the new observation time — is what
``scripts.core.book_research_pick`` prices from, and the snapshot stores that
copy as the raw evidence the validator replays. Nothing is written back to
``data/book-receipts.json``; the committed file remains the research record.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

from scripts.core import BOOK_RECEIPTS, book_candidate, fresh, iso, norm, quote_book

# Read schema.org identities as JSON objects, never as neighbouring fragments.
# Property order/description length has no identity meaning; a different event's
# startDate must not be borrowed just because it is nearby in the HTML.
NAME_VS_RE = re.compile(r'(.+?)\s+VS\s+(.+)')
NUMBER = r'(?<![\d.])\d+(?:\.\d+)?(?![\d.])'
# After tag-stripping, the odds widget reads "Label1 od1 Make a bet od2" (or
# "Label1 od1 ... Label2 od2 od1 Make a bet od2", including integer odds like 12).
MAKE_BET_RE = re.compile(r'(' + NUMBER + r')\s+Make a bet\s+(' + NUMBER + r')')
STAVKA_NAME_RE = re.compile(r'(.+?)\s*(?:—|–)\s*(.+)')
STAVKA_WINLINE_RE = re.compile(r'П1\s*(' + NUMBER + r')\s*П2\s*(' + NUMBER + r')')

PLACEHOLDER = (1.8, 1.8)


def _unique_object(pairs):
    """JSON duplicate keys are conflicting evidence, not last-value-wins."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON-LD property')
        result[key] = value
    return result


def _listing_event(soup):
    """One unambiguous JSON-LD event, with names/start in the same object.

    Arrays/@graph are supported, but multiple event declarations are refused
    (even duplicate declarations): the unscoped widget cannot establish which
    event it prices. Repeated widgets for one event are handled separately.
    The canonical Nuxt reader remains the source-specific route for STAVKA's
    multi-event payload.
    """
    events, budget = {}, 10_000
    try:
        for script in soup.select('script[type="application/ld+json"]'):
            text = script.get_text()
            if len(text) > 2_000_000:
                return None
            pending = [(json.loads(text, object_pairs_hook=_unique_object), 0)]
            while pending:
                node, depth = pending.pop()
                budget -= 1
                if budget < 0 or depth > 24:
                    return None
                if isinstance(node, list):
                    pending.extend((item, depth + 1) for item in node)
                    continue
                if not isinstance(node, dict):
                    continue
                pending.extend((item, depth + 1) for item in node.values()
                               if isinstance(item, (list, dict)))
                name = node.get('name')
                if not isinstance(name, str):
                    continue
                pair = NAME_VS_RE.fullmatch(name.strip())
                kind = 'egw'
                if pair is None:
                    pair = STAVKA_NAME_RE.fullmatch(name.strip())
                    kind = 'stavka'
                if pair is None:
                    continue
                types = node.get('@type', ['SportsEvent'])
                types = [types] if isinstance(types, str) else types
                if not isinstance(types, list) or not any(t in ('SportsEvent', 'Event') for t in types):
                    continue
                team1, team2 = (part.strip() for part in pair.groups())
                start = node.get('startDate')
                if (not norm(team1) or not norm(team2) or norm(team1) == norm(team2)
                        or not isinstance(start, str)):
                    return None
                utc_start = iso(start)  # timezone must be explicit, never inferred
                for field, expected in (('homeTeam', team1), ('awayTeam', team2)):
                    if field in node:
                        label = node[field]
                        if isinstance(label, dict):
                            label = label.get('name')
                        if not isinstance(label, str) or norm(label) != norm(expected):
                            return None
                if events:
                    return None  # more than one event declaration is ambiguous
                key = (kind, norm(team1), norm(team2), utc_start)
                events[key] = {'team1': team1, 'team2': team2,
                               'start': start if kind == 'egw' else utc_start, 'kind': kind}
    except (ValueError, TypeError, RecursionError, OverflowError):
        return None
    return next(iter(events.values())) if len(events) == 1 else None


def _stavka_nuxt_listing(html):
    """Read the actual canonical-page Nuxt payload, not related-card odds.

    Retained pages use NewsArticle JSON-LD, not SportsEvent/startDate. Nuxt's
    reference table supplies the exact UTC fixture and labelled one_two panel.
    This remains a secondary promotional listing, not verified operator access.
    No JavaScript, embedded expression or arbitrary object hook is executed.
    """
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.select_one('script#__NUXT_DATA__')
    canonical = soup.select_one('link[rel="canonical"]')
    parts = urlsplit(canonical.get('href', '') if canonical else '')
    if not script or parts.scheme != 'https' or parts.hostname not in ('stavka.tv', 'www.stavka.tv'):
        return None  # not this source; retain the other listing parsers
    path = re.fullmatch(r'/matches/csgo/([^/]+)/?', parts.path)
    if not path:
        return []
    try:
        if len(script.get_text()) > 2_000_000:
            return []
        table = json.loads(script.get_text())
        if not isinstance(table, list) or len(table) > 100_000:
            return []

        budget = 50_000

        def deref(index, stack=()):
            nonlocal budget
            budget -= 1
            if budget < 0 or type(index) is not int or not 0 <= index < len(table) or index in stack or len(stack) >= 24:
                raise ValueError('Unverified Nuxt reference')
            value = table[index]
            if isinstance(value, dict):
                return {k: deref(v, stack + (index,)) for k, v in value.items()}
            if isinstance(value, list):
                return [deref(v, stack + (index,)) for v in value]
            return value

        matches = [deref(i) for i, value in enumerate(table)
                   if isinstance(value, dict) and 'promoSettings' in value
                   and 'slug' in value and deref(value['slug']) == path[1]]
        if len(matches) != 1:
            return []
        match = matches[0]
        if (match.get('sportSlug') != 'csgo' or match.get('isLive') is not False
                or match.get('isFinished') is not False or match.get('status') != 0):
            return []
        best_of = match.get('bestOf')
        if type(best_of) is not int or best_of not in (1, 3, 5, 7) or match.get('numberOfGames') != best_of:
            return []
        start = iso(match['matchDate'])  # missing timezone is a refusal
        team1, team2 = (match['teams'][side]['name'] for side in ('home', 'away'))
        if not all(isinstance(n, str) and n.strip() for n in (team1, team2)) or norm(team1) == norm(team2):
            return []
        panel = match['promoSettings']['maxBookmakerOdds']['one_two']
        if not isinstance(panel, list) or len(panel) != 2:
            return []
        sides = {q['outcome']: q for q in panel}
        if set(sides) != {'w1', 'w2'} or any(q.get('type') != 'one_two' or q.get('bookmakerCode') != 'winline' for q in panel):
            return []
        odds = [float(sides[side]['value']) for side in ('w1', 'w2')]
        if odds[0] == odds[1] or any(not 1 < v < float('inf') for v in odds):
            return []
        return [{'team1': team1, 'team2': team2, 'start': start, 'best_of': best_of,
                 'odds': odds, 'bound_to_labels': True,
                 'source_note': 'STAVKA canonical Nuxt promotional one_two panel; operator price timestamp/availability not independently verified.'}]
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError):
        return []  # malformed/changed payload never falls back to unrelated odds


def parse_listing(html):
    """Read a unique event and every labelled two-way widget on its page.

    Identical repeated renderings collapse to one reading. Distinct prices stay
    distinct, so callers can refuse ambiguity rather than choose the first or
    silently mix bookmaker prices. An unrelated first widget cannot hide a later
    verifiable one. Unbound readings remain diagnostic only, never priced.
    """
    if not isinstance(html, str) or not html:
        return []
    if '__NUXT_DATA__' in html:
        nuxt = _stavka_nuxt_listing(html)
        if nuxt is not None:
            return nuxt
    soup = BeautifulSoup(html, 'html.parser')
    event = _listing_event(soup)
    if event is None:
        return []
    team1, team2, start = (event[key] for key in ('team1', 'team2', 'start'))
    # Script/style text is not a displayed quote. BeautifulSoup also decodes
    # escaped label characters before comparing them to the structured names.
    text = soup.get_text(' ', strip=True)
    readings = []
    pattern = MAKE_BET_RE if event['kind'] == 'egw' else STAVKA_WINLINE_RE
    for widget in pattern.finditer(text):
        odds = (float(widget.group(1)), float(widget.group(2)))
        if odds == PLACEHOLDER or odds[0] == odds[1] or any(not 1 < v < float('inf') for v in odds):
            continue
        if event['kind'] == 'egw':
            # Existing witnessed layouts put side two either before the button
            # (alongside side one) or after it. Both labels must repeat the
            # widget's own numbers, not merely occur somewhere on the page.
            window = text[max(0, widget.start() - 240):widget.end()]
            m1 = None
            for candidate in re.finditer(re.escape(team1) + r'\s*(' + NUMBER + r')', window):
                m1 = candidate
            tail = text[widget.start(2):widget.end() + 240]
            m2 = re.search(re.escape(team2) + r'\s*(' + NUMBER + r')', tail) or \
                 re.search(r'(' + NUMBER + r')\s*' + re.escape(team2), tail)
            if m2 is None and m1 is not None:
                for candidate in re.finditer(re.escape(team2) + r'\s*(' + NUMBER + r')', window):
                    if candidate.start() > m1.start():
                        m2 = candidate
            bound = (bool(m1) and abs(float(m1.group(1)) - odds[0]) < 1e-9
                     and bool(m2) and abs(float(m2.group(1)) - odds[1]) < 1e-9)
        else:
            window = text[max(0, widget.start() - 600):widget.start()]
            bound = norm(team1) in norm(window) and norm(team2) in norm(window)
        reading = {'team1': team1, 'team2': team2, 'start': start,
                   'odds': list(odds), 'bound_to_labels': bool(bound)}
        if reading not in readings:
            readings.append(reading)
    return readings


def _comparable(alias_lists, label):
    for aliases in alias_lists:
        if any(norm(a) == norm(label) for a in aliases if a):
            return norm(aliases[0])
    return norm(label)


def for_unpriced(receipts, fixtures):
    """Only re-read listings for open fixtures the featured tiers cannot price.

    Historical receipts remain in the research register, but fetching a closed
    match (or a match already resolved from a current market) cannot improve its
    pick. Avoid spending the refresh's network budget on those unrelated pages.
    Exact pair/start/format validation still happens before any line is used.
    """
    needed = {str(m['id']) for m in fixtures if m.get('state') == 'open'
              and m.get('probabilities') is None and not m.get('resolution_blocked')}
    return [r for r in receipts if str(r.get('fixture_id')) in needed]


def reobserve(receipts, src, now):
    """Re-read each receipt's listing URL and renew only source-bound readings.

    Returns ``(receipts, records)``: the receipt list with renewals applied to
    copies (the committed file is untouched) and one audit record per receipt.
    Any error is recorded and leaves that receipt stale.
    """
    renewed, records = [], []
    for receipt in receipts:
        record = {'id': receipt.get('id'), 'fixture_id': receipt.get('fixture_id'),
                  'url': receipt.get('url'),
                  'reobserved_at': iso(now), 'status': 'not_reobserved'}
        out = receipt
        try:
            html, _evidence = src.get('Book listing re-observation ' + str(receipt.get('id')),
                                      receipt.get('url') or receipt.get('api_url'), False)
        except Exception as exc:  # access failure is data, never a number
            record.update(status='error', reason=str(exc)[:300])
            records.append(record)
            renewed.append(out)
            continue
        try:
            readings = parse_listing(html)
            aliases = receipt.get('team_aliases') or []
            wanted = (_comparable(aliases, receipt['source_teams'][0]),
                      _comparable(aliases, receipt['source_teams'][1]))
            matches = []
            for reading in readings:
                pair = (_comparable(aliases, reading['team1']), _comparable(aliases, reading['team2']))
                if pair != wanted or not reading.get('bound_to_labels'):
                    continue
                if reading.get('best_of') is not None and receipt.get('best_of') is not None and reading['best_of'] != receipt['best_of']:
                    continue  # explicitly contradictory series format
                try:
                    if iso(reading['start']) != iso(receipt['start']):
                        continue
                except (TypeError, ValueError):
                    continue
                if reading not in matches:
                    matches.append(reading)
            if len(matches) != 1:
                record.update(status='parse_miss',
                              reason=('No unique verified re-observation: the live page did not re-confirm '
                                      'one exact team pair, UTC start and asymmetric two-way pair bound to '
                                      'both labels. Ambiguous/conflicting pairs, the 1.8/1.8 placeholder and '
                                      'unbound pairs are refused. The stored observation stands until it expires.'))
            else:
                match = matches[0]
                observed = _evidence.get('observed_at')
                if not fresh(observed, now):
                    raise ValueError('Source observation is missing, invalid or stale; the stored receipt is not renewed.')
                out = dict(receipt)
                out['odds'] = list(match['odds'])
                out['observed_at'] = iso(observed)
                out['source_receipts'] = [dict(_evidence)]
                out['reobserved'] = {
                    'by': 'scripts/books.py reobserve',
                    'observed_at': iso(observed),
                    'source_url': receipt.get('url'),
                    'odds_seen': list(match['odds']),
                    'odds_first_recorded': list(receipt.get('odds') or []),
                }
                record.update(status='renewed', odds=list(match['odds']),
                              reason='Live listing re-confirmed the exact pair, UTC start and an asymmetric '
                                     'two-way pair; observation renewed from the page itself.')
        except Exception as exc:
            record.update(status='error', reason='Parse failure treated as a miss: ' + str(exc)[:300])
        records.append(record)
        renewed.append(out)
    return renewed, records


def watch_unpriced(receipts, fixtures, src, now, register=None):
    """Revisit previously rejected EGW pages for currently unpriced fixtures.

    A rejection is a URL to check, NEVER a price or a reusable identity claim.
    Read the page again, require a unique exact team pair / timezone-aware start,
    both label-bound asymmetric odds and a fresh collector observation. The
    accepted quote remains an explicitly secondary listing estimate; no named
    operator, price-update time, format or percentage is inferred. Newly found
    receipts live only in this run's evidence, not in the curated register.
    """
    if register is None:
        try:
            register = json.loads(Path(BOOK_RECEIPTS).read_text()).get('rejected_listings', [])
        except (OSError, ValueError, AttributeError):
            register = []
    covered = {str(r.get('fixture_id')) for r in receipts}
    needed = {str(m['id']): m for m in fixtures if m.get('state') == 'open'
              and m.get('probabilities') is None and not m.get('resolution_blocked')
              and str(m['id']) not in covered}
    watched, records, accepted = set(), [], []
    for prior in register:
        if not isinstance(prior, dict):
            continue
        ident, url = str(prior.get('fixture_id') or ''), prior.get('url') or ''
        fixture = needed.get(ident)
        if fixture is None or (ident, url) in watched:
            continue
        # Only previously researched public EGW fixture URLs. No guessed slugs,
        # search-result snippets, arbitrary outbound URLs or permission bypasses.
        try:
            parts = urlsplit(url)
            if (parts.scheme != 'https' or parts.netloc != 'egamersworld.com'
                    or not parts.path.startswith('/counterstrike/match/')
                    or parts.query or parts.fragment):
                continue
            if sorted(map(norm, prior.get('teams') or [])) != sorted(map(norm, fixture['teams'])):
                continue
        except (TypeError, ValueError):
            continue
        watched.add((ident, url))
        record = {'provider': 'Book listing gap recheck', 'fixture_id': ident,
                  'url': url, 'status': 'unresolved'}
        try:
            html, evidence = src.get('Book listing gap recheck ' + ident, url, False)
            observed = evidence.get('observed_at')
            if not fresh(observed, now):
                raise ValueError('Source observation is missing, invalid or outside the eight-hour window; no timestamp inferred.')
            candidates = [r for r in parse_listing(html) if r.get('bound_to_labels')
                          and sorted(map(norm, (r['team1'], r['team2']))) == sorted(map(norm, fixture['teams']))
                          and iso(r['start']) == iso(fixture['start'])]
            if len(candidates) != 1:
                raise ValueError('No unique exact pair/start with asymmetric odds bound to both labels; placeholder, unnamed opponent and ambiguous readings are refused.')
            if fixture.get('best_of') is not None:
                raise ValueError('A known fixture format requires a separately verified listing format; none is inferred by this adapter.')
            reading = candidates[0]
            receipt = {
                'provider': 'EGamersWorld book listing', 'id': 'egw-gap-recheck-' + ident,
                'fixture_id': ident, 'source_teams': [reading['team1'], reading['team2']],
                'team_aliases': [[reading['team1']], [reading['team2']]],
                'start': iso(reading['start']), 'odds': list(reading['odds']),
                'observed_at': iso(observed), 'url': url, 'api_url': url,
                'source_receipts': [dict(evidence)],
                'identity_evidence': [
                    {'label': 'Official Hotspawn membership / start only', 'url': fixture['source_url']},
                    {'label': 'Live listing exact team labels and UTC start', 'url': url}],
                'limitation': 'Secondary EGamersWorld listing estimate, not verified single-operator odds. '
                              'No operator attribution or price-update timestamp is supplied. Exact source '
                              'observation time and response receipt are retained; expires within eight hours.',
            }
            # Reuse the established arithmetic/margin/time gate before storing
            # anything as an accepted receipt. A URL's old rejected price is ignored.
            quote_book(book_candidate(receipt), [0, 1], now)
            accepted.append(receipt)
            record.update(status='resolved', reason='Live previously rejected listing now confirms the exact pair, UTC start and label-bound asymmetric prices. Published only as a secondary listing estimate.')
            needed.pop(ident)  # one whole-page quote per fixture, never best-of mixing
        except Exception as exc:
            record['reason'] = str(exc)[:500]
        records.append(record)
    return list(receipts) + accepted, records
