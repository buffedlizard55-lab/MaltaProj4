"""Session ff49b2ef — 22 Oct 2026 unpriced-row research sweep + collision merge.

Locks the outcome of the line-by-line sweep over the rows that carried a pick
with no win probability on the 2026-10-22 00:55 UTC board:

* 1082769 K27 vs NEXORA is priced from the researched EGamersWorld book
  listing (8.1 / 1.021). This session and concurrent session 767649ba captured
  the same listing and pair independently; the merged file keeps exactly one
  receipt for the fixture (the repository bar rejects duplicate listing pairs),
  and this session's later 01:56 UTC sighting lives on as review evidence;
* this session's later placeholder re-reads (01:57-02:08 UTC) are recorded as
  dated refusals for the rows that still have no asymmetric pair;
* every sweep finding is published on the Flagged for Review source with
  dated, labelled source links.

Run: python -m unittest discover -s tests
"""
from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import book_candidate, book_receipts, book_research_pick, quote_book

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / 'data' / 'book-receipts.json'
NOTES = ROOT / 'data' / 'review-notes.json'

NOW = datetime(2026, 10, 22, 2, 15, tzinfo=timezone.utc)


def fixture(**over):
    row = {'id': '1082769', 'teams': ['K27', 'NEXORA'], 'start': '2026-10-22T17:30:00Z',
           'state': 'open', 'probabilities': None, 'pick': None, 'evidence': None,
           'flags': [], 'attempts': [], 'best_of': None, 'lock': '2026-10-22T17:24:00Z'}
    row.update(over)
    return row


class DataFilesStayMachineReadable(unittest.TestCase):
    def test_both_files_keep_indent_1_serialisation(self):
        for path in (BOOKS, NOTES):
            raw = path.read_text()
            self.assertEqual(raw, json.dumps(json.loads(raw), indent=1, ensure_ascii=False) + '\n')


class K27NexoraLine(unittest.TestCase):
    """The fixture must carry exactly one researched receipt: the merged one."""

    @classmethod
    def setUpClass(cls):
        cls.books = json.loads(BOOKS.read_text())
        cls.for_fixture = [r for r in cls.books['receipts'] if r['fixture_id'] == '1082769']
        cls.receipt = next(r for r in cls.books['receipts']
                           if r['id'] == 'egw-4yp_dlKtNl-nexora-k27')

    def test_exactly_one_receipt_prices_the_fixture(self):
        self.assertEqual(len(self.for_fixture), 1,
                         'duplicate listing pairs for fixture 1082769 are refused by test_session_b214c818')
        self.assertEqual(self.for_fixture[0]['id'], 'egw-4yp_dlKtNl-nexora-k27')

    def test_identity_fields_are_exact(self):
        self.assertEqual(self.receipt['fixture_id'], '1082769')
        self.assertEqual(self.receipt['source_teams'], ['NEXORA', 'K27'])
        self.assertEqual(self.receipt['start'], '2026-10-22T17:30:00Z')
        self.assertEqual(self.receipt['best_of'], 3)
        self.assertEqual(self.receipt['odds'], [8.1, 1.021])
        self.assertEqual(self.receipt['observed_at'], '2026-10-22T01:12:00Z')
        self.assertTrue(self.receipt['url'].startswith('https://egamersworld.com/'))

    def test_every_identity_fact_carries_a_link(self):
        self.assertGreaterEqual(len(self.receipt['identity_evidence']), 3)
        for item in self.receipt['identity_evidence']:
            self.assertTrue(item['url'].startswith('https://'), item)
            self.assertTrue(item['label'].strip(), item)
        self.assertTrue(all(s.get('url', '').startswith('https://')
                            for s in self.receipt['corroboration'] if 'url' in s))

    def test_limitations_are_published_not_hidden(self):
        self.assertIn('8-hour', self.receipt['limitation'])
        self.assertIn('corroborated', self.receipt['limitation'])

    def test_quote_de_vigs_to_a_directional_line(self):
        candidate = book_candidate(self.receipt)
        # order maps candidate sides (NEXORA, K27) into fixture order (K27, NEXORA)
        quote = quote_book(candidate, [1, 0], NOW)
        p = quote['probabilities']
        self.assertAlmostEqual(sum(p), 1.0, places=9)
        self.assertGreater(p[0], 0.85)      # K27 is the favourite
        self.assertLess(p[1], 0.15)
        self.assertGreaterEqual(quote['overround'], -0.02)
        self.assertLessEqual(quote['overround'], 0.25)

    def test_research_pick_prices_the_row_and_labels_it(self):
        row = fixture()
        book_research_pick(row, receipts=book_receipts(), now=NOW)
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertEqual(row['pick'], 'K27')
        self.assertAlmostEqual(row['probabilities'][0], 0.8881, places=3)
        self.assertAlmostEqual(row['probabilities'][1], 0.1119, places=3)
        self.assertTrue(any('researched listing' in f for f in row['flags']))
        self.assertEqual(row['attempts'][-1]['status'], 'resolved')

    def test_quote_refuses_after_the_eight_hour_window(self):
        row = fixture()
        book_research_pick(row, receipts=book_receipts(),
                           now=datetime(2026, 10, 22, 10, 0, tzinfo=timezone.utc))
        self.assertIsNone(row['probabilities'])
        self.assertEqual(row['attempts'][-1]['status'], 'unresolved')
        self.assertIn('stale', row['attempts'][-1]['reason'])

    def test_other_rows_are_never_priced_from_this_receipt(self):
        row = fixture(id='1081869', teams=['Morningstar', 'NEXVOID'],
                      start='2026-10-22T03:00:00Z')
        book_research_pick(row, receipts=book_receipts(), now=NOW)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])


