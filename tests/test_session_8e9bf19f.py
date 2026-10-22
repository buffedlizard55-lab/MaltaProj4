"""Independent verification regressions for the integrated 22 October 2026 board.

These tests were written by session 8e9bf19f while merging sessions cb867c3c
(PR #175) and eaff7cce (PR #177). They do not add evidence; they re-derive the
published numbers from the quoted source prices and assert the invariants the
executive summary relies on, so a later edit cannot quietly change a pick,
a percentage, or the discoverability of the picks/unresolved sections.
"""
import json
import html
import unittest
import urllib.parse
from pathlib import Path

from scripts.vrs import calibrated, expected

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data/latest.json').read_text())
# Arithmetic regression belongs to its immutable real source capture, not to a
# future refreshed market's price/tier. Live arithmetic is checked below too.
HISTORICAL = json.loads((ROOT / 'research/session-eaff7cce/historical-priced-rows-0758.json').read_text())
RECEIPTS = HISTORICAL['receipts']
INDEX = (ROOT / 'index.html').read_text()
PICKS = (ROOT / 'picks.html').read_text()

ALLOWED_HOSTS = {
    'polymarket.com', 'www.polymarket.com', 'gamma-api.polymarket.com',
    'www.hltv.org', 'hltv.org', 'stavka.tv', 'www.stavka.tv',
    'www.pinnacle.com', 'guest.api.arcadia.pinnacle.com', 'egamersworld.com', 'www.egamersworld.com',
    'github.com', 'raw.githubusercontent.com', 'api.github.com',
    'www.hotspawn.com', 'play.hotspawn.com',
}


def de_vig(odds):
    implied = [1.0 / float(o) for o in odds]
    total = sum(implied)
    return [x / total for x in implied]


def open_rows():
    return [m for m in SNAPSHOT['matches'] if m.get('state') == 'open']


def by_id(fixture_id, snapshot=None):
    return next(m for m in (SNAPSHOT if snapshot is None else snapshot)['matches'] if str(m['id']) == str(fixture_id))


def early_attested_capture():
    return (SNAPSHOT.get('generated_at') in ('2026-10-22T07:58:54.670274Z', '2026-10-22T08:58:49.178528Z')
            and SNAPSHOT.get('generated_at', '') <= SNAPSHOT.get('built_at', '') < '2026-10-22T10:54:00Z')


class BookmakerLineArithmetic(unittest.TestCase):
    """A quoted two-way price must reproduce the published percentage exactly."""

    def test_stavka_winline_line_reproduces_fixture_1079654(self):
        receipt = next(r for r in RECEIPTS if r.get('fixture_id') == '1079654')
        # Read by hand at 2026-10-22T08:55Z on the match header: "П11.90 [winline] П21.80 [winline]".
        self.assertEqual(receipt['odds'], [1.9, 1.8])
        self.assertEqual(receipt['start'], '2026-10-23T08:00:00Z')
        row = by_id('1079654', HISTORICAL)
        self.assertEqual(row['method'], 'bookmaker_fallback')
        for published, derived in zip(row['probabilities'], de_vig(receipt['odds'])):
            self.assertAlmostEqual(published, derived, places=12)
        self.assertEqual(row['pick'], 'ex-RUSTEC')
        self.assertAlmostEqual(row['fair_odds'][0], 1 / row['probabilities'][0], places=12)

    def test_kin_guide_backup_line_de_vigs_to_the_stored_corroboration(self):
        receipt = next(r for r in RECEIPTS if r.get('fixture_id') == '1082919')
        # Read by hand at 2026-10-22T09:02Z: "П11.06 [winline] П27.26 [winline]".
        self.assertEqual(receipt['odds'], [1.06, 7.26])
        self.assertAlmostEqual(de_vig(receipt['odds'])[0], 0.8726, places=4)
        # The published row stays on the exchange (exchange_wide), never on the book.
        row = by_id('1082919', HISTORICAL)
        self.assertEqual(row['method'], 'exchange_wide')
        self.assertEqual(row['probabilities'], [0.75, 0.25])


class MirrorModelArithmetic(unittest.TestCase):
    """HLTV's dated Valve ranking rows must reproduce our published model lines."""

    def test_mirror_rows_replay_from_their_recorded_points(self):
        rows = [m for m in HISTORICAL['matches'] if m.get('method') == 'model_vrs_mirror']
        self.assertEqual({str(m['id']) for m in rows}, {'1081149', '1081150', '1082926'})
        for row in rows:
            self.assertTrue(row['evidence'][0]['ranking_heading'].startswith('ranking on October 22nd, 2026'))
        # Also reproduce every live mirror row; its date/selection may change.
        rows += [m for m in SNAPSHOT['matches'] if m.get('method') == 'model_vrs_mirror']
        for row in rows:
            evidence = row['evidence'][0]
            self.assertTrue(evidence['url'].startswith('https://www.hltv.org/valve-ranking/teams'))
            self.assertTrue(evidence['ranking_heading'].startswith('ranking on '))
            points = evidence['points']
            self.assertEqual(len(points), 2)
            published = row['probabilities'][0]
            self.assertAlmostEqual(calibrated(expected(*points)), published, places=12)
            self.assertAlmostEqual(row['probabilities'][0] + row['probabilities'][1], 1.0, places=12)


