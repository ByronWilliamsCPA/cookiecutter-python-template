"""Tests for validating generated project content."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest


if TYPE_CHECKING:
    from pathlib import Path


class TestGeneratedFileContent:
    """Tests for validating content of generated files."""

    def test_no_template_variables_remain(self, generated_project: Path) -> None:
        """Verify no Jinja2 template variables remain in generated files."""
        # Check all text files for {{ }} patterns
        excluded_patterns = {
            ".git",
            ".venv",
            "__pycache__",
            "*.pyc",
            "node_modules",
        }

        jinja_pattern = re.compile(r"\{\{.*?\}\}|\{%.*?%\}")

        for file_path in generated_project.rglob("*"):
            # Skip directories and excluded patterns
            if file_path.is_dir():
                continue
            if any(pattern in str(file_path) for pattern in excluded_patterns):
                continue

            # Only check text files
            try:
                content = file_path.read_text()
                matches = jinja_pattern.findall(content)
                assert not matches, \
                    f"Found unreplaced Jinja2 variables in {file_path}: {matches}"
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files we can't read
                continue

    def test_pyproject_toml_valid(self, generated_project: Path) -> None:
        """Verify pyproject.toml is valid TOML."""
        import tomli

        pyproject = generated_project / "pyproject.toml"
        with pyproject.open("rb") as f:
            data = tomli.load(f)

        # Check required sections exist
        assert "project" in data, "pyproject.toml should have [project] section"
        assert "name" in data["project"], "pyproject.toml should have project.name"
        assert "version" in data["project"], "pyproject.toml should have project.version"

    def test_readme_has_project_name(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify README contains the actual project name, not placeholder."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, minimal_config)
        readme = project_dir / "README.md"
        content = readme.read_text()

        # Should contain actual project name
        assert minimal_config["project_name"] in content, \
            "README should contain actual project name"

        # Should NOT contain placeholders
        assert "My Python Project" not in content, \
            "README should not contain default placeholder"

    def test_src_directory_structure(self, generated_project: Path) -> None:
        """Verify src directory has correct structure."""
        src_dir = generated_project / "src"
        assert src_dir.exists(), "src directory should exist"

        # Should have at least one package directory
        package_dirs = [d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        assert len(package_dirs) >= 1, "src should contain at least one package"

        # Each package should have __init__.py
        for package_dir in package_dirs:
            init_file = package_dir / "__init__.py"
            assert init_file.exists(), f"{package_dir.name} should have __init__.py"

    def test_tests_directory_structure(self, generated_project: Path) -> None:
        """Verify tests directory has correct structure."""
        tests_dir = generated_project / "tests"
        assert tests_dir.exists(), "tests directory should exist"

        # Should have at least one test file
        test_files = list(tests_dir.rglob("test_*.py"))
        assert len(test_files) >= 1, "tests should contain at least one test file"

    def test_no_hardcoded_author_info(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Verify no hardcoded author information in generated files."""
        config = {
            "project_name": "Test Project",
            "project_slug": "test_project",
            "author_name": "Custom Author",
            "author_email": "custom@example.com",
            "github_username": "customuser",
        }

        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, config)

        # Check pyproject.toml has custom author
        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()

        assert "Custom Author" in content, "Should contain custom author name"
        assert "custom@example.com" in content, "Should contain custom email"

        # Should NOT contain template author
        assert "Byron Williams" not in content, \
            "Should not contain template author name"
        assert "williaby" not in content, \
            "Should not contain template GitHub username"

    def test_github_workflows_generated(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Verify GitHub workflows are generated when enabled."""
        config = {
            "project_name": "Test Project",
            "project_slug": "test_project",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "include_github_actions": "yes",
        }

        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, config)

        workflows_dir = project_dir / ".github" / "workflows"
        assert workflows_dir.exists(), "Workflows directory should exist"

        # Should have at least CI workflow
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        assert len(workflow_files) >= 1, "Should have at least one workflow file"

    def test_optional_files_not_generated(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Verify optional files are not generated when disabled."""
        config = {
            "project_name": "Test Project",
            "project_slug": "test_project",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "include_cli": "no",
            "include_docker": "no",
            "include_nox": "no",
            "use_mkdocs": "no",
        }

        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, config)

        # These files should NOT exist
        assert not (project_dir / "Dockerfile").exists(), \
            "Dockerfile should not exist when Docker disabled"
        assert not (project_dir / "noxfile.py").exists(), \
            "noxfile.py should not exist when Nox disabled"
        assert not (project_dir / "mkdocs.yml").exists(), \
            "mkdocs.yml should not exist when MkDocs disabled"


class TestLicenseGeneration:
    """Tests for license file generation."""

    @pytest.mark.parametrize(
        "license_type",
        ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0"],
    )
    def test_license_file_generated(
        self, template_dir: Path, temp_dir: Path, license_type: str
    ) -> None:
        """Verify correct license file is generated."""
        config = {
            "project_name": "Test Project",
            "project_slug": "test_project",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "license": license_type,
        }

        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, config)

        # License should be in LICENSES directory (REUSE compliance)
        licenses_dir = project_dir / "LICENSES"
        if licenses_dir.exists():
            license_files = list(licenses_dir.glob(f"*{license_type}*"))
            assert len(license_files) >= 1, \
                f"License file for {license_type} should exist in LICENSES/"


class TestPythonVersionConfiguration:
    """Tests for Python version configuration."""

    @pytest.mark.parametrize(
        "python_version",
        ["3.10", "3.11", "3.12", "3.13"],
    )
    def test_python_version_in_pyproject(
        self, template_dir: Path, temp_dir: Path, python_version: str
    ) -> None:
        """Verify Python version is correctly set in pyproject.toml."""
        config = {
            "project_name": "Test Project",
            "project_slug": "test_project",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "python_version": python_version,
        }

        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, config)

        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()

        # Should specify the Python version
        assert python_version in content, \
            f"pyproject.toml should reference Python {python_version}"
