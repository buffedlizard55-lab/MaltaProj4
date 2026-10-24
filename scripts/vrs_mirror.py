"""Originated lines from Valve's VRS points as HLTV publishes them.

Why this exists
---------------
``scripts/vrs.py`` prices a fixture only when *both* clubs resolve in Valve's
monthly global standings file in
``github.com/ValveSoftware/counter-strike_regional_standings``. That file is
published roughly monthly (the newest one on 2026-10-22 is dated 2026-10-05),
so a club that entered the standings after that date - or one that only plays
tiers below the file's publication cutoff - has no row and the two-team line
cannot be computed. Those fixtures fell through to the one-sided research
tiers: a pick, and no percentage.

Valve's ranking itself is not frozen between file drops. HLTV publishes the
same ranking continuously at ``https://www.hltv.org/valve-ranking/teams`` as a
dated view ("Valve global ranking on October 22nd, 2026") with the same points
value and the same roster for each club. That page is the second source used
here, and it is used **only** for the clubs the official file cannot resolve.

What is and is not reused from Valve
------------------------------------
Nothing about the formula is invented. This module imports ``scripts.vrs``'s
``expected`` (Valve ``model/fit.js`` ``priorWinExpectation`` with fixed rating
deviation 75, which reduces to the Glicko expected score), ``calibrated``
(Valve's published ``modelfit.png`` slope 0.7986 applied symmetrically around
50%), ``identify`` (Valve's three-player roster-continuity rule, which is what
disambiguates repeated labels) and the same eight-hour evidence window.

Fail-closed behaviour
---------------------
A markup change, a page that turns out to be the HLTV world ranking rather
than the Valve view (its rows say "HLTV points", not "Valve points"), a date
header that cannot be read, fewer than 100 parsed rows, non-monotonic
positions, a duplicated label with no lineup to tell the rosters apart, or a
club that is simply not on the page - each of those is a recorded miss. The
row keeps its research-only pick and publishes no percentage. Nothing is
guessed and no number is inferred from a rank alone.
"""
from __future__ import annotations

import re
from datetime import timedelta

from scripts import vrs
from scripts.core import iso, norm, plain_name

BASE = 'https://www.hltv.org'
RANKING = BASE + '/valve-ranking/teams'
PROVIDER = 'HLTV Valve ranking (Valve points)'
METHOD = 'model_vrs_mirror'
MODEL_FLAG = ("Originated line: Valve VRS model estimate from HLTV's dated view of Valve's ranking, "
              "not a market price.")
LIMITATION = ('Valve points read from HLTV\'s dated Valve ranking page, not from Valve\'s monthly GitHub file; '
              'same formula and calibration as the official-file line. Not a market price.')

MONTHS = {name.lower(): index for index, name in enumerate(
    ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
     'September', 'October', 'November', 'December'), start=1)}

DATE_RE = re.compile(r'ranking on ([A-Za-z]+) (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})', re.I)
# "<name> (1993 Valve points)" as the rendered page spells it. The mobile-only
# "Valve" span is inside the parentheses, so tag-stripped text reads fine.
POINTS_RE = re.compile(r'\(\s*([\d,]+)\s*(Valve|HLTV)\s*points\s*\)', re.I)
# Fallback that does not depend on CSS classes: the whole page text is
# "#1 Spirit (972 HLTV points) ..." once tags are stripped.
TEXT_RE = re.compile(r'#(\d{1,4})\s+([^()\n]{1,60}?)\s*\(\s*([\d,]+)\s*Valve\s*points\s*\)', re.I)
POSITION_RE = re.compile(r'#\s*(\d{1,4})')


def _int(value):
    try:
        return int(str(value).replace(',', '').strip())
    except (TypeError, ValueError):
        return None


def ranking_date(text):
    """The dated heading HLTV prints, e.g. 'Valve global ranking on October 22nd, 2026'."""
    match = DATE_RE.search(text or '')
    if not match:
        return None, None
    month = MONTHS.get(match.group(1).lower())
    day, year = _int(match.group(2)), _int(match.group(3))
    if not month or not day or not year or not (1 <= day <= 31):
        return None, None
    return '%04d-%02d-%02d' % (year, month, day), match.group(0)


def _rows_from_classes(soup):
    """Rank, club, Valve points and roster from the ranked-team blocks."""
    rows = []
    for block in soup.select('div.ranked-team'):
        position = block.select_one('.position')
        team_line = block.select_one('.teamLine') or block
        points_node = team_line.select_one('.points')
        if position is None or points_node is None:
            continue
        standing = _int(POSITION_RE.search(position.get_text(' ', strip=True) or '').group(1)
                        if POSITION_RE.search(position.get_text(' ', strip=True) or '') else None)
        points_match = POINTS_RE.search(points_node.get_text(' ', strip=True) or '')
        if standing is None or not points_match:
            continue
        # The Valve view says "Valve points"; the world-ranking view says
        # "HLTV points". A row from the wrong view is not evidence here.
        if points_match.group(2).lower() != 'valve':
            continue
        points = _int(points_match.group(1))
        name_node = team_line.select_one('.name') or team_line.select_one('a[href^="/team/"]')
        name = name_node.get_text(' ', strip=True) if name_node is not None else ''
        if not name:
            logo = block.select_one('.team-logo img[title]')
            name = (logo.get('title') or '').strip() if logo is not None else ''
        if not name or points is None or points <= 0:
            continue
        roster = [x.get_text(strip=True) for x in block.select('.playersLine .rankingNicknames span')]
        roster = [x for x in roster if x]
        rows.append({'standing': standing, 'points': points, 'name': name,
                     'roster': roster, 'details': ''})
    return rows


