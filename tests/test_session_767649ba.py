"""Deterministic unit & first-principles replay tests for session 767649ba.

Deliberately avoids pinning mutable ``data/latest.json`` open-fixture counts or
transient match states so future scheduled cron refreshes remain 100% green.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.books import parse_listing, reobserve
from scripts.core import book_candidate, book_receipts, book_research_pick, quote_book
from scripts.session_767649ba import RECEIPT_ID, apply, load_captures, verify_capture_replay
from scripts.vrs import ROSTER_OVERLAP, identify, parse as parse_vrs


class Session767649baTests(unittest.TestCase):
    ROOT_DIR = Path(__file__).resolve().parents[1]

    def test_k27_nexora_receipt_replays_exact_probabilities_and_corroboration(self):
        summary = verify_capture_replay()
        self.assertEqual(summary['receipt_id'], RECEIPT_ID)
        self.assertEqual(summary['fixture_id'], '1082769')
        self.assertEqual(summary['pick'], 'K27')
        self.assertAlmostEqual(summary['probabilities'][0], 0.8880605196798597, places=12)
        self.assertAlmostEqual(summary['probabilities'][1], 0.11193948032014032, places=12)
        self.assertAlmostEqual(summary['overround'], 0.10288871960435797, places=12)

        # Cross-book corroboration spread across EGW (8.1/1.021), Stavka (7.80/1.06),
        # and KushVSporte (8.20/1.04) is strictly below 0.8 percentage points.
        p_egw = summary['probabilities'][0]
        p_stavka = (1.0 / 1.06) / ((1.0 / 7.80) + (1.0 / 1.06))
        p_kush = (1.0 / 1.04) / ((1.0 / 8.20) + (1.0 / 1.04))
        self.assertLess(abs(p_egw - p_stavka), 0.008)
        self.assertLess(abs(p_egw - p_kush), 0.002)

    def test_book_receipt_present_and_dead_noncanonical_slugs_repaired(self):
        doc = json.loads((self.ROOT_DIR / 'data/book-receipts.json').read_text(encoding='utf-8'))
        receipt = next((r for r in doc['receipts'] if r['id'] == RECEIPT_ID), None)
        self.assertIsNotNone(receipt)
        cand = book_candidate(receipt)
        quote = quote_book(cand, [1, 0], datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc))
        self.assertIsNotNone(quote)
        self.assertAlmostEqual(sum(quote['probabilities']), 1.0, places=9)

        for rej in doc['rejected_listings']:
            url = rej.get('url', '')
            self.assertNotIn('/match/CCTEU8/', url)
            self.assertNotIn('/match/DFRAG26/', url)

    def test_reobserve_accepts_live_asymmetric_pair_and_refuses_18_placeholder(self):
        receipt = next(r for r in book_receipts() if r['id'] == RECEIPT_ID)
        now = datetime(2026, 10, 22, 8, 0, tzinfo=timezone.utc)

        class StubSource:
            def __init__(self, body: str):
                self.body = body

            def get(self, _label: str, _url: str, _json: bool):
                return self.body, {"observed_at": now.isoformat().replace("+00:00", "Z")}

        live_html = (
            '<script type="application/ld+json">'
            '{"name":"NEXORA VS K27","startDate":"2026-10-22T17:30:00.000Z"}'
            '</script>'
            '<div>NEXORA 8.1 Make a bet 1.021 K27</div>'
        )
        renewed, records = reobserve([receipt], StubSource(live_html), now)
        self.assertEqual(records[0]['status'], 'renewed')
        self.assertEqual(renewed[0]['observed_at'], '2026-10-22T08:00:00Z')

        placeholder_html = (
            '<script type="application/ld+json">'
            '{"name":"NEXORA VS K27","startDate":"2026-10-22T17:30:00.000Z"}'
            '</script>'
            '<div>NEXORA 1.8 Make a bet 1.8 K27</div>'
        )
        self.assertEqual(parse_listing(placeholder_html), [])
        not_renewed, miss_records = reobserve([receipt], StubSource(placeholder_html), now)
        self.assertEqual(miss_records[0]['status'], 'parse_miss')
        self.assertEqual(not_renewed[0]['observed_at'], receipt['observed_at'])

    def test_apply_is_strictly_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy_path = Path(tmp) / 'book-receipts.json'
            shutil.copyfile(self.ROOT_DIR / 'data/book-receipts.json', copy_path)
            apply(receipts_path=copy_path)
            first_bytes = copy_path.read_bytes()
            apply(receipts_path=copy_path)
            second_bytes = copy_path.read_bytes()
            self.assertEqual(first_bytes, second_bytes)

    def test_valve_vrs_strict_continuity_edge_cases_proven_on_vendored_standings(self):
        standings = parse_vrs((self.ROOT_DIR / 'data/vrs/standings_global_2026_10_05.md').read_text(encoding='utf-8'))
        # 1. ex-RUSTEC (youka, bl1x1, yiksrezo, Brilliance, jakekeS) ties 3 == 3
        # between #92 RUSTEC (1066 pts) and #152 ex-RUSTEC (824 pts) -> refused (None).
        ex_rustec_entry, ex_rustec_note = identify(
            'ex-RUSTEC', standings, ['youka', 'bl1x1', 'yiksrezo', 'Brilliance', 'jakekeS']
        )
        self.assertIsNone(ex_rustec_entry)
        self.assertIn('same number of players', ex_rustec_note)

        # 2. LFO 10 (Sapec, L00m1, dottie, Mann3n, dan1) is unlisted directly and
        # shares at most 2/5 players across all 380 rows (#156 Entropy), strictly
        # below ROSTER_OVERLAP == 3 even if an alias to Entropy were attempted.
        lfo10_entry, _ = identify('LFO 10', standings, ['Sapec', 'L00m1', 'dottie', 'Mann3n', 'dan1'])
        self.assertIsNone(lfo10_entry)
        entropy_entry, entropy_note = identify('Entropy', standings, ['Sapec', 'L00m1', 'dottie', 'Mann3n', 'dan1'])
        self.assertIsNone(entropy_entry)
        self.assertIn(f'fewer than {ROSTER_OVERLAP} players', entropy_note)

    def test_independent_auditor_passes_fresh_build_zero_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / 'site'
            subprocess.run(
                [sys.executable, '-m', 'scripts.build', '--data', str(self.ROOT_DIR / 'data/latest.json'), '--out', str(out_dir)],
                check=True,
                cwd=self.ROOT_DIR,
            )
            proc = subprocess.run(
                [sys.executable, str(self.ROOT_DIR / 'verification-767649ba/audit_2026_10_22.py'),
                 '--snapshot', str(self.ROOT_DIR / 'data/latest.json'), '--site', str(out_dir)],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.ROOT_DIR,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(payload['failures'], [])
            self.assertGreater(payload['checks_run'], 200)
            self.assertGreaterEqual(payload['open_unpicked'], 0)


if __name__ == '__main__':
    unittest.main()
