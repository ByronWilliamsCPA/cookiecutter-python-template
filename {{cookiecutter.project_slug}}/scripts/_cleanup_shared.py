"""Shared helpers for cleanup_conditional_files.py and check_orphaned_files.py.

Centralizes utilities that both scripts need (the cruft context loader).
Both scripts import the shared function via sibling import:

    from _cleanup_shared import get_cruft_context

This module has no module-level side effects and is safe to import.
"""

from __future__ import annotations

import json
from pathlib import Path


def get_cruft_context() -> dict[str, str]:
    """Read cookiecutter context from .cruft.json.

    Returns:
        Dictionary of cookiecutter context values.

    Raises:
        FileNotFoundError: If .cruft.json doesn't exist.
        json.JSONDecodeError: If .cruft.json is invalid JSON.
    """
    cruft_file = Path(".cruft.json")
    if not cruft_file.exists():
        msg = ".cruft.json not found. Is this a cruft-managed project?"
        raise FileNotFoundError(msg)

    cruft_data = json.loads(cruft_file.read_text(encoding="utf-8"))
    return cruft_data.get("context", {}).get("cookiecutter", {})
