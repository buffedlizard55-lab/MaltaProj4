"""Cadence watchdog for the CS2 pick desk (no publication, no data writes).

Why this exists: on 15-16 October 2026 GitHub delivered the workflow's
``schedule`` events 3-5 hours late and then skipped the 23:17, 00:17 and 02:17
slots entirely (``gh api repos/.../actions/runs?event=schedule`` shows the last
scheduled run at 21:22:25Z, which also failed). A cron-only refresh cannot meet
the requested "every 4-8 hours" promise, because evidence expires eight hours
after it was observed.

This script turns the promise into a measurable rule and runs from a cheap
workflow: it reads the *published* snapshot age straight from the live site's
build receipt and the workflow run history through GitHub's API, and dispatches
the existing, fully verified publication workflow only when the published data
is older than the allowed window. It never edits data, never publishes, never
bypasses a check, and stops itself if it would loop.

Read-only on the site; write permission is used for exactly one call:
``POST /repos/{repo}/actions/workflows/pages.yml/dispatches``.
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


def evaluate(runs, receipt, now, max_age_minutes, cooldown_minutes, budget, failures):
    """Pure decision function - unit tested. Returns (action, detail)."""
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
        return 'ok', 'published snapshot is %.0f min old (limit %d min); no action' % \
            (snapshot_age, max_age_minutes)
    reason = ('published snapshot is %.0f min old, over the %d-min limit; the scheduled run was late or skipped '
              '(last completed run %s). Dispatching the same verified workflow once.'
              % (snapshot_age, max_age_minutes,
                 next((r.get('updated_at') for r in runs if r.get('conclusion') == 'success'), 'unknown')))
    return 'dispatch', reason


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY'))
    parser.add_argument('--token', default=os.environ.get('ACTIONS_TOKEN'))
    parser.add_argument('--max-age-minutes', type=int, default=150)
    parser.add_argument('--cooldown-minutes', type=int, default=45)
    parser.add_argument('--budget', type=int, default=10)
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
    report = {'checked_at': now.isoformat(timespec='seconds'), 'action': action, 'decision': detail,
              'pages_url': base, 'max_age_minutes': args.max_age_minutes,
              'published_snapshot_generated_at': (receipt or {}).get('snapshot_generated_at'),
              'published_revision': (receipt or {}).get('revision'),
              'published_rows': (receipt or {}).get('rows'),
              'runs_considered': [{'event': r.get('event'), 'status': r.get('status'),
                                   'conclusion': r.get('conclusion'), 'created_at': r.get('created_at'),
                                   'updated_at': r.get('updated_at'), 'head_sha': (r.get('head_sha') or '')[:8]}
                                  for r in runs[:6]],
              'problems': problems, 'dry_run': args.dry_run}
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
            for problem in problems:
                handle.write('- source problem: %s\n' % problem)
    if problems and action == 'stop':
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
