#!/usr/bin/env python3
"""Independent read-only line-by-line board, receipt, CSV, and HTML auditor (session 071642e7).

Deliberately imports nothing from ``scripts/``. Re-implements every source,
identity, mathematical de-vigging, Valve Regional Standings (VRS) Glicko-2
expectation + published 0.7986 calibration slope, blank-value preservation,
crowd-leakage prohibition, and per-table-row primary-source link check from
first principles.

Usage:
    python verification-071642e7/audit_071642e7.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

VRS_REPO = 'ValveSoftware/counter-strike_regional_standings'
VRS_RD = 75.0
VRS_SLOPE = 0.7986
VRS_Q = math.log(10.0) / 400.0
VRS_G = 1.0 / math.sqrt(1.0 + 3.0 * VRS_Q * VRS_Q * VRS_RD * VRS_RD / (math.pi ** 2))
VRS_ROW_RE = re.compile(
    r'^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]\(([^)]+)\)'
)

TRUSTED_SOURCE_PREFIXES = (
    'https://gamma-api.polymarket.com/',
    'https://polymarket.com/',
    'https://docs.polymarket.com/',
    'https://guest.api.arcadia.pinnacle.com/',
    'https://www.pinnacle.com/',
    'https://www.pinnaclesports.com/',
    'https://www.hltv.org/',
    'https://github.com/ValveSoftware/counter-strike_regional_standings',
    'https://github.com/ValveSoftware/counter-strike_regional_standings/',
    'https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/',
    'https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/',
    'https://github.com/buffedlizard55-lab/MaltaProj4/',
    'https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/',
    'https://docs.github.com/',
    'https://stavka.tv/',
    'https://winline.ru/',
    'https://egamersworld.com/',
    'https://kushvsporte.ru/',
    'https://thunderpick.io/',
    'https://gg.bet/',
    'https://bo3.gg/',
    'https://api.bo3.gg/',
    'https://www.bo3.gg/',
    'https://www.rivalry.com/',
    'https://stake.com/',
    'https://picklebet.com/',
    'https://kalshi.com/',
    'https://api.elections.kalshi.com/',
    'https://liquipedia.net/counterstrike/',
    'https://draft5.gg/',
    'https://dfrag.gg/',
    'https://www.strafe.com/',
    'https://esportbet.com/',
    'https://white.market/',
    'https://game-tournaments.com/',
    'https://www.teamliquid.com/',
    'https://betboom.team/',
    'https://auroragg.com/',
    'https://nip.gl/',
    'https://www.hotspawn.com/',
    'https://play.hotspawn.com/',
    'https://phpstack-1372681-6459848.cloudwaysapps.com/',
    'https://buffedlizard55-lab.github.io/MaltaProj4/',
)

PLACEHOLDER_TOKENS = ('{{', '}}', 'TBD_PLACEHOLDER', 'NaN%', '>undefined<', '>NaN<', '[object Object]')


def fold_name(value: str) -> str:
    nfkd = unicodedata.normalize('NFKD', str(value or '')).casefold()
    base = ''.join(ch for ch in nfkd if not unicodedata.combining(ch))
    return ''.join(ch for ch in unicodedata.normalize('NFKC', base) if ch.isalnum())


def parse_dt(value: object) -> datetime:
    text = str(value)
    if text.isdigit():
        return datetime.fromtimestamp(int(text) / 1000.0, tz=timezone.utc)
    dt = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError(f'Missing timezone on {value!r}')
    return dt


def parse_json_array(value: object) -> list:
    return json.loads(value) if isinstance(value, str) else list(value)


def valve_probabilities(pts_a: float, pts_b: float) -> tuple[float, list[float]]:
    raw = 1.0 / (1.0 + 10.0 ** (-VRS_G * (float(pts_a) - float(pts_b)) / 400.0))
    cal = 0.5 + VRS_SLOPE * (raw - 0.5)
    return raw, [cal, 1.0 - cal]


def is_official_vrs(url: str, hosts: tuple[str, ...] = ('github.com',)) -> bool:
    parts = urlsplit(url or '')
    return (
        parts.scheme == 'https'
        and parts.hostname in hosts
        and parts.path.startswith('/' + VRS_REPO + '/')
    )


def is_trusted_url(url: str) -> bool:
    return (
        url == 'https://github.com/ValveSoftware/counter-strike_regional_standings'
        or str(url or '').startswith(TRUSTED_SOURCE_PREFIXES)
    )


def parse_vendored_vrs(path: Path) -> dict[tuple[int, str], dict]:
    rows: dict[tuple[int, str], dict] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        m = VRS_ROW_RE.match(line)
        if not m:
            continue
        standing, points, label, roster, details = m.groups()
        rows[(int(standing), label.strip())] = {
            'standing': int(standing),
            'points': int(points),
            'name': label.strip(),
            'roster': [p.strip() for p in roster.split(',') if p.strip()],
            'details': details.strip(),
        }
    return rows


def build_alias_lookup(identities_doc: dict) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    alias_map: dict[str, str] = {}
    for entry in identities_doc.get('aliases', []):
        canonical = entry.get('canonical', '')
        src = entry.get('source', '')
        if not str(src).startswith('https://'):
            errors.append(f'identities.json {canonical}: missing https primary source ({src!r})')
        for n in entry.get('names', []):
            alias_map[fold_name(n)] = fold_name(canonical)
    return alias_map, errors


def audit_repository(root: Path = ROOT) -> dict:
    errors: list[str] = []
    latest_path = root / 'data/latest.json'
    latest_bytes = latest_path.read_bytes()
    latest_sha = hashlib.sha256(latest_bytes).hexdigest()
    snap = json.loads(latest_bytes)

    identities_raw = (root / 'data/identities.json').read_text(encoding='utf-8')
    identities_doc = json.loads(identities_raw)
    if identities_raw != json.dumps(identities_doc, indent=1, ensure_ascii=False) + '\n':
        errors.append('data/identities.json does not preserve canonical indent=1 formatting')
    alias_map, alias_errors = build_alias_lookup(identities_doc)
    errors.extend(alias_errors)

    def norm_team(label: str) -> str:
        key = fold_name(label)
        return alias_map.get(key, key)

    books_raw = (root / 'data/book-receipts.json').read_text(encoding='utf-8')
    books_doc = json.loads(books_raw)
    if books_raw != json.dumps(books_doc, indent=1, ensure_ascii=False) + '\n':
        errors.append('data/book-receipts.json does not preserve canonical indent=1 formatting')

    notes_raw = (root / 'data/review-notes.json').read_text(encoding='utf-8')
    notes_doc = json.loads(notes_raw)
    if notes_raw != json.dumps(notes_doc, indent=1, ensure_ascii=False) + '\n':
        errors.append('data/review-notes.json does not preserve canonical indent=1 formatting')

    vendored_meta = json.loads((root / 'data/vrs/meta.json').read_text(encoding='utf-8'))
    vendored_table = parse_vendored_vrs(root / 'data/vrs' / vendored_meta['file'])

    captured_at = parse_dt(snap['generated_at'])
    raw_by_id = {str(r['id']): r for r in snap['fixture_evidence']}
    matches = snap['matches']

    if len(raw_by_id) != len(snap['fixture_evidence']) or len({m['id'] for m in matches}) != len(matches):
        errors.append('Duplicate fixture IDs detected in matches or fixture_evidence')
    if {str(m['id']) for m in matches} != set(raw_by_id):
        errors.append('Set of match IDs differs from fixture_evidence IDs')

    with (root / 'data/matches.csv').open(encoding='utf-8') as fh:
        csv_rows = list(csv.DictReader(fh))
    if len(csv_rows) != len(matches):
        errors.append(f'CSV row count {len(csv_rows)} != JSON match count {len(matches)}')
    csv_by_id = {r['hotspawn_id']: r for r in csv_rows}

    counts = {
        'total_rows': len(matches),
        'open_rows': 0,
        'not_open_rows': 0,
        'open_with_pick': 0,
        'open_with_probability': 0,
        'open_research_only': 0,
        'open_unresolved': 0,
        'methods': {},
    }
    ledger: list[dict] = []

    for idx, m in enumerate(matches, start=1):
        mid = str(m['id'])
        row_errors: list[str] = []
        raw_fix = raw_by_id.get(mid, {})

        # 1. Primary Hotspawn fixture parity & zero crowd field leakage
        if m.get('teams') != [raw_fix.get('participants0_name'), raw_fix.get('participants1_name')]:
            row_errors.append('teams mismatch against raw fixture_evidence')
        if m.get('team_ids') != [raw_fix.get('participants0_id'), raw_fix.get('participants1_id')]:
            row_errors.append('team_ids mismatch against raw fixture_evidence')
        for field, raw_key in (
            ('competition', 'competition_name'),
            ('tier', 'tier'),
            ('best_of', 'best_of'),
            ('source_status', 'status'),
        ):
            if m.get(field) != raw_fix.get(raw_key):
                row_errors.append(f'{field} differs from raw fixture_evidence')
        for field, raw_key in (('start', 'scheduled_start_time'), ('lock', 'lock_time')):
            raw_val = raw_fix.get(raw_key)
            if (m.get(field) is None) != (not raw_val):
                row_errors.append(f'{field} nullability differs from raw timestamp')
            elif raw_val and parse_dt(m[field]) != parse_dt(raw_val):
                row_errors.append(f'{field} timestamp mismatch against raw timestamp')

        if any('picked' in k or k == 'total_picks' for k in raw_fix):
            row_errors.append('Hotspawn crowd pick field leaked into fixture_evidence')
        src_host = urlsplit(m.get('source_url') or '').hostname
        if src_host not in ('play.hotspawn.com', 'www.hotspawn.com', 'hotspawn.com'):
            row_errors.append(f'Invalid official fixture source_url {m.get("source_url")!r}')

        state = m.get('state')
        method = m.get('method')
        probs = m.get('probabilities')
        fair = m.get('fair_odds')
        pick = m.get('pick')
        ev = (m.get('evidence') or [None])[0]

        if state == 'open':
            counts['open_rows'] += 1
            counts['methods'][str(method)] = counts['methods'].get(str(method), 0) + 1
            if pick is not None:
                if pick not in m['teams']:
                    row_errors.append(f'pick {pick!r} is not one of {m["teams"]!r}')
                else:
                    counts['open_with_pick'] += 1
            else:
                counts['open_unresolved'] += 1
                if probs is not None or fair is not None or method is not None:
                    row_errors.append('unresolved open row carries derived method/probability/fair_odds')
                if not m.get('reason'):
                    row_errors.append('unresolved open row lacks explicit limitation reason')

            if probs is not None:
                counts['open_with_probability'] += 1
                if not ev:
                    row_errors.append('priced row lacks primary evidence object')
                else:
                    prov_str = str(ev.get('provider') or '')
                    url_str = str(ev.get('url') or '')
                    api_str = str(ev.get('api_url') or '')
                    if 'hotspawn' in prov_str.lower() or 'hotspawn' in url_str.lower() or 'hotspawn' in api_str.lower():
                        row_errors.append('Hotspawn crowd data used as probability source')
                    if not (is_trusted_url(url_str) and is_trusted_url(api_str)):
                        row_errors.append(f'Untrusted probability URL ({url_str!r}, {api_str!r})')

                    obs_delta = (captured_at - parse_dt(ev['observed_at'])).total_seconds()
                    if not (-300 <= obs_delta <= 28800):
                        row_errors.append(f'Evidence observation outside [-300s, +28800s]: {obs_delta:.1f}s')

                    if method in ('exchange', 'exchange_wide'):
                        raw_mkt = ev['raw']
                        outcomes = parse_json_array(raw_mkt['outcomes'])
                        prices = [Decimal(str(x)) for x in parse_json_array(raw_mkt['outcomePrices'])]
                        bid = Decimal(str(raw_mkt['bestBid']))
                        ask = Decimal(str(raw_mkt['bestAsk']))
                        spread = ask - bid
                        liq = Decimal(str(raw_mkt['liquidity']))
                        upd_delta = (captured_at - parse_dt(raw_mkt['updatedAt'])).total_seconds()
                        if not (raw_mkt.get('active') and not raw_mkt.get('closed') and raw_mkt.get('acceptingOrders')):
                            row_errors.append('Inactive or closed Polymarket market used')
                        if not (-300 <= upd_delta <= 28800):
                            row_errors.append(f'Stale Polymarket updatedAt delta: {upd_delta:.1f}s')
                        if liq < Decimal('100'):
                            row_errors.append(f'Polymarket liquidity {liq} < 100')
                        if method == 'exchange' and spread > Decimal('0.25'):
                            row_errors.append(f'Strict exchange row exceeds 0.25 spread ({spread})')
                        if method == 'exchange_wide':
                            if not (Decimal('0.25') < spread <= Decimal('0.60')):
                                row_errors.append(f'Wide exchange spread {spread} outside (0.25, 0.60]')
                            if not ev.get('strict_rejection') or not any('Low confidence' in f for f in m.get('flags', [])):
                                row_errors.append('Wide exchange row missing strict_rejection or Low confidence flag')
                        meta = ev.get('team_metadata') or (ev.get('event') or {}).get('teams') or []
                        slot_aliases = []
                        for out_name in outcomes:
                            s = {norm_team(out_name)}
                            for tm in meta:
                                if tm.get('name') == out_name and tm.get('abbreviation'):
                                    s.add(norm_team(tm['abbreviation']))
                            slot_aliases.append(s)
                        order = [next(i for i, sa in enumerate(slot_aliases) if norm_team(t) in sa) for t in m['teams']]
                        expected = [float(prices[i] / sum(prices)) for i in order]
                    elif method == 'bookmaker_fallback':
                        raw_bk = ev['raw']
                        if 'line' in raw_bk:
                            matchup, line = raw_bk['matchup'], raw_bk['line']
                            parts = {p['alignment']: p['name'] for p in matchup['participants']}
                            p_map = {p['designation']: Decimal(str(p['price'])) for p in line['prices']}
                            dec_odds = [
                                1 + (v / 100 if v > 0 else 100 / (-v))
                                for v in (p_map['home'], p_map['away'])
                            ]
                            weights = [Decimal(1) / d for d in dec_odds]
                            overround = sum(weights) - Decimal(1)
                            if not (Decimal('-0.02') <= overround <= Decimal('0.25')):
                                row_errors.append(f'Pinnacle overround {overround} out of bounds')
                            order = [0 if norm_team(parts['home']) == norm_team(t) else 1 for t in m['teams']]
                            expected = [float(weights[i] / sum(weights)) for i in order]
                        else:
                            raw_odds = [Decimal(str(x)) for x in raw_bk['odds']]
                            if len(raw_odds) != 2 or raw_odds[0] == raw_odds[1] or any(x <= 1 for x in raw_odds):
                                row_errors.append(f'Invalid or symmetric placeholder book odds {raw_odds}')
                            weights = [Decimal(1) / x for x in raw_odds]
                            overround = sum(weights) - Decimal(1)
                            if not (Decimal('-0.02') <= overround <= Decimal('0.25')):
                                row_errors.append(f'Book receipt overround {overround} out of bounds')
                            t_aliases = raw_bk.get('team_aliases') or [[t] for t in raw_bk['source_teams']]
                            slot_aliases = [
                                {norm_team(a) for a in ([st] + list(ta)) if a}
                                for st, ta in zip(raw_bk['source_teams'], t_aliases)
                            ]
                            order = [next(i for i, sa in enumerate(slot_aliases) if norm_team(t) in sa) for t in m['teams']]
                            expected = [float(weights[i] / sum(weights)) for i in order]
                    elif method in ('model_vrs', 'model_vrs_mirror'):
                        raw_exp, expected = valve_probabilities(ev['points'][0], ev['points'][1])
                        if abs(ev['raw_expected'][0] - raw_exp) > 1e-10:
                            row_errors.append('Valve raw_expected mismatch')
                        if not any('not a market price' in f for f in m.get('flags', [])):
                            row_errors.append('Model row missing non-market price flag')
                        if method == 'model_vrs' and ev.get('standings_commit') == vendored_meta['commit']:
                            for standing, vname, pts, roster in zip(
                                ev['standings'], ev['vrs_teams'], ev['points'], ev['rosters']
                            ):
                                vrow = vendored_table.get((standing, vname))
                                if not vrow or vrow['points'] != pts or vrow['roster'] != roster:
                                    row_errors.append(f'Vendored Valve row mismatch for #{standing} {vname}')
                    else:
                        expected = []
                        row_errors.append(f'Unknown pricing method {method!r}')

                    if expected:
                        if any(abs(a - b) > 1e-9 for a, b in zip(probs, expected)):
                            row_errors.append(f'Probability mismatch {probs} vs expected {expected}')
                        if not fair or any(abs(f - 1.0 / p) > 1e-9 for f, p in zip(fair, expected)):
                            row_errors.append(f'Fair odds mismatch {fair} vs 1/expected')
                        exp_pick = m['teams'][0 if expected[0] > expected[1] else 1]
                        if pick != exp_pick:
                            row_errors.append(f'Pick {pick!r} != higher probability side {exp_pick!r}')
            else:
                if pick is not None:
                    counts['open_research_only'] += 1
                    if not str(method or '').startswith('research_'):
                        row_errors.append(f'Unpriced open pick has non-research method {method!r}')
                    if fair is not None or m.get('evidence'):
                        row_errors.append('Research-only row carries fair_odds or quote evidence')
                    if 'not a market probability' not in str(m.get('reason') or ''):
                        row_errors.append('Research-only row missing explicit non-market reason')
        else:
            counts['not_open_rows'] += 1
            if probs is not None or fair is not None or pick is not None or method is not None:
                row_errors.append('Closed/locked row carries active pick or probability')

        # 2. CSV 1-to-1 verification
        csv_row = csv_by_id.get(mid)
        if not csv_row:
            row_errors.append('Missing row in data/matches.csv')
        else:
            if csv_row['pick'] != (pick or ''):
                row_errors.append(f'CSV pick {csv_row["pick"]!r} != JSON {pick!r}')
            if csv_row['source'] != m['source_url']:
                row_errors.append('CSV source URL mismatch')

        errors.extend(f'{mid} ({" vs ".join(t or "?" for t in m["teams"])}): {err}' for err in row_errors)
        primary_url = (
            (ev or {}).get('url')
            or (m.get('hltv_context') or {}).get('source')
            or (m.get('vrs_research') or {}).get('source')
            or m.get('source_url')
        )
        ledger.append({
            'index': idx,
            'id': mid,
            'teams': m['teams'],
            'competition': m.get('competition'),
            'start': m.get('start'),
            'lock': m.get('lock'),
            'state': state,
            'method': method,
            'pick': pick,
            'probabilities': probs,
            'fair_odds': fair,
            'primary_source': primary_url,
            'status': 'PASS' if not row_errors else 'FAIL: ' + '; '.join(row_errors),
        })

    # 3. Verify all built HTML pages, manifest SHA-256s, placeholders, and per-row source links
    manifest = json.loads((root / 'build-info.json').read_text(encoding='utf-8'))
    html_pages_checked = 0
    table_rows_checked = 0
    for rel_path, expected_sha in manifest['files'].items():
        target = (root / rel_path).resolve()
        if not target.is_file():
            errors.append(f'Missing file in build-info.json: {rel_path}')
            continue
        actual_sha = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            errors.append(f'SHA-256 mismatch in build-info.json for {rel_path}')
        if not rel_path.endswith('.html'):
            continue
        html_pages_checked += 1
        text = target.read_text(encoding='utf-8')
        for token in PLACEHOLDER_TOKENS:
            if token in text:
                errors.append(f'{rel_path}: unreplaced placeholder token {token!r}')
        soup = BeautifulSoup(text, 'html.parser')
        for tr in soup.select('tbody tr'):
            table_rows_checked += 1
            ext_links = [
                a['href'] for a in tr.find_all('a', href=True)
                if a['href'].startswith('https://') and is_trusted_url(a['href'])
            ]
            if not ext_links:
                errors.append(f'{rel_path}: table row lacks a trusted https:// primary source link')
        for tag in soup.select('[href], [src]'):
            href = tag.get('href') or tag.get('src') or ''
            parts = urlsplit(href)
            if parts.scheme:
                if parts.scheme != 'https':
                    errors.append(f'{rel_path}: non-https external URL {href!r}')
            elif href and not href.startswith('#'):
                dest = (target.parent / unquote(parts.path)).resolve() if parts.path else target
                if not dest.exists():
                    errors.append(f'{rel_path}: broken relative target {href!r}')

    return {
        'session': '071642e7',
        'audited_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'snapshot_generated_at': snap['generated_at'],
        'fixtures_observed_at': snap['fixtures_observed_at'],
        'snapshot_sha256': latest_sha,
        'counts': counts,
        'html_pages_checked': html_pages_checked,
        'table_rows_checked': table_rows_checked,
        'error_count': len(errors),
        'errors': errors,
        'ledger': ledger,
    }


def render_markdown(report: dict) -> str:
    c = report['counts']
    lines = [
        '# Session `071642e7` — Independent Line-by-Line Source & Mathematical Audit',
        '',
        f"- **Audited at**: `{report['audited_at']}`",
        f"- **Snapshot `generated_at`**: `{report['snapshot_generated_at']}`",
        f"- **Hotspawn `fixtures_observed_at`**: `{report['fixtures_observed_at']}`",
        f"- **Snapshot SHA-256**: `{report['snapshot_sha256']}`",
        f"- **Total retained fixtures**: **{c['total_rows']}** (**{c['open_rows']} `open`**, **{c['not_open_rows']} `not_open`**)",
        f"- **Open fixtures with verified pick**: **{c['open_with_pick']} / {c['open_rows']}** (`unresolved: {c['open_unresolved']}`)",
        f"- **Open fixtures with calibrated probabilities**: **{c['open_with_probability']} / {c['open_rows']}** (`research-only: {c['open_research_only']}`)",
        f"- **HTML pages checksummed & audited**: **{report['html_pages_checked']}** (**{report['table_rows_checked']}** rendered `<tbody><tr>` rows verified for trusted `https://` primary-source links)",
        f"- **Audit failures**: **{report['error_count']}**",
        '',
        '## Open Match Line-by-Line Verification Table',
        '',
        '| # | Fixture | Match | Competition | Start (UTC) | Method | Pick | Win % | Fair Odds | Primary Source | Result |',
        '| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    open_idx = 0
    for row in report['ledger']:
        if row['state'] != 'open':
            continue
        open_idx += 1
        probs = (
            f"{row['probabilities'][0]*100:.1f}% / {row['probabilities'][1]*100:.1f}%"
            if row['probabilities'] else '— (blank)'
        )
        odds = (
            f"{row['fair_odds'][0]:.3f} / {row['fair_odds'][1]:.3f}"
            if row['fair_odds'] else '— (blank)'
        )
        lines.append(
            f"| {open_idx} | [{row['id']}](https://play.hotspawn.com/lobby) | "
            f"{row['teams'][0]} vs {row['teams'][1]} | {row['competition']} | "
            f"`{row['start']}` | `{row['method'] or '—'}` | **{row['pick'] or '—'}** | "
            f"`{probs}` | `{odds}` | [Source]({row['primary_source']}) | {row['status']} |"
        )
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--json-out', type=Path, default=None)
    parser.add_argument('--md-out', type=Path, default=None)
    args = parser.parse_args()

    report = audit_repository(args.root.resolve())
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(render_markdown(report), encoding='utf-8')

    summary = {k: v for k, v in report.items() if k != 'ledger'}
    print(json.dumps(summary, indent=2))
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
