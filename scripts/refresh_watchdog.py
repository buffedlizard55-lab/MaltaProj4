"""Cadence watchdog for the CS2 pick desk (no publication, no data writes).

Why this exists: on 15-16 October 2026 GitHub delivered the workflow's
``schedule`` events 3-5 hours late and then skipped the 23:17, 00:17 and 02:17
slots entirely (``gh api repos/.../actions/runs?event=schedule`` shows the last
scheduled run at 21:22:25Z, which also failed). A cron-only refresh cannot meet
the requested "every 4-8 hours" promise, because evidence expires eight hours
after it was observed.

This script turns the promise into a measurable rule and runs from a cheap
workflow every 10 minutes: it reads the *published* snapshot age straight from the
live site's build receipt and the workflow run history through GitHub's API, and
dispatches the existing, fully verified publication workflow only when the
published data is older than 90 minutes - beyond the 15-minute scheduled slots. It never edits data, never publishes, never
bypasses a check, and stops itself if it would loop.

Read-only on the site; write permission is used for exactly two things:
``POST /repos/{repo}/actions/workflows/pages.yml/dispatches``, and - only when the
watchdog has stopped because the publication workflow keeps failing on the same
commit - a single deduplicated GitHub issue so the outage is visible to a human
instead of sitting in a log nobody reads. That second path exists because on
23 October 2026 a failing test step held the board frozen for 8 h 40 min: the
watchdog correctly refused to re-dispatch, the live site withheld every pick, and
nothing anywhere said why. The issue is updated in place (never duplicated), the
watchdog closes it automatically once the published snapshot is back inside its
evidence window, and it is not re-created until the gate fails again.

It happened again on 24 October 2026, with the alert path already in place, which
is what session 35c6e1e9 repaired. Measured facts: five consecutive ``pages.yml``
failures on ``5d56f35e`` from 2026-10-23T12:49Z to 2026-10-24T04:23Z, all at the
step *Unit and independent failure-mode tests*; the live Pages receipt still
serving ``snapshot_generated_at 2026-10-23T11:47:19Z``, i.e. 1066 min old against
the snapshot's own ``stale_after_hours: 8``; the watchdog's own pure decision
function replayed against that real run list returning ``action='stop'``,
``consecutive_failures=5``, ``should_escalate=True``; and yet no escalation issue
anywhere - ``GET /search/issues`` for the exact title returned ``total_count: 0``
and ``GET /repos/{repo}/issues?state=open`` returned only ``[239, 204, 7, 5, 1]`` -
while every watchdog tick reported ``success``. The authoring sandbox cannot
download Actions logs (``results-receiver.actions.githubusercontent.com`` is
outside its egress allowlist), so which call raised is not provable and is not
asserted here. What is provable is that the design guaranteed the silence: a
required escalation that failed was swallowed into ``report['escalation']`` inside
a log nobody reads, and the tick still exited 0. Three changes follow from that.
The dedupe lookup now reads the core REST issues listing instead of the Search
API, so the alert depends on the one API family the tick already uses
successfully rather than on a second, separately limited service. A required but
undelivered escalation now emits an ``::error::`` annotation and fails the tick,
because a silent alert is not an alert. And escalation is triggered by the harm
itself - a ``stop`` while the published snapshot is outside its evidence window -
not only by a streak of three, since the budget and unknown-state stops carry no
streak at all. The issue body also names the failing step, read from the jobs
endpoint, so the answer to "why is the board frozen" is in the alert.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

WORKFLOW = 'pages.yml'
ESCALATION_TITLE = 'Publish gate is red: no CS2 picks can be published'
ESCALATION_MARKER = '<!-- cs2-scout-watchdog -->'
UA = {'User-Agent': 'cs2-scout-watchdog/1.0', 'Accept': 'application/vnd.github+json'}


def utc(value):
    return datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(datetime.timezone.utc)


def api(path, token, method='GET', payload=None):
    request = urllib.request.Request('https://api.github.com' + path, method=method,
                                     headers=dict(UA, **{'Authorization': 'Bearer ' + token}))
    if payload is not None:
        request.add_header('Content-Type', 'application/json')
        body = json.dumps(payload).encode()
    else:
        body = None
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode() or '{}')


def http_json(url, timeout=25):
    request = urllib.request.Request(url, headers={'User-Agent': 'cs2-scout-watchdog/1.0'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def age_minutes(value, now):
    if not value:
        return None
    try:
        return (now - utc(value)).total_seconds() / 60.0
    except (ValueError, TypeError):
        return None


def consecutive_failures(runs):
    """Count consecutive completed failed runs at the head of ``runs``."""
    streak = 0
    for r in runs:
        if r.get('status') != 'completed':
            continue
        if r.get('conclusion') == 'failure':
            streak += 1
        else:
            break
    return streak


def evaluate(runs, receipt, now, max_age_minutes, cooldown_minutes, budget, failures):
    """Pure decision function - unit tested. Returns (action, detail)."""
    streak = consecutive_failures(runs)
    fresh = [r for r in runs if r.get('status') != 'completed']
    if fresh:
        return 'skip', ('a refresh run is already %s (%s); the chain re-arms when it completes'
                        % (fresh[0].get('status'), fresh[0].get('html_url')))
    dispatched = [r for r in runs if r.get('event') == 'workflow_dispatch'
                  and age_minutes(r.get('created_at'), now) is not None
                  and age_minutes(r.get('created_at'), now) < cooldown_minutes]
    if dispatched:
        return 'skip', 'a watchdog-triggered run was started %.0f min ago; cooldown applies' % \
            age_minutes(dispatched[0].get('created_at'), now)
    budget_used = sum(1 for r in runs if r.get('event') == 'workflow_dispatch'
                      and (age_minutes(r.get('created_at'), now) or 9e9) < 24 * 60)
    if budget_used >= budget:
        return 'stop', '%d watchdog dispatches in the last 24 h (budget %d); refusing to loop. ' \
                       'Investigate why the scheduled runs are not publishing.' % (budget_used, budget)
    if failures and not receipt:
        return 'stop', ('the live build receipt could not be read (%s) and the Pages URL is not reachable; '
                        'no dispatch on an unknown state' % failures[-1])
    snapshot_age = age_minutes((receipt or {}).get('snapshot_generated_at'), now)
    build_age = age_minutes((receipt or {}).get('built_at'), now)
    if snapshot_age is None:
        if receipt is None:
            return 'stop', 'no build receipt and no fallback timestamp; refusing to guess a staleness value'
        return 'dispatch', 'the receipt has no snapshot time; falling back to build age %.0f min' % (build_age or -1)
    if snapshot_age <= max_age_minutes:
        note = (' (warning: %d consecutive failed runs on main)' % streak) if streak >= 2 else ''
        return 'ok', ('published snapshot is %.0f min old (limit %d min); no action%s'
                      % (snapshot_age, max_age_minutes, note))
    completed = [r for r in runs if r.get('status') == 'completed']
    head_shas = {r.get('head_sha') for r in completed[:streak] if r.get('head_sha')}
    if streak >= 3 and len(head_shas) == 1:
        sha = next(iter(head_shas))[:8]
        return 'stop', ('%d consecutive failed runs on commit %s while snapshot is %.0f min old; '
                        'code or test gate failure requires a fix before dispatching again'
                        % (streak, sha, snapshot_age))
    reason = ('published snapshot is %.0f min old, over the %d-min limit; the scheduled run was late or skipped '
              '(last completed run %s). Dispatching the same verified workflow once.'
              % (snapshot_age, max_age_minutes,
                 next((r.get('updated_at') for r in runs if r.get('conclusion') == 'success'), 'unknown')))
    return 'dispatch', reason


def should_escalate(action, streak, outside_evidence_window=False):
    """Pure rule: raise an issue only when the chain has stopped and the board is harmed.

    ``evaluate`` returns ``stop`` for a red gate (3+ consecutive failures on one
    commit), for a spent budget, and for an unknown state. Only the red-gate case
    is actionable by a human, and only that case carries the streak - so the
    streak rule is kept exactly as it was.

    Session 35c6e1e9 (2026-10-24) adds the second, independent trigger. Measured
    on that date: five consecutive `pages.yml` failures on `5d56f35e` held the
    published snapshot at 1066 min against its own 8 h evidence window, every
    open pick was withheld, and no escalation issue existed - while every
    watchdog tick reported `success`. A `stop` is also the budget-exhausted and
    unknown-state paths, and neither carries a streak of 3 at the moment the
    board first goes stale, so a streak-only rule can leave the harmed window
    unannounced. Escalating on "stopped *and* the published snapshot is outside
    its evidence window" ties the alert to the user-visible harm instead of to
    one particular cause. The two-argument form is unchanged, so every existing
    caller and every pinned assertion keeps its meaning.
    """
    if action != 'stop':
        return False
    return streak >= 3 or bool(outside_evidence_window)


def failing_steps(token, repo, run_id):
    """The names of the failed steps in one run, read from the core REST API.

    The escalation issue existed to answer "why is the board frozen", but it
    named only runs, so a human still had to open each log. On 2026-10-24 the
    answer was a single step - *Unit and independent failure-mode tests* - which
    the jobs endpoint returns directly. Best effort by design: the alert must
    still be filed when this lookup fails, so every error becomes an empty list
    rather than an exception.
    """
    if not run_id:
        return []
    try:
        data = api('/repos/%s/actions/runs/%s/jobs' % (repo, run_id), token) or {}
    except Exception:
        return []
    names = []
    for job in (data.get('jobs') or []) if isinstance(data, dict) else []:
        for step in job.get('steps') or []:
            if step.get('conclusion') == 'failure':
                label = '%s (%s)' % (step.get('name'), job.get('name')) if job.get('name') else str(step.get('name'))
                if label not in names:
                    names.append(label)
    return names


def escalation_body(detail, runs, receipt, pages_url, streak, steps=None, snapshot_age=None,
                    evidence_window_minutes=None):
    """The issue body: what stopped, which runs, which step, and what to fix."""
    failing = [r for r in runs if r.get('conclusion') == 'failure'][:3]
    lines = [ESCALATION_MARKER,
             'The refresh watchdog stopped dispatching because `pages.yml` keeps failing on the same commit, '
             'so the published snapshot cannot leave its evidence window and **every pick is withheld** on the live site.',
             '',
             '- decision: %s' % detail,
             '- consecutive failed `pages.yml` runs on `main`: **%d**' % streak,
             '- published snapshot: `%s`' % ((receipt or {}).get('snapshot_generated_at') or 'unreadable')]
    if snapshot_age is not None:
        window = ('%d min' % evidence_window_minutes) if evidence_window_minutes else 'its evidence window'
        lines.append('- snapshot age: **%.0f min**, outside %s' % (snapshot_age, window))
    lines += ['- live site: %s' % pages_url,
              '',
              'Recent failing runs:']
    for r in failing:
        lines.append('- %s (%s, commit `%s`)' % (r.get('html_url'), r.get('created_at'), (r.get('head_sha') or '')[:8]))
    if not failing:
        lines.append('- none recorded in the last 25 runs')
    if steps:
        lines += ['', 'Failing step(s) reported by the jobs endpoint:']
        lines += ['- `%s`' % s for s in steps]
    lines += ['', 'Fix the failing gate; the watchdog closes this issue automatically once the published '
                  'snapshot is back inside its evidence window, and opens a new one only if it recurs.']
    return '\n'.join(lines)


def find_open_issue(token, repo, title):
    """The open escalation issue for this repository, or None.

    Reads the core REST issues listing, not the Search API. Measured on
    2026-10-24 while the board was frozen: `GET /search/issues?q=...in:title
    "Publish gate is red: no CS2 picks can be published"` returned
    `total_count: 0` and no such issue existed anywhere in
    `GET /repos/{repo}/issues?state=open` (`[239, 204, 7, 5, 1]`), even though
    the watchdog's own pure decision function returned `action='stop'` with
    `should_escalate=True` on the real run list, and the same search shape did
    find #204 and #239 when called by hand. The alert therefore did not land,
    and the tick still exited green. Whichever call raised, the fix is to depend
    on one API family instead of two: this listing is the same core REST service
    the run-history read already uses successfully in the same tick, so the alert
    no longer needs a second, separately limited service to be reachable.

    The listing includes pull requests, so those are skipped; matching is on the
    exact title this script files. Three pages of 100 bound the read.
    """
    for page in (1, 2, 3):
        data = api('/repos/%s/issues?state=open&per_page=100&page=%d' % (repo, page), token)
        if not isinstance(data, list):
            return None
        for item in data:
            if not isinstance(item, dict) or 'pull_request' in item:
                continue
            if (item.get('title') or '') == title:
                return item
        if len(data) < 100:
            return None
    return None


def sync_escalation(token, repo, title, body):
    """Create the issue once, then keep its body current. Returns the action taken."""
    existing = find_open_issue(token, repo, title)
    if existing is None:
        created = api('/repos/%s/issues' % repo, token, method='POST', payload={'title': title, 'body': body})
        return 'created #%s' % created.get('number')
    if (existing.get('body') or '').strip() != body.strip():
        api('/repos/%s/issues/%s' % (repo, existing['number']), token, method='PATCH', payload={'body': body})
        return 'updated #%s' % existing['number']
    return 'unchanged #%s' % existing['number']


def close_escalation(token, repo, title, snapshot_generated_at):
    """Close the escalation issue once the board has actually recovered.

    An alert nobody can close trains everyone to ignore it. Recovery is decided
    by the caller from the published receipt (the snapshot is back inside its
    evidence window), and only an issue this script filed - exact title plus the
    marker in its body - is ever touched. Returns the action taken, or None when
    there was nothing open to close.
    """
    existing = find_open_issue(token, repo, title)
    if existing is None:
        return None
    if ESCALATION_MARKER not in (existing.get('body') or ''):
        return 'skipped #%s (no watchdog marker)' % existing.get('number')
    number = existing['number']
    api('/repos/%s/issues/%s/comments' % (repo, number), token, method='POST',
        payload={'body': '%s\nClosed automatically by the refresh watchdog: the published snapshot '
                         '(`%s`) is back inside its evidence window and picks are live again.'
                         % (ESCALATION_MARKER, snapshot_generated_at or 'unreadable')})
    api('/repos/%s/issues/%s' % (repo, number), token, method='PATCH', payload={'state': 'closed'})
    return 'closed #%s (board recovered)' % number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY'))
    parser.add_argument('--token', default=os.environ.get('ACTIONS_TOKEN'))
    # 90 minutes: pages.yml is scheduled every 15 minutes. The watchdog does not
    # duplicate that cadence; it backfills when the published snapshot has fallen
    # well behind the scheduled slots and uses a cooldown/budget to avoid loops.
    parser.add_argument('--max-age-minutes', type=int, default=90,
                        help='dispatch when the published snapshot is older than this (default: %(default)s)')
    parser.add_argument('--cooldown-minutes', type=int, default=45,
                        help='minimum gap between watchdog-triggered runs (default: %(default)s)')
    parser.add_argument('--budget', type=int, default=10,
                        help='maximum watchdog dispatches per 24 h (default: %(default)s)')
    # 480 min = the snapshot's own `stale_after_hours: 8` in data/latest.json.
    # Past that window every open pick is withheld on the live board, which is
    # the user-visible harm the escalation issue exists to announce. It is a
    # separate, larger threshold than --max-age-minutes: dispatching is about
    # cadence, escalating is about the board being frozen.
    parser.add_argument('--evidence-window-minutes', type=int, default=480,
                        help='escalate a stop once the published snapshot is older than this (default: %(default)s)')
    parser.add_argument('--pages-url', default=None)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--now', default=None, help='Override "now" (tests only)')
    args = parser.parse_args()
    if not args.repo:
        print('GITHUB_REPOSITORY is required', file=sys.stderr)
        return 2
    now = utc(args.now) if args.now else datetime.datetime.now(datetime.timezone.utc)
    problems = []
    runs = []
    try:
        listing = api('/repos/%s/actions/workflows/%s/runs?branch=main&per_page=25'
                      % (args.repo, WORKFLOW), args.token)
        runs = listing.get('workflow_runs') or []
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as exc:
        problems.append('run history unreadable: %s' % str(exc)[:200])
    owner, _, name = args.repo.partition('/')
    base = (args.pages_url or ('https://%s.github.io/%s/' % (owner, name))).rstrip('/') + '/'
    receipt = None
    try:
        receipt = http_json(base + 'build-info.json?watchdog=' + now.strftime('%Y%m%d%H%M'))
    except Exception as exc:
        problems.append('live build receipt unreadable: %s' % str(exc)[:200])
    action, detail = evaluate(runs, receipt, now, args.max_age_minutes, args.cooldown_minutes,
                              args.budget, problems)
    streak = consecutive_failures(runs)
    snapshot_age = age_minutes((receipt or {}).get('snapshot_generated_at'), now)
    outside_window = snapshot_age is not None and snapshot_age > args.evidence_window_minutes
    report = {'checked_at': now.isoformat(timespec='seconds'), 'action': action, 'decision': detail,
              'consecutive_failures': streak,
              'pages_url': base, 'max_age_minutes': args.max_age_minutes,
              'evidence_window_minutes': args.evidence_window_minutes,
              'published_snapshot_age_minutes': snapshot_age,
              'published_snapshot_outside_evidence_window': outside_window,
              'published_snapshot_generated_at': (receipt or {}).get('snapshot_generated_at'),
              'published_revision': (receipt or {}).get('revision'),
              'published_rows': (receipt or {}).get('rows'),
              'runs_considered': [{'event': r.get('event'), 'status': r.get('status'),
                                   'conclusion': r.get('conclusion'), 'created_at': r.get('created_at'),
                                   'updated_at': r.get('updated_at'), 'head_sha': (r.get('head_sha') or '')[:8]}
                                  for r in runs[:6]],
              'problems': problems, 'dry_run': args.dry_run}
    alert_required = should_escalate(action, streak, outside_window)
    report['alert_required'] = alert_required
    alert_failed = False
    if alert_required and not args.dry_run and args.token:
        newest_failed = next((r.get('id') for r in runs if r.get('conclusion') == 'failure'), None)
        try:
            report['escalation'] = sync_escalation(
                args.token, args.repo, ESCALATION_TITLE,
                escalation_body(detail, runs, receipt, base, streak,
                                steps=failing_steps(args.token, args.repo, newest_failed),
                                snapshot_age=snapshot_age,
                                evidence_window_minutes=args.evidence_window_minutes))
        except Exception as exc:  # never let the alert path break the tick
            alert_failed = True
            report['escalation'] = 'failed: %s' % str(exc)[:200]
            # Measured 2026-10-24: this was the whole alert. A required
            # escalation that did not land was recorded only inside the run log
            # and the step summary, and the tick still exited 0, so five
            # consecutive failed publish runs and a 1066-minute-old snapshot
            # produced a green watchdog and no notification anywhere. The alert
            # is now a workflow error annotation and a red tick, because a
            # silent alert is not an alert.
            print('::error title=Publish gate red and the alert failed::'
                  'The published snapshot is %.0f min old (evidence window %d min) and %d consecutive '
                  'pages.yml runs have failed, but the escalation issue could not be filed: %s'
                  % (snapshot_age if snapshot_age is not None else -1, args.evidence_window_minutes,
                     streak, str(exc)[:200]))
    if action == 'ok' and not outside_window and not args.dry_run and args.token:
        # Recovery closes its own alert, so an open escalation issue always means
        # a board that is genuinely frozen right now.
        try:
            closed = close_escalation(args.token, args.repo, ESCALATION_TITLE,
                                      (receipt or {}).get('snapshot_generated_at'))
            if closed:
                report['escalation'] = closed
        except Exception as exc:
            report['escalation_close'] = 'failed: %s' % str(exc)[:200]
    if action == 'dispatch' and not args.dry_run and args.token:
        try:
            api('/repos/%s/actions/workflows/%s/dispatches' % (args.repo, WORKFLOW), args.token,
                method='POST', payload={'ref': 'main'})
            report['dispatched'] = True
        except Exception as exc:
            report['dispatched'] = False
            report['dispatch_error'] = str(exc)[:250]
    print(json.dumps(report, indent=1, sort_keys=True))
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as handle:
            handle.write('## CS2 refresh watchdog\n\n'
                         '- decision: **%s**\n- %s\n- published snapshot: `%s` (revision `%s`, %s rows)\n'
                         % (action, detail, report['published_snapshot_generated_at'],
                            (report['published_revision'] or '')[:8], report['published_rows']))
            if streak >= 2:
                handle.write('- warning: **%d** consecutive failed `pages.yml` runs on `main`\n' % streak)
            if outside_window:
                handle.write('- **the published snapshot is %.0f min old, outside its %d-min evidence window: '
                             'every open pick is withheld on the live site**\n'
                             % (snapshot_age, args.evidence_window_minutes))
            if alert_required:
                handle.write('- escalation required: yes (%s)\n'
                             % (report.get('escalation') or 'not attempted: no token or --dry-run'))
            if report.get('escalation'):
                handle.write('- escalation issue: %s\n' % report['escalation'])
            for problem in problems:
                handle.write('- source problem: %s\n' % problem)
    if problems and action == 'stop':
        return 1
    if alert_failed:
        # The board is frozen and the alert that was supposed to say so did not
        # land. A green tick here is what made the 2026-10-24 outage invisible.
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
