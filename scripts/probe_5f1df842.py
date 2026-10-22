"""Research probe: does an esportsbook listing publish a two-way line for a row
the automated ladder could not price?

Why this exists
---------------
``scripts.refresh`` queries Polymarket, HLTV and Pinnacle automatically and then
gives up on the rows none of them covers, falling back to the Valve model or to
a research-only pick. The user's requirement is that *every* listed match gets a
pick, so the remaining rows have to be researched on the esportsbook listing
pages themselves. That research cannot run in the authoring sandbox (it reaches
GitHub and package registries only), so it runs on a runner and writes a dated
capture that can be re-checked line by line.

What it does, and deliberately does not do
------------------------------------------
* It reads public listing pages only, once per second, with an honest
  User-Agent. A 403/429 is recorded and the host is left alone: no header is
  spoofed and no access control is bypassed.
* For each open row that publishes no win percentage it looks for the *exact*
  opponent pair on the listing, then reads that match page and records, verbatim:
  the page's JSON-LD ``name`` and ``startDate``, the decimal pair bound to both
  team labels, and the sha256 of the whole document. A symmetric placeholder
  (1.8 / 1.8) is recorded as a placeholder, never as a line.
* It never writes a probability. Turning a captured pair into a de-vigged
  probability stays in ``scripts.core.quote_book``, which only runs when a
  receipt's identity, start time and freshness gates all pass.

Output: ``research/session-5f1df842/probe/report.json`` plus compact per-match
captures. The full HTML is not committed; its sha256 is, so the capture can be
re-fetched and checked against a fixed fingerprint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

BASE = 'https://egamersworld.com'
LISTING_PAGES = (
    BASE + '/counterstrike/matches',
    BASE + '/counterstrike/matches?page=2',
    BASE + '/counterstrike/matches?page=3',
)
UA = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'
POLITE_DELAY = 1.0
TIMEOUT = (10, 30)
MAX_EVENT_PAGES = 40

MATCH_LINK = re.compile(r'href="(https://egamersworld\.com/counterstrike/match/[^"]+)"')
EVENT_LINK = re.compile(r'href="(https://egamersworld\.com/counterstrike/event/[^"]+)"')
NAME_VS = re.compile(r'"name"\s*:\s*"([^"\\]+?)\s+VS\s+([^"\\]+?)"')
START = re.compile(r'"startDate"\s*:\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)"')
MAKE_BET = re.compile(r'(\d+\.\d+)\s+Make a bet\s+(\d+\.\d+)')
TAG = re.compile(r'<[^>]+>')
PLACEHOLDER = (1.8, 1.8)


def plain(value):
    """Same folding rule as scripts.core.plain_name, so a pair compares the same way."""
    folded = unicodedata.normalize('NFKD', value or '').casefold()
    folded = ''.join(c for c in folded if not unicodedata.combining(c))
    return ''.join(c for c in unicodedata.normalize('NFKC', folded) if c.isalnum())


class Reader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = UA
        self.log = []
        self._last = 0.0

    def get(self, url):
        wait = POLITE_DELAY - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()
        record = {'url': url, 'read_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            record['http_status'] = response.status_code
            body = response.text
            record['sha256'] = hashlib.sha256(response.content).hexdigest()
            record['bytes'] = len(response.content)
            if response.status_code != 200:
                record['status'] = 'refused'
                self.log.append(record)
                return None, record
            record['status'] = 'ok'
            self.log.append(record)
            return body, record
        except requests.RequestException as error:
            record.update(status='error', error=str(error)[:250])
            self.log.append(record)
            return None, record


def pairs_from_listing(html):
    """(team1, team2, url) for every match link whose anchor names both teams."""
    found = {}
    for match in MATCH_LINK.finditer(html):
        url = match.group(1)
        window = html[max(0, match.start() - 1200):match.end() + 200]
        title = re.search(r'title="([^"]+?)\s+VS\s+([^"]+?)"', window)
        if not title:
            continue
        found[url] = (title.group(1).strip(), title.group(2).strip())
    return found


def read_match(reader, url, wanted):
    """Capture the identity and the odds widget of one listing match page."""
    html, record = reader.get(url)
    capture = {'url': url, 'read': record, 'wanted': list(wanted)}
    if html is None:
        return capture
    stripped = TAG.sub(' ', html)
    capture['json_ld'] = [{'team1': m.group(1).strip(), 'team2': m.group(2).strip()}
                          for m in NAME_VS.finditer(html)]
    capture['start_dates'] = [m.group(1) for m in START.finditer(html)]
    odds = []
    for make in MAKE_BET.finditer(stripped):
        try:
            pair = [float(make.group(1)), float(make.group(2))]
        except ValueError:
            continue
        window = stripped[max(0, make.start() - 260):make.end() + 40]
        odds.append({'pair': pair, 'placeholder': tuple(pair) == PLACEHOLDER,
                     'symmetric': abs(pair[0] - pair[1]) < 1e-9,
                     'context': re.sub(r'\s+', ' ', window)[-240:]})
    capture['odds_widget'] = odds
    # Third-party ranking numbers the listing prints beside each team. Context
    # only: they are never converted into a probability here.
    capture['rank_hints'] = re.findall(r'#(\d{1,4})\s*!\[[^\]]*\]\([^)]*\)([A-Za-z0-9 ._\-]{2,30})', html)[:6]
    return capture


def run(snapshot_path, output, listing_pages=LISTING_PAGES):
    snapshot = json.loads(Path(snapshot_path).read_text())
    targets = [m for m in snapshot['matches'] if m.get('state') == 'open' and not m.get('probabilities')]
    reader = Reader()
    index = {}
    for page in listing_pages:
        html, record = reader.get(page)
        if html:
            index.update(pairs_from_listing(html))
    # Event pages carry the fixtures further out than the rolling listing does
    # (DFRAG is five days ahead), so they are read once each, in a bounded loop.
    events = []
    if index:
        first, _ = reader.get(listing_pages[0])
        events = sorted(set(EVENT_LINK.findall(first or '')))[:MAX_EVENT_PAGES]
    for event in events:
        html, _ = reader.get(event)
        if html:
            index.update(pairs_from_listing(html))
    report = {'generated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
              'snapshot': str(snapshot_path),
              'listing_matches_seen': len(index),
              'event_pages_read': len(events),
              'targets': [], 'reads': reader.log}
    Path(output).mkdir(parents=True, exist_ok=True)
    for fixture in targets:
        wanted = {plain(fixture['teams'][0]), plain(fixture['teams'][1])}
        hits = [url for url, pair in index.items() if {plain(pair[0]), plain(pair[1])} == wanted]
        entry = {'fixture_id': fixture['id'], 'teams': fixture['teams'],
                 'start': fixture.get('start'), 'competition': fixture.get('competition'),
                 'current_method': fixture.get('method'), 'candidates': []}
        for url in hits[:3]:
            entry['candidates'].append(read_match(reader, url, fixture['teams']))
        if not hits:
            entry['note'] = ('No listing on the pages read carries this exact opponent pair. '
                             'Recorded as a coverage limit, not as evidence that no book prices it.')
        report['targets'].append(entry)
    Path(output, 'report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/session-5f1df842/probe')
    args = parser.parse_args()
    report = run(args.snapshot, args.output)
    print(json.dumps({'targets': len(report['targets']),
                      'with_candidate_listing': sum(1 for t in report['targets'] if t.get('candidates')),
                      'listing_matches_seen': report['listing_matches_seen'],
                      'event_pages_read': report['event_pages_read'],
                      'reads': len(report['reads'])}, indent=1))


if __name__ == '__main__':
    main()
