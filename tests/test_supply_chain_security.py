"""Tests for supply chain security feature generation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest


if TYPE_CHECKING:
    from pathlib import Path


class TestSupplyChainSecurityEnabled:
    """Tests for template generation with supply chain security enabled."""

    @pytest.fixture
    def supply_chain_config(self, minimal_config: dict[str, Any]) -> dict[str, Any]:
        """Provide configuration with supply chain security enabled."""
        return {
            **minimal_config,
            "project_name": "Supply Chain Test",
            "project_slug": "supply_chain_test",
            "include_supply_chain_security": "yes",
            "include_github_actions": "yes",
            "infisical_domain": "https://secrets.example.com",
            "gcp_project_id": "test-gcp-project",
            "gcp_artifact_registry": "python-libs",
            "gcp_region": "us-central1",
        }

    def test_infisical_json_created(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify .infisical.json is created when supply chain security enabled."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        infisical_file = project_dir / ".infisical.json"
        assert infisical_file.exists(), ".infisical.json should exist"

        # Verify it's valid JSON with expected structure
        content = json.loads(infisical_file.read_text())
        assert "workspaceId" in content, ".infisical.json should have workspaceId"
        assert "defaultEnvironment" in content, ".infisical.json should have defaultEnvironment"
        assert "gitBranchToEnvironmentMapping" in content, (
            ".infisical.json should have gitBranchToEnvironmentMapping"
        )

        # Verify branch mappings
        mappings = content["gitBranchToEnvironmentMapping"]
        assert mappings.get("main") == "prod", "main branch should map to prod"
        assert mappings.get("develop") == "staging", "develop branch should map to staging"
        assert mappings.get("*") == "dev", "default (*) should map to dev"

    def test_setup_supply_chain_script_created(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify setup-supply-chain.sh script is created."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        script_file = project_dir / "scripts" / "setup-supply-chain.sh"
        assert script_file.exists(), "setup-supply-chain.sh should exist"

        content = script_file.read_text()

        # Verify script contains key functionality
        assert "gcloud" in content, "Script should reference gcloud CLI"
        assert "Artifact Registry" in content or "artifactregistry" in content.lower(), (
            "Script should reference Artifact Registry"
        )
        assert "Infisical" in content or "infisical" in content.lower(), (
            "Script should reference Infisical"
        )

    def test_dependency_review_workflow_created(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify dependency-review.yml workflow is created."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        workflow_file = project_dir / ".github" / "workflows" / "dependency-review.yml"
        assert workflow_file.exists(), "dependency-review.yml should exist"

        content = workflow_file.read_text()

        # Verify workflow structure
        assert "Dependency Review" in content, "Workflow should have Dependency Review name"
        assert "pull_request" in content, "Workflow should trigger on pull requests"
        assert "dependency-review-action" in content, "Workflow should use dependency-review-action"
        assert "fail-on-severity" in content, "Workflow should have severity configuration"

    def test_pyproject_has_uv_index_config(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify pyproject.toml has UV index configuration."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()

        # Verify Assured OSS index
        assert "assured-oss" in content, "pyproject.toml should have assured-oss index"
        assert "cloud-aoss" in content, "pyproject.toml should reference cloud-aoss URL"

        # Verify internal registry index
        assert "internal" in content.lower(), "pyproject.toml should have internal index"

        # Verify the GCP configuration values are rendered
        assert supply_chain_config["gcp_project_id"] in content, (
            "pyproject.toml should contain GCP project ID"
        )
        assert supply_chain_config["gcp_region"] in content, (
            "pyproject.toml should contain GCP region"
        )

        # Verify PyPI fallback
        assert "pypi" in content.lower(), "pyproject.toml should have PyPI fallback"

    def test_pyproject_has_supply_chain_dependencies(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify pyproject.toml has supply-chain optional dependency group."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()

        # Verify supply-chain optional dependency group
        assert "supply-chain" in content, (
            "pyproject.toml should have supply-chain optional dependencies"
        )

        # Verify key supply chain tools are included
        assert "cyclonedx-bom" in content, "Should include cyclonedx-bom"
        assert "pip-audit" in content, "Should include pip-audit"

    def test_env_example_has_supply_chain_vars(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify .env.example has supply chain configuration variables."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        env_example = project_dir / ".env.example"
        content = env_example.read_text()

        # Verify supply chain section header
        assert "Supply Chain Security" in content, (
            ".env.example should have Supply Chain Security section"
        )

        # Verify Infisical documentation
        assert "Infisical" in content, ".env.example should mention Infisical"

        # Verify GCP configuration
        assert "GOOGLE_CLOUD_PROJECT" in content, ".env.example should have GOOGLE_CLOUD_PROJECT"
        assert "GCP_ARTIFACT_REGISTRY" in content, ".env.example should have GCP_ARTIFACT_REGISTRY"

    def test_ci_workflow_has_infisical_integration(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify CI workflow has Infisical secrets integration."""
        from tests.conftest import generate_project

        # Also disable org workflows to test standalone CI
        config = {**supply_chain_config, "use_org_workflows": "no"}
        project_dir = generate_project(template_dir, temp_dir, config)

        ci_workflow = project_dir / ".github" / "workflows" / "ci.yml"
        assert ci_workflow.exists(), "ci.yml should exist"

        content = ci_workflow.read_text()

        # Verify Infisical action
        assert "Infisical" in content or "infisical" in content.lower(), (
            "CI workflow should reference Infisical"
        )
        assert "secrets-action" in content or "INFISICAL" in content, (
            "CI workflow should use Infisical secrets action"
        )

    def test_readme_has_supply_chain_section(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify README has supply chain security documentation."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        readme = project_dir / "README.md"
        content = readme.read_text()

        # Verify supply chain section
        assert "Supply Chain Security" in content, (
            "README should have Supply Chain Security section"
        )
        assert "Assured OSS" in content or "SLSA" in content, (
            "README should mention Assured OSS or SLSA"
        )
        assert "Infisical" in content, "README should mention Infisical"
        assert "setup-supply-chain.sh" in content, "README should reference setup script"

    def test_contributing_has_dependency_guidance(
        self, template_dir: Path, temp_dir: Path, supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify CONTRIBUTING.md has dependency management guidance."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, supply_chain_config)

        contributing = project_dir / "CONTRIBUTING.md"
        content = contributing.read_text()

        # Verify dependency management section
        assert "Dependency Management" in content, (
            "CONTRIBUTING should have Dependency Management section"
        )
        assert "Package Index Priority" in content or "secure package indexes" in content, (
            "CONTRIBUTING should explain package index priority"
        )


class TestSupplyChainSecurityDisabled:
    """Tests for template generation with supply chain security disabled."""

    @pytest.fixture
    def no_supply_chain_config(self, minimal_config: dict[str, Any]) -> dict[str, Any]:
        """Provide configuration with supply chain security disabled."""
        return {
            **minimal_config,
            "project_name": "No Supply Chain Test",
            "project_slug": "no_supply_chain_test",
            "include_supply_chain_security": "no",
            "include_github_actions": "yes",
        }

    def test_infisical_json_not_created(
        self, template_dir: Path, temp_dir: Path, no_supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify .infisical.json is NOT created when supply chain security disabled."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, no_supply_chain_config)

        infisical_file = project_dir / ".infisical.json"
        assert not infisical_file.exists(), (
            ".infisical.json should NOT exist when supply chain disabled"
        )

    def test_setup_script_not_created(
        self, template_dir: Path, temp_dir: Path, no_supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify setup-supply-chain.sh is NOT created when disabled."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, no_supply_chain_config)

        script_file = project_dir / "scripts" / "setup-supply-chain.sh"
        assert not script_file.exists(), (
            "setup-supply-chain.sh should NOT exist when supply chain disabled"
        )

    def test_dependency_review_workflow_not_created(
        self, template_dir: Path, temp_dir: Path, no_supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify dependency-review.yml is NOT created when disabled."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, no_supply_chain_config)

        workflow_file = project_dir / ".github" / "workflows" / "dependency-review.yml"
        assert not workflow_file.exists(), (
            "dependency-review.yml should NOT exist when supply chain disabled"
        )

    def test_pyproject_has_no_uv_indexes(
        self, template_dir: Path, temp_dir: Path, no_supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify pyproject.toml does NOT have UV index configuration."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, no_supply_chain_config)

        pyproject = project_dir / "pyproject.toml"
        content = pyproject.read_text()

        # Should NOT have [[tool.uv.index]] sections for Assured OSS
        assert "[[tool.uv.index]]" not in content or 'name = "assured-oss"' not in content, (
            "pyproject.toml should NOT have assured-oss index configuration when disabled"
        )

        # Should NOT have cloud-aoss URL in index configuration
        assert "us-python.pkg.dev/cloud-aoss" not in content, (
            "pyproject.toml should NOT have cloud-aoss URL when disabled"
        )

        # Should NOT have supply-chain dependency group as optional dependency section
        # Note: Comments about Assured OSS in dev dependencies may still exist
        assert "[tool.uv.sources]" not in content or "internal-package" not in content, (
            "pyproject.toml should NOT have uv.sources section when disabled"
        )

    def test_env_example_has_minimal_gcp_section(
        self, template_dir: Path, temp_dir: Path, no_supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify .env.example has minimal GCP configuration when disabled."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, no_supply_chain_config)

        env_example = project_dir / ".env.example"
        content = env_example.read_text()

        # Should NOT have full supply chain section
        assert "Supply Chain Security Configuration" not in content, (
            ".env.example should NOT have supply chain section when disabled"
        )

        # Should NOT have Infisical references
        assert "Infisical" not in content or "infisical" not in content.lower(), (
            ".env.example should NOT mention Infisical when disabled"
        )

    def test_readme_has_alternative_section(
        self, template_dir: Path, temp_dir: Path, no_supply_chain_config: dict[str, Any]
    ) -> None:
        """Verify README has alternative/minimal section when supply chain disabled."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, no_supply_chain_config)

        readme = project_dir / "README.md"
        content = readme.read_text()

        # Should NOT have full supply chain section
        assert (
            "Supply Chain Security" not in content or "Enabling Supply Chain Security" in content
        ), "README should not have full Supply Chain section when disabled"


class TestSupplyChainSecurityDefaultBehavior:
    """Tests for supply chain security default behavior."""

    def test_supply_chain_defaults_to_yes(self, template_dir: Path) -> None:
        """Verify supply chain security defaults to yes in cookiecutter.json."""
        cookiecutter_json = template_dir / "cookiecutter.json"
        with cookiecutter_json.open() as f:
            data = json.load(f)

        # Check the default value
        supply_chain_setting = data.get("include_supply_chain_security")
        if isinstance(supply_chain_setting, list):
            # First item is the default
            assert supply_chain_setting[0] == "yes", (
                "include_supply_chain_security should default to yes"
            )
        else:
            assert supply_chain_setting == "yes", (
                "include_supply_chain_security should default to yes"
            )

    def test_default_generation_has_supply_chain(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify default generation includes supply chain security."""
        from tests.conftest import generate_project

        # Don't explicitly set include_supply_chain_security - use default
        project_dir = generate_project(template_dir, temp_dir, minimal_config)

        # Should have supply chain files by default
        infisical_file = project_dir / ".infisical.json"
        assert infisical_file.exists(), (
            ".infisical.json should exist by default (supply chain enabled)"
        )


class TestSupplyChainSecurityFileContent:
    """Tests for validating supply chain file content details."""

    @pytest.fixture
    def supply_chain_project(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> Path:
        """Generate a project with supply chain security for content tests."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "project_slug": "content_test",
            "include_supply_chain_security": "yes",
            "include_github_actions": "yes",
            "gcp_project_id": "my-gcp-project",
            "gcp_artifact_registry": "my-python-libs",
            "gcp_region": "us-east1",
            "infisical_domain": "https://infisical.mycompany.com",
        }
        return generate_project(template_dir, temp_dir, config)

    def test_dependency_review_license_config(self, supply_chain_project: Path) -> None:
        """Verify dependency review workflow has proper license configuration."""
        workflow = supply_chain_project / ".github" / "workflows" / "dependency-review.yml"
        content = workflow.read_text()

        # Should deny copyleft licenses
        assert "GPL-3.0" in content, "Should deny GPL-3.0"
        assert "AGPL-3.0" in content, "Should deny AGPL-3.0"

        # Should allow permissive licenses
        assert "MIT" in content, "Should allow MIT"
        assert "Apache-2.0" in content, "Should allow Apache-2.0"

    def test_gcp_variables_rendered_in_pyproject(self, supply_chain_project: Path) -> None:
        """Verify GCP variables are properly rendered in pyproject.toml."""
        pyproject = supply_chain_project / "pyproject.toml"
        content = pyproject.read_text()

        # Check GCP config values are rendered
        assert "my-gcp-project" in content, "GCP project ID should be rendered"
        assert "my-python-libs" in content, "Artifact registry name should be rendered"
        assert "us-east1" in content, "GCP region should be rendered"

    def test_env_example_has_gcp_variables(self, supply_chain_project: Path) -> None:
        """Verify .env.example has rendered GCP variables."""
        env_example = supply_chain_project / ".env.example"
        content = env_example.read_text()

        # Check GCP variables
        assert "my-gcp-project" in content, "GCP project ID should be in .env.example"
        assert "my-python-libs" in content, "Artifact registry should be in .env.example"
        assert "us-east1" in content, "GCP region should be in .env.example"

    def test_no_jinja_variables_in_supply_chain_files(self, supply_chain_project: Path) -> None:
        """Verify no unreplaced Jinja2 variables in supply chain files."""
        import re

        jinja_pattern = re.compile(r"\{\{.*?cookiecutter.*?\}\}|\{%.*?%\}")

        files_to_check = [
            supply_chain_project / ".infisical.json",
            supply_chain_project / "scripts" / "setup-supply-chain.sh",
            supply_chain_project / ".github" / "workflows" / "dependency-review.yml",
        ]

        for file_path in files_to_check:
            if file_path.exists():
                content = file_path.read_text()
                matches = jinja_pattern.findall(content)
                assert not matches, (
                    f"Found unreplaced Jinja2 variables in {file_path.name}: {matches}"
                )


class TestSupplyChainWithOtherFeatures:
    """Tests for supply chain security interaction with other features."""

    def test_supply_chain_with_docker(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify supply chain works with Docker enabled."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "project_slug": "docker_supply_chain",
            "include_supply_chain_security": "yes",
            "include_docker": "yes",
            "include_github_actions": "yes",
        }

        project_dir = generate_project(template_dir, temp_dir, config)

        # Both Docker and supply chain files should exist
        assert (project_dir / "Dockerfile").exists(), "Dockerfile should exist"
        assert (project_dir / ".infisical.json").exists(), ".infisical.json should exist"

    def test_supply_chain_with_frontend(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify supply chain works with React frontend enabled."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "project_slug": "frontend_supply_chain",
            "include_supply_chain_security": "yes",
            "include_frontend": "react",
            "include_api_framework": "yes",
            "include_github_actions": "yes",
        }

        project_dir = generate_project(template_dir, temp_dir, config)

        # Both frontend and supply chain files should exist
        assert (project_dir / "frontend").exists(), "frontend directory should exist"
        assert (project_dir / ".infisical.json").exists(), ".infisical.json should exist"

    def test_supply_chain_with_codecov_sonarcloud(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Verify supply chain works with Codecov and SonarCloud."""
        from tests.conftest import generate_project

        config = {
            **minimal_config,
            "project_slug": "quality_supply_chain",
            "include_supply_chain_security": "yes",
            "include_codecov": "yes",
            "include_sonarcloud": "yes",
            "include_github_actions": "yes",
        }

        project_dir = generate_project(template_dir, temp_dir, config)

        # All features should coexist
        assert (project_dir / ".infisical.json").exists(), ".infisical.json should exist"
        assert (project_dir / "codecov.yml").exists(), "codecov.yml should exist"
        assert (project_dir / "sonar-project.properties").exists(), (
            "sonar-project.properties should exist"
        )
