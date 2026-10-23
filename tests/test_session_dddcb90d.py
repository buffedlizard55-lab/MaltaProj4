"""Session dddcb90d deliverable pins (2026-10-23).

Everything here runs offline against committed bytes:

* the documented research tiers stay accepted by the repaired scheduled-publish
  assertions (the red-run fix that unblocks ``pages.yml`` on main);
* the phone-width stale-mode layout fix that makes
  ``tests/browser_eaff7cce.cjs`` pass stays in BOTH byte-identical style.css
  copies (the build reads ``site/assets/style.css``; the staged root reads
  ``assets/style.css``);
* the two dated review notes carry their exact ids, both sides of the
  1081149 start conflict, and source links that are absolute URLs;
* the session's runner harvest stays non-publishing and bound to this branch,
  and its probe only requests URLs the committed receipts/rows already own -
  no guessed slugs;
* ``pages.yml`` keeps registering this branch so pushes run the full pipeline.
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path):
    return (ROOT / path).read_text(encoding='utf-8')


class ResearchTierRepair(unittest.TestCase):
    """The red scheduled publish (runs 39871808909 / 39886171791) fix stays."""

    def test_repaired_assertion_accepts_documented_tier_set(self):
        text = _read('tests/test_session_75ebd2d6.py')
        block = re.search(r'RESEARCH_TIERS\s*=\s*\{([^}]+)\}', text)
        self.assertIsNotNone(block, 'the repaired file must define RESEARCH_TIERS')
        for tier in ('research_rank', 'research_rank_single', 'research_vrs_single'):
            self.assertRegex(block.group(1), rf'["\']{tier}["\']',
                             f'{tier} must stay in the accepted set')
        self.assertIn('assertIn(m["method"], RESEARCH_TIERS', text.replace("'", '"'))

    def test_sibling_selector_keeps_the_tier_tuple(self):
        text = _read('tests/test_session_13e99ca6.py')
        self.assertIn('research_vrs_single', text)
        self.assertIn('assertIn', text)

    def test_every_blank_percentage_open_row_keeps_pick_method_and_source(self):
        """Snapshot-independent invariant: blanks are never unpickable or inferred.

        The concrete set of blank rows changes as sources resolve (1082860 may
        price itself through the Polymarket exchange tier); what must hold on
        every snapshot is pick + documented research method + official source
        link, and the two rows this session researched keep their tier if still
        blank.
        """
        data = json.loads(_read('data/latest.json'))
        blanks = [m for m in data['matches']
                  if m.get('state') == 'open' and m.get('probabilities') is None]
        for m in blanks:
            self.assertTrue(m.get('pick'), m['id'])
            self.assertIn(m.get('method'),
                          ('research_vrs_single', 'research_rank_single', 'research_rank'))
            self.assertTrue(str(m.get('source_url', '')).startswith('https://'), m['id'])
        by_id = {str(m['id']): m for m in blanks}
        for row_id, tier in (('1081149', 'research_vrs_single'),
                             ('1082860', 'research_rank_single')):
            if row_id in by_id:
                self.assertEqual(by_id[row_id]['method'], tier)


class StalePhoneLayoutFix(unittest.TestCase):
    """The exact fix for browser_eaff7cce's stale-mode first-screen gates."""

    def test_style_copies_stay_byte_identical(self):
        root_css = (ROOT / 'assets/style.css').read_bytes()
        site_css = (ROOT / 'site/assets/style.css').read_bytes()
        self.assertEqual(root_css, site_css,
                         'scripts.build sources site/assets/style.css; the two copies must match')

    def test_stale_strip_links_order_and_state_removal(self):
        text = _read('assets/style.css')
        self.assertIn('.fresh-strip.stale .fresh-links{order:-1}', text)
        self.assertIn('.fresh-strip.stale .fresh-state{display:none}', text)
        # Both live inside the phone media block so desktop layout is untouched.
        phone = text.split('@media(max-width:650px)', 1)[1]
        self.assertIn('.fresh-strip.stale .fresh-links{order:-1}', phone)
        self.assertIn('#runtime-stale{margin:0 0 12px;padding:11px 13px}', phone)

    def test_manifest_sha_matches_shipped_css(self):
        import hashlib
        man = json.loads(_read('build-info.json'))
        shipped = hashlib.sha256((ROOT / 'assets/style.css').read_bytes()).hexdigest()
        self.assertEqual(man['files']['assets/style.css'], shipped)


