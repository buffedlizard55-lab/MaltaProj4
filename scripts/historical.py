"""Research picks for feed rows that are not open.

The requirement is a pick for *every* CS2 match the Hotspawn feed returns. Two
independent audits in this repository forbid the obvious implementation:

* ``scripts/audit_9b97d585.py`` — "not-open row carries an actionable value"
* ``scripts/audit_cecfe864.py`` — "not_open {id}: carries live pick/probability
  fields"

Both are correct and are kept. A row whose own sourced ``lock``/``start`` has
passed must never publish a *current* recommendation in ``pick``,
``probabilities``, ``fair_odds`` or ``method``, because a visitor reading the
board on a phone cannot tell a live pick from a four-month-old one.

So the resolved value for those rows lives in a separate, explicitly labelled
``historical`` block. It is produced by exactly the same originated-line ladder
the open rows use — Valve's official standings through Valve's own published
formula and calibration — and it is re-derivable offline from the snapshot plus
the vendored copy of Valve's file, which is what ``scripts.validate`` checks.

Tiers, in order, per row:

1. ``model_vrs`` — both teams resolve in Valve's official global standings, so
   the originated Glicko line applies and a win probability is published.
2. ``research_vrs_single`` — exactly one team resolves and the other label is
   genuinely absent from that file. A pick, **no percentage**: one input of the
   formula does not exist, so no number is invented.
3. ``unresolved`` — neither side is usable. No pick, and the exact reason per
   team plus every attempt is retained instead of a guess.

Nothing here is a current recommendation and nothing is a market price.
"""
import copy
from datetime import datetime, timezone

from scripts import vrs
from scripts import vrs_history
from scripts.core import iso, plain_name

SCHEMA_VERSION = 1

LABELS = {
    'model_vrs': 'Past fixture · our VRS model line (not a current pick)',
    'research_vrs_single': 'Past fixture · research pick, one Valve listing (no percentage)',
    'research_vrs_invariant': 'Past fixture · research pick, direction holds for every listed roster (no percentage)',
    'unresolved': 'Past fixture · unresolved (no supportable pick)',
}

# Published verbatim on the executive summary and the unresolved page. Every
# entry names a measured cause, not a general disclaimer.
LIMITATIONS = [
    'These rows are past fixtures. Hotspawn\'s own sourced lock and start times for '
    'them are before this snapshot\'s observation clock, so no current recommendation '
    'is published for them: the live pick, probability, fair line and method fields '
    'stay blank and two repository audits enforce that.',
    'No betting market prices them. Every exchange and bookmaker line this project '
    'collects is a pre-match price; a market on a match that has already started or '
    'finished is closed, so no percentage in this section comes from a book. '
    'Polymarket, Pinnacle, Thunderpick (bo3.gg) and GG.BET were all checked for the '
    'current board and none carries a two-way line for a fixture whose lock has passed.',
    'Probabilities here are our own originated line: Valve\'s official global '
    'standings points through Valve\'s own published expected-win formula and '
    'calibration slope. That is a model estimate of relative team strength from a '
    'monthly ranking file, not an observed result and not a market price.',
    'Each row is priced from the newest official Valve standings file published on or '
    'before that fixture\'s own sourced start, not from the current file. Measured on '
    '2026-10-24: the 2026-10-05 file repeats the label "Johnny Speeds" for two '
    'different rosters (#99 bsover/draken/hampus/Rack/Svedjehed and #164 '
    'HEAP/jocab/Lekr0/nawwk/titulus), while the 2026-06-01 file that was current for '
    'the June fixtures lists it once. Using the wrong-dated file would attach the '
    'wrong roster to a June fixture, so the date cut is part of the method.',
    'A monthly standings file cannot resolve a club that entered the ranking after it '
    'was cut, or a label the file repeats for an older roster with no current lineup '
    'available to tell the rosters apart. Those rows publish no percentage.',
    'Where exactly one of the two teams resolves, the pick is the listed team and no '
    'percentage is derived, because one input of the two-team formula does not exist.',
    'Where neither team resolves, no pick is published at all. The row stays in the '
    'unresolved section with the reason per team; it is never filled with 50/50.',
    'A current HLTV roster is deliberately not used to disambiguate a repeated Valve '
    'label on these rows. For the June fixtures the club that plays today is often the '
    'other of the two listed rosters, so an anchor built from today\'s lineup would '
    'select the wrong row. The anchor mechanism in data/vrs-anchors.json is reserved '
    'for open fixtures, where the current lineup is the relevant one.',
    'Rosters still change inside a month. Even the correctly dated file may list a '
    'roster that differs from the five who actually played, so these lines are '
    'strength comparisons between clubs, not reconstructions of a played match.',
]


