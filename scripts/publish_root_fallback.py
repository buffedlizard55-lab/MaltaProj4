"""Publish the verified build to the legacy ``main:/`` root, but only forwards.

Measured, not assumed: this repository's GitHub Pages site is still configured as
``build_type: legacy`` with ``source: main:/`` (read from
``GET /repos/buffedlizard55-lab/MaltaProj4/pages`` on 2026-10-21T21:20Z; the
``PUT`` that would switch it to GitHub Actions answers HTTP 403 for this
integration). Every push therefore republishes the *committed* root pages over
whatever the verified artifact deploy just published.

On 2026-10-21 that made the live board stale for three days: the last push at
21:14:32Z republished a root fallback built from the frozen 2026-10-18
bootstrap, so the public site showed ``Snapshot expired ... Current picks are
withheld`` and 34 closed matches while CI was publishing a fresh, fully verified
build at the same moment. Nothing in the site was wrong; the committed fallback
was simply old, and the old staging path had no rule against going backwards.

This module is that rule. It stages the verified ``public/`` build to the
repository root (and the matching snapshot to ``data/latest.json``, so the
committed fallback stays internally consistent and ``scripts.validate --site .``
still reproduces it) only when:

* the verified build carries a readable snapshot timestamp;
* that snapshot is inside the 8-hour evidence window, so an expired or
  timestamp-less build is never promoted;
* it is strictly newer than the snapshot already committed at the root;
* the committed root is older than the cooldown (4 hours by default), which
  keeps the promise of a 4-8 hour refresh without committing on every push.

Every refusal is a normal exit with a machine-readable reason, so the workflow
can log why the root was left alone instead of failing a green build.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import stage_legacy

DEFAULT_COOLDOWN_HOURS = 4.0
DEFAULT_STALE_AFTER_HOURS = 8.0


def moment(value):
    """Parse an ISO-8601 timestamp into an aware UTC datetime, or return None."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def decide(fresh_snapshot, committed_snapshot, now, cooldown_hours=DEFAULT_COOLDOWN_HOURS,
           stale_after_hours=DEFAULT_STALE_AFTER_HOURS):
    """Return ``(publish, reason)`` for one verified build. Pure, so it is unit tested."""
    fresh = moment(fresh_snapshot)
    if fresh is None:
        return False, 'the verified build carries no readable snapshot timestamp, so it cannot be published'
    age_hours = (now - fresh).total_seconds() / 3600.0
    if age_hours > stale_after_hours:
        return False, ('the verified snapshot is %.1f hours old, outside the %.0f-hour evidence window, '
                       'so publishing it would only move the expiry banner' % (age_hours, stale_after_hours))
    committed = moment(committed_snapshot)
    if committed is not None and committed >= fresh:
        return False, ('the committed root fallback already carries a snapshot at least as new '
                       '(%s >= %s)' % (committed_snapshot, fresh_snapshot))
    if committed is not None:
        committed_hours = (now - committed).total_seconds() / 3600.0
        if committed_hours < cooldown_hours:
            return False, ('the committed root fallback is %.1f hours old, inside the %.1f-hour cooldown'
                           % (committed_hours, cooldown_hours))
    return True, 'staging the verified build: %s replaces %s' % (fresh_snapshot, committed_snapshot or 'no committed snapshot')


def committed_snapshot(root):
    """Snapshot stamp of the build currently committed at the repository root."""
    try:
        manifest = json.loads((Path(root) / 'build-info.json').read_text())
    except (OSError, ValueError):
        return None
    return manifest.get('snapshot_generated_at')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--public', default='public')
    parser.add_argument('--root', default='.')
    parser.add_argument('--cooldown-hours', type=float, default=DEFAULT_COOLDOWN_HOURS)
    parser.add_argument('--stale-after-hours', type=float, default=DEFAULT_STALE_AFTER_HOURS)
    parser.add_argument('--now', default=None, help='override the clock for a dry run (ISO-8601)')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    public, root = Path(args.public), Path(args.root)
    try:
        manifest = json.loads((public / 'build-info.json').read_text())
    except (OSError, ValueError) as error:
        print(json.dumps({'publish': False, 'reason': 'no readable verified build: %s' % error}))
        return 0
    fresh = manifest.get('snapshot_generated_at')
    previous = committed_snapshot(root)
    now = moment(args.now) or datetime.now(timezone.utc)
    publish, reason = decide(fresh, previous, now,
                             cooldown_hours=args.cooldown_hours,
                             stale_after_hours=args.stale_after_hours)
    written = []
    if publish and not args.dry_run:
        written = stage_legacy.stage(public, root)
    print(json.dumps({'publish': publish, 'reason': reason, 'snapshot_generated_at': fresh,
                      'committed_snapshot': previous, 'files': written}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
