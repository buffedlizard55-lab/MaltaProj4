"""Dated, read-only coverage probe and compact SHA-256 raw archive for session cb867c3c.

Runs after ``scripts.refresh`` and ``scripts.quarantine`` on a GitHub-hosted runner.
Retains every successful official HTTP response body as deterministic gzip bytes
keyed by SHA-256 so every published or research-only row can be re-derived offline
byte-for-byte without guessing or manufacturing values.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from scripts.core import iso


def evidence_index(snapshot: dict, source_dir: str | Path, destination: str | Path) -> list[dict]:
    source_dir, destination = Path(source_dir), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
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
        record.update(
            archive_status='exact response bytes retained',
            archive='raw/' + target.name,
            archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        )
        records.append(record)
    return records


def verify_primary_inventory(snapshot: dict, raw: bytes) -> dict:
    decoded = json.loads(raw)
    items = decoded.get('data') if isinstance(decoded, dict) else decoded
    if not isinstance(items, list):
        raise ValueError('Unrecognized official fixtures response')
    primary = {str(r['id']): r for r in items if r.get('sport_alias') == 'cs2'}
    retained = {str(r['id']): r for r in snapshot['fixture_evidence']}
    if set(primary) != set(retained):
        return {
            'status': 'unverified single-source parity; inspect all contributing captures',
            'primary_ids': sorted(primary),
            'retained_ids': sorted(retained),
            'rows': [],
        }
    rows = []
    for ident, row in retained.items():
        for key, value in row.items():
            if 'picked' in key or key == 'total_picks':
                raise ValueError('Crowd field retained as evidence: ' + key)
            if key not in primary[ident] or primary[ident][key] != value:
                raise ValueError('Primary field mismatch: ' + ident + ' / ' + key)
        rows.append({
            'fixture_id': ident,
            'status': 'every retained field matches the official response',
            'fields_checked': len(row),
        })
    return {
        'status': 'exact ID-set and non-crowd field parity',
        'rows_checked': len(rows),
        'fields_total': sum(r['fields_checked'] for r in rows),
        'rows': rows,
    }


def coverage(snapshot: dict) -> dict:
    rows = [m for m in snapshot['matches'] if m['state'] == 'open']
    methods: dict[str, int] = {}
    for m in rows:
        key = str(m.get('method') or 'none')
        methods[key] = methods.get(key, 0) + 1
    return {
        'feed_rows': len(snapshot['matches']),
        'open': len(rows),
        'with_pick': sum(bool(m.get('pick')) for m in rows),
        'with_probability': sum(m.get('probabilities') is not None for m in rows),
        'market': sum(
            m.get('probabilities') is not None
            and m.get('method') in ('exchange', 'exchange_wide', 'bookmaker_fallback', 'bookmaker')
            for m in rows
        ),
        'model': sum(
            m.get('probabilities') is not None
            and m.get('method') in ('model_vrs', 'model_vrs_mirror')
            for m in rows
        ),
        'official_file_models': sum(
            m.get('probabilities') is not None and m.get('method') == 'model_vrs'
            for m in rows
        ),
        'hltv_mirror_models': sum(
            m.get('probabilities') is not None and m.get('method') == 'model_vrs_mirror'
            for m in rows
        ),
        'research_only': sum(
            m.get('probabilities') is None and bool(m.get('pick'))
            for m in rows
        ),
        'unresolved': sum(not m.get('pick') for m in rows),
        'methods': dict(sorted(methods.items())),
    }


def markdown(snapshot: dict) -> str:
    counts = coverage(snapshot)
    out = [
        '# Official-source row audit — session cb867c3c',
        '',
        'Snapshot: **' + iso(snapshot['generated_at']) + '**. Inventory coverage: **' + snapshot['coverage'] + '**.',
        '',
        'Hotspawn supplies CS2 fixture inventory and lock times only; crowd percentages are never retained or used. '
        'Every published win probability re-derives from a dated external two-way quote or Valve\'s published VRS model.',
        '',
        '| Fixture | Tournament | Start UTC | Pick | Team 1 / Team 2 win % | Fair odds | Method | Sources | Notes / Limitations |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]

    def cell(value: object) -> str:
        return str(value or '').replace('|', '\\|').replace('\n', ' ')

    for m in snapshot['matches']:
        if m['state'] != 'open':
            continue
        quotes = m.get('evidence') or []
        source = (
            (quotes[0].get('url') if quotes else None)
            or (m.get('vrs_research') or {}).get('source')
            or (m.get('hltv_context') or {}).get('source')
        )
        links = '[Hotspawn](' + m['source_url'] + ')'
        if source:
            links += ' · [Evidence](' + source + ')'
        probs = ' / '.join(f'{p:.1%}' for p in m['probabilities']) if m.get('probabilities') is not None else ''
        fair = ' / '.join(f'{o:.2f}' for o in m['fair_odds']) if m.get('fair_odds') is not None else ''
        limitation = m.get('reason') or '; '.join(m.get('flags') or [])
        values = [
            f"{m['id']}: {' vs '.join(m['teams'])}",
            m.get('competition'),
            m.get('start'),
            m.get('pick'),
            probs,
            fair,
            m.get('method'),
            links,
            limitation,
        ]
        out.append('| ' + ' | '.join(cell(x) for x in values) + ' |')
    out += ['', '## Inventory issues and source checks', '']
    for issue in snapshot.get('issues') or []:
        out.append(f"- **{cell(issue.get('code'))}:** {cell(issue.get('message'))} ([source]({issue.get('source') or ''}))")
    out.append('')
    return '\n'.join(out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-cb867c3c')
    args = parser.parse_args(argv)
    snapshot = json.loads(Path(args.snapshot).read_text())
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'snapshot.json').write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    )
    index = evidence_index(snapshot, 'runtime/sources', output / 'raw')
    (output / 'evidence-index.json').write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + '\n'
    )
    fixture_source = next(
        (r for r in index if r.get('name') == 'Hotspawn CS2 fixtures' and r.get('archive')),
        None,
    )
    if fixture_source:
        raw = gzip.decompress((output / fixture_source['archive']).read_bytes())
        parity = verify_primary_inventory(snapshot, raw)
        parity['official_source'] = fixture_source['url']
        parity['source_sha256'] = fixture_source['sha256']
        (output / 'primary-inventory-audit.json').write_text(
            json.dumps(parity, indent=2, ensure_ascii=False) + '\n'
        )
    (output / 'coverage.md').write_text(markdown(snapshot))
    (output / 'counts.json').write_text(json.dumps(coverage(snapshot), indent=2) + '\n')
    print(json.dumps(coverage(snapshot), indent=2))


if __name__ == '__main__':
    main()
