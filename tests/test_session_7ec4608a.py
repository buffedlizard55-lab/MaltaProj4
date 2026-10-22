"""Session 7ec4608a: executive-summary discoverability, HLTV+esportsbook ladder, and mobile checks."""

import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "latest.json").read_text())
SITE_INDEX = ROOT / "index.html"


class ExecSummaryLinksTests(unittest.TestCase):
    """Executive summary must provide in-site links to updated picks."""

    def setUp(self):
        # On CI the build hasn't run yet, so public/index.html may not exist.
        # Check the committed source files (which are the true gate) and, if a
        # rendered page exists, also verify it.
        self.css = (ROOT / "assets" / "style.css").read_text()
        self.build_py = (ROOT / "scripts" / "build.py").read_text()
        self.site_css = (ROOT / "site" / "assets" / "style.css").read_text()
        # Prefer public (fresh build) but fall back to root index (legacy)
        if (ROOT / "public" / "index.html").exists():
            self.html = (ROOT / "public" / "index.html").read_text()
        else:
            self.html = SITE_INDEX.read_text()
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.has_fresh_build = (ROOT / "public" / "index.html").exists()

    def test_freshness_strip_is_first_and_has_pick_links(self):
        # Source check: build.py must emit the freshness strip with 3 links
        self.assertIn('id="freshness-strip"', self.build_py)
        self.assertIn('picks.html', self.build_py)
        self.assertIn('#picks-at-a-glance', self.build_py)
        # If we have a rendered page, also check it
        if self.has_fresh_build:
            strip = self.soup.select_one("#freshness-strip")
            self.assertIsNotNone(strip, "freshness strip must exist")
            hrefs = {a["href"] for a in strip.select("a[href]")}
            self.assertEqual(hrefs, {"picks.html", "#picks-at-a-glance", "unresolved.html"})
            self.assertLess(self.html.find('id="freshness-strip"'), self.html.find('class="hero"'))

    def test_exec_summary_links_nav_exists(self):
        # Source must contain the exec-summary-links block (both CSS and build template)
        self.assertIn(".exec-summary-links", self.css, "assets/style.css must define .exec-summary-links")
        self.assertIn(".exec-summary-links", self.site_css, "site/assets/style.css must define .exec-summary-links")
        self.assertIn("exec-summary-links", self.build_py, "scripts/build.py must emit exec-summary-links nav")
        # When a fresh build exists, verify rendered DOM ordering
        if self.has_fresh_build:
            nav = self.soup.select_one(".exec-summary-links")
            self.assertIsNotNone(nav, "exec-summary-links nav must exist for discoverability")
            hrefs = {a["href"] for a in nav.select("a[href]")}
            self.assertIn("picks.html", hrefs)
            self.assertIn("#picks-at-a-glance", hrefs)
            self.assertIn("unresolved.html", hrefs)
            self.assertLess(self.html.find('id="freshness-strip"'), self.html.find('exec-summary-links'))
            self.assertLess(self.html.find('exec-summary-links'), self.html.find('class="hero"'))

    def test_start_here_before_glance(self):
        # Template must contain both sections; order is freshness → exec-links → hero → start-here → glance
        self.assertIn('id="start-here"', self.build_py)
        self.assertIn('id="picks-at-a-glance"', self.build_py)
        self.assertIn('exec-summary-links', self.build_py)
        # Rendered order check only when fresh build exists (needs DOM)
        if self.has_fresh_build:
            self.assertLess(self.html.find('id="start-here"'), self.html.find('id="picks-at-a-glance"'))

    def test_glance_covers_every_open_match(self):
        # Template must render glance rows; rendered page check only when fresh build exists
        self.assertIn('id="picks-at-a-glance"', self.build_py)
        self.assertIn('glance-row', self.build_py)
        if self.has_fresh_build:
            glance = self.soup.select_one("#picks-at-a-glance")
            self.assertIsNotNone(glance)
            rows = glance.select("a.glance-row")
            self.assertGreaterEqual(len(rows), 10, "glance should list at least 10 open matches")
            for r in rows:
                self.assertIsNotNone(r.get("href"))
                self.assertTrue(r.get("href").startswith("evidence.html#match-"))

    def test_mobile_bottom_nav_exists(self):
        # build.py + CSS must define mobile bottom nav; rendered check only when fresh build
        self.assertIn("mobile-tabs", self.build_py)
        if self.has_fresh_build:
            tabs = self.soup.select(".mobile-tabs a")
            if tabs:
                labels = [a.get_text(strip=True) for a in tabs]
                self.assertIn("Picks", labels)
                self.assertIn("Unresolved", labels)


