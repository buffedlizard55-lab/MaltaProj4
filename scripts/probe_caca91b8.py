"""Live coverage & low-tier gap probe for session caca91b8 (read-only research receipt).

Run inside .github/workflows/harvest-caca91b8.yml after scripts.refresh + scripts.quarantine.
Records:
1. Exact coverage breakdown of the refreshed Hotspawn CS2 snapshot.
2. For any open match still missing a win probability or missing a pick, queries public
   trusted CS2 sources (BO3.gg upcoming feed, HLTV search/team pages, Valve VRS standings,
   Stavka/EGW listings) to find any legitimate alias, roster lineup, bookmaker quote, or
   documented coverage limitation — never fabricating or inferring a number.
3. Exact live GitHub Pages manifest state at capture time.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from scripts.core import dt, iso, norm

UA = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'


def _tokens(label: str) -> set[str]:
    cleaned = re.sub(r'[^a-z0-9]+', ' ', (label or '').lower()).split()
    stop = {'team', 'esports', 'gaming', 'club', 'cs2', 'cs', 'the', 'fe', 'academy', 'ac', 'jr'}
    return {t for t in cleaned if len(t) >= 3 and t not in stop} or set(cleaned)


def check_live_pages(session: requests.Session) -> dict:
    base = 'https://buffedlizard55-lab.github.io/MaltaProj4/'
    cb = f'?_cb={int(time.time() * 1000)}'
    out: dict = {'checked_at': iso(datetime.now(timezone.utc)), 'base_url': base}
    try:
        r = session.get(base + 'build-info.json' + cb, timeout=(10, 20))
        out['manifest_http_status'] = r.status_code
        out['manifest_sha256'] = hashlib.sha256(r.content).hexdigest()
        if r.status_code == 200:
            manifest = r.json()
            out['manifest'] = {
                'revision': manifest.get('revision'),
                'built_at': manifest.get('built_at'),
                'snapshot_generated_at': manifest.get('snapshot_generated_at'),
                'rows': manifest.get('rows'),
            }
            snap_ts = manifest.get('snapshot_generated_at')
            if snap_ts:
                age_s = (datetime.now(timezone.utc) - dt(snap_ts)).total_seconds()
                out['snapshot_age_seconds'] = round(age_s, 1)
                out['snapshot_age_hours'] = round(age_s / 3600.0, 3)
                out['within_8h_window'] = age_s <= 8 * 3600
    except Exception as exc:
        out['error'] = str(exc)[:240]
    return out


def fetch_bo3_upcoming(session: requests.Session) -> list[dict]:
    rows: list[dict] = []
    for offset in range(0, 400, 100):
        url = (
            f'https://api.bo3.gg/api/v1/matches?page[offset]={offset}&page[limit]=100'
            '&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1'
            '&sort=start_date&with=teams,tournament'
        )
        try:
            r = session.get(url, timeout=(10, 25))
            if r.status_code != 200:
                break
            payload = r.json()
            batch = payload.get('results') if isinstance(payload, dict) else None
            if not isinstance(batch, list) or not batch:
                break
            rows.extend(batch)
            if len(batch) < 100:
                break
        except Exception:
            break
    return rows


def match_bo3_candidates(match: dict, bo3_rows: list[dict]) -> list[dict]:
    teams = match.get('teams') or []
    if len(teams) != 2:
        return []
    t0_toks, t1_toks = _tokens(teams[0]), _tokens(teams[1])
    m_start = dt(match['start']) if match.get('start') else None
    hits = []
    for row in bo3_rows:
        if not isinstance(row, dict):
            continue
        t1 = (row.get('team1') or {}).get('name') or ''
        t2 = (row.get('team2') or {}).get('name') or ''
        r_start_raw = row.get('start_date')
        try:
            r_start = dt(r_start_raw) if r_start_raw else None
        except Exception:
            r_start = None
        same_window = bool(m_start and r_start and abs((m_start - r_start).total_seconds()) <= 12 * 3600)
        tok1, tok2 = _tokens(t1), _tokens(t2)
        tok_hit = bool((t0_toks & (tok1 | tok2)) or (t1_toks & (tok1 | tok2))
                       or norm(teams[0]) in (norm(t1), norm(t2))
                       or norm(teams[1]) in (norm(t1), norm(t2)))
        if tok_hit or (same_window and abs((m_start - r_start).total_seconds()) <= 1800):
            bet = row.get('bet_updates') or {}
            hits.append({
                'bo3_id': row.get('id'),
                'slug': row.get('slug'),
                'url': f"https://bo3.gg/matches/{row.get('slug')}" if row.get('slug') else None,
                'start_date': r_start_raw,
                'bo_type': row.get('bo_type'),
                'team1': t1,
                'team2': t2,
                'tournament': (row.get('tournament') or {}).get('name'),
                'bet_team_1': bet.get('team_1'),
                'bet_team_2': bet.get('team_2'),
                'token_overlap': tok_hit,
            })
    return hits[:15]


def search_vrs_candidates(teams: list[str]) -> dict:
    vrs_dir = Path('data/vrs')
    files = sorted(vrs_dir.glob('standings_*.md'))
    out: dict = {'file': str(files[-1]) if files else None, 'teams': {}}
    if not files:
        return out
    text = files[-1].read_text(encoding='utf-8', errors='replace')
    lines = [ln.strip() for ln in text.splitlines() if ln.strip().startswith('|')]
    for team in teams:
        toks = _tokens(team)
        n_team = norm(team)
        matches = []
        for ln in lines:
            low = ln.lower()
            if n_team and n_team in norm(ln):
                matches.append(ln)
            elif any(tok in low for tok in toks if len(tok) >= 4):
                matches.append(ln)
        out['teams'][team] = matches[:10]
    return out


def probe_hltv_search(session: requests.Session, team: str) -> list[dict]:
    url = f'https://www.hltv.org/search?query={quote_plus(team)}'
    try:
        time.sleep(2.5)
        r = session.get(url, timeout=(10, 20))
        if r.status_code != 200:
            return [{'url': url, 'http_status': r.status_code}]
        soup = BeautifulSoup(r.text, 'html.parser')
        found = []
        for a in soup.select('a[href^="/team/"]'):
            href = a.get('href') or ''
            label = a.get_text(' ', strip=True)
            if href and label:
                found.append({'label': label, 'url': 'https://www.hltv.org' + href})
        return found[:8]
    except Exception as exc:
        return [{'url': url, 'error': str(exc)[:180]}]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output-dir', default='research/session-caca91b8')
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    snap = json.loads(Path(args.snapshot).read_text(encoding='utf-8'))

    session = requests.Session()
    session.headers['User-Agent'] = UA

    matches = snap.get('matches') or []
    opens = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in opens if m.get('probabilities') is not None]
    research_only = [m for m in opens if m.get('probabilities') is None and m.get('pick')]
    unresolved = [m for m in opens if m.get('probabilities') is None and not m.get('pick')]

    methods: dict[str, int] = {}
    for m in opens:
        key = str(m.get('method') or 'none')
        methods[key] = methods.get(key, 0) + 1

    bo3_rows = fetch_bo3_upcoming(session) if (research_only or unresolved) else []

    gap_details = []
    for m in opens:
        if m.get('probabilities') is not None:
            continue
        teams = m.get('teams') or []
        hltv_hits = {t: probe_hltv_search(session, t) for t in teams}
        gap_details.append({
            'id': m.get('id'),
            'teams': teams,
            'tournament': m.get('tournament'),
            'start': m.get('start'),
            'lock': m.get('lock'),
            'best_of': m.get('best_of'),
            'source_url': m.get('source_url'),
            'pick': m.get('pick'),
            'method': m.get('method'),
            'reason': m.get('reason'),
            'hltv_context': m.get('hltv_context'),
            'hltv_team_pages': m.get('hltv_team_pages'),
            'attempts': m.get('attempts'),
            'bo3_candidates': match_bo3_candidates(m, bo3_rows),
            'vrs_candidates': search_vrs_candidates(teams),
            'hltv_search': hltv_hits,
        })

    open_ledger = [
        {
            'id': m.get('id'),
            'teams': m.get('teams'),
            'tournament': m.get('tournament'),
            'start': m.get('start'),
            'lock': m.get('lock'),
            'pick': m.get('pick'),
            'probabilities': m.get('probabilities'),
            'method': m.get('method'),
            'source_url': m.get('source_url'),
            'evidence_urls': [e.get('url') for e in (m.get('evidence') or []) if e.get('url')],
            'flags': m.get('flags') or [],
        }
        for m in opens
    ]

    report = {
        'session': 'caca91b8',
        'generated_at': snap.get('generated_at'),
        'fixtures_observed_at': snap.get('fixtures_observed_at'),
        'coverage': snap.get('coverage'),
        'counts': {
            'total_feed_rows': len(matches),
            'open_rows': len(opens),
            'not_open_rows': len(matches) - len(opens),
            'open_with_pick': sum(1 for m in opens if m.get('pick')),
            'open_with_probabilities': len(priced),
            'open_research_only_no_pct': len(research_only),
            'open_unresolved_no_pick': len(unresolved),
        },
        'methods': methods,
        'issues': snap.get('issues') or [],
        'live_pages_before_merge': check_live_pages(session),
        'open_ledger': open_ledger,
        'gaps': gap_details,
    }
    (out_dir / 'probe-report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({
        'counts': report['counts'],
        'methods': methods,
        'gaps_probed': len(gap_details),
        'live_pages_within_8h': report['live_pages_before_merge'].get('within_8h_window'),
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
