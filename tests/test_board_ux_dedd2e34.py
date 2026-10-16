"""The board has to answer "where is my pick, and why is this one blank?" (dedd2e34).

Two rules the site exists to keep: every fixture that can be picked is named on the
front page for the day it is played, and a fixture that cannot be priced shows the
external evidence that was found instead - as a rejected observation, never as a
probability. These tests pin the rendering helpers that do that work.
"""
import json
import unittest
import copy
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from scripts.build import gap_ledger, overview, starts_on

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]


def attempt(provider='Polymarket', reason='Exchange observation or update is older than eight hours.',
            api_url='https://gamma-api.polymarket.com/markets/1'):
    return {'provider': provider, 'status': 'unresolved', 'reason': reason,
            'url': api_url, 'rejected_quote': {'api_url': api_url, 'provider': provider,
                                               'notice': 'Rejected evidence, not a pick or verified probability.',
                                               'raw': {'outcomes': '["Alpha","Beta"]', 'outcomePrices': '["0.69","0.31"]',
                                                       'bestBid': 0.41, 'bestAsk': 0.97, 'liquidity': '102.4399',
                                                       'updatedAt': '2026-10-15T08:26:50Z'},
                                               'observed_at': '2026-10-16T04:22:09Z'}}


def row(match_id='1', teams=('Alpha', 'Beta'), start='2026-10-16T14:00:00Z', probabilities=None,
        pick='Alpha', attempts=(), competition='Some Series', tier='b'):
    return {'id': match_id, 'teams': list(teams), 'start': start, 'lock': '2026-10-16T13:54:00Z',
            'probabilities': probabilities, 'pick': pick, 'attempts': list(attempts),
            'competition': competition, 'tier': tier, 'state': 'open',
            'source_url': 'https://www.hotspawn.com/matches/alpha-vs-beta-' + match_id,
            'flags': ['Research pick on one-sided ranking evidence: no probability published.']}


class StartsOnTests(unittest.TestCase):
    def test_day_is_the_utc_calendar_date_of_the_start(self):
        today = datetime(2026, 10, 16, tzinfo=timezone.utc).date()
        self.assertTrue(starts_on(row(start='2026-10-16T00:00:00Z'), today))
        self.assertTrue(starts_on(row(start='2026-10-16T23:59:59Z'), today))
        self.assertFalse(starts_on(row(start='2026-10-17T00:00:00Z'), today))

    def test_unusable_timestamps_are_excluded_not_defaulted(self):
        today = datetime(2026, 10, 16, tzinfo=timezone.utc).date()
        for start in (None, '', 'unverified', 'yesterday'):
            self.assertFalse(starts_on(row(start=start), today), start)


class GapLedgerTests(unittest.TestCase):
    captured = datetime(2026, 10, 16, 4, 22, 9, tzinfo=timezone.utc)

    def render(self, rows):
        html = gap_ledger(rows, self.captured)
        return html, BeautifulSoup(html, 'html.parser')

    def test_empty_input_renders_nothing(self):
        self.assertEqual(gap_ledger([], self.captured), '')

    def test_rejected_quote_shows_its_numbers_and_is_labelled(self):
        html, soup = self.render([row(attempts=[attempt()])])
        text = soup.get_text(' ', strip=True)
        self.assertIn('rejected observation', text)
        self.assertIn('quoted mid: Alpha 69.0% / Beta 31.0%', text)
        self.assertIn('bid 0.41', text)
        self.assertIn('ask 0.97', text)
        self.assertIn('liquidity $102.44', text)          # rounded, not raw float noise
        self.assertIn('bid-ask gap 56.0 points', text)    # the gate it failed, in points
        self.assertIn('19.9 h before this snapshot', text)
        self.assertIn('alpha-vs-beta-1', html)            # link to the fixture itself
        self.assertEqual(soup.select('a[href^="https://gamma-api"]')[0].get_text(strip=True), 'Raw source record ↗')

    def test_the_same_rejection_tried_twice_is_listed_once(self):
        # The collector queries the exchange twice (a wide retry after the strict
        # pass); a repeated card line reads like a bug, so the summary dedupes.
        _, soup = self.render([row(attempts=[attempt(), attempt()])])
        self.assertEqual(len(soup.select('li')), 1)

    def test_a_distinct_attempt_from_the_same_provider_still_shows(self):
        _, soup = self.render([row(attempts=[attempt(), attempt(reason='No exact team-pair and UTC-start match in retrieved feed.')])])
        self.assertEqual(len(soup.select('li')), 2)

    def test_a_row_with_no_attempts_says_so_instead_of_rendering_a_blank_card(self):
        html, soup = self.render([row()])
        self.assertIn('No attempt was recorded for this fixture.', soup.get_text(' ', strip=True))
        self.assertNotIn('0.69', html)

    def test_no_probability_language_leaks_into_a_gap_card(self):
        _, soup = self.render([row(attempts=[attempt()])])
        text = soup.get_text(' ', strip=True)
        for phrase in ('our pick', 'recommended'):
            self.assertNotIn(phrase, text.lower())


class OverviewSectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = overview(json.loads((ROOT / 'data/latest.json').read_text()))

    def soup(self):
        return BeautifulSoup(self.body, 'html.parser')

    def test_every_fixture_id_appears_once_on_the_page(self):
        # scripts/validate.py refuses a page that renders the same fixture twice, so
        # the today/later split and the gap section must partition the open rows.
        ids = [tr['data-match'] for tr in self.soup().select('tr[data-match]')]
        self.assertEqual(len(ids), len(set(ids)))

    def today_wrap(self, soup):
        return soup.select_one('.table-wrap[aria-label="Today\'s picks"]')

    def test_today_section_holds_only_priced_rows_starting_that_day(self):
        data = json.loads((ROOT / 'data/latest.json').read_text())
        captured = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00')).date()
        by_id = {m['id']: m for m in data['matches']}
        wrap = self.today_wrap(self.soup())
        if wrap is None:
            # Nothing starts on the capture date, so the section must fall back to the
            # next fixtures rather than showing an empty "Today" heading.
            self.assertIn('Next on the board', self.body)
            return
        shown = [tr['data-match'] for tr in wrap.select('tr[data-match]')]
        self.assertTrue(shown)
        for match_id in shown:
            m = by_id[match_id]
            self.assertEqual(m['state'], 'open', match_id)
            self.assertIsNotNone(m['probabilities'], match_id)
            self.assertTrue(starts_on(m, captured), match_id)
        starts = [m['start'] for m in (by_id[i] for i in shown)]
        self.assertEqual(starts, sorted(starts))

    def test_no_priced_fixture_today_falls_back_to_the_next_board(self):
        # Same page, captured after the last start of the day: the section still names
        # picks, it just relabels them and keeps the ordering rule.
        data = json.loads((ROOT / 'data/latest.json').read_text())
        data['generated_at'] = '2026-10-13T23:45:00Z'
        body = overview(data)
        soup = BeautifulSoup(body, 'html.parser')
        self.assertIsNone(self.today_wrap(soup))
        self.assertIn('Next on the board', body)
        shown = [tr['data-match'] for tr in soup.select('.table-wrap[aria-label="Later picks"] tr[data-match]')]
        by_id = {m['id']: m for m in data['matches']}
        self.assertTrue(shown)
        for match_id in shown:
            self.assertEqual(by_id[match_id]['state'], 'open', match_id)
            self.assertIsNotNone(by_id[match_id]['probabilities'], match_id)

    def test_gap_section_lists_exactly_the_unpriced_open_rows(self):
        # A VRS-model row is priced (by us) and belongs in the board above; only a row
        # with no percentage at all goes in the gap section. Mixing them duplicates a
        # fixture on one page, which the validator refuses.
        data = json.loads((ROOT / 'data/latest.json').read_text())
        unpriced = sorted(m['id'] for m in data['matches'] if m['state'] == 'open' and m['probabilities'] is None)
        priced_today = {m['id'] for m in data['matches'] if m['state'] == 'open' and m['probabilities'] is not None}
        table = self.soup().select_one('.table-wrap[aria-label="Open matches without a market line"]').select_one('table')
        shown = sorted(tr['data-match'] for tr in table.select('tr[data-match]'))
        self.assertEqual(shown, unpriced)
        self.assertFalse(set(shown) & priced_today)
        cards = self.soup().select('#unresolved-summary .gap-card h3')
        self.assertTrue(cards, 'every unpriced open row should get a card of attempted sources')


if __name__ == '__main__':
    unittest.main()
