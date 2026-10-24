"""Session 0cc1138a: independent re-derivation of every pick, both-team phone
cards, and the executive summary's unresolved/limitations section.

What this session had to prove, and how it is proven here
--------------------------------------------------------
1. Every published pick and percentage can be rebuilt from its archived primary
   evidence by code that shares nothing with the pipeline. ``verify_0cc1138a``
   is that independent re-derivation (exchange mid, book de-vig, Valve's own
   Glicko expectation with Valve's published calibration), and it is replayed
   here against the committed snapshot and against deliberately corrupted copies.
2. A phone card states *both* teams' win chances and makes our pick obvious,
   including after the price expires (the opponent's number is withdrawn too).
3. The executive summary carries a separate unresolved-picks section with the
   limitations for generating a pick, counted from the snapshot's own recorded
   attempts rather than hand-written.
4. Live Hotspawn coverage: the exact fixture set observed on the public lobby on
   2026-10-23 is the set in the board (see research/session-0cc1138a/REPORT.md).
"""
import copy
import importlib.util
from datetime import datetime
import json
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.build import glance, overview, unresolved_limits_card

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
# Rendered from the committed snapshot, so this suite never depends on whether a
# local build has already written public/ (CI runs the unit suite before build).
INDEX = overview(copy.deepcopy(SNAPSHOT))
CSS = (ROOT / 'site' / 'assets' / 'style.css').read_text()
APP = (ROOT / 'site' / 'assets' / 'app.js').read_text()


