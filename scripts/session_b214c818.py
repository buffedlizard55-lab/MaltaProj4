"""Apply session b214c818's retained listing captures to the shared registers.

The captures in ``research/session-b214c818/captures.json`` are verbatim live
reads of public listing/match pages made on 2026-10-19 with the Arena retrieval
tools (the runner's egress cannot reach these hosts directly). This script is
the only writer: it validates each capture's invariants (exact fixture start,
asymmetric two-way pair, de-vig margin in bounds — the same checks
``scripts.core.quote_book`` replays later) and then appends

* accepted readings to ``data/book-receipts.json`` (the ``bookmaker_fallback``
  tier prices open rows from these while they are inside the evidence window),
* refused listings to that file's ``rejected_listings`` (identical 1.8/1.8
  placeholder pairs and unbindable pairs, with the reason),
* one sourced label mapping to ``data/identities.json`` (Aurora YB →
  Aurora Young Blud), and
* the dated findings to ``data/review-notes.json`` (Flagged for Review).

Run:  python -m scripts.session_b214c818
Idempotent: a second run changes nothing (receipt ids, rejection
fixture/observation pairs and note ids are unique keys).
"""
from __future__ import annotations

import json
from pathlib import Path

from scripts.core import book_candidate, quote_book, dt, iso

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / 'research/session-b214c818/captures.json'
RECEIPTS = ROOT / 'data/book-receipts.json'
IDENTITIES = ROOT / 'data/identities.json'
NOTES = ROOT / 'data/review-notes.json'

PROVIDER = 'EGamersWorld book listing'
LIMITATION = (
    'Aggregator listing of bookmaker odds; the underlying bookmaker is not named on the header row and '
    'supplies no price-update timestamp. Observation time is shown and the standard eight-hour evidence '
    'window applies: when the observation lapses the row falls back to the next documented tier (originated '
    'VRS model line, then the research-only ranking pick) and says so. The scheduled refresh re-reads this '
    'listing URL (scripts/books.py) and renews the observation only when the page re-confirms the exact '
    'team pair, UTC start and an asymmetric two-way pair; a parse miss leaves the observation to expire.')


def build_receipt(capture):
    odds = [float(x) for x in capture['odds']]
    assert odds[0] != odds[1], capture['id'] + ': identical odds are the placeholder default'
    assert all(x > 1.0 for x in odds), capture['id'] + ': odds must be valid decimal prices'
    teams = list(capture['source_teams'])
    assert len(teams) == 2
    aliases = []
    alias_sources = []
    for team, evidence in zip(teams, capture['identity_evidence'][:2] + [None, None]):
        names = [team]
        for addition in (capture.get('label_aliases') or {}).get(team, []):
            if addition not in names:
                names.append(addition)
        aliases.append(names)
        alias_sources.append(evidence['url'] if evidence else None)
    # Map each displayed book label onto the Hotspawn fixture labels via the
    # identity register / explicit alias lists captured with the page.
    fixture_labels = {
        'Team Nemesis': 'Nemesis', 'Nuclear TigeRES': 'Nuclear TigeRES',
        'ASTRAL Esports': 'ASTRAL', 'Leo Team': 'Leo',
        'Fire Flux Esports': 'Fire Flux', 'ex-6666': 'ex-6666',
        'Lavked': 'Lavked', 'Sangal': 'Sangal',
        'Aurora Young Blud': 'Aurora YB',
    }
    for i, team in enumerate(teams):
        mapped = fixture_labels.get(team)
        if mapped and mapped not in aliases[i]:
            aliases[i].append(mapped)
    receipt = {
        'provider': PROVIDER,
        'id': capture['id'],
        'fixture_id': capture['fixture_id'],
        'source_teams': teams,
        'team_aliases': aliases,
        'alias_sources': alias_sources,
        'start': capture['jsonld_start'],
        'best_of': int(capture['format'].replace('Bo', '')),
        'odds': odds,
        'observed_at': capture['observed_at'],
        'url': capture['url'],
        'api_url': capture['url'],
        'event': capture['event'],
        'identity_evidence': capture['identity_evidence'],
        'corroboration': capture.get('corroboration') or [],
        'limitation': LIMITATION,
    }
    # Invariant gate: the exact replay the validator will run at build time.
    candidate = book_candidate(receipt)
    quote = quote_book(candidate, [0, 1], dt(capture['observed_at']))
    assert quote['probabilities'][0] + quote['probabilities'][1] == 1.0 or abs(
        sum(quote['probabilities']) - 1.0) < 1e-9
    assert -.02 <= quote['overround'] <= .25, capture['id'] + ': margin outside validation bounds'
    receipt['session_note'] = capture['decision_note']
    return receipt


