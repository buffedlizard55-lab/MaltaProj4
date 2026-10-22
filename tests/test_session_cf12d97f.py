"""Session cf12d97f regressions: the publication gate must not expire on the
wall clock, and every committed snapshot must be internally consistent.

Defect repaired here
---------------------
The scheduled publication stopped on 2026-10-22 (run 39731049149 failed at
*Unit and independent failure-mode tests*). The failing assertion was
``tests/test_session_bf09aa40.py``::

    validate_model_row(row, quote, datetime.now(timezone.utc))

``row`` is a **historical committed capture**
(``research/harvest-bf09aa40/snapshot.json``, observed 2026-10-21T21:18:58Z).
``scripts.validate.validate_model_row`` re-checks the eight-hour evidence
window against the ``now`` it is given, so measuring that dated capture
against the wall clock makes the test fail exactly eight hours after the
capture - and, because the test gate runs before the refresh, it blocks every
publication slot from 2026-10-22T05:18Z onward.

The repair measures the dated capture against **its own capture time**. The
freshness gate itself is untouched and still rejects a stale row; the tests
below prove both halves of that.
"""
import json
import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import validate, vrs_mirror
from scripts.core import dt
from scripts.validate import validate_model_row

ROOT = Path(__file__).resolve().parents[1]
HARVEST_SNAPSHOT = json.loads((ROOT / 'research/harvest-bf09aa40/snapshot.json').read_text())
RANKING_HTML = ROOT / 'research/harvest-76712ccc/HLTV_world_ranking.html'


class TestHistoricalSnapshotReplay(unittest.TestCase):
    """The dated harvest capture must replay at its own capture time."""

    def setUp(self):
        self.row = next(m for m in HARVEST_SNAPSHOT['matches'] if m['id'] == '1082858')
        self.quote = self.row['evidence'][0]

    def test_the_row_replays_against_the_snapshot_capture_time(self):
        validate_model_row(self.row, self.quote, dt(HARVEST_SNAPSHOT['generated_at']))

    def test_the_eight_hour_gate_is_still_real(self):
        # Nine hours after the capture the same row is stale, exactly as the
        # live pipeline requires. The repair removed the wall-clock coupling,
        # not the evidence window.
        with self.assertRaises(AssertionError) as caught:
            validate_model_row(self.row, self.quote,
                               dt(HARVEST_SNAPSHOT['generated_at']) + timedelta(hours=9))
        self.assertIn('eight hours', str(caught.exception))

    def test_the_repaired_test_no_longer_measures_a_dated_capture_against_the_clock(self):
        source = (ROOT / 'tests/test_session_bf09aa40.py').read_text()
        self.assertNotIn('validate_model_row(row, quote, datetime.now(timezone.utc))', source,
                         'a dated capture must never be replayed against the wall clock')

    def test_every_committed_snapshot_is_fresh_at_its_own_capture_time(self):
        # General invariant: a snapshot's own evidence must be inside the
        # eight-hour window measured from that snapshot's generation time.
        for path in sorted(ROOT.glob('research/**/snapshot.json')):
            try:
                snapshot = json.loads(path.read_text())
            except (ValueError, OSError):
                continue
            generated = snapshot.get('generated_at')
            if not generated:
                continue
            for row in snapshot.get('matches') or []:
                for quote in row.get('evidence') or []:
                    observed = quote.get('observed_at')
                    if not observed:
                        continue
                    age = (dt(generated) - dt(observed)).total_seconds()
                    self.assertLess(age, 8 * 3600,
                                     '%s: %s has evidence older than the window at capture time'
                                     % (path.relative_to(ROOT), row.get('id')))
                    self.assertGreater(age, -600,
                                       '%s: %s evidence is dated after its capture'
                                       % (path.relative_to(ROOT), row.get('id')))

    def test_the_committed_harvest_capture_still_carries_its_own_numbers(self):
        # Guard against "fixing" the failure by editing the published numbers.
        self.assertEqual(self.row['method'], 'model_vrs')
        self.assertEqual(self.row['pick'], 'Off Chops')
        self.assertAlmostEqual(sum(self.row['probabilities']), 1.0, places=12)
        self.assertEqual(self.quote['points'], [878, 971])
        self.assertEqual(self.quote['observed_at'], '2026-10-21T21:18:58.286925Z')
        self.assertEqual(HARVEST_SNAPSHOT['generated_at'], '2026-10-21T21:18:58.345679Z')
        self.assertLess((dt(HARVEST_SNAPSHOT['generated_at'])
                         - dt('2026-10-21T21:18:58.286925Z')).total_seconds(), 60)


