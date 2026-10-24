"""Originated lines from Valve's official Regional Standings (VRS).

Inputs are official: Valve publishes its global standings in
github.com/ValveSoftware/counter-strike_regional_standings. The ``Points``
column is the team's Glicko rank value (model/report.js prints
``glickoTeam.rank()``).

Formula, reproduced from Valve's own model code, not invented here:
model/fit.js ``priorWinExpectation`` evaluates a match with fixed rating
deviation 75 (``defaultGlickoParams.rd``) using model/glicko.js. The win and
loss rating deltas share one factor, so the expected win rate reduces exactly
to the Glicko expected score::

    g  = 1 / sqrt(1 + 3 q^2 RD^2 / pi^2),  q = ln(10) / 400, RD = 75
    E  = 1 / (1 + 10 ** (-g * (points_a - points_b) / 400))

Calibration: Valve's published model-fit chart (modelfit.png, same
repository) reports observed = 0.7986 x expected + 0.126, i.e. the raw
expectation is overconfident. We apply the published slope symmetrically
around 50% so the two sides always sum to one::

    p = 0.5 + 0.7986 * (E - 0.5)

Identity: Valve treats rosters sharing at least three players as the same
team (model/team.js ``TEAM_OVERLAP_TO_SHARE_ROSTER = 3``). The standings
repeat some labels for older rosters, so a label is used only when it is
unique, or when the current HLTV lineup selects exactly one listed roster.

This is a model estimate, never presented as a market price.
"""
import copy
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import norm, plain_name, IDENTITIES, iso, directional

OWNER_REPO = 'ValveSoftware/counter-strike_regional_standings'
API = 'https://api.github.com/repos/' + OWNER_REPO
RAW = 'https://raw.githubusercontent.com/' + OWNER_REPO
BLOB = 'https://github.com/' + OWNER_REPO + '/blob'
RD = 75.0
Q = math.log(10) / 400
G = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
SLOPE = 0.7986
ROSTER_OVERLAP = 3
MAX_STANDINGS_AGE_DAYS = 62  # Valve publishes monthly; two missed updates is too old.
VENDORED = Path(__file__).resolve().parents[1] / 'data/vrs'
FILE_RE = re.compile(r'^standings_global_(\d{4})_(\d{2})_(\d{2})\.md$')
ROW_RE = re.compile(r'^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]\(([^)]+)\)')
MODEL_FLAG = 'Originated line: Valve VRS model estimate, not a market price.'


def expected(points_a, points_b):
    """Valve's fit.js expected win rate for team A (Glicko expected score, RD 75)."""
    return 1 / (1 + 10 ** (-G * (float(points_a) - float(points_b)) / 400))


def calibrated(raw):
    """Valve's published fit slope, applied symmetrically around 50%."""
    return 0.5 + SLOPE * (raw - 0.5)


def parse(text):
    """Parse a published standings markdown file into rows. Fails closed."""
    as_of = re.search(r'Standings as of (\d{4})_(\d{2})_(\d{2})', text)
    if not as_of:
        raise ValueError('VRS standings date header missing')
    rows = []
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        roster = [p.strip() for p in m.group(4).split(',') if p.strip()]
        rows.append({'standing': int(m.group(1)), 'points': int(m.group(2)), 'name': m.group(3).strip(),
                     'roster': roster, 'details': m.group(5)})
    if len(rows) < 50 or [r['standing'] for r in rows] != sorted(r['standing'] for r in rows):
        raise ValueError('VRS standings table did not parse as a complete ordered table')
    return {'as_of': '-'.join(as_of.groups()), 'teams': rows}


def _players(values):
    return {plain_name(v) for v in values or [] if v and plain_name(v)}


def identify(team, standings, lineup=None):
    """Return (entry, note) for a Hotspawn team label, or (None, reason)."""
    key = norm(team)
    hits = [row for row in standings['teams'] if norm(row['name']) == key]
    if not hits:
        return None, 'not listed in the Valve global standings'
    if lineup:
        current = _players(lineup)
        scored = sorted(((len(current & _players(row['roster'])), row) for row in hits), key=lambda x: -x[0])
        best = scored[0][0]
        if best < ROSTER_OVERLAP:
            return None, ('listed under this name, but the current HLTV lineup shares fewer than %d players with every '
                          'listed roster (Valve roster-continuity rule)' % ROSTER_OVERLAP)
        if len(scored) > 1 and scored[1][0] == best:
            return None, 'more than one listed roster shares the same number of players with the current HLTV lineup'
        return dict(scored[0][1], roster_overlap=best, lineup=list(lineup)), 'roster verified against the HLTV lineup'
    if len(hits) == 1:
        return dict(hits[0], roster_overlap=None, lineup=None), 'unique label; roster not checked (no lineup available)'
    return None, 'label appears %d times in the standings and no lineup was available to tell the rosters apart' % len(hits)


