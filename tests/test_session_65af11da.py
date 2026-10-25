"""Session 65af11da: the executive summary must not describe one set as another.

Measured on the live board at 2026-10-25T13:56Z (`https://buffedlizard55-lab.github.io/MaltaProj4/`),
the executive summary said both

* "Of those 78 feed rows, 61 are past-dated records the endpoint still returns with
  status: scheduled", and
* "62 of 78 feed rows are past their lock or start and stay unpriced on All matches".

Two different numbers for what a reader takes to be the same thing, because the second
sentence counted rows whose ``state`` is not ``open`` while calling them past. A retained
feed row can be not open for a reason other than its start time (its sourced status is not
scheduled), so the two sets are not interchangeable. The count stays the not-open count —
that is what actually stays unpriced — and the wording now says exactly that.

These tests pin the wording to the arithmetic so the two sentences cannot drift apart again,
and pin the dated HLTV re-check added to the limitations list on the same day.
"""
from __future__ import annotations

import copy
import json
import re
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build as build_module
from scripts import summary

ROOT = Path(__file__).resolve().parents[1]
NOT_OPEN_RE = re.compile(r'(\d+) of (\d+) feed rows are not open by sourced status or start time')


class ExecutiveSummaryCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / 'data/latest.json').read_text())
        cls.temp = tempfile.TemporaryDirectory()
        observed = datetime.fromisoformat(cls.snapshot['generated_at'].replace('Z', '+00:00'))
        build_module.build(copy.deepcopy(cls.snapshot), cls.temp.name, now=observed)
        cls.index = BeautifulSoup((Path(cls.temp.name) / 'index.html').read_text(), 'html.parser')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_banner_does_not_call_every_not_open_row_past(self):
        text = self.index.get_text(' ', strip=True)
        self.assertNotIn('past their lock or start', text,
                         'the not-open count must not be described as a past-start count')

    def test_banner_count_equals_not_open_count(self):
        text = self.index.get_text(' ', strip=True)
        match = NOT_OPEN_RE.search(text)
        self.assertIsNotNone(match, 'the not-open sentence is missing from the executive summary')
        not_open, feed_rows = int(match.group(1)), int(match.group(2))
        rows = self.snapshot['matches']
        self.assertEqual(feed_rows, len(rows))
        self.assertEqual(not_open, sum(1 for m in rows if m.get('state') != 'open'))

    def test_past_dated_sentence_still_counts_past_dated_rows(self):
        text = self.index.get_text(' ', strip=True)
        past = build_module.past_dated_rows(self.snapshot['matches'], self.snapshot)
        if not past:
            self.skipTest('no past-dated rows in this snapshot')
        self.assertIn(f'{len(past)} are past-dated records', text)

    def test_quicknav_does_not_call_every_not_open_row_past(self):
        text = self.index.get_text(' ', strip=True)
        self.assertNotIn('past feed rows are not open', text)
        self.assertIn('feed rows are not open', text)


class NotOpenIsNotPastTests(unittest.TestCase):
    """A row can be not open while its start is still ahead; the sentence must follow the count."""

    def snapshot_with_future_not_open_row(self):
        data = json.loads((ROOT / 'data/latest.json').read_text())
        open_rows = [m for m in data['matches'] if m.get('state') == 'open']
        if not open_rows:
            self.skipTest('no open rows in this snapshot')
        clone = copy.deepcopy(open_rows[0])
        clone['id'] = clone['id'] + '9'
        start = datetime.fromisoformat(clone['start'].replace('Z', '+00:00')) + timedelta(days=30)
        clone['start'] = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        clone['lock'] = (start - timedelta(minutes=6)).strftime('%Y-%m-%dT%H:%M:%SZ')
        clone['state'] = 'not_open'
        clone['pick'] = None
        clone['probabilities'] = None
        data['matches'].append(clone)
        return data

    def test_banner_follows_not_open_count_when_a_future_row_is_not_open(self):
        data = self.snapshot_with_future_not_open_row()
        past = build_module.past_dated_rows(data['matches'], data)
        not_open = sum(1 for m in data['matches'] if m.get('state') != 'open')
        self.assertNotEqual(not_open, len(past),
                            'fixture precondition: the two counts must differ for this test to mean anything')
        banner = build_module.exec_summary_bar(data)
        match = NOT_OPEN_RE.search(BeautifulSoup(banner, 'html.parser').get_text(' ', strip=True))
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), not_open)
        self.assertEqual(int(match.group(2)), len(data['matches']))

    def test_banner_accounts_for_the_retained_not_open_row(self):
        data = self.snapshot_with_future_not_open_row()
        text = BeautifulSoup(build_module.executive_banner(data), 'html.parser').get_text(' ', strip=True)
        past = len(build_module.past_dated_rows(data['matches'], data))
        not_open = sum(1 for m in data['matches'] if m.get('state') != 'open')
        retained = not_open - past
        self.assertGreaterEqual(retained, 1)
        if retained == 1:
            self.assertIn('and 1 more is retained but not open by its sourced status', text)
        else:
            self.assertIn(f'and {retained} more are retained but not open by their sourced status', text)
        # The three published numbers must add up to the feed size.
        self.assertIn(f'Of those {len(data["matches"])} feed rows, {past} are past-dated records', text)

    def test_count_span_matches_the_built_page_when_counts_move(self):
        data = self.snapshot_with_future_not_open_row()
        counts = summary.counts(data['matches'])
        self.assertEqual(counts['feed_rows'] - counts['open'],
                         sum(1 for m in data['matches'] if m.get('state') != 'open'))


class HltvLimitationTests(unittest.TestCase):
    """The dated HLTV re-check must reach both pages that publish the ladder."""

    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / 'data/latest.json').read_text())
        cls.temp = tempfile.TemporaryDirectory()
        observed = datetime.fromisoformat(cls.snapshot['generated_at'].replace('Z', '+00:00'))
        build_module.build(copy.deepcopy(cls.snapshot), cls.temp.name, now=observed)
        cls.output = Path(cls.temp.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_limitations_list_carries_the_dated_check_and_both_links(self):
        index = BeautifulSoup((self.output / 'index.html').read_text(), 'html.parser')
        panel = index.find(id='pick-limitations')
        self.assertIsNotNone(panel, 'the limitations panel is missing from the executive summary')
        text = panel.get_text(' ', strip=True)
        self.assertIn('25 Oct 2026', text)
        self.assertIn('rendered one partner promo row with no price', text)
        hrefs = {a.get('href') for a in panel.find_all('a')}
        self.assertIn('https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7', hrefs)
        self.assertIn('https://www.hltv.org/betting/analytics/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7', hrefs)

    def test_ladder_step_states_the_dated_check(self):
        hltv = next(step for step in summary.LADDER if step[0] == 'hltv')
        self.assertIn('25 Oct 2026', hltv[2])
        self.assertIn('2399918', hltv[2])
        unresolved = (self.output / 'unresolved.html').read_text()
        self.assertIn('25 Oct 2026', unresolved)


if __name__ == '__main__':
    unittest.main()
