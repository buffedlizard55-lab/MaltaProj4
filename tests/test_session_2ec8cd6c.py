"""Session 2ec8cd6c regressions: independent line-by-line re-derivation of the
published board, the official VRS input, and the unresolved-section contract.

What this session verified (see research/session-2ec8cd6c/REPORT.md)
--------------------------------------------------------------------
* every one of the 107 published rows carries an https source link on an
  official host;
* every open row's pick is one of its two teams and, where a probability is
  published, the strictly higher-probability side; the pair sums to one and
  the fair odds are the reciprocals;
* all 37 published probabilities reproduce from the retained raw inputs
  (Polymarket outcome prices, the Pinnacle American line, or Valve's official
  standings points through Valve's own published formula and calibration),
  with team identity mapped exactly as the pipeline maps it (plain-name
  folding, the explicit alias register, Polymarket event-team abbreviations);
* the six research-only rows each state their limitation and are listed with
  their sources on both the executive summary's unresolved section and the
  standalone research-queue page;
* the vendored Valve standings file is byte-identical to the live official
  file and 2026-10-05 is still the newest official publication.

These tests pin that state. They run fully offline: the audit replays the
committed snapshot against the committed pages and the vendored official
file; no value is fetched or inferred here.
"""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'research/session-2ec8cd6c/audit_board.py'
AUDIT_RECEIPT = ROOT / 'research/session-2ec8cd6c/audit-receipt.json'
VRECEIPT = ROOT / 'research/session-2ec8cd6c/valve-file-receipt.json'


def load(path):
    return json.loads(Path(path).read_text())


class TestBoardReDerivation(unittest.TestCase):
    """The committed snapshot must re-derive line by line from its receipts."""

    @classmethod
    def setUpClass(cls):
        cls.proc = subprocess.run(
            [sys.executable, str(AUDIT)],
            capture_output=True, text=True, cwd=str(ROOT), timeout=600)

    def test_audit_exits_clean(self):
        self.assertEqual(self.proc.returncode, 0,
                         'audit failures:\n' + self.proc.stdout[-3000:] + self.proc.stderr[-3000:])

    def test_receipt_counts_match_the_snapshot(self):
        snap = load(ROOT / 'data/latest.json')
        receipt = load(AUDIT_RECEIPT)
        open_rows = [m for m in snap['matches'] if m.get('state') == 'open']
        with_prob = [m for m in open_rows if m.get('probabilities') is not None]
        without = [m for m in open_rows if m.get('probabilities') is None]
        counts = receipt['counts']
        self.assertEqual(receipt['status'], 'pass')
        self.assertEqual(receipt['failures'], [])
        self.assertEqual(receipt['rows_total'], len(snap['matches']))
        self.assertEqual(receipt['rows_open'], len(open_rows))
        self.assertEqual(counts['rows_with_official_source'], len(snap['matches']))
        self.assertEqual(counts['open_with_pick'], len(open_rows))
        self.assertEqual(counts['open_with_probability'], len(with_prob))
        # Every published percentage re-derived from retained raw inputs.
        self.assertEqual(counts['probabilities_reproduced'], len(with_prob))
        # Every research-only row is named on both unresolved surfaces.
        self.assertEqual(counts['research_only'], len(without))
        self.assertEqual(counts['research_listed_on_both_pages'], len(without))


class TestUnresolvedSectionContract(unittest.TestCase):
    """The executive summary must expose the unresolved section and the
    links that let a phone user reach the pick list and its limitations."""

    def setUp(self):
        self.index = (ROOT / 'index.html').read_text()
        self.unresolved = (ROOT / 'unresolved.html').read_text()

    def test_executive_summary_has_the_unresolved_section(self):
        self.assertIn('id="unresolved-summary"', self.index)
        self.assertIn('id="pick-limitations"', self.index)

    def test_executive_summary_links_the_pick_board_and_unresolved_page(self):
        self.assertIn('href="picks.html"', self.index)
        self.assertIn('href="unresolved.html"', self.index)

    def test_every_open_row_without_a_probability_is_named_on_both_pages(self):
        snap = load(ROOT / 'data/latest.json')
        for m in snap['matches']:
            if m.get('state') != 'open' or m.get('probabilities') is not None:
                continue
            for team in m['teams']:
                self.assertIn(team, self.unresolved,
                              '%s missing from unresolved.html' % team)
                section = self.index.split('id="unresolved-summary"')[-1]
                self.assertIn(team, section,
                              '%s missing from the executive summary unresolved section' % team)


class TestValveOfficialInput(unittest.TestCase):
    """The model's input must stay byte-identical to Valve's official file."""

    def test_vendored_copy_matches_the_recorded_official_hash(self):
        meta = load(ROOT / 'data/vrs/meta.json')
        vendored = ROOT / 'data/vrs' / meta['file']
        self.assertEqual(hashlib.sha256(vendored.read_bytes()).hexdigest(), meta['sha256'])

    def test_live_official_verification_receipt_passes(self):
        receipt = load(VRECEIPT)
        self.assertEqual(receipt['status'], 'pass')
        for name, ok in receipt['checks'].items():
            self.assertTrue(ok, 'official-input check failed: %s' % name)
        meta = load(ROOT / 'data/vrs/meta.json')
        vendored_sha = hashlib.sha256((ROOT / 'data/vrs' / meta['file']).read_bytes()).hexdigest()
        self.assertEqual(receipt['live_file']['sha256'], vendored_sha)
        self.assertEqual(receipt['snapshot_cited_file'], meta['file'])


if __name__ == '__main__':
    unittest.main()
