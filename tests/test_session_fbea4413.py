"""Unit and corruption-rejection tests for session fbea4413 independent verifier."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts import verify_fbea4413 as V

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


class SessionFbea4413VerifierTests(unittest.TestCase):
    def test_committed_snapshot_verifies_zero_problems(self):
        report = V.audit_snapshot(SNAPSHOT)
        self.assertEqual(report['problems'], [], report['problems'][:5])
        counts = report['counts']
        self.assertGreater(counts['total'], 0)
        self.assertGreater(counts['open'], 0)
        self.assertEqual(counts['open'] + counts['not_open'], counts['total'])
        self.assertEqual(
            counts['open_with_pick'] + counts['open_unresolved'],
            counts['open'],
            'every open match must either have a pick or be explicitly unresolved',
        )

    def test_site_html_and_css_verify_zero_problems(self):
        report = V.audit_site(ROOT)
        self.assertEqual(report['problems'], [], report['problems'][:5])
        for expected in (
            'css_byte_identical',
            'index_has_exec-summary',
            'index_has_exec-quicknav',
            'index_has_freshness-strip',
            'index_has_picks-at-a-glance',
            'index_has_unresolved-summary',
            'index_has_unresolved-limits',
        ):
            self.assertIn(expected, report['checks'])

    def test_independent_arithmetic_replays_every_open_priced_row(self):
        groups = V.load_alias_groups()
        open_priced = [m for m in SNAPSHOT['matches'] if m.get('state') == 'open' and m.get('probabilities') is not None]
        self.assertTrue(open_priced, 'snapshot must have open priced matches')
        for m in open_priced:
            replayed, kind = V.replay_quote(m['evidence'][0], m['teams'], groups)
            self.assertIn(kind, ('exchange_mid', 'pinnacle_devig', 'book_devig', 'valve_vrs', 'vrs_mirror'))
            self.assertAlmostEqual(m['probabilities'][0], replayed[0], places=6, msg=m['id'])
            self.assertAlmostEqual(m['probabilities'][1], replayed[1], places=6, msg=m['id'])
            self.assertAlmostEqual(replayed[0] + replayed[1], 1.0, places=9, msg=m['id'])
            higher = m['teams'][0 if replayed[0] > replayed[1] else 1]
            self.assertEqual(m['pick'], higher, m['id'])

    def test_negative_hotspawn_vote_leak_is_rejected(self):
        bad = copy.deepcopy(SNAPSHOT)
        open_row = next(m for m in bad['matches'] if m.get('state') == 'open' and m.get('evidence'))
        open_row['evidence'][0]['total_picks'] = 420
        report = V.audit_snapshot(bad)
        self.assertTrue(any('Hotspawn crowd-vote or URL leaked' in p for p in report['problems']))

    def test_negative_50_50_placeholder_is_rejected(self):
        bad = copy.deepcopy(SNAPSHOT)
        open_row = next(m for m in bad['matches'] if m.get('state') == 'open' and m.get('probabilities'))
        open_row['probabilities'] = [0.5, 0.5]
        open_row['fair_odds'] = [2.0, 2.0]
        report = V.audit_snapshot(bad)
        self.assertTrue(any('50/50' in p for p in report['problems']))

    def test_negative_priced_row_without_pick_is_rejected(self):
        bad = copy.deepcopy(SNAPSHOT)
        open_row = next(m for m in bad['matches'] if m.get('state') == 'open' and m.get('probabilities'))
        open_row['pick'] = None
        report = V.audit_snapshot(bad)
        self.assertTrue(any('pick None !=' in p for p in report['problems']))

    def test_negative_flipped_pick_is_rejected(self):
        bad = copy.deepcopy(SNAPSHOT)
        open_row = next(m for m in bad['matches'] if m.get('state') == 'open' and m.get('probabilities'))
        other = open_row['teams'][0] if open_row['pick'] == open_row['teams'][1] else open_row['teams'][1]
        open_row['pick'] = other
        report = V.audit_snapshot(bad)
        self.assertTrue(any('!= higher probability team' in p for p in report['problems']))

    def test_negative_tampered_probability_is_rejected(self):
        bad = copy.deepcopy(SNAPSHOT)
        open_row = next(m for m in bad['matches'] if m.get('state') == 'open' and m.get('probabilities'))
        open_row['probabilities'] = [0.91, 0.09]
        open_row['fair_odds'] = [1.0 / 0.91, 1.0 / 0.09]
        open_row['pick'] = open_row['teams'][0]
        report = V.audit_snapshot(bad)
        self.assertTrue(any('replayed probabilities' in p for p in report['problems']))

    def test_negative_non_featured_missing_hltv_attempt_is_rejected(self):
        bad = copy.deepcopy(SNAPSHOT)
        non_ex = next(m for m in bad['matches'] if m.get('state') == 'open' and m.get('method') != 'exchange')
        non_ex['attempts'] = [a for a in (non_ex.get('attempts') or []) if 'hltv.org' not in str(a.get('url') or '')]
        non_ex.pop('hltv_context', None)
        non_ex.pop('hltv_team_pages', None)
        report = V.audit_snapshot(bad)
        self.assertTrue(any('missing HLTV attempt' in p for p in report['problems']))

    def test_review_note_is_registered_and_rendered(self):
        notes = json.loads((ROOT / 'data' / 'review-notes.json').read_text())
        note = next((n for n in notes if n.get('id') == 'session-fbea4413-audit-receipt-2026-10-24'), None)
        self.assertIsNotNone(note)
        self.assertGreaterEqual(len(note.get('sources') or []), 3)
        for src in note['sources']:
            self.assertTrue(str(src.get('url') or '').startswith('https://'))
        review_html = (ROOT / 'review.html').read_text()
        self.assertIn('session-fbea4413-audit-receipt-2026-10-24', review_html)


if __name__ == '__main__':
    unittest.main()