class TestDatedValveRankingMirror(unittest.TestCase):
    """HLTV's dated Valve ranking, the fallback when the canonical URL is refused.

    HLTV answers the canonical ``/valve-ranking/teams`` path with HTTP 403 to
    this collector (measured, recorded in the refresh log), while the same view
    is also published with the ranking date in the path. The mirror tier now
    reads the dated form when the canonical form is refused, and it still fails
    closed: a page that does not parse as a complete dated Valve-points list
    produces no number, and every refusal is recorded.
    """

    def valve_view(self):
        """The retained HLTV page with its points label flipped to Valve's wording."""
        html = RANKING_HTML.read_text(encoding='utf-8', errors='replace')
        return re.sub(r'(<span class="gtSmartphone-only">\s*)HLTV(\s*</span>)', r'\1Valve\2', html)

    class Src:
        """A source that serves only the URLs it was given, and refuses the rest."""

        def __init__(self, pages, refused=()):
            self.pages = pages
            self.refused = set(refused)
            self.read = []

        def get(self, name, url, as_json=True, headers=None):
            self.read.append(url)
            if url in self.refused:
                raise ValueError('HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run.')
            if url not in self.pages:
                raise ValueError('Not found: ' + url)
            return self.pages[url], {'url': url, 'observed_at': '2026-10-22T02:00:00Z',
                                     'status': 'ok', 'http_status': 200, 'sha256': 'b' * 64}

    def test_dated_urls_cover_the_last_three_days_newest_first(self):
        now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)
        urls = vrs_mirror.dated_urls(now)
        self.assertEqual([
            'https://www.hltv.org/valve-ranking/teams/2026/october/22',
            'https://www.hltv.org/valve-ranking/teams/2026/october/21',
            'https://www.hltv.org/valve-ranking/teams/2026/october/20'], urls)

    def test_the_dated_view_is_used_when_the_canonical_url_is_refused(self):
        now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)
        dated = vrs_mirror.dated_urls(now)[0]
        src = self.Src({dated: self.valve_view()}, refused=[vrs_mirror.RANKING])
        standings, meta, problem = vrs_mirror.fetch(src, now)
        self.assertIsNone(problem)
        self.assertEqual(dated, meta['url'])
        self.assertEqual('2026-10-12', standings['as_of'])
        self.assertGreaterEqual(len(standings['teams']), 100)
        # The dated view is read first: the collector blocks a whole host for the
        # rest of the run once it has refused it repeatedly, so a canonical URL
        # that answers 403 would make every later HLTV read unreachable.
        self.assertEqual([dated], src.read)

    def test_a_blocked_host_does_not_hide_the_dated_view(self):
        """The collector blocks the host after a refused read; the dated view
        must therefore be asked for before the canonical URL."""
        now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)
        dated = vrs_mirror.dated_urls(now)[0]

        class BlockingSrc(self.Src):
            def get(self, name, url, as_json=True, headers=None):
                if self.read:
                    raise ValueError('Skipped after earlier access/rate restriction on this host: 403')
                return super().get(name, url, as_json, headers)

        src = BlockingSrc({dated: self.valve_view()}, refused=[vrs_mirror.RANKING])
        standings, meta, problem = vrs_mirror.fetch(src, now)
        self.assertIsNone(problem)
        self.assertEqual(dated, meta['url'])
        self.assertEqual([dated], src.read)

    def test_every_refusal_is_recorded_and_nothing_is_invented(self):
        now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)
        src = self.Src({}, refused=[vrs_mirror.RANKING] + vrs_mirror.dated_urls(now))
        standings, meta, problem = vrs_mirror.fetch(src, now)
        self.assertIsNone(standings)
        self.assertIsNone(meta)
        self.assertIn('unavailable', problem)
        for url in [vrs_mirror.RANKING] + vrs_mirror.dated_urls(now):
            self.assertIn(url, problem)
        self.assertIn('403', problem)

    def test_a_transport_error_is_recorded_not_raised(self):
        now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)

        class BrokenSrc(self.Src):
            def get(self, name, url, as_json=True, headers=None):
                raise RuntimeError('connection reset')

        standings, meta, problem = vrs_mirror.fetch(BrokenSrc({}), now)
        self.assertIsNone(standings)
        self.assertIsNone(meta)
        self.assertIn('read error', problem)

    def test_a_page_that_does_not_parse_is_a_miss_not_a_number(self):
        now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)
        dated = vrs_mirror.dated_urls(now)[0]
        src = self.Src({dated: '<html><body>not a ranking</body></html>'},
                       refused=[vrs_mirror.RANKING])
        standings, meta, problem = vrs_mirror.fetch(src, now)
        self.assertIsNone(standings)
        self.assertIsNone(meta)
        self.assertIn('parse miss', problem)

    def test_the_validator_accepts_the_dated_form_and_still_refuses_other_hosts(self):
        now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)
        standings = vrs_mirror.parse(self.valve_view())
        # Two clubs that the retained page lists, so a real mirror line is built.
        names = [row['name'] for row in standings['teams']]
        first, second = names[0], names[40]
        meta = {'url': 'https://www.hltv.org/valve-ranking/teams/2026/october/12',
                'observed_at': '2026-10-22T02:00:00Z', 'sha256': 'c' * 64,
                'as_of': standings['as_of'], 'heading': standings['heading'],
                'teams_count': len(standings['teams']), 'parsed_by': standings['parsed_by']}
        row = {'id': '999002', 'teams': [first, second], 'state': 'open', 'probabilities': None,
               'fair_odds': None, 'pick': None, 'method': None, 'evidence': [], 'attempts': [], 'flags': [],
               'start': '2026-10-23T10:00:00Z', 'lock': None, 'best_of': None, 'reason': None}
        official = {'file': 'standings_global_2026_10_05.md', 'commit': 'e' * 40, 'as_of': '2026-10-05'}
        vrs_mirror.apply(row, standings, meta, {}, official)
        self.assertEqual('model_vrs_mirror', row['method'])
        validate.validate_mirror_row(row, row['evidence'][0], now)
        quote = dict(row['evidence'][0])
        quote['url'] = quote['api_url'] = 'https://example.com/valve-ranking/teams'
        with self.assertRaises(AssertionError):
            validate.validate_mirror_row(row, quote, now)