def identities_used(team, vrs_name):
    if plain_name(team) == plain_name(vrs_name):
        return []
    return copy.deepcopy([item for item in IDENTITIES if {plain_name(team), plain_name(vrs_name)} <= {plain_name(n) for n in item['names']}])


def line(fixture, standings, meta, lineups=None):
    """Compute the originated line for one fixture, or (None, reason)."""
    lineups = lineups or {}
    entries, notes, counts = [], [], []
    for team in fixture['teams']:
        lineup = next((v for k, v in lineups.items() if k and norm(k) == norm(team)), None)
        entry, note = identify(team, standings, lineup)
        if entry is None:
            return None, '%s: %s.' % (team, note)
        entries.append(entry)
        notes.append(note)
        counts.append(sum(norm(row['name']) == norm(team) for row in standings['teams']))
    if plain_name(entries[0]['name']) == plain_name(entries[1]['name']) and entries[0]['standing'] == entries[1]['standing']:
        return None, 'Both teams resolve to the same standings row.'
    raw = expected(entries[0]['points'], entries[1]['points'])
    p = [calibrated(raw), 1 - calibrated(raw)]
    used = [x for team, entry in zip(fixture['teams'], entries) for x in identities_used(team, entry['name'])]
    quote = {
        'provider': 'Valve VRS model',
        'id': 'vrs-%s-%d-%d' % (standings['as_of'], entries[0]['standing'], entries[1]['standing']),
        'api_url': meta['raw_url'], 'url': meta['blob_url'],
        'observed_at': meta['observed_at'], 'updated_at': None,
        'standings_as_of': standings['as_of'], 'standings_commit': meta.get('commit'),
        'standings_file': meta['file'], 'standings_origin': meta['origin'],
        'fixture_teams': list(fixture['teams']),
        'vrs_teams': [e['name'] for e in entries],
        'points': [e['points'] for e in entries],
        'standings': [e['standing'] for e in entries],
        'rosters': [e['roster'] for e in entries],
        'details_urls': [meta['details_base'] + e['details'] for e in entries],
        'roster_checks': [{'lineup': e['lineup'], 'overlap': e['roster_overlap'], 'note': n} for e, n in zip(entries, notes)],
        'label_counts': counts,
        'raw_expected': [raw, 1 - raw],
        'calibration_slope': SLOPE, 'rating_deviation': RD,
        'formula_source': BLOB + '/' + (meta.get('commit') or 'main') + '/model/fit.js',
        'calibration_source': BLOB + '/' + (meta.get('commit') or 'main') + '/modelfit.png',
        'probabilities': p,
        'identity_sources': used,
        'warning': MODEL_FLAG + ' Inputs: Valve standings of %s; calibrated with Valve\'s published fit slope.' % standings['as_of'],
    }
    return quote, None


def apply(fixture, standings, meta, lineups=None):
    """Price an open fixture that has no market line. Never overwrites a market."""
    if fixture['probabilities'] is not None or fixture['state'] != 'open' or fixture.get('resolution_blocked'):
        return
    quote, reason = line(fixture, standings, meta, lineups)
    attempt = {'provider': 'Valve VRS model', 'url': meta['blob_url'] if meta else BLOB}
    if quote is None:
        attempt.update(status='unresolved', reason='No originated line: ' + reason)
        fixture['attempts'].append(attempt)
        return
    p = quote['probabilities']
    index = directional(p)
    if index is None:
        # Session 2b856884: a model line that lands exactly on 0.5000/0.5000 names
        # no side either, so it follows the same convention as the exchange and
        # book tiers -- kept as neutral context in ``no_edge_lines``, recorded as
        # an unresolved attempt, and the row continues to the research tiers
        # instead of publishing a coin flip with no pick.
        fixture.setdefault('no_edge_lines', []).append(copy.deepcopy(quote))
        fixture['reason'] = 'Equal model estimate; no directional edge. Continue independent research.'
        attempt.update(status='unresolved', reason='Originated Valve model is exactly even (0.5000 / 0.5000); no directional edge. The '
                       'neutral line is retained in no_edge_lines as context, the rejected quote remains '
                       'replayable, and the ladder continues.',
                       rejected_quote=dict(quote, notice='Rejected evidence, not a pick or verified probability.'))
        fixture['attempts'].append(attempt)
        return
    fixture.update(probabilities=p, fair_odds=[1 / x for x in p], pick=fixture['teams'][index],
                   method='model_vrs', evidence=[quote], reason=None)
    fixture['flags'].append(MODEL_FLAG)
    if any(c['overlap'] is None for c in quote['roster_checks']):
        fixture['flags'].append('VRS roster continuity not checked for at least one team (no HLTV lineup available).')
    attempt.update(status='resolved', reason='Originated line from both teams\' Valve standings points (%s).' % standings['as_of'])
    fixture['attempts'].append(attempt)


