from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import books, core
from verification_071642e7_helper import load_auditor


ROOT = Path(__file__).resolve().parents[1]


class Session071642e7VerificationTests(unittest.TestCase):
    def test_books_parse_listing_integer_decimal_and_placeholder_guards(self):
        live_html = '''<html><body>
        <script type="application/ld+json">
        {"@type":"SportsEvent","name":"FlyQuest VS Staqued","startDate":"2026-10-27T03:00:00.000Z"}
        </script>
        <div>FlyQuest 1.001 Make a bet 12 Staqued</div>
        </body></html>'''
        readings = books.parse_listing(live_html)
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0]['odds'], [1.001, 12.0])
        self.assertTrue(readings[0]['bound_to_labels'])

        placeholder_html = '''<html><body>
        <script type="application/ld+json">
        {"@type":"SportsEvent","name":"FlyQuest VS Staqued","startDate":"2026-10-27T03:00:00.000Z"}
        </script>
        <div>FlyQuest 1.8 Make a bet 1.8 Staqued</div>
        </body></html>'''
        self.assertEqual(books.parse_listing(placeholder_html), [])

        numeric_team_html = '''<html><body>
        <script type="application/ld+json">
        {"@type":"SportsEvent","name":"FORZE Reload VS LFO 10","startDate":"2026-10-23T08:00:00.000Z"}
        </script>
        <div>FORZE Reload 1.38 Make a bet 2.95 LFO 10</div>
        </body></html>'''
        num_readings = books.parse_listing(numeric_team_html)
        self.assertEqual(len(num_readings), 1)
        self.assertEqual(num_readings[0]['odds'], [1.38, 2.95])
        self.assertTrue(num_readings[0]['bound_to_labels'])

    def test_flyquest_staqued_receipt_and_retained_harvest_provenance(self):
        receipts_doc = json.loads((ROOT / 'data/book-receipts.json').read_text(encoding='utf-8'))
        matching = [r for r in receipts_doc['receipts'] if r.get('id') == 'egw-4kaAQWgKEx-flyquest-staqued']
        self.assertEqual(len(matching), 1)
        rec = matching[0]
        self.assertEqual(rec['fixture_id'], '1082860')
        self.assertEqual(rec['odds'], [1.001, 12.0])
        self.assertEqual(rec['start'], '2026-10-27T03:00:00Z')

        # Historical placeholder rejection on 2026-10-22T01:14:00Z remains documented, never erased
        rejected_1082860 = [
            r for r in receipts_doc.get('rejected_listings', [])
            if str(r.get('fixture_id')) == '1082860'
        ]
        self.assertGreaterEqual(len(rejected_1082860), 1)

        # Replay exact de-vig math against retained 071642e7 harvest fixture
        harvest = json.loads((ROOT / 'research/session-071642e7/refresh-snapshot.json').read_text(encoding='utf-8'))
        row = copy.deepcopy(next(m for m in harvest['matches'] if m['id'] == '1082860'))
        row['probabilities'] = None
        row['fair_odds'] = None
        row['pick'] = None
        row['method'] = None
        row['reason'] = None
        row['flags'] = []
        core.book_research_pick(row, receipts=[rec], now=core.dt(harvest['generated_at']))
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertEqual(row['pick'], 'FlyQuest')
        self.assertAlmostEqual(row['probabilities'][0] + row['probabilities'][1], 1.0, places=9)
        self.assertAlmostEqual(round(row['probabilities'][0] * 100, 1), 92.3, places=1)
        self.assertAlmostEqual(round(row['probabilities'][1] * 100, 1), 7.7, places=1)

    def test_canonical_json_formatting_and_review_notes_present(self):
        for rel in ('data/identities.json', 'data/book-receipts.json', 'data/review-notes.json'):
            raw = (ROOT / rel).read_text(encoding='utf-8')
            parsed = json.loads(raw)
            self.assertEqual(
                raw,
                json.dumps(parsed, indent=1, ensure_ascii=False) + '\n',
                f'{rel} must keep canonical indent=1 formatting',
            )
        notes = json.loads((ROOT / 'data/review-notes.json').read_text(encoding='utf-8'))
        note_ids = {n['id'] for n in notes}
        self.assertIn('071642e7-flyquest-staqued-polymarket-wide-clob-vs-6book-line-2026-10-23', note_ids)
        self.assertIn('071642e7-rooster-abyssal-polymarket-wide-clob-vs-vrs-2026-10-23', note_ids)
        self.assertIn('071642e7-forze-reload-lfo10-hltv-dated-valve-mirror-2026-10-23', note_ids)
        self.assertIn('071642e7-refresh-gate-identities-format-and-320px-fold-fixes-2026-10-23', note_ids)

    def test_workflow_post_refresh_gate_and_mobile_fold_css(self):
        wf = (ROOT / '.github/workflows/pages.yml').read_text(encoding='utf-8')
        self.assertIn("cron: '4,19,34,49 * * * *'", wf)
        publish_idx = wf.index('python -m scripts.publish_root_fallback')
        # Session 572c65b7: the unit gate now runs through scripts.staged_gate.
        post_test_idx = wf.index('python -m scripts.staged_gate --check units', publish_idx)
        commit_idx = wf.index('git config user.name "cs2-scout-publisher"', publish_idx)
        self.assertLess(publish_idx, post_test_idx)
        self.assertLess(post_test_idx, commit_idx)

        css = (ROOT / 'assets/style.css').read_text(encoding='utf-8')
        self.assertIn('.fresh-strip .fresh-state{font-size:10.5px;order:4}', css)

    def test_independent_line_by_line_auditor_passes_and_catches_corruptions(self):
        auditor = load_auditor()
        receipt = auditor.audit_repository(ROOT)
        self.assertEqual(receipt['errors'], [])

        # Negative test: probability drift must fail immediately
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            manifest = json.loads((ROOT / 'build-info.json').read_text(encoding='utf-8'))
            (tdir / 'build-info.json').write_text((ROOT / 'build-info.json').read_text(encoding='utf-8'), encoding='utf-8')
            shutil.copytree(ROOT / 'data', tdir / 'data')
            for rel in manifest['files'].keys():
                src_p = ROOT / rel
                if src_p.exists():
                    (tdir / rel).parent.mkdir(parents=True, exist_ok=True)
                    (tdir / rel).write_bytes(src_p.read_bytes())
            corrupted = json.loads((tdir / 'data/latest.json').read_text(encoding='utf-8'))
            open_row = next(m for m in corrupted['matches'] if m['state'] == 'open')
            open_row['probabilities'] = [0.6, 0.3]  # sums to 0.9 != 1.0
            (tdir / 'data/latest.json').write_text(json.dumps(corrupted), encoding='utf-8')
            bad_receipt = auditor.audit_repository(tdir)
            self.assertTrue(any('Probability' in err or 'probabilities' in err for err in bad_receipt['errors']))


if __name__ == '__main__':
    unittest.main()
