"""Tests for the guarded legacy-root publication (scripts/publish_root_fallback.py).

The live site is served from the committed ``main:/`` root, so a wrong decision
here is visible to every visitor: either the board freezes at an old build (the
2026-10-21 three-day outage) or it is overwritten with an expired one. The rules
are pure and pinned here.
"""
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import publish_root_fallback as publish
from scripts import stage_legacy

NOW = datetime(2026, 10, 21, 21, 0, tzinfo=timezone.utc)


def stamp(hours_ago):
    return (NOW - timedelta(hours=hours_ago)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


class Decide(unittest.TestCase):
    def test_publishes_a_fresh_verified_build_over_an_old_committed_one(self):
        ok, reason = publish.decide(stamp(0.1), stamp(30), NOW)
        self.assertTrue(ok, reason)

    def test_publishes_when_nothing_is_committed_yet(self):
        ok, reason = publish.decide(stamp(0.1), None, NOW)
        self.assertTrue(ok, reason)

    def test_never_goes_backwards_to_an_older_snapshot(self):
        ok, reason = publish.decide(stamp(5), stamp(1), NOW)
        self.assertFalse(ok)
        self.assertIn('at least as new', reason)

    def test_refuses_an_identical_snapshot(self):
        ok, reason = publish.decide(stamp(1), stamp(1), NOW)
        self.assertFalse(ok)

    def test_refuses_to_promote_an_expired_build(self):
        ok, reason = publish.decide(stamp(9), stamp(40), NOW)
        self.assertFalse(ok)
        self.assertIn('evidence window', reason)

    def test_respects_the_four_hour_cooldown(self):
        ok, reason = publish.decide(stamp(0.1), stamp(2), NOW)
        self.assertFalse(ok)
        self.assertIn('cooldown', reason)

    def test_publishes_again_once_the_cooldown_expires(self):
        ok, reason = publish.decide(stamp(0.1), stamp(4.5), NOW)
        self.assertTrue(ok, reason)

    def test_refuses_a_build_without_a_readable_timestamp(self):
        for value in (None, '', 'not-a-timestamp'):
            ok, reason = publish.decide(value, stamp(30), NOW)
            self.assertFalse(ok, value)
            self.assertIn('no readable snapshot timestamp', reason)

    def test_unreadable_committed_snapshot_does_not_block_a_good_build(self):
        ok, reason = publish.decide(stamp(0.1), 'not-a-timestamp', NOW)
        self.assertTrue(ok, reason)


class Staging(unittest.TestCase):
    def build(self, root):
        """Write a tiny but manifest-complete public build into a temp directory."""
        public = Path(root) / 'public'
        manifest = {}
        for index, relative in enumerate(sorted(stage_legacy.ALLOWED | stage_legacy.EXTRA)):
            path = public / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            body = ('file %d %s\n' % (index, relative)).encode()
            path.write_bytes(body)
            if relative in stage_legacy.ALLOWED:
                manifest[relative] = hashlib.sha256(body).hexdigest()
        (public / 'build-info.json').write_text(json.dumps({
            'schema_version': 1, 'revision': 'deadbeef', 'built_at': stamp(0),
            'snapshot_generated_at': stamp(0), 'rows': 1, 'files': manifest}))
        return public

    def call(self, public, root):
        with contextlib.redirect_stdout(io.StringIO()):
            return publish.main(['--public', str(public), '--root', root, '--now', stamp(0)])

    def test_stages_only_the_allowlisted_verified_files(self):
        with tempfile.TemporaryDirectory() as root:
            public = self.build(root)
            written = stage_legacy.stage(public, root)
            self.assertEqual(sorted(written), sorted(stage_legacy.ALLOWED | stage_legacy.EXTRA))
            self.assertTrue((Path(root) / 'index.html').is_file())
            self.assertTrue((Path(root) / 'data/latest.json').is_file())
            self.assertTrue((Path(root) / '.nojekyll').is_file())

    def test_refuses_a_build_whose_bytes_do_not_match_its_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            public = self.build(root)
            (public / 'index.html').write_text('tampered')
            with self.assertRaises(AssertionError):
                stage_legacy.stage(public, root)

    def test_cli_skips_a_root_that_is_already_current(self):
        with tempfile.TemporaryDirectory() as root:
            public = self.build(root)
            self.assertEqual(self.call(public, root), 0)
            self.assertTrue((Path(root) / 'index.html').is_file())
            # A second run with the same build must not stage anything again.
            self.assertEqual(self.call(public, root), 0)
            manifest = json.loads((Path(root) / 'build-info.json').read_text())
            self.assertEqual(manifest['snapshot_generated_at'], stamp(0))

    def test_cli_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as root:
            public = self.build(root)
            with contextlib.redirect_stdout(io.StringIO()):
                publish.main(['--public', str(public), '--root', root, '--now', stamp(0), '--dry-run'])
            self.assertFalse((Path(root) / 'index.html').exists())


if __name__ == '__main__':
    unittest.main()
