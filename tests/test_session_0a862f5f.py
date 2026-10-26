"""Session 0a862f5f: name the fixtures the lobby lists and the feed omits.

Measured, 2026-10-26
--------------------
* The published capture (`build-info.json`) read the official fixtures API at
  `2026-10-26T00:07:16Z`, held 73 CS2 rows, and was built at 00:10:50Z from
  revision `3b158a37`.
* The public lobby, read at 00:47Z, linked eight further CS2 fixtures that
  capture does not contain: 1079201 INOX Division vs Nemesis, 1081159 LFO 10 vs
  ex-6666, 1079202 FOKUS vs ex-Zero Tenacity, 1081160 HAVU vs ILLYRIANS, 1079203
  Metizport vs BRUTE, 1081162 ex-RUSTEC vs Spirit Academy, 1081163 BakS vs Saint
  Sinners, 1081164 Inner Circle Academy vs Lavked.
* The same feed read again at 00:57Z returned those rows interleaved with rows the
  00:07Z snapshot already held, so the likeliest cause is lazy publication by
  Hotspawn. That is recorded as an observation, never as a proven cause, and it
  is never used to justify inventing a start time or a probability.

What these tests pin
--------------------
1. The parser accepts exactly one Hotspawn match-permalink shape and nothing else,
   so a blocked or half-rendered page cannot masquerade as an empty lobby, and only
   the CS2 pick'em page may support a CS2 coverage claim (the general lobby has a
   sport switcher, so one of its anchors can name another game).
2. `compare` reports only lobby-not-in-feed ids, and a lobby read that produced no
   ids is reported as unread rather than as parity.
3. `scripts.inventory.discover` keeps the behaviour it had -- it does not invent a
   row for a lobby-only fixture -- and now also records the gap and names it in the
   snapshot's issue list with the lobby URL.
4. The rendered coverage block lists each missing id with both official sources,
   publishes no percentage for it, and renders nothing when the snapshot carries
   no coverage record (an older capture must not imply parity it never measured).
"""
import json
import unittest
from pathlib import Path

from scripts import build, lobby_gap
from scripts.core import FIXTURES, HOTSPAWN, dt, iso
from scripts.inventory import LOBBY, discover

ROOT = Path(__file__).resolve().parents[1]
NOW = dt('2026-10-26T00:07:00Z')
ROW = {'id': '900001', 'sport_alias': 'cs2', 'participants0_name': 'Alpha',
       'participants1_name': 'Beta', 'scheduled_start_time': '2026-10-26T12:00:00Z',
       'lock_time': '2026-10-26T11:54:00Z', 'status': 'scheduled'}

LOBBY_HTML = (
    '<a href="https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-2026-1082858">x</a>'
    '<a href="/matches/inox-division-vs-nemesis-nodwin-2026-1079201">x</a>'
    '<a href="https://play.hotspawn.com/matches/lfo-10-vs-ex-6666-cct-2026-1081159?tab=pick">x</a>'
    '<a href="https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-2026-1082858">x</a>'
    '<a href="https://example.com/matches/not-hotspawn-1099999">x</a>'
    '<a href="/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1">api</a>'
)


class ParserTests(unittest.TestCase):
    def test_extracts_hotspawn_match_permalinks_only(self):
        self.assertEqual(lobby_gap.ids_from_html(LOBBY_HTML),
                         ['1079201', '1081159', '1082858'])

    def test_non_string_and_empty_bodies_are_not_an_empty_lobby(self):
        for value in (None, '', 0, b'<a href="/matches/x-1082858">'):
            self.assertEqual(lobby_gap.ids_from_html(value), [])

    def test_compare_reports_only_ids_the_feed_did_not_return(self):
        result = lobby_gap.compare(['1082858', '900001'], ['1082858', '1079201', '1081159'])
        self.assertEqual(result['missing_from_feed'], ['1079201', '1081159'])
        self.assertEqual(result['missing_count'], 2)
        self.assertTrue(result['lobby_read'])
        self.assertEqual(result['feed_count'], 2)
        self.assertEqual(result['lobby_count'], 3)

    def test_compare_calls_an_id_less_lobby_unread_not_parity(self):
        result = lobby_gap.compare(['1082858'], [])
        self.assertFalse(result['lobby_read'])
        self.assertEqual(result['missing_count'], 0)

    def test_summary_sentence_names_the_ids_and_counts(self):
        text = lobby_gap.summary_gap(['1079201', '1081159'])
        self.assertIn('2 fixture(s)', text)
        self.assertIn('1079201', text)


class Sources:
    def __init__(self, responses, html=None):
        self.responses = responses
        self.html = html or {}
        self.log = []

    def get(self, name, url, as_json=True):
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        if as_json:
            payload = response
        else:
            payload = self.html.get(url, '<script id="ng-state">' + json.dumps(
                {'test': {'u': FIXTURES.split('?')[0], 'b': response}}) + '</script>')
        return payload, {'observed_at': iso(NOW), 'url': url}


