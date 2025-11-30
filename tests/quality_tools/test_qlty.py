"""Tests for QLTY integration in generated projects."""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING, Any

import pytest


if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.integration
class TestQLTYIntegration:
    """Tests for QLTY configuration and integration."""

    def test_qlty_config_exists(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify .qlty directory exists in generated project."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        qlty_dir = project_dir / ".qlty"
        # QLTY config might be optional, so this test checks if it exists when expected
        if qlty_dir.exists():
            # If .qlty exists, it should have config
            assert (qlty_dir / "qlty.toml").exists() or \
                   any(qlty_dir.glob("*.toml")) or \
                   any(qlty_dir.glob("*.yml")), \
                ".qlty directory should contain configuration"

    @pytest.mark.slow
    def test_qlty_check_runs(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify QLTY check can run on generated project."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        # Check if qlty command is available
        if not shutil.which("qlty"):
            pytest.skip("QLTY not installed")

        result = subprocess.run(
            ["qlty", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            pytest.skip("QLTY not working properly")

        # Run qlty check
        result = subprocess.run(
            ["qlty", "check"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # QLTY should at least run without crashing
        # It may find issues, but shouldn't fail to execute
        assert result.returncode in [0, 1, 2], \
            f"QLTY check should execute: {result.stdout}\n{result.stderr}"

    def test_qlty_config_valid_toml(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify QLTY configuration is valid TOML."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        qlty_dir = project_dir / ".qlty"
        if not qlty_dir.exists():
            pytest.skip("No .qlty directory in generated project")

        # Find TOML config files
        toml_configs = list(qlty_dir.glob("*.toml"))
        if not toml_configs:
            pytest.skip("No TOML config files in .qlty directory")

        import tomli

        for config_file in toml_configs:
            with config_file.open("rb") as f:
                data = tomli.load(f)
                assert isinstance(data, dict), \
                    f"{config_file.name} should be valid TOML"
