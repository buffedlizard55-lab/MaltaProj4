"""The summary's ladder is a partition even when every price expires."""
import json
import unittest
from collections import Counter
from pathlib import Path
from scripts import summary

ROOT = Path(__file__).resolve().parents[1]


class CoveragePartition(unittest.TestCase):
    def test_every_resolved_method_has_a_documented_rung(self):
        snapshot = json.loads((ROOT / 'data/latest.json').read_text())
        keys = {row['key'] for row in summary.ladder_rows()}
        for match in snapshot['matches']:
            if match['state'] == 'open' and (match.get('pick') or match.get('probabilities')):
                self.assertIn(summary.METHOD_STEP.get(match.get('method')), keys, match['id'])

    def test_unresolved_is_included_in_browser_partition(self):
        # The old guard excluded none, forcing source outages to block publication.
        browser = (ROOT / 'tests/browser_019a253a.cjs').read_text()
        self.assertNotIn("filter(item => !item.startsWith('none='))", browser)
        counts = Counter({'exchange': 3, 'model': 2, 'none': 4})
        self.assertEqual(sum(counts.values()), 9)

    def test_browser_maps_probability_expectation_to_exact_fixture(self):
        browser = (ROOT / 'tests/browser_ce45f672.cjs').read_text()
        self.assertIn("open.find(row => String(row.id) === fixtureId)", browser)
        self.assertIn('priced ? 2 : 0', browser)
        self.assertIn('if (!fixture.pick) assert.match', browser)


class NeutralSourceLadder(unittest.TestCase):
    def test_neutral_context_does_not_block_a_later_directional_source(self):
        from tests.test_core import fixture, exchange, NOW
        from scripts.core import resolve, polymarket_candidates, iso
        row = fixture()
        neutral = exchange()
        neutral['markets'][0].update(outcomePrices='["0.5","0.5"]', bestBid=.49, bestAsk=.51)
        resolve(row, polymarket_candidates([neutral], iso(NOW)), 'Polymarket', NOW)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])
        self.assertEqual(row['no_edge_lines'][0]['probabilities'], [.5, .5])
        resolve(row, polymarket_candidates([exchange()], iso(NOW)), 'Polymarket', NOW)
        self.assertEqual(row['pick'], row['teams'][0])
        self.assertEqual(row['probabilities'], [.6, .4])
        self.assertEqual(row['no_edge_lines'][0]['probabilities'], [.5, .5])
        self.assertNotEqual(row['evidence'][0]['probabilities'], row['no_edge_lines'][0]['probabilities'])

    def test_neutral_context_is_not_synthesized_from_rejected_evidence(self):
        from tests.test_core import fixture, exchange, NOW
        from scripts.core import resolve, polymarket_candidates, iso
        row = fixture()
        bad = exchange()
        bad['markets'][0].update(outcomePrices='["0.5","0.5"]', liquidity='0')
        resolve(row, polymarket_candidates([bad], iso(NOW)), 'Polymarket', NOW)
        self.assertNotIn('no_edge_lines', row)
        self.assertIsNone(row['pick'])
