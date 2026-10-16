"""Deploy-receipt polling (session 9a81b26f).

Regression target: run 38936303441 (2026-10-16) deployed successfully but
the old one-shot verifier read the previous deployment's bytes in the same
second the deploy ended and failed the run. The verifier must now wait for
propagation -- while still failing closed on an older build, a torn file
set, or garbage. All fetches/sleeps/clocks are fakes; no network, no waits.
"""
import hashlib
import json
import unittest

from scripts import verify_live


def manifest(built_at, files=None, revision='abc123', rows=83):
    body = {'revision': revision, 'built_at': built_at, 'rows': rows,
            'files': files if files is not None else {}}
    return json.dumps(body).encode(), body


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class AssessTest(unittest.TestCase):
    def test_exact_manifest_matches(self):
        raw, _ = manifest('2026-10-16T17:00:47Z')
        verdict, live = verify_live.assess(raw, sha(raw), '2026-10-16T17:00:47Z')
        self.assertEqual(verdict, verify_live.MATCH)
        self.assertEqual(live['revision'], 'abc123')

    def test_newer_build_is_superseded(self):
        raw, _ = manifest('2026-10-16T18:00:00Z')
        verdict, _ = verify_live.assess(raw, 'different', '2026-10-16T17:00:47Z')
        self.assertEqual(verdict, verify_live.SUPERSEDED)

    def test_older_build_is_older(self):
        raw, _ = manifest('2026-10-16T12:00:00Z')
        verdict, _ = verify_live.assess(raw, 'different', '2026-10-16T17:00:47Z')
        self.assertEqual(verdict, verify_live.OLDER)

    def test_garbage_is_invalid_never_an_exception(self):
        for raw in (b'not json', b'[]', b'{"files": "nope"}', b'', None):
            verdict, live = verify_live.assess(raw, 'x', '2026-10-16T17:00:47Z')
            self.assertEqual(verdict, verify_live.INVALID, raw)
            self.assertIsNone(live)

    def test_missing_built_at_cannot_supersede(self):
        raw, _ = manifest('')
        verdict, _ = verify_live.assess(raw, 'different', '2026-10-16T17:00:47Z')
        self.assertEqual(verdict, verify_live.OLDER)


class VerifyPollingTest(unittest.TestCase):
    OURS = '2026-10-16T17:00:47Z'

    def run_verify(self, fetch, deadline=360, interval=15):
        clock = FakeClock()
        return verify_live.verify(
            'https://example.invalid/site/', self._sha, self.OURS, 'run1',
            deadline_seconds=deadline, interval_seconds=interval,
            fetch=fetch, sleep=clock.sleep, clock=clock, log=lambda *a: None)

    def setUp(self):
        self.page = b'<html>ok</html>'
        files = {'index.html': sha(self.page)}
        self.raw, _ = manifest(self.OURS, files=files)
        # build-info.json must hash to MANIFEST_SHA; files dict is inside it,
        # so compute the manifest sha from the exact bytes we will serve.
        self._sha = sha(self.raw)
        self.old_raw, _ = manifest('2026-10-16T12:00:00Z', files=files,
                                    revision='old999')

    def test_waits_for_propagation_then_verifies(self):
        # The 38936303441 shape: previous build first, ours a poll later.
        calls = {'build-info.json': 0}

        def fetch(url):
            if 'build-info.json' in url:
                calls['build-info.json'] += 1
                return self.old_raw if calls['build-info.json'] < 3 else self.raw
            return self.page

        receipt = self.run_verify(fetch)
        self.assertTrue(receipt['verified'])
        self.assertTrue(receipt['bytes_match_this_build'])
        self.assertEqual(receipt['attempts'], 3)
        self.assertEqual(receipt['mismatched'], [])

    def test_older_build_forever_fails_closed(self):
        def fetch(url):
            return self.old_raw if 'build-info.json' in url else self.page

        receipt = self.run_verify(fetch, deadline=30, interval=15)
        self.assertFalse(receipt['verified'])
        self.assertEqual(receipt['verdict'], verify_live.OLDER)

    def test_torn_file_set_fails_closed(self):
        def fetch(url):
            return self.raw if 'build-info.json' in url else b'stale page'

        receipt = self.run_verify(fetch, deadline=30, interval=15)
        self.assertFalse(receipt['verified'])
        self.assertEqual(receipt['mismatched'], ['index.html'])

    def test_file_propagating_late_still_verifies(self):
        state = {'page_calls': 0}

        def fetch(url):
            if 'build-info.json' in url:
                return self.raw
            state['page_calls'] += 1
            return b'stale page' if state['page_calls'] < 2 else self.page

        receipt = self.run_verify(fetch)
        self.assertTrue(receipt['verified'])
        self.assertEqual(receipt['attempts'], 2)

    def test_superseded_requires_byte_consistent_newer_build(self):
        newer_raw, _ = manifest('2026-10-16T18:00:00Z',
                                 files={'index.html': sha(self.page)},
                                 revision='newer42')

        def fetch(url):
            return newer_raw if 'build-info.json' in url else self.page

        receipt = self.run_verify(fetch)
        self.assertTrue(receipt['verified'])
        self.assertTrue(receipt['superseded_by_newer_build'])
        self.assertFalse(receipt['bytes_match_this_build'])

    def test_fetch_errors_are_polled_not_fatal(self):
        state = {'n': 0}

        def fetch(url):
            state['n'] += 1
            if state['n'] == 1:
                raise OSError('connection reset')
            return self.raw if 'build-info.json' in url else self.page

        receipt = self.run_verify(fetch)
        self.assertTrue(receipt['verified'])


if __name__ == '__main__':
    unittest.main()
