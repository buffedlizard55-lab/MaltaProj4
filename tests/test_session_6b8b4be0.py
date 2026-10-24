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
