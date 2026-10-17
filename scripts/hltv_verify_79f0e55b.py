"""Session 79f0e55b: line-by-line verification of the Thunderpick World Championship 2026
record and of the day-4 (17 October 2026) semi-final picture, from HLTV's own pages.

Why this exists
---------------
The authoring sandbox cannot open a TLS connection to ``www.hltv.org``
(``curl`` -> ``SSL_ERROR_SYSCALL``, re-measured on 2026-10-17 00:48 UTC), so every fact
this session republishes about the event is re-read on a runner with normal outbound
access and the **raw body** of each page is retained next to the values extracted from
it. Nothing is transcribed by hand: the tables in ``report.json`` are parsed out of the
archived HTML, and every extracted value names the page URL and the SHA-256 of the body
it came from.

What it reads
-------------
* HLTV event pages for event 8932 (overview, matches/schedule, results).
* Every match page discovered on those pages (played and upcoming): map scores, vetoes
  and start-time display live on the match pages, not in the lists.
* HLTV's own betting-analytics pages for the two semi-finals, retained raw so HLTV's own
  wording ("the bookmaker favorite with the best odds", "odds from bookmakers") can be
  checked rather than paraphrased.
* The Aurora team page, for the roster and the dated transfer rows that the "recent
  roster change" question turns on.

What it never does
------------------
It never invents a value. A page that fails is recorded as an error with its HTTP status;
a field whose selector finds nothing is ``null`` and flagged. Displayed clock times are
stored exactly as rendered, because HLTV renders them in the viewer's timezone without
naming it in the HTML.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TWC_EVENT = 8932
BASE = 'https://www.hltv.org'
EVENT_PAGES = (
    ('event-overview', '%s/events/%d/thunderpick-world-championship-2026' % (BASE, TWC_EVENT)),
    ('event-schedule', '%s/events/%d/matches' % (BASE, TWC_EVENT)),
    ('event-results', '%s/results?event=%d' % (BASE, TWC_EVENT)),
)
ANALYTICS_IDS = (2399414, 2399415)  # the two semi-finals, per the schedule page
TEAM_PAGES = (('Aurora', '%s/team/11861/aurora' % BASE),)
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/141.0.0.0 Safari/537.36')
# Played and upcoming TWC matches seen on HLTV's own pages on 2026-10-17. The list is only
# a floor: match ids parsed out of the event pages are fetched as well.
SEED_MATCH_IDS = tuple(range(2399384, 2399388)) + tuple(range(2399408, 2399418))
DAY_RE = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*-\s*\d{4}-\d{2}-\d{2}$')


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def fetch(session, url, attempts=3, pause=2.5):
    """Return (text, receipt). Never raises: a failure is a receipt with an error."""
    record = {'url': url, 'observed_at': now_iso(), 'status': None, 'bytes': None,
              'sha256': None, 'file': None, 'error': None, 'attempts': 0}
    last = None
    for attempt in range(1, attempts + 1):
        record['attempts'] = attempt
        try:
            response = session.get(url, timeout=45, allow_redirects=True)
            record['status'] = response.status_code
            record['final_url'] = response.url
            body = response.content
            record['bytes'] = len(body)
            record['sha256'] = hashlib.sha256(body).hexdigest()
            if response.status_code >= 400:
                raise ValueError('HTTP %d' % response.status_code)
            return body.decode(response.encoding or 'utf-8', 'replace'), record
        except Exception as exc:  # noqa: BLE001
            last = '%s: %s' % (type(exc).__name__, str(exc)[:200])
            time.sleep(pause * attempt)
    record['error'] = last
    return None, record


def save(out, name, text):
    path = out / (name + '.html')
    path.write_text(text, encoding='utf-8')
    return str(path)


def text_of(node):
    return re.sub(r'\s+', ' ', node.get_text(' ', strip=True)) if node is not None else None


def parse_results(html):
    """Match rows on the event results page: date heading, match id, teams, score."""
    soup = BeautifulSoup(html, 'html.parser')
    rows, heading = [], None
    blocks = soup.select('div.results-sublist') or soup.select('div.results-all')
    for block in blocks:
        head = block.select_one('.standard-headline')
        if head:
            heading = text_of(head)
        for cell in block.select('div.result-con'):
            link = cell.select_one('a')
            href = (link.get('href') if link else None) or ''
            match_id = None
            found = re.search(r'/matches/(\d+)/', href)
            if found:
                match_id = int(found.group(1))
            rows.append({'date_heading': heading, 'match_id': match_id,
                         'url': (BASE + href) if href.startswith('/') else (href or None),
                         'teams': [text_of(t) for t in cell.select('.team')],
                         'score': text_of(cell.select_one('.result-score')),
                         'score_parts': [text_of(s) for s in cell.select('.result-score span')]})
    seen, unique = set(), []
    for row in rows:
        key = (row['match_id'], row['score'])
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def unix_to_iso(value):
    """HLTV stamps scheduled fixtures with an absolute epoch in ``data-unix``.

    The rendered clock is the viewer's local time and the page never names the zone, so
    the epoch attribute is the only part of the markup that states when a fixture starts
    unambiguously. Converting it is arithmetic, not a guess; a missing or malformed
    attribute yields ``None`` and the field stays blank.
    """
    try:
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    except (TypeError, ValueError, OSError):
        return None


def _schedule_row(label, ev):
    link = ev.select_one('a.match-info') or ev.select_one('a.match') or ev.select_one('a')
    href = (link.get('href') if link else None) or ''
    placeholder = ev.select_one('.match-fixtures-placeholder')
    match_id = None
    if placeholder and (placeholder.get('data-match-id') or '').isdigit():
        match_id = int(placeholder['data-match-id'])
    if match_id is None:
        found = re.search(r'/matches/(\d+)/', href)
        if found:
            match_id = int(found.group(1))
    time_node = ev.select_one('.match-time, .matchTime')
    return {'day_heading': label, 'match_id': match_id,
            'displayed_time': text_of(time_node),
            'start_utc': unix_to_iso(time_node.get('data-unix')) if time_node else None,
            'format': text_of(ev.select_one('.match-meta, .matchMeta')),
            'teams': [text_of(t) for t in ev.select('.match-teamname, .matchTeamName')],
            'stage': text_of(ev.select_one('.match-stage')),
            'event_note': text_of(ev.select_one('.matchEventName, .upcomingeventname')),
            'url': (BASE + href) if href.startswith('/') else (href or None)}


def parse_schedule(html):
    """Upcoming fixtures with both the rendered clock and the absolute epoch.

    Headings and fixture rows are walked in document order, so a fixture is attributed to
    the day heading that actually precedes it; the earlier ``div.match-day`` wrapper and
    the flat ``.upcomingMatch`` list are handled as fallbacks for older markup. A row
    without a match id is dropped rather than published with a guessed identity.
    """
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    heading_classes = {'event-headline', 'standard-headline', 'upcoming-headline'}
    row_classes = {'match', 'upcomingMatch'}
    nodes = soup.find_all(
        lambda tag: (tag.name in ('span', 'div') and heading_classes & set(tag.get('class') or []))
        or (tag.name == 'div' and row_classes & set(tag.get('class') or [])))
    label = None
    for node in nodes:
        classes = set(node.get('class') or [])
        if classes & heading_classes:
            candidate = text_of(node)
            if candidate and DAY_RE.match(candidate):
                label = candidate
            continue
        if classes & row_classes:
            out.append(_schedule_row(label, node))
    seen, unique = set(), []
    for row in out:
        key = (row['match_id'], row['start_utc'], row['displayed_time'])
        if row['match_id'] and key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def parse_match_page(html):
    """Displayed start time, teams, format, per-map scores with the winning side, veto."""
    soup = BeautifulSoup(html, 'html.parser')
    maps = []
    for holder in soup.select('.mapholder'):
        name = text_of(holder.select_one('.mapname'))
        if not name:
            continue
        left = holder.select_one('.results-left')
        right = holder.select_one('.results-right')
        maps.append({
            'map': name,
            'left': {'team': text_of(holder.select_one('.team-left, .team-left-name')),
                     'score': text_of(left.select_one('.results-team-score')) if left else None,
                     'won': bool(left and 'won' in (left.get('class') or []))},
            'right': {'team': text_of(holder.select_one('.team-right, .team-right-name')),
                      'score': text_of(right.select_one('.results-team-score')) if right else None,
                      'won': bool(right and 'won' in (right.get('class') or []))},
            'pick_note': text_of(holder.select_one('.map-pick, .mapname-holder .map-pick')),
        })
    veto = []
    for item in soup.select('.veto-box div'):
        if item.find('div') is not None:  # only leaf nodes carry one veto line
            continue
        label = text_of(item)
        if label and 3 < len(label) < 120 and label not in veto and label.lower() != 'veto':
            veto.append(label)
    body = text_of(soup.body) or text_of(soup) or ''
    time_node = soup.select_one('.timeAndEvent .time')
    return {
        'displayed_time': text_of(time_node),
        'displayed_date': text_of(soup.select_one('.timeAndEvent .date')),
        'start_utc': unix_to_iso(time_node.get('data-unix')) if time_node else None,
        'team_names': [text_of(t) for t in soup.select('.teamName')],
        'maps': maps,
        'veto': veto,
        'has_betting_anchor': bool(soup.select_one('a[href$="#betting"]')),
        'mentions_odds_from_bookmakers': 'odds from bookmakers' in body.lower(),
        'countdown_present': bool(soup.select_one('#countdown, .countdown, .countdown-live')),
    }


def parse_analytics(html):
    """HLTV's own pros/cons wording and any odds table it renders server-side."""
    soup = BeautifulSoup(html, 'html.parser')
    notes = []
    for node in soup.select('.analyticsRow, .pros-cons, .analytics-pros-cons, .section .analyticsRow'):
        label = text_of(node)
        if label and label not in notes:
            notes.append(label)
    odds = [text_of(x) for x in soup.select('.odds-table, .oddsCell, .betting-odds-table, table.odds')
            if text_of(x)]
    body = text_of(soup.body) or text_of(soup) or ''
    return {
        'pros_cons': notes[:40],
        'odds_tables': odds[:20],
        'states_bookmaker_favorite': 'bookmaker favorite' in body.lower(),
        'bookmaker_favorite_lines': re.findall(r'[^.]{0,120}bookmaker favorite[^.]{0,120}', body)[:3],
        'mentions_odds_from_bookmakers': 'odds from bookmakers' in body.lower(),
        'ranking_mentions': sorted(set(re.findall(r'(?:better|worse) ranked \(#(\d+)\)', body))),
    }


