"""Session f89bb1f8: phone-first executive summary + live coverage audit.

Two contracts, both measured rather than asserted from prose:

1. **The home page's first phone screen contains a real pick.** The 2026-10-23
   build put the first pick card at y=864 at 320x568 (and y=767 at 390x844), so
   the first screen on both phones was a heading, a status card and a folded
   guide. The layout fix is CSS ordering plus a one-line next pick in the strip;
   this module pins the markup and the rules that produce it so a later session
   cannot quietly undo them, and checks that no pick, percentage or source link
   was removed to achieve it.

2. **Every future fixture carries a pick or a documented limitation.**
   ``scripts.audit_f89bb1f8`` re-derives the coverage answer from the published
   snapshot. These tests drive it with the real board and with corrupted copies,
   so a silent blank or a dropped row fails loudly.
"""
import copy
import json
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import audit_f89bb1f8, build, summary
from scripts.core import dt

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/latest.json').read_text())
CSS = (ROOT / 'site/assets/style.css').read_text()
APP = (ROOT / 'site/assets/app.js').read_text()
CLOCK = dt(DATA['built_at'])


class PhoneFirstScreenTests(unittest.TestCase):
    """The strip and the glance list, at the level a phone actually renders."""

    @classmethod
    def setUpClass(cls):
        cls.html = build.overview(copy.deepcopy(DATA))
        cls.soup = BeautifulSoup(cls.html, 'html.parser')
        cls.opens = [m for m in DATA['matches'] if m.get('state') == 'open']

    def test_strip_names_the_first_pick_with_its_number(self):
        first = sorted([m for m in self.opens if m.get('pick')],
                       key=lambda m: (m.get('start') or '', m['id']))[0]
        block = self.soup.select_one('#freshness-strip .fresh-next')
        self.assertIsNotNone(block)
        text = block.get_text(' ', strip=True)
        self.assertIn(first['pick'], text)
        index = first['teams'].index(first['pick'])
        self.assertIn('%.1f%%' % (first['probabilities'][index] * 100), text)
        self.assertIn('23 Oct', text)

    def test_strip_pick_is_a_linked_recommendation_with_a_deadline(self):
        anchor = self.soup.select_one('#freshness-strip .fresh-next a.fresh-next-link')
        self.assertIsNotNone(anchor)
        self.assertTrue(anchor['href'].startswith('evidence.html#match-'))
        self.assertEqual(anchor['data-next-expires'], anchor['data-next-lock'])
        self.assertEqual(anchor['data-next-expires'],
                         build.pick_deadline(next(m for m in self.opens
                                                  if 'match-' + m['id'] == anchor['href'].split('#')[1]),
                                             DATA['fixtures_observed_at']))

    def test_strip_pick_zeroes_out_when_the_snapshot_goes_stale(self):
        self.assertIn("[data-next-expires]", APP)
        self.assertIn(".fresh-next-pick", APP)
        self.assertIn('withheld — refresh pending', APP)

    def test_glance_list_still_lists_every_open_match_once(self):
        glance = self.soup.select_one('#picks-at-a-glance')
        self.assertEqual(len(glance.select('a.glance-row')), len(self.opens))
        self.assertEqual(len(glance.select('a.glance-card-mobile')), len(self.opens))
        for match in self.opens:
            links = glance.select(f'a[href="evidence.html#match-{match["id"]}"]')
            self.assertGreaterEqual(len(links), 2, match['id'])

    def test_phone_rules_reorder_and_never_delete_the_pick_content(self):
        # The list precedes the folded guide on a phone; both stay in the DOM.
        self.assertIn('body[data-page="index"] main>#picks-at-a-glance{order:4}', CSS)
        self.assertIn('body[data-page="index"] main>details.briefing-more{order:6}', CSS)
        # Cards stack the teams so a long name cannot break mid-word.
        self.assertIn('.glance-card-teams{display:block;overflow-wrap:break-word;word-break:normal', CSS)
        # The two tap targets stay a full-size row.
        self.assertRegex(CSS, r'\.fresh-links a\{min-height:44px|\.fresh-strip \.fresh-links a\{min-height:44px')
        # The browser-computed age line stays readable on a phone (session
        # 138cbedd added it after this layout); only the static timestamps fold.
        self.assertIn('body[data-page="index"] .fresh-strip .fresh-main>strong,', CSS)
        self.assertNotIn('body[data-page="index"] .fresh-strip .fresh-main{display:none}', CSS)
        # Desktop keeps its own order and its panel chrome.
        self.assertIn('.fresh-strip .fresh-next{order:2}', CSS)
        self.assertNotIn('@media(min-width:651px){body[data-page="index"] #picks-at-a-glance{background:transparent', CSS)

    def test_duplicated_phone_guide_is_gone_but_the_facts_remain(self):
        text = self.soup.get_text(' ', strip=True)
        self.assertEqual(text.count('the bottom bar has'), 1)
        self.assertEqual(text.count('15-minute schedule'), 1)
        self.assertIn('90 minutes old', text)

    def test_strip_counts_and_actions_are_unchanged(self):
        strip = self.soup.select_one('#freshness-strip')
        self.assertIsNotNone(strip.select_one('a.fresh-cta[href="picks.html"]'))
        self.assertIsNotNone(strip.select_one('[data-count="open"]'))
        self.assertIsNotNone(strip.select_one('[data-count="picked"]'))
        self.assertIsNotNone(strip.select_one('[data-count="priced"]'))
        self.assertEqual(int(strip.select_one('[data-count="open"]').get_text()),
                         len(self.opens))


