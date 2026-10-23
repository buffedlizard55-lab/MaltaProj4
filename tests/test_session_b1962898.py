"""Regression tests for session b1962898.

Covers the two things this session changed:

* the independent row audit (``scripts/audit_b1962898.py``) must catch every
  corruption it claims to catch, and must not fire on a correct row whose
  operator lists its outcomes in the opposite order to Hotspawn;
* the published freshness clock must not print a build-time "next slot" that is
  already in the past, and the schedule disclosure must be derived from the
  committed run-history measurement rather than typed by hand.
"""
import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import audit_b1962898, build

ROOT = Path(__file__).resolve().parents[1]
OBSERVED = '2026-10-23T08:29:19.125787Z'


def exchange_row(**overrides):
    """A correct exchange row whose operator order is the reverse of Hotspawn's."""
    row = {
        'id': '999001',
        'teams': ['BakS', 'BRUTE'],
        'state': 'open',
        'method': 'exchange',
        'pick': 'BRUTE',
        'probabilities': [0.495, 0.505],
        'fair_odds': [1 / 0.495, 1 / 0.505],
        'start': '2026-10-23T17:00:00Z',
        'lock': '2026-10-23T16:54:00Z',
        # Eight hours after the recorded observation, which is earlier than both
        # the lock and the start: the real rows behave exactly like this.
        'expires_at': '2026-10-23T16:29:19Z',
        'source_url': 'https://www.hotspawn.com/matches/brute-vs-baks-999001',
        'evidence': [{
            'provider': 'Polymarket',
            'url': 'https://polymarket.com/event/cs2-brute-baks-2026-10-23',
            'api_url': 'https://gamma-api.polymarket.com/markets/6035008',
            'observed_at': OBSERVED,
            'raw': {'outcomes': '["Brute", "BakS eSports"]', 'outcomePrices': '["0.505", "0.495"]'},
        }],
    }
    row.update(overrides)
    return row


class AuditRowTests(unittest.TestCase):
    def failures(self, row):
        problems = []
        audit_b1962898.audit_row(row, problems)
        return [p['code'] for p in problems]

    def test_correct_row_passes_even_when_operator_order_differs(self):
        self.assertEqual(self.failures(exchange_row()), [])

    def test_probability_sum_is_checked(self):
        codes = self.failures(exchange_row(probabilities=[0.6, 0.5], fair_odds=[1 / 0.6, 1 / 0.5]))
        self.assertIn('probability-sum', codes)

    def test_raw_outcome_prices_must_reproduce_the_published_pair(self):
        row = exchange_row(probabilities=[0.7, 0.3], fair_odds=[1 / 0.7, 1 / 0.3], pick='BakS')
        self.assertIn('raw-price', self.failures(row))

    def test_pick_must_be_the_higher_probability_team(self):
        self.assertIn('pick-direction', self.failures(exchange_row(pick='BakS')))

    def test_pick_must_be_one_of_the_two_teams(self):
        self.assertIn('pick-identity', self.failures(exchange_row(pick='Some Other Team')))

    def test_expiry_may_not_exceed_the_match_start(self):
        codes = self.failures(exchange_row(expires_at='2026-10-23T18:00:00Z'))
        self.assertIn('expiry', codes)

    def test_expiry_may_not_exceed_the_eight_hour_evidence_window(self):
        late = (datetime.fromisoformat(OBSERVED.replace('Z', '+00:00')) + timedelta(hours=9))
        row = exchange_row(start='2026-10-24T09:00:00Z', lock='2026-10-24T08:54:00Z',
                           expires_at=late.isoformat().replace('+00:00', 'Z'))
        self.assertIn('expiry', self.failures(row))

    def test_priced_row_must_cite_a_non_hotspawn_source(self):
        row = exchange_row()
        row['evidence'] = []
        self.assertIn('external-source', self.failures(row))

    def test_model_row_must_cite_official_valve_or_hltv(self):
        row = exchange_row(method='model_vrs',
                           evidence=[{'provider': 'Valve VRS model', 'url': 'https://example.com/model',
                                      'observed_at': OBSERVED}])
        self.assertIn('model-source', self.failures(row))
        row['evidence'][0]['url'] = ('https://github.com/ValveSoftware/counter-strike_regional_standings/'
                                     'blob/eec4853/live/2026/standings_global_2026_10_05.md')
        self.assertEqual(self.failures(row), [])

    def test_research_tier_must_not_publish_a_probability(self):
        codes = self.failures(exchange_row(method='research_rank'))
        self.assertIn('tier-probability', codes)

    def test_research_row_without_percentage_needs_a_reason_and_an_attempt(self):
        row = exchange_row(method='research_rank', probabilities=None, fair_odds=None,
                           expires_at=None, evidence=[], reason='')
        codes = self.failures(row)
        self.assertIn('reason', codes)
        self.assertIn('attempts', codes)

    def test_open_row_without_pick_needs_a_reason(self):
        codes = self.failures(exchange_row(method=None, probabilities=None, fair_odds=None,
                                           expires_at=None, pick=None, evidence=[], reason=''))
        self.assertIn('reason', codes)

    def test_inventory_view_disagreement_is_reported(self):
        result = audit_b1962898.audit({'matches': [exchange_row()],
                                       'coverage_counts': {'api': 1, 'page': 1, 'lobby': 2, 'retained': 1}})
        self.assertIn('view-parity', [p['code'] for p in result['problems']])

    def test_retained_count_must_match_the_row_count(self):
        result = audit_b1962898.audit({'matches': [exchange_row()],
                                       'coverage_counts': {'api': 2, 'page': 2, 'lobby': 2, 'retained': 2}})
        self.assertIn('row-count', [p['code'] for p in result['problems']])

    def test_committed_board_passes_the_independent_audit(self):
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        result = audit_b1962898.audit(snapshot)
        self.assertEqual(result['problems'], [], result['problems'])
        self.assertEqual(result['summary']['rows'], len(snapshot['matches']))
        self.assertEqual(result['summary']['picked'],
                         result['summary']['priced'] + result['summary']['research_only'])
        self.assertGreater(result['summary']['checks_run'], result['summary']['rows'])


