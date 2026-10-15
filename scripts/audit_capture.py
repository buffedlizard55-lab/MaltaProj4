"""Run the preserved independent auditor on an explicitly supplied capture.

The auditor imports no production normalization/probability code. This wrapper
only supplies its three original input paths; it does not alter its assertions.
Use an API capture only when its ID set equals the selected snapshot (partial
unions need every contributing capture, not a false single-source parity claim).
"""
import argparse
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', type=Path, default=Path('data/latest.json'))
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    path = ROOT / 'verification-95b588c2/audit_snapshot.py'
    spec = importlib.util.spec_from_file_location('independent_capture_auditor', path)
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    with tempfile.TemporaryDirectory() as temp:
        inputs = Path(temp)
        (inputs / 'data').mkdir()
        (inputs / 'research/probe').mkdir(parents=True)
        shutil.copyfile(args.snapshot, inputs / 'data/latest.json')
        shutil.copyfile(args.fixtures, inputs / 'research/probe/fixtures.txt')
        shutil.copyfile(ROOT / 'data/identities.json', inputs / 'data/identities.json')
        report = auditor.run(inputs)
    report['implementation'] = 'buffedlizard55-lab/MaltaProj4'
    report['inputs'] = {'snapshot': str(args.snapshot), 'retained_primary_response': str(args.fixtures),
                       'auditor': str(path.relative_to(ROOT))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f"Independent capture audit: {report['row_count']} rows and {report['priced_rows_recomputed']} quote calculations passed.")


if __name__ == '__main__':
    main()
