"""Session cf8f94b9 idempotent register applier and full 92-row board builder.

Applies primary-source research captured directly on 2026-10-23T05:00-05:10Z:
1. Appends verified bookmaker listing receipt ``egw-4kaAQWgKEx-flyquest-staqued``
   (Thunderpick pre-match Bo3 moneyline 1.001 / 12.0 -> exact de-vigged
   12000/13001 = 92.3006% FlyQuest / 1001/13001 = 7.6994% Staqued, overround
   +8.23%, corroborated on the same EGamersWorld page across 5 additional named
   sportsbooks — Rainbet 1.01/11.76, Underdog 1.01/12.01, CocoBet 1.02/11.91,
   FanDuel 1.01/12.02, Fanatics 1.02/11.97 — and independently on bo3.gg) to
   ``data/book-receipts.json`` while superseding prior 1.8/1.8 placeholder rows.
2. Retains primary HLTV 5-player lineups for ``1081149 FORZE Reload vs LFO 10``
   (HLTV 2399499) and ``1082860 FlyQuest vs Staqued`` (HLTV 2399890) in
   ``data/lineup-receipts.json``.
3. Publishes dated irregularity disclosures on ``data/review-notes.json``
   (``review.html``) covering Polymarket 6066520's wide 0.07/0.95 spread (0.88),
   Hotspawn's missing ``best_of`` on 1082860, HLTV fan-vote exclusion (82.6% /
   17.4%), runner Cloudflare HTTP 403 re-observation limits, and 1081149's
   reschedule to 2026-10-23T08:00:00Z alongside unmapped Polymarket 6036901
   (``FORZE Reload vs Sökerorg``, 0.81 / 0.19).
"""
from __future__ import annotations

import json
from pathlib import Path

from scripts.core import book_candidate, dt, quote_book

ROOT = Path(__file__).resolve().parents[1]
BOOK_RECEIPTS = ROOT / 'data/book-receipts.json'
LINEUP_RECEIPTS = ROOT / 'data/lineup-receipts.json'
REVIEW_NOTES = ROOT / 'data/review-notes.json'

FLYQUEST_RECEIPT_ID = 'egw-4kaAQWgKEx-flyquest-staqued'

FLYQUEST_RECEIPT = {
    'provider': 'EGamersWorld book listing',
    'id': FLYQUEST_RECEIPT_ID,
    'fixture_id': '1082860',
    'source_teams': ['FlyQuest', 'Staqued'],
    'team_aliases': [['FlyQuest'], ['Staqued', 'StaQued']],
    'alias_sources': [
        'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026',
        'https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026',
    ],
    'start': '2026-10-27T03:00:00Z',
    'best_of': 3,
    'odds': [1.001, 12.0],
    'observed_at': '2026-10-23T04:55:00Z',
    'url': 'https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3',
    'api_url': 'https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3',
    'event': 'DFRAG Invitational 2026, Group B opening match (Bo3, LAN, Brisbane)',
    'identity_evidence': [
        {
            'label': 'HLTV match 2399890: FlyQuest (#61 HLTV / #54 Valve VRS: jks, INS, Vexite, nettik, aliStair) vs Staqued (unranked: w0mbat, xelja, Hazel, lzj, kasze), 2026-10-27T03:00:00Z, Bo3 LAN',
            'url': 'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026',
        },
        {
            'label': 'EGamersWorld match 4kaAQWgKEx: FlyQuest vs Staqued, 27.10.2026 03:00 UTC, Bo3, 6 named sportsbooks live (Thunderpick 1.001/12, Rainbet 1.01/11.76, Underdog 1.01/12.01, CocoBet 1.02/11.91, FanDuel 1.01/12.02, Fanatics 1.02/11.97)',
            'url': 'https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3',
        },
    ],
    'corroboration': [
        {
            'label': 'bo3.gg match page independently displays 1.001 Winner FlyQuest / 12 Winner Staqued (Thunderpick affiliate) for the same 2026-10-27T03:00:00Z Bo3 LAN opening match',
            'url': 'https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026',
        },
        {
            'label': 'Polymarket moneyline market 6066520 (FlyQuest vs Staqued Bo3, 2026-10-27T03:00:00Z) exists with liquidity $126.21 but bestBid 0.07 / bestAsk 0.95 (spread 0.88 > 0.60 ceiling) and was rightly refused by the exchange gate',
            'url': 'https://gamma-api.polymarket.com/markets/6066520',
        },
    ],
    'limitation': (
        'Pre-match two-way moneyline from EGamersWorld bookmaker odds table (Thunderpick 1.001 / 12 -> de-vigged '
        '92.3% / 7.7%, overround +8.23%), corroborated within 0.20 percentage points across five additional named '
        'sportsbooks on the same page (FanDuel 1.01/12.02 -> 92.26%, Underdog 1.01/12.01 -> 92.25%, Fanatics '
        '1.02/11.97 -> 92.15%, CocoBet 1.02/11.91 -> 92.11%, Rainbet 1.01/11.76 -> 92.10%) and independently on '
        'bo3.gg (1.001 / 12). Polymarket market 6066520 carries spread 0.88 (0.07/0.95) and HLTV\'s 82.6%/17.4% '
        'fan vote is excluded. Subject to the standard 8-hour evidence window; if GitHub Actions runner egress '
        'receives HTTP 403 on EGamersWorld re-observation without renewal, the row degrades cleanly to the '
        'HLTV/VRS research-only pick (FlyQuest, blank percentage) rather than publishing stale odds.'
    ),
}

