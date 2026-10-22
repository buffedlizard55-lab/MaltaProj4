"""Retain a dated, replayable, non-publishing source audit on this session branch.

No pick or input is invented here. The real collector and independent arithmetic
review run first; this script archives their exact response bytes and reports
coverage at the observation clock separately from coverage at the audit clock.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import iso
from scripts.coverage_contract import inspect
from scripts.probe_ac4743a3 import evidence_index, verify_primary_inventory, coverage


def capture(snapshot_path, output, source_dir='runtime/sources'):
    snapshot = json.loads(Path(snapshot_path).read_text())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'snapshot.json').write_text(json.dumps(snapshot, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    index = evidence_index(snapshot, source_dir, output / 'raw')
    (output / 'evidence-index.json').write_text(json.dumps(index, indent=2) + '\n')
    fixture = next((r for r in index if r.get('name') == 'Hotspawn CS2 fixtures' and r.get('archive')), None)
    if fixture:
        parity = verify_primary_inventory(snapshot, gzip.decompress((output / fixture['archive']).read_bytes()))
        parity.update(official_source=fixture['url'], source_sha256=fixture['sha256'])
        (output / 'primary-inventory-audit.json').write_text(json.dumps(parity, indent=2) + '\n')
    report = {
        'session': 'eaff7cce', 'run_id': os.getenv('GITHUB_RUN_ID'),
        'revision': os.getenv('GITHUB_SHA'), 'audited_at': iso(datetime.now(timezone.utc)),
        'snapshot_generated_at': snapshot['generated_at'], 'inventory_coverage': snapshot['coverage'],
        'snapshot_counts': coverage(snapshot),
        'at_snapshot_clock': inspect(snapshot, snapshot['generated_at']),
        'at_audit_clock': inspect(snapshot),
        'limitation': 'Checks provenance/accounting and retained source bytes; not forecast accuracy. Blank percentages are unverified, never 50/50.',
    }
    (output / 'coverage-report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    lines = ['# Official-source audit — eaff7cce', '',
             f"Snapshot: {snapshot['generated_at']}. Inventory: {snapshot['coverage']}.", '',
             'Hotspawn determines membership only, never probabilities. Every row below links its primary fixture and its external evidence ledger. '
             'Probabilities are reproducible estimates, not verified outcomes. Empty cells are deliberately unverified.', '',
             '| Hotspawn fixture | Start UTC | Pick | Team 1 / team 2 probability | Method | Sources | Limitation |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    def cell(value):
        return str(value or '').replace('|', '\\|').replace('\n', ' ')
    for match in snapshot['matches']:
        if match['state'] != 'open':
            continue
        quote = (match.get('evidence') or [{}])[0]
        external = quote.get('url') or (match.get('hltv_context') or {}).get('source') or (match.get('vrs_research') or {}).get('source')
        links = '[Official fixture](' + match['source_url'] + ')'
        if external:
            links += ' · [External input](' + external + ')'
        p = match.get('probabilities')
        values = [match['id'] + ': ' + ' vs '.join(match['teams']), match['start'], match.get('pick'),
                  ' / '.join(f'{v:.1%}' for v in p) if p is not None else '', match.get('method'), links,
                  match.get('reason') or '; '.join(match.get('flags') or [])]
        lines.append('| ' + ' | '.join(cell(v) for v in values) + ' |')
    lines += ['', 'Exact response bodies, URL, observation time and SHA-256 are indexed in `evidence-index.json`; '
              'independent calculation verification is in `row-audit.md`. Failed reads remain recorded, not bypassed.', '']
    (output / 'rows.md').write_text('\n'.join(lines))
    print(json.dumps(report['snapshot_counts']))
    print('Coverage contract errors:', report['at_snapshot_clock']['problems'])
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/session-eaff7cce/capture')
    args = parser.parse_args()
    report = capture(args.snapshot, args.output)
    if report['at_snapshot_clock']['problems']:
        raise SystemExit('Coverage contract refused unsupported rows')


if __name__ == '__main__':
    main()
