"""Tests for the utility functions and standalone helpers in hooks/post_gen_project.py.

Covers the basic file/dir helpers (`remove_file`, `remove_dir`,
`make_executable`, `run_command`) plus the standalone data-processing
functions (`get_cruft_skip_patterns`, `inject_creation_date`,
`add_cruft_skip_patterns`, `ensure_trailing_newlines`).

These functions don't depend on Jinja2-rendered context, so they can be
exercised directly via importlib without invoking cookiecutter.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_post_gen_module() -> object:
    """Load hooks/post_gen_project.py via importlib (not a normal package)."""
    repo_root = Path(__file__).resolve().parents[2]
    hook_path = repo_root / "hooks" / "post_gen_project.py"
    spec = importlib.util.spec_from_file_location("post_gen_project", hook_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["post_gen_project"] = mod
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------
# remove_file
# ----------------------------------------------------------------------------


def test_remove_file_removes_existing(tmp_path: Path) -> None:
    """remove_file unlinks an existing file."""
    mod = _load_post_gen_module()
    target = tmp_path / "doomed.txt"
    target.write_text("x", encoding="utf-8")
    assert target.exists()
    mod.remove_file(target)
    assert not target.exists()


def test_remove_file_silent_on_nonexistent(tmp_path: Path) -> None:
    """remove_file does NOT raise when the path is missing."""
    mod = _load_post_gen_module()
    mod.remove_file(tmp_path / "never_existed.txt")  # must not raise


# ----------------------------------------------------------------------------
# remove_dir
# ----------------------------------------------------------------------------


def test_remove_dir_removes_recursively(tmp_path: Path) -> None:
    """remove_dir removes the directory tree."""
    mod = _load_post_gen_module()
    target = tmp_path / "tree"
    (target / "sub").mkdir(parents=True)
    (target / "sub" / "file.txt").write_text("x", encoding="utf-8")
    mod.remove_dir(target)
    assert not target.exists()


def test_remove_dir_silent_on_nonexistent(tmp_path: Path) -> None:
    """remove_dir is a no-op when the path is missing."""
    mod = _load_post_gen_module()
    mod.remove_dir(tmp_path / "never_existed")  # must not raise


# ----------------------------------------------------------------------------
# make_executable
# ----------------------------------------------------------------------------


def test_make_executable_sets_user_exec_bit(tmp_path: Path) -> None:
    """make_executable adds the executable bits."""
    mod = _load_post_gen_module()
    target = tmp_path / "script.sh"
    target.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    target.chmod(0o644)
    mod.make_executable(target)
    new_mode = target.stat().st_mode & 0o777
    assert new_mode & 0o100, f"user-exec bit not set: {oct(new_mode)}"


def test_make_executable_silent_on_nonexistent(tmp_path: Path) -> None:
    """make_executable is a no-op when the path is missing."""
    mod = _load_post_gen_module()
    mod.make_executable(tmp_path / "missing")  # must not raise


# ----------------------------------------------------------------------------
# run_command
# ----------------------------------------------------------------------------


def test_run_command_returns_true_on_success() -> None:
    """run_command returns True for a command that exits 0."""
    mod = _load_post_gen_module()
    assert mod.run_command(["true"], check=False) is True


def test_run_command_returns_false_on_nonzero_exit() -> None:
    """run_command returns False when the command exits non-zero with check=True."""
    mod = _load_post_gen_module()
    assert mod.run_command(["false"], check=True) is False


def test_run_command_returns_false_on_command_not_found() -> None:
    """run_command returns False when the command does not exist on PATH."""
    mod = _load_post_gen_module()
    assert mod.run_command(["this_command_definitely_does_not_exist_xyz"]) is False


# ----------------------------------------------------------------------------
# get_cruft_skip_patterns
# ----------------------------------------------------------------------------


def test_get_cruft_skip_patterns_returns_list() -> None:
    """get_cruft_skip_patterns returns a non-empty list of strings."""
    mod = _load_post_gen_module()
    patterns = mod.get_cruft_skip_patterns()
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    assert all(isinstance(p, str) for p in patterns)


def test_get_cruft_skip_patterns_includes_uvlock() -> None:
    """The returned patterns include the well-known uv.lock case."""
    mod = _load_post_gen_module()
    patterns = mod.get_cruft_skip_patterns()
    assert any("uv.lock" in p for p in patterns)


def test_get_cruft_skip_patterns_includes_template_specific() -> None:
    """The returned patterns include template-owned files like CLAUDE.md."""
    mod = _load_post_gen_module()
    patterns = mod.get_cruft_skip_patterns()
    assert "CLAUDE.md" in patterns
    assert "REUSE.toml" in patterns


# ----------------------------------------------------------------------------
# inject_creation_date
# ----------------------------------------------------------------------------


def test_inject_creation_date_replaces_placeholder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """inject_creation_date replaces __PROJECT_CREATION_DATE__ in target files."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    (tmp_path / "CLAUDE.md").write_text(
        "# Created __PROJECT_CREATION_DATE__\n", encoding="utf-8"
    )
    (tmp_path / "README.md").write_text(
        "Built __PROJECT_CREATION_DATE__\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text(
        "# created on __PROJECT_CREATION_DATE__\n", encoding="utf-8"
    )
    mod.inject_creation_date()
    for fname in ("CLAUDE.md", "README.md", "pyproject.toml"):
        text = (tmp_path / fname).read_text(encoding="utf-8")
        assert "__PROJECT_CREATION_DATE__" not in text
        # The injected date should look like YYYY-MM-DD
        import re as _re

        assert _re.search(r"\d{4}-\d{2}-\d{2}", text)