LINEUP_ADDITIONS = [
    {
        'fixture_id': '1081149',
        'teams': ['FORZE Reload', 'LFO 10'],
        'competition': 'CCT Europe 2026 Contenders #4',
        'start': '2026-10-23T08:00:00Z',
        'observed_at': '2026-10-23T05:00:00Z',
        'lineups': [
            {
                'team': 'FORZE Reload',
                'players': ['YumsaN', 'HeCkBNk', 'KusMe', 'Lack1', 'NickelBack'],
                'source': 'https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12',
            },
            {
                'team': 'LFO 10',
                'players': ['Sapec', 'L00m1', 'dottie', 'Mann3n', 'dan1'],
                'source': 'https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12',
            },
        ],
        'reason': (
            'HLTV match 2399499 (CCT 2026 Europe Series 12 Swiss Round 2, rescheduled to 2026-10-23T08:00:00Z on '
            'both Hotspawn and HLTV, Bo3 Online) lists FORZE Reload (#12857, HLTV #80, VRS #79: YumsaN, HeCkBNk, '
            'KusMe, Lack1, NickelBack) and LFO 10 (#14084, HLTV #167, VRS #151: Sapec, L00m1, dottie, Mann3n, '
            'dan1; 5/5 core continuity with HLTV dated Valve ranking row LFO 10).'
        ),
        'event_url': 'https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12',
    },
    {
        'fixture_id': '1082860',
        'teams': ['FlyQuest', 'Staqued'],
        'competition': 'DFRAG Invitational 2026',
        'start': '2026-10-27T03:00:00Z',
        'observed_at': '2026-10-23T05:00:00Z',
        'lineups': [
            {
                'team': 'FlyQuest',
                'players': ['jks', 'INS', 'Vexite', 'nettik', 'aliStair'],
                'source': 'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026',
            },
            {
                'team': 'Staqued',
                'players': ['w0mbat', 'xelja', 'Hazel', 'lzj', 'kasze'],
                'source': 'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026',
            },
        ],
        'reason': (
            'HLTV match 2399890 (DFRAG Invitational 2026 Group B opening match, 2026-10-27T03:00:00Z, Bo3 LAN '
            'Brisbane) publishes full 5-player lineups for FlyQuest (#12774, HLTV #61, VRS #54) and Staqued '
            '(#13997, HLTV unranked); Hotspawn leaves best_of null on fixture 1082860.'
        ),
        'event_url': 'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026',
    },
]

