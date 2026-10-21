"""Roster anchors for duplicated Valve labels (session 2d0a85f2, request R-1).

Valve's official global standings sometimes carry the same label twice for two
different rosters (on 2026-10-05: ``benched gods`` at #157 and #329). The
collector's identity rule then correctly refuses to guess, and a fixture whose
HLTV page has no lineup yet can never resolve — leaving an open Hotspawn match
with no pick at all.

An *anchor* is a dated record (``data/vrs-anchors.json``, installed only by
``scripts/apply_2d0a85f2.py`` after fail-closed validation) that supplies the
official HLTV lineup of the team's most recent *played* match so Valve's own
>=3-shared-player rule (``model/team.js``) can select exactly one row. This
module only injects that exact lineup where the fixture page provides none, and
records on the row where the lineup came from. It never invents players, never
creates a price and never changes a pick tier: with the anchor the existing
pick-only ``research_vrs_single`` tier can fire, publishing a pick and blank
probabilities.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from scripts.core import norm

ANCHORS = Path(__file__).resolve().parents[1] / "data" / "vrs-anchors.json"


def load() -> list[dict[str, Any]]:
    """Anchors installed on disk; an unreadable or missing file yields none."""
    if not ANCHORS.exists():
        return []
    try:
        doc = json.loads(ANCHORS.read_text())
    except Exception:
        return []
    return [a for a in doc.get("anchors", []) if isinstance(a, dict)]


def _official_lineup_source(anchor: dict[str, Any]) -> dict[str, Any]:
    for s in anchor.get("lineup_sources", []) or []:
        if s.get("kind") == "official_hltv_played_match_lineup":
            return s
    return (anchor.get("lineup_sources") or [{}])[0]


def with_anchors(fixture: dict[str, Any], lineups: Optional[dict[str, Any]],
                 anchors: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
    """Add anchor lineups for fixture teams the HLTV fixture page did not list."""
    out = dict(lineups or {})
    have = {norm(t) for t in out}
    teams = [norm(t) for t in fixture.get("teams", [])]
    for anchor in anchors if anchors is not None else load():
        team = anchor.get("team")
        lineup = anchor.get("anchor_lineup")
        if not team or not lineup or norm(team) not in teams or norm(team) in have:
            continue
        out[team] = list(lineup)
        src = _official_lineup_source(anchor)
        fixture.setdefault("attempts", []).append({
            "provider": "Valve VRS roster anchor",
            "status": "resolved",
            "reason": ("Fixture HLTV page lists no lineup yet; the lineup used is the official HLTV lineup of this "
                       "team's most recent played match (%d players, %s of them shared with Valve standings row %d, "
                       "under Valve's own >=3 shared-player rule). Anchor validated by scripts/apply_2d0a85f2.py; "
                       "it enables a pick-only research tier and publishes no probability."
                       % (len(lineup), anchor.get("overlap_selected"), anchor.get("valve_standing"))),
            "url": src.get("url"),
        })
        flag = ("Roster anchor used: a duplicated Valve label was resolved by an official HLTV lineup; "
                "research pick only, no percentage published.")
        if flag not in fixture.setdefault("flags", []):
            fixture["flags"].append(flag)
    return out
