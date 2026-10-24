"""Session ce45f672: every-match pick integrity plus the phone-first summary.

What this session had to prove
------------------------------
1. The independent re-derivation accepts a team label that differs between
   Hotspawn and the exchange **only** when the row's own evidence carries an
   ``identity_sources`` record naming both labels with an https primary source.
   An undocumented label difference is still refused, so the published board
   keeps its no-guessing contract.
2. The shipped stylesheet is the canonical one: identical bytes, balanced
   blocks. An unclosed media block silently gates every later phone rule, which
   is exactly what shipped before this session.
3. The home page opens with an executive summary that names itself and links to
   the updated picks, the unresolved section and the rest of the board — the
   in-site routes a phone reader needs.
4. Every open match on the published board carries a pick and a probability, or
   is listed in the separate unresolved section with its limitation, and no row
   prints a default 50/50.
"""
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.build import overview

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
CSS = (ROOT / 'assets' / 'style.css').read_text()
INDEX = overview(json.loads(json.dumps(SNAPSHOT)))


def load_verifier():
    spec = importlib.util.spec_from_file_location(
        'verify_0cc1138a_ce45f672', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_verifier()

LABELS = ['Tropa do KinGui', 'MEIA NOITE']
PRICES = [0.615, 0.385]
HOTSPAWN_TEAMS = ['Projeto do KinGui', 'MEIA NOITE']


def evidence(**overrides):
    record = {'provider': 'Polymarket',
              'raw': {'outcomes': json.dumps(LABELS), 'outcomePrices': json.dumps(PRICES)},
              'identity_sources': [{
                  'canonical': 'Tropa do KinGui',
                  'names': ['Tropa do KinGui', 'Projeto do KinGui', 'ex-Keyd Stars'],
                  'source': 'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7',
                  'additional_source': 'https://gamma-api.polymarket.com/markets/6033256',
                  # The re-derivation requires a written basis on the evidence
                  # record AND the same pair inside the committed registry.
                  'basis': ('Fixture parity and a five-for-five active roster between HLTV match 2399904 and the '
                            'Polymarket listing, recorded in data/identities.json by session 9f3e77d2.'),
              }]}
    record.update(overrides)
    return record


class AliasAwareReDerivation(unittest.TestCase):
    """A label difference is accepted only with a source-linked identity record."""

    def test_a_source_linked_alias_is_mapped_onto_the_fixture_order(self):
        probabilities, kind = V.evidence_probabilities(evidence(), HOTSPAWN_TEAMS)
        self.assertEqual(kind, 'exchange_mid')
        self.assertAlmostEqual(probabilities[0], 0.615, places=12)
        self.assertAlmostEqual(probabilities[1], 0.385, places=12)

    def test_an_undocumented_label_difference_is_still_refused(self):
        record = evidence()
        record.pop('identity_sources')
        with self.assertRaises(ValueError):
            V.evidence_probabilities(record, HOTSPAWN_TEAMS)

    def test_an_identity_record_without_an_https_source_is_refused(self):
        record = evidence()
        record['identity_sources'][0]['source'] = 'http://insecure.example/team'
        with self.assertRaises(ValueError):
            V.evidence_probabilities(record, HOTSPAWN_TEAMS)

    def test_an_alias_outside_the_committed_register_is_refused(self):
        record = evidence()
        record['identity_sources'][0]['names'] = ['Tropa do KinGui', 'Some Other Club']
        with self.assertRaises(ValueError):
            V.evidence_probabilities(record, ['Some Other Club', 'MEIA NOITE'])

    def test_an_identity_record_without_a_written_basis_is_refused(self):
        record = evidence()
        record['identity_sources'][0].pop('basis')
        with self.assertRaises(ValueError):
            V.evidence_probabilities(record, HOTSPAWN_TEAMS)

    def test_an_identity_record_naming_only_one_side_is_refused(self):
        record = evidence()
        record['identity_sources'][0]['names'] = ['Projeto do KinGui', 'Some Other Club']
        with self.assertRaises(ValueError):
            V.evidence_probabilities(record, HOTSPAWN_TEAMS)

    def test_the_two_teams_may_never_share_one_source_outcome(self):
        record = evidence()
        record['identity_sources'][0]['names'] = ['Tropa do KinGui', 'Projeto do KinGui', 'MEIA NOITE']
        with self.assertRaises(ValueError):
            V.evidence_probabilities(record, HOTSPAWN_TEAMS)

    def test_every_published_open_row_still_reproduces(self):
        rows = V.audit(SNAPSHOT)
        failures = [row for row in rows if row['problems']]
        self.assertEqual(failures, [], 'unreproducible: %r' % failures[:3])
        for row in rows:
            if row['published']:
                self.assertIsNotNone(row['re_derived'], row['id'])


class ShippedStylesheet(unittest.TestCase):
    def test_the_shipped_copy_is_the_canonical_copy(self):
        canonical = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        self.assertEqual(canonical, CSS)

    def test_the_shipped_copy_has_balanced_blocks(self):
        self.assertEqual(CSS.count('{'), CSS.count('}'),
                         'an unclosed block gates every later phone rule')

    def test_the_phone_summary_rules_are_inside_a_closed_block(self):
        # The label and the card time rule must not be swallowed by an earlier
        # unclosed media query: prove they parse by brace depth at their offset.
        depth = 0
        found = {}
        for match in re.finditer(r'[{}]|\.glance-card-meta\s+\.glance-card-time\b|body\[data-page="index"\]\s+\.glance-card-mobile\b', CSS):
            token = match.group(0)
            if token == '{':
                depth += 1
            elif token == '}':
                depth -= 1
            else:
                found[re.sub(r'\s+', ' ', token.strip())] = depth
        # The card's time-in-meta rule is top level; the index-only density rules
        # sit one block deep inside their media query, never swallowed by an
        # earlier unclosed block (which is what shipped before this session).
        self.assertEqual(found.get('.glance-card-meta .glance-card-time'), 0)
        self.assertEqual(found.get('body[data-page="index"] .glance-card-mobile'), 1)


class ExecutiveSummaryRoutes(unittest.TestCase):
    def setUp(self):
        self.soup = BeautifulSoup(INDEX, 'html.parser')

    def test_the_phone_summary_names_itself_an_executive_summary(self):
        # The on-phone label is the compact quick nav above the strip; it was
        # added in main by session 4ed657ce and this session keeps it as the
        # phone's "you are looking at the executive summary" marker.
        line = self.soup.select_one('#exec-quicknav .exec-quicknav-line')
        self.assertIsNotNone(line)
        self.assertTrue(line.get_text(' ', strip=True).startswith('Executive summary'))

    def test_the_first_screen_links_to_the_picks_and_the_unresolved_section(self):
        strip = self.soup.select_one('#freshness-strip')
        hrefs = {a.get('href') for a in strip.select('a[href]')}
        self.assertIn('picks.html', hrefs)
        self.assertIn('unresolved.html', hrefs)

    def test_the_executive_summary_bar_links_every_in_site_route(self):
        bar = self.soup.select_one('#exec-summary')
        self.assertIsNotNone(bar)
        hrefs = {a.get('href') for a in bar.select('a[href]')}
        for target in ('picks.html', 'unresolved.html', 'matches.html', 'review.html'):
            self.assertIn(target, hrefs)

    def test_the_summary_carries_the_unresolved_section_with_its_limitations(self):
        self.assertIsNotNone(self.soup.select_one('#unresolved-limits'))
        self.assertIsNotNone(self.soup.select_one('#unresolved-summary'))
        limitations = self.soup.select_one('#unresolved-limits')
        self.assertIn('limitation', limitations.get_text(' ', strip=True).lower())

    def test_every_open_row_has_a_pick_or_a_published_reason(self):
        cards = {a['href'].rsplit('-', 1)[-1]: a
                 for a in self.soup.select('#picks-at-a-glance a.glance-card-mobile')}
        for match in [m for m in SNAPSHOT['matches'] if m['state'] == 'open']:
            card = cards[match['id']]
            text = card.get_text(' ', strip=True)
            self.assertNotIn('50/50', text, match['id'])
            if match['pick'] and match['probabilities']:
                self.assertEqual(card.get('data-glance-priced'), '1', match['id'])
                self.assertIn(match['pick'], text, match['id'])
            elif match['pick']:
                self.assertEqual(card.get('data-glance-research'), '1', match['id'])
            else:
                self.assertEqual(card.get('data-glance-priced'), '0', match['id'])
                self.assertIn('No percentage', text, match['id'])
                self.assertTrue(match.get('reason'), match['id'])


class EvenWideQuoteNeverBecomesA50Fifty(unittest.TestCase):
    """A flat midpoint inside the wide tier must not stop the ladder.

    ``scripts.core.resolve`` used to publish the midpoint of a spread that had
    already failed the strict ceiling. On the 2026-10-24T07:09Z harvest that
    produced fixture 1083122 (LOS NINOS vs BORRACHEIROS) as an uninformative
    0.500/0.500 with no pick, and because the row then had probabilities it never
    reached the model or research tiers that could have originated a pick.
    """

    def setUp(self):
        from tests.test_session_92e3275c import fixture, market_event, NOW
        self.fixture = fixture
        self.market_event = market_event
        self.now = NOW

    def _resolve(self, **event):
        from scripts.core import polymarket_candidates, resolve
        row = self.fixture()
        resolve(row, polymarket_candidates([self.market_event(**event)],
                                           '2026-10-22T08:06:00Z'), 'Polymarket', self.now, relax=True)
        return row

    def test_an_even_wide_midpoint_is_rejected_as_evidence(self):
        row = self._resolve(prices=('0.5', '0.5'), bid='0.24', ask='0.76')
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])
        self.assertEqual(row['attempts'][0]['status'], 'unresolved')
        self.assertIn('exactly even', row['attempts'][0]['reason'])
        self.assertIn('rejected_quote', row['attempts'][0])
        self.assertEqual(row['attempts'][0]['rejected_quote']['notice'],
                         'Rejected evidence, not a pick or verified probability.')

    def test_a_directional_wide_quote_still_publishes_its_real_spread(self):
        row = self._resolve(prices=('0.75', '0.25'), bid='0.54', ask='0.96')
        self.assertEqual(row['method'], 'exchange_wide')
        self.assertEqual(row['pick'], row['teams'][0])
        self.assertAlmostEqual(row['probabilities'][0], 0.75, places=12)
        self.assertTrue(any('wide' in flag.lower() for flag in row['flags']))

    def test_a_tight_even_market_continues_to_the_next_research_rung(self):
        row = self._resolve(prices=('0.5', '0.5'), bid='0.49', ask='0.51')
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])
        self.assertIn('exactly even', row['attempts'][0]['reason'])
        self.assertIn('rejected_quote', row['attempts'][0])

    def test_the_published_board_never_stops_on_a_priced_row_without_a_pick(self):
        for match in [m for m in SNAPSHOT['matches'] if m['state'] == 'open']:
            if match.get('probabilities'):
                self.assertIn(match.get('pick'), match['teams'], match['id'])
                self.assertGreaterEqual(abs(match['probabilities'][0] - match['probabilities'][1]), 1e-4, match['id'])


if __name__ == '__main__':
    unittest.main()
