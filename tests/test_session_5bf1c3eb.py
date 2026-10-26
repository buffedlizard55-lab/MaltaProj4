"""Session 5bf1c3eb regressions: the third register — closed pick windows.

The brief asks for a pick on every match *and* for a separate section naming the
matches that cannot have one, with the limitations that cause it, referenced from
the executive summary. Measured on the live harvest run 40251492364 (fixtures
observed 2026-10-26T00:53:32Z): every open Hotspawn row resolves through the
ladder (19 picks, 19 win probabilities, 0 unresolved), while 62 rows the fixtures
endpoint still returns carry a ``lock_time`` earlier than the observation clock.
Folding those rows into "unresolved" is what made the board read as dozens of
matches with no pick, so they get their own register.

These tests pin, against whatever snapshot is committed:

* the register contains exactly the not-open rows, each with its own lock time
  taken from the snapshot's retained feed evidence and nothing inferred;
* the register is a *separate* section on the executive summary page and on the
  unresolved page, linked from the always-visible executive bar and banner;
* no closed row renders a probability, a fair line or a pick anywhere;
* every closed row keeps an official Hotspawn source link and its evidence anchor;
* the pick list still precedes the register in DOM order, so a phone's first
  screen is untouched by this section;
* the upstream ``status: scheduled`` + past ``end_time`` conflict is disclosed on
  the Flagged for Review page under this session's note id, not repaired.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build as build_module
from scripts import summary

ROOT = Path(__file__).resolve().parents[1]
NOTE_ID = 'session-5bf1c3eb-hotspawn-stale-scheduled-2026-10-26'


class ClosedWindowRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        cls.register = summary.closed_register(cls.snapshot['matches'], cls.snapshot)
        cls.temp = tempfile.TemporaryDirectory()
        observed = datetime.fromisoformat(cls.snapshot['generated_at'].replace('Z', '+00:00'))
        build_module.build(copy.deepcopy(cls.snapshot), cls.temp.name, now=observed)
        cls.pages = {name: BeautifulSoup((Path(cls.temp.name) / name).read_text(), 'html.parser')
                     for name in ('index.html', 'unresolved.html', 'review.html')}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def not_open(self):
        return [m for m in self.snapshot['matches'] if m.get('state') != 'open']

    def test_register_is_exactly_the_not_open_rows(self):
        self.assertEqual({r['id'] for r in self.register}, {m['id'] for m in self.not_open()})
        for row in self.register:
            self.assertFalse(any(m['id'] == row['id'] and m['state'] == 'open'
                                 for m in self.snapshot['matches']))

    def test_every_closed_row_carries_its_own_lock_and_no_invented_fields(self):
        locks = {m['id']: m.get('lock') for m in self.not_open()}
        for row in self.register:
            self.assertEqual(row['lock_utc'], locks[row['id']])
            self.assertTrue(row['reasons'], 'a closed row must state its limitation')
            self.assertTrue(row['source_url'].startswith('https://'))
            for field in ('feed_status', 'scheduled_start_utc'):
                self.assertIsNotNone(row[field], 'retained feed evidence must not be dropped')

    def test_conflict_count_comes_from_the_retained_feed_evidence(self):
        evidence = {str(x.get('id')): x for x in self.snapshot.get('fixture_evidence') or []}
        expected = 0
        for m in self.not_open():
            raw = evidence.get(str(m['id'])) or {}
            if raw.get('end_time') and (raw.get('status') or m.get('source_status')) == 'scheduled':
                expected += 1
        self.assertEqual(sum(1 for r in self.register if r['upstream_conflict']), expected)

    def test_sentence_arithmetic_matches_the_register(self):
        sentence = summary.closed_sentence(self.register)
        self.assertTrue(sentence.startswith('%d feed rows cannot carry a pick' % len(self.register)))
        self.assertIn(str(sum(1 for r in self.register if r['upstream_conflict'])), sentence)
        self.assertNotIn('past their lock or start', sentence)

    def test_separate_section_exists_on_summary_and_unresolved_pages(self):
        for name in ('index.html', 'unresolved.html'):
            section = self.pages[name].select_one('#closed-windows')
            self.assertIsNotNone(section, name + ' must carry the closed-window register')
            self.assertIn('Closed pick windows', section.get_text())
            limits = section.select_one('#closed-limits')
            self.assertIsNotNone(limits, name + ' must state the limitations')
            self.assertGreaterEqual(len(limits.select('li')), 3)

    def test_every_closed_row_is_listed_with_an_official_source_and_no_probability(self):
        section = self.pages['index.html'].select_one('#closed-windows')
        rows = section.select('tbody tr')
        self.assertEqual(len(rows), len(self.register))
        for row in rows:
            hrefs = {a.get('href') for a in row.select('a')}
            self.assertTrue(any('hotspawn.com' in (h or '') for h in hrefs),
                            'closed row without an official Hotspawn link')
            self.assertTrue(any((h or '').startswith('evidence.html#match-') for h in hrefs))
            self.assertNotIn('%', row.select_one('td[data-label="Why no pick is possible"]').get_text())

    def test_closed_rows_render_no_probability_or_pick_anywhere(self):
        """The board stays the open rows only; closed rows never carry a price."""
        index = self.pages['index.html']
        for m in self.not_open():
            self.assertEqual(index.select('tr[data-match="%s"]' % m['id']), [],
                             'a closed row must not appear on the open pick board')
        unresolved = self.pages['unresolved.html']
        for m in self.not_open():
            for cell in unresolved.select('tr[data-match="%s"]' % m['id']):
                self.assertFalse(cell.select('.prob-pair span'))
                self.assertIsNone(cell.select_one('.pick-cell .pick'))

    def test_executive_summary_links_to_the_register(self):
        index = self.pages['index.html']
        bar = index.select_one('#exec-summary')
        self.assertIsNotNone(bar)
        self.assertIn('#closed-windows', {a.get('href') for a in bar.select('a')})
        banner = index.select_one('#exec-banner')
        self.assertIn('#closed-windows', {a.get('href') for a in banner.select('a')})
        unresolved_section = index.select_one('#unresolved-picks')
        self.assertIn('#closed-windows', {a.get('href') for a in unresolved_section.select('a')})

    def test_pick_list_precedes_the_register_in_dom_order(self):
        raw = (Path(self.temp.name) / 'index.html').read_text()
        self.assertLess(raw.index('id="picks-at-a-glance"'), raw.index('id="closed-windows"'),
                        'the register must never push the pick list off the first phone screen')
        self.assertLess(raw.index('id="unresolved-picks"'), raw.index('id="closed-windows"'))

    def test_upstream_conflict_is_flagged_not_repaired(self):
        review = self.pages['review.html']
        self.assertIsNotNone(review.find(id=NOTE_ID),
                             'the upstream status conflict must be on Flagged for Review')
        notes = json.loads((ROOT / 'data' / 'review-notes.json').read_text())
        note = next(n for n in notes if n['id'] == NOTE_ID)
        self.assertTrue(all(s['url'].startswith('https://') for s in note['sources']))
        self.assertIn('1052746', note['finding'])


if __name__ == '__main__':
    unittest.main()
