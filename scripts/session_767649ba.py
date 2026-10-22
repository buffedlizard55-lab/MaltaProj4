"""Apply and replay session 767649ba's primary book-receipt research.

Reads ``research/session-767649ba/captures.json``, replays every accepted
receipt through ``scripts.core.book_candidate``, ``scripts.core.quote_book``,
``scripts.core.book_research_pick``, and ``scripts.books.parse_listing``,
repairs three non-canonical EGamersWorld slugs in ``data/book-receipts.json``
to their live canonical URLs, and idempotently upserts:

* accepted two-way receipt ``egw-4yp_dlKtNl-nexora-k27`` (fixture ``1082769``,
  ``K27 vs NEXORA``, ``2026-10-22T17:30:00Z``, ``[8.1, 1.021]`` in page order
  ``[NEXORA, K27]`` -> de-margined ``K27 88.81% / NEXORA 11.19%``, corroborated
  within 0.8 pp by СТАВКА ТВ ``7.80 / 1.06`` and KushVSporte ``8.20 / 1.04``);
* six fresh 2026-10-22 refused-placeholder / moneyline-absent records across
  ``1081869``, ``1079654``, ``1081149``, and ``1081150`` (plus refreshed
  canonical URLs and observation timestamps for ``1081597``, ``1082858``, and
  ``1082860``).

Idempotent: safe to run any number of times with zero duplicate entries.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.books import parse_listing
from scripts.core import book_candidate, book_research_pick, quote_book

ROOT = Path(__file__).resolve().parents[1]
CAPTURES_PATH = ROOT / 'research/session-767649ba/captures.json'
RECEIPTS_PATH = ROOT / 'data/book-receipts.json'
RECEIPT_ID = 'egw-4yp_dlKtNl-nexora-k27'


def load_captures(path: Path = CAPTURES_PATH) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def verify_capture_replay(captures: dict | None = None) -> dict:
    data = captures or load_captures()
    receipt = data['accepted_receipts'][0]
    assert receipt['id'] == RECEIPT_ID
    assert receipt['odds'][0] != receipt['odds'][1], 'identical placeholder pair is forbidden'
    assert all(float(x) > 1.0 for x in receipt['odds']), 'decimal odds must exceed 1.0'

    candidate = book_candidate(receipt)
    observed = datetime(2026, 10, 22, 1, 15, tzinfo=timezone.utc)
    # Candidate source_teams are ["NEXORA", "K27"], whereas Hotspawn fixture 1082769
    # has teams ["K27", "NEXORA"] -> index order [1, 0].
    quote = quote_book(candidate, [1, 0], observed)
    assert quote is not None, 'accepted receipt must pass quote_book freshness & margin gates'
    assert 0.0 < quote['overround'] <= 0.25, f"margin outside bounds: {quote['overround']}"
    assert abs(sum(quote['probabilities']) - 1.0) < 1e-12

    row = {
        'id': '1082769',
        'state': 'open',
        'teams': ['K27', 'NEXORA'],
        'start': '2026-10-22T17:30:00Z',
        'best_of': 3,
        'pick': None,
        'method': None,
        'probabilities': None,
        'fair_odds': None,
        'evidence': [],
        'flags': [],
        'attempts': [],
    }
    book_research_pick(row, [receipt], now=observed)
    assert row['pick'] == 'K27'
    assert row['method'] == 'bookmaker_fallback'
    assert abs(row['probabilities'][0] - 0.8880605196798597) < 1e-12
    assert abs(row['probabilities'][1] - 0.11193948032014032) < 1e-12

    # Confirm live-style HTML fragment satisfies scripts.books.parse_listing.
    sample_html = (
        '<script type="application/ld+json">'
        '{"name":"NEXORA VS K27","startDate":"2026-10-22T17:30:00.000Z"}'
        '</script>'
        '<div>NEXORA 8.1 Make a bet 1.021 K27</div>'
    )
    parsed = parse_listing(sample_html)
    assert len(parsed) == 1 and parsed[0]['bound_to_labels'] is True
    assert parsed[0]['odds'] == [8.1, 1.021]

    return {
        'receipt_id': RECEIPT_ID,
        'fixture_id': '1082769',
        'pick': row['pick'],
        'probabilities': row['probabilities'],
        'fair_odds': row['fair_odds'],
        'overround': quote['overround'],
    }


def apply(receipts_path: Path = RECEIPTS_PATH, captures_path: Path = CAPTURES_PATH) -> dict:
    captures = load_captures(captures_path)
    summary = verify_capture_replay(captures)
    doc = json.loads(receipts_path.read_text(encoding='utf-8'))

    if '767649ba' not in doc.get('collected_by', ''):
        doc['collected_by'] = doc['collected_by'].rstrip() + ', session 767649ba'
    doc['collected_at'] = '2026-10-22T01:15:00Z'

    existing_ids = {r['id']: idx for idx, r in enumerate(doc['receipts'])}
    for rec in captures['accepted_receipts']:
        if rec['id'] in existing_ids:
            doc['receipts'][existing_ids[rec['id']]] = rec
        else:
            doc['receipts'].append(rec)

    repairs = {
        (item['fixture_id'], item['old_url']): item
        for item in captures.get('canonical_url_repairs', [])
    }
    for rej in doc['rejected_listings']:
        key = (str(rej.get('fixture_id')), rej.get('url'))
        if key in repairs:
            rej['url'] = repairs[key]['new_url']
            rej['observed_at'] = repairs[key]['observed_at']

    seen_rejections = {
        (str(r.get('fixture_id')), r.get('url')): idx
        for idx, r in enumerate(doc['rejected_listings'])
    }
    for rej in captures['rejected_listings']:
        key = (str(rej['fixture_id']), rej['url'])
        if key in seen_rejections:
            doc['rejected_listings'][seen_rejections[key]] = rej
        else:
            doc['rejected_listings'].append(rej)

    receipts_path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return summary


if __name__ == '__main__':
    result = apply()
    print(json.dumps(result, indent=2))
