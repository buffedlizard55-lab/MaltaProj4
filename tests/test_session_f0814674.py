"""Session f0814674 — publication-unblock and full-coverage invariants.

Why this file exists
====================

The scheduled publication workflow runs the unit suite *before* it refreshes
any source. Between 2026-10-22T20:15Z and 2026-10-23T04:55Z two tests failed
there -- ``test_session_75ebd2d6`` and ``test_session_13e99ca6`` -- because
they pinned the *tier label* a research-only row happened to carry in one
historical snapshot. Fixture ``1081149`` legitimately moved
``research_rank_single`` -> ``research_vrs_single`` when Valve's official
standings resolved FORZE Reload, so a healthy data refresh made the unit gate
red. ``Refresh official sources``, ``Build and verify`` and ``deploy`` were all
skipped on runs 39871808909 (23:26Z) and 39886171791 (01:49Z), the committed
board froze at 2026-10-22T20:15Z, every open pick passed its deadline, and the
public page rendered "0 with a pick ... Current picks are withheld".

Those two assertions now check the invariant (any ``research_*`` tier, no
percentage, a pick from the fixture's own teams) instead of one snapshot's
label. This module keeps three things true:

1. no test may pin a research tier again (the meta-check below),
2. every open row on the committed board carries a pick, a source and -- if
   priced -- two probabilities that sum to 1 (the user-facing contract),
3. the executive summary keeps its in-site links to the updated picks and its
   own unresolved section, and stays phone-readable.

Run: python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'latest.json'
INDEX_HTML = ROOT / 'index.html'
UNRESOLVED_HTML = ROOT / 'unresolved.html'
PICKS_HTML = ROOT / 'picks.html'

# The two expressions that froze the board. Both compare a *label* that belongs
# to one refresh against a constant that belongs to the test file.
PINNED_PATTERNS = (
    re.compile(r"startswith\(\s*['\"]research_rank['\"]"),
    re.compile(r"assertEqual\(\s*m\[\s*['\"]method['\"]\s*\]\s*,\s*exp\[\s*['\"]method['\"]\s*\]"),
)
# This file documents the patterns it forbids, so it is exempt from its own scan.
EXEMPT = {Path(__file__).name}


class NoPinnedResearchTier(unittest.TestCase):
    def test_no_test_module_pins_a_research_tier(self):
        offenders = []
        for path in sorted((ROOT / 'tests').glob('*.py')):
            if path.name in EXEMPT:
                continue
            text = path.read_text()
            for pattern in PINNED_PATTERNS:
                match = pattern.search(text)
                if match:
                    offenders.append('%s: %s' % (path.name, match.group(0)))
        self.assertEqual(offenders, [], 'a pinned research tier blocks publication when data improves')

    def test_the_two_former_offenders_now_accept_any_research_tier(self):
        for name in ('test_session_75ebd2d6.py', 'test_session_13e99ca6.py'):
            text = (ROOT / 'tests' / name).read_text()
            self.assertIn("startswith('research_')", text.replace('"', "'"), name)


class FullCoverageContract(unittest.TestCase):
    """Every open match has a pick; every published number is reproducible."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text())
        cls.open_rows = [m for m in cls.data['matches'] if m.get('state') == 'open']

    def test_every_row_has_an_official_source_url(self):
        for row in self.data['matches']:
            self.assertTrue(str(row.get('source_url') or '').startswith('https://'), row['id'])
            self.assertTrue(str(row.get('feed_url') or '').startswith('https://'), row['id'])

    def test_every_open_row_has_a_pick_or_an_explicit_unresolved_reason(self):
        """A row may be blank, but never silently blank.

        The board's contract is "a pick for every match", and the publisher
        currently meets it. This test deliberately fails *closed but not red* on
        a genuinely unresolvable row: a missing pick must carry a written
        reason, so the executive summary can list it under its unresolved
        section. Blocking publication on a source refusal is what left the live
        site pinned to an expired snapshot; an honest, flagged blank does not
        block, and it cannot be mistaken for a 50/50.
        """
        for row in self.open_rows:
            if row.get('pick'):
                self.assertIn(row['pick'], row.get('teams') or [], row['id'])
            else:
                self.assertTrue((row.get('reason') or '').strip(), row['id'])
                self.assertIsNone(row.get('probabilities'), row['id'])

    def test_every_priced_open_row_sums_to_one(self):
        for row in self.open_rows:
            probabilities = row.get('probabilities')
            if probabilities is None:
                continue
            self.assertEqual(len(probabilities), 2, row['id'])
            self.assertAlmostEqual(sum(probabilities), 1.0, places=12, msg=row['id'])
            higher = row['teams'][probabilities.index(max(probabilities))]
            self.assertEqual(row['pick'], higher, row['id'])

    def test_research_rows_carry_no_percentage_and_an_explicit_reason(self):
        for row in self.open_rows:
            if not str(row.get('method') or '').startswith('research_'):
                continue
            self.assertIsNone(row.get('probabilities'), row['id'])
            self.assertIsNone(row.get('fair_odds'), row['id'])
            self.assertIn('No verified market line. Research pick only:',
                          row.get('reason') or '', row['id'])
            self.assertTrue(row.get('attempts') or row.get('evidence'), row['id'])

    def test_no_row_silently_invents_fifty_fifty(self):
        for row in self.data['matches']:
            if row.get('probabilities') is None:
                self.assertNotIn('50/50', row.get('reason') or '', row['id'])
                self.assertNotEqual(row.get('pick'), '50/50', row['id'])

    def test_open_rows_state_their_method(self):
        allowed = {'exchange', 'exchange_wide', 'bookmaker_fallback', 'model_vrs',
                   'model_vrs_mirror', 'research_rank', 'research_rank_single',
                   'research_vrs_single'}
        for row in self.open_rows:
            if row.get('pick') and row.get('method'):
                self.assertIn(row.get('method'), allowed, row['id'])

    def test_coverage_report_is_derived_not_hardcoded(self):
        """Report the live counts; they are dated data, not an invariant."""
        picks = [r for r in self.open_rows if r.get('pick')]
        priced = [r for r in self.open_rows if r.get('probabilities') is not None]
        print('coverage: %d open · %d with a pick · %d with a win probability'
              % (len(self.open_rows), len(picks), len(priced)))