def _attempt(provider, status, reason, url):
    return {'provider': provider, 'status': status, 'reason': reason, 'url': url}


def _one_sided(fixture, standings, meta, lineups=None):
    """Apply ``vrs.research_single``'s exact guards without touching live fields.

    ``vrs.research_single`` writes ``pick``/``method`` on the fixture and refuses
    to run on a row that is not open, so it cannot be reused directly here. Its
    conditions are reproduced one for one and each rejection reason is kept, so
    an unresolved row says precisely which guard stopped it.
    """
    evidence = vrs.research_resolution(fixture, standings, meta, lineups)
    resolved = evidence['resolved_vrs']
    listed = [r for r in resolved if r['status'] == 'listed']
    url = meta['blob_url'] if meta else vrs.BLOB
    if len(listed) != 1:
        return evidence, None, '%d of the two teams resolve in the Valve global standings, not exactly one' % len(listed)
    winner = listed[0]
    loser = next(r for r in resolved if r is not winner)
    if loser['status'] != 'absent':
        return evidence, None, ('%s is named in the standings but cannot be resolved (%s), so it is not treated as absent'
                                % (loser['team'], loser['note']))
    if (plain_name(winner['vrs_name']) != plain_name(winner['team'])
            and not vrs.identities_used(winner['team'], winner['vrs_name'])):
        return evidence, None, ('the listed label %s differs from the fixture label with no registered identity source'
                                % winner['vrs_name'])
    context = fixture.get('hltv_context') or {}
    for row in context.get('ranks', []):
        from scripts.core import norm
        if norm(row.get('team') or '') == norm(loser['team']) and row.get('vrs_rank_on_hltv'):
            return evidence, None, ('HLTV already displays VRS rank #%d for %s, so absence from the %s file is not '
                                    'treated as unlisted' % (row['vrs_rank_on_hltv'], loser['team'], standings['as_of']))
    reason = ('No verified market line exists for a match whose lock has passed. Research pick only: %s is #%d in '
              'Valve\'s official global standings of %s (%d points) while %s does not appear in that %d-team file at '
              'all. One-sided standings evidence, not a market probability, and no percentage is published.'
              % (winner['team'], winner['standing'], standings['as_of'], winner['points'],
                 loser['team'], evidence['teams_count']))
    return evidence, winner['team'], reason


def _invariant(fixture, standings, meta, lineups=None):
    """A pick that survives the opponent's roster ambiguity, or None.

    Valve's standings sometimes carry the same label twice for two different
    rosters, and with no current lineup available ``vrs.identify`` correctly
    refuses to choose between them. That blocks a probability — the two rows
    have different points — but it does not always block a *direction*: if the
    same team wins the originated line against **every** listed candidate, the
    pick does not depend on which roster the fixture meant.

    Measured on the 2026-06-01 file for Hotspawn fixture 1052748: Inner Circle
    Academy (#152, 872 points) beats both sAw rows (#208, 734 and #250, 656),
    so the pick is Inner Circle Academy whichever sAw roster played. For
    fixture 1051339 the same test flips — Infinite at #48 (1269) beats Acend
    (#61, 1200) while Infinite at #287 (586) loses to it — so no pick is
    published and the row stays unresolved. No probability is published in
    either case, because the candidates genuinely disagree about it.
    """
    from scripts.core import norm
    lineups = lineups or {}
    candidates = []
    unique_index = None
    ambiguous_index = None
    for index, team in enumerate(fixture['teams']):
        lineup = next((v for k, v in lineups.items() if k and norm(k) == norm(team)), None)
        hits = [row for row in standings['teams'] if norm(row['name']) == norm(team)]
        if lineup or not hits:
            return None, 'roster ambiguity is not the blocker for %s' % team
        if len(hits) == 1:
            if unique_index is not None:
                return None, 'both teams resolve uniquely, so the model tier should have priced this row'
            unique_index = index
        else:
            if ambiguous_index is not None:
                return None, 'both labels appear more than once in the standings'
            ambiguous_index = index
            candidates = hits
    if unique_index is None or ambiguous_index is None:
        return None, 'expected exactly one unique label and exactly one repeated label'
    anchor = next(row for row in standings['teams'] if norm(row['name']) == norm(fixture['teams'][unique_index]))
    spread = []
    for candidate in candidates:
        if unique_index == 0:
            raw = vrs.expected(anchor['points'], candidate['points'])
        else:
            raw = 1 - vrs.expected(candidate['points'], anchor['points'])
        spread.append({
            'vrs_team': candidate['name'],
            'standing': candidate['standing'],
            'points': candidate['points'],
            'roster': candidate['roster'],
            'details_url': meta['details_base'] + candidate['details'],
            'probability_for_unique_side': vrs.calibrated(raw),
        })
    favourites = {unique_index if row['probability_for_unique_side'] > 0.5 else ambiguous_index for row in spread}
    if len(favourites) != 1:
        return None, ('the favourite flips between the %d rosters Valve lists under the label %s, so no direction is '
                      'publishable' % (len(spread), fixture['teams'][ambiguous_index]))
    winner_index = favourites.pop()
    winner = fixture['teams'][winner_index]
    return {
        'pick': winner,
        'unique_side': fixture['teams'][unique_index],
        'unique_row': {'vrs_team': anchor['name'], 'standing': anchor['standing'], 'points': anchor['points'],
                       'roster': anchor['roster'], 'details_url': meta['details_base'] + anchor['details']},
        'ambiguous_label': fixture['teams'][ambiguous_index],
        'candidates': spread,
    }, None


