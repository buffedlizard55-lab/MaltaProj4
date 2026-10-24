"""Independent zero-shared-code verifier for the Hotspawn CS2 pick board (session fbea4413).

Verifies every row in ``data/latest.json`` and the rendered static pages line by line:
1. Official Hotspawn fixture provenance and SHA-256 source receipts on every row.
2. Zero Hotspawn crowd-vote or popularity leakage into ``evidence`` or probabilities.
3. Independent arithmetic replay for every open row from its stored raw inputs:
   - Polymarket exchange (`exchange`, `exchange_wide`): `p_i = x_i / (x_1 + x_2)`
   - Researched bookmaker listing (`bookmaker_fallback`, `bookmaker`): `q_i = 1 / d_i`, `p_i = q_i / (q_1 + q_2)`
   - Pinnacle moneyline (`pinnacle`): American-to-decimal conversion then de-vig
   - Originated Valve VRS model (`model_vrs`) and HLTV dated VRS mirror (`model_vrs_mirror`):
     Glicko expectation `1 / (1 + 10 ** ((pts_b - pts_a) / 400))` with Valve calibration
     `p = max(0.01, min(0.99, 0.7986 * raw + 0.1007))`
4. Every open priced row names a strict directional pick (`p_0 != p_1`, never a 50/50 placeholder
   or pick-less probability pair), and every non-featured open row records an HLTV attempt and an
   esportsbook/exchange attempt before any lower tier.
5. Executive summary and mobile discoverability: `#exec-summary`, `#exec-quicknav`, `#freshness-strip`,
   `#picks-at-a-glance`, `#unresolved-summary`, `#unresolved-limits`, `unresolved.html`, and `review.html`
   link integrity and CSS brace balance / byte parity.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

MARKET_METHODS = frozenset({'exchange', 'exchange_wide', 'bookmaker', 'bookmaker_fallback', 'pinnacle'})
MODEL_METHODS = frozenset({'model_vrs', 'model_vrs_mirror'})
RESEARCH_METHODS = frozenset({'research_rank', 'research_rank_single', 'research_vrs_single', 'research_form'})
ALL_METHODS = MARKET_METHODS | MODEL_METHODS | RESEARCH_METHODS


def parse_utc(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    elif re.search(r'[+-]\d{2}$', text):
        text = text + ':00'
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def norm_team(name: str) -> str:
    text = unicodedata.normalize('NFKD', str(name or '')).encode('ascii', 'ignore').decode('ascii').lower()
    text = re.sub(r'[^a-z0-9]+', ' ', text).strip()
    for suffix in (' esports', ' esport', ' gaming', ' team', ' club', ' fe'):
        if text.endswith(suffix) and len(text) > len(suffix) + 1:
            text = text[:-len(suffix)].strip()
    return text


def load_alias_groups(identities_path: Path | None = None) -> list[set[str]]:
    path = identities_path or (ROOT / 'data' / 'identities.json')
    try:
        doc = json.loads(path.read_text())
    except (OSError, ValueError):
        return []
    groups: list[set[str]] = []
    for item in doc.get('aliases') or []:
        if not isinstance(item, dict):
            continue
        src = str(item.get('source') or '')
        basis = str(item.get('basis') or '').strip()
        names = item.get('names') or []
        if src.startswith('https://') and basis and isinstance(names, list) and len(names) >= 2:
            groups.append({norm_team(n) for n in names if n})
    return groups


def same_team(a: str, b: str, evidence: dict | None = None, committed_groups: list[set[str]] | None = None) -> bool:
    na, nb = norm_team(a), norm_team(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if not evidence:
        return False
    # Check quote-attached team_aliases (from book receipts) or identity_sources (from identities.json)
    for aliases in evidence.get('team_aliases') or []:
        if isinstance(aliases, list):
            normed = {norm_team(x) for x in aliases if x}
            if na in normed and nb in normed:
                return True
    ev_sources = evidence.get('identity_sources') or []
    for item in ev_sources:
        if not isinstance(item, dict):
            continue
        src = str(item.get('source') or '')
        basis = str(item.get('basis') or '').strip()
        names = {norm_team(x) for x in (item.get('names') or []) if x}
        if src.startswith('https://') and basis and na in names and nb in names:
            if committed_groups is None or any(na in g and nb in g for g in committed_groups):
                return True
    for meta in evidence.get('team_metadata') or []:
        if isinstance(meta, dict):
            names = {norm_team(meta.get('name') or ''), norm_team(meta.get('abbreviation') or '')} - {''}
            if na in names and nb in names:
                return True
    return False


def match_orientation(fixture_teams: list[str], source_teams: list[str],
                      evidence: dict | None = None,
                      committed_groups: list[set[str]] | None = None) -> tuple[int, int] | None:
    if len(fixture_teams) != 2 or len(source_teams) != 2:
        return None
    direct = (same_team(fixture_teams[0], source_teams[0], evidence, committed_groups)
              and same_team(fixture_teams[1], source_teams[1], evidence, committed_groups))
    flipped = (same_team(fixture_teams[0], source_teams[1], evidence, committed_groups)
               and same_team(fixture_teams[1], source_teams[0], evidence, committed_groups))
    if direct and not flipped:
        return (0, 1)
    if flipped and not direct:
        return (1, 0)
    return None


def glicko_expect(pts_a: float, pts_b: float) -> float:
    q = math.log(10.0) / 400.0
    rd = 75.0
    g = 1.0 / math.sqrt(1.0 + 3.0 * q * q * rd * rd / (math.pi ** 2))
    return 1.0 / (1.0 + 10.0 ** (-g * (float(pts_a) - float(pts_b)) / 400.0))


def valve_calibrate(raw_p: float) -> float:
    return 0.5 + 0.7986 * (float(raw_p) - 0.5)


def american_to_decimal(price: float) -> float:
    val = float(price)
    if val == 0:
        raise ValueError('zero American odds')
    return 1.0 + (val / 100.0 if val > 0 else 100.0 / abs(val))


def replay_quote(evidence: dict, fixture_teams: list[str],
                 committed_groups: list[set[str]] | None = None) -> tuple[list[float], str]:
    provider = str(evidence.get('provider') or '')
    raw = evidence.get('raw') or {}
    if provider == 'Polymarket':
        outcomes = raw.get('outcomes')
        prices = raw.get('outcomePrices')
        if isinstance(outcomes, str):
            outcomes = json.loads(outcomes)
        if isinstance(prices, str):
            prices = json.loads(prices)
        if not isinstance(outcomes, list) or not isinstance(prices, list) or len(outcomes) != 2 or len(prices) != 2:
            raise ValueError('Polymarket raw outcomes/prices malformed')
        vals = [float(x) for x in prices]
        total = vals[0] + vals[1]
        if total <= 0:
            raise ValueError('Polymarket prices non-positive sum')
        normed = [vals[0] / total, vals[1] / total]
        source_teams = list(evidence.get('source_teams') or outcomes)
        order = (match_orientation(fixture_teams, source_teams, evidence, committed_groups)
                 or match_orientation(fixture_teams, outcomes, evidence, committed_groups))
        if order is None:
            raise ValueError(f'Polymarket teams {source_teams!r} do not match {fixture_teams!r}')
        return [normed[order[0]], normed[order[1]]], 'exchange_mid'

    if provider == 'Pinnacle':
        prices = raw.get('prices') or []
        by_side = {p.get('designation'): american_to_decimal(p['price']) for p in prices if isinstance(p, dict)}
        if set(by_side) != {'home', 'away'}:
            raise ValueError('Pinnacle raw prices missing home/away')
        inv = [1.0 / by_side['home'], 1.0 / by_side['away']]
        total = inv[0] + inv[1]
        normed = [inv[0] / total, inv[1] / total]
        source_teams = list(evidence.get('source_teams') or [])
        order = match_orientation(fixture_teams, source_teams, evidence, committed_groups)
        if order is None:
            raise ValueError(f'Pinnacle teams {source_teams!r} do not match {fixture_teams!r}')
        return [normed[order[0]], normed[order[1]]], 'pinnacle_devig'

    if 'decimal_odds' in evidence or ('odds' in raw and isinstance(raw.get('odds'), list)):
        raw_odds = raw.get('odds') if isinstance(raw.get('odds'), list) else evidence.get('decimal_odds')
        if not isinstance(raw_odds, list) or len(raw_odds) != 2:
            raise ValueError('Bookmaker raw odds malformed')
        dec = [float(x) for x in raw_odds]
        if dec[0] <= 1.0 or dec[1] <= 1.0:
            raise ValueError('Bookmaker decimal odds must exceed 1.0')
        if abs(dec[0] - dec[1]) < 1e-9:
            raise ValueError('Symmetric placeholder bookmaker odds rejected')
        inv = [1.0 / dec[0], 1.0 / dec[1]]
        total = inv[0] + inv[1]
        normed = [inv[0] / total, inv[1] / total]
        source_teams = list(raw.get('source_teams') or evidence.get('source_teams') or fixture_teams)
        order = match_orientation(fixture_teams, source_teams, evidence, committed_groups)
        if order is None:
            raise ValueError(f'Bookmaker teams {source_teams!r} do not match {fixture_teams!r}')
        return [normed[order[0]], normed[order[1]]], 'book_devig'

    if provider.startswith('Valve VRS model') or provider.startswith('HLTV Valve ranking'):
        points = evidence.get('points') or raw.get('points')
        if not isinstance(points, list) or len(points) != 2:
            raise ValueError('VRS model evidence missing points pair')
        raw_p = glicko_expect(float(points[0]), float(points[1]))
        p0 = valve_calibrate(raw_p)
        kind = 'vrs_mirror' if 'hltv' in provider.lower() else 'valve_vrs'
        return [p0, 1.0 - p0], kind

    raise ValueError(f'Unsupported evidence provider: {provider!r}')


def audit_snapshot(snapshot: dict, identities_path: Path | None = None) -> dict:
    committed_groups = load_alias_groups(identities_path)
    gen_at = parse_utc(snapshot.get('generated_at'))
    obs_at = parse_utc(snapshot.get('fixtures_observed_at'))
    matches = snapshot.get('matches') or []
    seen_ids: set[str] = set()
    row_reports: list[dict] = []
    problems: list[str] = []

    counts = {
        'total': len(matches),
        'open': 0,
        'not_open': 0,
        'open_with_pick': 0,
        'open_with_probabilities': 0,
        'open_research_only': 0,
        'open_unresolved': 0,
        'by_method': {},
    }

    if gen_at is None or obs_at is None:
        problems.append('Snapshot missing valid UTC generated_at or fixtures_observed_at')

    for m in matches:
        mid = str(m.get('id') or '')
        teams = list(m.get('teams') or [])
        state = m.get('state')
        method = m.get('method')
        pick = m.get('pick')
        probs = m.get('probabilities')
        fair = m.get('fair_odds')
        ev_list = m.get('evidence') or []
        attempts = m.get('attempts') or []
        row_probs: list[str] = []
        checks: list[str] = []

        if not mid or mid in seen_ids:
            row_probs.append(f'{mid}: duplicate or empty fixture id')
        seen_ids.add(mid)

        if len(teams) != 2 or not all(isinstance(t, str) and t.strip() for t in teams):
            row_probs.append(f'{mid}: teams must be two non-empty strings')

        src_url = str(m.get('source_url') or '')
        feed_url = str(m.get('feed_url') or '')
        if not (src_url.startswith('https://www.hotspawn.com/matches/') or src_url.startswith('https://play.hotspawn.com/')):
            row_probs.append(f'{mid}: missing official Hotspawn match source_url')
        else:
            checks.append('official_hotspawn_url')
        if not feed_url.startswith('https://'):
            row_probs.append(f'{mid}: missing official feed_url')

        f_sources = m.get('fixture_sources') or []
        if not f_sources or not all(str(s.get('url') or '').startswith('https://') and s.get('sha256') for s in f_sources):
            row_probs.append(f'{mid}: missing SHA-256 fixture_sources receipts')
        else:
            checks.append('fixture_source_sha256')

        start_dt = parse_utc(m.get('start'))
        lock_dt = parse_utc(m.get('lock'))
        if start_dt is None:
            row_probs.append(f'{mid}: invalid or non-UTC start timestamp')

        # Check no Hotspawn crowd-vote leakage anywhere in evidence
        ev_blob = json.dumps(ev_list).lower()
        if 'total_picks' in ev_blob or 'picked_team' in ev_blob or any(
            'hotspawn' in str(e.get('provider') or '').lower() or 'hotspawn.com' in str(e.get('url') or '').lower()
            for e in ev_list if isinstance(e, dict)
        ):
            row_probs.append(f'{mid}: Hotspawn crowd-vote or URL leaked into evidence')
        else:
            checks.append('no_hotspawn_vote_leak')

        if state != 'open':
            counts['not_open'] += 1
            if any(x is not None for x in (pick, probs, fair, method)):
                row_probs.append(f'{mid}: not_open row must have pick/probabilities/fair_odds/method = None')
            else:
                checks.append('not_open_withheld')
        else:
            counts['open'] += 1
            counts['by_method'][str(method)] = counts['by_method'].get(str(method), 0) + 1
            if gen_at and lock_dt and lock_dt <= gen_at:
                row_probs.append(f'{mid}: open row lock {m.get("lock")} is not after generated_at {snapshot.get("generated_at")}')
            if gen_at and start_dt and start_dt <= gen_at:
                row_probs.append(f'{mid}: open row start {m.get("start")} is not after generated_at {snapshot.get("generated_at")}')

            if probs is not None:
                counts['open_with_probabilities'] += 1
                if method not in (MARKET_METHODS | MODEL_METHODS):
                    row_probs.append(f'{mid}: priced row has unexpected method {method!r}')
                if not isinstance(probs, list) or len(probs) != 2:
                    row_probs.append(f'{mid}: probabilities must be a 2-element list')
                else:
                    p0, p1 = float(probs[0]), float(probs[1])
                    if not (0.0 < p0 < 1.0 and 0.0 < p1 < 1.0 and abs((p0 + p1) - 1.0) <= 1e-6):
                        row_probs.append(f'{mid}: probabilities {probs!r} do not sum to 1 in (0, 1)')
                    if abs(p0 - p1) < 1e-4:
                        row_probs.append(f'{mid}: exact 50/50 probabilities {probs!r} cannot originate a pick')
                    expected_pick = teams[0 if p0 > p1 else 1] if len(teams) == 2 else None
                    if pick != expected_pick:
                        row_probs.append(f'{mid}: pick {pick!r} != higher probability team {expected_pick!r}')
                    else:
                        counts['open_with_pick'] += 1
                        checks.append('directional_pick_verified')
                    if not isinstance(fair, list) or len(fair) != 2:
                        row_probs.append(f'{mid}: missing 2-element fair_odds')
                    else:
                        if abs(float(fair[0]) - (1.0 / p0)) > 1e-6 or abs(float(fair[1]) - (1.0 / p1)) > 1e-6:
                            row_probs.append(f'{mid}: fair_odds {fair!r} != 1/p')
                        else:
                            checks.append('fair_odds_verified')
                if not ev_list:
                    row_probs.append(f'{mid}: priced row has empty evidence')
                else:
                    ev0 = ev_list[0]
                    ev_url = str(ev0.get('url') or ev0.get('api_url') or '')
                    if not ev_url.startswith('https://') or 'hotspawn.com' in ev_url:
                        row_probs.append(f'{mid}: evidence URL {ev_url!r} is missing or points to Hotspawn')
                    else:
                        checks.append('external_evidence_url')
                    try:
                        replayed, kind = replay_quote(ev0, teams, committed_groups)
                        delta = max(abs(float(probs[0]) - replayed[0]), abs(float(probs[1]) - replayed[1]))
                        if delta > 1e-6:
                            row_probs.append(f'{mid}: replayed probabilities {replayed} differ from published {probs} (delta={delta})')
                        else:
                            checks.append(f'replayed:{kind}')
                    except Exception as exc:
                        row_probs.append(f'{mid}: evidence replay failed: {exc}')
            elif pick is not None:
                counts['open_with_pick'] += 1
                counts['open_research_only'] += 1
                if method not in RESEARCH_METHODS:
                    row_probs.append(f'{mid}: research-only pick has invalid method {method!r}')
                if pick not in teams:
                    row_probs.append(f'{mid}: research pick {pick!r} not in teams {teams!r}')
                if fair is not None:
                    row_probs.append(f'{mid}: research-only pick must keep fair_odds=None')
                if not str(m.get('reason') or '').strip():
                    row_probs.append(f'{mid}: research-only pick missing limitation reason')
                checks.append(f'research_pick:{method}')
            else:
                counts['open_unresolved'] += 1
                if any(x is not None for x in (probs, fair, method)):
                    row_probs.append(f'{mid}: unresolved open row must keep probabilities/fair_odds/method = None')
                if not str(m.get('reason') or '').strip():
                    row_probs.append(f'{mid}: unresolved open row missing limitation reason')
                if not attempts or not all(str(a.get('url') or '').startswith('https://') for a in attempts):
                    row_probs.append(f'{mid}: unresolved open row missing official source attempt URLs')
                checks.append('unresolved_fail_closed')

            # Every non-featured open row must record an HLTV attempt and an esportsbook/exchange attempt
            if method != 'exchange':
                has_hltv = any('hltv.org' in str(a.get('url') or '') for a in attempts) or bool(
                    (m.get('hltv_context') or {}).get('url') or m.get('hltv_team_pages'))
                has_book = any(
                    a.get('provider') in ('Polymarket', 'Pinnacle', 'Thunderpick', 'GG.BET', 'Book research', 'BO3.gg book listing')
                    and str(a.get('url') or '').startswith('https://')
                    for a in attempts
                )
                if not has_hltv:
                    row_probs.append(f'{mid}: non-featured row ({method}) missing HLTV attempt with official URL')
                else:
                    checks.append('hltv_attempted')
                if not has_book:
                    row_probs.append(f'{mid}: non-featured row ({method}) missing esportsbook/exchange attempt with URL')
                else:
                    checks.append('esportsbook_attempted')

        if row_probs:
            problems.extend(row_probs)
        row_reports.append({
            'id': mid,
            'teams': teams,
            'start': m.get('start'),
            'state': state,
            'method': method,
            'pick': pick,
            'probabilities': probs,
            'source_url': src_url,
            'checks': checks,
            'problems': row_probs,
        })

    return {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'counts': counts,
        'problems': problems,
        'rows': row_reports,
    }


def audit_site(site_root: Path | None = None) -> dict:
    root = site_root or ROOT
    problems: list[str] = []
    checks: list[str] = []

    # 1. Stylesheet parity and brace balance
    canonical_css = root / 'site' / 'assets' / 'style.css'
    root_css = root / 'assets' / 'style.css'
    if canonical_css.is_file() and root_css.is_file():
        c_bytes = canonical_css.read_bytes()
        r_bytes = root_css.read_bytes()
        if c_bytes != r_bytes:
            problems.append('site/assets/style.css and assets/style.css differ byte-for-byte')
        else:
            checks.append('css_byte_identical')
        text = c_bytes.decode('utf-8', errors='replace')
        if text.count('{') != text.count('}'):
            problems.append(f'CSS brace imbalance: {text.count("{")} open vs {text.count("}")} close')
        else:
            checks.append(f'css_braces_balanced:{text.count("{")}')

    # 2. Executive summary & unresolved sections on index.html
    index_path = root / 'index.html'
    if not index_path.is_file():
        problems.append('index.html missing')
    else:
        soup = BeautifulSoup(index_path.read_text(), 'html.parser')
        for sel in ('#exec-summary', '#exec-quicknav', '#freshness-strip', '#picks-at-a-glance',
                    '#unresolved-summary', '#unresolved-limits'):
            node = soup.select_one(sel)
            if node is None:
                problems.append(f'index.html missing required section {sel}')
            else:
                if sel in ('#exec-summary', '#exec-quicknav', '#freshness-strip') and node.find_parent('details'):
                    problems.append(f'index.html {sel} is hidden inside a collapsed <details> element')
                checks.append(f'index_has_{sel.lstrip("#")}')
        exec_bar = soup.select_one('#exec-summary')
        if exec_bar:
            hrefs = {a.get('href') for a in exec_bar.select('a[href]')}
            for target in ('picks.html', '#picks-at-a-glance', 'unresolved.html',
                           '#unresolved-summary', 'matches.html', 'review.html'):
                if target not in hrefs:
                    problems.append(f'#exec-summary missing link to {target}')

    # 3. Every table row on picks.html, matches.html, unresolved.html, review.html has an https:// source link
    for page_name in ('picks.html', 'matches.html', 'unresolved.html', 'review.html'):
        p = root / page_name
        if not p.is_file():
            problems.append(f'{page_name} missing')
            continue
        soup = BeautifulSoup(p.read_text(), 'html.parser')
        rows = soup.select('tbody tr')
        for idx, tr in enumerate(rows, 1):
            ext = [a.get('href') for a in tr.select('a[href]') if str(a.get('href') or '').startswith('https://')]
            if not ext:
                problems.append(f'{page_name} row {idx} has no https:// official source link')
        checks.append(f'{page_name}_rows_linked:{len(rows)}')

    return {'checks': checks, 'problems': problems}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--data', default=str(ROOT / 'data' / 'latest.json'))
    parser.add_argument('--site', default=str(ROOT))
    parser.add_argument('--output', default=None)
    args = parser.parse_args(argv)

    snapshot = json.loads(Path(args.data).read_text())
    snap_report = audit_snapshot(snapshot)
    site_report = audit_site(Path(args.site))
    combined = {
        'schema_version': 1,
        'session': 'fbea4413',
        'snapshot_generated_at': snap_report['snapshot_generated_at'],
        'fixtures_observed_at': snap_report['fixtures_observed_at'],
        'counts': snap_report['counts'],
        'site_checks': site_report['checks'],
        'problems': snap_report['problems'] + site_report['problems'],
        'rows': snap_report['rows'],
    }
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({
        'snapshot_generated_at': combined['snapshot_generated_at'],
        'counts': combined['counts'],
        'site_checks': len(combined['site_checks']),
        'problems': len(combined['problems']),
    }))
    return 1 if combined['problems'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
