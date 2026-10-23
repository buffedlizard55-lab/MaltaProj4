"""Automated pre-match CS2 moneyline feed via BO3.gg's public JSON API.

Why this exists
---------------
``https://thunderpick.io/esports/cs2-betting`` serves a client-side shell with no
server-rendered odds, and ``https://egamersworld.com/`` answers datacenter IPs on
GitHub Actions runners with HTTP 403 (leaving manually researched book receipts
unable to re-observe past the project's eight-hour evidence window).

BO3.gg's public REST endpoint (``https://api.bo3.gg/api/v1/matches``) returns
structured pre-match CS2 fixtures together with active Thunderpick series
moneyline odds bound explicitly by team IDs, exact ISO-8601 UTC ``start_date``,
series format ``bo_type``, and direct links to both the BO3.gg fixture page and
the Thunderpick match market (``https://thunderpick.io/match/<id>``).

Every accepted candidate passes fail-closed gates:
* ``discipline_id == 1`` and ``game_version == 2`` (Counter-Strike 2 only);
* ``status == 'upcoming'`` with ``end_date is None``, ``winner_team_id is None``
  and ``loser_team_id is None`` (strictly pre-match);
* non-empty ``team1`` / ``team2`` records with distinct positive integer IDs and
  ``discipline_id == 1``;
* ``bet_updates`` present with ``team_1.active is True``, ``team_2.active is True``,
  ``team_1.team_id == team1.id``, ``team_2.team_id == team2.id``;
* finite decimal odds ``> 1.0`` passing ``scripts.core.devig`` margin bounds
  (``-0.02 <= overround <= 0.25``);
* unique exact opponent pair + exact UTC start via ``scripts.core.orientation``
  (exact normalized names or sourced ``data/identities.json`` entries only — never
  fuzzy matching);
* series-format agreement whenever the Hotspawn row specifies ``best_of``;
* fresh HTTP observation inside the eight-hour evidence window.

Accepted quotes use the standard ``book_candidate`` / ``quote_book`` shape
(``method = 'bookmaker_fallback'``) so ``scripts.validate`` and
``verification-c6/audit_snapshot.py`` independently replay every calculation from
retained ``raw`` fields without special cases.
"""
from __future__ import annotations

import copy
import math
from urllib.parse import urlsplit

from scripts.core import book_candidate, devig, fresh, iso, norm, orientation, quote_book

API_BASE = 'https://api.bo3.gg/api/v1'
SITE_BASE = 'https://bo3.gg'
PROVIDER = 'Thunderpick (via BO3.gg API)'
ATTEMPT_PROVIDER = 'Thunderpick (via BO3.gg API)'
PAGE_LIMIT = 100
MAX_PAGES = 6


def page_url(offset: int = 0, limit: int = PAGE_LIMIT) -> str:
    return (
        f'{API_BASE}/matches?page[offset]={int(offset)}&page[limit]={int(limit)}'
        '&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1'
        '&sort=start_date&with=teams,tournament'
    )


def _valid_https(url: object, allowed_hosts: tuple[str, ...]) -> bool:
    if not isinstance(url, str) or not url.strip():
        return False
    parts = urlsplit(url.strip())
    return parts.scheme == 'https' and parts.netloc in allowed_hosts and bool(parts.path and parts.path != '/')


