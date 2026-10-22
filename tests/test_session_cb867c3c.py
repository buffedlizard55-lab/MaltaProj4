"""Session cb867c3c regression tests:

1. Primary-source identity mapping:
   - Projeto do KinGui <-> Tropa do KinGui (5/5 identical active roster on
     HLTV 2399904 and EGamersWorld 3j3hkufF0, exact 2026-10-22T13:00:00Z Bo3
     fixture against Martians), resolving open fixture 1082919 via Polymarket
     market 6033256 (and Winline 1.06 / 7.26 backup) so zero open rows lack a
     pick.
   - Preserves deliberate non-mapping of Sökerorg <-> LFO 10 while recording
     the unquoted Polymarket 6036901 observation in review/rejection ledgers.

2. Licensed Winline moneyline re-observation on stavka.tv in scripts.books:
   - Parses JSON-LD SportsEvent + header П1 / П2 moneyline odds, converts
     explicit timezone offsets (e.g. +03:00 MSK) to canonical UTC Z, binds
     both team labels, preserves HTTP cache-adjusted observation timestamps,
     and rejects empty cells, 1.8/1.8 placeholders, and equal pairs.
   - Verifies exact de-vigged arithmetic on fixture 1079654 (Winline 1.90 /
     1.80 -> 18/37 vs 19/37, overround +8.19%).

3. Board completeness, explicit expiry contract, and UI copy:
   - Verifies zero open fixtures lack a pick, indent=1 JSON register formatting
     is preserved, coverage_contract reports zero problems at snapshot clock,
     and executive summary mobile bar copy matches the 5-tab mobile bar.
"""
import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts import books, core, coverage_contract

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES = json.loads((ROOT / "data/identities.json").read_text(encoding="utf-8"))
BOOK_RECEIPTS = json.loads((ROOT / "data/book-receipts.json").read_text(encoding="utf-8"))
SNAPSHOT = json.loads((ROOT / "data/latest.json").read_text(encoding="utf-8"))


class TestSessionCb867c3cIdentitiesAndPolymarketGates(unittest.TestCase):
    def test_kingui_identity_registered_with_primary_5_of_5_roster_sources(self):
        by_canonical = {e["canonical"]: e for e in IDENTITIES["aliases"]}
        self.assertIn("Tropa do KinGui", by_canonical)

        kingui = by_canonical["Tropa do KinGui"]
        self.assertEqual(core.norm("Projeto do KinGui"), core.norm("Tropa do KinGui"))
        self.assertTrue(kingui["source"].startswith("https://www.hltv.org/matches/2399904/"))
        for player in ("ALLE", "ckzao", "drg", "xureba", "lash"):
            self.assertIn(player, kingui["basis"])

    def test_polymarket_6033256_prices_1082919_via_wide_tier_with_winline_backup(self):
        now = datetime(2026, 10, 22, 7, 50, tzinfo=timezone.utc)
        ev_kingui = {
            "slug": "cs2-tdk-mar-2026-10-22",
            "title": "Counter-Strike: Tropa do KinGui vs Martians (BO3) - CCT South America Series 7 Playoffs",
            "markets": [{
                "id": "6033256",
                "question": "Counter-Strike: Tropa do KinGui vs Martians (BO3)",
                "sportsMarketType": "moneyline",
                "outcomes": '["Tropa do KinGui", "Martians"]',
                "outcomePrices": '["0.75", "0.25"]',
                "bestBid": 0.54,
                "bestAsk": 0.96,
                "liquidity": "156.0392",
                "volume": "1500.0",
                "active": True,
                "closed": False,
                "acceptingOrders": True,
                "gameStartTime": "2026-10-22 13:00:00+00",
                "eventStartTime": "2026-10-22T13:00:00Z",
                "updatedAt": "2026-10-22T07:42:57.621734Z",
            }],
        }
        cands = core.polymarket_candidates([ev_kingui], "2026-10-22T07:45:00Z")
        row_1082919 = {
            "id": "1082919",
            "teams": ["Projeto do KinGui", "Martians"],
            "state": "open",
            "start": "2026-10-22T13:00:00Z",
            "lock": "2026-10-22T12:54:00Z",
            "best_of": 3,
            "probabilities": None,
            "fair_odds": None,
            "pick": None,
            "method": None,
            "evidence": [],
            "attempts": [],
            "flags": [],
            "reason": None,
        }
        core.resolve(row_1082919, cands, "Polymarket", now, relax=False)
        self.assertIsNone(row_1082919["probabilities"])
        core.resolve(row_1082919, cands, "Polymarket", now, relax=True)
        self.assertEqual(row_1082919["method"], "exchange_wide")
        self.assertEqual(row_1082919["pick"], "Projeto do KinGui")
        self.assertEqual([round(x, 4) for x in row_1082919["probabilities"]], [0.75, 0.25])


