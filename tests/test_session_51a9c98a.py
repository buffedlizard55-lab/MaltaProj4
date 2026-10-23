"""Session 51a9c98a: the feed's own scope has to be visible, not implied.

Measured on 2026-10-23: the Hotspawn fixtures endpoint returned 92 CS2 rows with
``status=scheduled``, 62 of which start in June/July 2026, while the public lobby
listed 30 open matches. The board keeps every row (an inventory must not be
trimmed silently) but a reader opening "All matches" saw June fixtures beside
tonight's with no explanation. These tests pin the disclosure that fixes that:

* ``past_dated_rows`` splits on the **snapshot's own observation clock**, never
  the machine clock, so one snapshot always yields one answer;
* ``feed_scope`` states the split with the snapshot's counts and links both
  official sources;
* the executive summary names the past-dated rows instead of letting "92 feed
  rows" read as "92 matches";
* past rows are labelled as past fixtures, and an open row never is;
* the three dated findings added this session are on the review page with
  official source links and canonical JSON formatting.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build as build_module
from scripts.build import build, executive_banner, feed_scope, past_dated_rows, table

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data' / 'latest.json').read_text(encoding='utf-8'))
OBSERVED = '2026-10-23T08:29:19Z'


def row(match_id, start, state='open', pick='Alpha', competitions=('Some Series',)):
    return {
        'id': match_id, 'teams': ['Alpha', 'Beta'], 'start': start, 'lock': start,
        'state': state, 'pick': pick, 'probabilities': [0.6, 0.4] if pick else None,
        'fair_odds': [1.66, 2.5] if pick else None, 'method': 'exchange' if pick else None,
        'competition': competitions[0], 'tier': 'b', 'best_of': None,
        'source_url': 'https://www.hotspawn.com/matches/alpha-vs-beta-' + match_id,
        'flags': [], 'attempts': [], 'evidence': [], 'reason': None,
    }


class PastDatedRowsTests(unittest.TestCase):
    def test_only_rows_before_the_snapshot_observation_are_past(self):
        data = {'fixtures_observed_at': OBSERVED, 'matches': [
            row('1', '2026-06-26T10:30:00Z', state='not_open', pick=None),
            row('2', '2026-10-23T08:00:00Z', state='not_open', pick=None),
            row('3', '2026-10-23T11:00:00Z'),
        ]}
        self.assertEqual([m['id'] for m in past_dated_rows(data['matches'], data)], ['1', '2'])

    def test_an_unreadable_snapshot_clock_marks_nothing_past(self):
        for value in (None, '', 'not-a-date'):
            data = {'fixtures_observed_at': value,
                    'matches': [row('1', '2026-06-26T10:30:00Z', state='not_open', pick=None)]}
            self.assertEqual(past_dated_rows(data['matches'], data), [], value)

    def test_unusable_row_starts_are_skipped_not_guessed(self):
        data = {'fixtures_observed_at': OBSERVED, 'matches': [
            row('1', None, state='not_open', pick=None),
            row('2', 'yesterday', state='not_open', pick=None),
            row('3', '2026-06-26T10:30:00Z', state='not_open', pick=None),
        ]}
        self.assertEqual([m['id'] for m in past_dated_rows(data['matches'], data)], ['3'])


class FeedScopeTests(unittest.TestCase):
    def data(self):
        return {'fixtures_observed_at': OBSERVED, 'matches': [
            row('1', '2026-06-26T10:30:00Z', state='not_open', pick=None),
            row('2', '2026-07-10T08:00:00Z', state='not_open', pick=None),
            row('3', '2026-10-23T11:00:00Z'),
        ]}

    def test_counts_and_window_come_from_the_snapshot(self):
        soup = BeautifulSoup(feed_scope(self.data()), 'html.parser')
        text = soup.get_text(' ', strip=True)
        # No implied sum: the open counter is live, so it is stated next to the
        # past count, never added to it.
        self.assertIn('2 of 3 feed rows are past fixtures', text)
        self.assertNotIn('feed rows =', text)
        self.assertIn('only the 1 open rows carry prices', text)
        self.assertIn('2 CS2 rows', text)
        self.assertIn('status: scheduled', text)
        self.assertIn('never given a pick or a percentage', text)
        self.assertIn('26 Jun · 10:30', text)
        self.assertIn('10 Jul · 08:00', text)

    def test_both_official_sources_are_linked(self):
        soup = BeautifulSoup(feed_scope(self.data()), 'html.parser')
        hrefs = {a['href'] for a in soup.select('a[href]')}
        self.assertIn('https://play.hotspawn.com/lobby', hrefs)
        self.assertIn(build_module.FIXTURES, hrefs)

    def test_the_panel_offers_a_tap_to_the_past_rows_and_to_the_picks(self):
        soup = BeautifulSoup(feed_scope(self.data()), 'html.parser')
        hrefs = {a['href'] for a in soup.select('a[href]')}
        # The board opens on open matches, so the counted past rows need their own tap.
        self.assertIn('matches.html?status=not_open', hrefs)
        self.assertIn('picks.html', hrefs)

    def test_a_feed_without_past_rows_renders_no_panel(self):
        data = {'fixtures_observed_at': OBSERVED, 'matches': [row('3', '2026-10-23T11:00:00Z')]}
        self.assertEqual(feed_scope(data), '')


class ExecutiveSummaryDisclosureTests(unittest.TestCase):
    def test_banner_names_the_past_dated_rows_and_links_the_panel(self):
        data = {'fixtures_observed_at': OBSERVED, 'matches': [
            row('1', '2026-06-26T10:30:00Z', state='not_open', pick=None),
            row('3', '2026-10-23T11:00:00Z'),
        ]}
        soup = BeautifulSoup(executive_banner(data), 'html.parser')
        text = soup.get_text(' ', strip=True)
        self.assertIn('Of those 2 feed rows, 1 are past-dated', text)
        self.assertIn('never priced', text)
        self.assertIn('matches.html#feed-scope', {a['href'] for a in soup.select('a[href]')})

    def test_a_feed_without_past_rows_makes_no_such_claim(self):
        data = {'fixtures_observed_at': OBSERVED, 'matches': [row('3', '2026-10-23T11:00:00Z')]}
        text = BeautifulSoup(executive_banner(data), 'html.parser').get_text(' ', strip=True)
        self.assertNotIn('past-dated', text)
        self.assertNotIn('past fixtures', text)


class RowLabelTests(unittest.TestCase):
    def test_past_rows_are_labelled_and_open_rows_are_not(self):
        past = row('1', '2026-06-26T10:30:00Z', state='not_open', pick=None)
        current = row('3', '2026-10-23T11:00:00Z')
        html = table([past, current], past_ids={'1'})
        soup = BeautifulSoup(html, 'html.parser')
        cells = {tr.get('data-match'): tr.get_text(' ', strip=True) for tr in soup.select('tr.row')}
        self.assertIn('Past fixture · not in the lobby', cells['1'])
        self.assertNotIn('Past fixture', cells['3'])
        self.assertIn('Alpha', cells['3'])

    def test_the_default_keeps_the_previous_wording(self):
        past = row('1', '2026-06-26T10:30:00Z', state='not_open', pick=None)
        soup = BeautifulSoup(table([past]), 'html.parser')
        self.assertIn('Not open', soup.get_text(' ', strip=True))
        self.assertNotIn('Past fixture', soup.get_text(' ', strip=True))


class BuiltSiteDisclosureTests(unittest.TestCase):
    """The committed snapshot must produce the same split the page states.

    Session b6e37c61 repair (flagged to 51a9c98a in COORDINATION.md): the
    build must run on the snapshot's own clock. ``build()`` re-derives
    openness against its ``now``, so building a committed snapshot at wall
    clock made the panel count depend on when CI ran — on 2026-10-23 the
    10:44Z snapshot built after the 11:00Z starts showed 27 open vs the
    snapshot's 30, failing every main publish at the test step (the tests
    run before the refresh, so a fresh snapshot could never replace the
    stale one). Building at ``generated_at`` keeps the test's intent —
    panel equals snapshot — true at any wall-clock time, matching this
    file's own rule that one snapshot always yields one answer.
    """

    @classmethod
    def setUpClass(cls):
        from scripts.core import dt
        cls.tmp = tempfile.TemporaryDirectory()
        build(json.loads(json.dumps(DATA)), cls.tmp.name, now=dt(DATA['generated_at']))
        cls.matches_html = (Path(cls.tmp.name) / 'matches.html').read_text(encoding='utf-8')
        cls.index_html = (Path(cls.tmp.name) / 'index.html').read_text(encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_panel_counts_equal_the_snapshot_itself(self):
        past = past_dated_rows(DATA['matches'], DATA)
        # build() re-applies its own lock/expiry clock, so the open count the page
        # publishes is the one in its own data file, not the committed state field.
        built = json.loads((Path(self.tmp.name) / 'data' / 'latest.json').read_text(encoding='utf-8'))
        opened = sum(1 for m in built['matches'] if m['state'] == 'open')
        self.assertEqual(len(built['matches']), len(DATA['matches']))
        soup = BeautifulSoup(self.matches_html, 'html.parser')
        panel = soup.select_one('#feed-scope')
        self.assertIsNotNone(panel)
        text = panel.get_text(' ', strip=True)
        self.assertIn(f'{len(past)} of {len(DATA["matches"])} feed rows are past fixtures', text)
        self.assertNotIn('feed rows =', text)
        self.assertIn(f'only the {opened} open rows carry prices', text)
        self.assertIn(f'still returns {len(past)} CS2 rows', text)

    def test_every_past_row_is_labelled_and_no_open_row_is(self):
        soup = BeautifulSoup(self.matches_html, 'html.parser')
        past_ids = {str(m['id']) for m in past_dated_rows(DATA['matches'], DATA)}
        open_ids = {str(m['id']) for m in DATA['matches'] if m['state'] == 'open'}
        labelled = {tr.get('data-match') for tr in soup.select('tr.row')
                    if 'Past fixture' in tr.get_text(' ', strip=True)}
        self.assertEqual(labelled, past_ids)
        self.assertFalse(labelled & open_ids)

    def test_past_rows_carry_no_pick_or_percentage(self):
        for match in past_dated_rows(DATA['matches'], DATA):
            self.assertIsNone(match.get('pick'), match['id'])
            self.assertIsNone(match.get('probabilities'), match['id'])

    def test_executive_summary_states_the_same_count(self):
        past = len(past_dated_rows(DATA['matches'], DATA))
        text = BeautifulSoup(self.index_html, 'html.parser').get_text(' ', strip=True)
        self.assertIn(f'Of those {len(DATA["matches"])} feed rows, {past} are past-dated records', text)


class ReviewNoteTests(unittest.TestCase):
    IDS = (
        'session-51a9c98a-feed-rows-vs-lobby-2026-10-23',
        'session-51a9c98a-lobby-clocks-are-edt-2026-10-23',
        'session-51a9c98a-scheduled-delivery-2026-10-23',
    )

    def test_canonical_formatting_and_notes_present(self):
        raw = (ROOT / 'data' / 'review-notes.json').read_text(encoding='utf-8')
        notes = json.loads(raw)
        self.assertEqual(raw, json.dumps(notes, indent=1, ensure_ascii=False) + '\n')
        by_id = {n['id']: n for n in notes}
        for note_id in self.IDS:
            self.assertIn(note_id, by_id)
            self.assertGreaterEqual(len(by_id[note_id]['sources']), 2, note_id)
            for source in by_id[note_id]['sources']:
                self.assertRegex(source['url'], r'^https://', note_id)
                self.assertTrue(source['label'].strip(), note_id)

    def test_findings_are_dated_and_carry_no_invented_numbers(self):
        notes = {n['id']: n for n in json.loads((ROOT / 'data' / 'review-notes.json').read_text(encoding='utf-8'))}
        for note_id in self.IDS:
            self.assertIn('2026-10-23', notes[note_id]['finding'], note_id)
            # A dated observation, never a probability claim.
            self.assertIsNone(re.search(r'\d+\.\d+%', notes[note_id]['finding']), note_id)


if __name__ == '__main__':
    unittest.main()
