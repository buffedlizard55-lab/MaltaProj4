"""Session 241b0c14: fail-closed probe verdicts and board-source invariants.

Offline only. The probe's network reads run on the harvest runner; these tests
pin the pure decision functions so a placeholder, a wide book, a wrong-fixture
listing or a guessed slug can never read as a candidate line, and they check
the committed board against the project contract without pinning live counts
(the board changes every refresh; the *shape* of an honest row does not).
"""
import json
import unittest
from pathlib import Path

from scripts import probe_241b0c14 as probe
from scripts import summary

ROOT = Path(__file__).resolve().parents[1]


class TestPolymarketVerdict(unittest.TestCase):
    def test_ninety_point_book_is_refused(self):
        # Market 6036921 as recorded on row 1082925: 0.05/0.95, $108.62.
        verdict = probe.polymarket_verdict({
            'bestBid': 0.05, 'bestAsk': 0.95, 'liquidity': '108.6187',
            'outcomePrices': '["0.5", "0.5"]', 'updatedAt': '2026-10-22T07:54:57Z',
            'acceptingOrders': True, 'active': True, 'closed': False})
        self.assertEqual(verdict['verdict'], 'refused')
        self.assertEqual(verdict['spread_points'], 90.0)

    def test_strict_and_wide_shapes_are_descriptive_only(self):
        strict = probe.polymarket_verdict({'bestBid': 0.55, 'bestAsk': 0.65, 'liquidity': '900'})
        wide = probe.polymarket_verdict({'bestBid': 0.54, 'bestAsk': 0.96, 'liquidity': '156.04'})
        self.assertEqual(strict['verdict'], 'strict_gate_shape')
        self.assertEqual(wide['verdict'], 'wide_gate_shape')
        self.assertIn('refresh still owns', strict['reason'])

    def test_low_liquidity_and_missing_book_are_refused(self):
        self.assertEqual(probe.polymarket_verdict(
            {'bestBid': 0.5, 'bestAsk': 0.55, 'liquidity': '40'})['verdict'], 'refused')
        self.assertEqual(probe.polymarket_verdict({'liquidity': '500'})['verdict'], 'refused')


class TestListingVerdict(unittest.TestCase):
    FIXTURE = {'teams': ['BESTIA Academy', 'RED Canids Academy'],
               'start': '2026-10-23T19:00:00Z'}

    def test_exact_bound_asymmetric_reading_is_a_candidate(self):
        verdict = probe.listing_verdict([{
            'team1': 'RED Canids Academy', 'team2': 'BESTIA Academy',
            'start': '2026-10-23T19:00:00Z', 'odds': [1.72, 2.0],
            'bound_to_labels': True}], self.FIXTURE)
        self.assertEqual(verdict['verdict'], 'candidate_line')

    def test_wrong_start_unbound_and_empty_are_refused(self):
        base = {'team1': 'BESTIA Academy', 'team2': 'RED Canids Academy',
                'odds': [1.72, 2.0], 'bound_to_labels': True}
        self.assertEqual(probe.listing_verdict(
            [base | {'start': '2026-10-23T22:00:00Z'}], self.FIXTURE)['verdict'], 'refused')
        self.assertEqual(probe.listing_verdict(
            [base | {'start': '2026-10-23T19:00:00Z', 'bound_to_labels': False}],
            self.FIXTURE)['verdict'], 'refused')
        self.assertEqual(probe.listing_verdict([], self.FIXTURE)['verdict'], 'refused')

    def test_registered_identity_label_still_matches(self):
        # Projeto do KinGui (Hotspawn) is Tropa do KinGui in data/identities.json.
        verdict = probe.listing_verdict([{
            'team1': 'Tropa do KinGui', 'team2': 'Martians',
            'start': '2026-10-22T13:00:00Z', 'odds': [1.06, 7.26],
            'bound_to_labels': True}],
            {'teams': ['Projeto do KinGui', 'Martians'], 'start': '2026-10-22T13:00:00Z'})
        self.assertEqual(verdict['verdict'], 'candidate_line')


