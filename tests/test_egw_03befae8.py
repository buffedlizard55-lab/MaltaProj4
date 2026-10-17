"""Session 03befae8 (2026-10-17): book-listing tier, day-five block, mobile summary.

Three things are covered here:

* a researched book-listing receipt prices the row it names, and only that row;
* the researched book tier runs before our own originated model line, because an
  external price outranks a model estimate;
* the day-five bracket block and the mobile executive summary are complete,
  sourced and reachable.
"""
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import build, core

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 17, 1, 0, tzinfo=timezone.utc)
RECEIPTS = json.loads((ROOT / 'data/book-receipts.json').read_text())


def fixture(**kw):
    base = {
        'id': '1081521', 'teams': ['ex-6666', 'Privateer'], 'state': 'open',
        'start': '2026-10-18T13:45:00Z', 'lock': '2026-10-18T13:39:00Z',
        'probabilities': None, 'pick': None, 'evidence': [], 'attempts': [],
        'flags': [], 'best_of': None, 'competition': 'CCT Europe 2026 Challengers #8',
    }
    base.update(kw)
    return base


class BookListingReceiptTests(unittest.TestCase):
    def test_the_new_receipt_names_the_row_it_prices(self):
        receipt = next(r for r in RECEIPTS['receipts'] if r['id'] == 'egw-rW6Ymkl0D-ex-6666-privateer')
        self.assertEqual('1081521', receipt['fixture_id'])
        self.assertEqual(['ex-6666', 'Privateer Gaming'], receipt['source_teams'])
        self.assertEqual('2026-10-18T13:45:00Z', receipt['start'])
        self.assertEqual([1.15, 4.5], receipt['odds'])
        self.assertTrue(receipt['url'].startswith('https://egamersworld.com/counterstrike/match/'))
        for source in receipt['alias_sources']:
            self.assertTrue(source.startswith('https://'), source)

    def test_the_receipt_replays_to_a_two_sided_line_and_a_pick(self):
        receipt = next(r for r in RECEIPTS['receipts'] if r['id'] == 'egw-rW6Ymkl0D-ex-6666-privateer')
        candidate = core.book_candidate(receipt)
        quote = core.quote_book(candidate, [0, 1], NOW)
        self.assertAlmostEqual(0.796, quote['probabilities'][0], places=2)
        self.assertAlmostEqual(0.204, quote['probabilities'][1], places=2)
        self.assertLessEqual(quote['overround'], 0.25)
        row = fixture()
        core.book_research_pick(row, RECEIPTS['receipts'], now=NOW)
        self.assertEqual('ex-6666', row['pick'])
        self.assertEqual('bookmaker_fallback', row['method'])
        self.assertAlmostEqual(0.796, row['probabilities'][0], places=2)
        self.assertTrue(any('Book research' == a['provider'] and a['status'] == 'resolved'
                            for a in row['attempts']))

    def test_receipt_expires_at_eight_hours_even_when_fixture_is_open(self):
        receipt = next(r for r in RECEIPTS['receipts'] if r['id'] == 'egw-rW6Ymkl0D-ex-6666-privateer')
        observed = core.dt(receipt['observed_at'])
        for offset, accepted in ((timedelta(hours=8, microseconds=-1), True),
                                 (timedelta(hours=8), False),
                                 (timedelta(days=30), False)):
            with self.subTest(offset=offset):
                row = fixture()
                core.book_research_pick(row, [receipt], now=observed + offset)
                self.assertEqual(accepted, row['probabilities'] is not None)

    def test_a_receipt_never_prices_a_row_it_does_not_name(self):
        row = fixture(id='1081522', teams=['antidaun', 'Phantom Academy'],
                      start='2026-10-18T13:45:00Z')
        core.book_research_pick(row, RECEIPTS['receipts'], now=NOW)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])

    def test_a_stale_receipt_prices_nothing(self):
        receipt = next(r for r in RECEIPTS['receipts'] if r['id'] == 'egw-rW6Ymkl0D-ex-6666-privateer')
        stale = dict(receipt, observed_at='2026-10-16T16:00:00Z')
        row = fixture()
        core.book_research_pick(row, [stale], now=NOW)
        self.assertIsNone(row['probabilities'])
        self.assertTrue(any('stale' in a['reason'].lower() for a in row['attempts']))

    def test_the_refused_listings_are_recorded_and_never_priced(self):
        refused = {r['fixture_id']: r for r in RECEIPTS['rejected_listings']}
        for fixture_id in ('1081511', '1079634', '1081522', '1081861', '1081863'):
            self.assertIn(fixture_id, refused, fixture_id)
            self.assertEqual([1.8, 1.8], refused[fixture_id]['displayed'])
            self.assertIn('1.8', refused[fixture_id]['reason'])
        priced = {r['fixture_id'] for r in RECEIPTS['receipts']}
        self.assertNotIn('1081511', priced)
        self.assertNotIn('1079634', priced)
        self.assertNotIn('1081861', priced)
        self.assertNotIn('1081863', priced)

    def test_the_refused_ex_6666_listing_is_marked_superseded(self):
        entry = next(r for r in RECEIPTS['rejected_listings'] if r['fixture_id'] == '1081521')
        self.assertEqual('egw-rW6Ymkl0D-ex-6666-privateer', entry['superseded_by'])


