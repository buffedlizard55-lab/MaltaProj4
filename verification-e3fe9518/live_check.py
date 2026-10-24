"""Read-only runner verification of public Pages and operator quote provenance.

This does not harvest new picks or write to any branch. Changed live prices are
reported as drift, never used to rewrite an archived observation. Bookmaker
links reported by an aggregator are never counted as operator verification.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import audit_e3fe9518 as audit
from scripts.verify_live import verify

SITE = 'https://buffedlizard55-lab.github.io/MaltaProj4/'
OUT = ROOT / 'runtime/verification-e3fe9518'


def fetch(url):
    request = Request(url, headers={'User-Agent': 'CS2-Scout-source-review/1.0', 'Cache-Control': 'no-cache'})
    try:
        with urlopen(request, timeout=25) as response:
            content = response.read(8_000_001)
            if len(content) > 8_000_000:
                raise ValueError('Response exceeds 8 MB verification limit')
            return content, {'url': url, 'http_status': response.status,
                             'observed_at': datetime.now(timezone.utc).isoformat(),
                             'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
    except HTTPError as exc:
        return None, {'url': url, 'http_status': exc.code, 'error': 'HTTP access failure; not evidence that no odds exist'}
    except (URLError, ValueError, TimeoutError, OSError) as exc:
        return None, {'url': url, 'error': type(exc).__name__}


def array(value):
    return json.loads(value) if isinstance(value, str) else value


def compare_operator_record(quote, payload):
    """Compare, do not price. Only an exact current operator record confirms inputs."""
    if not isinstance(payload, dict) or str(payload.get('id')) != str(quote.get('id')):
        return {'identity_matches': False, 'snapshot_inputs_confirmed_now': False,
                'limitation': 'Live market ID or response schema differs from the captured operator record'}
    raw = quote.get('raw') or {}
    try:
        identity = (array(payload.get('outcomes')) == array(raw.get('outcomes'))
                    and audit.moment(payload.get('gameStartTime') or payload.get('eventStartTime'))
                    == audit.moment(raw.get('gameStartTime') or raw.get('eventStartTime'))
                    and payload.get('sportsMarketType') == raw.get('sportsMarketType') == 'moneyline')
        same_prices = (array(payload.get('outcomePrices')) == array(raw.get('outcomePrices')))
    except (ValueError, TypeError):
        identity, same_prices = False, False
    active = (payload.get('active') is True and payload.get('closed') is False
              and payload.get('acceptingOrders') is True)
    return {'identity_matches': identity, 'captured_prices_still_equal': same_prices,
            'market_currently_accepting_orders': active,
            'snapshot_inputs_confirmed_now': identity and same_prices and active,
            'live_updated_at': payload.get('updatedAt'),
            'limitation': ('Live state checked independently; this does not renew the snapshot or establish forecast accuracy.'
                           if identity and same_prices and active else
                           'Live state or prices differ / cannot be confirmed. Archived captured values are not re-labelled as current.')}


def check_quote(item):
    match, quote = item
    raw, receipt = fetch(quote['api_url'])
    comparison = {'snapshot_inputs_confirmed_now': False}
    if raw:
        try:
            comparison = compare_operator_record(quote, json.loads(raw))
        except (ValueError, UnicodeError):
            comparison['limitation'] = 'Operator response was not readable JSON'
    return {'fixture_id': match['id'], 'fixture_url': match['source_url'],
            'receipt': receipt, 'comparison': comparison}


def expectation(reference, root_bytes, published_bytes=None):
    """An unmerged branch may audit production, never claim its own release live."""
    if reference and reference != 'refs/heads/main':
        if published_bytes is None:
            raise ValueError('Cannot establish the current production manifest')
        return published_bytes, 'observed_production_not_this_unmerged_branch'
    return root_bytes, 'this_merged_main_build_or_a_coherent_newer_release'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = os.environ.get('GITHUB_RUN_ID') or str(int(time.time()))
    reference = os.environ.get('GITHUB_REF')
    published_bytes = None
    if reference and reference != 'refs/heads/main':
        published_bytes, _ = fetch(SITE + 'build-info.json?verification=' + stamp)
    expected_bytes, expectation_mode = expectation(
        reference, (ROOT / 'build-info.json').read_bytes(), published_bytes)
    expected = json.loads(expected_bytes)
    receipt = verify(SITE, hashlib.sha256(expected_bytes).hexdigest(), expected['built_at'],
                     stamp, deadline_seconds=360, interval_seconds=15)
    receipt['expectation_mode'] = expectation_mode
    (OUT / 'live-build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    raw, snapshot_receipt = fetch(SITE + 'data/latest.json?verification=' + stamp)
    if raw is None:
        (OUT / 'snapshot-fetch.json').write_text(json.dumps(snapshot_receipt, indent=2) + '\n')
        return 1
    (OUT / 'live-snapshot.json').write_bytes(raw)
    snapshot = json.loads(raw)
    manifest_raw, manifest_receipt = fetch(SITE + 'build-info.json?verification=' + stamp)
    live_manifest = json.loads(manifest_raw) if manifest_raw else {}
    manifest_snapshot_hash_matches = (live_manifest.get('files', {}).get('data/latest.json')
                                      == hashlib.sha256(raw).hexdigest())
    documents = audit.archived_standings()
    document_receipts = []
    urls = sorted({q['api_url'] for m in snapshot['matches'] for q in m.get('evidence', [])
                   if audit.source_kind(q) == 'official_input_model'})
    for url in urls:
        content, source_receipt = fetch(url)
        document_receipts.append(source_receipt)
        if content:
            documents[url] = content
            (OUT / ('valve-' + hashlib.sha256(content).hexdigest()[:16] + '.md')).write_bytes(content)
    (OUT / 'primary-document-rechecks.json').write_text(json.dumps(document_receipts, indent=2) + '\n')
    now = datetime.now(timezone.utc)
    result = audit.inspect(snapshot, now.isoformat(), standings_documents=documents)
    if not manifest_snapshot_hash_matches:
        result['errors'].append('Public snapshot bytes differ from the manifest read alongside them; deployment may be racing')
    result['snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
    (OUT / 'live-source-audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    (OUT / 'live-source-audit.md').write_text(audit.markdown(result))
    candidates = [(m, q) for m in snapshot['matches'] if m.get('state') == 'open'
                  for q in m.get('evidence', []) if q.get('provider') == 'Polymarket'
                  and audit.source_kind(q) == 'operator_market']
    with ThreadPoolExecutor(max_workers=3) as pool:
        quotes = list(pool.map(check_quote, candidates))
    (OUT / 'operator-input-rechecks.json').write_text(json.dumps(quotes, indent=2) + '\n')
    age = (now - audit.moment(snapshot['fixtures_observed_at'])).total_seconds()
    summary = {'checked_at': now.isoformat(), 'site': SITE,
               'snapshot_generated_at': snapshot['generated_at'],
               'snapshot_sha256': result['snapshot_sha256'],
               'snapshot_age_seconds': age, 'inside_eight_hour_window': -300 <= age < 28800,
               'build_bytes_verified': receipt['verified'],
               'snapshot_matches_adjacent_manifest': manifest_snapshot_hash_matches,
               'official_model_rows_file_crosschecked': sum(
                   r['official_standings_input_crosscheck'] is True for r in result['rows']),
               'rows': len(result['rows']), 'categories': result['counts'],
               'actionable_at_check': result['actionable_at_audit_clock'],
               'operator_quotes_rechecked': len(quotes),
               'captured_operator_inputs_still_confirmed': sum(
                   r['comparison']['snapshot_inputs_confirmed_now'] for r in quotes),
               'primary_price_confirmation_for_third_party_listings': None,
               'errors': result['errors']}
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as handle:
            handle.write('## Independent live source review\n\n```json\n' + json.dumps(summary, indent=2)
                         + '\n```\n\nAn aggregator link is not operator price verification. '
                         'Changed live prices are not used to rewrite captured picks.\n')
    return int(not receipt['verified'] or not summary['inside_eight_hour_window'] or bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
