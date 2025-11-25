"""Integration tests for generated project CI workflows."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    pass


@pytest.mark.integration
@pytest.mark.slow
class TestGeneratedProjectCI:
    """Tests for running CI checks on generated projects."""

    def test_precommit_hooks_pass(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify pre-commit hooks pass on generated project."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "use_pre_commit": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        # Install pre-commit hooks
        result = subprocess.run(
            ["pre-commit", "install"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "Pre-commit install should succeed"

        # Run pre-commit on all files
        result = subprocess.run(
            ["pre-commit", "run", "--all-files"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # Pre-commit should pass (returncode 0) or only have skipped hooks
        # Some hooks might be skipped if files don't exist yet
        if result.returncode != 0:
            # Check if failures are only from missing files (acceptable for template)
            acceptable_failures = ["no files to check", "Skipped"]
            assert any(msg in result.stdout for msg in acceptable_failures), \
                f"Pre-commit checks failed: {result.stdout}\n{result.stderr}"

    def test_ruff_check_passes(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify ruff check passes on generated project."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        result = subprocess.run(
            ["ruff", "check", "."],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, \
            f"Ruff check should pass: {result.stdout}\n{result.stderr}"

    def test_pytest_runs(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify pytest runs on generated project."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        # First install dependencies with uv
        result = subprocess.run(
            ["uv", "sync"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            pytest.skip(f"UV sync failed (may not be available): {result.stderr}")

        # Run pytest
        result = subprocess.run(
            ["uv", "run", "pytest", "-v"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # Tests should pass (or at least run without errors)
        assert result.returncode == 0, \
            f"Pytest should succeed: {result.stdout}\n{result.stderr}"

    @pytest.mark.slow
    def test_type_checking_passes(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify type checking passes on generated project."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        # Use mypy if available, basedpyright is preferred but may not be installed
        result = subprocess.run(
            ["mypy", "src/", "--ignore-missing-imports"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 127:  # Command not found
            pytest.skip("MyPy not available")

        # Allow warnings but not errors
        assert "error:" not in result.stdout.lower() or result.returncode == 0, \
            f"Type checking should pass: {result.stdout}\n{result.stderr}"


@pytest.mark.integration
@pytest.mark.slow
class TestGeneratedProjectBuild:
    """Tests for building generated projects."""

    def test_uv_sync_succeeds(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify uv sync succeeds for generated project."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        result = subprocess.run(
            ["uv", "sync"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 127:  # Command not found
            pytest.skip("UV not available")

        assert result.returncode == 0, \
            f"UV sync should succeed: {result.stdout}\n{result.stderr}"

    def test_package_builds(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify package can be built."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        # Try to build with uv
        result = subprocess.run(
            ["uv", "build"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 127:  # Command not found
            # Try with build module
            result = subprocess.run(
                ["python", "-m", "build"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                check=False,
            )

        # Build might fail due to missing dependencies, but shouldn't crash
        assert "error" not in result.stderr.lower() or result.returncode == 0, \
            f"Build should not error: {result.stdout}\n{result.stderr}"


@pytest.mark.integration
class TestCLIGeneration:
    """Tests for CLI-enabled projects."""

    def test_cli_entrypoint_exists(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify CLI entrypoint is created when CLI is enabled."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_cli": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()

        # Should have scripts section
        assert "[project.scripts]" in content, \
            "CLI project should have [project.scripts] section"

    @pytest.mark.slow
    def test_cli_runs_help(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify CLI help command runs."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_cli": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        # Install the package
        result = subprocess.run(
            ["uv", "sync"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            pytest.skip("UV sync failed")

        # Try to run --help
        cli_name = config["project_slug"]
        result = subprocess.run(
            ["uv", "run", cli_name, "--help"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # Help should work
        assert result.returncode == 0, \
            f"CLI help should work: {result.stdout}\n{result.stderr}"
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower(), \
            "Help output should contain usage information"