class TierOrderTests(unittest.TestCase):
    def test_the_researched_book_tier_runs_before_the_model(self):
        source = (ROOT / 'scripts/refresh.py').read_text()
        book = source.index('book_research_pick(m, now=now)')
        model = source.index('vrs.apply(m,standings,vrs_meta,lineups)')
        self.assertLess(book, model, 'A researched external book line must outrank our own model line')

    def test_the_model_still_fills_the_gap_when_no_listing_exists(self):
        row = fixture(id='9999999', teams=['Aaa', 'Bbb'], start='2026-10-18T13:45:00Z')
        core.book_research_pick(row, RECEIPTS['receipts'], now=NOW)
        self.assertIsNone(row['probabilities'])


class DayFiveBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = json.loads((ROOT / 'data/analysis.json').read_text())

    def test_the_block_is_complete_and_sourced(self):
        plan = self.notes['day_five_guidance']
        for key in ('date', 'headline', 'summary', 'points', 'fixtures', 'not_listed', 'unverified'):
            self.assertIn(key, plan)
        self.assertTrue(plan['points'])
        for point in plan['points']:
            self.assertTrue(point['source'].startswith('https://'), point)
            self.assertGreater(len(point['claim']), 10)
            self.assertGreater(len(point['detail']), 40)
        self.assertEqual(2, len(plan['not_listed']))
        for card in plan['not_listed']:
            self.assertTrue(card['hltv_url'].startswith('https://'))
            self.assertNotIn('points', card, 'No Sunday model line is attached without verified model inputs')
            self.assertEqual(2, len(card['teams']))
            self.assertFalse(any('TBA' in team for team in card['teams']))
            self.assertIn(card['pick'], card['teams'])
            self.assertIn('Research-only', card['pick_detail'])
            self.assertNotIn('market', card, 'Unverified Sunday prices must stay absent')

    def test_the_front_page_still_points_at_the_day_that_is_played(self):
        self.assertEqual('day_five_guidance', self.notes['front_page_plan'])
        self.assertEqual('Day-5 final-day guide', build.guidance_label(self.notes))
        self.assertIs(build.front_page_plan(self.notes), self.notes['day_five_guidance'])

    def test_the_day_four_block_lists_the_two_board_rows(self):
        plan = self.notes['day_four_guidance']
        ids = [f['hotspawn_id'] for f in plan['fixtures']]
        self.assertIn('1080207', ids)
        self.assertIn('1080208', ids)
        for f in plan['fixtures']:
            for source in f['sources']:
                self.assertTrue(source['url'].startswith('https://'), source)

    def test_the_analysis_page_renders_the_day_five_section(self):
        data = json.loads((ROOT / 'data/latest.json').read_text())
        html = build.analysis_page(data)
        self.assertIn('id="day-five-guidance"', html)
        self.assertIn('Third-place decider', html)
        self.assertIn('Grand final', html)
        self.assertIn('not computable for this fixture', html)

    def test_the_review_flag_for_the_book_listing_is_published(self):
        notes = json.loads((ROOT / 'data/review-notes.json').read_text())
        entry = next(n for n in notes if n['id'] == 'book-listing-access-egw')
        self.assertIn('403', entry['finding'])
        for source in entry['sources']:
            self.assertTrue(source['url'].startswith('https://'), source)


class MobileSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'data/latest.json').read_text())
        cls.html = build.overview(cls.data)

    def test_the_summary_offers_in_page_jumps(self):
        self.assertIn('class="jump-nav"', self.html)
        for anchor in ('#today', '#later', '#unresolved-summary', '#coverage'):
            self.assertIn(f'href="{anchor}"', self.html)

    def test_the_summary_lists_the_next_picks_with_their_price(self):
        self.assertIn('class="queue"', self.html)
        self.assertIn('queue-pick', self.html)
        self.assertIn('evidence.html#match-', self.html)

    def test_the_summary_still_links_to_the_picks_list(self):
        self.assertIn('href="picks.html"', self.html)
        self.assertIn('href="unresolved.html', self.html)


if __name__ == '__main__':
    unittest.main()