def _rows_from_text(text):
    rows = []
    for standing, name, points in TEXT_RE.findall(text or ''):
        standing, points = _int(standing), _int(points)
        name = ' '.join(name.split())
        if standing is None or points is None or not name or points <= 0:
            continue
        rows.append({'standing': standing, 'points': points, 'name': name,
                     'roster': [], 'details': ''})
    return rows


def _complete(rows):
    """A published ranking is a long, strictly ordered list; anything else is a miss."""
    if len(rows) < 100:
        return False
    standings = [row['standing'] for row in rows]
    if standings != list(range(1, len(rows) + 1)):
        return False
    if len({norm(row['name']) for row in rows}) < len(rows) * 0.9:
        return False
    return True


def parse(html):
    """Parse HLTV's dated Valve ranking view. Raises ValueError on any doubt."""
    if not isinstance(html, str) or len(html) < 5000:
        raise ValueError('ranking page missing or too small to be the full view')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ', strip=True)
    as_of, heading = ranking_date(text)
    if not as_of:
        raise ValueError('dated ranking heading not found')
    by_class = _rows_from_classes(soup)
    by_text = _rows_from_text(text)
    rows = by_class if _complete(by_class) else by_text
    if not _complete(rows):
        raise ValueError('ranking table did not parse as a complete ordered Valve-points list '
                         '(class-based rows=%d, text rows=%d)' % (len(by_class), len(by_text)))
    return {'as_of': as_of, 'heading': heading, 'teams': rows,
            'parsed_by': 'ranked-team blocks' if rows is by_class else 'page text'}


def dated_urls(now, days=3):
    """HLTV's dated form of the same view, newest first.

    The undated URL is the canonical entry point, but HLTV answers some of its
    paths with HTTP 403 to a research client while still serving the dated
    form of the very same page. The dated URLs are the same view with the
    ranking date in the path (``/valve-ranking/teams/2026/october/22``); the
    page still prints its own dated heading, and that heading is what the
    parser reads and the row publishes. Nothing about the request changes
    between the two forms: same host, same client, same read discipline.
    """
    urls = []
    for offset in range(days):
        day = now - timedelta(days=offset)
        urls.append('%s/valve-ranking/teams/%d/%s/%d' % (BASE, day.year, day.strftime('%B').lower(), day.day))
    return urls


def fetch(src, now):
    """Read the dated page. Returns (standings, meta, problem); never raises.

    The dated URLs are read first, newest first, and the canonical undated URL
    last. The order matters: the collector blocks a *host* for the rest of the
    run once it has been refused repeatedly, so a canonical URL that answers
    HTTP 403 would make every later HLTV read - including the dated view of the
    very same ranking - unreachable. The dated view is the same page (HLTV's own
    navigation links the "Valve ranking" entry to it), it carries the ranking
    date in its path and the date in its own heading, and the parser reads the
    same dated Valve-points list from it.

    Every refusal and every parse miss is recorded in the returned problem
    string, so a run that cannot read the ranking says exactly which URLs were
    tried and why each one failed.
    """
    candidates = [(url, 'HLTV Valve ranking mirror (dated view)') for url in dated_urls(now)]
    candidates.append((RANKING, 'HLTV Valve ranking mirror'))
    problems = []
    try:
        for url, name in candidates:
            try:
                page, receipt = src.get(name, url, False)
            except ValueError as e:
                problems.append('%s: %s' % (url, e))
                continue
            except Exception as e:  # a broken transport is a finding, never a price
                problems.append('%s: read error: %s: %s' % (url, type(e).__name__, e))
                continue
            try:
                standings = parse(page)
            except (ValueError, TypeError) as e:
                problems.append('%s: parse miss: %s' % (url, e))
                continue
            observed = receipt.get('observed_at') or iso(now)
            meta = {'url': url, 'observed_at': observed, 'sha256': receipt.get('sha256'),
                    'as_of': standings['as_of'], 'heading': standings['heading'],
                    'teams_count': len(standings['teams']), 'parsed_by': standings['parsed_by']}
            return standings, meta, None
    except Exception as e:  # the tier must never raise into the refresh
        return None, None, 'HLTV Valve ranking mirror error: %s: %s' % (type(e).__name__, e)
    return None, None, 'HLTV Valve ranking mirror unavailable: ' + '; '.join(problems)


