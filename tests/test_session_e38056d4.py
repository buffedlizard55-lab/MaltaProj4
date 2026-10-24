"""Session e38056d4 (2026-10-24): the board stays publishable, and a phone can find it.

Two rules this session had to repair or re-verify, neither pinned anywhere else:

1. A root-fallback gate failure may never discard a verified board. Measured on
   `main`: runs 40082763751 (09:38Z), 40084520702 (10:05Z), 40097410704 (13:16Z)
   and the 16:06Z slot all failed at *Keep the legacy main:/ root fallback on the
   verified build* after refresh, quarantine, the independent row audit, build,
   validate and twelve browser suites had passed. The step's `exit 1` skipped
   `upload-pages-artifact` and `deploy`, so the live site kept the 08:26Z root
   until its eight-hour window closed at 16:06:51Z and started withholding every
   pick. The gate still refuses the *commit*; it no longer kills the *run*, and
   the failing names are recorded so the next occurrence is diagnosable.

2. The executive summary has to name where the picks are, and carry a separate
   unresolved/limitations section, in markup a phone renders without opening a
   disclosure. Both blocks must exist even when nothing is missing, because
   "0 unresolved today" is not a claim about tomorrow.

Nothing here pins a fixture ID, team, count or calendar day: the structural
assertions are re-run against whatever snapshot is committed.
"""
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.build import overview, page

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github/workflows/pages.yml').read_text(encoding='utf-8')
STEP_NAME = '      - name: Keep the legacy main:/ root fallback on the verified build'
NEXT_STEP = '      - name: Record the exact artifact expected at the public site'
STEP = WORKFLOW.split(STEP_NAME, 1)[1].split(NEXT_STEP, 1)[0]


def committed():
    return json.loads((ROOT / 'data/latest.json').read_text())


def soup_of(data):
    return BeautifulSoup(overview(data), 'html.parser')


class RootGateCannotDiscardAVerifiedBoard(unittest.TestCase):
    def test_a_failed_staged_root_is_a_warning_not_a_dead_run(self):
        # Both the first pass and the replay path: warn, keep the root, exit 0.
        self.assertEqual(STEP.count('[ "$rc" = "3" ] && {'), 2)
        for line in STEP.splitlines():
            if '[ "$rc" = "3" ] && {' in line:
                self.assertIn('::warning::', line)
                self.assertIn('still deployed', line)
                self.assertIn('exit 0', line)
                self.assertNotIn('::error::', line)

    def test_the_gate_still_blocks_the_commit_and_names_what_failed(self):
        # Fatal for the commit: validate and the suite both return 3, and the
        # suite's failing names are written to runtime/ and the job summary
        # before that decision -- 2026-10-24's runs published only an exit code.
        self.assertIn('python -m scripts.validate --data data/latest.json --site . || return 3', STEP)
        self.assertIn('python -m unittest discover -s tests > runtime/staged-root-units.log 2>&1', STEP)
        self.assertIn('runtime/staged-root-failures.txt', STEP)
        self.assertIn('GITHUB_STEP_SUMMARY', STEP)
        self.assertIn('[ "$units" = "0" ] || return 3', STEP)
        self.assertLess(STEP.index('staged-root-failures.txt'),
                        STEP.index('[ "$units" = "0" ] || return 3'))

    def test_the_deploy_is_downstream_of_this_step(self):
        # The point of the change: the artifact upload and the deploy step are
        # gated on this job succeeding, so this step must not fail the job for a
        # reason that is not about the verified bytes.
        self.assertLess(WORKFLOW.index(STEP_NAME), WORKFLOW.index('upload-pages-artifact'))
        self.assertLess(WORKFLOW.index(STEP_NAME), WORKFLOW.index('name: Deploy verified static dashboard'))


