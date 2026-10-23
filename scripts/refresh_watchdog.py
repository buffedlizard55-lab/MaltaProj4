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
nothing anywhere said why. The issue is updated in place (never duplicated) and
is not re-created once a human closes it until the gate fails again.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
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


def should_escalate(action, streak):
    """Pure rule: raise an issue only when the gate has stopped the chain.

    ``evaluate`` returns ``stop`` for a red gate (3+ consecutive failures on one
    commit), for a spent budget, and for an unknown state. Only the red-gate case
    is actionable by a human, and only that case carries the streak.
    """
    return action == 'stop' and streak >= 3


def escalation_body(detail, runs, receipt, pages_url, streak):
    """The issue body: what stopped, which runs, and what to fix."""
    failing = [r for r in runs if r.get('conclusion') == 'failure'][:3]
    lines = [ESCALATION_MARKER,
             'The refresh watchdog stopped dispatching because `pages.yml` keeps failing on the same commit, '
             'so the published snapshot cannot leave its evidence window and **every pick is withheld** on the live site.',
             '',
             '- decision: %s' % detail,
             '- consecutive failed `pages.yml` runs on `main`: **%d**' % streak,
             '- published snapshot: `%s`' % ((receipt or {}).get('snapshot_generated_at') or 'unreadable'),
             '- live site: %s' % pages_url,
             '',
             'Recent failing runs:']
    for r in failing:
        lines.append('- %s (%s, commit `%s`)' % (r.get('html_url'), r.get('created_at'), (r.get('head_sha') or '')[:8]))
    if not failing:
        lines.append('- none recorded in the last 25 runs')
    lines += ['', 'Fix the failing gate and close this issue; the watchdog opens a new one only if it recurs.']
    return '\n'.join(lines)


def find_open_issue(token, repo, title):
    """The open escalation issue for this repository, or None."""
    query = urllib.parse.quote('repo:%s is:issue is:open in:title "%s"' % (repo, title))
    data = api('/search/issues?q=' + query, token) or {}
    items = data.get('items') or []
    return items[0] if items else None


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
    report = {'checked_at': now.isoformat(timespec='seconds'), 'action': action, 'decision': detail,
              'consecutive_failures': streak,
              'pages_url': base, 'max_age_minutes': args.max_age_minutes,
              'published_snapshot_generated_at': (receipt or {}).get('snapshot_generated_at'),
              'published_revision': (receipt or {}).get('revision'),
              'published_rows': (receipt or {}).get('rows'),
              'runs_considered': [{'event': r.get('event'), 'status': r.get('status'),
                                   'conclusion': r.get('conclusion'), 'created_at': r.get('created_at'),
                                   'updated_at': r.get('updated_at'), 'head_sha': (r.get('head_sha') or '')[:8]}
                                  for r in runs[:6]],
              'problems': problems, 'dry_run': args.dry_run}
    if should_escalate(action, streak) and not args.dry_run and args.token:
        try:
            report['escalation'] = sync_escalation(
                args.token, args.repo, ESCALATION_TITLE,
                escalation_body(detail, runs, receipt, base, streak))
        except Exception as exc:  # never let the alert path break the tick
            report['escalation'] = 'failed: %s' % str(exc)[:200]
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
            if report.get('escalation'):
                handle.write('- escalation issue: %s\n' % report['escalation'])
            for problem in problems:
                handle.write('- source problem: %s\n' % problem)
    if problems and action == 'stop':
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
