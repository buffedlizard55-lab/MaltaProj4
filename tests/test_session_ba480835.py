"""Session ba480835 — historical rows must say their numbers are post-hoc.

Background (measured, not assumed). Session 11e17543's every-match table already
gives every listed Hotspawn row a pick or a recorded limitation, and labels a row
whose pick lock has passed as "Lock passed" / "historical evidence". What it did
not say is the thing that decides how such a number may be read: the percentages
on those rows are re-derived at BUILD time from the Valve standings file current at
that moment, so for a fixture played in June they come from a file that postdates
it and they move whenever Valve publishes a new one. This session therefore adds
one sentence per historical priced row plus one sentence for the section, and pins
both here.

Nothing in this file changes a pick, a probability or a source: it only requires
that the historical numbers carry their own date and provenance.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build, validate
from scripts.core import dt

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data' / 'latest.json').read_text(encoding='utf-8'))

NOTE = 'Post-hoc estimate, not a contemporaneous price'


class PostHocNoteUnit(unittest.TestCase):
    def row(self, **over):
        row = {'actionable': False, 'probabilities': [0.6, 0.4], 'ladder': 'model_vrs',
               'start': '2026-06-26T10:30:00Z'}
        row.update(over)
        return row

    def test_historical_model_row_names_the_standings_date_and_the_fixture(self):
        note = build.post_hoc_note(self.row(), '2026-10-05')
        self.assertIn(NOTE, note)
        self.assertIn('2026-10-05', note)
        self.assertIn('2026-06-26T10:30:00Z', note)

    def test_an_actionable_row_never_gets_the_note(self):
        self.assertEqual(build.post_hoc_note(self.row(actionable=True), '2026-10-05'), '')

    def test_a_row_without_a_percentage_never_gets_the_note(self):
        self.assertEqual(build.post_hoc_note(self.row(probabilities=None), '2026-10-05'), '')

    def test_a_market_line_never_gets_the_note(self):
        for ladder in ('pipeline', 'researched_line', 'unresolved'):
            self.assertEqual(build.post_hoc_note(self.row(ladder=ladder), '2026-10-05'), '', ladder)

    def test_the_tiers_that_use_the_standings_file_do_get_it(self):
        for ladder in build.POST_HOC_TIERS:
            self.assertIn(NOTE, build.post_hoc_note(self.row(ladder=ladder), '2026-10-05'), ladder)

    def test_an_unverified_start_is_described_not_invented(self):
        note = build.post_hoc_note(self.row(start=None), '2026-10-05')
        self.assertIn('an unverified start', note)


class RenderedDisclosure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        build.build(json.loads(json.dumps(DATA)), cls.out, now=dt(DATA['generated_at']))
        cls.soup = BeautifulSoup((cls.out / 'matches.html').read_text(encoding='utf-8'), 'html.parser')
        cls.section = cls.soup.find(id='every-match')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_historical_priced_row_carries_the_note(self):
        self.assertIsNotNone(self.section)
        rep = build.every_match_report(DATA)
        expected = {str(r['id']) for r in rep['rows']
                    if not r['actionable'] and r['probabilities'] and r['ladder'] in build.POST_HOC_TIERS}
        self.assertTrue(expected, 'the fixture snapshot must contain historical priced rows for this test to mean anything')
        seen = set()
        for tr in self.section.select('tbody tr'):
            limitation = tr.select_one('td[data-label="Limitation"]')
            if not limitation:
                continue
            text = limitation.get_text(' ', strip=True)
            fixture = tr.select_one('td[data-label="Fixture"]').get_text(strip=True)
            if NOTE in text:
                seen.add(fixture)
                self.assertIn(rep['standings']['as_of'], text, fixture)
                self.assertIn('postdate the fixture', text, fixture)
        self.assertEqual(seen, expected)

    def test_no_actionable_row_carries_the_note(self):
        rep = build.every_match_report(DATA)
        actionable = {str(r['id']) for r in rep['rows'] if r['actionable']}
        self.assertTrue(actionable)
        for tr in self.section.select('tbody tr'):
            fixture = tr.select_one('td[data-label="Fixture"]').get_text(strip=True)
            if fixture in actionable:
                self.assertNotIn(NOTE, tr.get_text(' ', strip=True), fixture)

    def test_the_section_states_the_rule_once_with_its_count(self):
        text = self.section.get_text(' ', strip=True)
        self.assertIn('Historical rows are post-hoc', text)
        rep = build.every_match_report(DATA)
        self.assertIn('%d rows here had already passed their Hotspawn pick lock'
                      % (rep['rows_total'] - rep['actionable']), text)
        self.assertIn(rep['standings']['as_of'], text)

    def test_the_published_site_still_validates_with_the_note(self):
        report = validate.validate_site(self.out)
        self.assertGreaterEqual(report['displayed_match_rows_verified'], len(DATA['matches']))

    def test_the_note_never_leaks_into_the_pick_board(self):
        """The actionable board must not carry a post-hoc sentence at all."""
        picks = BeautifulSoup((self.out / 'picks.html').read_text(encoding='utf-8'), 'html.parser')
        self.assertNotIn(NOTE, picks.get_text(' ', strip=True))


if __name__ == '__main__':
    unittest.main()