class TestExecutiveSummaryCounts(unittest.TestCase):
    """Every number on the executive summary must be one live counter.

    The freshness strip used to print build-time totals as static text while
    the coverage card underneath printed live counters. One row that locked or
    started moved the card and left the strip behind, so the page contradicted
    itself (observed live: strip "34 open / 34 with a pick / 29 with a win
    probability" above card "33 open / 33 picks / 28 with a win
    probability"). The strip and the coverage notices now carry the same
    ``data-count`` spans, which is what ``assets/app.js`` rewrites.
    """

    def setUp(self):
        from scripts import build
        self.build = build

        def row(index, priced, pick=True):
            return {'id': str(index), 'teams': ['Alpha %d' % index, 'Bravo %d' % index],
                    'state': 'open', 'probabilities': [0.6, 0.4] if priced else None,
                    'fair_odds': [1.67, 2.5] if priced else None, 'pick': pick if pick else None,
                    'method': 'exchange' if priced else 'research_rank', 'evidence': [],
                    'attempts': [], 'flags': [], 'start': '2026-10-23T10:00:00Z', 'lock': None,
                    'best_of': 3, 'reason': None, 'source': None, 'sources': []}

        self.data = {
            'last_attempt_at': '2026-10-22T08:00:00Z',
            'matches': [row(1, True), row(2, True), row(3, False)],
        }
        self.strip = build.fresh_strip(self.data, [1, 2, 3], [1, 2], [1], [])
        self.card = build.coverage_now(self.data)

    def counts_in(self, html):
        """The number rendered inside each live counter of a block."""
        return re.findall(r'<span data-count="([a-z_]+)">(\d+)</span>', html)

    def test_the_strip_uses_live_counters(self):
        counters = dict(self.counts_in(self.strip))
        self.assertEqual({'open': '3', 'picked': '3', 'priced': '2', 'unresolved': '0'}, counters)

    def test_the_strip_has_no_static_totals_left(self):
        # The build-time numbers are still the fallback inside the spans; what
        # must not survive is a bare number in the surrounding prose.
        text = re.sub(r'<span data-count="[a-z_]+">\d+</span>', '', self.strip)
        self.assertNotRegex(text, r'>(\d+) open CS2 match')
        self.assertNotRegex(text, r'>(\d+) with a pick')
        self.assertNotRegex(text, r'>(\d+) with a win probability')

    def test_the_strip_and_the_card_agree_before_any_expiry(self):
        strip = dict(self.counts_in(self.strip))
        card = dict(self.counts_in(self.card))
        for key in ('open', 'picked', 'priced'):
            self.assertEqual(card[key], strip[key], 'the strip and the card disagree on %r' % key)

    def test_the_card_still_reports_its_own_counts(self):
        counters = dict(self.counts_in(self.card))
        self.assertIn('open', counters)
        self.assertIn('priced', counters)


