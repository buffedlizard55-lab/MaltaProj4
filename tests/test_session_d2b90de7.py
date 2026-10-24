"""Session d2b90de7: offline invariants over this session's retained evidence.

Context (all recorded in COORDINATION.md and research/session-d2b90de7/REPORT.md):
this session measured the 2026-10-23/24 publication freeze — five scheduled runs
(39956197341, 39998307424, 40025828846, 40042111432, 40062143026) died at the
unit step while the live site served an expired board for ~18h — reproduced the
deadlock locally (tests/test_session_0cc1138a.py::LiveHotspawnCoverage demanding
feed-rotated fixtures 1081148/1079655), repaired it on this branch, and ran a
full non-publishing capture (run 40067605793, snapshot 2026-10-24T05:57:43Z:
88 feed rows, 25 open, 25 picks, 25 probabilities, 0 unresolved) with
independent live spot-checks (own lobby read 1:1, Valve file byte-identical to
the pinned commit, Polymarket 6075573 re-read, both BO3.gg lines de-vigged to
the digit, HLTV 24 Oct mirror points/rosters confirmed).

While that was in flight, sessions cb16f548, d2a55add, 174afa4f and a30d31a0
merged PRs #245/#246/#251/#258/#260: an archive-pinned parity repair, the
verifier/strip pins, a newer 06:19Z board (92 rows, 31 open, 31 picks, 31
probabilities), the verifier's evidence-alias mapping (``alias_groups``) and a
hardened root publisher. This session independently found and repaired the same
post-merge defects (verifier alias refusal on row 1083121, stale root CSS) and
its competing edits to the shared files were dropped at integration in favour of
the merged repairs rather than layered over them — nothing of any other session
was discarded, logged in COORDINATION.md. What remains here pins only this
session's own retained artifacts, so the evidence behind the outage record, the
coverage measurement and the flagged notes cannot silently rot:

1. The harvest receipts exist, are internally consistent and say what the
   COORDINATION/README prose says (88/25/25/25, quarantine 0, audits 0
   failures, probe 0 rows, non-publishing).
2. The lobby-read table lists exactly the snapshot's 25 open fixture IDs —
   the 1:1 independent-parity claim, re-checkable offline.
3. The published numbers on the retained snapshot re-derive from their own
   stored evidence with arithmetic written here, sharing nothing with the
   pipeline: exchange mid, book de-vig, Valve's Glicko expectation and
   published calibration.
4. Both dated review notes are present with https sources and rendered on the
   committed Flagged-for-Review page.
"""
import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Session a22008ff (2026-10-24): when Hotspawn rotates this fixture out of the
# lobby the row correctly disappears from the live board, and this test used to
# skip -- leaving the alias contract unexercised (seven silent skips on the
# 17:03Z board). The retained capture below is this repository's own dated
# evidence of the board while the row was open, so the property is checked
# against it instead. A row missing from both places is a failure, not a skip.
ALIAS_ARCHIVE = ROOT / 'research' / 'harvest-ce45f672' / 'snapshot.json'


def retained_alias_row(row_id, rows):
    for match in rows:
        if str(match.get('id')) == str(row_id):
            return match, 'data/latest.json'
    if not ALIAS_ARCHIVE.exists():
        raise AssertionError('the retained alias capture %s is missing' % ALIAS_ARCHIVE)
    archived = json.loads(ALIAS_ARCHIVE.read_text()).get('matches') or []
    for match in archived:
        if str(match.get('id')) == str(row_id):
            return match, str(ALIAS_ARCHIVE.relative_to(ROOT))
    raise AssertionError('fixture %s is in neither the board nor the retained capture' % row_id)
HARVEST = ROOT / 'research' / 'harvest-d2b90de7'
SESSION = ROOT / 'research' / 'session-d2b90de7'
SNAP = json.loads((HARVEST / 'refresh-snapshot.json').read_text())
NOTES = json.loads((ROOT / 'data' / 'review-notes.json').read_text())

TOL = 1e-9
RD = 75.0
SLOPE = 0.7986


def glicko_expect(pa, pb, rd=RD):
    q = math.log(10) / 400
    g = 1 / math.sqrt(1 + 3 * q * q * rd * rd / math.pi ** 2)
    return 1 / (1 + 10 ** (-g * (float(pa) - float(pb)) / 400))


