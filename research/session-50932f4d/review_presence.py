"""Read-only verification that this release's four findings reached public Pages."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

SITE = 'https://buffedlizard55-lab.github.io/MaltaProj4/'
NOTE_IDS = (
    'session-50932f4d-listing-event-binding',
    'session-50932f4d-source-authority-and-calibration',
    'session-50932f4d-neutral-model-and-rotating-test-gates',
    'session-50932f4d-corrected-capture-prose',
)


def inspect_review(manifest, body):
    soup = BeautifulSoup(body, 'html.parser')
    rows = soup.find_all('tr')
    present = {key: any(row.get('id') == key or key in row.get_text(' ', strip=True)
                        for row in rows) for key in NOTE_IDS}
    digest = hashlib.sha256(body).hexdigest()
    matches = manifest.get('files', {}).get('review.html') == digest
    return {'review_sha256': digest, 'review_hash_matches_manifest': matches,
            'published_revision': manifest.get('revision'), 'notes_present': present,
            'verified': matches and all(present.values())}


def fetch(path, stamp):
    request = Request(SITE + path + '?release-review=' + stamp,
                      headers={'User-Agent': 'CS2-Scout-release-readback/1.0',
                               'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        body = response.read(4_000_001)
        if len(body) > 4_000_000:
            raise ValueError('Public response exceeds the verification size limit')
        return body


def main():
    stamp = os.environ['GITHUB_RUN_ID']
    out = Path('research/session-50932f4d/live') / stamp
    out.mkdir(parents=True, exist_ok=True)
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'verified': False,
              'scope': 'Actual public review rows and exact adjacent manifest bytes; no publication.'}
    try:
        target = Path('research/session-50932f4d/release-target.json')
        expected = os.environ.get('EXPECTED_REVISION', '')
        if not expected and target.is_file():
            expected = json.loads(target.read_text())['expected_revision']
        manifest = json.loads(fetch('build-info.json', stamp))
        result.update(inspect_review(manifest, fetch('review.html', stamp)))
        result['expected_revision'] = expected or None
        if not result['verified']:
            raise ValueError('One or more review entries are missing, or the bytes do not match the manifest')
        if expected:
            actual = result['published_revision']
            if not all(re.fullmatch('[0-9a-f]{7,40}', str(v or '')) for v in (expected, actual)):
                raise ValueError('Revision binding requires real hexadecimal commit IDs')
            raw = subprocess.check_output([
                'gh', 'api', f'repos/{os.environ["GITHUB_REPOSITORY"]}/compare/{expected}...{actual}'])
            comparison = json.loads(raw)
            result['comparison_status'] = comparison['status']
            result['verified_includes_merge'] = comparison['status'] in ('ahead', 'identical')
            if not result['verified_includes_merge']:
                raise ValueError('The public review manifest does not include the requested merge')
    except Exception as error:
        result.update(verified=False, error=f'{type(error).__name__}: {error}')
    (out / 'review-presence.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