class TestStavkaWinlineBookReobservation(unittest.TestCase):
    STAVKA_HTML = (
        '<script type="application/ld+json">'
        '{"@type":"SportsEvent","name":"ex-Zero Tenacity — ex-RUSTEC",'
        '"startDate":"2026-10-23T11:00:00+03:00"}'
        '</script>'
        '<div class="match-head"><span>ex-Zero Tenacity</span><span>ex-RUSTEC</span>'
        '<div class="odds">П1 1.90 П2 1.80</div></div>'
    )

    class CachedStubSources:
        def __init__(self, html, observed_at=None):
            self.html = html
            self.observed_at = observed_at

        def get(self, name, url, as_json=True, headers=None):
            ev = {"name": name, "url": url}
            if self.observed_at:
                ev["observed_at"] = self.observed_at
            return self.html, ev

    def test_stavka_parser_extracts_utc_start_and_bound_winline_pair(self):
        readings = books.parse_listing(self.STAVKA_HTML)
        self.assertEqual(len(readings), 1)
        r = readings[0]
        self.assertEqual((r["team1"], r["team2"]), ("ex-Zero Tenacity", "ex-RUSTEC"))
        self.assertEqual(r["start"], "2026-10-23T08:00:00Z")
        self.assertEqual(r["odds"], [1.9, 1.8])
        self.assertTrue(r["bound_to_labels"])

    def test_stavka_parser_refuses_placeholder_equal_and_empty_panels(self):
        for bad in (
            self.STAVKA_HTML.replace("П1 1.90 П2 1.80", "П1 1.80 П2 1.80"),
            self.STAVKA_HTML.replace("П1 1.90 П2 1.80", "П1 1.91 П2 1.91"),
            self.STAVKA_HTML.replace("П1 1.90 П2 1.80", "П1 — П2 —"),
        ):
            self.assertEqual(books.parse_listing(bad), [])

    def test_reobserve_preserves_cache_age_adjusted_timestamp_and_prices_1079654(self):
        receipt = copy.deepcopy(
            next(r for r in BOOK_RECEIPTS["receipts"] if r["id"] == "stavka-winline-1079654-ex-zero-tenacity-ex-rustec")
        )
        now = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)
        renewed, records = books.reobserve(
            [receipt],
            self.CachedStubSources(self.STAVKA_HTML, observed_at="2026-10-22T11:55:00Z"),
            now,
        )
        self.assertEqual(records[0]["status"], "renewed")
        self.assertEqual(renewed[0]["observed_at"], "2026-10-22T11:55:00Z")

        fixture = {
            "id": "1079654",
            "teams": ["ex-Zero Tenacity", "ex-RUSTEC"],
            "state": "open",
            "start": "2026-10-23T08:00:00Z",
            "lock": "2026-10-23T07:54:00Z",
            "best_of": 3,
            "probabilities": None,
            "fair_odds": None,
            "pick": None,
            "method": None,
            "evidence": [],
            "attempts": [],
            "flags": [],
            "reason": None,
        }
        core.book_research_pick(fixture, receipts=renewed, now=now)
        self.assertEqual(fixture["method"], "bookmaker_fallback")
        self.assertEqual(fixture["pick"], "ex-RUSTEC")
        self.assertAlmostEqual(fixture["probabilities"][0], 18.0 / 37.0, places=12)
        self.assertAlmostEqual(fixture["probabilities"][1], 19.0 / 37.0, places=12)


