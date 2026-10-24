"""Regression for the 2026-10-24 fresh capture's verified even-line row.

Run 40111530750 found a strict Polymarket line whose re-derived probabilities
were exactly 0.5 / 0.5. The collector correctly refused to invent a favourite,
but the old independent verifier rejected it and summary counters omitted it
from the unresolved-picks path. These tests use a synthetic mutation of the
committed fixture, not a hand-authored current pick or probability.
"""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from bs4 import BeautifulSoup

from scripts import build, summary


ROOT = Path(__file__).resolve().parents[1]


class VerifiedEvenLine(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data/latest.json').read_text())
        self.row = next(m for m in self.data['matches']
                        if m.get('state') == 'open' and m.get('method') == 'exchange'
                        and m.get('probabilities'))
        self.row['probabilities'] = [0.5, 0.5]
        self.row['fair_odds'] = [2.0, 2.0]
        self.row['pick'] = None
        self.row['reason'] = 'Equal verified prices; no directional edge.'
        raw = self.row['evidence'][0].setdefault('raw', {})
        raw['outcomePrices'] = json.dumps(['0.5', '0.5'])
        self.match_id = self.row['id']

    def test_counts_and_all_summary_surfaces_include_the_no_pick_row(self):
        counts = summary.counts(self.data['matches'])
        self.assertIn(self.match_id, {m['id'] for m in counts['directionless_rows']})
        expected_picks = sum(m.get('state') == 'open' and bool(m.get('pick'))
                             for m in self.data['matches'])
        expected_no_pick = sum(m.get('state') == 'open' and not m.get('pick')
                               for m in self.data['matches'])
        self.assertEqual(counts['with_pick'], expected_picks)
        self.assertEqual(counts['no_pick'], expected_no_pick)

        index = BeautifulSoup(build.overview(copy.deepcopy(self.data)), 'html.parser')
        section = index.select_one('#unresolved-picks')
        link = section.select_one('a.unresolved-row[href="evidence.html#match-%s"]' % self.match_id)
        self.assertIsNotNone(link, 'the priced no-pick row disappeared from unresolved picks')
        item = link.find_parent('li')
        text = item.get_text(' ', strip=True)
        self.assertIn('No directional edge', text)
        self.assertIn('50.0% / 50.0%', text)
        self.assertIn('Equal verified prices', text)
        self.assertEqual(link['data-glance-priced'], '1')
        hrefs = {a.get('href') for a in item.select('a[href]')}
        self.assertIn(self.row['source_url'], hrefs)
        self.assertIn('evidence.html#match-' + self.match_id, hrefs)

        fresh = index.select_one('#freshness-strip')
        self.assertEqual(int(fresh.select_one('[data-count="picked"]').get_text()), expected_picks)
        self.assertEqual(int(fresh.select_one('[data-count="unresolved"]').get_text()), expected_no_pick)
        limitations = index.select_one('#unresolved-limits')
        self.assertEqual(int(limitations.select_one('[data-count="unresolved"]').get_text()), expected_no_pick)
        self.assertIn('no directional', limitations.get_text(' ', strip=True))

    def test_unresolved_page_keeps_the_even_line_and_official_source(self):
        now = datetime.fromisoformat(self.data['generated_at'].replace('Z', '+00:00'))
        now = now.astimezone(timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            build.build(copy.deepcopy(self.data), tmp, now=now)
            page = BeautifulSoup((Path(tmp) / 'unresolved.html').read_text(), 'html.parser')
        row = page.select_one('tr[data-match="%s"]' % self.match_id)
        self.assertIsNotNone(row, 'unresolved.html omitted a strict-market row with no directional pick')
        self.assertIn('No directional edge', row.get_text(' ', strip=True))
        self.assertIn('50.0%', row.get_text(' ', strip=True))
        self.assertIsNotNone(row.select_one('a[href="%s"]' % self.row['source_url']))


if __name__ == '__main__':
    unittest.main()
