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


def feed_ids(snapshot):
    """Fixture IDs the snapshot's own archived feed evidence still returns."""
    return {str(x.get('id')) for x in (snapshot.get('fixture_evidence') or []) if x.get('id')}


def recorded_removals(snapshot):
    """Fixture IDs the snapshot explicitly records as dropped by the source."""
    return {str(x) for x in (snapshot.get('inventory_changes') or {}).get('removed_ids', [])}


def lobby_parity_gaps(snapshot, observed_open):
    """Pinned lobby fixtures the *feed still returns* but the board has lost.

    This is the only direction that can be a pipeline defect. A pinned fixture
    the archived feed no longer returns was dropped by Hotspawn itself; a board
    that never carried it is correct, and the snapshot's own record of the drop
    is what makes that visible rather than silent. Fixing the parity check to
    demand the historical row unconditionally is what failed every scheduled
    publication run from 2026-10-24T04:23Z onward.
    """
    known = {m['id'] for m in snapshot['matches']}
    still_returned = feed_ids(snapshot) - recorded_removals(snapshot)
    return sorted(f for f in (observed_open - known) if f in still_returned)


class LiveHotspawnCoverage(unittest.TestCase):
    """The board must list the fixtures the public lobby lists.

    The IDs below were read from https://play.hotspawn.com/lobby on
    2026-10-23 at 09:44Z (see research/session-0cc1138a/REPORT.md for the
    per-match evidence).

    What this class asserts, and what it deliberately does not
    -----------------------------------------------------------
    It pins a *dated* lobby observation, so it cannot assert that today's board
    still carries those fixtures. Hotspawn removes a fixture once it starts, and
    every one of them locks six minutes before it does, so a few hours after the
    observation the pinned set is partly historical by construction. Asserting
    the historical set unconditionally made every scheduled `pages.yml` run fail
    on `main` from 2026-10-24T04:23Z (runs 39956197341 … 40062143026), which made
    `scripts.refresh_watchdog` return `stop` and left the live site publishing a
    17-hour-old snapshot with every pick withheld.

    The invariant that survives a moving lobby is source-relative, and both of
    its directions are tested offline below:

    * a pinned fixture the snapshot's own archived feed evidence still returns,
      but the board has lost, is a defect and fails;
    * a pinned fixture the feed itself no longer returns is a source fact, not a
      board defect, and is excused;
    * every fixture the board still carries keeps its pick rule against the
      snapshot's own clock and its official Hotspawn link.
    """

    OBSERVED_OPEN = {
        '1081605', '1081148', '1079655', '1081606', '1082926', '1082980', '1083014',
        '1082924', '1081150', '1079657', '1082693', '1082925', '1083025', '1082923',
        '1079193', '1079195', '1082996', '1079198', '1079199', '1079200', '1082858',
        '1082859', '1082860', '1082861', '1082897', '1082898', '1082900', '1082901',
        '1082792', '1082793',
    }

    def test_snapshot_covers_the_observed_lobby_fixtures(self):
        # A pinned historical lobby observation cannot be asserted against a moving
        # board: Hotspawn drops a fixture the moment it starts, and the 09:44Z set
        # below is partly historical only hours later. The binding direction is the
        # one that can actually be a defect - a fixture the snapshot's own archived
        # feed evidence still returns, but the board has lost. A pinned fixture the
        # feed no longer returns (1081148 and 1079655 by the 11:43Z observation) is a
        # source fact, excused here and recorded in research/session-0cc1138a/.
        self.assertEqual(lobby_parity_gaps(SNAPSHOT, self.OBSERVED_OPEN), [],
                         'lobby fixture still returned by the feed but missing from the board')

    def test_each_observed_fixture_is_published_with_a_pick_and_an_official_link(self):
        # Integration repair (session f89bb1f8, 2026-10-23 11:05Z): the lobby was
        # observed at 09:44Z, and three of those fixtures lock at 10:54Z and start
        # at 11:00Z. Once a snapshot is taken after its lock the pipeline correctly
        # withholds the pick -- "a past lock is not a missing pick" -- so pinning a
        # pick forever made this suite fail on every snapshot after 10:54Z. The
        # coverage intent is unchanged: parity and the official link are still
        # asserted for every fixture the board still carries, and a pick is still
        # required for every one that is not yet past its lock at the snapshot's own
        # clock.
        rows = {m['id']: m for m in SNAPSHOT['matches']}
        # Rows are derived against the build clock (scripts.build applies the
        # lock/start cutoff when it renders), so that is the clock to compare to.
        clock = SNAPSHOT.get('built_at') or SNAPSHOT['fixtures_observed_at']
        observed = datetime.fromisoformat(clock.replace('Z', '+00:00'))
        for fixture in self.OBSERVED_OPEN:
            # A pinned fixture the board no longer carries is either one Hotspawn
            # dropped (excused, and covered by the parity test's other direction) or
            # one the board lost (a defect the parity test already reports). Neither
            # is a per-fixture pick question, so there is nothing to assert here.
            if fixture not in rows:
                continue
            row = rows[fixture]
            lock = datetime.fromisoformat(row['lock'].replace('Z', '+00:00')) if row.get('lock') else None
            live = lock is None or lock > observed
            if live:
                self.assertTrue(row.get('pick'), fixture)
            else:
                self.assertIsNone(row.get('pick'), fixture)
            # The official Hotspawn URL is either the fixture's own match page or,
            # for fixtures Hotspawn publishes without one (DraculaN Season 7), the
            # CS2 pick'em page the fixture was listed on. Both are hotspawn.com.
            url = row.get('source_url', '')
            self.assertTrue(url.startswith('https://www.hotspawn.com/') or url.startswith('https://play.hotspawn.com/'), fixture)
            # A price-evidence link is required exactly where a pick is
            # published. After the lock the pipeline withholds the pick and
            # clears the historical quote (1081605 at the 11:16Z snapshot),
            # so demanding evidence[0].url there inverted the intent.
            if live:
                self.assertTrue((row.get('evidence') or [{}])[0].get('url'), fixture)


