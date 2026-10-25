"""Session 5717f7d9 — independent line-by-line audit of every-match pick coverage.

These regressions pin the contract behind the user's standing brief: every open
Hotspawn CS2 fixture must carry a sourced pick and win probability (or an
explicit, sourced unresolved reason), the numbers must re-derive from the
retained primary evidence, and the rendered dashboard must expose those picks
and limitations on a phone. The auditor under test (``scripts.audit_5717f7d9``)
imports no production pipeline code, so these are independent checks rather
than the pipeline validating itself.

Two groups:

* ``CommittedSnapshot`` — the shipped board satisfies every contract today.
* ``AuditorCatchesDefects`` — the auditor fails closed on synthetic tampering,
  so a green run is evidence rather than a tautology.
"""
import copy
import json
import unittest
from pathlib import Path

from scripts import audit_5717f7d9 as audit

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / "data" / "latest.json").read_text(encoding="utf-8"))
AMAP = audit.load_alias_map()
STANDINGS = audit.load_vendored_standings()


def run_audit():
    findings, ledger, expected = audit.audit(SNAPSHOT, AMAP, STANDINGS)
    site_findings = []
    site = audit.audit_site(SNAPSHOT, site_findings)
    return findings + site_findings, ledger, expected, site


class CommittedSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings, cls.ledger, cls.expected, cls.site = run_audit()
        cls.opens = [m for m in SNAPSHOT["matches"] if m.get("state") == "open"]

    def test_no_hard_failure_or_unexplained_flag(self):
        hard = [f for f in self.findings if f["severity"] in ("fail", "flag")]
        self.assertEqual(hard, [], json.dumps(hard, indent=2))

    def test_full_coverage_every_open_row_picked_and_priced(self):
        self.assertGreater(len(self.opens), 0)
        self.assertEqual(self.expected["with_pick"], self.expected["open"])
        self.assertEqual(self.expected["with_prob"], self.expected["open"])
        self.assertEqual(self.expected["unresolved"], 0)
        for m in self.opens:
            self.assertTrue(m.get("pick"), m["id"])
            self.assertIsNotNone(m.get("probabilities"), m["id"])
            self.assertTrue(m.get("evidence"), m["id"])
            self.assertTrue(m.get("expires_at"), m["id"])

    def test_probabilities_complement_favourite_and_fair_odds(self):
        for m in self.opens:
            p = m["probabilities"]
            self.assertAlmostEqual(sum(p), 1.0, places=12)
            self.assertEqual(len(p), 2)
            if abs(p[0] - p[1]) > audit.EPS:
                self.assertEqual(m["pick"], m["teams"][p.index(max(p))], m["id"])
            for prob, odds in zip(p, m["fair_odds"]):
                self.assertAlmostEqual(odds, 1 / prob, places=6)

    def test_not_open_rows_are_never_priced(self):
        for m in SNAPSHOT["matches"]:
            if m.get("state") != "open":
                self.assertIsNone(m["probabilities"], m["id"])
                self.assertIsNone(m["pick"], m["id"])
                self.assertIsNone(m["method"], m["id"])

    def test_no_probability_originates_from_hotspawn(self):
        for m in self.opens:
            for e in m["evidence"]:
                for key in ("url", "api_url"):
                    url = e.get(key) or ""
                    if e.get("probabilities") is not None:
                        self.assertNotIn("hotspawn.com", url, (m["id"], url))
                        self.assertNotIn("cloudwaysapps.com", url, (m["id"], url))

    def test_exchange_prices_rederive_from_named_raw_outcomes(self):
        # Rotation-proof: only asserts against exchange rows the current board has.
        rows = [m for m in self.opens if m["method"] in ("exchange", "exchange_wide")]
        if not rows:
            self.skipTest("no exchange-tier rows on this snapshot")
        for m in rows:
            e = next(x for x in m["evidence"] if x.get("provider") == "Polymarket" and "raw" in x)
            outcomes = json.loads(e["raw"]["outcomes"])
            prices = [float(x) for x in json.loads(e["raw"]["outcomePrices"])]
            by_name = {audit.norm(name, AMAP): price for name, price in zip(outcomes, prices)}
            for team, published in zip(m["teams"], m["probabilities"]):
                self.assertIn(audit.norm(team, AMAP), by_name, (m["id"], team, outcomes))
                self.assertAlmostEqual(by_name[audit.norm(team, AMAP)], published, places=12)
            self.assertTrue(e["raw"]["acceptingOrders"] and not e["raw"]["closed"], m["id"])

    def test_bookmaker_devig_rederives(self):
        rows = [m for m in self.opens if m["method"] == "bookmaker_fallback"]
        if not rows:
            self.skipTest("no researched-book rows on this snapshot")
        for m in rows:
            e = m["evidence"][0]
            inverse = [1 / float(o) for o in e["decimal_odds"]]
            fair = [x / sum(inverse) for x in inverse]
            for got, want in zip(m["probabilities"], fair):
                self.assertAlmostEqual(got, want, places=12)

    def test_vrs_lines_rederive_and_match_the_vendored_valve_file(self):
        rows = [m for m in self.opens if m["method"] == "model_vrs"]
        if not rows:
            self.skipTest("no originated VRS rows on this snapshot")
        for m in rows:
            e = next(x for x in m["evidence"] if x["provider"] == "Valve VRS model")
            pa, pb = e["points"]
            expect = audit.vrs_expected(pa, pb)
            self.assertAlmostEqual(audit.vrs_calibrated(expect), m["probabilities"][0], places=12)
            # every retained standing/points pair exists verbatim in Valve's file
            for team, pts, standing in zip(e["vrs_teams"], e["points"], e["standings"]):
                row = STANDINGS["by_standing"][standing]
                self.assertEqual(row["points"], pts, (m["id"], team))
                self.assertEqual(audit.plain_name(row["name"]), audit.plain_name(team))

    def test_any_duplicated_valve_label_is_disambiguated_by_roster_overlap(self):
        # Valve repeats some labels for distinct rosters. Wherever the current
        # board uses one, the >=3-player HLTV overlap must select the standing;
        # no fixture id or calendar value is pinned, so this cannot time-bomb.
        duplicated = {name for name, rows in STANDINGS["by_name"].items() if len(rows) > 1}
        model_rows = [m for m in self.opens if m["method"] == "model_vrs"]
        found = False
        for m in model_rows:
            e = next(x for x in m["evidence"] if x["provider"] == "Valve VRS model")
            for i, (team, standing) in enumerate(zip(e.get("vrs_teams", []), e.get("standings", []))):
                if audit.plain_name(team) not in duplicated:
                    continue
                found = True
                chk = e.get("roster_checks", [None, None])[i]
                self.assertIsNotNone(chk, (m["id"], team))
                self.assertGreaterEqual(chk["overlap"], 3, (m["id"], team))
                self.assertEqual(STANDINGS["by_standing"][standing]["points"], e["points"][i])
        if not found:
            self.skipTest("no duplicated-label VRS row on this snapshot")

    def test_executive_summary_quicknav_links_to_picks_and_unresolved(self):
        from bs4 import BeautifulSoup
        index = BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "html.parser")
        qn = index.find(id="exec-quicknav")
        self.assertIsNotNone(qn)
        hrefs = [a["href"] for a in qn.find_all("a", href=True)]
        self.assertTrue(any(h.startswith("picks.html") for h in hrefs))
        self.assertTrue(any("unresolved" in h for h in hrefs))
        self.assertIsNotNone(index.find(id="unresolved-limits"))

    def test_mobile_tab_bar_and_viewport_on_every_real_page(self):
        from bs4 import BeautifulSoup
        for name in ("index.html", "picks.html", "unresolved.html", "matches.html",
                     "analysis.html", "review.html", "sources.html", "evidence.html"):
            soup = BeautifulSoup((ROOT / name).read_text(encoding="utf-8"), "html.parser")
            self.assertIsNotNone(soup.find("meta", attrs={"name": "viewport"}), name)
            tabs = soup.find("nav", class_="mobile-tabs")
            self.assertIsNotNone(tabs, name)
            label = tabs.get_text(" ", strip=True)
            for need in ("Home", "Picks", "Unresolved", "Matches", "Analysis"):
                self.assertIn(need, label, (name, need))

    def test_every_pick_row_has_an_external_source_and_both_percentages(self):
        import re
        from bs4 import BeautifulSoup
        soup = BeautifulSoup((ROOT / "picks.html").read_text(encoding="utf-8"), "html.parser")
        rows = {r["data-match"]: r for r in soup.find_all("tr", attrs={"data-match": True})}
        for m in self.opens:
            row = rows[m["id"]]
            ext = [a["href"] for a in row.find_all("a", href=True) if a["href"].startswith("http")]
            self.assertTrue(ext, m["id"])
            self.assertGreaterEqual(len(re.findall(r"\d+(?:\.\d+)?%", row.get_text(" ", strip=True))), 2, m["id"])
            self.assertIn(m["pick"], row.get_text(" ", strip=True))


