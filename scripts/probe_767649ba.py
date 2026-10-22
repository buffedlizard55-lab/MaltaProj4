"""Live GitHub Actions runner harvester & verifier for session 767649ba.

Fetches public primary sources directly from the runner IP, records HTTP status
codes, response lengths, UTC timestamps, and SHA-256 digests, verifies the
refreshed snapshot's coverage across all Hotspawn CS2 fixtures, and writes
compact machine-readable artifacts into ``research/harvest-767649ba/``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)

ENDPOINTS = [
    ('hotspawn_lobby', 'https://play.hotspawn.com/lobby'),
    ('hotspawn_cs2_pickems', 'https://play.hotspawn.com/cs2-pickems'),
    ('hotspawn_fixtures_api', 'https://play.hotspawn.com/api/v2/fixtures?sport_alias=cs2&status=scheduled&tenantId=1'),
    ('polymarket_sports', 'https://gamma-api.polymarket.com/sports'),
    ('pinnacle_cs2_straight', 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight'),
    ('valve_vrs_2026_10_05', 'https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md'),
    ('stavka_nexora_k27_1082769', 'https://stavka.tv/matches/csgo/22-10-2026-nexora-k27'),
    ('stavka_ex_z10_ex_rustec_1079654', 'https://stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec'),
    ('stavka_ex_rustec_saint_sinners_1081150', 'https://stavka.tv/matches/csgo/23-10-2026-ex-rustec-saint-sinners'),
    ('stavka_forze_lfo10_1081149', 'https://stavka.tv/matches/csgo/23-10-2026-forze-reload-lfo-10'),
    ('egw_nexora_k27_1082769', 'https://egamersworld.com/counterstrike/match/4yp_dlKtNl/nexora-vs-k27-U_TH-dVYT'),
    ('egw_morningstar_nexvoid_1081869', 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/morningstar-vs-nexvoid-e_MT2tamL'),
    ('egw_benched_titanflow_1081597', 'https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn'),
    ('egw_flyquest_staqued_1082860', 'https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3'),
    ('hltv_nexora_k27_2399846', 'https://www.hltv.org/matches/2399846/nexora-vs-k27-winline-mpkbk-cis-lan-season-9'),
    ('hltv_benched_titanflow_2399696', 'https://www.hltv.org/matches/2399696/cct-2026-challengers-europe-series-8-lower-bracket-round-3-2-cct-2026-challengers-europe-series-8'),
    ('hltv_flyquest_staqued_2399890', 'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026'),
]


def probe_url(label: str, url: str, timeout: int = 20) -> dict:
    observed_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
            text = raw.decode('utf-8', errors='replace')
            record = {
                'label': label,
                'url': url,
                'observed_at': observed_at,
                'http_status': status,
                'bytes': len(raw),
                'sha256': hashlib.sha256(raw).hexdigest(),
            }
            if 'stavka.tv' in url:
                decimals = re.findall(r'\b[1-9]\d*\.\d{2}\b', text)
                record['decimal_tokens_sample'] = decimals[:12]
            return record
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b''
        return {
            'label': label,
            'url': url,
            'observed_at': observed_at,
            'http_status': exc.code,
            'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest() if body else None,
            'error': str(exc),
        }
    except Exception as exc:
        return {
            'label': label,
            'url': url,
            'observed_at': observed_at,
            'http_status': None,
            'bytes': 0,
            'sha256': None,
            'error': str(exc)[:240],
        }


def summarize_snapshot(snapshot_path: Path) -> dict:
    snap = json.loads(snapshot_path.read_text(encoding='utf-8'))
    matches = snap['matches']
    open_rows = [m for m in matches if m.get('state') == 'open']
    priced_open = [m for m in open_rows if m.get('probabilities')]
    unpriced_open = [m for m in open_rows if not m.get('probabilities')]
    by_method = {}
    for m in open_rows:
        by_method[m['method']] = by_method.get(m['method'], 0) + 1
    k27_row = next((m for m in matches if str(m['id']) == '1082769'), None)
    return {
        'generated_at': snap.get('generated_at'),
        'total_rows': len(matches),
        'open_rows': len(open_rows),
        'open_with_pick': sum(1 for m in open_rows if m.get('pick')),
        'open_with_probability': len(priced_open),
        'open_research_only_no_percentage': len(unpriced_open),
        'open_unpicked': sum(1 for m in open_rows if not m.get('pick')),
        'open_by_method': by_method,
        'fixture_1082769': {
            'teams': k27_row['teams'],
            'pick': k27_row['pick'],
            'method': k27_row['method'],
            'probabilities': k27_row['probabilities'],
            'fair_odds': k27_row['fair_odds'],
        } if k27_row else None,
        'open_no_percentage_ids': [
            {'id': m['id'], 'teams': m['teams'], 'start': m['start'], 'pick': m['pick'], 'method': m['method']}
            for m in unpriced_open
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    probes = [probe_url(label, url) for label, url in ENDPOINTS]
    manifest = {
        'session': '767649ba',
        'harvested_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'probes': probes,
    }
    summary = summarize_snapshot(args.snapshot)

    (args.out / 'probe-manifest.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )
    (args.out / 'coverage-summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
