"""Every source link in the research data must be a real absolute URL.

The analysis and review-note files are written by hand and re-written by several
sessions, and a bulk text substitution once turned a source link into
``https://the official rules page`` - which rendered as a broken link on a page
whose whole purpose is carrying source links. ``scripts/validate.py`` only resolves
*internal* links, so an external-looking field that is not a URL slips through.
These assertions close that gap without touching any pipeline code.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = ('data/analysis.json', 'data/review-notes.json')
URL_KEYS = re.compile(r'^(url|source|.*_url|.*_source)$')
ABSOLUTE_URL = re.compile(r'^https?://[^\s]+\.[^\s]+$')


def strings(node, path=''):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from strings(value, f'{path}/{key}')
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from strings(value, f'{path}[{index}]')
    elif isinstance(node, str):
        yield path, node


class SourceUrlTest(unittest.TestCase):
    def test_every_url_field_is_an_absolute_url(self):
        offenders = []
        for name in FILES:
            data = json.loads((ROOT / name).read_text())
            for path, value in strings(data):
                if URL_KEYS.match(path.rsplit('/', 1)[-1]) and not ABSOLUTE_URL.match(value):
                    offenders.append(f'{name} {path} = {value[:80]!r}')
        self.assertEqual(offenders, [], 'Source links that are not absolute URLs:\n' + '\n'.join(offenders))

    def test_no_url_field_contains_whitespace_or_placeholder_text(self):
        offenders = []
        for name in FILES:
            data = json.loads((ROOT / name).read_text())
            for path, value in strings(data):
                if not URL_KEYS.match(path.rsplit('/', 1)[-1]):
                    continue
                if re.search(r'\s', value) or 'TODO' in value or value.count('://') != 1:
                    offenders.append(f'{name} {path} = {value[:80]!r}')
        self.assertEqual(offenders, [], 'Malformed source links:\n' + '\n'.join(offenders))

    def test_every_fact_bearing_entry_carries_at_least_one_source(self):
        """A claim, finding or fixture with no link is exactly what this project forbids."""
        analysis = json.loads((ROOT / 'data/analysis.json').read_text())
        missing = []
        for point in analysis['day_three']['points']:
            if not point.get('source'):
                missing.append('day_three point: ' + point.get('claim', '')[:60])
        for rule in analysis['strategy']['rules']:
            if not rule.get('verify'):
                missing.append('strategy rule: ' + rule.get('rule', '')[:60])
        for day in (analysis['day_one'], analysis['day_two']):
            for match in day['matches']:
                if not match.get('match_url') or not match.get('report_url'):
                    missing.append(f"{day['label']} {match.get('winner')} beat {match.get('loser')}")
        for fixture in analysis['day_three']['fixtures']:
            if not fixture.get('hltv_match'):
                missing.append('day_three fixture: ' + ' vs '.join(fixture.get('teams', [])))
        notes = json.loads((ROOT / 'data/review-notes.json').read_text())
        for note in notes:
            if not note.get('sources'):
                missing.append('review note: ' + note.get('id', '<no id>'))
            for source in note.get('sources', []):
                if not source.get('url') or not source.get('label'):
                    missing.append('review note source: ' + note.get('id', '<no id>'))
        self.assertEqual(missing, [], 'Entries without a source link:\n' + '\n'.join(missing))


if __name__ == '__main__':
    unittest.main()
