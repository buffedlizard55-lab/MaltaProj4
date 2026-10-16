"""Decide whether a scheduled publication run has anything to do.

Why this exists (measured, not assumed): this repository's ``schedule`` events are
delivered late and sometimes not at all. On 15-16 October 2026 ``pages.yml`` saw
exactly three scheduled runs (16:59:51Z success, 21:22:25Z failure, 04:33:39Z
failure) and none at all for the 05:17/06:17/07:17Z slots, while the previous
six-hour cron was delivered 3h05m and 4h42m late (see
``research/refresh-ab18fe2a/DIAGNOSIS.md``). A sparse cron therefore cannot meet
the "every 4-8 hours" refresh promise on its own, and a dense cron would spend a
full build, test and deploy cycle on every slot.

This gate makes a dense schedule affordable: it runs first, before any
dependency install, and answers one question - does the live site already carry
this exact revision with a snapshot inside the freshness budget? If yes, the
expensive steps and the deploy are skipped and the workflow exits in seconds, so
many cheap slots can be scheduled. If the answer is no, unknown or unreadable,
the step fails open and the full verified publication runs.

Rules (pure function, unit tested in ``tests/test_publish_gate_ef0969b9.py``):

* ``pull_request`` and any other event that must verify code always run in full.
* A push to main (or a manual dispatch) always runs in full: it is the only way
  new code and new data reach the site.
* A scheduled run skips only when the live receipt is readable, its ``revision``
  equals the commit being deployed, and its snapshot is inside the budget.
* Anything else - missing receipt, unparsable JSON, old revision, stale or
  unknown snapshot age - publishes.

The gate never weakens verification: when it skips, nothing is built and nothing
is deployed, so there is nothing to verify. The published bytes stay exactly
those of the last fully verified build.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MAX_AGE_MINUTES = 60
DEFAULT_URL = 'https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json'


def utc(value):
    return datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(datetime.timezone.utc)


def age_minutes(value, now):
    """Age of an ISO timestamp in minutes, or None when it cannot be read."""
    if not value:
        return None
    try:
        return (now - utc(value)).total_seconds() / 60.0
    except (ValueError, TypeError):
        return None


def decide(event_name, head_sha, receipt, fetch_error, now, max_age_minutes=DEFAULT_MAX_AGE_MINUTES):
    """Pure decision function. Returns (publish: bool, reason: str, detail: dict)."""
    if event_name != 'schedule':
        return True, 'event %r always publishes (push to main, manual dispatch or pull-request verification)' % event_name, {}
    if fetch_error:
        return True, 'the live build receipt could not be read (%s); publishing rather than assuming freshness' % fetch_error, {}
    if not isinstance(receipt, dict):
        return True, 'no usable live build receipt; publishing', {}
    live_revision = receipt.get('revision')
    snapshot_age = age_minutes(receipt.get('snapshot_generated_at'), now)
    build_age = age_minutes(receipt.get('built_at'), now)
    detail = {'live_revision': live_revision, 'head_sha': head_sha,
              'snapshot_age_minutes': None if snapshot_age is None else round(snapshot_age, 1),
              'build_age_minutes': None if build_age is None else round(build_age, 1),
              'rows': receipt.get('rows')}
    if not live_revision or not head_sha:
        return True, 'live revision or head commit is missing; publishing', detail
    if live_revision != head_sha:
        return True, ('the live site is on revision %s but this run deploys %s; publishing'
                      % (live_revision[:12], head_sha[:12])), detail
    effective_age = snapshot_age if snapshot_age is not None else build_age
    if effective_age is None:
        return True, 'the live receipt has neither a snapshot nor a build timestamp; publishing', detail
    if effective_age > max_age_minutes:
        return True, ('the live snapshot is %.0f min old (budget %d min); publishing'
                      % (effective_age, max_age_minutes)), detail
    return False, ('the live site already carries this revision (%s) with a %.0f-min-old snapshot (budget %d min); '
                   'skipping the build, the tests and the deploy so the dense schedule stays cheap'
                   % (head_sha[:12], effective_age, max_age_minutes)), detail


def fetch_receipt(url, timeout=25):
    """Read the published build receipt. Returns (receipt, error_string)."""
    request = urllib.request.Request(url, headers={'User-Agent': 'cs2-scout-publish-gate/1.0',
                                                  'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode('utf-8', 'replace')
        return json.loads(body), None
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as exc:
        return None, '%s: %s' % (type(exc).__name__, exc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event', default=os.environ.get('GITHUB_EVENT_NAME', 'schedule'))
    parser.add_argument('--sha', default=os.environ.get('GITHUB_SHA', ''))
    parser.add_argument('--url', default=DEFAULT_URL)
    parser.add_argument('--max-age-minutes', type=int, default=DEFAULT_MAX_AGE_MINUTES)
    parser.add_argument('--now', default=None, help='Override "now" (tests only)')
    parser.add_argument('--receipt', default=None, help='Read the receipt from a local file instead of the site')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    now = utc(args.now) if args.now else datetime.datetime.now(datetime.timezone.utc)
    if args.receipt:
        try:
            receipt = json.loads(open(args.receipt, encoding='utf-8').read())
            error = None
        except (OSError, ValueError) as exc:
            receipt, error = None, '%s: %s' % (type(exc).__name__, exc)
    else:
        receipt, error = fetch_receipt(args.url)
    publish, reason, detail = decide(args.event, args.sha, receipt, error, now, args.max_age_minutes)
    report = {'publish': publish, 'reason': reason, 'checked_at': now.isoformat(), 'event': args.event,
              'receipt_read': error is None and receipt is not None, 'receipt_error': error, **detail}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print('publish=%s' % ('true' if publish else 'false'))
        print(reason)
    destination = os.environ.get('GITHUB_OUTPUT')
    if destination:
        with open(destination, 'a', encoding='utf-8') as handle:
            handle.write('publish=%s\n' % ('true' if publish else 'false'))
            handle.write('reason=%s\n' % reason.replace('\n', ' '))
    return 0


if __name__ == '__main__':
    sys.exit(main())
