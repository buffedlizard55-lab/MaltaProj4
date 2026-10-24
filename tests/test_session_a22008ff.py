"""Session a22008ff — the contracts this session changed, pinned.

What was measured, and why these tests exist
--------------------------------------------
1. **A published row is either picked or explicitly unresolved.** On the
   2026-10-24T16:28Z refresh one open fixture (Color vs ex-Zero Tenacity,
   fixture 1079200) was stored as ``probabilities = [0.5, 0.5]`` with
   ``pick = None`` because its Polymarket line was *exactly* even. No coverage
   contract in this repository allows that shape ("priced but unpicked", "open
   with probability" > "open with pick"), so the publish rehearsal reported 42
   failures and 3 errors, and `main`'s publisher refused every refresh at its
   root-fallback gate (runs 40084520702, 40082763751, 40097410704 — all
   annotated "The staged root failed its own validator or unit gate").
   An even line is a real observation, so it is now kept as
   ``even_market_line`` (published with its operator link) and the ladder
   continues to the originated model / research tiers.

2. **Two live-fixture tests inside the publish gate were rotation-coupled.**
   `test_session_35c6e1e9` pinned fixture 1083121 and `test_session_e9be3e6b`
   pinned 1082859/1081152 out of the rotating snapshot; Hotspawn rotated them
   out, so the gate went red for reasons unrelated to what those tests prove.
   They now find their subject by property and fall back to a retained dated
   archive, failing loudly when no retained row qualifies.

3. **The executive summary must answer "where are the picks?" on a phone.**
   The compact summary row is measured in `research/measure_a22008ff.json`;
   these tests pin its links, its position before the list and its counts.

Nothing here is skipped when data is missing: a missing property fails.
"""
import json
import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.core import polymarket_candidates, resolve

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
NOW = datetime(2026, 10, 24, 16, 40, tzinfo=timezone.utc)


def fixture():
    from tests.test_session_92e3275c import fixture as proven_fixture
    return proven_fixture()


def market_event(**event):
    from tests.test_session_92e3275c import market_event as proven_event
    return proven_event(**event)


class EvenLineIsNeverAPricedUnpickedRow(unittest.TestCase):
    """Contract 1: the shape that held the publisher red cannot come back."""

    OBSERVED = '2026-10-24T16:30:00Z'

    def resolve(self, prices, bid, ask):
        row = fixture()
        resolve(row, polymarket_candidates(
            [market_event(prices=prices, bid=bid, ask=ask, updated=self.OBSERVED)],
            self.OBSERVED), 'Polymarket', NOW, relax=True)
        return row

    def resolve_even(self):
        return self.resolve(('0.5', '0.5'), '0.49', '0.51')

    def test_an_even_line_publishes_no_probability(self):
        row = self.resolve_even()
        self.assertIsNone(row['probabilities'], 'an even line must not be stored as the row price')
        self.assertIsNone(row['fair_odds'])
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])

    def test_the_even_line_is_retained_as_an_observation_with_its_source(self):
        line = self.resolve_even()['even_market_line']
        self.assertEqual(line['probabilities'], [0.5, 0.5])
        self.assertEqual(line['fair_odds'], [2.0, 2.0])
        self.assertTrue(line['url'].startswith('https://gamma-api.polymarket.com/'), line['url'])
        self.assertIn('cannot', line['note'])

    def test_the_attempt_says_why_and_the_ladder_may_continue(self):
        row = self.resolve_even()
        last = row['attempts'][-1]
        self.assertEqual(last['status'], 'unresolved')
        self.assertIn('no directional edge', last['reason'].lower())
        self.assertTrue(last['url'].startswith('https://'))

    def test_a_directional_line_is_unchanged(self):
        row = self.resolve(('0.62', '0.38'), '0.61', '0.63')
        self.assertEqual(row['pick'], row['teams'][0])
        self.assertEqual(row['method'], 'exchange')
        self.assertNotIn('even_market_line', row)

    def test_no_committed_row_is_priced_without_a_pick(self):
        problems = []
        for m in SNAPSHOT['matches']:
            if m.get('state') != 'open':
                continue
            if m.get('probabilities') is not None and not m.get('pick'):
                problems.append(m['id'])
            if m.get('probabilities') is None and m.get('method'):
                problems.append(m['id'] + ' (method without a price)')
        self.assertEqual(problems, [], 'priced-but-unpicked or method-without-price rows')

    def test_every_even_observation_on_the_board_keeps_a_source(self):
        for m in SNAPSHOT['matches']:
            line = m.get('even_market_line')
            if not line:
                continue
            self.assertTrue(str(line.get('url', '')).startswith('https://'), m['id'])
            self.assertEqual(len(line.get('probabilities') or []), 2, m['id'])
            self.assertAlmostEqual(sum(line['probabilities']), 1, places=9, msg=m['id'])


class RotationProofLiveFixtureTests(unittest.TestCase):
    """Contract 2: a rotated-out fixture must not redden the publish gate."""

    def test_the_alias_contract_finds_its_subject_by_property(self):
        source = (ROOT / 'tests/test_session_35c6e1e9.py').read_text()
        self.assertIn('def alias_bearing_row', source)
        self.assertNotIn("m['id'] == '1083121')", source)
        self.assertIn('ALIAS_ARCHIVES', source)

    def test_the_ladder_arithmetic_replay_falls_back_to_a_retained_capture(self):
        source = (ROOT / 'tests/test_session_e9be3e6b.py').read_text()
        self.assertIn('def rows_by_id', source)
        self.assertIn('ARCHIVE', source)
        archive = ROOT / 'research/harvest-d2b90de7/snapshot.json'
        self.assertTrue(archive.exists(), 'the retained archive the fallback reads is missing')
        archived = {m['id'] for m in json.loads(archive.read_text())['matches']}
        self.assertTrue({'1082859', '1081152'}.issubset(archived), 'archive lost the replay rows')

    def test_the_fallbacks_never_pass_by_skipping(self):
        for relative in ('tests/test_session_35c6e1e9.py', 'tests/test_session_e9be3e6b.py'):
            source = (ROOT / relative).read_text()
            for marker in ('self.skipTest(', '@unittest.skip', 'skipUnless', 'skipIf'):
                self.assertNotIn(marker, source,
                                 '%s weakens the gate with %s' % (relative, marker))


