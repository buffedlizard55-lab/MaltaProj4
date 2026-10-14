import copy
import json
import math
import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from collect import (parse_hotspawn, parse_rankings, parse_time, pair_normalize, no_vig,
                     rating_probability, matching_market, assemble, norm)

NOW = datetime(2026, 10, 14, 4, 0, tzinfo=timezone.utc)


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.row = {'teams': ['Team A', 'Team B'], 'start_at': '2026-10-14T08:00:00Z'}
        self.market = {'id':'123', 'outcomes':'["Team B", "Team A"]', 'outcomePrices':'["0.3", "0.7"]',
                       'sportsMarketType':'moneyline', 'active':True, 'closed':False, 'acceptingOrders':True,
                       'gameStartTime':'2026-10-14 08:00:00+00', 'updatedAt':'2026-10-14T03:59:00Z', 'liquidityNum':2000}
        self.event = {'id':'test', 'slug':'cs2-test', 'markets':[self.market]}

    def pick(self):
        return matching_market(self.row, [self.event], NOW)[0]

    def test_reversed_outcomes(self):
        self.assertEqual(self.pick()['probabilities'], [0.7,0.3])

    def test_child_map_rejected(self):
        self.market['sportsMarketType'] = 'child_moneyline'
        self.assertIsNone(self.pick())

    def test_old_market_rejected(self):
        self.market['updatedAt'] = '2026-10-13T00:00:00Z'
        self.assertIsNone(self.pick())

    def test_future_update_rejected(self):
        self.market['updatedAt'] = '2026-10-15T00:00:00Z'
        self.assertIsNone(self.pick())

    def test_closed_no_liquidity_and_suspended(self):
        for key, value in [('closed',True), ('liquidityNum',0), ('acceptingOrders',False)]:
            original = self.market[key]
            self.market[key] = value
            self.assertIsNone(self.pick())
            self.market[key] = original

    def test_ended_event_rejected(self):
        self.event['ended'] = True
        self.assertIsNone(self.pick())

    def test_academy_not_parent(self):
        self.row['teams'][0] = 'Team A Academy'
        self.assertIsNone(self.pick())

    def test_rescheduled_match_rejected(self):
        self.market['gameStartTime'] = '2026-10-15T08:00:00Z'
        self.assertIsNone(self.pick())

    def test_duplicate_market_rejected(self):
        self.event['markets'].append(copy.deepcopy(self.market))
        self.assertIsNone(self.pick())

    def test_nan_boundary_and_invalid_prices(self):
        for prices in ['[0,1]', '["NaN",0.5]', '[0.3,0.2]', '[1.1,-0.1]']:
            self.market['outcomePrices'] = prices
            self.assertIsNone(self.pick())

    def test_equal_probabilities_no_invented_lean(self):
        self.assertEqual(pair_normalize([.51,.51]), [.5,.5])
        self.assertEqual(rating_probability([1000,1000]), [.5,.5])

    def test_no_vig(self):
        self.assertEqual(no_vig([2,2]), [.5,.5])
        self.assertEqual(no_vig([1.5,3]), [.666667,.333333])
        for odds in ([1,2], [float('nan'),2]):
            with self.assertRaises(ValueError): no_vig(odds)

    def test_model_symmetric(self):
        a = rating_probability([1800,1000])
        b = rating_probability([1000,1800])
        self.assertEqual(a, list(reversed(b)))
        self.assertGreater(a[0],.5)

    def test_timezone_required(self):
        self.assertEqual(parse_time('1791964800000').tzinfo, timezone.utc)
        with self.assertRaises(ValueError): parse_time('2026-10-14T08:00:00')

    def test_duplicate_organization_rankings_rejected(self):
        text = '| 1 | 1000 | Team A | a,b | link |\n| 2 | 950 | Team A | c,d | link |'
        self.assertNotIn('team a', parse_rankings(text))

    def test_actual_hotspawn_schema_and_coverage(self):
        html = (Path(__file__).parent/'fixtures/hotspawn.html').read_text()
        rows, links, count = parse_hotspawn(html)
        self.assertEqual(len(rows),88)
        self.assertEqual(count,88)
        self.assertNotIn('picked_percent',json.dumps(rows))
        with self.assertRaises(ValueError): parse_hotspawn(html.replace('All tiers (88)', 'All tiers (89)'))
        with self.assertRaises(ValueError): parse_hotspawn('<html>Challenge page</html>')

    def test_locked_rows_and_missing_inputs_blank(self):
        html = (Path(__file__).parent/'fixtures/hotspawn.html').read_text()
        rows, links, count = parse_hotspawn(html)
        snapshot = assemble(rows, links, count, [], {}, None, None, NOW, [])
        self.assertEqual(len(snapshot['matches']),88)
        self.assertTrue(all(r['probabilities'] is None for r in snapshot['matches']))
        self.assertTrue(any(r['flags'] for r in snapshot['matches']))

    def test_normalization_is_conservative(self):
        self.assertEqual(norm(' FURIA '), 'furia')
        self.assertNotEqual(norm('Aurora Gaming'),norm('Aurora'))


if __name__ == '__main__': unittest.main()