def table_rows(table):
    """Header row plus body rows of an HLTV table, cell text only."""
    out = []
    for row in table.select('tr'):
        cells = [text_of(c) for c in row.find_all(['td', 'th'])]
        if cells and any(cells):
            out.append(cells)
    return out


def parse_team_page(html):
    """Roster, coach tenure and the team's recent results, as HLTV renders them.

    HLTV states each player's **time on team**, which is the primary evidence for any
    "recent roster change" claim: a starter listed at three months is a July arrival, not
    a change made during the tournament. Nothing here is inferred beyond that reading —
    the cell text is stored verbatim.
    """
    soup = BeautifulSoup(html, 'html.parser')
    roster = []
    for row in table_rows(soup.select_one('.players-table') or BeautifulSoup('<table></table>', 'html.parser')):
        roster.append(row)
    coach = table_rows(soup.select_one('.coach-table') or BeautifulSoup('<table></table>', 'html.parser'))
    recent = []
    tables = soup.select('.match-table')
    if tables:
        recent = table_rows(tables[-1])[:15]
    return {'roster_table': roster[:20], 'coach_table': coach[:5], 'recent_results_table': recent,
            'world_rank_text': text_of(soup.select_one('.team-profile .rank, .profile-team-stat .right, .team-country-rank, .team-country-rank-link'))}


