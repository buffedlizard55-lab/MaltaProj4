"""Session 35c6e1e9: the publication-continuity audit, and the rule that keeps
it advisory.

What had to be provable, and how it is proven here
--------------------------------------------------
1. The auditor's verdict comes from the sources it read, never from a value the
   pipeline asserted about itself. Each rule is exercised on a good input and on
   a deliberately corrupted one, because a check that cannot fail is decoration.
2. An *undecidable* state is reported as undecidable. Offline, the run history
   is not read and the published receipt is not read; claiming "frozen" there
   would make this auditor red for a reason nobody can act on, and claiming
   "current" would be the silence that let the 2026-10-24 outage run 17.7 h.
3. This auditor is never wired into the merge gate. It reads wall-clock
   staleness, so a committed baseline older than its own evidence window is
   normal between refreshes. On 2026-10-23/24 two snapshot-coupled assertions
   in ``tests/test_session_0cc1138a.py`` did exactly that and held every
   scheduled publication for 17.7 h; the pin below is the guard against this
   module becoming the next one.
4. The measured outage is recorded as a dated receipt, so the report cites
   official run and step identifiers rather than prose.
"""
import contextlib
import datetime
import io
import json
import pathlib
import unittest

from scripts import verify_35c6e1e9 as A

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOW = datetime.datetime(2026, 10, 24, 5, 33, tzinfo=datetime.timezone.utc)
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


def stamp(minutes_ago):
    return (NOW - datetime.timedelta(minutes=minutes_ago)).strftime('%Y-%m-%dT%H:%M:%SZ')


def live_receipt(minutes_ago=30, revision='deadbeef'):
    return {'revision': revision, 'built_at': stamp(minutes_ago),
            'snapshot_generated_at': stamp(minutes_ago), 'rows': 90}


def run(conclusion='success', created=60, sha='5d56f35e' + '0' * 32, event='schedule',
        status='completed', run_id=1):
    return {'id': run_id, 'event': event, 'status': status, 'conclusion': conclusion,
            'created_at': stamp(created), 'updated_at': stamp(created + 2),
            'head_sha': sha, 'html_url': 'https://github.com/o/r/actions/runs/%d' % run_id}


def codes(findings):
    return [f['code'] for f in findings]


class SnapshotWindow(unittest.TestCase):
    def test_a_live_snapshot_inside_its_window_passes(self):
        found = A.check_snapshot_age(live_receipt(30), 8, NOW)
        self.assertEqual(codes(found), ['snapshot_inside_evidence_window'])
        self.assertEqual(found[0]['severity'], 'ok')

    def test_a_live_snapshot_outside_its_window_is_proof_of_a_frozen_board(self):
        # The measured 2026-10-24 state: 1066 min against a stated 8 h TTL.
        found = A.check_snapshot_age(live_receipt(1066), 8, NOW)
        self.assertEqual(codes(found), ['snapshot_outside_evidence_window'])
        self.assertEqual(found[0]['severity'], 'frozen')
        self.assertIn('every open pick is withheld', found[0]['detail'])
        self.assertAlmostEqual(found[0]['age_minutes'], 1066, delta=1)
        self.assertEqual(found[0]['window_minutes'], 480)

    def test_a_stale_committed_baseline_is_a_flag_not_a_proof(self):
        # Offline the published receipt was never read, so an old committed
        # baseline cannot prove the public site is frozen. Reporting it as frozen
        # is how an advisory auditor becomes a deadlocking merge gate.
        found = A.check_snapshot_age(live_receipt(1066), 8, NOW, receipt_is_live=False)
        self.assertEqual(codes(found), ['committed_baseline_outside_evidence_window'])
        self.assertEqual(found[0]['severity'], 'flag')
        self.assertIn('not proof the live site is frozen', found[0]['detail'])

    def test_an_unreadable_timestamp_is_never_a_guess(self):
        self.assertEqual(A.check_snapshot_age({}, 8, NOW)[0]['code'], 'receipt_unreadable')
        self.assertEqual(A.check_snapshot_age({'snapshot_generated_at': 'not a time'}, 8, NOW)[0]['code'],
                         'receipt_unreadable')
        self.assertEqual(A.check_snapshot_age(None, 8, NOW)[0]['severity'], 'frozen')
        # Offline the same unreadable state is undecidable, not proof.
        self.assertEqual(A.check_snapshot_age(None, 8, NOW, receipt_is_live=False)[0]['severity'], 'flag')

    def test_the_window_comes_from_the_snapshots_own_ttl(self):
        self.assertEqual(SNAPSHOT['stale_after_hours'], 8)
        found = A.check_snapshot_age(live_receipt(481), SNAPSHOT['stale_after_hours'], NOW)
        self.assertEqual(found[0]['code'], 'snapshot_outside_evidence_window')
        self.assertEqual(A.check_snapshot_age(live_receipt(479), SNAPSHOT['stale_after_hours'], NOW)[0]['code'],
                         'snapshot_inside_evidence_window')


