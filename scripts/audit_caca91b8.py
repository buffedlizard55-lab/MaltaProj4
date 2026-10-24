"""Independent line-by-line audit for session caca91b8 (2026-10-24 UTC).

Shares zero probability, orientation, or Valve VRS calculation code with
``scripts.core`` or ``scripts.vrs``: every de-vig, exchange midpoint,
Glicko expectation, calibration slope, identity alias check, fallback ladder
order check, and HTML link check is re-derived from raw evidence and committed
registries only, with zero network access.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HOTSPAWN_HOSTS = {'hotspawn.com', 'www.hotspawn.com', 'play.hotspawn.com'}
FEED_HOST = 'phpstack-1372681-6459848.cloudwaysapps.com'
TRUSTED_EVIDENCE_HOSTS = {
    'polymarket.com',
    'gamma-api.polymarket.com',
    'guest.api.arcadia.pinnacle.com',
    'pinnacle.com',
    'www.pinnacle.com',
    'hltv.org',
    'www.hltv.org',
    'bo3.gg',
    'api.bo3.gg',
    'thunderpick.io',
    'egamersworld.com',
    'gg.bet',
    'github.com',
    'raw.githubusercontent.com',
}
PRICED_METHODS = {
    'exchange',
    'exchange_wide',
    'sportsbook',
    'bookmaker_fallback',
    'model_vrs',
    'model_vrs_mirror',
}
UNPRICED_PICK_METHODS = {'research_form', 'research_ranking'}
PRIMARY_PAGES = (
    'index.html',
    'picks.html',
    'unresolved.html',
    'matches.html',
    'analysis.html',
    'sources.html',
    'evidence.html',
    'methodology.html',
    'review.html',
)


def _fold(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f'Invalid team label: {name!r}')
    nfkd = unicodedata.normalize('NFKD', name).casefold()
    stripped = ''.join(ch for ch in nfkd if not unicodedata.combining(ch))
    return ''.join(ch for ch in unicodedata.normalize('NFKC', stripped) if ch.isalnum())


def _parse_utc(value: str | int | float) -> datetime:
    if value is None or value == '':
        raise ValueError('Missing timestamp')
    if isinstance(value, (int, float)) or str(value).isdigit():
        return datetime.fromtimestamp(float(value) / 1000.0, timezone.utc)
    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError(f'Naive timestamp: {value!r}')
    return dt.astimezone(timezone.utc)


def load_sourced_alias_map(identities_path: Path | None = None) -> dict[str, str]:
    path = identities_path or (ROOT / 'data' / 'identities.json')
    raw = json.loads(path.read_text(encoding='utf-8'))
    mapping: dict[str, str] = {}
    for entry in raw.get('aliases', []):
        src = entry.get('source', '')
        basis = entry.get('basis', '')
        names = entry.get('names', [])
        canonical = entry.get('canonical', '')
        if not (isinstance(src, str) and src.startswith('https://')):
            continue
        if not (isinstance(basis, str) and basis.strip()):
            continue
        if not canonical or len(names) < 2:
            continue
        canon_key = _fold(canonical)
        for label in names:
            mapping[_fold(label)] = canon_key
    return mapping


def load_vrs_standings(standings_path: Path | None = None) -> dict[int, dict]:
    path = standings_path or (ROOT / 'data' / 'vrs' / 'standings_global_2026_10_05.md')
    by_rank: dict[int, dict] = {}
    pattern = re.compile(
        r'^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
    )
    for line in path.read_text(encoding='utf-8').splitlines():
        m = pattern.match(line)
        if not m:
            continue
        rank = int(m.group(1))
        points = int(m.group(2))
        team = m.group(3).strip()
        roster = [p.strip() for p in m.group(4).split(',') if p.strip()]
        by_rank[rank] = {'rank': rank, 'points': points, 'team': team, 'roster': roster}
    return by_rank


def independent_glicko_calibrated(
    pts_a: float,
    pts_b: float,
    rd: float = 75.0,
    slope: float = 0.7986,
) -> tuple[list[float], list[float]]:
    q = math.log(10.0) / 400.0
    g = 1.0 / math.sqrt(1.0 + 3.0 * (q * q) * (rd * rd) / (math.pi * math.pi))
    exp_a = 1.0 / (1.0 + 10.0 ** (-g * (pts_a - pts_b) / 400.0))
    exp_b = 1.0 - exp_a
    cal_a = 0.5 + slope * (exp_a - 0.5)
    cal_b = 1.0 - cal_a
    return [exp_a, exp_b], [cal_a, cal_b]


def _match_side_order(
    fixture_teams: list[str],
    source_teams: list[str],
    alias_map: dict[str, str],
    extra_aliases: list[list[str]] | None = None,
    extra_sources: list[str] | None = None,
) -> list[int]:
    if len(fixture_teams) != 2 or len(source_teams) != 2:
        raise ValueError('Both fixture_teams and source_teams must have length 2')
    local_map = dict(alias_map)
    if extra_aliases and len(extra_aliases) == 2:
        if not extra_sources or len(extra_sources) != 2 or not all(
            isinstance(u, str) and u.startswith('https://') for u in extra_sources
        ):
            raise ValueError('team_aliases lacks https:// alias_sources')
        for idx, group in enumerate(extra_aliases):
            canon = local_map.get(_fold(source_teams[idx]), _fold(source_teams[idx]))
            for label in group:
                local_map[_fold(label)] = canon
    fix_keys = [local_map.get(_fold(t), _fold(t)) for t in fixture_teams]
    src_keys = [local_map.get(_fold(t), _fold(t)) for t in source_teams]
    if len(set(fix_keys)) != 2 or len(set(src_keys)) != 2:
        raise ValueError(f'Collapsed team keys: {fix_keys} vs {src_keys}')
    if fix_keys == src_keys:
        return [0, 1]
    if fix_keys == [src_keys[1], src_keys[0]]:
        return [1, 0]
    raise ValueError(f'Unverified team mapping: {fixture_teams} vs {source_teams}')


def replay_row_independently(
    row: dict,
    alias_map: dict[str, str],
    vrs_by_rank: dict[int, dict],
) -> tuple[list[float], str]:
    method = row.get('method')
    ev_list = row.get('evidence') or []
    if not ev_list:
        raise ValueError(f"Row {row.get('id')} has method={method!r} without evidence")
    ev = ev_list[0]
    for url_key in ('url', 'api_url'):
        val = ev.get(url_key)
        if not (isinstance(val, str) and val.startswith('https://')):
            raise ValueError(f"Row {row.get('id')} missing https {url_key}")
        host = (urlparse(val).hostname or '').lower()
        if host in HOTSPAWN_HOSTS or host == FEED_HOST:
            raise ValueError(f"Row {row.get('id')} contaminated by Hotspawn host {host}")
        if host not in TRUSTED_EVIDENCE_HOSTS:
            raise ValueError(f"Row {row.get('id')} untrusted evidence host {host}")

    if method in ('exchange', 'exchange_wide'):
        raw = ev.get('raw') or {}
        outcomes = raw.get('outcomes')
        prices = raw.get('outcomePrices')
        if isinstance(outcomes, str):
            outcomes = json.loads(outcomes)
        if isinstance(prices, str):
            prices = json.loads(prices)
        raw_probs = [float(x) for x in prices]
        if len(raw_probs) != 2 or any(p <= 0.0 or p >= 1.0 for p in raw_probs):
            raise ValueError(f"Invalid exchange outcomePrices: {prices}")
        total = raw_probs[0] + raw_probs[1]
        norm_probs = [raw_probs[0] / total, raw_probs[1] / total]
        meta = ev.get('team_metadata') or (ev.get('event') or {}).get('teams') or []
        pm_aliases = [
            [t, *[m.get('abbreviation', '') for m in meta if m.get('name') == t and len(_fold(m.get('abbreviation', '') or 'x')) >= 4]]
            for t in outcomes
        ]
        order = _match_side_order(
            row['teams'],
            outcomes,
            alias_map,
            extra_aliases=pm_aliases,
            extra_sources=[ev['url'], ev['url']],
        )
        mapped = [norm_probs[order[0]], norm_probs[order[1]]]
        if abs(mapped[0] - mapped[1]) < 1e-12:
            raise ValueError(f"Symmetric exchange quote accepted on {row['id']}")
        liquidity = float(raw.get('liquidity') or ev.get('liquidity') or 0.0)
        if liquidity < 100.0:
            raise ValueError(f"Exchange liquidity < $100 on {row['id']}: {liquidity}")
        bid = float(raw.get('bestBid'))
        ask = float(raw.get('bestAsk'))
        spread = ask - bid
        ceiling = 0.25 if method == 'exchange' else 0.60
        if spread < -1e-9 or spread > ceiling + 1e-9:
            raise ValueError(f"Spread {spread} outside {method} gate ({ceiling})")
        if _parse_utc(ev['start']) != _parse_utc(row['start']):
            raise ValueError(f"Exchange start mismatch on {row['id']}")
        return mapped, method

    if method in ('sportsbook', 'bookmaker_fallback'):
        odds = ev.get('decimal_odds') or (ev.get('raw') or {}).get('odds')
        if not odds or len(odds) != 2:
            raise ValueError(f"Missing two-way odds on {row['id']}")
        dec = [float(x) for x in odds]
        if any(not math.isfinite(d) or d <= 1.0 for d in dec):
            raise ValueError(f"Invalid decimal odds on {row['id']}: {dec}")
        if abs(dec[0] - dec[1]) < 1e-12:
            raise ValueError(f"Symmetric bookmaker placeholder accepted on {row['id']}")
        inv = [1.0 / dec[0], 1.0 / dec[1]]
        overround = (inv[0] + inv[1]) - 1.0
        if not (-0.02 <= overround <= 0.25):
            raise ValueError(f"Overround {overround} out of bounds on {row['id']}")
        devigged = [inv[0] / (inv[0] + inv[1]), inv[1] / (inv[0] + inv[1])]
        src_teams = ev.get('source_teams') or (ev.get('raw') or {}).get('source_teams')
        order = _match_side_order(
            row['teams'],
            src_teams,
            alias_map,
            extra_aliases=ev.get('team_aliases'),
            extra_sources=ev.get('alias_sources'),
        )
        if _parse_utc(ev['start']) != _parse_utc(row['start']):
            raise ValueError(f"Bookmaker start mismatch on {row['id']}")
        return [devigged[order[0]], devigged[order[1]]], method

    if method in ('model_vrs', 'model_vrs_mirror'):
        pts = ev.get('points') or []
        ranks = ev.get('standings') or []
        if len(pts) != 2 or len(ranks) != 2:
            raise ValueError(f"Missing VRS points/standings on {row['id']}")
        if pts[0] == pts[1]:
            raise ValueError(f"Equal VRS points cannot originate a directional pick on {row['id']}")
        raw_exp, cal = independent_glicko_calibrated(
            float(pts[0]),
            float(pts[1]),
            rd=float(ev.get('rating_deviation', 75.0)),
            slope=float(ev.get('calibration_slope', 0.7986)),
        )
        for i in (0, 1):
            if abs(raw_exp[i] - float(ev['raw_expected'][i])) > 1e-12:
                raise ValueError(f"VRS raw_expected mismatch on {row['id']}")
        for chk in ev.get('roster_checks') or []:
            if chk.get('lineup') and int(chk.get('overlap', 0)) < 3:
                raise ValueError(f"VRS roster overlap < 3 on {row['id']}: {chk}")
        warning = (ev.get('warning') or '') + ' ' + ' '.join(row.get('flags') or [])
        if 'not a market price' not in warning.lower():
            raise ValueError(f"Model row {row['id']} lacks 'not a market price' disclosure")
        if method == 'model_vrs' and ev.get('standings_as_of') == '2026-10-05' and vrs_by_rank:
            for side_idx in (0, 1):
                rank_num = int(ranks[side_idx])
                official = vrs_by_rank.get(rank_num)
                if not official:
                    raise ValueError(f"Rank #{rank_num} missing from vendored Valve 2026-10-05 file")
                if official['points'] != int(pts[side_idx]):
                    raise ValueError(
                        f"Rank #{rank_num} points {pts[side_idx]} != official {official['points']}"
                    )
        return cal, method

    raise ValueError(f"Unsupported priced method {method!r} on {row.get('id')}")


def audit_snapshot(snapshot: dict, root: Path = ROOT) -> dict:
    alias_map = load_sourced_alias_map(root / 'data' / 'identities.json')
    vrs_by_rank = load_vrs_standings(root / 'data' / 'vrs' / 'standings_global_2026_10_05.md')
    errors: list[str] = []
    seen_ids: set[str] = set()
    method_counts: dict[str, int] = {}
    reproduced = 0
    rejected_even_quotes = 0
    open_rows = 0

    for row in snapshot.get('matches', []):
        mid = str(row.get('id', '')).strip()
        if not mid or mid in seen_ids:
            errors.append(f'Invalid or duplicate fixture id: {mid!r}')
            continue
        seen_ids.add(mid)
        src_url = row.get('source_url', '')
        feed_url = row.get('feed_url', '')
        if not (isinstance(src_url, str) and src_url.startswith('https://') and urlparse(src_url).hostname in HOTSPAWN_HOSTS):
            errors.append(f'{mid}: missing official Hotspawn source_url ({src_url!r})')
        if not (isinstance(feed_url, str) and urlparse(feed_url).hostname == FEED_HOST):
            errors.append(f'{mid}: missing official Hotspawn feed_url ({feed_url!r})')

        for att in row.get('attempts') or []:
            rq = att.get('rejected_quote')
            if rq is not None:
                rejected_even_quotes += 1
                if att.get('status') != 'unresolved':
                    errors.append(f"{mid}: rejected_quote attempt must keep status='unresolved'")
                if 'Rejected evidence' not in (rq.get('notice') or ''):
                    errors.append(f'{mid}: rejected_quote missing explicit notice')

        if row.get('state') != 'open':
            if row.get('pick') is not None or row.get('probabilities') is not None:
                errors.append(f'{mid}: non-open row carries pick/probabilities')
            continue

        open_rows += 1
        method = row.get('method')
        method_counts[str(method)] = method_counts.get(str(method), 0) + 1

        if method != 'exchange':
            providers = [a.get('provider', '') for a in (row.get('attempts') or [])]
            if 'HLTV' not in providers:
                errors.append(f'{mid}: non-featured row ({method}) did not attempt HLTV')
            else:
                hltv_idx = providers.index('HLTV')
                book_indices = [
                    idx for idx, p in enumerate(providers)
                    if p in ('Pinnacle', 'Thunderpick', 'GG.BET', 'Thunderpick (via BO3.gg API)', 'Book research')
                ]
                if not book_indices:
                    errors.append(f'{mid}: non-featured row ({method}) recorded no sportsbook attempt')
                elif hltv_idx > min(book_indices):
                    errors.append(f'{mid}: sportsbook attempted before HLTV ({providers})')
                for model_label in ('Valve VRS model', 'HLTV Valve ranking (Valve points)'):
                    if model_label in providers and min(book_indices, default=999) > providers.index(model_label):
                        errors.append(f'{mid}: {model_label} attempted before sportsbooks ({providers})')

        if row.get('pick') is None:
            if any(row.get(k) is not None for k in ('probabilities', 'fair_odds', 'method')):
                errors.append(f'{mid}: unresolved row must leave probabilities/fair_odds/method blank')
            if not (row.get('reason') or '').strip():
                errors.append(f'{mid}: unresolved row missing limitation reason')
            if not (row.get('attempts') or []):
                errors.append(f'{mid}: unresolved row missing source attempts')
            continue

        if row['pick'] not in row['teams']:
            errors.append(f"{mid}: pick {row['pick']!r} not in {row['teams']}")

        if method in UNPRICED_PICK_METHODS:
            if row.get('probabilities') is not None or row.get('fair_odds') is not None:
                errors.append(f'{mid}: research-only pick must leave probabilities blank')
            continue

        if method not in PRICED_METHODS:
            errors.append(f'{mid}: unknown method {method!r}')
            continue

        probs = row.get('probabilities')
        fair = row.get('fair_odds')
        if not probs or len(probs) != 2 or not fair or len(fair) != 2:
            errors.append(f'{mid}: priced row missing two-sided probabilities/fair_odds')
            continue
        if abs((probs[0] + probs[1]) - 1.0) > 1e-9:
            errors.append(f'{mid}: probabilities do not sum to 1 ({probs})')
        if abs(probs[0] - probs[1]) < 1e-12:
            errors.append(f'{mid}: symmetric 50/50 probability is forbidden ({probs})')
        expected_pick = row['teams'][0] if probs[0] > probs[1] else row['teams'][1]
        if row['pick'] != expected_pick:
            errors.append(f"{mid}: pick {row['pick']!r} != higher-probability team {expected_pick!r}")
        for idx in (0, 1):
            if abs(fair[idx] - (1.0 / probs[idx])) > 1e-9:
                errors.append(f'{mid}: fair_odds[{idx}] != 1/p[{idx}]')

        try:
            re_probs, _ = replay_row_independently(row, alias_map, vrs_by_rank)
            for idx in (0, 1):
                if abs(re_probs[idx] - probs[idx]) > 1e-9:
                    errors.append(
                        f'{mid}: independent replay {re_probs} != published {probs}'
                    )
            reproduced += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f'{mid}: replay failed: {exc}')

    return {
        'generated_at': snapshot.get('generated_at'),
        'coverage': snapshot.get('coverage'),
        'coverage_counts': snapshot.get('coverage_counts'),
        'rows_total': len(snapshot.get('matches', [])),
        'rows_open': open_rows,
        'probabilities_reproduced': reproduced,
        'method_counts': method_counts,
        'rejected_even_quotes': rejected_even_quotes,
        'errors': errors,
    }


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.in_details = 0
        self.outside_details_hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'details':
            self.in_details += 1
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.hrefs.append(href)
                if self.in_details == 0:
                    self.outside_details_hrefs.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == 'details' and self.in_details > 0:
            self.in_details -= 1


def audit_site(site_dir: Path, root: Path = ROOT) -> dict:
    errors: list[str] = []
    for page_name in PRIMARY_PAGES:
        p = site_dir / page_name
        if not p.exists():
            errors.append(f'Missing primary page: {page_name}')
    index_path = site_dir / 'index.html'
    if index_path.exists():
        parser = _LinkCollector()
        html = index_path.read_text(encoding='utf-8')
        parser.feed(html)
        for target in ('picks.html', 'unresolved.html', 'matches.html', 'analysis.html', 'sources.html', 'evidence.html', 'review.html'):
            if not any(h.split('#')[0] == target for h in parser.outside_details_hrefs):
                errors.append(f'index.html missing unfolded executive link to {target}')
        if not any(h in ('methodology.html', 'sources.html#method') for h in parser.outside_details_hrefs):
            errors.append('index.html missing unfolded executive link to methodology')
        if 'id="unresolved-picks"' not in html and 'id="unresolved-summary"' not in html:
            errors.append('index.html missing unresolved section')

    review_path = site_dir / 'review.html'
    notes = json.loads((root / 'data' / 'review-notes.json').read_text(encoding='utf-8'))
    caca_notes = [n for n in notes if str(n.get('id', '')).startswith('session-caca91b8-')]
    if review_path.exists():
        rhtml = review_path.read_text(encoding='utf-8')
        for note in caca_notes:
            if note['id'] not in rhtml:
                errors.append(f"review.html missing rendered note {note['id']}")
    return {
        'pages_checked': len(PRIMARY_PAGES),
        'session_review_notes_checked': len(caca_notes),
        'errors': errors,
    }


if __name__ == '__main__':
    snap = json.loads((ROOT / 'data' / 'latest.json').read_text(encoding='utf-8'))
    report = audit_snapshot(snap, ROOT)
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report['errors'] else 0)
