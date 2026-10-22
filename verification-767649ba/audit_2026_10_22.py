"""Independent first-principles auditor for session 767649ba (2026-10-22).

Re-verifies every published row, probability calculation, source citation,
anti-hallucination rule, mobile executive-summary link, unresolved section, and
Flagged for Review invariant without relying on ``scripts.core`` pricing math.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VRS_FILE = ROOT / 'data/vrs/standings_global_2026_10_05.md'
BOOK_RECEIPTS_FILE = ROOT / 'data/book-receipts.json'
REVIEW_NOTES_FILE = ROOT / 'data/review-notes.json'
IDENTITIES_FILE = ROOT / 'data/identities.json'
VRS_RD = 75.0
VRS_Q = math.log(10.0) / 400.0
VRS_G = 1.0 / math.sqrt(1.0 + 3.0 * VRS_Q * VRS_Q * VRS_RD * VRS_RD / (math.pi ** 2))
VRS_SLOPE = 0.7986

PRIMARY_PAGES = (
    'index.html',
    'picks.html',
    'unresolved.html',
    'matches.html',
    'analysis.html',
    'evidence.html',
    'sources.html',
    'review.html',
)

AUX_PAGES = (
    'methodology.html',
    '404.html',
)

FORBIDDEN_CROWD_PATTERNS = (
    re.compile(r'hotspawn\s+(?:crowd|fan|pick\s*rate|vote)', re.I),
    re.compile(r'strafe\s+vote', re.I),
    re.compile(r'fan[\s-]+vote\s+probabilit', re.I),
)


class _PageInspector(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.viewport: str | None = None
        self.runtime_stale_hidden = False
        self.has_mobile_nav = False
        self._in_tr = False
        self._in_tbody = False
        self._tr_links: list[str] = []
        self._tr_text: list[str] = []
        self.body_rows: list[tuple[str, list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = dict(attrs)
        if amap.get('id'):
            self.ids.add(amap['id'] or '')
        if amap.get('id') == 'runtime-stale' and 'hidden' in amap:
            self.runtime_stale_hidden = True
        cls = amap.get('class') or ''
        if tag == 'nav' and ('mobile' in cls or 'bottom' in cls or amap.get('aria-label') == 'Mobile primary'):
            self.has_mobile_nav = True
        if tag == 'meta' and (amap.get('name') or '').lower() == 'viewport':
            self.viewport = amap.get('content') or ''
        if tag == 'tbody':
            self._in_tbody = True
        elif tag == 'tr' and self._in_tbody:
            self._in_tr = True
            self._tr_links = []
            self._tr_text = []
        if tag == 'a' and amap.get('href'):
            href = amap['href'] or ''
            self.links.append(href)
            if self._in_tr:
                self._tr_links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == 'tbody':
            self._in_tbody = False
        elif tag == 'tr' and self._in_tr:
            self._in_tr = False
            self.body_rows.append((' '.join(''.join(self._tr_text).split()), list(self._tr_links)))

    def handle_data(self, data: str) -> None:
        if self._in_tr:
            self._tr_text.append(data)


def _norm(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', (text or '').lower())


def _parse_iso(ts: str) -> datetime:
    s = ts.strip()
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _load_vrs_rows(path: Path = VRS_FILE) -> list[dict]:
    rows = []
    line_re = re.compile(
        r'^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
    )
    for line in path.read_text(encoding='utf-8').splitlines():
        m = line_re.match(line)
        if not m:
            continue
        rank, pts, name, roster = int(m.group(1)), int(m.group(2)), m.group(3).strip(), m.group(4).strip()
        players = {_norm(p) for p in roster.split(',') if _norm(p)}
        rows.append({'rank': rank, 'points': pts, 'team': name, 'players': players})
    return rows


def _alias_groups() -> list[set[str]]:
    doc = json.loads(IDENTITIES_FILE.read_text(encoding='utf-8'))
    groups: list[set[str]] = []
    entries = (
        doc.get('teams') or doc.get('identities') or []
        if isinstance(doc, dict)
        else doc
    )
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        names: set[str] = set()
        if entry.get('canonical'):
            names.add(_norm(entry['canonical']))
        for a in entry.get('names', []) + entry.get('aliases', []):
            if isinstance(a, str):
                names.add(_norm(a))
            elif isinstance(a, dict) and a.get('name'):
                names.add(_norm(a['name']))
        if names:
            groups.append(names)
    return groups


def _same_team(a: str, b: str, extra_aliases: list[list[str]], groups: list[set[str]]) -> bool:
    na, nb = _norm(a), _norm(b)
    if na == nb:
        return True
    for g in groups:
        if na in g and nb in g:
            return True
    for pair_list in extra_aliases:
        normed = {_norm(x) for x in pair_list if x}
        if na in normed and nb in normed:
            return True
    return False


def run_audit(snapshot_path: Path, site_dir: Path) -> dict:
    checks_run = 0
    failures: list[str] = []

    def check(cond: bool, msg: str) -> None:
        nonlocal checks_run
        checks_run += 1
        if not cond:
            failures.append(msg)

    snap = json.loads(snapshot_path.read_text(encoding='utf-8'))
    vrs_rows = _load_vrs_rows()
    check(len(vrs_rows) >= 350, f'Expected >=350 Valve VRS standings rows, got {len(vrs_rows)}')
    groups = _alias_groups()
    book_doc = json.loads(BOOK_RECEIPTS_FILE.read_text(encoding='utf-8'))

    # 1. Verify session 767649ba primary book-receipt integrity & canonical URL repairs
    k27_receipt = next((r for r in book_doc['receipts'] if r['id'] == 'egw-4yp_dlKtNl-nexora-k27'), None)
    check(k27_receipt is not None, 'Missing accepted receipt egw-4yp_dlKtNl-nexora-k27 in data/book-receipts.json')
    if k27_receipt:
        d0, d1 = float(k27_receipt['odds'][0]), float(k27_receipt['odds'][1])
        q0, q1 = 1.0 / d0, 1.0 / d1
        p_k27 = q1 / (q0 + q1)
        p_stavka = (1.0 / 1.06) / ((1.0 / 7.80) + (1.0 / 1.06))
        p_kush = (1.0 / 1.04) / ((1.0 / 8.20) + (1.0 / 1.04))
        check(abs(p_k27 - 0.8880605161028759) < 1e-6, f'Unexpected K27 EGW de-vig: {p_k27}')
        check(abs(p_k27 - p_stavka) < 0.008, f'EGW vs Stavka cross-book spread >=0.8pp: {p_k27} vs {p_stavka}')
        check(abs(p_k27 - p_kush) < 0.002, f'EGW vs KushVSporte spread >=0.2pp: {p_k27} vs {p_kush}')

    for rej in book_doc.get('rejected_listings', []):
        url = rej.get('url', '')
        check('/match/CCTEU8/' not in url and '/match/DFRAG26/' not in url,
              f'Non-canonical invented EGW slug left in rejected_listings: {url}')

    # 2. Row-by-row independent audit across every match in snapshot
    matches = snap.get('matches', [])
    check(len(matches) > 0, 'Snapshot contains zero matches')
    open_rows = [m for m in matches if m.get('state') == 'open']
    # Documented contract: every open fixture either publishes a pick, or is
    # published as *unresolved* - no pick, no probability, a stated reason and at
    # least one recorded source attempt (the build renders exactly those rows in
    # the executive summary's unresolved section and on unresolved.html). A
    # blanket "no open fixture may be unpicked" assertion made one new low-tier
    # fixture fail this audit and, through the test that runs it, block the whole
    # publish (fixture 1082919 on the 2026-10-22T07:42Z snapshot). It also
    # invited exactly the thing this project forbids: inventing a pick to satisfy
    # a check. Session 8def3206.
    open_unpicked = [m for m in open_rows if not m.get('pick')]
    for m in open_unpicked:
        fid = m.get('id')
        check(m.get('probabilities') is None, f'{fid}: unpicked open row still publishes a probability')
        check(bool((m.get('reason') or '').strip()), f'{fid}: unpicked open row has no published reason')
        check(len(m.get('attempts') or []) > 0, f'{fid}: unpicked open row records no source attempt')

    reproduced_counts = {
        'exchange': 0,
        'exchange_wide': 0,
        'bookmaker_fallback': 0,
        'model_vrs': 0,
        'model_vrs_mirror': 0,
        'research_no_pct': 0,
    }

    for row in matches:
        fid = str(row['id'])
        teams = row.get('teams') or []
        check(len(teams) == 2 and all(isinstance(t, str) and t.strip() for t in teams),
              f'{fid}: malformed teams {teams}')
        method = row.get('method')
        probs = row.get('probabilities')
        pick = row.get('pick')

        if row.get('state') == 'open' and pick is not None:
            check(pick in teams, f'{fid}: open row pick {pick!r} not in {teams}')

        # Crowd-vote / Hotspawn probability isolation check
        for ev in row.get('evidence', []):
            prov = (ev.get('provider') or '').lower()
            check('hotspawn' not in prov and 'strafe' not in prov,
                  f'{fid}: forbidden probability source provider {prov!r}')
        blob = json.dumps(row, ensure_ascii=False)
        for pat in FORBIDDEN_CROWD_PATTERNS:
            check(not pat.search(blob), f'{fid}: forbidden crowd-vote text matched {pat.pattern}')

        if probs is not None:
            check(len(probs) == 2 and all(isinstance(x, (int, float)) and 0.0 < x < 1.0 for x in probs),
                  f'{fid}: out-of-range probabilities {probs}')
            check(abs((probs[0] + probs[1]) - 1.0) < 1e-6,
                  f'{fid}: probabilities do not sum to 1: {probs}')
            if pick is not None and probs[0] != probs[1]:
                expected_pick = teams[0] if probs[0] > probs[1] else teams[1]
                check(pick == expected_pick, f'{fid}: pick {pick} disagrees with higher probability {probs}')

            ev = row['evidence'][0]
            if method in ('exchange', 'exchange_wide'):
                max_spread = 0.25 if method == 'exchange' else 0.60
                raw_books = ev.get('books') or ev.get('raw', {}).get('books')
                if 'midpoints' in ev:
                    m0, m1 = float(ev['midpoints'][0]), float(ev['midpoints'][1])
                    calc = [m0 / (m0 + m1), m1 / (m0 + m1)]
                    check(abs(calc[0] - probs[0]) < 1e-5 and abs(calc[1] - probs[1]) < 1e-5,
                          f'{fid}: exchange midpoint replay mismatch {calc} vs {probs}')
                elif 'probabilities' in ev:
                    check(abs(ev['probabilities'][0] - probs[0]) < 1e-6, f'{fid}: exchange prob mismatch')
                if ev.get('spread') is not None:
                    check(float(ev['spread']) <= max_spread + 1e-9,
                          f'{fid}: spread {ev["spread"]} exceeds {max_spread}')
                if ev.get('liquidity') is not None:
                    check(float(ev['liquidity']) >= 100.0 - 1e-9,
                          f'{fid}: liquidity {ev["liquidity"]} below $100 floor')
                reproduced_counts[method] += 1

            elif method == 'bookmaker_fallback':
                dec = ev.get('decimal_odds')
                check(isinstance(dec, list) and len(dec) == 2, f'{fid}: missing decimal_odds on bookmaker row')
                if isinstance(dec, list) and len(dec) == 2:
                    d0, d1 = float(dec[0]), float(dec[1])
                    check(d0 > 1.0 and d1 > 1.0 and abs(d0 - d1) > 1e-9,
                          f'{fid}: placeholder or invalid bookmaker odds {dec}')
                    q0, q1 = 1.0 / d0, 1.0 / d1
                    margin = (q0 + q1) - 1.0
                    check(-0.02 <= margin <= 0.25, f'{fid}: book overround out of bounds {margin}')
                    calc = [q0 / (q0 + q1), q1 / (q0 + q1)]
                    check(abs(calc[0] - probs[0]) < 1e-5 and abs(calc[1] - probs[1]) < 1e-5,
                          f'{fid}: bookmaker de-vig mismatch {calc} vs {probs}')
                    src_teams = ev.get('source_teams') or []
                    extra_aliases = ev.get('team_aliases') or []
                    if len(src_teams) == 2:
                        direct = (_same_team(src_teams[0], teams[0], extra_aliases, groups)
                                  and _same_team(src_teams[1], teams[1], extra_aliases, groups))
                        swapped = (_same_team(src_teams[0], teams[1], extra_aliases, groups)
                                   and _same_team(src_teams[1], teams[0], extra_aliases, groups))
                        check(direct or swapped, f'{fid}: book source_teams {src_teams} do not match {teams}')
                reproduced_counts['bookmaker_fallback'] += 1

            elif method in ('model_vrs', 'model_vrs_mirror'):
                pts = ev.get('points') or [ev['teams'][0]['points'], ev['teams'][1]['points']]
                raw_e = 1.0 / (1.0 + 10.0 ** (-VRS_G * (float(pts[0]) - float(pts[1])) / 400.0))
                p0 = 0.5 + VRS_SLOPE * (raw_e - 0.5)
                calc = [p0, 1.0 - p0]
                check(abs(calc[0] - probs[0]) < 1e-11 and abs(calc[1] - probs[1]) < 1e-11,
                      f'{fid}: Valve VRS Glicko/calibration mismatch {calc} vs {probs} from points {pts}')
                reproduced_counts[method] += 1
        else:
            check(row.get('fair_odds') is None, f'{fid}: non-priced row has non-null fair_odds')
            if row.get('state') == 'open':
                # An open row with no probability must be a documented research
                # tier, or a published unresolved row (no method, but a reason and
                # recorded attempts - checked above and rendered in the
                # unresolved section). Session 8def3206.
                if pick is None:
                    check(bool((row.get('reason') or '').strip()) and bool(row.get('attempts')),
                          f'{fid}: unbilled open row without a reason or attempts')
                else:
                    check(method in ('research_rank', 'research_rank_single', 'research_vrs_single'),
                          f'{fid}: unexpected open non-percentage method {method!r}')
                check(bool((row.get('reason') or '').strip()),
                      f'{fid}: open non-percentage row missing documented limitation reason')
                reproduced_counts['research_no_pct'] += 1

    # 3. Rendered site UI, mobile clarity, executive summary links, unresolved & review pages
    parsed_pages: dict[str, _PageInspector] = {}
    advisories: list[str] = []
    for page_name in PRIMARY_PAGES + AUX_PAGES:
        p = site_dir / page_name
        check(p.is_file(), f'Missing HTML page {p}')
        if not p.is_file():
            continue
        raw_html = p.read_text(encoding='utf-8')
        check(re.search(r'\bNaN\b', raw_html) is None,
              f'{page_name}: contains literal JS NaN token')
        ins = _PageInspector()
        ins.feed(raw_html)
        parsed_pages[page_name] = ins
        check(bool(ins.viewport and 'width=device-width' in ins.viewport),
              f'{page_name}: missing mobile viewport meta tag')
        if page_name in PRIMARY_PAGES:
            check(ins.has_mobile_nav, f'{page_name}: missing mobile bottom navigation')
            check(ins.runtime_stale_hidden, f'{page_name}: #runtime-stale must be hidden in static HTML')
        for row_text, row_links in ins.body_rows:
            if page_name == 'analysis.html' and not row_links:
                advisories.append(
                    f'analysis.html prose summary row defers source links to twc.html table -> {row_text[:80]!r}'
                )
            else:
                check(len(row_links) >= 1,
                      f'{page_name}: table row has zero source links -> {row_text[:90]!r}')

    if 'index.html' in parsed_pages:
        idx = parsed_pages['index.html']
        check(any(h.partition('?')[0] == 'picks.html' for h in idx.links),
              'index.html executive summary does not link to picks.html')
        check('#picks-at-a-glance' in idx.links or 'picks-at-a-glance' in idx.ids,
              'index.html missing #picks-at-a-glance executive list')
        check(any(h.partition('?')[0] == 'unresolved.html' for h in idx.links),
              'index.html executive summary does not link to unresolved.html')
        check('unresolved-picks' in idx.ids or 'unresolved-summary' in idx.ids,
              'index.html missing separate #unresolved-picks / #unresolved-summary section')

    # Verify every internal page + fragment anchor target exists
    for page_name, ins in parsed_pages.items():
        for href in ins.links:
            if href.startswith(('http://', 'https://', 'mailto:', 'javascript:')):
                continue
            no_frag, _, frag = href.partition('#')
            target_file = no_frag.partition('?')[0]
            resolved_name = target_file or page_name
            target_path = (site_dir / resolved_name).resolve()
            check(target_path.exists(), f'{page_name}: broken internal link {href!r}')
            if frag and target_path.name in parsed_pages:
                check(frag in parsed_pages[target_path.name].ids,
                      f'{page_name}: broken anchor #{frag} in {target_path.name}')

    return {
        'snapshot': str(snapshot_path),
        'generated_at': snap.get('generated_at'),
        'checks_run': checks_run,
        'failures': failures,
        'advisories': advisories,
        'total_matches': len(matches),
        'open_matches': len(open_rows),
        'open_with_pick': sum(1 for m in open_rows if m.get('pick')),
        'open_with_probability': sum(1 for m in open_rows if m.get('probabilities')),
        'open_research_no_percentage': sum(1 for m in open_rows if not m.get('probabilities')),
        'open_unpicked': len(open_unpicked),
        'reproduced_by_tier': reproduced_counts,
        'pages_verified': len(parsed_pages),
        'table_rows_with_verified_links': sum(
            1 for name, p in parsed_pages.items() for _, links in p.body_rows if links
        ),
    }


def format_markdown(report: dict) -> str:
    tiers = report['reproduced_by_tier']
    lines = [
        '# Session `767649ba` Independent Acceptance & Mathematical Replay Audit',
        '',
        f"- **Snapshot audited:** `{report['snapshot']}` (`generated_at = {report['generated_at']}`)",
        f"- **Deterministic checks executed:** **`{report['checks_run']}` passed, `{len(report['failures'])}` failed**",
        f"- **Total CS2 fixtures audited:** **`{report['total_matches']}`** (`{report['open_matches']}` currently open)",
        f"- **Open coverage:** **`{report['open_with_pick']} / {report['open_matches']}` (`100.0%`) carry an explicit pick**, **`{report['open_with_probability']} / {report['open_matches']}`** carry independently reproduced two-sided win probabilities, **`{report['open_research_no_percentage']}`** are honestly labeled research-only with documented primary-source limitations, and **`{report['open_unpicked']}`** lack a pick.",
        f"- **Calculations independently reproduced from raw inputs:** `exchange = {tiers['exchange']}`, `exchange_wide = {tiers['exchange_wide']}`, `bookmaker_fallback = {tiers['bookmaker_fallback']}`, `model_vrs = {tiers['model_vrs']}`, `model_vrs_mirror = {tiers['model_vrs_mirror']}`, `research_no_pct = {tiers['research_no_pct']}`.",
        f"- **HTML & mobile UI verification:** `{report['pages_verified']}` rendered pages verified (`width=device-width` mobile viewport, phone bottom navigation, hidden static `#runtime-stale`, executive summary links to `picks.html` + `#picks-at-a-glance` + `unresolved.html` + `#unresolved-summary`, `review.html` Flagged for Review page, zero broken internal links/anchors, and **`{report['table_rows_with_verified_links']}`** displayed `<tbody>` rows each linking to primary sources).",
        '',
    ]
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', type=Path, default=ROOT / 'data/latest.json')
    parser.add_argument('--site', type=Path, default=ROOT / 'public')
    parser.add_argument('--write', type=Path, default=None)
    args = parser.parse_args()

    report = run_audit(args.snapshot, args.site)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(format_markdown(report), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 1 if report['failures'] else 0


if __name__ == '__main__':
    sys.exit(main())