class EveryOpenMatchIsResolvedOrExplained(unittest.TestCase):
    def test_open_rows_have_a_pick_and_a_probability_or_a_reason(self):
        rows = open_rows()
        if early_attested_capture():
            self.assertGreater(len(rows), 0)
        for row in rows:
            if row.get('pick') is None:
                for field in ('probabilities', 'fair_odds', 'method'):
                    self.assertIsNone(row.get(field), msg=(row['id'], field))
                self.assertTrue(row.get('reason'), msg=row['id'])
                self.assertTrue(row.get('attempts'), msg=row['id'])
                self.assertTrue(str(row.get('source_url') or '').startswith('https://'), msg=row['id'])
                continue
            self.assertIn(row['pick'], row['teams'], msg=row['id'])
            if row.get('probabilities'):
                self.assertEqual(len(row['probabilities']), 2)
                self.assertAlmostEqual(sum(row['probabilities']), 1.0, places=12)
            else:
                self.assertTrue(row.get('reason'), msg=row['id'])
                self.assertIn('No verified market line', row['reason'], msg=row['id'])

    def test_only_the_two_research_rows_remain_unpriced(self):
        unpriced = {str(m['id']) for m in open_rows() if not m.get('probabilities')}
        if early_attested_capture():
            self.assertEqual(unpriced, {'1082925', '1082860'})
        for row in open_rows():
            if str(row['id']) in unpriced:
                if row.get('pick') is None:
                    self.assertIsNone(row.get('method'), msg=row['id'])
                    self.assertTrue(row.get('reason'), msg=row['id'])
                else:
                    self.assertTrue(str(row.get('method', '')).startswith('research_'), msg=row['id'])
                self.assertIsNone(row.get('fair_odds'), msg=row['id'])


class EveryCitedSourceIsOfficialAndHttps(unittest.TestCase):
    def test_evidence_urls_are_https_on_known_hosts(self):
        seen = 0
        for row in SNAPSHOT['matches']:
            for evidence in row.get('evidence', []):
                for key in ('url', 'api_url'):
                    url = evidence.get(key)
                    if not url:
                        continue
                    parts = urllib.parse.urlsplit(url)
                    self.assertEqual(parts.scheme, 'https', msg=url)
                    self.assertIn(parts.netloc, ALLOWED_HOSTS, msg=url)
                    seen += 1
        if any(m.get('probabilities') is not None for m in open_rows()):
            self.assertGreater(seen, 0)

    def test_market_rows_link_their_own_listing(self):
        for row in open_rows():
            if row.get('method') in ('exchange', 'exchange_wide', 'bookmaker_fallback'):
                self.assertTrue(row.get('evidence'), msg=row['id'])
                self.assertTrue(any(e.get('url') for e in row['evidence']), msg=row['id'])


class ExecutiveSummaryDiscoverability(unittest.TestCase):
    def test_summary_links_the_updated_picks_and_the_unresolved_section(self):
        self.assertIn('href="picks.html"', INDEX)
        self.assertIn('href="unresolved.html"', INDEX)
        self.assertIn('href="#unresolved-summary"', INDEX)
        self.assertIn('id="unresolved-summary"', INDEX)
        self.assertIn('id="picks-at-a-glance"', INDEX)
        self.assertIn('Limitations for generating these picks', INDEX)
        # Every current gap, not only the two named at the old capture, is visible.
        for row in open_rows():
            if row.get('probabilities') is None:
                for name in row['teams']:
                    self.assertIn(html.escape(name), INDEX)

    def test_summary_counts_match_the_snapshot(self):
        rows = open_rows()
        priced = [m for m in rows if m.get('probabilities')]
        self.assertIn(f'data-count="open">{len(rows)}<', INDEX)
        self.assertIn(f'data-count="priced">{len(priced)}<', INDEX)
        picked = sum(bool(m.get('pick')) for m in rows)
        researched = sum(m.get('pick') is not None and m.get('probabilities') is None for m in rows)
        self.assertIn(f'data-count="picked">{picked}<', INDEX)
        self.assertIn(f'data-count="researched">{researched}<', INDEX)
        self.assertIn(f'data-count="unresolved">{len(rows) - picked}<', INDEX)

    def test_pick_board_renders_both_teams_probabilities_and_the_pick(self):
        for row in open_rows():
            if not row.get('probabilities'):
                continue
            self.assertIn(row['teams'][0].replace('&', '&amp;'), PICKS, msg=row['id'])
            self.assertIn(row['teams'][1].replace('&', '&amp;'), PICKS, msg=row['id'])
            self.assertIn(f'{row["probabilities"][0] * 100:.1f}%', PICKS, msg=row['id'])


if __name__ == '__main__':
    unittest.main()
