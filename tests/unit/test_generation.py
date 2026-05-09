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
        assert "typer" in content.lower() or "click" in content.lower(), (
            "CLI framework should be in dependencies"
        )

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
        assert "fastapi" in content.lower() or "flask" in content.lower(), (
            "API framework should be in dependencies"
        )
        assert "sqlalchemy" in content.lower(), (
            "Database framework should be in dependencies"
        )

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
        assert any(pkg in content.lower() for pkg in ml_packages), (
            "ML dependencies should be in pyproject.toml"
        )

    def test_frontend_generation(
        self, template_dir: Path, temp_dir: Path, frontend_config: dict[str, Any]
    ) -> None:
        """Test generation with React frontend configuration."""
        from tests.conftest import generate_project

        project_dir = generate_project(template_dir, temp_dir, frontend_config)
        assert project_dir.exists(), "Project directory should exist"

        # Check for frontend directory and key files
        frontend_dir = project_dir / "frontend"
        assert frontend_dir.exists(), "frontend directory should exist"
        assert (frontend_dir / "package.json").exists(), "package.json should exist"
        assert (frontend_dir / "vite.config.ts").exists(), "vite.config.ts should exist"
        assert (frontend_dir / "tsconfig.json").exists(), "tsconfig.json should exist"
        assert (frontend_dir / "Dockerfile").exists(), (
            "frontend Dockerfile should exist"
        )
        assert (frontend_dir / "nginx.conf").exists(), "nginx.conf should exist"

        # Check for React source files
        assert (frontend_dir / "src" / "App.tsx").exists(), "App.tsx should exist"
        assert (frontend_dir / "src" / "main.tsx").exists(), "main.tsx should exist"
        assert (frontend_dir / "src" / "hooks" / "useApi.ts").exists(), (
            "useApi.ts hook should exist"
        )
        assert (frontend_dir / "src" / "components" / "ApiStatus.tsx").exists(), (
            "ApiStatus.tsx component should exist"
        )

        # Check for test setup
        assert (frontend_dir / "src" / "test" / "App.test.tsx").exists(), (
            "App.test.tsx should exist"
        )
        assert (frontend_dir / "src" / "test" / "setup.ts").exists(), (
            "test setup.ts should exist"
        )

        # Check OpenAPI client generator script exists (include_openapi_client=yes)
        assert (project_dir / "scripts" / "generate-client.sh").exists(), (
            "generate-client.sh should exist when include_openapi_client=yes"
        )

        # Check Docker compose includes frontend
        docker_compose = project_dir / "docker-compose.yml"
        assert docker_compose.exists(), "docker-compose.yml should exist"
        content = docker_compose.read_text()
        assert "frontend" in content, (
            "docker-compose.yml should include frontend service"
        )

    def test_frontend_without_openapi_client(
        self,
        template_dir: Path,
        temp_dir: Path,
        frontend_no_openapi_config: dict[str, Any],
    ) -> None:
        """Test that generate-client.sh is removed when include_openapi_client=no."""
        from tests.conftest import generate_project

        project_dir = generate_project(
            template_dir, temp_dir, frontend_no_openapi_config
        )
        assert project_dir.exists(), "Project directory should exist"

        # Frontend should still exist
        assert (project_dir / "frontend").exists(), "frontend directory should exist"

        # But generate-client.sh should NOT exist
        assert not (project_dir / "scripts" / "generate-client.sh").exists(), (
            "generate-client.sh should NOT exist when include_openapi_client=no"
        )

    def test_no_frontend_generation(
        self, template_dir: Path, temp_dir: Path, minimal_config: dict[str, Any]
    ) -> None:
        """Test that frontend is not created when include_frontend=no (default)."""
        from tests.conftest import generate_project

        # minimal_config doesn't set include_frontend, so it defaults to "no"
        project_dir = generate_project(template_dir, temp_dir, minimal_config)
        assert project_dir.exists(), "Project directory should exist"

        # Frontend directory should NOT exist
        assert not (project_dir / "frontend").exists(), (
            "frontend directory should NOT exist when include_frontend=no"
        )

        # generate-client.sh should NOT exist
        assert not (project_dir / "scripts" / "generate-client.sh").exists(), (
            "generate-client.sh should NOT exist when include_frontend=no"
        )

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
        assert (project_dir / ".github" / "workflows").exists(), (
            "GitHub workflows should exist"
        )
        assert (project_dir / "docs").exists(), "docs directory should exist"

        # Verify frontend is included in full config
        assert (project_dir / "frontend").exists(), (
            "frontend directory should exist in full config"
        )


