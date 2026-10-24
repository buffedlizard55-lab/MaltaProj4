"""Publication-continuity audit: is the live board current, and if not, why?

Session 35c6e1e9, 2026-10-24.

Why this exists
---------------
This repository can already prove that a *snapshot* is internally consistent:
``scripts.validate`` re-checks every row, calculation, link and checksum,
``verification-c6/audit_snapshot.py`` re-derives each row independently, and
``research/session-0cc1138a/verify_0cc1138a.py`` replays the arithmetic with no
shared code. None of them can answer the one question that mattered on
2026-10-24, because all of them run *inside* the pipeline they are auditing:

    Is the board the public actually sees current - and if it is not, what
    stopped it, at which step, on which commit, and for how long?

Measured that day, from ``api.github.com`` and the committed artifacts:

* five consecutive ``pages.yml`` runs on ``main`` failed -
  39956197341 (2026-10-23T12:49:03Z), 39998307424 (17:50:02Z),
  40025828846 (21:18:45Z), 40042111432 (23:53:03Z), 40062143026
  (2026-10-24T04:23:24Z) - every one on ``head_sha 5d56f35e``, and the jobs
  endpoint names the same failed step for all five:
  ``Unit and independent failure-mode tests (verify-build)``;
* ``GET /repos/{repo}/pages/builds/latest`` reported ``status: built``,
  ``commit 5d56f35e``, ``created_at 2026-10-23T11:48:51Z``;
* the published ``build-info.json`` still carried
  ``snapshot_generated_at 2026-10-23T11:47:19.504519Z`` - 1066 min old at
  05:33Z against the snapshot's own ``stale_after_hours: 8``;
* so every open pick on the live site was withheld, and nothing in the
  repository said so: the watchdog ticks all reported ``success`` and no
  escalation issue existed.

This auditor is deliberately outside the pipeline. It reads three official
sources and compares them with each other, never with a value the pipeline
asserted about itself:

1. the live Pages build receipt (``build-info.json`` served at the site root);
2. the ``pages.yml`` run history and each failed run's job/step conclusions;
3. the committed snapshot ``data/latest.json`` for its own stated TTL and rows.

Two modes
---------
``--offline`` audits only what is committed, so it can run in CI on a pull
request with no network and no token. ``--live`` adds the two GitHub reads and
the published receipt; it is what produces a dated receipt for the record.

Nothing here writes data, publishes, or bypasses a gate. Exit code 0 means the
board is current (or the audit could not be performed and said so); exit 1
means the audit *proved* the board is frozen; exit 2 means the audit itself
could not read enough to decide. Failing closed on an undecidable state is the
whole point: "we could not tell" must never be reported as "all good".

This auditor is **advisory and must never be wired into the merge gate**. It
reads wall-clock staleness, so a committed baseline older than its own evidence
window is normal between refreshes; making that red would deadlock exactly the
pipeline it is meant to protect - which is what happened on 2026-10-23/24, when
two snapshot-coupled assertions in ``tests/test_session_0cc1138a.py`` held every
scheduled publication for 17.7 h. ``tests/test_session_35c6e1e9.py`` pins the
rule: ``.github/workflows/pages.yml`` must not invoke this module.
"""
import argparse
import datetime
import json
import sys
import urllib.error
import urllib.request

PAGES_WORKFLOW = 'pages.yml'
SITE = 'https://buffedlizard55-lab.github.io/MaltaProj4/'
REPO = 'buffedlizard55-lab/MaltaProj4'
UA = {'User-Agent': 'cs2-continuity-audit/1.0', 'Accept': 'application/vnd.github+json'}
# Hosts whose URLs count as an official source for a row. Anything else is
# reported, never silently accepted.
OFFICIAL_EVIDENCE_HOSTS = (
    'polymarket.com', 'hltv.org', 'bo3.gg', 'github.com', 'hotspawn.com',
    'valvesoftware.com', 'kalshi.com', 'pinnacle.com', 'gg.bet', 'egamersworld.com',
)


def utc(value):
    """Parse an ISO-8601 instant. Returns None rather than guessing."""
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def age_minutes(value, now):
    then = utc(value)
    return None if then is None else (now - then).total_seconds() / 60.0


def get_json(url, token=None, timeout=30):
    headers = dict(UA)
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode() or 'null')


def api(path, token):
    return get_json('https://api.github.com' + path, token)


