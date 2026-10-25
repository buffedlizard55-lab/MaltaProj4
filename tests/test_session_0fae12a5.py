"""Session 0fae12a5 — full-coverage coherence + discoverability contracts.

What this module checks (all offline, against the committed snapshot/pages):

1. Every row's pick/probability/fair-odds triple is internally coherent:
   probabilities sum to 1, fair odds are exact reciprocals, and a set pick is
   the argmax of its own teams. Research/unresolved-shaped rows (pick with no
   percentage, or neither) are accepted as honest states -- this file pins
   invariants, never counts or tier labels, so a legitimate future refresh can
   never turn this gate red (cf. the 22-23 Oct 2026 deadlock).
2. Every published percentage replays from its own evidence: exchange rows from
   the market's two outcome prices (orientation-agnostic: labels, not positions),
   book rows from decimal-odds de-vigging, VRS rows from ``scripts.vrs`` with the
   row's own points.
3. Probability inputs come only from official/external line hosts; Hotspawn crowd
   data can never be a probability source, while every row keeps its Hotspawn
   inventory link.
4. The executive summary keeps in-site links to the updated picks, its separate
   unresolved/limitations section, and the phone layout (viewport + bottom tabs).

Run: python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

from scripts.vrs import calibrated, expected

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'latest.json'
INDEX_HTML = ROOT / 'index.html'
PAGES = ['index.html', 'picks.html', 'unresolved.html', 'matches.html', 'analysis.html']

# Hosts allowed to originate a win probability. Hotspawn pages/API are fixture
# inventory only and must never appear here; HLTV supplies identity/lineups.
LINE_HOSTS = {
    'polymarket.com',
    'gamma-api.polymarket.com',
    'github.com',  # Valve standings file behind the originated VRS line
    'raw.githubusercontent.com',
    'www.hltv.org',
    'hltv.org',  # dated Valve-ranking mirror behind model_vrs_mirror
    'egamersworld.com',
    'bo3.gg',
    'guest.api.arcadia.pinnacle.com',
}
HOTSPAWN_HOSTS = {
    'play.hotspawn.com',
    'www.hotspawn.com',
    'phpstack-1372681-6459848.cloudwaysapps.com',
}


def load_snapshot():
    with open(DATA, encoding='utf-8') as fh:
        return json.load(fh)


def norm_label(text):
    return re.sub(r'[^a-z0-9]+', '', str(text).lower())


class RowCoherenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matches = load_snapshot()['matches']

    def test_probabilities_sum_to_one_and_fair_odds_reciprocal(self):
        for m in self.matches:
            p, f = m.get('probabilities'), m.get('fair_odds')
            if p is None:
                self.assertIsNone(f, 'fair odds without probabilities on %s' % m['id'])
                continue
            self.assertEqual(len(p), 2, 'two-way probability on %s' % m['id'])
            self.assertAlmostEqual(p[0] + p[1], 1.0, places=9, msg=m['id'])
            self.assertTrue(all(0.0 < x < 1.0 for x in p), 'strictly inside (0,1): %s' % m['id'])
            self.assertIsNotNone(f, 'fair odds present when priced: %s' % m['id'])
            self.assertAlmostEqual(f[0], 1.0 / p[0], places=9, msg=m['id'])
            self.assertAlmostEqual(f[1], 1.0 / p[1], places=9, msg=m['id'])

    def test_pick_is_argmax_or_honest_blank(self):
        for m in self.matches:
            pick, teams, p = m.get('pick'), m.get('teams'), m.get('probabilities')
            if pick is None:
                # An honest blank: must say why (reason text or flags), never 50/50 filler.
                self.assertTrue(m.get('reason') or m.get('flags'),
                                'blank pick needs a reason/flag: %s' % m['id'])
                continue
            self.assertIn(pick, teams, 'pick from fixture teams: %s' % m['id'])
            if p is not None:
                winner = teams[0] if p[0] >= p[1] else teams[1]
                self.assertEqual(pick, winner, 'pick is argmax: %s' % m['id'])

    def test_research_shaped_rows_carry_no_percentage(self):
        for m in self.matches:
            method = (m.get('method') or '')
            if method.startswith('research'):
                self.assertIsNone(m.get('probabilities'), 'research tier has no %%: %s' % m['id'])
                self.assertIsNone(m.get('fair_odds'), 'research tier has no fair odds: %s' % m['id'])

    def test_open_rows_have_evidence_and_hotspawn_inventory_link(self):
        for m in self.matches:
            if m.get('state') != 'open':
                continue
            self.assertTrue(m.get('evidence'), 'open row needs evidence: %s' % m['id'])
            urls = [m.get('source_url', ''), m.get('feed_url', '')]
            urls += [s.get('url', '') for s in m.get('fixture_sources', [])]
            hosts = {urlparse(u).hostname for u in urls if u}
            self.assertTrue(hosts & HOTSPAWN_HOSTS,
                            'open row keeps a Hotspawn inventory link: %s' % m['id'])

    def test_probability_inputs_come_only_from_line_hosts(self):
        for m in self.matches:
            if not m.get('probabilities'):
                continue
            for e in m.get('evidence', []):
                host = urlparse(e.get('url', '')).hostname
                self.assertIn(host, LINE_HOSTS,
                              'probability input from an official line host: %s' % m['id'])
                self.assertNotIn(host, HOTSPAWN_HOSTS,
                                 'Hotspawn crowd data is never a probability: %s' % m['id'])


class CalculationReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matches = load_snapshot()['matches']

    def test_exchange_rows_replay_from_outcome_prices(self):
        for m in self.matches:
            if m.get('method') not in ('exchange', 'exchange_wide'):
                continue
            raw = m['evidence'][0]['raw']
            prices = [float(x) for x in json.loads(raw['outcomePrices'])]
            total = sum(prices)
            want = sorted(x / total for x in prices)
            got = sorted(m['probabilities'])
            self.assertEqual(len(want), 2, m['id'])
            for a, b in zip(want, got):
                self.assertAlmostEqual(a, b, places=9, msg='exchange replay: %s' % m['id'])

    def test_book_rows_replay_from_decimal_odds(self):
        for m in self.matches:
            if m.get('method') != 'bookmaker_fallback':
                continue
            odds = m['evidence'][0]['decimal_odds']
            q = [1.0 / float(o) for o in odds]
            total = sum(q)
            for a, b in zip([x / total for x in q], m['probabilities']):
                self.assertAlmostEqual(a, b, places=12, msg='book de-vig: %s' % m['id'])

    def test_vrs_rows_replay_from_valve_formula(self):
        for m in self.matches:
            if m.get('method') not in ('model_vrs', 'model_vrs_mirror'):
                continue
            ev = m['evidence'][0]
            raw = expected(ev['points'][0], ev['points'][1])
            self.assertAlmostEqual(raw, ev['raw_expected'][0], places=12,
                                   msg='VRS raw: %s' % m['id'])
            self.assertAlmostEqual(calibrated(raw), ev['probabilities'][0], places=12,
                                   msg='VRS calibrated: %s' % m['id'])
            self.assertAlmostEqual(calibrated(raw), m['probabilities'][0], places=12,
                                   msg='VRS published: %s' % m['id'])
            # Mirror scripts/validate.py validate_model_row: a checked roster
            # must satisfy Valve's 3-player continuity rule; an unchecked one
            # (no HLTV lineup available) is legitimate only when the Valve
            # label is unique, and the row must carry that limitation flag.
            # (Session 5bf6ae1b, 2026-10-25: fixture 1086697 rotated into the
            # unchecked shape and the old unconditional assertion went red on
            # valid, validator-passing data.)
            for check, count in zip(ev['roster_checks'], ev['label_counts']):
                if check['overlap'] is None:
                    self.assertEqual(count, 1,
                                     'unchecked VRS roster with duplicated label: %s' % m['id'])
                    self.assertIn('roster continuity not checked',
                                  ' '.join(m.get('flags') or []),
                                  'unchecked VRS roster not flagged: %s' % m['id'])
                else:
                    self.assertGreaterEqual(check['overlap'], 3,
                                            'Valve 3-player roster rule: %s' % m['id'])


class DiscoverabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = INDEX_HTML.read_text(encoding='utf-8')

    def test_executive_summary_links_to_updated_picks(self):
        for target in ('picks.html', 'unresolved.html', 'matches.html',
                       '#picks-at-a-glance', '#unresolved-summary'):
            self.assertIn(target, self.index, 'summary links to %s' % target)

    def test_summary_anchors_exist(self):
        for anchor in ('id="picks-at-a-glance"', 'id="unresolved-summary"',
                       'id="pick-limitations"', 'id="coverage"'):
            self.assertIn(anchor, self.index, 'anchor present: %s' % anchor)

    def test_separate_unresolved_and_limitations_section(self):
        self.assertIn('id="unresolved-picks"', self.index)
        body = self.index.split('id="pick-limitations"')[1].split('</section>')[0]
        self.assertGreaterEqual(body.count('<li>'), 5, 'limitation catalogue is substantive')
        for phrase in ('No book lists the match', 'never 50/50', 'never used'):
            self.assertIn(phrase, self.index)

    def test_phone_layout_on_main_pages(self):
        for page in PAGES:
            html = (ROOT / page).read_text(encoding='utf-8')
            self.assertIn('name="viewport"', html, 'viewport: %s' % page)
            tabs = re.search(r'<nav class="mobile-tabs".*?</nav>', html, re.S)
            self.assertIsNotNone(tabs, 'phone tab bar: %s' % page)
            for tab in ('Home', 'Picks', 'Unresolved', 'Matches', 'Analysis'):
                self.assertIn(tab, tabs.group(0), '%s tab on %s' % (tab, page))


if __name__ == '__main__':
    unittest.main()
