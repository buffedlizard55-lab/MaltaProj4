"""Book-listing identity/ambiguity regressions; all inputs here are synthetic.

No test pins the rotating live board or asserts that a test price is a real line.
The real STAVKA Nuxt replay is already covered in test_session_eaff7cce.py.
"""
import copy
import json
import unittest
from datetime import datetime, timezone

from scripts import books, core

NOW = datetime(2026, 10, 24, 17, tzinfo=timezone.utc)
START = '2026-10-25T17:00:00Z'
URL = 'https://egamersworld.com/counterstrike/match/test-only-50932f4d/synthetic'


def event(**changes):
    value = {'@type': 'SportsEvent', 'name': 'Alpha VS Bravo', 'startDate': START}
    value.update(changes)
    return value


def page(payload=None, widgets=None):
    payload = event() if payload is None else payload
    widgets = '<div>Alpha 1.5 Make a bet 3.0 Bravo</div>' if widgets is None else widgets
    return ('<html><head><script type="application/ld+json">' + json.dumps(payload)
            + '</script></head><body>' + widgets + '</body></html>')


def receipt():
    return {'provider': 'Synthetic listing', 'id': 'TEST_ONLY_50932F4D',
            'fixture_id': 'TEST_ONLY_50932F4D', 'source_teams': ['Alpha', 'Bravo'],
            'team_aliases': [['Alpha'], ['Bravo']], 'start': START,
            'odds': [1.6, 2.8], 'observed_at': '2026-10-23T00:00:00Z',
            'url': URL, 'api_url': URL}


def fixture():
    return {'id': 'TEST_ONLY_50932F4D', 'teams': ['Alpha', 'Bravo'],
            'state': 'open', 'start': START, 'lock': '2026-10-25T16:54:00Z',
            'source_url': 'https://play.hotspawn.com/cs2-pickems', 'best_of': None,
            'probabilities': None, 'fair_odds': None, 'pick': None, 'method': None,
            'evidence': [], 'attempts': [], 'flags': []}


class Source:
    def __init__(self, html, observed_at='2026-10-24T16:55:00Z'):
        self.html, self.observed_at = html, observed_at

    def get(self, name, url, as_json):
        return self.html, {'name': name, 'url': url, 'observed_at': self.observed_at}


class ListingEventIdentityTests(unittest.TestCase):
    def bound(self, html):
        return [r for r in books.parse_listing(html) if r.get('bound_to_labels')]

    def test_same_object_start_and_labels_are_accepted(self):
        found = self.bound(page())
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['odds'], [1.5, 3.0])
        self.assertEqual(found[0]['start'], START)

    def test_json_key_order_cannot_remove_a_real_pair(self):
        payload = {'startDate': START, 'description': 'x' * 800,
                   'name': 'Alpha VS Bravo', '@type': 'SportsEvent'}
        self.assertEqual(len(self.bound(page(payload))), 1)

    def test_cannot_borrow_start_from_a_different_json_object(self):
        payload = [{'@type': 'SportsEvent', 'name': 'Alpha VS Bravo'},
                   {'@type': 'SportsEvent', 'startDate': START, 'name': 'Other VS Rival'}]
        self.assertEqual(self.bound(page(payload)), [])

    def test_json_string_that_looks_like_an_event_is_not_an_event(self):
        html = '<div>"name":"Alpha VS Bravo","startDate":"' + START + '"</div>'
        html += '<div>Alpha 1.5 Make a bet 3.0 Bravo</div>'
        self.assertEqual(self.bound(html), [])

    def test_json_ld_graph_with_one_event_is_supported(self):
        payload = {'@context': 'https://schema.org',
                   '@graph': [{'@type': 'Organization', 'name': 'Example'}, event()]}
        found = self.bound(page(payload))
        self.assertEqual(len(found), 1)

    def test_duplicate_event_declarations_remain_ambiguous(self):
        self.assertEqual(self.bound(page([event(), event()])), [])

    def test_escaped_names_are_decoded_not_lost(self):
        payload = event(name='Grêmio VS Bravo')
        found = self.bound(page(payload, '<div>Grêmio 1.5 Make a bet 3.0 Bravo</div>'))
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['team1'], 'Grêmio')

    def test_two_distinct_events_cannot_share_unscoped_widget(self):
        for other in (event(startDate='2026-10-26T17:00:00Z'), event(name='Other VS Rival')):
            with self.subTest(other=other):
                self.assertEqual(self.bound(page([event(), other])), [])

    def test_event_identity_with_conflicting_home_away_labels_is_refused(self):
        payload = event(homeTeam={'name': 'Academy Alpha'}, awayTeam={'name': 'Bravo'})
        self.assertEqual(self.bound(page(payload)), [])

    def test_event_type_and_timezone_are_required_when_stated(self):
        for payload in (event(**{'@type': 'NewsArticle'}), event(startDate=START[:-1]),
                        event(name='Alpha VS Alpha')):
            with self.subTest(payload=payload):
                self.assertEqual(self.bound(page(payload)), [])

    def test_malformed_json_cannot_be_partially_salvaged(self):
        valid = page()
        for html in (valid.replace('"@type": "SportsEvent",', 'broken,'),
                     valid.replace('"startDate":', '"startDate":"2026-10-24T17:00:00Z","startDate":')):
            self.assertEqual(self.bound(html), [])


