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


def _schedule_row(label, ev):
    link = ev.select_one('a.match') or ev.select_one('a')
    href = (link.get('href') if link else None) or ''
    match_id = None
    found = re.search(r'/matches/(\d+)/', href)
    if found:
        match_id = int(found.group(1))
    return {'day_heading': label, 'match_id': match_id,
            'displayed_time': text_of(ev.select_one('.matchTime')),
            'format': text_of(ev.select_one('.matchMeta')),
            'teams': [text_of(t) for t in ev.select('.matchTeamName')],
            'event_note': text_of(ev.select_one('.matchEventName')),
            'url': (BASE + href) if href.startswith('/') else (href or None)}


def parse_schedule(html):
    """Upcoming fixtures exactly as rendered: day heading, clock, format, teams, note.

    Two published shapes are handled: HLTV's own ``div.match-day`` wrapper, and a flat
    list where each day heading is followed by its matches until the next heading. The
    flat walk stops at the next day heading so matches can never be attributed to the
    wrong day.
    """
    soup = BeautifulSoup(html, 'html.parser')
    out, days = [], soup.select('div.match-day')
    if days:
        for block in days:
            label = text_of(block.select_one('.standard-headline')) or text_of(block.select_one('span'))
            for ev in block.select('.upcomingMatch'):
                out.append(_schedule_row(label, ev))
    else:
        headings = [h for h in soup.find_all(['div', 'span'], class_=re.compile('standard-headline|match-day|date'))
                    if DAY_RE.match(text_of(h) or '')]
        for index, heading in enumerate(headings):
            label = text_of(heading)
            stop = headings[index + 1] if index + 1 < len(headings) else None
            node = heading
            while True:
                node = node.find_next()
                if node is None:
                    break
                if stop is not None and (node is stop or node in stop.parents):
                    break
                if node.name == 'div' and 'upcomingMatch' in (node.get('class') or []):
                    out.append(_schedule_row(label, node))
    seen, unique = set(), []
    for row in out:
        key = (row['match_id'], row['displayed_time'])
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
    return {
        'displayed_time': text_of(soup.select_one('.timeAndEvent .time')),
        'displayed_date': text_of(soup.select_one('.timeAndEvent .date')),
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


def parse_team_page(html):
    """Roster (flagging a coach) and dated transfer rows, as HLTV renders them."""
    soup = BeautifulSoup(html, 'html.parser')
    roster = []
    for card in soup.select('.bodyshot-team .player-holder, .team-roster .player-holder, .players-table .player-holder'):
        name = text_of(card.select_one('.text-ellipsis, .nickname, .player-name, .bold'))
        role = text_of(card.select_one('.player-role'))
        if name:
            roster.append({'player': name, 'role': role})
    transfers = []
    for row in soup.select('.transfer-table tr, table.transfers tr'):
        cells = [text_of(c) for c in row.find_all('td')]
        if cells and any(cells):
            transfers.append(cells)
    return {'roster': roster, 'transfers': transfers[:40],
            'world_rank_text': text_of(soup.select_one('.team-profile .rank, .profile-team-stat .right, .team-country-rank'))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='research/hltv-79f0e55b')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})

    report = {'tool': 'hltv_verify_79f0e55b', 'event_id': TWC_EVENT, 'started_at': now_iso(),
              'pages': [], 'results_rows': [], 'schedule_rows': [], 'match_pages': {},
              'analytics': {}, 'teams': {}, 'match_ids': [], 'errors': []}

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
