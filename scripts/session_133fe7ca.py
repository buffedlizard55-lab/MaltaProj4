"""Session 133fe7ca: verified final-day results and the Aurora YB identity mapping.

Two additive, idempotent data updates, each with its primary source:

1. ``data/analysis.json`` - the Thunderpick World Championship 2026 final day is
   complete. HLTV's event results page and both match pages were read on
   2026-10-19 and show Aurora 2-1 Falcons (third place) and FURIA 3-2 BETBOOM
   (grand final). The pre-match Day-5 guidance block stays in place as a dated
   record, but its "TODAY" wording is replaced with past tense so the page cannot
   present an 18 October fixture as still upcoming on 19 October.
2. ``data/identities.json`` - Hotspawn labels the same club ``Aurora YB`` that
   HLTV labels ``Aurora Young Blud``. The mapping is fixture parity, not a name
   guess: Hotspawn 1082157 and HLTV 2399777 are the same Sangal fixture at the
   same 2026-10-20T12:00:00Z start, and no other club with that label appears in
   the Stake Ranked Episode 6 Closed Qualifier. The mapping lets the existing
   HLTV ranking tier emit a research pick with no probability; it never
   manufactures one.

Re-running never duplicates or rewrites a verified value.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / 'data' / 'analysis.json'
IDENTITIES = ROOT / 'data' / 'identities.json'
REVIEW = ROOT / 'data' / 'review-notes.json'
RECEIPTS = ROOT / 'data' / 'book-receipts.json'

RESULTS_URL = 'https://www.hltv.org/results?event=8932'
AURORA_FALCONS = 'https://www.hltv.org/matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026'
FURIA_BETBOOM = 'https://www.hltv.org/matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026'
HLTV_SANGAL_AURORA = 'https://www.hltv.org/matches/2399777/sangal-vs-aurora-young-blud-stake-ranked-episode-6-closed-qualifier'
HOTSPAWN_SANGAL_AURORA = 'https://www.hotspawn.com/matches/sangal-vs-aurora-yb-stake-ranked-episode-6-closed-qualifier-1082157'
HLTV_STANDINGS = 'https://www.hltv.org/ranking/teams'

DAY_FIVE_RESULTS = {
    'date': '2026-10-18',
    'label': 'Day five · 18 October 2026 · final day',
    'key': 'day-five-results',
    'results_url': RESULTS_URL,
    'note': ('Series and map scores re-read from the two HLTV match pages on 19 October 2026 (UTC). '
             'The event results page marks the tournament finished. Pick outcomes are compared with the '
             'board pick that was published before lock, not with a later line.'),
    'matches': [
        {
            'winner': 'Aurora',
            'loser': 'Falcons',
            'score': '2-1',
            'maps': 'Anubis 8-13, Dust2 19-17, Nuke 13-9',
            'stage': 'Third-place decider (BO3)',
            'match_url': AURORA_FALCONS,
            'report_url': RESULTS_URL,
            'detail': ('Veto: Aurora removed Ancient, Falcons removed Cache, Aurora picked Anubis (lost 8-13), '
                       'Falcons picked Dust2 (lost 17-19 after overtime), Nuke was left over (Aurora won 13-9). '
                       'The pre-lock board pick was Falcons at 60.5% from the Polymarket exchange line; that pick lost. '
                       'Dust2 halves 8:4, 4:8, overtime 7:5; Nuke halves 5:7, 8:2.'),
            'flag': ('The match page displays a local clock time; the date and event are verified on the page and '
                     'the series is listed under 18 October on the event results page. No start time is inferred here.'),
        },
        {
            'winner': 'FURIA',
            'loser': 'BETBOOM',
            'score': '3-2',
            'maps': 'Dust2 13-6, Ancient 16-19, Nuke 9-13, Mirage 13-11, Cache 13-6',
            'stage': 'Grand final (BO5)',
            'match_url': FURIA_BETBOOM,
            'report_url': RESULTS_URL,
            'detail': ('Veto: FURIA removed Anubis, BETBOOM removed Inferno, FURIA picked Dust2 (won 13-6), '
                       'BETBOOM picked Ancient (won 19-16 after overtime), FURIA picked Nuke (lost 9-13), '
                       'BETBOOM picked Mirage (lost 11-13), Cache was left over (FURIA won 13-6). '
                       'The pre-lock board pick was FURIA at 70.5% from the Polymarket exchange line; that pick won. '
                       'This was the event\'s only best-of-five series.'),
            'flag': ('Map scores are transcribed from the match page and were not independently re-read a second '
                     'time; the series score 3-2 is also shown on the event results page.'),
        },
    ],
    'pick_outcomes': {
        'label': 'Pre-lock board picks on the final day',
        'summary': ('One of two final-day board picks won: FURIA (70.5%) beat BETBOOM 3-2, while Falcons (60.5%) '
                    'lost the third-place decider 1-2 to Aurora. A 1-1 split is a single-day observation, not a '
                    'calibrated accuracy claim and not evidence that the market or model is right or wrong.'),
        'rows': [
            {'match': 'Aurora 2-1 Falcons', 'board_pick': 'Falcons', 'board_probability': 60.5, 'result': 'lost'},
            {'match': 'FURIA 3-2 BETBOOM', 'board_pick': 'FURIA', 'board_probability': 70.5, 'result': 'won'},
        ],
        'sources': [
            {'label': 'HLTV final-day results', 'url': RESULTS_URL},
            {'label': 'HLTV Aurora–Falcons match page', 'url': AURORA_FALCONS},
            {'label': 'HLTV FURIA–BETBOOM match page', 'url': FURIA_BETBOOM},
        ],
    },
}

AURORA_YB_ALIAS = {
    'canonical': 'Aurora Young Blud',
    'names': ['Aurora Young Blud', 'Aurora YB'],
    'source': HLTV_SANGAL_AURORA,
    'additional_source': HOTSPAWN_SANGAL_AURORA,
    'basis': ('Fixture parity for one abbreviated label, the same basis as the WROTBERRY and Hacha entries. '
              'Hotspawn row 1082157 lists Sangal vs Aurora YB in the Stake Ranked Episode 6 Closed Qualifier at '
              '2026-10-20T12:00:00Z (lock 11:54Z). HLTV match 2399777 lists Sangal vs Aurora Young Blud in the '
              'same competition with the same opponent pair. Hotspawn and both book listings give 12:00Z; the HLTV '
              'page renders its clock in the reader\'s local timezone, and Liquipedia lists this bracket match '
              'at 08:00 EDT, which is 12:00Z. Both labels name the same single round-of-16 slot, differing only '
              'by the abbreviated club suffix. This is the academy/junior club, not the main Aurora roster; the '
              'register entry is separate and the alias map only joins "Aurora YB" to "Aurora Young Blud". '
              'No roster-continuity or result inference. Exact opponent pair and UTC start are still required '
              'before any price or ranking evidence is used.'),
}

BOOK_RECEIPT = {
    'provider': 'EGamersWorld book listing',
    'id': 'egw-41yaj8BdVx-sangal-aurora-young-blud',
    'fixture_id': '1082157',
    'source_teams': ['Sangal', 'Aurora Young Blud'],
    'team_aliases': [['Sangal'], ['Aurora Young Blud', 'Aurora YB']],
    'alias_sources': [HLTV_SANGAL_AURORA, HOTSPAWN_SANGAL_AURORA],
    'start': '2026-10-20T12:00:00Z',
    'best_of': 3,
    'odds': [1.08, 6.28],
    'observed_at': '2026-10-19T04:12:00Z',
    'url': 'https://egamersworld.com/counterstrike/match/41yaj8BdVx/sangal-vs-aurora-young-blud-t529SG6szs',
    'api_url': 'https://egamersworld.com/counterstrike/match/41yaj8BdVx/sangal-vs-aurora-young-blud-t529SG6szs',
    'event': 'Stake Ranked Episode 6 Closed Qualifier',
    'identity_evidence': [
        {'label': 'Hotspawn row 1082157: Sangal vs Aurora YB, 20 October 2026 12:00, Stake Ranked Episode 6 Closed Qualifier.',
         'url': HOTSPAWN_SANGAL_AURORA},
        {'label': 'HLTV match 2399777: Sangal vs Aurora Young Blud, 20 October 2026, same competition, best of 3, round of 16.',
         'url': HLTV_SANGAL_AURORA},
        {'label': 'EGamersWorld header row: Sangal 1.08 / Aurora Young Blud 6.28, 20.10.26 14:00 (listing local display; 12:00Z), Bo3.',
         'url': 'https://egamersworld.com/counterstrike/match/41yaj8BdVx/sangal-vs-aurora-young-blud-t529SG6szs'},
    ],
    'corroboration': [
        {'label': 'Independent Russian book listing: P1 1.08 / P2 6.51, 20 October 15:00 Moscow (12:00Z).',
         'url': 'https://kushvsporte.ru/event/6983768-sangal-esports-aurora-young-blud'},
        {'label': 'The two listings differ by less than one point after de-vig: 85.33% vs 85.77% for Sangal.',
         'url': 'https://kushvsporte.ru/event/6983768-sangal-esports-aurora-young-blud'},
    ],
    'limitation': ('Aggregator listing of bookmaker odds: the underlying books are not named and no price-update '
                   'timestamp is supplied, so the 2026-10-19T04:12Z observation is what ages out under the standard '
                   'eight-hour window. After that window this row falls back to the sourced HLTV research pick with '
                   'no probability. EGamersWorld refuses the project automated runner with HTTP 403, so this is a '
                   'manual dated read, not a self-refreshing line.'),
}

REVIEW_NOTE = {
    'id': 'aurora-yb-alias-133fe7ca',
    'status': 'Needs review — fixture-parity alias',
    'finding': ('Hotspawn displays "Aurora YB" where HLTV displays "Aurora Young Blud". The register now maps '
                'the two labels for exact fixtures only, on fixture parity: the same Sangal opponent and the same '
                '2026-10-20T12:00:00Z start, in a 16-team event with one slot for that club. No primary statement '
                'was found that says "Aurora YB is the official short name of Aurora Young Blud", so the mapping '
                'remains visible here for manual review. It enables the HLTV ranking tier to pick Sangal (world '
                '#45) over the unranked opponent with no percentage; it is not a market price or a probability.'),
    'sources': [
        {'label': 'Hotspawn fixture (Sangal vs Aurora YB, row 1082157)', 'url': HOTSPAWN_SANGAL_AURORA},
        {'label': 'HLTV fixture (Sangal vs Aurora Young Blud, 12:00Z)', 'url': HLTV_SANGAL_AURORA},
        {'label': 'HLTV world ranking (Sangal #45; Aurora Young Blud unranked on its fixture page)', 'url': HLTV_STANDINGS},
    ],
}


def apply_analysis() -> bool:
    doc = json.loads(ANALYSIS.read_text())
    changed = False
    if doc.get('day_five_results') != DAY_FIVE_RESULTS:
        doc['day_five_results'] = DAY_FIVE_RESULTS
        changed = True
    guide = doc.get('day_five_guidance')
    if isinstance(guide, dict):
        updates = {
            'date': 'Day 5 · Sunday 18 October 2026 · pre-match record, lines read 18 October 00:55 UTC',
            'archived': True,
            'card': ('Final day is complete: Aurora beat Falcons 2-1 in the third-place decider and FURIA beat '
                     'BETBOOM 3-2 in the grand final. The pre-lock board picks were Falcons 60.5% (lost) and '
                     'FURIA 70.5% (won). Open the final results for the verified scores.'),
            'summary': ('This block is the dated pre-match record for Sunday 18 October, not a live guide. '
                        'FURIA–BETBOOM (15:00 UTC, BO5) and Aurora–Falcons (11:30 UTC, BO3) were priced from '
                        'validated Polymarket exchange lines at FURIA 70.5% and Falcons 60.5%; the Thunderpick '
                        'single-book cross-check read 68.24% and 61.54% at 00:55Z. The event is now complete: '
                        'Aurora won the third-place decider 2-1 and FURIA won the grand final 3-2. The percentages '
                        'below are historical observations, not current picks, and Hotspawn crowd votes were never used.'),
        }
        for key, value in updates.items():
            if guide.get(key) != value:
                guide[key] = value
                changed = True
    if doc.get('reviewed_at') != '2026-10-19':
        doc['reviewed_at'] = '2026-10-19'
        changed = True
    if doc.get('reviewed_at_utc') != '2026-10-19T04:20:00Z':
        doc['reviewed_at_utc'] = '2026-10-19T04:20:00Z'
        changed = True
    if changed:
        ANALYSIS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')
    return changed


def apply_alias() -> bool:
    doc = json.loads(IDENTITIES.read_text())
    aliases = doc.setdefault('aliases', [])
    existing = next((item for item in aliases if item.get('canonical') == AURORA_YB_ALIAS['canonical']), None)
    if existing is None:
        aliases.append(AURORA_YB_ALIAS)
        changed = True
    elif existing != AURORA_YB_ALIAS:
        existing.clear()
        existing.update(AURORA_YB_ALIAS)
        changed = True
    else:
        changed = False
    if doc.get('reviewed_at') != '2026-10-19':
        doc['reviewed_at'] = '2026-10-19'
        changed = True
    if changed:
        IDENTITIES.write_text(json.dumps(doc, indent=2, ensure_ascii=True) + '\n')
    return changed


def apply_review_note() -> bool:
    doc = json.loads(REVIEW.read_text())
    if any(item.get('id') == REVIEW_NOTE['id'] for item in doc):
        return False
    doc.append(REVIEW_NOTE)
    REVIEW.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')
    return True


def apply_book_receipt() -> bool:
    doc = json.loads(RECEIPTS.read_text())
    if any(item.get('id') == BOOK_RECEIPT['id'] for item in doc.get('receipts', [])):
        return False
    doc.setdefault('receipts', []).append(BOOK_RECEIPT)
    doc['collected_by'] = 'sessions 2e920ea8, bca04a82, 03befae8, 85c33bf9, 133fe7ca'
    doc['collected_at'] = '2026-10-19T04:12:00Z'
    RECEIPTS.write_text(json.dumps(doc, indent=1, ensure_ascii=True) + '\n')
    return True


def main() -> int:
    print('analysis.json updated:', apply_analysis())
    print('identities.json updated:', apply_alias())
    print('review-notes.json updated:', apply_review_note())
    print('book-receipts.json updated:', apply_book_receipt())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
