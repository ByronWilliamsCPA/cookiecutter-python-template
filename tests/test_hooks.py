"""Unit tests for cookiecutter hooks."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from pathlib import Path


class TestPreGenHook:
    """Tests for pre_gen_project.py hook."""

    def test_hook_file_exists(self, template_dir: Path) -> None:
        """Verify pre_gen_project.py exists."""
        hook_file = template_dir / "hooks" / "pre_gen_project.py"
        assert hook_file.exists(), "pre_gen_project.py hook file should exist"

    def test_hook_has_valid_python_syntax(self, template_dir: Path) -> None:
        """Verify hook file has valid Python syntax."""
        hook_file = template_dir / "hooks" / "pre_gen_project.py"
        result = subprocess.run(
            ["python", "-m", "py_compile", str(hook_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Hook has invalid Python syntax: {result.stderr}"

    def test_hook_imports(self, template_dir: Path) -> None:
        """Verify hook file can be imported."""
        hook_file = template_dir / "hooks" / "pre_gen_project.py"
        # Just check it doesn't raise import errors
        result = subprocess.run(
            ["python", "-c", f"import sys; sys.path.insert(0, '{hook_file.parent}'); "
                              "import pre_gen_project"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Hook import failed: {result.stderr}"


class TestPostGenHook:
    """Tests for post_gen_project.py hook."""

    def test_hook_file_exists(self, template_dir: Path) -> None:
        """Verify post_gen_project.py exists."""
        hook_file = template_dir / "hooks" / "post_gen_project.py"
        assert hook_file.exists(), "post_gen_project.py hook file should exist"

    def test_hook_has_valid_python_syntax(self, template_dir: Path) -> None:
        """Verify hook file has valid Python syntax."""
        hook_file = template_dir / "hooks" / "post_gen_project.py"
        result = subprocess.run(
            ["python", "-m", "py_compile", str(hook_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Hook has invalid Python syntax: {result.stderr}"

    def test_hook_imports(self, template_dir: Path) -> None:
        """Verify hook file can be imported."""
        hook_file = template_dir / "hooks" / "post_gen_project.py"
        result = subprocess.run(
            ["python", "-c", f"import sys; sys.path.insert(0, '{hook_file.parent}'); "
                              "import post_gen_project"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Hook import failed: {result.stderr}"


class TestHookCodeQuality:
    """Tests for hook code quality."""

    def test_hooks_pass_ruff(self, template_dir: Path) -> None:
        """Verify hooks pass ruff linting."""
        hooks_dir = template_dir / "hooks"
        result = subprocess.run(
            ["ruff", "check", str(hooks_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Ruff check failed: {result.stdout}"

    def test_hooks_pass_black(self, template_dir: Path) -> None:
        """Verify hooks are formatted with black."""
        hooks_dir = template_dir / "hooks"
        result = subprocess.run(
            ["black", "--check", str(hooks_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Black formatting check failed: {result.stderr}"

    @pytest.mark.slow
    def test_hooks_pass_mypy(self, template_dir: Path) -> None:
        """Verify hooks pass mypy type checking."""
        hooks_dir = template_dir / "hooks"
        result = subprocess.run(
            ["mypy", str(hooks_dir), "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            check=False,
        )
        # MyPy returns 0 on success
        assert result.returncode == 0, f"MyPy check failed: {result.stdout}"
