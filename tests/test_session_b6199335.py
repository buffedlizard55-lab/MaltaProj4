"""Session b6199335: the pipeline that publishes the board must be able to run.

Three defects found by reading the repository on 2026-10-24, each reproduced
before it was changed and each pinned here so it cannot come back silently:

1. **A frozen fixture list in a test deadlocked publishing.** Every scheduled
   run of `Verify, refresh and publish CS2 Scout` had failed since 13:27Z on
   2026-10-23 at the unit-test step, so the board served one snapshot for 17h47m.
   `tests/test_session_0cc1138a.py` required the 30 fixtures seen on the lobby at
   09:44Z to stay on the board for ever; Hotspawn drops a fixture when it
   finishes, so the assertion could never hold again. The parity claim that
   matters -- the three official views agree with the retained board -- is
   re-derived from each snapshot and is asserted in that module.

2. **The phone layout only applied to short phones.** A missing closing brace in
   `site/assets/style.css` nested the entire `@media(max-width:650px)` phone
   block inside `@media(max-width:650px) and (max-height:700px)`. On a 390x844
   phone the rules never matched, so the pick list stayed below the folded guide
   and the first pick was measured at y=868, off the first screen. This module
   proves the stylesheet parses and that the phone rule is reachable at an
   ordinary phone height.

3. **Two browser suites asserted time-dependent behaviour against the wall
   clock,** so they only passed within eight hours of a build. They now pin the
   page clock to the snapshot under test (`tests/pinned-clock.cjs`).

None of these tests asserts a number that the snapshot itself does not carry.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_COPIES = [ROOT / 'site' / 'assets' / 'style.css', ROOT / 'assets' / 'style.css']
DATA = json.loads((ROOT / 'data' / 'latest.json').read_text())


def brace_depth_before(source, needle):
    """CSS nesting depth at `needle`, counting only braces outside comments.

    Returns (depth, [(line, selector-prefix) for each open block]). A rule is
    reachable at top level only when the depth is 0.
    """
    index = source.find(needle)
    if index < 0:
        raise AssertionError('selector not found: %r' % needle)
    body = re.sub(r'/\*.*?\*/', '', source[:index], flags=re.S)
    stack, line = [], 1
    for char in body:
        if char == '\n':
            line += 1
        elif char == '{':
            stack.append(line)
        elif char == '}' and stack:
            stack.pop()
    return len(stack), stack


class StylesheetIsParsable(unittest.TestCase):
    """A missing brace silently disables every rule after it."""

    def test_every_committed_copy_balances_its_braces_and_parens(self):
        for path in CSS_COPIES:
            source = re.sub(r'/\*.*?\*/', '', path.read_text(), flags=re.S)
            self.assertEqual(source.count('{'), source.count('}'),
                             '%s has unbalanced CSS blocks' % path)
            self.assertEqual(source.count('('), source.count(')'),
                             '%s has unbalanced CSS parentheses' % path)

    def test_the_two_committed_copies_are_identical(self):
        # The build serves one of these and the tests read the other; drift
        # between them is how a "verified" fix fails to reach the visitor.
        self.assertEqual(CSS_COPIES[0].read_bytes(), CSS_COPIES[1].read_bytes())

    def test_the_phone_layout_is_reachable_at_an_ordinary_phone_height(self):
        # 390x844 is the common modern phone. Before the repair this rule sat two
        # blocks deep, inside `max-height:700px`, so 390x844 never matched it and
        # the first pick was measured at y=868 instead of y=434.
        source = CSS_COPIES[0].read_text()
        depth, stack = brace_depth_before(source, 'body[data-page="index"] main>#picks-at-a-glance{order:4}')
        self.assertEqual(depth, 1, 'the order rule is nested inside blocks opened at %r' % stack)

    def test_no_phone_rule_is_trapped_inside_a_short_screen_query(self):
        # Every `body[data-page="index"]` phone rule must live in the plain
        # max-width block, never in the max-height one.
        source = CSS_COPIES[0].read_text()
        for needle in (
            'body[data-page="index"] main>#picks-at-a-glance{order:4}',
            'body[data-page="index"] main>#unresolved-limits',
            'body[data-page="index"] #picks-at-a-glance>.glance-list',
        ):
            if needle not in source:
                continue
            depth, stack = brace_depth_before(source, needle)
            self.assertEqual(depth, 1, '%r is nested in %r' % (needle, stack))

    def test_a_short_screen_query_does_not_swallow_the_next_block(self):
        source = CSS_COPIES[0].read_text()
        short_queries = [m.start() for m in re.finditer(
            r'@media\(max-width:650px\) and \(max-height:700px\)', source)]
        self.assertTrue(short_queries, 'the short-screen block should still exist')
        # Each query's block must close before the next top-level comment that
        # introduces an unrelated section, or the following rules are captured.
        for start in short_queries:
            tail = source[start:]
            close = tail.find('\n}\n')
            self.assertGreater(close, 0, 'short-screen query never closes')
            captured = tail[:close]
            self.assertNotIn('body[data-page="index"] main>#picks-at-a-glance',
                             captured,
                             'a short-screen query swallowed the main phone layout')


class ClockPinnedBrowserSuites(unittest.TestCase):
    """Suites that assert a layout must not depend on when they are run."""

    def test_the_pinned_clock_helper_pins_the_constructor_not_only_now(self):
        helper = (ROOT / 'tests' / 'pinned-clock.cjs').read_text()
        self.assertIn('class PinnedDate extends RealDate', helper)
        self.assertIn('static now()', helper)
        self.assertIn('args.length === 0', helper)

    def test_the_suites_that_measure_layout_pin_the_snapshot_clock(self):
        for name in ('browser_f0814674.cjs', 'browser_9b97d585.cjs'):
            source = (ROOT / 'tests' / name).read_text()
            self.assertIn("require('./pinned-clock.cjs')", source, name)
            self.assertIn('clockScript(', source, name)

    def test_neither_suite_pins_the_clock_with_a_bare_date_now_override(self):
        # `Date.now = () => t` alone leaves `new Date()` on the wall clock, which
        # is how the first attempt at this repair produced a future-dated
        # snapshot and tripped app.js's clock-skew guard instead.
        for name in ('browser_f0814674.cjs', 'browser_9b97d585.cjs'):
            source = (ROOT / 'tests' / name).read_text()
            self.assertNotIn('Date.now = () => t', source, name)


class CoverageParityIsDerivedNotPinned(unittest.TestCase):
    """The claim the summary makes must be true of every snapshot, not of one."""

    def test_the_retired_fixture_pin_is_gone(self):
        source = (ROOT / 'tests' / 'test_session_0cc1138a.py').read_text()
        self.assertNotIn(
            "self.OBSERVED_OPEN - known - removed", source,
            'a frozen lobby list must not be able to fail the publish again')
        self.assertIn('test_board_matches_the_snapshots_own_official_views', source)

    def test_this_snapshots_views_agree_with_the_retained_board(self):
        counts = DATA.get('coverage_counts') or {}
        rows = len(DATA['matches'])
        for view in ('api', 'page', 'lobby', 'retained'):
            self.assertEqual(counts.get(view), rows, view)

    def test_every_retained_row_has_an_official_fixture_source(self):
        for row in DATA['matches']:
            urls = [s.get('url', '') for s in row.get('fixture_sources') or []]
            self.assertTrue(urls, row['id'])
            self.assertTrue(all(url.startswith('https://') for url in urls), row['id'])


class UnresolvedClassIsPublishable(unittest.TestCase):
    """An unresolved row is allowed, but only with its limitation attached."""

    def open_rows(self):
        return [m for m in DATA['matches'] if m.get('state') == 'open']

    def test_no_open_row_is_silently_blank(self):
        for row in self.open_rows():
            if row.get('pick'):
                continue
            self.assertTrue(row.get('reason'), row['id'])
            self.assertTrue(row.get('attempts'), row['id'])
            self.assertTrue(any((a.get('url') or '').startswith('https://')
                                for a in row['attempts']), row['id'])

    def test_a_published_pick_names_one_of_the_two_teams(self):
        for row in self.open_rows():
            if row.get('pick'):
                self.assertIn(row['pick'], row['teams'], row['id'])


if __name__ == '__main__':
    unittest.main()
