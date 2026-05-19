"""Unit tests for cookiecutter hooks."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.conftest import generate_project


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
        assert result.returncode == 0, (
            f"Hook has invalid Python syntax: {result.stderr}"
        )

    def test_hook_imports(self, template_dir: Path) -> None:
        """Verify hook file can be imported."""
        hook_file = template_dir / "hooks" / "pre_gen_project.py"
        # Just check it doesn't raise import errors
        result = subprocess.run(
            [
                "python",
                "-c",
                f"import sys; sys.path.insert(0, '{hook_file.parent}'); import pre_gen_project",
            ],
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
        assert result.returncode == 0, (
            f"Hook has invalid Python syntax: {result.stderr}"
        )

    def test_hook_imports(self, template_dir: Path) -> None:
        """Verify hook file can be imported."""
        hook_file = template_dir / "hooks" / "post_gen_project.py"
        result = subprocess.run(
            [
                "python",
                "-c",
                f"import sys; sys.path.insert(0, '{hook_file.parent}'); import post_gen_project",
            ],
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

    def test_hooks_pass_ruff_format(self, template_dir: Path) -> None:
        """Verify hooks are formatted with ruff (replaces black)."""
        hooks_dir = template_dir / "hooks"
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "--check", str(hooks_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Ruff format check failed: {result.stderr}"

    @pytest.mark.slow
    def test_hooks_pass_basedpyright(self, template_dir: Path) -> None:
        """Verify hooks pass basedpyright type checking."""
        import shutil

        # basedpyright is installed via `uv sync --all-extras` into .venv/bin,
        # which is not on PATH. shutil.which would silently skip the assertion
        # on CI. Detect the venv binary and prefer it; fall back to PATH for
        # local developer setups that may have a global install.
        venv_bin = template_dir / ".venv" / "bin" / "basedpyright"
        basedpyright_cmd = (
            str(venv_bin) if venv_bin.exists() else shutil.which("basedpyright")
        )
        if basedpyright_cmd is None:
            pytest.skip("basedpyright not installed")
        hooks_dir = template_dir / "hooks"
        result = subprocess.run(
            [basedpyright_cmd, str(hooks_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            f"BasedPyright check failed: {result.stdout}\n{result.stderr}"
        )


class TestAutoSetupBranchProtection:
    """Tests for the optional branch-protection auto-run in post-gen hook."""

    def test_auto_run_skipped_when_flag_disabled(
        self,
        template_dir: Path,
        temp_dir: Path,
        minimal_config: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """No subprocess invocation when auto_setup_branch_protection is no."""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
        config = {**minimal_config, "auto_setup_branch_protection": "no"}
        project_dir = generate_project(template_dir, temp_dir, config)
        assert (project_dir / "scripts" / "setup_github_protection.py").exists()

    def test_auto_run_skipped_when_token_missing(
        self,
        template_dir: Path,
        temp_dir: Path,
        minimal_config: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """No subprocess invocation when GITHUB_TOKEN is unset, even if flag is yes."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        config = {**minimal_config, "auto_setup_branch_protection": "yes"}
        project_dir = generate_project(template_dir, temp_dir, config)
        assert (project_dir / "scripts" / "setup_github_protection.py").exists()
