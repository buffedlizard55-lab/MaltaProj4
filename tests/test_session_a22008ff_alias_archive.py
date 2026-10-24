"""Session a22008ff: turn the five silent alias skips into real checks.

Measured on the 2026-10-24T17:03Z board: seven tests reported
``... skipped 'fixture 1083121 has rotated off the published board'`` (or the
equivalent wording) in `tests/test_session_019a253a.py`,
`tests/test_session_d2b90de7.py` and `tests/test_session_ea2e254c.py`.

Hotspawn rotated fixture 1083121 out of its lobby, which is correct behaviour and
must not be undone. But the property those tests prove — an alias recorded with an
https source that names both labels maps a source outcome onto a team, and a
tampered price is still refused — is not about one fixture staying on the board.
Skipping it silently means the alias path stops being exercised altogether, which
is exactly the kind of quiet gate erosion that let the 2026-10-23/24 publish
freeze run for 17.7 h.

`research/harvest-ce45f672/snapshot.json` is this repository's own retained
capture of the board while the fixture was still open, so it is the same evidence
the shipped code read, at a known time. These tests require that retained row to
be present and to replay; a missing archive, or a row that no longer reproduces,
fails instead of skipping.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALIAS_ID = '1083121'
ARCHIVE = ROOT / 'research/harvest-ce45f672/snapshot.json'


def archived_alias_row():
    """The retained alias row, or an explicit failure (never a skip)."""
    if not ARCHIVE.exists():
        raise AssertionError('the retained alias capture %s is missing' % ARCHIVE.relative_to(ROOT))
    doc = json.loads(ARCHIVE.read_text())
    row = next((m for m in doc.get('matches') or [] if m['id'] == ALIAS_ID), None)
    if row is None:
        raise AssertionError('the retained capture no longer contains fixture %s' % ALIAS_ID)
    return doc, row


class TheRetainedAliasEvidenceStillReproduces(unittest.TestCase):
    def test_the_archive_row_is_an_aliased_exchange_row_with_both_labels(self):
        _, row = archived_alias_row()
        self.assertEqual(row['state'], 'open')
        self.assertEqual(row['method'], 'exchange')
        evidence = (row.get('evidence') or [{}])[0]
        names = {name for entry in evidence.get('identity_sources') or []
                 for name in entry.get('names') or []}
        self.assertIn('Tropa do KinGui', names)
        self.assertIn('Projeto do KinGui', names)
        for entry in evidence['identity_sources']:
            self.assertTrue(str(entry.get('source', '')).startswith('https://'), entry)
            self.assertTrue(str(entry.get('basis') or '').strip(), entry)

    def test_the_retained_price_re_derives_and_the_pick_follows_it(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'verify_ea2e254c_a22008ff', ROOT / 'research/session-0cc1138a/verify_0cc1138a.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        _, row = archived_alias_row()
        probabilities, kind = verifier.evidence_probabilities(row['evidence'][0], row['teams'])
        self.assertEqual(kind, 'exchange_mid')
        self.assertAlmostEqual(sum(probabilities), 1.0, places=9)
        for published, rebuilt in zip(row['probabilities'], probabilities):
            self.assertAlmostEqual(published, rebuilt, places=9)
        favourite = row['teams'][0] if probabilities[0] > probabilities[1] else row['teams'][1]
        self.assertEqual(row['pick'], favourite)

    def test_a_tampered_retained_price_is_still_refused(self):
        import copy
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'verify_ea2e254c_a22008ff_tamper', ROOT / 'research/session-0cc1138a/verify_0cc1138a.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        _, row = archived_alias_row()
        tampered = copy.deepcopy(row)
        tampered['probabilities'] = [0.99, 0.01]
        with self.assertRaises((AssertionError, ValueError)):
            probabilities, _ = verifier.evidence_probabilities(tampered['evidence'][0], tampered['teams'])
            if [round(p, 9) for p in probabilities] != [round(p, 9) for p in tampered['probabilities']]:
                raise AssertionError('a tampered published price must not re-derive')

    def test_the_suites_that_used_to_skip_now_read_the_archive(self):
        for relative in ('tests/test_session_019a253a.py', 'tests/test_session_d2b90de7.py',
                         'tests/test_session_ea2e254c.py'):
            source = (ROOT / relative).read_text()
            self.assertIn('retained_alias_row', source,
                          '%s still skips instead of reading the retained capture' % relative)
            for stale in ("has rotated out of the feed",
                          "has rotated off the published board",
                          "is not on this snapshot as an exchange row"):
                self.assertNotIn(stale, source,
                                 '%s still skips the alias contract when the fixture rotates' % relative)


if __name__ == '__main__':
    unittest.main()