class PlaceholderRejectionsRecorded(unittest.TestCase):
    """This session's later direct reads must be recorded as dated refusals, and
    no receipt may ever be built from a 1.8/1.8 default pair."""

    @classmethod
    def setUpClass(cls):
        cls.books = json.loads(BOOKS.read_text())

    def test_no_receipt_uses_the_default_placeholder_pair(self):
        for r in self.books['receipts']:
            self.assertNotEqual([float(x) for x in r['odds']], [1.8, 1.8], r['id'])

    def test_rejection_keys_are_unique(self):
        keys = [(r['fixture_id'], r['observed_at']) for r in self.books['rejected_listings']]
        self.assertEqual(len(keys), len(set(keys)))

    def test_later_placeholder_reads_are_recorded(self):
        expected = {
            ('1081869', '2026-10-22T01:57:00Z'),
            ('1081597', '2026-10-22T02:00:00Z'),
            ('1079654', '2026-10-22T02:05:00Z'),
            ('1081149', '2026-10-22T02:06:00Z'),
            ('1081150', '2026-10-22T02:08:00Z'),
        }
        by_key = {(r['fixture_id'], r['observed_at']): r for r in self.books['rejected_listings']}
        self.assertTrue(expected <= set(by_key))
        for key in expected:
            entry = by_key[key]
            self.assertEqual([float(x) for x in entry['displayed']], [1.8, 1.8])
            self.assertIn('Refused', entry['reason'])
            self.assertTrue(entry['url'].startswith('https://egamersworld.com/'))

    def test_concurrent_sessions_reads_are_not_discarded(self):
        expected = {
            ('1081597', '2026-10-22T01:08:00Z'),
            ('1081869', '2026-10-22T01:14:00Z'),
            ('1082860', '2026-10-22T01:14:00Z'),
        }
        have = {(r['fixture_id'], r['observed_at']) for r in self.books['rejected_listings']}
        self.assertTrue(expected <= have)


class ReviewNotesPublished(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = json.loads(NOTES.read_text())
        cls.by_id = {n['id']: n for n in cls.notes}

    def test_sweep_findings_are_flagged(self):
        for note_id in ('ff49b2ef-k27-nexora-egw-line-2026-10-22',
                        'ff49b2ef-unpriced-rows-sweep-2026-10-22',
                        'ff49b2ef-forze-lfo10-identity-2026-10-22',
                        'ff49b2ef-ex-rustec-shalfey-transfer-2026-10-22'):
            self.assertIn(note_id, self.by_id)

    def test_every_new_note_has_dated_labelled_sources(self):
        for note_id in self.by_id:
            if not note_id.startswith('ff49b2ef-'):
                continue
            note = self.by_id[note_id]
            self.assertTrue(note['finding'].strip())
            self.assertGreaterEqual(len(note['sources']), 3, note_id)
            for source in note['sources']:
                self.assertTrue(source['url'].startswith('https://'), (note_id, source))
                self.assertTrue(source['label'].strip(), (note_id, source))

    def test_collision_note_records_the_dropped_duplicate(self):
        finding = self.by_id['ff49b2ef-k27-nexora-egw-line-2026-10-22']['finding']
        self.assertIn('dropped', finding.lower())
        self.assertIn('egw-4yp_dlKtNl-nexora-k27', finding)

    def test_sweep_note_names_the_rows_it_covered(self):
        finding = self.by_id['ff49b2ef-unpriced-rows-sweep-2026-10-22']['finding']
        for fixture_id in ('1081869', '1081597', '1082860', '1082769'):
            self.assertIn(fixture_id, finding)


if __name__ == '__main__':
    unittest.main()
