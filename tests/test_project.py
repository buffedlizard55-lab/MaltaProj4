import sys,json,unittest,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from model import probabilities
class ProjectTests(unittest.TestCase):
    def test_normalization(self):
        p=probabilities([-150,120]);self.assertAlmostEqual(sum(p),1);self.assertAlmostEqual(p[0],.5689655172413793)
    def test_invalid(self):
        for odds in ([0,100],[float('nan'),150],[100],[-99,100]):
            with self.assertRaises(ValueError):probabilities(odds)
    def test_snapshot(self):
        data=json.loads(Path('site/data/matches.json').read_text());ids=set()
        for row in data['matches']:
            self.assertNotIn(row['id'],ids);ids.add(row['id'])
            self.assertEqual(len(row['teams']),2);self.assertTrue(row['source'].startswith('https://www.hotspawn.com/'))
            if row['odds']:
                self.assertTrue(row['bookSource'].startswith('https://thunderpick.io/'));self.assertTrue(row['oddsAt']);self.assertAlmostEqual(sum(probabilities(row['odds'])),1)
            else:self.assertTrue(row['reason'])
    def test_local_links(self):
        for page in Path('site').glob('*.html'):
            for href in re.findall(r'(?:href|src)="([^"]+)"',page.read_text()):
                if href.startswith(('http','#')):continue
                self.assertTrue((page.parent/href).exists(),f'{page}: {href}')
    def test_no_crowd_probabilities(self):
        data=Path('site/data/matches.json').read_text()
        self.assertNotIn('% picked',data)
    def test_lobby_parser(self):
        from collect import lobby_cards
        html='<div>Oct 15, 10:00<h3>Test event</h3>Points available<a href="https://www.hotspawn.com/matches/a-vs-b-1234567">View Match</a>Who will win?<p>A</p><p>90% picked</p><p>B</p><p>10% picked</p></div>'
        rows=lobby_cards(html);self.assertEqual(rows[0]['teams'],['A','B']);self.assertIsNone(rows[0]['odds']);self.assertIsNone(rows[0]['startUtc'])
