"""Pytest configuration and shared fixtures for template testing."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test output."""
    return tmp_path


@pytest.fixture
def template_dir() -> Path:
    """Provide the path to the template root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir() -> Path:
    """Provide the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def configs_dir(fixtures_dir: Path) -> Path:
    """Provide the path to the test configurations directory."""
    return fixtures_dir / "configs"


@pytest.fixture
def minimal_config() -> dict[str, Any]:
    """Provide minimal test configuration."""
    return {
        "project_name": "Test Project",
        "project_slug": "test_project",
        "project_short_description": "A test project",
        "author_name": "Test Author",
        "author_email": "test@example.com",
        "github_username": "testuser",
        "version": "0.1.0",
    }


@pytest.fixture
def cli_config(minimal_config: dict[str, Any]) -> dict[str, Any]:
    """Provide CLI application test configuration."""
    return {
        **minimal_config,
        "project_name": "CLI Tool",
        "project_slug": "cli_tool",
        "include_cli": "yes",
        "include_nox": "yes",
        "use_pre_commit": "yes",
    }


@pytest.fixture
def api_config(minimal_config: dict[str, Any]) -> dict[str, Any]:
    """Provide API service test configuration."""
    return {
        **minimal_config,
        "project_name": "API Service",
        "project_slug": "api_service",
        "include_api_framework": "yes",
        "include_database": "sqlalchemy_migrations",
        "include_health_checks": "yes",
        "include_codecov": "yes",
    }


@pytest.fixture
def ml_config(minimal_config: dict[str, Any]) -> dict[str, Any]:
    """Provide ML project test configuration."""
    return {
        **minimal_config,
        "project_name": "ML Project",
        "project_slug": "ml_project",
        "include_ml_dependencies": "yes",
        "include_docker": "yes",
        "include_nox": "yes",
        "include_codecov": "yes",
    }


@pytest.fixture
def full_config(minimal_config: dict[str, Any]) -> dict[str, Any]:
    """Provide full-featured test configuration."""
    return {
        **minimal_config,
        "project_name": "Full Featured Project",
        "project_slug": "full_featured_project",
        "include_cli": "yes",
        "include_api_framework": "yes",
        "include_ml_dependencies": "yes",
        "include_database": "sqlalchemy_migrations",
        "include_codecov": "yes",
        "include_sonarcloud": "yes",
        "include_semantic_release": "yes",
        "include_docker": "yes",
        "include_nox": "yes",
        "include_mutation_testing": "yes",
        "use_mkdocs": "yes",
    }


@pytest.fixture
def generated_project(
    temp_dir: Path, template_dir: Path, minimal_config: dict[str, Any]
) -> Generator[Path, None, None]:
    """Generate a test project and provide its path.

    Automatically cleans up after the test.
    """
    # Create a config file
    config_file = temp_dir / "config.json"
    with config_file.open("w") as f:
        json.dump({"default_context": minimal_config}, f)

    # Generate the project
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    subprocess.run(
        [
            "cookiecutter",
            str(template_dir),
            "--no-input",
            "--config-file",
            str(config_file),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    project_dir = output_dir / minimal_config["project_slug"]
    yield project_dir

    # Cleanup
    if project_dir.exists():
        shutil.rmtree(project_dir)


def generate_project(
    template_dir: Path, output_dir: Path, config: dict[str, Any]
) -> Path:
    """Generate a project with the given configuration.

    Args:
        template_dir: Path to the template directory
        output_dir: Path where the project should be generated
        config: Configuration dictionary for cookiecutter

    Returns:
        Path to the generated project directory
    """
    # Create a config file
    config_file = output_dir / "config.json"
    with config_file.open("w") as f:
        json.dump({"default_context": config}, f)

    # Generate the project
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
        check=True,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Project generation failed: {result.stderr}")

    return output_dir / config["project_slug"]


@pytest.fixture
def project_generator(template_dir: Path, temp_dir: Path):
    """Provide a function to generate projects with custom configurations."""

    def _generate(config: dict[str, Any]) -> Path:
        return generate_project(template_dir, temp_dir, config)

    return _generate
