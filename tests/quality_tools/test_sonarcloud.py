"""Tests for SonarCloud integration in generated projects."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest


if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.integration
class TestSonarCloudIntegration:
    """Tests for SonarCloud configuration and integration."""

    def test_sonarcloud_config_generated(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify SonarCloud config is generated when enabled."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_sonarcloud": "yes",
            "sonarcloud_organization": "test-org",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        sonar_config = project_dir / "sonar-project.properties"
        assert sonar_config.exists(), \
            "sonar-project.properties should exist when SonarCloud enabled"

        # Verify basic configuration
        content = sonar_config.read_text()
        assert "sonar.projectKey=" in content, \
            "Should have project key"
        assert "sonar.organization=test-org" in content, \
            "Should have organization"
        assert "sonar.sources=" in content, \
            "Should specify source directories"

    def test_sonarcloud_workflow_generated(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify SonarCloud workflow is generated when enabled."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_sonarcloud": "yes",
            "include_github_actions": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        workflows_dir = project_dir / ".github" / "workflows"
        sonar_workflow = workflows_dir / "sonarcloud.yml"

        assert sonar_workflow.exists(), \
            "SonarCloud workflow should exist when enabled"

        # Verify workflow content
        content = sonar_workflow.read_text()
        assert "SonarCloudScan" in content or "sonarcloud" in content.lower(), \
            "Workflow should reference SonarCloud"
        assert "SONAR_TOKEN" in content, \
            "Workflow should use SONAR_TOKEN secret"

    def test_sonarcloud_not_generated_when_disabled(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify SonarCloud files are not generated when disabled."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_sonarcloud": "no",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        sonar_config = project_dir / "sonar-project.properties"
        assert not sonar_config.exists(), \
            "sonar-project.properties should not exist when SonarCloud disabled"

    @pytest.mark.slow
    def test_sonar_scanner_config_valid(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify sonar-project.properties is valid."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_sonarcloud": "yes",
            "sonarcloud_organization": "test-org",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        sonar_config = project_dir / "sonar-project.properties"
        content = sonar_config.read_text()

        # Validate required properties
        required_props = [
            "sonar.projectKey=",
            "sonar.organization=",
            "sonar.sources=",
            "sonar.python.version=",
        ]

        for prop in required_props:
            assert prop in content, \
                f"sonar-project.properties should have {prop}"

        # Validate sources point to actual directories
        # Extract sources value
        for line in content.split("\n"):
            if line.startswith("sonar.sources="):
                sources = line.split("=", 1)[1].strip()
                # Should reference src directory
                assert "src" in sources, \
                    "sonar.sources should include src directory"

    @pytest.mark.slow
    def test_sonarcloud_with_coverage(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify SonarCloud config includes coverage when CodeCov enabled."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "include_sonarcloud": "yes",
            "include_codecov": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)

        sonar_config = project_dir / "sonar-project.properties"
        content = sonar_config.read_text()

        # Should configure coverage
        assert "sonar.python.coverage" in content or "coverage.xml" in content, \
            "SonarCloud config should reference coverage when CodeCov enabled"
