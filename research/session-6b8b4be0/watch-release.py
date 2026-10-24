"""Read-only watcher using GitHub's separately allocated GraphQL quota.

No deployment, dispatch, credential changes or rate-limit bypass. Stops after
20 minutes or when the merge's legacy Pages deployment completes.
"""
import json
import subprocess
import time
from pathlib import Path

QUERY = '''query { repository(owner:"buffedlizard55-lab",name:"MaltaProj4") {
 object(expression:"7e320778df976bda92a2ec06ac1ebdff43c82a9e") { ... on Commit {
 statusCheckRollup { contexts(first:40) { nodes { ... on CheckRun {
 name status conclusion detailsUrl } } } } } } } }'''
DEST = Path(__file__).with_name('release-status.json')
for attempt in range(40):
    result = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + QUERY], capture_output=True, text=True)
    if result.returncode:
        print(result.stderr, flush=True)
        raise SystemExit(result.returncode)
    data = json.loads(result.stdout)
    checks = data['data']['repository']['object']['statusCheckRollup']['contexts']['nodes']
    receipt = {'merge_commit': '7e320778df976bda92a2ec06ac1ebdff43c82a9e',
               'observed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'checks': checks,
               'scope': 'Official GitHub check results; not a direct public-byte read from this sandbox.'}
    DEST.write_text(json.dumps(receipt, indent=1) + '\n')
    print(receipt['observed_at'], json.dumps(checks), flush=True)
    pages = [c for c in checks if c.get('name') == 'deploy' and '/40113397250/' in c.get('detailsUrl', '')]
    if any(c.get('conclusion') == 'SUCCESS' for c in pages):
        print('Legacy Pages deployment for the exact merge succeeded.', flush=True)
        break
    if any(c.get('conclusion') in {'FAILURE', 'CANCELLED', 'TIMED_OUT'} for c in pages):
        raise SystemExit('Legacy Pages deployment did not succeed; review official receipt.')
    time.sleep(30)
else:
    raise SystemExit('Deployment not confirmed inside the observation window.')
