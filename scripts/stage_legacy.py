"""Stage the small, verified root-site fallback required by legacy main:/ Pages.

Only run after build + validate. This is not the six-hour updater: production
refreshes publish a verified Pages artifact. No git operations occur here.
"""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
ALLOWED = {
    'index.html', 'picks.html', 'matches.html', 'unresolved.html', 'review.html',
    'sources.html', 'evidence.html', '404.html', 'assets/app.js', 'assets/style.css',
    'assets/favicon.svg', 'data/latest.json', 'data/matches.csv',
    'methodology.html', 'site/index.html', 'site/picks.html', 'site/unresolved.html',
    'site/review.html', 'site/methodology.html',
}


def main():
    manifest = json.loads((PUBLIC / 'build-info.json').read_text())
    assert set(manifest['files']) == ALLOWED, 'Unexpected public file set; review before copying'
    for relative, digest in manifest['files'].items():
        source = PUBLIC / relative
        assert source.is_file() and not source.is_symlink()
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    for relative in sorted(ALLOWED | {'build-info.json', '.nojekyll'}):
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PUBLIC / relative, destination)
    print('Staged verified static root fallback; no branches changed or pushed.')


if __name__ == '__main__':
    main()
