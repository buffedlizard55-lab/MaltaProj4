"""Independent checks for the source-freshness and parity work (session 3c8d1136).

These tests are deliberately separate from `tests/` because another active session
(`2e920ea8`) claimed new files there. They cover three claims this session makes:

1. a cache-busting request argument is appended without altering the public URL's own
   query, and it is only ever *measured* - never asserted to work;
2. `summarise()` cannot report a successful cache bust without receipts saying so;
3. the parity report classifies fixtures only from provenance the snapshot carries, and
   never constructs a Hotspawn permalink that the snapshot does not contain.

Run: `python -m unittest discover -s verification-3c8d1136 -p 'test_*.py' -v`
"""
import datetime
import json
import unittest
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from scripts.cdn_probe_3c8d1136 import bust, ids_of, summarise, VIEWS
from scripts.core import FIXTURES, HOTSPAWN
from scripts.coverage_report_3c8d1136 import API, LOBBY, PAGE, markdown, report

SNAPSHOT = Path('data/latest.json')


def receipt(view, variant, age, ids, status='ok', sha=None):
    return {'view': view, 'variant': variant, 'cache_busted': variant != 'plain',
            'canonical_url': dict((v[0], v[2]) for v in VIEWS)[view],
            'url': 'https://example/%s?_cb=%s' % (view, variant), 'status': status,
            'age_seconds': age, 'cs2_ids': sorted(ids), 'bytes': 10,
            'sha256': sha or ('%s-%s' % (view, variant))}


class CacheBustUrlTests(unittest.TestCase):
    def test_existing_query_arguments_are_preserved_verbatim(self):
        target = bust(FIXTURES, 'abc123')
        pairs = parse_qsl(urlsplit(target).query)
        self.assertIn(('sport_alias', 'cs2'), pairs)
        self.assertIn(('status', 'scheduled'), pairs)
        self.assertIn(('tenantId', '1'), pairs)
        self.assertEqual(pairs[-1], ('_cb', 'abc123'))
        self.assertEqual(urlsplit(target).netloc, urlsplit(FIXTURES).netloc)
        self.assertEqual(urlsplit(target).path, urlsplit(FIXTURES).path)

    def test_query_free_url_gains_exactly_one_argument(self):
        for url in (HOTSPAWN, LOBBY):
            target = bust(url, 'tok')
            self.assertEqual(parse_qsl(urlsplit(target).query), [('_cb', 'tok')])
            self.assertEqual(target.split('?')[0], url)

    def test_distinct_tokens_produce_distinct_urls(self):
        self.assertNotEqual(bust(HOTSPAWN, 'a'), bust(HOTSPAWN, 'b'))

    def test_no_view_is_probed_without_a_plain_baseline(self):
        variants = [r[0] for r in VIEWS]
        self.assertEqual(variants, ['api', 'page', 'lobby'])
        self.assertEqual(FIXTURES, dict((v[0], v[2]) for v in VIEWS)['api'])


class IdParsingTests(unittest.TestCase):
    def test_only_cs2_rows_are_counted(self):
        self.assertEqual(ids_of([{'id': 1, 'sport_alias': 'cs2'}, {'id': 2, 'sport_alias': 'dota2'}], True), ['1'])

    def test_duplicate_ids_refuse_a_coverage_claim(self):
        with self.assertRaises(ValueError):
            ids_of([{'id': 1, 'sport_alias': 'cs2'}, {'id': 1, 'sport_alias': 'cs2'}], True)

    def test_a_non_list_payload_is_not_an_empty_lobby(self):
        with self.assertRaises(ValueError):
            ids_of({'id': 1}, True)

    def test_html_hydration_is_parsed_through_the_production_reader(self):
        html = ('<script id="ng-state">{"a":{"u":"https://x/api/v1/fixtures","b":'
                '[{"id":7,"sport_alias":"cs2"}]}}</script>')
        self.assertEqual(ids_of(html, False), ['7'])