RESEARCH_FLAG = ('Research pick on one-sided Valve standings evidence (only one team is listed '
                 'in the official global standings): no probability published.')


def research_resolution(fixture, standings, meta, lineups=None):
    """Per-team Valve standings evidence, re-derivable from the snapshot alone.

    Mirrors ``scripts.core.rank_resolution`` for the HLTV tiers: each row keeps
    the fixture label, the matched Valve label (or genuine absence from the
    file), the standings position/points/roster when listed, and the label
    count, so a validator that never touches the network can still re-derive
    any pick made from it.
    """
    lineups = lineups or {}
    resolved = []
    for team in fixture['teams']:
        lineup = next((v for k, v in lineups.items() if k and norm(k) == norm(team)), None)
        entry, note = identify(team, standings, lineup)
        count = sum(norm(row['name']) == norm(team) for row in standings['teams'])
        resolved.append({
            'team': team,
            'vrs_name': entry['name'] if entry else None,
            'standing': entry['standing'] if entry else None,
            'points': entry['points'] if entry else None,
            'roster': entry['roster'] if entry else None,
            'details_url': (meta['details_base'] + entry['details']) if entry else None,
            'roster_overlap': entry['roster_overlap'] if entry else None,
            'lineup': entry['lineup'] if entry else (list(lineup) if lineup else None),
            'label_count': count,
            'identity_sources': identities_used(team, entry['name']) if entry else [],
            'note': note,
            'status': 'listed' if entry else ('absent' if count == 0 else 'unresolved_label'),
        })
    return {'standings_as_of': standings['as_of'], 'standings_file': meta['file'],
            'standings_commit': meta.get('commit'), 'standings_origin': meta['origin'],
            'source': meta['blob_url'], 'raw_url': meta['raw_url'],
            'observed_at': meta['observed_at'], 'teams_count': len(standings['teams']),
            'resolved_vrs': resolved}


def research_single(fixture, standings, meta, lineups=None):
    """Last-resort research pick: one team is in Valve's standings, one is not.

    Final tier, after every market line, the originated two-team model line
    and the HLTV ranking tiers. It fires only when exactly one team resolves
    in Valve's official global standings under the same identity rules as the
    model line (unique label, or a current HLTV lineup sharing at least three
    players with exactly one listed roster) and the other team's label is
    genuinely absent from that file. It publishes a pick and no numbers: no
    probability, no fair odds and no points-difference formula, because one
    input of that formula does not exist.

    Two conflicts keep it silent: a present-but-unusable label (duplicate
    label, or a listed roster the current lineup no longer matches) is not
    "absent"; and if the HLTV fixture page already displays a VRS rank for
    the supposedly absent team, HLTV is looking at a newer VRS view than the
    standings file, so the absence claim is not made.
    """
    if fixture['probabilities'] is not None or fixture['state'] != 'open' or fixture.get('resolution_blocked'):
        return
    if fixture.get('pick'):
        return
    evidence = research_resolution(fixture, standings, meta, lineups)
    fixture['vrs_research'] = evidence
    resolved = evidence['resolved_vrs']
    listed = [r for r in resolved if r['status'] == 'listed']
    attempt = {'provider': 'Valve VRS research',
               'url': meta['blob_url'] if meta else BLOB}
    problems = []
    if len(listed) != 1:
        problems.append('%d of the two teams resolve in the Valve global standings, not exactly one' % len(listed))
    else:
        winner = listed[0]
        loser = next(r for r in resolved if r is not winner)
        if loser['status'] != 'absent':
            problems.append('%s is named in the standings but cannot be resolved (%s), so it is not treated as absent'
                            % (loser['team'], loser['note']))
        if plain_name(winner['vrs_name']) != plain_name(winner['team']) and not identities_used(winner['team'], winner['vrs_name']):
            problems.append('the listed label %s differs from the fixture label with no registered identity source'
                            % winner['vrs_name'])
        context = fixture.get('hltv_context') or {}
        for row in context.get('ranks', []):
            if norm(row.get('team') or '') == norm(loser['team']) and row.get('vrs_rank_on_hltv'):
                problems.append('HLTV already displays VRS rank #%d for %s, so absence from the %s file is not treated as unlisted'
                                % (row['vrs_rank_on_hltv'], loser['team'], standings['as_of']))
    if problems:
        attempt.update(status='unresolved',
                       reason='No one-sided Valve standings pick: ' + '; '.join(problems) + '. No pick invented, and no probability derived from a single points value.')
        fixture['attempts'].append(attempt)
        return
    winner = listed[0]
    loser = next(r for r in resolved if r is not winner)
    fixture.update(pick=winner['team'], method='research_vrs_single', probabilities=None, fair_odds=None,
                   reason=('No verified market line. Research pick only: %s is #%d in Valve\'s official global standings of %s (%d points) while %s does not appear in that %d-team file at all. '
                           'One-sided standings evidence, not a market probability, and no percentage is published.'
                           % (winner['team'], winner['standing'], standings['as_of'], winner['points'],
                              loser['team'], evidence['teams_count'])))
    fixture['flags'].append(RESEARCH_FLAG)
    attempt.update(status='resolved',
                   reason='Exactly one team resolves in Valve\'s official global standings of %s under the model identity rules; the other label is absent from that file. Pick only, no probability derived.' % standings['as_of'])
    fixture['attempts'].append(attempt)