class TestConfigurationVariations:
    """Tests for various configuration combinations."""

    @pytest.mark.parametrize(
        "config_name",
        [
            "minimal",
            "cli-app",
            "api-service",
            "ml-project",
            "frontend-react",
            "full-featured",
            "supply-chain",
        ],
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

        assert result.returncode == 0, (
            f"Generation failed for {config_name}: {result.stderr}"
        )

        # Verify project directory exists
        with config_file.open() as f:
            config_data = json.load(f)
        project_slug = config_data["default_context"]["project_slug"]
        project_dir = output_dir / project_slug

        assert project_dir.exists(), f"Project directory should exist for {config_name}"
        assert (project_dir / "pyproject.toml").exists(), (
            f"pyproject.toml should exist for {config_name}"
        )


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
        assert result.returncode != 0, "Generation should fail with empty project name"


class TestWorkflowRendering:
    """Regression tests for render_workflow_templates() post-gen hook.

    Verifies that no {{ cookiecutter.xxx }} patterns survive into generated
    workflow files and that known config values are correctly substituted.
    """

    def test_no_unrendered_cookiecutter_variables(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Verify no {{ cookiecutter.xxx }} patterns remain after render_workflow_templates."""
        from tests.conftest import generate_project

        config: dict[str, Any] = {
            "project_name": "Workflow Render Test",
            "project_slug": "workflow_render_test",
            "project_short_description": "Regression test for workflow rendering",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "github_username": "testuser",
            "version": "0.1.0",
            "include_github_actions": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)
        workflows_dir = project_dir / ".github" / "workflows"
        assert workflows_dir.exists(), ".github/workflows should exist"

        unrendered: list[str] = []
        for wf_file in workflows_dir.glob("*.yml"):
            content = wf_file.read_text()
            if "{{ cookiecutter." in content or "{{cookiecutter." in content:
                unrendered.append(wf_file.name)

        assert not unrendered, (
            f"Unrendered cookiecutter variables found in workflows: {unrendered}"
        )

    def test_github_org_resolved_in_workflows(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Verify github_org_or_user resolves to the configured username in workflows."""
        from tests.conftest import generate_project

        config: dict[str, Any] = {
            "project_name": "Workflow Render Test",
            "project_slug": "workflow_render_test",
            "project_short_description": "Regression test for workflow rendering",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "github_username": "testuser",
            "version": "0.1.0",
            "include_github_actions": "yes",
        }
        project_dir = generate_project(template_dir, temp_dir, config)
        workflows_dir = project_dir / ".github" / "workflows"
        assert workflows_dir.exists(), ".github/workflows should exist"

        all_content = "".join(
            wf_file.read_text() for wf_file in workflows_dir.glob("*.yml")
        )
        assert "testuser" in all_content, (
            "Resolved github_org_or_user ('testuser') should appear in generated workflows"
        )


class TestDockerfileGeneration:
    """Regression tests for the Dockerfile dependency-stage README.md fix.

    pyproject.toml's [project] table references README.md via the readme field,
    so `uv sync --frozen` (which validates project metadata) requires README.md
    to be present in the build context. The Dockerfile must therefore COPY
    README.md before running uv sync, and .dockerignore must not exclude it.
    """

    @staticmethod
    def _generate_with_docker(template_dir: Path, temp_dir: Path) -> Path:
        from tests.conftest import generate_project

        config: dict[str, Any] = {
            "project_name": "Docker Regression",
            "project_slug": "docker_regression",
            "project_short_description": "Dockerfile README regression test",
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "github_username": "testuser",
            "version": "0.1.0",
            "include_docker": "yes",
        }
        return generate_project(template_dir, temp_dir, config)

    def test_dockerfile_dependency_stage_copies_readme(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Dockerfile must COPY README.md before the dep-only `uv sync` runs.

        pyproject.toml's [project] readme = "README.md" makes README.md a
        dependency of metadata resolution. uv sync reads metadata even with
        --no-install-project, so the file must be in the build context before
        the first uv sync invocation. Whether README.md ships in the same
        COPY layer as pyproject.toml or in a separate layer is an
        implementation detail; this test asserts the ordering invariant
        (README is copied before the first uv sync), not the layer count.
        """
        project_dir = self._generate_with_docker(template_dir, temp_dir)
        dockerfile = project_dir / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile should exist when include_docker=yes"

        lines = dockerfile.read_text(encoding="utf-8").splitlines()

        first_uv_sync_idx: int | None = None
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("RUN ") and "uv sync" in stripped:
                first_uv_sync_idx = idx
                break
        assert first_uv_sync_idx is not None, "Expected a `RUN uv sync ...` line"

        readme_copied_before_sync = any(
            line.strip().startswith("COPY ") and "README.md" in line
            for line in lines[:first_uv_sync_idx]
        )
        assert readme_copied_before_sync, (
            "Dependency-stage build must COPY README.md before the first "
            "`RUN uv sync` so uv can validate the [project] readme reference. "
            "Without it, every include_docker=yes build fails with "
            "`error: Failed to read metadata: README.md not found`."
        )

    def test_dockerignore_does_not_exclude_readme(
        self, template_dir: Path, temp_dir: Path
    ) -> None:
        """Generated .dockerignore must NOT exclude README.md."""
        project_dir = self._generate_with_docker(template_dir, temp_dir)
        dockerignore = project_dir / ".dockerignore"
        assert dockerignore.exists(), (
            ".dockerignore should exist when include_docker=yes"
        )

        # Strip comments and blank lines, then check for any pattern that would
        # exclude README.md.
        active_patterns = [
            line.strip()
            for line in dockerignore.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        bad_patterns = {"README.md", "README*", "*.md", "*"}
        offending = [p for p in active_patterns if p in bad_patterns]
        assert not offending, (
            f".dockerignore would exclude README.md via patterns: {offending}. "
            "README.md is required by Dockerfile during uv sync (see "
            "test_dockerfile_dependency_stage_copies_readme)."
        )