class SummaryTests(unittest.TestCase):
    def test_effective_bust_requires_fresh_ages_on_both_html_views_and_parity(self):
        ids = ['1', '2']
        rows = [receipt('api', 'plain', None, ids), receipt('page', 'plain', 14241, ids[:1]),
                receipt('lobby', 'plain', 6251, ids[:1]),
                receipt('api', 'bust-a', 0, ids), receipt('page', 'bust-a', 0, ids),
                receipt('lobby', 'bust-a', 3, ids),
                receipt('api', 'bust-b', 0, ids), receipt('page', 'bust-b', 1, ids),
                receipt('lobby', 'bust-b', 0, ids)]
        summary = summarise(rows)
        self.assertTrue(summary['page']['cache_bust_effective'])
        self.assertTrue(summary['lobby']['cache_bust_effective'])
        self.assertTrue(summary['busted_parity'])
        self.assertFalse(summary['plain_parity'])
        self.assertEqual(summary['plain_api_only'], ['2'])
        self.assertIn('fresh copy', summary['conclusion'])

    def test_a_still_cached_view_is_never_reported_as_busted(self):
        ids = ['1', '2']
        # Same body hash as the plain request: the CDN answered with the same stored object.
        rows = [receipt('api', 'plain', None, ids), receipt('page', 'plain', 14241, ids, sha='page-body'),
                receipt('lobby', 'plain', 6251, ids, sha='lobby-body'),
                receipt('api', 'bust-a', 0, ids), receipt('page', 'bust-a', 14230, ids, sha='page-body'),
                receipt('lobby', 'bust-a', 6240, ids, sha='lobby-body'),
                receipt('api', 'bust-b', 0, ids), receipt('page', 'bust-b', 14200, ids, sha='page-body'),
                receipt('lobby', 'bust-b', 6200, ids, sha='lobby-body')]
        summary = summarise(rows)
        self.assertFalse(summary['page']['cache_bust_effective'])
        self.assertTrue(summary['page']['same_object_as_plain'])
        self.assertTrue(summary['lobby']['same_object_as_plain'])
        self.assertIn('did not measurably defeat', summary['conclusion'])

    def test_missing_receipts_never_produce_a_positive_claim(self):
        rows = [receipt('api', 'plain', None, ['1']), receipt('page', 'plain', 999, ['1'], status='error'),
                receipt('lobby', 'plain', 999, ['1'], status='error')]
        summary = summarise(rows)
        self.assertFalse(summary['page']['cache_bust_measured'])
        self.assertFalse(summary['page']['cache_bust_effective'])
        self.assertNotIn('plain_parity', summary)
        self.assertIn('did not measurably defeat', summary['conclusion'])

    def test_a_busted_response_with_no_age_header_is_not_called_fresh(self):
        ids = ['1']
        rows = [receipt('api', 'plain', None, ids), receipt('page', 'plain', 100, ids),
                receipt('lobby', 'plain', 100, ids),
                receipt('api', 'bust-a', 0, ids), receipt('page', 'bust-a', None, ids),
                receipt('lobby', 'bust-a', None, ids),
                receipt('api', 'bust-b', 0, ids), receipt('page', 'bust-b', None, ids),
                receipt('lobby', 'bust-b', None, ids)]
        summary = summarise(rows)
        self.assertFalse(summary['page']['cache_bust_effective'])
        self.assertFalse(summary['page']['cache_bust_measured'])


