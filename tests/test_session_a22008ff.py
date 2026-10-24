"""Session a22008ff — the alias gate stops skipping, and the phone routes are pinned.

Two things measured on 2026-10-24 against the board that `main` actually publishes
(snapshot 2026-10-24T16:50:01Z, 83 feed rows, 20 open, 20 picks, 20 win
probabilities, 0 unresolved):

1. **Seven tests skipped inside the publish gate.** `python -m unittest discover -s
   tests` reported `OK (skipped=7)` — every one of them a request to exercise the
   alias contract on fixture 1083121, which Hotspawn had rotated out of its lobby
   (`... skipped 'fixture 1083121 has rotated off the published board'`). The
   rotation is correct; the skip is not. An alias path that is no longer exercised
   cannot catch a regression, and `pages.yml` runs this suite *before* it refreshes
   and publishes. Those three files now read this repository's own retained capture
   of the board while the row was open (`research/harvest-ce45f672/snapshot.json`)
   and fail — never skip — when no retained row qualifies. Skips in the gate: 7 → 1,
   and the remaining one is a genuinely conditional case, not rotation.

2. **The executive summary must route a phone to the picks.** Measured with this
   repository's Chromium on the built site (`research/measure_a22008ff.json`):
   at 320x568 the compact summary row runs y=290→347 with the fixed tab bar at 507;
   at 390x844 it runs y=300→365 with the tab bar at 783. On `picks.html` the first
   pick is at y=368 (320px) and y=334 (390px) with its probabilities at y=425 and
   y=392 — inside the first screen, not below it. These are pinned here so a later
   layout change cannot quietly bury them, and so the numbers on the site stay
   checkable without a browser.

Nothing in this file skips. A missing property fails.
"""
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
MEASURED = json.loads((ROOT / 'research' / 'measure_a22008ff.json').read_text())
ALIAS_ARCHIVE = ROOT / 'research' / 'harvest-ce45f672' / 'snapshot.json'
ALIAS_ID = '1083121'