def load_verifier():
    spec = importlib.util.spec_from_file_location(
        'verify_0cc1138a', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_verifier()


def open_rows():
    return [m for m in SNAPSHOT['matches'] if m['state'] == 'open']


class IndependentReDerivation(unittest.TestCase):
    def test_every_committed_open_row_reproduces_with_no_shared_code(self):
        rows = V.audit(SNAPSHOT)
        self.assertEqual(len(rows), len(open_rows()))
        failures = [r for r in rows if r['problems']]
        self.assertEqual(failures, [], 'unreproducible: %r' % failures[:3])
        self.assertTrue(all(r['re_derived'] for r in rows if r['published']))

    def test_every_pick_is_the_larger_re_derived_probability(self):
        for r in V.audit(SNAPSHOT):
            if not r['published']:
                continue
            p = r['re_derived']
            self.assertEqual(r['pick'], r['teams'][p.index(max(p))], r['id'])

    def test_a_tampered_percentage_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['method'] == 'exchange')
        row['probabilities'] = [row['probabilities'][1], row['probabilities'][0]]
        row['pick'] = row['teams'][0]
        failures = [r for r in V.audit(doc) if r['problems']]
        self.assertTrue(failures, 'reversed prices must not pass')
        blob = ' '.join(failures[0]['problems'])
        self.assertIn('re-derived', blob)

    def test_a_tampered_pick_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
        row['pick'] = row['teams'][1 - row['teams'].index(row['pick'])]
        failures = [r for r in V.audit(doc) if r['problems']]
        self.assertEqual(len(failures), 1)
        self.assertIn('not the larger probability', ' '.join(failures[0]['problems']))

    def test_a_missing_source_link_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['evidence'])
        row['source_url'] = 'http://insecure.example/row'
        failures = [r for r in V.audit(doc) if r['problems']]
        self.assertTrue(failures)
        self.assertIn('non-https', ' '.join(failures[0]['problems']))

    def test_valve_expectation_matches_valve_published_calibration(self):
        # modelfit.png in Valve's repository: observed = 0.7986 * expected + 0.126.
        self.assertAlmostEqual(V.calibrate(0.5), 0.5, places=12)
        self.assertAlmostEqual(V.calibrate(0.0), 0.5 - 0.7986 / 2, places=12)
        self.assertAlmostEqual(V.calibrate(1.0), 0.5 + 0.7986 / 2, places=12)
        # Equal points must be a coin flip, and the function must be antisymmetric.
        self.assertAlmostEqual(V.glicko_expect(1000, 1000), 0.5, places=12)
        self.assertAlmostEqual(V.glicko_expect(1200, 1000) + V.glicko_expect(1000, 1200), 1.0, places=12)

    def test_team_labels_map_onto_the_fixture_order(self):
        # An exchange listing the fixture in the opposite order must not flip the pick.
        self.assertEqual(V.order_prices(['Beta', 'Alpha'], [0.3, 0.7], ['Alpha', 'Beta']), [0.7, 0.3])
        self.assertEqual(V.order_prices(['BakS eSports', 'Brute'], [0.4, 0.6], ['BakS', 'BRUTE']), [0.4, 0.6])
        self.assertEqual(V.order_prices(['ALKA', 'Los Ni\u00f1os'], [0.7, 0.3], ['Alka', 'LOS NINOS']), [0.7, 0.3])
        with self.assertRaises(ValueError):
            V.order_prices(['Alpha', 'Alpha'], [0.5, 0.5], ['Alpha', 'Beta'])

    def test_renamed_team_maps_only_through_a_sourced_alias(self):
        # Fixture 1083121 (2026-10-24): Hotspawn "Projeto do KinGui" is priced
        # under Polymarket's "Tropa do KinGui". The names do not fuzzy-match, so
        # without a documented identity the independent verifier must refuse.
        # The merged verifier (PR #251 / 174afa4f) accepts the evidence dict and
        # reads the reviewed identity_sources carried on that record itself.
        labels = ['Tropa do KinGui', 'MEIA NOITE']
        teams = ['Projeto do KinGui', 'MEIA NOITE']
        with self.assertRaises(ValueError):
            V.order_prices(labels, [0.615, 0.385], teams)
        sourced_ev = {'identity_sources': [
            {'names': ['Tropa do KinGui', 'Projeto do KinGui', 'ex-Keyd Stars'],
             'source': 'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7',
             'basis': 'Fixture parity and Valve four-player roster-continuity rule, checked 22 Oct 2026.'}]}
        self.assertEqual(V.order_prices(labels, [0.615, 0.385], teams, sourced_ev), [0.615, 0.385])
        # An identity with no https source is never accepted (no invented values).
        with self.assertRaises(ValueError):
            V.order_prices(labels, [0.615, 0.385], teams,
                            {'identity_sources': [{'names': ['Tropa do KinGui', 'Projeto do KinGui']}]})
        with self.assertRaises(ValueError):
            V.order_prices(labels, [0.615, 0.385], teams,
                            {'identity_sources': [{'names': ['Tropa do KinGui', 'Projeto do KinGui'],
                                                   'source': 'http://insecure.example/x'}]})
        # A sourced alias is still refused if it maps both teams onto one outcome.
        with self.assertRaises(ValueError):
            V.order_prices(['Tropa do KinGui', 'Projeto do KinGui'], [0.5, 0.5], teams, sourced_ev)


