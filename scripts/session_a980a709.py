"""Apply session a980a709's retained capture to the shared evidence registers.

Context: the 2026-10-21T12:43Z published snapshot left exactly one open
Hotspawn CS2 fixture without a pick (1082762 ex-CYBERSHOKE vs BlinkDagger,
CIS LAN Championship #9 Group C, 15:00 UTC). The automated ladder could not
price it: the exchange market is below the liquidity floor, the listing
aggregator shows the identical 1.8/1.8 placeholder, HLTV exposes no numeric
two-way line, and Valve's standings repeat the CYBERSHOKE label twice while
the fixture uses ex-CYBERSHOKE.

The capture in ``research/session-a980a709/captures.json`` records a dated
read of a named-operator odds panel (Winline 1.14 / BetBoom 7.50) for that
exact pair and UTC start. This script is the only writer:

* append the accepted reading to ``data/book-receipts.json`` so the existing
  ``bookmaker_fallback`` tier prices the row (de-vigged by
  ``scripts.core.quote_book`` exactly like every other receipt);
* append two refused readings to ``rejected_listings`` (the 1.8/1.8
  placeholder and the sub-$100 Polymarket market, with its prices retained as
  corroboration only);
* append one dated finding to ``data/review-notes.json`` for Flagged for
  Review: the cross-operator composite basis and the unmerged ex-CYBERSHOKE
  label.

Run:  python -m scripts.session_a980a709
Idempotent: receipt id, rejection fixture ids and note id are unique keys.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import book_candidate, quote_book

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / 'research/session-a980a709/captures.json'
RECEIPTS = ROOT / 'data/book-receipts.json'
NOTES = ROOT / 'data/review-notes.json'

RECEIPT_ID = 'stavka-cybershoke-blinkdagger-1082762'
NOTE_ID = 'a980a709-cybershoke-blinkdagger-composite'
PROVIDER = 'Named-operator odds panel (Winline / BetBoom via СТАВКА ТВ)'
HOTSPAWN_ROW = 'https://www.hotspawn.com/matches/ex-cybershoke-vs-blinkdagger-cis-lan-championship-9-1082762'
EGW = 'https://egamersworld.com/counterstrike/match/4yp_dlKtNl/ex-cybershoke-vs-blinkdagger-5sOoK5oHU4'
STAVKA = 'https://stavka.tv/matches/csgo/21-10-2026-cybershoke-esports-blinkdagger'
LIQUIPEDIA = 'https://liquipedia.net/counterstrike/CIS_LAN_Championship/9'
HLTV = 'https://www.hltv.org/matches/2399839/match'
POLYMARKET = 'https://polymarket.com/esports/cs2'
VALVE = ('https://github.com/ValveSoftware/counter-strike_regional_standings/blob/'
         'eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md')

LIMITATION = (
    'Cross-operator price panel: the page shows the best available price per side from two named '
    'operators (Winline 1.14 on ex-CYBERSHOKE, BetBoom 7.50 on BlinkDagger), not one bookmaker\'s own '
    'two-way line, and it exposes no price-update timestamp. The de-vig is the standard project formula '
    'applied to that pair, so the published probabilities are a market-implied estimate, not one book\'s '
    'consensus and not a multi-book average. The observation is dated and expires under the same '
    'eight-hour evidence window as every other researched listing; the scheduled refresh re-reads this '
    'URL (scripts/books.py) and renews the observation only when it re-confirms the exact pair, UTC start '
    'and an asymmetric two-way pair. An identical placeholder pair is never accepted.')


def build_receipt(capture):
    odds = [float(x) for x in capture['odds']]
    assert odds[0] != odds[1], 'identical odds are the placeholder default'
    assert all(x > 1.0 for x in odds), 'decimal prices only'
    receipt = {
        'provider': PROVIDER,
        'id': RECEIPT_ID,
        'fixture_id': '1082762',
        'source_teams': ['ex-CYBERSHOKE', 'BlinkDagger'],
        'team_aliases': [['ex-CYBERSHOKE'], ['BlinkDagger']],
        'alias_sources': [EGW, LIQUIPEDIA],
        'start': '2026-10-21T15:00:00Z',
        'best_of': 3,
        'odds': odds,
        'observed_at': '2026-10-21T12:46:00Z',
        'url': capture['url'],
        'api_url': capture['url'],
        'event': 'CIS LAN Championship #9',
        'identity_evidence': [
            {'label': 'Hotspawn board row 1082762: ex-CYBERSHOKE vs BlinkDagger, 2026-10-21T15:00:00Z',
             'url': HOTSPAWN_ROW},
            {'label': 'EGamersWorld page JSON-LD startDate 2026-10-21T15:00:00.000Z with the same pair',
             'url': EGW},
            {'label': 'Liquipedia CIS LAN Championship #9: Group C opening match 21 Oct 2026 18:00 MSK '
                      '(15:00 UTC), CYBERSHOKE Esports vs BlinkDagger, Bo3, with lineups',
             'url': LIQUIPEDIA},
            {'label': 'HLTV fixture referenced by that Liquipedia page', 'url': HLTV},
        ],
        'corroboration': [
            {'label': 'Polymarket lists CYBERSHOKE Esports vs BlinkDagger (BO3) CIS LAN Championship '
                      'Group C at 1.16 / 5.00 with $10 volume - same favourite, but below the $100 '
                      'liquidity floor, so it is never used as the quote',
             'url': POLYMARKET},
        ],
        'limitation': LIMITATION,
        'session_note': ('Accepted only because every other tier declined this fixture: exchange liquidity '
                         'floor, 1.8/1.8 placeholder, no numeric HLTV line, duplicated Valve label. The '
                         'pair is asymmetric, the exact opponent pair and UTC start are verified against '
                         'three independent pages, and the row is flagged for review.'),
    }
    # Replay the same checks the published row will be replayed with.
    candidate = book_candidate(receipt)
    quote = quote_book(candidate, [0, 1], datetime(2026, 10, 21, 12, 50, tzinfo=timezone.utc))
    assert abs(sum(quote['probabilities']) - 1) < 1e-9
    return receipt, quote['probabilities']


def rejections():
    return [
        {
            'fixture_id': '1082762',
            'teams': ['ex-CYBERSHOKE', 'BlinkDagger'],
            'url': EGW,
            'observed_at': '2026-10-21T12:45:00Z',
            'displayed': [1.8, 1.8],
            'reason': ('Identical 1.8/1.8 default odds on both sides: a listing placeholder, never a '
                       '50/50. The same page confirms the pair and the 15:00 UTC start, but supplies no '
                       'usable price.'),
        },
        {
            'fixture_id': '1082762',
            'teams': ['ex-CYBERSHOKE', 'BlinkDagger'],
            'url': POLYMARKET,
            'observed_at': '2026-10-21T12:46:00Z',
            'displayed': [1.16, 5.0],
            'reason': ('Polymarket market "CYBERSHOKE Esports vs BlinkDagger (BO3) - CIS LAN Championship '
                       'Group C" shows $10 volume, below the project\'s $100 liquidity floor. The prices '
                       'are retained as corroboration only; no probability is derived from this market.'),
        },
    ]


def note():
    return {
        'id': NOTE_ID,
        'status': 'Needs review - cross-operator price panel published for one previously unresolved fixture',
        'finding': (
            'Fixture 1082762 (ex-CYBERSHOKE vs BlinkDagger, CIS LAN Championship #9 Group C, 21 Oct '
            '15:00 UTC) was the only open Hotspawn CS2 match without a pick on the 2026-10-21T12:43Z '
            'snapshot. Every automated tier declined it: Polymarket shows 1.16 / 5.00 with $10 volume '
            '(below the $100 floor); the EGamersWorld listing shows the identical 1.8/1.8 placeholder; '
            'HLTV exposes no numeric two-way line and its fan vote is excluded by policy; and Valve\'s '
            'official standings label two different rosters CYBERSHOKE (#61 and #171) while the fixture '
            'uses ex-CYBERSHOKE, so neither the model nor the one-sided standings tier will guess. The '
            'named-operator panel on the СТАВКА ТВ match page shows Winline 1.14 on ex-CYBERSHOKE and '
            'BetBoom 7.50 on BlinkDagger for the exact pair and event, which de-vigs to roughly 86.8% / '
            '13.2% in ex-CYBERSHOKE\'s favour. That is the best available price per side from two '
            'operators rather than one book\'s own two-way line, so it is published as a labelled, dated '
            'market-implied estimate and flagged here. No team-name alias was registered between '
            'ex-CYBERSHOKE and Valve\'s CYBERSHOKE label in this session; the duplicate-label conflict is '
            'left visible for review.'),
        'sources': [
            {'url': STAVKA, 'label': 'СТАВКА ТВ match page - Winline 1.14 / BetBoom 7.50 panel (observed 2026-10-21 12:46 UTC)'},
            {'url': EGW, 'label': 'EGamersWorld listing - 1.8/1.8 placeholder, JSON-LD start 15:00 UTC'},
            {'url': LIQUIPEDIA, 'label': 'Liquipedia CIS LAN Championship #9 - 18:00 MSK (15:00 UTC) Group C fixture and lineups'},
            {'url': HLTV, 'label': 'HLTV fixture page (identity only, no numeric line)'},
            {'url': POLYMARKET, 'label': 'Polymarket CS2 page - CYBERSHOKE Esports vs BlinkDagger, $10 volume'},
            {'url': VALVE, 'label': 'Valve official global standings 2026-10-05 - two CYBERSHOKE rows, no ex-CYBERSHOKE or BlinkDagger row'},
            {'url': HOTSPAWN_ROW, 'label': 'Hotspawn fixture page for row 1082762'},
        ],
    }


def write_intent(intent):
    print(json.dumps(intent, indent=1, ensure_ascii=False))


def main():
    captures = json.loads(CAPTURES.read_text())
    capture = next(c for c in captures['captures'] if c['decision'] == 'accepted_receipt')
    receipt, probabilities = build_receipt(capture)

    doc = json.loads(RECEIPTS.read_text())
    added_receipt = added_rejections = 0
    if not any(r['id'] == RECEIPT_ID for r in doc['receipts']):
        doc['receipts'].append(receipt)
        added_receipt = 1
    seen = {(str(r.get('fixture_id')), str(r.get('url'))) for r in doc['rejected_listings']}
    for rejection in rejections():
        key = (str(rejection['fixture_id']), str(rejection['url']))
        if key not in seen:
            doc['rejected_listings'].append(rejection)
            seen.add(key)
            added_rejections += 1
    RECEIPTS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')

    notes = json.loads(NOTES.read_text())
    added_notes = 0
    if not any(n['id'] == NOTE_ID for n in notes):
        notes.append(note())
        added_notes = 1
    NOTES.write_text(json.dumps(notes, indent=1, ensure_ascii=False) + '\n')

    write_intent({'receipts_added': added_receipt, 'rejections_added': added_rejections,
                  'notes_added': added_notes,
                  'probabilities': [round(p, 6) for p in probabilities],
                  'de_vigged': 'ex-CYBERSHOKE %.4f / BlinkDagger %.4f' % tuple(probabilities)})


if __name__ == '__main__':
    main()