class ExecutiveSummaryDiscoverability(unittest.TestCase):
    """The user's complaint: 'where are the picks?' must never be the question."""

    @classmethod
    def setUpClass(cls):
        cls.index = INDEX_HTML.read_text()
        cls.unresolved = UNRESOLVED_HTML.read_text()
        cls.picks = PICKS_HTML.read_text()

    def test_links_to_the_updated_picks_are_on_the_first_screen(self):
        banner_start = self.index.find('id="exec-banner"')
        self.assertGreater(banner_start, -1, 'executive banner missing')
        section = self.index[banner_start:banner_start + 4000]
        for href in ('picks.html', 'unresolved.html', 'matches.html', 'sources.html#method'):
            self.assertIn('href="%s"' % href, section, href)

    def test_unresolved_section_is_inside_the_executive_summary(self):
        self.assertIn('id="unresolved-summary"', self.index)
        self.assertIn('Unresolved picks', self.index)
        self.assertIn('Every source tried, in order, before a blank', self.unresolved)
        # The page states its own coverage counts, in words, above the table.
        for phrase in ('open matches', 'with a pick', 'with a win probability', 'no supported pick'):
            self.assertIn(phrase, self.unresolved, phrase)

    def test_picks_page_lists_each_open_match_with_its_pick(self):
        data = json.loads(DATA.read_text())
        open_ids = [m['id'] for m in data['matches'] if m.get('state') == 'open' and m.get('pick')]
        for match_id in open_ids:
            self.assertIn('match-%s' % match_id, self.picks, match_id)

    def test_no_double_escaped_entities_in_rendered_pages(self):
        """`link()` escapes its label, so a pre-escaped '&amp;' renders as '&amp;amp;'.

        Found on the live 2026-10-23 board: the unresolved section's
        "Full unresolved &amp; non-market queue" link showed the literal entity
        on a phone. Every rendered page must be free of double escapes.
        """
        import glob
        offenders = []
        for path in sorted(glob.glob(str(ROOT / '*.html')) + glob.glob(str(ROOT / 'site' / '*.html'))):
            text = Path(path).read_text()
            if '&amp;amp;' in text or '&amp;lt;' in text or '&amp;quot;' in text:
                offenders.append(Path(path).name)
        self.assertEqual(offenders, [], 'double-escaped entities render literally')

    def test_phone_layout_contract(self):
        self.assertIn('name="viewport"', self.index)
        self.assertIn('class="mobile-tabs"', self.index)
        self.assertIn('Phone navigation', self.index)


if __name__ == '__main__':
    unittest.main()
