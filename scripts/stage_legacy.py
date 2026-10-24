"""Stage the small, verified root-site fallback required by legacy main:/ Pages.

Only run after build + validate. This is not the scheduled updater by itself:
production refreshes publish a verified Pages artifact. But the repository's
Pages source is legacy ``main:/``, so any push also republishes whatever is
committed at the repository root, and that committed copy is what visitors get
until the next artifact deployment. ``scripts.publish_root_fallback`` is the
guarded production caller used by ``pages.yml``; this module only copies files
and verifies hashes. No git operations occur here.
"""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
ALLOWED = {
    'index.html', 'picks.html', 'matches.html', 'unresolved.html', 'review.html',
    'analysis.html', 'sources.html', 'evidence.html', '404.html', 'assets/app.js', 'assets/style.css',
    'assets/favicon.svg', 'data/latest.json', 'data/matches.csv',
    'methodology.html', 'site/index.html', 'site/picks.html', 'site/unresolved.html',
    'site/review.html', 'site/methodology.html',
}
EXTRA = {'build-info.json', '.nojekyll'}


def ensure_stylesheet_parity(root=ROOT):
    """Make the served root stylesheet byte-identical to the canonical one.

    Measured on 2026-10-24: the committed root copy of ``assets/style.css`` was
    one ``}`` short of ``site/assets/style.css`` (725 vs 724), so the closing
    brace of a short-phone media block was missing and every later phone rule
    was nested inside it. Nothing regenerated the root copy after the canonical
    stylesheet changed, because the two files only ever meet during a staged
    publish. Staging now repairs that drift itself and reports it, instead of
    copying a build and hoping the copies agree.
    """
    root = Path(root)
    canonical = root / 'site' / 'assets' / 'style.css'
    served = root / 'assets' / 'style.css'
    if not canonical.is_file() or not served.is_file():
        return None
    if canonical.read_bytes() == served.read_bytes():
        return False
    shutil.copyfile(canonical, served)
    return True


def stage(public=PUBLIC, root=ROOT):
    """Copy the hash-verified public build into the legacy root fallback.

    Returns the sorted list of repository paths written. The manifest must
    describe exactly ``ALLOWED``: a build that adds or drops a public file has to
    be reviewed here first, so the committed root can never drift silently from
    the verified artifact.
    """
    public, root = Path(public), Path(root)
    manifest = json.loads((public / 'build-info.json').read_text())
    assert set(manifest['files']) == ALLOWED, 'Unexpected public file set; review before copying'
    for relative, digest in manifest['files'].items():
        source = public / relative
        assert source.is_file() and not source.is_symlink()
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    written = []
    for relative in sorted(ALLOWED | EXTRA):
        source = public / relative
        if relative in ALLOWED:
            assert source.is_file(), relative
        if not source.is_file():
            continue
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        written.append(relative)
    if ensure_stylesheet_parity(root):
        print('Repaired root assets/style.css from the canonical site/assets/style.css '
              '(the committed copy had drifted; see scripts.validate.stylesheet_problems).')
        written.append('assets/style.css')
    return written


def main():
    written = stage()
    print('Staged verified static root fallback (%d files); no branches changed or pushed.' % len(written))


if __name__ == '__main__':
    main()