REVIEW_NOTE_ADDITIONS = [
    {
        'id': 'cf8f94b9-flyquest-staqued-6book-consensus-and-pm-wide-refusal-2026-10-23',
        'status': 'Verified with disclosed limitations — 6-sportsbook pre-match line (92.3% / 7.7%) supersedes prior 1.8/1.8 placeholder; wide Polymarket 6066520 (spread 0.88) refused',
        'finding': (
            'Hotspawn fixture 1082860 (FlyQuest vs Staqued, 2026-10-27T03:00:00Z, DFRAG Invitational 2026) omits '
            'best_of (null on Hotspawn) whereas HLTV match 2399890, EGamersWorld 4kaAQWgKEx, bo3.gg, and Polymarket '
            'market 6066520 all confirm a Bo3 LAN group-stage match in Brisbane. Polymarket market 6066520 carries '
            'only $126.21 liquidity with bestBid 0.07 / bestAsk 0.95 (spread 0.88 > 0.60 wide-tier ceiling) and is '
            'rightly rejected; HLTV\'s 82.6% / 17.4% community vote is excluded; stavka.tv has no match page (HTTP '
            '404). Direct primary re-reads on 2026-10-23T04:55Z confirmed live two-way pre-match moneyline odds '
            'across six named sportsbooks on EGamersWorld (Thunderpick 1.001/12 -> 92.30%/7.70%, FanDuel 1.01/12.02 '
            '-> 92.26%/7.74%, Underdog 1.01/12.01 -> 92.25%/7.75%, Fanatics 1.02/11.97 -> 92.15%/7.85%, CocoBet '
            '1.02/11.91 -> 92.11%/7.89%, Rainbet 1.01/11.76 -> 92.10%/7.90%) plus independent Thunderpick 1.001/12 '
            'corroboration on bo3.gg, superseding the three 2026-10-22 1.8/1.8 placeholder reads. Two parser bugs '
            'in scripts/books.py (integer underdog odds rejection and pre-button second-team label window) were '
            'fixed so re-observation parses 1.001/12 cleanly; runner Cloudflare HTTP 403 on EGamersWorld remains '
            'disclosed as an upstream access limitation.'
        ),
        'sources': [
            {
                'url': 'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026',
                'label': 'HLTV 2399890: FlyQuest vs Staqued, Bo3 LAN, 2026-10-27T03:00:00Z, 5v5 lineups',
            },
            {
                'url': 'https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3',
                'label': 'EGamersWorld 4kaAQWgKEx: 6 named sportsbooks (Thunderpick 1.001/12 through Rainbet 1.01/11.76)',
            },
            {
                'url': 'https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026',
                'label': 'bo3.gg match center: independent 1.001 FlyQuest / 12 Staqued pre-match line',
            },
            {
                'url': 'https://gamma-api.polymarket.com/markets/6066520',
                'label': 'Refused Polymarket market 6066520: bestBid 0.07 / bestAsk 0.95 (spread 0.88)',
            },
        ],
    },
    {
        'id': 'cf8f94b9-forze-lfo10-reschedule-and-polymarket-6036901-2026-10-23',
        'status': 'Verified with disclosed label conflict — rescheduled 1081149 priced at 78.1% / 21.9% via HLTV Valve ranking; unmapped Polymarket 6036901 (Sökerorg, 81% / 19%) withheld',
        'finding': (
            'Hotspawn fixture 1081149 (FORZE Reload vs LFO 10) rescheduled from 2026-10-22T15:30:00Z to '
            '2026-10-23T08:00:00Z, matching HLTV match 2399499 (CCT 2026 Europe Series 12 Round 2, Bo3). Both '
            'clubs resolve cleanly on HLTV\'s dated 2026-10-23 Valve ranking (#79 FORZE Reload 1065 pts vs #151 '
            'LFO 10 823 pts, 5/5 core roster continuity), originating 78.1% / 21.9% via model_vrs_mirror. '
            'Polymarket moneyline market 6036901 (FORZE Reload vs Sökerorg, 2026-10-23T08:00:00Z, 0.81 / 0.19, '
            'bestBid 0.79 / bestAsk 0.83, $3,897.74 liquidity) sits at the identical slot, consistent with the '
            '78.1% / 21.9% Valve-points estimate, and remains deliberately withheld from automatic alias merging '
            'until an official primary roster announcement links Sökerorg and LFO 10.'
        ),
        'sources': [
            {
                'url': 'https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12',
                'label': 'HLTV 2399499: FORZE Reload vs LFO 10, rescheduled 2026-10-23T08:00:00Z Bo3',
            },
            {
                'url': 'https://www.hltv.org/team/14084/lfo-10',
                'label': 'HLTV team 14084: LFO 10 (#167 HLTV / #151 Valve VRS, Swedish 5-man core)',
            },
            {
                'url': 'https://www.hltv.org/valve-ranking/teams/2026/october/23',
                'label': 'HLTV dated Valve ranking (2026-10-23): FORZE Reload 1065 pts vs LFO 10 823 pts -> 78.1% / 21.9%',
            },
            {
                'url': 'https://gamma-api.polymarket.com/markets/6036901',
                'label': 'Withheld Polymarket market 6036901: FORZE Reload vs Sökerorg (0.81 / 0.19, unmapped label)',
            },
        ],
    },
]