# --------------------------------------------------------------------------
# Pure checks. Each returns a list of findings; a finding is a dict with a
# severity ('ok', 'flag', 'frozen'), a code and human text. Nothing in here
# touches the network, so every rule is unit-testable on its own.
# --------------------------------------------------------------------------

def check_snapshot_age(receipt, snapshot_ttl_hours, now, receipt_is_live=True):
    """Is the published snapshot inside the evidence window it states for itself?

    ``receipt_is_live`` matters. A stale *committed* baseline only proves that the
    artifact in the repository is old; it cannot prove the public site is frozen,
    because the publisher may have deployed something newer minutes ago. Reporting
    the two cases identically is how a stale baseline turns into a red merge gate -
    the exact deadlock PR #240 was merged to end on 2026-10-24 - so the offline
    case is a flag, never a proof.
    """
    generated = (receipt or {}).get('snapshot_generated_at')
    age = age_minutes(generated, now)
    if age is None:
        return [{'severity': 'frozen' if receipt_is_live else 'flag',
                 'code': 'receipt_unreadable' if receipt_is_live else 'committed_baseline_unreadable',
                 'detail': 'the live build receipt exposes no readable snapshot_generated_at, '
                           'so the published board cannot be shown to be current'
                           if receipt_is_live else
                           'no snapshot timestamp could be read offline, so the committed baseline '
                           'cannot be shown to be current'}]
    window = (snapshot_ttl_hours or 8) * 60
    if age > window and not receipt_is_live:
        return [{'severity': 'flag', 'code': 'committed_baseline_outside_evidence_window',
                 'detail': 'the committed baseline snapshot %s is %.0f min old, outside its own %d h '
                           '(%d min) evidence window. This is not proof the live site is frozen - the '
                           'published receipt was not read - but it is what gets published next if the '
                           'pipeline does not refresh first'
                           % (generated, age, snapshot_ttl_hours or 8, window),
                 'snapshot_generated_at': generated, 'age_minutes': round(age, 1),
                 'window_minutes': window}]
    if age > window:
        return [{'severity': 'frozen', 'code': 'snapshot_outside_evidence_window',
                 'detail': 'published snapshot %s is %.0f min old, outside its own %d h (%d min) '
                           'evidence window: every open pick is withheld on the live site'
                           % (generated, age, snapshot_ttl_hours or 8, window),
                 'snapshot_generated_at': generated, 'age_minutes': round(age, 1),
                 'window_minutes': window}]
    return [{'severity': 'ok', 'code': 'snapshot_inside_evidence_window',
             'detail': 'published snapshot %s is %.0f min old, inside its %d h evidence window'
                       % (generated, age, snapshot_ttl_hours or 8),
             'snapshot_generated_at': generated, 'age_minutes': round(age, 1)}]


def check_publish_chain(runs, now, stale_run_hours=24, history_read=True):
    """Is the publication chain alive, and if it is red, exactly where?

    ``runs`` is the ``pages.yml`` run list for ``main``, newest first. A chain is
    red when the newest completed runs are consecutive failures; the audit then
    reports the streak and the commit, and the caller adds the step names.
    """
    if not runs:
        # Offline (or an unreadable API) cannot prove the chain is red; it can only
        # say the chain was not observed. Claiming 'frozen' here would make every
        # pull-request run of this auditor red for a reason nobody can act on.
        return [{'severity': 'frozen' if history_read else 'flag',
                 'code': 'no_run_history' if history_read else 'run_history_not_read',
                 'detail': 'no %s runs on main were readable, so publication cannot be shown to be alive'
                           % PAGES_WORKFLOW if history_read else
                           'the %s run history was not read in this mode, so whether publication is '
                           'alive is undecidable from here' % PAGES_WORKFLOW}]
    completed = [r for r in runs if r.get('status') == 'completed']
    in_flight = [r for r in runs if r.get('status') != 'completed']
    streak, head = 0, None
    for run in completed:
        if run.get('conclusion') == 'failure':
            streak += 1
            head = head or run.get('head_sha')
        else:
            break
    same_commit = bool(head) and all((r.get('head_sha') or head) == head
                                     for r in completed[:streak])
    findings = []
    newest = completed[0] if completed else None
    if newest is not None:
        last_age = age_minutes(newest.get('created_at'), now)
        if last_age is not None and last_age > stale_run_hours * 60:
            findings.append({'severity': 'flag', 'code': 'no_recent_run',
                             'detail': 'the newest completed %s run on main is %.1f h old (%s); '
                                       'scheduled delivery, not the cron expression, is the binding constraint'
                                       % (PAGES_WORKFLOW, last_age / 60.0, newest.get('created_at')),
                             'run_url': newest.get('html_url')})
    if streak >= 2:
        findings.append({'severity': 'frozen' if same_commit else 'flag',
                         'code': 'publish_chain_red',
                         'detail': '%d consecutive failed %s runs on main%s; publication is not advancing'
                                   % (streak, PAGES_WORKFLOW,
                                      (' on one unmoved commit %s' % head[:8]) if same_commit else ''),
                         'streak': streak, 'head_sha': head,
                         'failed_run_urls': [r.get('html_url') for r in completed[:streak]],
                         'failed_run_ids': [r.get('id') for r in completed[:streak]]})
    elif in_flight:
        findings.append({'severity': 'ok', 'code': 'publish_chain_in_flight',
                         'detail': 'a %s run is %s on main (%s)'
                                   % (PAGES_WORKFLOW, in_flight[0].get('status'), in_flight[0].get('html_url'))})
    elif newest is not None and newest.get('conclusion') == 'success':
        findings.append({'severity': 'ok', 'code': 'publish_chain_green',
                         'detail': 'the newest completed %s run on main succeeded (%s)'
                                   % (PAGES_WORKFLOW, newest.get('html_url'))})
    return findings


