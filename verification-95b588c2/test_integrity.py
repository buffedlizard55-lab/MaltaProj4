"""Independent integrity regressions; hypothetical mutations never enter production.

Run from the implementation root after installing requirements:
  python /path/to/verification-95b588c2/test_integrity.py
The audited baseline has failures. They are genuine acceptance failures, not
expectedFailure decorations. The integrator should fix its owned files.
"""
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from scripts.core import dt, quote_polymarket
from scripts.validate import validate_data


class IntegrityAcceptance(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path('data/latest.json').read_text())
        self.match = next(m for m in self.data['matches'] if m['method'] == 'exchange')
        self.q = self.match['evidence'][0]

    def test_baseline_arithmetic_and_membership(self):
        result = validate_data(self.data)
        self.assertEqual(result['rows_verified_against_primary_snapshot'], len(self.data['matches']))

    def test_nonfinite_liquidity_rejected(self):
        q = copy.deepcopy(self.q)
        q['market'] = q['raw']
        q['prices'] = list(map(float, json.loads(q['raw']['outcomePrices'])))
        q['teams'] = q['source_teams']
        for value in ('NaN', 'Infinity'):
            with self.subTest(value=value):
                q['market']['liquidity'] = value
                with self.assertRaises((ValueError, TypeError)):
                    quote_polymarket(q, [0, 1], dt(self.data['generated_at']))

    def test_validator_binds_raw_outcomes_to_identity(self):
        # Not a real source observation. A corrupted raw source record must fail.
        self.q['raw']['outcomes'] = json.dumps(['AUDIT_ONLY_TEAM_A', 'AUDIT_ONLY_TEAM_B'])
        with self.assertRaises((AssertionError, ValueError)):
            validate_data(self.data)

    def test_validator_enforces_two_sided_liquidity_gate(self):
        self.q['raw']['bestBid'] = 0.01
        self.q['raw']['bestAsk'] = 0.99
        self.q['raw']['liquidity'] = '1'
        with self.assertRaises((AssertionError, ValueError)):
            validate_data(self.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