def resolve_row(match, standings, meta, lineups=None):
    """The historical block for one non-open row. Never touches live fields."""
    fixture = {'teams': list(match['teams']), 'hltv_context': match.get('hltv_context')}
    attempts = []
    quote, why = vrs.line(fixture, standings, meta, lineups)
    provenance = {
        'standings_as_of': standings['as_of'],
        'standings_file': meta['file'],
        'standings_commit': meta.get('commit'),
        'standings_teams': len(standings['teams']),
        'source': meta['blob_url'],
        'raw_url': meta['raw_url'],
        'sha256': meta.get('sha256'),
        'origin': meta.get('origin'),
    }
    if quote is not None:
        p = quote['probabilities']
        pick = None if abs(p[0] - p[1]) < 1e-4 else match['teams'][0 if p[0] > p[1] else 1]
        attempts.append(_attempt('Valve VRS model', 'resolved',
                                 'Originated line from both teams\' Valve standings points (%s).' % standings['as_of'],
                                 meta['blob_url'] if meta else vrs.BLOB))
        flags = [vrs.MODEL_FLAG, 'Past fixture: this is a research reconstruction, not a current recommendation.']
        if any(c['overlap'] is None for c in quote['roster_checks']):
            flags.append('VRS roster continuity not checked for at least one team (no HLTV lineup available).')
        block = {
            'schema_version': SCHEMA_VERSION,
            'status': 'model_vrs',
            'label': LABELS['model_vrs'],
            'pick': pick,
            'probabilities': p,
            'fair_odds': [1 / x for x in p] if pick else None,
            'evidence': [quote],
            'resolution': vrs.research_resolution(fixture, standings, meta, lineups),
            'attempts': attempts,
            'flags': flags,
            'not_a_current_pick': True,
            'reason': ('No current recommendation: this row\'s own sourced lock/start has passed. Reconstruction from '
                       'both teams\' Valve standings points (%s), published for completeness of the inventory.'
                       % standings['as_of']) if pick else
                      ('No current recommendation: this row\'s own sourced lock/start has passed, and the originated '
                       'model line is exactly level, so there is no directional edge to publish.'),
        }
        block.update(provenance)
        return block
    attempts.append(_attempt('Valve VRS model', 'unresolved', 'No originated line: ' + why + '.',
                             meta['blob_url'] if meta else vrs.BLOB))
    evidence, pick, reason = _one_sided(fixture, standings, meta, lineups)
    if pick is not None:
        attempts.append(_attempt('Valve VRS research', 'resolved',
                                 'Exactly one team resolves in Valve\'s official global standings of %s under the model '
                                 'identity rules; the other label is absent from that file. Pick only, no probability '
                                 'derived.' % standings['as_of'],
                                 meta['blob_url'] if meta else vrs.BLOB))
        block = {
            'schema_version': SCHEMA_VERSION,
            'status': 'research_vrs_single',
            'label': LABELS['research_vrs_single'],
            'pick': pick,
            'probabilities': None,
            'fair_odds': None,
            'evidence': [],
            'resolution': evidence,
            'attempts': attempts,
            'flags': [vrs.RESEARCH_FLAG,
                      'Past fixture: this is a research reconstruction, not a current recommendation.'],
            'not_a_current_pick': True,
            'reason': reason,
        }
        block.update(provenance)
        return block
    attempts.append(_attempt('Valve VRS research', 'unresolved',
                             'No one-sided Valve standings pick: ' + reason + '. No pick invented, and no probability '
                             'derived from a single points value.',
                             meta['blob_url'] if meta else vrs.BLOB))
    invariant, why_not = _invariant(fixture, standings, meta, lineups)
    if invariant is not None:
        span = [row['probability_for_unique_side'] for row in invariant['candidates']]
        attempts.append(_attempt('Valve VRS research (roster-invariant)', 'resolved',
                                 'The originated line favours %s against every one of the %d rosters Valve lists '
                                 'under the repeated label %s, so the direction does not depend on which roster the '
                                 'fixture meant. Pick only: the candidates disagree about the number (%.1f%% to '
                                 '%.1f%% for %s), so no single probability is published.'
                                 % (invariant['pick'], len(invariant['candidates']), invariant['ambiguous_label'],
                                    100 * min(span), 100 * max(span), invariant['unique_side']),
                                 meta['blob_url'] if meta else vrs.BLOB))
        block = {
            'schema_version': SCHEMA_VERSION,
            'status': 'research_vrs_invariant',
            'label': LABELS['research_vrs_invariant'],
            'pick': invariant['pick'],
            'probabilities': None,
            'fair_odds': None,
            'evidence': [],
            'resolution': vrs.research_resolution(fixture, standings, meta, lineups),
            'invariant': invariant,
            'attempts': attempts,
            'flags': [vrs.RESEARCH_FLAG,
                      'Roster-invariant research pick: the opponent label appears %d times in Valve\'s standings and '
                      'no lineup was available to choose between them, so no percentage is published.'
                      % len(invariant['candidates']),
                      'Past fixture: this is a research reconstruction, not a current recommendation.'],
            'not_a_current_pick': True,
            'reason': ('No verified market line exists for a match whose lock has passed, and %s appears %d times in '
                       'Valve\'s official global standings of %s with no lineup available to choose between the '
                       'rosters. The originated line favours %s against every one of those rosters '
                       '(%.1f%% to %.1f%% for %s), so the direction is published as a research pick. No single '
                       'percentage is published, because the candidates genuinely disagree about it.'
                       % (invariant['ambiguous_label'], len(invariant['candidates']), standings['as_of'],
                          invariant['pick'], 100 * min(span), 100 * max(span), invariant['unique_side'])),
        }
        block.update(provenance)
        return block
    attempts.append(_attempt('Valve VRS research (roster-invariant)', 'unresolved',
                             'No roster-invariant pick: ' + why_not + '.',
                             meta['blob_url'] if meta else vrs.BLOB))
    missing = [r for r in evidence['resolved_vrs'] if r['status'] != 'listed']
    block = {
        'schema_version': SCHEMA_VERSION,
        'status': 'unresolved',
        'label': LABELS['unresolved'],
        'pick': None,
        'probabilities': None,
        'fair_odds': None,
        'evidence': [],
        'resolution': evidence,
        'attempts': attempts,
        'flags': ['Past fixture: this is a research reconstruction, not a current recommendation.'],
        'not_a_current_pick': True,
        'reason': ('No current recommendation, and no supportable historical pick either: '
                   + '; '.join('%s — %s' % (r['team'], r['note']) for r in missing)
                   + '. Roster-invariant test: ' + why_not
                   + '. Valve\'s %d-team global standings of %s is the only line source that can price a fixture '
                     'whose lock has passed, and it does not resolve this pair. Blank, never 50/50.'
                   % (evidence['teams_count'], standings['as_of'])),
    }
    block.update(provenance)
    return block


