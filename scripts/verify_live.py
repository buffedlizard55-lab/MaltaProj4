"""Verify that the live GitHub Pages site serves this run's exact build.

Why this polls instead of fetching once (measured 2026-10-16, session
9a81b26f): scheduled run 38936303441 built at 17:00:47Z, deployed
17:01:52-17:01:57Z, and the old one-shot verifier fetched build-info.json in
the same second the deploy step ended, read the *previous* deployment's
bytes, and failed the run while deployment 7124811549 was still updating
(until 17:02:00Z). The site then served exactly that build. Publication had
succeeded; only the receipt failed. The same shape recurred at 12:46Z and on
the PR #41 push run.

This verifier therefore polls for up to ``--deadline-seconds`` (default 360),
re-fetching with a fresh cache-busting query per attempt, until the live
manifest is byte-identical to this run's manifest -- or is a provably newer
build whose own files are byte-consistent with its manifest (an overlapping
deployment to the same github-pages environment superseded this one; the
site is then fresher, not stale). Any other outcome still fails closed:
an older build, a torn/mismatched file set, or an unreadable manifest is a
failed publication. Polling changes *patience*, never the standard of proof.

Stdlib only: the deploy job runs this with the runner's python3 and no pip
installs. The decision logic (``assess``) and the polling loop (``verify``
with injected fetch/sleep/clock) are unit-tested in
tests/test_verify_live_9a81b26f.py.
"""
import hashlib
import json
import os
import pathlib
import sys
import time
import urllib.request
from datetime import datetime, timezone

MATCH = 'match'
SUPERSEDED = 'superseded'
OLDER = 'older'
INVALID = 'invalid'


def assess(raw, manifest_sha, built_at):
    """Classify one fetched build-info.json payload against this run's build.

    Returns (verdict, live_dict_or_None). Never raises on malformed input:
    anything unparseable is INVALID, which the caller treats as not-yet-
    verified while polling and as failure at the deadline.
    """
    try:
        live = json.loads(raw)
    except (ValueError, TypeError, UnicodeDecodeError):
        return INVALID, None
    if not isinstance(live, dict) or not isinstance(live.get('files'), dict):
        return INVALID, None
    if manifest_sha and hashlib.sha256(raw).hexdigest() == manifest_sha:
        return MATCH, live
    live_built = live.get('built_at') or ''
    ours_built = built_at or ''
    if live_built and ours_built and live_built >= ours_built:
        return SUPERSEDED, live
    return OLDER, live


def _fetch(url, timeout=30):
    return urllib.request.urlopen(url, timeout=timeout).read()


def verify(site, manifest_sha, built_at, stamp, deadline_seconds=360,
           interval_seconds=15, fetch=_fetch, sleep=time.sleep,
           clock=time.monotonic, log=print):
    """Poll the live site until verified or the deadline passes.

    Returns a receipt dict. ``verified`` is True only when the live manifest
    matched this build (or a coherent newer build superseded it) *and* every
    file in the governing manifest hashed to its recorded digest.
    """
    base = site.rstrip('/') + '/'
    started = clock()
    attempts = 0
    last = {'verdict': INVALID, 'live': None, 'error': None}

    def bust(path):
        return '%s%s?deployment=%s-%d-%d' % (base, path, stamp, attempts, int(clock() * 1000))

    def files_match(live):
        mismatched = []
        for path, digest in live.get('files', {}).items():
            try:
                body = fetch(bust(path))
            except Exception as exc:  # treated as not-yet-propagated
                mismatched.append('%s (fetch error: %s)' % (path, type(exc).__name__))
                continue
            if hashlib.sha256(body).hexdigest() != digest:
                mismatched.append(path)
        return mismatched

    while True:
        attempts += 1
        try:
            raw = fetch(bust('build-info.json'))
            verdict, live = assess(raw, manifest_sha, built_at)
            last = {'verdict': verdict, 'live': live, 'error': None}
        except Exception as exc:
            last = {'verdict': INVALID, 'live': None, 'error': repr(exc)}
            verdict, live = INVALID, None
        elapsed = clock() - started
        if verdict in (MATCH, SUPERSEDED) and live is not None:
            mismatched = files_match(live)
            if not mismatched:
                return _receipt(base, live, built_at, manifest_sha, verdict,
                                mismatched, attempts, elapsed, verified=True)
            last['mismatched'] = mismatched
            log('Live manifest is %s but %d file(s) not yet consistent '
                '(attempt %d, %.0fs elapsed); still polling.'
                % (verdict, len(mismatched), attempts, elapsed))
        else:
            log('Live build-info verdict=%s (attempt %d, %.0fs elapsed); '
                'still polling.' % (verdict, attempts, elapsed))
        if elapsed >= deadline_seconds:
            live = last.get('live') or {}
            return _receipt(base, live, built_at, manifest_sha,
                            last.get('verdict', INVALID),
                            last.get('mismatched', []), attempts, elapsed,
                            verified=False, error=last.get('error'))
        sleep(min(interval_seconds, max(0.0, deadline_seconds - elapsed)))