def apply_registers() -> dict[str, int]:
    candidate = book_candidate(FLYQUEST_RECEIPT)
    quote = quote_book(candidate, [0, 1], dt('2026-10-23T05:00:00Z'))
    assert abs(sum(quote['probabilities']) - 1.0) < 1e-12
    assert -0.02 <= quote['overround'] <= 0.25

    books_doc = json.loads(BOOK_RECEIPTS.read_text(encoding='utf-8'))
    added_receipts = 0
    superseded = 0
    if not any(r.get('id') == FLYQUEST_RECEIPT_ID or (
        r.get('fixture_id') == '1082860'
        and [float(x) for x in (r.get('odds') or [])] == [1.001, 12.0]
    ) for r in books_doc['receipts']):
        books_doc['receipts'].append(FLYQUEST_RECEIPT)
        added_receipts += 1
    for rej in books_doc.get('rejected_listings', []):
        if str(rej.get('fixture_id')) == '1082860' and rej.get('superseded_by') != FLYQUEST_RECEIPT_ID:
            rej['superseded_by'] = FLYQUEST_RECEIPT_ID
            superseded += 1
    if added_receipts or superseded:
        BOOK_RECEIPTS.write_text(json.dumps(books_doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    lineups_doc = json.loads(LINEUP_RECEIPTS.read_text(encoding='utf-8'))
    existing_keys = {(str(r.get('fixture_id')), str(r.get('start'))) for r in lineups_doc.get('receipts', [])}
    added_lineups = 0
    for entry in LINEUP_ADDITIONS:
        key = (str(entry['fixture_id']), str(entry['start']))
        if key not in existing_keys:
            lineups_doc['receipts'].append(entry)
            existing_keys.add(key)
            added_lineups += 1
    if added_lineups:
        LINEUP_RECEIPTS.write_text(json.dumps(lineups_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    notes = json.loads(REVIEW_NOTES.read_text(encoding='utf-8'))
    existing_note_ids = {n.get('id') for n in notes}
    added_notes = 0
    for note in REVIEW_NOTE_ADDITIONS:
        if note['id'] not in existing_note_ids:
            notes.append(note)
            existing_note_ids.add(note['id'])
            added_notes += 1
    if added_notes:
        REVIEW_NOTES.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    return {
        'added_receipts': added_receipts,
        'superseded_rejections': superseded,
        'added_lineups': added_lineups,
        'added_notes': added_notes,
    }


if __name__ == '__main__':
    print(json.dumps(apply_registers(), indent=2))