def calibrate(raw, slope=SLOPE):
    return 0.5 + slope * (raw - 0.5)


def resolve_aliases(ev, teams, labels):
    """Map fixture teams onto source outcome indices via the evidence's own identity records.

    A self-contained replica (no imports) of the documented mapping semantics the
    merged verifier carries (research/session-0cc1138a/verify_0cc1138a.py
    ``alias_groups``, PR #251): only names stored in the row's ``identity_sources``
    may rename a label; otherwise the label must match the team exactly or be an
    unambiguous prefix run of at least three characters (the documented tolerance
    for exchanges listing "BakS eSports" for Hotspawn's "BakS"). Any ambiguity
    raises rather than guessing. Returns the outcome index per team, in team order.
    """
    alias = {}
    for rec in ev.get('identity_sources') or []:
        names = set(rec.get('names') or [])
        if rec.get('canonical'):
            names.add(rec['canonical'])
        team = next((t for t in teams if t in names), None)
        if team:
            for n in names:
                alias.setdefault(n, team)
    mapped = [alias.get(l, l) for l in labels]

    def same(a, b):
        # The verifier folds case and accents before comparing ("BRUTE" == "Brute").
        a, b = a.lower(), b.lower()
        if a == b:
            return True
        short = min(a, b, key=len)
        return len(short) >= 3 and (a.startswith(b) or b.startswith(a))

    order = []
    for t in teams:
        hits = [i for i, l in enumerate(mapped) if same(l, t)]
        if len(hits) != 1:
            raise ValueError('cannot map %r to exactly one source outcome %r' % (t, labels))
        order.append(hits[0])
    if len(set(order)) != len(order):
        raise ValueError('two teams mapped to the same source outcome %r' % (labels,))
    return order


class HarvestReceiptsAreConsistent(unittest.TestCase):
    def test_run_receipt_is_non_publishing_and_names_the_run(self):
        run = json.loads((HARVEST / 'run.json').read_text())
        self.assertEqual(run['workflow_run_id'], '40067605793')
        self.assertFalse(run['publishes_pages'])
        self.assertIn('actions/runs/40067605793', run['run_url'])

    def test_snapshot_carries_the_claimed_coverage(self):
        self.assertEqual(SNAP['generated_at'], '2026-10-24T05:57:43.355890Z')
        self.assertEqual(SNAP['coverage'], 'verified')
        self.assertEqual(set(SNAP['coverage_counts'].values()), {88})
        opens = [m for m in SNAP['matches'] if m['state'] == 'open']
        self.assertEqual((len(opens),
                          sum(1 for m in opens if m.get('pick')),
                          sum(1 for m in opens if m.get('probabilities'))), (25, 25, 25))
        feed = {str(e['id']) for e in SNAP['fixture_evidence']}
        self.assertEqual(feed, {m['id'] for m in SNAP['matches']})

    def test_gate_logs_say_zero_failures_and_zero_withheld(self):
        cov = json.loads((HARVEST / 'coverage-report.json').read_text())
        self.assertEqual((cov['open_rows'], cov['open_with_pick'], cov['open_with_probability']), (25, 25, 25))
        self.assertEqual(cov['open_without_pick'], [])
        self.assertEqual(cov['open_without_probability'], [])
        self.assertIn('"withheld_rows": 0', (HARVEST / 'logs' / 'quarantine.txt').read_text())
        self.assertIn('"fixtures_probed": 0', (HARVEST / 'logs' / 'unresolved-probe.txt').read_text())
        for audit in ('row-audit.md', 'published-row-audit.md'):
            self.assertIn('failures: **0**', (HARVEST / audit).read_text())
        ledger = json.loads((HARVEST / 'audit.json').read_text())
        self.assertTrue(ledger['coverage_complete'])
        self.assertFalse(ledger['integrity_failures'])  # recorded as a list; empty == none
        self.assertEqual((HARVEST / 'logs' / 'browser.txt').read_text().count('Passed'), 8)