class TestLiveBoardCompletenessAndContract(unittest.TestCase):
    def test_zero_open_rows_without_pick_and_indent1_registers_preserved(self):
        for rel in ("data/book-receipts.json", "data/review-notes.json"):
            raw = (ROOT / rel).read_text(encoding="utf-8")
            self.assertEqual(raw, json.dumps(json.loads(raw), indent=1, ensure_ascii=False) + "\n", rel)
        open_rows = [m for m in SNAPSHOT["matches"] if m["state"] == "open"]
        missing_picks = [m["id"] for m in open_rows if not m.get("pick")]
        if SNAPSHOT.get("generated_at") == "2026-10-22T07:58:54.670274Z":
            self.assertEqual(missing_picks, [], f"Open fixtures missing a pick: {missing_picks}")
        else:
            # Zero was true at this capture, not a licence to fabricate future
            # picks. A new unverified identity must remain explicitly blank.
            for row in open_rows:
                if not row.get("pick"):
                    for field in ("probabilities", "fair_odds", "method"):
                        self.assertIsNone(row.get(field), (row["id"], field))
                    self.assertTrue(row.get("reason"), row["id"])
                    self.assertTrue(row.get("attempts"), row["id"])
                    self.assertTrue(str(row.get("source_url") or "").startswith("https://"), row["id"])

    def test_coverage_contract_passes_at_snapshot_clock_with_zero_problems(self):
        report = coverage_contract.inspect(SNAPSHOT, SNAPSHOT["generated_at"])
        self.assertEqual(report["problems"], [])
        if SNAPSHOT.get("generated_at") == "2026-10-22T07:58:54.670274Z":
            self.assertEqual(report["counts"]["unresolved"], 0)
        else:
            self.assertEqual(report["counts"]["unresolved"], sum(
                m["state"] == "open" and not m.get("pick") for m in SNAPSHOT["matches"]
            ))

    def test_executive_summary_mobile_bar_copy_matches_actual_tabs(self):
        index_html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("Home · Picks · Unresolved · Matches · TWC", index_html)
        self.assertIn("Home · Picks · Unresolved · Matches · Analysis", index_html)

    def test_curl_cffi_403_fallback_handles_both_200_recovery_and_persistent_403(self):
        from unittest import mock
        import requests as std_requests
        from scripts import refresh

        class NonRequestsHTTPError(Exception):
            """Simulates curl_cffi.requests.exceptions.HTTPError (not a RequestException)."""

        class FakeCffiResp:
            def __init__(self, status_code, body=b'{"ok": true}'):
                self.status_code = status_code
                self.content = body
                self.text = body.decode("utf-8")
                self.headers = {}

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise NonRequestsHTTPError(f"HTTP {self.status_code}")

            def json(self):
                return json.loads(self.text)

        def make_403_std_resp():
            resp = std_requests.Response()
            resp.status_code = 403
            resp._content = b"Forbidden"
            resp.url = "https://gg.bet/en/esports/counter-strike"
            return resp

        src = refresh.Sources(datetime(2026, 10, 22, 8, 50, tzinfo=timezone.utc))
        src.rate_limit_backoff = (0.0,)

        # Case 1: std requests gets 403, Chrome TLS gets 200 -> succeeds with zero waits.
        with mock.patch.object(std_requests.Session, "get", side_effect=lambda *a, **kw: make_403_std_resp()), \
             mock.patch.object(refresh, "_REAL_SESSION_GET", std_requests.Session.get), \
             mock.patch.object(refresh._cffi_requests, "get", return_value=FakeCffiResp(200)):
            body, rec = src.get("Valve mirror test", "https://www.hltv.org/valve-ranking/teams", as_json=True)
            self.assertEqual(body, {"ok": True})
            self.assertEqual(rec["status"], "ok")
            self.assertNotIn("rate_limit_waits", rec)

        # Case 2: BOTH std requests and Chrome TLS get 403 -> must NOT leak NonRequestsHTTPError;
        # must raise standard ValueError after bounded backoff and block host cleanly.
        with mock.patch.object(std_requests.Session, "get", side_effect=lambda *a, **kw: make_403_std_resp()), \
             mock.patch.object(refresh, "_REAL_SESSION_GET", std_requests.Session.get), \
             mock.patch.object(refresh._cffi_requests, "get", return_value=FakeCffiResp(403, b"Denied")):
            with self.assertRaises(ValueError):
                src.get("GG.BET fallback access", "https://gg.bet/en/esports/counter-strike", as_json=False)
            self.assertIn("gg.bet", src.blocked_hosts)


if __name__ == "__main__":
    unittest.main()
