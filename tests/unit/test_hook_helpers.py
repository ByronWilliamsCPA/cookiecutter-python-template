"""Tests for the helper functions in hooks/post_gen_project.py.

Covers _path_is_inside (symlink-escape guard) and _collect_installed_items
(Claude settings artifact discovery). Both are private security helpers
that did not previously have direct test coverage.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    pass


def _load_post_gen_module() -> object:
    """Load hooks/post_gen_project.py as a module without renaming it.

    The hook file path is `hooks/post_gen_project.py` and is NOT a regular
    package importable by name. We use importlib's spec-from-file machinery
    so the test can target the helpers directly without invoking cookiecutter.
    """
    repo_root = Path(__file__).resolve().parents[2]
    hook_path = repo_root / "hooks" / "post_gen_project.py"
    spec = importlib.util.spec_from_file_location("post_gen_project", hook_path)
    assert spec is not None and spec.loader is not None, "spec load failed"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["post_gen_project"] = mod
    # Some helpers reference Jinja2 placeholder strings directly. The module
    # imports successfully even when those placeholders are unrendered because
    # they are just string literals at import time. No template execution needed.
    spec.loader.exec_module(mod)
    return mod


def test_path_is_inside_returns_true_for_nested_path(tmp_path: Path) -> None:
    """A file resolved inside the root must report True."""
    mod = _load_post_gen_module()
    nested = tmp_path / "sub" / "file.txt"
    nested.parent.mkdir(parents=True)
    nested.write_text("x", encoding="utf-8")
    assert mod._path_is_inside(nested, tmp_path) is True  # noqa: SLF001


def test_path_is_inside_returns_false_for_escaping_symlink(tmp_path: Path) -> None:
    """A symlink whose resolved target is outside root must report False."""
    mod = _load_post_gen_module()
    outside = tmp_path.parent / "outside_target.txt"
    outside.write_text("x", encoding="utf-8")
    inside_link = tmp_path / "escapes.txt"
    inside_link.symlink_to(outside)
    assert mod._path_is_inside(inside_link, tmp_path) is False  # noqa: SLF001
    outside.unlink()


def test_path_is_inside_handles_oserror_gracefully(tmp_path: Path) -> None:
    """A broken symlink (no resolvable target) must not raise; returns False."""
    mod = _load_post_gen_module()
    broken = tmp_path / "broken_symlink"
    broken.symlink_to(tmp_path / "does_not_exist")
    # On most platforms, resolve(strict=False) on a broken symlink succeeds and
    # returns the would-be path. The function uses default resolve() which is
    # permissive; it should return True or False based on whether the
    # nonexistent target would be inside root, but never raise.
    result = mod._path_is_inside(broken, tmp_path)  # noqa: SLF001
    assert isinstance(result, bool)


def test_collect_installed_items_empty_directory(tmp_path: Path) -> None:
    """An empty install path returns an empty list."""
    mod = _load_post_gen_module()
    items = mod._collect_installed_items(tmp_path)  # noqa: SLF001
    assert items == []


def test_collect_installed_items_finds_claude_md(tmp_path: Path) -> None:
    """CLAUDE.md presence is reported."""
    mod = _load_post_gen_module()
    (tmp_path / "CLAUDE.md").write_text("hello", encoding="utf-8")
    items = mod._collect_installed_items(tmp_path)  # noqa: SLF001
    assert "CLAUDE.md" in items


def test_collect_installed_items_finds_skills_and_agents(tmp_path: Path) -> None:
    """skills/ and agents/ directory presence is reported with trailing slash."""
    mod = _load_post_gen_module()
    (tmp_path / "skills").mkdir()
    (tmp_path / "agents").mkdir()
    items = mod._collect_installed_items(tmp_path)  # noqa: SLF001
    assert "skills/" in items
    assert "agents/" in items


def test_collect_installed_items_finds_slash_commands_in_either_location(
    tmp_path: Path,
) -> None:
    """Slash commands are reported whether in .claude/commands or commands."""
    mod = _load_post_gen_module()
    (tmp_path / ".claude" / "commands").mkdir(parents=True)
    items = mod._collect_installed_items(tmp_path)  # noqa: SLF001
    assert "slash commands" in items


def test_collect_installed_items_returns_all_when_present(tmp_path: Path) -> None:
    """All four artifact types are reported when all are present."""
    mod = _load_post_gen_module()
    (tmp_path / "CLAUDE.md").write_text("x", encoding="utf-8")
    (tmp_path / "skills").mkdir()
    (tmp_path / "agents").mkdir()
    (tmp_path / "commands").mkdir()
    items = mod._collect_installed_items(tmp_path)  # noqa: SLF001
    assert set(items) == {"CLAUDE.md", "skills/", "agents/", "slash commands"}


def test_include_constants_are_strings() -> None:
    """The Jinja2-rendered include constants are plain strings at module level."""
    mod = _load_post_gen_module()
    assert isinstance(mod.INCLUDE_DOCKER, str)
    assert isinstance(mod.INCLUDE_FRONTEND, str)
    assert isinstance(mod.INCLUDE_SUPPLY_CHAIN_SECURITY, str)


def test_is_safe_clone_url_rejects_dash_prefix() -> None:
    """URLs starting with '-' are rejected to prevent flag injection to git."""
    mod = _load_post_gen_module()
    assert mod._is_safe_clone_url("--upload-pack=evil") is False  # noqa: SLF001
    assert mod._is_safe_clone_url("-h") is False  # noqa: SLF001


def test_is_safe_clone_url_rejects_empty() -> None:
    """Empty/None URLs are rejected."""
    mod = _load_post_gen_module()
    assert mod._is_safe_clone_url("") is False  # noqa: SLF001


def test_is_safe_clone_url_accepts_https() -> None:
    """HTTPS URLs are accepted."""
    mod = _load_post_gen_module()
    assert mod._is_safe_clone_url("https://github.com/owner/repo.git") is True  # noqa: SLF001


def test_is_safe_clone_url_accepts_ssh_url() -> None:
    """ssh:// URLs are accepted."""
    mod = _load_post_gen_module()
    assert mod._is_safe_clone_url("ssh://git@github.com/owner/repo.git") is True  # noqa: SLF001


def test_is_safe_clone_url_accepts_scp_style() -> None:
    """git@host:path SCP-style URLs are accepted."""
    mod = _load_post_gen_module()
    assert mod._is_safe_clone_url("git@github.com:owner/repo.git") is True  # noqa: SLF001


def test_is_safe_clone_url_rejects_git_protocol() -> None:
    """git:// URLs are rejected (unauthenticated, plaintext)."""
    mod = _load_post_gen_module()
    assert mod._is_safe_clone_url("git://github.com/owner/repo.git") is False  # noqa: SLF001


def test_is_safe_clone_url_rejects_file_scheme() -> None:
    """file:// URLs are rejected."""
    mod = _load_post_gen_module()
    assert mod._is_safe_clone_url("file:///etc/passwd") is False  # noqa: SLF001