class PublishChain(unittest.TestCase):
    def test_a_green_chain_passes(self):
        found = A.check_publish_chain([run('success', 20)], NOW)
        self.assertEqual(codes(found), ['publish_chain_green'])

    def test_an_in_flight_run_is_not_a_red_chain(self):
        found = A.check_publish_chain([run(created=20, status='in_progress', conclusion=None),
                                       run('success', 200)], NOW)
        self.assertIn('publish_chain_in_flight', codes(found))
        self.assertNotIn('publish_chain_red', codes(found))

    def test_consecutive_failures_on_one_commit_are_frozen_and_name_the_commit(self):
        runs = [run('failure', 60 + 150 * i, run_id=40062143026 + i) for i in range(5)]
        found = A.check_publish_chain(runs, NOW)
        red = next(f for f in found if f['code'] == 'publish_chain_red')
        self.assertEqual(red['severity'], 'frozen')
        self.assertEqual(red['streak'], 5)
        self.assertTrue(red['head_sha'].startswith('5d56f35e'))
        self.assertIn('one unmoved commit 5d56f35e', red['detail'])
        self.assertEqual(len(red['failed_run_urls']), 5)
        self.assertEqual(red['failed_run_ids'][0], 40062143026)

    def test_a_streak_across_different_commits_is_a_flag_not_a_deadlock(self):
        runs = [run('failure', 60, sha='a' * 40), run('failure', 200, sha='b' * 40),
                run('success', 400)]
        red = next(f for f in A.check_publish_chain(runs, NOW) if f['code'] == 'publish_chain_red')
        self.assertEqual(red['severity'], 'flag', 'a moving main is retrying, not deadlocked')

    def test_an_unread_history_is_undecidable_offline(self):
        self.assertEqual(A.check_publish_chain([], NOW)[0]['code'], 'no_run_history')
        self.assertEqual(A.check_publish_chain([], NOW)[0]['severity'], 'frozen')
        found = A.check_publish_chain([], NOW, history_read=False)
        self.assertEqual(codes(found), ['run_history_not_read'])
        self.assertEqual(found[0]['severity'], 'flag')
        self.assertIn('undecidable', found[0]['detail'])

    def test_a_run_older_than_a_day_is_flagged_as_starved_delivery(self):
        found = A.check_publish_chain([run('success', 60 * 30)], NOW)
        self.assertIn('no_recent_run', codes(found))
        self.assertIn('scheduled delivery, not the cron expression', next(
            f for f in found if f['code'] == 'no_recent_run')['detail'])