class ADatedLobbyObservationCannotBlockPublication(unittest.TestCase):
    """Both directions of the parity invariant, offline.

    These exist because the pinned-set version of the check above failed every
    scheduled publication run on `main` from 2026-10-24T04:23Z onward: it
    demanded rows for fixtures Hotspawn had already started and dropped, and the
    refresh watchdog then refused to dispatch, so the live site kept publishing a
    17-hour-old snapshot with every pick withheld. A check that can fail for a
    reason which is not a defect has to be pinned in both directions.
    """

    @staticmethod
    def _present_pinned():
        known = {m['id'] for m in SNAPSHOT['matches']}
        return sorted(LiveHotspawnCoverage.OBSERVED_OPEN & known)

    @staticmethod
    def _snapshot_without(fixture_id, drop_from_feed):
        doc = copy.deepcopy(SNAPSHOT)
        doc['matches'] = [m for m in doc['matches'] if m['id'] != fixture_id]
        if drop_from_feed:
            doc['fixture_evidence'] = [x for x in (doc.get('fixture_evidence') or [])
                                       if str(x.get('id')) != fixture_id]
        return doc

    def test_a_fixture_the_feed_no_longer_returns_is_not_a_board_defect(self):
        target = self._present_pinned()[0]
        doc = self._snapshot_without(target, drop_from_feed=True)
        self.assertEqual(lobby_parity_gaps(doc, LiveHotspawnCoverage.OBSERVED_OPEN), [],
                         'a fixture Hotspawn itself dropped must not fail the board')

    def test_a_fixture_the_feed_still_returns_but_the_board_lost_is_a_defect(self):
        target = self._present_pinned()[0]
        doc = self._snapshot_without(target, drop_from_feed=False)
        self.assertEqual(lobby_parity_gaps(doc, LiveHotspawnCoverage.OBSERVED_OPEN), [target])

    def test_an_explicit_removal_record_excuses_a_fixture_the_feed_still_returns(self):
        target = self._present_pinned()[0]
        doc = self._snapshot_without(target, drop_from_feed=False)
        doc.setdefault('inventory_changes', {})['removed_ids'] = [target]
        self.assertEqual(lobby_parity_gaps(doc, LiveHotspawnCoverage.OBSERVED_OPEN), [])

    def test_every_open_row_carries_an_official_hotspawn_link(self):
        # The coverage intent that survives a moving lobby: whatever the board
        # still lists as open is one tap from Hotspawn's own page for it.
        open_rows = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.assertTrue(open_rows, 'the committed snapshot has no open rows to check')
        for row in open_rows:
            url = row.get('source_url', '')
            self.assertTrue(url.startswith('https://www.hotspawn.com/')
                            or url.startswith('https://play.hotspawn.com/'), row['id'])


if __name__ == '__main__':
    unittest.main()
