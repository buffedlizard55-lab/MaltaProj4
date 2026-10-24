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


def feed_removed_ids(snapshot, observed_ids):
    """Observed IDs the snapshot's own verified feed evidence proves are gone.

    Durable parity rule (session 174afa4f, 2026-10-24). The earlier rule
    excused only IDs in ``inventory_changes.removed_ids`` — the delta against
    the *previous* snapshot. When Hotspawn removed 1079655 and 1081148
    between the 09:44Z lobby observation and the 11:25Z comparison snapshot,
    the committed 11:47Z snapshot recorded ``removed_ids: []`` while its raw
    feed evidence no longer contained either ID, so this suite failed on
    every scheduled run from 2026-10-23T12:49Z (runs 39956197341,
    39998307424, 40025828846, 40042111432, 40062143026) *before* the refresh
    step could run — a self-sustaining publish deadlock.

    An ID therefore also counts as feed-removed when the snapshot itself
    proves the collector dropped nothing:

    * ``coverage == 'verified'`` (the Hotspawn views agreed with each
      other; partial/retained snapshots prove nothing and excuse nothing),
    * the raw CS2 ``fixture_evidence`` ID set equals the published
      ``matches`` ID set exactly (the same completeness invariant
      ``scripts.validate`` asserts), and
    * the ID is absent from that raw evidence.

    A collector-side drop (ID present in the raw evidence, missing from
    ``matches``) can never satisfy this, so parity still fails loudly where
    it matters. ``inventory_changes.removed_ids`` remains sufficient on its
    own, as before.
    """
    removed = {str(x) for x in (snapshot.get('inventory_changes') or {}).get('removed_ids', [])}
    excused = {i for i in observed_ids if i in removed}
    if snapshot.get('coverage') != 'verified':
        return excused
    evidence = {str(x.get('id')) for x in snapshot.get('fixture_evidence') or [] if x.get('id') is not None}
    known = {str(m['id']) for m in snapshot.get('matches') or []}
    if not evidence or evidence != known:
        return excused
    return excused | {i for i in observed_ids if i not in evidence}


class LiveHotspawnCoverage(unittest.TestCase):
    """The board must list the fixtures the public lobby lists.

    The IDs below were read from https://play.hotspawn.com/lobby on
    2026-10-23 at 09:44Z (see research/session-0cc1138a/REPORT.md for the
    per-match evidence). This pins parity with that observation instead of
    asserting a permanent count.
    """

    OBSERVED_OPEN = {
        '1081605', '1081148', '1079655', '1081606', '1082926', '1082980', '1083014',
        '1082924', '1081150', '1079657', '1082693', '1082925', '1083025', '1082923',
        '1079193', '1079195', '1082996', '1079198', '1079199', '1079200', '1082858',
        '1082859', '1082860', '1082861', '1082897', '1082898', '1082900', '1082901',
        '1082792', '1082793',
    }
    # Live read 09:44-09:56Z (research/session-0cc1138a/REPORT.md, section 2).
    # The strict "every still-open observed fixture carries its pick"
    # assertion is only meaningful inside the project's own eight-hour
    # evidence window from that read; after it, those picks have expired by
    # design and live completeness is asserted snapshot-relatively (summary
    # counts, validator, coverage contract), never against fixed IDs.
    OBSERVED_AT = datetime.fromisoformat('2026-10-23T09:44:00+00:00')

    def test_snapshot_covers_the_observed_lobby_fixtures(self):
        # Integration repair (session b6e37c61, 2026-10-23): Hotspawn itself
        # can drop a fixture after the 09:44Z observation — it removed
        # 1081148 before the 11:16Z snapshot, which records exactly that in
        # its own inventory_changes.removed_ids (and the raw feed evidence
        # no longer contains it). Parity still binds for every fixture the
        # feed still returns; only feed-removed IDs, per the pipeline's own
        # sourced record, are excused.
        # Durable extension (session 174afa4f, 2026-10-24): feed removal is
        # proved by feed_removed_ids() from the snapshot's verified raw
        # evidence, not only by the one-step removed_ids delta — see that
        # helper for the deadlock this prevents.
        known = {m['id'] for m in SNAPSHOT['matches']}
        removed = feed_removed_ids(SNAPSHOT, self.OBSERVED_OPEN)
        self.assertEqual(self.OBSERVED_OPEN - known - removed, set(), 'lobby fixture missing from the board')

    def test_each_observed_fixture_is_published_with_a_pick_and_an_official_link(self):
        # Integration repair (session f89bb1f8, 2026-10-23 11:05Z): the lobby was
        # observed at 09:44Z, and three of those fixtures lock at 10:54Z and start
        # at 11:00Z. Once a snapshot is taken after its lock the pipeline correctly
        # withholds the pick -- "a past lock is not a missing pick" -- so pinning a
        # pick forever made this suite fail on every snapshot after 10:54Z. The
        # coverage intent is unchanged: parity and the official link are still
        # asserted for all 30 fixtures, and a pick is still required for every one
        # that is not yet past its lock at the snapshot's own clock.
        # Window rule (session 174afa4f, 2026-10-24): that pick requirement
        # binds while the snapshot's fixture evidence is inside the
        # eight-hour window from the 09:44Z read. Outside it the observed
        # picks have expired by design, so only parity (above), the official
        # link, and "no pick without its evidence link" bind here; current
        # completeness is then a property of the new snapshot's own rows.
        rows = {m['id']: m for m in SNAPSHOT['matches']}
        # Rows are derived against the build clock (scripts.build applies the
        # lock/start cutoff when it renders), so that is the clock to compare to.
        clock = SNAPSHOT.get('built_at') or SNAPSHOT['fixtures_observed_at']
        observed = datetime.fromisoformat(clock.replace('Z', '+00:00'))
        feed_clock = datetime.fromisoformat(SNAPSHOT['fixtures_observed_at'].replace('Z', '+00:00'))
        from datetime import timedelta
        in_window = feed_clock <= self.OBSERVED_AT + timedelta(hours=8)
        removed = feed_removed_ids(SNAPSHOT, self.OBSERVED_OPEN)
        for fixture in self.OBSERVED_OPEN:
            if fixture in removed and fixture not in rows:
                continue
            row = rows[fixture]
            if not in_window:
                url = row.get('source_url', '')
                self.assertTrue(url.startswith('https://www.hotspawn.com/') or url.startswith('https://play.hotspawn.com/'), fixture)
                if row.get('pick'):
                    self.assertIn(row['pick'], row['teams'], fixture)
                    if row.get('probabilities') is not None:
                        self.assertTrue((row.get('evidence') or [{}])[0].get('url'), fixture)
                continue
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


if __name__ == '__main__':
    unittest.main()
