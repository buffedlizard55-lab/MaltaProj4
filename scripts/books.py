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

* the JSON-LD name pair (``"A vs B"``) maps to the receipt's teams through the
  receipt's own alias lists (``scripts.core.norm``), never fuzzy matching;
* the JSON-LD ``startDate`` equals the receipt's stored UTC start exactly;
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

from scripts.core import BOOK_RECEIPTS, book_candidate, fresh, iso, norm, quote_book

# The page embeds schema.org JSON as compact JSON in script bodies. The
# rendered reads of 2026-10-19 show name/startDate/competitor fragments in the
# form {"name":"Lavked VS ex-6666","description":"...","startDate":"2026-10-20T17:00:00.000Z",...}.
NAME_VS_RE = re.compile(r'"name"\s*:\s*"([^"\\]+?)\s+VS\s+([^"\\]+?)"')
START_RE = re.compile(r'"startDate"\s*:\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)"')
# After tag-stripping, the odds widget reads "Label1 od1 Make a bet od2".
MAKE_BET_RE = re.compile(r'(\d+\.\d+)\s+Make a bet\s+(\d+\.\d+)')
STAVKA_NAME_RE = re.compile(r'"name"\s*:\s*"([^"\\]+?)\s*(?:—|–)\s*([^"\\]+?)"')
STAVKA_START_RE = re.compile(r'"startDate"\s*:\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))"')
STAVKA_WINLINE_RE = re.compile(r'П1\s*(\d+\.\d+)\s*П2\s*(\d+\.\d+)')
TAG_RE = re.compile(r'<[^>]+>')
NUMBER = r'\d+\.\d+'

PLACEHOLDER = (1.8, 1.8)


def _stripped(html):
    return TAG_RE.sub(' ', html)


def parse_listing(html):
    """Extract every (team pair, UTC start, odds pair) the page states.

    Returns a list of candidate readings; an empty list is a parse miss. Each
    reading carries the JSON-LD names as displayed and the odds pair in page
    order (first side, second side).
    """
    readings = []
    if not isinstance(html, str) or not html:
        return readings
    text = _stripped(html)
    # JSON-LD name/start pairs. A start within 400 characters of the name is
    # treated as that event's start (the fragment layout observed on the live
    # pages); anything else is ignored rather than guessed.
    starts = [(m.start(), m.group(1)) for m in START_RE.finditer(html)]
    for name_match in NAME_VS_RE.finditer(html):
        team1, team2 = name_match.group(1).strip(), name_match.group(2).strip()
        start = None
        for pos, value in starts:
            if 0 <= pos - name_match.start() <= 400:
                start = value
                break
        if not start:
            continue
        # Bind the odds pair to the first team label when possible. The widget
        # order observed everywhere is: team1 name, team1 odds, "Make a bet",
        # team2 odds. A pair that cannot be bound to both labels is still
        # recorded, but marked unbound so callers can require the binding.
        bound, pair = None, None
        for make in MAKE_BET_RE.finditer(text):
            try:
                odds = (float(make.group(1)), float(make.group(2)))
            except ValueError:
                continue
            if odds == PLACEHOLDER:
                continue  # the listing's placeholder default: not a market line
            if odds[0] == odds[1]:
                continue  # identical pair: a coin-flip claim we cannot source
            window = text[max(0, make.start() - 240):make.end()]
            m1 = None
            for cand in re.finditer(re.escape(team1) + r'\s*(' + NUMBER + r')', window):
                m1 = cand
            tail = text[make.start(2):make.end() + 240]
            m2 = re.search(re.escape(team2) + r'\s*(' + NUMBER + r')', tail) or \
                 re.search(r'(' + NUMBER + r')\s*' + re.escape(team2), tail)
            ok1 = bool(m1) and abs(float(m1.group(1)) - odds[0]) < 1e-9
            ok2 = bool(m2) and abs(float(m2.group(1)) - odds[1]) < 1e-9
            bound = ok1 and ok2
            pair = odds
            break
        if pair is None:
            continue
        readings.append({'team1': team1, 'team2': team2, 'start': start,
                         'odds': list(pair), 'bound_to_labels': bound})
    # Licensed operator moneyline panel on stavka.tv ("Team1 — Team2" JSON-LD +
    # header "П1 od1 П2 od2"). Empty П1/П2 panels parse as [] (miss, never guessed).
    stavka_starts = [(m.start(), m.group(1)) for m in STAVKA_START_RE.finditer(html)]
    for name_match in STAVKA_NAME_RE.finditer(html):
        team1, team2 = name_match.group(1).strip(), name_match.group(2).strip()
        start = None
        for pos, value in stavka_starts:
            if 0 <= pos - name_match.start() <= 600:
                try:
                    start = iso(value)
                except (TypeError, ValueError):
                    start = None
                break
        if not start:
            continue
        for wl in STAVKA_WINLINE_RE.finditer(text):
            try:
                odds = (float(wl.group(1)), float(wl.group(2)))
            except ValueError:
                continue
            if odds == PLACEHOLDER or odds[0] == odds[1] or min(odds) <= 1.0:
                continue
            window = text[max(0, wl.start() - 600):wl.start()]
            ok1 = norm(team1) in norm(window)
            ok2 = norm(team2) in norm(window)
            readings.append({'team1': team1, 'team2': team2, 'start': start,
                             'odds': list(odds), 'bound_to_labels': bool(ok1 and ok2)})
            break
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
    """Re-read each receipt's listing URL and renew only verified readings.

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
            match = None
            for reading in readings:
                pair = (_comparable(aliases, reading['team1']), _comparable(aliases, reading['team2']))
                if pair != wanted or not reading.get('bound_to_labels'):
                    continue
                try:
                    if iso(reading['start']) != iso(receipt['start']):
                        continue
                except (TypeError, ValueError):
                    continue
                match = reading
                break
            if match is None:
                record.update(status='parse_miss',
                              reason=('No verified re-observation: the live page did not re-confirm the exact '
                                      'team pair, UTC start and an asymmetric two-way pair bound to both labels '
                                      '(the 1.8/1.8 placeholder and unbound pairs are refused). The stored '
                                      'observation stands until it expires.'))
            else:
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
