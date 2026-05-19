#!/usr/bin/env python3
"""Post-generation hook for cookiecutter Python template.

Performs cleanup and setup tasks after project generation.
Runs after all files have been created.
"""

import os
import re
import shutil
import subprocess  # nosec B404
import sys
from datetime import datetime
from pathlib import Path


# Module-level constants for repeated cookiecutter feature-flag references.
# These are rendered ONCE by Jinja2 at cookiecutter-generation time and then
# used throughout the post-gen hook. Extracting them satisfies SonarCloud
# python:S1192 (duplicated literal) and centralizes the source of truth.
INCLUDE_DOCKER = "{{ cookiecutter.include_docker }}"
INCLUDE_FRONTEND = "{{ cookiecutter.include_frontend }}"
INCLUDE_SUPPLY_CHAIN_SECURITY = "{{ cookiecutter.include_supply_chain_security }}"


def remove_file(filepath: Path) -> None:
    """Remove a file if it exists.

    Args:
        filepath: Path to the file to remove
    """
    if filepath.exists():
        filepath.unlink()
        print(f"  ✓ Removed: {filepath}")


def remove_dir(dirpath: Path) -> None:
    """Remove a directory if it exists.

    Args:
        dirpath: Path to the directory to remove
    """
    if dirpath.exists():
        shutil.rmtree(dirpath)
        print(f"  ✓ Removed: {dirpath}/")


def make_executable(filepath: Path) -> None:
    """Make a file executable.

    Args:
        filepath: Path to the file to make executable
    """
    if filepath.exists():
        filepath.chmod(filepath.stat().st_mode | 0o111)


