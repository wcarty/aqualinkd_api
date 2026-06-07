"""Pytest conftest to make `custom_components` importable in CI.

This adds the nearest ancestor directory containing `custom_components`
to `sys.path` so tests can `import custom_components.aqualinkd_api...`.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_custom_components_on_path() -> None:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "custom_components").is_dir():
            sys.path.insert(0, str(parent))
            return


_ensure_custom_components_on_path()
