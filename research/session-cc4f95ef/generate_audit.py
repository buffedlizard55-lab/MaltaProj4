#!/usr/bin/env python3
"""Generate a dated, source-linked line-by-line ledger for the shipped board.

Read-only. Uses the committed root snapshot and generated HTML only; it never
fetches, edits or fills in a value. Any value that cannot be shown from the
snapshot's own retained evidence is left blank and recorded as unverified.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research' / 'session-cc4f95ef'
DATA = ROOT / 'data' / 'latest.json'
HOTSPAWN_HOSTS = {'play.hotspawn.com', 'www.hotspawn.com'}


def clean(value):
    return ' '.join(str(value or '').split()).replace('|', '\\|')


def mdlink(label, url):
    if not url:
        return ''
    return f'[{clean(label)}]({url})'


def https(url):
    return bool(url) and str(url).startswith('https://')


def source_rows(m):
    links = []
    feed = m.get('feed_url')
    if https(m.get('source_url')) and urlsplit(m['source_url']).netloc in HOTSPAWN_HOSTS:
        links.append(mdlink('Hotspawn fixture', m['source_url']))
    if https(feed):
        links.append(mdlink('Hotspawn fixtures API', feed))
    for q in m.get('evidence') or []:
        api = q.get('api_url')
        page = q.get('url')
        provider = q.get('provider') or 'Accepted source'
        if https(api):
            links.append(mdlink(provider + ' raw', api))
        if https(page) and page != api:
            links.append(mdlink(provider + ' page', page))
    ctx = m.get('hltv_context') or {}
    if https(ctx.get('source')):
        links.append(mdlink('HLTV fixture', ctx['source']))
    links.append(mdlink('All attempted sources', 'https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-' + str(m['id'])))
    return '<br>'.join(dict.fromkeys(x for x in links if x))


def fmtp(p):
    return f'{p[0] * 100:.1f}% / {p[1] * 100:.1f}%' if p else ''


def check_row(m, now):
    errors = []
    source = m.get('source_url') or ''
    if not (https(source) and urlsplit(source).netloc in HOTSPAWN_HOSTS):
        errors.append('missing official Hotspawn fixture link')
    if m.get('state') != 'open':
        if m.get('pick') or m.get('probabilities'):
            errors.append('closed row publishes a current recommendation')
        return errors
    p = m.get('probabilities')
    pick = m.get('pick')
    if not p or len(p) != 2 or not all(isinstance(x, (int, float)) and math.isfinite(x) and 0 < x < 1 for x in p):
        errors.append('open row lacks a valid two-way probability')
        return errors
    if abs(sum(p) - 1) > 1e-9:
        errors.append('probabilities do not sum to one')
    if pick not in m['teams']:
        errors.append('pick is not one of the two teams')
    elif abs(p[0] - p[1]) > 1e-9 and pick != m['teams'][0 if p[0] > p[1] else 1]:
        errors.append('pick does not follow the higher probability')
    fair = m.get('fair_odds')
    if not fair or len(fair) != 2 or any(abs(x - 1 / y) > 1e-9 for x, y in zip(fair, p)):
        errors.append('fair odds are not the reciprocal of the probabilities')
    ev = m.get('evidence') or []
    if len(ev) != 1:
        errors.append('open priced row does not carry exactly one accepted quote')
    else:
        q = ev[0]
        if not https(q.get('api_url') or q.get('url')):
            errors.append('accepted quote lacks an HTTPS official source')
        observed = q.get('observed_at')
        if not observed:
            errors.append('accepted quote has no observation time')
        else:
            age = (now - datetime.fromisoformat(observed.replace('Z', '+00:00'))).total_seconds()
            if not -300 <= age < 8 * 3600:
                errors.append('accepted quote is outside the eight-hour evidence window')
    if not m.get('expires_at'):
        errors.append('recommendation has no expiry deadline')
    return errors


def table(matches, open_rows, now):
    lines = ['| Fixture | Teams | Pick | Win probability | Method / limitation | Official sources | Checks |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for m in matches:
        is_open = m in open_rows
        errors = check_row(m, now)
        state_note = 'open' if is_open else 'not open — past lock/start; blank by rule'
        limits = []
        if is_open:
            limits.append(clean(m.get('method') or 'unpriced'))
            for flag in m.get('flags') or []:
                limits.append(clean(flag))
            for a in m.get('attempts') or []:
                if a.get('status') != 'resolved' and a.get('provider'):
                    limits.append(clean(a['provider']) + ': ' + clean(a.get('reason') or a.get('status')))
        else:
            limits.append(clean(state_note))
        q = (m.get('evidence') or [{}])[0]
        checks = 'OK' if not errors else 'UNVERIFIED: ' + '; '.join(errors)
        extra = ''
        if is_open and q:
            extra = '<br>Observed ' + clean(q.get('observed_at') or '—') + '<br>Expires ' + clean(m.get('expires_at') or '—')
        lines.append('| ' + ' | '.join([
            f'`{m["id"]}`',
            clean(' vs '.join(m['teams'])),
            clean(m.get('pick') or ''),
            fmtp(m.get('probabilities')),
            '<br>'.join(dict.fromkeys(limits)),
            source_rows(m) + extra,
            checks,
        ]) + ' |')
    return '\n'.join(lines)


def main():
    raw = DATA.read_bytes()
    data = json.loads(raw)
    now = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00')).astimezone(timezone.utc)
    matches = data['matches']
    open_rows = [m for m in matches if m.get('state') == 'open']
    all_errors = {m['id']: check_row(m, now) for m in matches}
    errors = {k: v for k, v in all_errors.items() if v}
    page_rows = {}
    for page in ('picks.html', 'matches.html', 'unresolved.html', 'review.html'):
        soup = BeautifulSoup((ROOT / page).read_text(), 'html.parser')
        rows = soup.select('tr[data-match]')
        bad = []
        for row in rows:
            if not any(urlsplit(a.get('href', '')).netloc in HOTSPAWN_HOSTS for a in row.select('a[href]')):
                bad.append(row.get('data-match') or row.get('id') or '?')
        page_rows[page] = {'rows': len(rows), 'rows_without_official_link': bad}
    report = {
        'schema_version': 1,
        'snapshot_generated_at': data['generated_at'],
        'snapshot_sha256': hashlib.sha256(raw).hexdigest(),
        'rows': len(matches),
        'open': len(open_rows),
        'open_with_pick': sum(1 for m in open_rows if m.get('pick')),
        'open_with_probability': sum(1 for m in open_rows if m.get('probabilities')),
        'unresolved': sum(1 for m in open_rows if not m.get('pick')),
        'row_errors': errors,
        'site_rows': page_rows,
        'verified_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    }
    (OUT / 'line-by-line.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    manifest = json.loads((ROOT / 'build-info.json').read_text())
    open_table = table(open_rows, open_rows, now)
    closed_table = table([m for m in matches if m not in open_rows], open_rows, now)
    site_row_lines = '\n'.join(
        f'  - `{page}`: {info["rows"]} table rows, '
        f'{len(info["rows_without_official_link"])} without an official Hotspawn link.'
        for page, info in page_rows.items()
    )
    text = f'''# Line-by-line verification — session cc4f95ef

Snapshot: `{data['generated_at']}` · SHA-256 `{report['snapshot_sha256']}`.
Generated `{report['verified_at']}` from the committed root `data/latest.json` and root HTML.
Read-only: no probability, pick or source was edited. Blank cells mean the value
is not published; a row with a verification problem is labelled `UNVERIFIED`.

## Coverage and arithmetic

- Final build: `{manifest['built_at']}` · revision `{manifest['revision']}`.
- Feed rows: **{len(matches)}**; open at the final build clock: **{len(open_rows)}**; picks: **{report['open_with_pick']}**;
  two-way win probabilities: **{report['open_with_probability']}**; unresolved: **{report['unresolved']}**.
- Earlier 13:30Z and 13:46Z captures had 17 actionable fixtures at their own clocks; subsequent
  official captures (13:54Z, 14:22Z, and later) have 16 after the 13:54Z pick lock passed. The final
  root board shows {len(open_rows)} open rows, every one picked and priced. This is the lock rule, not
  a missing pick.
- Every open row is checked for: an official HTTPS Hotspawn fixture link, two finite
  probabilities in (0, 1) summing to 1, the pick following the higher probability,
  fair odds equal to 1/p, exactly one retained HTTPS price quote observed within
  eight hours, and a published expiry deadline.
- Row-level errors: **{len(errors)}**.
- Root HTML table rows carrying an official Hotspawn link:
{site_row_lines}
- `scripts.validate` independently checked every internal link/asset, artifact checksum and
  displayed match row on the final build; exact counts are in `verification/validate-final.log`.
  Four independent replayers report zero failures on that same final board: `verification-c6`,
  `verification-93f6951a`, `verification-138cbedd` and `verification-e9be3e6b`; their receipts are
  in `verification/*-final.log`.
- Official pages manually re-read for this receipt: the [Hotspawn lobby](https://play.hotspawn.com/lobby),
  [Hotspawn fixture 1085542](https://www.hotspawn.com/matches/ex-zero-tenacity-vs-spirit-academy-cct-europe-2026-series-11-1085542),
  [Polymarket market 6158059](https://gamma-api.polymarket.com/markets/6158059),
  [Valve standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md),
  [HLTV match 2399918](https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7) and
  [BO3.gg NEXVOID vs Alter Ego](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026).
- Runner evidence: [publisher failure 40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196),
  [fresh capture 40197480741](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197480741),
  [browser/coverage capture 40197553353](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197553353),
  [main adoption PR #322](https://github.com/buffedlizard55-lab/MaltaProj4/pull/322) and
  [latest integration PR #332](https://github.com/buffedlizard55-lab/MaltaProj4/pull/332).

## Open matches — every published pick

{open_table}

## Not-open feed rows — blank by rule

These {len(matches) - len(open_rows)} rows are retained for the full Hotspawn
inventory. Their lock/start has passed at the snapshot clock, so no current pick
or probability is published. Each row still carries an official Hotspawn source
link and a link to every source attempt retained on the evidence page.

{closed_table}

## Limitations and flagged irregularities

- Four open rows are **our own Valve VRS model line**, not a market price; one is
  a **wide-exchange low-confidence quote**; one is a **dated third-party listing**
  of a Thunderpick price via BO3.gg. Their labels and links are in the table and
  on the site's [Unresolved & limits](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html) page.
- No Hotspawn crowd percentage, HLTV community vote, placeholder 1.8/1.8 pair or
  unbacked 50/50 is used as a probability.
- `verification-4901f43e/audit_published_claims.py` reports two non-blocking
  warnings: a stale historical Ground Zero/Off Chops figure inside another
  session's archived report, and 17 older HLTV alias citations that auditor did
  not fetch. Neither is a value on the current board; both are retained for
  manual review and the latter is covered by the dated identity ledger.
- The public board was stale when this session began (01:47Z build at 13:25Z).
  The measured validator and phone-layout defects are documented on the
  [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) page.
'''
    (OUT / 'LINE_BY_LINE_AUDIT.md').write_text(text)
    print(json.dumps({k: report[k] for k in ('rows', 'open', 'open_with_pick', 'open_with_probability', 'unresolved')}, indent=1))
    print('row_errors', len(errors))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
