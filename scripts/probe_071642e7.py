"""Comprehensive primary-source gap & alias/roster discovery probe (session 071642e7).

Runs on a GitHub-hosted runner (or locally against an existing snapshot) inside the
session-exclusive scope ``research/session-071642e7/``. It never mutates shared board
files, receipts, identities, or generated pages; every HTTP read is archived as
deterministic gzip named by its SHA-256 digest so every finding can be independently
replayed offline byte-for-byte.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from scripts import books, hltv, vrs, vrs_mirror
from scripts.core import (
    FIXTURES,
    GAMMA,
    PIN,
    devig,
    dt,
    iso,
    norm,
    plain_name,
    pinnacle_candidates,
    polymarket_candidates,
)
from scripts.refresh import Sources

PLACEHOLDER = (1.8, 1.8)
STAVKA_LINK_RE = re.compile(r'href=["\']((?:https?://(?:www\.)?stavka\.tv)?/matches/csgo/[a-z0-9-]+/?)["\']', re.I)
EGW_LINK_RE = re.compile(r'href=["\']((?:https?://(?:www\.)?egamersworld\.com)?/counterstrike/match/[^"\'#?]+)["\']', re.I)


def archive_bytes(raw_bytes: bytes, raw_dir: Path) -> dict:
    raw_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(raw_bytes).hexdigest()
    gz_path = raw_dir / f'{digest}.gz'
    if not gz_path.exists():
        gz_path.write_bytes(gzip.compress(raw_bytes, mtime=0))
    return {'sha256': digest, 'bytes': len(raw_bytes), 'archive': f'raw/{digest}.gz'}


def fetch_archived(src: Sources, label: str, url: str, raw_dir: Path, records: list, as_json: bool = False):
    try:
        payload, meta = src.get(f'{label} (071642e7)', url, as_json=as_json)
    except Exception as exc:
        entry = {
            'label': label,
            'url': url,
            'status': 'error',
            'error': str(exc)[:300],
            'observed_at': iso(datetime.now(timezone.utc)),
        }
        records.append(entry)
        return None, entry
    if as_json:
        raw_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        src_path = Path('runtime/sources') / f"{meta.get('sha256', '')}.json"
        if src_path.exists():
            raw_bytes = src_path.read_bytes()
    else:
        raw_bytes = payload.encode('utf-8', 'replace') if isinstance(payload, str) else bytes(payload)
        src_path = Path('runtime/sources') / f"{meta.get('sha256', '')}.html"
        if src_path.exists():
            raw_bytes = src_path.read_bytes()
    saved = archive_bytes(raw_bytes, raw_dir)
    entry = {
        'label': label,
        'url': url,
        'status': meta.get('http_status', 200),
        'observed_at': meta.get('observed_at') or iso(datetime.now(timezone.utc)),
        'retrieved_at': meta.get('retrieved_at'),
        **saved,
    }
    records.append(entry)
    return payload, entry


def stavka_slugs_for_pair(teams: list[str], start_iso: str, discovered_urls: list[str]) -> list[str]:
    out: list[str] = []

    def add(u: str):
        u = u.rstrip('/')
        if u.startswith('/'):
            u = 'https://stavka.tv' + u
        if u not in out:
            out.append(u)

    def slugify(name: str) -> list[str]:
        base = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        variants = [base]
        stripped_ex = re.sub(r'^ex-', '', base)
        if stripped_ex and stripped_ex not in variants:
            variants.append(stripped_ex)
        return variants

    # 1. Any URL discovered directly on stavka.tv index/date pages matching either team token
    tokens = {tok for t in teams for tok in re.findall(r'[a-z0-9]{4,}', t.lower()) if tok not in {'team', 'gaming', 'esports', 'academy', 'club'}}
    for u in discovered_urls:
        low = u.lower()
        if any(tok in low for tok in tokens):
            add(u)

    # 2. Deterministic date + slug permutations
    try:
        base_day = dt(start_iso).date()
    except Exception:
        base_day = datetime.now(timezone.utc).date()
    s1_list = slugify(teams[0])
    s2_list = slugify(teams[1])
    for offset in (0, -1, 1):
        stamp = (base_day + timedelta(days=offset)).strftime('%d-%m-%Y')
        for a in s1_list:
            for b in s2_list:
                add(f'https://stavka.tv/matches/csgo/{stamp}-{a}-{b}')
                add(f'https://stavka.tv/matches/csgo/{stamp}-{b}-{a}')
    return out[:18]


def roster_overlap_scan(lineups: dict[str, list[str]], standings_sets: list[tuple[str, dict]]) -> list[dict]:
    hits = []
    for team, players in (lineups or {}).items():
        pset = {plain_name(p) for p in players if p and plain_name(p)}
        if not pset:
            continue
        for source_label, table in standings_sets:
            if not table or not table.get('teams'):
                continue
            for row in table['teams']:
                rset = {plain_name(p) for p in (row.get('roster') or []) if p and plain_name(p)}
                shared = sorted(pset & rset)
                if len(shared) >= 2 or plain_name(row['name']) == plain_name(team) or norm(row['name']) == norm(team):
                    hits.append({
                        'fixture_team': team,
                        'fixture_lineup': players,
                        'source': source_label,
                        'as_of': table.get('as_of'),
                        'standing': row.get('standing'),
                        'points': row.get('points'),
                        'listed_name': row.get('name'),
                        'listed_roster': row.get('roster'),
                        'details': row.get('details'),
                        'shared_count': len(shared),
                        'shared_players': shared,
                        'passes_valve_3_rule': len(shared) >= 3,
                    })
    return hits


def extract_lineups_for_row(row: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for x in (row.get('hltv_context') or {}).get('lineups') or []:
        if x.get('team') and x.get('players'):
            out[x['team']] = list(x['players'])
    for x in (row.get('hltv_team_pages') or {}).get('teams') or []:
        players = x.get('players') or x.get('lineup')
        if x.get('team') and players:
            out.setdefault(x['team'], list(players))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', default='runtime/latest.json')
    ap.add_argument('--output', default='research/session-071642e7')
    args = ap.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)

    snap_path = Path(args.snapshot)
    snapshot = json.loads(snap_path.read_text())
    now = datetime.now(timezone.utc)

    # Save manifest of runtime/sources archived during scripts.refresh
    refresh_sources = []
    for check in snapshot.get('source_checks') or []:
        entry = dict(check)
        sha = entry.get('sha256')
        if sha:
            for ext in ('.json', '.html'):
                candidate = Path('runtime/sources') / f'{sha}{ext}'
                if candidate.exists():
                    saved = archive_bytes(candidate.read_bytes(), raw_dir)
                    entry['archived_raw'] = saved['archive']
                    break
        refresh_sources.append(entry)

    src = Sources(now)
    probe_reads: list[dict] = []

    # Load Valve official standings + HLTV dated Valve mirror for 3-of-5 roster scan
    official_standings, official_meta, official_err = vrs.fetch(src, now, os.environ.get('GITHUB_TOKEN'))
    mirror_standings, mirror_meta, mirror_err = vrs_mirror.fetch(src, now)
    standings_sets = []
    if official_standings:
        standings_sets.append(('valve_official', official_standings))
    if mirror_standings:
        standings_sets.append(('hltv_valve_mirror', mirror_standings))

    # Load all active Polymarket & Pinnacle candidates to detect same-time alias mismatches
    poly_all = []
    sports, _ = fetch_archived(src, 'Polymarket sports', GAMMA + '/sports', raw_dir, probe_reads, as_json=True)
    if isinstance(sports, list):
        cs2 = [s for s in sports if s.get('sport') == 'cs2']
        if len(cs2) == 1:
            for offset in range(0, 1000, 100):
                params = urlencode({
                    'series_id': cs2[0]['series'],
                    'active': 'true',
                    'closed': 'false',
                    'end_date_min': now.strftime('%Y-%m-%dT00:00:00Z'),
                    'limit': 100,
                    'offset': offset,
                    'order': 'id',
                    'ascending': 'true',
                })
                batch, rec = fetch_archived(
                    src, f'Polymarket batch {offset // 100 + 1}', f'{GAMMA}/events?{params}',
                    raw_dir, probe_reads, as_json=True,
                )
                if not isinstance(batch, list):
                    break
                poly_all.extend(polymarket_candidates(batch, rec['observed_at']))
                if len(batch) < 100:
                    break

    pin_all = []
    pin_m, pm_rec = fetch_archived(src, 'Pinnacle matchups', f'{PIN}/sports/12/matchups?withSpecials=false', raw_dir, probe_reads, as_json=True)
    pin_l, pl_rec = fetch_archived(src, 'Pinnacle straight lines', f'{PIN}/sports/12/markets/straight', raw_dir, probe_reads, as_json=True)
    if isinstance(pin_m, list) and isinstance(pin_l, list):
        pin_all = pinnacle_candidates(pin_m, pin_l, min(pm_rec['observed_at'], pl_rec['observed_at'], key=dt))

    # Discover live Stavka CS2 match links from Stavka index pages
    discovered_stavka: list[str] = []
    for st_url in (
        'https://stavka.tv/matches/csgo',
        'https://stavka.tv/matches/csgo?date=' + now.strftime('%Y-%m-%d'),
        'https://stavka.tv/matches/csgo?date=' + (now + timedelta(days=1)).strftime('%Y-%m-%d'),
    ):
        html, _ = fetch_archived(src, 'Stavka index', st_url, raw_dir, probe_reads, as_json=False)
        if isinstance(html, str):
            for hit in STAVKA_LINK_RE.findall(html):
                full = ('https://stavka.tv' + hit) if hit.startswith('/') else hit
                full = full.rstrip('/')
                if full not in discovered_stavka:
                    discovered_stavka.append(full)

    # Discover live EGamersWorld match links
    discovered_egw: list[str] = []
    for egw_url in (
        'https://egamersworld.com/counterstrike/matches',
        'https://egamersworld.com/counterstrike/matches/page/2',
    ):
        html, _ = fetch_archived(src, 'EGamersWorld index', egw_url, raw_dir, probe_reads, as_json=False)
        if isinstance(html, str):
            for hit in EGW_LINK_RE.findall(html):
                full = ('https://egamersworld.com' + hit) if hit.startswith('/') else hit
                full = full.rstrip('/')
                if full not in discovered_egw:
                    discovered_egw.append(full)

    open_rows = [m for m in snapshot.get('matches') or [] if m.get('state') == 'open']
    gap_rows = [m for m in open_rows if m.get('probabilities') is None or not m.get('pick')]

    gap_reports = []
    for row in gap_rows:
        teams = row.get('teams') or []
        start = row.get('start')
        lineups = extract_lineups_for_row(row)
        item = {
            'id': str(row.get('id')),
            'teams': teams,
            'competition': row.get('competition'),
            'tier': row.get('tier'),
            'best_of': row.get('best_of'),
            'start': start,
            'lock': row.get('lock'),
            'source_url': row.get('source_url'),
            'current_pick': row.get('pick'),
            'current_method': row.get('method'),
            'current_reason': row.get('reason'),
            'hltv_context': row.get('hltv_context'),
            'hltv_team_pages': row.get('hltv_team_pages'),
            'vrs_research': row.get('vrs_research'),
            'same_start_polymarket': [],
            'same_start_pinnacle': [],
            'hltv_team_search': {},
            'roster_standings_candidates': [],
            'stavka_checks': [],
            'egw_checks': [],
        }

        # Same-UTC-start Polymarket / Pinnacle candidates (detects alias gaps!)
        for c in poly_all:
            try:
                if abs((dt(c['start']) - dt(start)).total_seconds()) <= 3600:
                    item['same_start_polymarket'].append({
                        'id': c['id'],
                        'teams': c['teams'],
                        'start': c['start'],
                        'prices': c['prices'],
                        'bestBid': c['raw'].get('bestBid'),
                        'bestAsk': c['raw'].get('bestAsk'),
                        'liquidity': c['raw'].get('liquidity'),
                        'acceptingOrders': c['raw'].get('acceptingOrders'),
                        'api_url': c['api_url'],
                        'url': c['url'],
                    })
            except Exception:
                pass

        for c in pin_all:
            try:
                if abs((dt(c['start']) - dt(start)).total_seconds()) <= 3600:
                    item['same_start_pinnacle'].append({
                        'id': c['id'],
                        'teams': c['teams'],
                        'start': c['start'],
                        'league': ((c['raw'].get('matchup') or {}).get('league') or {}).get('name'),
                        'prices': (c['line'] or {}).get('prices'),
                        'cutoffAt': (c['line'] or {}).get('cutoffAt'),
                        'status': c.get('status'),
                        'line_status': (c['line'] or {}).get('status'),
                    })
            except Exception:
                pass

        # Search HLTV team pages for each team if lineup missing
        for team in teams:
            q_url = hltv.SEARCH + re.sub(r'\s+', '+', team.strip())
            s_html, s_rec = fetch_archived(src, f'HLTV team search {team}', q_url, raw_dir, probe_reads, as_json=False)
            found_teams = {}
            if isinstance(s_html, str):
                found_teams = hltv.search_teams(s_html)
            profiles = []
            for t_url, t_label in list(found_teams.items())[:3]:
                p_html, p_rec = fetch_archived(src, f'HLTV profile {t_label}', t_url, raw_dir, probe_reads, as_json=False)
                if isinstance(p_html, str):
                    soup = BeautifulSoup(p_html, 'html.parser')
                    txt = ' '.join(soup.get_text(' ', strip=True).split())
                    players = [a.get_text(strip=True) for a in soup.select('.bodyshot-team a .text-ellipsis, .bodyshot-team-bg a .text-ellipsis')]
                    if not players:
                        players = [img.get('title').strip() for img in soup.select('.bodyshot-team img[title]') if img.get('title')]
                    if players and norm(t_label) == norm(team):
                        lineups.setdefault(team, players[:5])
                    profiles.append({
                        'url': t_url,
                        'label': t_label,
                        'observed_at': p_rec['observed_at'],
                        'sha256': p_rec['sha256'],
                        'players': players[:6],
                        'snippet': txt[:500],
                    })
            item['hltv_team_search'][team] = {
                'search_url': q_url,
                'observed_at': s_rec.get('observed_at'),
                'candidates': found_teams,
                'profiles': profiles,
            }

        # Scan all Valve official + HLTV Valve mirror rows against known lineups
        item['roster_standings_candidates'] = roster_overlap_scan(lineups, standings_sets)

        # Probe Stavka canonical pages
        for st_url in stavka_slugs_for_pair(teams, start, discovered_stavka):
            html, rec = fetch_archived(src, f"Stavka {row['id']}", st_url, raw_dir, probe_reads, as_json=False)
            if not isinstance(html, str):
                item['stavka_checks'].append({'url': st_url, 'status': 'error_or_404', 'error': rec.get('error')})
                continue
            parsed = books.parse_listing(html)
            item['stavka_checks'].append({
                'url': st_url,
                'observed_at': rec['observed_at'],
                'sha256': rec['sha256'],
                'archive': rec['archive'],
                'parsed_readings': parsed,
            })

        # Probe EGamersWorld pages matching team tokens + existing book-receipts entries
        egw_targets = []
        tokens = [tok for t in teams for tok in re.findall(r'[a-z0-9]{4,}', t.lower()) if tok not in {'team', 'gaming', 'esports', 'academy'}]
        for u in discovered_egw:
            if any(tok in u.lower() for tok in tokens):
                egw_targets.append(u)
        try:
            doc = json.loads(Path('data/book-receipts.json').read_text())
            for entry in (doc.get('receipts') or []) + (doc.get('rejected_listings') or []):
                if str(entry.get('fixture_id')) == str(row.get('id')) and entry.get('url'):
                    if entry['url'] not in egw_targets:
                        egw_targets.append(entry['url'])
        except Exception:
            pass
        for egw_url in egw_targets[:8]:
            html, rec = fetch_archived(src, f"EGW {row['id']}", egw_url, raw_dir, probe_reads, as_json=False)
            if not isinstance(html, str):
                item['egw_checks'].append({'url': egw_url, 'status': 'error', 'error': rec.get('error')})
                continue
            parsed = books.parse_listing(html)
            stripped = re.sub(r'<[^>]+>', ' ', html)
            item['egw_checks'].append({
                'url': egw_url,
                'observed_at': rec['observed_at'],
                'sha256': rec['sha256'],
                'archive': rec['archive'],
                'parsed_readings': parsed,
                'placeholder_1_8': '1.8 Make a bet 1.8' in stripped,
            })

        gap_reports.append(item)

    summary = {
        'session': '071642e7',
        'probed_at': iso(datetime.now(timezone.utc)),
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'coverage': snapshot.get('coverage'),
        'counts': {
            'total_rows': len(snapshot.get('matches') or []),
            'open_rows': len(open_rows),
            'open_with_pick': sum(bool(m.get('pick')) for m in open_rows),
            'open_with_probability': sum(m.get('probabilities') is not None for m in open_rows),
            'open_research_only': sum(m.get('probabilities') is None and bool(m.get('pick')) for m in open_rows),
            'open_unresolved_no_pick': sum(not m.get('pick') for m in open_rows),
            'methods': {
                k: sum((m.get('method') or 'none') == k for m in open_rows)
                for k in sorted({m.get('method') or 'none' for m in open_rows})
            },
        },
        'official_vrs_meta': official_meta,
        'official_vrs_error': official_err,
        'mirror_vrs_meta': mirror_meta,
        'mirror_vrs_error': mirror_err,
        'polymarket_total_candidates': len(poly_all),
        'pinnacle_total_candidates': len(pin_all),
        'discovered_stavka_links': discovered_stavka,
        'discovered_egw_links': discovered_egw,
        'open_board': [
            {
                'id': str(m.get('id')),
                'teams': m.get('teams'),
                'competition': m.get('competition'),
                'tier': m.get('tier'),
                'best_of': m.get('best_of'),
                'start': m.get('start'),
                'lock': m.get('lock'),
                'source_url': m.get('source_url'),
                'pick': m.get('pick'),
                'method': m.get('method'),
                'probabilities': m.get('probabilities'),
                'expires_at': m.get('expires_at'),
                'evidence_urls': [e.get('url') for e in (m.get('evidence') or []) if e.get('url')],
                'reason': m.get('reason'),
            }
            for m in open_rows
        ],
        'gap_reports': gap_reports,
        'refresh_source_manifest': refresh_sources,
        'probe_reads': probe_reads,
    }

    (out_dir / 'probe-report.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary['counts'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