def snapshot(**overrides):
    base = {
        'generated_at': '2026-10-16T07:21:23Z', 'fixtures_observed_at': '2026-10-16T03:23:45Z',
        'built_at': '2026-10-16T07:24:04Z', 'coverage': 'partial',
        'coverage_counts': {'api': 2, 'page': 1, 'lobby': 1, 'retained': 3},
        'source_checks': [
            {'name': 'Hotspawn CS2 fixtures', 'url': API, 'http_status': 200, 'status': 'ok',
             'retrieved_at': '2026-10-16T07:21:05Z', 'observed_at': '2026-10-16T07:21:05Z',
             'cache_age_seconds': None},
            {'name': 'Hotspawn CS2 lobby', 'url': PAGE, 'http_status': 200, 'status': 'ok',
             'retrieved_at': '2026-10-16T07:21:06Z', 'observed_at': '2026-10-16T03:23:45Z',
             'cache_age_seconds': 14241}],
        'matches': [
            {'id': '1', 'state': 'open', 'pick': 'A', 'method': 'exchange', 'start': '2026-10-16T14:00:00Z',
             'lock': '2026-10-16T13:54:00Z', 'teams': ['A', 'B'], 'competition': 'TWC',
             'probabilities': [0.7, 0.3], 'expires_at': '2026-10-16T11:23:45Z',
             'source_url': 'https://www.hotspawn.com/matches/a-vs-b-1',
             'fixture_sources': [{'url': API}, {'url': PAGE}]},
            {'id': '2', 'state': 'open', 'pick': 'C', 'method': 'model_vrs', 'start': '2026-10-16T17:00:00Z',
             'lock': '2026-10-16T16:54:00Z', 'teams': ['C', 'D'], 'competition': 'TWC',
             'probabilities': [0.6, 0.4], 'expires_at': '2026-10-16T11:23:45Z',
             'fixture_sources': [{'url': API}]},
            {'id': '3', 'state': 'not_open', 'pick': None, 'method': None, 'teams': ['E', 'F'],
             'start': '2026-10-15T16:00:00Z', 'fixture_sources': [{'url': PAGE}, {'url': LOBBY}]},
            {'id': '4', 'state': 'open', 'pick': None, 'teams': ['G', 'H'], 'fixture_sources': []}],
        'issues': [{'code': 'coverage_difference', 'message': 'parity unverified', 'source': PAGE}]}
    base.update(overrides)
    return base


class CoverageReportTests(unittest.TestCase):
    def test_rows_are_classified_only_by_the_provenance_they_carry(self):
        rep = report(snapshot())
        self.assertEqual(rep['ids_per_source'], {'api': 2, 'page': 2, 'lobby': 1, 'retained': 0})
        self.assertFalse(rep['parity'])
        self.assertEqual([r['id'] for r in rep['api_only']], ['2'])
        self.assertEqual([r['id'] for r in rep['html_only']], ['3'])
        # Row 1 is attested by the API and the CS2 page but not by the general lobby,
        # so it - not row 3 - is the page/lobby difference. Classification follows the
        # receipts, not the fixture's own labels.
        self.assertEqual(rep['page_vs_lobby_symmetric_difference'], ['1'])

    def test_a_row_without_provenance_is_reported_not_guessed(self):
        rep = report(snapshot())
        self.assertEqual(rep['unattributable_rows'], ['4'])
        self.assertEqual(rep['open_rows'], 3)
        self.assertEqual(rep['open_rows_with_a_pick'], 2)
        self.assertEqual([r['id'] for r in rep['open_rows_without_a_pick']], ['4'])

    def test_markdown_links_only_urls_the_snapshot_contains(self):
        data = snapshot()
        data['matches'][1]['source_url'] = 'https://www.hotspawn.com/matches/c-vs-d-2'
        text = markdown(report(data))
        self.assertIn('https://www.hotspawn.com/matches/c-vs-d-2', text)
        # Row 1 carries a permalink but appears in no difference table, so it is not linked.
        self.assertNotIn('https://www.hotspawn.com/matches/a-vs-b-1', text)
        self.assertNotIn('play.hotspawn.com/match/', text)
        self.assertIn('Age', text)
        self.assertIn('14241', text)

    def test_empty_differences_are_stated_as_none(self):
        rep = report(snapshot(matches=[{'id': '1', 'state': 'open', 'pick': 'A', 'teams': ['A', 'B'],
                                        'fixture_sources': [{'url': API}, {'url': PAGE}, {'url': LOBBY}]}]))
        self.assertTrue(rep['parity'])
        self.assertIn('None.', markdown(rep))


