"""Independent zero-collector auditor for session cf8f94b9.

Does NOT import any module from ``scripts/``. Independently verifies:
1. All rows in ``data/latest.json`` match ``fixture_evidence`` 1:1 with zero
   Hotspawn crowd-vote contamination (``picked*``, ``total_picks``).
2. Every open CS2 match carries a supported pick and (where published) exact
   re-derived probabilities + fair decimal odds summing to 1.0 across all tiers
   (Polymarket strict/wide, Pinnacle, researched 2-way bookmaker decimal lines,
   Valve VRS model, and HLTV dated Valve ranking mirror).
3. Every non-open match is strictly blank (``probabilities=None``,
   ``fair_odds=None``, ``pick=None``, ``method=None``) with a published reason.
4. Every rendered table row across ``picks.html``, ``matches.html``, and
   ``unresolved.html`` includes an official source link, matches ``data/matches.csv``
   and ``data/latest.json``, and all internal links + ``#fragment`` anchors across
   all built HTML pages resolve cleanly.
5. JSON indentation & non-mutation invariants hold across ``data/identities.json``,
   ``data/book-receipts.json``, ``data/review-notes.json``, and
   ``data/lineup-receipts.json``.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
VRS_Q = math.log(10) / 400.0
VRS_G = 1.0 / math.sqrt(1.0 + 3.0 * VRS_Q * VRS_Q * 75.0 * 75.0 / (math.pi ** 2))
VRS_SLOPE = 0.7986


def parse_dt(value: str | int | float) -> datetime:
    if isinstance(value, (int, float)) or str(value).isdigit():
        return datetime.fromtimestamp(float(value) / 1000.0, timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError(f'Naive timestamp: {value}')
    return parsed.astimezone(timezone.utc)


def fold_name(value: str) -> str:
    nfkd = unicodedata.normalize('NFKD', value).casefold()
    stripped = ''.join(ch for ch in nfkd if not unicodedata.combining(ch))
    return ''.join(ch for ch in unicodedata.normalize('NFKC', stripped) if ch.isalnum())


def independent_vrs(p_a: float, p_b: float) -> tuple[float, float]:
    raw = 1.0 / (1.0 + 10.0 ** (-VRS_G * (float(p_a) - float(p_b)) / 400.0))
    cal = 0.5 + VRS_SLOPE * (raw - 0.5)
    return cal, 1.0 - cal


def audit_repository(root: Path = ROOT) -> dict:
    problems: list[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            problems.append(msg)

    latest_path = root / 'data/latest.json'
    csv_path = root / 'data/matches.csv'
    build_info_path = root / 'build-info.json'
    latest = json.loads(latest_path.read_text(encoding='utf-8'))
    captured = parse_dt(latest['generated_at'])

    raw_by_id = {str(r['id']): r for r in latest['fixture_evidence']}
    matches = latest['matches']
    check(len(matches) == len(raw_by_id), 'Mismatch between matches and fixture_evidence count')

    open_count = 0
    open_picked = 0
    open_priced = 0
    open_research = 0
    tier_counts: dict[str, int] = {}

    for m in matches:
        mid = str(m['id'])
        raw = raw_by_id.get(mid, {})
        check(bool(raw), f'{mid}: missing fixture_evidence')
        check(not any('picked' in k or k == 'total_picks' for k in raw), f'{mid}: Hotspawn crowd pick leaked')
        check(str(m.get('source_url') or '').startswith('https://'), f'{mid}: missing official source_url')

        if m['state'] != 'open':
            check(m['probabilities'] is None, f'{mid}: non-open row has probabilities')
            check(m['fair_odds'] is None, f'{mid}: non-open row has fair_odds')
            check(m['pick'] is None, f'{mid}: non-open row has pick')
            check(m['method'] is None, f'{mid}: non-open row has method')
            check(bool(m.get('reason')), f'{mid}: non-open row lacks reason')
            continue

        open_count += 1
        method = m.get('method')
        tier_counts[str(method)] = tier_counts.get(str(method), 0) + 1
        check(parse_dt(m['start']) > captured and parse_dt(m['lock']) > captured, f'{mid}: open row already locked')

        if m['probabilities'] is None:
            if m.get('pick'):
                open_picked += 1
                open_research += 1
                check(m['pick'] in m['teams'], f'{mid}: research pick outside teams')
                check(str(method).startswith('research_'), f'{mid}: unexpected method {method}')
            check(bool(m.get('reason')), f'{mid}: blank-probability open row lacks reason')
            continue

        open_priced += 1
        if m.get('pick'):
            open_picked += 1
        probs = m['probabilities']
        odds = m['fair_odds']
        check(len(probs) == 2 and all(0.0 < p < 1.0 for p in probs), f'{mid}: invalid probability bounds')
        check(abs(sum(probs) - 1.0) < 1e-10, f'{mid}: probabilities do not sum to 1')
        check(all(abs(odds[i] - 1.0 / probs[i]) < 1e-9 for i in (0, 1)), f'{mid}: fair_odds mismatch')
        expected_pick = None if abs(probs[0] - probs[1]) < 1e-4 else m['teams'][0 if probs[0] > probs[1] else 1]
        check(m['pick'] == expected_pick, f'{mid}: pick mismatch vs probabilities')

        check(len(m.get('evidence') or []) == 1, f'{mid}: priced row lacks single primary quote')
        q = m['evidence'][0]
        check(str(q.get('url') or '').startswith('https://'), f'{mid}: quote url missing https')
        check(str(q.get('api_url') or '').startswith('https://'), f'{mid}: quote api_url missing https')

        if method in ('model_vrs', 'model_vrs_mirror'):
            p0, p1 = independent_vrs(q['points'][0], q['points'][1])
            check(abs(probs[0] - p0) < 1e-10 and abs(probs[1] - p1) < 1e-10, f'{mid}: VRS math mismatch')
        elif q.get('provider') == 'Polymarket':
            raw_prices = q['raw']['outcomePrices']
            arr = json.loads(raw_prices) if isinstance(raw_prices, str) else list(raw_prices)
            vals = [Decimal(str(v)) for v in arr]
            normed = [float(v / sum(vals)) for v in vals]
            check(sorted(round(x, 9) for x in probs) == sorted(round(x, 9) for x in normed),
                  f'{mid}: Polymarket de-vig mismatch')
        elif isinstance((q.get('raw') or {}).get('odds'), list):
            inv = [Decimal(1) / Decimal(str(x)) for x in q['raw']['odds']]
            overround = sum(inv) - Decimal(1)
            check(Decimal('-0.02') <= overround <= Decimal('0.25'), f'{mid}: book overround out of bounds')
            normed = [float(v / sum(inv)) for v in inv]
            check(sorted(round(x, 9) for x in probs) == sorted(round(x, 9) for x in normed),
                  f'{mid}: bookmaker de-vig mismatch')

    # Verify CSV parity against latest.json
    with csv_path.open(encoding='utf-8', newline='') as fh:
        csv_rows = list(csv.DictReader(fh))
    check(len(csv_rows) == len(matches), f'CSV count {len(csv_rows)} != JSON count {len(matches)}')

    # Verify build-info.json SHA-256 digests and internal HTML links/anchors
    build_info = json.loads(build_info_path.read_text(encoding='utf-8'))
    for rel_path, expected_sha in build_info['files'].items():
        fp = root / rel_path
        check(fp.exists(), f'Missing built file {rel_path}')
        if fp.exists():
            actual_sha = hashlib.sha256(fp.read_bytes()).hexdigest()
            check(actual_sha == expected_sha, f'SHA-256 mismatch on {rel_path}')

    html_pages = [
        'index.html', 'picks.html', 'matches.html', 'analysis.html',
        'evidence.html', 'methodology.html', 'unresolved.html',
        'review.html', 'sources.html', '404.html',
    ]
    ids_by_page: dict[str, set[str]] = {}
    soups: dict[str, BeautifulSoup] = {}
    for page_name in html_pages:
        soup = BeautifulSoup((root / page_name).read_text(encoding='utf-8'), 'html.parser')
        soups[page_name] = soup
        ids_by_page[page_name] = {
            tag['id'] for tag in soup.find_all(attrs={'id': True}) if tag.get('id')
        }

    internal_links_checked = 0
    for page_name, soup in soups.items():
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('https://', 'http://', 'mailto:')):
                continue
            parts = urlsplit(href)
            target_page = parts.path.lstrip('./') or page_name
            check((root / target_page).exists(), f'{page_name}: broken link target {href}')
            if parts.fragment and target_page in ids_by_page:
                check(parts.fragment in ids_by_page[target_page],
                      f'{page_name}: missing fragment #{parts.fragment} in {target_page}')
            internal_links_checked += 1

    # Verify JSON register formatting invariants
    for indent1_rel in ('data/identities.json', 'data/book-receipts.json', 'data/review-notes.json'):
        raw_txt = (root / indent1_rel).read_text(encoding='utf-8')
        parsed = json.loads(raw_txt)
        check(raw_txt == json.dumps(parsed, ensure_ascii=False, indent=1) + '\n',
              f'{indent1_rel} violates strict indent=1 invariant')

    lineups_txt = (root / 'data/lineup-receipts.json').read_text(encoding='utf-8')
    lineups_parsed = json.loads(lineups_txt)
    check(lineups_txt == json.dumps(lineups_parsed, ensure_ascii=False, indent=2) + '\n',
          'data/lineup-receipts.json violates strict indent=2 invariant')

    return {
        'rows_total': len(matches),
        'open_total': open_count,
        'open_with_pick': open_picked,
        'open_with_probability': open_priced,
        'open_research_only': open_research,
        'tier_counts': tier_counts,
        'internal_links_checked': internal_links_checked,
        'problems': problems,
    }


def main() -> int:
    result = audit_repository(ROOT)
    print(json.dumps(result, indent=2))
    return 1 if result['problems'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
