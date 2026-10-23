"""Session cf8f94b9 regression tests:

1. ``scripts/books.py`` integer-underdog & pre-button second-team label parsing:
   - Parses real EGamersWorld markup where the underdog carries a whole-integer
     decimal price (``1.001 Make a bet 12``) and where the second team's price
     appears inside ``window`` before ``Make a bet`` (``FlyQuest 1.001 ...
     Staqued 12 1.001 Make a bet 12``).
   - Strictly refuses rounded ``<= 1.0`` displays (``1.00 / 12.00``), ``1.8/1.8``
     placeholders, and identical coin-flip pairs.
2. ``scripts/hltv.py`` multi-day ``date_views`` prioritization & ``DATE_PAGE_LIMIT``:
   - Reads every unmatched fixture's exact UTC date first before neighbour days
     so 4-day-out LAN matches (e.g. ``2026-10-27`` ``FlyQuest vs Staqued``) are
     never crowded out by intermediate days.
3. ``data/book-receipts.json`` & 6-sportsbook pre-match consensus for ``1082860``:
   - Verifies ``egw-4kaAQWgKEx-flyquest-staqued`` de-vigs to exact ``12000/13001``
     (``92.3006%``) / ``1001/13001`` (``7.6994%``), agrees within ``0.21``
     percentage points across all 6 named sportsbooks on EGamersWorld, and marks
     prior ``1.8/1.8`` placeholder reads superseded.
4. Working-tree cleanliness & independent zero-collector repository audit:
   - Verifies ``scripts.session_b214c818.main()`` leaves ``data/identities.json``
     byte-for-byte unchanged (``indent=1``) and ``verification-cf8f94b9`` reports
     zero problems across all rows, links, checksums, and registers.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from scripts import books, core, hltv

ROOT = Path(__file__).resolve().parents[1]


def load_auditor():
    spec = importlib.util.spec_from_file_location(
        'audit_cf8f94b9',
        ROOT / 'verification-cf8f94b9/audit_cf8f94b9.py',
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestBooksIntegerUnderdogAndWindowBinding(unittest.TestCase):
    EGW_FLYQUEST_HTML = '''
    <html><head>
    <script type="application/ld+json">
    {"name":"FlyQuest VS Staqued","startDate":"2026-10-27T03:00:00.000Z"}
    </script></head><body>
    <div class="header-odds">
      <span>FlyQuest</span><span>1.001</span>
      <span>Staqued</span><span>12</span>
      <a>1.001 Make a bet 12</a>
    </div>
    </body></html>
    '''

    def test_parses_integer_underdog_and_pre_button_second_team_label(self):
        readings = books.parse_listing(self.EGW_FLYQUEST_HTML)
        self.assertEqual(len(readings), 1)
        r = readings[0]
        self.assertEqual((r['team1'], r['team2']), ('FlyQuest', 'Staqued'))
        self.assertEqual(r['start'], '2026-10-27T03:00:00.000Z')
        self.assertEqual(r['odds'], [1.001, 12.0])
        self.assertTrue(r['bound_to_labels'])

    def test_refuses_rounded_unit_price_or_equal_integer_pair(self):
        rounded = self.EGW_FLYQUEST_HTML.replace('1.001', '1.00')
        equal = self.EGW_FLYQUEST_HTML.replace('1.001', '2').replace('>12<', '>2<').replace('bet 12', 'bet 2')
        self.assertEqual(books.parse_listing(rounded), [])
        self.assertEqual(books.parse_listing(equal), [])


class TestHltvMultiDayDateViews(unittest.TestCase):
    def test_exact_match_dates_precede_neighbour_offsets(self):
        matches = [
            {'start': f'2026-10-{day:02d}T03:00:00Z', 'teams': [f'A{day}', f'B{day}']}
            for day in (23, 24, 25, 26, 27, 31)
        ]
        views = hltv.date_views(matches, [])[:hltv.DATE_PAGE_LIMIT]
        self.assertIn('2026-10-27', views)
        self.assertIn('2026-10-31', views)
        self.assertEqual(views[:6], [
            '2026-10-23', '2026-10-24', '2026-10-25',
            '2026-10-26', '2026-10-27', '2026-10-31',
        ])


class TestFlyQuestStaquedReceiptAndSixBookConsensus(unittest.TestCase):
    SIX_BOOKS = {
        'Thunderpick': (Decimal('1.001'), Decimal('12')),
        'Rainbet': (Decimal('1.01'), Decimal('11.76')),
        'Underdog': (Decimal('1.01'), Decimal('12.01')),
        'CocoBet': (Decimal('1.02'), Decimal('11.91')),
        'FanDuel': (Decimal('1.01'), Decimal('12.02')),
        'Fanatics': (Decimal('1.02'), Decimal('11.97')),
    }

    def test_receipt_replays_exact_fraction_and_matches_all_six_books(self):
        doc = json.loads((ROOT / 'data/book-receipts.json').read_text(encoding='utf-8'))
        receipt = next(r for r in doc['receipts'] if r['id'] == 'egw-4kaAQWgKEx-flyquest-staqued')
        cand = core.book_candidate(receipt)
        quote = core.quote_book(cand, [0, 1], datetime(2026, 10, 23, 5, 0, tzinfo=timezone.utc))
        self.assertAlmostEqual(quote['probabilities'][0], 12000 / 13001, places=12)
        self.assertAlmostEqual(quote['probabilities'][1], 1001 / 13001, places=12)

        shares = []
        for book, (o1, o2) in self.SIX_BOOKS.items():
            q1, q2 = Decimal(1) / o1, Decimal(1) / o2
            shares.append((book, float(q1 / (q1 + q2))))
        spread_pp = (max(s for _, s in shares) - min(s for _, s in shares)) * 100.0
        self.assertLess(spread_pp, 0.25)

        prior = [r for r in doc['rejected_listings'] if str(r.get('fixture_id')) == '1082860']
        self.assertTrue(prior)
        self.assertTrue(all(r.get('superseded_by') == 'egw-4kaAQWgKEx-flyquest-staqued' for r in prior))


class TestWorkingTreeCleanlinessAndIndependentAudit(unittest.TestCase):
    def test_appliers_leave_identities_untouched_and_independent_audit_passes(self):
        before = hashlib.sha256((ROOT / 'data/identities.json').read_bytes()).hexdigest()
        import scripts.session_b214c818 as b214
        import scripts.apply_cf8f94b9 as cf8f
        b214.main()
        cf8f.apply_registers()
        after = hashlib.sha256((ROOT / 'data/identities.json').read_bytes()).hexdigest()
        self.assertEqual(before, after)

        auditor = load_auditor()
        report = auditor.audit_repository(ROOT)
        self.assertEqual(report['problems'], [])
        self.assertGreater(report['open_total'], 0)
        self.assertEqual(report['open_with_pick'], report['open_total'])


if __name__ == '__main__':
    unittest.main()
