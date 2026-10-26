"""Read-only gap probe for session 5bf1c3eb: why a row has no pick, and what the
outside sources actually said in the same minute the snapshot was taken.

Two questions are answered separately, because the brief treats them as
different failures and they are not the same failure:

1. **Open rows with no pick / no percentage.** For each one, the esports sources
   the brief names are re-read in order -- HLTV first, then the book/exchange
   endpoints this project already collects (Polymarket, Pinnacle, BO3.gg's
   Thunderpick feed, EGamersWorld's bookmaker-average listing) -- and the raw
   response for that exact fixture is retained. A source that renders no numeric
   two-way price is recorded as a *collection limitation*, never converted into
   a number and never defaulted to 50/50.

2. **Rows that cannot take a pick at all** because Hotspawn's own lock time has
   passed. These are not unresolved research; the pick window is closed. The
   probe derives that from the feed's own ``lock_time`` / ``start_time`` /
   ``end_time`` / ``status`` fields, which are already in the snapshot, so the
   statement is reproducible offline from committed evidence with no network
   read and nothing inferred.

Nothing here writes to the site, mutates a probability or publishes a pick. It
produces dated research receipts for line-by-line review.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from scripts.core import PIN, GAMMA, dt, iso, norm
from scripts.probe_caca91b8 import (
    UA,
    check_live_pages,
    fetch_bo3_upcoming,
    match_bo3_candidates,
    probe_hltv_search,
    search_vrs_candidates,
)

EGW_LISTING = 'https://egamersworld.com/counterstrike/matches'
EGW_MATCH_LINK_RE = re.compile(r'href="(/counterstrike/(?:match|tip)/[A-Za-z0-9_\-]+/[^"]+)"')
# EGamersWorld renders a two-sided bookmaker average in plain sentences; these are
# the verbatim patterns scripts/egw_probe.py already publishes. A changed page is a
# parse miss that stays a parse miss.
EGW_FAVOURITE_RE = re.compile(
    r'According to leading bookmakers predictions, the team (.+?) are the favorite'
    r' with average odds ([0-9.]+) at the moment', re.I)
EGW_OUTSIDER_RE = re.compile(
    r'bookmakers consider (.+?) to be the outsider of the match with odds on a'
    r' victory in the sum of about ([0-9.]+)', re.I)
EGW_OFFERS_RE = re.compile(
    r'Bookmakers make (.+?) the favourites at ([0-9.]+), with (.+?) the underdogs at ([0-9.]+)',
    re.I)

# Bounded on purpose: this runs inside a 30-minute non-publishing workflow that
# also runs the real refresh, so the probe must not become the long pole.
EGW_PAGE_BUDGET = 10
HLTV_SLEEP_SECONDS = 2.5


def _get(session, url, as_json=True, timeout=(10, 25)):
    """One read, recorded. A refusal is a finding, never a retry storm."""
    record = {'url': url, 'read_at': iso(datetime.now(timezone.utc))}
    try:
        r = session.get(url, timeout=timeout)
        record['http_status'] = r.status_code
        record['bytes'] = len(r.content)
        if r.status_code != 200:
            record['status'] = 'refused'
            return record, None, ''
        if as_json:
            try:
                return dict(record, status='ok'), r.json(), r.text
            except ValueError as exc:
                record.update(status='non_json_body', error=str(exc)[:180])
                return record, None, r.text[:4000]
        record['status'] = 'ok'
        return record, None, r.text
    except Exception as exc:  # network/DNS/TLS: recorded, not guessed around
        record.update(status='error', error='%s: %s' % (type(exc).__name__, str(exc)[:200]))
        return record, None, ''


def egw_readings(text):
    """Every bookmaker-average reading EGamersWorld renders in one page body."""
    found = []
    for favourite, fav_odds in EGW_FAVOURITE_RE.findall(text or ''):
        outsider = EGW_OUTSIDER_RE.search(text or '')
        if not outsider:
            continue
        found.append({'form': 'bookmakers_predictions',
                      'favourite_team': favourite.strip(), 'favourite_odds': float(fav_odds),
                      'outsider_team': outsider.group(1).strip(),
                      'outsider_odds': float(outsider.group(2))})
    for fav, fav_odds, dog, dog_odds in EGW_OFFERS_RE.findall(text or ''):
        found.append({'form': 'bookmakers_offers', 'favourite_team': fav.strip(),
                      'favourite_odds': float(fav_odds), 'outsider_team': dog.strip(),
                      'outsider_odds': float(dog_odds)})
    return found


def probe_egamersworld(session, targets):
    """Read the EGamersWorld CS2 listing, then the match/tip pages whose slug
    names one of the unpriced fixtures. Returns per-fixture readings plus the
    page receipts. Slugs are matched on normalised team tokens; a page that
    renders no two-way price is kept as a parse miss."""
    out = {'listing': None, 'pages': [], 'per_fixture': {}}
    record, _, body = _get(session, EGW_LISTING, as_json=False)
    out['listing'] = record
    if not body:
        return out
    hrefs, seen = [], set()
    for href in EGW_MATCH_LINK_RE.findall(body):
        if href in seen:
            continue
        seen.add(href)
        hrefs.append(href)
    wanted = []
    for fixture_id, teams in targets:
        toks = {norm(t) for t in teams} | {t for team in teams for t in re.sub(r'[^a-z0-9]+', ' ', team.lower()).split() if len(t) >= 4}
        for href in hrefs:
            slug = norm(href.rsplit('/', 1)[-1] if '/' in href else href)
            if any(tok and tok in slug for tok in toks):
                wanted.append((fixture_id, href))
    for fixture_id, href in wanted[:EGW_PAGE_BUDGET]:
        url = 'https://egamersworld.com' + href
        page_record, _, page_body = _get(session, url, as_json=False)
        readings = egw_readings(page_body)
        entry = dict(page_record, fixture_id=fixture_id, readings=readings,
                     parse_miss=not readings)
        out['pages'].append(entry)
        out['per_fixture'].setdefault(fixture_id, []).append(
            {'url': url, 'readings': readings, 'http_status': page_record.get('http_status')})
        time.sleep(1.0)
    return out


def probe_polymarket(session, targets):
    """Ask Polymarket's own public sports registry and event search for each
    unpriced pair. The receipt records whether a two-sided market exists at all,
    which is the difference between 'not covered' and 'covered but gated'."""
    out = {'registry': None, 'searches': []}
    record, payload, _ = _get(session, GAMMA + '/sports')
    out['registry'] = dict(record, leagues=len(payload) if isinstance(payload, list) else None)
    for fixture_id, teams in targets:
        for team in teams:
            url = GAMMA + '/events?limit=20&active=true&closed=false&search=' + quote_plus(team)
            rec, payload, _ = _get(session, url)
            hits = []
            if isinstance(payload, list):
                for event in payload:
                    if not isinstance(event, dict):
                        continue
                    title = str(event.get('title') or '')
                    if all(norm(t) and norm(t) in norm(title) for t in teams):
                        hits.append({'event_id': event.get('id'), 'title': title,
                                     'slug': event.get('slug'),
                                     'url': 'https://polymarket.com/event/' + str(event.get('slug') or event.get('id'))})
            out['searches'].append(dict(rec, fixture_id=fixture_id, query_team=team,
                                        both_teams_in_title=hits))
            time.sleep(0.4)
    return out


def probe_pinnacle(session, targets):
    """Read Pinnacle's guest esports moneyline endpoint once and report, per
    unpriced fixture, whether a two-way price for that exact pair was offered."""
    out = {'matchups': None, 'moneylines': None, 'per_fixture': {}}
    mrec, matchups, _ = _get(session, PIN + '/sports/12/matchups?withSpecials=false')
    lrec, lines, _ = _get(session, PIN + '/sports/12/markets/straight')
    out['matchups'] = dict(mrec, count=len(matchups) if isinstance(matchups, list) else None)
    out['moneylines'] = dict(lrec, count=len(lines) if isinstance(lines, list) else None)
    names = []
    for row in matchups if isinstance(matchups, list) else []:
        if not isinstance(row, dict):
            continue
        for part in row.get('participants') or []:
            if isinstance(part, dict) and part.get('name'):
                names.append({'matchup_id': row.get('id'), 'name': part['name'],
                              'starts': row.get('starts')})
    for fixture_id, teams in targets:
        hits = [n for n in names
                if all(any(norm(t) in norm(n['name']) or norm(n['name']) in norm(t)
                           for t in teams) for n in [n])]
        out['per_fixture'][fixture_id] = {
            'pinnacle_names_matching_both_teams': hits[:10],
            'note': ('No Pinnacle esports matchup row names both clubs in the same '
                     'minute as this snapshot.' if not hits else
                     'Pinnacle names this pair; see the retained moneyline receipt.'),
        }
    return out


def closed_row_ledger(snapshot):
    """Every feed row Hotspawn still returns that cannot take a pick because its
    own lock/start/end has passed. Derived only from the committed feed fields,
    so it is reproducible offline and nothing is inferred."""
    now = datetime.now(timezone.utc)
    rows, evidence = [], {str(x.get('id')): x for x in snapshot.get('fixture_evidence') or []}
    for m in snapshot.get('matches') or []:
        if m.get('state') == 'open':
            continue
        raw = evidence.get(str(m.get('id'))) or {}
        def ms(field):
            value = raw.get(field)
            try:
                return iso(datetime.fromtimestamp(int(value) / 1000.0, timezone.utc)) if value else None
            except (TypeError, ValueError, OSError, OverflowError):
                return None
        lock, start, end = ms('lock_time'), ms('start_time'), ms('end_time')
        reason = []
        if m.get('lock') and dt(m['lock']) <= now:
            reason.append('Hotspawn lock_time has passed (%s), so the pick window is closed.' % m['lock'])
        if m.get('start') and dt(m['start']) <= now:
            reason.append('Hotspawn scheduled_start_time has passed (%s).' % m['start'])
        if end:
            reason.append('Hotspawn also reports an end_time (%s) while status is still "%s".'
                          % (end, raw.get('status') or m.get('source_status')))
        rows.append({
            'id': m.get('id'),
            'teams': m.get('teams'),
            'competition': m.get('competition'),
            'tier': m.get('tier'),
            'scheduled_start_utc': m.get('start'),
            'lock_utc': m.get('lock'),
            'feed_status': raw.get('status') or m.get('source_status'),
            'feed_start_time_utc': start,
            'feed_end_time_utc': end,
            'feed_lock_time_utc': lock,
            'feed_url': m.get('feed_url'),
            'source_url': m.get('source_url'),
            'cannot_take_a_pick_because': reason or ['Lock/start has passed by the snapshot clock.'],
            'upstream_irregularity': bool(end and (raw.get('status') == 'scheduled')),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output-dir', default='research/session-5bf1c3eb/gaps')
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot = json.loads(Path(args.snapshot).read_text(encoding='utf-8'))

    session = requests.Session()
    session.headers['User-Agent'] = UA

    matches = snapshot.get('matches') or []
    opens = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in opens if m.get('probabilities') is not None]
    research_only = [m for m in opens if m.get('probabilities') is None and m.get('pick')]
    unresolved = [m for m in opens if m.get('probabilities') is None and not m.get('pick')]
    gaps = [m for m in opens if m.get('probabilities') is None]

    methods: dict[str, int] = {}
    for m in opens:
        key = str(m.get('method') or 'none')
        methods[key] = methods.get(key, 0) + 1

    # The brief asks for outside-source evidence specifically for the rows that
    # cannot be resolved the way the featured (market-priced) picks are, so the
    # book/exchange probes also cover every open row whose published line is NOT
    # a market line: a dated "no two-way price found" receipt per row is the
    # evidence that the model label on it is honest.
    nonmarket = [m for m in opens if m.get('probabilities') is not None
                 and str(m.get('method')) not in ('exchange', 'bookmaker_fallback', 'exchange_wide')]
    targets = [(str(m.get('id')), list(m.get('teams') or [])) for m in gaps + nonmarket]
    bo3_rows = fetch_bo3_upcoming(session) if targets else []

    per_row = []
    for m in gaps:
        teams = list(m.get('teams') or [])
        per_row.append({
            'id': m.get('id'),
            'teams': teams,
            'competition': m.get('competition'),
            'tier': m.get('tier'),
            'start': m.get('start'),
            'lock': m.get('lock'),
            'best_of': m.get('best_of'),
            'pick': m.get('pick'),
            'method': m.get('method'),
            'reason': m.get('reason'),
            'flags': m.get('flags') or [],
            'attempts': m.get('attempts') or [],
            'source_url': m.get('source_url'),
            'bo3_candidates': match_bo3_candidates(m, bo3_rows),
            'vrs_candidates': search_vrs_candidates(teams),
            'hltv_search': {t: probe_hltv_search(session, t) for t in teams},
        })

    report = {
        'session': '5bf1c3eb',
        'probed_at': iso(datetime.now(timezone.utc)),
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'coverage': snapshot.get('coverage'),
        'policy': ('Read-only. No probability is derived, converted or defaulted here; a '
                   'source with no numeric two-way price is retained as a collection '
                   'limitation for manual review.'),
        'counts': {
            'total_feed_rows': len(matches),
            'open_rows': len(opens),
            'not_open_rows': len(matches) - len(opens),
            'open_with_pick': sum(1 for m in opens if m.get('pick')),
            'open_with_probabilities': len(priced),
            'open_research_only_no_pct': len(research_only),
            'open_unresolved_no_pick': len(unresolved),
        },
        'open_pick_methods': methods,
        'issues': snapshot.get('issues') or [],
        'live_pages_at_probe_time': check_live_pages(session),
        'open_rows_without_a_percentage': per_row,
        'nonmarket_rows_probed': [fid for fid, _ in targets if fid not in
                                  {str(m.get('id')) for m in gaps}],
        'source_probes': {
            'bo3_gg_upcoming_rows': len(bo3_rows),
            'egamersworld': probe_egamersworld(session, targets) if targets else {'skipped': 'every open row already carries a probability'},
            'polymarket': probe_polymarket(session, targets) if targets else {'skipped': 'every open row already carries a probability'},
            'pinnacle': probe_pinnacle(session, targets) if targets else {'skipped': 'every open row already carries a probability'},
        },
        'closed_rows_that_cannot_take_a_pick': closed_row_ledger(snapshot),
    }
    (out_dir / 'gap-report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    closed = report['closed_rows_that_cannot_take_a_pick']
    print(json.dumps({
        'counts': report['counts'],
        'open_pick_methods': methods,
        'closed_rows': len(closed),
        'closed_rows_with_upstream_status_conflict': sum(1 for r in closed if r['upstream_irregularity']),
        'gaps_probed': len(per_row),
        'live_pages_within_8h': report['live_pages_at_probe_time'].get('within_8h_window'),
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
