from __future__ import annotations

import importlib.util
from pathlib import Path


def load_auditor():
    spec_path = Path(__file__).resolve().parents[1] / 'verification-071642e7' / 'audit_071642e7.py'
    spec = importlib.util.spec_from_file_location('audit_071642e7', spec_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod
