"""Session 11e17543 - a pick, or a recorded limitation, for EVERY match Hotspawn lists.

Why this exists
---------------
The production ladder (``scripts/refresh.py`` + ``scripts/core.py``) prices only the
rows whose pick lock is still open.  That is the right rule for a *recommendation*
board - a price you cannot act on is not a recommendation - but it left the rest of
the list with no pick at all.  Measured on the published snapshot
``2026-10-26T00:10:49Z`` (``data/latest.json``): Hotspawn's fixtures endpoint returned
**73** CS2 rows, **11** of them open and priced, **62** of them carrying nothing.

The requirement is coverage of *every* listed match.  This module therefore walks the
same source ladder over every row Hotspawn lists, and reports - per row - either a
sourced pick with a win probability, a sourced directional pick without one, or the
exact reason no pick could be generated.  Nothing is inferred: a row with no official
source stays blank and is reported as unresolved with its limitation.

Ladder (highest rung that returns evidence wins)
------------------------------------------------
0. ``pipeline``        - the line the production ladder already published for an open
                         row.  Kept verbatim, with its own evidence URL.
1. ``researched_line`` - a two-way price this session read on an outside esports
                         source for that exact fixture.  Only rows present in
                         ``research/session-11e17543/outside-lines.json`` qualify; the
                         file is written from captured responses, never from memory.
2. ``model_vrs``       - our own originated line from Valve's official Regional
                         Standings points through Valve's published expected-win
                         formula.  Labelled as a model everywhere; never a market price.
3. ``research_one_sided`` - exactly one club appears in Valve's official standings and
                         the other does not.  Directional pick only, no percentage.
4. ``unresolved``      - no official source supports a pick.  The row is published with
                         its limitation, never with a guessed number.

Every output row carries at least one official source URL, and ``actionable`` is false
whenever Hotspawn's own pick lock has passed, so a reader can never mistake a
historical line for a live recommendation.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import dt, norm, plain_name
from scripts import vrs

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'research' / 'session-11e17543'
OUTSIDE_LINES = OUT_DIR / 'outside-lines.json'

VALVE_URL = 'https://github.com/ValveSoftware/counter-strike_regional_standings'
HOTSPAWN_FEED = ('https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures'
                 '?sport_alias=cs2&status=scheduled&tenantId=1')
HOTSPAWN_LOBBY = 'https://play.hotspawn.com/lobby'

TIER_LABEL = {
    'pipeline': 'Published production line',
    'researched_line': 'Researched outside line',
    'model_vrs': 'Our Valve VRS model line',
    'research_one_sided': 'Research pick, no percentage',
    'research_bounded': 'Research pick, bounded direction, no percentage',
    'unresolved': 'Unresolved',
}
TIER_RANK = ['pipeline', 'researched_line', 'model_vrs', 'research_one_sided',
             'research_bounded', 'unresolved']


def _now(snapshot_iso):
    """The snapshot's own clock, or the machine clock when it carries none.

    ``scripts.core.dt`` raises on a missing or unparseable timestamp rather than
    returning None, so a synthetic snapshot built by a test used to take the whole
    ladder down with ``ValueError: Missing timestamp``. The snapshot clock is the
    right reference when it exists - the split must not move with the machine clock
    - and falling back is correct when it does not.
    """
    try:
        return dt(snapshot_iso)
    except (TypeError, ValueError, OverflowError, OSError):
        return datetime.now(timezone.utc)


def listed(name, standings):
    """True when a club label appears in Valve's official global standings.

    Ambiguity (the same label on two standings rows) does not matter for a
    one-sided *directional* pick: whichever row belongs to the club, the club is
    listed.  It does matter for a percentage, which is why :func:`scripts.vrs.line`
    refuses ambiguous labels and this rung publishes no number.
    """
    key = norm(name)
    return any(norm(row['name']) == key for row in standings['teams'])


def candidates(name, standings):
    """Every standings row Valve publishes under this label (alias-mapped)."""
    key = norm(name)
    return [row for row in standings['teams'] if norm(row['name']) == key]


def bounded_direction(teams, standings):
    """Direction that holds for EVERY roster Valve lists under either label.

    Valve's official ``standings_global_2026_10_05.md`` repeats 31 normalised labels
    on two different rows with two different rosters (measured: 'Johnny Speeds' is
    #99 / 1049 points and #164 / 802 points).  ``scripts.vrs.line`` correctly refuses
    to publish a percentage for those, because it cannot know which roster is meant.
    The *direction* can still be certain: if the weaker of one club's candidate
    point totals still beats the stronger of the other's, then every possible
    reading of Valve's file gives the same winner.  No roster is guessed and no
    number is invented - when the candidate ranges overlap the row stays unresolved.

    Returns ``(index, detail)`` or ``(None, reason)``.
    """
    sets = [candidates(t, standings) for t in teams]
    if not sets[0] or not sets[1]:
        return None, 'at least one club is absent from the Valve global standings'
    ranges = [(min(r['points'] for r in s), max(r['points'] for r in s)) for s in sets]
    if len(sets[0]) == 1 and len(sets[1]) == 1:
        return None, 'both labels are unique; the percentage rung already handled this row'
    detail = {'%s points' % teams[i]: sorted(r['points'] for r in sets[i]) for i in (0, 1)}
    if ranges[0][0] > ranges[1][1]:
        return 0, detail
    if ranges[1][0] > ranges[0][1]:
        return 1, detail
    return None, ("Valve's file lists %s as %s points and %s as %s points across its candidate rosters; the "
                  'ranges overlap, so the direction depends on a roster this project cannot confirm'
                  % (teams[0], ranges[0], teams[1], ranges[1]))



def outside_line(fixture_id, table):
    """Return this session's captured outside line for a fixture, or None."""
    entry = (table or {}).get(str(fixture_id))
    if not entry:
        return None
    prices = entry.get('prices')
    if not isinstance(prices, list) or len(prices) != 2:
        return None
    try:
        a, b = float(prices[0]), float(prices[1])
    except (TypeError, ValueError):
        return None
    if not (0 < a < 1 and 0 < b < 1):
        return None
    if abs(a + b - 1.0) > 0.02:
        return None
    if not entry.get('url') or not entry.get('provider'):
        return None
    return {'provider': entry['provider'], 'url': entry['url'],
            'probabilities': [a, b], 'observed_at': entry.get('observed_at'),
            'note': entry.get('note'), 'teams': entry.get('teams')}


def ladder_row(match, standings, meta, outside, snapshot_at):
    """One row of the every-match table. Never raises; always returns a dict."""
    teams = list(match['teams'])
    lock = dt(match['lock']) if match.get('lock') else None
    start = dt(match['start']) if match.get('start') else None
    actionable = match.get('state') == 'open'
    row = {
        'id': str(match['id']),
        'teams': teams,
        'competition': match.get('competition'),
        'tier': match.get('tier'),
        'start': match.get('start'),
        'lock': match.get('lock'),
        'actionable': actionable,
        'state': match.get('state'),
        'source_url': match.get('source_url') or HOTSPAWN_LOBBY,
        'feed_url': match.get('feed_url') or HOTSPAWN_FEED,
        'pick': None, 'probabilities': None, 'fair_odds': None,
        'ladder': None, 'ladder_label': None, 'sources': [], 'limitation': None,
    }
    if not actionable:
        passed = []
        if lock and lock < snapshot_at:
            passed.append('Hotspawn pick lock %s has passed' % match['lock'])
        if start and start < snapshot_at:
            passed.append('scheduled start %s has passed' % match['start'])
        row['limitation'] = ('Not actionable: ' + ' and '.join(passed) +
                             '. Any line below is historical evidence, not a current recommendation.'
                             if passed else 'Not open by sourced status or timestamp.')

    # Rung 0 - the production line, kept verbatim.
    if match.get('probabilities') and match.get('pick'):
        sources = [{'provider': ev.get('provider'), 'url': ev.get('url')}
                   for ev in (match.get('evidence') or [])
                   if isinstance(ev, dict) and ev.get('url')]
        if not sources:
            sources = [{'provider': match.get('method'), 'url': row['source_url']}]
        row.update(pick=match['pick'], probabilities=match['probabilities'],
                   fair_odds=match.get('fair_odds'), ladder='pipeline',
                   ladder_label=TIER_LABEL['pipeline'], sources=sources)
        return row

    # Rung 1 - an outside line this session captured for this exact fixture.
    quote = outside_line(match['id'], outside)
    if quote:
        p = quote['probabilities']
        index = 0 if p[0] > p[1] else 1
        row.update(pick=teams[index], probabilities=p, fair_odds=[1 / p[0], 1 / p[1]],
                   ladder='researched_line', ladder_label=TIER_LABEL['researched_line'],
                   sources=[{'provider': quote['provider'], 'url': quote['url']},
                            {'provider': 'Valve VRS (comparison only)', 'url': VALVE_URL}])
        return row

    # Rung 2 - our own originated Valve VRS line.
    quote, reason = vrs.line({'teams': teams}, standings, meta)
    if quote:
        p = quote['probabilities']
        index = 0 if p[0] > p[1] else 1
        sources = [{'provider': 'Valve Regional Standings %s' % standings['as_of'],
                    'url': meta.get('blob_url') or VALVE_URL}]
        # Valve publishes one detail page per listed club; linking them is what
        # makes the two point totals checkable by hand in one tap each.
        for name, detail in zip(quote.get('vrs_teams') or teams, quote.get('details_urls') or []):
            sources.append({'provider': 'Valve detail page: %s' % name, 'url': detail})
        row.update(pick=teams[index], probabilities=p, fair_odds=[1 / p[0], 1 / p[1]],
                   ladder='model_vrs', ladder_label=TIER_LABEL['model_vrs'],
                   sources=sources,
                   vrs_points=list(quote.get('points') or []),
                   vrs_standings=list(quote.get('standings') or []))
        return row

    # Rung 2b - Valve lists a club's label twice, but the direction still holds for
    # every roster it publishes.  No percentage: the points are ambiguous.
    index, detail = bounded_direction(teams, standings)
    if index is not None:
        note = ("Valve's official standings list %s twice with two different rosters, so no win percentage is "
                'published. The direction holds for every reading: candidate points %s.'
                % (teams[index], json.dumps(detail)))
        row.update(pick=teams[index], ladder='research_bounded',
                   ladder_label=TIER_LABEL['research_bounded'],
                   sources=[{'provider': 'Valve Regional Standings %s' % standings['as_of'],
                             'url': meta.get('blob_url') or VALVE_URL}],
                   limitation=((row['limitation'] + ' ') if row['limitation'] else '') + note)
        return row

    # Rung 3 - one-sided Valve standings evidence: directional, no percentage.
    flags = [listed(t, standings) for t in teams]
    if flags.count(True) == 1:
        index = 0 if flags[0] else 1
        note = ('One club (%s) is listed in Valve\'s official standings and %s is not; that supports a direction '
                'but no win probability.' % (teams[index], teams[1 - index]))
        row.update(pick=teams[index], ladder='research_one_sided',
                   ladder_label=TIER_LABEL['research_one_sided'],
                   sources=[{'provider': 'Valve Regional Standings %s' % standings['as_of'],
                             'url': meta.get('blob_url') or VALVE_URL}],
                   limitation=((row['limitation'] + ' ') if row['limitation'] else '') + note)
        return row

    # Rung 4 - unresolved, with the reason that actually came back.
    row.update(ladder='unresolved', ladder_label=TIER_LABEL['unresolved'],
               sources=[{'provider': 'Valve Regional Standings %s' % standings['as_of'],
                         'url': meta.get('blob_url') or VALVE_URL}])
    row['limitation'] = ((row['limitation'] or '') + ' No pick: ' + reason +
                         ' No outside esports line for this fixture could be confirmed from an official source.').strip()
    return row


def report(rows, generated_at, fixtures_observed_at, standings, meta, outside,
           session='11e17543', snapshot_path=None):
    """Run the ladder over ``rows`` and return the report dict.

    Split out from :func:`build` so the site builder can run the identical ladder
    over the snapshot it is publishing (after ``scripts.build`` has already expired
    whatever it must expire) instead of re-reading a file that may be older.
    """
    snapshot_at = _now(generated_at)
    out = [ladder_row(m, standings, meta, outside, snapshot_at) for m in rows]
    counts = {tier: sum(1 for r in out if r['ladder'] == tier) for tier in TIER_RANK}
    return {
        'session': session,
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'snapshot_generated_at': generated_at,
        'fixtures_observed_at': fixtures_observed_at,
        'snapshot_path': snapshot_path,
        'standings': {'as_of': standings['as_of'], 'file': meta['file'], 'blob_url': meta.get('blob_url'),
                      'origin': meta.get('origin')},
        'feed_url': HOTSPAWN_FEED,
        'lobby_url': HOTSPAWN_LOBBY,
        'rows_total': len(out),
        'actionable': sum(1 for r in out if r['actionable']),
        'with_pick': sum(1 for r in out if r['pick']),
        'with_probability': sum(1 for r in out if r['probabilities']),
        'unresolved': counts['unresolved'],
        'counts_by_ladder': counts,
        'rows': out,
    }


def load_outside(outside_path=None):
    """This session's captured outside lines, keyed by Hotspawn fixture id."""
    outside_path = Path(outside_path or OUTSIDE_LINES)
    if not outside_path.exists():
        return {}
    return json.loads(outside_path.read_text()).get('lines') or {}


def build(snapshot_path=None, outside_path=None):
    """Run the ladder over every row in the snapshot and return the report dict."""
    snapshot_path = Path(snapshot_path or ROOT / 'data' / 'latest.json')
    data = json.loads(snapshot_path.read_text())
    outside = load_outside(outside_path)
    standings, meta = vrs.vendored()
    return report(data['matches'], data.get('generated_at'), data.get('fixtures_observed_at'),
                  standings, meta, outside, snapshot_path=str(snapshot_path.relative_to(ROOT)))


CSV_FIELDS = ['id', 'teams', 'competition', 'tier', 'start', 'lock', 'actionable', 'pick',
              'p_team1', 'p_team2', 'ladder', 'ladder_label', 'source_urls', 'limitation']


def to_csv(report):
    out = []
    for r in report['rows']:
        p = r['probabilities']
        out.append({
            'id': r['id'], 'teams': ' vs '.join(r['teams']), 'competition': r['competition'],
            'tier': r['tier'], 'start': r['start'], 'lock': r['lock'],
            'actionable': 'yes' if r['actionable'] else 'no',
            'pick': r['pick'] or '', 'p_team1': ('%.4f' % p[0]) if p else '',
            'p_team2': ('%.4f' % p[1]) if p else '',
            'ladder': r['ladder'], 'ladder_label': r['ladder_label'],
            'source_urls': ' | '.join(s['url'] for s in r['sources'] if s.get('url')),
            'limitation': r['limitation'] or '',
        })
    return out


def to_markdown(report):
    lines = [
        '# Every match Hotspawn lists for CS2 - pick, probability, or the reason there is neither',
        '',
        'Session `11e17543`. Snapshot `%s` (fixture evidence `%s`). Standings: Valve `%s`.' % (
            report['snapshot_generated_at'], report['fixtures_observed_at'], report['standings']['as_of']),
        '',
        'Feed: <%s>' % report['feed_url'],
        '',
        '| Coverage | Count |',
        '| --- | --- |',
        '| CS2 rows Hotspawn lists | %d |' % report['rows_total'],
        '| Still actionable (pick lock open) | %d |' % report['actionable'],
        '| With a pick | %d |' % report['with_pick'],
        '| With a win probability | %d |' % report['with_probability'],
        '| Unresolved (no official source supports a pick) | %d |' % report['unresolved'],
        '',
    ]
    for tier in TIER_RANK:
        lines.append('* %s: %d' % (TIER_LABEL[tier], report['counts_by_ladder'][tier]))
    lines += ['', '| Fixture | Match | Start (UTC) | Actionable | Pick | Win probability | Ladder rung | Source | Limitation |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in sorted(report['rows'], key=lambda x: (not x['actionable'], x['start'] or '')):
        p = r['probabilities']
        prob = '%s %.1f%% / %s %.1f%%' % (r['teams'][0], p[0] * 100, r['teams'][1], p[1] * 100) if p else 'none published'
        src = '<br>'.join('[%s](%s)' % (s.get('provider') or 'source', s['url']) for s in r['sources'] if s.get('url'))
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['id'], ' vs '.join(r['teams']), r['start'] or '', 'yes' if r['actionable'] else 'no',
            r['pick'] or '-', prob, r['ladder_label'], src, (r['limitation'] or '').replace('|', '/')))
    lines.append('')
    return '\n'.join(lines)


def write_all(report=None, out_dir=None):
    report = report or build()
    out_dir = Path(out_dir or OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'every-match-picks.json').write_text(json.dumps(report, indent=1, sort_keys=False) + '\n')
    with (out_dir / 'every-match-picks.csv').open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(to_csv(report))
    (out_dir / 'every-match-picks.md').write_text(to_markdown(report))
    return report


if __name__ == '__main__':
    rep = write_all()
    print('rows %d | picks %d | probabilities %d | unresolved %d' % (
        rep['rows_total'], rep['with_pick'], rep['with_probability'], rep['unresolved']))
    print('by rung:', json.dumps(rep['counts_by_ladder']))