def run_command(cmd: list[str], check: bool = True) -> bool:
    """Run a shell command.

    Args:
        cmd: Command and arguments as list
        check: Whether to check return code

    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.run(cmd, check=check, capture_output=True, text=True)  # nosec B603
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        # Command not found (e.g., pre-commit not installed)
        return False
    except OSError:
        # Other OS-level errors (permission denied, etc.)
        return False
    else:
        return True


def maybe_run_branch_protection(flag: str, remote_url: str) -> bool:
    """Invoke setup_github_protection.py if all preconditions are met.

    Preconditions:
        1. flag == "yes" (the cookiecutter auto_setup_branch_protection value)
        2. GITHUB_TOKEN environment variable is set and non-empty
        3. remote_url is non-empty (project has a git remote)

    The invocation is non-fatal. Any failure produces a stdout warning
    and the post-gen hook continues.

    Args:
        flag: The cookiecutter auto_setup_branch_protection value.
        remote_url: The git remote.origin.url value (empty string if none).

    Returns:
        True if the script was invoked and exited 0, False otherwise.
    """
    if flag != "yes":
        return False
    if not os.environ.get("GITHUB_TOKEN"):
        return False
    if not remote_url:
        return False

    script = Path("scripts") / "setup_github_protection.py"
    if not script.exists():
        print(f"  Warning: {script} not found; skipping auto branch protection.")
        return False

    print("  * Auto-configuring branch protection...")
    success = run_command(["uv", "run", "python", str(script)], check=False)
    if success:
        print("  Branch protection configured.")
        return True
    print(
        "  Warning: Branch protection auto-run failed; "
        "re-run manually with: "
        "GITHUB_TOKEN=ghp_xxx uv run python scripts/setup_github_protection.py"
    )
    return False


def _cleanup_documentation_files() -> None:
    """Remove documentation files based on cookiecutter choices."""
    # Remove CLI if not needed
    if "{{ cookiecutter.include_cli }}" == "no":
        remove_file(Path("src/{{ cookiecutter.project_slug }}/cli.py"))

    # Remove MkDocs if not needed
    if "{{ cookiecutter.use_mkdocs }}" == "no":
        remove_file(Path("mkdocs.yml"))
        remove_dir(Path("docs"))
        remove_file(Path("tools/validate_front_matter.py"))
        remove_dir(Path("tools/frontmatter_contract"))

    # Remove CODE_OF_CONDUCT if not needed
    if "{{ cookiecutter.include_code_of_conduct }}" == "no":
        remove_file(Path("CODE_OF_CONDUCT.md"))

    # Remove SECURITY if not needed
    if "{{ cookiecutter.include_security_policy }}" == "no":
        remove_file(Path("SECURITY.md"))

    # Remove .editorconfig if not needed
    if "{{ cookiecutter.include_editorconfig }}" == "no":
        remove_file(Path(".editorconfig"))

    # Remove CONTRIBUTING if not needed
    if "{{ cookiecutter.include_contributing_guide }}" == "no":
        remove_file(Path("CONTRIBUTING.md"))


def _cleanup_tooling_files() -> None:
    """Remove tooling and integration files based on cookiecutter choices."""
    # Remove Nox if not needed
    if "{{ cookiecutter.include_nox }}" == "no":
        remove_file(Path("noxfile.py"))

    # Remove pre-commit if not needed
    if "{{ cookiecutter.use_pre_commit }}" == "no":
        remove_file(Path(".pre-commit-config.yaml"))

    # Remove REUSE if not needed
    if "{{ cookiecutter.use_reuse_licensing }}" == "no":
        remove_file(Path("REUSE.toml"))
        remove_dir(Path("LICENSES"))
        remove_file(Path(".github/workflows/reuse.yml"))

    # Remove codecov config and workflow if not needed
    if "{{ cookiecutter.include_codecov }}" == "no":
        remove_file(Path("codecov.yml"))
        remove_file(Path(".github/workflows/codecov.yml"))

    # Remove SonarCloud if not needed
    if "{{ cookiecutter.include_sonarcloud }}" == "no":
        remove_file(Path("sonar-project.properties"))
        remove_file(Path(".github/workflows/sonarcloud.yml"))

    # Remove renovate if not needed
    if "{{ cookiecutter.include_renovate }}" == "no":
        remove_file(Path("renovate.json"))

    # Remove CodeRabbit if not needed
    if "{{ cookiecutter.include_coderabbit }}" == "no":
        remove_file(Path(".coderabbit.yaml"))

    # Remove Docker files if not needed
    if INCLUDE_DOCKER == "no":
        remove_file(Path("Dockerfile"))
        remove_file(Path("docker-compose.yml"))
        remove_file(Path("docker-compose.prod.yml"))
        remove_file(Path(".dockerignore"))
        remove_file(Path(".github/workflows/container-security.yml"))


def _cleanup_api_and_backend_files() -> None:
    """Remove API, backend, and service files based on cookiecutter choices."""
    # Remove health check endpoints if not needed or if no API framework
    if (
        "{{ cookiecutter.include_health_checks }}" == "no"
        or "{{ cookiecutter.include_api_framework }}" == "no"
    ):
        remove_file(Path("src/{{ cookiecutter.project_slug }}/api/health.py"))
        # Remove api directory if empty
        api_dir = Path("src/{{ cookiecutter.project_slug }}/api")
        if api_dir.exists() and not any(
            f.name not in {"__pycache__", "__init__.py"} for f in api_dir.iterdir()
        ):
            remove_dir(api_dir)

    # Remove API middleware if API framework not included
    if "{{ cookiecutter.include_api_framework }}" == "no":
        remove_file(Path("src/{{ cookiecutter.project_slug }}/middleware/security.py"))
        remove_file(
            Path("src/{{ cookiecutter.project_slug }}/middleware/correlation.py")
        )
        # Remove middleware directory if only __init__.py / __pycache__ remain
        middleware_dir = Path("src/{{ cookiecutter.project_slug }}/middleware")
        if middleware_dir.exists() and not any(
            f.name not in {"__pycache__", "__init__.py"}
            for f in middleware_dir.iterdir()
        ):
            remove_dir(middleware_dir)

    # Remove background job files if not needed
    if "{{ cookiecutter.include_background_jobs }}" == "no":
        remove_dir(Path("src/{{ cookiecutter.project_slug }}/jobs"))

    # Remove caching utilities if not needed
    if "{{ cookiecutter.include_caching }}" == "no":
        remove_file(Path("src/{{ cookiecutter.project_slug }}/core/cache.py"))

    # Remove Sentry monitoring if not needed
    if "{{ cookiecutter.include_sentry }}" == "no":
        remove_file(Path("src/{{ cookiecutter.project_slug }}/core/sentry.py"))


def _cleanup_frontend_files() -> None:
    """Remove frontend files based on cookiecutter choices."""
    # Remove load testing files if not needed
    if "{{ cookiecutter.include_load_testing }}" == "no":
        remove_dir(Path("tests/load"))

    # Remove frontend if not needed
    if INCLUDE_FRONTEND == "no":
        remove_dir(Path("frontend"))
        remove_file(Path("scripts/generate-client.sh"))
    else:
        # Frontend is enabled
        # Handle OpenAPI client generator script
        if "{{ cookiecutter.include_openapi_client }}" == "yes":
            make_executable(Path("scripts/generate-client.sh"))
        else:
            remove_file(Path("scripts/generate-client.sh"))

        # Warn if frontend enabled without API framework
        if "{{ cookiecutter.include_api_framework }}" == "no":
            print("  ⚠ Warning: Frontend enabled without API framework")
            print("    Consider enabling include_api_framework for full-stack support")


def _cleanup_workflow_files() -> None:
    """Remove workflow and CI files based on cookiecutter choices.

    Must be called last since it may remove .github/ entirely.
    """
    # Remove fuzzing files and workflow if not needed
    if "{{ cookiecutter.include_fuzzing }}" == "no":
        remove_file(Path(".github/workflows/cifuzzy.yml"))
        remove_dir(Path(".clusterfuzzlite"))
        remove_dir(Path("fuzz"))

    # Remove supply chain security files if not needed
    if INCLUDE_SUPPLY_CHAIN_SECURITY == "no":
        remove_file(Path(".infisical.json"))
        remove_file(Path("scripts/setup-supply-chain.sh"))
        remove_file(Path(".github/workflows/dependency-review.yml"))

    # Remove MkDocs workflow if MkDocs not used (before removing all of .github/)
    if "{{ cookiecutter.use_mkdocs }}" == "no":
        remove_file(Path(".github/workflows/docs.yml"))

    # Remove GitHub Actions workflows if not needed
    if "{{ cookiecutter.include_github_actions }}" == "no":
        remove_dir(Path(".github/workflows"))
        remove_dir(Path(".github"))


def cleanup_conditional_files() -> None:
    """Remove files based on cookiecutter choices."""
    print("\n🧹 Cleaning up conditional files...")
    _cleanup_documentation_files()
    _cleanup_tooling_files()
    _cleanup_api_and_backend_files()
    _cleanup_frontend_files()
    _cleanup_workflow_files()  # Must be last: may remove .github/ entirely
    # Note: Security scanning workflows (security-analysis.yml) are always included


def mark_scripts_executable() -> None:
    """Ensure all shebang scripts have executable permissions.

    Cookiecutter does not always preserve git file modes, so this
    explicitly sets 0o755 on every script that carries a shebang line.
    Must run after cleanup so removed files are not targeted.
    """
    executable_paths = [
        "scripts/check_fips_compatibility.py",
        "scripts/check_orphaned_files.py",
        "scripts/check_quality_gate.py",
        "scripts/check_type_hints.py",
        "scripts/cleanup_conditional_files.py",
        "scripts/cruft-update.sh",
        "scripts/generate-client.sh",
        "scripts/generate_requirements.sh",
        "scripts/setup-supply-chain.sh",
        "scripts/setup_github_protection.py",
        "scripts/update-claude-standards.sh",
        "scripts/validate_assuredoss.py",
        "tools/validate_front_matter.py",
        "fuzz/fuzz_input_validation.py",
        ".claude/skills/project-planning/scripts/validate-planning-docs.py",
    ]
    for path_str in executable_paths:
        make_executable(Path(path_str))


def initialize_git() -> None:
    """Initialize git repository with main as default branch."""
    # #ASSUME: External Resources: git is installed and on PATH.
    # #VERIFY: run_command catches FileNotFoundError and returns False, falling
    #          through to the "git not found" message below.
    print("\n🔧 Initializing Git repository...")

    if run_command(["git", "init", "-b", "main"], check=False):
        print("  ✓ Git repository initialized (default branch: main)")

        # Create initial commit
        if run_command(["git", "add", "."], check=False) and run_command(
            ["git", "commit", "-m", "Initial commit from cookiecutter template"],
            check=False,
        ):
            print("  ✓ Initial commit created")
    else:
        print("  ⚠ Git not found - skipping git initialization")


def setup_claude_subtree() -> None:
    """Add the standard .claude repo as a git subtree."""
    print("\n🔧 Setting up Claude standards subtree...")

    # Check if git is initialized
    if not Path(".git").exists():
        print("  ⚠ Git not initialized - skipping Claude standards setup")
        print("    Run 'git init' and then manually add the subtree:")
        print("    git subtree add --prefix .claude/standard \\")
        print("      https://github.com/williaby/.claude.git main --squash")
        return

    # Check if user wants to add the subtree
    try:
        response = (
            input("\n  Add standard Claude configuration via git subtree? (Y/n): ")
            .strip()
            .lower()
        )
    except (EOFError, KeyboardInterrupt):
        print("\n  Skipping Claude standards setup.")
        return

    # Default to yes if empty response
    if response in ["", "y", "yes"]:
        claude_repo = "https://github.com/williaby/.claude.git"
        subtree_prefix = ".claude/standard"

        print(f"\n  📥 Adding Claude standards from {claude_repo}...")

        # Add the subtree
        if run_command(
            [
                "git",
                "subtree",
                "add",
                "--prefix",
                subtree_prefix,
                claude_repo,
                "main",
                "--squash",
            ],
            check=False,
        ):
            print(f"  ✓ Claude standards added to {subtree_prefix}/")

            # Check what was added
            standard_dir = Path(subtree_prefix)
            if (standard_dir / "CLAUDE.md").exists():
                print("  ✓ Standard CLAUDE.md available")
            if (standard_dir / "commands").exists():
                print("  ✓ Standard commands available")
            if (standard_dir / "skills").exists():
                print("  ✓ Standard skills available")
            if (standard_dir / "agents").exists():
                print("  ✓ Standard agents available")
            if (standard_dir / "standards").exists():
                print(
                    "  ✓ Development standards available (git, python, security, linting)"
                )

            print("\n  ✅ Claude standards integrated successfully!")
            print("\n  To update standards later, run:")
            print("     ./scripts/update-claude-standards.sh")
        else:
            print("  ⚠ Failed to add Claude standards subtree")
            print("    You can manually add it later with:")
            print(f"     git subtree add --prefix {subtree_prefix} \\")
            print(f"       {claude_repo} main --squash")
    else:
        print("\n  ℹ Skipping Claude standards setup.")  # noqa: RUF001
        print("    You can add it later with:")
        print("     git subtree add --prefix .claude/standard \\")
        print("       https://github.com/williaby/.claude.git main --squash")


def setup_pre_commit() -> None:
    """Install pre-commit hooks if pre-commit is available."""
    if "{{ cookiecutter.use_pre_commit }}" == "no":
        return

    print("\n🔧 Setting up pre-commit hooks...")

    # Check if pre-commit is installed
    if run_command(["pre-commit", "--version"], check=False):
        if run_command(["pre-commit", "install"], check=False):
            print("  ✓ Pre-commit hooks installed")
        else:
            print("  ⚠ Failed to install pre-commit hooks")
    else:
        print(
            "  ⚠ pre-commit not found - run 'uv sync' and 'uv run pre-commit install'"
        )


def create_initial_directories() -> None:
    """Create additional directories that may be needed."""
    print("\n📁 Creating additional directories...")

    directories = [
        "logs",
        "data",
        "scripts",
        "configs",
    ]

    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        # Create .gitkeep to track empty directories
        (dir_path / ".gitkeep").touch()

    print(f"  ✓ Created {len(directories)} directories")


def render_workflow_templates() -> None:
    """Render GitHub workflow templates with cookiecutter variables.

    This fixes the issue where workflows from external repositories contain
    unrendered Jinja2 variables. We replace them with actual cookiecutter values.
    """
    # #ASSUME: External Resources: workflow files exist under .github/workflows
    #          and are UTF-8 encoded.
    # #VERIFY: read_text/write_text use encoding="utf-8" explicitly below.
    #
    # #ASSUME: Data Integrity: every {% raw %}{{ cookiecutter.X }}{% endraw %} placeholder rendered
    #          here corresponds to a key defined in cookiecutter.json.
    # #VERIFY: post-gen test scans all rendered workflows for surviving
    #          {% raw %}{{ cookiecutter.{% endraw %} patterns; missing keys leave the placeholder
    #          verbatim and the test catches it.
    print("\n🔧 Rendering GitHub workflow templates...")

    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("  ⚠ No workflows directory found - skipping template rendering")
        return

    # Cookiecutter context variables
    context = {
        "project_name": "{{ cookiecutter.project_name }}",
        "project_slug": "{{ cookiecutter.project_slug }}",
        "python_version": "{{ cookiecutter.python_version }}",
        "pypi_package_name": "{{ cookiecutter.pypi_package_name }}",
        "github_org_or_user": "{{ cookiecutter.github_org_or_user }}",
        "author_name": "{{ cookiecutter.author_name }}",
        "author_email": "{{ cookiecutter.author_email }}",
        "version": "{{ cookiecutter.version }}",
        # Feature flags and integration settings referenced in workflow templates
        "code_coverage_target": "{{ cookiecutter.code_coverage_target }}",
        "frontend_package_manager": "{{ cookiecutter.frontend_package_manager }}",
        "include_codecov": "{{ cookiecutter.include_codecov }}",
        "include_docker": INCLUDE_DOCKER,
        "include_frontend": INCLUDE_FRONTEND,
        "include_fuzzing": "{{ cookiecutter.include_fuzzing }}",
        "include_github_actions": "{{ cookiecutter.include_github_actions }}",
        "include_semantic_release": "{{ cookiecutter.include_semantic_release }}",
        "include_sonarcloud": "{{ cookiecutter.include_sonarcloud }}",
        "include_supply_chain_security": INCLUDE_SUPPLY_CHAIN_SECURITY,
        "infisical_domain": "{{ cookiecutter.infisical_domain }}",
        "license": "{{ cookiecutter.license }}",
        "node_version": "{{ cookiecutter.node_version }}",
        "sonarcloud_organization": "{{ cookiecutter.sonarcloud_organization }}",
        "use_mkdocs": "{{ cookiecutter.use_mkdocs }}",
        "use_org_workflows": "{{ cookiecutter.use_org_workflows }}",
        "use_reuse_licensing": "{{ cookiecutter.use_reuse_licensing }}",
    }

    rendered_count = 0
    workflow_files = list(workflows_dir.glob("*.yml")) + list(
        workflows_dir.glob("*.yaml")
    )
    workflow_files.append(workflows_dir / "README.md")  # Also render README

    for workflow_file in workflow_files:
        if not workflow_file.exists():
            continue

        try:
            content = workflow_file.read_text(encoding="utf-8")
            original_content = content

            # Replace all cookiecutter variable patterns (with/without spaces)
            for key, value in context.items():
                # Handle various spacing patterns
                # Build patterns using separate strings to avoid Jinja2 interpretation
                open_brace = "{" + "{"
                close_brace = "}" + "}"
                pattern1 = open_brace + f" cookiecutter.{key} " + close_brace
                pattern2 = open_brace + f"cookiecutter.{key}" + close_brace
                pattern3 = open_brace + f"  cookiecutter.{key}  " + close_brace
                content = content.replace(pattern1, value)
                content = content.replace(pattern2, value)
                content = content.replace(pattern3, value)

            # Only write if changes were made
            if content != original_content:
                workflow_file.write_text(content, encoding="utf-8")
                rendered_count += 1
                print(f"  ✓ Rendered: {workflow_file.name}")

        except (OSError, ValueError, KeyError) as e:
            print(f"  ⚠ Failed to render {workflow_file.name}: {e}")

    if rendered_count > 0:
        print(f"  ✓ Rendered {rendered_count} workflow file(s)")
    else:
        print("  ℹ No unrendered templates found (workflows already rendered)")  # noqa: RUF001


def _is_safe_clone_url(repo_url: str) -> bool:
    """Validate that a git clone URL uses an allowed scheme and host shape.

    Rejects values that could be interpreted as git options (leading "-"),
    schemes other than https/ssh, and ssh URLs that do not look like
    user@host:path. This prevents user input from being passed to git as a
    flag (mitigates argument injection in subprocess) or pointing at
    an unexpected scheme.
    """
    if not repo_url or repo_url.startswith("-"):
        return False
    # Allowed shapes: https://..., ssh://..., or git@host:path/path.git
    # git:// is intentionally excluded: it is unauthenticated and plaintext,
    # which is unacceptable for a settings-clone source.
    if repo_url.startswith(("https://", "ssh://")):
        return True
    return bool(
        re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+:[A-Za-z0-9_./~-]+", repo_url)
    )


def _collect_installed_items(install_path: Path) -> list[str]:
    """Return labels for Claude settings artefacts present in install_path."""
    items: list[str] = []
    if (install_path / "CLAUDE.md").exists():
        items.append("CLAUDE.md")
    if (install_path / "skills").exists():
        items.append("skills/")
    if (install_path / "agents").exists():
        items.append("agents/")
    if (install_path / ".claude" / "commands").exists() or (
        install_path / "commands"
    ).exists():
        items.append("slash commands")
    return items


def _install_claude_settings(repo_url: str, install_path: Path) -> None:
    """Clone and verify user-level Claude Code settings.

    Args:
        repo_url: Git repository URL to clone from. Must pass _is_safe_clone_url.
        install_path: Local path to install settings into. Must be inside the
            user's home directory to prevent path traversal.
    """
    # #CRITICAL: Security: user-supplied repo_url passed to git clone via subprocess.
    # #VERIFY: _is_safe_clone_url rejects flag-like values and unknown schemes.
    if not _is_safe_clone_url(repo_url):
        print(f"  ⚠ Refusing to clone from unsafe URL: {repo_url!r}")
        return

    # #CRITICAL: Security: install_path is user-supplied; reject paths that resolve
    # outside the user's home directory.
    # #VERIFY: resolve to absolute path and check ancestry against Path.home().
    install_path = install_path.expanduser().resolve()
    home = Path.home().resolve()
    if home not in install_path.parents and install_path != home:
        print(f"  ⚠ Refusing to install settings outside $HOME: {install_path}")
        return

    print(f"\n  📥 Cloning settings from {repo_url}...")

    if run_command(["git", "clone", "--", repo_url, str(install_path)], check=False):
        print(f"  ✓ User-level settings installed at: {install_path}")

        installed_items = _collect_installed_items(install_path)
        if installed_items:
            print(f"  ✓ Installed: {', '.join(installed_items)}")

        print(
            "\n  ✅ User-level settings are now available to all Claude Code sessions!"
        )
    else:
        # Sanitize repo_url before echoing to terminal: strip ANSI/control chars
        # so a maliciously crafted URL cannot inject terminal escape sequences
        # into the operator's terminal session.
        safe_repo_url = re.sub(r"[\x00-\x1f\x7f]", "", repo_url)
        print("  ⚠ Failed to clone settings repo. You can manually set up later:")
        print(f"     git clone {safe_repo_url} {install_path}")


def setup_claude_user_settings() -> None:
    """Interactively set up user-level Claude Code settings."""
    print("\n🤖 Claude Code User-Level Settings Setup")
    print("=" * 60)

    # Check common locations for existing settings
    possible_locations = [
        Path.home() / ".claude",
        Path.home() / ".config" / "claude",
    ]

    for location in possible_locations:
        if location.exists() and (location / "CLAUDE.md").exists():
            print(f"\n  ℹ User-level settings already exist at: {location}")  # noqa: RUF001
            print("    Skipping setup.")
            return

    print("\n  User-level Claude settings provide:")
    print("    • Global CLAUDE.md configuration (best practices, workflows)")
    print("    • Skills (reusable capabilities)")
    print("    • Agents (specialized task handlers)")
    print("    • Custom slash commands and hooks")

    print("\n  These settings enhance Claude Code's capabilities across all projects.")

    # Get user input
    try:
        response = (
            input("\n  Would you like to set up user-level Claude settings? (Y/n): ")
            .strip()
            .lower()
        )
    except (EOFError, KeyboardInterrupt):
        print("\n  Skipping user-level settings setup.")
        return

    # Default to yes if empty response
    if response in ["", "y", "yes"]:
        default_repo = "https://github.com/williaby/.claude"
        default_location = str(Path.home() / ".claude")

        try:
            repo_url = input(
                f"\n  Settings repo URL (press Enter for default: {default_repo}): "
            ).strip()
            if not repo_url:
                repo_url = default_repo

            install_location = input(
                f"  Install location (press Enter for default: {default_location}): "
            ).strip()
            if not install_location:
                install_location = default_location

            _install_claude_settings(repo_url, Path(install_location).expanduser())

        except (EOFError, KeyboardInterrupt):
            print("\n  Setup cancelled.")
    else:
        print("\n  ℹ Skipping setup. You can set up user-level settings later by:")  # noqa: RUF001
        print("     git clone https://github.com/williaby/.claude ~/.claude")


def _collect_optional_features(
    include_background_jobs: str,
    include_frontend: str,
    include_docker: bool,
    include_sentry: bool,
    include_health_checks: bool,
    include_caching: bool,
    include_load_testing: bool,
    include_semantic_release: bool,
    include_coderabbit: bool,
    include_linear: bool,
    include_supply_chain: bool,
) -> list[str]:
    """Collect enabled optional features into a display list.

    Args:
        include_background_jobs: Background jobs setting ("no", "arq", or "celery").
        include_frontend: Frontend setting ("no", "react", etc.).
        include_docker: Whether Docker is enabled.
        include_sentry: Whether Sentry is enabled.
        include_health_checks: Whether health checks are enabled.
        include_caching: Whether caching is enabled.
        include_load_testing: Whether load testing is enabled.
        include_semantic_release: Whether semantic release is enabled.
        include_coderabbit: Whether CodeRabbit is enabled.
        include_linear: Whether Linear is enabled.
        include_supply_chain: Whether supply chain security is enabled.

    Returns:
        List of feature description strings for enabled features.
    """
    simple_features: list[tuple[bool, str]] = [
        (include_docker, "Docker containerization"),
        (include_sentry, "Sentry monitoring"),
        (include_health_checks, "Health check endpoints"),
        (include_caching, "Redis caching"),
        (include_load_testing, "Load testing (Locust & k6)"),
        (include_semantic_release, "Semantic Release (automated versioning)"),
        (include_coderabbit, "CodeRabbit (AI code reviews)"),
        (include_linear, "Linear (project management integration)"),
        (include_supply_chain, "Supply chain security (Assured OSS + Infisical)"),
    ]
    features: list[str] = [label for flag, label in simple_features if flag]
    if include_background_jobs != "no":
        features.append(f"Background jobs ({include_background_jobs.upper()})")
    if include_frontend != "no":
        features.append(f"Frontend ({include_frontend.title()} + Vite + TypeScript)")
    return features


def _print_next_steps(
    project_slug: str, use_pre_commit: bool, use_mkdocs: bool
) -> None:
    """Print numbered next steps for project setup.

    Args:
        project_slug: The generated project's directory name.
        use_pre_commit: Whether pre-commit is enabled.
        use_mkdocs: Whether MkDocs is enabled.
    """
    print("\n📦 Next steps:")
    print("\n  1. Navigate to your project:")
    print(f"     cd {project_slug}")

    print("\n  2. Install dependencies:")
    print("     uv sync --with dev")

    if use_pre_commit:
        print("\n  3. Install pre-commit hooks:")
        print("     uv run pre-commit install")
        print("\n  4. Install Qlty CLI for unified code quality:")
        print("     curl https://qlty.sh | bash")
        print('     # Or on Windows: powershell -c "iwr https://qlty.sh | iex"')

    print("\n  5. Run tests:")
    print("     uv run pytest -v")

    if use_pre_commit:
        print("\n  6. Verify code quality setup:")
        print("     qlty check")

    if use_mkdocs:
        print("\n  7. Build documentation:")
        print("     uv run mkdocs build")

    print("\n  8. Initialize git (if not done automatically):")
    print("     git init")
    print("     git add .")
    print("     git commit -m 'Initial commit'")

    print("\n  9. Create GitHub repository:")
    print(f"     gh repo create {project_slug} --public --source=.")


def _print_infrastructure_integrations(
    include_docker: bool,
    include_background_jobs: str,
    include_load_testing: bool,
    include_sentry: bool,
) -> None:
    """Print setup instructions for infrastructure integrations.

    Args:
        include_docker: Whether Docker is enabled.
        include_background_jobs: Background jobs setting ("no", "arq", or "celery").
        include_load_testing: Whether load testing is enabled.
        include_sentry: Whether Sentry is enabled.
    """
    project_slug = "{{ cookiecutter.project_slug }}"

    if include_docker:
        print("\n  📦 Docker:")
        print("     docker-compose up -d    # Start development environment")
        print("     docker build -t app .   # Build production image")

    if include_background_jobs != "no":
        if include_background_jobs == "arq":
            print("\n  ⚙️  ARQ Worker:")
            print(f"     uv run arq {project_slug}.jobs.worker.WorkerSettings")
        else:
            print("\n  ⚙️  Celery Worker:")
            print(f"     uv run celery -A {project_slug}.jobs worker -l info")

    if include_load_testing:
        print("\n  🚀 Load Testing:")
        print("     uv run locust -f tests/load/locustfile.py  # Start Locust")
        print("     k6 run tests/load/k6-script.js              # Run k6")

    if include_sentry:
        print("\n  🔍 Sentry:")
        print("     Set SENTRY_DSN in .env to enable error tracking")


def _print_developer_tool_integrations(
    include_semantic_release: bool,
    include_coderabbit: bool,
    include_linear: bool,
    include_supply_chain: bool,
    include_frontend: str,
    frontend_package_manager: str,
    include_docker: bool,
) -> None:
    """Print setup instructions for developer tool integrations.

    Args:
        include_semantic_release: Whether semantic release is enabled.
        include_coderabbit: Whether CodeRabbit is enabled.
        include_linear: Whether Linear is enabled.
        include_supply_chain: Whether supply chain security is enabled.
        include_frontend: Frontend setting ("no", "react", etc.).
        frontend_package_manager: Package manager for frontend ("npm", "pnpm", etc.).
        include_docker: Whether Docker is enabled.
    """
    if include_semantic_release:
        print("\n  🚀 Semantic Release:")
        print("     Releases are automated on push to main/master branch")
        print("     Use conventional commits: feat:, fix:, BREAKING CHANGE:")
        print("     Manual release: gh workflow run 'Semantic Release'")
        print("     PyPI publishing requires trusted publisher setup")

    if include_coderabbit:
        print("\n  🐰 CodeRabbit:")
        print("     AI-powered code reviews are configured")
        print(
            "     Install CodeRabbit GitHub App: https://github.com/apps/coderabbitai"
        )
        print("     Reviews will run automatically on PRs")
        print("     Use @coderabbitai in PR comments to interact")

    if include_linear:
        print("\n  📋 Linear:")
        print("     Project management integration is configured")
        print("     Connect your repo: https://linear.app/settings/integrations/github")
        print("     Link PRs to issues: 'Closes ENG-123' in PR description")
        print("     Issues sync bidirectionally with GitHub")

    if include_supply_chain:
        print("\n  🔐 Supply Chain Security:")
        print(
            "     ./scripts/setup-supply-chain.sh    # Configure local authentication"
        )
        print("     gcloud auth application-default login  # GCP credentials")
        print("     infisical login && infisical init      # Secrets management")
        print("     See README.md for full setup instructions")

    if include_frontend != "no":
        print("\n  🎨 Frontend (React + Vite):")
        print("     cd frontend")
        print(f"     {frontend_package_manager} install")
        print(
            f"     {frontend_package_manager} run dev          # Start dev server (http://localhost:3000)"
        )
        print(f"     {frontend_package_manager} run test         # Run tests")
        print(
            f"     {frontend_package_manager} run build        # Build for production"
        )
        if include_docker:
            print("\n     Or with Docker:")
            print("     docker-compose up frontend  # Start frontend container")


def print_success_message() -> None:
    """Print success message with next steps."""
    project_name = "{{ cookiecutter.project_name }}"
    project_slug = "{{ cookiecutter.project_slug }}"
    use_pre_commit = "{{ cookiecutter.use_pre_commit }}" == "yes"
    use_mkdocs = "{{ cookiecutter.use_mkdocs }}" == "yes"
    include_docker = INCLUDE_DOCKER == "yes"
    include_sentry = "{{ cookiecutter.include_sentry }}" == "yes"
    include_health_checks = "{{ cookiecutter.include_health_checks }}" == "yes"
    include_background_jobs = "{{ cookiecutter.include_background_jobs }}"
    include_caching = "{{ cookiecutter.include_caching }}" == "yes"
    include_load_testing = "{{ cookiecutter.include_load_testing }}" == "yes"
    include_semantic_release = "{{ cookiecutter.include_semantic_release }}" == "yes"
    include_coderabbit = "{{ cookiecutter.include_coderabbit }}" == "yes"
    include_linear = "{{ cookiecutter.include_linear }}" == "yes"
    include_frontend = INCLUDE_FRONTEND
    frontend_package_manager = "{{ cookiecutter.frontend_package_manager }}"
    include_supply_chain = INCLUDE_SUPPLY_CHAIN_SECURITY == "yes"

    print("\n" + "=" * 60)
    print(f"🎉 SUCCESS! {project_name} has been created!")
    print("=" * 60)

    optional_features = _collect_optional_features(
        include_background_jobs,
        include_frontend,
        include_docker,
        include_sentry,
        include_health_checks,
        include_caching,
        include_load_testing,
        include_semantic_release,
        include_coderabbit,
        include_linear,
        include_supply_chain,
    )
    if optional_features:
        print("\n✨ Optional features included:")
        for feature in optional_features:
            print(f"  • {feature}")

    _print_next_steps(project_slug, use_pre_commit, use_mkdocs)
    _print_infrastructure_integrations(
        include_docker, include_background_jobs, include_load_testing, include_sentry
    )
    _print_developer_tool_integrations(
        include_semantic_release,
        include_coderabbit,
        include_linear,
        include_supply_chain,
        include_frontend,
        frontend_package_manager,
        include_docker,
    )

    print("\n" + "=" * 60)
    print("📚 Documentation:")
    print("  - README.md: Project overview and quick start")
    print("  - CONTRIBUTING.md: Contribution guidelines")
    print("  - CLAUDE.md: Claude Code development guidance")
    if include_load_testing:
        print("  - tests/load/README.md: Load testing guide")
    if include_frontend != "no":
        print("  - frontend/README.md: Frontend development guide")
    print("=" * 60 + "\n")


def inject_creation_date() -> None:
    """Inject the actual project creation date into files.

    Replaces the placeholder __PROJECT_CREATION_DATE__ with the current date.
    This ensures the date reflects when the project was generated, not when
    the cookiecutter template was created.
    """
    print("\n📅 Injecting project creation date...")

    creation_date = datetime.now().strftime("%Y-%m-%d")

    # Files that may contain the date placeholder
    files_to_update = [
        Path("CLAUDE.md"),
        Path("README.md"),
        Path("pyproject.toml"),
    ]

    placeholder = "__PROJECT_CREATION_DATE__"
    updated_count = 0

    # NOTE: SonarCloud pythonsecurity:S2083 (path traversal) flags the
    # filepath.write_text below as user-controlled. False positive: filepath
    # comes exclusively from files_to_update, a hardcoded literal list above.
    # No user input reaches this sink.
    for filepath in files_to_update:
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
            if placeholder in content:
                content = content.replace(placeholder, creation_date)
                # NOSONAR S2083 false positive: filepath comes from the
                # hardcoded files_to_update list above (3 literal paths).
                # No user input reaches this sink.
                filepath.write_text(content, encoding="utf-8")  # NOSONAR
                updated_count += 1
                print(f"  ✓ Updated: {filepath}")
        except (OSError, UnicodeDecodeError) as e:
            print(f"  ⚠ Could not update {filepath}: {e}")

    if updated_count > 0:
        print(
            f"  ✓ Injected creation date ({creation_date}) into {updated_count} file(s)"
        )
    else:
        print("  ✓ No date placeholders found")


def _path_is_inside(filepath: Path, root: Path) -> bool:
    """Return True iff filepath's resolved path is inside root.

    #CRITICAL: Security: rglob follows symlinks by default; this guard blocks
    a malicious template that ships a symlink pointing outside the generated
    tree from causing writes outside project_root.
    #VERIFY: filepath.resolve().is_relative_to(root) before any write.
    """
    try:
        return filepath.resolve().is_relative_to(root)
    except OSError:
        return False


def ensure_trailing_newlines() -> None:
    """Ensure all text files end with a trailing newline.

    This prevents the pre-commit hook 'end-of-file-fixer' from modifying
    files on first run, which would indicate a template quality issue.
    """
    print("\n🔧 Ensuring trailing newlines...")

    # File extensions to process (text files only)
    text_extensions = {
        ".py",
        ".md",
        ".txt",
        ".yml",
        ".yaml",
        ".json",
        ".toml",
        ".cfg",
        ".ini",
        ".sh",
        ".bash",
        ".zsh",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".env",
        ".example",
        ".rst",
        ".css",
        ".html",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
    }

    # Also include common dotfiles
    dotfiles = {
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".pre-commit-config.yaml",
        ".env.example",
    }

    fixed_count = 0
    project_root = Path().resolve()

    for filepath in project_root.rglob("*"):
        if not filepath.is_file():
            continue

        # Skip git directory and symlinks that escape project_root (delegated
        # to _path_is_inside helper to keep this function under the C901 limit).
        if ".git" in filepath.parts or not _path_is_inside(filepath, project_root):
            continue

        # Check if file should be processed
        should_process = (
            filepath.suffix.lower() in text_extensions
            or filepath.name in dotfiles
            or (filepath.name.startswith(".") and filepath.suffix in text_extensions)
        )

        if not should_process:
            continue

        try:
            content = filepath.read_bytes()

            # Skip empty files and binary files
            if not content or b"\x00" in content[:1024]:
                continue

            # Check if file ends with newline
            if not content.endswith(b"\n"):
                filepath.write_bytes(content + b"\n")
                fixed_count += 1

        except (OSError, UnicodeDecodeError):
            # Skip files that can't be read
            continue

    if fixed_count > 0:
        print(f"  ✓ Added trailing newlines to {fixed_count} file(s)")
    else:
        print("  ✓ All files already have trailing newlines")


def run_code_fixes() -> None:
    """Run automatic code fixes on generated project.

    Applies Ruff auto-fix to clean up code quality issues in the generated project.
    This ensures projects start with clean, properly formatted code.
    """
    print("\n🔧 Running automatic code fixes...")

    # Check if uv is available (it should be from template generation)
    if not shutil.which("uv"):
        print("  - Skipping code fixes (uv not found)")
        return

    # Run Ruff auto-fix
    # Format code with Ruff (replaces Black)
    print("  • Formatting code with Ruff...")
    success = run_command(["uv", "run", "ruff", "format", "."], check=False)
    if success:
        print("  ✓ Ruff format completed")
    else:
        print("  - Ruff format completed with some issues (review manually)")

    # Fix linting issues with Ruff
    print("  • Fixing linting issues with Ruff...")
    success = run_command(["uv", "run", "ruff", "check", "--fix", "."], check=False)
    if success:
        print("  ✓ Ruff auto-fix completed")
    else:
        print("  - Ruff auto-fix completed with some issues (review manually)")


def main() -> None:
    """Run post-generation tasks."""
    print("\n🚀 Running post-generation setup...")

    try:
        cleanup_conditional_files()
        render_workflow_templates()  # Fix unrendered Jinja2 variables in workflows
        inject_creation_date()  # Inject actual creation date into files
        create_initial_directories()
        run_code_fixes()  # Auto-fix code quality issues before git init
        ensure_trailing_newlines()  # Ensure all files have trailing newlines
        mark_scripts_executable()  # Ensure shebang scripts have executable permissions
        initialize_git()
        setup_claude_subtree()  # Add Claude standards via git subtree
        setup_pre_commit()
        setup_claude_user_settings()
        # Optional auto-run of branch protection (opt-in via cookiecutter flag).
        remote_url = ""
        git_bin = shutil.which("git")
        if git_bin:
            try:
                result = subprocess.run(
                    [git_bin, "config", "--get", "remote.origin.url"],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5,
                )
                remote_url = result.stdout.strip()
            except (subprocess.TimeoutExpired, OSError):
                remote_url = ""
        maybe_run_branch_protection(
            flag="{{ cookiecutter.auto_setup_branch_protection }}",
            remote_url=remote_url,
        )
        print_success_message()
    except Exception as e:  # noqa: BLE001
        # Architectural decision: main() is the top-level error boundary for the
        # cookiecutter post-generation hook. Cookiecutter swallows exceptions raised
        # from hooks and prints generic traceback noise; a broad catch here
        # produces actionable error output and a clean non-zero exit. This is
        # NOT a tracked-for-fix suppression in the CLAUDE.md sense; it is a
        # deliberate top-level guard. Per-step exceptions are caught by the
        # individual setup functions. Do not narrow without auditing every call
        # site above for the full set of raisable exception types.
        print(f"\n❌ Error during post-generation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