def _receipt(base, live, built_at, manifest_sha, verdict, mismatched,
             attempts, elapsed, verified, error=None):
    return {
        'site': base,
        'revision': live.get('revision'),
        'rows': live.get('rows'),
        'built_at': live.get('built_at'),
        'expected_built_at': built_at or '',
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'files_checked': len(live.get('files', {})),
        'manifest_sha256': manifest_sha,
        'bytes_match_this_build': verdict == MATCH,
        'superseded_by_newer_build': verdict == SUPERSEDED,
        'verdict': verdict,
        'mismatched': mismatched,
        'attempts': attempts,
        'elapsed_seconds': round(elapsed, 1),
        'verified': verified,
        'last_error': error,
    }


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--deadline-seconds', type=float,
                        default=float(os.environ.get('VERIFY_DEADLINE_SECONDS', '360')))
    parser.add_argument('--interval-seconds', type=float, default=15.0)
    parser.add_argument('--receipt', default='runtime/live-verification.json')
    args = parser.parse_args(argv)

    site = os.environ.get('SITE') or 'https://buffedlizard55-lab.github.io/MaltaProj4/'
    manifest_sha = os.environ.get('MANIFEST_SHA') or ''
    built_at = os.environ.get('BUILT_AT') or ''
    stamp = os.environ.get('GITHUB_RUN_ID') or 'manual'
    if not manifest_sha or not built_at:
        raise SystemExit('MANIFEST_SHA and BUILT_AT are required; refusing to '
                         'verify against an unknown build.')

    receipt = verify(site, manifest_sha, built_at, stamp,
                     deadline_seconds=args.deadline_seconds,
                     interval_seconds=args.interval_seconds)
    receipt['deploy_outcome'] = os.environ.get('DEPLOY_OUTCOME')
    receipt['retry_outcome'] = os.environ.get('RETRY_OUTCOME')

    out = pathlib.Path(args.receipt)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2))
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as handle:
            handle.write('## Live Pages verification\n'
                         + json.dumps(receipt, indent=2) + '\n')

    if receipt['verified'] and receipt['bytes_match_this_build']:
        print('Verified %s against this build manifest (%d files, %d attempt(s), %.0fs).'
              % (receipt['site'], receipt['files_checked'], receipt['attempts'],
                 receipt['elapsed_seconds']))
        return 0
    if receipt['verified'] and receipt['superseded_by_newer_build']:
        print('The site serves a newer, byte-consistent build (%s >= %s); this run '
              'was superseded, which is not a failure.'
              % (receipt['built_at'], built_at))
        return 0
    if receipt['mismatched']:
        raise SystemExit('live files do not match the governing manifest after '
                         'polling: %s' % receipt['mismatched'])
    raise SystemExit('the live site is on an older or unreadable build (%s < %s, '
                     'verdict=%s) after polling; publication failed'
                     % (receipt['built_at'], built_at, receipt['verdict']))


if __name__ == '__main__':
    sys.exit(main())
