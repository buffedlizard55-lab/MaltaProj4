"""Line-by-line verification of one board snapshot, as a reviewable table.

For every open match the report prints, on one row: both team labels, both
probabilities, the pick, how the pick was derived, and the exact official
source link(s) a reviewer can open. It then re-derives every check that does not
need the network and marks each row PASS/FAIL, so a value that cannot be
confirmed is visible as such instead of being filled in.

Checks per priced row (all re-derived from the row's own stored evidence):
  P1  two probabilities, each strictly between 0 and 1
  P2  the pair sums to 1 within 1e-9
  P3  fair odds are the reciprocal of the probabilities within 1e-9
  P4  the pick is the higher-probability side (and blank when level)
  P5  at least one https source link is present on the row
  P6  the fixture page is an official Hotspawn URL
  P7  the method is one of the published ladder labels
  P8  the row is still open at the snapshot instant and not locked

Rows that carry a pick with no probability are reported separately, with the
method and the reason, and are never given a number here.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

METHODS = {'exchange', 'exchange_wide', 'bookmaker_fallback', 'model_vrs', 'model_vrs_mirror',
           'research_vrs_single', 'research_rank', 'research_rank_single', 'research_form',
           'book_listing', 'bookmaker'}


def parse(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


def money(p):
    return '%.1f%%' % (p * 100)


def row_checks(m, captured):
    """The eight published checks for one priced open row, re-derived from the row."""
    a, b = m['probabilities']
    checks = {}
    checks['P1'] = 0 < a < 1 and 0 < b < 1
    checks['P2'] = abs((a + b) - 1) <= 1e-9
    odds = m.get('fair_odds') or []
    checks['P3'] = len(odds) == 2 and all(abs(p - 1 / o) <= 1e-9 for p, o in zip((a, b), odds))
    expected = None if abs(a - b) < 1e-9 else m['teams'][1 if b > a else 0]
    checks['P4'] = m.get('pick') == expected
    checks['P5'] = any(str((q or {}).get(k) or '').startswith('https://')
                       for q in (m.get('evidence') or []) for k in ('api_url', 'url'))
    host = urlsplit(m.get('source_url') or '').hostname
    checks['P6'] = host in ('play.hotspawn.com', 'www.hotspawn.com', 'hotspawn.com')
    checks['P7'] = m.get('method') in METHODS
    try:
        checks['P8'] = parse(m['lock']) > captured and parse(m['start']) > captured
    except (TypeError, ValueError, KeyError):
        checks['P8'] = False
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot')
    ap.add_argument('--output', default=None)
    ap.add_argument('--raw', default=None, help='write the row checks as JSON here')
    args = ap.parse_args()
    data = json.loads(Path(args.snapshot).read_text())
    captured = parse(data['generated_at'])
    matches = data['matches']
    open_rows = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    pick_only = [m for m in open_rows if m.get('pick') and m.get('probabilities') is None]
    nowhere = [m for m in open_rows if not m.get('pick')]

    lines, raw = [], []
    lines.append('# Line-by-line verification of one board snapshot')
    lines.append('')
    lines.append('| Fact | Value |')
    lines.append('| --- | --- |')
    lines.append('| Snapshot generated | `%s` |' % data.get('generated_at'))
    lines.append('| Fixtures observed | `%s` |' % data.get('fixtures_observed_at'))
    lines.append('| Coverage | `%s` |' % data.get('coverage'))
    lines.append('| Feed rows | %d |' % len(matches))
    lines.append('| Open at the snapshot instant | %d |' % len(open_rows))
    lines.append('| Open with a pick | %d |' % (len(priced) + len(pick_only)))
    lines.append('| Open with a win probability | %d |' % len(priced))
    lines.append('| Open, pick with no percentage (research tier) | %d |' % len(pick_only))
    lines.append('| Open, unresolved | %d |' % len(nowhere))
    lines.append('')

    lines.append('## Every priced open match, re-derived')
    lines.append('')
    lines.append('| Fixture | Teams | A % | B % | Pick | Method | Sum | Fair odds | Checks | Source |')
    lines.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for m in sorted(priced, key=lambda r: (str(r.get('start')), str(r.get('id')))):
        a, b = m['probabilities']
        checks = row_checks(m, captured)
        odds = m.get('fair_odds') or []
        failed = [k for k, ok in checks.items() if not ok]
        quote = (m.get('evidence') or [{}])[0]
        source = quote.get('api_url') or quote.get('url') or ''
        lines.append('| [%s](%s) | %s vs %s | %s | %s | **%s** | `%s` | %s | %s / %s | %s | [evidence](%s) |' % (
            m['id'], m.get('source_url') or '', m['teams'][0], m['teams'][1], money(a), money(b),
            m.get('pick') or '—', m.get('method'), '%.12g' % (a + b),
            '%.2f' % odds[0] if len(odds) == 2 else '—', '%.2f' % odds[1] if len(odds) == 2 else '—',
            'PASS' if not failed else 'FAIL ' + ','.join(failed), source))
        raw.append({'id': m['id'], 'teams': m['teams'], 'probabilities': m['probabilities'],
                    'pick': m.get('pick'), 'method': m.get('method'),
                    'checks': checks, 'failed': failed, 'source_url': m.get('source_url'),
                    'quote_url': source, 'quote_provider': quote.get('provider')})

    lines.append('')
    lines.append('## Open matches with a pick but no percentage (research tiers)')
    lines.append('')
    if pick_only:
        lines.append('| Fixture | Teams | Pick | Method | Why there is no percentage | Source |')
        lines.append('| --- | --- | --- | --- | --- | --- |')
        for m in pick_only:
            lines.append('| [%s](%s) | %s vs %s | **%s** | `%s` | %s | %s |' % (
                m['id'], m.get('source_url') or '', m['teams'][0], m['teams'][1], m['pick'],
                m.get('method'), (m.get('reason') or '').replace('|', '\\|')[:400],
                (m.get('hltv_context') or {}).get('source') or (m.get('source_url') or '')))
    else:
        lines.append('None in this snapshot.')

    lines.append('')
    lines.append('## Open matches with no pick (unresolved), and why')
    lines.append('')
    if nowhere:
        lines.append('Every row below is listed with the sources that were tried and the gate each one failed. '
                     'A blank percentage here means unverified, never 50/50.')
        lines.append('')
        lines.append('| Fixture | Teams | Start (UTC) | Sources tried | Last reason |')
        lines.append('| --- | --- | --- | --- | --- |')
        for m in nowhere:
            tried = sorted({str((a or {}).get('provider')) for a in (m.get('attempts') or [])})
            lines.append('| [%s](%s) | %s vs %s | %s | %s | %s |' % (
                m['id'], m.get('source_url') or '', m['teams'][0], m['teams'][1], m.get('start'),
                ', '.join(tried) or 'none recorded',
                (m.get('reason') or '').replace('|', '\\|')[:400]))
    else:
        lines.append('None in this snapshot: every open match carries a pick and a percentage or a labelled '
                     'research pick.')

    total = len(priced)
    passed = sum(1 for r in raw if not r['failed'])
    lines.append('')
    lines.append('## Result')
    lines.append('')
    lines.append('%d of %d priced rows pass every re-derived check; %d fail. '
                 'A row is never marked verified unless every check on it passes.' % (passed, total, total - passed))
    text = '\n'.join(lines) + '\n'
    if args.output:
        Path(args.output).write_text(text, encoding='utf-8')
    if args.raw:
        Path(args.raw).write_text(json.dumps(raw, indent=1), encoding='utf-8')
    print(text)
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