def main():
    captures = json.loads(CAPTURES.read_text())
    receipts_doc = json.loads(RECEIPTS.read_text())
    identities_doc = json.loads(IDENTITIES.read_text())
    notes = json.loads(NOTES.read_text())

    added_receipts = added_rejections = added_aliases = added_notes = 0
    have_ids = {r.get('id') for r in receipts_doc['receipts']}
    have_rejects = {(r.get('fixture_id'), r.get('observed_at')) for r in receipts_doc.get('rejected_listings', [])}

    for capture in captures['accepts']:
        receipt = build_receipt(capture)
        # A parallel session may already have registered the same listing read
        # (same fixture and same pair) under its own capture id; keep the entry
        # that is already on file and never duplicate a fixture line.
        already = any(r.get('fixture_id') == receipt['fixture_id']
                      and [float(x) for x in (r.get('odds') or [])] == receipt['odds']
                      for r in receipts_doc['receipts'])
        if capture['id'] in have_ids or already:
            print('receipt =', capture['id'], '-> already on file for fixture', capture['fixture_id'])
            continue
        receipts_doc['receipts'].append(receipt)
        have_ids.add(receipt['id'])
        added_receipts += 1
        print('receipt +', receipt['id'], '->', receipt['fixture_id'], receipt['odds'])

    for capture in captures['rejects']:
        key = (capture['fixture_id'], capture['observed_at'])
        if key in have_rejects:
            continue
        receipts_doc.setdefault('rejected_listings', []).append({
            'fixture_id': capture['fixture_id'],
            'teams': capture.get('source_teams') or [capture.get('page_title', '')],
            'url': capture['url'],
            'observed_at': capture['observed_at'],
            'displayed': capture['displayed'],
            'reason': capture['decision_note'],
        })
        have_rejects.add(key)
        added_rejections += 1
        print('reject  +', capture['id'], '->', capture['fixture_id'], capture['displayed'])

    have_canonical = {a.get('canonical') for a in identities_doc['aliases']}
    for addition in captures.get('identity_additions', []):
        if addition['canonical'] in have_canonical:
            continue
        identities_doc['aliases'].append({
            'canonical': addition['canonical'],
            'names': addition['names'],
            'source': addition['source'],
            'additional_source': addition['additional_source'],
            'basis': addition['basis'],
        })
        have_canonical.add(addition['canonical'])
        added_aliases += 1
        print('alias   +', addition['canonical'], '<-', ', '.join(addition['names']))

    note_specs = [
        {
            'id': 'b214c818-default-odds-rejections',
            'status': 'Needs review — placeholder listings rejected, fallback tiers retained',
            'finding': (
                'Six open fixtures (1081130 PCIFIC–ILLYRIANS, 1079643 The Last Resort–LFO 10, 1079644 BakS–ILLYRIANS, '
                '1081862 Rare Atom–Alter Ego, 1081863 Chinggis Warriors–WXM, 1081864 NEXVOID–Vitalem Aerem) were '
                'researched on HLTV first, then on esportsbook listings. EGamersWorld lists each of them but shows '
                'only its identical placeholder pair 1.8/1.8 (no bookmaker data), and the TLR listing additionally '
                'leaves the opponent slot unnamed. Placeholder pairs are rejected — publishing one would fabricate '
                'a 50/50 — and each row keeps its next documented tier: the originated VRS model line where Valve '
                'standings resolve, or the research-only ranking pick (no percentage) where they do not. Every '
                'rejected listing is recorded in data/book-receipts.json with its URL, displayed values and reason.'),
            'sources': [
                {'url': 'https://egamersworld.com/counterstrike/match/1sGIL2gAYu/pcific-espor-vs-illyrians-GbfpHB8g8H', 'label': 'Rejected listing: PCIFIC–ILLYRIANS (1.8/1.8)'},
                {'url': 'https://egamersworld.com/counterstrike/match/_rW8GEyWK/the-last-resort-vs-xWf8Vr4Hp', 'label': 'Rejected listing: The Last Resort vs unnamed opponent (1.8/1.8)'},
                {'url': 'https://egamersworld.com/counterstrike/match/_rW8GEyWK/baks-esports-vs-illyrians-ozacJiuxA', 'label': 'Rejected listing: BakS–ILLYRIANS (1.8/1.8)'},
                {'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/rare-atom-vs-alter-ego-O8GeLuSod4', 'label': 'Rejected listing: Rare Atom–Alter Ego (1.8/1.8)'},
                {'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/chinggis-warriors-vs-wxm-_ddme1I7dZ', 'label': 'Rejected listing: Chinggis Warriors–WXM (1.8/1.8)'},
                {'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/nexvoid-vs-vitalem-aerem-LHqHITkk7x', 'label': 'Rejected listing: NEXVOID–Vitalem Aerem (1.8/1.8)'},
            ],
        },
        {
            'id': 'b214c818-rare-atom-alter-ego-conflict',
            'status': 'Needs review — secondary market quotes contradict the published model line',
            'finding': (
                'For 1081862 Rare Atom–Alter Ego (VOID Autumn Cup, 20 Oct 05:00 UTC) no verified book line exists: '
                'the EGamersWorld match page shows only the 1.8/1.8 placeholder. A search-cached EGamersWorld '
                'matches-list snippet shows an asymmetric pair (2.16/1.62) but its side ordering cannot be '
                'established from the snippet, and a Russian preview (stavka.tv, 19 Oct) quotes a different pair '
                'again (Alter Ego 1.60 / Rare Atom ≈2.20) that favours the opposite team to our originated VRS '
                'model line (Rare Atom 59.5%, from the official 5 Oct Valve standings). No line is published for '
                'this row beyond the labelled model line, nothing is averaged or guessed, and the contradiction '
                'is left here for manual review. HLTV fan votes are never used as probabilities.'),
            'sources': [
                {'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/rare-atom-vs-alter-ego-O8GeLuSod4', 'label': 'EGamersWorld match page (placeholder 1.8/1.8, observed 2026-10-19 04:47 UTC)'},
                {'url': 'https://stavka.tv/matches/csgo/20-10-2026-alter-ego-rare-atom', 'label': 'Secondary preview quoting Alter Ego 1.60 / Rare Atom ≈2.20 (not used as a line)'},
                {'url': 'https://www.hltv.org/matches/2399577/rare-atom-vs-alter-ego-macemedia-void-autumn-cup-2026', 'label': 'HLTV fixture page (fan vote exists and is excluded by policy)'},
                {'url': 'https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/research/session-b214c818/captures.json', 'label': 'Session capture record'},
            ],
        },
        {
            'id': 'b214c818-book-line-upgrades',
            'status': 'Published — dated aggregator lines, re-observed by the refresh',
            'finding': (
                'Five open fixtures moved from model/research tiers onto dated external lines: 1081532 ASTRAL–Leo '
                '(2.05/1.68), 1081552 Nemesis–Nuclear TigeRES (1.75/2.00), 1079181 Fire Flux–ex-6666 (2.23/1.56), '
                '1079646 Lavked–ex-6666 (2.20/1.57) and 1082157 Sangal–Aurora YB (1.08/6.28), all read live on '
                '2026-10-19 from the EGamersWorld listing pages and de-vigged by scripts.core.quote_book. This is '
                'an aggregator display of bookmaker odds (underlying book unnamed, no price-update timestamp) — '
                'one listing, not consensus. Each observation is valid for eight hours unless scripts/books.py '
                're-confirms it from the listing page on a scheduled refresh; after that the row falls back to the '
                'documented lower tiers and says so.'),
            'sources': [
                {'url': 'https://egamersworld.com/counterstrike/match/V1JAWhPomg/astral-esports-vs-leo-team-8fOCBVAsJ', 'label': 'ASTRAL–Leo listing (1081532)'},
                {'url': 'https://egamersworld.com/counterstrike/match/4JaFCnn5Ve/team-nemesis-vs-nuclear-tigeres-L6K0vG-5-', 'label': 'Nemesis–Nuclear TigeRES listing (1081552)'},
                {'url': 'https://egamersworld.com/counterstrike/match/Nk9F-Ov54e/fire-flux-esports-vs-ex-6666-g84ZstIes', 'label': 'Fire Flux–ex-6666 listing (1079181)'},
                {'url': 'https://egamersworld.com/counterstrike/match/_rW8GEyWK/lavked-vs-ex-6666-7kGDDWVoD', 'label': 'Lavked–ex-6666 listing (1079646)'},
                {'url': 'https://egamersworld.com/counterstrike/match/41yaj8BdVx/sangal-vs-aurora-young-blud-t529SG6szs', 'label': 'Sangal–Aurora Young Blud listing (1082157)'},
                {'url': 'https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/research/session-b214c818/REPORT.md', 'label': 'Session research report'},
            ],
        },
    ]
    have_notes = {n.get('id') for n in notes}
    for spec in note_specs:
        if spec['id'] in have_notes:
            continue
        notes.append(spec)
        have_notes.add(spec['id'])
        added_notes += 1
        print('note    +', spec['id'])

    if added_receipts:
        receipts_doc['collected_by'] = (receipts_doc.get('collected_by', '') + ', session b214c818').lstrip(', ')
        receipts_doc['note'] = (receipts_doc.get('note') or '') + (
            ' Session b214c818 (2026-10-19) added five live listing receipts and six refused placeholder '
            'listings; captures and decision notes are in research/session-b214c818/captures.json.')
    receipts_doc['collected_at'] = '2026-10-19T05:05:00Z'

    RECEIPTS.write_text(json.dumps(receipts_doc, ensure_ascii=False, indent=1) + '\n')
    IDENTITIES.write_text(json.dumps(identities_doc, ensure_ascii=False, indent=2) + '\n')
    NOTES.write_text(json.dumps(notes, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({'receipts_added': added_receipts, 'rejections_added': added_rejections,
                      'aliases_added': added_aliases, 'notes_added': added_notes}, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