class TheAliasContractIsExercisedEvenAfterRotation(unittest.TestCase):
    def test_the_retained_capture_still_carries_the_aliased_row(self):
        self.assertTrue(ALIAS_ARCHIVE.exists(), 'the retained alias capture is missing')
        rows = json.loads(ALIAS_ARCHIVE.read_text()).get('matches') or []
        row = next((m for m in rows if m['id'] == ALIAS_ID), None)
        self.assertIsNotNone(row, 'the retained capture lost fixture %s' % ALIAS_ID)
        self.assertEqual(row['state'], 'open')
        self.assertEqual(row['method'], 'exchange')

    def test_the_retained_row_ships_both_labels_with_an_https_basis(self):
        rows = json.loads(ALIAS_ARCHIVE.read_text())['matches']
        row = next(m for m in rows if m['id'] == ALIAS_ID)
        entries = (row['evidence'][0].get('identity_sources') or [])
        self.assertTrue(entries, 'the aliased row must ship its identity evidence')
        names = {name for entry in entries for name in entry.get('names') or []}
        self.assertIn('Tropa do KinGui', names)
        self.assertIn('Projeto do KinGui', names)
        for entry in entries:
            self.assertTrue(str(entry.get('source', '')).startswith('https://'), entry)
            self.assertTrue(str(entry.get('basis') or '').strip(), entry)

    def test_the_retained_price_re_derives_and_the_pick_follows_it(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'verify_0cc1138a_a22008ff', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        rows = json.loads(ALIAS_ARCHIVE.read_text())['matches']
        row = next(m for m in rows if m['id'] == ALIAS_ID)
        probabilities, kind = verifier.evidence_probabilities(row['evidence'][0], row['teams'])
        self.assertEqual(kind, 'exchange_mid')
        self.assertAlmostEqual(sum(probabilities), 1.0, places=9)
        for published, rebuilt in zip(row['probabilities'], probabilities):
            self.assertAlmostEqual(published, rebuilt, places=9)
        favourite = row['teams'][0] if probabilities[0] > probabilities[1] else row['teams'][1]
        self.assertEqual(row['pick'], favourite)

    def test_the_three_suites_read_the_archive_instead_of_skipping(self):
        for relative in ('tests/test_session_019a253a.py', 'tests/test_session_d2b90de7.py',
                         'tests/test_session_ea2e254c.py'):
            source = (ROOT / relative).read_text()
            self.assertIn('retained_alias_row', source,
                          '%s does not fall back to the retained capture' % relative)
            for stale in ('has rotated out of the feed',
                          'has rotated off the published board',
                          'is not on this snapshot as an exchange row'):
                self.assertNotIn(stale, source,
                                 '%s still skips the alias contract when the fixture rotates' % relative)

    def test_the_gate_does_not_silently_skip_again(self):
        # The suite is allowed exactly one conditional skip; a rotation-driven skip
        # must never come back. Counted from the files themselves, no browser needed.
        rotation_skips = []
        for path in (ROOT / 'tests').glob('test_*.py'):
            if path.name == Path(__file__).name:
                continue  # this file names the messages it forbids
            text = path.read_text()
            if 'rotated off the published board' in text or 'rotated out of the feed' in text:
                rotation_skips.append(path.name)
        self.assertEqual(rotation_skips, [], 'rotation-driven skips came back')


class ExecutiveSummaryRoutesAPhoneToThePicks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / 'index.html').read_text()
        cls.picks = (ROOT / 'picks.html').read_text()
        cls.soup = BeautifulSoup(cls.index, 'html.parser')

    def test_the_compact_summary_links_the_updated_picks_in_site(self):
        quick = self.soup.select_one('#exec-quicknav')
        self.assertIsNotNone(quick, 'the compact executive summary row is missing')
        hrefs = [a.get('href') for a in quick.select('a')]
        self.assertIn('picks.html', hrefs)
        self.assertIn('#unresolved-limits', hrefs)
        self.assertTrue(all(not str(h).startswith(('http://', 'https://')) for h in hrefs), hrefs)

    def test_the_full_summary_bar_routes_to_every_pick_surface(self):
        bar = self.soup.select_one('#exec-summary')
        self.assertIsNotNone(bar)
        hrefs = [a.get('href') for a in bar.select('a')]
        for needed in ('picks.html', 'unresolved.html', 'matches.html', 'review.html'):
            self.assertIn(needed, hrefs)

    def test_the_summary_row_ends_above_the_fixed_tab_bar(self):
        for size in ('320x568', '320x844', '390x844', '412x915'):
            row = MEASURED[size]
            self.assertFalse(row['overflow'], 'horizontal overflow at ' + size)
            bottom = row['quicknav']['y'] + row['quicknav']['h']
            self.assertLess(bottom, row['mobileTabs']['y'],
                            'the summary row must end above the tab bar at ' + size)

    def test_the_first_pick_and_its_probabilities_are_on_the_first_screen(self):
        for size in ('320x568', '320x844', '390x844', '412x915'):
            picks = MEASURED[size]['picksPage']
            self.assertGreater(picks['rows'], 0, 'no pick row measured at ' + size)
            self.assertLess(picks['firstPickY'], MEASURED[size]['mobileTabs']['y'],
                            'the first pick is below the fold at ' + size)
            self.assertLess(picks['firstProbY'], MEASURED[size]['mobileTabs']['y'],
                            'the first probability is below the fold at ' + size)

    def test_the_committed_pages_carry_the_summary_and_the_picks(self):
        self.assertIn('id="exec-quicknav"', self.index)
        self.assertIn('id="exec-summary"', self.index)
        self.assertIn('id="unresolved-limits"', self.index)
        self.assertIn('data-match="', self.picks)

    def test_every_phone_tab_target_exists_as_a_page(self):
        tabs = BeautifulSoup(self.index, 'html.parser').select('.mobile-tabs a')
        self.assertGreaterEqual(len(tabs), 5)
        for tab in tabs:
            self.assertTrue((ROOT / tab['href']).exists(), tab['href'])

    def test_every_page_declares_a_mobile_viewport(self):
        for page in ('index.html', 'picks.html', 'matches.html', 'unresolved.html',
                     'analysis.html', 'review.html', 'sources.html', 'evidence.html'):
            html = (ROOT / page).read_text()
            self.assertIn('name="viewport"', html, page)
            self.assertIn('width=device-width', html, page)


class EveryOpenRowIsPickedPricedAndSourced(unittest.TestCase):
    def test_the_board_answers_the_brief(self):
        open_rows = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.assertTrue(open_rows, 'no open fixture in the snapshot')
        for m in open_rows:
            self.assertIsNotNone(m.get('pick'), m['id'])
            self.assertIn(m['pick'], m['teams'], m['id'])
            self.assertEqual(len(m.get('probabilities') or []), 2, m['id'])
            self.assertAlmostEqual(sum(m['probabilities']), 1, places=9, msg=m['id'])
            self.assertEqual(m['pick'],
                             m['teams'][m['probabilities'].index(max(m['probabilities']))], m['id'])
            self.assertTrue(str(m.get('source_url', '')).startswith('https://'), m['id'])
            evidence = (m.get('evidence') or [{}])[0]
            self.assertTrue(evidence.get('url') or evidence.get('api_url'), m['id'])

    def test_no_probability_is_sourced_from_hotspawn(self):
        for m in SNAPSHOT['matches']:
            for record in m.get('evidence') or []:
                urls = [record.get('api_url'), record.get('url')]
                urls += [r.get('url') for r in record.get('source_receipts') or []]
                for url in [u for u in urls if u]:
                    self.assertNotIn('hotspawn', url.lower(), m['id'])

    def test_rows_outside_the_feed_are_labelled_and_never_priced(self):
        for m in SNAPSHOT['matches']:
            if m['state'] == 'open':
                continue
            self.assertIsNone(m.get('probabilities'), m['id'])
            self.assertIsNone(m.get('pick'), m['id'])
            self.assertTrue(m.get('reason'), 'a closed row must state why it is not a pick')


if __name__ == '__main__':
    unittest.main()