def compare(fixture, standings, meta, lineups=None):
    """Attach the model line beside a market-priced row, for review only."""
    if fixture['probabilities'] is None or fixture.get('method') == 'model_vrs':
        return
    quote, reason = line(fixture, standings, meta, lineups)
    if quote is None:
        fixture['model_check'] = {'status': 'unavailable', 'reason': reason}
        return
    # Only reproducible values are stored; the gap to the market is derived at
    # render time, so a later change to the market line can never leave it stale.
    fixture['model_check'] = {'status': 'ok', 'probabilities': quote['probabilities'], 'points': quote['points'],
        'vrs_teams': quote['vrs_teams'], 'standings': quote['standings'], 'standings_as_of': quote['standings_as_of'],
        'source': quote['url'], 'identity_sources': quote['identity_sources'], 'roster_checks': quote['roster_checks']}


def gap(fixture):
    """(model minus market for the first team, same favourite?) or None."""
    check = fixture.get('model_check') or {}
    if check.get('status') != 'ok' or fixture.get('probabilities') is None:
        return None
    market, model = fixture['probabilities'][0], check['probabilities'][0]
    same = abs(market - .5) < 1e-9 or abs(model - .5) < 1e-9 or (model > .5) == (market > .5)
    return model - market, same


def _vendored(now):
    meta_path = VENDORED / 'meta.json'
    import json
    meta = json.loads(meta_path.read_text())
    text = (VENDORED / meta['file']).read_text()
    standings = parse(text)
    meta = dict(meta, origin='vendored copy (live fetch unavailable)', observed_at=iso(now))
    return standings, meta


def vendored(now=None):
    """The vendored official copy, with the provenance keys a quote has to carry.

    ``meta.json`` is Valve's file metadata only, so a caller that reads it directly
    and hands it to :func:`line` used to fail with a ``KeyError`` on ``observed_at``.
    This is the supported way to originate a line without a live fetch.
    """
    return _vendored(now or datetime.now(timezone.utc))


def fetch(src, now=None, token=None):
    """Latest global standings: live from GitHub, else the vendored copy.

    Returns (standings, meta, problem). ``problem`` is a string when the live
    fetch failed and the vendored copy was used, or when nothing usable exists.
    """
    now = now or datetime.now(timezone.utc)
    headers = {'Accept': 'application/vnd.github+json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    problem = None
    try:
        names = []
        for year in (now.year, now.year - 1):
            listing, _ = src.get('Valve VRS standings index %d' % year, API + '/contents/live/%d' % year, True, headers=headers)
            names = sorted((x['name'] for x in listing if FILE_RE.match(x.get('name', ''))), reverse=True)
            if names:
                break
        if not names:
            raise ValueError('No global standings file found in the official repository')
        name = names[0]
        year = FILE_RE.match(name).group(1)
        path = 'live/%s/%s' % (year, name)
        commits, _ = src.get('Valve VRS standings commit', API + '/commits?path=%s&per_page=1' % path, True, headers=headers)
        commit = commits[0]['sha']
        raw_url = '%s/%s/%s' % (RAW, commit, path)
        text, receipt = src.get('Valve VRS global standings', raw_url, False)
        standings = parse(text)
        meta = {'file': name, 'path': path, 'commit': commit, 'raw_url': raw_url,
                'blob_url': '%s/%s/%s' % (BLOB, commit, path), 'details_base': '%s/%s/live/%s/' % (BLOB, commit, year),
                'observed_at': receipt['observed_at'], 'origin': 'live official repository'}
    except (ValueError, KeyError, IndexError, TypeError) as e:
        problem = 'Live VRS fetch failed (%s); vendored official copy used.' % str(e)[:160]
        try:
            standings, meta = _vendored(now)
        except (OSError, ValueError, KeyError) as v:
            return None, None, problem + ' Vendored copy unusable: ' + str(v)[:120]
    age = (now.date() - datetime.strptime(standings['as_of'], '%Y-%m-%d').date()).days
    if age > MAX_STANDINGS_AGE_DAYS:
        return None, None, 'VRS standings of %s are %d days old; model lines withheld.' % (standings['as_of'], age)
    return standings, meta, problem