class CoverageBoundaryTests(unittest.TestCase):
    """The rule set that explains matches a pick cannot be issued for."""

    @classmethod
    def setUpClass(cls):
        cls.soup = BeautifulSoup(build.unresolved_page_intro(copy.deepcopy(DATA)), 'html.parser')

    def test_boundary_section_names_all_three_cases_with_official_links(self):
        section = self.soup.select_one('#coverage-boundary')
        self.assertIsNotNone(section)
        text = section.get_text(' ', strip=True)
        self.assertIn('TBD', text)
        self.assertIn('Lock or start already passed', text)
        self.assertIn('Present in one Hotspawn view', text)
        hrefs = {a['href'] for a in section.select('a')}
        self.assertIn('https://www.hotspawn.com/counter-strike/matches', hrefs)
        self.assertIn('https://play.hotspawn.com/cs2-pickems', hrefs)
        self.assertIn('https://play.hotspawn.com/lobby', hrefs)
        self.assertTrue(any(u.startswith('https://phpstack-1372681-6459848')
                            and 'api/v1/fixtures' in u for u in hrefs))

    def test_boundary_renders_no_fixture_rows(self):
        # One rendered row per fixture is a validator invariant; this section is
        # prose + an explanatory table only.
        self.assertEqual(self.soup.select('#coverage-boundary tr[data-match]'), [])

    def test_the_summary_links_to_the_boundary(self):
        html = build.overview(copy.deepcopy(DATA))
        self.assertIn('unresolved.html#coverage-boundary', html)
        self.assertIn('Matches that can never carry a pick', html)


