"""A valid data file is not enough: displayed values must match it too."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from scripts.validate import validate_site

ROOT = Path(__file__).resolve().parents[1]


class RenderedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        manifest = json.loads((ROOT / 'build-info.json').read_text())
        for relative in [*manifest['files'], 'build-info.json']:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def test_wrong_rendered_probability_fails_before_checksum_check(self):
        path = self.root / 'picks.html'
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        soup.select_one('.prob-pair span').string = '99.9%'
        path.write_text(str(soup))
        with self.assertRaisesRegex(AssertionError, 'Rendered probability differs'):
            validate_site(self.root)

    def test_missing_visible_inventory_row_fails_before_checksum_check(self):
        path = self.root / 'matches.html'
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        soup.select_one('tr[data-match]').decompose()
        path.write_text(str(soup))
        with self.assertRaisesRegex(AssertionError, 'full retained inventory'):
            validate_site(self.root)


if __name__ == '__main__':
    unittest.main()