class TestTlsFallbackNeverEscapes(unittest.TestCase):
    """The fingerprinted transport must not be able to abort a refresh.

    Measured on 2026-10-22: the unguarded curl_cffi refusal raised its own
    error type, which is not a ``requests`` exception, so it escaped the
    source layer and killed the refresh step (run 39750217188). The refusal
    has to end up as the same rate-limit decision the plain transport
    produces, and a broken fingerprinted transport has to fall back to the
    response the plain transport already got.
    """

    def setUp(self):
        from scripts import refresh
        self.refresh = refresh

    class Refused:
        status_code = 403
        headers = {}
        content = b''
        text = ''

        def raise_for_status(self):
            import requests
            raise requests.HTTPError('403 Client Error', response=self)

    class BrokenFingerprint:
        @staticmethod
        def get(*args, **kwargs):
            raise RuntimeError('curl_cffi transport failure')

    def test_a_failing_fingerprinted_transport_keeps_the_plain_decision(self):
        refresh = self.refresh
        original_get = refresh.requests.Session.get
        original_real = refresh._REAL_SESSION_GET
        original_cffi = refresh._cffi_requests
        refused = self.Refused
        refresh.requests.Session.get = lambda *a, **k: refused()
        refresh._REAL_SESSION_GET = refresh.requests.Session.get
        refresh._cffi_requests = self.BrokenFingerprint
        try:
            src = refresh.Sources(datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc))
            record = {'name': 'test', 'url': 'https://www.hltv.org/valve-ranking/teams'}
            with self.assertRaises(refresh.RateLimited):
                src._read(record, record['url'], False, None)
            self.assertIn('tls_fallback', record)
            self.assertTrue(str(record['tls_fallback']).startswith('failed:'))
        finally:
            refresh.requests.Session.get = original_get
            refresh._REAL_SESSION_GET = original_real
            refresh._cffi_requests = original_cffi

    def test_a_successful_fingerprinted_transport_is_used(self):
        refresh = self.refresh
        original_get = refresh.requests.Session.get
        original_real = refresh._REAL_SESSION_GET
        original_cffi = refresh._cffi_requests

        class Ok:
            status_code = 200
            headers = {'Age': '0'}
            content = b'<html>ok</html>'
            text = '<html>ok</html>'

            def raise_for_status(self):
                return None

        class Fingerprint:
            @staticmethod
            def get(*args, **kwargs):
                return Ok()

        refused = self.Refused
        refresh.requests.Session.get = lambda *a, **k: refused()
        refresh._REAL_SESSION_GET = refresh.requests.Session.get
        refresh._cffi_requests = Fingerprint
        try:
            src = refresh.Sources(datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc))
            record = {'name': 'test', 'url': 'https://www.hltv.org/valve-ranking/teams'}
            body, receipt = src._read(record, record['url'], False, None)
            self.assertEqual('<html>ok</html>', body)
            self.assertEqual('used', record['tls_fallback'])
        finally:
            refresh.requests.Session.get = original_get
            refresh._REAL_SESSION_GET = original_real
            refresh._cffi_requests = original_cffi


if __name__ == '__main__':
    unittest.main()