def apply_all(data, standings=None, meta=None, now=None):
    """Resolve every non-open row in place; return the coverage summary.

    Each row is priced from the newest official Valve standings file published
    on or before that fixture's own sourced start (``scripts.vrs_history``),
    because pricing a June fixture with October points is wrong and can attach
    the wrong roster to a repeated label. ``standings``/``meta`` override that
    for a single file when a caller already holds the live copy; without either,
    the vendored dated copies are used, which is what lets ``scripts.validate``
    re-derive every number here with no network.
    """
    if standings is not None and meta is not None:
        history = [(standings, meta)]
    else:
        history = vrs_history.load()
        if not history:
            now0 = now or datetime.now(timezone.utc)
            history = [vrs.vendored(now0)]
    now = now or datetime.now(timezone.utc)
    lineups = data.get('historical_lineups') or {}
    counts = {'rows': 0, 'model_vrs': 0, 'research_vrs_single': 0, 'research_vrs_invariant': 0, 'unresolved': 0}
    files_used = {}
    unresolved = []
    for match in data['matches']:
        if match.get('state') == 'open':
            match.pop('historical', None)
            continue
        counts['rows'] += 1
        row_standings, row_meta, note = vrs_history.select(match.get('start'), history)
        block = resolve_row(match, row_standings, row_meta, lineups)
        if note:
            block['flags'].append(note)
            block['standings_note'] = note
        # The live fields stay blank; two audits in this repository require it.
        assert match.get('pick') is None and match.get('probabilities') is None
        match['historical'] = block
        counts[block['status']] += 1
        key = block['standings_file']
        files_used[key] = files_used.get(key, 0) + 1
        if block['status'] == 'unresolved':
            unresolved.append({'id': match['id'], 'teams': list(match['teams']),
                               'competition': match.get('competition'), 'start': match.get('start'),
                               'standings_as_of': block['standings_as_of'],
                               'standings_source': block['source'],
                               'reason': block['reason'],
                               'attempts': copy.deepcopy(block['attempts'])})
    resolved = counts['model_vrs'] + counts['research_vrs_single'] + counts['research_vrs_invariant']
    coverage = {
        'schema_version': SCHEMA_VERSION,
        'generated_at': iso(now),
        'standings_files': sorted(files_used),
        'standings_files_used': files_used,
        'standings_repository': vrs.OWNER_REPO,
        'formula_source': vrs.BLOB + '/' + (history[-1][1].get('commit') or 'main') + '/model/fit.js',
        'calibration_source': vrs.BLOB + '/' + (history[-1][1].get('commit') or 'main') + '/modelfit.png',
        'counts': counts,
        'resolved': resolved,
        'coverage_pct': round(100.0 * resolved / counts['rows'], 1) if counts['rows'] else None,
        'with_probability': counts['model_vrs'],
        'research_only': counts['research_vrs_single'] + counts['research_vrs_invariant'],
        'tiers': [
            {'status': 'model_vrs', 'rows': counts['model_vrs'],
             'publishes': 'pick + win probability',
             'basis': 'Both teams resolve in the Valve standings file that was current for the fixture; the originated '
                      'Glicko line applies.'},
            {'status': 'research_vrs_single', 'rows': counts['research_vrs_single'],
             'publishes': 'pick, no percentage',
             'basis': 'Exactly one team resolves and the other label is genuinely absent from that file; one input of '
                      'the two-team formula does not exist.'},
            {'status': 'research_vrs_invariant', 'rows': counts['research_vrs_invariant'],
             'publishes': 'pick, no percentage',
             'basis': 'One label resolves uniquely and the other appears more than once with no lineup to choose '
                      'between them; the originated line favours the same team against every listed roster, so the '
                      'direction is published but the number is not.'},
            {'status': 'unresolved', 'rows': counts['unresolved'],
             'publishes': 'nothing',
             'basis': 'Neither team resolves, or the favourite flips between the rosters Valve lists under a repeated '
                      'label. No pick and no number is invented.'},
        ],
        'unresolved': unresolved,
        'limitations': list(LIMITATIONS),
        'note': ('Resolved for inventory completeness only. Every row here is past its own sourced lock or start, so '
                 'none of these is a current recommendation, and none comes from a betting market: a market on a '
                 'match that has already started is closed. Each row is priced from the newest official Valve '
                 'standings file published on or before its own sourced start, through Valve\'s own published formula '
                 'and calibration.'),
    }
    data['historical_coverage'] = coverage
    return coverage


