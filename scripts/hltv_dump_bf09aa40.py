"""Replay the collector's own HLTV list reads from the bytes it archived.

Why this exists
---------------
``scripts.refresh`` archives every source body it reads (``runtime/sources/<sha256>.html``)
and records each read — name, URL, HTTP status, observation time and SHA-256 — in
the snapshot's ``source_checks``. When a fixture ends a run with no HLTV identity,
the only honest question is *what did HLTV actually list*, and that answer is
already on disk. This script re-runs ``scripts.hltv.discover`` over those exact
archived bytes and writes:

* every parsed candidate (team labels, exact UTC start, HLTV URL) per list read;
* for each open fixture that collected no HLTV identity, the candidates sharing a
  team label at any start, the candidates at its exact start, and a verbatim
  text search for each of its team labels in the raw page (with surrounding
  context) so a label HLTV spells differently, or markup this parser does not
  read, is visible instead of assumed.

Read-only, offline, no network: it never fetches anything, never edits a row and
never produces a probability. Run it in the research workflow after the refresh.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts.core import dt, iso, norm
from scripts.hltv import discover

CONTEXT = 220


def candidates_from(path):
    body = Path(path).read_text(encoding='utf-8', errors='replace')
    try:
        return discover(body), body
    except ValueError as exc:
        return None, body, str(exc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--sources', default='runtime/sources')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    snapshot = json.loads(Path(args.snapshot).read_text())
    sources = Path(args.sources)
    report = {'snapshot_generated_at': snapshot.get('generated_at'), 'reads': [], 'gaps': []}

    list_reads = [c for c in (snapshot.get('source_checks') or [])
                  if str(c.get('name') or '').startswith(('HLTV fallback discovery', 'HLTV matches '))]
    parsed = {}
    for read in list_reads:
        entry = {'name': read.get('name'), 'url': read.get('url'), 'status': read.get('status'),
                 'http_status': read.get('http_status'), 'observed_at': read.get('observed_at'),
                 'sha256': read.get('sha256')}
        path = sources / ('%s.html' % read.get('sha256'))
        if not path.exists():
            entry.update(archived=False)
            report['reads'].append(entry)
            continue
        found = candidates_from(path)
        if len(found) == 3:
            entry.update(archived=True, parsed=False, parse_error=found[2])
            report['reads'].append(entry)
            continue
        candidates, body = found
        entry.update(archived=True, parsed=True, candidates=len(candidates))
        parsed[read.get('url')] = (candidates, body)
        report['reads'].append(entry)

    for row in snapshot.get('matches') or []:
        if row.get('state') != 'open' or (row.get('hltv_context') or {}).get('source'):
            continue
        wanted = [row['teams'][0], row['teams'][1]]
        gap = {'id': row['id'], 'teams': wanted, 'start': row.get('start'),
               'competition': row.get('competition'), 'sharing_a_label': [], 'at_that_start': [],
               'raw_text_hits': []}
        for url, (candidates, body) in parsed.items():
            for c in candidates:
                if {norm(t) for t in c['teams']} & {norm(t) for t in wanted}:
                    gap['sharing_a_label'].append({'list': url, **c})
                if c['start'] == row.get('start'):
                    gap['at_that_start'].append({'list': url, 'teams': c['teams'], 'url': c['url']})
            text = re.sub(r'<[^>]+>', ' ', body)
            text = re.sub(r'\s+', ' ', text)
            for label in wanted:
                for match in list(re.finditer(re.escape(label), text, re.I))[:3]:
                    gap['raw_text_hits'].append({
                        'list': url, 'label': label,
                        'context': text[max(0, match.start() - CONTEXT):match.end() + CONTEXT]})
        report['gaps'].append(gap)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print('list reads: %d (parsed %d)' % (len(report['reads']),
                                          sum(1 for r in report['reads'] if r.get('parsed'))))
    for gap in report['gaps']:
        print('%s %s: sharing=%d at_start=%d raw_hits=%d' % (
            gap['id'], ' vs '.join(gap['teams']), len(gap['sharing_a_label']),
            len(gap['at_that_start']), len(gap['raw_text_hits'])))


if __name__ == '__main__':
    main()