class FreshnessClockTests(unittest.TestCase):
    """The freshness clock must be the browser's, not the build's.

    Session 138cbedd landed the same repair on main while this branch was open;
    these assertions therefore pin the *combined* contract rather than a second
    implementation: one clock element, one slot list, and the browser recomputing
    both from the reader's clock.
    """

    def strip(self):
        snapshot = '2026-10-23T08:29:19.125787Z'
        row = 'row'
        return BeautifulSoup(build.fresh_strip(
            {'last_attempt_at': snapshot, 'fixtures_observed_at': snapshot, 'built_at': snapshot},
            [row, row], [row], [], []), 'html.parser').select_one('#freshness-strip')

    def test_strip_publishes_the_slot_list_for_the_live_clock(self):
        strip = self.strip()
        schedule = strip.select_one('[data-slot-minutes]')
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule['data-slot-minutes'], ','.join(str(x) for x in build.SLOT_MINUTES))
        self.assertIn(':04, :19, :34 and :49', strip.get_text(' ', strip=True))

    def test_strip_has_exactly_one_live_age_element(self):
        ages = self.strip().select('.fresh-age')
        self.assertEqual(len(ages), 1)
        self.assertEqual(ages[0].get('id'), 'fresh-age')
        self.assertEqual(ages[0].get_text(), '', 'the build must not bake an age into the page')

    def test_browser_script_recomputes_slot_and_age_from_the_readers_clock(self):
        script = (ROOT / 'assets' / 'app.js').read_text()
        legacy = (ROOT / 'site' / 'assets' / 'app.js').read_text()
        self.assertEqual(script, legacy, 'both copies of app.js must stay byte-identical')
        self.assertIn("querySelector('#next-slot')", script)
        self.assertIn("querySelector('#fresh-age')", script)
        self.assertIn('dataset.slotMinutes', script)

    def test_slot_minutes_match_the_workflow_cron(self):
        workflow = (ROOT / '.github' / 'workflows' / 'pages.yml').read_text()
        self.assertIn("cron: '%s * * * *'" % ','.join(str(x) for x in build.SLOT_MINUTES), workflow)


class ScheduleDisclosureTests(unittest.TestCase):
    def test_measurement_is_read_from_the_committed_capture(self):
        measured = build.schedule_delivery()
        self.assertIsNotNone(measured)
        record = json.loads((ROOT / 'research' / 'session-b1962898' / 'run-delivery.json').read_text())
        self.assertEqual(measured['scheduled'], record['counts']['schedule'])
        self.assertEqual(measured['pushes'], record['counts']['push'])
        self.assertGreater(measured['hours'], 0)
        self.assertEqual(measured['pages'] + measured['watchdog'], measured['scheduled'])

    def test_disclosure_states_the_measured_rate(self):
        measured = build.schedule_delivery()
        text = build.schedule_disclosure(measured)
        self.assertIn('Measured delivery', text)
        self.assertIn(str(measured['scheduled']), text)
        self.assertIn('run history', text)

    def test_disclosure_degrades_without_the_measurement(self):
        self.assertIn('no exact delivery guarantee', build.schedule_disclosure(None))

    def test_sources_page_publishes_the_disclosure(self):
        # Rendered here rather than read from public/, which is a gitignored build
        # output: the unit step runs on a clean checkout before any build.
        data = json.loads((ROOT / 'data' / 'latest.json').read_text())
        page = BeautifulSoup(build.methodology(data), 'html.parser')
        text = page.get_text(' ', strip=True)
        self.assertIn('Measured delivery, not just intent', text)
        self.assertIn('Freshness therefore depends on commits as well as cron', text)
        self.assertIn('run history', text)


if __name__ == '__main__':
    unittest.main()