class TestDiscoveryAndPresence(unittest.TestCase):
    def test_stavka_discovery_needs_both_teams_in_a_listed_href(self):
        hrefs = ['/matches/csgo/23-10-2026-bestia-academy-red-canids-academy',
                 '/matches/csgo/23-10-2026-bestia-academy-someone-else',
                 '/matches/csgo']
        found = probe.stavka_candidates(hrefs, TestListingVerdict.FIXTURE)
        self.assertEqual(found, ['https://stavka.tv/matches/csgo/23-10-2026-bestia-academy-red-canids-academy'])

    def test_mirror_presence_reports_absence_honestly(self):
        standings = {'teams': [{'standing': 61, 'points': 1093, 'name': 'FlyQuest'}]}
        presence = probe.mirror_presence(standings, {'teams': ['FlyQuest', 'Staqued']})
        self.assertEqual(presence[0]['listed_rows'][0]['points'], 1093)
        self.assertEqual(presence[1]['listed_rows'], [])


class TestDiff(unittest.TestCase):
    def test_added_changed_and_blank_rows_are_reported(self):
        old = {'generated_at': 'a', 'matches': [
            {'id': '1', 'state': 'open', 'pick': 'A', 'method': 'exchange',
             'probabilities': [0.6, 0.4], 'teams': ['A', 'B']}]}
        new = {'generated_at': 'b', 'matches': [
            {'id': '1', 'state': 'open', 'pick': None, 'method': None,
             'probabilities': None, 'teams': ['A', 'B']},
            {'id': '2', 'state': 'open', 'pick': 'C', 'method': 'research_rank',
             'probabilities': None, 'teams': ['C', 'D']}]}
        diff = probe.diff_snapshots(old, new)
        self.assertEqual(diff['added_fixture_ids'], ['2'])
        self.assertEqual(diff['blank_percentage_fresh'], ['1', '2'])
        self.assertEqual(diff['unpicked_fresh'], ['1'])
        self.assertIn('pick', diff['changed_rows'][0]['changes'])


class TestCommittedBoardContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'data/latest.json').read_text())
        cls.opens = [m for m in cls.data['matches'] if m['state'] == 'open']

    def test_counts_partition_the_open_board(self):
        c = summary.counts(self.data['matches'])
        self.assertEqual(c['with_pick'] + c['no_pick'] + (0 if c['open'] else 0),
                         c['open'] + (c['no_pick'] - sum(not m.get('pick') for m in self.opens)))
        self.assertEqual(c['priced'] + c['without_percentage'], c['open'])
        self.assertEqual(c['market'] + c['model'] + c['research'] +
                         sum(not m.get('pick') for m in self.opens) +
                         sum(1 for m in self.opens
                             if m.get('probabilities') is not None
                             and summary.origin(m)[0] == 'unknown'),
                         c['open'])

    def test_every_open_row_carries_official_source_links(self):
        for m in self.opens:
            self.assertTrue(str(m.get('source_url') or '').startswith('https://'), m['id'])
            has_evidence_link = bool(
                (m.get('evidence') or []) or (m.get('hltv_context') or {}).get('source')
                or any(a.get('url') for a in m.get('attempts') or []))
            self.assertTrue(has_evidence_link, m['id'])

    def test_blank_percentage_rows_state_their_limitation(self):
        for m in self.opens:
            if m.get('probabilities') is None:
                self.assertTrue((m.get('reason') or '').strip(), m['id'])
                self.assertIsNone(m.get('fair_odds'), m['id'])
                if m.get('pick'):
                    self.assertIn(m.get('method'),
                                  ('research_rank', 'research_rank_single', 'research_vrs_single'),
                                  m['id'])


class TestExecutiveSummaryLinks(unittest.TestCase):
    def test_summary_links_to_picks_and_unresolved_section(self):
        html_text = (ROOT / 'index.html').read_text()
        for needle in ('id="unresolved-picks"', 'href="picks.html"',
                       'href="unresolved.html"', '#picks-at-a-glance',
                       'id="freshness-strip"', 'data-count="priced"'):
            self.assertIn(needle, html_text)


class TestResearchRegister(unittest.TestCase):
    def test_placeholder_refusals_for_the_two_blank_rows_are_on_record(self):
        doc = json.loads((ROOT / 'data/book-receipts.json').read_text())
        for fixture_id in ('1082925', '1082860'):
            refusals = [r for r in doc.get('rejected_listings') or []
                        if str(r.get('fixture_id')) == fixture_id
                        and r.get('displayed') == [1.8, 1.8]]
            self.assertTrue(refusals, fixture_id)


if __name__ == '__main__':
    unittest.main()