class ExecutiveSummaryNamesWhereThePicksAre(unittest.TestCase):
    def test_the_summary_is_never_inside_a_disclosure(self):
        soup = soup_of(committed())
        summary = soup.find(id='exec-summary')
        self.assertIsNotNone(summary, 'the executive summary must always render')
        self.assertIsNone(summary.find_parent('details'),
                          'the executive summary may not sit inside a folded disclosure')
        links = {a.get('href') for a in summary.find_all('a')}
        for required in ('picks.html', 'unresolved.html', 'matches.html', 'review.html'):
            self.assertIn(required, links, 'the executive summary must link inside this site to %s' % required)
        self.assertTrue(any(href and href.startswith('#') for href in links),
                        'the executive summary must point at the sections on this page')

    def test_the_unresolved_section_is_separate_and_outside_the_disclosure(self):
        soup = soup_of(committed())
        block = soup.find(id='unresolved-limits')
        self.assertIsNotNone(block, 'the separate unresolved/limitations section must always render')
        self.assertIsNone(block.find_parent('details'),
                          'the unresolved/limitations section must be readable without opening a disclosure')
        text = block.get_text(' ', strip=True)
        self.assertIn('limitation', text.lower())
        # The ladder (HLTV first, then an esportsbook, then our own originated
        # line) has to be named where a reader meets the blanks, not only on the
        # method page.
        for rung in ('HLTV', 'esportsbook', 'Valve'):
            self.assertIn(rung, text)
        self.assertIn('unresolved.html', {a.get('href') for a in block.find_all('a')})

    def test_the_section_still_renders_when_nothing_is_unresolved(self):
        data = committed()
        for match in data['matches']:
            match['state'] = 'not_open'
            match['probabilities'] = None
            match['fair_odds'] = None
            match['pick'] = None
            match['method'] = None
        soup = soup_of(data)
        self.assertIsNotNone(soup.find(id='unresolved-limits'))
        self.assertIsNotNone(soup.find(id='exec-summary'))

    def test_an_unpriced_open_match_is_named_in_the_section(self):
        data = committed()
        opens = [m for m in data['matches'] if m.get('state') == 'open']
        if not opens:
            self.skipTest('no open row in the committed snapshot to unpick')
        victim = opens[0]
        victim['probabilities'] = None
        victim['fair_odds'] = None
        victim['pick'] = None
        victim['method'] = None
        victim['attempts'] = [{'provider': 'HLTV', 'status': 'unresolved',
                               'reason': 'no exact fixture identity',
                               'url': 'https://www.hltv.org/matches'}]
        html = overview(data)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.find(id='unresolved-limits').get_text(' ', strip=True)
        self.assertIn('no win percentage', text.lower())
        self.assertIn('HLTV', text)
        # A blank is never a 50/50 and never a typed number.
        self.assertNotIn(victim['teams'][0] + ' 50', text)


class PhoneOrderingKeepsThePicksFirst(unittest.TestCase):
    def test_both_stylesheet_copies_put_the_pick_list_before_the_folded_guide(self):
        for copy in ('site/assets/style.css', 'assets/style.css'):
            css = (ROOT / copy).read_text(encoding='utf-8')
            rule = 'body[data-page="index"] main>#picks-at-a-glance{order:4}'
            self.assertIn(rule, css, '%s must keep the pick list on the first phone screen' % copy)
            self.assertLess(css.index(rule), css.index('body[data-page="index"] main>details.briefing-more{order:6}'))
            self.assertEqual(css.count('{') - css.count('}'), 0, '%s must stay brace-balanced' % copy)

    def test_the_phone_tab_bar_links_the_picks_and_the_unresolved_page(self):
        data = committed()
        soup = BeautifulSoup(page('index', 'Executive summary', overview(data), data), 'html.parser')
        tabs = soup.find('nav', class_='mobile-tabs')
        self.assertIsNotNone(tabs, 'the phone tab bar must always render')
        hrefs = {a.get('href') for a in tabs.find_all('a')}
        self.assertIn('picks.html', hrefs)
        self.assertIn('unresolved.html', hrefs)
        self.assertEqual(len(tabs.find_all('a')), 5, 'the phone bar carries exactly five destinations')


if __name__ == '__main__':
    unittest.main()