def parse_match_row(row: object, observed_at: str, feed_url: str, source_receipt: dict | None = None) -> tuple[dict | None, str]:
    """Validate one raw ``api.bo3.gg`` match object.

    Returns ``(parsed_entry, status_reason)``. When ``row`` is a valid CS2 upcoming
    series whose ``bet_updates`` are absent or inactive, ``parsed_entry`` is still
    returned with ``priced = False`` so callers can log an exact diagnostic attempt
    without inventing any number. Malformed or non-CS2 rows return ``(None, reason)``.
    """
    if not isinstance(row, dict):
        return None, 'row is not an object'
    if row.get('discipline_id') != 1 or row.get('game_version') != 2:
        return None, 'not a Counter-Strike 2 match'
    if (row.get('status') != 'upcoming' or row.get('end_date') is not None
            or row.get('winner_team_id') is not None or row.get('loser_team_id') is not None):
        return None, 'not an unstarted upcoming match'
    match_id = row.get('id')
    slug = row.get('slug')
    if not isinstance(match_id, int) or isinstance(match_id, bool) or match_id <= 0:
        return None, 'missing positive integer match id'
    if not isinstance(slug, str) or not slug.strip() or '/' in slug or '?' in slug or '#' in slug:
        return None, 'missing or invalid match slug'
    t1 = row.get('team1')
    t2 = row.get('team2')
    if not isinstance(t1, dict) or not isinstance(t2, dict):
        return None, 'TBA or missing team object'
    id1, id2 = t1.get('id'), t2.get('id')
    name1, name2 = t1.get('name'), t2.get('name')
    if (not isinstance(id1, int) or isinstance(id1, bool) or id1 <= 0
            or not isinstance(id2, int) or isinstance(id2, bool) or id2 <= 0
            or id1 == id2):
        return None, 'invalid or identical team ids'
    if t1.get('discipline_id') not in (None, 1) or t2.get('discipline_id') not in (None, 1):
        return None, 'non-CS2 team discipline'
    if (not isinstance(name1, str) or not name1.strip()
            or not isinstance(name2, str) or not name2.strip()
            or norm(name1) == norm(name2)):
        return None, 'missing or identical team labels'
    try:
        start_iso = iso(row.get('start_date'))
    except (TypeError, ValueError, OverflowError, OSError):
        return None, 'missing or non-UTC start_date'
    bo_type = row.get('bo_type')
    best_of = bo_type if type(bo_type) is int and bo_type in (1, 2, 3, 5, 7) else None
    match_url = f'{SITE_BASE}/matches/{slug.strip()}'

    base = {
        'bo3_id': match_id,
        'slug': slug.strip(),
        'teams': [name1.strip(), name2.strip()],
        'team_ids': [id1, id2],
        'start': start_iso,
        'best_of': best_of,
        'url': match_url,
        'api_url': feed_url,
        'observed_at': iso(observed_at),
        'tournament': ((row.get('tournament') or {}).get('name')
                       if isinstance(row.get('tournament'), dict) else None),
        'priced': False,
        'odds': None,
        'book_provider': None,
        'book_url': None,
        'source_receipt': copy.deepcopy(source_receipt) if isinstance(source_receipt, dict) else None,
    }

    bet = row.get('bet_updates')
    if not isinstance(bet, dict):
        base['unpriced_reason'] = 'Fixture found on BO3.gg with exact UTC start, but no active sportsbook moneyline is posted yet (bet_updates is null).'
        return base, base['unpriced_reason']

    b1 = bet.get('team_1')
    b2 = bet.get('team_2')
    if not isinstance(b1, dict) or not isinstance(b2, dict):
        base['unpriced_reason'] = 'BO3.gg bet_updates lacks two team quote objects.'
        return base, base['unpriced_reason']
    if b1.get('active') is not True or b2.get('active') is not True:
        base['unpriced_reason'] = 'Sportsbook quote on BO3.gg is marked inactive/suspended.'
        return base, base['unpriced_reason']
    if b1.get('team_id') != id1 or b2.get('team_id') != id2:
        base['unpriced_reason'] = 'BO3.gg bet_updates team_id does not bind 1-to-1 to team1/team2.'
        return base, base['unpriced_reason']
    if b1.get('name') and norm(str(b1['name'])) != norm(name1):
        base['unpriced_reason'] = 'BO3.gg bet_updates team_1 label disagrees with team1.name.'
        return base, base['unpriced_reason']
    if b2.get('name') and norm(str(b2['name'])) != norm(name2):
        base['unpriced_reason'] = 'BO3.gg bet_updates team_2 label disagrees with team2.name.'
        return base, base['unpriced_reason']

    try:
        c1, c2 = float(b1.get('coeff')), float(b2.get('coeff'))
    except (TypeError, ValueError):
        base['unpriced_reason'] = 'BO3.gg bet_updates coefficients are non-numeric.'
        return base, base['unpriced_reason']
    if not (math.isfinite(c1) and math.isfinite(c2) and c1 > 1.0 and c2 > 1.0):
        base['unpriced_reason'] = 'BO3.gg bet_updates decimal odds must both exceed 1.0.'
        return base, base['unpriced_reason']
    try:
        _, margin = devig([c1, c2])
    except ValueError as exc:
        base['unpriced_reason'] = f'BO3.gg bet_updates failed devig gate: {exc}'
        return base, base['unpriced_reason']
    if not (-0.02 <= margin <= 0.25):
        base['unpriced_reason'] = f'BO3.gg sportsbook margin {margin:.4f} outside [-0.02, 0.25] gate.'
        return base, base['unpriced_reason']

    book_provider = str(bet.get('provider') or '').strip()
    if not book_provider:
        base['unpriced_reason'] = 'BO3.gg bet_updates omits sportsbook provider identifier.'
        return base, base['unpriced_reason']
    book_path = bet.get('path')
    book_url = book_path.strip() if _valid_https(book_path, ('thunderpick.io', 'www.thunderpick.io')) else None

    base.update(
        priced=True,
        odds=[c1, c2],
        book_provider=book_provider,
        book_url=book_url,
        markets_count=bet.get('markets_count') if isinstance(bet.get('markets_count'), int) else None,
        raw_bet_updates={
            'provider': book_provider,
            'path': book_url,
            'markets_count': bet.get('markets_count') if isinstance(bet.get('markets_count'), int) else None,
            'team_1': {'team_id': id1, 'name': b1.get('name'), 'coeff': c1, 'active': True},
            'team_2': {'team_id': id2, 'name': b2.get('name'), 'coeff': c2, 'active': True},
        },
    )
    return base, 'ok'


