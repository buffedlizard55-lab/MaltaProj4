"""Historical research must not destroy later sourced Day-5 cards."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import day5_f4e34907 as legacy

ROOT = Path(__file__).resolve().parents[1]


class HistoricalReapplyTests(unittest.TestCase):
    def test_current_published_research_is_protected_byte_for_byte(self):
        original = (ROOT / 'data/analysis.json').read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data').mkdir()
            path = root / 'data/analysis.json'
            path.write_bytes(original)
            with patch.object(legacy, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'Newer research'):
                    legacy.apply()
            self.assertEqual(path.read_bytes(), original)

    def test_market_evidence_is_protected_even_with_older_top_level_date(self):
        for market in ({'observed_at': '2026-10-17T20:20:00Z'}, {}, None):
            with self.subTest(market=market):
                notes = {'reviewed_at_utc': legacy.REVIEWED_AT,
                         'day_five_guidance': {'not_listed': [{'market': market}]}}
                with self.assertRaisesRegex(ValueError, 'Market evidence'):
                    legacy.ensure_safe_reapplication(notes)

    def test_missing_malformed_or_naive_chronology_fails_closed(self):
        for value in (None, '', 'yesterday', '2026-10-17T20:00:00', 42):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'chronology'):
                    legacy.ensure_safe_reapplication({'reviewed_at_utc': value})

    def test_timezone_equivalent_cutoff_is_allowed(self):
        legacy.ensure_safe_reapplication({'reviewed_at_utc': '2026-10-17T22:24:00+02:00'})

    def test_future_review_is_never_downgraded(self):
        with self.assertRaisesRegex(ValueError, 'Newer research'):
            legacy.ensure_safe_reapplication({'reviewed_at_utc': '2026-10-18T00:00:00Z'})

    def test_retained_market_quotes_have_not_been_dropped(self):
        notes = json.loads((ROOT / 'data/analysis.json').read_text())
        cards = notes['day_five_guidance']['not_listed']
        self.assertEqual(len([c for c in cards if c.get('market')]), 2)
