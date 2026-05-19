"""Tests for scripts/check_unverified_assumption_tags.py.

Cover the pairing logic, narrative-prose skipping, and CLI behavior of the
helper used by the LLM Governance CI check.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_unverified_assumption_tags.py"


def _run(root: Path, *extra: str) -> tuple[int, str, str]:
    """Run the helper script and return (rc, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def test_zero_tags_returns_zero(tmp_path: Path) -> None:
    """A directory with no tags should report 0 unverified."""
    (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")
    rc, out, _ = _run(tmp_path)
    assert rc == 0
    assert out.strip() == "0"


def test_critical_with_paired_verify_is_clean(tmp_path: Path) -> None:
    """A #CRITICAL tag with #VERIFY in next line is fully verified."""
    (tmp_path / "paired.py").write_text(
        "# #CRITICAL: Security: user input flows to subprocess.\n"
        "# #VERIFY: input is validated by allowlist below.\n"
        "x = 1\n",
        encoding="utf-8",
    )
    rc, out, _ = _run(tmp_path)
    assert rc == 0
    assert out.strip() == "0"


def test_critical_without_verify_is_unverified(tmp_path: Path) -> None:
    """A #CRITICAL tag with no #VERIFY in following window is flagged."""
    (tmp_path / "bare.py").write_text(
        "# #CRITICAL: Security: dangerous operation.\n"
        "x = 1\n"
        "y = 2\n"
        "z = 3\n"
        "w = 4\n"
        "u = 5\n",
        encoding="utf-8",
    )
    rc, out, _ = _run(tmp_path)
    assert rc == 0
    assert out.strip() == "1"


def test_assume_with_paired_verify_is_clean(tmp_path: Path) -> None:
    """A #ASSUME tag paired with #VERIFY is verified."""
    (tmp_path / "paired_assume.py").write_text(
        "# #ASSUME: External Resources: API is reachable.\n"
        "# #VERIFY: timeout/retry on the call below.\n"
        "x = 1\n",
        encoding="utf-8",
    )
    rc, out, _ = _run(tmp_path)
    assert rc == 0
    assert out.strip() == "0"


def test_narrative_prose_mention_is_skipped(tmp_path: Path) -> None:
    """A #CRITICAL inside a docstring (not a code comment) must NOT be flagged."""
    (tmp_path / "docstring.py").write_text(
        'def f() -> None:\n'
        '    """This function handles a #CRITICAL: Security risk inline."""\n'
        '    return None\n',
        encoding="utf-8",
    )
    rc, out, _ = _run(tmp_path)
    assert rc == 0
    assert out.strip() == "0"


def test_window_size_can_be_overridden(tmp_path: Path) -> None:
    """A larger --window catches a #VERIFY further down."""
    (tmp_path / "wide.py").write_text(
        "# #CRITICAL: dangerous.\n"
        "x = 1\nx = 1\nx = 1\nx = 1\nx = 1\n"  # 5 filler lines
        "x = 1\nx = 1\n"  # 2 more (total 7)
        "# #VERIFY: addressed below.\n",
        encoding="utf-8",
    )
    rc_default, out_default, _ = _run(tmp_path)
    assert out_default.strip() == "1", "Default window=5 should miss the far #VERIFY"
    rc_wide, out_wide, _ = _run(tmp_path, "--window", "10")
    assert out_wide.strip() == "0", "Window=10 should catch the #VERIFY"


def test_verbose_emits_violator_locations_to_stderr(tmp_path: Path) -> None:
    """--verbose prints file:line for each unverified tag to stderr."""
    (tmp_path / "v.py").write_text(
        "# #CRITICAL: dangerous\n"
        "x = 1\nx = 2\nx = 3\nx = 4\nx = 5\n",
        encoding="utf-8",
    )
    rc, out, err = _run(tmp_path, "--verbose")
    assert rc == 0
    assert out.strip() == "1"
    assert "v.py:1" in err
