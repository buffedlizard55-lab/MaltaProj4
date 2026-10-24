"""Regression suite for session cecfe864 (2026-10-24).

Covers:
1. ``research/session-0cc1138a/verify_0cc1138a.py`` re-derives source outcome
   labels mapped through receipted ``ev['identity_sources']`` entries (such as
   ``Projeto do KinGui`` <-> ``Tropa do KinGui`` on fixture ``1083121``), while
   still rejecting unverified or source-less aliases.
2. ``.github/workflows/pages.yml`` guards ``publish()`` commands with explicit
   ``|| return 1`` (so ``set +e; publish; rc=$?; set -e`` cannot ignore a
   failing validator or unit suite) and rebuilds ``public/`` before ``publish``
   when replaying onto ``origin/main``.
3. ``site/assets/style.css`` and ``assets/style.css`` stay byte-identical with
   balanced braces.
4. Independent line-by-line audit (``scripts.audit_cecfe864``) passes with zero
   errors across all open and not-open rows, verifying HLTV-first then
   esportsbook/betting-line fallback trails on every non-featured open row.
5. Executive summary in-site links, separate unresolved/limitations section,
   and session cecfe864 review notes published on ``review.html``.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import audit_cecfe864, build

ROOT = Path(__file__).resolve().parents[1]


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_0cc1138a",
        ROOT / "research" / "session-0cc1138a" / "verify_0cc1138a.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifierIdentitySourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = _load_verifier()

    def test_receipted_identity_source_maps_projeto_to_tropa_do_kingui(self):
        id_sources = [
            {
                "canonical": "Tropa do KinGui",
                "names": ["Tropa do KinGui", "Projeto do KinGui", "ex-Keyd Stars"],
                "source": "https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7",
                "basis": "Five-for-five active lineup and UTC slot parity across HLTV and Polymarket.",
            }
        ]
        ordered = self.v.order_prices(
            ["Tropa do KinGui", "MEIA NOITE"],
            [0.615, 0.385],
            ["Projeto do KinGui", "MEIA NOITE"],
            id_sources,
        )
        self.assertEqual(ordered, [0.615, 0.385])

    def test_unverified_or_sourceless_alias_is_still_refused(self):
        with self.assertRaises(ValueError):
            self.v.order_prices(
                ["Tropa do KinGui", "MEIA NOITE"],
                [0.615, 0.385],
                ["Projeto do KinGui", "MEIA NOITE"],
                [],
            )
        with self.assertRaises(ValueError):
            self.v.order_prices(
                ["Tropa do KinGui", "MEIA NOITE"],
                [0.615, 0.385],
                ["Projeto do KinGui", "MEIA NOITE"],
                [{"names": ["Tropa do KinGui", "Projeto do KinGui"], "source": "http://bad", "basis": "x"}],
            )
        # Even with https source + basis, a fabricated alias not in data/identities.json is refused
        with self.assertRaises(ValueError):
            self.v.order_prices(
                ["Fabricated Club Alpha", "MEIA NOITE"],
                [0.615, 0.385],
                ["Invented Alias Beta", "MEIA NOITE"],
                [
                    {
                        "names": ["Fabricated Club Alpha", "Invented Alias Beta"],
                        "source": "https://www.hltv.org/matches/1/fake",
                        "basis": "not in data/identities.json",
                    }
                ],
            )


class PublisherWorkflowHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yml = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        start = cls.yml.index("Keep the legacy main:/ root fallback on the verified build")
        end = cls.yml.index("Record the exact artifact expected at the public site")
        cls.step = cls.yml[start:end]

    def test_branch_is_registered(self):
        self.assertIn("arena/cecfe864-maltaproj4", self.yml)

    def test_publish_function_guards_commands_under_set_plus_e(self):
        self.assertIn(
            "python -m scripts.publish_root_fallback --public public --root . --cooldown-hours 0.2 || return 1",
            self.step,
        )
        self.assertIn(
            "python -m scripts.validate --data data/latest.json --site . || return 3",
            self.step,
        )
        self.assertIn("python -m unittest discover -s tests 2>&1 | tee runtime/staged-root-unit.log", self.step)
        self.assertIn("return 3", self.step)
        self.assertIn("--check-drift --revision", self.step)


class StylesheetAndAuditContractTests(unittest.TestCase):
    def test_canonical_and_published_stylesheets_match_and_balance(self):
        site_css = (ROOT / "site" / "assets" / "style.css").read_text(encoding="utf-8")
        root_css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
        self.assertEqual(site_css, root_css)
        self.assertEqual(site_css.count("{"), site_css.count("}"))

    def test_independent_cecfe864_audit_passes_with_zero_errors(self):
        res = audit_cecfe864.audit_snapshot(ROOT / "data" / "latest.json")
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["coverage"], "verified")
        self.assertGreater(res["rows_open"], 0)
        self.assertEqual(res["open_with_pick"] + res["open_unresolved"], res["rows_open"])
        for nf in res["non_featured_ledger"]:
            providers = [a["provider"] for a in nf["attempt_trail"]]
            self.assertIn("HLTV", providers, nf["id"])

    def test_executive_summary_links_and_review_notes(self):
        snap = json.loads((ROOT / "data" / "latest.json").read_text(encoding="utf-8"))
        soup = BeautifulSoup(build.overview(copy.deepcopy(snap)), "html.parser")
        exec_bar = soup.select_one("#exec-summary")
        self.assertIsNotNone(exec_bar)
        hrefs = {a.get("href") for a in exec_bar.select("a[href]")}
        self.assertTrue(
            {"picks.html", "#picks-at-a-glance", "#unresolved-summary", "unresolved.html", "matches.html", "review.html"}
            <= hrefs,
            hrefs,
        )
        self.assertIsNotNone(soup.select_one("#unresolved-limits"))
        self.assertIsNotNone(soup.select_one("#unresolved-summary"))

        notes = json.loads((ROOT / "data" / "review-notes.json").read_text(encoding="utf-8"))
        note_ids = {n["id"] for n in notes}
        for expected_id in (
            "session-cecfe864-publisher-replay-and-identity-verifier-2026-10-24",
            "session-cecfe864-31open-board-line-by-line-review-2026-10-24",
        ):
            self.assertIn(expected_id, note_ids)
        review_html = (ROOT / "review.html").read_text(encoding="utf-8")
        self.assertIn("session-cecfe864-publisher-replay-and-identity-verifier-2026-10-24", review_html)
        self.assertIn("session-cecfe864-31open-board-line-by-line-review-2026-10-24", review_html)


if __name__ == "__main__":
    unittest.main()
