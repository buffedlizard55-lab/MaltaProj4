"""Session 8def3206: keep the board publishing, and put the picks in the first tap.

Three changes are pinned here. Each one is a regression guard for a defect that
was reproduced on this checkout, not a restatement of a preference.

1. **Publication was blocked by a clock-dependent test.** ``tests/test_session_
   bf09aa40.py`` replayed a committed ``2026-10-21T21:18:58Z`` model observation
   with ``datetime.now()``. ``scripts.validate.validate_model_row`` refuses model
   inputs older than eight hours, so from ``2026-10-22T05:18Z`` on, the
   "Unit and independent failure-mode tests" step in ``.github/workflows/
   pages.yml`` failed before the refresh ran (scheduled run 39731049149:
   verify-build failed, deploy skipped, live board frozen at 03:33Z). The fixed
   test replays the snapshot at its own ``generated_at``, which is exactly what
   ``scripts.validate`` does. Assertion 1 locks both halves: the replay is fresh
   at the snapshot time, and the production validator still rejects the same
   inputs at a later wall-clock time (so the eight-hour gate is not weakened).

2. **The executive summary put about two phone screens of chrome before the
   first pick.** At 390x844 the first match card now starts at y=702px, i.e.
   inside the first screen; before the change the first pick was far below the
   fold behind a prose navigation block, a coverage panel, a hero and four
   destination cards. The order and the tap targets are asserted, not the pixels.

3. **The independent auditor rejected a normal build output.** A row that
   ``scripts.build`` closes on its deadline rule keeps its historical evidence
   (the ledger must still show what was observed) and has no probabilities, so
   ``verification-7271c5d5/audit_board_7271c5d5.py`` reported "Unpriced row
   carries derived fair_odds or quote evidence". Any snapshot taken after a
   lock passes would fail that check on the next run. The audit now exempts
   exactly that case and still rejects an *open* unpriced row that carries a
   price - both directions are tested here.
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build, vrs  # noqa: E402
from scripts.core import norm, research_rank_pick  # noqa: E402
from scripts.core import dt, iso  # noqa: E402

DATA = json.loads((ROOT / 'data/latest.json').read_text())
CSS = (ROOT / 'assets' / 'style.css').read_text()
AUDIT = ROOT / 'verification-7271c5d5' / 'audit_board_7271c5d5.py'


def phone_block(css):
    """Every rule inside a ``max-width:650px`` block, concatenated.

    Brace-counted rather than regex-matched: the sheet contains nested blocks
    and a lazy regex silently truncates them mid-rule.
    """
    out = []
    marker = '@media(max-width:650px){'
    start = css.find(marker)
    while start != -1:
        depth, index = 0, start + len(marker) - 1
        while index < len(css):
            if css[index] == '{':
                depth += 1
            elif css[index] == '}':
                depth -= 1
                if depth == 0:
                    break
            index += 1
        out.append(css[start + len(marker):index])
        start = css.find(marker, index)
    return ''.join(out)


class PublicationBlockerTests(unittest.TestCase):
    """1. The eight-hour model gate still bites, but the pinned test no longer does."""

    def setUp(self):
        self.snapshot = json.loads((ROOT / 'research/harvest-bf09aa40/snapshot.json').read_text())
        self.row = next(m for m in self.snapshot['matches'] if m['id'] == '1082858')
        self.quote = self.row['evidence'][0]
        self.observed = dt(self.quote['observed_at'])

    def test_the_snapshot_replay_is_fresh_and_the_wall_clock_is_not(self):
        from scripts.validate import validate_model_row
        # The pinned observation is fresh at its own generation time ...
        self.assertLess(abs((dt(self.snapshot['generated_at']) - self.observed)), timedelta(minutes=5))
        validate_model_row(self.row, self.quote, dt(self.snapshot['generated_at']))
        # ... and the production eight-hour gate is still enforced.
        with self.assertRaises(AssertionError):
            validate_model_row(self.row, self.quote, self.observed + timedelta(hours=9))

    def test_that_module_passes_when_the_clock_is_a_day_later(self):
        """Run the fixed module under a +24h clock: a pinned replay must not expire."""
        clock = (
            "import datetime as m, sys, unittest\n"
            "real = m.datetime; shift = m.timedelta(days=1)\n"
            "class F(real):\n"
            "    @classmethod\n"
            "    def now(cls, tz=None):\n"
            "        v = real.now(tz) + shift\n"
            "        return real(v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond, v.tzinfo)\n"
            "    @classmethod\n"
            "    def utcnow(cls):\n"
            "        return cls.now(None)\n"
            "    @classmethod\n"
            "    def today(cls):\n"
            "        return cls.now(None)\n"
            "m.datetime = F\n"
            "suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_session_bf09aa40')\n"
            "sys.exit(0 if unittest.TextTestRunner(verbosity=0).run(suite).wasSuccessful() else 1)\n"
        )
        proc = subprocess.run([sys.executable, '-c', clock], cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, (proc.stderr or proc.stdout)[-800:])

    def test_the_workflow_still_runs_that_test_before_it_publishes(self):
        workflow = (ROOT / '.github' / 'workflows' / 'pages.yml').read_text()
        unit = workflow.index('python -m unittest discover -s tests -v')
        self.assertLess(unit, workflow.index('python -m scripts.refresh --output runtime/latest.json'))
        self.assertIn('python -m unittest discover -s verification-c6', workflow)


class ExecutiveSummaryOrderTests(unittest.TestCase):
    """2. Picks first on a phone, one unambiguous site map, real tap targets."""

    @classmethod
    def setUpClass(cls):
        cls.html = build.overview(deepcopy(DATA))
        cls.soup = BeautifulSoup(cls.html, 'html.parser')

    def test_the_pick_list_comes_before_every_other_block(self):
        order = [self.html.index(k) for k in (
            'id="freshness-strip"',
            'class="exec-summary-links"',
            'id="picks-at-a-glance"',
            'id="coverage-now"',
            'class="hero"',
            'id="start-here"',
            'id="unresolved-picks"',
        )]
        self.assertEqual(order, sorted(order), 'the first content after the strip must be the picks')

    def test_the_site_map_is_four_tap_targets_with_the_right_destinations(self):
        nav = self.soup.select_one('.exec-summary-links')
        self.assertIsNotNone(nav)
        chips = nav.select('a.exec-chip')
        self.assertEqual(len(chips), 4)
        self.assertEqual({a['href'] for a in chips},
                         {'picks.html', '#picks-at-a-glance', 'unresolved.html', 'matches.html'})
        self.assertEqual(sum(1 for a in chips if 'primary' in a.get('class', [])), 1)
        for chip in chips:
            self.assertTrue(chip.get_text(strip=True), 'a chip without a label is not tappable in words')
        # The one primary destination is the updated pick board.
        self.assertEqual(next(a for a in chips if 'primary' in a.get('class', []))['href'], 'picks.html')

    def test_the_duplicate_navigation_blocks_are_gone(self):
        # Prose nav, four destination cards and the two in-page navs used to
        # repeat the same four destinations; only the cards remain (retitled).
        self.assertEqual(len(self.soup.select('.exec-summary-links')), 1)
        start = self.soup.select_one('#start-here')
        self.assertIn('What each page holds', start.get_text(' ', strip=True))
        self.assertNotIn('Where the picks are', start.get_text(' ', strip=True))

    def test_unresolved_picks_and_limits_are_still_in_the_summary(self):
        section = self.soup.select_one('#unresolved-picks')
        self.assertIsNotNone(section)
        limitations = self.soup.select_one('#pick-limitations')
        self.assertIsNotNone(limitations)
        text = limitations.get_text(' ', strip=True)
        for phrase in ('No book lists the match', 'Names differ between sites', 'model needs both teams'):
            self.assertIn(phrase, text)
        # Every unpriced open fixture is listed with its reason.
        unpriced = [m for m in DATA['matches'] if m['state'] == 'open' and m['probabilities'] is None]
        rows = section.select('a.unresolved-row')
        self.assertEqual(len(rows), len(unpriced))
        for li in section.select('li.unresolved-item'):
            self.assertTrue(li.select_one('p.unresolved-why').get_text(strip=True))

    def test_phone_css_keeps_the_picks_and_the_tap_targets(self):
        phone = phone_block(CSS)
        self.assertIn('.exec-chip{min-height:46px', phone)
        self.assertIn('grid-template-columns:1fr 1fr', phone)
        # Duplicated CTAs above the pick list are removed on phones only.
        self.assertIn('.glance-actions{display:none}', phone)
        self.assertIn('.fresh-strip .fresh-links{display:none}', phone)
        # But they are never hidden on the desktop layout.
        desktop = CSS.split('@media(max-width:650px)')[0]
        self.assertNotIn('.glance-actions{display:none}', desktop)
        self.assertNotIn('.fresh-strip .fresh-links{display:none}', desktop)

    def test_the_new_phone_controls_meet_the_44px_target(self):
        for selector in ('.exec-chip', '.board-note>summary', '.coverage-now .actions .button'):
            heights = [int(h) for rule in CSS.split('}') if selector in rule
                       for h in re.findall(r'min-height:(\d+)px', rule)]
            self.assertTrue(heights, f'{selector} declares no min-height')
            self.assertGreaterEqual(max(heights), 44, f'{selector} tap target: {heights}')


class UnresolvedPageTests(unittest.TestCase):
    """The separate unresolved section keeps its ladder, as a disclosure."""

    @classmethod
    def setUpClass(cls):
        cls.html = build.unresolved_page_intro(deepcopy(DATA))
        cls.soup = BeautifulSoup(cls.html, 'html.parser')

    def test_the_ladder_is_still_complete_and_collapsed(self):
        intro = self.soup.select_one('#unresolved-overview')
        self.assertIsNotNone(intro)
        details = intro.select_one('details.board-note')
        self.assertIsNotNone(details)
        steps = details.select('ol.ladder > li')
        self.assertGreaterEqual(len(steps), 7)
        self.assertEqual(len(steps), self.html.count('<li><strong>'))
        # Every step carries its official source link.
        for step in steps:
            self.assertTrue(step.select_one('a[href^="https://"]'), step.get_text(' ', strip=True)[:60])
        self.assertFalse(details.has_attr('open'), 'the ladder must not push the rows down by default')

    def test_the_pick_board_note_is_a_disclosure_and_keeps_its_wording(self):
        # Exercises the real generated page rather than a copy of the string.
        out = Path(tempfile.mkdtemp())
        build.build(deepcopy(DATA), out)
        soup = BeautifulSoup((out / 'picks.html').read_text(), 'html.parser')
        details = soup.select_one('details.board-note')
        self.assertIsNotNone(details)
        text = details.get_text(' ', strip=True)
        self.assertIn('One complete board', text)
        self.assertIn('no percentage', text)
        self.assertTrue(details.select_one('a[href="unresolved.html"]'))
        self.assertFalse(details.has_attr('open'))
        # The filter controls and the first match still follow it on the page.
        self.assertLess(str(soup).index('board-note'), str(soup).index('class="filters"'))


class AuditDeadlineExemptionTests(unittest.TestCase):
    """3. A closed row keeps its evidence; an open unpriced row still fails."""

    def run_audit(self, data):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
            json.dump(data, handle)
            path = handle.name
        return subprocess.run([sys.executable, str(AUDIT), '--snapshot', path, '--site-dir', str(ROOT)],
                              capture_output=True, text=True)

    def test_a_row_closed_by_the_deadline_rule_is_accepted(self):
        data = deepcopy(DATA)
        row = next(m for m in data['matches'] if m['probabilities'] is not None)
        row.update(state='not_open', probabilities=None, fair_odds=None, pick=None, method=None,
                   reason='Source start or pick lock has passed. Historical evidence is not a current recommendation.')
        proc = self.run_audit(data)
        self.assertEqual(proc.returncode, 0, proc.stdout[-400:] or proc.stderr[-400:])
        self.assertEqual(json.loads(proc.stdout)['errors'], [])

    def test_an_open_unpriced_row_that_keeps_a_price_is_still_rejected(self):
        data = deepcopy(DATA)
        row = next(m for m in data['matches'] if m['probabilities'] is not None and m['state'] == 'open')
        row.update(probabilities=None, fair_odds=None, pick=None, method=None,
                   reason='No verified market line for this fixture.')
        proc = self.run_audit(data)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('Unpriced row carries derived fair_odds or quote evidence', json.loads(proc.stdout)['errors'][0])

    def test_a_closed_row_that_still_publishes_a_pick_is_rejected(self):
        """The exemption is narrow: a closed row must clear pick, method and odds."""
        from scripts.validate import validate_data
        data = deepcopy(DATA)
        row = next(m for m in data['matches'] if m['probabilities'] is not None)
        row.update(state='not_open', probabilities=None, fair_odds=None,
                   reason='Source start or pick lock has passed. Historical evidence is not a current recommendation.')
        with self.assertRaises(AssertionError):
            validate_data(data)


class LastUnpickedFixtureTests(unittest.TestCase):
    """Fixture 1082919: identity resolved from primary pages, no line invented."""

    def test_the_register_maps_the_two_labels_to_one_organisation(self):
        register = json.loads((ROOT / 'data/identities.json').read_text())
        entry = next((a for a in register['aliases'] if a['canonical'] == 'Tropa do KinGui'), None)
        self.assertIsNotNone(entry)
        self.assertEqual({norm(n) for n in entry['names']}, {norm('Tropa do KinGui'), norm('Projeto do KinGui')})
        self.assertTrue(entry['source'].startswith('https://www.hltv.org/matches/2399904/'))
        self.assertTrue(entry['additional_source'].startswith('https://www.hltv.org/team/13151/'))
        basis = entry['basis'].lower()
        self.assertIn('utc start', basis)
        self.assertIn('exact opponent', basis)
        # The mapping must not swallow an academy/child team.
        self.assertNotEqual(norm('Projeto do KinGui Academy'), norm('Tropa do KinGui'))

    def test_the_ranking_tier_yields_a_sourced_pick_with_no_percentage(self):
        """Exactly what scripts.hltv.context() records for HLTV match 2399904."""
        fixture = {'id': '1082919', 'state': 'open', 'teams': ['Projeto do KinGui', 'Martians'],
                   'probabilities': None, 'pick': None, 'attempts': [], 'flags': [],
                   'hltv_context': {'ranks': [
                       {'team': 'Tropa do KinGui', 'hltv_rank': None, 'source': 'https://www.hltv.org/matches/2399904/x'},
                       {'team': 'Martians', 'hltv_rank': 240, 'source': 'https://www.hltv.org/matches/2399904/x'}],
                       'limitation': 'HLTV fixture page only; no market price.'}}
        research_rank_pick(fixture)
        self.assertEqual(fixture['pick'], 'Martians')
        self.assertEqual(fixture['method'], 'research_rank_single')
        self.assertIsNone(fixture['probabilities'], 'a research pick must never carry a number')
        self.assertIsNone(fixture['fair_odds'])
        self.assertIn('#240', fixture['reason'])

    def test_no_ranked_teams_means_no_pick(self):
        fixture = {'id': '1082919', 'state': 'open', 'teams': ['Projeto do KinGui', 'Martians'],
                   'probabilities': None, 'pick': None, 'attempts': [], 'flags': [],
                   'hltv_context': {'ranks': [], 'limitation': 'no ranks'}}
        research_rank_pick(fixture)
        self.assertIsNone(fixture['pick'])

    def test_the_discrepancy_is_published_for_review(self):
        notes = json.loads((ROOT / 'data/review-notes.json').read_text())
        note = next((n for n in notes if n.get('id') == '8def3206-alias-scope-projeto-do-kingui-2026-10-22'), None)
        self.assertIsNotNone(note)
        text = (note['finding'] + ' ' + note['status']).lower()
        for phrase in ('vrs: #149', '20.0%/80.0%', 'scope risk', 'no two-way market line'):
            self.assertIn(phrase, text)
        urls = {src['url'] for src in note['sources']}
        self.assertTrue(any('hltv.org/matches/2399904' in u for u in urls))
        self.assertTrue(any('hltv.org/team/13151' in u for u in urls))
        self.assertTrue(any('hotspawn.com/matches/' in u for u in urls))


class CoverageIsUnchangedTests(unittest.TestCase):
    """The presentation changed; no published probability did."""

    def test_every_open_row_still_publishes_a_pick_or_is_flagged(self):
        """Nothing is silently blank: a pick, or a published unresolved row."""
        opens = [m for m in DATA['matches'] if m['state'] == 'open']
        for m in opens:
            if not m.get('pick'):
                # Documented unresolved state (fixture 1082919 is the live case):
                # no probability, a stated reason and at least one source attempt,
                # which the build renders in the summary's unresolved section and
                # on unresolved.html. A manufactured pick would be worse.
                self.assertIsNone(m['probabilities'], m['id'])
                self.assertTrue((m.get('reason') or '').strip(), m['id'])
                self.assertTrue(m.get('attempts'), m['id'])
        for m in opens:
            if m['probabilities'] is not None:
                self.assertAlmostEqual(sum(m['probabilities']), 1.0, places=9, msg=m['id'])
                self.assertIsNotNone(m['fair_odds'], m['id'])
            else:
                self.assertEqual(m['fair_odds'], None, m['id'])
                self.assertTrue(m.get('reason'), m['id'])

    def test_the_build_does_not_invent_a_probability_for_a_blank_row(self):
        data = deepcopy(DATA)
        blank = next(m for m in data['matches']
                     if m['state'] == 'open' and m['probabilities'] is None and m.get('pick'))
        out = Path(tempfile.mkdtemp())
        build.build(data, out)
        built = json.loads((out / 'data/latest.json').read_text())
        row = next(m for m in built['matches'] if m['id'] == blank['id'])
        if row['state'] == 'open':
            self.assertIsNone(row['probabilities'], 'a blank percentage must stay blank')
            self.assertIsNone(row['fair_odds'])


if __name__ == '__main__':
    unittest.main()