class RowSources(unittest.TestCase):
    def open_only(self, **overrides):
        doc = {'matches': [dict(m, **overrides) for m in SNAPSHOT['matches'] if m['state'] == 'open']}
        return doc

    def test_the_committed_board_passes(self):
        # Counts are read from the snapshot under test, never pinned here. This
        # suite exists because two assertions in tests/test_session_0cc1138a.py
        # pinned a point-in-time board and held every scheduled publication for
        # 17.7 h when Hotspawn rotated that board; hardcoding 27 would make this
        # the next one. The invariant is the interesting part: every open row is
        # sourced, and every open row answers.
        open_rows = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        found = A.check_row_sources(SNAPSHOT)
        self.assertEqual(codes(found), ['rows_sourced'], found)
        self.assertEqual(found[0]['open_rows'], len(open_rows))
        self.assertEqual(found[0]['with_pick'], sum(1 for m in open_rows if m.get('pick')))
        self.assertEqual(found[0]['with_probability'],
                         sum(1 for m in open_rows if m.get('probabilities')))
        self.assertGreater(len(open_rows), 0, 'a snapshot with no open rows cannot prove sourcing')

    def test_a_row_losing_its_official_fixture_link_is_frozen(self):
        doc = self.open_only()
        doc['matches'][0]['source_url'] = 'http://insecure.example/match'
        found = A.check_row_sources(doc)
        self.assertIn('row_without_official_fixture_link', codes(found))
        self.assertIn(doc['matches'][0]['id'], next(
            f for f in found if f['code'] == 'row_without_official_fixture_link')['detail'])

    def test_evidence_outside_the_official_allowlist_is_flagged(self):
        doc = self.open_only()
        doc['matches'][0]['evidence'] = [{'url': 'https://random-blog.example/odds'}]
        found = A.check_row_sources(doc)
        self.assertIn('evidence_host_outside_allowlist', codes(found))
        self.assertIn('random-blog.example', next(
            f for f in found if f['code'] == 'evidence_host_outside_allowlist')['detail'])

    def test_a_subdomain_of_an_official_host_is_accepted(self):
        doc = self.open_only()
        doc['matches'][0]['evidence'] = [{'url': 'https://www.hltv.org/matches/2399086/x'}]
        self.assertNotIn('evidence_host_outside_allowlist', codes(A.check_row_sources(doc)))

    def test_a_row_with_neither_pick_nor_reason_is_the_reported_symptom(self):
        # "We don't have picks" is exactly this state, and it is the only one the
        # auditor treats as frozen rather than flaggable.
        doc = self.open_only()
        row = doc['matches'][0]
        row['pick'] = None
        row['reason'] = None
        row['attempts'] = []
        found = A.check_row_sources(doc)
        self.assertIn('row_with_neither_pick_nor_limitation', codes(found))

    def test_a_row_with_a_recorded_limitation_is_not_a_failure(self):
        doc = self.open_only()
        row = doc['matches'][0]
        row['pick'] = None
        row['probabilities'] = None
        row['attempts'] = [{'provider': 'Polymarket', 'status': 'unresolved',
                            'reason': 'No exact team-pair and UTC-start match'}]
        self.assertNotIn('row_with_neither_pick_nor_limitation', codes(A.check_row_sources(doc)))

    def test_an_empty_board_is_never_reported_as_fully_sourced(self):
        # "All zero open rows carry an official link" is a vacuous truth. A
        # vacuous pass is worse than no check, so an empty board reports itself.
        for doc in ({'matches': []}, {'matches': [{'id': '1', 'state': 'not_open'}]}, None, {}):
            found = A.check_row_sources(doc)
            self.assertNotIn('rows_sourced', codes(found), doc)
        found = A.check_row_sources({'matches': [{'id': '1', 'state': 'not_open'}]})
        self.assertEqual(codes(found), ['no_open_rows'])
        self.assertEqual(found[0]['severity'], 'flag')
        self.assertIn('This is not coverage', found[0]['detail'])