def test_inject_creation_date_skips_missing_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """inject_creation_date is a no-op when none of its target files exist."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    mod.inject_creation_date()  # must not raise; no files present


def test_inject_creation_date_leaves_files_without_placeholder_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files with no __PROJECT_CREATION_DATE__ marker are unchanged."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    original = "# regular project file\nno placeholder here\n"
    (tmp_path / "CLAUDE.md").write_text(original, encoding="utf-8")
    mod.inject_creation_date()
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == original


# ----------------------------------------------------------------------------
# add_cruft_skip_patterns
# ----------------------------------------------------------------------------


def test_add_cruft_skip_patterns_creates_minimal_when_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When .cruft.json is absent, a minimal one is created with skip patterns."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    mod.add_cruft_skip_patterns()
    cruft_file = tmp_path / ".cruft.json"
    assert cruft_file.exists()
    config = json.loads(cruft_file.read_text(encoding="utf-8"))
    assert "skip" in config
    assert isinstance(config["skip"], list)
    assert len(config["skip"]) > 0


def test_add_cruft_skip_patterns_merges_with_existing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When .cruft.json exists, new patterns are merged with the user's existing skip."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    existing = {
        "template": "https://example.com/template",
        "skip": ["my_user_pattern.txt", "uv.lock"],  # uv.lock overlaps with new
    }
    (tmp_path / ".cruft.json").write_text(json.dumps(existing), encoding="utf-8")
    mod.add_cruft_skip_patterns()
    config = json.loads((tmp_path / ".cruft.json").read_text(encoding="utf-8"))
    # User's pattern preserved
    assert "my_user_pattern.txt" in config["skip"]
    # Original 'template' field preserved
    assert config.get("template") == "https://example.com/template"
    # Some standard skip pattern present
    assert any("uv.lock" in p for p in config["skip"])
    # No duplicates
    assert len(config["skip"]) == len(set(config["skip"]))


def test_add_cruft_skip_patterns_normalizes_string_skip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If existing skip is a single string (not list), it is normalized."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    existing = {
        "template": "https://example.com/template",
        "skip": "single_pattern.txt",  # malformed: should be list
    }
    (tmp_path / ".cruft.json").write_text(json.dumps(existing), encoding="utf-8")
    mod.add_cruft_skip_patterns()
    config = json.loads((tmp_path / ".cruft.json").read_text(encoding="utf-8"))
    assert isinstance(config["skip"], list)
    assert "single_pattern.txt" in config["skip"]


# ----------------------------------------------------------------------------
# ensure_trailing_newlines
# ----------------------------------------------------------------------------


def test_ensure_trailing_newlines_appends_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files without a trailing newline get one appended."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "no_newline.py"
    target.write_bytes(b"print('hi')")  # NO trailing \n
    mod.ensure_trailing_newlines()
    assert target.read_bytes().endswith(b"\n")


def test_ensure_trailing_newlines_leaves_correctly_terminated_files_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files that already end with a newline are not double-terminated."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "ok.py"
    target.write_bytes(b"print('hi')\n")
    mod.ensure_trailing_newlines()
    assert target.read_bytes() == b"print('hi')\n"


def test_ensure_trailing_newlines_skips_binary_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files containing NUL bytes in the first 1KB are skipped."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "binary.bin"
    # Write content with NUL byte and no trailing newline
    target.write_bytes(b"binary\x00data")
    mod.ensure_trailing_newlines()
    # Must remain unchanged (no trailing \n appended)
    assert target.read_bytes() == b"binary\x00data"


def test_ensure_trailing_newlines_skips_git_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files under .git/ are not touched (avoids corrupting git internals)."""
    mod = _load_post_gen_module()
    monkeypatch.chdir(tmp_path)
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    target = git_dir / "HEAD"
    target.write_bytes(b"ref: refs/heads/main")  # no trailing \n
    mod.ensure_trailing_newlines()
    # Must remain unchanged because .git/ is skipped
    assert target.read_bytes() == b"ref: refs/heads/main"


# ----------------------------------------------------------------------------
# maybe_run_branch_protection
# ----------------------------------------------------------------------------


class TestAutoSetupBranchProtectionHelper:
    """Tests for the maybe_run_branch_protection helper in post_gen_project.py."""

    def test_helper_skips_when_flag_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Helper returns False when flag is no."""
        mod = _load_post_gen_module()
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        result = mod.maybe_run_branch_protection(flag="no", remote_url="https://github.com/x/y")
        assert result is False

    def test_helper_skips_when_token_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Helper returns False when GITHUB_TOKEN is unset."""
        mod = _load_post_gen_module()
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        result = mod.maybe_run_branch_protection(flag="yes", remote_url="https://github.com/x/y")
        assert result is False

    def test_helper_skips_when_remote_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Helper returns False when no remote URL is supplied."""
        mod = _load_post_gen_module()
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        result = mod.maybe_run_branch_protection(flag="yes", remote_url="")
        assert result is False
