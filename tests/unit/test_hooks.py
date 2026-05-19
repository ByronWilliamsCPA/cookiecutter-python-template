"""Unit tests for cookiecutter hooks."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from tests.conftest import generate_project


def _load_post_gen_module() -> Any:
    """Load hooks/post_gen_project.py via importlib for direct in-process testing."""
    repo_root = Path(__file__).resolve().parents[2]
    hook_path = repo_root / "hooks" / "post_gen_project.py"
    spec = importlib.util.spec_from_file_location("post_gen_project", hook_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["post_gen_project"] = mod
    spec.loader.exec_module(mod)
    return mod


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


def _is_setup_protection_invocation(cmd: list[str]) -> bool:
    """True iff cmd is a run_command argv that invokes setup_github_protection.py."""
    return any("setup_github_protection.py" in str(part) for part in cmd)


class TestAutoSetupBranchProtection:
    """Tests for the optional branch-protection auto-run in post-gen hook.

    These tests exercise the in-process helper directly (rather than running
    the full cookiecutter generation pipeline) so that we can assert the
    NEGATIVE invariant the original tautological generate_project assertions
    failed to verify: setup_github_protection.py is NOT executed when a
    precondition is missing. Earlier versions of these tests asserted only
    that the script file existed on disk, which is unrelated to whether it
    was invoked.
    """

    def test_auto_run_skipped_when_flag_disabled(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """No subprocess invocation when auto_setup_branch_protection is no."""
        mod = _load_post_gen_module()

        # Stage a fake script so existence cannot mask the early-return.
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "setup_github_protection.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")

        invocations: list[list[str]] = []

        def spy_run_command(cmd: list[str], check: bool = True) -> bool:  # noqa: ARG001
            invocations.append(list(cmd))
            return True

        monkeypatch.setattr(mod, "run_command", spy_run_command)

        result = mod.maybe_run_branch_protection(
            flag="no", remote_url="https://github.com/x/y.git"
        )

        assert result is False
        offending = [c for c in invocations if _is_setup_protection_invocation(c)]
        assert offending == [], (
            f"setup_github_protection.py must NOT be invoked when the flag is "
            f"disabled; observed offending invocations: {offending}"
        )

    def test_auto_run_skipped_when_token_missing(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """No subprocess invocation when GITHUB_TOKEN is unset, even if flag is yes."""
        mod = _load_post_gen_module()

        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "setup_github_protection.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

        invocations: list[list[str]] = []

        def spy_run_command(cmd: list[str], check: bool = True) -> bool:  # noqa: ARG001
            invocations.append(list(cmd))
            return True

        monkeypatch.setattr(mod, "run_command", spy_run_command)

        result = mod.maybe_run_branch_protection(
            flag="yes", remote_url="https://github.com/x/y.git"
        )

        assert result is False
        offending = [c for c in invocations if _is_setup_protection_invocation(c)]
        assert offending == [], (
            f"setup_github_protection.py must NOT be invoked when GITHUB_TOKEN "
            f"is unset; observed offending invocations: {offending}"
        )

    def test_auto_run_invokes_script_when_all_preconditions_met(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Positive control: real-invocation negative test would be meaningless
        without a paired positive test proving the spy can catch invocations.

        With flag=yes, token set, remote set, and the script present, the
        helper MUST call run_command with an argv that targets
        setup_github_protection.py. If this test fails while the two
        "skipped" tests pass, the spy is wired up wrong and the negative
        assertions are false positives.
        """
        mod = _load_post_gen_module()

        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "setup_github_protection.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")

        invocations: list[list[str]] = []

        def spy_run_command(cmd: list[str], check: bool = True) -> bool:  # noqa: ARG001
            invocations.append(list(cmd))
            return True

        monkeypatch.setattr(mod, "run_command", spy_run_command)

        result = mod.maybe_run_branch_protection(
            flag="yes", remote_url="https://github.com/x/y.git"
        )

        assert result is True
        matching = [c for c in invocations if _is_setup_protection_invocation(c)]
        assert len(matching) == 1, (
            f"Expected exactly one setup_github_protection.py invocation; "
            f"observed: {invocations}"
        )


class TestAutoSetupBranchProtectionGeneration:
    """End-to-end-style tests that the generation pipeline keeps the script.

    These cover the orthogonal invariant that even when the auto-run skips,
    the setup_github_protection.py script is still shipped into the generated
    project so the user can re-run it manually.
    """

    def test_setup_script_is_shipped_when_flag_disabled(
        self,
        template_dir: Path,
        temp_dir: Path,
        minimal_config: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Script must still ship even when auto_setup_branch_protection is no."""
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
        config = {**minimal_config, "auto_setup_branch_protection": "no"}
        project_dir = generate_project(template_dir, temp_dir, config)
        assert (project_dir / "scripts" / "setup_github_protection.py").exists()

    def test_setup_script_is_shipped_when_token_missing(
        self,
        template_dir: Path,
        temp_dir: Path,
        minimal_config: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Script must still ship even when GITHUB_TOKEN is unset."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        config = {**minimal_config, "auto_setup_branch_protection": "yes"}
        project_dir = generate_project(template_dir, temp_dir, config)
        assert (project_dir / "scripts" / "setup_github_protection.py").exists()
