"""Dated, read-only coverage report and compact, byte-replayable source archive.

Run after the real refresh and quarantine on a network-capable GitHub runner.
No values are added to the snapshot: unsupported percentages stay blank.
Raw successful responses are archived as deterministic gzip files, keyed by
SHA-256, rather than committing a large uncompressed crawler dataset.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from scripts.core import iso


def evidence_index(snapshot, source_dir, destination):
    """Archive the exact bytes named by the collector's receipts, never a re-encoding."""
    source_dir, destination = Path(source_dir), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for receipt in snapshot.get('source_checks', []):
        record = dict(receipt)
        digest = receipt.get('sha256')
        if not digest:
            record['archive_status'] = 'no successful response body'
            records.append(record)
            continue
        candidates = list(source_dir.glob(digest + '.*'))
        if len(candidates) != 1:
            record['archive_status'] = 'missing or ambiguous body; unverified'
            records.append(record)
            continue
        path = candidates[0]
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != digest:
            raise ValueError('Source body hash mismatch: ' + path.name)
        target = destination / (path.name + '.gz')
        target.write_bytes(gzip.compress(body, mtime=0))
        record.update(archive_status='exact response bytes retained',
                      archive='raw/' + target.name,
                      archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        records.append(record)
    return records


def verify_primary_inventory(snapshot, raw):
    """Compare every retained non-crowd input field to the exact API response.

    A multi-source union must not be falsely certified from a single response:
    if the ID sets differ, report that limitation instead of claiming parity.
    The independent row auditor separately checks normalization and arithmetic.
    """
    decoded = json.loads(raw)
    items = decoded.get('data') if isinstance(decoded, dict) else decoded
    if not isinstance(items, list):
        raise ValueError('Unrecognized official fixtures response')
    primary = {str(r['id']): r for r in items if r.get('sport_alias') == 'cs2'}
    retained = {str(r['id']): r for r in snapshot['fixture_evidence']}
    if set(primary) != set(retained):
        return {'status': 'unverified single-source parity; inspect all contributing captures',
                'primary_ids': sorted(primary), 'retained_ids': sorted(retained), 'rows': []}
    rows = []
    for ident, row in retained.items():
        for key, value in row.items():
            if 'picked' in key or key == 'total_picks':
                raise ValueError('Crowd field retained as evidence: ' + key)
            if key not in primary[ident] or primary[ident][key] != value:
                raise ValueError('Primary field mismatch: ' + ident + ' / ' + key)
        rows.append({'fixture_id': ident, 'status': 'every retained field matches the official response',
                     'fields_checked': len(row)})
    return {'status': 'exact ID-set and non-crowd field parity', 'rows_checked': len(rows), 'rows': rows}


def coverage(snapshot):
    rows = [m for m in snapshot['matches'] if m['state'] == 'open']
    return {
        'feed_rows': len(snapshot['matches']),
        'open': len(rows),
        'with_pick': sum(bool(m.get('pick')) for m in rows),
        'with_probability': sum(m.get('probabilities') is not None for m in rows),
        'market': sum(m.get('probabilities') is not None and m.get('method') in ('exchange', 'exchange_wide', 'bookmaker_fallback', 'bookmaker') for m in rows),
        'model': sum(m.get('probabilities') is not None and m.get('method') in ('model_vrs', 'model_vrs_mirror') for m in rows),
        'official_file_models': sum(m.get('probabilities') is not None and m.get('method') == 'model_vrs' for m in rows),
        'hltv_mirror_models': sum(m.get('probabilities') is not None and m.get('method') == 'model_vrs_mirror' for m in rows),
        'research_only': sum(m.get('probabilities') is None and bool(m.get('pick')) for m in rows),
        'unresolved': sum(not m.get('pick') for m in rows),
    }


def markdown(snapshot):
    counts = coverage(snapshot)
    out = [
        '# Official-source row audit — session ac4743a3', '',
        'Snapshot: **' + iso(snapshot['generated_at']) + '**. Inventory coverage: **' + snapshot['coverage'] + '**.', '',
        'This is a dated observation, not a promise about future fixtures or prices. '
        'Hotspawn is inventory only; its crowd fields are excluded. Blank means unverified, never 50/50.', '',
        ' · '.join(str(value) + ' ' + key.replace('_', ' ') for key, value in counts.items()), '',
        '| Fixture | Start UTC | Pick | Team 1 / team 2 probability | Method | Official fixture / probability evidence | Limitation |',
        '| --- | --- | --- | --- | --- | --- | --- |',
    ]
    def cell(value):
        return str(value or '').replace('|', '\\|').replace('\n', ' ')
    for m in snapshot['matches']:
        if m['state'] != 'open':
            continue
        quotes = m.get('evidence') or []
        source = (quotes[0].get('url') if quotes else None) or (m.get('vrs_research') or {}).get('source') or (m.get('hltv_context') or {}).get('source')
        links = '[Hotspawn](' + m['source_url'] + ')'
        if source:
            links += ' · [External evidence](' + source + ')'
        probabilities = ' / '.join(f'{p:.1%}' for p in m['probabilities']) if m.get('probabilities') is not None else ''
        limitation = m.get('reason') or '; '.join(m.get('flags') or [])
        values = [m['id'] + ': ' + ' vs '.join(m['teams']), m['start'], m.get('pick'), probabilities, m.get('method'), links, limitation]
        out.append('| ' + ' | '.join(cell(x) for x in values) + ' |')
    out += ['', '## Inventory irregularities and source limits', '']
    for issue in snapshot.get('issues') or []:
        out.append('- **' + cell(issue.get('code')) + ':** ' + cell(issue.get('message')) + ' [Source](' + str(issue.get('source') or '') + ')')
    out += ['', 'Every successful collector response is retained under `raw/` as exact gzip-compressed bytes. '
            '`evidence-index.json` records the official URL, observation time, response SHA-256 and archive SHA-256. '
            'Access failures are recorded, not bypassed. The independent audit is in `row-audit.md`.', '']
    return '\n'.join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/session-ac4743a3/capture')
    args = parser.parse_args(argv)
    snapshot = json.loads(Path(args.snapshot).read_text())
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'snapshot.json').write_text(json.dumps(snapshot, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    index = evidence_index(snapshot, 'runtime/sources', output / 'raw')
    (output / 'evidence-index.json').write_text(json.dumps(index, indent=2, ensure_ascii=False) + '\n')
    fixture_source = next((r for r in index if r.get('name') == 'Hotspawn CS2 fixtures' and r.get('archive')), None)
    if fixture_source:
        raw = gzip.decompress((output / fixture_source['archive']).read_bytes())
        parity = verify_primary_inventory(snapshot, raw)
        parity['official_source'] = fixture_source['url']
        parity['source_sha256'] = fixture_source['sha256']
        (output / 'primary-inventory-audit.json').write_text(json.dumps(parity, indent=2) + '\n')
    (output / 'coverage.md').write_text(markdown(snapshot))
    (output / 'counts.json').write_text(json.dumps(coverage(snapshot), indent=2) + '\n')
    print(json.dumps(coverage(snapshot)))
    for row in snapshot['matches']:
        if row['state'] == 'open' and row.get('probabilities') is None:
            print(row['id'], ' vs '.join(row['teams']), row.get('pick'), row.get('method'), row.get('reason'))


if __name__ == '__main__':
    main()