class LobbyReadMatchesTheSnapshot(unittest.TestCase):
    def test_the_independent_lobby_table_lists_exactly_the_open_ids(self):
        text = (SESSION / 'lobby-read-2026-10-24T0530Z.md').read_text()
        listed = set(re.findall(r'^\| \d+ \| (\d{7}) \|', text, re.M))
        opens = {m['id'] for m in SNAP['matches'] if m['state'] == 'open'}
        self.assertEqual(len(listed), 25)
        self.assertEqual(listed, opens)

    def test_crowd_votes_are_marked_refused_not_used(self):
        text = (SESSION / 'lobby-read-2026-10-24T0530Z.md').read_text()
        self.assertIn('never used as picks or percentages', text)
        # No published probability equals a lobby vote share: the votes are not lines.
        votes = set()
        for pair in re.findall(r'\| (\d+)% / (\d+)% \|', text):
            votes.update(float(v) for v in pair)
        self.assertTrue(votes)
        for m in SNAP['matches']:
            if m['state'] == 'open' and m.get('probabilities'):
                published = {round(p * 100, 1) for p in m['probabilities']}
                self.assertFalse(published & votes, '%s equals a crowd vote' % m['id'])


class PublishedNumbersReDeriveFromStoredEvidence(unittest.TestCase):
    """Arithmetic written in this file only; no pipeline code is imported."""

    def rows(self):
        return [m for m in SNAP['matches'] if m['state'] == 'open']

    def test_every_open_row_reproduces_from_its_first_evidence_record(self):
        for m in self.rows():
            ev = (m.get('evidence') or [None])[0]
            self.assertIsNotNone(ev, m['id'])
            probs = m['probabilities']
            provider = ev.get('provider')
            if provider in ('Valve VRS model', 'HLTV Valve ranking (Valve points)'):
                rd = float(ev.get('rating_deviation', RD))
                slope = float(ev.get('calibration_slope', SLOPE))
                p0 = calibrate(glicko_expect(ev['points'][0], ev['points'][1], rd), slope)
                calc = [p0, 1 - p0]
            elif 'decimal_odds' in ev:
                q = [1 / float(d) for d in ev['decimal_odds']]
                calc = [v / sum(q) for v in q]
            else:
                raw = ev.get('raw') or {}
                prices = raw.get('outcomePrices')
                self.assertTrue(prices, m['id'])
                x = [float(v) for v in (json.loads(prices) if isinstance(prices, str) else prices)]
                calc = [v / sum(x) for v in x]
                labels = json.loads(raw['outcomes']) if isinstance(raw.get('outcomes'), str) else raw.get('outcomes')
                mapped = resolve_aliases(ev, m['teams'], labels)
                calc = [calc[i] for i in mapped]
            self.assertLessEqual(max(abs(probs[i] - calc[i]) for i in (0, 1)), 1e-6,
                                 '%s: published %r != re-derived %r' % (m['id'], probs, calc))
            # The pick is the larger re-derived probability, and sides sum to 1.
            self.assertEqual(m['pick'], m['teams'][probs.index(max(probs))], m['id'])
            self.assertAlmostEqual(sum(probs), 1.0, places=9)
            fair = m.get('fair_odds')
            if fair:
                self.assertLessEqual(max(abs(fair[i] - 1 / probs[i]) for i in (0, 1)), 1e-6, m['id'])

    def test_the_two_spot_checked_book_lines_match_their_live_pages(self):
        rows = {m['id']: m for m in self.rows()}
        nexvoid = rows['1082859']['evidence'][0]['decimal_odds']
        self.assertEqual([float(d) for d in nexvoid], [1.6, 2.17])
        flyquest = rows['1082860']['evidence'][0]['decimal_odds']
        self.assertEqual([float(d) for d in flyquest], [1.001, 12.0])

    def test_the_mirror_rows_match_the_live_hltv_points(self):
        rows = {m['id']: m for m in self.rows()}
        for fid, points in (('1081156', [1030, 819]), ('1081158', [1141, 1074])):
            ev = rows[fid]['evidence'][0]
            self.assertEqual(ev['provider'], 'HLTV Valve ranking (Valve points)')
            self.assertEqual(ev['points'], points)
            self.assertEqual(ev['url'], 'https://www.hltv.org/valve-ranking/teams/2026/october/24')


