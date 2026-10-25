"""Session 85087497 (2026-10-25): the two measured publication blockers and
the first-phone-screen clarifications.

1. Publisher freeze. The live board served the 2026-10-25T01:47Z snapshot all
   morning and withheld every pick; scheduled runs 40170923727 (06:56Z) and
   40193317196 (12:29Z) failed at "Build and independently verify every row".
   The non-publishing harvest on this branch (run 40197633940) reproduced it
   exactly: refresh and quarantine succeeded, the independent auditor found
   0 failures, and `scripts.validate` asserted "Model roster has no HLTV
   source on this row" for fixture 1086697 (Projeto do KinGui vs Yawara).
   HLTV's exact-pair/exact-start page names the club "Tropa do KinGui" — a
   sourced identity-register alias with the identical starting five — which
   the collector and the auditor accept through `norm`, while the validator
   compared raw labels. `lineup_source_ok` now requires the *same* register
   team and still the *exact* five players.

2. 320x568 fold. On the same fresh board, picks.html's first row put its
   probabilities at y=519 against a tab-bar top of y=507 (browser gate).
   Short-phone picks cards return ~34px of chrome; no font or content change.
   The browser measurement itself lives in tests/browser_019a253a.cjs; here we
   pin the CSS so the two shipped copies cannot drift apart.

3. Executive summary wording/links. The phone quick-nav's "unresolved" count
   is the no-percentage count; it now says so ("unresolved (no %)"), and the
   always-visible summary bar links the method page in one tap.
"""
import copy
import json
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build, summary
from scripts.core import IDENTITIES, plain_name
from scripts.validate import lineup_source_ok, validate_data

ROOT = Path(__file__).resolve().parents[1]
PLAYERS = ['Player One', 'Player Two', 'Player Three', 'Player Four', 'Player Five']


def _alias_pair():
    """One register entry whose two labels differ as raw text (rotation-proof)."""
    for item in IDENTITIES:
        names = item.get('names') or []
        for other in names:
            if plain_name(other) != plain_name(item['canonical']):
                return item['canonical'], other
    raise AssertionError('identity register holds no textual alias pair to test')


class AliasLineupSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical, cls.alias = _alias_pair()

    def _row(self, source_label, players=PLAYERS):
        return {'id': '85087497', 'teams': [self.alias, 'Opponent Club'],
                'hltv_context': {'lineups': [
                    {'team': source_label, 'players': list(players)},
                    {'team': 'Opponent Club', 'players': list(PLAYERS)}]}}

    def test_register_alias_label_with_exact_players_is_sourced(self):
        # HLTV prints the canonical label; the fixture uses the alias (or the
        # reverse). Either direction is the same register team.
        self.assertTrue(lineup_source_ok(self._row(self.canonical), self.alias, PLAYERS))
        row = self._row(self.alias)
        self.assertTrue(lineup_source_ok(row, self.canonical, PLAYERS))

    def test_exact_label_still_sourced(self):
        self.assertTrue(lineup_source_ok(self._row(self.alias), self.alias, PLAYERS))

    def test_alias_label_with_a_different_player_fails(self):
        changed = PLAYERS[:-1] + ['Never On This Roster']
        self.assertFalse(lineup_source_ok(self._row(self.canonical), self.alias, changed))

    def test_unregistered_label_with_exact_players_fails(self):
        self.assertFalse(lineup_source_ok(self._row('Totally Different Club'), self.alias, PLAYERS))

    def test_empty_lineup_fails(self):
        self.assertFalse(lineup_source_ok(self._row(self.canonical), self.alias, []))

    def test_team_page_branch_also_uses_the_register_and_the_url(self):
        row = {'id': '85087497', 'teams': [self.alias, 'Opponent Club'],
               'hltv_team_pages': {'teams': [
                   {'team': self.canonical, 'url': 'https://www.hltv.org/team/13151/example',
                    'players': list(PLAYERS)}]}}
        self.assertTrue(lineup_source_ok(row, self.alias, PLAYERS))
        row['hltv_team_pages']['teams'][0]['url'] = 'https://example.invalid/team/13151/example'
        self.assertFalse(lineup_source_ok(row, self.alias, PLAYERS))


class FreshBoardRegressionTests(unittest.TestCase):
    def test_retained_fresh_snapshot_validates(self):
        path = ROOT / 'research' / 'harvest-85087497' / 'refresh-snapshot.json'
        if not path.exists():
            self.skipTest('harvest snapshot not retained in this tree')
        data = json.loads(path.read_text())
        # The exact assertion that froze the publisher must not fire on the
        # board that froze it (validate_data replays at the snapshot clock).
        validate_data(data)
        row = next((m for m in data['matches'] if m['id'] == '1086697'), None)
        if row is not None and row.get('method') == 'model_vrs':
            quote = row['evidence'][0]
            check = quote['roster_checks'][0]
            self.assertTrue(lineup_source_ok(row, row['teams'][0], check.get('lineup') or []))


class ShortPhonePicksCssTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        cls.root = (ROOT / 'assets' / 'style.css').read_text()

    def test_copies_identical_and_balanced(self):
        self.assertEqual(self.site, self.root)
        self.assertEqual(self.site.count('{'), self.site.count('}'))

    def test_short_phone_picks_compaction_present(self):
        marker = 'Session 85087497'
        self.assertIn(marker, self.site)
        block = self.site[self.site.index(marker):]
        for needle in ('@media(max-width:650px) and (max-height:700px)',
                       'body[data-page=picks] .page-head{margin-bottom:10px}',
                       'body[data-page=picks] caption{padding:8px 11px;margin-bottom:8px}',
                       'body[data-page=picks] tbody tr{padding:12px;gap:10px 14px}',
                       'body[data-page=picks] td.team-col{padding-bottom:9px}'):
            self.assertIn(needle, block, needle)


class ExecutiveSummaryClarityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'data' / 'latest.json').read_text())
        cls.soup = BeautifulSoup(build.overview(copy.deepcopy(cls.data)), 'html.parser')

    def test_summary_bar_links_the_method_page(self):
        bar = self.soup.select_one('#exec-summary')
        self.assertIsNotNone(bar)
        hrefs = {a.get('href') for a in bar.select('a[href]')}
        self.assertIn('sources.html#method', hrefs)
        # The pre-existing in-site routes stay.
        self.assertTrue({'picks.html', '#picks-at-a-glance', 'unresolved.html',
                         '#unresolved-summary', '#unresolved-limits', 'matches.html',
                         'review.html'} <= hrefs)

    def test_quicknav_says_what_its_unresolved_count_counts(self):
        quick = self.soup.select_one('#exec-quicknav')
        self.assertIsNotNone(quick)
        c = summary.counts(self.data['matches'])
        text = re.sub(r'\s*/\s*', '/', quick.get_text(' ', strip=True))
        self.assertIn('%d/%d picks' % (c['with_pick'], c['open']), text)
        self.assertIn('%d unresolved (no %%)' % c['without_percentage'], text)


if __name__ == '__main__':
    unittest.main()