def check_row_sources(snapshot):
    """Does every open row carry an official fixture link and price evidence?

    The user's rule is that every table row must have a source link to an
    official site, and a value that cannot be confirmed stays blank and flagged.
    This check never fills anything in: it only reports what the committed
    snapshot already carries.
    """
    rows = (snapshot or {}).get('matches') or []
    open_rows = [m for m in rows if m.get('state') == 'open']
    findings = []
    if not open_rows:
        # "All zero open rows are sourced" is a vacuous truth, and a vacuous pass
        # is worse than no check: it is the shape of an assurance nobody earned.
        # An empty board is a real state (every fixture past its lock) but it is
        # reported as itself, never as coverage.
        return [{'severity': 'flag', 'code': 'no_open_rows',
                 'detail': 'the snapshot carries %d row(s) and none is open, so there is no current pick '
                           'to source-check. This is not coverage; it is an empty board.' % len(rows),
                 'rows': len(rows), 'open_rows': 0}]
    missing_source, missing_evidence, unofficial, no_answer = [], [], [], []
    for row in open_rows:
        label = '%s %s' % (row.get('id'), ' vs '.join(row.get('teams') or []))
        source = row.get('source_url') or ''
        if not source.startswith('https://') or 'hotspawn.com' not in source:
            missing_source.append(label)
        evidence = row.get('evidence') or []
        if not evidence:
            missing_evidence.append(label)
        for item in evidence:
            url = item.get('url') or ''
            host = url.split('/')[2] if url.startswith('https://') and len(url.split('/')) > 2 else ''
            if host and not any(host == h or host.endswith('.' + h) for h in OFFICIAL_EVIDENCE_HOSTS):
                unofficial.append('%s -> %s' % (label, url))
        # A row must publish a pick, or say why it cannot. Both blank is the
        # only unacceptable state, and it is what "no picks" looks like.
        if not row.get('pick') and not (row.get('reason') or row.get('attempts')):
            no_answer.append(label)
    if missing_source:
        findings.append({'severity': 'frozen', 'code': 'row_without_official_fixture_link',
                         'detail': '%d open row(s) carry no https hotspawn.com fixture link: %s'
                                   % (len(missing_source), '; '.join(missing_source[:5]))})
    if missing_evidence:
        findings.append({'severity': 'flag', 'code': 'row_without_evidence',
                         'detail': '%d open row(s) carry no evidence entry: %s'
                                   % (len(missing_evidence), '; '.join(missing_evidence[:5]))})
    if unofficial:
        findings.append({'severity': 'flag', 'code': 'evidence_host_outside_allowlist',
                         'detail': '%d evidence URL(s) point outside the official-host allowlist: %s'
                                   % (len(unofficial), '; '.join(unofficial[:5]))})
    if no_answer:
        findings.append({'severity': 'frozen', 'code': 'row_with_neither_pick_nor_limitation',
                         'detail': '%d open row(s) publish neither a pick nor a recorded reason: %s'
                                   % (len(no_answer), '; '.join(no_answer[:5]))})
    if not findings:
        findings.append({'severity': 'ok', 'code': 'rows_sourced',
                         'detail': 'all %d open rows carry an official hotspawn.com fixture link, at least '
                                   'one evidence URL inside the official-host allowlist, and a pick or a '
                                   'recorded reason' % len(open_rows),
                         'open_rows': len(open_rows),
                         'with_pick': sum(1 for m in open_rows if m.get('pick')),
                         'with_probability': sum(1 for m in open_rows if m.get('probabilities'))})
    return findings


