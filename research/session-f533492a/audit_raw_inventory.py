"""Replay every published fixture row against the retained raw Hotspawn bytes.

This is deliberately independent of scripts.core/scripts.inventory. Crowd fields
are excluded only from the retained-evidence comparison; no crowd value is read
as a probability. Primary-source rows may not be missing from the board. Extra
history in a competition supplement is disclosed and cannot enter the board
without a per-row reviewed receipt.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research/harvest-f533492a/sources/manifest.json"
SNAPSHOT = ROOT / "data/latest.json"
OUTPUT = ROOT / "research/session-f533492a/raw-inventory-audit.json"


def retained_fields(row):
    return {key: value for key, value in row.items()
            if "picked" not in key and key != "total_picks"}


def hydrated_rows(document):
    soup = BeautifulSoup(document, "html.parser")
    node = soup.select_one("#ng-state")
    assert node is not None, "Missing ng-state"
    state = json.loads(node.string)
    hits = [value["b"] for value in state.values()
            if isinstance(value, dict)
            and str(value.get("u", "")).endswith("/api/v1/fixtures")
            and isinstance(value.get("b"), list)]
    assert len(hits) == 1, "Expected exactly one hydrated fixture response"
    return hits[0]


def main():
    snapshot = json.loads(SNAPSHOT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    board = {str(match["id"]): match for match in snapshot["matches"]}
    evidence = {str(row["id"]): row for row in snapshot["fixture_evidence"]}
    assert len(board) == len(snapshot["matches"]) == len(evidence)
    failures = []
    sources = {}
    source_meta = {}

    for item in manifest:
        path = ROOT / item["file"]
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        receipt = item["source"]
        if digest != receipt["sha256"] or len(raw) != receipt["bytes"]:
            failures.append(f"{path}: manifest hash/byte count differs")
        rows = json.loads(raw) if path.suffix == ".json" else hydrated_rows(raw)
        ids = [str(row["id"]) for row in rows]
        if len(ids) != len(set(ids)):
            failures.append(f"{path}: duplicate raw fixture IDs")
        by_id = {str(row["id"]): row for row in rows}
        sources[receipt["url"]] = by_id
        source_meta[receipt["url"]] = receipt
        missing = sorted(set(by_id) - set(board))
        is_supplement = receipt["name"].startswith("Hotspawn reviewed inventory supplement ")
        if missing and not is_supplement:
            failures.append(f"{path}: primary rows missing from board: {missing}")
        source_meta[receipt["url"]]["raw_rows_not_retained"] = missing

    rows = []
    comparisons = 0
    fields = 0
    for ident, match in sorted(board.items(), key=lambda item: (item[1]["start"], item[0])):
        row_problems = []
        provenance = match.get("fixture_sources") or []
        source_urls = []
        row_fields = 0
        for source in provenance:
            url = source.get("url")
            source_urls.append(url)
            if url not in sources:
                row_problems.append("provenance URL is absent from raw manifest")
                continue
            if source.get("sha256") != source_meta[url]["sha256"]:
                row_problems.append("provenance hash differs from raw manifest")
            raw = sources[url].get(ident)
            if raw is None:
                row_problems.append("fixture ID absent from cited raw response")
                continue
            cleaned = retained_fields(raw)
            comparisons += 1
            fields += len(cleaned)
            row_fields += len(cleaned)
            if cleaned != evidence[ident]:
                row_problems.append("retained non-crowd fields differ from cited raw response")
        if match.get("feed_url") not in source_urls:
            row_problems.append("displayed feed URL is not in raw provenance")
        if urlsplit(match.get("source_url") or "").hostname not in {
                "play.hotspawn.com", "www.hotspawn.com", "hotspawn.com"}:
            row_problems.append("missing official Hotspawn row link")
        if match.get("inventory_receipt"):
            receipt = match["inventory_receipt"]
            if str(receipt.get("fixture_id")) != ident or receipt.get("api_url") != match.get("feed_url"):
                row_problems.append("reviewed receipt does not match row/feed")
        if match["state"] == "not_open" and any(match.get(key) is not None for key in
                ("pick", "probabilities", "fair_odds", "method")):
            row_problems.append("not-open row carries an actionable value")
        if match["state"] == "open" and (not match.get("pick") or match.get("probabilities") is None):
            row_problems.append("open row lacks a pick/probability pair")
        rows.append({"id": ident, "teams": match["teams"], "state": match["state"],
                     "raw_sources": len(provenance), "non_crowd_fields_compared": row_fields,
                     "official_source": match.get("source_url"), "problems": row_problems})
        failures.extend(f"{ident}: {problem}" for problem in row_problems)

    report = {
        "schema_version": 1,
        "snapshot_generated_at": snapshot["generated_at"],
        "fixtures_observed_at": snapshot["fixtures_observed_at"],
        "snapshot_sha256": hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "scope": "Exact raw-byte hashes and every retained non-crowd fixture field; crowd values are never probability inputs.",
        "source_counts": {item["source"]["name"]: len(sources[item["source"]["url"]]) for item in manifest},
        "supplement_history_not_retained": {
            item["source"]["name"]: source_meta[item["source"]["url"]]["raw_rows_not_retained"]
            for item in manifest if item["source"]["name"].startswith("Hotspawn reviewed inventory supplement ")},
        "counts": {"board_rows": len(board), "open": sum(m["state"] == "open" for m in board.values()),
                   "not_open": sum(m["state"] == "not_open" for m in board.values()),
                   "raw_row_comparisons": comparisons, "non_crowd_field_comparisons": fields,
                   "failures": len(failures)},
        "failures": failures,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({key: report[key] for key in
                      ("source_counts", "supplement_history_not_retained", "counts")}, indent=1))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
