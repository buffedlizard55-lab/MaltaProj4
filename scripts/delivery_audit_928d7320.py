"""Read-only delivery ledger. Never fetches, fills, or edits source data.

Checks fallback ordering and distinguishes primary prices from indirect listings
and originated models. Arithmetic/source payload replay is a separate gate:
verification-c6/audit_snapshot.py. Exit nonzero on missing auditability.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


def secure_url(value):
    try:
        p = urlsplit(value or '')
        return p.scheme == 'https' and bool(p.hostname) and not p.username and not p.password
    except ValueError:
        return False


def evidence_class(method):
    if (method or '').startswith('model_'):
        return 'Originated model; not a betting price'
    if method == 'bookmaker_fallback':
        return 'Indirect bookmaker listing; not direct book verification'
    if (method or '').startswith('research_'):
        return 'Research-only; percentage unverified'
    if method == 'exchange_wide':
        return 'Wide exchange; reduced confidence'
    return 'Primary market' if method in ('exchange', 'bookmaker') else 'Unresolved'


def inspect(snapshot):
    errors, ledger = [], []
    counts = Counter()
    seen = set()
    for row in snapshot['matches']:
        ident = str(row['id'])
        if ident in seen:
            errors.append(f'{ident}: duplicate fixture ID')
        seen.add(ident)
        if not secure_url(row.get('source_url')):
            errors.append(f'{ident}: missing fixture source URL')
        if row.get('state') != 'open':
            continue
        method = row.get('method')
        counts[method or 'unresolved'] += 1
        evidence = row.get('evidence') or []
        attempts = row.get('attempts') or []
        providers = [a.get('provider', '') for a in attempts]
        # Strict featured exchange resolution needs no additional research.
        # All other methods must show the requested HLTV-first, book-next path.
        if method != 'exchange':
            hltv = next((i for i, p in enumerate(providers) if p == 'HLTV'), None)
            book = next((i for i, p in enumerate(providers)
                         if any(x in p.lower() for x in ('pinnacle', 'thunderpick', 'gg.bet', 'book'))), None)
            if hltv is None or book is None or hltv >= book:
                errors.append(f'{ident}: missing HLTV-before-esportsbook attempt trail')
        if row.get('pick') and row['pick'] not in row.get('teams', []):
            errors.append(f'{ident}: pick is not a fixture team')
        if row.get('pick') and not evidence:
            errors.append(f'{ident}: pick without evidence')
        for e in evidence:
            if not secure_url(e.get('url')):
                errors.append(f'{ident}: evidence lacks source URL')
            if not e.get('observed_at'):
                errors.append(f'{ident}: evidence lacks observation timestamp')
            host = urlsplit(e.get('url') or '').hostname or ''
            if host == 'hotspawn.com' or host.endswith('.hotspawn.com'):
                errors.append(f'{ident}: Hotspawn cannot supply a probability')
        if not row.get('pick') and (not row.get('reason') or not attempts):
            errors.append(f'{ident}: unresolved row lacks limitation or attempt trail')
        if method and method.startswith('research_') and row.get('probabilities') is not None:
            errors.append(f'{ident}: research-only row has an unsupported percentage')
        ledger.append({
            'id': ident, 'teams': row.get('teams'), 'pick': row.get('pick'),
            'probabilities': row.get('probabilities'), 'method': method,
            'classification': evidence_class(method), 'fixture_source': row.get('source_url'),
            'evidence_sources': [e.get('url') for e in evidence],
            'attempts': [{'provider': a.get('provider'), 'status': a.get('status'),
                          'url': a.get('url'), 'reason': a.get('reason')} for a in attempts],
            'limitations': [e.get('limitation') or e.get('warning') for e in evidence
                            if e.get('limitation') or e.get('warning')] + ([row['reason']] if row.get('reason') else []),
        })
    return {'generated_at': snapshot.get('generated_at'),
            'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
            'total_rows': len(snapshot['matches']), 'open_rows': len(ledger),
            'methods': dict(sorted(counts.items())), 'errors': errors, 'rows': ledger}


def escape(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def markdown(result):
    lines = ['# Independent delivery ledger', '',
             f"Snapshot: `{result['generated_at']}`. Fixture evidence: `{result['fixtures_observed_at']}`.",
             f"{result['total_rows']} feed rows; {result['open_rows']} open; {len(result['errors'])} auditability failures.",
             '', 'This is a replay of retained evidence, **not a live HTTP recheck**. A source link is not proof that a provider is accessible now. Models are originated estimates, not verified bookmaker prices; third-party listings are not direct bookmaker confirmations. Historical/not-open entries are not current recommendations.', '',
             '| Match | Pick | Team probabilities (same order) | Evidence type | Fixture / probability sources | Limitations |',
             '| --- | --- | --- | --- | --- | --- |']
    for r in result['rows']:
        probs = r['probabilities']
        percent = ' / '.join(f'{p:.1%}' for p in probs) if probs is not None else ''
        links = [f"[Hotspawn]({r['fixture_source']})"]
        links += [f'[Evidence {i+1}]({url})' for i, url in enumerate(r['evidence_sources'])]
        lines.append('| ' + ' | '.join(map(escape, [r['id'] + ': ' + ' vs '.join(r['teams']), r['pick'], percent, r['classification'], ' · '.join(links), '; '.join(r['limitations'])])) + ' |')
    lines += ['', '## Research order and access limitations', '',
              'The JSON companion retains every provider attempt, status, reason and source link. Every non-featured row must attempt HLTV before an esportsbook. Failed access is recorded, never interpreted as a price. Unresolved percentages remain blank.', '',
              '## Auditability failures', ''] + (['- ' + e for e in result['errors']] or ['None.'])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='data/latest.json')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raw = Path(args.data).read_bytes()
    result = inspect(json.loads(raw))
    result['snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
    dest = Path(args.output)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'ledger.json').write_text(json.dumps(result, indent=2) + '\n')
    (dest / 'ledger.md').write_text(markdown(result))
    print(f"{result['total_rows']} rows / {result['open_rows']} open / {len(result['errors'])} failures")
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
