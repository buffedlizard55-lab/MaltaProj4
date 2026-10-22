from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent


def load_auditor():
    spec = importlib.util.spec_from_file_location(
        "audit_repo_86b56cf6", ROOT / "verification-86b56cf6/audit_repo_86b56cf6.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def early_attested_capture(data):
    return (data.get('generated_at') in ('2026-10-22T07:58:54.670274Z', '2026-10-22T08:58:49.178528Z')
            and data.get('generated_at', '') <= data.get('built_at', '') < '2026-10-22T10:54:00Z')


class TestSession86b56cf6ForensicVerification(unittest.TestCase):
    """End-to-end regression suite for session 86b56cf6 line-by-line repo & site verification."""

    @classmethod
    def setUpClass(cls) -> None:
        auditor = load_auditor()
        cls.audit = auditor.audit_all(ROOT)

    def test_zero_audit_errors_across_entire_repo_and_html(self) -> None:
        self.assertEqual(self.audit["errors"], [], f"Forensic audit errors: {self.audit['errors']}")
        self.assertEqual(self.audit["status"], "ok")

    def test_all_open_matches_picked_and_hotspawn_never_used_for_probability(self) -> None:
        data = json.loads((ROOT / 'data/latest.json').read_text())
        opens = [m for m in data['matches'] if m['state'] == 'open']
        self.assertEqual(self.audit['rows_open'], len(opens))
        self.assertEqual(self.audit['rows_open_picked'], sum(bool(m.get('pick')) for m in opens))
        self.assertEqual(self.audit['rows_open_priced'], sum(m.get('probabilities') is not None for m in opens))
        if early_attested_capture(data):
            self.assertGreater(self.audit['rows_open'], 0)
            self.assertEqual(self.audit['rows_open_picked'], self.audit['rows_open'])
            self.assertGreaterEqual(self.audit['rows_open_priced'], 39)

    def test_every_html_table_row_across_all_nine_pages_carries_trusted_external_source_link(self) -> None:
        data = json.loads((ROOT / 'data/latest.json').read_text())
        parsed = [BeautifulSoup((ROOT / page).read_text(), 'html.parser') for page in self.audit['html_pages']]
        tables = [table for soup in parsed for table in soup.find_all('table')]
        rows = [row for table in tables for row in table.find_all('tr') if row.find('td')]
        self.assertEqual(self.audit['html_tables_checked'], len(tables))
        self.assertEqual(self.audit['html_rows_checked'], len(rows))
        if early_attested_capture(data):
            self.assertEqual(self.audit['html_tables_checked'], 38)
            self.assertGreaterEqual(self.audit['html_rows_checked'], 575)
        for page_name in (
            "index.html",
            "picks.html",
            "unresolved.html",
            "matches.html",
            "analysis.html",
            "evidence.html",
            "sources.html",
            "review.html",
        ):
            self.assertIn(page_name, self.audit["html_pages"])

    def test_lineup_receipts_100_percent_hltv_verified_with_zero_hallucinated_rosters(self) -> None:
        doc = json.loads((ROOT / "data/lineup-receipts.json").read_text())
        by_id = {str(r["fixture_id"]): r for r in doc["receipts"]}
        self.assertTrue(
            {"1081597", "1081869", "1082769", "1079654", "1081149", "1081150", "1082860", "1082919", "1082925", "1082926"}.issubset(
                by_id.keys()
            )
        )
        self.assertEqual(
            by_id["1081869"]["lineups"][0]["players"],
            ["swiftsteel", "fineshine52", "Apraki", "Freeman", "Terryyy"],
        )
        self.assertEqual(
            by_id["1082769"]["lineups"][0]["players"],
            ["xeedo", "qw1nk1", "kashl1d", "X5G7V", "clax"],
        )
        self.assertEqual(
            by_id["1082769"]["lineups"][1]["players"],
            ["matusik", "torox", "hurtfrisk", "VRONSKY", "Pryan3ch"],
        )
        self.assertEqual(
            by_id["1081149"]["lineups"][0]["players"],
            ["YumsaN", "HeCkBNk", "KusMe", "Lack1", "NickelBack"],
        )
        self.assertEqual(
            by_id["1081149"]["lineups"][1]["players"],
            ["Sapec", "L00m1", "dottie", "Mann3n", "dan1"],
        )
        self.assertEqual(
            by_id["1082860"]["lineups"][1]["players"],
            ["w0mbat", "xelja", "Hazel", "lzj", "kasze"],
        )

    def test_review_page_flags_unpriced_vrs_proof_and_remediated_irregularities(self) -> None:
        review_html = (ROOT / "review.html").read_text()
        for note_id in (
            "86b56cf6-board-status-41-of-43-and-unpriced-proof-2026-10-22",
            "86b56cf6-lineup-receipts-audit-2026-10-22",
            "86b56cf6-book-receipts-audit-and-renewal-2026-10-22",
        ):
            self.assertIn(note_id, review_html)

    def test_mobile_first_executive_summary_direct_links_and_responsive_layout(self) -> None:
        soup = BeautifulSoup((ROOT / "index.html").read_text(), "html.parser")
        vp = soup.find("meta", attrs={"name": "viewport"})
        self.assertIsNotNone(vp)
        self.assertIn("width=device-width", vp["content"])
        hrefs = {a.get("href", "") for a in soup.find_all("a", href=True)}
        for target in ("picks.html", "unresolved.html", "matches.html", "analysis.html", "sources.html", "review.html"):
            self.assertIn(target, hrefs)


if __name__ == "__main__":
    unittest.main()
