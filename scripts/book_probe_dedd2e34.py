"""Read-only esportsbook accessibility probe (research only, never a price).

The user asked for a pick on every fixture on the board and, where the featured
method cannot resolve one, for research into esportsbooks and esports betting
lines. Whether a book can be used at all is a factual, checkable question, so
this script measures it instead of asserting it: it performs one unauthenticated
GET per endpoint, records HTTP status, content type, byte count and any error,
and never parses a result into a probability and never retries against an access
restriction.

Run only from the research workflow on an Actions runner (the authoring sandbox
has no route to these hosts). A 200 here means "reachable", not "usable": no
adapter is claimed for a source that this file does not show returning a
validated two-sided line.
"""
import argparse
import datetime
import json
import pathlib
import urllib.error
import urllib.request

UA = {'User-Agent': 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)',
      'Accept': 'application/json, text/html;q=0.9'}

# (name, url, category, why it matters). All are unauthenticated public
# endpoints that the operator's own site or a public registry consumes.
ENDPOINTS = [
    ('Pinnacle esports leagues', 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/leagues',
     'bookmaker', 'Whether the already-used book lists the league a fixture is played in.'),
    ('Pinnacle esports matchups', 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups?withSpecials=false',
     'bookmaker', 'The endpoint the collector already reads for a fallback bookmaker line.'),
    ('Pinnacle esports outrights', 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/tournaments',
     'bookmaker', 'Tournament-level lines; useful for context, never a match pick.'),
    ('Polymarket CS2 registry', 'https://gamma-api.polymarket.com/sports',
     'exchange', 'Registry entry that scopes the primary exchange method.'),
    ('Polymarket CS2 events', ('https://gamma-api.polymarket.com/events?tag_slug=cs2&active=true'
                               '&closed=false&limit=100&offset=0'),
     'exchange', 'How many CS2 markets the exchange currently exposes at all.'),
    ('HLTV match list', 'https://www.hltv.org/matches', 'schedule',
     'Identity and ranking context; the collector must not depend on it.'),
    ('GG.BET esports CS2 page', 'https://gg.bet/en/esports/counter-strike', 'bookmaker',
     'A book that covers low-tier CS2; measured for automated accessibility.'),
    ('GG.BET public sport API', 'https://gg.bet/api/v1/sport/matches/mixed?sport_ids%5B%5D=1&lang=en',
     'bookmaker', 'The JSON endpoint the site itself consumes; recorded as returned.'),
    ('Thunderpick CS2 page', 'https://thunderpick.io/esports/cs2-betting', 'bookmaker',
     'Event sponsor and a book with broad CS2 coverage; measured for accessibility.'),
    ('Thunderpick open API root', 'https://api.thunderpick.com/v1/sports', 'bookmaker',
     'Checked once: an open documented API would allow a validated adapter later.'),
    ('Oddschecker CS2 odds page', 'https://www.oddschecker.com/esports/counter-strike', 'aggregator',
     'An odds aggregator would give many books at once; measured for access control.'),
    ('Steam/Valve VRS standings index', 'https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings',
     'model', 'The originated-line input this project already uses.'),
]


def probe(name, url, category, why, timeout=25):
    record = {'name': name, 'url': url, 'category': category, 'why': why}
    try:
        request = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(400_000)
            record.update(status=response.status, content_type=response.headers.get('Content-Type'),
                          bytes=len(body), cache_age=response.headers.get('Age'))
    except urllib.error.HTTPError as exc:
        record.update(status=exc.code, error=str(exc)[:200])
    except Exception as exc:  # DNS, TLS, timeout, refused - all limitations, never a price
        record.update(status=None, error='%s: %s' % (type(exc).__name__, str(exc)[:200]))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='runtime/book-probe.json')
    parser.add_argument('--only', default=None, help='Substring filter, for a quick single check')
    args = parser.parse_args()
    results = []
    for name, url, category, why in ENDPOINTS:
        if args.only and args.only.lower() not in (name + url).lower():
            continue
        results.append(probe(name, url, category, why))
    payload = {'probed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
               'policy': ('One unauthenticated GET per endpoint. No cookies, no logins, no access-control '
                          'bypass, no retries against a refused host, and no probability derived from any '
                          'result. A reachable page is not an automated quote.'),
               'results': results}
    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, sort_keys=True) + '\n')
    for record in results:
        print('%-34s %s %s' % (record['name'], record.get('status'),
                               (record.get('content_type') or record.get('error') or '')[:60]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