class ReviewNotes(unittest.TestCase):
    """The two dated, source-linked notes for the Flagged for Review page."""

    @classmethod
    def setUpClass(cls):
        cls.notes = {n['id']: n for n in json.loads(_read('data/review-notes.json'))}
        cls.n1 = cls.notes['session-dddcb90d-1081149-start-conflict-2026-10-23']
        cls.n2 = cls.notes['session-dddcb90d-1082860-new-exchange-listing-2026-10-23']

    def test_start_conflict_note_records_both_sides(self):
        finding = self.n1['finding']
        self.assertIn('14:00:00Z', finding)
        self.assertIn('08:00Z', finding)
        self.assertIn('13:54:00Z', finding)
        self.assertIn('Sökerorg', finding)
        self.assertIn('No start, lock, pick or', finding)  # no value restated

    def test_exchange_listing_note_pins_market_and_gates(self):
        finding = self.n2['finding']
        self.assertIn('6066520', finding)
        self.assertIn('88-point spread', finding)
        self.assertIn('60-point wide-tier ceiling', finding)
        self.assertIn('research_rank_single', finding)

    def test_sources_are_absolute_unique_urls(self):
        for note in (self.n1, self.n2):
            self.assertGreaterEqual(len(note['sources']), 4)
            urls = [s['url'] for s in note['sources']]
            self.assertEqual(len(urls), len(set(urls)))
            for source in note['sources']:
                self.assertRegex(source['url'], r'^https?://[^\s]+\.[^\s]+$')
                self.assertTrue(source['label'].strip())

    def test_note_ids_are_unique_in_the_file(self):
        ids = [n['id'] for n in json.loads(_read('data/review-notes.json'))]
        self.assertEqual(len(ids), len(set(ids)))


class HarvestScope(unittest.TestCase):
    """The session harvest stays non-publishing, branch-bound, receipt-driven."""

    @classmethod
    def setUpClass(cls):
        cls.wf = _read('.github/workflows/harvest-dddcb90d.yml')

    def test_workflow_bound_to_session_branch(self):
        self.assertIn('arena/dddcb90d-maltaproj4', self.wf)
        self.assertIn("contains(github.event.head_commit.message, '[capture]')", self.wf)

    def test_workflow_never_publishes_pages(self):
        self.assertIn('non-publishing', self.wf)
        self.assertNotIn('peaceiris/actions-gh-pages', self.wf)
        self.assertNotIn('deploy', self.wf.lower().replace('non-publishing', ''))
        self.assertIn('git add -- research/harvest-dddcb90d', self.wf)
        self.assertIn('[skip ci]', self.wf)

    def test_probe_only_requests_urls_the_repo_already_owns(self):
        probe = _read('scripts/probe_dddcb90d.py')
        receipts = _read('data/book-receipts.json')
        for url in re.findall(r"'(https://[^']+'[^']*'?)", probe):
            url = url.rstrip("'")
            if not re.fullmatch(r'https://[^/\s]+\.[^/\s]+.*', url):
                continue  # e.g. the startswith('https://gamma-api') scope check
            self.assertRegex(url, r'^https?://[^\s]+\.[^\s]+$', url)
            if 'egamersworld.com/counterstrike/match/' in url:
                self.assertIn(url, receipts,
                              'EGW listing URLs must come from committed receipts, never be guessed')
        # The ladder's Polymarket market id is the exact-pair market recorded in
        # the review note; HLTV ids come from the rows' own hltv_context evidence.
        self.assertIn('6066520', probe)
        self.assertIn('2399499', probe)
        self.assertIn('2399890', probe)

    def test_probe_writes_the_documented_artifacts(self):
        import tempfile
        from scripts.probe_dddcb90d import audit, blank_rows
        snapshot = json.loads(_read('data/latest.json'))
        with tempfile.TemporaryDirectory() as tmp:
            report = audit(snapshot, snapshot, pathlib.Path(tmp))
            for key in ('coverage_counts_fresh', 'added_vs_committed', 'removed_vs_committed',
                        'start_or_lock_diffs_vs_committed', 'blank_percentage_open_rows'):
                self.assertIn(key, report)
            self.assertEqual((pathlib.Path(tmp) / 'coverage-audit.md').exists(), True)
        rows = blank_rows(snapshot)
        expected = [m for m in snapshot['matches']
                    if m.get('state') == 'open' and m.get('probabilities') is None]
        self.assertEqual(len(rows), len(expected))
        for row in rows:
            for key in ('id', 'teams', 'start', 'lock', 'pick', 'method', 'source_url'):
                self.assertIn(key, row)


class PagesRegistration(unittest.TestCase):
    def test_branch_registered_for_full_pipeline_push_runs(self):
        text = _read('.github/workflows/pages.yml')
        self.assertIn('arena/dddcb90d-maltaproj4', text)


if __name__ == '__main__':
    unittest.main()