class DiscoveryTests(unittest.TestCase):
    def sources(self, html=None):
        return Sources({FIXTURES: [ROW], HOTSPAWN: [ROW], LOBBY: [ROW]}, html)

    def test_lobby_only_fixture_is_recorded_and_named_but_never_invented(self):
        html = {CS2_PAGE: '<script id="ng-state">' + json.dumps(
            {'test': {'u': FIXTURES.split('?')[0], 'b': [ROW]}}) + '</script>'
            '<a href="/matches/inox-division-vs-nemesis-1079201">x</a>'
            '<a href="https://www.hotspawn.com/matches/alpha-vs-beta-900001">x</a>'}
        result = discover(self.sources(html), NOW)
        # The board still holds exactly the feed's own row: no synthetic fixture.
        self.assertEqual([m['id'] for m in result['matches']], ['900001'])
        self.assertEqual(result['lobby']['missing_from_feed'], ['1079201'])
        issue = next(i for i in result['flags'] if i['code'] == 'lobby_gap')
        self.assertIn('1079201', issue['message'])
        self.assertEqual(issue['source'], LOBBY)

    def test_no_gap_records_parity_without_an_issue(self):
        html = {CS2_PAGE: '<script id="ng-state">' + json.dumps(
            {'test': {'u': FIXTURES.split('?')[0], 'b': [ROW]}}) + '</script>'
            '<a href="https://www.hotspawn.com/matches/alpha-vs-beta-900001">x</a>'}
        result = discover(self.sources(html), NOW)
        self.assertEqual(result['lobby']['missing_from_feed'], [])
        self.assertFalse([i for i in result['flags'] if i['code'] == 'lobby_gap'])
        self.assertTrue(result['lobby']['lobby_read'])

    def test_general_lobby_links_never_claim_a_cs2_gap(self):
        # The general lobby carries a sport switcher, so only the CS2 pick'em page
        # may support a CS2 coverage claim. A non-CS2 permalink there is ignored.
        html = {CS2_PAGE: '<script id="ng-state">' + json.dumps(
            {'test': {'u': FIXTURES.split('?')[0], 'b': [ROW]}}) + '</script>',
            LOBBY: '<a href="/matches/some-lol-final-999888">x</a>'
                   '<a href="https://www.hotspawn.com/matches/alpha-vs-beta-900001">x</a>'}
        result = discover(self.sources(html), NOW)
        self.assertEqual(result['lobby']['missing_from_feed'], [])
        self.assertFalse(result['lobby']['lobby_read'])
        self.assertFalse([i for i in result['flags'] if i['code'] == 'lobby_gap'])

    def test_unreadable_cs2_page_is_reported_as_unread_not_as_parity(self):
        html = {LOBBY: '<a href="/matches/inox-division-vs-nemesis-1079201">x</a>'}
        result = discover(self.sources(html), NOW)
        self.assertFalse(result['lobby']['lobby_read'])
        self.assertEqual(result['lobby']['missing_from_feed'], [])


CS2_PAGE = HOTSPAWN


class RenderTests(unittest.TestCase):
    def snapshot(self, coverage=None):
        data = json.loads((ROOT / 'data' / 'latest.json').read_text())
        if coverage is not None:
            data['lobby_coverage'] = coverage
        return data

    def test_gap_rows_carry_both_official_sources_and_no_probability(self):
        data = self.snapshot({'feed_count': 73, 'lobby_count': 81, 'lobby_read': True,
                              'missing_from_feed': ['1079201', '1081159'],
                              'missing_count': 2, 'observed_at': '2026-10-26T00:07:16Z',
                              'note': 'Lobby-only fixtures are named, never priced.'})
        html = build.lobby_coverage_panel(data)
        self.assertIn('id="lobby-coverage"', html)
        self.assertIn('1079201', html)
        self.assertIn('1081159', html)
        self.assertIn('https://play.hotspawn.com/lobby', html)
        self.assertIn('api/v1/fixtures', html)
        self.assertIn('no pick', html)
        # A coverage record may never publish a percentage for a row it lacks.
        self.assertNotIn('%', html)

    def test_parity_is_stated_only_when_the_lobby_was_read(self):
        data = self.snapshot({'feed_count': 73, 'lobby_count': 73, 'lobby_read': True,
                              'missing_from_feed': [], 'missing_count': 0,
                              'observed_at': '2026-10-26T00:07:16Z', 'note': ''})
        self.assertIn('CS2 page and the feed agreed', build.lobby_coverage_panel(data))
        data = self.snapshot({'feed_count': 73, 'lobby_count': 0, 'lobby_read': False,
                              'missing_from_feed': [], 'missing_count': 0,
                              'observed_at': '2026-10-26T00:07:16Z', 'note': ''})
        html = build.lobby_coverage_panel(data)
        self.assertIn('parity is unverified', html)
        self.assertNotIn('CS2 page and the feed agreed', html)

    def test_older_capture_without_the_record_renders_nothing(self):
        # Session b964dffd (2026-10-26): fresh snapshots now always carry the
        # lobby_coverage record (first seen on the 2026-10-26T02:44Z refresh),
        # so "an older capture without the record" must be simulated by
        # removing the key; asserting against the live snapshot as-is made
        # this test fail the publisher's staged-root gate on every fresh board.
        data = self.snapshot()
        data.pop('lobby_coverage', None)
        self.assertEqual(build.lobby_coverage_panel(data), '')

    def test_the_published_snapshot_is_a_dated_observation(self):
        # The committed snapshot either carries a coverage record or predates the
        # check; either way every open row it publishes must still be sourced.
        data = json.loads((ROOT / 'data' / 'latest.json').read_text())
        if 'lobby_coverage' in data:
            self.assertIn('missing_from_feed', data['lobby_coverage'])
        for row in data['matches']:
            if row['state'] == 'open' and row.get('probabilities') is not None:
                self.assertTrue(row.get('evidence') or row.get('method') == 'model_vrs')
                self.assertTrue(row['source_url'].startswith('https://'))


if __name__ == '__main__':
    unittest.main()
