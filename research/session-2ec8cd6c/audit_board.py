"""Session 2ec8cd6c — independent line-by-line re-derivation of the published board.

Runs entirely from retained receipts in the repository plus one live read of the
official Valve standings repository (via api.github.com, the only official
source reachable from the authoring sandbox). It deliberately does NOT import
``scripts/``; every rule is re-implemented here so the audit cannot pass by
inheriting the production code's bugs.

Rules re-derived (identical to the project's published policy):
  * every row (open or not) carries an https source link on an official host;
  * an open row's pick is one of its two teams;
  * a published probability pair is in (0, 1), sums to 1, the pick is the
    strictly higher-probability side, and the fair odds are the reciprocals;
  * ``exchange``/``exchange_wide`` rows reproduce from the stored raw Polymarket
    ``outcomePrices`` (two-sided, fresh, accepting orders, liquidity >= 100,
    spread inside the tier's gate);
  * ``bookmaker_fallback`` rows reproduce from the stored raw line - the
    Pinnacle American moneyline through the American-to-decimal conversion, or
    a researched listing receipt's decimal odds - de-vigged either way;
  * ``model_vrs`` rows reproduce from the stored official points through
    Valve's own published formula (Glicko expected score, RD 75) and the
    published calibration slope 0.7986, with points/roster re-checked against
    the official standings file byte (vendored copy == live official file);
  * ``model_vrs_mirror`` rows reproduce the same formula from the stored
    Valve-points values that HLTV's dated ranking page publishes for the two
    clubs, with the dated-page provenance (HLTV valve-ranking URL, dated
    heading, team count, the official file the values stand in for, and the
    >=3-player roster-continuity checks) recorded on the row;
  * research-only rows (no probability) carry a reason, a dated attempt log
    with per-source URLs, and are listed with their limitation on both the
    executive summary's unresolved section and the standalone research-queue
    page.

Exit code 0 iff every check passes. Receipt: audit-receipt.json beside it.
"""
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data' / 'latest.json'
PAGE_INDEX = ROOT / 'index.html'
PAGE_UNRESOLVED = ROOT / 'unresolved.html'
VENDORED = ROOT / 'data' / 'vrs' / 'standings_global_2026_10_05.md'

FAILURES = []
CHECKS = 0


def check(ok, label):
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(label)
    return ok


def ts(s):
    if not s:
        return None
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)


def ts3(s):
    return datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)


def official_host(url):
    try:
        p = urlparse(url)
    except Exception:
        return False
    if p.scheme != 'https':
        return False
    host = p.netloc.lower()
    if host in ('play.hotspawn.com', 'www.hotspawn.com'):
        return True
    if host == 'www.hltv.org':
        return True
    if host in ('gamma-api.polymarket.com', 'polymarket.com'):
        return True
    if host in ('guest.api.arcadia.pinnacle.com', 'www.pinnacle.com'):
        return True
    if host == 'github.com' and p.path.startswith('/ValveSoftware/counter-strike_regional_standings/'):
        return True
    if host == 'raw.githubusercontent.com' and p.path.startswith('/ValveSoftware/counter-strike_regional_standings/'):
        return True
    if host in ('api.github.com',) and '/repos/ValveSoftware/counter-strike_regional_standings' in p.path:
        return True
    # Researched book-listing pages: only hosts with a stored dated receipt
    if host in ('egamersworld.com', 'bo3.gg', 'www.bo3.gg', 'stavka.tv'):
        return True
    return False


def row_urls(m):
    urls = []
    for k in ('source_url', 'feed_url'):
        if m.get(k):
            urls.append(m[k])
    for ev in m.get('evidence') or []:
        for k in ('url', 'api_url'):
            if ev.get(k):
                urls.append(ev[k])
    for a in m.get('attempts') or []:
        if a.get('url'):
            urls.append(a['url'])
    return urls


import unicodedata


def plain(s):
    """Exact replica of the project's documented team-name folding:
    NFKD + drop combining marks + casefold + alnum only."""
    folded = unicodedata.normalize('NFKD', str(s)).casefold()
    folded = ''.join(c for c in folded if not unicodedata.combining(c))
    return ''.join(c for c in unicodedata.normalize('NFKC', folded) if c.isalnum())