class PickReproduction(unittest.TestCase):
    def test_every_committed_pick_reproduces(self):
        self.assertEqual(codes(A.check_pick_is_the_larger_probability(SNAPSHOT)), ['picks_reproducible'])

    def test_a_flipped_pick_is_caught(self):
        doc = {'matches': [dict(m) for m in SNAPSHOT['matches'] if m['state'] == 'open']}
        row = doc['matches'][0]
        row['pick'] = row['teams'][1 - row['teams'].index(row['pick'])]
        found = A.check_pick_is_the_larger_probability(doc)
        self.assertEqual(found[0]['code'], 'pick_not_reproducible')
        self.assertIn('the larger probability is', found[0]['detail'])

    def test_probabilities_that_do_not_sum_to_one_are_caught(self):
        doc = {'matches': [dict(m) for m in SNAPSHOT['matches'] if m['state'] == 'open']}
        doc['matches'][0]['probabilities'] = [0.6, 0.6]
        self.assertIn('sum to', A.check_pick_is_the_larger_probability(doc)[0]['detail'])

    def test_unpriced_rows_are_skipped_not_invented(self):
        doc = {'matches': [{'id': 'x', 'state': 'open', 'teams': ['A', 'B'],
                            'probabilities': None, 'pick': 'A'}]}
        self.assertEqual(codes(A.check_pick_is_the_larger_probability(doc)), ['picks_reproducible'])


class VerdictAndExitCodes(unittest.TestCase):
    def test_a_current_board_is_current(self):
        result = A.audit(live_receipt(30), [run('success', 20)], SNAPSHOT, NOW)
        self.assertEqual(result['verdict'], 'current')
        self.assertTrue(result['current'])
        self.assertEqual(result['counts']['frozen'], 0)

    def test_a_frozen_board_is_frozen_and_carries_the_step_names(self):
        runs = [run('failure', 60 + 150 * i, run_id=40062143026 + i) for i in range(5)]
        steps = {str(40062143026 + i): ['Unit and independent failure-mode tests (verify-build)']
                 for i in range(5)}
        result = A.audit(live_receipt(1066), runs, SNAPSHOT, NOW, steps_by_run=steps)
        self.assertEqual(result['verdict'], 'frozen')
        self.assertFalse(result['current'])
        red = next(f for f in result['findings'] if f['code'] == 'publish_chain_red')
        self.assertIn('Unit and independent failure-mode tests', red['detail'])
        self.assertEqual(len(red['failed_steps']), 5)
        # Both independent proofs of the outage are present, not just one.
        self.assertIn('snapshot_outside_evidence_window', codes(result['findings']))

    def test_offline_is_honest_about_what_it_could_not_read(self):
        result = A.audit({'snapshot_generated_at': stamp(1066)}, [], SNAPSHOT, NOW,
                         receipt_is_live=False, history_read=False)
        self.assertFalse(any(f['severity'] == 'frozen' for f in result['findings']),
                         'offline must not claim proof it does not have')
        self.assertIn('run_history_not_read', codes(result['findings']))
        self.assertIn('committed_baseline_outside_evidence_window', codes(result['findings']))

    def test_the_ledger_links_every_run_it_cites(self):
        runs = [run('failure', 60 + 150 * i, run_id=40062143026 + i) for i in range(5)]
        steps = {'40062143026': ['Unit and independent failure-mode tests (verify-build)']}
        text = A.markdown(A.audit(live_receipt(1066), runs, SNAPSHOT, NOW, steps_by_run=steps))
        self.assertIn('https://github.com/o/r/actions/runs/40062143026', text)
        self.assertIn('Unit and independent failure-mode tests', text)
        self.assertIn('build-info.json', text)
        self.assertIn('data/latest.json', text)
        self.assertIn('FROZEN', text)

    def test_timestamps_are_parsed_or_none_never_guessed(self):
        self.assertIsNone(A.utc(None))
        self.assertIsNone(A.utc('yesterday'))
        self.assertIsNone(A.age_minutes('yesterday', NOW))
        self.assertAlmostEqual(A.age_minutes(stamp(90), NOW), 90, delta=0.01)


