"""Assemble a research harvest from a real refresh run.

This helper never publishes and never writes to the site. It exists because the
authoring environment can reach GitHub but not the primary sources, so the real
refresh (with normal internet access) runs on a GitHub Actions runner and the
resulting snapshot plus every command log is committed for local re-checking.

Nothing here derives or alters a value: the snapshot is copied byte-for-byte and
only inventory counts are summarised.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def describe_snapshot(path):
    data = json.loads(path.read_text())
    matches = data.get('matches') or []
    open_rows = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    research = [m for m in open_rows if m.get('method') == 'research_rank']
    blank = [m for m in open_rows if m.get('probabilities') is None and m.get('method') != 'research_rank']
    return {
        'generated_at': data.get('generated_at'),
        'fixtures_observed_at': data.get('fixtures_observed_at'),
        'coverage': data.get('coverage'),
        'rows_total': len(matches),
        'rows_open': len(open_rows),
        'rows_open_with_prices': len(priced),
        'rows_open_research_only': len(research),
        'rows_open_without_pick': len(blank),
        'open_pick_methods': {m.get('method'): sum(1 for x in open_rows if x.get('method') == m.get('method')) for m in open_rows},
        'unresolved_open_ids': [m['id'] for m in blank],
        'open_ids': [m['id'] for m in open_rows],
        'issues': data.get('issues'),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    runtime = Path(args.runtime)
    if runtime.exists() and runtime.stat().st_size:
        target = out / 'latest.json'
        shutil.copyfile(runtime, target)
        files['latest.json'] = sha256(target)
        summary = describe_snapshot(target)
    else:
        summary = {'error': 'refresh produced no snapshot; see logs/refresh.txt'}
    for name in ('validation.json', 'row-audit.md', 'published-row-audit.md'):
        source = Path('runtime') / name
        if source.exists() and source.stat().st_size:
            target = out / name
            shutil.copyfile(source, target)
            files[name] = sha256(target)
    (out / 'harvest-summary.json').write_text(json.dumps({'files': files, 'snapshot': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2)[:4000])

if __name__ == '__main__':
    main()