class LiveCoverageAuditTests(unittest.TestCase):
    """scripts.audit_f89bb1f8 must pass the real board and reject corruptions."""

    def test_published_board_passes_and_reports_full_coverage(self):
        failures, audit = audit_f89bb1f8.audit(copy.deepcopy(DATA), CLOCK)
        self.assertEqual(failures, [])
        self.assertEqual(audit['future_rows'], audit['future_with_pick'])
        self.assertEqual(audit['future_unresolved'], 0)
        # A refresh may legitimately add or remove source fixtures. Pin the
        # audit to this snapshot's measured inventory, not a permanent count.
        expected = len(DATA['matches'])
        self.assertEqual(audit['rows'], expected)
        self.assertEqual(audit['counts'], {'api': expected, 'page': expected, 'lobby': expected})

    def test_every_future_row_carries_a_probability_or_is_labelled_research(self):
        _, audit = audit_f89bb1f8.audit(copy.deepcopy(DATA), CLOCK)
        self.assertEqual(audit['future_priced'] + audit['future_research_only'],
                         audit['future_rows'])

    def _first_future(self, data):
        return next(m for m in data['matches']
                    if m.get('state') == 'open' and m.get('pick') and m.get('probabilities'))

    def test_a_dropped_pick_fails(self):
        data = copy.deepcopy(DATA)
        row = self._first_future(data)
        row['pick'] = None
        row['probabilities'] = None
        row['method'] = None
        row.pop('reason', None)
        row['attempts'] = []
        failures, _ = audit_f89bb1f8.audit(data, CLOCK)
        self.assertTrue(any('no published reason' in f for f in failures), failures)
        self.assertTrue(any('lists no attempted source' in f for f in failures), failures)

    def test_an_unresolved_row_without_an_https_attempt_fails(self):
        data = copy.deepcopy(DATA)
        row = self._first_future(data)
        row.update({'pick': None, 'probabilities': None, 'method': None,
                    'reason': 'No price found.', 'attempts': [{'provider': 'X', 'url': 'http://insecure'}]})
        failures, _ = audit_f89bb1f8.audit(data, CLOCK)
        self.assertTrue(any('no official https source' in f for f in failures), failures)

    def test_a_market_row_blanked_without_a_reason_is_still_caught(self):
        # The real price attempts are retained, so only the missing limitation is
        # new: the audit must report exactly that and nothing invented.
        data = copy.deepcopy(DATA)
        row = self._first_future(data)
        row['pick'] = None
        row['probabilities'] = None
        row['method'] = None
        row.pop('reason', None)
        failures, audit = audit_f89bb1f8.audit(data, CLOCK)
        self.assertEqual(failures, ['%s: unresolved row carries no published reason' % row['id']])
        self.assertEqual(audit['future_unresolved'], 1)

    def test_a_pick_outside_the_two_teams_fails(self):
        data = copy.deepcopy(DATA)
        self._first_future(data)['pick'] = 'Nobody'
        failures, _ = audit_f89bb1f8.audit(data, CLOCK)
        self.assertTrue(any('not one of the two teams' in f for f in failures), failures)

    def test_probabilities_that_do_not_sum_to_one_fail(self):
        data = copy.deepcopy(DATA)
        row = self._first_future(data)
        row['probabilities'] = [0.9, 0.9]
        failures, _ = audit_f89bb1f8.audit(data, CLOCK)
        self.assertTrue(any('do not sum to 1' in f for f in failures), failures)

    def test_a_future_row_marked_not_open_fails(self):
        data = copy.deepcopy(DATA)
        self._first_future(data)['state'] = 'not_open'
        failures, _ = audit_f89bb1f8.audit(data, CLOCK)
        self.assertTrue(any('future fixture is not open' in f for f in failures), failures)

    def test_a_source_count_that_disagrees_with_the_retained_rows_fails(self):
        data = copy.deepcopy(DATA)
        data['coverage_counts']['lobby'] = 94
        failures, _ = audit_f89bb1f8.audit(data, CLOCK)
        self.assertTrue(any('coverage_counts.lobby' in f for f in failures), failures)

    def test_an_expired_snapshot_fails(self):
        data = copy.deepcopy(DATA)
        data['fixtures_observed_at'] = '2026-10-01T00:00:00Z'
        failures, _ = audit_f89bb1f8.audit(data, CLOCK)
        self.assertTrue(any('8-hour evidence window' in f for f in failures), failures)

    def test_audit_never_reads_the_hotspawn_crowd_percentage(self):
        source = (ROOT / 'scripts/audit_f89bb1f8.py').read_text()
        self.assertNotIn('picked_percent', source.replace('participants*_picked_percent', ''))


class InventoryRecordTests(unittest.TestCase):
    """The dated live-inventory record must keep its sources and its numbers."""

    def test_record_exists_and_states_the_three_views(self):
        record = (ROOT / 'research/session-f89bb1f8/LIVE-INVENTORY-2026-10-23.md').read_text()
        for url in ('https://play.hotspawn.com/lobby',
                    'https://play.hotspawn.com/cs2-pickems',
                    'https://www.hotspawn.com/counter-strike/matches',
                    'https://www.hltv.org/events/9435/macemedia-void-autumn-cup-2026',
                    'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures'):
            self.assertIn(url, record)
        self.assertIn('94', record)
        self.assertIn('92', record)
        self.assertIn('TBD', record)


if __name__ == '__main__':
    unittest.main()