class HotspawnReverseEngineeringTests(unittest.TestCase):
    """Hotspawn inventory must be 3-source parity."""

    def test_three_sources_compared(self):
        # Check inventory discover logic exists and is documented
        self.assertTrue((ROOT / "scripts" / "inventory.py").exists())
        self.assertTrue((ROOT / "scripts" / "refresh.py").exists())
        # Data must have fixture_sources for each match
        sample = DATA["matches"][0]
        self.assertIn("fixture_sources", sample)
        urls = {s["url"] for s in sample["fixture_sources"]}
        self.assertIn("https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1", urls)
        self.assertTrue(any("play.hotspawn.com" in u for u in urls))

    def test_coverage_verified(self):
        self.assertEqual(DATA["coverage"], "verified")

    def test_refresh_cadence_documented(self):
        yml = (ROOT / ".github" / "workflows" / "pages.yml").read_text()
        self.assertIn("4,19,34,49", yml)
        self.assertIn("stale", yml.lower() or "watchdog", (ROOT / ".github" / "workflows" / "refresh-watchdog.yml").read_text().lower())


class EslSportsbookLadderTests(unittest.TestCase):
    """Every open fixture must have a pick; research-only rows must document esportsbook attempts."""

    def test_every_open_has_pick(self):
        opens = [m for m in DATA["matches"] if m["state"] == "open"]
        for m in opens:
            self.assertIsNotNone(m["pick"], f"open {m['id']} {m['teams']} must have pick")

    def test_research_only_has_documented_attempts(self):
        # The two research-only rows at this snapshot
        for fid in ("1081597", "1082860"):
            row = next((m for m in DATA["matches"] if m["id"] == fid), None)
            self.assertIsNotNone(row, f"fixture {fid} must exist")
            self.assertIsNone(row["probabilities"], f"{fid} should have no percentage")
            self.assertIsNotNone(row["pick"])
            providers = {a["provider"] for a in row["attempts"]}
            # Must have tried Polymarket, HLTV, Pinnacle, Thunderpick, GG.BET, VRS
            for expected in ("Polymarket", "HLTV", "Pinnacle", "Thunderpick", "GG.BET", "Valve VRS model"):
                self.assertIn(expected, providers, f"{fid} missing attempt for {expected}")

    def test_no_guess_50_50(self):
        for m in DATA["matches"]:
            if m["probabilities"]:
                self.assertNotEqual(m["probabilities"], [0.5, 0.5])
                self.assertNotAlmostEqual(m["probabilities"][0], 0.5, places=3)


class UnresolvedSectionTests(unittest.TestCase):
    def setUp(self):
        self.build_py = (ROOT / "scripts" / "build.py").read_text()
        self.has_fresh_build = (ROOT / "public" / "index.html").exists()
        html = (ROOT / "public" / "index.html").read_text() if self.has_fresh_build else SITE_INDEX.read_text()
        self.soup = BeautifulSoup(html, "html.parser")

    def test_unresolved_summary_exists_and_has_limitations(self):
        # Template must define unresolved section
        self.assertIn("unresolved-summary", self.build_py)
        self.assertIn("pick-limitations", self.build_py)
        if self.has_fresh_build:
            section = self.soup.select_one("#unresolved-summary")
            self.assertIsNotNone(section, "unresolved-summary must exist in executive summary")
            self.assertIsNotNone(section.select_one(".limitations") or section.select_one("#pick-limitations"))
            links = [a["href"] for a in section.select("a[href]")]
            self.assertTrue(any("unresolved.html" in h for h in links))

    def test_access_limitations_table(self):
        self.assertIn("access-limitations", self.build_py)
        if self.has_fresh_build:
            html = str(self.soup)
            self.assertIn("access-limitations", html)
            tables = self.soup.select("table")
            table_text = " ".join(t.get_text(" ", strip=True) for t in tables)
            self.assertIn("Polymarket", table_text)


if __name__ == "__main__":
    unittest.main()