def parse_feed_page(payload: object, observed_at: str, feed_url: str, source_receipt: dict | None = None) -> list[dict]:
    """Validate a paginated ``api.bo3.gg/api/v1/matches`` response."""
    if not isinstance(payload, dict) or not isinstance(payload.get('results'), list):
        raise ValueError('Unrecognized BO3.gg matches schema')
    out: list[dict] = []
    for raw_row in payload['results']:
        parsed, _ = parse_match_row(raw_row, observed_at, feed_url, source_receipt)
        if parsed is not None:
            out.append(parsed)
    return out


def fetch_entries(src) -> tuple[list[dict], list[dict]]:
    """Fetch upcoming CS2 series from ``api.bo3.gg`` using ``Sources.get``.

    Returns ``(entries, errors)``. Never raises; network/schema failures are
    recorded cleanly in ``errors``.
    """
    entries: list[dict] = []
    errors: list[dict] = []
    for page in range(MAX_PAGES):
        url = page_url(page * PAGE_LIMIT, PAGE_LIMIT)
        try:
            payload, receipt = src.get(f'BO3.gg CS2 upcoming feed page {page + 1}', url, True)
            batch = parse_feed_page(payload, receipt['observed_at'], url, receipt)
        except Exception as exc:
            errors.append({'url': url, 'error': str(exc)[:300]})
            break
        entries.extend(batch)
        results = payload.get('results') or []
        total_pages = ((payload.get('total') or {}).get('pages')
                       if isinstance(payload.get('total'), dict) else None)
        if len(results) < PAGE_LIMIT or (isinstance(total_pages, int) and page + 1 >= total_pages):
            break
    return entries, errors