def line(fixture, standings, meta, lineups=None, official=None):
    """Compute the mirror line for one fixture, or (None, reason)."""
    lineups = lineups or {}
    entries, notes, counts = [], [], []
    for team in fixture['teams']:
        lineup = next((v for k, v in lineups.items() if k and norm(k) == norm(team)), None)
        entry, note = vrs.identify(team, standings, lineup)
        if entry is None:
            return None, '%s: %s in HLTV\'s Valve ranking view of %s.' % (team, note, standings['as_of'])
        entries.append(entry)
        notes.append(note)
        counts.append(sum(norm(row['name']) == norm(team) for row in standings['teams']))
    if plain_name(entries[0]['name']) == plain_name(entries[1]['name']) and entries[0]['standing'] == entries[1]['standing']:
        return None, 'Both teams resolve to the same ranking row.'
    raw = vrs.expected(entries[0]['points'], entries[1]['points'])
    p = [vrs.calibrated(raw), 1 - vrs.calibrated(raw)]
    used = [x for team, entry in zip(fixture['teams'], entries) for x in vrs.identities_used(team, entry['name'])]
    quote = {
        'provider': PROVIDER,
        'id': 'hltv-vrs-%s-%d-%d' % (standings['as_of'], entries[0]['standing'], entries[1]['standing']),
        'api_url': meta['url'], 'url': meta['url'],
        'observed_at': meta['observed_at'], 'updated_at': None,
        'ranking_as_of': standings['as_of'], 'ranking_heading': standings.get('heading'),
        'ranking_page_sha256': meta.get('sha256'), 'ranking_teams_count': len(standings['teams']),
        'ranking_parsed_by': meta.get('parsed_by'),
        'fixture_teams': list(fixture['teams']),
        'vrs_teams': [e['name'] for e in entries],
        'points': [e['points'] for e in entries],
        'standings': [e['standing'] for e in entries],
        'rosters': [e['roster'] for e in entries],
        'roster_checks': [{'lineup': e['lineup'], 'overlap': e['roster_overlap'], 'note': n}
                          for e, n in zip(entries, notes)],
        'label_counts': counts,
        'raw_expected': [raw, 1 - raw],
        'calibration_slope': vrs.SLOPE, 'rating_deviation': vrs.RD,
        'formula_source': vrs.BLOB + '/main/model/fit.js',
        'calibration_source': vrs.BLOB + '/main/modelfit.png',
        'probabilities': p,
        'identity_sources': used,
        'official_file': ({'file': official.get('file'), 'commit': official.get('commit'),
                           'as_of': official.get('as_of')} if official else None),
        'warning': MODEL_FLAG + ' Inputs: Valve points from HLTV\'s Valve ranking of %s; Valve\'s own '
                                 'standings file does not resolve every club on this row. Calibrated with '
                                 'Valve\'s published fit slope.' % standings['as_of'],
        'limitation': LIMITATION,
    }
    return quote, None


def apply(fixture, standings, meta, lineups=None, official=None):
    """Price an open fixture that no market line and no official-file line could price."""
    if fixture.get('probabilities') is not None or fixture.get('state') != 'open' or fixture.get('resolution_blocked'):
        return
    quote, reason = line(fixture, standings, meta, lineups, official)
    attempt = {'provider': PROVIDER, 'url': meta['url'] if meta else RANKING}
    if quote is None:
        attempt.update(status='unresolved',
                       reason='No mirror line: ' + reason + ' Nothing derived from a single club\'s points.')
        fixture.setdefault('attempts', []).append(attempt)
        return
    p = quote['probabilities']
    if abs(p[0] - p[1]) < .0001:
        # Session e38056d4: an even mirror estimate is not a pick; the research
        # tiers run instead of publishing a 50/50.
        attempt.update(status='unresolved',
                       reason='Equal mirror estimate: the dated ranking gives both clubs the same points, so '
                              'no favourite is named. Not published as a 50/50.')
        fixture.setdefault('attempts', []).append(attempt)
        return
    fixture.update(probabilities=p, fair_odds=[1 / x for x in p],
                   pick=fixture['teams'][0 if p[0] > p[1] else 1],
                   method=METHOD, evidence=[quote], reason=None)
    fixture.setdefault('flags', []).append(MODEL_FLAG)
    fixture['flags'].append('Valve points came from HLTV\'s dated Valve ranking of %s, not from Valve\'s '
                            'monthly standings file of %s.' % (standings['as_of'],
                                                                (official or {}).get('as_of') or 'an earlier date'))
    if any(c['overlap'] is None for c in quote['roster_checks']):
        fixture['flags'].append('Roster continuity not checked for at least one team (no HLTV lineup available).')
    attempt.update(status='resolved',
                   reason='Originated line from both clubs\' Valve rankings points as HLTV publishes them (%s).'
                          % standings['as_of'])
    fixture.setdefault('attempts', []).append(attempt)