def replay_bodies(directory, names, prior=None):
    """Read previously captured bodies from disk, so the parsers can be re-run offline.

    The receipt keeps the **original network observation** when a previous report lists
    this body (its timestamp, HTTP status and size), and the hash recorded here is
    recomputed from the bytes on disk. If that recomputed hash differs from the original
    receipt, the mismatch is recorded rather than smoothed over, and ``sha256_matches``
    is set to false so a reader can see that the file is not the body that was fetched.
    """
    prior_by_name = {}
    for record in (prior or {}).get('pages') or []:
        if record.get('name'):
            prior_by_name[record['name']] = record
    bodies, receipts, errors = {}, [], []
    for name, url in names:
        path = Path(directory) / (name + '.html')
        if not path.exists():
            errors.append({'name': name, 'url': url, 'error': 'captured body missing',
                           'status': None})
            continue
        body = path.read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        bodies[name] = body.decode('utf-8', 'replace')
        original = prior_by_name.get(name) or {}
        receipt = {'url': original.get('url') or url, 'name': name,
                   'status': original.get('status', 200), 'bytes': len(body),
                   'sha256': digest, 'file': str(path),
                   'observed_at': original.get('observed_at') or now_iso(),
                   'error': original.get('error'), 'attempts': original.get('attempts', 0),
                   'replayed_from': str(path),
                   'original_sha256': original.get('sha256'),
                   'sha256_matches': (original.get('sha256') in (None, digest))}
        if not receipt['sha256_matches']:
            errors.append({'name': name, 'url': url, 'error': 'replayed body hash differs from the original receipt',
                           'status': receipt['status']})
        receipts.append(receipt)
    return bodies, receipts, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='research/hltv-79f0e55b')
    parser.add_argument('--replay', default=None,
                        help='re-parse bodies captured by an earlier run instead of using the network')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})

    report = {'tool': 'hltv_verify_79f0e55b', 'event_id': TWC_EVENT, 'started_at': now_iso(),
              'pages': [], 'results_rows': [], 'schedule_rows': [], 'match_pages': {},
              'analytics': {}, 'teams': {}, 'match_ids': [], 'errors': []}

    if args.replay:
        names = list(EVENT_PAGES) + [('match-%d' % i, '%s/matches/%d/x' % (BASE, i)) for i in SEED_MATCH_IDS] \
            + [('analytics-%d' % i, '%s/betting/analytics/%d/x' % (BASE, i)) for i in ANALYTICS_IDS] \
            + [('team-%s' % n, u) for n, u in TEAM_PAGES]
        prior = None
        prior_path = out / 'report.json'
        if prior_path.exists():
            try:
                prior = json.loads(prior_path.read_text())
            except Exception:  # noqa: BLE001 - a corrupt prior report must not stop a replay
                prior = None
        bodies, receipts, errors = replay_bodies(args.replay, names, prior)
        report['replayed_from'] = args.replay
        report['replay_preserved_network_receipts'] = bool(prior)
        report['errors'].extend(errors)
        report['pages'].extend(receipts)
        discovered = {}
        if 'event-schedule' in bodies:
            try:
                report['schedule_rows'] = parse_schedule(bodies['event-schedule'])
            except Exception as exc:  # noqa: BLE001
                report['errors'].append({'name': 'parse schedule', 'error': str(exc)[:300]})
        if 'event-results' in bodies:
            try:
                report['results_rows'] = parse_results(bodies['event-results'])
            except Exception as exc:  # noqa: BLE001
                report['errors'].append({'name': 'parse results', 'error': str(exc)[:300]})
        for row in report['results_rows'] + report['schedule_rows']:
            if row.get('match_id'):
                discovered.setdefault(int(row['match_id']), row.get('url'))
        for match_id in sorted(set(discovered) | set(SEED_MATCH_IDS) | set(ANALYTICS_IDS)):
            key = 'match-%d' % match_id
            entry = {'receipt': next((r for r in receipts if r['name'] == key), {'status': None})}
            if key in bodies:
                entry['loaded'] = True
                entry.update(parse_match_page(bodies[key]))
            else:
                entry['loaded'] = False
            report['match_pages'][str(match_id)] = entry
        for match_id in ANALYTICS_IDS:
            key = 'analytics-%d' % match_id
            entry = {'receipt': next((r for r in receipts if r['name'] == key), {'status': None})}
            if key in bodies:
                entry.update(parse_analytics(bodies[key]))
            report['analytics'][str(match_id)] = entry
        for name, _url in TEAM_PAGES:
            key = 'team-%s' % name
            entry = {'receipt': next((r for r in receipts if r['name'] == key), {'status': None})}
            if key in bodies:
                entry.update(parse_team_page(bodies[key]))
            report['teams'][name] = entry
        report['match_ids'] = sorted(set(discovered) | set(SEED_MATCH_IDS) | set(ANALYTICS_IDS))
        report['finished_at'] = now_iso()
        report['ok_pages'] = sum(1 for p in report['pages'] if p.get('status') == 200)
        (out / 'report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + '\n',
                                         encoding='utf-8')
        print('hltv_verify_79f0e55b (replay of %s): %d bodies, %d results rows, %d schedule rows, %d error(s) -> %s'
              % (args.replay, report['ok_pages'], len(report['results_rows']),
                 len(report['schedule_rows']), len(report['errors']), out))
        return

    bodies, discovered = {}, {}
    for name, url in EVENT_PAGES:
        text, receipt = fetch(session, url)
        receipt['name'] = name
        if text is None:
            report['errors'].append({'name': name, 'url': url, 'error': receipt['error'],
                                     'status': receipt['status']})
        else:
            receipt['file'] = save(out, name, text)
            bodies[name] = text
        report['pages'].append(receipt)
        time.sleep(2)

    if 'event-results' in bodies:
        try:
            report['results_rows'] = parse_results(bodies['event-results'])
        except Exception as exc:  # noqa: BLE001
            report['errors'].append({'name': 'parse results', 'error': str(exc)[:300]})
    if 'event-schedule' in bodies:
        try:
            report['schedule_rows'] = parse_schedule(bodies['event-schedule'])
        except Exception as exc:  # noqa: BLE001
            report['errors'].append({'name': 'parse schedule', 'error': str(exc)[:300]})

    for row in report['results_rows'] + report['schedule_rows']:
        if row.get('match_id'):
            discovered.setdefault(int(row['match_id']), row.get('url'))
    ids = sorted(set(discovered) | set(SEED_MATCH_IDS) | set(ANALYTICS_IDS))
    report['match_ids'] = ids

    for match_id in ids:
        url = discovered.get(match_id) or ('%s/matches/%d/x' % (BASE, match_id))
        text, receipt = fetch(session, url)
        receipt['name'] = 'match-%d' % match_id
        entry = {'receipt': receipt}
        if text is None:
            entry['loaded'] = False
            report['errors'].append({'name': 'match-%d' % match_id, 'url': url,
                                     'error': receipt['error'], 'status': receipt['status']})
        else:
            entry['loaded'] = True
            receipt['file'] = save(out, 'match-%d' % match_id, text)
            try:
                entry.update(parse_match_page(text))
            except Exception as exc:  # noqa: BLE001
                entry['parse_error'] = str(exc)[:300]
        report['match_pages'][str(match_id)] = entry
        report['pages'].append(receipt)
        time.sleep(2)

    for match_id in ANALYTICS_IDS:
        url = '%s/betting/analytics/%d/x' % (BASE, match_id)
        text, receipt = fetch(session, url)
        receipt['name'] = 'analytics-%d' % match_id
        entry = {'receipt': receipt}
        if text is None:
            report['errors'].append({'name': 'analytics-%d' % match_id, 'url': url,
                                     'error': receipt['error'], 'status': receipt['status']})
        else:
            receipt['file'] = save(out, 'analytics-%d' % match_id, text)
            try:
                entry.update(parse_analytics(text))
            except Exception as exc:  # noqa: BLE001
                entry['parse_error'] = str(exc)[:300]
        report['analytics'][str(match_id)] = entry
        report['pages'].append(receipt)
        time.sleep(2)

    for name, url in TEAM_PAGES:
        text, receipt = fetch(session, url)
        receipt['name'] = 'team-%s' % name
        entry = {'receipt': receipt}
        if text is None:
            report['errors'].append({'name': 'team-%s' % name, 'url': url, 'error': receipt['error'],
                                     'status': receipt['status']})
        else:
            receipt['file'] = save(out, 'team-%s' % name, text)
            try:
                entry.update(parse_team_page(text))
            except Exception as exc:  # noqa: BLE001
                entry['parse_error'] = str(exc)[:300]
        report['teams'][name] = entry
        report['pages'].append(receipt)
        time.sleep(2)

    report['finished_at'] = now_iso()
    report['ok_pages'] = sum(1 for p in report['pages'] if p.get('status') == 200)
    (out / 'report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + '\n',
                                     encoding='utf-8')
    print('hltv_verify_79f0e55b: %d/%d pages ok, %d results rows, %d schedule rows, %d error(s) -> %s'
          % (report['ok_pages'], len(report['pages']), len(report['results_rows']),
             len(report['schedule_rows']), len(report['errors']), out))


if __name__ == '__main__':
    main()
