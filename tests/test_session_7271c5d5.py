"""Deterministic unit, replay, and independent verification tests for session 7271c5d5.

Avoids brittle hardcoded open-row counts on ``data/latest.json`` so scheduled
15-minute cron refreshes remain permanently green while strictly enforcing:
1. End-to-end replay of ``egw-4yp_dlKtNl-nexora-k27`` (`1082769 K27 vs NEXORA`)
   through ``scripts.books.reobserve``, ``scripts.core.book_research_pick``,
   ``scripts.validate.validate_data``, and ``verification-c6/audit_snapshot.py``.
2. Automatic supersession whenever a valid live exchange/bookmaker quote passes
   strict gates (and fail-closed placeholder ``1.8 / 1.8`` rejection).
3. Canonical URL & primary-evidence hygiene across ``data/book-receipts.json``
   and ``data/lineup-receipts.json`` (including zero ``2-1`` hallucination on
   forfeit match ``2399691`` and zero synthetic ``/match/CCTEU8/`` or ``/match/DFRAG26/`` slugs).
4. Full pass of ``verification-7271c5d5/audit_board_7271c5d5.py`` across the
   committed snapshot and a fresh ``scripts.build`` site directory (executive
   summary links, phone tabs, unresolved section, 0 broken internal links,
   and official ``https://`` source links on every displayed table row).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts import books, core, hltv, validate, vrs


ROOT = Path(__file__).resolve().parents[1]


class Session7271c5d5Tests(unittest.TestCase):
    def test_k27_nexora_receipt_end_to_end_validator_and_c6_audit(self) -> None:
        receipt = next((r for r in core.book_receipts() if r.get("id") == "egw-4yp_dlKtNl-nexora-k27"), None)
        self.assertIsNotNone(receipt)

        raw_row = {
            "id": 1082769,
            "sport_alias": "cs2",
            "participants0_id": 9001,
            "participants0_name": "K27",
            "participants1_id": 9002,
            "participants1_name": "NEXORA",
            "competition_name": "CIS LAN Championship #9",
            "tier": "c",
            "best_of": 3,
            "status": "scheduled",
            "scheduled_start_time": "2026-10-22T17:30:00Z",
            "lock_time": "2026-10-22T17:25:00Z",
        }
        now_iso = "2026-10-22T02:00:00Z"
        now = core.dt(now_iso)
        row = core.normalize_fixtures([raw_row], {}, now)[0]
        core.book_research_pick(row, now=now)

        self.assertEqual(row["pick"], "K27")
        self.assertEqual(row["method"], "bookmaker_fallback")
        self.assertAlmostEqual(row["probabilities"][0], 0.8880605196798597, places=12)
        self.assertAlmostEqual(row["probabilities"][1], 0.11193948032014032, places=12)

        snap = {
            "schema_version": 2,
            "generated_at": now_iso,
            "last_attempt_at": now_iso,
            "fixtures_observed_at": "2026-10-22T01:55:00Z",
            "fixture_evidence": [raw_row],
            "matches": [row],
        }
        validate.validate_data(snap)

        spec = importlib.util.spec_from_file_location("c6_mod", ROOT / "verification-c6" / "audit_snapshot.py")
        assert spec and spec.loader
        c6 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(c6)
        _, c6_errors = c6.inspect(snap)
        self.assertEqual(c6_errors, [])

    def test_book_and_lineup_receipt_ledgers_are_clean_and_primary_sourced(self) -> None:
        book_doc = json.loads((ROOT / "data" / "book-receipts.json").read_text(encoding="utf-8"))
        for rej in book_doc["rejected_listings"]:
            url = rej.get("url", "")
            self.assertTrue(url.startswith("https://"), url)
            self.assertNotIn("/match/CCTEU8/", url)
            self.assertNotIn("/match/DFRAG26/", url)

        lineup_doc = json.loads((ROOT / "data" / "lineup-receipts.json").read_text(encoding="utf-8"))
        by_fid = {r["fixture_id"]: r for r in lineup_doc["receipts"]}
        for fid in ("1081597", "1081869", "1082769", "1079654", "1081149", "1081150", "1082860"):
            self.assertIn(fid, by_fid)
            entry = by_fid[fid]
            self.assertNotIn("2-1 ex-6666", entry.get("reason", ""))
            for team_name, lu in zip(entry["teams"], entry["lineups"]):
                self.assertEqual(lu["team"], team_name)
                self.assertTrue(lu["source"].startswith("https://www.hltv.org/matches/"))
                self.assertTrue(
                    validate.lineup_source_ok({"id": fid, "teams": entry["teams"]}, team_name, lu["players"])
                )

    def test_reobserve_renews_valid_pair_and_rejects_placeholder_default(self) -> None:
        rec = next(r for r in core.book_receipts() if r.get("id") == "egw-4yp_dlKtNl-nexora-k27")
        now = datetime(2026, 10, 22, 6, 0, tzinfo=timezone.utc)

        class DummySrc:
            def __init__(self, html: str) -> None:
                self.html = html

            def get(self, _label: str, _url: str, _json: bool):
                return self.html, {"observed_at": core.iso(now)}

        valid_html = (
            '<script type="application/ld+json">'
            '{"name":"NEXORA VS K27","startDate":"2026-10-22T17:30:00.000Z"}'
            '</script><div>NEXORA 8.1 Make a bet 1.021 K27</div>'
        )
        renewed, records = books.reobserve([rec], DummySrc(valid_html), now)
        self.assertEqual(records[0]["status"], "renewed")
        self.assertEqual(renewed[0]["observed_at"], "2026-10-22T06:00:00Z")

        placeholder_html = (
            '<script type="application/ld+json">'
            '{"name":"NEXORA VS K27","startDate":"2026-10-22T17:30:00.000Z"}'
            '</script><div>NEXORA 1.8 Make a bet 1.8 K27</div>'
        )
        unchanged, miss = books.reobserve([rec], DummySrc(placeholder_html), now)
        self.assertEqual(miss[0]["status"], "parse_miss")
        self.assertEqual(unchanged[0]["observed_at"], rec["observed_at"])

    def test_full_board_and_fresh_build_pass_independent_auditor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "site"
            subprocess.run(
                [sys.executable, "-m", "scripts.build", "--data", str(ROOT / "data" / "latest.json"), "--out", str(out_dir)],
                cwd=ROOT,
                check=True,
            )
            validate.validate_data(json.loads((ROOT / "data" / "latest.json").read_text()))
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "verification-7271c5d5" / "audit_board_7271c5d5.py"),
                    "--snapshot",
                    str(ROOT / "data" / "latest.json"),
                    "--site-dir",
                    str(out_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            report = json.loads(proc.stdout)
            self.assertEqual(report["errors"], [])
            self.assertGreaterEqual(report["site_stats"]["pages"], 10)
            self.assertGreater(report["site_stats"]["rendered_rows"], 100)


if __name__ == "__main__":
    unittest.main()
