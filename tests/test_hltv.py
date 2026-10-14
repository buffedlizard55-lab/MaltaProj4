import unittest
from pathlib import Path
from scripts.hltv import discover,context

class HltvTests(unittest.TestCase):
    def test_discovery_from_primary_excerpt(self):
        c=discover(Path('tests/fixtures/hltv.html').read_text())
        self.assertEqual(len(c),3);self.assertEqual(c[0]['teams'],['GenOne','6666'])
        self.assertTrue(c[0]['start'].endswith('Z'))
    def test_missing_list(self):
        with self.assertRaises(ValueError):discover('<h1>Blocked</h1>')
    def test_context_never_uses_fan_votes(self):
        f={'teams':['Ryvex','PCIFIC'],'start':'2026-10-14T14:00:00Z'}
        c=context(Path('tests/fixtures/hltv-pcific.html').read_text(),f)
        self.assertEqual(c['numeric_quote_rows'],0);self.assertEqual(c['ranks'][0]['hltv_rank'],135)
        self.assertNotIn('probabilities',c)
    def test_wrong_match(self):
        with self.assertRaises(ValueError):context(Path('tests/fixtures/hltv-pcific.html').read_text(),{'teams':['Ryvex Academy','PCIFIC'],'start':'2026-10-14T14:00:00Z'})