def main():
    """Refresh the historical blocks of a committed snapshot, with no network.

    ``python -m scripts.historical --data data/latest.json`` re-derives every
    non-open row from the vendored copies of Valve's dated standings files. It
    writes no probability that the same functions the validator replays cannot
    reproduce. ``--vendor`` first re-fetches Valve's published files.
    """
    import argparse
    import json
    import os
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/latest.json')
    parser.add_argument('--write', action='store_true', help='Write the snapshot back (default: report only)')
    parser.add_argument('--vendor', action='store_true', help='Re-fetch Valve\'s dated standings files first')
    args = parser.parse_args()
    vendored_problem = None
    if args.vendor:
        vendored_problem = vrs_history.fetch_history(token=os.environ.get('GITHUB_TOKEN'))
        if vendored_problem:
            print('::warning::' + vendored_problem)
    path = Path(args.data)
    data = json.loads(path.read_text())
    coverage = apply_all(data)
    if args.write:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    report = {k: coverage[k] for k in ('standings_files', 'standings_files_used', 'counts', 'resolved',
                                       'coverage_pct', 'with_probability', 'research_only')}
    report['vendoring_problem'] = vendored_problem
    report['unresolved_ids'] = [u['id'] for u in coverage['unresolved']]
    report['written'] = args.write
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