class ListingWidgetSelectionTests(unittest.TestCase):
    def renew(self, html, observed_at='2026-10-24T16:55:00Z'):
        original = receipt()
        before = copy.deepcopy(original)
        renewed, records = books.reobserve([original], Source(html, observed_at), NOW)
        self.assertEqual(original, before, 'Re-observation must never mutate the curated record')
        return renewed[0], records[0]

    def test_unrelated_first_widget_cannot_hide_later_verified_pair(self):
        html = page(widgets='<div>Other 1.8 Make a bet 2.1 Rival</div>'
                    + '<p>' + 'padding ' * 60 + '</p>'
                    + '<div>Alpha 1.5 Make a bet 3.0 Bravo</div>')
        renewed, record = self.renew(html)
        self.assertEqual(record['status'], 'renewed')
        self.assertEqual(renewed['odds'], [1.5, 3.0])
        row = fixture()
        core.book_research_pick(row, [renewed], NOW)
        self.assertEqual(row['pick'], 'Alpha')
        self.assertAlmostEqual(row['probabilities'][0], 2 / 3)

    def test_conflicting_bound_pairs_refuse_renewal_instead_of_picking_first(self):
        html = page(widgets='<div>Alpha 1.5 Make a bet 3.0 Bravo</div>'
                    + '<p>' + 'padding ' * 60 + '</p>'
                    + '<div>Alpha 2.5 Make a bet 1.6 Bravo</div>')
        renewed, record = self.renew(html)
        self.assertEqual(record['status'], 'parse_miss')
        self.assertEqual(renewed, receipt())
        self.assertIn('ambiguous', record['reason'].lower())

    def test_identical_mobile_and_desktop_widgets_are_one_quote(self):
        html = page(widgets='<div>Alpha 1.5 Make a bet 3.0 Bravo</div>' * 2)
        renewed, record = self.renew(html)
        self.assertEqual(record['status'], 'renewed')
        self.assertEqual(renewed['observed_at'], '2026-10-24T16:55:00Z')
        self.assertEqual(len(books.parse_listing(html)), 1)

    def test_gap_watcher_uses_same_unique_quote_rule(self):
        register = [{'fixture_id': 'TEST_ONLY_50932F4D', 'teams': ['Alpha', 'Bravo'], 'url': URL}]
        duplicate = page(widgets='<div>Alpha 1.5 Make a bet 3.0 Bravo</div>' * 2)
        found, records = books.watch_unpriced([], [fixture()], Source(duplicate), NOW, register)
        self.assertEqual(len(found), 1)
        self.assertEqual(records[0]['status'], 'resolved')
        conflicting = page(widgets='<div>Alpha 1.5 Make a bet 3.0 Bravo</div>'
                           + '<p>' + 'padding ' * 60 + '</p>'
                           + '<div>Alpha 2.5 Make a bet 1.6 Bravo</div>')
        found, records = books.watch_unpriced([], [fixture()], Source(conflicting), NOW, register)
        self.assertEqual(found, [])
        self.assertEqual(records[0]['status'], 'unresolved')

    def test_expired_missing_future_and_invalid_clock_never_renew(self):
        for observed in (None, 'invalid', '2026-10-24T09:00:00Z', '2026-10-25T09:00:00Z'):
            with self.subTest(observed=observed):
                renewed, record = self.renew(page(), observed)
                self.assertEqual(record['status'], 'error')
                self.assertEqual(renewed, receipt())

    def test_defaults_and_absent_second_label_stay_unpriced(self):
        for widget in ('Alpha 1.8 Make a bet 1.8 Bravo', 'Alpha 1.5 Make a bet 3.0',
                       'Alpha 1.0 Make a bet 12 Bravo'):
            with self.subTest(widget=widget):
                renewed, record = self.renew(page(widgets='<div>' + widget + '</div>'))
                self.assertEqual(record['status'], 'parse_miss')
                self.assertEqual(renewed, receipt())


if __name__ == '__main__':
    unittest.main()
