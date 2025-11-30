"""Tests for template generation with various configurations."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

import pytest


if TYPE_CHECKING:
    from pathlib import Path


class TestBasicGeneration:
    """Tests for basic template generation."""

    def test_cookiecutter_json_valid(self, template_dir: Path) -> None:
        """Verify cookiecutter.json is valid JSON."""
        cookiecutter_json = template_dir / "cookiecutter.json"
        with cookiecutter_json.open() as f:
            data = json.load(f)
        assert isinstance(data, dict), "cookiecutter.json should be a dictionary"
        assert "project_name" in data, "cookiecutter.json should have project_name"

    def test_minimal_generation(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Test generation with minimal configuration."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)
        assert project_dir.exists(), "Project directory should exist"
        assert (project_dir / "pyproject.toml").exists(), "pyproject.toml should exist"
        assert (project_dir / "README.md").exists(), "README.md should exist"
        assert (project_dir / "src").exists(), "src directory should exist"
        assert (project_dir / "tests").exists(), "tests directory should exist"

    def test_cli_generation(
        self, template_dir: Path, temp_dir: Path, cli_config: dict[str, Any]
    ) -> None:
        """Test generation with CLI configuration."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, cli_config)
        assert project_dir.exists(), "Project directory should exist"

        # Check for CLI-specific files
        pyproject = project_dir / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml should exist"

        # Verify CLI dependencies are included
        content = pyproject.read_text()
        assert "typer" in content.lower() or "click" in content.lower(), \
            "CLI framework should be in dependencies"

    def test_api_generation(
        self, template_dir: Path, temp_dir: Path, api_config: dict[str, Any]
    ) -> None:
        """Test generation with API service configuration."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, api_config)
        assert project_dir.exists(), "Project directory should exist"

        # Check for API-specific files
        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()
        assert "fastapi" in content.lower() or "flask" in content.lower(), \
            "API framework should be in dependencies"
        assert "sqlalchemy" in content.lower(), \
            "Database framework should be in dependencies"

    def test_ml_generation(
        self, template_dir: Path, temp_dir: Path, ml_config: dict[str, Any]
    ) -> None:
        """Test generation with ML project configuration."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, ml_config)
        assert project_dir.exists(), "Project directory should exist"

        # Check for ML-specific dependencies
        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()
        # At least some ML-related packages should be present
        ml_packages = ["numpy", "pandas", "scikit-learn", "torch", "tensorflow"]
        assert any(pkg in content.lower() for pkg in ml_packages), \
            "ML dependencies should be in pyproject.toml"

    @pytest.mark.slow
    def test_full_featured_generation(
        self, template_dir: Path, temp_dir: Path, full_config: dict[str, Any]
    ) -> None:
        """Test generation with all features enabled."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, full_config)
        assert project_dir.exists(), "Project directory should exist"

        # Verify key features are present
        assert (project_dir / "noxfile.py").exists(), "noxfile.py should exist"
        assert (project_dir / "Dockerfile").exists(), "Dockerfile should exist"
        assert (project_dir / ".github" / "workflows").exists(), \
            "GitHub workflows should exist"
        assert (project_dir / "docs").exists(), "docs directory should exist"


class TestConfigurationVariations:
    """Tests for various configuration combinations."""

    @pytest.mark.parametrize(
        "config_name",
        ["minimal", "cli-app", "api-service", "ml-project", "full-featured"],
    )
    def test_predefined_configs(
        self, template_dir: Path, temp_dir: Path, configs_dir: Path, config_name: str
    ) -> None:
        """Test generation with predefined configuration files."""
        config_file = configs_dir / f"{config_name}.json"
        assert config_file.exists(), f"Config file {config_name}.json should exist"

        # Generate project
        output_dir = temp_dir / config_name
        output_dir.mkdir()

        result = subprocess.run(
            [
                "cookiecutter",
                str(template_dir),
                "--no-input",
                "--config-file",
                str(config_file),
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, \
            f"Generation failed for {config_name}: {result.stderr}"

        # Verify project directory exists
        with config_file.open() as f:
            config_data = json.load(f)
        project_slug = config_data["default_context"]["project_slug"]
        project_dir = output_dir / project_slug

        assert project_dir.exists(), \
            f"Project directory should exist for {config_name}"
        assert (project_dir / "pyproject.toml").exists(), \
            f"pyproject.toml should exist for {config_name}"


class TestInvalidInputHandling:
    """Tests for handling invalid inputs."""

    def test_generation_with_empty_project_name(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Test that generation fails gracefully with empty project name."""
        config = {
            "project_name": "",  # Invalid: empty
            "author_name": "Test Author",
            "author_email": "test@example.com",
        }

        config_file = temp_dir / "invalid_config.json"
        with config_file.open("w") as f:
            json.dump({"default_context": config}, f)

        result = subprocess.run(
            [
                "cookiecutter",
                str(template_dir),
                "--no-input",
                "--config-file",
                str(config_file),
                "--output-dir",
                str(temp_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Should fail validation in pre_gen_project.py
        assert result.returncode != 0, \
            "Generation should fail with empty project name"
