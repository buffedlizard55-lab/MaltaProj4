"""Capture EGamersWorld Counter-Strike pages for a book-listing provider.

Why this exists
---------------
Five open rows on the Hotspawn board carried a *research-only* pick with no
percentage on 2026-10-17: neither Polymarket nor Pinnacle lists them, and the
originated model line cannot be used for them either. EGamersWorld publishes a
two-sided **bookmaker average** line for the same fixtures in plain text, for
example on a match page:

    "According to leading bookmakers predictions, the team <A> are the favorite
     with average odds 1.39 at the moment. Respectively, bookmakers consider <B>
     to be the outsider of the match with odds on a victory in the sum of about
     2.65."

and on a prediction page:

    "Bookmakers make HEROIC the favourites at 1.67, with NiP the underdogs at 2.16."

This probe is the evidence step: it fetches the pages with the project's own
read-only HTTP client, keeps the status, byte count, SHA-256, observation time
and the raw body, and writes the result to disk so the parser that will consume
these pages can be written against the real markup instead of against a guess.

It never converts a price into a probability and it never retries a refused
host. A blocked or missing page is recorded as a finding, not as a number.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.refresh import Sources

BASE = 'https://egamersworld.com'
LISTING = BASE + '/counterstrike/matches'
HOME = BASE + '/counterstrike/'

# The two bookmaker-average sentences the site renders, kept verbatim as patterns
# so a changed page is a parse miss (recorded, never guessed around).
FAVOURITE_RE = re.compile(
    r'According to leading bookmakers predictions, the team (.+?) are the favorite'
    r' with average odds ([0-9.]+) at the moment', re.I)
OUTSIDER_RE = re.compile(
    r'bookmakers consider (.+?) to be the outsider of the match with odds on a'
    r' victory in the sum of about ([0-9.]+)', re.I)
OFFERS_RE = re.compile(
    r'Bookmakers make (.+?) the favourites at ([0-9.]+), with (.+?) the underdogs at ([0-9.]+)',
    re.I)
MATCH_LINK_RE = re.compile(r'href="(/counterstrike/(?:match|tip)/[A-Za-z0-9_\-]+/[^"]+)"')


def sniff(text):
    """Return every bookmaker-average reading found in one page body."""
    found = []
    for favourite, fav_odds in FAVOURITE_RE.findall(text):
        outsider = OUTSIDER_RE.search(text)
        if not outsider:
            continue
        found.append({
            'form': 'bookmakers_predictions',
            'favourite_team': favourite.strip(),
            'favourite_odds': float(fav_odds),
            'outsider_team': outsider.group(1).strip(),
            'outsider_odds': float(outsider.group(2)),
        })
    for fav, fav_odds, dog, dog_odds in OFFERS_RE.findall(text):
        found.append({
            'form': 'bookmakers_offers',
            'favourite_team': fav.strip(),
            'favourite_odds': float(fav_odds),
            'outsider_team': dog.strip(),
            'outsider_odds': float(dog_odds),
        })
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='research/harvest-03befae8/egw')
    parser.add_argument('--pages', type=int, default=6,
                        help='How many match/tip page pairs to capture from the listing.')
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    src = Sources(now)
    report = {'probed_at': now.isoformat(timespec='seconds'),
              'policy': ('One read per page with the project client. Raw bodies are kept for '
                         'review. No price is turned into a probability here.'),
              'pages': []}

    def capture(name, url):
        record = {'name': name, 'url': url,
                  'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
        try:
            body, evidence = src.get(name, url, as_json=False)
        except Exception as exc:
            record.update(status='error', error='%s: %s' % (type(exc).__name__, str(exc)[:200]))
            report['pages'].append(record)
            return record, ''
        record.update({k: v for k, v in evidence.items() if k != 'name'})
        record['readings'] = sniff(body)
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:80]
        (out / (slug + '.html')).write_text(body, encoding='utf-8')
        (out / (slug + '.sha256')).write_text(
            hashlib.sha256(body.encode('utf-8', 'replace')).hexdigest() + '\n', encoding='utf-8')
        report['pages'].append(record)
        return record, body

    listing_record, listing_html = capture('listing', LISTING)
    home_record, home_html = capture('home', HOME)

    links = []
    for match in MATCH_LINK_RE.finditer(listing_html) or MATCH_LINK_RE.finditer(home_html or ''):
        href = match.group(1)
        if href not in links:
            links.append(href)
    report['listing_links'] = links[:120]
    for href in links[:args.pages]:
        base = href.rsplit('/', 1)[-1]
        capture('match %s' % base, BASE + href.replace('/counterstrike/tip/', '/counterstrike/match/'))
        capture('tip %s' % base, BASE + href.replace('/counterstrike/match/', '/counterstrike/tip/'))

    (out / 'egw-probe.json').write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    for record in report['pages']:
        print('%-46s %s %s readings=%s' % (record['name'][:46], record.get('status'),
                                           record.get('bytes'), len(record.get('readings') or [])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
