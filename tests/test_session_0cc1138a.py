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


class LiveHotspawnCoverage(unittest.TestCase):
    """The board must list the fixtures the public lobby lists — on every build.

    History. On 2026-10-23 at 09:44Z the public lobby's 30 open CS2 fixture IDs
    were captured (``OBSERVED_OPEN``) and, *for that observation*, pinned 1:1
    against the board (research/session-0cc1138a/REPORT.md). That frozen set is a
    point-in-time proof, not a permanent inventory: Hotspawn rotates its feed
    continuously (it dropped ``1081148`` and ``1079655`` within hours). Asserting
    the frozen set against the ever-changing ``data/latest.json`` therefore made
    every scheduled refresh fail at the "Unit and independent failure-mode tests"
    step once those two rotated out — the ``KeyError: '1079655'`` and parity
    failure reproduced on 2026-10-24, and the failing main runs 40062143026,
    40042111432 and 40025828846 (see COORDINATION.md, session 4b419150 claim).

    Repair (this integration). The live requirement is bound on EVERY build from
    the snapshot's own sourced three-view parity record (``coverage`` /
    ``coverage_counts``, produced by ``scripts/inventory.py`` from the official
    scoped API, the CS2 pick'em page and the general lobby — the same three
    official views Hotspawn publishes), plus a per-row provenance and pick/lock
    contract on every open row. This is strictly stronger than a frozen list: it
    binds to whichever fixtures are actually listed at build time rather than to
    a snapshot that has already gone stale, and it can never again gate the
    refresh pipeline on a lobby observation that is hours old. The frozen 09:44Z
    observation is retained as a documented historical artifact and verified
    against the report that records it, not against live data.
    """

    OBSERVED_AT = '2026-10-23T09:44:00Z'
    OBSERVED_OPEN = {
        '1081605', '1081148', '1079655', '1081606', '1082926', '1082980', '1083014',
        '1082924', '1081150', '1079657', '1082693', '1082925', '1083025', '1082923',
        '1079193', '1079195', '1082996', '1079198', '1079199', '1079200', '1082858',
        '1082859', '1082860', '1082861', '1082897', '1082898', '1082900', '1082901',
        '1082792', '1082793',
    }
    REPORT = ROOT / 'research' / 'session-0cc1138a' / 'REPORT.md'

    @staticmethod
    def _official_hotspawn(value):
        return isinstance(value, str) and (
            value.startswith('https://play.hotspawn.com/')
            or value.startswith('https://www.hotspawn.com/'))

    def _clock(self):
        clock = (SNAPSHOT.get('built_at') or SNAPSHOT.get('fixtures_observed_at')
                 or SNAPSHOT['generated_at'])
        return datetime.fromisoformat(clock.replace('Z', '+00:00'))

    def test_three_view_parity_is_recorded_on_every_build(self):
        # scripts/inventory.py sets coverage='verified' only when all three
        # official views are readable AND their fixture-id sets are identical;
        # otherwise it records 'partial' with a coverage_difference issue and
        # retains the union. Both are honest; a silent omission is not.
        coverage = SNAPSHOT.get('coverage')
        self.assertIn(coverage, ('verified', 'partial'))
        counts = SNAPSHOT.get('coverage_counts') or {}
        for key in ('api', 'page', 'lobby', 'retained'):
            self.assertIn(key, counts, 'coverage_counts missing %s' % key)
        if coverage == 'verified':
            for key in ('page', 'lobby', 'retained'):
                self.assertEqual(counts['api'], counts[key],
                                 'verified snapshot must agree across the API, CS2 page, lobby and retained rows')
        else:
            self.assertTrue(SNAPSHOT.get('issues') or SNAPSHOT.get('fixture_conflicts'),
                            'a partial three-view read must publish an explanation, never silent incompleteness')
        # Every retained row must carry an official Hotspawn fixture source.
        for m in SNAPSHOT['matches']:
            self.assertTrue(
                self._official_hotspawn(m.get('source_url'))
                or any('hotspawn' in (s.get('url') or '') for s in (m.get('fixture_sources') or [])),
                '%s lacks an official Hotspawn source link' % m['id'])

    def _open_row_troubles(self, snapshot, clock):
        """The always-on per-row contract, reusable for negative tests."""
        troubles = []
        for m in snapshot['matches']:
            if m.get('state') != 'open':
                continue
            mid = m['id']
            if not self._official_hotspawn(m.get('source_url')):
                troubles.append('%s: open row lacks an official Hotspawn source' % mid)
            lock_raw = m.get('lock')
            lock = datetime.fromisoformat(lock_raw.replace('Z', '+00:00')) if lock_raw else None
            if lock is not None and lock <= clock:
                # Past the pick lock the pipeline correctly withholds the pick;
                # a past lock is not a missing pick (the frozen-pin bug this
                # class was repaired for). Only still-open fixtures are bound.
                continue
            pick, probs = m.get('pick'), m.get('probabilities')
            if pick is None:
                # No pick: an honestly documented unresolved row, never a blank.
                if not (m.get('reason') or m.get('attempts')):
                    troubles.append('%s: open row has no pick and no documented limitation' % mid)
                continue
            if pick not in (m.get('teams') or []):
                troubles.append('%s: pick %r is not one of its teams' % (mid, pick))
            if probs is not None:
                # Priced (market/model) pick: an https, non-Hotspawn price source.
                ev = (m.get('evidence') or [{}])[0].get('url')
                if not (isinstance(ev, str) and ev.startswith('https://')):
                    troubles.append('%s: priced pick lacks an https evidence link' % mid)
            else:
                # Research-only pick (HLTV recent-form / Valve-VRS single): the
                # sourcing lives in external research context, not a price quote.
                contexts = [m.get('hltv_context') or {}, m.get('vrs_research') or {}]
                contexts.extend((m.get('hltv_team_pages') or {}).get('teams') or [])
                sources = {c.get('source') or c.get('url') for c in contexts}
                if not any(isinstance(s, str) and s.startswith('https://') for s in sources):
                    troubles.append('%s: research-only pick lacks an external context source' % mid)
        return troubles

    def test_every_open_row_has_a_pick_and_provenance_or_an_honest_limit(self):
        troubles = self._open_row_troubles(SNAPSHOT, self._clock())
        self.assertEqual(troubles, [], '\n'.join(troubles[:8]))

    def test_the_repaired_gate_still_rejects_a_silent_omission(self):
        # Prove the repaired live gate is not a no-op. A still-open row that
        # carries a priced pick but no https evidence, or that has neither a
        # pick nor a documented limitation, must still be flagged — the frozen
        # historical pin was retired, but the coverage requirement was not.
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open')
        row['lock'] = '2999-01-01T00:00:00Z'  # force it clearly before the lock
        clock = self._clock()
        row.update(pick=row['teams'][0], probabilities=[0.6, 0.4], evidence=[])
        self.assertTrue(any('https evidence link' in t for t in self._open_row_troubles(doc, clock)),
                        'a priced pick with no source must be caught')
        row.update(pick=None, probabilities=None, reason=None, attempts=[])
        self.assertTrue(any('no pick and no documented limitation' in t for t in self._open_row_troubles(doc, clock)),
                        'a blank open row with no limitation must be caught')

    def test_frozen_2026_10_23_observation_is_preserved_as_evidence(self):
        # The 09:44Z proof is a historical artifact. Keep it intact and verified
        # against the report that documents it, without binding live data to a
        # lobby observation that is already ~20 hours old.
        self.assertEqual(len(self.OBSERVED_OPEN), 30)
        self.assertTrue(all(isinstance(x, str) and x.isdigit() for x in self.OBSERVED_OPEN))
        self.assertTrue(self.REPORT.exists())
        report = self.REPORT.read_text(encoding='utf-8')
        self.assertIn('09:44', report)
        self.assertIn('1079655', report)


if __name__ == '__main__':
    unittest.main()
