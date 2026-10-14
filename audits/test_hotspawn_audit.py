import json
import unittest
from audits.hotspawn_audit import audit

NOW = "2026-10-14T04:42:38Z"


def page(rows, links=None):
    return '<div class="vs-card"></div><script id="ng-state" type="application/json">' + json.dumps({
        "unstable-request-hash": {"b": rows},
        "another-hash": {"b": {"permalinks": links or {}}},
    }) + '</script>'


def row(**kwargs):
    return {"id": "1081111", "sport_alias": "cs2", "status": "scheduled",
            "scheduled_start_time": "1791964800000", "participants0_name": "Enjoy",
            "participants1_name": "B8 Academy", **kwargs}


class SourceAuditTests(unittest.TestCase):
    def test_keeps_cards_without_detail_links(self):
        result = audit(page([row()]), NOW)
        self.assertEqual(result["embedded_cs2_record_count"], 1)
        self.assertIn("no_match_detail_permalink", result["rows"][0]["flags"])

    def test_does_not_treat_past_scheduled_as_upcoming(self):
        result = audit(page([row(scheduled_start_time="1782469800000")]), NOW)
        self.assertEqual(result["past_date_record_count"], 1)
        self.assertIn("past_date_still_scheduled", result["rows"][0]["flags"])

    def test_no_vote_leak_into_evidence(self):
        result = audit(page([row(participants0_picked_percent=99, participants1_picked_percent=1)]), NOW)
        self.assertNotIn("picked_percent", json.dumps(result))
        self.assertNotIn("probability", json.dumps(result))

    def test_utc_uses_epoch_not_rendered_local_clock(self):
        result = audit(page([row()]), NOW)
        self.assertEqual(result["rows"][0]["scheduled_start_utc_derived"], "2026-10-14T08:00:00+00:00")

    def test_unknown_fields_stay_null(self):
        result = audit(page([row(scheduled_start_time="invalid")]), NOW)
        self.assertIsNone(result["rows"][0]["scheduled_start_utc_derived"])
        self.assertIsNone(result["rows"][0]["best_of"])
        self.assertEqual(result["unknown_date_record_count"], 1)

    def test_failed_fetch_never_means_empty_lobby(self):
        for html in ["Access denied", page([])]:
            with self.assertRaises(ValueError):
                audit(html, NOW)

    def test_duplicate_ids_fail_closed(self):
        with self.assertRaises(ValueError):
            audit(page([row(), row()]), NOW)

    def test_excludes_other_sports(self):
        result = audit(page([row(), row(id="2", sport_alias="lol")]), NOW)
        self.assertEqual(result["embedded_cs2_record_count"], 1)

    def test_naive_time_rejected(self):
        with self.assertRaises(ValueError):
            audit(page([row()]), "2026-10-14T04:42:38")


if __name__ == "__main__":
    unittest.main()