class StoredIdentityAliasesAreHonoredNotGuessed(unittest.TestCase):
    """The merged 06:19Z board added fixture 1083121 (CCT South America Series #7),
    publishing Hotspawn's 'Projeto do KinGui' against Polymarket outcome 'Tropa do
    KinGui' under the alias record session 9f3e77d2 stored on 2026-10-22 (HLTV match
    2399904 fixture parity + Valve roster continuity). The strict independent
    verifier initially refused the rename, re-freezing every scheduled publication
    on the merged tree — the same deadlock mode as the 18-hour freeze this session
    measured. The repair that shipped is PR #251's evidence-alias mapping; this
    session found the same RED concurrently and keeps these offline checks of both
    halves: the recorded alias reproduces the published price, and an UNrecorded
    rename is still refused."""

    def board_row(self):
        doc = json.loads((ROOT / 'data' / 'latest.json').read_text())
        row, _source = retained_alias_row('1083121', doc['matches'])
        self.assertEqual(row['state'], 'open')
        return row

    def test_published_alias_row_reproduces_from_its_stored_record(self):
        m = self.board_row()
        ev = m['evidence'][0]
        recs = ev.get('identity_sources') or []
        names = {n for r in recs for n in (r.get('names') or [])}
        names |= {r.get('canonical') for r in recs if r.get('canonical')}
        self.assertIn('Projeto do KinGui', names)
        self.assertIn('Tropa do KinGui', names)
        for r in recs:  # every alias record carries its primary sources
            self.assertTrue(str(r.get('source', '')).startswith('https://'))
        raw = ev['raw']
        x = [float(v) for v in (json.loads(raw['outcomePrices'])
                                if isinstance(raw['outcomePrices'], str) else raw['outcomePrices'])]
        labels = json.loads(raw['outcomes']) if isinstance(raw.get('outcomes'), str) else raw.get('outcomes')
        p = [v / sum(x) for v in x]
        order = resolve_aliases(ev, m['teams'], labels)
        calc = [p[i] for i in order]
        self.assertLessEqual(max(abs(m['probabilities'][i] - calc[i]) for i in (0, 1)), 1e-6)
        self.assertEqual(m['pick'], m['teams'][m['probabilities'].index(max(m['probabilities']))])

    def test_unrecorded_rename_is_still_refused(self):
        m = self.board_row()
        ev = m['evidence'][0]
        raw = ev['raw']
        labels = json.loads(raw['outcomes']) if isinstance(raw.get('outcomes'), str) else raw.get('outcomes')
        stripped = {k: v for k, v in ev.items() if k != 'identity_sources'}
        with self.assertRaises(ValueError):
            resolve_aliases(stripped, m['teams'], labels)
        # ... and a guessed near-match is refused too: renames must be recorded, not fuzzy.
        guessed = {'identity_sources': [{'canonical': 'Tropa do KinGui',
                                         'names': ['Tropa do KinGui', 'Projeto do KinGui X']}]}
        with self.assertRaises(ValueError):
            resolve_aliases(guessed, m['teams'], labels)


class DatedNotesArePublished(unittest.TestCase):
    IDS = ('session-d2b90de7-publish-deadlock-2026-10-24',
           'session-d2b90de7-coverage-measurement-2026-10-24')

    def notes_by_id(self):
        return {n['id']: n for n in NOTES}

    def test_both_notes_exist_with_https_sources(self):
        by_id = self.notes_by_id()
        for nid in self.IDS:
            self.assertIn(nid, by_id)
            note = by_id[nid]
            self.assertGreaterEqual(len(note['sources']), 5)
            for src in note['sources']:
                self.assertTrue(src['url'].startswith('https://'), src)
                self.assertTrue(src.get('label'))
            self.assertGreater(len(note['finding']), 400)

    def test_both_notes_are_rendered_on_the_committed_review_page(self):
        html = (ROOT / 'review.html').read_text()
        for nid in self.IDS:
            self.assertIn(nid, html)

    def test_the_deadlock_note_names_all_five_failed_runs(self):
        finding = self.notes_by_id()[self.IDS[0]]['finding']
        for run in ('39956197341', '39998307424', '40025828846', '40042111432', '40062143026'):
            self.assertIn(run, finding)
        # Honest provenance: the repair that shipped on main is cb16f548's.
        self.assertIn('245', finding)


if __name__ == '__main__':
    unittest.main()