def check_pick_is_the_larger_probability(snapshot):
    """Re-derive the pick from the row's own numbers. Never trusts the label."""
    wrong = []
    for row in (snapshot or {}).get('matches') or []:
        if row.get('state') != 'open':
            continue
        probs, teams, pick = row.get('probabilities'), row.get('teams') or [], row.get('pick')
        if not probs or not pick or len(probs) != len(teams):
            continue
        if abs(sum(probs) - 1.0) > 0.01:
            wrong.append('%s probabilities sum to %.4f' % (row.get('id'), sum(probs)))
        elif teams[probs.index(max(probs))] != pick:
            wrong.append('%s publishes pick %s but the larger probability is %s'
                         % (row.get('id'), pick, teams[probs.index(max(probs))]))
    if wrong:
        return [{'severity': 'frozen', 'code': 'pick_not_reproducible',
                 'detail': '%d open row(s) do not reproduce from their own numbers: %s'
                           % (len(wrong), '; '.join(wrong[:5]))}]
    return [{'severity': 'ok', 'code': 'picks_reproducible',
             'detail': 'every published open-row pick is the larger of its own two probabilities, '
                       'and each pair sums to 1.000 within 0.01'}]


def audit(receipt, runs, snapshot, now, steps_by_run=None, receipt_is_live=True, history_read=True):
    """Run every check and return one receipt. Pure: no network, no clock reads."""
    findings = []
    findings += check_snapshot_age(receipt, (snapshot or {}).get('stale_after_hours'), now, receipt_is_live)
    chain = check_publish_chain(runs, now, history_read=history_read)
    findings += chain
    red = next((f for f in chain if f['code'] == 'publish_chain_red'), None)
    if red and steps_by_run:
        named = {str(run_id): steps for run_id, steps in steps_by_run.items() if steps}
        if named:
            red['failed_steps'] = named
            red['detail'] += '; failed step(s): ' + '; '.join(
                sorted({s for steps in named.values() for s in steps}))
    findings += check_row_sources(snapshot)
    findings += check_pick_is_the_larger_probability(snapshot)
    frozen = [f for f in findings if f['severity'] == 'frozen']
    flags = [f for f in findings if f['severity'] == 'flag']
    return {'schema': 'publication-continuity/1', 'audited_at': now.isoformat(timespec='seconds'),
            'site': SITE, 'repo': REPO,
            'published_revision': (receipt or {}).get('revision'),
            'published_built_at': (receipt or {}).get('built_at'),
            'published_snapshot_generated_at': (receipt or {}).get('snapshot_generated_at'),
            'published_rows': (receipt or {}).get('rows'),
            'committed_snapshot_generated_at': (snapshot or {}).get('generated_at'),
            'committed_stale_after_hours': (snapshot or {}).get('stale_after_hours'),
            'current': not frozen,
            'verdict': ('current' if not frozen and not flags else
                        'current-with-flags' if not frozen else 'frozen'),
            'counts': {'ok': sum(1 for f in findings if f['severity'] == 'ok'),
                       'flag': len(flags), 'frozen': len(frozen)},
            'findings': findings}


