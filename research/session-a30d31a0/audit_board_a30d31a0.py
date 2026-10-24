"""Session a30d31a0: independent row-by-row read of a committed board.

Inputs (all primary data, no pipeline code imported):
  * the board snapshot (default: data/latest.json);
  * research/session-a30d31a0/hotspawn-cs2-pickems-2026-10-24T0657Z.json - the
    open cards read from Hotspawn's cache-busted CS2 pick'ems page;
  * Valve's official standings file at the commit each VRS row cites
    (pass --vrs-file with a local copy read from
    https://github.com/ValveSoftware/counter-strike_regional_standings);
  * research/session-a30d31a0/polymarket-live-2026-10-24.json - live Gamma reads.

The only shared code is the Valve formula in the independent verifier
research/session-0cc1138a/verify_0cc1138a.py (glicko_expect/calibrate).
Writes a Markdown table with one line per open row and the official links a
reviewer needs; prints a summary. Exit status 1 if any check fails.
"""
import argparse
import importlib.util
import json
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def verifier():
    spec = importlib.util.spec_from_file_location('verify_0cc1138a', ROOT / 'research/session-0cc1138a/verify_0cc1138a.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valve_rows(path):
    rows = {}
    for line in Path(path).read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and cells[0].isdigit():
            rows.setdefault(cells[2].casefold(), []).append((int(cells[0]), int(cells[1])))
    return rows


def pct(x):
    return '%.1f%%' % (100 * x)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', default=str(ROOT / 'data/latest.json'))
    parser.add_argument('--lobby', default=str(HERE / 'hotspawn-cs2-pickems-2026-10-24T0657Z.json'))
    parser.add_argument('--live', default=str(HERE / 'polymarket-live-2026-10-24.json'))
    parser.add_argument('--vrs-file', default=None)
    parser.add_argument('--out', default=str(HERE / 'row-audit.md'))
    args = parser.parse_args(argv)
    V = verifier()
    board = json.loads(Path(args.board).read_text())
    lobby = {c['id']: c for c in json.loads(Path(args.lobby).read_text())['open_cards']}
    live = json.loads(Path(args.live).read_text())['markets'] if Path(args.live).exists() else {}
    vrs = valve_rows(args.vrs_file) if args.vrs_file else None
    rows = sorted((m for m in board['matches'] if m['state'] == 'open'), key=lambda m: (m['start'], str(m['id'])))
    failures, lines = [], []
    lines.append('| # | Fixture (Hotspawn) | UTC start | Method | Published | Pick | Independent checks | Official links |')
    lines.append('| - | - | - | - | - | - | - | - |')
    for n, m in enumerate(rows, 1):
        rid = str(m['id'])
        ev = (m.get('evidence') or [{}])[0]
        checks, bad = [], []
        card = lobby.get(rid)
        if card is None:
            bad.append('not on the Hotspawn page read')
        else:
            utc = (datetime.strptime('2026 ' + card['page_time'], '%Y %b %d, %H:%M') + timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:00Z')
            if utc == m['start'] and card['teams'] == m['teams']:
                checks.append('Hotspawn card: same teams, order and start')
            else:
                bad.append('Hotspawn card differs (%s %s)' % (card['teams'], utc))
        probs = m.get('probabilities') or []
        if len(probs) == 2 and m.get('pick') == m['teams'][probs.index(max(probs))] and abs(sum(probs) - 1) < 1e-9:
            checks.append('pick = larger probability, sum 1')
        else:
            bad.append('pick/probabilities inconsistent')
        method = m.get('method')
        links = ['[Hotspawn](%s)' % m['source_url']]
        if method in ('exchange', 'exchange_wide'):
            raw = ev.get('raw') or {}
            gst = str(raw.get('gameStartTime') or '').replace(' ', 'T').replace('+00', 'Z')
            if gst[:16] == m['start'][:16]:
                checks.append('stored Gamma gameStartTime = start')
            else:
                bad.append('stored gameStartTime %r != start' % raw.get('gameStartTime'))
            links.append('[Polymarket](%s)' % ev['url'])
            links.append('[Gamma API](%s)' % ev['api_url'])
            obs = live.get(str(ev.get('id')))
            if obs:
                mid = obs['prices'][0] / sum(obs['prices'])
                labels = obs['outcomes']
                mapped = mid if V.same_team(labels[0], m['teams'][0]) or labels[0] == ev.get('source_teams', [None])[0] else 1 - mid
                drift = 100 * (mapped - probs[0])
                ok = obs['active'] and not obs['closed'] and obs['accepting_orders'] and obs['game_start_utc'][:16] == m['start'][:16]
                (checks if ok else bad).append('live Gamma %s: active moneyline, start %s, mid %s (drift %+.1f pts)' % (
                    obs['read_at'], obs['game_start_utc'][11:16], pct(mapped), drift))
                if (mapped > 0.5) != (probs[0] > 0.5):
                    bad.append('live mid flips the pick')
                if obs.get('description_time_conflict'):
                    checks.append('FLAG: Gamma description says %s' % obs['description_time_conflict'])
        elif method == 'model_vrs':
            links.append('[Valve standings](%s)' % ev['url'])
            raw_e = V.glicko_expect(ev['points'][0], ev['points'][1])
            p = V.calibrate(raw_e)
            if abs(p - probs[0]) < 1e-9:
                checks.append('Valve formula reproduces %s' % pct(p))
            else:
                bad.append('formula gives %.6f' % p)
            if vrs is not None:
                for i, team in enumerate(ev['vrs_teams']):
                    hits = vrs.get(team.casefold(), [])
                    if (ev['standings'][i], ev['points'][i]) in hits:
                        checks.append('%s #%d %d pts in Valve file%s' % (team, ev['standings'][i], ev['points'][i],
                                                                     ' (label listed %dx; roster rule picks this one)' % len(hits) if len(hits) > 1 else ''))
                    else:
                        bad.append('%s rank/points not in Valve file' % team)
        elif method == 'model_vrs_mirror':
            links.append('[HLTV Valve ranking](%s)' % ev['url'])
            raw_e = V.glicko_expect(ev['points'][0], ev['points'][1])
            p = V.calibrate(raw_e)
            (checks if abs(p - probs[0]) < 1e-9 else bad).append('Valve formula on HLTV-mirrored points gives %s (points not re-read: HLTV blocks automated reads here)' % pct(p))
        elif method == 'bookmaker_fallback':
            links.append('[listing](%s)' % ev['url'])
            q = [1 / float(d) for d in ev['decimal_odds']]
            p = q[0] / sum(q)
            (checks if abs(p - probs[0]) < 1e-9 else bad).append('de-vigged odds %s reproduce %s (odds not re-read live)' % (ev['decimal_odds'], pct(p)))
        else:
            bad.append('unknown method %r' % method)
        if bad:
            failures.append((rid, bad))
        lines.append('| %d | %s · `%s` | %s | %s | %s / %s | **%s** | %s | %s |' % (
            n, ' vs '.join(m['teams']), rid, m['start'][5:16].replace('T', ' '), method,
            pct(probs[0]), pct(probs[1]), m.get('pick'),
            '; '.join(checks + ['**FAIL: %s**' % b for b in bad]), ' · '.join(links)))
    Path(args.out).write_text('\n'.join(lines) + '\n')
    print('open rows %d · rows with a failed check %d' % (len(rows), len(failures)))
    for rid, bad in failures:
        print(' ', rid, bad)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