class ExecutiveSummaryRoutesAPhoneToThePicks(unittest.TestCase):
    """Contract 3: the answer to "where are the picks?" is on the first screen."""

    @classmethod
    def setUpClass(cls):
        from scripts.build import exec_summary_bar, exec_summary_quicknav
        cls.data = json.loads(json.dumps(SNAPSHOT))
        cls.index = (ROOT / 'index.html').read_text()
        cls.generated = exec_summary_quicknav(cls.data) + exec_summary_bar(cls.data)
        cls.soup = BeautifulSoup(cls.generated, 'html.parser')

    def test_the_compact_summary_links_the_updated_pick_list_in_site(self):
        quick = self.soup.select_one('#exec-quicknav')
        self.assertIsNotNone(quick)
        hrefs = [a.get('href') for a in quick.select('a')]
        self.assertIn('picks.html', hrefs)
        self.assertIn('#unresolved-limits', hrefs)
        self.assertTrue(all(not h.startswith(('http://', 'https://')) for h in hrefs), hrefs)

    def test_the_compact_summary_ends_above_the_fixed_tab_bar_on_a_phone(self):
        # Visual order, not DOM order: the summary row is CSS-ordered onto the
        # first screen. research/measure_a22008ff.json is the Chromium receipt.
        measured = json.loads((ROOT / 'research/measure_a22008ff.json').read_text())
        for size in ('320x568', '390x844', '412x915'):
            row = measured[size]
            self.assertLess(row['quicknav']['y'] + row['quicknav']['h'], row['mobileTabs']['y'], size)

    def test_the_full_summary_bar_also_routes_to_every_pick_surface(self):
        bar = self.soup.select_one('#exec-summary')
        self.assertIsNotNone(bar)
        hrefs = [a.get('href') for a in bar.select('a')]
        for needed in ('picks.html', 'unresolved.html', 'matches.html', 'review.html'):
            self.assertIn(needed, hrefs)

    def test_the_summary_states_the_freshness_window_from_the_snapshot(self):
        hours = SNAPSHOT['stale_after_hours']
        self.assertIn('%s h freshness window' % hours, self.generated)
        self.assertIn(':04 · :19 · :34 · :49 UTC', self.generated)

    def test_the_committed_home_page_carries_both_summary_routes(self):
        self.assertIn('id="exec-quicknav"', self.index)
        self.assertIn('id="exec-summary"', self.index)

    def test_every_phone_tab_target_exists_as_a_page(self):
        tabs = BeautifulSoup(self.index, 'html.parser').select('.mobile-tabs a')
        self.assertGreaterEqual(len(tabs), 5)
        for tab in tabs:
            self.assertTrue((ROOT / tab['href']).exists(), tab['href'])

    def test_the_measured_mobile_geometry_is_recorded(self):
        path = ROOT / 'research/measure_a22008ff.json'
        self.assertTrue(path.exists(), 'the phone measurement receipt is missing')
        measured = json.loads(path.read_text())
        for size in ('320x568', '390x844'):
            self.assertIn(size, measured)
            self.assertFalse(measured[size]['overflow'], size)
            self.assertLess(measured[size]['quicknav']['y'] + measured[size]['quicknav']['h'],
                            measured[size]['mobileTabs']['y'],
                            'the summary row must end above the fixed tab bar at ' + size)


class EveryFeedRowIsAccountedFor(unittest.TestCase):
    """The brief: every match Hotspawn lists is on the board, priced or explained."""

    def test_the_snapshot_is_internally_consistent(self):
        rows = SNAPSHOT['matches']
        self.assertEqual(len(rows), len({m['id'] for m in rows}), 'duplicate fixture id')
        for m in rows:
            self.assertTrue(m['source_url'].startswith('https://'), m['id'])
            if m.get('state') == 'open':
                priced = m.get('probabilities') is not None
                picked = bool(m.get('pick'))
                self.assertTrue(priced or picked or (m.get('reason') or m.get('attempts')),
                                '%s is neither priced, picked nor explained' % m['id'])
                if priced:
                    self.assertEqual(len(m['probabilities']), 2, m['id'])
                    self.assertAlmostEqual(sum(m['probabilities']), 1, places=9, msg=m['id'])
                    self.assertIn(m['pick'], m['teams'], m['id'])
                    self.assertEqual(m['pick'], m['teams'][0] if m['probabilities'][0] > m['probabilities'][1]
                                     else m['teams'][1], m['id'])

    def test_the_unresolved_section_renders_even_when_nothing_is_unresolved(self):
        self.assertIn('id="unresolved-picks"', (ROOT / 'index.html').read_text())
        self.assertIn('id="unresolved-limits"', (ROOT / 'index.html').read_text())

    def test_hotspawn_is_never_the_probability_source(self):
        for m in SNAPSHOT['matches']:
            for record in m.get('evidence') or []:
                urls = [record.get('api_url'), record.get('url')]
                urls += [r.get('url') for r in record.get('source_receipts') or []]
                for url in [u for u in urls if u]:
                    self.assertNotIn('hotspawn', url.lower(), m['id'])


if __name__ == '__main__':
    unittest.main()
