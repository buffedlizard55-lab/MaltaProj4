#!/usr/bin/env python3
"""Record the live publication state of the GitHub Pages site, with the API as source.

Why this exists (measured 2026-10-21, session 93fafca6)
-------------------------------------------------------
This repository has **two** publishers writing to one URL:

1. ``.github/workflows/pages.yml`` deploys a verified artifact with
   ``actions/deploy-pages`` and then proves the served bytes with
   ``scripts/verify_live.py``;
2. GitHub's own legacy Pages builder publishes the **committed root** of
   ``main`` because ``GET /repos/{owner}/{repo}/pages`` reports
   ``"build_type": "legacy"`` with ``"source": {"branch": "main", "path": "/"}``.

Every push to ``main`` therefore fires both, and whichever finishes last is what
a phone visitor reads. The committed root is a fallback staged from the
2026-10-18 bootstrap snapshot, so when the legacy builder wins, the live board
regresses by days and every pick on it is expired.

Prior sessions recorded this from a branch and recommended the owner-level fix
(``research/session-84295759/REPORT.md`` §7, session a980a709's addendum, and
PR #57's note). This module turns the recommendation into a reproducible
measurement instead of a repeated assertion: it reads the Pages configuration,
the last Pages builds, the publication run history and the live receipt, then
derives *which publisher is serving right now*. With ``--attempt-fix`` it also
re-attempts ``PUT /repos/{owner}/{repo}/pages {"build_type": "workflow"}`` and
records the exact HTTP verdict and the permissions GitHub says are required, so
the 403 is evidence rather than folklore.

Read-only by default. Stdlib only. Nothing here writes to a shared repository
path; the caller chooses the output file.
"""
import argparse
import datetime
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = 'https://api.github.com'
DEFAULT_REPO = 'buffedlizard55-lab/MaltaProj4'
LIVE_RECEIPT = 'https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json'
STALE_HOURS = 8.0
UA = {'User-Agent': 'cs2-scout-publication-state/1.0 (session 93fafca6)',
      'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}


def utc(value):
    if not value:
        return None
    try:
        text = str(value).strip()
        return datetime.datetime.fromisoformat(text.replace('Z', '+00:00')).astimezone(datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def age_hours(value, now):
    stamp = utc(value)
    if not stamp or not now:
        return None
    return round((now - stamp).total_seconds() / 3600.0, 2)


def request(url, token=None, method='GET', payload=None, timeout=30):
    """One API/site call. Returns a dict that always carries the HTTP verdict."""
    headers = dict(UA)
    if token:
        headers['Authorization'] = 'Bearer ' + token
    body = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        body = json.dumps(payload).encode()
    record = {'url': url, 'method': method, 'status': None, 'error': None,
              'accepted_permissions': None, 'request_id': None, 'payload': payload}
    try:
        opener = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(opener, timeout=timeout) as response:
            raw = response.read().decode('utf-8', 'replace')
            record['status'] = response.status
            record['accepted_permissions'] = response.headers.get('X-Accepted-Github-Permissions')
            record['request_id'] = response.headers.get('X-Github-Request-Id')
            try:
                record['body'] = json.loads(raw or 'null')
            except ValueError:
                record['body'] = raw[:4000]
    except urllib.error.HTTPError as exc:
        detail = ''
        try:
            detail = exc.read().decode('utf-8', 'replace')[:2000]
        except Exception:  # pragma: no cover - defensive
            pass
        record.update(status=exc.code, error='HTTP %s' % exc.code,
                      accepted_permissions=exc.headers.get('X-Accepted-Github-Permissions') if exc.headers else None,
                      request_id=exc.headers.get('X-Github-Request-Id') if exc.headers else None,
                      body=detail)
    except Exception as exc:
        record.update(error='%s: %s' % (type(exc).__name__, exc))
    return record


def classify(live_revision, committed_revision, main_head):
    """Name the publisher that is serving the live site. Pure and unit-tested."""
    if not live_revision:
        return 'unknown'
    if committed_revision and live_revision == committed_revision and live_revision != main_head:
        return 'committed-root-fallback'
    if main_head and live_revision == main_head:
        return 'artifact-current-main'
    return 'artifact-older-commit'


def summarize(pages, builds, runs, live_receipt, committed_receipt, main_head, now,
              fix_attempt=None, pages_after=None):
    """Derive the publication state. Pure: no I/O, so it is directly testable.

    ``pages_after`` is the configuration re-read after an owner-level fix attempt
    succeeded; when present it is the forward-looking truth, while ``pages`` stays
    in the record as the configuration that was actually serving the site.
    """
    pages_body = (pages or {}).get('body') if isinstance(pages, dict) else None
    pages_body = pages_body if isinstance(pages_body, dict) else {}
    after_body = (pages_after or {}).get('body') if isinstance(pages_after, dict) else None
    after_body = after_body if isinstance(after_body, dict) else None
    effective = after_body or pages_body
    live_body = (live_receipt or {}).get('body') if isinstance(live_receipt, dict) else None
    live_body = live_body if isinstance(live_body, dict) else {}
    committed_body = committed_receipt if isinstance(committed_receipt, dict) else {}
    build_list = (builds or {}).get('body') if isinstance(builds, dict) else None
    build_list = build_list if isinstance(build_list, list) else []
    run_list = (runs or {}).get('body') if isinstance(runs, dict) else None
    run_list = (run_list or {}).get('workflow_runs') if isinstance(run_list, dict) else None
    run_list = run_list if isinstance(run_list, list) else []

    live_revision = live_body.get('revision')
    serving = classify(live_revision, committed_body.get('revision'), main_head)
    snapshot_age = age_hours(live_body.get('snapshot_generated_at'), now)
    successful = [r for r in run_list if r.get('conclusion') == 'success']
    legacy_builds = [{'created_at': b.get('created_at'), 'status': b.get('status'),
                      'commit': b.get('commit')} for b in build_list[:6]]
    newest_build = legacy_builds[0] if legacy_builds else None
    return {
        'read_at': now.isoformat().replace('+00:00', 'Z') if now else None,
        'pages_configuration': {
            'status': (pages or {}).get('status'),
            'error': (pages or {}).get('error'),
            'build_type': pages_body.get('build_type'),
            'source_branch': (pages_body.get('source') or {}).get('branch'),
            'source_path': (pages_body.get('source') or {}).get('path'),
            'site_status': pages_body.get('status'),
            'html_url': pages_body.get('html_url'),
        },
        'live_receipt': {
            'status': (live_receipt or {}).get('status'),
            'revision': live_revision,
            'built_at': live_body.get('built_at'),
            'snapshot_generated_at': live_body.get('snapshot_generated_at'),
            'rows': live_body.get('rows'),
            'snapshot_age_hours': snapshot_age,
        },
        'committed_root_receipt': {
            'revision': committed_body.get('revision'),
            'built_at': committed_body.get('built_at'),
            'snapshot_generated_at': committed_body.get('snapshot_generated_at'),
            'rows': committed_body.get('rows'),
        },
        'main_head': main_head,
        'serving': serving,
        'legacy_overwrite_detected': serving == 'committed-root-fallback',
        'outside_evidence_window': None if snapshot_age is None else snapshot_age > STALE_HOURS,
        # Since pages.yml began re-staging the committed root from the verified
        # build (step "Keep the legacy main:/ root fallback on the verified
        # build", 2026-10-21), the legacy publisher serving the root is no
        # longer by itself a stale-board event: the root can carry a fresh
        # snapshot. Whether the served board is actually outside its evidence
        # window is what makes it one, so the two are recorded separately and
        # the wording follows the evidence rather than the classification.
        'legacy_overwrote_with_a_stale_board': (serving == 'committed-root-fallback'
                                                and snapshot_age is not None
                                                and snapshot_age > STALE_HOURS),
        'pages_builds': legacy_builds,
        'newest_pages_build': newest_build,
        'newest_pages_build_matches_live_revision': bool(
            newest_build and live_revision and str(newest_build.get('commit') or '').startswith(live_revision[:12])),
        'publication_runs': [{'id': r.get('id'), 'event': r.get('event'), 'status': r.get('status'),
                              'conclusion': r.get('conclusion'), 'started': r.get('run_started_at'),
                              'url': r.get('html_url')} for r in run_list[:8]],
        'last_successful_publication': successful[0].get('html_url') if successful else None,
        'pages_configuration_after_fix': None if after_body is None else {
            'status': (pages_after or {}).get('status'),
            'build_type': after_body.get('build_type'),
            'source_branch': (after_body.get('source') or {}).get('branch') if after_body.get('source') else None,
            'source_path': (after_body.get('source') or {}).get('path') if after_body.get('source') else None,
            'site_status': after_body.get('status'),
        },
        # Forward-looking: the race is possible whenever the *effective*
        # configuration still builds from the branch source.
        'dual_publisher_race_possible': effective.get('build_type') == 'legacy',
        'owner_fix_attempt': fix_attempt,
    }


def legacy_clause(state):
    """Wording for the serving-publisher row, following the evidence.

    Naming the legacy publisher is a classification; calling it a stale-board
    event is a claim, and since ``pages.yml`` began re-staging the committed
    root from the verified build the two can disagree. Each branch says only
    what the timestamps support, and says so when they cannot be read.
    """
    if not state.get('legacy_overwrite_detected'):
        return ''
    outside = state.get('outside_evidence_window')
    if outside is True:
        return (' — **the legacy root fallback is serving and the board it carries is outside '
                'its 8-hour evidence window**')
    if outside is False:
        return (' — the legacy publisher is serving the committed root, which is itself a fresh '
                'verified build re-staged by `pages.yml`, so the served board is inside its '
                'evidence window')
    return (' — the legacy publisher is serving the committed root; the served snapshot\'s age '
            'could not be read, so whether the board is fresh or expired is unknown and is not '
            'assumed here')


def to_markdown(state):
    """A short, link-carrying record of what is serving the site right now."""
    pages = state['pages_configuration']
    live = state['live_receipt']
    root = state['committed_root_receipt']
    lines = [
        '# Publication state of the live site',
        '',
        'Read at `%s` from the GitHub API and the live build receipt.' % state['read_at'],
        '',
        '| Question | Answer | Source |',
        '| --- | --- | --- |',
        '| How is Pages configured? | `build_type: %s`, source `%s:%s`, site status `%s` | [GET /repos/%s/pages](%s/repos/%s/pages) |'
        % (pages['build_type'], pages['source_branch'], pages['source_path'], pages['site_status'],
           DEFAULT_REPO, API, DEFAULT_REPO),
        '| Which publisher is serving now? | `%s`%s | live [build-info.json](%s) revision `%s` |'
        % (state['serving'], legacy_clause(state), LIVE_RECEIPT, live['revision']),
        ('| What does the live receipt say? | built `%s`, snapshot `%s`, %s rows, %.2f h old '
         '| [live build-info.json](%s) |'
         % (live['built_at'], live['snapshot_generated_at'], live['rows'],
            live['snapshot_age_hours'], LIVE_RECEIPT))
        if live['snapshot_age_hours'] is not None else
        ('| What does the live receipt say? | unreadable (HTTP `%s`) | [live build-info.json](%s) |'
         % (live['status'], LIVE_RECEIPT)),
        '| What does the committed root fallback say? | revision `%s`, built `%s`, %s rows | [build-info.json on main](https://github.com/%s/blob/main/build-info.json) |'
        % (root['revision'], root['built_at'], root['rows'], DEFAULT_REPO),
        '| Is the served board inside its 8-hour evidence window? | %s | derived from the two timestamps above |'
        % ('**no**' if state['outside_evidence_window'] else 'yes'
           if state['outside_evidence_window'] is False else 'unknown'),
        '| Can the legacy builder still overwrite it? | %s | Pages `build_type` above |'
        % ('**yes**' if state['dual_publisher_race_possible'] else 'no'),
        *(['| Configuration after the fix attempt | `build_type: %s`, source `%s:%s` | [GET /repos/%s/pages](%s/repos/%s/pages) |'
           % (state['pages_configuration_after_fix']['build_type'],
              state['pages_configuration_after_fix']['source_branch'],
              state['pages_configuration_after_fix']['source_path'], DEFAULT_REPO, API, DEFAULT_REPO)]
          if state.get('pages_configuration_after_fix') else []),
        '',
        '## Last Pages builds (both publishers write here)',
        '',
        '| Created (UTC) | Status | Commit |',
        '| --- | --- | --- |',
    ]
    for build in state['pages_builds']:
        lines.append('| %s | %s | `%s` |' % (build['created_at'], build['status'], build['commit']))
    lines += ['', '## Last publication workflow runs', '',
              '| Started (UTC) | Event | Conclusion | Run |', '| --- | --- | --- | --- |']
    for run in state['publication_runs']:
        lines.append('| %s | %s | %s | [%s](%s) |' % (run['started'], run['event'],
                                                      run['conclusion'], run['id'], run['url']))
    attempt = state.get('owner_fix_attempt')
    if attempt:
        lines += ['', '## Owner-level fix attempt',
                  '',
                  '`%s %s` with payload `%s`' % (attempt.get('method'), attempt.get('url'),
                                                  json.dumps(attempt.get('payload'))),
                  '',
                  '* HTTP status: **%s** (%s)' % (attempt.get('status'), attempt.get('error') or 'no error'),
                  '* GitHub says these permissions are accepted: `%s`' % attempt.get('accepted_permissions'),
                  '* Request id: `%s`' % attempt.get('request_id'),
                  '* Response: `%s`' % str(attempt.get('body'))[:400],
                  '',
                  'The setting must be changed by someone holding `pages: write` (Settings → Pages → '
                  'Build and deployment → Source → GitHub Actions). Until then both publishers keep '
                  'writing to the same URL.']
    lines.append('')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--repo', default=DEFAULT_REPO)
    parser.add_argument('--token', default=None, help='GitHub token for the API reads')
    parser.add_argument('--main-head', default=None, help='current main HEAD sha, for publisher identity')
    parser.add_argument('--committed-receipt', default='build-info.json')
    parser.add_argument('--attempt-fix', action='store_true',
                        help='also attempt PUT /repos/{repo}/pages {"build_type":"workflow"} and record the verdict')
    parser.add_argument('--now', default=None)
    parser.add_argument('--output', default=None, help='write the JSON receipt here')
    parser.add_argument('--markdown', default=None, help='write the markdown report here')
    args = parser.parse_args(argv)

    now = utc(args.now) or datetime.datetime.now(datetime.timezone.utc)
    committed = None
    if args.committed_receipt and Path(args.committed_receipt).exists():
        try:
            committed = json.loads(Path(args.committed_receipt).read_text())
        except ValueError:
            committed = None

    calls = {
        'pages': request('%s/repos/%s/pages' % (API, args.repo), args.token),
        'builds': request('%s/repos/%s/pages/builds?per_page=6' % (API, args.repo), args.token),
        'runs': request('%s/repos/%s/actions/workflows/pages.yml/runs?per_page=8' % (API, args.repo), args.token),
        'live_receipt': request(LIVE_RECEIPT + '?_pubstate=%s' % now.strftime('%Y%m%dT%H%M%SZ')),
    }
    fix = after = None
    if args.attempt_fix:
        fix = request('%s/repos/%s/pages' % (API, args.repo), args.token, method='PUT',
                      payload={'build_type': 'workflow'})
        if fix.get('status') in (200, 204):
            # Prove the outcome rather than trusting the status code: re-read the
            # configuration, and re-read the live receipt once the mode is known.
            after = request('%s/repos/%s/pages' % (API, args.repo), args.token)
            calls['pages_after_fix'] = after
            calls['live_receipt_after_fix'] = request(
                LIVE_RECEIPT + '?_pubstate=after%s' % now.strftime('%Y%m%dT%H%M%SZ'))
    state = summarize(calls['pages'], calls['builds'], calls['runs'], calls['live_receipt'],
                      committed, args.main_head, now, fix_attempt=fix, pages_after=after)
    markdown = to_markdown(state)
    payload = {'state': state, 'raw_calls': calls}
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n')
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(markdown)
    print(markdown)
    return 0


if __name__ == '__main__':
    sys.exit(main())