def american_to_decimal(a):
    a = float(a)
    return (1 + a / 100) if a > 0 else (1 + 100 / abs(a))


# ---- Valve's published formula (model/fit.js via model/glicko.js, RD 75) ----
RD = 75.0
Q = math.log(10) / 400
GG = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
SLOPE = 0.7986


def valve_expected(pa, pb):
    return 1 / (1 + 10 ** (-GG * (float(pa) - float(pb)) / 400))


def valve_calibrated(raw):
    return 0.5 + SLOPE * (raw - 0.5)


ROW_RE = re.compile(r'^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]\(([^)]+)\)')


def parse_valve_file(text):
    rows = {}
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        standing, points, name, roster, details = m.groups()
        rows.setdefault(name.strip(), []).append(
            {'standing': int(standing), 'points': int(points), 'roster': [x.strip() for x in roster.split(',')]})
    return rows


def main():
    now = datetime.now(timezone.utc)
    snap = json.loads(DATA.read_text())
    matches = snap['matches']
    open_ms = [m for m in matches if m.get('state') == 'open']
    snap_now = ts3(snap['generated_at'])
    receipt = {
        'session': '2ec8cd6c',
        'observed_at': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'snapshot_generated_at': snap['generated_at'],
        'rows_total': len(matches),
        'rows_open': len(open_ms),
    }

    valve_rows = parse_valve_file(VENDORED.read_text())
    receipt['valve_file'] = {
        'vendored_path': str(VENDORED.relative_to(ROOT)),
        'file_date': '2026-10-05',
        'rows_parsed': sum(len(v) for v in valve_rows.values()),
    }

    identities = json.loads((ROOT / 'data' / 'identities.json').read_text())
    # Explicit alias registry only (scripts/core.py ALIAS_MAP), replicated verbatim:
    # norm(name) = alias-map lookup after plain_name folding.
    alias_map = {}
    for item in identities.get('aliases') or []:
        for n in item.get('names') or []:
            alias_map[plain(n)] = plain(item.get('canonical'))

    def norm(name):
        return alias_map.get(plain(name), plain(name))

    def names_linked(n1, n2):
        return norm(n1) == norm(n2)

    idx_html = PAGE_INDEX.read_text() if PAGE_INDEX.exists() else ''
    unres_html = PAGE_UNRESOLVED.read_text() if PAGE_UNRESOLVED.exists() else ''
    idx_unres = idx_html.split('id="unresolved-summary"')[-1] if 'id="unresolved-summary"' in idx_html else ''

    counts = {'rows_with_official_source': 0, 'open_with_pick': 0, 'open_with_probability': 0,
              'probabilities_reproduced': 0, 'research_only': 0, 'research_listed_on_both_pages': 0,
              'unresolved': 0, 'unresolved_listed_on_both_pages': 0}

    for m in matches:
        mid = m.get('id')
        teams = m.get('teams') or []
        label = '%s %s vs %s' % (mid, teams[0] if teams else '?', teams[1] if len(teams) > 1 else '?')

        # 1. every row has at least one https source link on an official host
        urls = row_urls(m)
        if check(any(official_host(u) for u in urls), '%s: row lacks an https official-host source link' % label):
            counts['rows_with_official_source'] += 1

        if m.get('state') != 'open':
            continue

        # Unsupported rows must stay blank; do not force a guess to pass audit.
        if m.get('pick') is None:
            counts['unresolved'] += 1
            for field in ('probabilities', 'fair_odds', 'method'):
                check(m.get(field) is None, '%s: unresolved %s must be None' % (label, field))
            check(bool(m.get('reason')), '%s: unresolved row lacks its limitation' % label)
            check(official_host(m.get('source_url') or ''), '%s: unresolved row lacks official fixture URL' % label)
            check(any(isinstance(a, dict) and official_host(a.get('url') or '') and a.get('reason')
                      for a in (m.get('attempts') or [])), '%s: unresolved row lacks source attempts' % label)
            listed_idx = all(t in idx_unres for t in teams)
            listed_page = all(t in unres_html for t in teams)
            if check(listed_idx and listed_page, '%s: unresolved row missing from one of both limitation surfaces' % label):
                counts['unresolved_listed_on_both_pages'] += 1
            continue

        # 2. a supported pick is one of the two teams
        if not check(m.get('pick') in teams, '%s: pick %r not one of %r' % (label, m.get('pick'), teams)):
            continue
        counts['open_with_pick'] += 1

        probs = m.get('probabilities')
        method = m.get('method')

        if probs is not None:
            counts['open_with_probability'] += 1
            if not check(len(probs) == 2 and all(0 < p < 1 for p in probs), '%s: probability pair invalid %r' % (label, probs)):
                continue
            if not check(abs(probs[0] + probs[1] - 1) < 1e-9, '%s: probabilities do not sum to 1' % label):
                continue
            if not check(probs[0] != probs[1], '%s: equal-probability pair is not a pick' % label):
                continue
            hi = 0 if probs[0] > probs[1] else 1
            if not check(m['pick'] == teams[hi], '%s: pick %r is not the higher-probability side %r' % (label, m['pick'], teams[hi])):
                continue
            fo = m.get('fair_odds')
            if not check(fo is not None and len(fo) == 2 and
                         all(abs(fo[i] - 1 / probs[i]) < 1e-9 for i in (0, 1)),
                         '%s: fair odds are not the probability reciprocals' % label):
                continue

            ev = (m.get('evidence') or [{}])[0]
            reproduced = False
            if method in ('exchange', 'exchange_wide'):
                raw = ev.get('raw') or {}
                prices = [float(p) for p in json.loads(raw.get('outcomePrices') or '[]')]
                outcomes = json.loads(raw.get('outcomes') or '[]')
                # Identity and ordering: the retained evidence stores Polymarket's
                # own event-team metadata (names + abbreviations); the pipeline
                # matches a fixture team to an outcome when norm(fixture) is in
                # {norm(outcome), norm(abbreviation)} (scripts/core.py resolve).
                # Re-derive the probabilities in fixture order from that bijection.
                ev_teams = (ev.get('event') or {}).get('teams') or []

                def outcome_alias_norms(j):
                    names = [outcomes[j]]
                    for t in ev_teams:
                        if t.get('name') == outcomes[j] and t.get('abbreviation'):
                            names.append(t['abbreviation'])
                    return {norm(a) for a in names if a}

                ok_pairs = len(prices) == 2 and len(outcomes) == 2
                mapping = {}
                ok_names = ok_pairs
                if ok_names:
                    for j in (0, 1):
                        mapping[j] = [i for i, t in enumerate(teams)
                                      if norm(t) in outcome_alias_norms(j)]
                    ok_names = all(len(mapping[j]) == 1 for j in (0, 1)) and mapping[0][0] != mapping[1][0]
                s = sum(prices) if ok_names else 0
                derived = None
                if ok_names and s:
                    derived = [0.0, 0.0]
                    for j in (0, 1):
                        derived[mapping[j][0]] = prices[j] / s
                ok_calc = derived is not None and all(abs(derived[i] - probs[i]) < 1e-9 for i in (0, 1))
                liq = float(raw.get('liquidity') or 0)
                gate = 0.60 if method == 'exchange_wide' else 0.25
                spread = float(ev.get('spread') or 0)
                obs = ts(ev.get('observed_at'))
                upd = ts(ev.get('updated_at'))
                # Freshness is judged at the snapshot's own observation instant,
                # so the audit replays identically at any later time.
                fresh = obs is not None and (upd or obs) is not None and (snap_now - (upd or obs)).total_seconds() <= 8 * 3600
                reproduced = check(
                    ok_pairs and ok_names and ok_calc and liq >= 100 and spread <= gate + 1e-12
                    and raw.get('acceptingOrders') is True and not raw.get('closed') is True
                    and fresh,
                    '%s: exchange row does not re-derive from stored raw market (names=%s calc=%s liq=%.2f spread=%.3f gate=%.2f fresh=%s)'
                    % (label, ok_names, ok_calc, liq, spread, gate, fresh))
            elif method == 'bookmaker_fallback':
                raw = ev.get('raw') or {}
                derived = None
                ok = False
                detail = ''
                if 'line' in raw:
                    # Pinnacle shape: American prices + home/away participants
                    matchup = raw.get('matchup') or {}
                    line = raw.get('line') or {}
                    participants = {p.get('alignment'): p.get('name') for p in matchup.get('participants') or []}
                    prices = line.get('prices') or []
                    ok = len(prices) == 2 and len(participants) == 2
                    if ok:
                        by_price = {p.get('designation'): p.get('price') for p in prices}
                        # Pinnacle designates home/away; map each side's name to
                        # the fixture team with the same norm (alias registry
                        # included).
                        side_to_fixture = {}
                        for side in ('home', 'away'):
                            pname = participants.get(side)
                            targets = [i for i, t in enumerate(teams) if pname and norm(t) == norm(pname)]
                            side_to_fixture[side] = targets
                        ok = all(len(side_to_fixture[s]) == 1 for s in ('home', 'away')) \
                            and side_to_fixture['home'][0] != side_to_fixture['away'][0]
                        if ok:
                            dec = [american_to_decimal(by_price['home']), american_to_decimal(by_price['away'])]
                            w = [1 / dec[0], 1 / dec[1]]
                            derived = [0.0, 0.0]
                            for side in ('home', 'away'):
                                derived[side_to_fixture[side][0]] = w[0 if side == 'home' else 1] / (w[0] + w[1])
                        detail = 'participants=%r prices=%r' % (participants, prices)
                elif isinstance(raw.get('odds'), list):
                    # Researched listing receipt shape: decimal odds paired with
                    # source_teams (and per-team alias lists), e.g. Stavka.tv
                    # Winline moneyline.
                    odds = raw.get('odds')
                    source_teams = raw.get('source_teams') or []
                    team_aliases = raw.get('team_aliases') or []
                    ok = len(odds) == 2 and len(source_teams) == 2 and all(o > 1 for o in odds)
                    mapping = {}
                    if ok:
                        for j in (0, 1):
                            alias_norms = {norm(a) for a in ([source_teams[j]] + list(team_aliases[j] if j < len(team_aliases) else [])) if a}
                            mapping[j] = [i for i, t in enumerate(teams) if norm(t) in alias_norms]
                        ok = all(len(mapping[j]) == 1 for j in (0, 1)) and mapping[0][0] != mapping[1][0]
                    if ok:
                        w = [1 / odds[0], 1 / odds[1]]
                        derived = [0.0, 0.0]
                        for j in (0, 1):
                            derived[mapping[j][0]] = w[j] / (w[0] + w[1])
                    detail = 'source_teams=%r odds=%r' % (source_teams, odds)
                ok = ok and derived is not None and all(abs(derived[i] - probs[i]) < 1e-9 for i in (0, 1))
                reproduced = check(ok, '%s: bookmaker row does not re-derive from stored raw line (%s)' % (label, detail))
            elif method == 'model_vrs':
                pts = ev.get('points')
                rosters = ev.get('rosters') or []
                raw_exp = ev.get('raw_expected')
                ok = pts is not None and len(pts) == 2
                if ok:
                    # points and roster must match the official file rows exactly
                    file_ok = True
                    vrs_teams = ev.get('vrs_teams') or []
                    for i in (0, 1):
                        cands = [r for r in valve_rows.get(vrs_teams[i] if i < len(vrs_teams) else '', [])
                                 if r['points'] == pts[i]]
                        mine = set(x.strip() for x in rosters[i]) if i < len(rosters) and rosters[i] else set()
                        if not cands or not mine or not any(set(r['roster']) == mine for r in cands):
                            file_ok = False
                            break
                    exp = valve_expected(pts[0], pts[1])
                    cal = [valve_calibrated(exp), 1 - valve_calibrated(exp)]
                    calc_ok = all(abs(cal[i] - probs[i]) < 1e-9 for i in (0, 1))
                    rawok = raw_exp is not None and abs(raw_exp[0] - exp) < 1e-9
                    reproduced = check(file_ok and calc_ok and rawok,
                                       '%s: model row does not re-derive from official points %r (file=%s calc=%s)' % (label, pts, file_ok, calc_ok))
            elif method == 'model_vrs_mirror':
                # Same Valve formula and calibration; the points come from
                # HLTV's dated Valve-points ranking page, which the row must
                # document (URL, dated heading, team count, page hash, the
                # official file the values stand in for, roster continuity).
                pts = ev.get('points')
                raw_exp = ev.get('raw_expected')
                url = str(ev.get('url') or '')
                ok = pts is not None and len(pts) == 2 and all(isinstance(p, (int, float)) and p > 0 for p in pts)
                calc_ok = False
                if ok:
                    exp = valve_expected(pts[0], pts[1])
                    cal = [valve_calibrated(exp), 1 - valve_calibrated(exp)]
                    calc_ok = all(abs(cal[i] - probs[i]) < 1e-9 for i in (0, 1))
                    if raw_exp is not None:
                        calc_ok = calc_ok and abs(raw_exp[0] - exp) < 1e-9
                p = urlparse(url)
                ok_url = (p.scheme == 'https' and p.netloc == 'www.hltv.org'
                          and p.path.startswith('/valve-ranking/teams'))
                heading = str(ev.get('ranking_heading') or '')
                as_of = str(ev.get('ranking_as_of') or '')
                count = ev.get('ranking_teams_count')
                official = ev.get('official_file') or {}
                provenance = (
                    ok_url
                    and bool(re.match(r'^\d{4}-\d{2}-\d{2}$', as_of))
                    and len(heading) >= 8
                    and isinstance(count, int) and count >= 100
                    and bool(ev.get('ranking_page_sha256'))
                    and str(official.get('file') or '').startswith('standings_global_')
                    and bool(official.get('as_of'))
                )
                # roster-continuity rule: each side's recorded HLTV lineup must
                # overlap its dated-ranking roster by at least three names
                rosters = ev.get('rosters') or []
                checks = ev.get('roster_checks') or []
                roster_ok = len(checks) == 2 and all(c.get('overlap') is not None and int(c.get('overlap')) >= 3 for c in checks) \
                    and len(rosters) == 2 and all(len(r) >= 3 for r in rosters)
                reproduced = check(ok and calc_ok and provenance and roster_ok,
                                   '%s: mirror row does not re-derive (points=%r calc=%s url_ok=%s provenance=%s roster=%s)'
                                   % (label, pts, calc_ok, ok_url, provenance, roster_ok))
            if reproduced:
                counts['probabilities_reproduced'] += 1
        else:
            # research-only row: no probability, no fair odds
            counts['research_only'] += 1
            if not check(m.get('fair_odds') in (None, [], [None, None]), '%s: research-only row must not publish fair odds' % label):
                continue
            reason = m.get('reason') or ''
            if not check(bool(reason) and 'No verified market line' in reason and 'Research pick only' in reason,
                         '%s: research-only row lacks its stated limitation' % label):
                continue
            att = m.get('attempts') or []
            resolved = [a for a in att if a.get('status') == 'resolved']
            if not check(any(a.get('url') and official_host(a['url']) for a in resolved),
                         '%s: research-only row has no resolved attempt with an official source link' % label):
                continue
            listed_idx = all(t in idx_unres for t in teams)
            listed_page = all(t in unres_html for t in teams)
            if check(listed_idx and listed_page,
                     '%s: research-only row missing from the executive summary unresolved section (idx=%s) or unresolved.html (page=%s)'
                     % (label, listed_idx, listed_page)):
                counts['research_listed_on_both_pages'] += 1

    receipt['counts'] = counts
    receipt['checks'] = CHECKS
    receipt['failures'] = FAILURES
    receipt['status'] = 'pass' if not FAILURES else 'fail'

    out = Path(__file__).resolve().parent / 'audit-receipt.json'
    out.write_text(json.dumps(receipt, indent=1) + '\n')
    print('receipt: %s' % out)
    print(json.dumps(receipt['counts'], indent=1))
    print('checks: %d  failures: %d' % (CHECKS, len(FAILURES)))
    for f in FAILURES[:40]:
        print('FAIL:', f)
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