def build_receipt_for_fixture(fixture: dict, entries: list[dict], now) -> tuple[dict | None, dict]:
    """Match one open unpriced ``fixture`` against ``entries``.

    Returns ``(receipt_or_none, attempt_record)``. Requires a unique exact
    opponent-pair and UTC-start match and validates the resulting receipt through
    ``book_candidate`` + ``quote_book`` before returning it.
    """
    exact = [e for e in entries if orientation(fixture, e['teams'], e['start']) is not None]
    if not exact:
        return None, {
            'provider': ATTEMPT_PROVIDER,
            'status': 'unresolved',
            'url': page_url(0, PAGE_LIMIT),
            'reason': 'No exact team-pair and UTC-start match in the live BO3.gg CS2 feed.',
        }
    if len(exact) > 1:
        return None, {
            'provider': ATTEMPT_PROVIDER,
            'status': 'unresolved',
            'url': exact[0]['url'],
            'reason': f'{len(exact)} duplicate BO3.gg entries matched the same pair and UTC start; ambiguous listing refused.',
        }
    entry = exact[0]
    if not fresh(entry['observed_at'], now):
        return None, {
            'provider': ATTEMPT_PROVIDER,
            'status': 'unresolved',
            'url': entry['url'],
            'reason': 'BO3.gg observation timestamp is outside the 8-hour freshness window.',
        }
    if not entry.get('priced'):
        return None, {
            'provider': ATTEMPT_PROVIDER,
            'status': 'unresolved',
            'url': entry['url'],
            'reason': entry.get('unpriced_reason') or 'No active two-way sportsbook moneyline posted on BO3.gg.',
        }
    if fixture.get('best_of') is not None and (entry.get('best_of') is None or int(entry['best_of']) != int(fixture['best_of'])):
        return None, {
            'provider': ATTEMPT_PROVIDER,
            'status': 'unresolved',
            'url': entry['url'],
            'reason': 'Known Hotspawn series format differs from BO3.gg bo_type; refused.',
        }

    corroboration = [
        {'label': 'BO3.gg CS2 match page', 'url': entry['url']},
    ]
    if entry.get('book_url'):
        corroboration.insert(0, {
            'label': f"Direct {entry['book_provider'].title()} match market ({entry['odds'][0]} / {entry['odds'][1]})",
            'url': entry['book_url'],
        })

    receipt = {
        'provider': PROVIDER,
        'id': f"bo3-{entry['book_provider']}-{entry['bo3_id']}",
        'fixture_id': str(fixture['id']),
        'source_teams': list(entry['teams']),
        'team_aliases': [[entry['teams'][0]], [entry['teams'][1]]],
        'alias_sources': [entry['url'], entry['url']],
        'start': entry['start'],
        'best_of': entry['best_of'],
        'odds': list(entry['odds']),
        'observed_at': entry['observed_at'],
        'url': entry['url'],
        'api_url': entry['api_url'],
        'event': entry.get('tournament') or fixture.get('competition'),
        'source_receipts': [entry['source_receipt']] if entry.get('source_receipt') else [],
        'identity_evidence': [
            {'label': 'Official Hotspawn fixture membership and UTC schedule', 'url': fixture['source_url']},
            {'label': f"BO3.gg CS2 match {entry['bo3_id']} ({entry['teams'][0]} vs {entry['teams'][1]}, {entry['start']})", 'url': entry['url']},
        ],
        'corroboration': corroboration,
        'raw_bo3': entry.get('raw_bet_updates'),
        'limitation': (
            f"Automated live {entry['book_provider'].title()} series moneyline via BO3.gg REST API "
            f"({entry['odds'][0]} / {entry['odds'][1]}); single-operator sportsbook price with no tick-level "
            'exchange timestamp. Observation time shown and standard 8-hour evidence window applies.'
        ),
    }
    order = orientation(fixture, entry['teams'], entry['start'])
    quote_book(book_candidate(receipt), order, now)
    return receipt, {
        'provider': ATTEMPT_PROVIDER,
        'status': 'resolved',
        'url': entry['url'],
        'reason': (
            f"Exact pair and UTC start verified on BO3.gg CS2 API; live {entry['book_provider'].title()} "
            f"series moneyline ({entry['odds'][0]} / {entry['odds'][1]}) validated."
        ),
    }


def discover_receipts(fixtures: list[dict], src, now) -> tuple[list[dict], list[dict]]:
    """Fetch ``api.bo3.gg`` once when needed and build validated receipts for open unpriced rows."""
    unpriced = [m for m in fixtures if m.get('state') == 'open'
                and m.get('probabilities') is None and not m.get('resolution_blocked')]
    if not unpriced:
        return [], []
    entries, errors = fetch_entries(src)
    if not entries and errors:
        err = errors[0]
        attempts = [{
            'fixture_id': str(m['id']),
            'provider': ATTEMPT_PROVIDER,
            'status': 'error',
            'url': err['url'],
            'reason': 'BO3.gg CS2 API read failed: ' + err['error'],
        } for m in unpriced]
        return [], attempts
    receipts: list[dict] = []
    attempts: list[dict] = []
    for m in unpriced:
        receipt, attempt = build_receipt_for_fixture(m, entries, now)
        attempts.append({'fixture_id': str(m['id']), **attempt})
        if receipt is not None:
            receipts.append(receipt)
    return receipts, attempts