def markdown(receipt):
    """A human-readable ledger. Every claim carries its source link."""
    lines = ['# Publication-continuity audit — %s' % receipt['audited_at'], '',
             'Verdict: **%s**%s' % (receipt['verdict'],
                                     '' if receipt['current'] else ' — the board the public sees is frozen'),
             '',
             '| Field | Value | Source |', '| --- | --- | --- |',
             '| published revision | `%s` | [build-info.json](%sbuild-info.json) |'
             % (receipt.get('published_revision') or 'unreadable', SITE),
             '| published built_at | `%s` | [build-info.json](%sbuild-info.json) |'
             % (receipt.get('published_built_at') or 'unreadable', SITE),
             '| published snapshot | `%s` | [build-info.json](%sbuild-info.json) |'
             % (receipt.get('published_snapshot_generated_at') or 'unreadable', SITE),
             '| committed snapshot | `%s` | [data/latest.json](https://github.com/%s/blob/main/data/latest.json) |'
             % (receipt.get('committed_snapshot_generated_at') or 'unreadable', REPO),
             '| stated evidence TTL | `%s h` | [data/latest.json](https://github.com/%s/blob/main/data/latest.json) |'
             % (receipt.get('committed_stale_after_hours'), REPO),
             '', '## Findings', '']
    for finding in receipt['findings']:
        icon = {'ok': 'PASS', 'flag': 'FLAG', 'frozen': 'FROZEN'}[finding['severity']]
        lines.append('- **%s** `%s` — %s' % (icon, finding['code'], finding['detail']))
        for url in finding.get('failed_run_urls') or []:
            lines.append('  - run: %s' % url)
        for run_id, steps in (finding.get('failed_steps') or {}).items():
            for step in steps:
                lines.append('  - run %s failed step: `%s` (GitHub jobs endpoint)' % (run_id, step))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--repo', default=REPO)
    parser.add_argument('--site', default=SITE)
    parser.add_argument('--token', default=None, help='GitHub token for the live reads (--live only)')
    parser.add_argument('--snapshot', default='data/latest.json')
    parser.add_argument('--live', action='store_true',
                        help='read the live Pages receipt and the pages.yml run history')
    parser.add_argument('--offline', action='store_true',
                        help='audit the committed artifacts only (no network, no token)')
    parser.add_argument('--output', default=None, help='write the JSON receipt here')
    parser.add_argument('--markdown', default=None, help='write the ledger here')
    parser.add_argument('--now', default=None, help='override "now" (tests only)')
    args = parser.parse_args()
    if args.live and args.offline:
        print('--live and --offline are mutually exclusive', file=sys.stderr)
        return 2
    now = utc(args.now) if args.now else datetime.datetime.now(datetime.timezone.utc)
    try:
        with open(args.snapshot) as handle:
            snapshot = json.load(handle)
    except (OSError, ValueError) as exc:
        print('committed snapshot unreadable: %s' % exc, file=sys.stderr)
        return 2
    receipt, runs, steps_by_run, problems = None, [], {}, []
    if args.live:
        if not args.token:
            print('--live needs --token', file=sys.stderr)
            return 2
        try:
            receipt = get_json(args.site.rstrip('/') + '/build-info.json?audit=' + now.strftime('%Y%m%d%H%M'))
        except Exception as exc:
            problems.append('live build receipt unreadable: %s' % str(exc)[:200])
        try:
            listing = api('/repos/%s/actions/workflows/%s/runs?branch=main&per_page=25'
                          % (args.repo, PAGES_WORKFLOW), args.token) or {}
            runs = listing.get('workflow_runs') or []
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as exc:
            problems.append('run history unreadable: %s' % str(exc)[:200])
        failed = [r for r in runs if r.get('conclusion') == 'failure'][:5]
        for run in failed:
            try:
                jobs = api('/repos/%s/actions/runs/%s/jobs' % (args.repo, run.get('id')), args.token) or {}
                names = []
                for job in jobs.get('jobs') or []:
                    names += ['%s (%s)' % (s.get('name'), job.get('name'))
                              for s in (job.get('steps') or []) if s.get('conclusion') == 'failure']
                steps_by_run[str(run.get('id'))] = names
            except Exception:
                steps_by_run[str(run.get('id'))] = []
    else:
        # Offline: the committed build receipt stands in for the published one,
        # and the run history is absent, which the chain check reports honestly
        # instead of treating as green.
        try:
            with open('build-info.json') as handle:
                committed = json.load(handle)
            receipt = {'revision': committed.get('revision'), 'built_at': committed.get('built_at'),
                       'rows': committed.get('rows'),
                       'snapshot_generated_at': snapshot.get('generated_at')}
        except (OSError, ValueError) as exc:
            problems.append('committed build receipt unreadable: %s' % str(exc)[:200])
    result = audit(receipt, runs, snapshot, now, steps_by_run,
                   receipt_is_live=bool(args.live), history_read=bool(args.live))
    result['mode'] = 'live' if args.live else 'offline'
    result['source_problems'] = problems
    if problems and not args.live:
        # Offline mode cannot see the run history, so it cannot certify that
        # publication is alive. Say so rather than implying a clean bill.
        result['verdict'] = result['verdict'] + '-undecidable-run-history'
    text = json.dumps(result, indent=1, sort_keys=True)
    print(text)
    if args.output:
        with open(args.output, 'w') as handle:
            handle.write(text + '\n')
    if args.markdown:
        with open(args.markdown, 'w') as handle:
            handle.write(markdown(result))
    if result['counts']['frozen']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
