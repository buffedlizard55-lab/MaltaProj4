"""Rotation-proof ledger regressions: synthetic fixtures, never pinned live IDs."""
import copy
import unittest
from scripts.delivery_audit_928d7320 import inspect, evidence_class, secure_url, markdown


def fixture():
    return {'id': 'test', 'state': 'open', 'teams': ['A', 'B'], 'pick': 'A',
            'method': 'model_vrs', 'probabilities': [0.6, 0.4],
            'source_url': 'https://play.hotspawn.com/cs2-pickems',
            'evidence': [{'url': 'https://github.com/ValveSoftware/counter-strike_regional_standings',
                          'observed_at': '2026-10-24T00:00:00Z', 'warning': 'Not a market price'}],
            'attempts': [{'provider': 'HLTV'}, {'provider': 'Pinnacle'}]}


class LedgerTests(unittest.TestCase):
    def check_row(self, row):
        return inspect({'matches': [row]})

    def test_documented_fallback(self):
        self.assertEqual(self.check_row(fixture())['errors'], [])

    def test_reverse_order_fails(self):
        row = fixture()
        row['attempts'].reverse()
        self.assertTrue(self.check_row(row)['errors'])

    def test_missing_hltv_fails(self):
        row = fixture()
        row['attempts'] = [{'provider': 'Pinnacle'}]
        self.assertTrue(self.check_row(row)['errors'])

    def test_missing_book_fails(self):
        row = fixture()
        row['attempts'] = [{'provider': 'HLTV'}]
        self.assertTrue(self.check_row(row)['errors'])

    def test_featured_does_not_require_research(self):
        row = fixture()
        row.update(method='exchange', attempts=[])
        self.assertFalse(self.check_row(row)['errors'])

    def test_hotspawn_probability_is_rejected(self):
        for host in ('hotspawn.com', 'play.hotspawn.com'):
            row = fixture()
            row['evidence'][0]['url'] = f'https://{host}/lobby'
            self.assertTrue(self.check_row(row)['errors'])

    def test_missing_observation_rejected(self):
        row = fixture()
        del row['evidence'][0]['observed_at']
        self.assertTrue(self.check_row(row)['errors'])

    def test_missing_evidence_rejected(self):
        row = fixture()
        row['evidence'] = []
        self.assertTrue(self.check_row(row)['errors'])

    def test_duplicate_id_rejected(self):
        row = fixture()
        self.assertTrue(inspect({'matches': [row, copy.deepcopy(row)]})['errors'])

    def test_unresolved_blank_is_preserved(self):
        row = fixture()
        row.update(pick=None, probabilities=None, method=None, evidence=[], reason='No available source')
        result = self.check_row(row)
        self.assertFalse(result['errors'])
        self.assertIsNone(result['rows'][0]['probabilities'])

    def test_unexplained_blank_rejected(self):
        row = fixture()
        row.update(pick=None, probabilities=None, method=None, evidence=[])
        self.assertTrue(self.check_row(row)['errors'])

    def test_research_percentage_rejected(self):
        row = fixture()
        row['method'] = 'research_rank'
        self.assertTrue(self.check_row(row)['errors'])

    def test_indirect_price_not_called_primary(self):
        self.assertIn('Indirect', evidence_class('bookmaker_fallback'))
        self.assertIn('not a betting price', evidence_class('model_vrs_mirror'))

    def test_https_and_no_credentials_required(self):
        for url in ('http://example.com', 'https:///missing', 'https://user:pass@example.com'):
            self.assertFalse(secure_url(url))
        self.assertTrue(secure_url('https://example.com/path'))

    def test_report_has_sources_and_replay_disclaimer(self):
        text = markdown(self.check_row(fixture()))
        self.assertIn('[Hotspawn](https://', text)
        self.assertIn('[Evidence 1](https://', text)
        self.assertIn('not a live HTTP recheck', text)


if __name__ == '__main__':
    unittest.main()
