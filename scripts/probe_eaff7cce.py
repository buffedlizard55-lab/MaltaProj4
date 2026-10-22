"""Retain a dated, replayable, non-publishing source audit on this session branch.

No pick or input is invented here. The real collector and independent arithmetic
review run first; this script archives their exact response bytes and reports
coverage at the observation clock separately from coverage at the audit clock.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import iso, pick_deadline
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
    # The collector's raw snapshot has no expires_at: the build derives it.
    # Check the same pure deadline function without changing the retained input
    # or resetting any observed/updated clock. Missing inputs still fail closed.
    checked = copy.deepcopy(snapshot)
    for match in checked['matches']:
        match['expires_at'] = pick_deadline(match, checked.get('fixtures_observed_at'))
    report = {
        'session': 'eaff7cce', 'run_id': os.getenv('GITHUB_RUN_ID'),
        'revision': os.getenv('GITHUB_SHA'), 'audited_at': iso(datetime.now(timezone.utc)),
        'snapshot_generated_at': snapshot['generated_at'], 'inventory_coverage': snapshot['coverage'],
        'snapshot_counts': coverage(snapshot),
        'at_snapshot_clock': inspect(checked, snapshot['generated_at']),
        'at_audit_clock': inspect(checked),
        'normalization': 'Only expires_at is derived using the production build pick_deadline function. Retained snapshot.json and every source timestamp remain unchanged.',
        'calculated_deadlines': {m['id']: m['expires_at'] for m in checked['matches'] if m.get('pick') or m.get('probabilities') is not None},
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


# Research leads, not a probability register. All concern current uncovered rows.
TARGETS = [
    ('1079654', 'STAVKA secondary winner panel lead', 'https://stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec'),
    ('1081150', 'STAVKA secondary listing follow-up', 'https://stavka.tv/matches/csgo/23-10-2026-ex-rustec-saint-sinners'),
    ('1082919', 'Hotspawn fixture identity', 'https://www.hotspawn.com/matches/projeto-do-kingui-vs-martians-cct-south-america-2026-series-7-1082919'),
    ('1082919', 'Hotspawn linked team roster', 'https://www.hotspawn.com/counter-strike/teams/projeto-do-kingui-205414'),
    ('1082919', 'HLTV near-match identity and lineup', 'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7'),
    ('1082919', 'HLTV team roster/history conflict', 'https://www.hltv.org/team/13151/tropa-do-kingui'),
    ('1082919', 'EGW named fixture and roster; placeholder odds are rejected', 'https://egamersworld.com/counterstrike/match/0U32SId-H/projeto-do-kingui-vs-martians-esports-3j3hkufF0'),
]


def read_targets(output, source=None):
    """Retain exact bytes for manual audit; never turn arbitrary panels into odds.

    Uses the normal collector, including rate limits, cached-source clocks and
    access refusals. No spoofing or bypass; failed reads are useful audit output.
    """
    from bs4 import BeautifulSoup
    from scripts.refresh import Sources
    src = source or Sources(datetime.now(timezone.utc))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for fixture_id, name, url in TARGETS:
        row = {'fixture_id': fixture_id, 'name': name, 'url': url, 'accepted_as_probability': False}
        try:
            body, receipt = src.get(name, url, False)
            soup = BeautifulSoup(body, 'html.parser')
            row['title'] = soup.title.get_text(' ', strip=True) if soup.title else None
            row['structured_data'] = []
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    row['structured_data'].append(json.loads(script.get_text()))
                except (TypeError, ValueError):
                    row['structured_data'].append({'unverified': 'invalid structured data'})
            for node in soup(['script', 'style', 'nav', 'footer']):
                node.decompose()
            text_path = output / (fixture_id + '-' + str(len(rows)) + '.txt')
            text_path.write_text(soup.get_text(' ', strip=True)[:40000] + '\n')
            row.update(status='captured for review, not accepted', text_file=text_path.name,
                       sha256=receipt.get('sha256'), observed_at=receipt.get('observed_at'))
        except (ValueError, KeyError, TypeError) as error:
            row.update(status='unverified; access failed', error=str(error))
        rows.append(row)
    index = evidence_index({'source_checks': src.log}, 'runtime/sources', output / 'raw')
    report = {'run_id': os.getenv('GITHUB_RUN_ID'), 'revision': os.getenv('GITHUB_SHA'),
              'audited_at': iso(datetime.now(timezone.utc)), 'targets': rows, 'source_checks': index,
              'limitation': 'Research only. No fixture, alias, ranking or probability register is modified. All displayed prices require manual market/UTC/operator review.'}
    (output / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'targets': len(rows), 'captured': sum(bool(r.get('sha256')) for r in rows), 'probabilities_accepted': 0}))
    return report


def capture_live(output, expected_path='build-info.json', fetch=None, verifier=None, now=None):
    """Archive exact, independently hash-verified public bytes, never new inputs.

    A runner performs this read because the sandbox cannot download Azure audit
    artifacts. No publication, clock renewal, model calculation or source access
    occurs here. A later receipt PR can retain a newer live snapshot rather than
    accidentally re-publish an older committed fallback.
    """
    import hashlib
    import time
    from scripts import core, verify_live

    output, expected_path = Path(output), Path(expected_path)
    output.mkdir(parents=True, exist_ok=True)
    fetch, verifier = fetch or verify_live._fetch, verifier or verify_live.verify
    expected_bytes = expected_path.read_bytes()
    expected = json.loads(expected_bytes)
    baseline = json.loads((expected_path.parent / 'data/latest.json').read_bytes())
    site = 'https://buffedlizard55-lab.github.io/MaltaProj4/'
    stamp = os.getenv('GITHUB_RUN_ID', str(time.time_ns()))
    receipt = verifier(site, hashlib.sha256(expected_bytes).hexdigest(),
                       expected['built_at'], stamp, fetch=fetch)
    try:
        if receipt.get('verified') is not True:
            raise ValueError('Public bytes are not independently verified')
        raw_manifest = fetch(site + 'build-info.json?delivery=' + stamp)
        live = json.loads(raw_manifest)
        if (live.get('revision'), live.get('built_at')) != (receipt.get('revision'), receipt.get('built_at')):
            raise ValueError('Public build changed after verification; rerun without mixing versions')
        if set(live['files']) != set(expected['files']) or receipt.get('files_checked') != len(expected['files']):
            raise ValueError('Public manifest must retain the full expected file set')
        raw_snapshot = fetch(site + 'data/latest.json?delivery=' + stamp)
        if hashlib.sha256(raw_snapshot).hexdigest() != live['files']['data/latest.json']:
            raise ValueError('Public snapshot bytes do not match the governing manifest')
        snapshot = json.loads(raw_snapshot)
        if snapshot['generated_at'] != live['snapshot_generated_at']:
            raise ValueError('Public generation and manifest disagree')
        if core.dt(snapshot['generated_at']) < core.dt(baseline['generated_at']):
            raise ValueError('Refuse a backward snapshot generation')
        if core.dt(snapshot['fixtures_observed_at']) < core.dt(baseline['fixtures_observed_at']):
            raise ValueError('Refuse a backward fixture observation')
        if not core.fresh(snapshot['fixtures_observed_at'], now or datetime.now(timezone.utc)):
            raise ValueError('Refuse expired or future fixture observations')
        receipt.update(snapshot_generated_at=snapshot['generated_at'],
                       fixtures_observed_at=snapshot['fixtures_observed_at'],
                       live_manifest_sha256=hashlib.sha256(raw_manifest).hexdigest(),
                       snapshot_sha256=hashlib.sha256(raw_snapshot).hexdigest(),
                       snapshot_counts=coverage(snapshot), run_id=os.getenv('GITHUB_RUN_ID'),
                       note='Exact public bytes; no source/quote timestamp was renewed.')
        (output / 'live-build-info.json').write_bytes(raw_manifest)
        (output / 'live-snapshot.json').write_bytes(raw_snapshot)
    except Exception as exc:
        receipt.update(verified=False, last_error=str(exc))
        raise
    finally:
        (output / 'live-verification.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-only', action='store_true', help='Archive exact 20-file-verified public bytes without publishing or refreshing sources')
    parser.add_argument('--targets-only', action='store_true', help='Read bounded, unaccepted gap-research leads only; do not refresh or change picks')
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/session-eaff7cce/capture')
    args = parser.parse_args()
    if args.live_only:
        capture_live(Path(args.output).parent / 'publication' / os.getenv('GITHUB_RUN_ID', 'local'))
        return
    if args.targets_only:
        read_targets(Path(args.output).parent / 'targeted')
        return
    report = capture(args.snapshot, args.output)
    if report['at_snapshot_clock']['problems']:
        raise SystemExit('Coverage contract refused unsupported rows')


if __name__ == '__main__':
    main()