class VerifierConsultsTheSourcedAliasRegister(unittest.TestCase):
    """Row 1083121 blocked the merge gate for all 31 open rows.

    Hotspawn lists *Projeto do KinGui*; Polymarket market 6081997 lists the
    outcome *Tropa do KinGui* at the same 2026-10-24T16:00:00Z start against
    *MEIA NOITE*. `verification-c6/audit_snapshot.py` — the auditor wired into
    `scripts.quarantine` — reported 0 failures, while
    `research/session-0cc1138a/verify_0cc1138a.py` refused the row, failing three
    assertions and blocking publication for every other verified row.

    The pairing is not a guess: `data/identities.json` records
    `canonical: "Tropa do KinGui"` with
    `names: ["Tropa do KinGui", "Projeto do KinGui", "ex-Keyd Stars"]`, sourced to
    an HLTV match page and a Polymarket market with a written basis (Valve's
    four-player roster-continuity rule, checked 2026-10-22).

    Session 35c6e1e9 first repaired this by making the verifier read that
    register. While the branch was in review, sessions 174afa4f / a30d31a0 /
    cecfe864 landed a **stricter** version of the same repair (PR #265): the
    mapping is accepted only when the evidence record's own `identity_sources`
    *and* the committed registry both name the labels under one canonical
    identity with an `https://` source and a written basis. That supersedes this
    session's edit, so the edit was dropped on rebase rather than merged over
    theirs. These tests pin the contract that actually shipped, and the property
    that made it safe: the alias is evidence-bound, not blanket.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'verify_0cc1138a', ROOT / 'research/session-0cc1138a/verify_0cc1138a.py')
        cls.V = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.V)
        # Integration repair (session bf1b12c7, 2026-10-24): fixture 1083121
        # locked and left Hotspawn's scheduled feed, so on the 16:34Z refresh
        # ``next(...)`` raised StopIteration inside the publisher's root gate
        # (harvest run 40112589540). The alias contract is a property of the
        # verifier, so the row is read from the live snapshot when it is still
        # listed, else from the retained capture that published it (08:06Z,
        # research/harvest-ce45f672/snapshot.json). The full-board audit below
        # still runs over the live snapshot.
        cls.row = next((m for m in SNAPSHOT['matches'] if m['id'] == '1083121'), None)
        cls.archived = None
        if cls.row is None or not (cls.row.get('evidence') or []):
            archive = json.loads((ROOT / 'research/harvest-ce45f672/snapshot.json').read_text())
            cls.row = next(m for m in archive['matches'] if m['id'] == '1083121')
            cls.archived = archive
        cls.ev = (cls.row.get('evidence') or [{}])[0]

    def test_the_registry_entry_is_sourced_and_links_both_labels(self):
        entries = json.loads((ROOT / 'data' / 'identities.json').read_text())['aliases']
        entry = next(e for e in entries if e.get('canonical') == 'Tropa do KinGui')
        self.assertIn('Projeto do KinGui', entry['names'])
        self.assertTrue(entry['source'].startswith('https://www.hltv.org/'), entry['source'])
        self.assertTrue(str(entry.get('additional_source', '')).startswith('https://'), entry)
        self.assertTrue(str(entry.get('basis', '')).strip(), 'a written basis is required')

    def test_the_evidence_record_carries_the_same_receipted_alias(self):
        # The stricter rule needs BOTH halves, so pin the half that is per-row.
        ids = self.ev.get('identity_sources') or []
        entry = next((e for e in ids if e.get('canonical') == 'Tropa do KinGui'), None)
        self.assertIsNotNone(entry, 'evidence record lost its identity_sources')
        self.assertIn('Projeto do KinGui', entry['names'])
        self.assertTrue(str(entry.get('source', '')).startswith('https://'), entry)
        self.assertTrue(str(entry.get('basis', '')).strip(), entry)

    def test_the_row_now_reproduces(self):
        groups = self.V.alias_groups(self.ev)
        self.assertTrue(any({self.V.norm('Tropa do KinGui'), self.V.norm('Projeto do KinGui')} <= g
                            for g in groups), groups)
        self.assertEqual(
            self.V.order_prices(['Tropa do KinGui', 'MEIA NOITE'], [0.615, 0.385],
                                self.row['teams'], self.ev), [0.615, 0.385])
        self.assertEqual(self.row['pick'], 'Projeto do KinGui')
        # Integration repair (session ce45f672, 2026-10-24): [0.615, 0.385] was
        # this row's exchange mid on the 06:19Z board; the market moved to
        # [0.595, 0.405] by 08:03Z, so the literal was pinning a price rather
        # than the property under test. The row must reproduce from its own
        # evidence, whatever the market's current mid is.
        rederived, kind = self.V.evidence_probabilities(self.ev, self.row['teams'])
        self.assertEqual(kind, 'exchange_mid')
        self.assertAlmostEqual(self.row['probabilities'][0], rederived[0], places=9)
        self.assertAlmostEqual(self.row['probabilities'][1], rederived[1], places=9)
        self.assertAlmostEqual(self.row['probabilities'][0] + self.row['probabilities'][1], 1.0, places=9)
        failures = [r for r in self.V.audit(SNAPSHOT) if r['problems']]
        self.assertEqual(failures, [], 'unreproducible: %r' % failures[:2])

    def test_the_alias_is_evidence_bound_not_blanket(self):
        # Without the row's own receipted evidence the same labels must still be
        # refused. This is the property that makes accepting the alias safe: it
        # is bound to the fixture that sourced it, not a global rename.
        with self.assertRaises(ValueError):
            self.V.order_prices(['Tropa do KinGui', 'MEIA NOITE'], [0.615, 0.385],
                                ['Projeto do KinGui', 'MEIA NOITE'])
        self.assertFalse(self.V.same_team('Tropa do KinGui', 'Projeto do KinGui'))
        self.assertTrue(self.V.same_team('Tropa do KinGui', 'Projeto do KinGui',
                                         self.ev.get('identity_sources')))

    def test_an_ambiguous_or_unmapped_label_is_still_refused(self):
        with self.assertRaises(ValueError):
            self.V.order_prices(['Alpha', 'Alpha'], [0.5, 0.5], ['Alpha', 'Beta'], self.ev)
        with self.assertRaises(ValueError):
            self.V.order_prices(['Some Unknown XI', 'Beta'], [0.5, 0.5],
                                ['Unrelated Club', 'Beta'], self.ev)

    def test_the_previously_pinned_label_behaviours_are_unchanged(self):
        self.assertEqual(self.V.order_prices(['Beta', 'Alpha'], [0.3, 0.7], ['Alpha', 'Beta']), [0.7, 0.3])
        self.assertEqual(self.V.order_prices(['BakS eSports', 'Brute'], [0.4, 0.6], ['BakS', 'BRUTE']),
                         [0.4, 0.6])
        self.assertEqual(self.V.order_prices(['ALKA', 'Los Ni\u00f1os'], [0.7, 0.3], ['Alka', 'LOS NINOS']),
                         [0.7, 0.3])

    def test_an_unsourced_registry_entry_is_not_evidence(self):
        groups = self.V.committed_identity_groups()
        self.assertTrue(groups, 'the committed registry produced no usable groups')
        entries = json.loads((ROOT / 'data' / 'identities.json').read_text())['aliases']
        for entry in entries:
            group = {self.V.norm(n) for n in (entry.get('names') or []) if self.V.norm(n)}
            if not str(entry.get('source', '')).startswith('https://') or not str(entry.get('basis', '')).strip():
                self.assertNotIn(group, groups, 'an unsourced alias was accepted as evidence')


class NeverAMergeGate(unittest.TestCase):
    def test_pages_yml_does_not_invoke_this_auditor(self):
        # The 2026-10-23/24 outage was caused by snapshot-coupled assertions
        # running as a blocking publication gate. This module reads wall-clock
        # staleness and is advisory by design; if it ever appears in the
        # publication workflow the same deadlock returns.
        pages = (ROOT / '.github/workflows/pages.yml').read_text()
        self.assertNotIn('verify_35c6e1e9', pages)

    def test_the_auditor_documents_the_rule(self):
        self.assertIn('never be wired into the merge gate', A.__doc__)
        self.assertIn('17.7 h', A.__doc__)

    def test_the_module_never_writes_data_or_publishes(self):
        source = (ROOT / 'scripts/verify_35c6e1e9.py').read_text()
        for forbidden in ('scripts.build', 'scripts.refresh', 'publish_root_fallback',
                          'upload-pages-artifact', "method='PUT'", "method='DELETE'"):
            self.assertNotIn(forbidden, source, forbidden)


class RootFallbackCannotDivergePairedAssets(unittest.TestCase):
    """Commit f54b37a moved one half of a byte-identical pair; this is the guard.

    ``scripts/build.py`` copies ``site/assets`` into ``public/assets``, and
    ``scripts.stage_legacy.ALLOWED`` stages ``assets/style.css`` but never
    ``site/assets/style.css``. Staging a ``public/`` tree built from a different
    source copy therefore reverts one committed file and leaves its twin, which
    turned main red and deadlocked the next scheduled publication before it ever
    reached refresh, build or deploy.
    """

    def write(self, tree, relative, text):
        path = tree / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_identical_pairs_are_safe_to_stage(self):
        import tempfile
        from scripts.publish_root_fallback import asset_divergence
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            self.write(tree, 'public/assets/style.css', 'a{color:red}')
            self.write(tree, 'site/assets/style.css', 'a{color:red}')
            self.assertEqual(asset_divergence(tree / 'public', tree), [])

    def test_a_build_from_an_older_source_is_refused_not_staged(self):
        import tempfile
        from scripts.publish_root_fallback import asset_divergence, main
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            # public/ carries the pre-exec-bar CSS; site/ already has the new one,
            # exactly the f54b37a shape.
            self.write(tree, 'public/assets/style.css', 'a{color:red}')
            self.write(tree, 'site/assets/style.css', 'a{color:red}.exec-bar-link{}')
            found = asset_divergence(tree / 'public', tree)
            self.assertEqual([d['asset'] for d in found], ['assets/style.css'])
            self.assertNotEqual(found[0]['staged_sha256'], found[0]['committed_source_sha256'])
            # The manifest is fresh, so the snapshot rule alone would publish.
            self.write(tree, 'public/build-info.json', json.dumps(
                {'snapshot_generated_at': '2026-10-24T06:00:00Z'}))
            self.write(tree, 'build-info.json', json.dumps(
                {'snapshot_generated_at': '2026-10-23T01:00:00Z'}))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(['--public', str(tree / 'public'), '--root', str(tree),
                             '--cooldown-hours', '0', '--now', '2026-10-24T06:30:00+00:00'])
            self.assertEqual(code, 0, 'a refusal is a normal exit with a reason, not a crash')
            report = json.loads(out.getvalue())
            self.assertFalse(report['publish'])
            self.assertIn('byte-identical', report['reason'])
            self.assertIn('f54b37a', report['reason'])
            self.assertEqual(report['files'], [], 'nothing may be written')
            self.assertEqual(report['asset_divergence'][0]['asset'], 'assets/style.css')
            # The root copy was left exactly as it was.
            self.assertEqual((tree / 'site/assets/style.css').read_text(), 'a{color:red}.exec-bar-link{}')
            self.assertFalse((tree / 'assets/style.css').exists())

    def test_app_js_is_guarded_too(self):
        import tempfile
        from scripts.publish_root_fallback import asset_divergence
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            self.write(tree, 'public/assets/app.js', 'old()')
            self.write(tree, 'site/assets/app.js', 'new()')
            self.assertEqual([d['asset'] for d in asset_divergence(tree / 'public', tree)],
                             ['assets/app.js'])

    def test_a_missing_copy_is_not_a_divergence(self):
        # Nothing to compare is not proof of a conflict; the ALLOWED-set
        # assertion inside stage_legacy still governs what may be written.
        import tempfile
        from scripts.publish_root_fallback import asset_divergence
        with tempfile.TemporaryDirectory() as tmp:
            tree = pathlib.Path(tmp)
            self.write(tree, 'public/assets/style.css', 'a{}')
            self.assertEqual(asset_divergence(tree / 'public', tree), [])

    def test_the_committed_copies_are_identical_right_now(self):
        # The repair itself: both committed copies carry the build's own output,
        # including the exec-bar rules the phone layout needs.
        #
        # Only *committed* files are compared. An earlier revision of this test
        # also compared ROOT/public/assets/style.css and failed the moment main
        # moved forward, because public/ is a gitignored scratch directory: it
        # holds whatever build happened to run last in this checkout, not the
        # repository's state. Asserting on it pins an ephemeral artifact, which
        # is the same category of mistake as pinning a point-in-time board.
        root_css = (ROOT / 'assets' / 'style.css').read_bytes()
        self.assertEqual(root_css, (ROOT / 'site' / 'assets' / 'style.css').read_bytes(),
                         'the two committed CSS copies must stay byte-identical')
        self.assertIn(b'.exec-bar-link', root_css)
        self.assertIn(b'body[data-page="index"] main>#exec-summary{order:5}', root_css)

    def test_the_manifest_describes_the_css_that_ships(self):
        import hashlib
        man = json.loads((ROOT / 'build-info.json').read_text())
        shipped = hashlib.sha256((ROOT / 'assets' / 'style.css').read_bytes()).hexdigest()
        self.assertEqual(man['files']['assets/style.css'], shipped)


class MeasuredOutageReceipt(unittest.TestCase):
    """The committed receipt cites official identifiers, so the report is checkable."""

    # Dated on purpose. This is frozen evidence of a specific outage, not a
    # mutable file: once the board recovers the streak resets, and a test pinned
    # to a regenerated receipt would start asserting a history that no longer
    # happened. Reproduce with:
    #   python -m scripts.verify_35c6e1e9 --live --token $TOKEN \
    #     --output research/session-35c6e1e9/continuity-receipt-<NEW>.json
    RECEIPT = ROOT / 'research/session-35c6e1e9/continuity-receipt-OUTAGE-2026-10-24T0602Z.json'

    def test_the_receipt_records_the_five_failed_runs_and_their_step(self):
        self.assertTrue(self.RECEIPT.exists(), 'the dated outage receipt is committed evidence')
        data = json.loads(self.RECEIPT.read_text())
        self.assertEqual(data['mode'], 'live')
        red = next(f for f in data['findings'] if f['code'] == 'publish_chain_red')
        self.assertEqual(red['streak'], 5)
        self.assertTrue(red['head_sha'].startswith('5d56f35e'))
        self.assertEqual(set(red['failed_run_ids']),
                         {39956197341, 39998307424, 40025828846, 40042111432, 40062143026})
        for run_id, steps in red['failed_steps'].items():
            self.assertIn('Unit and independent failure-mode tests (verify-build)', steps, run_id)

    def test_the_receipt_records_what_the_sandbox_could_not_read(self):
        # The authoring sandbox cannot reach the Pages host, and that is recorded
        # rather than papered over: an unread source is a stated limitation.
        data = json.loads(self.RECEIPT.read_text())
        self.assertTrue(any('live build receipt unreadable' in p for p in data['source_problems']),
                        data['source_problems'])


if __name__ == '__main__':
    unittest.main()