class BothTeamsOnPhoneCards(unittest.TestCase):
    def test_every_open_card_prints_both_percentages(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        cards = {a['href'].rsplit('-', 1)[-1]: a for a in soup.select('#picks-at-a-glance a.glance-card-mobile')}
        self.assertEqual(len(cards), len(open_rows()))
        for m in open_rows():
            card = cards[m['id']]
            text = card.get_text(' ', strip=True)
            for i, team in enumerate(m['teams']):
                self.assertIn(team, text, m['id'])
                if m['probabilities']:
                    self.assertIn('%.1f%%' % (m['probabilities'][i] * 100), text, '%s %s' % (m['id'], team))

    def test_the_pick_is_visually_tagged_not_only_bolded(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        cards = soup.select('#picks-at-a-glance a.glance-card-mobile')
        for card in cards:
            if card.get('data-glance-priced') == '1':
                self.assertIn('OUR PICK', card.get_text(' ', strip=True))
                self.assertEqual(len(card.select('.glance-card-score')), 2)
                self.assertEqual(len(card.select('.glance-card-score.other')), 1)
                self.assertEqual(len(card.select('.glance-card-pick-team')), 1)

    def test_no_card_repeats_the_pick_name_outside_the_score_rows(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        for card in soup.select('#picks-at-a-glance a.glance-card-mobile'):
            if card.get('data-glance-priced') != '1':
                continue
            scores = card.select_one('.glance-card-scores').get_text(' ', strip=True)
            block = card.select_one('.glance-card-pick').get_text(' ', strip=True)
            self.assertEqual(block.replace('OUR PICK', '').strip(), scores.strip())

    def test_unpriced_cards_never_invent_a_number(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        for card in soup.select('#picks-at-a-glance a.glance-card-mobile'):
            if card.get('data-glance-priced') == '0':
                self.assertIn('No percentage', card.get_text(' ', strip=True))
                self.assertNotIn('50/50', card.get_text(' ', strip=True))

    def test_expiry_withdraws_the_opponents_number_too(self):
        self.assertIn(".glance-card-other-prob", APP)
        self.assertIn("for (const other of item.querySelectorAll('.glance-card-other-prob')) other.textContent = 'Withheld'", APP)

    def test_both_published_css_copies_carry_the_score_rows(self):
        # Compare against the committed root copy only. CI runs this suite before
        # `scripts.build` has ever written public/, so depending on that gitignored
        # folder would pass locally and fail on a clean checkout; asserting its
        # absence instead would fail locally. The committed copies are the contract.
        self.assertEqual(CSS, (ROOT / 'assets' / 'style.css').read_text())
        flat = CSS.replace(' ', '')
        self.assertIn('.glance-card-scores{display:flex;flex-direction:column', flat)
        self.assertIn('.glance-card-score.other', flat)

    def test_glance_accepts_a_row_whose_pick_is_absent(self):
        # A priced row with no pick must not raise; it is simply not highlighted.
        html = glance({'last_attempt_at': '2026-10-23T10:00:00Z'}, [{
            'id': 'X1', 'teams': ['A Team', 'B Team'], 'state': 'open',
            'start': '2026-10-24T10:00:00Z', 'lock': '2026-10-24T09:54:00Z',
            'expires_at': '2026-10-24T09:54:00Z', 'probabilities': [0.6, 0.4],
            'pick': None, 'method': 'exchange', 'competition': 'Test Cup'}])
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(len(soup.select('.glance-card-score')), 2)
        self.assertEqual(soup.select('.glance-card-pick-team'), [])


class UnresolvedSectionInTheSummary(unittest.TestCase):
    def test_section_exists_with_its_own_heading(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        section = soup.select_one('#unresolved-limits')
        self.assertIsNotNone(section)
        self.assertIn('Unresolved picks, and why a pick can be missing',
                      section.select_one('h2').get_text(' ', strip=True))
        # It must sit inside the executive summary, next to the pick list.
        self.assertIsNotNone(soup.select_one('#picks-at-a-glance'))
        hrefs = {a['href'] for a in section.select('a[href]')}
        self.assertTrue({'#unresolved-summary', 'unresolved.html', 'review.html'} <= hrefs, hrefs)

    def test_counts_come_from_the_snapshot_not_from_prose(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        text = soup.select_one('#unresolved-limits').get_text(' ', strip=True)
        missing = len([m for m in open_rows() if m['probabilities'] is None])
        if missing:
            self.assertIn('%d of the %d open matches publish no win percentage' % (missing, len(open_rows())), text)
        else:
            self.assertIn('every one of the %d open matches' % len(open_rows()), text)

    def test_refusals_and_lookups_are_reported_from_recorded_attempts(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open')
        row['probabilities'] = row['fair_odds'] = row['pick'] = row['method'] = None
        row['attempts'] = [
            {'provider': 'Polymarket', 'status': 'unresolved', 'reason': 'No exact team-pair and UTC-start match'},
            {'provider': 'GG.BET', 'status': 'error', 'reason': 'HTTP 403 persisted'},
        ]
        soup = BeautifulSoup(unresolved_limits_card(doc), 'html.parser')
        text = soup.get_text(' ', strip=True)
        open_count = len([m for m in doc['matches'] if m['state'] == 'open'])
        self.assertIn('1 of the %d open matches publish no win percentage' % open_count, text)
        self.assertIn('Polymarket returned no exact team pair', text)
        self.assertIn('GG.BET: HTTP 403 persisted', text)
        self.assertIn('never bypassed', text)

    def test_no_refusal_is_ever_stated_as_an_absence_of_odds(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        section = soup.select_one('#unresolved-limits')
        text = section.get_text(' ', strip=True).lower()
        self.assertIn('access controls are never bypassed', text)
        # The only place 50/50 may appear is the sentence that refuses to use it.
        plain = section.get_text(' ', strip=True)
        self.assertEqual(plain.count('50/50'), plain.count('default 50/50'))

    def test_section_renders_when_nothing_is_missing(self):
        doc = copy.deepcopy(SNAPSHOT)
        for row in doc['matches']:
            if row['state'] == 'open':
                row['attempts'] = []
        html = unresolved_limits_card(doc)
        self.assertIn('id="unresolved-limits"', html)
        self.assertIn('default 50/50', html)


# ---------------------------------------------------------------------------
# Archival lobby observation: 2026-10-23 09:44Z
# ---------------------------------------------------------------------------
# The 30 fixtures below were read from https://play.hotspawn.com/lobby on
# 2026-10-23 at 09:44Z (per-match evidence in research/session-0cc1138a/REPORT.md).
# Each entry carries the UTC start the fixture itself published at that time;
# the starts are the archived values in research/harvest-9b97d585/snapshot.json
# (fixture evidence observed 2026-10-23T09:55:02Z), not values inferred here.
#
# Why the starts are needed (session 019a253a, 2026-10-24): this suite used to
# index the board by that fixed ID set and raise KeyError once a fixture left
# Hotspawn's `status=scheduled` feed. On 2026-10-24 that hard pin failed on
# `1079655` and `1081148` - both of which had legitimately started at
# 2026-10-23T11:00Z - and the failure landed in the *unit* gate, which runs
# before refresh, build and deploy. Every scheduled publication therefore
# stopped for ~16 hours and the public board was withheld once its evidence
# window closed. A past fixture leaving a schedule feed is correct behaviour,
# so the assertions now separate two cases that were previously conflated:
#
#   present on the board -> parity + official link + pick while live (unchanged)
#   absent from the board -> allowed only when the fixture's own archived start
#                            is at or before the snapshot's observation clock
#
# A *future* fixture disappearing from the feed still fails, which is the
# regression this class exists to catch.
OBSERVED_OPEN_STARTS = {
    '1079193': '2026-10-24T08:00:00Z', '1079195': '2026-10-24T14:00:00Z',
    '1079198': '2026-10-25T12:00:00Z', '1079199': '2026-10-25T15:00:00Z',
    '1079200': '2026-10-25T18:00:00Z', '1079655': '2026-10-23T11:00:00Z',
    '1079657': '2026-10-23T17:00:00Z', '1081148': '2026-10-23T11:00:00Z',
    '1081150': '2026-10-23T17:00:00Z', '1081605': '2026-10-23T11:00:00Z',
    '1081606': '2026-10-23T13:00:00Z', '1082693': '2026-10-23T18:00:00Z',
    '1082792': '2026-10-31T09:00:00Z', '1082793': '2026-10-31T13:00:00Z',
    '1082858': '2026-10-26T03:00:00Z', '1082859': '2026-10-26T03:00:00Z',
    '1082860': '2026-10-27T03:00:00Z', '1082861': '2026-10-27T03:00:00Z',
    '1082897': '2026-10-27T08:00:00Z', '1082898': '2026-10-27T11:00:00Z',
    '1082900': '2026-10-27T17:00:00Z', '1082901': '2026-10-27T20:00:00Z',
    '1082923': '2026-10-23T22:00:00Z', '1082924': '2026-10-23T16:00:00Z',
    '1082925': '2026-10-23T19:00:00Z', '1082926': '2026-10-23T13:00:00Z',
    '1082980': '2026-10-23T13:00:00Z', '1082996': '2026-10-25T09:00:00Z',
    '1083014': '2026-10-23T13:00:00Z', '1083025': '2026-10-23T21:00:00Z',
}
OBSERVED_OPEN = set(OBSERVED_OPEN_STARTS)


def _utc(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


ARCHIVE = json.loads((ROOT / 'research' / 'harvest-9b97d585' / 'snapshot.json').read_text())
"""The archived snapshot observed at 2026-10-23T09:55:02Z (fixture evidence),
which is the read the 09:44Z lobby observation is checked against. The parity
contract is pinned to this retained file, not to ``data/latest.json``: that
file rotates every refresh, so pinning an observation to it made a past
fixture's legitimate exit from the schedule feed look like a coverage bug and
blocked publication (session 019a253a). The *live* board's own parity is
asserted from the snapshot's ``coverage_counts`` in
tests/test_session_019a253a.py, which is rotation-proof by construction.
"""


def _utc(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


def archived_coverage_problems(snapshot):
    """Return the parity/pick problems for the archived lobby observation.

    Pure function of one snapshot so that both the archive assertion and the
    rotation guard (tests/test_session_019a253a.py) exercise the same code.
    It never indexes a fixture that the snapshot does not carry.
    """
    rows = {str(m['id']): m for m in snapshot['matches']}
    changes = snapshot.get('inventory_changes') or {}
    removed = {str(x) for x in changes.get('removed_ids') or []}
    clock = snapshot.get('fixtures_observed_at') or snapshot.get('built_at')
    observed = _utc(clock)
    problems = []
    for fixture, archived_start in sorted(OBSERVED_OPEN_STARTS.items()):
        row = rows.get(fixture)
        if row is None:
            # Absence is only legitimate once the fixture's own start has
            # passed, or when the snapshot records the feed removing it.
            if fixture in removed:
                continue
            if _utc(archived_start) > observed:
                problems.append('%s: still-future fixture is missing from the board' % fixture)
            continue
        lock = _utc(row['lock']) if row.get('lock') else None
        live = lock is None or lock > observed
        if live and not row.get('pick'):
            problems.append('%s: live fixture publishes no pick' % fixture)
        if not live and row.get('pick'):
            problems.append('%s: fixture past its lock still publishes a pick' % fixture)
        url = str(row.get('source_url') or '')
        if not (url.startswith('https://www.hotspawn.com/') or url.startswith('https://play.hotspawn.com/')):
            problems.append('%s: no official Hotspawn fixture URL' % fixture)
        if live and not (row.get('evidence') or [{}])[0].get('url'):
            problems.append('%s: pick published with no evidence link' % fixture)
    return problems


class LiveHotspawnCoverage(unittest.TestCase):
    """Parity with the 09:44Z lobby observation, asserted on the archive.

    The observation, its archived start times and the reason the assertions
    are shaped this way are documented above ``OBSERVED_OPEN_STARTS``.
    """

    def test_archived_observation_lists_every_fixture_with_a_pick(self):
        self.assertEqual(len(OBSERVED_OPEN_STARTS), 30)
        self.assertEqual(archived_coverage_problems(ARCHIVE), [])

    def test_archived_snapshot_is_same_parity_read(self):
        # The archive the parity is pinned to is the three-view 92/92/92/92 read.
        self.assertEqual(set(ARCHIVE['coverage_counts'].values()), {92})
        known = {str(m['id']) for m in ARCHIVE['matches']}
        self.assertEqual(OBSERVED_OPEN - known, set())

    def test_a_fully_rotated_board_cannot_break_the_coverage_gate(self):
        # Guard (session 019a253a): every archived fixture absent and past its
        # start must produce no problem at all - this is the state that used to
        # raise KeyError and stop publication for the whole board.
        rotated = {
            'fixtures_observed_at': '2026-11-05T00:00:00Z',
            'built_at': '2026-11-05T00:00:01Z',
            'matches': [],
            'inventory_changes': {'removed_ids': []},
        }
        self.assertEqual(archived_coverage_problems(rotated), [])

    def test_a_still_future_fixture_that_vanishes_is_still_reported(self):
        # The guard must not be able to hide a real coverage regression.
        rotated = {
            'fixtures_observed_at': '2026-10-23T23:30:00Z',
            'built_at': '2026-10-23T23:30:01Z',
            'matches': [],
            'inventory_changes': {'removed_ids': []},
        }
        problems = archived_coverage_problems(rotated)
        self.assertIn('1079193: still-future fixture is missing from the board', problems)


if __name__ == '__main__':
    unittest.main()