class AuditorCatchesDefects(unittest.TestCase):
    def _open_row(self):
        candidates = [x for x in SNAPSHOT["matches"] if x.get("state") == "open"]
        if not candidates:
            self.skipTest("no open fixtures on this snapshot")
        return copy.deepcopy(candidates[0])

    def test_a_wrong_probability_is_a_hard_failure(self):
        m = self._open_row()
        m["probabilities"] = [0.99, 0.01]
        # break the favourite/pick relationship and the fair-odds inverse too
        m["pick"] = m["teams"][1] if m["probabilities"][0] > m["probabilities"][1] else m["teams"][0]
        findings, _, _ = audit.audit({**SNAPSHOT, "matches": [m]}, AMAP, STANDINGS)
        self.assertTrue(any(f["severity"] == "fail" for f in findings))

    def test_a_priced_not_open_row_is_rejected(self):
        m = self._open_row()
        m["state"] = "not_open"
        findings, _, _ = audit.audit({**SNAPSHOT, "matches": [m]}, AMAP, STANDINGS)
        self.assertTrue(any(f["area"] == "not_open_priced" and f["severity"] == "fail" for f in findings))

    def test_missing_evidence_link_is_rejected(self):
        m = self._open_row()
        for e in m["evidence"]:
            e["url"] = None
            e["api_url"] = None
        findings, _, _ = audit.audit({**SNAPSHOT, "matches": [m]}, AMAP, STANDINGS)
        self.assertTrue(any(f["severity"] == "fail" for f in findings))

    def test_tampered_vrs_points_break_rederivation(self):
        candidates = [x for x in SNAPSHOT["matches"]
                      if x.get("state") == "open" and x["method"] == "model_vrs"]
        if not candidates:
            self.skipTest("no model_vrs row on this snapshot")
        m = copy.deepcopy(candidates[0])
        e = next(x for x in m["evidence"] if x["provider"] == "Valve VRS model")
        e["points"] = [e["points"][0] + 400, e["points"][1]]
        findings = []
        audit._audit_vrs(m, audit.parse_ts(SNAPSHOT["generated_at"]), STANDINGS, findings, {"checks": []})
        self.assertTrue(any(f["severity"] == "fail" for f in findings))

    def test_hotspawn_probability_leakage_is_rejected(self):
        m = self._open_row()
        m["evidence"][0]["url"] = "https://www.hotspawn.com/matches/should-never-price"
        findings, _, _ = audit.audit({**SNAPSHOT, "matches": [m]}, AMAP, STANDINGS)
        self.assertTrue(any(f["area"] == "hotspawn_leakage" and f["severity"] == "fail" for f in findings))

    def test_unpriced_row_without_reason_is_rejected(self):
        m = self._open_row()
        m["probabilities"] = None
        m["fair_odds"] = None
        m["pick"] = None
        m["reason"] = None
        m["attempts"] = []
        findings, _, _ = audit.audit({**SNAPSHOT, "matches": [m]}, AMAP, STANDINGS)
        self.assertTrue(any(f["area"] == "unresolved_contract" and f["severity"] == "fail" for f in findings))


if __name__ == "__main__":
    unittest.main()
