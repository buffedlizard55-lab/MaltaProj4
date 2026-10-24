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

Forwards in *source*, not only in data (session a30d31a0, 2026-10-24)
--------------------------------------------------------------------
A newer snapshot is not a newer build. Run ``40068512182`` built from
``dd92178`` (the merge of PR #246); while it ran, PR #245 merged as ``4a50ea4``
and changed ``site/assets/style.css``. The run's replay path re-staged its older
build over the newer ``origin/main`` and committed ``dce494b``: the snapshot
clock moved forwards, but the root stylesheet moved *backwards* to the
pre-#245 copy, ``site/assets`` and ``assets`` diverged, and seven unit tests went
red on ``main`` — the gate every scheduled refresh runs first. The rule below
therefore also refuses a build whose source revision differs from the checkout
it would be staged into in any path that can change a build. Generated root
outputs, ``COORDINATION.md``, ``README.md`` and ``research/**`` (which the build
links but never reads) are not build inputs. Each push to ``main`` runs this
workflow for its own revision, so a refused older build is always superseded by
the newer revision's own run; nothing is lost by refusing.
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import stage_legacy

DEFAULT_COOLDOWN_HOURS = 4.0
DEFAULT_STALE_AFTER_HOURS = 8.0
# Paths a newer commit may change without making an older build stale: the
# generated root outputs this module itself stages, plus documents and research
# receipts that scripts.build links to but never reads.
NON_SOURCE_FILES = frozenset(stage_legacy.ALLOWED | stage_legacy.EXTRA | {'COORDINATION.md', 'README.md'})
NON_SOURCE_PREFIXES = ('research/',)


def is_source_path(path):
    """True when a change to ``path`` can change what ``scripts.build`` produces."""
    path = str(path).strip()
    return bool(path) and path not in NON_SOURCE_FILES and not path.startswith(NON_SOURCE_PREFIXES)


def source_drift(revision, against='HEAD', root='.'):
    """Return the build-input paths that differ between ``revision`` and ``against``.

    Compares the two trees directly (``git diff --name-only``), so it needs both
    commit objects but no shared history and works in a shallow CI checkout.
    A root outside any git work tree has no committed source to roll back, so it
    reports no drift. Inside a work tree the check fails closed: a missing
    revision or an unreadable comparison is reported as a one-item drift list
    explaining why, never as "no drift".
    """
    try:
        inside = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=str(root),
                                capture_output=True, text=True, check=False)
    except OSError:
        return []
    if inside.returncode != 0 or inside.stdout.strip() != 'true':
        return []
    if not revision:
        return ['<the verified build records no source revision>']
    try:
        result = subprocess.run(['git', 'diff', '--name-only', str(revision), str(against), '--'],
                                cwd=str(root), capture_output=True, text=True, check=False)
    except OSError as error:
        return ['<git unavailable: %s>' % error]
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or '').strip().splitlines()
        return ['<cannot compare %s with %s: %s>' % (revision, against, detail[0] if detail else 'git diff failed')]
    return sorted(path for path in result.stdout.splitlines() if is_source_path(path))


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


# Assets that exist as two committed copies which must stay byte-identical.
# ``scripts/build.py`` copies ``ROOT/site/assets`` into ``public/assets``
# (``shutil.copytree(ROOT/'site/assets', out/'assets', dirs_exist_ok=True)``), so
# ``site/assets/*`` is the source and ``public/assets/*`` is a copy of it. But
# ``scripts.stage_legacy.ALLOWED`` stages ``assets/style.css`` and
# ``assets/app.js`` and deliberately does *not* stage ``site/assets/style.css``
# or ``site/assets/app.js``. Staging a ``public/`` tree that was built from a
# *different* source copy than the one currently committed therefore moves one
# half of the pair and leaves the other behind.
#
# Measured, not assumed: commit ``f54b37a`` ("Publish the verified build to the
# legacy main:/ root fallback", cs2-scout-publisher, 2026-10-24T06:02:34Z) did
# exactly that. Its parent ``dd92178`` (PR #246) carried 15 ``.exec-bar`` rules
# in both copies; ``f54b37a`` deleted 43 lines from ``assets/style.css``,
# reverting it to the ``60a150b`` (PR #240) content with zero ``.exec-bar``
# rules, while ``site/assets/style.css`` kept the newer copy. Five committed
# tests require the two copies to be byte-identical
# (``test_session_0cc1138a``, ``test_session_138cbedd``,
# ``test_session_5f1df842``, ``test_session_d2a55add``,
# ``test_session_dddcb90d``), so main went red, and because that suite runs
# *before* refresh/build/deploy in ``pages.yml`` the next scheduled publication
# was already deadlocked - the same shape as the 17.7-hour freeze this module's
# caller was racing to recover from.
PAIRED_ASSETS = ('assets/style.css', 'assets/app.js')


def asset_divergence(public, root):
    """The paired assets this build would move without moving their source.

    Pure and byte-exact: it compares the staged copy in ``public/`` with the
    committed source copy in ``root/site/``. A non-empty result means the
    ``public/`` tree was built from a different source than the one now
    committed, so staging it would break the identity the committed tests
    require. Empty means staging is safe.
    """
    diverged = []
    for relative in PAIRED_ASSETS:
        staged, source = Path(public) / relative, Path(root) / ('site/' + relative)
        if not staged.is_file() or not source.is_file():
            continue
        if staged.read_bytes() != source.read_bytes():
            diverged.append({'asset': relative, 'source': 'site/' + relative,
                             'staged_sha256': hashlib.sha256(staged.read_bytes()).hexdigest(),
                             'committed_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    return diverged


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--public', default='public')
    parser.add_argument('--root', default='.')
    parser.add_argument('--cooldown-hours', type=float, default=DEFAULT_COOLDOWN_HOURS)
    parser.add_argument('--stale-after-hours', type=float, default=DEFAULT_STALE_AFTER_HOURS)
    parser.add_argument('--now', default=None, help='override the clock for a dry run (ISO-8601)')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--check-drift', action='store_true',
                        help='only report whether the build revision is behind --against in a build input; '
                             'exit 0 when it is not, 3 when it is (or cannot be compared)')
    parser.add_argument('--revision', default=None,
                        help='source revision of the verified build (default: public/build-info.json)')
    parser.add_argument('--against', default='HEAD',
                        help='commit the build would be published on top of (default: HEAD of --root)')
    args = parser.parse_args(argv)
    public, root = Path(args.public), Path(args.root)
    try:
        manifest = json.loads((public / 'build-info.json').read_text())
    except (OSError, ValueError) as error:
        if args.check_drift and args.revision:
            manifest = {}
        else:
            print(json.dumps({'publish': False, 'reason': 'no readable verified build: %s' % error}))
            return 3 if args.check_drift else 0
    revision = args.revision or manifest.get('revision')
    drift = source_drift(revision, args.against, root)
    if args.check_drift:
        print(json.dumps({'revision': revision, 'against': args.against, 'source_drift': drift}))
        return 3 if drift else 0
    fresh = manifest.get('snapshot_generated_at')
    previous = committed_snapshot(root)
    now = moment(args.now) or datetime.now(timezone.utc)
    publish, reason = decide(fresh, previous, now,
                             cooldown_hours=args.cooldown_hours,
                             stale_after_hours=args.stale_after_hours)
    # Two independent guards against the same measured failure, both kept.
    # Session ea2e254c (PR #257) added source_drift: refuse when the build
    # revision is behind the checkout in any build input. Session 35c6e1e9 added
    # asset_divergence: refuse when the staged paired assets differ byte-for-byte
    # from the committed source copy they must stay identical to. The first is
    # general and revision-based; the second is specific and byte-exact, so it
    # still catches a divergence when the revision comparison cannot be made (no
    # readable manifest revision, a shallow clone, or a build staged by hand
    # through scripts.stage_legacy as this repair was). Neither replaces the
    # other; a build must pass both to be staged.
    if publish and drift:
        publish = False
        reason = ('the verified build was made from %s, but the checkout it would be staged into differs in '
                  '%d build input(s) (%s); staging it would roll newer source back, so the newer revision\'s '
                  'own run publishes the root instead' % (revision, len(drift), ', '.join(drift[:5])))
    diverged = asset_divergence(public, root) if publish else []
    if diverged:
        # Refuse, and say exactly which pair would break. This is the same
        # posture as every other refusal here: a normal exit with a
        # machine-readable reason, so the workflow logs why the root was left
        # alone instead of committing a tree its own tests reject.
        publish = False
        reason = ('refusing to stage a build whose %s differ from the committed source copy in '
                  'site/assets: staging would move one half of a pair the committed tests require to be '
                  'byte-identical (see commit f54b37a). Rebuild public/ from this commit first.'
                  % ', '.join(d['asset'] for d in diverged))
    written = []
    if publish and not args.dry_run:
        written = stage_legacy.stage(public, root)
    print(json.dumps({'publish': publish, 'reason': reason, 'snapshot_generated_at': fresh,
                      'committed_snapshot': previous, 'revision': revision, 'source_drift': drift,
                      'files': written, 'asset_divergence': diverged}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
