"""Regression checks for the independently observed Hotspawn view-count mismatch.

The source read exposed different counts on the generic lobby and the dedicated
CS2 Pick'ems page, but did not expose the generic lobby's selected game or the
exact IDs behind the difference. The review note must keep that uncertainty
visible, cite Hotspawn itself, and avoid manufacturing fixture rows or picks.
"""
import json
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build, core

ROOT = Path(__file__).resolve().parents[1]
NOTE_ID = '98367382-hotspawn-lobby-view-count-difference-2026-10-23'
GENERAL_LOBBY = 'https://play.hotspawn.com/lobby'
CS2_PICKEMS = 'https://play.hotspawn.com/cs2-pickems'
FIXTURE_API = ('https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures'
               '?sport_alias=cs2&status=scheduled&tenantId=1')


class HotspawnCountMismatchReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = json.loads((ROOT / 'data' / 'review-notes.json').read_text(encoding='utf-8'))
        matches = [note for note in cls.notes if note.get('id') == NOTE_ID]
        if len(matches) != 1:
            raise AssertionError('the live Hotspawn mismatch must have exactly one review note')
        cls.note = matches[0]

    def test_note_states_the_counts_and_preserves_the_uncertainty(self):
        self.assertIn('94', self.note['finding'])
        self.assertIn('92', self.note['finding'])
        self.assertIn('selected-game state', self.note['finding'])
        self.assertIn('does not establish that two CS2 fixtures are missing', self.note['finding'])
        self.assertIn('Do not infer', self.note['finding'])
        self.assertIn('three-source capture', self.note['finding'])

    def test_every_manual_review_link_is_an_official_hotspawn_view(self):
        urls = {source['url'] for source in self.note['sources']}
        self.assertEqual(urls, {GENERAL_LOBBY, CS2_PICKEMS, FIXTURE_API})
        self.assertTrue(all(url.startswith('https://') for url in urls))

    def test_finding_is_rendered_on_the_flagged_for_review_page(self):
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text(encoding='utf-8'))
        clock = core.dt(snapshot['generated_at'])
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            build.build(snapshot, out, now=clock)
            soup = BeautifulSoup((out / 'review.html').read_text(encoding='utf-8'), 'html.parser')
        row = soup.find('tr', id=NOTE_ID)
        self.assertIsNotNone(row, 'the verified count discrepancy must appear on review.html')
        text = row.get_text(' ', strip=True)
        self.assertIn('94', text)
        self.assertIn('92', text)
        self.assertIn('no picks added', row.get_text(' ', strip=True).lower())
        self.assertEqual({a.get('href') for a in row.select('a')},
                         {GENERAL_LOBBY, CS2_PICKEMS, FIXTURE_API})


if __name__ == '__main__':
    unittest.main()
