"""Session e9be3e6b — pin the independent source-ladder verifier and the phone links.

Nothing here collects data. The verifier replays every published number from the
snapshot's own stored evidence; these tests also prove the verifier fails on
deliberate corruption, so a green run cannot be obtained by weakening a check.
"""
import copy
import importlib.util
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


# Retained observation containing both arithmetic fixtures (NEXVOID vs Alter Ego,
# HAVU vs Azuolas) exactly as published on 2026-10-24T05:57:43Z.
ARCHIVE = ROOT / 'research/harvest-d2b90de7/snapshot.json'


def rows_by_id():
    """Today's snapshot, with fixtures it has rotated out read from the archive."""
    rows = {m['id']: m for m in SNAPSHOT['matches']}
    if ARCHIVE.exists():
        archived = json.loads(ARCHIVE.read_text())
        for m in archived.get('matches') or []:
            rows.setdefault(m['id'], m)
    return rows


def load_verifier():
    spec = importlib.util.spec_from_file_location(
        'verify_source_ladder_e9be3e6b', ROOT / 'verification-e9be3e6b' / 'verify_source_ladder.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_verifier()


def audit(doc=None, at=None):
    doc = doc or SNAPSHOT
    clock = at or (datetime.fromisoformat(doc['generated_at'].replace('Z', '+00:00'))
                   + timedelta(minutes=1))
    return V.audit(doc, at=clock.isoformat())


class SourceLadderVerification(unittest.TestCase):
    def test_every_committed_row_verifies_with_no_network(self):
        report = audit()
        self.assertEqual(report['summary']['failures'], 0,
                         [r for r in report['rows'] if r['problems']][:3])
        self.assertEqual(report['summary']['rows'], len(SNAPSHOT['matches']))

    def test_every_open_match_has_a_pick_a_percentage_and_a_fixture_link(self):
        report = audit()
        s = report['summary']
        self.assertEqual(s['open'], s['open_with_pick'])
        self.assertEqual(s['open'], s['open_with_probability'])
        self.assertEqual(s['open_unresolved'], 0)
        for row in report['rows']:
            if row['state'] == 'open':
                self.assertTrue(str(row['source_url']).startswith('https://'), row['id'])
                self.assertTrue(str(row['evidence_url']).startswith('https://'), row['id'])
                self.assertIn('official Hotspawn fixture link', row['checks'])
                self.assertIn('probability source is external to Hotspawn', row['checks'])

    def test_every_non_featured_row_records_hltv_then_a_book_attempt(self):
        report = audit()
        non_featured = [r for r in report['rows']
                        if r['state'] == 'open' and r['method'] and r['method'] != 'exchange']
        self.assertTrue(non_featured, 'this snapshot must still exercise the fallback ladder')
        for row in non_featured:
            self.assertIn('HLTV attempted with an official link', row['checks'], row['id'])
            self.assertIn('esportsbook/exchange attempted with a link', row['checks'], row['id'])

    def test_model_lines_publish_their_points_vintage_and_are_not_market_prices(self):
        report = audit()
        models = [r for r in report['rows']
                  if r['state'] == 'open' and r['method'] in ('model_vrs', 'model_vrs_mirror')]
        self.assertTrue(models)
        for row in models:
            self.assertTrue(any('non-market' in c for c in row['checks']), row['id'])

    def test_book_listings_refuse_the_symmetric_placeholder(self):
        report = audit()
        books = [r for r in report['rows'] if r['state'] == 'open' and r['method'] == 'bookmaker_fallback']
        self.assertTrue(books)
        for row in books:
            self.assertTrue(any(c.startswith('book listing:') for c in row['checks']), row['id'])

    def test_corruption_cases_are_all_rejected(self):
        cases = V.corrupted_cases(SNAPSHOT)
        self.assertEqual(len(cases), 8)
        for name, doc in cases.items():
            with self.subTest(case=name):
                self.assertGreater(audit(doc)['summary']['failures'], 0, name)

    def test_a_sourced_rename_maps_but_an_unsourced_one_does_not(self):
        sourced = [{'names': ['Tropa do KinGui', 'Projeto do KinGui'],
                    'source': 'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians'}]
        self.assertTrue(V.same_team('Tropa do KinGui', 'Projeto do KinGui', sourced))
        self.assertFalse(V.same_team('Tropa do KinGui', 'Projeto do KinGui'))
        self.assertFalse(V.same_team('Tropa do KinGui', 'Projeto do KinGui',
                                     [{'names': ['Tropa do KinGui', 'Projeto do KinGui'],
                                       'source': 'http://insecure.example/rename'}]))

    def test_known_listing_and_model_arithmetic(self):
        # Session a22008ff (2026-10-24): these two arithmetic fixtures were pinned to
        # `data/latest.json`, so the publisher went red the moment Hotspawn rotated
        # them out of the lobby (`KeyError: '1081152'` in the publish rehearsal). The
        # replay targets a dated, retained observation instead: today's snapshot when
        # it still lists the fixture, otherwise the archive captured while it was on
        # the board. A missing id everywhere is still a failure, never a skip.
        by_id = rows_by_id()
        book = by_id['1082859']['evidence'][0]
        p, kind = V.replay_evidence(book, by_id['1082859']['teams'])
        # Thunderpick via BO3.gg: 1.61 / 2.18, de-vigged.
        self.assertEqual(kind, 'listing_devig')
        self.assertAlmostEqual(p[0], 0.575197889182058, places=12)
        self.assertAlmostEqual(p[1], 0.42480211081794195, places=12)
        model = by_id['1081152']['evidence'][0]
        p, kind = V.replay_evidence(model, by_id['1081152']['teams'])
        # Valve 2026-10-05 file: HAVU 937, Azuolas 863; Glicko RD 75, slope 0.7986.
        self.assertEqual(kind, 'valve_vrs')
        self.assertAlmostEqual(p[0], 0.5815710671661513, places=12)
        self.assertAlmostEqual(V.glicko_expect(1011, 750) * 0.7986 + 0.1007,
                               V.calibrate(V.glicko_expect(1011, 750)), places=12)


class ExecutiveSummaryLinksAndPhoneLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / 'index.html').read_text()
        cls.picks = (ROOT / 'picks.html').read_text()
        cls.unresolved = (ROOT / 'unresolved.html').read_text()
        cls.notes = json.loads((ROOT / 'data' / 'review-notes.json').read_text())

    def test_executive_summary_is_outside_any_folded_block(self):
        soup = BeautifulSoup(self.index, 'html.parser')
        bar = soup.select_one('#exec-summary')
        self.assertIsNotNone(bar)
        self.assertFalse(bar.find_parent('details'), 'the pick links must not require a tap')
        links = {a.get('href') for a in bar.select('a[href]')}
        for target in ('picks.html', '#picks-at-a-glance', 'unresolved.html',
                       '#unresolved-summary', 'matches.html', 'review.html'):
            self.assertIn(target, links, target)

    def test_the_phone_quick_nav_answers_where_the_picks_are(self):
        soup = BeautifulSoup(self.index, 'html.parser')
        quick = soup.select_one('#exec-quicknav')
        self.assertIsNotNone(quick, 'phones need an executive-summary answer above the list')
        self.assertFalse(quick.find_parent('details'))
        hrefs = {a.get('href') for a in quick.select('a[href]')}
        self.assertIn('picks.html', hrefs)
        self.assertIn('#unresolved-limits', hrefs)
        self.assertIn('unresolved', quick.get_text(' ', strip=True).lower())

    def test_a_separate_unresolved_section_states_the_limitations(self):
        soup = BeautifulSoup(self.index, 'html.parser')
        section = soup.select_one('#unresolved-summary')
        self.assertIsNotNone(section)
        text = section.get_text(' ', strip=True).lower()
        for phrase in ('limitations for generating these picks', 'no book lists the match',
                       'hltv has no usable line', 'our model needs both teams'):
            self.assertIn(phrase, text, phrase)
        self.assertIn('#unresolved-summary', {a.get('href') for a in soup.select('#exec-summary a[href]')})

    def test_every_displayed_open_row_has_an_official_source_link(self):
        open_ids = {m['id'] for m in SNAPSHOT['matches'] if m['state'] == 'open'}
        for page in (self.picks, self.unresolved):
            soup = BeautifulSoup(page, 'html.parser')
            external = {a['href'] for a in soup.select('a[href^="https://"]')}
            self.assertTrue(any('hotspawn.com/matches/' in u for u in external))
            self.assertTrue(any('hltv.org' in u for u in external) or
                            any('polymarket.com' in u for u in external) or
                            any('github.com/ValveSoftware' in u for u in external) or
                            any('bo3.gg' in u for u in external))
        for ident in open_ids:
            self.assertIn('match-%s' % ident, self.picks + self.index)

    def test_the_two_shipped_stylesheets_match_and_are_brace_balanced(self):
        rooted = (ROOT / 'assets' / 'style.css').read_text()
        canonical = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        self.assertEqual(rooted, canonical)
        self.assertEqual(rooted.count('{'), rooted.count('}'))
        # Upstream PR #267 (4ed657ce) put a compact quick nav on the first phone
        # screen instead of moving the full bar. The geometry is measured by
        # verification-e9be3e6b/mobile_probe.cjs.
        self.assertIn('body[data-page="index"] main>#exec-quicknav{order:3}', rooted)
        self.assertIn('.exec-quicknav{display:none}', rooted)

    def test_this_session_published_its_flagged_irregularities(self):
        ids = {n.get('id') for n in self.notes}
        for required in ('session-e9be3e6b-vrs-vintage-2026-10-24',
                         'session-e9be3e6b-egw-listing-vs-detail-2026-10-24',
                         'session-e9be3e6b-divergent-short-price-2026-10-24'):
            self.assertIn(required, ids)
        for note in self.notes:
            if str(note.get('id') or '').startswith('session-e9be3e6b-'):
                self.assertTrue(note.get('finding'))
                for source in note.get('sources') or []:
                    self.assertTrue(str(source.get('url') or '').startswith('https://'))


if __name__ == '__main__':
    unittest.main()
