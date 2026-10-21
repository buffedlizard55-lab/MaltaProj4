"""Apply session 50f79045's research for fixture 1081597 (benched gods vs TitanFlow).

The 2026-10-21T20:16Z live snapshot left one Hotspawn CS2 fixture without
a supported pick: 1081597 benched gods vs TitanFlow (CCT Europe 2026
Challengers #8, 22 Oct 2026 11:00 UTC). The automated HLTV fetch was rate-limited
(HTTP 403) in that run, so HLTV ranking context was absent and the Valve VRS
lookup only has one team's 2026-10-05 roster entry. HLTV's current Valve global
ranking page (2026/october/21) lists benched gods at #160 (791 points, roster
Wign/K014NZ/facer/norescue/yoyoS2) and TitanFlow at #234 (664 points, roster
Henma/Saiman Strit/keeisen/...). HLTV match page context confirms the fixture
identity.

This script records the evidence as one-sided ranking research (research_rank_single)
for benched gods, following the existing policy. No probability is invented.

Idempotent: fixture id 1081597 is the unique key.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / 'data/review-notes.json'

NOTE_ID = '50f79045-benched-gods-titanflow-hltv-rank'
HLTV_VRS = 'https://www.hltv.org/valve-ranking/teams/2026/october/21'
HLTV_EVENT = 'https://www.hltv.org/events/9453/cct-2026-challengers-europe-series-8'
HOTSPAWN_ROW = 'https://www.hotspawn.com/matches/benched-gods-vs-titanflow-cct-europe-2026-challengers-8-1081597'
EGAMERSWORLD = 'https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn'


def main():
    notes = json.loads(NOTES.read_text())
    items = notes['notes'] if isinstance(notes, dict) and 'notes' in notes else notes
    # Skip if already present
    if any(n.get('id') == NOTE_ID for n in items if isinstance(n, dict)):
        print('Note already present; nothing to add')
        return
    entry = {
        'id': NOTE_ID,
        'status': 'Research pick — one-sided HLTV Valve ranking',
        'finding': (
            'Fixture 1081597 (benched gods vs TitanFlow, CCT Europe 2026 Challengers #8, '
            '22 Oct 2026 11:00 UTC) was listed as unresolved in the 20:16 UTC snapshot because '
            'the HLTV context fetch returned HTTP 403 (rate-limited) and the vendored '
            '2026-10-05 Valve standings only list one roster entry for benched gods. A manual '
            'read of HLTV\'s Valve global ranking for 21 Oct 2026 shows benched gods at #160 '
            '(791 points, roster Wign/K014NZ/facer/norescue/yoyoS2) and TitanFlow at #234 '
            '(664 points). EGamersWorld shows the symmetric 1.8/1.8 placeholder pair '
            '(rejected; no named-operator odds). Polymarket and Pinnacle have no validated '
            'line. Hotspawn crowd picks (92% / 8%) are never used as probability. The row '
            'resolves as a one-sided ranking research pick for benched gods with no published '
            'percentage; the scheduled refresh will replace this with a market line or two-team '
            'VRS line if either becomes available.'
        ),
        'sources': [
            {'url': HLTV_VRS, 'label': 'HLTV Valve global ranking, 21 Oct 2026 (benched gods #160, TitanFlow #234)'},
            {'url': HLTV_EVENT, 'label': 'HLTV CCT Europe 2026 Challengers #8 event page'},
            {'url': HOTSPAWN_ROW, 'label': 'Hotspawn fixture 1081597'},
            {'url': EGAMERSWORLD, 'label': 'EGamersWorld match page (1.8/1.8 placeholder, rejected)'},
        ],
    }
    if isinstance(notes, list):
        notes.append(entry)
    elif 'notes' in notes:
        notes['notes'].append(entry)
    else:
        notes[NOTE_ID] = entry
    NOTES.write_text(json.dumps(notes, indent=1))
    print('Added note', NOTE_ID)


if __name__ == '__main__':
    main()