class PublishedSnapshotCharacterisationTests(unittest.TestCase):
    """What the committed snapshot actually says - re-checked, not assumed."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SNAPSHOT.read_text())
        cls.rep = report(cls.data)

    def test_the_board_anchor_is_the_oldest_hotspawn_observation(self):
        hotspawn = [sc for sc in self.data['source_checks'] if 'Hotspawn' in str(sc.get('name'))
                    and sc.get('status') == 'ok']
        self.assertTrue(hotspawn)
        self.assertEqual(self.data['fixtures_observed_at'], min(sc['observed_at'] for sc in hotspawn))

    def test_a_cached_html_view_is_what_anchors_the_committed_snapshot(self):
        anchored = [sc for sc in self.data['source_checks']
                    if sc.get('observed_at') == self.data['fixtures_observed_at'] and 'Hotspawn' in str(sc.get('name'))]
        self.assertTrue(anchored, 'no Hotspawn receipt carries the anchor time')
        self.assertTrue(any((sc.get('cache_age_seconds') or 0) > 0 for sc in anchored),
                        'anchor came from a response with no CDN Age; re-measure before citing this defect')

    def test_parity_gap_arithmetic_is_consistent(self):
        counts = self.data['coverage_counts']
        self.assertEqual(counts['retained'], len(self.data['matches']))
        self.assertGreaterEqual(counts['api'], counts['page'])
        self.assertEqual(self.rep['ids_per_source']['api'], counts['api'])
        union = set()
        for match in self.data['matches']:
            union.add(str(match['id']))
        self.assertEqual(len(union), counts['retained'])

    def test_every_difference_row_is_named_with_its_pick_state(self):
        for row in self.rep['api_only'] + self.rep['html_only']:
            self.assertTrue(row['id'])
            self.assertIn(row['state'], ('open', 'not_open', None))
            if row['state'] == 'open':
                self.assertIsNotNone(row['start'])


if __name__ == '__main__':
    unittest.main()


class ApiRejectionTests(unittest.TestCase):
    """The fixtures API answered HTTP 400 to `_cb` in run 38869016384; the probe must say so."""

    def rows(self):
        ids = ['1', '2']
        rejected = receipt('api', 'bust-a', None, [], status='error')
        rejected['http_status'] = 400
        rejected2 = receipt('api', 'bust-b', None, [], status='error')
        rejected2['http_status'] = 400
        return [receipt('api', 'plain', None, ids), receipt('page', 'plain', 7620, ids[:1]),
                receipt('lobby', 'plain', 7620, ids[:1]),
                rejected, receipt('page', 'bust-a', 0, ids), receipt('lobby', 'bust-a', 0, ids),
                rejected2, receipt('page', 'bust-b', 0, ids), receipt('lobby', 'bust-b', 0, ids)]

    def test_the_rejection_is_recorded_and_the_fresh_api_is_used_as_the_reference(self):
        summary = summarise(self.rows())
        self.assertTrue(summary['api']['rejects_cache_bust_argument'])
        self.assertFalse(summary['page']['rejects_cache_bust_argument'])
        self.assertEqual(summary['api_reference'], 'api/plain')
        self.assertTrue(summary['html_cache_bust_effective'])
        self.assertTrue(summary['busted_parity'])
        self.assertEqual(summary['busted_api_only'], [])
        self.assertEqual(summary['busted_html_only'], [])
        self.assertIn('agreed on the CS2 fixture ID set', summary['conclusion'])
        self.assertFalse(summary['plain_parity'])
        self.assertEqual(summary['plain_html_only'], [])
        self.assertEqual(summary['plain_api_only'], ['2'])

    def test_fresh_html_without_any_usable_api_read_is_not_oversold(self):
        # Every API attempt failed (plain missing, both busted rejected with HTTP 400):
        # the HTML views are fresh, but parity cannot be claimed without a reference set.
        rows = [r for r in self.rows() if not (r['view'] == 'api' and r['variant'] == 'plain')]
        summary = summarise(rows)
        self.assertIsNone(summary['api_reference'])
        self.assertNotIn('busted_parity', summary)
        self.assertTrue(summary['html_cache_bust_effective'])
        self.assertIn('not established', summary['conclusion'])


class ProductionFetchTests(unittest.TestCase):
    """`scripts.refresh.Sources.get` must ask the CDN for a current copy, and fall back safely."""

    class Response:
        def __init__(self, status, body, headers):
            self.status_code = status
            self.content = body.encode()
            self.headers = headers
            self.text = body

        def raise_for_status(self):
            if self.status_code >= 400:
                raise ValueError('%d Client Error' % self.status_code)

        def json(self):
            return json.loads(self.text)

    class Session:
        def __init__(self, responses):
            self.responses = responses
            self.requested = []
            self.headers = {}

        def get(self, url, timeout=None, headers=None):
            self.requested.append(url)
            return self.responses[url.split('?')[-1] if False else url]

    def sources(self, responses):
        from scripts.refresh import Sources
        src = Sources(datetime.datetime(2026, 10, 16, 7, 44, tzinfo=datetime.timezone.utc))
        src.session = self.Session(responses)
        return src

    def test_html_lobby_view_is_requested_with_a_distinct_argument(self):
        from scripts.refresh import CACHE_BUST_ARGUMENT
        html = '<script id="ng-state">{"a":{"u":"https://x/api/v1/fixtures","b":[{"id":7,"sport_alias":"cs2"}]}}</script>'
        captured = {}

        class Recording(self.Session):
            def get(inner, url, timeout=None, headers=None):
                captured['url'] = url
                return ProductionFetchTests.Response(200, html, {'Age': '0', 'X-Cache': 'MISS'})

        src = self.sources({})
        src.session = Recording({})
        body, record = src.get('Hotspawn general lobby', LOBBY, False)
        self.assertEqual(record['url'], LOBBY, 'the published evidence link must stay canonical')
        self.assertIn(CACHE_BUST_ARGUMENT + '=', captured['url'])
        self.assertTrue(captured['url'].startswith(LOBBY + '?'))
        self.assertEqual(record['status'], 'ok')
        self.assertEqual(record['cache_age_seconds'], 0)
        self.assertEqual(record['cache_status'], 'MISS')
        self.assertTrue(record['request_url'].startswith(LOBBY))
        self.assertEqual(body.count('ng-state'), 1)

    def test_a_source_that_rejects_the_argument_is_still_read_plain(self):
        html = '<script id="ng-state">{"a":{"u":"https://x/api/v1/fixtures","b":[{"id":7,"sport_alias":"cs2"}]}}</script>'
        responses = {}

        class Rejecting(self.Session):
            calls = []

            def get(inner, url, timeout=None, headers=None):
                Rejecting.calls.append(url)
                if '_cb=' in url:
                    return ProductionFetchTests.Response(400, 'bad request', {})
                return ProductionFetchTests.Response(200, html, {'Age': '7620', 'X-Cache': 'HIT'})

        src = self.sources(responses)
        src.session = Rejecting(responses)
        _body, record = src.get('Hotspawn general lobby', LOBBY, False)
        self.assertEqual(Rejecting.calls[0].split('?')[0], LOBBY)
        self.assertIn('_cb=', Rejecting.calls[0])
        self.assertEqual(Rejecting.calls[1], LOBBY, 'the retry must use the canonical URL')
        self.assertEqual(record['status'], 'ok')
        self.assertEqual(record['url'], LOBBY)
        self.assertEqual(record['request_url'], LOBBY)
        self.assertIsNone(record['cache_bust'])
        self.assertEqual(record['cache_age_seconds'], 7620)

    def test_json_apis_and_other_hosts_are_never_cache_busted(self):
        src = self.sources({})
        for url, as_json in ((FIXTURES, True), ('https://www.hltv.org/matches', False),
                             ('https://gamma-api.polymarket.com/sports', True),
                             ('https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups', True)):
            self.assertFalse(src.bustable(url, as_json), url)
        self.assertTrue(src.bustable(HOTSPAWN, False))
        self.assertTrue(src.bustable(LOBBY, False))
        self.assertFalse(src.bustable(HOTSPAWN, True))
