"""Independent, read-only audit of a captured official Hotspawn HTML response.

No network requests, odds, votes or invented match facts. Run against a source
snapshot, not against arbitrary text. UTC conversion is explicitly derived.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path

SOURCE = "https://play.hotspawn.com/cs2-pickems"


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_state = False
        self.state_parts = []
        self.cards = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("id") == "ng-state":
            self.in_state = True
        if "vs-card" in attrs.get("class", "").split():
            self.cards += 1

    def handle_data(self, text):
        if self.in_state:
            self.state_parts.append(text)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_state = False


def utc_from_millis(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def audit(html, observed_at, source_url=SOURCE):
    now = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    if now.tzinfo is None:
        raise ValueError("Observed time must include its timezone")
    page = Page()
    page.feed(html)
    if not page.state_parts:
        raise ValueError("No ng-state: discovery failed, NOT an empty lobby")
    state = json.loads("".join(page.state_parts))
    candidates = [v["b"] for v in state.values() if isinstance(v, dict)
                  and isinstance(v.get("b"), list) and v["b"]
                  and isinstance(v["b"][0], dict)
                  and "sport_alias" in v["b"][0]]
    if len(candidates) != 1:
        raise ValueError("Missing or ambiguous match array; cannot claim completeness")
    permalinks = {}
    for v in state.values():
        if isinstance(v, dict) and isinstance(v.get("b"), dict):
            permalinks.update(v["b"].get("permalinks", {}))
    rows = []
    seen = set()
    for raw in candidates[0]:
        if raw.get("sport_alias") != "cs2":
            continue
        match_id = raw.get("id")
        if not match_id or str(match_id) in seen:
            raise ValueError("Missing or duplicate CS2 match ID")
        match_id = str(match_id)
        seen.add(match_id)
        start = utc_from_millis(raw.get("scheduled_start_time"))
        past = datetime.fromisoformat(start) < now if start else None
        flags = []
        if past and raw.get("status") == "scheduled":
            flags.append("past_date_still_scheduled")
        if not start:
            flags.append("unverified_start_time")
        if not raw.get("participants0_name") or not raw.get("participants1_name"):
            flags.append("unverified_team_identity")
        if not permalinks.get(match_id):
            flags.append("no_match_detail_permalink")
        rows.append({
            "hotspawn_id": match_id,
            "team_a": raw.get("participants0_name"),
            "team_b": raw.get("participants1_name"),
            "team_a_source_id": raw.get("participants0_id"),
            "team_b_source_id": raw.get("participants1_id"),
            "competition": raw.get("competition_name"),
            "tier": raw.get("tier"),
            "source_status": raw.get("status"),
            "scheduled_start_epoch_ms": raw.get("scheduled_start_time"),
            "scheduled_start_utc_derived": start,
            "lock_epoch_ms": raw.get("lock_time"),
            "best_of": raw.get("best_of"),
            "source_url": source_url,
            "detail_url": permalinks.get(match_id),
            "past_at_observation": past,
            "flags": flags,
        })
    return {
        "audit_kind": "historical_source_membership_only_not_live_picks",
        "observed_at": observed_at,
        "source_url": source_url,
        "source_sha256": sha256(html.encode()).hexdigest(),
        "rendered_card_count": page.cards,
        "embedded_cs2_record_count": len(rows),
        "past_date_record_count": sum(r["past_at_observation"] is True for r in rows),
        "future_or_present_record_count": sum(r["past_at_observation"] is False for r in rows),
        "unknown_date_record_count": sum(r["past_at_observation"] is None for r in rows),
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--source-url", default=SOURCE)
    args = parser.parse_args()
    print(json.dumps(audit(args.html.read_text(), args.observed_at, args.source_url), indent=2))
